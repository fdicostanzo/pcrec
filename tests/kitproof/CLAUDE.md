# tests/kitproof/ — [KIT-VERIFY] Z2's `cover` checks (`make test-kitproof`)

`docs/design/kit_proof.md` §6.3, §6.4, §7 Z2. The `cover` LOCATE row is routed
by the default build since D172 S3 (before it, only by the test harness's lever,
`PcrecHarnessOptions.kit_proof`, now inert and kept for its callers); the
artifacts here are still compiled by `build/pcrec-harness` through it, which
since S3 renders the default build's text. A `make test`
section (about 4 s); mech arm `kitproof` (rows S1130-S1141, S1144, S1148,
S3220-S3226, S3234; S1149 retired with the span slice, `docs/design/cover_cap.md` §5.4).

- `run_cover.sh` — the check. Three row kinds from `cases.tsv`: `verdict` (the
  artifact's `RX_DFA_SCAN` reads `cover`, or does not), `facts` (the
  `cover` section row `build/pcrec --emit-facts` prints, `why|k|exact_len|sets`,
  `docs/spec/facts_listing.md` §4.5; the loader tracks the `#section` line and
  keys the row on the encoding), `answer`
  (`rx_search` at every startoffset and match_api.md §3.1.3's find-all loop,
  every group span, against `answers.tsv`). Every answer pattern must itself
  read `cover` (its REACH), and each row kind's population has a K35 floor
  literal (60 / 21 / 140 since stage 2 B7, lane covs2g) that a change adding rows raises. Also runs
  `width_opt.c` (the library side of `window_search_width`).
- `cases.tsv` — the witnesses, each with the sabotage row or kit_proof clause it
  serves. The verdicts are kit_proof.md's witness list (`conj.txt` D) and
  `cover_cap.md` §5.3's; the facts values are the records `x0.py stated` holds
  green against libpcre2 10.46 (`cover_cap.md` §3.6 Q2).
- `answers.tsv` — GENERATED, do not edit: libpcre2 10.46's answers for every
  `answer` row, written by `oracle.c` through `gen_answers.sh`. Committed, so
  the check needs no libpcre2.
- `oracle.c` — the libpcre2 side: knows nothing of pcrec. An "x" in its output
  is a startoffset on a UTF-8 continuation byte (pcrec's boundary guard
  refuses it), never compared.
- `gen_answers.sh` — regenerates `answers.tsv` (checks the library is 10.46).
- `drv.c` — pcrec's side: linked with one built artifact; pre-fills the caps
  array with a sentinel before every call, so a group left unwritten is seen.
- `loader.sh` — sourced by `run_cover.sh` and `reach.sh`: the ONE reading of a
  FLAGS/PATTERN pair ([COVER-CAP] stage 2, `cover_cap.md` §11.6.2; fails loud on an unknown FLAGS letter or a malformed `width=N`): the `W`, `N`
  letter, `@D`/`@D1`/`@LD`/`@LD1` and verdict `width=N`, read from
  `--list-limits` and failing loud on a missing row.
- `width_opt.c` — `window_search_width` through the library: refusal out of
  range, legal edges, and the field moving the route (`[0-9a-f]{24}` at 24/23).
- `reach.sh` — the sabotage rows' REACH probe: does the witness, compiled
  through the lever on the CLEAN tree, read `cover`; with `--facts`, does the
  clean tree's `cover` record equal the row's VALUE (a facts-value plant);
  with `--why`, one more line `REACH-WHY=[ID]`, the listing's `why`, which the
  rows pin so a witness is tied to the conjunct its plant moves (review r9 CHECKS-1).

The lever's spelling appears in this directory, which the lever fence
(`tests/compound/run_lever_fence.sh`) allowlists for that reason.
