"""Shared preview builder for Business setup (placeholder until Runs 3–5)."""
from __future__ import annotations

from typing import Any

from app.domains.business.catalog import business_type_name
from app.domains.business.setup.schemas import SetupPreviewResponse, SetupSummaryBlock


def build_placeholder_preview(
    *,
    moment_type_code: str,
    answers: dict[str, Any],
    template_id: str,
) -> SetupPreviewResponse:
    name = answers.get("moment_name") or answers.get("team_name") or business_type_name(moment_type_code)
    currency = answers.get("default_currency_code") or answers.get("operating_currency_code")
    blocks = [
        SetupSummaryBlock(
            block_id="identity",
            title="Identity",
            body=str(name),
            items=[
                {"label": "Template", "value": template_id},
                {"label": "Type", "value": moment_type_code},
            ],
        ),
        SetupSummaryBlock(
            block_id="international",
            title="International settings",
            body="Draft-capable settings (not fully validated in Run 2)",
            items=[
                {"label": "Country", "value": answers.get("country_code")},
                {"label": "Locale", "value": answers.get("locale")},
                {"label": "Timezone", "value": answers.get("timezone")},
                {"label": "Currency", "value": currency},
                {"label": "Multi-currency", "value": answers.get("allow_multi_currency")},
                {"label": "Financial year start", "value": answers.get("financial_year_start")},
            ],
        ),
    ]
    # Run 2: always allow activation for v1 creatable types (full validation in Runs 3–5).
    return SetupPreviewResponse(
        summary_blocks=blocks,
        warnings=[],
        blocking_errors=[],
        activation_ready=True,
    )
