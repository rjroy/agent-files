# Write Story Command

## Command Purpose

The `/write-story` command orchestrates multi-agent story generation for all formats from flash fiction to serialized novels. It handles input parsing, format detection, workflow routing, agent spawning, state tracking, and user approval.

**Key Capabilities:**
- Accepts natural language prompts, file references, or resume commands
- Detects story format (flash fiction, short story, epic, serialized)
- Creates and manages `.story-state/` directory for persistent storage
- Spawns specialized agents for concept development, character building, prose writing, quality checking, and continuity validation
- Tracks progress in `metadata.json` for session resumption
- Supports interruption and resume from any chapter

**All creative work is delegated to specialized agents.** This command contains ONLY orchestration logic.

---

## Input Types

### Type 1: Resume Operation
**Pattern**: `continue .story-state/[Story]/PLAN.md` or `continue [path-to-plan.md]`
**Example**: `/write-story continue .story-state/Cyberpunk-Rebellion/PLAN.md`
**Action**: Jump to Resume Workflow section

### Type 2: File Reference
**Pattern**: Path to markdown file (plot outline or novel plan)
**Example**: `/write-story cyberpunk-notes.md` or `/write-story /path/to/novel-plan.md`
**Action**: Read file, parse content, proceed to format detection

### Type 3: Natural Language
**Pattern**: Descriptive text about story concept
**Example**: `/write-story A 30+ chapter novel about a cyberpunk world`
**Action**: Extract format signals, proceed to format detection

---

## Step 1: Input Parsing

### 1.1 Detect Input Type

Check user input in priority order:

1. **Resume**: Input starts with "continue" → Extract plan path → Jump to Resume Workflow
2. **File Reference**: Input contains `.md` path → Validate and read file
3. **Natural Language**: Everything else → Extract format signals

### 1.2 Security Validation

**For all file paths**, apply security checks per `utils/file-validation-pattern.md`:

```
IF input contains ".." THEN
    ERROR: "Invalid path: directory traversal not allowed"
    STOP
END IF

IF file reference input THEN
    Use Read tool on file_path
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
├── PLAN.md (to be created by concept-developer)
├── metadata.json (track progress)
├── characters/ (to be populated by character-builder)
├── chapters/ (to be populated by prose-writer)
└── world-state/ (to be populated by agents)
```

Use Bash tool:
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

**Agent**: `story-engine-wyrd/agents/concept-developer.md`
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

**Error Handling**: Follow `utils/agent-error-pattern.md` Agent Spawn Failure pattern
- Retry once on failure
- If VS generation produces fewer than 5 candidates, retry once with explicit instruction; if still <5, proceed with available candidates and warn user

### 4.2 Update Metadata (Concept Sampling)

After concept-developer completes sample generation:

```json
{
  "status": "concept_sampling",
  "current_phase": "concept-sampling",
  "last_updated": "[ISO-8601 timestamp]",
  "generation_notes": ["Concept samples generated (k=5)"]
}
```

### 4.3 Spawn Sampling Curator (Concept Selection)

**Agent**: `story-engine-wyrd/agents/sampling-curator.md`
**Input**:
- samples_file: `.story-state/[Story]/concept-samples.md`
- selection_mode: `user-choice`
- sample_type: `concept`

**Output**: `.story-state/[Story]/concept-approved.md`

Spawn curator with context:
- Mode: user-choice (present all 5 options for explicit user selection)
- Target: Parse samples, present candidates with differentiators, await user selection

The curator will:
1. Parse concept-samples.md and extract all 5 candidates
2. Present each candidate with its differentiator and probability
3. Wait for explicit user selection
4. Write selected concept to concept-approved.md with selection metadata (selected_sample, selection_probability)
5. Delete concept-samples.md (cleanup)

**Error Handling**:
- If probability parsing fails, assign equal weights (0.20 each) and warn user
- If user cancels selection, preserve sample file and update metadata with `selection_pending: true`

