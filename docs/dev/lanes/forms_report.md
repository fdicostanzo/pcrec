# forms report — R-45 plan A: the span forms I / L / H(h), their option row, the head lever, the cards C1-C5

Lane forms (opus), 2026-11-17, branch `lane/memfn-forms` cut from `lane/memfn-span4k` @ 60c2958ae.
Design of record: `docs/design/memfn/r45_reply.md` rev 6 (69acf5376). Rulings file
`docs/dev/lanes/forms_rulings.md`: empty at every checkpoint.

## Summary

- The three span forms are built inside the window family's candidate test (`memfn/src/window.c`, THE SPAN
  FORMS): a stretch of two or more consecutive tested offsets, every entry core, one WIDE byte set and one
  table offer (not a C-run compare, not the skip entry), renders as ONE loop from the head `h` on; before
  `h` each position stays a lone test. I = `--memfn=no-span-loop` (no loop), L = `--memfn=span-loop`
  (h = 0), H(h) = the default. The shipped head is 64, labelled `UNMEASURED DEFAULT` (the grid top, set by
  the cards), so NOTHING MOVES at width 32.
- Option row `span-loop` (MF_OPT_PAIR, the deny wins); `--list-axes`'s memfn floor 13 -> 14 (registry.md
  §6¶8b); spec hunks in registry.md §6¶8a and tuning.md §2.43¶3d.
- Test-only valued lever `span-head=N` (N 0..4095; kit `mf_lever`, pcrec `--harness=span-head=N`), with the
  identity check (`cards.py identity H`): the lever at 64 is byte-equal to the default build (0 of 42 differ,
  both trees); at 8 it differs (28 of 42), the control.
- Cards C1-C5 (`kit-grid@7`, 5 rows) and their script `memfn/tests/span_forms/cards.py`: plan, dry run, timing
  (NOT run), rule R0-R5, the design's 21 drills (all pass), identity check. Dry run on the combined tree:
  1,374 cells, 269 distinct compiles, every cell built and gated, 0 failures.
- Movers: ZERO at width 32 / h = 64 (emit_sweep against 60c2958ae, full corpus; and the deny arm over the
  corpus, 0 differ). At width 4095 (the combined tree): see Movers. Main's probe `[0-9a-f]{3400}` at width
  4095: 24,024 C bytes (H(64)) against the 500,000 cap; I (the deny) is refused at 510,538 (main measured
  510,342 on its tree).
- R28-2 and R28-3: both recorded UNREACHED with their reasons, in place (compose.c ask_sel, window.c
  wdecide_framed).
- Sabotage rows S3276-S3279.

## Pieces

