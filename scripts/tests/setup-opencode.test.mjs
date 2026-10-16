import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

const repositoryRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const installerSource = path.join(repositoryRoot, "scripts", "setup-opencode.mjs");
assert.ok(fs.existsSync(installerSource), "expected scripts/setup-opencode.mjs");

function writeSkill(repo, root, skillName) {
  const skillDir = path.join(repo, root, skillName);
  fs.mkdirSync(skillDir, { recursive: true });
  fs.writeFileSync(path.join(skillDir, "SKILL.md"), `# ${skillName}\n`);
}

function createFixture({
  config = { skills: [] },
  configName = "opencode.json",
  createConfig = true,
} = {}) {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), "opencode setup fixture "));
  const repo = path.join(temp, "repository with spaces");
  const scriptsDir = path.join(repo, "scripts");
  const configHome = path.join(temp, "xdg config with spaces");
  const home = path.join(temp, "home with spaces");
  const configDir = path.join(configHome, "opencode");
  const fixtureInstaller = path.join(scriptsDir, path.basename(installerSource));

  fs.mkdirSync(scriptsDir, { recursive: true });
  fs.mkdirSync(path.join(repo, "omo-slim-agents"), { recursive: true });
  fs.mkdirSync(configDir, { recursive: true });
  fs.copyFileSync(installerSource, fixtureInstaller);
  fs.chmodSync(fixtureInstaller, fs.statSync(installerSource).mode);
  fs.writeFileSync(path.join(repo, "COMMON.md"), "# Shared instructions\n");
  fs.writeFileSync(path.join(repo, "omo-slim-agents", "fixture-agent.md"), "Prompt body\n");

  writeSkill(repo, ".agents/skills", "local-skill");
  writeSkill(repo, "skills", "root-skill");
  writeSkill(repo, "plugins/fixture-plugin/skills", "plugin-skill");
  fs.mkdirSync(path.join(repo, "plugins/empty-plugin/skills"), { recursive: true });
  fs.writeFileSync(path.join(repo, "plugins/empty-plugin/skills", "NOT-A-SKILL.md"), "not a skill\n");

  const configFile = path.join(configDir, configName);
  if (createConfig) fs.writeFileSync(configFile, `${JSON.stringify(config, null, 2)}\n`);

  return {
    temp,
    repo,
    configHome,
    home,
    configDir,
    configFile,
    fixtureInstaller,
    cleanup: () => fs.rmSync(temp, { recursive: true, force: true }),
  };
}

function runSetup(fixture, args = [], { preload, env = {} } = {}) {
  const nodeArgs = preload ? ["--import", preload, fixture.fixtureInstaller, ...args] : [fixture.fixtureInstaller, ...args];
  return spawnSync(process.execPath, nodeArgs, {
    cwd: fixture.repo,
    encoding: "utf8",
    env: {
      ...process.env,
      HOME: fixture.home,
      XDG_CONFIG_HOME: fixture.configHome,
      ...env,
    },
  });
}

function writePreload(fixture, name, source) {
  const preload = path.join(fixture.repo, "scripts", name);
  fs.writeFileSync(preload, source);
  return preload;
}

function snapshotTree(root) {
  if (!fs.existsSync(root) && !fs.lstatSync(root, { throwIfNoEntry: false })) return null;
  const stat = fs.lstatSync(root);
  if (stat.isSymbolicLink()) return { type: "link", target: fs.readlinkSync(root) };
  if (stat.isFile()) return { type: "file", bytes: fs.readFileSync(root).toString("base64") };
  return {
    type: "directory",
    entries: Object.fromEntries(
      fs.readdirSync(root).sort().map((name) => [name, snapshotTree(path.join(root, name))]),
    ),
  };
}

function symlinkPaths(root, prefix = "") {
  const result = [];
  for (const name of fs.readdirSync(root)) {
    const fullPath = path.join(root, name);
    const relativePath = path.posix.join(prefix, name);
    const stat = fs.lstatSync(fullPath);
    if (stat.isSymbolicLink()) result.push(relativePath);
    else if (stat.isDirectory()) result.push(...symlinkPaths(fullPath, relativePath));
  }
  return result.sort();
}

