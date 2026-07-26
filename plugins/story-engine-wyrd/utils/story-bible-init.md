# Story Bible Initialization Utility

**Version**: 1.0.0
**Purpose**: Implementation guide for initializing `.story-state/[Story-Title]/` directory structure with required subdirectories and starter files.
**Related Schema**: [story-bible-schema.md](../docs/story-bible-schema.md)

---

## Overview

This utility creates the complete file system structure for a new story project in the `.story-state/` directory. It handles directory name sanitization, creates all required subdirectories, and initializes starter files (metadata.json, quality-rubrics.md) with default values.

**Critical Security Requirement**: This utility MUST prevent directory traversal attacks by rejecting any paths containing `..` and returning the exact error message: `Invalid path: directory traversal not allowed`

---

## Initialization Workflow

### Step 1: Sanitize Story Title for Directory Name

**Input**: Raw story title from user or PLAN.md (e.g., `"The Cyberpunk Rebellion!"`, `"My Story: A Novel"`, `"../malicious-path"`)

**Output**: Sanitized directory name (e.g., `"The-Cyberpunk-Rebellion"`, `"My-Story-A-Novel"`)

**Algorithm**:

```
FUNCTION sanitize_story_title(raw_title: string) -> Result<string, error>

  // Step 1: Security check - directory traversal prevention
  IF raw_title contains ".." THEN
    RETURN Error("Invalid path: directory traversal not allowed")
  END IF

  // Step 2: Remove leading/trailing whitespace
  title = trim(raw_title)

  // Step 3: Remove special characters
  // Keep only: alphanumeric, spaces, hyphens, underscores
  // Remove: !@#$%^&*()[]{}+=|\\:;"'<>,?/
  title = replace_all(title, pattern="[^a-zA-Z0-9\s\-_]", replacement="")

  // Step 4: Replace spaces with hyphens
  title = replace_all(title, pattern="\s+", replacement="-")

  // Step 5: Remove consecutive hyphens
  title = replace_all(title, pattern="-+", replacement="-")

  // Step 6: Remove leading/trailing hyphens
  title = trim(title, chars="-")

  // Step 7: Enforce length limit (100 characters max)
  IF length(title) > 100 THEN
    title = substring(title, 0, 100)
    // Remove trailing partial word if cut mid-word
    last_hyphen_index = last_index_of(title, "-")
    IF last_hyphen_index > 80 THEN  // Only if reasonably close to end
      title = substring(title, 0, last_hyphen_index)
    END IF
  END IF

  // Step 8: Validate non-empty result
  IF length(title) == 0 THEN
    RETURN Error("Story title sanitization resulted in empty string")
  END IF

  RETURN Ok(title)
END FUNCTION
```

**Examples**:

| Input | Output | Notes |
|-------|--------|-------|
| `"The Cyberpunk Rebellion"` | `"The-Cyberpunk-Rebellion"` | Standard case |
| `"My Story: A Novel!"` | `"My-Story-A-Novel"` | Special chars removed |
| `"Multiple    Spaces"` | `"Multiple-Spaces"` | Multiple spaces → single hyphen |
| `"  Leading/Trailing  "` | `"LeadingTrailing"` | Trim + special char removal |
| `"../etc/passwd"` | ERROR | Security rejection |
| `"./../malicious"` | ERROR | Security rejection |
| `"A" * 150` | `"A" * 100` | Length capped at 100 |
| `""` | ERROR | Empty input |
| `"!!!"` | ERROR | No valid characters |

---

### Step 2: Create Directory Structure

**Input**: Sanitized story title, optional part structure flag

**Output**: Created directory tree

**Directory Creation Algorithm**:

```
FUNCTION create_story_bible_structure(sanitized_title: string, use_parts: bool = false) -> Result<path, error>

  // Step 1: Build base path
  base_path = ".story-state/" + sanitized_title

  // Step 2: Check if directory already exists
  IF directory_exists(base_path) THEN
    RETURN Error("Story directory already exists: " + base_path +
                 "\nUse resume command to continue existing story, or choose different title.")
  END IF

  // Step 3: Create base directory
  TRY
    create_directory(base_path)
  CATCH error
    RETURN Error("Failed to create base directory: " + error.message)
  END TRY

  // Step 4: Create required subdirectories
  required_subdirs = [
    "characters",
    "world-state",
    "plot-threads"
  ]

  FOR EACH subdir IN required_subdirs DO
    subdir_path = base_path + "/" + subdir
    TRY
      create_directory(subdir_path)
    CATCH error
      // Cleanup: remove partially created structure
      remove_directory_recursive(base_path)
      RETURN Error("Failed to create subdirectory " + subdir + ": " + error.message)
    END TRY
  END FOR

  // Step 5: Create chapters directory (with or without part structure)
  IF use_parts THEN
    // Part structure will be created later when part count known
    // For now, just create chapters/ base directory
    create_directory(base_path + "/chapters")
  ELSE
    create_directory(base_path + "/chapters")
  END IF

  RETURN Ok(base_path)
END FUNCTION
```

