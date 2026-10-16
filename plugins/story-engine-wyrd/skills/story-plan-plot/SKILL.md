---
name: story-plan-plot
description: Collaboratively develop and refine a structured plot outline grounded in narrative craft.
---

**Conversational use:** Accept the user request and any available context directly; do not require slash-command syntax or a positional `$ARGUMENTS` string. Clarify only missing required choices. Use OpenCode-supported file and subagent capabilities.

# story-plan-plot Skill

## Skill Activation

Use this skill when the user wants to plan, diagnose, or revise story structure.

---

## Purpose

This workflow helps users plan story structure and plot using narrative theory. It can be used:
- Standalone (planning story before writing)
- As preparation for write-story workflow
- For outlining complex narratives
- For troubleshooting plot problems in existing stories

---

## System Activation

**STEP 1: Load the story-engine-reference skill**

Consult the sibling `story-engine-reference` skill and load only relevant reference files:

```
`../story-engine-reference/SKILL.md`
```

**STEP 2: Load narrative structure theory**

Read this resource relative to the current `story-plan-plot` skill directory:
- `../story-engine-reference/story/theory/theory-narrative-structure.md`

**Optional (based on user needs):**
- World file if user mentions specific world
- Lens file if user mentions specific genre
- Format file if user mentions specific format

---

## User Interaction

**STEP 1: Understand User's Need**

Ask clarifying questions:

1. **What are you planning?**
   - New story from scratch?
   - Existing story that needs structure?
   - Specific problem to solve?

2. **Format (if known):**
   - "What story format? (Flash, Short Story, Epic, Serialized, or not sure yet?)"
   - Load appropriate format file if specified

3. **World/Genre (if known):**
   - "Which world?" (Telvaren or other)
   - "Any genre lens?" (Mystery, Romance, Horror, Coming-of-Age)
   - Load appropriate files if specified

4. **Starting Point:**
   - "Do you have any initial ideas (characters, conflicts, themes)?"
   - "Or should we start from scratch?"

---

## Plot Planning Process

**STEP 2: Guided Plot Development**

Using loaded theory, help user develop plot through structured approach:

### Core Concept

**Establish foundation:**

**Protagonist:**
- Who is the main character?
- What do they want? (external desire)
- What do they need? (internal growth)

**Central Conflict:**
- What prevents protagonist from getting what they want?
- External obstacle (person, society, world, nature)
- Internal obstacle (fear, flaw, belief)

**Stakes:**
- What happens if protagonist fails?
- Why does this matter?
- What makes this personal?

**Thematic Question:**
- What question does this story explore?
- What truth or idea is at the heart of this?

### Structural Framework

**Help user choose structure based on story needs:**

**Three-Act Structure (Most Common):**

**Act 1 (Setup)** - 20-25%
- Establish protagonist, world, status quo
- Inciting incident disrupts normalcy
- Protagonist commits to goal/journey
- Stakes clear

**Act 2 (Confrontation)** - 50-60%
- Protagonist pursues goal, faces obstacles
- Complications escalate
- **Midpoint (50%):** Major revelation or reversal
- Dark moment: All seems lost

**Act 3 (Resolution)** - 15-25%
- Climax: Final confrontation
- Resolution: Consequences play out
- New equilibrium

**Alternative Structures (if appropriate):**

**Kishotenketsu:**
- Introduction → Development → Twist → Reconciliation
- Good for contemplative stories

**In Medias Res:**
- Start in middle of action
- Reveal context through flashbacks
- Good for mysteries/thrillers

**Circular:**
- End where you began, but transformed
- Good for character studies

**Help user select:** "Based on your story, [structure] would work well because [reason]."

### Plot Beat Planning

**Map major beats to structure:**

**For each act, identify:**

**Act 1 Beats:**
1. Opening image/status quo
2. Inciting incident (what disrupts normalcy)
3. Decision point (protagonist commits)
4. End of Act 1 (crosses threshold)

**Act 2 Beats:**
5. Rising action (obstacles and attempts)
6. **Midpoint** (revelation that shifts everything)
7. Complications escalate
8. Dark moment (lowest point, seems hopeless)

**Act 3 Beats:**
9. Climax (final confrontation/choice)
10. Resolution (consequences, new normal)
11. Closing image

**Adjust based on format:**
- Flash: Highly compressed, may only have 3-4 beats
- Short Story: 5-7 key beats
- Epic: Many more beats, subplots
- Serialized: Beats distributed across chapters

### Tension Architecture

**Build escalation pattern:**

**Stakes Progression:**
- How do stakes increase?
- What gets worse over story?
- Why can't protagonist walk away?

**Obstacles Escalation:**
- List 3-5 major obstacles
- Each harder than last
- Each requires protagonist to grow/adapt

**Information Revelation:**
- What does protagonist learn and when?
- What's hidden from reader/protagonist?
- When are secrets revealed?

### Scene-Level Planning

**Break plot into scenes (especially for longer formats):**

**For each major scene:**
- Purpose (what it accomplishes)
- Whose POV
- Key conflict or revelation
- How it connects to overall arc
- Pacing (fast action or slow reflection)

**Typical scene counts:**
- Flash Fiction: 1 scene
- Short Story: 3-5 scenes
- Epic: 20-50+ scenes
- Serialized: 2-4 scenes per chapter

### World/Lens Integration

**If world or lens specified:**

