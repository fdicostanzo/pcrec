# bsu2fix report: review r75's fixes to R-47 U2 (lane bsu2fix, sonnet)

## STATE AT HANDOFF

- Branch `lane/bsu2fix`, cut from `lane/bsu2` @ d9d86e39e (U2 + U2b, abi 111). Two content commits on top
  (cca26a4a6 the gate and the trace readers; c1dcbcaea the kit self-check, rev 4.2, spec and help text) plus this report's.
- Rulings file `docs/dev/lanes/bsu2fix_rulings.md` was empty at every re-read (before each commit and this report): no ruling applied.
- All FIX-NOW and DOC items of r75's MANAGER RULING are applied; the PLAN items (U3) and the `wrap-clang` answer are NOT mine and
  untouched. No abi number moved (111). No emitted byte moved (IDENTITY).
- In-lane green: `nice make -j2`, `make strict` (rc 0), the fixed gate on the clean tree, every plant, the light identity checks.
- OWED (queued box jobs, named in OWED RUNS): `kit-bsu2fix-test`, `kit-bsu2fix-mech`, `kit-bsu2fix-gate`, `kit-bsu2fix-ids`.
  Not run in-lane: `make test-codegen` and the G2 window family (both are sections of `kit-bsu2fix-test`; the box was held by
  the queue's `kit-bsu2-test` and a lock wait would have idled this lane).

## THE JOB

Apply r75's FIX-NOW and DOC items to U2 exactly as the MANAGER RULING (kit, 2026-11-21) says, with no emitted byte moving, each
check fix proven against the code round's plant, and `block_span.md` rev 4.2 recording D201 add. 4. Stop rule: any moved byte,
a fix needing more than the review's text, or floors not holding on the clean tree: none tripped.

## FIXES APPLIED

- **CHECKS-1+3** (`tests/memfn/span_vector_identity.py`): `FLOORS` per cell: default movers at least 28 byte / 20 utf8 (c-default, width
  32), 0 on c-vm, 31 at width 4095 (the V sites of the committed `span_seed.rxt`; the seed's patterns are always in the corpus
  population so the floors hold at any `--every`). A cell that compiled nothing fails; fewer than 41 seed patterns fails.
  Plants: `deadv` (every V row dead) FAIL by floor (was PASS); `noseed` FAIL ("0 span_seed.rxt patterns, fewer than the committed 41").
- **CHECKS-2**: at each mover the default-vs-deny diff (GNU diff -U0 of the same binary's two artifacts) must be one pure insertion
  of one `__body` + one selector definition per site, and one single-line walk hunk per site whose only change is the stretch ->
  one `<p>_mf<h>_vs<j>(S, C)`; one call per defined site. Plant `vsite_extra` (an extra byte and a doubled call only at V sites) FAIL
  (was PASS); `vcall_drop`, `vcall_rename`, `bytemove_default` FAIL.
- **CHECKS-4**: mask rows are named (M1..M9), applied first-match; a group is replaced only where it equals THAT SIDE's stated abi
  (`--ref-abi`, `--abi`, required, cross-checked against the probe artifact's M1 and M2), others stay and show; per-row hit counts
  printed per side and cell. The hard slice is gone. Plants: `abimask_all` (abi 999 in every mask spelling, was PASS) now refused at the
  probe; `abinonmask_all` FAIL; `bytemove_deny` FAIL. An invented row can no longer be added without a code edit that names it.
- **CHECKS-5**: the `-fmemfn-simd=x86-64` layer is in `LAYERS` (corpus, utf8 and seed4095 cells): 3 layers, 15 cells.
- **CHECKS-7**: S3280's `SAB_DESC` names `wf_span_h`; `memfn_arm.py`'s span-vector comment says the three bench texts are corpus
  patterns counted inside the floor they back.
- **SLOT-1**: chose "the readers tolerate" the tag: `(?:[a-z_]+=\S+ )*?` before `chosen=` in `tests/memfn/reach_equal.py` (the one that
  actually missed wfS ENDs), `memfn/tests/g2/run_part_census.py`, and the two traced-define greps (`memfn/tests/run_g2_win.sh`,
  `tests/memfn/run_finder.sh`); `memfn/docs/trace_format.md` states it. The trace's own bytes did not move.
- **SLOT-2**: `fd_tables_check` (`memfn/src/finder.c`, declared in `kit.h`, called from `mf_art_begin` next to `wf_tables_check`): each
  `fd_named_id` must be a row id of `fd_rows`. Plant (R7w -> "R7W"): every artifact compile now errors ("the memfn kit refused ...");
  before, it compiled and silently dropped T-vscan. Sabotage **S3510** (`tests/mech/sabotages/S3510_fd_named_id_typo.sh`, suite `codegen`)
  is the committed form. The general form (named-row index) stays PLAN.
- **SLOT-5**: `docs/design/memfn/block_span.md` rev 4.2: status and history, a D201 add. 4 row in the FREEZE NOTE, R-4's record cited
  as the kit's r69 ruling, the CONSTRAINT collapsed to arm 1, §2.2 ANSWERED, §2.1's U2b record and COMPILER SCOPE, OPEN owner question
  `wrap-clang` (new §2.2.1), §14/§15 text, §18.0a dispositions table.
- **SLOT-6**: `tests/memfn/decider_census.tsv` lists the six wfS rows.
- **CONTRACT-2**: the `span-vector` help string (`memfn/src/options.def`, `--list-axes`) and registry §6¶8a / tuning §2.43¶3d say U2
  does (a call of a function whose one body is the inline test, at every setting and target; no vector body is built).
- **CONTRACT-3**: "walks to the stop with the default set walk" in registry ¶8a and tuning ¶3d.

## DOC ITEMS

- **CENSUS-1/2/4/5** (in rev 4.2 §2.1): the grid's DIFFERS set is three classes at every k 16..31: `\w` (20 lines), `[aeiou]` (38,
  a block reorder), `[A-Za-z0-9_-]` (2); 48 of 128 eligible. At width 4095 the same three at every sampled k 32..1000. Under `-e utf8`
  hex and `[0-9]` differ at `{25}`, `{28}` (10-13 lines); the 3 bench patterns stay identical (4 of 4). `\w{20}` is 20 by GNU diff
  or difflib `autojunk=False`; the 42 / 26-22 / 24-20 spread was difflib's autojunk.
- **CENSUS-3**: the census is gcc 15.2 -O2. The 3 real bench sites are identical under gcc -O1/-O2/-O3 (also -fPIC, -march=native) and
  differ under clang 21 -O2/-O3 (`\d{32}` 264 lines, hex 12) and gcc -Os (5 lines each), both widths. Recorded in §2.1; owner question
  `wrap-clang` OPEN in §2.2.1 (relay to Frank is main's).
- **CHECKS-6**: §14 states the identity gate is a delivery step (its reference is a pre-merge build); the repeatable floors are
  `memfn_arm.py`'s span-vector DIFFER rows; a pinned reference commit is a PLAN item.
- **CONTRACT-1**: one sentence each in registry ¶8a and tuning ¶3d: the call's text can push a pattern within a few hundred bytes of
  `PCREC_MAX_VM_EMIT_CODE_BYTES` (width near 4095) over it where the deny compiles.
- Relays to main (per the ruling, not done here): [BSPAN-SCALAR-RISK]'s shape list (`[aeiou]`-like, `[A-Za-z0-9_-]`-like, utf8 hex/digit
  k, the clang/-Os fact); the abi 110 reservation's record.

## IDENTITY

Reference builds (scratch): BASE 0481a4130 (abi 109) and d9d86e39e (abi 111), built with `make` from `git archive`.
- Fixed gate, clean tree, light run `--every 400` (56 corpus patterns incl. the 41 seed ones; 12 corpus cells + 3 seed4095 cells, 795
  compiled): **deny differs 0 in every cell**; default movers **28 byte / 20 utf8 (c-default, all three layers), 0 (c-vm), 31 (seed4095,
  all three layers)** = the floors; mover_not_vsite 0; PASS. Mask hit counts printed (M1-M5 hit each, M6-M9 0 on this population).
- Bytes vs d9d86e39e (no mask: same abi): the 41 seed patterns x {off, v3, x86-64, deny, width 4095, width 4095 v3, utf8, vm}:
  **0 of 328 differ** (compiled 41 per cell, all ok). The full-corpus identity sweep is OWED (`kit-bsu2fix-ids`).
- `--list-axes` carries the new help text; no emitted artifact text reads it (seed sweep above is the proof: 0 moved).

## OWED RUNS

Queued as the last act (non-timing, all end well before 01:00); the verdict of each is read from its queue result:
- `kit-bsu2fix-test`: `make test` via perfrun (log `/var/tmp/pcrec-pcrec/scratch/bsu2fix/maketest.log`); includes test-codegen,
  the G2 window family, test-registry, the claude-md size check. Verdict: `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'` empty.
- `kit-bsu2fix-mech`: S3510 (new) and S3280 (description). Expect `== mech run COMPLETE: 2 rows`, 0 unexpected/undetected.
- `kit-bsu2fix-gate`: the fixed gate at `--every 10` against the BASE build (all cells). Expect PASS, deny 0, movers 28/20/31.
- `kit-bsu2fix-ids`: `emit_sweep` of this tip vs d9d86e39e (corpus --every 8: off, v3, x86-64, utf8, deny; seed at 4095: off, v3, deny).
  Expect 0 movers in every cell (logs `scratch/bsu2fix/ids_*.log`).
If any moves a byte: STOP and report; do not land.
