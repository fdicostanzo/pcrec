# docs/dev/optloop/lossreview/rev2/ — fixes.md revision 2's no-clock instruments

Lane `lrrev`, 2026-10-11. COUNTS AND SIZES ONLY: nothing here reads a clock,
and nothing is built or run by `make`. Scratch (`build/lr/`, gitignored)
holds a `git archive` copy of pcrec-bench (read-only source) whose capability
throughput generator was run IN THE COPY (11 subjects, sha256-checked against
`manifest_throughput.tsv`), and the compiled artifacts. Compiler: this
worktree's `build/pcrec` at main 8359970e (abi 74).

- `split_size.sh PCREC BENCH_REPO WORKDIR` → `split_size.txt` — [OPT-ATTEMPT-SPLIT]'s
  size on its one witness (Q2's census): `.c` bytes, `.o` bytes (`gcc -O2 -c`)
  for the original, the four `^`-free arms (`u`) and the `^` arm (`a`)
  (`../dfa/twins/mk_split.py`). `esc.py` is the `--pattern-esc` encoder.
- `run_wordwait.sh ART_DIR SUBJ_DIR` → `wordwait.txt` — `../vm/stayprobe.py`
  (unmodified, top five states) plus `wordwait.py` (per-state step totals,
  stay-run counts and mean run, the shipped stay tables' visits) on hex8-bounded,
  json-constant and dbnames over the 11 capability throughput subjects.
- `run_pairskip.sh ART_DIR CNT_DIR SUBJ_DIR TWINS_DIR` → `pairskip.txt` —
  `../dfa/twins/mk_count.py` + `stepcount.c` (today's skip-block entries,
  reproducing dfa.md §2.2's 0.146 / 0.095 / 0.067 per byte) and
  `pairskip_count.py` (the boundary-pair stop count `!(T[s[p]] & NW[s[p-1]])`
  read off the artifact's own `rx_start_bytes` and `rx_forward_seed_state`).
