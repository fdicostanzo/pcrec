# r112 predfold1127 process
- setup start ~20:37; freeze 860331f12 verified; main at setup 17468e317; lint 10099/0; committed model 13/0, sabotage 15/15.
- full model re-run launched 20:38 (background), verdict pending at briefing.
- briefs written 20:41.
- critics launched 20:40 (two opus, background, unnamed): ruling (529 s, 38 tools), examples (399 s, 35 tools); both files complete with CRITIC COMPLETE; both final replies undelivered (expected).
- full model re-run #1 (clone without branch lane/pred-rev28): RED, SUCCESSOR1127 74 reds vs 73 declared: predfold1123 QUOTES UNDECLARED, predfix111 SUCCESSOR111 KEY CHANGED. Cause: predfold1123_model.py:1482 reads `lane/pred-rev28:...COND-FAMILY.md` by branch NAME (unpinned). Created the ref at the freeze in the clone; re-run #2 launched 20:49.
- verification inline (quote claims + walker one-calls, .coord/v/v1.py): all CONFIRMED findings held; RULING-2 PARTLY (the "body's own is B.d" is the manager's Class sentence of the argument-label ruling, not his words).
- freeze drift: lane/pred-rev28 moved 860331f12 -> 2b678db52 (journal only, denied path; no subject change). main unchanged 17468e317.
- re-run #2 ~21:00: `predfold1127_model: 13 checks, 0 failed`, PASS/FAIL lines identical to committed.
- draft written ~21:00; time to draft ~25 min from setup.
## Process observations
- Two narrow opus lenses finished in 7-9 min with 15 findings, 0 refuted; the RULING lens's tag grep over the record found three earlier-ruling collisions (the top class), the EXAMPLES lens independently found the same unmarked readers from the documents' side (overlap useful, not waste: different sites).
- The brief's "create every branch ref the models read by name" was right: the first re-run was red for exactly that reason. The skill's re-run step should say it.
- COMMON was sent before the full re-run finished (it takes ~10 min); no critic needed the verdict. Fine for a small round.
## Proposed changes
- SKILL.md §3 design-mode evidence: "Before the re-run, grep every evidence model the successor chain runs for `git show <name>:` with a non-hex ref and create each ref at the freeze in the clone; a model that reads a branch by name is a finding (r112 COORD-1: predfold1123 read lane/pred-rev28, red without it)."
- Ruling-lens brief template for folds: "grep the record for EVERY earlier ruling whose text states the clause the new ruling replaces, on a named example; each is a collision to mark" (r112 F1).
## Framework notes
- A two-critic coordinator round on a small fold costs ~25 minutes end to end, verification inline; the coordinator pattern scales down well when the subject is design-only text.
