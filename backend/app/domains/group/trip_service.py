"""Compatibility shim — TripService delegates to SharedExperienceService."""
from app.domains.group.shared_experience_service import SharedExperienceService as TripService

__all__ = ["TripService"]
