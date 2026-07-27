"""Life Ops expense validator — JSON-safe canonical payloads."""
from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.domains.personal.life_operations.quick_add.validators.expense import (
    validate_expense_payload,
)


@pytest.mark.asyncio
async def test_validate_expense_payload_is_json_serializable():
    account_id = uuid4()
    user_id = uuid4()
    session = AsyncMock()
    account = MagicMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = account
    session.execute.return_value = result

    validated = await validate_expense_payload(
        {
            "expense": {
                "amount_minor": 450000,
                "currency_code": "INR",
                "category_code": "FOOD",
                "account_id": str(account_id),
                "transaction_type": "EXPENSE",
                "pressure_impact": "Essential",
            }
        },
        session=session,
        user_id=user_id,
    )

    assert validated["account_id"] == str(account_id)
    assert isinstance(validated["account_id"], str)
    json.dumps({"expense": validated})
