# window_site — the UNIFIED WINDOW SITE: spans with a required core, one row family (design, rev 1)

Lane uwin (kit manager's lane), 2026-10-21, branch `lane/memfn-uwin` cut from `lane/memfn-b4scope`
(`3da6aa04c`). DESIGN ONLY: there is NO BUILD GO. Nothing under `memfn/src`, `src/`, `cli/`,
`lib/` or `tests/` changed; no make, no timing run.

Direction: Frank, 2026-10-21, to the kit. Today's hand-off is three mechanisms for one fact:
`mf_site.ctx[]` with its `absent` rule and caps; the REPORT kind with its own row (RPT) and check
(`kit_report_exact`); and fast rows with narrow intakes (ofsskip needs `plan_hint` and pcrec's
tables, so R-27 had to re-describe pcrec's site to fit it, panel finding M1). Frank's model:
pcrec states SPANS, each with a start offset (may be negative), a set per position and a
REQUIRED CORE; REPORT is the find-window with every span verified; most choices are declared
tables.

Reads behind this note: `memfn/include/memfn.h` (MF_SITE_ABI 18), `memfn/src/{compose,finder,
ofsskip,generic,pffind,fields.def}`, integration.md §14.5, §14.6, §14.7, §14.9, §15.1, §R4.3.5;
kit_proof.md §2.5, §3, §4; window_contract.md §2; ctx_span.md §3; requests R-18, R-21, R-25,
R-26, R-27; r27_report.md §2-§5; the panel `docs/dev/reviews/2026-10-21-r1-memfn-r27.md`;
walk_vs_v1_record.md; D161, D168, D169 + addendum.

---

## 0. One screen

**The facts (§1).** A window site states one or more SPANS and its frame:

| fact | per | meaning | unstated |
|---|---|---|---|
| start | span | signed offset of the span's first position from the candidate | refused |
| sets | span position | the byte set the position must hold (all 256 = "any byte") | refused (a span has ≥ 1 position) |
| core | span | the contiguous stretch of positions that must lie INSIDE the subject; may be empty | refused (empty is a stated value) |
| verify | span | YES: every candidate the kit yields satisfies this span, whatever the kit thinks it needs. NO: a true filter the kit may use or skip | refused |
| table offer | span position | pcrec already emits a membership table for this set, under this name (a host capability) | no offer (never read as a set) |
| floor | site | SUBJECT (reads may go to offset 0) or pcrec's expression; a candidate needing a read below an expression floor is pcrec's EDGE | refused where any span reaches below the candidate |
| frame | site | today's form/op/handoff/empty/end_back/use/body/decl_point/hooks, unchanged | as today |
| subject facts | art | the analysis object and the measure set, already on `mf_art_begin` | as today |

**The absence rule.** A position that falls off the subject (before 0 or at/after `n`) PASSES
outside the core and FAILS inside it. No per-position bit is needed: absence is monotone at both
edges, so a position between two core positions can never be absent alone (§1.2).

**One row family (§2).** Every forward FIND (PF, MLINE, the VM hat, the offset-skip block, the
pre-check's FUNC parts, the REPORT/cover site) is served by ONE family of five declared
first-match tables over the stated spans: A the STOP PICK, B the STOP'S FIND FORM (the finder
table's FIND slot, the walk for an unknown subject; a [MEMFN-REGIME] slot left empty), C the
VERIFY PLAN, D the RESUME, E the FRAME. The generic row is the family's floor.

**What retires (§4).** `ctx[]`/`nctx` and `MF_MAX_CTX`/`MF_MAX_AHEAD`; `absent`, `consumable`,
`consumable_len`, `exact_len`, `prefix_stated`, the BOUNDED/CONTEXT span classes; the REPORT
kind's special meaning, RPT and `kit_report_exact`; the per-term `need` (it becomes the per-span
verify); `read_floor` (merged with the `floor` hook); the window fields W0-W2; `consumer`;
ofsskip/pffind as separate arms with narrow intakes; then, after the M5 comparator holds,
`plan_hint`, `plan_pos` and `rank_*`.

**Staging (§5), every step zero artifact movers until B1:** W1 the kit's internal span form and
the family, built from today's fields (kit-only, no ABI) → W2 R-27 on the family, preview-only →
W3 pcrec states spans (`MF_SITE_ABI` 19, pcrec builder restatement, shadow-compared) → W4 the old
fields retire (`MF_SITE_ABI` 20) → W5 the stop pick moves to the kit, then `plan_hint` retires
(`MF_SITE_ABI` 21) → B1 routes REPORT by default: the ONE byte-moving step here, a pcrec abi event
with its deny row in the same commit.

**Open questions for Frank: §9** (five, each with a leaning).

---

## 1. The facts

### 1.1 The minimal set, and what each replaces

A SPAN is a run of consecutive positions `start, start+1, ..., start+len-1` relative to the
candidate `c`, one byte set per position. A gap inside a span is a position whose set is all 256
bytes. The site's candidates are the positions `c` where EVERY span holds (a conjunction). Spans
may overlap; the kit never needs a stacking rule, because each span is tested on its own terms.

| fact | replaces today | why it is enough |
|---|---|---|
| span start + sets | `mf_term` (SET/RUN, `offset`, `set`, `run`/`mask`/`run_len`), `ctx[]` entries, the context stop's `pred`, W0-W2 (`window_stated`, `move_back`, `overshoot`) | a RUN term with a mask is a product of per-position cubes, so sets lose nothing; every FIND site today states `move_back` = its least offset and `overshoot` 0 (`pcrec_memfn_window_is_candidate`), i.e. "the window is the candidate", which the span start already says |
| core | `absent` (SATISFIES/FAILS), `span_class` BOUNDED/CONTEXT, the "every term read below n" rule (§14.5 rule 3), Q-R7-1's reads-below range | §1.2 |
| verify | per-term `need`, per-predicate `need`, `consumable`, `consumable_len`, the REPORT kind's "every term REQUIRED" | §1.4 |
| table offer | `table_ref` + `table_name` | the same capability, per position; a row that wants it reads it, no row requires it (§2.4) |
| floor | `read_floor` (enum) and the `floor` hook (text) | one fact, §1.3 |

Bounds: ONE position range per site (the least and greatest offset any span may reach), a SHAPE
bound DERIVED from pcrec's producers (`PCREC_PREFIX_K_MAX` on each side of span 0,
`PCREC_MAX_REQ_RUN_SCAN` for the run) and asserted where pcrec builds the site; and a span count
derived the same way. Neither is a tuning constant and neither carries a trigger. `mf_class.proven[]`
keeps its meaning over that range.

**Every fact has an UNSTATED handling (no silent defaults).** A missing start, set, core or
verify is refused naming the field; an empty core is a stated value; a missing table offer means
"no table", never a set; the subject facts keep E-1's present-or-explicitly-absent rule.

**Not a fact, stated so nobody adds it:** exactness (EXACT/SUPERSET). The kit tests byte
MEMBERSHIP and proves membership (`proven[]`). Whether a verified span is a LANGUAGE proof is
pcrec's reading of the kit's proof (kit_proof §4.2 "Language vs membership"). So R-26.7 is not
needed: a SUPERSET context item is sent as a verify-NO span (a filter), and a `cover` site
declines on an inexact item exactly as today (C6/C11), all on pcrec's side.

### 1.2 The core rule, and why no per-position absent bit is needed

**Rule.** At candidate `c`, a span holds iff for every position `d` of the span:
- `c + d` inside the subject: `s[c+d]` is in the position's set;
- `c + d` outside the subject: `d` lies outside the core.

**Claim.** Any per-position absent assignment pcrec could state is equivalent to one contiguous
core. Proof: let FAILS-positions be those where absence must fail. Take the core as their convex
hull. A position `p` inside the hull lies between core positions `q1 ≤ p ≤ q2`. If `c+p < 0` then
`c+q1 < 0`; if `c+p ≥ n` then `c+q2 ≥ n`. Either way the span already fails, so `p`'s own absent
verdict never decides anything. Absence can only happen at the two edges, never in the middle.

**Per-position vs per-item.** The generic row's `ctx_pred_test` today treats a SATISFIES item as
a whole ("holds if any read is outside"). Per position, an absent position passes and a present
one is still tested. The two agree on every item any producer emits: SATISFIES items are width 1
(kit_proof §3.3's table; ctx_span §3.5 declines a negative lookbehind or lookahead wider than one
byte). A future SATISFIES item wider than one byte whose meaning is whole-item is not a span; the
producer declines it (§7).

**Every current site, restated** (builders read by grep at `3da6aa04c`):

| site (builder) | spans | core | verify |
|---|---|---|---|
| PF FIND, DFA scan / HYB_PF (`find_site`, `emit_dfa.c`) | one, `{0: S}` (S = the candidate set, table offered) | `[0]` | YES (`need` REQUIRED today) |
| PF bounded (`holdback`, `end_back` 1) | as PF; the range keeps `end_back` | `[0]` | YES |
| VM hat seek (VM_ATTEMPT) | one, `{0: S}` | `[0]` | YES |
| MLINE `(?m)^` stop (`mline_find_of` + `pcrec_memfn_context_stop`) | one, `{-1: \n}` | `[-1]` (today's `absent` FAILS) | YES; floor = the expression `start` (the edge is pcrec's) |
| offset-skip FUNC (`ofs_pred_of`) and the pre-check's FUNC parts | two: R = the run (REQUIRED today) and K = the scan byte and the selected k-set positions (OPTIONAL today) | R: all its positions; K: all its positions | R YES, K NO |
| cover / REPORT, main's Z2 (aeb381c25: `known.c` `cover_ctx_item` and the site builder, `emit_dfa.c` `emit_cover`, `DELEG_COVER`; routed only through the harness lever `--harness=kit-proof`, which calls `mf_preview(art, "R-26.6")`) | span 0 `{0..k-1: S_d}`; one span per context item, `{-1: C_{-1}}` and/or `{k: C_k}` | span 0: `[0, k)`; an item: its position if FAILS, empty if SATISFIES | all YES |
| kit_proof §3.3 rows: `\b`/`\B`, `(?<=X)`, `(?<!X)`, `(?m)$`, `(?=X)`/`(?!X)` width 1, `\z` (`C_k = ∅`, SATISFIES) | a one-position span at -1 or k | FAILS → in core; SATISFIES → empty core | as the consumer needs |

`\z` shows the rule's reach: an empty set with an empty core means "this position must not
exist", i.e. `c + k = n`. An empty set inside a core can never hold; the site is well defined and
its answer is "no candidate" (§2.4 sends it to the floor row, panel S5).

**Out of the family, unchanged:** PRESENCE spans (`pspans`, ALL_PRESENT): their offset from the
match start is unbounded (`omin` only), so they have no position relative to a candidate and no
core. SKIP/ADVANCE, the EXPR VERIFY run compare (VMRUN) and MISMATCH are other operations; the
verify chain's run compare (runcmp) is shared with VMRUN, as today.

### 1.3 The floor and the edge (one fact for two fields)

Today MLINE states BOTH `read_floor` SUBJECT and the `floor` hook `"start"`; the enum says reads
may reach offset 0, the hook says they stay at or above `start`. One fact replaces both:
- **SUBJECT**: every read lies in `[0, n)`; below 0 the core rule decides. A REPORT site states it.
- **an expression F** (pcrec's text, `floor <= lo` its precondition, Q-G2-6): every read lies in
  `[F, n)`. A candidate whose span positions would need a read in `[0, F)` is NOT COVERED: the
  kit does not yield it and pcrec's EDGE attempt owns it (window_contract §2.4 "Coverage and the
  edge", today's MLINE behaviour).

This replaces kit_proof §3.5's refusal ("LO with a below-origin term has no verdict") by the edge
rule that MLINE already lives under. A site whose consumer cannot own an edge (REPORT) states
SUBJECT; that is pcrec's builder obligation, asserted there.

**The candidate range** becomes one rule: `c ≥ lo`, `c ≤ n`, every core position of every span
inside `[floor, n - end_back)`, every non-core read inside `[floor, n)` or below 0. Q-R7-1's
special reads-below range is this rule's case with no core at or after offset 0 (`(?m)^$` on
"a\n" still finds 2).

### 1.4 Where `need`, `consumable`, R-26.7 and the REPORT kind go

- **`need` → verify, at SPAN grain.** §14.5's REQUIRED ("a pcrec decision relies on it having
  been tested") and window_contract's T-NEED ("dropping it could let a budgeted engine do more
  work") are one obligation: every yielded candidate satisfies the span. OPTIONAL is "true, speed
  only". Today only the offset-skip predicate mixes needs inside one predicate (run REQUIRED,
  scan byte and k-set OPTIONAL, `ofs_pred_of`); it becomes two spans, R and K. Every other
  builder states one need per predicate. The rule "the kit may never ADD a constraint pcrec did
  not pass" survives unchanged.
