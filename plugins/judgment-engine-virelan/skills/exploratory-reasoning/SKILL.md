---
name: exploratory-reasoning
description: Use when the question is too big to solve but too important to guess, when you need thinking space that sharpens structure, when answers feel fluent but hollow, or when each thought adds complexity without traction. Generates multiple distinct reasoning paths with assumptions and risks visible.
---

# Exploratory Reasoning 🧭

A skill for breaking open big questions and returning multiple paths with their assumptions and risks visible.

---

## Use This When

- The question is too big to solve, but too important to guess
- You need thinking space that sharpens structure, not just ideas
- Answers feel fluent but hollow
- Each thought adds complexity without traction

---

## What This Does

Exploratory Reasoning generates multiple distinct reasoning paths for complex questions:

1. Restates the root question to sharpen framing
2. Returns 3+ distinct reasoning paths (not variations of the same approach)
3. For each path: names assumptions, surfaces risks, defines when it holds
4. Closes with cross-path prompts to test thinking

---

## Operation Flow

### Step 1: Sharpen the Root Question
Take your question and reframe it for clarity. Sometimes the reframing itself reveals assumptions.

### Step 2: Generate Distinct Paths
Create 3-5 genuinely different approaches. Not:
- Variations on the same theme
- Different implementations of the same solution
- Superficial re-framings

But truly different lenses or frameworks for thinking about the problem.

### Step 3: For Each Path

**Assumptions**: What must be true for this path to work?

**Risks**: Where does this approach break down?

**Right if**: Under what conditions would this be the correct path?

### Step 4: Cross-Path Prompts
Questions that test across all paths:
- What breaks first in each path under pressure?
- What does each path pretend not to care about?
- What costs are visible in one path but hidden in others?
- Where do paths overlap in surprising ways?

---

## Output Format

```
### Root Question
[Restated and sharpened version of your question]

### Path 1: [Approach Name]
**Core idea**: [What this path prioritizes]
**Assumptions**:
- [What must be true]
- [Another assumption]
**Risks**:
- [Where this breaks]
- [What this ignores]
**Right if**: [Conditions under which this path works]

### Path 2: [Different Approach]
[Same structure]

### Path 3: [Yet Another Approach]
[Same structure]

### Cross-Path Prompts
- What breaks first in each path under pressure?
- What does each path pretend not to care about?
- [Additional testing questions specific to these paths]
```

---

## Example Paths

**Question: "How should we prioritize technical debt?"**

Path 1: **User Impact First**
- Assumptions: User-facing issues are most critical
- Risks: Backend fragility accumulates silently
- Right if: User trust is the limiting factor

Path 2: **System Health First**
- Assumptions: Stable foundation enables all else
- Risks: Visible user issues erode trust faster
- Right if: Team has breathing room to address foundations

Path 3: **Team Capacity First**
- Assumptions: Sustainable pace prevents larger failures
- Risks: Urgent issues may force unsustainable work anyway
- Right if: Team morale and retention are at risk

---

## Flows Into

- **Simulated Debate** → to stress-test two paths against each other
- **Convergence Move** → when you need to choose or combine paths
- **Idea Crucible** → to pressure-test a specific path before committing
- **Coherence Pass** → if paths reveal unexpected common ground

---

## Guards

- **Truly distinct paths**: Not just variations
- **Honest about assumptions**: Every path rests on something
- **Explicit about risks**: Every approach has fracture points
- **Conditional validity**: No path is universally right

---

## Example Invocation

"Run Exploratory Reasoning on: How should we structure our testing strategy?"

"I need different thinking paths for this architecture decision."

"Exploratory mode - I keep circling the same solution and need genuinely different approaches."
