"""CONNECTION → personal_relationship_connection_events."""
from __future__ import annotations

from typing import Any

from app.domains.personal.life_operations.quick_add.handlers.base import (
    QuickAddContext,
    TimelineDraft,
)
from app.domains.personal.models import PersonalRelationshipConnectionEvents
from app.domains.personal.quick_add.enum_utils import normalize_choice
from app.domains.personal.relationships.quick_add.handlers.base import notes_for, payload_for
from app.domains.personal.relationships.quick_add.handlers.mappings import (
    CONNECTION_QUALITIES,
    CONNECTION_TYPES,
    EMOTIONAL_TONE_ALIASES,
    EMOTIONAL_TONE_VALUES,
    RELATIONSHIP_TYPE_ALIASES,
    RELATIONSHIP_TYPES,
    TIME_INVESTED_ALIASES,
    TIME_INVESTED_VALUES,
)


def resolve_optional_enum(
    value: Any,
    *,
    valid: set[str],
    aliases: dict[str, str],
) -> str | None:
    if value is None or str(value).strip() == "":
        return None
    raw = str(value).strip()
    mapped = aliases.get(raw) or aliases.get(raw.upper()) or aliases.get(raw.lower())
    if mapped:
        return mapped
    if raw in valid:
        return raw
    upper = raw.upper()
    for candidate in valid:
        if candidate.upper() == upper:
            return candidate
    return None


class ConnectionHandler:
    event_type = "CONNECTION"

    async def handle(self, ctx: QuickAddContext) -> TimelineDraft:
        data = payload_for(ctx)
        connection_type = normalize_choice(
            data.get("connection_type"),
            CONNECTION_TYPES,
            "Other",
        )
        relationship_type = normalize_choice(
            data.get("relationship_type"),
            RELATIONSHIP_TYPES,
            "Friend",
            aliases=RELATIONSHIP_TYPE_ALIASES,
        )
        quality = normalize_choice(
            data.get("connection_quality"),
            CONNECTION_QUALITIES,
            "Meaningful",
        )
        emotional_tone = resolve_optional_enum(
            data.get("emotional_tone"),
            valid=EMOTIONAL_TONE_VALUES,
            aliases=EMOTIONAL_TONE_ALIASES,
        )
        time_invested = resolve_optional_enum(
            data.get("time_invested"),
            valid=TIME_INVESTED_VALUES,
            aliases=TIME_INVESTED_ALIASES,
        )
        row = PersonalRelationshipConnectionEvents(
            quick_add_event_id=ctx.quick_add_event_id,
            moment_id=ctx.moment_id,
            user_id=ctx.user_id,
            connection_type=connection_type,
            relationship_type=relationship_type,
            connection_quality=quality,
            emotional_tone=emotional_tone,
            time_invested_bucket=time_invested,
            note=notes_for(ctx, data),
        )
        ctx.session.add(row)
        await ctx.session.flush()
        return TimelineDraft(
            display_title=ctx.event_title,
            display_subtitle=f"{connection_type} · {quality}",
            impact_labels={
                "connection_type": connection_type,
                "relationship_type": relationship_type,
            },
        )
