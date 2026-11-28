# docs/dev/lanes/predfix114_evidence/ — lane predfix114's evidence

Evidence for docs/dev/lanes/predfix114_report.md: review r114's ruled dispositions applied to the predicate
documents, with the owner's correction on stacked labels, his answer on list-over-label, and the rulings
list-opens-one-step, a list that passes nothing and branch-in-loop (record docs/design/plan_row_bodies/COND-FAMILY.md,
the 2026-11-28 entries). Design evidence only. Nothing here rules, and no check under `make` reads it.

## Files

- `predfix114_model.py` is a STANDALONE python3 model, the successor of `../predfold1129_evidence/predfold1129_model.py`.
  - It LOADS predfold1129's model unchanged, up to its checks (`# ==== CHECKS129`). The older models load through it.
  - It amends the walker GATE129 and the entry `prog` (switch `X114[0]`; off is predfold1129 as merged, the control):
    ORDER114 (stacked labels are ordered steps), INCALL114 (a path naming a call's gate is inside the call), TWIN114
    (a body placing a name twice, or reading before its only placement, answered as its explicit-label twin), SENTINL114
    (a sent label inlined at the call), LIST114, LOOP114, BRANCH114/NAMEBOTH114, LOUD114 (a crash is never a refusal; a
    fallback refusal is prefixed `FALLBACK114:`). The docstring names each.
  - The checks: RULE114 (65 programs, verdicts typed from the ruled words, including predfold1129's RULE129 rows the
    correction left), TWIN114, LOUD114, SWEEP114 (start commit b935b91b6 under the control; declarations inline),
    ERRSWEEP114, QUOTES114 (record pinned at 4b2a952b3), STALE114 (search strings from the record's own REVISES /
    REVERSES / WITHDRAWN / IN DOUBT sentences), TAGS114, OTHER114 (each open reading, both run), SUCCESSOR114, PLANTS114.
  - SUCCESSOR114 runs predfold1129 in full (its SUCCESSOR129 re-runs predfix113 and the 22 before it, dumping their
    outputs in a subdirectory). It keys every red with predfix90's `red_key10`, declared in `predfix114_succ_decl.tsv`. A
    traceback is never declarable.
  - Its verdict is its last line, `predfix114_model: N checks, F failed`. It exits non-zero iff that line reports a
    failure.
  - Run: `timeout 12000 python3 -I -B <this dir>/predfix114_model.py` from the worktree root, with
    `PREDFIX114_SUCCDIR=DIR` (an existing EMPTY scratch directory).
    - `PREDFIX114_LIGHT=1` skips SUCCESSOR114. `PREDFIX114_READDUMP=1` reads DIR instead of re-running.
    - `PREDFIX114_WRITEDECL=F` writes the seen reds as a declaration draft.
    - `PREDFIX114_SABOTAGE=sN` plants one wrong rule, fact or text (PLANTS114, s1..s18). `=all` runs every plant, one
      LIGHT subprocess each; s18 reads DIR.
- `predfix114_succ_decl.tsv`: SUCCESSOR114's declarations (model, red check, class, reason, key).
- `predfix114_model.out`, `predfix114_sabotage.out`: the committed runs at the delivered tip.

## Pinned commits

The model reads git only by commit id (START114 = b935b91b6, REC114 = 4b2a952b3). One older model it re-runs still
reads a branch by NAME: predfold1123_model.py (`lane/pred-rev28:`); those lane files are historical and not edited.

## Known limits

- A loop in a body (`(rx SEQ ";"){2}`) is rewritten to a hole by the older reader; its labels are not modelled (r114
  F22). Only `rx.repeat` over a top-level `|` of labelled branches is modelled (branch-in-loop).
- `$rx.g` in a body is refused by the evidence engine (r114 F23).
- `[(=g) = rx]` over a labelled argument goes to the in-force engine and is refused `FALLBACK114:` (r114 F24).
- The walker parses no named list: the named-list lines are the in-force engine's (r114 F12).
- A group question over a number (`@0`) is beyond the reader and goes to the in-force engine.
- A list that passes nothing is recognised only over a literal (`[(=) = [L = /.../]]`, `[(=) = /.../]`).
- A body that reads `p.` bare AND is read through the list from outside in one program is not modelled.
- 49 printed compile-error lines are FALLBACK114 refusals (the in-force engine's reason, loud).

Lane files are historical after merge; never edited then.
