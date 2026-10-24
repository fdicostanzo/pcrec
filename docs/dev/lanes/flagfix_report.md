# flagfix report — [FLAG-SPELL]: a concatenation drops an empty that carries nothing

Lane flagfix (opus), 2026-10-24, branch `lane/flagfix` off main `b260c1f46`.
Brief: drop empty nodes from concatenations at ONE place, so flag spellings
compile alike; checks, re-pins, measurements, then queue `615-flagfix-test`.

## Premise test (main, b260c1f46)

Reproduced as the findings doc says: `--engine=vm` `(?i)abc` vs `(?i:abc)`
differ beyond the pattern text by one `goto rx_L2` label pair
(`RX_VM_PROGRAM_BYTES` 634 vs 577); on the DFA, `a(?i)bc` reads
`RX_REQ_RUN "none"` / `RX_REQ_WHY "dominated"` / `RX_DFA_PREFILTER "memchr"`
where `a(?i:bc)` reads `"614243@1/ffdfdf"` / `"emitted"` / `"handoff"`.

## Where the drop lives, and why there

`src/parse/parse.c` `p_cat`, the one builder of concatenation spines from
pattern text. A new one-line predicate `empty_carries_nothing(a)` is
`a->k == A_EMPTY && !a->reg`; `p_cat` skips such an element after `p_rep`
returned it, and a head that is one is replaced by the next element. A branch
made only of such empties keeps its first one (an empty branch stays empty).

Why the parser and not a post-parse normal-form pass:
- Every producer of a carry-nothing empty inside a concatenation is a parse-time
  producer reached from `p_cat` (a bare option run from `mod_modifiers.c`,
  `(*UTF)`-style options from `mod_ucp.c`, an empty group `(?:)` whose body
  `p_cat` returned as A_EMPTY, a group whose body is one run). One rule at the
  one builder covers all of them; nothing names a construct.
- The quantifier has already bound by then: `p_rep` ran the err-109 check and
  built any `A_REP` before `p_cat` sees the element, so the drop can never
  change what a quantifier applies to (R1). A quantified empty group is an
  `A_REP`, not an `A_EMPTY`, and is never touched.
- A whole-tree pass would have to tell DELIBERATE empties apart: the anchor
  seal `pcrec_wrap_bare_anchor` builds `CAT(anchor, EMPTY)` so a quantifier
  lands on a CAT, and `lower_enc.c`'s `A_CAT(A_EMPTY, alt)` seal ([LOWERENC-SEAL]).
  Both are built outside `p_cat` and keep their empties; a later pass would
  need an exemption per seal, which is the special-case shape the brief forbids.
- Never dropped: anything that is not `A_EMPTY` (captures, calls, verbs,
  assertions, `\K` are their own kinds), and an `A_EMPTY` carrying a registry
  stamp (`reg`, D67: an engine fact and its offset; no producer stamps one
  today, so the guard is the definition of "carries nothing", not a live case).

## What it deletes (simplification)

- `src/parse/ctxnode.c` `lang_charset`'s A_CAT arm: the loop that skipped
  `A_EMPTY` elements so `(?:)a` read as `a` (18 lines) is now
  `case A_CAT: return false;`. A parsed concatenation no longer holds such an
  empty, so a CAT is two or more items that carry something. Lookarounds over
  `(?=(?i)a)`, `(?<=a(?:))` still become context nodes (checked: engine `dfa`
  before and after).
- Not deleted, and why: `src/facts/endwin.c`'s trailing-empty skip
  (`em_tails`) still serves the anchor seal `CAT($, EMPTY)`; `emit_vm.c`'s
  A_EMPTY arm still emits a branch that is only an empty. `src/facts/req.c`'s
  handling of an empty mid-CAT (the cause of the lost run) is no longer reached
  from parsed patterns; it was not traced further (out of scope).

## Checks

- `tests/codegen/run_case_spelling_identity.sh`: the flag group now compares
  `(?i)abc` against `(?i:ABC)` / `(?i:aBc)`, and a new group `flag-mid`
  compares `a(?i)bc` against `a(?i:BC)` / `a(?i:bC)` (the DFA's witness: the
  required run). 35 passed / 0 failed, 26 cells compared. Also fixed the
  per-group failure message, which claimed "every cell was refused" when the
  cells had DIFFERED (a stale second claim, coding §5).
- Sabotage S1560 (`tests/mech/sabotages/S1560_cat_keeps_empty.sh`): the
  predicate returns false (every empty stays). Hand-planted on the branch:
  `run_case_spelling_identity.sh` 28 passed / 7 failed (flag-spelling vm/byte
  and vm/utf8 on `RX_VM_PROGRAM_BYTES 634 vs 577`; flag-mid on all four cells,
  `RX_REQ_RUN "none"` vs `"614243@1/ffdfdf"`). REACH probe evaluated by hand on
  the clean tree: prints `REACH-BARE-RUN-DROPPED`. The matrix row's own run
  is OWED (the box lock was held; see STATE).
