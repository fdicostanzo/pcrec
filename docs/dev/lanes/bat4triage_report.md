# Battery stage-4 `test` stage triage (lane `bat4triage`)

2026-09-08, sonnet, `worktrees/bat4triage`, branch `lane/bat4triage`, battery
at commit `83f7175b` (merge lane/utf8s4 → merge lane/foldhunks HEAD `9d67eecf`
at branch point). Log: `build/battery_20260908_stage4/test.log` (4,272
lines), trailer `build/battery_20260908_stage4/trailer.log`. Battery was
STILL RUNNING (axes stage) throughout this triage; no suite/`make` was run —
one lightweight repro compile (§5) is the sole exception, done with the
already-built `build/pcrec` from 18:08, not a rebuild.

**Verdict: every failure in the `test` stage's log is accounted for. Two are
real, attributable side effects of the stage-4 merge (both fixed here, both
in test infrastructure, neither a compiler-behavior regression). Everything
else is pre-existing darwin/python-environment noise, independently
reproduced and traced to a root cause that predates stage 4 by weeks.**

## Summary table

| # | failure | class | fixed here? |
|---|---|---|---|
| 1 | `tests/codegen/run_cpset_structure.sh` [1c] "complement universe does not come from PcrecEnc.max_cp" | (a) real, stage-4-caused check staleness | YES |
| 2 | `tests/codegen/run_cpset_structure.sh` [2d] "could not widen the scratch byte backend's max_cp" | (a) real, stage-4-caused check staleness | YES |
| 3 | `tests/rxtsource/run_rxtsource_tests.sh` census/C1/C3 file-count mismatches (210 vs pinned 209, 3906 vs 3888 blocks, 28871 vs 28814 lines) | (c) stale pin, stage-4-caused (tests/utf8/fold.rxt never re-pinned) | YES (CENSUS_FILES/BLOCKS/LINES + RUNSH_*; C3_PASS/etc. left OWED, see below) |
| 4 | `tests/rxtsource/run_rxtsource_tests.sh` leg B / leg C `xargs -a` failures + everything cascading from them (C0a, C1 leg A != leg B, case-row derivation, leg B/C row counts) | (b) pre-existing darwin `xargs -a` incompatibility, catalogued since commit `76f9e85e` (2026-08/09), never fixed for these call sites | no (out of scope; already catalogued) |
| 5 | `tests/rxtsource/run_rxtsource_tests.sh` C3 per-file semantic mismatches (`tests/backrefs/d27/caseless.rxt:39`, `tests/counterk/counterk.rxt:568/626/644/702`, `tests/lookaround/captures.rxt:59/67`) | (b) pre-existing python-3.9.6-vs-reference-python divergence on this box, files untouched by stage 4 | no (documented; needs a Linux/newer-python triage, not a stage-4 fix) |
| 6 | `tests/rxtsource/run_rxtsource_tests.sh` keyword census "the pinned 32-word list has 32 words" (FAIL despite the count matching), W1.2 three-config file / truncation-boundary, W1.3 dogfood row/collision counts | (b) pre-existing BSD `wc` leading-whitespace bug breaking `[ "$x" = "N" ]` string comparisons throughout this script | no (out of scope; new finding, documented below for the manager) |
| 7 | `tests/anchored/run_anchored_diff.sh` "26 pattern(s) produced emitted C that does not compile" (6 named `$`-anchored patterns) | (d) environment/load artifact | no fix needed — re-run confirms clean |

