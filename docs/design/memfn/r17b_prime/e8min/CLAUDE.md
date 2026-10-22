# r17b_prime/e8min/

B4's kit-tier verdict (E8), cut to the minimum on Frank's ruling (2026-10-21: "build what is needed and not theoretical needs"; the harness is ours and changes when a need shows).

- `plan.md` — the cut (lane emin): the question, KEEP/DROP (each dropped item with its trigger), one ~30 min window, main's part. Accepted by the kit manager 2026-10-21 with one change: E5 does not wait on the bench's answer to I-156 (bench cells are added as FINDING-only lines when the answer arrives).

Lane e8min (2026-10-21) builds the plan's KEEP list (report `docs/dev/lanes/e8min_report.md`; no `src/`, `memfn/src/`, `cli/`, `lib/` or harness change):

- `mk_j1_patterns.py`, `j1_patterns.tsv` — J1's pattern list from `docs/dev/lanes/rwquest/questions.tsv` (177 questions; flags i/m/s inline, utf as `-e utf8`, ucp as `--ucp`), the input of `../fdb1/shadow_census.py manifest --patterns`.
- `j1_census.tsv` — the census (the manifest pipeline, b4prep's lever set `b4prep-v1max2.tsv`): every set-FIND site of the J1 patterns with shape, row, pick, mover, and the question id in the last column.
- `pickcheck.py`, `pickcheck.out` — the independent pick-vs-term-count check (V1 iff r+e+c <= 2; exceptions listed with cause).
- `nonmover_cmp.sh`, `nonmover_cmp.tsv` — the non-mover byte check (walkcmp's shape): kit-side artifact vs main's, per J1 pattern.
- `readslot.py` — raw window launches -> one row per cell (grid2read's floor verdict, the null-control reading); `losers` writes f2perf's input.
- `verdict.py` — the verdict script, plan section 2 items (a)-(g); `sabotage.py`, `sabotage.out` — its sabotage pair (planted unlisted loss REFUTES, planted listed loss does not, plus an INVALID plant) on a synthetic table.
- `e8design.py`, `e8build.sh` — the window's cell design (94 J1 cells + 18 anchor/control cells) and the slot build (grid1's ext-arm-set shape; compile only).
- `jobs/560-kit-e8-window` — the ONE boxqueue job for the timing window (as prepared; NOT enqueued: the window needs Frank's clearance).
- `prereg.md` — E5: the shas the bars were fixed against.
