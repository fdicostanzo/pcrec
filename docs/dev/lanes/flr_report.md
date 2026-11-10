# flr / flr2 report: four emit_sweep DIFFER floors after span arms R1

## STATE AT HANDOFF

Measured with `scratch/flr/meas.py` (per-pattern differ sets, `<sha>.json`),
distinct-pattern populations 5095 / 5104 / 5126 / 5126 / 5137 (the corpus
grew: R1 added `tests/litscan/spanarms.rxt`). Deltas: `delta.json`; facts:
`facts.json`; answers: `ans.py` (all under `$PCREC_TMPDIR/scratch/flr/`).

### Counts, cell x commit

| cell | cf578177e | 4d63929cf (E1) | df9f79996 (E2) | 2d72849ed (kit 3.0a) | 6638e3679 (R1) | old pin | new pin |
|---|---|---|---|---|---|---|---|
| pick byte c-default | 143 | 144 | 140 | 140 | 87 | 142 | 87 |
| pick utf8 c-default | 228 | 229 | 216 | 216 | 139 | 224 | 139 |
| set-lead byte c-default | 15 | 16 | 13 | 13 | 6 | 14 | 6 |
| set-lead byte c-vm | 18 | 19 | 16 | 16 | 11 | 18 | 11 |
| set-lead utf8 c-default | 7 | 7 | 7 | 7 | 3 | 7 | 3 |
| set-lead utf8 c-vm | 8 | 8 | 8 | 8 | 3 | 8 | 3 |

