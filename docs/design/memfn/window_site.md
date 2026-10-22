# window_site — the UNIFIED WINDOW SITE: spans with a required core, one row family (design, rev 3)

Rev 3: lane uwin3, 2026-10-22 (rev 2 + the kit branch). DESIGN ONLY: no source or test edit, no make,
no timing. Applies the panel `docs/dev/reviews/2026-10-22-r1-memfn-window-site-rev2.md` and job 581's
reading (`docs/dev/lanes/r27b_report.md` RESULT). Every code claim was re-read; where the code says more
than the panel, the code wins (`[code]`). Marks: `[rev3 <id>]`, `bB*` build, `dD*` dir, `rR*` rit.
The step rev 2 called "S3 = B1" is **S3** here (not finding bB1). Appendix B places every finding.

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
| frame | site | form/op/handoff/empty/use/body/decl_point/hooks as today, the span range `span_lo`/`span_hi`, whether it is the VM attempt's seek | as today |
| alternatives | site | an UNORDERED set of 1 or 2 span lists, each a sound candidate definition alone `[rev3 dD1]` | one |
| entry | alternative | PARKED: candidates are where the parked machine leaves its start state (role A, k0); RESEED: from the walk (role B), the machine re-seeded at each. (The panel's HANDOFF, renamed: the frame has a `handoff` field) | no entry fact |
| frequencies | art | the byte-rate pcrec already declares (the analysis object on `mf_art_begin`) and the measure set | as today (E-1) |

**The absence rule.** A position off the subject PASSES outside the core and FAILS inside it (§1.2).

**The two-phase ask `[rev3 bB1]`.** Phase 1, DECISION: pcrec asks with the spans, alternatives and
frequencies; the kit answers the chosen alternative, the stop and the plan, and writes no text. pcrec's
NEXT predicates read that reply. Phase 2, TEXT: pcrec states the frame its NEXT row chose and asks for
the C text. The decision reads no frame fact (prefix_k reads none; the mass rule reads none).

**One row family (§2):** A STOP (one least-cost choice over (alternative, stop), with the declared
MARGIN row), B FIND FORM, C VERIFY PLAN, D RESUME (`c + 1`, or the Horspool row D-hors on a dense stop),
E FRAME. Floor: `generic`. Every rule is keyed on a stated fact, never on a label `[rev3 dD2]`.

**Staging (§5):** S1+S2 land as ONE branch of six commits `[rev3 seq]`, zero movers, one `MF_SITE_ABI`
event at the last commit. **S3**: REPORT routed by default, D-hors with it; the one byte-moving step,
judged on the scalar layer against the default build, with two named, capped losses `[rev3 S3]`.

---

## 1. The facts

### 1.1 The set, what each replaces, and the producer obligations

A SPAN is a run of consecutive positions `start .. start+len-1` relative to the candidate `c`, one set
per position; a gap is an all-256 position. Candidates are the `c` where every span of the chosen
alternative holds. Spans may overlap; positions at one offset are tested as their intersection (§2.3).

| fact | replaces | why it is enough |
|---|---|---|
| start + sets | `mf_term` (SET/RUN/mask), `ctx[]`, the context stop's `pred`, W0-W2 | a masked RUN is a product of per-position sets; every FIND site states "the window is the candidate" today |
| core | `absent`, `span_class` BOUNDED/CONTEXT, §14.5 rule 3, Q-R7-1's reads-below range, `end_back` | §1.2; `end_back` 1 is a full-set core position at the window's end |
| verify | per-term/per-predicate `need`, `consumable`, `consumable_len`, REPORT's "every term REQUIRED" | §1.4 |
| table offer | `table_ref` + `table_name` | the same capability per position; no row requires it |
| floor | `read_floor` + the `floor` hook | §1.3 |
| alternatives + entry | `plan_hint`'s implicit "pcrec chose the skip" (`pf_ofs_applies` reading `ofsk.nsel`) | the parked scan and the walk's skip are two DIFFERENT sound conjunctions (`\b\.[0-9]{4}Z`: `.` is outside k0; folding k0 into the walk's spans makes the offset-0 meet empty, MISCOMPILE-1's shape, S188) `[rev3 dD1]` |
| frequencies | `plan_hint`, `plan_pos`, `rank_n/pos/ppm` | the kit derives every rank and pick from the byte-rate it already receives |

**Spans are finite; the limits are pcrec's.** The one kit bound is the PROOF range `[MF_PROOF_LO,
MF_MAX_FWD)` (`mf_class.proven[]` is fixed): outside it a position is tested, unproven; a consumer needing
the proof declines on pcrec's side (trigger to grow it: a longer lookaround as context source, §7). pcrec
truncates a long run to its stated stretch (`pcrec_find_run_window_start`) before stating it (§9).

**Producer obligations** (asserted where pcrec builds the site): a verify-NO core is a SUBSET of the
positions where absence truly fails; each alternative is sound alone under its entry; each walked offset
is its OWN one-position span `[rev3 bB4]`; the pinned run R is stated in BOTH alternatives as verify NO
`[rev3 bB1]`; a whole-item SATISFIES item wider than one byte is declined. Exactness is not a fact
(R-26.7 dissolves: a SUPERSET item is sent only as verify NO, never readable as a proof).

### 1.2 The core rule

At candidate `c`, a span holds iff for every position `d`: `c+d` inside `[0, n)` → `s[c+d]` in the set;
`c+d` outside → `d` lies outside the core. Any per-position absent assignment equals one contiguous
core (the convex hull of the FAILS positions). Width-1 SATISFIES items, the cover mapping, MLINE and
`\z` were PROBED-AND-HELD by the r2 facts critic.

**An empty set** inside a core never holds (floor row). Outside the core it holds exactly when the
position is off the subject (`\z`: `c+k = n`).

| site (builder) | alternatives (entry) | spans | core | verify |
|---|---|---|---|---|
| the DFA prefilter (PF FIND `find_site`, offset-skip `ofs_pred_of`; HYB_PF) | PARKED: `{0: k0}` + R; RESEED (where pcrec's `offset-set` row applies, undenied): `{0: F0}` + one span per walked offset + R | as listed | `[0]` (bounded `[0, 1]` with `{1: any}`); R all; walked all | k0 YES, F0 YES, walked NO, R NO |
| VM hat seek | one | `{0: S}` | `[0]` | YES |
| MLINE `(?m)^` (`mline_find_of`, BOTH callers `[rev3 bB7]`) | one | `{-1: \n}` | `[-1]` | YES; floor = expression `start` |
| pre-check FUNC parts | one | one span per part | all | as the part's need |
| cover / REPORT (Z2: `known.c`) | one | span 0 `{0..k-1: S_d}`; one span per context item | `[0, k)`; an item: its position if FAILS, empty if SATISFIES | all YES |

Out of the family, unchanged: PRESENCE (`pspans`, ALL_PRESENT), SKIP/ADVANCE, VMRUN, MISMATCH.

### 1.3 The floor and the edge

- **SUBJECT**: reads lie in `[0, n)`; below 0 the core rule decides. REPORT states it.
- **an expression F** (`F <= lo`): reads lie in `[F, n)`; a candidate needing a read in `[0, F)` is NOT
  COVERED: the kit does not yield it and pcrec's EDGE attempt owns it (today's MLINE).

**The guard is three-way**, per non-core position: off the subject → passes; inside `[0, F)` → the
edge's (not covered); else → membership. Core positions get ONE hoisted bound per candidate.

### 1.4 `need`, `consumable`, REPORT

- `need` becomes the span's verify (REQUIRED = YES, OPTIONAL = NO). The kit never ADDS a constraint.
- R-25 is the proof rule: `proven[d]` = "for every yielded `c` with `c+d` inside the subject, `s[c+d]` is
  in the set", computed from the plan the text TESTS; off-subject positions are the core rule's.
- `consumable`/`consumable_len` retire (no reader); `exact_len`/`prefix_stated` are pcrec-internal.
- **REPORT is the window site with every span verify YES. Nothing else.** The VM seek is a FRAME fact
  with one reader (D1w) and a RETIREMENT TRIGGER `[rev3 dD6]`: when D1w is measured (finder.c's trigger,
  grid2's VM_ATTEMPT one-byte cells) it folds into D1 or becomes MEASURED; on the fold the fact retires.

---

## 2. One row family

```
  phase 1 (DECISION, no text)
    A  the STOP: one least-cost choice over (alternative, stop); the MARGIN row
    C  the VERIFY PLAN of the chosen (alternative, stop)
  phase 2 (TEXT, in the frame pcrec chose from the reply)
    B  FIND the next p in [max(c + d*, F, 0), n) with s[p] in set(d*); empty if the start >= n
    C  test the plan at c (one hoisted core bound, three-way guards outside it)
    D  on failure RESUME
    E  render in the FRAME
  floor: generic (a byte loop over the chosen alternative's spans under the core rule)
```

Every table is a `kit_table` on `kit_walk` (compose.c): first match, a contract per row, a deny where it
moves bytes, a basis; every cost row reads ONE cost table (§3.3). The family emits a PATH ID per site
(trace build); §2.7 maps paths to old rows for the reach floors `[rev3 bB9]`.

### 2.1 Table A — the stop; adoption is its alternative half (no ADOPT table) `[rev3 dD1, dD2, bB2]`

| row | holds when | the choice | basis |
|---|---|---|---|
| A-parked | the alternative's entry is PARKED | stop = its verify-YES position (k0 at offset 0): the parked scan may skip only bytes that keep the machine parked | role A (prefix_k's comment); today's |
| A-model | the alternative's entry is RESEED | over its one-member positions at offset != 0 (the model's DOMAIN: the scan moves, as a singleton; MEASURED, §3.2), the least `model_cost` with C-model's plan; ties to the LOWER offset | prefix_k verbatim (§3.2) |
| A-mass | no entry fact (REPORT, pre-check parts, VM seek, MLINE) | over the core positions, the least mass; ties by the TIE COLUMN below | 580/581 (REPORT); `pcrec_find_run_rank` (parts) |
| MARGIN | two alternatives stated | a RESEED alternative wins only at less than HALF the least-cost PARKED one: `best * 2 < base` (prefix_k: `best * MATERIAL_NUM >= base * MATERIAL_DEN` rejects) | §4.5's argument; ipv4's 1.5-1.6x inside the error bars |
| (none) | no core position | the floor row | — |

`base` is the PARKED alternative's cost with an EMPTY plan, `model_cost(k0 one member ? C_MEMCHR :
C_BITMAP, mass(k0), 0, 1000000)`: prefix_k prices the parked scan by k0's count, not by B's form.

**The TIE COLUMN**, keyed on the position's kind (zero movers needs both; replaces rev 2's single rule
and dir D5's contingency `[rev3 bB2]`):

| position kind | tie | code | basis |
|---|---|---|---|
| inside a stated run stretch (one-member or cube positions, C-run's grouping) | HIGHER offset | `pcrec_find_run_rank` (stable insertion over `[n-1..0]`), finder P3 "ties to the higher pattern order" | today's; on REPORT literal stretches UNMEASURED DEFAULT |
| a set position | LOWER offset | prefix_k's strict `<` over ascending offsets | MEASURED on REPORT: job 581's PRR (rightmost) loses 1.23-1.57x on year4, 1.03-1.40x on hex8 `[rev3 581]` |

### 2.2 Table B — how the stop is found

Table B IS the finder's FIND slot (`fd_rows`, finder.c), asked "the next byte in set(d*) at offset d*".
The rows R8, R3a, R3b, R4, R1, R2 are KEPT UNCHANGED, inert without the knowledge they read `[rev3 bB8]`.

| row | holds when | form | basis |
|---|---|---|---|
| R8, R3a, R3b, R4, R1, R2 | as today (iterator history, measured gaps, crossovers) | as today | as today; inert without knowledge |
| D1c | the stop lies below the candidate (re-keyed from today's `SF_CONTEXT_STOP`) `[rev3 bB7]` | libc back search | UNMEASURED DEFAULT (today's) |
| PAIR | today's scope: the stop is a two-member cube inside a stated run stretch (ofsskip's `fn-pair`, now a FIND-slot row) | two `memchr` streams | today's; no PAIR cost constant `[rev3 bB2]` |
| (SIMD) | `-fmemfn-simd`: vrun's PREFIX rows | today's | inert at OFF |
| D1 | one member, not the VM seek | `memchr` | UNMEASURED DEFAULT (finder.c's basis column) |
| D1w | one member, the VM seek | the table walk | UNMEASURED DEFAULT; retirement trigger §1.4 |
| R7w | every other set | the WALK (walk_vs_v1_record.md) | MEASURED (B4′) |

`[code]` rev 2 marked D1 MEASURED; finder.c says `FB_UNMEASURED_DEFAULT`. D2 and RPT retire.

### 2.3 Table C — the verify plan

One plan object (positions in order, each with its test): the renderer walks it, `proven[]` is computed
from it, a trace build asserts rendered = plan. The text shape is the E rows'.

| step | row | rule |
|---|---|---|
| 1 merge | C-meet | positions at one offset, across spans, are ONE position with the intersection set, before grouping; empty inside a core → floor row |
| 2 select | C-yes | every verify-YES position (on a RESEED alternative: F0 at offset 0, always) |
|  | C-model | on a RESEED alternative: plus prefix_k's greedy pick among verify-NO walked offsets (§3.2, exact) |
|  | C-none | otherwise no verify-NO position (PARKED alternatives, REPORT, parts) |
| 3 pin | C-pin | `[rev3 bB1]` R becomes ONE compare (its selected offsets dropped) when R is stated (length >= 2), the stop IS R's scan member (the run position the mass rule picks; on a PARKED alternative k0 is that one byte), and the plan does not already test all of R. `[code]` narrower than the panel's "a stop inside the stretch": `pf_run_applies_common` requires EQUALITY with the scan member |
| 4 drop | C-stop | minus the stop's own position when B's set equals it, except inside a pinned stretch (C-pin keeps it whole) |
| 5 group | C-run | a maximal stretch of consecutive one-member or cube positions inside ONE stated span is one run compare; never across one-position spans `[rev3 bB4]` |
| 6 test | C-table / C-own | an offered table (pcrec's name), else the kit's own `set_test` |
| 7 order | C-asc | ascending offset (today's) |

`[code]` C-pin is a PLAN row after the choice, not a third alternative: today's `run-pinned` with
`nsel == 0` is PARKED + C-pin, rendered by the re-seeding emitter with no margin; MARGIN ignores C-pin.

### 2.4 How pcrec's NEXT rows read the reply `[rev3 bB1]`

Today's NEXT predicates read the planner's PICK (`pf_ofs_applies_common`: `ofsk.nsel > 0`;
`pf_run_applies_common`: the model's scan, `ofs_test_model`). Rows 5-7 do not test `nsel`; first-match
order reaches them only when `nsel == 0`. After S2 the same rows, order and denies read the reply:

| row | today | reads instead |
|---|---|---|
| `run-pinned[-bounded]` | pin + identity + clause 4 | the reply's plan carries C-pin |
| `offset-set[-bounded]` | `nsel > 0` | the reply chose the RESEED alternative |
| rows 5-13 | `nsel == 0` by order | unchanged (the reply chose PARKED with no C-pin) |

`-fno-offset-skip` keeps its identity: denied, pcrec states only the PARKED alternative (and the
run-pinned pair's deny bits remove C-pin's row from pcrec's NEXT, as today).

### 2.5 Table D — the resume `[rev3 dD3, 581]`

| row | holds when | resume | basis |
|---|---|---|---|
| D-hors | the stop's set has mass >= `HORS_MIN` (~146,000 ppm) and the window is at least 2 positions | Horspool over the TESTED sets (581's HRS text): probe the window's LAST position; on a miss or a failed verify advance by `sh[b]` = least `t` with `b` in the tested set at `last - t`, else the window length. It replaces B's scan on that site | job 581, PROVISIONAL |
| D-one | always | `c + 1` | the floor (today's) |

`HORS_MIN` (§3.3) is PROVISIONAL: fit on 8 cells with ONE winner (hex8, stop mass 284,434 ppm; the next
densest 74,760 ppm), at the gap's geometric middle. Physically: with no rare stop to skip to, skip by the
window's end (the stop span's core). Its FIRST NEW POPULATION (S1's count, §5.2) is its re-test trigger:
read (G1, scalar) before the row is called measured.

D-hors moves bytes: it lands at S3 with its own deny, never at S2. D-shift stays out: 581 fits its rule,
but HRS serves hex8 and SHF's wins elsewhere are marginal.

### 2.6 Table E — the frame

| row | holds when | text |
|---|---|---|
| E-func | FUNC/RETURN, miss `n`, no expression floor | today's `static inline size_t` (D155 seam) |
| E-stmt | STMT/ASSIGN or ON_MISS | today's PF block (guard, post-test, `moved` hook, `decl_point`) |
| E-generic | anything else | the floor row |

REPORT is STMT/ASSIGN: E-stmt, and **keeps the STMT frame** `[rev3 581]`: PRF (the FUNC twin) reads
1.03-1.09x search_short/none, 1.07-1.25x dense vs COV. Native offset-skip sites keep FUNC (zero movers).

### 2.7 What folds where, and the path map

| row today | fate | family path id (reach floors, §5.3) |
|---|---|---|
| `pf_memchr`, `pf_memchr_bounded` | FOLD: A-parked + D1 + C-none + E-stmt | `parked-d1[-b]` |
| `pf_walk`, `pf_walk_bounded` | FOLD: A-parked + R7w + C-none + E-stmt | `parked-walk[-b]` |
| `pf_memchr_back` | FOLD: A-mass + D1c + E-stmt | `back` |
| `ofsskip` `fn-memchr` / `fn-pair` / vrun PREFIX | FOLD: A-model (+ C-pin) + D1 / PAIR / vrun + C-model + E-func | `reseed-d1`, `reseed-pair`, `reseed-vrun`, `pin-*` |
| `precheck` | STAY (ALL_PRESENT); its FUNC parts render through A-mass + C-yes | `part-*` |
| `runcmp`, `mismatch_inplace`, `generic` | STAY (C-run's compare; MISMATCH; the floor) | — |
| RPT, `kit_report_exact`, `SF_PROOF_EXACT`, `FF_PROOF`, D2 | RETIRE | `report` (S3) |

**Deny identities and form names are preserved**: `fd-d1` (→ D1w), `fd-pres-*`, `pres-set-lead`,
`vrun-*` keep names and effects; `vrun-kb` reads the kit's own ranking (a `registry.md §6¶8a` wording
hunk in S2); every folded row's `_MEMFN_FORMS` name stays that path's name.

---

## 3. The decision is the kit's, from pcrec's frequencies

### 3.1 Why there is no plan hint

prefix_k reads the pattern's sets and the byte-rate; the kit has both, so a pick from pcrec would be a
method (D157). The planner's RULES become rows keyed on stated facts (entry, position kind).

### 3.2 prefix_k as rows, exactly `[rev3 bB3]`

Units: hundredths of a cycle per subject byte; masses in ppm (`pcrec_find_set_ppm` = the kit's
`set_mass`, PROBED-AND-HELD). Every division is integer and truncates, in this order:

```
verify_cost(p)               = C_VERIFY + C_MISPRED * min(p, 1e6 - p) / 1e6
model_cost(scan, m, vc, vr)  = scan + m * vc / 1e6 + (m * vr / 1e6) * C_ENTER / 1e6
base                         = model_cost(k0 one member ? C_MEMCHR : C_BITMAP, mass(k0), 0, 1e6)
for each walked offset si >= 1 whose set has ONE member (scan cost C_MEMCHR):
    order = the other walked offsets j >= 1, j != si, by ascending mass via prefix_k's exchange sort
            (UNSTABLE on equal masses: the cap's tie order is that sort's, declared as the algorithm)
    plan  = {F0}; vr = mass(F0); vc = verify_cost(mass(F0)); cost = model_cost(C_MEMCHR, mass(si), vc, vr)
    for a in order while |plan| < MAX_SET - 1:      (MAX_SET = 4: F0 plus at most TWO verify-NO offsets)
        nv = vr * mass(a) / 1e6; nc = model_cost(C_MEMCHR, mass(si), vc + verify_cost(mass(a)), nv)
        if nc >= cost: continue                     (skip it and keep trying; no early stop)
        take a
    best = least cost over si, strict <  (ties: lower offset)
adopt iff best * 2 < base
```

The table rows' bases: the mispredict term and MISCOMPILE-1 (S188, F0 never k0) as the code cites;
"the scan moves, as a singleton" MEASURED (uuid 4.5x, iso-ts 4.8x, stack-frame 7.2x, needleXYZW 17.1x
moved; bignum 0.96-1.02x stayed, offset_k_skip.md §7.3); the margin argued (§4.5, ipv4's 1.5-1.6x).

### 3.3 The constants: data, with provenance and box `[rev3 dD4]`

One declared kit table (an X-macro beside `options.def`, e.g. `plan_cost.def`: name, value, unit,
provenance, box, basis), read by every cost row; prefix_k's INTEGERS verbatim, no re-measurement:

| name | value (unit) | provenance | box | basis |
|---|---|---|---|---|
| C_MEMCHR | 6 (1/100 c/B) | opt3_dfa_scan_measurement.md §4 CONTROL 1 (0.055 c/B, glibc AVX2 memchr) | ubuntubudu, Ryzen 5 1600 | MEASURED |
| C_BITMAP | 116 (1/100 c/B) | same table, row 1 (1.16 c/B) | ubuntubudu | MEASURED |
| C_VERIFY | 250 (1/100 c per candidate) | none beyond the header's "one load + one table probe" | — | UNMEASURED DEFAULT |
| C_ENTER | 2000 (1/100 c per entry) | [OPT-3]'s 10.7 c/B times an ASSUMED ~2 bytes; sensitivity swept over 1,352 patterns (offset_k_skip.md §4.3) | ubuntubudu | MEASURED x ASSUMED |
| C_MISPRED | 1500 (1/100 c) | the before/after of offset_k_skip.md §7.3 | ubuntubudu | DERIVED from a measured before/after |
| MATERIAL | 2/1 | §4.5's argument | — | ARGUED |
| HORS_MIN | ~146,000 (ppm) | job 581 (r27b_report.md RESULT) | dev box, 7700X | PROVISIONAL (§2.5) |

Re-measuring any is a byte-moving kit event (integration.md §21.3): own deny, pcrec abi event, G1.

### 3.4 The stamps read the phase-1 reply

`<PREFIX>_DFA_PREFILTER_OFFSETS` and `<PREFIX>_DFA_PREFILTER`'s `offset-set` value are written from the
reply (chosen alternative, stop, plan), never from a pcrec-side recomputation; phase 1 makes the reply
exist before the stamp line. Spec hunks in S2: `match_api.md §6.3.1¶5a`, `tuning.md §2.14¶3` and
`§2.30¶2`. Their VALUES must not move at S2.

**The `_FINDINGS` consulted line and the UNDERIVABLE/BROKEN diagnostics `[rev3 bB5]`** are raised by the
first ask of `pcrec_find_byte_rate` (findings.c), today made by askers that retire (prefix_k, the run
rank's callers). The builder that states frequencies to a family site asks it there, for exactly today's
population, so neither moves.

### 3.5 The reseed is the chosen alternative's entry

The reseed is keyed on the reply's chosen alternative's ENTRY, a fact; no special keying `[rev3 dD1]`.
Making it unconditional (integration.md §R4.3.5's M5′ item) would mean stating every alternative as
RESEED: a byte-moving pcrec event, filed if anyone wants it (D77).

---

## 4. What retires, with its readers (re-grep at the build commit)

All rows retire at S2 unless marked. Sabotage rows are derived by §5.4's rule at the step's commit, not
listed per row `[rev3 rR1]`.

| retires | readers |
|---|---|
| `ctx`/`nctx`, `MF_MAX_CTX`, `MF_MAX_AHEAD` | `memfn.h`, `memfn/include/CLAUDE.md`, compose.c, gate.c, generic.c, fields.def, `src/gen/known.c`, `src/ir/dfa.c`, `src/core/internal.h`, `tests/memfn/proof_check.c` |
| `absent`, `consumable`, `consumable_len`, `mf_absent` | `memfn.h`, kit.h, compose.c, gate.c, generic.c, fields.def, `memfn/tests/g2/{g2_gen,g2_simd_gen}.c`, `known.c`, `memfn_sites.{c,h}`, `tests/memfn/{arm_fixtures.c,proof_run.c,proof_check.c}` |
| `prefix_stated`, `exact_len` (contract side) | `memfn.h`, kit.h, compose.c, gate.c, fields.def, formhash.c, g2 generators, `known.{c,h}`, `memfn_sites.{c,h}`, `tests/memfn/{proven_check,arm_fixtures,proof_check}.c` |
| `span_class` BOUNDED/CONTEXT (PRESENCE stays) | `memfn.h`, compose.c, gate.c, generic.c, formhash.c, g2 generators, `known.c`, `memfn_sites.c`, `emit_dfa.c`, `tests/memfn/{proven_check.c,arm_fixtures.c,run_proof.sh,proof_check.c}` |
| `read_floor` (merged into floor) | `memfn.h`, kit.h, compose.c, gate.c, fields.def, g2 generators, `known.{c,h}`, `memfn_sites.{c,h}`, `tests/memfn/{arm_fixtures,proof_check}.c` |
| W0-W2, `end_back` | `memfn.h`, kit.h, compose.c, finder.c, gate.c, fields.def, formhash.c, g2 generators, `memfn_sites.{c,h}`, `tests/memfn/{run_arm_pins.sh,proven_check.c,arm_fixtures.c,proof_check.c}`, `tests/codegen/run_fallback_table.sh` |
| per-term/per-predicate `need` (presence spans keep theirs) | `memfn.h`, every builder (`emit_dfa.c`, `emit_vm.c`, `memfn_sites.c`, `known.c`), compose.c, finder.c, gate.c |
| `site_kind` REPORT's meaning, `consumer` `[rev3 rR2]` | `memfn.h`, `memfn/include/CLAUDE.md`, kit.h, compose.c, finder.c, gate.c, fields.def, formhash.c (its canonical site sets `consumer`), g2.h, g2_gen.c, g2_simd_gen.c, `known.{c,h}`, `memfn_sites.{c,h}`, `emit_dfa.c`, `src/parse/rxt_source.c`, `tests/memfn/{site_census.py,site_manifest.tsv,site_manifest_check.py,finder_check.py,proven_check.c,arm_fixtures.c,proof_check.c,run_deleg_sites.sh}` |
| RPT, `kit_report_exact`, `SF_PROOF_EXACT`, `FF_PROOF`, D2 | finder.c, kit.h, compose.c, `memfn/src/CLAUDE.md`, `tests/memfn/{rows.tsv,row_floors.tsv,arm_fixtures.c,run_proof.sh,finder_check.py,run_rows.sh,proof_check.c}` |
| `plan_hint`, `plan_pos`, `rank_n/pos/ppm`, `MF_RANK_MAX` | `memfn.h`, compose.c, formhash.c, ofsskip.c, precheck.c, vrun.c, `memfn/tests/{run_g2_simd.py,g2/*}`, `known.c`, `memfn_sites.c`, `emit_dfa.c` (`ofs_pred_of`, `ofs_pred_rank`), `tests/memfn/{run_rank.sh,rank_check.py,proven_check.c,arm_fixtures.c,proof_check.c}` |
| pcrec's selection (`pcrec_prefix_ksets`' pick; the walk `kset_walk` STAYS, it is a fact) | `src/opt/prefix_k.c`, `src/core/internal.h`, `emit_dfa.c` (`ofsk`, the NEXT predicates §2.4, `ofs_test_model`), `tests/codegen/{run_offset_skip.sh,run_form_census.sh}` |
| ofsskip/pffind as arms | compose.c `arms[]`, precheck.c, `tests/memfn/rows.tsv`, finder.c's arm map |
| `mf_preview("R-26.6")` | stays until S3; then retires with RPT: `memfn_sites.c`, `src/core/internal.h` |

**`MF_SITE_ABI` readers `[rev3 rR3]`:** `memfn.h`; compose.c and presence.c (the refusals); formhash.c
and `memfn_sites.c` (fills); `g2_gen.c` (incl. abi-mismatch cases), `g2_simd_gen.c`; the ledgers and
CLAUDE.md files that cite it. S2 re-pins `tests/memfn/pins/arms.tsv` and `pins/m6_target/*`.
**The number reaches no artifact `[rev3 rR8]`:** `grep -n MF_SITE_ABI memfn/src/*.c` shows only fills,
refusal comparisons and compose.c's refusal message; the form hash hashes rendered text; the stamps carry
no kit version. Check: S2's emit_sweep is byte-identical across the number change.

---

## 5. Staging

### 5.1 One landing, six commits `[rev3 seq]`

Order: B4′ (landed) → S1+S2 as ONE branch, ONE landing → S3. No adapter: no code reads old fields into
spans. Every commit builds and passes `make test`.

| # | commit | owner |
|---|---|---|
| 1 | the kit family under `mf_preview("window-family")` (tables, cost table, plan object, guard, decision ask); G2 generates span sites | kit lane |
| 2 | pcrec states spans, alternatives with entry, and the byte-rate BESIDE the old fields; the family never reads old fields | pcrec lane |
| 3 | a trace shadow comparing the family's decision with today's pick per site: a LOCALIZER for commit 5's diffs, never the acceptance | pcrec lane |
| 4 | the two-phase ask under the lever; NEXT predicates read the reply (§2.4) | pcrec lane + kit lane |
| 5 | the lever's default flips. THE witness: emit_sweep against pre-S2 main on every arm, plus the reach floors | manager reads |
| 6 | delete the old path and old fields; stamps read the reply; spec hunks; the `MF_SITE_ABI` number (and `MF_CLASS_V` for the reply) at this commit, "next at landing" | both lanes |

### 5.2 The steps

| | S1+S2 (commits 1-6) | S3 (one commit, kit + pcrec) |
|---|---|---|
| content | the family; pcrec's builders (PF, MLINE both callers, VM hat, OFS, pre-check FUNC parts, Z2's cover site) state facts only; §4's rows retire; the stamps and the consulted line as §3.4 | REPORT routed by default (the cover site renders the family's E-stmt text); D-hors enters the default table |
| witness | G2 (generated spans vs the scalar byte loop); `proof_run` (sentinels); emit_sweep byte-identical to pre-S2 main on every arm (default, each deny, `--engine=vm`, both SIMD layers), stamps included; `tests/findings/manifests/*_movers.txt` unchanged `[rev3 rR5]`; reach floors; `REACH_ONLY=1` re-aim | the 650 harness at the SCALAR layer, §6's bar; the answer gate; G1 on every non-REPORT site D-hors moves (emit_sweep's diff names them) |
| abi | ONE `MF_SITE_ABI` event (+ `MF_CLASS_V`), at commit 6; NO pcrec abi event | pcrec abi bump (readers by grep, D76/D94) in the same commit |
| spec | `match_api.md §6.3.1¶5a`, `tuning.md §2.14¶3`, `§2.30¶2`; `registry.md §6¶8a` (`vrun-kb`'s source); `findings.md` §4's reader table: the k-set selection and the run's scan member become the kit's readers, tie orders as declared `[rev3 rR5]` | `registry.md §6¶8a` (two new rows), `§6¶8b` floor 12 → 14; the cover stamps where caller-visible |
| deny | none new; the `--list-axes` memfn rows and floor (12) do NOT move `[rev3 rR4]` | TWO kit DENY rows (SCALAR, `options.def`): the routed REPORT row and D-hors, names the kit's; each its change's alpha OFF arm; `test-axes` sweeps them via `--list-axes` `[rev3 rR4]` |
| sabotage | §5.4's derived re-aims; kit plants: an untested offset claimed; absent-FAILS yielded; absent-SATISFIES dropped; empty meet not sent to the floor; a below-F read passing; C-pin splitting the stretch; a RESEED chosen under the margin | the routed row denied but rendering; D-hors's bound one short (581's own plant: `c + K > n` read as `c + K - 1 > n`) |
| go | G2 + `proof_run` green; zero movers MEASURED on every arm; every reach floor met; the derived sabotage list green; S1's two COUNTS reported (below) | §6 |
| no-go | any red, any mover, any floor missed, any stamp or manifest moved | §6 |

**Sabotage ids `[rev3 rR6]`.** pcrec-side ids are main's, above the highest id on main AND in
`worktrees/*/tests/mech` at filing; kit-side ids come from a range the request reserves.

**S1's counts** (at commit 5, no clock): `[rev3 dD2]` sites outside the model's scope stating verify-NO
positions (pre-check OPTIONAL parts, cover SUPERSET items; UL3's population); `[rev3 581]` native family
sites satisfying D-hors (its first new population).

### 5.3 Reach floors per old row `[rev3 bB9]`

Before S2 the trace build counts each OLD row's sites (§2.7, the cover site under the lever) over the
emit_sweep corpus; after S2 each replacing PATH ID's count must be at least the old row's (the kit's reach
counter, `row_contracts.md`; driver `scripts/emit_sweep.py`; a zero is red, K35; MLINE counts both callers).

### 5.4 Z2's cover site, and the derived sabotage rule

S2 restates Z2's cover site (§1.2; `mf_preview` until S3); the default build never renders it, so its
witness adds the lever's arts before and after (`--harness=kit-proof`, 393 cells and X1).

**Sabotage re-aims are DERIVED**, over `tests/mech/sabotages/`, in the step's commit: (1) candidates =
rows whose `SAB_FILE` the step's diff touches; (2) `VALIDATE_ONLY=1`: an unresolved anchor is re-aimed;
(3) an anchor inside a changed hunk or naming a §4 identifier is re-aimed, intent re-verified; (4)
`REACH_ONLY=1` over the touched arms; (5) a row whose `SAB_SUITES` detector the step edits gets a FULL
run; (6) the report prints the union and its count; a row retires only with its code, naming its successor.
Z2's cover rows are S1130-S1141, S1144, S1148 and S1149. There is no S1257-S1290.

---

## 6. S3's acceptance, and hex8 `[rev3 S3, dD3, 581]`

The kit manager's ruling (panel §2; Frank on hex8: "make the judgement call ... we need this regardless
of where hex lands"), in substance:
- **Scalar layer only**; the SIMD verdict is pcrec-bench's (D144 add. 4). Rev 2's "both layers" was wrong.
- **The floor** is job 580/581's per-cell floor(PRO) column.
- **The user-facing comparison is DEF** (the default build). COV (today's unrouted, never-shipped REPORT
  form) is a design-quality check, not a regression bar.
- **Two named, measured losses, each capped at its measured ratio plus the floor:** hex8-bounded
  throughput/dense (an all-hex subject; every form loses to DEF: HRS 1.531, PRO 1.412, SHF 1.378, COV
  1.322; HRS routes hex8 for its 2-6x wins elsewhere: 0.458, 0.490, 0.523, 0.173 against DEF), and
  file-ext-order search_short/none (PRO/DEF 1.033 against a 0.020 floor; one bounded effort, PRF, read
  worse at 1.094; accepted).
- **cat-bounded search_short/dense is not a user regression:** PRO/DEF 0.402; it reads 1.18 only vs COV.

S3's go: zero answer changes; every other `real`/`none`/`dense` throughput and search_short cell not
slower than DEF beyond its floor(PRO); the two named cells within their caps; G1 green on D-hors's
non-REPORT movers. This rewords main's R-27.1 bar ("`dense` not slower than COV"); main is asked (§9).
In family terms, 581's PRO = A-mass + B + C-yes + D-one + E-stmt and HRS = PRO with D-hors.

---

## 7. The pcrec producer (D168, `ctx_span.md`)

`MkLang`'s `S_d` are span 0's positions; each `MkCtx` item is one span (least to greatest offset, gaps
full-set; FAILS → core, width-1 SATISFIES → empty core; EXACT may be YES, SUPERSET only NO). A longer
lookaround is a longer span with no new field. What does NOT dissolve: the proof range (§1.1) and the
SOURCE switch (`(?<=ab)` needs the facts-layer producer as THE context source, pcrec's own event with X1
as its control).

---

## 8. The three standing questions (`docs/design/CLAUDE.md`)

1. **Measurement regime: RELEVANT at S3 and D-hors only.** S1+S2 move no default byte (emit_sweep reads
   them). S3: R-27.1's regime (650 harness, three regimes x three classes, SCALAR, Linux, pinned, 581's
   absolute columns and A/A pair) against DEF. The cost constants are Zen 1 (ubuntubudu), HORS_MIN Zen 4
   (dev box); another box could move the margin's or HORS_MIN's verdict, each its own event.
2. **Independent control: RELEVANT.** Answers: `proof_run` (sentinels), 581's python `re` differential,
   G2's scalar loop over generated spans; none shares the family's source. Movers: emit_sweep's pcrec-side
   diff vs pre-S2 main (planner and kit share a MODEL, no code: the diff proves the move, not the model),
   plus the findings mover manifests (another prior); reach floors count the old rows' population (K35).
3. **What moves when data is regenerated: RELEVANT.** The byte-rate and the cost table (HORS_MIN
   included) feed every decision: regenerating either can move a stop, plan, adoption or D-hors site, a
   pcrec abi event (integration.md §21.3) and the `DFA_PREFILTER*` stamps' values (D80).

---

## 9. Questions

Ruled: Q1-Q5 (r2: one offset; the kit's rules; no REPORT label; hex8 the kit's, applied §6; `end_back` a
core position); 581 settles the LEFTMOST tie on set positions and the STMT frame for REPORT.

**OPEN, for main:**
- **The S3 bar wording** (§6): DEF as the user-facing comparison and the two capped losses, which rewords
  R-27.1's "dense not slower than COV". Leaning: agree (the panel's ruling).
- **`<PREFIX>_REQ_RUN`'s `@idx`** ("which position of the run the scan tests", `findings.md` §4): after S2
  the kit picks it by the same mass rule. Read the reply, as OFFSETS does, or stay pcrec's rarity fact?
  Its value cannot move at S2. Leaning: read the reply, in commit 6, with the findings.md hunk.
- **The run truncation window** (`pcrec_find_run_window_start`, least mass, ties leftmost) is a
  frequency-based choice inside pcrec shaping R. Leaning: pcrec's at S2, a limit of the statement like
  the proof range; revisit when a span longer than `PCREC_MAX_REQ_RUN_EMIT` is stated.

**OPEN, for S1 to measure:** the two counts (§5.2). **Filed:** UL1-UL4 (panel §3); PRF's reading on
native offset-skip FUNC sites (a byte move; trigger: a bench cell showing FUNC losing on a native site).

---

## Appendix A. The S2 request text (for main to file in `memfn/docs/requests.md`; facts only, D157)

> **R-NN (date, pcrec manager) — the window site stated as spans, alternatives and frequencies; the
> decision and its text are the kit's**
>
> **Customer:** D172 (Frank, 2026-10-21: "pcrec states spans; the find-window and REPORT are the same
> request; choices are table-driven"), and integration.md §14.9 items 2-3 / Q40 (RULED YES: the kit
> decides adoption).
>
> **Facts pcrec will state, for every FIND site of the family (PF, PF bounded, MLINE at both callers,
> the VM hat seek, the offset-skip block, the pre-check's FUNC parts, Z2's cover site):**
>
> | fact | meaning |
> |---|---|
> | spans | per span: a signed start offset from the candidate, one byte set per position, a contiguous required core (possibly empty), verify YES (every yielded candidate satisfies it) or NO (a true filter) |
> | the core rule | at candidate c, a position d off the subject PASSES outside the core and FAILS inside it; on the subject the byte must be in the set |
> | table offers | per position, where pcrec already emits a membership table for that set, its name |
> | floor | SUBJECT, or an expression F; per non-core position the guard is three-way: off the subject passes, inside `[0, F)` is pcrec's edge (the candidate is not covered), else membership |
> | alternatives | an UNORDERED set of one or two span lists, each a sound candidate definition alone, each with its ENTRY: PARKED (candidates where the parked machine leaves its start state) or RESEED (candidates from the walk; the machine is re-seeded at each) |
> | frame (phase 2 only) | form/op/handoff/empty/use/body/decl_point/hooks, span range, whether it is the VM attempt's seek |
> | frequencies | the analysis object's byte-rate and the measure set, as already passed on `mf_art_begin` |
>
> **Producer obligations pcrec asserts:** a verify-NO core is a subset of the positions where absence
> truly fails; each alternative is sound alone under its entry; each walked offset is its own
> one-position span; the pinned run, when pinned, is stated in every alternative as verify NO.
>
> pcrec stops stating `plan_hint`, `plan_pos`, `rank_*`, `ctx[]`, `absent`, `consumable`,
> `consumable_len`, `exact_len`, `prefix_stated`, `span_class` BOUNDED/CONTEXT, `read_floor`, W0-W2,
> `end_back`, per-term `need`, `consumer` and REPORT's kind meaning.
>
> **What pcrec needs back:** (phase 1, no text) the chosen alternative, the stop (offset and set), the
> positions the plan tests and whether the pinned run is compared whole; (phase 2) the C text in the
> stated frame and the proof class as today. pcrec's NEXT rows and the `DFA_PREFILTER`/`_OFFSETS` stamps
> read the phase-1 reply.
>
> **The kit retires `[rev3 rR7]`:** RPT, `kit_report_exact`, `SF_PROOF_EXACT`, `FF_PROOF`, D2, ofsskip
> and pffind as arms (folded), and every reader of the fields above in ofsskip.c, precheck.c and vrun.c.
>
> **Landing bar** (window_site.md §5): one branch of six commits, one landing; zero movers on every
> emit_sweep arm, stamps included; the findings mover manifests unchanged; reach floors met; every deny
> keeps its identity, the `memfn` floor stays 12; one `MF_SITE_ABI` (and `MF_CLASS_V`) event, numbered at
> landing; the derived sabotage list green.
>
> **Not asked:** any method. How the kit picks, plans, finds or resumes is the kit's (D157).
>
> **Sequencing:** after B4′; S3 (REPORT routed, D-hors) follows as its own byte-moving event.
>
> **Sabotage ids:** kit-side from a range this request reserves; pcrec-side from main's ledger above the
> highest id on main and in worktrees at filing. The Z2 cover rows that exist are S1130-S1141, S1144,
> S1148 and S1149; S1257-S1290 does not exist.

---

## Appendix B. Where each finding landed

**This panel (2026-10-22 r1):** build B1 §0 (two-phase ask), §1.1 (R in both), §2.3 C-pin (`[code]`
narrowed), §2.4; B2 §2.1 (A-model/A-mass, tie column), §2.2 PAIR; B3 §3.2; B4 §1.1, §2.3 C-run; B5 §3.4;
B6 §6; B7 §2.2 D1c, §1.2 and §5.3 (both MLINE callers); B8 §2.2; B9 §2, §2.7, §5.3; seq §5.1. dir D1
§0, §2.1 MARGIN, §3.5; D2 §2.1, §5.2 count; D3 superseded by 581, §2.5; D4 §3.3; D5 yields to the tie
column; D6 §1.4; D7 Appendix A; D8 held (§3.1); UL1-UL4 §9 (filed). rit R1 §4 (defers to §5.4); R2 §4;
R3 §4; R4 §5.2; R5 §5.2; R6 §5.2; R7 Appendix A; R8 §4. §2's S3 ruling §6. Job 581: leftmost tie §2.1;
STMT frame §2.6; HRS §2.5, §3.3, §6.

**The r2 panel (2026-10-21) and the kit manager's rulings, as they stand in rev 3:** P1 §5.1; P2
superseded by kit-mgr 1 (§3); P3 §1.4; P4 §2.3; P5 §2.1 tie column, §2.2 (REGIME gone), §2.5 (D-shift
out); P6 §2.2 PAIR; P7 §1.1; G1 dissolved (§5.1 commit 3 is a localizer, not a comparator); G2 §2.3
C-stop/C-pin; G3 §2.7, §2.4; G4 §3.4; G5 §5.3; G6 §5.4; G7 §5.1 commit 6; G8 Appendix A; G9 superseded
by P1; G10 §5.1, §4; F1 §1.1; F2 §1.3; F3 §1.1-§1.2; F4 §2 (B's clamped start); F5 §1.4, §5.2; F6 §1.1;
F7a-e §1.2, §0, §2.3, §2.5; Q1-Q5 §9; U1-U7 unchanged as filed; kit-mgr 1 §3, §2.1; kit-mgr 2 §3.4;
kit-mgr 3 §2.5, §6 (581 applied); kit-mgr 4-5 §5, Appendix A.
