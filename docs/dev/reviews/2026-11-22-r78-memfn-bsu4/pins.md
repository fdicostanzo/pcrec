# CRITIC PINS: memfn-bsu4 (r78)

(append below; never overwrite)

## Findings


### PINS-1 CONFIRMED: the k source drops §10.1's C-own clause, and no check prints the own population. Severity: maintenance/check-design. Effort: small. Blast: span_pins census + cells.
§10.1 says the k source has "C-own read off the loop's test (no table name)". §10.2 says "No plant guards R-5's `own` condition ... Its population (0) is printed by the k-source census (K35)". `tests/memfn/span_pins.py` k_source (l.101-114) and `eligible` (l.96-98) have no C-own term (`grep -n own span_pins.py`: only prose). Its sibling `memfn/tests/g2_vspan.py:551` does compute `own`, but neither file prints an own/not-own count. So the census the design names as the K35 printer prints nothing for it. Repro: grep both files. Expected: the own clause applied in the predicate and "not-own eligible loops: 0" printed.

### PINS-2 CONFIRMED (mutation survivor): the predicate's `frame == 'E-find'` clause cannot fail on this population. Severity: maintenance (K35). Effort: small.
Two mutated copies (pins/m/noframe.py drops the frame term from `eligible`; pins/m/noframe1.py drops it from the per-cell reach check l.128). Both are SAME (rc 0, 65/65 pass) against the subject tree with the traced compiler. Why: in SPAN-SEED at w32, 5 sites are R7w/E-stmt (`[0-9]{65}`, `{66}`, `[0-9a-f]{1001}`, `{1002}`, `[0-9a-f]{20}[g-z]{20}`). Their head-0 compile renders no `_j =` loop at all (0 loops; pins/estmt.py), so the frame term never decides. At w4095 all 41 sites are E-find (pins/frames.py: w32 D-hors 20, R7w/E-find 14, R7w/E-stmt 5, D1 1, PAIR 1; w4095 D-hors 23, R7w 16, D1 1, PAIR 1). R-15 retired the frame cell, so a population of 0 may be by design. But the check neither counts it nor says so. Fix: print "non-E-find sites with an in-range loop: N", or name the term as unreachable.

### PINS-3 CONFIRMED (mutation survivor): the 20-cell floor counts list entries, not distinct cells. Severity: maintenance. Effort: trivial.
Mutation pins/m/dup19.py changes cell 20's layer `['v3']` to `['off']`, which makes it a copy of cell 19. Result SAME: rc 0, 65 pass, "20 cells (floor 20)". T-force at x86-64-v3 (§10.2 cells 19-20 "both layers") is then unguarded with no red. `n` counts `CELLS` results (l.168-176); the cell numbers 1..20 and the distinctness of (pattern, width, flags, layer) are never checked. Fix: assert `[c[0] for c in CELLS] == list(range(1, 21))` and 20 distinct tuples.

### PINS-4 CONFIRMED (by text; SUSPECTED that no other check covers it): cell 16 cannot tell which stretch carries the selector, and never reads the second stretch's k. Severity: design/speed guard. Effort: small.
§10.2 cell 16 says "stretches k 20 and 19, both eligible". §10.1 says "first eligible stretch per site". `pin_cell` reads only `loops.get(1,[0])[0]` (k 20). The head-0 text carries both loops, `_j = 0 ... < 20` and `_j = 20 ... < 39` (pins: harness render at w4095), so k 19 is never checked. The text count (1 selector, 1 `__w32`) also reads the same whether the selector covers stretch 1 or stretch 2. The seed census uses `any(... for k in ls)` (l.160). So a kit that vectorizes the second stretch instead of the first passes both. Answer identity would not catch it either, since both are correct. The shipped v3 text does take the first (`vs0(...) && s[c+20] in g-z`). Confirm: plant "pick last eligible stretch" in window.c and run span_pins (not done: no planted tree for it).

### PINS-5 CONFIRMED: the SPAN-SEED census collapses two selector calls at one site to one. Severity: maintenance. Effort: trivial.
l.161 `kit = {int(h) for h in CALL.findall(text)}`. On the real w32 v3 text of `[0-9a-f]{17}` (pins/c3.c) with the walk's call doubled, CALL.findall gives 2 and the set gives 1, so the census reads "agree". Once-per-site is then pinned only on cell 16's single pattern, not over the 41 seed patterns. Fix: compare per-handle counts (a Counter), with each count equal to 1.

### PINS-6 CONFIRMED: the utf8 counts 20 / 21 are checked by no k-source check, and the 4095 count (21) by no check at all. Severity: check gap/doc. Effort: small (one more encoding loop).
§10.1 says "Under `-e utf8`: 20 and 21", and §12 says "SPAN-SEED floors 28 / 31 (byte), 20 / 21 (utf8) | DERIVED: the table's predicate ... by the independent k source". span_pins runs byte only: SEED_FLOOR {32: 28, 4095: 31}, and no `-e` flag anywhere. `span_vector_identity.py:116` floors utf8 at w32 = 20 as a kit mover count (not the k source), and its seed4095 row is byte only. So nothing checks 21. Either add utf8 to span_pins's census, or strike the k-source claim for utf8 from §12.

