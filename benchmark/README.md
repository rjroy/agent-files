# Model benchmark

The benchmark runs cases before asking a human to grade responses from 1 to 5.
By default it does not use a model to grade. An optional standalone pass can
add a local decision-model second opinion, but human grades remain the result.
Results, including model identities and the anonymous mapping, are private local
files under `benchmark/results/` by default. Do not inspect those files until
review is complete if you are the grader.

## Offline rehearsal

From the repository root, using Python 3.9 or later:

```sh
python -m benchmark run --demo --output-dir benchmark/results/rehearsal
# Open benchmark/results/rehearsal/review.html and download benchmark-grades.json.
python -m benchmark import-grades /path/to/benchmark-grades.json \
  --output-dir benchmark/results/rehearsal
```

The demo has two fake models and synthetic responses. It does not demonstrate
model quality, tool use, or spend. Fixture checks run in a
bubblewrap sandbox when available, but the demo makes no changes, so coding
checks may fail. Open the generated HTML locally, grade in the browser, then
download and import the complete grades file. Even a deterministic-only run
requires its empty grades export to be imported. The scorecard is revealed only
after import. Import finalizes grades: an identical import may be retried to
restore reports, but changed grades are rejected.

`python -m benchmark resume --output-dir benchmark/results/rehearsal`
regenerates the review from saved state without calling models or rerunning
checks or local grading. Legacy partial grades are prefilled; a completed run
restores its scorecard instead. Resume also restores a saved machine report,
including during review; that report reveals identities. If execution
was interrupted, unrecorded runs are marked missing rather than repeated.
Browser autosave for `file://` pages depends on the browser and local file
policy, so do not rely on it across browsers or devices. Download the grades
file before closing the page. Only one command can use an output directory at a time; a
concurrent command fails rather than reveal an incomplete scorecard.

## Graphs

After importing grades, generate a standalone report with:

```sh
python -m benchmark graphs --output-dir benchmark/results/rehearsal
```

Open `graphs.html` locally to compare human rubric grades as bars on a shared
scale. Missing grades have no bar. If saved local grader results are available,
separate per-case charts show pairwise wins minus losses. Ties and order
disagreements are listed separately; neither counts as a loss. The run and check
matrix also includes cases with no human rubrics.

The command reads saved state without running models or changing the review.
The report reveals model identities and grades, so keep it private. The default
output directory is `benchmark/results/latest`.

## Live runs

Install OpenCode and authenticate your providers as described in
[OPENCODE.md](OPENCODE.md). The benchmark runs through your real OpenCode
setup, using your logins, agents, and configuration as-is. Copy
`benchmark/models.example.json` to a private file, replace
the placeholders with actual provider/model IDs, and agree on a spend limit
before running. The benchmark does not enforce a spend limit; provider billing
and limits remain your responsibility.

`doctor` checks the installed CLI and model catalog without sending a prompt
or running inference. It does not verify that authentication works or that
the account has usable funds.

```sh
python -m benchmark doctor --model provider/model-one --profile talking --json
python -m benchmark doctor --model provider/model-one --profile coding --json
python -m benchmark run --config /path/to/models.json --allow-live \
  --output-dir benchmark/results/comparison
python -m benchmark resume --output-dir benchmark/results/comparison
```

The runner requires both explicit configuration and `--allow-live`. It runs
doctor for every model and applicable profile before execution, and refuses to
proceed if a model is not available in the installed OpenCode. Use a fresh
output directory per run.
To start with only the handoff, put a copy of the `handoff` case directory
in a separate cases directory and pass `--cases-dir /path/to/cases`. Run this
single comparison first and review its cost before expanding the pilot.

During review each case receives a shuffled anonymous order. The page gates
evidence on message-only grades, but evidence is included in the HTML and can be
read by inspecting its source. Responses, prompts, and evidence are redacted for
configured model IDs, but model-generated text could still identify a model
indirectly. Keep the output directory private: state and machine reports expose
identities. Failed checks, check execution errors, and missing model runs are
separate outcomes. Import the downloaded grades to display and save the
scorecard.

## Local second opinion (optional)

Once execution has finished, a local Ollama decision model can compare
responses pairwise, independently of human review. Run this explicit command
whenever desired; run and resume do not invoke it. Its report reveals model
identities, so a human grader should not inspect it before importing grades.
It is supplementary and never replaces the human scorecard.

```sh
python -m benchmark autograde --output-dir benchmark/results/comparison \
  --grader d3:latest
```

`d3` is a zero-shot decision model, not a chat model. It answers questions
about supplied text, so the pass compares each pair in both orders with choices
A (first is better), B (second is better), and C (neither is clearly better).
C in both orders is a tie; inconsistent choices are recorded separately as an
order disagreement. Neither counts as a win. The pass writes
`auto_scorecard.md` and stores
results under `state["auto_grades"]`. Agreement with human grades is separate
from machine rankings and is refreshed on a successful human import without
rerunning inference. Inputs are blinded and response text is clipped to a target
character budget; the report counts truncations. The pass retries with a shorter
budget on context-length errors, but the character target does not guarantee
that input fits the model's token context. The runner checks the installed model
list first and refuses to pull a missing model.

An earlier pilot comparison showed weak rank agreement with human grades (mean
Spearman 0.15, negative on both talking cases). Treat this as a screen or a
sanity check, not a substitute for human judgment. Use `--max-chars` to lower
the input budget and `--ollama-bin` to point at a different Ollama executable.

## Case format

Each `cases/<id>/case.json` is a version 1 JSON object with `id` matching the
directory, `role`, ordered `turns`, and a `rubrics` list. A rubric has a
`label`, a human-facing `prompt`, and a Boolean `evidence`. Put evidence
rubrics after all message-only rubrics. An optional nonblank `decision_prompt`
provides wording for the local decision model. An empty list makes a case
deterministic-only. Optional `fixture` names a directory copied into a fresh
workspace. Optional `check` names a Python script invoked independently as
`python check.py <workspace>`, from outside that workspace. Exit zero means
pass, exit one means fail, and other exit codes, launch errors, or timeout mean
check error. Checks also run on partial work after an adapter error.
Linux bubblewrap and `/usr/bin/python3` are required for checks. The sandbox
has a read-only system runtime, checker and workspace, a private temporary
directory and empty home, a sanitized environment, and no network. It does
not expose the case directory or results. If isolation cannot be established,
the check is recorded as an error rather than run on the host. Keep the output,
cases and workspace outside `/usr`, which is visible read-only in the sandbox.
Roles `coding`, `handoff`, and `orchestrator` receive coding tools; other roles
are conversation-only.
An existing protocol needs no runner changes for a new case.

Run the offline CLI acceptance and checker boundary tests with:

```sh
python -m unittest benchmark.tests.test_cli_rehearsal
python -m unittest benchmark.tests.test_check_boundary
python -m unittest benchmark.tests.test_local_grader
```
