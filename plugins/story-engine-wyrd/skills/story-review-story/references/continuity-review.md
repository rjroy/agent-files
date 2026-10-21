# Continuity Review Procedure

**Purpose**: Detect contradictions across multiple chapters using available file-search capability for systematic pattern matching. Cross-references character files, world-state files, timeline files, and plot threads to identify inconsistencies. Outputs detailed contradiction report with chapter:line references.

---

## Agent Role

Apply this procedure when the shared story reviewer is invoked in continuity mode. Detect contradictions across the requested chapters. Your job is to systematically search through generated chapters using the available file-search capability to find contradictions in character traits, world mechanics, timeline chronology, and plot threads by cross-referencing against canonical story bible files.

**Core Responsibilities**:
- Use available file-search capability for pattern matching (NOT manual chapter reading)
- Cross-reference findings against canonical story bible files
- Output detailed contradiction report with chapter:line references (e.g., "Ch. 5 Line 234 vs. Ch. 8 Line 567")
- Honor the range and purpose supplied by the parent workflow (automatic checkpoint defaults to every 3 chapters; on-demand review covers all completed chapters)

---

## Input Context Files

### 1. metadata.json
**Location**: `.story-state/[Story-Title]/metadata.json`

**Extract**:
- `completed_chapters`: Total chapters generated
- `continuity_checkpoints`: Array of chapter numbers completed by automatic checkpoints; on-demand reviews do not change this metadata
- `continuity_checkpoint_interval`: Custom interval (default: 3)

**Purpose**: Supply completion bounds and, only for an automatic checkpoint with no explicit range, the last automatic checkpoint. A caller-supplied range always takes precedence.

### 2. PLAN.md
**Location**: `.story-state/[Story-Title]/PLAN.md`

**Extract**:
- Frontmatter: `title`, `total_chapters`, `world`
- Chapter summaries: Plot threads, character arcs, major events

**Purpose**: Identify expected thread progression and events

### 3. Character Files
**Location**: `.story-state/[Story-Title]/characters/`

**Files**: All `protagonist-*.md`, `antagonist-*.md`, `supporting-*.md`

**Extract from each**:
- **Physical Description**: Eye color, hair, age, height/build, distinctive features, clothing, mannerisms
- **Core Traits**: Distinctive voice, external desire, internal need, fear
- **Relationships**: Established connections with other characters

**Purpose**: Canonical source of truth for character traits

### 4. World-State Files
**Location**: `.story-state/[Story-Title]/world-state/`

**Files**:
- `mechanics.md`: World rules, capabilities, limitations, usage history
- `locations.md`: Descriptions, spatial relationships, appearance history
- `timeline.md`: Story duration, event chronology, time passage, flashbacks

**Purpose**: Canonical source of truth for world rules and chronology

### 5. Plot Thread Files
**Location**: `.story-state/[Story-Title]/plot-threads/`

**Files**:
- `thread-status.md`: Active/resolved/abandoned threads
- `thread-*.md`: Individual thread progression notes

**Purpose**: Track thread status to detect premature resolution or reappearance

---

## Validation Categories (REQ-F-27)

### 1. Character Inconsistencies

**Physical Traits**: Eye color, hair color/style, age, height, distinctive features
- Search for `[Character Name].*(eyes|eye color|hair|age|years old)`
- Cross-reference matches against canonical character files
- Flag contradictions with chapter:line references

**Personality/Voice Drift**: Speech patterns, vocabulary, formality
- Search for `[Character Name].*:\s*\"` to extract dialogue
- Compare early chapters vs. current batch for voice consistency
- Flag major shifts without narrative justification

**Character Knowledge**: Knowledge reveals and anachronisms
- Search for knowledge-related keywords (specific reveals tracked in timeline.md)
- Verify knowledge was revealed in prior chapter
- Flag references to information before reveal chapter

**Relationships**: Established vs. first meeting contradictions
- Search for `met.*first time|first met|worked together for.*years`
- Cross-reference against canonical relationship descriptions
- Flag contradictions in relationship timeline

### 2. World Rule Violations

**Mechanics/Rules**: Magic systems, technology capabilities, established limitations
- Search for rule keywords from mechanics.md
- Read matching passages with surrounding context
- Verify usage matches canonical capabilities/limitations
- Flag violations with canonical rule citation

**Location Descriptions**: Appearance, layout, atmosphere
- Search for location names
- Cross-reference descriptions against canonical locations.md
- Flag contradictory descriptions (e.g., "vertical hall" vs. "open halls")

**Geographic/Travel**: Spatial relationships, travel times
- Search for `walked from|traveled to|journey.*took`
- Verify travel times match canonical spatial relationships
- Flag impossible travel times

