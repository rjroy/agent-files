---
title: Bounded independent review through OpenRouter
date: 2026-10-26
status: draft
tags: [openrouter, independent-review, plugin, oh-my-opencode-slim]
---

# Bounded independent review through OpenRouter

Discussion notes, not an implementation authorization or finalized specification. No configuration changes or paid review calls have been made for this proposal.

## Goal

Add independent challenge from non-OpenAI models to the existing mostly OpenAI agent workflow without unpredictable spending. The user's comfortable initial budget is $25–50/month. The primary value sought is independent perspective, not replacing everyday implementation capacity.

## Direction reached

Favor a narrow plugin exposing a dedicated review tool, with a companion skill, rather than a skill that invokes ordinary subagents.

The user identified two reasons:

- The calling model should request a review capability without making special decisions about subagent configuration, model selection, permissions, and retries.
- oh-my-opencode-slim strongly governs delegation. A competing skill-only subagent workflow would work against that routing rather than establish a clean boundary.

The initial skill-only recommendation was revised in response. Exact plugin integration and runtime behavior still need investigation.

## Responsibility boundary

**omo-slim owns the workforce; the review plugin owns an external second opinion.**

```text
Orchestrator prepares a bounded question and evidence
    → dedicated independent-review tool
    → plugin applies configured model/provider and budget policy
    → direct OpenRouter request
    → structured findings, evidence gaps, and usage
    → existing agents verify findings and implement any accepted changes
```

The external reviewer does not implement changes, access filesystem tools, or delegate further. Missing evidence should produce an explicit evidence gap, not an invented conclusion. Existing agents can collect additional evidence for a separately justified follow-up.

### Companion skill

- Explain when independent review is worthwhile.
- Define an adequate evidence packet.
- Guide interpretation and verification of findings.
- Describe when human approval for escalation is needed.

### Plugin and tool

- Select models/providers using user-owned configuration.
- Handle credentials, request limits, usage accounting, and bounded retries.
- Enforce supported budget controls rather than relying on prompt instructions.
- Prevent silent premium fallback.
- Return a consistent result with findings, evidence gaps, completion status, and actual usage/cost when available.
- Keep the external reviewer separate from normal agent execution.

### omo-slim routing

Proposed narrow rule: independent cross-model challenge uses the review tool; ordinary technical review, investigation, and implementation remain with existing agents.

This rule remains a proposal. The plugin alone does not guarantee that the orchestrator will select it or avoid duplicate review.

## Proposed interface

Illustrative, not a committed API:

```text
request_independent_review(question, evidence, constraints)
    → findings, evidence gaps, usage/cost, completion status
```

Prefer task-oriented inputs over exposing subagent/model/system-prompt/permissions configuration to the caller. Keep model policy in plugin configuration. Any premium-escalation interface and authorization mechanism remain undecided.

## Model preferences and routing

The user favors GLM-5.3 and DeepSeek V4.1 Flash, with Sonnet 5.5 or possibly Opus 5.5 for selected higher-cost reviews.

Proposed trial:

- Compare DeepSeek and GLM on similar bounded reviews.
- Pick the usual challenger using verified useful findings, not price alone.
- Use Sonnet or Opus only when stakes or unresolved uncertainty justify escalation.
- Do not automatically invoke all four models or construct a mandatory escalation ladder.

For deliberately independent parallel reviews, provide the same evidence but withhold the other reviewer's conclusions initially. Agreement is not proof; disagreement needs investigation, not majority voting.

Observed catalog IDs on 2026-10-26:

- `z-ai/glm-5.3`
- `deepseek/deepseek-v4.1-flash`
- `deepseek/deepseek-v4.1-flash-1017`
- `anthropic/claude-sonnet-5.5`
- `anthropic/claude-opus-5.5`

Pricing is volatile. The DeepSeek alias and dated version had materially different prices; the dated version also listed time-dependent overrides. Verify actual provider routes, prices, reasoning billing, and data policies before implementation. Earlier discussion initially overlooked newer Sonnet models; Sonnet 4.5 is not the preferred comparison candidate.

## Cost and privacy controls

- Trial budget: $25–50/month; a dedicated key with an initial $25 monthly limit was proposed, not configured.
- Consider a modest prepaid balance without automatic replenishment during the trial.
- Start with one response per review; further paid passes require a deliberate decision.
- Bound evidence size, output, retries, concurrency, and premium escalation.
- A prompt saying “spend no more than $1” is not a financial control.
- Output token limits alone do not establish a dollar ceiling; input, reasoning, tool charges, and retries matter.
- Provider/key limits may permit in-flight overage. Investigate budget reservation and accounting before claiming strict per-review or monthly enforcement.
- Do not transmit the whole conversation, full skill library, private profile, credentials, or unrelated files. Pass relevant constraints and the minimum sufficient evidence.
- Check provider data handling before sending private or proprietary material.

## Review contract

Ask for material failure modes, unsupported assumptions, and missing verification. Require evidence, severity, uncertainty, and a way to establish each concern. Permit “no material findings.” Do not reward objections merely for being adversarial.

Useful triggers include difficult-to-reverse architecture, security or data-integrity changes, public APIs, migrations, substantial cross-system changes, and persistent disagreement or failed fixes. Routine changes do not automatically need paid review.

Evidence packets should include the objective, acceptance criteria, relevant constraints, design or diff, necessary surrounding code, and test evidence. Omitting crucial context creates false positives; indiscriminately forwarding context creates cost and privacy risks.

## Trial evaluation

Track actual review cost, new material findings confirmed by existing agents, false positives, investigation time, and whether a review changed a decision or prevented a defect. Roughly ten meaningful reviews was suggested as an initial evaluation point, not a fixed requirement.

## Next design questions

- Verify the installed OpenCode/plugin APIs and omo-slim integration points.
- Decide how the plugin exposes or packages its companion skill.
- Establish provider policy, key storage, redaction, and permission boundaries.
- Define budget enforcement, concurrent-call reservations, accounting failures, and retry behavior.
- Decide whether evidence is inline only or assembled through controlled local tooling.
- Define result validation and handling of incomplete, malformed, or reasoning-only responses.
- Define explicit authorization for premium escalation.

Keep the initial scope to one tool, one companion skill, and one narrow routing rule. Do not build a second orchestration system.

## Sources consulted during discussion

- Current project agent configuration: `config/oh-my-opencode-slim.json`.
- OpenRouter live model catalog: <https://openrouter.ai/api/v1/models>.
- OpenRouter spending controls: <https://openrouter.ai/docs/guides/best-practices/spend-controls>.
- OpenCode V2 documentation: <https://opencode.ai/v2/docs/>.

These notes preserve the discussion's direction. Recheck live documentation and installed implementation before choosing configuration fields or claiming enforceable controls.
