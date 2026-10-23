# tests/kitproof/ — [KIT-VERIFY] Z2's `cover` checks (`make test-kitproof`)

`docs/design/kit_proof.md` §6.3, §6.4, §7 Z2. The `cover` LOCATE row is routed
by the default build since D172 S3 (before it, only by the test harness's lever,
`PcrecHarnessOptions.kit_proof`, now inert and kept for its callers); the
artifacts here are still compiled by `build/pcrec-harness` through it, which
since S3 renders the default build's text. A `make test`
section (about 1.5 s); mech arm `kitproof` (rows S1130-S1141, S1144, S1148,
S1149).

- `run_cover.sh` — the check. Three row kinds from `cases.tsv`: `verdict` (the
  artifact's `RX_DFA_SCAN` reads `cover`, or does not), `facts` (the
  `span_facts` value `build/pcrec --emit-facts` prints), `answer`
  (`rx_search` at every startoffset and match_api.md §3.1.3's find-all loop,
  every group span, against `answers.tsv`). Every answer pattern must itself
  read `cover` (its REACH), and each row kind's population has a K35 floor
  literal (24 / 6 / 55) that a change adding rows raises.
- `cases.tsv` — the witnesses, each with the sabotage row or kit_proof clause it
  serves. The verdicts are kit_proof.md's witness list (`conj.txt` D); the facts
  values are the statements `x0.py stated` holds green against libpcre2 10.46
  (`docs/design/kit_proof/z2/out/stated_built.txt`).
- `answers.tsv` — GENERATED, do not edit: libpcre2 10.46's answers for every
  `answer` row, written by `oracle.c` through `gen_answers.sh`. Committed, so
  the check needs no libpcre2.
- `oracle.c` — the libpcre2 side: knows nothing of pcrec. An "x" in its output
  is a startoffset on a UTF-8 continuation byte (pcrec's boundary guard
  refuses it), never compared.
- `gen_answers.sh` — regenerates `answers.tsv` (checks the library is 10.46).
- `drv.c` — pcrec's side: linked with one built artifact; pre-fills the caps
  array with a sentinel before every call, so a group left unwritten is seen.
- `reach.sh` — the sabotage rows' REACH probe: does the witness, compiled
  through the lever on the CLEAN tree, read `cover`.

The lever's spelling appears in this directory, which the lever fence
(`tests/compound/run_lever_fence.sh`) allowlists for that reason.
