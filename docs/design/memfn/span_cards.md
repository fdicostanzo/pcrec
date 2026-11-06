# span_cards — span_pick STAGE 2: the cards, their producer, the noise channel (design, rev 1)

**Status: PROPOSED, rev 1 (lane s2rev1, 2026-11-06), over rev 0 (lane s2design). DESIGN ONLY: no code, no
make, no timing, no box job. The design of record for span_pick stage 2** (`span_pick.md` rev 5.2 §Staging
"Stage 2", §Cost cards, §The pick; kit request R-35, `memfn/docs/requests.md:805`; Frank's GO 2026-11-06,
plan 80341284e). Rev 1 applies review `docs/dev/reviews/2026-11-06-r4-memfn-span-cards.md` as ruled by the
kit manager (its "## Rulings" section), main's DEFAULTS ruling (B), D188 (Frank, 2026-11-06, homed here) and
Frank's SIMD end-state ruling D188 add. 1 (per-target variants; applied by the manager after delivery, `[rev1 D188a1]`). **Read §R1 (every finding id to its answer) and §0 first.** Changed
text is marked `[rev1 <id>]`; unmarked text is rev 0's, still valid. Cites are to the kit branch at the
review's build tree (main fb22c62a6 + the kit branch) unless a commit is named; spec files by section number.

## R1. What revision 1 changed, by finding

Every id of the review is answered here, in a section of this note or as PLAN/NOTED with its home.

