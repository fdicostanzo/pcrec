# docs/dev/lanes/predfold1129_evidence/ — lane predfold1129's evidence

Evidence for docs/dev/lanes/predfold1129_report.md: the fold of seven owner rulings of 2026-11-28 (record
docs/design/plan_row_bodies/COND-FAMILY.md, reference-example-checked to same-path-last) into the predicate
documents. Design evidence only. Nothing here rules, and no check under `make` reads it.

## Files

- `predfold1129_model.py` is a STANDALONE python3 model, the successor of `../predfix113_evidence/predfix113_model.py`.
  - It LOADS predfix113's model unchanged, up to its checks (`# ==== CHECKS113`). The older models load through it.
  - GATE129 is its own walker, written from the ruled statements (every crossing a gate, never skipped; stacked labels
    one spot's names; the last placement; one full path or an error naming both). MECH129 builds a python `re`
    mechanically from the parsed program text for a read the loaded engine refuses. `X129[0]` off is predfix113 as
    merged: the control of the census and SWEEP129.
  - `_part129` is the front end for a path placed in a pattern (part-of-argument). RESPELL129 lists the programs the
    reader cannot parse, each with a hand-judged same-meaning spelling the engine runs (named in the report).
  - The checks: RULE129 (30 programs, verdicts and texts typed from the record), CENSUS129, SWEEP129 (start commit
    43bbce01f under the control; declarations in `predfold1129_decl.py`), ERRSWEEP129, MARK129, QUOTES129 (the
    record at the PINNED start commit), STALE129, PART129 (hand regexes), OTHER129 (each open reading, both run),
    SUCCESSOR129, PLANTS129.
  - SUCCESSOR129 runs predfix113 in full (its SUCCESSOR113 re-runs predfold1128 and the 21 before it, dumping their
    outputs beside it). It keys every red with predfix90's `red_key10`, declared in `predfold1129_succ_decl.tsv`. A
    traceback is never declarable.
  - Its verdict is its last line, `predfold1129_model: N checks, F failed`. It exits non-zero iff that line reports a
    failure.
  - Run: `timeout 6000 python3 -I -B <this dir>/predfold1129_model.py` from the worktree root, with
    `PREDFOLD1129_SUCCDIR=DIR` (an existing EMPTY scratch directory).
    - `PREDFOLD1129_LIGHT=1` skips SUCCESSOR129. `PREDFOLD1129_READDUMP=1` reads DIR instead of re-running.
    - `PREDFOLD1129_WRITEDECL=F` writes the seen reds as a declaration draft.
    - `PREDFOLD1129_CENSUS=1` prints the census and exits 0.
    - `PREDFOLD1129_SABOTAGE=sN` plants one wrong rule, fact or text per check (PLANTS129, s1..s15). `=all` runs
      every plant, one LIGHT subprocess each; s15 reads DIR.
- `predfold1129_census.out`: the census of the documents AT the start commit 43bbce01f: every program printed on a
  three-mode or compile-error line of the six documents, the in-force engine against GATE129. A first version was
  committed before any document edit (99c49e22f); the committed one is from GATE129 as delivered.
- `predfold1129_decl.py`: SWEEP129's declarations (a printed program the lane moved or dropped, and why).
- `predfold1129_succ_decl.tsv`: SUCCESSOR129's declarations (model, red check, class, reason, key).
- `predfold1129_model.out`, `predfold1129_sabotage.out`: the committed runs at the delivered tip.

## Pinned commits

The model reads git only by commit id (START129 = 43bbce01f). One older model it re-runs still reads a branch by
NAME: predfold1123_model.py (`lane/pred-rev28:`); those lane files are historical and not edited.

## Known limits

- The reader parses no label parameter, `occurrences` call, `rx.repeat` or map form: those programs go to the
  loaded engine (the census counts them as not parsed).
- `_part129` specializes a macro whose body places a path of its parameter at a call with a bare binding argument
  only; MECH129 refuses holes, atomics, lookarounds, backreferences and conditions that are not one read.
- A number with a leading zero is no number (the documents' `042xx` FAILS); PART129's hand regexes follow it.
- Reads printed in bullet prose (not on a three-mode or compile-error line) are not swept.

Lane files are historical after merge; never edited then.
