# pf32 — [PATFACTS] step 3.2, "E1: kinds, nullable" (lane report)

Lane pf32, 2026-09-27, opus. Branch `lane/pf32` off main `e7e08872` (abi 40).
Spec: `docs/design/patfacts/design.md` §9's 3.2 row, §2, §3, §4.2, §9.1.
**Not merged. No abi event: the step is byte-identical.**

## 1. What landed, commit by commit

| commit | what | gate |
|---|---|---|
| `b236aec3` | `src/facts/kinds.c` (`pcrec_pattern_kinds`: the `PF_KIND_*` mask composed from the root answers of the `atomic.c`/`mod_vars.c` node predicates) and `src/facts/widths.c` (`pcrec_pattern_nullable` = `pcrec_minw(root) == 0`). Two `facts.def` rows (`kinds`, `nullable`, epoch 1, no deny). `pcrec_facts_seal_e1` is called by `compile_driver` right after `pcrec_callgraph_build` (today at `compile.c:1414`, just before `pcrec_select_engine`) and FORCES both facts. `pcrec_facts_seal_e2` now runs the **E1 invariance cross-check** (`pf_check_e1`) first: it re-derives both facts on the lowered tree, and an internal-error refusal follows on any disagreement. It also refuses when E1 was never sealed. The readers switched to the accessors: `select_engine.c`'s `forces_captures` (live capture) and `prefilter_decision` (the bref/linked-call/var locals, collapsible repeat, nullable); `compile.c`'s collapse gate (`pfc_rep`, `!nullable`); `emit_vm.c`'s `mrl_win` (atomic, lookaround) and the `--emit-ir` listing's `has_bref`/`has_call` (R1); and `pcrec_startgate_needed` (K50), which now takes `Ctx *`. **`EngineFit.lang_nullable` and `EngineFit.prefilter_has_collapsible_rep` are deleted** [r1 A7]. Their argument comments moved to `widths.c`'s header. The params `prefilter_decision(root)` and `vm_emit_epilogue(root)` went unused and were dropped. S140/S176/S206/S207/S236 are re-anchored (§4). | A/B: §2 |
| `5d954de2` | `run_facts_checks.sh` check 7, **[facts-e1]**. The sabotage rows **S302/S303**. `facts_listing.md` names the two new rows' value spellings (D80). CLAUDE.md updates for src/facts, src/opt, src/core, tests/codegen and tests/mech. | test/docs only, no `src/` change |
| `34b35289` | plan.md: the [PATFACTS] row gains its 3.2 delivered note (no state flipped) | — |

No file RELOCATED in this step (both files are new compositions), so
carve-out (e)'s one-relocation-per-commit rule applied to nothing. The one
code commit carries the whole migration. Per design §5 item 4 it has no
dual-write period: each field and its accessor were never alive together.

**Design deviation (named, not silent): the kind mask has no `CALL` bit.**
Design §1 lists `CALL` in the mask. `pcrec_has_call` has no root-grain
reader: its only call outside `atomic.c`'s own recursion is module
`lookaround`'s subtree ask (`mod_lookaround.c:534`). A bit with no
pattern-grain consumer is built ahead of need, and that is design §1's own
reason for dropping the root widths (D77). The trigger to add the bit is the
first root-grain reader of "any call". The seven bits that exist are BREF,
LINKED_CALL, VAR, ATOMIC, LOOK, LIVE_CAPTURE and COLLAPSIBLE_REP.

**Also not moved (outside the 3.2 row):** `v->root_minw = pcrec_minw(root)`
(`emit_vm.c:9855`) is the E2 root byte `minw`, which design §4.2.1 files
under `widths.c`. The 3.2 row names only kinds and nullable, so it stays
where it is. Its trigger is the step that migrates the VM's root checks.

## 2. The zero-movers gate

