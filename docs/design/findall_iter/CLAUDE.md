# docs/design/findall_iter/ — [FINDALL-NEXT]'s design probes

Evidence for `../findall_iter.md` (lane `iterdes`, 2026-10-14). Answers, sizes and
instruction identity only: no file here reads a clock. Build outputs go to the
worktree's `build/` (gitignored), never `/tmp`.

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

## twin/ — the iterator as code, on real artifacts

- `iter_abi.h` — the proposed shared-block addition (`rx_iter`, the header word
  states, `PCREC_ERR_ITER`, `RX_ITER_INIT` as a static inline returning a struct with
  only the header set).
- `mktwin.py` — a mechanical transform of a pcrec-emitted artifact into the
  iterator shape (`<p>__find`, thin `<p>_search`, `<p>__adv`, `<p>__step`,
  `<p>_next`, `<p>_next_n`). `--retry` adds the VM accept-label NOTEMPTY_ATSTART
  guard and the anchored retry (the flag rides `ctx->user` in the twin only).
  `--shared` makes the body one static noinline function (the size alternative). A
  body with a static label table is always made shared (gcc cannot copy it). Every
  rewritten anchor must match exactly once or the script exits.
- `drv.c` — the answer driver: per subject, the §3.1.3 loop (`L`), `next` with caps
  (`I`), `next` with NULL caps (`Z`, the count), a misbound call (`B`, must be
  `PCREC_ERR_ITER`), and `next_n` with k = 3 (`N`); checks stickiness after the end.
- `run_twin.sh TREE OUTDIR` — builds 17 cases (DFA, VM, hybrid, utf8, `\G`, 8 retry
  patterns), runs them, compares `I == L == libpcre2 L` (plain) or
  `I == libpcre2 G` (retry), `I == N` always, and reports `.text` sizes and whether
  `_search`'s instructions are identical to the plain artifact's.
  `TWIN_SHARED=1` selects the shared body.
- `init_spellings.c` — codegen probe: stores emitted by each iterator-init spelling
  (aggregate, statement macro, static-inline-returning expression, re-init, init-at).
- `label_census.py` — over every distinct corpus pattern (byte and utf8 arms),
  counts the artifacts whose search body keeps a static label table, by engine and
  scan stamp.
- `out/` — `run_twin_inline.out`, `run_twin_shared.out` (60 case lines each, ALL
  OK), `init_spellings.out`, `label_census.out`.

## rev3/ — revision 3's one measurement (lane `iterrev3`, 2026-10-16)

- `layout.c` — `sizeof(rx_iter)` at revision 2's layout (152 B, not the 160 B revision 2
  predicted), at revision 3's I1 layout (96 B: no `owner`, the batch setter's fields, no
  `st`) and at I2 (160 B, `st` with S = 64); and the BOUND fast path's instructions under
  `-fPIC` (one `cmpl $imm32, (%rdi)`, no GOT load). Its header has the build lines.
- `out/layout.out` — its output at gcc 15.2.0, main `37086a1db`.
