import * as fs from "fs";
import * as path from "path";
import { createPrediction, waitForCompletion, downloadFile, imageToDataUri } from "./replicate-client.ts";

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
  let model: string | undefined;
  let outputArg: string | undefined;
  let paramsJson: string | undefined;

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case "--image":
        imagePath = args[++i];
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

  // Correct output extension to .png — background removal always produces PNG
  const rawOutput = outputArg as string;
  let correctedOutput = rawOutput;
  if (!rawOutput.toLowerCase().endsWith(".png")) {
    correctedOutput = rawOutput.replace(/\.[^.]+$/, ".png");
    process.stderr.write(`Note: Output extension corrected to .png (background removal always produces PNG)\n`);
  }

  const outputBase = path.resolve(process.cwd(), correctedOutput);
  const outputDir = path.dirname(outputBase);
  fs.mkdirSync(outputDir, { recursive: true });

  try {
    // Start with --params values, then override with image (named flag always wins)
    const input: Record<string, unknown> = { ...extraParams };
    input["image"] = await imageToDataUri(imagePath as string);

    process.stderr.write(`Submitting prediction to ${model as string}...\n`);
    let prediction = (await createPrediction(model as string, input, 60, fetchFn)) as {
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

    const outputUrl = prediction.output as string;

    const startIdx = findFirstFreeIndex(outputBase);
    const filePath = makeOutputPath(outputBase, startIdx);

    process.stderr.write(`Downloading output...\n`);
    await downloadFile(outputUrl, filePath, fetchFn);
    process.stdout.write(`${filePath}\n`);
  } catch (err) {
    process.stderr.write(`Error: ${err instanceof Error ? err.message : String(err)}\n`);
    process.exit(1);
  }
}

if (import.meta.main) {
  run(process.argv.slice(2));
}