**Final Structure Created**:

```
.story-state/
└── [Sanitized-Story-Title]/
    ├── characters/           # Character profile files
    ├── world-state/          # World mechanics, locations, timeline
    ├── plot-threads/         # Plot thread tracking files
    └── chapters/             # Chapter prose files (flat or part-N/ subdirs)
```

**Note on Part Structure**: Part subdirectories (e.g., `chapters/part-1/`, `chapters/part-2/`) are created dynamically during chapter generation based on PLAN.md `part_structure` field, not during initialization. This allows the orchestrator to determine part boundaries from the approved plan.

---

### Step 3: Initialize metadata.json

**Purpose**: Create progress tracking file with initial values.

**Initial Values**:

```json
{
  "story_title": "[Sanitized Title]",
  "format": "not_specified",
  "total_chapters": 0,
  "completed_chapters": 0,
  "current_status": "in_progress",
  "last_session": "[ISO date of initialization - YYYY-MM-DD]",
  "created": "[ISO date of initialization - YYYY-MM-DD]",
  "continuity_checkpoints": [],
  "quality_issues_found": 0,
  "quality_issues_resolved": 0,
  "partial_chapters": [],
  "generation_notes": []
}
```

**Creation Algorithm**:

```
FUNCTION create_metadata_file(base_path: string, sanitized_title: string) -> Result<void, error>

  // Step 1: Get current ISO date
  current_date = format_iso_date(now())  // Format: "YYYY-MM-DD"

  // Step 2: Build metadata object
  metadata = {
    "story_title": sanitized_title,
    "format": "not_specified",  // Will be updated after plan approval
    "total_chapters": 0,         // Will be updated after plan approval
    "completed_chapters": 0,
    "current_status": "in_progress",
    "last_session": current_date,
    "created": current_date,
    "continuity_checkpoints": [],
    "quality_issues_found": 0,
    "quality_issues_resolved": 0,
    "partial_chapters": [],
    "generation_notes": []
  }

  // Step 3: Convert to JSON with pretty printing (2-space indent)
  json_string = to_json(metadata, indent=2)

  // Step 4: Write to file
  file_path = base_path + "/metadata.json"
  TRY
    write_file(file_path, json_string)
  CATCH error
    RETURN Error("Failed to create metadata.json: " + error.message)
  END TRY

  RETURN Ok()
END FUNCTION
```

**Post-Plan-Approval Update**:

After the user approves the plan, the orchestrator updates `metadata.json` with:
- `format`: From PLAN.md frontmatter `format` field
- `total_chapters`: From PLAN.md frontmatter `total_chapters` field

---

### Step 4: Initialize quality-rubrics.md

**Purpose**: Create validation checklist with default 6-category rubric template.

**Template Content**:

```markdown
# Quality Rubrics for [Story Title]

**Version**: 1.0.0
**Created**: [ISO Date]
**Last Updated**: [ISO Date]

---

## Instructions

This checklist is used by the quality-checker agent to validate each chapter. All criteria must pass for a chapter to be marked complete. Users may edit this file to add story-specific criteria or adjust standards.

---

## 1. World Consistency

**Category Purpose**: Ensure chapter respects established world rules and mechanics.

- [ ] No violations of established world mechanics (magic, technology, physics)
- [ ] Technology/magic use follows defined rules and limitations
- [ ] Geography and locations match previous descriptions
- [ ] Social structures and cultural norms remain consistent
- [ ] Historical references align with established timeline
- [ ] Weather/environmental details fit setting

**Severity**: High - violations break reader immersion

---

## 2. Character Voice

**Category Purpose**: Ensure characters speak and act consistently with their profiles.

- [ ] Speech patterns match character profile (formal/informal, vocabulary)
- [ ] Decisions align with established motivations and fears
- [ ] Character reactions fit personality and emotional state
- [ ] Physical mannerisms consistent with prior appearances
- [ ] Internal monologue (if POV) matches thought patterns
- [ ] Character knowledge/skills match backstory

**Severity**: High - out-of-character moments break believability

---

## 3. Prose Clarity

**Category Purpose**: Ensure chapter is readable and comprehensible.

- [ ] No unclear antecedents or ambiguous pronoun references
- [ ] Scene transitions are clear and logical
- [ ] Action sequences are followable step-by-step
- [ ] Time progression is explicit (hours, days, weeks)
- [ ] Spatial relationships are described clearly
- [ ] Sentence structure varies (not all short/all long)
- [ ] Paragraph breaks occur at natural thought/scene shifts

**Severity**: Medium - clarity issues slow reading but don't break story

---

## 4. Dialogue Authenticity

**Category Purpose**: Ensure dialogue serves story and sounds natural.

- [ ] Characters sound distinct from each other
- [ ] Dialogue serves plot advancement or character development
- [ ] Subtext present in important conversations
- [ ] Balance of dialogue tags and action beats
- [ ] No "as you know, Bob" exposition dumps
- [ ] Dialogue rhythm matches scene tension
- [ ] Characters interrupt, overlap, or pause naturally

**Severity**: Medium - weak dialogue is noticeable but not fatal

---

## 5. Plot Logic

**Category Purpose**: Ensure events follow causally from previous chapters.

- [ ] Events follow causally from previous chapters
- [ ] No unresolved contradictions from prior plot beats
- [ ] Character actions have logical motivations
- [ ] Stakes escalate appropriately
- [ ] Consequences of prior events acknowledged
- [ ] Pacing matches story format (not rushed/not dragging)
- [ ] Chapter advances at least one plot thread

**Severity**: High - plot holes undermine narrative coherence

---

## 6. Thematic Alignment

**Category Purpose**: Ensure chapter serves story's central themes and motifs.

- [ ] Chapter serves story's central themes
- [ ] Motifs are reinforced (not over-explained)
- [ ] Tone matches established atmosphere
- [ ] Emotional beats land with appropriate weight
- [ ] Symbolism (if any) is subtle and earned
- [ ] Chapter contributes to overall narrative arc

**Severity**: Low to Medium - thematic drift is gradual, fixable in revision

---

## Custom Criteria

[Users may add story-specific criteria here]

---

## Notes

**Validation Process**: Quality-checker agent reads this file before validating each chapter. Failures are reported with specific line references. Chapters with failures are regenerated with constraint instructions addressing flagged issues.

**Customization**: Users may edit criteria to match story needs (e.g., horror stories might add "sustains dread atmosphere" to thematic alignment, romance stories might add "relationship dynamic progresses" to plot logic).
```

**Creation Algorithm**:

```
FUNCTION create_quality_rubrics(base_path: string, story_title: string) -> Result<void, error>

  // Step 1: Get current ISO date
  current_date = format_iso_date(now())  // Format: "YYYY-MM-DD"

  // Step 2: Load template content (shown above)
  template = load_quality_rubrics_template()

  // Step 3: Replace placeholders
  content = replace(template, "[Story Title]", story_title)
  content = replace(content, "[ISO Date]", current_date)

  // Step 4: Write to file
  file_path = base_path + "/quality-rubrics.md"
  TRY
    write_file(file_path, content)
  CATCH error
    RETURN Error("Failed to create quality-rubrics.md: " + error.message)
  END TRY

  RETURN Ok()
END FUNCTION
```

---

## Complete Initialization Function

**Main Entry Point**: This is the function the orchestrator calls to initialize a new story.

```
FUNCTION initialize_story_bible(raw_title: string, use_parts: bool = false) -> Result<string, error>

  // Step 1: Sanitize title
  sanitized_title = sanitize_story_title(raw_title)?
  // Note: ? operator propagates Error if sanitization fails

  // Step 2: Create directory structure
  base_path = create_story_bible_structure(sanitized_title, use_parts)?

  // Step 3: Create metadata.json
  create_metadata_file(base_path, sanitized_title)?

  // Step 4: Create quality-rubrics.md
  create_quality_rubrics(base_path, sanitized_title)?

  // Step 5: Return success with base path
  RETURN Ok(base_path)
END FUNCTION
```

**Usage Example** (in orchestrator):

