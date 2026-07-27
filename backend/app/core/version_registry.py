"""Platform version registry for granular client cache invalidation."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PlatformVersions:
    reference_data_version: int = 1
    template_version: int = 1
    ui_schema_version: int = 1
    quick_add_version: int = 1
    setup_version: int = 1

    @property
    def metadata_version(self) -> int:
        """Aggregate version for backward compatibility."""
        return max(
            self.reference_data_version,
            self.template_version,
            self.ui_schema_version,
            self.quick_add_version,
            self.setup_version,
        )

    def as_dict(self) -> dict[str, int]:
        return {
            "reference_data_version": self.reference_data_version,
            "template_version": self.template_version,
            "ui_schema_version": self.ui_schema_version,
            "quick_add_version": self.quick_add_version,
            "setup_version": self.setup_version,
            "metadata_version": self.metadata_version,
        }


_registry = PlatformVersions(reference_data_version=18)


def get_platform_versions() -> PlatformVersions:
    return _registry


def bump_version(domain: str, amount: int = 1) -> int:
    """Bump a domain version and return the new value."""
    global _registry
    attr = f"{domain}_version"
    if not hasattr(_registry, attr):
        raise ValueError(f"Unknown version domain: {domain}")
    current = getattr(_registry, attr)
    new_val = current + amount
    _registry = PlatformVersions(
        reference_data_version=_registry.reference_data_version,
        template_version=_registry.template_version,
        ui_schema_version=_registry.ui_schema_version,
        quick_add_version=_registry.quick_add_version,
        setup_version=_registry.setup_version,
    )
    setattr(_registry, attr, new_val)
    # Rebuild dataclass since it's frozen-ish usage
    versions = PlatformVersions(
        reference_data_version=_registry.reference_data_version,
        template_version=_registry.template_version,
        ui_schema_version=_registry.ui_schema_version,
        quick_add_version=_registry.quick_add_version,
        setup_version=_registry.setup_version,
    )
    setattr(versions, attr, new_val)
    _registry = versions
    return new_val


def sync_reference_data_version(version: int) -> None:
    global _registry
    _registry = PlatformVersions(
        reference_data_version=version,
        template_version=_registry.template_version,
        ui_schema_version=_registry.ui_schema_version,
        quick_add_version=_registry.quick_add_version,
        setup_version=_registry.setup_version,
    )
