CRITIC verdict / harness fidelity to the owner's rulings (opus): growth2 (r74)

Read /var/tmp/pcrec-pcrec/scratch/crit-growth2/COMMON.md first; it binds you (scope, read-only, denylist, output).
Your dir: /var/tmp/pcrec-pcrec/scratch/crit-growth2/verdict/ ; findings file verdict/findings.md (PRE-CREATED: append only); ids VERDICT-n.

ONE question, two sub-parts:
(a) Does every outcome the rulings in R/rulings/GROWTH-SWEEP.md (and the plan row's RULE / addendum / growth-memcap,
    R/rulings/plan-row-GROWTH-SWEEP.txt) call RED make SUBJECT's runner, `make test-growth`'s body (run_growth.sh)
    and `make test-stackdepth`'s depth arm exit nonzero, and does every outcome they call PASS go green? Work the
    rulings clause by clause: limit-test-criteria (1) STABILITY: clean refusal by THAT limit (a crash, timeout,
    runaway, a DIFFERENT refusal, a compile are red); (2) LIMIT: compiles AND its matcher runs, a refusal is red;
    (3) crossing over red both ways; (4) memory-cap cells stability-only; growth-compile-cells "a cell that used to
    refuse and now compiles goes red"; limit-cell-matcher-cost (the NAMED compile-only exceptions: which cells, under
    which name, and how many: the ruling and the MANAGER readings say how they are named); the K156 lines. Drill
    every PASS predicate (judge(), ladder_ok(), matcher(), the red ID:KIND branch, the norun branch, selftest's
    own pass condition) with constructed outcomes through the REAL code: a fake driver / planted copy via
    kit/mkcopy.sh, or judge() called directly on a Cell. Required drills: an `internal error:` refusal; a refusal
    whose text CONTAINS a limit's substring but names another limit; a "never ran" outcome; a matcher that exits 2,
    3 or by signal, and one that runs but answers wrongly (does the harness need the answer? say what the ruling
    says "its matcher runs" means); a red cell failing in its own kind vs another; a stability cell that compiles
    inside a red; library mode (lib_mode()) given limit and stability cells: which of the rulings' verdicts does it
    apply, and is that what the library-vs-process DIRECTION asks? Can `--selftest` itself fail (plant a judge()
    that always passes: does run_growth.sh go red)?
(b) You verify the OWNER'S QUOTES word for word: every place SUBJECT's code comments, tests/growth/CLAUDE.md,
    docs/testing.md, cells.tsv / plus_edges.tsv headers and the Makefile comment quote or paraphrase an owner ruling,
    diff it against R/rulings/: a paraphrase that widens or narrows the ruling, or a MANAGER reading presented as
    the owner's, is a finding. Mark per MANAGER line in GROWTH-SWEEP.md whether SUBJECT implements it.
Do NOT probe the table EDGES (is n really the largest that compiles): another lens owns that. No plants (another
lens owns them).
Probe budget: about 60 real cell runs (kit/judge_cell.py) + any number of fake-driver runs (they compile nothing);
a mkcopy main-loop run must select at most 6 cells.
Deliver: append findings as you go; end with `## PROBED-AND-HELD` and `CRITIC COMPLETE`; run lanecheck
(COMMON's command, lens name `verdict`) until DONE; END.