function regularFiles(root) {
  if (!fs.existsSync(root)) return [];
  const stat = fs.lstatSync(root);
  if (stat.isSymbolicLink()) return [];
  if (stat.isFile()) return [root];
  return fs.readdirSync(root).flatMap((name) => regularFiles(path.join(root, name)));
}

function assertSuccessful(result) {
  assert.equal(result.error, undefined, result.error?.message);
  assert.equal(result.status, 0, result.stderr || result.stdout);
}

function assertFailed(result) {
  assert.equal(result.error, undefined, result.error?.message);
  assert.notEqual(result.status, 0, `expected failure, got: ${result.stdout}`);
}

function expectedSkillRoots(repo) {
  return [
    path.join(repo, ".agents", "skills"),
    path.join(repo, "skills"),
    path.join(repo, "plugins", "fixture-plugin", "skills"),
  ];
}

function assertOnlyManagedLinks(fixture) {
  assert.deepEqual(symlinkPaths(fixture.configDir), ["AGENTS.md", "oh-my-opencode-slim"]);
  for (const [link, source] of [
    [path.join(fixture.configDir, "AGENTS.md"), path.join(fixture.repo, "COMMON.md")],
    [path.join(fixture.configDir, "oh-my-opencode-slim"), path.join(fixture.repo, "omo-slim-agents")],
  ]) {
    assert.equal(path.resolve(path.dirname(link), fs.readlinkSync(link)), source);
  }
  for (const forbidden of ["agents", "commands", "skills"]) {
    assert.equal(fs.existsSync(path.join(fixture.configDir, forbidden)), false, `${forbidden} must not be installed`);
  }
  for (const configName of ["opencode.json", "opencode.jsonc"]) {
    const configFile = path.join(fixture.configDir, configName);
    if (fs.existsSync(configFile)) assert.equal(fs.lstatSync(configFile).isFile(), true, `${configName} stays a regular file`);
  }
}

test("default invocation previews without writing files, links, directories, or backups", (t) => {
  const fixture = createFixture({ config: { skills: [] } });
  t.after(fixture.cleanup);
  const before = snapshotTree(fixture.temp);
  const result = runSetup(fixture);
  assertSuccessful(result);
  assert.deepEqual(snapshotTree(fixture.temp), before, "preview must leave the fixture byte-for-byte unchanged");
});

test("help describes preview and apply modes without touching the fixture", (t) => {
  const fixture = createFixture({ config: { skills: [] } });
  t.after(fixture.cleanup);
  const before = snapshotTree(fixture.temp);
  const result = runSetup(fixture, ["--help"]);
  assertSuccessful(result);
  assert.match(`${result.stdout}\n${result.stderr}`, /--apply/);
  assert.deepEqual(snapshotTree(fixture.temp), before, "help must be side-effect free");
});

test("--apply preserves skills.paths object shape and adds only real skill roots", (t) => {
  const fixture = createFixture({
    config: { name: "preserve me", skills: { paths: ["/opt/team-skills"], enabled: false }, unrelated: { value: 7 } },
  });
  t.after(fixture.cleanup);
  const original = fs.readFileSync(fixture.configFile, "utf8");
  const result = runSetup(fixture, ["--apply"]);
  assertSuccessful(result);

  const updatedText = fs.readFileSync(fixture.configFile, "utf8");
  const updated = JSON.parse(updatedText);
  assert.equal(fs.lstatSync(fixture.configFile).isFile(), true);
  assert.deepEqual(updated.name, "preserve me");
  assert.deepEqual(updated.unrelated, { value: 7 });
  assert.equal(Array.isArray(updated.skills), false, "skills.paths representation must remain an object");
  assert.equal(updated.skills.enabled, false);
  assert.deepEqual(updated.skills.paths, ["/opt/team-skills", ...expectedSkillRoots(fixture.repo)]);
  assert.equal(updatedText === original, false, "new skill roots must be persisted");
  assertOnlyManagedLinks(fixture);

  const backups = regularFiles(fixture.configHome)
    .filter((candidate) => candidate !== fixture.configFile)
    .map((candidate) => fs.readFileSync(candidate));
  assert.ok(backups.some((bytes) => bytes.equals(Buffer.from(original))), "changed config needs a recoverable backup");
});