The instrument is reused, not a second one: `docs/dev/optloop/s1/s1_identity.py`,
unchanged, driven by a scratch copy of findb1's `gate.sh`. BASE is main
`e7e08872`'s build and NEW is `b236aec3`'s build. The grid is
`{-e byte, -e utf8} × {default, -fno-req-byte, -fno-req-run, -fno-end-window,
-fno-vm-anchor-bound, -fno-run-prefilter, -fno-offset-skip}`, 14 runs. Each
run covers pcrec-bench's 64 capability patterns × 4 configs (auto/vm ×
caps/nocaps) plus every distinct corpus pattern × {`--features all`,
`+ --engine=vm`}, so the brief's `--engine=vm` column is inside every run.
The raw comparison applies no normalization (no abi event, no
`DROP_FINDINGS`).

**Result: 14 of 14 runs have identity lines of "identical/refused" only,
with zero `changed`, zero refusal mismatches and zero timeouts.** Each of
the 7 byte runs reads bench `{identical 249, refused 7}` and corpus
`{identical 5689, refused 715}`. Each of the 7 utf8 runs reads bench
`{identical 245, refused 11}` and corpus `{identical 5721, refused 683}`.
The refusal counts equal pf30's and findb1's on the same population, and
BASE and NEW refused the same inputs. Log:
`scratchpad/gate_c1.log` (`GATE c1 DONE`).

**REACH.** Every compile that reaches the call graph seals E1, and
`prefilter_decision` asks `pcrec_fact_kinds` and `pcrec_fact_nullable` on
every compile. So every compiled artifact in every run asked the migrated
accessors. The count is the `identical` column of each run: 5,938 byte /
5,966 utf8 artifact-configs.

**The `--emit-ir` listing (design §9 3.2 gate; coding guide §3.3).** It is
output, not an artifact, and it is covered by `tests/codegen/run_ir_listing.sh`
(§5). A spot check over 7 patterns × 2 encodings × {auto, vm} was
byte-identical against the base binary for both `.c` and `--emit-ir`.

**Mover classification (§9.1):** none found, of either class. No K-row
was filed and there is no abi bump.

## 3. The E1 invariance cross-check and its two sabotage rows

`pf_check_e1` (`src/facts/facts.c`) calls the SAME two derivations on the
lowered tree that E1 ran on the structural tree. Its shape follows the
`cstart_check_omission` precedent: it is always on, and a disagreement is a
`pcrec_ctx_fail` internal error, never an `abort()`. The design's "debug
self-check build shape" is that precedent, and that precedent has no debug
gate, so this check has none either.

Its detector is `run_facts_checks.sh` **[facts-e1]**: 12 witnesses
(encoding, pattern, kinds, nullable), whose values were written BY HAND from
each pattern's structure. 10 of them sit on a utf8 tree that the lowering
rewrites, which is the only place the two derivations can disagree. Every
witness must compile and list exactly those values. REACH fails the check if
there is no witness, no rewritten witness, or a `PF_KIND_*` bit in `facts.h`
with no witness (7 of 7 today). Clean run: `checks passed: 7`, `checks failed: 0`.

| row | plant (src/opt/lower_enc.c) | hand-verified failing direction | attribution |
|---|---|---|---|
| **S302** kind mask | `lower_walk`'s splice wraps each rewritten class in an `A_ATOMIC` (answer-neutral: an atomic around one character's byte alternation cuts nothing) | `facts:1fail/6pass`: every rewritten witness is refused with `internal error: [PATFACTS] the kind mask sealed at E1 (0x0) disagrees with the lowered tree's (0x8)` | With the cross-check's call removed, [facts-e1] is **GREEN**: only the cross-check sees this plant |
| **S303** nullability | `lower_class_utf8` returns `A_EMPTY` for a non-empty class | `facts:1fail/6pass`: `\x{3b1}`, `[\x{3b1}-\x{3c9}]` and the others are refused with `nullability sealed at E1 (no) disagrees with the lowered tree's (yes)` | With the cross-check's call removed, the same witnesses are **still refused**, now by [K50-NULLGATE]'s `cstart_check_omission` ("omitted the character-boundary gate on a pattern that can ACCEPT without consuming"). That is a second, independent, machine-level detector (DFA-unanchored route only). The cross-check fires first and covers every route. This is recorded in the row, not claimed away |

**Which checks fire under S303, per witness** (the manager asked for this
record, 2026-09-27; measured on a scratch tree, not the worktree build):

