# k69fix — K69 fixed, [PATFACTS] step 3.5 closed (lane report)

Lane k69fix, 2026-09-27, opus. Branch `lane/k69fix` off main `25854c26`
(abi 41, pf35 merged). Ruling: the manager's K69 disposition (a). Charter:
`docs/dev/known_issues.md` K69, `docs/dev/lanes/pf35_report.md` §2/§5,
`docs/design/patfacts/design.md` §4.3/§9 (E1 seal, one owner per derivation),
D126. **Not merged.** abi 41 -> 42.

## 1. What changed

| commit | what |
|---|---|
| `8fd5d4f3` c1 | `src/opt/callgraph.c` `cg_minw_publish` writes `u.call.nonnullable = minw != 0` beside `minw`: the LEAST fixpoint, published by `pcrec_callgraph_build` before the E1 seal. `src/gen/emit_vm.c`'s `vm_resolve_nonnull` + `vm_publish_nonnull` (the greatest fixpoint, run after the seal) deleted. `src/facts/widths.c` `pcrec_pattern_nullable` returns `pcrec_nullable(root)`. `pcrec_nullable`'s `A_CALL` arm unchanged (design §4.3 keeps it). Comments in `internal.h`, `mrl.c`, `callgraph.c`, `emit_vm.c`, `widths.c`; `src/gen/CLAUDE.md` |
| `60170e80` | `tests/recursion/k69.rxt`; `run_facts_checks.sh` [facts-e1] gains six call rows |
| `bcffbd42` c2 | abi 41 -> 42 (`PCREC_ARTIFACT_ABI`, `ABI_EXPECT` + its narrative, `docs/dev/history/abi_changelog.md`); sabotage S318/S319; S206/S207 re-anchored; CLAUDE.md in `src/core`, `src/opt`, `src/facts`, `tests/codegen`, `tests/mech`, `tests/recursion`. **The last `src/` commit** |
| `2d31b39f` c3 | `run_recursion_identity.sh` (B) FILEPIN -> `bcffbd42` (self-pin) |
| `7e368ec4` | `run_rxtsource_tests.sh` census +1/+16/+70 (CENSUS_* and RUNSH_*: 222/4051/29381); K69 FIXED addendum; `plan.md` 3.5 flipped |

**Why `minw != 0` is exact.** A callee's language is the least fixpoint of
its equations (a match is a finite derivation). `minw`'s Kleene iteration from
infinity down computes that language's least width, so "epsilon is in it" is
`minw == 0`. For every non-call kind `pcrec_minw(a) == 0` and
`pcrec_nullable(a)` already agreed (pf35 §2); with the call arm now reading
the same fixpoint, the two agree on every kind, so E1 can compose
`pcrec_nullable` and nothing reads two answers. M1 (greatest vs least) and M2
(published after the seal) are both closed by the one publisher.

**Arena zero still safe.** An un-run graph (possessify's early `pcrec_minw`
calls; a target outside the graph) reads `nonnullable = false`, i.e.
"nullable", as before.

## 2. Movers — measured against the brief's prediction

Instrument: pf35's gate, reused (`scratchpad/gate.sh`, paths changed plus
`ABI_FROM=41 ABI_TO=42`), driving `docs/dev/optloop/s1/s1_identity.py`
unchanged. BASE = main `25854c26`'s build, NEW = `bcffbd42`'s. Grid
`{byte, utf8} × {none, -fno-req-byte, -fno-req-run, -fno-end-window,
-fno-vm-anchor-bound, -fno-run-prefilter, -fno-offset-skip, -fno-lit-run}`,
each run = pcrec-bench's 64 capability patterns × 4 configs + every corpus
pattern × {auto, `--engine=vm`}. Log `scratchpad/gate_c2.log`.

| population | movers |
|---|---|
| pcrec-bench capability, every run | **0** |
| main's corpus (every pre-existing `.rxt` pattern), every run | **0** |
| the new `tests/recursion/k69.rxt` | **12 per run** = 6 patterns × {auto, vm}: `(a\|(?1))*?b`, `(a\|(?1))+?b`, `(a\|(?1)){2,}?c`, `(a\|(?1)(?1))*?b`, `(?(DEFINE)(?<g>a\|(?&g)))x(?&g)*?y`, `(?(DEFINE)(?<g>a\|(?&h))(?<h>(?&g)))x(?&g)*?y` |

Every mover's moved set is `RX_SLOT_EMPTY_GUARD0` (gone), `RX_NSLOTS`, the
following slot's index, `RX_VM_PROGRAM_BYTES`, `RX_FAST_TRAIL` (or
`RX_FAST_FRAMES`) and `program`: one guard slot, its `RX_SET` and its compare
removed. **Disposition, each: M1, K69's class** — a quantifier over a callee
whose cycle escapes only through the call, language `{a}`. No mover outside
the class. By hand, `(a|(?1))*` (not a corpus pattern): 17 diff lines, the
guard's two sites gone, same stamps.

