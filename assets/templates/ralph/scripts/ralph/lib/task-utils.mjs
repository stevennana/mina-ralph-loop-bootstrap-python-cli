import fs from "node:fs";
import path from "node:path";

export const REPO_ROOT = process.cwd();
export const ACTIVE_TASK_DIR = path.join(REPO_ROOT, "docs", "exec-plans", "active");
export const COMPLETED_TASK_DIR = path.join(REPO_ROOT, "docs", "exec-plans", "completed");
export const STATE_DIR = path.join(REPO_ROOT, "state");
export const GENERATED_DIR = path.join(REPO_ROOT, "scripts", "ralph", "generated");
export const DEFAULT_EXECUTION_REQUIREMENTS = {
  worker_sandbox: "workspace-write",
  evaluator_sandbox: "read-only",
  network_required: false,
  blocker_policy: "standard_rca_after_3",
};
export const DEFAULT_PROMOTION_EVIDENCE_FRESHNESS = "current_cycle";
const CURRENT_CYCLE_FRESHNESS_GRACE_MS = 1000;

export function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
}

export function readText(filePath) {
  return fs.readFileSync(filePath, "utf8");
}

export function writeText(filePath, content) {
  ensureDir(path.dirname(filePath));
  fs.writeFileSync(filePath, content, "utf8");
}

export function fileExists(filePath) {
  return fs.existsSync(filePath);
}

export function timestamp() {
  return new Date().toISOString();
}

export function normalizeTaskId(raw) {
  return String(raw).trim().replace(/\.md$/, "");
}

export function readCurrentTaskId() {
  const filePath = path.join(STATE_DIR, "current-task.txt");
  if (!fileExists(filePath)) return null;
  const value = normalizeTaskId(readText(filePath));
  return value.length > 0 ? value : null;
}

export function normalizeExecutionRequirements(taskMeta = {}) {
  const provided =
    taskMeta && typeof taskMeta === "object" && taskMeta.execution_requirements && typeof taskMeta.execution_requirements === "object"
      ? taskMeta.execution_requirements
      : {};

  const workerSandbox = ["workspace-write", "danger-full-access"].includes(provided.worker_sandbox)
    ? provided.worker_sandbox
    : DEFAULT_EXECUTION_REQUIREMENTS.worker_sandbox;
  const evaluatorSandbox = ["read-only", "workspace-write", "danger-full-access"].includes(provided.evaluator_sandbox)
    ? provided.evaluator_sandbox
    : DEFAULT_EXECUTION_REQUIREMENTS.evaluator_sandbox;
  const blockerPolicy = ["standard_rca_after_3", "external_runtime_rca_after_3"].includes(provided.blocker_policy)
    ? provided.blocker_policy
    : DEFAULT_EXECUTION_REQUIREMENTS.blocker_policy;

  return {
    worker_sandbox: workerSandbox,
    evaluator_sandbox: evaluatorSandbox,
    network_required: Boolean(provided.network_required),
    blocker_policy: blockerPolicy,
  };
}

export function normalizePromotionEvidence(taskMeta = {}) {
  const provided =
    taskMeta && typeof taskMeta === "object" && Array.isArray(taskMeta.promotion_evidence)
      ? taskMeta.promotion_evidence
      : [];

  return provided
    .map((item, index) => {
      if (!item || typeof item !== "object") {
        return null;
      }

      const kind = ["command_artifact", "jsonl_event_log"].includes(item.kind)
        ? item.kind
        : "command_artifact";
      const freshness = ["current_cycle", "latest"].includes(item.freshness)
        ? item.freshness
        : DEFAULT_PROMOTION_EVIDENCE_FRESHNESS;
      const producerCommand = typeof item.producer_command === "string" ? item.producer_command.trim() : "";
      const manifestPath = typeof item.manifest_path === "string" ? item.manifest_path.trim() : "";

      if (!producerCommand || !manifestPath) {
        return null;
      }

      const normalized = {
        id: typeof item.id === "string" && item.id.trim() ? item.id.trim() : `evidence-${index + 1}`,
        kind,
        producer_command: producerCommand,
        manifest_path: manifestPath,
        freshness,
      };

      if (typeof item.log_path === "string" && item.log_path.trim()) {
        normalized.log_path = item.log_path.trim();
      }
      if (typeof item.required_event === "string" && item.required_event.trim()) {
        normalized.required_event = item.required_event.trim();
      }

      return normalized;
    })
    .filter(Boolean);
}

