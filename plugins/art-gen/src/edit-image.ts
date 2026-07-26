import * as fs from "fs";
import * as path from "path";
import { createPrediction, waitForCompletion, downloadFile, imageToDataUri } from "./replicate-client.ts";
import { getImg2ImgParams } from "./data/img2img-image-params.ts";

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
  let strength = 0.75;
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
      case "--strength":
        strength = parseFloat(args[++i]);
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
      process.stderr.write(`Error: --params is not valid JSON: ${paramsJson}\n`);
      process.exit(1);
    }
  }

  try {
    const resolvedImagePath = path.resolve(process.cwd(), imagePath);
    const dataUri = await imageToDataUri(resolvedImagePath);

    const params = getImg2ImgParams(model);

    // Start with --params values, then override with named flags
    const input: Record<string, unknown> = { ...extraParams };

    if (params.isArray) {
      input[params.paramName] = [dataUri];
    } else {
      input[params.paramName] = dataUri;
    }

    // Named flags override --params
    input["prompt"] = prompt;
    if (params.strengthParam !== null) {
      input[params.strengthParam] = strength;
    }

    process.stderr.write(`Starting prediction for model: ${model}\n`);
    const prediction = (await createPrediction(model, input, 60, fetchFn)) as {
      id: string;
      status: string;
      output?: unknown;
    };

    let finalPrediction = prediction;
    if (prediction.status !== "succeeded") {
      finalPrediction = (await waitForCompletion(prediction.id, 3000, 300000, fetchFn)) as typeof prediction;
    }

    const outputUrls = Array.isArray(finalPrediction.output)
      ? (finalPrediction.output as string[])
      : [finalPrediction.output as string];

    const outputBase = path.resolve(process.cwd(), outputArg);
    const outputDir = path.dirname(outputBase);
    fs.mkdirSync(outputDir, { recursive: true });

    const startIdx = findFirstFreeIndex(outputBase);
    const outputPath = makeOutputPath(outputBase, startIdx);

    const url = outputUrls[0];
    process.stderr.write(`Downloading output to: ${outputPath}\n`);
    await downloadFile(url, outputPath, fetchFn);
    process.stdout.write(`${outputPath}\n`);
  } catch (err) {
    process.stderr.write(`Error: ${err instanceof Error ? err.message : String(err)}\n`);
    process.exit(1);
  }
}

if (import.meta.main) {
  run(process.argv.slice(2));
}