**Against the brief's predicted list.** `(a|(?1))*` moves, as predicted.
`(a)?(?1)`, `(?:(a)|)(?1)` and `(?(DEFINE)(?<g>a))(?&g)` under utf8 do **NOT**
move, on either encoding, and their E1 `nullable` reads `no` before and after
(measured with `--emit-facts`, both builds). Their movement in pf35 §5 and in
K69's table was the SWAP build's M2 artifact: that build composed
`pcrec_nullable` at the seal while the field still held the arena zero
("nullable"). Publishing before the seal removes the artifact rather than
shipping it, so those three are not movers of the fix and the utf8 start gate
is not gained. This is a correction of the prediction, not a finding against
the fix: the E1 value moved on NO pattern.

## 3. The regression corpus and its oracle

`tests/recursion/k69.rxt`, hand-written (framebuffer.rxt's precedent; not
added to `gen_corpus.py`, whose re-run re-measures every file), 16 blocks /
70 cases: the six witnesses above plus `^(a|(?1))$` (ground truth: the group
is `{a}`); the controls that must KEEP the guard (`(?(DEFINE)(?<g>a?))(?&g)*`,
the g -> h = `b?` cycle, `^(a?)(?1)*$`); pf35's controls `(a(?1)?)*`,
`(a|b(?1))*`; the M2 E1 witnesses `(a)?(?1)`, `(?:(a)|)(?1)`,
`(?(DEFINE)(?<g>a))(?&g)` (byte and utf8). All VM-forced except the DEFINE
M2 cells.

Oracle: libpcre2 **10.46** on the reference box, light probe, committed
binding `sr_oracle.py` (`search` from 0), transcript
`scratchpad/oracle_1046.txt`:

    libpcre2 10.46 2025-08-27 selfcheck []
    '(a|(?1))*?b'   'aab' -> m 0 3 ((1,2),)   'b' -> m 0 1 ()   'xab' -> rc -52
    '(a|(?1))+?b'   'ab' -> m 0 2 ((0,1),)    'aaab' -> m 0 4 ((2,3),)
    '(a|(?1)){2,}?c' 'aac' -> m 0 3 ((1,2),)  'aaac' -> m 0 4 ((2,3),)
    '(a|(?1)(?1))*?b' 'aaab' -> m 0 4 ((2,3),) 'b' -> m 0 1 ()
    '(?(DEFINE)(?<g>a|(?&g)))x(?&g)*?y'  'xaay' -> m 0 4  'xy' -> m 0 2
    '(?(DEFINE)(?<g>a|(?&h))(?<h>(?&g)))x(?&g)*?y'  'xaay' -> m 0 4  'xy' -> m 0 2
    '^(a|(?1))*$'   '' / 'a' / 'aa' -> rc -52 (no expectation writable)
    '^(a|(?1))$'    'a' -> m 0 1 ((0,1),)
    '(a(?1)?)*'     'aaa' -> m 0 3 ((0,3),)   '' -> m 0 0 ()
    '(a|b(?1))*'    'abba' -> m 0 4 ((1,4),)  'c' -> m 0 0 ()
    '(a)?(?1)'      'aa' -> m 0 2 ((0,1),)  'a' -> m 0 1 ()  'b' -> n
    '(?:(a)|)(?1)'  'aa' -> m 0 2 ((0,1),)  'a' -> m 0 1 ()  'b' -> n
    '(?(DEFINE)(?<g>a))(?&g)'  'a' -> m 0 1  'ba' -> m 1 2  'b' -> n
    '(?(DEFINE)(?<g>a?))(?&g)*'  'aaa' -> m 0 3  '' -> m 0 0
    '(?(DEFINE)(?<g>(?&h)|a)(?<h>b?))(?&g)*'  'bba' -> m 0 2  'a' -> m 0 0
    '^(a?)(?1)*$'   'aaa' -> m 0 3 ((0,1),)   '' -> m 0 0 ((0,0),)

