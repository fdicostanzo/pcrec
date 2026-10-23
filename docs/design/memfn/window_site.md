# window_site — the UNIFIED WINDOW SITE: spans with a required core, one row family (design, rev 3.3 DRAFT)

Rev 3: lane uwin3, 2026-10-22 (rev 2 + the kit branch). DESIGN ONLY: no source or test edit, no make,
no timing. Applies the panel `docs/dev/reviews/2026-10-22-r1-memfn-window-site-rev2.md` and job 581's
reading (`docs/dev/lanes/r27b_report.md` RESULT). Every code claim was re-read; where the code says more
than the panel, the code wins (`[code]`). Marks: `[rev3 <id>]`, `bB*` build, `dD*` dir, `rR*` rit.
The step rev 2 called "S3 = B1" is **S3** here (not finding bB1). Appendix B places every finding.
Rev 3.1 (uwin3, 2026-10-22): the verification critic's V1-V7 text fixes, each re-read in the code; marks `[rev3.1 V<n>]`.
Rev 3.2 (2026-10-22): main's agreement notes 1-7 (S3 bar names every slower cell, match included; both layers
reported; R-on-PARKED as a soundness fact + the RE-SEED bit; the reply owns the run pin; tie obligations; one
tie table + one reply-to-stamp table; sabotage ids); marks `[rev3.2 n<k>]`.
**Rev 3.3 (DRAFT for the manager; lane s3, 2026-10-23):** records S3 as built and the S3 code review
r1's C1 build (`docs/dev/reviews/2026-10-23-r1-memfn-s3-code.md`, findings C1, C3, C4, C7, C9, C10):
E-find, the Table E row the design did not have (§2.6); Table B asked the design's question and its
pick rendered, PAIR and the SIMD rows reachable (§2.2); Table D a kit_table (§2.5); the bar's mover
sample and foobar's layout cap (§6). Marks `[rev3.3 C<k>]`. NOT YET ACCEPTED: rev 3.2 is the design
of record until the manager accepts this revision.

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
MARGIN row), B FIND FORM (the finder's FIND slot, asked about the stop itself; its pick rendered
`[rev3.3 C1]`), C VERIFY PLAN, D RESUME (`c + 1`, or the Horspool row D-hors on a dense stop), E FRAME
(today's rows, E-find's own find-then-verify text `[rev3.3 C4]`, the floor). Floor: `generic`. Every
rule is keyed on a stated fact, never on a label `[rev3 dD2]`.

**Staging (§5):** S1+S2 land as ONE branch of six commits `[rev3 seq]`, zero movers, one `MF_SITE_ABI`
event at the last commit. **S3**: REPORT routed by default, D-hors with it; the one byte-moving step,
judged on the scalar layer against the default build (SIMD-on reported beside it), with EVERY slower cell
named and capped, all-hex dense bulk input's ~1.53x loss among them `[rev3 S3, rev3.2 n1-n2]`.

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
positions where absence truly fails; each alternative is sound alone under its entry; **R on a PARKED
alternative holds only if the matcher is re-seeded at the candidate** (a soundness FACT; the kit's rows
enforce it internally, §2, and the reply says whether its plan re-seeds, §3.5) `[rev3.1 W1, rev3.2 n3]`; each
walked offset is its OWN one-position span `[rev3 bB4]`, and walked spans are LISTED in walk-index
(ascending offset) order, which prefix_k's ties and exchange sort read (§2.1 TIE) `[rev3.2 n5]`; the run R
states its positions as facts (exact = one-member set, cube = two), never a pinned member or stretch
(§2.3 C-pin) `[rev3.2 n4]`; the pinned run R (verify NO) is stated in the RESEED alternative,
and in the PARKED one ONLY where an EXACT position of R lies at offset 0 with `DFA_PF_ONE_BYTE` and
k0 = {its byte} = F0 (today's `nsel == 0` pin clause in `pf_run_applies_common`, minus the member choice,
which is the reply's: C-pin fires only when the reply's member is that position, as today) `[rev3.2 n4]`: R's offsets count from the
match start, a parked candidate need not be one (`\b\.ab`: k0 = word bytes, R=`.ab` @0, meet empty)
`[rev3.1 V1]`; R is not stated where its NEXT rows are denied (§2.4) `[rev3.1 V2]`; a whole-item SATISFIES item wider than one byte is declined. Exactness is not a fact
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
| the DFA prefilter (PF FIND `find_site`, offset-skip `ofs_pred_of`; HYB_PF) | PARKED: `{0: k0}` (+ R only under §1.1's pin fact `[rev3.1 V1]`); RESEED (forward scan, kind != `DFA_PF_NONE`, k0 with 1-255 members, prefix_k.c's own gate; `-fno-offset-skip` undenied) `[rev3.1 V6]`: `{0: F0}` + one span per walked offset + R | as listed | `[0]` (bounded `[0, 1]` with `{1: any}`); R all; walked all | k0 YES, F0 YES, walked NO, R NO |
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
moves bytes, a basis; every cost row reads ONE cost table (§3.3). Table D is one since the S3 code review
`[rev3.3 C7]`; Table C and B's renderers (§2.2) are declared row lists read in order. The family emits a
PATH ID per site (trace build); §2.7 maps paths to old rows for the reach floors `[rev3 bB9]`.

