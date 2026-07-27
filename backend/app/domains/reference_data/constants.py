"""Seed reference data collections. Bump REFERENCE_DATA_VERSION when any collection changes."""
from __future__ import annotations

from typing import Any

REFERENCE_DATA_VERSION = 20

# All supported collection keys (including future stubs).
COLLECTION_KEYS = frozenset(
    {
        "currencies",
        "countries",
        "locales",
        "timezones",
        "languages",
        "expense_categories",
        "income_categories",
        "account_types",
        "recovery_activities",
        "mood_tags",
        "reflection_prompts",
        "commitment_types",
        "business_departments",
        "group_roles",
        "goal_types",
        "habit_types",
        "relationship_tags",
        "investment_types",
        "transport_modes",
        "meal_types",
        "emotion_tags",
        "weather",
        "group_split_styles",
        "group_participation_roles",
        "group_invitation_methods",
        "group_contribution_types",
        "group_vendor_categories",
        "group_planning_item_types",
        "group_activity_types",
        "group_booking_types",
        "group_accommodation_types",
    }
)


def _item(
    code: str,
    label: str,
    *,
    icon: str = "",
    color: str = "",
    sort_order: int = 0,
    is_active: bool = True,
    **extra: Any,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "code": code,
        "label": label,
        "icon": icon,
        "color": color,
        "sort_order": sort_order,
        "is_active": is_active,
    }
    row.update(extra)
    return row


CURRENCIES: list[dict[str, Any]] = [
    _item(
        "INR",
        "Indian Rupee",
        symbol="₹",
        minor_unit=2,
        locale_hint="en-IN",
        icon="currency_rupee",
        sort_order=10,
    ),
    _item(
        "USD",
        "US Dollar",
        symbol="$",
        minor_unit=2,
        locale_hint="en-US",
        icon="attach_money",
        sort_order=20,
    ),
    _item(
        "EUR",
        "Euro",
        symbol="€",
        minor_unit=2,
        locale_hint="en-EU",
        icon="euro",
        sort_order=30,
    ),
    _item(
        "GBP",
        "British Pound",
        symbol="£",
        minor_unit=2,
        locale_hint="en-GB",
        icon="currency_pound",
        sort_order=40,
    ),
    _item(
        "AED",
        "UAE Dirham",
        symbol="د.إ",
        minor_unit=2,
        locale_hint="ar-AE",
        icon="currency_exchange",
        sort_order=50,
    ),
    _item(
        "SGD",
        "Singapore Dollar",
        symbol="S$",
        minor_unit=2,
        locale_hint="en-SG",
        icon="currency_exchange",
        sort_order=60,
    ),
    _item(
        "JPY",
        "Japanese Yen",
        symbol="¥",
        minor_unit=0,
        locale_hint="ja-JP",
        icon="currency_yen",
        sort_order=70,
    ),
    _item(
        "KWD",
        "Kuwaiti Dinar",
        symbol="د.ك",
        minor_unit=3,
        locale_hint="ar-KW",
        icon="currency_exchange",
        sort_order=80,
    ),
]

COUNTRIES: list[dict[str, Any]] = [
    _item("IN", "India", icon="flag", sort_order=10),
    _item("US", "United States", icon="flag", sort_order=20),
    _item("GB", "United Kingdom", icon="flag", sort_order=30),
    _item("AE", "United Arab Emirates", icon="flag", sort_order=40),
    _item("SG", "Singapore", icon="flag", sort_order=50),
    _item("JP", "Japan", icon="flag", sort_order=60),
    _item("DE", "Germany", icon="flag", sort_order=70),
    _item("FR", "France", icon="flag", sort_order=80),
]

LOCALES: list[dict[str, Any]] = [
    _item("en-IN", "English (India)", sort_order=10),
    _item("en-US", "English (United States)", sort_order=20),
    _item("en-GB", "English (United Kingdom)", sort_order=30),
    _item("en-SG", "English (Singapore)", sort_order=40),
    _item("ar-AE", "Arabic (UAE)", sort_order=50),
    _item("ja-JP", "Japanese (Japan)", sort_order=60),
    _item("de-DE", "German (Germany)", sort_order=70),
    _item("fr-FR", "French (France)", sort_order=80),
]

TIMEZONES: list[dict[str, Any]] = [
    _item("Asia/Kolkata", "Asia/Kolkata (IST)", sort_order=10),
    _item("America/New_York", "America/New_York (ET)", sort_order=20),
    _item("America/Los_Angeles", "America/Los_Angeles (PT)", sort_order=30),
    _item("Europe/London", "Europe/London (GMT/BST)", sort_order=40),
    _item("Asia/Dubai", "Asia/Dubai (GST)", sort_order=50),
    _item("Asia/Singapore", "Asia/Singapore (SGT)", sort_order=60),
    _item("Asia/Tokyo", "Asia/Tokyo (JST)", sort_order=70),
    _item("Europe/Berlin", "Europe/Berlin (CET)", sort_order=80),
]

