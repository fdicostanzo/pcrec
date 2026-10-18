# docs/dev/lanes/b3b/ — lane b3b's delivery pieces (R17-b′ B3b)

The pieces `../b3b_report.md` cites; the lane's voice, historical once merged.

- `proposed/entry_use.diff` — the MAIN-SIDE adoption of `MF_USE_ENTRY` (DELEG_SITES PRE's use
  ceiling, `check_use`/`deleg_check`, `emit_dfa.c` stating `s->use = MF_USE_ENTRY`, the deleg
  sed plant) as a PROPOSED diff for main's review; `git apply --check` clean at the lane tip.
- `chain.sh` — the OWED heavy validation (build/strict, make test via perfrun, mech rows solo,
  G2 full, N2 census + floor propose, memfn reach arm, form census, B3b's own censuses). The kit
  manager arms it in a slot at a pinned tip; verdict = the last line of `chain.status`,
  `^CHAIN (COMPLETE|FAILED)`.
- `mech_rows.txt` — the mech rows `chain.sh` runs solo, DERIVED by `derive_rows.sh` (its header
  names the tip and the four parts' counts); `chain.sh` refuses at arm time any line that is not
  `^S[0-9]+$` (b3brev finding 1: the first list carried a bare `S`).
- `derive_rows.sh` — writes `mech_rows.txt`: sabotage_anchors.py `--step` over c88537116..HEAD,
  rows anchored in an edited memfn/ or tests/ file or detected by a changed suite, the judged
  rows, and the rows the branch adds or re-aims.
- `mech_rows_judged.txt` — the first list's judged kit/test/suite rows (103 ids, its bare `S`
  removed), `derive_rows.sh`'s part (c).
- `reach_chain.sh` — lane b3breach's OWED heavy pair (2026-10-18): the full N2 census + `n2_report.py
  --floors --propose` and the FULL axes-pres pass, in its own `git worktree add --detach` scratch at a
  pinned tip, every step bounded by gnutimeout and a 00:25 deadline; verdict = the last line of its
  `chain.status`, `^CHAIN (COMPLETE|FAILED)`.
- `mech_score.sh` — the scorer (copied from the b3a heavy slot): verdict from a row's own
  COMPLETE trailer against its declared SAB_EXPECT.
