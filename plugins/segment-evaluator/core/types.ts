/** Domain types for compact, evidence-linked work segments. No transcript text is stored. */

export type Actor = "user" | "assistant" | "tool" | "reviewer" | "system";
export type AgreementStatus = "proposed" | "agreed" | "disputed" | "superseded";
export type Outcome = "accepted" | "failed" | "blocked" | "unknown";

export interface WorkspaceScope {
  /** Stable host-provided workspace identity, not a display name. */
  readonly workspaceId: string;
}

export interface Attribution {
  actor: Actor;
  /** Optional session that supplied or confirmed this information. */
  sessionId?: string;
  source: "explicit" | "inferred" | "reconstructed" | "external-record";
  reference?: string;
  /** Host-observed producer of a model-tool annotation; distinct from caller-reported actor. */
  producer?: AnnotationProducer;
}

export interface AnnotationProducer {
  kind: "opencode-tool";
  sessionId: string;
  messageId?: string;
}

export interface CriterionVersion {
  version: number;
  text: string;
  createdAt: string;
  attribution: Attribution;
  agreement: AgreementStatus;
  /** Earlier criterion version, if this version revises it. */
  revisesVersion?: number;
}

export interface Criterion {
  id: string;
  versions: CriterionVersion[];
}

export interface EvidenceReference {
  /** Pointer/URI to evidence; never inline transcript or command output. */
  uri: string;
  kind: "test" | "artifact" | "git" | "beads" | "review" | "session" | "other";
  description?: string;
}

export interface Attempt {
  id: string;
  startedAt: string;
  endedAt?: string;
  reconstruction?: { basis: string; attribution: Attribution };
  evidence: EvidenceReference[];
  /** Informational event only; tool success/failure cannot determine segment outcome. */
  toolResult?: "succeeded" | "failed" | "unknown";
}

export type InterventionCategory =
  | "requirement-clarification" | "scope-priority" | "permission-safety"
  | "environment-tool-repair" | "diagnosis-debugging" | "manual-execution"
  | "recovery-direction" | "acceptance-handoff" | "other";

export interface Intervention {
  id: string;
  triggeredBy: string;
  category: InterventionCategory;
  actor: Actor;
  changed: string;
  outcome: string;
  timestamp: string;
  rescueBasis?: { causal: boolean; explanation: string };
  producer?: AnnotationProducer;
}

export interface CriterionFinding {
  criterionId: string;
  criterionVersion: number;
  status: "met" | "not-met" | "unclear";
  attribution: Attribution;
  evidence: EvidenceReference[];
}

export interface OutcomeAdjudication {
  outcome: Outcome;
  attribution: Attribution;
  rationale: string;
  evidence: EvidenceReference[];
  /** Criterion versions this judgment covers; retained if later revisions make it stale. */
  criterionVersions: Array<{ criterionId: string; version: number }>;
  /** Missing on pre-phase-3a records; those legacy judgments are unverified. */
  verificationStatus?: "verified" | "unverified";
}

export interface HarnessLesson {
  text: string;
  provenance: Attribution;
  applicability: string;
}

export interface PromptReference {
  workspaceId: string;
  sessionId: string;
  messageId: string;
  observedAt: string;
}

/** Minimal tool lifecycle metadata only; never contains tool arguments/results. */
export interface ToolObservation {
  workspaceId: string;
  sessionId: string;
  messageId?: string;
  toolCallId: string;
  toolName: string;
  status: "succeeded" | "failed";
  reference: string;
  observedAt: string;
}

export interface Segment {
  schemaVersion: 1;
  id: string;
  workspace: WorkspaceScope;
  linkedSessionIds: string[];
  originalIntent: { text: string; attribution: Attribution };
  criteria: Criterion[];
  attempts: Attempt[];
  interventions: Intervention[];
  findings: CriterionFinding[];
  /** Only explicit adjudication establishes a non-unknown outcome. */
  adjudication?: OutcomeAdjudication;
  harnessLesson?: HarnessLesson;
  captureIntegrityWarning?: string;
  lifecycle?: "active" | "closed";
  promptReferences?: PromptReference[];
  toolObservations?: ToolObservation[];
  createdAt: string;
  updatedAt: string;
}

export interface SegmentStore {
  get(workspaceId: string, segmentId: string): Promise<Segment | undefined>;
  put(segment: Segment): Promise<void>;
  list(workspaceId: string): Promise<Segment[]>;
}