export function writeCurrentTaskId(taskId) {
  writeText(path.join(STATE_DIR, "current-task.txt"), `${normalizeTaskId(taskId)}\n`);
}

export function extractTaskMeta(markdown) {
  const match = markdown.match(/```json taskmeta\s*([\s\S]*?)```/);
  if (!match) return null;
  return JSON.parse(match[1].trim());
}

export function replaceTaskMeta(markdown, nextMeta) {
  const serialized = JSON.stringify(nextMeta, null, 2);
  return markdown.replace(
    /```json taskmeta\s*[\s\S]*?```/,
    `\`\`\`json taskmeta\n${serialized}\n\`\`\``
  );
}

export function listTaskDocs(dirPath = ACTIVE_TASK_DIR) {
  if (!fileExists(dirPath)) return [];
  const entries = fs.readdirSync(dirPath, { withFileTypes: true });
  const docs = [];
  for (const entry of entries) {
    if (!entry.isFile() || !entry.name.endsWith(".md")) continue;
    const fullPath = path.join(dirPath, entry.name);
    const markdown = readText(fullPath);
    const meta = extractTaskMeta(markdown);
    if (!meta) continue;
    docs.push({
      id: normalizeTaskId(meta.id ?? entry.name),
      fileName: entry.name,
      filePath: fullPath,
      markdown,
      meta,
    });
  }
  return docs.sort((a, b) => {
    const ao = a.meta.order ?? Number.MAX_SAFE_INTEGER;
    const bo = b.meta.order ?? Number.MAX_SAFE_INTEGER;
    return ao - bo || a.fileName.localeCompare(b.fileName);
  });
}

export function findTaskDoc(taskId, dirPath = ACTIVE_TASK_DIR) {
  const normalized = normalizeTaskId(taskId);
  return listTaskDocs(dirPath).find((task) => task.id === normalized) ?? null;
}

export function getFirstQueuedOrActiveTask() {
  const tasks = listTaskDocs();
  return tasks.find((task) => ["active", "queued"].includes(task.meta.status)) ?? null;
}

export function extractSection(markdown, heading) {
  const escaped = heading.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const regex = new RegExp(`^## ${escaped}\\n([\\s\\S]*?)(?=^## |\\Z)`, "m");
  const match = markdown.match(regex);
  return match ? match[1].trim() : "";
}

export function appendTaskProgressNote(markdown, noteLine) {
  const marker = "## Progress log";
  if (!markdown.includes(marker)) return `${markdown.trim()}\n\n## Progress log\n\n- ${noteLine}\n`;
  return markdown.replace(
    /## Progress log\s*([\s\S]*)$/,
    (_whole, tail) => `${marker}\n\n${tail.trim()}\n- ${noteLine}\n`
  );
}

export function renderBacklogMarkdown(tasks, currentTaskId) {
  const lines = ["# Backlog", ""];
  for (const task of tasks) {
    const isCurrent = normalizeTaskId(task.id) === normalizeTaskId(currentTaskId);
    const marker =
      task.meta.status === "completed"
        ? "x"
        : task.meta.status === "blocked"
          ? "!"
          : " ";
    const currentTag = isCurrent ? " ← current" : "";
    const statusTag = task.meta.status === "blocked" ? " (blocked)" : "";
    lines.push(`- [${marker}] ${task.id} — ${task.meta.title}${statusTag}${currentTag}`);
  }
  lines.push("");
  return `${lines.join("\n")}\n`;
}

export function safeJsonParse(text, fallback) {
  try {
    return JSON.parse(text);
  } catch {
    return fallback;
  }
}

