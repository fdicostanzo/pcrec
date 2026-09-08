# lane ntriage — night_20260907 triage report

Charter: triage and classify the four red stages from the overnight Linux
run (`night_20260907`, commit `2786497c`, ubuntubudu) — `test.log`,
`encchk.log`, `uprops_utf8.log`, `mech.log` — REAL-REGRESSION vs
STALE-PIN/CALIBRATION vs ENVIRONMENT, fixed where fixable.

Branch: `lane/ntriage`, worktree `worktrees/ntriage`. Not merged to main.

## Summary table

| # | red | classification | status |
|---|---|---|---|
| 1 | uprops oracle build failure (Linux, rc=2) | **REAL DEFECT** (include-order bug in a shared header, latent since the file was written, never exercised on Linux until this run) | FIXED, committed |
| 2 | test-rxtsource population pin mismatch | **STALE PIN** (a re-pin lane touched CENSUS_*/RUNSH_* but never C3_*, a different denominator nobody was watching) | FIXED, re-pinned with full derivation |
| 3 | encchk DD12a(i) (4 failures) | **STALE CALIBRATION** (manifest calibrated at a 250-block light-run sample, never re-measured at the full 2,994-block population) + **one real check-design bug** (a classifier gap; a truncation-vs-staleness conflation) | FIXED, committed; full-population re-verification OWED (in flight, see §3.5) |
| 4 | mech S-U9 UNDETECTED/UNEXPECTED | **STALE EXPECTATION** (reached, zero population for the behavioural cross product it needs — same shape as the already-documented S-U6) | FIXED (re-classified), committed |

