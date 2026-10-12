# docs/dev/optloop/matchsplit/ — `[MATCH-SPLIT]` STEP 0, the survey's instruments and outputs

Lane `mssurvey` (2026-10-12, sonnet). The survey `docs/design/match_split_requirements.md` section 6
designs, RUN: COMPILE-ONLY (no clock, no timing); one counted-work arm (a load COUNT, `qwork.py`).
The reading is `../../lanes/mssurvey_report.md`; the verbatim outputs are `summary.txt`, `qwork.txt`,
`oracle.txt`, `c4.txt` and `ms_rows.tsv.gz`. Reproduction (box: the Linux dev box, `make -j4` at most):

    make -j4 && gcc -O1 -Ilib -Isrc -o build/ms/msprobe docs/dev/optloop/matchsplit/msprobe.c build/libpcrec.a
    PCREC=build/pcrec PROBE=build/ms/msprobe BENCH=/home/pcrec/projects/pcrec-bench CORPUS=$PWD \
      OUT=build/ms/out JOBS=3 python3 docs/dev/optloop/matchsplit/survey.py
    python3 docs/dev/optloop/matchsplit/analyze.py build/ms/out/ms_rows.tsv.gz > summary.txt
    python3 docs/dev/optloop/matchsplit/c4check.py build/ms/out/ms_rows.tsv.gz        # + --plant ml_edge|look_end: must be red
    python3 docs/dev/optloop/matchsplit/msoracle.py build/ms/out/ms_rows.tsv.gz       # libpcre2 10.46: C2, C3, C-RT
    PCREC=build/pcrec CORPUS=$PWD python3 docs/dev/optloop/matchsplit/qwork.py build/ms/out/ms_rows.tsv.gz build/ms/qw

## Files

- `msprobe.c` — links `libpcrec.a` and drives the REAL parser (revend_probe.c's recipe). Dumps the RAW parse
  tree as JSON (CAT/ALT spines flattened) and carries a COPY of `src/facts/endwin.c`'s `ew_walk` (the
  shipped end-anchor walk), cross-checked by `analyze.py` C1 against the shipped `end_pin` fact.
- `msclass.py` — section 2.2's path-class analysis over that dump: the summary of a node is the set of
  (start pins, end pins, consumption, leads-with-unbounded-repeat) over its live paths; absolute pins on a
  consumed path are DEAD, line pins away from the path's edge are landmarks; anchors in lookarounds are counted
  and unclassified; a structural redundancy check; and the unparse that yields the FREE (no pin) and END
  (has an end pin) sub-language texts the survey compiles on their own. `PLANT` carries C4's two defects.
- `survey.py` — populations (bench, corpus + D27 flag, catalog, idioms, planted), the compiles (cached in
  `compile_cache.jsonl` under OUT; stamps read from `--emit-facts`' decisions section, `start_max` from one
  `-o -` compile), prior masses from `src/findings/default.rxt`, the TSV.
- `analyze.py` — the section 6.4 counts and the C1/C5 controls. Verbatim output: `summary.txt`.
- `msoracle.py` — libpcre2 10.46 controls that share no source with pcrec: C2 (pin-only rows' matches satisfy a
  live path's pins), C3 (the free/end texts match only where the full pattern does), C-RT (the unparse is
  language-identical). `--selftest` plants a wrong class: it must go red.
- `c4check.py`, `planted.txt` — C4 planted classes (35 witnesses, expected label + flag).
- `idioms.txt` — the real-world idioms added by this survey (section 6.1.3), hand-written, which is a bias.
- `qdrv.c`, `qwork.py` — (d): the counted-work arm. The artifact compiled `-O0 -fsanitize=kernel-address`
  with call-per-load hooks counts subject-byte loads of a whole find-all; no clock.
- `summary.txt`, `qwork.txt`, `oracle.txt`, `c4.txt`, `ms_rows.tsv.gz` — verbatim outputs / the per-pattern TSV
  (pattern bytes as hex, the three sub-language texts as hex, every stamp read).

Regenerating `ms_rows.tsv.gz` moves every number in the report.
