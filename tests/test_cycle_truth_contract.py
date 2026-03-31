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


class CycleTruthContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo_root = Path(self.temp_dir.name)
        shutil.copytree(RALPH_TEMPLATE_ROOT, self.repo_root, dirs_exist_ok=True)
        (self.repo_root / "docs" / "exec-plans" / "active").mkdir(parents=True, exist_ok=True)
        (self.repo_root / "docs" / "exec-plans" / "completed").mkdir(parents=True, exist_ok=True)
        (self.repo_root / "AGENTS.md").write_text("Read docs.\n", encoding="utf-8")
        (self.repo_root / "docs" / "PLANS.md").write_text("# PLANS\n", encoding="utf-8")

        self.task_id = "107-report-result-and-real-llm-e2e-acceptance"
        self.live_proof_manifest = (
            self.repo_root
            / "state"
            / "artifacts"
            / "live-proofs"
            / self.task_id
            / "latest"
            / "manifest.json"
        )
        self.live_proof_log = self.live_proof_manifest.parent / "llm-operational.jsonl"
        taskmeta = {
            "id": self.task_id,
            "title": "Report result and real LLM E2E acceptance",
            "order": 107,
            "status": "active",
            "next_task_on_success": None,
            "prompt_docs": ["AGENTS.md", "docs/PLANS.md"],
            "required_commands": ["make verify", "make verify-real-llm"],
            "required_files": [],
            "human_review_triggers": ["Do not broaden scope."],
            "promotion_evidence": [
                {
                    "id": "real-llm-onboarding-report",
                    "kind": "jsonl_event_log",
                    "producer_command": "make verify-real-llm",
                    "manifest_path": f"state/artifacts/live-proofs/{self.task_id}/latest/manifest.json",
                    "log_path": f"state/artifacts/live-proofs/{self.task_id}/latest/llm-operational.jsonl",
                    "required_event": "llm.request.completed",
                    "freshness": "current_cycle",
                }
            ],
            "execution_requirements": {
                "worker_sandbox": "danger-full-access",
                "evaluator_sandbox": "read-only",
                "network_required": True,
                "blocker_policy": "external_runtime_rca_after_3",
            },
        }
        (self.repo_root / "docs" / "exec-plans" / "active" / f"{self.task_id}.md").write_text(
            textwrap.dedent(
                f"""\
                # Report result and real LLM E2E acceptance

                ```json taskmeta
                {json.dumps(taskmeta, indent=2)}
                ```

                ## Objective

                Prove the live path.

                ## Scope

                - run the live real-LLM path

                ## Out of scope

                - unrelated refactors

                ## Exit criteria

                1. Live proof succeeds.

                ## Evaluator notes

                Prefer current-cycle truth.
                """
            ),
            encoding="utf-8",
        )

        self.run_node("scripts/ralph/ensure-state.mjs")
        (self.repo_root / "state" / "current-task.txt").write_text(f"{self.task_id}\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def run_node(self, script_relative_path: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["node", script_relative_path, *args],
            cwd=self.repo_root,
            check=True,
            text=True,
            capture_output=True,
        )

    def write_live_proof(self, *, checked_at: str, status: str = "passed", event_found: bool = True) -> None:
        self.live_proof_manifest.parent.mkdir(parents=True, exist_ok=True)
        self.live_proof_log.write_text(
            "\n".join(
                [
                    json.dumps({"event": "llm.request.started"}),
                    json.dumps({"event": "llm.request.completed"}) if event_found else json.dumps({"event": "llm.request.failed"}),
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        self.live_proof_manifest.write_text(
            json.dumps(
                {
                    "task_id": self.task_id,
                    "producer_command": "make verify-real-llm",
                    "checked_at": checked_at,
                    "status": status,
                    "event_found": event_found,
                    "copied_log_path": f"state/artifacts/live-proofs/{self.task_id}/latest/llm-operational.jsonl",
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    def test_render_evaluator_prompt_declares_current_cycle_precedence(self) -> None:
        self.write_live_proof(checked_at="2026-03-31T00:00:01Z")
        (self.repo_root / "state" / "deterministic-checks.json").write_text(
            json.dumps(
                {
                    "checked_at": "2026-03-31T00:00:00Z",
                    "task_id": self.task_id,
                    "pass": True,
                    "commands": [
                        {"command": "make verify", "ok": True, "output": "ok"},
                        {"command": "make verify-real-llm", "ok": True, "output": "1 passed, 78 deselected"},
                    ],
                    "missing_files": [],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (self.repo_root / "state" / "worker-handoff.txt").write_text(
            "Worker observed an earlier blocked narrative and suspects the live path may still be blocked.\n",
            encoding="utf-8",
        )

        result = self.run_node("scripts/ralph/render-evaluator-prompt.mjs")
        prompt_path = self.repo_root / result.stdout.strip()
        prompt = prompt_path.read_text(encoding="utf-8")

        self.assertIn("Worker handoff summary from this cycle:", prompt)
        self.assertIn("Promotion evidence summary for this cycle:", prompt)
        self.assertIn("Authoritative precedence for this cycle:", prompt)
        self.assertIn("treat the current-cycle deterministic check summary as the primary machine-readable truth", prompt)
        self.assertIn("treat current-cycle promotion evidence manifests as the primary live-proof truth", prompt)
        self.assertIn("do not let stale blocked narrative override current-cycle passing checks", prompt)

    def test_write_cycle_summary_makes_evaluation_authoritative(self) -> None:
        (self.repo_root / "state" / "deterministic-checks.json").write_text(
            json.dumps(
                {
                    "task_id": self.task_id,
                    "pass": True,
                    "commands": [{"command": "make verify-real-llm", "ok": True, "output": "1 passed"}],
                    "missing_files": [],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (self.repo_root / "state" / "worker-handoff.txt").write_text(
            "Worker suspected a block before evaluator reran commands.\n",
            encoding="utf-8",
        )
        (self.repo_root / "state" / "evaluation.json").write_text(
            json.dumps(
                {
                    "task_id": self.task_id,
                    "status": "done",
                    "promotion_eligible": True,
                    "summary": "Live proof completed successfully in the current cycle.",
                    "execution_requirements": {
                        "worker_sandbox": "danger-full-access",
                        "evaluator_sandbox": "read-only",
                        "network_required": True,
                        "blocker_policy": "external_runtime_rca_after_3",
                    },
                    "llm": {
                        "satisfied_exit_criteria": ["Live proof succeeds."],
                    },
                    "promotion_evidence": [
                        {
                            "id": "real-llm-onboarding-report",
                            "valid": True,
                        }
                    ],
                    "missing_requirements": [],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        self.run_node("scripts/ralph/write-cycle-summary.mjs")

        cycle_summary = json.loads((self.repo_root / "state" / "current-cycle-summary.json").read_text(encoding="utf-8"))
        last_result = (self.repo_root / "state" / "last-result.txt").read_text(encoding="utf-8")

        self.assertEqual(cycle_summary["authoritative_source"], "evaluation")
        self.assertEqual(cycle_summary["status"], "done")
        self.assertTrue(cycle_summary["promotion_eligible"])
        self.assertIn("Authoritative current-cycle decision: status=`done` promotion=`true`.", last_result)
        self.assertIn("Promotion evidence: 1/1 item(s) valid for this cycle.", last_result)
        self.assertIn("Worker handoff from this cycle (context only, not authoritative for promotion):", last_result)
        self.assertIn("Worker suspected a block before evaluator reran commands.", last_result)


if __name__ == "__main__":
    unittest.main()
