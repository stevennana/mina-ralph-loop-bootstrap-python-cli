import path from "node:path";
import {
  STATE_DIR,
  fileExists,
  readText,
  safeJsonParse,
  timestamp,
  writeText,
} from "./lib/task-utils.mjs";

const evaluationPath = path.join(STATE_DIR, "evaluation.json");
if (!fileExists(evaluationPath)) {
  throw new Error("No evaluation.json found.");
}

const evaluation = safeJsonParse(readText(evaluationPath), null);
if (!evaluation || typeof evaluation !== "object") {
  throw new Error("evaluation.json is invalid.");
}

const workerHandoffPath = path.join(STATE_DIR, "worker-handoff.txt");
const workerHandoff = fileExists(workerHandoffPath) ? readText(workerHandoffPath).trim() : "";
const deterministicPath = path.join(STATE_DIR, "deterministic-checks.json");
const deterministic = fileExists(deterministicPath)
  ? safeJsonParse(readText(deterministicPath), null)
  : null;

const summary = {
  generated_at: timestamp(),
  task_id: evaluation.task_id ?? null,
  authoritative_source: "evaluation",
  status: evaluation.status ?? "unknown",
  promotion_eligible: Boolean(evaluation.promotion_eligible),
  deterministic_pass: deterministic?.pass === true,
  execution_requirements: evaluation.execution_requirements ?? null,
  summary: evaluation.summary ?? "",
  missing_requirements: Array.isArray(evaluation.missing_requirements) ? evaluation.missing_requirements : [],
  satisfied_exit_criteria: Array.isArray(evaluation?.llm?.satisfied_exit_criteria)
    ? evaluation.llm.satisfied_exit_criteria
    : [],
  worker_handoff_summary: workerHandoff || "",
};

writeText(path.join(STATE_DIR, "current-cycle-summary.json"), `${JSON.stringify(summary, null, 2)}\n`);

const lines = [
  "**Result**",
  "",
  `Authoritative current-cycle decision: status=\`${summary.status}\` promotion=\`${String(summary.promotion_eligible)}\`.`,
];

if (summary.summary) {
  lines.push("", summary.summary);
}

if (summary.deterministic_pass === true) {
  lines.push("", "Deterministic checks for this cycle passed.");
} else if (summary.deterministic_pass === false) {
  lines.push("", "Deterministic checks for this cycle did not pass.");
}

if (summary.satisfied_exit_criteria.length > 0) {
  lines.push("", "Satisfied exit criteria:");
  for (const item of summary.satisfied_exit_criteria) {
    lines.push(`- ${item}`);
  }
}

if (summary.missing_requirements.length > 0) {
  lines.push("", "Remaining requirements:");
  for (const item of summary.missing_requirements) {
    lines.push(`- ${item}`);
  }
}

if (summary.worker_handoff_summary) {
  lines.push("", "Worker handoff from this cycle (context only, not authoritative for promotion):", summary.worker_handoff_summary);
}

writeText(path.join(STATE_DIR, "last-result.txt"), `${lines.join("\n")}\n`);
