import { describe, test, expect, beforeEach, afterEach, spyOn } from "bun:test";
import * as os from "os";
import * as fs from "fs";
import * as path from "path";
import { run } from "../src/generate-video.ts";

let exitSpy: ReturnType<typeof spyOn>;
let tmpDir: string;
let testImagePath: string;
let stderrChunks: string[];
let origStderrWrite: typeof process.stderr.write;

beforeEach(() => {
  process.env.REPLICATE_API_TOKEN = "test-token";
  const throwingExit = ((_code?: number): never => {
    throw new Error(`process.exit(${_code})`);
  }) as unknown as typeof process.exit;
  exitSpy = spyOn(process, "exit").mockImplementation(throwingExit);

  tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "video-test-"));
  testImagePath = path.join(tmpDir, "input.png");
  fs.writeFileSync(testImagePath, Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]));

  stderrChunks = [];
  origStderrWrite = process.stderr.write.bind(process.stderr);
  (process.stderr as NodeJS.WriteStream).write = (chunk: unknown): boolean => {
    stderrChunks.push(String(chunk));
    return true;
  };
});

afterEach(() => {
  exitSpy.mockRestore();
  process.stderr.write = origStderrWrite;
  fs.rmSync(tmpDir, { recursive: true, force: true });
});

// ---------------------------------------------------------------------------
// Fetch helpers
// ---------------------------------------------------------------------------

function makeVideoFetch(opts: {
  predId?: string;
  outputUrl?: string;
  failOnPoll?: boolean;
} = {}): { fetchFn: typeof fetch; getCapturedInput: () => Record<string, unknown> | null } {
  const predId = opts.predId ?? "vid-pred-1";
  const outputUrl = opts.outputUrl ?? "https://example.com/video.mp4";
  const failOnPoll = opts.failOnPoll ?? false;

  let capturedInput: Record<string, unknown> | null = null;
  let pollCount = 0;

  const fetchFn = async (
    url: string | URL | Request,
    init?: RequestInit,
  ): Promise<Response> => {
    const urlStr = url.toString();

    if (init?.method === "POST") {
      capturedInput = (
        JSON.parse(init.body as string) as { input: Record<string, unknown> }
      ).input;
      return new Response(
        JSON.stringify({ id: predId, status: "processing" }),
        { status: 200 },
      );
    }

    // Download step — any non-API URL
    if (!urlStr.includes("api.replicate.com")) {
      return new Response(new Uint8Array([0, 1, 2, 3]), { status: 200 });
    }

    // Poll GET — replicate predictions endpoint
    pollCount++;
    if (failOnPoll) {
      return new Response(
        JSON.stringify({ id: predId, status: "failed" }),
        { status: 200 },
      );
    }
    // Succeed immediately on first poll to avoid 10s setTimeout
    return new Response(
      JSON.stringify({ id: predId, status: "succeeded", output: outputUrl }),
      { status: 200 },
    );
  };

  return { fetchFn, getCapturedInput: () => capturedInput };
}

// ---------------------------------------------------------------------------
// Argument validation
// ---------------------------------------------------------------------------

describe("run() argument validation", () => {
  test("missing --image exits with code 1", async () => {
    const { fetchFn } = makeVideoFetch();
    const outPath = path.join(tmpDir, "out.mp4");
    await expect(
      run(["--prompt", "fly away", "--model", "minimax/video-01-live", "--output", outPath], fetchFn),
    ).rejects.toThrow("process.exit(1)");
  });

  test("missing --prompt exits with code 1", async () => {
    const { fetchFn } = makeVideoFetch();
    const outPath = path.join(tmpDir, "out.mp4");
    await expect(
      run(
        ["--image", testImagePath, "--model", "minimax/video-01-live", "--output", outPath],
        fetchFn,
      ),
    ).rejects.toThrow("process.exit(1)");
  });

  test("missing --model exits with code 1", async () => {
    const { fetchFn } = makeVideoFetch();
    const outPath = path.join(tmpDir, "out.mp4");
    await expect(
      run(["--image", testImagePath, "--prompt", "fly away", "--output", outPath], fetchFn),
    ).rejects.toThrow("process.exit(1)");
  });

  test("missing --output exits with code 1", async () => {
    const { fetchFn } = makeVideoFetch();
    await expect(
      run(
        ["--image", testImagePath, "--prompt", "fly away", "--model", "minimax/video-01-live"],
        fetchFn,
      ),
    ).rejects.toThrow("process.exit(1)");
  });
});