LANGUAGES: list[dict[str, Any]] = [
    _item("en", "English", sort_order=10),
    _item("hi", "Hindi", sort_order=20),
    _item("ar", "Arabic", sort_order=30),
    _item("ja", "Japanese", sort_order=40),
    _item("de", "German", sort_order=50),
    _item("fr", "French", sort_order=60),
]

EXPENSE_CATEGORIES: list[dict[str, Any]] = [
    # Parents (taxonomy EXPENSE)
    _item("FOOD", "Food", icon="restaurant", color="#F5C542", sort_order=10, taxonomy="EXPENSE"),
    _item(
        "TRANSPORT",
        "Transport",
        icon="directions_car",
        color="#5B8DEF",
        sort_order=20,
        taxonomy="EXPENSE",
    ),
    _item("HOUSING", "Housing", icon="home", color="#9B7EDE", sort_order=30, taxonomy="EXPENSE"),
    _item("HEALTH", "Health", icon="favorite", color="#E85D75", sort_order=40, taxonomy="EXPENSE"),
    _item(
        "ENTERTAINMENT",
        "Entertainment",
        icon="movie",
        color="#FF8C42",
        sort_order=50,
        taxonomy="EXPENSE",
    ),
    _item("OTHER", "Other", icon="more_horiz", color="#8E8E93", sort_order=100, taxonomy="EXPENSE"),
    # Children
    _item(
        "GROCERIES",
        "Groceries",
        icon="local_grocery_store",
        sort_order=11,
        taxonomy="EXPENSE",
        parent_code="FOOD",
    ),
    _item(
        "DINING_OUT",
        "Dining out",
        icon="restaurant_menu",
        sort_order=12,
        taxonomy="EXPENSE",
        parent_code="FOOD",
    ),
    _item("COFFEE", "Coffee", icon="local_cafe", sort_order=13, taxonomy="EXPENSE", parent_code="FOOD"),
    _item(
        "FUEL",
        "Fuel",
        icon="local_gas_station",
        sort_order=21,
        taxonomy="EXPENSE",
        parent_code="TRANSPORT",
    ),
    _item(
        "RIDESHARE",
        "Rideshare",
        icon="local_taxi",
        sort_order=22,
        taxonomy="EXPENSE",
        parent_code="TRANSPORT",
    ),
    _item(
        "TRANSIT",
        "Transit",
        icon="directions_bus",
        sort_order=23,
        taxonomy="EXPENSE",
        parent_code="TRANSPORT",
    ),
    _item(
        "RESIDENTIAL_RENT",
        "Residential rent",
        icon="apartment",
        sort_order=31,
        taxonomy="EXPENSE",
        parent_code="HOUSING",
    ),
    _item(
        "UTILITIES",
        "Utilities",
        icon="bolt",
        sort_order=32,
        taxonomy="EXPENSE",
        parent_code="HOUSING",
    ),
    _item(
        "MAINTENANCE",
        "Maintenance",
        icon="handyman",
        sort_order=33,
        taxonomy="EXPENSE",
        parent_code="HOUSING",
    ),
    _item(
        "PHARMACY",
        "Pharmacy",
        icon="local_pharmacy",
        sort_order=41,
        taxonomy="EXPENSE",
        parent_code="HEALTH",
    ),
    _item("CLINIC", "Clinic", icon="medical_services", sort_order=42, taxonomy="EXPENSE", parent_code="HEALTH"),
    _item("MOVIES", "Movies", icon="theaters", sort_order=51, taxonomy="EXPENSE", parent_code="ENTERTAINMENT"),
    _item(
        "SUBSCRIPTIONS",
        "Subscriptions",
        icon="subscriptions",
        sort_order=52,
        taxonomy="EXPENSE",
        parent_code="ENTERTAINMENT",
    ),
]

INCOME_CATEGORIES: list[dict[str, Any]] = [
    _item("SALARY", "Salary", icon="payments", color="#34C759", sort_order=10),
    _item("FREELANCE", "Freelance", icon="work", color="#5AC8FA", sort_order=20),
    _item("INVESTMENT", "Investment", icon="trending_up", color="#AF52DE", sort_order=30),
    _item("GIFT", "Gift", icon="card_giftcard", color="#FF9500", sort_order=40),
    _item("OTHER", "Other", icon="more_horiz", color="#8E8E93", sort_order=100),
]

