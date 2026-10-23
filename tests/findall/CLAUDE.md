# tests/findall — the find-all iterator's checks ([FINDALL-NEXT] I1)

`<prefix>_next(rx_iter *, caps)` (docs/spec/match_api.md §3.8) held to
libpcre2's GLOBAL iteration, the loop of pcre2demo.c (after an empty match,
retry anchored with NOTEMPTY_ATSTART, else step one character). `make
test-findall` runs `run_findall_tests.sh`; mech arm `findall`.

## Files

- **iter_drv.c** — the driver, built against one artifact and libpcre2-8.
  Per subject: the iterator's spans (`I`), libpcre2's global loop (`G`, the
  oracle) and match_api.md §3.1.3's loop (`L`), plus the state-machine arms
  (sticky, endset, nullcaps, poison, dirty-init, info, at1), and the I4 arms
  (`<prefix>_next_n` at k = 1, 2, 3, 64; its NULL-caps count; `_next` and
  `_next_n` alternating; the generic loops over `info->next` (G1) and
  `info->next_n` (GN, batches of 4); k = 0 on FRESH/BOUND/ENDED). Each subject's `R=` field lists the reach tokens of
  sabotage rows S1309-S1314, S1319, S1321, which `run_iter_diff.sh` floors (`REACH_NEED`).
  Verdicts OK /
  DIFF / GIVEUP / ILLFORMED / SKIP (its header defines each). The caps buffer
  and the `rx_iter` are heap-allocated at their exact sizes, so an over-write
  is an ASan error in the ASan cells.
- **run_iter_diff.sh** — the differential over a cell file, grouped by
  (encoding, flags, pattern), each group on `auto`, `--engine=vm` and
  `--engine=dfa` (a DFA refusal is not a cell). Also holds
  `<PREFIX>_ITER_RETRY` to the text (`vm-guard` iff the accept guard,
  `dfa-root` iff a retry machine). Floors: compiled groups, RETRY cells
  (subjects where `I` differs from `L`, i.e. the retry decided a match), and
  at least one artifact of each retry form, and every I4 reach token. A
  GIVEUP is a failure except under `-futf-check` (the documented refusal of
  an ill-formed subject) and `--step-budget` (the cells that end mid-batch);
  ILLFORMED (a utf subject that is not well-formed, the iterator agreeing
  with the loop) is counted, the documented boundary difference.
- **run_findall_tests.sh** — the section: `run_iter_diff.sh cells.tsv`,
  `run_one_body.sh`, then the ASan cells (a subset rebuilt with
  `-fsanitize=address,undefined`).
  `run_iter_diff.sh` is also in `tests/lib/san_scripts.txt` ([TT-9]), so the
  sanitizer axes run it through `$GENCFLAGS`.
- **run_one_body.sh** — [FINDALL-NEXT] I4 (ruling R1), re-pinned by lane
  iteropt2: `rx__one`'s body equals, as text, the pinned one
  (`one_body/*.one_body.txt`, written by the iteropt2 compiler when the
  cursor retired the I1 text identity), on `\w+`, `^a|b` and `(a)`, with a
  planted one-token control.
- **one_body/** — those three expectations.
- **cells.tsv** — the cells: lane iterdes's targeted byte set
  (docs/design/findall_iter/sem/targeted.tsv), the retry shapes the design
  names (`\K`, lookaround, anchors, compound splits) over 18 subjects, and
  utf8 groups with ill-formed subjects, plain, `-futf-check` and
  `-fstartpos-guard=align` (`a\x80a` and `\xc3\xa9\x80a` put a stray right
  after a non-empty match: S1300's witness, K75's aligned end).
- **gen_global.py** — writes **global.rxt**, the `mg` corpus
  (rxt_format.md §1.7.1), from libpcre2's counts through `iter_drv.c`, with
  `# pcre2-only` computed against python `re.finditer`. global.rxt rides
  `test-corpus` (run.sh's `mg` arm drives `<prefix>_next`; verify_rxt.py
  re-verifies with `re.finditer`).

- **mover_census.py** — IT15's MOVER CENSUS (not a `make test` section; a
  delivery-bar run): every corpus pattern under the parent compiler and the
  iterator's, default engine and `--engine=vm`, comparing the outcome, the
  engine stamps and the COUNTED size (`--warn-emit-bytes=1`'s report, what a
  length decision reads). A counted move is explained only by a dfa-root
  retry machine, or by one byte on a compound shell.

The pattern column is the pattern as written; the subject column is the
`.rxt` subject-escape vocabulary. libpcre2 is resolved by
tests/lib/resolve_pcre2.sh; without it the section SKIPS loudly.
