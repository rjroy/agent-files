import { validateSegment } from "./segment";
import type { Segment, SegmentStore } from "./types";

/** Narrow adapter boundary; a host can back this with ctx.storage without coupling the domain to it. */
export interface KeyValueStorage {
  read(key: string): Promise<unknown | undefined>;
  write(key: string, value: unknown): Promise<void>;
  keys(prefix: string): Promise<string[]>;
}

export class StorageSegmentStore implements SegmentStore {
  constructor(private readonly storage: KeyValueStorage) {}

  async get(workspaceId: string, segmentId: string): Promise<Segment | undefined> {
    const value = await this.storage.read(key(workspaceId, segmentId));
    if (value === undefined) return undefined;
    validateSegment(value);
    const segment = value;
    if (segment.workspace.workspaceId !== workspaceId || segment.id !== segmentId) throw new Error("stored segment scope/key mismatch");
    return segment;
  }

  async put(segment: Segment): Promise<void> {
    validateSegment(segment);
    await this.storage.write(key(segment.workspace.workspaceId, segment.id), segment);
  }

  async list(workspaceId: string): Promise<Segment[]> {
    const prefix = workspacePrefix(workspaceId);
    const values = await Promise.all((await this.storage.keys(prefix)).map((entry) => this.storage.read(entry)));
    return values.filter((value): value is Segment => value !== undefined).map((value) => {
      validateSegment(value);
      const segment = value;
      if (segment.workspace.workspaceId !== workspaceId) throw new Error("stored segment workspace mismatch");
      return segment;
    });
  }
}

function workspacePrefix(workspaceId: string): string { return `segment-evaluator:v1:${encodeURIComponent(workspaceId)}:`; }
function key(workspaceId: string, segmentId: string): string { return `${workspacePrefix(workspaceId)}${encodeURIComponent(segmentId)}`; }