ACCOUNT_TYPES: list[dict[str, Any]] = [
    _item("SAVINGS", "Savings", icon="savings", sort_order=10),
    _item("CURRENT", "Current", icon="account_balance", sort_order=20),
    _item("CREDIT_CARD", "Credit Card", icon="credit_card", sort_order=30),
    _item("INVESTMENT", "Investment", icon="trending_up", sort_order=40),
    _item("WALLET", "Wallet", icon="account_balance_wallet", sort_order=50),
    _item("CASH", "Cash", icon="payments", sort_order=60),
    _item("CUSTOM", "Custom", icon="edit", sort_order=70),
]

RECOVERY_ACTIVITIES: list[dict[str, Any]] = [
    _item("SLEEP", "Sleep", icon="bedtime", sort_order=10),
    _item("WALK", "Walk", icon="directions_walk", sort_order=20),
    _item("MEDITATION", "Meditation", icon="self_improvement", sort_order=30),
    _item("EXERCISE", "Exercise", icon="fitness_center", sort_order=40),
    _item("REST", "Rest", icon="weekend", sort_order=50),
]

MOOD_TAGS: list[dict[str, Any]] = [
    _item("CALM", "Calm", color="#5AC8FA", sort_order=10),
    _item("OKAY", "Okay", color="#8E8E93", sort_order=20),
    _item("STRESSED", "Stressed", color="#FF9500", sort_order=30),
    _item("ENERGIZED", "Energized", color="#34C759", sort_order=40),
    _item("LOW", "Low", color="#5856D6", sort_order=50),
]

REFLECTION_PROMPTS: list[dict[str, Any]] = [
    _item("GRATITUDE", "What are you grateful for?", sort_order=10),
    _item("WIN", "What went well today?", sort_order=20),
    _item("CHALLENGE", "What challenged you?", sort_order=30),
    _item("LEARN", "What did you learn?", sort_order=40),
]

COMMITMENT_TYPES: list[dict[str, Any]] = [
    _item("TASK", "Task", icon="task_alt", sort_order=10),
    _item("MEETING", "Meeting", icon="groups", sort_order=20),
    _item("DEEP_WORK", "Deep Work", icon="psychology", sort_order=30),
    _item("ADMIN", "Admin", icon="description", sort_order=40),
]

# Future stubs — empty but registered in the engine.
BUSINESS_DEPARTMENTS: list[dict[str, Any]] = []
GROUP_ROLES: list[dict[str, Any]] = [
    _item("ORGANIZER", "Organizer", icon="star", sort_order=10),
    _item("CO_ORGANIZER", "Co-organizer", icon="group", sort_order=20),
    _item("PARTICIPANT", "Participant", icon="person", sort_order=30),
    _item("GUEST", "Guest", icon="person_outline", sort_order=40),
]
GOAL_TYPES: list[dict[str, Any]] = []
HABIT_TYPES: list[dict[str, Any]] = []
RELATIONSHIP_TAGS: list[dict[str, Any]] = []
INVESTMENT_TYPES: list[dict[str, Any]] = []
TRANSPORT_MODES: list[dict[str, Any]] = [
    _item("FLIGHT", "Flight", icon="flight", sort_order=10),
    _item("TRAIN", "Train", icon="train", sort_order=20),
    _item("BUS", "Bus", icon="directions_bus", sort_order=30),
    _item("CAR", "Car", icon="directions_car", sort_order=40),
    _item("FERRY", "Ferry", icon="directions_boat", sort_order=50),
]
MEAL_TYPES: list[dict[str, Any]] = []
EMOTION_TAGS: list[dict[str, Any]] = []
WEATHER: list[dict[str, Any]] = []

