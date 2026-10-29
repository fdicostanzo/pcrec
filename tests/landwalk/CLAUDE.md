# tests/landwalk — the landmark walk's answer net

[LANDWALK] stage 1 (lane p1build, 2026-10-29): the `landmark-walk` LOCATE row
(`docs/spec/tuning.md` §2.54, `RX_DFA_SCAN "landmark-walk"`).

## Files

- `landwalk.rxt` — the answer net, GENERATED from libpcre2 10.46's answers
  (every block `# pcre2-only`); rides `test-corpus` like every module corpus,
  and the axes sweep runs it under `-fno-landmark-walk`/`-fno-anchored-dfa`.
  Families W (the walk), R (the reach guard), B (word context, lookbehind),
  U (utf8), D (declines). Never hand-edit: re-generate.
- `gen_landwalk.py` — writes `landwalk.rxt` from the oracle
  (`tests/fuzz/pcre2_oracle.c`); re-check with `tests/revend/verify_stage2.py`
  (shares no code with the generator). Usage in its header.
- `card_lwalk.sh` — the walk's measurement card ([LANDWALK-CARD]): `lwhit`
  (wlen 2/8/32, miss and hit arms, with the `lwfit` a + b*wlen), `lwcall`;
  walkbytes against one forward DFA step measured in the same run;
  instructions beside. `--timed` only in a cleared window, else every row is
  UNMEASURED; `--smoke` runs in run_landmark_walk.sh §4.

## Pointers

The STRUCTURAL checks (which patterns walk, the deny both ways, the reach
guard as a cost) are `tests/codegen/run_landmark_walk.sh` (mech arm
`landwalk`); the size-cap rung is `tests/codegen/run_fallback_table.sh`
(`seq-lwdrop`, `seq-lwref`, `att-sclw`); sabotages S1820-S1829. Design:
`docs/dev/lanes/p1dsg3_report.md`, `docs/dev/lanes/p1build_report.md`.
