# [ARRAY-CAPTURE] body (filed 2026-11-09)

Frank 2026-11-09: "Unscheduled item: array capture for (X){M, N} perhaps using special syntax. Cap N become N capture groups. No unbounded".

**The idea.** A bounded counted repeat of a capturing group, `(X){m,n}`, can report EVERY iteration's span, not only the last one's (PCRE2 keeps the last). Because pcrec compiles ahead of time and n is bounded, each iteration gets its own fixed slot: n slots, no allocation, no runtime growth. Unbounded repeats (`*`, `+`, `{m,}`) are excluded.

**Constraints already known (recorded, not decided):**
- Opt-in by special syntax only: PCRE2's default (last iteration wins) stays the default (D26: what a pattern reports follows PCRE2). The syntax is new (PCRE2 has none; .NET's CaptureCollection is the nearest precedent).
- Group numbering: the array must not renumber the pattern's other groups (callers and backreferences read today's numbers); an array is one group with n entries, read through its own accessor, not n new group numbers.
- Unset entries for iterations that did not happen (count < n) need a stated "unset" value and a count.
- Backtracking: an iteration given back un-sets its entry; the VM's capture save/restore covers it, the DFA route reports captures only through the VM path today.
- Nested arrays (`((X){2}){3}`), backreferences to an array, and `{0}` are design questions for its design pass.

**Trigger (D77):** a caller asking for it, or a corpus/bench pattern family that today re-runs a match per iteration to recover each one; until then UNSCHEDULED. Related: [POSTFACT] (the per-match callbacks and the `(?<0>...)` group ideas, same caller-facing family).
