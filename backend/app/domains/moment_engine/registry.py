"""Domain registry — maps context keys to template, adapter, and service.

MomentEngine resolves everything through this registry so lifecycle code never
branches on ``if context == "GROUP"``. Routers and facades can look up the
registered service class when wiring dependency injection.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, TypeVar

from app.domains.moment_engine.adapters import MomentAdapter, SharedMomentsAdapter
from app.domains.moment_engine.templates import MomentTemplate

AdapterFactory = Callable[[Any], MomentAdapter]
ServiceT = TypeVar("ServiceT")


@dataclass(slots=True)
class DomainRegistration:
    context: str
    template: MomentTemplate
    adapter_factory: AdapterFactory
    service: type | None = None


class DomainRegistry:
    def __init__(self) -> None:
        self._domains: dict[str, DomainRegistration] = {}

    def register(
        self,
        context: str,
        *,
        template: MomentTemplate,
        adapter_factory: AdapterFactory,
        service: type | None = None,
    ) -> None:
        self._domains[context] = DomainRegistration(
            context=context,
            template=template,
            adapter_factory=adapter_factory,
            service=service,
        )

    def get(self, context: str) -> DomainRegistration:
        key = context.upper()
        if key not in self._domains:
            raise KeyError(f"No domain registered for context {context!r}")
        return self._domains[key]

    def resolve_template(self, context: str, moment_type: str | None) -> MomentTemplate:
        reg = self.get(context)
        if moment_type and reg.template.moment_type == moment_type:
            return reg.template
        if reg.template.moment_type is None:
            return reg.template
        # Per-type override when a domain registers additional templates later.
        return reg.template

    def adapter(self, session: Any, context: str) -> MomentAdapter:
        return self.get(context).adapter_factory(session)

    def contexts(self) -> tuple[str, ...]:
        return tuple(sorted(self._domains))


_registry = DomainRegistry()


def get_domain_registry() -> DomainRegistry:
    return _registry


def register_default_domains() -> None:
    """Register Personal, Group, and Business domains (idempotent)."""
    reg = get_domain_registry()
    if reg._domains:
        return

    reg.register(
        context="MY_MONEY",
        template=MomentTemplate(
            context="MY_MONEY",
            initial_status="DRAFT",
            initial_setup_state="SETUP",
            worker_context="personal",
            refresh_on_create=True,
            refresh_on_activate=True,
        ),
        adapter_factory=lambda session: SharedMomentsAdapter(session, context="MY_MONEY"),
    )

    reg.register(
        context="GROUP",
        template=MomentTemplate(
            context="GROUP",
            initial_status="DRAFT",
            worker_context="group",
            refresh_on_create=True,
            refresh_on_activate=True,
        ),
        adapter_factory=lambda session: SharedMomentsAdapter(session, context="GROUP"),
        service=_lazy_service("app.domains.group.group_service", "GroupService"),
    )

    reg.register(
        context="BUSINESS",
        template=MomentTemplate(
            context="BUSINESS",
            initial_status="DRAFT",
            worker_context="business",
            refresh_on_create=True,
            refresh_on_activate=True,
        ),
        adapter_factory=lambda session: SharedMomentsAdapter(session, context="BUSINESS"),
        service=_lazy_service("app.domains.business.services.moments", "BusinessMomentsModule"),
    )

    reg.register(
        context="PERSONAL",
        template=MomentTemplate(
            context="PERSONAL",
            initial_status="DRAFT",
            worker_context="personal",
            refresh_on_create=True,
            refresh_on_activate=True,
        ),
        adapter_factory=lambda session: SharedMomentsAdapter(session, context="PERSONAL"),
    )


def _lazy_service(module_path: str, class_name: str) -> type:
    import importlib

    return getattr(importlib.import_module(module_path), class_name)


def register_default_templates() -> None:
    """Backward-compatible alias — templates now live on the domain registry."""
    register_default_domains()
