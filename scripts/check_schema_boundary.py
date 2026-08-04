#!/usr/bin/env python3
"""CI boundary check: verify App and Engine Alembic migration chains
never reference each other's tables.

App-schema migrations (apps/api/migrations/) must only reference tables
in the 'app' schema. Engine-schema migrations (packages/engine/migrations/)
must only reference tables in the 'engine' schema.

This is the mechanical enforcement of Finding #1: the Engine owns its own
schema, the App owns its own schema, and neither reaches into the other.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Patterns that indicate cross-schema references
APP_FORBIDDEN_PATTERNS = [
    re.compile(r"""schema\s*=\s*["']engine["']""", re.IGNORECASE),
    re.compile(r"""engine\.\w+"""),  # e.g., engine.workflow_run
]

ENGINE_FORBIDDEN_PATTERNS = [
    re.compile(r"""schema\s*=\s*["']app["']""", re.IGNORECASE),
    re.compile(r"""app\.\w+"""),  # e.g., app.feature_flags
]


def check_migrations(
    migration_dir: Path,
    forbidden_patterns: list[re.Pattern],
    schema_label: str,
) -> list[str]:
    """Check migration files for forbidden cross-schema references.

    Returns a list of violation descriptions.
    """
    violations = []

    versions_dir = migration_dir / "versions"
    if not versions_dir.exists():
        return violations

    for migration_file in sorted(versions_dir.glob("*.py")):
        content = migration_file.read_text()

        for pattern in forbidden_patterns:
            matches = pattern.findall(content)
            if matches:
                for match in matches:
                    violations.append(
                        f"  {schema_label} migration {migration_file.name} "
                        f"references forbidden pattern: {match}"
                    )

    return violations


def main() -> int:
    """Run the schema boundary check."""
    project_root = Path(__file__).resolve().parent.parent

    app_migrations = project_root / "apps" / "api" / "migrations"
    engine_migrations = project_root / "packages" / "engine" / "migrations"

    violations = []

    # Check App migrations don't reference Engine schema
    violations.extend(check_migrations(app_migrations, APP_FORBIDDEN_PATTERNS, "App"))

    # Check Engine migrations don't reference App schema
    violations.extend(check_migrations(engine_migrations, ENGINE_FORBIDDEN_PATTERNS, "Engine"))

    if violations:
        print("❌ Schema boundary violations detected:")
        for v in violations:
            print(v)
        return 1

    print("✅ Schema boundary check passed — no cross-schema references found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
