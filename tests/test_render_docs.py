from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from render_docs import (  # noqa: E402
    _normalize_slice_size,
    _resolve_backlog_target,
    derive_exec_tasks_from_feature_specs,
    validate_exec_tasks,
)


def make_feature_spec(
    title: str,
    *,
    behavior_count: int = 4,
    validation_count: int = 3,
    with_external_dependency: bool = False,
) -> dict[str, object]:
    slug = title.lower().replace(" ", "-")
    behavior = [f"{title} behavior {index}" for index in range(1, behavior_count + 1)]
    validation = [f"{title} validation {index}" for index in range(1, validation_count + 1)]
    required_commands = ["make verify"]
    if with_external_dependency:
        behavior.append(f"{title} integrates with a third-party provider")
        validation.append(f"{title} passes the relevant end-to-end scenario")
        required_commands.append("make test-e2e")
    return {
        "title": title,
        "slug": slug,
        "goal": f"Implement {title}.",
        "trigger": f"User starts {title}.",
        "scope": title,
        "behavior_bullets": behavior,
        "validation_bullets": validation,
        "required_commands": required_commands,
    }


class RenderDocsDerivationTests(unittest.TestCase):
    def test_defaults_to_balanced_slice_size(self) -> None:
        self.assertEqual(_normalize_slice_size(None), "balanced")
        self.assertEqual(_normalize_slice_size("balanced"), "balanced")

    def test_default_backlog_target_prefers_twelve_total_tasks(self) -> None:
        target = _resolve_backlog_target({}, slice_size="balanced", feature_count=4)
        self.assertEqual(target["minimum_total_tasks"], 10)
        self.assertEqual(target["preferred_total_tasks"], 12)
        self.assertEqual(target["maximum_total_tasks"], 15)

    def test_balanced_default_can_expand_beyond_five_tasks(self) -> None:
        feature_specs = [
            make_feature_spec("Auth And Invites", with_external_dependency=True),
            make_feature_spec("Note Editing"),
            make_feature_spec("Search Retrieval", with_external_dependency=True),
            make_feature_spec("Sharing"),
        ]

        exec_tasks = derive_exec_tasks_from_feature_specs(
            feature_specs,
            "demo-app",
            runtime_startup_required=False,
            slice_size="balanced",
            preferred_total_tasks=11,
        )

        self.assertGreater(len(exec_tasks), 5)
        self.assertEqual(exec_tasks[-1]["title"], "Hardening and maintenance")
        self.assertEqual(exec_tasks[0]["status"], "active")
        self.assertTrue(any(task["title"].startswith("Auth And Invites:") for task in exec_tasks[:-1]))

    def test_one_large_feature_can_expand_into_multiple_tasks_for_same_spec(self) -> None:
        feature_specs = [
            make_feature_spec("Search Retrieval", behavior_count=5, validation_count=4, with_external_dependency=True),
        ]

        exec_tasks = derive_exec_tasks_from_feature_specs(
            feature_specs,
            "demo-app",
            runtime_startup_required=False,
            slice_size="balanced",
            preferred_total_tasks=4,
        )

        non_hardening = exec_tasks[:-1]
        self.assertGreaterEqual(len(non_hardening), 3)
        validate_exec_tasks(feature_specs, exec_tasks)
        prompt_docs_sets = {tuple(task["prompt_docs"]) for task in non_hardening}
        self.assertEqual(len(prompt_docs_sets), 1)
        self.assertTrue(any("Acceptance And Edge Coverage" in task["title"] for task in non_hardening))

    def test_slice_size_changes_task_count(self) -> None:
        feature_specs = [
            make_feature_spec("Uploads And Media", behavior_count=6, validation_count=4, with_external_dependency=True),
        ]

        coarse = derive_exec_tasks_from_feature_specs(
            feature_specs,
            "demo-app",
            runtime_startup_required=False,
            slice_size="coarse",
            preferred_total_tasks=2,
        )
        balanced = derive_exec_tasks_from_feature_specs(
            feature_specs,
            "demo-app",
            runtime_startup_required=False,
            slice_size="balanced",
            preferred_total_tasks=4,
        )
        micro = derive_exec_tasks_from_feature_specs(
            feature_specs,
            "demo-app",
            runtime_startup_required=False,
            slice_size="micro",
            preferred_total_tasks=5,
        )

        self.assertLess(len(coarse), len(balanced))
        self.assertLessEqual(len(balanced), len(micro))

    def test_validator_accepts_multiple_tasks_for_one_product_spec(self) -> None:
        feature_specs = [make_feature_spec("AI Tagging", behavior_count=5, validation_count=4, with_external_dependency=True)]
        exec_tasks = derive_exec_tasks_from_feature_specs(
            feature_specs,
            "demo-app",
            runtime_startup_required=False,
            slice_size="micro",
            preferred_total_tasks=5,
        )

        validate_exec_tasks(feature_specs, exec_tasks)

    def test_external_acceptance_task_gets_network_execution_requirements(self) -> None:
        feature_specs = [make_feature_spec("Real LLM Reporting", with_external_dependency=True)]

        exec_tasks = derive_exec_tasks_from_feature_specs(
            feature_specs,
            "demo-app",
            runtime_startup_required=False,
            slice_size="balanced",
            preferred_total_tasks=3,
        )

        coverage_task = next(task for task in exec_tasks if "Acceptance And Edge Coverage" in str(task["title"]))
        requirements = coverage_task["execution_requirements"]
        self.assertEqual(requirements["worker_sandbox"], "danger-full-access")
        self.assertEqual(requirements["evaluator_sandbox"], "read-only")
        self.assertTrue(requirements["network_required"])
        self.assertEqual(requirements["blocker_policy"], "external_runtime_rca_after_3")
        promotion_evidence = coverage_task["promotion_evidence"]
        self.assertEqual(len(promotion_evidence), 1)
        self.assertEqual(promotion_evidence[0]["kind"], "command_artifact")
        self.assertEqual(promotion_evidence[0]["producer_command"], "make verify")
        self.assertEqual(
            promotion_evidence[0]["manifest_path"],
            "state/artifacts/live-proofs/real-llm-reporting-acceptance-and-edge-coverage/latest/manifest.json",
        )
        self.assertEqual(promotion_evidence[0]["freshness"], "current_cycle")

    def test_default_tasks_keep_default_execution_requirements(self) -> None:
        feature_specs = [make_feature_spec("Note Editing", with_external_dependency=False)]

        exec_tasks = derive_exec_tasks_from_feature_specs(
            feature_specs,
            "demo-app",
            runtime_startup_required=False,
            slice_size="balanced",
            preferred_total_tasks=2,
        )

        primary_task = exec_tasks[0]
        hardening_task = exec_tasks[-1]
        for task in (primary_task, hardening_task):
            requirements = task["execution_requirements"]
            self.assertEqual(requirements["worker_sandbox"], "workspace-write")
            self.assertEqual(requirements["evaluator_sandbox"], "read-only")
            self.assertFalse(requirements["network_required"])
            self.assertEqual(requirements["blocker_policy"], "standard_rca_after_3")
            self.assertEqual(task["promotion_evidence"], [])


if __name__ == "__main__":
    unittest.main()
