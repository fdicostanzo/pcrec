# p1cpu — [XARCH-DEV] unit P1: the CPU target option and `--list-cpu-targets` (0 bytes)

Lane p1cpu, sonnet, 2026-11-08, branch lane/p1cpu (off main 831ed8280). Build go: Frank 2026-11-07.

## Summary

The one flag is built: `-fmemfn-simd` (SIMD on, host family's default list), `-fmemfn-simd=TOKEN[,TOKEN..]` (SIMD on, exactly those; a family token means that family's default list), `-fno-memfn-simd` (off, the kit's portable target); the last of them on the command line wins, and `-fno-memfn-simd` discards an earlier list, so a CPU is specifiable only with SIMD on by construction. pcrec names no token, target, family or CPU feature (C4 untouched by this lane); every token goes through `mf_target_parse` / `mf_family_parse` at option parse and the kit's refusal text is shown unchanged. One-member lists only; a longer list is refused with a plain message naming the rule (until unit U4). `--list-cpu-targets` prints the kit's families and targets. No artifact byte moves by construction (the host default list and the portable target reproduce today's SIMD-on / SIMD-off split exactly; the proof job is queued, see Checks). No abi change, no new flag bit.

## Option table

Spelling is the same in the three carriers: CLI `-fmemfn-simd[=LIST]` / `-fno-memfn-simd`; the `.rxt` directive is a config's / target's raw `pcrec -fmemfn-simd=LIST` line (the CLI's own parser, no parallel mechanism); the library carries the existing bits `PCREC_NO_MEMFN_SIMD` / `PCREC_FORCE_MEMFN_SIMD` plus ONE new pointer field `pcrec_options.memfn_simd` (the list text, NULL = none), appended at the struct's end.

The selection is the first-match table `simd_rows` in `src/gen/memfn_targets.c`, over (axis on?, list given?):

| # | SIMD axis | list | answer |
|---|---|---|---|
| 1 | off | given | refused (API only; the CLI cannot reach it) |
| 2 | off | any | the kit's portable target (the default) |
| 3 | on | given | exactly the list (family token -> kit's default list) |
| 4 | on | none | the host family's default list |

Then the one-family and one-member checks. The kit's policy bit `MF_P_PORTABLE_ONLY` is set iff the set is the portable target alone (`pcrec_memfn_policy`, now taking the options, moved from memfn_stamps.c). Row 1 is the API's loud refusal in place of a silent-deny row: a list beside the deny bit, or with neither bit, is a refusal.

## Kit calls

`mf_target_parse`, `mf_family_parse` (each token, refusal text kept; an unknown token shows the target text then the family text, both the kit's), `mf_portable_target`, `mf_host_defaults`; the listing uses `mf_families`, `mf_targets`, `mf_host_family` and each row's `name`, `family`, `defaults`, `features`, `doc` fields. Family and target of a member are compared as kit row pointers. Nothing in memfn/ was edited; no missing entry (stop rule not hit).

## Spec hunks

- cli.md: new §1.24 (the flag, refusal at parse, one-member rule, carriers, composition, rename at [IFACE-PUSH]) and §2.16 (`--list-cpu-targets` columns); §2¶1 count and list; TOC regenerated.
- tuning.md: §1¶10 (the pair is last-wins on the command line; deny wins only in the library), §2.43¶3 (the policy bit reads the set), new ¶3e (the target set table).
- match_api.md: new §8.2¶7d (`memfn_simd`).
- rxt_format.md §1.1¶2: the raw `pcrec` line carries the flag. table_contract.md §1: the new listing.

## Checks

- cli cases (tests/cli/run_cli_tests.sh, "cpu targets" block, probe tests/cli/simd_target_probe.c): all pass locally (`cases failed: 0`). They name no token: tokens come from `--list-cpu-targets`, the listing is compared with the kit's own `memfn/src/targets.def`, and refusal text is compared with what the kit itself returns (probe). Rows: off, host, list, family token, case-blind, repeated target, portable-alone = default, last-wins x4, early fail at parse (also beside a query mode, so only option parse can refuse), library door (unknown token, list beside deny, list with no bit, force with host target, force with no list), two targets one family, two families, a config's raw line (good and bad).
- Local spot check: 15 compiles (3 flag settings x 5 patterns) byte-identical to main's binary. The full proof (`emit_sweep --ref 831ed8280`, default and `--extra=-fmemfn-simd`) is OWED, queued.
- `make strict` green; `scripts/check_claudemd_size.sh --all` green; the spec pre-commit checks green.
- C4 (`tests/memfn/run_arch_blind.sh`): my files add nothing; it reports ONE pre-existing failure, tests/mech/sabotages/S2977_targets_region_no_gcc_target.sh (kit lane's file, a class-1 hit in its SAB_EXPECT comment), not from this lane.
- Sabotage S1864-S1869 (one per table row / early-fail site; each plant text matches exactly once; fields validate): S1864 policy bit not read off the set; S1865 the host row answers portable; S1866 the list-off row dropped; S1867 the CLI's parse-time check dropped; S1868 the compile's check dropped; S1869 the one-member rule dropped. Detector arm: cli. Not yet RUN: OWED (mech job).
- Flag bits: none consumed (the force/deny pair 48/49 reused). By a grep of `PCREC_BIT(n)` in lib/pcrec.h, bits 0-54, 56 and 57 are used; 55 and 58-63 look free (7), above the 4-bit trigger; not otherwise audited.

## STATE AT HANDOFF

Code, tests, spec, CLAUDE.md files, history entry committed on lane/p1cpu. Rulings file read at each commit: empty (no entry to apply). OWED queue jobs (all `470-main-`, owner main): `main-p1cpu-sweep` (emit_sweep 0-moved proof at default and `--extra=-fmemfn-simd`; log `/var/tmp/pcrec-pcrec/scratch/p1cpu/sweep-{default,simd}.log`; verdict line `p1cpu-sweep: VERDICT GREEN`), `main-p1cpu-maketest` (make, make strict, make test; log `/var/tmp/pcrec-pcrec/scratch/p1cpu/maketest.log`), `main-p1cpu-mech` (S1864-S1869; ends `== mech run COMPLETE: 6 rows`, all 6 must read DETECTED). The queue holds 19:00-01:00. Not done: the D146 addendum was already filed with K0; no decision addendum is owed by P1. Next unit on this seam: U2+U3 (kit and pcrec, one landing).
