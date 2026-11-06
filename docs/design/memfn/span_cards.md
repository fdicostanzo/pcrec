# span_cards — span_pick STAGE 2: the cards, their producer, the noise channel (design, rev 0)

**Status: PROPOSED, rev 0 (lane s2design, 2026-11-06). DESIGN ONLY: no code, no make, no timing, no box
job. The design of record for span_pick stage 2** (`span_pick.md` rev 5.2 §Staging "Stage 2", §Cost
cards, §The pick; kit request R-35 item 1, `memfn/docs/requests.md:805`; Frank's GO 2026-11-06, plan
80341284e). Read §0 (the decisions in one table) first. Cites are to the kit branch
`lane/memfn-k1102` at c03c2d711 unless a commit is named; spec files are cited by section number.

## 0. The decisions, one line each

| # | question (brief item) | decision | where |
|---|---|---|---|
| 1 | the cards | four quantities under a NEW method version `kit-grid@3`: `find_byte`, `find_hit`, `verify_cmp`, `enter`; the UNIT row is `kit.find_byte.walk`; every key read by row 1 (or, for SIMD forms, by Frank's C9 row); `memchr-back` DEFERRED (no reader); `hors.probe`/`find_hit(hors)` out (R14c) | §2 |
| 2 | the producer | kit-owned `memfn/measure/` (never built by make): cell texts rendered by the kit through G2's window-site builder, one timing driver, quiet-gated `idle-ok` boxqueue jobs, one window, ~35-45 min of timing; the per-launch medians KEPT as `measure_store/zen4-grid3/1/raw.tsv` (committed, never embedded); FULL/PARTIAL/REFUSED per `measure_sets.md` §7.3; the PAIR width sweep its own first job | §3 |
| 3 | the noise channel | `mf_measure` gains `noise_state` + `noise_e6` appended LAST (MF_SITE_ABI 23 -> 24; an UNSTATED state is REFUSED, so every constructor must state it); noise reaches the kit ONLY from a set whose digest covers it; derived noise by quadrature as a STORED, RECOMPUTED field (`measures.md` §3.2 gains its noise rule) | §4 |
| 4 | noise in the digest | set FORMAT 2: `noise_e6` is a parsed value and the digest domain is `pcrec-meas-2`; format 1 stays legal and unchanged, so zen4-grid1@1, its digest `13a6536315af1520`, DEFAULTS.log row 1 and every pin stay byte for byte | §5 |
| 5 | the coverage factor | z = 2 (2.3 % one-sided false departure on an equal-price comparison), a kit constant in `plan_cost.def`'s MARGIN family, UNMEASURED DEFAULT (D149), written WITH its reader at row 1; defined (value, derivation, trigger) here | §6 |
| 6 | the step-0 gate | CONFIRMED: D176 Q3's "step-0 census" = SRS §7 step 0. Its trigger is met in advance (smp20 alone); it runs FIRST anyway, compile-only, because its population SCOPES the card grid (D77) and is re-run after the cards as row 1's forecast | §7 |
| 7 | what stage 2 moves | NO emitted byte, NO pcrec abi, NO stamp value. Moves: MF_SITE_ABI 24; set format 2 + digest domain 2 (format 1 untouched); a new built-in set zen4-grid3@1; `kit-grid@3` card rows; form-hash ids. DEFAULTS: a reading for main (§8.3) | §8 |
| 8 | build plan | six units S2a-S2f; one timing window (S2d); sabotage rows listed per unit, ids the manager's | §9 |
| 9 | questions | none for Frank; four items for main (DEFAULTS, memchr-back, the rate-noise field, match_api) | §10 |

## 1. Goals

Ranked; a higher goal wins a conflict (`docs/dev/guide/architecture.md`).

| # | goal (who benefits) | measurable form |
|---|---|---|
| 1 | **Stage 2 moves nothing a caller sees** (every user; span_pick Goal 2's stage-2 cell; R-35 "adds no reader, moves no emitted byte") | `scripts/emit_sweep.py` byte-identical on EVERY arm (default, each deny, `--engine=vm`, both SIMD layers) at each unit's HEAD against its base, stamps included; zen4-grid1@1's file sha and digest unchanged; `--list-measurements` changes by exactly the new set's row |
| 2 | **Every card row row 1 prices is measured with its noise** (row 1's lane; span_pick §The pick 4: a card without noise cannot qualify) | every key §2.5 lists for row 1 is `measured` with `noise_e6` set in zen4-grid3@1, or the set is PARTIAL and names it; the unit group passes its half gate and bimodal test |
| 3 | **The set is self-checking from kept data** (the next editor; K35) | a pcrec-side check recomputes every row's `value_e6` and `noise_e6` from `raw.tsv` EXACTLY (integer rule), and the format-2 digest from the rows, each by code that shares no source with the producer |
| 4 | **The least producer that gives a trustworthy set** (Frank 2026-10-21, pcrec-test-harness-minimal) | one driver, one cell generator (G2's builder, not a second), job scripts in the 650 template's shape; no card without a named reader (D77) |

**Non-goals.** Any priced reader (row 1's). Unit 3.0. Retuning `PAIR_LOOKAHEAD` (a later unit change if the
sweep says so, §3.6). The SIMD official verdict (D144 add. 4: pcrec-bench). Horspool's cards (R14c). The
bundle-side sampling noise (§4.6). A between-window drift term (§3.5, a known gap with its trigger).

## 2. The cards

### 2.1 The method version: `kit-grid@3`

The set's `method` header is one `owner-name@ver` (`measures.md` §2.1¶1) and a set's `cards` must equal the
owner's committed rows at that ver (`measure_sets.md` §7.2). The span cards are quantities of the grid's
successor method (span_pick.md:267-268), but **`kit-grid@2` is TAKEN**: it is the method grid2's slot ran
under (`r17b_prime.md:2040`, "Method `kit-grid@2`"; :2059), never written to `memfn/data/cards/kit-grid.tsv`
(its header: "`ver 2` ... is grid2's prep lane's, NOT written here") and never committed to the store. D186
add. 2 refused to reuse `zen4-grid2` for the same reason (a name its readers already mean). So the new
method is **`kit-grid@3`**, appended to `kit-grid.tsv` (append-only by version).

**Relation to `r17b_prime.md` §5.4** (grid2's one slot spec): kit-grid@3 KEEPS its run rules (one box, one
method version, gcc 15.2 `-O2`, `taskset`-pinned, rotated interleaving, 7 rounds per launch, the per-launch
median, the quiet gate at every group boundary, the pre-registered CROSS-LAUNCH rerun trigger of rev3 C7,
the correctness gate before any clock, perf optional per D166 add. 1) and CHANGES what is timed: §5.4 timed
whole pcrec artifacts (grid1's harness, `docs/dev/lanes/grid1/README.md`); kit-grid@3 times the kit's
rendered FORM TEXT in a fixed find-all loop (§3.2), whole artifacts only where the quantity is the
consumer's (`enter`, §2.5) or the charter names a pattern (the PAIR sweep, §3.6). Cross-set comparison is
only within one `method@ver` (`measure_sets.md` §1.4), so zen4-grid3's ratios are not compared with grid1's.
Launches: 5 (+2 by the cross-launch rule), not §5.4's 3: grid2 found 3 sufficient for VALUES, but a noise
estimate from 3 launch medians is a two-degree-of-freedom spread, and noise now gates departures; the cost
is +2/3 of a ~35-minute window (§3.7).

### 2.2 What carries over from kit-grid@1: only the unit's regime

D77: a grid quantity no reader reads is not re-measured. At this branch no kit row reads a set key
(`measures.md` §4¶4; R1/R2/R8 retired at span_pick 1f; `kit.h3a`/`kit.gstar.*` "stay in zen4-grid1,
unread", span_pick.md:372), so none of grid1's ten quantities (`beta saving eps f xover block delta ccold
wuse gstar`) is re-measured. The UNIT is: its regime is pinned by the card ("streamed, fresh, long,
member-free", `measure_sets.md` §1.4), and that is exactly `find_byte`'s regime, so **the unit row is
`kit.find_byte.walk`** (value 1,000,000 by construction; `unit_key` may name any row, `measures.md`
§3.1¶2). byte(walk) in span_pick's price IS the unit: one row, not a unit row plus a walk row that
measure the same text twice. The unit group keeps §1.4's half gate and bimodal test.

### 2.3 The four quantities

Key grammar (`measures.md` §2.3): a quantity is `[a-z][a-z0-9_]*`, so span_pick's `find.byte` is spelled
`find_byte`. Units (`measures.md` §3.1): `ratio` = per subject byte relative to the unit; `walkbytes` =
a per-event cost in u.B. Tokens are the kit's own (the format reads no owner's vocabulary, §2.3¶2).

| quantity | dims | unit | subject (the card's regime) | lengths / points | per |
|---|---|---|---|---|---|
| `find_byte` | `method` | ratio | streamed-fresh, MISS-ONLY (no member in the subject), long | the slope over 64 Ki, 256 Ki, 1 Mi | subject byte, all the method's streams (span_pick.md:216) |
| `find_hit` | `method;landing;split` | walkbytes | streamed-fresh, hits planted `periodic` (every g bytes) or `random` (seeded uniform, mean gap g); `split` `one` (one member occurs) or `alt` (both members, alternating) | the slope of time over hit count at g in {4096, 256, 32}, the miss-only point shared with `find_byte` | candidate returned and restarted |
| `verify_cmp` | `form;cls;pass` | walkbytes | a fixed candidate array (positions spread over a 1 Mi fresh buffer), the compared bytes seeded so the test passes with probability 0 (`p0`) or 1/2 (`p50`); a failing run differs at a uniformly seeded position | the arm minus the `null` arm (same loop, compare replaced by a constant), per compare | one compare: cmp0, cmp½ (span_pick.md:220) |
| `enter` | `kind;entry` | walkbytes | a WHOLE ARTIFACT (`build/pcrec`) of a fixture pattern whose site states `kind` and an alternative of `entry`; candidates that pass every verify position and die in the consumer one byte past the window (`die1`) vs candidates that fail the last verify position | the slope over candidate count at g in {4096, 256}, the pass arm minus the fail arm | candidate passed on (span_pick.md:222) |

`[C10]` (span_pick.md:258): `enter` BAKES IN its fixture's survival (the consumer dies one byte past the
window); the alternative (a pcrec-stated survival x a per-byte card) waits for a reader that states survival.

**The SIMD forms** (D186 add. 2 C9: "SIMD-form cards join stage 2"; span_pick.md:243-244, scalar the bar).
The forms that EXIST at this branch: `vrun-w16`, `vrun-w32` (`memfn/src/vrun.c`, levels `levels.def`
LV_X86_W16/W32; routed as PREFIX rungs of OFS and pre-check FUNC sites, denies in `options.def` :31-45)
and `vany2`/`vany3` at w16/w32 (`memfn/src/vany.c`, NOT routed, declared in `kit-kernels@1`, UNMEASURED).
They are measured as METHOD TOKENS of the same two quantities (`find_byte`, `find_hit`), not as new
quantities: a SIMD form is a method on a layer (D147), and a C9 row then reads one table. Their scalar bar
sits in the same group: `pair` for vany2 and for vrun (vrun's scalar BODY `fn-pair` is the same leapfrog,
`ofsskip.c` `ofs_pair_text`), the walk for vany3.

### 2.4 The card rows (`kit-grid@3`, appended to `memfn/data/cards/kit-grid.tsv`)

`gate_e6` 30000 is grid1's UNMEASURED DEFAULT (D149) carried; the unit group gates at half (§1.4). `deps`
are R-MS3 form ids; the ids marked NEW are added to `formhash.c`'s `canon()` (today `walk` and `libc`
only, `memfn/src/formhash.c:240`) in unit S2c, so `finder_check.py` check C resolves every card dep.

| owner | quantity | ver | dims | unit | subject | lengths | launches | rounds | aa_rule | gate_e6 | env | deps |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| kit | find_byte | 3 | method | ratio | streamed-fresh miss-only | slope 64Ki-1Mi | 5 | 7 | pair-per-group;bimodal-unit | 30000 | - | kit:form.\<method\> (walk, libc; pair, vany2-w16, vany2-w32, vany3-w16, vany3-w32, vrun-w16, vrun-w32 NEW) |
| kit | find_hit | 3 | method;landing;split | walkbytes | streamed-fresh landed:periodic\|random | slope g in {4096,256,32} | 5 | 7 | pair-per-group | 30000 | - | as find_byte |
| kit | verify_cmp | 3 | form;cls;pass | walkbytes | candidate-array pass:0\|1/2 | arm minus null | 5 | 7 | pair-per-group | 30000 | - | kit:form.\<form\> (settest, rc-words, rc-overlap, rc-bytes, rc-memcmp NEW) |
| kit | enter | 3 | kind;entry | walkbytes | artifact die1 | slope g in {4096,256}, pass minus fail | 5 | 7 | pair-per-group | 30000 | - | kit:form.\<the site's method\>; pcrec: OWED (§2.6) |

`libc` deps also record `libc:glibc@<ver>` as provenance, never row staleness (`r17b_prime.md` §5.3).

### 2.5 Keys, and the reader of each (D77)

The population of keys is the step-0 census's (§7): a token below is measured only if the census finds a
row-1-class site that reads it, except the SIMD rows (their reader is the C9 row, Frank's, whose own
design picks its keys: these are its inputs, never its candidate shapes, span_pick rev5 D4).

| keys | reader | why that reader reads it |
|---|---|---|
| `find_byte.walk` (UNIT), `.memchr`, `.pair` | row 1 | byte(m) of the three methods row 1's candidates use: a one-member stop by memchr or walk, `{X,x}` by PAIR or walk (finder.c rows D1, PAIR, R7w) |
| `find_hit.{memchr,walk}.{periodic,random}.one`, `find_hit.pair.{periodic,random}.{one,alt}`, `find_hit.walk.{periodic,random}.alt` | row 1 | hit(m); the landing pair is the robustness regime span_pick requires (a random-like regime, §Robustness); WHICH landing the price reads is row 1's design item (recorded §10.2) |
| `verify_cmp.<form>.<cls>.{p0,p50}` for the (form, cls) the census finds on row-1 sites | row 1 | cmp(f, p) at its two points (span_pick.md:220) |
| `enter.<kind>.NONE` for the kinds the census finds | row 1 | passes_r x enter on its NONE alternatives |
| `enter.<kind>.PARKED`, `enter.<kind>.RESEED`, same kinds | row 1's E2 family unification | span_pick.md:157-160: the "beat the incumbent by a margin" family unifies AT row 1, trigger the `enter` cards; MARGIN stays until the PARKED and RESEED cards exist (:257-258) |
| `find_byte`/`find_hit` for `vrun-w16/w32`, `vany2-w16/w32`, `vany3-w16/w32` | the C9 SIMD T-PICK row (D186 add. 2; span_pick §The pick 6) | Frank's ruling puts SIMD-form cards in stage 2; one separable job (J6), droppable alone |
| **DEFERRED: `memchr-back`** | none | finder row D1c serves MLINE (`finder.c:270-275`); no priced row admits MLINE; D1c's own revisit trigger needs a libc-free back-find card that does not exist. R-35 and [MEASURE-SET]'s `next:` list it: For main (§10.1). Trigger: the first priced row admitting MLINE sites |
| **OUT: `hors.probe`, `find_hit.hors`** | the Horspool priced row (later) | R14c (span_pick.md:254-256): D-hors incumbents stay unpriced |

**Row 1's SIMD-on arm needs no SIMD card**, and that is CHECKED, not assumed: the census (§7) reads each
row-1-class site's `<PREFIX>_MEMFN_FORMS` stamp on the `-fmemfn-simd` arm; `none` means the text is
identical to the SIMD-off compile (memfn/CLAUDE.md, Stamps), so the scalar cards price both layers. A
non-`none` site there is a census finding that adds that form's keys to the row-1 list.

### 2.6 Known gaps of the card set

- **`enter`'s consumer is pcrec's.** Its staleness cannot be a kit form hash; the set header's
  `code_commit` is the only record. A `pcrec:` dep id for the consumer's entry text is OWED, trigger: a
  re-measure showing `enter` moved beyond noise on a consumer-only change.
- **Isolation.** A form timed in the fixture's loop is not the form inside a DFA's register pressure: that
  is model error, which span_pick puts OUTSIDE the band and in row 1's predicted-vs-measured print
  (span_pick.md:283-284). The cards make no in-situ claim.

## 3. The producer

### 3.1 Where it lives

`memfn/measure/` (new, the kit's, own CLAUDE.md; never built or run by pcrec's make), because the cards are
the kit's (memfn/CLAUDE.md: "the kit owns ... set values and method"; `measure_sets.md` §7.1: "a kit
quantity is measured by the kit's harness mode: the forms and their timing arms are the kit's") and Frank's
formal library re-runs it on every future box (D176 Q3: "the kit contributes its method cards to that
script"). Not `tests/` (not a test, never in `make test`); not `docs/design/kit_proof/measure` (a design
evidence dir for one verdict). The job scripts live there too, as the 650 template does.

| file | role |
|---|---|
| `cells.tsv` | the cell manifest: card key, arm, group, subject recipe, points; the census writes the row-1 population into it (§7) |
| (G2) `memfn/tests/g2/g2_win_gen.c --cards CELLS` | renders each kit-isolated arm's text through the kit's public entries (`mf_art_begin`, `mf_define`), the method chosen by the existing denies (`--memfn=no-...`) or force rows; ONE window-site builder, not a second (pcrec-general-mechanisms-not-special-cases); its existing G2 check is the answer gate: every arm's find-all count equals the scalar byte loop's on every subject |
| `drv.c` | the timing driver: one binary per (group, arm) with a find-all loop over the arm's function (kit arms) or the artifact's match_api §3.1 loop (`enter`, the sweep); calibrate by doubling to >= 50 ms per timed loop (D144 add. 1), 7 rounds, the median per launch, arm order rotated per launch |
| `subj.py` | seeded subject generator (fresh streamed buffers, planted hits, candidate arrays); writes the expected counts the gate reads |
| `read.py` | per-launch medians -> rows (value_e6, noise_e6, n) by §3.4's estimator, the gates, the interim set |
| `jobs/<NNN>-kit-s2-<what>` | the boxqueue jobs (§3.3) |

### 3.2 The timed text

Each kit arm is the kit's text for one window site (one stop set S at offset 0, the method its deny forces),
wrapped as a `static` function the driver's loop calls from `pos` to `n`, counting candidates. The A/A arm
(`walk#b`, `null#b`) is a SEPARATE compile and link of the same text (650's AA, grid1's `walk#b`), so code
placement differences are in the floor, not hidden. `enter` and the sweep compile fixture patterns with
`build/pcrec` (`--emit-main`-free: the driver links the artifact).

### 3.3 The job shape

Template: `docs/design/kit_proof/measure/650-covertime-slot`. Each job: `--dry-run` builds every arm and runs
the answer gate (no clock), prints `boxqueue: cap`, `patience none`, `idle-ok`, `est`, and `expect
groups=N lines=^== s2 GROUP done` (a population the work prints per group, so a short job is
POPULATION-SHORT, not green); `--ready` is 650's quiet gate (no running queue job, no box-lock holder,
load1 < 2.0 on two samples >= 55 s apart); the work is `exec measure.sh run`. Pinned `taskset` to CPU 7,
sibling CPU 15 idle (650's pair; grid1 used 14, which only names a different core: the set's `box`
records it). Jobs chain with `after` and declare `not-before`/the window's times; one stage per job, each
under an hour (BOILERPLATE, Frank 2026-10-30). The quiet gate checks only the START (BOILERPLATE:236):
every group boundary re-checks load and records it, and a group whose in-group walk differs from the unit
row's walk beyond its A/A floor is REFUSED (PARTIAL), which is how drift inside the window is caught.

### 3.4 The estimator (kit-grid@3's, written once here, recomputed by the check)

Per point p (group, arm, length or density) and launch l: m(p,l) = the median over 7 rounds of ns per unit
of work (per byte, per hit, per compare, per candidate). All arithmetic in integers at e6 (`measure_sets.md`
§1.7: int128 intermediates, round half away from zero `rhafz`); the square root is `isqrt_rn(N)` = r =
floor(sqrt(N)), plus 1 iff N - r^2 > r (exact, no ties for integer N).

- **value.** find_byte: the least-squares slope of m over the three lengths, per launch, then the median
  over launches. find_hit and enter: the slope of time over hit (candidate) count, per launch, then the
  median. verify_cmp: m(arm) - m(null) per launch, then the median. `abs_ns_e6` is that; `value_e6 =
  rhafz(abs_ns_e6 x 10^6, unit abs_ns_e6)` (`measure_sets.md` §1.4: the checker re-derives it EXACTLY).
- **noise** (`measure_sets.md` §7.3: A/A floor and the launch spread in quadrature), as an ABSOLUTE 1-sigma in
  the row's own unit x 10^6: `noise_e6 = isqrt_rn(aa^2 + sp^2)`, where `aa` = the group's A/A floor
  (the median over launches of |m(A#b,l) - m(A,l)|, A the group's A/A arm, scaled to the row's unit by the
  same ratio as the value) and `sp` = the sample standard deviation of the per-launch values (not divided by
  sqrt(L): between-launch variation is systematic, not averaged away). ABSOLUTE, not a fraction, because
  span_pick's band is a quadrature sum of `(coef_a - coef_b) x noise` in price units (span_pick.md:231-233).
- `n` = launches x rounds actually run (>= the card's 5 x 7, `measure_sets.md` §7.2).

### 3.5 Gates, outcomes, and what the run is

Per group (`measure_sets.md` §7.3): pass iff `noise_e6 / value_e6 <= gate_e6` on every row of the group, the
quiet gate held, and the in-group walk agrees with the unit within the A/A floor; the unit group at half and
bimodal-tested. **FULL**: every group passes, `partial 0`. **PARTIAL** (exit 4): the unit group and at least
one other pass; the set holds only passing groups' rows and the summary names each refused group and the
row-1 keys now unpriced (they cannot qualify, span_pick §The pick 4: safe). **REFUSED** (exit 3): no set.
**The run** is the six jobs of one window at one frozen commit (D166: one box, one run, one method version);
the id `zen4-grid3` is TAKEN AT COMMIT, so a REFUSED or unsatisfying run is re-run whole in a later window
and nothing is mixed across windows. **Known gap**: noise is WITHIN-window; between-window drift (review
2026-10-31-r3 MEAS-7, the bake-off's `s_bw`) is unmeasured. Trigger: row 1's predicted-vs-measured spread
(R5.3) exceeding the band on its movers.

### 3.6 [PAIR-LOOKAHEAD-TIME]: job J1, first

The charter (plan.md:1711-1715): sweep w in {32, 64, 128, 256, 512} on union-select and the query-string pair
on the two bench subjects' shapes, ONE bounded effort (pcrec-one-pass-loss-chasing), after R-30's abi 94
(DONE: abi 95, `src/gen/emit_dfa.c:55`). It is the trigger's "measurement-set revision for the pair card".

- **What is timed.** The kit's PAIR text with the declaration's width literal substituted (`ofs_pair_decl`,
  `ofsskip.c:278`, writes `wa = 128, wb = 128`; the generator asserts exactly that declaration and
  substitutes), so neither the kit nor pcrec gains a lever (pcrec-test-harness-minimal). Subjects: the
  bench's two subject files, read-only from the sibling checkout's published data (never its ledgers;
  pcrec-ask-bench-dev), regimes throughput (1 MiB find-all) and short (1,024 records); A/A = `128#b`.
- **What it decides.** (a) 128 within the A/A floor of the best w on every cell: the comment in `ofsskip.c`
  changes from "its TIME is an UNMEASURED DEFAULT" to MEASURED with this job named (a kit source comment
  that reaches no artifact: no byte moves); the PAIR cards proceed. (b) some w beats 128 beyond the floor
  on a cell and loses on none: a D186 UNIT change is filed (its own deny, abi event, G1 at both layers);
  it is NOT stage 2, and the PAIR cards (`find_byte.pair`, `find_hit.pair.*`) are timed only after it
  lands (their form hash moves with the literal), the other cards not waiting. (c) mixed: accept 128, record.
- J1 runs first in the window so that (b) is known before J2 times PAIR.

### 3.7 Box time

Per point-launch 0.95 s (`regime_eval` §2.1's figure, used by `r17b_prime.md` §5.4), 5 launches, +40 % for
the cross-launch reruns (an allowance, UNMEASURED: grid2's cross-launch trigger fired in 28 of its 32
F1 reruns, `r17b_prime.md:2043`). Builds and answer gates run
in `--dry-run`, OUTSIDE the clock.

| job | content | points | timed (min) |
|---|---|---|---|
| J0 census | compile-only (§7); NOT a timing job, no window | (R-33's job 240: 5,492 compiles in 14 s) | ~1 |
| J1 sweep | 2 patterns x 2 subjects x 2 regimes = 8 groups x 6 arms | 48 | 5 |
| J2 unit + byte | 1 group: walk, walk#b, memchr, pair x 3 lengths | 12 | 1.5 |
| J3 hit | 2 landings x 3 densities x 2 splits = 12 groups, 4-5 arms | 54 | 6 |
| J4 verify | 2 passes x {set: 7 arms, run: ~11 arms} | ~36 | 4 |
| J5 enter | ~3 kinds x 2 densities = 6 groups x 7 arms | ~42 | 5 |
| J6 SIMD | byte: 6 forms + 2 x 3 lengths; hit: vany 6 groups x 6, vrun 6 groups x 5 | ~90 | 10 |
| | **window total** (J1-J6) | ~280 | **~32, ~45 with quiet-gate waits** |

`verify` and `enter` counts are the census's to fix (§7); the totals move by minutes.

### 3.8 How the set is assembled

1. `read.py` writes the kit's interim set `memfn/data/sets/kit-interim-grid3.tsv` (FORMAT 2, §5; the kit's
   publication, as grid1's was) and `raw.tsv` (every per-launch median: group, arm, point, launch, value),
   committed on the kit branch.
2. `measure_store/from_interim.py` (gains the format-2 digest; its one-time grid1 path unchanged) sets the
   id `zen4-grid3`, rev 1, recomputes `values_digest`; then `pcrec --list-measurements x.tsv > set.tsv`,
   the canonical writer (canonical by construction, `measures.md` §6¶2), as grid1's PROVENANCE.md records.
3. `measure_store/zen4-grid3/1/{set.tsv, raw.tsv, PROVENANCE.md}`; `index.tsv` row (tier `scratch`);
   `make gen-measures` (only `set.tsv` is embedded: Makefile `MEAS_STORE_SRCS` globs `*/*/set.tsv`); the
   drift gate `make gen-tables && git diff --exit-code`.
4. The recompute check (Goal 3): a pcrec-side python under `tests/knowledge/`, written from §3.4's text,
   re-derives every row's `value_e6` and `noise_e6` from `raw.tsv` and the digest from the rows, exactly.
   `raw.tsv`'s sha-256 is in PROVENANCE.md and checked like `set.tsv`'s.

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
  constructor to state it: the three positional constructors found by grep (`cli/main.c:160`, the
  `--harness=measures=FILE` reader; `src/gen/memfn_sites.c:89`; `tests/memfn/arm_fixtures.c:1562`) zero-
  initialize the new fields, so an unedited one is refused at `mf_art_begin`, not silently "measured 0".
- **No `n`.** No reader would read it (D77); it stays a listed provenance column.
- **The kit's check** (`compose.c` `measures_check`, :892-905) adds: state in {MEASURED, UNMEASURED};
  MEASURED: 0 <= noise_e6 <= MF_MEASURE_MAX; UNMEASURED: noise_e6 == 0. Refused, never clamped.
- MF_SITE_ABI 23 -> 24 (a layout move; no MF_VOCAB, no MF_CLASS_V); the history comment at memfn.h:39ff
  gains its entry. MF_SITE_ABI reaches no text (span_pick.md:361, memfn_sites.c's stamp path), so no pcrec
  byte moves. Kit readers of `mf_measure` by grep: `compose.c:895` (the check) and `finder.c:442-446` (value
  lookup, unchanged); no kit row reads noise until row 1.

### 4.2 pcrec's fill (`src/gen/memfn_sites.c` `memfn_measures`)

**Noise reaches the kit only from a set whose digest covers it** (format 2, §5): a format-2 row with a
parsed noise is MEASURED; `-` is UNMEASURED; EVERY row of a format-1 set is UNMEASURED, whatever its text
column says, because a format-1 file with invented noise and the committed values has the committed digest
and is not refused by no-shadowing (`measures.md` §5¶4), so its noise is not identity-bearing. The
harness reader (`cli/main.c`) and `arm_fixtures.c` follow the same rule. The MFMEAS trace record (`meas_record`, :123)
gains a count of MEASURED rows, which the S2a witness reads.

### 4.3 Derived noise, by quadrature: a stored, recomputed field

`measures.md` §3.2's list is CLOSED and names values only. Options: (a) noise of derived rows not stored,
the kit recomputing it (refused: the kit never sees derivations or inputs, `measure_sets.md` §4.1, and
§3.2¶2 forbids reader recompute); (b) a new derivation per noise (refused: a noise is not a row);
(c) **CHOSEN: noise is a STORED field of every row, and on a derived or fitted row it is the producer's
recompute by a rule per derivation, checked by §8.2's recompute exactly like the value**. The spec gains a
noise column to §3.2's table (format 2 only):

| derivation | noise (sigma, in the row's unit) |
|---|---|
| `ratio`, `ratio-complement` | \|a/b\| x sqrt((sa/a)^2 + (sb/b)^2) |
| `diff` | sqrt(sa^2 + sb^2) |
| `cross-lin` | \|v\| x sqrt((sFa^2 + sFb^2)/(Fb - Fa)^2 + (sBa^2 + sBb^2)/(Ba - Bb)^2) |
| `step` | 0, MEASURED (a form's width is exact) |
| `min`, `max`, `env-max`, `env-min` | the noise of the input that supplies the value; on a tie, the larger |
| `interp-log2` | UNMEASURED (no reader; D77; trigger: the first reader of a format-2 fitted row) |

Every product in int128 at e6, `rhafz` at each division, `isqrt_rn` at the root (§3.4). An input with
UNMEASURED noise makes the derived noise UNMEASURED; a NULL row's noise is `-` (as its value is empty).
zen4-grid3 holds NO derived row (§2.2: every card row is measured), so the rule's population there is zero;
it is in the format because noise is identity-bearing in format 2 and a FILE set (the install tool's,
`measure_sets.md` §7.5) may carry derived rows. Its witness is a synthetic fixture (`tests/knowledge/
mfixtures.py`).

### 4.4 Spec and design hunks (same commit as the seam)

- `docs/spec/measures.md` (D80; numbers by letter, never renumbered, docs/spec/CLAUDE.md): §2.1¶1's `format`
  row (`1` or `2`) and a new ¶1a (what format 2 changes); §2.2¶3a (format 2: `noise_e6` is `-` or a
  non-negative integer in value_e6's one spelling, `-` on a `null` row); §3.2¶3 (the noise column above);
  §3.3¶1a (the format-2 digest, §5); §7 table rows (a misspelled or negative noise; noise on a null row;
  `format` outside {1, 2}); §8¶1 (`raw.tsv`, kept, never loaded, sha in PROVENANCE.md); §8¶3 (sets today);
  §5¶6 per §8.3's reading.
- `docs/design/measure_sets.md` §4.1: "No provenance columns" amended: `noise_e6` is handed from format-2 sets
  (R-35); `n` and the rest are not. A `[s2]` revision line.
- `match_api.md`: **NO hunk.** Its measures sentences (§6¶14a, §6.3.10¶12-¶13) state the stamp's grammar
  `id@rev:digest` and that no kit row reads a set: both stay true through stage 2, and the digest's
  definition is `measures.md`'s (§3.3), which carries the change. R-35 names a match_api hunk: For main (§10.4).

### 4.5 The pcrec-side code (main reviews; the same commit)

`src/core/ks_measures.{c,h}`: `format` 1 or 2 (today refused unless 1, `ks_measures.c:305`); on format 2
`noise_e6` parsed into a new `KsMeasRow.noise_e6` (KS_MEAS_EMPTY for `-`) and the spelling refusals; a
second digest role beside the first (§5); the canonical writer writes noise back in its one spelling.
`src/gen/memfn_sites.c` (§4.2), `cli/main.c` harness reader, `src/dump/measures_dump.c` (the decoded view
gains `noise_e6` as parsed). `tests/knowledge/ks_ref.py` (the independent python digest and parser) and
`mfixtures.py`.

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
  value). Format 1 keeps `pcrec-meas-1` and its rule, byte for byte.
- **Why a format, not a re-digest.** A committed revision never changes (`measures.md` §8¶1). Re-digesting
  zen4-grid1@1 would rewrite its header, its file sha (`index.tsv`), DEFAULTS.log row 1 (`zen4-grid1@1:
  13a6536315af1520`) and its movers file's identity, all for noise it does not carry (68 rows, all `-`).
  Under the format rule **zen4-grid1@1 stays format 1, unchanged: its digest `13a6536315af1520`, its
  sha `d332967c...`, DEFAULTS and DEFAULTS.log row 1**. The format-1 noise rule (§4.2: never handed) closes
  the no-shadowing hole for it.
- **Every reader of the digest, by grep** (`git grep 'pcrec-meas-1'`, values_digest in code), and what each
  does: `src/core/ks_measures.c:245` and `.h:114` (a second `KsDigest` role; the first's line kept byte for
  byte so `S1244`'s anchor holds); `tests/knowledge/ks_ref.py:91` (format dispatch); `measure_store/
  from_interim.py:31` (format-2 path, §3.8); `memfn/data/sets/generate.py:79` and `tests/memfn/
  finder_check.py:320` (the kit's synthetic sets stay format 1: UNCHANGED); `S1244`, `S1227` (format-1
  plants: still valid; two new format-2 plants, §9); `cli/main.c:78,143` and `measures_dump.c:29` (the
  header key only: unchanged); `memfn_sites.c:95,128`, `memfn_stamps.c:290` (the hex: unchanged);
  `docs/spec/measures.md` §3.3, `docs/design/measure_sets.md:476,1923` (text). Every committed digest:
  one, grid1's, unchanged.
- **No emitted byte or stamp moves, and how that is PROVEN.** The stamp is `id@rev:digest` of the loaded
  set iff a reader consulted it (`measures.md` §4¶2) and no kit row reads a set at stage 2 (§4¶4): every
  artifact's `<PREFIX>_MEASURES` is `""` before and after. Proof, per unit: `emit_sweep.py` byte-identical
  on every arm (stamps included), plus the DATA-MOVER census (`emit_sweep.py`'s data mode, `measure_sets.md`
  §9.3) compiling the corpus under `--measures=zen4-grid1` and `--measures=zen4-grid3`: zero movers. A
  non-empty stamp anywhere is a red, not a finding to explain.

## 6. The coverage factor

- **What it is.** The band of a comparison (span_pick.md:231) is z x sqrt(sum over cards of ((coef_a -
  coef_b) x noise)^2) [+ the bundle's term, §4.6]; z is the coverage factor.
- **Value: z = 2, UNMEASURED DEFAULT (D149).** Derivation, from a stated tolerance: with 1-sigma card noise
  and two plans of EQUAL true price, a departure happens with probability Phi(-z) per comparison: 15.9 % at
  z = 1 (span_pick.md:234's figure), 2.3 % at z = 2, 0.5 % at 2.58. A departure to a plan truly dearer by
  d happens with Phi(-z - d/sigma), below the equal-price figure, so the equal-price case bounds the harm.
  2.58 (a family-wise 5 % over smp20's ~10 candidates) was weighed and not taken: candidates share cards,
  so the comparisons are positively correlated and Bonferroni over-corrects, and each un-taken departure is
  a win forgone. Spelled `COVER_Z_E3 2000` (thousandths).
- **Where it lives.** A kit constant, NOT a set row: a set holds measurements of a box (D166) and a stamped
  per-set z would let a re-measure move a policy. It joins MATERIAL_NUM/DEN (MARGIN, "ARGUED") in
  `memfn/src/plan_cost.def`, the same family ("beat the incumbent by a margin", span_pick.md:158), which
  row 1 unifies; when plan_cost.def's cost rows migrate into sets (D176 Q1), its policy rows stay.
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
  pricing pass, `docs/design/memfn/span_pick/census0.py`, a generalization of `smp20.py` over every window
  site of the sweep: per site, each candidate (alternative x core position x the methods T-FIND admits on
  its facts) priced under P (the default prior) with smp20.py's STAND-INS at the corners of its grid (k
  1.00 and 12.00; h1 5 and 40; hit(PAIR) 1x and 8x h1); the BAND-0 argmin vs the incumbent read from the
  trace. Outputs: (1) movers by class (row 1's class: a NONE alternative whose core position 0 is a
  two-member set; others) at any corner; (2) **the card population**: for row-1-class sites, the methods,
  verify (form, cls) pairs, consumer kinds x entry facts their candidates read, and their `-fmemfn-simd`
  `MEMFN_FORMS` (§2.5). Who runs it: a kit lane (the instrument is the kit's, like `smp20.py`).
- **What it must show.** A non-zero row-1-class population: that is the trigger, and it is ALREADY MET by
  smp20 alone (`smp20.out`: '/' is P's band-0 argmin at 3,381 of 3,536 grid points, span_pick.md:306-307),
  so as a GATE it cannot stop stage 2. It runs first anyway because its output (2) is the D77 reader list
  that scopes J4/J5's arms (§2.5), and Frank's ruling names it. **Control:** on smp20 it reproduces
  `smp20.out`'s band-0 argmin at the stand-in point; plant: a census reading the incumbent from the wrong
  trace field moves smp20's line (red).
- **Does stage 2's landing wait on it?** Its TIMING waits (J4/J5's arms come from it); it is unit S2b,
  before the window. Row 1 waits on stage 2, so on it too. It is **re-run after the cards** (S2f) with the
  measured values in place of the stand-ins: still compile-only and readerless, it becomes row 1's
  forecast mover list and the watched witness's stage-2 reading ("is the measured card point above or
  below k*?", span_pick.md:336).

## 8. What stage 2 moves

### 8.1 Nothing emitted

No pcrec abi event (PCREC_ARTIFACT_ABI stays 95, `src/gen/emit_dfa.c:55`), no stamp value, no `--list-axes`
row (no new deny: no kit text changes), no `--memfn=` option. Proof per unit: §5's last item.

### 8.2 The numbers that change, and their same-commit packages (readers by grep, D76/D94)

| number / artifact | change | package (same commit) |
|---|---|---|
| MF_SITE_ABI | 23 -> 24 (S2a) | memfn.h history entry; the four constructors (§4.1); compose.c check; memfn/include/CLAUDE.md; `memfn/docs/journal.md` + responses ledger (memfn/CLAUDE.md: kit-contract changes are recorded there); `grep -rn 'MF_SITE_ABI'` re-run at landing for any test pinning the number |
| set `format` | `1` -> `1` or `2` (S2a) | `measures.md` hunks §4.4; `ks_measures.c` refusal text; ks_ref.py; mfixtures.py goldens (a format-2 fixture pair differing only in noise must digest apart) |
| digest domain | + `pcrec-meas-2` (S2a) | the readers of §5; grid1 untouched |
| form-hash ids | + pair, settest, rc-*, vany*, vrun-* (S2c) | `formhash.c` `canon()`; `finder_check.py` check C's dep resolution; memfn/data/cards/CLAUDE.md |
| card table | + `kit-grid@3` rows (S2c) | memfn/data/cards/kit-grid.tsv header line; its CLAUDE.md |
| built-in sets | + `zen4-grid3@1` (S2e) | `measure_store/` files + `index.tsv`; `make gen-measures` (`measures_store.inc`, `measures_table.inc`); `measures.md` §8¶3; measure_store/CLAUDE.md ("Sets today", the `raw.tsv` row); every test pinning the set LIST (`--list-measurements` output pins: `grep -rn 'zen4-grid1' tests/`), each re-pinned by a count that grows by one |
| `ofsskip.c` PAIR_LOOKAHEAD comment | UNMEASURED -> MEASURED, iff §3.6 (a) | none (a source comment; no artifact text) |

### 8.3 DEFAULTS: a conflict for main to read

R-35 and span_pick rev3 C6 say stage 2 leaves `DEFAULTS` at `idk zen4-grid1@1` and row 1 flips it. Frank's
D166 addendum 2 (Q-MS-1, `decisions.md` D166) says: until a SECOND OFFICIAL set exists (M2), "a bare compile
reads the LATEST set", and `measures.md` §5¶6 says the same ("its default is the latest committed set").
Committing zen4-grid3@1 with DEFAULTS unchanged makes §5¶6 false. Both readings give byte-identical
artifacts (nothing consults: every stamp `""`) and equal cost, so it is the manager's (answer-free) call:

- **(B) RECOMMENDED: follow D166 add. 2 literally.** S2e's commit also writes `DEFAULTS` `idk zen4-grid3@1`,
  DEFAULTS.log row 2 and `movers/0002.tsv` from the data-mover census, which is EMPTY by §5's proof; §5¶6's
  literal changes. Row 1 is then the first READER of the default set, its census the bare compiles that
  newly price. No ruling is amended.
- (A) keep grid1 the default until row 1: amends D166 add. 2 (Frank's), so it becomes a question for Frank,
  and §5¶6's wording changes from "latest" to "the set DEFAULTS names".

## 9. Build plan

Stage 2 is SIX units on the kit branch, in this order; each is a delivered commit set with its witness.
No unit moves an emitted byte (§8.1). The pcrec-side hunks (S2a, S2e) ride the kit's same-commit package,
reviewed by main, as R-35 (a) rules for unit 3.0. Heavy runs are boxqueue jobs; ONLY S2d needs the timing
window main clears with Frank (R-35 (b); never 20:00-01:00, never beside another timing run).

| unit | content | witness | heavy runs | sabotage rows (ids: the manager's) |
|---|---|---|---|---|
| **S2a** noise channel + format 2 | §4.1-§4.5, §5: the seam field and check (kit); format 2, the digest role, parse/write, fill, harness reader, dump, spec hunks (pcrec); the derived-noise rule in spec, C and ks_ref.py | emit_sweep byte-identical every arm; grid1's canonical view and digest byte-identical; a format-2 synthetic set round-trips canonically; ks_ref.py's digest equals C's on format-2 fixtures; a compile under a format-2 `--measures=FILE` shows the MEASURED count in MFMEAS, a format-1 file shows 0 | `make test` (normal, boxqueue), emit_sweep | (1) format-2 digest skips noise; (2) format-2 domain spelled `pcrec-meas-1`; (3) the fill hands format-1 noise as MEASURED; (4) the kit accepts `noise_state` UNSTATED; (5) the fill drops a format-2 noise (UNMEASURED); (6) the ratio noise rule sums instead of quadrature; (7) the canonical writer writes `-` noise as `0` |
| **S2b** step-0 census | `census0.py`, its run (J0) and output; `cells.tsv`'s row-1 population | reproduces `smp20.out`'s band-0 argmin; counts non-zero (§7) | J0 (compile-only boxqueue job, ~1 min; not timing) | (8) incumbent read from the wrong trace field (smp20's line moves) |
| **S2c** producer | `memfn/measure/` (§3.1), the G2 `--cards` mode, form-hash ids, `kit-grid@3` cards, dry runs of every job | every job's `--dry-run` green (builds + answer gate); `finder_check.py` check C resolves every new dep; R-MS3's two fixtures per new id (rename: hash kept; one-instruction edit: hash moves); the ids pairwise distinct | dry runs only (each job's `--dry-run`, light) | (9) an A/A arm linked from the base's object (not a separate compile): the driver's distinct-build check red; (10) an arm's text from another method than its key (dep hash mismatch: check C red); (11) a planted wrong find in one arm: the answer gate red; (12) two form ids hashing one text |
| **S2d** the window | J1 sweep, then J2-J6 chained `after`, one window | each job's declared population met (POPULATION-SHORT otherwise); the gate outcome FULL or an accepted PARTIAL; J1's reading (a)/(b)/(c) | J1-J6: quiet-gated `idle-ok` timing jobs, **the window main clears with Frank** (~45 min) | — (a measurement; its control is S2e's recompute and the in-group walk) |
| **S2e** the set | §3.8: interim, `raw.tsv`, `from_interim.py` format 2, canonical writer, store files, `index.tsv`, gen-measures; DEFAULTS per §8.3; the recompute check | the recompute check exact on every row; the drift gate; `tests/knowledge/` green; the data-mover census under both sets: zero movers; emit_sweep byte-identical | `make test` (normal), the data-mover census (boxqueue) | (13) the producer's noise off by one unit on one row (recompute red); (14) `raw.tsv` edited after its sha was recorded (sha check red) |
| **S2f** the forecast | census0.py re-run with the measured cards; the watched-witness reading; the report | the smp20 reading stated (above/below k*); row 1's mover forecast listed | J0 again (compile-only) | — |

## 10. Questions

**For Frank: none.** Every choice above is answer-free or already ruled (D186 add. 2 C9 for SIMD cards;
D176 Q3 for the census and the window; D149 for the labelled defaults).

**For main** (answer-free; each with the kit's recommendation):

1. **memchr-back DEFERRED** (§2.5): R-35 and [MEASURE-SET]'s `next:` list it; no priced row reads it (D77).
   Recommend: defer with its trigger; it costs ~1 minute of window if main wants it anyway.
2. **DEFAULTS** (§8.3): recommend (B), the literal D166 add. 2 reading, a zero-mover transition at S2e.
3. **The bundle's sampling-noise field** (§4.6): deferred to its producer; it amends span_pick.md:237-238.
4. **No match_api hunk** (§4.4): R-35 names one; nothing there moves.

### 10.2 Row 1's design items this note hands on (not decided here)

Which `find_hit` landing the price reads (or both, as two regimes); verify priced over T-VERIFY's step list
(span_pick R21) using `verify_cmp`'s (form, cls) keys; the `COVER_Z_E3` row and its trace line; the E2 family
unification reading the three `enter` cards; the band's bundle term (§4.6).

## 11. The three standing questions (docs/design/CLAUDE.md)

1. **The measurement regime: RELEVANT.** Every card names it (§2.3): Linux dev box (Zen 4 7700X), gcc 15.2
   `-O2`, glibc's memchr, CPU 7 pinned, sibling idle; throughput on long fresh streamed subjects (byte, hit),
   a candidate array (verify), whole-artifact find-all (enter); hits periodic AND random (a regime flip
   between them is exactly what the robustness rule wants seen); per-call (short-subject) regimes are NOT
   carded ([SPAN-PICK-PERCALL]'s, span_pick.md:198-199), so a priced row's per-call cells fall outside the
   cards' claim. A different box flips picks; that is a new set id, never this one.
2. **The independent control: RELEVANT.** Answers: G2's scalar byte loop on every arm before any clock.
   Values and noise: the pcrec-side recompute from `raw.tsv` (a separate implementation from §3.4's text,
   not importing `read.py`), the digest by ks_ref.py (python, from the spec's table, not the C). Drift: the
   in-group walk against the unit row, per group. "Stage 2 moves nothing": emit_sweep and the data-mover
   census, counted pcrec-side from artifact diffs (K35), never the kit's `moved`. The census (§7) shares the
   price formula with row 1, so it LOCALIZES only (SRS §8 item 2), never accepts. Populations: every job
   declares its group count and the queue counts it (POPULATION-SHORT).
3. **What moves when the data is regenerated: RELEVANT.** Re-measuring makes a NEW id (`measures.md` §8¶1);
   a re-reading of `raw.tsv` a new rev. With no reader (stage 2), nothing emitted moves under any set (§5's
   proof). From row 1, a new default set moves the picks of consulting artifacts and their
   `<PREFIX>_MEASURES` stamps: a default-set change is an abi event with its census (`measure_sets.md`
   §3.6, D162). A PAIR width retune (§3.6 (b)) stales the PAIR cards through their form hash.

## STATE AT HANDOFF

Rev 0, lane s2design. OWED: nothing of the design; every unit of §9 is unbuilt. No make, no timing, no box job.
Not a build go.
