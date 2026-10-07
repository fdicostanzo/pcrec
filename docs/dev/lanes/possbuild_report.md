# possbuild: [ART-POSS-ARMS] BUILD (arms A + B), per poss_arms.md rev 2.1

Lane `possbuild`, opus, 2026-10-07, branch `lane/possbuild` from main
`101d1a56`. It is an engine optimization and an abi event (65 -> 66). Three
sonnet sub-lanes worked in their own worktrees and were merged here:
`possbuild-pd` (§8.1 possdiff), `possbuild-cm` (§8.3 CLAIM-vs-MARK) and
`possbuild-rx` (oracle cells, stamp/route tests, unit checks).

**Status.** Code, tests, sabotage rows, spec and docs are committed. The
heavy slot chain is **OWED** (see "Slot results"). Its script is
`build/slot/chain.sh`, which is gitignored and re-creatable from this
report. Its logs go to `build/slot/`, and it writes `build/slot/STAGES` plus
`build/SLOT_DONE`.

## What was built (src)

- **`src/opt/possessify.c`.** The arms are production code, not the
  prototype patch.
  - **The per-walk fact record.** `Fq` lives on `Pss` and holds the arms,
    arm B's capture fact and the "an arm narrowed" flags. It is never a
    file static.
  - **`first_of` now takes `Fq`.**
    - The `A_CTX` arm is A0, through `pcrec_poss_ctx_admits` (S(P), with
      §2.1's empty-S widening).
    - The `A_BREF` arm is arm B, through `bref_first`. Its inputs are the
      capture fact (`cap_build`/`cap_group`, indexed and memoized per group
      number, where "in progress" means widen) and `text_first` (N1: a
      zero-width kind is (∅, nullable)).
    - The fold uses the SEAM's own caseless relation,
      `pcrec_enc_span_fold`, in `src/enc/enc.c`.
  - **A1.** The Glushkov scratch records each position's class and the
    body's LAST set. `pss_walk` threads a `PCont` continuation chain: one
    link per item, a marker at each `A_CAP` end carrying K93's join, and an
    atomic-body END. The chain is summarized once per link (`PSum`/`PGate`,
    the R-4 fix). The fold is iterative (D10/K20). `pss_verdict` re-asks row
    3 with gates valued by the LAST polarities, for greedy loops with
    `m >= 1` only.
  - **R-5.** The summary valued A0 must equal FOLLOW, and the end flag must
    equal may_end, at EVERY verdict. A mismatch is the house-form internal
    error. Under `--emit-ir` the summary is also checked against the plain
    per-Q fold (R4SUM).
  - **The stamp.** `Ctx.poss_arms` → `<PREFIX>_VM_POSS_ARMS`, bits 0x1 A0,
    0x2 A1, 0x4 B.
    - A1 is attributed directly.
    - A0 and B are attributed by a counterfactual SHADOW walk with that arm
      off. The walk runs only when the arm narrowed something, and it rests
      on the verdicts being monotone in each arm.
- **`PCREC_MAX_POSS_REF_DEPTH`** (64, in `limits.def`). It bounds arm B's
  recursion through reference chains, and past it the fold widens. This is
  a stack bound, not a measured knee.
- **Deny bits** in `lib/pcrec.h` and `src/core/axes.def`:
  - `-fno-poss-ctx-follow` is bit 50. It is ENGINE-SELECTING and is in the
    `kept` set of `src/gen/emit_dfa.c`.
  - `-fno-poss-bref-first` is bit 51. It is masked.
- **Stamp emission.** `src/gen/emit_vm.c` emits the stamp beside
  `VM_STRATS`.
- **`--list-axes` rows** in `src/dump/axes_dump.c`. There are 2 axes and 5
  rows, taking the totals to 136 rows / 46 axes.

## Per build-bar item: evidence

| item | evidence |
|---|---|
| §9 abi event | abi 65 → 66 (the readers are listed below) |
| §9 deny bits | A is kept (`run_prechecks.sh` 6b `KEPT_ALWAYS`). B is masked. Both are checked by `run_possessify_tests.sh` section 9 (e). |
| §9 spec (D80) | `tuning.md` §2.1, §2.8, §2.44 and §2.45, plus the `rx_info.flags` rule (three engine-selecting denials) and §2.32's kept list. `match_api.md` §6 change log, K80 example and §6.3 stamp entry. `cli.md` hidden-flag list. `registry.md` axes count. |
| §8.1 possdiff | `tests/possessify/run_possdiff.sh` gained the exhaustive subjects (`subjects_exh.py`), `# flags:` headers, REACH and the arms populations (`arms_*.txt`). It is in `make test-possessify`. The named-manifest floor is `arms_manifest.tsv`. Result: **288 patterns agree, 0 diverge, 623,938 cells, reach 15/15, manifest 35/35, 6 route-flip witnesses DFA-routed**. Red direction (sub-lane pd): the N2 plant is detected on `(\w+?(?:\b|))`. |
| §8.2 sabotage | 10 rows: S560-S565 (A-m0, A-firstpol, A-mixed, B-nofold, B-firstmem, B-nonnull) and S601-S604 (A-cc, B-depth, A-lazy, B-textpos). S600 was taken by lane stc4. Every row is `harness possdiff`, targets `tests/possessify/possessify.rxt`, has a stamp-reading `SAB_REACH` (verified answering at HEAD, 10/10) and a `SAB_REACH_POP` (verified matching, 19/19 lines). **Mech verdicts OWED (slot).** |
| §8.3/8.3a CLAIM-vs-MARK | `docs/design/poss_arms_measurements/built/` against the built compiler. The generators were verified at their pinned sha1s and not edited. **AB: computed 32,994 compared, 0 mark≠expect, 0 unsound, 662 extra flips, 0 anomalies; hand 44 / 0.** Base-marked 2,160. utf,ucp REFUSED 4,502 (`UCP_PIN` holds). The single-arm configs mismatch only in the safe direction (unsound 0). |
| OWED instrument item | Replicated copies are keyed as one target (`built/claimmark_build.py`, a COMPARISON edit with its new sha1 in `built/CLAUDE.md`). The 5 rows (`(?:[a-z]+(?:(?=\W)[ab])+y)+` and siblings) resolve; target-unresolved goes 3,459 legacy → 0. |
| §8.5 stamp + identity gate | `run_recursion_identity.sh` (A) gains the `poss-arms-moved` bucket. A mover is excused if it stamps nonzero and both-deny restores the pin. Both directions of the converse are checked, and the `POSS_PATTERNS` manifest holds §5.2's three corpus movers. (B) FILEPIN is self-pinned to `b81230c2`, to be re-pinned at merge. **Its run is in `make test` (OWED).** `scripts/emit_sweep.py --ref main` mover validation is OWED (it needs the slot). |
| §8.6 give-up | `run_axes.sh` reports the GIVEUP(code)→GIVEUP(code) class off BUDGET rows. `possdiff_driver.c` `describe()` reads `outcome_word.h` (pd). The committed-subject work budgets were re-measured on the BUILT compiler: denied 394, arm B 595, arm A 998, A+B 1,199, user-written possessive 1,199, `-fno-possessify` 394. These are identical to rev 2, and `tuning.md` §2.1 is re-pointed. **K35 re-count (`built/build_census.py`, three ways, diff vs `census_r21.tsv`) is OWED (slot).** |
| §8.7 R-4 | Wall seconds, this box, `--engine=vm`, to the size refusal: Bsame n=12,800 armed **2.13** vs denied 2.21; A1alt n=12,800 armed **4.67** vs denied 5.11 (the OWED rev-2.1 column). A1lb n=1,600/6,400 armed 0.03/0.14 vs denied 0.03/0.13. An adversarial all-distinct-class variant at 1,600/6,400 runs 0.08/0.34 vs 0.08/0.36. A1lb at 12,800 is over the argv cap and is skipped, as in rev21. All are within the 2× bar. |
| §8.7 R-5 | The always-on check is in `pss_verdict`. The R4SUM unit cells and population are in `run_possessify_tests.sh` (rx). The suites above ran with it on: 0 internal errors. |
| §8.7 R-6 | `reject_engine_dfa_bref_nocaptures` in `tests/reject/`, armed and denied, both PASS. |
| §3.3 tripwires | `check_poss_arms_tripwires` in `registry_check.c`: `(*ACCEPT)` (soundness) and `(?|` (re-verify) still read `unbuilt`. `registry_check` count 229 → 231. |
| §7 ctx_admits model check | `tests/possessify/ctx_admits_check.c` covers all 16 fn × 3 P × a set of C, including the A-F3 cell C={U+0100} → widen (rx). |
| .rxt cells | `possessify.rxt` gains the witness pairs (greedy + possessive spelling), `engine vm`, verified on libpcre2 10.46 through the committed ctypes binding (with and without `NO_AUTO_POSSESS`). It also gains the branching-cycle B-depth cell (oracle: no match, both spellings). `tests/recursion/k93.rxt` gains the A-F1 cells. |
| §8.8 composition | `built/run_composition_build.sh` (the rev21 hook with deny flags). **The run is OWED (slot).** |

**abi readers, found by grep for `65`:**
- `src/gen/emit_dfa.c` `PCREC_ARTIFACT_ABI`;
- `tests/codegen/run_codegen_tests.sh` `ABI_EXPECT` and its ledger message;
- `docs/spec/match_api.md`: the K80 example (twice) and the §6 change-log
  bullet;
- `run_recursion_identity.sh` (B) FILEPIN.

Historical mentions (`lib/pcrec.h:446/505`, `lib/CLAUDE.md`,
`src/gen/CLAUDE.md` [FLAGBITS] paragraph) were left as they are. Other pins
this change moves: the `--list-axes` row count (`registry.md`), the
`axes_registry_check` PASS count 205 → 214, `registry_check` 229 → 231, and
the `limits_check.sh` manifest and count 72 → 73.

**Light validation run (this box):**
- `make strict` clean.
- `make test-possessify test-recursion test-reject` green (314 s).
- `make test-registry` green.
- `test-corpus` green: 50,915 cases. `test-backrefs` and `test-atomic` green.

## Deviations from the note (each with its reason)

1. **The arm B fold relation is the SEAM's, not T2-through-
   `pcrec_ast_class_from_cpset`.**
   - That producer's T2 walk reads `cx->mods` (the scoped `(?i)`/UCP
     state). At possessify time that is the END-OF-PARSE state, which is
     wrong for `(a)A+(?i:\1)` (D62's defect class).
   - The build instead selects the relation exactly as the emitter selects
     the caseless entry. That is `pcrec_enc_span_fold` beside
     `vm_caseless_entry`'s predicate: Latin-1 under `ucp` when the backend
     carries the UCP entry, the encoding's fold otherwise. So the arm folds
     by the RUNTIME compare's own relation, which is exact rather than
     merely a superset.
   - The note's "seam ⊆ T2 inclusion check" therefore becomes "arm B's
     relation = the seam's". That equality is already checked by
     `fold_agreement_check` §9/§9b/§9c (byte, utf8, `--ucp`), which ran
     green in `test-backrefs`. No new check was added.
   - **Recommendation:** accept. A T2 path would need the reference's
     scoped state, which only `u.bref.caseless`/`ucp` carry.
2. **B-depth (S602) needs a BRANCHING-cycle witness.**
   - The build adds a stack bound (`PCREC_MAX_POSS_REF_DEPTH`) that the
     prototype did not have. With it, dropping the in-progress guard leaves
     a LINEAR cycle (`(a\2)(b\1)x+\1`) sound and fast. The prototype's
     SEGV witness therefore no longer detects anything.
   - `(a\2\3)(b\1)(c\1)x+\1` makes the bound alone exponential, and it was
     added as an oracle cell.
   - **The guard is now a cost guard; the depth bound is the termination
     guard.**
3. **A-cc (S601) is detected by R-5, not by a wrong answer.** The summary is
   shared by R-5 and A1, so dropping the join trips the always-on
   FOLLOW-equality check, an internal error on call-bearing verdicts. That
   is the check doing what §8.7 built it for.
4. **R4SUM's "test-time half"** runs the plain fold only under `--emit-ir`,
   a query mode, so production compiles stay linear. The census, CLAIM-vs-MARK
   and the rx population all compile with `--emit-ir`.
5. **The per-arm stamp's A0/B bits are counterfactual (shadow walks).** The
   note says "contributed to some positive verdict". A shadow walk costs at
   most two extra possessify walks per round, and only on compiles where
   that arm narrowed a set. The R-4 timings above include it.
6. **The stamp bit values are spec-documented, not named constants** in the
   `PCREC_RX_ABI_H` block (§6.3 paragraph). This keeps the abi event to one
   VM-only line.

## Sibling-of-a-family lens

The wiring adds members to existing decision families:
- the `rx_info.flags` `kept` set (a third engine-selecting denial);
- `run_recursion_identity.sh`'s stamp-or-deny excuse family (a fifth
  region-moving axis);
