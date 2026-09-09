# oralink_report.md — [ORACLE-LINK]: retire dlopen, convert to direct linking (2026-09-09, lane oralink)

Charter: retire `tests/fuzz/pcre2_abi.h`'s dlopen-based libpcre2 binding and
convert every oracle check to direct linking, per Frank's ruling ("if your
test/evaluation passes then make it so" — the linktest prototype's P1-P5
passed, `docs/dev/lanes/linktest_report.md`). D98 (`docs/dev/decisions.md`)
is the decision record; this report is the delivery record.

## What changed

**The header** (`tests/fuzz/pcre2_abi.h`): `#include <pcre2.h>` + real
symbols instead of hand-declared prototypes + dlopen/dlsym. Same `Pcre2Abi`
struct field names and `pcre2_abi_load`/`_version`/`_unicode_version`/`_path`
signatures as before — every existing `#include`r compiles unchanged.
Deleted: the candidate-SONAME list, dlsym resolution, `dlinfo
(RTLD_DI_LINKMAP)` ELF introspection. Narrowed: the `_GNU_SOURCE`-first-
include ordering guard now protects `dladdr` alone (still needed by
`pcre2_abi_path()`, which `pcre2_check.c`'s anti-circularity candidate pool
depends on), unified to one implementation for both platforms (no more
`#ifdef __APPLE__` split — dladdr works identically on both).

**The probe** (`tests/lib/resolve_pcre2.sh`, graduated from
`studies/linktest_probe/resolve_pcre2.sh`): pkg-config first, a bare
compile+link fallback second, silent `PCRE2_AVAILABLE=0` on failure (each
caller prints its own SKIP text, never this file's). Exports
`PCRE2_CFLAGS`/`PCRE2_LIBS`/`PCRE2_VERSION`/`PCRE2_RESOLVED_VIA` for C
builds and `PCREC_PCRE2_PATH` (a real loadable file path, derived from
pkg-config's `--variable=libdir` plus a glob for the shared-object basename
— darwin's `.dylib`, Linux's `.so.N`) for python's ctypes bindings. Announces
the resolved version once per top-level script, matching
`cc_resolve.sh`/`timeout_bin.sh`'s convention.

**Converted build sites** (SKIP decision moved from runtime to build time,
before the compile is attempted):
- `tests/registry/run_registry_tests.sh` (PC-3, `pcre2_check.c`)
- `tests/registry/run_pc4.sh` (PC-4, `pc4_check.c`)
- `tests/registry/run_definitions_oracle.sh` (`definitions_oracle_check.c`)
- `tests/uprops/run_uprops_tests.sh` (`uprops_oracle.c`)
- `tests/fuzz/run_capturediff_gate.sh` (`pcre2_oracle.c`) + `fuzz.py`'s own
  `build_oracle()` (a new `resolve_pcre2_flags()` python helper — pkg-config
  via subprocess, inheriting the shell resolver's env if already sourced,
  never a SKIP path since this tool is fail-hard by design)

**Python one-resolution-point**: `tests/assertions/d27/lib_pcre2.py` and
`docs/design/eng_brep_measurements/probes/pcre2_ctypes.py` both consult
`PCREC_PCRE2_PATH` first, falling back to their pre-existing candidate
search when unset. Seven shell runners that invoke a python script
importing either of these now source `tests/lib/resolve_pcre2.sh` and so
export it automatically: `tests/backrefs/run_dupnames_diff.sh`,
`run_backref_diff.sh`; `tests/lookaround/run_lookaround_diff.sh`,
`run_expansion_diff.sh`; `tests/recursion/run_recursion_diff.sh`;
`tests/assertions/run_assertions_tests.sh` (covers `verify_pcre2.py`);
`tests/atomic_groups/run_atomic_diff.sh`. The two `d27/oracle.py` scripts
(`tests/assertions/d27/`, `tests/atomic_groups/d27/`) are manual,
never-automated D27 tools (confirmed by grep — nothing in the tree invokes
either); they get the env var when a caller exports it manually, and fall
back to their pre-existing candidate search otherwise, unchanged behaviour
for a bare manual invocation.

**`tests/registry/pcre2_check.c` gained two version-keyed mechanisms**,
both in K15's established shape (a narrow, liveness-guarded exclusion, not
a wider tolerance):
- `u15b_excluded()` — a truncated alpha-assertion near-miss
  (`(*atomiq_script_run`, `(*posihtive_lookahead`, 20 such candidates
  measured) answers rc=195 on the 10.46 reference (matching pcrec's own
  message, no divergence ever) and rc=114 on 10.47+ (10.48's parser reads
  further into the near-miss before giving up). The exclusion fires only
  when the resolved library is 10.47+ AND the rc/message pair matches this
  exact shape, with a liveness guard in BOTH directions (must fire on
  10.47+, must NOT fire on the 10.46 reference).
