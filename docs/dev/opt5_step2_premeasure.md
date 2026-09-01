# [OPT-5] STEP 2 pre-panel measurement — the three numbers §7 owes

Lane `opt5m2`, 2026-09-01. Measurement only: nothing under `src/`/`tests/`
lands from this lane; `src/gen/emit_dfa.c`'s `[OPT5M2-PROBE]` block is a
measurement-only stamp (`RX_PROBE_PINNED`), kept only for this lane's own
sweeps and not proposed for merge. Answers `docs/design/opt5_step2_twopass.md`
(lane `opt5d`) §7 items 1-3.

(WIP — M1 done, M2/M3 in progress; this file is updated as each lands.)

## M1 — N_pinned (§7 item 1)

**MEASURED.** Population: 2,845 distinct `pattern` lines under `tests/`
(`grep -rhE '^pattern ' tests | sed 's/^pattern //' | LC_ALL=C sort -u`,
floor 2,620 — the standing census rule). Default (auto) engine, `--features
all`.

Command (per pattern): `pcrec_run build/pcrec --features all -p rx -o a.c --
'<pattern>'`, reading `RX_ENGINE` and a measurement-only `RX_PROBE_PINNED`
stamp added to `pcrec_emit_dfa_scan_stamps` in this lane's own worktree
(never proposed for merge). The stamp evaluates the design note's P1+P2 for
the forward machine's start state — `member_ok`'s own body
(`src/opt/scanedge.c:188-194`) plus the base accept bit, copied verbatim
rather than re-derived — and P3 over the live seed states when
`dfa_needs_seed` holds, at the exact point `unanch_start`'s own `start_acc`
is computed a few lines above in the same file.

```
ENGINE totals:        1492 vm / 1060 dfa / 293 refused
DFA-scan totals:       1872 unanchored / 357 attempt / 8 empty / 315 none (plain VM)
PIN totals:            1642 notacc / 175 yes / 47 view / 8 classctx  (N/A: 680 = 357 attempt + 8 empty + 315 no-scan)
PIN=yes among hybrids (ENG=vm):    0
PIN=yes among pure DFA (ENG=dfa):  175
```

**N_pinned = 175**, all of it DFA artifacts, **0 among VM hybrids** — matching
§1.2's own prediction exactly ("in practice the hybrid ∩ start-pinned
population should be at or near zero", because a start-accepting machine gets
no candidate prefilter and a hybrid only exists where a prefilter was built).
175 is comfortably non-vacuous (9.35% of the 1,872-artifact `unanchored`
population the predicate is even asked of), which is what the note's §7 item 1
trigger required before the panel.

Top decline reasons, of the 1,697 unanchored artifacts the predicate refuses:

| reason | count | share of declines | meaning |
|---|---|---|---|
| `notacc` | 1,642 | 96.8% | start state does not accept at all (not nullable) — the overwhelming default case |
| `view` | 47 | 2.8% | start state accepts only under an EOL/END view (the `$` shape, F3's counter-example class) |
| `classctx` | 8 | 0.5% | start state's accept varies by class context (the `\b`/`(?m)` shape) |

No artifact was declined at the **seed** stage (P3) — every pattern whose
`fs` already passed P1+P2 also had every live seed state pass, where
`dfa_needs_seed` applied. Read conservatively: this corpus's fseed-needing
patterns and its nullable-start patterns barely overlap, not that P3 is
provably redundant — a synthetic witness would be needed to be sure the
seed conjunct is reachable at all, and this lane did not build one (out of
scope: this is a census, not a check).

Sanity probes (hand patterns, not part of the census): `a*` -> `yes`;
`$` -> `view` (the design's own named counter-example, F3); `\bx*` ->
`classctx`; `abc` -> `notacc`.

## M2 — N_declined_by_view at today's tree (§7 item 2)

(running — see below for a methodology defect found and fixed before the
real sweep)

**A first attempt over-counted by roughly 100x on a spurious signal, caught
before it was reported.** The scratch narrowed variant (`unanch_start`'s
`start_acc` narrowed from `state_acc_any(&fd->st[fs])` to the view-strict
`fd->st[fs].up[UPC_PLAIN].accept` — and the matching seed-loop narrowing —
the wave C edit, applied via `git archive HEAD | tar -x` into a scratch copy,
never committed) was diffed against the baseline using DIFFERENT `-o`
basenames per side (`a.c` vs `b.c`). `pcrec` derives an `#include
"<basename>.h"` from the output filename, so EVERY artifact differed by that
one line regardless of `start_acc` — 188/200 patterns "changed" in the first
200, an order of magnitude over wave C's ~21-artifact scale, which is what
flagged it as wrong rather than a real number. Confirmed directly: diffing
two `abc` artifacts built with `-o a.c` / `-o b.c` differs ONLY in the
`#include` line. Fixed by using the SAME basename (`art.c`) in two separate
directories. Re-verified on two controls before the real sweep: `abc`
(non-nullable start) — identical, as expected, since `start_acc` cannot
matter when the state doesn't accept at all; `\bx*` — **also identical**,
which is itself informative: `\bx*`'s widened/narrowed `start_acc` values
genuinely differ (word-context accept vs plain-view accept), but `cand.usable`
is false for it (no proper byte subset to filter on), so `!start_acc &&
o->cand.usable` never both hold and the emitted `RX_DFA_PREFILTER` stays
`"none"` either way — reproducing wave C's own finding in `src/gen/CLAUDE.md`
that "§3.6.1's `\bx*` prediction is false."

## M3 — which precondition declines `(?:[a-z]{0,2048})\z` (§7 item 3)

**MEASURED**, static reading confirmed by one discriminating probe pair.
`\z` forces an END view (`endvar >= 0`) onto every state in the counted
`[a-z]{0,2048}` chain, since each such state's accept depends on whether
`pos == n`. `src/opt/scanedge.c`'s `member_ok` (line 190) checks
`st->endvar >= 0` FIRST, before the class-context loop, so **precondition
(3)** ("NO POSITION VIEW ON ANY MEMBER") is what refuses every member —
never reaching precondition (2)'s class-context check.

```
$ build/pcrec --features all -p rx -o m3a.c -- '(?:[a-z]{0,2048})\z'
#define RX_DFA_SCAN_EDGE "none"
#define RX_DFA_PREFILTER "byte-class-bounded"

$ build/pcrec --features all -p rx -o m3b.c -- '(?:[a-z]{0,2048})'
#define RX_DFA_SCAN_EDGE "range"
#define RX_DFA_PREFILTER "none"
```

Removing `\z` alone (same skeleton, no other change) flips `RX_DFA_SCAN_EDGE`
from `"none"` to `"range"` — the discriminating pair the brief asked for.
Confirms both the design note's own §2 item 1 INFERRED claim and the
manager's observed `RX_DFA_SCAN_EDGE "none"`: precondition (3), not (1) or
(2), is what declines the whole form.
