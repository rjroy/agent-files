---
description: Use when you want to interrogate a concept, system, or plan systematically, when you need to force judgment through structured questioning, when you want one question at a time (not all at once), or when preparing for a review, planning session, or decision point. Conducts interactive interrogation.
---

# Q&A Runner 🧠

A skill for interrogating concepts, systems, or plans—one question at a time.

---

## Use This When

- You want to interrogate a concept, system, or plan systematically
- You need to force judgment through structured questioning
- You want one question at a time, not all at once
- You're preparing for a review, planning session, or decision point

---

## What This Does

Q&A Runner conducts interactive interrogation by:

1. Accepting a target context and optional prompt set
2. Optionally setting a posture (Quinn, Max, Librarian, etc.)
3. Asking one question at a time
4. Waiting for your answer
5. Optionally following up based on posture
6. Continuing until you exit, export, or change topic

---

## Operation Flow

### Setup
1. **Define Target Context**: What are we interrogating?
2. **Choose Prompt Set** (optional): Use a pre-defined question bank, or let the skill generate questions
3. **Set Posture** (optional): Quinn (reflective), Max (challenging), Librarian (precision), Field Guide (procedural), etc.

### Loop
For each question:
1. **Ask** one focused question
2. **Wait** for your response
3. **Optional follow-up** if posture requires deeper probing
4. **Continue** to next question or let you control flow

### Controls
- **Continue**: Move to next question
- **Skip**: Pass on this question
- **Change Posture**: Switch to different role mid-session
- **Export**: Save session as Inquiry Digest
- **End**: Complete the session

---

## Output Format

```
### ❓ Question [#]: [The question]

[Your response appears here]

(Optional follow-up based on posture)

→ Continue | Skip | Change Posture | Export | End
```

---

## Posture Effects

**Quinn** 🦆: Reflective, grounding questions. Holds space for judgment without pressure.

**Max** 🪓: Challenging questions that test what you're avoiding or assuming.

**Librarian** 📘: Precision questions about definitions, defaults, and ambiguities.

**Field Guide** 🧭: Procedural questions about steps, dependencies, and clarity.

**Systems Analyst** 🧠: Questions about interactions, unintended consequences, and dependencies.

---

## Feeds Into

- **Writing Workshop** → sharpen your answers into shareable docs
- **Judgment Traceback** → audit which answers held and which wobbled
- **Inquiry Digest** → compress the session into reusable insights
- **Coherence Pass** → integrate scattered insights from the session

---

## Pre-Built Prompt Sets

The skill includes several pre-built question banks:

- **Planning Basics**: Priority, escalation, delegation, failure handling
- **Core Profile Extraction**: Observable behavior patterns for leadership assessment
- **API Review**: Assumptions, silent defaults, missing flows, error handling
- **1-on-1 Prep**: What's alive, where's pressure, what's the move

To use: "Run Q&A Runner with the Planning Basics prompt set"

---

## Example Invocation

"Start Q&A Runner. Target: my new feature design. Posture: Max."

"Q&A Runner with Librarian posture - I need to review this API spec."

"Use the Core Profile Extraction prompt set to help me think through this team member."

"Continue the Q&A session from earlier about the planning decision."