| witness (utf8) | route | cross-check present | cross-check removed |
|---|---|---|---|
| `\x{3b1}` | DFA | refused: `[PATFACTS] nullability sealed at E1 (no) disagrees with the lowered tree's (yes)` | refused: `[K50-NULLGATE] omitted the character-boundary gate ...` |
| `[\x{3b1}-\x{3c9}]` | DFA | same [PATFACTS] refusal | same [K50-NULLGATE] refusal |
| `\x{3b1}{2,5}` | DFA | same [PATFACTS] refusal | same [K50-NULLGATE] refusal |
| `(\x{3b1})\1` | VM (bref) | same [PATFACTS] refusal | **passes**: no start gate is built on a VM route, so K50's self-check never runs, and the listing shows the sealed E1 value |

**The mech matrix cannot attribute detection per check, and I did not build
attribution** (per the ruling). The `facts` arm scores
`run_facts_checks.sh`'s failed-CHECK count. [facts-e1] is one check, and it
is red under either detector. So if someone removed the cross-check, S303
would still read DETECTED (`facts:1fail/6pass`) through K50 on the three DFA
witnesses. What does show that the new check is live: S302 (answer-neutral,
and GREEN with the cross-check removed), plus this table's backreference
row, which only the cross-check refuses. The same table is recorded in
S303's header. The cheapest attribution, if it is ever wanted, is a
[facts-e1] sub-check that fails only when a refusal carries the
`[PATFACTS]` tag. I did not build it (D77: no measured need beyond this
record).

For the S302 plant I chose `A_ATOMIC` rather than the design's suggested
`A_BREF`. An `A_BREF` in the lowered tree also trips `nfa.c`'s "bad AST node"
on every DFA route, so a row planting it would be DETECTED even with the
cross-check deleted, and it would not test the cross-check.

The solo mech runs are in §5.

## 4. Re-anchored rows

Each row was copied from the current tree. Each carries a dated
"[PATFACTS] step 3.2 RE-AIMED, INTENT RE-VERIFIED" note at its foot, and
`scripts/m6read_check_sab_anchors.py` reports `sabotages checked: 308 (324
anchor sites)`, `all anchors resolve`.

- **S206/S207**: moved from `fit->lang_nullable = pcrec_minw(root) == 0;` to `widths.c`'s `return pcrec_minw(root) == 0;`. The plant reaches every nullability reader through the one derivation, as it did through the one field. The E2 cross-check calls the same derivation, agrees, and stays silent.
- **S236**: moved to `pcrec_startgate_needed`'s `return pcrec_fact_nullable(cx);`.
- **S176**: moved to `const bool has_call = (kinds & PF_KIND_LINKED_CALL) != 0;`.
- **S140**: moved to `mrl_win`'s two kind-mask conjuncts. The columns are kept, and the plant still deletes the lookaround conjunct alone.

**Stale figures, not touched:** the `SAB_DOC_FIGURE` text of S296-S301
records `facts:Nfail/5pass` or `…/4pass`. The `facts` arm now runs 7
checks, so a re-run reads `…/6pass` or `…/5pass`. The matrix scores the
fail count and does not read the figure.

## 5. Validation

Done in-lane:
- `make strict CC=gcc-16`: `strict: whole tree compiles clean with -Werror -Wshadow` (rc 0).
- `bash tests/codegen/run_facts_checks.sh`: `checks passed: 7`, `checks failed: 0`.
- `tests/registry/limits_check.sh`: 31/0. The new `PF_KIND_*` enum needs no allowlist entry.
- `scripts/m6read_check_sab_anchors.py`: 308 rows, all anchors resolve.
- The A/B gate is in §2: 14/14 runs, zero movers.

The chain results that had landed at hand-off (logs in the scratchpad
`/private/tmp/claude-501/-Users-fdicostanzo-pcrec/pf32/scratchpad/`):
- `make test-codegen` (`codegen.log`): `run_group: 11/12 scripts passed`. The one red is the accepted `FAIL: nm could not read arm_a.o (no rx_search symbol)` (run_inline_capability.sh). That is GREEN by the brief's standard.
- `run_prechecks.sh` (`prechecks.log`): `checks passed: 301`, `checks failed: 0`.
- `run_ir_listing.sh` (`irlisting.log`): 147/0. The `--emit-ir` listing is unchanged.
- `run_vm_identity.sh` (`vmidentity.log`): 10/0.

