# possarms21: [ART-POSS-ARMS] revision 2.1 (design + measurement lane)

Lane `possarms21`, opus, 2026-10-07, branch `lane/possarms21` from main
`abb3db6c`. DESIGN + MEASUREMENT only: nothing under `src/`, `cli/`, `lib/` or
`tests/` changed. The prototype is committed as a patch only
(`docs/design/poss_arms_measurements/rev21/proto_rev21.patch`).

**Deliverables**

- `docs/design/poss_arms.md` REVISION 2.1. Edits are marked `[r2.1 <id>]`,
  and §R2.1 is the table.
- `docs/design/poss_arms_measurements/rev21/`: the prototype patch, the
  FROZEN generators, the instruments, the 10.46 transcript, the composition
  hook and `results/`. It has its own CLAUDE.md.
- `docs/dev/plan.md`: the [ART-POSS-ARMS] body is corrected (R-8). The R-7
  re-sweep trigger is added to [UCP] and [CLS-TREE]. [POSS-CTX-TABLE] gains
  the READER field.
- `docs/design/decision_families_survey.md` §3.14: the reader-field finding.

**Where it ran.** The heavy battery ran on the LINUX box (ubuntubudu,
12 cores, libpcre2 **10.46**, so every oracle sweep below is on the
reference), per the manager. Worktrees `possarms21-lx` and `-lx2` were
created there and then removed (see "Box hygiene"). The Mac ran only the
prototype builds, the light probes and the smoke tests.

## Per row: discharged how, evidence

