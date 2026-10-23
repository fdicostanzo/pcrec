# i1tri — triage of I1's red `make test` (job 610) (lane report)

Lane i1tri (opus), 2026-10-21, continuing `lane/i1build` from `4d4aa0cd9`.
Brief: diagnose and fix the four red sections of queue job
`610-i1build-maketest` (test-codegen, test-anchored-match,
test-cpset-structure, test-dfa-uniform-fold), explain why the predicted reds
(compound, partlayout, encoding-checks) did not appear, re-queue the chain.
Rulings file `i1tri_rulings.md`: empty at every checkpoint (no entry applied).

## 0. Premise and the finding that reframes it

`scripts/verdict` on 610's `job.log.make` names exactly the four sections
(premise holds). **But 610 did not complete.** perfrun pipes make through
`scripts/sectiontimes stamp`, which reads stdin strictly as UTF-8; a `0xff`
byte in make's output raised `UnicodeDecodeError` (in `job.log`), the pipe
closed, and make died of SIGPIPE. `job.log.make` ends mid `test-vars` output
(line 5774); no `sections ran` trailer; every section scheduled after that
point never reported. So:

- **compound / partlayout / encoding-checks did not go red because they
  never reached their check** (no output from `run_compound_unit.sh`,
  `run_partlayout_tests.sh` or `run_encoding_checks.sh` in the log). The
  i1build predictions are untested, not refuted.
- The log's last output is a **real I1 defect in test-vars** (fix 5 below),
  which was never counted red because make's error line was never written.
- perfrun reported `class=RED-REAL contaminated=YES`; the class is right for
  the four sections it saw. None of them is load contamination.

Harness finding for main (not fixed here, main-tree file): `sectiontimes`
should read stdin as bytes or with `errors="surrogateescape"`; a
non-UTF-8 byte in any test's output kills the whole run. The re-queued job
sets `PYTHONIOENCODING=utf-8:surrogateescape` in its own environment (it
reaches sectiontimes, which runs without `-I`/`-E`; it changes only how an
undecodable byte on a std stream is handled, where the strict path crashes).

## 1. Fix-by-fix