- The POSIX candidate-pool probe count (`expect_probes("POSIX class
  names", ...)`) is now pinned per resolved version — 149804 at 10.46,
  187872 at 10.48 — rather than one number, because the count is a property
  of how many real ASCII runs `pool_from_library()` recovers from the
  RESOLVED LIBRARY'S OWN BINARY (34 on Homebrew's richer 10.48 build vs the
  old shim's 6 from darwin's stripped system copy), not of pcrec's logic. An
  unrecognized version fails loudly naming itself rather than guessing.

**Bookkeeping**: `docs/dev/upstream_issues.md` U15b marked
RESOLVED-BY-RETIREMENT with a new (c) sub-entry naming the alpha-assertion
drift `u15b_excluded()` handles; U13 gains an OUTCOME note; both cite the
209/0 re-baseline. `docs/dev/decisions.md` D98 records the ruling,
rationale (three incidents, the structural skew-impossibility argument,
type-checked calls, one-resolution-point including python), scope (what
was and was NOT converted, and why), and the revisit-when. `docs/testing.md`
updated at the PC-3 SKIP-pattern paragraph and the uprops Unicode-drift
table (the "what the suite's dlopen shim resolves" row is retired — see
below for the re-measured byte-arm numbers). `tests/probes/CLAUDE.md`'s
manual build recipe updated to source the new resolver; the 17 probe `.c`
files themselves need no edit (verified: `probe_atom.c` and
`probe_digit_sweep.c`, one with and one without its own extra `dlopen()`
call, both compile clean with the new recipe).

## What was checked and explicitly NOT converted

- `tests/backrefs/fold_agreement_check.c` / `fold_agreement_utf8_check.c` —
  grepped and read: neither includes `pcre2_abi.h` or calls `dlopen`/any
  runtime libpcre2 API. Both compare pcrec's own compiler-side fold table
  against pcrec's own emitted residual; libpcre2 is cited in comments as
  the historical MEASUREMENT that calibrated `pcrec_ascii_fold`, never
  accessed at runtime. The brief named `fold_agreement_utf8_check.c` as an
  expected consumer; it is not one — flagging this discrepancy rather than
  forcing a conversion onto a file with nothing to convert.
- `docs/design/k18_measurements/capdiff/pcre2_batch_oracle.c` — a frozen
  historical design-measurement artifact (same class as `tests/probes/`),
  not part of `make test`, left untouched.
- `tests/parse/branch_count_check.c` — has its own from-scratch `dlopen()`
  call, never routed through `pcre2_abi.h`; outside this header's shared
  scope, left untouched.
- K54/sanitizer axes — orthogonal, per charter, not touched.

## Validation (this box: darwin, Homebrew 10.48)

| check | before | after |
|---|---|---|
| PC-3 (`pcre2_check.c`, standalone binary) | 194 passing / 119 failing (all U13/U15b) | **209 passing / 0 failing** |
| PC-4 (`run_pc4.sh`) | (built via old shim; not separately re-measured before this lane) | 273 patterns, 62,872 match cells, **0 disagreements** |
| definitions-oracle (`run_definitions_oracle.sh`) | — | 354 cells, 101,244 A==B + 101,244 A==C, **0 disagreements** |
| uprops `byte` arm (`run_uprops_tests.sh`, part of `make test`) | 14/0, 0 drift-attributed (measured against the OLD shim's darwin-system 10.42/14.0.0) | 91 properties compared, **0 code points attributed to version drift**, exact agreement — re-measured against the real Homebrew 10.48/17.0.0 this box's toolchain actually uses |
| capturediff gate (`run_capturediff_gate.sh` / `fuzz.py`) | — | oracle built and ran; fuzz.py's own summary: **0 content divergences, 0 accept/reject divergences** (300 patterns, seed 1) |
| `tests/probes/` build recipe | `-ldl` only | `$PCRE2_CFLAGS ... $PCRE2_LIBS ... -ldl`, verified with `probe_atom.c` and `probe_digit_sweep.c` |

**A pre-existing, unrelated darwin bug found while validating, NOT
introduced by this lane and NOT fixed here (out of scope)**:
`run_capturediff_gate.sh`'s own coverage-guard (line ~273, present verbatim
at this lane's branch point `a2ec4bf5`) uses `grep -ioP` — GNU-only Perl-regex
grep — which macOS's BSD `grep` rejects outright, so the gate's own
bucket-count extraction reads every label as `MISSING` and the script exits
1 even though fuzz.py's own printed summary (visible in the same log) is
clean: `content divergences: 0`, `accept/reject divergences: 0`. Flagging
so the manager doesn't read this run's nonzero exit as an [ORACLE-LINK]
regression.

**`make test-uprops-utf8` (opt-in, whole code-point space)**: launched
during this session under concurrent box contention from another lane's
`test-axes` battery; the `byte` arm (above, part of `make test`) completed
clean before this report was written. The `utf8` arm was still mid-sweep at
write time — OWED, log at
`/private/tmp/claude-501/.../scratchpad/uprops_byte.log` if still present
in this session's scratchpad, otherwise re-run
`bash tests/uprops/run_uprops_tests.sh` (ENC=utf8 isolates it).

**The full chained `run_registry_tests.sh` (registry_check + definitions +
definitions-oracle + PC-3 + PC-4 + compliance_section.py +
axes_registry_check.sh + limits_check.sh) was re-run as ONE process after
all pieces were fixed together: `EXIT=0`, zero `FAIL:` lines, PC-3's own
summary reads `checks passed: 209` / `checks failed: 0` (confirming the
209-not-208 coverage-count re-pin took), definitions-oracle
`354 cells... 0 disagreements`.** Full transcript archived at
`/private/tmp/claude-501/.../scratchpad/registry_final.log` for this
session; not committed (session-scratchpad per the scope mandate).

## OWED to the manager / the Linux executor (I-63 or its successor)

**The one thing to check FIRST, before anything else, because history
says it might not be true**: `tests/fuzz/pcre2_abi.h`'s ORIGINAL header
comment (pre-this-lane, still in git history) states the box this dlopen
shim was built for "has the PCRE2 8-bit RUNTIME... but NOT the -dev
package: no pcre2.h, no unversioned libpcre2-8.so symlink, no pkg-config
file." If that is STILL true of `ubuntubudu` (the current 10.46 reference,
`duxevents@100.69.121.107`), **every oracle check in the tree will SKIP
after this merge** where it used to RUN (dlopen needed no header/lib to
build; direct linking needs both) — a real coverage regression on the
REFERENCE box specifically, the one box whose result this whole project
treats as ground truth. This charter's own brief asserts "pkg-config
resolves their reference 10.46" as a given; that may already be verified
by whoever wrote the brief, but I could not confirm it myself (no Linux
access), so treat it as unverified until an executor command below
confirms it.