test("--apply preserves the skills array shape and does not duplicate an existing absolute root", (t) => {
  const fixture = createFixture({
    config: { skills: ["/opt/team-skills", path.join(path.resolve("/tmp"), "not-a-fixture-root")] },
  });
  t.after(fixture.cleanup);
  const existingRoot = expectedSkillRoots(fixture.repo)[1];
  const original = { skills: ["/opt/team-skills", existingRoot] };
  fs.writeFileSync(fixture.configFile, `${JSON.stringify(original, null, 2)}\n`);

  const result = runSetup(fixture, ["--apply"]);
  assertSuccessful(result);
  const updated = JSON.parse(fs.readFileSync(fixture.configFile, "utf8"));
  assert.ok(Array.isArray(updated.skills), "skills array representation must remain an array");
  assert.deepEqual(updated.skills, ["/opt/team-skills", existingRoot, expectedSkillRoots(fixture.repo)[0], expectedSkillRoots(fixture.repo)[2]]);
  assert.equal(updated.skills.filter((entry) => entry === existingRoot).length, 1);
  assertOnlyManagedLinks(fixture);
});

test("tilde and symlink-alias skill roots deduplicate canonically without rewriting existing values", (t) => {
  const fixture = createFixture({ config: { skills: [] } });
  t.after(fixture.cleanup);
  const homeRepository = path.join(fixture.home, "repository");
  fs.mkdirSync(homeRepository, { recursive: true });
  fs.symlinkSync(path.join(fixture.repo, "skills"), path.join(homeRepository, "skills"), "dir");
  const repositoryAlias = path.join(fixture.repo, "skills-alias");
  fs.symlinkSync(path.join(fixture.repo, "skills"), repositoryAlias, "dir");
  const originalValues = ["~/repository/skills", repositoryAlias];
  const original = { skills: { paths: originalValues, custom: "keep" } };
  fs.writeFileSync(fixture.configFile, `${JSON.stringify(original, null, 2)}\n`);

  assertSuccessful(runSetup(fixture, ["--apply"]));
  const updated = JSON.parse(fs.readFileSync(fixture.configFile, "utf8"));
  assert.deepEqual(updated.skills.paths.slice(0, 2), originalValues);
  assert.equal(updated.skills.custom, "keep");
  assert.equal(updated.skills.paths.includes(path.join(fixture.repo, "skills")), false);
  assert.deepEqual(updated.skills.paths.slice(2), [expectedSkillRoots(fixture.repo)[0], expectedSkillRoots(fixture.repo)[2]]);
});

test("a configured ancestor covers descendant skill roots without rewriting config or making a backup", (t) => {
  const fixture = createFixture({ config: { skills: ["/placeholder"] } });
  t.after(fixture.cleanup);
  const original = `${JSON.stringify({ skills: [fixture.repo] }, null, 2)}\n`;
  fs.writeFileSync(fixture.configFile, original);

  assertSuccessful(runSetup(fixture, ["--apply"]));
  assert.equal(fs.readFileSync(fixture.configFile, "utf8"), original);
  assert.deepEqual(regularFiles(fixture.configHome), [fixture.configFile]);
  assertOnlyManagedLinks(fixture);
});

test("reapplying an already-applied setup is a no-op", (t) => {
  const fixture = createFixture({ config: { skills: [] } });
  t.after(fixture.cleanup);
  assertSuccessful(runSetup(fixture, ["--apply"]));
  const afterFirstApply = snapshotTree(fixture.configDir);
  const second = runSetup(fixture, ["--apply"]);
  assertSuccessful(second);
  assert.deepEqual(snapshotTree(fixture.configDir), afterFirstApply);
  assertOnlyManagedLinks(fixture);
});

