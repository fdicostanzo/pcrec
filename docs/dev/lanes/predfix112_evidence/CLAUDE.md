# docs/dev/lanes/predfix112_evidence/ — lane predfix112's evidence

Evidence for docs/dev/lanes/predfix112_report.md. The lane applies review r112 (as ruled) to the predicate documents
and folds two owner rulings: array-gate ("error. Agree with lean") and body-own-name ("agree"; record
docs/design/plan_row_bodies/COND-FAMILY.md, 2026-11-27). Design evidence only. Nothing here rules, and no check
under `make` reads it.

## Files

- `predfix112_model.py` is a STANDALONE python3 model, the successor of
  `../predfold1127_evidence/predfold1127_model.py`.
  - It LOADS predfold1127's model unchanged, up to its checks (`# ==== CHECKS (a probe loads the model up to this
    line)`). The older models load through it.
  - BODY112 is the one patch to predfold1127's walker WALK1127 (its source text, one hook line, asserted present):
    body-own-name as asked. At each step a target directly under the step is read, and targets reached by a skip
    beside it are not counted; applied before the gate check. array-gate is predfold1127's printed side, now ruled.
  - `X112[0]` off is predfold1127's walker as merged: the control of CANARY112, SWEEP112 and READINGS112.
  - `GROUND112[0]` on models the owner's own ground for the call case: BODY112 off, and a target across an
    argument's place not counted when another target is. It is a switch for READINGS112 (b), never the rule.
  - The checks, by name: CANARY112; RULE112 (20 reads, hand verdicts citing their ruled lines, legal reads against
    hand regexes); READINGS112 (body-own-name's readings (a)-(c), his ground against the asked statement, the gate
    beside a direct target both ways); TABLE112 (the kinds table, the two rows added against the walker's node
    kinds); SWEEP112 (every printed three-mode line against the start commit 2d7718d4e under the control; GONE112
    declarations); ERRSWEEP112; SPECLINES112; STALE112; QUOTES112 (the record at the PINNED start commit); MECH112
    (MECH111's mechanically built regexes for every read made legal); SUCCESSOR112.
  - SUCCESSOR112 runs predfold1127 in full (its SUCCESSOR1127 re-runs the nineteen before it and dumps their
    outputs) and keys every red of all twenty with predfix90's `red_key10`, declared in `predfix112_succ_decl.tsv`.
    A traceback is never declarable.
  - Its verdict is its last line, `predfix112_model: N checks, F failed`. It exits non-zero iff that line reports
    a failure.
  - Run: `timeout 6000 python3 -I -B <this dir>/predfix112_model.py` from the worktree root, with
    `PREDFIX112_SUCCDIR=DIR` (an existing EMPTY scratch directory for the successor outputs: the older models read
    every `.out` in it, so a stale dump turns SUCCESSOR111 and SUCCESSOR1127 red; SUCCESSOR112 refuses a non-empty one).
    - `PREDFIX112_LIGHT=1` skips SUCCESSOR112. `PREDFIX112_READDUMP=1` reads DIR instead of re-running.
    - `PREDFIX112_WRITEDECL=F` writes the seen reds as a declaration draft.
  - `PREDFIX112_SABOTAGE=sN` plants one wrong rule, fact or text per check (PLANTS112, s1..s12). `=all` runs every
    plant, one LIGHT subprocess each; s12 reads DIR.
- `predfix112_model.out`, `predfix112_sabotage.out`: the committed runs at the delivered tip.
- `predfix112_succ_decl.tsv`: SUCCESSOR112's declarations (model, red check, class, reason, key).

## Pinned commits (review r112 COORD-1)

This model reads git only by commit id (START112). One older model it re-runs still reads a branch by NAME:
predfold1123_model.py (`lane/pred-rev28:`). In a clone without that local branch, predfold1123 QUOTES and predfix111
SUCCESSOR111 turn red and SUCCESSOR112 with them; those lane files are historical and not edited.

## Known limits

- predfold1127's limits hold (38 printed dotted reads its walker does not parse).
- The walker parses no labelled part under `?` or `*` (review r112 F4: the optional and loop counting is a marked
  reading, not run).

Lane files are historical after merge; never edited then.
