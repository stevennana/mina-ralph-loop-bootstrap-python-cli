import path from "node:path";
import {
  evaluatePromotionEvidence,
  GENERATED_DIR,
  extractSection,
  findTaskDoc,
  readCurrentTaskId,
  readText,
  writeText,
  fileExists,
} from "./lib/task-utils.mjs";

const taskId = readCurrentTaskId();
if (!taskId || taskId === "NONE") {
  throw new Error("No current task is configured.");
}

const task = findTaskDoc(taskId);
if (!task) {
  throw new Error(`Active task '${taskId}' not found.`);
}

const deterministicPath = path.join(process.cwd(), "state", "deterministic-checks.json");
const deterministic = fileExists(deterministicPath) ? readText(deterministicPath) : "{}";
const deterministicJson = fileExists(deterministicPath) ? JSON.parse(readText(deterministicPath)) : null;
const workerHandoffPath = path.join(process.cwd(), "state", "worker-handoff.txt");
const workerHandoff = fileExists(workerHandoffPath) ? readText(workerHandoffPath) : "";
const promotionEvidence = evaluatePromotionEvidence(task.meta, {
  currentCycleStartedAt: deterministicJson?.checked_at ?? null,
});

const objective = extractSection(task.markdown, "Objective");
const scope = extractSection(task.markdown, "Scope");
const outOfScope = extractSection(task.markdown, "Out of scope");
const exitCriteria = extractSection(task.markdown, "Exit criteria");
const evaluatorNotes = extractSection(task.markdown, "Evaluator notes");

const docsToRead = Array.from(new Set(task.meta.prompt_docs ?? []));

const prompt = `
You are the promotion evaluator for a repository-local Ralph loop.

Read these documents before deciding:
${docsToRead.map((doc) => `- ${doc}`).join("\n")}
- ${task.filePath.replace(`${process.cwd()}/`, "")}

Current task id: ${task.id}
Current task title: ${task.meta.title}

Objective:
${objective}

Scope:
${scope}

Out of scope:
${outOfScope}

Exit criteria:
${exitCriteria}

Evaluator notes:
${evaluatorNotes}

Deterministic check summary:
${deterministic}

Promotion evidence summary for this cycle:
${promotionEvidence.length ? JSON.stringify(promotionEvidence, null, 2) : "[]"}

Worker handoff summary from this cycle:
${workerHandoff || "(empty)"}

Authoritative precedence for this cycle:
- treat the current-cycle deterministic check summary as the primary machine-readable truth
- treat current-cycle promotion evidence manifests as the primary live-proof truth for external acceptance tasks
- treat concrete runtime artifacts you can verify in the repository or temp logs as stronger evidence than historical prose
- treat the worker handoff as context only, not as the authoritative promotion decision
- treat older progress-log or acceptance-note prose as lowest precedence when it conflicts with current-cycle passing evidence
- do not let stale blocked narrative override current-cycle passing checks or concrete success artifacts unless the blocker is still reproducible now
- do not let worker handoff prose overrule a valid current-cycle promotion evidence manifest that satisfies the required live-proof condition

Your job:
- inspect the repository and current implementation
- determine whether the current task is actually complete
- mark \`done\` only if the exit criteria are satisfied in substance, not just approximately
- prefer conservative decisions
- recommend promotion only if the task is truly ready

Return JSON only using the provided schema.
`.trim();

const outputPath = path.join(GENERATED_DIR, "current-evaluator-prompt.txt");
writeText(outputPath, `${prompt}\n`);
console.log(outputPath);
