from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PROMOTE_TASK_TEMPLATE = REPO_ROOT / "assets" / "templates" / "ralph" / "scripts" / "ralph" / "promote-task.mjs"
MANUAL_PROMOTE_TEMPLATE = REPO_ROOT / "assets" / "templates" / "ralph" / "scripts" / "ralph" / "manual-promote.sh"
TASK_UTILS_TEMPLATE = REPO_ROOT / "assets" / "templates" / "ralph" / "scripts" / "ralph" / "lib" / "task-utils.mjs"
BLOCKER_UTILS_TEMPLATE = REPO_ROOT / "assets" / "templates" / "ralph" / "scripts" / "ralph" / "lib" / "blocker-utils.mjs"


def write_task(path: Path, *, task_id: str, title: str, status: str, next_task_on_success: str | None) -> None:
    taskmeta = {
        "id": task_id,
        "title": title,
        "order": int(task_id.split("-", 1)[0]),
        "status": status,
        "next_task_on_success": next_task_on_success,
        "prompt_docs": ["AGENTS.md"],
        "required_commands": ["make verify"],
        "required_files": [],
        "human_review_triggers": [],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                f"# {title}",
                "",
                "```json taskmeta",
                json.dumps(taskmeta, indent=2),
                "```",
                "",
                "## Progress log",
                "",
                "- Start here.",
                "",
            ]
        ),
        encoding="utf-8",
    )


class ManualPromotionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="manual-promotion-test-"))
        self.repo_root = self.temp_dir / "repo"
        (self.repo_root / "scripts" / "ralph" / "lib").mkdir(parents=True, exist_ok=True)
        shutil.copy2(PROMOTE_TASK_TEMPLATE, self.repo_root / "scripts" / "ralph" / "promote-task.mjs")
        shutil.copy2(MANUAL_PROMOTE_TEMPLATE, self.repo_root / "scripts" / "ralph" / "manual-promote.sh")
        shutil.copy2(TASK_UTILS_TEMPLATE, self.repo_root / "scripts" / "ralph" / "lib" / "task-utils.mjs")
        shutil.copy2(BLOCKER_UTILS_TEMPLATE, self.repo_root / "scripts" / "ralph" / "lib" / "blocker-utils.mjs")

        (self.repo_root / "state").mkdir(parents=True, exist_ok=True)
        (self.repo_root / "state" / "current-task.txt").write_text("025-owner-shell-density-reset\n", encoding="utf-8")
        (self.repo_root / "state" / "task-history.md").write_text("", encoding="utf-8")

        write_task(
            self.repo_root / "docs" / "exec-plans" / "active" / "025-owner-shell-density-reset.md",
            task_id="025-owner-shell-density-reset",
            title="Owner shell density reset",
            status="active",
            next_task_on_success="026-owner-dashboard-density",
        )
        write_task(
            self.repo_root / "docs" / "exec-plans" / "active" / "026-owner-dashboard-density.md",
            task_id="026-owner-dashboard-density",
            title="Owner dashboard density",
            status="queued",
            next_task_on_success=None,
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def run_node(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["node", *args],
            cwd=self.repo_root,
            check=False,
            capture_output=True,
            text=True,
        )

    def write_not_eligible_evaluation(self) -> None:
        (self.repo_root / "state" / "evaluation.json").write_text(
            json.dumps(
                {
                    "task_id": "025-owner-shell-density-reset",
                    "status": "not_done",
                    "promotion_eligible": False,
                    "summary": "stalled",
                    "missing_requirements": ["worker stalled"],
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    def test_manual_promotion_overrides_not_eligible_evaluation(self) -> None:
        artifact = "state/artifacts/20260321T112504-025-owner-shell-density-reset"
        self.write_not_eligible_evaluation()

        result = self.run_node(
            "scripts/ralph/promote-task.mjs",
            "--manual",
            "--reason",
            "task is complete; loop stalled after implementation",
            "--artifact",
            artifact,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Manually promoted 025-owner-shell-density-reset -> 026-owner-dashboard-density", result.stdout)
        self.assertFalse((self.repo_root / "docs" / "exec-plans" / "active" / "025-owner-shell-density-reset.md").exists())
        self.assertTrue((self.repo_root / "docs" / "exec-plans" / "completed" / "025-owner-shell-density-reset.md").exists())
        self.assertEqual(
            (self.repo_root / "state" / "current-task.txt").read_text(encoding="utf-8").strip(),
            "026-owner-dashboard-density",
        )
        next_markdown = (self.repo_root / "docs" / "exec-plans" / "active" / "026-owner-dashboard-density.md").read_text(
            encoding="utf-8"
        )
        self.assertIn('"status": "active"', next_markdown)

        evaluation = json.loads((self.repo_root / "state" / "evaluation.json").read_text(encoding="utf-8"))
        self.assertTrue(evaluation["promotion_eligible"])
        self.assertEqual(evaluation["manual_override"]["reason"], "task is complete; loop stalled after implementation")
        self.assertEqual(evaluation["manual_override"]["artifact"], artifact)

        history = (self.repo_root / "state" / "task-history.md").read_text(encoding="utf-8")
        self.assertIn("manually promoted 025-owner-shell-density-reset -> 026-owner-dashboard-density", history)

    def test_manual_promotion_without_args_uses_default_reason(self) -> None:
        self.write_not_eligible_evaluation()

        result = self.run_node("scripts/ralph/promote-task.mjs", "--manual")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Manually promoted 025-owner-shell-density-reset -> 026-owner-dashboard-density", result.stdout)
        evaluation = json.loads((self.repo_root / "state" / "evaluation.json").read_text(encoding="utf-8"))
        self.assertEqual(evaluation["manual_override"]["reason"], "operator manual promotion")
        self.assertIsNone(evaluation["manual_override"]["artifact"])

        history = (self.repo_root / "state" / "task-history.md").read_text(encoding="utf-8")
        self.assertIn("reason=operator manual promotion", history)

    def test_manual_promotion_with_only_artifact_uses_default_reason(self) -> None:
        artifact = "state/artifacts/20260321T112504-025-owner-shell-density-reset"
        self.write_not_eligible_evaluation()

        result = self.run_node("scripts/ralph/promote-task.mjs", "--manual", "--artifact", artifact)

        self.assertEqual(result.returncode, 0, result.stderr)
        evaluation = json.loads((self.repo_root / "state" / "evaluation.json").read_text(encoding="utf-8"))
        self.assertEqual(evaluation["manual_override"]["reason"], "operator manual promotion")
        self.assertEqual(evaluation["manual_override"]["artifact"], artifact)

    def test_regular_promotion_still_refuses_not_eligible_task(self) -> None:
        self.write_not_eligible_evaluation()

        result = self.run_node("scripts/ralph/promote-task.mjs")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Task 025-owner-shell-density-reset not eligible for promotion.", result.stdout)
        self.assertTrue((self.repo_root / "docs" / "exec-plans" / "active" / "025-owner-shell-density-reset.md").exists())
        self.assertFalse((self.repo_root / "docs" / "exec-plans" / "completed" / "025-owner-shell-density-reset.md").exists())


if __name__ == "__main__":
    unittest.main()
