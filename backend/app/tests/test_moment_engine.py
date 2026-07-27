from __future__ import annotations

from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from app.core.errors import NotFoundError, StateTransitionError
from app.domains.moment_engine.adapters import SharedMomentsAdapter
from app.domains.moment_engine.engine import MomentEngine
from app.domains.moment_engine.state import assert_transition
from app.domains.moment_engine.registry import register_default_domains
from app.domains.personal.catalog import PERSONAL_CONTEXT
from app.domains.users.models import UserModel
from app.shared.events.bus import EventBus


def test_state_transitions_allow_activate_from_draft():
    assert_transition("DRAFT", "ACTIVE")


def test_state_transitions_reject_archive_from_draft_to_completed():
    with pytest.raises(StateTransitionError):
        assert_transition("DRAFT", "COMPLETED")


@patch("app.dependencies.auth.verify_firebase_token")
@patch("app.core.config.settings")
@patch("app.workers.tasks.snapshots.refresh_snapshots")
@patch("app.workers.tasks.memory.refresh_memory")
@patch("app.workers.tasks.analytics.refresh_analytics")
@pytest.mark.celery_enqueue
def test_personal_create_enqueues_refresh_jobs(
    mock_analytics,
    mock_memory,
    mock_snapshots,
    mock_settings,
    mock_verify,
    client,
    mock_db,
    sample_user: UserModel,
):
    mock_verify.return_value = {"uid": "test123", "email": "test@example.com"}
    type(mock_settings).effective_celery_broker = PropertyMock(return_value="redis://localhost/0")
    mock_snapshots.delay = MagicMock()
    mock_memory.delay = MagicMock()
    mock_analytics.delay = MagicMock()
    mock_db.add(sample_user)

    resp = client.post(
        "/api/v1/personal/moments",
        json={"moment_type_code": "LIFE_OPERATIONS", "moment_name": "Engine Test"},
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code == 201
    mock_snapshots.delay.assert_called_once()
    mock_memory.delay.assert_called_once()
    mock_analytics.delay.assert_called_once()


@pytest.mark.asyncio
@patch("app.core.config.settings")
async def test_moment_created_handlers_update_module_state(
    mock_settings, mock_db, sample_user: UserModel
):
    from app.domains.moment_engine.handlers import register_moment_handlers
    from app.domains.moment_engine.handlers.moment_created import MOMENT_CREATED_HANDLERS
    from app.domains.moment_engine.handlers.sync.update_module_state import (
        UpdateModuleStateHandler,
    )

    type(mock_settings).effective_celery_broker = PropertyMock(return_value="")
    register_default_domains()
    register_moment_handlers()
    adapter = SharedMomentsAdapter(mock_db, context=PERSONAL_CONTEXT)
    mock_db.add(sample_user)
    engine = MomentEngine()

    await engine.create(adapter, sample_user.id, moment_type="LIFE_OPERATIONS", title="Ops")

    handler_types = {type(h) for h in MOMENT_CREATED_HANDLERS}
    assert UpdateModuleStateHandler in handler_types
    assert any(
        ms.state == "ACTIVE" and "MY_MONEY" in key
        for key, ms in mock_db._stores["module_states"].items()
    )


@pytest.mark.asyncio
async def test_engine_create_uses_template_defaults(mock_db, sample_user: UserModel):
    register_default_domains()
    bus = EventBus()
    published: list[str] = []

    async def _capture(event):
        published.append(event.name)

    bus.subscribe("moment.created", _capture)

    class _BusPublisher:
        async def publish(self, event):
            await bus.publish(event)

    engine = MomentEngine(publisher=_BusPublisher())
    adapter = SharedMomentsAdapter(mock_db, context=PERSONAL_CONTEXT)
    mock_db.add(sample_user)

    ref = await engine.create(
        adapter,
        sample_user.id,
        moment_type="LIFE_OPERATIONS",
        title="Ops",
    )
    assert ref.status == "DRAFT"
    assert ref.setup_state == "ACTIVE"
    assert "moment.created" in published


@pytest.mark.asyncio
async def test_engine_delete_draft_only(mock_db, sample_user: UserModel):
    register_default_domains()
    adapter = SharedMomentsAdapter(mock_db, context=PERSONAL_CONTEXT)
    mock_db.add(sample_user)
    engine = MomentEngine()

    ref = await engine.create(
        adapter,
        sample_user.id,
        moment_type="LIFE_OPERATIONS",
        title="Delete me",
    )
    await engine.delete(adapter, sample_user.id, ref.moment_id)

    with pytest.raises(NotFoundError):
        await adapter.get_owned(sample_user.id, ref.moment_id)


def test_domain_registry_resolves_contexts():
    from app.domains.moment_engine.registry import get_domain_registry, register_default_domains

    register_default_domains()
    reg = get_domain_registry()
    assert "MY_MONEY" in reg.contexts()
    assert "GROUP" in reg.contexts()
    assert "BUSINESS" in reg.contexts()
    group = reg.get("GROUP")
    assert group.template.worker_context == "group"
    assert group.service is not None
