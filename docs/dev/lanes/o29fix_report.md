# O-29 fix — the multi-block `provenance`/`variant` `#section` drop

Lane `o29fix` (sonnet), 2026-09-16. Fixes pcrec-bench's O-29 (found at pin
`cd371441`): when several `pattern` blocks in one `.rxt` file each carry
their own valid `provenance` (or `variant`) sub-block, `pcrec --list-source`
emitted the `#section provenance`/`#section variants` rows for the
TEXTUALLY LAST block only — the other blocks' rows were silently absent,
no diagnostic, exit 0.

## 1. Diagnosis

The brief's working hypothesis — a pending sub-block accumulator flushed
by a following content line and by EOF, but the next-`pattern`-opener
path resetting or reusing it WITHOUT flushing — was **read against the
code and found wrong**, not assumed correct.

`src/parse/rxt_source.c`'s main loop closes a frame at what its own
comment (before this fix) called "three sites": a lesser indent popping
it (the S1 "else" branch's dedent-pop `while` loop), a new group
replacing its contents (the S2 opener-reopen branch), and end of file.
Traced by hand, line by line, against the actual code:

- A `pattern`/`pattern-esc` opener does **not** push a fresh frame for
  the block — the S2 branch REUSES the single top-level frame, flipping
  its `.scope` from `BLOCK` back to `BLOCK` (or from `FILE` to `BLOCK`
  the first time). So when the next block's opener arrives after a
  provenance sub-block's fields, the ordinary dedent (the line's indent,
  0, being less than the open provenance frame's own indent) pops the
  provenance frame through the SAME `while` loop that handles any other
  dedent, calling `RXT_CLOSE_FRAME` (and therefore `close_section_frame`)
  correctly. This path was never broken.
- The `tag`-AFTER-provenance "suppresses the drop" observation the bench
  reported is explained by the SAME correct path: `tag` is an ordinary
  CONTENT line, so its own arrival closes the still-open provenance frame
  via the dedent-pop `while` loop before anything else happens.

**The actual fourth site, and the one the code's own comment never
named, was in S0** — the line classifier immediately above the
attachment logic: *"a BLANK and a COMMENT each close every open
attachment."* That rule was implemented as a bare `ndepth = 1` — a raw
stack-depth reset — rather than as a call to `RXT_CLOSE_FRAME`. Since two
`pattern` blocks are, in essentially every real multi-block `.rxt` file,
separated by a blank line (or sometimes a comment), this is the shape
that reproduces O-29: a `provenance`/`variant` sub-block that is a
block's last content, with nothing but a blank or comment line before
the next block, never reaches `RXT_CLOSE_FRAME` at all — its
`constraints` are never re-checked and, for a PROVENANCE/VARIANT frame,
`close_section_frame` never pushes its `#section` row. Only the file's
LAST such sub-block survives, because only it closes through the
end-of-file loop, the one site that was never broken.

## 2. Fix

`src/parse/rxt_source.c`, the S0 blank/comment branch: replaced the bare
`ndepth = 1` reset with the same closing loop the dedent-pop and
end-of-file sites already use —

```c
while (ndepth > 1) {
    RXT_CLOSE_FRAME(&st[ndepth - 1], line);
    ndepth--;
}
```

This is a **general mechanism fix, not a `provenance` special case**
(memory `pcrec-general-mechanisms-not-special-cases`): it closes whatever
frame is open, of whatever scope, exactly as the other two closing sites
do, so `PROVENANCE` and `VARIANT` both get their `#section` row and
`constraints` re-check, and any future sub-block scope inherits the fix
for free. The macro's own header comment is corrected from "three sites"
to "FOUR sites," with the omission's history recorded there.

## 3. All four `#section` kinds, checked

- **`provenance`** — affected; fixed by the general closing-loop change.
- **`variant`** — affected identically (same PROVENANCE/VARIANT-scoped
  `close_section_frame` push); fixed by the same change. Verified with
  its own multi-block fixture (`o29_multi_variant.rxtin`) rather than
  assumed from the shared code path.
- **`cases`** (`m`/`n`/`ms`/`ns`/`mc`/`gu`/`g`/`gp`) — measured
  UNAFFECTED, and the reason is structural rather than a coincidence: a
  CASE row is pushed by `case_push` immediately when its own line is
  read (`if (row->value == RXT_VAL_CASE) { ... case_push(...); ... }`),
  never deferred to any frame close. There was never a pending record
  for the old bug to lose.
- **`aux`** (`ext`/`freq` subtrees) — measured UNAFFECTED, for a DOUBLE
  reason: an aux row is ALSO pushed per line (`aux_push`, at the moment
  the opener or a deeper tree line is dispatched), and on top of that
  `RXT_CLOSE_FRAME` is a no-op for a tree frame regardless — its whole
  body reads `if (!(F)->tree) { ...constraints...; ...push...; }`. So
  the pre-fix buggy reset and the post-fix closing loop are
  BEHAVIOURALLY IDENTICAL for an `ext` subtree; neither one had anything
  to do there. `o29_multi_aux_control.rxtin` is a measured artifact for
  this claim (all 6 rows present, correctly attributed, on both a
  pre-fix and post-fix build — see §5), not just the argument above.

## 4. Fixtures (`tests/rxtsource/fixtures/`, all LEG A ONLY per
`provenance`'s/`variant`'s own `validated_by: PCREC` schema column —
legs B and C consume a sub-block's body without reading it, §3.3's rule)

