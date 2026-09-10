# battery 20260910_115427 `test`-stage TRIAGE (lane btriage2)

Triage of the RED `test` stage from `/Users/fdicostanzo/pcrec/build/battery_20260910_115427/test.log`
(shape `make -k -j4 PROCS=3 test`, battery over commit 6edf8920). The
battery validates four merges: [K53-SELRETRY], the oracle-interface design
doc, [TT-4M] axes-batch (HARNESS_BATCH, unset/byte-identical on the `test`
stage), and arm61fix.

**Bottom line: every failure traces to ONE of three causes, and NONE of
them is a real correctness regression from today's four merges.**

1. **Six distinct pre-existing darwin/BSD-tool portability bugs**, three of
   them a known class (`docs/dev/lanes/macport_report.md` §8, this
   project's `wc -l < file` right-justify-pads-with-leading-spaces
   finding) recurring at sites that fix missed, and three new-to-this-
   triage instances of the same "this box's coreutils/sed/grep aren't
   GNU's" family the tree already has a standing TRAPS table for
   (`tests/codegen/CLAUDE.md`). All six are **FIXED in this lane**
   (commits below), verified against a fresh worktree build.
2. **One 7th oracle-build site the [ORACLE-LINK]/D98 direct-link
   conversion (and lane mechtri2's own six-site follow-up sweep) both
   missed** — `tests/assertions/verify_pcre2.py`'s `build_oracle()` still
   carried the pre-retirement `-ldl` dlopen-shim command line. **FIXED**
   in this lane, same shape as the six sites mechtri2 already fixed.
3. **Genuine environment/toolchain facts that are not fixable by editing a
   test script**: a gcc-16-on-macOS-ARM64 crash under `RLIMIT_CPU`
   (reproduced standalone, outside the harness entirely), a darwin
   thread-stack platform-behavior question (K33's whole framing assumes
   musl/Linux stack semantics), and a message-truncation effect driven by
   macOS's much longer default `TMPDIR`. All three are **left unfixed and
   flagged** for a deliberate ruling — the first two because there is no
   test-script fix that addresses a compiler crash or a real platform
   difference, the third because its own check message already names the
   correct remedy (shorten pcrec's own diagnostic text) and that is a
   `src/` change outside a triage lane's charter.

Also confirmed as the exact chartered, already-known non-regression named
in the brief: `run_inline_capability.sh` (Mach-O leading-underscore vs the
CC-DIFF probe's ELF greps — belongs to [CC-DIFF], not this battery).

## Section-by-section disposition

### test-gentimeout — INFRASTRUCTURE, not fixed, flagged

`FAIL: gen-timeout: CPU control fired (rc=139) but the diagnostic is
wrong: gcc-16: internal compiler error: Cputime limit exceeded: 24 signal
terminated program cc1` / `environment: line 1: ... Segmentation fault: 11`.

**Reproduced standalone, with no pcrec harness involved at all**:

```
$ ( ulimit -t 1; timeout 30 gcc-16 -O2 -std=gnu11 -c -o /dev/null gen.c )
gcc-16: internal compiler error: Cputime limit exceeded: 24 signal terminated program cc1
Segmentation fault: 11
$ echo $?
139
```

gcc-16 (Homebrew, ARM64) segfaults in its own SIGXCPU crash-reporting path
on this box, rather than exiting cleanly with the ICE text D45's own design
(`docs/dev/decisions.md`, the D45 third/fourth addenda) anticipated ("gcc:
internal compiler error: CPU time limit exceeded signal terminated program
cc1", the shape recorded at `docs/dev/artifact_size_census.md:540` and
`docs/dev/dev_journal.md:8759`). `gen_cc`'s wrapper diagnostic text never
gets appended because the compiler process itself dies by SIGSEGV instead
of returning normally. No file under today's four merges touches
`tests/lib/gen_timeout.sh` or this test file (`git log` confirms the last
touch is `59cc8af3`, the Mac move's own [MACPORT] commit). **Not fixed**:
there is no test-script edit that stops a compiler from crashing on a
resource-limit signal. Flagged for the manager — worth a minimal upstream
report to Homebrew/GCC, or an accepted-failure-mode note in the check
itself if this gcc-16 build is expected to keep doing this.

### test-codegen (`run_inline_capability.sh`) — KNOWN NON-REGRESSION

Confirmed exactly as chartered in the brief: `run_group` reports "7/8
scripts passed", the one failure is `run_inline_capability.sh`'s `nm`
probe (`FAIL: nm could not read arm_a.o (no rx_search symbol)`), and every
other script in the group (including `run_vm_frameless.sh`,
`run_dfa_uniform_fold.sh`, `run_trie_identity.sh`, `run_scan_edge_census.sh`,
`run_n1_budget.sh`) is fully green. Mach-O leading-underscore symbols vs a
probe written against ELF `nm` output; the [CC-DIFF] STEP 2 probe has never
run on darwin (`docs/dev/lanes/utf8k53_report.md` already names this root
cause). Not this battery's to fix.

### test-vm (`run_ir_listing.sh`) — FIXED

`FAIL`s: "the listing shows a label more than once" (all 9 corpus
witnesses, every run) and "the cap counts N resume points but the artifact
emits N — being checked against the wrong number" (also every witness,
**even when the two printed numbers were textually identical**, e.g. "0"
vs "0").

Root cause: two unguarded `wc -l` sites (`c_rp`, and `cdup`/`idup` via
`uniq -d | wc -l`) compared with bash `[ = ]`/`[ != ]` against unpadded
values from `grep`. BSD `wc -l` right-justifies its count with leading
spaces even through a pipe or `<` redirection — confirmed directly:
`echo -e "a\nb\nc" | wc -l` prints `"       3"`, not `"3"`. Every
comparison against a padded `"0"`/count therefore failed regardless of the
actual duplicate/resume-point state. This is the SAME class
`docs/dev/lanes/macport_report.md` §8 already named and partially swept
(`tests/registry/run_definitions_oracle.sh` was fixed 2026-09-04); this
file's own two sites were missed by that sweep.

Fixed with `| tr -d ' '` at both sites. Reproduced clean against a fresh
worktree build: **82 passed / 0 failed** (was 60/22).

Commit: `82af94b8`.

### test-prefilter (`run_prefilter_tests.sh`) — FIXED

`FAIL: functional sanity: forced-on gave 'cc-fail', forced-off gave
'cc-fail'; expected both '1,3 1,2'`.

Root cause: `sed -i "s/.../.../ " "$d/gen.c"` with no backup-suffix
argument. BSD `sed -i` REQUIRES a suffix argument (even an empty one);
given none, it consumes the next shell argument as the suffix and fails
outright — confirmed directly (`sed -i "s/.../.../ " file` exits 1 with
`undefined label '.c'`, file untouched). The `#include` rewrite from the
per-target filename to `"gen.h"` never landed, so both compiles referenced
a nonexistent header and `gen_cc` failed for both arms, giving the
identical `"cc-fail"` string the check reported.
`tests/mrl/run_mrl_tests.sh` already has the byte-identical rewrite using
the portable `sed -i.bak ... && rm -f *.bak` form; copied verbatim.

Fixed. Reproduced clean: **32 passed / 0 failed** (was 31/1), including
the named functional-sanity check.

**Related, NOT fixed** (out of the battery's failing set):
`tests/possessify/run_possessify_tests.sh:292`'s boundary-ceiling check has
the identical bare `sed -i` shape, but its `gen_cc` failure there is
folded into a `bnd_ok=0` flag that SKIPS the subsequent read rather than
failing loudly — a vacuous-pass risk of the same class, flagged for the
manager rather than fixed here since it isn't in today's failing set.

Commit: `27d9a1cc`.

### test-assertions (`verify_pcre2.py` via `run_assertions_tests.sh`) — FIXED

`FAIL: libpcre2 oracle: tests/assertions/ cells disagree with libpcre2`,
root: `verify_pcre2: could not build the oracle: ... fatal error: pcre2.h:
No such file or directory`.

`tests/assertions/verify_pcre2.py`'s `build_oracle()` was a **7th oracle
build site [ORACLE-LINK]/D98 (the dlopen-shim retirement, commit
`48917742`/`d871978c`) and lane mechtri2's own six-site follow-up sweep
(`c9ddb933`) both missed**. It still compiled `tests/fuzz/pcre2_oracle.c`
with the pre-retirement `-ldl` command line — no `-I` for `pcre2.h`, no
`-lpcre2-8`, and no `$PCRE2_AVAILABLE` skip check — even though
`pcre2_abi.h` now `#include`s the real header unconditionally.
mechtri2's own list (atomic_diff, gstart/kreset/mline diffs, the matrix's
pc3/pc4 arms) does not include this file; this is a distinct, previously
unfound gap in the same conversion.

Fixed identically to the six already-converted sites: read
`PCRE2_AVAILABLE`/`PCRE2_CFLAGS`/`PCRE2_LIBS` from the environment
(exported by `tests/lib/resolve_pcre2.sh`, already sourced by
`run_assertions_tests.sh` before it calls this script) instead of a
hardcoded `-ldl`. Reproduced clean: `verify_pcre2.py` standalone now
reports 849/849 cells agreeing with libpcre2 10.48; the full
`run_assertions_tests.sh` section is **54 passed / 0 failed, exit 0**
(was 53/1).

Pre-existing (predates today's four merges — confirmed `013e5e03`,
mechtri2's own merge, is already an ancestor of `fb62d844`, the first of
today's four).

Commit: `d9329395`.

### test-stackdepth (`run_stackdepth_tests.sh`) — DARWIN PLATFORM QUESTION, not fixed, flagged

`FAIL: [TS-4] arm A did NOT die (exit 0, 'default rc=1 n=342 stack=131072').
K33 is pinned as a LIVE defect here and in docs/dev/known_issues.md; ...
A pass HERE would be a further narrowing ... and needs its own
measurement, not an edit to this line`.

The check's own comment already anticipates and names exactly this
situation, and its instruction is explicit: do not silently absorb it.
K33 (`docs/dev/known_issues.md`) is framed entirely in terms of a **musl
default 128 KB thread stack** ("a call-bearing VM artifact's default
entries SIGSEGV on a musl-default 128 KB thread stack") — a Linux/musl
libc-specific fact about stack-overflow guard-page behavior. On this run,
the SAME artifact (measured 134384 B deep-path frame vs a 131072 B thread
stack, over budget by 3312 B) ran to completion (`exit 0`) instead of
crashing. macOS's own pthread stack-allocation/guard-page mechanics are
not musl's, and this is very likely the first time this specific check has
actually executed on darwin: the journal's last "stackdepth pinned" record
(`docs/dev/dev_journal.md:15094`) is dated 2026-08-25, ten days before the
2026-09-04 Mac move, and nothing in the journal or in `docs/dev/lanes/
macport_report.md` (which did darwin-port `watchdog`/`safekill` and four
`tests/lib` shims) records re-verifying this check post-move — the same
"never actually ran here before" shape `santriage_report.md` found for
`san`/`lint`. Every commit touching `tests/thread/` predates today's four
merges.

**Not fixed**: this is a genuine platform-behavior question the check's
own author explicitly reserved for deliberate handling, not a bug a test
edit resolves. Flagged for a ruling — either K33's own framing needs a
darwin clause, or this arm needs a darwin-aware exemption analogous to
the TSan `SKIP` immediately above it in the same file.

### test-capturediff (`run_capturediff_gate.sh`) — FIXED

Every one of the gate's 19 pinned-count label extractions read back
`MISSING` ("label vanished from fuzz.py's summary"), so the gate failed
regardless of the underlying fuzz run's actual result.

Root cause: `grep -ioP "${label}[^:]*:\s*\K[0-9]+"` — BSD grep has no `-P`
(Perl regex, needed here for `\s` and the `\K` lookbehind) and errors
outright (`grep: invalid option -- P`) rather than degrading. Rewritten in
portable ERE (`grep -E`, no lookbehind): capture the whole `"label...:
NNN"` match first, then pull the trailing digits off that match with a
second `grep -oE '[0-9]+$'` — identical semantics to the original `\K`
(only the number immediately after THIS label's own colon, never an
earlier digit in a parenthetical), no BSD/GNU grep divergence either box.

Reproduced clean: **PASS** (seed=1, patterns=300, subjects=15) — 2745
subject pairs compared, 0 content divergences, 0 accept/reject
divergences, every one of the 19 pinned counts matching exactly.

Pre-existing (script dates to 2026-08-17).

Commit: `976a7f50`.

### test-rxtsource (`run_rxtsource_tests.sh`) — MOSTLY FIXED, 3 residuals

**106 passed / 14 failed → 115 passed / 3 failed.**

Eleven of the fourteen original failures were ONE root cause cascading:
six unfixed `xargs -a` sites (BSD xargs has no `-a` spelling — the exact
class this file's own line-130 comment already documents was fixed
*elsewhere* in this same script and in `run_mrl_tests.sh` on 2026-09-05,
but six more sites here were missed) plus six more unguarded `wc -l`
padding sites in the same "macport_report.md §8" class as the test-vm fix
above. Fixed by switching every `xargs -a "$FILES" CMD` to the portable
`xargs CMD < "$FILES"` form the file's own census derivation (line 271)
already used, and piping every remaining unguarded `wc -l`/`wc -c` count
used in a string comparison through `tr -d ' '`.

This single fix resolved: C0a (both sides were genuinely 0, but one side's
"0" was padded), C1's leg A vs B/C diff (legs B/C were reading back
completely empty because their `xargs -a` calls errored before invoking
anything), the case-row derivation (0+0+0 for the same reason), the file
list count, the keyword census's self-check on its own 32-word list length,
the W1.2 three-config compile's `.c`/`.h`/`.name` counts (whose FAIL
message showed VISUALLY MATCHING numbers — `3 (want 3)`, `1 (want 1)` —
because the padding was invisible in the printed text but broke the `[ = ]`
underneath), and the W1.3 altwide dogfood's row/collision counts.

Commit: `fb1b9c5e` (full before/after evidence and every site listed
in the commit message).

**Three residuals, NOT fixed, each with a distinct disposition:**

1. **`FAIL: C3: verify_rxt.py reported failures`** — `caseless.rxt` (1),
   `counterk.rxt` (4), `captures.rxt` (2). This is `docs/dev/lanes/
   bat4triage_report.md`'s **already-documented** finding, verbatim: "three
   genuine python-3.9.6-vs-reference divergences in untouched corpus files
   (caseless.rxt/counterk.rxt/captures.rxt, each reproduced with this box's
   own python3)" — from the *previous* battery's own triage, 2026-09-08.
   The check's own message is candid about why: "this oracle was previously
   invoked by nothing, and its default covered 40 of 210 files. Its first
   run over the rest is a DISCOVERY of expectations that were never
   oracle-checked, not a regression this change caused." A genuine
   python-version oracle divergence, pre-existing, needing a ruling
   (mark `# pcre2-only` / re-verify against the pinned python / accept as
   a new tracked upstream_issues.md entry), not a test-portability bug.

2 & 3. **`FAIL: W1.2: a resolution refusal is TRUNCATED`** (263/263/268
   bytes against a 263-byte check threshold) and **`FAIL: W1.3 refusal
   (one definition name declared in two files...): missing:
   [compose_dup_definition.rxt]`** (the message is cut off exactly before
   the `.rxt` extension of the second path) are **the SAME underlying
   cause**: `pcrec_error.msg` is a fixed 256-byte buffer, these two checks'
   fixture messages embed one or two full scratch-directory file paths, and
   macOS's default `TMPDIR` (`/var/folders/<hash>/T/`, measured **49
   bytes**) is 43 bytes longer than Linux's `/tmp/` (**6 bytes**). Verified
   directly with the identical fixture and binary: the SAME `--source
   no_such_definition.rxt -o trunc.c` refusal is **263 bytes** under the
   real macOS `$TMPDIR` and **231 bytes** under a forced short `/tmp/short`
   — a 32-byte difference tracking the TMPDIR-length delta exactly. Not a
   regression: it is `pcrec_error.msg`'s pre-existing fixed-size budget
   colliding with an environment fact (macOS's much longer default scratch
   path) that a Linux box never exercises. The check's own failure message
   already names the correct remedy — "Shorten the message; do not raise
   the buffer" — which is a `src/` change to the refusal text's own prose,
   outside a test-portability triage lane's scope. Flagged for the manager;
   would very likely reproduce on any darwin box using the system default
   `TMPDIR`.

### All other sections in the log

Everything else in `test.log` that is not enumerated above ran green,
including the full `test-codegen`/`test-vm` run_groups apart from the two
items already named, `test-anchored-match`, `test-search-pinned`,
`test-uprops`, `test-recursion`, `test-known-fail` (the K34 ratchet, 1
still-failing/expected, 0 now-passing — correct), `test-thread`'s
stackdepth-adjacent TSan section (`SKIP: gcc-16 does not support
-fsanitize=thread on this box`, a pre-existing, already-understood darwin
gap, not a FAIL), and `test-definitions`.

## Delivery

Branch `lane/btriage2`, five commits, each independently verified against
a fresh `make -j4 CC=gcc-16` build of this worktree (not the battery's own
binary — the battery is still running and the box-concurrency rule
forbids touching it):

| commit | file | before → after |
|---|---|---|
| `d9329395` | `tests/assertions/verify_pcre2.py` | oracle build failed → 849/849 cells agree, exit 0 |
| `82af94b8` | `tests/codegen/run_ir_listing.sh` | 60/22 → 82/0 |
| `27d9a1cc` | `tests/prefilter/run_prefilter_tests.sh` | 31/1 → 32/0 |
| `976a7f50` | `tests/fuzz/run_capturediff_gate.sh` | FAIL (all 19 labels MISSING) → PASS, every count exact |
| `fb1b9c5e` | `tests/rxtsource/run_rxtsource_tests.sh` | 106/14 → 115/3 (3 residuals flagged above, not fixable by a test-script edit) |

One process note: my first attempt at the `verify_pcre2.py` fix
accidentally edited the MAIN TREE copy (missing `worktrees/btriage2/` in
the file path) rather than the worktree's. Caught before any commit —
`git diff` showed the single stray hunk, `git checkout --
tests/assertions/verify_pcre2.py` reverted it cleanly in the main tree
(confirmed clean via `git status`), and the identical edit was then
redone correctly in the worktree. No main-tree commit or scope violation
occurred; noted here per this project's convention of recording such
incidents rather than treating a caught-in-time mistake as unremarkable.

## Re-validation owed post-battery

The manager's full battery is the merge/close standard; this lane's own
verification used the worktree's own build, not the battery's. Post-battery,
re-run (from the merged main, after these five commits land):

- `make test-vm`, `make test-prefilter`, `make test-assertions`,
  `make test-capturediff`, `make test-rxtsource` — expect all green except
  test-rxtsource's C3 arm (3 pre-existing oracle divergences, a ruling
  owed, not a re-validation) and test-codegen's known `run_inline_capability.sh`
  non-regression.
- `test-gentimeout`, `test-stackdepth` — expected to reproduce their
  respective findings above (gcc-16 CPU-limit crash; K33's darwin
  behavior) until a deliberate ruling changes either check or the
  environment. Re-run only to confirm they still reproduce identically
  (a *different* symptom on re-run would itself be a finding).
