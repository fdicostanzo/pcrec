# tests/lookaround/d27_l3 — span_arms L3's D27 blinded witnesses

Goal-written witnesses for lookaround unit L3 (`docs/design/span_arms.md` §14.4 L3): "a positive
lookbehind's fixed bytes join the required run in front of the consumed part" (group A), dead
combinations (B) and look-alike controls (C). Written by a D27-blinded author (lane l3d27,
`docs/dev/lanes/l3d27_report.md`); every answer is libpcre2-8 10.46's. Wired like `d27_l1/` (lane l3wire).

## Files

- `l3d27_witnesses.rxt` — the 136 witnesses' ANSWERS (284 blocks, 13,722 cases, each under the default
  engine and `engine vm`); rides `test-corpus` like every `.rxt` under `tests/`. The author's file: do
  not edit (re-cut from the author's generator in scratch if it must change). Two build-side,
  comment-only edits (lane l3wire, as l1ffix did for L1): the two HEAD lines `description` and
  `oracle pcre2/10.46` are `#` comments (both words are guarded by `tests/rxtsource`'s keyword census), and
  the 28 blocks whose pattern holds non-ASCII text carry `# pcre2-only` (python `re` cannot read them);
  so verify_rxt.py cross-checks the rest (11,646 cells PASS).
- `l3d27_listing.tsv` — the author's record of each witness's LISTING per witness x encoding x config
  (def, vm, vmpf = vm + `-fprefilter`, dfa where accepted): run, K, why, `req_set_maxoff`, and
  PASS/LIMIT/INFO against the spec. The author's file: do not edit except to re-pin a moved listing
  after re-judging it.
- `l3d27_limits.tsv` — BUILD-side: the declared limit each LIMIT witness rests on (F1-F4; one plan row
  each under [REQ-LOOKAROUND]). F5/F6 (INFO: C03, C05) are sound joins and name none.
- the check itself is `../d27_l1/check_listing.py PCREC DIR` (one checker for both suites, never a
  copy); `make test-lookaround` runs it over this directory.

## Rules

- A later unit that lifts a limit turns the check red on its rows: re-judge each against the record's
  `claim`, re-pin, drop the limit row and its plan row.