GROUP_SPLIT_STYLES: list[dict[str, Any]] = [
    _item("EQUAL", "Split equally", icon="balance", sort_order=10),
    _item("CUSTOM", "Custom split", icon="tune", sort_order=20),
    _item("PERCENT", "By percentage", icon="percent", sort_order=30),
    _item("SHARES", "By shares", icon="pie_chart", sort_order=40),
]
GROUP_PARTICIPATION_ROLES: list[dict[str, Any]] = GROUP_ROLES
GROUP_INVITATION_METHODS: list[dict[str, Any]] = [
    _item("WHATSAPP", "WhatsApp", icon="chat", sort_order=10),
    _item("QR", "QR code", icon="qr_code", sort_order=20),
    _item("EMAIL", "Email", icon="email", sort_order=30),
    _item("COPY_LINK", "Copy link", icon="link", sort_order=40),
]
GROUP_CONTRIBUTION_TYPES: list[dict[str, Any]] = [
    _item("POOL", "Shared pool", icon="account_balance_wallet", sort_order=10),
    _item("GIFT", "Gift contribution", icon="card_giftcard", sort_order=20),
    _item("SPONSOR", "Sponsor", icon="volunteer_activism", sort_order=30),
]
GROUP_VENDOR_CATEGORIES: list[dict[str, Any]] = [
    _item("VENUE", "Venue", icon="location_city", sort_order=10),
    _item("CATERING", "Catering", icon="restaurant", sort_order=20),
    _item("PHOTO", "Photography", icon="photo_camera", sort_order=30),
    _item("TRANSPORT", "Transport", icon="directions_car", sort_order=40),
]
GROUP_PLANNING_ITEM_TYPES: list[dict[str, Any]] = [
    _item("STAY", "Stay", icon="hotel", sort_order=10),
    _item("TRAVEL", "Travel", icon="flight", sort_order=20),
    _item("ACTIVITY", "Activity", icon="hiking", sort_order=30),
    _item("MEAL", "Meal", icon="restaurant", sort_order=40),
]
GROUP_ACTIVITY_TYPES: list[dict[str, Any]] = [
    _item("EXPENSE", "Expense", icon="receipt", sort_order=10),
    _item("BOOKING", "Booking", icon="event", sort_order=20),
    _item("MEMORY", "Memory", icon="photo_camera", sort_order=30),
    _item("POLL", "Poll", icon="poll", sort_order=40),
    _item("UPDATE", "Update", icon="campaign", sort_order=50),
]
GROUP_BOOKING_TYPES: list[dict[str, Any]] = [
    _item("STAY", "Stay", icon="hotel", sort_order=10),
    _item("TRAVEL", "Travel", icon="flight", sort_order=20),
    _item("ACTIVITY", "Activity", icon="confirmation_number", sort_order=30),
]
GROUP_ACCOMMODATION_TYPES: list[dict[str, Any]] = [
    _item("HOTEL", "Hotel", icon="hotel", sort_order=10),
    _item("HOSTEL", "Hostel", icon="bed", sort_order=20),
    _item("RENTAL", "Rental", icon="home", sort_order=30),
    _item("HOMESTAY", "Homestay", icon="cottage", sort_order=40),
]

COLLECTIONS: dict[str, list[dict[str, Any]]] = {
    "currencies": CURRENCIES,
    "countries": COUNTRIES,
    "locales": LOCALES,
    "timezones": TIMEZONES,
    "languages": LANGUAGES,
    "expense_categories": EXPENSE_CATEGORIES,
    "income_categories": INCOME_CATEGORIES,
    "account_types": ACCOUNT_TYPES,
    "recovery_activities": RECOVERY_ACTIVITIES,
    "mood_tags": MOOD_TAGS,
    "reflection_prompts": REFLECTION_PROMPTS,
    "commitment_types": COMMITMENT_TYPES,
    "business_departments": BUSINESS_DEPARTMENTS,
    "group_roles": GROUP_ROLES,
    "goal_types": GOAL_TYPES,
    "habit_types": HABIT_TYPES,
    "relationship_tags": RELATIONSHIP_TAGS,
    "investment_types": INVESTMENT_TYPES,
    "transport_modes": TRANSPORT_MODES,
    "meal_types": MEAL_TYPES,
    "emotion_tags": EMOTION_TAGS,
    "weather": WEATHER,
    "group_split_styles": GROUP_SPLIT_STYLES,
    "group_participation_roles": GROUP_PARTICIPATION_ROLES,
    "group_invitation_methods": GROUP_INVITATION_METHODS,
    "group_contribution_types": GROUP_CONTRIBUTION_TYPES,
    "group_vendor_categories": GROUP_VENDOR_CATEGORIES,
    "group_planning_item_types": GROUP_PLANNING_ITEM_TYPES,
    "group_activity_types": GROUP_ACTIVITY_TYPES,
    "group_booking_types": GROUP_BOOKING_TYPES,
    "group_accommodation_types": GROUP_ACCOMMODATION_TYPES,
}

# Maps category group keys used in bootstrap response.
CATEGORY_GROUPS: dict[str, list[dict[str, Any]]] = {
    "expense": EXPENSE_CATEGORIES,
    "income": INCOME_CATEGORIES,
    "account_type": ACCOUNT_TYPES,
    "recovery_activity": RECOVERY_ACTIVITIES,
    "mood_tag": MOOD_TAGS,
    "reflection_prompt": REFLECTION_PROMPTS,
    "commitment_type": COMMITMENT_TYPES,
    "business_department": BUSINESS_DEPARTMENTS,
    "group_role": GROUP_ROLES,
    "group_split_style": GROUP_SPLIT_STYLES,
    "group_invitation_method": GROUP_INVITATION_METHODS,
    "group_contribution_type": GROUP_CONTRIBUTION_TYPES,
    "group_vendor_category": GROUP_VENDOR_CATEGORIES,
    "group_planning_item_type": GROUP_PLANNING_ITEM_TYPES,
    "group_activity_type": GROUP_ACTIVITY_TYPES,
    "group_booking_type": GROUP_BOOKING_TYPES,
    "group_accommodation_type": GROUP_ACCOMMODATION_TYPES,
    "transport_mode": TRANSPORT_MODES,
}
