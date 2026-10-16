#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HELP = `Usage: node scripts/setup-opencode.mjs [--apply] [--help]

Preview planned OpenCode setup changes by default. Use --apply to update an
existing OpenCode config and create the two approved global links.
`;

function parseArgs(args) {
  let apply = false;
  let help = false;
  for (const arg of args) {
    if (arg === "--help" || arg === "-h") {
      help = true;
      continue;
    }
    if (arg === "--apply") {
      apply = true;
      continue;
    }
    throw new Error(`Unknown option: ${arg}\n\n${HELP.trim()}`);
  }
  return { apply, help };
}

function resolveRepository() {
  const scriptPath = fs.realpathSync(fileURLToPath(import.meta.url));
  return path.dirname(path.dirname(scriptPath));
}

function hasSkillFile(directory) {
  if (!fs.existsSync(directory) || !fs.statSync(directory).isDirectory()) return false;
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    const candidate = path.join(directory, entry.name);
    if (entry.isFile() && entry.name === "SKILL.md") return true;
    if (entry.isDirectory() && hasSkillFile(candidate)) return true;
  }
  return false;
}

function discoverSkillRoots(repository) {
  const roots = [path.join(repository, ".agents", "skills"), path.join(repository, "skills")];
  const plugins = path.join(repository, "plugins");
  if (fs.existsSync(plugins) && fs.statSync(plugins).isDirectory()) {
    for (const plugin of fs.readdirSync(plugins, { withFileTypes: true })) {
      if (plugin.isDirectory()) roots.push(path.join(plugins, plugin.name, "skills"));
    }
  }
  const canonicalRoots = roots
    .map((root) => path.resolve(root))
    .filter(hasSkillFile)
    .map((root) => fs.realpathSync(root));
  return [...new Set(canonicalRoots)];
}

function captureConfigSnapshot(configPath) {
  const stat = fs.lstatSync(configPath, { throwIfNoEntry: false });
  if (!stat || stat.isSymbolicLink() || !stat.isFile()) {
    throw new Error(`OpenCode config changed or is not a regular file: ${configPath}`);
  }
  return {
    dev: stat.dev,
    ino: stat.ino,
    mode: stat.mode & 0o777,
    bytes: fs.readFileSync(configPath),
  };
}

function assertConfigSnapshot(configPath, expected) {
  const current = captureConfigSnapshot(configPath);
  if (
    current.dev !== expected.dev ||
    current.ino !== expected.ino ||
    current.mode !== expected.mode ||
    !current.bytes.equals(expected.bytes)
  ) {
    throw new Error(`OpenCode config changed during setup; refusing to overwrite it: ${configPath}`);
  }
  return current;
}

function safeParseLocation(message) {
  const lineColumn = /\bline\s+(\d+)\s+column\s+(\d+)\b/i.exec(message);
  if (lineColumn) return `line ${lineColumn[1]}, column ${lineColumn[2]}`;
  const position = /\bposition\s+(\d+)\b/i.exec(message);
  if (position) return `position ${position[1]}`;
  return "location unavailable";
}

function readConfig(configDirectory) {
  const jsonPath = path.join(configDirectory, "opencode.json");
  const jsoncPath = path.join(configDirectory, "opencode.jsonc");
  const jsonExists = fs.lstatSync(jsonPath, { throwIfNoEntry: false });
  const jsoncExists = fs.lstatSync(jsoncPath, { throwIfNoEntry: false });
  if (jsonExists && jsoncExists) throw new Error("Both opencode.json and opencode.jsonc exist; refusing ambiguous config.");
  const configPath = jsonExists ? jsonPath : jsoncExists ? jsoncPath : null;
  if (!configPath) throw new Error(`OpenCode config is required at ${jsonPath} or ${jsoncPath}.`);

  const stat = fs.lstatSync(configPath);
  if (stat.isSymbolicLink()) throw new Error(`Refusing symlinked OpenCode config: ${configPath}`);
  if (!stat.isFile()) throw new Error(`OpenCode config is not a regular file: ${configPath}`);

  const snapshot = captureConfigSnapshot(configPath);
  const original = snapshot.bytes;
  let config;
  try {
    config = JSON.parse(original.toString("utf8"));
  } catch (error) {
    const kind = configPath.endsWith(".jsonc")
      ? "JSONC comments and extended syntax are unsupported; .jsonc must contain strict JSON"
      : "Malformed JSON";
    throw new Error(`${kind} in ${path.basename(configPath)} (${safeParseLocation(error.message)}).`);
  }
  if (!config || typeof config !== "object" || Array.isArray(config)) {
    throw new Error(`OpenCode config must contain a JSON object: ${configPath}`);
  }
  return { configPath, config, snapshot };
}

function isUrl(value) {
  return /^[a-z][a-z\d+.-]*:/i.test(value) && !/^[a-z]:[\\/]/i.test(value);
}

function expandHome(value, home) {
  if (!home) return value;
  if (value === "~") return home;
  if (value.startsWith("~/") || value.startsWith("~\\")) return path.join(home, value.slice(2));
  return value;
}

function resolveConfiguredRoot(value, configDirectory, home) {
  if (typeof value !== "string" || isUrl(value)) return null;
  const expanded = expandHome(value, home);
  const absolute = path.resolve(configDirectory, expanded);
  try {
    if (!fs.statSync(absolute).isDirectory()) return null;
    return fs.realpathSync(absolute);
  } catch (error) {
    if (error.code === "ENOENT" || error.code === "ENOTDIR") return absolute;
    throw error;
  }
}

function containsPath(parent, child) {
  const relative = path.relative(parent, child);
  return relative === "" || (
    relative !== ".." &&
    !relative.startsWith(`..${path.sep}`) &&
    !path.isAbsolute(relative)
  );
}

function rootIsCovered(candidate, roots) {
  return roots.some((root) => containsPath(root, candidate) && hasSkillFile(root));
}

function addSkillRoots(config, configDirectory, roots, home) {
  let existing;
  let assign;
  if (Array.isArray(config.skills)) {
    existing = config.skills;
    assign = (next) => { config.skills = next; };
  } else if (config.skills === undefined) {
    existing = [];
    assign = (next) => { config.skills = { paths: next }; };
  } else if (config.skills && typeof config.skills === "object" && !Array.isArray(config.skills)) {
    if (config.skills.paths === undefined) config.skills.paths = [];
    if (!Array.isArray(config.skills.paths)) {
      throw new Error("Unsupported skills.paths value; expected an array while preserving the skills object shape.");
    }
    existing = config.skills.paths;
    assign = (next) => { config.skills.paths = next; };
  } else {
    throw new Error("Unsupported skills config; expected a skills array or an object with skills.paths.");
  }

  const known = existing
    .map((value) => resolveConfiguredRoot(value, configDirectory, home))
    .filter(Boolean);
  const added = [];
  for (const root of roots) {
    if (rootIsCovered(root, known)) continue;
    added.push(root);
    known.push(root);
  }
  if (added.length) assign([...existing, ...added]);
  return added;
}

function isCorrectLink(target, source) {
  const stat = fs.lstatSync(target, { throwIfNoEntry: false });
  if (!stat) return false;
  if (!stat.isSymbolicLink()) throw new Error(`Refusing existing path: ${target}`);
  const linkedPath = path.resolve(path.dirname(target), fs.readlinkSync(target));
  if (linkedPath !== source) throw new Error(`Refusing conflicting or dangling link: ${target} -> ${fs.readlinkSync(target)}`);
  return true;
}

function inspectLink(target, source) {
  const stat = fs.lstatSync(target, { throwIfNoEntry: false });
  if (!stat) return false;
  return isCorrectLink(target, source);
}

function writeDurableFile(filePath, bytes, mode) {
  let fd;
  try {
    fd = fs.openSync(filePath, "wx", mode);
    fs.writeFileSync(fd, bytes);
    fs.fchmodSync(fd, mode);
    fs.fsyncSync(fd);
    fs.closeSync(fd);
  } catch (error) {
    if (fd !== undefined) {
      try { fs.closeSync(fd); } catch { /* Preserve the original write error. */ }
      try { fs.rmSync(filePath, { force: true }); } catch { /* Leave the original error actionable. */ }
    }
    throw error;
  }
}

function syncDirectory(directory) {
  const fd = fs.openSync(directory, "r");
  try {
    fs.fsyncSync(fd);
  } finally {
    fs.closeSync(fd);
  }
}

function backupPathFor(configPath) {
  const base = `${configPath}.bak-${Date.now()}-${process.pid}`;
  let candidate = base;
  let suffix = 0;
  while (fs.existsSync(candidate)) candidate = `${base}-${++suffix}`;
  return candidate;
}

function replaceConfig(configPath, snapshot, updated) {
  const backup = backupPathFor(configPath);
  const temporary = path.join(path.dirname(configPath), `.${path.basename(configPath)}.tmp-${process.pid}-${Date.now()}`);
  let backupCreated = false;
  let temporaryCreated = false;
  let replaced = false;
  let writtenSnapshot = null;
  try {
    writeDurableFile(backup, snapshot.bytes, snapshot.mode);
    backupCreated = true;
    syncDirectory(path.dirname(configPath));
    writeDurableFile(temporary, updated, snapshot.mode);
    temporaryCreated = true;
    writtenSnapshot = captureConfigSnapshot(temporary);
    assertConfigSnapshot(configPath, snapshot);
    fs.renameSync(temporary, configPath);
    temporaryCreated = false;
    replaced = true;
    assertConfigSnapshot(configPath, writtenSnapshot);
    syncDirectory(path.dirname(configPath));
    return { backup, writtenSnapshot };
  } catch (error) {
    if (temporaryCreated) fs.rmSync(temporary, { force: true });
    if (backupCreated && replaced) {
      if (!writtenSnapshot) {
        throw new Error(`${error.message}; config may have changed after replacement; backup retained at ${backup}`);
      }
      try {
        restoreConfig(configPath, backup, writtenSnapshot);
        backupCreated = false;
      } catch (restoreError) {
        throw new Error(`${error.message}; additionally failed to restore config from ${backup}: ${restoreError.message}`);
      }
    }
    if (backupCreated) fs.rmSync(backup, { force: true });
    throw error;
  }
}

function restoreConfig(configPath, backup, expectedCurrent) {
  if (!backup) return;
  let current;
  try {
    current = captureConfigSnapshot(configPath);
  } catch {
    throw new Error(`Config changed during setup; preserving it and retaining backup at ${backup}`);
  }
  if (
    current.dev !== expectedCurrent.dev ||
    current.ino !== expectedCurrent.ino ||
    current.mode !== expectedCurrent.mode ||
    !current.bytes.equals(expectedCurrent.bytes)
  ) {
    throw new Error(`Config changed during setup; preserving it and retaining backup at ${backup}`);
  }
  fs.renameSync(backup, configPath);
  syncDirectory(path.dirname(configPath));
}

function planSetup() {
  const repository = resolveRepository();
  const instructionsSource = path.join(repository, "COMMON.md");
  const slimSource = path.join(repository, "omo-slim-agents");
  if (!fs.existsSync(instructionsSource) || !fs.statSync(instructionsSource).isFile()) {
    throw new Error(`Shared instructions are missing: ${instructionsSource}`);
  }
  if (!fs.existsSync(slimSource) || !fs.statSync(slimSource).isDirectory()) {
    throw new Error(`Slim prompt directory is missing: ${slimSource}`);
  }

  const home = process.env.HOME;
  const configHome = process.env.XDG_CONFIG_HOME || (home ? path.join(home, ".config") : null);
  if (!configHome) throw new Error("Cannot locate config home; set XDG_CONFIG_HOME or HOME.");
  const configDirectory = path.resolve(configHome, "opencode");
  const { configPath, config, snapshot } = readConfig(configDirectory);
  const skillRoots = discoverSkillRoots(repository);
  const addedSkillRoots = addSkillRoots(config, configDirectory, skillRoots, home);
  const updated = addedSkillRoots.length ? `${JSON.stringify(config, null, 2)}\n` : snapshot.bytes.toString("utf8");
  const configChanged = !Buffer.from(updated).equals(snapshot.bytes);

  const links = [
    { target: path.join(configDirectory, "AGENTS.md"), source: instructionsSource },
    { target: path.join(configDirectory, "oh-my-opencode-slim"), source: slimSource },
  ];
  for (const link of links) link.existedCorrectly = inspectLink(link.target, link.source);

  return { repository, configDirectory, configPath, snapshot, updated, configChanged, addedSkillRoots, links };
}

function printPlan(plan, apply) {
  const verb = apply ? "Create" : "Would create";
  const change = apply ? "Add" : "Would add";
  console.log(apply ? "Applying OpenCode setup:" : "OpenCode setup preview (no files will be written):");
  for (const link of plan.links) {
    console.log(`${link.existedCorrectly ? "Keep" : verb} ${link.target} -> ${link.source}`);
  }
  if (plan.configChanged) {
    for (const root of plan.addedSkillRoots) console.log(`${change} skill root ${root} in ${plan.configPath}`);
  } else {
    console.log(`Keep config unchanged: ${plan.configPath}`);
  }
  if (plan.configChanged) {
    console.log("A recoverable backup will be kept beside the config. Reconcile chezmoi source if this file is managed.");
  }
  console.log("Restart OpenCode to activate changes.");
}

function applyPlan(plan) {
  const createdLinks = [];
  let configReplacement = null;
  try {
    assertConfigSnapshot(plan.configPath, plan.snapshot);
    if (plan.configChanged) {
      configReplacement = replaceConfig(plan.configPath, plan.snapshot, Buffer.from(plan.updated));
    }
    for (const link of plan.links) {
      if (link.existedCorrectly) continue;
      fs.symlinkSync(link.source, link.target);
      const created = { target: link.target, source: link.source, dev: null, ino: null };
      createdLinks.push(created);
      const stat = fs.lstatSync(link.target);
      if (stat.isSymbolicLink()) {
        created.dev = stat.dev;
        created.ino = stat.ino;
      }
    }
    if (createdLinks.length) syncDirectory(plan.configDirectory);
    return configReplacement?.backup ?? null;
  } catch (error) {
    const rollbackErrors = [];
    for (const created of createdLinks.reverse()) {
      try {
        const { target, source } = created;
        const stat = fs.lstatSync(target, { throwIfNoEntry: false });
        if (!stat) continue;
        if (
          created.dev === null ||
          stat.dev !== created.dev ||
          stat.ino !== created.ino ||
          !stat.isSymbolicLink() ||
          path.resolve(path.dirname(target), fs.readlinkSync(target)) !== source
        ) {
          rollbackErrors.push(`preserved changed path ${target}`);
          continue;
        }
        fs.unlinkSync(target);
      } catch (cleanupError) {
        rollbackErrors.push(`could not remove created link ${created.target}: ${cleanupError.message}`);
      }
    }
    if (configReplacement) {
      try {
        restoreConfig(plan.configPath, configReplacement.backup, configReplacement.writtenSnapshot);
      } catch (restoreError) {
        rollbackErrors.push(`could not restore config from ${configReplacement.backup}: ${restoreError.message}`);
      }
    }
    if (rollbackErrors.length) throw new Error(`${error.message}; rollback incomplete: ${rollbackErrors.join("; ")}`);
    throw error;
  }
}

function main() {
  const options = parseArgs(process.argv.slice(2));
  if (options.help) {
    console.log(HELP.trimEnd());
    return;
  }
  const plan = planSetup();
  printPlan(plan, options.apply);
  if (options.apply) {
    const backup = applyPlan(plan);
    if (backup) console.log(`Config backup: ${backup}`);
  }
}

try {
  main();
} catch (error) {
  console.error(`Error: ${error.message}`);
  process.exitCode = 1;
}