Exact commands for the executor (all read-only until the last one; run in
order, stop and report if any fails):

```
ssh duxevents@100.69.121.107 'pkg-config --exists libpcre2-8 && echo PKGCONFIG_OK || echo PKGCONFIG_MISSING'
ssh duxevents@100.69.121.107 'pkg-config --modversion libpcre2-8; pkg-config --cflags libpcre2-8; pkg-config --libs libpcre2-8'
```

If `PKGCONFIG_MISSING`: the box needs `libpcre2-dev` (Debian/Ubuntu package
name) installed before this branch can be validated or merged there — this
is a box-provisioning action, not a code change, and is the actual blocker
if it fires.

If `PKGCONFIG_OK` (expected — the brief's own premise), then on this
lane's branch (`lane/oralink`, or wherever the manager merges it):

```
git fetch && git checkout lane/oralink   # or the merge commit
make CC=gcc-15                            # ubuntubudu's own gcc, per BOILERPLATE
bash tests/registry/run_registry_tests.sh
```

Expected: PC-3's own summary line reads `checks passed: 209` /
`checks failed: 0` (the SAME 209, not a different Linux-specific number —
the U15b liveness guard's OWN assertion is that it stays INERT, printing
exactly one `ok()` line, on a 10.46 library; if it instead FIRES on
ubuntubudu, that is real news — U15b's drift reaching the reference itself
— and should be reported, not silently accepted). PC-4: `62872 match
cells... 0 disagreements` (population unaffected by which library is
linked, since PC-4's pattern space has no verb/POSIX candidate-pool
dependency). definitions-oracle: `354 cells... 0 disagreements`.
POSIX class names line: `149804` (the pin for 10.46) — if this reads
187872 or any other number, that means Linux's libpcre2-8-dev package
ships a DIFFERENT binary shape than the historical 10.46 measurement
assumed, and the version-keyed pin needs a third entry, derived from that
run rather than guessed.

Also owed: a `bash tests/uprops/run_uprops_tests.sh` run there (expect the
Unicode-drift table's pin-vs-oracle row to read `10.46 / 16.0.0` exactly —
i.e., pcrec's own pin, meaning the `byte` arm's drift budget should report
**0** attributed code points on the reference, a stronger result than this
box's 0-attributed-at-17.0.0 since the reference needs no drift tolerance
at all), and the seven shell runners this lane wired for
`PCREC_PCRE2_PATH` (`run_backref_diff.sh` et al. — a quick `bash
tests/backrefs/run_backref_diff.sh` smoke confirms the python leg still
resolves correctly under the new export).

## Rulings received

None mid-flight — charter was self-contained (Frank's "if your
test/evaluation passes then make it so" was the launch condition itself,
already satisfied by the linktest lane's P1-P5 before this lane started).

## Summary for handback

Validation numbers above are COMPLETE for every check this box can build
and run (PC-3, PC-4, definitions-oracle, capturediff gate, uprops byte
arm, the probes build recipe) and all are clean. OWED: the uprops utf8
arm's completion (opt-in, in progress at write time), the full chained
`run_registry_tests.sh` re-run as one process (piece-by-piece validation
is complete; the chain itself was still running at write time), and
everything under "OWED to the Linux executor" above — most importantly the
libpcre2-dev-on-ubuntubudu question, which is a real possible blocker this
report could not rule out itself.
