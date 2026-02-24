# AGENTS

This repo prefers minimal, pragmatic implementation style.

## Coding Guidelines

- Keep solutions as simple as possible while still correct.
- Do not add extra abstractions (helper classes, layers, generic frameworks) unless there is clear repeated need.
- Prefer straightforward, explicit flow over clever patterns.
- Inline one-off logic instead of creating reusable helpers when reuse is unlikely.
- Keep comments minimal; add only when they clarify non-obvious behavior.

## Error Handling

- Default to fail-fast behavior.
- Avoid retries, fallback branches, and recovery logic unless explicitly requested.
- Avoid broad exception handling; only catch errors when needed for clear user-facing output.

## Scope Control

- Implement only the requested behavior; avoid unrelated refactors.
- Keep CLI output concise and human/agent readable.
- Preserve existing project conventions unless asked to change them.
