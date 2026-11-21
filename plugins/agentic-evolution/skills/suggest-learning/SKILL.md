---
name: suggest-learning
description: Capture a possible reusable skill improvement from an observed task without interrupting the work.
---

# Suggest learning

Record a concise candidate when an actual observation suggests a reusable new
skill or an improvement to an existing one. This is a lead for later review,
not a rule, instruction, or proof. Continue the current task without asking
questions, proposing a follow-up, or starting a review. If there is no
meaningful observation, do nothing.

## Locate the inbox

Resolve this skill's loader-provided directory to its real path, then find its
ancestor `plugins/agentic-evolution`. Use that directory's `.inbox/` as the
single inbox, not the current project or working directory. If the loader does
not supply a resolvable skill directory, or the ancestor is not identifiable,
skip capture rather than guessing or creating another inbox.

## Capture

Write one small Markdown note containing:

- Observation and proposed learning, clearly distinguished from each other.
- Concrete evidence: a short, sanitized description and a source reference
  such as a file and relevant location, or a description of the observed
  interaction. Mark inference or missing evidence explicitly.
- Source scope: project identity and root if applicable, otherwise global or
  unknown; identify the relevant skill and its source path if known.
- Date and, if useful, why the candidate might apply beyond this one task.

Do not copy secrets, credentials, private user content, sensitive output, or
unnecessary excerpts into the note. Omit a reference too if its path or identity
is sensitive. Never weaken this boundary to make a note more useful.

Create the gitignored inbox if needed with owner-only permissions. Before
using it, require a real directory owned by the current user, with no group or
other permissions; reject a symlink or an existing directory that fails these
checks. Apply the same checks to the staging directory, creating it owner-only
if needed. Do not follow symlinks or repair unsafe existing paths. If these
conditions cannot be maintained through publication, skip capture.

For concurrent writers, create a uniquely named owner-only regular
temporary file in the staging directory, write the whole
note, then publish it atomically under a unique `.md` name without overwriting
an existing note. For example, an exclusive temporary file followed by a hard
link to a unique destination gives atomic, no-replace publication on the same
filesystem; retry on a name collision and remove the temporary file afterward.
Never append to or rewrite a shared file. Reviewers should ignore staging files.
If safe creation or publication fails, skip capture and continue the task; do
not fall back to an unsafe location or interrupt the user. Do not modify skills,
delete notes, or trigger review.
