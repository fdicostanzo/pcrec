CRITIC house / tables and docs against the code (sonnet): growth2 (r74)

Read /var/tmp/pcrec-pcrec/scratch/crit-growth2/COMMON.md first; it binds you (scope, read-only, denylist, output).
Your dir: /var/tmp/pcrec-pcrec/scratch/crit-growth2/house/ ; findings file house/findings.md (PRE-CREATED: append only); ids HOUSE-n.

ONE question, two sub-parts:
(a) House rules and the owner's minimal-harness rule ("build the least that gives a trustworthy verdict, no
    future-proofing"): over the SUBJECT diff (tests/growth/*, tests/thread/run_compile_stack.sh), against
    docs/dev/guide/coding.md + style.md: duplication (name the shared abstraction), dead code, flags/modes/columns
    nobody uses (`--sample`, `--pairs`, `pair`, UNPAIRED reporting, red kinds nobody uses, plus_edges.tsv's 92 rows:
    is each piece needed for a trustworthy verdict, or future-proofing?), open sets where a closed set is declared,
    silent defaults, and the COST the subject adds to `make test` (the depth arm now builds and runs a matcher per
    depth@250 cell: time ONE depth@250 cell with `kit/judge_cell.py subject depth/grp@250` vs
    `kit/judge_cell.py --harness base subject depth/grp@250`, and scale by the population; say whether that cost
    buys verdict the ruling asks for).
(b) Every NUMBER and CLAIM in the tables' headers and docs (cells.tsv header, plus_edges.tsv header,
    matrix_axes.tsv/depth_families.tsv headers, tests/growth/CLAUDE.md, docs/testing.md "Growth sweep",
    tests/thread/CLAUDE.md, the Makefile comment, known_issues hunks, run_growth.py docstring/help) against the
    code and a probe: counts (cells, pairs, exceptions: `run_growth.py --list`/`--pairs`), and the EDGES: a limit
    cell claims to be "JUST BEFORE" its limit (the largest n that compiles) and its stability twin to be past it.
    For a sample of pairs, run n (must compile), n+1 (must be refused by the named limit) and, where the twin sits
    further than n+1, the gap between (e.g. spine/alt_lit 70657 vs 70773; the header explains why): is the limit
    cell really at the edge in the mode it is run in, and is the twin refused by the SAME limit? Probe n+1 by
    editing a mkcopy cells.tsv row (or a one-line python3 using run_growth.spine()/nest() to write a patfile and
    growth_driver one ... as judge_cell does). Include at least: two depth pairs, two matrix `+` pairs from
    plus_edges.tsv, alt_lit, alt_cap_emit, one raise-1 NFA pair (z_cls or lit, ~8 s each), cnt_past.
Probe budget: about 120 cell runs (raise-1 131k cells cost ~8 s each; no more than 15 of those).
Deliver: append findings as you go; end with `## PROBED-AND-HELD` and `CRITIC COMPLETE`; run lanecheck
(COMMON's command, lens name `house`) until DONE; END.
