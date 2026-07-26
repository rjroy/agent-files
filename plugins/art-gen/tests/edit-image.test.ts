import { describe, test, expect, beforeEach, afterEach, spyOn } from "bun:test";
import * as os from "os";
import * as fs from "fs";
import * as path from "path";
import { run } from "../src/edit-image.ts";

// --- Fixtures ---

let tmpDir: string;
let testImagePath: string;
let exitSpy: ReturnType<typeof spyOn>;

beforeEach(() => {
  process.env.REPLICATE_API_TOKEN = "test-token";
  exitSpy = spyOn(process, "exit").mockImplementation((code?: number) => {
    throw new Error(`process.exit(${code})`);
  });
  tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "edit-image-test-"));
  testImagePath = path.join(tmpDir, "test.png");
  // Minimal PNG header bytes
  fs.writeFileSync(testImagePath, Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]));
});

afterEach(() => {
  exitSpy.mockRestore();
  fs.rmSync(tmpDir, { recursive: true, force: true });
});

// --- Mock fetch factory ---

function makeMockFetch(outputUrl = "https://example.com/result.png") {
  let capturedInput: Record<string, unknown> | null = null;

  const fetchFn = async (url: string | URL | Request, init?: RequestInit): Promise<Response> => {
    if (init?.method === "POST") {
      const body = JSON.parse(init.body as string) as { input: Record<string, unknown> };
      capturedInput = body.input;
      return new Response(
        JSON.stringify({ id: "pred-1", status: "succeeded", output: [outputUrl] }),
        { status: 200 },
      );
    }
    // Binary download
    return new Response(new Uint8Array([0, 1, 2, 3]), { status: 200 });
  };

  return { fetchFn, get capturedInput() { return capturedInput; } };
}

// --- Missing required args ---

describe("missing required args", () => {
  test("missing --image exits 1", async () => {
    await expect(
      run([
        "--prompt", "make it better",
        "--model", "black-forest-labs/flux-2-pro",
        "--output", path.join(tmpDir, "out.png"),
      ]),
    ).rejects.toThrow("process.exit(1)");
  });

  test("missing --prompt exits 1", async () => {
    await expect(
      run([
        "--image", testImagePath,
        "--model", "black-forest-labs/flux-2-pro",
        "--output", path.join(tmpDir, "out.png"),
      ]),
    ).rejects.toThrow("process.exit(1)");
  });

  test("missing --model exits 1", async () => {
    await expect(
      run([
        "--image", testImagePath,
        "--prompt", "make it better",
        "--output", path.join(tmpDir, "out.png"),
      ]),
    ).rejects.toThrow("process.exit(1)");
  });

  test("missing --output exits 1", async () => {
    await expect(
      run([
        "--image", testImagePath,
        "--prompt", "make it better",
        "--model", "black-forest-labs/flux-2-pro",
      ]),
    ).rejects.toThrow("process.exit(1)");
  });
});

// --- flux-2-pro: isArray true ---

describe("flux-2-pro (isArray: true)", () => {
  test("sets input_images as array containing data URI", async () => {
    const mock = makeMockFetch();
    const outputPath = path.join(tmpDir, "out.png");

    await run(
      [
        "--image", testImagePath,
        "--prompt", "make it better",
        "--model", "black-forest-labs/flux-2-pro",
        "--output", outputPath,
      ],
      mock.fetchFn,
    );

    expect(Array.isArray(mock.capturedInput!.input_images)).toBe(true);
    expect((mock.capturedInput!.input_images as string[])[0]).toStartWith("data:image/png;base64,");
  });
});

// --- stability-ai/stable-diffusion-img2img: isArray false ---

describe("stability-ai/stable-diffusion-img2img (isArray: false)", () => {
  test("sets image as scalar data URI string, not an array", async () => {
    const mock = makeMockFetch();
    const outputPath = path.join(tmpDir, "out.png");

    await run(
      [
        "--image", testImagePath,
        "--prompt", "make it better",
        "--model", "stability-ai/stable-diffusion-img2img",
        "--output", outputPath,
      ],
      mock.fetchFn,
    );

    expect(typeof mock.capturedInput!.image).toBe("string");
    expect(Array.isArray(mock.capturedInput!.image)).toBe(false);
    expect((mock.capturedInput!.image as string)).toStartWith("data:image/png;base64,");
  });
});

// --- Unknown model: defaults to scalar image ---

describe("unknown model", () => {
  test("defaults to scalar image data URI", async () => {
    const mock = makeMockFetch();
    const outputPath = path.join(tmpDir, "out.png");

    await run(
      [
        "--image", testImagePath,
        "--prompt", "make it better",
        "--model", "unknown/model-xyz",
        "--output", outputPath,
      ],
      mock.fetchFn,
    );

    expect(typeof mock.capturedInput!.image).toBe("string");
    expect((mock.capturedInput!.image as string)).toStartWith("data:image/png;base64,");
  });
});

// --- strengthParam: null → no strength key ---

describe("flux-2-pro (strengthParam: null)", () => {
  test("does not include prompt_strength in prediction input", async () => {
    const mock = makeMockFetch();
    const outputPath = path.join(tmpDir, "out.png");

    await run(
      [
        "--image", testImagePath,
        "--prompt", "make it better",
        "--model", "black-forest-labs/flux-2-pro",
        "--output", outputPath,
      ],
      mock.fetchFn,
    );

    expect(mock.capturedInput!.input_images).toBeDefined();
    expect(mock.capturedInput!.prompt_strength).toBeUndefined();
  });
});

// --- strengthParam set → strength value sent ---

describe("stability-ai/stable-diffusion-img2img (strengthParam: 'prompt_strength')", () => {
  test("includes prompt_strength: 0.75 in prediction input", async () => {
    const mock = makeMockFetch();
    const outputPath = path.join(tmpDir, "out.png");

    await run(
      [
        "--image", testImagePath,
        "--prompt", "make it better",
        "--model", "stability-ai/stable-diffusion-img2img",
        "--output", outputPath,
      ],
      mock.fetchFn,
    );

    expect(mock.capturedInput!.prompt_strength).toBe(0.75);
  });
});

// --- Output file collision → _1 suffix ---

describe("output file collision", () => {
  test("creates out_1.png when out.png already exists", async () => {
    const mock = makeMockFetch();
    const outputPath = path.join(tmpDir, "out.png");

    // Pre-create the collision file
    fs.writeFileSync(outputPath, "existing content");

    await run(
      [
        "--image", testImagePath,
        "--prompt", "make it better",
        "--model", "black-forest-labs/flux-2-pro",
        "--output", outputPath,
      ],
      mock.fetchFn,
    );

    const suffixedPath = path.join(tmpDir, "out_1.png");
    expect(fs.existsSync(suffixedPath)).toBe(true);
  });
});
