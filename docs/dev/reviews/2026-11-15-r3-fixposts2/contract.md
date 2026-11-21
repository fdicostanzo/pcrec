# CONTRACT findings

## Findings

### CONTRACT-1 — the arm-0 catch-all is ASSUMED, not enforced (CONFIRMED by reading; design/maintenance, small, req.c only)
`rb_row_scan` (src/facts/req.c:392-404) stops at `n-1` and never reads the last row's `arm` nor calls its predicate; the
callers then apply that row unconditionally. So the four-table behaviour is identical to BASE (see PROBED-AND-HELD), and the
two BASE hazards are gone (no read past the end; `rr_alt`/`rb_zero_into` are bounded). But the r1 Family note asked for a
helper that ENFORCES an arm-0 catch-all; this one holds the invariant only by the header comment ("carries arm 0") and by
convention. Failure scenarios, all silent (nothing reds, emitted text unchanged): (a) give the catch-all a nonzero arm, e.g.
`{ rr_alt_affix, PCREC_WALK_ARM(TIE) }` -> `--harness=restore=tie` still applies it, the tag is inert and misleading;
(b) append a row after `rb_zero_any/CUT` -> the old catch-all becomes a scanned row whose `when` is `true`, the new row is dead.
`_Static_assert` on the last element cannot do it (gcc 15, -std=gnu11: "expression in static assertion is not constant",
probe sa.c in this dir). Proposal (pick one): a cheap runtime guard in `rb_row_scan` (last row's arm != 0 -> internal error,
one memcpy per call), or structural: the scan returns `n` when no live row above decides and each caller names its default
row outside the table so it cannot carry an arm. Either makes the comment a checked fact. Blast radius: req.c only, no abi.

