# SLOT findings

Subject: docs/design/memfn/span_cards.md rev 0 (copy span_cards_rev0.md). Code cites at the build tree
worktrees/crit-memfn-span-cards (main fb22c62a6). Rulings at 80341284e only.

## Findings

### SLOT-1 — `raw.tsv` (and `cells.tsv`) re-create a slot the set format already has: the `cells` section
CONFIRMED (text + code). Severity design/maintenance. Effort S (design text), M (build). Blast: S2a/S2e, measures.md §8¶1 hunk, the recompute check.
- The format already carries the raw cells IN the set: `docs/spec/measures.md` §2¶2 (sections `header cards rows cells members`), §2.2 table `cells | cell group arm length launch round ns_e6`, §2.2¶3 (`inputs` may name "cell ids of this set"); `src/core/ks_measures.c:44` parses it, the canonical writer sorts it (`:180-219`), `tests/knowledge/ks_ref.py:79` reads it. `measure_sets.md` §1.2 table ("`cells` | the raw per-launch cells every `fitted` row ... reads"), and §8 (`measure_sets.md:557`): "**The `raw/` directory is gone.** Its job (the reader's input) moved into the set's `cells` section, where the checker can reach it". grid1's set has an empty `#section cells` (set.tsv:105).
- span_cards §3.8 steps 1/3 and §4.4 ("§8¶1 (`raw.tsv`, kept, never loaded, sha in PROVENANCE.md)") add a SECOND home, `measure_store/zen4-grid3/1/raw.tsv`, plus the same file "committed on the kit branch" at step 1 (two copies), with its own sha check (sabotage 14). The doc never names the `cells` section (grep `cells` in the rev 0: only the new `cells.tsv` and "per-call cells").
- `memfn/measure/cells.tsv` (§3.1: "card key, arm, group, subject recipe, points") is the third: the `cells` section's `cell group arm length` columns, and the card row's `subject`/`lengths` columns, again.
- Fix: either widen `cells` (spec §2.2: "every row the checker recomputes", today narrowed to fitted/NULL-rule rows) and hold the per-launch medians there, recomputed by the EXISTING checker path (Goal 3 then rides `test-measures`, not a new tests/knowledge script); or state the force that forbids it. The one real force I can see is size: `cells` is embedded (Makefile `MEAS_STORE_SRCS` embeds set.tsv whole). ~280 points x 5-7 launches x arms is ~10^4 rows; that argues "the embed omits `cells`" (one embed rule), not a second file format with its own sha, writer and check.

### SLOT-2 — `memfn/measure/` is the rejected alternative of measure_sets §7.1 (one driver), built without naming it
CONFIRMED (text). Severity design. Effort S (argue) to M (reshape). Blast: S2c, the M3 tool later.
- `measure_sets.md` §7.1 "Home: one driver, owner-supplied cards and probes": `pcrec-measure` in `measure/` OWNS "run control: the quiet gate, the governor, affinity, A/A pairs; the card interpreter; the NULL rule; the set writer and its self-check"; "Owners supply METHOD CARDS (§7.2) and PROBES. A kit quantity is measured by the kit's harness mode". Priced and REJECTED there: "(b) A mode of the kit's harness only" (inverts ownership) and "(c) One python script. Install time must not need python."
- span_cards §3.1 puts run control (drv.c: calibration, rounds, rotation), the estimator, the gates and the interim-set writer (read.py, python) in a kit-owned dir, and cites D176 Q3 as "the kit contributes its method cards to that script" — that phrase is NOT in D176 at 80341284e (grep of decisions.md and plan.md: no hit); D176 Q3 + [MEASURE-SET] FORMAL LIBRARY (a) say "a canned, self-contained pcrec script (part of pcrec, not bench)".
- D77 rightly keeps M3 unbuilt, but the design should split along §7.1's seam now: the KIT supplies probes (the G2 `--cards` texts) and card rows; the estimator/gates/writer are written as the format's own rule (spec), so M3's C driver implements the same text later, rather than a python read.py becoming a second, kit-owned set writer. At minimum §3.1 must cite §7.1 and say why (b)/(c) are acceptable for a slot.

