# Lane spanarms — report

Lane spanarms (opus, 2026-11-08), branch `lane/spanarms`, base main `7b9ddd890`. Design and
single-pattern measurement only (no build go; nothing under `src/`, `cli/`, `lib/`, `memfn/`,
`tests/` edited). Deliverable: `docs/design/span_arms.md` (PROPOSED rev 0). Evidence:
`docs/dev/lanes/spanarms_evidence/` (`probe.sh` and its `*.out` over the lane's own
`nice make -j2 build/pcrec` of the base; `oracle.out` from libpcre2-8 10.46 through
`tests/lib/p2probe.c`; `owner_rep.out`).

## Summary

The note designs the three arms alt_normal_form left as follow-ups (§3.5 table, §3.6, §9 S2-S4),
each as ONE rule that is a language identity, so its soundness is the existing CAT arm's:

- **REP**: `X{m,n}` = `X^m · X{0,n−m}` (head, best) = `X{0,n−m} · X^m` (tail); `X^m` unrolled
  through `rr_cat` to a saturation DERIVED from `PCREC_MAX_REQ_RUN_SCAN` (2 copies for a non-`all`
  body, `ceil(32/w)+1` for an `all` one); no new limits row.
- **EMPTY**: every node that consumes nothing is CAT's width-0 unit, EXACT if it cannot fail,
  GUARDED if it can; the run joins across both, the rewrite owner across EXACT only (its head
  already reads through zero-width nodes).
