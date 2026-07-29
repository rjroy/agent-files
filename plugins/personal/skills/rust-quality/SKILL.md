---
name: rust-quality
description: Rust quality standards and idioms. Use when writing, reviewing, or modifying Rust code (.rs files), designing Rust types/traits/lifetimes, choosing error handling strategy, deciding on async vs sync, evaluating unsafe usage, or making decisions about ownership, borrowing, mutability, or API surface. Triggers on any Rust work in this user's projects.
---

# Rust Quality

## Ownership and Borrowing

**Ownership is the type system, not a puzzle to solve.** When the compiler fights you, it is usually right. Restructure the data flow; do not paper over it.

- Pass by reference (`&T`) by default. Pass `&mut T` only when the callee must mutate. Pass by value when the callee needs to consume or store.
- Return owned values (`T`) rather than references unless the lifetime is tied to an input and the caller benefits from borrowing.
- Clone when the cost is negligible or when cloning is cheaper than the lifetime gymnastics required to avoid it. Do not clone reflexively to silence the borrow checker.
- `Rc` and `Arc` are not defaults. Reach for them when ownership is genuinely shared across independent lifetimes, not because threading a lifetime through two function signatures felt annoying.

## Lifetimes

**Most lifetimes should be elided.** If you are writing `<'a>` on a function, you are making a claim about how input and output lifetimes relate. Make sure the claim is true. Do not write lifetimes you don't need.

- Prefer owned return types over borrowed ones in public APIs.
- Do not add lifetime parameters to a struct unless the struct genuinely borrows from somewhere else.
- `'static` on a reference means "lives for the duration of the program." On a type bound (`T: 'static`) it means "contains no non-`'static` borrows." Know which you mean.
- If a lifetime name has more than one letter, you are overthinking it.

## Error Handling

Use `Result<T, E>` for failures the caller might handle. Use `Option<T>` for absence. Use `panic!` for bugs — conditions that cannot occur if the program is correct.

- **Library code:** define an enumerable error type with variants that name conditions, not messages.
- **Application code:** a boxed or type-erased error is fine at the outer layer.
- Convert library errors to application errors at a single explicit boundary.

**`?` is the default.** Add context explicitly at the `?` site, not everywhere the error later travels.

- `unwrap()` in production code is a bug waiting to be filed. Allow it only in tests, examples, and `const` contexts.
- `expect("msg")` is acceptable when the message is "this cannot fail because X" and X is a genuine invariant.
- `unreachable!()` and `todo!()` are both panics. `todo!()` must never ship.
- Do not swallow errors with `let _ = ...` without a comment explaining why the failure is safely ignored.

## Pattern Matching

**Exhaustiveness is a feature.** Do not reach for `_ =>` as a catch-all unless you genuinely mean "any future variant should behave like this." A `_` arm silences the compiler when someone adds a variant; that is usually the opposite of what you want.

- `if let` for one branch with a fallback. `let else` for unwrap-or-return control flow.
- `#[non_exhaustive]` on a public enum forces downstream callers to include `_`. Use it only when planning future variants explicitly.

## Types and Traits

**Reach for the weakest abstraction that fits.**

- **Struct** when the fields are a unit. Tuple struct for newtypes. Plain tuple only for local, ad-hoc pairing — never in a public API.
- **Enum** when the type has a fixed set of shapes. If you are writing `if kind == Kind::A { ... } else { ... }`, the branches probably want to be enum variants.
- **Trait** when you need polymorphism across types you do not own. Traits with one implementation are usually a smell.
- **Generics** when dispatch can be resolved at compile time. **`dyn Trait`** when you need runtime heterogeneity.

**Coherence:** implement a foreign trait for a foreign type by wrapping it in a newtype. This is the intended pattern.

## Mutability

**`let` by default, `let mut` when required.** The rule is minimum visible mutability, not no mutability ever.

**Interior mutability is a signal.** Sometimes it is the right answer; often it is a symptom of an ownership design you have not worked out.

- `Cell` and `RefCell` for single-threaded interior mutability. `RefCell` moves borrow checking to runtime — a panic on overlapping borrows is worse than a compile error.
- `Mutex` for threaded sharing. Prefer it over `RwLock` unless reads genuinely dominate.
- Atomics for simple counters and flags, not complex shared state.

## Unsafe

**`unsafe` is a contract, not an escape hatch.** Every `unsafe` block must document the invariants that make it sound. Never use `unsafe` to silence the borrow checker.

