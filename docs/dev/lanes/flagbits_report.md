# flagbits — `rx_info.flags` deny bits 18 and 21 (K92), and what `.flags` is supposed to mean

Lane `flagbits`, 2026-10-06, branch `lane/flagbits` off main `19ddb5c0` (abi 64).
Task: triage `decision_families_survey.md` §4.3 (Frank's ruling 2026-10-06), then
a meta review of the contract. Verdict: **a bug, one general fix, built.**

## 1. Cause

`emit_info_def` (`src/gen/emit_dfa.c`) wrote `.flags` as
`cx->opt->flags & ~strategy_denials`, where `strategy_denials` was a
hand-kept OR of masked bits. It was written at [ENG-BREP] and every later
axis was APPENDED to it by hand. Bits 18 (`-fno-size-term`, [ART-SIZE]) and 21
(`-fno-scan-edge`, [OPT-5]) were never appended. Reproduced on `abc`:
`.flags = 0ULL` becomes `2097152ULL` (`-fno-scan-edge`) and `262144ULL`
(`-fno-size-term`); a byte diff of the two artifacts shows that line and
nothing else.

It is the same defect as bit 19 and K68, a fourth time (bit 19, bits
28/29/30, now 18/21), and for the same reason: nothing read `.flags` as a
number for these bits. `run_prechecks.sh` section 6 held only 28-30.

## 2. Population per bit

Measured: 200 corpus `pattern` lines sampled at random (`LC_ALL=C`, seed 7,
compiled at default features, 60 bytes or shorter), each compiled with and
without every `-f` spelling `--list-axes` carries (plus `--trace`,
`--fast-or-fail`). "`.flags` moved" = the `.flags` line differs from baseline.
"only" = it is the ONLY line that differs (the pure leak). "other" = some other
line differs, i.e. the flag reaches the artifact. Script and raw output were
scratch (`build/fb/pop.sh`, not committed); the committed control is
`run_prechecks.sh` section 6b.

| bit | flag | before: `.flags` moved | before: only | other | after |
|---|---|---|---|---|---|
| 4-11, 14-17, 19, 20, 22-24, 26-33, 35-38, 41-47 | every other strategy axis (incl. `--fast-or-fail`) | 0 / 200 | 0 | varies | 0 |
| 12 | `-fno-atomic-discharge` | 200 | 200 | 0 | 200 (kept, by design) |
| 13 | `-fno-splice-calls` | 200 | 200 | 0 | 200 (kept, by design) |
| **18** | `-fno-size-term` | **200** | **137** | 63 | **0** |
| **21** | `-fno-scan-edge` | **200** | **133** | 67 | **0** |
| 25, 39, 40 | startpos guard / `-futf-check` | 0 under `byte`; moves under `-e utf8` | | | unchanged (contract, kept) |
| 0-3, 34 | `-i`, `--emit-main`, `--no-captures`, `--trace`, `--ucp` | semantic flags, not axes | | | unchanged |

So of 44 axis bits through 47, exactly two (18, 21) were wrongly unmasked.
Bits 12/13 are unmasked on purpose (`tuning.md` §2.8/§2.9, they select the
engine and `--engine=dfa` plus the denial refuses). The survey's phrase "on
artifacts they cannot act on" is the wrong criterion: the leak was on 200 of
200, including the 63/67 where the denial DID reach the artifact (see
section 3). After the fix the same sweep reads 0 moved for every masked bit
and 60/60 for 12/13/`--trace`.

## 3. Meta verdict: is `.flags` the REQUESTED or the EFFECTIVE options?

Neither, exactly, and the contract says which in one sentence:

- D43 (`decisions.md`): `.flags` = "the compile-time option FLAGS (PCREC_*
  bits, exactly as compiled)". Origin meaning: REQUESTED.
- `match_api.md` §6.3 (as amended, and restated at the section on
  round-tripping flags): `flags` "records the REQUEST ... with the
  testing/tuning denials masked OUT, because an axis that changes no answer
  must not make two identically-behaving artifacts differ in their reflection
  surface". What the emitter DID lives in the stamps and macros
  (`RX_DFA_SCAN_EDGE`, `RX_UNROLL_K_WHY`, ...), "to see what was ASKED FOR you
  cannot use `flags` for a masked axis at all".