| row | how | evidence |
|---|---|---|
| **N1** | Arm B reads `TEXT_FIRST`, in which a zero-width item is (∅, nullable). The two `first_of` questions are named: POSITION vs TEXT, the READER field of [POSS-CTX-TABLE] (note §2.1, §3.1, §7; plan and survey updated). | 10.46: the three witnesses give (0,3) greedy and NOMATCH possessive. The rev-2.1 prototype answers (0,3) and rev 2's answers NOMATCH. Plant `PROTO_SAB_TEXTPOS` is DETECTED on 4 patterns. Ablation `textpos`: 303+903 claimed, 86+6 diverging. |
| **N2** | Greedy-only is kept and its justification rewritten (note §2.3, §8.4a). Bypass follows and bounded lazy quantifiers were added to the generators. The lazy plant is now a sabotage row (A-lazy, id at build). RC-Q1 is answered NO. | Ablation `lazy`: 3,964 newly claimed, **477 diverging** (+80/26 in B's family). The plant is DETECTED on 5 patterns. 10.46: `(\w+?(?:\b\|))` on `ab` is (0,1). |
| **R-3(b)** | The predicate is FROZEN by sha1, with a post-freeze edit rule. Hand and computed rows are reported separately (note §8.3a). Two rule-level edits were applied under that rule; see below. | `claimmark.out`: AB computed 33,037 compared, 5 mismatches; hand 44, 0 mismatches. |
| **R-4** | The capture fact is indexed and memoized per group number; in-progress means widen; state is on Ctx for one walk. NEW finding: A1's fold was ALSO quadratic. It now uses a Q-independent continuation summary. A build-bar witness cell is specified (note §8.7). | Linux: `Bsame` at 12,800 refs is 40.94 s on rev 2 vs 7.19 s on rev 2.1 (denied: 7.40 s). `A1alt` at 6,400 is 100.15 s vs 1.36 s (denied: 1.35 s). |
| **R-5** | A1 ≡ FOLLOW as an always-on house-form check over the summary. An atomic-end sentinel was added. | Census: 5,437/5,437 verdicts eq, 0 summary/fold mismatches. |
| **R-6** | A tripwire is designed: `reject_engine_dfa_bref_nocaptures` in `tests/reject/`. | `--engine=dfa --no-captures '(a)x+\1'` is refused today, armed and denied. |
| **R-7** | Per-quantifier marks come from `--emit-ir` strategies, keyed by ordinal. `UCP_PIN`=4,502. The trigger is added to the [UCP] and [CLS-TREE] rows. | `r21_claimmark.py` |
| **R-8** | The plan row body is corrected. | `plan.md` |
| **R-3(a) hook** | `rev21/run_composition.sh` (note §8.8). | Smoke test: 0 divergences armed; the N1 plant is reported as a divergence on both routes. |

**Other battery results (Linux, 10.46)**

- Claims are oracle-clean after the edits:
  - arm A: 11,800 claimed, 0 diverging;
  - A0: 7,614 claimed, 0 diverging;
  - B: 1,905 claimed, 0 diverging.
- Exhaustive possdiff: 104 patterns agree, 517,382 cells, reach 15/15. Every
  plant is DETECTED.
- Extra-mark possdiff: 676 patterns, 0 diverging, 7.57 M cells.
- Census: unchanged from rev 2. The arms fire on 6 bench / 13 corpus
  patterns, with 0 engine flips and a 0 mark delta from rev 2. No corpus
  pattern has N1's shape.

## The post-freeze predicate edits — the manager's four conditions, per category

The first run against the freeze (sha1s in note §8.3a) disagreed on 2,815
rows. Every disagreement traced to the EXPECTATION model; none traced to a
pcrec mark.

1. **Exact-count rows (2,047).**
   - *Direction:* none. The CLAIM is unchanged; only the comparison changed.
   - *What they are (condition 2):* the base build with the arms DENIED
     already marks these rows (the shipped ladder's row 1). So the possessive
     spelling flips nothing, and the target reads `base-marked`.
   - *Fix:* the comparison now treats MARK as the target's state, not a flip.
2. **R-block `hi` (745 rows).**
   - 520 rows move FEWER (pcrec declines by representation).
   - 225 rows move MORE.
   - *Oracle (condition 1):* the libpcre2 10.46 sweep over exactly those 225
     rows gives **225/225 agree, 0 diverging, 2,522,475 subjects**.
3. **A0 LAST position class (18 rows).**
   - *Direction:* FEWER.
   - *Basis:* this is the semantics statement in the note's own rule (§2.3
     already says "classes at Glushkov LAST positions").
   - *Oracle (condition 4):* **18/18 agree** on 10.46 (134,658 subjects).
4. **Unresolved targets (5 rows).**
   - *What they are (condition 3):* each target body is emitted twice, so the
     possessive spelling flips two ordinals and the target is unresolved.
   - The arms mark a DIFFERENT quantifier: `(?:(?=C)[ab])+`, whose body can
     never match.
   - These 5, and all 657 extra flips, are checked by the exhaustive possdiff:
     676 patterns, 0 diverging, 7.57 M cells.
   - Still **OPEN** as an instrument item: replicated copies should be keyed
     as one target.
5. **Edit 2, found by the oracle sweep.**
   - The frozen R block omitted `fold_ref`, so it CLAIMED 14 rows that
     10.46 refutes.
   - pcrec DECLINED all 14.
   - The edit narrows 48 claims (FEWER): 14 refuted, 34 sound.

## OWED

- **R-4 timing:** the `A1alt` n=12,800 rev-2.1 columns and the whole `A1lb`
  family. Linux timing was stopped at the manager's wrap-up. Rerun with
  `PROTO=… PROTO2=… TIMEOUT=gnutimeout rev21/timing_r4.sh`.
- **Instrument:** key replicated quantifier copies as one target in
  `r21_claimmark.py` (the 5 unresolved rows).
- **The note:** §8.7's R-4 table rows marked OWED; the old §8.2 S-id
  paragraph was fixed at the possland landing (no plant carries S567/S568;
  ids are taken at build, the reserved S560-S565 block holds six of ten rows).
- **Not this lane's:** R-3(a) (the blinded corpus, via `run_composition.sh`),
  R-3(c), R-9.

## Process notes (my errors)

- The first Linux run built an early patch snapshot without A1's summary.
  It was rebuilt in phase 2, and the semantics were verified equal by the
  census R4SUM check.
- eqcheck shards were OOM-killed; the sweep is now chunked at 200 rows per
  process.
- I missed two background completion notices.

## Box hygiene

- `worktrees/possarms21-lx` and `-lx2`, the bundle and the build logs were
  removed on ubuntubudu, `git worktree prune` was run, and the chain was
  safekilled.
- Mac: the scratch tree `worktrees/possarms21-scratch/` (gitignored) remains.

