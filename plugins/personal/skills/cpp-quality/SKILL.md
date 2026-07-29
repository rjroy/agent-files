---
name: cpp-quality
description: C++ quality standards and idioms. Use when writing, reviewing, or modifying C++ code (.cpp/.h/.hpp/.cc/.hh files), designing C++ types or classes, choosing error handling strategy, or making decisions about ownership, move semantics, const correctness, or modern C++ idioms. Triggers on any C++ work in this user's projects.
---

# C++ Quality

## Resource Management

**RAII is non-negotiable.** Resources (memory, handles, locks) are acquired in constructors and released in destructors. If you're calling `delete`, `free`, `CloseHandle`, or `unlock` manually, something is wrong.

**Smart pointers:**
- `std::unique_ptr` is the default for ownership
- `std::shared_ptr` only when ownership is genuinely shared (rare)
- Raw pointers mean "non-owning observer" and nothing else
- If a function takes a raw pointer, it must not store or delete it

**The Rule of Zero:** Classes should not define destructors, copy/move constructors, or copy/move assignment unless they directly manage a resource. Prefer composition with RAII types over manual resource management.

**Avoid raw `new` and `delete`.** Use `std::make_unique`, `std::make_shared`, or containers. If you must use `new`, it should be wrapped in a smart pointer on the same line.

## Const Correctness

Mark everything `const` that can be `const`. This is not pedantry; it's documentation that the compiler enforces.

- Member functions that don't modify state are `const`
- Parameters passed by reference that aren't modified are `const&`
- Local variables that don't change are `const`
- Pointers to data you don't modify are `const T*`

When you see non-const where const would work, treat it as a code smell.

## Value Semantics and Move

**Prefer value semantics.** Pass and return by value when the type is cheap to copy or move. Let the compiler optimize.

**Move semantics:**
- Implement move constructor and move assignment for types that own resources
- After a move, the source object must be in a valid (if unspecified) state
- Use `std::move` only when you're done with a value
- Don't `std::move` from const objects (it silently copies)

## Error Handling

Pick one strategy per project and stick to it:

- **Exceptions:** Use for truly exceptional conditions. Never use for control flow. If a function can throw, document it. If performance is critical, measure before assuming exceptions are the bottleneck.
- **Error codes/std::expected:** Use when failure is routine or exceptions are prohibited. Always check return values (use `[[nodiscard]]`).
- **Assertions:** Use for invariants that should never be violated. `assert` is for programmer errors, not runtime conditions.

Never mix strategies inconsistently within a codebase.

## Initialization

**Use braced initialization `{}` for data, parentheses `()` for construction.** This avoids the most-vexing-parse and signals intent.

**Initialize all members.** Uninitialized variables are undefined behavior waiting to happen. Use in-class member initializers as defaults.

## Lifetime and References

**Never return references or pointers to locals.** The compiler sometimes catches this; don't rely on it.

**Dangling references kill.** When storing references or pointers, ensure the referenced object outlives the reference. When in doubt, copy or use smart pointers.

## Headers and Includes

- Include what you use; don't rely on transitive includes
- Forward declare when you can (pointers and references don't need full definitions)
- Keep headers minimal; implementation details go in source files
- Use include guards or `#pragma once`

## Naming

- Types: `PascalCase`
- Functions and variables: `camelCase` or `snake_case` (pick one, be consistent)
- Constants and enum values: `SCREAMING_SNAKE_CASE` or `kPascalCase`
- Member variables: prefix or suffix to distinguish from locals (`m_member`, `member_`)
- Macros: `SCREAMING_SNAKE_CASE` (and avoid macros when possible)

## Modern C++ Idioms

**Prefer algorithms over raw loops.** `std::find`, `std::transform`, `std::accumulate` express intent better than `for` loops and are harder to get wrong.

**Use `auto` judiciously.** Good when the type is obvious or verbose. Bad when it hides important information.

**Use `nullptr`, not `NULL` or `0`.** Type safety matters.

**Use `enum class`, not `enum`.** Scoped enums don't pollute namespaces and don't implicitly convert to int.

**Use `override` and `final`.** The compiler will catch mistakes in virtual function signatures.

**Use `constexpr`, not `#define`** for constants.

**Prefer `std::vector` or `std::array` over C-style arrays** in C++ code.

## Performance Awareness

- Pass large objects by `const&`, not by value (unless you need a copy)
- Reserve container capacity when size is known
- Avoid unnecessary allocations in hot paths
- Measure before optimizing; intuition about C++ performance is often wrong
- Understand when copies happen (assignment, pass-by-value, return)

## C-Style Interop

C-style casts, `malloc`/`free`, and raw arrays are acceptable when interfacing with C APIs. In pure C++ code, use `static_cast`/`dynamic_cast`/`const_cast`/`reinterpret_cast`, `std::make_unique`/`std::make_shared`, and `std::vector`/`std::array` instead. Don't mix the two styles within a single module.

Don't ignore compiler warnings; they're often errors waiting to surface.
