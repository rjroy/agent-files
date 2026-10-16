---
name: story-review-story
description: Run an informational, read-only continuity review of a completed or in-progress story bible.
---

**Conversational use:** Accept the user request and any available context directly; do not require slash-command syntax or a positional `$ARGUMENTS` string. Clarify only missing required choices. Use OpenCode-supported file and subagent capabilities.

# story-review-story Skill

**Purpose**: Run on-demand continuity validation for an existing story without affecting generation state.

**When to Use**:
- After completing chapters, verify narrative consistency before continuing
- Investigate suspected continuity issues between chapters
- Validate story quality before marking as complete
- Review long-running stories for drift detection

**Key Difference from Automatic Checkpoints**:
- **Automatic checkpoints** (Step 7.4 in `story-write-story`): Run during generation, block on errors
- **Review-story workflow**: Run on demand, informational only, never blocks

---

## Skill Inputs

Ask for a continuity review and provide the story directory, for example: "Review `.story-state/Cyberpunk-Rebellion/` for continuity issues."

**Parameters**:
- `story-directory-path`: Absolute or relative path to `.story-state/[Story]/` directory

**Examples**:
Examples: "Review `.story-state/Cyberpunk-Rebellion/`." or "Check `/home/user/projects/.story-state/Epic-Fantasy/` for continuity issues."

---

## Workflow

When the user asks for this workflow, apply these steps. Start from details already provided; ask only for missing information that changes the next decision.

### Step 1: Parse and Validate Parameters

**1.1 Extract Story Directory Path**
- Parse the story directory path from the user request
- Normalize path (resolve relative paths to absolute)
- Trim whitespace and trailing slashes

**1.2 Security Validation**
- Reject paths containing `../` (directory traversal attempts)
- Reject paths containing null bytes or other suspicious characters
- If invalid, report error and show correct syntax

**1.3 Verify Directory Exists**
- Check if the specified directory exists
- If not found, provide clear error message with the attempted path
- Suggest checking the path or listing available stories

**1.4 Validate Story Bible Structure**
- Verify required files exist:
  - `metadata.json` (story metadata and progress tracking)
  - `PLAN.md` (narrative structure and plot outline)
  - `chapters/` directory (contains completed chapters)
- If any required file is missing, report incomplete story bible and exit

**Example Error Messages**:
```
ERROR: Directory not found: .story-state/Missing-Story/
Please verify the path and try again.

ERROR: Invalid story bible - missing metadata.json
The story bible appears incomplete. Required files: metadata.json, PLAN.md, chapters/
```

---

### Step 2: Load Story Context

**2.1 Read Story Metadata**
- Load `metadata.json` to extract:
  - `title`: Story title
  - `total_chapters`: Planned chapter count
  - `completed_chapters`: Number of chapters written so far
  - `genre`: Genre classification
  - `themes`: Thematic elements

**2.2 Read Narrative Plan**
- Load `PLAN.md` to understand:
  - Story arc structure
  - Plot threads and their intended progression
  - Character arcs
  - World-building elements

**2.3 Count Completed Chapters**
- Scan `chapters/` directory for chapter files
- Expected format: `chapter-NNN.md` where NNN is zero-padded chapter number
- Count total chapter files found
- Verify count matches `completed_chapters` in metadata (warn if mismatch)

**2.4 Validate Chapter Range**
- If no chapters exist, report "No chapters to validate" and exit gracefully
- Determine validation range: chapter 1 through highest completed chapter
- Report to user: "Validating [X] chapters from [Story Title]"

**Example Output**:
```
Loading story: "The Cyberpunk Rebellion"
- Genre: Cyberpunk Thriller
- Total chapters planned: 15
- Completed chapters: 8
- Validating chapters 1-8 for continuity...
```

---

### Step 3: Invoke the Shared Story Reviewer

Invoke a fresh `story-engine-wyrd-story-reviewer` subagent with `mode: continuity`, the validated story directory, an explicit range from chapter 1 through `completed_chapters`, and relevant plan context. This on-demand range is authoritative even when it overlaps prior checkpoints. The reviewer loads only the continuity procedure at `references/continuity-review.md` relative to this skill directory. Do not delegate through another wrapper or reuse a prior reviewer invocation.

The reviewer is read-only and returns evidence-based findings, with chapter references and severity where supported. It does not change source files or metadata. This on-demand skill remains informational and never blocks story generation; parent-workflow checkpoint gates are owned by `story-write-story`.

---

### Step 4: Present Validation Report

**4.1 Display Reviewer Findings**
- Show the complete validation report from the story-engine-wyrd-story-reviewer
- Preserve all chapter:line references for easy navigation
- Maintain category groupings (Character, World, Timeline, Plot Threads)

