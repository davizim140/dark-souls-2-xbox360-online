from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class ProjectStructureTests(unittest.TestCase):
    def test_required_docs_exist(self):
        for relative in (
            "README.md",
            "docs/architecture.md",
            "docs/research-plan.md",
            "docs/protocol/xbox360-connection-failure-analysis.md",
            "docs/compatibility/ds2-breakin-visitor-manager-audit.md",
            "docs/compatibility/ds2-player-data-state-audit.md",
            "docs/compatibility/ds2-character-persistence-audit.md",
            "docs/compatibility/ds2-upstream-steam-dependency-audit.md",
            "docs/compatibility/ds2-steam-identity-dependency-audit.md",
            "docs/protocol/ds2-allstatus-protobuf-field-audit.md",
            "docs/protocol/ds2-player-status-upload-config-audit.md",
            "docs/compatibility/ds2-matchmaking-manager-audit.md",
            "docs/compatibility/ds2-ghosts-messages-bloodstains-audit.md",
            ".github/workflows/ci.yml",
            "backend/include/identity/external_identity.hpp",
            "backend/tests/external_identity_test.cpp",
            "backend/include/identity/identity_registry.hpp",
            "backend/tests/identity_registry_test.cpp",
            "docs/architecture/identity-registry.md",
            "docs/compatibility/ds2-identity-migration-audit.md",
            "docs/compatibility/ds2-copy-migration-contract.md",
            "docs/compatibility/dsos-ds2-pc-client-redirection-audit.md",
            "docs/compatibility/dsos-xboxone-stubs-not-xbox360-audit.md",
            "backend/include/identity/sqlite_identity_store.hpp",
            "backend/src/identity/sqlite_identity_store.cpp",
            "backend/tests/sqlite_identity_store_test.cpp",
            "tools/inspect_dsos_identity_db.py",
            "tools/migrate_dsos_identity_copy.py",
            "tests/test_dsos_db_inspector.py",
            "tests/test_dsos_identity_migration.py",
        ):
            with self.subTest(path=relative):
                self.assertTrue((ROOT / relative).is_file(), relative)

    def test_status_is_honest(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("fase de levantamento técnico", readme)
        self.assertIn("Não implementado", readme)
        self.assertNotIn("XEX funcional já compilado", readme)

    def test_plan_requires_evidence(self):
        plan = (ROOT / "docs/research-plan.md").read_text(encoding="utf-8")
        self.assertIn("Title ID", plan)
        self.assertIn("evidências", plan.lower())

    def test_dsos_pc_redirect_is_not_misrepresented_as_xbox_support(self):
        report = (ROOT / "docs/compatibility/dsos-ds2-pc-client-redirection-audit.md").read_text(encoding="utf-8").lower()
        self.assertIn("50031", report)
        self.assertIn("winsock", report)
        self.assertIn("injector.dll", report)
        self.assertIn("steam", report)
        self.assertIn("protocolo xbox permanece não identificado", report)

    def test_dsos_xboxone_stubs_are_not_claimed_as_xbox360_support(self):
        report = (ROOT / "docs/compatibility/dsos-xboxone-stubs-not-xbox360-audit.md").read_text(encoding="utf-8").lower()
        self.assertIn("requestqueryloginserverinfoforxboxone", report)
        self.assertIn("getservicestatusforxboxone", report)
        self.assertIn("loginclient.cpp", report)
        self.assertIn("steamticket", report)
        self.assertIn("não é evidência de xbox 360", report)
        self.assertIn("não cria xex", report)

    def test_xbox_connection_failure_does_not_claim_unknown_protocol_details(self):
        report = (ROOT / "docs/protocol/xbox360-connection-failure-analysis.md").read_text(encoding="utf-8").lower()
        self.assertIn("protocolo xbox 360 não identificado", report)
        self.assertIn("não identifica qual etapa falhou", report)
        self.assertIn("hostname", report)
        self.assertIn("desconhecida", report)
        self.assertIn("não implementar ainda", report)

    def test_upstream_audits_preserve_xbox_compatibility_boundary(self):
        paths = (
            "docs/compatibility/ds2-breakin-visitor-manager-audit.md",
            "docs/compatibility/ds2-player-data-state-audit.md",
            "docs/compatibility/ds2-character-persistence-audit.md",
            "docs/compatibility/ds2-upstream-steam-dependency-audit.md",
            "docs/protocol/ds2-allstatus-protobuf-field-audit.md",
            "docs/compatibility/ds2-matchmaking-manager-audit.md",
            "docs/compatibility/ds2-ghosts-messages-bloodstains-audit.md",
        )
        for relative in paths:
            with self.subTest(path=relative):
                content = (ROOT / relative).read_text(encoding="utf-8").lower()
                self.assertIn("xbox", content)
                self.assertTrue("não" in content or "not" in content)

if __name__ == "__main__":
    unittest.main(verbosity=2)
