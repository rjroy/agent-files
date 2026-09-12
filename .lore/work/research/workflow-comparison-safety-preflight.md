# Workflow-comparison clone safety preflight

> **Superseded for the current assessment:** See [the documentation capability assessment](local-marketplace-documentation-capability-assessment.md). This execution-focused preflight remains historical safety context and does not authorize trials, loading, installation, or configuration changes.

**Issue:** `agents-alv.6`  
**Status:** partial and unfinished. Source-only inspection completed for the proposed Forge strict-validation and Factory dry-run admission paths; runtime safety and OpenCode loading remain unknown.  
**Scope:** static inspection only. No clone code was executed, installed, loaded, or imported. No network contact, trial, adapter, configuration change, commit, push, or sync occurred.

## Reviewed trial controls

The following pre-results controls were reviewed:

- [trial protocol](workflow-comparison-candidates-and-trial-protocol.md), lines 46-101, requires frozen common conditions, candidate-neutral tasks, a user-approved repeat count, and approved budgets, resource limits, commands, permissions, reviewers, and any OpenCode load trace before trials begin.
- [trial protocol](workflow-comparison-candidates-and-trial-protocol.md), lines 103-163, requires safety, feasibility, comparability, evidence-integrity gates, intervention logging, independent review, and preregistered directional metrics, thresholds, margins, and minima before any result.
- [decision rubric](workflow-comparison-decision-rubric.md), lines 16-46, requires a per-task/per-condition evaluation record, fixed common conditions, independent review, and a stop for unapproved sensitive actions. Its OpenCode feasibility gate requires source/API review and, only when authorized, a reproducible host registration/load trace. A manifest, README, or source presence is not a pass.
- [opportunity and risk register](workflow-comparison-opportunity-risk-register.md), lines 13-18 and 103-112, records an earlier inspection-only comparison and concludes that OpenCode loading and effective execution remain unknown. It supports bounded alternatives and trials, not adoption or replacement.

## Current source tree availability

The requested current source tree is present at `/home/rjroy/.agents/tmp/local-marketplace`, including `forge/`, `factory-plugin/`, and related project directories. The prior statement that this path was absent was erroneous and is retracted.

The scoped source-only inspection recorded below has been completed. Directory presence and the prior content snapshot still do not establish upstream provenance, execution safety, or OpenCode compatibility.

## Source-only inspection findings

**Identity and provenance.** The comparison directory exists at
`/home/rjroy/.agents/tmp/local-marketplace`. Its earlier recorded content
snapshot is SHA-256
`70daf1ea1c30e6bfb26fff52396753a62eb82d3e29cd6b5665899716bf94648f` over
5,773 files ([baseline evidence](workflow-comparison-baseline-evidence.md), lines 31-54).
It resolves inside the current worktree rather than as an independently
identified Git checkout (lines 35-42). The snapshot is a content identity, not
upstream origin, authorship, signature, or supply-chain provenance.

### Forge, scoped to strict validation rather than A2A execution

- **Validation behavior, inspected.** `forge/scripts/forge/validation.py`,
  lines 27-146, checks graph structure, capability gaps/quarantine, declared
  test and artifact existence, user-entrypoint and production-caller paths,
  exact evidence hashes, test command and zero exit status, and current
  acceptance receipts. The path checks establish existence only, not semantic
  reachability.
- **Filesystem behavior, inspected.** `forge/scripts/forge/store.py`, lines
  24-134, locates `.forge/plan.graph.json`, reads JSON, creates `.forge/`,
  writes `.forge/.gitignore`, atomically replaces graph files, creates a
  persistent adjacent lock file, and uses advisory locking. Therefore even a
  narrow Forge invocation writes run state and must be confined to a disposable
  worktree. Direct graph editing is expressly prohibited by its source comment
  (lines 1-7).
- **Out-of-scope execution surfaces, inspected as a risk.** The Forge `a2a/`
  source contains subprocess, local server, URL, environment, home-directory,
  skill-copy, worktree, telemetry, and network-sandbox paths, including
  `scripts/a2a/rpc.py`, lines 28-48; `provider.py`, lines 166-202;
  `telemetry.py`, lines 124-213; and `process_sandbox.py`, lines 105-338.
  These paths are excluded from the proposed I1/H1 trial. Source presence is
  not a guarantee that no unreviewed code path can reach them.

### Factory, scoped to one dry-run gate rather than dispatch

- **Admission decision, inspected.** `factory-plugin/scripts/run-factory-cycle.py`,
  lines 171-185 and 222-297, blocks stale control planes, unavailable or
  unready providers, pending approvals, blocked queues, and unknown agent
  state. A `would_dispatch` item is explicitly `apply: false`,
  `claim_task: false`, `write_mode: "read_only"`, and
  `operator_approval_required: true` (lines 283-296).
- **Actual writes and subprocess, inspected.** The same script invokes
  `validate-factory-artifacts.py` through `subprocess.run` (lines 505-515) and
  writes a JSON report under `reports/` (lines 535-539). Its `--snapshot` path
  uses resolved paths and requires the source fixture to stay within the
  contracts directory (lines 29-57), but this does not make arbitrary command
  execution or reports-directory writes safe outside an isolated copy.
- **Envelope coupling and credentials, inspected.**
  `factory-plugin/schemas/supervised-run-envelope.schema.json`, lines 7-30,
  requires approval, idempotency, bounded paths, validation commands,
  context/audit links, and signature metadata. It hard-codes Teamsters, Dream
  Mentor, and test-engineering names (lines 83-120), and permits `hmac-sha256`
  or `external-signer` signature values (lines 174-182). No secret value was
  read. These requirements are incompatible with crediting the full envelope
  as an OpenCode-native integration.