| # | section / check | diagnosis | fix | commit |
|---|---|---|---|---|
| 1 | codegen `run_codegen_tests.sh` body() (skip states, anchored fast path, minimization, M2.7, M2.12, engine selection, OS-1, OS-0b, M6.2-WORDB, k24 control) — ~40 FAILs | STALE: I1 moved every engine body from `<p>_search` into `<p>__find` (`static inline __attribute__((always_inline))` / `static __attribute__((noinline))`); body() matched `^(static )?int rx_search(` and read the forwarder | body() head admits `inline` + one attribute; engine callers ask for `rx__find`; the two-engine fixture renames engine B's `rx__find` to `rx_search_b` | 59d5a9e8d |
| 2 | codegen [M5-SEAM] D58/DD-12(7) — ~75 FAILs | STALE (4 test-parser gaps the I1 text exposed): (a) the twins' `static` is on its own line, so `residual_names` read `rx__next_pos` etc. as exported; (b) `rx_next` (the iterator entry) is fixed surface; (c) the shared block's one-line body `{ ... }` left `calls_in_bodies` "inside a body" for the rest of the file; (d) attribute heads named every such function `__attribute__`. Then two LEGITIMATE moves: engine bodies call the twin `rx__X`, which IS a residual call; the iterator's `<p>__step` advances with `next_pos` (the find-all caller protocol, `main`'s case); `<p>__bind_checks` is one more `-futf-check` caller-position site | the four parser fixes; twin tokens counted with the entry's; `rx__step` allowlisted with `main`; `residutfdfa` 2->3, `residutfvm` 3->4 | 59d5a9e8d |
| 3 | codegen [OPT-HYB-RESEED] 13 FAILs | STALE: the VM search loop is `<p>__find`, `_search_run` is range test + guard over it | `rs_body` reads `rx__find` | 59d5a9e8d |
| 4 | codegen [K35], [TT-9] | REAL test hygiene of I1's new scripts: `run_residual_twins.sh:67` unguarded `sort -u`; `run_iter_diff.sh` in no sanitizer manifest | `LC_ALL=C`; `tests/findall/run_iter_diff.sh` added to `tests/lib/san_scripts.txt` (it compiles through `$GENCFLAGS`) | 59d5a9e8d |
| 5 | test-vars `caseless.rxt` (log tail, never counted) | **REAL I1 DEFECT**: a utf8 var-bearing VM artifact does not compile — `<p>_vars_resolve` calls the static twin `<p>__var_valid`, defined later with the other twins and declared nowhere ahead of it (pre-I1 it called the exported `rx_var_valid`, declared in the prologue). Witness `'^${v}$' --features vars -e utf8` | `vm_emit_vars_resolve` call moved below `pcrec_emit_residual_inline`'s block in `vm_emit_search_body`, text unchanged; witness + `-i` variant gcc-clean | 8d5536143 |
| 6 | codegen run_comments_axis.sh [D112] 9 FAILs | **REAL I1 DEFECT** (emission hygiene): `<p>_iter_buffers`' doc comment sits outside the shared block, unbracketed, so it shipped in every default `.h` | bracketed `PCREC_CMT_NONESSENTIAL` inside the scaffold bracket; `-fcomments` unchanged; the 9 CASES default artifacts read clean | 7bd781b74 |
| 7 | test-dfa-uniform-fold §3, 14 disagreements | **REAL I1 DEFECT** (stamp honesty): `<PREFIX>_DFA_UNIFORM_FOLDS` folds over the path members only; the retry machine `Job.nedfa`'s folded accessors were emitted but uncounted (every witness is reports_empty) | `dfa_uniform_folds` adds `nedfa`'s folds where the retry is emitted (`retry_ok && NEXT emitted`, the emission's own condition); match_api.md §6.3.4¶9 (`0..8`), abi_changelog 83 entry. All 14 witnesses: stamp == text | 7bd781b74 |
| 8 | test-cpset-structure [5b] | REAL (structural rule): I0's `rw_node` shares an arm `case A_WCLASS: case A_CLASS:` | separate arms (widths.c:121's shape); same answer; `run_wclass_census.sh` part 1 green | 7bd781b74 |
| 9 | codegen run_dfa_stamps.sh [start] 62 | STALE: `<p>__retry` writes `capture_spans[0][0] = search_from`, which the reader took for the search's pinned start | the reader skips the `rx__retry` body; the failing witnesses read their stamp | 59d5a9e8d |
| 10 | codegen run_facts_checks.sh [facts-decisions] | STALE: `RX_ITER_INIT(s_, n_)` is the shared block's caller macro, read as a stamp | `ITER_INIT` joins MACHINERY | 59d5a9e8d |
| 11 | codegen run_inline_capability.sh arm B | STALE: the textual strip removed `always_inline` from `<p>__step`/`__step_own`, which carry it at every rung (the entry shape dials the search chain, not `_next`) | the strip skips the step heads; arm B's two spellings byte-identical on the witness | 59d5a9e8d |
| 12 | codegen run_n1_budget.sh raised budget | LEGITIMATE MOVE, spec stale: the notempty retry machine is MANDATORY (compile.c `build_notempty_dfa`, I1's design), so on the nullable witness it is charged to the auto budget; re-bisected: 5,999 trips, 6,000 does not (was 3,500/4,000). limits.md §3.3.4¶1 said "only against the two mandatory machines" | raise 5000 -> 8000, header re-measured; limits.md §3.3.4¶1 names the third machine | 59d5a9e8d |
| 13 | test-anchored-match §2 (4) | STALE: the positive half read `^int rx_search(` | reads `rx__find` | 59d5a9e8d |
| 14 | identity gate (B) | owed by 6/7/5 (emitted bytes) | FILEPIN self-pinned 7bd781b74, then 8d5536143 | 674105c46, dac8cdb8c |
| 15 | mech anchors | `m6read_check_sab_anchors.py`: S02, S05 stale after fix 1 | re-anchored, mechanism unchanged (S02 still drops the head anchor; S05 leaves engine B's `rx__find`, a double definition); all 922 anchors resolve; both added to the mech job | a21d2d7ce |

Emitted-byte changes are inside I1's own abi 83 event (unmerged): no bump.
No ABI shape, entry or I1 design element changed. Nothing above contradicts
the i1build report except its reds forecast (§0).

**Not validated by me beyond the witnesses named**: every edited script ran
only in extracted pieces (helpers sourced against fresh artifacts); the
suites themselves run in job 611.

**Possible design question (no action taken)**: fix 12 means a nullable
DFA-eligible pattern now falls back to the VM at roughly 1.5x lower
auto-budget spend than before I1 (at the 30,000,000 default no corpus
pattern is near it). Making the notempty machine OPTIONAL instead (fall back
to a VM-guard retry, or decline the retry) would be a design change, so it
is only named here.

## 2. Ids

No sabotage ids, D or K ids used. Proposed for the manager: a K entry for
the `sectiontimes` strict-UTF-8 crash (a run killed by one byte, reported
as RED-REAL on the sections that happened to finish).

## STATE AT HANDOFF

Head `lane/i1build` = the commit carrying this report (after a21d2d7ce).
Last rulings entry applied: none (file empty). Job scripts (uncommitted
scratch) in `worktrees/i1build/build/i1jobs/`: `611-i1build-maketest`,
`621-i1build-mech`, `631-i1build-census`, `641-i1build-parity`, added to the
queue in that order (owner i1build), chained by readiness so nothing runs on
a red predecessor:

| job | runs | ready when | green line |
|---|---|---|---|
| `611-i1build-maketest` | `make -j8`, `make strict`, `scripts/perfrun --label i1build --shape 8,8` (full `make test`; src changed) | at once | `scripts/verdict` on `job.log.make` reads `VERDICT GREEN`; perfrun `DONE rc=0`; no `*** [Makefile:N: test-` line. Expected: compound / partlayout / encoding-checks may now go red as i1build §4 forecast (re-pins, not answers) — they never ran in 610 |
| `621-i1build-mech` | S1297-S1308, S504 S701 S891 S902 S1126 S1151 S693, S02 S05 | `boxqueue after i1build-maketest` = 0 | `== mech run COMPLETE: 21 rows` with 0 unexpected (verdict GREEN) |
| `631-i1build-census` | `tests/findall/mover_census.py` I0 vs I1 | after i1build-mech green | the census exits 0 (CLEAN, no UNEXPLAINED) |
| `641-i1build-parity` | parity timing, PARITY_POST=1 | after i1build-census green + the quiet gate | `== parity COMPLETE 24 verdict rows`; cells c1, c3, c4 read `GATE I PASS` |

If 611 is red, 621-641 wait (their `after` answers 75); the reader triages
611 and `boxqueue cancel`s or retries the rest.
