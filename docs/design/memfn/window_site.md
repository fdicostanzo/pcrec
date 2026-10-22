# window_site — the UNIFIED WINDOW SITE: spans with a required core, one row family (design, rev 2)

Rev 2: lane uwin2 (kit manager's lane), 2026-10-21, branch `lane/memfn-uwin2` = rev 1 + the kit branch
`lane/memfn-b4scope` (B4′ landed in it: `MF_SITE_ABI` 19, the routed bit gone, R7/R5/R0 withdrawn; tip
`cc6eec191`). DESIGN ONLY, NO BUILD GO: no `memfn/src`/`src/`/`cli/`/`lib/`/`tests/` edit, no make, no timing.

Rev 2 applies the D6 panel `docs/dev/reviews/2026-10-21-r2-memfn-window-site.md` (P1-P7, G1-G10,
F1-F7, Q1-Q5) and the kit manager's rulings of 2026-10-21, which SUPERSEDE the panel's P2 and Q2:
- **the stop choice** (Frank: "if we are simply picking the least frequent byte, why do we need pcrec?
  doesn't pcrec send a table of frequencies?"): pcrec sends spans and frequencies, NO plan hint; the
  kit's tables carry pcrec's planner's rules as declared rows over those frequencies (§3);
- **the stamp** `<PREFIX>_DFA_PREFILTER_OFFSETS` reads the kit's reply (§3.4);
- **the failure-shift / Horspool row** is a declared row whose use condition reads the frequencies;
  its threshold is OWED to job 581; hex8 is the kit's call and B1 does not wait on it (§6);
- **staging after B4′**: S1 (kit family + R-27 preview), S2 (the restatement, one request), S3 = B1 (§5);
- **the S2 request text** (Appendix A).

Changed text is marked `[rev2 <id>]`; Appendix B places every finding by id.

---

## 0. One screen

**pcrec states facts; the kit decides everything else.** A window site states:

| fact | per | meaning | unstated |
|---|---|---|---|
| start | span | signed offset of the span's first position from the candidate | refused |
| sets | span position | the byte set the position must hold (all 256 = any byte; empty is legal, §1.2) | refused |
| core | span | the contiguous positions that must lie INSIDE the subject; may be empty | refused (empty is a value) |
| verify | span | YES: every yielded candidate satisfies the span. NO: a true filter the kit may use or skip | refused |
| table offer | span position | pcrec already emits a membership table for this set, under this name | no offer |
| floor | site | SUBJECT, or pcrec's expression F (reads below F are pcrec's EDGE) | refused where a span reaches below the candidate |
| frame | site | form/op/handoff/empty/use/body/decl_point/hooks as today, plus the span range `span_lo`/`span_hi` `[rev2 F7b]` | as today |
| alternatives | site | 1 or 2 span lists, EACH a sound candidate definition on its own; the kit answers which it serves `[rev2 kit-mgr 1]` | one |
| frequencies | art | the byte-rate pcrec already declares (`pcrec_find_set_ppm`'s source: the analysis object on `mf_art_begin`) and the measure set | as today (E-1) |

**The absence rule.** A position off the subject PASSES outside the core and FAILS inside it. No
per-position bit is needed: absence happens only at the edges (§1.2).

**One row family (§2):** A STOP (least cost under the planner's measured model), B FIND FORM (by
the same measured costs; the finder's FIND slot), C VERIFY PLAN (all verify-YES positions; on native
sites, the model's greedy subset of the verify-NO ones), ADOPT (does the skip pay at all: the 2x bar),
D RESUME (step 1; the Horspool row where its frequency predictor says so), E FRAME. Floor: `generic`.

**No plan hint, no interim (§3).** The planner's rules (`src/opt/prefix_k.c`) move into the kit's
tables as declared rows reading pcrec's frequencies, with its constants as DATA in a declared table
with provenance. On native sites they reproduce today's choices, so the restatement is ZERO movers,
proven by emit_sweep. This IS M5 + M5′ (integration.md §14.9 items 2-3, Q40 RULED YES) folded into
the restatement; there is no "honour pcrec's pick" step and no later switch event.

**Staging (§5):** **S1** (kit) the family + R-27's preview, developed against the NEW statement,
landing together with **S2** (pcrec + kit, one request): pcrec states spans and frequencies only, the
old fields and `plan_hint` retire, Z2's cover site is restated, ONE `MF_SITE_ABI` event ("next at
landing"), zero movers. **S3 = B1**: REPORT routed by default, the one byte-moving step, a pcrec abi
event with its deny row in the same commit.

---

## 1. The facts

### 1.1 The set, what each replaces, and the producer obligations

A SPAN is a run of consecutive positions `start .. start+len-1` relative to the candidate `c`, one
set per position; a gap is an all-256 position. Candidates are the `c` where every span of the
chosen alternative holds. Spans may overlap; positions at one offset are tested as their
intersection (§2.3).

| fact | replaces | why it is enough |
|---|---|---|
| start + sets | `mf_term` (SET/RUN/mask), `ctx[]`, the context stop's `pred`, W0-W2 | a masked RUN is a product of per-position sets; every FIND site states "the window is the candidate" today (`pcrec_memfn_window_is_candidate`) |
| core | `absent`, `span_class` BOUNDED/CONTEXT, §14.5 rule 3, Q-R7-1's reads-below range, `end_back` `[rev2 F3/Q5]` | §1.2; `end_back` 1 is a full-set core position at the window's end |
| verify | per-term/per-predicate `need`, `consumable`, `consumable_len`, REPORT's "every term REQUIRED" | §1.4 |
| table offer | `table_ref` + `table_name` | the same capability per position; no row requires it |
| floor | `read_floor` + the `floor` hook | §1.3 |
| alternatives | `plan_hint`'s implicit "pcrec chose the skip" (`pf_ofs_applies` reading `ofsk.nsel`) | §3.2: the baseline scan and the offset-k skip are two DIFFERENT sound conjunctions (`\b\.[0-9]{4}Z`: `.` is outside k0), so neither can be folded into the other |
| frequencies | `plan_hint`, `plan_pos`, `rank_n/pos/ppm` | the kit derives every rank and pick from the byte-rate it already receives |

**Spans are finite; the limits are pcrec's** `[rev2 P7]`. The contract states no span count or reach
cap. One kit-side bound stays, because `mf_class.proven[]` is a fixed array `[rev2 F1]`: the PROOF
range `[MF_PROOF_LO, MF_MAX_FWD)`. A position outside it is still tested and carries no proof bit; a
consumer that needs its proof (the cover site) declines on pcrec's side, as C6/C11 decline today.
Trigger to grow it: a longer lookaround becomes a context source (§7), an `MF_CLASS_V` layout event.

**Producer obligations** (asserted where pcrec builds the site):
- a verify-NO span's core is a SUBSET of the positions where absence truly fails `[rev2 F6]` (a wider
  core would drop true candidates);
- each alternative is sound on its own;
- a SATISFIES item wider than one byte whose meaning is whole-item is not a span; the producer
  declines it (§1.2).

Every fact has an UNSTATED handling; exactness (EXACT/SUPERSET) is not a fact (R-26.7 dissolves: a
SUPERSET item is sent only as verify NO, a filter that can never be read as a proof).

### 1.2 The core rule

At candidate `c`, a span holds iff for every position `d`: `c+d` inside `[0, n)` → `s[c+d]` in the
set; `c+d` outside → `d` lies outside the core. Any per-position absent assignment equals one
contiguous core (the convex hull of the FAILS positions: a position between two core positions can
never be off the subject alone). Width-1 SATISFIES items read the same whole-item and per-position;
the facts critic PROBED-AND-HELD both, the cover mapping (all-0xff FAILS item included), MLINE `{-1:\n}`
keeping `c = n` reachable, and `\z` as an empty set outside the core.

**An empty set** inside a core never holds (the site yields nothing: floor row). Outside the core
it is LIVE `[rev2 F7d]`: it holds exactly when the position is off the subject (`\z`: `c+k = n`).

| site (builder, at `cc6eec191`) | spans | core | verify |
|---|---|---|---|
| PF FIND, DFA scan / HYB_PF (`find_site`, `emit_dfa.c`) | `{0: k0}` | `[0]`; bounded: `[0, 1]` with `{1: any}` `[rev2 F3]` | YES |
| VM hat seek | `{0: S}` | `[0]` | YES |
| MLINE `(?m)^` (`mline_find_of`) | `{-1: \n}` | `[-1]` | YES; floor = expression `start` |
| offset-skip (`ofs_pred_of`) | alternative 1: `{0: k0}` (the baseline); alternative 2: R = the run (if any), K = `{0: F0}` (the walk's frontier, role B) and every walked k-set offset | alt 2: R all, K all | R YES, F0 YES (the "offset 0 always verified" rule), other K NO |
| pre-check FUNC parts | ONE span per part `[rev2 F7a]` | all | as the part's need |
| cover / REPORT (Z2: `known.c`, `emit_cover`) | span 0 `{0..k-1: S_d}`; one span per context item | `[0, k)`; an item: its position if FAILS, empty if SATISFIES | all YES |

Out of the family, unchanged: PRESENCE (`pspans`, ALL_PRESENT: no position relative to a candidate),
SKIP/ADVANCE, VMRUN, MISMATCH.

### 1.3 The floor and the edge

- **SUBJECT**: reads lie in `[0, n)`; below 0 the core rule decides. REPORT states it.
- **an expression F** (`F <= lo`): reads lie in `[F, n)`; a candidate needing a read in `[0, F)` is
  NOT COVERED: the kit does not yield it and pcrec's EDGE attempt owns it (today's MLINE).

**The guard is three-way** `[rev2 F2]`, per non-core position: off the subject (`< 0` or `>= n`)
→ passes; inside `[0, F)` → the edge's (the candidate is not covered); else → membership. Rev 1's
two-way guard read `\b`'s `{-1}` position below F as "passes" and yielded a candidate the edge owns.
Core positions get ONE hoisted bound per candidate: every core position inside `[F, n)` (`[0, n)` under
SUBJECT).

### 1.4 `need`, `consumable`, REPORT

- `need` becomes the span's verify (REQUIRED = YES, OPTIONAL = NO). The kit never ADDS a constraint.
- R-25 survives as the proof rule: `proven[d]` states only what the rendered plan TESTS. Restated
  `[rev2 F5]`: `proven[d]` = "for every yielded `c` with `c+d` inside the subject, `s[c+d]` is in the
  set"; it says nothing about off-subject positions, which the core rule governs. The core's own
  control is the sentinel buffers (§8) and the plant "absent-FAILS candidate yielded".
- `consumable`/`consumable_len`: no reader; retire. `exact_len`/`prefix_stated`: pcrec-internal (`MkLang`).
- **REPORT is the window site with every span verify YES. Nothing else** `[rev2 P3/Q3]`: no consumer
  category, no label. The VM hat's seek (rev 1's only reader, D1 vs D1w) is a FRAME fact: the frame
  says the site is the VM attempt's seek, and Table B reads it.

---

## 2. One row family

```
  ADOPT  which alternative (native offset-skip sites: baseline vs skip, the 2x bar)
  A      the STOP: one core position d* (least model cost)
  B      FIND the next p in [max(c + d*, F, 0), n) with s[p] in set(d*); empty if the start >= n   [rev2 F4]
  C      test the VERIFY PLAN at c (one hoisted core bound, three-way guards outside it)
  D      on failure RESUME at c + shift
  E      render in the site's FRAME
  floor: generic (a byte loop over the chosen alternative's spans under the core rule)
```

Every table is a `kit_table` on `kit_walk` (compose.c): first match, a contract per row, a deny where it
moves bytes, a basis; every cost row reads ONE declared cost table (§3.3).

### 2.1 Table A — the stop

| row | holds when | stop | basis |
|---|---|---|---|
| A-cost | always | the core position of least model cost: `scan_cost(B's form) + mass · verify_cost(plan) + mass · plan_rate · C_ENTER` (`prefix_k.c` `model_cost`); on native skip alternatives the stop is a singleton at `k > 0` (the "scan must move" rule, measured: §3.2) | pcrec's planner, its constants as data (§3.3) |
| (none) | no core position | the floor row | — |

A stop lies in a core and may come from a verify-NO span. Ties: ONE stated rule `[rev2 P5]`,
"the lower offset" (prefix_k's `cost < best` over ascending offsets), labelled UNMEASURED DEFAULT
until job 581's PRR arm reads. **Zero-mover caveat:** run-pinned sites take today's stop from the
rarity rank, "ties to the higher offset" (`mf_pred.rank_*`). Whether a model tie ever falls inside a
run on the corpus is a COUNT S1 owes (§5, S1 go reading); if nonzero, the tie rule is a declared
column per verify kind (run stretch: higher; otherwise: lower), both UNMEASURED DEFAULT, never a
special-case branch.

### 2.2 Table B — how the stop is found

Table B IS the finder's FIND slot (`fd_rows`, finder.c), asked "the next byte in set(d*) at offset d*".

| row | holds when | form | basis |
|---|---|---|---|
| D1c | the stop lies below the candidate | libc back search | UNMEASURED DEFAULT (today's) |
| PAIR | the stop's facts: a two-member set inside a verify-YES literal stretch `[rev2 P6]` | two `memchr` streams | today's; a frame that cannot host it declines in E |
| (SIMD) | `-fmemfn-simd`: vrun's PREFIX rows | today's | inert at OFF |
| D1 | one member, the frame is not the VM seek | `memchr` (C_MEMCHR) | MEASURED (§3.3) |
| D1w | one member, the frame IS the VM seek | the table walk | UNMEASURED DEFAULT (today's) |
| R7w | every other set | the WALK (C_BITMAP; Frank 2026-10-21, walk_vs_v1_record.md) | MEASURED (B4′) |

The REGIME slot of rev 1 is gone `[rev2 P5]`: [MEMFN-REGIME] adds its row when it is built. D2 and
RPT retire.

### 2.3 Table C — the verify plan

The plan is ONE object (positions in order, each with its test): the renderer walks it, `proven[]`
is computed from it, a trace build asserts rendered = plan. C is a PLAN BUILDER with its real choice
rows `[rev2 P4]`; the text shape (one `&&` chain or branches) is a measured property of the E rows,
not of C.

| step | row | rule |
|---|---|---|
| 1 merge | C-meet | positions at one offset, across spans, are ONE position with the intersection set, BEFORE grouping `[rev2 F7c]`; an empty intersection inside a core → floor row |
| 2 select | C-yes | every verify-YES position |
|  | C-model | on a native skip alternative: plus the verify-NO positions the planner's greedy pass picks (ascending mass, kept while the model cost falls; at most `PCREC_OFSK_MAX_SET - 1`) (§3.2) |
|  | C-none | otherwise no verify-NO position |
| 3 drop | C-stop | minus the stop's own position when B's set equals it, EXCEPT inside a run stretch: a stop inside a run keeps the stretch whole `[rev2 G2]` (ofsskip.c's one run compare); witness: an in-run stop reached, with a floor |
| 4 group | C-run | a maximal stretch of consecutive one-member or cube positions inside one span is one run compare (runcmp's rows) |
| 5 test | C-table / C-own | an offered table (pcrec's name), else the kit's own `set_test` |
| 6 order | C-asc | ascending offset (today's) |

### 2.4 ADOPT — does the skip pay

| row | holds when | answer |
|---|---|---|
| ADOPT-skip | the site states two alternatives, and the skip alternative's best plan costs less than HALF the baseline's (`best · 2 < base`, prefix_k's MATERIAL 2/1) | the skip alternative |
| ADOPT-one | otherwise | the first (baseline) alternative |

This is integration.md §14.9 item 3 / Q40, RULED YES: the kit decides adoption. pcrec keeps its
semantic row (`offset-set`, applies when a walked set beyond offset 0 exists and its deny
`-fno-offset-skip` is not set); when it applies, pcrec states both alternatives; denied, only the
baseline. The deny keeps its identity `[rev2 G3]`.

### 2.5 Table D — the resume

| row | holds when | resume | basis |
|---|---|---|---|
| D-hors | a declared USE CONDITION over the frequencies (below) | Horspool over the TESTED sets: shift `sh[b]` = least `t` with `b` in the tested set at `last - t`, else the window length `[rev2 F7e]` | job 581 |
| D-one | always | `c + 1` | the floor (today's) |

**D-hors's use condition** reads only masses (the byte-rate summed per set, presence.c's `set_mass`):
- predicted false-start survival = `sum over j >= 1 of prod_{i<=j} mass(test_i)` over the plan's tests;
- the candidate rate = the stop's mass;
- the expected advance `sum_b rate[b] · sh[b]`.

Job 581 (`581-kit-r27-follow`, lane r27b) labels each cell WIN/LOSE for HRS and finds the best
threshold rule per predictor against the no-rule baseline. **State at writing: 581 is PENDING in the
queue; its table does not exist.** So the row is declared with its three predictors and its threshold
**OWED to 581**; it is not built until the table names a rule that beats the baseline. If none does,
D-hors is not built and hex8 stays a named loss (§6).
D-shift (580's shift, cost year4 12-48%) is FILED with its trigger, not in the table.

### 2.6 Table E — the frame

| row | holds when | text |
|---|---|---|
| E-func | FUNC/RETURN, miss `n`, no expression floor | today's `static inline size_t` (D155 seam, PREFIX slot) |
| E-stmt | STMT/ASSIGN or ON_MISS | today's PF block (guard, post-test, `moved` hook, `decl_point`) |
| E-generic | anything else | the floor row |

A REPORT site is STMT/ASSIGN: E-stmt, no re-description (the r1 panel's M1).

### 2.7 What folds where

| row today | fate |
|---|---|
| `pf_memchr`, `pf_memchr_bounded`, `pf_walk`, `pf_walk_bounded`, `pf_memchr_back` | FOLD: A + B (D1/R7w/D1w/D1c) + C (empty plan; bounded = a full-set core position) + E-stmt |
| `ofsskip` (`fn-memchr`, `fn-pair`, vrun PREFIX) | FOLD: ADOPT + A + B + C-model + E-func |
| `precheck` | STAY (ALL_PRESENT); its FUNC parts render through the family |
| `runcmp`, `mismatch_inplace`, `generic` | STAY (C-run's compare; MISMATCH; the floor) |
| RPT, `kit_report_exact`, `SF_PROOF_EXACT`, `FF_PROOF`, D2 | RETIRE |

**Deny identities and form names are preserved** `[rev2 G3]`: `fd-d1` still denies the C library on a
one-member stop outside the VM seek (→ D1w), `fd-pres-*`/`pres-set-lead` are untouched, `vrun-*` keep
their names and effects; `vrun-kb` keeps its effect and reads the kit's own ranking from the
frequencies instead of `rank_*`, a wording change in `registry.md §6¶8a` (D80) in S2's commit. Every
`_MEMFN_FORMS` form name a folded row emitted is kept as that path's form name.

---

## 3. The stop choice is the kit's, from pcrec's frequencies

### 3.1 Why there is no plan hint

pcrec's planner (`prefix_k.c`) reads two things: the pattern's sets (which pcrec states as spans) and
the byte-rate (which pcrec already declares on the art). The kit has both, so pcrec has nothing left
to say about the plan. Sending a pick would be sending a method (D157). The kit's tables therefore
carry the planner's RULES as declared rows (§2.1, §2.3 C-model, §2.4), each reading the same
frequencies pcrec's planner reads today.

### 3.2 The rules, as rows

| prefix_k rule | row | measured basis (prefix_k.c) |
|---|---|---|
| the cost model `model_cost` and `verify_cost` (with the mispredict term) | A-cost, C-model | §3.3 |
| greedy verify selection, exact because each verify multiplies the entry rate independently | C-model | derived (the code's own argument) |
| offset 0 always verified with the WALK's set F0 (role B), never k0 | the skip alternative's F0 span is verify YES (§1.2) | MISCOMPILE-1, S188 |
| the scan must MOVE off offset 0, and a moved scan is a singleton | A-cost on the skip alternative | MEASURED: uuid 4.5x, iso-ts 4.8x, stack-frame 7.2x, needleXYZW 17.1x moved; bignum 0.96-1.02x stayed (offset_k_skip.md §7.3) |
| adopt only at 2x | ADOPT-skip | §4.5's argument + the measured spread (ipv4's 1.5-1.6x inside the error bars) |
| the baseline is k0's cost (C_MEMCHR if one member, else C_BITMAP) | ADOPT's `base` | as C_MEMCHR/C_BITMAP |

On REPORT sites "verify everything" is fixed, so only A-cost and B apply (C-model and ADOPT have
nothing to choose).

### 3.3 The constants: data, with provenance, no new tuning

**Correction to the panel (P2):** the panel called the constants "unmeasured". `prefix_k.c` documents
them as MEASURED:
- C_MEMCHR = 0.055 cycles/byte (opt3_dfa_scan_measurement.md §4, CONTROL 1);
- C_BITMAP = 1.16 cycles/byte (same table);
- C_ENTER = 10.7 cycles/byte × the ~2 bytes a false start survives, its sensitivity swept over 1,352
  patterns (offset_k_skip.md §4.3);
- C_MISPRED from a measured before/after (offset_k_skip.md §7.3);
- the 2x bar from §4.5's argument.

Nuance: C_VERIFY (2.5 cycles/candidate) has no cited number beyond the header's claim; the table says so.

They move as DATA: one declared kit table (an X-macro beside `options.def`, e.g. `plan_cost.def`:
name, value, unit, provenance cite, box), read by every cost row; `prefix_k.c`'s values verbatim, no
re-measurement, no new constant. Re-measuring any of them is a byte-moving kit event (integration.md
§21.3): its own deny, pcrec abi event and G1 at both layers.

### 3.4 The stamps read the kit's reply `[rev2 G4]`

Once the kit picks, `<PREFIX>_DFA_PREFILTER_OFFSETS` (the offset list, `*` on the scan) and
`<PREFIX>_DFA_PREFILTER`'s `offset-set` value are written from the kit's reply (the chosen
alternative, the stop, the plan positions), never from a pcrec-side recomputation. Today's streamed
writer (`dfa_prefilter_offsets`, `emit_dfa.c`) becomes a read of the reply; the reply must exist
before the stamp line is written (the site is asked first, as `mf_ask` already allows). The spec hunk,
in S2's commit: `match_api.md §6.3.1¶5a` (the stamp names the selection the artifact RUNS, now the
kit's), `tuning.md §2.14¶3` and `§2.30¶2` (who chooses the offsets). The identity gate reads both
stamp lines; their VALUES must not move at S2. `<PREFIX>_FINDINGS`'s consulted line likewise must not
move.

### 3.5 What S2 does NOT fold

integration.md §R4.3.5 also lists "the reseed becomes unconditional" for M5′. That moves bytes (the
reseed is keyed on adoption today), so it is NOT in S2: after S2 the reseed stays keyed exactly as
today, on the adoption answer, now read from the kit's reply. Making it unconditional is a separate
measured event, filed if anyone wants it (D77).

---

## 4. What retires, with its readers (re-grepped at `cc6eec191` `[rev2 G10]`; re-grep at the build commit)

All rows retire at S2 unless marked.

| retires | readers |
|---|---|
| `ctx`/`nctx`, `MF_MAX_CTX`, `MF_MAX_AHEAD` | `memfn.h`, `memfn/include/CLAUDE.md`, compose.c, gate.c, generic.c, fields.def, `src/gen/known.c`, `src/ir/dfa.c`, `src/core/internal.h`, `tests/memfn/proof_check.c` |
| `absent`, `consumable`, `consumable_len`, `mf_absent` | `memfn.h`, kit.h, compose.c, gate.c, generic.c, fields.def, `memfn/tests/g2/{g2_gen,g2_simd_gen}.c`, `known.c`, `memfn_sites.{c,h}`, `tests/memfn/{arm_fixtures.c,proof_run.c,proof_check.c}` |
| `prefix_stated`, `exact_len` (contract side; `MkLang` keeps them) | `memfn.h`, kit.h, compose.c, gate.c, fields.def, formhash.c, g2 generators, `known.{c,h}`, `memfn_sites.{c,h}`, `tests/memfn/{proven_check,arm_fixtures,proof_check}.c` |
| `span_class` BOUNDED/CONTEXT (PRESENCE stays) | `memfn.h`, compose.c, gate.c, generic.c, formhash.c, g2 generators, `known.c`, `memfn_sites.c`, `emit_dfa.c`, `tests/memfn/{proven_check.c,arm_fixtures.c,run_proof.sh,proof_check.c}` |
| `read_floor` (merged into floor) | `memfn.h`, kit.h, compose.c, gate.c, fields.def, g2 generators, `known.{c,h}`, `memfn_sites.{c,h}`, `tests/memfn/{arm_fixtures,proof_check}.c` |
| W0-W2 (`window_stated`, `move_back`, `overshoot`), `end_back` | `memfn.h`, kit.h, compose.c, finder.c, gate.c, fields.def, formhash.c, g2 generators, `memfn_sites.{c,h}`, `tests/memfn/{run_arm_pins.sh,proven_check.c,arm_fixtures.c,proof_check.c}`, `tests/codegen/run_fallback_table.sh` |
| per-term/per-predicate `need` (presence spans keep theirs) | `memfn.h`, every builder (`emit_dfa.c`, `emit_vm.c`, `memfn_sites.c`, `known.c`), compose.c, finder.c, gate.c |
| `site_kind` REPORT's meaning, `consumer` | `memfn.h`, kit.h, compose.c, finder.c (incl. R7w's proof-site condition, B4′), gate.c, fields.def, g2_gen.c, `known.{c,h}`, `memfn_sites.{c,h}`, `emit_dfa.c`, `src/parse/rxt_source.c` (check), `tests/memfn/{site_census.py,site_manifest.tsv,site_manifest_check.py,finder_check.py,proven_check.c,arm_fixtures.c,proof_check.c}`, S1091, S1102 |
| RPT, `kit_report_exact`, `SF_PROOF_EXACT`, `FF_PROOF` | finder.c, kit.h, compose.c, `memfn/src/CLAUDE.md`, `tests/memfn/{rows.tsv,row_floors.tsv,arm_fixtures.c,run_proof.sh,finder_check.py,run_rows.sh,proof_check.c}`, S1255, S1256 |
| `plan_hint`, `plan_pos`, `rank_n/pos/ppm`, `MF_RANK_MAX` | `memfn.h`, compose.c, formhash.c, ofsskip.c, precheck.c, vrun.c, `memfn/tests/{run_g2_simd.py,g2/*}`, `known.c`, `memfn_sites.c`, `emit_dfa.c` (`ofs_pred_of`, `ofs_pred_rank`), `tests/memfn/{run_rank.sh,rank_check.py,proven_check.c,arm_fixtures.c,proof_check.c}`; the `REQ_RUN @idx` spec text and the `[OPT-REQPOS]` note (§14.9 item 1's re-spec, a `findings.md` hunk) |
| pcrec's selection (`pcrec_prefix_ksets`' pick; the walk `kset_walk` STAYS, it is a fact) | `src/opt/prefix_k.c`, `src/core/internal.h`, `emit_dfa.c` (`ofsk`, `pf_ofs_applies`), `tests/codegen/{run_offset_skip.sh,run_form_census.sh}`, S187, S188 (S188's plant stays pcrec's: F0 is a stated set) |
| ofsskip/pffind as arms | compose.c `arms[]`, precheck.c, `tests/memfn/rows.tsv`, finder.c's arm map |
| `mf_preview("R-26.6")` | stays until S3; then retires with RPT: `memfn_sites.c`, `src/core/internal.h`, S1251-S1254 |

---

## 5. Staging

### 5.1 The order and the S1/S2 decision `[rev2 P1, G9, G10]`

Order: B4′ (landed in this branch) → S1+S2 as ONE landing → S3.

**S1 and S2 land together; no adapter is built.** S1 built alone would have to read today's fields
(terms, `need`, `ctx[]`, `plan_hint`) to render anything, which is exactly the adapter P1 rejected,
and its zero-mover proof would compare the family against a translation sharing its model. Instead the
kit lane develops the family against the NEW statement on its own branch (G2 generates span sites
directly; fixtures state spans), while the pcrec builder hunk is written to the same request; the
manager merges both as one commit pair at one `MF_SITE_ABI` event. The only places today's fields
remain are the sites outside the family (PRESENCE, SKIP/ADVANCE, VMRUN, MISMATCH), which S2 does not
touch: that is the "unavoidable" set, and it is not an adapter.

### 5.2 The steps

| | S1 (kit) | S2 (pcrec + kit, ONE request) | S3 = B1 (kit + pcrec, ONE commit) |
|---|---|---|---|
| content | the family (ADOPT, A-E, the cost table §3.3, C as plan builder, the three-way guard, the merged plan object); RPT and `kit_report_exact` replaced by the family's plan-derived proof; R-27 on the family in PREVIEW (`mf_preview`, harness lever only) | pcrec's builders state spans, alternatives and frequencies only (PF, MLINE, VM hat, OFS, pre-check FUNC parts, Z2's cover site §5.4); §4's rows retire; `plan_hint`/`rank_*` retire; pcrec's planner selection retires; stamps read the reply (§3.4) | REPORT routed by default: the cover site renders the family's text |
| owner | kit lane | main files the request; a pcrec lane writes the builder hunk; the kit lane the kit hunk; manager merges both | kit + pcrec |
| witness | G2 over a GENERATED span space against the scalar byte loop; `proof_run` (BIND/PROOF/EXACT/COMPL) with the sentinel buffers (r1 panel S2); the preview arts' answers (kitproof arm, 393 cells, X1) | emit_sweep on EVERY arm, byte-identical to the pre-S2 main (default, every deny arm, `--engine=vm`, both SIMD layers); stamp lines included; per-old-row REACH FLOORS (§5.3) read before and after; `REACH_ONLY=1` mech re-aim | the 650 harness (R-27.1), answer gate, G1 alpha at both layers vs the new deny |
| abi events | none (no default byte) | ONE `MF_SITE_ABI` event, "next at landing" `[rev2 G7]`; NO pcrec abi event (zero movers) | pcrec abi bump (readers by grep, D76/D94) in the same commit |
| spec hunks | none | `match_api.md §6.3.1¶5a`, `tuning.md §2.14¶3`, `§2.30¶2` (§3.4); `registry.md §6¶8a` (`vrun-kb`'s source, G3); `findings.md` (`REQ_RUN @idx` as pcrec's rarity fact) | the routed REPORT row's deny in `registry.md §6¶8a` (+ the section floor `§6¶8b`); the cover stamps where caller-visible |
| deny | none | none new; every existing deny keeps its identity (§2.7) | born here, as the step's alpha OFF arm |
| sabotage | kit-side ids on request: a plan claiming an untested offset; an absent-FAILS candidate yielded (F5); an absent-SATISFIES candidate dropped; an empty-intersection site not sent to the floor; a below-F read treated as passing (F2); an in-run stop splitting the stretch (G2) | §5.4's derived re-aims; ids on request (main's ledger next free after R-27's S1331) | the routed row denied but still rendering; RPT-free proof mismatch |
| go | the S1 go readings: G2 + proof_run green; the run-tie COUNT (§2.1) reported; the preview's model picks on the 8 R-27 cells listed against 580's mass picks (no clock) | zero movers MEASURED on every arm; every reach floor met before AND after; derived sabotage list run green | R-27.1 at BOTH layers: no `real`/`none` throughput or search_short cell slower beyond its floor, `dense` not slower than COV; zero answer changes; hex8's cells as §6 says |
| no-go | any G2/proof red | any mover, any floor missed, any stamp value moved | any non-hex8 cell slower beyond floor |

### 5.3 Reach floors per old row `[rev2 G5]`

Before S2, the trace build counts, per OLD row (`pf_memchr`, `pf_memchr_bounded`, `pf_walk`,
`pf_walk_bounded`, `pf_memchr_back`, `ofsskip` per form, pre-check FUNC parts, the cover site under the
lever), its sites over the emit_sweep corpus; after S2 the same population is counted on the family
PATH that replaces it (§2.7's map), and each path's count must be at least the old row's. The counter
is the kit's existing reach counter (`row_contracts.md`); the driver is `scripts/emit_sweep.py` with
the trace build. A path with zero reach is red (K35).

### 5.4 Z2's cover site, and the derived sabotage rule

S2 restates Z2's cover site (span 0 `[0, k)` YES; one span per context item; floor SUBJECT;
`exact_len` stays in `MkLang`; `pcrec_cover_proof_diff` unchanged in meaning; `mf_preview` until S3).
Its zero-mover witness is emit_sweep for the default build plus the lever's arts compared before and
after (`--harness=kit-proof`, the kitproof arm's 393 cells and X1), because the default build never
renders it.

**Sabotage re-aims are DERIVED.** In the step's commit, over every row in `tests/mech/sabotages/`:
1. candidates: rows whose `SAB_FILE` is in `git diff --name-only <base>..HEAD`;
2. anchor test: `VALIDATE_ONLY=1` over the candidates; an unresolved `SAB_BEFORE` is re-aimed;
3. intent test: an anchor inside a changed hunk, or naming an identifier §4 retires, is re-aimed with
   its intent re-verified;
4. reach test: `REACH_ONLY=1` over the arms the step touches; a row that stopped reaching is re-aimed;
5. **suite test** `[rev2 G6]`: a row whose `SAB_SUITES` names a suite whose DETECTOR the step edits
   or retires gets a FULL run (its detection, not only its anchor);
6. the report prints the union and its count; a row retires only with the code it plants in, named
   with its successor plant.

Z2's cover rows are S1130-S1141, S1144, S1148 and S1149 (members, not the list). **There is no
S1257-S1290** on any branch `[rev2 G6]`; rev 1's range is withdrawn and main corrects D172's brief.

---

## 6. R-27 and hex8

Job 580: the window search with no shift (PRO) meets R-27.1 on 42 of 48 non-match cells. Under the
family PRO is A + B + C-yes + D-one + E-stmt; S1's preview renders it with A-cost's pick rather than
580's least-mass pick (the two coincide wherever B's form is the same for every candidate stop).

**hex8 is the kit's judgement call (Frank).** REPORT routing (S3) proceeds REGARDLESS of hex8. If
job 581 yields a D-hors rule that clears hex8's cells, D-hors ships in S1 (or a later kit event) as a
declared row. If no row clears them, S3 ships with hex8-bounded's cells named in its report as a
known, MEASURED loss (580/581's numbers). No hex-only row, no waiver step.

The r1 panel's R-27 findings keep rev 1's answers under the new names (M1 E-stmt; M3 the FIND slot;
M4/S3 core bound + three-way guard; M5 D-shift filed; S1 one plan object; S5 C-meet; T1 §2.1).

---

## 7. The pcrec producer (D168, `ctx_span.md`)

`MkLang`'s `S_d` are span 0's positions; each `MkCtx` item is one span (least to greatest offset, gaps
full-set; FAILS → core, width-1 SATISFIES → empty core; EXACT may be YES, SUPERSET only NO). A longer
lookbehind or lookahead is a longer span with no new field. What does NOT dissolve: the proof range
(§1.1, F1) and the SOURCE switch (the DFA machine reading sees one seed byte, so `(?<=ab)` needs the
facts-layer producer as THE context source, pcrec's own event with X1 as its control).

---

## 8. The three standing questions (`docs/design/CLAUDE.md`)

1. **Measurement regime: RELEVANT at S3 and at D-hors only.** S1 and S2 move no default byte: identity
   steps read by emit_sweep. S3 is read in R-27.1's regime (650 harness: match / search_short /
   throughput × real / none / dense; scalar layer; Linux, `taskset`-pinned; 581's absolute columns and
   A/A pair; G1 at both layers; SIMD verdict pcrec-bench's, D144 add. 4). The cost table's numbers
   were measured where `prefix_k.c` cites; moving them is its own event.
2. **Independent control: RELEVANT.** Answers: `proof_run`'s byte loop with sentinel buffers, 581's
   python `re` differential, G2's scalar byte loop over a generated span space; none shares source with
   the family. Movers: emit_sweep's pcrec-side artifact diff, never the kit's `moved`. S2's zero is
   read against the PRE-S2 main's artifacts, which were produced by pcrec's own planner: the planner and
   its kit transcription share a MODEL (rules and constants) but no code, so the diff proves the move,
   not that the model is right; correctness stays with the answer gates.
3. **What moves when data is regenerated: RELEVANT.** Every cost row reads the byte-rate and the
   cost table. Regenerating the byte-rate (the analysis object, the default prior) or re-measuring a
   constant can move a stop, a plan or an adoption: a pcrec abi event (integration.md §21.3) and the
   `DFA_PREFILTER*` stamps' values (D80). S2's identity gate reads the stamp lines.

---

## 9. Questions, as ruled

- **Q1 one offset or a range:** one offset (both critics); a range waits for K82's fused gate.
- **Q2 the stop rule:** SUPERSEDED by the kit manager's ruling: one set of rules, the planner's, in the
  kit, from pcrec's frequencies (§3). No interim, no switch event.
- **Q3 REPORT's label:** deleted (§1.4).
- **Q4 hex8:** the kit's call; S3 does not wait; a named loss if no row clears it (§6).
- **Q5 `end_back`:** folded now, as a full-set core position (§1.1).

One item for the panel that reviews rev 2, not for Frank: the ALTERNATIVES fact (§1.1). It is the
minimal fact that lets adoption move to the kit without a pick from pcrec; a reviewer should try to
fold it away (I could not: the two conjunctions differ, `\b\.[0-9]{4}Z`).

---

## Appendix A. The S2 request text (for main to file in `memfn/docs/requests.md`; facts only, D157)

> **R-NN (date, pcrec manager) — the window site stated as spans and frequencies; the plan and its
> adoption are the kit's**
>
> **Customer:** D172 (Frank, 2026-10-21: "pcrec states spans; the find-window and REPORT are the same
> request; choices are table-driven"), and integration.md §14.9 items 2-3 / Q40 (RULED YES: the kit
> decides adoption).
>
> **Facts pcrec will state, for every FIND site of the family (PF, PF bounded, MLINE, the VM hat seek,
> the offset-skip block, the pre-check's FUNC parts, Z2's cover site):**
>
> | fact | meaning |
> |---|---|
> | spans | per span: a signed start offset from the candidate, one byte set per position, a contiguous required core (possibly empty), and verify YES (every yielded candidate satisfies it) or NO (a true filter) |
> | table offers | per position, where pcrec already emits a membership table for that set, its name |
> | floor | SUBJECT, or an expression F; a candidate needing a read in `[0, F)` is pcrec's edge |
> | frame | the site's form/op/handoff/empty/use/body/decl_point/hooks and its span range; whether it is the VM attempt's seek |
> | alternatives | one or two span lists, each a sound candidate definition alone (the offset-skip block states its baseline scan and its walked k-sets) |
> | frequencies | the analysis object's byte-rate and the measure set, as already passed on `mf_art_begin` |
>
> pcrec stops stating `plan_hint`, `plan_pos`, `rank_*`, `ctx[]`, `absent`, `consumable`,
> `consumable_len`, `exact_len`, `prefix_stated`, `span_class` BOUNDED/CONTEXT, `read_floor`, W0-W2,
> `end_back`, per-term `need`, `consumer` and REPORT's kind meaning.
>
> **What pcrec needs back:** the C text for the site; which alternative it serves; the positions it
> tests and the one it searches for (pcrec writes `<PREFIX>_DFA_PREFILTER`/`_OFFSETS` from them); the
> proof class as today.
>
> **Landing bar:** zero artifact movers on every emit_sweep arm, stamp lines included; per-old-row
> reach floors met on the replacing paths; every existing deny keeps its identity; one `MF_SITE_ABI`
> event, numbered at landing; the derived sabotage list (window_site.md §5.4) green.
>
> **Not asked:** any method. How the kit picks, plans, finds or resumes is the kit's (D157).
>
> **Sequencing:** after B4′; the kit's family and R-27's preview land with this step, never before it
> on old fields; B1 follows as its own byte-moving event.
>
> **Sabotage ids:** kit-side on request (main ledger next free after S1331). Correction to D172's
> brief: the Z2 cover rows that exist are S1130-S1141, S1144, S1148 and S1149; S1257-S1290 does not
> exist.

---

## Appendix B. Where each finding landed

| id | landed | | id | landed |
|---|---|---|---|---|
| P1 | §5.1 (no adapter, one landing) | | G6 | §5.4 step 5; range corrected |
| P2 | superseded by kit-mgr ruling 1: §3 | | G7 | §5.2 "next at landing" |
| P3 | §1.4 (label deleted; VM seek a frame fact) | | G8 | §5.2 (one request, Appendix A) |
| P4 | §2.3 (plan builder; text shape in E) | | G9 | superseded by P1 |
| P5 | §2.1 tie, §2.2 REGIME gone, §2.5 D-shift filed | | G10 | §5.1 order; §4 re-grepped at `cc6eec191` |
| P6 | §2.2 PAIR on the stop's facts | | F1 | §1.1 proof range with its trigger |
| P7 | §1.1 (spans finite, limits pcrec's) | | F2 | §1.3 three-way guard |
| G1 | dissolved (no transcription comparator; C-model reproduces the subset) | | F3 | §1.1/§1.2 `end_back` as a core position |
| G2 | §2.3 C-stop | | F4 | §2 B's clamped start |
| G3 | §2.7 deny identities; §5.2 spec hunk | | F5 | §1.4 restated; plant in §5.2 |
| G4 | §3.4 | | F6 | §1.1 producer obligation |
| G5 | §5.3 | | F7a-e | §1.2 (a, d), §0 frame (b), §2.3 (c), §2.5 (e) |
| Q1-Q5 | §9 | | U1-U7 | unchanged as filed (panel §3) |
| kit-mgr 1 | §3, §2.1, §2.4 | | kit-mgr 3 | §2.5, §6 |
| kit-mgr 2 | §3.4 | | kit-mgr 4, 5 | §5, Appendix A |

## Appendix C. Charter vs committed

| charter item (brief) | where | state |
|---|---|---|
| apply every ruling of the r2 review | Appendix B | done |
| 1. no plan_hint; the planner's rules as rows over frequencies; adoption the kit's; zero movers; constants as data; "unmeasured" corrected | §3, §2.1, §2.4 | done (zero movers OWED to S2's emit_sweep; the run-tie count OWED to S1) |
| 2. the OFFSETS stamp reads the reply, spec hunk | §3.4, §5.2 | done |
| 3. Horspool row with predictors; 581 folded or threshold OWED; hex8 the kit's call | §2.5, §6 | 581 PENDING: threshold OWED |
| 4. S1/S2/S3 with content, owner, witness, abi, spec, sabotage, go/no-go; S1+S2 together decided | §5 | done |
| 5. the S2 request text with the range correction | Appendix A | done |
| rev 1's length or shorter; one-screen lead; CLAUDE.md row | whole note; `docs/design/memfn/CLAUDE.md` | done |
| design only: no src/tests edits, no make, no timing | — | held |
