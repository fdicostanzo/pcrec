# docs/design/findall_iter/ — [FINDALL-NEXT]'s design probes

Evidence for `../findall_iter.md` (lane `iterdes`, 2026-10-14). Answers, sizes and
instruction identity, plus (lane `parity`, 2026-10-21) the pre-build parity gate's
harness: `twin/tdrv.c` is the ONE file here that reads a clock, and only in its `time`
mode. Build outputs go to the worktree's `build/` (gitignored), never `/tmp`.

## sem/ — what the iterator answers (libpcre2 as the oracle)

- `semprobe.c` — for each `PATTERN<TAB>SUBJECT` line (`.rxt` subject-escape
  vocabulary; a leading `U<TAB>` selects `PCRE2_UTF|PCRE2_MATCH_INVALID_UTF`), runs
  libpcre2-8 through two find-all loops: `L`, `match_api.md` §3.1.3's loop
  transcribed (today's protocol), and `G`, pcre2demo.c's global loop (the
  NOTEMPTY_ATSTART|ANCHORED retry after an empty match). Prints SAME/DIFF/SKIP with
  both span lists. Build: `gcc -O1 -o semprobe semprobe.c -lpcre2-8`.
- `harvest.py` — the corpus population: every `pattern` block with no `flags`, no
  extra `pcrec` flags and a byte encoding, paired with each DISTINCT inline subject of
  its case lines (`--list-source`'s `cases` section). `python3 -I harvest.py
  PCREC_BIN TREE > pairs.tsv`.
- `nullable_census.py` — joins semprobe's verdicts with pcrec's own `nullable` fact
  (`--emit-facts`) per pattern and checks the retry gate's soundness (a pattern the
  gate calls false must never diverge). Its header records the first run's finding:
  bare nullability fails on `ab\K`; the gate is nullable OR `\K`.
- `targeted.tsv` — `tests/encseam/findall_cases.txt`'s pairs plus 18 targeted cells.
- `out/` — `targeted.out` (semprobe over targeted.tsv), `corpus_summary.out` (the
  corpus totals), `corpus_diff.out` (every DIFF line, each cut to 400 chars),
  `nullable_census.out`, `retry_anchoring.out` (the anchored retry against an
  unanchored NOTEMPTY_ATSTART variant: 0 corpus pairs differ, a `\G` cell does; the variant is
  `semprobe.c` with `| PCRE2_ANCHORED` deleted from the retry's options).

Reproduce: `python3 -I sem/harvest.py build/pcrec . > P; semprobe < P > O;
python3 -I sem/nullable_census.py build/pcrec O`.

## twin/ — the iterator as code, on real artifacts (RE-SPELLED to revision 3, lane `parity`)

Revision 3 (lane `parity`, 2026-10-21) replaced revision 1's twin in place; revision 1's
`iter_abi.h`, `mktwin.py`, `drv.c` and `run_twin.sh` are in git history, and its outputs
stay in `out/` as the record.

- `iter_abi.h` — §1.1's shared-block addition at I1, transcribed: the header word (tag,
  LAYOUT 3, FRESH/BOUND/ENDED, option bits), no `owner`, no `st`, `RX_ITER_INIT(s, n)`
  (binding at init), the setters `rx_iter_at`/`rx_iter_vars`/`rx_iter_batch` with the
  poison/ENDED-no-op rule.
- `mktwin.py` — a mechanical transform of a pcrec-emitted artifact into the revision-3
  shape: `<p>__find` (the whole `_search` body), a thin `<p>_search`, `<p>__adv`, STEP
  (`<p>__step`), `<p>__enter` (bind: normalize every optional field, K into `nbatch`,
  BOUND; ENDED returns 0; else refuse with `PCREC_ERR_ITER`), `<p>__end`, and
  `int <p>_next(rx_iter *, caps)` whose fast path is the one header compare. The
  `iterate` row's batch cell: default `off` (STEP once, K forced to 1, plus
  `<p>_next_n`), `--fill` (`__deliver`, `__fill` with the IT2 test first, the cursor
  test in `_next`; no `_next_n`). `--retry` adds the VM accept-label NOTEMPTY_ATSTART
  guard and the anchored retry; `--shared` makes the body one static noinline function
  (the `I_shared` arm); a body with a static label table is always shared. Stated
  fidelity gap: the per-call entry checks stay in `__find` (the design moves them to
  bind), which costs the twin, never the loop. Every anchor must match exactly once.
- `drv.c` — the answer driver: per subject the §3.1.3 loop (`L`), `next` with caps
  (`I`, with stickiness and the setter-on-ENDED no-op), NULL caps (`Z`), the header
  state machine (`X`: setter on BOUND poisons, zeroed header refuses), an
  `rx_iter_at(&it, 1)` start against the loop from 1 (`A`/`La`); off builds add
  `next_n` k = 3 (`N`), fill builds (`-DTWIN_FILL`) the batched `B` (K = 64) and `BK`
  (K = 2, 3 and a one-entry region against `I`, final rc included; regions are
  exact-size heap so an over-fill is an ASan error).
- `run_twin.sh TREE OUTDIR` — builds the 17 cases (DFA, VM, hybrid, utf8, `\G`, 8
  retry patterns), compares `I == L == libpcre2 L` and `A == La` (plain) or
  `I == libpcre2 G` (retry), `I == N` or `I == B` + `BK=ok`, `X=ok` always, and
  reports `.text` sizes and `_search` instruction identity. `TWIN_SHARED=1`,
  `TWIN_FILL=1`, `TWIN_ASAN=1` (ASan+UBSan), `TWIN_DIR=` (a planted copy).
- `tdrv.c` — §5.3's TIMING driver, one binary per (pattern, arm, regime): `-DARM_LOOP`
  (the §3.1.3 loop), `-DARM_ITER`, `-DARM_BATCH` (64-entry region), `-DARM_NEXTN`
  (k = 64). `check` prints count + FNV-1a hash of the spans; `time` calibrates reps to a
  target per sample and prints the median ns per whole find-all.
- `parity.sh build|gate|time|verdict|run|smoke|calib OUT` — the parity slot's run: the
  subjects (rwcorpus prose sha-pinned: `pg2701.txt` bytes [64 KiB, 64 KiB + 1 MiB) and its
  first 4 KiB), the four artifacts with cell 6's `attempt` stamp asserted, 9 arms x 2
  regimes; THE ANSWER GATE (G1 the three twins' 60-case tables under ASan, G2 every timing
  binary against `L_old`, G3 `L_old` against python `re`, G4 the PLT structure), exit 3
  before any timing on a disagreement; then 5 launches pinned to `PARITY_CPU` (7), arms
  rotated, and the verdict. Its header states every arm decision.
- `parity_expect.py` — G3's independent answers (python `re` over the subject bytes).
- `parity_verdict.py` — §5.3's table and verdict rule (floor from the A/A arm, I and B64
  gates, the batch cell, I_shared/N64 reported), ending `== parity COMPLETE <rows>`.
- **[FINDALL-NEXT] I4 (lane i2build, `../findall_iter_i2.md` §4):** `PARITY_I4=1` (implies
  `PARITY_POST=1`, `PCREC_OLD` = the I1 compiler) adds arms `I_i1`/`I_i1b` (the I1 artifact's
  `_next`, two compiles), `I` (this compiler's `_next`), `F`/`Fb` (RX_FOREACH over `rx_info`,
  two compiles), `I_info` (`rx_info.next` per match), `N4`/`N64` (`_next_n`, entries NCAPS
  apart), cell `c8` (one match at byte 16 of 1 MiB, stop 1); the answer reference is `I_i1`;
  G4 expects no PLT call of the rx_info arms. `tdrv.c` gains `ARM_FOREACH`, `ARM_INFO` and
  `NEXTN_K`. `i4_verdict.py` (called by `parity_verdict.py` when an `Fb` arm is present):
  per-ratio A/A floors over the launches, gates G1 `I/I_i1`, G2 `F/I` never worse, G3 the
  positive gain on c3-4k/c3-1m R2, G4 c7/c8, and the `QUIET` line the queue job re-queues on.
- `parity_job.sh` — the `150-parity-slot` boxqueue job (`--dry-run` a no-clock build and
  the quick gate; `--ready` the quiet gate, load1 < 2.0 twice a minute apart, read back
  from `queue.log`; the work `exec taskset -c 7 parity.sh run`).
- `init_spellings.c` — codegen probe: stores emitted by each iterator-init spelling
  (aggregate, statement macro, static-inline-returning expression, re-init, init-at).
  Revision 1's (one-word init); not re-run for revision 3's `RX_ITER_INIT(s, n)`.
- `label_census.py` — over every distinct corpus pattern (byte and utf8 arms),
  counts the artifacts whose search body keeps a static label table, by engine and
  scan stamp.
- `out/` — revision 1's `run_twin_inline.out`, `run_twin_shared.out` (60 case lines
  each, ALL OK), `init_spellings.out`, `label_census.out`; revision 3's
  `run_twin_rev3_{off,shared,fill}.out` (60 case lines each, ALL OK under ASan+UBSan,
  main `5cc3d7179`, gcc 15.2.0).

## rev3/ — revision 3's one measurement (lane `iterrev3`, 2026-10-16)

- `layout.c` — `sizeof(rx_iter)` at revision 2's layout (152 B, not the 160 B revision 2
  predicted), at revision 3's I1 layout (96 B: no `owner`, the batch setter's fields, no
  `st`) and at I2 (160 B, `st` with S = 64); and the BOUND fast path's instructions under
  `-fPIC` (one `cmpl $imm32, (%rdi)`, no GOT load). Its header has the build lines.
- `out/layout.out` — its output at gcc 15.2.0, main `37086a1db`.