### SLOT-3 — the DEFAULTS recommendation (B) contradicts R-35 and span_pick, and breaks Goal 1's own measure
CONFIRMED (text). Severity design (a ruling conflict). Effort S. Blast: S2e, row 1's landing.
- R-35 "What pcrec needs" item 1: "Stage 2 adds no reader, moves no emitted byte, and leaves DEFAULTS unchanged."; item 3: row 1 "flips DEFAULTS to zen4-grid3 ... Its flip needs its own landing verdict from main." span_pick.md §Staging Stage 2: "No reader, zero movers, stamps and `DEFAULTS` unchanged."; Row 1 `[rev3 C6]` "It flips `DEFAULTS` to the new set."
- span_cards §8.3 (B) says "No ruling is amended": false — it amends main's R-35 and span_pick rev 5.2 (main-approved). The conflict with D166 add. 2 / measures.md §5¶6 / measure_sets.md:794-796 ("names the newest official set, or the newest scratch set while no official one exists") is real and correctly found, so the honest framing is: either reading amends something; (A) amends a Frank ruling's literal => a question for Frank (the design's §10 says "For Frank: none").
- Goal 1's measurable form (§1): "`--list-measurements` changes by exactly the new set's row". Under (B) grid1's row ALSO changes: spec §6¶1's `sets` view carries `default_for`, which moves from `idk` on grid1 to grid3. So the recommended reading fails the design's top goal's check as written.
- Consequence of (B) for row 1: its "flip" and its separate landing verdict (R-35 item 3) vanish; row 1 becomes the first READER of an already-default set. Main should rule this knowingly.

### SLOT-4 — check C cannot resolve the new cards' deps: the dim is named `method`, the dep id `libc` vs token `memchr`; `enter`'s dep names no key token
CONFIRMED (code). Severity maintenance/answer-of-a-check (a witness claim false). Effort S. Blast: S2c's witness "check C resolves every new dep".
- `tests/memfn/finder_check.py:396-399`: a dep is resolved only `if table == "kit-grid" and c["dims"].split(";")[0] == "form"`, the id = the key's first token (`WALK`->`walk`). grid1's cards use dim `form` (`kit-grid.tsv` rows: `form;kind;shape` etc.).
- span_cards §2.4: `find_byte` dims `method`, `find_hit` `method;landing;split`, `enter` `kind;entry`. Check C skips all three silently (no bad(), no unreached) — the S2c witness reads green with nothing resolved. Only `verify_cmp` (`form;cls;pass`) is reached.
- Token/id mismatch: keys use `memchr` (§2.5 `find_byte.memchr`), the deps list `libc` (§2.4 "kit:form.\<method\> (walk, libc; ...)"), and `formhash.c:240` `canon()` knows `walk`/`libc` only. `kit:form.<method>` substitutes `memchr`, which hashes nothing.
- `enter`'s deps "kit:form.\<the site's method\>": the method is not a dim of `enter.<kind>.<entry>`, so the dep is not a function of the key (measures.md §2.3¶2 tokens = dims). Either add the dim or name the fixed form.
- Fix: one dim name for "the kit's text id" across kit-grid@1 and @3 (`form`; a method IS a form on a layer, D147, as §2.3 itself says), the key token = the canon id (`libc`, or canon gains `memchr`), and check C's guard keyed on that.

### SLOT-5 — "Row 1's SIMD-on arm needs no SIMD card" is false at row 1's own witness; J6 is not "droppable alone"
CONFIRMED (run). Severity design. Effort S. Blast: S2d's job split, row 1's SIMD arm.
- Repro: `build/pcrec -p rx -o a.c --pattern '(?i)x/1234'` -> `#define RX_MEMFN_FORMS "none"`; with `-fmemfn-simd` -> `#define RX_MEMFN_FORMS "vrun@w32+w16"` (a w16/w32 prefix rung of the `rx_mf1_ofsskip` site). `RX_MEASURES ""` on both.
- span_cards §2.5: "Row 1's SIMD-on arm needs no SIMD card ... `none` means the text is identical"; the table row puts vrun/vany cards under the C9 row only, "one separable job (J6), droppable alone". The design's own census rule ("a non-`none` site there ... adds that form's keys to the row-1 list") then pulls `find_byte.vrun-w16/w32` and their `find_hit` into ROW 1's list at the watched witness. If J6 is dropped (or PARTIAL), row 1's SIMD-arm incumbent is unpriced and span_pick §The pick 4 keeps it: row 1 cannot depart on the SIMD arm, and D186 C9's premise "(on '/' the SIMD build calls memchr, the same as scalar)" covers the candidate only, not the incumbent.
- Fix: state the vrun cards as row-1 keys (J2/J3), leave only vany* in the separable C9 job.

### SLOT-6 — the harness set reader is a sunset mechanism the design extends instead of retiring; format-2 logic lands in four parsers
CONFIRMED (code). Severity maintenance. Effort S. Blast: S2a.
- `cli/main.c:73-76`: "THE HARNESS'S SET READER, the test build's `--harness=measures=FILE` lever **until [MEASURE-SET] M0's loader** ... gives a shipped compile one." M0 is on main ([MEASURE-SET] status; `--measures=FILE` works: the build tree ran it). `tests/memfn/arm_fixtures.c:1527-1565` `fd_load_set` is a further private parser (key + value_e6 only, source "-").
- span_cards §4.2/§4.5 teach BOTH the format-1/format-2 noise rule ("The harness reader (`cli/main.c`) and `arm_fixtures.c` follow the same rule"), on top of ks_measures.c, ks_ref.py and from_interim.py. D166 add. 3 allows several READERS of one format, but the format-1=>UNMEASURED rule is a pcrec POLICY, now written three times in C.
- Least form: the two test levers state `MF_NOISE_UNMEASURED` unconditionally (they are test inputs; the MEASURED path's witness is `--measures=FILE`, which S2a already uses), or the harness lever retires per its own "until".

### SLOT-7 — two noise-policy constants, two homes; z placed in a file ruled to migrate into sets
CONFIRMED (text). Severity maintenance. Effort S. Blast: row 1.
- `gate_e6` 30000 (a per-card noise policy, UNMEASURED DEFAULT) lives in `kit-grid.tsv`; `COVER_Z_E3` (the band's noise policy) goes to `memfn/src/plan_cost.def`, whose header is "THE WINDOW FAMILY'S COST TABLE" with columns (value, unit, provenance, BOX, basis) and "RE-MEASURING ANY ROW IS A BYTE-MOVING KIT EVENT"; [MEASURE-SET] RULED Q1 / D176 Q3: "`plan_cost.def` rows migrate into the sets". span_cards §6 narrows that to "cost rows migrate ... its policy rows stay" — not what the ruling says.
- The design argues correctly that z must not be a set row (a re-measure must not move policy). Then the home is a declared kit POLICY table (MATERIAL_NUM/DEN, MAX_SET, HORS_MIN, z, and the gate default), which row 1's E2 unification already owes; naming it now avoids a fourth family member. Low effort; row 1's.

### SLOT-8 — census0.py is a second kit-side pricer beside smp20.py (third implementation of the price formula)
SUSPECTED (design text; confirm by reading census0's spec when written). Severity maintenance. Effort S.
- §7: census0.py is "a generalization of `smp20.py`"; its control "reproduces `smp20.out`". smp20.py stays. With row 1's C pricer and span_pick §The independent control's pcrec-side re-pricer (`span_pick.md:473`, deliberately independent), the KIT side then has two python pricers of one formula. census0 should REPLACE smp20.py (smp20 = census0 on one site; `smp20.out` its golden), so a formula fix lands once.

### SLOT-9 — the unit's noise is propagated by one rule for derived rows and ignored for measured rows
SUSPECTED (text). Severity design (band width). Effort S.
- §3.4: `aa` is "scaled to the row's unit by the same ratio as the value", `sp` per launch; the unit row's own uncertainty never enters a measured row's noise. §4.3's `ratio` rule for a derived row is `|a/b| x sqrt((sa/a)^2 + (sb/b)^2)`. Both describe "a value relative to another". Per-launch relative values (each launch's slope / that launch's walk slope) would make `sp` carry it; otherwise state why the unit's noise cancels (it does only when both priced plans share the coefficient, span_pick band rule).

### SLOT-10 — derived-noise rules built with zero population, while §4.6 defers a field for the same D77 reason
SUSPECTED (consistency). Severity design. Effort S.
- §4.3: "zen4-grid3 holds NO derived row ... the rule's population there is zero"; its only producers are the M3 install tool and M2 envelope (both unscheduled; `env-max/env-min` are envelope derivations). §4.6 defers the bundle's sampling-noise field because "A seam field nobody writes and nobody reads is built ahead of need (D77)". R-35 does ask for "derived noise by quadrature", but its "Not asked" leaves the shape to the kit: one rule "derived rows: UNMEASURED until the first producer of a format-2 derived row" (as §4.3 already does for `interp-log2`) meets D77 and R-35 with no table, no C and no ks_ref.py work.

### SLOT-11 — R-35's "Sabotage ids" rule is inverted
CONFIRMED (text). Severity doc/process. Effort trivial.
- R-35: "**Sabotage ids:** the kit takes its own from the top of the free range and records them in its first commit (three lanes are allocating)." span_cards §0 row 8 and §9 header: "sabotage rows listed per unit, ids the manager's" / "(ids: the manager's)".

### SLOT-12 — small text inconsistencies
CONFIRMED (text). Severity doc.
- §4.1 "the three positional constructors found by grep" (verified: cli/main.c:160, memfn_sites.c:89, arm_fixtures.c:1562 — three) vs §8.2 "the four constructors (§4.1)".
- §4.3 "checked by §8.2's recompute": §8.2 is the numbers table; the recompute is §3.8 item 4.
- `kit-grid.tsv`'s header hard-codes the unit for every version ("ratio (to u = beta_walk(DFA_SCAN, r1e0c0) = 0.1892 ns/B"); kit-grid@3's unit is `find_byte.walk`. §8.2's package for the card table names "the header line" but not this per-version unit sentence.
- §2.4 cards say `rounds 7` while grid1's @1 cards say `rounds 5`; §2.1 says kit-grid@3 "KEEPS" §5.4's 7 rounds. Fine for a new ver, but §2.1's "keeps" is relative to grid2's slot, not to the table's previous ver; say so.

## Rulings: agreement and consequences (summary)
- R-35: agrees on cards/noise/digest/coverage/step-0; DISAGREES on DEFAULTS (SLOT-3), sabotage ids (SLOT-11); defers memchr-back and the match_api hunk openly (§10, for main: fine, but R-35 named both, so each needs main's ruling, not just a recommendation). (a) facts-only pcrec hunks: S2a's pcrec hunks hand noise as a fact with a state; no kit method enters pcrec (held). (b) window: only S2d needs one, never 20:00-01:00 (held).
- span_pick 5.2: stage 2 content matches; DEFAULTS (SLOT-3); `kit-grid@2` name collision correctly avoided (r17b_prime.md "Method `kit-grid@2`"; kit-grid.tsv header) (held).
- D77: applied to grid1 quantities and memchr-back (held); unevenly to derived noise (SLOT-10) and SIMD vany* cards (unrouted forms carded for an undesigned C9 row: ruled by C9 "SIMD-form cards join stage 2", so accepted, but the key list is pre-chosen for a reader whose design picks its keys).
- D149: gate_e6, z, +40 % allowance, 5 launches all labelled (held).
- D157: noise travels as a stated fact; no kit method in pcrec (held).
- D166 + add. 2: conflict found correctly; mis-framed (SLOT-3). Fresh id per run (D186 add. 2 over D176 Q3's "new revision") held.
- D176 Q1/Q3: Q3 misquoted and §7.1's one-driver home not engaged (SLOT-2); Q1's "plan_cost.def rows migrate" narrowed (SLOT-7).
- D186 add. 2 C9: SIMD cards in stage 2 (held); the smp20 SIMD arm is not `none` (SLOT-5).
- D153: stage 2 touches compose.c/formhash.c/ofsskip.c (comment) as a non-opt unit; J1 is the O3-WAIT look-ahead sweep, released by stage 1's completion (held).

## Goals (§1)
Ranked and checkable (held as a form). Order served: Goal 1 is undercut by the recommended §8.3 (B) (SLOT-3). Goal 4 ("least producer", "one cell generator") is undercut by a second home for raw cells and a third manifest (SLOT-1) and a kit-owned driver/writer beside §7.1's one driver (SLOT-2). Goal 3 is cheaper through the existing `cells` + checker path (SLOT-1).

## SIBLING OF A FAMILY
- raw cells: `cells` section (spec) / raw.tsv / cells.tsv -> one (SLOT-1).
- measure harness dirs: measure_sets §7.1 `measure/` (designed), kit_proof/measure (650), memfn/tests/g2, grid1's lane harness, now memfn/measure/ (SLOT-2). G2's builder reused (good).
- noise-state enum: pcrec side keeps `KS_MEAS_EMPTY` sentinel for `-`, kit side gets a 3-state enum; the row `status` column (measured/derived/fitted/null) is the sibling state. Acceptable (the seam needs UNSTATED), held.
- format version + digest domain: `KsDigest` roles (`pcrec-meas-1`, `pcrec-find-1`) are the family; a second role is the family's own extension mechanism (held). General form: a format->(parse columns, fold, domain) row table so format 3 is a row.
- policy constants: gate_e6 / z / MATERIAL / HORS_MIN (SLOT-7).
- pricers: smp20.py / census0.py (SLOT-8).

## GENERAL FORM + UNLOCKS
- A measured row is a DERIVATION over cells: `measured` rows get a declared estimator derivation (`launch-median-slope`, `arm-minus-null`) with `inputs` = cell ids, recomputed by the existing §3.2 checker. Unlocks: Goal 3 for free; the M3 install tool implements a spec, not a python script; noise rules become one table column. Trigger: S2a (format 2 is the event that would carry it).
- One noise-policy table (gate default, z, margins). Unlocks row 1's E2 family unification. Trigger: row 1.
- The census as THE priced-forecast tool (census0 subsumes smp20 and each later row's mover forecast). Trigger: S2b.

## PROBED-AND-HELD
- mf_measure layout (memfn.h:1226-1231 {key,value_e6,unit,source}), kit readers compose.c:895 only by grep of `mf_measure` (finder.c lookups by rows); 3 constructors (cli/main.c:160, memfn_sites.c:89, arm_fixtures.c:1562): matches §4.1's three.
- Zero-init of appended fields refuses unedited constructors (compound literals zero trailing members): the design's mechanism works.
- `pcrec-meas-1` digest: ks_measures.c:245, .h:114 as cited; format refusal at ks_measures.c:305 as cited.
- `kit-grid@2` taken (kit-grid.tsv header: "`ver 2` ... is grid2's prep lane's, NOT written here"): held.
- `formhash.c` canon() walk/libc only (:237-241): held.
- Token grammar allows `-` (measures.md §2.3 `token := [A-Za-z0-9_+-]+`): `vrun-w16` keys legal.
- Unit row: spec §3.1¶2 (a ratio of value 1e6; any row by `unit_key`): `find_byte.walk` legal.
- `RX_MEASURES ""` on `(?i)x/1234` default, `--measures=zen4-grid1`, and `-fmemfn-simd` (3 compiles); default vs `--measures=zen4-grid1` byte-identical except the output-name include line: §5's no-mover premise holds at that site.
- R-35, span_pick stage 2 lists, D186 add. 2 (C9, fresh id), D166 + add. 1-3, D176 Q1-Q5, [MEASURE-SET] row: read at 80341284e.
- 6 compiles total.
