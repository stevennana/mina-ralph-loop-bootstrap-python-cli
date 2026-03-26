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

    def test_encoded_later_companion_skills_are_available(self) -> None:
        self.assertEqual(
            set(SKILLS),
            {
                "clean-architecture",
                "python-packaging-release",
                "cli-ux-typer-rich",
                "config-and-secrets",
                "cli-testing-observability",
                "systemd-worker-ops",
            },
        )
        self.assertIn("companion-skills/cli-ux-typer-rich", SKILLS["cli-ux-typer-rich"].source_path)
        self.assertIn(
            "mina-ralph-loop-bootstrap-python-cli/companion-skills/cli-ux-typer-rich",
            "\n".join(SKILLS["cli-ux-typer-rich"].pinned_commands),
        )

    def test_readme_documents_later_installable_companion_skills(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        for skill_name in [
            "python-packaging-release",
            "cli-ux-typer-rich",
            "config-and-secrets",
            "cli-testing-observability",
            "systemd-worker-ops",
        ]:
            self.assertIn(skill_name, readme)
        self.assertIn("python3 <skill>/scripts/companion_skills.py install cli-ux-typer-rich", readme)


if __name__ == "__main__":
    unittest.main()
