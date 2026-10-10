# Lane rsform — [OPT-HYB-RESEED-FORM] round 1: A1 built, A2's bake-off prepared (2026-10-03)

Opus. Branch `lane/rsform` from main `1f244692` (abi 55). [OPTLOOP] round 1
under D144, per `docs/design/xcall.md` and the manager's rulings on its §7.
NOT merged; the full `make test` and the Linux bake-off are the manager's.

## Summary (resume from here)

- **plan.md.** It now files `[OPT-HYB-RESEED-FORM]` (STATE:started, under
  [OPTLOOP], round 1) and `[OPT-HYB-RESEED-POLICY]` (STATE:not-started,
  the §7 Q7 residual, an unmeasured candidate). Both
  `[OPT-HYB-RESEED-XCALL]` entries are annotated HELD 2026-10-03 with the
  new D77 trigger and B2 as the API of record. [OPTLOOP]'s round-1 list
  points at the re-pointing.
- **A1 is built (abi 55 -> 56).** `pcrec_reseed_rows` gains an undeniable
  `anchored` row after `clamped`.
  - Its predicate is `pcrec_fact_start_anchor(v->cx) != PCREC_SANCH_NONE`.
    That is the same fact `att_max` reads for [OPT-ANCHOR-VM]'s
    `attempt_max = search_from` bound, so there is one derivation, and
    `-fno-vm-anchor-bound` empties the bound and the row together.
  - Its action is FIXED. A start-anchored hybrid now carries the deny's
    retry, and its artifact equals its `-fno-hyb-reseed` artifact byte for
    byte, stamp line included.
- **A2 is not built, by ruling (Q4).** Its form is picked by the x86
  gcc+clang bake-off first. The kit is in `studies/hyb_reseed_cal/bakeoff/`
  and the manager's three steps are in its `README.md`. The Mac smoke run
  completed end to end, answers the same on all 40 rows (see §3). Q3's byte
  budget (a `tuning.md` §2.35 sentence plus the utf8 re-calibration)
  belongs to A2's build and is recorded on the plan row. Nothing for it
  lands here.

## 1. A1 — what changed

| file | change |
|---|---|
| `src/gen/emit_vm.c` | `VRS_P_ANCHORED`, row `anchored` (table comment says why undeniable), its `vm_reseed_holds` arm |
| `src/gen/emit_dfa.c` | `PCREC_ARTIFACT_ABI` 55 -> 56 |
| `docs/spec/match_api.md` | #abi-guard's quoted guard block (3 digits), the abi change log in docs/dev/history/abi_changelog.md (new top entry), §6.3's `RX_VM_RESEED` value table (`"anchored"` row) |
| `docs/spec/tuning.md` | §2.35's table gains row 3 `anchored` (rows renumbered 4-6) and a sentence on the deny |
| `tests/codegen/run_codegen_tests.sh` | `ABI_EXPECT=56` plus its log message (copied from §6); the `[OPT-HYB-RESEED]` block gains check (5): witnesses `anchored` (`^(?>a\|ab): (.*)$`), `gstart` (`\G(?>a\|ab)c`) and the control `unbound` (the `^` pattern under `-fno-vm-anchor-bound`, which reads `adaptive-dense` with the framed calibration), plus the two byte-equality checks against `-fno-hyb-reseed` |
| `tests/codegen/run_recursion_identity.sh` | FILEPIN re-pinned 35a9e2b4 -> `376d7250`, this lane's src commit (the self-pin convention) |
| `tests/mech/sabotages/S441_hyb_reseed_anchored_row_never_holds.sh` | the row's predicate answers false. **S441 because S440 may be taken by lane vedge**, building in parallel |
| `src/gen/CLAUDE.md`, `tests/codegen/CLAUDE.md` | the row and the check |
| `docs/dev/reseed/anchored_sweep.py` (+ CLAUDE.md) | the byte-identity sweep for this change |

**abi readers, found by grep** (`git grep -E "abi[ =-]*55|ABI_H \+ 0\) != 55|ABI_H 55|ABI_EXPECT"`
outside history docs):
- `emit_dfa.c:52`
- `match_api.md#abi-guard`
- `run_codegen_tests.sh` `ABI_EXPECT`
- the change log (docs/dev/history/abi_changelog.md)

