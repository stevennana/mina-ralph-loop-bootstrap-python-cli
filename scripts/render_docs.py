#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from template_utils import copy_rendered_tree, load_answers, load_answers_json


def _slugify(text: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "-" for ch in text.strip())
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned.strip("-") or "item"


def _as_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            if not isinstance(item, str):
                raise ValueError("Structured list values must contain strings only.")
            result.append(item)
        return result
    if isinstance(value, str):
        return [value]
    raise ValueError("Expected a string or list of strings.")


def _render_bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- TODO"


def _render_numbered(items: list[str]) -> str:
    return "\n".join(f"{index}. {item}" for index, item in enumerate(items, start=1)) if items else "1. TODO"


def _json_block(payload: object) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _product_spec_doc(filename: str) -> str:
    return f"docs/product-specs/{filename}"


def _boolish(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "required"}
    return False


def _is_hardening_task(task: dict[str, object]) -> bool:
    title = str(task.get("title") or "").lower()
    task_id = str(task.get("id") or "").lower()
    prompt_docs = _as_list(task.get("prompt_docs"))
    return (
        "hardening" in title
        or "maintenance" in title
        or "hardening" in task_id
        or "maintenance" in task_id
        or any(doc in {"docs/QUALITY_SCORE.md", "docs/RELIABILITY.md", "docs/SECURITY.md"} for doc in prompt_docs)
    )


def _product_spec_docs(prompt_docs: list[str]) -> list[str]:
    return [doc for doc in prompt_docs if doc.startswith("docs/product-specs/")]


def _runtime_startup_required(feature_specs: list[dict[str, object]], answers_json: dict[str, object]) -> bool:
    if any(
        _boolish(answers_json.get(key))
        for key in (
            "RUNTIME_STARTUP_REQUIRED",
            "STARTUP_SMOKE_REQUIRED",
            "HAS_PERSISTENT_RUNTIME_STATE",
            "USES_PERSISTENT_RUNTIME_STATE",
        )
    ):
        return True

    for spec in feature_specs:
        commands = _as_list(spec.get("required_commands")) + _as_list(spec.get("required_checks"))
        if any(command == "make worker-smoke" for command in commands):
            return True
    return False


def _normalize_slice_size(value: object) -> str:
    normalized = str(value or "").strip().lower().replace("_", "-")
    if normalized in {"micro", "smallest", "smallest-safe", "tiny", "fine-grained", "fine"}:
        return "micro"
    if normalized in {"coarse", "broad", "large", "fewer"}:
        return "coarse"
    return "balanced"


def _task_capacity_per_day(slice_size: str) -> int:
    if slice_size == "micro":
        return 6
    if slice_size == "coarse":
        return 3
    return 5


def _parse_positive_int(value: object) -> int | None:
    if isinstance(value, int):
        return value if value > 0 else None
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.isdigit():
            parsed = int(stripped)
            return parsed if parsed > 0 else None
    return None


