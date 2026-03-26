from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from companion_skills import SKILLS  # noqa: E402


class CompanionSkillTests(unittest.TestCase):
    def test_python_preset_keeps_clean_architecture_as_the_only_pinned_installable_skill(self) -> None:
        self.assertEqual(list(SKILLS), ["clean-architecture"])

    def test_readme_documents_additional_python_cli_companion_skill_areas(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        for skill_area in [
            "python-packaging-release",
            "cli-ux-typer-rich",
            "config-and-secrets",
            "cli-testing-observability",
            "systemd-worker-ops",
        ]:
            self.assertIn(skill_area, readme)


if __name__ == "__main__":
    unittest.main()
