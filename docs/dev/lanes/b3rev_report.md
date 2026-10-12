# b3rev — B3 revised into a build-ready design: tag only where the artifact can tie

Lane b3rev, 2026-10-12, main `e8ca12523` (abi 76), Linux dev box (7700X, gcc 15.2). No `src/` change.
Design: `docs/design/endmark.md` §R (its §R.0 maps every panel finding S1-S10/C1-C8 to a section).
Evidence: `docs/design/endmark/b3rev/` (probe, driver, results) and `b3rev/timing/` (the clock, a sub-lane).

## The design in one table (§R.1)
F0 `denied` (new deny `-fno-rev-end-onewalk`, bit 55) | F1 `one-seed`: `nl_last` false, one seed chosen by
the last byte plus a zero-length probe at `n` — **223 of 266** | F2 `tagged`: the tie fact (some tagged state
carries two distances under some context atom, the absent atom included) and every lowered machine fits —
**43** (bench 1) | F3 `two-seed`: can consume a final newline, cannot tie (`a\n$`) — 0 shipped, 3 witnesses |
F4 `overflow`: decline to today's. Fixes: S1 by making `$`'s lowering an NFA-build PARAMETER (one tree; F2
builds forward, reverse and anchored lowered; `end_pin` keeps one answer, `eol`); S3 by making the accept value
the distance set (four COMPARE sites compare values: minimize.c:133, scanedge.c:287, dfa.c:1204,
emit_dfa.c:3992; byte-identical on 0/1 machines); S4 by optional builds + a `fit_rungs[]` row `drop-end-mark`;
S5 unmarked arms carry d = 0; S6 the VM keeps the `$` assertion (a reading of add. 4, Q3); S7 `mark_prio`
measured; S9 the tail from `\Z`'s definitions row; S10 leaning yes: the accept-value set is the one EndDist
representation and `mark_prio` is FINISH row `prio-const`.

## Measured (every count pcrec's own machines; 13 controls, all equal except named ctx/one-off rows)
- **Tagged reverse after scan-edge (C4's spike):** F2 151 -> 281 states (1.86x, max 2.75x, +7 max); the pass
  compacts nothing on the tagged set (281 -> 281). Over 2x+1: `[^c]{0,4}?$`, `[^c]{0,4}$` (the exemptions).
- **Add. 4 forward/anchored growth (F2 only):** forward 216 -> 290 (+34%, max +3/machine), anchored 163 -> 215
  (+32%, max +6); the tag adds no forward/anchored state (Moore with `back` == untagged, 220/220).
  Time from s*: verify-at today/lowered **1.09-1.31x** (lowered FASTER), relocate 0.97-1.07x (A/A 0.87-1.20);
  782 subjects x 6 arms answer-checked vs libpcre2 10.46 and today, 0 wrong.
- **mark_prio (S7):** const0 28, const1 10, ctx-unmodelled 5, state-dependent 0; cost 230 unpruned states in
  total, median 4, max 39.
- **N-sweep (C2):** linear in N in all four families (no |Q|^2); the tag never outgrows today's forward
  machine (no state-cap event), but it defeats scan-edge: `\s{0,N}$` 4 -> 2N+3 states (a byte-cap event).
- **Refusal set (C3; plain/lowsize/lowboth, 360 keys each):** +0 with the declines; without them +10 plain
  (sweep N >= 3072-6144, `((a)|bc){0,4000}d\s*$`, four utf8 `\p{L}...\s*$`), +0 lowsize/lowboth.
- **[REVEND-WALK-FORM] decided:** the whole T/R style gap (1.22-1.60x) is the per-iteration view probe
  (V/R 1.30-1.71x, T/V 0.92-0.96, +0.93 ns per CALL, per-load cost unchanged); the build takes form W (seed
  views resolved before the loop, first step peeled): T/W 1.47-1.90x; U (one seed in today's text) /T
  0.67-0.73 on newline-terminated cells. 0 wrong over 90,962,254 cells, every arm.
- Cells per class (C1): F2 nl-m 0.37-0.38x of today, nonl 0.66-0.76x; F1 0.67-0.73x nl, 0.92-1.00x nonl.

## Owed, open, requested
- **Sabotage ids: please issue a range of 10** (plants P1-P10, §R.7.2; none invented).
- Q1-Q4 for Frank (§R.9): the deny bit; selective tagging deletes nothing; the VM reading of add. 4;
  file `[REVBLOCK-VIEW]` (the same ~1 ns/call view probe sits in every composite's reverse pass).
- For main to file: `[REVEND-WALK-FORM]` answered (form W); `[REVBLOCK-VIEW]` as above.
- Not modelled by the probe: forward/anchored tagged figures and `mark_prio` on the 5 context-atom F2
  artifacts (owed to the build's census check); bytes are predictions (gate G3 measures at build).
- The timing sub-lane delivered its files and report.txt but no closing message; its numbers above are read
  from `b3rev/timing/results/report.txt` (run2, cross-checked against run1).

## Re-run
`b3rev.py census|sweep|refusal` (env in its header; census ~4 min, refusal ~25 min at JOBS=6);
timing: `b3rev/timing/CLAUDE.md`.
