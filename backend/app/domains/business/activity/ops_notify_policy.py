"""Backward-compatible re-export — prefer business_notify_policy."""
from app.domains.business.activity.business_notify_policy import (  # noqa: F401
    apply_business_notify_policy,
    apply_ops_notify_policy,
)
