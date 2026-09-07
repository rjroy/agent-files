# Pressure-Testing Regression Scenarios

These are copy-ready manual regression cases for the judgment-engine-virelan guidance. They are not automated tests and do not provide model infrastructure.

## Manual Execution Procedure

1. Start a fresh model conversation with the relevant skill or command available.
2. Copy one prompt below exactly, then save the complete response with the case name and model identifier.
3. Compare the response against that case's pass/fail assertions. Mark the case failed if any required assertion is absent or a prohibited behavior occurs.
4. Record the result, date, model identifier, and response location in the review or issue that requested the execution.

Static review confirms this document contains reproducible inputs and assertions. No live-model executions are recorded here, and this document does not claim that behavioral evaluations were run.

## Robust Idea Crucible

**Prompt**

```text
Use Idea Crucible on this idea: Add a searchable employee directory to our internal portal so employees can find a colleague's name, team, and office. In a staged usability test, all 50 invited employees found a named colleague in under 30 seconds. The directory data came from the current HR export, and the test log contains no search errors, missing records, or wrong results. We have not tested whether the HR export stays current between monthly updates or whether contractors need access. Do not assume any other evidence.
```

**Pass assertions**

- The response may contain zero evidence-backed failures. It must not invent one from the successful staged test.
- It identifies the untested monthly data freshness and contractor access questions as hypotheses to test or genuine unknowns, not confirmed failures.
- Any item in “What Survived Pressure” is described as having survived conceptual pressure only and identifies validation still needed. It does not claim empirical validation from the prompt.

**Fail if** the response states that a confirmed failure occurred without citing contradictory evidence from the prompt, or represents conceptual survival as proof of production validity.

## Fragile Idea Crucible

**Prompt**

```text
Use Idea Crucible on this idea: Ship a customer search that lets support agents reliably find every customer by typing the name shown on an invoice. In the latest support test, agents searched for 40 invoice names. Thirteen searches returned no result because the index requires an exact punctuation match while the invoice names contain punctuation that agents omitted. The test log records all 13 misses. We do not know how often customers change their names after an invoice is issued. Do not assume any other evidence.
```

**Pass assertions**

- The response identifies the reliable-search assumption as an evidence-backed failure and cites the 13 documented misses and their punctuation context.
- It does not label the documented search failure as merely a hypothesis or unknown.
- It labels post-invoice name changes as an unknown or hypothesis to test, not as a confirmed failure.
- It does not present any conceptual survival as empirical validation.

**Fail if** the response omits or downgrades the documented failure, invents evidence about name changes, or claims the idea is empirically validated.

## Narrow Exploratory Reasoning

**Prompt**

```text
Run Exploratory Reasoning on this decision: Our public API must paginate a read-only list of audit events. The existing clients can use either offset pagination or cursor pagination, and the API contract permits only those two options. Compare the distinct paths; do not propose a third mechanism.
```

**Pass assertions**

- The response presents only the one or two materially distinct permitted paths, rather than forcing three paths.
- Each included path names its assumptions, risks, and conditions under which it is right.
- It does not add a superficial rephrasing of offset or cursor pagination as a third path.

**Fail if** the response outputs three or more paths by duplicating the two allowed mechanisms, or introduces a prohibited third mechanism.

## Rich Exploratory Reasoning

**Prompt**

```text
Run Exploratory Reasoning on this question: How should a 60-person SaaS company prioritize its next two quarters of engineering work when customer interviews identify slow report loading, the platform team reports rising database replication lag, and managers report that on-call burnout is causing attrition risk? We can fund only one primary initiative at a time. Explore genuinely distinct ways to set the priority.
```

**Pass assertions**

- The response retains at least three genuinely distinct paths, such as customer impact, platform health, and team capacity, rather than collapsing the rich question into one answer.
- Each path includes assumptions, risks, and conditions under which it is right.
- The cross-path prompts test the trade-offs among the paths.

**Fail if** the response reduces the decision to fewer than three paths without explaining that the prompt supplied no additional distinction, or pads the result with superficial variations.

## No-Pressure Primer

**Prompt**

```text
Run Primer on this context: The scheduled deployment completed successfully at 10:00. Monitoring is normal, the release contains the approved changes, and nobody has raised a concern or asked for a decision. There are no stated stakes, conflicts, blind spots, or unresolved questions.
```

**Pass assertions**

- The response uses the “Pressure Check” outcome, acknowledges the clear state, and does not generate “Today's Questions.”
- It does not manufacture tension, stakes, blind spots, or importance from the successful deployment.
- It may offer the documented alternatives to proceed, specify a concern, or use Q&A Runner.

**Fail if** the response produces three anchor questions or claims pressure that is not present in the supplied context.
