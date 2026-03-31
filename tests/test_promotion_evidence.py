from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RALPH_TEMPLATE_ROOT = REPO_ROOT / "assets" / "templates" / "ralph"


class PromotionEvidenceEvaluationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo_root = Path(self.temp_dir.name)
        shutil.copytree(RALPH_TEMPLATE_ROOT, self.repo_root, dirs_exist_ok=True)
        (self.repo_root / "docs" / "exec-plans" / "active").mkdir(parents=True, exist_ok=True)
        (self.repo_root / "docs" / "exec-plans" / "completed").mkdir(parents=True, exist_ok=True)
        (self.repo_root / "AGENTS.md").write_text("Read docs.\n", encoding="utf-8")
        (self.repo_root / "docs" / "PLANS.md").write_text("# Plans\n", encoding="utf-8")

        self.task_id = "107-report-result-and-real-llm-e2e-acceptance"
        taskmeta = {
            "id": self.task_id,
            "title": "Report result and real LLM E2E acceptance",
            "order": 107,
            "status": "active",
            "next_task_on_success": None,
            "prompt_docs": ["AGENTS.md", "docs/PLANS.md"],
            "required_commands": ["make verify-real-llm"],
            "required_files": [],
            "human_review_triggers": [],
            "promotion_evidence": [
                {
                    "id": "real-llm-proof",
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

                - run the live path

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

        subprocess.run(["node", "scripts/ralph/ensure-state.mjs"], cwd=self.repo_root, check=True)
        (self.repo_root / "state" / "current-task.txt").write_text(f"{self.task_id}\n", encoding="utf-8")

        self.bin_dir = self.repo_root / "test-bin"
        self.bin_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write_executable(self, name: str, content: str) -> None:
        path = self.bin_dir / name
        path.write_text(content, encoding="utf-8")
        path.chmod(0o755)

    def run_evaluator(self) -> subprocess.CompletedProcess[str]:
        env = dict(os.environ)
        env["PATH"] = f"{self.bin_dir}:{env.get('PATH', '')}"
        return subprocess.run(
            ["node", "scripts/ralph/evaluate-task.mjs"],
            cwd=self.repo_root,
            check=True,
            text=True,
            capture_output=True,
            env=env,
        )

    def test_evaluate_task_blocks_when_promotion_evidence_is_missing(self) -> None:
        self.write_executable(
            "make",
            "#!/bin/sh\n"
            "if [ \"$1\" = \"verify-real-llm\" ]; then\n"
            "  echo '1 passed'\n"
            "  exit 0\n"
            "fi\n"
            "echo \"unexpected make target: $1\" >&2\n"
            "exit 1\n",
        )
        self.write_executable("codex", "#!/bin/sh\nexit 99\n")

        self.run_evaluator()

        evaluation = json.loads((self.repo_root / "state" / "evaluation.json").read_text(encoding="utf-8"))
        self.assertEqual(evaluation["status"], "blocked")
        self.assertFalse(evaluation["promotion_eligible"])
        self.assertIn("promotion evidence is missing or invalid", evaluation["summary"])
        self.assertIn("Missing manifest", "\n".join(evaluation["missing_requirements"]))

    def test_evaluate_task_accepts_current_cycle_promotion_evidence(self) -> None:
        manifest_rel = f"state/artifacts/live-proofs/{self.task_id}/latest/manifest.json"
        log_rel = f"state/artifacts/live-proofs/{self.task_id}/latest/llm-operational.jsonl"
        self.write_executable(
            "make",
            textwrap.dedent(
                f"""\
                #!/bin/sh
                if [ "$1" = "verify-real-llm" ]; then
                  mkdir -p "$(dirname "{manifest_rel}")"
                  cat > "{log_rel}" <<'EOF'
                {{"event":"llm.request.started"}}
                {{"event":"llm.request.completed"}}
                EOF
                  checked_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
                  cat > "{manifest_rel}" <<EOF
                {{
                  "task_id": "{self.task_id}",
                  "producer_command": "make verify-real-llm",
                  "checked_at": "$checked_at",
                  "status": "passed",
                  "event_found": true,
                  "copied_log_path": "{log_rel}"
                }}
                EOF
                  echo '1 passed'
                  exit 0
                fi
                echo "unexpected make target: $1" >&2
                exit 1
                """
            ),
        )
        self.write_executable(
            "codex",
            "#!/bin/sh\n"
            "output=''\n"
            "while [ \"$#\" -gt 0 ]; do\n"
            "  if [ \"$1\" = \"-o\" ]; then\n"
            "    output=\"$2\"\n"
            "    shift 2\n"
            "    continue\n"
            "  fi\n"
            "  shift\n"
            "done\n"
            "cat > \"$output\" <<'EOF'\n"
            "{\"decision\":\"done\",\"recommend_promotion\":true,\"confidence\":0.9,\"summary\":\"Live proof completed.\",\"satisfied_exit_criteria\":[\"Live proof succeeds.\"],\"missing_requirements\":[],\"human_review_triggers\":[]}\n"
            "EOF\n",
        )

        self.run_evaluator()

        evaluation = json.loads((self.repo_root / "state" / "evaluation.json").read_text(encoding="utf-8"))
        self.assertEqual(evaluation["status"], "done")
        self.assertTrue(evaluation["promotion_eligible"])
        self.assertEqual(len(evaluation["promotion_evidence"]), 1)
        self.assertTrue(evaluation["promotion_evidence"][0]["valid"])
        self.assertEqual(evaluation["promotion_evidence"][0]["required_event_found"], True)


if __name__ == "__main__":
    unittest.main()
