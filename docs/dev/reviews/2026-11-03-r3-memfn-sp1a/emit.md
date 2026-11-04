# Critic `emit` (memfn-sp1a): emitted-vs-replaced, BASE 564db08c5 vs SUBJECT c0c73bc20

Method: the two BUILT binaries (base/build/pcrec, worktrees/crit-memfn-sp1a/build/pcrec), single
compiles `-p rx -o -`, sha256 of stdout AND stderr per (pattern, arm), compared row by row.

## Findings

None. No emitted byte, stamp, header, diagnostic or query output moved in any arm probed (counts in
PROBED-AND-HELD). The one output difference the change makes is in MF_TRACE builds only (H6), and it
is exactly the difference span_pick.md rev 5.2 declares for 1a (:371).

Limits of this probe (not findings): (a) the per-deny arms skipped the 29 bench patterns over 2,000
characters (they ran at the 6 core arms, incl. all 14 denies at once, H9); (b) no MF_TRACE /
PCREC_CAND_TRACE binary was built (out of brief: single compiles only), so H5/H6 are static
readings; (c) the patterns are argv `--pattern`, never a `.rxt` source (the same compile below the CLI).

## PROBED-AND-HELD

- H1 Non-C CLI outputs, 10 queries: `--version`, `--help`, `--list-axes`, `--list-limits`, `--list-syntax`,
  `--list-definitions`, `--list-verbs`, `--list-families`, `--list-schema`, `--emit-support`: byte-identical
  (sha256, stdout+stderr). The deny set is taken from the binary's own `--list-axes` `#section memfn`
  (14 `--memfn=no-X` rows; same at BASE).
- H2 `--emit-facts` and `--emit-ir`, 5 patterns x 3 arms (default, `-e utf8`, `-fmemfn-simd`) = 30 queries:
  identical.
- H3 File output (`-o F.c`, so the `.h` too), 6 patterns x 3 arms (default, `-fmemfn-simd`,
  `--engine=vm`) = 18 pairs, 36 files: `diff -r` empty.
- H4 MF_CLASS_V 5->6 (memfn.h:1047) reaches NO emitted text, stamp, listing or trace line: its only
  writers are `out->v` (compose.c:360/978, window.c:2686) and its only readers are the kit's own
  harness self-compares (tests/memfn/arm_fixtures.c:376, proof_check.c:408); nothing under src/, cli/,
  lib/ or docs/spec/ reads it. Declared by span_pick.md rev 5.2 Goals row 2 and :349/:358.
- H5 pres_row/pres_led index shift: pcrec's only reader is the trace-build `pcrec_memfn_pres_routed`
  (src/gen/memfn_sites.c:787, under PCREC_CAND_TRACE + PCREC_MF_ROUTE_TRACE), which maps the index
  through the SAME build's `mf_finder_rows` listing and prints the row's NAME and pick, so the
  `MFROUTED ... PRE` lines carry names, not indices: no trace line moves from the shift by
  construction. The kit's own `MFTRACE FD ... slot=PRES` line prints `rows[i]->id` (finder.c:1084),
  also a name. `MFTRACE FDROUTE` (compose.c:1102) prints a name.
- H6 The ONE trace-only move (declared): gate.c `reach_print` (:885-900) prints a
  `MFTRACE REACH table=fd row=R3a|R3b|R4 chosen=0 asked=0` line per registered contract, so an
  MF_TRACE build at SUBJECT prints three fewer REACH lines per compile. That is exactly the declared
  difference (span_pick.md :371 "the declared difference the three gone table=fd lines R3a, R3b, R4";
  reach_equal.py `--gone`). Static reading; not run (needs an MF_TRACE build, out of my brief).
- H7 Deleted logic was dead at every compile: R3a/R3b/R4 all carried KN_H in `needs`, and BASE's
  `fd_holds` returned 0 for any KN_H row unconditionally (`if (r->needs & KN_H) return 0;`) before
  any key lookup, and `cmp_eval`'s FL_H_SPAN/FL_H_POP cases returned 0; no `fd_value` (measure-key
  lookup, the `consulted` path) could run for them. `mf_set_terms` had no caller in src/ or memfn/src
  outside terms.c at BASE (grep). No `docs/spec` file names R3a/R3b/R4.
- H8 Sweep at the DEFAULT feature set (std1, no `--features`): 419 patterns (356 distinct from
  spanpick_bench_patterns.txt via its escapes + 63 hand-written: literals, sets, alternations, classes,
  anchored, `(?i)`, long, high bytes) x 6 arms {default, `--engine=vm`, all 14 denies at once} x
  {SIMD-off, `-fmemfn-simd`} = 2,514 compiles per binary, plus 63 hand patterns x {-i, -e utf8,
  --no-captures, --emit-main} + 12 tests/memfn/n2_sample_patterns.txt = 264 x the same 6 arms = 1,584:
  4,098 per binary, sha256 of stdout and stderr and the exit code IDENTICAL row for row (8,196
  compiles). Of these 2,982 compiled (rc 0); the rest are module refusals at std1 (`\b requires
  module 'assertions'`, ...) and 13 size refusals, identical diagnostics on both sides. Hence the
  re-run at `--features all` below (emit_sweep's and reach_equal.py's own setting).
- H9 `--features all` (emit_sweep's setting), core arms: the same 419 + 264 cases x 6 arms = 4,098
  compiles per binary IDENTICAL (exit code, stdout and stderr sha256), 3,942 of them compiling.
  The 15 cases refused for size on some arm re-run with `--max-emit-bytes=30000000
  --max-emit-code-bytes=30000000 --max-nfa-states=1000000` x 6 arms = 90 per binary: identical
  (54 compile).
- H10 The kit's OWN witnesses (aimed at the find/pre-check/PRES sites): every `pattern` row of
  tests/memfn/rows.tsv with its flags and again with its control/deny flags, pres_pick_witnesses.tsv,
  c10_presence.tsv, c10_onebyte.tsv, pr11_witnesses.tsv: 68 distinct cases x ALL 34 arms (default,
  `--engine=vm`, each of the 14 denies, all 14 at once; x SIMD-off and `-fmemfn-simd`) = 2,312 per
  binary, all compile, IDENTICAL. Liveness of the arms on this population (bytes differ from the
  same layer's default): vm 65 cases, fd-d1 38, fd-pres-pick 32, pres-set-lead 26, fd-pres-g1 24,
  precheck-assign-byte 22, window-search 11, each other deny >= 20 (its stamp at least), all-deny 50/52.
- H11 Extra axes on the 63 hand patterns at `--features all`: `--tune=-2`, `--tune=2`, `--trace`,
  `--engine=dfa`, `-fmemfn-simd --tune=2`, `-e utf8 -fmemfn-simd`, `-i -fmemfn-simd --engine=vm`,
  `--fno-step-budget` = 504 per binary, identical.
- H12 Deny arms at `--features all`: the 390 cases under 2,000 characters x the 28 single-deny
  arms (14 denies x {SIMD-off, `-fmemfn-simd`}) = 10,920 compiles per binary, IDENTICAL (10,360
  compile; 0 timeouts). An earlier std1 pass over the first 1,216 of these rows was identical too.

TOTAL: about 23,300 compiles per binary (46,600 compiles) plus 50 query/listing runs and 18 file-output
pairs, every one byte-identical between BASE 564db08c5 and SUBJECT c0c73bc20 (exit code, stdout, stderr).
