# docs/dev/lanes/k73utf_evidence/ — K73's oracle transcripts and census

Lane k73utf, 2026-09-29. All of it is evidence for `../k73utf_report.md`.

- `pr2.c`, `probe.sh`, `k73_witness_10.46.txt`: the libpcre2 10.46 probe
  (PCRE2_UTF|PCRE2_MATCH_INVALID_UTF, start 0, plus a PCRE2_ANCHORED arm)
  and its transcript. The source of every cell in
  `tests/utf8/k73_startskip.rxt` and of the seven K73 rows in
  `tests/utf8/run_startbnd_diff.sh` §5.
- `pr3.c`, `k73_mc_findall_10.46.txt`: the match_api §3.1 find-all
  protocol driven through libpcre2 10.46. It gives the `mc` counts for
  `mc_illformed_utf8.rxtin` and finding F2's `a` over `a\x80a`.
- `k73_census.py`, `k73_census.out`: the emitted-C mover census, branch
  point vs fix, over every distinct corpus pattern under byte / utf8 /
  utf8-vm.