function parseTimestampMs(value) {
  if (typeof value !== "string" || !value.trim()) return null;
  const parsed = Date.parse(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function resolveRepoPath(relativeOrAbsolutePath) {
  if (typeof relativeOrAbsolutePath !== "string" || !relativeOrAbsolutePath.trim()) {
    return null;
  }
  if (path.isAbsolute(relativeOrAbsolutePath)) {
    return relativeOrAbsolutePath;
  }
  return path.join(REPO_ROOT, relativeOrAbsolutePath);
}

function findEventInJsonl(logPath, eventName) {
  if (!logPath || !eventName || !fileExists(logPath)) {
    return false;
  }

  const lines = readText(logPath)
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);

  for (const line of lines) {
    const payload = safeJsonParse(line, null);
    if (payload?.event === eventName) {
      return true;
    }
  }

  return readText(logPath).includes(eventName);
}

export function evaluatePromotionEvidence(taskMeta = {}, options = {}) {
  const currentCycleStartedAt = parseTimestampMs(options.currentCycleStartedAt ?? null);

  return normalizePromotionEvidence(taskMeta).map((evidence) => {
    const manifestAbsolutePath = resolveRepoPath(evidence.manifest_path);
    const base = {
      ...evidence,
      manifest_absolute_path: manifestAbsolutePath,
      manifest_exists: false,
      manifest_status: "missing",
      manifest_checked_at: null,
      producer_command_matches: false,
      fresh_enough: evidence.freshness !== "current_cycle",
      log_path: evidence.log_path ?? null,
      required_event_found: evidence.required_event ? false : null,
      valid: false,
      issues: [],
    };

    if (!manifestAbsolutePath || !fileExists(manifestAbsolutePath)) {
      base.issues.push(`Missing manifest: ${evidence.manifest_path}`);
      return base;
    }

    base.manifest_exists = true;
    const manifest = safeJsonParse(readText(manifestAbsolutePath), null);
    if (!manifest || typeof manifest !== "object") {
      base.manifest_status = "invalid";
      base.issues.push(`Invalid manifest JSON: ${evidence.manifest_path}`);
      return base;
    }

    base.manifest_status = typeof manifest.status === "string" ? manifest.status : "unknown";
    base.manifest_checked_at = typeof manifest.checked_at === "string" ? manifest.checked_at : null;
    base.producer_command_matches = manifest.producer_command === evidence.producer_command;
    base.log_path =
      typeof evidence.log_path === "string" && evidence.log_path
        ? evidence.log_path
        : typeof manifest.copied_log_path === "string"
          ? manifest.copied_log_path
          : null;

    if (!base.producer_command_matches) {
      base.issues.push(
        `Manifest producer command mismatch for ${evidence.id}: expected '${evidence.producer_command}'.`,
      );
    }

    if (evidence.freshness === "current_cycle" && currentCycleStartedAt !== null) {
      const manifestCheckedAt = parseTimestampMs(base.manifest_checked_at);
      base.fresh_enough =
        manifestCheckedAt !== null &&
        manifestCheckedAt >= currentCycleStartedAt - CURRENT_CYCLE_FRESHNESS_GRACE_MS;
      if (!base.fresh_enough) {
        base.issues.push(`Manifest for ${evidence.id} is stale for the current cycle.`);
      }
    }

    if (base.manifest_status !== "passed") {
      base.issues.push(`Manifest status for ${evidence.id} is '${base.manifest_status}', not 'passed'.`);
    }

    if (evidence.required_event) {
      const manifestEventFound = manifest.event_found === true;
      const resolvedLogPath = resolveRepoPath(base.log_path);
      const logEventFound = resolvedLogPath ? findEventInJsonl(resolvedLogPath, evidence.required_event) : false;
      base.required_event_found = manifestEventFound || logEventFound;
      if (!base.required_event_found) {
        base.issues.push(`Required event '${evidence.required_event}' was not preserved for ${evidence.id}.`);
      }
    }

    base.valid =
      base.manifest_exists &&
      base.manifest_status === "passed" &&
      base.producer_command_matches &&
      base.fresh_enough &&
      (base.required_event_found === null || base.required_event_found === true);

    return base;
  });
}
