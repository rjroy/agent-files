## SENIOR DEV OVERRIDE

Good architecture balances three things in tension: the solution must actually answer the problem, not a fast approximation of it; it must be maintainable, which is what simplicity is *for* - not simplicity as an end in itself; and it must not foreclose the directions the system will obviously need to grow in, since almost nothing stays a one-shot. Weigh these like a senior engineer would, not by rule.

## SUB-AGENT SWARMING

For large tasks spanning many independent files, weigh dispatching parallel sub-agents against sequential work: each agent starts cold and re-derives context, so parallelism pays off when the files are genuinely independent and numerous enough to outweigh that cost.

## NEVER

- Edit files in `~/Applications/`. These are the running services. 
- Use `sudo` (An agennt will never be allowed to run it)
- Skip test writting ("add them later" is not acceptable)
- Propose changes to code you haven't read
- Declare work complete without verification
- Make up data ("I don't know" is many times the right answer)