**4.2 Summarize Issue Count**
- Count total issues found across all categories
- Count issues by category if agent provides breakdown
- Count issues by severity if agent provides classification
- Present summary statistics at the top of the report

**4.3 Highlight Critical Issues**
- If the agent identifies critical contradictions, highlight them prominently
- Critical issues might include:
  - Character deaths contradicted by later appearances
  - Major world-building rule violations
  - Timeline impossibilities (character in two places at once)
  - Plot threads that contradict established facts

**4.4 Format for Readability**
- Use clear section headers for each category
- Use bullet points or numbered lists for findings
- Include chapter:line references for every issue
- Provide brief excerpts showing the contradiction

**Example Report Format**:
```
CONTINUITY VALIDATION REPORT
Story: "The Cyberpunk Rebellion"
Chapters Validated: 1-8
Validation Date: 2025-11-16

SUMMARY:
- Total Issues Found: 5
- Critical: 1
- Major: 2
- Minor: 2

CATEGORY BREAKDOWN:
- Character Issues: 2
- World Issues: 1
- Timeline Issues: 1
- Plot Thread Issues: 1

---

DETAILED FINDINGS:

CHARACTER ISSUES (2 found)

1. [MAJOR] Character Knowledge Contradiction
   - Chapter 3, Line 45: "Maya had never seen neural implants before"
   - Chapter 6, Line 123: "Maya recalled her first neural implant surgery at age 12"
   - Issue: Maya's prior knowledge of neural implants is contradicted

2. [MINOR] Character Trait Inconsistency
   - Chapter 2, Line 67: "Alex despised coffee, always ordering tea"
   - Chapter 7, Line 89: "Alex sipped his morning coffee gratefully"
   - Issue: Beverage preference changed without explanation

WORLD ISSUES (1 found)

3. [CRITICAL] World Rule Violation
   - Chapter 4, Line 201: "The neural network required physical contact to hack"
   - Chapter 8, Line 34: "She hacked the network remotely from across the city"
   - Issue: Established world rule about hacking requirements violated

... [additional findings] ...
```

---

### Step 5: Informational Summary and Next Steps

**5.1 Emphasize Report Nature**
- Clearly state this report is **informational only**
- Emphasize validation does **NOT block story generation**
- User can continue writing immediately if desired
- Manual review and correction is optional (but recommended for quality)

**5.2 Provide Next Steps Based on Findings**

**If Issues Found:**
- Review specific chapters mentioned in the report
- Decide which issues to address based on severity
- Options for correction:
  - **Manual edit**: Use OpenCode's available file-editing capability to fix specific lines
  - **Regenerate chapter**: Use `story-write-story` continue` with context about needed fixes
  - **Accept inconsistency**: Some minor issues may be acceptable creative choices
- Consider requesting `story-review-story` again after corrections to verify fixes

**If No Issues Found:**
- Confirm narrative consistency across all validated chapters
- Congratulate user on maintaining continuity
- Story is ready to continue or mark as complete
- No action required

**5.3 Additional Recommendations**

For long-running stories (10+ chapters):
- Request `story-review-story` periodically (every 5-10 chapters)
- Pay special attention to character knowledge and timeline
- Consider maintaining a separate continuity notes file

For complex stories (multiple POVs, timelines, locations):
- Review world-building consistency carefully
- Validate timeline ordering with special attention
- Check plot thread tracking for all active threads

**Example Summary (Issues Found)**:
```
---

NEXT STEPS:

This validation report is INFORMATIONAL ONLY and does not block story generation.
You can continue writing immediately if desired.

Based on the findings above, consider these options:

1. REVIEW CRITICAL ISSUES FIRST
   - Address the world rule violation in chapters 4 and 8
   - This may require re-establishing the hacking mechanics clearly

2. MANUAL CORRECTIONS
   - Use OpenCode's available file-editing capability to fix specific contradictions
   - Update chapter-003.md line 45 or chapter-006.md line 123 for Maya's knowledge
   - Update chapter-002.md line 67 or chapter-007.md line 89 for Alex's beverage preference

3. REGENERATE CHAPTERS
   - Use `story-write-story` continue to regenerate problematic chapters
   - Provide context about continuity issues to fix during regeneration

4. VERIFY FIXES
   - After making corrections, run `story-review-story` again to confirm issues resolved

5. ACCEPT MINOR INCONSISTENCIES
   - Some minor issues may be acceptable creative evolution
   - Focus on critical and major issues that impact story coherence
```

**Example Summary (No Issues)**:
```
---

VALIDATION COMPLETE

No continuity issues detected across 8 chapters!

