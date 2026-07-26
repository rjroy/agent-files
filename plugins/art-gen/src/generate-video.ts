import * as fs from "fs";
import * as path from "path";
import { createPrediction, waitForCompletion, downloadFile, imageToDataUri } from "./replicate-client.ts";
import { getVideoParams } from "./data/video-image-params.ts";

function makeOutputPath(base: string, idx: number): string {
  if (idx === 0) return base;
  const lastDot = base.lastIndexOf(".");
  if (lastDot === -1) return `${base}_${idx}`;
  return `${base.slice(0, lastDot)}_${idx}${base.slice(lastDot)}`;
}

function findFirstFreeIndex(base: string): number {
  let idx = 0;
  while (fs.existsSync(makeOutputPath(base, idx))) idx++;
  return idx;
}

export async function run(args: string[], fetchFn: typeof fetch = globalThis.fetch): Promise<void> {
  if (!process.env.REPLICATE_API_TOKEN) {
    process.stderr.write("Error: REPLICATE_API_TOKEN is not set. Get a token at replicate.com/account/api-tokens\n");
    process.exit(1);
  }

  let imagePath: string | undefined;
  let prompt: string | undefined;
  let model: string | undefined;
  let outputArg: string | undefined;
  let paramsJson: string | undefined;

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case "--image":
        imagePath = args[++i];
        break;
      case "--prompt":
        prompt = args[++i];
        break;
      case "--model":
        model = args[++i];
        break;
      case "--output":
        outputArg = args[++i];
        break;
      case "--params":
        paramsJson = args[++i];
        break;
    }
  }

  if (!imagePath) {
    process.stderr.write("Error: --image is required\n");
    process.exit(1);
  }

  if (!prompt) {
    process.stderr.write("Error: --prompt is required\n");
    process.exit(1);
  }

  if (!model) {
    process.stderr.write("Error: --model is required\n");
    process.exit(1);
  }

  if (!outputArg) {
    process.stderr.write("Error: --output is required\n");
    process.exit(1);
  }

  let extraParams: Record<string, unknown> = {};
  if (paramsJson !== undefined) {
    try {
      extraParams = JSON.parse(paramsJson);
    } catch {
      process.stderr.write("Error: --params value is not valid JSON\n");
      process.exit(1);
    }
  }

  process.stderr.write("Warning: Video generation costs $0.10–$1.50+ per video and takes 2–5 minutes.\n");

  const outputBase = path.resolve(process.cwd(), outputArg);
  const outputDir = path.dirname(outputBase);
  fs.mkdirSync(outputDir, { recursive: true });

  try {
    const dataUri = await imageToDataUri(imagePath);
    const params = getVideoParams(model);

    // Start with --params values, then override with named flags
    const input: Record<string, unknown> = { ...extraParams, prompt };

    if (params.isArray) {
      input[params.paramName] = [dataUri];
    } else {
      input[params.paramName] = dataUri;
    }

    process.stderr.write(`Submitting prediction to ${model}...\n`);
    const prediction = (await createPrediction(model, input, undefined, fetchFn)) as {
      id: string;
      status: string;
      output?: unknown;
    };

    let completed: { id: string; status: string; output?: unknown };
    try {
      completed = (await waitForCompletion(prediction.id, 10000, 600000, fetchFn)) as {
        id: string;
        status: string;
        output?: unknown;
      };
    } catch (err) {
      process.stderr.write(`Error: ${err instanceof Error ? err.message : String(err)}\n`);
      process.stderr.write(`Check prediction status at https://replicate.com/p/${prediction.id}\n`);
      process.exit(1);
    }

    const rawOutput = completed.output;
    const url = typeof rawOutput === "string" ? rawOutput : (rawOutput as string[])[0];

    const startIdx = findFirstFreeIndex(outputBase);
    const filePath = makeOutputPath(outputBase, startIdx);

    process.stderr.write("Downloading video output...\n");
    await downloadFile(url, filePath, fetchFn);
    process.stdout.write(`${filePath}\n`);
  } catch (err) {
    process.stderr.write(`Error: ${err instanceof Error ? err.message : String(err)}\n`);
    process.exit(1);
  }
}

if (import.meta.main) {
  run(process.argv.slice(2));
}
