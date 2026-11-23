# specfind — why `make test-spec` fails 13 of 14 on main (2b4e56eab)

## Summary

Premise reproduced: `timeout 600 make test-spec` at 2b4e56eab prints
`SUMMARY: 1 passed, 13 failed`. Nothing in the 13 is a wrong ANSWER from pcrec.
Three stacked causes:

1. HARNESS, 8 of the 13 (check02, 03, 05, 11, 12, 13, 14 plus the cascade
   into check09): commit 489177423 ([ORACLE-LINK], 2026-09-09) turned
   `tests/fuzz/pcre2_abi.h` from a dlopen shim into a direct-link header, but
   `tests/spec_mod0/run_spec_mod0.sh` still compiles with `-ldl` only (no
   `-lpcre2-8`, no resolve_pcre2.sh), so every C check dies with
   `undefined reference to pcre2_compile_8`. Past the link step,
   `spec_common.h` `spec_start()` still calls `dlsym(spec_abi.handle, ...)`
   where `handle` is now a function address, not a dlopen handle: SIGSEGV
   (gdb bt: `dlsym` from `spec_start`).
2. HARNESS, check07 (and check09 behind it): check07 detects the `--features`
   surface by grepping the first 4096 bytes of `pcrec --help`
   (`char out[4096]`); the help is now 14.8 KB and `--features` first appears
   at byte 12384, so it reads "not present - awaiting", compares 0 pairs and
   fails its floor; check09 reads check07's output and fails on the cascade.
3. STALE EXPECTATIONS, check04, 06, 08, 10: the registry grew and the pinned
   expectations were not updated (details below). Four failures remain after
   (1) and (2) are repaired.

Evidence method: the repo was not edited. A scratch copy of tests/spec_mod0
with `dlsym(...)` replaced by `spec_abi.pattern_info` and a gcc wrapper adding
`-lpcre2-8` gave `8 passed, 6 failed` (check04, 06, 07, 08, 09, 10). Detailed log:
/var/tmp/pcrec-pcrec/scratch/specfind/spec3.log. Oracle: libpcre2 10.46.

## Each failing case

Spec text each case tests: docs/spec/registry.md §2 (the `--list-syntax`
columns, incl. `quantifiable`, `class_expect`) and §7 (what the tests pin);
the suite's own contract is tests/spec_mod0/CLAUDE.md.

| case | expected | actual (first differing line) |
|---|---|---|
| check01_isolation | n/a | PASS |
| check02_capture_count | compile + run | link error `undefined reference to pcre2_compile_8` (cause 1) |
| check03_lexical | same | same link error |
| check04_class_position | every class-reachable row pinned in class_expectations.inc | link error as shipped; after repair 13 DISAGREE: `row '\g<1>' has no pinned class-position expectation` (also `\g'1'`, `\g<0>`, `\g<01>`, `\g'0'`, `\g'01'`, `\a \e \f \n \r \t \x41`) |
| check05_digits | compile + run | link error |
| check06_cursor | rows reaching no doorway = `(?:...) a*+ a++ a?+ a{1,2}+` | actual adds `$ ${name} (a) ^`: `pcrec --probe-ask` refuses constructs not starting `\ (? (* [` (diagnostic names the rule) |
| check07_gate_equivalence | `--features` present, >= 44 compared pairs | link error as shipped; after repair `(--features not present - awaiting)`, 0 pairs, floor 44 (cause 2; help.out is 14805 bytes, `--features` at byte 12384, buffer 4096) |
| check08_endpoints | all cells described by model or endpoint_deviations.inc | after repair 2 DISAGREE: `[0-^]` and `[^-z]` - model predicts ERR(106) for endpoint `^`, libpcre2 10.46 COMPILES |
| check09_every_feature_toggles | PERNAME line for each of 21 module names | `no check07 output` as shipped; after repair 23 DISAGREE (21 "no PERNAME line", classes/modifiers 0 pairs) - pure cascade from check07 |
| check10_quantifiable | pcrec `quantifiable=yes` agrees with libpcre2 on `<syntax>*` | link error; after repair 18 DISAGREE: `\g<1> \g'1' \g<01> \g'01' (?P>n) (?&name) (?1)..(?10) (?01)`: libpcre2 says `a(?1)*` does not compile (err 115, no group 1 in the probe); `(a)(?1)*` compiles (measured) |
| check11, 12, 13, 14 | compile + run | link error as shipped; all PASS after repair |

