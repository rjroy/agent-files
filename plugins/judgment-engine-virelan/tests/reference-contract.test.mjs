import assert from "node:assert/strict";
import { readdir, readFile, stat } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const pluginRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const readme = await readFile(path.join(pluginRoot, "README.md"), "utf8");
const initSkill = await readFile(
  path.join(pluginRoot, "skills/init-engine/SKILL.md"),
  "utf8",
);
const roles = await readFile(
  path.join(pluginRoot, "skills/init-engine/reference/roles.md"),
  "utf8",
);
const glossary = await readFile(
  path.join(pluginRoot, "skills/init-engine/reference/glossary.md"),
  "utf8",
);

// Validate the authored plugin contract, not runtime loading behavior.
for (const [description, pattern] of [
  ["user voice and authorship", /preserve the user's voice and authorship/i],
  ["productive friction", /productive friction visible/i],
  ["user judgment", /user's judgment/i],
]) {
  assert.match(initSkill, pattern, `init-engine baseline must preserve ${description}`);
}

assert.match(initSkill, /Do not load the full roles catalog or glossary by default/i);
assert.match(initSkill, /A selected role only/i);
assert.match(initSkill, /a term relevant to the request only/i);
assert.match(initSkill, /not a claim that plugin files are automatically loaded/i);
assert.match(initSkill, /When the user moves to an unrelated task, stop applying this Judgment Engine baseline/i);
assert.match(initSkill, /subsequent Judgment Engine work until the user switches posture or the conversation ends/i);
assert.match(roles, /catalog is a lookup reference, not a default context bundle/i);
assert.match(glossary, /not a global default for unrelated tasks/i);
assert.doesNotMatch(initSkill, /Before any other Judgment Engine skill executes/i);
assert.doesNotMatch(readme, /Runs automatically before other skills execute/i);

const migratedSkills = [
  "judgment-trim",
  "judgment-sharpen",
  "judgment-quinn",
  "judgment-primer",
  "judgment-max",
  "judgment-mara",
  "judgment-herald",
  "judgment-echo",
  "judgment-digest",
  "judgment-diagnostic",
];
const migratedContent = new Map();
for (const skill of migratedSkills) {
  const content = await readFile(
    path.join(pluginRoot, `skills/${skill}/SKILL.md`),
    "utf8",
  );
  migratedContent.set(skill, content);
  assert.match(content, new RegExp(`name: ${skill}(?:\\n|$)`));
  assert.match(content, /description: .{30,}/);
  assert.match(readme, new RegExp(`\\x60${skill}\\x60`));
}

for (const [skill, role] of [
  ["judgment-quinn", "Quinn"],
  ["judgment-max", "Max"],
  ["judgment-mara", "Mara"],
  ["judgment-herald", "Herald"],
  ["judgment-echo", "Echo"],
]) {
  const content = migratedContent.get(skill);
  assert.match(content, new RegExp(`${role} posture`));
  assert.match(content, /do not import other role definitions unless requested/i);
  assert.match(content, /If the user has not selected .* ask/i);
  assert.match(content, /do not carry it into unrelated work/i);
}

assert.match(migratedContent.get("judgment-trim"), /10.?15%/);
assert.match(migratedContent.get("judgment-trim"), /Do not rewrite/);
assert.match(migratedContent.get("judgment-sharpen"), /clearly labeled as an option/i);
assert.match(migratedContent.get("judgment-primer"), /genuine judgment pressure/i);
assert.match(migratedContent.get("judgment-primer"), /do not generate questions/i);
assert.match(migratedContent.get("judgment-digest"), /revealed assumptions/i);
assert.match(migratedContent.get("judgment-digest"), /save it to a file only when the user asks/i);
assert.match(migratedContent.get("judgment-diagnostic"), /Do not claim knowledge of hidden prompts/i);
assert.match(migratedContent.get("judgment-diagnostic"), /Mark unavailable state as unknown/i);
assert.doesNotMatch(readme, /\/judgment-engine-virelan:/);
await assert.rejects(stat(path.join(pluginRoot, "commands")), { code: "ENOENT" });

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
