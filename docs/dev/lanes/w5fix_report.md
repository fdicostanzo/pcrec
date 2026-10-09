# w5fix report -- alloc_check W5 reach made robust (2026-10-09)

## Cause
Kit unit M6 shifted arena traffic in src/gen/emit_vm.c. W5's pattern `(?:a?){700}` used to open an arena block in its forced loop (L=1); on M6 it makes 0 allocations, so the K35 floor (W5_MIN_INLOOP 1) fired and test-resource Section 2b went red. Reach is boundary luck per repeat count (triage14: {600},{750} reach; {650},{690},{710},{800} do not).

## Fix (tests/core/alloc_check.c only)
The arena exposes no way to force a block open, so the witness MEASURES. `w5_run` walks `w5_counts` (700, 600, 750, 500, 900, 1000, 400, 1200, 300, 1500), builds `(?:a?){N}`, runs the existing hook-less/hooked trace pair, and takes the first with L >= W5_MIN_INLOOP. Skipped candidates and the chosen one are printed (NOTE lines). It fails loudly only when no candidate reaches. W5_MIN_INLOOP is unchanged and applies to the population actually asserted; W1-W4 untouched. Header comment and W5_MIN_TOTAL comment updated (measured 190 at {600}; 220 at {700} pre-M6). tests/core/CLAUDE.md has a one-line note.

## Why robust
A shift that kills the current choice falls through to the next candidate instead of failing; the candidate set spans many boundary phases, so all-dead is unlikely, and if it happens the failure names the exhausted list.

## Validation
- `make -j4` ok. `taskset -c 12-15 gnutimeout 1200 make alloc` rc 0: {700} L=0 skipped, {600} chosen, PASS 1 in-loop trial (call 179 of 190), 6 margin trials diagnosed (log .scratch/alloc.log, uncommitted).
- Fall-through proof (scratch edit, restored): list set to 700,650,690,710,800,500,900,...; six dead candidates skipped, {900} chosen, PASS (call 272 of 283). .scratch/alloc_drop.log.
- `taskset -c 12-15 gnutimeout 1800 bash tests/resource/run_resource_tests.sh` rc 0, 0 sections skipped; the "[F6(b)] [D110] allocation-failure injector" line PASSes (Section 2b clean). .scratch/res.log.

## Sabotage/anchors
S646 cites alloc_check.c W5 only in prose (behaviour: in-loop trial reads "was REFUSED"), no line anchor. `python3 scripts/m6read_check_sab_anchors.py`: 571 sabotages, 589 anchor sites, all resolve. S646 itself not re-run (heavy mech in progress); its detection path (in-loop trial assertion) is unchanged.
