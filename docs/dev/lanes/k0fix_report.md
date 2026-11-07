# k0fix — distinct family and target tokens (kit request R-36, unit K0 fix)

Lane k0fix (sonnet), worktree `worktrees/k0`, branch `lane/memfn-k0`. Frank's 2026-11-07 ruling (one flag
`-fmemfn-simd[=TOKEN,..]`, target_seam_units.md §6) needs a list that mixes family and target tokens, so no token may be both.

## Summary

SPELLING BUILT (the manager's second brief overrides the first): FAMILY tokens `amd64` and `arm64` (Go GOARCH /
Debian names), NOT `x86_64`/`aarch64`; TARGET tokens `generic`, `x86-64`, `x86-64-v3`, `armv8-a` (aarch64's target
renamed). Default lists: `amd64` -> `x86-64`, `arm64` -> `armv8-a`. An interim build with `x86_64`/`aarch64` families
(commit 9c96d2231) is superseded.

- The parser matches ASCII-case-blind and otherwise exactly: the old `_` -> `-` fold is gone (`x86_64` is refused as a
  target and as a family).
- The table check holds one token space, and refuses a family token that EQUALS a target token once `_` reads as `-`
  and case is dropped (`x86_64` vs `x86-64`: one typo from a different valid meaning). Sabotage S2981 plants `x86_64`
  as the family.
- Addendum 2: `mf_host_family()`, and a `doc` line on every facts row.

## Token spellings

Changed (grep over the whole worktree for every old token used as a family or target name):

| file | change |
|---|---|
| `memfn/src/targets.def` | families `x86-64` -> `amd64`, `aarch64` -> `arm64` (defaults `x86-64`, `armv8-a`); target `aarch64` -> `armv8-a` (id `MF_TGT_AARCH64` -> `MF_TGT_ARMV8_A`); header: the token-spaces paragraph, the `doc` column; a `doc` argument on every row |
| `memfn/src/targets.c` | `tok_names`: the `_` -> `-` fold removed; macros take `doc`; `mf_host_family` |
| `memfn/include/memfn.h` | the matching-rule paragraph; `doc` fields; `mf_host_family` |
| `memfn/include/CLAUDE.md` | the K0 paragraph |
| `memfn/tests/check_targets.sh` | one token space, the cross-space `_`-folded rule, the `doc` column |
| `tests/memfn/targets_check.c` | rows, defaults, host default (`armv8-a`), cross-space refusals, doc lines, `mf_host_family` |
| `tests/mech/sabotages/S2976`, `S2980` | anchors follow the rows' new shape (family `amd64`; `"neon",`) |
| `tests/mech/sabotages/S2981_*.sh`, `tests/memfn/c4_allowlist.tsv` | the new row and its C4 anchor lines (class 6, 4 hits) |
| `tests/mech/run_sabotage_matrix.sh`, `tests/memfn/NOTES.md` | S2975-S2981 |
| `docs/dev/lanes/k0_report.md` | the tokens |

Not changed on purpose: `levels.def` (the LEVELS' family column, a different table U2 replaces), `-march=`/`--target=`
strings in `run_targets.sh` and the check (compiler names), `__x86_64__` guards, `uname -m` comparisons (the test's host
default maps `x86_64` -> `x86-64` and `aarch64`/`arm64` -> `armv8-a`), design notes that predate the ruling.

## Distinctness check

`check_targets.sh`: (1) `seen_tok`, one map over family and target names under a case-only fold (any repeat, in either
space, is a MISMATCH); (2) NEW, every (family, target) pair compared after lowercasing and `_` -> `-`. `x86_64` as a
family also fails the token-list regex (it holds a `_`), so two rules fire on the plant; (2) is the one that states
the reason. `targets_check.c` holds the same at the entries (`strcasecmp`), plus cross-space refusals.

SABOTAGE S2981 (next free id; no S2981+ anywhere): the first family row is respelled `x86_64`. Hand-planted through
`TARGETS_DEF` on a scratch copy: `MISMATCH family MF_FAM_X86_64: token 'x86_64' equals target MF_TGT_X86_64's 'x86-64'
once _ reads as -`, red (and the entries' literal is red: `amd64` no longer parses). The real mech run is job 453
(rows=7), OWED. Jobs 450-453 re-dry-run clean (453: `expect rows=7`).

## Addendum 2: host family and doc column

- `const mf_family *mf_host_family(void)`: the family the kit was compiled for, NULL when the table has no row for the
  host. `mf_host_defaults` stays. Tested: its defaults equal `mf_host_defaults()` (no family: the portable token).
- `doc` on every FACTS row (`mf_family.doc`, `mf_target.doc`; macros' last argument): one plain-English line in the kit's
  words. The token-list rule exempts exactly `doc`; a doc line is refused when empty, over 100 bytes, or holding any of
  `# _ { } ; \ " |` (so no preprocessor or C token). Hand-planted: `#if defined(__ARM_NEON)` as a doc is red; S2980's
  plant (`__ARM_NEON` as a feature) still red (it sits in a token column). Docs avoid `;`.

## Spec and contract hunks

- `memfn.h`: FAMILY tokens are the Go/Debian names, TARGET tokens gcc's -march names, the spaces disjoint; a family
  token in a list means that family's default list (the caller's reading; the kit only parses); matching ASCII-case-blind
  and exact. The enumeration entries `mf_targets`, `mf_families`, `mf_host_family` are the listing's SOURCE: every field
  pcrec prints (name, doc, defaults, needs, features) is the kit's text.
- `target_seam_units.md` is main's and is NOT edited (an interim hunk was reverted); see "For main". The flag text (`-fmemfn-simd`, `-fno-memfn-simd`, last wins) and
  `--list-cpu-targets` are P1's.
- `docs/spec/` states none of this today (no caller yet), so no spec hunk.

## For main

Relay for `target_seam_units.md` §6 and P1 (the kit's token statement; the flag text is P1's): FAMILY tokens are `amd64`
and `arm64` (Go/Debian names; not `x86_64`, one character from the target `x86-64`). TARGET tokens are `generic`,
`x86-64`, `x86-64-v3`, `armv8-a`. The spaces are disjoint and the kit refuses a family token equal to a target token
after lowercasing and `_` -> `-`. Matching is ASCII-case-blind and otherwise exact. A family token in a list means that
family's default list (`amd64` -> `x86-64`, `arm64` -> `armv8-a`), the caller's reading. Text in units.md and the K0
report that spells the family `x86-64` or the target `aarch64` predates this. The listing's source is `mf_targets`,
`mf_families`, `mf_host_family`; each row's `doc` is the kit's text. The same statement is in memfn.h's comment.

## Light checks

niced, `scripts/boxlock status` showed only a queue job (213-altcatch-axes), no timing window:
`make` rc 0 (rerun after the second brief; table check `ok: 2 families, 4 targets, 2 compared against gcc -march, 1 skipped, host MF_FAM_X86_64, 4 host cells`);
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

## STATE AT HANDOFF

Committed on `lane/memfn-k0`; nothing uncommitted from this lane. OWED (queue keys unchanged, none queued by this lane):
`kit-k0-strict` (450), `kit-k0-sections` (451), `kit-k0-test` (452), `kit-k0-mech` (453, now 7 rows incl. S2981). A fresh
agent reads their verdicts. No rulings file applies.