- **Network and credential surface, inspected and excluded.**
  `factory-plugin/scripts/provider-smoke.py`, lines 181-215 and 309-341,
  reads a provider key from an environment variable when `--live` is used,
  adds it as an HTTP authorization header, and performs `urlopen` requests.
  This script and all `--live` provider behavior are forbidden from the
  proposed trial. Other Factory scripts contain subprocess, git/worktree,
  delete, and HTTP-bound paths, including `run-plan-cycle.py` and
  `run-supervised-envelope.py`, as identified by source search; they are also
  excluded.

### Manifest, lifecycle, hooks, and OpenCode boundary

- The local marketplace registry at `.agents/plugins/marketplace.json`, lines
  6-102, offers Forge and Factory as local plugin paths with
  `installation: "AVAILABLE"` and `authentication: "ON_INSTALL"`. This is a
  registry declaration, not an installation result or safe lifecycle proof.
- The searched Forge/Factory package roots contained no top-level package
  manifest or lockfile matching `package.json`, `pyproject.toml`,
  `requirements*.txt`, lockfiles, `plugin.json`, or `manifest.json`; only
  Forge's web package and example-project manifests matched. This is a bounded
  filename inspection, not a proof that no installer, hook, or dependency path
  exists elsewhere in the comparison tree. No install lifecycle or hook was
  executed.
- The clone POC is explicitly non-production and requires copying or symlinking
  skill trees before OpenCode use (`opencode.jsonc`, lines 1-19). It defines a
  local-vLLM provider, interpolates `VLLM_API_KEY`, and names a localhost HTTP
  endpoint (lines 21-43). No copied/symlinked files, configuration, provider,
  plugin, hook, or host registration/load trace was created or run.
- The baseline contract remains: Beads owns task/dependency state, Git owns
  source, and candidate records are only run-local evidence
  ([trial protocol](workflow-comparison-candidates-and-trial-protocol.md),
  lines 40-43). OpenCode compatibility is **inconclusive**. Static source
  supports a manually invoked isolated CLI experiment only after approval; it
  does not support a host-loaded Forge/Factory plugin, Claude-oriented
  integration, hook, dispatch, resume, or credential/provider equivalence.

## Required static safety preflight, unresolved

The following checks remain unrun. They must be performed from the present source tree only, without installing dependencies, invoking package scripts, loading extensions, or contacting a network service.

| Area | Required evidence | Status |
| --- | --- | --- |
| Manifests and install behavior | Bounded root filename and local-registry inspection | Partial: no top-level Forge/Factory package manifest found by inspected names; registry says installation/authentication are available; no lifecycle behavior observed |
| Hooks and automatic loading | POC and registry source | Partial: POC requires manual copy/symlink; no Forge/Factory OpenCode hook or registration source was inspected; loading unknown |
| Subprocess behavior | Focused source inspection | Partial: Factory dry-run invokes a validator; Forge A2A and other Factory scripts have broader subprocess paths, excluded from proposal |
| Filesystem behavior | Focused source inspection | Partial: Forge graph and Factory reports write within supplied roots; broader paths remain excluded and unexecuted |
| Network behavior | Focused source inspection | Partial: Factory provider smoke can issue authenticated HTTP; Forge A2A has URL/telemetry/provider paths; all excluded |
| Credential exposure | Focused source inspection | Partial: POC and provider smoke reference environment keys/signatures; no values read; retention/redaction behavior remains unknown |
| OpenCode compatibility | POC plus existing baseline host review | Inconclusive: no supported Forge/Factory host adapter or authorized registration/load trace |

Static inspection can identify observable source-level risks and compatibility claims. It cannot prove that execution is safe, that all behavior is reachable from reviewed source, or that runtime behavior is compatible. The rubric separately requires an authorized host registration/load trace for OpenCode feasibility.

## Trial matrix, explicitly unrun

| Trial requirement | Status | Blocking approval/input |
| --- | --- | --- |
| Small behavior change with focused automated check | Unrun | User-approved task, repeat count, model allocation, time/cost budget, resources, commands, permissions, independent protocol and acceptance reviewers, and preregistered acceptance/metric thresholds |
| Cross-file defect or requirement change with regression check | Unrun | Same approvals and frozen common conditions |
| Predeclared safe failure or blocked-path check | Unrun | Same approvals, plus approved fixture, recovery boundary, and independent expected-outcome check |
| Any OpenCode load/registration trace | Unrun | Explicit authorization, versioned configuration, isolated boundary, and required-source compatibility review |

No outcomes, artifacts, interventions, timing, cost, variance, pass/fail results, or OpenCode equivalence claims exist because no trial ran.

## Outstanding approvals and inputs

1. Perform the source-only safety and compatibility inspection of the present source tree before any execution.
2. Approve the concrete representative tasks and repeat count.
3. Approve resource and cost budgets, model allocation, allowed commands, permissions, and isolated workspace/OpenCode configuration boundaries.
4. Preregister independent protocol and acceptance reviewers, acceptance checks, metrics, numerical thresholds, non-inferiority margins, and evidence/sample minima before any trial.
5. Approve the safe failure/blocked-path fixture and recovery boundary.
6. Explicitly authorize any versioned OpenCode registration/load trace only after the source compatibility review is complete.
