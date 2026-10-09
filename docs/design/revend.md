# `[OPT-REVEND]` — reverse-from-end search for end-pinned patterns

**REVISION 2, lane `revrev`, 2026-10-09. DESIGN + HAND-TWIN; nothing under `src/` is built.**
Revision 1 was lane `revdes` (main `de6acf09`, abi 70). Revision 2 is cut from main
`9e431f6d` (abi 71) and applies:
- the light D6 panel `../dev/reviews/2026-10-09-r-revend-panel.md` (X1-X13): every
  finding has a disposition in §R2 and an in-place `[r2 Xn]` edit;
- lane `revq1`'s bounded-pattern timing (`../../studies/revend_twin/q1_bounded.md`): form B
  is 1.4-1.55x slower than W1 on matching bounded tails;
- **Frank's point**: with no captures, do not walk forwards at all. The end is known.
  This revision makes that **form C ("walk-only")** the primary design and keeps forms A
  and B as recorded alternatives (§2.5).

Code citations are at `9e431f6d`. Charter inputs as in revision 1: the plan row
(`docs/dev/plan.md`), the census (`docs/dev/optloop/revend_census.md`; its "zero
start-unanchored unbounded bench cells" was read at capability@0.1 and is superseded by
bench O-91 (c)), `start_table.md` (refactor A is complete) and `where_to_start.md` (D151).
Evidence: `../../studies/revend_twin/` (revision 2's files are named `r2_*`, `run_r2_*`,
`mksubj_r2.py`, `timedrv4.c`, `r2_table.py`, and `mktwin.py`'s `TWIN_FORM=walk`).

## R2. What changed, by panel finding

| id | sev | disposition | where |
|---|---|---|---|
| X1 | HIGH | **FIXED.** A speculative seed whose reverse start state is DEAD is skipped before the first view lookup (`if (<p>_reverse_is_dead(reverse_state)) continue;`). §3.1/§3.4's "trailing lookarounds are declined" was false: `ew_walk`'s `A_CAT` arm treats a `cwmax == 0` factor (`A_LOOK` included) as transparent, so `end_pin` ADMITS `\d+$(?=\n)`. Revision 2 keeps them admitted (they are sound once the dead seed is skipped) and makes "a seed may be dead" an obligation of the §8 family helper. Measured: 6 trailing-lookaround shapes in the twin, 0 diffs; with the check removed (control `nodead`, built with ASan) 3 shapes SEGV in `<p>_reverse_view_live`. Answer-net cells and a sabotage row (§9.2 rows 7) | §3.7, §6.2, §8, §9.2 |
| X2 | HIGH | **FIXED by the form change.** Form C hands a complete answer: `START` (with the end) or `VERDICT`, to the CALLER. That needs one declared edge, **E13: WINDOW → CALLER**, and nothing else: CALLER already accepts `START \| VERDICT`, so `cand_rows_selfcheck`'s `table-hands-unaccepted` test passes once `CN(CAND_NODE_CALLER)` joins WINDOW's `succ`. The one arm that still hands `LOWER` (a tie in an artifact with no anchored machine, §2.4) uses E2 unchanged. "No new edge" (rev 1) was false and is withdrawn | §2.1, §2.2 |
| X3 | HIGH | **FIXED.** R2b (`cand_read(WINDOW, RECOVER, ...)`) is dropped: it dereferenced `.d = NULL` inside `start_pinned_applies` and could never be false. In its place the emitter ASSERTS that `rev-end` and RECOVER `pinned` never co-occur, the way `start_pinned_assert_routing` (`emit_dfa.c:7857`) asserts its own premise | §2.3 |
| X4 | HIGH | **FIXED.** `.routes = CAND_ALL_ROUTES`. The predicate reads only artifact facts (`end_pin`, `cand_route_of(cx)`, the engine's emptiness, `fit.chosen`), never `s->route`, so `cand_every_route`'s cross-route walk returns the same row on every asked route | §2.2, §2.3 |
| X5 | HIGH | **FIXED.** §5.3 is now the full reader list by grep: the abi-NUMBER readers, the `END_WINDOW` stamp-VALUE readers, the byte-count readers, and (new with form C) the downstream slot stamps whose value moves on movers. The build lane re-pins all; this lane edits none | §5.3 |
| X6 | MED | **MEASURED, and it decides Q1.** Form C removes the extra passes: on a matching bounded tail it runs ONE pass over the match (the walk) against W1's two. The timing table is §6.3; Q1's discussion is §10 | §4.2, §6.3, §10 |
| X7 | MED | **FIXED.** The walk sits at the HEAD of the search, before any PRESENCE pre-check. In the twin `mktwin.py` now deletes the pre-check (forms A/C: nothing runs after the walk for it to filter) or moves it after the walk (form B). The `.txt` cells are re-timed on a body with NO `.txt` anywhere before the tail (`mksubj_r2.py` replaces the vocabulary word `file.txt` with `file.dat` and asserts it). "The twin is §5.1's text" was false in revision 1 and is now true | §5.1, §6 |
| X8 | MED | **FIXED (re-aim named).** Under REVEND-first, S264's probe `abc$` stamps `rev-end` and W1's clamp is never emitted, so S264 goes UNREACHED. The build re-aims its reach probe to a W1-served pattern that `rev-end` declines: a capture-bearing (VM-routed) end-pinned pattern, `(abc)$`, whose `<PREFIX>_END_WINDOW` stays the bound | §4.2, §9.2 |
| X9 | MED | **FIXED in the sabotage plan.** Rows added for R2 (the attempt route: witnesses `(?m:^)\w+$`, `^\w+$\|\d+$`, `(?:^\|,)\w*$`), R3, the `\G` decline and the dead-seed check; row 4's witness becomes `(?:a$)?` (the old `(?:a$)?b` is never admitted). The twin's `eol` column is hand-entered, so `end_pin` itself is never exercised by the twin; the build's net takes the seed count from the compiler and floors the emitted `revend_seed` TEXT, not just the stamp. The independent controls are the libpcre2 answer net and the `-fno-rev-end` arm; the mover-vs-stamp census shares its source with the selection and is a consistency check, not a control | §9.2, §12.2 |
| X10 | MED | **FIXED.** One spelling: the stamp token is the row's listed name, `"rev-end"` (the writer prints `cand_listed_name(row)`). `"reverse"` is withdrawn | §5.2 |
| X11 | LOW | **FIXED.** A fourth conjunct: `!dfa_engine_is_empty(cx)` (`emit_dfa.c:4403`). `[^\x00-\xff]$` declines | §2.3 |
| X12 | LOW | **FIXED.** The answer net's K74 exclusion covers `$` cells too (`[^a]*$`, `\B.*$` on `"a\xce"` diverge at an ill-formed end, pre-existing); a line for K74's entry is listed for the build lane | §9.3 |
| X13 | LOW | **FIXED in the build plan.** The `-fno-rev-end` axes floor arm is new work (test-axes has no automatic per-flag mover floor). Form C SHRINKS a mover's `<p>_search` (the forward pass, its prefilter and the pre-check are not emitted), so it cannot push an artifact over an emit cap; the refusal-set check is still listed, because a `$` artifact without an anchored machine keeps its body (§2.4 row 3) | §9.1 |

Beyond the panel, this revision adds:
- **form C** and its exactness argument (§3.2-§3.3);
- the **tie** rule and the static fact that removes it (§2.4);
- the stamp consequence of not running the downstream slots (§5.2), with its reader census
  (§5.3) and a question for Frank (§10 Q2);
- a filed widening: the walk needs only the REVERSE machine, so a pattern whose forward
  unanchored DFA overflows (e.g. `[a-z]{0,8192}\z`, which falls back to the VM today) could
  stay on the DFA route (§9.1 item 5).

## 0. Answers first

1. **The design (form C, walk-only).** ONE new WINDOW-slot row `rev-end`, first in the
   slot. For an end-pinned pattern on the DFA route, `<p>_search` is the artifact's own
   reverse machine walked back from each possible end (`n`; and `n-1` under `$`/`\Z` when
   `s[n-1] == '\n'`), recording which seed reaches the smallest accepting position `s*`.
   - Exactly one seed reaches `s*`: the answer is `(s*, that seed)`. No forward pass runs.
   - Both seeds reach `s*` (a TIE): leftmost-first priority decides `n` vs `n-1`, resolved
     by ONE anchored forward run from `s*`.
   - No seed accepts: NOMATCH.

   It hands `START` (and the end) or `VERDICT` to the CALLER over a new declared edge E13
   (X2). PRESENCE, FIRST, NEXT and RECOVER are not asked on the search path.
2. **The tie (§2.4).** A tie needs a non-empty match that ends at `n` by consuming the final
   `'\n'`. Where the reverse machine's seed state cannot consume `'\n'` under the end view
   (e.g. `\d+$`, `[a-z]+\.txt$`, `.*\.txt$`: `'\n'` is in none of their last-byte sets), or
   the pattern pins `\z` (one seed), no tie is possible and no tie code is emitted. Otherwise
   the tie arm is a three-row first-match table: no tie / one anchored run (`<p>_match`,
   the unwrapped anchored machine) / hand `s*` to the body as `LOWER` (an artifact whose
   `_match` is the `search-filter` wrapper, where calling it would recurse).
3. **Exactness (§3).** Every match ends in `E = {n} ∪ {n-1 if $/\Z and s[n-1]=='\n'}`. The
   reverse machine seeded at `e` accepts at exactly the starts of the matches that end at
   `e`, so `s*` is the leftmost-first start (panel-upheld), and a single reaching seed is the
   only possible end at `s*`. Empty matches, `search_from`, find-all, views/lookbehind at
   the start edge, utf8 (K49/K50 by construction) and the dead seed (X1) are each argued in
   §3 and swept in the twin.
4. **Evidence (§6).** Answer identity on 74 patterns (43 + 18 new X1/tie/wide shapes +
   revq1's 13 bounded): forms C, A and B each **0 twin disagreements over 1,393,750 cells**
   (A: 1,372,523; it cannot twin `[a-z]{0,4096}\z`, whose `_match` is the search-filter
   wrapper), **0 / 78,341 find-all**, and **0 vs libpcre2 10.46** except K74's 55 cells
   (artifact and twin identical). Form C on `-fno-anchored-dfa` artifacts (ties hand `s*`
   to the body): 0 / 339,632. Five planted controls each go red on a named witness.
   <!-- R2-TIMING-0 -->
5. **Q1 and Q2 (§10).** <!-- R2-Q-0 -->
6. **Family (§8).** Unchanged in shape: RECOVER's reverse pass, REVEND and D151's
   rev-inner share one parameterized reverse-block helper. Revision 2 adds two obligations
   to it: "a seed may be dead" (X1) and "report which seed(s) reached the minimum".

---

## 1. What fired, and what today costs

Unchanged from revision 1. Bench O-91 (c) gives five patterns x three `t-tail-*-1m` bodies
(15 cells), plus `\s+$` x `t-trim-nearmiss-16k` and `\d+$` x `t-1m`.
- Every pcrec cell stamps `engine=dfa, match=unwrapped, start=reverse-pass` and costs
  0.20-2.72 ns/B whatever the tail. RE2, rust and vectorscan are 22-255 ns flat; the JIT is
  at parity with pcrec.
- Today is linear because the forward pass of an end-pinned pattern can only accept at
  `n`/`n-1`, so it always runs to `n` (`emit_unanchored`, `emit_dfa.c:9715`; the loop's
  last-accept record and dead-state break).

## 2. Route and admission — one WINDOW row

### 2.1 Why WINDOW, and what it hands `[r2 X2]`

The WINDOW slot asks "can a match begin before some position computed from the END?"
(`start_table.md` §1.2). REVEND answers it with the whole match: the start `s*`, and the
end. Under form C the row therefore hands the match itself to the CALLER:

| outcome | type | edge |
|---|---|---|
| one seed reaches `s*` | `START` = `s*`, end = that seed | **E13** WINDOW → CALLER (new) |
| a tie, the artifact has an anchored machine | `START` = `s*`, end = `s*` + the anchored run's length | E13 |
| no seed accepts | `VERDICT` (NOMATCH) | E13 |
| a tie, `<PREFIX>_DFA_MATCH "search-filter"` | `LOWER` = `s*` | E2 (unchanged), into the body |

E13 is the 13th edge of `start_table.md` §1.6's table, written in the same shape:

| E13 | WINDOW `rev-end` (`START` and the match END, or `VERDICT`) | the CALLER, who re-enters at E1 for find-all | the walk's own return | yes: find-all, as E10 |

`cand_nodes[CAND_SLOT_WINDOW].succ` gains `CN(CAND_NODE_CALLER)`. CALLER already accepts
`CT_START | CT_VERDICT` (`emit_dfa.c:8086`), and `cand_rows_selfcheck` accepts a row's
hands against the union of its slot's successors, so the row's
`CT_START | CT_VERDICT | CT_LOWER` passes `table-hands-unaccepted`. The existing W1 and
`window-none` rows still hand `LOWER` only. `start_table.md` §4.4 had REVEND handing `CAND`;
the build lane corrects that line to point here.

### 2.2 The row `[r2 X2, X4, X10]`

```
{ .c = { "rev-end", PCREC_NO_REV_END, cand_rev_end_applies },
  .slot = CAND_SLOT_WINDOW, .routes = CAND_ALL_ROUTES, .tok = "rev-end",
  .map = CM_EXACTREV, .hands = CT_START | CT_VERDICT | CT_LOWER, .giveup = CG_NEUTRAL,
  .list = { [CAND_ROUTE_DFA] = { "end-window", 1, "rev-end", PCREC_NO_REV_END } },
  .desc = "per artifact, DFA route: every alternative ends in $/\\Z/\\z outside multiline "
          "(the end_pin fact) and the artifact has a non-empty reverse machine, so the "
          "search walks that machine back from the subject end (and from before a final "
          "newline under $/\\Z) and returns the match it finds; no forward pass runs",
  .u.window = { .clamp = false, .walk = true } }
```

It sits at the head of the WINDOW block, before `window` (W1). W1's listing order moves
1 → 2 and `window-none` 2 → 3 (a listing change, so a spec change, §9.4). `CM_EXACTREV` is
the mapping `start_table.md` §1.4 reserved for D151; this row is its first user.

### 2.3 The predicate `[r2 X3, X4, X11]`

```c
static bool cand_rev_end_applies(const CandSel *s)
{
    if (pcrec_fact_end_pin(s->cx) == PCREC_EPIN_NONE) return false;   /* R1 */
    if (cand_route_of(s->cx) != CAND_ROUTE_DFA) return false;          /* R2 */
    if (dfa_engine_is_empty(s->cx)) return false;                      /* R4 [r2 X11] */
    return s->cx->job->fit.chosen == ENGM_DFA;                         /* R3 */
}
```

- **R1, the fact `end_pin`.** As revision 1: `ew_walk`'s view plus its `\G` and multiline
  declines, with no width and no encoding conjunct; `end_window` becomes its reader, so the
  two cannot drift. `[r2 X1]` It admits a trailing zero-width factor, lookarounds included
  (`A_CAT`'s `cwmax == 0` arm, `endwin.c:88`): `\d+$(?=\n)` reads `eol`. That is sound,
  because seeding a position where no match ends is always sound (the walk accepts nothing
  there), PROVIDED a dead seed is skipped (§3.7).
- **R2, a reverse machine exists.** `cand_route_of(cx) == CAND_ROUTE_DFA` is `ENG_UNANCH`,
  the only engine with `job->rdfa`. The attempt route (`(?m:^)\w+$`, `^\w+$|\d+$`,
  `(?:^|,)\w*$`) and VM artifacts decline here. `[r2 X3]` R2b is gone. The emitter asserts,
  where it emits the walk, that RECOVER did not select `pinned` (P1 needs a PLAIN-view
  accept at `s0`, which an end-pinned accept never is), aborting the compile if it did:
  the premise is held where it is used, as `start_pinned_assert_routing` holds its own.
- **R4, a non-empty engine.** `[r2 X11]` `[^\x00-\xff]$` would otherwise stamp `rev-end`
  and emit no walk.
- **R3, the caller-facing entry**, W1's own site condition.

`[r2 X4]` None of the four reads `s->route`; the row is route-independent by construction.

### 2.4 The tie arm: three rows, first match

A TIE is both seeds reaching `s*`. Then `(s*, n)` and `(s*, n-1)` both match, and
leftmost-first priority (the pattern's own preference order at `s*`) picks one: `\s*$` on
`" \n"` is `(0,2)`, `\s*?$` is `(0,1)`. The reverse walk cannot see priority. So:

| # | row | applies when | emitted |
|---|---|---|---|
| T1 | `no-tie` | `end_pin == z` (one seed), or the fact `nl_last` is false | no tie code at all |
| T2 | `anchored` | `<PREFIX>_DFA_MATCH "unwrapped"` (the artifact owns an anchored machine) | `if (tie) end = s* + <p>_match(s*)` |
| T3 | `body` | otherwise (`"search-filter"`: `<p>_match` wraps `<p>_search`, so calling it from the walk would recurse) | `if (tie) { search_from = s*; <the body> }` (form B's arm, ties only) |

**The fact `nl_last`** ("a non-empty match can end by consuming `'\n'`"). A tie needs seed
`n` to accept below `n` while `s[n-1] == '\n'`; seed `n`'s first reverse step consumes that
`'\n'`. So `nl_last` is false exactly when the reverse machine's seed state, after the end
view is taken at `n`, steps to the dead state on `byte_class['\n']` (for a seed-table
artifact: when every seed-table entry for that class is dead). It is computed on the BUILT
reverse machine, at emission, by the walk's own emitter. In pattern terms: `'\n'` is not in
the set of bytes that can be a match's last byte. The bench's five: `\d+$`, `[a-z]+\.txt$`,
`.*\.txt$` have `nl_last` false (no tie code); `\w+\z` is one seed; `\s+$` has `nl_last`
true (a tie is real: `"end of file   \n"`, timed in §6.3).

The table is data (`start_table.md` §0a's rule): its rows are the WINDOW row's payload
(`u.window.tie`), listed under `--list-axes` as a sub-axis, and the emitter does not branch on
row names.

### 2.5 The recorded alternatives

| form | what the walk hands | passes over the match | needs | status |
|---|---|---|---|---|
| **C** walk-only | the match (`START` + end) or NOMATCH | 1 (+1 anchored run on a tie) | the reverse machine; an anchored machine only for T2 | **primary** |
| A exact | `CAND` = `s*` to the anchored entry | 2 (walk + anchored run, every call) | an anchored machine always (refuses `[a-z]{0,4096}\z`) | recorded |
| B lower | `LOWER` = `s*` to the unchanged body | 3 (walk + forward + reverse) | nothing new | recorded; it is form C's T3 tie arm |

Form B was revision 1's choice because it kept every stamp truthful and needed no new
edge. Both reasons are re-weighed in §10 Q2 against the timing.

### 2.6 Deny/force axis, and what `make test-axes` needs

As revision 1: deny only, `-fno-rev-end` / `PCREC_NO_REV_END` (one new bit, the manager's
allocation); the flag removes the row and nothing branches on it. `make test-axes` picks
the arm up from `--list-axes`; it owes a population FLOOR counted from the emitted text
(`[r2 X9]`: the `revend_seed` loop, not only the stamp), and the axis's divergence class is
empty.

## 3. Exactness

### 3.1 The leftmost start

As revision 1 (panel-upheld). `E` is `{n}` for `\z`, and `{n, n-1}` for `$`/`\Z` when
`s[n-1] == '\n'` (`EW_EOL_SLACK`). The reverse machine seeded at `e` accepts at exactly the
positions `p ≥ search_from` where some path of the pattern matches `[p, e)` with the end
views applied at `e` and the left-context views at `p`. So `s* = min over e ∈ E` of the
earliest such `p` is the smallest start of any match, which is the leftmost-first match's
start: PCRE2 takes the smallest start with any match, and priority acts only among ends at
that start.

### 3.2 The end without a forward pass (form C)

Let `R(e)` be the set of accepting positions of the walk seeded at `e`.
- **One seed.** If `s* ∈ R(e)` for exactly one `e`, then every match starting at `s*`
  ends at `e` (no other end is possible: the admission fact puts every end in `E`, and
  `s* ∉ R(e')` says no match spans `[s*, e')`). The priority-preferred match at `s*` is the
  only one, `(s*, e)`.
- **Tie.** If `s* ∈ R(n) ∩ R(n-1)`, both ends are possible and the pattern's priority
  chooses. An anchored leftmost-first run from `s*` returns exactly that choice (it is the
  `<p>_match` contract: the match the search would report, given that it starts at
  `s*`). T3 instead hands `s*` to the forward pass, whose first accepting thread starts at
  `s*` and whose last accept is the preferred end.
- **None.** If no `R(e)` meets `[search_from, n]`, no match exists.

The walk's accepting set is exact, not a superset: it is the full reverse DFA over the
whole pattern, stopped only by the dead state or `search_from`, and the stay-skip arms
(`dir_rev_skip`) record "every position the run passed accepts" exactly as today's
reverse pass does.

### 3.3 Empty matches, nullable bodies

A nullable body accepts at the seed itself, so `s*` can be `n` or `n-1`.
- `s* = n` (an empty match at the end) comes only from seed `n` (seed `n-1` cannot accept
  above `n-1`): one seed, end `n`. `a*$` on `"bb"` is `(2,2)`.
- `a*$` on `"aa\n"`: seed 3 consumes `'\n'` and dies, `R(3) = {3}`; seed 2 walks back over
  `aa`, `R(2) = {2,1,0}`. `s* = 0` from seed 2 alone: `(0,2)`.
- `\s*$` on `" \n"`: `R(2) = {2,1,0}`, `R(1) = {1,0}`. Tie at 0; the anchored greedy run
  takes `" \n"`: `(0,2)`. `\s*?$`: the anchored lazy run stops at 1, where `$` holds before
  the final newline: `(0,1)`. These are the controls `tien`/`tien1` (§6.2).

### 3.4 `search_from > 0`, find-all

As revision 1: a seed `e < search_from` is skipped; the walk stops at `search_from` with
the existing lower-bound test after the accept test, reading `subject[search_from - 1]` for
left context (`where_to_start.md` §2.5's obligation); `search_from > n` keeps `return 0`.
The tie's anchored run starts at `s* ≥ search_from` and reads `subject[s* - 1]` for its own
left context, which is the anchored entry's contract. Find-all re-enters at E1 with the
returned end; an empty match at `n` advances past `n` by the caller's rule and the guard
ends the loop. The twin runs the find-all loop on every subject (§6.1).

### 3.5 `$` vs `\z` vs `\Z` vs `(?m)$`

As revision 1. A mix (`\d+$|\w+\z`) seeds both and the views reject the `\z` branch at
`n-1`; `(?m)$` is declined by the fact. `\s*$|x\z` is in the twin set (a tie-capable mix).

### 3.6 utf8: the K49/K50 obligation

As revision 1: the seeds are character starts, and the reverse machine accepts only after
consuming whole well-formed characters (an ill-formed byte matches nothing under the
invalid-tolerant contract), so `s*` is a character start and the anchored tie run starts on
a boundary. The entry's startpos guard and K75's offset-0 alignment run before the walk
(the twin keeps both at the head). `tie-utf8` (`\s+?$` under `-e utf8`) is in the set.

### 3.7 A dead seed `[r2 X1]`

A seed is SPECULATIVE: nothing proved that a match can end there. For an artifact whose
reverse machine seeds through `<p>_reverse_seed_state[...]` (a trailing lookahead reads the
byte AT the seed), the seed at `n` has no byte and is the dead state `-1`; for a constant
seed under a view that cannot hold, the view-taken state can be dead. The reverse block's
first statement reads `view[row(reverse_state)]`, so a dead seed is an out-of-bounds read
(rvcrit1: ASan SEGV on `\d+$(?=\n)`, `\d$(?!\n)`, `a\Z(?=\n)`). The fix is one line after the
seed declaration: `if (<p>_reverse_is_dead(reverse_state)) continue;`. Today's RECOVER pass
never meets this, because its seed is a real forward accept. The family helper (§8) makes
the check part of its contract, since rev-inner's landmark seeds are speculative too.

### 3.8 Absent or refused reverse machine

R2 declines; the artifact keeps W1 or `none`. No row of this design runs without its
machine.

### 3.9 The give-up posture

`NEUTRAL` on the DFA route (no VM attempt exists to skip). The VM hybrid stage 2 would be
`ONE_WAY` (§9.1 item 6).

### 3.10 Captures

DFA artifacts carry group 0 only, so form C is complete on its route. A captures-needing
artifact is a VM hybrid and R3 declines it today. Stage 2 would hand the VM the walk's
exact window: one VM attempt anchored at `s*` with its end bounded by the walk's end (or
both ends on a tie), producing the captures over the span. It needs the reverse tables in
the VM entry's function and a `ONE_WAY` posture. It is not trivial, so it stays FILED with
its trigger (D77): a captures-bearing end-pinned bench cell, e.g. `(\d+)$`.

## 4. Interactions

### 4.1 With the other slots

Under form C the search path asks only WINDOW. PRESENCE, WIDTH, FIRST, NEXT, RETRY, BOUND
and RECOVER are not asked by `<p>_search` on an admitted artifact, except on the T3 tie arm,
where the body asks them exactly as today over `[s*, n)`. The anchored entry `<p>_match`
is unchanged and keeps its own selections.

### 4.2 With `[OPT-ENDWIN]` (W1) `[r2 X6, X8]`

REVEND first takes the class B byte rows (bounded width, start-unanchored) from W1 on the
DFA route. Revision 1 called them "flat either way"; the panel showed form B was three
passes against W1's two, and revq1 measured it 1.4-1.55x slower on matching tails. Form C is
one pass (the walk), plus a tie run only where `nl_last` holds. §6.3 times W1, C, A and B
interleaved on revq1's 13 bounded rows. W1 stays the row for the VM route, for hybrids until
stage 2, and for the `-fno-rev-end` arm. S264's reach probe moves to a W1-served pattern
(§9.2).

### 4.3 With `memfn` (D146/D147)

As revision 1 for the walk: a DFA step loop, never delegated (T8); its stay-skips are the
existing STAY site's `dir_rev_skip`. Revision 2 adds one consequence: on an admitted
artifact the FORWARD pass's delegated sites (the PRE pre-check, the PF/OFS prefilter, the
forward STAY/EDGE loops) are no longer emitted in `<p>_search`. The site manifest counts
sites by function, so C17 (`tests/memfn/run_site_manifest.sh`) and the kit's per-artifact
`MEMFN_FORMS`/`MEMFN_LIBC` stamps must be re-run on the movers; a fall in a row's population
floor is the expected direction and is re-pinned in the build commit. No [MEMFN] request.

### 4.4 With `[ENG-TACTICS]` rev-inner (D151)

See §8.

## 5. Emitted shape and the ABI event

### 5.1 The C (form C; `mktwin.py TWIN_FORM=walk` is this text) `[r2 X7]`

The walk is the first thing `<p>_search` does after the entry guards (K50, K75): it is
emitted at W1's position and before any PRESENCE pre-check. The reverse machine's tables
are emitted ahead of it; the forward tables, the prefilter, the pre-check and the forward
and reverse passes are not emitted on an admitted artifact (except under T3).

```c
    if (search_from > subject_length) return 0;
    size_t revend_start = (size_t)-1, revend_end = 0;
    int revend_tie = 0;
    for (int revend_seed = 0; revend_seed < 2; revend_seed++) {   /* 1 under \z */
        size_t match_end_position = subject_length;
        if (revend_seed == 1) {
            if (subject_length == 0 || subject[subject_length - 1] != '\n') break;
            match_end_position = subject_length - 1;
        }
        if (match_end_position < search_from) break;
        size_t match_start_position = (size_t)-1;
        size_t rewind_position = match_end_position;
        <p>_reverse_state reverse_state = <the seed, as today>;
        if (<p>_reverse_is_dead(reverse_state)) continue;          /* [r2 X1] */
        <the reverse block emit_scan_loop(c, &rev) writes today, label renamed>
        if (match_start_position == (size_t)-1) continue;
        if (match_start_position < revend_start) {
            revend_start = match_start_position; revend_end = match_end_position; revend_tie = 0;
        } else if (match_start_position == revend_start) revend_tie = 1;
    }
    if (revend_start == (size_t)-1) return 0;
    <tie arm, §2.4: T1 nothing; T2 `if (revend_tie) revend_end = revend_start + <p>_match(&ctx);`;
                    T3 `if (revend_tie) { search_from = revend_start; <the body as today> }`>
    if (capture_spans) { capture_spans[0][0] = revend_start; capture_spans[0][1] = revend_end; }
    return 1;
```

- Under `\z` the loop bound is 1 and there is no newline arm and no tie arm.
- The block's label needs a distinct name in the walk copy (a parameter of the family
  helper, §8).

### 5.2 Stamps `[r2 X10]`

- `<PREFIX>_END_WINDOW` gains the value `"rev-end"` (closed vocabulary + 1; it was a number
  or `"none"`).
- **The downstream search stamps** (`RX_DFA_SCAN`, `RX_DFA_PREFILTER`,
  `RX_DFA_PREFILTER_OFFSETS`, `RX_DFA_START`, `RX_REQ_BYTE`/`_RUN`/`_WHY`/`_HANDOFF`) describe
  passes that form C does not emit on an admitted artifact (T1/T2). Left as they are, they
  would be the "stamp names a pass that does not run" defect class `start_table.md` §0 lists.
  The proposal: each takes its existing `"none"` value where it has one, with
  `RX_REQ_WHY`/`RX_DFA_START` reading `"rev-end"` (the reason), following `[OPT-5]`'s
  precedent (the pinned search removed the reverse machine and `RX_DFA_START` gained
  `"pinned"`). Under T3 the body is emitted and they keep their values. This is the largest
  reader cost of form C (§5.3) and the substance of §10 Q2.
- `rx_info` has no window field; `rx_info.search_form` (the `[OPT-5]` mirror) gains the same
  value as `RX_DFA_START`.

### 5.3 The readers (found by grep at `9e431f6d`; NOT edited by this lane) `[r2 X5]`

The rule (root CLAUDE.md; D76/D94): grep at build time for the CURRENT abi number and every
stamp value that moves, then run the suites that COUNT (registry, codegen, rxtsource). The
numbers below are this lane's grep at `9e431f6d`; the build lane re-greps.

**(a) abi-NUMBER readers** (`grep -rnE 'PCREC_ARTIFACT_ABI|abi[ =:]+71\b|\babi 71\b|ABI_H 71'`
over `src lib cli tests docs/spec memfn scripts` plus the `start_table/`/`dec_fallback/`
data):
- `src/gen/emit_dfa.c:54` (the constant; `:138`, `:1863`, `:2946` read it);
- `lib/pcrec.h:12`, `lib/CLAUDE.md:298`, `src/gen/CLAUDE.md:48`;
- `docs/spec/match_api.md:302,305` (the TU-guard example), `:2318` (the abi sentence), §6's
  change log;
- `tests/codegen/run_codegen_tests.sh:3042` (`ABI_EXPECT=71`);
- `tests/codegen/run_recursion_identity.sh:1226` (the (B) FILEPIN self-pin);
- `tests/registry/limits_check.sh:530`;
- `tests/mech/sabotages/S693_abi_not_bumped.sh:24-25` (`SAB_BEFORE`/`SAB_AFTER`);
- `docs/design/start_table/sabotage_anchors.tsv:568`,
  `docs/design/dec_fallback/sabotage_anchors.tsv:568` and the three `call_graph*.txt`
  (`def-const PCREC_ARTIFACT_ABI src/gen/emit_dfa.c:54-54`).

**(b) byte-count readers** (values move with any emitted text; no digit of the abi):
`tests/codegen/run_cpset_structure.sh`'s `EMITTED_BYTES` manifest (12 rows),
`tests/resource/run_resource_tests.sh`'s K59-PREMUL rung, `tests/size/`'s tripwire and
`docs/dev/artifact_size_log.tsv`, `tests/codegen/run_size_term.sh`'s cap-rescue cap. Form C
SHRINKS movers, so a size-cap witness can move out of its refusal: each is re-measured.

**(c) `END_WINDOW` stamp-VALUE readers** (`grep -rlE 'END_WINDOW|end-window|end_window'`,
37 files; the ones that read a VALUE):
- `tests/codegen/run_encoding_checks.sh` DD12a(i) (`:505-522` and its "utf8 always declines"
  premise, `:706`, `:1106-1112`, `:1334-1336`): REVEND admits utf8, so the premise ends;
- `tests/codegen/run_prechecks.sh` §2.1/§2.1b/§2.2;
- `scripts/emit_sweep.py` (the DIFFER pin, the `<W>` collapse near `:692`, the ASSERT_ZERO
  utf8 cells) and `scripts/tests/emit_sweep.py.test`;
- `tests/mech/sabotages/S264`, `S295`, `S297`, `S551`; `tests/mech/run_sabotage_matrix.sh`;
- `tests/codegen/run_codegen_tests.sh`, `run_recursion_identity.sh`,
  `tests/registry/run_registry_tests.sh`, `tests/resource/run_resource_tests.sh`,
  `tests/rxtsource/run_rxtsource_tests.sh`, `tests/lookaround/run_expansion_diff.sh`,
  `tests/startset/manifests/manifest_s2_vm_forced.tsv`;
- spec: `docs/spec/tuning.md`, `match_api.md`, `registry.md` (axis counts),
  `facts_listing.md` (the new `end_pin` row), `cli.md`; `lib/pcrec.h` (the bit) and
  `src/core/axes.def`.

**(d) downstream slot-stamp readers** (form C, §5.2), files per stamp under
`src lib cli tests docs/spec scripts memfn/src memfn/tests`, `.rxt` and CLAUDE.md
excluded: `DFA_START` 19 (5 sabotage rows), `DFA_SCAN` 33 (6), `DFA_PREFILTER` 54 (25),
`DFA_PREFILTER_OFFSETS` 15 (0), `REQ_BYTE|RUN|WHY|HANDOFF` 90 (47). Most of these read a
specific witness pattern; the ones that move are those whose population includes an admitted
artifact, which only the build's movers census (`emit_sweep` default vs `-fno-rev-end`) can
name. This is the reader cost §10 Q2 weighs.

### 5.4 Movers

Every artifact the row admits moves: the corpus class U DFA byte rows (32 distinct),
class B byte rows (117, under §10 Q1), the utf8 rows, and on the bench the 15 + 2
acceptance cells, the 5 class B cells and `letters-bounded-tail-z`. The census is mechanical
(`emit_sweep` default vs `-fno-rev-end`); the moved set must equal the set whose emitted
text carries the `revend_seed` loop, and the stamp set must equal it too.

## 6. The hand-twin (`../../studies/revend_twin/`, scratch tier)

`mktwin.py` takes each UNMODIFIED artifact (`--features all`, `-e utf8` on utf8 rows,
built with `-fno-end-window` because `rev-end` precedes W1) and rewrites its `<p>_search`.
Revision 2's generator places the walk at the head (X7), skips a dead seed (X1), and has
three forms: `walk` (C), `exact` (A), `lower` (B). Every marker is asserted; an artifact of
another shape is refused. A head line that is neither an entry guard (K50/K75) nor a
pre-check (`if (...) return 0;`) is refused.

### 6.1 Answer identity (`run_r2_check.sh`; `results/r2_identity.txt`)

Population: `patterns.tsv` (43), `r2_patterns.tsv` (18 new: six X1 trailing-lookaround
shapes, eleven tie witnesses incl. one utf8, the widest DFA-routed bound
`[a-z]{0,4096}\z`), and revq1's 13 bounded rows: 74 patterns. Pools as revision 1 (848 byte
+ 12 long bodies; 300 utf8), every `search_from` in `[0, n+1]`, plus a find-all loop.

| form | patterns | twin vs artifact | find-all | artifact = twin vs libpcre2 10.46 |
|---|---:|---|---|---|
| C walk | 74 | **0** / 1,393,750 | **0** / 78,341 | 0 / 1,233,468 except K74's 55 cells on `\B\w*\z` (artifact identical) |
| A exact | 73 (refuses `[a-z]{0,4096}\z`: `_match` is the search-filter wrapper) | **0** / 1,372,523 | **0** / 76,962 | as C |
| B lower | 74 | **0** / 1,393,750 | **0** / 78,341 | as C |
| C walk on `-fno-anchored-dfa` artifacts (T3: a tie hands `s*` to the body) | 16 (X1 + tie, byte) | **0** / 339,632 | **0** / 18,277 | 0 / 301,680 |

### 6.2 The controls (`results/r2_controls.txt`; each must go red)

Run on form C over `controls_r2.tsv` (9 patterns):

| control | what it breaks | red on (twin_diff pool + long) | silent on (and why) |
|---|---|---|---|
| `noeol` | drops seed `n-1` | `\d+$` 10+70, `a*$`/`.*$`/`\s*?$` 552+355, `\d+$(?=\n)` 10+70, `a\Z(?=\n)` 24 | `\s+$`, `\s*$` (seed `n` consumes the `'\n'` and reaches the same start), `\d$(?!\n)` (never ends at `n-1`) |
| `firstseed` | first accepting seed, not the minimum | `a*$`, `.*$`, `\s*?$` (552+355 each) | the rest (seed `n` dies at once on a final newline, or both reach the same start) |
| `tien` | a tie takes `n` without the run | `\s*?$` (lazy: 552+355) | greedy ties (`n` is right) |
| `tien1` | a tie takes `n-1` without the run | `\s+$` 36+140, `\s*$` 552+355 | lazy ties |
| `nodead` (ASan) | drops the dead-seed check | `\d+$(?=\n)`, `\d$(?!\n)`, `a\Z(?=\n)`: AddressSanitizer SEGV in `<p>_reverse_view_live` | patterns whose seed is never dead |

So every control has a witness, and the per-pattern zeros name what the build's answer net
must contain: a lazy and a greedy tie witness, a nullable newline-consuming `$` pattern, and
a trailing-lookaround shape.

### 6.3 Timing (`run_r2_timing.sh`; `results/r2_timing.tsv`, `results/r2_table.md`)

<!-- R2-TIMING-6 -->

## 7. Predicted values for the bench (O-91 ask 2)

<!-- R2-PRED-7 -->

## 8. Family: the seeded reverse walk

As revision 1: RECOVER's reverse pass, REVEND and D151's rev-inner are one operation ("seed
a reverse machine at a known position, walk down to a lower bound, take the smallest
accepting position") and share ONE emitted helper, `emit_scan_loop(c, &rev)` with its four
hard-coded names (seed, result, lower bound, label) made parameters. Revision 2 adds two
obligations to the helper's contract:
- **a seed may be dead** (X1): the helper skips it before the first view lookup. RECOVER's
  seed is a real forward accept and never dead; REVEND's and rev-inner's seeds are
  speculative;
- **report which seed(s) reached the minimum**: form C needs it for the end; rev-inner can
  ignore it.

Build order unchanged: REVEND first.

## 9. The build plan

### 9.1 Steps

1. **S0 — the fact split (no mover).** As revision 1, plus `[r2 X1]` the fact's doc states
   that trailing zero-width factors are admitted.
2. **S1 — the helper (no mover).** Parameterize `emit_scan_loop`'s reverse arm by (seed,
   result, lower bound, label), with the dead-seed skip as an option the RECOVER caller does
   not take (byte-identical).
3. **S2 — the row (the abi event).** The `rev-end` row with E13 declared, its predicate, the
   tie table and the `nl_last` fact, the `CandWindow` payload, the walk emission and the
   suppression of the forward body on T1/T2, the stamps (§5.2), the listing row and
   `-fno-rev-end`. Then: the abi bump with every §5.3 (a) reader re-pinned in the same
   commit; the (b)/(c)/(d) readers re-measured; the movers census; the answer net (§9.3); the
   codegen structural check (`"rev-end"` stamp ⇔ the `revend_seed` loop is emitted; a
   declining pattern is byte-identical under `-fno-rev-end`; `nl_last` false ⇔ no tie text);
   the sabotage rows; the test-axes floor arm `[r2 X13]` (new work: test-axes has no
   automatic per-flag mover floor); a refusal-set check across the emit caps for the T3 rows
   (`tests/utf8/axis12_scripts.rxt:296` sits 75 B under the cap); C17 and the memfn stamps
   re-run (§4.3); `make test-codegen`, the counting suites, then the full battery (the
   manager's, at merge).
4. **S3 — the bench AFTER window** (§11).
5. **Filed, not scheduled (D77):** the lockstep two-seed walk (trigger: a `$` cell whose two
   walks are both long); **the forward-machine-free admission** (new): form C reads only the
   reverse machine, so a pattern whose forward unanchored DFA overflows the auto budget
   (`[a-z]{0,8192}\z` and wider fall back to the VM today; `[a-z]{0,60000}\z` stamps
   `ENGINE_SEL declined-nullable`) could stay on the DFA route if its reverse machine builds.
   Trigger: a bench cell on such a pattern; it changes engine selection, so it is its own
   design.
6. **Filed: stage 2, the VM hybrid** (§3.10), trigger a captures-bearing end-pinned bench
   cell.

### 9.2 Sabotage plan (ids NOT taken; **16 needed**)

Answer-level (each with its named witness from §6.2):
1. Seed `n-1` dropped. Witness `\d+$`, `a*$` on `"...\n"`.
2. First-accepting seed instead of the minimum. Witness `a*$`, `.*$`, `\s*?$`.
3. The `match_end_position < search_from` seed guard deleted (nullable `$` pattern,
   `search_from == n` with a final newline).
4. `end_pin` over-admits `rmin == 0` repeats (the `A_REP` arm returns the body's view).
   `[r2 X9]` Witness `(?:a$)?` or `(?:a$)?\b` (the old `(?:a$)?b` is never admitted).
5. `end_pin` admits `(?m)$` (decline (4) dropped). Multiline subjects.
6. `end_pin` drops the `\G` decline (3). A `\G...$` pattern at `search_from > 0`.
7. `[r2 X1]` The dead-seed skip deleted. Witness `\d+$(?=\n)`, `\d$(?!\n)`, `a\Z(?=\n)`
   (ASan-detected; the answer net runs under the san battery).
8. A tie takes `n` without the run. Witness `\s*?$` on `" \n"`.
9. A tie takes `n-1` without the run. Witness `\s*$`, `\s+$` on `"  \n"`.
10. `nl_last` over-claims (no tie text emitted for a pattern that can tie). Witness `\s+$`
    on whitespace ending in `\n`, lazy and greedy.

Structural (expectation from `--list-axes`/`emit_sweep`, never from the row):
11. R2 dropped: an attempt-route artifact selects `rev-end` with no reverse machine.
    Witnesses `(?m:^)\w+$`, `^\w+$|\d+$`, `(?:^|,)\w*$` (a compile abort or a refusal).
12. R3 dropped: a VM hybrid selects it.
13. R4 dropped: `[^\x00-\xff]$` stamps `rev-end` with no walk.
14. The row's deny unplumbed (`-fno-rev-end` inert): the axes floor arm or the codegen
    check reads red.
15. The forward-body suppression made unconditional (the T3 body dropped): a
    `-fno-anchored-dfa` tie witness recurses or answers wrong.
16. The stamp forked from the selection (`"rev-end"` printed from a separate condition):
    the codegen stamp ⇔ text check.

Plus re-aims: S264 (`[r2 X8]`, its reach probe to `(abc)$`), S693 (abi constant), and every
§5.3 (d) row whose witness becomes a mover (the build's census names them).

### 9.3 The answer net and its oracle

`tests/assertions/rev_end.rxt`, in `end_window.rxt`'s shape, every claim at a subject where
the row fires and (via the axes arm) where it is denied. Cells: matching/non-matching tails;
a final newline with both seeds, lazy and greedy ties (`\s*?$` vs `\s*$` on `" \n"`);
`search_from` at 0, mid-match, `n-1`, `n`, `n+1`; nullable bodies; find-all `mc` cells;
`\d+$|\w+\z`, `\s*$|x\z`; the X1 trailing-lookaround shapes; utf8 multibyte tails, a
utf8 tie, an ill-formed byte before the tail. Expectations from python `re` (base tier,
`\Z` mapped as `end_window.rxt` documents) and libpcre2 (`verify_pcre2.py`), never from
pcrec. `[r2 X12]` K74 cells are out of scope for BOTH `\B`/`\b` and `$` shapes at an
ill-formed end (`[^a]*$`, `\B.*$` on `"a\xce"`); `known_fail` keeps them, and K74's entry
gains the `$` family.

### 9.4 Spec hunks (D80)

As revision 1 (`tuning.md` §2.x `-fno-rev-end`, §2.26's W1 line, the flags index;
`match_api.md` `END_WINDOW` vocabulary + `"rev-end"`, the abi sentence and TU-guard example;
`registry.md` axis counts; `facts_listing.md` `end_pin`; `cli.md` where it lists axes), plus:
- `match_api.md`: the downstream search stamps' `"none"`/`"rev-end"` values on admitted
  artifacts (§5.2), and `rx_info.search_form`;
- `start_table.md` §1.6: E13 (manager's merge); §4.4's REVEND line corrected.

## 10. Questions for Frank (discussion)

<!-- R2-Q-10 -->

## 11. Bench-only questions (for the manager to relay)

1. Will the AFTER window run on the fixed driver ([B133])? The predictions assume it; on
   the grown driver add O-94's 40-50 ns per call.
2. Can the AFTER window add a 64 KiB `t-tail-*` variant? The claim is size-independence.
3. The bench's `t-tail-txt-1m` body: does it contain a `.txt` before the tail? Revision 1's
   timing depended on it (X7); form C does not, but today's arm does.
4. Keep the 5 class B cells and `letters-bounded-tail-z` in the AFTER window as
   do-not-regress cells (§10 Q1).
5. A tie cell does not exist in the bench family: `\s+$` on a body ending
   `"   \n"` would be the first (`t-tail-spacenl`).

## 12. Standing questions (`docs/design/CLAUDE.md`)

**12.1 The measurement regime — RELEVANT.**
<!-- R2-REGIME -->

**12.2 The independent control — RELEVANT.**
- The twin-vs-artifact compare SHARES its reverse machine and reverse block with the subject
  (the twin is built from the artifact). It proves the seeding, the seed record and the tie
  arm, not the machine.
- The independent leg is libpcre2 10.46 on every cell where it answers the same question: 0
  disagreements beyond K74.
- The sweep's ability to fail is shown by five planted controls (§6.2), each with a witness.
- `[r2 X9]` The twin's `eol` column is hand-entered, so the twin never exercises `end_pin`;
  the build's net takes its seeds from the compiler, and its structural checks read the
  emitted text (the `revend_seed` loop), not the row's predicate. The movers-vs-stamp census
  shares a source with the selection and is a consistency check only; the independent
  controls are the libpcre2 answer net and the `-fno-rev-end` arm.
- Population (K35): the axis floor counts admitted artifacts from the emitted text.

**12.3 What moves when data is regenerated — RELEVANT, little.**
- REVEND reads no calibration or table; `end_pin` and `nl_last` are derived per compile
  (`nl_last` from the built reverse machine).
- The stamps and the emitted walk move only with the row's admission: the §5 abi event.
- A regenerated bench body moves nothing in the design; the predictions depend only on the
  tails.