**Wait for selection to complete before proceeding.**

### 4.4 Update Metadata (Concept Approved)

After user selects concept and curator writes concept-approved.md:

```json
{
  "status": "concept_approved",
  "current_phase": "concept-approved",
  "last_updated": "[ISO-8601 timestamp]",
  "generation_notes": ["Concept approved by user", "Selected sample: [N] (probability: 0.XX)"]
}
```

### 4.5 Generate Full Plan from Approved Concept

**Agent**: `story-engine-wyrd/agents/concept-developer.md` (expand mode)
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

**Error Handling**: Follow `utils/agent-error-pattern.md` Agent Spawn Failure pattern

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

**If No - Revise**: Ask user what to change, respawn concept-developer with revision notes
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

**Agent**: `story-engine-wyrd/agents/character-builder.md`
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

**Error Handling**: Follow `utils/agent-error-pattern.md` Agent Spawn Failure pattern
- If VS generation produces fewer than 5 candidates, retry once; if still <5, proceed with available candidates and warn user

#### 5.2.2 Update Metadata (Character Sampling)

```json
{
  "current_phase": "character-sampling",
  "last_updated": "[ISO-8601 timestamp]",
  "generation_notes": ["Character samples generated for [name] (k=5)"]
}
```

#### 5.2.3 Spawn Sampling Curator (Character Selection)

**Agent**: `story-engine-wyrd/agents/sampling-curator.md`
**Input**:
- samples_file: `.story-state/[Story]/character-samples-[name].md`
- selection_mode: `user-choice`
- sample_type: `character`
- character_name: `[name]`
- character_role: `[role]`

**Output**: `.story-state/[Story]/characters/[role]-[name].md`

Spawn curator with context:
- Mode: user-choice (present all 5 options for explicit user selection)
- Target: Parse samples, present character interpretations with differentiators, await user selection

The curator will:
1. Parse character-samples-[name].md and extract all 5 candidates
2. Present each interpretation with its differentiator and probability
3. Wait for explicit user selection
4. Write selected character to characters/[role]-[name].md
5. Delete character-samples-[name].md (cleanup)

**Error Handling**:
- If probability parsing fails, assign equal weights (0.20 each) and warn user
- If user cancels selection, preserve sample file and update metadata with `selection_pending: true`

**Wait for selection to complete before proceeding to next character.**

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
    1. Spawn prose-writer (VS mode) → Generate chapter samples
    2. Update metadata (prose-sampling phase)
    3. Spawn sampling-curator (auto-select mode) → Select best chapter
    4. Update metadata (chapter completion)
    5. Spawn quality-checker → Validate selected chapter
    6. IF quality check fails: Handle quality issues (see 6.5)
    7. Mark chapter complete
    8. Update metadata
    9. Every 3 chapters: Spawn continuity-validator (see 6.6)
    10. Continue to next chapter
