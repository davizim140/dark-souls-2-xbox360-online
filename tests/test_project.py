from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class ProjectStructureTests(unittest.TestCase):
    def test_required_docs_exist(self):
        for relative in (
            "README.md",
            "docs/architecture.md",
            "docs/research-plan.md",
            "docs/compatibility/ds2-breakin-visitor-manager-audit.md",
            "docs/compatibility/ds2-player-data-state-audit.md",
            "docs/compatibility/ds2-character-persistence-audit.md",
            "docs/compatibility/ds2-upstream-steam-dependency-audit.md",
            "docs/protocol/ds2-allstatus-protobuf-field-audit.md",
            "docs/protocol/ds2-player-status-upload-config-audit.md",
            "docs/compatibility/ds2-matchmaking-manager-audit.md",
            "docs/compatibility/ds2-ghosts-messages-bloodstains-audit.md",
            ".github/workflows/ci.yml",
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
