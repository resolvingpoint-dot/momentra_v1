"""Settlement split allocation and debt simplification."""
from __future__ import annotations

from collections.abc import Mapping, Sequence

from app.domains.group.settlements.schemas import (
    MemberBalance,
    SettlementPreview,
    SplitStyle,
    TransferSuggestion,
)


def normalize_split_style(expense: Mapping[str, object]) -> SplitStyle:
    raw = str(expense.get("split_style") or expense.get("split_type") or "EQUAL").upper()
    aliases = {
        "EQUAL": "EQUAL",
        "EQUAL_SPLIT": "EQUAL",
        "CUSTOM": "EXACT",
        "EXACT": "EXACT",
        "CUSTOM_AMOUNT": "EXACT",
        "PERCENT": "PERCENTAGE",
        "PERCENTAGE": "PERCENTAGE",
        "CUSTOM_PERCENTAGE": "PERCENTAGE",
        "SHARES": "SHARES",
        "BY_SHARES": "SHARES",
    }
    lowered = raw.lower()
    if lowered == "equal":
        return "EQUAL"
    if lowered in {"custom", "exact"}:
        return "EXACT"
    if lowered in {"percent", "percentage"}:
        return "PERCENTAGE"
    if lowered == "shares":
        return "SHARES"
    return aliases.get(raw, "EQUAL")  # type: ignore[return-value]


def _sorted_participants(participant_ids: Sequence[str]) -> list[str]:
    return sorted({str(pid) for pid in participant_ids if pid})


def allocate_equal(amount_minor: int, participant_ids: Sequence[str]) -> dict[str, int]:
    ids = _sorted_participants(participant_ids)
    if not ids or amount_minor <= 0:
        return {pid: 0 for pid in ids}
    base, remainder = divmod(amount_minor, len(ids))
    out = {pid: base for pid in ids}
    if remainder:
        out[ids[0]] += remainder
    return out


def allocate_exact(
    amount_minor: int,
    participant_ids: Sequence[str],
    splits: Sequence[Mapping[str, object]] | None,
) -> dict[str, int]:
    ids = _sorted_participants(participant_ids)
    out = {pid: 0 for pid in ids}
    if not splits:
        return allocate_equal(amount_minor, ids)
    for row in splits:
        member_id = str(row.get("member_id") or "")
        if member_id in out:
            out[member_id] = int(row.get("amount_minor") or 0)
    total = sum(out.values())
    if total < amount_minor and ids:
        out[ids[0]] += amount_minor - total
    return out


def allocate_percentage(
    amount_minor: int,
    participant_ids: Sequence[str],
    splits: Sequence[Mapping[str, object]] | None,
) -> dict[str, int]:
    ids = _sorted_participants(participant_ids)
    if not ids or amount_minor <= 0:
        return {pid: 0 for pid in ids}
    if not splits:
        return allocate_equal(amount_minor, ids)
    pct_by_member: dict[str, int] = {pid: 0 for pid in ids}
    for row in splits:
        member_id = str(row.get("member_id") or "")
        if member_id in pct_by_member:
            pct_by_member[member_id] = int(row.get("percent") or row.get("percentage") or 0)
    allocated = 0
    out = {pid: 0 for pid in ids}
    for pid in ids:
        share = (amount_minor * pct_by_member[pid]) // 100
        out[pid] = share
        allocated += share
    remainder = amount_minor - allocated
    if remainder > 0:
        out[ids[0]] += remainder
    return out


