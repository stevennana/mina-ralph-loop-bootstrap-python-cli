import path from "node:path";
import { execSync, spawnSync } from "node:child_process";
import {
  GENERATED_DIR,
  STATE_DIR,
  evaluatePromotionEvidence,
  ensureDir,
  findTaskDoc,
  readCurrentTaskId,
  readText,
  safeJsonParse,
  timestamp,
  writeText,
  fileExists,
  normalizeExecutionRequirements,
} from "./lib/task-utils.mjs";

function deriveExternalRuntimeBlocker(commandResults) {
  for (const result of commandResults) {
    const combinedOutput = `${result?.output ?? ""}\n${result?.error ?? ""}`;
    const lines = combinedOutput.split("\n").map((line) => line.trim()).filter(Boolean);

    for (const line of lines) {
      const structuredMatch = line.match(
        /EXTERNAL_RUNTIME_BLOCKED(?:\s+kind=(\S+))?(?:\s+endpoint=(\S+))?(?:\s+reason=(.+))?/i,
      );
      if (structuredMatch) {
        return {
          kind: structuredMatch[1] || "external_runtime_blocked",
          endpoint: structuredMatch[2] || "unknown-endpoint",
          reason: (structuredMatch[3] || "blocked by the current runtime").trim(),
          source_command: result.command,
        };
      }

      const reachableMatch = line.match(
        /configured endpoint ([^\s]+) is unreachable from this shell runtime: (.+)/i,
      );
      if (reachableMatch) {
        return {
          kind: "real_llm_endpoint_unreachable",
          endpoint: reachableMatch[1],
          reason: reachableMatch[2].trim(),
          source_command: result.command,
        };
      }

      const genericUnreachableMatch = line.match(
        /([a-z0-9.-]+(?::\d+)?) is unreachable from (?:this|the current) shell runtime: (.+)/i,
      );
      if (genericUnreachableMatch) {
        return {
          kind: "external_endpoint_unreachable",
          endpoint: genericUnreachableMatch[1],
          reason: genericUnreachableMatch[2].trim(),
          source_command: result.command,
        };
      }
    }
  }
  return null;
}

function runShellCommand(command) {
  try {
    const output = execSync(command, {
      cwd: process.cwd(),
      encoding: "utf8",
      stdio: ["ignore", "pipe", "pipe"],
    });
    return {
      command,
      ok: true,
      output,
    };
  } catch (error) {
    return {
      command,
      ok: false,
      output: error.stdout?.toString?.() ?? "",
      error: error.stderr?.toString?.() ?? error.message,
    };
  }
}

ensureDir(STATE_DIR);
ensureDir(GENERATED_DIR);
const evaluationStartedAt = timestamp();

const taskId = readCurrentTaskId();
if (!taskId || taskId === "NONE") {
  writeText(
    path.join(STATE_DIR, "evaluation.json"),
    JSON.stringify({ status: "blocked", reason: "No active task configured." }, null, 2),
  );
  process.exit(0);
}

const task = findTaskDoc(taskId);
if (!task) {
  writeText(
    path.join(STATE_DIR, "evaluation.json"),
    JSON.stringify({ status: "blocked", reason: `Task '${taskId}' not found.` }, null, 2),
  );
  process.exit(0);
}

const executionRequirements = normalizeExecutionRequirements(task.meta);

const commandResults = [];
for (const command of task.meta.required_commands ?? ["make verify"]) {
  commandResults.push(runShellCommand(command));
}

const missingFiles = [];
for (const relativePath of task.meta.required_files ?? []) {
  const absolutePath = path.join(process.cwd(), relativePath);
  if (!fileExists(absolutePath)) {
    missingFiles.push(relativePath);
  }
}

const deterministic = {
  checked_at: timestamp(),
  task_id: task.id,
  commands: commandResults,
  missing_files: missingFiles,
  pass: commandResults.every((result) => result.ok) && missingFiles.length === 0,
};

writeText(path.join(STATE_DIR, "deterministic-checks.json"), JSON.stringify(deterministic, null, 2));

const externalBlocker = deriveExternalRuntimeBlocker(commandResults);
const promotionEvidence = evaluatePromotionEvidence(task.meta, {
  currentCycleStartedAt: evaluationStartedAt,
});
const promotionEvidenceIssues = promotionEvidence.flatMap((item) => item.issues ?? []);
const promotionEvidenceRequired = promotionEvidence.length > 0;
const promotionEvidencePass = promotionEvidence.every((item) => item.valid === true);

