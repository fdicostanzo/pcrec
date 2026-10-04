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
- `c3_movers.py` / `c3_movers.log` — **C3's mover manifest and deny arm**
  (lane `c3build`, 2026-10-03; design §5.1 item 1): the census's own
  populations (corpus via `--list-source` with flags/encoding x {auto, vm};
  every pcrec-bench export x {auto, vm} x {caps, --no-captures}), compiled by
  the abi-58 and abi-59 compilers and by abi 59 under `-fno-req-run-fold`.
  Asserts the BICONDITIONAL (moved, byte for byte after the abi digit, <=>
  NEW's `REQ_RUN` carries `/mask`) and that the deny restores the abi-58
  artifact whole; lists every mover's REQ_RUN/REQ_WHY/prefilter/pin move.
  Landing: 41 auto movers = the census's 41 (corpus 15 A1 + 15 C, bench 8 A1
  + 3 C), 0 off-diagonal, deny arm identical on all 7,802 compiled
  artifact-configs. `BASE`/`NEW`/`SCR`/`BENCH` from the environment.
- `c3_answers.py` / `c3_answers.log` / `c3_answers_san.log` — **C3's answer
  differential** (design §5.1 item 2, §5.2): every mover BASE vs NEW through
  `tests/possessify/possdiff_driver.c` at every startpos over
  `tests/findings/b1_mover_answers.py`'s subject sweep (PREFIXES=1) plus
  subjects of length 0..7, classified by the design's table (give-up ->
  NOMATCH allowed; NOMATCH -> give-up, give-up -> match and any span change
  a DEFECT). `_san` is the same run built `-fsanitize=address,undefined
  -fno-builtin-memcmp -DDIFF_EXACT_SUBJECT`. Landing: 104/104 identical,
  125,328 cells, both builds.
- `alpha_c3.sh` — **C3's Linux alpha block** for the manager's executor run
  (design §6.1-§6.2's C3 table; D144 addendum 1): `build` (BASE = abi 58,
  NEW = C3, DENY = NEW `-fno-req-run-fold`; every bench set's throughput
  subjects regenerated under `$S4A` by importing its own generator with its
  output paths repointed, sha256-checked against the committed manifests),
  `check` (DENY == BASE modulo the abi digit alone; witnesses moved with a
  masked REQ_RUN, controls not; answers identical), `time` (taskset, load1 <
  0.5, launches round-robin, >= 50 ms calibrated loops; ABSOLUTE deltas
  beside the |DENY - BASE| floor, ns/B for throughput cells and ns/CALL for
  `union-srch`, union-select's search_short subjects). Cells: union-select
  nocaps/caps, the census's bench movers, slack and http-5xx (class C),
  A0/B controls.
- `hot.c` — a darwin SCRATCH-tier find-all loop over 1 MiB (random text, and
  a near-miss band): today's per-byte fold chain, masked words `&&`/`|`, and
  exact `memcmp`/`overlap`/`|` at L = 7. `gcc-16 -O2 -o hot hot.c && ./hot 0`
  (and `1`). Directional only: it is cited because it CONTRADICTS
  `memcmp_lowering_study.md` §11 in this loop shape (design note §1.6).
- `c3census/` — lane `s4rev`'s r1 census for C3 (design note §2.3.7),
  RE-RUN for r2 by lane `s4rev2` (2026-10-03, from main `af615d01`,
  serial): `proto.patch` now also carries r2's fact half (the cube-candidate
  PICK, the member-mass window, `req_byte`'s exact-member clause, the
  exact-stretch `run_pin`, rendered `o` or `o:at+len`), the TSV gains
  PROTO's `req_run`/`req_byte`/`run_pin` columns, and `c3_report.py` checks
  class B on all four facts and reports the pins of classes A1/C:
  - `proto.patch` — the necessary-run walk ((T, K) positions in the
    two-member domain, the alternation cube hull, the information ranking,
    `whole_mask` rendered in `--emit-facts`' `req_whole_run`) plus r2's fact
    half above, applied to a SCRATCH copy of main (`af615d01` at r2;
    `92b8bbf0` at r1). Never applied under `src/`. Its emitted C is not
    meaningful (the emitters still read T as exact; `us_run_pin` hides a
    sub-window pin from them so the compile does not trip their checks).
  - `c3_census.py` — compiles every corpus `.rxt` pattern (as written, via
    `--list-source`) and every pcrec-bench export (read-only) at `--features
    all --emit-facts` under `BASE` and `PROTO`. Patterns are passed to argv
    as BYTES. Env `BASE PROTO BENCH CORPUS OUT JOBS` (JOBS defaults to 1:
    serial). It writes `c3_census.tsv`.
  - `c3_census.tsv` — that raw output (4,663 rows at r2).
  - `c3_report.py` / `c3_summary.txt` — applies the one floor (16 bits) and
    classifies A0/A0b/A1/B/B!/C. The summary is the numbers the note cites.