### CONTRACT-2 — `rn_better`'s fall-through maps a 0 answer to `b` where BASE returned `a` (CONFIRMED by reading, latent; maintenance, 1 char)
BASE `rn_better` returned `a` when no row decided (and skipped a zero answer of the last row). SUBJECT (req.c:510-516) re-calls
the last row and returns `x.c > 0 ? a : b`, so a last row answering 0 now yields `b`. Unreachable today: the last row is
`rn_first`, which returns 1 unconditionally (req.c:474-480), and it has arm 0, so every reachable input gets `a` in both trees.
It bites the day the catch-all is replaced by a comparison that can tie (e.g. moving `rn_content` last, whose comment already
calls it "Row 4, the last"). Proposal: `return x.c >= 0 ? a : b;` (BASE's tie-to-`a`), or state in the header that the catch-all
must never answer 0. Same family: `rr_alt` ignores the catch-all's bool and `rb_rep_row`/`rb_zero_into` never evaluate the
catch-all's `when` (BASE `rb_rep_row` did not either; BASE `rb_zero_into` did, but `rb_zero_any` is `true`), so "catch-all =
unconditional" is the uniform contract now; only `rn_better` maps the unconditional row's own answer, and it maps it differently.

### CONTRACT-3 — the helper's shape costs more than the loops it replaced; "hit" is an apply in two of four tables (CONFIRMED by reading; maintenance, small-medium, req.c only)
Net req.c +106/-20 for four loops of 3-7 lines: one void-pointer callback type, four ctx structs/adapters
(`rn_choice_hit`, `rr_alt_hit`, `rb_rep_hit`, `rb_zero_hit`), the arm read by `memcpy` at an `offsetof`, and the first
`__typeof__` anywhere in src/ cli/ lib/ (grep: req.c only), used five times because the four row structs are anonymous.
House-rule notes: (i) the four adapters and the two ctx typedefs carry no header (coding.md §4.2 [HDR-1]: every function);
(ii) `(void *)a` at req.c:1139 casts away `const Ast *` only because `ctx` is non-const for the sake of `rn_choice_hit`,
which WRITES `x->c` (a predicate with a side effect) — `rr_alt_hit` likewise writes `x->o`; for those two tables the "hit"
is the row's action, which is why `rn_better` and `rr_alt` each repeat "if the scan reached the last row, apply it" by hand
(req.c:514-515, 700-701) while `rb_rep_row`/`rb_zero_into` do not need to; (iii) `memcpy(&arm, ..., sizeof arm)` trusts the
comment that `arm` is `unsigned`; an `unsigned char arm` row type would compile and read garbage — `_Static_assert(sizeof
(tab)[0].arm == sizeof (unsigned), ...)` inside `RB_ROW_SCAN` IS a constant expression and closes it. Proposal (one of):
(A) keep the function but have it call `hit` on the last row too and ignore the answer ("the catch-all always applies") —
the two hand-written "if last" lines vanish and the pure catch-alls (`rb_rep_any`, `rb_zero_any`) cost one call returning
true; plus name the row typedefs (drops every `__typeof__` cast in the adapters); or (B) a type-safe statement macro
`RB_ROW_FIRST(w, tab, i, cond)` = the bounded `for` over `i + 1 < n` skipping `(tab)[i].arm & (w)->restored`, with `cond`
an expression on `(tab)[i]` — no void*, no adapters, no const cast, ~10 lines total. (B) is the simpler and keeps one bound
in one place, which is what CONTRACT-1(r1) asked for; (A) keeps a callable seam if a table ever moves out of req.c.

### Standing question: SIBLING OF A FAMILY
Held. `grep -rn "unsigned arm;" src/` finds exactly the four tables (req.c:484, 678, 1021, 1118) and the helper's own local
(req.c:398); `w->restored` has one reader left, the helper (req.c:400) — so all four `{row, arm}` restore tables are on it
and no ad-hoc arm test survives. Other first-match row tables exist tree-wide (parse.c `fold_rows` :782, emit_iter.c
`iter_retry_rows` :64, entries.c `entry_rows` :310, callout.c `co_culprit_rows`, mod_lookaround.c `la_rows`, ctxnode.c
`pcrec_look_rows`, stamp_kinds.c `stamp_rows`, ...) but they have no restore arm and no catch-all-by-convention; they are
NOT this family and the helper (RbWalk-typed, file-static) is rightly not offered to them. No proposal.

### Standing question: GENERAL FORM + UNLOCKS
General form: "a declared first-match table whose rows each carry the restored arm that passes them over, ending in an
UNCONDITIONAL default" — the default being a separate, arm-less part of the declaration (CONTRACT-1's structural option),
and the scan applying it itself (CONTRACT-3 (A)), so a table is `{rows[], default}` and every caller is one call.
Unlocks: (1) the arm population per table becomes enumerable data — the r1 Family note's generated "row not restored"
sabotage per (table, row) could iterate it instead of hand-writing S1921/S1930/S3131 (trigger: the next arm, L1's `look`,
landing, which would add a fifth hand-written plant); (2) a `--list-*`-style dump of each table's rows and arms for the
harness (trigger: a restore arm whose reach someone has to establish by hand, as PLANTS-1 did for S3012). Both are build-on-
need (D77); neither is due now.

## PROBED-AND-HELD

- (a) Behaviour identity by reading, all four tables, every reachable input: `rn_better` (last row `rn_first` returns 1,
  arm 0 -> `a` in both trees; a middle row's nonzero answer returns the same side; ctx copies `a`/`b` are by value and equal),
  `rr_alt` (row 1 `rr_alt_union` writes `*o` only after every check passes, so a false answer leaves no partial `o` in either
  tree; the catch-all `rr_alt_affix` always returns true and writes all six fields), `rb_rep_row` (BASE was already
  `last`-bounded; identical), `rb_zero_into` (BASE evaluated `rb_zero_any` = true at the last row; SUBJECT skips the call;
  identical). n=1 and n=0 edge: tables are non-empty constants. 4 of 4 HOLD.
- `_Static_assert` on the catch-all's arm is impossible in gnu11 (gcc 15 probe, sa.c) — so CONTRACT-1's fix must be
  runtime or structural.
- (b) Emitted-byte identity, BASE vs SUBJECT, `BIN=pcrec-harness`, patterns.txt (27 patterns: 8 consuming-body repeats incl.
  width-0/`{m}`/`{m,n}`/`+`/`?`/`{20}`; 9 zero-width incl. `()`, `^`, `\b`, `$`, `\K`, positive/negative lookahead and
  lookbehind (`--features all`); 7 alternations equal/unequal width incl. utf8 multibyte and 3-way, under
  `-fno-altcls-merge -fno-altcls-factor`; 4 run-choice ties), x 7 arm configs (default, empty, zero, rep, tie, alt, and
  `empty+zero+rep+tie+alt` which drives every table to its catch-all) x {byte, utf8}: **378 SAME, 0 DIFF, 0 RCDIFF**
  (per arm/enc: 27 SAME each, 14 cells). 70 further pairs were BOTHFAIL from a first pass without `--features all` (the 5
  module-gated patterns; re-run with it, counted above). Results: results.tsv, results2.tsv; runner run.sh/run2.sh.
- Reach (SUBJECT, facts listing + one emitted-C pair): every arm moves `req_whole_run` on its witness (`abcd(?:)*efgh`,
  `abcd()efgh` empty; `xy(?:ab){1,3}zw` rep; `x(?!ab)ac` zero; `xy(?:ab|ac)zw` alt; `abcd.*efgh`, `mq.*qm` tie — tie reaches
  the `rn_first` catch-all; `ab(?:^)+cd` all arms), and `restore=tie` changes `RX_REQ_RUN`/`RX_REQ_BYTE` in the emitted C,
  so the SAME counts are not vacuous. ~17 compiles.
- Compile budget used: ~1,080 (incl. 140 cheap BOTHFAIL rejects) — over the ~800 guideline by the failed first pass; noted.
