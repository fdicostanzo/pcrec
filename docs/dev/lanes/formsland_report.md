# formsland report (sonnet, 2026-11-17)

## Summary

Merged lane/memfn-formsfixa and lane/memfn-formsfixb into lane/memfn-forms, applied the doc lines each lane left
for the other, validated locally. One merge conflict (history index, docs only). F15's arm-I zero-loop assertion is
NOT in cards.py (see below). Movers 0.

## Merges

- formsfixa: fast-forward-style merge, no conflict (6918cc35c).
- formsfixb: one conflict, `docs/dev/history/claude_md/docs__dev__lanes.md` (both lanes appended an index line at
  the same spot). Kept both lines (0ac0677df). No code conflict.
- Doc lines applied (de21b8d4c): cli/CLAUDE.md option (12) "N decimal digits only, 0..MF_SPAN_HEAD_MAX (memfn.h,
  MF_WREACH - 1)"; memfn/tests/CLAUDE.md `run_g2_win.sh` line (~150 s, pointer to NOTES.md for env and plants S3280-S3284,
  trimmed to hold the 12 KB limit; NOTES.md already carries the detail); r45_reply.md §3 "The twins" (derived,
  R1, 32 / 32 / 1024 before the raise); window.c span-forms comment ("WIDE includes the empty set") and
  `wf_loop_len` comment (minimum of two DERIVED, rev 7 §3). Comments only.
- F15: cards.py has NO assertion that arm I has zero loops (grep for loops/zero finds none). Not added: it is a
  code change in cards.py; owed to the kit manager (formsfixa's note: an assertion in `dry`/`run` over arm I's artifacts).

## Validation

All local, niced, -j4, gnutimeout; logs in the lane scratch dir (scratch/memfn/formsland/).
- make strict rc 0; make test-codegen rc 0; test-registry rc 0; test-rxtsource rc 0; test-memfn-finder rc 0;
  test-memfn-link rc 0; test-resource rc 0.
- make test-memfn-g2 (quick, G2_JOBS=4): rc 0, checks passed 70358673, failed 0 (16 min).
- cards.py selftest: 37 checks, 0 failed. "(F2) noise drill, normal launches sigma 1 %: P(h* != 64) = 0.033 over
  300 trials (accept <= 0.05)"; "(F2) noise drill, t(5) launches: P = 0.027"; "(F3) unimodal drill, t(5) launches:
  void rate 0.020 of nights, 0.00017 of cells over 300 nights (accept <= 0.05)".
- cards.py dry (`WIDTH_FLAG=none`, `--quick`): cells 1374, built and gated 1374, failures 0; distinct compiles 269.
  (Without WIDTH_FLAG=none every cell fails: this tree has no width option; not a defect.)
- emit_sweep --ref 7506bca30: DONE rc 0, movers 0 on every stream, argv population 7071.

## STATE AT HANDOFF

Branch lane/memfn-forms, tip = the commit carrying this report (see git log). Rulings file empty (no entries).
OWED: none