## Since when

- All 14 pass at e913a492e (2026-08-22, M6.4.2); tests/spec_mod0 was last
  touched for substance 2026-09-21 (REL-1.10 call-site migration) and
  2026-10-21 (doc-only).
- `489177423^` (just before ORACLE-LINK): 8 passed / 6 failed (the six are
  causes 2 and 3). 489177423 itself: 1 passed / 13 failed. So the 8 harness
  failures were introduced by ORACLE-LINK on 2026-09-09; check07/09 and
  check04/06/08/10 were already red then.
- Bisect of e913a492e..489177423^ (git bisect run, ~11 builds) is NOT clean:
  the history is non-monotonic (good, bad, good flips: 8e4af411b, d80ec7483,
  528626535 all 14/14; a7f4e4ba0 12/14). First "bad" it reported:
  a7f4e4ba0 ([M6.5.2] WIP slices 1-3, A_BREF, 2026-08-22), whose two failures
  are check04 (`\g<1>`, `\g'1'` unpinned, new rows) and check07 (backrefs rows
  `\1 \2 \k<name> \g{-1}`: all-on=refused-as-invalid vs all-off=refused-as-
  unimplemented, a module going live mid-WIP). Treat it as "the first of a
  series of red-on-landing events", not a single regression: each module or
  registry-row landing since late August moved a pin nobody re-pinned, because
  test-spec is not in `make test`.
- Bisect trees left in place (clean, detached): worktrees/specfind-bis-a (at
  a7f4e4ba0), worktrees/specfind-bis-b (at 489177423). Remove with scripts/wtprune.

## Classification

- Broken harness: 9 (check02, 03, 05, 11, 12, 13, 14 link/dlsym; check07 help
  buffer; check09 cascade). check04 and check10 are also link-broken as
  shipped, but their post-repair failures are the next class.
- Stale expectation: 4 (check04 unpinned new rows; check06 base-answered set;
  check08 `^` endpoint; check10 recursion rows - a probe that is not
  self-contained, where pcrec's registry says `quantifiable=yes`; per
  registry.md §2 the right value for a row whose own probe does not compile
  may be a non-askable verdict, or the check should wrap the probe with a
  group - a design call, not an answer bug).
- Real pcrec regression: 0 observed. check08's `^` endpoint and check10 are the
  only cells where pcrec's registry and libpcre2 differ in substance; both
  are better read as check/model staleness, but check08's `^` row deserves
  a one-line look by someone who knows the model (pcrec has no wrong answer
  shown, only a model prediction).
- Classes overlap per case (check04, check10 count in both); 1 pass.

## Recommendation

Wire it back in only after repair, in this order:
1. Fix the harness (one small change): link via tests/lib/resolve_pcre2.sh
   (`$PCRE2_CFLAGS $PCRE2_LIBS`) like the registry runner, drop `-ldl`, replace
   the `dlsym` in `spec_start()` with `spec_abi.pattern_info`, and raise or
   stream the `--help` buffer in check07 (or probe `--list-flags` style). This
   alone recovers 8 of 14 green.
2. Re-pin the stale expectations (check04 pins via `--emit-pins`; check06 set;
   check08 `^`; check10 recursion probes) - each oracle-verified.
3. Then decide wire-in vs retire: the suite is the D27 spec-first tier that
   found a tier-1 miscompile once, and it is cheap, so wiring it into
   `make test` (so the next registry row moves its pins in the same change)
   is the better of the two; retiring would lose it. If the owner will not
   fund (1) and (2), retire it explicitly rather than leave a suite that
   reports red for months and trains people to ignore it.

## STATE AT HANDOFF

- Fact-finding only; no tests or code edited. Rulings file: none present (no
  R-n applied).
OWED: none
- Logs in /var/tmp/pcrec-pcrec/scratch/specfind/ (spec.log
  as shipped, spec3.log repaired scratch copy, bisect.log, a7.spec).
- Open: whether check08's `^`-endpoint model deviation is a pcrec classification
  quirk (not examined beyond the one libpcre2 probe, which compiles).
