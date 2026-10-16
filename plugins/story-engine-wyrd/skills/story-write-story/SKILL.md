---
name: story-write-story
description: Orchestrate the resumable, user-approved story creation workflow from concept sampling through chapters and final review.
---

**Conversational use:** Accept the user request and any available context directly; do not require slash-command syntax or a positional `$ARGUMENTS` string. Clarify only missing required choices. Use OpenCode-supported file and subagent capabilities.

# story-write-story Skill

## Command Purpose

This skill orchestrates multi-agent story generation for all formats from flash fiction to serialized novels. It handles conversational input, format detection, workflow routing, agent delegation, state tracking, and user approval.

**Key Capabilities:**
- Accepts natural language prompts, file references, or resume workflows
- Detects story format (flash fiction, short story, epic, serialized)
- Creates and manages `.story-state/` directory for persistent storage
- Spawns specialized agents for concept development, character building, prose writing, quality, continuity, and final review
- Tracks progress in `metadata.json` for session resumption
- Supports interruption and resume from any chapter

**All creative work is delegated to specialized agents.** This skill contains orchestration and parent-owned sample-selection logic. Delegate through OpenCode's subagent capability, using the final Slim agent IDs listed below; do not rely on retired host-specific delegation syntax.

Before the parent writes a selected character profile or chapter, load `../../docs/story-bible-schema.md` relative to this skill directory. The parent applies that schema's required frontmatter; the selected sample body does not supply final-file frontmatter.

---

## Input Types

### Type 1: Resume Operation
**Pattern**: Detect explicit continuation or resume intent anywhere in the user's request, paired with a plan path; do not require "continue" or "resume" to be the first word.
**Example**: "Please resume .story-state/example/PLAN.md" or "Continue the story at `.story-state/Cyberpunk-Rebellion/PLAN.md`."
**Action**: Extract the plan path and jump to Resume Workflow before considering any `.md` path as new-story source material.

### Type 2: Natural Language
**Pattern**: A descriptive story request that does not indicate resuming an existing story.
**Example**: "Write a 30+ chapter novel about a cyberpunk world."
**Action**: Extract format signals, proceed to format detection

### Type 3: File Reference
**Pattern**: Path to markdown file (plot outline or novel plan)
**Example**: "Use `cyberpunk-notes.md` as the starting outline."
**Action**: Read file, parse content, proceed to format detection

---

## Step 1: Input Parsing

### 1.1 Detect Input Type

Check user input in priority order:

1. **Resume**: If the request explicitly asks to continue/resume an existing story and includes its plan path, extract that path and jump to Resume Workflow, regardless of where the intent appears.
2. **Natural Language**: If there is no resume intent and no source file, extract format signals.
3. **File Reference**: If there is no resume intent and the user supplies a source `.md` path (such as an outline), validate and read it as new-story input.

### 1.2 Security Validation

