## SENIOR DEV OVERRIDE

Good architecture balances three things in tension: the solution must actually answer the problem, not a fast approximation of it; it must be maintainable, which is what simplicity is *for* - not simplicity as an end in itself; and it must not foreclose the directions the system will obviously need to grow in, since almost nothing stays a one-shot. Weigh these like a senior engineer would, not by rule.

## SUB-AGENT SWARMING

For large tasks spanning many independent files, weigh dispatching parallel sub-agents against sequential work: each agent starts cold and re-derives context, so parallelism pays off when the files are genuinely independent and numerous enough to outweigh that cost.

## LOGGING

"Add logging" does not mean wrapping one call in a try/catch with a single log line on failure. That only covers the case where something fails cleanly or succeeds silently — real systems do neither. Log state changes: what changed, what triggered it, and enough of the surrounding state to reconstruct the sequence of events afterward. If the code is a service boundary (API call, DB write, queue publish/consume, external process, cache invalidation), log the attempt and the outcome, not just the exception. Use judgment on density — a per-request or per-service-call granularity is usually right; a per-frame or per-loop-iteration granularity is usually noise. When in doubt, log at the seams: the points where control or data crosses from one component/service/process into another.

## NEVER

- Edit files in `~/Applications/`. These are the running services. 
- Use `sudo` (An agennt will never be allowed to run it)
- Skip test writting ("add them later" is not acceptable)
- Propose changes to code you haven't read
- Declare work complete without verification
- Make up data ("I don't know" is many times the right answer)
