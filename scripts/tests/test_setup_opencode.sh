#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
setup_script="$repo_dir/scripts/setup-opencode.sh"
temp_dir="$(mktemp -d)"
trap 'rm -rf "$temp_dir"' EXIT

config_dir="$temp_dir/config/opencode"
mkdir -p "$config_dir"
cat >"$config_dir/opencode.json" <<'JSON'
{
  "skills": ["/existing/skills", "https://example.test/skills"]
}
JSON

XDG_CONFIG_HOME="$temp_dir/config" "$setup_script" >"$temp_dir/first.out"

node - "$config_dir/opencode.json" "$repo_dir/plugins" "$config_dir" <<'NODE'
const fs = require("node:fs");
const path = require("node:path");

const [configFile, pluginsDir, configDir] = process.argv.slice(2);
const config = JSON.parse(fs.readFileSync(configFile, "utf8"));
const expectedSkills = ["/existing/skills", "https://example.test/skills"];
if (JSON.stringify(config.skills) !== JSON.stringify(expectedSkills)) {
  throw new Error(`existing skills config was not preserved: ${JSON.stringify(config.skills)}`);
}

const repositoryDir = path.dirname(pluginsDir);
const skillCollections = [
  ".agents/skills",
  "skills",
  "plugins/art-gen/skills",
  "plugins/audio-analysis/skills",
  "plugins/field-guide/skills",
  "plugins/judgment-engine-virelan/skills",
  "plugins/lore-development/skills",
  "plugins/music-engine-rowan/skills",
  "plugins/personal/skills",
  "plugins/story-engine-wyrd/skills",
];
const skillSources = skillCollections.flatMap((collection) => {
  const collectionDir = path.join(repositoryDir, collection);
  if (!fs.existsSync(collectionDir)) return [];
  return fs.readdirSync(collectionDir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory() && fs.existsSync(path.join(collectionDir, entry.name, "SKILL.md")))
    .map((entry) => path.join(collectionDir, entry.name));
});
if (skillSources.length !== 48) throw new Error(`expected 48 skills, found ${skillSources.length}`);
for (const sourceDir of skillSources) {
  const target = path.join(configDir, "skills", path.basename(sourceDir));
  if (!fs.lstatSync(target).isSymbolicLink()) throw new Error(`${target} is not a skill symlink`);
  if (fs.realpathSync(target) !== fs.realpathSync(sourceDir)) {
    throw new Error(`${target} does not point to its source skill directory`);
  }
}

const refactorSource = path.join(repositoryDir, "plugins/lore-development/skills/refactor");
const refactorTarget = path.join(configDir, "skills/refactor");
if (!fs.lstatSync(refactorTarget).isSymbolicLink()) {
  throw new Error(`${refactorTarget} is not a refactor skill symlink`);
}
if (fs.realpathSync(refactorTarget) !== fs.realpathSync(refactorSource)) {
  throw new Error(`${refactorTarget} does not point to the refactor skill source`);
}

const skillSymlinkNames = fs.readdirSync(path.join(configDir, "skills"), { withFileTypes: true })
  .filter((entry) => entry.isSymbolicLink())
  .map((entry) => entry.name);
for (const removedSkill of ["qa-runner", "writing-workshop", "plan-breakdown"]) {
  if (skillSymlinkNames.includes(removedSkill)) {
    throw new Error(`removed skill ${removedSkill} is still in the OpenCode skill symlink inventory`);
  }
}

for (const [collection, prefix] of [
  ["music-engine-rowan", "music-engine-rowan-"],
  ["story-engine-wyrd", "story-engine-wyrd-"],
]) {
  const sourceDir = path.join(pluginsDir, collection, "agents");
  for (const sourceName of fs.readdirSync(sourceDir).filter((name) => name.endsWith(".md"))) {
    const source = path.join(sourceDir, sourceName);
    const definition = fs.readFileSync(source, "utf8");
    if (!definition.startsWith("---\n") || !definition.includes("\nmode: subagent\n")) {
      throw new Error(`${source} is not a portable OpenCode subagent definition`);
    }
    const target = path.join(configDir, "agents", `${prefix}${sourceName}`);
    if (!fs.lstatSync(target).isSymbolicLink()) throw new Error(`${target} is not a symlink`);
    if (fs.realpathSync(target) !== fs.realpathSync(source)) {
      throw new Error(`${target} does not point to its source agent`);
    }
  }
}
NODE

collision="$config_dir/agents/music-engine-rowan-lyric-writer.md"
rm "$collision"
printf 'user-owned agent\n' >"$collision"
definition_collision="$config_dir/agents/story-engine-wyrd-character-builder.md"
rm "$definition_collision"
ln -s "$temp_dir/missing-agent.md" "$definition_collision"
skill_collision="$config_dir/skills/implement"
rm "$skill_collision"
ln -s "$temp_dir/missing-skill" "$skill_collision"
XDG_CONFIG_HOME="$temp_dir/config" "$setup_script" >"$temp_dir/second.out" 2>"$temp_dir/second.err"

test "$(cat "$collision")" = "user-owned agent"
test "$(readlink "$definition_collision")" = "$temp_dir/missing-agent.md"
test "$(readlink "$skill_collision")" = "$temp_dir/missing-skill"
grep -F "Warning: preserving existing OpenCode agent: $collision" "$temp_dir/second.err" >/dev/null
grep -F "Warning: preserving existing OpenCode agent: $definition_collision" "$temp_dir/second.err" >/dev/null
grep -F "Warning: preserving existing OpenCode skill: $skill_collision" "$temp_dir/second.err" >/dev/null

printf 'setup-opencode tests passed\n'
