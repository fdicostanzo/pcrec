# dd10b — [DD-10] follow-up: the parser's per-level stack (lane report)

Lane dd10b (opus), 2026-10-22, branch `lane/dd10b` off `lane/dd10` @
1a7823bee. Build go: manager under Frank's "keep busy" (2026-10-21), parked on
the branch. Standing ruling: dd10 R1 (keep the 250 cap, state the measured
budget, no lower cap, no parser rewrite). Rulings file `dd10b_rulings.md`:
empty at handoff.

## 1. Summary

dd10 left the recursive-descent parser as the depth limit: a lookaround nest
cost 2,480 B per level. The cause was the one dd10 named. `ExtResult` carried
`char msg[256]` by value, and an ExtResult (or the hidden return slot for one)
sits in every frame on the group recursion: `p_group_body` (inlined into
`p_rep`), `pcrec_ext_group`/`group_answer`, and the module port
(`pcrec_laport_group`, `pcrec_agport_atomic`, `pcrec_modport_optrun`,
`pcrec_ngport_declare`). `pcrec_laport_group` also held a second 256-byte
`buf` for the width refusal.

The fix is a frame diet, not a parser rewrite, so the STOP rule did not fire.
`ExtResult.msg` is now a `const char *`. A formatted refusal is written into
the compile's arena by one new helper, `pcrec_ext_msgf(cx, fmt, ...)`, which
still cuts at `sizeof pcrec_error.msg` (256) so truncation is unchanged. A
constant text is assigned as is. `REFUSE` calls the helper, and so do the
hand-built refusals. The lookbehind width text moved to an arena buffer of
`LA_MSG_MAX` bytes.

The effect was larger than dd10's estimate (~1.3 KB/level, ~330 KB at 250).
Plain groups dropped too, because `p_atom`/`p_group_body`/`esc_atom` inline
into `p_rep` and each carried an ExtResult.

## 2. Measurements (x86-64, gcc 15.2 -O2, `features=all`, the 7700X)

Probe: `tests/thread/compile_stack_driver.c` (painted, guard-paged thread).
"before" is lane/dd10 @ 1a7823bee, "after" is this branch.

| family | d=250 before | d=250 after | per level before → after | max depth on 128 KB before → after |
|---|---|---|---|---|
| `a` alone (floor) | 61,616 | 61,616 | — | — |
| `((((a))))` plain / `(?:` / `(?:…)*` | 250,504 | 118,760 | 944 → 416 | 123 → 250 (cap) |
| `(a\|(a\|…b))` | 250,504 | 187,336 | — | 123 → 166 |
| `(a(a…)?)?` | 362,736 | 362,736 | 1,376 (analysis) | 81 → 81 |
| `(?:a(?:a…)?)?` VM | 287,008 | 287,008 | (analysis) | 104 → 104 |
| `(?=(?=…a))` / `(?<=` | 634,504 | 198,760 | 2,480 → 736 | 47 → 158 |
| `(?>(?>…a))` | 562,504 | 194,760 | → 720 | 53 → 161 |
| `(?i:(?i:…a))` | 606,648 | 210,904 | → 784 | 49 → 148 |
| `(?<n0>(?<n1>…a))` | 566,504 | 202,760 | → 752 | 52 → 154 |
| refusal at 251, worst | 636,520 | 212,360 | | |

Per-level figures are (d250 − d125)/125. The 128 KB depths come from
bisection on a 131,072-byte thread. The "before" column reproduces dd10's
§3.10 numbers exactly (47 and 123), and that serves as the control. The
width/chain arm did not move (24,068–62,912 B).

The worst family is now `(a(a…)?)?` at 362,736 B. An analysis sets that
slope (dd10 finding 4: possessify `first_of` 448 B + `text_first` 336 B,
`First` by value), not the parser, and this lane did not touch it.

Budget, by dd10's formula (measured worst + ~20%): 362,736 × 1.2 = 435,283,
rounded up to the next 16 KB, gives **432 KB (442,368 B)**, which is 1.22× the
worst. `limits.md` §3.10 ¶2-¶4 and `COMPILE_STACK` were lowered together.

Static frames after (parse/, `-fstack-usage`): `p_rep` 336 (with `p_atom`
and `p_group_body` inlined), `pcrec_ext_group` 176 (was 368, plus 448 for
`group_answer`, now inlined), `pcrec_laport_group` 144 (was 736),
`pcrec_modport_optrun` 192 (was 624), `pcrec_agport_atomic` 128 (448),
`pcrec_ngport_declare` 160 (464). `pcrec_ext_escape` grew to 464 because its
setdef error buffer is now a local. It is a leaf, called once per escape and
never on the recursion, so it costs no stack per level.

## 3. What changed

- `src/core/internal.h`: `ExtResult.msg` is `const char *` (comment carries
  the numbers). `pcrec_ext_msgf` is declared. `REFUSE` formats through it, so
  it now needs `cx` in scope, as it already needed `want`.
- `src/parse/ext.c`: `pcrec_ext_msgf` (arena, 256-byte cut). The three
  hand-built refusals and the `\d`-under-UCP setdef refusal use it (the latter
  through a local error buffer, off the recursion).