### 3. Timeline Contradictions

**Event Chronology**: Time passage consistency
- Search for `days? later|weeks? later|days? (since|after|before)|the next (day|morning|week)`
- Cross-reference with timeline.md event dates
- Calculate expected vs. actual dates
- Flag time passage errors

**Flashbacks**: Documented flashbacks and age math
- Search for `years ago|years earlier|flashback|remembered when`
- Verify flashbacks documented in timeline.md
- Check age math (current age - years ago = flashback age)
- Flag undocumented flashbacks and math errors

**Event Sequence**: Logical order (no effect-before-cause)
- Search for event keywords from timeline.md
- Verify events referenced in correct chapter order
- Flag anachronistic references

### 4. Plot Holes

**Premature Thread Resolutions**: Active threads resolved too early
- Search for thread keywords from thread-status.md
- Check if active thread described as resolved
- Flag premature resolutions with expected resolution context

**Resolved Threads Reappearing**: Completed threads treated as ongoing
- Search for resolved thread keywords
- Verify no post-resolution references treat thread as active
- Flag reappearances

**Missing Thread Progression**: Expected beats absent from prose
- Search for thread advancement keywords from PLAN.md chapter summaries
- Verify expected progression present in chapter
- Flag missing beats

**Abandoned Threads Reappearing**: Dropped threads referenced again
- Search for abandoned thread keywords
- Verify no post-abandonment references
- Flag reappearances without narrative justification

---

## Validation Process

### Step 1: Determine Validation Scope

Read `completed_chapters` from `metadata.json` and inspect the caller's request:

- **If the caller supplied a range**, use that exact start and end for every read, search, report heading, and finding. Do not narrow it by `continuity_checkpoints`, even if the requested range overlaps earlier checkpoints. If its end exceeds `completed_chapters`, report the bound and cap only the end to the highest completed chapter.
- **Only if this is an automatic checkpoint and no range was supplied**, calculate the range from the last automatic checkpoint plus one through `completed_chapters`; if there is no prior automatic checkpoint, start at chapter 1.
- Do not infer “automatic checkpoint” from metadata alone; the parent caller identifies review purpose and range.

Example: with 12 completed chapters and a checkpoint at 12, an explicit on-demand request for chapters 1–12 still reviews chapters 1–12. The checkpoint history never overrides a caller-supplied range.

**Special Cases**:
- First automatic checkpoint with no supplied range: validate chapters 1 through the configured interval (default 1-3)
- On-demand review: the caller supplies chapters 1 through the highest completed chapter; review that entire range
- No gaps in an automatic checkpoint: validate the full range since the last automatic checkpoint

### Step 2: Execute Search-Based Pattern Matching

For each validation category:

1. Read canonical files to extract search terms and values.
2. Use the available OpenCode file-search capability to search chapter files for those terms and likely contradictions.
3. Inspect matching files and surrounding passages with available file-reading tools; do not rely on an assumed search-tool option or shell syntax.
4. Record source paths and line references when the tools provide them, and verify each match against its canonical source.
5. Flag only supported contradictions with specific chapter references.

**Search Guidance**:
- Search only chapter files within the selected range using the available file-search capability; do not silently skip or widen chapters based on checkpoint history.
- Use pattern searches for likely terms, then read the matching chapter passages and canonical files to confirm.
- Cite line numbers only when available from the file-reading/search results; never invent line numbers.

### Step 3: Compile Contradiction Report

For each flagged contradiction, document:
- **Category**: Character/World/Timeline/Plot
- **Canonical Source**: File and value
- **Contradiction**: Chapter:line reference and contradictory text
- **Severity**: Critical (breaks continuity), Moderate (noticeable), Minor (optional fix)
- **Recommendation**: Specific action to resolve

---

## Contradiction Report Format

