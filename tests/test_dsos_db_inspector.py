import importlib.util
import sqlite3
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "inspect_dsos_identity_db.py"
SPEC = importlib.util.spec_from_file_location("inspect_dsos_identity_db", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class DsosDatabaseInspectorTests(unittest.TestCase):
    def make_fixture(self, duplicate=False):
        temp = tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False)
        temp.close()
        connection = sqlite3.connect(temp.name)
        connection.executescript("""
            PRAGMA foreign_keys=ON;
            CREATE TABLE Players (
                PlayerId INTEGER PRIMARY KEY AUTOINCREMENT,
                PlayerSteamId CHAR(50) NOT NULL
            );
            CREATE TABLE Characters (
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                PlayerId INTEGER NOT NULL,
                CharacterId INTEGER NOT NULL,
                Data BLOB,
                FOREIGN KEY(PlayerId) REFERENCES Players(PlayerId)
            );
            CREATE TABLE BloodMessages (
                Id INTEGER PRIMARY KEY,
                PlayerSteamId CHAR(50) NOT NULL
            );
        """)
        connection.execute("INSERT INTO Players(PlayerId, PlayerSteamId) VALUES(7, 'steam-user-7')")
        connection.execute("INSERT INTO Characters(Id, PlayerId, CharacterId, Data) VALUES(11, 7, 2, X'0102')")
        connection.execute("INSERT INTO BloodMessages(Id, PlayerSteamId) VALUES(21, 'steam-user-7')")
        if duplicate:
            connection.execute("INSERT INTO Players(PlayerId, PlayerSteamId) VALUES(8, 'steam-user-7')")
        connection.commit()
        connection.close()
        return Path(temp.name)

    def test_reports_schema_and_is_read_only(self):
        path = self.make_fixture()
        try:
            before = path.read_bytes()
            report = MODULE.inspect_database(str(path))
            self.assertTrue(report["read_only"])
            self.assertTrue(report["migration_ready"])
            self.assertEqual(report["legacy_players_identity"]["null_or_empty_count"], 0)
            self.assertEqual(len(report["identity_columns"]), 2)
            self.assertEqual(path.read_bytes(), before)
            characters = next(t for t in report["tables"] if t["table"] == "Characters")
            self.assertEqual(characters["foreign_keys"][0]["table"], "Players")
        finally:
            path.unlink()

    def test_duplicate_legacy_identity_blocks_readiness(self):
        path = self.make_fixture(duplicate=True)
        try:
            report = MODULE.inspect_database(str(path))
            self.assertFalse(report["migration_ready"])
            self.assertEqual(len(report["legacy_players_identity"]["duplicate_identity_groups"]), 1)
        finally:
            path.unlink()


if __name__ == "__main__":
    unittest.main()
