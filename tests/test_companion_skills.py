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

    def test_readme_points_to_reference_as_the_detailed_companion_skill_source(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("references/python-cli-uv-preset.md", readme)
        for skill_name in ["mina-rich-cli-interface", "mina-uv-pytest-unit-testing"]:
            self.assertIn(skill_name, readme)
        self.assertNotIn("python-packaging-release", readme)
        self.assertNotIn("config-and-secrets", readme)
        self.assertNotIn("systemd-worker-ops", readme)
        self.assertIn("install mina-rich-cli-interface", readme)
        self.assertIn("install mina-uv-pytest-unit-testing", readme)

    def test_skill_md_points_to_reference_for_later_companion_skill_policy(self) -> None:
        skill = (REPO_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("references/python-cli-uv-preset.md", skill)
        self.assertIn("mina-rich-cli-interface", skill)
        self.assertIn("mina-uv-pytest-unit-testing", skill)
        self.assertNotIn("python-packaging-release", skill)
        self.assertNotIn("config-and-secrets", skill)
        self.assertNotIn("systemd-worker-ops", skill)

    def test_uv_pytest_skill_encodes_the_added_uv_workflow_guidance(self) -> None:
        skill = (REPO_ROOT / "companion-skills" / "mina-uv-pytest-unit-testing" / "SKILL.md").read_text(encoding="utf-8")
        reference = (
            REPO_ROOT / "companion-skills" / "mina-uv-pytest-unit-testing" / "references" / "uv-testing-workflow.md"
        ).read_text(encoding="utf-8")

        self.assertIn("references/uv-testing-workflow.md", skill)
        for phrase in [
            "uv sync",
            "uv init --package",
            "uv tool install",
            "uv tool upgrade",
            "workspace = true",
        ]:
            self.assertIn(phrase, reference)

    def test_rich_cli_skill_encodes_cli_design_guidance(self) -> None:
        skill = (REPO_ROOT / "companion-skills" / "mina-rich-cli-interface" / "SKILL.md").read_text(encoding="utf-8")
        for phrase in [
            "Rich CLI / Command-Line UI Design Guidelines",
            "Separate human output from machine output",
            "--json",
            "NO_COLOR",
            "TERM=dumb",
            "Interactive prompts must be optional",
            "Use progress indicators honestly",
            "Linux and macOS Service-Oriented CLI Guidance",
            "When choosing between a prettier interface and a more reliable one, prefer reliability.",
        ]:
            self.assertIn(phrase, skill)


if __name__ == "__main__":
    unittest.main()
