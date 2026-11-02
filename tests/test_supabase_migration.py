import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "supabase/migrations/20261102000100_initial_online_services.sql"
DOCS = ROOT / "docs/supabase-cloud-setup.md"


class SupabaseMigrationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sql = MIGRATION.read_text(encoding="utf-8").lower()
        cls.docs = DOCS.read_text(encoding="utf-8").lower()

    def test_expected_tables_exist(self):
        for table in (
            "profiles",
            "platform_identities",
            "player_characters",
            "player_presence",
            "matchmaking_requests",
        ):
            with self.subTest(table=table):
                self.assertIn(f"create table if not exists public.{table}", self.sql)

    def test_all_tables_enable_row_level_security(self):
        for table in (
            "profiles",
            "platform_identities",
            "player_characters",
            "player_presence",
            "matchmaking_requests",
        ):
            with self.subTest(table=table):
                self.assertIn(f"alter table public.{table} enable row level security", self.sql)

    def test_platform_identity_is_opaque_and_not_assumed_to_be_xuid(self):
        self.assertIn("external_subject text not null", self.sql)
        self.assertIn("opaque until xbox 360 identity semantics are proven", self.sql)
        self.assertIn("não assumir que seja xuid", self.docs)

    def test_no_client_policy_for_platform_identity_or_queue_writes(self):
        self.assertNotIn('on public.platform_identities for insert', self.sql)
        self.assertNotIn('on public.matchmaking_requests for insert', self.sql)
        self.assertIn("only trusted backend code", self.sql)

    def test_service_role_is_not_for_the_console(self):
        self.assertIn("never receive it", self.sql)
        self.assertIn("nunca no xex", self.docs)


if __name__ == "__main__":
    unittest.main()
