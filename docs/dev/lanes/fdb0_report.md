# fdb0 — R17-b′ step B0: R17-a's seam ported to main

Lane fdb0 (opus), 2026-10-16, for the memfn kit manager (pcrecdev3). Branch
`lane/fdb0`, cut from the kit branch `lane/memfn-fd` = main `063b4a4b4`
(abi 78, `MF_SITE_ABI` 10). Design: `docs/design/memfn/r17b_prime.md` rev 2
(on `lane/memfn-r17`) §0, §1.1, §1.6, §3.1 (row B0), §3.4 (B0's rows), §4.9.
Box: the Linux dev box, every build and suite `taskset -c 12-15`, `-j4`.

**Verdict: PORTED, ZERO MOVERS, NO pcrec abi event; `MF_SITE_ABI` 10 → 11.**
Every R17-a code commit applied to main without a conflict and with no
semantic re-work; see §2 for the evidence and §6 for what is OWED.
One note on the trace: the ordered (non-gating) compare differs because the
VM hat's define asks its start row once more (§2).

## 1. What was ported, by R17-a commit

R17-a is `f2b16c801..9cc286ef7` on `lane/r17a` (report
`docs/dev/lanes/r17a_report.md`, already on main since `2514f8074`). Each
commit was cherry-picked in order onto main; the kit files it touches
(`memfn/include`, `memfn/src`, `memfn/tests`, `tests/memfn`) are unchanged
between R17-a's base `89626ec9` and main, so the only files where main had
moved are `src/gen/emit_dfa.c`, `src/gen/emit_vm.c`, `src/core/internal.h`,
`tests/memfn/site_manifest.tsv` and the CLAUDE.md files. All auto-merged.

| R17-a commit | lane commit | content | applied |
|---|---|---|---|
| `f2b16c801` | `51f75f235` | the seam: `memfn.h` (abi 11, W0-W2, W4, W5's STMT reading, `mf_locals`, `mf_defined`, `mf_result.reads_table`/`includes`), `fields.def`, `gate.c`, `kit.h`, `compose.c` (`window_check`, the storage refusals), every arm's two new columns; pcrec's `find_site`/`find_hooks`/`find_define`/`find_locals`/`find_use`, `CandPf.emit_define`, `DfaForm.pf_find`/`pf_stem`, `pcrec_emit_vm_start_define`, `Job.mf_vmhat`, N4's `find_door` | clean (3 files auto-merged) |
| `05cf55041` | `0a4c5ec57` | fixtures and G2 state the window (`fx_win`, `g2_win`); `seq_cases` (19 refusal/protocol cases); `GATE_CASE_FLOOR` 79 → 98 | clean |
| `ccf7f51a4` | `5a5b160ef` | sabotage rows S846-S849; CLAUDE.md updates; `mf_result` on the arena | clean |
| `9c267671d` | `5096e996b` | `mf_locals` above the FORWARD SCAN comment (S07 keeps its anchor); `rank_check.py` counts `FINDDOOR` | clean |
| `30e4c1d6f` | `9bcda0b86` | `memfn/CLAUDE.md`'s MF_SITE_ABI 11 narrative | clean |
| `7699beaf5` | `8ff930af8` | N4 door floors; the PF manifest row names `find_define` | clean |
| `45cf4b5be` | `34f5bd9aa` | the define moves to `u.pf.emit_define`, after the run pre-check's site (R-15's handle order) | clean |
| `9cc286ef7` | `1934361ac` | report + lanes index + `tests/memfn/CLAUDE.md` rank note | report and index ALREADY on main; only the CLAUDE.md note ported (the lanes-index conflict resolved to main's text) |
| (kit `fa72eaa5c`, slot24 triage) | `977fea388` | N2 `pf_walk` pcrec floor 608765 → 430563 (R17-a's define-once VM hat) | ported, see §4 |

Lane-only commits beyond the port: `977fea388` (the floor, and one stale
sentence in `src/gen/CLAUDE.md`: "`ofs_test_of` now keys on `PF_SCAN_OFS`"
was true of R17-a's first commit and false after its own `45cf4b5be`;
`ofs_test_of` still keys on `emit_block`, `src/gen/emit_dfa.c` line ~6861),
and this report.

### 1.1 What did not apply, and why

- **Nothing in the code.** Main's movement since R17-a (B3 the match-end
  mark, [COMPOUND] B0-B4, K110, seambuild, CAND-PATH-READS, the
  [REQ-HANDOFF-L1] re-entry) touches none of R17-a's hunks' meaning: every
  DFA set-row body is still written by `emit_unanchored` or by
  `emit_rev_end`'s relocate (the only two callers of `u.pf.emit_block`, and
  now of `u.pf.emit_define`), and the VM hat's two seeks are still the two
  `pcrec_emit_vm_start_seek` calls under one `vm_emit_search_body`. A
  compound's parts run the unchanged pipeline, so each part defines its own
  sites (D163). Proven by the sweeps in §2, not by this argument.
- **`r17a_report.md` and its lanes-index line**: already on main (the kit
  docs import `2514f8074`); not re-added.
- **slot24's `precheck_assign_byte` floor (PLACEHOLDER → 20088)**: NOT
  ported. It is main's own item (class (a) in `slot24_triage.md`: R-15's row
  went `reach pcrec` with L1, before R17-a) and was measured on the kit
  branch; main's next N2 census pins it.
