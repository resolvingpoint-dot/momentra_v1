"""Migrate personal_accounts.account_type to reference catalog codes.

Revision ID: mom_13_account_type_codes
Revises: mom_12_money_minor
"""
from typing import Sequence, Union

from alembic import op


revision: str = "mom_13_account_type_codes"
down_revision: Union[str, Sequence[str], None] = "mom_12_money_minor"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_LEGACY_TO_CODE = {
    "Cash": "CASH",
    "Bank": "CURRENT",
    "Wallet": "WALLET",
    "Credit Card": "CREDIT_CARD",
    "Investment": "INVESTMENT",
    "Custom": "CUSTOM",
}


def upgrade() -> None:
    for legacy, code in _LEGACY_TO_CODE.items():
        op.execute(
            f"""
            UPDATE personal_accounts
            SET account_type = '{code}'
            WHERE account_type = '{legacy}'
            """
        )
    op.drop_constraint("chk_personal_account_type", "personal_accounts", type_="check")
    op.create_check_constraint(
        "chk_personal_account_type",
        "personal_accounts",
        "account_type::text = ANY (ARRAY['SAVINGS'::character varying, 'CURRENT'::character varying, "
        "'CREDIT_CARD'::character varying, 'INVESTMENT'::character varying, 'WALLET'::character varying, "
        "'CASH'::character varying, 'CUSTOM'::character varying]::text[])",
    )


def downgrade() -> None:
    op.drop_constraint("chk_personal_account_type", "personal_accounts", type_="check")
    op.create_check_constraint(
        "chk_personal_account_type",
        "personal_accounts",
        "account_type::text = ANY (ARRAY['Cash'::character varying, 'Bank'::character varying, "
        "'Wallet'::character varying, 'Credit Card'::character varying, 'Investment'::character varying, "
        "'Custom'::character varying]::text[])",
    )
    _CODE_TO_LEGACY = {v: k for k, v in _LEGACY_TO_CODE.items()}
    for code, legacy in _CODE_TO_LEGACY.items():
        op.execute(
            f"""
            UPDATE personal_accounts
            SET account_type = '{legacy}'
            WHERE account_type = '{code}'
            """
        )