test("already-correct managed links are preserved as no-ops", (t) => {
  const fixture = createFixture({ config: { skills: [] } });
  t.after(fixture.cleanup);
  fs.writeFileSync(fixture.configFile, `${JSON.stringify({ skills: expectedSkillRoots(fixture.repo) }, null, 2)}\n`);
  fs.symlinkSync(path.join(fixture.repo, "COMMON.md"), path.join(fixture.configDir, "AGENTS.md"));
  fs.symlinkSync(path.join(fixture.repo, "omo-slim-agents"), path.join(fixture.configDir, "oh-my-opencode-slim"));
  const before = snapshotTree(fixture.configDir);

  assertSuccessful(runSetup(fixture, ["--apply"]));
  assert.deepEqual(snapshotTree(fixture.configDir), before);
});

test("a conflicting AGENTS.md is preserved and prevents all planned changes", (t) => {
  const fixture = createFixture({ config: { skills: [] } });
  t.after(fixture.cleanup);
  const agentsLink = path.join(fixture.configDir, "AGENTS.md");
  fs.writeFileSync(agentsLink, "user-owned instructions\n");
  const before = snapshotTree(fixture.temp);

  const result = runSetup(fixture, ["--apply"]);
  assert.equal(result.error, undefined, result.error?.message);
  assertFailed(result);
  assert.equal(fs.readFileSync(agentsLink, "utf8"), "user-owned instructions\n");
  assert.deepEqual(snapshotTree(fixture.temp), before, "preflight failure must not create the other link or edit config");
});

test("a dangling Slim-directory link is preserved and prevents creation of AGENTS.md", (t) => {
  const fixture = createFixture({ config: { skills: [] } });
  t.after(fixture.cleanup);
  const slimLink = path.join(fixture.configDir, "oh-my-opencode-slim");
  fs.symlinkSync(path.join(fixture.temp, "missing slim target"), slimLink);
  const before = snapshotTree(fixture.temp);

  const result = runSetup(fixture, ["--apply"]);
  assertFailed(result);
  assert.equal(fs.readlinkSync(slimLink), path.join(fixture.temp, "missing slim target"));
  assert.deepEqual(snapshotTree(fixture.temp), before, "preflight failure must not create AGENTS.md or edit config");
});

test("missing configuration is an error with no partial installation", (t) => {
  const fixture = createFixture({ createConfig: false });
  t.after(fixture.cleanup);
  const before = snapshotTree(fixture.temp);
  const result = runSetup(fixture, ["--apply"]);
  assertFailed(result);
  assert.deepEqual(snapshotTree(fixture.temp), before);
});

test("malformed configuration is rejected without changing its bytes or creating links", (t) => {
  const fixture = createFixture({ config: { skills: [] } });
  t.after(fixture.cleanup);
  const malformed = '{"x":s3cr3t}\n';
  fs.writeFileSync(fixture.configFile, malformed);
  const before = snapshotTree(fixture.temp);
  const result = runSetup(fixture, ["--apply"]);
  assertFailed(result);
  assert.deepEqual(snapshotTree(fixture.temp), before);
  assert.equal(`${result.stdout}\n${result.stderr}`.includes("s3cr3t"), false);
});

test("a config changed after preflight is preserved and installation aborts", (t) => {
  const fixture = createFixture({ config: { skills: [] } });
  t.after(fixture.cleanup);
  const newerConfig = '{"external_change":"keep this newer config"}\n';
  const preload = writePreload(fixture, "mutate-after-preflight.mjs", `
    import fs from "node:fs";
    const log = console.log.bind(console);
    let changed = false;
    console.log = (...args) => {
      log(...args);
      if (!changed && args[0] === "Applying OpenCode setup:") {
        fs.writeFileSync(process.env.SETUP_TEST_CONFIG, process.env.SETUP_TEST_NEW_CONFIG);
        changed = true;
      }
    };
  `);

  const result = runSetup(fixture, ["--apply"], {
    preload,
    env: { SETUP_TEST_CONFIG: fixture.configFile, SETUP_TEST_NEW_CONFIG: newerConfig },
  });
  assertFailed(result);
  assert.equal(fs.readFileSync(fixture.configFile, "utf8"), newerConfig);
  assert.deepEqual(symlinkPaths(fixture.configDir), []);
});