- **R-25 survives as the proof rule, not as a field:** `proven[d]` states only what the rendered
  plan TESTS (§2.4), whatever a span's verify says.
- **`consumable` / `consumable_len` → verify.** No row reads either (fields.def: "no form reads
  it"). Their only stated non-zero value is the cover site's `consumable_len = k` with every term
  REQUIRED, which verify YES already says. The other reading, "prove it if cheap and I will use
  it", has no customer; filed (§9 does not ask it, D77).
- **`exact_len` / `prefix_stated` → pcrec-internal.** No kit row reads them. They are pcrec's
  interpretation of `proven[]` as a language proof (`span0_exact_len`, the X0 check), and stay in
  pcrec's `MkLang`.
- **R-26.7 (EXACT/SUPERSET) dissolves** (§1.1).
- **The REPORT kind.** REPORT is the window site with every span verify YES. Its separate row,
  its separate exactness check and its refusals keyed on the kind retire. What is left is a
  CATEGORY fact: what consumes the candidates. `site_kind` and `consumer` fold into one consumer
  category (window_contract's S3 already retires `consumer`), whose value for the cover site is
  "pcrec's finisher reports it". The find-form table reads only one thing from it, the VM
  attempt's seek role (D1 vs D1w). §9 Q3 asks whether to keep that value at all.

---

## 2. One row family

### 2.1 The shape

```
  candidate stream at c ≥ lo:
    A  pick the STOP: one position d* of one span (or none: the floor row)
    B  FIND the next p ≥ c + d* with s[p] in set(d*)            -> c = p - d*
    C  test the VERIFY PLAN at c, under one core bound + per-position guards
    D  on failure, RESUME at c + shift (1 unless a shift row holds)
    E  render all of it in the site's FRAME (FUNC function / STMT block)
  floor: the generic row (a byte loop over the conjunction), reached when A, B or C has no row
```

Every table is a `kit_table` on the kit's one walk (`kit_walk`, compose.c): first match, each row
with its contract (fields.def), its predicate, its deny where it moves bytes, and its basis. No
if-then web: the choice of stop, form, plan, resume and frame is five lookups.

### 2.2 Table A — the stop pick

| row | holds when | stop | basis | lives |
|---|---|---|---|---|
| A-hint | pcrec states `plan_hint`/`plan_pos` | that position | pcrec's model (transitional) | W1 → retires at W5 |
| A-one | the site's verify spans have exactly one position not proven by another (PF, MLINE, the VM hat) | that position | derived | W1 |
| A-model | a multi-position site | `prefix_k`'s pick, transcribed (its five constants, the 2x materiality bar, `verify_cost`; each labelled where it stands, D149) | pcrec's model, moved (§3) | W5 |
| A-mass | a multi-position site no earlier row decides (before W5: the REPORT site) | the position of least byte-rate mass (presence.c's `set_mass`, cardinality without a table); ties by the declared TIE column | derived; the tie column is MEASURED by job 581's PRR arm (panel T1) | W2 |
| (none) | — | the floor row renders the site | — | — |

The TIE column is one declared column shared with P3's pick (panel U5): today P3 breaks ties
RIGHTMOST and R-27's PRO was measured LEFTMOST. Until PRR reads, the column states LEFTMOST for
A-mass and RIGHTMOST for P3 and is labelled UNMEASURED DEFAULT on A-mass.

A stop must lie in a span's CORE (a non-core position may be absent, so it cannot be the stop);
it may come from a verify-NO span (today's OFS scan byte is OPTIONAL).

### 2.3 Table B — how the stop is found

Table B IS the finder table's slot FIND (`fd_rows`, finder.c), asked for the one-position
sub-question "find the next byte in set(d*) at offset d*". No second walk implementation exists
(panel M3, D122).

| row (today's id) | holds when | form | basis |
|---|---|---|---|
| D1c | the stop lies below the candidate (MLINE) | the libc back search (`pf_memchr_back`) | UNMEASURED DEFAULT (today's) |
| D1 | one member, not the VM attempt's seek role | `memchr` | UNMEASURED DEFAULT (today's) |
| PAIR | the stop is a two-member cube inside a verify span's literal stretch, in a FUNC frame (today's `fn-pair` predicate restated over spans) | two `memchr` streams, the nearer hit | today's |
| (SIMD layer) | `-fmemfn-simd`: vrun's PREFIX rows over the stop's stretch | today's | today's, inert at OFF |
| REGIME (SLOT, EMPTY) | [MEMFN-REGIME] states the subject's stops are sparse or irregular | a wide form (V1/M64) | — : designed as a slot, NOT filled |
| D1w | one member in the seek role (the VM hat, Q-R5) | the table walk | UNMEASURED DEFAULT |
| R7w | every other set | the WALK (Frank, 2026-10-21: "the walk when the subject is not known"; walk_vs_v1_record.md) | MEASURED (B4′) |

D2 (span 0 a RUN term → the nested fn walk) and RPT (FF_PROOF) retire: a run's stop is one of its
positions under A, and REPORT is not a separate form.

### 2.4 Table C — the verify plan

The plan is ONE object: the list of positions tested at a stop, in order, each with its test. The
renderer walks it, `proven[]` is computed from it, and a trace build asserts the rendered
positions equal it (panel S1).

| question | row | rule |
|---|---|---|
| which positions | C-all | every position of every verify-YES span, minus the stop's own when its set is the stop's (the find proved it) |
|  | C-hint (W1 → W5) | plus every position pcrec sent in a verify-NO span (today: prefix_k's selected subset; ofsskip tests every sent term) |
|  | C-model (W5) | plus the verify-NO positions prefix_k's selection would test, transcribed (§3) |
| grouping | C-run | inside ONE span, a maximal stretch of consecutive one-member or cube positions is ONE run compare (runcmp's rows: memcmp / words / overlap); a verify-NO span's positions are tested one by one. This is today's grouping on every routed row; W3's identity gate checks it |
|  | C-meet | two spans' positions at one offset are tested once, as the intersection (panel S5: merge by OFFSET); an empty intersection sends the site to the floor row (plant R27-i) |
| a set's test | C-table | an offered table: pcrec's name (rule 7) |
|  | C-own | no offer: the kit's own test (generic's `set_test`, one rendering) |
| order | C-asc | ascending offset (today's ofsskip and generic order) |
| bounds | C-core | ONE hoisted test that every core position is inside `[floor, n - end_back)` for this `c` (`c + K ≤ n`, `c + D ≥ 0`); every non-core position tested as `(outside ? pass : member)` with its own guard. No read leaves `[0, n)`, nor `[F, n)` under an expression floor (panel M4/S3; the counterexample "cat" + FAILS `s`@3 has `@3` inside the core, so the hoisted bound rejects `c = 0` on "cat") |
| text shape | C-chain | the plan as ONE `&&` chain after the bound test, `pos = c + 1` on failure (the shape job 580 measured as PRO; separate branches read 1.2-1.8x on year4) |

### 2.5 Table D — the resume

| row | holds when | resume | deny | basis |
|---|---|---|---|---|
| D-shift (fn-shift, R-27's E4) | DECLARED, NOT BUILT: a plan where some tested offset `j` has `t > 1` (the least `t` with `S_{j-t} ⊄ S_j`) | `c + t` at the failing `j`; separate branches | its own | trigger: a measured cell; job 580 read it costing year4 12-48%, so never a default |
| D-hors (panel U6) | DECLARED, NOT BUILT: a long span of dense sets where the stop search gains nothing | Horspool over sets: a bad-character shift from the window's last position | its own | trigger FIRED in 580 (hex8); job 581 measures it |
| D-one | always | `c + 1` | — | the floor of this table (today's) |

### 2.6 Table E — the frame

| row | holds when | text |
|---|---|---|
| E-func | FUNC / RETURN, miss `n`, no expression floor | today's `static inline size_t` function with the D155 selector seam and the PREFIX slot (ofsskip's frame, transcribed) |
| E-stmt | STMT / ASSIGN (or ON_MISS) | today's PF block: the guard, the post-test, the bounded wrapper (`end_back` 1), the `moved` hook, the storage point (`decl_point`) |
| E-generic | anything else | the floor row |

The frame is where the panel's M1 fix lands for free: a REPORT site is STMT/ASSIGN, so it is
served by E-stmt with no re-description and no FUNC rewrite.

### 2.7 The floor, and what folds where

The floor row is `generic` (compose.c's last arm): a byte loop over every span under the core
rule. It honours every fact, so no deny leaves a site without code (§14.6).

| row today | fate | where |
|---|---|---|
| `pf_memchr`, `pf_memchr_bounded` | FOLD | A-one + B D1 + C (empty plan) + E-stmt (bounded by `end_back`) |
| `pf_walk`, `pf_walk_bounded` | FOLD | A-one + B R7w/D1w + E-stmt |
| `pf_memchr_back` | FOLD | A-one + B D1c + E-stmt, floor expression |
| `ofsskip` (`fn-memchr`, `fn-pair`, vrun PREFIX) | FOLD | A-hint/A-model + B D1/PAIR/SIMD + C + E-func |
| `precheck` (3 rows) | STAY (ALL_PRESENT); its FUNC parts render through the family | — |
| `runcmp` | STAY as C-run's compare rows and VMRUN's EXPR VERIFY | — |
| `mismatch_inplace` | STAY (MISMATCH) | — |
| `generic` | STAY: the family's floor | — |
| RPT (`fd_rows`), `kit_report_exact`, `SF_PROOF_EXACT`, `FF_PROOF`, D2's nested walk | RETIRE | §4 |

---

## 3. The stop choice moves to the kit (integration.md §14.9 item 2, §R4.3.5's M5)

**Path.**
1. **W1**: A-hint is the first row, so every native site renders pcrec's pick, byte for byte.
2. **W5a, the transcription, zero movers.** `prefix_k`'s selection is transcribed into the kit as
   A-model and C-model (the stop AND the verify-NO subset). pcrec now sends the WHOLE k-set slice
   as the verify-NO span. On every compile, the trace build's SHADOW COMPARATOR asks A-model and
   C-model and asserts they equal pcrec's `plan_hint`, `plan_pos` and the subset pcrec selected;
   A-hint still decides. Population: every OFS and pre-check FUNC site of every emit_sweep arm,
   with a floor on the comparison count (a comparator that compared nothing is red, K35).
3. **W5b, the switch, zero movers.** A-model decides; A-hint is deleted; emit_sweep every arm is
   byte-identical (MEASURED, the plain arm is the witness: panel M6).
4. **W5c, retirement.** pcrec stops computing `plan_hint`/`plan_pos`/`rank_*`; vrun's KB pick
   reads the kit's own ranking from byte-rate (window_contract S2/S3); `MF_SITE_ABI` 21.
5. **Not in M5:** ADOPTION (whether an offset-skip block exists at all) stays pcrec's semantic row
   until M5′, the ruled byte-moving event of §R4.3.5 (Q40).

**Comparator honesty.** The comparator's two sides are pcrec's live model and the kit's
transcription: it proves the MIGRATION is byte-identical, not that the pick is right. Correctness
stays with the byte-loop oracle (`proof_run`) and the answer gates, which share no source with
either side.

**A-mass vs A-model on REPORT sites.** Before W5, REPORT sites (no hint) take A-mass. At W5a the
comparator also LOGS, unasserted, A-model's pick on every REPORT site. If the two differ on any
of job 580's eight cells beyond noise, that is §9 Q2's measurement; if not, A-mass retires into
A-model and the family has one stop rule.

---

## 4. What retires, with its readers (by grep at `3da6aa04c`; re-grep at each build commit)

| retires | at | readers |
|---|---|---|
| `mf_site.ctx`/`nctx`, `MF_MAX_CTX`, `MF_MAX_AHEAD` (the caps and UL-8's trigger) | W4 | `memfn.h`, `memfn/include/CLAUDE.md`, compose.c (site check), generic.c (`site_test`), finder.c (`[FLD_ctx]`), fields.def/gate.c (`cl_ctx`), `src/gen/known.c` (`cover_ctx_item`), `tests/memfn/proof_check.c`, `memfn/tests/g2/` |
| `mf_pred.absent`/`consumable`, `mf_absent`, `mf_consumable` | W4 | `memfn.h`, compose.c, generic.c (`ctx_pred_test`), gate.c (`cl_absent`, `cl_consumable`), fields.def, `src/gen/known.c`, `src/gen/memfn_sites.c` (`pcrec_memfn_context_stop`) |
| `prefix_stated`, `exact_len`, `consumable_len` (contract fields; pcrec keeps them in `MkLang`) | W4 | `memfn.h`, fields.def/gate.c, compose.c, `src/gen/memfn_sites.c` (`pcrec_memfn_span0_stated`, `span0_exact_len`), `src/gen/known.c` |
| `span_class` BOUNDED / CONTEXT (PRESENCE stays) | W4 | `memfn.h`, compose.c, finder.c (`SF_SPAN0`, `SF_CONTEXT_STOP`), `memfn_sites.c` |
| `read_floor` (merged into the floor fact) | W4 | `memfn.h`, compose.c, gate.c (`cl_read_floor`), fields.def, `memfn_sites.c`, `known.c` |
| W0-W2 (`window_stated`, `move_back`, `overshoot`, the unbounded sentinels) | W4 | `memfn.h`, compose.c, fields.def, `memfn_sites.c` (`pcrec_memfn_window_is_candidate`) |
| per-term and per-predicate `need` (becomes the span's verify) | W4 | `memfn.h`, every builder (`emit_dfa.c`, `emit_vm.c`, `memfn_sites.c`, `known.c`), compose.c (`pred_kinds`), finder.c (`[FLD_need]`, `cl_need`), presence spans (keep their own need) |
| REPORT's special meaning: RPT, `kit_report_exact`, `SF_PROOF_EXACT`, `FF_PROOF`, the RESULT-only refusals | W2 (RPT unrouted, preview only, so no default byte) | finder.c, compose.c, kit.h, `memfn/src/CLAUDE.md`, `memfn/docs/finder_history.md`, `tests/memfn/run_proof.sh`, `arm_fixtures.c`, `proof_check.c`, S1255, S1256 (re-aimed at the family's proof and the floor row) |
| `consumer` (folded into the consumer category) | W4 | `memfn.h`, compose.c, `emit_dfa.c`, `emit_vm.c`, `memfn_sites.c`, `known.c`, `formhash.c`, `memfn/tests/g2/g2_gen.c` |
| ofsskip/pffind as arms (their narrow intakes: one-byte scan, tables required, `plan_hint` required) | W1 | compose.c `arms[]`, precheck.c (FUNC parts), `tests/memfn/rows.tsv`, finder.c's `fd_route` arm map |
| `plan_hint`, `plan_pos`, `rank_n`/`rank_pos`/`rank_ppm` | W5c | `memfn.h`, ofsskip.c, precheck.c, vrun.c, compose.c, formhash.c, `emit_dfa.c` (`ofs_pred_of`, `ofs_pred_rank`), `memfn_sites.c`, `known.c`, `memfn/tests/g2/*`, `tests/memfn/{proven_check.c,arm_fixtures.c,rank_check.py,proof_check.c}`, the `[OPT-REQPOS]` note and the `REQ_RUN @idx` spec text (§14.9 item 1's re-spec, a `docs/spec/findings.md` hunk) |
| `mf_preview("R-26.6")` | stays until B1; then its step name retires with RPT | `memfn_sites.c` (`pcrec_memfn_art`, behind `pcrec_kit_proof_routed`), `src/core/internal.h`, the R-26.6 sabotage rows S1251-S1254 |
| Z2's cover statement in R-26 terms (ctx items, REPORT kind, `consumer` RESULT, prefix facts `exact_len = consumable_len = k`, `read_floor` SUBJECT) | restated at W3, old spelling gone at W4 | `known.c` (`cover_ctx_item`, the site builder, `pcrec_cover_proof_diff`), `emit_dfa.c` (`emit_cover`), `memfn_sites.c` (`pcrec_memfn_span0_stated`: the true `exact_len` stays pcrec-internal), the kitproof arm's rows (§5.1) |

---

## 5. Staging at zero artifact movers

| step | side | what | movers | `MF_SITE_ABI` | pcrec abi | deny |
|---|---|---|---|---|---|---|
| W1 | kit | the INTERNAL span form: one function reads today's `mf_site` (terms, needs, `ctx[]`, `absent`, the context stop, `floor`/`read_floor`, `plan_hint`) into spans + core + verify + offers; tables A-E; ofsskip/pffind become rows of it | 0, MEASURED (emit_sweep every arm, identity gates, G2, `REACH_ONLY=1` mech re-aim) | none | none | none (no byte moves) |
| W2 | kit | R-27 on the family: A-mass, C-own, the core bound, E-stmt for REPORT; RPT and `kit_report_exact` retire into the family's plan-derived proof; preview-only (`mf_preview`) | 0 default; preview arts move (harness only) | none | none | owed at B1 (panel Q1) |
| W3 | pcrec (a request main files: "the window site stated as spans") + kit | pcrec's builders state spans directly (PF, MLINE, VM hat, OFS, pre-check FUNC parts, and Z2's cover site, §5.1); the kit's trace build asserts W1's internal form from the OLD fields equals the STATED spans on every compile | 0, MEASURED | 19 (appended fields) | none | none |
| W4 | kit + pcrec builders | the old fields leave the contract (§4's W4 rows) | 0, MEASURED | 20 (layout) | none | none |
| W5a/b/c | kit (transcription, switch) + pcrec (stop computing) | §3 | 0, MEASURED at each | 21 at W5c | none | none |
| B1 | kit + pcrec, ONE commit | REPORT routed by default (the cover site renders the family's text); also waits for R17-b′ B4 (R-27's sequencing) | YES: the cover artifacts | none | YES, same commit (readers by grep, D76/D94; G1 both layers; R-27.1's 650 re-run) | YES, born in this commit |
| later | kit | Table B's REGIME slot ([MEMFN-REGIME]); Table D's shift rows (each on its measured trigger); M5′ adoption (Q40) | each its own event | as needed | each | each its own |

Every `MF_SITE_ABI` event is a kit-contract change: memfn journal, ledger, `memfn.h` comment,
`memfn/include/CLAUDE.md`. W3 is the only step pcrec must REQUEST (main files it on main before
its lane is briefed); W4 and W5c each carry a pcrec builder hunk in the same commit as the kit's.

### 5.1 W3's pcrec restatement includes Z2's cover site `[addendum: kit manager, 2026-10-21]`

Main's Z2 (merged `aeb381c25`, harness-only, 0 default movers) states the cover site in
R-26's terms: `ctx[]` items, the REPORT kind, `consumer` RESULT, span 0's prefix facts and
`read_floor` SUBJECT, with `mf_preview("R-26.6")` on the lever's arts. W3's request names
it as one of the builders it restates, beside PF, MLINE, the VM hat, OFS and the pre-check
FUNC parts:

| Z2 states today (R-26 terms) | W3 states | moves |
|---|---|---|
| `pred` = span 0, k SET terms, all REQUIRED, BOUNDED, `exact_len = consumable_len = k` | span 0 `{0..k-1: S_d}`, core `[0, k)`, verify YES; `exact_len` stays in `MkLang` (C8/X0 keep reading it there) | nothing (harness-only arts) |
| `ctx[]` items at -1 and k (`cover_ctx_item`), `absent`, `consumable` YES | one span per item, core per §1.2, verify YES | nothing |
| `site_kind` REPORT, `consumer` RESULT | the consumer category's RESULT value (§9 Q3) | nothing |
| `read_floor` SUBJECT | floor SUBJECT | nothing |
| `pcrec_cover_proof_diff` (the DEFAULT build holds the kit's class to the stated sets, C14) | unchanged in meaning: the stated sets are the verify spans' sets; it stays pcrec's check | nothing |
| `mf_preview("R-26.6")` behind the lever | unchanged until B1 | nothing |

Its zero-mover witness is the same as Z2's: emit_sweep (every arm) for the default build,
plus the lever's own arts compared before/after the restatement (`--harness=kit-proof`,
the kitproof arm's 393 cells and X1), because the default build never renders the cover
site.

**Sabotage re-aims are DERIVED, never hand-listed.** At each W step (W1-W5, B1), in the
step's own commit, the build lane runs this rule over EVERY row in `tests/mech/sabotages/`
(Z2's S1130-S1141, S1144, S1148, S1149 and whatever of S1257-S1290 exists by then are
members, not the list):
1. **Candidates** = rows whose `SAB_FILE` is in `git diff --name-only <base>..HEAD`.
2. **Anchor test**: `VALIDATE_ONLY=1 bash tests/mech/run_sabotage_matrix.sh <candidates>`;
   a row whose `SAB_BEFORE` no longer resolves MUST be re-aimed.
3. **Intent test**: a candidate whose `SAB_BEFORE`/`SAB_AFTER` text lies inside a changed
   hunk of the diff (grep the anchor's lines against `git diff -U0`), or names an identifier
   §4 retires at this step, is re-aimed with its intent re-verified (BOILERPLATE: "a re-anchor
   needs its intent re-verified").
4. **Reach test**: `REACH_ONLY=1 bash tests/mech/run_sabotage_matrix.sh` over the arms the
   step touches (`kitproof`, `memfnfinder`, `memfng2`); every row whose witness no longer
   reaches its site is re-aimed.
5. The step's report prints the derived list with the rule's output (the union of 2-4) and
   the count; a row may be RETIRED only where §4 retires the code it plants in, named with
   its successor plant (e.g. S1256 "NONE accepted on REPORT" becomes the floor-row plant on
   an all-verify site).

Illustration only (not the list): an identifier pre-screen at main `ca4ec4d10`, restricted
to the files the W steps edit, already flags about 22 rows (S1101, S1102, S1133, S1137,
S1222-S1226, S1251, S1252, S1256, S689, S736, S737, S750-S754, S794, S849, S917). Steps 1-4
find the rest, Z2's rows anchored in edited hunks included.

Why W1 before W3: R-27 is not blocked on pcrec. The kit can normalize today's fields itself and
prove the family at zero movers; pcrec's restatement then has a comparator ready.

---

## 6. R-27 as the first consumer

Job 580 (r27_report.md §5): PRO, the window search with no shift, meets R-27.1's bar on 42 of 48
non-match cells and beats today's REPORT pick everywhere. Misses: hex8-bounded (4 cells),
cat-bounded `search_short`/dense against COV (1.18), file-ext-order `search_short`/none (1.033).
SHF fixes most of hex8 `search_short` but costs year4 12-48%. Under this design PRO IS the family:
A-mass (memchr for one member, the walk for a set via Table B), C-chain, D-one, E-stmt.

| finding | answer under the family |
|---|---|
| M1 (RPT re-describes the site) | DISSOLVED. Nothing re-describes: the family reads pcrec's spans; STMT/ASSIGN is E-stmt; the stop is Table A, not `plan_hint` written over pcrec's MF_NO_PRED; SET→RUN is C-run's grouping |
| M2 (fallback as if-then) | the floor row of every table, ending in generic |
| M3 (a second walk inside ofsskip) | Table B is the finder's FIND slot; [MEMFN-REGIME]'s slot is its row, no new code |
| M4 + S3 (read limits under ctx) | C-core: one hoisted core bound, per-position guards outside the core, the floor fact. The "cat" + FAILS `s`@3 counterexample is a core position |
| M5 (E4 is a REPORT special case) | D-shift, a declared row with its own predicate, deny and census; not built |
| M6 (zero movers argued) | every W step's zero is MEASURED by the emit_sweep plain arm |
| M7 (POSCOST notice) | stands: R-27 is [MEMFN-POSCOST]'s first built member; main's row |
| S1 (a dropped ctx item keeps `proven[]`) | the plan is one object: `proven[]` from it, the renderer walks it, a trace assertion holds rendered = plan; drift plant kept |
| S2 (over-reads invisible) | unchanged harness fix: exact-size buffers with per-site satisfying sentinels, `make asan`; plants R27-g, R27-h |
| S4 | dissolved (no s′) |
| S5 (merge by offset) | C-meet; empty intersection → floor row; plant R27-i |
| S6 (stop reach) | a harness switch beside `mf_preview` forcing each Table A row and each core position in turn; floors on walk stops, stops at d > 0 and a shift strictly between 1 and j+1 |
| S7 | plant R27-e2; a gap is a full-set position (native now); table = set asserted where C-table reads an offer |
| S8 | the kit is encoding-blind: spans are bytes; the cover builder states `end_back` 0; the 8-bit precondition is the frame's |
| T1 | the TIE column (§2.2); PRR in job 581 |
| T2-T9 | job 581's, unchanged by this shape: the no-clock differential vs python `re`, PRF (FUNC proxy) for the three literal cells, the profile header and "scalar only" (SIMD is pcrec-bench's, D144 add. 4), absolute ns columns, PRO2 A/A, hits per KiB, `cpu_busy`, the match-regime flag |
| Q1 (deny) | born at B1's routing commit, or earlier in any commit that moves a default byte |
| Q2 (tie) | the declared column |
| Q3 (E4) | D-shift or nothing |

**hex8-bounded stays an algorithm question.** It is a span of dense sets (`[0-9a-f]` x 8) with
context; a stop search gains little on hex-rich text. D-hors (Horspool over sets) is its candidate
as a declared row: job 581 measures it. If it misses, the honest options are a waiver of that cell
for B1 or a further measured row, never a hex8-only special case (§9 Q4).

**Unlocks from the panel, placed:** U1 (context on ordinary FIND sites) is native: any span not
covering offset 0 is served. U2 = §3. U3 = Table B. U4/U6 = Table D. U5 = the tie column. U7 =
the harness.

---

## 7. The pcrec-side producer: D168 / [DD-11.5], `ctx_span.md`

D168's ONE producer (`span_facts`, `MkLang`) states span 0's per-offset slice `S_d` and one
record per context ITEM (`MkCtx`: terms at offsets, `absent`, `form`). It maps onto spans with no
new field:

| `MkLang`/`MkCtx` | span |
|---|---|
| `S_d`, d < `exact_len` | span 0's positions; core = all; verify per the consumer (cover: YES) |
| an item's terms | one span from its least to its greatest offset; gaps full-set |
| `absent` FAILS / SATISFIES | core = the item's positions / empty (width-1 SATISFIES only, §1.2) |
| `form` EXACT | may be verify YES and be consumed as a proof (pcrec's reading) |
| `form` SUPERSET | sent only as verify NO (a filter); a cover site declines on it (pcrec-side, as today) |

**Free consequences (Frank).** A fixed-length POSITIVE lookbehind longer than one byte
(`(?<=ab)`) is a two-position span at -2..-1, core both. A lookahead AFTER the span longer than
one byte is a span at `k..k+w-1`. `\b` and a width-1 negative lookbehind are one-position spans
outside the core.

**The UL-8 cap lift dissolves.** `MF_MAX_CTX` = 2 existed because stage 1's machine reading
states one item each side, and `MF_MAX_AHEAD` = 1 because its after-context is one byte. With
spans, a site's count and reach are shape bounds derived from the producer (§1.1), so there is
no cap to lift and no trigger to wait on.

**What does NOT dissolve:** the SOURCE switch. The DFA machine reading cannot see a lookbehind
wider than one byte (kit_proof §3.3: the DFA reads one seed byte), so a cover site with
`(?<=ab)` needs the facts-layer producer to be THE context source, with the machine reading as
its control (ctx_span P1b). That is pcrec's own event with its own controls (X1 against
libpcre2); the kit side is ready the day it lands.

---

## 8. The three standing questions (`docs/design/CLAUDE.md`)

1. **Measurement regime: RELEVANT, only at the byte-moving steps.** W1-W5 move no artifact byte,
   so they are identity steps, read by emit_sweep and the identity gates, not by timing. B1 is
   read in R-27.1's regime: the 650 harness (match / search_short / throughput x real / none /
   dense), scalar layer, Linux, `taskset`-pinned, with job 581's absolute columns and A/A pair; G1
   at both layers; the SIMD verdict is pcrec-bench's (D144 add. 4). A-mass's tie and D-hors are
   accepted on 581's readings, in every regime their sites can be in (K-1).
2. **Independent control: RELEVANT.** Answers: the byte-loop oracle (`proof_run`'s BIND, PROOF,
   EXACT, COMPL, with S2's sentinel buffers) and job 581's python `re` differential, neither
   sharing source with the family. Movers: emit_sweep's pcrec-side artifact diff, never the kit's
   own `moved`. W3's comparator (normalized old fields vs stated spans) and W5's comparator
   (transcription vs pcrec's live model) are MIGRATION controls: they share a model by design
   and prove identity only, which §3 states.
3. **What moves when data is regenerated: RELEVANT.** A-mass and A-model read the analysis
   object's byte-rate and the measure set. Regenerating either can move a stop, which moves
   bytes: a pcrec abi event (integration.md §21.3). At W5b the CONSULTED stamp (`<PREFIX>_FINDINGS`,
   D167 add. 2) moves from pcrec's ask to the kit's `consulted`; its VALUE must not change, and
   W5b's identity gate reads the stamp line too.

---

## 9. Open questions for Frank (plain words, each with a leaning)

- **Q1. Should a span's start be one offset, or a range?** Today every site's span starts at a
  fixed distance from the candidate. The K82 handoff's fused gate (R-18) would want "the second
  span starts 3 to 7 bytes after the first". *Leaning:* one offset now; a start range is added
  the day that multi-span site is built (D77). Nothing today needs it.
- **Q2. One rule for picking the stop, or two?** The kit's copy of pcrec's planner picks the stop
  for native sites; the "rarest position" rule picked it for R-27's measured REPORT cells.
  *Leaning:* one rule. At the planner move (W5) log both on the eight cells; if they agree within
  noise, keep only the planner.
- **Q3. Does a REPORT site still name its consumer at all?** Once "report" just means "verify
  everything", the only thing left is a label saying pcrec's finisher reads the answer, and no
  kit table reads it. *Leaning:* keep the label as one value of the consumer category (so every
  site states its consumer), with no special handling anywhere.
- **Q4. hex8-bounded: wait for the Horspool-over-sets measurement, or decide now?** No measured
  form clears that cell. *Leaning:* measure the Horspool row in job 581; if it misses, ask you to
  waive that one cell for B1 rather than build a hex-specific row.
- **Q5. Fold `end_back` into the spans?** "The candidate needs one more byte after it" is exactly
  a full-set core position at +1, so the bounded PF rows' range field could become a span.
  *Leaning:* not now: it moves the bounded rows' text for a pure simplification; filed, and
  worth doing only together with another change to those rows.

---

## 10. Charter vs committed

| charter item (brief) | where | state |
|---|---|---|
| 1. the minimal facts, each with its unstated handling | §1.1 | done |
| 1. the core rule proven over every current site (known.c, emit_dfa.c, span_facts, MLINE FAILS, R-26 ctx items) and every row's use of ctx/absent/consumable/need/site_kind/consumer/plan_hint/plan_pos/table_ref | §1.2 (sites), §1.4 + §4 (row readers) | done, by grep at `3da6aa04c` |
| 1. where `need`, `consumable`, R-26.7 go | §1.4 | done: need → verify (span grain); consumable → verify; R-26.7 dissolves |
| 2. one row family as declared tables: stop pick, stop find (walk; REGIME slot unfilled), verify chain under the edge rule with no read outside [0, n), generic floor | §2.2-§2.7 | done |
| 2. which rows fold, stay, retire | §2.7 | done |
| 3. stop choice to the kit, first row = prefix_k's pick, comparator, `plan_hint` retires | §3 | done |
| 4. what retires, readers by grep | §4 | done (re-grep owed at each build commit) |
| 5. staging at zero movers; byte-moving steps as pcrec abi events; `MF_SITE_ABI` events; pcrec vs kit side | §5 | done |
| 6. R-27 as first consumer; M1-M7, S1-S8, T1-T9 answered; hex8 and U6 | §6 | done |
| 7. the pcrec producer (D168, ctx_span); UL-8 dissolves | §7 | done (the source switch does not dissolve, stated) |
| 8. open questions in plain words with leanings | §9 | done (5) |
| standing questions | §8 | done |
| no edits under memfn/src, src/, cli/, lib/, tests/; no make; no timing | — | held |
| a row in docs/design/memfn/CLAUDE.md | that file | done |
| addendum (kit manager): W3's restatement includes Z2's cover statement; sabotage re-aims DERIVED by rule + grep | §5.1 | done (rule stated; its output is each build step's) |
| claims needing a run | §5 every "MEASURED" zero; §2.4 C-run's grouping = today's (W3's identity gate); §3 the comparator population floor | OWED to the build lanes |
