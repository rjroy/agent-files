import type {
  Actor, Attribution, Criterion, CriterionFinding, CriterionVersion,
  EvidenceReference, Outcome, OutcomeAdjudication, Segment,
} from "./types";

const now = () => new Date().toISOString();

export function createSegment(input: {
  id: string;
  workspaceId: string;
  sessionId: string;
  originalIntent: string;
  attribution: Attribution;
  criteria?: Array<{ id: string; text: string; agreement?: CriterionVersion["agreement"] }>;
  captureIntegrityWarning?: string;
  at?: string;
}): Segment {
  if (!input.workspaceId.trim() || !input.id.trim()) throw new Error("segment and workspace IDs are required");
  const timestamp = input.at ?? now();
  return {
    schemaVersion: 1,
    id: input.id,
    workspace: { workspaceId: input.workspaceId },
    linkedSessionIds: [input.sessionId],
    originalIntent: { text: input.originalIntent, attribution: input.attribution },
    criteria: (input.criteria ?? []).map(({ id, text, agreement }) => ({
      id,
      versions: [{ version: 1, text, createdAt: timestamp, attribution: input.attribution, agreement: agreement ?? "proposed" }],
    })),
    attempts: [], interventions: [], findings: [],
    lifecycle: "active", promptReferences: [], toolObservations: [],
    captureIntegrityWarning: input.captureIntegrityWarning,
    createdAt: timestamp, updatedAt: timestamp,
  };
}

export function linkSession(segment: Segment, sessionId: string): Segment {
  if (!sessionId.trim()) throw new Error("session ID is required");
  return update(segment, { linkedSessionIds: [...new Set([...segment.linkedSessionIds, sessionId])] });
}

export function reviseCriterion(segment: Segment, input: {
  criterionId: string; text: string; attribution: Attribution; agreement?: CriterionVersion["agreement"]; at?: string;
}): Segment {
  const criteria = segment.criteria.map((criterion) => {
    if (criterion.id !== input.criterionId) return criterion;
    const previous = criterion.versions.at(-1);
    if (!previous) throw new Error(`criterion ${criterion.id} has no versions`);
    return { ...criterion, versions: [...criterion.versions, {
      version: previous.version + 1, text: input.text, createdAt: input.at ?? now(),
      attribution: input.attribution, agreement: input.agreement ?? "proposed", revisesVersion: previous.version,
    }] };
  });
  if (!segment.criteria.some((c) => c.id === input.criterionId)) throw new Error(`unknown criterion: ${input.criterionId}`);
  return update(segment, { criteria });
}

export function addAttempt(segment: Segment, attempt: {
  id: string; startedAt?: string; endedAt?: string; reconstruction?: { basis: string; attribution: Attribution };
  evidence?: EvidenceReference[]; toolResult?: "succeeded" | "failed" | "unknown";
}): Segment {
  if (segment.attempts.some((entry) => entry.id === attempt.id)) throw new Error(`duplicate attempt: ${attempt.id}`);
  return update(segment, { attempts: [...segment.attempts, {
    ...attempt, startedAt: attempt.startedAt ?? now(), evidence: [...(attempt.evidence ?? [])],
  }] });
}

export function recordFinding(segment: Segment, finding: CriterionFinding): Segment {
  const criterion = segment.criteria.find((item) => item.id === finding.criterionId);
  if (!criterion?.versions.some((v) => v.version === finding.criterionVersion)) throw new Error("finding references unknown criterion version");
  return update(segment, { findings: [...segment.findings, { ...finding, evidence: [...finding.evidence] }] });
}

export function outcomeOf(segment: Segment): Outcome {
  const adjudication = segment.adjudication;
  if (!adjudication) return "unknown";
  const current = segment.criteria.map((criterion) => ({ criterionId: criterion.id, version: criterion.versions.at(-1)?.version ?? 0 }));
  return adjudication.verificationStatus === "verified" && sameCriterionVersions(adjudication.criterionVersions, current) ? adjudication.outcome : "unknown";
}