test("failed partial link rollback restores config and reports any retained created link", (t) => {
  const fixture = createFixture({ config: { skills: [] } });
  t.after(fixture.cleanup);
  const originalConfig = fs.readFileSync(fixture.configFile);
  const preload = writePreload(fixture, "fail-partial-link-rollback.mjs", `
    import fs from "node:fs";
    import path from "node:path";
    import { syncBuiltinESMExports } from "node:module";
    const createLink = fs.symlinkSync;
    const unlink = fs.unlinkSync;
    const remove = fs.rmSync;
    fs.symlinkSync = function (source, target, ...options) {
      if (path.basename(target) === "oh-my-opencode-slim") {
        const error = new Error("injected second-link failure");
        error.code = "EIO";
        throw error;
      }
      return createLink.call(fs, source, target, ...options);
    };
    fs.unlinkSync = function (target, ...options) {
      if (path.basename(target) === "AGENTS.md") {
        const error = new Error("injected rollback unlink failure");
        error.code = "EIO";
        throw error;
      }
      return unlink.call(fs, target, ...options);
    };
    fs.rmSync = function (target, ...options) {
      if (path.basename(target) === "AGENTS.md") {
        const error = new Error("injected rollback remove failure");
        error.code = "EIO";
        throw error;
      }
      return remove.call(fs, target, ...options);
    };
    syncBuiltinESMExports();
  `);

  const result = runSetup(fixture, ["--apply"], { preload });
  assertFailed(result);
  const retainedLink = path.join(fixture.configDir, "AGENTS.md");
  assert.deepEqual(symlinkPaths(fixture.configDir), ["AGENTS.md"]);
  assert.equal(path.resolve(path.dirname(retainedLink), fs.readlinkSync(retainedLink)), path.join(fixture.repo, "COMMON.md"));
  assert.equal(fs.readFileSync(fixture.configFile).equals(originalConfig), true, "config must be restored");
  assert.deepEqual(regularFiles(fixture.configHome), [fixture.configFile], "successful rollback must consume its backup");
  assert.match(`${result.stdout}\n${result.stderr}`, /rollback/i);
  assert.ok(`${result.stdout}\n${result.stderr}`.includes(retainedLink), "rollback report must name the retained link");
});

test("simultaneous JSON and JSONC configs fail as ambiguous without writes", (t) => {
  const fixture = createFixture({ config: { skills: [] } });
  t.after(fixture.cleanup);
  fs.writeFileSync(path.join(fixture.configDir, "opencode.jsonc"), '{"skills": []}\n');
  const before = snapshotTree(fixture.temp);
  const result = runSetup(fixture, ["--apply"]);
  assertFailed(result);
  assert.deepEqual(snapshotTree(fixture.temp), before);
});

test("commented JSONC is either preserved by a supported editor or refused without data loss", (t) => {
  const fixture = createFixture({ configName: "opencode.jsonc", config: { skills: [] } });
  t.after(fixture.cleanup);
  const original = `{// preserve this comment\n  "skills": []\n}\n`;
  fs.writeFileSync(fixture.configFile, original);
  const before = snapshotTree(fixture.temp);
  const result = runSetup(fixture, ["--apply"]);
  assert.equal(result.error, undefined, result.error?.message);

  if (result.status === 0) {
    const updated = fs.readFileSync(fixture.configFile, "utf8");
    assert.match(updated, /\/\/ preserve this comment/);
    for (const root of expectedSkillRoots(fixture.repo)) assert.ok(updated.includes(JSON.stringify(root)));
    assertOnlyManagedLinks(fixture);
  } else {
    assert.notEqual(result.status, null, result.stderr || "installer did not exit");
    assert.deepEqual(snapshotTree(fixture.temp), before, "unsupported JSONC must remain untouched");
  }
});

test("a symlinked top-level config is refused and its managed target remains untouched", (t) => {
  const fixture = createFixture({ createConfig: false });
  t.after(fixture.cleanup);
  const managedTarget = path.join(fixture.temp, "managed opencode config.json");
  const original = '{"skills": []}\n';
  fs.writeFileSync(managedTarget, original);
  fs.symlinkSync(managedTarget, fixture.configFile);
  const before = snapshotTree(fixture.temp);

  const result = runSetup(fixture, ["--apply"]);
  assertFailed(result);
  assert.deepEqual(snapshotTree(fixture.temp), before);
});
