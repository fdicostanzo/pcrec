# loglines_stack_frame (`\bat (?:ident\.){2,}ident\((...java:N|Native Method|Unknown Source)\)`, DFA find-all) — rvA01

Scratch verdicts: NONE timed (no timing allowed that night). All leads are
identity-verified (plain + ASan/UBSan) and "scratch timing owed"; effects are
ordered from work counts taken with an instrumented scratch copy (wrap
`memchr` with a counter macro, count DFA steps by editing the step lines; a
10-minute job that tells you where the cell's time goes before reading asm).

## First: find which subject group sets the cell number

The cell is a MEDIAN over twelve subjects in three groups of four. Here
`syslog` has no `)` and is dismissed by one memchr; `fail` and `hit` are the
rest; the median (positions 6-7) lands in the cheaper of those two groups
(`fail`). So the only thing that moves the cell is the fail path — and on fail
this artifact runs NO DFA at all: its whole cost is the required-run
prefilter. Count before you optimize a per-byte loop.

## Waste patterns and how to spot them

1. **Prefilter keyed on a common byte while a much rarer required byte
   exists.** Spot: `rx_reqrun` (or any `memchr(subject + pos, C, ...)` loop at
   the top of `_search`) with C = first byte of the required literal; then
   count every byte the pattern REQUIRES (literal bytes anywhere, single-byte
   delimiters like `(` `)` `"` `=`). Here `'a'` is 3.2% of bytes and `(` 0.36%.
   The usable rare byte is one whose distance back to the start is recoverable:
   a delimiter preceded by a class run that cannot contain it, preceded by the
   literal. Twin: memchr the rare byte, walk back over the run with a 256-byte
   table, test the literal, then call the artifact's own anchored entry
   (`<p>_match`) at the candidate; on failure continue after the rare byte.
   (L1; 33,377 -> 3,820 memchr calls per MiB on fail.)
2. **memchr on the literal's first byte instead of its rarest.** Spot: same
   loop; compare byte counts of each literal byte on the subjects. Here `'t'`
   beats `'a'` by 17%. Cheap twin (memchr at offset 1, test the neighbours).
   Also spot the redundant check: the found byte is re-tested by an overlapping
   16-bit compare. (L2.)
3. **A reverse DFA pass recovering a start the required literal already
   pins.** Spot: `reverse_state`/`rewind_position` loop after the forward
   accept. Ask: can the literal occur inside a match anywhere but at its start?
   If not, the start is the last literal occurrence before the end. (L3, hit
   only.)
4. **The handoff is re-skipped.** Spot: `handoff_position` seeds the loop with
   state 0 and no accept, and the loop's first act is the skip call, which
   re-finds the handoff (count: one prefilter call per `_search` call). (L4,
   tiny.)

## Identity pitfalls met

- **The class run includes bytes `\w` does not** (`$`, `.`): the backward run
  set and the `\b` test are different sets. Dropping `$` from the run set FAILS
  identity (the battery reaches `$` on its own).
- **A match starting exactly at `search_from`.** The candidate test must be
  `k >= search_from + 3`, not `>`; the off-by-one FAILS identity (find-all over
  back-to-back matches catches it).
- **Literal without its delimiter.** Searching back for `"at"` instead of
  `"at "` FAILS: identifiers in the run (`data`, `format`) contain "at".
- Never read below `search_from` in the backward walk; the `\b` lookbehind is
  the anchored entry's seed's job (it reads `s[pos-1]`, which is allowed).
- Argue linearity for any "anchor on byte X, attempt per X" twin: here backward
  runs stop at the previous `(` and an anchored attempt dies by the next `(`.

## Abandoned / rejected

- Tightening the per-byte DFA loops (accept-table load per byte, re-materialized
  `@PAGEOFF` add in the loop): latency-bound on the state -> `ldrh` chain
  (~6 cycles/byte); the extra instructions are off the chain. And on the
  median's subjects the loops never run.
- Two-byte-stride tables: ~90 KB for 58 states x 28^2 classes.
- Dropping the per-call `memchr(')')` presence check: it is what dismisses the
  syslog group; under L1 the `(` memchr would just take its place. Agrees with
  rvA07a's "restart cost per find-all match is negligible".
- Scalar Horspool over a 3-byte literal: ~3-byte shifts, worse than memchr.
- The in-loop `rx_ofsskip` is weaker than the entry prefilter ("at" vs "at ")
  and runs only in state 0 (in-word state 28 walks byte by byte): real, but
  cold whenever every literal occurrence is a match (as on these subjects).
  Look for it on a subject where the literal occurs without matches.
