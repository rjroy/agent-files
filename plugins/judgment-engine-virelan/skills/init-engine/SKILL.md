---
description: Use when any Judgment Engine skill is invoked, when any Judgment Engine command is run, or when the user explicitly requests to engage with the Judgment Engine system. This skill loads the foundational context that shapes how the Judgment Engine operates, including core posture, system roles, and conceptual glossary.
---

# Init Engine 🔧

Initializes the Judgment Engine by loading foundational context files that define the system's posture, roles, and conceptual framework.

---

## Purpose

This skill ensures that whenever the Judgment Engine is engaged—through any skill invocation, command execution, or explicit user request—the system operates with its full context loaded. It establishes the core directives, system roles, and shared vocabulary that make the Judgment Engine distinct.

---

## What This Loads

This skill loads three foundational context files:

@judgment-engine-virelan/skills/init-engine/reference/core-posture.md
@judgment-engine-virelan/skills/init-engine/reference/roles.md
@judgment-engine-virelan/skills/init-engine/reference/glossary.md

---

## When This Runs

This skill should be invoked:
- Before any other Judgment Engine skill executes
- When any Judgment Engine slash command is run
- When the user explicitly asks to engage the Judgment Engine
- At the start of any session where judgment-sharpening work is needed

---

## What It Does

1. Loads **Core Posture** - Defines the ambient tone, judgment posture, and interaction principles
2. Loads **System Roles** - Provides character roles (Quinn, Max, etc.) that shape response style
3. Loads **Glossary** - Establishes shared vocabulary for concepts like "stretch thinking," "fracture," and "fluency masks fragility"

These files work together to ensure the Judgment Engine maintains its distinctive approach: surfacing tension, protecting user judgment, and preferring structural integrity over premature resolution.

---

## Integration

Once loaded, these contexts inform:
- How other skills operate (Coherence Pass, Convergence Move, etc.)
- How commands behave (diagnostic, digest, etc.)
- The overall tone and approach of system responses
- Decision-making about when to hold tension vs. when to converge
