import { describe, test, expect, beforeEach, afterEach, spyOn } from "bun:test";
import * as os from "os";
import * as fs from "fs";
import * as path from "path";
import { run } from "../src/remove-background.ts";

// --- Fixtures ---

let tmpDir: string;
let testImagePath: string;
let exitSpy: ReturnType<typeof spyOn>;

beforeEach(() => {
  process.env.REPLICATE_API_TOKEN = "test-token";
  exitSpy = spyOn(process, "exit").mockImplementation((code?: number) => {
    throw new Error(`process.exit(${code})`);
  });
  tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "rmbg-test-"));
  testImagePath = path.join(tmpDir, "input.png");
  // Minimal PNG header bytes
  fs.writeFileSync(testImagePath, Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]));
});

afterEach(() => {
  exitSpy.mockRestore();
  fs.rmSync(tmpDir, { recursive: true, force: true });
});

// --- Mock fetch factory ---

function makeRmbgFetch(outputUrl = "https://example.com/nobg.png") {
  const fetchFn = async (url: string | URL | Request, init?: RequestInit): Promise<Response> => {
    if (init?.method === "POST") {
      return new Response(
        JSON.stringify({ id: "rmbg-1", status: "succeeded", output: outputUrl }),
        { status: 200 },
      );
    }
    // Binary download
    return new Response(new Uint8Array([0, 1, 2, 3]), { status: 200 });
  };
  return fetchFn;
}

// --- Missing required args ---

describe("missing required args", () => {
  test("missing --image exits 1", async () => {
    await expect(
      run([
        "--model", "lucataco/remove-bg",
        "--output", path.join(tmpDir, "out.png"),
      ]),
    ).rejects.toThrow("process.exit(1)");
  });

  test("missing --model exits 1", async () => {
    await expect(
      run([
        "--image", testImagePath,
        "--output", path.join(tmpDir, "out.png"),
      ]),
    ).rejects.toThrow("process.exit(1)");
  });

  test("missing --output exits 1", async () => {
    await expect(
      run([
        "--image", testImagePath,
        "--model", "lucataco/remove-bg",
      ]),
    ).rejects.toThrow("process.exit(1)");
  });
});

// --- Extension correction ---

describe("non-PNG extension corrected to .png", () => {
  test("output file created ends with .png when .jpg passed", async () => {
    const fetchFn = makeRmbgFetch();
    const outputJpg = path.join(tmpDir, "result.jpg");

    const stderrMessages: string[] = [];
    const origWrite = process.stderr.write.bind(process.stderr);
    process.stderr.write = (chunk: string | Uint8Array): boolean => {
      stderrMessages.push(chunk.toString());
      return true;
    };

    try {
      await run(
        [
          "--image", testImagePath,
          "--model", "lucataco/remove-bg",
          "--output", outputJpg,
        ],
        fetchFn,
      );
    } finally {
      process.stderr.write = origWrite;
    }

    const expectedPng = path.join(tmpDir, "result.png");
    expect(fs.existsSync(expectedPng)).toBe(true);
    expect(fs.existsSync(outputJpg)).toBe(false);
  });

  test("stderr note contains .png when extension corrected", async () => {
    const fetchFn = makeRmbgFetch();
    const outputJpg = path.join(tmpDir, "result.jpg");

    const stderrMessages: string[] = [];
    const origWrite = process.stderr.write.bind(process.stderr);
    process.stderr.write = (chunk: string | Uint8Array): boolean => {
      stderrMessages.push(chunk.toString());
      return true;
    };

    try {
      await run(
        [
          "--image", testImagePath,
          "--model", "lucataco/remove-bg",
          "--output", outputJpg,
        ],
        fetchFn,
      );
    } finally {
      process.stderr.write = origWrite;
    }

    expect(stderrMessages.some((m) => m.includes(".png"))).toBe(true);
  });

  test("no correction note when extension is already .png", async () => {
    const fetchFn = makeRmbgFetch();
    const outputPng = path.join(tmpDir, "result.png");

    const stderrMessages: string[] = [];
    const origWrite = process.stderr.write.bind(process.stderr);
    process.stderr.write = (chunk: string | Uint8Array): boolean => {
      stderrMessages.push(chunk.toString());
      return true;
    };

    try {
      await run(
        [
          "--image", testImagePath,
          "--model", "lucataco/remove-bg",
          "--output", outputPng,
        ],
        fetchFn,
      );
    } finally {
      process.stderr.write = origWrite;
    }

    expect(stderrMessages.some((m) => m.toLowerCase().includes("corrected"))).toBe(false);
  });
});

// --- Output file collision ---

describe("output file collision", () => {
  test("creates result_1.png when result.png already exists", async () => {
    const fetchFn = makeRmbgFetch();
    const outputPath = path.join(tmpDir, "result.png");

    // Pre-create the collision file
    fs.writeFileSync(outputPath, "existing content");

    await run(
      [
        "--image", testImagePath,
        "--model", "lucataco/remove-bg",
        "--output", outputPath,
      ],
      fetchFn,
    );

    const suffixedPath = path.join(tmpDir, "result_1.png");
    expect(fs.existsSync(suffixedPath)).toBe(true);
    // Original untouched
    expect(fs.readFileSync(outputPath, "utf8")).toBe("existing content");
  });
});

// --- Successful flow: output path written to stdout ---

describe("successful flow", () => {
  test("output file path is written to stdout", async () => {
    const fetchFn = makeRmbgFetch();
    const outputPath = path.join(tmpDir, "out.png");

    const stdoutMessages: string[] = [];
    const origStdout = process.stdout.write.bind(process.stdout);
    process.stdout.write = (chunk: string | Uint8Array): boolean => {
      stdoutMessages.push(chunk.toString());
      return true;
    };

    try {
      await run(
        [
          "--image", testImagePath,
          "--model", "lucataco/remove-bg",
          "--output", outputPath,
        ],
        fetchFn,
      );
    } finally {
      process.stdout.write = origStdout;
    }

    expect(stdoutMessages.some((m) => m.includes(outputPath))).toBe(true);
  });

  test("output file is created on disk", async () => {
    const fetchFn = makeRmbgFetch();
    const outputPath = path.join(tmpDir, "out.png");

    await run(
      [
        "--image", testImagePath,
        "--model", "lucataco/remove-bg",
        "--output", outputPath,
      ],
      fetchFn,
    );

    expect(fs.existsSync(outputPath)).toBe(true);
  });
});
