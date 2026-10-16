---
name: story-develop-character
description: Collaboratively create and refine a story character profile grounded in character-development theory.
---

**Conversational use:** Accept the user request and any available context directly; do not require slash-command syntax or a positional `$ARGUMENTS` string. Clarify only missing required choices. Use OpenCode-supported file and subagent capabilities.

# story-develop-character Skill

## Skill Activation

Use this skill when the user wants to create or refine one or more story characters.

---

## Purpose

This workflow helps users develop rich, authentic characters for their stories using structured character development theory. It can be used:
- Standalone (developing characters before or outside main story workflow)
- As preparation for write-story workflow
- For refining existing characters
- For exploring character concepts

---

## System Activation

**STEP 1: Load the story-engine-reference skill**

Consult the sibling `story-engine-reference` skill and load only relevant reference files:

```
`../story-engine-reference/SKILL.md`
```

**STEP 2: Load character development theory**

Read this resource relative to the current `story-develop-character` skill directory:
- `../story-engine-reference/story/theory/theory-character-development.md`

**Optional (if user mentions world):**
- `../story-engine-reference/story/worlds/world-[worldname].md`

---

## User Interaction

**STEP 1: Understand User's Need**

Ask clarifying questions:

1. **Context:**
   - "Are you developing this character for a specific story, or exploring independently?"
   - If for specific story: "What's the story about? What role does this character play?"

2. **Starting Point:**
   - "Do you have any initial ideas about this character, or should we start from scratch?"

3. **World (if applicable):**
   - "Which story world is this character from?" (Currently: Telvaren)
   - If Telvaren or other world, load that world file

---

## Character Development Process

**STEP 2: Guided Character Creation**

Using loaded theory, help user develop character through structured questions:

### Core Identity

**Ask and develop:**

**Who are they?**
- Name
- Role/profession
- Key defining trait
- What makes them memorable?

**Desire (External)**
- What do they want? (plot-level goal)
- Why do they want it?
- What are they willing to do to get it?

**Need (Internal)**
- What do they actually need? (character-level growth)
- What's missing from their life?
- What would make them whole?

**Fear**
- What prevents them from acting?
- What are they afraid of losing/becoming/discovering?
- How does fear complicate desire?

### World Integration (if applicable)

**If character is from specific world (e.g., Telvaren):**

**Relationship to world mechanics:**
- How do they interact with this world's unique elements?
- Are they empowered or limited by world mechanics?
- What about this world shapes who they are?

**Example prompts for Telvaren:**
- "Do they have Memory Shaper abilities?"
- "How do they feel about memory editing?"
- "Have their memories been edited? Do they know?"

### Voice and Personality

**Develop distinctive traits:**

**Speech patterns:**
- Formal or casual?
- Talkative or reserved?
- Vocabulary level and style
- Recurring phrases or verbal tics

**Perspective:**
- Optimistic or cynical?
- Analytical or emotional?
- What do they notice that others miss?

**Behavior:**
- How do they handle stress?
- How do they treat people with less power?
- What habits define them?

### Relationships

**If developing multiple characters or character has key relationships:**

**Function in story:**
- Protagonist, ally, antagonist, foil, mirror?

**Key relationships:**
- Who matters to them?
- Who do they trust/distrust?
- Who challenges them?
- Who do they want to protect/impress/defeat?

### Character Arc

**Transformation over story:**

**Starting state:**
- Who are they at story's beginning?
- What defines them?
- What do they believe?

**Pressure:**
- What challenges them?
- What forces growth?
- What they must confront?

**Defining choice:**
- What decision transforms them?
- What must they sacrifice or risk?

**Ending state:**
- Who have they become?
- What's changed?
- What have they learned/lost/gained?

---

## Output Format

**STEP 3: Present Character Profile**

Create comprehensive character profile:

```markdown
# [Character Name]

## Core Identity

**Role:** [Profession/function in story]
**Defining Trait:** [What makes them memorable]

**External Desire:** [What they want - plot level]
**Internal Need:** [What they actually need - character level]
**Core Fear:** [What prevents them from acting]

## Personality & Voice

**Speech Pattern:** [How they talk]
- [Specific examples of vocabulary or verbal tics]

**Perspective:** [How they see the world]
**Distinctive Behaviors:** [Habits, quirks, patterns]

## World Integration
[If applicable - how they relate to world mechanics]

## Key Relationships
[If applicable - who matters and why]

## Character Arc

**Start:** [Who they are at beginning]
**Pressure:** [What challenges them]
**Choice:** [Defining decision]
**End:** [Who they become]

## Character Snapshot (50-100 words)
[Concise summary capturing essence]
```

**STEP 4: Refine if Needed**

Ask: "Does this character feel right? Would you like to adjust anything?"

Iterate on character until user is satisfied.

---

## Advanced Options

### Multiple Characters

If user wants to develop multiple characters:
- Develop one at a time
- After each, ask about relationships between characters
- Create character dynamics map if helpful
- Ensure each character has distinctive voice

### Character Contrast

If developing supporting character:
- Ask how they differ from protagonist
- What do they provide (skills, perspective, challenge)?
- How do they complicate protagonist's journey?

---

## Auto-Save Option

**STEP 5: Save Character Profile (Optional)**

Ask: "Would you like me to save this character profile?"

If yes, save using OpenCode file-writing tools:

**Filename:**
```
character-[name-slug]-[world]-[timestamp].md
```

Example: `character-aria-shadowkeeper-telvaren-20251105.md`

**File structure:**
Use the markdown profile format created in Step 3.

If the user approves saving, write the file to the current working directory as requested.

---

## Integration with Write-Story

**If user is developing characters for a story:**

Note: "These characters are ready to use with the `story-write-story` workflow. When you run that workflow and reach Phase 2 (Character Development), you can reference or adapt these profiles."

---

## Character Development Principles

Throughout this process, emphasize:

1. **Desire drives plot** - Character must want something
2. **Fear creates depth** - Internal conflict makes them interesting
3. **Voice distinguishes** - Each character should sound like themselves
4. **World shapes character** - Integration beats decoration
5. **Arc requires pressure** - Change must be earned
6. **Action reveals** - Who they are is what they do under stress

---

## Example Prompts for User

If user is stuck, offer prompts:

**For Desire:**
- "What would they risk everything for?"
- "What's the one thing they can't have but desperately want?"

**For Fear:**
- "What would destroy them if they lost it?"
- "What truth are they avoiding?"

**For Voice:**
- "How would they tell someone bad news?"
- "What word or phrase do they overuse?"

**For Arc:**
- "What belief do they hold that's actually wrong?"
- "What would force them to change?"

---

## Final Notes

The develop-character workflow is a standalone tool that helps users create deep, authentic characters grounded in narrative theory. It can be used:
- Before starting a story (preparation)
- Independently (character exploration)
- As practice (understanding character craft)
- For refinement (improving existing characters)

Characters developed through this workflow are ready to integrate into stories created via write-story or used in other creative work.