### 2.1 Table A — the stop; adoption is its alternative half (no ADOPT table) `[rev3 dD1, dD2, bB2]`

| row | holds when | the choice | basis |
|---|---|---|---|
| A-parked | the alternative's entry is PARKED | stop = its verify-YES position (k0 at offset 0): the parked scan may skip only bytes that keep the machine parked | role A (prefix_k's comment); today's |
| A-model | the alternative's entry is RESEED | over its one-member positions at offset != 0 (the model's DOMAIN: the scan moves, as a singleton; MEASURED, §3.2), the least `model_cost` with C-model's plan; ties per the TIE table | prefix_k verbatim (§3.2) |
| A-mass | no entry fact (REPORT, pre-check parts, VM seek, MLINE) | over the core positions, the least mass; ties per the TIE table | 580/581 (REPORT); `pcrec_find_run_rank` (parts) |
| MARGIN | two alternatives stated | a RESEED alternative wins only at less than HALF the least-cost PARKED one: `best * 2 < base` (prefix_k: `best * MATERIAL_NUM >= base * MATERIAL_DEN` rejects) | §4.5's argument; ipv4's 1.5-1.6x inside the error bars |
| (none) | no core position | the floor row | — |

`base` is the PARKED alternative's cost with an EMPTY plan, `model_cost(k0 one member ? C_MEMCHR :
C_BITMAP, mass(k0), 0, 1000000)`: prefix_k prices the parked scan by k0's count, not by B's form.

**THE TIE TABLE**, the ONE place every tie rule of the family and of pcrec's statement lives; every other
section cites it (zero movers needs each; replaces rev 2's single rule, dir D5's contingency and rev 3.1's
three scattered rules `[rev3 bB2, rev3.2 n6]`):

| where the tie arises | tie goes to | code it reproduces | basis |
|---|---|---|---|
| A-mass, a position inside a stated run stretch (one-member or cube positions, C-run's grouping), incl. the run MEMBER C-pin and `@idx` read (§2.3, §3.4) | HIGHER offset | `pcrec_find_run_scan_index`/`pcrec_find_run_rank` (candidates `[n-1..0]`), `pcrec_run_pin` (exact positions listed highest first); finder P3 | today's; on REPORT literal stretches UNMEASURED DEFAULT |
| A-mass, a set position | LOWER offset | strict `<` over ascending offsets | MEASURED on REPORT: 581's PRR (rightmost) loses 1.23-1.57x on year4, 1.03-1.40x on hex8 `[rev3 581]` |
| A-model, among stop offsets of equal cost | LOWER offset | prefix_k's strict `cost < best` over `si` in walk-index order | today's; reproduces only under §1.1's walk-index listing obligation `[rev3.2 n5]` |
| C-model, verify-NO offsets of equal mass | prefix_k's exchange-sort order (unstable, declared as the algorithm, §3.2) | prefix_k's `order[]` over walk-index order | today's; same obligation |
| MARGIN, `best * 2 == base` | PARKED | prefix_k's `>=` rejects | today's |
| the truncation window (pcrec's, a limit of the statement, §9) | LEFTMOST window start | `pcrec_find_run_window_start`'s strict `<` | today's |

### 2.2 Table B — how the stop is found

Table B IS the finder's FIND slot (`fd_rows`, finder.c), asked "the next byte in set(d*) at offset d*".
The rows R8, R3a, R3b, R4, R1, R2 are KEPT UNCHANGED, inert without the knowledge they read `[rev3 bB8]`.

**The question as built `[rev3.3 C1, C3]`** (`fd_find`; S3 first built a made-up one, `fd_find_form`:
offset 0, a `table_ref` nobody stated, its decision read as LIBC or WALK only, the contracts widened):
- the SITE asked about is the window site itself under its define hooks: its consumer kind, `body`,
  `policy`, options (so `fd-d1` and the VM seek's role keep their effect); a window site states no terms,
  so the gate reads its `table_ref` as UNSTATED (its offers are `toffer`, read by C-table);
- the STOP's facts are its own: its set, its offset d* (below the candidate: a CONTEXT stop), and the
  stretch fact PAIR reads (a two-member cube inside a stated run stretch); its need is REQUIRED (B's find
  is the stop's test at every candidate it yields);
- the decision is the OFF variant's, as `fd_route`'s (the finder's §1.5 rule 1: decided once, every layer
  inherits it); the SIMD forms are the offset-skip function's PREFIX rows over PAIR's body, which read the
  site's actual `policy`;
- REPORT is served only by the rows whose pick renders a window site's stop (D1, D1c, D1w, PAIR, R7w); the
  inert rows and the PRES rows keep the native kinds (S3's KD_ALL widening reverted where no REPORT site
  asks).

| row | holds when | form | basis |
|---|---|---|---|
| R8, R3a, R3b, R4, R1, R2 | as today (iterator history, measured gaps, crossovers) | as today | as today; inert without knowledge |
| D1c | the stop lies below the candidate (re-keyed from today's `SF_CONTEXT_STOP`) `[rev3 bB7]`; one member; kinds MLINE's (DFA_ATTEMPT) and REPORT `[rev3.3 C3]` | libc back search | UNMEASURED DEFAULT (today's) |
| PAIR | today's scope: the stop is a two-member cube inside a stated run stretch (ofsskip's `fn-pair`, now a FIND-slot row); BUILT `[rev3.3 C1]`, after D1w and before R7w (its facts are disjoint from D1/D1c/D1w's) | two `memchr` streams | today's; no PAIR cost constant `[rev3 bB2]` |
| (SIMD) | `-fmemfn-simd`: vrun's PREFIX rows, over PAIR's fn-pair body (reached through B-fn, below) | today's | inert at OFF |
| D1 | one member, not the VM seek | `memchr` | UNMEASURED DEFAULT (finder.c's basis column) |
| D1w | one member, the VM seek | the table walk | UNMEASURED DEFAULT; retirement trigger §1.4 |
| R7w | every other set | the WALK (walk_vs_v1_record.md) | MEASURED (B4′) |

`[code]` rev 2 marked D1 MEASURED; finder.c says `FB_UNMEASURED_DEFAULT`. D2 and RPT retire.

**B's renderers on E-find's text `[rev3.3 C1]`** (`wf_brows`, window.c), first match over the pick and
the plan; they decide nothing about the find, and a pick none names (an unbuilt form) leaves E-find with no
text for the plan:

| row | holds when | renders |
|---|---|---|
| B-fn | PAIR, and the plan IS the offset-skip function's predicate (it translates exactly, one RUN term holding the stop's cube, the function's BODY walk takes it) | the offset-skip function (`fn-pair`'s body, `vrun`'s SIMD rows over it under `-fmemfn-simd`), called from E-find's frame: D155's seam, so the SIMD-on artifact adds only guarded rungs over the SIMD-off text |
| B-pair | PAIR | two `memchr` streams in E-find's loop, each a pending hit searched again only once C + d* passes it |
| B-memchr | LIBC (D1), LIBC_BACK (D1c) | one `memchr` in the loop; a stop below the candidate raises C first |
| B-walk | WALK (R7w, D1w) | the walk in the loop (C-table or C-own) |

**No row decides a stop of two or more members below the candidate** (D1c is one byte; R7w and PAIR
need the stop at or past it): E-find declines it, and a REPORT site's cover declines with it (the
default build's composite). A finding, not a fix: the corpus's count is in the census.

### 2.3 Table C — the verify plan

One plan object (positions in order, each with its test): the renderer walks it, `proven[]` is computed
from it, a trace build asserts rendered = plan. The text shape is the E rows'.

| step | row | rule |
|---|---|---|
| 1 merge | C-meet | positions at one offset, across spans, are ONE position with the intersection set, before grouping; empty inside a core → floor row |
| 2 select | C-yes | every verify-YES position (on a RESEED alternative: F0 at offset 0, always) |
|  | C-model | on a RESEED alternative: plus prefix_k's greedy pick among verify-NO walked offsets (§3.2, exact) |
|  | C-none | otherwise no verify-NO position (PARKED alternatives, REPORT, parts) |
| 3 pin | C-pin | `[rev3 bB1]` R becomes ONE compare (its selected offsets dropped) when R is stated (length >= 2), the stop IS R's MEMBER (the reply's: A-mass over R's exact positions, TIE table; on a PARKED alternative k0 is that one byte), and the plan does not already test all of R. The stretch is the maximal run of exact positions around the member. `[code]` narrower than the panel's "a stop inside the stretch": `pf_run_applies_common` requires EQUALITY with the scan member |
| 4 drop | C-stop | minus the stop's own position when B's set equals it, except inside a pinned stretch (C-pin keeps it whole) |
| 5 group | C-run | a maximal stretch of consecutive one-member or cube positions inside ONE stated span is one run compare; never across one-position spans, whose positions stay SEPARATE terms, including a position C-meet merged with any one-position span `[rev3.1 W2]` (`ofs_test_model`, one term per selected offset) unless C-pin made the stretch whole `[rev3 bB4, rev3.1 V3]` |
| 6 test | C-table / C-own | an offered table (pcrec's name), else the kit's own `set_test` |
| 7 order | C-asc | ascending offset (today's) |

`[code]` C-pin is a PLAN row after the choice, not a third alternative: today's `run-pinned` with
`nsel == 0` is PARKED + C-pin, rendered by the re-seeding emitter with no margin; MARGIN ignores C-pin.

**The reply is the ONE owner of the pinned run member and its stretch `[rev3.2 n4]`.** pcrec states R's
positions and offsets (§1.1); the reply names member and stretch; `@idx` and the run-pinned NEXT rows read
it (§3.4). `pcrec_run_pin`'s SELECTION (`kset.c`: PICK over the exact positions, highest first, the
stretch around it, the walk offset spelling it) retires at commit 6; readers in §4.

### 2.4 How pcrec's NEXT rows read the reply `[rev3 bB1]`

Today's NEXT predicates read the planner's PICK (`pf_ofs_applies_common`: `ofsk.nsel > 0`;
`pf_run_applies_common`: the model's scan, `ofs_test_model`). Rows 5-7 do not test `nsel`; first-match
order reaches them only when `nsel == 0`. After S2 the same rows, order and denies read the reply:

| row | today | reads instead |
|---|---|---|
| `run-pinned[-bounded]` | pin + identity + clause 4 | the reply's plan carries C-pin AND its RE-SEED bit is set (§3.5) `[rev3.2 n3]` |
| `offset-set[-bounded]` | `nsel > 0` | the reply chose the RESEED alternative (RE-SEED set) |
| rows 5-13 | `nsel == 0` by order | unchanged (the reply chose PARKED, RE-SEED clear) |

`-fno-offset-skip` keeps its identity: denied, pcrec states only the PARKED alternative (and the
run-pinned pair's deny bits remove C-pin's row from pcrec's NEXT, as today).
**A denied NEXT row's fact is not stated `[rev3.1 V2]`:** under `PCREC_NO_OFFSET_SKIP` or
`PCREC_NO_RUN_PREFILTER` (the run-pinned pair's deny bits, emit_dfa.c's `dfa_pfs[]` head) pcrec does not
state R, so no reply can carry C-pin and the OFFSETS stamp cannot show a pinned plan. C-model and
A-model never read R, so the RESEED alternative's choice is unchanged under `PCREC_NO_RUN_PREFILTER`.

### 2.5 Table D — the resume `[rev3 dD3, 581]`

A `kit_table` on `kit_walk` `[rev3.3 C7]` (window.c `wf_dtable`), asked on E-find's text only: a contract
per row (D-hors's window is a stated core), the deny `wf-hors`, trace and reach counters, a `holds` column
(D-hors: the rule below, exactly as S3 built it; no new admission predicate, the E[sh] reading decides that
later); the path id gains `+hors` where it fires.

| row | holds when | resume | basis |
|---|---|---|---|
| D-hors | the stop's set has mass >= `HORS_MIN` (~146,000 ppm) and the window is at least 2 positions | Horspool over the TESTED sets (581's HRS text): probe the window's LAST position; on a miss or a failed verify advance by `sh[b]` = least `t` with `b` in the tested set at `last - t`, else the window length. It replaces B's scan on that site | job 581, PROVISIONAL |
| D-one | always | `c + 1` | the floor (today's) |

`HORS_MIN` (§3.3) is PROVISIONAL: fit on 8 cells with ONE winner (hex8, stop mass 284,434 ppm; the next
densest 74,760 ppm), at the gap's geometric middle. Physically: with no rare stop to skip to, skip by the
window's end (the stop span's core). It is re-read at S3 at BOTH layers (G1, scalar
and SIMD-on, §6) and on any new population (S1's count, §5.2, is the first) before the row is called
measured `[rev3.2 n2]`.

D-hors moves bytes: it lands at S3 with its own deny, never at S2. D-shift stays out: 581 fits its rule,
but HRS serves hex8 and SHF's wins elsewhere are marginal.

### 2.6 Table E — the frame

| row | holds when | text |
|---|---|---|
| E-func | FUNC/RETURN, miss `n`, no expression floor | today's `static inline size_t` (D155 seam) |
| E-stmt | STMT/ASSIGN or ON_MISS | today's PF block (guard, post-test, `moved` hook, `decl_point`) |
| E-find `[rev3.3 C4]` | STMT/ASSIGN (its contract), the plan has a stop short of every byte, and Table D resumes it by D-hors or Table B decides its find and one of B's renderers renders it; deny `wf-find` | the family's own find-then-verify text: B (§2.2's renderers), C (C-yes under the hoisted bound and the three-way guard; C-run through runcmp), D (§2.5) |
| E-generic | anything else but a REPORT site | the floor row |

The legacy rows (E-func, E-stmt) come first, so every site today's rows serve keeps today's bytes; they
never translate a REPORT site (the composer refuses REPORT stated in terms). E-find comes before the floor,
so the movers are the sites the legacy rows decline that E-find renders: REPORT, and D-hors inside E-find.
E-generic declines REPORT (the floor's byte loop is COV, R-27's 10x loss), so a REPORT site E-find does not
render is REFUSED and pcrec keeps its default (`no-wf-find` is the OFF arm, the default build before S3).
E-find and the floor share the statement frame, the statement expression's head and tail and the candidate
test `[rev3.3 C9]`.

REPORT is STMT/ASSIGN: E-find, and **keeps the STMT frame** `[rev3 581]`: PRF (the FUNC twin) reads
1.03-1.09x search_short/none, 1.07-1.25x dense vs COV. Native offset-skip sites keep FUNC (zero movers).
B-fn calls the offset-skip function FROM the STMT frame (the frame stays STMT).

### 2.7 What folds where, and the path map

| row today | fate | family path id (reach floors, §5.3) |
|---|---|---|
| `pf_memchr`, `pf_memchr_bounded` | FOLD: A-parked + D1 + C-none + E-stmt | `parked-d1[-b]` |
| `pf_walk`, `pf_walk_bounded` | FOLD: A-parked + R7w + C-none + E-stmt | `parked-walk[-b]` |
| `pf_memchr_back` | FOLD: A-mass + D1c + E-stmt | `back` |
| `ofsskip` `fn-memchr` / `fn-pair` / vrun PREFIX | FOLD: A-model (+ C-pin) + D1 / PAIR / vrun + C-model + E-func | `reseed-d1`, `reseed-pair`, `reseed-vrun`, `pin-*` |
| `precheck` | STAY (ALL_PRESENT); its FUNC parts render through A-mass + C-yes | `part-*` |
| `runcmp`, `mismatch_inplace`, `generic` | STAY (C-run's compare; MISMATCH; the floor) | — |
| RPT, `kit_report_exact`, `SF_PROOF_EXACT`, `FF_PROOF`, D2 | RETIRE | `report` (S3): E-find's sites read `mass[+pin][+hors]`, the FIND slot's deciding row in the trace's `FDROUTE`/`WPATH fd=` `[rev3.3 C1]` |

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

Every stamp that reports a family choice is written from the reply, never from a pcrec-side
recomputation; phase 1 makes the reply exist before the stamp line. **THE REPLY-TO-STAMP TABLE**, the one
declared map (a row per stamp value; a stamp not listed reads no reply) `[rev3.2 n6]`:

| stamp (value) | reply field it reads | site |
|---|---|---|
| `<PREFIX>_DFA_PREFILTER` `offset-set[-bounded]` | ALTERNATIVE = RESEED (RE-SEED set) | the PF site |
| `<PREFIX>_DFA_PREFILTER` `run-pinned[-bounded]` | PLAN carries C-pin, RE-SEED set | the PF site |
| `<PREFIX>_DFA_PREFILTER_OFFSETS` | STOP offset (the `*`) and the PLAN's tested offsets, C-asc order; under C-pin every offset of the pinned stretch | the PF site, when either row above holds; else `"none"` |
| `<PREFIX>_REQ_RUN`'s `@idx` | RUN MEMBER (R's position the reply names, TIE table HIGHER) `[rev3.2 n4]` | the site stating R (the PF site's R, or the pre-check's run part: one rule over one statement, so they agree; a trace build asserts it) |

Spec hunks at commit 6: `match_api.md §6.3.1¶5a`, `tuning.md §2.14¶3`, `§2.30¶2`, `findings.md` §4's `@idx`
and pin rows. Their VALUES must not move at S2.
`[code]` `ReqRun.idx` (`pcrec_find_run_scan_index`, `req.c`) has readers outside the stamp; §9 asks.

**The `_FINDINGS` consulted line and the UNDERIVABLE/BROKEN diagnostics `[rev3 bB5]`** are raised by the
first ask of `pcrec_find_byte_rate` (findings.c), today made by askers that retire (prefix_k, the run
rank's callers). The builder that states frequencies to a family site asks it there, for exactly today's
population, so neither moves.

### 3.5 The reseed is the NEXT row form's property `[rev3.1 V4]`

The re-seed is the property of the form pcrec's NEXT row picks from the reply (`.reseeds` on the
row), NOT keyed on ENTRY: a RESEED choice re-seeds, and so does PARKED + C-pin (today's `nsel == 0`
`run-pinned`, rendered by `pf_emit_ofs`). PARKED without C-pin does not `[rev3 dD1]`.
Making it unconditional (integration.md §R4.3.5's M5′ item) would mean stating every alternative as
RESEED: a byte-moving pcrec event, filed if anyone wants it (D77).

**The RE-SEED bit `[rev3.2 n3]`.** The phase-1 reply carries RE-SEED: whether the kit's plan needs the
matcher re-seeded at each candidate (set on a RESEED choice and on any plan reading R on a PARKED
alternative, the soundness fact of §1.1). pcrec's run-pinned and offset-set NEXT keys read the bit
(§2.4); RE-SEED set reaching a non-re-seeding row is a loud refusal. The request names no kit row.

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
| RPT, `kit_report_exact`, `SF_PROOF_EXACT`, `FF_PROOF` (at S3, with the R-26.6 step below), D2 | finder.c, kit.h, compose.c, `memfn/src/CLAUDE.md`, `tests/memfn/{rows.tsv,row_floors.tsv,arm_fixtures.c,run_proof.sh,finder_check.py,run_rows.sh,proof_check.c}` |
| `plan_hint`, `plan_pos`, `rank_n/pos/ppm`, `MF_RANK_MAX` | `memfn.h`, compose.c, formhash.c, ofsskip.c, precheck.c, vrun.c, `memfn/tests/{run_g2_simd.py,g2/*}`, `known.c`, `memfn_sites.c`, `emit_dfa.c` (`ofs_pred_of`, `ofs_pred_rank`), `tests/memfn/{run_rank.sh,rank_check.py,proven_check.c,arm_fixtures.c,proof_check.c}` |
| pcrec's selection (`pcrec_prefix_ksets`' pick; the walk `kset_walk` STAYS, it is a fact) | `src/opt/prefix_k.c`, `src/core/internal.h`, `emit_dfa.c` (`ofsk`, the NEXT predicates §2.4, `ofs_test_model`), `tests/codegen/{run_offset_skip.sh,run_form_census.sh}` |
| `pcrec_run_pin`'s selection (commit 6, §2.3) `[rev3.2 n4]` | `src/facts/{kset.c,facts_derive.h,facts.c,facts.def}` (`PF_RUN_PIN`, the `run_pin` text `o`/`o:at+len`), `emit_dfa.c` (`us_run_pin`; `pf_run_applies_common`, `ofs_test_model`, `ofs_test_verifies_run`), `prefix_k.c` (comment); `--emit-facts` makes it caller-visible: `facts_listing.md §4.1.2¶7`, `tuning.md §2.30¶4`, `§2.39¶4`, `findings.md` §4; tests naming it: `tests/rxtsource`, `tests/litscan/{reqcube.rxt,gen_reqcube.py}`, `tests/endmark/b3_*.tsv`, `tests/axes/start_landing_movers.tsv`, mech S280, S285, S306 |
| ofsskip/pffind as arms | compose.c `arms[]`, precheck.c, `tests/memfn/rows.tsv`, finder.c's arm map |
| `mf_preview("R-26.6")` | stays until S3; then retires with RPT: `memfn_sites.c`, `src/core/internal.h` |

**RPT and its companions retire at S3, not S2 (the kit manager's R3, 2026-10-22).** RPT,
`kit_report_exact`, `SF_PROOF_EXACT`, `FF_PROOF` and the `"R-26.6"` preview step STAY through S2: the
preview step is accepted only while RPT names it, so deleting RPT at commit 6 would refuse every kit-proof
compile, and RPT still serves the old-field REPORT sites G2 and `proof_check.c` state. They retire at S3,
when REPORT is routed (§5.2). This table's row above, §2.7's RETIRE row and Appendix A's "kit retires" line
listed them for S2; §4's own last row already kept the preview step until S3. Recorded in
`docs/dev/lanes/wsc6_report.md`.

**The old fields at commit 6 (the kit manager's R1, 2026-10-22).** pcrec states none of them. The fields no
renderer reads are DELETED with their `site_check` rules: W0-W2, the prefix facts, `absent`/`consumable`,
`ctx`/`nctx` (with the generic row's context test), `read_floor` and `consumer`. `plan_hint`, `plan_pos`,
`rank_*`, `end_back`, `span_class` BOUNDED/CONTEXT and `need` STAY as the kit's RENDERER INTERFACE: written
only by the family's translation and by G2, never by a host, and a window site stating one is refused.
Moving that interface into a kit-internal struct is filed (trigger: the next G2 site-builder regeneration,
or a renderer change).

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
| 3 | a trace shadow comparing the family's decision with today's pick per site, over the emit_sweep corpus AND G2's GENERATED span sites `[rev3.2 n5]`: a LOCALIZER for commit 5's diffs, never the acceptance | pcrec lane |
| 4 | the two-phase ask under the lever; NEXT predicates read the reply (§2.4) | pcrec lane + kit lane |
| 5 | the lever's default flips. THE witness: emit_sweep against pre-S2 main on every arm, plus the reach floors | manager reads |
| 6 | delete the old path and old fields (`pcrec_run_pin`'s selection included); stamps read the reply (§3.4's table); spec hunks; the `MF_SITE_ABI` number (and `MF_CLASS_V` for the reply) at this commit, "next at landing" | both lanes |

### 5.2 The steps

| | S1+S2 (commits 1-6) | S3 (one commit, kit + pcrec) |
|---|---|---|
| content | the family; pcrec's builders (PF, MLINE both callers, VM hat, OFS, pre-check FUNC parts, Z2's cover site) state facts only; §4's rows retire; the stamps and the consulted line as §3.4 | REPORT routed by default (the cover site renders the family's E-stmt text); D-hors enters the default table |
| witness | G2 (generated spans vs the scalar byte loop); `proof_run` (sentinels); emit_sweep byte-identical to pre-S2 main on every arm (default, each deny, `--engine=vm`, both SIMD layers), stamps included; `tests/findings/manifests/*_movers.txt` unchanged `[rev3 rR5]`; reach floors; `REACH_ONLY=1` re-aim | the 650 harness at the SCALAR layer (§6's bar) and the SIMD-on layer (reported, §6); the answer gate; G1 on every non-REPORT site D-hors moves (emit_sweep's diff names them) |
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

## 6. S3's acceptance, and hex8 `[rev3 S3, dD3, 581, rev3.2 n1-n2]`

The kit manager's ruling (panel §2; Frank on hex8: "make the judgement call ... we need this regardless
of where hex lands"), as main agreed it:
- **Layers.** The go/no-go bar is read on the SCALAR layer, the default (`-fmemfn-simd` is OFF). The
  SIMD-on layer is ALSO measured and reported in the same reading (memfn/CLAUDE.md's G1 at both layers),
  each cell against SIMD-on DEF; a SIMD-on loss is a finding for the SIMD thread, not an S3 blocker. The
  official SIMD verdict stays pcrec-bench's (D144 add. 4). D-hors's PROVISIONAL `HORS_MIN` is re-read here
  at both layers, and on any new population (§2.5). Rev 3.1's "scalar layer only" is corrected.
- **The floor** is 581's per-cell floor(PRO) (581 supersedes 580; 580's table, `r27_report.md` §5, has no
  other cell). **The comparison is DEF**; COV is a design check (cat-bounded search_short/dense: PRO/DEF
  0.404, 1.18 only vs COV). **Routed form:** D-hors fires on hex8 alone (284,434 ppm; next 74,760): HRS
  there, PRO elsewhere.

**EVERY cell where the routed form is slower than DEF beyond its floor**, all regimes (`match`
included), from the 581 table; each is capped at its measured ratio plus its floor:

| cell | routed form | 581 ratio / DEF | floor | cap | reason |
|---|---|---|---|---|---|
| hex8-bounded throughput/dense | HRS | 1.531 | 0.020 | 1.551 | an all-hex subject has no rare stop; every form loses (PRO 1.412, SHF 1.378, COV 1.322); HRS routes hex8 for its 2-6x wins (throughput real 0.458, none 0.490; search_short real 0.523, none 0.173) |
| hex8-bounded search_short/dense | HRS | 1.139 | 0.020 | 1.159 | the same subject; PRO 1.132, COV 1.184 |
| file-ext-order search_short/none | PRO | 1.033 | 0.020 | 1.053 | literal `.` stop on a no-hit short subject; one bounded effort (PRF, the FUNC twin) read worse at 1.094; accepted (one-pass rule) |
| file-ext-order match/real | PRO | 1.039 | 0.020 | 1.059 | `match` regime (T9), reproduced from 580 (1.043); cause not diagnosed; accepted under the same one-pass rule |
| file-ext-order match/none | PRO | 1.065 | 0.020 | 1.085 | the same (580: 1.057) |

Cells reading S inside their floor (foobar throughput/none PRO 1.011, hex8 match/real HRS 1.011) are not
named; the bar holds them at the floor like every other cell.

**Users WILL see about 1.53x slower on all-hex dense bulk input**, because D-hors routes hex8 to HRS. This
is accepted for the 2-6x wins on real and no-hit text (Frank: "we need this regardless of where hex
lands"; the kit's judgement call), and it is stated in the S2 request (Appendix A).

S3's go: zero answer changes; on the scalar layer every `real`/`none`/`dense` cell of every regime
(throughput, search_short, match) not slower than DEF beyond its floor(PRO), the five named cells within
their caps; G1 green on D-hors's non-REPORT movers; the SIMD-on reading reported.

**Rev 3.3 additions to the bar `[rev3.3 C10]`** (main agreed, 2026-10-23):
- **foobar match/real**, a LAYOUT cap at 1.052 (job 605's 1.032 plus its floor 0.020): `rx_match` is
  byte-identical between the arms and its placement moved (s3_report.md §6.2);
- **the mover sample is part of the bar**: job 588's 24 stratified cover movers (`sample_588.tsv`), DEF
  vs routed at the scalar layer, NO STRATUM SLOWER THAN DEF BEYOND ITS FLOOR (its cells' geometric-mean
  ratio within 1 + this run's A/A), every sample row and cell printed PASS/FAIL, a dropped row a FAIL;
  the SIMD layer reported. This rewords main's R-27.1
bar ("`dense` not slower than COV"); main AGREED (rev 3.2). In family terms, 581's PRO = A-mass + B + C-yes
+ D-one + E-stmt and HRS = PRO with D-hors.

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
   them). S3: R-27.1's regime (650 harness, three regimes x three classes, SCALAR for the bar and SIMD-on reported, Linux, pinned, 581's
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
core position); 581 settles the LEFTMOST tie on set positions and the STMT frame for REPORT. Main AGREED
rev 3.1's three leanings (rev 3.2) `[rev3.2 n1, n4]`:
- **The S3 bar** (§6): DEF the user-facing comparison, every slower cell named and capped, `match` included.
- **`<PREFIX>_REQ_RUN`'s `@idx`** reads the reply (§3.4's table), at commit 6 with the `findings.md` hunk;
  the reply is the ONE owner of the pinned member and its stretch, `pcrec_run_pin`'s selection retires (§2.3).
- **The run truncation window** (`pcrec_find_run_window_start`, ties LEFTMOST, TIE table) stays pcrec's at
  S2, a limit of the statement like the proof range; revisit when a span longer than
  `PCREC_MAX_REQ_RUN_EMIT` is stated.

**OPEN, for main `[rev3.2 n4]`:** `ReqRun.idx` (pcrec's scan index, the same rule as the reply's member)
has readers beyond `@idx`: `<PREFIX>_REQ_BYTE` (`pcrec_req_pick`), the truncation window, the
`[OPT-REQPOS]` comment, `req_set_leads_own`, the pick shadow. Zero movers at S2, but two choosers of one
value. Leaning: where a family site states R they read the reply (commit 6); the truncation window, and
artifacts where no site states R, keep pcrec's index as a fact of the statement.

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
> truly fails; each alternative is sound alone under its entry; R on a PARKED alternative holds only if
> the matcher is re-seeded at the candidate; each walked offset is its own one-position span, the walked
> spans listed in walk-index (ascending offset) order; the run R is stated as its positions (exact or
> cube) and offsets, never a chosen member or stretch; the pinned run R (verify NO) is stated in the RESEED alternative, and in the
> PARKED one only where an exact position of R is at offset 0, the filter is one byte and k0 = F0 =
> {R's byte there} (a parked candidate is otherwise not a match start). Under the deny bits
> `PCREC_NO_OFFSET_SKIP` or `PCREC_NO_RUN_PREFILTER`, pcrec does not state R at all.
>
> pcrec stops stating `plan_hint`, `plan_pos`, `rank_*`, `ctx[]`, `absent`, `consumable`,
> `consumable_len`, `exact_len`, `prefix_stated`, `span_class` BOUNDED/CONTEXT, `read_floor`, W0-W2,
> `end_back`, per-term `need`, `consumer` and REPORT's kind meaning.
>
> **What pcrec needs back:** (phase 1, no text) the chosen alternative, the stop (offset and set), the
> positions the plan tests, whether the pinned run is compared whole, the run's member and stretch where
> R is stated, and a RE-SEED bit (whether the plan needs the matcher re-seeded at each candidate);
> (phase 2) the C text in the stated frame and the proof class as today. pcrec's NEXT rows and the
> `DFA_PREFILTER`, `_OFFSETS` and `REQ_RUN` `@idx` stamps read the phase-1 reply (window_site.md §3.4's
> table); the reply is the only owner of the pinned run member and its stretch.
>
> **The kit retires `[rev3 rR7]`:** RPT, `kit_report_exact`, `SF_PROOF_EXACT`, `FF_PROOF`, D2, ofsskip
> and pffind as arms (folded), and every reader of the fields above in ofsskip.c, precheck.c and vrun.c.
>
> *(Note, the kit manager's R3, 2026-10-22: RPT, `kit_report_exact`, `SF_PROOF_EXACT` and `FF_PROOF`
> retire at S3, when REPORT is routed, with the `"R-26.6"` preview step (§4); D2 retired at S2.)*
>
> **Landing bar** (window_site.md §5): one branch of six commits, one landing; zero movers on every
> emit_sweep arm, stamps included; the findings mover manifests unchanged; reach floors met; every deny
> keeps its identity, the `memfn` floor stays 12; one `MF_SITE_ABI` (and `MF_CLASS_V`) event, numbered at
> landing; the derived sabotage list green.
>
> **Not asked:** any method. How the kit picks, plans, finds or resumes is the kit's (D157).
>
> **Sequencing:** after B4′; S3 (REPORT routed, D-hors) follows as its own byte-moving event, judged on
> the scalar layer against the default build with every slower cell named and capped (window_site.md §6),
> the SIMD-on layer reported beside it. Users WILL see about 1.53x slower on all-hex dense bulk input
> (D-hors routes hex8 to HRS), accepted for the 2-6x wins on real and no-hit text.
>
> **Sabotage ids:** kit-side S1400-S1429 (30 ids, ALLOCATED by main to D172 S2; dd10 holds S1336-S1345,
> S1386-S1393 are taken, R-28 holds S1430-S1439); pcrec-side
> from main's ledger above the highest id on main and in worktrees at filing. The Z2 cover rows that exist are S1130-S1141, S1144,
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

**The rev-3 verification critic (rev 3.1):** V1 §1.1, §1.2 PF row, Appendix A; V2 §1.1, §2.4,
Appendix A; V3 §2.3 C-run; V4 §3.5; V5 §9; V6 §1.2 PF row; V7 Appendix A (range S1400-S1429).

**Main's agreement notes (rev 3.2):** n1 §6 (every slower cell, `match` included; the 1.53x statement),
Appendix A; n2 §6, §2.5, §5.2, §8; n3 §1.1, §2.4, §3.5 (RE-SEED bit), Appendix A; n4 §2.3, §3.4, §4, §5.1
commit 6, §9, Appendix A; n5 §1.1, §2.1 TIE, §5.1 commit 3; n6 §2.1 TIE table, §3.4 reply-to-stamp table;
n7 Appendix A.

**The r2 panel (2026-10-21) and the kit manager's rulings, as they stand in rev 3:** P1 §5.1; P2
superseded by kit-mgr 1 (§3); P3 §1.4; P4 §2.3; P5 §2.1 tie column, §2.2 (REGIME gone), §2.5 (D-shift
out); P6 §2.2 PAIR; P7 §1.1; G1 dissolved (§5.1 commit 3 is a localizer, not a comparator); G2 §2.3
C-stop/C-pin; G3 §2.7, §2.4; G4 §3.4; G5 §5.3; G6 §5.4; G7 §5.1 commit 6; G8 Appendix A; G9 superseded
by P1; G10 §5.1, §4; F1 §1.1; F2 §1.3; F3 §1.1-§1.2; F4 §2 (B's clamped start); F5 §1.4, §5.2; F6 §1.1;
F7a-e §1.2, §0, §2.3, §2.5; Q1-Q5 §9; U1-U7 unchanged as filed; kit-mgr 1 §3, §2.1; kit-mgr 2 §3.4;
kit-mgr 3 §2.5, §6 (581 applied); kit-mgr 4-5 §5, Appendix A.
