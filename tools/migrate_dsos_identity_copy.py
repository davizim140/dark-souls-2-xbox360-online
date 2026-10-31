#!/usr/bin/env python3
"""Create a separate DSOS database copy with a normalized legacy Steam identity map.

The source is opened read-only. The destination must not already exist. Existing
DSOS tables and PlayerId values are preserved; no Xbox identity is inferred.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path


def _database_fingerprint(connection: sqlite3.Connection) -> dict:
    tables = [row[0] for row in connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    )]
    schema = connection.execute(
        "SELECT type, name, tbl_name, sql FROM sqlite_master WHERE name NOT LIKE 'sqlite_%' ORDER BY type, name"
    ).fetchall()
    counts = {}
    for table in tables:
        quoted = '"' + table.replace('"', '""') + '"'
        counts[table] = connection.execute('SELECT COUNT(*) FROM ' + quoted).fetchone()[0]
    return {"table_rows": counts, "schema": [tuple(row) for row in schema]}


def migrate_copy(source_path: str, destination_path: str) -> dict:
    source = Path(source_path).resolve()
    destination = Path(destination_path).resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if source == destination:
        raise ValueError("source and destination must be different files")
    if destination.exists():
        raise FileExistsError(f"destination already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)

    source_uri = source.as_uri() + "?mode=ro"
    src = sqlite3.connect(source_uri, uri=True)
    dst = None
    try:
        src.execute("PRAGMA query_only=ON")
        players = src.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='Players'"
        ).fetchone()
        if not players:
            raise ValueError("source database has no Players table")
        cols = {row[1].lower(): row[1] for row in src.execute('PRAGMA table_info("Players")')}
        if "playerid" not in cols or "playersteamid" not in cols:
            raise ValueError("Players must contain PlayerId and PlayerSteamId")

        q_id = '"' + cols["playerid"].replace('"', '""') + '"'
        q_steam = '"' + cols["playersteamid"].replace('"', '""') + '"'
        rows = src.execute(
            f'SELECT {q_id}, {q_steam} FROM "Players" ORDER BY {q_id}'
        ).fetchall()
        source_fingerprint = _database_fingerprint(src)
        seen = set()
        normalized = []
        for player_id, steam_id in rows:
            if not isinstance(player_id, int) or player_id <= 0:
                raise ValueError(f"invalid PlayerId: {player_id!r}")
            if not isinstance(steam_id, str) or not steam_id.strip():
                raise ValueError(f"PlayerId {player_id} has an empty/non-text PlayerSteamId")
            identity = steam_id.encode("utf-8")
            if identity in seen:
                raise ValueError("duplicate PlayerSteamId values; migration stopped")
            seen.add(identity)
            normalized.append((player_id, identity))

        dst = sqlite3.connect(str(destination))
        src.backup(dst)
        copied_fingerprint = _database_fingerprint(dst)
        if copied_fingerprint != source_fingerprint:
            raise RuntimeError("SQLite backup differs from source schema or table row counts")
        dst.execute("PRAGMA foreign_keys=ON")
        dst.execute("BEGIN IMMEDIATE")
        dst.execute("""
            CREATE TABLE external_identities (
                player_id INTEGER NOT NULL UNIQUE,
                provider TEXT NOT NULL,
                identity_value BLOB NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY(provider, identity_value),
                FOREIGN KEY(player_id) REFERENCES Players(PlayerId)
            )
        """)
        dst.executemany(
            "INSERT INTO external_identities(player_id, provider, identity_value) VALUES(?, 'steam', ?)",
            normalized,
        )
        copied = dst.execute("SELECT COUNT(*) FROM external_identities").fetchone()[0]
        if copied != len(rows):
            raise RuntimeError(f"identity row count mismatch: expected {len(rows)}, got {copied}")
        mismatches = dst.execute("""
            SELECT COUNT(*) FROM Players p
            LEFT JOIN external_identities e
              ON e.player_id = p.PlayerId
             AND e.provider = 'steam'
             AND e.identity_value = CAST(p.PlayerSteamId AS BLOB)
            WHERE e.player_id IS NULL
        """).fetchone()[0]
        if mismatches:
            raise RuntimeError(f"{mismatches} Players rows were not mapped exactly")
        foreign_key_errors = dst.execute("PRAGMA foreign_key_check").fetchall()
        if foreign_key_errors:
            raise RuntimeError(f"foreign key check failed: {foreign_key_errors[:5]}")
        dst.commit()
        return {
            "source": source.name,
            "destination": destination.name,
            "source_unchanged": True,
            "players_preserved": len(rows),
            "identity_rows_added": copied,
            "provider": "steam",
            "player_ids_preserved": True,
            "foreign_key_check": "passed",
            "legacy_table_row_counts": source_fingerprint["table_rows"],
            "legacy_schema_verified_before_extension": True,
            "note": "This is a copy-only legacy Steam mapping, not Xbox authentication or protocol support.",
        }
    except Exception:
        if dst is not None:
            dst.rollback()
        if destination.exists():
            destination.unlink()
        raise
    finally:
        if dst is not None:
            dst.close()
        src.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="Path to an offline copy of the DSOS SQLite database")
    parser.add_argument("destination", help="New destination path; must not exist")
    args = parser.parse_args()
    print(json.dumps(migrate_copy(args.source, args.destination), indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"migration aborted: {exc}", file=sys.stderr)
        raise SystemExit(1)