Your story maintains strong narrative consistency:
- Character traits, voice, and knowledge are stable
- World-building rules are consistently applied
- Timeline progression is logical and coherent
- Plot threads are properly tracked and developed

Your story is ready to:
- Continue writing additional chapters
- Mark as complete if target length reached
- Share with readers confident in narrative quality

Great work maintaining continuity!
```

---

## Error Handling

Handle the following error scenarios gracefully:

### Invalid Path Format
```
ERROR: Invalid story directory path
Ask for a continuity review and include the story directory, for example `.story-state/My-Story/`.
```

### Directory Not Found
```
ERROR: Story directory not found
Path: .story-state/Missing-Story/

Please verify:
1. The directory path is correct
2. The story bible exists at this location
3. You have read permissions for this directory

To list available stories, check the .story-state/ directory.
```

### Missing Story Bible Files
```
ERROR: Incomplete story bible detected
Directory: .story-state/Broken-Story/

Missing required files:
- metadata.json (MISSING)
- PLAN.md (FOUND)
- chapters/ (FOUND)

The story bible appears corrupted or incomplete.
Cannot proceed with validation.
```

### No Chapters to Validate
```
VALIDATION SKIPPED

Story: "Untitled Story"
Completed chapters: 0

No chapters have been written yet. Validation requires at least one completed chapter.

Use `story-write-story` to begin writing chapters, then run `story-review-story` again.
```

### Agent Spawn Failure
```
ERROR: Failed to spawn story-engine-wyrd-story-reviewer

This may be due to:
- System resource constraints
- Agent configuration issues
- Temporary service interruption

Please try again. If the error persists, report this issue.
```

### Metadata/Chapter Mismatch
```
WARNING: Chapter count mismatch detected

metadata.json reports: 8 completed chapters
chapters/ directory contains: 7 chapter files

This may indicate:
- A chapter file was deleted manually
- The metadata is out of sync

Proceeding with validation of 7 chapters found in chapters/ directory.
Consider investigating the missing chapter file.
```

---

## Example Scenarios

### Scenario 1: Clean Validation (No Issues)

**Command**:
```
`story-review-story` .story-state/The-Lighthouse-Mystery/
```

**Output**:
```
Loading story: "The Lighthouse Mystery"
- Genre: Supernatural Mystery
- Total chapters planned: 12
- Completed chapters: 6
- Validating chapters 1-6 for continuity...

[Invoking story-engine-wyrd-story-reviewer in continuity mode...]

CONTINUITY VALIDATION REPORT
Story: "The Lighthouse Mystery"
Chapters Validated: 1-6
Validation Date: 2025-11-16

SUMMARY:
- Total Issues Found: 0
- Critical: 0
- Major: 0
- Minor: 0

DETAILED FINDINGS:

CHARACTER ISSUES: None found
All character traits, dialogue voice, and knowledge remain consistent.

WORLD ISSUES: None found
All supernatural mechanics and location descriptions are consistent.

TIMELINE ISSUES: None found
Event chronology and flashback sequences are properly ordered.

PLOT THREAD ISSUES: None found
All active threads are tracked and developing appropriately.

---

VALIDATION COMPLETE

No continuity issues detected across 6 chapters!

Your story maintains strong narrative consistency:
- Character traits, voice, and knowledge are stable
- World-building rules are consistently applied
- Timeline progression is logical and coherent
- Plot threads are properly tracked and developed

Your story is ready to:
- Continue writing additional chapters
- Mark as complete if target length reached
- Share with readers confident in narrative quality

Great work maintaining continuity!
```

---

### Scenario 2: Issues Found (Contradictions Detected)

**Command**:
```
`story-review-story` .story-state/Cyberpunk-Rebellion/
```

**Output**:
```
Loading story: "The Cyberpunk Rebellion"
- Genre: Cyberpunk Thriller
- Total chapters planned: 15
- Completed chapters: 10
- Validating chapters 1-10 for continuity...

[Invoking story-engine-wyrd-story-reviewer in continuity mode...]

CONTINUITY VALIDATION REPORT
Story: "The Cyberpunk Rebellion"
Chapters Validated: 1-10
Validation Date: 2025-11-16

SUMMARY:
- Total Issues Found: 7
- Critical: 1
- Major: 3
- Minor: 3

CATEGORY BREAKDOWN:
- Character Issues: 3
- World Issues: 2
- Timeline Issues: 1
- Plot Thread Issues: 1

---

DETAILED FINDINGS:

CHARACTER ISSUES (3 found)

1. [MAJOR] Character Knowledge Contradiction
   - Chapter 3, Line 45: "Maya had never seen neural implants before"
   - Chapter 6, Line 123: "Maya recalled her first neural implant surgery at age 12"
   - Issue: Maya's prior knowledge of neural implants contradicted

