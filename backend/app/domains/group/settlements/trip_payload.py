"""Trip settlement payload for Pulse widget + settlements/context (mobile/web).

Maps SettlementEngine preview into the client-facing shape (user_id fields,
member contributions, totals). No mock amounts — empty when no expenses.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence

from app.domains.group import moment_store as store
from app.domains.group.settlements import calculator
from app.domains.group.settlements.repository import SettlementRepository
from app.domains.group.settlements.schemas import MemberBalance, SettlementPreview, TransferSuggestion
from app.domains.group.settlements.service import (
    _active_expenses,
    _members,
    _moment_currency,
)
from app.domains.moments.models import MomentModel


def _member_lookup(members: Sequence[Mapping[str, object]]) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for m in members:
        mid = str(m.get("id") or "")
        if mid:
            out[mid] = dict(m)
    return out


def _photo_url(member: Mapping[str, object] | None) -> str | None:
    if not member:
        return None
    for key in ("photo_url", "avatar_url", "image_url"):
        val = member.get(key)
        if val:
            return str(val)
    return None


def _display_name(member: Mapping[str, object] | None, fallback: str = "Member") -> str:
    if not member:
        return fallback
    return str(member.get("full_name") or member.get("display_name") or fallback)


def _contribution_status(net_minor: int) -> str:
    if net_minor > 0:
        return "will_receive"
    if net_minor < 0:
        return "needs_to_pay"
    return "settled"


def _pending_status_label(net_minor: int) -> str:
    if net_minor > 0:
        return "Receives"
    if net_minor < 0:
        return "Needs to pay"
    return "Settled"


def apply_settled_transfers(
    balances: list[MemberBalance],
    settled_rows: Sequence[Mapping[str, object]],
) -> list[MemberBalance]:
    """Adjust nets after SETTLED transfers: payer gains net, receiver loses net."""
    by_id = {b.member_id: b.model_copy() for b in balances}
    for row in settled_rows:
        if str(row.get("status") or "").upper() != "SETTLED":
            continue
        if row.get("deleted"):
            continue
        from_id = str(row.get("from_member_id") or "")
        to_id = str(row.get("to_member_id") or "")
        amount = int(row.get("amount_minor") or 0)
        if amount <= 0 or not from_id or not to_id:
            continue
        if from_id in by_id:
            src = by_id[from_id]
            by_id[from_id] = src.model_copy(update={"net_minor": src.net_minor + amount})
        if to_id in by_id:
            dst = by_id[to_id]
            by_id[to_id] = dst.model_copy(update={"net_minor": dst.net_minor - amount})
    return list(by_id.values())


def build_preview_with_settlements(moment: MomentModel) -> SettlementPreview:
    currency = _moment_currency(moment)
    expenses = _active_expenses(moment)
    members = _members(moment)
    balances, total = calculator.compute_member_balances(
        expenses, members, currency_code=currency
    )
    repo = SettlementRepository()
    settled = [
        row
        for row in repo.list_all(moment)
        if str(row.get("status") or "").upper() == "SETTLED" and not row.get("deleted")
    ]
    balances = apply_settled_transfers(balances, settled)
    suggestions = calculator.simplify_debts(balances)
    return SettlementPreview(
        moment_id=str(moment.id),
        currency_code=currency,
        total_expenses_minor=total,
        member_balances=balances,
        suggestions=suggestions,
        harmony_label=calculator._harmony_label(balances),
        balance_insight=calculator._balance_insight(total, suggestions, currency),
        status="preview",
    )


def _dominant_split_method(expenses: Sequence[Mapping[str, object]]) -> str:
    counts: dict[str, int] = {}
    for row in expenses:
        style = calculator.normalize_split_style(row)
        counts[style] = counts.get(style, 0) + 1
    if not counts:
        return "EQUAL"
    return max(counts.items(), key=lambda kv: kv[1])[0]


def _map_suggestion(
    s: TransferSuggestion,
    lookup: dict[str, dict],
) -> dict:
    from_m = lookup.get(s.from_member_id)
    to_m = lookup.get(s.to_member_id)
    return {
        "from_user_id": s.from_member_id,
        "to_user_id": s.to_member_id,
        "from_member_id": s.from_member_id,
        "to_member_id": s.to_member_id,
        "from_display_name": s.from_display_name,
        "to_display_name": s.to_display_name,
        "from_photo_url": _photo_url(from_m),
        "to_photo_url": _photo_url(to_m),
        "amount_minor": s.amount_minor,
        "currency_code": s.currency_code,
        "reason": s.reason or "to stabilize balance",
    }


def build_trip_settlement_payload(moment: MomentModel) -> dict:
    """Full settlement context + pulse widget fields from live expenses."""
    currency = _moment_currency(moment)
    members = _members(moment)
    lookup = _member_lookup(members)
    expenses = _active_expenses(moment)
    preview = build_preview_with_settlements(moment)

    total_paid = sum(max(0, b.paid_minor) for b in preview.member_balances)
    unsettled = sum(abs(b.net_minor) for b in preview.member_balances if b.net_minor < 0)
    # Creditor-side sum equals debtor-side for a closed system; use debtors.
    pending_settlement = unsettled
    members_needing = sum(1 for b in preview.member_balances if b.net_minor != 0)
    total_expenses = preview.total_expenses_minor
    if total_expenses <= 0:
        balance_sync = 100.0
    else:
        balance_sync = max(0.0, min(100.0, 100.0 * (1.0 - (pending_settlement / total_expenses))))

    contributions: list[dict] = []
    pending_balances: list[dict] = []
    preview_rows: list[dict] = []
    for b in sorted(preview.member_balances, key=lambda x: abs(x.net_minor), reverse=True):
        member = lookup.get(b.member_id)
        name = b.display_name or _display_name(member)
        status = _contribution_status(b.net_minor)
        row = {
            "user_id": b.member_id,
            "member_id": b.member_id,
            "display_name": name,
            "photo_url": _photo_url(member),
            "paid_minor": b.paid_minor,
            "expected_minor": b.owed_minor,
            "owed_minor": b.owed_minor,
            "net_minor": b.net_minor,
            "currency_code": b.currency_code or currency,
            "status": status,
        }
        contributions.append(row)
        if b.net_minor != 0:
            amount = abs(b.net_minor)
            pending_balances.append(
                {
                    "user_id": b.member_id,
                    "display_name": name,
                    "photo_url": _photo_url(member),
                    "subtitle": f"{_pending_status_label(b.net_minor)}",
                    "amount_minor": amount,
                    "currency_code": b.currency_code or currency,
                    "status": status,
                }
            )
            if len(preview_rows) < 3:
                preview_rows.append(
                    {
                        "user_id": b.member_id,
                        "display_name": name,
                        "photo_url": _photo_url(member),
                        "amount_minor": amount,
                        "currency_code": b.currency_code or currency,
                        "status": status,
                        "chip_label": (
                            f"Receives"
                            if b.net_minor > 0
                            else "Needs to pay"
                        ),
                    }
                )

    suggestions = [_map_suggestion(s, lookup) for s in preview.suggestions]
    suggested = suggestions[0] if suggestions else None

    if not expenses or members_needing == 0:
        status_line = "All balances are settled."
    else:
        status_line = (
            f"{members_needing} member{'s' if members_needing != 1 else ''} need settlement"
        )

    state = store.read_state(moment)
    payload = state.get("payload") or {}
    trip_name = str(
        payload.get("moment_name")
        or payload.get("trip_name")
        or getattr(moment, "name", None)
        or "Trip"
    )
    cover = payload.get("cover_image_url")

    widget = {
        "currency_code": currency,
        "total_paid_minor": total_paid,
        "pending_settlement_minor": pending_settlement,
        "members_needing_settlement": members_needing,
        "preview_members": preview_rows,
        "status_line": status_line,
        "harmony_label": preview.harmony_label,
    }

    return {
        "moment_id": str(moment.id),
        "trip_name": trip_name,
        "cover_image_url": cover,
        "status_line": status_line,
        "balance_sync_percent": round(balance_sync, 1),
        "balance_insight": preview.balance_insight,
        "harmony_label": preview.harmony_label,
        "currency_code": currency,
        "total_expenses_minor": total_expenses,
        "total_paid_minor": total_paid,
        "pending_settlement_minor": pending_settlement,
        "unsettled_minor": pending_settlement,
        "members_needing_settlement": members_needing,
        "split_method": _dominant_split_method(expenses),
        "members_count": len(preview.member_balances),
        "member_contributions": contributions,
        "suggested_transfer": suggested,
        "suggestions": suggestions,
        "pending_balances": pending_balances,
        "guest_attributions": [],
        "settlement_widget": widget,
    }