**For all file paths**, apply security checks per `../../utils/file-validation-pattern.md` (resolved from this skill's directory):

```
IF input contains ".." THEN
    ERROR: "Invalid path: directory traversal not allowed"
    STOP
END IF

IF file reference input THEN
    Read the referenced file with available OpenCode file-reading tools
    IF Read fails THEN
        ERROR: "File not found: [file_path]"
        STOP
    END IF
END IF
```

### 1.3 Format Signal Extraction (Natural Language Only)

**Format Keywords:**
- Flash Fiction: "flash", "flash fiction"
- Short Story: "short", "short story"
- Epic: "epic", "10,000+", "10k+", "10000+"
- Serialized: "serialized", "30+ chapter", "novel", "chapter-by-chapter"

**Priority**: Serialized > Epic > Short Story > Flash Fiction

---

## Step 2: Format Detection and Confirmation

### 2.1 Determine Format

**From Natural Language**: Use detected format keywords
**From File Reference**: Scan file content for chapter count, structure hints, or explicit format declarations

### 2.2 User Confirmation

Present detected format to user:

> "I detected you want to create a **[detected format]** story. Is this correct?"
>
> Options: [Yes] [No - Flash Fiction] [No - Short Story] [No - Epic] [No - Serialized]

If no format detected:

> "What story format would you like?"
>
> Options: [Flash Fiction (1 chapter)] [Short Story (2-5 chapters)] [Epic (6-15 chapters)] [Serialized (15+ chapters)]

Record confirmed format for workflow routing.

---

## Step 3: Directory Initialization

### 3.1 Title Sanitization

Extract story title from input or file, then sanitize for directory naming:

**Rules:**
1. Remove special characters except spaces, hyphens, underscores
2. Replace spaces with hyphens
3. Convert to lowercase
4. Limit to 50 characters
5. Remove leading/trailing hyphens

**Example**: "The Cyberpunk Rebellion!" → "the-cyberpunk-rebellion"

### 3.2 Create Directory Structure

```
.story-state/[sanitized-title]/
├── PLAN.md (to be created by story-engine-wyrd-concept-developer)
├── metadata.json (track progress)
├── characters/ (to be populated by story-engine-wyrd-character-builder)
├── chapters/ (to be populated by story-engine-wyrd-prose-writer)
└── world-state/ (to be populated by agents)
```

Create the requested directories with available OpenCode filesystem tools (or a narrowly scoped shell workflow):
```bash
mkdir -p .story-state/[sanitized-title]/{characters,chapters,world-state}
```

### 3.3 Initialize Metadata

Create `metadata.json`:

```json
{
  "title": "[Original Title]",
  "format": "[flash_fiction|short_story|epic|serialized]",
  "status": "planning",
  "created": "[ISO-8601 timestamp]",
  "last_updated": "[ISO-8601 timestamp]",
  "total_chapters": null,
  "completed_chapters": 0,
  "current_phase": "concept_development",
  "generation_notes": []
}
```

---

## Step 4: Plan Generation Workflow

### 4.1 Spawn Concept Developer (VS Mode)

**Agent**: `story-engine-wyrd-concept-developer`
**Input**: User's original input (natural language or file content)
**Output**: `.story-state/[Story]/concept-samples.md` (k=5 concept candidates)

Spawn agent with context:
- Format: [confirmed format]
- Input type: [natural language | file reference]
- Content: [user's input or file content]
- Mode: verbalized_sampling
- Target: Generate 5 distinct concept candidates with probabilities and differentiators

The agent will explore diversity dimensions (narrative voice, structural approach, emotional arc, thematic focus) and generate 5 concept variations, each with:
- Probability score (0.XX format)
- One-sentence differentiator explaining unique creative direction
- Diversity dimensions used
- Full concept content (story concept, character summary, chapter preview)

**Error Handling**: Follow `../../utils/agent-error-pattern.md` Agent Spawn Failure pattern
- Retry once on failure
- If VS generation produces fewer than 5 candidates, retry once with explicit instruction; if still <5, proceed with available candidates and warn user

### 4.2 Update Metadata (Concept Sampling)

After story-engine-wyrd-concept-developer completes sample generation:

```json
{
  "status": "concept_sampling",
  "current_phase": "concept-sampling",
  "last_updated": "[ISO-8601 timestamp]",
  "generation_notes": ["Concept samples generated (k=5)"]
}
```

### 4.3 Select the Concept (Parent Workflow)

Apply the parent-owned `sample-selection.md` procedure to `.story-state/[Story]/concept-samples.md` in explicit user-choice mode. Present all candidates without recommendation, wait for the user's explicit choice, and write the complete selected concept to `.story-state/[Story]/concept-approved.md` with selection metadata. Do not proceed until selection succeeds. On cancellation, preserve samples and mark `selection_pending: true`; resume at this selection step. Clean up the samples only after the destination write and metadata update both succeed.

### 4.4 Update Metadata (Concept Approved)

After the parent writes concept-approved.md following user selection:

```json
{
  "status": "concept_approved",
  "current_phase": "concept-approved",
  "last_updated": "[ISO-8601 timestamp]",
  "generation_notes": ["Concept approved by user", "Selected sample: [N] (probability: 0.XX)"]
}
```

### 4.5 Generate Full Plan from Approved Concept

**Agent**: `story-engine-wyrd-concept-developer` (expand mode)
**Input**: `.story-state/[Story]/concept-approved.md`
**Output**:
- `.story-state/[Story]/PLAN.md` (full chapter breakdown)
- `.story-state/[Story]/quality-rubrics.md`
- `.story-state/[Story]/world-state/mechanics.md`
- `.story-state/[Story]/plot-threads/thread-status.md`

Spawn agent with context:
- Mode: expand_approved_concept
- Input file: concept-approved.md
- Format: [confirmed format]
- Target: Generate complete PLAN.md with all chapter summaries and supporting story bible files

The agent will:
1. Read the approved concept from concept-approved.md
2. Expand it into full PLAN.md with detailed chapter breakdowns
3. Generate quality-rubrics.md based on the concept's genre and tone
4. Initialize world-state/mechanics.md for world rules
5. Initialize plot-threads/thread-status.md for narrative tracking
6. Preserve selection metadata in PLAN.md frontmatter (selected_sample, selection_probability)

**Error Handling**: Follow `../../utils/agent-error-pattern.md` Agent Spawn Failure pattern

### 4.6 Update Metadata (Plan Created)

After full plan generation completes:

```json
{
  "status": "plan_created",
  "total_chapters": [from PLAN.md],
  "current_phase": "awaiting_plan_approval",
  "last_updated": "[ISO-8601 timestamp]",
  "generation_notes": ["Full plan generated from approved concept"]
}
```

### 4.7 Present Plan for User Approval

Read `.story-state/[Story]/PLAN.md` and extract:
- Title
- Format
- Total chapters
- Chapter summaries (first 3-5 chapters)
- Key characters
- World/setting

Present to user:

> **Story Plan: [Title]**
>
> Format: [format] ([total_chapters] chapters)
>
> **Summary**: [from PLAN.md]
>
> **Key Characters**: [list]
>
> **Chapters** (showing first 5):
> 1. [Chapter 1 title and brief summary]
> 2. [Chapter 2 title and brief summary]
> ...
>
> **Full plan available at**: `.story-state/[Story]/PLAN.md`
>
> **Do you approve this plan?** [Yes - Proceed] [No - Revise] [Cancel]

**If No - Revise**: Ask user what to change, respawn story-engine-wyrd-concept-developer with revision notes
**If Cancel**: Stop workflow, preserve files for later
**If Yes**: Proceed to character building

### 4.8 Update Metadata After Approval

```json
{
  "status": "plan_approved",
  "current_phase": "character_building",
  "last_updated": "[ISO-8601 timestamp]",
  "generation_notes": ["Plan approved by user"]
}
```

---

## Step 5: Character Building Phase

### 5.1 Extract Character List from PLAN.md

Read PLAN.md and identify all named characters needing profiles.

**Criteria for profile creation:**
- Protagonist(s): Always
- Antagonist(s): Always
- Supporting characters with arc or significant role: Yes
- Minor/background characters: No (described inline in prose)

### 5.2 Character Generation Loop (Per Character with VS)

**For each character requiring a profile:**

#### 5.2.1 Spawn Character Builder (VS Mode)

**Agent**: `story-engine-wyrd-character-builder`
**Input**: Character name, role, relevant PLAN.md sections
**Output**: `.story-state/[Story]/character-samples-[name].md` (k=5 character interpretations)

Spawn agent with context:
- Character: [name]
- Role: [protagonist/antagonist/supporting]
- Plan reference: [relevant sections from PLAN.md]
- Mode: verbalized_sampling
- Target: Generate 5 distinct character interpretations with probabilities and differentiators

The agent will explore diversity dimensions (arc type, voice style, fear/desire balance, relationship dynamics) and generate 5 character variations, each with:
- Probability score (0.XX format)
- One-sentence differentiator explaining unique interpretation
- Diversity dimensions used
- Full character profile (core traits, physical description, arc, relationships)

**Error Handling**: Follow `../../utils/agent-error-pattern.md` Agent Spawn Failure pattern
- If VS generation produces fewer than 5 candidates, retry once; if still <5, proceed with available candidates and warn user

#### 5.2.2 Update Metadata (Character Sampling)

```json
{
  "current_phase": "character-sampling",
  "last_updated": "[ISO-8601 timestamp]",
  "generation_notes": ["Character samples generated for [name] (k=5)"]
}
```

#### 5.2.3 Select the Character (Parent Workflow)

Apply the parent-owned `sample-selection.md` procedure to `.story-state/[Story]/character-samples-[name].md` in explicit user-choice mode. Present all candidates without recommendation and wait for the user's explicit choice. Write the full selected profile to `.story-state/[Story]/characters/[role]-[name].md`. On cancellation, preserve samples and mark `selection_pending: true`; resume this character selection before continuing to the next character. Clean up samples only after the destination write and metadata update succeed.

#### 5.2.4 Update Metadata After Character Selection

```json
{
  "current_phase": "character_building",
  "last_updated": "[ISO-8601 timestamp]",
  "generation_notes": ["Character approved: [name] (selected sample: [N], probability: 0.XX)"]
}
```

### 5.3 Update Metadata After All Characters

```json
{
  "status": "characters_created",
  "current_phase": "chapter_generation",
  "last_updated": "[ISO-8601 timestamp]"
}
```

---

## Step 6: Chapter Generation Loop

**This is the core workflow** - iterate through all chapters sequentially.

### 6.1 Chapter Loop Structure

```
FOR chapter_num FROM 1 TO total_chapters:
    1. Spawn story-engine-wyrd-prose-writer (VS mode) → Generate chapter samples
    2. Update metadata (prose-sampling phase)
    3. Parent applies `sample-selection.md` and writes schema-complete chapter frontmatter/body
    4. Invoke a fresh `story-engine-wyrd-story-reviewer` in `quality` mode → Validate selected chapter (read-only)
    5. Parent records the reviewer result and resolves or explicitly accepts failures (see 6.6)
    6. Update metadata from the result; do not treat acceptance as a pass
    7. Every 3 chapters, invoke a fresh `story-engine-wyrd-story-reviewer` in `continuity` mode (see 6.7)
    8. Continue to next chapter
END FOR
```

### 6.2 Spawn Prose Writer (VS Mode)

**Agent**: `story-engine-wyrd-prose-writer`
**Input**:
- Chapter number
- Chapter summary from PLAN.md
- Previous chapter (for continuity) - `.story-state/[Story]/chapters/chapter-[N-1].md`
- Character profiles from `.story-state/[Story]/characters/`

**Output**: `.story-state/[Story]/chapter-[N]-samples.md` (k=5 chapter variations)

Spawn `story-engine-wyrd-prose-writer` with context:
- Story directory: `.story-state/[Story]/`
- Chapter: [N]
- Mode: verbalized_sampling
- Target: Generate 5 distinct chapter variations with probabilities and differentiators

The agent will explore diversity dimensions (scene construction, pacing rhythm, dialogue density, atmospheric approach) and generate 5 chapter versions, each with:
- Probability score (0.XX format)
- One-sentence differentiator explaining unique approach
- Diversity dimensions used
- Full chapter prose
- Word count

**Error Handling**: Per `../../utils/agent-error-pattern.md` Empty/Invalid Output pattern
- If VS generation produces fewer than 5 candidates, retry once; if still <5, proceed with available candidates and warn user

### 6.3 Update Metadata (Prose Sampling)

```json
{
  "current_phase": "prose-sampling",
  "last_updated": "[ISO-8601 timestamp]",
  "generation_notes": ["Chapter [N] samples generated (k=5)"]
}
```

### 6.4 Select the Chapter (Parent Workflow)

Apply `sample-selection.md` to `.story-state/[Story]/chapter-[N]-samples.md` in prose auto-select mode: select the highest probability sample without user interaction, unless the user explicitly requests “show all options.” The parent loads the story-bible schema, writes the full selected prose with required chapter frontmatter, verifies both, updates parent-owned phase/selection metadata, then cleans up the sample file only after every write succeeds. If cancelled or any write/verification fails, preserve samples and resume from selection.

### 6.5 Per-Chapter Quality Review

**Agent**: `story-engine-wyrd-story-reviewer` (mode: `quality`)
**Input**:
- Chapter file: `.story-state/[Story]/chapters/chapter-[N].md`
- Quality rubrics: `.story-state/[Story]/quality-rubrics.md`

**Output**: Validation report (returned by agent)

Invoke a fresh reviewer with context:
- Mode: quality
- Chapter path: `.story-state/[Story]/chapters/chapter-[N].md`
- Rubrics path: `.story-state/[Story]/quality-rubrics.md`
- Target: Validate chapter against rubrics, report issues

The reviewer only returns findings. The parent applies the result to schema-defined chapter frontmatter and `metadata.json`:
- **PASS**: `quality_checked: true`, `quality_review_status: "passed"`, `status: "complete"`; update issue counts and remove the chapter from `incomplete_chapters`.
- **FAIL**: `quality_checked: false`, `quality_review_status: "revision_needed"`, `status: "revision_needed"`; increment `quality_issues_found`, record the chapter as incomplete, and do not proceed until revised and passed or explicitly accepted by the user. Increment `quality_issues_resolved` only for issues actually fixed.
- **User accepts a failed review as-is**: `quality_checked` remains `false`, `quality_review_status: "accepted_with_issues"`, `status: "complete"`; retain the issue count and failure details, and record the user's explicit acceptance in `generation_notes`. Remove this chapter from `incomplete_chapters` only when its quality failure is the sole unresolved cause; preserve its incomplete marker if another cause remains, and never clear unrelated incomplete entries. Never convert the reviewer result to PASS or mark `quality_checked: true` without a fresh passing review.

**Error Handling**: Per `../../utils/agent-error-pattern.md`

### 6.6 Quality Issue Resolution

**If the quality-mode reviewer reports issues:**

1. Present issues to user:
> **Quality Check Issues Found in Chapter [N]**
>
> [List issues with severity]
>
> Options:
> 1. Auto-revise (regenerate chapter samples with feedback, allow reselection)
> 2. Manual fix (you edit the chapter file)
> 3. Accept as-is (mark chapter complete despite issues)

2. **If option 1 (Auto-revise)**: Respawn story-engine-wyrd-prose-writer (VS mode) with quality feedback, then apply `sample-selection.md` for the new selection, then invoke a fresh quality-mode reviewer
3. **If option 2 (Manual fix)**: Wait for user to edit file, then invoke a fresh quality-mode reviewer
4. **If option 3 (Accept)**: Apply the accepted-with-issues state above; acceptance permits workflow continuation but is not a passing review.

### 6.7 Continuity Checkpoint (Every 3 Chapters)

**Trigger**: After chapters 3, 6, 9, 12, ... (every 3rd chapter completion)

**Agent**: `story-engine-wyrd-story-reviewer` (mode: `continuity`)
**Input**: Last 3 completed chapters + story bible files
**Output**: Continuity report (returned by agent)

Invoke a fresh reviewer instance with context:
- Mode: continuity
- Story directory: `.story-state/[Story]/`
- Chapters: [N-2, N-1, N] (last 3 completed)
- Target: Check cross-chapter consistency

The reviewer is read-only. For **automatic checkpoints only**, after every result the parent appends the covered checkpoint to `continuity_checkpoints`, updates `continuity_checkpoint_results` with the actual status and issue count, and updates `continuity_issues_found` / `continuity_issues_resolved` from findings and fixes. For a failed checkpoint, use `status: "needs_revision"`, record affected chapters in `incomplete_chapters`, and block continuation. If the user explicitly accepts the contradictions as intentional, record `status: "accepted_with_issues"`, retain the issues-found count and acceptance note, remove only the accepted chapters from `incomplete_chapters`, and continue. Never record an accepted or failed checkpoint as `passed`. On-demand `story-review-story` runs remain read-only and informational; they do not alter metadata or gate generation.

**If continuity issues found:**
1. Present to user with affected chapters
2. Offer resolution options:
   - Revise specific chapter (regenerate samples with correction, allow reselection)
   - Mark as intentional (document in metadata)
3. Resolve before continuing to next chapter

**Error Handling**: Per `../../utils/agent-error-pattern.md` Continuity Contradictions pattern

### 6.8 Update Metadata After Each Chapter

```json
{
  "completed_chapters": [N],
  "current_phase": "chapter_generation",
  "last_updated": "[ISO-8601 timestamp]",
  "generation_notes": [
    "Chapter [N] completed (selected sample: [X], probability: 0.XX)",
    "Quality check: [passed|issues resolved|accepted with issues]"
  ]
}
```

Increment `completed_chapters` only after quality findings were passed or explicitly accepted. An accepted chapter may be complete, but its `quality_checked` stays `false` and its `quality_review_status` stays `accepted_with_issues`.

### 6.9 Flash Fiction Optimization

**For format = flash_fiction (1 chapter):**
- Skip continuity validation (only 1 chapter)
- Skip chapter loop (only 1 iteration)

---

## Step 7: Final Review Phase

**Trigger**: After all chapters completed

**Agent**: `story-engine-wyrd-story-reviewer` (mode: `final-review`)
**Input**: Complete story directory
**Output**: Final review notes

### 7.1 Invoke Final-Review Mode

Invoke a fresh reviewer instance with context:
- Mode: final-review
- Story directory: `.story-state/[Story]/`
- Total chapters: [total_chapters]
- Batch range: [start-end], with carry-forward notes returned by the immediately preceding batch (if any)
- Target: Batched review with note carrying; do not reuse a prior reviewer instance

The reviewer returns findings and carry-forward notes only. The parent reviews contiguous batches of 3-5 chapters sequentially, invokes a fresh instance per batch, passes forward notes, and writes each returned report section to `.story-state/[Story]/final-review-notes.md`; the final batch includes the overall assessment. For a resumed final review, recover the latest carry-forward notes from that report before invoking a fresh reviewer. The parent owns this report artifact and all workflow state.

**Error Handling**: Per `../../utils/agent-error-pattern.md`

### 7.2 Update Metadata

```json
{
  "status": "complete",
  "current_phase": "final_review_complete",
  "last_updated": "[ISO-8601 timestamp]",
  "generation_notes": ["Final review completed"]
}
```

---

## Step 8: Completion Output

Present completion message to user:

> **Story Complete: [Title]**
>
> Format: [format] ([total_chapters] chapters)
> Total word count: [sum from chapter frontmatter]
>
> **Files created:**
> - Plan: `.story-state/[Story]/PLAN.md`
> - Chapters: `.story-state/[Story]/chapters/chapter-1.md` through `chapter-[N].md`
> - Characters: `.story-state/[Story]/characters/` ([count] profiles)
> - Metadata: `.story-state/[Story]/metadata.json`
> - Final review: `.story-state/[Story]/final-review-notes.md`
>
> **Next steps:**
> - Review individual chapters for editing
> - Use the story compiler skill to generate full novel document
> - Manually edit story bible files if needed
>
> All files are in `.story-state/[Story]/` directory.

---

## Resume Workflow

**Trigger**: The user asks to continue a story and provides its plan path.

### Resume Step 1: Validate Resume Input

1. Extract plan path from input
2. Apply security validation (reject `..` per `../../utils/file-validation-pattern.md`)
3. Verify plan file exists with OpenCode file-reading tools
4. Extract story directory from plan path (parent directory)

### Resume Step 2: Load Story State

1. Read `metadata.json` from story directory
2. Validate metadata format (required fields: status, total_chapters, completed_chapters, current_phase)
3. Check `current_phase` for VS intermediate states (see Resume Step 2a for VS-specific handling)
4. Verify plan file consistency:
   - Compare provided plan path with story directory structure
   - If plan path doesn't match expected location (`.story-state/[title]/PLAN.md`), follow Conflicting State pattern
5. Read PLAN.md (if exists)
6. Determine resume point based on phase (see Resume Step 2a)

### Resume Step 2a: Handle VS Intermediate Phases

**Check `current_phase` field in metadata.json for VS sampling states:**

**If `current_phase = "concept-sampling"`:**
1. Verify `concept-samples.md` exists
2. Apply `sample-selection.md` in explicit user-choice mode to complete concept selection
3. After selection, proceed to Step 4.5 (Generate Full Plan from Approved Concept)

**If `current_phase = "concept-approved"`:**
1. Verify `concept-approved.md` exists
2. If PLAN.md does NOT exist, proceed to Step 4.5 (Generate Full Plan from Approved Concept)
3. If PLAN.md exists, proceed to Step 4.7 (Present Plan for User Approval)

**If `current_phase = "character-sampling"`:**
1. Check `generation_notes` to identify which character is being sampled
2. Verify `character-samples-[name].md` exists
3. Apply `sample-selection.md` in explicit user-choice mode to complete character selection
4. After selection, continue character building loop (Step 5.2) for remaining characters

**If `current_phase = "prose-sampling"`:**
1. Determine chapter number from `generation_notes` or by checking existing chapter files
2. Verify `chapter-[N]-samples.md` exists
3. Apply `sample-selection.md` in prose auto-select mode to complete chapter selection
4. After selection, invoke a fresh quality-mode reviewer (Step 6.5) for that chapter

**If `current_phase` is NOT a sampling state:**
- Proceed with standard resume logic (next step)

**VS Cleanup on Resume:**
- If sample files exist but phase has moved past sampling (e.g., `current_phase=chapter_generation` but `chapter-3-samples.md` exists), those are orphaned files from interrupted workflow
- Warn user about orphaned sample files and offer to delete them

### Resume Step 3: Handle Partial Chapter

**Check if next chapter file exists:**

```bash
test -f .story-state/[Story]/chapters/chapter-[next].md
```

**If partial chapter exists:**
1. Read chapter file
2. Check frontmatter status field
3. If status = "draft" or "incomplete":
   - Present to user: "Chapter [N] partially written. Options: [Rewrite from scratch] [Continue from where it left off]"
   - **Rewrite**: Delete file, proceed with normal chapter generation
   - **Continue**: Respawn story-engine-wyrd-prose-writer with "completion mode" context

**If no partial chapter:**
- Proceed with normal chapter generation from next chapter

### Resume Step 4: Continue Chapter Loop

Jump to Step 6 (Chapter Generation Loop) at chapter number = `completed_chapters + 1`

**All subsequent steps identical to normal workflow:**
- Generate remaining chapters
- Run quality-mode reviews
- Run continuity checkpoints every 3 chapters
- Final review after last chapter
- Update metadata throughout

### Resume Error Handling

**Corrupted metadata.json**: Follow `../../utils/agent-error-pattern.md` Corrupted/Malformed Files pattern
**Conflicting state**: Follow `../../utils/agent-error-pattern.md` Conflicting State pattern
**Missing story directory**: Error "Story state not found at [path]", offer to start new story

---

## State Tracking (metadata.json)

**Purpose**: Track progress for resumption, debugging, and user transparency

**Update frequency**: After every significant step
- Concept samples generated
- Concept selected
- Plan created
- Plan approved
- Character samples generated (per character)
- Character selected (per character)
- Chapter samples generated (per chapter)
- Chapter selected (per chapter)
- Quality check
- Continuity checkpoint
- Final review

**Fields:**
- `title`: Story title (string)
- `format`: Story format (string: flash_fiction, short_story, epic, serialized)
- `status`: Current status (string: concept_sampling, concept_approved, plan_created, plan_approved, characters_created, generating_chapters, complete)
- `created`: Creation timestamp (ISO-8601)
- `last_updated`: Last modification timestamp (ISO-8601)
- `total_chapters`: Total chapter count (integer, null until plan created)
- `completed_chapters`: Completed chapter count (integer)
- `current_phase`: Current workflow phase (string - see Phase Values below)
- `generation_notes`: Audit trail (array of strings)

**Phase Values** (for `current_phase` field):
- `concept_development`: Initial phase, before VS
- `concept-sampling`: Awaiting user selection from concept samples
- `concept-approved`: Concept selected, generating full plan
- `awaiting_plan_approval`: PLAN.md created, awaiting user approval
- `character_building`: Building character profiles
- `character-sampling`: Awaiting user selection from character samples (includes character name in generation_notes)
- `chapter_generation`: Normal chapter generation phase
- `prose-sampling`: Awaiting auto-selection from chapter samples (includes chapter number in generation_notes)
- `final_review_complete`: All done

**VS-Specific Metadata:**
- When selection occurs, `generation_notes` includes: `"Selected sample: [N] (probability: 0.XX)"`
- This preserves transparency about which candidate was chosen and with what confidence

**Write pattern**: Read existing metadata, modify relevant fields, write back to file

---

## Error Handling References

**This skill does not implement error handling inline.** Instead, reference patterns from `../../utils/agent-error-pattern.md` (relative to this skill directory):

### Agent Spawn Failures
Follow Agent Spawn Failure pattern:
- Retry once with same parameters
- On second failure, present diagnostic info and recovery options

### File Write Failures
Follow File Write Failure pattern:
- Preserve in-memory state
- Offer retry/alternate location options

### Invalid Agent Output
Follow Empty/Invalid Output pattern:
- Retry with explicit instruction
- Escalate with manual generation option

### Corrupted State Files
Follow Corrupted/Malformed Files pattern:
- Report specific errors with line numbers
- Offer reinitialize/continue/repair options

### Continuity Contradictions
Follow Continuity Contradictions pattern:
- Present contradiction with affected chapters
- Offer revision/intentional options

### File Validation
Follow `../../utils/file-validation-pattern.md` (relative to this skill directory):
- Security: Reject `..` in all paths
- Existence: Verify files before read operations

---

## Success Criteria

**This workflow succeeds when:**
1. User input correctly parsed and routed
2. Story format detected and confirmed by user
3. `.story-state/[Story]/` directory created with proper structure
4. story-engine-wyrd-concept-developer generates PLAN.md
5. User approves plan
6. story-engine-wyrd-character-builder generates profiles for all key characters
7. story-engine-wyrd-prose-writer generates all chapters sequentially
8. story-engine-wyrd-story-reviewer in quality mode validates each chapter (issues resolved or accepted)
9. story-engine-wyrd-story-reviewer in continuity mode checks consistency every 3 chapters (issues resolved or marked intentional)
10. story-engine-wyrd-story-reviewer completes independently invoked final-review batches
11. `metadata.json` accurately reflects completion status
12. User receives completion message with file locations

**Resume workflow succeeds when:**
1. Plan path validated and loaded
2. metadata.json read successfully
3. Resume point determined (next chapter after last completed)
4. Partial chapters handled appropriately
5. Chapter generation continues from resume point
6. Story completes normally with all validations

---

## Notes

**Orchestration Only**: This workflow contains no prose generation, character development, or concept creation. It delegates creation to specialized agents; selection and workflow state remain parent-owned, while the shared reviewer returns read-only findings.

**Agent Responsibilities**:
- `story-engine-wyrd-concept-developer`: Generate PLAN.md from user input
- `story-engine-wyrd-character-builder`: Create character profiles
- `story-engine-wyrd-prose-writer`: Generate chapter prose
- `story-engine-wyrd-story-reviewer`: Read-only quality, continuity, or final review according to the single mode selected for each fresh invocation

**State Management**: Creation agents communicate through `.story-state/` files. The parent passes only the required review mode, range, and carry-forward notes to fresh reviewer invocations.

**Single System**: One workflow handles all formats (flash → serialized), adjusting behavior based on chapter count.

**Theory Loading**: Agents load theory modules on demand via `story-engine-reference` skill, not loaded by this workflow.
