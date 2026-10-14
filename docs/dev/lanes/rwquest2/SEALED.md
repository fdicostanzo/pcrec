# rwquest2 — SEALED RESERVE (second blinded question list, "j1b")

Lane `rwquest2` (sonnet), sealed 2026-10-14. The CONTENT of the question list is
WITHHELD: only its hash is committed. The file lives at
`worktrees/.corpus/sealed/j1b_questions.tsv` (gitignored, beside the corpus) and
must not be read by anyone judging the decision table until the table is frozen.

- file: `j1b_questions.tsv`
- sha256: `f41abc634bad5e498726b5fbe14a1b379ba8fbdb6fac185f541057bd631b32fe`
- rows: 165 (plus one header line, 166 lines total)
- per class: logs 24, code 26, prose 23, structured 23, markup 24, nonenglish 23, binary 22
- column header (tab-separated, in this order):
  `id class files intent pattern flags mode freq_guess py_status py_matches py_mib py_per_mib py_equiv_pattern`
- id form: `J1B-<LOG|COD|PRO|STR|MKP|NON|BIN>-NN`
- the check script beside it (`j1b_build.py`) regenerates the file byte-identically
  (hash verified on two runs); `j1b_pcre2_compile.py` only checks that every pattern
  compiles under libpcre2-8 with its flags.

The list is independent of the first list (`rwquest`): its files were not read.
Statement: the question content is withheld from this commit, from the report and
from the handback; verify a later reveal against the sha256 above.