def allocate_shares(
    amount_minor: int,
    participant_ids: Sequence[str],
    splits: Sequence[Mapping[str, object]] | None,
) -> dict[str, int]:
    ids = _sorted_participants(participant_ids)
    if not ids or amount_minor <= 0:
        return {pid: 0 for pid in ids}
    if not splits:
        return allocate_equal(amount_minor, ids)
    shares_by_member: dict[str, int] = {pid: 0 for pid in ids}
    for row in splits:
        member_id = str(row.get("member_id") or "")
        if member_id in shares_by_member:
            shares_by_member[member_id] = int(row.get("shares") or 0)
    total_shares = sum(shares_by_member.values())
    if total_shares <= 0:
        return allocate_equal(amount_minor, ids)
    allocated = 0
    out = {pid: 0 for pid in ids}
    for pid in ids:
        share = (amount_minor * shares_by_member[pid]) // total_shares
        out[pid] = share
        allocated += share
    remainder = amount_minor - allocated
    if remainder > 0:
        out[ids[0]] += remainder
    return out


def allocate_expense(
    expense: Mapping[str, object],
    participant_ids: Sequence[str],
) -> dict[str, int]:
    amount_minor = int(expense.get("amount_minor") or 0)
    ids = _sorted_participants(participant_ids)
    if not ids or amount_minor <= 0:
        return {pid: 0 for pid in ids}

    # Prefer already-resolved shares written by expense_contract (source of truth).
    raw_shares = expense.get("shares")
    if isinstance(raw_shares, list) and raw_shares:
        out = {pid: 0 for pid in ids}
        for row in raw_shares:
            if not isinstance(row, Mapping):
                continue
            mid = str(row.get("member_id") or "")
            if mid in out:
                out[mid] = int(row.get("amount_minor") or 0)
        if sum(out.values()) == amount_minor:
            return out

    style = normalize_split_style(expense)
    splits = expense.get("splits")
    if not isinstance(splits, list):
        details = expense.get("split_details")
        splits = details if isinstance(details, list) else None
    if style == "EXACT":
        return allocate_exact(amount_minor, ids, splits)
    if style == "PERCENTAGE":
        return allocate_percentage(amount_minor, ids, splits)
    if style == "SHARES":
        return allocate_shares(amount_minor, ids, splits)
    return allocate_equal(amount_minor, ids)


def _payer_id(expense: Mapping[str, object]) -> str:
    return str(
        expense.get("paid_by_member_id")
        or expense.get("paid_by_participant_id")
        or expense.get("paid_by_user_id")
        or expense.get("payer_member_id")
        or ""
    )


def _expense_participants(expense: Mapping[str, object], all_member_ids: Sequence[str]) -> list[str]:
    raw = expense.get("participant_ids") or expense.get("participants")
    if isinstance(raw, list) and raw:
        return _sorted_participants(str(x) for x in raw)
    splits = expense.get("splits")
    if isinstance(splits, list) and splits:
        return _sorted_participants(str(row.get("member_id") or "") for row in splits if row.get("member_id"))
    return _sorted_participants(all_member_ids)


def compute_member_balances(
    expenses: Sequence[Mapping[str, object]],
    members: Sequence[Mapping[str, object]],
    *,
    currency_code: str = "INR",
) -> tuple[list[MemberBalance], int]:
    member_ids = _sorted_participants(str(m.get("id") or "") for m in members)
    names = {str(m.get("id") or ""): str(m.get("full_name") or "Member") for m in members}
    paid: dict[str, int] = {pid: 0 for pid in member_ids}
    owed: dict[str, int] = {pid: 0 for pid in member_ids}
    total_expenses = 0

    for expense in expenses:
        if expense.get("deleted"):
            continue
        amount_minor = int(expense.get("amount_minor") or 0)
        if amount_minor <= 0:
            continue
        expense_currency = str(expense.get("currency_code") or currency_code)
        if expense_currency != currency_code:
            continue
        total_expenses += amount_minor
        participants = _expense_participants(expense, member_ids)
        if not participants:
            continue
        allocations = allocate_expense(expense, participants)
        payer = _payer_id(expense)
        if payer in paid:
            paid[payer] += amount_minor
        for pid, share in allocations.items():
            if pid in owed:
                owed[pid] += share

    balances: list[MemberBalance] = []
    for pid in member_ids:
        paid_minor = paid.get(pid, 0)
        owed_minor = owed.get(pid, 0)
        balances.append(
            MemberBalance(
                member_id=pid,
                display_name=names.get(pid, "Member"),
                paid_minor=paid_minor,
                owed_minor=owed_minor,
                net_minor=paid_minor - owed_minor,
                currency_code=currency_code,
            )
        )
    return balances, total_expenses


