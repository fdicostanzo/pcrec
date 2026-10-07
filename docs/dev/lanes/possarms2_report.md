# possarms2 — [ART-POSS-ARMS] revision 2 (design + measurement lane)

Lane `possarms2`, opus, 2026-10-07, branch `lane/possarms2` from main
`c2a0c6df`. DESIGN + MEASUREMENT only: nothing under `src/`, `cli/`,
`lib/` or `tests/` changed. The prototype lives in a scratch copy and is
committed only as a patch.

**Deliverables**

- `docs/design/poss_arms.md`: REVISION 2. Every disposition is applied in
  place and marked `[r2 <id>]`, and §R2 is the table.
- `docs/design/poss_arms_measurements/rev2/`: every instrument and result,
  with its own CLAUDE.md. The parent CLAUDE.md points to it.
- `docs/dev/plan.md`: the [ART-POSS-ARMS] row is updated, and
  **[POSS-CTX-TABLE] is FILED** (under [OPTLOOP] candidates per D137,
  UNSCHEDULED).
- `docs/design/decision_families_survey.md`: family 14, §3.14 and a §6
  entry.
- `docs/design/CLAUDE.md`: the poss_arms entry, revised.

**Validation.** Every measurement below ran to completion, so none is owed.
`make test` was not run, as is right for a design lane: no shipping code
changed. The heavy sweeps ran under `worktrees/.mac-suite.lock`, which has
been released. ubuntubudu was used for ONE light pcre2test session
(`rev2/witnesses_r2_10.46.out`).

## Per review row: how it was discharged

