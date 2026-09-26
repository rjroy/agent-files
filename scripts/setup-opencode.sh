#!/usr/bin/env bash
# Register this repository's instructions, skills, agents, and commands with OpenCode V2.
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
plugins_dir="$repo_dir/plugins"
config_home="${XDG_CONFIG_HOME:-$HOME/.config}"
config_dir="$config_home/opencode"
if [ ! -d "$plugins_dir" ]; then
	printf 'Error: plugin directory not found: %s\n' "$plugins_dir" >&2
	exit 1
fi

mkdir -p "$config_dir"

node - "$plugins_dir" "$config_dir" <<'NODE'
const fs = require("node:fs");
const path = require("node:path");

const [pluginsDir, configDir] = process.argv.slice(2);
const resolvedPluginsDir = path.resolve(pluginsDir);

function isSymlinkTo(target, source) {
  const targetStat = fs.lstatSync(target, { throwIfNoEntry: false });
  if (!targetStat?.isSymbolicLink()) return false;

  return path.resolve(path.dirname(target), fs.readlinkSync(target)) === path.resolve(source);
}

const instructionsSource = path.join(path.dirname(resolvedPluginsDir), "COMMON.md");
const instructionsTarget = path.join(configDir, "AGENTS.md");
if (!fs.existsSync(instructionsSource)) {
  throw new Error(`OpenCode instructions not found: ${instructionsSource}`);
}
if (fs.lstatSync(instructionsTarget, { throwIfNoEntry: false })) {
  if (!isSymlinkTo(instructionsTarget, instructionsSource)) {
    console.error(`Warning: preserving existing OpenCode instructions: ${instructionsTarget}`);
  }
} else {
  fs.symlinkSync(instructionsSource, instructionsTarget);
}

const collections = [
  { name: "lore-development", kind: "agents" },
  { name: "music-engine-rowan", kind: "agents", prefix: "music-engine-rowan-" },
  { name: "story-engine-wyrd", kind: "agents", prefix: "story-engine-wyrd-" },
  { name: "art-gen", kind: "commands" },
  { name: "judgment-engine-virelan", kind: "commands" },
  { name: "music-engine-rowan", kind: "commands" },
  { name: "story-engine-wyrd", kind: "commands" },
];

for (const { name, kind, prefix = "" } of collections) {
  const sourceDir = path.join(resolvedPluginsDir, name, kind);
  const targetDir = path.join(configDir, kind);
  if (!fs.existsSync(sourceDir)) continue;
  fs.mkdirSync(targetDir, { recursive: true });

  let registered = 0;
  for (const entry of fs.readdirSync(sourceDir, { withFileTypes: true })) {
    if (!entry.isFile() || path.extname(entry.name) !== ".md") continue;
    const source = path.join(sourceDir, entry.name);
    const target = path.join(targetDir, `${prefix}${entry.name}`);
    if (fs.existsSync(target) || fs.lstatSync(target, { throwIfNoEntry: false })?.isSymbolicLink()) {
      if (!isSymlinkTo(target, source)) {
        console.error(`Warning: preserving existing OpenCode ${kind.slice(0, -1)}: ${target}`);
        continue;
      }
    } else {
      fs.symlinkSync(source, target);
    }
    registered += 1;
  }
  console.log(`Registered ${registered} ${name} ${kind} definition(s) in ${targetDir}.`);
}

const skillsDir = path.join(configDir, "skills");
fs.mkdirSync(skillsDir, { recursive: true });
let registeredSkills = 0;
const skillCollections = [
  "art-gen",
  "audio-analysis",
  "field-guide",
  "judgment-engine-virelan",
  "lore-development",
  "music-engine-rowan",
  "personal",
  "story-engine-wyrd",
];
const skillSourceDirs = [
  path.join(path.dirname(resolvedPluginsDir), ".agents", "skills"),
  path.join(path.dirname(resolvedPluginsDir), "skills"),
  ...skillCollections.map((collection) => path.join(resolvedPluginsDir, collection, "skills")),
];

for (const collectionDir of skillSourceDirs) {
  if (!fs.existsSync(collectionDir)) continue;
  for (const entry of fs.readdirSync(collectionDir, { withFileTypes: true })) {
    if (!entry.isDirectory()) continue;
    const sourceDir = path.join(collectionDir, entry.name);
    if (!fs.existsSync(path.join(sourceDir, "SKILL.md"))) continue;
    const target = path.join(skillsDir, entry.name);
    if (fs.existsSync(target) || fs.lstatSync(target, { throwIfNoEntry: false })?.isSymbolicLink()) {
      if (!isSymlinkTo(target, sourceDir)) {
        console.error(`Warning: preserving existing OpenCode skill: ${target}`);
        continue;
      }
    } else {
      fs.symlinkSync(sourceDir, target);
    }
    registeredSkills += 1;
  }
}
console.log(`Registered ${registeredSkills} skill definition(s) in ${skillsDir}.`);
NODE

printf 'Quit and restart OpenCode for the updated configuration to take effect.\n'