export function adjudicate(segment: Segment, input: {
  outcome: Outcome; attribution: Attribution; rationale: string;
  evidence?: EvidenceReference[];
}): Segment {
  if (input.outcome !== "unknown") assertAdjudicationAuthority(input.attribution, input.evidence ?? []);
  if (!input.rationale.trim()) throw new Error("adjudication rationale is required");
  return update(segment, { adjudication: {
    ...input, evidence: [...(input.evidence ?? [])],
    criterionVersions: segment.criteria.map((criterion) => ({ criterionId: criterion.id, version: criterion.versions.at(-1)?.version ?? 0 })),
    verificationStatus: "verified",
  } });
}

export function setHarnessLesson(segment: Segment, lesson: Segment["harnessLesson"]): Segment {
  if (lesson && (!lesson.text.trim() || !lesson.applicability.trim())) throw new Error("lesson text and applicability are required");
  return update(segment, { harnessLesson: lesson });
}

export function validateSegment(value: unknown): asserts value is Segment {
  if (!isRecord(value)) throw new Error("invalid segment value");
  const segment = value as Segment;
  if (segment.schemaVersion !== 1 || !isRecord(segment.workspace) ||
      !nonEmpty(segment.workspace.workspaceId) || !nonEmpty(segment.id)) throw new Error("invalid segment schema, scope, or ID");
  for (const field of ["linkedSessionIds", "criteria", "attempts", "interventions", "findings"] as const) {
    if (!Array.isArray(segment[field])) throw new Error(`invalid segment ${field}`);
  }
  if (!isRecord(segment.originalIntent) || typeof segment.originalIntent.text !== "string") throw new Error("invalid original intent");
  validateAttribution(segment.originalIntent.attribution);
  if (segment.linkedSessionIds.some((id) => !nonEmpty(id)) || new Set(segment.linkedSessionIds).size !== segment.linkedSessionIds.length) {
    throw new Error("invalid or duplicate linked session ID");
  }
  if (segment.lifecycle !== undefined && !["active", "closed"].includes(segment.lifecycle)) throw new Error("invalid lifecycle");
  if (segment.promptReferences !== undefined) {
    if (!Array.isArray(segment.promptReferences)) throw new Error("invalid prompt references");
    const refIds = segment.promptReferences.map((ref) => `${ref.workspaceId}\u0000${ref.sessionId}\u0000${ref.messageId}`);
    if (segment.promptReferences.some((ref) => !isRecord(ref) || !nonEmpty(ref.workspaceId) || !nonEmpty(ref.sessionId) || !nonEmpty(ref.messageId) || !nonEmpty(ref.observedAt)) || new Set(refIds).size !== refIds.length) throw new Error("invalid or duplicate prompt reference");
  }
  if (segment.toolObservations !== undefined) {
    if (!Array.isArray(segment.toolObservations) || segment.toolObservations.some((event) => !isRecord(event) ||
      !nonEmpty(event.workspaceId) || !nonEmpty(event.sessionId) || !nonEmpty(event.toolCallId) || !nonEmpty(event.toolName) ||
      !["succeeded", "failed"].includes(event.status) || !nonEmpty(event.reference) || !nonEmpty(event.observedAt))) throw new Error("invalid tool observations");
  }
  assertUniqueIds(segment.criteria, "criterion");
  assertUniqueIds(segment.attempts, "attempt");
  assertUniqueIds(segment.interventions, "intervention");
  for (const criterion of segment.criteria) {
    if (!isRecord(criterion) || !nonEmpty(criterion.id) || !Array.isArray(criterion.versions) || criterion.versions.length === 0) throw new Error("invalid criterion");
    let expectedVersion = 1;
    for (const version of criterion.versions) {
      if (!isRecord(version) || !["proposed", "agreed", "disputed", "superseded"].includes(version.agreement)) throw new Error(`invalid criterion version ${criterion.id}`);
      if (version.version !== expectedVersion++) throw new Error(`non-contiguous versions for criterion ${criterion.id}`);
      if (!nonEmpty(version.text)) throw new Error(`empty criterion ${criterion.id}`);
      validateAttribution(version.attribution);
    }
  }
  for (const finding of segment.findings) {
    if (!isRecord(finding) || !segment.criteria.some((criterion) => criterion.id === finding.criterionId && criterion.versions.some((v) => v.version === finding.criterionVersion)) ||
        !["met", "not-met", "unclear"].includes(finding.status) || !Array.isArray(finding.evidence)) throw new Error("invalid finding reference or status");
    validateAttribution(finding.attribution);
    finding.evidence.forEach(validateEvidence);
  }
  if (segment.adjudication !== undefined) {
    const adjudication = segment.adjudication;
    if (!isRecord(adjudication) || !["accepted", "failed", "blocked", "unknown"].includes(adjudication.outcome) ||
        !nonEmpty(adjudication.rationale) || !Array.isArray(adjudication.evidence) || !Array.isArray(adjudication.criterionVersions)) {
      throw new Error("invalid outcome adjudication");
    }
    validateAttribution(adjudication.attribution);
    if (adjudication.verificationStatus !== undefined && !["verified", "unverified"].includes(adjudication.verificationStatus)) throw new Error("invalid adjudication verification status");
    if (adjudication.verificationStatus === "verified" && adjudication.outcome !== "unknown") assertAdjudicationAuthority(adjudication.attribution, adjudication.evidence);
    adjudication.evidence.forEach(validateEvidence);
    const snapshotIds = adjudication.criterionVersions.map((entry) => entry?.criterionId);
    if (new Set(snapshotIds).size !== snapshotIds.length || adjudication.criterionVersions.some((entry) =>
      !isRecord(entry) || !nonEmpty(entry.criterionId) || !Number.isInteger(entry.version) || entry.version < 0)) {
      throw new Error("invalid adjudication criterion snapshot");
    }
  }
  for (const attempt of segment.attempts) {
    if (!isRecord(attempt) || !nonEmpty(attempt.id) || !nonEmpty(attempt.startedAt) || !Array.isArray(attempt.evidence)) throw new Error("invalid attempt");
    attempt.evidence.forEach(validateEvidence);
    if (attempt.reconstruction) validateAttribution(attempt.reconstruction.attribution);
  }
  for (const intervention of segment.interventions) {
    if (!isRecord(intervention) || !nonEmpty(intervention.id) || !nonEmpty(intervention.triggeredBy) || !nonEmpty(intervention.changed) || !nonEmpty(intervention.outcome)) throw new Error("invalid intervention");
  }
}

