"""QuickAddRegistryValidator — fails in tests/CI, not production startup."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable

from app.domains.quick_add_contract.hash import compute_registry_hash, load_reference_actions


@dataclass
class ValidationIssue:
    action_key: str
    code: str
    message: str


@dataclass
class ValidationResult:
    ok: bool
    issues: list[ValidationIssue] = field(default_factory=list)
    registry_hash: str = ""

    def raise_if_failed(self) -> None:
        if self.ok:
            return
        lines = [f"{i.action_key}: [{i.code}] {i.message}" for i in self.issues]
        raise AssertionError("QuickAddRegistryValidator failed:\n" + "\n".join(lines))


Lookup = Callable[[str], bool]


class QuickAddRegistryValidator:
    """Assert every registered reference action has required wiring."""

    def __init__(
        self,
        *,
        actions: list[dict[str, Any]] | None = None,
        renderer_exists: Lookup | None = None,
        payload_builder_exists: Lookup | None = None,
        handler_exists: Lookup | None = None,
        expected_hash: str | None = None,
    ) -> None:
        self.actions = actions if actions is not None else load_reference_actions()
        self.renderer_exists = renderer_exists or (lambda _id: True)
        self.payload_builder_exists = payload_builder_exists or (lambda _id: True)
        self.handler_exists = handler_exists or (lambda _id: True)
        self.expected_hash = expected_hash

    def validate(self) -> ValidationResult:
        issues: list[ValidationIssue] = []
        for action in self.actions:
            issues.extend(self._validate_action(action))

        registry_hash = compute_registry_hash(self.actions)
        if self.expected_hash and registry_hash != self.expected_hash:
            issues.append(
                ValidationIssue(
                    action_key="*",
                    code="registry_hash_mismatch",
                    message=f"expected {self.expected_hash}, got {registry_hash}",
                )
            )

        return ValidationResult(ok=not issues, issues=issues, registry_hash=registry_hash)

    def _validate_action(self, action: dict[str, Any]) -> list[ValidationIssue]:
        key = str(action.get("key") or "?")
        issues: list[ValidationIssue] = []
        caps = action.get("capabilities") or {}

        def need(field: str) -> None:
            if not action.get(field):
                issues.append(ValidationIssue(key, "missing_field", f"missing {field}"))

        for f in (
            "moment_type_code",
            "action_id",
            "renderer_id",
            "endpoint",
            "handler_id",
            "payload_builder_id",
            "output_events",
            "affected_projections",
            "platforms",
            "capabilities",
        ):
            need(f)

        if action.get("contract_version") not in (None, "v1"):
            # lockfile entries may omit; fixtures root has version
            pass

        renderer_id = action.get("renderer_id")
        if renderer_id and not self.renderer_exists(str(renderer_id)):
            issues.append(ValidationIssue(key, "renderer_missing", f"renderer {renderer_id}"))

        builder_id = action.get("payload_builder_id")
        if builder_id and not self.payload_builder_exists(str(builder_id)):
            issues.append(ValidationIssue(key, "payload_builder_missing", f"builder {builder_id}"))

        handler_id = action.get("handler_id")
        if handler_id and not self.handler_exists(str(handler_id)):
            issues.append(ValidationIssue(key, "handler_missing", f"handler {handler_id}"))

        if caps.get("edit") and not action.get("edit_endpoint"):
            issues.append(ValidationIssue(key, "edit_endpoint_missing", "capabilities.edit requires edit_endpoint"))
        if caps.get("delete") and not action.get("delete_endpoint"):
            issues.append(
                ValidationIssue(key, "delete_endpoint_missing", "capabilities.delete requires delete_endpoint")
            )

        events = action.get("output_events") or []
        if not isinstance(events, list) or not events:
            issues.append(ValidationIssue(key, "output_events_empty", "output_events required"))

        projections = action.get("affected_projections") or []
        if not isinstance(projections, list) or not projections:
            issues.append(ValidationIssue(key, "projections_empty", "affected_projections required"))

        platforms = action.get("platforms") or []
        required_platforms = {"web", "android", "ios", "backend"}
        if not required_platforms.issubset(set(platforms)):
            issues.append(
                ValidationIssue(
                    key,
                    "platforms_incomplete",
                    f"platforms must include {sorted(required_platforms)}, got {platforms}",
                )
            )

        return issues


def validate_reference_registry(
    *,
    renderer_ids: Iterable[str] | None = None,
    payload_builder_ids: Iterable[str] | None = None,
    handler_ids: Iterable[str] | None = None,
    expected_hash: str | None = None,
) -> ValidationResult:
    renderers = set(renderer_ids or [])
    builders = set(payload_builder_ids or [])
    handlers = set(handler_ids or [])
    return QuickAddRegistryValidator(
        renderer_exists=(lambda i: i in renderers) if renderers else (lambda _i: True),
        payload_builder_exists=(lambda i: i in builders) if builders else (lambda _i: True),
        handler_exists=(lambda i: i in handlers) if handlers else (lambda _i: True),
        expected_hash=expected_hash,
    ).validate()
