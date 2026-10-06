# artharness report -- [ARTREV] S0 harness + draft selection (2026-10-05, sonnet)

Branch `lane/artharness` (worktree `worktrees/artharness`), off main `9f444d41`. Nothing under
`src/ cli/ lib/ tests/` changed (tests/ was READ for the corpus reader). Mac only; nothing was
run on ubuntubudu; no `make`/suite run. No SIMD anywhere.

## What was built (`studies/artrev/`, own CLAUDE.md + README.md; scratch `build-artrev/`, gitignored)

| piece | where | notes |
|---|---|---|
| `gen` | `artrev.py` | pcrec binary + pattern + flags -> `artifact.c/.h`, `artifact.s` (`gcc -O2 -fPIC -S` of the shim TU), `meta.json`, `GENERATION.txt` (pin, abi, gcc, the exact generation / asm / compile lines, binary sha256). `--features all` is added as the bench does. Refuses clang (bare `gcc` on this Mac IS clang: use `ARTREV_CC=gcc-16`). |
| `twin` | `artrev.py` | `--patch FILE`, `--null`, or `--new` + hand edit + `--seal` (writes `twins/<arm>.rN.patch`). REJECTS (exit 4, arm dir removed, row logged REJECTED): intrinsics headers, `__builtin_ia32_*`, `__builtin_neon*`, vector builtins, `vector_size`/`ext_vector_type`, `#pragma GCC optimize/target`, `ivdep`/omp-simd pragmas, `__attribute__((optimize/target/target_clones/simd))`, `__m128`-style and NEON types, `_mm*`/`vld1*` calls, and ANY `artifact.h` change or stray file. Scans the lines the twin ADDS (difflib), not the patch text. |
| `identity` | `identity.py`, `driver_id.c`, `shim.c` | transcripts of original and twin compared byte for byte over S, SI, M, MI, C, CI, N (next_pos), V (valid_upto) at several `from` offsets plus a find-all walk (F/FC/FSI) on supplied files; every call on a private exact-length heap copy, caps pre-set to -2. Populations: (i) `--subject` files, (ii) `--corpus` = every `tests/**/*.rxt` `m`/`n` subject of a block whose pattern text, flags and encoding equal the artifact's, (iii) a battery: random over the pattern's alphabet, lengths 0-64 and k*B-1/k*B/k*B+1 for each `--block B`, a regex SAMPLER (sre_parse, PCRE->Python shim) seeds real matches, then matches alone / at start / at end / with filler, and near-misses (delete, replace, truncate each end, duplicate, extend). Prints the match share and a THIN warning under 5%. libpcre2 sample (`pcre2_ref.c`, 1500 cases, 10.48 Homebrew, version printed; pcrec give-ups skipped and counted; a disagreement the ORIGINAL shares is a note, a twin-only one fails). `--san` builds both arms with ASan+UBSan. Writes an `identity` ledger row (PASS/FAIL, sha). First differing line, case and subject printed on failure. |
| `time` | `timing.py`, `bench_t.c` | u3twin's shape: all arms built first, per-subject answer checksums, reps calibrated on the original (~80 ms/unit), arms rotated per round, load gate before EVERY unit, median + IQR per arm per subject, `orig`, `orig2` (original recompiled) and `null` as standard arms (null mandatory). Verdict per charter S4: WIN/LOSS only past max(null deviation, IQR_arm, IQR_orig). Output `timing/NNN/{raw.tsv,summary.tsv,summary.txt,watchdog.log}`. Under `scripts/watchdog` (wall 600 s, RSS 2 GB). Refuses (exit 5) on `worktrees/.mac-suite.lock` (FILE or DIRECTORY form), a held `build-artrev/.timing.lock`, an arm with no PASS identity row for its exact sha, or an arm whose `artifact.c` is not its last logged revision (unlogged edit); exit 7 and nothing logged when load stays over the gate (default 2.0 darwin / 0.5 Linux). |
| `--remote ubuntubudu` | `timing.py` | refuses outside 08:00-19:00 local; bundles arms + harness + `scripts/watchdog`, `ssh -o BatchMode=yes duxevents@100.69.121.107`, atomic `mkdir ~/scratch_lx/artrev/.timing.lock`, `gnutimeout` + watchdog + `_rawtime`, `scp` raw back, lock + run dir removed in a `finally`. BUILT AND DRY-RUN ONLY: `--dry-run` prints the seven commands; the bundle was additionally unpacked and run locally as the remote would. NOT executed against the box. |
| bounds | `common.py` | `iterations.tsv` per artifact, one row per twin revision (REJECTED/NOAPPLY included) and per timing run (failed included): refuses a 7th lead, a 5th revision, a 4th timing run of one revision (exit 3, "BOUND"). `null`, `ctl_*` and the standing arms are uncounted. A load-gate refusal is not an attempt. |
| overrides | | `--gate-override`, `--hour-override`, `ARTREV_SUITE_LOCK_PATH` work ONLY under `ARTREV_SELFTEST=1` (set by selftest.sh alone), are logged in the ledger and stamped in `raw.tsv`, and are refused otherwise (self-tested). |

