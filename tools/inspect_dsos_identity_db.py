#!/usr/bin/env python3
"""Read-only inspection of a DSOS SQLite database before identity migration.

This tool never writes to the input database. It reports the legacy player
identity column, dependent columns with the same name, foreign keys, duplicate
identities, and row counts so a later importer can be based on observed schema.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any


def inspect_database(path: str) -> dict[str, Any]:
    db_path = Path(path)
    if not db_path.is_file():
        raise FileNotFoundError(path)
    uri = db_path.resolve().as_uri() + "?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    connection.row_factory = sqlite3.Row
    try:
        tables = [
            row["name"] for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            )
        ]
        table_reports = []
        identity_columns = []
        for table in tables:
            quoted = '"' + table.replace('"', '""') + '"'
            columns = [dict(row) for row in connection.execute(f"PRAGMA table_info({quoted})")]
            foreign_keys = [dict(row) for row in connection.execute(f"PRAGMA foreign_key_list({quoted})")]
            count = connection.execute(f"SELECT COUNT(*) FROM {quoted}").fetchone()[0]
            for column in columns:
                if column["name"].lower() in {"playersteamid", "steam_id", "player_steam_id"}:
                    identity_columns.append({
                        "table": table,
                        "column": column["name"],
                        "notnull": bool(column["notnull"]),
                        "primary_key": bool(column["pk"]),
                    })
            table_reports.append({
                "table": table,
                "row_count": count,
                "columns": columns,
                "foreign_keys": foreign_keys,
            })

        players = next((t for t in tables if t.lower() == "players"), None)
        legacy_identity = None
        if players:
            player_columns = {
                row["name"].lower(): row["name"]
                for row in connection.execute(
                    f'PRAGMA table_info("{players.replace(chr(34), chr(34)*2)}")'
                )
            }
            id_col = player_columns.get("playersteamid")
            player_id_col = player_columns.get("playerid")
            if id_col and player_id_col:
                q_players = '"' + players.replace('"', '""') + '"'
                q_identity = '"' + id_col.replace('"', '""') + '"'
                legacy_identity = {
                    "table": players,
                    "identity_column": id_col,
                    "player_id_column": player_id_col,
                    "null_or_empty_count": connection.execute(
                        f"SELECT COUNT(*) FROM {q_players} WHERE {q_identity} IS NULL OR TRIM({q_identity}) = ''"
                    ).fetchone()[0],
                    "duplicate_identity_groups": [
                        dict(row) for row in connection.execute(
                            f"SELECT {q_identity} AS identity_value, COUNT(*) AS occurrences "
                            f"FROM {q_players} WHERE {q_identity} IS NOT NULL "
                            f"GROUP BY {q_identity} HAVING COUNT(*) > 1 ORDER BY occurrences DESC"
                        )
                    ],
                }

        return {
            "database": db_path.name,
            "read_only": True,
            "tables": table_reports,
            "identity_columns": identity_columns,
            "legacy_players_identity": legacy_identity,
            "migration_ready": bool(
                legacy_identity
                and legacy_identity["null_or_empty_count"] == 0
                and not legacy_identity["duplicate_identity_groups"]
            ),
            "limitations": [
                "Schema inspection only; no migration is performed.",
                "Column-name matches are candidates, not proof of semantic identity.",
                "A clean report does not establish Xbox identity or Xbox protocol compatibility.",
            ],
        }
    finally:
        connection.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database", help="Path to a copied DSOS SQLite database")
    args = parser.parse_args()
    print(json.dumps(inspect_database(args.database), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