```markdown
# Continuity Validation Report: Chapters [X]-[Y]

**Story**: [Story Title]
**Chapters Validated**: [X] through [Y]
**Validation Date**: [YYYY-MM-DD]
**Previous Checkpoint**: Chapter [N]
**Total Contradictions Found**: [Count]

---

## Validation Summary

**Contradiction Categories**:
- Character Inconsistencies: [N] found
- World Rule Violations: [N] found
- Timeline Contradictions: [N] found
- Plot Holes: [N] found

**Severity Breakdown**:
- Critical: [N] (must fix before proceeding)
- Moderate: [N] (should fix)
- Minor: [N] (optional)

**Overall Status**: [PASS / FAIL / CONDITIONAL PASS]

---

## Detailed Findings

### 1. Character Inconsistencies

[For each contradiction:]

**[Character Name] - [Trait Type]**
- **Canonical** ([file path]): [canonical value]
- **Ch. [N] Line [L]**: "[text]" ✓/✗
- **Severity**: [Critical/Moderate/Minor]
- **Recommendation**: [Specific fix]

### 2. World Rule Violations

[Same structure as above]

### 3. Timeline Contradictions

[Same structure as above]

### 4. Plot Holes

[Same structure as above]

---

## Contradiction Resolution Recommendations

### Critical Issues (Must Fix Before Proceeding)

[List each critical contradiction with impact and fix]

### Moderate Issues (Should Fix)

[List each moderate contradiction]

### Minor Issues (Optional Fixes)

[List each minor contradiction]

---

## Validation Methodology

### Search Patterns Used

[List all patterns used with match counts]

### Cross-Reference Files Used

[List all canonical files referenced]

---

## Next Steps

### If CRITICAL Contradictions Found (FAIL):
1. Return report to parent workflow for the required resolution decision
2. Parent presents user options: revise chapters, update canonical files, or mark as intentional deviation
3. At automatic checkpoints, parent blocks progression until contradictions are resolved; on-demand reports remain informational
4. Parent updates metadata and chapter state as appropriate

### If Only MODERATE/MINOR Contradictions (CONDITIONAL PASS):
1. Return report for optional fixes
2. Parent may proceed when moderate issues are acceptable
3. Parent may carry issues into final review

### If NO Contradictions (PASS):
1. Return clean report; parent updates metadata.json continuity_checkpoints for automatic checkpoints
2. Parent may continue to next chapter batch

---

## Sign-Off

**Story Reviewer (continuity mode)**: Findings complete
**Total Contradictions**: [N] Critical, [N] Moderate, [N] Minor
**Recommendation**: [RESOLVE CRITICAL ISSUES / CONDITIONAL APPROVAL / FULL APPROVAL]
```

---

## Error Handling

### Missing Story Bible Files
**Pattern**: Follow agent-error-pattern.md for file validation failures

If canonical files missing:
```
ERROR: Cannot validate continuity without canonical source files

Missing Files:
- characters/protagonist-aria.md (required for character trait validation)
- world-state/mechanics.md (required for world rule validation)

Recommendation: Ensure the `creator` agent has completed the concept-developer and character-builder procedures
story bible files before running continuity validation.
```

### No Previous Checkpoint (Automatic First Validation)

If no explicit range was supplied and `continuity_checkpoints` has no prior automatic checkpoint:
- Note this is first checkpoint
- Validate chapters 1 through interval
- Focus on internal consistency within validated range
- Establish baseline for future validations

An explicit caller-supplied range remains authoritative even when the checkpoint array is empty or already includes its end chapter.

### Empty Search Results

If the available file-search capability returns no matches:
- Record pattern and path in the report methodology
- Continue validation (no matches = no contradictions for that term)
- Note in methodology section

### Invalid Chapter Range

If requested range exceeds completed chapters:
```
ERROR: Invalid chapter range for validation

Requested: Chapters 10-15
Completed: 12 chapters (per metadata.json)

Recommendation: Preserve the requested start and validate only through the highest completed chapter (10-12)
```

---

## Example Workflow

### Standard Checkpoint (Chapters 10-12)

**Orchestrator Input**:
- Story: ".story-state/Memory's-Price/"
- Interval: 3
- Completed: 12
- Last checkpoint: 9

**Your Process**:

1. Read metadata.json → Extract scope (validate 10-12)

2. Read canonical files:
   - PLAN.md
   - characters/*.md
   - world-state/*.md
   - plot-threads/*.md

3. Use the available OpenCode file-search capability for character, world-mechanics, timeline, and plot-thread terms; inspect matching passages and canonical sources with file-reading tools. Record only supported line references.

4. Compile report:
   - Character: 1 contradiction
   - World: 1 violation
   - Timeline: 1 contradiction
   - Plot: 1 premature resolution
   - **Total: 4 contradictions (3 critical, 1 moderate)**

5. Determine status: **FAIL** (critical contradictions present)

6. Return detailed report and proposed affected chapters to parent; do not edit metadata or source files

### On-Demand Full Review with an Existing Final Checkpoint

**Caller Input**:
- Story: `.story-state/Memory's-Price/`
- Requested range: chapters 1-12
- Completed: 12
- Last checkpoint: 12

The explicit range is authoritative: inspect and report on chapters 1-12. Do not reduce this request to an empty range because the latest automatic checkpoint is already chapter 12.

---

**End of Continuity Review Procedure**