```
// User invokes: /write-story A 30-chapter novel about cyberpunk rebellion

raw_title = extract_title_from_input("A 30-chapter novel about cyberpunk rebellion")
// raw_title = "Cyberpunk Rebellion"

result = initialize_story_bible(raw_title, use_parts=false)

MATCH result WITH
  | Ok(base_path) ->
      print("Story bible initialized at: " + base_path)
      proceed_to_plan_generation(base_path)

  | Error(message) ->
      print("ERROR: " + message)
      abort_generation()
END MATCH
```

---

## Error Handling Specifications

### Error Case 1: Directory Traversal Attack

**Trigger**: User provides title containing `..`

**Example Input**: `"../etc/passwd"`, `"./../malicious"`, `"story/../attack"`

**Expected Behavior**:
```
RETURN Error("Invalid path: directory traversal not allowed")
```

**Orchestrator Response**: Display error message to user, abort initialization, do not create any files or directories.

---

### Error Case 2: Directory Already Exists

**Trigger**: `.story-state/[Sanitized-Title]/` directory already exists on filesystem

**Example**: User runs `/write-story Cyberpunk Rebellion` twice

**Expected Behavior**:
```
RETURN Error("Story directory already exists: .story-state/Cyberpunk-Rebellion\nUse resume command to continue existing story, or choose different title.")
```

**Orchestrator Response**: Display error message, suggest resume command: `/write-story continue .story-state/Cyberpunk-Rebellion/PLAN.md`

---

### Error Case 3: Empty Title After Sanitization

**Trigger**: User provides title with only special characters

**Example Input**: `"!!!"`, `"@#$%"`, `"   "`

**Expected Behavior**:
```
RETURN Error("Story title sanitization resulted in empty string")
```

**Orchestrator Response**: Display error message, ask user to provide valid story title.

---

### Error Case 4: File System Write Failure

**Trigger**: Filesystem error during directory creation or file writing (disk full, permissions, etc.)

**Example**: Permission denied when creating `.story-state/Story/` directory

**Expected Behavior**:
```
// During directory creation:
RETURN Error("Failed to create base directory: [filesystem error message]")

// During file writing:
RETURN Error("Failed to create metadata.json: [filesystem error message]")
```

**Cleanup**: If error occurs after partial directory structure created, remove entire `.story-state/[Sanitized-Title]/` directory to prevent corrupted state.

**Orchestrator Response**: Display error message with full filesystem error details, suggest checking disk space and permissions, abort initialization.

---

### Error Case 5: Partial Creation Cleanup

**Trigger**: Error occurs after some subdirectories created but before initialization completes

**Example**: Successfully created `.story-state/Story/` and `characters/` subdirectory, but error when creating `world-state/`

**Expected Behavior**:
1. Catch error during subdirectory creation
2. Remove entire `.story-state/[Sanitized-Title]/` directory (cleanup)
3. Return error message

**Cleanup Algorithm**:
```
TRY
  create_directory(subdir_path)
CATCH error
  // Cleanup: remove partially created structure
  remove_directory_recursive(base_path)
  RETURN Error("Failed to create subdirectory " + subdir + ": " + error.message)
END TRY
```

**Rationale**: Prevent corrupted partial directory structures that could cause issues on resume attempts.

---

## Validation Checklist

After initialization completes successfully, the following structure and files MUST exist:

**Directory Structure**:
- [ ] `.story-state/[Sanitized-Title]/` exists
- [ ] `.story-state/[Sanitized-Title]/characters/` exists
- [ ] `.story-state/[Sanitized-Title]/world-state/` exists
- [ ] `.story-state/[Sanitized-Title]/plot-threads/` exists
- [ ] `.story-state/[Sanitized-Title]/chapters/` exists

**Files**:
- [ ] `.story-state/[Sanitized-Title]/metadata.json` exists
- [ ] `metadata.json` contains valid JSON with all required fields
- [ ] `metadata.json` has `current_status` set to `"in_progress"`
- [ ] `metadata.json` has `completed_chapters` set to `0`
- [ ] `.story-state/[Sanitized-Title]/quality-rubrics.md` exists
- [ ] `quality-rubrics.md` contains all 6 rubric categories
- [ ] `quality-rubrics.md` frontmatter has `version`, `created`, `last_updated` fields

**Security**:
- [ ] Directory name does not contain `..`
- [ ] Directory name does not contain special characters: `!@#$%^&*()[]{}+=|\\:;"'<>,?/`
- [ ] Directory name length does not exceed 100 characters

