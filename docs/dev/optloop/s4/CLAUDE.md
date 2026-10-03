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
