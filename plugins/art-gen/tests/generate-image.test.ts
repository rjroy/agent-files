import { describe, test, expect, beforeEach, afterEach, spyOn } from "bun:test";
import * as os from "os";
import * as fs from "fs";
import * as path from "path";
import { run } from "../src/generate-image.ts";

let exitSpy: ReturnType<typeof spyOn>;
let tmpDir: string;

beforeEach(() => {
  process.env.REPLICATE_API_TOKEN = "test-token";
  const throwingExit = ((_code?: number): never => {
    throw new Error(`process.exit(${_code})`);
  }) as unknown as typeof process.exit;
  exitSpy = spyOn(process, "exit").mockImplementation(throwingExit);
  tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "art-gen-test-"));
});

afterEach(() => {
  exitSpy.mockRestore();
  fs.rmSync(tmpDir, { recursive: true, force: true });
});

function makeSuccessFetch(
  numOutputs = 1,
): { fetchFn: typeof fetch; getBody: () => { input: Record<string, unknown> } | null } {
  let capturedBody: { input: Record<string, unknown> } | null = null;
  let downloadCount = 0;

  const outputUrls = Array.from(
    { length: numOutputs },
    (_, i) => `https://example.com/output_${i}.png`,
  );

  const fetchFn = async (
    url: string | URL | Request,
    init?: RequestInit,
  ): Promise<Response> => {
    const urlStr = url.toString();

    if (init?.method === "POST") {
      capturedBody = JSON.parse(init.body as string) as {
        input: Record<string, unknown>;
      };
      return new Response(
        JSON.stringify({ id: "pred-123", status: "succeeded", output: outputUrls }),
        { status: 200 },
      );
    }

    // Binary download for any output URL
    if (urlStr.includes("example.com")) {
      downloadCount++;
      return new Response(new Uint8Array([0, 1, 2, 3]), { status: 200 });
    }

    // Fallback
    return new Response(new Uint8Array([0]), { status: 200 });
  };

  return { fetchFn, getBody: () => capturedBody };
}

describe("run() argument validation", () => {
  test("missing --prompt exits with code 1", async () => {
    const { fetchFn } = makeSuccessFetch();
    const outPath = path.join(tmpDir, "out.png");
    await expect(run(["--output", outPath], fetchFn)).rejects.toThrow("process.exit(1)");
  });

  test("missing --output exits with code 1", async () => {
    const { fetchFn } = makeSuccessFetch();
    await expect(run(["--prompt", "test prompt"], fetchFn)).rejects.toThrow("process.exit(1)");
  });

  test("invalid --params JSON exits with code 1", async () => {
    const { fetchFn } = makeSuccessFetch();
    const outPath = path.join(tmpDir, "out.png");
    await expect(
      run(["--prompt", "test", "--output", outPath, "--params", "{invalid}"], fetchFn),
    ).rejects.toThrow("process.exit(1)");
  });
});

describe("run() output path handling", () => {
  test("relative output path is resolved against cwd", async () => {
    const { fetchFn } = makeSuccessFetch();
    const relPath = "relative/out.png";
    const expectedPath = path.resolve(process.cwd(), relPath);

    try {
      await run(["--prompt", "test", "--output", relPath], fetchFn);
      expect(fs.existsSync(expectedPath)).toBe(true);
    } finally {
      const dir = path.resolve(process.cwd(), "relative");
      if (fs.existsSync(dir)) {
        fs.rmSync(dir, { recursive: true, force: true });
      }
    }
  });

  test("collision: existing out.png causes output at out_1.png", async () => {
    const { fetchFn } = makeSuccessFetch();
    const outPath = path.join(tmpDir, "out.png");

    // Pre-create out.png to trigger collision
    fs.writeFileSync(outPath, "existing");

    await run(["--prompt", "test", "--output", outPath], fetchFn);

    const collisionPath = path.join(tmpDir, "out_1.png");
    expect(fs.existsSync(collisionPath)).toBe(true);
    // Original must be untouched
    expect(fs.readFileSync(outPath, "utf8")).toBe("existing");
  });

  test("multi-output collision: out.png and out_1.png exist → outputs at out_2, out_3, out_4", async () => {
    const { fetchFn } = makeSuccessFetch(3);
    const outPath = path.join(tmpDir, "out.png");

    // Pre-create the first two collision slots
    fs.writeFileSync(outPath, "existing");
    fs.writeFileSync(path.join(tmpDir, "out_1.png"), "existing");

    await run(["--prompt", "test", "--output", outPath, "--num-outputs", "3"], fetchFn);

    expect(fs.existsSync(path.join(tmpDir, "out_2.png"))).toBe(true);
    expect(fs.existsSync(path.join(tmpDir, "out_3.png"))).toBe(true);
    expect(fs.existsSync(path.join(tmpDir, "out_4.png"))).toBe(true);
  });
});

describe("run() parameter forwarding", () => {
  test("--aspect-ratio wins over --width: body contains aspect_ratio, not width", async () => {
    let capturedInput: Record<string, unknown> | null = null;

    const fetchFn = async (
      _url: string | URL | Request,
      init?: RequestInit,
    ): Promise<Response> => {
      if (init?.method === "POST") {
        const body = JSON.parse(init.body as string) as { input: Record<string, unknown> };
        capturedInput = body.input;
        return new Response(
          JSON.stringify({ id: "p1", status: "succeeded", output: ["https://ex.com/img.png"] }),
          { status: 200 },
        );
      }
      return new Response(new Uint8Array([0]), { status: 200 });
    };

    const outPath = path.join(tmpDir, "out.png");
    await run(
      ["--prompt", "test", "--output", outPath, "--aspect-ratio", "16:9", "--width", "1024"],
      fetchFn,
    );

    expect(capturedInput?.aspect_ratio).toBe("16:9");
    expect(capturedInput?.width).toBeUndefined();
  });

  test("--params values are included in the POST body", async () => {
    const { fetchFn, getBody } = makeSuccessFetch();
    const outPath = path.join(tmpDir, "out.png");

    await run(
      [
        "--prompt",
        "test",
        "--output",
        outPath,
        "--params",
        JSON.stringify({ guidance_scale: 7.5, steps: 20 }),
      ],
      fetchFn,
    );

    const body = getBody();
    expect(body?.input.guidance_scale).toBe(7.5);
    expect(body?.input.steps).toBe(20);
  });

  test("prompt is forwarded in POST body", async () => {
    const { fetchFn, getBody } = makeSuccessFetch();
    const outPath = path.join(tmpDir, "out.png");

    await run(["--prompt", "a beautiful sunset", "--output", outPath], fetchFn);

    const body = getBody();
    expect(body?.input.prompt).toBe("a beautiful sunset");
  });
});