- New mech arm `casespell` in `tests/mech/run_sabotage_matrix.sh` (vocabulary
  entry + arm), because no existing arm ran the spelling check (`codegen` runs
  only `run_codegen_tests.sh`).
- Re-aimed S338 (`src/parse/ctxnode.c`): its anchor was in the deleted loop.
  New plant: the CAT arm reads a concatenation as its first element
  (`a = a->l; continue;`), so `(?<=ab)x` becomes `(?<=a)x`; intent unchanged,
  verified by hand: planted build matches "ax" (`match 1 2`), clean answers
  `nomatch`.
- R1 cells: `tests/modifiers/empty_drop.rxt` (+ `empty_drop.gen.py`), 17
  blocks / 49 lines, every expectation produced by libpcre2 10.46
  (`tests/lib/p2gen.py`): `(?i)abc+` vs `(?i:abc)+` on abcc/abcabc (0-4 vs
  0-3 / 0-3 vs 0-6), `a(?:)+b`, `a(?:)*b`, `a(?:){3}b`, `a(?:)b`, `a(?i)bc`,
  `abc(?i)` (run at the end), `(?i)` and `(?i)(?s)` as the whole pattern,
  `(a(?i))b`, `(?i)|x`, `x|(?i)`, `(x|(?i))y` (empty branches stay empty
  branches), and `perr` for `a(?i)+b`, `a(?i)*b`, `(?i)+` (libpcre2 err 109).
  harness: 49 passed / 0 failed on the branch AND on the b260c1f46 build (the
  same accept/refuse and answers before and after).

## Measurements

Emitted VM program bytes (`--engine=vm`, `RX_VM_PROGRAM_BYTES`, ref = b260c1f46):

| pattern | ref | new |
|---|---|---|
| (?i)abc / (?i:abc) | 634 / 577 | 577 / 577 |
| (?s)a.c | 580 | 523 |
| (?x)a b | 450 | 393 |
| (?U)a+b | 870 | 813 |
| (?n)(a)b | 450 | 393 |
| (?s). | 266 | 209 |
| (?-i)abc | 369 | 312 |
| a(?i)bc / a(?i:bc) | 625 / 568 | 568 / 568 |
| a(?:)b | 450 | 393 |
| (?:)abc | 369 | 312 |

Required-run stamp, mid-pattern (DFA, default engine): `a(?i)bc`
`RX_REQ_RUN "none"`, `RX_REQ_WHY "dominated"`, `RX_DFA_PREFILTER "memchr"`
-> `"614243@1/ffdfdf"`, `"emitted"`, `"handoff"` (identical to `a(?i:bc)`).

Corpus sweep (scratch `sweep_flagfix.py`, ref b260c1f46 built from `git
archive` vs the branch, run under `scripts/boxlock`; corpus = emit_sweep's own
enumeration, 6,065 rows / 4,813 distinct patterns, `--features all`):

| cell | same | movers | refused (both) | answer diffs |
|---|---|---|---|---|
| default engine, byte | 4,273 | 108 | 432 | 0 |
| --engine=vm, byte | 4,021 | 361 | 431 | 0 |
| default engine, utf8 | 4,302 | 113 | 398 | 0 |

- 366 distinct patterns change emitted text in some cell; 0 accept/refuse
  differences. Every mover's text contains an empty producer (a bare option
  run, `(?:)`, `(*...)`): a grep for patterns without one returns none.