The rest are dated history (design notes, reviews, known_issues, the
`run_nomatch_caps.sh` comment, the S439 comment, xcall.md's "abi 55 at
c231ffc1"), and they stay as written. The registry pin of 171 did not move:
the row has no deny bit, so it adds no triple, and the `RX_VM_RESEED`
value-set check reads `anchored` in both directions.

**Why no flag of its own (Q2, ruled YES).** D144 item 4 gives every
optimization its own deny. A1 is a selection CORRECTION, not an
optimization with a choice in it:
- The adaptive text it removes is unreachable. The loop returns at
  `attempt_position >= attempt_max` after the first failed attempt, before
  the tail.
- So the artifact with the row is, by construction, the artifact the deny
  produces. A flag would select between two spellings of the same program
  and could never answer differently or run differently.
- `-fno-hyb-reseed` remains the kill switch for the whole mechanism, and
  `-fno-vm-anchor-bound` removes the row's premise along with the bound.
- `exact` is undeniable for the same reason: the choice does not exist.

## 2. A1 — validation

All runs were on the Mac at load 15-37 (other lanes running), in the
background, logs under `worktrees/rsform-scratch/`. Verdicts come from
make's `*** [` lines.

| run | verdict | log |
|---|---|---|
| `make strict` | rc 0, clean | `strict.log` |
| `make test-codegen` | `*** [test-codegen] Error 1`, **13/14 scripts**. The one red is `run_inline_capability.sh`'s darwin `nm could not read arm_a.o`, accepted by the brief. `run_codegen_tests.sh` 135/0, the reseed block 20 checks | `test-codegen.log` |
| `make test-registry` | rc 0, no `*** [`; axes pin 171 holds; `[RX_VM_RESEED]` value set (with `anchored`) both directions PASS | `test-registry.log` |
| `make test-recursion-identity` (the re-pinned FILEPIN) | **OWED** (chain2, running at hand-off). Completion: `=== recid rc=N` in `chain2.status`; verdict: the trailer `checks passed: 16 / checks failed: 0` expected (pre-change was 16/0) | `test-recursion-identity.log` |
| byte-identity sweep, default (`anchored_sweep.py`) | **OWED** (chain2). Completion: `=== sweep rc=N`; `rc=0` and `violations: 0` on the log's last line is the pass. The tally lines carry the mover census (expect `mover base=adaptive-dense new=anchored` = 48 under `byte`, with start `anchored`/`gstart`) | `anchored_sweep.log` / `.tsv` |
| byte-identity sweep, engine arm (`--extra="--engine=vm -fprefilter"`) | **OWED** (chain2). Completion: `=== sweepvm rc=N`; same pass rule | `anchored_sweep_vm.log` |
| answer identity at every startpos over the movers (`answer_diff.py`, unchanged, fed the sweep TSV) | **OWED** (chain2). Completion: `=== adiff rc=N`; the head of `answer_diff.log` reads `movers: N` and the tally follows it; any `DIFF`/`COMPILE-FAIL`/`ERROR:` line is a finding (`SKIP-LINK` = a `vars` artifact) | `answer_diff.log` |
| sabotage S441 (`run_sabotage_matrix.sh S441`) | **OWED** (chain2). Completion: `=== s441 rc=N` then `CHAIN2-DONE`; expect `DETECTED` with `codegen` failing the anchored/gstart stamp, call-site and equality checks (5-6 fails) | `s441.log` |

**Mover census.** OWED with the sweep. The prediction is xcall.md §4's
census at c231ffc1: 48 under `byte` (47 `anchored` + 1 `gstart`, all
formerly `adaptive-dense`), and a similar number under `utf8`. Any
`UNEXPECTED-MOVER`, `ROW-RENAMED` or `ANCHORED-NOT-DENY` row is a finding.
The four witnesses compiled by hand already show the claimed shape: base
versus new differs by exactly the stamp line, the declaration and the
nine tail lines, and new equals new-deny byte for byte.

**Chain2** is `worktrees/rsform-scratch/chain2.sh`, detached under `caffeinate -s`. It runs
recid, sweep, sweepvm, adiff and s441 in that order, and its status is in
`worktrees/rsform-scratch/chain2.status`.

## 3. A2 — the bake-off kit (`studies/hyb_reseed_cal/bakeoff/`)

**The variants.** Every cell is built in these variants:
- `a`: the shipped adaptive form.
- Six forms from `mkforms.py`:
  - `ai`: shipped plus a forced-inline prefilter.
  - `f1` / `f2`: lane xcalldes's `mkbound.py`.
  - `f3`: lane xcalldes's `mkb3.py`.
  - `f3i`: F3 plus the forced-inline prefilter, which is xcall §4's third
    starting point.
  - `f4`: a second spelling of "init on the entry pass only". It is F2 with
    the entry pass told apart by `seed_from == search_from` instead of the
    `~0u` sentinel. It is there because F2's x1.742 says gcc's answer
    depends on the spelling.
- `d`: the deny.
- Two noise-floor copies of `d`:
  - `d2`: the same binary relaunched.
  - `dL`: the same source, link order swapped (a layout perturbation).

**The cells** (`cells.tsv`) are xcall §6's improve and keep lists:
- possq ss/thr; lka-pos, lka-verb, lka-neg and lka-nonatomic ss; lka-pos
  and lka-verb thr (keep); grp-atomic-alt ss/thr.
- asr-lb-varwidth synth-dense (improve), and synth-1m, gap64 and bursty
  (keep).
- asr-lb-fixed synth-1m and synth-64k-asc (improve), and gap64 and bursty
  (keep).
- asr-lb-neg synth-1m (keep).
- A1's own cell, logparse-atomic ss, on capability's 75 short subjects. Its
  `a` is main's artifact and its `d` the lane's.

**How a run goes.** `bakeoff.sh` builds every variant with gcc and clang
at -O2 (188 binaries). It checks each variant's answer hash against the
deny's, then calibrates iterations on the deny to at least 50 ms per pass.
It runs 15 round-robin launches per binary with the order rotated per round,
each one `taskset -c CORE` and each the median of 7 passes. It prints one
table, then a per-compiler, per-form footer: the geomean and worst over the
improve rows, the count above 1 + floor, and the worst keep-row loss against
`a`.

**Mac smoke run.** It used `LAUNCHES=2 PASSES=1 MINMS=2`, gcc-16 plus Apple
clang, at load ~37. It is plumbing only and its numbers are NOT evidence.
It completed with answers the same on every row. It incidentally reproduced
xcall's gcc shape: possq thr f1 x1.10, f2 x1.75, f3 x1.24.

**Owed to the manager:**
1. The pack (prep.sh), already built at
   `worktrees/rsform-scratch/rsform_bakeoff.tgz` from `bea57c8c`.
2. scp it to the box.
3. One command, about 45 minutes on one pinned core.

## 4. What is owed / next

- **The manager's `make test`** on the branch.
- **Lane vedge's parallel abi bump.** Both lanes took main's abi + 1 = 56.
  At merge the second lane takes 57, and that means:
  - `emit_dfa.c`, `ABI_EXPECT` and its message;
  - the §2 quote and the §6 log entry order;
  - the FILEPIN re-pin.
  The S-ids do not collide: S440 is vedge's, S441 is this lane's.
- **The Linux bake-off (§3).** Its table picks A2's form. A2's build then
  carries:
  - the emitter text;
  - the abi bump;
  - the S370/S371/S372 re-aims (grep `reseed_steps`/`reseed_block` under
    `tests/mech/sabotages/`, and treat the count as a floor);
  - the calibration check re-read;
  - the Q3 byte-budget sentence plus the utf8 re-calibration witnesses
    (`cjk*`, `asr-lb-*`);
  - the identity sweep.
- **The bench alpha** for A1 (logparse-atomic ss), per xcall §6, through
  pcrecdev2. The bake-off's `lpatom` row is a pcrec-side preview of it.
