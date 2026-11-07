# k0fix — distinct family and target tokens (kit request R-36, unit K0 fix)

Lane k0fix (sonnet), worktree `worktrees/k0`, branch `lane/memfn-k0`. Frank's 2026-11-07 ruling (one flag
`-fmemfn-simd[=TOKEN,..]`, target_seam_units.md §6) needs a list that mixes family and target tokens, so no token may be both.

## Summary

- Family tokens are the `uname -m` names: `x86_64`, `aarch64`. Target tokens are gcc's -march names: `generic`, `x86-64`,
  `x86-64-v3`, and aarch64's target renamed `armv8-a`. Default lists: `x86_64` -> `x86-64`, `aarch64` -> `armv8-a`.
- THE PARSER FOLD HAD TO CHANGE. The matching rule read `_` as `-`, which makes the new family `x86_64` and the target
  `x86-64` one token. `_` is no longer folded: ASCII-case-blind and otherwise exact. `x86_64_v3` is now refused as a target.
- The table check holds ONE token space (below); one new sabotage row, S2981.

## Token spellings

Changed (every old token used as a family or target name, found by grep over the whole worktree):

| file | change |
|---|---|
| `memfn/src/targets.def` | family `x86-64` -> `x86_64`; family `aarch64` default `aarch64` -> `armv8-a`; target `aarch64` -> `armv8-a` (id `MF_TGT_AARCH64` -> `MF_TGT_ARMV8_A`); header gains the two-token-spaces paragraph |
| `memfn/src/targets.c` | `tok_names`: the `_` -> `-` fold removed |
| `memfn/include/memfn.h` | the matching-rule paragraph: two token spaces, family token in a list = the family's default list, `_` is not `-` |
| `memfn/tests/check_targets.sh` | one token space; the fold is case only; token regex admits `_` after the first char; floor comment |
| `tests/memfn/targets_check.c` | rows, defaults, host default (`armv8-a`), refusals across the spaces, a no-token-in-both loop |
| `tests/mech/sabotages/S2976_*.sh` | SAB_BEFORE/AFTER carry the family `x86_64` |
| `tests/mech/sabotages/S2981_*.sh`, `tests/memfn/c4_allowlist.tsv` | the new row and its two C4 anchor lines (class 6, count 2, as S2976's) |
| `tests/mech/run_sabotage_matrix.sh`, `tests/memfn/NOTES.md` | S2975-S2981 |
| `docs/dev/lanes/k0_report.md` | the tables and sentences naming the old tokens (the uncommitted heading renames in the tree are committed with it) |
| `docs/design/memfn/target_seam_units.md` | §6: the token-spelling ruling bullet |

Not changed on purpose: `levels.def` (`MF_LEVEL(..., "x86-64", ...)`: the LEVELS' family column, a different table the
kit's U2 replaces), `-march=`/`--target=` strings in `run_targets.sh` and the check (compiler names), `__x86_64__`
guards, `uname -m` comparisons, design notes that predate the ruling.

## Distinctness check

`check_targets.sh` keeps one `seen_tok` map over family and target names under the parser's fold (case only): a name equal
to any earlier row's, in either space, is a MISMATCH ("token 'X' is also family F's (one token space ...)"). The old rule
(distinct within each space) could not see a family and a target share a token. `targets_check.c` adds the same fact at
the entries (no listed family and target are `strcasecmp`-equal) and four cross-space refusals (`x86_64` and `aarch64`
as targets; `x86-64` and `armv8-a` as families).

SABOTAGE S2981 (next free id; grep of the tree and all worktrees found no S2981+): plants the family `x86_64` respelled
`x86-64`, equal to the target. Only the distinctness rule sees it (the default list names targets). Hand-planted
through `TARGETS_DEF` on a scratch copy: `MISMATCH target MF_TGT_X86_64: token 'x86-64' is also family MF_FAM_X86_64's`,
red. The real mech run is job 453 (rows=7), OWED. Jobs 450-453 re-dry-run: clean, see Light checks.

## Spec and contract hunks

- `memfn.h` (the contract pcrec reads): FAMILY tokens are the `uname -m` names, TARGET tokens gcc's -march names, the two
  spaces disjoint; a family token in a list means that family's default list (the caller's reading; the kit only parses each
  token as one or the other); matching is ASCII-case-blind and exact otherwise.
- `target_seam_units.md` §6 records the ruling. The flag text (`-fmemfn-simd`, `-fno-memfn-simd`, last wins) is P1's.
- `docs/spec/` states none of this today (no caller yet), so no spec hunk.

## Light checks

niced, `scripts/boxlock status` showed only a queue job (213-altcatch-axes), no timing window:
`make` rc 0 (table check `ok: 2 families, 4 targets, 2 compared against gcc -march, 1 skipped, host MF_FAM_X86_64, 4 host cells`);
`make strict` rc 0; `make test-memfn-targets test-codegen test-memfn-arch test-memfn-link test-claudemd-size
test-spec-history test-ci-shards` rc 0 (no `*** [test-` line). The first run's one red, C4 on the new row's anchor lines
(class 6, 2 hits), is the allowlist rows above. No make test, no mech, no box job queued. Jobs 450-453 re-dry-run clean (453: `expect rows=7`, field validation of 7 definitions; 450-452 unchanged).
Logs: `/var/tmp/pcrec-pcrec/scratch/memfn/k0fix/`.

OWED (unchanged keys): kit-k0-strict kit-k0-sections kit-k0-test kit-k0-mech (453 now runs 7 rows).

## Charter-vs-committed checklist

| charter item | committed |
|---|---|
| respell tokens everywhere, list changes | yes, Token spellings |
| distinctness rule in the table check | yes, one token space |
| one sabotage row, red, in 453, rows count raised, jobs 450-453 re-dry-run | S2981; 453 IDS +1 (N derived); dry-runs clean (Light checks) |
| spec hunk: two token spaces, family token in a list | memfn.h + units §6 |
| light checks | all green |
| report, history index line, lanecheck | yes |
