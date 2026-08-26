#!/usr/bin/env bash
# Register this repository's Claude-compatible skills with OpenCode.
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
plugins_dir="$repo_dir/plugins"
lore_agents_dir="$plugins_dir/lore-development/agents"
config_home="${XDG_CONFIG_HOME:-$HOME/.config}"
config_dir="$config_home/opencode"
config_file="$config_dir/opencode.json"
opencode_agents_dir="$config_dir/agents"

if ! command -v node >/dev/null 2>&1; then
	printf 'Error: Node.js is required to update %s.\n' "$config_file" >&2
	exit 1
fi

if [ ! -d "$plugins_dir" ]; then
	printf 'Error: plugin directory not found: %s\n' "$plugins_dir" >&2
	exit 1
fi

mkdir -p "$config_dir"

node - "$config_file" "$plugins_dir" <<'NODE'
const fs = require("node:fs");
const path = require("node:path");

const [configFile, pluginsDir] = process.argv.slice(2);
let config = {};

if (fs.existsSync(configFile)) {
  try {
    config = JSON.parse(fs.readFileSync(configFile, "utf8"));
  } catch (error) {
    console.error(`Error: ${configFile} is not valid JSON: ${error.message}`);
    process.exit(1);
  }
}

if (config === null || Array.isArray(config) || typeof config !== "object") {
  console.error(`Error: ${configFile} must contain a JSON object.`);
  process.exit(1);
}

config.$schema ??= "https://opencode.ai/config.json";
config.skills ??= {};

if (config.skills === null || Array.isArray(config.skills) || typeof config.skills !== "object") {
  console.error('Error: "skills" must be an object containing a "paths" array.');
  process.exit(1);
}

config.skills.paths ??= [];
if (!Array.isArray(config.skills.paths) || !config.skills.paths.every((entry) => typeof entry === "string")) {
  console.error('Error: "skills.paths" must be an array of strings.');
  process.exit(1);
}

const resolvedPluginsDir = path.resolve(pluginsDir);
const alreadyRegistered = config.skills.paths.some((entry) => path.resolve(entry) === resolvedPluginsDir);

if (!alreadyRegistered) config.skills.paths.push(resolvedPluginsDir);

const temporaryFile = `${configFile}.${process.pid}.tmp`;
fs.writeFileSync(temporaryFile, `${JSON.stringify(config, null, 2)}\n`, "utf8");
fs.renameSync(temporaryFile, configFile);

const skillCount = fs.readdirSync(resolvedPluginsDir, { recursive: true })
  .filter((entry) => path.basename(entry) === "SKILL.md").length;
console.log(`${alreadyRegistered ? "Verified" : "Added"} ${resolvedPluginsDir} in ${configFile}.`);
console.log(`OpenCode will discover ${skillCount} skill definition(s) from this directory.`);
NODE

if [ -d "$lore_agents_dir" ]; then
	mkdir -p "$opencode_agents_dir"
	agent_count=0
	for source in "$lore_agents_dir"/*.md; do
		target="$opencode_agents_dir/$(basename "$source")"
		if [ -e "$target" ] || [ -L "$target" ]; then
			if [ "$(readlink -f "$target")" != "$(readlink -f "$source")" ]; then
				printf 'Warning: preserving existing OpenCode agent: %s\n' "$target" >&2
				continue
			fi
		else
			ln -s "$source" "$target"
		fi
		agent_count=$((agent_count + 1))
	done
	printf 'Registered %d lore-development agent definition(s) in %s.\n' \
		"$agent_count" "$opencode_agents_dir"
fi

printf 'Quit and restart OpenCode for the updated configuration to take effect.\n'
