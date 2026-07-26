import * as fs from "fs";
import * as path from "path";
import { createPrediction, waitForCompletion, downloadFile } from "./replicate-client.ts";

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

  let prompt: string | undefined;
  let outputArg: string | undefined;
  let model = "black-forest-labs/flux-schnell";
  let aspectRatio: string | undefined;
  let width: number | undefined;
  let height: number | undefined;
  let numOutputs: number | undefined;
  let seed: number | undefined;
  let paramsJson: string | undefined;

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case "--prompt":
        prompt = args[++i];
        break;
      case "--output":
        outputArg = args[++i];
        break;
      case "--model":
        model = args[++i];
        break;
      case "--aspect-ratio":
        aspectRatio = args[++i];
        break;
      case "--width":
        width = Number(args[++i]);
        break;
      case "--height":
        height = Number(args[++i]);
        break;
      case "--num-outputs":
        numOutputs = Number(args[++i]);
        break;
      case "--seed":
        seed = Number(args[++i]);
        break;
      case "--params":
        paramsJson = args[++i];
        break;
    }
  }

  if (!prompt) {
    process.stderr.write("Error: --prompt is required\n");
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

  // Start with --params values, then override with named flags
  const input: Record<string, unknown> = { ...extraParams, prompt };

  if (aspectRatio !== undefined && (width !== undefined || height !== undefined)) {
    process.stderr.write("Warning: --aspect-ratio and --width/--height are both set; using aspect-ratio, ignoring dimensions\n");
  }

  if (aspectRatio !== undefined) {
    input.aspect_ratio = aspectRatio;
  } else {
    if (width !== undefined) input.width = width;
    if (height !== undefined) input.height = height;
  }

  if (numOutputs !== undefined) input.num_outputs = numOutputs;
  if (seed !== undefined) input.seed = seed;

  const outputBase = path.resolve(process.cwd(), outputArg);
  const outputDir = path.dirname(outputBase);
  fs.mkdirSync(outputDir, { recursive: true });

  try {
    process.stderr.write(`Submitting prediction to ${model}...\n`);
    let prediction = (await createPrediction(model, input, 60, fetchFn)) as {
      id: string;
      status: string;
      output?: unknown;
    };

    if (prediction.status !== "succeeded") {
      prediction = (await waitForCompletion(prediction.id, 3000, 300000, fetchFn)) as {
        id: string;
        status: string;
        output?: unknown;
      };
    }

    const rawOutput = prediction.output;
    const urls: string[] = Array.isArray(rawOutput) ? rawOutput : [rawOutput as string];

    const startIdx = findFirstFreeIndex(outputBase);

    for (let i = 0; i < urls.length; i++) {
      const filePath = makeOutputPath(outputBase, startIdx + i);
      process.stderr.write(`Downloading output ${i + 1} of ${urls.length}...\n`);
      await downloadFile(urls[i], filePath, fetchFn);
      process.stdout.write(`${filePath}\n`);
    }
  } catch (err) {
    process.stderr.write(`Error: ${err instanceof Error ? err.message : String(err)}\n`);
    process.exit(1);
  }
}

if (import.meta.main) {
  run(process.argv.slice(2));
}