(`()` = all groups unset; written `g N -1 -1`.) Greedy witnesses are absent
on purpose: they run into the left recursion at the end of every run, where
libpcre2 answers rc -52. pcrec answers those identically on both builds
(`^(a|(?1))*$` on "aa" matches (0,2) — the d27 corpus's finding-4 class),
which is pre-existing and unrelated.

**Harness, `bash tests/harness/run.sh tests/recursion/k69.rxt`: 70/0 on the
fixed build AND 70/0 on the base build** — answers do not move, which is the
fix's claim; the guard's presence is not answer-visible.

[facts-e1] (`tests/codegen/run_facts_checks.sh`, re-run standalone: 8/0,
18 witnesses): `(a|(?1))`, `(a)?(?1)`, `(?:(a)|)(?1)` byte and
`(?(DEFINE)(?<g>a))(?&g)` utf8 expect `no`; `(?(DEFINE)(?<g>a?))(?&g)` byte
and the g -> h cycle utf8 expect `yes`. These read `pcrec_nullable`'s call
arm through the E1 fact — the same function the guard asks.

## 4. Sabotage

| row | plant | arm | expected |
|---|---|---|---|
| **S318** | `nonnullable = false` (every call nullable; the greatest fixpoint's answer on K69's population) | `facts` | DETECTED: [facts-e1]'s four `no` call rows. Answer-neutral by construction |
| **S319** | `nonnullable = true` (no call nullable; the unsafe direction) | `harness` on `tests/recursion/k69.rxt` | DETECTED: the nullable-callee controls lose their guard and give up on the step budget |
| S206/S207 | re-anchored onto `return pcrec_nullable(root);` (S207 inverts it) | unchanged | their recorded verdicts |

Highest S-id on main was S307; findb2 holds S308-S317. `scripts/m6read_check_
sab_anchors.py`: 316 rows, 332 sites, all resolve. Each row solo in the chain.

## 5. The abi 41 -> 42 ritual (D76/D94)

Readers found by grep (`41` near `abi`/`ABI`, `` `41` ``, `ABI_EXPECT`,
`FILEPIN`, and the byte-count manifests): `src/gen/emit_dfa.c`
`PCREC_ARTIFACT_ABI`; `tests/codegen/run_codegen_tests.sh` `ABI_EXPECT` and
its narrative; `docs/dev/history/abi_changelog.md` ("gap-free from 2 to 42", the new
top entry, 41 demoted to "was"); `tests/codegen/run_recursion_identity.sh`
(B) FILEPIN -> `bcffbd42`. The remaining `abi 41` hits (`limits.md`,
`tuning.md` §2.31, `lib/pcrec.h`, `run_tune_dial.sh`, `src/gen/CLAUDE.md`,
design notes) are dated history of S2a, not readers. The digit is the same
length, so no byte-count manifest moves on it; the gate shows no corpus
artifact of main's moved otherwise, so `m5_stage1_stamps.tsv` and the other
recorded manifests are unaffected (to be confirmed by test-codegen in the
chain). Spec: `docs/dev/history/abi_changelog.md` is the contract hunk (stamp VALUES move on
movers; no stamp/member added).

## 6. Validation at handoff

| check | result |
|---|---|
| `make strict` (c1) | clean |
| `run_facts_checks.sh` | 8/0 |
| `tests/harness/run.sh tests/recursion/k69.rxt` | 70/0 fixed, 70/0 base |
| `tests/rxtsource/run_rxtsource_tests.sh` | 255 pass / 0 fail, rc 0 (census 222/4051/29381) |
| sabotage anchors | all resolve |
| A/B gate c2 (§2) | byte: 8/8 runs complete, bench 0 / corpus 12 (all k69.rxt) each; utf8: see STATE |
| everything heavy | **OWED — the chain below** |

## STATE AT HANDOFF

Everything above is committed on `lane/k69fix` (HEAD at the report commit).
One detached chain, `scratchpad/chain.sh`
(`/private/tmp/claude-501/-Users-fdicostanzo-pcrec/k69fix/scratchpad/`), log
`scratchpad/chain.log`, runs under `caffeinate -s` via `nohup … & disown`. It
first WAITS for `FINDB2 CHAIN DONE` in findb2's `chain.log` and for
`GATE c2 DONE` in `gate_c2.log`, then runs each stage in series, one
`K69 CHAIN:` line per stage, ending `K69 CHAIN: ALL DONE`.

| stage | log | accepted verdict |
|---|---|---|
| A/B gate c2 (launched earlier, detached) | `gate_c2.log` | 32 `identity:` lines; bench runs have no `changed`; every corpus run `changed: 12`, the MOVER lines exactly §2's six patterns × {auto, vm}. Any other mover: classify per design §9.1, stop, report |
| build at HEAD | `chain_build.log` | rc 0 |
| `run_vm_identity.sh` | `vmid.log` | rc 0 |
| `run_ir_listing.sh` | `irlisting.log` | rc 0 |
| `run_prechecks.sh` | `prechecks.log` | rc 0 |
| `make test-codegen` | `codegen.log` | the ONE accepted red: `FAIL: nm could not read arm_a.o (no rx_search symbol)` |
| `make test-registry` | `registry.log` | no `*** [` line (PC-3 red locally is U13-expected) |
| `make test-recursion-identity` | `recid.log` | rc 0; (B) against `bcffbd42` |
| `make test-recursion` | `recursion.log` | rc 0 (§5 sweeps k69.rxt on both linkages) |
| mech S318, S319, S206, S207 | `mech_S*.log` | `mech run COMPLETE`, each DETECTED (S206/S207 at their recorded arms) |
| `make test CC=gcc-16` | `make_test.log` | make's `*** [test-X] Error` lines: only test-codegen's nm probe |