def simplify_debts(balances: Sequence[MemberBalance]) -> list[TransferSuggestion]:
    creditors: list[list[object]] = [
        [b.member_id, b.display_name, b.net_minor]
        for b in balances
        if b.net_minor > 0
    ]
    debtors: list[list[object]] = [
        [b.member_id, b.display_name, -b.net_minor]
        for b in balances
        if b.net_minor < 0
    ]
    creditors.sort(key=lambda row: (-int(row[2]), str(row[0])))
    debtors.sort(key=lambda row: (-int(row[2]), str(row[0])))

    suggestions: list[TransferSuggestion] = []
    i = 0
    j = 0
    currency = balances[0].currency_code if balances else "INR"
    while i < len(debtors) and j < len(creditors):
        debtor_id, debtor_name, debt_amt = debtors[i]
        creditor_id, creditor_name, credit_amt = creditors[j]
        transfer = min(int(debt_amt), int(credit_amt))
        if transfer > 0:
            suggestions.append(
                TransferSuggestion(
                    from_member_id=str(debtor_id),
                    to_member_id=str(creditor_id),
                    from_display_name=str(debtor_name),
                    to_display_name=str(creditor_name),
                    amount_minor=transfer,
                    currency_code=currency,
                )
            )
        debt_amt = int(debt_amt) - transfer
        credit_amt = int(credit_amt) - transfer
        debtors[i][2] = debt_amt
        creditors[j][2] = credit_amt
        if debt_amt == 0:
            i += 1
        if credit_amt == 0:
            j += 1
    return suggestions


def _harmony_label(balances: Sequence[MemberBalance]) -> str:
    if not balances:
        return "In harmony"
    max_imbalance = max((abs(b.net_minor) for b in balances), default=0)
    if max_imbalance == 0:
        return "In harmony"
    if max_imbalance <= 100:
        return "Nearly settled"
    return "Tracking"


def _balance_insight(total_expenses_minor: int, suggestions: Sequence[TransferSuggestion], currency_code: str) -> str:
    if total_expenses_minor <= 0:
        return "Nobody owes anything yet — log an expense to get started."
    if not suggestions:
        return f"{currency_code} {total_expenses_minor / 100:.0f} tracked — all balances even."
    top = suggestions[0]
    return (
        f"{top.from_display_name} owes {top.to_display_name} "
        f"{currency_code} {top.amount_minor / 100:.0f}"
    )


def build_preview(
    moment_id: str,
    expenses: Sequence[Mapping[str, object]],
    members: Sequence[Mapping[str, object]],
    *,
    currency_code: str = "INR",
) -> SettlementPreview:
    balances, total = compute_member_balances(expenses, members, currency_code=currency_code)
    suggestions = simplify_debts(balances)
    return SettlementPreview(
        moment_id=moment_id,
        currency_code=currency_code,
        total_expenses_minor=total,
        member_balances=balances,
        suggestions=suggestions,
        harmony_label=_harmony_label(balances),
        balance_insight=_balance_insight(total, suggestions, currency_code),
        status="preview",
    )


def life_preview_dict(preview: SettlementPreview) -> dict:
    suggested = preview.suggestions[0].model_dump(mode="json") if preview.suggestions else None
    return {
        "status": preview.status,
        "harmony_label": preview.harmony_label,
        "balance_insight": preview.balance_insight,
        "currency_code": preview.currency_code,
        "total_spent_minor": preview.total_expenses_minor,
        "pending_count": len(preview.suggestions),
        "suggested_transfer": suggested,
    }
