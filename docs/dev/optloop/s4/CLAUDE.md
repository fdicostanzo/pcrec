# docs/dev/optloop/s4/ — `[OPT-LITSCAN]` S4's design instruments (lane `s4des`, 2026-10-03)

The counts and probes behind `docs/design/litscan_s4.md`. Reference
material, never built or run by `make`. Every number they produced is quoted
in the design note with its section.

- `census.py` — compiles every pcrec-bench `bench/*/patterns/*.rx` export
  (read-only; `-e utf8` for the utf8 set) at default selection and at
  `--engine=vm`, and counts P4 `memcmp` lengths, artifacts with a compare at
  an overlap length (C1's movers) and VM fold-pair tests (C2's candidates).
  Paths come from `PCREC`, `BENCH` and `OUT` (default `cen/`, a scratch
  directory: never commit its output). Pass any argument to list the
  forced-VM artifacts with at least 3 fold tests. Design note §7.
- `spell.c` — the candidate emitted spellings as free functions: masked
  `&&` vs `|`-of-xors at L = 3, 6 and 12, a masked L = 20 multi-word, and exact
  `memcmp` vs `overlap` at L = 3 and 5, all with the endian-neutral
  `memcpy`-from-string-literal constants. Read with `gcc-16 -O1/-O2 -S`,
  `clang -O2 -S` (arm64 and `-target x86_64-apple-macos`). Design note
  §1.4-§1.5; the x86 gcc-15 arm is the alpha block's step 0 (§6.2).
- `one.c`, `two.c` — the ASan-visibility pair: the hand overlap (`one.c`)
  gets one `__asan_report_load_n` per word at `gcc-16 -O2
  -fsanitize=address`; the constant `memcmp` (`two.c`) gets none, and is
  intercepted only under `-fno-builtin-memcmp`. Design note §0 item 5, §5.2.
- `c1_movers.py` — **C1's mover census and deny arm** (lane `s4build`,
  2026-10-03): every pcrec-bench `bench/*/patterns/*.rx` export and every
  corpus pattern, x {auto, vm}, compiled by the C0 (abi 55) and C1 (abi 56)
  compilers and by C1 under `-fno-run-overlap`. Asserts the BICONDITIONAL
  (moved after normalizing the abi digit and dropping the `RX_RUN_WORDS`
  line <=> the C1 artifact's `RX_RUN_WORDS > 0`) and that the deny restores
  the abi-55 program. `BASE`/`NEW`/`SCR` from the environment; its transcript
  is in `docs/dev/lanes/s4build_report.md`.
- `alpha_c1.sh` — **C1's Linux alpha block** (design §6.1-§6.2, D144 item 1)
  for the manager's executor run on ubuntubudu: `step0` ([WORD-FOLD]'s owed
  gcc-15/x86 instruction arm on `spell.c`/`one.c`/`two.c`), `build` (BASE =
  C0, NEW = C1, DENY = NEW `-fno-run-overlap`; the subjects regenerated and
  sha256-checked against the bench's manifests, writing nothing in either
  repo), `check` (DENY == BASE modulo the abi digit and the stamp line, the
  witnesses reached and the controls not, every arm and the two fused `|`
  twins answer-identical), `time` (`taskset`, load1 < 0.5, 5 launches
  round-robin x 5 timed loops of >= 60 ms each, median of medians; per D144
  addendum 1 it reports ABSOLUTE ns/B deltas beside the floor |DENY - BASE|,
  never a ratio, and a delta inside the floor reads NULL). Its `build`/`check` steps were smoke-tested on the Mac with
  the lane's own binaries; `time` is Linux-only.
- `hot.c` — a darwin SCRATCH-tier find-all loop over 1 MiB (random text, and
  a near-miss band): today's per-byte fold chain, masked words `&&`/`|`, and
  exact `memcmp`/`overlap`/`|` at L = 7. `gcc-16 -O2 -o hot hot.c && ./hot 0`
  (and `1`). Directional only: it is cited because it CONTRADICTS
  `memcmp_lowering_study.md` §11 in this loop shape (design note §1.6).
- `c3census/` — lane `s4rev`'s r1 census for C3 (design note §2.3.7):
  - `proto.patch` — the r1 necessary-run walk ONLY ((T, K) positions in the
    two-member domain, the alternation cube hull, the information ranking,
    `whole_mask` rendered in `--emit-facts`' `req_whole_run`), applied to a
    SCRATCH copy of main `92b8bbf0`. Never applied under `src/`. Its emitted C
    is not meaningful (window/pick/emitters still read T as exact).
  - `c3_census.py` — compiles every corpus `.rxt` pattern (as written, via
    `--list-source`) and every pcrec-bench export (read-only) at `--features
    all --emit-facts` under `BASE` and `PROTO`. Patterns are passed to argv
    as BYTES. Env `BASE PROTO BENCH CORPUS OUT JOBS`. It writes
    `c3_census.tsv`.
  - `c3_census.tsv` — that raw output (4,657 rows).
  - `c3_report.py` / `c3_summary.txt` — applies the one floor (16 bits) and
    classifies A0/A0b/A1/B/B!/C. The summary is the numbers the note cites.
