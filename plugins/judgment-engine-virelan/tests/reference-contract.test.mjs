import assert from "node:assert/strict";
import { readdir, readFile, stat } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const pluginRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const readme = await readFile(path.join(pluginRoot, "README.md"), "utf8");

const aliases = [
  ["Inquiry Digest", "digest"],
  ["Judgment Primer", "primer"],
  ["System Diagnostic Report", "diagnostic"],
];

for (const [alias, command] of aliases) {
  const artifact = `commands/${command}.md`;
  const invocation = `/judgment-engine-virelan:${command}`;
  await stat(path.join(pluginRoot, artifact));
  assert.ok(
    readme.includes(`| ${alias} | \`${artifact}\` | \`${invocation}\` |`),
    `${alias} must document its artifact and canonical invocation`,
  );
}

const removedSkillDirectories = ["qa-runner", "writing-workshop"];
for (const skill of removedSkillDirectories) {
  await assert.rejects(
    stat(path.join(pluginRoot, "skills", skill)),
    { code: "ENOENT" },
    `removed skill directory ${skill} must not exist`,
  );
}

const staleReferences = [
  ["Q&A", "Runner"].join(" "),
  ["Writing", "Workshop"].join(" "),
  "qa-runner",
  "writing-workshop",
  "Prep Tech Writer",
  "API Walkthrough",
  "Document Spine Analyzer",
  "Slide Cut Protocol",
];

async function markdownFiles(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const nested = await Promise.all(
    entries.map(async (entry) => {
      const fullPath = path.join(directory, entry.name);
      if (entry.isDirectory()) return markdownFiles(fullPath);
      return entry.isFile() && entry.name.endsWith(".md") ? [fullPath] : [];
    }),
  );
  return nested.flat();
}

for (const file of await markdownFiles(pluginRoot)) {
  const content = await readFile(file, "utf8");
  for (const phrase of staleReferences) {
    assert.ok(
      !content.toLowerCase().includes(phrase.toLowerCase()),
      `${path.relative(pluginRoot, file)} contains stale reference: ${phrase}`,
    );
  }
}

console.log("Plugin reference contract passed.");