So: `.flags` is the requested options **minus the answer-identical strategy
denials, masked unconditionally by axis class.** That is NOT the effective
options. K68's own fix masked bits 28-30 on every artifact, including ones
where they act (`^abc` forced VM, `abc$`); `-fno-possessify` is masked even
where it possessifies. An "effective options" reading would keep a bit
exactly where it acted, which no masked bit does. The rule is by class:

| class | `.flags` | members |
|---|---|---|
| strategy (answer-identical) | masked, always | everything in `axes.def` not listed below, plus `--fast-or-fail` |
| engine-selecting | kept | `-fno-atomic-discharge`, `-fno-splice-calls` |
| contract (selects semantics) | kept, masked only under `byte` | `-fno-startpos-guard`, `-fstartpos-guard=align`, `-futf-check` |
| semantic / instrument flags | kept | `-i`, `--emit-main`, `--no-captures`, `--trace`, `--ucp` |

Is the rule stated? Yes, in pieces: `match_api.md` §6.3 states the principle;
`lib/pcrec.h` and `tuning.md` state "masked" per axis, with the keep-reasons
at §2.8/§2.9/§2.23/§2.36. It was NOT stated for 18 and 21 (`tuning.md`
§2.16/§2.18 and their `lib/pcrec.h` comments were silent), which is how the
omission survived: the spec was consistent with the code. Was it applied
uniformly? No: 42 of 44 axis bits, by a hand-maintained list. Is there a
general mechanism? There was not: `axes.def` knew every axis bit and
the mask was a second, hand-typed list of them. Per-bit special-casing is
exactly what produced four incidents.

Two smaller findings from the read:

- `axes.def`'s comment on `PCREC_NO_CTX_NODE` calls it "ENGINE-SELECTING like
  atomic-discharge", yet it is masked (and `tuning.md` §2.32 says masked).
  The classification is stated both ways and never reconciled. I left it
  masked (spec and code agree; the comment is the outlier) and did not edit
  the comment; it needs the `class` column below to be settled in one place.
- The survey's §4.3 framing ("unmasked on artifacts they cannot act on")
  would, if taken as the rule, argue for a CONDITIONAL mask; the contract
  argues against it. The conditional mask is only right for the two contract
  bits, where an encoding makes them inert.

Bench consumption: per our own docs only (`k68fix_report.md`), the bench
re-pinned its reflection-surface byte-identity pins on K68 (I-111/I-112). A
bench pin of `.flags` under `-fno-size-term`/`-fno-scan-edge` would move;
nothing in this repo records one, and the move is toward the documented
rule.

## 4. The fix, and why it is the general one

`strategy_denials` is now DERIVED from `src/core/axes.def` by X-macro, with
polarity "masked unless named in `kept`" (`kept` = the two engine-selecting
denials + the three contract bits; `startpos_guard_inert`/`utf_check_inert`
still mask the contract bits under `byte`; `PCREC_FAST_OR_FAIL` is not an
axis row and is added). The ~290-line hand OR (with its per-bit narratives,
now redundant) is gone. The polarity matters more than the derivation:
every incident was "a new axis forgot to join the list" (silent, moves
bytes); under the new polarity a forgotten `kept` row is the loud direction
(one-bit red in section 6b), and a wrongly masked contract bit would fail its
positive control. The fuller [AXES-DENY-MASK] design (a `class` column in
`axes.def`, shared with [OPT-SETS] §2.8) is NOT built: it is larger (registry
dump column, spec, readers) and not needed to remove the failure; it would
also settle the ctx-node wording above. I recommend it stay a filed row; this
change is its first half and should be noted on the row.

Verification of equivalence: the same 200-pattern sweep before and after
(60 after) gives identical `.flags` for every other flag; only 18/21 changed.

## 5. What changed (commits on `lane/flagbits`)

