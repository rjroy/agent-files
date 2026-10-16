# Story Sample Selection Procedure

The `story-write-story` parent performs selection directly using this procedure; there is no delegated sampling-curator agent. Parent owns all workflow state, file writes, metadata changes, and cleanup. Parse and preserve the selected sample's full content rather than summarizing it.

## Parse candidates

Read the sample file and extract each candidate's number, content, probability, differentiator, diversity dimensions, and phase-specific metadata. Expect five candidates, but proceed with available candidates and warn if fewer exist. If probabilities cannot be parsed, assign equal weights and warn. If all probabilities are within 0.02, note the tie. Validate that parsed probabilities approximately sum to 1.0 (0.95–1.05); warn but proceed otherwise. Require at least one parseable candidate.

Always display differentiators, probabilities, and diversity dimensions when presenting options. Do not present a recommendation for concept or character selection: all candidates receive equal consideration and the user must choose explicitly.

## Choose by phase

- **Concept** (`concept-samples.md`): present all candidates and wait for the user's explicit selection. Never choose automatically.
- **Character** (`character-samples-[name].md`): present all candidates and wait for the user's explicit selection for each character. Never choose automatically.
- **Prose** (`chapter-[NN]-samples.md`): select the highest-probability candidate without prompting by default. If the user requested “show all options,” present all candidates and wait for an explicit choice. When probabilities tie within 0.02, choose the first and note the tie unless the user requested options.

For interactive choices, use OpenCode's supported question capability if available; otherwise ask the user conversationally. If the user cancels, preserve the sample file, set `selection_pending: true` in parent-owned `metadata.json`, and stop before writing or cleanup. Resume later from this selection stage, not by regenerating samples.

## Write selected content and update parent state

Before writing a character profile or selected chapter, load `../../docs/story-bible-schema.md` relative to this skill directory. Treat that schema as authoritative for the final file's required frontmatter and body. Copy the complete selected candidate body; remove only VS wrapper fields (sample number, probability, differentiator, diversity dimensions) that do not belong in the final file. Do not summarize, truncate, or rewrite any selected creative content.

Write the complete selected candidate to its destination with schema-required frontmatter:

| Sample | Destination |
| --- | --- |
| Concept | `.story-state/[Story]/concept-approved.md`, including `selected_sample` and `selection_probability` metadata |
| Character | `.story-state/[Story]/characters/[role]-[name].md`; frontmatter includes required `name`, `role`, `created`, and `last_updated` from the story-bible schema |
| Prose | `.story-state/[Story]/chapters/chapter-[NN].md`; frontmatter includes schema-required `chapter_number`, `chapter_title`, `word_count`, `target_word_count`, `generated`, `quality_checked`, and `status` |

### Selected character frontmatter

Derive `name` and `role` from the selected sample's `character_name` and `role`; set both dates to the current ISO date:

```yaml
---
name: "[Character name]"
role: "[protagonist|antagonist|supporting]"
created: "[YYYY-MM-DD]"
last_updated: "[YYYY-MM-DD]"
---
```

Use the story-bible schema's `# Character Profile: [Name]` heading and preserve every selected profile section/body in full.

### Selected chapter frontmatter before first review

Initialize a generated chapter as pending review without claiming it has passed:

```yaml
---
chapter_number: [N]
chapter_title: "[Title from PLAN.md]"
word_count: [count of complete selected prose]
target_word_count: "[target from PLAN.md]"
generated: "[YYYY-MM-DD]"
quality_checked: false
quality_review_status: pending
status: complete
---
```

The body contains the chapter heading followed by the complete selected prose. Verify all required fields and the full body were written before changing parent metadata or deleting samples. `quality_checked: false` and `quality_review_status: pending` are the required initial state until the parent applies a reviewer result.

Only after the destination write succeeds, update parent-owned metadata: `concept-sampling` → `concept-approved`, `character-sampling` → `character-approved`, or `prose-sampling` → `prose-approved`; set `selection_pending: false` and record the chosen sample/probability in generation notes. A failed destination write must not advance phase or delete the sample file; preserve state and offer retry/recovery.

Only after a successful chosen-content write and state update, delete the corresponding sample file. If deletion fails, warn but continue; the chosen content remains valid. Do not clean up samples on cancellation, failed writes, or before successful selection.

Return a concise summary of selected candidate, probability, differentiator, destination, phase transition, and whether cleanup succeeded. The parent then proceeds to the next workflow stage.

## Recovery

- Fewer than five candidates: warn and allow choice among available candidates.
- Malformed probabilities: use equal weights, warn, and retain the recorded original data if possible.
- Malformed sample structure: best-effort parse; report unparseable entries and require at least one usable candidate.
- User rejects all options: ask what should change and offer to regenerate samples with user guidance; do not discard existing samples without permission.
- Cancellation: preserve samples and mark selection pending for resume.
- Cleanup failure: warn, but do not roll back a successful selection.
