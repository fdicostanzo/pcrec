# Lane regred — why `make test`'s registry section exits 1 on darwin

## Cause

`tests/registry/run_registry_tests.sh` is a chain of independent checks
(`registry_check`, `compliance_section.py`, PC-3 `pcre2_check`, PC-4,
`axes_registry_check.sh`, `limits_check.sh`, the definitions structural
check, the definitions-oracle self-check). Each chained script's own PASS
count is pinned by an exact-count "coverage guard" so a deleted check is
visible even on a green run. **The `limits_check.sh` guard was stale.**

`[LIM-OVR]` (2026-09-22, `docs/dev/plan.md`'s O-18 §3(a) finding) added
"part 4, OVERRIDE HONESTY" to `limits_check.sh`: three new PASS lines
(`[override-src]` x2 — the `raise_only_limits[]` manifest check and the
bespoke `--warn-emit-bytes=` site check — and `[override-honesty]`, the
BUILD_D/FLAG_D cross-check). That landing never re-pinned
`run_registry_tests.sh`'s own count guard, which still read:

```
tests/registry/run_registry_tests.sh:586:if [ "$limitsn" -ne 24 ]; then
```

`limits_check.sh` now emits **27** PASS lines (confirmed in the cited gate
log, `checks passed: 27` / `checks failed: 0`), so the guard fires its
"COVERAGE CHANGED" branch and sets `rc=1`, which `exit $rc` at the end of
`run_registry_tests.sh` propagates to `test-registry`'s own exit code.

**Why this reads as "everything green"**: the guard's message
(`tests/registry/run_registry_tests.sh:588`, `"registry: limits_check
COVERAGE CHANGED — $limitsn passing checks, expected 24."`) never contains
the substring `FAIL:` — it is a `registry:`-prefixed informational line by
design, the same shape every other coverage guard in this file uses (the
`registry_check`/PC-3/axes guards at lines 96-109, 274-293, 540-552 all
share it). So a log scanned for `FAIL:` or for `checks failed:` (nonzero)
finds nothing, while `test-registry` still exits 1. Confirmed in the exact
log the brief cited:

```
/private/tmp/claude-501/-Users-fdicostanzo-pcrec/c7ec5900-bab2-4d19-b2df-f72f9b26896b/scratchpad/gate_ff63ebf3.log:2151:
registry: limits_check COVERAGE CHANGED — 27 passing checks, expected 24.
```
(line 2151, immediately after `checks passed: 27` / `checks failed: 0` at
line ~2149-2150, and immediately before `PASS: definitions: ...` resumes —
i.e. no `FAIL:` line anywhere near it, exactly as the brief described.)

**Confirmed against the landing lane's own report**: `docs/dev/lanes/
admin1_report.md` ([MACPORT-XARGS] + [LIM-OVR] bundle, 2026-09-22, lane
admin1) states validation as `"limits_check.sh 27/0"` — i.e. admin1 ran
`limits_check.sh` standalone and correctly saw 27 passing/0 failing, which
is right. What was never re-run (or re-pinned) was `run_registry_tests.sh`
itself, the DIFFERENT file that chains `limits_check.sh`'s output through
its own hardcoded count guard. Editing the checked file and validating it
directly, without touching or re-running the file that counts it, is
exactly how the pin went stale.

**This is NOT a standing darwin-known red.** Nothing about the mismatch is
platform-specific — `limits_check.sh`'s PASS count is a pure function of
the script's own code and the tree's `limits.def`/`cli/main.c` contents,
identical on Linux. The same log would show the identical red on the CI
box. It is a plain recipe/pin bug: a caller-observable-check landing that
missed re-pinning one of its own readers, the same class D94's addendum
already names ("a reader whose text never cites the number still moves
with it") — `run_registry_tests.sh`'s guard cites no `[LIM-OVR]`-specific
text, so a grep for the feature's own name would not have found it either.

## Fix

`tests/registry/run_registry_tests.sh` (commit afb6a5a5 on `lane/regred`):
re-pinned the guard from 24 to 27, with the same explanatory-comment
convention every other pin move in this file already uses (see the
existing `[REG-SV]` comment chain in the same file for the axes guard's
precedent). No other reader of the `24` figure exists — grepped the whole
tree for `expected 24`, `-ne 24`, `limitsn`, `LIM-1.*24`; the only hits
outside this file (`tests/CLAUDE.md`, `tests/counterk/CLAUDE.md`,
`docs/testing.md`) are unrelated features (`island`/`counterk` test
counts) that coincidentally also say "24 checks". `tests/registry/
CLAUDE.md` documents `limits_check.sh`'s four parts including `[LIM-OVR]`
but never states its PASS count, so nothing there needed updating.

Zero `src/` changes, as scoped. No `docs/spec/` hunk needed — `[LIM-OVR]`
itself already landed its own spec/behavior; this fixes only the stale
test-harness pin that missed it.

## Disposition for docs/testing.md's darwin known-reds list

**Not added.** This is not a darwin-specific known-red; it is a fixed
recipe bug, and the fix in this same commit closes it. Recorded here
instead, per the situation-index row about a check-design fix: `docs/dev/
learnings.md` §3 already generalizes the "a control's own re-pin is missed
at the landing that needs it" pattern (see the multiple prior instances
this file's own comment history documents: [LIM-2] N1's row missed
2026-09-04/re-pinned 2026-09-05; `[REVW.4]` wave 4 missed the same shape
one item later). This is a fourth instance of the identical failure mode
in the identical file, worth a §3 addendum if the manager wants one — not
attempted here (read-only outside the target file, and out of this lane's
scope).

## Validation — OWED

**Box rule**: `worktrees/optimpl1`'s `make test-axes` sweep (pid 66860)
was still running (~5 min elapsed) when this lane's investigation
finished, so per the one-heavy-suite-at-a-time box rule I did not launch
`make test-registry` (a full build + link + run of every registry
sub-check, including PC-3 and PC-4, is a heavy suite on this box).

**Owed**: once pid 66860 is confirmed gone (`kill -0 66860`), run in this
worktree:

```
cd /Users/fdicostanzo/pcrec/worktrees/regred
timeout 1800 make test-registry CC=gcc-16 > build/regred_registry.log 2>&1; echo rc=$?
```

Expected: `rc=0`, with `limits_check` showing `checks passed: 27` /
`checks failed: 0` and no `COVERAGE CHANGED` line. If a *different*
coverage guard fires instead (registry_check's 225, PC-3's 209, or axes'
108), that is a SEPARATE stale pin from whatever landed between the
gate log's commit (ff63ebf3) and `main`'s current HEAD (511dee26) and
should be triaged the same way this one was (diff the guard's expected
number against a fresh run's actual PASS count).

## Handback

Branch `lane/regred` (from `main` 511dee26), one commit (afb6a5a5),
this report committed alongside it. `tests/registry/CLAUDE.md` needed no
edit (see above). Validation numbers are OWED per the box rule above —
not a gap in the analysis, a wait on another lane's exclusive box time.
