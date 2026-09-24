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

const postureCommands = [
  ["quinn", "Quinn"],
  ["max", "Max"],
  ["mara", "Mara"],
  ["herald", "Herald"],
  ["echo", "Echo"],
];
for (const [command, role] of postureCommands) {
  const content = await readFile(path.join(pluginRoot, `commands/${command}.md`), "utf8");
  const [title] = content.split(/\r?\n/, 1);
  assert.match(title, new RegExp(`^Adopt ${role}'s posture:`));
  assert.match(content, new RegExp(`Within Judgment Engine work, embody only ${role}'s characteristics`));
  assert.match(content, /Do not apply other role definitions unless the user requests them/i);
  assert.match(content, new RegExp(`Maintain ${role}'s selected posture across subsequent Judgment Engine work`));
  assert.match(content, /When the user moves to an unrelated task, leave this plugin's scope/i);
  assert.match(content, new RegExp(`if Judgment Engine work resumes, ${role} remains selected unless switched`));
  assert.match(content, /not automatic runtime loading/i);
}

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
