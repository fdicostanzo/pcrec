# rpfloor — diagnosis of the run-pinned floor drop on main (150 -> 117)

Lane `rpfloor` (sonnet, TRIAGE), branch `lane/rpfloor` from `main`
(`eee1d36a`). Scope held: the pcrec repo only, this worktree
(`worktrees/rpfloor`); a scratch detached worktree
(`worktrees/rpfloor-bis`) was created for the A/B bisection and removed
per the brief when done.

## 1. The commit, found by A/B, not by reading history

`tests/codegen/run_form_census.sh`'s `D:RX_DFA_PREFILTER=run-pinned` floor
(130) was set at `[OPT-LITSCAN] S1`'s build (`6edec9de`, 2026-09-25),
measuring 150 (155 at the S1 branch's own merge to main, `0bb87eda` —
confirmed live below). Lane `triaxes` had already found main red on this
floor independent of `lane/ucpu2` (117 against 130) but did not diagnose
what moved it, and named `[FIND-TIE]` (merge `72e3ae41`) and
`[OPT-LITSCAN] F5` (merge `4666ba54`) as the two candidates to test first.

**Built and censused three points on main's own line**, one `pcrec`
binary and one `bash tests/codegen/run_form_census.sh` run per point (all
in `worktrees/rpfloor-bis`, `make -j4 CC=gcc-16`):

| commit | what it is | run-pinned population |
|---|---|---|
| `0bb87eda` | `[OPT-LITSCAN] S1` steps 1-5 merged to main | **155** |
| `4666ba54` | `[OPT-LITSCAN] F5` merged to main | **165** (up) |
| `72e3ae41` | `[FIND-TIE]` merged to main | **117** |

**F5 is exonerated** — the population went UP (155 -> 165) at its merge,
not down. **The entire 155(165)->117 drop happens exactly at FIND-TIE's
merge**, and nothing after it moves the number further: main (`eee1d36a`)
measures 117 directly (same number triaxes measured independently at
`fdcf3e00`), and triaxes's own audit already confirmed zero `src/`/`tests/`
changes between `fdcf3e00` and today's main. FIND-TIE is the sole cause.

## 2. The mechanism, confirmed by named witnesses, not just read from the diff

`pf_run_applies_common` (`src/gen/emit_dfa.c:5357`) is `run-pinned`'s
predicate. It requires an IDENTITY between two INDEPENDENTLY-COMPUTED
offsets:

- `sp = pin.o + r->idx` — `r->idx` comes from
  `pcrec_find_run_scan_index` (`src/core/findings.c:500`), the run
  reader's own PICK of which run byte to scan.
- `o->walk->k[o->sel[o->scan]].k` — the offset-set walk's own chosen scan
  offset, from `pcrec_prefix_ksets` (`src/opt/prefix_k.c:209-322`), a
  COST-GREEDY selection over the k-set walk that has nothing to do with
  the run reader at all. Its own tie-break (line ~277, `if (cost < best)
  continue`, strict `<`) keeps the first-found candidate on a cost tie,
  i.e. the LOWEST offset (ascending walk order) — unaffected by FIND-TIE,
  since FIND-TIE never touches `prefix_k.c`.

`[FIND-TIE]` (`ed51481b`, merged `72e3ae41`, 2026-09-28) changed ONLY the
run reader's own data-tie rule: on a genuine rate tie among a run's bytes,
`pcrec_find_run_scan_index` used to pick the LEFTMOST tied member and now
picks the RIGHTMOST (D126 Q4: a PICK's data-tie answer should equal its
own NONE answer, which is rightmost — the fix `pcrec_find_set_pick`
already had). FIND-TIE's own report says this is "answer-identical...
moves only a speed [choice]" — true for MATCH correctness, but incomplete:
because `pf_run_applies_common`'s identity clause compares the run
reader's pick against a SEPARATE, unrelated selector that never moved,
**flipping the run reader's tie-break also moves FORM** — whether an
artifact is `run-pinned` at all, not merely which byte inside an unchanged
mechanism gets scanned.

**Confirmed live** (binaries built at `4666ba54` = pre-FIND-TIE, `72e3ae41`
= post-FIND-TIE):

```
(a)(bb)(ccc)   OLD: RX_REQ_RUN "...@1"  RX_DFA_PREFILTER "run-pinned"      OFFSETS "0,1*,2,3,4,5"
               NEW: RX_REQ_RUN "...@2"  RX_DFA_PREFILTER "offset-set"      OFFSETS "0,1*"

SS             OLD: RX_REQ_RUN "5353@0" RX_DFA_PREFILTER "run-pinned"      OFFSETS "0*,1"
               NEW: RX_REQ_RUN "5353@1" RX_DFA_PREFILTER "memchr"          OFFSETS "none"

\(\)           OLD: RX_REQ_RUN "2829@0" RX_DFA_PREFILTER "run-pinned"      OFFSETS "0*,1"
               NEW: RX_REQ_RUN "2829@1" RX_DFA_PREFILTER "memchr"          OFFSETS "none"

(abc)(abc)     OLD: RX_REQ_RUN "...@1"  RX_DFA_PREFILTER "run-pinned"      OFFSETS "0,1*,2,3,4,5"
               NEW: RX_REQ_RUN "...@4"  RX_DFA_PREFILTER "offset-set"      OFFSETS "0,1*"
```

