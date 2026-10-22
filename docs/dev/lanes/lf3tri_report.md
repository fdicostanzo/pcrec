# lf3tri report (2026-10-22, sonnet) -- triage of 699-langfix3-test's two red sections

Both reds are class (a): pins that the branch's own new corpus files moved. No
wrong answer, no emitted-byte mover on a previously right pattern.

- `test-memfn-arch` (C4): `tests/lookaround/lookbehind_group_alt.{gen.py,rxt}` carry the SUBJECT
  string `adx` (lookbehind alternatives ab|cd, then x), which the isa-name class reads as the ADX
  extension: 2 hits in each file, 0 allowed. Fix: two `tests/memfn/c4_allowlist.tsv` rows (count 2
  each, reason: a subject string). The K35 floor (27) is a lower bound; total allowed now 50.
  `run_arch_blind.sh` alone: 17 passed, 0 failed.
- `test-startset` (the dfahat and stage-1 checks passed; the two red checks were `[vm-movers]`
  auto and forced in `vmhat_checks.py`): the manifests pin every VM-hat mover by file:line; the
  branch added eight corpus files (possessive_ungreedy, xbrace_space, lookbehind_group_alt,
  optrun_group, xmode_utf8, utf8_names, inlookaround_self, octal_wide) whose blocks are correct
  movers never pinned. `census_s1.py` on this tree (-fno-start-set arm; bench checkout read-only,
  bench rows not refreshed): `s2_vm_auto` +15, `s2_vm_forced` +81, `s3_dfa` +0, 0 existing rows
  gone or changed. Rows appended with a dated comment line per the manifests' convention.
  `run_vmhat_checks.sh` alone: 22 passed, 0 failed (9 min).
- Classes (b)/(c)/(d) ruled out: both failures are deterministic and name only new-file rows.

Owed: queued `707-lf3tri-test` (full make test, same shape as 699-langfix3-test).
699-langfix3-mech and 699-langfix3-k124diff left untouched.
