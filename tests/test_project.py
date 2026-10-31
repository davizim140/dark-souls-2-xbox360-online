from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class ProjectStructureTests(unittest.TestCase):
    def test_required_docs_exist(self):
        for relative in (
            "README.md",
            "docs/architecture.md",
            "docs/research-plan.md",
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

if __name__ == "__main__":
    unittest.main(verbosity=2)
