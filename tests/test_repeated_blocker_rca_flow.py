from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RALPH_TEMPLATE_ROOT = REPO_ROOT / "assets" / "templates" / "ralph"


class RepeatedBlockerRcaFlowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo_root = Path(self.temp_dir.name)
        shutil.copytree(RALPH_TEMPLATE_ROOT, self.repo_root, dirs_exist_ok=True)

        (self.repo_root / "docs" / "exec-plans" / "active").mkdir(parents=True, exist_ok=True)
        (self.repo_root / "docs" / "exec-plans" / "completed").mkdir(parents=True, exist_ok=True)
        (self.repo_root / "docs" / "exec-plans" / "tech-debt-tracker.md").write_text(
            "# Tech Debt Tracker\n\n## Current Debt\n\n- Existing debt item.\n",
            encoding="utf-8",
        )
        (self.repo_root / "AGENTS.md").write_text("Read docs.\n", encoding="utf-8")
        (self.repo_root / "docs" / "PLANS.md").write_text("# PLANS\n", encoding="utf-8")

        self.parent_task_id = "077-external-note-api-auth-foundation"
        self.parent_task_path = (
            self.repo_root / "docs" / "exec-plans" / "active" / f"{self.parent_task_id}.md"
        )
        self.parent_task_path.write_text(self.build_parent_task_markdown(), encoding="utf-8")

        self.run_node("scripts/ralph/ensure-state.mjs")
        (self.repo_root / "state" / "current-task.txt").write_text(
            f"{self.parent_task_id}\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def build_parent_task_markdown(self) -> str:
        taskmeta = {
            "id": self.parent_task_id,
            "title": "External note API auth foundation",
            "order": 77,
            "status": "active",
            "promotion_mode": "standard",
            "next_task_on_success": "078-external-note-api-create-and-publish",
            "prompt_docs": ["AGENTS.md", "docs/PLANS.md"],
            "required_commands": ["make verify"],
            "required_files": ["src/app/api"],
            "human_review_triggers": ["Do not broaden scope."],
        }
        return textwrap.dedent(
            f"""\
            # External note API auth foundation

            ```json taskmeta
            {json.dumps(taskmeta, indent=2)}
            ```

            ## Objective

            Add the auth boundary.

            ## Scope

            - auth boundary

            ## Out of scope

            - UI regression fixes

            ## Exit criteria

            1. `make verify` passes.

            ## Required checks

            - `make verify`

            ## Evaluator notes

            Keep the task narrow.

            ## Progress log

            - initial note
            """
        )

    def write_failing_evaluation(self) -> None:
        payload = {
            "checked_at": "2026-03-22T16:26:00Z",
            "task_id": self.parent_task_id,
            "status": "not_done",
            "promotion_eligible": False,
            "deterministic": {
                "checked_at": "2026-03-22T16:26:00Z",
                "task_id": self.parent_task_id,
                "pass": False,
                "commands": [
                    {
                        "command": "make verify",
                        "ok": False,
                        "output": "FAILED tests/e2e/test_cli_auth.py::test_login_flow\nFAILED tests/e2e/test_cli_queue.py::test_queue_listing\n",
                        "error": "AssertionError: expected output in tests/e2e/test_cli_auth.py\n",
                    }
                ],
                "missing_files": [],
            },
            "summary": "Deterministic checks failed; task is not ready for promotion.",
        }
        (self.repo_root / "state" / "evaluation.json").write_text(
            json.dumps(payload, indent=2) + "\n",
            encoding="utf-8",
        )

    def run_node(self, script_relative_path: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["node", script_relative_path, *args],
            cwd=self.repo_root,
            check=True,
            text=True,
            capture_output=True,
        )

    def read_json(self, relative_path: str) -> dict:
        return json.loads((self.repo_root / relative_path).read_text(encoding="utf-8"))

    def test_repeated_blocker_branches_and_returns_to_parent(self) -> None:
        self.write_failing_evaluation()

        for expected_count in (1, 2, 3):
            completed = self.run_node("scripts/ralph/record-blocker.mjs", "--kind", "evaluation")
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["repeat_count"], expected_count)
            self.assertEqual(payload["signature"].split("|")[0], "deterministic_failure")

        branch = self.run_node("scripts/ralph/branch-rca-task.mjs")
        branch_payload = json.loads(branch.stdout)
        self.assertTrue(branch_payload["branched"])
        rca_task_id = branch_payload["rca_task_id"]

        current_task = (self.repo_root / "state" / "current-task.txt").read_text(encoding="utf-8").strip()
        self.assertEqual(current_task, rca_task_id)

        parent_markdown = self.parent_task_path.read_text(encoding="utf-8")
        self.assertIn('"status": "blocked"', parent_markdown)
        self.assertIn(f'"blocked_by_task_id": "{rca_task_id}"', parent_markdown)

        tracker = self.read_json("state/blocker-tracker.json")
        signature = branch_payload["blocker_signature"]
        entry = tracker["tasks"][self.parent_task_id]["signatures"][signature]
        self.assertEqual(entry["repeat_count"], 3)
        self.assertEqual(entry["branched_to_task_id"], rca_task_id)

        rca_task_path = self.repo_root / "docs" / "exec-plans" / "active" / f"{rca_task_id}.md"
        self.assertTrue(rca_task_path.exists())
        rca_markdown = rca_task_path.read_text(encoding="utf-8")
        self.assertIn(f'"rca_for_task_id": "{self.parent_task_id}"', rca_markdown)
        self.assertIn(f'"next_task_on_success": "{self.parent_task_id}"', rca_markdown)

        tech_debt = (
            self.repo_root / "docs" / "exec-plans" / "tech-debt-tracker.md"
        ).read_text(encoding="utf-8")
        self.assertIn(rca_task_id, tech_debt)

        prompt = self.run_node("scripts/ralph/render-task-prompt.mjs")
        prompt_path = self.repo_root / prompt.stdout.strip()
        rendered_prompt = prompt_path.read_text(encoding="utf-8")
        self.assertIn("This is an auto-generated blocker RCA task", rendered_prompt)
        self.assertIn(f"Do not resume or broaden into parent task {self.parent_task_id}", rendered_prompt)

        (self.repo_root / "state" / "evaluation.json").write_text(
            json.dumps(
                {
                    "task_id": rca_task_id,
                    "status": "done",
                    "promotion_eligible": True,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        self.run_node("scripts/ralph/promote-task.mjs")

        current_task = (self.repo_root / "state" / "current-task.txt").read_text(encoding="utf-8").strip()
        self.assertEqual(current_task, self.parent_task_id)

        restored_parent = self.parent_task_path.read_text(encoding="utf-8")
        self.assertIn('"status": "active"', restored_parent)
        self.assertNotIn('"blocked_by_task_id"', restored_parent)
        self.assertIn("blocker RCA task", restored_parent)

        completed_rca_path = self.repo_root / "docs" / "exec-plans" / "completed" / f"{rca_task_id}.md"
        self.assertTrue(completed_rca_path.exists())
        self.assertFalse(rca_task_path.exists())

        tracker_after_promotion = self.read_json("state/blocker-tracker.json")
        self.assertEqual(tracker_after_promotion["tasks"], {})


if __name__ == "__main__":
    unittest.main()