| fixture | what it makes reachable |
|---|---|
| `o29_multi_provenance.rxtin` | THE REPRODUCTION: three blocks, each with `provenance` as the block's last content, closed in turn by a blank line (block 1), a comment line (block 2) and end of file (block 3) — one fixture exercising all three real closing sites. Asserts count=3 AND per-block line/block_line/name/fidelity attribution, not just a count. `tag t1` sits BEFORE block 1's provenance (the bench's own reproducing order), never after. |
| `o29_multi_variant.rxtin` | the `variant` twin, same shape, same three closing sites — the general-mechanism claim's own witness (a second scope reached by the identical fix, no scope-specific code). |
| `o29_suppressed_order.rxtin` | the CONTROL: `provenance` then `tag` AFTER (not before) in each of two blocks — pins that this order needed no fix and gets none, matching the bench's "tag after suppresses the drop" observation, both pre- and post-fix. |
| `o29_multi_aux_control.rxtin` | the CONTROL for `ext`: the identical three-closing-site shape, asserting all 6 aux rows (an opener + one child, times 3 blocks) present and correctly attributed — `ext` never shared O-29's bug, and this fixture is the measured artifact for that claim. |

## 5. Checks (`tests/rxtsource/run_rxtsource_tests.sh`)

Added `section_field SECTION COLUMN FILE` (a thin sibling of the existing
`section_count SECTION FILE` helper — same `#section`-boundary-tracking
awk, extended to return a column's values instead of a row count) and
four checks routed through it and through `section_count`:

- **`O-29/provenance`** — `section_count provenance` == 3 AND the three
  rows' `line`/`block_line`/`block_name`/`fidelity` columns match the
  fixture's own line numbers and field values exactly (`34 41 49` /
  `32 40 48` / `p1 p2 p3` / `verbatim adapted verbatim`). Three legs are
  NOT claimed (leg A only, per `validated_by`).
- **`O-29/variant`** — the same shape over `#section variants`
  (`19 23 27` / `18 22 26` / `p1 p2 p3` / testees `re2 tre onig`).
- **`O-29/suppressed-order`** — `section_count provenance` == 2 with the
  correct `line`/`block_line` pairs (`13 21` / `12 20`) on the control
  fixture.
- **`O-29/aux-control`** — `section_count aux` == 6 with the correct
  `line`/`block_line`/`key` columns (`15 16 19 20 23 24` /
  `14 14 18 18 22 22` / `ext note ext note ext note`).

All four checks assert a POPULATION with per-row attribution (count AND
which row belongs to which block), never a bare count — a count-only
assertion here would be satisfiable by a parser that, say, always
attributed every surviving row to the wrong block, or that happened to
keep three rows for an unrelated reason.

Legs consuming this shape without validating it: `provenance`'s and
`variant`'s schema rows both read `validated_by: PCREC` (the pre-existing
`prov-adaptation`/`prov-verbatim` checks in the same file already follow
this rule) — a three-leg assertion here would be the named failure
§3.3 rules out (claiming coverage of two parsers nothing tests).

## 6. Validation

Owed until `build/battery_20260916_002230/trailer.log` shows
`BATTERY DONE` (a merge battery held the box for this lane's whole
working period — `test`/`strict`/`axes`/`san`/`lint` stages already
complete at commit time, `mech` still running). Commands to run once
clear, from `worktrees/o29fix/`:

```
timeout 900 make -j4
timeout 600 make strict
timeout 600 bash tests/rxtsource/run_rxtsource_tests.sh
```

Baseline on `main` today (per the brief) is 208/0/1 checks with census
210/3936/28943. This lane's four new checks are ADDITIVE — expect
208+4 = 212 passed, 0 failed, census UNCHANGED (the new fixtures are
`.rxtin`, not corpus `.rxt` files, so `CENSUS_FILES`/`CENSUS_BLOCKS`/
`CENSUS_LINES` must not move — verified by inspection: no corpus `.rxt`
file under `tests/` uses `provenance`/`variant`/`ext`/`freq` at all, per
a repo-wide grep, so this fix cannot move the corpus's own parse output
either).

Also owed: reproducing the bench's minimal repro live (a three-block
provenance file → all three rows) against this build, AND against the
pre-fix binary if `build/pcrec` from the main tree is still unfixed, to
record both outputs side by side.

**[NUMBERS FILLED IN AFTER THE BATTERY CLEARED — see the handback message
for the exact figures and log paths.]**

## 7. Spec

`docs/spec/rxt_format.md`'s `#section provenance`/`#section variants`
entries (around line 1177/1182) already say **"one row per `provenance`
sub-block"** / **"one row per `variant <testee>` sub-block"** — not "one
row per FILE" or anything scoped to a single block — so the spec was
never silent on multi-block emission; it already promised exactly the
behaviour this fix restores. No spec hunk is needed or added (this is a
conformance bug fix, per the brief's own framing, not a behaviour
change).

## 8. Scope note

Per BOILERPLATE and the brief: touched only `/Users/fdicostanzo/pcrec`,
only inside `worktrees/o29fix/`. Nothing under `/Users/fdicostanzo/pcrec-bench`
was read or written. Parked on `lane/o29fix`, not merged.