2. [MINOR] Character Voice Inconsistency
   - Chapter 2, Line 89: "Alex spoke in clipped, military-style sentences"
   - Chapter 8, Line 156: "Alex rambled philosophically for several minutes"
   - Issue: Character speech patterns changed without explanation

3. [MINOR] Character Relationship Contradiction
   - Chapter 4, Line 201: "Sarah and Tom met for the first time"
   - Chapter 9, Line 78: "Sarah remembered working with Tom five years ago"
   - Issue: Prior relationship contradicts first meeting

WORLD ISSUES (2 found)

4. [CRITICAL] World Rule Violation
   - Chapter 4, Line 203: "Neural hacking required physical contact with the target"
   - Chapter 10, Line 34: "She hacked his neural implant remotely from across the city"
   - Issue: Established world rule about hacking mechanics violated

5. [MAJOR] Location Contradiction
   - Chapter 5, Line 112: "The SafeZone was located in the northern sector"
   - Chapter 9, Line 245: "They traveled south to reach the SafeZone"
   - Issue: Location geography is inconsistent

TIMELINE ISSUES (1 found)

6. [MAJOR] Event Chronology Error
   - Chapter 7, Line 89: "Three weeks after the raid on DataCorp..."
   - Chapter 8, Line 23: "The DataCorp raid happened yesterday"
   - Issue: Timeline of events contradicts established chronology

PLOT THREAD ISSUES (1 found)

7. [MINOR] Dropped Thread Detection
   - Chapter 3, Line 167: "They needed to find the encryption key within 48 hours"
   - Chapters 4-10: No mention of encryption key search or deadline
   - Issue: Active plot thread appears to have been dropped without resolution

---

NEXT STEPS:

This validation report is INFORMATIONAL ONLY and does not block story generation.
You can continue writing immediately if desired.

Based on the findings above, consider these options:

1. REVIEW CRITICAL ISSUES FIRST
   - Address the world rule violation (Issue #4) in chapters 4 and 10
   - This may require establishing clear rules about neural hacking range/requirements

2. MANUAL CORRECTIONS
   - Fix character knowledge contradiction (Issue #1): Update chapter 3 or chapter 6
   - Fix location geography (Issue #5): Establish consistent SafeZone location
   - Fix timeline error (Issue #6): Reconcile event chronology in chapters 7-8

3. PLOT THREAD RECOVERY
   - Address dropped encryption key thread (Issue #7)
   - Either resolve in upcoming chapters or retcon earlier mention

4. REGENERATE CHAPTERS
   - Use `story-write-story` continue to regenerate problematic chapters
   - Provide context about continuity issues to fix during regeneration

5. VERIFY FIXES
   - After making corrections, run `story-review-story` again to confirm issues resolved

6. PRIORITIZATION GUIDANCE
   - Critical issues (1): Fix before continuing story
   - Major issues (3): Should fix for narrative coherence
   - Minor issues (3): Optional, may be acceptable creative evolution
```

---

### Scenario 3: Error - Directory Not Found

**Command**:
```
`story-review-story` .story-state/Nonexistent-Story/
```

**Output**:
```
ERROR: Story directory not found
Path: .story-state/Nonexistent-Story/

Please verify:
1. The directory path is correct
2. The story bible exists at this location
3. You have read permissions for this directory

To list available stories, check the .story-state/ directory.

Example usage:
`story-review-story` .story-state/My-Story/
```

---

### Scenario 4: Error - No Chapters Written Yet

**Command**:
```
`story-review-story` .story-state/New-Story-Outline/
```

**Output**:
```
Loading story: "New Story Outline"
- Genre: Science Fiction
- Total chapters planned: 20
- Completed chapters: 0

VALIDATION SKIPPED

No chapters have been written yet. Validation requires at least one completed chapter.

Use `story-write-story` to begin writing chapters, then run `story-review-story` again.
```

---

## Summary

The `story-review-story` skill provides on-demand continuity validation with these key features:

**Core Functionality**:
- Validates all completed chapters in a story bible
- Invokes story-engine-wyrd-story-reviewer in continuity mode for systematic analysis
- Reports contradictions across 4 categories (Character, World, Timeline, Plot)
- Informational only - never blocks story generation

**User Experience**:
- Simple conversational request naming the story directory to review
- Clear error messages for common issues
- Detailed validation reports with chapter:line references
- Actionable next steps based on findings
- No modification to story bible files (read-only operation)

**Quality Assurance Value**:
- Catch continuity drift in long-running stories
- Validate before marking story as complete
- Investigate suspected narrative inconsistencies
- Complement automatic checkpoints during generation

This workflow empowers users to maintain narrative quality through manual validation at any point in the writing process.
