import { describe, expect, test } from "bun:test";
import {
  addAttempt, adjudicate, createSegment, linkSession, outcomeOf, recordFinding,
  reviseCriterion, StorageSegmentStore,
} from "../core";
import type { KeyValueStorage } from "../core";

const user = { actor: "user" as const, source: "explicit" as const, sessionId: "s1" };
const evidence = { uri: "beads://issue/abc", kind: "beads" as const };
const segment = (workspaceId = "workspace-a") => createSegment({
  id: "seg-1", workspaceId, sessionId: "s1", originalIntent: "Create notebook export",
  attribution: user, criteria: [{ id: "export", text: "Notebook exports successfully" }], at: "2026-09-24T00:00:00Z",
});

class MemoryStorage implements KeyValueStorage {
  data = new Map<string, unknown>();
  async read(key: string) { return this.data.get(key); }
  async write(key: string, value: unknown) { this.data.set(key, value); }
  async keys(prefix: string) { return [...this.data.keys()].filter((key) => key.startsWith(prefix)); }
}

describe("segment domain", () => {
  test("retrospectively reconstructs failed notebook attempt only from user's explicit judgment", () => {
    let current = addAttempt(segment(), {
      id: "attempt-1", reconstruction: { basis: "User said the notebook export attempt did not work", attribution: user },
      evidence: [evidence], toolResult: "succeeded",
    });
    current = adjudicate(current, { outcome: "failed", attribution: user, rationale: "User explicitly judged the requested notebook attempt unsuccessful", evidence: [evidence] });
    expect(current.attempts[0]?.reconstruction?.attribution).toEqual(user);
    expect(current.attempts[0]?.toolResult).toBe("succeeded");
    expect(outcomeOf(current)).toBe("failed");
  });

  test("supports a multi-turn retry and records intervention without treating intermediate tool failure as segment failure", () => {
    let current = addAttempt(segment(), { id: "first", toolResult: "failed", evidence: [evidence] });
    expect(outcomeOf(current)).toBe("unknown");
    current = linkSession(current, "s2");
    current = { ...current, interventions: [{
      id: "help-1", triggeredBy: "first attempt failed", category: "recovery-direction", actor: "user",
      changed: "Use a corrected notebook path", outcome: "retry proceeded", timestamp: "2026-09-24T00:01:00Z",
      rescueBasis: { causal: true, explanation: "Retry used the path supplied in this intervention" },
    }] };
    current = addAttempt(current, { id: "retry", toolResult: "succeeded", evidence: [{ uri: "test://notebook-export", kind: "test" }] });
    expect(current.linkedSessionIds).toEqual(["s1", "s2"]);
    expect(current.attempts).toHaveLength(2);
    expect(outcomeOf(current)).toBe("unknown");
  });

  test("tool success, idle state, or assistant self-report cannot establish success", () => {
    const current = addAttempt(segment(), { id: "attempt", toolResult: "succeeded" });
    expect(outcomeOf(current)).toBe("unknown");
    expect(() => adjudicate(current, { outcome: "accepted", attribution: { actor: "assistant", source: "explicit" }, rationale: "Done" })).toThrow("explicit user/reviewer");
  });

  test("outcome authority matrix permits explicit human judgments and requires traceable external records", () => {
    for (const actor of ["user", "reviewer"] as const) {
      const current = adjudicate(segment(), { outcome: "accepted", attribution: { actor, source: "explicit" }, rationale: "Explicitly accepted" });
      expect(outcomeOf(current)).toBe("accepted");
    }
    expect(() => adjudicate(segment(), { outcome: "failed", attribution: { actor: "reviewer", source: "inferred" }, rationale: "Looks failed" })).toThrow("explicit");
    expect(() => adjudicate(segment(), { outcome: "accepted", attribution: { actor: "assistant", source: "external-record", reference: "review://1" }, rationale: "Reported accepted", evidence: [evidence] })).toThrow("explicit");
    expect(() => adjudicate(segment(), { outcome: "accepted", attribution: { actor: "reviewer", source: "external-record", reference: "review://1" }, rationale: "Accepted" })).toThrow("traceable");
    expect(() => adjudicate(segment(), { outcome: "blocked", attribution: { actor: "reviewer", source: "external-record" }, rationale: "Blocked", evidence: [evidence] })).toThrow("traceable");
    const referenced = adjudicate(segment(), { outcome: "accepted", attribution: { actor: "reviewer", source: "external-record", reference: "review://acceptance" }, rationale: "External acceptance record", evidence: [{ uri: "review://acceptance", kind: "review" }] });
    expect(outcomeOf(referenced)).toBe("accepted");
    expect(outcomeOf(adjudicate(segment(), { outcome: "failed", attribution: user, rationale: "User explicitly judged failure" }))).toBe("failed");
  });

  test("keeps criteria revisions and findings attached to a specific version", () => {
    let current = reviseCriterion(segment(), { criterionId: "export", text: "Notebook exports with citations", attribution: user, agreement: "agreed" });
    current = recordFinding(current, { criterionId: "export", criterionVersion: 2, status: "unclear", attribution: { actor: "reviewer", source: "external-record" }, evidence: [evidence] });
    expect(current.criteria[0]?.versions.map((version) => version.text)).toEqual([
      "Notebook exports successfully", "Notebook exports with citations",
    ]);
    expect(current.criteria[0]?.versions[1]?.revisesVersion).toBe(1);
    expect(current.findings[0]?.criterionVersion).toBe(2);
  });

  test("criterion revision makes prior acceptance unknown until re-adjudication", () => {
    const accepted = adjudicate(segment(), { outcome: "accepted", attribution: { actor: "reviewer", source: "explicit" }, rationale: "Reviewed and accepted" });
    const revised = reviseCriterion(accepted, { criterionId: "export", text: "Notebook exports with citations", attribution: user, agreement: "agreed" });
    expect(revised.adjudication?.outcome).toBe("accepted"); // historical judgment remains visible
    expect(outcomeOf(revised)).toBe("unknown");
    expect(outcomeOf(adjudicate(revised, { outcome: "accepted", attribution: { actor: "reviewer", source: "explicit" }, rationale: "Re-reviewed revised criterion" }))).toBe("accepted");
  });

  test("recall is workspace-isolated", async () => {
    const backend = new MemoryStorage();
    const store = new StorageSegmentStore(backend);
    await store.put(segment("workspace-a"));
    await store.put({ ...segment("workspace-b"), id: "seg-1" });
    expect((await store.list("workspace-a")).map((item) => item.workspace.workspaceId)).toEqual(["workspace-a"]);
    expect(await store.get("workspace-b", "seg-1")).toMatchObject({ workspace: { workspaceId: "workspace-b" } });
    expect(await store.get("workspace-a", "missing")).toBeUndefined();
  });

  test("rejects malformed persisted values on get and list", async () => {
    const backend = new MemoryStorage();
    const store = new StorageSegmentStore(backend);
    await store.put(segment());
    const key = "segment-evaluator:v1:workspace-a:seg-1";
    backend.data.set(key, { ...segment(), schemaVersion: 9 });
    await expect(store.get("workspace-a", "seg-1")).rejects.toThrow("schema");

    backend.data.set(key, {
      ...segment(),
      findings: [{ criterionId: "missing", criterionVersion: 1, status: "met", attribution: user, evidence: [] }],
    });
    await expect(store.list("workspace-a")).rejects.toThrow("finding");

    backend.data.set(key, {
      ...segment(), adjudication: { outcome: "optimistic", attribution: user, rationale: "bad", evidence: [], criterionVersions: [] },
    });
    await expect(store.get("workspace-a", "seg-1")).rejects.toThrow("adjudication");
  });
});