- **positive LOOKAROUND**: a guarded unit plus a GUARD (lookahead body's fixed head at `[0,h)`,
  lookbehind body's fixed tail at `[-t,0)`), intersecting overlapped consumed positions and
  extending past them; a run gains a REACH `(back, ahead)`, the walk takes the admitted reach as a
  parameter (as it takes `pos_set`), one fact raised for every reader together.

Premise tests all HOLD at `7b9ddd890` (note §0): `rb_rep_into` (`req.c:549-558`) keeps only the
body's best and sets `pd_none`; `A_LOOK` (`req.c:761`) cuts through `rb_row_into` →
`rb_assert_into` (`:627-645`). Two findings beyond the brief: stage 2a (the EMPTY arm's direct
half) is itself unbuilt (`A_EMPTY` is in the same cut list, `:756`), and the SPAN facts already see
through repeats (`span_facts` gives `A{4}` as `4:65,65,65,65`): [REPEAT-RUN]'s span half is
already true, only the run half is not.

The window site today (D172): span starts are admitted in `[-8, 64)` (`memfn.h:235`, `:586-591`,
checked `memfn_sites.c:587-592`), but pcrec states only two negative starts, both `-1` (MLINE's
`{-1:\n}`, `emit_dfa.c:8393`/`:6909`; the cover site's `ctx_before`, `known.c:465`, a machine
fact); R never starts below 0 (`walk_proves`, `emit_dfa.c:6809`); no lookbehind body's bytes are
stated anywhere. The presence statement is stricter: the kit REFUSES a negative `omin`
(`memfn.h:679-684`).

The reader census (note §5.4, by grep; a delegated census agent did not deliver and was not
used): 7 assumption rows over every accessor reader (all in `emit_dfa.c` plus `kset.c`'s pin).
AHEAD needs no reader code (a spec hunk, match_api.md §6.3.7¶4/¶6, and a kit doc sentence); BACK
needs four changes: the kit's negative `omin`, the handoff's re-entry floor (`emit_dfa.c:1524-1529`),
the landmark K's `-1` sentinel split (`facts.h:566-573`, declined at `emit_dfa.c:8835`; a back-1
run's K would collide with it exactly), and signed set offsets (`RbSet.off` is `uint32_t`,
`facts_derive.h:78`).

## Arms designed

| arm | rule | owner (at `7b9ddd890`) | predicted movers (measured spellings) | unit |
|---|---|---|---|---|
| REP | two decompositions, `X^m` through CAT, derived saturation | `req.c` `A_REP` arm `:708-740` + `rb_rep_into` `:549-558`; a power combinator in `desc.c` | `xy(?:ab){2}zw` 2 → 8; `A{4}` none → 4; `ab{3}c` none → 5; `(?i)xy(?:ab){2}zw` none → 8 cube positions; `abcd(?:ab\|Ab){2}efgh` 4 → 12; `xy(?:ab){2,3}zw` 2 → 6 | R1; the owner's REP head (`altnf.c:223-230`) is R2 |
| EMPTY | width-0 group = CAT's unit, EXACT/GUARDED | `req.c` cut list `:756-771`, `rb_row_into` `:637-645`; kind row untouched | `abcd(?:)*efgh`, `abcd(?:){3}efgh` 4 → 8 (E1); `xyz(?<=yz)abc` 3 → 6, `x(?!ab)ac` 2 → 3 (E2) | E1 (with 2a), E2 |
| LOOKAROUND (positive) | guard + reach, INSIDE / AHEAD / BACK rows | `req.c` `case A_LOOK` `:761`, `rr_cat` `:450-468`, the walk's signature `:789` | `a(?=b)[bc]` none → `ab`; `a(?=bc)bc` 2 → 3 (INSIDE); `bar(?=baz)` → `barbaz` ahead 3; `(?<=foo)bar` → `foobar` back 3; `(?<=ab\|b)c` none → `bc` back 1 | L1, L2, L3 |

Answer identity: every arm states a necessary condition (alt_normal_form §8a C1, facts are
order-free); a wrong run comes only from a wrong decomposition, which the witnesses plant.

## Decisions as tables

All first-match, in the note's §6: T1 the arm table (node class → consumed part, guard part);
T2 the REP rows (width-0 body → unit; m = 0 → gap; m = n → `X^c`; else the two decompositions);
T3 the zero-width rows E-1..E-5; T4 the guard placement rows (INSIDE, AHEAD, BACK; empty
intersection → the "cannot match" fact); T5 the reader admission rows (§5.4, A1-A7); T6 the units
and triggers (§8). Deny levers: no public bit; alt_normal_form §11's one harness-only lever becomes
one lever with an arm set (`alt`, `empty`, `rep`, `guard`, `look`), built by whichever unit lands
first. Proposed D-next text in note §12.

Units (note §8), each triggered by a named census (D77): E1 (exact width-0 units through REP,
with or after 2a), R1 (the power arm), E2 (guarded units), L1 (INSIDE, reach (0,0)), L2 (AHEAD:
spec hunk + kit doc line), L3 (BACK: A1-A4 + the kit's negative `omin`, at most `MF_MAX_BACK`),
R2 (the owner's REP head; measured `(?:ab|ax{2}|ad)` `RX_ALTCLS_MERGES` 0 vs 1 spelled).

## Witnesses

Every expected answer is libpcre2's (`oracle.out`); every correct run is measured today or by
its spelling.

| id | planted error | pattern on subject, expected | why it can fail |
|---|---|---|---|
| W-R1 | `all` at m < n | `xy(?:ab){1,2}zw` on `xyababzw`, (0,8) | sabotaged `xyabzw` absent: NOMATCH |
| W-R2 | unroll n copies, not m | `xy(?:ab){1,3}zw` on `xyabzw`, (0,6) | `xyabab..` absent |
| W-R3 | min-0 walked as m ≥ 1 | `ab(?:cd){0,2}ef` on `abef`, (0,4) | `abcd` absent (on `abcdef` it is present: not a witness) |
| W-R4 | width-0 test reads min width | `ab(?:c?){2}de` on `abcde`, (0,5) | `abde` absent |
| W-R5 | saturation one copy short | `(?:abc){20}` | FACT witness only (a shorter run is sound) |
| S-g (parent) | `A_BREF` sent to the EMPTY arm | `(ab)x\1y` on `abxaby`, (0,6) | `abxy` absent |
| W-E1 | a negative body read as a guard | `x(?!ab)ac` on `xac`, (0,3) | empty intersection claims "cannot match" |
| S-L (parent) | lookbehind body read as consumed | `(?<=foo)bar` on `foobar` from 3, (3,6) | `foobar@0` from 3 absent |
| W-L1 | the scan not stepped back | `(?<=foo)bar` from 3 / 2 / 4: (3,6) / (3,6) / NOMATCH | a scan from 3 misses `foobar` |
| W-L2 | guard extension leaves `all` true | `(?:(?=abcd)ab)cd` on `abcd`, (0,4) | `abcdcd` absent |
| W-L3 | variable tail from the first branch | `(?<=ab\|b)c` on `xbc`, (2,3) | `abc` absent |
| W-L4 | AHEAD leaked at reach (0,0) | `bar(?=baz)` | FACT witness only: no reader at the base assumes the run ends by the match end |

## Open questions for Frank

In plain words with leanings (note §13): (1) count a repeat as its copies for the run — yes, unit
R1 on its census; (2) stop cutting at `\b`, `$`, `\K`, negative lookarounds — count first (E2);
(3) a run reaching outside the match: one value raised for every reader together, or a second wider
fact — one value (no parallel mechanism); (4) the `_REQ_RUN` stamp's "every match must contain"
sentence — widen it at L2, leave a new stamp spelling to the interface push; (5) lookbehinds over 8
bytes stay inside-the-match runs unless the BACK census asks the kit to lift its bound; (6)
[REWRITE-ADJ] design may start once this note is ruled, not after its units are built.

## STATE AT HANDOFF

STATE: delivered (design complete; no build). Commits on `lane/spanarms`: the WIP commits
`30143f390`, `fe2fdb8e8` and the delivery commit carrying this report. Rulings file
`docs/dev/lanes/spanarms_rulings.md`: empty at every re-read (before each commit and before this
report); last entry applied: none. Validation: none owed (design lane; no suite run, per the
brief); the measurements are single-pattern compiles with the lane's own build of `7b9ddd890`
(`build.log` in the lane scratch, rc 0) and libpcre2 probes. Next: a critic round on the note
(design) before any unit's census lane; each unit's census is its trigger. Notes for the
manager: (a) the reader census was done by the lane directly (the delegated agent produced no
report); (b) the docs/design/CLAUDE.md index had 23 bytes of headroom, so the new note was folded
into the `alt_normal_form.md` line (its "lane altrev2, after re-check r4" history words dropped).
