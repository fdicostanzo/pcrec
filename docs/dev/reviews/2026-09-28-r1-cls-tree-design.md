# r1 — [CLS-TREE] design note, light D6 panel (2026-09-28)

Target: `docs/design/cls_tree_design.md` at `8d8933a0` (lane clsdes88).
Two read-only critics (sonnet). They never ran make and wrote nothing.

- **(i) semantics**: engine correctness seams against PCRE2 (UTF-8 ill-formed
  input, caseless, UCP, the splice).
- **(ii) measurement/altitude**: re-derived every cited number from the
  committed TSVs, plus the general-mechanism, D77 and check-design lenses.

**Verdict: no BLOCKER.** Critic (i) found no correctness defect. Two
MUST-FIX and four SHOULD/NIT findings from critic (ii) concern the note's
numbers and sourcing, and all are fixed. Every fix is marked `[r1 <ID>]` in
the note.

## Findings and dispositions

| ID | sev | finding | disposition |
|---|---|---|---|
| SEM-1 | SHOULD | `-Wswitch` makes each of the 49 `case A_CLASS` sites + 6 comparisons get TOUCHED. It does not make their handling of `A_WCLASS` RIGHT, so CT-4's safety is BELIEVED until the census exists | **ACCEPTED.** §7 a2 now requires, for every "reads bytes" site, what `A_WCLASS` must answer (width, count, first-unit set), spelled out before S3 merges |
| SEM-2 | SHOULD | §9 asserts that `back_step + decode + kit` supplies UCP `\b`'s parts. Only `back_step(k=1)` itself is verified; the composition against PCRE2 is not measured | **ACCEPTED.** §9 gains a status line saying so, and UCP's design owns the differential |
| MEAS-1 | MUST-FIX | The 28-set kit subtotal was 58,466, and the committed file gives **58,038** (+3.4%, not +2.6%) | **ACCEPTED and root-caused.** This lane's sum was keyed on set NAME, and two uprops sets share a name (27 unique names in 28 rows), so one set was double-counted. Corrected in §1.3 |
| MEAS-2 | MUST-FIX | `^C` on member subjects is bimodal in the ubuntubudu run, in lockstep across all arms (`bitmap1` 1.60 vs 13.30 ns). The note did not disclose this | **ACCEPTED.** It is disclosed in §1.2, and every statistic was recomputed with `^C` dropped: member r = +0.06, 16/33, geomeans 0.113/0.409/0.467. The conclusions are unchanged. b1 re-measures the cell |
| MEAS-3 | SHOULD | The "reversed forward automaton" fan-out (270) could not be reproduced from any committed script | **ACCEPTED.** `automaton.py` gains `sink_indegree` → the `revfwd_root_fanout` column. `results/automaton_k53.tsv` was regenerated and reproduces 270 |
| MEAS-4 | SHOULD | TS = 10 rested on an uncommitted sweep | **ACCEPTED.** `python3 wholeset.py k53` → `results/page3_ts_k53.tsv` is committed, and it reproduces the cited ranges |
| ALT-1 | SHOULD | "the kit closes to within ~11%" (ascii) held only at λ0. At λ16 the gap is +15% and at λ256 +17% | **ACCEPTED.** The sentence now states 11-17% with all three medians |
| ALT-3 | NIT | The note does not say how a whole-set section enters a DP whose window is ≤ 64 intervals | **ACCEPTED.** §1.3 now says it is compared at `best[n]` as a one-section alternative, and that S1 may generalise it to a table section over any run |
| NIT (loadavg) | NIT | `bench.py`'s gate reaches `os.getloadavg()` on Linux only through the sysctl branch's exception handler | **ACCEPTED.** `os.getloadavg()` is now tried first, so the gate semantics are unchanged |

## Verified correct by the panel (not re-litigated)

- **Critic (i)**: `$_span_ci_decode` and the `u8_box`/`u8_ranges` automaton
  reject the same ill-formed set, covering truncation, stray continuation,
  every overlong lead range, surrogates, > U+10FFFF and F5-FF. The critic
  found no divergent subject. Surrogates in complemented sets are
  unreachable on both routes. `pcrec_lower_enc` runs after `postresolve`, so
  lookbehind width analysis never sees a lowered class. The byte backend
  never produces `A_WCLASS`. Caseless closure is orbit-based, which covers
  the k/K/KELVIN case. The flat alternation's branches are pairwise
  disjoint, so the minimal-automaton splice loses no priority information,
  and isomorphism is the right gate.
- **Critic (ii)**: the timefit table (every r, ρ, pairwise count and
  geomean) reproduced exactly. So did every cell of §1.3's K53 table, the
  population totals (114,609 / 85,613 / 84,106), the λ constants, and the
  K53/K55/K67/D77/D103 citations. The b1 brief's target and flags produce
  4,620 rows as stated.

## Reflection

The one wrong number was a derived subtotal, and its cause was a join key
(a set name) that is not unique in the population. This is the same class
of mistake as the study's own §8 pricing bug, where a number was computed
one way and checked another. The number was caught only because a critic
recomputed it from the committed file rather than from the lane's script.
The bimodal `^C` cell had sat in a committed TSV since 2026-09-11. No
document had looked at per-round spread until a critic did.
