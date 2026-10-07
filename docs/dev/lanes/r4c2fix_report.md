# r4c2fix — [MEMFN] R4c′: the pcrec manager's R4c review fixes (2026-10-07)

Lane r4c2fix (opus), branch `lane/r4c2fix`, cut at main 81bc13de, with
`lane/memfn-r4c2` merged in (docs only, clean). The item list is the R-4
"note: 2026-10-07" entry in `memfn/docs/responses.md`. None of these items
may move an emitted byte. The zero-mover gate below is how that is shown.

## 1. Summary (resume from here)

All items (a)-(g) and the nits are committed. The light validation is
complete and green: `make strict` and the touched make sections (§3).
**OWED (launched detached as this lane's LAST act):**
- the zero-mover gate `scripts/emit_sweep.py --ref 81bc13de`, judged by
  `memfn_r4c_gate.py --zero-dumps`;
- the four touched/added mech rows solo (S511, S524, S525, S530).

They run as one chain. Its summary goes to
`worktrees/r4c2fix/build/scratch/final/summary.txt`. It is complete when
that file's last line starts `R4C2FIX-DONE`. Each step's log sits beside it
(§4).

## 2. Items

| item | commit | what | evidence |
|---|---|---|---|
| (a) | 4f2b401f, re-shifted in 4c39ded2 | r4ccore_report.md §3's B1-B18 re-pinned. Each entry was re-located by READING the code at 81bc13de. The old pin was 917a3624, before FLAGBITS (00ede5dc) and Q-G2-18 (5c652bbb) shifted most of the file by ~250 lines. (c) then inserted lines (+2 after line 1472, +8 after 1504), so every number was moved and re-checked line by line on this tree. | 48 line numbers spot-printed with `sed -n Np` after the shift; each one prints the read it names. |
| (b) | 4f2b401f | B19 = `pcrec_fact_req_run(cx)->len >= 2` in `pcrec_emit_req_byte_check` (now :1525, the guard on B5′). B20 = `ofs_pred_of`'s per-term need classification (:1083-1107: predicate REQUIRED, scan byte OPTIONAL plus its plan hint unless it lies in the run, run term REQUIRED, k-set terms OPTIONAL with a table only when multi-byte). | Both re-located by grep and read. |
| (c) | 4c39ded2 | `pcrec_emit_req_byte_check` now fails the compile when `mf_pre` is NULL and `req_admit_emits(req_admit(cx))` says a pre-check is emitted: `pcrec_ctx_fail(cx, 0, "internal error: a search entry uses a pre-check the admission emits, but no site was defined for it")`. With no site and a declined admission it still emits nothing. Header sentence updated. Added as B21 to the list (a consistency read, not a decision). **Sabotage row S530**, the lowest free id of S530-S549 (S550+ are main's): the plant deletes `emit_unanchored`'s `pcrec_emit_req_run_blocks` call. The detector is the `harness` arm on `tests/litscan/reqcube.rxt`. SAB_REACH: `frank|fred` is unanchored DFA with `RX_REQ_WHY "emitted"`. | Failing-direction proof (scratch trees, same plant): WITH the fix, `pcrec --features all --pattern 'frank\|fred'` → rc 1, the internal error. WITHOUT the fix → rc 0, and the pre-check silently drops out. `VALIDATE_ONLY=1` on S530: valid. Matrix verdict OWED (§4). Internal diagnostic, no `docs/spec/` hunk (not caller-observable on a correct build). |
| (d) | 12a7936f | `memfn_r4c_i2.py --selftest` gains three INERT-branch plants on the real one-binary `-fmemfn-simd` inert log: c-default bytes moved (differ=3/3), a c-vm stamp moved (stamp=1/1), the c-vm row missing. Logs are now picked by their `extra=[...]` header across pooled LOGDIRs, the inert one also by `sides=ONE BINARY`. The 91f5b607 run's `-fmemfn-simd` arm (i2_2) compared REF with the tip and is not an inert arm; picking it read the clean control red, which is why that test exists. A log that is not found FAILS the selftest. A plant that does not apply FAILS. | `--selftest r4c-lx-results/build/scratch/r4c_lx r4c-lx-results/rerun/build/scratch/r4c_lx`: 8/8 plants red, 3/3 undoctored logs green, rc 0. With the first dir alone: rc 1 ("no i2_*.log with extra=['-fmemfn-simd']"). |
| (e) | 1d99a5ea | **Chose: cover both layers** (cheap: one more pcrec compile per sampled artifact, +~10 s on the quick tier). Each pattern-stream artifact is now compiled at `-fno-memfn-simd` AND `-fmemfn-simd`, and each must be byte-equal to the default. The docstring now says the default IS `-fno-memfn-simd` (so (a) only restates it), and that the ON side is replaced by the movers half at R4e′. Runner header and the tuning.md §2.43 sentence updated. | quick: both "identical (no SIMD form)" PASS lines, 548 artifacts, `checks failed: 0`. Plant (a scratch wrapper pcrec that appends a comment under `-fmemfn-simd`): `FAIL: FORMS identity (SIMD-on) ... differs`, rc 1. Full `make test-memfn-stamps`: §3. |
| (f) | 7081dc30 | The 0-byte `m_lahf-lm.txt` is replaced by the re-probed `m_sahf.txt` (copied from `worktrees/r4c-lx-results/gccmacros2/`, 15564 B; adds `__LAHF_SAHF__` over the baseline). C4's population loading (`read_population`) now FAILS on any dump with no `#define`. A scratch control on every run empties the first `m_*.txt` of a copy and requires the refusal. References fixed: c4_populations/CLAUDE.md (dumps use gcc's own flag spelling; an empty dump fails), tests/memfn/CLAUDE.md, and r4clx_report.md's probe list (`lahf-lm` → `sahf`, with a note). No other reader names the file (grep). | On the OLD dump: `FAIL: population gcc15.2-x86_64-ubuntubudu: m_lahf-lm.txt is an EMPTY dump`, `checks failed: 1`. After the swap: 37/37 and 48/48 plants hit (18 dumps), empty-dump control PASS, `checks failed: 0`. |
| (g) | 6e8d5ec1 | S524 and S525 demand `checks failed: 0` on the clean tree, like S526/S527. S525 had only SAB_REACH_POP, so it gains the same SAB_REACH (`run_form_checks.sh`). tests/mech/CLAUDE.md says so. | `VALIDATE_ONLY=1`: both valid. Clean `run_form_checks.sh`: `checks failed: 0`. Matrix verdicts OWED (§4). |
| nits | 7f5e466a | S511's header describes its CURRENT plant (MLINE / `emit_attempt`), with the re-aim history wrapped beneath. `strategy_denials`: lib/pcrec.h (§2.43's contract comment) and tuning.md §2.43 now name it identically: "`emit_info_def`'s `strategy_denials` mask (src/gen/emit_dfa.c), under tuning.md §2's derived `rx_info.flags` rule", which masks force bits too. Spellings grepped: `strategy_denials` is the only one; the variable is unchanged. | `VALIDATE_ONLY=1` on S511: valid. |
| gate tool | e4355941 | `memfn_r4c_gate.py` required the dumps stream to show exactly ONE mover (R4c's `--list-axes` rows against e6e6d6eb). Against 81bc13de that mover cannot exist, so the gate as written would read a correct run red. New `--zero-dumps`: every stream, dumps and facts included, must read 0 movers. The default mode is unchanged. | On the R4c Linux gate log: the default mode PASSES (unchanged); `--zero-dumps` FAILS on its dumps mover (correct). The same log doctored to dumps=0 PASSES, and doctored to c-default movers=2 FAILS. |

## 3. Validation (Mac, light)

- `make strict`: rc 0, "whole tree compiles clean with -Werror -Wshadow".
- Sections, each run alone (`build/scratch/sections.log`):
  `test-memfn-arch` rc 0 (12 s; C4 `checks failed: 0`, 37/37 + 48/48
  population plants, empty-dump control PASS), `test-memfn-forms` rc 0,
  `test-memfn-manifest` rc 0, `test-memfn-reach` rc 0, `test-memfn-link`
  rc 0, `test-memfn-stamps` rc 0 (47 s, the FULL C11: 14 passed / 0 failed,
  both layers "identical (no SIMD form)"), `test-memfn-g2` rc 0 (66 s),
  `test-registry` rc 0 (177 s; PC-3 213/0, five `checks failed: 0`
  summaries). No `*** [test-` line in any section log. The one `FAIL` grep
  hit is the survey text `(*FAIL)`.

## 4. OWED: the long chain (detached; launched as this lane's last act)

`build/scratch/final/chain.sh`, run under nohup + caffeinate. Steps, in
order:
1. `python3 scripts/emit_sweep.py --ref 81bc13de` → `final/gate.log`,
   judged by `memfn_r4c_gate.py --zero-dumps` → `final/gate.judge`.
   Required: `R4C-GATE PASS (--zero-dumps)`. The floors are Linux's
   (4165/4166/4166/38). A Mac reach below a floor would be a population
   finding, not a mover; read `gate.log`'s stream lines.
2. `bash tests/mech/run_sabotage_matrix.sh S511`, then S524, S525, S530,
   one id per call → `final/mech_<id>.log`. Required: each verdict line
   DETECTED with reach ok.

Completion line: `R4C2FIX-DONE gate=<rc> mech=<ids not DETECTED or none>`,
the last line of `final/summary.txt`.

## 5. Charter vs committed

- [x] read BOILERPLATE, memfn/CLAUDE.md, coding_guide, learnings §3
- [x] merge lane/memfn-r4c2 alone (clean), then `make`
- [x] (a)+(b) first, in their own commit (4f2b401f); interim message sent
- [x] (c) loud internal error, sabotage row S530, failing-direction proof
- [x] (d) inert-branch plant(s) in the I2 selftest
- [x] (e) both layers, not just the docstring (said which, and why)
- [x] (f) m_sahf.txt in, m_lahf-lm.txt out, references fixed, empty dump FAILS, proved by a control
- [x] (g) S524/S525 reach line
- [x] nits: S511 prose; strategy_denials naming
- [x] CLAUDE.md files: tests/mech, tests/memfn, tests/memfn/c4_populations, docs/design/memfn/probes/lxrun
- [x] docs/spec: only the tuning.md §2.43 sentences (naming; C11's both-layer check). (c) is internal, so no hunk.
- [x] make strict; touched sections individually
- [ ] OWED: solo mech rows S511/S524/S525/S530 (§4)
- [ ] OWED: zero-mover gate vs 81bc13de (§4)
- [ ] not done (the kit manager's, per wake §4): R4c's `done:` post, journal line
