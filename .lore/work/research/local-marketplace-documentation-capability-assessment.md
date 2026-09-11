---
title: Local Marketplace documentation capability assessment
date: 2026-09-11
status: complete
tags: [workflow, opencode, forge, factory, documentation]
related: [workflow-comparison-review.md, workflow-comparison-baseline-evidence.md, workflow-comparison-trial-proposal.md, workflow-comparison-safety-preflight.md]
---

# Local Marketplace documentation capability assessment

## Key findings

The available local documentation supports a narrow, documentation-led assessment, not an adoption or runtime-support conclusion. Forge offers a dependency graph with test and evidence gates, replanning, strict validation, and documented A2A/Pi workflows. Factory offers contract loading, read-only gathering, pure decision-making, schema-validated dry-run reports, and a supervised handoff. These are useful design capabilities relative to the current OpenCode workflow, especially where durable machine-checkable execution evidence or explicit pre-dispatch gates are wanted.

OpenCode is a POC target, not a supported drop-in runtime in the available material. The local portability document says targeted adapters are required for command frontmatter, Teamsters dispatch, model aliases, and Ponytail hooks. It describes `opencode.jsonc` as a POC. The documented portable core is narrower: skills, deterministic Factory scripts, schemas, and some provider-contract configuration.

No trial, import, installation, clone, adapter, OpenCode configuration change, or live service interaction occurred for this assessment. Runtime effectiveness, safety in execution, and current upstream release status remain unverified.

## Source and release status

The local README identifies the claimed upstream repository as <https://github.com/ai-sand-castles/local-marketplace>. On 2026-09-11, authenticated `gh api` repository, releases, and tags requests returned HTTP 404, `gh repo view` could not resolve the repository, and public web requests for the repository, releases, and tags also returned HTTP 404:

- <https://github.com/ai-sand-castles/local-marketplace>
- <https://github.com/ai-sand-castles/local-marketplace/releases>
- <https://github.com/ai-sand-castles/local-marketplace/tags>

This may mean the repository is private, renamed, deleted, or inaccessible to the current GitHub identity. It prevents verification of an official upstream README, repository metadata, tags, releases, commit provenance, and current support policy. Do not treat the local tree as a verified checkout: the earlier baseline records that it resolves within this workspace rather than as an independent Git worktree.

The local marketplace README lists Forge `0.14.0` and Factory `0.1.0` in its plugin table. They are local documented plugin versions only, not verified GitHub releases or tags.

## Capability comparison for the OpenCode workflow

| Capability | Documentary evidence | OpenCode disposition |
| --- | --- | --- |
| Dependency-aware planning and replanning | Forge documents a spec-to-DAG model, ready frontier, stale-state handling, `graph replan`, and strict validation of reachability, evidence drift, capability coverage, and acceptance. | Useful conceptual or adapter candidate. It is not shown installed, loaded, or effective in OpenCode. |
| Test and acceptance evidence | Forge records tests, command exit status, hashes, graph revision, and operator receipts. | Potentially valuable where the current instruction-led workflow needs durable evidence. Running it would add `.forge` state and is outside this assessment. |
| Pre-dispatch gating | Factory documents contracts, read-only snapshots, pure decisions, a validated dry-run report, and a stop at supervised handoff. Optional orchestration starts only after that boundary. | Strongest portable candidate on documentation: deterministic scripts and schemas are described as runtime-agnostic. No OpenCode execution support is proven. |
| Parallel dispatch and delegation | Forge documents A2A/Pi workflows. The marketplace composes Factory with Teamsters for worker dispatch. | Unsupported for OpenCode from this evidence. Teamsters uses Claude-specific `Agent`/`Task` semantics and model aliases. |
| Hooks and always-on simplification | Ponytail supplies review policy, but the portability document identifies its JS hook events as Claude/Codex-coupled. | Prompt-level policy may transfer, but no OpenCode-native hook equivalent is documented. |
| Local OpenAI-compatible providers | The portability POC describes an OpenAI-compatible provider route and local vLLM configuration. | POC only. Tool-call reliability, parser configuration, context degradation, and observability are documented risks. |

## Decision-relevant limits and unknowns

The evidence supports retaining the existing OpenCode workflow as the supported runtime. Treat Forge graph and Factory dry-run concepts as documentation-backed adaptation candidates, not plugins ready to install. Do not replace Beads, current work artifacts, or existing acceptance practices: the local material supplies no reconciliation design between Beads and Forge/Factory state.

The critical unresolved claims are whether the claimed upstream remains available and maintained, which exact revision the local tree represents, whether an OpenCode adapter exists upstream, and whether the required dispatch, hook, model-routing, and lifecycle surfaces work with this OpenCode version. If one of those claims becomes decision-critical, an explicitly authorized, isolated smoke test can target that claim. Runtime testing is not a blanket prerequisite for the documentation conclusions above.

## Local sources

- [Local marketplace README](../../../tmp/local-marketplace/README.md), plugin roles and local version table.
- [Forge README](../../../tmp/local-marketplace/forge/README.md), graph, validation, replan, A2A, and Pi claims.
- [Factory README](../../../tmp/local-marketplace/factory-plugin/README.md), contract, read-only gather, pure decision, dry-run, and supervised-handoff claims.
- [OpenCode portability POC](../../../tmp/local-marketplace/docs/opencode-portability.md), dated 2026-06-28, adapter inventory and runtime risks.
- [Baseline evidence](workflow-comparison-baseline-evidence.md), local-tree identity and dated current-workflow boundary.