- **R17-b** (`pf_terms_mask`, `terms.c`, abi 77 on the kit branch): not
  touched, per the brief (B4's byte move).

## 2. Zero-mover evidence

Reference `build/ref063/build/pcrec` (`git archive 063b4a4b4`, built in the
worktree), working `build/pcrec` (lane tip, src identical to `34f5bd9aa`).
Chain `build/land/chain.sh`, verdict lines `build/land/verdict.txt`, logs
`build/land/sweep_*.log` (worktree, gitignored).

Every sweep `scripts/emit_sweep.py --jobs 4`, pinned `taskset -c 12-15`. The first five
use `--ref-bin build/ref063/build/pcrec --bin build/pcrec --no-self-check`; variants and
trace use `--ref 063b4a4b4 --tree-rev 34f5bd9aa` (both sides built by the tool, self-checks
run). Population: the full corpus, argv 5,790 patterns, composition 386 files / 106
artifacts, dumps 7.

| run | streams | movers | rc and why |
|---|---|---|---|
| plain | c-default, c-vm, emit-ir-vm, facts, emit-ir-auto ×4, stderr, composition, dumps (11) | **0 on every stream**, 0 asymmetric | 0 |
| start (`--arms start`) | the 11 + 4,624 distinct patterns × every start arm, byte and utf8 bases, null arm | **0** on every stream; every arm's DIFFER count equal on both sides (e.g. `-fno-start-set` 302/302, `-fno-offset-skip` 528/528) | 0 |
| simd (`--extra=-fmemfn-simd`) | the 11 | **0** | 0 |
| utf8 (`--extra='-e utf8'`) | the 11 | **0** | 0 |
| vm (`--extra=--engine=vm`) | the 11 | **0** | 1: `COMPOSITION ARTIFACTS FLOOR VIOLATION: 86 < 100`. The floor is the plain arm's; `--engine=vm` composition produces 86 artifacts on BOTH sides (movers 0). The same instrument property slot24_triage.md §2 found for the utf8 arm; main's, not B0's |
| variants (`--variant all`, byte + utf8 bases) | 90 cell-streams | **0 on all 90**, 0 asymmetric; self-checks PASSED | 1: 40 TAG FLOOR lines, every one printed identically for side a (main) and side b (lane), e.g. `no-backreference 461 < 462` ×6 cells, `no-size-cap` and `stderr-default` on the lowered-cap cells. Main's `VARIANT_PINS` are stale against main itself (B3/B4 since the last re-pin); slot24_triage.md §1's class (a) |
| trace (`--trace`) | c-default, c-vm, both orders built | gate **CLEAN** (SET compare); trace builds' stdout = default builds' on 0/0 | 0. The ordered compare (a diagnostic, not gating) differs on 7,719 sequences: `pcrec_emit_vm_start_define` asks the VM route's start row once more at define time, so the working side carries extra copies of records the reference already has (c-vm 168,701 → 179,405 records; c-default 509,269 → 512,495). Expected from R17-a's define-then-use and invisible to the SET gate by design |

Verdict lines: `build/land/verdict.txt`; logs `build/land/sweep_{plain,start,simd,utf8,vm,variants,trace}.log`.

Plus a hand sample before the chain: 12 patterns × 7 arms (default,
`--engine=vm`, `-e utf8`, `-fmemfn-simd`, `-fno-offset-skip`,
`-fno-rev-end`, `-fno-start-landing`) at `--features all`, `.c`, `.h`,
stderr and rc compared: 84 compiles, 0 differences.

## 3. Suite verdicts (this box, pinned, lane tip)

| suite | verdict | wall |
|---|---|---|
| `make -j4` | clean | — |
| `make strict` | clean | 12 s |
| `test-memfn-arms` (C5 pins + 98 gate cases incl. R17-a's 19) | 383/0 | 2 s |
| `test-memfn-rows` | 157/0 | 1 s |
| `test-memfn-forms` | 5/0 | <1 s |
| `test-memfn-deleg` | 5/0 | 1 s |
| `test-memfn-stamps` | 25/0 | 20 s |
| `test-memfn-guarded` | 10/0 | 75 s |
| `test-memfn-simdfloor` | 51/0 | 28 s |
| `test-memfn-rank` (+ N4 door) | 15/0; door 5,151 tables equal; populations can_begin_match 1,570 / start_bytes 80 / start_set 3,501 (floors 1400/70/3100) | 12 s |
| `test-memfn-manifest` (C17) | 11/0 | 3 s |
| `test-memfn-link`, `-reach`, `-arch` | 8/0, 4/0, 15/0 | 8 s |
| `test-registry` | 79/0 | 59 s |
| `test-rxtsource` | 298/0 | 67 s |
| `test-codegen` (SABANCHOR inside) | rc 0 | 4 min 48 s |
| `test-memfn-g2` (G2 quick) | 52,987,686/0 | 7 min 13 s |

Logs `build/land/<section>.log`. No `*** [... test-` line in any.

## 4. MF_SITE_ABI readers, found by grep

`git grep -n 'MF_SITE_ABI'` over `*.c *.h *.py *.sh *.def Makefile`, minus
comment lines, and `git grep -i site_abi -- docs/spec docs/dev/history`:
- the DIGIT has two readers, both moved by R17-a's own commits:
  `memfn/include/memfn.h:39` (`#define MF_SITE_ABI 11` and its log line) and
  `memfn/include/CLAUDE.md:4` ("It carries `MF_SITE_ABI` 11");
  `memfn/CLAUDE.md` gains the narrative paragraph;
- every code reader uses the SYMBOL (`compose.c:546`'s check;
  `memfn_sites.c:203`, `arm_fixtures.c:220`, `g2_gen.c` ×7,
  `g2_simd_gen.c:302` set `s->abi = MF_SITE_ABI`; `g2_gen.c`'s abi±d
  refusal cases are relative), so none pins a number;
- `docs/spec/` and `docs/dev/history/` carry no `MF_SITE_ABI` reader (the
  kit's contract number is not caller-observable; B0 has no spec hunk,
  r17b_prime.md §3.4).

The N2 floor (`tests/memfn/row_floors.tsv`, `arms pf_walk`) is a COUNT reader
that moves with R17-a without citing the number: the VM hat is now defined
once and used at both seeks, so its define-phase selections halve
(slot24_triage.md §3's decomposition, `580 + 3204` defines against
`580 + 2 × 3204` uses on the kit branch). Ported as slot24 measured it
(430563 = floor(0.9 × 478404)); main's next full N2 census re-reads it
(OWED, §6).

## 5. Sabotage rows and their reach

Solo runs, `bash tests/mech/run_sabotage_matrix.sh <id>` at `977fea388`, logs
`build/land/mech_<id>.log`; each trailer `mech run COMPLETE: 1 rows (unexpected: 0,
undetected: 0, unreached: 0, anomalies: 0)`.

| id | plant | detector | figure |
|---|---|---|---|
| S846 | mf_locals' `s`/`n` comparison always passes | locals-n-differs, locals-s-differs | reach ok(2/2), memfnarms 2fail/381pass, DETECTED |
| S847 | "placed twice" refusal guarded off | locals-twice | reach ok(1/1), 1fail/382pass, DETECTED |
| S848 | "placed, never read" disabled | locals-unread | reach ok(1/1), 1fail/382pass, DETECTED |
| S849 | W0 0 accepted (site_check AND gate) | window-unstated | reach ok(1/1), 1fail/382pass, DETECTED |
| S478 (re-run: its anchor line moved into `vm_hat_find_of`) | VM hat table drops its lowest member | vmhat | reach ok(1/1), vmhat 773fail/18pass, DETECTED |

The figures equal R17-a's on the kit branch (r17a_report.md §4) except S478's vmhat count
(770 → 773, main's corpus grew). R17-a's G2 and fixture cases (`fx_win`, `g2_win`, the 19
`seq_cases`, `GATE_CASE_FLOOR` 98) came over unchanged and pass (§3).

Derived re-run list for this step
(`docs/design/start_table/sabotage_anchors.py build/ref063 build/tmp/cg_ref.txt
docs/design/start_table/refactor_edit_set.tsv --repo . --step
fdb0=063b4a4b4..34f5bd9aa`, `build/tmp/sa_step_fdb0.tsv`; exit 2 is the
pre-existing UNRESOLVED S176/S571/S640 plus [COMPOUND]'s S897/S906, none in
a file this lane touched): **51 src rows** (hunk 45, reach 6): S06 S07 S36
S63 S85 S88 S141 S144 S168 S181 S221 S223 S255 S283 S284 S287 S370 S371 S400
S430 S448 S462 S469 S473 S478 S481 S483 S524 S556 S566 S594 S595 S596 S598
S599 S600 S610 S738 S741 S745 S759 S768 S770 S771 S772 S777 S785 S786 S787
S789 S790. Kit-side rows anchored within 25 lines of a changed `memfn/`
hunk (the tool reads `src/` only): S526 S619 S681 S682 S803, plus S722 from
R17-a's own list. Re-aims: none ([SABANCHOR] inside `test-codegen`, §3).
S284 is declared UNDETECTED (expected) since s1build.

## 6. OWED (heavy, to the kit manager's slot)

1. mech: the 51 derived src rows and the six kit rows of §5 (S846-S849 and
   S478 were run here, §5). Note slot24's judge reading: `unexpected: 0`,
   `unreached: 0` (S284 is a declared UNDETECTED).
2. `make test` via `scripts/perfrun --label fdb0 -- LOG`.
3. `make test-memfn-g2-full`.
4. The N2 census (`n2_report.py --floors`) on main + B0: re-reads the ported
   `pf_walk` floor and fills main's `precheck_assign_byte` PLACEHOLDER.
5. Main's pre-existing emit_sweep pin items, if still open at the slot
   (slot24_triage.md §1-§2: the thin-tag manifests, the lowered-cap tag
   floors, the composition floor applied to `--extra` arms). Not B0's.

## 7. CLAUDE.md files

Updated by the ported commits: `memfn/CLAUDE.md` (MF_SITE_ABI 11
narrative), `memfn/include/CLAUDE.md`, `memfn/src/CLAUDE.md`,
`memfn/tests/CLAUDE.md`, `src/gen/CLAUDE.md` (the defined FIND; the
`ofs_test_of` sentence corrected here), `tests/memfn/CLAUDE.md` (fixtures'
window, `seq_cases`, the N4 door note), `tests/mech/CLAUDE.md` (S846-S849).
`docs/dev/lanes/CLAUDE.md` gains this report's line. No file was added or
removed outside `tests/mech/sabotages/` (four rows, indexed in
`tests/mech/CLAUDE.md`).

## 8. Charter vs committed

| charter promise | artifact |
|---|---|
| port R17-a's seam to main (W0-W2, `decl_point`, `mf_locals`, `mf_defined`, storage refusals, set FIND sites defined at file scope) | commits `51f75f235`..`34f5bd9aa` (§1), all clean picks |
| MF_SITE_ABI 10 → 11, readers by grep | `memfn.h:39`, `memfn/include/CLAUDE.md:4`; grep in §4 |
| zero pcrec movers, no pcrec abi event | §2: 0 movers on every stream of plain/start/simd/utf8/vm/variants, trace SET clean; abi stays 78 |
| sabotage S846-S849 ported and reached | §5, all DETECTED solo |
| G2 / fixture / refusal cases ported | `0a4c5ec57`; arms 383/0, G2 quick 0 failed |
| `make strict`, `test-codegen`, registry, rxtsource, memfn sections | §3, all green |
| what did not apply, said rather than forced | §1.1 |
| CLAUDE.md files updated | §7 |
| heavy runs NOT run (make test, test-axes, mech batch, san) | OWED §6, owner: kit manager's slot; trigger: B0's merge into the kit branch |
| derived mech re-run list | §5 (51 src + 6 kit rows), OWED §6 item 1 |
| N2 census on main + B0 | OWED §6 item 4 (kit manager's slot) |
| report | this file |