| row | discharged how | evidence |
|---|---|---|
| **A-F1** BLOCKER | Fix (a) is implemented in the prototype. A1's continuation carries a marker at every `A_CAP` end; at a marker, and at the root end, it unions `cc[g].follow ∪ cc[g].encl` (A0-valued; `cc` never holds an A1 value). Both witnesses decline. They are possdiff patterns, CLAIM-vs-MARK rows and a sabotage plant (`PROTO_A1_NOCC`, DETECTED). Their `.rxt` cells are owed by the build | note §2.3a; `pdx/plant_A1_NOCC.log` (3 diverge); census `vm_ABnocc` |
| **C-2** HIGH | Option (b): a joined context supplies the P = {0,1} component only. Three reasons: it is sound (Q(P) ⊆ Q({0,1})); the triple is ill-defined (P is relative to ONE gate set C, while a continuation holds gates over several sets); its measured gain is 0 (below) | note §2.3a |
| **C-1 / B-M1** HIGH | ROUTE-FLIP CENSUS: **0 of 4,132** change default engine. **186** at risk (VM-forced by an atomic group or possessive suffix; 117 in tests/atomic_groups). Both engines are recorded per pattern. Six constructed witnesses do flip, and their DFA answers equal the VM-denied build's on the exhaustive sweep. A's bit is ENGINE-SELECTING (`kept`), with an `--engine=dfa` refusal witness and spec sentences | note §5.4, §9; `census_r2.tsv.gz`, `routeflip_witness.out`, `pdx/routeflip_default.log` |
| **B-B1** BLOCKER | EXHAUSTIVE-SUBJECT possdiff (`subjects_exh.py` + `possdiff_exh.sh`): length ≤ 4, case-flip-closed alphabet + word/non-word reps, code points under `-e utf8`, a `# flags:` header, and a REACH check (11/11). **Arms: 79 agree, 0 diverge, 403,943 cells.** All SIX plants S560-S565 DETECTED (2/3/1/1/2/2 patterns), plus A-F1 (3) and the depth-1 termination plant (compiler SEGV on 3 patterns). The lazy control is NOT detected, which is consistent with the ablation | note §8.1, §8.2; `pdx_verdicts.txt`, `pdx/` |
| **B-B2** BLOCKER | CLAIM-vs-MARK (`r2_claimmark.py`) over every claimed row, every ablation-tagged row and a 1-in-10 sample: **10,315 compared, 0 mismatches**. Every plant is detected without subjects (2,345 / 1,197 / 432 / 1 / 2 / 33 / 3 newly mismatched rows). The mixed-LAST body is added to the generator. Its first run found 25 disagreements, ALL in the independent predicate (below) | note §8.3; `claimmark.out.gz`, `claimmark_v1.out.gz` |
| **B-B3** BLOCKER | ABLATION TABLE at ML ≥ 4. Diverging/newly-claimed per conjunct: m ≥ 1 996/2,268; LAST polarity 338/1,314; mixed LAST 168/504; ENCL 3/2,272 (after adding bypass rows, below); call-site join 4/4; B fold 2/2, all refs 2/2, all A_CAP 1/1, nullability 12/12, ACCEPT 1/1, unset 1/1. **Greedy-only: 0/1,134**. The depth-1 witness `(a\2)(b\1)x+\1` is claimed, compiles and does not diverge; its plant hangs the compiler | note §8.4; `a2_abl_ml4.out.gz`, `a2_new_ml4.out`, `b2_ml5.out` |
| **B-M2** MAJOR | Designed: the `<PREFIX>_VM_POSS_ARMS` bitmask stamp (A0/A1/B bits; do-or-die on the artifact), a `poss-arms-moved` bucket in run_recursion_identity.sh (A) with stamp-or-deny and a named-manifest floor, and `emit_sweep.py --ref` with movers = manifest by id, 0 off-diagonal | note §8.5 (build-time) |
| **B-M3** MAJOR | The subject generator is COMMITTED (`wb_subject.py`, deterministic, 809 B, sha1 bc1608f6…), with a bisector that FAILS LOUDLY (`minwb2.sh`). ONE re-measurement: **denied 394 → arms 1,199 = user-written possessive 1,199** (A alone 998, B alone 595). The design reuses run_axes' GIVEUP1 classifier and allowance, `outcome_word.h` in possdiff_driver.c, and a fourth GIVEUP→GIVEUP class | note §6, §8.6; `wb_runs.tsv` |
| **B-M4** MAJOR | A0 FAMILY SWEEP (`gen_a0.py`, 8,064 pairs, ML=4): **3,000 claimed, 0 diverging; 2,117 non-claimed diverge**. Claims exist in every position named (direct, alternation, quantified group, gate in body, lookbehind, enclosing loop), including 552 lazy and 552 m = 0 rows. Denominator: 4,132, of which 393 are refused, with the list committed. A deny-delta re-count at build is specified | note §5.1, §5.3, §8.6; `a0_ml4.out.gz`, `census_r2_refused.tsv` |
| **A-F3** LOW | Rule stated and prototyped (`px_S`): Q(P) non-empty and S empty → widen. Truncation is exact against every compared set otherwise. It replaces the "FIRST(X) ≤ 0xFF" conjunct, which it subsumes. Unreachable today via `ctxnode.c`'s `t3_ctx_applies` | note §2.1 |
| **A-F4** LOW | The prototype's rule is adopted: narrowed gates are non-nullable. The reason: every reader asks about a retreat exit, which has a right-hand character. It is also today's nullability, byte-identical. Measured delta against rev-1's prose rule: 0 of 4,132 | note §2.1; census `vm_ABa0null` |
| **B-M5** MAJOR | `# flags:` beside `# features:`, no TAB column, `--corpus` takes each pattern's own encoding and flags, a named-manifest floor, per-arm firing from `--emit-ir` and the stamp | note §8.1; `possdiff_exh.sh` |
| **C-S1..S9 / B-M6 / A-F2** | §1 rewritten as history plus the built join. Q4 STRUCK (D154 add. 1, U18). §6/§9 spec drafts cut to arms-specific sentences (possside landed the general ones). Citations by function name. The census is re-based on post-K93 possessify. S-ids, bits and abi are "at build, by grep" (S560-S565 free, S566 taken, highest S588, abi 65 at this writing). [FLAGBITS] is derived from axes.def. The plan row and the docs/design/CLAUDE.md entry are updated | note §1, §6, §9, §11 |
| **C-K94** | Not a prerequisite (T2 ⊇ seam on both sides of K94). Latin-1 byte + `--ucp` caseless-backref cells are held out of arm B's cell set until K94 merges. A seam ⊆ T2 inclusion check is added to `fold_agreement_check.c` (build) | note §3.3 |
| **Q3** | Ship A0: yes. Both preconditions are discharged (A-F3, the family sweep). Alpha cell `email-local-nodup`, or D149's "unmeasured" label | note §11 |
| **Q6** | B's form: registry_check.c asserts that the `(*ACCEPT)` and `(?\|` rows stay `unbuilt`, plus a `features verbs` perr block. The headline count is corrected to ONE soundness tripwire; `(?\|` is a re-verification prompt | note §3.3 |
| **Q7** | File-local statics, separately testable. `ctx_admits` gets an exhaustive model check (16 truth tables × 3 P subsets) that reports beyond-tier members. The capture fact is keyed by number over every A_CAP | note §7 |
| **B-FAM** | [POSS-CTX-TABLE] filed (plan.md + survey family 14 / §3.14) | plan.md, decision_families_survey.md |
| **Ranking** | Cost S → M; rank 3a-2 stands | note §9 |

## Where a measurement REFUTED or corrected the dispositions themselves