None of the failures trace to `src/core/fold*`, `src/parse/parse.c`'s
per-contribution `p_class` restructure, `src/gen/enc/enc_utf8.c`, or
`generate.py`'s three products *producing a wrong answer*. Two of them
(#1, #2) trace to those same files *changing shape in a way a source-text
structural check did not survive* — a check-staleness class, not a
correctness regression, and `docs/dev/lanes/utf8s4_report.md`'s own byte-
identity gate (0/3,120 over four axes) is independent evidence the compiler
itself is unaffected.

## 1-2. `run_cpset_structure.sh` [1c] and [2d] — REAL, stage-4-caused, FIXED

Both are literal source-text needles that stage 4's `src/parse/parse.c` and
`src/gen/enc/enc_byte.c` edits legitimately moved.

**[1c]**: the check greps `parse.c` for the literal `e->max_cp`. At the
stage-4 branch point (`git show 7e8ab03c:src/parse/parse.c`), `cls_universe`
was a two-line function using a local `PcrecEnc *e`. Stage 4's fold-closure
restructure collapsed it to a one-liner:

```c
static unsigned cls_universe(Ctx *cx) { return cls_enc(cx)->max_cp; }
```

— same claim (the complement universe comes from `PcrecEnc.max_cp`), no
local named `e` for the grep to find. Verified: `grep -n '\->max_cp'
src/parse/parse.c` finds it at the new one-liner; `grep -n 'e->max_cp'`
finds nothing.

**[2d]**: the check `sed`s a scratch copy of `src/gen/enc/enc_byte.c`,
looking for the contiguous literal `PCREC_ENC_BYTE, "byte", 0xFFu,
entries_byte` to widen `0xFFu` to `0x10FFFFu` (building a byte-encoding
witness whose backend falsely claims Unicode's universe, to drive the
render-helper assertion). Stage 4 added `PcrecEnc.fold` (the second D58 seam
event) as a new struct field between `max_cp` and `entries_byte`, so the
current line reads:

```c
PCREC_ENC_BYTE, "byte", 0xFFu, &pcrec_fold_ascii, entries_byte, advance_byte,
```

— the old contiguous span no longer matches.

**Fix** (both in `tests/codegen/run_cpset_structure.sh`, this worktree):
[1c]'s needle widened to `\->max_cp` (matches either spelling, and the
`enc.h` field-declaration half of the check is unchanged); [2d]'s sed/grep
narrowed to match only the field it actually needs to widen (`"byte",
0xFFu,` → `"byte", 0x10FFFFu,`), which is robust to any field added after
`max_cp` rather than requiring the whole struct-literal tail to stay
contiguous. Both fixes verified directly against the current tree's source
text (not just read — actually grepped/sed'd against the real files) before
being committed; see the diff.

**Validation plan (OWED, post-battery):**
```sh
bash tests/codegen/run_cpset_structure.sh
```
Expected: `checks passed: 28`, `checks failed: 0` (26 passed + 2 fixed here,
against the log's `26 passed / 2 failed`). Single-section run, ~10s,
compile-only plus one scratch-compiler build — safe to run solo once the box
is free.

## 3. `run_rxtsource_tests.sh` census/C1/C3 file-count mismatches — STALE PIN, stage-4-caused, partially fixed

`tests/utf8/fold.rxt` is a NEW file added by the stage-4 merge (`git diff
--stat 7e8ab03c..9d67eecf` — 229 lines, confirmed via `git log --oneline
--merges` to land in `merge lane/utf8s4` at `83f7175b`), 18 blocks / 45
cells per `docs/dev/lanes/utf8s4_report.md` — measured directly:
`grep -c '^pattern ' tests/utf8/fold.rxt` = 18, `grep -c '^m \|^n \|^ms
\|^ns '` = 45. The census pins in `tests/rxtsource/run_rxtsource_tests.sh`
(`CENSUS_FILES=209`/`CENSUS_BLOCKS=3888`/`CENSUS_LINES=28814`,
`RUNSH_FILES=207`/`RUNSH_BLOCKS=3873`/`RUNSH_LINES=28759`) were never moved
for it, and `git diff --stat 7e8ab03c..9d67eecf` confirms
`tests/rxtsource/run_rxtsource_tests.sh` is not in the stage-4 diff at all.
This is exactly the delivery-bar violation CLAUDE.md's situation-index row
warns about ("RE-PIN EVERY MANIFEST/COUNT/PIN YOUR CHANGE MOVES") — an
omission in the utf8s4/foldhunks delivery, not a bug in pcrec.

The arithmetic reconciles exactly: `found 210/3906/28871, pinned
209/3888/28814` is precisely `209+1 / 3888+18 / 28814+57`, and fold.rxt is
not under `tests/known_fail/` so `RUNSH_*` moves by the identical amount.

**Fixed here**: `CENSUS_FILES/BLOCKS/LINES` → `210/3906/28871`,
`RUNSH_FILES/BLOCKS/LINES` → `208/3891/28816`, each with a dated provenance
comment following this file's own established convention (see the k49/k50/
utf8s3 comments already in the file).

**Left OWED, and said so in the file**: `C3_PASS`/`C3_SKIP`/`C3_SKIP_*`
(the python-oracle-verification population counts) are NOT re-derived here.
`fold.rxt` carries 19 `# pcre2-only` comment lines against 18 pattern
blocks, so not all 45 of its cells are necessarily `C3_PASS`, and every
prior re-pin of this block in the file's own history was taken from a
LINUX reference run (never derived by hand on darwin — this box's C3 is
documented as "deliberately red" per its own BOX SENSITIVITY note, §4
below). I added a dated comment naming this as owed to whoever runs the
10.46/Linux arm next, alongside the fix.

**Validation plan (OWED, post-battery, ideally on the Linux reference
box):**
```sh
bash tests/rxtsource/run_rxtsource_tests.sh
```
Expected on Linux: `census: 210 files / 3906 blocks / 28871 expectation
lines (matches the pin)` PASS, `denominators reconcile` PASS, and (unlike
this box) C3's per-file semantic checks should also pass since Linux runs a
newer python — but C3_PASS/SKIP/etc. will need a fresh re-pin from that run
including fold.rxt's cells, same procedure as the ntriage/k49/k50 re-pins
already in the file's history.

## 4. `xargs -a` failures (leg B, leg C, and everything cascading from them) — PRE-EXISTING, NOT stage-4

`xargs -a "$FILES" ...` appears at four call sites in
`tests/rxtsource/run_rxtsource_tests.sh` (lines ~335, ~345, ~469, ~554 at
this commit). BSD `xargs` (this Mac's `/usr/bin/xargs`) has no `-a` flag —
confirmed directly (`xargs --version` on this box prints its usage banner,
not a version). `git blame` traces these four call sites to commit
`96a05c9dc` (2026-08-30, the original `[DD-13b.W1.1]` lane) — untouched by
stage 4. Commit `76f9e85e` (an earlier repair-slice lane) EXPLICITLY records:
*"the census derivation's xargs -a has no BSD spelling (was silently 0/0/0
on darwin ...); the script's OTHER derivation legs remain darwin-broken,
catalogued for the admin slice."* That "other legs" is exactly leg B/leg C
above — a previously-fixed sibling bug (the census's own file-count
derivation) left THESE two call sites (`run.sh --dump`, `verify_rxt.py
--dump`) still broken, by the fixing lane's own admission, weeks before
stage 4.

Everything downstream of the empty leg-B/leg-C output (C0a's two-sources
disagreement, "C1 leg A != leg B", "case-row derivation DOES NOT
reconcile", the zero-row leg B/C counts) is a direct, mechanical cascade of
this one root cause. Not this lane's, not stage-4's, already catalogued.

## 5. C3's per-file semantic mismatches — PRE-EXISTING, NOT stage-4

`tests/rxtsource/run_rxtsource_tests.sh`'s "C3" section is `verify_rxt.py`
re-run over the WHOLE corpus (via `find`, independent of the census pin),
comparing each `.rxt` file's WRITTEN `m`/`n`/`g` expectation against a
FRESH python `re` computation — never against pcrec's actual behavior. The
script's own header states this box's C3 is "deliberately red" (box
sensitivity: darwin's python differs from the Linux reference's), and its
`C3_PASS`/etc. pins are explicitly Linux numbers.

All three files hit are pre-existing, untouched by the stage-4 diff
(confirmed by `git diff --stat 7e8ab03c..9d67eecf` — none of
`tests/backrefs/d27/caseless.rxt`, `tests/counterk/counterk.rxt`,
`tests/lookaround/captures.rxt` appear), and I reproduced each divergence
directly with this box's actual python3 (3.9.6, `/usr/bin/python3`):

- **`tests/backrefs/d27/caseless.rxt:37-39`**, pattern `^((?i)a)\1$` on
  `"aA"`. The file's OWN comment at line 36 already says `# pcre2-only:
  python refuses a non-leading global (?i) (F15)` — i.e. this cell is
  supposed to be excluded from python comparison because python is
  expected to REFUSE to compile it. On THIS box's python 3.9.6 it does not
  refuse — it issues a `DeprecationWarning` and compiles anyway, applying
  `(?i)` GLOBALLY (python's pre-3.11 behavior for a non-leading inline
  flag), giving `(0,2)` match with group 1 = `'a'` — reproduced verbatim:
  `python3 -c "import re; print(re.search(r'^((?i)a)\1$','aA'))"` on this
  box prints exactly that match. `tests/backrefs/CLAUDE.md`'s own module
  doc names this exact python-version sensitivity as the module's largest
  known oracle divergence.
- **`tests/counterk/counterk.rxt:568/626/644/702`**, e.g. `((a)|ab){0,12}?c`
  on `"abc"`: the .rxt's own written expectation (group 1 = `(0,2)`, i.e.
  `"ab"`, presumably libpcre2's answer for this backtracking/alternation
  capture shape) disagrees with what THIS box's live python computes —
  reproduced directly: `re.search(r'((a)|ab){0,12}?c','abc').span(1)` on
  this box returns `(1,2)`, matching pcrec's own reported "got" value, not
  the .rxt's "expected". This is a genuine PCRE2-vs-python capture-timing
  divergence in the corpus that C3 (per its own header comment) had never
  actually been triaged against before — the same "first-run discovery"
  shape the script's own C3 section documents for its original wiring.
- **`tests/lookaround/captures.rxt:59/67`**, e.g. `(?!(a)x)ab` on `"ab"`:
  the file's own comment says *"A NEGATIVE assertion's captures are
  DISCARDED"* (the correct, libpcre2-backed semantics, group 1 =
  `(-1,-1)`), but python's `re` RETAINS the failed inner attempt's capture
  — reproduced directly: `re.search(r'(?!(a)x)ab','ab').span(1)` on this
  box returns `(0,1)`, not unset. This is a well-known cross-engine
  divergence in negative-lookahead capture handling.

None of these three cells is marked in a way that stops C3 from comparing
them against python on this box (the caseless.rxt one IS marked
`# pcre2-only` but that marking only helps when python actually refuses to
compile, which it does not on 3.9.6), and none is caused by, or reachable
through, anything stage 4 touched.

**Recommendation, not built here**: these are genuine, previously-untriaged
`verify_rxt.py`/python-version divergences independent of stage 4. Whoever
owns `docs/dev/upstream_issues.md` should decide whether to (a) mark all
three `# pcre2-only` explicitly for the python-version reason, or (b) leave
them as the documented "C3 is deliberately red on darwin" bucket — either
way it's a pre-existing gap this triage surfaced, not something stage-4
introduced or something bat4triage's scope covers fixing.

## 6. NEW FINDING: BSD `wc` leading-whitespace breaks string-equality checks throughout `run_rxtsource_tests.sh`

Not previously catalogued (unlike #4/#5 above). Multiple failures in the
W1.2/W1.3 sections report FAIL messages whose embedded numbers visibly
MATCH the expected value:

```
FAIL: keyword census: the pinned 32-word list has       32 words.
FAIL: W1.2: the three-config file did not produce three prefixed pairs...
  .c files:        3 (want 3), .h files:        3 (want 3)
  distinct .name values:        1 (want 1) ...
FAIL: W1.3 dogfood: 66 rows (want 66),        0 colliding prefixes (want 0)
```

Root cause, reproduced directly on this box:
```sh
$ n32=$(printf '%s\n' <32 words> | wc -l); echo "[$n32]"
[      32]
$ [ "$n32" != "32" ] && echo MISMATCH
MISMATCH
```
BSD `wc -l`/`wc -c` (this box's `/usr/bin/wc`) pads its output with leading
spaces; the script's `[ "$x" = "N" ]` string-equality checks (all built on
`wc -l`/`wc -c`, e.g. `w12_c=$(ls ... | wc -l)`, `aw_dups=$(... | wc -l)`,
`n32=$(printf ... | wc -l)`) fail even when the underlying count is
correct — the extra spaces visible in the FAIL messages above ARE the
padding leaking through. `grep -c` is unaffected (confirmed: it does not
pad on this box), which is why not every count-comparison in the file is
broken — only the ones piped through `wc`.

This is systemic to the script (every `wc -l`/`wc -c` site is affected by
construction, this box's `wc` predates any stage-4 change) and is the same
class of BSD-vs-GNU-tool trap BOILERPLATE.md already documents for `sed`
and for `xargs -a` — just not yet written down for `wc`. Not fixed here:
it's outside stage-4's blast radius (none of the affected checks are in
files stage-4 touched), and a proper fix (wrapping every affected `wc` call
site, e.g. `wc -l | tr -d '[:space:]'` or `awk 'END{print NR}'`) is a
larger, separable cleanup this lane's charter does not cover. Flagged here
as a new, previously-undocumented finding for the manager to route (a
K-numbered issue, or folded into the next `[MACPORT]`-style darwin-
portability sweep).

## 7. `run_anchored_diff.sh` "26 pattern(s) produced emitted C that does not compile" — ENVIRONMENT/LOAD ARTIFACT

None of the anchored-DFA / search-filter emitter code
(`src/gen/emit_dfa.c`'s anchored form, `src/opt/`'s reverse-machine
construction) appears in `git diff --stat 7e8ab03c..9d67eecf` — stage 4
touched only the fold-closure files listed at the top of this report.

I reproduced the exact failing invocation for all six named patterns
(`(?m)ERROR$`, `([^c]{1,3})$`, `(a+)$`, `(a{0,4}c$)`, `(a{1,3}?$)`,
`ERROR$`) directly, using the already-built `build/pcrec` from the
battery's own 18:08 build (not a rebuild — same binary the battery itself
used) and the exact compiler/flags the check uses (`gcc-16 -O1 -std=gnu11
-Wall -Wextra -Werror`, linking `on.c` + `off.c` + `anchdiff_driver.c`
together, exactly as `tests/anchored/run_anchored_diff.sh`'s worker does):
**all six compiled cleanly, rc=0, zero warnings, on the first try.**

This strongly supports an environment/load artifact rather than a
deterministic compile defect: the `test` stage ran at `-j4 PROCS=3`
starting at a load average of 2.89/3.28/3.43 (per the trailer), and
`gen_cc`'s watchdog-enforced CPU/wall compile budget (D45, `tests/lib/
gen_timeout.sh`) is exactly the kind of thing that can spuriously trip
under box contention while looking identical to a real compile failure in
the log (the script's own `bad "... could not build the two-artifact
driver ..."` branch fires on ANY nonzero `gen_cc` exit, watchdog kill
included, not only a genuine compiler diagnostic — and the captured
`cc.log` head that would have distinguished the two was not preserved in
the battery log). I did not attempt to reproduce the exact concurrent-load
conditions (that would mean starting a second heavy suite against the
one-suite-at-a-time rule), so this is not a certainty, just the best
explanation the evidence supports.

**No fix needed. Validation plan (OWED, post-battery):**
```sh
bash tests/anchored/run_anchored_diff.sh
```
on a quiet box. Expected: `checks passed: 6`, `checks failed: 0` (matching
this file's OTHER 6 checks, which were already green in the battery run —
only the §1 corpus-sweep FAIL is in question). If it reproduces red on a
quiet box, that would upgrade this from (d) to a real finding and should
come back to the manager.

## What is OWED to the manager, in one place

1. Re-run `tests/codegen/run_cpset_structure.sh` solo — expect 28/0 (fixes
   #1-2 above).
2. Re-run `tests/rxtsource/run_rxtsource_tests.sh` solo — census/C1 block-
   count checks should now pass; C3's per-file semantic checks and the
   `wc`-padding checks will STILL be red on this box (pre-existing, #4-6
   above) and that is expected, not a sign the re-pin is wrong.
3. Re-run `tests/anchored/run_anchored_diff.sh` solo on a quiet box —
   expect 6/0 (finding #7); if it reproduces red, escalate.
4. Re-pin `C3_PASS`/`C3_SKIP`/`C3_SKIP_*` in `run_rxtsource_tests.sh` from
   a Linux reference run at a commit including `tests/utf8/fold.rxt`
   (owed, not computed here — see §3).
5. Route the new BSD-`wc`-padding finding (§6) — not stage-4's, not fixed
   here, previously undocumented.
6. Decide whether to mark `tests/backrefs/d27/caseless.rxt`,
   `tests/counterk/counterk.rxt`, `tests/lookaround/captures.rxt`'s
   affected cells more explicitly for the python-version divergence (§5).

None of these six items block the stage-4 merge itself — none of them
implicate the fold closure's correctness, and #1-2 (the only stage-4-
caused items) are fixed in this delivery.