| id | ruled | answered in |
|---|---|---|
| DRIFT-1 (D188) | FIX-NOW | §2.7 (the three facts, model-neutral), §3.2 (fact (b) is what a fixture's built code contains), §9 S2g |
| PREMISE-1 + SLOT-5 | FIX-NOW | §2.5 (row 1 prices the SCALAR layer only, SIMD forms ride as rungs; the cost stated), §2.7 |
| PREMISE-2 | FIX-NOW | §3.2 (cell builders named per family and site shape; vrun's RUN-term regime goes with J6, HELD) |
| PREMISE-3 | FIX-NOW | §3.2 (formhash gains a declared entry table: id, site shape, stated facts, policy), §9 S2c (re-costed) |
| PREMISE-4 + SLOT-3 + CONTRACT-4 | main RULED (B) | §8.3 (the flip at S2e and the three texts it amends), §1 Goal 1 (restated), §9 S2e (S1229 re-aim) |
| PREMISE-5 | FIX-NOW | §3.2 (the two-member walk is a site FACT on the composer's FIND site; a kit.h-only test entry if not) |
| PREMISE-6 | DOC | §10.2 (span_pick amendment: `kit-grid@2` -> `kit-grid@3`) |
| PREMISE-7 | FIX-NOW (text) | §2.7 (vany dropped; `kit-kernels@1` keeps governing vany, kit-kernels.tsv unchanged) |
| PREMISE-8 + CONTRACT-2 + SLOT-6 | FIX-NOW | §4.2 (the claim restated "on the shipped loader path"; both test levers hand UNMEASURED always) |
| PREMISE-9 + SLOT-12 + CONTRACT-9 | DOC | §4.1, §8.2 (three constructors), §4.3, §2.1 (7 rounds vs grid2's slot), §8.2 (kit-grid.tsv's per-version unit sentence) |
| PREMISE-10 | DOC (+ FIX-NOW with COST-5 (8)) | §7 (cite span_pick; census0 commits the P-blind count as a golden line) |
| PREMISE-11 | DOC | §3.7 (fixed 7 launches, no rerun allowance; 0.95 s cited as regime_eval's upper-bound figure) |
| PREMISE-12 | DOC | §3.7 (`docs/dev/lanes/r33_report.md` Sources line) |
| PREMISE-13 | DOC | §3.6 (`<h>wa = 128, <h>wb = 128`) |
| MEAS-1 | FIX-NOW | §3.2 (the A/A twin is a PERTURBED build of identical text), §9 row (j) |
| MEAS-2 | FIX-NOW | §3.5 (`noise_e6 x 10^6 <= gate_e6 x value_e6`, value > 0 required; cost rows only) |
| MEAS-3 | FIX-NOW | §3.5 (delta rows take `measure_sets.md` §7.4's NULL rule, never refuse a group) |
| MEAS-4 | FIX-NOW | §3.4 (A/A per arm, on the value), §3.5 (unit group = walk + walk#b only) |
| MEAS-5 | FIX-NOW | §3.4 (the literal integer recipe: cells, slope, event delta, normalization, medians, spread, root) |
| MEAS-6 | FIX-NOW | §2.3 (`find_hit` is per density, one group each, at row 1's mass range), §3.4 (event delta in one group) |
| MEAS-7 | FIX-NOW | §3.5 (one walk control per JOB, threshold from the between-launch spread, a stated size that matters) |
| MEAS-8 | FIX-NOW | §3.6 (paired per-launch sign + margin, a family majority rule; drilled) |
| MEAS-9 | FIX-NOW (text) | §6 (the error the band covers, z re-derived: 3.0, drilled) |
| MEAS-10 | FIX-NOW | §3.4 (the spread drops the one launch farthest from the median), §3.5 drill table |
| MEAS-11 + SLOT-9 | NOTED -> folds into MEAS-5 | §3.4 (every row is a per-launch ratio to that launch's own unit control) |
| MEAS-12 | FIX-NOW (text) | §2.3 (the buffer pool pinned on the card's `subject`); confirm later, trigger in §2.6 |
| MEAS-13 + CONTRACT-6 + COST-1 + SLOT-10 | ACCEPTED, strong form | §4.3 (derived rows carry `-` noise; no engine, no §3.2 column, sabotage (6) dropped), §12 (the general form as an unlock) |
| MEAS-14 | DOC | §3.7 (one window figure: 35 minutes; J3 counted from §2.5's keys) |
| SLOT-1 | FIX-NOW | §3.8 (per-launch cells in the set's `cells` section; no `raw.tsv`, no `cells.tsv`), §4.4 |
| SLOT-2 | FIX-NOW | §3.1 (split along `measure_sets.md` §7.1's seam; the D176 Q3 misquote fixed) |
| SLOT-4 | FIX-NOW | §2.4 (one dim name `form`, key token = canon id, check C's guard keyed on the deps column) |
| SLOT-7 | PLAN + DOC | §6 (z's home is [KIT-POLICY-TABLE], filed by main, trigger row 1; rev 0's narrowing withdrawn) |
| SLOT-8 | FIX-NOW (text) | §7 (census0 REPLACES smp20; `smp20.out` its one-site golden) |
| SLOT-11 | DOC | §9 (ids are the kit's, from the top of the free range at build time, R-35) |
| CONTRACT-1 | FIX-NOW | §3.8 (no format-2 file under `memfn/data/sets/`), §5, §9 row (o) |
| CONTRACT-3 | FIX-NOW (text) | §4.5 (`scripts/ksgen.c`, the regenerated `measures_table.inc`, the KsKind digest role), §8.2 |
| CONTRACT-5 | FIX-NOW (noise half) + PLAN (value half) | §4.1, §4.4 (the loader refuses noise past 10^15, S2a); the value half is pcrec's **K138** (main), not this note's |
| CONTRACT-7 | DOC | §4.5 (format 1: no parsed-noise field; grid1's decoded view byte-identical) |
| CONTRACT-8 | FIX-NOW (text) | §4.2 (MFMEAS prints a text digest of the handed triples), §9 rows (e), (f) |
| COST-2 | DOC | §7 (census0's output lives in `span_pick/`), §9 S2b |
| COST-3 | NOTED, for main | §2.7 (vany cards dropped; C9-scope context for main) |
| COST-4 | FIX-NOW (text) | §4.1 ("the next free MF_SITE_ABI at landing"), §8.1, §9 (each unit names its base and re-baselines), §2.6 (`enter` staleness) |
| COST-5 | FIX-NOW (text) | §9 (every sabotage row states why it can go red) |
| COST-6 | DOC | §8.2 (the `--list-measurements` readers by name; mfixtures `format 2` row; memfn CLAUDE.md gate) |
| COST-7 | NOTED | §9 (separability) |

Main's and the kit manager's rulings beyond the table, each with its home: DEFAULTS (B) §8.3; D188 §2.7; the
SIMD model ruled (D188 add. 1) §2.5, §2.7, §9 S2g; derived noise dropped §4.3, §12; `cells` and the §7.1 seam §3.1, §3.8;
the executable estimator §3.4, §3.5; MF_SITE_ABI at landing §4.1, §9; sabotage ids and why-red §9; K138 §4.1.

## 0. The decisions, one line each

| # | question (brief item) | decision | where |
|---|---|---|---|
| 1 | the cards | four quantities under a NEW method version `kit-grid@3`: `find_byte`, `find_hit` `[rev1 MEAS-6]` (per density), `verify_cmp`, `enter`; the UNIT row is `kit.find_byte.walk`; every key read by row 1; `[rev1 PREMISE-1]` scalar forms only: row 1 prices the scalar layer and SIMD forms ride as rungs; `memchr-back` DEFERRED (no reader); `hors.probe`/`find_hit(hors)` out (R14c) | §2 |
| 2 | the producer | `[rev1 SLOT-2]` split along `measure_sets.md` §7.1's seam: the KIT contributes probes (cell texts rendered through G2's generators) and card rows; the estimator, gates and NULL rule are SPEC text (`measures.md`'s new sections 3.4-3.5) that M3 later implements; this one run's harness is a slot harness (§7.1 (d)), evidence, never built by make; the writer is pcrec's canonical writer. `[rev1 SLOT-1]` Per-launch cells go in the set's own `cells` section | §3 |
| 3 | the noise channel | `mf_measure` gains `noise_state` + `noise_e6` appended LAST (`[rev1 COST-4]` the next free MF_SITE_ABI at landing; an UNSTATED state is REFUSED); noise reaches the kit only from a set whose digest covers it, `[rev1 PREMISE-8]` on the shipped loader path; `[rev1 MEAS-13]` derived rows carry `-` noise (UNMEASURED): no derived-noise rule | §4 |
| 4 | noise in the digest | set FORMAT 2: `noise_e6` is a parsed value and the digest domain is `pcrec-meas-2`; format 1 stays legal and unchanged, so zen4-grid1@1, its digest `13a6536315af1520` and its file sha stay byte for byte | §5 |
| 5 | the coverage factor | `[rev1 MEAS-9]` z = 3.0 (`COVER_Z_E3 3000`): a 2.3 % one-sided false departure on an equal-price one-card comparison, for the noise §3.4 defines (7 launches, a trimmed spread), drilled; UNMEASURED DEFAULT (D149); `[rev1 SLOT-7]` its home is [KIT-POLICY-TABLE], written WITH its reader at row 1 | §6 |
| 6 | the step-0 gate | CONFIRMED: D176 Q3's "step-0 census" = SRS §7 step 0. Its trigger is met in advance; it runs FIRST anyway, compile-only, because its population SCOPES the card grid (D77); `[rev1 SLOT-8]` census0 REPLACES smp20 | §7 |
| 7 | what stage 2 moves | NO emitted byte, NO pcrec abi, NO stamp value. Moves: MF_SITE_ABI (next free); set format 2 + digest domain 2; a new built-in set zen4-grid3@1; `kit-grid@3` card rows; form-hash entries; `[rev1 PREMISE-4]` DEFAULTS `idk` -> zen4-grid3@1 at S2e (main RULED (B)), zero movers | §8 |
| 8 | build plan | SIX scalar units S2a-S2f; one timing window (S2d, ~35 min); `[rev1 D188]` J6 (SIMD, vrun only) is unit S2g, SEPARABLE and HELD until the SIMD model is ruled; `[rev1 SLOT-11]` sabotage ids the kit's, each row with why it can go red | §9 |
| 9 | questions | none for Frank from this note (the SIMD model is ruled, D188 add. 1); five items for main | §10 |

## 1. Goals

Ranked; a higher goal wins a conflict (`docs/dev/guide/architecture.md`).

| # | goal (who benefits) | measurable form |
|---|---|---|
| 1 | **Stage 2 moves nothing a caller sees** (every user; span_pick Goal 2's stage-2 cell; R-35 "adds no reader, moves no emitted byte") | `scripts/emit_sweep.py` byte-identical on EVERY arm (default, each deny, `--engine=vm`, both SIMD layers) at each unit's HEAD against `[rev1 COST-4]` its NAMED base commit, stamps included; every `<PREFIX>_MEASURES` is `""`; zen4-grid1@1's file sha and digest unchanged; `[rev1 PREMISE-4]` `--list-measurements` (no value) changes ONLY at S2e and by exactly TWO rows: zen4-grid3's new row (`default_for` `idk`) and zen4-grid1's row (`default_for` `idk` -> empty) |
| 2 | **Every card row row 1 prices is measured with its noise** (row 1's lane; span_pick §The pick 4: a card without noise cannot qualify) | every key §2.5 lists for row 1 is `measured` with `noise_e6` set (or `null` by §3.5's NULL rule) in zen4-grid3@1, or the set is PARTIAL and names it; the unit group passes its half gate and bimodal test |
| 3 | **The set is self-checking from kept data** (the next editor; K35) | `[rev1 SLOT-1, MEAS-5]` a pcrec-side check recomputes every measured row's `value_e6`, `noise_e6` and NULL status, and the `partial` verdict, from the set's own `cells` section EXACTLY by the spec's integer recipe (`measures.md`'s new sections 3.4-3.5), and the format-2 digest from the rows, each by code that shares no source with the producer |
| 4 | **The least producer that gives a trustworthy set** (Frank 2026-10-21, pcrec-test-harness-minimal) | `[rev1 SLOT-1, SLOT-2]` no second home for raw data (the `cells` section), no second set writer (the canonical writer), the kit's G2 generators as the only cell renderers; no card without a named reader (D77) |

**Non-goals.** Any priced reader (row 1's). Unit 3.0. Retuning `PAIR_LOOKAHEAD` (a later unit change if the
sweep says so, §3.6). The SIMD official verdict (D144 add. 4: pcrec-bench). `[rev1 D188]` Any SIMD card
(J6, HELD: §2.7). Horspool's cards (R14c). The bundle-side sampling noise (§4.6). Derived-row noise (§4.3).
A between-window drift term (§3.5, a known gap with its trigger).

## 2. The cards

### 2.1 The method version: `kit-grid@3`

The set's `method` header is one `owner-name@ver` (`measures.md` §2.1¶1) and a set's `cards` must equal the
owner's committed rows at that ver (`measure_sets.md` §7.2). The span cards are quantities of the grid's
successor method (span_pick.md:266-267), but **`kit-grid@2` is TAKEN**: it is the method grid2's slot ran
under (`r17b_prime.md:2040`, "Method `kit-grid@2`"; :2059), never written to `memfn/data/cards/kit-grid.tsv`
(its header: "`ver 2` ... is grid2's prep lane's, NOT written here") and never committed to the store. D186
add. 2 refused to reuse `zen4-grid2` for the same reason (a name its readers already mean). So the new
method is **`kit-grid@3`**, appended to `kit-grid.tsv` (append-only by version). `[rev1 PREMISE-6]`
span_pick.md's own `(kit-grid@2)` is amended (§10.2).

**Relation to `r17b_prime.md` §5.4** (grid2's one slot spec): kit-grid@3 KEEPS its run rules (one box, one
method version, gcc 15.2 `-O2`, `taskset`-pinned, rotated interleaving, the per-launch median, the quiet gate
at every group boundary, the correctness gate before any clock, perf optional per D166 add. 1) and CHANGES
what is timed: §5.4 timed whole pcrec artifacts (grid1's harness, `docs/dev/lanes/grid1/README.md`);
kit-grid@3 times the kit's rendered FORM TEXT in a fixed find-all loop (§3.2), whole artifacts only where
the quantity is the consumer's (`enter`, §2.3) or the charter names a pattern (the PAIR sweep, §3.6).
Cross-set comparison is only within one `method@ver` (`measure_sets.md` §1.4), so zen4-grid3's ratios are
not compared with grid1's. `[rev1 SLOT-12]` Rounds: 7, as grid2's §5.4 slot ran (kit-grid@1's cards say 5;
a new version may differ). `[rev1 MEAS-9, MEAS-10, MEAS-14]` Launches: **7, fixed, with no rerun rule**
(rev 0: 5, +2 by rev3 C7's cross-launch trigger). grid2's trigger fired in 28 of its 32 F1 reruns, so a
"+2 when spread exceeds the floor" rule is close to "+2 always"; a fixed 7 gives the spread estimate about
five degrees of freedom after the trim (§3.4), an odd launch count (a true median), and a box time that is a
number, not a range.

### 2.2 What carries over from kit-grid@1: only the unit's regime

D77: a grid quantity no reader reads is not re-measured. At this branch no kit row reads a set key
(`measures.md` §4¶4; R1/R2/R8 retired at span_pick 1f; `kit.h3a`/`kit.gstar.*` "stay in zen4-grid1,
unread", span_pick.md:372), so none of grid1's ten quantities (`beta saving eps f xover block delta ccold
wuse gstar`) is re-measured. The UNIT is: its regime is pinned by the card ("streamed, fresh, long,
member-free", `measure_sets.md` §1.4), and that is exactly `find_byte`'s regime, so **the unit row is
`kit.find_byte.walk`** (value 1,000,000 by construction; `unit_key` may name any row, `measures.md`
§3.1¶2). byte(walk) in span_pick's price IS the unit: one row, not a unit row plus a walk row that
measure the same text twice. The unit group keeps §1.4's half gate and bimodal test. `[rev1 MEAS-4]` The
unit group holds the walk and its A/A twin ONLY; every other arm is in another group.

### 2.3 The four quantities

Key grammar (`measures.md` §2.3): a quantity is `[a-z][a-z0-9_]*`, so span_pick's `find.byte` is spelled
`find_byte`. Units (`measures.md` §3.1): `ratio` = per subject byte relative to the unit; `walkbytes` =
a per-event cost in u.B. Tokens are the kit's own (the format reads no owner's vocabulary, §2.3¶2).
`[rev1 SLOT-4]` The first dim of every quantity a kit form renders is `form`, and its token is the form's
canon id (§2.4).

`[rev1 MEAS-12]` **The subject pool is pinned.** "Streamed-fresh" is a POOL of distinct seeded buffers the
loop cycles through, never one buffer re-read: the pool is **16 MiB** (beyond the 7700X's 1 MiB L2, inside
its 32 MiB L3), stated on every card's `subject` token as `pool16Mi`. memchr's and PAIR's rates move with
the cache level and the walk's do not, so the RATIO is a property of the pool; 16 MiB is the bench's
throughput regime (1 MiB subjects re-scanned, L3-resident), an UNMEASURED choice (D149) with its trigger in
§2.6.

| quantity | dims | unit | subject (the card's regime) | points | estimator (§3.4) | per |
|---|---|---|---|---|---|---|
| `find_byte` | `form` | ratio | streamed-fresh `pool16Mi`, MISS-ONLY (no member in the subject) | lengths 64 Ki, 256 Ki, 1 Mi | `slope` over the three lengths | subject byte, all the method's streams (span_pick.md:216) |
| `find_hit` | `form;landing;split;gap` `[rev1 MEAS-6]` | walkbytes | streamed-fresh `pool16Mi` 1 Mi subjects, hits planted `periodic` (every g bytes) or `random` (seeded uniform, mean gap g); `split` `one` (one member occurs) or `alt` (both members, alternating) | `[rev1 MEAS-6]` g in {256, 1024}, each its OWN row and group | `delta` against the same form on the miss-only 1 Mi subject, per hit | candidate returned and restarted |
| `verify_cmp` | `form;cls;pass` | walkbytes | a fixed candidate array (positions spread over a 1 Mi fresh buffer), compared bytes seeded so the test passes with probability 0 (`p0`) or 1/2 (`p50`); a failing run differs at a uniformly seeded position | one point | `delta` against the `null` arm (same loop, compare replaced by a constant), per compare | one compare: cmp0, cmp½ (span_pick.md:220) |
| `enter` | `kind;entry` | walkbytes | a WHOLE ARTIFACT (`build/pcrec`) of a fixture pattern whose site states `kind` and an alternative of `entry`; candidates every 256 bytes that pass every verify position and die in the consumer one byte past the window (`die1`) | one point (g = 256) | `delta` of the pass subject against the fail subject (candidates fail the last verify position), per candidate | candidate passed on (span_pick.md:222) |

`[rev1 MEAS-6]` **Why per density.** Rev 0's one `find_hit` slope over g in {4096, 256, 32} plus the
miss-only point spanned four groups and two jobs, and its least-squares weights put 74 % of the slope on
g = 32 (31,250 ppm), far denser than row 1's masses (1,097 ppm for `{x,X}`, 4,154 ppm for '/': g ~ 912 and
~241, span_pick.md §Robustness). Periodic hits at g = 32 are branch-predictable where g ~ 900 random hits are
not. g in {256, 1024} brackets row 1's range; each density is one row measured inside ONE group against a
miss-only base in the same launch, so its A/A, gate and NULL rule have one group to refer to. WHICH density
(or both, as regimes) the price reads is row 1's design item (§10.3), with the landing pair.

`[rev1 MEAS-6]` **`enter` at one density.** The pass-minus-fail difference at one candidate count cancels the
per-byte and per-candidate find costs (both subjects run the same find on the same positions), so rev 0's
second density bought nothing the difference does not already remove.

`[C10]` (span_pick.md:258): `enter` BAKES IN its fixture's survival (the consumer dies one byte past the
window); the alternative (a pcrec-stated survival x a per-byte card) waits for a reader that states survival.

`[rev1 PREMISE-1, D188]` **No SIMD form is a stage-2 card** (rev 0 carried vrun and vany as method tokens
here). §2.5 states row 1's position; §2.7 carries D188 and the held SIMD job.

### 2.4 The card rows (`kit-grid@3`, appended to `memfn/data/cards/kit-grid.tsv`)

`gate_e6` 30000 is grid1's UNMEASURED DEFAULT (D149) carried; the unit group gates at half (§1.4).
`[rev1 SLOT-4]` `deps` are R-MS3 form ids; a card whose `deps` names `kit:form.<form>` has `form` as a dim,
and the key's `form` token IS the canon id (`libc`, never `memchr`: canon's `libc` id is the libc forward
one-byte find, memchr; `formhash.c:240`). The ids marked NEW gain `formhash.c` entries in unit S2c (§3.2).
`[rev1 MEAS-1, MEAS-4]` `aa_rule` `twin-per-arm`: every timed arm has its own perturbed A/A twin (§3.2);
the unit's adds `bimodal-unit` (§3.5). `[rev1 MEAS-5]` `lengths` names the row's ESTIMATOR in the spec's
grammar (§3.4), so a card says how its rows are computed.

| owner | quantity | ver | dims | unit | subject | lengths | launches | rounds | aa_rule | gate_e6 | env | deps |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| kit | find_byte | 3 | form | ratio | streamed-fresh pool16Mi miss-only | slope 65536,262144,1048576 | 7 | 7 | twin-per-arm;bimodal-unit | 30000 | - | kit:form.\<form\> (walk, libc; pair, walk-set NEW) |
| kit | find_hit | 3 | form;landing;split;gap | walkbytes | streamed-fresh pool16Mi landed:periodic\|random | delta base.\<form\> 1048576 per-hit | 7 | 7 | twin-per-arm | 30000 | - | as find_byte |
| kit | verify_cmp | 3 | form;cls;pass | walkbytes | candidate-array pass:0\|1/2 | delta base.null.\<cls\> 1048576 per-compare | 7 | 7 | twin-per-arm | 30000 | - | kit:form.\<form\> (settest, rc-words, rc-overlap, rc-bytes, rc-memcmp NEW; the census's (form, cls) pairs only) |
| kit | enter | 3 | kind;entry | walkbytes | artifact die1 g256 | delta base.fail.\<kind\>.\<entry\> 1048576 per-candidate | 7 | 7 | twin-per-arm | 30000 | - | `-` (kit side: the pass-minus-fail difference cancels the find form, §2.3); pcrec: OWED (§2.6) |

`walk-set` is the walk over a two-member stop (T-FIND's R7w). If S2c finds its text hashes as canon's
`walk` (one renderer row, the set test inlined identically), the id is `walk` and the `walk-set` keys fold
into it; the hash decides, never the name (§3.2).

`[rev1 SLOT-4]` **check C** (`tests/memfn/finder_check.py`, today resolving a dep only when the first dim is
`form`, :395-399) gains its guard on the DEPS column: a kit-grid card whose `deps` names `kit:form.` and has
no `form` dim is a red, never a skip; every key's `form` token must resolve to a canon id with a hash.
`enter`'s `-` kit dep is then explicit, not silently skipped.

`libc` deps also record `libc:glibc@<ver>` as provenance, never row staleness (`r17b_prime.md` §5.3).

### 2.5 Keys, and the reader of each (D77)

The population of keys is the step-0 census's (§7): a token below is measured only if the census finds a
row-1-class site that reads it.

| keys | reader | why that reader reads it |
|---|---|---|
| `find_byte.walk` (UNIT), `.libc`, `.pair`, `.walk-set` | row 1 | byte(m) of the methods row 1's candidates use: a one-member stop by memchr (`libc`) or walk, `{X,x}` by PAIR or walk (finder.c rows D1, D1w, PAIR, R7w) |
| `find_hit.{libc,walk}.{periodic,random}.one.{256,1024}`, `find_hit.pair.{periodic,random}.{one,alt}.{256,1024}`, `find_hit.walk-set.{periodic,random}.alt.{256,1024}` | row 1 | hit(m); the landing pair is the robustness regime span_pick requires (a random-like regime, §Robustness); WHICH landing and density the price reads is row 1's design item (§10.3) |
| `verify_cmp.<form>.<cls>.{p0,p50}` for the (form, cls) the census finds on row-1 sites | row 1 | cmp(f, p) at its two points (span_pick.md:220) |
| `enter.<kind>.NONE` for the kinds the census finds | row 1 | passes_r x enter on its NONE alternatives |
| `enter.<kind>.PARKED`, `enter.<kind>.RESEED`, same kinds | row 1's E2 family unification | span_pick.md:157-160: the "beat the incumbent by a margin" family unifies AT row 1, trigger the `enter` cards; MARGIN stays until the PARKED and RESEED cards exist (:257-258) |
| **HELD: `find_byte`/`find_hit` for `vrun-w16/w32`** | the C9 SIMD T-PICK row (D186 add. 2; span_pick §The pick 6) | `[rev1 D188]` J6, unit S2g, HELD until the SIMD model is ruled (§2.7) |
| **DROPPED: vany2/vany3 cards** | none | `[rev1 COST-3, PREMISE-7]` unrouted forms (`vany.c:16`), no reader (D77); §2.7 |
| **DEFERRED: `memchr-back`** | none | finder row D1c serves MLINE (`finder.c:270-275`); no priced row admits MLINE; D1c's own revisit trigger needs a libc-free back-find card that does not exist. R-35 and [MEASURE-SET]'s `next:` list it: For main (§10.1). Trigger: the first priced row admitting MLINE sites |
| **OUT: `hors.probe`, `find_hit.hors`** | the Horspool priced row (later) | R14c (span_pick.md:254-256): D-hors incumbents stay unpriced |

`[rev1 PREMISE-1, SLOT-5]` **Row 1 prices the SCALAR layer only; SIMD forms ride as rungs.** Rev 0 said "row
1's SIMD-on arm needs no SIMD card", and that is false on row 1's own witness: `(?i)x/1234` stamps
`RX_MEMFN_FORMS "none"` by default and `"vrun@w32+w16"` under `-fmemfn-simd` (the incumbent `{X,x}`'s fn-pair
body gains vrun rungs; the challenger '/' calls memchr on both layers, which is what D186 add. 2 C9's "NOT
smp20" speaks of). span_pick §The pick 6 offers two readings, and this note states one:

- **CHOSEN (recommended, natural under the hold): row 1 is a scalar-layer row.** Its prices read scalar
  cards only; under `-fmemfn-simd` its pick is the scalar pick, and the SIMD layer adds its rungs to
  whatever span was picked (§The pick 6's "else SIMD forms are rungs", D147). The C9 row, with SIMD cards
  and SIMD-on evidence, is the only way a SIMD layer picks its own span.
- (other) vrun keys are row-1 keys (measured by J2/J3, not J6). Refused here: it needs the SIMD cards whose
  build waits for [XARCH-DEV] (D188 add. 1), and it would make the scalar units depend on the held job.

**What the choice costs.** On a site whose scalar incumbent carries a SIMD rung (smp20's `{X,x}` ->
`vrun@w32+w16`), a scalar-priced departure to a span with no rung (memchr '/') can be SLOWER on the SIMD
layer than the incumbent was, because the price never saw the rung. Bounded: the SIMD layer is OFF by
default (D147); row 1's acceptance reading reports BOTH layers (memfn/CLAUDE.md, the layers rule), so a
SIMD-on loss is SEEN at row 1's landing verdict, not silent; and the C9 row is the named fix. The
alternative's cost is the hold itself: no row-1 key could be measured until the SIMD model is ruled.

### 2.6 Known gaps of the card set

- **`enter`'s consumer is pcrec's.** Its staleness cannot be a kit form hash; the set header's
  `code_commit` is the only record. A `pcrec:` dep id for the consumer's entry text is OWED, trigger: a
  re-measure showing `enter` moved beyond noise on a consumer-only change. `[rev1 COST-4]` Two byte-moving
  pcrec lanes land on main around stage 2 (variable lookbehind stage 1; the alternation normal form stages
  1/2p/2b, R-35 Concurrency). The window's frozen commit is main's tip when S2d is enqueued, recorded as
  `code_commit`; an entry-text change landing after it stales the `enter` rows, recorded in
  PROVENANCE.md as the known staleness with the trigger above. The window is NOT held for the landers.
- **Isolation.** A form timed in the fixture's loop is not the form inside a DFA's register pressure: that
  is model error, which span_pick puts OUTSIDE the band and in row 1's predicted-vs-measured print
  (span_pick.md:283-284). The cards make no in-situ claim. `[rev1 MEAS-1]` The perturbed A/A twin (§3.2)
  measures the fixture side of the placement effect; the in-DFA side stays outside the band.
- `[rev1 MEAS-12]` **The pool level.** The ratio of memchr/PAIR to the walk is a property of the pinned
  16 MiB pool. Trigger to re-pin: a find_byte(libc) re-measure at a 256 MiB pool moving the ratio beyond
  the row's noise, or row 1's predicted-vs-measured spread (R5.3) on long subjects.

### 2.7 `[rev1 DRIFT-1]` SIMD: D188's facts, and J6 (HELD)

**D188** (Frank, 2026-11-06, homed in this rev). Per SIMD level (memfn's `levels.def`), a measurement set
records three facts:

- **(a)** the CPU has it (cpuid), else "absent (CPU)", never run;
- **(b)** the BUILT fixture contains code for it, read off that artifact's `MEMFN_FORMS` stamp, else
  "absent (build)", never timed;
- **(c)** its cost, only when (a) and (b) both hold.

A set never grants availability; it only prices. Availability on a target stays with the target's compile
(D147, D144 add. 4); letting measured cards enable a level is the C9 row plus the separately ruled
SIMD-default event.

**The SIMD model is RULED (D188 add. 1, Frank 2026-11-06; manager's edit after delivery, `[rev1 D188a1]`).** There are
no `#if` arms in the end state. A code path is a per-target VARIANT, planned and priced for its DECLARED target.
One artifact may hold several variants (generic plus 1-2 SIMD) as target-attributed functions behind a
once-per-process CPU dispatch, each variant's entry exposed. The target set is an explicit caller-given LIST
with a declared, stamped default, never assumed. D188's three facts are therefore read PER DECLARED TARGET:
(a) the CPU has the target's features; (b) the built fixture contains that target's variant; (c) the
variant's cost, only when (a) and (b) hold. A set prices a variant; it never grants a target. The build of
variants waits for [XARCH-DEV]'s go, and the details are settled there. This note never builds on `#if`
fall-through. One observation for main (§10.5) stands for TODAY's tree only: `MEMFN_FORMS` names the levels
the emitted TEXT carries (`match_api.md` §6.3.10¶4: "`ID@LEVEL+LEVEL`"), so under today's `#if` arms a stamp
can name a level the fixture's own compile excluded. Under variants, fact (b) is read off the artifact's
declared-target list, and its spelling is J6's design item at [XARCH-DEV].

**What zen4-grid3@1 records under D188.** It is a SCALAR-ONLY set: every cell is `MF_P_PORTABLE_ONLY` text
(§3.2). (a): the measuring box's cpuid feature list in the header's `isa` key (provenance, existing);
(b): absent (build) for every level, stated in PROVENANCE.md, because no stage-2 fixture is built with SIMD
text; (c): none. The in-format spelling of (b) and (c) per level (rows, a section, header keys) is a format
event that J6's design makes, when there is a level to record present.

**J6 = unit S2g, SEPARABLE and HELD until [XARCH-DEV]'s go (D188 add. 1).** Content once released: vrun only (`vrun-w16`, `vrun-w32`; the kit
manager's ruling drops vany, §2.5). Its cells cannot come from the scalar builders: vrun renders only through
window row B-fn on ONE RUN term with REACH >= VW + T (`vrun.c:19-25`), and its G2 family is
`g2_simd_gen.c` (a policy word without `MF_P_PORTABLE_ONLY`), so its `subject` is a RUN-term regime of its
own (run length, mask hit rate, verify), designed with the model. Its form hashes need `formhash.c` entries
under a SIMD policy (today hard-wired PORTABLE, `formhash.c:291`). It records D188's facts per level and
times only levels where (a) and (b) hold. **Nothing in S2a-S2f depends on it**: no scalar card, gate,
estimator line or witness reads a SIMD cell. A set is one run (D166), so J6's rows join the NEXT set id,
measured with the scalar cards it is compared against (scalar the bar, D147), never appended to
zen4-grid3@1.

## 3. The producer

### 3.1 `[rev1 SLOT-2]` Where it lives: along `measure_sets.md` §7.1's seam

`measure_sets.md` §7.1 designs ONE install-time driver (`pcrec-measure`, M3) that owns run control, the card
interpreter, the NULL rule and the set writer, while **"Owners supply METHOD CARDS (§7.2) and PROBES. A kit
quantity is measured by the kit's harness mode: the forms and their timing arms are the kit's"**; it priced
and REJECTED "(b) a mode of the kit's harness only" (inverts ownership) and "(c) one python script" (install
time must not need python). Rev 0's `memfn/measure/` (a kit-owned driver, estimator, gates and interim-set
writer) was (b). **Rev 1 splits along the seam:**

| part | owner and home | built by make |
|---|---|---|
| PROBES: the rendered text of every kit arm, and its form hash | the kit: G2's generators gain a `--cards` mode (§3.2), `memfn/tests/g2/` | as G2 is today (the kit's own checks) |
| METHOD CARDS | the kit: `memfn/data/cards/kit-grid.tsv` `ver 3` rows (§2.4) | no (data) |
| the ESTIMATOR, the GATES, the NULL rule | SPEC text: `docs/spec/measures.md`'s new sections 3.4-3.5 (the format's own rule for a set that publishes cells), written so M3's C driver implements the same text | no (text) |
| the WRITER | pcrec's canonical writer, `pcrec --list-measurements FILE` (`measures.md` §6¶2); the format-2 digest by `tests/knowledge/ks_ref.py`, verified by the C loader on load (two independent implementations) | yes (existing) |
| THIS RUN's harness: driver, subject generator, the slot's implementation of the spec's estimator, the job scripts | a SLOT HARNESS (`measure_sets.md` §7.1 (d), "slots only", for this one run): `docs/design/memfn/span_cards/slot/`, evidence like `docs/design/kit_proof/measure/` (the 650 template) and grid1's `docs/dev/lanes/grid1/` | no, never |
| the RECOMPUTE CHECK (Goal 3) | pcrec: `tests/knowledge/`, written from the spec's text, sharing no source with the slot harness | yes (`make test`'s measures section) |

**Why a slot harness, and why that is not (b) or (c).** M3 is unbuilt and unscheduled (D77: no measured need
for an install-time tool yet). Stage 2 is ONE run on ONE box, which is what a slot is; (b) and (c) are
rejected as the INSTALL-TIME tool, and nothing here becomes one. The harness owns no format text: the
estimator and gates it runs are the spec's, so when M3 is built it implements `measures.md`'s new sections 3.4-3.5 and
the slot harness stays behind as evidence. Python is fine for a slot (§7.1 (c)'s objection is install
time). The kit owns no writer: the set is written by pcrec's canonical writer.

`[rev1 SLOT-2]` **The D176 Q3 misquote, fixed.** Rev 0 quoted D176 Q3 as "the kit contributes its method cards
to that script"; that phrase is in neither decisions.md nor plan.md. D176 Q3 says: the kit measures this box
"as a new revision of the box's set, in a night window cleared with Frank, gated on the step-0 census. The
library (a canned self-contained pcrec measuring script, closest-match selection over declared fallback rows,
targeting another machine, the generic envelope) is [MEASURE-SET], already filed; `plan_cost.def` rows migrate
into the sets." The owner-supplies-cards-and-probes division is `measure_sets.md` §7.1's, quoted above.

### 3.2 The timed text, and the cell builders

`[rev1 PREMISE-2]` Rev 0's "ONE window-site builder ... one stop set S at offset 0" cannot render every
arm. Rev 1 names the builder per arm, all of them existing G2 generators (no new builder):

| arms | builder (`memfn/tests/g2/`) | site shape | how the form is reached |
|---|---|---|---|
| `walk` (unit), `libc` (memchr), `pair` | `g2_win_gen.c --cards` | a window FIND site, stop at the candidate | its FACTS: a one-member stop takes D1 (`libc`); `--memfn=no-fd-d1` takes D1w (`walk`); a two-member `{X,x}` stop takes PAIR (the window family's asker renders PAIR, `kit.h` `fd_stop.renders_pair`) |
| `walk-set` | `g2_win_gen.c --cards` through the composer's FIND site (`mf_define`, :1048) | a composer FIND site, its span 0 the two-member set | `[rev1 PREMISE-5]` a FACT, not a deny: PAIR holds only for an asker that renders PAIR, which "the composer's renderers do not" (`kit.h:546-555`, `finder.c:656`), so T-FIND's own first match there is R7w. If S2c finds the composer's R7w text differs from the window's R7w text in anything but names, the lever is a `kit.h`-only TEST entry stating `renders_pair = 0` at a window site: no `options.def` row, no `--memfn=` name, no caller lever (pcrec-flag-follows-caller-effect: a test-only lever) |
| `verify_cmp` forms (`settest`, `rc-*`) | `g2_win_gen.c --cards` | a window site whose verify plan T-VERIFY picks | the FACTS that make T-VERIFY pick each (form, cls) the census lists (run length and alignment for `rc-*`, a set position for `settest`); a pair no fact set reaches is reported by S2c, never forced |
| `null` (verify base) | the driver | the candidate loop with the compare replaced by a constant | — |
| `enter` arms, J1's widths | `build/pcrec` (whole artifacts, `--emit-main`-free, the driver links them) | the fixture patterns | the patterns' own sites |

All of them are `MF_P_PORTABLE_ONLY` (every `mf_art_begin` in `g2_win_gen.c` passes it: the scalar layer,
which is all stage 2 times). **The answer gate**: G2's existing reference check (`g2_win_run.c` holds every
answer to the facts, `g2_win_gen.c:18-19`) plus the driver's find-all count on every subject against the
subject generator's expected count, before any clock.

Each kit arm is wrapped as a `static` function the driver's loop calls from `pos` to `n`, counting
candidates, over the pool (§2.3).

`[rev1 MEAS-1]` **The A/A twin is a PERTURBED build of identical text.** Rev 0's twin ("a SEPARATE compile and
link of the same text") is the same binary: gcc is deterministic, and the 650 template even cmp-asserts the
two sources (`kit_proof/measure/measure.sh:71-72`). So its A/A held run-to-run noise, never placement. Rev 1:
the twin's translation unit is the arm's text, byte-identical, preceded by a top-level `.text` pad of 40
bytes (not a multiple of 16 or 64), and linked in the opposite object order; the timed loop's alignment
against cache lines and the uop cache therefore differs. The driver asserts BOTH: the arm texts `cmp` equal
and the two built objects `cmp` DIFFERENT; either failing refuses the dry run. D188's fact (b) is the same
class of question (what code a fixture actually contains), answered for J6 in §2.7.

`[rev1 PREMISE-3]` **Form hashes: a declared entry table, not canon() entries.** `mf_form_hash` is hard-wired
to `mf_art_begin(..., MF_P_PORTABLE_ONLY, ...)` + `mf_emit` on a plain STMT/FIND site (`formhash.c:291`);
PAIR holds only for the window asker, and `rc-*` are compare rows inside a run verify (`runcmp.c`), not FIND
sites. So S2c replaces `canon()`'s two-way branch with a declared table, one row per id: `id | site shape
(composer FIND / window FIND stop / window verify step) | stated facts | policy word | deny string`, read by
one renderer path. Rows at S2c: `walk`, `libc` (today's, byte for byte), `pair`, `walk-set` (or folded,
§2.4), `settest`, `rc-words`, `rc-overlap`, `rc-bytes`, `rc-memcmp` (the census's set). No `memfn.h` change
(the table is `formhash.c`'s; `mf_form_hash`'s signature stays). No SIMD id (S2g). **The cell-text check**
(COST-5 (10)): G2 `--cards` writes, beside every cell text, the hash of that text by `mf_form_hash`'s own
fold, and S2c's witness compares it with `mf_form_hash(<the key's form token>)`; a mismatch is red.

### 3.3 The job shape

Template: `docs/design/kit_proof/measure/650-covertime-slot`. Each job: `--dry-run` builds every arm and runs
the answer gate (no clock), prints `boxqueue: cap`, `patience none`, `idle-ok`, `est`, and `expect
groups=N lines=^== s2 GROUP done` (a population the work prints per group, so a short job is
POPULATION-SHORT, not green); `--ready` is 650's quiet gate (no running queue job, no box-lock holder,
load1 < 2.0 on two samples >= 55 s apart); the work is the slot harness's `run`. Pinned `taskset` to CPU 7,
sibling CPU 15 idle (650's pair; grid1 used 14, which only names a different core: the set's `box`
records it). Jobs chain with `after` and declare `not-before`/the window's times; one stage per job, each
under an hour (BOILERPLATE, Frank 2026-10-30). The quiet gate checks only the START (BOILERPLATE:236):
every group boundary re-checks load and records it. `[rev1 MEAS-7]` Every job's FIRST group is its CONTROL:
the walk's miss-only text at the three find_byte lengths (in J2 this IS the unit group); §3.4 normalizes
each launch by it and §3.5 checks drift with it.

### 3.4 `[rev1 MEAS-5]` The estimator, literally (the spec text of `measures.md` new §3.4)

Rev 0's §3.4 was not executable (a slope of a per-byte figure over length, a miss point borrowed from
another job, an unnamed A/A arm, an unstated spread unit and order of operations). Rev 1 states it as the
spec will, integer by integer. Notation: `rhafz(n, d)` and canonical order are `measure_sets.md` §1.7's
(round half away from zero, truncating division, int128 intermediates in C, integer `divmod` in python);
`isqrt_rn(N)` = r + (1 if N - r^2 > r else 0) with r = floor(sqrt(N)) exact (no ties for integer N);
`med(v)` = the LOWER median, element `(n - 1) / 2` (truncating) of v sorted ascending, never an average.
L = the card's `launches` (7), R = its `rounds` (7).

**1. Cells (the `cells` section, §3.8).** For arm `a`, point `x` and launch `l`, a round times N calls of the
arm over the pool (N calibrated by doubling to >= 50 ms per timed loop, D144 add. 1) and gives T ns; its
per-call figure is `rhafz(T x 10^6, N)` (ns x 10^6 per call). The cell is `c(a, x, l)` = `med` over the R
rounds. Arm names: the row KEY the arm times; its twin `KEY#b`; a base `base.<name>`; the control `ctl`.

**2. Per-launch absolute, by the card's estimator.**
- `slope X1,X2,X3` (find_byte, and the control): with x_i the lengths in bytes and y_i = c(a, x_i, l),
  S = n·Σx_i·y_i − Σx_i·Σy_i and D = n·Σx_i^2 − (Σx_i)^2 (n = 3, exact integers), `abs_l = rhafz(S, D)`
  (ns x 10^6 per byte).
- `delta B LEN per-EVENT` (find_hit, verify_cmp, enter): `abs_l = rhafz(c(a, LEN, l) − c(B, LEN, l), E)`
  (ns x 10^6 per event), E = the subject's event count per call (hits, compares or candidates), written in the
  cell's `length` field (§3.8). The base is in the SAME group and launch.

**3. `[rev1 MEAS-11, SLOT-9]` Per-launch value, normalized by the launch's own unit.** `u_l` = the job's
control `abs_l` (its `slope`) in launch l. `v_l = rhafz(abs_l x 10^6, u_l)` (ratio: x 10^6; walkbytes: u.B x
10^6). A launch-wide shift (frequency, page colouring) moves the arm and the control together and cancels
in v_l, so it never enters a row's spread, and the unit's own launch noise is inside every ratio. **The unit
row** (J2's control): `v_l = rhafz(u_l x 10^6, U)` with `U = med(u_l)`; its median launch maps to exactly
10^6, so `value_e6 = 10^6` holds by construction; its twin is normalized by the same `U`
(`v#b_l = rhafz(u#b_l x 10^6, U)`), so step 5's difference compares like with like.

**4. value.** `value_e6 = med(v_l)`. `abs_ns_e6` (provenance) = `med(abs_l)`.

**5. `[rev1 MEAS-4, MEAS-6]` A/A, per arm, on the value.** `v#b_l` = step 2-3 on the twin's cells (same base,
same `u_l`). `aa = med(|v#b_l − v_l|)`.

**6. `[rev1 MEAS-10]` Spread: trimmed, scaled.** Drop the ONE launch farthest from `med(v_l)` (ties: the later
launch); with the remaining n = L − 1 values w, `Q = n·Σw^2 − (Σw)^2` (exact), and
`sp2 = rhafz(K_TRIM_E6 x Q, 10^6 x n x (n − 1))`, `K_TRIM_E6 = 1723000`. K_TRIM is DERIVED, not tuned: the
trimmed variance of 7 normal launches is low by the factor 1/1.723 (simulation, 200,000 draws, lane s2rev1,
`span_cards/coverage_drill.py`: rms of the trimmed s.d. 0.7618 sigma, 1/0.7618^2 = 1.723), so `sp2` estimates one launch's variance. One bad launch is the dropped one;
a two-cluster row keeps its split in `sp2` (§3.5's drill).

**7. noise.** `noise_e6 = isqrt_rn(aa^2 + sp2)`: an ABSOLUTE 1-sigma in the row's unit x 10^6 (span_pick's band
is a quadrature sum of `(coef_a − coef_b) x noise` in price units, span_pick.md:231-233). The only roundings
are the cell medians' `rhafz` (step 1), steps 2, 3 and 6's `rhafz`, and the root: the recompute agrees
EXACTLY or fails (`measure_sets.md` §1.7).

**8.** `n` (provenance) = L x R.

### 3.5 `[rev1 MEAS-2, MEAS-3, MEAS-7]` Gates, the NULL rule, drift, outcomes (the spec text of `measures.md` new §3.5)

- **Cost rows** (the `slope` rows, the unit included) pass iff `value_e6 > 0` and
  `noise_e6 x 10^6 <= gate_e6 x value_e6` (`gate_e6` the card's; the unit's at HALF). A non-positive cost is
  a failed measurement.
- **Delta rows** (`delta` estimators: `find_hit`, `verify_cmp`, `enter`) take `measure_sets.md` §7.4's NULL
  rule on the per-call deltas `D_l = c(a, LEN, l) − c(B, LEN, l)`: the row is `null` (EMPTY value, `-` noise)
  UNLESS every `D_l > 0` and `med(D_l) > max(aa_D, rhafz(FRG_E6 x med(c(B, LEN, l)), 10^6))`, with
  `aa_D = med(|c(KEY#b, LEN, l) − c(a, LEN, l)|)`. The sign rule is one-sided because these deltas are COSTS:
  a consistently negative per-event cost (an arm faster than its base, MEAS-3's alignment win over `null`)
  is a fixture artifact, `null`, named in the row's `source`, never priced. **A delta row never refuses its
  group**: a `null` row is unpriced, and an unpriced candidate cannot qualify (span_pick §The pick 4: safe).
- **FRG** (§7.4's run-wide floor) = the p90 of the per-call A/A fraction over every twinned arm at its
  largest point, `rhafz(med(|c(a#b) − c(a)|) x 10^6, med(c(a)))`, sorted ascending, element
  `(9·m + 9)/10 − 1` (truncating) of m. Recorded in PROVENANCE.md; the recompute re-derives it.
- **The unit's bimodal test**: with the unit's `u_l` sorted ascending (s_0..s_6), bimodal iff for some k in
  2..5 (both clusters >= 2 launches) `rhafz((s_k − s_(k−1)) x 10^6, U) > gate_e6/2`: a split as large as the
  unit's own gate, the size that would shift every ratio.
- **`[rev1 MEAS-7]` Drift, per JOB** (rev 0: per group, against a within-launch floor, which refused 25-57 %
  of clean groups): with `C_j` = `med` of job j's control slopes and `U` the unit's,
  `drift_j = rhafz(|C_j − U| x 10^6, U)`; job j's groups are REFUSED iff
  `drift_j > max(gate_e6/2, 3 x isqrt_rn(sp2_U + sp2_Cj))`, the `sp2` of each series taken on its relative
  values `rhafz(x x 10^6, med)`. The size that matters is the unit's own gate: since every row is normalized
  per launch (§3.4 step 3), a common drift cancels, and a residual below the unit gate is inside every row's
  own gate. The threshold uses the between-launch spread, the quantity a difference of medians carries.
- **A group passes** iff every cost row passes, the quiet gate held at its start (the load the harness
  records; the producer's record, not recomputable), and its job is not drift-refused. **FULL**: every group
  passes, `partial 0`. **PARTIAL** (exit 4): the unit group and at least one other pass; the set holds only
  passing groups' rows, and the summary names each refused group and the row-1 keys now unpriced.
  **REFUSED** (exit 3): the unit group fails (gate or bimodal), or nothing else passes; no set.
- **The run** is the five jobs of one window at one frozen commit (D166: one box, one run, one method
  version); the id `zen4-grid3` is TAKEN AT COMMIT, so a REFUSED or unsatisfying run is re-run whole in a
  later window and nothing is mixed across windows. **Known gap**: noise is WITHIN-window; between-window
  drift (review 2026-10-31-r3 MEAS-7, the bake-off's `s_bw`) is unmeasured. Trigger: row 1's
  predicted-vs-measured spread (R5.3) exceeding the band on its movers.

**`[rev1 MEAS-2..MEAS-10]` The rules on constructed outcomes** (the review's five, plus the delta and drift
cases; L = 7; computed by `span_cards/drill.py`, an implementation of §3.4-§3.5 from this text):

| outcome | constructed per-launch input | rule | result |
|---|---|---|---|
| clean | cost row v = 59900..60100 (±0.2 %), twin +60 | cost gate | value 60000, noise 92 (0.15 %): PASS |
| one outlier | the same, one launch at +8 % (64800) | cost gate | value 60000, noise 92: PASS (the trimmed launch; rev 0's s.d.: 3.58 %, REFUSED) |
| bimodal (non-unit row) | 4 launches at 60000, 3 at 63000 | cost gate | value 60000 (majority), noise 2034 (3.39 %): REFUSED, the split kept in the spread |
| bimodal unit | walk 189.2 x4, 195.0 x3 (3 %) | bimodal test | gap 2.96 % > 1.5 %: run REFUSED |
| unit, one outlier | walk clean x6, one at +8 % | bimodal test | no interior gap (the outlier is a cluster of 1): PASS |
| A/A above spread | clean launches, twin +600 (1 %) | cost gate | noise 604 (1.01 %) = aa: PASS |
| A/A above the gate | clean launches, twin +2000 (3.3 %) | cost gate | noise 2001 (3.34 %): REFUSED (the arm is placement-sensitive beyond the gate) |
| delta near zero | D_l = +1.5, −2.0, +3.0, ... ns per call (signs mixed) | NULL rule | `null`; the group still passes |
| delta negative | D_l all ≈ −30 (consistent) | NULL rule | `null` (a negative cost), named; group passes |
| delta clean | D_l ≈ 40 µs per call, all positive; floor 6 µs per call | NULL rule | priced |
| no drift | control = unit + 0.03 % | drift | 0.03 % vs threshold 1.5 %: kept |
| drift, tight launches | control = unit x 1.03 | drift | 3.0 % > 1.5 %: job REFUSED |
| drift inside a wide spread | launches spread ±1.1 %, control x 1.02 | drift | 2.0 % < 4.96 %: kept (unresolvable at this spread; the rows carry it) |
| equal-effect sweep | J1, all five widths truly equal, 8 cells | §3.6 rule | (b) 0 of 20,000 drills; (a) 99.8 %, (c) 0.2 % |

### 3.6 [PAIR-LOOKAHEAD-TIME]: job J1, first

The charter (plan.md:1711-1715): sweep w in {32, 64, 128, 256, 512} on union-select and the query-string pair
on the two bench subjects' shapes, ONE bounded effort (pcrec-one-pass-loss-chasing), after R-30's abi 94
(DONE). It is the trigger's "measurement-set revision for the pair card".

- **What is timed.** The kit's PAIR text with the declaration's width literal substituted (`ofs_pair_decl`,
  `ofsskip.c:275-279`; `[rev1 PREMISE-13]` the generator asserts the `<h>wa = 128, <h>wb = 128` declaration,
  `<h>` the site's handle prefix: fn-pair writes `wa = 128, wb = 128`, a window B-pair writes
  `rx_mf1_wa = 128, rx_mf1_wb = 128`, and an unmatched declaration refuses the dry run), so neither the kit
  nor pcrec gains a lever (pcrec-test-harness-minimal). Subjects: the bench's two subject files, read-only
  from the sibling checkout's published data (never its ledgers; pcrec-ask-bench-dev), regimes throughput
  (1 MiB find-all) and short (1,024 records); `[rev1 MEAS-1]` one twin, `128#b`, per cell.
- `[rev1 MEAS-8]` **What it decides, by a pre-registered rule.** Per cell c and width w != 128, the paired
  per-launch relative difference `r_l = rhafz((t_l(w) − t_l(128)) x 10^6, t_l(128))` (same launch, so the
  launch cancels). w **beats** 128 on c iff every r_l < 0 and `|med(r_l)| > 2 x isqrt_rn(aa^2 + sp2(r))`
  (§3.4's aa of the 128 twin and spread of r, both as fractions); **loses** symmetrically. Then:
  **(b)** some ONE w beats 128 on at least 5 of the 8 cells and loses on none: a D186 UNIT change is filed
  (its own deny, abi event, G1 at both layers); it is NOT stage 2, and the PAIR cards (`find_byte.pair`,
  `find_hit.pair.*`) are timed only after it lands (their form hash moves with the literal), the other cards
  not waiting. **(a)** no w beats 128 on any cell: the comment in `ofsskip.c` changes from "its TIME is an
  UNMEASURED DEFAULT" to MEASURED with this job named (a kit source comment that reaches no artifact: no
  byte moves). **(c)** otherwise: accept 128, MEASURED, and record the cells where a width beat it.
- **Drilled** (`span_cards/j1_drill.py`; the launch effect and each arm's within-launch noise unit normal):
  with no true effect, (b) 0 of 20,000 (rev 0's rule: 50-55 %); with one width truly better by 2, 3, 4, 6
  within-launch s.d. on every cell, (b) 0.02 %, 12 %, 82 %, 100 % (5,000 drills each). A retune is filed only for an effect the
  sweep resolves on most cells.
- J1 runs first in the window so that (b) is known before J2 times PAIR.

### 3.7 `[rev1 MEAS-14, PREMISE-11]` Box time

Per point-launch 0.95 s: regime_eval's per-launch figure for a streamed or >= 1 MiB grid1 group
(`regime_eval.md`, "0.95 s per launch", used by `r17b_prime.md:2063`), a whole-artifact figure that
overshot grid2's estimate (`r17b_prime.md:2061`), so an upper-bound-style estimate here. 7 launches, fixed
(§2.1): no rerun allowance. A point is one (arm, length) timed per launch. Builds and answer gates run in
`--dry-run`, OUTSIDE the clock.

| job | content | points | timed (min) |
|---|---|---|---|
| J0 census | compile-only (§7); NOT a timing job, no window | `[rev1 PREMISE-12]` (R-33's job 240-kit-r33-sweep: 5,492 compiles, `docs/dev/lanes/r33_report.md` "Sources"; 14 s by the queue log) | ~1 |
| J1 sweep | control 3 + 8 cells x (5 widths + `128#b`) | 51 | 5.7 |
| J2 unit + byte | unit group: walk, walk#b x 3 lengths (6); byte group: libc, pair, walk-set and twins x 3 lengths (18) | 24 | 2.7 |
| J3 hit | control 3; miss bases libc, pair, walk-set at 1 Mi (3); 2 landings x 2 gaps = 4 groups x (6 hit arms + 6 twins) | 54 | 6.0 |
| J4 verify | control 3; ~8 census (form, cls) pairs x 2 passes x (arm + twin); 2 `null` bases | ~37 | 4.1 |
| J5 enter | control 3; ~3 kinds x 3 entries x (pass, pass#b, fail) | ~30 | 3.3 |
| | **timed total** (J1-J5) | ~196 | **~22** |

**The window to ask for: 35 minutes** (22 timed; five job starts, each behind the >= 55 s two-sample quiet
gate; slack). J3 is counted from §2.5's keys: `one` arms libc, walk, pair; `alt` arms pair, walk-set;
the walk's miss base is the control's 1 Mi point. `verify` and `enter` counts are the census's to fix (§7);
the total moves by minutes. J6 (S2g, HELD) is not in this window.

### 3.8 `[rev1 SLOT-1, CONTRACT-1]` How the set is assembled

1. The slot harness writes ONE draft set (format 2, §5; id `zen4-grid3`, rev 1; method `kit-grid@3`; tier
   `scratch`) under the lane's scratch directory, never under `memfn/data/sets/` (`tests/memfn/finder_check.py`
   digests every `.tsv` there with the format-1 rule, :343-374; it stays format-1 only, guarded by sabotage
   (o)). Its `rows` are §3.4's values, noise and NULLs; its **`cells` section** holds every per-launch cell
   §3.4 step 1 defines (spec §2.2's existing `cell group arm length launch round ns_e6`, §4.4's spelling);
   its `values_digest` comes from `tests/knowledge/ks_ref.py digest`.
2. `pcrec --list-measurements draft.tsv > set.tsv`: the C loader re-derives the digest (a mismatch refuses)
   and the canonical writer writes the file (canonical by construction, `measures.md` §6¶2), as grid1's
   PROVENANCE.md records. `measure_store/from_interim.py` is NOT used (its one-time grid1 path stays
   unchanged).
3. `measure_store/zen4-grid3/1/{set.tsv, PROVENANCE.md}` (PROVENANCE: the run, the method card version, the
   slot harness's commit, FRG, D188's facts (§2.7), the per-round transcript's location and sha-256: rounds
   no row reads are not committed, `measure_sets.md` §1.5); `index.tsv` row; DEFAULTS per §8.3;
   `make gen-measures`; the drift gate `make gen-tables && git diff --exit-code`.
4. **The recompute check** (Goal 3): `tests/knowledge/` gains a python check, written from `measures.md`'s new sections 3.4-3.5 and importing nothing from the slot harness, that re-derives from each committed set's
   `cells` every measured row's value, noise and NULL status, FRG and the `partial` verdict, exactly; it runs
   in `make test`'s measures section over every committed set whose cards name an estimator (zen4-grid3
   today; grid1's cards name none, so it is skipped by name, counted, and the count pinned).

**Size.** ~196 points x 7 launches = ~1,370 cells of ~70 bytes, ~96 KB of text in `set.tsv`, embedded by
`make gen-measures` as text and pre-parse (`measures.md` §8¶2, unchanged). UNMEASURED: S2e reports the
`libpcrec.a` growth (`docs/dev/artifact_size_log.tsv`'s neighbour figure); an embed rule that omits `cells`
from the pre-parse is a spec event of its own, raised only if main finds the growth material.

## 4. The noise channel (an MF abi event)

### 4.1 The seam

`mf_measure` (`memfn/include/memfn.h:1226-1231`) is {key, value_e6, unit, source}. It gains, APPENDED LAST:

```c
typedef enum { MF_NOISE_UNSTATED = 0, MF_NOISE_MEASURED, MF_NOISE_UNMEASURED } mf_noise_state;
    uint8_t     noise_state;  /* mf_noise_state; UNSTATED is refused              */
    int64_t     noise_e6;     /* 1-sigma, the row's unit x 1e6; 0 unless MEASURED */
```

- **A state, not a sentinel.** A missing noise is UNMEASURED, never 0 (span_pick.md:182), and a measured
  noise may round to 0; the house rule "an UNSTATED zero is refused" (memfn/CLAUDE.md) then FORCES every
  constructor to state it: `[rev1 PREMISE-9]` the THREE positional constructors found by grep
  (`cli/main.c:160`, the `--harness=measures=FILE` reader; `src/gen/memfn_sites.c:89`;
  `tests/memfn/arm_fixtures.c:1562`) zero-initialize the new fields, so an unedited one is refused at
  `mf_art_begin`, not silently "measured 0".
- **No `n`.** No reader would read it (D77); it stays a listed provenance column.
- **The kit's check** (`compose.c` `measures_check`, :892-905) adds: state in {MEASURED, UNMEASURED};
  MEASURED: 0 <= noise_e6 <= MF_MEASURE_MAX; UNMEASURED: noise_e6 == 0. Refused, never clamped.
  `[rev1 CONTRACT-5]` That refusal is unreachable from a LOADED set: pcrec's loader refuses a noise past
  10^15 first (§4.4), so a bad file is a load error naming the file, never a kit "internal error" on every
  compile. The VALUE half of the same shape (a `value_e6` past MF_MEASURE_MAX loads, then every compile is
  an internal error) is pcrec's **K138** (`docs/dev/known_issues.md`, main's); this note does not fix it,
  and its noise row reads the same bound so the two refusals agree when K138 lands.
- `[rev1 COST-4]` MF_SITE_ABI takes **the next free number at landing** (23 at rev 0's base; another lane may
  take 24 first, `alt_normal_form.md` names a future crossing): a layout move, no MF_VOCAB, no MF_CLASS_V;
  the history comment at memfn.h:39ff gains its entry. MF_SITE_ABI reaches no text (its only src use is
  `s->abi =`, `memfn_sites.c:406`), so no pcrec byte moves. Kit readers of `mf_measure` by grep:
  `compose.c:895` (the check) and `finder.c:440-451` (value lookup, unchanged); no kit row reads noise until
  row 1. `[rev1 CONTRACT-9]` Seam layout: `measures_check` walks `rows[]` at `mf_art_begin` with the new
  stride BEFORE the only abi field (`mf_site.abi`) is checked at `mf_define`; with pcrec and the kit built
  from one tree that is unreachable, and this note does not claim MF_SITE_ABI guards it.

### 4.2 pcrec's fill (`src/gen/memfn_sites.c` `memfn_measures`)

`[rev1 PREMISE-8, CONTRACT-2]` **On the shipped loader path, noise reaches the kit only from a set whose
digest covers it** (format 2, §5): the path is `memfn_measures` over a set `ks_measures.c` accepted, which
recomputes the digest. A format-2 row with a parsed noise is MEASURED; `-` is UNMEASURED; EVERY row of a
format-1 set is UNMEASURED, whatever its text column says, because a format-1 file with invented noise and
the committed values has the committed digest and is not refused by no-shadowing (`measures.md` §5¶4), so
its noise is not identity-bearing.

`[rev1 SLOT-6]` **The two test levers hand UNMEASURED always.** The harness reader (`cli/main.c:93-175`,
`--harness=measures=FILE`) copies `values_digest` verbatim and reads no `format`; `arm_fixtures.c`'s
`fd_load_set` reads key and value only, with no digest at all. Neither can enforce the rule, so neither
hands noise: both state `MF_NOISE_UNMEASURED` on every row. The MEASURED path's witness is `--measures=FILE`
(§9 S2a), which goes through the loader. The harness reader's own comment retires it "until [MEASURE-SET]
M0's loader", and M0 is on main: retiring it is NOT done here (its readers are tests outside this unit),
noted for main (§10.6).

`[rev1 CONTRACT-8]` **The MFMEAS trace record** (`meas_record`, :123; built only with `PCREC_CAND_TRACE`)
gains (i) the count of MEASURED rows and (ii) a TEXT digest of the handed triples: FNV-1a-64 over the lines
`key TAB state TAB noise_e6 LF` in canonical key order, 16 lowercase hex. `tests/knowledge/ks_ref.py` gains
the same digest computed from the FILE by the format rule, and S2a's witness compares the two. Unlike the
record's two `%p` addresses, the digest survives a write/read across processes. It is what sees a wrong
column, scale or sign that a state count cannot (the S983 column-swap class, `measure_sets.md:1551`).

### 4.3 `[rev1 MEAS-13, CONTRACT-6, COST-1, SLOT-10]` Derived rows: `-` noise, no rule

Rev 0 added a per-derivation noise column to `measures.md` §3.2 (quadrature rules) as a STORED, RECOMPUTED
field. That was a new recompute engine (no derived-value evaluator exists in C or python today; §3.2¶2 forbids
reader recompute) with population zero in zen4-grid3 and no reader, while §4.6 deferred a seam field on the
same D77 ground. **Ruled, strong form: derived and fitted rows carry `-` noise (UNMEASURED) in format 2**
until a format-2 derived row has a producer AND a reader (D77). No §3.2 noise column, no C or python
evaluator, no fixture for it; rev 0's sabotage (6) is dropped. The loader enforces the rule structurally:
format 2 refuses a numeric noise on a `derived`, `fitted` or `null` row (§4.4, a §7 row), so a FILE set
cannot hand a noise the format does not define. The general form this points at is filed as an unlock
(§12.1). R-35's "derived noise by quadrature" is answered as: not until a derived row has a reader; R-35's
"Not asked" leaves the shape to the kit.

### 4.4 Spec and design hunks (same commit as the seam, S2a, unless named)

- `docs/spec/measures.md` (D80; numbers by letter, never renumbered, docs/spec/CLAUDE.md): §2.1¶1's `format`
  row (`1` or `2`) and a new ¶1a (what format 2 changes); §2.2¶3a (format 2: `noise_e6` is `-` or a
  non-negative integer in value_e6's one spelling, at most 10^15 `[rev1 CONTRACT-5]`; `-` on a `null`,
  `derived` or `fitted` row `[rev1 MEAS-13]`); §3.3¶1a (the format-2 digest, §5); §6¶3a (the decoded view,
  §4.5); §7 table rows (a misspelled or negative noise; a noise past 10^15; a numeric noise on a null,
  derived or fitted row; `format` outside {1, 2}). `[rev1 SLOT-1]` NO `raw.tsv` paragraph: §8¶1 unchanged.
- `[rev1 MEAS-5, SLOT-1]` at **S2c**: `measures.md` new §3.4 (the estimator, §3.4 here: the `lengths`
  grammar `slope X1,X2,X3` / `delta B LEN per-EVENT`, the cell arm naming, steps 1-8) and §3.5 (§3.5 here:
  gates, NULL rule, FRG, bimodal, drift, outcomes); new paragraph 2.2¶5: a set may carry in `cells` the per-launch
  cells its measured rows' estimators read; a measured row names no `inputs` (§2.2¶3 unchanged), its cells
  are found by `arm` = its key.
- at **S2e**: `measures.md` §5¶6 and §8¶3 (the default and sets today, §8.3).
- `docs/design/measure_sets.md` (each with a `[s2]` revision line): §4.1 "No provenance columns" amended:
  `noise_e6` is handed from format-2 sets (R-35), `n` and the rest are not (S2a); `[rev1 CONTRACT-9]`
  :490-494 "What the digest excludes ... `noise_e6`" made format-1-only (S2a); §1.4's "the checker's
  recompute" and §1.5's "Cells no row reads are not committed": a method whose estimator normalizes per
  launch recomputes `value_e6` from its cells, not from `abs_ns_e6` (S2c); §7.3/§7.4: the M3 driver
  implements `measures.md`'s new sections 3.4-3.5 (S2c); §3.6 (S2e, §8.3).
- `match_api.md`: **NO hunk.** Its measures sentences (§6¶14a, §6.3.10¶12-¶13) state the stamp's grammar
  `id@rev:digest` and that no kit row reads a set: both stay true through stage 2, and the digest's
  definition is `measures.md`'s (§3.3), which carries the change. R-35 names a match_api hunk: For main (§10.4).

### 4.5 The pcrec-side code (main reviews; the same commit)

`src/core/ks_measures.{c,h}`: `format` 1 or 2 (today refused unless 1, `ks_measures.c:305`); on format 2
`noise_e6` parsed into a new `KsMeasRow.noise_e6` (KS_MEAS_EMPTY for `-`) with the spelling, bound and
row-status refusals; a second digest role beside the first (§5); the canonical writer writes noise back in
its one spelling. `[rev1 CONTRACT-7]` **Format 1**: `KsMeasRow.noise_e6` is KS_MEAS_EMPTY on every row (the
column stays free provenance text, never parsed), and the decoded view gains NO field for it, so grid1's
decoded view is byte-identical; format 2's decoded view gains one field per row, the parsed noise.
`[rev1 CONTRACT-3]` `scripts/ksgen.c` writes the new field POSITIONALLY into the committed pre-parse
`src/core/measures_table.inc` (`:347-358`), so it is in the package: without it the pre-parse holds 0 where a
fresh parse holds KS_MEAS_EMPTY and `tests/knowledge/meas_store_check.c` (pre vs fresh, :72-80) goes red.
The `.inc` regenerates for grid1 too (its `-` noise as KS_MEAS_EMPTY): a committed derived file that moves
(§8.2), its source `set.tsv` untouched. The measures KsKind row names ONE digest role
(`ks_measures.c:724-725`, the role's domain hashed first by `ksrc.c:533`); format 2's role is chosen by the
set's `format`, and the kind row's `.item`/`.stamp` role stays format 1's (no generic reader of `.item`
exists today; the choice is recorded so a future one reads the right role). `src/gen/memfn_sites.c` (§4.2),
`cli/main.c` harness reader (UNMEASURED, §4.2), `src/dump/measures_dump.c` (the decoded view).
`tests/knowledge/ks_ref.py` (the independent python digest, parser, decoded view and §4.2's triple digest)
and `mfixtures.py` (`[rev1 CONTRACT-9, COST-6]` its refused-format row `("format", hdr("format", "2"), ...)`,
:177, moves to `3`; new format-2 fixtures, §9).

### 4.6 Not here: the bundle's sampling noise

span_pick.md:234-238 puts B's sampling noise (block bootstrap, "pcrec STATES it with the rates") on "stage
2's MF_SITE_ABI event". **Decision: deferred to its producer.** No producer exists (`pcrec-analyze` writes
no noise; the bundle format has no field), a blind compile's P is an authored prior with no sample, and
row 1's witness compiles with data use the scratch `prose` bundle only. A seam field nobody writes and
nobody reads is built ahead of need (D77). Trigger: [BENCH-WITHDATA]'s held-out bundles (plan.md:1717) or
row 1's with-data band, whichever first; then one MF_SITE_ABI event with its pcrec producer. For main
(§10.3): it amends span_pick.md:237-238's "stage 2's".

## 5. Noise in `values_digest`: set FORMAT 2

- **The event.** `measures.md` §3.3¶1 hashes no provenance column, so noise is outside today's digest;
  span_pick.md:265 offers two exits: noise in the digest, or "a FILE set may not share a committed id".
  CHOSEN: noise in the digest, as a FORMAT version, not a domain swap for every set: **format 2** sets hash
  under domain `pcrec-meas-2` (13 bytes with its NUL, the same length) and per row the key, a NUL, the unit
  byte, the status byte, `value_e6` LE int64 and `noise_e6` LE int64 (`INT64_MIN` for `-`, as for an empty
  value). Format 1 keeps `pcrec-meas-1` and its rule, byte for byte. The `cells` section stays outside the
  digest in both formats (§3.3¶1); the file sha-256 covers it.
- **Why a format, not a re-digest.** A committed revision never changes (`measures.md` §8¶1). Re-digesting
  zen4-grid1@1 would rewrite its header, its file sha (`index.tsv`), DEFAULTS.log row 1 (`zen4-grid1@1:
  13a6536315af1520`) and its movers file's identity, all for noise it does not carry (68 rows, all `-`).
  Under the format rule **zen4-grid1@1 stays format 1, unchanged: its digest `13a6536315af1520`, its
  sha `d332967c...` and DEFAULTS.log row 1**. The format-1 noise rule (§4.2: never handed) closes the
  no-shadowing hole for it.
- **Every reader of the digest, by grep** (`git grep 'pcrec-meas-1'`, values_digest in code), and what each
  does: `src/core/ks_measures.c:245` and `.h:114` (a second `KsDigest` role; the first's line kept byte for
  byte so `S1244`'s anchor holds); `tests/knowledge/ks_ref.py:91` (format dispatch); `measure_store/
  from_interim.py:31` (`[rev1]` UNCHANGED: grid1's one-time path, unused by stage 2, §3.8);
  `memfn/data/sets/generate.py:79` and `[rev1 CONTRACT-1]` `tests/memfn/finder_check.py:313-324,343-374`
  (format-1 only, over EVERY `.tsv` in `memfn/data/sets/`: UNCHANGED because no format-2 file is placed
  there, §3.8, sabotage (o)); `S1244`, `S1227` (format-1 plants: still valid; format-2 plants, §9);
  `cli/main.c:78,143` and `measures_dump.c:29` (the header key only: unchanged); `memfn_sites.c:95,128`,
  `memfn_stamps.c:290` (the hex: unchanged); `tests/compound/run_part_measures.sh` (a synthetic header's
  text: unchanged); `docs/spec/measures.md` §3.3, `docs/design/measure_sets.md:476,:490-494,:1594,:1923`
  (text). Every committed digest: one, grid1's, unchanged.
- **No emitted byte or stamp moves, and how that is PROVEN.** The stamp is `id@rev:digest` of the loaded
  set iff a reader consulted it (`measures.md` §4¶2) and no kit row reads a set at stage 2 (§4¶4): every
  artifact's `<PREFIX>_MEASURES` is `""` before and after. Proof, per unit: `emit_sweep.py` byte-identical
  on every arm (stamps included) against the unit's named base, plus the DATA-MOVER census (`emit_sweep.py`'s
  data mode, `measure_sets.md` §9.3) compiling the corpus under `--measures=zen4-grid1` and
  `--measures=zen4-grid3`: zero movers. A non-empty stamp anywhere is a red, not a finding to explain.

## 6. The coverage factor

- **What it is.** The band of a comparison (span_pick.md:231) is z x sqrt(sum over cards of ((coef_a -
  coef_b) x noise)^2) [+ the bundle's term, §4.6]; z is the coverage factor.
- `[rev1 MEAS-9]` **Which error the band covers.** The stored value is the median of 7 launches; the artifact
  later runs in ONE launch-like condition. The error a departure risks is therefore a NEW RUN's draw against
  the stored median, with the noise itself estimated from 7 launches (§3.4: trimmed, scaled). Rev 0 quoted
  Phi(-z) (a known sigma), which is neither.
- **Value: z = 3.0, `COVER_Z_E3 3000`, UNMEASURED DEFAULT (D149).** Derivation, from the stated tolerance
  rev 0 chose (a 2.3 % one-sided false departure on an equal-price comparison, one card): by simulation
  of §3.4's estimator on normal launches (`span_cards/coverage_drill.py`, 200,000 draws), the one-card
  equal-price departure rate is 6.7 % at z = 2, 3.9 % at 2.5, 2.5 % at 2.9 and **2.3 % at 3.0** (for the
  t-reading: the new draw's variance is 1 + pi/(2 x 7) of one launch's, and the trimmed spread has about
  five degrees of freedom; t_5 at the 2.3 % tail, times 1.107, is 2.9-3.0). A departure to a plan truly
  dearer by d happens less often, so the equal-price case bounds the harm. A comparison over several cards
  sums more estimated variances, so its effective degrees of freedom rise and 3.0 errs WIDE there (wins
  forgone, the safe direction). 2.58 (family-wise over smp20's ~10 candidates) was weighed in rev 0 and not
  taken: candidates share cards, so the comparisons are positively correlated and Bonferroni over-corrects.
- `[rev1 SLOT-7]` **Where it lives: [KIT-POLICY-TABLE]** (plan.md, filed by main from this review; trigger
  row 1): one kit policy-constant table (z, the gate default, MATERIAL, MAX_SET, HORS_MIN). Not a set row (a
  set holds measurements of a box, D166; a stamped per-set z would let a re-measure move a policy), and not
  `plan_cost.def`: D176 Q3 says "`plan_cost.def` rows migrate into the sets", with no cost/policy split,
  and rev 0's "its policy rows stay" narrowed that ruling silently; rev 1 withdraws the narrowing.
  **Written WITH its reader, row 1** (D77: stage 2 adds no reader); stage 2 fixes its value and derivation
  here. Visible in row 1's trace (the band per comparison, span_pick.md:60-61); the pcrec-side re-pricer
  pins the literal and diffs it against the trace's.
- **Trigger to re-derive:** row 1's predicted-vs-measured spread (R5.3), which adds model error to the band.

## 7. The step-0 gate

- **The manager's reading is CONFIRMED.** span_pick.md:396 says only "the step-0 gate". D176 Q3
  (`decisions.md:9920`): the cards are measured "in a night window cleared with Frank, gated on the step-0
  census". That census is the stop-ranking study's §7 step 0 (SRS = `docs/design/memfn/stop_ranking_study.md`
  rev 2 on the unmerged `lane/memfn-stopstudy` fc6735cdf, the doc `pricesurvey_report.md:5-7` names SRS):
  "CENSUS, after C1 merges: per window site ... A-mass's pick vs the argmin's at both bracket ends of
  c_probe; count by kind (set to byte, set to PAIR, SKIP declined/admitted, two-byte non-case-pair stops,
  ... the fold)", compile-only, a heavy sweep, no clock; step 1 (THIS box's cards) has the trigger "step 0
  shows a population (any non-zero count of set-to-byte movers or SKIP flips)"; SRS §8 item 2: it "shares
  the price formula with the build, so it LOCALIZES movers and is never the acceptance". The pricesurvey
  cites agree: `:251` (NOT run), `:275` (the census row), `:366` (localize only), `:392` (prerequisite of
  D176's build). **Refinements under span_pick:** the incumbent is today's whole plan (KEY, M, TIE), not
  A-mass alone (span_pick §The pick 2); SKIP (Horspool) counts are out (R14c); "after C1" is met (C1 is S3's,
  landed).
- **What it is now.** J0: the R-33 sweep (job 240's MFTRACE build, re-made at the stage-2 base) plus a
  pricing pass, `docs/design/memfn/span_pick/census0.py`. `[rev1 SLOT-8]` **census0 REPLACES smp20.py**:
  smp20 is census0 on one site, so `smp20.py` is deleted in S2b and `smp20.out` becomes census0's golden on
  that site (one kit-side pricer of the formula, so a formula fix lands once; row 1's C pricer and
  span_pick's pcrec-side re-pricer stay deliberately independent). Per site, each candidate (alternative x
  core position x the methods T-FIND admits on its facts) is priced under P (the default prior) with
  smp20's STAND-INS at the corners of its grid (k 1.00 and 12.00; h1 5 and 40; hit(PAIR) 1x and 8x h1); the
  BAND-0 argmin vs the incumbent read from the trace. Outputs: (1) movers by class (row 1's class: a NONE
  alternative whose core position 0 is a two-member set; others) at any corner; (2) **the card population**:
  for row-1-class sites, the methods, verify (form, cls) pairs and consumer kinds x entry facts their
  candidates read. `[rev1 COST-2]` Output (2) is `docs/design/memfn/span_pick/census0.out` (span_pick's
  instruments directory, own CLAUDE.md), written by S2b and read by S2c's slot harness when it lists the
  cells; there is no separate cell manifest (SLOT-1). Who runs it: a kit lane (the instrument is the kit's).
- **What it must show.** A non-zero row-1-class population: that is the trigger, and it is ALREADY MET by
  smp20 alone (`[rev1 PREMISE-10]` span_pick.md:306-307: "(3,536 points) P's argmin is '/' at 3,381"; the
  figure is span_pick's, `smp20.out` has no P-blind grid line), so as a GATE it cannot stop stage 2. It
  runs first anyway because its output (2) is the D77 reader list that scopes J4/J5's arms (§2.5), and
  Frank's ruling names it. **Control** `[rev1 COST-5 (8), PREMISE-10]`: on smp20's site census0 reproduces
  `smp20.out`'s lines byte for byte, INCLUDING the `incumbent @...` lines (the band-0 argmin is computed
  without the incumbent, so a control on the argmin alone cannot see a wrong incumbent field), and it
  commits its own P-blind grid count as a NEW golden line, cross-checked once against span_pick's 3,381 of
  3,536 (a mismatch is a finding about span_pick's figure or census0, resolved before S2b lands).
- **Does stage 2's landing wait on it?** Its TIMING waits (J4/J5's arms come from it); it is unit S2b,
  before the window. Row 1 waits on stage 2, so on it too. It is **re-run after the cards** (S2f) with the
  measured values in place of the stand-ins: still compile-only and readerless, it becomes row 1's
  forecast mover list and the watched witness's stage-2 reading ("is the measured card point above or
  below k*?", span_pick.md:336).

## 8. What stage 2 moves

### 8.1 Nothing emitted

No pcrec abi event (`[rev1 COST-4]` `PCREC_ARTIFACT_ABI` does not move in any stage-2 unit, whatever its value
at the unit's base: other landers move it, stage 2 does not), no stamp value, no `--list-axes` row (no new
deny: no kit text changes), no `--memfn=` option. Proof per unit: §5's last item, against the unit's named
base.

### 8.2 The numbers that change, and their same-commit packages (readers by grep, D76/D94)

| number / artifact | change | package (same commit) |
|---|---|---|
| MF_SITE_ABI | `[rev1 COST-4]` +1, the next free number at landing (S2a) | memfn.h history entry; `[rev1 PREMISE-9]` the THREE constructors (§4.1); compose.c check; memfn/include/CLAUDE.md; `memfn/docs/journal.md` + responses ledger; `grep -rn 'MF_SITE_ABI'` re-run at landing (no test pins the number today: g2_gen.c uses `MF_SITE_ABI + 1` symbolically) |
| set `format` | `1` -> `1` or `2` (S2a) | `measures.md` hunks §4.4; `ks_measures.c` refusal text; ks_ref.py; mfixtures.py (the `format 2` refusal row -> `3`; a format-2 fixture pair differing only in noise must digest apart; a `-` noise row; a noise-past-10^15 row; a numeric noise on a derived row; a format-1 file with numeric noise text) |
| digest domain | + `pcrec-meas-2` (S2a) | the readers of §5; grid1 untouched |
| `KsMeasRow` layout | + `noise_e6` (S2a) | `[rev1 CONTRACT-3]` `scripts/ksgen.c`; the regenerated `src/core/measures_table.inc` (grid1's rows included, noise KS_MEAS_EMPTY); `meas_store_check.c` green pre vs fresh |
| form-hash entries | `[rev1 PREMISE-3]` formhash.c's declared entry table: + pair, walk-set, settest, rc-* (S2c) | `formhash.c`; `finder_check.py` check C's deps-column guard (§2.4); R-MS3's two fixtures per new id; memfn/data/cards/CLAUDE.md |
| card table | + `kit-grid@3` rows (S2c) | `kit-grid.tsv` (`[rev1 SLOT-12]` its header's unit sentence becomes per-version: ver 1 `u = beta_walk(DFA_SCAN, r1e0c0)`, ver 3 `u = find_byte.walk`); its CLAUDE.md |
| spec estimator text | + `measures.md`'s new sections 3.4-3.5, new paragraph 2.2¶5 (S2c) | the recompute check's source text (written in S2e); measure_sets §1.4/§1.5/§7.3 lines |
| built-in sets | + `zen4-grid3@1` (S2e) | `measure_store/` files + `index.tsv`; `make gen-measures` (`measures_store.inc`, `measures_table.inc`); `measures.md` §8¶3; measure_store/CLAUDE.md ("Sets today") |
| `DEFAULTS` | `idk` zen4-grid1@1 -> zen4-grid3@1 (S2e, §8.3) | DEFAULTS, DEFAULTS.log row 2, `movers/0002.tsv` (EMPTY by §5's proof); `measures.md` §5¶6; `measure_sets.md` §3.6 hunk; `[rev1 CONTRACT-4, COST-6]` the `--list-measurements` readers BY NAME: `S1229` (its `SAB_BEFORE` `{ "idk", "zen4-grid1", 1u },` re-aimed to `zen4-grid3`, intent re-verified: the plant still breaks the class's default row), `S1228`, `S1237`, `S1241`, `S1245`, `S1246` (anchors re-read; each re-aimed only if its anchor text moves), `tests/knowledge/run_measures_tests.sh`'s DEFAULTS vs `default_for` vs DEFAULTS.log check (:77-94, a reader of the flip), `run_code_tests.sh`, `c4_allowlist.tsv`, `arch_blind_check.py` (grep hits to re-read). There is NO count pin (`run_measures_tests.sh:75` is a floor `>= 1`) |
| `ofsskip.c` PAIR_LOOKAHEAD comment | UNMEASURED -> MEASURED, iff §3.6 (a) or (c) | none (a source comment; no artifact text) |
| new directories | `docs/design/memfn/span_cards/` (drills now; `slot/` at S2c) | its CLAUDE.md (`[rev1 COST-6]` under the 12 KB gate); docs/design/memfn/CLAUDE.md |

### 8.3 `[rev1 PREMISE-4, SLOT-3, CONTRACT-4]` DEFAULTS: main RULED (B), and what it amends

Rev 0 found a real conflict and mis-framed it ("No ruling is amended"). R-35 item 1 says stage 2 "leaves
DEFAULTS unchanged" and item 3 that row 1 "flips DEFAULTS to zen4-grid3 ... Its flip needs its own landing
verdict from main"; span_pick says the same (Stage 2: "stamps and `DEFAULTS` unchanged"; Row 1 `[rev3 C6]`
"It flips `DEFAULTS` to the new set"). Frank's D166 addendum 2 (Q-MS-1) and `measures.md` §5¶6 say a bare
compile reads the LATEST committed set. Either reading amends something; both give byte-identical artifacts
(nothing consults: every stamp `""`).

**Ruled (main, 2026-11-06): (B). S2e flips `DEFAULTS` `idk` to zen4-grid3@1, with zero movers.** S2e's commit
writes DEFAULTS, DEFAULTS.log row 2 (`2 idk zen4-grid1@1:13a6536315af1520 zen4-grid3@1:<digest>
movers/0002.tsv`) and `movers/0002.tsv` from the data-mover census, EMPTY by §5's proof. It amends three
texts, each in the same commit:

| amended text | owner | amendment |
|---|---|---|
| R-35 item 1 ("leaves DEFAULTS unchanged") and item 3 (row 1 flips, its own landing verdict) | main's request text | the flip moves to stage 2's S2e, judged in S2e's landing verdict; row 1 becomes the first READER of an already-default set (its consulting compiles' stamps move then, an abi event that is row 1's) |
| span_pick rev 5.2: Stage 2 "stamps and `DEFAULTS` unchanged"; Row 1 `[rev3 C6]` "It flips `DEFAULTS`"; §Defaults "until row 1 flips it" | the kit's design | `[s2]` lines: stage 2 flips DEFAULTS at zero movers; row 1 reads the default set |
| `measure_sets.md` §3.6 "Every default-set change is therefore an abi event" | the [MEASURE-SET] design | the "therefore" rests on consulting artifacts: a default-set change MOVES the stamp of every consulting artifact, so it is an abi event exactly when a consulting reader exists; a change with no consulting reader (every stamp `""`, the data-mover census empty) is a DEFAULTS.log transition with its census and no abi bump. A `[s2]` revision line (S2e) |

`measures.md` §5¶6 then reads "its default is the latest committed set: `zen4-grid3@1`" (S2e). Goal 1's
measure is restated for it (§1): two `--list-measurements` rows move at S2e, no other unit moves any.

## 9. Build plan

Stage 2 is SIX scalar units on the kit branch, in this order, plus the HELD SIMD unit S2g; each is a delivered
commit set with its witness. No unit moves an emitted byte (§8.1). The pcrec-side hunks (S2a, S2e) ride the
kit's same-commit package, reviewed by main, as R-35 (a) rules for unit 3.0. Heavy runs are boxqueue jobs;
ONLY S2d needs the timing window main clears with Frank (R-35 (b); never 20:00-01:00, never beside another
timing run).

`[rev1 COST-4]` **Bases.** Each unit names its BASE commit (main's tip it branches from) in its first commit,
and every identity witness (emit_sweep, the data-mover census) compares against that base. Two byte-moving
pcrec lanes land on main alongside (R-35 Concurrency): after any lander, an unlanded unit re-merges main,
re-baselines (a new named base) and re-runs its identity witness before delivery. MF_SITE_ABI is read at
landing (§4.1).

`[rev1 SLOT-11]` **Sabotage ids are the kit's**, taken at BUILD time from the top of the free range and
recorded in the unit's first commit (R-35: three lanes allocate). Below, rows are lettered; `[rev1 COST-5]`
each states the check that turns it red and why that check can see it.

| unit | content | witness | heavy runs | sabotage rows (why each goes red) |
|---|---|---|---|---|
| **S2a** noise channel + format 2 | §4.1-§4.5, §5: the seam field and check (kit); format 2, the digest role, parse/write, bound and status refusals, fill (format rule; test levers UNMEASURED), ksgen, dump, the MFMEAS triple digest, spec and design hunks (pcrec) | emit_sweep byte-identical every arm vs base; grid1's canonical and decoded views and digest byte-identical; a format-2 synthetic set round-trips canonically; ks_ref.py's digest equals C's on format-2 fixtures; in the `PCREC_CAND_TRACE` build, a compile under a format-2 `--measures=FILE` shows the MEASURED count and a triple digest equal to ks_ref.py's, a format-1 file with numeric noise text shows 0 and the all-UNMEASURED digest; a kit test hands a zero-initialized row and is refused | `make test` (normal, boxqueue), emit_sweep | (a) format-2 digest skips noise: ks_ref.py (written from the spec) digests the noise-only fixture pair apart, C does not -> mfixtures golden red. (b) format-2 domain spelled `pcrec-meas-1`: ks_ref.py's digest differs from C's on every format-2 fixture. (c) the fill hands format-1 noise as MEASURED: the format-1 fixture carries numeric noise text on every row, so the MFMEAS count is non-zero (expected 0). (d) the kit accepts UNSTATED: the named kit test builds a zero-initialized `mf_measure` and expects the refusal. (e) the fill drops a format-2 noise (UNMEASURED): the handed-triple digest differs from ks_ref.py's. (f) the fill hands `abs_ns_e6` as noise (S983's column swap): the triple digest differs (the fixture's abs and noise columns differ on every row). (g) the canonical writer writes `-` noise as `0`: the fixture holds a `-` row, so the round trip's bytes and digest (INT64_MIN vs 0) differ. (h) the loader admits noise past 10^15: mfixtures' bound row expects a refusal |
| **S2b** step-0 census | `census0.py` (smp20.py deleted), its run (J0) and `census0.out` | reproduces `smp20.out` byte for byte incl. the incumbent lines; the P-blind count committed and cross-checked (§7); counts non-zero | J0 (compile-only boxqueue job, ~1 min; not timing) | (i) incumbent read from the wrong trace field: the control diffs `smp20.out`'s `incumbent @` lines, which carry that field |
| **S2c** producer | the G2 `--cards` mode (§3.2), formhash's entry table, `kit-grid@3` cards, check C's deps guard, `measures.md`'s new sections 3.4-3.5 + new paragraph 2.2¶5, the measure_sets lines, the slot harness `span_cards/slot/` with dry runs of every job | every job's `--dry-run` green (builds, perturbed twins, answer gate); check C resolves every new dep; R-MS3's two fixtures per new id (rename: hash kept; one-instruction edit: hash moves); ids pairwise distinct; every cell text's hash equals its key's form hash | dry runs only (each job's `--dry-run`, light) | (j) a twin built without the pad: the driver's check requires the two built objects to DIFFER while the texts are equal, so identical objects refuse. (k) an arm rendered from another form than its key: the cell-text hash differs from `mf_form_hash(<form token>)`. (l) a planted wrong find in one arm: G2's reference check and the expected-count gate. (m) two form ids hashing one text: the pairwise-distinct check. (n) a kit-grid@3 card with a `kit:form.` dep and no `form` dim: check C's deps guard (it no longer skips). (o) a format-2 draft placed in `memfn/data/sets/`: finder_check's format-1 digest of it mismatches |
| **S2d** the window | J1 sweep, then J2-J5 chained `after`, one window | each job's declared population met (POPULATION-SHORT otherwise); the outcome FULL or an accepted PARTIAL; J1's reading (a)/(b)/(c) | J1-J5: quiet-gated `idle-ok` timing jobs, **the window main clears with Frank: 35 minutes** | — (a measurement; its control is S2e's recompute and the per-job drift check) |
| **S2e** the set | §3.8: draft, canonical writer, store files, `index.tsv`, gen-measures; DEFAULTS (B) and its three amendments (§8.3); the recompute check; S1229 re-aim | the recompute check exact on every row, FRG and `partial`; the drift gate; `tests/knowledge/` green; the data-mover census under both sets: zero movers; emit_sweep byte-identical; `--list-measurements` moves by the two rows | `make test` (normal), the data-mover census (boxqueue) | (p) the producer's noise off by one unit on one row: the recompute (an implementation of the spec text sharing no source with the slot harness) differs by one, and one unit is a failure (§1.7). (q) a cell edited after the set was written: the recompute no longer reproduces the row AND the file sha in PROVENANCE.md/`index.tsv` mismatches |
| **S2f** the forecast | census0.py re-run with the measured cards; the watched-witness reading; the report | the smp20 reading stated (above/below k*); row 1's mover forecast listed | J0 again (compile-only) | — |
| **S2g** SIMD (J6) **HELD** | vrun-w16/w32 cards under D188 (§2.7), once the SIMD model is ruled; its own window and the NEXT set id | designed then | — | designed then |

`[rev1 COST-7]` **Separability.** S2a lands and reverts alone until S2e lands (S2e's set is format 2); S2b is
separable; S2c reverts alone; S2d-S2e are order-locked to S2c. S2g depends on nothing here and nothing here
depends on it.

## 10. Questions and amendments

**For Frank: none from this note.** The SIMD model is ruled (D188 add. 1, §2.7); its build waits for [XARCH-DEV]; the window request goes through
main (35 minutes, §3.7).

**For main** (each with the kit's recommendation):

1. **memchr-back DEFERRED** (§2.5): R-35 and [MEASURE-SET]'s `next:` list it; no priced row reads it (D77).
   Recommend: defer with its trigger; ~1 minute of window if main wants it anyway.
2. **The bundle's sampling-noise field** (§4.6): deferred to its producer; it amends span_pick.md:237-238.
3. **No match_api hunk** (§4.4): R-35 names one; nothing there moves.
4. **Row 1 is a scalar-layer row** (§2.5): recommended under the hold, with its stated cost; it amends
   nothing ruled (span_pick §The pick 6 already allows it) but R-35 item 1's "scalar and SIMD" cards become
   scalar now, SIMD at S2g.
5. **D188 fact (b) and the stamp** (§2.7): `MEMFN_FORMS` names the levels the TEXT carries, so under `#if`
   arms a stamp can name a level a fixture's compile excluded; the read-back of (b) is J6's design item once
   the model is ruled. Relay to Frank with the model question if useful.
6. **The harness set reader's retirement** (§4.2, SLOT-6): its own "until M0" condition is met; noted, not
   done here.

### 10.2 Amendments this design makes to other documents (each lands with the named unit)

| document | text | amendment | unit |
|---|---|---|---|
| span_pick.md | :266-267 "(`kit-grid@2`)" | `[s2]` `kit-grid@3` (`@2` is grid2's, TAKEN) `[rev1 PREMISE-6]` | S2c |
| span_pick.md | Stage 2 "`DEFAULTS` unchanged"; Row 1 `[rev3 C6]`; §Defaults | §8.3 | S2e |
| span_pick.md | :237-238 "stage 2's MF_SITE_ABI event" (bundle noise) | deferred to its producer (§4.6) | S2a |
| R-35 (requests.md) | items 1 and 3 (DEFAULTS) | §8.3; main's text, main amends | S2e |
| measure_sets.md | §1.4, §1.5, :490-494, §3.6, §4.1, §7.3 | §4.4, §8.3 | S2a/S2c/S2e |
| kit-grid.tsv header | the unit sentence | per-version (§8.2) | S2c |

### 10.3 Row 1's design items this note hands on (not decided here)

Which `find_hit` landing and density the price reads (or both, as regimes); verify priced over T-VERIFY's
step list (span_pick R21) using `verify_cmp`'s (form, cls) keys; the `COVER_Z_E3` row in [KIT-POLICY-TABLE]
and its trace line; the E2 family unification reading the three `enter` cards; the band's bundle term
(§4.6); its SIMD-on acceptance reading (§2.5).

## 11. The three standing questions (docs/design/CLAUDE.md)

1. **The measurement regime: RELEVANT.** Every card names it (§2.3): Linux dev box (Zen 4 7700X), gcc 15.2
   `-O2`, glibc's memchr, CPU 7 pinned, sibling idle; `[rev1 MEAS-12]` a 16 MiB pool of fresh streamed
   buffers (in L3, beyond L2); throughput on long subjects (byte, hit at g 256 and 1024), a candidate array
   (verify), whole-artifact find-all (enter); hits periodic AND random (a regime flip between them is
   exactly what the robustness rule wants seen); the SCALAR layer only (§2.5); per-call (short-subject)
   regimes are NOT carded ([SPAN-PICK-PERCALL]'s, span_pick.md:198-199), so a priced row's per-call cells
   fall outside the cards' claim. A different box flips picks; that is a new set id, never this one.
2. **The independent control: RELEVANT.** Answers: G2's reference check and the expected-count gate on every
   arm before any clock. Values, noise, NULLs, FRG and `partial`: the pcrec-side recompute from the set's
   `cells` (an implementation of `measures.md`'s new sections 3.4-3.5, not importing the slot harness); the digest
   by ks_ref.py (python, from the spec's table, not the C), verified again by the C loader. Placement: the
   perturbed twin (§3.2), whose distinctness the driver asserts. Drift: one control per job against the
   unit, with a between-launch threshold. "Stage 2 moves nothing": emit_sweep and the data-mover census,
   counted pcrec-side from artifact diffs (K35), never the kit's `moved`. The seam's noise values: the
   MFMEAS triple digest against ks_ref.py's. The census (§7) shares the price formula with row 1, so it
   LOCALIZES only (SRS §8 item 2), never accepts. Populations: every job declares its group count and the
   queue counts it (POPULATION-SHORT); the recompute check counts the sets it skips.
3. **What moves when the data is regenerated: RELEVANT.** Re-measuring makes a NEW id (`measures.md` §8¶1);
   a re-reading of the same `cells` a new rev. With no reader (stage 2), nothing emitted moves under any set
   (§5's proof), and the DEFAULTS flip moves no stamp (§8.3). From row 1, a new default set moves the picks
   of consulting artifacts and their `<PREFIX>_MEASURES` stamps: then a default-set change is an abi event
   with its census (`measure_sets.md` §3.6 as amended, D162). A PAIR width retune (§3.6 (b)) stales the
   PAIR cards through their form hash; a consumer entry-text change stales `enter` (§2.6).

## 12. Unlocks (filed, not built)

1. `[rev1 MEAS-13, SLOT-1 general form]` **A measured row as a DERIVATION over `cells`.** The estimators of
   §3.4 (`slope`, `delta`) become registry derivations (`launch-median-slope`, `arm-minus-base`) whose
   `inputs` are cell ids, recomputed by the existing §3.2 checker path; a noise rule becomes one column of
   that registry, and derived-row noise follows from it. Unlocks: Goal 3 without a special-purpose check;
   M3's install tool implementing ONE registry; derived noise with a reader. Trigger: the first format-2
   derived row with a producer and a reader, or M3's driver build, whichever first.
2. **One kit noise-policy table** ([KIT-POLICY-TABLE], filed by main). Unlocks row 1's E2 unification.
   Trigger: row 1.
3. **The census as THE priced-forecast tool** (census0 subsumes smp20, §7, and every later row's mover
   forecast). Trigger: S2b (taken).

## STATE AT HANDOFF

Rev 1, lane s2rev1. OWED: nothing of the design; every unit of §9 is unbuilt; S2g HELD on the owner's SIMD
model. The drill scripts behind §3.5's table, §3.6 and §6 are committed under `docs/design/memfn/span_cards/`
(evidence, python only, no timing). No make, no timing, no box job. Not a build go.
