# docs/dev/lanes/predfold1128_evidence/ — lane predfold1128's evidence

Evidence for docs/dev/lanes/predfold1128_report.md. The lane folds five owner rulings (gate-beside-direct,
carve-out-reading, caller-label-export, named-list-use, param-reference) and the owner's STRONG LEAN
no-path-through-argument, applied and marked, into the predicate documents (record
docs/design/plan_row_bodies/COND-FAMILY.md, 2026-11-27). Design evidence only. Nothing here rules, and no check
under `make` reads it.

## Files

- `predfold1128_model.py` is a STANDALONE python3 model, the successor of
  `../predfix112_evidence/predfix112_model.py`.
  - It LOADS predfix112's model unchanged, up to its checks (`# ==== CHECKS112`). The older models load through it.
  - PLACE128 patches the walker's spot finder `_between`: a spot whose chain crosses an argument's place is dropped
    unless the place is listed (the door), or it is a label the sender writes and the step's start is neither the
    call nor a label right on it. `MODE128` switches the unasked readings (`A` printed, `A0`, `A2`); `SENT128` is
    sent-over-body-label's other reading. Neither switch is the printed rule.
  - MSG128 re-words a refusal caused by the place rule (it names the rule and the ways in).
  - The front ends: NAMED128 (named-list-use: the demand at the call, through a forwarding body, a never-satisfiable
    definition), REF128 (param-reference: the head's list, lines 2-4), WDPG128/MINI128 (the weekday program: a
    regex built mechanically from the bindings' text; python's `datetime` stands in for the planned `weekday_of`).
  - MECHROUTE128: a read whose walk crosses a place is answered by MECH111 (python `re` on the regex built from the
    program text, the walker's target named), never by the loaded engine, whose path rules predate the place rule.
  - `hits`' provided body is read from library.md as now printed (the list under `hit`) for the walker; the loaded
    engines keep the old body, answer-identical (READINGS128 runs both).
  - `X128[0]` off is predfix112 as merged: the control of CANARY128, READINGS128, SWEEP128 and MECH128.
  - The checks: CANARY128, RULE128 (28 reads, hand verdicts, legal reads against hand regexes), READINGS128,
    OPEN128 (each unasked question, both readings), NAMED128, REF128, WEEKDAY128 (against
    `../predbang_evidence/weekday.out`), TABLE128 (the kinds table's cells against walker runs), SWEEP128 (start
    commit 8e7cca4a9 under the control; GONE128 declarations), ERRSWEEP128, SPECLINES128, STALE128, MARK128 (the
    marker phrase counted, each moved line marked), MECH128, QUOTES128 (the record at the PINNED start commit),
    SUCCESSOR128, PLANTS128.
  - SUCCESSOR128 runs predfix112 in full (its SUCCESSOR112 re-runs the twenty before it and dumps their outputs)
    and keys every red with predfix90's `red_key10`, declared in `predfold1128_succ_decl.tsv`. A traceback is never
    declarable.
  - Its verdict is its last line, `predfold1128_model: N checks, F failed`. It exits non-zero iff that line reports
    a failure.
  - Run: `timeout 6000 python3 -I -B <this dir>/predfold1128_model.py` from the worktree root, with
    `PREDFOLD1128_SUCCDIR=DIR` (an existing EMPTY scratch directory).
    - `PREDFOLD1128_LIGHT=1` skips SUCCESSOR128. `PREDFOLD1128_READDUMP=1` reads DIR instead of re-running.
    - `PREDFOLD1128_WRITEDECL=F` writes the seen reds as a declaration draft.
    - `PREDFOLD1128_SABOTAGE=sN` plants one wrong rule, fact or text per check (PLANTS128, s1..s18). `=all` runs
      every plant, one LIGHT subprocess each; s18 reads DIR.
- `predfold1128_model.out`, `predfold1128_sabotage.out`: the committed runs at the delivered tip.
- `predfold1128_succ_decl.tsv`: SUCCESSOR128's declarations (model, red check, class, reason, key).

## Pinned commits

This model reads git only by commit id (START128). One older model it re-runs still reads a branch by NAME:
predfold1123_model.py (`lane/pred-rev28:`); those lane files are historical and not edited.

## Known limits

- predfix112's limits hold. The walker parses no label parameter (`Rs(l:, v)`): sent-over-body-label is run by
  the engine and the SENT128 switch only.
- MECHROUTE128 answers one read with a digit-range condition; other crossing reads stay the engine's.
- The front ends are text rewrites sized to the printed programs, not a parser.

Lane files are historical after merge; never edited then.
