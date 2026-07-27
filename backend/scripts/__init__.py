"""Operational / maintenance scripts (NOT application code).

Standalone entrypoints run out-of-band from the FastAPI app: data backfills,
one-off maintenance, snapshot rebuilds, admin bootstrap, etc. They may import
``app.*`` but nothing in ``app`` imports them. Invoke from the ``backend/``
directory, e.g. ``python -m scripts.rebuild_snapshots``.
"""
