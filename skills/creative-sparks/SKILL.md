---
name: creative-sparks
description: Offer small, open-ended creative prompts within a frame the user has chosen, such as a theme, world, lens, and medium. Use when they want inspiration or a few sparks before doing their own imagining, not developed concepts, plots, or lyrics.
---

# Creative Sparks

Offer a small page of prompts, like opening a chosen book to a page of prompts: the user supplies the frame (for example, Halloween + Virelan + song), and you give them room to imagine. This is a light on-ramp, not concept development. Do not invoke or run another workflow automatically.

## Make the sparks

- Unless the user asks for another amount, give about 5–8 sparks. Keep each to one sentence and leave it unfinished in spirit: an image, question, fragment, contradiction, or situation that invites the user's own idea.
- Vary the forms naturally; do not sort them into a taxonomy or force every kind into each page.
- Be evocative and specific enough to catch on, but do not turn a seed into a premise, pitch, character package, full arc, lyric, or plot outline. Do not rank, score, assign probabilities, or recommend a favorite.
- Do not add a selection gate or compulsory follow-up question. The user can take, combine, ignore, or continue any fragment.
- Respect the user's chosen theme, world, lens, medium, mood, and constraints. Avoid importing unrelated references. When a known world or lens matters, consult the relevant installed reference before writing; distinguish speculative sparks from established lore, and never present invented details as canon. If a reference is unavailable, stay general rather than guessing.
- Clarify only when a genuinely missing part of the frame blocks useful prompts. Otherwise, use what is known and keep ambiguity open.

## Continue from the user's fragments

If the user reacts to a spark, respond to that fragment and branch from it without completing or taking ownership of the idea. Offer a few adjacent openings if useful. Do not fill in the user's premise, decide what it means, or push toward a complete concept unless they ask.

If they ask for more or stranger sparks, provide another small, fresh page that honors their direction, including any liked or disliked qualities they named. Do not inflate the material into a developed concept.

## Handoff

Only hand material to a downstream workflow when the user asks. Preserve their own fragments and open questions, and label any assistant-generated sparks as exploratory rather than selected or approved. Do not bypass the receiving skill's approval, selection, or other entry requirements. In particular, offering song sparks does not authorize the `music-write-lyrics` workflow, and offering story sparks does not authorize `story-plan-plot`.

## Files and workflow boundaries

Do not create or edit files during ordinary use. Save or hand off material only when the user requests it, and only within the authorized scope. This skill does not start songwriting or plot-planning workflows, create approved concepts, or make selections on the user's behalf.

## Finding references

When relevant lore or lens context is needed, first locate and read the installed `music-engine-reference` or `story-engine-reference` skill entrypoint using the available skill discovery/read capabilities. Resolve its listed resource paths relative to that reference skill's installed directory, not this skill's directory, a sibling-relative path, or the current working directory. Load only the selected world's/lens's relevant material. If the reference skill cannot be located, do not assume a path or invent lore; keep prompts clearly speculative and broad.
