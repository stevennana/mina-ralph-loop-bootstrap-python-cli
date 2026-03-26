from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from companion_skills import DEFAULT_STARTUP_SKILL_NAMES, SKILLS  # noqa: E402


class CompanionSkillTests(unittest.TestCase):
    def test_python_preset_keeps_clean_architecture_as_the_only_default_startup_skill(self) -> None:
        self.assertEqual(DEFAULT_STARTUP_SKILL_NAMES, ("clean-architecture",))

    def test_clean_architecture_remains_the_only_pinned_skill_until_more_real_sources_are_added(self) -> None:
        self.assertEqual(set(SKILLS), {"clean-architecture", "mina-rich-cli-interface", "mina-uv-pytest-unit-testing"})
        self.assertEqual(DEFAULT_STARTUP_SKILL_NAMES, ("clean-architecture",))
        self.assertIn(
            "companion-skills/mina-uv-pytest-unit-testing",
            SKILLS["mina-uv-pytest-unit-testing"].source_path,
        )
        self.assertIn(
            "mina-ralph-loop-bootstrap-python-cli/companion-skills/mina-uv-pytest-unit-testing",
            "\n".join(SKILLS["mina-uv-pytest-unit-testing"].pinned_commands),
        )
        self.assertIn(
            "companion-skills/mina-rich-cli-interface",
            SKILLS["mina-rich-cli-interface"].source_path,
        )
        self.assertIn(
            "mina-ralph-loop-bootstrap-python-cli/companion-skills/mina-rich-cli-interface",
            "\n".join(SKILLS["mina-rich-cli-interface"].pinned_commands),
        )

    def test_readme_documents_desired_python_cli_companion_skills(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        for skill_name in [
            "python-packaging-release",
            "mina-rich-cli-interface",
            "config-and-secrets",
            "mina-uv-pytest-unit-testing",
            "systemd-worker-ops",
        ]:
            self.assertIn(skill_name, readme)
        self.assertNotIn("cli-ux-typer-rich", readme)
        self.assertIn("install mina-rich-cli-interface", readme)
        self.assertIn("install mina-uv-pytest-unit-testing", readme)


if __name__ == "__main__":
    unittest.main()
