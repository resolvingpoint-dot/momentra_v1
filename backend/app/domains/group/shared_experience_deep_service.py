"""Compatibility shim — TripDeepService remains canonical import path."""
from app.domains.group.trip_deep_service import TripDeepService as SharedExperienceDeepService

TripDeepService = SharedExperienceDeepService

__all__ = ["SharedExperienceDeepService", "TripDeepService"]
