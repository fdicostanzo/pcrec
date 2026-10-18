# docs/dev/lanes/b3b/ — lane b3b's delivery pieces (R17-b′ B3b)

The pieces `../b3b_report.md` cites; the lane's voice, historical once merged.

- `proposed/entry_use.diff` — the MAIN-SIDE adoption of `MF_USE_ENTRY` (DELEG_SITES PRE's use
  ceiling, `check_use`/`deleg_check`, `emit_dfa.c` stating `s->use = MF_USE_ENTRY`, the deleg
  sed plant) as a PROPOSED diff for main's review; `git apply --check` clean at the lane tip.
- `chain.sh` — the OWED heavy validation (build/strict, make test via perfrun, mech rows solo,
  G2 full, N2 census + floor propose, memfn reach arm, form census, B3b's own censuses). The kit
  manager arms it in a slot at a pinned tip; verdict = the last line of `chain.status`,
  `^CHAIN (COMPLETE|FAILED)`.
- `mech_rows.txt` — the mech rows `chain.sh` runs solo (sabotage_anchors.py `--step` over
  c88537116..tip, plus the kit/test-edit/suite-derived rows and B3b's new and re-aimed rows).
- `mech_score.sh` — the scorer (copied from the b3a heavy slot): verdict from a row's own
  COMPLETE trailer against its declared SAB_EXPECT.
