"""Shared Business setup service (draft → preview → activate)."""
from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.domains.app_bootstrap.service import AppBootstrapService
from app.domains.business.catalog import (
    BUSINESS_CONTEXT,
    BUSINESS_OPERATIONS,
    BUSINESS_RUNWAY,
    TEAM_OPERATIONS,
    V1_CREATABLE_CODES,
    business_type_id,
    business_type_name,
    normalize_moment_type_code,
)
from app.domains.business.setup import draft_store
from app.domains.business.setup.adapters import get_adapter
from app.domains.business.setup.business_moment_sync import ensure_business_moment
from app.domains.business.setup.invites import build_invite_draft_payload
from app.domains.business.setup.normalizers import normalize_template_id
from app.domains.business.setup.schemas import (
    ActivateResponse,
    MembershipRecord,
    SetupProgress,
    SetupStateResponse,
)
from app.domains.moment_engine.engine import MomentEngine
from app.domains.moment_engine.registry import get_domain_registry
from app.domains.module_states.service import ModuleStateService
from app.domains.moments.models import MomentModel

logger = logging.getLogger(__name__)


class BusinessSetupService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.engine = MomentEngine()
        self._adapter = get_domain_registry().adapter(session, BUSINESS_CONTEXT)
        self.modules = ModuleStateService(session)
        self.bootstrap = AppBootstrapService(session)

    async def _require_moment(self, user_id: UUID, moment_id: UUID) -> MomentModel:
        try:
            return await self._adapter.get_model(user_id, moment_id)
        except NotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Moment not found"
            ) from exc

    async def _flip_setup(self, user_id: UUID) -> None:
        await self.modules.set_state(user_id, "BUSINESS", "SETUP", "business_moment_draft")
        personal = await self.modules.get_state(user_id, "MY_MONEY")
        group = await self.modules.get_state(user_id, "GROUP")
        other_active = any(
            row and (row.state or "").upper() == "ACTIVE" for row in (personal, group)
        )
        if not other_active:
            await self.modules.set_state(user_id, "PULSE", "SETUP", "business_moment_draft")
        await self.bootstrap.invalidate_cache(user_id)

    async def _flip_active(self, user_id: UUID) -> None:
        await self.modules.set_state(user_id, "BUSINESS", "ACTIVE", "business_moment")
        await self.modules.set_state(user_id, "PULSE", "ACTIVE", "business_moment")
        await self.modules.set_state(user_id, "MOMENTS", "ACTIVE", "business_moment")
        await self.bootstrap.invalidate_cache(user_id)

    async def _owner_display_name(self, user_id: UUID) -> str:
        from sqlalchemy import select

        from app.domains.users.models import UserModel

        result = await self.session.execute(
            select(UserModel.display_name).where(UserModel.id == user_id)
        )
        name = result.scalar_one_or_none()
        if isinstance(name, str) and name.strip():
            return name.strip()
        return "You"

    async def _normalize(
        self,
        adapter: Any,
        answers: dict[str, Any],
        *,
        owner_user_id: UUID,
    ) -> dict[str, Any]:
        display = await self._owner_display_name(owner_user_id)
        return adapter.normalize_answers(
            answers,
            owner_user_id=str(owner_user_id),
            owner_display_name=display,
        )

    def _ensure_owner_answers(self, answers: dict[str, Any], owner_user_id: UUID, code: str) -> dict[str, Any]:
        adapter = get_adapter(code, self.session)
        return adapter.normalize_answers(answers, owner_user_id=str(owner_user_id), owner_display_name="You")

    def _state_response(self, moment: MomentModel, *, include_preview: bool = False) -> dict:
        env = draft_store.read_envelope(moment)
        code = normalize_moment_type_code(moment.moment_type or "") or (moment.moment_type or "")
        template_id = env.get("template_id") or normalize_template_id(None, code)
        answers = env.get("answers") or {}
        if code in {TEAM_OPERATIONS, BUSINESS_RUNWAY, BUSINESS_OPERATIONS}:
            answers = self._ensure_owner_answers(answers, moment.user_id, code)
        progress_raw = env.get("progress") or {}
        progress = SetupProgress(
            current_step=int(progress_raw.get("current_step") or 1),
            completed_steps=list(progress_raw.get("completed_steps") or []),
        )
        membership = [
            MembershipRecord(**m) if isinstance(m, dict) else m
            for m in (env.get("membership") or [])
        ]
        preview = None
        if include_preview:
            adapter = get_adapter(code, self.session)
            preview = adapter.build_preview(answers, owner_user_id=str(moment.user_id))
        updated = env.get("updated_at")
        if not updated and moment.updated_at:
            updated = moment.updated_at.isoformat()
        return SetupStateResponse(
            moment_id=str(moment.id),
            moment_type_code=code,
            status=moment.status,
            template_id=template_id,
            template_version=str(env.get("template_version") or "1"),
            setup_version=str(env.get("setup_version") or "1"),
            answers=answers,
            progress=progress,
            preview=preview,
            membership=membership,
            updated_at=updated,
        ).model_dump(mode="json")

    async def create_draft(
        self,
        user_id: UUID,
        *,
        moment_type_code: str,
        title: str | None = None,
        template_id: str | None = None,
        template_version: str | int | None = "1",
        workspace_id: UUID | None = None,
    ) -> dict:
        t0 = time.perf_counter()
        canonical = normalize_moment_type_code(moment_type_code)
        if canonical is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown business moment type: {moment_type_code}",
            )
        if canonical not in V1_CREATABLE_CODES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Moment type {canonical} is not available for create in v1",
            )
        if workspace_id is not None:
            from app.domains.business.workspace_service import BusinessWorkspaceService

            await BusinessWorkspaceService(self.session).require_member(workspace_id, user_id)

        tpl_id = normalize_template_id(template_id, canonical)
        name = title or business_type_name(canonical)
        envelope = draft_store.empty_envelope(
            template_id=tpl_id,
            template_version=str(template_version or "1"),
        )
        if title:
            envelope["answers"]["moment_name"] = title
        if workspace_id is not None:
            envelope["workspace_id"] = str(workspace_id)
        t_seed_start = time.perf_counter()
        if canonical in {TEAM_OPERATIONS, BUSINESS_RUNWAY, BUSINESS_OPERATIONS}:
            envelope["answers"] = self._ensure_owner_answers(envelope["answers"], user_id, canonical)
        seed_ms = int((time.perf_counter() - t_seed_start) * 1000)

        t_db_start = time.perf_counter()
        ref = await self.engine.create(
            self._adapter,
            user_id,
            moment_type=canonical,
            title=name,
            description=None,
            setup_state="SETUP",
        )
        moment = await self._adapter.get_model(user_id, ref.moment_id)
        draft_store.write_envelope(moment, envelope)
        if moment.status not in {"DRAFT", "SETUP"}:
            moment.status = "DRAFT"
        moment.setup_state = "SETUP"
        await ensure_business_moment(
            self.session,
            moment,
            owner_user_id=user_id,
            answers=envelope.get("answers") or {},
            workspace_id=workspace_id,
        )
        await self._flip_setup(user_id)
        db_ms = int((time.perf_counter() - t_db_start) * 1000)
        # Seeded setup fragment so clients can skip GET /setup on open.
        # Preview is never built here — clients request POST …/setup/preview on Review.
        state = self._state_response(moment, include_preview=False)
        total_ms = int((time.perf_counter() - t0) * 1000)
        logger.info(
            "event=BusinessSetupLoad op=create moment_id=%s type=%s "
            "seed_ms=%s db_ms=%s total_ms=%s preview=false",
            state.get("moment_id"),
            canonical,
            seed_ms,
            db_ms,
            total_ms,
        )
        return {
            **state,
            "moment_type_id": business_type_id(canonical),
            "moment_name": moment.title or name,
            "moment_description": None,
            "cover_image_url": None,
            "workspace_id": str(workspace_id) if workspace_id else None,
        }

    def _owner_missing_from_answers(self, answers: dict[str, Any], owner_user_id: UUID) -> bool:
        """True when repair write is needed (missing envelope members / owner row)."""
        members = answers.get("members") or answers.get("member_drafts") or []
        if not isinstance(members, list) or not members:
            return True
        uid = str(owner_user_id)
        for m in members:
            if not isinstance(m, dict):
                continue
            if str(m.get("user_id") or "") == uid and str(m.get("role") or "").upper() == "OWNER":
                return False
        return True

    async def get_setup_state(self, user_id: UUID, moment_id: UUID) -> dict:
        t0 = time.perf_counter()
        moment = await self._require_moment(user_id, moment_id)
        load_ms = int((time.perf_counter() - t0) * 1000)
        env = draft_store.read_envelope(moment)
        code = normalize_moment_type_code(moment.moment_type or "") or (moment.moment_type or "")
        missing_envelope = not env
        if missing_envelope:
            env = draft_store.empty_envelope(template_id=normalize_template_id(None, code))

        t_norm = time.perf_counter()
        repaired = False
        # Guarded migration/repair only — healthy drafts are read-only on GET.
        if code in {TEAM_OPERATIONS, BUSINESS_RUNWAY, BUSINESS_OPERATIONS}:
            raw_answers = env.get("answers") or {}
            if missing_envelope or self._owner_missing_from_answers(raw_answers, user_id):
                env["answers"] = self._ensure_owner_answers(raw_answers, user_id, code)
                draft_store.write_envelope(moment, env)
                repaired = True
        elif missing_envelope:
            draft_store.write_envelope(moment, env)
            repaired = True
        normalize_ms = int((time.perf_counter() - t_norm) * 1000)

        # Preview never built on GET — clients use POST …/setup/preview on Review.
        state = self._state_response(moment, include_preview=False)
        total_ms = int((time.perf_counter() - t0) * 1000)
        logger.info(
            "event=BusinessSetupLoad op=get moment_id=%s type=%s "
            "load_ms=%s normalize_ms=%s repaired=%s total_ms=%s preview=false",
            moment_id,
            code,
            load_ms,
            normalize_ms,
            repaired,
            total_ms,
        )
        return state

    async def save_draft(
        self,
        user_id: UUID,
        moment_id: UUID,
        *,
        answers: dict[str, Any] | None = None,
        progress: dict[str, Any] | None = None,
        template_id: str | None = None,
        template_version: str | int | None = None,
        setup_version: str | int | None = None,
    ) -> dict:
        moment = await self._require_moment(user_id, moment_id)
        if moment.status not in {"DRAFT", "SETUP"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot save draft for an activated moment",
            )
        code = normalize_moment_type_code(moment.moment_type or "") or (moment.moment_type or "")
        adapter = get_adapter(code, self.session)
        env = draft_store.read_envelope(moment) or draft_store.empty_envelope(
            template_id=normalize_template_id(template_id, code)
        )
        merged_incoming = draft_store.merge_answers(env.get("answers") or {}, answers or {})
        normalized = await self._normalize(adapter, merged_incoming, owner_user_id=user_id)
        env["answers"] = normalized
        if progress is not None:
            env["progress"] = {
                "current_step": int(progress.get("current_step") or 1),
                "completed_steps": list(progress.get("completed_steps") or []),
            }
        if template_id:
            env["template_id"] = normalize_template_id(template_id, code)
        if template_version is not None:
            env["template_version"] = str(template_version)
        if setup_version is not None:
            env["setup_version"] = str(setup_version)
        adapter.validate_draft(env["answers"])
        name = (
            env["answers"].get("moment_name")
            or env["answers"].get("operations_name")
            or env["answers"].get("runway_name")
            or env["answers"].get("team_name")
        )
        if name:
            moment.title = str(name)
        draft_store.write_envelope(moment, env)
        return self._state_response(moment)

    async def preview(
        self,
        user_id: UUID,
        moment_id: UUID,
        *,
        answers: dict[str, Any] | None = None,
    ) -> dict:
        moment = await self._require_moment(user_id, moment_id)
        code = normalize_moment_type_code(moment.moment_type or "") or (moment.moment_type or "")
        adapter = get_adapter(code, self.session)
        env = draft_store.read_envelope(moment) or draft_store.empty_envelope(
            template_id=normalize_template_id(None, code)
        )
        merged = draft_store.merge_answers(env.get("answers") or {}, answers or {})
        merged = await self._normalize(adapter, merged, owner_user_id=user_id)
        result = adapter.build_preview(merged, owner_user_id=str(user_id))
        return result.model_dump(mode="json")

    async def activate(self, user_id: UUID, moment_id: UUID) -> dict:
        moment = await self._require_moment(user_id, moment_id)
        code = normalize_moment_type_code(moment.moment_type or "") or (moment.moment_type or "")
        adapter = get_adapter(code, self.session)
        env = draft_store.read_envelope(moment) or draft_store.empty_envelope(
            template_id=normalize_template_id(None, code)
        )
        answers = await self._normalize(adapter, env.get("answers") or {}, owner_user_id=user_id)
        env["answers"] = answers

        if moment.status == "ACTIVE":
            # Heal split-brain: shared ACTIVE but legacy business_moments still configured.
            await ensure_business_moment(
                self.session,
                moment,
                owner_user_id=user_id,
                answers=answers,
            )
            await self.session.commit()
            membership = [
                MembershipRecord(**m) if isinstance(m, dict) else m
                for m in (env.get("membership") or [])
            ]
            if not membership:
                membership = [
                    MembershipRecord(
                        user_id=str(user_id),
                        role="OWNER",
                        status="ACTIVE",
                        invitation_status="ACCEPTED",
                    )
                ]
            return ActivateResponse(
                moment_id=str(moment.id),
                moment_type_code=code,
                status=moment.status,
                activated_at=env.get("activated_at"),
                membership=membership,
            ).model_dump(mode="json")

        errors = adapter.validate_activation(answers, owner_user_id=str(user_id))
        if errors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="; ".join(errors),
            )

        try:
            await adapter.commit_profile(
                moment_id=str(moment.id), user_id=str(user_id), answers=answers
            )
            await adapter.commit_governance(
                moment_id=str(moment.id), user_id=str(user_id), answers=answers
            )
            await adapter.commit_members(
                moment_id=str(moment.id), user_id=str(user_id), answers=answers
            )
        except HTTPException:
            raise
        except Exception as exc:  # noqa: BLE001
            from sqlalchemy.exc import IntegrityError, StatementError

            if isinstance(exc, (IntegrityError, StatementError)):
                logger.warning("Business activate commit failed: %s", exc)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Could not activate — check members and required fields, then retry",
                ) from exc
            raise

        owner = MembershipRecord(
            user_id=str(user_id),
            role="OWNER",
            status="ACTIVE",
            invitation_status="ACCEPTED",
        )
        env["membership"] = [owner.model_dump(mode="json")]
        activated_at = datetime.now(timezone.utc).isoformat()
        env["activated_at"] = activated_at
        draft_store.write_envelope(moment, env)

        if moment.status == "SETUP":
            moment.status = "DRAFT"
        await self.engine.activate(self._adapter, user_id, moment_id, setup_state="ACTIVE")
        await self._flip_active(user_id)

        # Promote legacy business_moments to active after shared moment is ACTIVE.
        moment = await self._adapter.get_model(user_id, moment_id)
        await ensure_business_moment(
            self.session,
            moment,
            owner_user_id=user_id,
            answers=answers,
        )

        await self.session.commit()

        # Invite delivery must not block activate response (client 30s timeout).
        deliver = getattr(adapter, "deliver_invites_best_effort", None)
        if deliver is not None:
            try:
                import asyncio

                from app.core.database import async_session_factory

                invite_answers = dict(answers)
                invite_moment_id = str(moment_id)

                async def _deliver_invites() -> None:
                    if async_session_factory is None:
                        return
                    async with async_session_factory() as invite_session:
                        try:
                            invite_adapter = get_adapter(code, invite_session)
                            invite_deliver = getattr(
                                invite_adapter, "deliver_invites_best_effort", None
                            )
                            if invite_deliver is None:
                                return
                            await invite_deliver(
                                moment_id=invite_moment_id, answers=invite_answers
                            )
                            await invite_session.commit()
                        except Exception:
                            await invite_session.rollback()
                            raise

                task = asyncio.create_task(_deliver_invites())

                def _invite_done(done: asyncio.Task[None]) -> None:
                    try:
                        done.result()
                    except Exception as invite_exc:  # noqa: BLE001
                        logger.warning(
                            "Invite delivery after activate failed (non-blocking): %s",
                            invite_exc,
                        )

                task.add_done_callback(_invite_done)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Invite delivery schedule failed (non-blocking): %s", exc)

        moment = await self._adapter.get_model(user_id, moment_id)

        # Post-commit warmup: never hold the activation transaction open.
        # 1) Enqueue Life/Memory Celery
        # 2) Bounded best-effort Pulse+Moments warm on a *separate* session
        #    (timeout/cancel must not invalidate the request session for get_db).
        # Warmup failure must not roll back activation.
        try:
            import asyncio

            from app.core.database import async_session_factory
            from app.domains.business.active_service import BusinessActiveService
            from app.domains.business.projection_cache import (
                enqueue_business_user_agg_refresh,
                invalidate_business_projections,
            )

            enqueue_business_user_agg_refresh(user_id, reason="activate_warmup")

            async def _warm_pulse_moments() -> None:
                if async_session_factory is None:
                    return
                async with async_session_factory() as warm_session:
                    try:
                        await BusinessActiveService(
                            warm_session
                        )._build_all_moment_slices(user_id, moment_id, code)
                        await warm_session.commit()
                    except Exception:
                        await warm_session.rollback()
                        raise

            try:
                # Fire-and-forget warm on a separate session — do not block activate response.
                task = asyncio.create_task(_warm_pulse_moments())

                def _warm_done(done: asyncio.Task[None]) -> None:
                    try:
                        done.result()
                    except Exception as warm_exc:  # noqa: BLE001
                        logger.debug(
                            "Business Pulse/Moments warmup failed (non-blocking): %s: %s",
                            type(warm_exc).__name__,
                            warm_exc,
                        )
                        try:
                            loop = asyncio.get_running_loop()
                            loop.create_task(
                                invalidate_business_projections(
                                    user_id,
                                    moment_id,
                                    moment_type=code,
                                    reason="activate_warmup_fallback",
                                )
                            )
                        except Exception:  # noqa: BLE001
                            pass

                task.add_done_callback(_warm_done)
            except Exception as warm_exc:  # noqa: BLE001
                logger.debug(
                    "Business Pulse/Moments warmup schedule failed (non-blocking): %s: %s",
                    type(warm_exc).__name__,
                    warm_exc,
                )
                try:
                    await invalidate_business_projections(
                        user_id,
                        moment_id,
                        moment_type=code,
                        reason="activate_warmup_fallback",
                    )
                except Exception:  # noqa: BLE001
                    pass
        except Exception as exc:  # noqa: BLE001
            logger.debug(
                "Business projection warmup failed (non-blocking): %s: %s",
                type(exc).__name__,
                exc,
            )

        return ActivateResponse(
            moment_id=str(moment.id),
            moment_type_code=code,
            status=moment.status,
            activated_at=activated_at,
            membership=[owner],
            projection_status="REFRESHING",
        ).model_dump(mode="json")

    async def _require_owner(self, user_id: UUID, moment: MomentModel) -> None:
        if moment.user_id != user_id:
            from app.domains.moment_engine.lifecycle_contract import deny_access
            from app.domains.business.catalog import BUSINESS_CONTEXT

            raise deny_access(
                context_type=BUSINESS_CONTEXT,
                moment_id=moment.id,
                moment_type=moment.moment_type,
                user_id=user_id,
                action="archive_or_complete",
                denial_reason="moment_not_owned",
                message="Only the moment owner may archive or complete this business moment.",
                owner_match=False,
                required_capability="activate_archive_complete",
            )

    def _lifecycle_payload(
        self,
        moment: MomentModel,
        *,
        previous_status: str | None = None,
        module_state: str | None = None,
        replacement_moment_id: str | None = None,
        replacement_moment_type_code: str | None = None,
    ) -> dict:
        from app.domains.moment_engine.lifecycle_contract import build_lifecycle_response
        from app.domains.business.catalog import BUSINESS_CONTEXT

        code = normalize_moment_type_code(moment.moment_type or "") or (moment.moment_type or "")
        return build_lifecycle_response(
            moment=moment,
            context_type=BUSINESS_CONTEXT,
            previous_status=previous_status or moment.status,
            module_state=module_state,
            replacement_moment_id=replacement_moment_id,
            replacement_moment_type_code=replacement_moment_type_code,
            extra={"moment_type_code": code},
        )

    async def _after_lifecycle_change(
        self,
        user_id: UUID,
        moment_id: UUID,
        *,
        code: str,
        reason: str,
    ) -> None:
        await self.modules.set_state(user_id, "BUSINESS", "SETUP", reason)
        await self.modules.set_state(user_id, "PULSE", "SETUP", reason)
        await self.modules.set_state(user_id, "MOMENTS", "SETUP", reason)
        await self.bootstrap.invalidate_cache(user_id)
        try:
            from app.domains.business.projection_cache import invalidate_business_projections

            await invalidate_business_projections(
                user_id, moment_id, moment_type=code, reason=reason
            )
        except Exception as exc:  # noqa: BLE001
            logger.debug("Business projection invalidate after lifecycle failed: %s", exc)

    async def archive(self, user_id: UUID, moment_id: UUID) -> dict:
        """Archive via shared MomentEngine (Team Ops / Runway / Ops)."""
        moment = await self._require_moment(user_id, moment_id)
        await self._require_owner(user_id, moment)
        previous = moment.status
        code = normalize_moment_type_code(moment.moment_type or "") or (moment.moment_type or "")
        if code not in {TEAM_OPERATIONS, BUSINESS_RUNWAY, BUSINESS_OPERATIONS}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Archive is only supported for v1 business templates via setup service.",
            )
        env = draft_store.read_envelope(moment) or {}
        answers = env.get("answers") or {}
        await self.engine.archive(self._adapter, user_id, moment_id)
        moment = await self._adapter.get_model(user_id, moment_id)
        await ensure_business_moment(
            self.session,
            moment,
            owner_user_id=user_id,
            answers=answers,
        )
        await self._after_lifecycle_change(
            user_id, moment_id, code=code, reason="business_moment_archived"
        )
        await self.session.commit()
        moment = await self._adapter.get_model(user_id, moment_id)
        from app.domains.moment_engine.lifecycle_contract import pick_replacement_moment, log_lifecycle_transition
        from app.domains.moments.repository import MomentRepository

        inventory = [
            m
            for m in await MomentRepository(self.session).list_by_context(user_id, BUSINESS_CONTEXT)
            if (m.status or "").upper() not in {"ARCHIVED", "DELETED"}
        ]
        repl_id, repl_type = pick_replacement_moment(inventory, exclude_id=moment.id)
        log_lifecycle_transition(
            context_type=BUSINESS_CONTEXT,
            moment_id=moment.id,
            moment_type=code,
            action="archive",
            previous_status=previous,
            final_status=moment.status,
            module_state="SETUP",
            replacement_moment_id=repl_id,
        )
        return self._lifecycle_payload(
            moment,
            previous_status=previous,
            module_state="SETUP",
            replacement_moment_id=repl_id,
            replacement_moment_type_code=repl_type,
        )

    async def delete(self, user_id: UUID, moment_id: UUID) -> dict:
        """Permanent purge via MomentPurgeService (ops cleared, analytics kept)."""
        from app.domains.moment_engine.lifecycle_contract import (
            log_lifecycle_transition,
            pick_replacement_moment,
        )
        from app.domains.moments.purge_service import MomentPurgeService
        from app.domains.moments.repository import MomentRepository

        moment = await self._require_moment(user_id, moment_id)
        await self._require_owner(user_id, moment)
        previous = moment.status
        code = normalize_moment_type_code(moment.moment_type or "") or (moment.moment_type or "")
        moment = await MomentPurgeService(self.session).purge(
            user_id, moment_id, expected_context=BUSINESS_CONTEXT
        )
        await self._after_lifecycle_change(
            user_id, moment_id, code=code, reason="business_moment_deleted"
        )
        await self.session.commit()
        inventory = [
            m
            for m in await MomentRepository(self.session).list_by_context(
                user_id, BUSINESS_CONTEXT
            )
            if (m.status or "").upper() not in {"ARCHIVED", "DELETED"}
        ]
        repl_id, repl_type = pick_replacement_moment(inventory, exclude_id=moment.id)
        log_lifecycle_transition(
            context_type=BUSINESS_CONTEXT,
            moment_id=moment.id,
            moment_type=code,
            action="delete",
            previous_status=previous,
            final_status=moment.status,
            module_state="SETUP",
            replacement_moment_id=repl_id,
        )
        return self._lifecycle_payload(
            moment,
            previous_status=previous,
            module_state="SETUP",
            replacement_moment_id=repl_id,
            replacement_moment_type_code=repl_type,
        )

    async def leave(self, user_id: UUID, moment_id: UUID) -> dict:
        """Active member exits self; owner must archive/delete instead."""
        from sqlalchemy import select

        from app.domains.business.access import require_business_moment_access
        from app.domains.business.models import BusinessMomentMembers
        from app.domains.moment_engine.lifecycle_contract import (
            deny_access,
            log_lifecycle_transition,
            pick_replacement_moment,
        )
        from app.domains.moments.repository import MomentRepository

        moment = await require_business_moment_access(self.session, user_id, moment_id)
        if (moment.context_type or "").upper() != BUSINESS_CONTEXT:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Moment not found"
            )
        if moment.user_id == user_id:
            raise deny_access(
                context_type=BUSINESS_CONTEXT,
                moment_id=moment_id,
                moment_type=moment.moment_type,
                user_id=user_id,
                action="leave",
                denial_reason="owner_cannot_leave",
                message="Owners must archive or delete the moment.",
                owner_match=True,
                membership_found=True,
            )

        previous = moment.status
        code = normalize_moment_type_code(moment.moment_type or "") or (
            moment.moment_type or ""
        )

        result = await self.session.execute(
            select(BusinessMomentMembers).where(
                BusinessMomentMembers.moment_id == moment_id,
                BusinessMomentMembers.user_id == user_id,
            )
        )
        for row in result.scalars().all():
            if (row.member_status or "").lower() == "removed":
                continue
            row.member_status = "removed"

        await self.session.flush()

        inventory = [
            m
            for m in await MomentRepository(self.session).list_business_accessible(
                user_id
            )
            if (m.status or "").upper() not in {"ARCHIVED", "DELETED"}
            and m.id != moment.id
        ]
        if inventory:
            await self.bootstrap.invalidate_cache(user_id)
            try:
                from app.domains.business.projection_cache import (
                    invalidate_business_projections,
                )

                await invalidate_business_projections(
                    user_id, moment_id, moment_type=code, reason="business_moment_left"
                )
            except Exception as exc:  # noqa: BLE001
                logger.debug("Business projection invalidate after leave failed: %s", exc)
            module_state = "ACTIVE"
        else:
            await self._after_lifecycle_change(
                user_id, moment_id, code=code, reason="business_moment_left"
            )
            module_state = "SETUP"

        await self.session.commit()
        repl_id, repl_type = pick_replacement_moment(inventory, exclude_id=moment.id)
        log_lifecycle_transition(
            context_type=BUSINESS_CONTEXT,
            moment_id=moment.id,
            moment_type=code,
            action="leave",
            previous_status=previous,
            final_status=moment.status,
            module_state=module_state,
            replacement_moment_id=repl_id,
        )
        return self._lifecycle_payload(
            moment,
            previous_status=previous,
            module_state=module_state,
            replacement_moment_id=repl_id,
            replacement_moment_type_code=repl_type,
        )

    async def complete(self, user_id: UUID, moment_id: UUID) -> dict:
        """Complete via shared MomentEngine (Team Ops / Runway / Ops)."""
        moment = await self._require_moment(user_id, moment_id)
        await self._require_owner(user_id, moment)
        previous = moment.status
        code = normalize_moment_type_code(moment.moment_type or "") or (moment.moment_type or "")
        if code not in {TEAM_OPERATIONS, BUSINESS_RUNWAY, BUSINESS_OPERATIONS}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Complete is only supported for v1 business templates via setup service.",
            )
        env = draft_store.read_envelope(moment) or {}
        answers = env.get("answers") or {}
        await self.engine.complete(self._adapter, user_id, moment_id)
        moment = await self._adapter.get_model(user_id, moment_id)
        await ensure_business_moment(
            self.session,
            moment,
            owner_user_id=user_id,
            answers=answers,
        )
        await self._after_lifecycle_change(
            user_id, moment_id, code=code, reason="business_moment_completed"
        )
        await self.session.commit()
        moment = await self._adapter.get_model(user_id, moment_id)
        from app.domains.moment_engine.lifecycle_contract import pick_replacement_moment, log_lifecycle_transition
        from app.domains.moments.repository import MomentRepository

        inventory = [
            m
            for m in await MomentRepository(self.session).list_by_context(user_id, BUSINESS_CONTEXT)
            if (m.status or "").upper() not in {"ARCHIVED", "DELETED"}
        ]
        repl_id, repl_type = pick_replacement_moment(
            inventory, exclude_id=moment.id, preferred_id=None
        )
        # Completed moment remains viewable — prefer keeping it selected when still selectable.
        repl_id, repl_type = pick_replacement_moment(
            inventory, preferred_id=moment.id
        )
        log_lifecycle_transition(
            context_type=BUSINESS_CONTEXT,
            moment_id=moment.id,
            moment_type=code,
            action="complete",
            previous_status=previous,
            final_status=moment.status,
            module_state="ACTIVE",
            replacement_moment_id=repl_id,
        )
        return self._lifecycle_payload(
            moment,
            previous_status=previous,
            module_state="ACTIVE",
            replacement_moment_id=repl_id,
            replacement_moment_type_code=repl_type,
        )

    async def invite_draft(
        self,
        user_id: UUID,
        moment_id: UUID,
        *,
        local_id: str | None = None,
        channel: str = "EMAIL",
        role: str | None = None,
    ) -> dict:
        from secrets import token_hex

        from sqlalchemy import select

        from app.domains.business.models import BusinessMomentInvitations
        from app.domains.business.setup.invite_roles import validate_invitee_role
        from app.domains.business.setup.invites import mint_and_bind_invitation
        from app.domains.invites.platform_service import (
            PlatformInviteService,
            opaque_creates_enabled,
        )

        moment = await self._require_moment(user_id, moment_id)
        await self._require_can_invite_members(user_id, moment)

        env = draft_store.read_envelope(moment) or {}
        answers = dict(env.get("answers") or {})
        members: list = list(answers.get("members") or [])
        if not isinstance(members, list):
            members = []

        resolved_role: str | None = None
        if role is not None and str(role).strip():
            try:
                resolved_role = validate_invitee_role(
                    role, moment_type=moment.moment_type
                )
            except ValueError as exc:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=str(exc),
                ) from exc

        lid = (local_id or "").strip() or None
        member: dict | None = None
        if lid:
            member = next(
                (
                    m
                    for m in members
                    if isinstance(m, dict) and str(m.get("local_id")) == lid
                ),
                None,
            )

        if resolved_role is not None:
            if member is None:
                lid = lid or f"invite-{token_hex(4)}"
                member = {
                    "local_id": lid,
                    "name": "",
                    "role": resolved_role,
                    "invite_status": "pending",
                    "invite_method": (channel or "LINK").upper(),
                }
                members.append(member)
            else:
                member["role"] = resolved_role
                lid = str(member.get("local_id") or lid)
            answers["members"] = members
            answers["member_drafts"] = members
            env["answers"] = answers
            draft_store.write_envelope(moment, env)
            await self._ensure_pending_business_member(
                moment_id=moment_id,
                user_id=user_id,
                local_id=lid,
                role_api=resolved_role,
                moment_type=moment.moment_type,
            )
        elif member is None:
            raise HTTPException(status_code=404, detail="Member draft not found")
        else:
            lid = str(member.get("local_id") or lid)
            raw_role = member.get("role")
            if raw_role:
                resolved_role = str(raw_role).strip().upper()

        assert lid is not None
        name = str(
            answers.get("team_name")
            or answers.get("moment_name")
            or moment.title
            or "Team"
        )
        ch = (channel or "EMAIL").upper()
        role_for_mint = resolved_role or str(member.get("role") or "MEMBER").upper()

        # Prefer opaque short URLs when enabled (parity with group switcher).
        if opaque_creates_enabled():
            minted = await PlatformInviteService(self.session).mint_opaque_moment_invite(
                user_id,
                moment,
                role_code=role_for_mint,
                max_uses=1,
                metadata={
                    "local_id": lid,
                    "business_moment": True,
                    "channel": ch,
                },
            )
            link = minted.get("invite_url") or minted.get("invite_link") or ""
            subject = f"You're invited to join {name}"
            body = f"You're invited to join \"{name}\" on Momentra.\n\nOpen this link to accept:\n{link}\n"
            whatsapp = f"Join our shared experience on Momentra: {name}\n{link}"
            sms = f"Join our shared experience on Momentra: {name} {link}"
            return {
                "invite_id": minted.get("invite_id") or "",
                "local_id": lid,
                "channel": ch,
                "invite_link": link,
                "invite_code": minted.get("code") or minted.get("invite_code") or "",
                "qr_payload": minted.get("qr_payload") or link,
                "email_subject": subject,
                "email_body": body,
                "whatsapp_text": whatsapp,
                "sms_text": sms,
                "expires_at": minted.get("expires_at"),
                "role": role_for_mint,
            }

        # Prefer durable DB invite row when present (post-activate or prior commit).
        inv_result = await self.session.execute(
            select(BusinessMomentInvitations).where(
                BusinessMomentInvitations.moment_id == moment_id,
                BusinessMomentInvitations.local_id == lid,
            )
        )
        try:
            inv_rows = list(inv_result.scalars().all())
        except Exception:
            inv_rows = []
        inv = next(
            (
                r
                for r in inv_rows
                if str(r.channel or r.invite_method or "").upper() == ch
                and (r.invite_status or "").lower() not in {"cancelled", "expired"}
            ),
            None,
        )
        if inv is None and inv_rows:
            inv = next(
                (
                    r
                    for r in inv_rows
                    if (r.invite_status or "").lower() not in {"cancelled", "expired"}
                ),
                None,
            )
        if inv is not None:
            draft = await mint_and_bind_invitation(
                self.session,
                inv,
                moment_id=moment_id,
                experience_name=name,
                mark_sent=False,
            )
            draft.pop("invite_token", None)
            draft.pop("token_hash", None)
            draft["role"] = role_for_mint
            return draft

        draft = build_invite_draft_payload(
            moment_id=str(moment_id),
            local_id=lid,
            channel=ch,
            experience_name=name,
            email=member.get("email") if isinstance(member, dict) else None,
        )
        draft.pop("invite_token", None)
        draft.pop("token_hash", None)
        draft["role"] = role_for_mint
        return draft

    async def _require_can_invite_members(self, user_id: UUID, moment: MomentModel) -> None:
        from sqlalchemy import select

        from app.domains.business.models import BusinessMomentMembers
        from app.domains.business.setup.invite_roles import (
            inviter_api_role_allowed,
            inviter_db_role_allowed,
        )

        if moment.user_id == user_id:
            return

        env = draft_store.read_envelope(moment) or {}
        answers = env.get("answers") or {}
        for m in answers.get("members") or []:
            if not isinstance(m, dict):
                continue
            uid = str(m.get("user_id") or "")
            if uid and uid == str(user_id) and inviter_api_role_allowed(m.get("role")):
                return

        result = await self.session.execute(
            select(BusinessMomentMembers).where(
                BusinessMomentMembers.moment_id == moment.id,
                BusinessMomentMembers.user_id == user_id,
            )
        )
        try:
            rows = list(result.scalars().all())
        except Exception:
            rows = []
        for row in rows:
            status_val = str(row.member_status or "").lower()
            if status_val in {"removed"}:
                continue
            if inviter_db_role_allowed(row.role) or inviter_api_role_allowed(row.role):
                return

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners, admins, or team leads can invite teammates",
        )

    async def _ensure_pending_business_member(
        self,
        *,
        moment_id: UUID,
        user_id: UUID,
        local_id: str,
        role_api: str,
        moment_type: str | None,
    ) -> None:
        """Upsert a pending BusinessMomentMembers row so accept can bind role."""
        from datetime import datetime, timezone
        from uuid import uuid4

        from sqlalchemy import select

        from app.domains.business.models import BusinessMomentMembers, BusinessMoments
        from app.domains.business.setup.member_roles import to_db_member_role
        from app.domains.business.setup.team_ops_permissions import (
            default_profile_for_role,
            member_permission_flags,
        )

        # Only when business_moments row exists (activated / synced).
        bm = await self.session.execute(
            select(BusinessMoments).where(BusinessMoments.moment_id == moment_id)
        )
        if bm.scalar_one_or_none() is None:
            return

        result = await self.session.execute(
            select(BusinessMomentMembers).where(
                BusinessMomentMembers.moment_id == moment_id,
                BusinessMomentMembers.local_id == local_id,
            )
        )
        try:
            existing = list(result.scalars().all())
        except Exception:
            existing = []
        row = existing[0] if existing else None
        db_role = to_db_member_role(role_api, template_code=moment_type or "team_operations")
        flags = member_permission_flags(role_api)
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        if row is None:
            row = BusinessMomentMembers(
                member_id=uuid4(),
                moment_id=moment_id,
                name="Invited teammate",
                role=db_role,
                member_status="invited",
                added_by=user_id,
                local_id=local_id,
                permission_profile=default_profile_for_role(role_api),
                permission_version=1,
                created_at=now,
                updated_at=now,
                can_manage_operations_settings=False,
                **flags,
            )
            self.session.add(row)
        else:
            if str(row.member_status or "").lower() == "active" and row.user_id:
                # Don't overwrite an active member; leave as-is.
                return
            row.role = db_role
            row.member_status = "invited"
            row.permission_profile = default_profile_for_role(role_api)
            row.permission_version = 1
            row.updated_at = now
            for k, v in flags.items():
                setattr(row, k, v)
        await self.session.flush()
