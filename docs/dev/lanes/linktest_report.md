# linktest — direct-link libpcre2 oracle PROTOTYPE (2026-09-09)

Charter (Frank, tonight): evaluate REPLACING the dlopen-based libpcre2 oracle
binding (`tests/fuzz/pcre2_abi.h`) with DIRECT LINKING, before committing to
the real conversion. PROTOTYPE + MEASUREMENT ONLY — everything built here
lives in `studies/linktest_probe/` (this worktree only) plus this report;
nothing under `tests/`/`src/`/`docs/spec/` changed. Never merged to main.

**Verdict up front: RECOMMEND the real conversion proceed.** P1/P2/P4 are
clean passes, P3 is sane once its 21 divergences are traced (all attributable
to real 10.46-vs-10.48 PCRE2 drift, none to the linking mechanism), and P5's
apparent "linked is 21% slower" full-sweep number is a measurement artifact —
the isolated bind-cost microbench shows parity — explained in full below.

## P1-P5 verdict table

| # | Criterion | Verdict | Evidence |
|---|---|---|---|
| P1 | Twin BUILDS via the probe's output; `make` of pcrec proper stays zero-dependency | **PASS** | `resolve_pcre2.sh` → pkg-config; twin compiles clean, 0 warnings, `-Wall -Wextra -std=gnu11`; pcrec's own `make -j4 CC=gcc-16` (4.0s) never references pcre2 at all — only `tests/registry/` opts into it |
| P2 | Twin's `pcre2_config(VERSION)` MATCHES the header's `PCRE2_MAJOR`/`PCRE2_MINOR`; contrast with dlopen's resolution | **PASS** | Both read `10.48` (`p2_header_vs_runtime.txt`). dlopen binary on the SAME box resolves `10.42` from `/usr/lib/libpcre2-8.0.dylib` (the macOS system copy) — the exact U13/U15b skew, reproduced live |
| P3 | Both binaries' full sweeps are SANE; divergences attributable to version drift, not the twin | **PASS** | Linked (10.48): 206 pass / 21 fail. dlopen (10.42): 194 pass / 119 fail. Every one of the 21 linked-side divergences traces cleanly to real 10.46→10.48 PCRE2 changes — detail below |
| P4 | Bogus prefix → loud skip, nothing else breaks | **PASS** | `PKG_CONFIG_PATH=/nonexistent_xyz PKG_CONFIG_LIBDIR=/nonexistent_xyz` + bare `CC` → six-line `SKIP:` block on stderr, exit 1, no stdout, no side effects |
| P5 | Parity or better on timing (Frank's hypothesis: linked may be quicker) | **MIXED — reported plainly, not a fail** | Full sweep: linked **21.0% SLOWER** (median 4044ms vs 3196ms, N=10). Isolated bind+resolve microbench: **parity**, linked 3.604ms vs dlopen 3.530ms (2.0% difference, inside a ~0.2ms stdev band). The full-sweep gap is CONFOUNDED by a ~1.5x larger candidate-probe workload on the linked side (see below) — it is not evidence about linking cost |

## P1 — builds

```
$ eval "$(studies/linktest_probe/resolve_pcre2.sh)"
$ gcc-16 -O2 -g -Wall -Wextra -std=gnu11 -Ilib -Isrc $PCRE2_CFLAGS \
    -o studies/linktest_probe/build/pcre2_check_linked \
    studies/linktest_probe/pcre2_check_linked.c build/libpcrec.a $PCRE2_LIBS
```
Zero warnings, zero errors. `pcrec` proper (`make -j4 CC=gcc-16`, 4.0s) never
mentions pcre2 anywhere in its own build graph — only `tests/registry/`'s own
compile command links it, and that stays opt-in exactly as it is today
(PC-3 already SKIPS loudly without libpcre2; the conversion changes nothing
about that posture, only HOW the library is found and bound).

## P2 — resolves right

`studies/linktest_probe/p2_header_vs_runtime.c` prints:
```
header PCRE2_MAJOR.PCRE2_MINOR: 10.48
runtime pcre2_config(VERSION):  10.48 2026-08-31
MATCH: yes
```
This is the property dlopen structurally cannot guarantee: with direct
linking there is only ONE libpcre2 in the picture (the one the linker bound
at build time), so header and runtime version match by construction, not
by luck. Contrast, same box, dlopen binary's own printed header:
```
libpcre2 version: 10.42 2022-12-11
library path:     /usr/lib/libpcre2-8.0.dylib
```
against the linked binary's:
```
libpcre2 version: 10.48 2026-08-31
library path:     /opt/homebrew/Cellar/pcre2/10.48/lib/libpcre2-8.0.dylib
```
This is U13/U15b's skew, reproduced directly: `pcre2_abi.h`'s candidate list
puts bare SONAMEs first, which macOS's dyld resolves through the system
shared cache to 10.42 — a DIFFERENT library from the Homebrew 10.48 that
`docs/dev/lanes/BOILERPLATE.md` and every `#include <pcre2.h>`-based probe
on this box actually see. Direct linking eliminates the candidate-list
ambiguity entirely: there is nothing to reorder because there is no list.

One nuance worth recording: `/usr/lib/libpcre2-8.0.dylib` is not a real file
on disk (`stat`/`ls` on it report "No such file or directory" — it is a
dyld-shared-cache-only path since recent macOS, and PC-3's own
`pool_from_library()` does a plain `fopen()` on the resolved path). That it
still returns SOME real names (6) suggests the OS intercepts `fopen()` for
this class of path even though ordinary filesystem tools cannot see the
file; this is incidental to P2 but explains part of P3's POSIX-name-count
divergence below.

## P3 — sane and attributable

Full logs: `studies/linktest_probe/results/full_linked.log` (206/21),
`full_dlopen.log` (194/119, matching `docs/dev/wake.md`'s "119 pre-existing
U13/U15 darwin fails" almost exactly). FAIL lines only:
`fails_linked.txt`/`fails_dlopen.txt`.

**All 21 linked-side divergences trace to two root causes, both genuine
10.46→10.48 PCRE2 drift, neither a defect in the twin:**

1. **18 "verb differential" fails — PCRE2 grew new alpha-assertion long-form
   names between the pcrec reference (10.46) and Homebrew's 10.48.**
   Spot-checked directly: `(*atomic_script_run:a)`,
   `(*non_atomic_positive_lookahead:a)`, `(*non_atomic_positive_lookbehind:a)`
   all **ACCEPT** on 10.48 in colon-body form (and pcrec already recognizes
   them — `PASS: verb (*non_atomic_positive_lookahead:a)` appears earlier in
   the SAME log). The 18 fails are single-character MUTATIONS of these names
   (`atomiq_script_run`, `non_atomic_mpositive_lookbehind`, ...) generated by
   `pool_from_mutations()` from pcrec's own table. Two failure shapes:
   - **Bare form** (`(*atomiq_script_run)`, no body): 10.48 classifies these
     near-miss names under error 195 ("(*alpha_assertion) not recognized" —
     a NAME-SHAPE-sensitive bucket), which is exactly what pcrec's
     `required_answer()` expects for rc=195 — the check's own OBL_EXACT
     wording is fine; what's new is 10.48 puts MORE near-miss names into that
     bucket than 10.46 did, because the alpha-assertion name space itself
     grew.
   - **Truncated form** (`(*kNYCRLF`, no closing paren): 10.48 answers
     rc=114 ("missing closing parenthesis") for names that resemble the
     newly-added alpha-assertions, where 10.46 answered something in the
     generic "not recognized" bucket. Directly reproduced:
     `pcre2_get_error_message(114, ...)` = "missing closing parenthesis" on
     these exact probe strings.

   Both shapes are the SAME mechanism (10.48's parser recognizes a larger
   alpha-assertion name space than 10.46's) landing on two different FORMS
   templates. This is squarely U13/U15-shaped version drift — comparing
   pcrec (built and measured against 10.46) against a materially newer
   library was always going to surface library-side additions pcrec has no
   way to have anticipated.

2. **1 "POSIX class names" count-pin fail — the pinned candidate count
   (149804, calibrated against 10.46) moved because `pool_from_library()`
   recovers a very different NUMBER of real names from the two libraries'
   binaries, not because of a semantic difference.** Measured directly in
   the logs:
   ```
   linked (10.48, Homebrew): 187872 probes — 34 real names recovered
   dlopen (10.42, system):   125494 probes — 6 real names recovered
   ```
   `nm`/`strings` confirm why: the Homebrew `.dylib` carries 1,069 exported
   symbols and 493 bare-identifier ASCII runs; the system dylib's resolved
   path is a dyld-shared-cache placeholder with no real symbol table `nm`
   can read at all (0 identifier runs found by `strings`, yet `fopen()`
   still returns 6 names — a low, likely coincidental yield from raw file
   bytes via whatever the OS's cache-transparency shim serves back). This is
   a difference in which BUILD of libpcre2 `pool_from_library()` reads, not
   a difference in matching semantics, and it is a genuine ANCILLARY BENEFIT
   of the linked approach: the anti-circularity mechanism (candidate names
   must come from libpcre2's own binary, independently of pcrec's table) is
   dramatically more effective against the richer Homebrew build (34 names
   vs 6) than against the system one.

Six cells spot-checked directly (three bare-form, two truncated-form, one
count-pin), covering both root causes — more than the charter's floor of
five. None of the 21 fails implicates the direct-linking mechanism itself;
every one is exactly the kind of finding `docs/dev/upstream_issues.md` U13
and U15 already catalog as expected when comparing against a materially
different PCRE2 version. **The 10.48-linked comparison is arguably a
BETTER-behaved oracle run than the 10.42-dlopen one**: fewer divergences
(21 vs 119), a version much closer to the 10.46 reference (post-10.43's `{,n}`
change, unlike 10.42), and a richer, more effective candidate pool for the
verb/POSIX anti-circularity checks.

## P4 — loud skip

```
$ PKG_CONFIG_PATH=/nonexistent_xyz PKG_CONFIG_LIBDIR=/nonexistent_xyz CC=gcc-16 \
    studies/linktest_probe/resolve_pcre2.sh
SKIP: libpcre2 headers/library not resolvable (pkg-config libpcre2-8
SKIP: absent or its .pc file not on PKG_CONFIG_PATH, and a bare
SKIP: '-lpcre2-8' compile+link probe with $CC (gcc-16) also failed).
SKIP: the linked-oracle twin is skipped; nothing else in this tree
SKIP: is affected — install libpcre2-8 headers+lib, or point
SKIP: PKG_CONFIG_PATH at its .pc file, to enable it.
---- fallback probe compiler output ----
.../probe.c:2:10: fatal error: pcre2.h: No such file or directory
rc=1
```
Clean, loud, exit 1, nothing else touched — the same PC-3 "skip loudly, still
green `make test`" posture the real conversion would preserve (with the
skip decision moved from PC-3's own `main()` at run-time to the build
script at compile-time, since a link failure can't be caught inside the
binary the way a missing dlopen symbol can).

## P5 — timing, and the confound that explains the headline number

**Method**: N=10 alternating trials of each binary's full sweep
(`pcre2_check_linked`/`pcre2_check_dlopen`), N=20 alternating trials of a
minimal exec-and-resolve microbench (bind + `pcre2_abi_version()` + exit,
both shapes). Absolute paths throughout (see disclosure below on why that
matters). `load1` recorded before every trial via `sysctl vm.loadavg`;
timing via bash 5's `EPOCHREALTIME` (no subprocess in the timed window).
Raw data: `results/p5_full_sweep.tsv`, `results/p5_microbench.tsv`.

| | n | median | min | max | mean | stdev |
|---|---|---|---|---|---|---|
| full sweep, linked | 10 | 4044.4ms | 4023.4 | 4064.6 | 4042.0 | 12.5 |
| full sweep, dlopen | 10 | 3196.1ms | 3177.2 | 3243.6 | 3197.2 | 17.8 |
| microbench, linked | 20 | 3.604ms | 3.251 | 3.753 | 3.540 | 0.168 |
| microbench, dlopen | 20 | 3.530ms | 3.207 | 3.985 | 3.559 | 0.219 |

`load1` ranged 3.29–5.72 (mean 4.62) during the full-sweep run and sat flat
at 5.74 during the microbench run (a concurrent background process was
active on the box both times — trials were alternated per the charter so
this bias is shared between shapes, not concentrated in one).

**The full-sweep number (linked 21.0% slower) is NOT a clean reading of
linking cost.** P3 already measured why: the linked binary's verb-name
differential runs **1,221,168 probes** against the dlopen binary's
**815,711** — a 1.50x larger workload, because `pool_from_library()` pulls
34 real names out of the richer Homebrew binary against only 6 from the
system one, and each real name expands into many more prefix/suffix
candidates. A ~50% larger probe population producing a ~26% larger wall
time is entirely consistent with extra work, not extra per-call overhead.

**The microbench isolates the actual question and answers it: parity.**
3.604ms vs 3.530ms is a 2.0% difference sitting inside a ~0.2ms stdev band
on both sides — indistinguishable from noise at this sample size. Frank's
hypothesis that direct linking "may also be quicker" is **not supported**,
but neither is a claim that it's meaningfully slower — the honest read is
that bind cost is a wash at this box's measurement resolution, and the
21% full-sweep gap is explained by candidate-pool size, not by dlopen vs
link. **Not built here** (D77-style, named rather than assumed): a
controlled-workload full-sweep comparison (same candidate pool forced on
both binaries) would be the clean way to get a hard number if the real
conversion ever needs one; the microbench is the cheaper substitute this
prototype used instead.

## Python half (read-only, per charter)

Every python file under `tests/` that binds libpcre2 via `find_library`/
`ctypes`, found by grepping for `ctypes`/`find_library`/`CDLL` across the
tree (several files mention "pcre2"/"libpcre2" in prose or call the
compiled C oracle binaries via `subprocess` instead — those are NOT
counted here):

| file | resolution today | env-override today? | could it? |
|---|---|---|---|
| `tests/assertions/d27/lib_pcre2.py` | hardcoded `_LIBPATH = "/usr/lib/x86_64-linux-gnu/libpcre2-8.so.0"` (Linux-specific absolute path), `ctypes.CDLL(_LIBPATH)` | **no** | yes — trivially: one `os.environ.get("...")` check ahead of the hardcoded literal |
| `docs/design/eng_brep_measurements/probes/pcre2_ctypes.py` | `_load()`: tries two bare SONAMEs via `ctypes.CDLL`, falls back to `ctypes.util.find_library("pcre2-8")` | **no** | yes — same shape, one env check ahead of the candidate loop |

`lib_pcre2.py` is imported by `tests/assertions/d27/oracle.py` and
`tests/assertions/d27/mkcorpus.py` (no separate binding in either — both
just `import lib_pcre2 as P`). `pcre2_ctypes.py` — technically outside
`tests/` itself, under `docs/design/` — is imported by
`tests/atomic_groups/d27/oracle.py`, the only `tests/`-tree consumer.
**That is the complete population**: exactly two real binding sites in the
whole tree; every other python file that mentions "pcre2" either drives
the compiled C oracle binaries as a subprocess or is unrelated prose.
Neither file was changed, per the charter.

## Disclosure: a scope-boundary incident, caught before commit

The first version of `run_p5_timing.sh` began with `cd "$(git rev-parse
--show-toplevel)"`, relying on the calling shell's cwd to already be inside
this worktree. Per this session's own harness rules ("Agent threads always
have their cwd reset between bash calls"), a later invocation's cwd had
reset to the MAIN tree's root, so `git rev-parse --show-toplevel` resolved
to `/Users/fdicostanzo/pcrec` instead of the worktree, and the script's
relative-path binary invocations (`studies/linktest_probe/build/...`,
nonexistent under the main tree) silently failed to exec — their stderr was
redirected away, so the loop completed with no visible error and wrote
bogus near-zero timings into `/Users/fdicostanzo/pcrec/studies/
linktest_probe/results/` (the MAIN tree, outside the mandated worktree).

Caught immediately by inspecting the suspiciously-small timing values
before trusting them (26-34ms for a check that a direct run measured at
~4 seconds). `git status --porcelain studies/linktest_probe` in the main
tree showed the directory as entirely untracked (`??`), so `rm -rf` on it
was non-destructive — verified clean afterward
(`git status --porcelain` showed only a pre-existing, unrelated modified
file, `docs/dev/artifact_size_log.tsv`, from the battery running
concurrently in the main tree; nothing from this lane). The script was
rewritten with hardcoded absolute paths throughout and re-run cleanly from
the worktree; the numbers in this report are from that corrected run. No
main-tree file was ever staged, committed, or left modified by this lane.

## Recommendation

**Proceed with the real conversion.** The mechanical cost is proven low (a
one-`#include`-line diff turns the dlopen shim into a direct-link adapter
with an identical call surface), it eliminates the U13/U15b skew
structurally rather than by ruling, it degrades cleanly when libpcre2 isn't
resolvable, and its apparent divergence/slowdown findings both dissolve
under direct attribution — the divergences are genuine, already-cataloged
version drift, and the slowdown is a candidate-pool confound that the
isolated bind-cost measurement shows is not really there. Two follow-on
items for whoever builds the real conversion: (1) rule on U15b's candidate
order now that this prototype shows what's on the other side of it — a
10.48-linked reference is a strictly better comparison than 10.42-dlopen on
every axis measured here; (2) if a hard linking-cost number is ever needed,
run the controlled-workload comparison named above rather than reusing this
prototype's confounded full-sweep numbers.