| piece | where | state |
|---|---|---|
| the span forms I / L / H(h) | `memfn/src/window.c` THE SPAN FORMS (`wf_span_head`, `wf_loop_len`, `wf_loop`, `wf_test_to`'s loop) | BUILT. A kind-2 one-class repeat: >= 2 consecutive offsets, every entry core, one KIT_POS_WIDE set, one table offer, not a C-run compare entry, not the skip entry. Entries before `h` render as today; from `h` on, `({ size_t J = lo; for (; J < end; J++) if (!member(S[C + J])) break; J == end; })`. Literal runs stay ONE compare (C-run, untouched): `a{k}` and `lit40` render the same text in every form (dry run). Over the existing segmenter (find_groups / c_run), as ruled |
| head selection | `wf_span_head` | deny `no-span-loop` -> INT32_MAX (I), force `span-loop` -> 0 (L), else the lever's N, else `WF_SPAN_HEAD` 64 `UNMEASURED DEFAULT: CHOSEN grid top, set by the form cards (r45_reply rev 6 §3)`. The deny wins over the force and the lever (`kit_opt_state`, new in options.c: -1 deny, 1 force, 0 neither) |
| scope fact | E-func / E-stmt | a window site the kit renders through an OLDER row (the plan translated into that row's site) keeps that row's text and does not loop: stated in tuning.md §2.43¶3d. Not declined to the floor when a plan would loop (that would move sites onto the slower floor) |
| option row | `memfn/src/options.def` `span-loop` | MF_OPT_PAIR, MF_B_ANY, MF_L_SCALAR. registry.md §6¶8a (the one pair row, its table row), ¶8b floor 13 -> 14 |
| test-only lever | `memfn/src/compose.c` `lever_span_head` (kit), `kit.h` (`KIT_LEVER_SPAN_HEAD`, `KIT_SPAN_HEAD_MAX` = MF_WREACH - 1, `art->span_head`), `cli/main.c` `--harness=span-head=N`, `src/core/internal.h` (`PcrecHarnessOptions.span_head`, N + 1), `src/gen/memfn_sites.c` | BUILT. A malformed or out-of-range N is refused by name at both layers. memfn.h's mf_lever comment and cli/CLAUDE.md's harness list (12) record it |
| identity check | `cards.py identity H [PATTERNS]` | the lever at H on the frozen `pcrec-harness` vs the rebuilt `build/pcrec`, byte for byte, both layers, over the card patterns, census covers and a predicted-movers file. At H = 64: 0 of 42 differ (this tree and the combined tree at width 4095); at H = 8: 28 of 42 differ (the check's control) |
| G2 | `memfn/tests/g2/g2_win_gen.c`, `g2_win_run.c`, `run_g2_win.sh` | the repeated-class family (own rng stream, 150 sites, heads 1..32, h-1..h+1 positions), the planted-candidate population (`G2W planted`, floor 56), loop counts per family; the default pass must loop 0 sites; head passes 0 / 8 / 24 through the lever (env `G2W_SPAN_HEAD`), each with its own loop floors |
| test-axes | `tests/axes/run_axes.sh`, `memfn_arm.py` | a pair row is two cells (`span-loop` the deny, `span-loop=force`); deny ASSERT_ZERO, force DIFFER (corpus 14 at c-default, 0 at c-vm) with witness `[0-9a-f]{32}` |
| cloud tables | `tests/ci/cloud_axes_shards.tsv`, `cloud_mech_shards.tsv` regenerated (`cloud_units_plan.py`, `--measured`); `cloud_units_plan.py` word_of: an internal arm x SIMD layer job takes its arm's word (before this the regenerated table split `--harness=mfind` into two words that each selected both jobs; cloud_axes_check.sh now PASS: 122 jobs, 32 passes) | DONE |
| R28-2 (ask_sel's verdict-first order) | `memfn/src/compose.c` ask_sel | RECORDED UNREACHED in place: kit_class writes a proof only on a FIND site; fd_pres refuses only in its PRES scope (ALL_PRESENT with pspans, fd_scope); the layout check needs npspan, which site_check refuses on every non-ALL_PRESENT site (kit_presence_check). No site writes a proof and is refused after it |
| R28-3 (`!art->err[0]` in wdecide_framed) | `memfn/src/window.c` | RECORDED UNREACHED in place: wf_plan_site sets the art's error only on a kit invariant failure (run_bytes' unspelled position, run_rank's non-strict tie row, the pinned rank's first position), each a fenced defect no stated input reaches; a witness needs a planted defect beside the conjunct's own plant |
| sabotage rows | `tests/mech/sabotages/S3276`-`S3279` | see Validation |
| NOT BUILT: a form-hash instance for the force spelling | `memfn/src/formhash.c` (r45_reply §3 "The option": "the force spelling gets its own form-hash instance") | DESIGN SITE, for the manager's ruling. The entry table's window shape (MF_FH_WINDOW) states ONE position (`fh_work.sp_set[2]`), and L needs a stop plus >= 2 core WIDE positions to loop, so an `L` entry is a new site shape, a new id read by finder_check.py's FORM_IDS (and its instance floor), rows.tsv / row_floors.tsv / arm_fixtures.c's id lists. No card in this build names a `kit:form.` dep (C1-C5 are whole-artifact cells, as J5's `enter`), so no set row can go stale on L's bytes yet: building it now is ahead of its reader (D77). Its trigger: the first set row keyed on a span form |

## Cards

- Rows: `memfn/data/cards/kit-grid.tsv` ver 7, `span_cross` (C1), `span_pop` (C2), `span_long` (C3), `span_size`
  (C4), `span_engine` (C5), UNMEASURED, deps `-` (whole-artifact cells; CARD_FORMDEP_COUNT unchanged at 20).
  DIVERGENCE from the design's text: r45_reply §3 names `kit-synthetic.tsv`; its header says its cards are the
  SYNTHETIC sets' ("test inputs, never measured"), and these are measured method cards, so they sit in kit-grid
  at a new ver (as @4-@6, none planned by the slot). For the manager to confirm or move.
- Script: `memfn/tests/span_forms/cards.py`. Cells: C1 hex/dig at k 24, 32; C2 uuid36, lit40, `(?:ab|ba|aa|bb){24}c`
  (49), `(?:abc){20}` (60), `[0-9a-f]{64}`; C3 hex and `a` at 500, 1000; C4 hex and `a` at 32, 500, 1000, 4095
  (compile only, the size cap lifted for the record); C5 the engine route on C1-C3's patterns; the A/A pair
  `lit-l16`. Arms I + the nine finite heads {0, 1, 2, 4, 8, 16, 24, 32, 64} (C1-C2), I / L / H(h*) (C3-C4); six
  regimes; both layers (SIMD-on = `-fmemfn-simd=x86-64-v3`). `plan`: 1,374 cells (AA 24, C1 480, C2 600, C3 144,
  C4 48, C5 78), 239 distinct timed compiles. The two bench-method regimes (NOT-WARM, `short-subject-search`)
  carry the kit's LABELLED approximations (an eviction sweep before each 4 KiB call; LF-separated 48-80 byte
  records) until the bench names its methods.
- Rule: `cards.py rule RESULTS [--g2 FILE]` implements R0 (defective heads out), R1 steps (1)-(5) (W(h) as the
  worst ratio to I over the cells read, a twice-void cell adding 1 only where H(h) is I there; E once, never
  chained; dominance with the fewest-dominators clause; the largest kept head; any C1-C2 cell void twice ->
  64 with the read pick recorded), the label text of R3-3, and the R2 / R3 / R4 / R5 filings. `f` = the largest
  |median ratio - 1| of the lit-l16 pair over every regime and layer; a missing A/A cell voids the night.
  `selftest`: the design's drills (i)-(xiv), R3-1's, (vii'), (x)/(xi) variants: 21 drills, 0 failed.
- Dry run (combined tree, width 4095, 1 MiB subjects): 1,374 cells built and gated against python `re`, 0
  failures. Text identical to I, per C1-C2 pattern (read off the artifacts): abc60 and lit40 at every head
  (literals stay one compare); hex24/dig24 at 24, 32, 64; hex32/dig32 at 32, 64; alt49, hex64, uuid36 at 64.
- C4 sizes (SIMD-off, emitted C bytes): `[0-9a-f]{k}` I / L / H(64): k 32 34,856 / 30,624 / 34,856; k 500
  105,495 / 30,873 / 40,226; k 1000 181,000 / 30,878 / 40,231; k 4095 660,723 / 30,882 / 40,235 (gcc -O2 -c
  6.5 s, 232 MB RSS for I). `a{k}`: one text at every form (27,555 at 32 .. 31,640 at 4095).
- **K1 (r45chk, for the kit manager to fold in).** This build answers r45read Q1 in fact: the forms branch
  respells NO pcrec caller or test of the combined branch. Its pcrec-side changes are new lines only (the
  harness option, its field, the lever call in memfn_sites.c, test-axes' pair cells, spec hunks), and
  lane/covs2b + this branch merged with ONE textual conflict (tuning.md §2.43¶3d, both sides appending to one
  paragraph: keep both) and built clean. Suggested sentence for R6 §7: "The kit's forms branch respells none of
  pcrec's callers or tests; it merges onto the combined branch with one documentation conflict (lane forms)."
- **K2 (r45chk).** One sentence for R6's regimes fallback: "a regime the bench runs takes its `lit-l16` A/A
  cells with it, so `f` is never read across two harnesses." The script computes `f` over every regime's A/A
  pair and voids the night on a missing one, so it already refuses the mixed case it cannot see.
- **covs2b W7.** The cover's proof diff (`pcrec_cover_proof_diff`, SHORT-RANGE internal error restored on the
  kit's count-bounded loop): the span loop tests the same positions a lone test would, and the plan's proof is
  per TESTED offset, so H(h) and L state the same proof range as I. Confirmed on the combined tree: every C4 /
  probe compile at width 4095 (k up to 4095, every form) completed with no internal error.

## Movers

- **Width 32 / h = 64 (this branch): ZERO.** `scripts/emit_sweep.py --ref 60c2958ae --extra=-fmemfn-simd=x86-64-v3
  --dumps-declared-new=--list-axes:span-loop` (log `/var/tmp/pcrec-pcrec/scratch/memfn/forms/sweep.log`): every
  stream, base and SIMD-on, `movers=0 asymmetric=0` (argv 7,071 patterns; composition 465 files, 38 producing;
  facts, emit-ir-auto x4, stderr; dumps 7 with the one declared new row). The script exits rc=1 on ONE
  notice, the arms family's `NO DIFFER FLOOR PINNED` for the `--extra` arm (SIMD-on against SIMD-off on BOTH
  sides, 59/59 c-default, 33/33 c-vm: no pin exists for that arm), not on a mover.
- **The option's arms over the corpus (this branch, width 32):** deny `no-span-loop` 0 differ in every cell
  (byte/utf8 x c-default/c-vm x SIMD off/on, 5,516 patterns); force `span-loop` (L) 14 corpus patterns differ
  at c-default (both encodings, both layers), 0 at c-vm.
- **Width 4095 (the combined tree, `--window-search-width=4095`, the same arm over the corpus):** default H(64)
  against I: **1** corpus pattern, `[ab]{1000}` (c-default, both encodings, both layers; c-vm 0). L against
  the default: 16 corpus patterns (18 / 17 with witnesses). Every other long census cover holds a literal run
  (`a{500}`, `(?:abc){20}`) or a stretch under 64 positions (k 36, 40, 49, 60), so H(64) is I there.
- **Main's probe** `[0-9a-f]{3400}` at width 4095 (combined tree): H(64) 24,024 C bytes byte / 26,311 utf8; L
  15,181 / 17,587; I REFUSED by the 500,000 cap at 510,538 / 511,891 (main measured 510,342 on its own tree; the
  same pattern with the cap lifted: 510,119 bytes written). The default now fits the cap with a ~20x margin.
- No default-width byte moved, so no STOP and no abi event.

## abi

- No pcrec abi event: no default-width byte moves (Movers). `PCREC_ARTIFACT_ABI` stays 108.
- No kit-contract event: no seam struct, vocabulary or class field changed (`art->span_head` and the lever bits
  are kit-internal; `mf_lever`'s signature is unchanged, it gains a NAME). MF_SITE_ABI 30, MF_CLASS_V 11.
- Caller-observable: the `span-loop` option row (`--list-axes`, `--memfn=`), spec hunks in the same change
  (registry.md §6¶8a/¶8b, tuning.md §2.43¶3d).

## Validation

Local, `nice`, -j4, each under gnutimeout, 2026-11-17 02:56-03:34; logs under
`/var/tmp/pcrec-pcrec/scratch/memfn/forms/` (`val_*.log`, `val.log`). No full `make test`, no queue job, no timing.

| check | verdict |
|---|---|
| `make strict` | rc 0 |
| `make test-codegen` | rc 0 |
| `make test-registry` (the `--list-axes` memfn floor 14) | rc 0 |
| `make test-rxtsource` | rc 0 |
| `make test-resource` | rc 0; "the allocation-failure injector's four witnesses: ... none is silently absorbed" (absorbs 0) |
| `make test-memfn-link` (R-28 frames), `-manifest`, `-stamps`, `-arms`, `-deleg`, `-arch`, `-forms`, `-reach`, `-targets`, `-rows`, `-guarded`, `-simdfloor`, `-d27region`, `-rank`, `test-kitproof` | each rc 0 |
| `make test-memfn-d27frame` | rc 0 (controls red in all 4 runs) |
| `make test-memfn-finder` | rc 0, 28,905 passed, 0 failed |
| `make test-memfn-g2` (quick) | rc 0, 70,358,673 passed, 0 failed |
| G2 window family, `memfn/tests/run_g2_win.sh` (default + heads 0/8/24) | rc 0, 29,580 passed, 0 failed; loops at default 0; head 0: mass 34, report 199, random 17, repeated 59; head 8: mass 1, random 3, repeated 24; head 24: repeated 9; planted 63 |
| `tests/memfn/run_arch_blind.sh` | rc 0 |
| G7 lever fence `tests/compound/run_lever_fence.sh` | PASS (3 checks, 4 controls), after one fix (my first `word_of` spelled the harness option's prefix in tests/ci; respelled) |
| `tests/axes` memfn arm (`MEMFN_REACH_ONLY=1`) | OK, 64 checks passed, 0 failed |
| `tests/ci/cloud_axes_check.sh`, `cloud_mech_check.sh` | PASS (122 jobs + 32 passes; 1,315 ids in 90 shards) |
| sabotage anchors `scripts/m6read_check_sab_anchors.py` | all anchors resolve (S1026 re-anchored: run_axes.sh's cell loop is one indent deeper) |
| `scripts/check_claudemd_size.sh --all` | within limits |
| cards: `cards.py selftest` | 21 drills, 0 failed |
| cards: `cards.py dry` (combined tree, 1 MiB subjects) | 1,374 cells, 269 distinct compiles, 0 failures |
| cards: `cards.py identity 64` / `identity 8` | 0 of 42 differ / 28 of 42 differ (control) |
| sabotage rows, `tests/mech/run_sabotage_matrix.sh S3276 S3277 S3278 S3279 S1026` at 6c923adbe | `mech run COMPLETE: 5 rows (unexpected: 0, undetected: 0, unreached: 0, anomalies: 0)` |

The rows, quoted:

    S1026-memfn-axes-arm-flag-dropped  axesmemfn  axesmemfn:170fail/230pass  DETECTED
    S3276-span-loop-end-short          g2win      g2win:124fail/23556pass    DETECTED
    S3277-span-loop-mixed-sets         g2win      g2win:157fail/23523pass    DETECTED
    S3278-span-loop-force-ignored      axesmemfn  axesmemfn:4fail/396pass    DETECTED
    S3279-span-head-lever-ignored      g2win      g2win:6fail/23674pass      DETECTED

Not run here: the cards' timing (a kit window main clears), the full `make test`, cloud runs.

## STATE AT HANDOFF

- Rulings file: empty at every checkpoint; last entry applied: none.
- Branch `lane/memfn-forms`, every piece committed (WIP commits per piece). The scratch combined tree
  `worktrees/forms-comb` (lane/covs2b 28af649c9 + this branch; one doc conflict resolved) was removed with
  `scripts/wtprune --apply --force forms-comb`.
- For the manager: (1) the kit-synthetic vs kit-grid@7 home of the cards (Cards); (2) the force spelling's
  form-hash instance, not built, its trigger named (Pieces); (3) K1/K2 sentences for R6 (Cards); (4) the joint
  landing will meet the same tuning.md §2.43¶3d conflict (keep both sides' sentences).
- OWED: none
