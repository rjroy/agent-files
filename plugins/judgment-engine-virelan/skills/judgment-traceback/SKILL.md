---
name: judgment-traceback
description: Use when you want to understand why you got a particular response, when something feels off and you need to diagnose the system's logic, when you're curious what influenced specific advice or framing, or when you want to learn how the Judgment Engine makes decisions. Provides transparency into reasoning.
---

# Judgment Traceback 🧭

A skill for understanding why the system produced its last output—the decisions, postures, and files that shaped it.

---

## Use This When

- You want to understand why you got a particular response
- Something feels off and you need to diagnose the system's logic
- You're curious what influenced a specific piece of advice or framing
- You want to learn how the Judgment Engine makes decisions

---

## What This Does

Judgment Traceback provides transparency into the system's reasoning:

1. Restates the user input that triggered the action
2. Identifies which mode(s) or posture(s) were active
3. Lists the key constraints and context files in play
4. Explains decision branches taken, including discarded options
5. Closes with what could change the outcome if re-run

---

## Operation Flow

### Step 1: Input Echo
Restate what you asked or what triggered the previous response.

### Step 2: Active Mode Identification
What mode, skill, or posture was active?
- Was it default Interaction Posture?
- Was a specific skill invoked?
- Was a role active (Quinn, Max, etc.)?

### Step 3: Context Files
What context was loaded?
- Core Posture Layer (always on)
- Specific mode documentation
- Role definitions
- User-provided context

### Step 4: Decision Branches
What choices did the system make?
- What approach was chosen and why?
- What alternatives were considered?
- What constraints influenced the choice?
- What assumptions were made?

### Step 5: Counterfactuals
What would change the output?
- Different mode or posture
- Additional context
- Different user phrasing
- Changed constraints

---

## Output Format

```
### Input Echo
[What you asked or what triggered the response]

### Active Configuration
**Mode/Skill**: [What was running]
**Posture**: [If any role was active]
**Context files**: [What was loaded]

### Decision Trace

**Approach chosen**: [What the system did]

**Why this approach**:
- [Reasoning factor 1]
- [Reasoning factor 2]

**Alternatives considered**:
- [Option A] - Discarded because [reason]
- [Option B] - Discarded because [reason]

**Key constraints**:
- [What limited the choices]

**Assumptions made**:
- [What the system assumed]

### Counterfactuals

**Would change if**:
- [Different mode]
- [Additional context]
- [Different phrasing]

**To get different output, try**:
- [Specific suggestion]
- [Another approach]
```

---

## Example Traces

### Example 1: Why Max was suggested
```
Your input: "This feels too easy"

Active: Default Interaction Posture
Context: Core Posture (fluency masks fragility)

Decision: Suggested Max posture

Why: "Too easy" triggered fluency warning.
System interpreted as potential fragility masked
by smooth language. Max's challenging stance
appropriate for testing what survives pressure.

Could change if:
- You specified "this solution is simple and robust"
- You asked for Herald (amplifying existing clarity)
```

### Example 2: Why Writing Workshop wasn't invoked
```
Your input: "Review this draft"

Active: Default Interaction Posture
Context: Core Posture only

Decision: Provided inline feedback

Why: No explicit Workshop invocation. "Review"
interpreted as wanting direct feedback rather
than structured Workshop process with authorship
protection and multi-stage revision.

Would invoke Workshop if:
- "Workshop this draft"
- "Help me strengthen this without ghostwriting"
- Clear signal of wanting protected authorship
```

---

## Meta-Use

Judgment Traceback can be run on itself:

"Why did Traceback give me that specific output?"

This reveals the system's self-awareness and helps you understand how transparency itself is structured.

---

## Flows Into

- **System Diagnostic** → for broader system state overview
- **Writing Workshop** → if traceback reveals tone or framing issues
- **Convergence Move** → if understanding the logic helps make a decision

---

## Example Invocation

"Run Traceback - why did you suggest that mode?"

"Judgment Traceback on your last response."

"I want to understand why you framed it that way."

"Traceback mode - what influenced that recommendation?"
