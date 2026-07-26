import { describe, test, expect, beforeEach } from "bun:test";
import * as os from "os";
import * as fs from "fs";
import * as path from "path";
import {
  createPrediction,
  waitForCompletion,
  downloadFile,
  imageToDataUri,
} from "../src/replicate-client.ts";

beforeEach(() => {
  process.env.REPLICATE_API_TOKEN = "test-token";
});

function mockFetch(
  responses: Array<{ status: number; body?: unknown }>,
): typeof fetch {
  let callIndex = 0;
  return async (_url: string | URL | Request, _init?: RequestInit) => {
    const response = responses[callIndex++] ?? responses[responses.length - 1];
    if (response.status === 0) throw new TypeError("network error");
    return new Response(JSON.stringify(response.body ?? null), {
      status: response.status,
      statusText: statusText(response.status),
    });
  };
}

function statusText(status: number): string {
  const map: Record<number, string> = {
    200: "OK",
    401: "Unauthorized",
    404: "Not Found",
    429: "Too Many Requests",
    500: "Internal Server Error",
  };
  return map[status] ?? String(status);
}

describe("createPrediction", () => {
  test("successful prediction returns object with id", async () => {
    const fetch = mockFetch([
      {
        status: 200,
        body: { id: "pred-1", status: "succeeded", output: ["https://example.com/img.png"] },
      },
    ]);
    const result = (await createPrediction("owner/model", { prompt: "test" }, undefined, fetch)) as {
      id: string;
    };
    expect(result.id).toBe("pred-1");
  });

  test("401 auth failure throws with 401 in message", async () => {
    const fetch = mockFetch([{ status: 401 }]);
    await expect(
      createPrediction("owner/model", { prompt: "test" }, undefined, fetch),
    ).rejects.toThrow("401");
  });

  test("404 model not found throws with 404 in message", async () => {
    const fetch = mockFetch([{ status: 404 }]);
    await expect(
      createPrediction("owner/model", { prompt: "test" }, undefined, fetch),
    ).rejects.toThrow("404");
  });

  test("429 rate limiting throws with 429 in message", async () => {
    const fetch = mockFetch([{ status: 429 }]);
    await expect(
      createPrediction("owner/model", { prompt: "test" }, undefined, fetch),
    ).rejects.toThrow("429");
  });

  test("network error rejects", async () => {
    const fetch = mockFetch([{ status: 0 }]);
    await expect(
      createPrediction("owner/model", { prompt: "test" }, undefined, fetch),
    ).rejects.toThrow(TypeError);
  });

  test("waitSeconds provided sends Prefer header", async () => {
    let capturedInit: RequestInit | undefined;
    const capturingFetch: typeof globalThis.fetch = async (
      _url: string | URL | Request,
      init?: RequestInit,
    ) => {
      capturedInit = init;
      return new Response(
        JSON.stringify({ id: "pred-2", status: "succeeded", output: [] }),
        { status: 200 },
      );
    };

    await createPrediction("owner/model", { prompt: "test" }, 60, capturingFetch);

    const headers = capturedInit?.headers as Record<string, string>;
    expect(headers["Prefer"]).toBe("wait=60");
  });

  test("no waitSeconds sends no Prefer header", async () => {
    let capturedInit: RequestInit | undefined;
    const capturingFetch: typeof globalThis.fetch = async (
      _url: string | URL | Request,
      init?: RequestInit,
    ) => {
      capturedInit = init;
      return new Response(
        JSON.stringify({ id: "pred-3", status: "succeeded", output: [] }),
        { status: 200 },
      );
    };

    await createPrediction("owner/model", { prompt: "test" }, undefined, capturingFetch);

    const headers = capturedInit?.headers as Record<string, string>;
    expect(headers["Prefer"]).toBeUndefined();
  });
});

describe("waitForCompletion", () => {
  test("times out when prediction never completes", async () => {
    const fetch = mockFetch([
      { status: 200, body: { id: "pred-timeout", status: "processing" } },
    ]);
    await expect(
      waitForCompletion("pred-timeout", 10, 50, fetch),
    ).rejects.toThrow("pred-timeout");
  });

  test("resolves when prediction succeeds on second poll", async () => {
    const fetch = mockFetch([
      { status: 200, body: { id: "pred-poll", status: "processing" } },
      { status: 200, body: { id: "pred-poll", status: "succeeded", output: ["url"] } },
    ]);
    const result = (await waitForCompletion("pred-poll", 10, 5000, fetch)) as {
      status: string;
    };
    expect(result.status).toBe("succeeded");
  });

  test("rejects when prediction fails", async () => {
    const fetch = mockFetch([
      { status: 200, body: { id: "pred-fail", status: "failed" } },
    ]);
    await expect(
      waitForCompletion("pred-fail", 10, 5000, fetch),
    ).rejects.toThrow("pred-fail");
  });
});

describe("downloadFile", () => {
  test("downloads binary content and returns byte count", async () => {
    const bytes = new Uint8Array([1, 2, 3]);
    const capturingFetch: typeof globalThis.fetch = async () => {
      return new Response(bytes);
    };

    const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "art-gen-test-"));
    const outputPath = path.join(tmpDir, "output.bin");

    const bytesWritten = await downloadFile("https://example.com/file", outputPath, capturingFetch);

    expect(bytesWritten).toBe(3);

    const written = fs.readFileSync(outputPath);
    expect(written.length).toBe(3);

    fs.rmSync(tmpDir, { recursive: true });
  });
});

describe("imageToDataUri", () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "art-gen-test-"));

  test("PNG file returns png data URI", async () => {
    const filePath = path.join(tmpDir, "test.png");
    fs.writeFileSync(filePath, new Uint8Array([137, 80, 78, 71]));
    const result = await imageToDataUri(filePath);
    expect(result.startsWith("data:image/png;base64,")).toBe(true);
  });

  test("JPEG file returns jpeg data URI", async () => {
    const filePath = path.join(tmpDir, "test.jpg");
    fs.writeFileSync(filePath, new Uint8Array([255, 216, 255, 224]));
    const result = await imageToDataUri(filePath);
    expect(result.startsWith("data:image/jpeg;base64,")).toBe(true);
  });

  test("WebP file returns webp data URI", async () => {
    const filePath = path.join(tmpDir, "test.webp");
    fs.writeFileSync(filePath, new Uint8Array([82, 73, 70, 70]));
    const result = await imageToDataUri(filePath);
    expect(result.startsWith("data:image/webp;base64,")).toBe(true);
  });

  test("unsupported extension rejects", async () => {
    const filePath = path.join(tmpDir, "test.gif");
    fs.writeFileSync(filePath, new Uint8Array([71, 73, 70, 56]));
    await expect(imageToDataUri(filePath)).rejects.toThrow(".gif");
  });
});