- `src/gen/emit_dfa.c`: derived mask; `PCREC_ARTIFACT_ABI` 64 -> 65.
- abi ritual, readers found by grep (the litscan_k82h.md recipe:
  `git grep -nE 'PCREC_ARTIFACT_ABI [0-9]|ABI_EXPECT=|abi 64|ABI_SUBJ|FILEPIN|...'`
  over `src lib cli tests docs/spec Makefile scripts`): `run_codegen_tests.sh`
  (`ABI_EXPECT=65` + ledger clause), `docs/dev/history/abi_changelog.md` entry and
  the K80 `#error` example (3 digits), `run_recursion_identity.sh` (B) FILEPIN
  self-pinned to `c59fa836`, `tests/codegen/CLAUDE.md` entry. The digit is the
  same width, so no `EMITTED_BYTES` manifest moves at default flags.
- D80 spec hunks: `tuning.md` §2 ("THE `rx_info.flags` RULE", stated once),
  §2.16, §2.18; `match_api.md §6¶16` round-trip paragraph; `lib/pcrec.h` comments on
  bits 18 and 21; `src/gen/CLAUDE.md`, `lib/CLAUDE.md`.
- `tests/codegen/run_prechecks.sh` section 6b: every `-f` spelling `--list-axes`
  carries (42, counted from the registry, floor 40), two witnesses (`abc`,
  `(a|b)*c(d)`) x `byte`/`utf8`; must leave `.flags` at baseline except the
  kept members, which are listed independently of the emitter and double as
  the positive control (each MUST move). Failing direction measured: against
  the pre-fix compiler it reads 8 FAIL, exactly bits 18/21 on all four cells;
  post-fix 364 passed / 0 failed for the whole script.
- Sabotage S65/S67/S295 re-aimed (their anchors named the deleted hand list):
  the plant is now "the bit joins `kept`". `scripts/m6read_check_sab_anchors.py`:
  463 rows, all anchors resolve. Solo DETECTED runs are OWED (section 7).
- `docs/dev/known_issues.md` K92 (FIXED).

## 6. Judgement calls

- abi number 65 is provisional against concurrent bumps (the kit and the start
  table lanes also bump); the manager renumbers at merge, as r1land did, and
  the FILEPIN self-pin must then follow.
- I did not take a new sabotage row: a plant that drops a bit from a derived
  mask has no spelling; S65/S67/S295 re-aimed at the `kept` direction cover
  it, and 6b's positive control covers the opposite direction.
- `-fprefilter` is do-or-die and refuses `abc`; 6b skips that one refusal
  and uses the hybrid witness for it rather than reading a refusal as a pass.

## 7. Validation

COMPLETE on this lane (Mac, gcc-16):
- `make` clean. `run_prechecks.sh` 364 passed / 0 failed post-fix; 360 / 8 against
  the pre-fix compiler (the 8 are 6b's control: bits 18/21 x four cells).
- `scripts/m6read_check_sab_anchors.py`: 463 sabotages, all anchors resolve.
- `tests/resource/run_resource_tests.sh` standalone: one FAIL, the
  `a{5,25000} -fno-scan-edge -fno-start-pinned` rescue byte pin, which read
  762691 against 762697 (the `.flags` literal `2097152ULL` -> `0ULL`, -6 bytes).
  Re-pinned to 762691 with its derivation in the pin's comment; every other
  resource row passed.

OWED, launched DETACHED as this lane's last act (`caffeinate -s`), driver
`build/fb/chain.sh` (untracked), progress in `build/fb/chain.log`:
1. `make strict CC=gcc-16` -> `build/fb/strict.log`, line `STRICT_RC=`.
2. solo mech rows S295, S65, S67 (re-aimed; each expected DETECTED) ->
   `build/fb/mech_S295.log` etc.; S295's suites include `harness`, so it is
   long. `MECH_<id>_RC=`.
3. `make test CC=gcc-16` -> `build/fb/test.log`, `TEST_RC=`. The verdict is
   make's `*** [test-X] Error` lines (`grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'`),
   not "sections ran". Known darwin red expected: `nm could not read arm_a.o`
   in test-codegen. Anything else is mine until A/B-ed.
Completion line in `build/fb/chain.log`: `ALL_DONE`. Not run: `make test-axes`
(multi-hour per-axis sweep); the two denials' own axes could be swept with
`AXES="-fno-size-term -fno-scan-edge" make test-axes` if the manager wants it.
The `(B)` FILEPIN (`c59fa836`) names this change's last src commit and must be
re-pinned by the manager if the abi number is renumbered at merge.
