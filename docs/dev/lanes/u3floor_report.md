# u3floor — `make test-memfn-simdfloor` re-aimed for the target seam (U2+U3)

STATE: delivered on lane/u3tgt (tip at handoff: see `git -C worktrees/u3tgt log -1`). Rulings
applied: R4 and R5 (R5 is the last entry in u3tgt_rulings.md).

## Summary

- **The premise held.** The full section at f8cd86c33 was red because every ON artifact failed
  (main-u3tgt-sections: `checks failed: 130663`). The guard lint rejected the TARGETS, guard and
  region lines, leg (a) found preprocessed text that differed, and routing_shape rejected the
  one-call selector.
- **No floor dropped (STOP RULE not hit).** Per target, the movers and SIMD FUNCs are 55 and 55 at both x86-64 and x86-64-v3 on the full corpus. That is up from the pre-seam 46, because the corpus grew. Every selector calls its target's top level: w16=55 at x86-64, w32=55 at v3. The floors are re-pinned to 55.
- **The check now covers what the seam does.**
  - The population is every corpus cell at `-fmemfn-simd=T`, for every target T whose family has
    a level (x86-64 and x86-64-v3 today), compared against `-fno-memfn-simd`.
  - The lint takes the admitted spellings from the kit's own table. `simd_levels.c` now dumps the
    targets with `mf_target_c_of` / `mf_family_c_of` text.
  - The lint admits exactly that scaffolding, and only at the places the sheet puts it.
  - Five plants run on every target's first mover, on every run.
- **The full section is GREEN:** `bash tests/memfn/run_simd_floor.sh` (the file `make test-memfn-simdfloor` runs) at 94de5432f + the target_text refactor (the run started after that edit): 10,195 cells x 2 targets, `checks passed: 20414`, `checks failed: 0` (scratch/u3floor/full.log). The floors were pinned from that run. The pin commit changes only the constants.
- **R4: libc_census re-aimed too, through one shared cutter.**
  - `tests/memfn/target_text.py` is the ONE reader of the target's own text: the table, admission,
    `cut`, and `aside`.
  - simdfloor's lint cuts with it.
  - C11's movers half now compares the ON artifact to the default with the target's own text set
    aside (TARGETS, guard, region, guarded bytes; tuning §2.43¶4). Its 40 FAILs were exactly that
    scaffolding. run_libc_census.sh builds the dumper and passes `--levels`.
- **Still red in main-u3floor-sections, and not this lane's (R4):** test-memfn-arch. C4 reports
  13 FAILs on the kit's U2 rows S2975, S2994 and S2995.

## Check changes

| file | change |
|---|---|
| tests/memfn/simd_levels.c | prints `level` rows (now with family and needs) and `target` rows: name, family, features, and the region open/close and family guard as hex |
| tests/memfn/simd_floor_check.py | rewritten for the seam (see the legs below) |
| tests/memfn/routing_shape.py | a one-line selector may call a level helper `<fn>__<token>` defined above it (it used to call only `<fn>__body`); 4 new planted controls; the `#if` chain shape is still admitted, as D155 add. 1's text says (libc_census reads this file too) |
| tests/mech/sabotages/S724 | RE-AIMED: its plant used the retired `lv->guard` field, so it would no longer compile (ANOMALY). It is now a CPU-free `#if 1` around a level's `#include`, which the lint must refuse |
| tests/mech/run_sabotage_matrix.sh | the `simdfloor` vocabulary comment |
| docs/spec/tuning.md §2.43¶4 | the sentence on what simdfloor holds |
| tests/memfn/target_text.py (new) | the shared reader: `read_table`, `admitted`, `cut`, `target_of`, `aside` |
| tests/memfn/libc_census.py, run_libc_census.sh | R4: C11's movers half compares the ON artifact with its target text set aside; the runner builds the dumper |
| tests/memfn/NOTES.md, CLAUDE.md | "simdfloor" section; the target_text.py row (two headings shortened to stay under 12 KB) |

The legs, per cell:
- **Placement.**
  - `<P>_TARGETS` reads `FAMILY:T`.
  - The guard text occurs once and starts a line, ahead of every `#include`.
  - The region open and close occur once each, in that order.
  - Every function body and initializer lies between the open and the close.
- **Exclusivity (the lint).**
  - First the three declared texts are cut from the ON artifact.
  - After the cut, the lines ON inserts over OFF hold no preprocessor line except
    `#include <H>`, where H is the header of an ADMITTED level.
  - Admission is recomputed here from the table's facts: the level's needs must be a subset of
    T's features. It is not read from the kit's gate.
  - No helper of an unadmitted level may appear.
