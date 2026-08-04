"""Runtime data store for group moments (JSON in ``moment.description``).

Setup draft state uses ``profile_code`` + ``payload``; live data (guests,
expenses, contributions, memories, residents) lives under ``runtime`` so
MockSession tests and draft saves coexist without migrations.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import uuid4

from app.domains.moments.models import MomentModel

_RUNTIME_KEYS = (
    "guests",
    "residents",
    "members",
    "invites",
    "expenses",
    "contributions",
    "budget_plans",
    "memories",
    "bookings",
    "polls",
    "tasks",
    "vendors",
    "attendances",
    "updates",
    "plans",
    "activities",
    "payments",
    "installments",
    "ownership_shares",
    "decisions",
    "milestones",
    "notes",
    "documents",
    "rent",
    "utilities",
    "groceries",
    "chores",
    "household_purchases",
    "maintenance",
    "settlements",
)


def _empty_runtime() -> dict:
    return {k: [] for k in _RUNTIME_KEYS}


def read_state(moment: MomentModel) -> dict:
    raw = moment.description or ""
    if not raw:
        return {"profile_code": None, "payload": {}, "runtime": _empty_runtime()}
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            data.setdefault("profile_code", None)
            data.setdefault("payload", {})
            rt = data.setdefault("runtime", {})
            for key in _RUNTIME_KEYS:
                rt.setdefault(key, [])
            return data
    except (ValueError, TypeError):
        pass
    return {"profile_code": None, "payload": {}, "runtime": _empty_runtime()}


def write_state(moment: MomentModel, state: dict) -> None:
    rt = state.setdefault("runtime", _empty_runtime())
    for key in _RUNTIME_KEYS:
        rt.setdefault(key, [])
    moment.description = json.dumps(state)
    moment.updated_at = datetime.now(timezone.utc)


def runtime(moment: MomentModel) -> dict:
    return read_state(moment)["runtime"]


def append_item(moment: MomentModel, collection: str, item: dict) -> dict:
    state = read_state(moment)
    state["runtime"].setdefault(collection, []).append(item)
    write_state(moment, state)
    return item


def list_items(moment: MomentModel, collection: str) -> list[dict]:
    return list(runtime(moment).get(collection, []))


def update_item(moment: MomentModel, collection: str, item_id: str, patch: dict) -> dict | None:
    state = read_state(moment)
    items = state["runtime"].setdefault(collection, [])
    for item in items:
        if str(item.get("id")) == str(item_id) and not item.get("deleted"):
            item.update(patch)
            item["updated_at"] = now_iso()
            write_state(moment, state)
            return item
    return None


def soft_delete_item(moment: MomentModel, collection: str, item_id: str) -> dict | None:
    return update_item(
        moment,
        collection,
        item_id,
        {"deleted": True, "deleted_at": now_iso()},
    )


def find_by_client_request_id(
    moment: MomentModel, collection: str, client_request_id: str | None
) -> dict | None:
    if not client_request_id:
        return None
    needle = str(client_request_id)
    for item in list_items(moment, collection):
        if item.get("deleted"):
            continue
        if str(item.get("client_request_id") or "") == needle:
            return item
    return None


def list_accepted_members(moment: MomentModel) -> list[dict]:
    """Accepted/active roster for expenses (runtime members, shared-moment safe)."""
    out: list[dict] = []
    for row in list_items(moment, "members"):
        if row.get("deleted"):
            continue
        status = str(row.get("status") or "").upper()
        if status and status not in {"ACTIVE", "ACCEPTED"}:
            continue
        mid = str(row.get("id") or row.get("member_id") or row.get("user_id") or "")
        if not mid:
            continue
        out.append(
            {
                "id": mid,
                "member_id": mid,
                "user_id": str(row.get("user_id") or "") or None,
                "display_name": str(row.get("display_name") or "Member").strip() or "Member",
                "role_code": str(row.get("role_code") or "PARTICIPANT").upper(),
                "status": status or "ACTIVE",
                "created_at": str(row.get("created_at") or ""),
            }
        )
    out.sort(key=lambda m: (m.get("created_at") or "", m.get("id") or ""))
    return out


def ensure_creator_organizer(
    moment: MomentModel,
    user_id,
    *,
    display_name: str = "You",
) -> dict:
    """Idempotent upsert of moment creator as ACTIVE ORGANIZER (+ guest for settlements)."""
    uid = str(user_id)
    name = (display_name or "You").strip() or "You"
    state = read_state(moment)
    rt = state.setdefault("runtime", _empty_runtime())
    members = rt.setdefault("members", [])
    existing = next(
        (
            m
            for m in members
            if not m.get("deleted")
            and str(m.get("user_id") or m.get("id") or m.get("member_id") or "") == uid
        ),
        None,
    )
    if existing is not None:
        existing["role_code"] = "ORGANIZER"
        existing["status"] = "ACTIVE"
        existing["display_name"] = existing.get("display_name") or name
        existing.setdefault("id", uid)
        existing.setdefault("member_id", uid)
        existing.setdefault("user_id", uid)
        member_row = existing
    else:
        member_row = {
            "id": uid,
            "member_id": uid,
            "user_id": uid,
            "display_name": name,
            "role_code": "ORGANIZER",
            "status": "ACTIVE",
            "created_at": now_iso(),
        }
        members.append(member_row)

    guests = rt.setdefault("guests", [])
    if not any(
        not g.get("deleted") and str(g.get("id") or "") == uid for g in guests
    ):
        guests.append(
            {
                "id": uid,
                "full_name": name,
                "relationship_type": "self",
                "status": "active",
                "assigned_role": "ORGANIZER",
            }
        )
    write_state(moment, state)
    return member_row


def seed_pending_residents(moment: MomentModel, expected_count: int | None) -> list[dict]:
    """Backfill placeholder PENDING residents so headcount matches setup intent.

    Idempotent: uses stable ``seed-resident-N`` ids so re-running activation never
    duplicates rows, and never removes/overwrites residents a user already added.
    """
    if not expected_count or expected_count <= 0:
        return []
    state = read_state(moment)
    rt = state.setdefault("runtime", _empty_runtime())
    residents = rt.setdefault("residents", [])
    guests = rt.get("guests", [])
    current_count = len([r for r in residents if not r.get("deleted")]) + len(
        [g for g in guests if not g.get("deleted")]
    )
    shortfall = expected_count - current_count
    if shortfall <= 0:
        return []
    existing_seed_ids = {str(r.get("id")) for r in residents}
    seeded: list[dict] = []
    next_slot = current_count + 1
    while len(seeded) < shortfall:
        seed_id = f"seed-resident-{next_slot}"
        next_slot += 1
        if seed_id in existing_seed_ids:
            continue
        row = {
            "id": seed_id,
            "full_name": f"Resident {next_slot - 1}",
            "relationship_type": "roommate",
            "assigned_role": "MEMBER",
            "status": "pending",
            "is_placeholder": True,
            "created_at": now_iso(),
        }
        residents.append(row)
        seeded.append(row)
    write_state(moment, state)
    return seeded


def expense_summary(moment: MomentModel) -> tuple[int, int]:
    """Return (count, total_minor) for stored expenses."""
    total = 0
    items = list_items(moment, "expenses")
    for row in items:
        try:
            total += int(row.get("amount_minor") or 0)
        except (ValueError, TypeError):
            pass
    return len(items), total


def contribution_summary(moment: MomentModel) -> int:
    total = 0
    for row in list_items(moment, "contributions"):
        try:
            total += int(row.get("amount_minor") or 0)
        except (ValueError, TypeError):
            pass
    return total


def guest_summaries(moment: MomentModel) -> list[dict]:
    guests = list_items(moment, "guests")
    residents = list_items(moment, "residents")
    out: list[dict] = []
    for g in guests:
        out.append(
            {
                "id": g.get("id", ""),
                "full_name": g.get("full_name", "Guest"),
                "phone": g.get("phone"),
                "email": g.get("email"),
                "relationship_type": g.get("relationship_type", "friend"),
                "assigned_role": g.get("assigned_role"),
                "status": g.get("status", "invited"),
            }
        )
    for r in residents:
        out.append(
            {
                "id": r.get("id", ""),
                "full_name": r.get("full_name", "Resident"),
                "phone": r.get("phone"),
                "email": r.get("email"),
                "relationship_type": r.get("relationship_type", "roommate"),
                "assigned_role": r.get("assigned_role"),
                "status": r.get("status", "active"),
            }
        )
    return out


def append_activity(moment: MomentModel, item: dict) -> dict:
    return append_item(moment, "activities", item)


def list_activities(moment: MomentModel) -> list[dict]:
    """Return timeline activities, backfilling any missing persisted ids."""
    return ensure_activity_ids(moment)


def ensure_activity_ids(moment: MomentModel) -> list[dict]:
    """Persist ids on timeline rows that were stored without one.

    Pulse/edit flows must never invent ephemeral ids — those 404 on GET/PATCH/DELETE.
    """
    state = read_state(moment)
    activities = state["runtime"].setdefault("activities", [])
    changed = False
    for item in activities:
        if not str(item.get("id") or "").strip():
            item["id"] = new_id()
            changed = True
    if changed:
        write_state(moment, state)
    return list(activities)


def memory_count(moment: MomentModel) -> int:
    return len(list_items(moment, "memories"))


def plan_count(moment: MomentModel) -> int:
    return len(list_items(moment, "plans"))


def profile_code(moment: MomentModel) -> str | None:
    return read_state(moment).get("profile_code")


def new_id() -> str:
    return uuid4().hex


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def to_minor(value) -> int:
    if value in (None, ""):
        return 0
    try:
        return int(round(float(str(value)) * 100))
    except (ValueError, TypeError):
        return 0