The two utf8 set-lead cells were also over their old pins at HEAD, so they
are re-pinned too (the brief's "any other failing cell").

### Leavers and joiners by step

- E1 (4d63929cf): none left; `ab(?:c?){2}de` joined every byte cell, pick utf8 too.
- E2 (df9f79996): pick byte 5 left (`\K` and `(?m)^` shapes: `ab\Kcd`, `(?m)^a\Kb`,
  `a(?m)^b`, `(?:cat|bat)(?<=..)s`), pick utf8 14 left (same shapes plus
  `(?>a\Kb)c`, `a\K/user`, `a\Kb\Kc`, recursion-with-\K); set-lead byte 4 left
  (`ab\Kcd`, `(a)y(?=\1)z`, `(a)y(?!\1)z`, `(a)y(?*\1)z`); `ab(?:|x)cd` joined each
  byte cell. Cause (E2 not re-verified with facts by this lane, only the R1 step was):
  E2's unit changed the span choice for these \K / lookaround shapes.
- 2d72849ed (kit 3.0a): no cell moved (zero left, zero joined).
- 6638e3679 (R1): pick byte 67 left / 14 joined; pick utf8 90 / 13; set-lead byte
  c-default 9 / 2; c-vm 11 / 6; utf8 c-default 4 / 0; utf8 c-vm 5 / 0.

### The R1 mechanism (every leaver explained; none unexplained)

R1 derives a REQUIRED RUN (`req_run`, stamp `RX_REQ_RUN`) for shapes that had
none or a short one: a counted/unbounded run of one byte followed by a literal
(`a{3,5}b` none -> `aaab@3`; `a{2,}b` none -> `aab@2`; `a+b`, `(a+?)b`,
`(?>a+)b`, `a+\Kb`, recursion bodies like `(a+)b(?1)a` -> `ab@1`; counted
groups `(abc){2}x` `abc@1` -> `abcabcx@6`; `(a)(?:ab){3}?x` `ab@1` ->
`aabababx@7`; `x{2,5}(?i:cat)` `cat@0` -> `xxcat@1` (case-folded mask);
`é{2}cat` `cat@0` -> `c3a9a9cat@2`; byte `€+` `e282@1` -> `e282ac@2`). With
a required run emitted, the PRE-CHECK that the pick / set-lead deny acts on
(the `rq_set` memchr pre-check, or the set-lead start the run replaces) is
dominated: both arms emit the run, so the deny arm changes no byte. This is
the c-vm statement already in the file ("every span there is REQUIRED, which
the pick's deny cannot reach"), now true at c-default for these shapes.
Verified by `--emit-facts` on 2d72849ed vs 6638e3679 for ALL 171
(encoding, pattern) leavers: `RX_REQ_RUN` changed in every one (0 unchanged).

Ten examples (byte, RX_REQ_RUN 2d72849ed -> 6638e3679): `a{3,5}b` none ->
`61616162@3`; `a{2,}b` none -> `616162@2`; `a{3,}c` none -> `61616163@3`;
`(a+?)b` none -> `6162@1`; `a+\Kb` none -> `6162@1`; `(?>a+)b`(utf8) none ->
`6162@1`; `(a{2,3}){2,3}c` none -> `61616161@3`; `(abc){2}x` `616263@1` ->
`61626361626378@6`; `x{2,5}(?i:cat)` `434154@0/dfdfdf` ->
`7878434154@1/ffffdfdfdf`; `€{1,2}` `e282@1` -> `e282ac@2`. Remaining
leavers group as: a-run + literal (the largest group: `a{n,m}b`, `a+b`,
`a{2,}?b`, possessive/atomic/lazy forms), a-run + literal inside a group /
assertion / recursion (`(?=(a+)b)a+b`, `(a+)b(?1)a`, `(?m)^a+b`),
counted groups (`(abc){2}x`, `(a)(?:ab){3}?x`, `z(?:ab){3,}?c?`), `\K` forms
(`a+\Kb`, `(a\K)+b`), and multibyte (`€+`, `😀{1,2}`, `é{2}cat`).

Joiners (R1): counted repeats that now carry a run so the pick has a second
candidate and its deny moves a byte: `a{500}`, `a{50,60}`, `a{200,500}(?)`,
`(a{10,20}){10,50}`, `(ab){300}`, `(?:abc){20}`, `xy(?:ab){1,2}zw`,
`ab{2,3}c`, `(a)(?:ab){2,}?c` (run -> 8-byte cap `61616161...@7` or longer);
plus corpus growth: `(?:a.){10}.?xyz`, `(a.){10}xyz`, `(?:abc){20}`,
`xy(?:ab){1,N}zw`, `a{2,4}\Kb.c` are new rows of `spanarms.rxt`
(`(a.){10}xyz`: RX_REQ_RUN unchanged `xyz@2`, the deny now removes a
`rq_set {97}` memchr pre-check because `req_pieces` declines `one-group`).

### Answers

For all 171 leaver (encoding, pattern) pairs, matchers compiled with
`--emit-main` at 2d72849ed and 6638e3679 (`--features all`, `-e` per cell),
about 150 subjects each (random strings over the pattern's letters, runs of
each letter with and without trailing b / leading x...c): 26,370 subject
runs, byte-identical output on every one, 0 differences.

### Witnesses (tuple third field)

pick byte and utf8 `a.{1,5}z`: in the HEAD differ set of both, kept.
set-lead witnesses `x{2,5}(?i:cat)`, `é{2}cat`, `a{3}(?i:cat)` LEFT at R1 (their
runs now dominate), so all four set-lead cells are re-aimed to
`(?i:select)\d+x`: present in the differ set of all four cells at HEAD and a
member at every one of the five commits (never a leaver or joiner).

### Re-pin and commit

`scripts/emit_sweep.py` DIFFER_PINS: pick 87 / 139, set-lead 6 / 11 / 3 / 3,
stamp floors 0, cause comments naming R1 (f7eb10528) and this file. Commit on
lane/flr: "flr2: re-pin four emit_sweep DIFFER floors to HEAD (span arms R1)".

### Floor check OWED

`python3 scripts/emit_sweep.py --tree $S/6638e3679 --bin .../build/pcrec
--ref-bin .../build/pcrec --arms start` (S = `$PCREC_TMPDIR/scratch/flr`), queued
behind the box lock label `flr2`; log `scratch/flr/floor.log`. Completion line
is the script's final verdict; any other failing cell is to be re-pinned.
