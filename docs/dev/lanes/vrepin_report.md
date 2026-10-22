# vrepin report (lane vrepin, sonnet, 2026-10-22)

Task: why do emit_sweep `--variant all` lowered-cap tag floors miss, and re-pin if legitimate.

## Premise test (done)
`scripts/emit_sweep.py` pins on main equal the kit's numbers: lowsize/lowboth byte `no-linked-call` 123
(lines 2157/2167/2176/2311/2321/2330), byte `yes` 1444 (lowboth) / 1450 (lowsize), utf8 `no-backreference` 461,
lowsize utf8 `yes` 1287. Kit table (vb-9950aa672 table.txt): measured values are lower by 1-11 and identical
at four recent commits, so the drop predates all four.

## Findings so far (no box needed)
- The floors were last set by 7900bfeb2 (2026-10-16, "re-pin VARIANT_PINS at b72291d84"). The drop is
  therefore inside b72291d84..ce5aa67a8: 811 commits, 183 on the first-parent line, 813 since to main.
- Candidate causes in range (src/lib/cli): E0 entry_rows (6f4269452 emit_comb.c), fdb/B1-B3 memfn sites,
  [ATTR-TABLE] (e13382b97), DD-11.5 P2a-P2e (\A/\z and (?m)^/$ fold into A_CTX), MEASURE-SET M0
  (abi 81->82), partmeas/K113 (1bf919a21). Several change what is emitted; none is yet implicated.
- Not yet decided: legitimate or regression. NO re-pin made.

## Method (queued)
`705-vrepin-bisect` (build/vrepin/705-vrepin-bisect in the worktree, gitignored): first-parent binary search,
one probe per commit = `emit_sweep --ref S --tree-rev S --variant lowsize --bases byte --streams emit-ir-auto
--no-variant-floor --no-self-check --emit-pins`, predicate lowsize/byte emit-ir-auto `no-linked-call` >= 123.
Checks both endpoints first. Prints `FIRST BAD (first-parent): SHA` then `== vrepin bisect COMPLETE`.
Probe logs: build/vrepin/probe_SHA.log. Caveat: the corpus (tests/) moves with each commit, so a first bad
commit may be a corpus change; the next step must diff that commit's rows/tags (a drop with reach rising and
no emitter change = corpus/tag move, legitimate).

## Next steps for the resuming agent
1. Read the job's log (`boxqueue status`, `scripts/verdict LOG`); take the first bad commit.
2. Decide: emitter output changed for fixed patterns (regression or intended change per its commit message)
   vs corpus change. If a regression: stop, file K131, report with the commit.
3. If legitimate: re-pin the floors with a dated comment block (date, commit, cause) per the script's
   convention, then queue `emit_sweep --variant all` on the branch (710-vrepin-all, same ready guard).

## STATE AT HANDOFF
- Queued: 705-vrepin-bisect (ready; i2build-parity is green so it is not held; box busy with 664-i2build-maketest2).
- OWED: bisect result; cause ruling; re-pin; green `--variant all` run. No rulings file entries read (none existed).

## Bisect verdict and cause ruling (lane vrepin2, 2026-10-22)
- 705-vrepin-bisect GREEN: FIRST BAD (first-parent) 813f43ec8 (merge of lane/m0build, [MEASURE-SET] M0, abi 81 -> 82),
  last good f5550b10d. lowsize/byte emit-ir-auto at f5550b10d vs 813f43ec8 (pins_*.py in build/vrepin):
  no-linked-call 123 -> 122, yes 1456 -> 1446, no-size-cap 76 -> 83, yes-collapsed 33 -> 35, refused 3444 -> 3446;
  -fprefilter yes 1597 -> 1587. Not a corpus move: M0's tests/ delta adds no corpus rows (reach not rising).
- Cause: M0's stamp scaffolding (`<PREFIX>_MEASURES`, rx_info.measures) grows every artifact; m0build_report.md
  section 8.3 measured the size-cap code count moving by +79 and the manager ruled it a DECLARED mover (byte-count
  reader class, D94 addendum; the size cap counts code bytes, scaffolding included, D84). The lowered 30000-byte
  cap therefore trips ~10 patterns sitting just under it: yes -> no-size-cap / yes-collapsed. Same shape as the
  precedents in emit_sweep.py's VARIANT_PINS comment (R4e'.0b 2026-10-09, VMLAZY +58 B). RULING: (a), legitimate;
  no K131. Pattern-level list NOT yet extracted (probe sweep dirs are deleted); 709-vrepin-measure keeps them.
- Re-pin NOT yet made: it needs measured values for every lowered cell at main, so it waits on the job.
## OWED (fresh follow-up lane)
1. 709-vrepin-measure (queued): keep_<sha>/ per-row TSVs for lowsize/byte at f5550b10d vs 813f43ec8 (diff the
   emit-ir-auto tag per pattern, list them here), and build/vrepin/pins_all_head.py = `--variant all --emit-pins`
   at branch HEAD.
2. Paste pins_all_head.py into VARIANT_PINS (pprint width 120), add a dated RE-PINNED block (cause above, 813f43ec8),
   then queue `emit_sweep --ref HEAD --tree-rev HEAD --variant all` as 710-vrepin-all, expect green.

## vrepin3 (sonnet, 2026-10-22): pins pasted, runs queued
- Merged main (a8897e529; one conflict, the lanes.md index, kept both sides). The merge brought new corpus files
  (tests/utf8/octal_wide, language-fix corpora), so 709's values (taken at the pre-merge branch HEAD) may be stale.
- Pasted `pins_all_head.py` (709) into `VARIANT_PINS` through pprint (width 120) with a dated RE-PINNED block
  (cause 813f43ec8, this report). Diff vs the old pins: the lowsize/lowboth tag cells named above, plus every reach and
  rising floor (corpus growth since 7900bfeb2; not all of it is M0), and utf8's yes-collapsed manifest witness
  `a{2,4}+a` -> `(a){2,4}` (a shorter new witness).
- Queued: 711-vrepin-remeasure (`--variant all --emit-pins` at the merged HEAD -> build/vrepin/pins_all_head2.py),
  then 710-vrepin-all (ready only after 711 is green; its prelude pastes pins_all_head2.py via build/vrepin/paste_pins.py
  and leaves the edit UNCOMMITTED, then runs `--variant all` with floors).
- OWED: after 711, diff pins_all_head2.py vs the pasted pins; any cell moving by more than the merge's corpus rows
  explains is the STOP RULE (report). After 710 is green, commit the script (if 710's prelude changed it) and END.

## jobfix (sonnet, 2026-10-22): 711 diff, 710 -> 715
- 710 failed READY-ERRORED: its `--ready` asked `boxqueue after 711-vrepin-remeasure`; the KEY is OWNER-REST (`vrepin-remeasure`), no PRIO prefix.
- Diff of 711's emitted pins (build/vrepin/pins_all_head2.py) vs the committed VARIANT_PINS (7924c9136): NONE. All 10 cells
  equal (also byte-identical to pins_all_head.py). 711 (08:30) re-measured the merged HEAD and 709's values (08:20) were
  already taken there; nothing to explain, no values to re-commit. The RE-PINNED block now says "re-measured after merging main a8897e529".
- 715-vrepin-all: the pin-pasting prelude is removed (it copied the checked values in, green by construction); the job
  runs `--variant all` against the committed pins, `--ready` is unconditional (no dependency left), and it exits on the tool's rc.
