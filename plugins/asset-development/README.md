# Asset Development Skills

Reusable guidance for authorized visual-asset work: exploratory concepts, production 2D art, Blender modeling and visualization, and post-acceptance production derivatives. This plugin has no manifest; skills are discovered from its `skills/` root by the configured skill loader.

## Skills

- `asset-workflow`: orchestrates the approval gates, 2D or Blender branch, evidence, source preservation, and handoff.
- `concept-art`: exploratory concept images through the authorized Codex image-generation route.
- `asset-art`: approved production 2D artwork and exact-version review.
- `atmospheric-narrative-illustration`: opt-in art-direction overlay for narrative-led cinematic illustration briefs, prompts, and visual reviews; not an execution workflow or authorization.
- `blender-model`: construction/revision of editable Blender sources under modeling authorization.
- `blender-visualize`: read-only previews and geometry critique of a saved Blender source.
- `asset-production`: separately authorized optimization/baking/export derivatives and consumer validation after accepted source work.

Load skills through the consuming environment's normal skill-discovery route. Skill-relative references and helpers resolve from the loaded skill directory. Project paths resolve from the consuming project root, not this plugin directory.

## Project context contract

For asset work, consult `<project-root>/docs/asset-direction.md` when it exists. It may link to a project-specific production guide; follow relevant project guidance and identify conflicts for the user rather than silently choosing. This context describes direction and does not approve an individual asset or bypass task authorization and approval gates. If the file is absent, use the user's brief and authorized references; ask only for requirements that critically block the next authorized step. Do not require creating a context file.

## Optional art direction

Load [atmospheric-narrative-illustration](skills/atmospheric-narrative-illustration/SKILL.md) only when the user requests or approves that style for the current work. It adds narrative staging, graphic-novel linework, painterly atmosphere, controlled color, and a visual-review rubric without replacing project identity or becoming a universal style default. Combine it with `asset-workflow` and the relevant execution skill: `concept-art` for exploration or `asset-art` for production 2D work, using their authorized Codex routes. For Blender, it may guide an approved reference but does not authorize modeling or alter read-only, neutral/restrained geometry critique. All description, concept/artwork, model, derivative, integration, and runtime-acceptance gates remain separate.

## Preserved and extracted workflow

The source `asset-workflow` material is preserved across this package as follows:

| Source guidance | Destination |
| --- | --- |
| Description approval; branch choice; concept/model/art/runtime gates; bounded iteration; distinct approvals | `skills/asset-workflow/SKILL.md` |
| Modeling/critique ownership, native-source default, optional generator, scope coverage, source preservation, relocatable package, and authorized acceptance-time cleanup | `skills/asset-workflow/SKILL.md`, `skills/blender-model/SKILL.md`, `skills/blender-visualize/SKILL.md` |
| Authorized Codex route; native image staging; decode, inspect, copy, checksum, and exact-version approval | `skills/concept-art/SKILL.md`, `skills/asset-art/SKILL.md` |
| Production artwork-specific framing, alpha, and projected-size checks | `skills/asset-art/SKILL.md` |
| Blender construction, task-dependent reproducibility, export/consumer caveats, bounded execution and recovery | `skills/blender-model/SKILL.md` |
| Read-only Blender rendering, source-integrity checks, bounded visual critique and evidence | `skills/blender-visualize/SKILL.md` |
| Separate production derivatives, source immutability, reproducible conversion, optimization/baking options, real-consumer validation and handoff | `skills/asset-production/SKILL.md` |

Project-specific Brightvale/Shining Stars direction and modeler agent routing were intentionally not carried over. Route visual decisions to the user/designer; use available authorized tools and agents only as explicitly scoped. Do not substitute a visual specialist without permission.
