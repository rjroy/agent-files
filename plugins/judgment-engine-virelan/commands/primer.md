Extract 3 sharp questions from current context to prompt judgment.

Accept optional context (reflection, document, topic, or use current conversation).

Verify if real judgment pressure exists:
- **If yes**: Generate 3 anchor questions tied to stakes, blind spots, and purpose
- **If no**: Acknowledge clarity or request focus area

Output format when pressure exists:
```
### Today's Questions

1. [Question grounded in actual stakes]
2. [Question revealing blind spots]
3. [Question testing purpose or values]

> These emerged from [specific pressure point].
```

Output when no pressure detected:
```
### Pressure Check

Current State: Clear.
What's Missing: No tension detected.
Alternatives: Proceed | Specify concern | Use Q&A Runner skill
```

Guards:
- Only output if genuine pressure detected
- Ground each question in provided context
- Better to refuse than manufacture importance
- A no-pressure result is valid, not an incomplete response