In every case the run's OWN scan index moves (the tie-break flip, exactly
as FIND-TIE describes) while the offset-set walk's own scan stays put at
its unrelated, cost-derived choice (offset 1 for the two capture-group
patterns) — so the two no longer agree, and `run-pinned`'s identity clause
fails. All four are byte-tie cases: `SS`/`\(\)` have a two-byte run of an
identical repeated byte (a certain data tie under any rate table);
`(a)(bb)(ccc)`/`(abc)(abc)` tie under the census's DEFAULT (unnamed)
analysis, whose built-in frequency table floors every zero/near-zero-count
byte identically — exactly the "the DEFAULT axis moves too" scope FIND-TIE's
own report named but did not check against this specific census.

**The exact population.** Compiled all 165 corpus patterns the OLD binary
stamps `run-pinned` (matching the S1-merge-point census exactly), then
compiled the same 165 with the NEW binary: **48 patterns leave run-pinned**
(to `offset-set`, `memchr`, or similar) — 165 - 48 = 117, the exact number
both this lane's own census and triaxes's independent one measured on
main. No corpus pattern moved INTO run-pinned under FIND-TIE in this
population (net delta accounts for the whole drop with no offsetting gain
inside the 165 starting set). Every witness sampled is answer-identical —
matches are unaffected, only the emitted structural form and the scanned
byte move, consistent with FIND-TIE's own "answer-identical" claim (which
is correct about MATCHES; it undersold the FORM consequence).

## 3. Verdict: INTENDED consequence of the ruled change, not a regression

The mechanism is deterministic, fully explained by a RULED design fix
(D126 Q4 applied consistently — the same "a PICK's tie must equal its own
NONE answer" rule that already governed `pcrec_find_set_pick`), and
answer-identical (no match, span, or capture changes on any witness
checked). This is the same shape as triaxes's own U2 finding: a ruled,
mechanism-explained change moving witnesses off `run-pinned` by construction,
not a defect.

**One process gap worth naming for the manager, not a reason to treat this
as a regression**: FIND-TIE's own delivery explicitly left the corpus-wide
movers census OWED ("the box was held by land84's chain for this lane's
whole working period"), and land85's later re-run (`7409ee63`) measured
large utf8 mover DELTAS (`ship_weblog` utf8 movers 781->636, `ship_log`
utf8 movers 971->833) but never ran `run_form_census.sh` specifically —
so nobody actually observed the FORM-population consequence this lane
found until now, and FIND-TIE's own "moves only a speed [choice]" framing
is incomplete (it also moves which STRUCTURAL FORM an artifact takes,
which is what tripped this floor). The fix here (re-deriving the floor)
is legitimate regardless; the framing gap is worth a note in a future
review of tie-break changes that feed a cross-module identity check.

## 4. The floor, derived K35-style

Both measurements are real, on trees this lane confirmed:

- **main** (FIND-TIE alone): **117**.
- **combined with U2** (FIND-TIE + U2's own further -4, `[CTX-PREFILTER]`'s
  precondition — the census's own A_CTX-carrying exact DFA machines
  breaking the SAME identity clause a second, independent way): **113**.

K35's convention on this file's own sibling rows: ~85-90% margin, rounded
down generously (`offset-set`'s own 322 -> 290 is 90.1%; the original S1
`150 -> 130` was 86.7%). **100** clears both 117 (85.5%) and 113 (88.5%)
comfortably inside that band and is a round number — the same value
triaxes independently proposed from U2's own tree. `run-pinned-bounded`'s
floor (12) is untouched: its population (14 on this lane's own build, 18
on U2's) still clears it by a wide margin and FIND-TIE's own witnesses show
no `-bounded` mover in the sample checked.

**Applied**: `tests/codegen/run_form_census.sh`'s `run-pinned` floor moved
130 -> 100, with the mechanism (this report's §2, condensed) recorded as a
comment at the site.

## 5. Validation — COMPLETE

- `make -j4 CC=gcc-16` on this worktree — clean build.
- `bash tests/codegen/run_form_census.sh` (this worktree's own build,
  `/tmp/rpfloor_final_census.log`) — **checks passed: 1 / checks failed: 0**,
  `D:RX_DFA_PREFILTER=run-pinned` reads **117** against the new floor of
  **100** (`floor OK`); `run-pinned-bounded` reads 14 against 12 (`floor
  OK`), unchanged.
- The A/B bisection itself (§1, three builds + three censuses) and the
  48-pattern witness diff (§2) were run standalone in the now-removed
  `worktrees/rpfloor-bis` scratch worktree, all logged during this
  session.

No heavy battery (`make test`/`make test-axes` full run) was run here by
design (TRIAGE tier, targeted validation only, per the brief) — the
manager's merge-time full battery is the delivery bar's own remaining
item.

## 6. What is owed

- Nothing outstanding from this lane's own scope. The manager's merge-time
  full battery (`make test-axes` at minimum, to re-confirm the census
  green end to end alongside the rest of the axis sweep).
- Separately (named for the manager, not this lane's fix): FIND-TIE's own
  report should probably gain an addendum noting the FORM-population
  consequence found here, the same way U2's own report got
  `[CTX-PREFILTER]` filed as a follow-up — a future tie-break change
  feeding a cross-module identity clause (any `pf_*_applies_common`-shaped
  predicate) should check the relevant form census, not just the answer
  census, before calling a change "moves only a speed [choice]".