if (
  externalBlocker &&
  executionRequirements.blocker_policy === "external_runtime_rca_after_3"
) {
  const finalResult = {
    checked_at: timestamp(),
    task_id: task.id,
    status: "blocked",
    promotion_eligible: false,
    deterministic,
    llm: null,
    execution_requirements: executionRequirements,
    external_blocker: externalBlocker,
    promotion_evidence: promotionEvidence,
    summary:
      `Task is blocked outside the repo by external runtime reachability. ` +
      `The configured endpoint ${externalBlocker.endpoint} could not be reached from ` +
      `${externalBlocker.source_command} while using the declared execution lane.`,
    missing_requirements: [
      `The current runtime cannot reach ${externalBlocker.endpoint}: ${externalBlocker.reason}`,
      `The live acceptance path still needs a successful rerun from the declared ${executionRequirements.worker_sandbox} worker lane.`,
    ],
  };
  writeText(path.join(STATE_DIR, "evaluation.json"), JSON.stringify(finalResult, null, 2));
  console.log(`evaluation: ${finalResult.status} promotion=${finalResult.promotion_eligible}`);
  process.exit(0);
}

if (!deterministic.pass) {
  const finalResult = {
    checked_at: timestamp(),
    task_id: task.id,
    status: "not_done",
    promotion_eligible: false,
    deterministic,
    llm: null,
    execution_requirements: executionRequirements,
    external_blocker: externalBlocker,
    promotion_evidence: promotionEvidence,
    summary: "Deterministic checks failed; task is not ready for promotion.",
    missing_requirements: [
      ...missingFiles.map((file) => `Missing required file: ${file}`),
      ...commandResults.filter((r) => !r.ok).map((r) => `Failed required command: ${r.command}`),
    ],
  };
  writeText(path.join(STATE_DIR, "evaluation.json"), JSON.stringify(finalResult, null, 2));
  console.log(`evaluation: ${finalResult.status} promotion=${finalResult.promotion_eligible}`);
  process.exit(0);
}

if (promotionEvidenceRequired && !promotionEvidencePass) {
  const finalResult = {
    checked_at: timestamp(),
    task_id: task.id,
    status: "blocked",
    promotion_eligible: false,
    deterministic,
    llm: null,
    execution_requirements: executionRequirements,
    external_blocker: externalBlocker,
    promotion_evidence: promotionEvidence,
    summary: "Deterministic checks passed, but current-cycle promotion evidence is missing or invalid.",
    missing_requirements: promotionEvidenceIssues,
  };
  writeText(path.join(STATE_DIR, "evaluation.json"), JSON.stringify(finalResult, null, 2));
  console.log(`evaluation: ${finalResult.status} promotion=${finalResult.promotion_eligible}`);
  process.exit(0);
}

spawnSync("node", [path.join("scripts", "ralph", "render-evaluator-prompt.mjs")], {
  cwd: process.cwd(),
  stdio: "inherit",
});

const evaluatorPromptPath = path.join(GENERATED_DIR, "current-evaluator-prompt.txt");
const schemaPath = path.join(process.cwd(), "scripts", "ralph", "schemas", "task-evaluation.schema.json");
const llmOutputPath = path.join(STATE_DIR, "evaluation.llm.json");
const evaluatorPrompt = readText(evaluatorPromptPath);

const codexArgs = [
    "exec",
    "--sandbox",
    executionRequirements.evaluator_sandbox,
    "--output-schema",
    schemaPath,
    "-o",
    llmOutputPath,
    evaluatorPrompt,
];


const evaluatorRun = spawnSync("codex", codexArgs, {
  cwd: process.cwd(),
  stdio: "inherit",
  encoding: "utf8",
});

let llm = null;
if (evaluatorRun.status === 0 && fileExists(llmOutputPath)) {
  llm = safeJsonParse(readText(llmOutputPath), null);
}

const finalStatus =
  llm?.decision === "done" && llm?.recommend_promotion === true ? "done" :
  llm?.decision === "blocked" ? "blocked" :
  "not_done";

const finalResult = {
  checked_at: timestamp(),
  task_id: task.id,
  status: finalStatus,
  promotion_eligible: finalStatus === "done",
  deterministic,
  llm,
  execution_requirements: executionRequirements,
  external_blocker: externalBlocker,
  promotion_evidence: promotionEvidence,
  summary:
    llm?.summary ??
    (finalStatus === "done"
      ? "Task eligible for promotion."
      : "Task remains active after evaluator review."),
  missing_requirements: Array.isArray(llm?.missing_requirements) ? llm.missing_requirements : [],
};

writeText(path.join(STATE_DIR, "evaluation.json"), JSON.stringify(finalResult, null, 2));
console.log(`evaluation: ${finalResult.status} promotion=${finalResult.promotion_eligible}`);