- `first_of`'s per-kind switch. The arms add `text_first` and `item_first`
  as two more per-AKind folds beside `first_of`, `gk_build`, `pss_walk`,
  `ps_node` and `cap_index`. This is the [POSS-CTX-TABLE] trigger the note
  names: the next per-kind possessify edit should unify them, with a
  reader field.

`pcrec_enc_span_fold` and `vm_caseless_entry` restate one predicate (UCP
entry present). It is two lines in two layers; fold them if a third reader
appears.

## Slot results — OWED

Run `build/slot/chain.sh` detached. It writes `build/slot/STAGES`, and each
stage's log is in `build/slot/`:

| stage | log | read |
|---|---|---|
| make test | `maketest.log` | `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'` (empty = green) |
| mech | `mech.log` | 10 DETECTED expected. S602 should be detected by timeout; S601 by compile refusal (R-5). |
| composition | `compo.log` | rc 0, ARMS-DIVERGE 0 on both routes, reach > 0 (prototype: 51/676) |
| census | `census_build.tsv`, `census_diff.txt` | diff vs `census_r21.tsv`; expect movers 6 bench / 13 corpus and 0 engine flips |
| test-axes (2 flags) | `axes.log` | each axis OK, or GIVEUP1 cases needing derived allowances |

Then restore `docs/dev/artifact_size_log.tsv` (the chain does
`git checkout` it).