---

## Integration with Orchestrator Workflow

**When to Call**: Orchestrator calls `initialize_story_bible()` after:
1. Parsing user input (`/write-story [input]`)
2. Extracting story title (from natural language or file reference)
3. Detecting this is a new story (not a resume operation)

**What Happens Next**: After successful initialization:
1. Orchestrator spawns `concept-developer` agent to generate PLAN.md
2. Concept-developer writes PLAN.md to `.story-state/[Title]/PLAN.md`
3. Orchestrator presents plan to user for approval
4. After approval, orchestrator updates `metadata.json` with `format` and `total_chapters` from PLAN.md
5. Orchestrator proceeds to character building and chapter generation

**Resume Operations**: If `.story-state/[Sanitized-Title]/` already exists, orchestrator:
1. Does NOT call `initialize_story_bible()` (would error)
2. Instead, calls resume logic: read `metadata.json`, read `PLAN.md`, identify last completed chapter
3. Continues generation from next chapter

---

## Examples

### Example 1: Standard Initialization

**Input**:
```
raw_title = "The Cyberpunk Rebellion"
use_parts = false
```

**Process**:
1. Sanitize: `"The-Cyberpunk-Rebellion"`
2. Create: `.story-state/The-Cyberpunk-Rebellion/`
3. Create subdirs: `characters/`, `world-state/`, `plot-threads/`, `chapters/`
4. Write `metadata.json` with initial values
5. Write `quality-rubrics.md` with default template

**Output**:
```
Ok(".story-state/The-Cyberpunk-Rebellion")
```

**Final Structure**:
```
.story-state/
└── The-Cyberpunk-Rebellion/
    ├── metadata.json
    ├── quality-rubrics.md
    ├── characters/
    ├── world-state/
    ├── plot-threads/
    └── chapters/
```

---

### Example 2: Title with Special Characters

**Input**:
```
raw_title = "My Story: A Novel of Love & Loss!"
use_parts = false
```

**Process**:
1. Sanitize:
   - Remove `:`, `!`, `&`
   - Replace spaces with hyphens
   - Result: `"My-Story-A-Novel-of-Love-Loss"`
2. Create directory structure
3. Write files

**Output**:
```
Ok(".story-state/My-Story-A-Novel-of-Love-Loss")
```

---

### Example 3: Security Rejection

**Input**:
```
raw_title = "../etc/passwd"
use_parts = false
```

**Process**:
1. Sanitize: Detects `..` in input
2. Return error immediately

**Output**:
```
Error("Invalid path: directory traversal not allowed")
```

**No files or directories created**.

---

### Example 4: Directory Already Exists

**Input**:
```
raw_title = "The Cyberpunk Rebellion"
use_parts = false

// Assume .story-state/The-Cyberpunk-Rebellion/ already exists from previous session
```

**Process**:
1. Sanitize: `"The-Cyberpunk-Rebellion"`
2. Check existence: Directory exists
3. Return error

**Output**:
```
Error("Story directory already exists: .story-state/The-Cyberpunk-Rebellion\nUse resume command to continue existing story, or choose different title.")
```

**Orchestrator suggests**: `/write-story continue .story-state/The-Cyberpunk-Rebellion/PLAN.md`

---

### Example 5: Very Long Title

**Input**:
```
raw_title = "The Incredibly Long and Elaborate Title That Goes On and On About a Cyberpunk Rebellion in a Dystopian Future Where Technology Has Advanced Beyond Recognition"
use_parts = false
```

**Process**:
1. Sanitize:
   - Remove special chars: All clean
   - Replace spaces with hyphens
   - Length: 164 characters
   - Truncate to 100 characters: `"The-Incredibly-Long-and-Elaborate-Title-That-Goes-On-and-On-About-a-Cyberpunk-Rebellion-in-a-D"`
   - Find last hyphen after position 80: position 99
   - Truncate at last hyphen: `"The-Incredibly-Long-and-Elaborate-Title-That-Goes-On-and-On-About-a-Cyberpunk-Rebellion-in-a"`
2. Create directory structure

**Output**:
```
Ok(".story-state/The-Incredibly-Long-and-Elaborate-Title-That-Goes-On-and-On-About-a-Cyberpunk-Rebellion-in-a")
```

---

## Testing Requirements

**Unit Tests** (from TASK-002 acceptance criteria):

1. **Test: Function creates all required subdirectories**
   - Input: Valid story title
   - Assert: `characters/`, `world-state/`, `plot-threads/`, `chapters/` all exist after initialization