- `src/parse/mod_lookaround.c`: the width-refusal `buf` moved to the arena.
  The `pcrec_lookaround_fix_widths` copy is untouched: it is not on the
  recursion, and S170 anchors on it.
- `src/parse/mod_modifiers.c`: `modport_refuse` takes `cx`; the `(?r)` site
  is a plain `REFUSE` (its `buf[112]` is gone). `mod_ucp.c`: `ucp_refuse`
  takes `cx`. `mod_classes.c`: the setdef refusal goes through a local buffer
  and `pcrec_ext_msgf`. `parse.c`: the octal refusal is a constant.
- `src/dump/syntax_dump.c`: comment only (`--probe-ask` copies `r.msg` before
  it frees the arena).
- `tests/thread/run_compile_stack.sh`: `COMPILE_STACK` 786,432 → 442,368. Two
  new depth families, `inlineopt` `(?i:` and `named` `(?<n%d>` (`nest`'s
  `<open>` is now a printf format given the level index). 30 checks, up from
  26.
- Mech: **S1440** (arm `compilestack`, `src/core/internal.h`): ExtResult
  grows a 256-byte inline buffer again. MEASURED by hand on a scratch build:
  10 FAIL (look, lookbehind, atomic, inlineopt and named, each at 250 and
  251, die on the 432 KB thread); plain groups 118,760 → 258,504 B.
- Docs: `docs/spec/limits.md` §3.10 ¶2-¶4, `docs/testing.md` (432 KB),
  S1336's comment, the plan.md [DD-10] status line.

## 4. abi / diagnostics / movers

There is no abi event and no emitted-byte change, because only the parser's
error plumbing changed. Spot check, old library vs new CLI, 24 patterns that
reach every edited site (lookbehind width, `\K` in a lookaround, missing `)`
in the lookaround and modifier ports, `(?r)` under utf8, octal > \377,
`(*UTF)` under byte, class-range endpoints, unknown POSIX name, `\p` gated,
`(?Z)`, `(*FOO)`, unknown escape, and accepted lookaround/atomic/named/inline
patterns): emitted `.c` and the diagnostic text plus exit code were
byte-identical in all 24. `--probe-ask verdict` output was identical for 4
constructs. The full checks (reject corpus, registry check06/`--explain`,
codegen identity gates) are in the queued `make test`.

## 5. Findings (not built here)

1. **The next lever is analysis, not parser**: possessify `first_of` (448 B)
   and `text_first` (336 B) set the worst family's 1,376 B/level. The general
   form is dd10's `rb_walk` one: results in depth-indexed arena slots instead
   of `First` (33 B) temporaries by value. Taking it to the ~0.75 KB/level of
   the doorway families would put the worst near 210 KB and the budget near
   256 KB. The trigger to build it is a caller who needs a smaller thread at
   full depth.
2. `p_rep`'s 336 B with the atom path inlined could lose about 100 B/level if
   `esc_atom` were `PCREC_OWN_FRAME` (out of line). That is about 25 KB at
   250. It does not move the budget while the analysis sets the worst, so it
   was not done.
3. The floor (62 KB, the memfn frames, dd10 finding 1) is now a third of the
   plain-group total at depth 250.

## 6. Validation done in the lane

- `nice make -j2` clean (no warnings at the default flags). `make strict`
  is OWED (queued).
- `tests/thread/run_compile_stack.sh` on this branch: 30 passed, 0 failed.
  Failing direction, the same script against the dd10 library
  (`LIBPCREC=`): 10 FAIL (the five doorway families at 250 and 251), which
  shows the lowered budget would have caught the old frames.
- `tests/registry/limits_check.sh`: 38 passed, 0 failed (§3.10 anchor).
  `scripts/plan_lint.sh`: 0 violations.
- Mech VALIDATE_ONLY: all 29 rows anchored in the edited files (`ext.c`,
  `mod_classes.c`, `mod_lookaround.c`, `mod_modifiers.c`, `mod_ucp.c`,
  `parse.c`, `internal.h`) are valid, and so is S1440.

## 7. STATE AT HANDOFF

- Branch `lane/dd10b`, all committed. Rulings file: no entries (none
  applied). It must merge AFTER lane/dd10 (it is built on it).
- OWED (queued, held, under the box lock, owner dd10b): `685-dd10b-build`
  (`make -j16`), `685-dd10b-strict`, `685-dd10b-test` (`scripts/perfrun
  --label dd10b`), `685-dd10b-mech` (S1336 S1337 S1338 S1339 S1340 S1440,
  arm compilestack, all expected DETECTED; dd10's five re-run against the
  432 KB budget). The first job's `--ready` exits 75 while
  `i2build-parity` is pending or running (tested: rc 75, "held until
  i2build-parity ends"). Verdicts: `scripts/boxqueue state dd10b-<stage>`,
  logs under `worktrees/.boxqueue/done/`, read with `scripts/verdict LOG`.
- Not run: asan/ubsan (tests/thread is plain-build only, as for dd10), and
  the Mac (the ~20% margin covers arm64; a red there means re-measuring, not
  a defect).
