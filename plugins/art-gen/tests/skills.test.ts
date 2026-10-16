import { expect, test } from "bun:test";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const pluginRoot = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "..",
);
const skill = await readFile(
  path.join(pluginRoot, "skills/art-gen-setup/SKILL.md"),
  "utf8",
);
const imageSkill = await readFile(
  path.join(pluginRoot, "skills/generate-image/SKILL.md"),
  "utf8",
);

test("art-gen setup skill is discoverable and collection-rooted", () => {
  expect(skill).toMatch(/^name: art-gen-setup$/m);
  expect(skill).toMatch(/^description: .{30,}$/m);
  expect(skill).toMatch(/only when the user asks/i);
  expect(skill).toMatch(/resolve the art-gen collection root two directories above it/i);
  expect(skill).toMatch(/bun install/);
  expect(skill).toMatch(/Do not run a generation script as a setup check/i);
  expect(skill).toMatch(/obtain confirmation before any generation request/i);
});

test("art-gen setup stays distinct from image generation", () => {
  expect(skill).toMatch(/does not generate an image or video/i);
  expect(imageSkill).toMatch(/generate-image skill/i);
});

test("active art-gen skills use loader-derived OpenCode paths", () => {
  expect(skill).toMatch(/absolute directory supplied by the OpenCode skill loader/i);
  expect(skill).toMatch(/two directories above it/i);
  expect(imageSkill).toMatch(/loader-provided absolute directory of this skill/i);
  expect(imageSkill).toMatch(/OpenCode's shell tool/i);
  expect(imageSkill).toMatch(/bun "\$ART_GEN_SKILL_DIR\/\.\.\/\.\.\/src\/generate-image\.ts"/);
  expect(imageSkill).not.toMatch(/CLAUDE_PLUGIN_ROOT|AskUserQuestion|Claude Code/i);
});

test("generation scripts use installed paths without changing project-relative media cwd", () => {
  for (const script of [
    "generate-image",
    "edit-image",
    "generate-video",
    "remove-background",
  ]) {
    expect(imageSkill).toContain(`bun "$ART_GEN_SKILL_DIR/../../src/${script}.ts"`);
  }
  for (const catalog of [
    "image-models",
    "video-models",
    "img2img-models",
    "remove-bg-models",
  ]) {
    expect(imageSkill).toContain(`$ART_GEN_SKILL_DIR/../../reference/${catalog}.md`);
  }

  expect(imageSkill).toMatch(/never from the user's working directory/);
  expect(imageSkill).toMatch(/Keep the shell's working directory at the user's project directory/);
  expect(imageSkill).toMatch(/do not `cd` to the skill or collection directory/);
  expect(imageSkill).toMatch(/resolve output paths against `process\.cwd\(\)` and read relative image paths from that same working directory/);
  expect(imageSkill).toMatch(/assets\/source\.png/);
  expect(imageSkill).toMatch(/generated\/source-edited\.png/);
  expect(imageSkill).toMatch(/the installed art-gen collection/);
});