1. **C-1 (2), "the two deny bits are ENGINE-SELECTING": refuted for arm B.**
   - Arm B reaches only patterns with a backreference. A backreference needs
     a capture group, and a capture-bearing pattern is VM-routed (and stays
     VM even under `--no-captures`).
   - So `-fno-poss-bref-first` can never move `RX_ENGINE`. Measured:
     `(a)x++\1` and `(a)(?>x+)\1` stay `vm` armed and denied.
   - The note classifies A's bit ENGINE-SELECTING and kept, and B's bit
     answer-identity-preserving and masked. That is RC-Q5 for the critic.
2. **B-B3's "each > 0 required" fails for ONE conjunct: greedy-only.** Over
   1,134 newly claimed lazy rows, 0 diverge at ML=4. The lazy plant also
   passes the exhaustive possdiff and adds 892 CLAIM-vs-MARK marks, all
   oracle-sound. This is explained in note §2.3: a lazy loop leaves early
   only at a retreat exit, where the A1-valued continuation cannot succeed.
   The note KEEPS the conjunct as declared-conservative; RC-Q1 asks whether
   to drop it. No sabotage row can be written for it.
3. **ENCL needed its own control.** The panel listed ENCL with the
   conjuncts. In the family as generated, dropping ENCL claims 2,268 rows
   with 0 diverging, because the gate always heads the in-body continuation.
   Bypass rows were added (`(?:a+(?:\b|)|ab)+c` on `aabc`: 10.46 gives
   (0,4) greedy and (1,4) possessive), and ENCL is load-bearing for A1 there
   (3 of 4 diverge). Without those rows the table would have read 0 for
   ENCL too.
4. **A-F1 is broader than the panel stated.** Dropping the join from A1
   re-opens K93 on EVERY call-bearing pattern, not only gate shapes: for a
   gate-free continuation, A1's lexical recompute IS the lexical follow. The
   plant newly marks 16 `tests/recursion/k93.rxt` patterns, so the existing
   corpus detects it.
5. **C-2's "cost S → S-M".** With every check the panel required, the row's
   total is M (the ranking section's own revision). The arm code alone is
   S-M.

## What CLAIM-vs-MARK found (the check working as intended)

The first run disagreed on 25 rows. **Every disagreement was a gap in the
INDEPENDENT Python predicate, not in pcrec**, and each was oracle-confirmed
sound before the predicate was corrected:

- **`\B` after a multi-character body** (`(?:a\.)+\B`, LAST `.`, FIRST `a`).
  rev 1's generator never modelled `\B` as a gate, and rev 1's §2.4 said
  "\B ... A1 declines by itself", which is true only for single-class
  bodies. Now 108 claims, 0 diverging.
- **A `\b` reached through an empty-able reference** (`(a?)x+\1\b`). rev 1's
  arm-B generator widened it with the comment "arm A does not apply". Now
  16 claims, 0 diverging.
- **Two hand claims WIDER than the rule**, `(?:x+\1|(a))+` and
  `(?:(a)|x+\1)+` (ENCL's ungated union). These are sound either way and are
  now tagged `encl`.

## Instrument defects hit (recorded in rev2/CLAUDE.md)

1. **`minwb2.sh`'s first version could not fail.** Its `exit 2` ran inside
   `$(...)`, and its extra-flags `"$@"` was the function's own arguments. It
   reported a confident minimum of 1. Fixed before any number was used.
2. **The arm × call witness `(a?)(x+\1)y(?2)x`** needed a `y` that the
   generator's alphabet lacked, and a length-5 subject beyond ML 4. Both the
   sweep (0 diverging) and the REACH check (MISS) said so. It was re-spelled
   with `b`; witness `xbxx`.

## Open questions for the re-check critic

These are the note's §11 RC-Q1..RC-Q5:

- **RC-Q1:** drop greedy-only? (0/1,134 diverging)
- **RC-Q2:** a gated ENCL?
- **RC-Q3:** accept "ill-defined + 0 measured gain" for the P = {0,1} join?
- **RC-Q4:** `-e utf8 --ucp` is wholly refused today (2,059 selected rows),
  so it is unmeasurable. Is "re-sweep when [CLS-TREE] S4 / [UCP] U3 lands"
  the right owed item?
- **RC-Q5:** accept the asymmetric bit classification (A kept, B masked)?

Also for the critic:

- The prototype is env-switched with file statics and is NOT the
  implementation. The build re-counts the census independently (§8.6).
- The `.rxt` cells for the new witnesses (A-F1, ENCL, arm × call) are a
  BUILD obligation. Their 10.46 answers are in
  `rev2/witnesses_r2_10.46.out`.

## Resuming

A fresh agent resumes from note §R2 and §11. The prototype rebuilds from
`rev2/proto_rev2.patch` on a scratch copy of main (`patch -p1`). Every
instrument runs with `PROTO=<scratch>/build/pcrec` and `TMPDIR=<scratch>`.
The scratch directory used here was `worktrees/possarms2-scratch/`
(gitignored).