### PINS-7 CONFIRMED (design; answers standing question b): two divergent copies of §10.1's k source in one unit. Severity: maintenance. Effort: small-medium.
`tests/memfn/span_pins.py:75-114` (LOOP, FDR, k_source, eligible) and `memfn/tests/g2_vspan.py:533-562` (H0_LOOP, FDROUTE, k_source) both implement "the k source". They already differ:
- g2_vspan applies C-own and stops at the first eligible stretch; span_pins does neither (PINS-1, PINS-4).
- The regexes differ: H0_LOOP is anchored on `j++) if (` and allows any prefix; LOOP is hard-wired to `rxa`.
- They take the trace from different binaries: pcrec-trace (span_pins) vs a traced harness (g2_vspan).
This is a parallel mechanism for one ruled fact (memory: general mechanisms, not special cases). See the standing-question answer below.

### PINS-8 SUSPECTED, nit: the text counts are whole-file, not "in the walk" / "in the selector" as §10.2 says. Severity: nit. Effort: small.
On pins/c3.c, I replaced the walk's call with `if (0)` and added a stray function holding `rxa_mf1_vs0(rxa_mf1_s, rxa_mf1_c)`. The check still reads 1/1 "present". Whether the call sits in the walk is the routing leg's (routing_shape.py) structure check, so the exposure is small. Note it in the docstring or scope the count to `rxa_search`.

### Standing question (b): family, general form, unlocks
- Family: span_pins is the sibling of two existing checks.
  - The finder-row trace checks: `tests/memfn/finder_check.py` (reads `MFTRACE FDROUTE` against design-written expected rows) and `rows_check.py` / `rows.tsv` / `row_floors.tsv` (per-row reach floors).
  - G2-V whole's k source (g2_vspan.py), which is the same control.
  The 20 cells are a "literal cell -> expected (row, k, text count)" table, the shape of `pres_pick_witnesses.tsv` and `pr11_witnesses.tsv` (witness TSVs read by a runner). Not joining them costs PINS-7 (two k sources) and keeps the cells as a Python literal that no row-floor tooling sees.
- General form: one shared module, a "site facts" reader: per (pattern, width, flags) it returns {site: row, frame, [(k, own)] per stretch}, from FDROUTE plus the head-0 loop text. The predicate table (row -> k range, frame, own) is declared once, as a first-match table. Consumers: span_pins cells, the span_pins census, G2-V whole's populations, and the identity gate's V-count. Cells move to a TSV beside the witness TSVs, with a uniqueness/1..N check (PINS-3).
- Unlocks, with triggers:
  1. The next span row (a new finder row admitted to V, or W > 32) adds a predicate-table row, not edits in two files. Trigger: R-47's next row, or any change to §3's span form table.
  2. utf8 and further encodings become a column (PINS-6). Trigger: now (§12 already claims utf8).
  3. row_floors-style reach floors per predicate row (D-hors / R7w at each rung) come for free from the shared reader. Trigger: the first rung or bound re-pin.
  4. Multi-site patterns: every seed pattern today has exactly 1 site (pins/frames.py: 0 non-1-site of 82). The reader's per-site keying is untested until a multi-site witness exists. Trigger: the first seed or cell pattern with two find sites.

## PROBED-AND-HELD
- Clean run on the subject tree (traced compiler trace/subject/pcrec-trace): rc 0, 65 checks pass, 0 fail. SPAN-SEED prints both counts: w32 28 by the k source and 28 selector calls; w4095 31 and 31.
- (a) The cells against §10.2, literally: all 20 match on pattern, width, binary, flags, layers, expectation, row and k. Cell 15's `--memfn=no-fd-d1` gives D1w. Cells 17-18 use pcrec-harness. Cells 17-20 run at off and v3. Every cell is reached; the verbose copy printed all 60 per-cell verdicts.
- The counting regexes match R71-6's spellings. On real text (pins/c3.c, w32 v3 `[0-9a-f]{17}`) the definition heads do not count: bare `vs0(` occurs 2 times and bare `__w32(` 2 times, but the counts read 1 and 1. `__w32_b(` does not match W32. Two selector calls in one cell read 2, which is red (cells require ==).
- The k source: the row and frame come from `MFTRACE FDROUTE`, which the design permits. k comes from the head-0 harness loop text (end - lo). The predicate lives in the check. Nothing is read from memfn/src or window.c (grep). SPAN-SEED is read via `--list-source` of tests/memfn/span_seed.rxt (41 patterns). The floors 28/31 and the pattern count 41 are literals. Every site disagreement is red.
- Mutations of copies (pins/m/*.py), 19 in all:
  - LOUD (rc 1): drop cell 20 (fails 1); flip cell 5 expectation (2); flip cell 17 expectation (2); cell 13 row D1->PAIR (1); LOOP regex broken (43); CALL broken (17); W32 broken (7); FDR broken (43); predicate 16->15 (4); 1000->1001 (2); 24->23 (4); 64->65 (2); seed list cut to 40 (1); override flag ignored (4).
  - Trace binary swaps: --trace /bin/true LOUD (43), /bin/false LOUD (22), plain build/pcrec LOUD (43).
  - Survivors: noframe, noframe1 (PINS-2) and dup19 (PINS-3). The kitlen control was an equivalent mutation.
- Population reached: 20 cells; 41 seed patterns x 2 widths = 82 sites, every one single-site.
- simd_floor_check.py:659 calls `span_pins.run(a.pcrec, a.harness, a.trace, ok, bad, a.jobs)`. `--trace` is required there, and run_simd_floor.sh builds the traced compiler fresh, so the wiring held.
CRITIC COMPLETE
