import importlib.util
import sqlite3
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "migrate_dsos_identity_copy.py"
SPEC = importlib.util.spec_from_file_location("migrate_dsos_identity_copy", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class DsosIdentityMigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.source = self.root / "source.sqlite"
        self.destination = self.root / "migrated.sqlite"
        db = sqlite3.connect(self.source)
        db.executescript("""
            PRAGMA foreign_keys=ON;
            CREATE TABLE Players (
                PlayerId INTEGER PRIMARY KEY AUTOINCREMENT,
                PlayerSteamId CHAR(50)
            );
            CREATE TABLE Characters (
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                PlayerId INTEGER,
                CharacterId INTEGER,
                Data BLOB,
                FOREIGN KEY(PlayerId) REFERENCES Players(PlayerId)
            );
            CREATE TABLE BloodMessages (
                MessageId INTEGER PRIMARY KEY AUTOINCREMENT,
                PlayerId INTEGER,
                PlayerSteamId CHAR(50),
                Data BLOB
            );
            CREATE TABLE Bans (
                BanId INTEGER PRIMARY KEY AUTOINCREMENT,
                PlayerSteamId CHAR(50)
            );
            INSERT INTO Players(PlayerId, PlayerSteamId) VALUES(17, 'steam-legacy-17');
            INSERT INTO Players(PlayerId, PlayerSteamId) VALUES(29, 'steam-legacy-29');
            INSERT INTO Characters(Id, PlayerId, CharacterId, Data)
                VALUES(101, 17, 3, X'001122');
            INSERT INTO BloodMessages(MessageId, PlayerId, PlayerSteamId, Data)
                VALUES(201, 17, 'steam-legacy-17', X'AABB');
            INSERT INTO Bans(BanId, PlayerSteamId) VALUES(301, 'banned-not-player');
        """)
        db.commit()
        db.close()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_copy_migration_preserves_ids_and_related_rows(self):
        original_bytes = self.source.read_bytes()
        report = MODULE.migrate_copy(str(self.source), str(self.destination))
        self.assertEqual(self.source.read_bytes(), original_bytes)
        self.assertEqual(report["players_preserved"], 2)
        self.assertEqual(report["identity_rows_added"], 2)
        self.assertTrue(report["player_ids_preserved"])
        self.assertTrue(report["legacy_schema_verified_before_extension"])
        self.assertEqual(report["legacy_table_row_counts"]["Players"], 2)
        self.assertEqual(report["legacy_table_row_counts"]["Characters"], 1)
        self.assertEqual(report["legacy_table_row_counts"]["BloodMessages"], 1)
        self.assertEqual(report["legacy_table_row_counts"]["Bans"], 1)
        db = sqlite3.connect(self.destination)
        self.assertEqual(db.execute("SELECT PlayerId FROM Players ORDER BY PlayerId").fetchall(), [(17,), (29,)])
        self.assertEqual(
            db.execute("SELECT player_id, provider, identity_value FROM external_identities ORDER BY player_id").fetchall(),
            [(17, "steam", b"steam-legacy-17"), (29, "steam", b"steam-legacy-29")],
        )
        self.assertEqual(db.execute("SELECT Id, PlayerId, Data FROM Characters").fetchall(), [(101, 17, bytes.fromhex("001122"))])
        self.assertEqual(db.execute("SELECT MessageId, PlayerId FROM BloodMessages").fetchall(), [(201, 17)])
        self.assertEqual(db.execute("SELECT PlayerSteamId FROM Bans").fetchall(), [("banned-not-player",)])
        self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(), [])
        db.close()

    def test_duplicate_legacy_identity_aborts_without_destination(self):
        db = sqlite3.connect(self.source)
        db.execute("INSERT INTO Players(PlayerId, PlayerSteamId) VALUES(30, 'steam-legacy-17')")
        db.commit()
        db.close()
        with self.assertRaisesRegex(ValueError, "duplicate"):
            MODULE.migrate_copy(str(self.source), str(self.destination))
        self.assertFalse(self.destination.exists())

    def test_empty_identity_aborts_without_destination(self):
        db = sqlite3.connect(self.source)
        db.execute("INSERT INTO Players(PlayerId, PlayerSteamId) VALUES(31, NULL)")
        db.commit()
        db.close()
        with self.assertRaisesRegex(ValueError, "empty"):
            MODULE.migrate_copy(str(self.source), str(self.destination))
        self.assertFalse(self.destination.exists())

    def test_existing_destination_is_never_overwritten(self):
        self.destination.write_bytes(b"keep")
        with self.assertRaises(FileExistsError):
            MODULE.migrate_copy(str(self.source), str(self.destination))
        self.assertEqual(self.destination.read_bytes(), b"keep")


if __name__ == "__main__":
    unittest.main()