2. **Test: Sanitizes story title for directory names (removes special chars, limits length)**
   - Input: `"My Story: A Novel!"`
   - Assert: Directory name is `"My-Story-A-Novel"`
   - Input: `"A" * 150`
   - Assert: Directory name is 100 characters or less

3. **Test: Creates metadata.json with initial values**
   - Input: Valid story title
   - Assert: `metadata.json` exists
   - Assert: `status` field is `"in_progress"`
   - Assert: `completed_chapters` field is `0`

4. **Test: Creates quality-rubrics.md with default 6-category rubric template**
   - Input: Valid story title
   - Assert: `quality-rubrics.md` exists
   - Assert: File contains 6 rubric sections (World Consistency, Character Voice, Prose Clarity, Dialogue Authenticity, Plot Logic, Thematic Alignment)

5. **Test: Prevents directory traversal attacks**
   - Input: `"../etc/passwd"`
   - Assert: Error returned with exact message: `"Invalid path: directory traversal not allowed"`
   - Assert: No files or directories created
   - Input: `"./../malicious"`
   - Assert: Same error message
   - Input: `"story/../attack"`
   - Assert: Same error message

6. **Test: Returns error if directory already exists (prevents accidental overwrite)**
   - Setup: Create `.story-state/Test-Story/` directory
   - Input: `"Test Story"`
   - Assert: Error returned mentioning directory already exists
   - Assert: Existing directory not modified

**Integration Tests**:

1. **Test: End-to-end initialization with valid title**
   - Call `initialize_story_bible("Cyberpunk Rebellion")`
   - Assert: All subdirectories exist
   - Assert: `metadata.json` has correct initial values
   - Assert: `quality-rubrics.md` has all 6 categories

2. **Test: Cleanup on partial failure**
   - Simulate filesystem error during subdirectory creation
   - Assert: Entire `.story-state/[Title]/` directory is removed (no partial structure left)

---

## Notes for Orchestrator Implementation

**Language-Agnostic Design**: This document describes algorithms in pseudocode. The orchestrator (implemented in markdown as a Claude Code command) will use natural language instructions to Claude to achieve the same results via Write, Read, and Bash tools.

**Recommended Orchestrator Approach**:
1. Use Write tool to create directories and files
2. Use Read tool to verify creation succeeded
3. Handle errors by checking Write tool responses
4. Use Bash tool for directory operations if needed (mkdir, rm -rf for cleanup)

**Example Orchestrator Implementation Pattern** (in `/write-story` command):

```markdown
## Story Bible Initialization

When creating a new story, follow these steps to initialize the story bible:

1. **Sanitize the story title**:
   - Remove special characters: `!@#$%^&*()[]{}+=|\\:;"'<>,?/`
   - Replace spaces with hyphens
   - Limit to 100 characters
   - **CRITICAL**: If title contains `..`, reject with error: "Invalid path: directory traversal not allowed"

2. **Check for existing directory**:
   - If `.story-state/[Sanitized-Title]/` exists, return error suggesting resume command
   - Do NOT overwrite existing stories

3. **Create directory structure** using Write tool:
   - Create `.story-state/[Sanitized-Title]/`
   - Create subdirectories: `characters/`, `world-state/`, `plot-threads/`, `chapters/`

4. **Initialize metadata.json**:
   - Write JSON file with fields: story_title, format="not_specified", total_chapters=0, completed_chapters=0, current_status="in_progress", last_session=[current date], created=[current date], continuity_checkpoints=[], quality_issues_found=0, quality_issues_resolved=0, partial_chapters=[], generation_notes=[]

5. **Initialize quality-rubrics.md**:
   - Write markdown file with 6 rubric categories (see template in story-bible-init.md)

6. **Handle errors**:
   - If any step fails, remove entire `.story-state/[Sanitized-Title]/` directory
   - Report specific error to user
```

**Reference**: The orchestrator can load this file (`story-bible-init.md`) during execution to reference the exact algorithms, templates, and error messages.

---

## Version History

**1.0.0** (2025-11-16):
- Initial utility documentation for TASK-002
- Sanitization algorithm with directory traversal protection
- Initial metadata.json structure with 10 required fields
- Quality rubrics template with 6 categories
- Error handling specifications for 5 error cases
- Complete initialization workflow with examples

---

**End of Story Bible Initialization Utility Documentation**
