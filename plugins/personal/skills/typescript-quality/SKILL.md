---
name: typescript-quality
description: TypeScript quality standards and type discipline. Use when writing, reviewing, or modifying TypeScript code (.ts/.tsx files), making decisions about type design, choosing between unknown/any, deciding between enums and union types, or debating non-null assertions. Triggers on any TypeScript work in this user's projects.
---

# TypeScript Quality

## `unknown` and `any`

Before using either, ask: is this actually unknowable, or am I avoiding the work of typing it properly? Find the real type.

## Enums

Prefer union types (`type Status = "pending" | "complete"`) or `as const` objects over enums.

## Non-null Assertion (`!`)

Don't use `!` without a comment explaining why the compiler is wrong.