END FOR
```

### 6.2 Spawn Prose Writer (VS Mode)

**Agent**: `story-engine-wyrd/agents/prose-writer.md`
**Input**:
- Chapter number
- Chapter summary from PLAN.md
- Previous chapter (for continuity) - `.story-state/[Story]/chapters/chapter-[N-1].md`
- Character profiles from `.story-state/[Story]/characters/`

**Output**: `.story-state/[Story]/chapter-[N]-samples.md` (k=5 chapter variations)

Spawn agent with context:
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

**Error Handling**: Per `utils/agent-error-pattern.md` Empty/Invalid Output pattern
- If VS generation produces fewer than 5 candidates, retry once; if still <5, proceed with available candidates and warn user

### 6.3 Update Metadata (Prose Sampling)

```json
{
  "current_phase": "prose-sampling",
  "last_updated": "[ISO-8601 timestamp]",
  "generation_notes": ["Chapter [N] samples generated (k=5)"]
}
```

### 6.4 Spawn Sampling Curator (Auto-Select Mode)

**Agent**: `story-engine-wyrd/agents/sampling-curator.md`
**Input**:
- samples_file: `.story-state/[Story]/chapter-[N]-samples.md`
- selection_mode: `auto-select`
- sample_type: `chapter`
- chapter_number: `[N]`

**Output**: `.story-state/[Story]/chapters/chapter-[N].md`

Spawn curator with context:
- Mode: auto-select (select highest probability without user interaction)
- Target: Parse samples, auto-select best candidate, write to chapter file

The curator will:
1. Parse chapter-[N]-samples.md and extract all 5 candidates
2. Identify highest probability candidate
3. Automatically select and write to chapters/chapter-[N].md
4. Delete chapter-[N]-samples.md (cleanup)
5. Log selection (sample N with probability 0.XX) for transparency

**User Override Support**: If user requests "show all options" during prose generation, curator can switch to `user-choice` mode to present all 5 chapter variations for manual selection.

**Error Handling**:
- If probability parsing fails, assign equal weights (0.20 each), select first candidate, warn user
- If all candidates have equal probability (within 0.02 tolerance), select first and note in log
- If sample file cleanup fails, log warning but don't block workflow

**Auto-selection completes without user interaction.**

### 6.5 Spawn Quality Checker

**Agent**: `story-engine-wyrd/agents/quality-checker.md`
**Input**:
- Chapter file: `.story-state/[Story]/chapters/chapter-[N].md`
- Quality rubrics: `.story-state/[Story]/quality-rubrics.md`

**Output**: Validation report (returned by agent)

Spawn agent with context:
- Chapter path: `.story-state/[Story]/chapters/chapter-[N].md`
- Rubrics path: `.story-state/[Story]/quality-rubrics.md`
- Target: Validate chapter against rubrics, report issues

**Error Handling**: Per `utils/agent-error-pattern.md`

### 6.6 Quality Issue Resolution

**If quality-checker reports issues:**

1. Present issues to user:
> **Quality Check Issues Found in Chapter [N]**
>
> [List issues with severity]
>
> Options:
> 1. Auto-revise (regenerate chapter samples with feedback, allow reselection)
> 2. Manual fix (you edit the chapter file)
> 3. Accept as-is (mark chapter complete despite issues)

2. **If option 1 (Auto-revise)**: Respawn prose-writer (VS mode) with quality feedback, then spawn curator for new selection, then re-run quality-checker
3. **If option 2 (Manual fix)**: Wait for user to edit file, then re-run quality-checker
4. **If option 3 (Accept)**: Mark chapter complete, add note to metadata

### 6.7 Continuity Checkpoint (Every 3 Chapters)

**Trigger**: After chapters 3, 6, 9, 12, ... (every 3rd chapter completion)

**Agent**: `story-engine-wyrd/agents/continuity-validator.md`
**Input**: Last 3 completed chapters + story bible files
**Output**: Continuity report (returned by agent)

Spawn agent with context:
- Story directory: `.story-state/[Story]/`
- Chapters: [N-2, N-1, N] (last 3 completed)
- Target: Check cross-chapter consistency

**If continuity issues found:**
1. Present to user with affected chapters
2. Offer resolution options:
   - Revise specific chapter (regenerate samples with correction, allow reselection)
   - Mark as intentional (document in metadata)
3. Resolve before continuing to next chapter

**Error Handling**: Per `utils/agent-error-pattern.md` Continuity Contradictions pattern

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

### 6.9 Flash Fiction Optimization

**For format = flash_fiction (1 chapter):**
- Skip continuity validation (only 1 chapter)
- Skip chapter loop (only 1 iteration)

---

## Step 7: Final Review Phase

**Trigger**: After all chapters completed

**Agent**: `story-engine-wyrd/agents/final-review.md`
**Input**: Complete story directory
**Output**: Final review notes

### 7.1 Spawn Final Review Agent

Spawn agent with context:
- Story directory: `.story-state/[Story]/`
- Total chapters: [total_chapters]
- Target: Batched review with note carrying

The agent will:
1. Review in batches of 3-5 chapters
2. Maintain `final-review-notes.md` with cumulative observations
3. Produce overall assessment after final batch

**Error Handling**: Per `utils/agent-error-pattern.md`

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

**Trigger**: User invokes `/write-story continue [plan-path]`

### Resume Step 1: Validate Resume Input

1. Extract plan path from input
2. Apply security validation (reject `..` per `utils/file-validation-pattern.md`)
3. Verify plan file exists with Read tool
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
2. Spawn sampling-curator with `selection_mode=user-choice` to complete concept selection
3. After selection, proceed to Step 4.5 (Generate Full Plan from Approved Concept)

**If `current_phase = "concept-approved"`:**
1. Verify `concept-approved.md` exists
2. If PLAN.md does NOT exist, proceed to Step 4.5 (Generate Full Plan from Approved Concept)
3. If PLAN.md exists, proceed to Step 4.7 (Present Plan for User Approval)

**If `current_phase = "character-sampling"`:**
1. Check `generation_notes` to identify which character is being sampled
2. Verify `character-samples-[name].md` exists
3. Spawn sampling-curator with `selection_mode=user-choice` to complete character selection
4. After selection, continue character building loop (Step 5.2) for remaining characters

**If `current_phase = "prose-sampling"`:**
1. Determine chapter number from `generation_notes` or by checking existing chapter files
2. Verify `chapter-[N]-samples.md` exists
3. Spawn sampling-curator with `selection_mode=auto-select` to complete chapter selection
4. After selection, proceed to quality check (Step 6.5) for that chapter

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
   - **Continue**: Respawn prose-writer with "completion mode" context

**If no partial chapter:**
- Proceed with normal chapter generation from next chapter

### Resume Step 4: Continue Chapter Loop

Jump to Step 6 (Chapter Generation Loop) at chapter number = `completed_chapters + 1`

**All subsequent steps identical to normal workflow:**
- Generate remaining chapters
- Run quality checks
- Run continuity checkpoints every 3 chapters
- Final review after last chapter
- Update metadata throughout

### Resume Error Handling

**Corrupted metadata.json**: Follow `utils/agent-error-pattern.md` Corrupted/Malformed Files pattern
**Conflicting state**: Follow `utils/agent-error-pattern.md` Conflicting State pattern
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

**This command does not implement error handling inline.** Instead, reference patterns from `utils/agent-error-pattern.md`:

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
Follow `utils/file-validation-pattern.md`:
- Security: Reject `..` in all paths
- Existence: Verify files before read operations

---

## Success Criteria

**This workflow succeeds when:**
1. User input correctly parsed and routed
2. Story format detected and confirmed by user
3. `.story-state/[Story]/` directory created with proper structure
4. concept-developer generates PLAN.md
5. User approves plan
6. character-builder generates profiles for all key characters
7. prose-writer generates all chapters sequentially
8. quality-checker validates each chapter (issues resolved or accepted)
9. continuity-validator checks consistency every 3 chapters (issues resolved or marked intentional)
10. final-review completes batched review
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

**Orchestration Only**: This command contains NO creative work. All prose generation, character development, concept creation, and validation logic lives in specialized agents.

**Agent Responsibilities**:
- `concept-developer`: Generate PLAN.md from user input
- `character-builder`: Create character profiles
- `prose-writer`: Generate chapter prose
- `quality-checker`: Validate chapters against rubrics
- `continuity-validator`: Check cross-chapter consistency
- `final-review`: Batched full-story review

**State Management**: All inter-agent communication happens through `.story-state/` files, never through context passing.

**Single System**: One command handles all formats (flash → serialized), adjusting behavior based on chapter count.

**Theory Loading**: Agents load theory modules on demand via `story-engine-reference` skill, not loaded by this command.