**World Mechanics:**
- How do world's unique elements create obstacles?
- How do they enable solutions?
- What conflict arises from world's nature?

**Genre Lens:**
- How does lens structure apply?
- Genre-specific beats to hit
- Conventions to satisfy or subvert

**Example (Telvaren + Mystery):**
- Inciting incident: Discover memory was edited
- Midpoint: Realize protagonist's own memories unreliable
- Climax: Confront who edited memories and why
- Resolution: Choose to preserve truth or accept edit

---

## Output Format

**STEP 3: Present Plot Outline**

Create structured plot outline:

```markdown
# Plot Outline: [Story Title/Concept]

## Core Concept

**Protagonist:** [Name/description]
- Wants: [External goal]
- Needs: [Internal growth]

**Central Conflict:** [What prevents them from succeeding]

**Stakes:** [What happens if they fail]

**Theme:** [Central question or truth]

## Structure: [Three-Act / Other]

### Act 1: Setup (Target: [X] words/pages)

**Opening:** [Status quo, who protagonist is]

**Inciting Incident:** [What disrupts normalcy]

**Decision/Commitment:** [Protagonist commits to goal]

**Act 1 End:** [Crosses threshold into journey]

### Act 2: Confrontation (Target: [X] words/pages)

**Rising Action:**
- Obstacle 1: [Description]
- Obstacle 2: [Description]

**Midpoint:** [Major revelation or reversal - around 50%]

**Complications:**
- Obstacle 3: [Description]
- Obstacle 4: [Description]

**Dark Moment:** [Lowest point, seems hopeless]

### Act 3: Resolution (Target: [X] words/pages)

**Climax:** [Final confrontation/choice]

**Resolution:** [Consequences, how conflict resolves]

**Closing:** [New equilibrium, where protagonist ends]

## Key Scenes
[If applicable - breakdown of major scenes]

1. [Scene description, purpose, pacing]
2. [Scene description, purpose, pacing]
etc.

## World/Lens Integration
[If applicable - how world mechanics or genre lens shapes plot]

## Pacing Notes
[Fast vs. slow sections, tension peaks]
```

**STEP 4: Refine if Needed**

Ask: "Does this plot structure work? Any adjustments or gaps to address?"

Iterate until user is satisfied.

---

## Advanced Options

### Problem-Solving Mode

If user has existing story with plot problems:

**Ask:**
- "What's not working?"
- "Where does the story feel weak or stuck?"

**Diagnose common issues:**
- Sagging middle → Need midpoint revelation
- Weak stakes → Make failure consequences clearer/worse
- Predictable → Subvert expectations, complicate
- Rushed ending → Ensure sufficient setup
- Unearned resolution → Plant seeds earlier

### Subplot Planning

For epic or complex stories:

**Identify subplots:**
- What secondary stories exist?
- How do they intersect main plot?
- When do they resolve?

**Ensure each subplot:**
- Has own mini-arc
- Connects to main story thematically
- Doesn't overshadow main plot
- Resolves before or during climax

### Chapter Planning (Serialized/Epic)

If user planning serialized or epic:

**Map beats to chapters:**
- Which chapters contain which beats?
- Chapter-end hooks for each
- Pacing variation (fast/slow chapters)
- POV rotation (if multiple)

---

## Auto-Save Option

**STEP 5: Save Plot Outline (Optional)**

Ask: "Would you like me to save this plot outline?"

If yes, save using OpenCode file-writing tools:

**Filename:**
```
plot-outline-[title-slug]-[world]-[timestamp].md
```

Example: `plot-outline-memory-fragments-telvaren-20251105.md`

**File structure:**
Use the markdown outline format created in Step 3.

If the user approves saving, write the file to the current working directory as requested.

---

## Integration with Write-Story

**If user is planning for write-story workflow:**

Note: "This plot outline is ready to use with the `story-write-story` workflow. When you run that workflow and reach Phase 1 (Story Concept), you can reference this structural planning."

---

## Plot Planning Principles

Throughout this process, emphasize:

1. **Conflict drives plot** - No conflict = no story
2. **Stakes must be personal** - Protagonist must care deeply
3. **Escalation is essential** - Each obstacle harder than last
4. **Structure serves story** - Choose framework that fits
5. **Midpoint shifts everything** - Revelation that reframes journey
6. **Climax must be earned** - Setup throughout, payoff at end
7. **World mechanics create unique plots** - Use what makes world special

---

## Example Prompts for User

If user is stuck, offer prompts:

**For Conflict:**
- "What's the worst thing that could happen to your protagonist?"
- "What do they want that they absolutely can't have?"

**For Stakes:**
- "What would they lose if they fail?"
- "Why can't they just walk away from this?"

**For Midpoint:**
- "What revelation would change everything they thought they knew?"
- "What truth have they been avoiding that must surface halfway through?"

**For Climax:**
- "What's the final test of who they've become?"
- "What choice will define them?"

---

## Final Notes

The plan-plot workflow is a standalone tool that helps users structure narratives using proven story theory. It can be used:
- Before writing (preparation and planning)
- During writing (when stuck or lost)
- For revision (fixing structural problems)
- For learning (understanding plot craft)

Plots developed through this workflow provide strong foundations for stories created via write-story or other creative work.

The goal is not rigid adherence to formula, but understanding structural principles that make stories work—then applying them thoughtfully to serve each unique narrative.
