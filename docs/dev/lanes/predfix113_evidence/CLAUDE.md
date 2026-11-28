# docs/dev/lanes/predfix113_evidence/ — lane predfix113's evidence

Evidence for docs/dev/lanes/predfix113_report.md. The lane applies review r113 (of the fold predfold1128) to the
predicate documents as RULED by the predicate manager (docs/dev/reviews/2026-11-27-r113-predfold1128.md). No owner
ruling is folded. Design evidence only. Nothing here rules, and no check under `make` reads it.

## Files

- `predfix113_model.py` is a STANDALONE python3 model, the successor of
  `../predfold1128_evidence/predfold1128_model.py`.
  - It LOADS predfold1128's model unchanged, up to its checks (`# ==== CHECKS128`). The older models load through it.
  - LIT113 (EXAMPLES-1) re-states the walker's spot finder: a label the sender writes is reached across the place only
    from a binding that USES the sender (`Y.a.h`), never from a label above the call in the sender's own text
    (`k.a.h`). Off, it is predfold1128's boundary ("a label directly on the call"), the other reading.
  - EXP113: a group inside an underscore group is not exported (the named list's underscore line).
  - ROWS113 (RULING-6 rows 1 and 8) and CHECKED113 (RULING-3): front-end switches, each between two readings. The
    printed reading is the default; the other is RUN by OPEN113.
  - `X113[0]` off is predfold1128 as merged: the control of CANARY113 and SWEEP113.
  - The checks: CANARY113, OPEN113 (both readings of each marked cell; the other's answers against hand regexes AND
    printed verbatim), SWEEP113 (start commit 8fa0108f9 under the control; GONE113 declarations), ERRSWEEP113,
    SPECLINES113, HAND113, MARK113 (the marker count from the start's count and the ruled sites), QUOTES113 (the
    record at the PINNED start commit), STALE113, TEXT113, SUCCESSOR113, PLANTS113.
  - SUCCESSOR113 runs predfold1128 in full (its SUCCESSOR128 re-runs predfix112 and the twenty before it, dumping their
    outputs beside it). It keys every red with predfix90's `red_key10`, declared in `predfix113_succ_decl.tsv`. A
    traceback is never declarable.
  - Its verdict is its last line, `predfix113_model: N checks, F failed`. It exits non-zero iff that line reports a
    failure.
  - Run: `timeout 6000 python3 -I -B <this dir>/predfix113_model.py` from the worktree root, with
    `PREDFIX113_SUCCDIR=DIR` (an existing EMPTY scratch directory).
    - `PREDFIX113_LIGHT=1` skips SUCCESSOR113. `PREDFIX113_READDUMP=1` reads DIR instead of re-running.
    - `PREDFIX113_WRITEDECL=F` writes the seen reds as a declaration draft.
    - `PREDFIX113_SABOTAGE=sN` plants one wrong rule, fact or text per check (PLANTS113, s1..s14). `=all` runs every
      plant, one LIGHT subprocess each; s14 reads DIR.
- `predfix113_model.out`, `predfix113_sabotage.out`: the committed runs at the delivered tip.
- `predfix113_succ_decl.tsv`: SUCCESSOR113's declarations (model, red check, class, reason, key).

## Pinned commits

This model reads git only by commit id (START113). One older model it re-runs still reads a branch by NAME:
predfold1123_model.py (`lane/pred-rev28:`); those lane files are historical and not edited.

## Known limits

- predfold1128's limits hold. The front ends are text rewrites sized to the printed programs, not a parser.
- A name the model binds at top level shadows the loaded engines' globals (a slice index named `_m2` broke the matcher
  once in this lane): the slice indices and plant names here carry the suffix 113.

Lane files are historical after merge; never edited then.