- **(c) Source level.**
  - The raw diff deletes only two kinds of line: the moved stamps (TARGETS, FORMS, GUARDED), and
    one `return <fn>__body(args);` per SIMD FUNC.
  - Each deleted call is replaced by the same call to `<fn>__w<VW>`, with VW an admitted width.
  - The inserted bytes equal `SIMD_GUARDED_BYTES` exactly. Measured on `(?i)cat` at x86-64:
    0x77f, which includes the guard, the region and the new call line.
- **(d)** routing_shape over the ON text.
- **Movers only.**
  - (b): the `gcc -E -P` diff deletes exactly the floor calls.
  - C9: the artifact compiles `-Werror` with no `-march`, at x86-64, -v2, sandybridge, -v3 and -v4,
    and at `-mgeneral-regs-only`.
  - nm at -O0 finds each selector's called helper at EVERY cell: the region, not the consumer's
    flags, supplies the ISA.
- **Retired: leg (a)** (off-target preprocessing equals OFF). It lost its subject with the `#if`
  arms. A no-vector consumer uses the default target (match_api §10.7¶4), and another family is
  refused by the guard (run_targets.sh 3c).
- **Floors are per target and per level** (`FLOORS`): x86-64 (55, 55, w16 55), x86-64-v3 (55, 55, w32 55), and LEVELS_FLOOR 2 / TARGETS_FLOOR 2.

The lint's spellings share a source with the emitter by design. The check holds where the text
goes and that nothing else is added, not the spelling itself. The compiler is the spelling's
control: the C9 cells here, and run_targets.sh's stripped-region refusal.

## Controls

| # | plant (scratch only, never committed) | where | result |
|---|---|---|---|
| 1 | stray `#pragma GCC optimize("O3")` before the region open | in-run, each target's first mover | rejected by `guard lint` (x86-64, x86-64-v3) |
| 2 | region close dropped | in-run | rejected by `placement` (both) |
| 3 | guard moved after the first `#include` | in-run | rejected by `placement` (both) |
| 4 | floor drop: the w32 form lost under x86-64-v3 (wrapper adds `--memfn=no-vrun-w32` at v3; scratch/u3floor/pcrec_now32.sh) | hand run, `--every 1000` | RED: `x86-64-v3: floor dropped (K35): ... w32 selectors 0 < 46`. (At this sample size the mover counts are also low; the w32 count of 0 is the plant's own signature, since x86-64's w16 count stays 5.) scratch/u3floor/ctl4.log |
| 5 | stray `#if 1` around a level `#include` inside the region | in-run | rejected by `guard lint` (both) |
| 6 | one line of a scalar `__body` deleted | in-run | rejected by `(c)` (both) |

- **No new sabotage rows.** Plants 1-3, 5 and 6 are artifact plants that the check runs itself on
  every run, which is stronger than a row. Plant 4 is a wrapper run.
- **The mech convention is a row per SOURCE plant.** The kit-side shape is covered by re-aiming
  S724. S1880-S1882 are already taken in this tree (altnf/island rows from main), so the brief's
  range was not used.
- S723 and S730 (simdfloor arm) are still aimed correctly: a RUN_WORDS stamp move fails leg (c)'s
  deleted-line rule, and a call line outside the bracket fails its byte count. They are queued in
  main-u3floor-mech; their verdicts are owed.

## STATE AT HANDOFF

- Last rulings entry applied: **R5**. The six jobs are re-queued as main-u3floor-*, each held to 01:00 or later and out of 20:00-01:00, and the tree is not edited after queueing.
- **Run here:** the full simdfloor section is GREEN (20414/0, above). routing_shape's selftest passes 14/14. Unit runs of text_legs and the 5 plants on `(?i)cat` at v3, and `target_text.aside` on a mover and a non-mover, all pass. libc_census.py and run_libc_census.sh pass py_compile and `bash -n` ONLY: their full run (test-memfn-stamps) is OWED in main-u3floor-sections. I stopped my own boxlock run of it so it would not take the box in Frank's 20:00 hold.
- **Queue:**
  - main-u3fix-sections was CANCELLED by this lane; the manager cancelled four more (R5), and
    movers was left running.
  - Queued `--owner main --prio 480` on the final tip, all with `not-before 2026-11-09T01:00` plus
    the 20:00-01:00 hour check in `--ready`: main-u3floor-sections, -movers, -sweepsimd, -mech,
    -axesmemfn, -maketest.
  - main-u3floor-mech carries u3fix's rows plus S723, S724 and S730.
  - Job files: /var/tmp/pcrec-pcrec/scratch/u3floor/jobs/; logs: .../u3floor/runs/.
- **OWED:** all six jobs; none has run. The predicted red is test-memfn-arch (the kit's C4 rows).
- Not touched: memfn/ and `MF_P_PORTABLE_ONLY`.
