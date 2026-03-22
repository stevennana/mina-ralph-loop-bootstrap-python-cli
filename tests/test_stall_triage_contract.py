from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class StallTriageContractTests(unittest.TestCase):
    def test_public_readme_describes_triage_before_rca(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("`!` = worker stalled and the loop stopped for triage", readme)
        self.assertIn("Only repeated environment-specific blockers on the same task should branch into the RCA/fix exec-plan flow.", readme)

    def test_environment_blocker_reference_keeps_first_stall_as_triage(self) -> None:
        reference = (REPO_ROOT / "references" / "environment-blockers.md").read_text(encoding="utf-8")
        self.assertIn("hand the task to operator triage", reference)
        self.assertIn("A single stall does not automatically mean", reference)

    def test_generated_ralph_docs_and_loop_message_say_triage(self) -> None:
        ralph_readme = (
            REPO_ROOT / "assets" / "templates" / "ralph" / "scripts" / "ralph" / "README.md"
        ).read_text(encoding="utf-8")
        run_loop = (
            REPO_ROOT / "assets" / "templates" / "ralph" / "scripts" / "ralph" / "run-loop.sh"
        ).read_text(encoding="utf-8")
        self.assertIn("stalled worker triage stop", ralph_readme)
        self.assertIn("stops the unattended loop for operator triage", ralph_readme)
        self.assertIn('Stopping loop for triage.', run_loop)


if __name__ == "__main__":
    unittest.main()