function assertAdjudicationAuthority(attribution: Attribution, evidence: EvidenceReference[]): void {
  const explicitHuman = (attribution.actor === "user" || attribution.actor === "reviewer") && attribution.source === "explicit";
  const traceableRecord = attribution.actor !== "assistant" && attribution.actor !== "tool" && attribution.actor !== "system" &&
    attribution.source === "external-record" && nonEmpty(attribution.reference) && evidence.length > 0 && evidence.every((item) => isRecord(item) && nonEmpty(item.uri));
  if (!explicitHuman && !traceableRecord) throw new Error("outcome requires explicit user/reviewer judgment or a traceable external record");
}

function validateAttribution(value: unknown): asserts value is Attribution {
  if (!isRecord(value) || !["user", "assistant", "tool", "reviewer", "system"].includes(value.actor) ||
      !["explicit", "inferred", "reconstructed", "external-record"].includes(value.source)) throw new Error("invalid attribution");
}
function validateEvidence(value: unknown): asserts value is EvidenceReference {
  if (!isRecord(value) || !nonEmpty(value.uri) || !["test", "artifact", "git", "beads", "review", "session", "other"].includes(value.kind)) throw new Error("invalid evidence reference");
}
function assertUniqueIds(items: unknown[], label: string): void {
  const ids = items.map((item) => isRecord(item) ? item.id : undefined);
  if (ids.some((id) => !nonEmpty(id)) || new Set(ids).size !== ids.length) throw new Error(`invalid or duplicate ${label} ID`);
}
function sameCriterionVersions(a: OutcomeAdjudication["criterionVersions"], b: OutcomeAdjudication["criterionVersions"]): boolean {
  return a.length === b.length && a.every((entry, i) => entry.criterionId === b[i]?.criterionId && entry.version === b[i]?.version);
}
function isRecord(value: unknown): value is Record<string, any> { return typeof value === "object" && value !== null && !Array.isArray(value); }
function nonEmpty(value: unknown): value is string { return typeof value === "string" && value.trim().length > 0; }

function update(segment: Segment, patch: Partial<Segment>): Segment {
  const result = { ...segment, ...patch, updatedAt: now() };
  validateSegment(result);
  return result;
}

// Keep public surface intentionally type-safe for attribution producers.
export type { Actor, Attribution, Criterion, CriterionFinding };
