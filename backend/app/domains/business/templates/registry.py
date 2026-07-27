"""Business template registry — maps moment_type to builder + mappers."""
from __future__ import annotations


def builders_for(moment_type: str, session):
    """Return {build, mappers} dict for the given moment type, or None."""
    mt = (moment_type or "").upper()
    if mt == "TEAM_OPERATIONS":
        from app.domains.business.templates.team_operations.handler import TeamOpsTemplateBuilder
        builder = TeamOpsTemplateBuilder(session)
        return {
            "build": builder.build,
            "mappers": _team_ops_mappers(),
        }
    if mt == "BUSINESS_RUNWAY":
        from app.domains.business.templates.business_runway.handler import RunwayTemplateBuilder
        builder = RunwayTemplateBuilder(session)
        return {
            "build": builder.build,
            "mappers": _runway_mappers(),
        }
    if mt == "BUSINESS_OPERATIONS":
        from app.domains.business.templates.business_operations.handler import OpsTemplateBuilder
        builder = OpsTemplateBuilder(session)
        return {
            "build": builder.build,
            "mappers": _ops_mappers(),
        }
    return None


def _team_ops_mappers():
    from app.domains.business.templates.team_operations.moments_mapper import build_moments
    from app.domains.business.templates.team_operations.pulse_mapper import build_pulse
    from app.domains.business.templates.team_operations.quick_add import build_quick_add
    return {
        "pulse": build_pulse,
        "moments": build_moments,
        "quick_add": build_quick_add,
    }


def _runway_mappers():
    from app.domains.business.templates.business_runway.moments_mapper import build_moments
    from app.domains.business.templates.business_runway.pulse_mapper import build_pulse
    from app.domains.business.templates.business_runway.quick_add import build_quick_add
    return {
        "pulse": build_pulse,
        "moments": build_moments,
        "quick_add": build_quick_add,
    }


def _ops_mappers():
    from app.domains.business.templates.business_operations.moments_mapper import build_moments
    from app.domains.business.templates.business_operations.pulse_mapper import build_pulse
    from app.domains.business.templates.business_operations.quick_add import build_quick_add
    return {
        "pulse": build_pulse,
        "moments": build_moments,
        "quick_add": build_quick_add,
    }
