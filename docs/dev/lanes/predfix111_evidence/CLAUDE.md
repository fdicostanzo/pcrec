# docs/dev/lanes/predfix111_evidence/ — lane predfix111's evidence

Evidence for docs/dev/lanes/predfix111_report.md. The lane applies review r111 as the manager ruled it
(docs/dev/reviews/2026-11-27-r111-predfold1125.md) and folds the owner's rulings group-node and peek-name into the
predicate documents. This is design evidence only. Nothing here rules, and no check under `make` reads it.

## Files

- `predfix111_model.py` is a STANDALONE python3 model, the successor of
  `../predfold1125_evidence/predfold1125_model.py`.
  - It LOADS predfold1125's model unchanged, up to its first check (`unit11("CANARY", `). The older models load
    through it.
  - WALK111 is a new path walker, written from the label-kind table of core/labels/rule/kinds (KINDS111, one row
    per kind, columns start / middle step / skippable / crossed from outside / exports). It judges every read of a
    parsed program. A legal read whose route names a part used alone, a macro call used alone or a named group of
    rx text is RELABELLED before the loaded engine answers it: each such node becomes a written label
    (`[q__1 = Q]`; a group at the top of its literal its part label) and the read the full path. No loaded rule is
    patched (review r111 F24).
  - The owner questions left open are SWITCHES (READ111): gate-twice-scope (`a` definition-wide, `b` under the
    read's prefix, printed `b`) and gate-beside-label (`i` an error, `ii` the gated targets not counted, printed,
    `iii` the last mention). Every reading is RUN.
  - FE111, the marked readings as text rewrites: `!` on a lookaround in rx text; `^c` / `!^c` on a condition;
    `when` with a condition test (its body READ from library.md); a label set only inside `!^A`; a group's whole
    name from a parameter (label-needs-mark); `.index` of a label inside one of two or more alternatives.
  - MECH111 builds a python `re` regex MECHANICALLY from a program's text and its bindings' bodies (the read's
    target group named, its condition laid on it), never from the engine.
  - `X111[0]` off is predfold1125's builder alone: the control of CANARY111 and SWEEP111.
  - The checks, by name: CANARY111; TABLE111 (the document table against KINDS111); GRID111 (28 reads, hand-filled
    verdicts each citing its ground, legal reads against MECH111); READ2, READ3 (the two owner questions);
    GROUPNODE (the record entry's readings (a)-(e), and every printed underscore group); MARKED111 (against
    regexes written from the sentences); SWEEP111 (every printed three-mode line; the starting commit cec257072
    under the control; declarations GONE111); ERRSWEEP111 (MSG111; F25's message); SPECLINES111 (every new printed
    line read and as printed); STALE111; QUOTES111 (the record at the PINNED starting commit); SUCCESSOR111.
  - SUCCESSOR111 runs predfold1125 in full (its SUCCESSOR11 re-runs the seventeen before it and dumps their
    outputs) and keys every red of all eighteen with predfix90's `red_key10`, which carries the red's own FAIL
    line and no document line numbers. Each red is declared in `predfix111_succ_decl.tsv`. A traceback is never
    declarable.
  - Its verdict is its last line, `predfix111_model: N checks, F failed`. It exits non-zero iff that line reports
    a failure.
  - Run: `timeout 6000 python3 -I -B <this dir>/predfix111_model.py`, with `PREDFIX111_SUCCDIR=DIR` (an existing
    scratch directory for the successor outputs).
    - `PREDFIX111_LIGHT=1` skips SUCCESSOR111. `PREDFIX111_READDUMP=1` reads DIR instead of re-running.
    - `PREDFIX111_WRITEDECL=F` writes the seen reds as a declaration draft.
  - `PREDFIX111_SABOTAGE=sN` plants one wrong rule, fact or text per check (PLANTS111, s1..s13). `=all` runs
    every plant, one LIGHT subprocess each; s10 reads DIR.
- `predfix111_model.out`, `predfix111_sabotage.out`: the committed runs at the delivered tip.
- `predfix111_succ_decl.tsv`: SUCCESSOR111's declarations (model, red check, class, reason, key).

## Known limits

- predfold1125's limits hold for every read WALK111 does not parse (a read it cannot parse goes to the loaded
  builder, as before).
- WALK111's grammar: labels, uses, calls (no label parameters), rx literals with named groups and holes; an
  alternation inside an rx literal holding the targets is handed to the loaded builder.
- The relabel converts a group only at the top of its literal, and one read per program.
- MECH111 lays a condition only as a single-digit range on the named target, or as a lookbehind.
- The rows of the table WALK111 does not model (an argument's shorthand label, a sent label, a label the caller
  writes in an argument) are printed by TABLE111 as not modelled.

Lane files are historical after merge; never edited then.