- Default to `#![forbid(unsafe_code)]`. Remove it only with a concrete, justified reason.
- FFI, manual memory layout, and performance-critical primitives are valid reasons. "This was easier" is not.
- Put `unsafe` in the smallest possible module, expose a safe API, and write the safety argument adjacent to the unsafe block.

## Async

**Async is a function color.** Non-async callers cannot call `async fn` without a runtime. Introducing `async` commits downstream code paths.

- Do not make functions `async` speculatively. A function with no awaits should not be `async`.
- `.await` points are cancellation points. State held across `.await` must survive being dropped mid-operation.
- A future holding a non-`Send` value across `.await` cannot move between threads; identify what is held and narrow its scope.
- Do not run blocking work on the async runtime. Use `spawn_blocking` or equivalent.

## Iterators and Loops

**Iterator chains are the default for transformations.** `map`, `filter`, `collect`, `fold`, `zip` express intent better than index-threaded loops.

- Prefer `for x in iter` over `while let Some(x) = iter.next()`.
- Fall back to an explicit loop when control flow is non-linear, the body does multiple unrelated things, or borrow-checker gymnastics to satisfy a closure produce worse code than the loop.
- `collect` in the middle of a pipeline is wasted allocation. Iterators compose.

## Collections and Strings

**Defaults:** `Vec<T>` for ordered sequences. `HashMap<K, V>` for keyed lookup. `BTreeMap<K, V>` for ordered iteration or range queries. `VecDeque<T>` for double-ended push/pop.

**At API boundaries:**
- Take `&[T]` instead of `&Vec<T>`. Take `&str` instead of `&String`. Take `&Path` instead of `&PathBuf`. The borrowed view is strictly more flexible.
- `impl Into<String>` to take ownership. `impl AsRef<str>` or `impl AsRef<Path>` to borrow.
- `Cow<'a, str>` when you sometimes need to allocate and sometimes do not. Not as a hedge.

**String discipline:** `&str` for borrowed text. `String` for owned, growable text. Do not use `String` as a poor man's enum.

## Modules and Visibility

**Private by default.** Every `pub` is a commitment. Removing one is a breaking change.

- `pub(crate)` for items that cross module boundaries within a crate. Most "shared helpers" belong here.
- Re-exports (`pub use`) curate a clean public surface without exposing internal module structure.
- Do not co-locate unrelated things because they are each small. Module boundaries are cheap.

## Naming

- Types, traits, enum variants: `PascalCase`.
- Functions, methods, variables, fields, modules: `snake_case`.
- Constants and statics: `SCREAMING_SNAKE_CASE`.
- Lifetimes: short, lowercase, single letter (`'a`).
- Type parameters: single capital letter or short `PascalCase` when the role matters (`T`, `E`, `K`, `V`, `Item`).

`_mut` for mutable getter variants. `try_` for fallible variants. `into_` consumes, `as_` borrows, `to_` clones. Do not mix them up.

## Testing

- Unit tests live in a `#[cfg(test)] mod tests { ... }` block at the bottom of the file they test.
- Integration tests live under `tests/` and exercise only the public API. A test needing private internals belongs inline.
- Doc tests in `///` examples are compiled and run. Use them for public API examples.
- Dependency-inject at seams. If a function needs the clock, filesystem, or a network client, it takes one. Tests pass fakes.
- Module-level mocking frameworks are a code smell. If you need them, the code is not structured for testability.

## Documentation

- `///` for items. `//!` for modules and crates.
- Every `pub` item in a library crate gets a doc comment.
- The first line is a one-sentence summary. Include `# Examples`, `# Errors`, and `# Panics` sections where they apply.
- Doc tests are tests. Fix broken examples; do not disable them.

## Tooling

**`rustfmt` and `clippy` are not optional.** CI fails if either does.

- `cargo fmt --check` in CI. Do not hand-tune whitespace.
- `cargo clippy --all-targets --all-features -- -D warnings` in CI.
- Tune clippy lint levels at the crate or workspace level in `Cargo.toml`, not via scattered `#[allow]` attributes.

## Performance Awareness

- Know where allocations happen: `String::from`, `vec!`, `Box::new`, `collect::<Vec<_>>`, `format!`.
- Iterator chains fuse at compile time. `.map().filter().collect()` is usually one pass.
- Reserve capacity (`Vec::with_capacity`, `String::with_capacity`) when the final size is known.
- Measure before optimizing. Rust performance intuition is better than C++ performance intuition, but still wrong often enough to matter.

## Debug Code

Don't leave `dbg!`, `println!`, or `todo!()` in committed code. Use `tracing` or the project's logging facade.

Write functions, not macros, when a function will do.
