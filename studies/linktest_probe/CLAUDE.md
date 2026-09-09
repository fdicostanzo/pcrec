# studies/linktest_probe — direct-link oracle PROTOTYPE (linktest lane, 2026-09-09)

PROTOTYPE + MEASUREMENT ONLY, per the lane's charter — evaluates replacing
the dlopen-based libpcre2 oracle binding (`tests/fuzz/pcre2_abi.h`) with
direct linking, before any real conversion lands. Nothing here is built by
the top-level `make`, run by `make test`, or linked into pcrec. See
`docs/dev/lanes/linktest_report.md` for the P1-P5 verdict table and
recommendation.

## Files

- `resolve_pcre2.sh` — the RESOLUTION PROBE a real conversion would ship:
  `pkg-config libpcre2-8` first, a five-line compile+link fallback second,
  a loud SKIP if neither resolves. `eval "$(resolve_pcre2.sh)"` sets
  `PCRE2_CFLAGS`/`PCRE2_LIBS`/`PCRE2_VERSION`/`PCRE2_RESOLVED_VIA`.
- `pcre2_abi_linked.h` — the direct-link twin of `tests/fuzz/pcre2_abi.h`:
  same `Pcre2Abi` struct field names and the same
  `pcre2_abi_load`/`_version`/`_unicode_version`/`_path` function names,
  backed by real `<pcre2.h>` linkage instead of dlopen/dlsym.
- `pcre2_check_linked.c` — a copy of `tests/registry/pcre2_check.c` whose
  ENTIRE diff against the original is one `#include` line (verified by
  `diff` in the report) — proof the adapter header is a sufficient,
  mechanical substitution.
- `p2_header_vs_runtime.c` — standalone P2 witness: header
  `PCRE2_MAJOR`/`PCRE2_MINOR` vs. runtime `pcre2_config(VERSION)` must
  match under direct linking (they do: both 10.48).
- `microbench_dlopen.c` / `microbench_linked.c` — P5's minimal
  exec-and-resolve microbench for each shape (bind + query version + exit).
- `run_p5_timing.sh` — P5's timing sweep (absolute paths throughout —
  the agent-thread cwd resets between Bash calls, and a relative-path
  first draft of this script once wrote its results into the MAIN tree by
  accident; see the report's own disclosure). Bash 5 `EPOCHREALTIME`
  timing, no python3 subprocess per sample.
- `results/` — committed evidence: `p2_resolution.txt` (P2's binary
  output), `p2_header_vs_runtime.txt`, `full_linked.log`/`full_dlopen.log`
  (P3's full check sweeps), `fails_linked.txt`/`fails_dlopen.txt` (FAIL
  lines only), `p5_full_sweep.tsv`/`p5_microbench.tsv` (P5's raw timing
  samples).
- `build/` — gitignored (repo-wide `build/` pattern), regenerate with the
  commands in the report.

Maintenance: this directory is lane-scoped evaluation work, not (yet) an
adopted study; the real conversion lane decides whether any of it survives
past this evaluation.