// ---------------------------------------------------------------------------
// Model-specific input parameter routing
// ---------------------------------------------------------------------------

describe("run() model parameter routing", () => {
  test("minimax/video-01-live sends first_frame_image as scalar data URI", async () => {
    const { fetchFn, getCapturedInput } = makeVideoFetch();
    const outPath = path.join(tmpDir, "out.mp4");

    await run(
      [
        "--image", testImagePath,
        "--prompt", "fly away",
        "--model", "minimax/video-01-live",
        "--output", outPath,
      ],
      fetchFn,
    );

    const input = getCapturedInput();
    expect(input).not.toBeNull();
    expect(typeof input!.first_frame_image).toBe("string");
    expect((input!.first_frame_image as string).startsWith("data:image/png;base64,")).toBe(true);
    expect(Array.isArray(input!.first_frame_image)).toBe(false);
    expect(input!.image).toBeUndefined();
  });

  test("unknown model defaults to image param as scalar data URI", async () => {
    const { fetchFn, getCapturedInput } = makeVideoFetch();
    const outPath = path.join(tmpDir, "out.mp4");

    await run(
      [
        "--image", testImagePath,
        "--prompt", "test prompt",
        "--model", "unknown/video-model",
        "--output", outPath,
      ],
      fetchFn,
    );

    const input = getCapturedInput();
    expect(input).not.toBeNull();
    expect(typeof input!.image).toBe("string");
    expect((input!.image as string).startsWith("data:image/png;base64,")).toBe(true);
    expect(input!.first_frame_image).toBeUndefined();
  });

  test("prompt is forwarded in input", async () => {
    const { fetchFn, getCapturedInput } = makeVideoFetch();
    const outPath = path.join(tmpDir, "out.mp4");

    await run(
      [
        "--image", testImagePath,
        "--prompt", "a dragon flies over a castle",
        "--model", "minimax/video-01-live",
        "--output", outPath,
      ],
      fetchFn,
    );

    const input = getCapturedInput();
    expect(input?.prompt).toBe("a dragon flies over a castle");
  });
});

// ---------------------------------------------------------------------------
// Failure / timeout path
// ---------------------------------------------------------------------------

describe("run() prediction failure", () => {
  test("failed prediction exits 1 and stderr contains prediction ID", async () => {
    const { fetchFn } = makeVideoFetch({ predId: "pred-fail-123", failOnPoll: true });
    const outPath = path.join(tmpDir, "out.mp4");

    await expect(
      run(
        [
          "--image", testImagePath,
          "--prompt", "fly away",
          "--model", "minimax/video-01-live",
          "--output", outPath,
        ],
        fetchFn,
      ),
    ).rejects.toThrow("process.exit(1)");

    const stderrOutput = stderrChunks.join("");
    expect(stderrOutput).toContain("pred-fail-123");
  });
});

// ---------------------------------------------------------------------------
// Output collision handling
// ---------------------------------------------------------------------------

describe("run() output collision", () => {
  test("existing out.mp4 causes output at out_1.mp4", async () => {
    const { fetchFn } = makeVideoFetch();
    const outPath = path.join(tmpDir, "out.mp4");

    fs.writeFileSync(outPath, "existing");

    await run(
      [
        "--image", testImagePath,
        "--prompt", "fly away",
        "--model", "minimax/video-01-live",
        "--output", outPath,
      ],
      fetchFn,
    );

    const collisionPath = path.join(tmpDir, "out_1.mp4");
    expect(fs.existsSync(collisionPath)).toBe(true);
    expect(fs.readFileSync(outPath, "utf8")).toBe("existing");
  });
});