## The compile flags (the bench's), and where they are

pcrec-bench compiles every pcrec artifact as `$CC -O2 -fPIC -shared shim.c` with the artifact's `.c`
`#include`d into the shim (one TU), `-I` the artifact dir; gcc by default (`$CC`, clang only on explicit
`cc = "clang"` configs). Source: `/Users/fdicostanzo/pcrec-bench/testees/pcrec/adapter.py` ("COMPILE
COST, THREE PHASES", ~line 86) and the opening comment of `testees/pcrec/shim.c`; `-O` axis configs
(`-o0/-o1/-o3/-os`) append after the fixed `-O2` (adapter ~3198). Here the same line is used for every arm:
`$CC -O2 -fPIC -I<arm> -DARTREV_PFX=<p> -DARTREV_PFXU=<P> [-DARTREV_HAVE_IN=1] shim.c <driver>.c`, with
`-shared` dropped because the drivers are executables (an `.so` and an executable differ in the PIC/PLT
treatment of the exported entries only). Unresolved: the Linux bench's gcc is 15.2 (bench NOTES) and the
Mac's Homebrew gcc is 16.2; the confirmer's ubuntubudu gcc is whatever is installed there, recorded in each
`raw.tsv` header.

## Self-test (`studies/artrev/selftest.sh` -> `selftest.log`): 101/101 checks, 0 failed, ~30 s

Failing direction, each a PASS meaning "the bad thing was caught":
- **wrong twin FAILS identity**: a twin shortening the match end in `search` (identity rc 1, "FIRST
  DIFFERENCE" printed); a twin corrupting one capture slot in `match_caps` only (rc 1, first difference on a
  `C` line) -- both on the VM+captures artifact.
- **`time` refuses an arm without a passing identity** (rc 3).
- **SIMD/flag patches REJECTED** (rc 4, "forbids", arm dir removed): ten variants (`<immintrin.h>`,
  `<arm_neon.h>`, `__builtin_ia32_*`, `__builtin_neon*`, `vector_size`, `#pragma GCC target`, `#pragma GCC
  optimize`, `__attribute__((optimize))`, `__attribute__((target))`, `_mm_*` calls), the `--patch` route, and
  an `artifact.h` edit.
- **slowed (answer-identical, busy loop per call) twin: identity PASS, then times as LOSS** on both subjects
  (cell 7.93 -> 49.8 ns/B; sparse 3.28 -> 21.1); **null twin NOISE; orig2 NOISE**; the verdict rule also
  checked on synthetic rounds (WIN, LOSS, null NOISE, a sub-null-deviation delta NOISE, a noisy faster arm
  NOISE).
- **bounds**: 6 leads sealed, the 7th refused; lead L1 revised to 4, the 5th refused; L2 timed 3x, the 4th
  refused; an unsealed hand edit refused by `time`.
- **locks and gates**: suite lock as a FILE and as a DIRECTORY, a held `.timing.lock`, the load gate (rc 7,
  not logged), `--remote` outside the window, the overrides outside the selftest -- all refused; `--remote
  --dry-run` prints `BatchMode=yes`, `gnutimeout`, `scratch_lx/artrev`, `watchdog`.
Positive direction: null twins PASS identity on the VM and DFA artifacts, plain and `--san`, with libpcre2
(1500 sampled cases, 0 disagreements).
CAVEAT, loud: the selftest timing runs with `--gate-override` on a Mac at load 8-29 (another lane's suite);
it proves the MECHANISM and the verdict rule, it says nothing about this box's noise floor. A real
`.mac-suite.lock` directory existed while I worked and the harness refused to time against it, unprompted.

## Draft selection (`docs/dev/optloop/artrev/selection.tsv` + `selection.md`)

16 cells A01-A16, stratified by route (dfa-scan, dfa-attempt, vm, hybrid, utf8) x captures x standing
(losing / near-tie / winning), every one a cell the bench already times (pcrec `auto-caps` vs libpcre2 jit,
`large-subject-throughput`, from pcrec-bench's `2026-10-02-*-fc719ca4` reports: 300 paired cells -> 71
losing, 8 near-tie, 221 winning; cross-checked against the 10-05 gap report). PILOT: **A01 loglines/stack-frame**
(DFA find-all, LOSING x4.83), **A07 capability/doubled-word** (VM with captures, LOSING x1.93), **A09
loglines/level-context** (hybrid, LOSING x3.82, CTX not START-SET). The three were generated at current main
(`ca7bdb11`, abi 61 -- the charter's pin is abi 62, so this is a dry run) and each passed null-twin identity
(1500-subject battery, 37k transcript lines, libpcre2 sample clean). `gen_selection.py` regenerates any
subset at a named pin.

## Unresolved / for the manager
1. **Pin**: regenerate the pilot at the post-START-SET-stage-2 binary (`gen_selection.py --pilot --force
   --pcrec BIN --pin SHA`); A01 and A10 may move with stage 2 (A10 certainly: it is the START-SET headline).
2. **Subjects**: only `bench/capability/throughput/*.bin` is in the Mac checkout; the loglines/syntax/utf8
   throughput subjects and the short-subject files need to come from the bench's generators or the Linux box
   (a pcrecdev2 relay). The attempt-form cells (A05 A06 A11) are ns/call cells and need short subjects, not
   throughput files.
3. **Selection gaps**: no VM/hybrid near-tie and no utf8 losing-vs-JIT cell exists in the data (documented in
   selection.md); ratios are one pin older than the 10-05 gap report.
4. **Remote mode is unproven on the real box** (by instruction). Needs: key-based ssh as `duxevents`, `gnutimeout`,
   `python3` >= 3.8, `gcc`, and `scripts/watchdog`'s /proc path; `ARTREV_REMOTE_CC` if gcc is not `gcc`. It cannot
   see a declared bench window, only the hour.
5. **The null twin is an unused `static` function**: it moves no code under -O2, so it measures process/ASLR/
   recompile noise like `orig2` does, NOT layout noise from a code-moving twin (the k87twin lesson). If the
   pilot shows layout cliffs, a pad-shifted null arm (k87twin's `.skip`) is the add; not built (D77).
6. **Python 3.9** on this Mac (`sre_parse` deprecation warnings appear on 3.11+; harmless). The libpcre2 sample
   is 10.48 Homebrew, not the 10.46 reference.
7. Identity covers `rx_info`-free call shapes only; `callout`/`vars` entries (not in selection) are not driven.

## Commits
WIP commits on `lane/artharness` (`git log 9f444d41..lane/artharness`); final head named in the handback.
