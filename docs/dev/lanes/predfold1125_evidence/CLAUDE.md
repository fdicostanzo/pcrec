# docs/dev/lanes/predfold1125_evidence/ — lane predfold1125's evidence

Evidence for docs/dev/lanes/predfold1125_report.md. The fold puts seven owner rulings into the predicate
documents: drop-not, array-argument, brace-counts, map-creator, string-literals, bang-split and and-not. It also
takes review r109's F5, F7, F13 and F14, and the rulings file's R-1..R-4 (sent-label-wall, label-needs-mark,
skip-past-wall, equivalence-inside). This is design evidence only. Nothing here rules, and no check under `make`
reads it.

## Files

- `predfold1125_model.py` is a STANDALONE python3 model, the successor of
  `../predfix90_evidence/predfix90_model.py`.
  - It LOADS predfix90's model unchanged, up to its first check (`unit10("CONTROL", `). The older models load
    through it.
  - Its front end TR11 (inlined source, `TR11_SRC`) reads the new spelling into the loaded engine's spelling, rule
    by rule:
    - `!` on a test, `~` on a set or pattern;
    - `^A` / `!^A` / `peek`;
    - the array argument `q(@d, S)`, and `every`;
    - the occurs counters;
    - brace counts;
    - strings;
    - map literals and their access;
    - label-needs-mark.
  - It refuses each wrong form with a message naming the form to write.
  - RX11 (inlined, `RX11_SRC`) lowers into python `re` the programs the engine refuses (a negative lookahead,
    `when`, a pattern complement). It works MECHANICALLY from the body text.
  - `X11[0]` switches the front end off. CANARY and SWEEP11's control run with it off.
  - The checks, by name in its output:
    - CANARY;
    - TR11, the rule table;
    - CENSUS11 (r109 F14), every printed `!`/`~` classed by its operand;
    - SWEEP11: every printed three-mode line run. The starting commit 212e234e6 is run under predfix90's engine,
      keyed by the translated program. Re-spellings (RESPELL11) and lines a ruling dropped (GONE11) are declared.
      The control's own reds are counted as INHERITED (same key, same status);
    - ERRSWEEP11 (r109 F5), each refusal message naming its form;
    - GROUP11, BRACES, STRINGS, MAP11: each against python `re` or a direct reading;
    - READINGS11: the manager's readings, each SUPPORTED, NOT SUPPORTED or UNTESTABLE;
    - SPECLINES: every new printed line, run from the SPEC11 table;
    - GRID: predfix90's section verbatim, with one declared GRULE patch for R-1;
    - SUCCESSOR11;
    - QUOTES11: the owner's words, in the record at the starting commit and in their piece;
    - DOC11: every SPECLINES line verbatim in its piece.
  - SUCCESSOR11 re-runs 17 models: predfix90 (LIGHT), predfold1124, and, through predfix88's `--succ` runner,
    predfix88 and the fourteen before it. Each red is declared in `predfold1125_succ_decl.tsv` by predfix90's
    `red_key10` key, which carries no document line numbers. A traceback is never declarable.
  - Its verdict is its last line, `predfold1125_model: N checks, F failed`. It exits non-zero iff that line reports
    a failure.
  - Run: `timeout 5400 python3 -I -B <this dir>/predfold1125_model.py`.
    - `PREDFOLD1125_LIGHT=1` skips SUCCESSOR11.
    - `PREDFOLD1125_SUCCDUMP=DIR` saves each successor's output. `PREDFOLD1125_READDUMP=1` re-reads those outputs.
    - `PREDFOLD1125_WRITEDECL=F` writes the seen reds as a declaration draft.
  - `PREDFOLD1125_SABOTAGE=qN` plants one wrong rule, fact or text per check (the PLANTS11 table, q1..q14).
    `=all` runs every plant, one LIGHT subprocess each; q12 reads the dumped successor runs. Each plant must FAIL
    its target check, with no traceback.
- `predfold1125_model.out`, `predfold1125_sabotage.out`: the committed runs at the delivered tip.
- `predfold1125_succ_decl.tsv`: SUCCESSOR11's declarations (model, red check, class, reason, key).

## Known limits

- predfix90's limits hold.
- TR11 selects only on map literals, and reads only constant brace counts.
- RX11 takes P's paths at a start by end, longest first.
- The engine does not parse `!!` or `~~` (TR11 reads `!!X` as X), and it cannot run a `|` of conditions. The
  record reading is run against a direct python reference over its 121 states.
- ERRSWEEP's reader is predfold1124's. Three lines it cannot read are counted.

Lane files are historical after merge; never edited then.