All four are diagnosed and fixed in this worktree. Nothing here is a genuine
regression in pcrec's own matching behaviour — every classification above is
either a latent build-portability bug (#1), a bookkeeping/pin staleness
(#2, #4), or a check-calibration gap plus one real check-design bug (#3).

---

## 1. uprops oracle build failure — REAL DEFECT, FIXED

**Symptom:** `tests/uprops/uprops_oracle.c` failed to build on Linux/glibc:
`implicit declaration of 'dlinfo'`, `'RTLD_DI_LINKMAP' undeclared`. Compiled
clean on darwin.

**Root cause, confirmed:** `tests/fuzz/pcre2_abi.h`'s own contract (stated in
its neighbour `tests/registry/pcre2_check.c`'s header comment: "pcre2_abi.h
defines _GNU_SOURCE, needed before any libc header") requires it be the
FIRST `#include` in any consumer, because glibc locks in the feature-test-
macro decision the first time `<features.h>` is pulled in for the whole
translation unit — a later `#define _GNU_SOURCE` has no effect once that has
happened. `uprops_oracle.c` included `<stdio.h>`/`<stdlib.h>`/`<string.h>`
**before** `"pcre2_abi.h"`, so on Linux/glibc `__USE_GNU` was never set when
`<dlfcn.h>` was later processed, and `dlinfo()`/`RTLD_DI_LINKMAP` (declared
under `#ifdef __USE_GNU`) never appeared. Invisible on darwin because that
branch is `#ifdef __APPLE__`-gated to `dladdr()` instead and never touches
`<link.h>`/`dlinfo()` at all — confirmed by reading the `#ifndef __APPLE__`
guard around the `dlinfo()` call site.

Grepped every other `pcre2_abi.h` consumer (`pcre2_oracle.c`,
`pcre2_check.c`, `definitions_oracle_check.c`, `pc4_check.c`,
`probe_uprops.c`) — all five already put it first. `uprops_oracle.c` was the
only violator.

**Fix:** reorder `uprops_oracle.c`'s includes (`tests/uprops/uprops_oracle.c`).
Also added a defensive `#error` inside `tests/fuzz/pcre2_abi.h` itself
(non-Apple only, gated behind the same `#ifndef __APPLE__` the `dlinfo()`
branch already uses): if `__USE_GNU` is not set by the time `<dlfcn.h>` has
been processed, it fails with a clear message pointing at the include-order
rule, instead of the cryptic two-line glibc error. This is a general fix for
the defect CLASS (a future third consumer making the same mistake), not just
this one file.

**Verified locally (darwin — this bug never manifested here, so this proves
no regression, not the Linux fix itself):**
- `make -j4 CC=gcc-16` — clean.
- `make strict CC=gcc-16` — clean.
- `bash tests/uprops/run_uprops_tests.sh` — `25 passed, 0 failed` (both byte
  and utf8 arms, §1-§4 all PASS).

**OWED to the Linux re-validation:** `bash tests/uprops/run_uprops_tests.sh`
and `ENC_MAX_BLOCKS=250 bash tests/codegen/run_encoding_checks.sh` (which
also links against `pcre2_abi.h`) should both build and run clean on
ubuntubudu now. Expected: `uprops: 25 passed, 0 failed`.

Commit: `a38ca912`.

---

## 2. test-rxtsource C3 population pin mismatch — STALE PIN, FIXED

**Symptom:** Linux run reported `PASS: got 13728, pinned 13876; SKIP: got
14997, pinned 14486; pcre2-only: got 2779, pinned 2268` in
`tests/rxtsource/run_rxtsource_tests.sh`'s C3 check (`verify_rxt.py`'s own
population, a DIFFERENT denominator from `CENSUS_FILES`/`RUNSH_FILES`).

**Root cause, derived and verified digit-for-digit:** the C3_PASS/SKIP/
PCRE2ONLY pins were last set at commit `0c34f5e0`. Between that commit and
the `[M5.0]` stage 3 merge (`819ec889`), the `[K50-BNDSTART]`/
`[K50-NULLGATE]` lane merges landed FIRST (K50 was fixed before stage 3
launched) and moved this same population, then stage 3's own axis04
promotion moved it again. Lane `utf8s3`'s own re-pin commit (`0b314761`)
caught `CENSUS_FILES`/`CENSUS_BLOCKS`/`CENSUS_LINES` and `RUNSH_*` but never
touched `C3_PASS`/`C3_SKIP`/`C3_SKIP_PCRE2ONLY` — a different denominator
nobody was watching.

Derived the exact movement per corpus file diff (see the new comment block
in `tests/rxtsource/run_rxtsource_tests.sh`):
- `axis04_p_categories.rxt` promotion: 148 `perr` blocks (each an agreeing
  "both engines decline `\p`" trivial PASS) became 136 live
  `# pcre2-only` blocks (462 lines) plus 12 blocks moved to
  `tests/known_fail/k53_uprops_oversize.rxt` (44 lines, also pcre2-only,
  counted — `verify_rxt.py` has no `known_fail` exclusion) → **-148 PASS,
  +506 pcre2-only/SKIP**.
- `axis09_nextpos_findall.rxt` (K50 fix): 2 now-invalid mid-character `ms`
  cells removed, relocated to `run_startbnd_diff.sh` Sec 6 → **-2**.
- `tests/known_fail/k50_utf8_dfa_midchar_start.rxt`: deleted (bug fixed,
  witness obsolete) → **-1**.
- `axis11_startpos_boundary.rxt` (new, K50's regression proof): 8 new
  pcre2-only cells → **+8**.

Net: **-148 PASS, +511 SKIP/pcre2-only** — matches the Linux "got" numbers
exactly (13876-148=13728; 14486+511=14997; 2268+511=2779), and
independently reconciles against the already-correct `CENSUS_LINES`
(28814): `13728 + 14997 + 89 (the one timed-out file's own line count) =
28814` exactly.

**Not lost coverage:** the -148 PASS were trivial "both engines decline
`\p`" agreements (the module wasn't wired yet); the 506 replacing them are
real membership assertions checked by `tests/uprops/`'s stronger whole-
code-point-space libpcre2 differential (0 divergences at landing) instead.
The axis09/known_fail movement is a relocation to a purpose-built
differential, not a deletion of a checked claim. axis11 is net new
coverage.

**Fix:** re-pinned `C3_PASS=13728`, `C3_SKIP=14997`,
`C3_SKIP_PCRE2ONLY=2779` in `tests/rxtsource/run_rxtsource_tests.sh`, with
the full per-file derivation as a comment.

**Verified:** the arithmetic reconciliation above is exact and independently
cross-checked against `CENSUS_LINES`. **Could not be exercised live on this
box**: darwin's C3 never reaches the pin-comparison code at all
(`c3rc != 0` from real python-3.9.6-version cell mismatches in
`caseless.rxt`/`counterk.rxt`/`captures.rxt` — none of the files this pin
touches, and documented as a pre-existing box-sensitivity red in the
script's own "BOX SENSITIVITY" comment). This is definitively unrelated to
the fix: the script only reads the `C3_PASS`/etc. pins inside
`if [ "$c3rc" -eq 0 ]`, which this box's run never enters regardless of the
pin values.

**OWED to the Linux re-validation:** `bash tests/rxtsource/
run_rxtsource_tests.sh` should read all nine C3 population pins PASS
(`checks passed` line), including "C3 reconciles: 13728 verified + 14997
skipped + 89 in the timed-out file = 28814".

Commit: `3b602379`.

---

## 3. encchk DD12a(i) — STALE CALIBRATION + one real check-design bug, FIXED

**Symptom (Linux, `encchk.log`):** four `FAIL` lines at
`ENC_MAX_BLOCKS=0` (full population, ~6,600 compiles) against a manifest
(`tests/codegen/manifests/k50_gate_refinement.txt`) calibrated only at the
`ENC_MAX_BLOCKS=250` light-local-run default:
(i) 164 pairs entered the K50 gate-refinement class without a manifest row;
(ii) the FORM sub-class at 29 against a ceiling of 8;
(iii) the undeclared-form exception list at manifest=3 vs run=13;
(iv) 24 of 2,793 strict-identity pairs differing outside the named
encoding-owned regions (finding lines `\Z`, `\b` x2, `\B`, `$` x2,
`(?m)\Z`, `\bx*`).

**Investigation.** Reproduced the exact Linux population locally
(source-text comparison, platform-independent by the check's own design):
extracted the check's own census + DD12a(i) python heredocs and ran them
directly against a full-population `blocks.tsv` (2,994 ASCII blocks) —
**PAIRS=2990 STRICT=2793 DIVERGE_STRICT=24 GATE=194 GATEFORM=29**, matching
the Linux numbers digit for digit. This confirms darwin and Linux see
byte-identical populations and that my local investigation is trustworthy
without needing the Linux box.

**Finding (iv) is NOT a separate defect from (iii)** — it is the same stale
manifest surfacing twice through two different assertions in the same
script: when the UNDECLARED exception list fails to match exactly, the
script's `DIVERGE_STRICT` variable is never reset to 0 (`run_encoding_
checks.sh:958`), so the SAME 13 pattern texts (24 raw compiled instances)
also trip the generic "differ outside named regions" failure at line 966.

**Regenerated the six named witnesses directly** (`\Z`, `$`, `\bx*`, and
compared `\D+`/`\p{Pc}+`/`[\D]+`/`[\h\d]+`/`[[:^alpha:]]+`/`\h+`/`\v+`
against their byte twins) and confirmed by reading the full diffs: every
one of these is a legitimate K50/axis-E FORM divergence (an extra byte-
equivalence class for the utf8 continuation-byte range, which is exactly
what the manifest's own header already documents as the expected
mechanism) — **not** a real per-encoding miscompile. No control-flow
difference beyond the already-excised K50 guard block was present in any
sample.

**A real, scoped check-design bug fell out of the investigation.**
`widens_under_utf8()` (the classifier that exempts a pattern from the
strict byte-identity bar when its byte-equivalence-class count genuinely
grows under utf8, e.g. `.`/`[^...]`) recognized only those two literal
spellings. MEASURED (compile both encodings, diff the class-legend
comment) to ALSO apply, and previously missed: `\D \S \W \H \V` (negated-
by-meaning shorthand escapes: `\D+` byte 2 classes → utf8 14), `\N` (any-
char-except-newline), `\h`/`\v` (lowercase, POSITIVE horizontal/vertical
whitespace — MEASURED to widen anyway, where `\d`/`\s`/`\w` show **zero**
diff at all, i.e. stay on the project's documented ASCII-only fold: `\h+`
byte 2 → utf8 6), `\p{...}`/`\P{...}` (module unicode-props, unborn when
this classifier was first written: `\p{Pc}+` byte 2 → utf8 13), and POSIX
negated classes (`[:^...:]`: `[[:^alpha:]]+` byte 2 → utf8 15) — in or out
of a class (`[\D]+` byte 2 → utf8 14). Fixed in
`tests/codegen/run_encoding_checks.sh`'s `widens_under_utf8()`.

**Re-measured at full population after the fix:** STRICT 2793 → 2754 (39
patterns correctly moved to WIDENS, which needs no manifest row at all),
GATE 194 → 174, GATEFORM 29 → 14 (raw pairs; 2 of the removed ones were the
newly-recognised `^[[:^lower:]]$` and `^\N{2,3}$`), DIVERGE_STRICT 24 → 22
(11 distinct pattern texts remain, was 13).

**Re-derived the manifest from the corrected full-population run**: 153
GATE members (up from 13), of which 11 are the FORM sub-class (up from 4,
same axis-E mechanism, more spellings — `$|\n`, `[a-z]*$`, `[ab]{0,4}$`,
`a*$`, `a*\Z`, `a*b*$`, `a{0,4}$`, `a{0,4}\Z`, `a{0,5}b{0,5}$`, `b*$`,
`x*$`), and 11 UNDECLARED-form exceptions (up from 3 — `$`, `(?m)\Z`,
`\B`, `\B\B`, `\Bx*`, `\Z`, `\b`, `\b\b`, `\b\w*`, `\bx*`, `\bx?`). 46 of
the 142 non-FORM GATE members are `tests/base/k18_deep_nesting.rxt`'s
deeply-nested `(?:...)*` towers and `tests/base/k18_split_shapes.rxt`'s
alternation/quantifier generator patterns (K18's own regression corpus —
heavily `a*`/optional-branch shaped, so K50-NULLGATE's nullability
predicate reaches nearly all of it); the rest are scattered across the
tree's other nullable/unanchored patterns. None traced to a source outside
the tree's own existing test corpus, and none is a new mechanism — every
one is a legitimate population member the 250-block calibration sample
never reached. Ceiling raised 8→16 (measured 11, with headroom matching
the file's own convention); floor left at 10 (a collapse tripwire, still
valid at 164).

**A SECOND real check-design bug found while doing the re-derivation**: the
manifest's exact-match staleness/growth guards compare against ONLY the
patterns this run's own (possibly `ENC_MAX_BLOCKS`-truncated) `blocks.tsv`
actually swept, with no way to distinguish "reached but stopped diverging"
(a real expiry) from "not reached in this slice" (an artifact of the
250-block light-run default) — so a manifest correct at full population
necessarily broke the required-green `ENC_MAX_BLOCKS=250` local default
(measured directly: 140 of 153 rows falsely read STALE, the light run went
from `checks passed: 11, checks failed: 0` to `10/3`). **This directory's
own §8.5 K51 manifest already has this exact problem and its own fix**
(`run_encoding_checks.sh:284-289`: a manifest row is checked against
whole-corpus presence only when it was NOT among this run's own swept
blocks, and reads as an informational "not reached in this slice" line
rather than a failure). Applied the identical shape to both the GATE
staleness check and the UNDECLARED exact-match check.

**Found and fixed one more bug while applying that fix**: the GATE class's
own reachability set is derived by walking `k50man.txt`, which is
`grep -v '^#'`-filtered and therefore structurally excludes every
`#UNDECLARED` line — reusing it for the UNDECLARED check silently read
every UNDECLARED row as unreached regardless of `blocks.tsv` (measured: 0
of 11 read reachable while 3 were visibly diverging in `k50strict.txt`,
which can only mean they had compiled this run). Fixed with a second,
UNDECLARED-specific reachability pass.

**Verified:**
- `ENC_MAX_BLOCKS=250 bash tests/codegen/run_encoding_checks.sh`: **checks
  passed: 11, checks failed: 0** (restored to the required baseline; log
  `/tmp/encchk_investigate/enc250_after3.log`).
- The full-population arithmetic (exact-set match, 0 stale, 0 grown, 0
  undeclared mismatch) was verified by direct `comm`/`diff` simulation
  against the corrected classifier's full-population output before writing
  the manifest.

**OWED — full-population (`ENC_MAX_BLOCKS=0`) end-to-end confirmation is
running in the background at hand-back time**, since it is a genuinely
heavy run (§8.5 alone compiles+links+runs ~6,000 artifacts):
- Command: `PCREC="$PWD/build/pcrec" CC=gcc-16 ENC_MAX_BLOCKS=0 bash
  tests/codegen/run_encoding_checks.sh`
- Log: `/tmp/encchk_investigate/enc_full_final.log` (this Mac's scratchpad
  — not committed; PID 84952 at launch)
- Expected completion line: `checks passed: 11` / `checks failed: 0`
- If it does NOT read 11/0, the most likely residual is a corpus edit
  landing on `main` between this lane's branch point and whenever it is
  re-run (a legitimate re-pin need, not a sign this derivation was wrong)
  — re-run the derivation steps in this section rather than hand-editing
  the manifest.
- **The Linux re-validation is the SAME command** on ubuntubudu; the
  derivation above claims (and this Mac's exact digit-for-digit
  reproduction of the ORIGINAL failure numbers supports) that the
  population is platform-independent, so the Linux run should read the
  same 11/0 this Mac's local full run is expected to.

Commit: `b7c8d43e` (classifier fix + manifest re-derivation + reachability
scoping, all in one change since they were discovered and fixed together).

---

## 4. mech S-U9 — STALE EXPECTATION, FIXED

**Symptom:** `S-U9-back-step-length-test-deleted` (the utf8 `back_step`'s
declared-length test) scored `UNDETECTED — ZERO CHECKS FAILED` with no
`SAB_EXPECT` declared, an unexpected mismatch, despite `reach:ok` and its
population floor holding (8 ≥ 6).

**Investigation.** The row's own comment names two routes to the hazard: (a)
an ill-formed continuation-byte run under a negative lookbehind, (b) a
mid-character caller-supplied `startpos` on an otherwise well-formed
subject. Grepped every `(?<!` occurrence under `tests/utf8/`: axis08's own
`(?<!.)x` cells (this row's `SAB_REACH` witness) run only against
well-formed subjects (`"ax"`, `"zx"`, `"\nx"`); axis03/axis10 test
ill-formed/surrogate subjects against `.`/`[^a]`/`\p{L}`, never a
lookbehind. **The behavioural cross product this row needs — a lookbehind
pattern over an ill-formed run — is empty in the corpus.** Confirmed by a
solo mech run: `reach:ok(1/1), corpus:0fail/1656pass`.

**Route (b) is now independently closed on the default axis**, confirmed
by inspecting an emitted utf8 artifact's `rx_search` prologue: `[K50]`'s
caller-startpos guard (landed after this row was written) refuses any
non-boundary `search_from` with `PCREC_ERR_STARTPOS` before any assertion
logic runs. Only `-fno-startpos-guard` still reaches route (b); the
default build's sole remaining route is (a), which the corpus does not
exercise.

**Classification: same shape as `S-U6`** (`docs/dev/known_issues.md`'s own
precedent) — a construct-level `SAB_REACH` proves the doorway is open
while the behavioural population it needs has no witness, and the closing
witness needs a real libpcre2 oracle answer for ill-formed UTF-8 under
`PCRE2_MATCH_INVALID_UTF`/no-`PCRE2_NO_UTF_CHECK` semantics — the same
UTF8-vs-libpcre2 corpus follow-up `S-U6`'s own header names as owed to the
admin queue, not something buildable as a small targeted check here.

**Fix:** re-classified `SAB_EXPECT=UNDETECTED` with the closing witness
named, matching `S-U6`'s exact shape (comment + `SAB_EXPECT`, no
`SAB_EXPECT_REASON` needed — that field is `UNREACHED`-only).

**Verified:** `bash tests/mech/run_sabotage_matrix.sh 'S-U9'` now reads
`UNDETECTED (EXPECTED — see this row's SAB_DOC_FIGURE for what would close
it)`, `unexpected: 0`.

Commit: `ed01a576`.

---

## What is owed to the manager / Linux executor channel

Exact commands, in priority order:

1. **`bash tests/uprops/run_uprops_tests.sh` on ubuntubudu** — confirms
   red #1's fix actually builds under glibc (never testable on darwin,
   since the bug never manifested there). Expected: `25 passed, 0 failed`.
2. **`PCREC=build/pcrec CC=gcc-16 ENC_MAX_BLOCKS=0 bash
   tests/codegen/run_encoding_checks.sh` on ubuntubudu** (or wherever the
   merge-time battery runs it) — the authoritative confirmation of red #3's
   fix. This Mac's own full-population run is in flight at hand-back
   (§3's "OWED" block); if it comes back green here, the Linux run should
   too, since the derivation is source-text-based and platform-independent
   by the check's own design (already confirmed once, on the ORIGINAL
   failure numbers).
3. **`bash tests/rxtsource/run_rxtsource_tests.sh` on ubuntubudu** —
   confirms red #2's re-pin against the real C3 python-oracle run (this
   Mac's own C3 never reaches the pin-comparison code, for an unrelated,
   pre-existing reason — see §2).
4. A full `make mech` (or at minimum `bash tests/mech/run_sabotage_matrix.sh
   'S-U9'`) re-confirms red #4's re-classification lands clean in the
   merged tree.

None of these four fixes touch each other's files; they can run
independently of the merge order.

## Validation summary (this worktree, darwin/gcc-16)

- `make -j4 CC=gcc-16` — clean.
- `make strict CC=gcc-16` — clean, 0 warnings.
- `bash tests/uprops/run_uprops_tests.sh` — 25/0.
- `ENC_MAX_BLOCKS=250 bash tests/codegen/run_encoding_checks.sh` — checks
  passed: 11, checks failed: 0.
- `bash tests/mech/run_sabotage_matrix.sh 'S-U9'` — unexpected: 0.
- `bash tests/rxtsource/run_rxtsource_tests.sh` — arithmetic verified by
  hand (13728+14997+89=28814); live run blocked by a pre-existing,
  unrelated darwin python-version red (documented in §2).
- Full-population `ENC_MAX_BLOCKS=0` encoding-checks run: OWED, in flight
  at hand-back (§3).

Never ran the full `make test`/`make mech` battery — out of scope for a
targeted triage lane per the brief, and each fix's own targeted validation
is listed above and in its own section.
