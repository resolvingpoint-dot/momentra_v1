"""Notifications domain.

Home for cross-context notification logic (repository/service/schemas). Delivery
is performed asynchronously by ``app.workers.tasks.notifications``; per-context
notification rows currently live in their owning domains (e.g. business
notifications). This package is the intended location for a unified notification
service as that logic is consolidated.
"""
