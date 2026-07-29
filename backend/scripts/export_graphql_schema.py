"""Export committed GraphQL SDL + checksum metadata."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
SCHEMA_PATH = ROOT / "app" / "api" / "graphql" / "schema.graphql"
META_PATH = ROOT / "app" / "api" / "graphql" / "schema.meta.json"
CHANGELOG_PATH = REPO / "docs" / "platform" / "graphql" / "SCHEMA_CHANGELOG.md"


def export(*, write_changelog: bool = True) -> dict:
    from app.api.graphql.schema import schema

    sdl = schema.as_str().strip() + "\n"
    digest = hashlib.sha256(sdl.encode("utf-8")).hexdigest()
    version = digest[:12]
    SCHEMA_PATH.parent.mkdir(parents=True, exist_ok=True)
    previous = None
    if META_PATH.exists():
        previous = json.loads(META_PATH.read_text(encoding="utf-8"))
    SCHEMA_PATH.write_text(sdl, encoding="utf-8")
    from app.core.config import settings

    meta = {
        "version": version,
        "checksum_sha256": digest,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "apq_schema_version": settings.graphql_apq_schema_version,
    }
    META_PATH.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    if write_changelog and (previous is None or previous.get("checksum_sha256") != digest):
        CHANGELOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        entry = (
            f"## {stamp} — `{version}`\n\n"
            f"- checksum: `{digest}`\n"
            f"- previous: `{previous.get('checksum_sha256') if previous else 'none'}`\n\n"
        )
        existing = CHANGELOG_PATH.read_text(encoding="utf-8") if CHANGELOG_PATH.exists() else "# GraphQL Schema Changelog\n\n"
        if f"`{version}`" not in existing:
            # Insert after title
            if existing.startswith("#"):
                parts = existing.split("\n", 2)
                head = parts[0] + "\n\n"
                rest = parts[2] if len(parts) > 2 else ""
                CHANGELOG_PATH.write_text(head + entry + rest, encoding="utf-8")
            else:
                CHANGELOG_PATH.write_text("# GraphQL Schema Changelog\n\n" + entry + existing, encoding="utf-8")
    return meta


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-changelog", action="store_true")
    args = parser.parse_args()
    meta = export(write_changelog=not args.no_changelog)
    print(f"Wrote {SCHEMA_PATH} version={meta['version']} checksum={meta['checksum_sha256']}")


if __name__ == "__main__":
    main()
