const API_BASE = "https://api.replicate.com/v1";

function authHeaders(): Record<string, string> {
  return {
    Authorization: `Token ${process.env.REPLICATE_API_TOKEN}`,
    "Content-Type": "application/json",
  };
}

async function assertOk(response: Response): Promise<void> {
  if (!response.ok) {
    throw new Error(`Replicate API error: ${response.status} ${response.statusText}`);
  }
}

export async function createPrediction(
  model: string,
  input: Record<string, unknown>,
  waitSeconds?: number,
  fetchFn: typeof fetch = globalThis.fetch,
): Promise<unknown> {
  const [owner, name] = model.split("/");
  const url = `${API_BASE}/models/${owner}/${name}/predictions`;

  const headers: Record<string, string> = authHeaders();
  if (waitSeconds && waitSeconds > 0) {
    headers["Prefer"] = `wait=${waitSeconds}`;
  }

  const response = await fetchFn(url, {
    method: "POST",
    headers,
    body: JSON.stringify({ input }),
  });

  await assertOk(response);
  return response.json();
}

export async function waitForCompletion(
  id: string,
  intervalMs: number,
  maxMs: number,
  fetchFn: typeof fetch = globalThis.fetch,
): Promise<unknown> {
  const url = `${API_BASE}/predictions/${id}`;
  const headers = authHeaders();
  const start = Date.now();

  while (true) {
    if (Date.now() - start >= maxMs) {
      throw new Error(`Prediction ${id} timed out after ${maxMs}ms`);
    }

    const response = await fetchFn(url, { headers });
    await assertOk(response);

    const prediction = (await response.json()) as { status: string; id: string };
    const { status } = prediction;

    process.stderr.write(`[${id}] status: ${status}\n`);

    if (status === "succeeded") {
      return prediction;
    }

    if (status === "failed" || status === "canceled") {
      throw new Error(`Prediction ${id} ended with status: ${status}`);
    }

    await new Promise((resolve) => setTimeout(resolve, intervalMs));
  }
}

export async function downloadFile(
  url: string,
  outputPath: string,
  fetchFn: typeof fetch = globalThis.fetch,
): Promise<number> {
  const response = await fetchFn(url);
  await assertOk(response);

  const buffer = await response.arrayBuffer();
  await Bun.write(outputPath, buffer);
  return buffer.byteLength;
}

export async function imageToDataUri(filePath: string): Promise<string> {
  const ext = filePath.slice(filePath.lastIndexOf(".")).toLowerCase();

  const mimeTypes: Record<string, string> = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
  };

  const mime = mimeTypes[ext];
  if (!mime) {
    throw new Error(`Unsupported image extension: ${ext}`);
  }

  const file = Bun.file(filePath);
  const buffer = await file.arrayBuffer();
  const b64 = Buffer.from(buffer).toString("base64");
  return `data:${mime};base64,${b64}`;
}
