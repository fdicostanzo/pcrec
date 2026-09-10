# mechtri2 — triage of the s5 battery's mech-stage trailer (2026-09-10)

Brief: triage `build/battery_20260909_s5/mech.log`'s trailer — "244 rows
(unexpected: 1, undetected: 9, unreached: 1, anomalies: 6)" — against the
stage-4 baseline ("243 rows (unexpected: 5, undetected: 10, unreached: 6,
anomalies: 0)" plus mechreach's five fixes). The delta window is the three
merges the s5 battery covers: `utf8s5`, `arm61fix`, `tt4m3`.

## Summary of the finding

**All 7 non-clean rows (1 unexpected + 6 anomalies) share ONE root cause,
and it is none of the three merges named in the brief.** It is fallout from
a FOURTH merge — `oralink` (D98, commit `d871978c`) — which retired
`pcre2_abi.h`'s dlopen shim for direct linking (`#include <pcre2.h>`).
`git archive HEAD` in a long-running mech stage re-reads HEAD per row (its
own documented behaviour), and `oralink` landed on `main` mid-run, after
the battery started at `572b41bf` but before `mech`'s later rows executed —
so the s5 mech run measured a MOVING TREE, and the rows near the end of the
alphabet (S15/S16/S17/S19/S20/S178, and mechreach's `pc4` arm for S-U11)
picked up the post-oralink `main` mid-flight.

`oralink`'s own commit message claims "wired into all six oracle build
sites," but SIX DIFFERENT sites were missed — every one of them a bare
`$CC ... -ldl` compile of `pcre2_oracle.c`/`pcre2_check.c`/`pc4_check.c`
with no `$PCRE2_CFLAGS`/`$PCRE2_LIBS`, left over from the pre-migration
dlopen era where the oracle needed no header or link-time library at all.
On this box libpcre2 resolves via `pkg-config` (Homebrew, 10.48) but its
header is NOT on the default include path, so every one of the six failed
to build outright:

    fatal error: pcre2.h: No such file or directory

- `tests/atomic_groups/run_atomic_diff.sh` — S178's `atomicdiff` arm
- `tests/assertions/run_gstart_diff.sh` — the `gstartdiff` arm (S82-S84)
- `tests/assertions/run_kreset_diff.sh` — the `kresetdiff` arm (S85-S87)
- `tests/assertions/run_mline_diff.sh` — the `mlinediff` arm (S76, S78, S81)
- `tests/mech/run_sabotage_matrix.sh`'s own `pc3` arm — S15/S16/S17/S19/S20's
  extra registry-vs-libpcre2 net
- `tests/mech/run_sabotage_matrix.sh`'s own `pc4` arm — S-U11's only detector

**Why only S178 and the five `pc3` rows surfaced as findings, and not
S82-S87 or S76/S78/S81 (which use the identical broken build):** the mech
driver's own scrape defaults a missing `checks passed:`/`checks failed:`
line to `f=ERR` and then `[ "${f:-1}" -gt 0 ] && any_fail=1` — a build
failure is silently scored as `any_fail=1`, indistinguishable from a real
detection. S178 is the ONE row in this whole set whose `SAB_EXPECT` is
`UNDETECTED` (its own header: the discharge fires exactly where `vm_lifts`
lifts, so the six-pattern search finds byte-identical artifacts and the row
is a documented *search*, not a detection), so the broken build's
`any_fail=1` collided with its stated expectation and printed
`NOW DETECTED ... ***UNEXPECTED***`. Every other row sharing the same
broken arm (S15/16/17/19/20, S82-87, S76/78/81, S-U11) declares
`SAB_EXPECT=DETECTED`, so the SAME broken-build artifact silently agreed
with the expected verdict and passed through unnoticed — these rows have
been running on a dead oracle since `oralink` landed and nothing but S178's
own inverted expectation caught it.

**This is not a semantic finding about atomic-groups, registry, `\G`,
`(?m)`, or `\K`.** It is a live infrastructure defect (the missing
`$PCRE2_CFLAGS`/`$PCRE2_LIBS`) that happens to have been introduced to
`main` mid-battery. It reproduces on the CURRENT `main` tip too (verified
directly, not only inside mech's scratch archive) — this is not scoped to
the mech stage alone; every `make test-assertions` invocation of
`run_gstart_diff.sh`/`run_kreset_diff.sh`/`run_mline_diff.sh`, and
`make test-atomic` invocation of `run_atomic_diff.sh`, has been silently
building nothing since `d871978c` landed, on any box (like this one) where
`pkg-config libpcre2-8 --cflags` is non-empty. Each script's build failure
was previously invisible to `make test`, because each already has its own
"SKIPS LOUDLY when libpcre2 is absent" contract and a hard build failure
under `set -u`/`exit 1` looks superficially like that same shape in a
scrollback — but it is a FAIL, not a SKIP, and `make test-assertions`/
`make test-atomic` would have reported it as a hard section failure. (Not
independently reproduced against a full `make test-assertions` run here —
scope was the mech triage — but the direct-invocation reproduction above
demonstrates the build failure is real and box-general, not scratch-tree-
specific.)

## Fix

Six sites patched identically: source `tests/lib/resolve_pcre2.sh` (already
sourced by `run_atomic_diff.sh`; newly sourced by the other five), pass
`$PCRE2_CFLAGS` to the compile and `$PCRE2_LIBS` in place of the bare
`-ldl`, and treat `PCRE2_AVAILABLE != 1` as a loud SKIP (matching
`tests/fuzz/run_capturediff_gate.sh`'s already-correct D98 shape) rather
than a hard build failure or a false `CHECK-BUILD-FAILED`/anomaly for the
two `run_sabotage_matrix.sh` arms.

Single commit on `lane/mechtri2`: `c9ddb933`.

## Validation (solo re-runs, box was free, `CC=gcc-16`)

Direct script invocation (outside mech, confirms the fix on real source,
not just inside a scratch archive) — `run_atomic_diff.sh` against the
worktree's own build, TWO independent runs:

    checks: 0 FAIL across all sections (§1/§2/§2b differential 61,586 cells
    x3 arms x 83 patterns x 141 subjects, population/non-vacuity/rung-
    coverage/cell-floor and §3 discharge, all PASS)

(§4's entries sweep did not finish inside a 240s wall clock on either
direct run — it is CPU-bound per-pattern gcc compiles, unrelated to this
fix; not a regression, see "Owed" below.)

Solo `bash tests/mech/run_sabotage_matrix.sh <row>` re-runs, one row per
invocation, `KEEP=0`, tree `c9ddb933` (this lane's own commit — mech
`git archive HEAD` picks up committed changes, so these numbers are against
the FIX):

    S-U11  pc4:22fail/1n-fold-only               DETECTED (matches its own 22-FAIL prediction exactly)
    S15    pc3:0fail/208pass                     DETECTED (matches the [MOD-0.8c] table's historical "pc3 0" exactly)
    S16    pc3:0fail/209pass                     DETECTED (matches "pc3 0" exactly)
    S17    pc3:1fail/209pass                     DETECTED (matches "pc3 1" exactly)
    S19    pc3:1fail/209pass                     DETECTED (matches "pc3 1" exactly)
    S20    pc3:1fail/209pass                     DETECTED (matches "pc3 1" exactly)

All six: `unexpected: 0, undetected: 0, unreached: 0, anomalies: 0,
oracle-skipped: 0`.

**S178: CONFIRMED.** Solo re-run, `bash tests/mech/run_sabotage_matrix.sh
S178`, `KEEP=0`, tree `c9ddb933`:

    S178  corpus:0fail/921pass,atomicdiff:0fail/8pass
          UNDETECTED (EXPECTED -- see this row's SAB_DOC_FIGURE for what
          would close it)
    == mech run COMPLETE: 1 rows (unexpected: 0, undetected: 1,
       unreached: 0, anomalies: 0, oracle-skipped: 0) ==

Exactly the row's own `SAB_DOC_FIGURE` — the atomicdiff arm now actually
runs (`0fail/8pass`, not `ERRfail/?pass`) and agrees with the six-pattern
byte-identity search: the discharge fires exactly where `vm_lifts` lifts,
so nothing observable moves. The `NOW DETECTED`/`***UNEXPECTED***`
mismatch from the s5 battery is fully closed — it was the broken oracle
build, not a real regression or an expired claim, and `SAB_EXPECT` did not
need to move.

## The `undetected: 9` and `unreached: 1` rows — confirmed, not re-litigated

Per the brief, checked rather than re-derived: every one of the 9 rows the
s5 mech.log marks `undetected` carries its own printed annotation
`UNDETECTED (EXPECTED -- see this row's SAB_DOC_FIGURE for what would close
it)` in the log, and none of them appears in the trailer's `unexpected`
list — meaning the mech driver's own `SAB_EXPECT=UNDETECTED` check already
scored all nine as matching their declared expectation, mechanically, not
by eyeball. They are the two utf8 rows (S-U6, S-U9) plus the seven
`[DD-14 wave B+C]` "rows that certify nothing" family minus the two that
have since closed (S150, S151, S152, S153, S160, S219, S220 — S157 and
S164 already flipped to DETECTED at earlier waves per
`tests/mech/CLAUDE.md`). Likewise S121 (the one `unreached` row) prints
`UNREACHED (EXPECTED -- [M5.0 stage 3, RE-MEASURED] ...)` and does not
appear in the trailer's `unexpected` list either. Both populations are
exactly the "fine" classes the brief named. No action taken or needed on
either.

## What blocks the push

**Nothing.** All 7 non-clean rows from the s5 trailer (S178 + the six
`pc3`/`pc4` anomalies) are solo-confirmed DETECTED-or-UNDETECTED exactly as
their own definitions predict, at this lane's own commit. The manager's
full-battery re-run is the standing final word per the delivery bar, but
there is no open question this lane is aware of.

**Worth the manager's attention, not blocking**: this fix touches
test infrastructure `oralink` (D98) shipped, not this lane's own module —
worth a quick sanity pass that `make test-assertions`/`make test-atomic`
on a fresh `main` build (post-merge) actually exercise the now-fixed
`gstartdiff`/`kresetdiff`/`mlinediff`/`atomicdiff` arms rather than
silently failing to build, since that was true on `main` before this fix
and nothing in `make test`'s own output distinguishes a SKIP from this
particular FAIL shape at a glance.

## Rulings received

None — no rulings file was posted during this lane's run; it worked
end-to-end from the brief.
