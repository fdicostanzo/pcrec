# studies/revend_twin/ — [OPT-REVEND]'s hand-twin (lane revdes, 2026-10-09)

The first owed step of the `[OPT-REVEND]` plan row: take emitted artifacts at
main (`de6acf09`, abi 70), replace the forward pass of `<prefix>_search` by
the reverse walk seeded at the subject end, check answer identity, and time
both. Backs `docs/design/revend.md` §6-§7. SCRATCH TIER: Linux dev box
(Ryzen 7700X, gcc 15.2, `-O2`), pinned to one core, load1 about 4 from a
concurrent chain. Never built or run by pcrec's `make`.

## Files

- `mktwin.py IN.c OUT.c PREFIX EOL`: the twin generator. Asserts every
  marker in the artifact's text and refuses rather than half-transforming.
  Forms (`TWIN_FORM`):
  - `exact` (form A, default): no forward pass; `<p>_match` from `s*` gives
    the end;
  - `lower` (form B, the design's choice): the walk sets `search_from = s*`
    and the body is untouched.

  Controls (`TWIN_SABOTAGE`): `noeol` drops the `n-1` seed; `firstseed`
  keeps the first accepting seed instead of the minimum.
- `check.c`: answer-identity driver. It links artifact (`o`), twin (`t`) and
  libpcre2-8.
  - It covers every `search_from` in `[0, n+1]` on subjects ≤ 512 B. Longer
    subjects get a sample, with the oracle asked only at 0 and the last 8
    (libpcre2's interpreter is quadratic on the nullable shapes).
  - It runs a find-all loop for each subject.
  - utf8 oracle flags: `PCRE2_UTF | PCRE2_MATCH_INVALID_UTF`, no UCP.
  - Mid-character startpos cells (pcrec refuses them, K50) are compared twin
    vs artifact only.
- `timedrv.c`: interleaved artifact/twin timing. 20 calls x 15 rounds, min
  and median, and an answer-identity assert.
- `mksubj.py REPO OUT`: deterministic subjects, written to `work/subj/`:
  - pools harvested from `tests/assertions`, `tests/base` and `tests/utf8`
    `.rxt` subjects, plus hand edges;
  - ~1 MiB synthesized bodies;
  - the timing stand-ins for the bench's `t-tail-*-1m`, `t-1m` and
    `t-trim-nearmiss-16k`. They use the bench MANIFEST's described tails, not
    its bytes.
- `patterns.tsv`: 43 rows (name, encoding, eol, pattern). They are the
  bench's five tail patterns, the census's 24 DFA-routed class-U corpus
  witnesses, 6 edge shapes and 8 utf8 shapes.
- `controls.tsv`: the four patterns the sabotage controls run on.
- `run_check.sh`, `run_timing.sh`, `run_all.sh`: the drivers. Run them with
  `PCREC=build/pcrec ./run_all.sh`. They regenerate everything into the
  gitignored `work/`.
- `results/`: the verbatim outputs.
  - `check.txt`: form A, byte.
  - `check_utf8.txt`: form A, utf8. It supersedes `check.txt`'s utf8 rows,
    which used a UCP oracle by mistake.
  - `check_lower.txt`: form B, all rows.
  - `control_noeol.txt`, `control_firstseed.txt`: must be red, and are.
  - `timing.txt`: form A, 3 repeats, with load1 per line.
  - `timing_lower.txt`: form B.
- `.gitignore`: `work/` (generated artifacts, binaries, ~25 MB of subjects).
