# r17a — R17-a, the zero-mover seam of R-17 (BUILD)

Lane r17a (opus), 2026-10-12, for the memfn kit manager. Branch `lane/r17a`,
cut from `lane/memfn-r17` at `89626ec9`. Design followed:
`docs/design/memfn/setfind.md` rev 2.3 §11.1 (with §2, §7, §10, §12.5,
§R4-§R6). Box: the Linux dev box, every heavy-ish command `taskset -c 12-15`,
`-j4`.

**Verdict: built, ZERO MOVERS on every stream measured, every light suite
green, the four refusal rows DETECTED solo.** The full sweep, `make test`,
G2 full and the derived mech re-runs are OWED to the kit manager's slot (§8).

## 1. What changed, per file

**Kit (`MF_SITE_ABI` 10 → 11, no `MF_VOCAB` move):**
- `memfn/include/memfn.h` — abi 11 and its log line; `MF_MOVE_UNBOUNDED` /
  `MF_OVER_UNBOUNDED` (reserved); `mf_pred.window_stated` / `move_back`
  (int32, signed, D161's origin) / `overshoot` (W0-W2, appended last);
  `mf_site.decl_point` (W4, appended last, the host capability with its
  refusals stated); `MF_OP_FIND` gains the W3 result meaning (non-wrapping;
  back < 0 refused; not extended to ALL_PRESENT's `ret_pred`); `fn_ref`'s
  STMT reading (W5, the opaque stem); `mf_result.reads_table` / `includes`
  (appended last); entries `mf_locals` and `mf_defined`; `mf_art_end`'s
  comment names the storage refusals.
- `memfn/src/fields.def` — class `D_MIN`; fields `window_stated` (OBLIG),
  `move_back`, `overshoot`, `decl_point` (OBLIG); `fn_ref` doc gains the STMT
  reading (K2-12).
- `memfn/src/gate.c` — the four classifiers: W0-W2 read on a FORWARD FIND
  only (unstated elsewhere, like `fold_kind`), W1/W2 only under W0 1;
  `decl_point` a flag on every site.
- `memfn/src/kit.h` — `kit_window_site`, `kit_d_min`; site record
  `def_s`/`def_n`/`placed`; two arm columns appended last (`reads_table`,
  `includes`); `MF_SERVES_WINDOW_TODAY` (W0 YES, W1 D_MIN, W2 ZERO, W4 any).
- `memfn/src/compose.c` — `window_check` (last of `site_check`): forward FIND
  must state W0 1; every other site, reverse sites and every `preds[]` entry
  state 0; W1/W2 only under W0; back < 0 refused (UNBOUNDED exempt, then
  refused by the gate); `decl_point` 0/1. `mf_define` copies a decl_point
  site's `s`/`n` texts. `mf_locals` (refused: no point offered, placed twice,
  `s`/`n` text differing from the define's; writes nothing today). `mf_use`
  refuses a decl_point site before its `mf_locals`. `mf_art_end`: "never
  placed", then "placed, never read", then the old "never used".
  `mf_defined` (form id, `reads_table` = row column AND a tabled SET term,
  `includes` = row column).
- `generic.c`, `pffind.c`, `ofsskip.c` (arm + `fn_rows[]`), `precheck.c`,
  `runcmp.c`, `mismatch.c`, `vrun.c` — every contract includes
  `MF_SERVES_WINDOW_TODAY`; every arm states its two new columns (PF walk
  rows, ofsskip, precheck x3: `reads_table` 1; every libc-writing row:
  `includes` `MF_INC_STRING_H`).

**pcrec (a contract seam, zero-mover, NO abi bump):**
- `src/gen/memfn_sites.{c,h}` — `pcrec_memfn_window_is_candidate` (W0 1, W1 =
  least term offset, W2 0); doors `pcrec_memfn_locals`, `pcrec_memfn_defined`;
  `PcrecFind.stem` (W5; set ⇒ W4 offered, define-then-use only).
- `src/gen/emit_dfa.c` — `find_site` split into `find_site` (states W0-W2, and
  W4/W5 when a stem is named) + `find_hooks`; `pcrec_emit_find` refuses a
  stem (one-call FINDs stay the byte rows and MLINE); `struct MemfnFind` and
  `find_define` / `find_locals` / `find_use` (D11 bound checked against the
  define); N4 `find_door` (probe builds); `ofs_site_define` states the window;
  `CandPf.emit_define` (NEW, see §6 D1) with `pf_define_find[_bounded]` on the
  three set rows; `DfaForm.pf_find` / `pf_stem` (stem `<fn>_pf`, set by
  `emit_unanchored` and `emit_rev_end`'s relocate); `pf_emit_find` uses the
  defined site where one exists; `unanch_scan` places `mf_locals` (§6 D2);
  `pf_tables_bcls` / `pf_tables_first` emit iff `reads_table` (+ door); VM
  hat: `vm_hat_find_of`, `pcrec_emit_vm_start_define`, and
  `pf_vm_emit_first_class` = locals + `start_set` iff `reads_table` + use at
  entry, use at retry, ONE handle.
- `src/gen/emit_vm.c` — `vm_emit_search_body` calls
  `pcrec_emit_vm_start_define` beside `pcrec_emit_req_run_blocks` (stem
  `<searchfn>_run_pf`).
- `src/core/internal.h` — the define's prototype; `Job.mf_vmhat`.

**Tests / checks:**
- `tests/memfn/arm_fixtures.c` — `fx_win`/`FXW` (fixtures state a forward
  FIND's window at the kit call, as pcrec does); `seq_case` / `seq_cases`:
  19 cases (protocol renders; `s`/`n` differ; twice; unread; never placed;
  use first; no point; none offered renders; decl_point 2; W0 unstated;
  back < 0; back > 0; back UNBOUNDED; overshoot; W1 under W0 0; W0 2;
  reverse; SKIP).
- `tests/memfn/run_arm_pins.sh` — the 19 expectations; `GATE_CASE_FLOOR`
  79 → 98; check 6's doc.
- `memfn/tests/g2/g2_gen.c`, `g2_simd_gen.c` — `g2_win`/`G2W` at all 15 kit
  calls (NOT blinded text; marked so in both files and memfn/tests/CLAUDE.md).
- `tests/memfn/rank_check.py` — N4 door: fails on any `N4 door` error,
  floors the `FINDDOOR` passes per table.
- `tests/memfn/site_manifest.tsv` — PF row names `find_define` and the new
  helpers (C17 rule 2 was red without it).
- `tests/mech/sabotages/S846-S849` — the four refusal rows (§4).
- CLAUDE.md: `memfn/`, `memfn/include/`, `memfn/src/`, `memfn/tests/`,
  `src/gen/`, `tests/memfn/`, `tests/mech/`.

## 2. Zero-mover evidence

Reference `build/r17a_ref/build/pcrec` (git archive `lane/memfn-r17`
`89626ec9`), working `build/pcrec` at `45cf4b5b` (the last src change);
`scripts/emit_sweep.py --ref-bin … --bin … --no-self-check --jobs 4`, chain
`build/tmp/sweep_chain.sh`, logs `build/tmp/sweep_{plain,start,simd,utf8}.log`
(in the worktree, gitignored):

| run | streams / population | movers |
|---|---|---|
| plain (`--every 4`) | c-default, c-vm, emit-ir-vm, facts, emit-ir-auto x4, stderr: 5,645 each (full corpus: `--every` thins only the arms); composition 384; dumps 7 | **0 on every stream**, rc 0 |
| start (`--every 8 --arms start`) | the same streams + the start arms on 568 distinct patterns, byte and utf8 bases, every deny arm | **0**, rc 0 |
| simd (`--every 4 --extra=-fmemfn-simd`) | streams 1-4 + the rest at -fmemfn-simd on both sides, 5,645 | **0** (rc 1 = the instrument's "NO DIFFER FLOOR PINNED" for an `--extra` arm, not identity) |
| utf8 (`--every 4 --extra='-e utf8'`) | the same at `-e utf8`, 5,645 | **0** (rc 1 likewise) |

Plus a hand sample of 119 compiles over all three set rows (byte-class,
byte-class-bounded, first-class-bounded), the VM hat, offset/run rows, at
default / vm / `-fno-offset-skip` / `-fno-run-prefilter` / utf8 /
`-fmemfn-simd`: 0 differences.

**The first sweep found 9 movers** (c-default; `possessive.rxt` x2,
`counterk.rxt`, `handoff.rxt` x2 …): R-15's `precheck_assign_byte` row names
its local `<p>_mf<handle>_q`, and defining the find at `emit_block` (before
`pcrec_emit_req_run_blocks`) renumbered the pre-check from handle 1 to 2.
Fixed by D1 (§6); the re-run above is clean. This is §7.6's
handle-renumbering hazard, observed on an existing row.

## 3. Suite verdicts (this box, pinned, all on the final code unless noted)

| suite | verdict |
|---|---|
| `make -j4`, `make strict` | clean, clean |
| `test-codegen` | rc 0, 3m20s (`build/tmp/codegen2.log`; [SABANCHOR] inside it: 701 rows, 723 sites, all resolve) |
| `test-memfn-arms` (C5 pins + gate cases) | 383/0 |
| `test-memfn-rows` | 157/0 |
| `test-memfn-forms` | 5/0 |
| `test-memfn-deleg` | 5/0 (first red: `mf_result` on the stack, check 4; moved to the arena) |
| `test-memfn-stamps` | 25/0 |
| `test-memfn-guarded` | 10/0 |
| `test-memfn-simdfloor` | 51/0 |
| `test-memfn-rank` (+ N4 door) | 15/0; door passes can_begin_match 1,574, start_bytes 78, start_set 3,441 (floors 1400/70/3100) |
| `test-memfn-manifest` (C17) | 11/0 (first red: `find_define` unlisted; PF row updated) |
| `test-memfn-link`, `-reach`, `-arch` | 8/0, 4/0, 15/0 |
| `test-memfn-g2` (G2 quick) | 52,987,686/0, 6m31s (`build/tmp/g2.log`); run before D1, which touched no kit or G2 file |

N4 door control: a planted set mismatch (one bit flipped in the set handed to
the kit, the table untouched) failed the compile with `internal error: N4
door …` on all three tables (`[xy]\d+\b -fno-offset-skip`, `\b[xy]\d`,
`--engine=vm a(b|c)+d`).

## 4. Sabotage figures (solo, `tests/mech/run_sabotage_matrix.sh <id>`, logs `build/tmp/mech_<id>.log`, at `45cf4b5b`)

| id | plant | detector | figure |
|---|---|---|---|
| S846 | `same_text` always equal (mf_locals' `s`/`n` binding) | locals-n-differs, locals-s-differs | reach ok(2/2), memfnarms 2fail/381pass, DETECTED |
| S847 | "placed twice" refusal guarded `if (0)` | locals-twice | reach ok(1/1), 1fail/382pass, DETECTED |
| S848 | "placed, never read" disabled (falls to the field-less never-used text) | locals-unread | reach ok(1/1), 1fail/382pass, DETECTED |
| S849 | W0 0 accepted: site_check AND gate (two edits) | window-unstated | reach ok(1/1), 1fail/382pass, DETECTED |
| S478 (named re-run) | VM hat table drops its lowest member | vmhat | reach ok(1/1), vmhat 770fail/18pass, DETECTED |

S849 needs both edits: measured, the site_check plant alone is masked by the
gate (`no row serves this site: \`window_stated\` (R2: stated as NO…)`).

## 5. Re-aims and the derived re-run list

- **Re-aims: none needed.** [SABANCHOR] exact-count: all 701 rows resolve.
  One anchor broke during the build (S07: `unanch_scan`'s comment +
  `scan_position` lines) and was kept by placing `mf_locals` above the
  comment instead (D2), not by re-aiming. S478's anchor line moved into
  `vm_hat_find_of`, text and column unchanged; intent re-verified (it still
  drops the member from the emitted `start_set`; the site's set follows it,
  so the N4 door, correctly, does not fire) and re-run DETECTED.
- **Derived re-run list** (`docs/design/start_table/sabotage_anchors.py
  build/r17a_ref build/tmp/cg_ref.txt …/refactor_edit_set.tsv --repo .
  --step r17a=89626ec9..HEAD`, `build/tmp/sa_step_r17a.tsv`; exit 2 is the
  pre-existing unresolved S176/S571/S640): **57 src rows** (hunk 51, reach 6):
  S06 S07 S36 S63 S85 S88 S141 S144 S168 S181 S221 S223 S255 S283 S284 S287
  S370 S371 S400 S430 S448 S462 S469 S473 S478 S481 S483 S524 S556 S566 S594
  S595 S596 S598 S599 S600 S610 S738 S741 S745 S758 S759 S760 S764 S765 S766
  S768 S770 S771 S772 S777 S780 S785 S786 S787 S789 S790.
  The tool reads `src/` only; kit-side rows whose anchor sits within 25
  lines of a changed hunk in `memfn/` (`build/tmp/kit_rerun.txt`): **S526
  S619 S681 S682 S722 S803**. Of all these only S478 was re-run here.

## 6. Deviations from §11.1, with reasons

- **D1. The DFA define point is a NEW hook `u.pf.emit_define`
  (`pf_define_find[_bounded]`), not `u.pf.emit_block`.** It is called at file
  scope above the body like `emit_block` (so the hybrid gets it), but AFTER
  `pcrec_emit_req_run_blocks`. Placed at `emit_block` the find was defined
  before the pre-check, renumbered its handle, and moved R-15's
  `<p>_mf<handle>_q` in 9 artifacts (§2). `emit_block` itself is unchanged
  (and `ofs_test_of` still keys on it). Two functions (bounded / unbounded)
  because the D11 bound must be a define-time fact; the use checks it.
- **D2. `mf_locals` sits in `unanch_scan` just ABOVE the "FORWARD SCAN"
  comment**, not between it and `size_t scan_position`, so S07's anchor
  keeps its text. Dominance is the same (before the loop and its `seedhead`
  jump, function scope). R17-b's declaration will print above that comment.
- **D3. W0's rule reads "forward FIND".** §2.2 refuses W0 0 on a FIND and W0 1
  on a reverse site, which together refuse every reverse FIND; I read it as
  forward FIND ⇒ 1, everything else (reverse included) ⇒ 0. No pcrec builder
  states a reverse FIND; G2 does, and stays green.
- **D4. Refusals added beyond the list:** `move_back`/`overshoot` nonzero
  under W0 0 (no silent values where nothing is stated; `fold_kind`'s
  precedent), W0 on a `preds[]` entry, `decl_point` > 1, and `mf_locals` on a
  site with `decl_point` 0. Each has a gate case.
- **D5. The storage refusals apply to EVERY decl_point site**, not only to a
  row that keeps storage (§7.1 says "for a row that keeps storage"). At R17-a
  no row keeps storage, so the protocol is checkable only this way (and
  S846-S849 are reachable only this way); pcrec's sites obey it.
- **D6. `includes` is a row-level bound** (an arm column), and `reads_table`
  an arm column AND "a SET term states a table". The kit accumulates
  includes at use time, so a per-site exact value at define would need the
  use; pcrec reads neither field except `reads_table` on the PF sites.
- **D7. The test drivers state the window at the kit call** (`fx_win`,
  `g2_win`) rather than editing each site constructor, so perturbation and
  refusal cases keep the refusal they were written for. G2's change is
  non-blinded and marked.
- **D8. N4 lives under `PCREC_RANK_PROBE`** (the existing idiom, §11.1 item
  4 allows it): the assertion runs where the table is emitted (the define now
  precedes it on both routes), against the set the defined site carries.
  `rank_check.py` gained its verdict and floors; `[vm-table]`'s use of the
  door record is R17-b's.
- **D9. emit_sweep used `--ref-bin`/`--bin` and `--no-self-check`** instead of
  `--ref … --tree-rev HEAD` (the same two binaries, built once, light).

Not deviations, as specified: no new row, no kit form change, no shared
helper block or renderer (K3-10), W6 not appended, `mf_flush_helpers`
unchanged, no pcrec abi bump, no spec hunk (§11.3's are R17-b's).

## 7. Notes for R17-b

- Handles feed names (`generic.c` `<p>_mf<h>`, `mismatch.c`, R-15's
  landmark): any reorder of defines can move bytes. D1 is the instance.
- `mf_locals` writes nothing yet; the arm interface has no `locals` hook —
  R17-b adds the storage row's.
- The door record exists; `vmhat_checks.py [vm-table]` and S841 are R17-b's.

## 8. OWED to the kit manager's slot (heavy, not run here)

1. `scripts/emit_sweep.py` FULL: `--ref lane/memfn-r17 --tree-rev <tip>` with
   self-check, `--arms start` at `--every 1`, `--variant all`, `--trace`,
   and the `-fmemfn-simd` / `-e utf8` extras.
2. `make test` via `scripts/perfrun --label r17a -- LOG` (verdict
   `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'`).
3. `make test-memfn-g2-full`.
4. mech: the 57 derived src rows (§5) + kit rows S526 S619 S681 S682 S722
   S803 (S846-S849 and S478 done, §4).
5. The N2 census (`n2_report.py --floors`): the MF_TRACE build's field table
   grew by four fields and one class (REACH lines can gain cells).
6. Main: annotate D155 addendum 4's "lands in R17-a" (the renderer is R17-b's,
   K3-10) — the design's own owed item, unchanged.

## 9. Charter vs committed

| charter item | committed |
|---|---|
| MF_SITE_ABI 10 → 11 | yes |
| W0-W2 on every FIND builder; W4/W5 on the three set sites | yes (find_site, ofs_site_define; set rows + VM hat); byte sites and MLINE W4 0, no fn_ref |
| define-then-use: DFA set rows at file scope, VM hat beside the run blocks; order define → locals → table iff reads_table → use | yes (DFA via `emit_define`, D1; locals placement D2) |
| `mf_result.reads_table`/`includes` via `mf_defined`; table iff reads_table | yes (D6) |
| mf_locals + refusals (twice, never placed, s/n differ; plus use-before, unread) | yes (D4, D5) |
| N4 door in trace/test builds | yes (D8), control fired |
| no new row / form change / helper block | none added |
| zero movers proven by emit_sweep sample + own sample | yes, 0 movers (§2) |
| make, strict, memfn suites, codegen, G2 quick | all green (§3) |
| sabotage S846-S849 solo, reach real | 4/4 DETECTED, reach ok |
| anchors re-derived, re-aims | 0 re-aims; derived list §5 |
| CLAUDE.md + memfn.h contract comments | yes |
| report with OWED list | this file |
