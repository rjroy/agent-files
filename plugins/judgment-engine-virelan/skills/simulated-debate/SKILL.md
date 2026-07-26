---
name: simulated-debate
description: Use when two ideas both feel right but won't fit cleanly together, when you need structured tension (not synthesized agreement), when you keep toggling between values and constraints, when one side dominates but doesn't hold all the stakes, or when you want to test competing definitions or approaches. Creates multi-voice argument to reveal tensions.
---

# Simulated Debate 🗣️

A skill for surfacing structured tension when two ideas both feel right but won't fit cleanly together.

---

## Use This When

- Two ideas both feel right but won't fit cleanly together
- You need structured tension, not synthesized agreement
- You keep toggling between values and constraints
- One side dominates but doesn't hold all the stakes
- You want to test competing definitions or approaches

---

## What This Does

Simulated Debate creates a multi-voice argument to reveal tensions and hidden overlaps:

1. Frames the core disagreement via a Framer
2. Assigns participants (customizable or default)
3. Presents each position with arguments, assumptions, and blind spots
4. Cross-examines for false splits or disguised overlap
5. Concludes with synthesis prompts (not forced resolution)

---

## Operation Flow

### Step 1: Framing
Restate the problem and identify the axis of disagreement.

### Step 2: Assign Participants
**Default positions:**
- **Position A**: Principle-first view (default)
- **Position B**: Pragmatic-first view (default)

**Optional roles:**
- **Framer**: Sets the problem statement
- **Cross-Examiner**: Challenges both sides
- **Synthesizer**: Offers integration prompts (but doesn't force resolution)

You can customize these or request specific postures (e.g., "Position A is Max, Position B is Mara")

### Step 3: Present Arguments
For each position:
- Core argument
- Foundational assumptions
- Blind spots or weaknesses

### Step 4: Cross-Examination
- What A gets wrong about B
- What B gets wrong about A
- Shared tensions both miss
- False splits that disguise actual overlap

### Step 5: Synthesis Prompts
Not resolution—but questions that guide judgment:
- What judgment does this require?
- What's the real cost of choosing one?
- What would holding both look like?
- What's the hidden third option?

---

## Output Format

```
### Framing
[Restatement + axis of disagreement]

### Position A – [Label]
**Argument**: [Core claim]
**Assumptions**: [What must be true]
**Blind spots**: [What this misses]

### Position B – [Label]
**Argument**: [Core claim]
**Assumptions**: [What must be true]
**Blind spots**: [What this misses]

### Cross-Examination
**What A gets wrong about B**: [...]
**What B gets wrong about A**: [...]
**Shared tensions**: [What both miss]

### Synthesis Prompts
- What judgment does this require?
- What's the real cost of choosing one?
- [Additional prompts based on the tension]
```

---

## Example Debates

**Tech debt vs. feature velocity**
- Position A: Engineering sustainability
- Position B: Product delivery speed
- Cross-exam reveals both depend on same resource pool

**Clarity vs. nuance in communication**
- Position A: Directness and action-orientation
- Position B: Contextual depth and subtlety
- Cross-exam surfaces when each approach creates different failures

**Standardization vs. flexibility**
- Position A: Consistent patterns, lower cognitive load
- Position B: Context-specific optimization
- Cross-exam reveals hidden cost of either extreme

---

## Flows Into

- **Convergence Move** → after tension is well-surfaced and you need to act
- **Writing Workshop** → to turn debate insights into clear communication
- **Exploratory Reasoning** → if cross-exam reveals need for entirely different approaches
- **Judgment Traceback** → to understand why one position felt more compelling

---

## Guards

- **Don't force synthesis**: If the tension is real, hold it
- **Equal treatment**: Both positions get equal rigor
- **Cross-exam matters most**: The examination often reveals more than the positions
- **Watch for false binaries**: Sometimes the debate itself is the wrong frame

---

## Example Invocation

"Run Simulated Debate: Should we refactor now or ship first?"

"Debate mode - Position A: Focus on user impact. Position B: Focus on technical quality."

"I want to debate whether to centralize or distribute this decision-making."

"Simulated Debate with Max as Position A and Mara as Position B."