def _resolve_backlog_target(
    answers_json: dict[str, object],
    *,
    slice_size: str,
    feature_count: int,
) -> dict[str, int | str]:
    explicit_count = _parse_positive_int(answers_json.get("TARGET_EXEC_TASK_COUNT")) or _parse_positive_int(
        answers_json.get("TASK_COUNT_TARGET")
    )
    if explicit_count is not None:
        return {
            "label": f"{explicit_count} tasks",
            "minimum_total_tasks": explicit_count,
            "preferred_total_tasks": explicit_count,
            "maximum_total_tasks": explicit_count,
        }

    backlog_value = answers_json.get("BACKLOG_DEPTH")
    backlog_text = str(backlog_value or "").strip().lower()
    if not backlog_text:
        backlog_text = "10-15 tasks"

    numbers = [int(match) for match in re.findall(r"\d+", backlog_text)]
    if "next wave" in backlog_text or "next tranche" in backlog_text or backlog_text in {"wave", "short"}:
        minimum_total = max(3, min(5, feature_count + 1))
        preferred_total = max(4, minimum_total)
        maximum_total = max(preferred_total, 5)
        return {
            "label": "next wave",
            "minimum_total_tasks": minimum_total,
            "preferred_total_tasks": preferred_total,
            "maximum_total_tasks": maximum_total,
        }

    if "day" in backlog_text:
        if len(numbers) >= 2:
            minimum_days, maximum_days = numbers[0], numbers[1]
        elif numbers:
            minimum_days = maximum_days = numbers[0]
        else:
            minimum_days = maximum_days = 2
        per_day = _task_capacity_per_day(slice_size)
        minimum_total = max(1, minimum_days * per_day)
        maximum_total = max(minimum_total, maximum_days * per_day)
        preferred_total = max(minimum_total, (minimum_total + maximum_total) // 2)
        return {
            "label": backlog_text,
            "minimum_total_tasks": minimum_total,
            "preferred_total_tasks": preferred_total,
            "maximum_total_tasks": maximum_total,
        }

    if "hour" in backlog_text:
        if len(numbers) >= 2:
            minimum_hours, maximum_hours = numbers[0], numbers[1]
        elif numbers:
            minimum_hours = maximum_hours = numbers[0]
        else:
            minimum_hours = maximum_hours = 24
        per_day = _task_capacity_per_day(slice_size)
        minimum_total = max(1, round((minimum_hours / 8) * per_day))
        maximum_total = max(minimum_total, round((maximum_hours / 8) * per_day))
        preferred_total = max(minimum_total, (minimum_total + maximum_total) // 2)
        return {
            "label": backlog_text,
            "minimum_total_tasks": minimum_total,
            "preferred_total_tasks": preferred_total,
            "maximum_total_tasks": maximum_total,
        }

    if "task" in backlog_text and len(numbers) >= 2:
        minimum_total, maximum_total = numbers[0], numbers[1]
        preferred_total = max(minimum_total, (minimum_total + maximum_total) // 2)
        return {
            "label": backlog_text,
            "minimum_total_tasks": minimum_total,
            "preferred_total_tasks": preferred_total,
            "maximum_total_tasks": maximum_total,
        }

    if "task" in backlog_text and len(numbers) == 1:
        total = numbers[0]
        return {
            "label": backlog_text,
            "minimum_total_tasks": total,
            "preferred_total_tasks": total,
            "maximum_total_tasks": total,
        }

    return {
        "label": "10-15 tasks",
        "minimum_total_tasks": 10,
        "preferred_total_tasks": 12,
        "maximum_total_tasks": 15,
    }


def _spec_text(spec: dict[str, object]) -> str:
    parts = [
        str(spec.get("title") or ""),
        str(spec.get("goal") or ""),
        str(spec.get("trigger") or ""),
        str(spec.get("scope") or ""),
        *_as_list(spec.get("behavior_bullets")),
        *_as_list(spec.get("validation_bullets")),
        *_as_list(spec.get("required_commands")),
        *_as_list(spec.get("required_checks")),
        *_as_list(spec.get("required_files")),
    ]
    return " ".join(parts).lower()


def _build_spec_profile(spec: dict[str, object]) -> dict[str, object]:
    behavior = _as_list(spec.get("behavior_bullets"))
    validation = _as_list(spec.get("validation_bullets"))
    required_commands = _as_list(spec.get("required_commands"))
    required_checks = _as_list(spec.get("required_checks"))
    required_files = _as_list(spec.get("required_files"))
    text = _spec_text(spec)
    external_keywords = (
        "oauth",
        "auth",
        "invite",
        "email",
        "ai",
        "upload",
        "media",
        "search",
        "retrieval",
        "third-party",
        "third party",
        "integration",
        "provider",
        "billing",
        "payment",
        "webhook",
        "sync",
    )
    external_dependency = any(keyword in text for keyword in external_keywords)
    requires_startup_smoke = any(command == "make worker-smoke" for command in (required_commands + required_checks))
    needs_foundation = external_dependency or requires_startup_smoke or bool(required_files) or len(behavior) >= 4
    needs_coverage_followup = (
        external_dependency
        or requires_startup_smoke
        or len(validation) >= 2
        or any("test-e2e" in command or "tests/e2e" in command for command in (required_commands + required_checks))
    )
    followup_capacity = 0
    if len(behavior) >= 2:
        followup_capacity += 1
    if len(behavior) >= 4 or len(validation) >= 3:
        followup_capacity += 1
    if len(behavior) >= 6 or len(validation) >= 5:
        followup_capacity += 1

    return {
        "behavior": behavior,
        "validation": validation,
        "required_commands": required_commands,
        "required_checks": required_checks,
        "required_files": required_files,
        "external_dependency": external_dependency,
        "requires_startup_smoke": requires_startup_smoke,
        "needs_foundation": needs_foundation,
        "needs_coverage_followup": needs_coverage_followup,
        "followup_capacity": followup_capacity,
        "complexity_score": len(behavior) * 2
        + len(validation)
        + (2 if external_dependency else 0)
        + (1 if requires_startup_smoke else 0)
        + (1 if required_files else 0),
    }


def _default_execution_requirements() -> dict[str, object]:
    return {
        "worker_sandbox": "workspace-write",
        "evaluator_sandbox": "read-only",
        "network_required": False,
        "blocker_policy": "standard_rca_after_3",
    }


def _default_promotion_evidence(task_id: str, producer_command: str) -> list[dict[str, object]]:
    return [
        {
            "id": f"{task_id}-live-proof",
            "kind": "command_artifact",
            "producer_command": producer_command,
            "manifest_path": f"state/artifacts/live-proofs/{task_id}/latest/manifest.json",
            "freshness": "current_cycle",
        }
    ]


def _merge_promotion_evidence(
    explicit: object | None,
    *,
    task_id: str,
    required_commands: list[str],
    needs_live_proof: bool = False,
) -> list[dict[str, object]]:
    evidence: list[dict[str, object]] = []
    if isinstance(explicit, list):
        for index, item in enumerate(explicit, start=1):
            if not isinstance(item, dict):
                continue
            producer_command = str(item.get("producer_command") or "").strip()
            manifest_path = str(item.get("manifest_path") or "").strip()
            if not producer_command or not manifest_path:
                continue
            entry: dict[str, object] = {
                "id": str(item.get("id") or f"evidence-{index}"),
                "kind": str(item.get("kind") or "command_artifact"),
                "producer_command": producer_command,
                "manifest_path": manifest_path,
                "freshness": str(item.get("freshness") or "current_cycle"),
            }
            if str(item.get("log_path") or "").strip():
                entry["log_path"] = str(item["log_path"]).strip()
            if str(item.get("required_event") or "").strip():
                entry["required_event"] = str(item["required_event"]).strip()
            evidence.append(entry)

    if evidence or not needs_live_proof or not required_commands:
        return evidence

    return _default_promotion_evidence(task_id, required_commands[0])


def _merge_execution_requirements(
    explicit: object | None,
    *,
    needs_network_lane: bool = False,
) -> dict[str, object]:
    requirements = dict(_default_execution_requirements())
    if isinstance(explicit, dict):
        requirements.update(
            {
                key: explicit[key]
                for key in ("worker_sandbox", "evaluator_sandbox", "network_required", "blocker_policy")
                if key in explicit
            }
        )
    if needs_network_lane:
        requirements.update(
            {
                "worker_sandbox": "danger-full-access",
                "network_required": True,
                "blocker_policy": "external_runtime_rca_after_3",
            }
        )
    return requirements


def _max_tasks_for_profile(profile: dict[str, object], slice_size: str) -> int:
    max_count = 1 + int(bool(profile["needs_foundation"])) + int(bool(profile["needs_coverage_followup"])) + int(
        profile["followup_capacity"]
    )
    if slice_size == "coarse":
        return min(max_count, 3)
    if slice_size == "micro":
        return min(max_count, 6)
    return min(max_count, 5)


def _initial_task_count_for_profile(profile: dict[str, object], slice_size: str) -> int:
    max_count = _max_tasks_for_profile(profile, slice_size)
    if slice_size == "coarse":
        count = 1 + int(profile["complexity_score"] >= 8)
    elif slice_size == "micro":
        count = 3 + int(profile["complexity_score"] >= 9) + int(profile["complexity_score"] >= 13)
    else:
        count = 2 + int(profile["complexity_score"] >= 9)
    return max(1, min(count, max_count))


def _distribute_task_counts(
    profiles: list[dict[str, object]],
    *,
    slice_size: str,
    preferred_total_tasks: int,
) -> list[int]:
    counts = [_initial_task_count_for_profile(profile, slice_size) for profile in profiles]
    total_non_hardening = sum(counts)
    if total_non_hardening >= preferred_total_tasks:
        return counts

    while total_non_hardening < preferred_total_tasks:
        candidate_index = None
        candidate_rank: tuple[int, int, int] | None = None
        for index, profile in enumerate(profiles):
            max_count = _max_tasks_for_profile(profile, slice_size)
            remaining_capacity = max_count - counts[index]
            if remaining_capacity <= 0:
                continue
            rank = (
                int(profile["complexity_score"]),
                remaining_capacity,
                -counts[index],
            )
            if candidate_rank is None or rank > candidate_rank:
                candidate_rank = rank
                candidate_index = index
        if candidate_index is None:
            break
        counts[candidate_index] += 1
        total_non_hardening += 1

    return counts


def _chunk_items(items: list[str], chunk_count: int) -> list[list[str]]:
    if chunk_count <= 0:
        return []
    if not items:
        return [[] for _ in range(chunk_count)]

    chunks: list[list[str]] = []
    start = 0
    total = len(items)
    for index in range(chunk_count):
        remaining_items = total - start
        remaining_chunks = chunk_count - index
        size = max(1, remaining_items // remaining_chunks)
        if remaining_items % remaining_chunks:
            size += 1
        end = min(total, start + size)
        chunks.append(items[start:end])
        start = end
    while len(chunks) < chunk_count:
        chunks.append([])
    return chunks


def _phase_slug(kind: str, followup_index: int | None = None) -> str:
    if kind == "foundation":
        return "foundation"
    if kind == "primary":
        return "first-vertical-slice"
    if kind == "coverage":
        return "acceptance-and-edge-coverage"
    if followup_index is None:
        return "follow-up-slice"
    return f"follow-up-slice-{followup_index}"


def _phase_title(spec_title: str, *, kind: str, followup_index: int | None = None, single_task: bool) -> str:
    if single_task and kind == "primary":
        return spec_title
    if kind == "foundation":
        label = "Foundation"
    elif kind == "primary":
        label = "First Vertical Slice"
    elif kind == "coverage":
        label = "Acceptance And Edge Coverage"
    else:
        label = f"Follow-Up Slice {followup_index or 1}"
    return f"{spec_title}: {label}"


def _default_scope_bullet(spec_title: str, *, kind: str, followup_index: int | None = None) -> str:
    feature_name = spec_title.lower()
    if kind == "foundation":
        return f"establish the minimum implementation and repo wiring needed for the first {feature_name} slice"
    if kind == "coverage":
        return f"close the remaining acceptance and edge-case gaps for {feature_name}"
    if kind == "primary":
        return f"ship the first promotion-ready {feature_name} path"
    return f"ship the next scoped {feature_name} increment without broadening into unrelated feature work"


def _default_exit_criteria(spec_title: str, *, kind: str) -> list[str]:
    feature_name = spec_title.lower()
    if kind == "foundation":
        return [
            f"The minimum enabling work for the first {feature_name} slice is in place.",
            "The task's required checks pass.",
        ]
    if kind == "coverage":
        return [
            f"The remaining acceptance-relevant gaps for {feature_name} are closed or made explicit.",
            "The task's required checks pass.",
        ]
    return [
        f"The scoped {feature_name} behavior works in substance.",
        "The task's required checks pass.",
    ]


def _derive_tasks_for_spec(
    filename: str,
    spec: dict[str, object],
    profile: dict[str, object],
    *,
    count: int,
    project_name: str,
) -> list[dict[str, object]]:
    title = str(spec.get("title") or "Feature slice")
    slug = str(spec.get("slug") or _slugify(title))
    behavior = list(profile["behavior"])
    validation = list(profile["validation"])
    prompt_docs = [
        "AGENTS.md",
        "ARCHITECTURE.md",
        "docs/CLI_SURFACE.md",
        _product_spec_doc(filename),
    ]
    required_commands = list(profile["required_commands"]) or ["make verify"]
    required_checks = list(profile["required_checks"]) or list(required_commands)
    required_files = list(profile["required_files"])
    out_of_scope = _as_list(spec.get("out_of_scope_bullets")) or [
        "unrelated feature fronts",
        "future product expansion beyond this feature",
    ]
    human_review_triggers = _as_list(spec.get("human_review_triggers")) or [
        "The task broadens into unrelated feature work.",
        "The deterministic checks do not actually prove the claimed behavior.",
    ]
    base_goal = str(spec.get("goal") or f"Implement {title} for {project_name}.")

    single_task = count == 1
    include_foundation = count >= 3 and bool(profile["needs_foundation"])
    include_coverage = count >= 2 and bool(profile["needs_coverage_followup"])

    phase_plan: list[tuple[str, int | None]] = []
    if include_foundation:
        phase_plan.append(("foundation", None))
    phase_plan.append(("primary", None))
    remaining_slots = count - len(phase_plan)
    if include_coverage:
        remaining_slots -= 1
    followup_slots = max(0, remaining_slots)
    for followup_index in range(1, followup_slots + 1):
        phase_plan.append(("followup", followup_index))
    if include_coverage:
        phase_plan.append(("coverage", None))

    behavior_phase_indexes = [index for index, (kind, _) in enumerate(phase_plan) if kind in {"primary", "followup"}]
    behavior_chunks = _chunk_items(behavior, len(behavior_phase_indexes))
    validation_phase_indexes = [index for index, (kind, _) in enumerate(phase_plan) if kind != "foundation"]
    validation_chunks = _chunk_items(validation, len(validation_phase_indexes))

    tasks: list[dict[str, object]] = []
    behavior_chunk_index = 0
    validation_chunk_index = 0
    for phase_index, (kind, followup_index) in enumerate(phase_plan):
        title_for_phase = _phase_title(title, kind=kind, followup_index=followup_index, single_task=single_task)
        phase_slug = slug if single_task and kind == "primary" else f"{slug}-{_phase_slug(kind, followup_index)}"
        needs_network_lane = bool(profile["external_dependency"]) and (kind == "coverage" or single_task)
        execution_requirements = _merge_execution_requirements(
            spec.get("execution_requirements"),
            needs_network_lane=needs_network_lane,
        )
        promotion_evidence = _merge_promotion_evidence(
            spec.get("promotion_evidence"),
            task_id=phase_slug,
            required_commands=required_commands,
            needs_live_proof=needs_network_lane,
        )

        if kind in {"primary", "followup"}:
            scope_bullets = behavior_chunks[behavior_chunk_index]
            behavior_chunk_index += 1
        elif kind == "foundation":
            scope_bullets = [
                _default_scope_bullet(title, kind="foundation"),
                f"prepare the repo contracts, docs, and checks needed to deliver the first {title.lower()} path safely",
            ]
        else:
            scope_bullets = [
                _default_scope_bullet(title, kind="coverage"),
                f"make the remaining {title.lower()} acceptance criteria and edge handling explicit in implementation and docs",
            ]

        if not scope_bullets:
            scope_bullets = [_default_scope_bullet(title, kind=kind, followup_index=followup_index)]

        if kind != "foundation":
            exit_criteria = validation_chunks[validation_chunk_index]
            validation_chunk_index += 1
        else:
            exit_criteria = []

        if not exit_criteria:
            exit_criteria = _default_exit_criteria(title, kind=kind)
        elif "The task's required checks pass." not in exit_criteria:
            exit_criteria = [*exit_criteria, "The task's required checks pass."]

        implementation_notes = _as_list(spec.get("implementation_notes_bullets"))
        if kind == "coverage" and profile["external_dependency"]:
            implementation_notes = [
                *implementation_notes,
                f"Require the relevant end-to-end scenario for {title.lower()} before promotion.",
            ]

        if kind == "foundation":
            objective = f"Prepare the minimum foundation needed to deliver the first {title.lower()} slice without broadening into the full feature."
            summary = f"lay the foundation for the first {title.lower()} slice"
        elif kind == "primary" and single_task:
            objective = base_goal
            summary = str(spec.get("summary") or str(spec.get("scope") or base_goal)).strip()
        elif kind == "primary":
            objective = f"Implement the first promotion-ready {title.lower()} slice."
            summary = f"ship the first promotion-ready {title.lower()} path"
        elif kind == "coverage":
            objective = f"Close the remaining {title.lower()} acceptance, edge-case, and coverage gaps."
            summary = f"close acceptance and edge-case gaps for {title.lower()}"
        else:
            objective = f"Implement the next scoped {title.lower()} increment without broadening into unrelated feature work."
            summary = f"ship the next scoped {title.lower()} increment"

        phase_out_of_scope = list(out_of_scope)
        if count > 1:
            phase_out_of_scope.append(f"other planned {title.lower()} slices outside this task")

        evaluator_notes = _as_list(spec.get("evaluator_notes")) or [
            f"Promote only when the {title.lower()} behavior works end-to-end in substance.",
        ]
        if kind == "foundation":
            evaluator_notes = [
                f"Promote only when the minimum enabling work for {title.lower()} is actually in place.",
                *evaluator_notes,
            ]
        elif kind == "coverage":
            evaluator_notes = [
                f"Promote only when the remaining acceptance and edge-case gaps for {title.lower()} are closed in substance.",
                *evaluator_notes,
            ]

        tasks.append(
            {
                "phase_slug": phase_slug,
                "title": title_for_phase,
                "prompt_docs": prompt_docs,
                "execution_requirements": execution_requirements,
                "promotion_evidence": promotion_evidence,
                "required_commands": required_commands,
                "required_files": required_files,
                "human_review_triggers": human_review_triggers,
                "objective": objective,
                "scope_bullets": scope_bullets,
                "out_of_scope_bullets": phase_out_of_scope,
                "exit_criteria": exit_criteria,
                "required_checks": required_checks,
                "evaluator_notes": evaluator_notes,
                "summary": summary,
                "why_now": str(spec.get("why_now") or ""),
                "implementation_notes_bullets": implementation_notes,
            }
        )
    return tasks


def derive_exec_tasks_from_feature_specs(
    feature_specs: list[dict[str, object]],
    project_name: str,
    *,
    runtime_startup_required: bool,
    slice_size: str = "balanced",
    preferred_total_tasks: int | None = None,
) -> list[dict[str, object]]:
    derived: list[dict[str, object]] = []
    ordered_specs: list[tuple[str, dict[str, object]]] = []
    for spec in feature_specs:
        title = str(spec.get("title", "")).strip()
        slug = str(spec.get("slug") or _slugify(title))
        filename = str(spec.get("filename") or f"{slug}.md")
        ordered_specs.append((filename, spec))

    profiles = [_build_spec_profile(spec) for _, spec in ordered_specs]
    target_non_hardening_tasks = preferred_total_tasks if preferred_total_tasks is not None else sum(
        _initial_task_count_for_profile(profile, slice_size) for profile in profiles
    )
    counts = _distribute_task_counts(
        profiles,
        slice_size=slice_size,
        preferred_total_tasks=target_non_hardening_tasks,
    )

    non_hardening_tasks: list[dict[str, object]] = []
    for (filename, spec), profile, count in zip(ordered_specs, profiles, counts, strict=False):
        non_hardening_tasks.extend(
            _derive_tasks_for_spec(
                filename,
                spec,
                profile,
                count=count,
                project_name=project_name,
            )
        )

    hardening_order = 10 + len(non_hardening_tasks) + 1
    hardening_id = f"{hardening_order:03d}-hardening-and-maintenance"
    for index, task in enumerate(non_hardening_tasks, start=1):
        order = 10 + index
        task_id = f"{order:03d}-{task.pop('phase_slug')}"
        next_task_on_success = (
            f"{order + 1:03d}-{non_hardening_tasks[index].get('phase_slug')}" if index < len(non_hardening_tasks) else hardening_id
        )
        derived.append(
            {
                "id": task_id,
                "order": order,
                "status": "active" if index == 1 else "queued",
                "next_task_on_success": next_task_on_success,
                **task,
            }
        )

    hardening_required_commands = ["make verify"]
    hardening_required_checks = ["make verify"]
    hardening_exit_criteria = [
        "`make verify` passes.",
        "Reliability and security docs match the implementation.",
        "Remaining debt is explicit.",
    ]
    hardening_evaluator_notes = [
        "Promote only when the repository is ready for longer unattended Ralph-loop runs under the current task contract.",
    ]
    if runtime_startup_required:
        hardening_required_commands.append("make worker-smoke")
        hardening_required_checks.append("make worker-smoke")
        hardening_exit_criteria.insert(1, "`make worker-smoke` passes.")
        hardening_evaluator_notes.append(
            "Do not promote if the production-style startup path still fails for normal repo reasons such as missing runtime preparation."
        )

    derived.append(
        {
            "id": hardening_id,
            "title": "Hardening and maintenance",
            "order": hardening_order,
            "status": "queued",
            "next_task_on_success": None,
            "execution_requirements": _default_execution_requirements(),
            "promotion_evidence": [],
            "prompt_docs": [
                "AGENTS.md",
                "ARCHITECTURE.md",
                "docs/QUALITY_SCORE.md",
                "docs/RELIABILITY.md",
                "docs/SECURITY.md",
            ],
            "required_commands": hardening_required_commands,
            "required_files": ["scripts/ralph/README.md"],
            "human_review_triggers": [
                "The task expands into broad feature work.",
                "Reliability or security docs do not match the actual code.",
            ],
            "objective": f"Close the reliability, security, and automation gaps after the {project_name} feature slices land.",
            "scope_bullets": [
                "reconcile docs and implementation drift",
                "keep the deterministic checks healthy",
                "record remaining debt explicitly",
            ],
            "out_of_scope_bullets": [
                "major new product features",
                "unrelated infrastructure expansion",
            ],
            "exit_criteria": hardening_exit_criteria,
            "required_checks": hardening_required_checks,
            "evaluator_notes": hardening_evaluator_notes,
            "summary": "reconcile reliability, security, and loop guidance after the feature slices land",
        }
    )
    return derived


def validate_exec_tasks(feature_specs: list[dict[str, object]], exec_tasks: list[dict[str, object]]) -> None:
    if not feature_specs:
        return

    spec_doc_map: dict[str, str] = {}
    for spec in feature_specs:
        title = str(spec.get("title", "")).strip()
        slug = str(spec.get("slug") or _slugify(title))
        filename = str(spec.get("filename") or f"{slug}.md")
        spec_doc_map[_product_spec_doc(filename)] = title or filename

    if len(exec_tasks) < len(feature_specs) + 1:
        raise ValueError(
            "EXEC_TASKS is too small for the feature set. Provide at least one task per feature spec plus a separate hardening/maintenance task."
        )

    if not any(_is_hardening_task(task) for task in exec_tasks):
        raise ValueError("EXEC_TASKS must include a separate hardening/maintenance task.")

    covered_specs: set[str] = set()
    for task in exec_tasks:
        prompt_docs = _as_list(task.get("prompt_docs"))
        product_docs = _product_spec_docs(prompt_docs)
        if _is_hardening_task(task):
            continue
        if len(product_docs) != 1:
            raise ValueError(
                f"Task '{task.get('id') or task.get('title')}' must reference exactly one product spec in prompt_docs to keep the slice narrow."
            )
        covered_specs.add(product_docs[0])

    missing = [spec_doc_map[doc] for doc in spec_doc_map if doc not in covered_specs]
    if missing:
        raise ValueError(
            "EXEC_TASKS does not cover every feature spec. Missing task coverage for: " + ", ".join(missing)
        )


def render_structured_feature_artifacts(repo_root: Path, answers_json: dict[str, object], *, overwrite: bool) -> None:
    feature_specs = answers_json.get("FEATURE_SPECS")
    exec_tasks = answers_json.get("EXEC_TASKS")

    if feature_specs is None and exec_tasks is None:
        return

    docs_root = repo_root / "docs"
    specs_dir = docs_root / "product-specs"
    active_dir = docs_root / "exec-plans" / "active"

    if feature_specs is not None:
        if not isinstance(feature_specs, list):
            raise ValueError("FEATURE_SPECS must be a list when provided.")

        spec_rows: list[str] = []
        feature_filenames: set[str] = set()
        for spec in feature_specs:
            if not isinstance(spec, dict):
                raise ValueError("Each FEATURE_SPECS entry must be an object.")
            title = str(spec.get("title", "")).strip()
            if not title:
                raise ValueError("Each FEATURE_SPECS entry must include a non-empty title.")
            slug = str(spec.get("slug") or _slugify(title))
            filename = str(spec.get("filename") or f"{slug}.md")
            feature_filenames.add(filename)
            status = str(spec.get("status") or "confirmed")
            scope = str(spec.get("scope") or title)
            goal = str(spec.get("goal") or "")
            trigger = str(spec.get("trigger") or "")
            behavior = _as_list(spec.get("behavior_bullets"))
            validation = _as_list(spec.get("validation_bullets"))
            spec_rows.append(f"| `{filename}` | {status} | {scope} |")

            if not goal or not trigger or not behavior or not validation:
                raise ValueError(
                    f"Feature spec '{title}' must include goal, trigger, behavior_bullets, and validation_bullets."
                )

            spec_path = specs_dir / filename
            if spec_path.exists() and not overwrite:
                continue

            spec_path.parent.mkdir(parents=True, exist_ok=True)
            spec_path.write_text(
                "\n".join(
                    [
                        f"# {title}",
                        "",
                        "## Goal",
                        goal,
                        "",
                        "## Trigger / Entry",
                        trigger,
                        "",
                        "## User-Visible Behavior",
                        _render_bullets(behavior),
                        "",
                        "## Validation",
                        _render_bullets(validation),
                        "",
                    ]
                ),
                encoding="utf-8",
            )

        generic_core_flow_path = specs_dir / "core-flow.md"
        if feature_filenames and "core-flow.md" not in feature_filenames and generic_core_flow_path.exists():
            generic_core_flow_path.unlink()

        if feature_specs:
            index_path = specs_dir / "index.md"
            index_path.write_text(
                "\n".join(
                    [
                        "# Product Specs Index",
                        "",
                        "## Purpose",
                        "This directory contains user-facing behavior specs.",
                        "If a UI or API behavior is visible to users, it should be defined here before implementation drifts.",
                        "",
                        "## Current Spec Set",
                        "| Spec | Status | Scope |",
                        "|---|---|---|",
                        *spec_rows,
                        "",
                        "## Editing Rule",
                        "When product behavior changes:",
                        "1. update the relevant spec",
                        "2. update the affected design or architecture docs if needed",
                        "3. only then adjust implementation plans",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

    feature_spec_objects = feature_specs if isinstance(feature_specs, list) else []

    runtime_startup_required = _runtime_startup_required(feature_spec_objects, answers_json)
    slice_size = _normalize_slice_size(answers_json.get("SLICE_SIZE"))
    backlog_target = _resolve_backlog_target(
        answers_json,
        slice_size=slice_size,
        feature_count=len(feature_spec_objects),
    )

    if exec_tasks is None and feature_spec_objects:
        exec_tasks = derive_exec_tasks_from_feature_specs(
            feature_spec_objects,
            repo_root.name,
            runtime_startup_required=runtime_startup_required,
            slice_size=slice_size,
            preferred_total_tasks=max(1, int(backlog_target["preferred_total_tasks"]) - 1),
        )

    if exec_tasks is not None:
        if not isinstance(exec_tasks, list):
            raise ValueError("EXEC_TASKS must be a list when provided.")
        validate_exec_tasks(feature_spec_objects, exec_tasks)

        sequence_lines: list[str] = []
        # The baseline templates always create generic 011/012 task files.
        # When the caller provides a structured task queue, those generic
        # contracts should not remain eligible for loop selection.
        for baseline_name in ("011-first-vertical-slice.md", "012-hardening-and-maintenance.md"):
            baseline_path = active_dir / baseline_name
            if baseline_path.exists():
                baseline_path.unlink()

        for task in exec_tasks:
            if not isinstance(task, dict):
                raise ValueError("Each EXEC_TASKS entry must be an object.")

            task_id = str(task.get("id", "")).strip()
            title = str(task.get("title", "")).strip()
            if not task_id or not title:
                raise ValueError("Each EXEC_TASKS entry must include non-empty id and title.")

            filename = str(task.get("filename") or f"{task_id}.md")
            objective = str(task.get("objective") or "")
            why_now = str(task.get("why_now") or "")
            summary = str(task.get("summary") or objective)
            sequence_lines.append(f"{len(sequence_lines) + 1}. `{filename}` -> {summary}")
            evaluator_notes = _as_list(task.get("evaluator_notes"))
            prompt_docs = _as_list(task.get("prompt_docs"))
            required_commands = _as_list(task.get("required_commands"))
            required_files = _as_list(task.get("required_files"))
            human_review_triggers = _as_list(task.get("human_review_triggers"))
            execution_requirements = _merge_execution_requirements(task.get("execution_requirements"))
            promotion_evidence = _merge_promotion_evidence(
                task.get("promotion_evidence"),
                task_id=task_id,
                required_commands=required_commands,
            )
            scope = _as_list(task.get("scope_bullets"))
            out_of_scope = _as_list(task.get("out_of_scope_bullets"))
            exit_criteria = _as_list(task.get("exit_criteria"))
            required_checks = _as_list(task.get("required_checks"))
            dependencies = _as_list(task.get("dependencies_bullets"))
            implementation_notes = _as_list(task.get("implementation_notes_bullets"))
            docs_to_update = _as_list(task.get("docs_to_update"))

            if not objective or not prompt_docs or not required_commands or not scope or not exit_criteria:
                raise ValueError(
                    f"Exec task '{task_id}' must include objective, prompt_docs, required_commands, scope_bullets, and exit_criteria."
                )

            order = int(task.get("order", 0))
            taskmeta = {
                "id": task_id,
                "title": title,
                "order": order,
                "status": str(task.get("status") or "queued"),
                "next_task_on_success": task.get("next_task_on_success"),
                "prompt_docs": prompt_docs,
                "execution_requirements": execution_requirements,
                "promotion_evidence": promotion_evidence,
                "required_commands": required_commands,
                "required_files": required_files,
                "human_review_triggers": human_review_triggers,
            }

            task_path = active_dir / filename
            if task_path.exists() and not overwrite:
                continue

            task_path.parent.mkdir(parents=True, exist_ok=True)
            body_lines = [
                f"# {title}",
                "",
                "```json taskmeta",
                _json_block(taskmeta),
                "```",
                "",
                "## Objective",
                "",
                objective,
                "",
            ]
            if why_now:
                body_lines.extend(
                    [
                        "## Why now",
                        "",
                        why_now,
                        "",
                    ]
                )
            if dependencies:
                body_lines.extend(
                    [
                        "## Dependencies",
                        "",
                        _render_bullets(dependencies),
                        "",
                    ]
                )
            body_lines.extend(
                [
                    "## Scope",
                    "",
                    _render_bullets(scope),
                    "",
                    "## Out of scope",
                    "",
                    _render_bullets(out_of_scope),
                    "",
                    "## Exit criteria",
                    "",
                    _render_numbered(exit_criteria),
                    "",
                    "## Required checks",
                    "",
                    _render_bullets(required_checks or required_commands),
                    "",
                ]
            )
            if implementation_notes:
                body_lines.extend(
                    [
                        "## Implementation notes",
                        "",
                        _render_bullets(implementation_notes),
                        "",
                    ]
                )
            if docs_to_update:
                body_lines.extend(
                    [
                        "## Docs to update",
                        "",
                        _render_bullets(docs_to_update),
                        "",
                    ]
                )
            body_lines.extend(
                [
                    "## Evaluator notes",
                    "",
                    "\n".join(evaluator_notes)
                    if evaluator_notes
                    else "Promote only when the task is substantively complete and the required checks prove the claimed behavior.",
                    "",
                    "## Progress log",
                    "",
                    "- Start here. Append timestamped progress notes as work lands.",
                    "- Note when existing partial implementations were found and reused instead of replaced.",
                    "",
                ]
            )
            task_path.write_text(
                "\n".join(body_lines),
                encoding="utf-8",
            )
        if exec_tasks:
            active_index_path = active_dir / "index.md"
            active_index_path.write_text(
                "\n".join(
                    [
                        "# Ralph Loop Task Queue",
                        "",
                        f"This queue is the task-level promotion source of truth for {repo_root.name}.",
                        "",
                        "Only task files in this directory that contain a `taskmeta` JSON block are eligible for automatic selection, evaluation, and promotion.",
                        "Queue depth is intentionally derived from the selected slice-size and backlog-depth planning controls when the planner provides them.",
                        "",
                        "## Current recommended sequence",
                        *sequence_lines,
                        "",
                        "## Operating rule",
                        "",
                        "A task may be promoted only when all of the following are true:",
                        "",
                        "- deterministic checks pass",
                        "- the evaluator marks the task as `done`",
                        "- the evaluator recommends promotion",
                        "- the task metadata declares a `next_task_on_success`, or explicitly declares that the queue ends here",
                        "",
                        "## When this queue ends",
                        "",
                        "When the active sequence is exhausted, do not continue with ad hoc prompts alone.",
                        "Update the relevant product specs and design docs first, then seed the next active queue for the next feature wave.",
                        "",
                    ]
                ),
                encoding="utf-8",
            )


def main() -> int:
    parser = argparse.ArgumentParser(description="Render root/doc templates into a target repo.")
    parser.add_argument("--answers", required=True, help="Path to the bootstrap answers JSON.")
    parser.add_argument("--repo-root", required=True, help="Target repository root.")
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="Leave unresolved {{PLACEHOLDER}} values in place instead of failing.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files instead of skipping them.",
    )
    args = parser.parse_args()

    skill_root = Path(__file__).resolve().parent.parent
    repo_root = Path(args.repo_root).expanduser().resolve()
    answers_path = Path(args.answers).expanduser().resolve()
    answers = load_answers(answers_path)
    answers_json = load_answers_json(answers_path)

    roots = [
        (skill_root / "assets" / "templates" / "root", repo_root),
        (skill_root / "assets" / "templates" / "docs", repo_root / "docs"),
    ]

    all_missing: list[str] = []
    for source, destination in roots:
        if not source.exists():
            continue
        all_missing.extend(
            copy_rendered_tree(
                source,
                destination,
                answers,
                allow_missing=args.allow_missing,
                overwrite=args.overwrite,
            )
        )

    all_missing = sorted(set(all_missing))
    if all_missing and not args.allow_missing:
        print("Missing placeholders:", ", ".join(all_missing), file=sys.stderr)
        return 1

    render_structured_feature_artifacts(repo_root, answers_json, overwrite=args.overwrite)

    print(f"Rendered docs into {repo_root}")
    if all_missing:
        print("Unresolved placeholders left in place:", ", ".join(all_missing))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