## STATE AT HANDOFF (2026-09-27)

Everything is committed on `lane/pf32`. Two detached processes are still running
(`nohup … & disown`), serially, one heavy suite at a time. Neither needs
this lane to be alive.

**1. The validation chain.** Script `scratchpad/chain.sh`, log `scratchpad/chain.log`, completion line
**`PF32 CHAIN: ALL DONE`**. Each stage writes one `PF32 CHAIN: <stage> rc=N` line:

| stage | log | how to read the verdict |
|---|---|---|
| `make test-recursion-identity` | `recid.log` | the trailer `checks passed:`/`checks failed: 0`. Its (B) pin must NOT move: the script is untouched, so a (B) `differing` > 0 is a real mover (§9.1, a K-row) and must NOT be re-pinned |
| mech solo S302 | `mech_S302.log` | `mech run COMPLETE: 1 rows (unexpected: 0, undetected: 0, unreached: 0, anomalies: 0 …)`. The expected cell is `facts:1fail/6pass` DETECTED |
| mech solo S303 | `mech_S303.log` | same completion line and `facts:1fail/6pass`. Per §3, this arm cannot attribute detection to the cross-check vs K50 |
| mech solo S140, S176, S206, S207, S236 (the re-anchored rows) | `mech_S<id>.log` | the same completion line, expected DETECTED. Compare each row's arm cells against its own `SAB_DOC_FIGURE` |

The chain line for each mech row also echoes that row's `mech run
COMPLETE` line.

**2. The full `make test`.** Script `scratchpad/final.sh`, launched detached. It waits
for `PF32 CHAIN: ALL DONE`, then runs `timeout 9000 make test CC=gcc-16`
in the worktree. Log `scratchpad/make_test.log`. Its own status goes to
`scratchpad/final.log`, whose completion line is
**`PF32 FINAL: make test rc=N`**. **The verdict is make's
`*** [test-X] Error` lines in `make_test.log`**, never a grep for FAIL
(learnings §3). Expected accepted reds: the darwin `nm could not read
arm_a.o` probe (test-codegen) and PC-3 (U13, local libpcre2 10.48). A
manifest drift is a DIFF TO REVIEW, never a bump (this step is
byte-identical). One known cause to check first for any `test-facts`-shaped
or listing-count red: the `facts` listing gained two rows (`kinds`,
`nullable`), so a pinned `facts` row count elsewhere would move. None was
found by grep.

**Triage owed by a fresh agent:** read the verdicts above, append them to
this section, and triage any red beyond the accepted ones. No handback of
the heavy-validation verdict was made: it is OWED.

## 6. Findings

1. **The two E1 fields had exactly the readers the design named, plus one
   more.** `forces_captures` (`select_engine.c:139`) asked
   `pcrec_has_live_capture(root)` at the root. The design's consumer column
   covers it only as "select_engine". It now reads the LIVE_CAPTURE bit.
   The consequence is that live-capture is now derived on every compile. It
   used to be derived only when captures were wanted (the eager seal's
   cost: a handful of iterative walks per compile).
2. **S303's drift has two detectors** (§3). The K50 machine-level self-check
   already guarded the nullability half of the invariance on the
   DFA-unanchored route. The E1 cross-check is the first detector, and the
   only one on the other routes.
3. **No disagreement between copies was found.** Over all 14 runs, not one
   compile hit the cross-check. The design §3 proof held on the whole corpus
   and the bench population, under both encodings and every deny set.
4. `pcrec_startgate_needed` lost its `const`: the accessor marks `used`,
   which writes `Job.pf`. Both callers already held a non-const `Ctx *`.

## 7. For the next step / a fresh agent

- 3.4 (E3) adds its seal inside the `ENG_UNANCH` arm. The force loop's
  epoch skip is its first real customer (every fact is E1/E2 today).
- The E2 root `minw` (`emit_vm.c:9855`) belongs in `widths.c` when its
  reader migrates.
- Not touched: plan STATE tags, the journal (the manager's).
