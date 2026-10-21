import assert from "node:assert/strict";
import { readFile, stat } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const pluginRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const readme = await readFile(path.join(pluginRoot, "README.md"), "utf8");

const migratedSkills = [
  "judgment-trim",
  "judgment-sharpen",
  "judgment-primer",
  "judgment-personas",
  "judgment-digest",
  "judgment-diagnostic",
];

for (const skill of migratedSkills) {
  const content = await readFile(
    path.join(pluginRoot, `skills/${skill}/SKILL.md`),
    "utf8",
  );
  const frontmatter = content.match(/^---\n([\s\S]*?)\n---/);
  assert.ok(frontmatter, `${skill} must have frontmatter`);
  assert.match(frontmatter[1], new RegExp(`^name: ${skill}$`, "m"));
  assert.match(frontmatter[1], /^description: .{30,}$/m);
  assert.ok(readme.includes(`\`${skill}\``), `${skill} must be listed in README`);
}

for (const skill of [
  "judgment-max",
  "judgment-quinn",
  "judgment-echo",
  "judgment-herald",
  "judgment-mara",
  "qa-runner",
  "writing-workshop",
]) {
  await assert.rejects(
    stat(path.join(pluginRoot, "skills", skill)),
    { code: "ENOENT" },
  );
}

await assert.rejects(stat(path.join(pluginRoot, "commands")), { code: "ENOENT" });
