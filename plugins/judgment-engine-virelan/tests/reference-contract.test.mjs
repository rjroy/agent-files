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
assert.match(initSkill, /load only the selected persona's reference/i);
assert.match(initSkill, /a term relevant to the request only/i);
assert.match(initSkill, /not a claim that plugin files are automatically loaded/i);
assert.match(initSkill, /When the user moves to an unrelated task, stop applying this Judgment Engine baseline/i);
assert.match(initSkill, /explicitly switches persona or returns to normal/i);
assert.match(roles, /catalog is a lookup reference, not a default context bundle/i);
assert.match(roles, /do not automatically select one/i);
assert.match(roles, /replaces, rather than blends, persona instructions/i);
assert.match(glossary, /not a global default for unrelated tasks/i);
assert.doesNotMatch(initSkill, /Before any other Judgment Engine skill executes/i);
assert.doesNotMatch(readme, /Runs automatically before other skills execute/i);

const migratedSkills = [
  "judgment-trim",
  "judgment-sharpen",
  "judgment-primer",
  "judgment-personas",
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

const personaSkill = migratedContent.get("judgment-personas");
assert.match(personaSkill, /Quinn, Max, Echo, Herald, and Mara/);
assert.match(readme, /`judgment-personas`/);
assert.match(personaSkill, /If the user has not selected a persona, ask a concise question/i);
assert.match(personaSkill, /Load only the selected persona's reference file/i);
assert.match(personaSkill, /remains active for relevant Judgment Engine work in this conversation/i);
assert.match(personaSkill, /explicitly switches persona or returns to normal/i);
assert.match(personaSkill, /preserve the conversation's subject and useful context/i);
assert.match(personaSkill, /replace the prior persona instructions/i);
assert.match(personaSkill, /Never blend personas/i);
assert.match(personaSkill, /multiple perspectives/i);
assert.match(personaSkill, /not independent agents/i);

for (const [persona, distinctive] of [
  ["quinn", /retrospective-quality questions/i],
  ["max", /challenge comfortable assumptions/i],
  ["echo", /do not rephrase for polish/i],
  ["herald", /earned confidence/i],
  ["mara", /Treat emotion as signal, not noise/i],
]) {
  const reference = await readFile(
    path.join(pluginRoot, `skills/judgment-personas/reference/${persona}.md`),
    "utf8",
  );
  assert.match(reference, new RegExp(`# ${persona[0].toUpperCase()}${persona.slice(1)} posture`));
  assert.match(reference, distinctive, `${persona} guidance must be preserved`);
  assert.match(personaSkill, new RegExp(`reference/${persona}\\.md`));
}

for (const skill of ["judgment-max", "judgment-quinn", "judgment-echo", "judgment-herald", "judgment-mara"]) {
  await assert.rejects(
    stat(path.join(pluginRoot, "skills", skill)),
    { code: "ENOENT" },
    `obsolete discoverable skill ${skill} must not exist`,
  );
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
