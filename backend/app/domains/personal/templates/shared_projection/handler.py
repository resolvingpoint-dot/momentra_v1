"""Shared template handler for My Money types without specialized moments projection."""
from __future__ import annotations

from app.domains.personal.templates.shared_projection.base_handler import BaseTemplateHandler


class SharedTemplateHandler(BaseTemplateHandler):
  """Life + memory projections for templates that have not specialized moments yet."""

  def __init__(self, moment_type_code: str) -> None:
      self.moment_type_code = moment_type_code.upper().replace("-", "_")
