"""Decimal ledger helpers and Goa Trip expected balances.

Sign convention:
  member_net = amount_paid - allocated_share
  Positive = should receive (creditor)
  Negative = owes (debtor)

Never use obsolete incorrect finals: +4050 / +3350 / -3450 / -3950.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from typing import Mapping

ZERO = Decimal("0.00")
Q2 = Decimal("0.01")

MEMBERS = ("santosh", "rahul", "priya", "kiran")


def D(value: str | int | Decimal) -> Decimal:
    return Decimal(str(value)).quantize(Q2, rounding=ROUND_HALF_UP)


def money_minor(amount: Decimal, *, minor_unit: int = 2) -> int:
    scale = Decimal(10) ** minor_unit
    return int((amount * scale).to_integral_value(rounding=ROUND_HALF_UP))


def money_major(minor: int, *, minor_unit: int = 2) -> Decimal:
    scale = Decimal(10) ** minor_unit
    return (Decimal(minor) / scale).quantize(Q2, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class ExpenseLine:
    key: str
    title: str
    total: Decimal
    payer: str
    shares: Mapping[str, Decimal]

    def validate_shares(self) -> None:
        share_sum = sum((D(v) for v in self.shares.values()), ZERO)
        if share_sum != D(self.total):
            raise AssertionError(
                f"{self.key}: share sum {share_sum} != expense total {self.total}"
            )

    def nets(self) -> dict[str, Decimal]:
        self.validate_shares()
        out: dict[str, Decimal] = {m: ZERO for m in MEMBERS}
        for m in MEMBERS:
            paid = D(self.total) if m == self.payer else ZERO
            share = D(self.shares.get(m, ZERO))
            out[m] = (paid - share).quantize(Q2)
        return out


@dataclass
class Ledger:
    balances: dict[str, Decimal] = field(
        default_factory=lambda: {m: ZERO for m in MEMBERS}
    )

    def apply(self, expense: ExpenseLine) -> dict[str, Decimal]:
        for m, net in expense.nets().items():
            self.balances[m] = (self.balances[m] + net).quantize(Q2)
        self.assert_balanced()
        return dict(self.balances)

    def apply_settlement(self, *, debtor: str, creditor: str, amount: Decimal) -> None:
        """Debtor pays creditor: debtor net increases (less debt), creditor net decreases."""
        amt = D(amount)
        self.balances[debtor] = (self.balances[debtor] + amt).quantize(Q2)
        self.balances[creditor] = (self.balances[creditor] - amt).quantize(Q2)
        self.assert_balanced()

    def assert_balanced(self) -> None:
        total = sum(self.balances.values(), ZERO).quantize(Q2)
        if total != ZERO:
            raise AssertionError(
                f"Group nets must sum to 0.00, got {total}: {self.balances}"
            )

    def assert_equals(self, expected: Mapping[str, Decimal], *, label: str) -> None:
        self.assert_balanced()
        for m in MEMBERS:
            exp = D(expected[m])
            act = self.balances[m]
            if act != exp:
                raise AssertionError(
                    f"{label}: {m} expected {exp}, actual {act} "
                    f"(diff {act - exp}); full={self.balances}"
                )


# --- Canonical Goa expenses (major INR) ---

GOA_EXPENSES: list[ExpenseLine] = [
    ExpenseLine(
        key="goa-fuel-001",
        title="Fuel",
        total=D("3200.00"),
        payer="santosh",
        shares={m: D("800.00") for m in MEMBERS},
    ),
    ExpenseLine(
        key="goa-lunch-001",
        title="Lunch",
        total=D("2400.00"),
        payer="rahul",
        shares={m: D("600.00") for m in MEMBERS},
    ),
    ExpenseLine(
        key="goa-hotel-001",
        title="Hotel",
        total=D("8000.00"),
        payer="santosh",
        shares={
            "santosh": D("3200.00"),
            "rahul": D("1600.00"),
            "priya": D("1600.00"),
            "kiran": D("1600.00"),
        },
    ),
    ExpenseLine(
        key="goa-scooter-001",
        title="Scooter Rental",
        total=D("1800.00"),
        payer="santosh",
        shares={"santosh": D("900.00"), "rahul": D("900.00")},
    ),
    ExpenseLine(
        key="goa-tickets-001",
        title="Beach Tickets",
        total=D("600.00"),
        payer="priya",
        shares={"priya": D("300.00"), "kiran": D("300.00")},
    ),
    ExpenseLine(
        key="goa-dinner-001",
        title="Dinner",
        total=D("5000.00"),
        payer="rahul",
        shares={m: D("1250.00") for m in MEMBERS},
    ),
]

PRE_SETTLEMENT = {
    "santosh": D("6250.00"),
    "rahul": D("2250.00"),
    "priya": D("-3950.00"),
    "kiran": D("-4550.00"),
}

POST_SETTLEMENT_KIRAN_TO_SANTOSH_2500 = {
    "santosh": D("3750.00"),
    "rahul": D("2250.00"),
    "priya": D("-3950.00"),
    "kiran": D("-2050.00"),
}

HOTEL_EDITED = ExpenseLine(
    key="goa-hotel-001",
    title="Hotel",
    total=D("9000.00"),
    payer="santosh",
    shares={
        "santosh": D("3600.00"),
        "rahul": D("1800.00"),
        "priya": D("1800.00"),
        "kiran": D("1800.00"),
    },
)

# After settlement then hotel edit (replacing original hotel nets)
POST_HOTEL_EDIT_AFTER_SETTLEMENT = {
    "santosh": D("4350.00"),
    "rahul": D("2050.00"),
    "priya": D("-4150.00"),
    "kiran": D("-2250.00"),
}

POST_SCOOTER_DELETE_AFTER_EDIT = {
    "santosh": D("3450.00"),
    "rahul": D("2950.00"),
    "priya": D("-4150.00"),
    "kiran": D("-2250.00"),
}


def build_pre_settlement_ledger() -> Ledger:
    ledger = Ledger()
    for expense in GOA_EXPENSES:
        ledger.apply(expense)
    ledger.assert_equals(PRE_SETTLEMENT, label="pre-settlement")
    return ledger


def apply_hotel_edit_in_place(ledger: Ledger) -> None:
    """Replace original hotel nets with edited hotel nets on an existing ledger."""
    original = next(e for e in GOA_EXPENSES if e.key == "goa-hotel-001")
    for m, net in original.nets().items():
        ledger.balances[m] = (ledger.balances[m] - net).quantize(Q2)
    for m, net in HOTEL_EDITED.nets().items():
        ledger.balances[m] = (ledger.balances[m] + net).quantize(Q2)
    ledger.assert_balanced()


def reverse_scooter(ledger: Ledger) -> None:
    scooter = next(e for e in GOA_EXPENSES if e.key == "goa-scooter-001")
    for m, net in scooter.nets().items():
        ledger.balances[m] = (ledger.balances[m] - net).quantize(Q2)
    ledger.assert_balanced()