- Answer identity of every mover cell: both artifacts built with a driver,
  `rx_search` rc and EVERY capture span compared over all strings to length 4
  on an alphabet drawn from the pattern (+ `\n`) and 1,000 seeded random
  strings (about 1,500-8,400 subjects per cell): 581 of 584 mover cells
  identical, 0 different. The 3 untested cells are `^(?i)${v}$` (needs a
  variable context; its answers are the vars corpus's, run by make test).
  Positive control: a ref `a(?i)bc` vs new `a(?i)(b)d` pair DIFFERS through the
  same comparison.
- Bytes over the movers: default/byte 2,384,246 -> 2,383,792 (-454; 96
  smaller, 12 larger); vm/byte 7,210,618 -> 7,191,383 (-19,235; 351 smaller,
  10 larger); default/utf8 -972 (103 smaller, 10 larger). EVERY larger artifact
  gained a required run: 12 per cell went `RX_REQ_RUN "none"` -> a run, 4 got a
  longer run; DFA prefilter moves `memchr` -> `handoff` (2: `a(?i)bc`,
  `x(?i)ab`) and `memchr` -> `run-pinned` (1: `(?<a>x)(?J)(?<a>y)`).

Size manifests / pins: `make test-size`, `test-codegen` (k50, s220, m5 stamp
manifests), `test-vm` (the IR listing baseline), `test-findings` all green
with no re-pin: no pinned witness has a bare run. `docs/dev/artifact_size_log.tsv`
is rewritten by the 615 run's corpus pass (per-pattern drift is its git diff).

Re-pins (each from its own check's output, old -> new), all from the new
corpus file, none from the drop itself:
- `tests/rxtsource/run_rxtsource_tests.sh`: CENSUS 294/6048/74005 ->
  295/6065/74054; RUNSH 270/6048/74005 -> 271/6065/74054; C3_PASS 21957 ->
  21987; C3_SKIP 51962 -> 51981; C3_SKIP_NOPYTHON 2218 -> 2237;
  C3_VERIFIABLE 24189 -> 24238.
- `tests/startset/manifests/manifest_s2_vm_forced.tsv`: +10 rows, every one
  an `empty_drop.rxt` block ([vm-movers] named exactly these; no existing row
  moved).

## abi

Per-pattern code only. The scaffolding did not move: `make test-codegen`
(the identity gates, the abi stamp readers) is green at abi 84 with no edit to
any abi reader; every mover diff is program text and per-pattern stamp values
(`RX_VM_PROGRAM_BYTES`, `RX_REQ_*`, prefilter). No abi bump. No spec hunk:
no contract sentence describes the empty label or a bare run's code.

## Validation run on the branch

`make strict` clean; `make test-codegen`, `test-registry`, `test-rxtsource`,
`test-parse`, `test-reject`, `test-vm`, `test-ucp`, `test-size`,
`test-findings`, `test-definitions`, `test-startset`: all green (verdict grep
empty).

## STATE AT HANDOFF

- Commits on `lane/flagfix` (see `git log b260c1f46..lane/flagfix`).
- Rulings file: R1 (manager, 2026-10-24) applied in full (cells above).
- OWED: queue job `615-flagfix-test` (make test on the branch through
  scripts/perfrun). Log `worktrees/.boxqueue/<done|failed>/*-615-flagfix-test/job.log.make`;
  completion line `sections ran: 77/77`; verdict
  `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'` empty / `scripts/boxqueue state 615-flagfix-test`.
- OWED: the S1560 and S338 matrix rows (`bash tests/mech/run_sabotage_matrix.sh S1560 S338`,
  expected DETECTED by arms `casespell` and `ctxnode`); not queued (the brief
  allowed one job).
- Follow-ups (not built): `req.c`'s run reset on an empty mid-CAT is now
  unreachable from parsed patterns but still reachable from built seals;
  `(?:|)` and `A_REP` over an empty are other empty-equivalent shapes the drop
  does not touch (the brief's general form is the concatenation element).

## flagfix2 (sonnet, 2026-10-24): the owed checks

### 1. The 3 `^(?i)${v}$` mover cells, with a variable context

Ref = b260c1f46 build (`/tmp/claude-1001/flagfix/ref/build/pcrec`), new = the
branch build. Cells = the sweep's three (default/byte, `--engine=vm`/byte,
default/utf8), `--features all`. Each artifact got a driver calling
`rx_search(s, n, 0, caps, &v, 1)` with `rx_var{"v", ...}` per subject line.
43,624 (variable state, subject) pairs per cell: 14 variable states (unset,
empty, `abc`, `ABC`, `k`, Kelvin sign, sharp s, `a-1_z`, `A-1_Z`, e-acute
both cases, `\xff`, `a\nb`, `ss`) x all strings to length 3 on 10 letters,
2,000 seeded random strings over a 21-symbol alphabet incl. multibyte, and
the value itself / upper / lower / prefixed / suffixed.
Result, per cell: rc and every capture span byte-identical (`cmp` on the full
output) in default/byte, vm/byte and default/utf8. Emitted text differs in each
(they are movers). Outputs are not degenerate: 45 / 45 / 66 matches (rc 1,
`0,2`), 3,116 / 3,116 / 6,232 unset-variable refusals (rc -8), rest no match.
No difference, so no STOP. Scratch: `/tmp/claude-1001/flagfix2/` (gen.py, drv.c).
Not run: a positive control for this driver (the earlier sweep's control
covered the comparison method, not this variable driver).

### 2. Mech rows

Queued `617-flagfix-mech` (`boxqueue add --name`, shaped like
`603-iterland-mech`): `bash tests/mech/run_sabotage_matrix.sh S1560 S338`,
`--ready` = `boxqueue after flagfix-test` (615), cap 3600, expect rows=2,
witness `== mech run COMPLETE: 2 rows`. Only S1560 uses the `casespell` arm
(the arm has no other rows); S338 is arm `ctxnode`. Dry-run green. No new
sabotage id used.

## STATE AT HANDOFF (flagfix2)

- Rulings file: R1 (only entry) already applied by flagfix; nothing new.
- Item 1 DONE, no answer differences. Item 2 queued, behind 615.
- OWED: job `617-flagfix-mech` (runs after 615 green). Log
  `worktrees/.boxqueue/<done|failed>/*-617-flagfix-mech/job.log`; expected
  DETECTED for S1560 (casespell) and S338 (ctxnode); `scripts/boxqueue state
  flagfix-mech`. The matrix measures committed HEAD only (this commit).
- OWED (unchanged): 615-flagfix-test.