## Open items, with recommendations

- **Plan row.** Leave [ART-POSS-ARMS] at `STATE:started` until the slot
  chain is green. Then the manager closes the row, and the
  [POSS-CTX-TABLE] trigger fires.
- **`emit_sweep.py --ref main` mover validation (§8.5).** Run it with the
  slot results. The movers should equal §5.2's corpus three plus the bench
  three, with 0 off-diagonal.
- **K94.** The Latin-1 byte + `--ucp` caseless-backref cells stay out
  (K94's to settle), as the note rules.

## Addendum (after handback)

- **The slot watcher was cancelled.** The manager granted `.lift` early and
  then revoked it; the chain had NOT started (no `STAGES` file). The watcher
  is killed because the manager may first merge post-[START-TABLE] C4 main
  into `lane/possbuild`. **The chain now starts by hand**:
  `nohup setsid bash build/slot/chain.sh > build/slot/chain.log 2>&1 & disown`
  (re-create `build/slot/chain.sh` from this report if the worktree was
  rebuilt). Sub-lane reports routed to the manager; they are relayed and match
  the numbers above. Sub-lane pd's open notes are: `--corpus` per-pattern
  flags not built; `hold/*` manifest rows pin witnesses that must NOT fire;
  other users of `possdiff_driver.c` (which now includes `outcome_word.h`) are
  covered by the full `make test`. Sub-lane rx adds .rxt blocks, so the
  rxtsource / startset / codegen pins move; the full `make test` must catch
  and re-pin them.
- **CLAIM-vs-MARK's oracle-version discrepancy, stated precisely.** Joined by
  row id, the built run (`built/results/claimmark_build.out.gz`, libpcre2
  **10.46**, this box's reference oracle, through `pcre2test_shim.c`) and
  the rev 2.1 record (`rev21/results/out2/claimmark.out`) differ in CLAIM on
  **5 compared rows** (sub-lane cm counts 43 over all rows, selected or not).
  - Every one is a `utf,i` row in the `(\b\w)\W*\1` family (A53860, A53925,
    A53926, A54102, ...). The claim is `yes` in the record and `no` here, and
    `hi=1` in both, so the expectation is **0 in both**. No mark≠expect
    verdict depends on it.
  - On 10.46 here, U+212A is in `\W` under `utf` and `utf,i`, is not in
    `\w`, and matches `(?i)k`. `(\b\w)\W+\1` matches `"k \x{212a}"` at
    (0,5) under `utf,i`.
  - Which oracle the record used is not stated per run. `rev21/CLAUDE.md`
    names a local `pcre2test` **10.48** for its sweeps, while
    `possarms21_report.md` says the battery ran on ubuntubudu (10.46). The 5
    differing rows point at the record's generator membership probes having
    run on 10.48.
  - **Recommendation:** treat the 10.46 run as the record of reference. If the
    rev 2.1 record must be settled, re-run its generator step once on
    ubuntubudu (10.46) and compare by id. The predicate files are unchanged
    (sha1s verified), so this is a version question, not a rule edit.
