# R17-b′ — the kit's first candidate-finder delivery: one table over (stop, form), one window request, zero movers first

**Revision 2 (2026-10-14), lane r17bp3, design only.** Branch `lane/memfn-r17bp3`, cut
from the kit branch `lane/memfn-r17` (`aea223614`). Revision 1 is commit `830bbce39`
(lane r17bp); text below marked `[rev2]` is new or changed in this revision, and
everything unmarked is carried from revision 1. Nothing under `src/`, `memfn/src/`,
`tests/` or `lib/` changes. No timing was run; no measured constant enters any source.
The compile-only instruments of revision 1 stay in `r17b_prime/` (own CLAUDE.md).

`[rev2]` **The baseline is MAIN.** The kit branch carries R17-a (MF_SITE_ABI 11) and
R17-b (MF_SITE_ABI 12, pcrec abi 77 on that branch); main (abi 78, MF_SITE_ABI 10)
has neither, and the kit branch's merge into main was aborted at 17 conflicts
(winreq Q-WR-10). The R17-b′ BUILD is cut fresh from main, so every step below is
stated against main's code: R17-a's seam and R17-b's form are PORTED as steps of this
plan, not presumed (§3).

Labels: **MEASURED** (read from a row or a counter), **DERIVED** (follows from a
measured value or from the form's text), **INTERPRETATION** (my inference),
**PROPOSED** (this note's design, for review), **RULED** (a decision of record).

How to read it: §0 first, then §R2 (what moved and why), then §1 (the table) and §3
(the step plan). §4 is the contract, §5 the measurements and the grid2 slot.

---

## 0. Answers first `[rev2]`

1. **Scope (§1.1).** One delivery covers every FIND site that searches for a match's
   START plus the presence pre-checks and handoffs that front it, all stated as ONE
   window request per search entry (D161 add. 14 and its clarification):
   - the set FIND sites (R-17): the DFA prefilter (`byte-class[-bounded]`), the DFA
     hat (`first-class-bounded`), the hybrid's inner prefilter, the VM hat
     (`first-class`, |S| = 1 included);
   - the one-byte stops (D161 add. 14): the DFA prefilter's `memchr[-bounded]`, the DFA
     hat's `first-memchr-bounded`, the hybrid's, and MLINE's `(?m)^` back FIND
     (Q-WR-2: in scope);
   - the presence pre-checks (`REQ_BYTE`, `REQ_RUN`, set-leads, K65 set-rest, K66
     whole run) and the K82/L1 handoff (FIRST and the NEXT re-entry), merged with the
     find they front.

   Out: OFS/run-pinned FUNCs (multi-position spans, R-18), the ADVANCE/VERIFY/
   MISMATCH sites, the compound route.
2. **The table (§1).** ONE declared first-match table `fd_rows[]` with a SLOT column,
   **21 rows**: 15 in slot FIND (the candidate stream's form for span 0) and 6 in slot
   PRES (each presence span: keep, drop, order, which member). Every row has `needs`
   (knowledge keys P/N/M/E/H/A/I), a condition over set references, a pick, an
   `unpaid` fallback and a deny. 18 rows are built by B4 and LOCKED there; F0 (NONE),
   F1 (a measured libc row) and P1 (the priced pre-scan) are designed now and added
   after lockdown as formal edits at B5. The no-data DEFAULT rows are exactly Q-WR-1's: D1
   (one member, not a VM attempt seek → the libc row, labelled UNMEASURED-DEFAULT)
   and R7 (LINER for every other cover). PRES's default is KEEP (Q-WR-9). NONE is a
   row that never applies where span 0 is REQUIRED (the VM hat, the no-DFA VM route).
3. **The step plan (§3).** Nine build steps B0-B8 plus the evaluator's E-steps,
   in one order:

   | step | what | zero-mover? | pcrec abi |
   |---|---|---|---|
   | B0 | port R17-a's seam to main | yes (proven on the kit branch) | none |
   | B1 | ST1 + R-19 + R-20 (kit half) + E3: facts, table, pick function, trace-only shadow | yes (nothing routed) | none |
   | B2 | ST2: one-byte FIND rows routed | yes (the default rows ARE today's rule) | none |
   | B3 | ST3: presence + handoff merged and routed (after E-1) | yes (five priced picks ported verbatim under a shadow) | none of its own (E-1 is window_contract's S1 event) |
   | — | **first delivery COMPLETE**; then grid2 → E4b → E5-E8 judge → LOCKDOWN | | |
   | B4 | R17-b′'s set-site ROUTING (LINER V1, R0 WALK), M0's stamp, the kit size rung | NO: the one censused mover | ONE event, 78 → next |
   | B5 | ST4: measured rows (libc, NONE, priced pre-scan), one census each | NO | one per default-moving row |
   | B6 | the W64 SIMD rows (CANDIDATE) | SIMD-off yes | none |
   | B7 | ST5: the libc class deny + three libc-free rows | yes at default | none |
   | B8 | ST6: the N-dispatch rows, if not already paid at B4 | NO | one |

   R17-b″ (D165 iterator) follows as B9 (§6).
4. **The contract (§4).** One `mf_site` per search entry holds span 0 (`pred`) and
   PRESENCE spans (`preds[]`, a new span class with `omin` and no `omax`, C-1/C-2).
   Presence binds at RANGE level, once per activation: a REQUIRED presence span absent
   from `[start + omin, n)` (`omin` measured from the match start, `start` R-19's hook)
   makes the stream EMPTY, and EMPTY = NOMATCH, decided before the first element (C-3,
   G-1, G-2). An unconstrained reply is the range `[lo, n)`, legal iff span 0 is
   OPTIONAL or absent (G-4); the per-candidate cut `hi' = p − omin + head_max` is a
   PERMISSION exercised only by the iterator (Q-WR-6). The kit reports, at
   `mf_define`, the PROVEN facts (D161 add. 8) as `mf_result.proven0` +
   `scan_exists` + `includes` + `pres_kept`, and each of pcrec's six readers maps to
   one of those kinds (no per-form read-back). The K65 obligation is a per-consumer
   table keyed by `need` (§4.6). The set arrives on `mf_art_begin` (`mf_measures`,
   R-MS1) and `consulted` comes back from `mf_art_end` (R-MS2).
5. **Measurements (§5).** 23 quantity families keyed (owner.quantity, form, site
   kind, shape), relative to u = β_walk. grid1 holds 15 (M1-M15). ABSENT: the three
   dispatch charges (M16-M18), the one-byte libc and libc-free costs and their
   crossover (M19-M21), NONE's effort (M22), the pre-scan gate's quantities (M23).
   Each has a method card row under `kit-grid@2` (R-MS5).
6. **zen4-grid2 (§5.4): ONE slot, ~88 min required + ~8 min optional ≈ 96 min**
   (plus quiet-gate waits): the 149 fit groups STREAMED (regime_eval's in-sample
   reference, ~56 min, and under Q-R17P-9's recommendation also the set's constant
   rows), the dispatch twins (~5 min), the one-byte and NONE arms (~17 min), the
   build and answer gate (~10 min); optional: the F2 perf passes (~6 min) and a
   pre-scan trigger probe (~2 min). Perf is never required (D166 add. 1); without
   counters every script prints the paranoid SUGGESTION (add. 1.1) and skips loudly.
7. **R17-b″'s seam (§6).** H rows (R3a, R3b, R4 and R8 under H), the form A3, the
   presence carry (`valid_until`, 8 B) and Q-WR-6's cut-off as a permission; the
   kit's state row grows 32 → 40 B. `findall_iter.md`'s S then reads 48 B if pcrec's
   K5 pair-hit row retires into the kit's carry, 64 B if not (Q-R17P-10).
8. **Questions (§7).** Rev 1's Q-R17P-1..8 are CLOSED with their rulings. Six new
   ones, Q-R17P-9..14, each with a recommendation: grid2's fit condition (9), S (10),
   the landmark admission's owner (11), the PF comment's `-fcomments` move (12),
   whether zero-mover routing may precede the judge (13), and the `libc:` dependency
   owner for measure_sets (14).

---

## R2. What revision 2 changed, by input `[rev2]`

| input | what it changed | where |
|---|---|---|
| main is the baseline (Q-WR-10) | R17-a and R17-b are PORTED steps (B0, B4), not presumed; MF_SITE_ABI renumbered from main's 10 | §3 |
| D161 add. 14 + clarification | scope adds the one-byte stops, MLINE, presence and handoff; ONE window request; EMPTY = NOMATCH; the K65 obligation | §1.1, §4 |
| D161 add. 15 (Q-WR-1/2/3/6/9) | default rows D1/R7; MLINE in scope, no NONE until measured; D158 single rule with the ST3 no-move posture; the cut-off as a permission; pre-scan default KEEP | §1.3, §1.4, §4.6, §6 |
| D161 add. 11/12/13 | one table over (stop, form) with slots; generic class only at M2; row edits free until lockdown, lockdown = B4 | §1, §3.3 |
| D161 add. 8/10 | proven facts as the read-back channel; verify/proof only on EXACT spans; rows that change a proven fact decide once per site, never per layer | §1.5, §4.5 |
| D166 + add. 1/1.1/2 | every threshold a set reference; latest set until M2; stale defaults carried; perf optional and the paranoid suggestion | §5 |
| R-19 | `mf_site.body`, the START hook (all FIND storage points and the PRE composite's entry) | §4.2 |
| R-20 (R-MS1..5) | `mf_measures` in, `consulted` out, `mf_form_hash`, the reader declarations (with the `--emit-facts` section `memfn`), method cards `kit-grid@N`; `--list-finder` WITHDRAWN | §4.7, §1.7, §5 |
| R-21 (PR-1..11, ST1-ST6, S964-S980) | every PR item placed in a step; the step plan; sabotage remapped | §3, §8.3 |
| winreq KW-1..13, C-1..16 | rows (KW-1/2/13), contract (C-items cited per piece) | §1, §4 |
| sbscope / pcscope | the consumer table; witnesses W1-W4 as sabotage witnesses; G-1..G-5; census | §4.6, §8.3 |
| regime_eval rev 2.2 | E3 = B1's table + denies + shadow; E4 agreement check; grid2's streamed fit cells; routing only after PASS (Q-REVAL-11) | §3, §5.4 |
| regime_tables rev 0.5 | R8 (needs E), R3 PROVISIONAL, A = set id and I = ISA as separate keys | §1.3 |
| finder_history.md | the table's row edits; this revision's edits logged there at build | §1.8 |
| measure_sets rev 2.1 | §1's TSV shape for the set; §2.4 staleness; §3.5 stamp spelling (`""` / `id@rev:digest16`); §4 channel; §10.1 M0 riding R17-b′ | §4.7, §5 |
| findall_iter.md | S is derived by a row sum (56 B today); the kit's row 32 → 40 | §6 |
| main's answers to rev 1 | Q-R17P-1..8 closed | §7.1 |

Rev 1 sections that SURVIVE with edits: the C shape (§1.2), the dispatch text and the
pay rule (§2), the size twins (§3.6), the G2 families (§8.2), acceptance (§9).
WITHDRAWN: `--list-finder` (R-MS4's listing replaces it), the `"none"` stamp spelling
(measure_sets §3.5), "the first set needs grid2 before anything ships" (the first
delivery reads no set, §3.2), the `FS_SPAN0`-only stop (the PRES slot adds presence
spans), SB1-SB12 as numbered in rev 1 (remapped to S911-S922 in §8.3).

---

## 1. The table: scope and rows

### 1.1 Scope `[rev2]`

The first delivery covers every site at which an artifact asks "where can the next match
START", and the presence pre-checks and handoffs that front such a site. On main
(abi 78, MF_SITE_ABI 10) these are three DELEG_SITES rows (`PF`, `MLINE`, `PRE`) at
five kinds of consumer. Populations are artifact counts (one artifact can be in several
classes), from sbscope §7.1 (main `711cf603a`, `--features all`, default flags) and
pcscope §7 (main `4e6464777`, trace build); re-counted at each step's census.

| group | today's selection (pcrec row → kit row on main) | DELEG | consumer kind (§4.3) | corpus / bench / rwquest |
|---|---|---|---|---|
| one-byte DFA prefilter | `memchr`, `memchr-bounded` → `pf_memchr`, `pf_memchr_bounded` | PF | DFA_SCAN | 581 / 35 / 16 (with the DFA hat's one-byte row) |
| one-byte DFA hat | `first-memchr-bounded` → `pf_memchr_bounded` + pcrec's re-seed | PF | DFA_HAT | (in the row above) |
| one-byte hybrid prefilter | the same rows inside a VM hybrid | PF | HYB_PF | 626 / 8 / 18 |
| set DFA prefilter / DFA hat | `byte-class[-bounded]`, `first-class-bounded` → `pf_walk[_bounded]` | PF | DFA_SCAN / DFA_HAT | 764 / 102 / 29 |
| set hybrid prefilter | the same, inside a hybrid | PF | HYB_PF | 241 / 16 / 8 |
| VM hat, any \|S\| | `first-class` → `pf_walk` (a table walk even at \|S\| = 1, Q-R5) | PF | VM_ATTEMPT | 257 / 17 / 5 (of which \|S\| = 1: 112 / 8 / 1) |
| MLINE | `pred-memchr` → `pf_memchr_back` (LOOP_EXIT `on_miss`) | MLINE | ATTEMPT_PRED | 52 / 2 / 23 |
| presence: one byte | REQ admission `emitted` → `precheck` | PRE | the route's (DFA_SCAN, HYB_PF or VM_ATTEMPT) | 292 corpus default (160 give-up-exposed) |
| presence: run window / K66 whole run | `emitted` (+ K66) → `precheck` | PRE | " | 52 (12) / 4 (4) |
| presence: K65 set rest | `emitted` on a no-DFA route → `precheck`'s `rq_set` loop | PRE | VM_ATTEMPT | 67 (67) |
| presence: set-leads | `set-leads` (bit 45) → `precheck`'s pair arm | PRE | " | 5 (5) |
| handoff FIRST (K82/L1) | `req-use` `handoff` → `precheck_assign` / `precheck_assign_byte` | PRE | the route's | 225 entry-only + 117 re-entered (corpus default); rwquest 56 |
| handoff NEXT re-entry | `cand_rows` NEXT `handoff` → the PRE site's second use | PRE | DFA_SCAN | (in the row above) |

Not in this delivery, each with its reason:
- **OFS / run-pinned FUNCs** (`offset-set*`, `run-pinned*`; 349 / 69 / 38 DFA): a span
  over positions 0..k is a multi-position span, R-18's first consumer. Their BODY is
  already the kit's (`fn_rows[]`) and stays so.
- **ADVANCE, VERIFY, MISMATCH sites** (STAY, EDGE, VMSPAN, VMSTRIDE, VMRUN, N7): not
  start searches.
- **The compound route** (`REQ_WHY "compound"`, 48 corpus): its parts are compiled by the
  unchanged pipeline and inherit whatever this delivery does to each part (D163); the
  controller itself holds no search site.
- **Withheld presence** (Q-WR-4, ruled): the G2-declined linear one-attempt (268 corpus
  default) and LOCATE `whole` (166 of G1's "dominators") get NO presence span; pcrec's
  sub-problem choice (D161 add. 4), zero-mover either way.

`[rev2]` **What "one window request" means here.** Today a search entry asks the kit
twice: once at the entry (the PRE site's pre-check) and once in the loop (the PF/VM-hat
FIND). Under D161 add. 14's clarification it asks ONCE: one `mf_site` per search entry
whose span 0 is the candidate set and whose PRESENCE spans are the necessary bytes and
runs, with several USES (the entry use decides presence and may yield the first
candidate; each loop use yields the next; the handoff's re-entry is a further use).
A site with no candidate set (a no-DFA VM route without a VM hat) is presence-only; a
site with no presence span is find-only. One site, one handle (`mf_locals`), so D165's
"one stateful site per search path" holds by construction (rev 1 F1's count stays true).

### 1.2 The C shape (PROPOSED; `memfn/src/finder.c`, `finder.h`) `[rev2: slot, kinds, I]`

```c
/* The knowledge keys (regime_tables.md §2, rev 0.5). A row's `needs` names the
 * keys its condition reads. KN_COMPILE keys are known when the site is defined;
 * KN_N at the storage point; KN_H only inside an iterator body (R17-b''). */
enum { KN_P = 1u << 0, KN_E = 1u << 1, KN_A = 1u << 2,   /* A: the measurement SET */
       KN_I = 1u << 3,                                     /* I: ISA availability    */
       KN_M = 1u << 4,                                     /* fixed per entry body   */
       KN_N = 1u << 5, KN_H = 1u << 6 };
#define KN_COMPILE (KN_P | KN_E | KN_A | KN_I | KN_M)

/* Which question a row answers (the house's cand_rows[] shape: one table, slots). */
typedef enum { FD_FIND, FD_PRES } fd_slot;

/* The layer a row applies under. A SIMD-on artifact evaluates the table once per
 * variant it renders (the floor body OFF, then W16, W32). */
enum { FL_OFF = 1u << 0, FL_W16 = 1u << 1, FL_W32 = 1u << 2 };

/* The consumer kinds (§4.3), a categorical fact pcrec states (R-21 PR-3). */
typedef enum { FK_UNSTATED = 0, FK_DFA_SCAN, FK_DFA_HAT, FK_HYB_PF,
               FK_VM_ATTEMPT, FK_ATTEMPT_PRED, FK_ANY } fd_kind;

typedef enum {                       /* forms; the kit's names, never pcrec's (D157) */
    FF_NONE,       /* slot FIND: no scan; the consumer runs its own loop             */
    FF_LIBC,       /* one byte: libc memchr (forward, bounded, or back), today's     */
    FF_WALK,       /* the table walk                                                  */
    FF_V1,         /* pf_terms_mask over mask8_swar (W8, SIMD-off)                   */
    FF_W64,        /* A1 at w32, S1 at w16 (B6)                                      */
    FF_RUN,        /* a RUN span: the nested fn_rows[] walk, unchanged              */
    FF_A3,         /* W64 with state in rx_iter (R17-b'')                           */
    FP_KEEP, FP_DROP, FP_PICK, FP_LEAD   /* slot PRES picks                          */
} fd_form;

/* A reference into the active measurement set (measure_sets.md §1.3: owner.quantity
 * then dimension tokens in the card's order). Resolved by the kit, never by pcrec. */
typedef struct { const char *quantity; uint8_t form, other, kind; const char *shape; } fd_ref;

typedef enum {
    FC_ALWAYS,          /* R7, R7s, D1's shape test, P9                               */
    FC_ONE_MEMBER,      /* D1/F1: |S| = 1, and not span 0 of a VM_ATTEMPT site       */
    FC_NO_SAVING,       /* R0: cover has >= 2 RANGE terms and V1's saving <= epsilon  */
    FC_DOMINATES,       /* F1: a libc-free form is no worse than libc at every
                           measured point of this kind                                */
    FC_G_BELOW, FC_G_AT_LEAST,          /* R5/R6 and F0: E (measured) vs a g* ref     */
    FC_N_BELOW, FC_N_AT_LEAST,          /* R1/R2 and R8: N vs a crossover ref         */
    FC_NEED_REQUIRED,   /* P0                                                          */
    FC_PROVEN_BY_FIND,  /* P2 (G1): span 0's proven fact covers this presence span    */
    FC_PRICED,          /* P1: expected-cost argmin over {KEEP, DROP}, measured E only */
    FC_H_SPAN_BELOW, FC_H_SPAN_IN, FC_H_POP_BELOW   /* R3a/R3b/R4, R17-b''            */
} fd_cond;

typedef struct {
    const char *id;       /* "R1": listed; cited by `evidence` and the decision record */
    fd_slot     slot;
    uint8_t     needs;    /* KN_*                                                      */
    uint8_t     layers;   /* FL_*                                                      */
    uint32_t    kinds;    /* bitset over fd_kind the row may apply to                  */
    fd_cond     cond;
    fd_ref      a, b;     /* the condition's operands (set references)                 */
    fd_form     pick;
    fd_form     unpaid;   /* the pick when a dispatch cannot pay (§2.5); FF_NONE here
                             means the row is dropped and its interval falls through   */
    const char *deny;     /* memfn/src/options.def name, or NULL                       */
    const char *evidence; /* listing text                                              */
} fd_row;
```

Notes on the shape (rev 1's, kept): this is the house first-match idiom, not a
planner; R-18's priced argmin over candidate CHAINS becomes one more `fd_cond` kind;
R7 is two rows, one per layer family, because under the floor rule a SIMD-on artifact
carries the SIMD-off body as well. `[rev2]` New: the SLOT column (one table, two
questions, `cand_rows[]`'s shape), the `kinds` column (applicability per consumer, so
the K65/G-4 exclusions are row data, not special cases), the separate I key (regime_tables
rev 0.4: A is the set, I the ISA), and the PRES picks.

### 1.3 Slot FIND: the rows `[rev2]`

Evaluated per site and per layer variant, first match (§1.5). Set references name the
quantity ids of §5.2. "Reachable at" = the first step whose data can make the condition
true on a default compile.

| # | id | needs | layers | kinds | condition (set references) | pick | unpaid | deny | reachable at |
|---|---|---|---|---|---|---|---|---|---|
| 1 | F0 `none` | P,E,A | off,w16,w32 | DFA_SCAN, DFA_HAT, HYB_PF (MLINE only once its M22 key exists, Q-WR-2) | span 0 OPTIONAL ∧ E's frequency kind MEASURED ∧ g(span 0) < `kit.gnone.<kind>.<shape>` (M22) | NONE | — | `fd-none` (PAIR, with the row at B5) | B5 (measured E + M22) |
| 2 | F1 `libc-m` | P,A | off,w16,w32 | all | \|S\| = 1 ∧ not span 0 of a VM_ATTEMPT site ∧ a libc-free one-byte form dominates libc at every measured point of this kind (`kit.f.*`, `kit.beta.*`, M19-M21) | that form | — | `fd-libc-m` (with the row at B5) | B5 (M19-M21 in the default set) |
| 3 | R0 | P,A | off | all | cover ≥ 2 RANGE terms ∧ 1 − β(V1, r2)/β(walk) ≤ ε (M3, M6) | WALK | — | `fd-r0` | B4 (routing) |
| 4 | R5 | P,E,A | w16,w32 | all | E MEASURED ∧ g < g\*(W64, kind) (M15) | WALK | — | `fd-r5` | E-1 + a measured bundle, B4 |
| 5 | R6 | P,E,A | off | all | E MEASURED ∧ g < g\*(V1, kind) (M15) — FRAGILE | WALK | — | `fd-r6` | same |
| 6 | R8 | P,N,M,E,A | w16,w32 | all | body ONESHOT ∧ N ≥ L\*(W64, kind) ∧ g ≥ g8 (gridread §6.3 D2; regime_tables rev 0.5) | W64 | V1 | `fd-r8` | B6 + measured E |
| 7 | R3a | H | w16,w32 | all | iterator ∧ previous step span < h3a | WALK | — | `fd-r3a` | R17-b″ (PROVISIONAL) |
| 8 | R3b | H | w16,w32 | all | iterator ∧ previous step span in [h3a, h3b) | A3 | — | `fd-r3b` | R17-b″ (PROVISIONAL) |
| 9 | R4 | H,P | off,w16,w32 | all | iterator ∧ block popcount says g < g\*(kind, layer) | WALK for that block | — | `fd-r4` | R17-b″ |
| 10 | R1 | P,M,N,A | off,w16,w32 | all | body ONESHOT ∧ N < xover(t, WALK), t = the terminal pick (M9; absent for t = LIBC) | WALK | — (row dropped) | `fd-ndisp` | B4 or B8 (needs M16-M18 to pay) |
| 11 | R2 | P,M,N,A | w16,w32 | all | body ONESHOT ∧ N < block(W64) (M11) | V1 | WALK | `fd-ndisp` | B6 + B8 |
| 12 | D1 `default-1b` | P | off,w16,w32 | all | \|S\| = 1 ∧ not span 0 of a VM_ATTEMPT site (UNMEASURED-DEFAULT, Q-WR-1: today's count rule) | LIBC (forward; bounded for `end_back` 1; back for ATTEMPT_PRED) | — | `fd-d1` (refused on ATTEMPT_PRED until a libc-free back row exists, Q-WR-7) | B2 |
| 13 | D2 `run` | P | off,w16,w32 | all | span 0 is a RUN term (a handoff landmark longer than one byte) | RUN (the nested `fn_rows[]` walk; its BODY/PREFIX rows and their denies unchanged) | — | none (the nested table's denies) | B3b |
| 14 | R7 | P | off | all | always (the LINER default; D162, D161 add. 12) | V1 | — | none (terminal; the FORM deny `pf-terms-mask` reaches it) | B4 |
| 15 | R7s | P,I | w16,w32 | all | the W64 form is BUILT for this level and I offers it | W64 | — (no row: the layer adds nothing, floor rule) | none (`pf-terms-w32`/`-w16` at B6) | B6 |

Notes:
- **Built when** `[rev2]`: rows 3-15 are source from B1 (the evaluator judges them; E3
  retires the Python mirror). F0 and F1 are DESIGNED here and BUILT at B5, after
  lockdown, each as a formal row addition with its replay delta and mover census
  (D161 add. 13): grid2 measures their quantities (M19-M22), so if they were source at
  B4 they would fire under grid2's default set and fold their movers into B4's census.
- **Order.** Rows needing only compile-time keys and true become the TERMINAL pick;
  N-rows above the terminal become emitted dispatch intervals (rev 1 §1.2, kept, §1.5).
  F0/F1 sit first because, when their data exists, they decide the form for every N.
  R0 sits above R1 so that a WALK terminal swallows R1's WALK interval (merge).
- **R1 reads the crossover between the interval's pick and the TERMINAL** `[rev2]`:
  `xover(t, WALK)`. Rev 1 read `xover(V1, WALK)` regardless of the terminal; under D1
  the terminal of a one-member site is LIBC, `kit.xover.LIBC.WALK` is not in grid1, so
  R1 is skipped there and the one-byte sites stay zero-mover even after grid2 pays the
  set sites' dispatch. One general rule, no one-byte special case.
- **D1 is a DEFAULT row, not evidence** (D149, `pcrec-no-silent-defaults`): its
  listing text reads `UNMEASURED-DEFAULT: today's count rule (Q-WR-1)`. It is replaced
  only by F1 firing on measured rows (a censused mover at B5), never edited in place.
- **D1 excludes the VM hat's seek** (span 0 of a VM_ATTEMPT site) because Q-R5 measured
  memchr per failed attempt at ×0.6 at 80% density; that is today's rule
  (`cand_derive`'s `use_memchr` plus the VM hat's table). The VM hat at \|S\| = 1
  therefore falls to R7 (V1 one-term cover) at B4, which is R17-b's own move there
  (112 / 8 / 1). A PRESENCE span on a VM route is not a per-attempt seek (one FIND of
  its first occurrence per activation), so D1 applies to it and renders today's
  `memchr`. The exclusion is a predicate on the span's role, not on the route.
- **MLINE's row is D1's back case.** It has no NONE row (Q-WR-2: F0's MLINE key is
  never written until a measurement is ruled in) and no libc-free row (the generic row
  never serves LOOP_EXIT, Q-R7-3), so `fd-d1` on an ATTEMPT_PRED site is a NAMED REFUSAL
  until B7 builds the back FIND row (D161 add. 14 point 4).
- **NONE never applies where span 0 is REQUIRED**: the VM hat and the no-DFA VM route
  state span 0 REQUIRED (PR-4, §4.6), and F0's applicability excludes those kinds
  structurally besides (C-12, C-13). An unconstrained reply there turns answers into
  `frames` give-ups (pcscope W3, GIVEUP1 F5).
- **Rows R5/R6/R8/F0 read E only at MEASURED provenance** (D162 add. 3, C-15). The
  frequency kind is always present after E-1 (D162 add. 2) but carries
  `prior-authored`/`prior-none` on a default compile, so these rows skip there.

### 1.4 Slot PRES: the rows `[rev2]`

Evaluated once per PRESENCE span of a site (§4.1), after slot FIND (P2 reads FIND's
proven fact, a declared cross-slot read, `cand_rows[]`'s `reads` precedent). The picks
are KEEP (verify over `[start + omin, n)` before the first element, §4.1), DROP (send no test),
PICK (keep only the chosen member of a set, or the chosen window of a run) and LEAD (an
ORDER: this span is tested before the run).

| # | id | needs | kinds | condition | pick | unpaid | deny | reachable at |
|---|---|---|---|---|---|---|---|---|
| 1 | P0 `required` | P | all | the span's `need` is REQUIRED | KEEP, every member and the WHOLE run (K65, K66), before the first element (G-1, G-2) | — | none: undeniable (a deny would let a budgeted engine give up where today answers, D158) | B3b |
| 2 | P1 `priced` | P,E,A,N,M | all | `need` OPTIONAL ∧ E MEASURED ∧ the set has the gate's quantities (M23) | argmin {KEEP, DROP} by expected cost | KEEP | `fd-pres-priced` (with the row) | B5, and only once Q-WR-9's trigger fires (a TUG cell measured losing for want of it) |
| 3 | P2 `dominated` (G1, ported) | P,E | all | `need` OPTIONAL ∧ span 0's PROVEN fact covers this span (identity; `run_verified`; or the density conjunct read from the frequency kind, prior included: a default row, not evidence) | DROP | — | `fd-pres-g1` | B3b |
| 4 | P3 `pick` (ported) | P,E | all | `need` OPTIONAL ∧ the span is one member of a necessary set, or the window of a run | PICK: the rarest member by the frequency kind, ties to the higher PATTERN ORDER (PR-7); the run's scan index / window start | — | `fd-pres-pick` (deny = keep every member) | B3b |
| 5 | P4 `set-leads` (ported) | P,E | all | the set's pick is strictly rarer than the run's scan member | LEAD | — | `pres-set-lead` (replaces pcrec's `-fno-req-set-lead`, bit 45, in the SAME commit: KW-11, Q-WR-12) | B3b |
| 6 | P9 `default` | P | all | always | KEEP (Q-WR-9: the total default) | — | none | B3b |

Notes:
- **These are pcrec's five priced picks, ported verbatim** (KW-8): the set pick (P3,
  with member order), the run scan index / window start (P3), set-leads (P4), G1 (P2:
  identity / `run_verified` / density). The fifth, the landmark admission
  (`req_landmark_admits`), is NOT a kit row: under framing (a) (Q-WR-5, ruled) it chooses
  the ORIGIN, which is pcrec's only choice (D161 add. 9). The kit computes it in the
  shadow only, as evidence for framing (b) (Q-R17P-11).
- **The ported rows read the frequency kind at any provenance.** They are the total
  default reproducing today (D162 ruling 2), which is why ST3 needs E-1 first: with a
  NULL analysis they would read nothing and move bytes (pcscope §5). Only P1 is an
  evidence row (C-15).
- **P1 is DESIGNED, not built** until Q-WR-9's trigger fires; it lands at B5 as a
  formal row addition. The locked PRES slot is P0, P2, P3, P4, P9.
- **P0 before P2/P3.** A REQUIRED span is never dropped or narrowed (the applicability
  rule, KW-6/C-9): on a no-DFA route every member and the whole run are verified, which
  is K65 fix (a) and K66 as row data.
- **What the kit still owns under P0** is the FORM of each kept test: a kept presence
  span is a FIND of its first occurrence over `[start + omin, n)`, and that FIND's form
  comes from slot FIND's rows evaluated for the span's shape (D1 for one byte, D2 for a
  run). One form table, not a second one.

### 1.5 Evaluation: one table, two times (rev 1 §1.2, with three `[rev2]` rules)

Per site, per slot, per layer variant: walk the rows; skip rows whose `layers` or `kinds`
exclude the variant; skip rows whose `needs` are unavailable (E absent or prior-only for
an evidence row, H outside an iterator, M unstated, a set reference ABSENT); a
compile-time row that holds is the terminal; an N-row becomes an emitted dispatch
interval; adjacent same-pick intervals merge; each dispatch interval must pay (§2.5) or
take its `unpaid`; one surviving form means no dispatch at all.

`[rev2]` Three rules this revision adds:
1. **Proven facts are decided once per site, at layer OFF.** A row whose pick changes
   what the site PROVES (F0 NONE proves nothing; LIBC proves byte b at offset 0; WALK and
   V1 prove S at offset 0; PRES DROP removes a verdict) is decided at the OFF variant,
   and the W16/W32 variants inherit that decision. They may pick a different form only
   among forms with the same proven fact. DERIVED from D161 add. 8 (the proof is the
   site's statement, identical in every layer) and the floor rule (a SIMD-on artifact is
   the SIMD-off one plus guarded text, so pcrec's own text, which reads the proof,
   cannot differ by layer).
2. **A span whose byte form is a SUPERSET** (D161 add. 10: a utf8 multi-byte class
   lowered to per-position byte sets) proves only the byte sets, never the class; its
   candidates are a filter and pcrec re-checks. No row of this delivery verifies a span.
3. **Totality.** NULL `mf_measures`, an unknown key, a NULL analysis and every absent
   kind make the reading rows skip; the last row of each slot (R7/R7s, P9) reads nothing.
   For layer W16/W32 with no W64 form built, R7s does not apply and the variant adds no
   text (the floor rule), so a SIMD-on artifact is byte-identical to SIMD-off until B6.

### 1.6 Routing state: shadow until each step routes `[rev2]`

The table is built whole at B1 (E3) and judged whole by [REGIME-EVAL]. It must not move
a byte before the judge (Q-REVAL-11). The two are reconciled by ONE temporary declared
list, `fd_route[]`, first-match over (slot, group predicate):

| group | state at B1 | routed at |
|---|---|---|
| FIND, \|S\| = 1, kind ≠ VM_ATTEMPT (D1's population, MLINE included) | SHADOW | B2 |
| FIND, span 0 a RUN (D2: handoff landmarks) | SHADOW | B3b |
| PRES, every span | SHADOW (no presence span exists until B3a states them) | B3b |
| FIND, every other site (set covers; the VM hat at any \|S\|) | SHADOW | B4 |

- **SHADOW** renders the site's pre-table form (main's kit rows, pcrec's encoding) and,
  in the MF_TRACE build only, writes the table's (site, slot, row, form) record, zero
  bytes (regime_eval §5.3's trace-only shadow, r4ccore's I1 pattern).
- **ROUTED** renders the table's pick.
- At B4 every group is ROUTED; the list is empty and is DELETED in B4's commit. It is
  implement-then-replace's switch written as data, not a parallel table: it holds no
  pick, only which groups the one table drives yet.

### 1.7 The listings `[rev2: --list-finder WITHDRAWN]`

Rev 1 proposed a new CLI flag `--list-finder`. Withdrawn: a new CLI surface waits for
[IFACE-PUSH] (memory `pcrec-iface-push-later`), and R-20's R-MS4 already carries the
same information through existing channels:
- **The rows**: `mf_finder_rows(size_t *n)` beside `mf_options()`, read by
  [LIST-TABLES]' census in its shape (measure_sets §5.4), with each row's `needs`, the
  keys it reads and, per threshold key, its SAFE direction (`max`/`min`/`none`, R-MS4;
  directions due at M2).
- **Per artifact**: a new `--emit-facts` section `memfn` (measure_sets §4.5): per site,
  the slot, the row that fired, its pick, and for a dispatch the interval literals. It is
  an APPEND to facts_listing.md §3's section set (a D80 hunk at B1).
- **The set's provenance** is the set's own listing (`--list-measurements`, M0).

### 1.8 The row-edit log

D161 add. 13: until LOCKDOWN (B4, §3.3) row edits are free and logged in
`memfn/docs/finder_history.md`; this revision's edits (F0, F1, D1, D2, the PRES slot,
R1's terminal-relative key) are logged there at B1's build, since that is when the
rows become source. regime_tables.md mirrors the FIND slot; the PRES slot is not a
regime row (it is not judged by [REGIME-EVAL]'s grid) and needs no mirror there.

---

## 2. The emitted N dispatch (rev 1 §2, carried; reached at B4 or B8)

Nothing in this section is emitted by the first delivery (B0-B3): the dispatch rows
R1/R2 need M16-M18 to pay (§2.5), and those are measured at the earliest in grid2. The
text is kept so the build has its shape, and so R-19's two facts have their reader.

### 2.1 Where it sits `[rev2: main's points]`

- **The storage point** is R17-a's (setfind.md §7.1), ported to main at B0. pcrec calls
  `mf_locals` there once per activation:
  - the DFA forward scan, in `unanch_scan` (main `src/gen/emit_dfa.c`), ahead of
    `size_t scan_position = <from>;`;
  - the VM hat, at the entry seek in `<searchfn>_run` (`pf_vm_emit_first_class`);
  - the rev-end relocate path's own activation, with its own `from`;
  - `[rev2]` the PRE composite's entry, `pcrec_emit_req_byte_check` (its two callers,
    the DFA entry and `emit_vm.c`'s `_search_run`), which under §1.1's merge is the same
    site's first use. Its `posvar` is the start (winreq §1.1's extension of R-19).
- **The START hook (R-19)** is the TEXT of the activation's origin at that point:
  `search_from` (DFA forward scan, VM `_search_run`), `fwd->from` in `unanch_scan`, the
  relocate path's moved start, and the PRE entry's `posvar`. The kit emits
  `N = n - start` from it. Unstated, every N-row skips (§1.5).
- **The form byte** is written in the site struct's initializer at the storage point.
  The use stays where today's use is. `<stem>__next_candidate` is never the dispatch.

### 2.2 The C text (rev 1 §2.2, unchanged except the start expression)

For one DFA prefilter site `rx_search_pf` (the stem and table of the emitted artifact
for `[0-9]+x`). Text marked `// R17-b` is R17-b's, ported at B4.

**(a) WALK + V1: a SIMD-off artifact with a paid dispatch.**

```c
/* define (file scope) */
struct rx_search_pf__c {
    const unsigned char *s;
    size_t n;
    size_t base, top;
    unsigned long long m;
    unsigned char f;            /* the form this activation runs: 0 WALK, 1 V1, 2 W64 */
};
/* rx_search_pf__mask, __member, __next_candidate: R17-b's text */
static inline size_t rx_search_pf__walk(const struct rx_search_pf__c *c, size_t lo,
                                        const unsigned char *t)
{
    while (lo < c->n && !t[c->s[lo]]) lo++;   /* pcrec's walk, bound read off the struct */
    return lo;
}
static inline unsigned char rx_search_pf__form__body(size_t n, size_t lo)
{
    size_t span = n - lo;       /* lo > n wraps high: the last row's pick, and the use's guard reads nothing */
    if (span < 36) return 0;    /* R1 -> WALK (the literal is the set's, §2.6) */
    return 1;                   /* R7 -> V1 */
}
static inline unsigned char rx_search_pf__form(size_t n, size_t lo)
{
    return rx_search_pf__form__body(n, lo);
}
static inline size_t rx_search_pf__next__body(struct rx_search_pf__c *c, size_t lo,
                                              const unsigned char *t)
{
    if (c->f == 0) return rx_search_pf__walk(c, lo, t);
    return rx_search_pf__next_candidate(c, lo);
}
static inline size_t rx_search_pf__next(struct rx_search_pf__c *c, size_t lo,
                                        const unsigned char *t)
{
    return rx_search_pf__next__body(c, lo, t);
}

/* storage point; `search_from` is the START hook's text (R-19) */
    struct rx_search_pf__c rx_search_pf__c = { subject, subject_length, 0, 0, 0,
                                               rx_search_pf__form(subject_length, search_from) };
/* use (inside the attempt loop) */
            if (scan_position < rx_search_pf__c.n) scan_position = rx_search_pf__next(&rx_search_pf__c, scan_position, rx_can_begin_match);
```

**(b) WALK + V1 + A1 (SIMD-on, R2 paid)** is (a) plus guarded insertions only: the V32
sub-block, `__next_candidate__w32`, `__form__w32` (`span < 36` → 0, `span < 64` → 1,
else 2) and `__next__w32`, then the selector FUNCs `__form` and `__next` whose whole
bodies are the `#if` chain, one call per arm (D155 add. 1). The storage point and the
use are byte-identical to (a). **(c) WALK + A1 (R2 unpaid)** merges R2 into R1's WALK
interval. Rev 1 §2.2 has the full text of (b); it is unchanged and is not repeated.

**Single-form sites.** One surviving form means no field `f`, no `__form`, and
`__next__body` is that form alone. A V1-only site is R17-b's text routed through
`__next`; a WALK-only site at SIMD-off (R0) is either the walk-only scaffold or main's
bare walk, decided by T3 (§2.5). `[rev2]` A LIBC site (D1) and a NONE site (F0) never
carry a scaffold: neither has a SIMD arm in this design, so F5's reason for the scaffold
does not arise.

### 2.3 Why behind `__next` and not in the use (rev 1, kept)

Only the selector shape keeps the use identical in every layer (D155: no `#if` in a body).
The measured cost side (`r17b_prime/out/walk_helper_asm.out`): the walk moved into the
helper and reached through the struct changes the holding function by −3 to +14
instructions on six cells, none identical. That is C_scaffold (M18), measured, never
assumed free.

### 2.4 What N is, and what M is (rev 1, kept; `[rev2]` M is now a STATED fact)

- **N** = `n − start` at the storage point, once per activation. For one `_search` call
  it is the span the call may scan; inside a find-all loop over `_search` it is the
  REMAINING subject, so dense 1 MiB find-all stays LINER-picked and R17-b′ does not fix
  ALPHA's dense find-all rows (bounded prose1m all +599 µs; dfa-hat prose1m all/first
  +232/+234 µs). Those belong to E (R5/R6) and to the iterator (R17-b″).
- **M** is fixed per entry BODY, so no row ever emits a compare on M. `[rev2]` R-19 makes
  it a fact: `mf_site.body` = `MF_BODY_ONESHOT` from every builder at B1 (the three FIND
  points, MLINE, and the PRE composite: winreq §1.1 asks that R-19's "every builder"
  include `req_site_define` and MLINE, and this note assumes it does), `MF_BODY_ITER`
  from `next` bodies at R17-b″, `0` = UNSTATED and N/M rows skip.

### 2.5 The pay rule (rev 1, kept: Q-R17P-3 stands as the kit's design, §7.1)

Every quantity in walk-byte units from the active set; no call-length distribution is
assumed. For a dispatch row r with interval I_r = [a_r, b_r), pick p_r and alternative
a′_r (its `unpaid`, else the pick its interval would fall to), ε the set's null floor
(M6), cost(f, N) the measured single-call cost:
- **T1 (pays where it fires):** max over measured N ∈ I_r of
  [cost(a′_r, N) − cost(p_r, N)] > C_disp_call + ε·cost(a′_r, N).
- **T2 (nothing measurable where it does not fire):** C_disp_call ≤ ε·cost(f_next, b_r).
- **T3 (nothing measurable per use):** C_disp_use ≤ ε·w_min (and C_scaffold ≤ ε·w_walk
  on a walk-only scaffold site).

A row failing T1/T2 takes its `unpaid` pick or is dropped; a site failing T3 gets no
dispatch; an ABSENT C_disp_call, C_disp_use or C_scaffold fails the test it appears in.
`[rev2]` With M16-M18 measured by grid2's TWINS (§5.4), T1-T3 may pass at B4; the BUILT
dispatch is then re-measured by [REGIME-TWIN] (E10) as the official dispatch term, and
the twin rows go STALE by their form hash (measure_sets §2.4) and are carried stale until
that re-measure. If grid2's twins fail T1-T3, no dispatch ships at B4 and B8 waits for
[REGIME-TWIN].

### 2.6 The thresholds are literals from the set (rev 1, kept)

The literals in `__form__*` are resolved from the active set at compile time and written
as integer constants. A different set produces different literals, so a default-set change
moves bytes and is an abi event with its census (D162 ruling 1, D166 item 1,
measure_sets §3.6).

---

## 3. The step plan `[rev2]`

### 3.1 One ordered plan

R-21's ST1-ST6, R-19, R-20 (R-MS1..5) and [REGIME-EVAL]'s E-steps, merged into one
order. Kit steps are B-steps; main's prerequisites and the evaluator's steps are listed
where they gate one. "Zero-mover" means byte-identical to main at SIMD-off AND SIMD-on
over emit_sweep's full population and every stream (the first delivery adds no SIMD row,
so SIMD-on is identical too).

| step | content | R-items | zero-mover? (why) | pcrec abi | MF_SITE_ABI | depends on |
|---|---|---|---|---|---|---|
| **B0** | port R17-a's seam to main: W0-W2 on every forward FIND, `decl_point`, `mf_locals` (binding `s`/`n`), `mf_defined` (`reads_table`, `includes`), the storage refusals, the set FIND sites DEFINED at file scope | (R-17's seam) | yes: R17-a was zero-mover on the kit branch (slot24), and nothing it adds is read by a row that moves a byte | none | 10 → 11 | — |
| **B1** | ST1: the facts and the table, unrouted. `mf_site.body` + the START hook (R-19); `mf_measures` on `mf_art_begin` (NULL until M0) and `consulted` from `mf_art_end` (R-MS1, R-MS2); `mf_form_hash` (R-MS3); the reader declarations (R-MS4 keys) and the `--emit-facts` section `memfn`; the kit's method cards `kit-grid@1` (R-MS5); E3: `fd_rows[]` (§1.3-§1.4: the 18 rows of the locked table; F0, F1, P1 wait for B5), `mf_finder_pick`, `fd_route[]` all SHADOW, the trace-only shadow call, and pcrec's PR-9 reader shadow (each reader computed both ways in the trace build, asserted equal) | R-19, R-MS1..5, PR-9 (shadow) | yes: every group is SHADOW; the shadow writes only to the MF_TRACE build's trace; the reader shadow is `#ifdef`-only | none | 11 → 12 | B0; E3b (oracle cell) runs beside |
| **B2** | ST2: one-byte FIND routed. PR-1 (the candidate set as a SET term at every count, one member included, plus the table offer), PR-2 (miss and move behaviour as hooks: `empty`/`on_miss`, the `n − 1` bound, a moved-candidate hook for the DFA hat's re-seed), PR-3's kind (`site_kind`, categorical, Q-WR-8), `need` re-numbered with an UNSTATED zero and stated by every builder, PR-9's switch for the one-byte readers (G1's memchr test, R4, the K admission, `landing` L4, `<string.h>`, the stamps), `mf_result.proven`/`scan_exists`; kit: KW-1 (the libc row as D1; the libc-free one-byte forms reachable by `fd-d1`), KW-2, KW-3 (the kit writes the guard, post-test, wrapper and moved hook), KW-4; `fd_route` group 1 ROUTED | PR-1, PR-2, PR-3 (kind), PR-4 (stated), PR-9 (one-byte), KW-1..4, KW-10 | yes: D1 IS today's count rule, the kit renders today's guard/post-test text, stamp VALUES stay pcrec row identities (sbscope F7). The PF comment (PR-10) is NOT changed here (Q-R17P-12) | none | 12 → 13 | B1 |
| (main) | E-1 = window_contract S1: `mf_analysis` with the frequency kind always present (`prior-authored`, `prior-none`, `measured`) | — | (window_contract's own) | **S1's own event** | (its own) | window_contract rev 3 (winreq §4's C-items) |
| **B3a** | ST3 shadow: presence spans STATED (PR-5 unpicked, PR-6 offsets with `omin` = 0 as a sound under-estimate, PR-7 member order) on the merged site, PRES SHADOW; the kit's ports of the five priced picks run in the trace build beside pcrec's and must agree on 100% of sites over corpus, bench and rwquest (KW-8); PR-11's control lands (the census over collapsed hybrids + a planted collapse that drops `rmin`) | PR-5, PR-6, PR-7, PR-11, KW-8 | yes: nothing routed | none | 13 → 14 (the presence class, `omin`) | E-1, B2 |
| **B3b** | ST3 route: PRES and D2 groups ROUTED; KW-5..7 (the presence class, G-1/G-2, the applicability rule, the PRE composite's several uses inside the one site); handoff framing (a) (Q-WR-5); presence withheld at G2's linear one-attempt and LOCATE `whole` (Q-WR-4); `-fno-req-set-lead` (bit 45) retired to `--memfn=no-pres-set-lead` in the same commit, with `--emit-facts`' `used`/`why` and the `--list-axes` `req-admit`/`req-use` rows re-sourced (Q-WR-12, KW-11); PR-8 checked (the verdict precedes the edge attempt, today's order) | PR-4, PR-8, PR-9 (presence), KW-5..8, KW-11 | yes for artifacts: the default rows are the ported picks, proven equal at B3a. NOT zero for the registry: bit 45 and two `--list-axes` axes move (a declared registry event, no artifact byte) | none | (14) | B3a |
| | **FIRST DELIVERY COMPLETE (B0-B3b).** | | | | | |
| (kit) | zen4-grid2: ONE slot (§5.4) | KW-12 | — | — | — | its prep lane, after this note's panel |
| (kit) | E4 evaluator build → E4b in-sample streamed replay on grid2 → E5 pre-registration → E6 site census → E7 judge (LEAN: two windows) → E8 results | — | — | — | — | B1, E3b; grid2 |
| (main) | [KNOW-SRC] K0-K3, then [MEASURE-SET] M0 (store, `ksgen`, the embed, the `measures` kind) | (R-MS1..5 consumed) | K0-K3 yes | M0's stamp rides B4 (measure_sets §3.6) | — | — |
| **B4** | THE ROUTING COMMIT and LOCKDOWN: `fd_route` group 4 ROUTED and the list deleted; R7 LINER (V1 = `pf_terms_mask` over `mask8_swar`, R17-b's form, ported: `terms.c`, the W8 shared sub-block, `needs_const_subject`, N6's reserved prefix) on set covers and the VM hat at any \|S\|; R0 → WALK on ≥ 2 RANGE terms; R1/R2 iff grid2's twins pay T1-T3; the `drop-kit-bytes` size rung with its pcrec bit 55 (`-fno-kit-size-drop`, r17c); PR-10's method-neutral PF comment; M0's `<PREFIX>_MEASURES` + `rx_info.measures` | (R-17's move), ST6 if paid, PR-10 | **NO**: the one censused mover (R17-b's movers less R0's population, plus the VM hat at \|S\| = 1; §3.5) | **ONE event**, 78 → the next number at landing | 14 → 15 | B3b; E8 PASS or PROVISIONAL PASS (Q-REVAL-11); M0 (else the stamp is a second event); the default set committed |
| **B5** | ST4: measured rows, each its own censused commit and a FORMAL row addition (post-lockdown: a ruled diff with its replay delta): (a) F1 (a measured libc row may displace D1, Q-WR-1); (b) F0 NONE where E is measured; (c) P1, only once Q-WR-9's trigger fires; (d) PR-6's true `omin`; (e) Q-WR-3's posture relaxed per measured cell (D158: give-up → answer allowed, direction-checked by GIVEUP1) | PR-4 (NONE), PR-6, KW-12, KW-13 | NO where a default compile moves; a row that fires only under a measured `--analysis` bundle moves no default byte | one per default-moving commit | per row | B4; the quantities in the default set |
| **B6** | the W64 rows (A1/S1, `pf-terms-w32`/`-w16`) as guarded selector arms over `__next`; CANDIDATE until a bench verdict (D144 add. 4) | (SIMD thread) | SIMD-off yes; SIMD-on moves (`MEMFN_FORMS` gains the PF site's token) | none (vrun's precedent) | — | B4 (F5: the scaffold exists) |
| **B7** | ST5: the libc class deny and the three libc-free rows (the OFS BODY, MLINE's back FIND, the exact compare outside `overlap`'s lengths), KW-9 | Q-WR-7 | yes at default (reachable only under the deny) | none | — | future work (Q-WR-7, ruled) |
| **B8** | ST6: the N-dispatch rows, if B4 did not ship them | ST6 | NO | one | — | B4; [REGIME-TWIN] E10 |
| B9 | R17-b″ (§6) | — | — | per its own plan | — | D165's build |

### 3.2 Why the first delivery needs no measurement set `[rev2]`

Rev 1 said nothing could ship before grid2 (F8). With the routing state of §1.6 that is
no longer so: through B3b every ROUTED group is decided by a row that reads no set value
(D1, D2, P0, P2-P4, P9). The set-reading rows are either in a SHADOW group (R0, R1, R2
on set sites), or read a key a NULL set cannot hold (R1 on a one-byte site, whose
terminal is LIBC), or are not built until B5 (F0, F1, P1). So B0-B3b need no
compiled-in set, no `mf_measures` value, and no `<PREFIX>_MEASURES` stamp. The shadow and `regime_pick` read the kit's interim TSV in
D166's shape (regime_eval Q-REVAL-10) as a TEST input only.

### 3.3 Lockdown, and where the judge sits

D161 add. 13 puts LOCKDOWN at "the table that passes [REGIME-EVAL]'s judge and ships with
R17-b′'s routing commit". In this plan that is B4. Q-REVAL-11 orders "R17-b′'s ROUTING
commit only after a PASS or PROVISIONAL PASS". B2 and B3b route too, but only rows that
reproduce today, proven by byte identity rather than by timing; this note reads
Q-REVAL-11 as gating the first commit whose picks MOVE a byte (Q-R17P-13 asks main to
confirm). After B4, a row edit is FORMAL: a ruled diff with its evidence, its replay delta
and its mover census.

### 3.4 Per step: abi readers, spec hunks, denies and floors, checks, sabotage

**Abi readers, found BY GREP at B4 (and at every later default-moving step).** The floor
of the list, from rev 1 §5.2, measure_sets §3.6 and findall_iter.md's abi plan:
- the digit's readers: `PCREC_ARTIFACT_ABI` (`src/gen/emit_dfa.c:54` on main), match_api's
  K80 `#error` text, its "abi is N" sentence, §6.3's stamp table and §6's `rx_info` member
  table, `docs/dev/history/abi_changelog.md`, `run_codegen_tests.sh`'s `ABI_EXPECT`,
  `run_recursion_identity.sh`'s FILEPIN / `ABI_SUBJ`, the alpha scripts' normalizers;
- the byte-count readers (their text cites no digit, their values move): the
  `EMITTED_BYTES` rows of `tests/codegen/manifests/m5_stage1_stamps.tsv`,
  `run_resource_tests.sh`'s K59-PREMUL pin (`a{5,25000}`), the size-term and K59/K53
  rung witnesses, the cpset manifest, the size tripwires, `run_anchored_match.sh` §5's
  drop-rung caps, emit_sweep's lowsize/lowboth `VARIANT_PINS`; all re-measured at the SAME
  `-o` basename, never re-typed;
- the mover-by-ID manifests that read PF-site or VM-hat text: the startset VM manifests;
- then the suites that count (registry, codegen, rxtsource) and `make test-codegen`
  (D94 addendum).

**Spec hunks (D80), per step:**

| step | hunk |
|---|---|
| B0 | none (no caller-observable surface) |
| B1 | `registry.md` §6¶8a (the six `fd-*` rows) and §6¶8b (floor); `facts_listing.md` §3 (the `memfn` section of `--emit-facts`) |
| B2 | none (no byte, stamp, listing or flag moves) |
| B3b | `tuning.md` §2.40 (bit 45 retired, reserved; the kit deny named), §2.29 and §2.41 (`req-admit`/`req-use`: which rows are now the kit's, and the listing's projection); `registry.md` §6 (those axes) and §6¶8a/8b; `lib/pcrec.h`'s bit-45 comment; `facts_listing.md` (`used`/`why` re-sourced, values unchanged) |
| B4 | `match_api.md` §6.3 (`<PREFIX>_MEASURES`) and §6 (`rx_info.measures`, beside 6¶14), §1¶7 (the W8 sub-block guard), the abi sentence, the `RX_DFA_PREFILTER` method sentences made method-neutral (setfind §11.3); `tuning.md` §2.42¶2 (the VM hat seek), §2.43¶3a, §2.49 (the `size` rows), and the bit-55 axis section; `limits.md` §8.4 (the `drop-kit-bytes` rung); `registry.md` floor and the bit-55 row; `cli.md` (N6's refused prefix; `--list-measurements` at M0); `docs/spec/measures.md` (new, M0) |
| B5 | per row: `registry.md` (its deny), `measures.md` (new keys' cards) |
| B6 | `limits.md` §8.3¶3 (guarded bound), `match_api.md` §6.3.10¶4 (the PF token in `MEMFN_FORMS`), `registry.md` |
| B7 | `registry.md` and `tuning.md` §2.43 (the libc class deny) |

**Denies and the `memfn` floor** (`registry.md` §6¶8b; main's floor is 6; each commit
raises it by the rows it adds, so the numbers below assume this order):

| step | rows added to `options.def` | floor |
|---|---|---|
| B1 | `fd-r0`, `fd-r5`, `fd-r6`, `fd-r8`, `fd-ndisp`, `fd-d1`: one per built row the evaluator can score (regime_eval §5.2: C3/C4 are row denies; E3 creates them) | 6 → 12 |
| B3b | `fd-pres-g1`, `fd-pres-pick`, `pres-set-lead` | 12 → 15 |
| B4 | `pf-terms-mask` (the V1 FORM deny, R17-b's) | 15 → 16 |
| B5 | `fd-libc-m`, `fd-none` (PAIR: its force spelling is how a later slot times NONE), `fd-pres-priced`, each with its row | +1 each |
| B6 | `pf-terms-w32`, `pf-terms-w16` | +2 |
| B7 | `libc` (the class deny) | +1 |
| B9 | `fd-r3a`, `fd-r3b`, `fd-r4` | +3 |

pcrec's own registry: bit 45 retires at B3b; bit 55 is taken at B4 (free on main: B3
took 56), leaving bits 57-63 (seven, above [IFACE-PUSH]'s ≤ 4 trigger).

**Checks per step (G1 = pcrec's gate, G2 = the kit's generated space):**

| step | G1 | G2 and other checks |
|---|---|---|
| B0 | emit_sweep full population, every stream and arm, 0 movers | R17-a's refusal cases (window fields, storage) ported |
| B1 | emit_sweep 0 movers; the trace SET compare (new records only under MF_TRACE) | R-MS1's bar (every finder row run with NULL, with each key absent in turn, with the full set; no kit row reads a `pcrec.` key); R-MS2's bar (no key read → false; an absent key read → true; a present key → true); R-MS3's fixtures (a zero-mover refactor keeps the hash, a one-instruction edit moves it); the blinded oracle E3b (regime_eval §5.4) and, at E4, the agreement check (regime_pick vs the shadow on every FIT cell) |
| B2 | emit_sweep 0 movers incl. `-e utf8`, `--engine=vm` and the start arms; the reader shadow's equality, then its retirement | KW-10's one-byte family: the count rule, NONE's answer identity at DFA consumers (shadow), NONE refused where `need` is REQUIRED, MLINE's generic shape |
| B3a | the five-pick shadow: 100% agreement, reported per pick | PR-11's control (shares no source with the req walk) |
| B3b | emit_sweep 0 movers on artifacts; the registry diff declared | KW-10's presence family (absent-at-end discovery, REQUIRED-all on proof routes, re-asked ranges with `omin` < 0); plants reaching NON-DFA routes only (a DFA-route-only green is vacuous) |
| B4 | G1 timing at both layers (§8.1) on the pcrec-side mover population; the mover census by ID (§3.5) | G2's setfind family; `make test-memfn-sets` (§8.2); measure_sets §8.1 (answers under every committed set and the synthetic extremes, REACH floors per arm on generated boundary subjects) |

**Sabotage** is in §8.3 (S911-S922 and S964-S980, each with its step).

### 3.5 Which artifacts move at B4 (rev 1 §5.1, re-based on main)

Rev 1's census (`r17b_prime/out/census_shapes.out`) counted R17-b's movers on the kit
branch: 996 byte / 2,910 byte-vm artifacts, one stateful site each, of which R0's ≥ 2
RANGE population is 219 / 243 (mostly `\w`, shape (3,0,1)). Against MAIN at B4:
- the set sites outside R0 (777 / 2,667) move to V1 behind `__next` (plus the dispatch if
  paid);
- R0's sites stay byte-identical to main except the abi digit and the new stamp (bare
  walk), or take the walk-only scaffold if T3 passes (§2.5);
- the VM hat at \|S\| = 1 (112 / 8 / 1, inside the byte-vm count) moves from main's table
  walk to V1's one-term cover;
- one-byte sites (D1) and presence (P-rows) do not move;
- every artifact moves by the abi digit and `<PREFIX>_MEASURES` (`""` where nothing
  consulted, measure_sets §3.5).

These counts are re-taken against main at B4 by a pcrec-side reader of the emitted C (the
census never reads the kit's `moved`). The utf8 arms' split (964 / 2,907 R17-b movers)
was not re-run for R0.

### 3.6 Size (rev 1 §5.4, MEASURED on hand twins, SIZE ONLY; kept)

`gcc -O2 -c`, `.text` + `.rodata`/`.data`, use-branch twins, thresholds 36/64:

| cell | main (walk) | R17-b (V1) | WALK+V1 | WALK+A1 | WALK+V1+A1 |
|---|---|---|---|---|---|
| dig | 2,436 | 2,692 | 3,076 | 3,844 | 4,292 |
| bounded | 2,372 | 2,794 | 3,204 | 3,972 | 4,612 |
| dfa-hat | 4,196 | 4,708 | 5,028 | 5,860 | 6,564 |
| vm-hat | 1,358 | 1,966 | 2,382 | 3,758 | 4,718 |
| hex-run | 2,572 | 2,892 | 3,276 | 4,236 | 4,748 |
| vm-hat-1 | 1,423 | 1,871 | 2,287 | 3,535 | 4,367 |

V1 alone (B4 with no dispatch) is R17-b's +256..+608 B per site over main; a paid
dispatch adds +320..+416 B more; the SIMD-on forms are guarded (outside the caps,
counted by `SIMD_GUARDED_BYTES`). `pf-terms-mask` is `MF_SZ_ADDS`, so the size ladder's
`drop-kit-bytes` rung denies it on a cap refusal and the site takes the walk.

---

## 4. The contract: the one window request `[rev2]`

Every field below is a FACT (D157): pcrec states what is true of the sub-problem it
hands over, never a method. Spellings are PROPOSED; the layout is the kit's to finalize
(window_contract §3.1's convention). Each piece cites the winreq C-item it implements;
§4.8 maps all sixteen.

### 4.1 The site: span 0 and the PRESENCE spans (C-1, C-2, C-4, C-16)

One `mf_site` per search entry (§1.1). It carries:
- **span 0** in `pred`: the candidate set as a SET term at every count, one member
  included, with the table offered (`table_name`, PR-1). A handoff landmark longer than
  one byte is a RUN term (D2). Absent on a presence-only site (`pred.nterm = 0`).
- **presence spans** in `preds[]`, each a new span class:

```c
typedef enum { MF_SPAN_UNSTATED = 0, MF_SPAN_BOUNDED, MF_SPAN_CONTEXT,
               MF_SPAN_PRESENCE } mf_span_class;       /* appended to mf_pred, B3a */
/* PRESENCE only:
 *   omin          the smallest offset, from the MATCH START, at which an occurrence
 *                 can begin; >= 0 (presence bytes lie inside [start, end): lookaround
 *                 bodies are never in the necessary set); 0 is a sound under-estimate
 *                 (PR-6) and is what B3a states; the true omin is B5's (PR-6 at ST4)
 *   member_order  for a one-byte span split from a necessary set: its position in
 *                 pattern order (PR-7), the fact the leftmost/rightmost tie reads
 *   window_stated 0 (a presence span has no omax: C-1)                              */
```

And on the site, one new fact, `head_max` (`h_max`): the largest distance from a match
start to span 0's start. It is 0 for a head-0 origin and K for the handoff's landmark
origin (PR-6's "K as h_max"); pcrec keeps `c − K` and the utf8 round-up in its own text
(window_contract §2.1). The kit needs it only for the per-candidate cut (§4.4).

- **Rules** (C-2): a PRESENCE span states `window_stated 0`, `omin ≥ 0` and a `need`;
  `move_back`/`overshoot` are not read for it; `MF_MOVE_UNBOUNDED` stays permanently
  refused for every class (D161 add. 5). The sequence rule (`spans_seq`) does not apply to
  presence spans: they carry no pairwise distance.
- **Unpicked** (PR-5): every necessary-set member is its own one-byte presence span, and
  the whole run is one span with its mask. The pick, the window and set-leads are the
  kit's rows (P3, P4), no longer pcrec's encoding. `req_set` is asked only where today
  asks (Q-WR-12).
- **Context predicates** stay as window_contract §2.2 has them: MLINE's `{\n}` at −1 is
  a CONTEXT span, never presence, and the edge stays pcrec's (D161 add. 7).
- **C-4** follows: no site keeps the ALL_PRESENT → VERDICT reply. ALL_PRESENT's
  renderers (`precheck`, `precheck_assign`, `precheck_assign_byte`) survive as the
  merged site's ENTRY-USE rendering at B3b (KW-7), not as a separate reply type.

`[rev2]` **Why `omin` is measured from the match start and not from span 0** (a
refinement of C-1, which writes "`omin ≥ −h_max` when the origin's head is bounded").
Presence is a fact of the MATCH, and the binding is per ACTIVATION (§4.4): every match of
an activation begins at or after the activation's start (R-19's START hook), and every
presence byte lies inside the match. So the verdict window is `[start + omin, n)`, which
at `omin = 0` is exactly today's `[posvar, n)` (zero-mover), and is sound for a landmark
origin with no read before `start`. Measured from span 0, the same window would be
`[lo − h_max, n)`: wider than today's (a mover), and reading below the call's floor.

### 4.2 The facts R-19 and R-21 add to the site (PR-3, PR-4; C-11, C-14)

| fact | values | stated by | step | why |
|---|---|---|---|---|
| `body` (R-19) | `MF_BODY_ONESHOT`, `MF_BODY_ITER`; 0 = UNSTATED, N/M rows skip | every builder (the three FIND points, MLINE, the PRE composite) | B1 | key M: R1/R2's "one-shot" |
| START hook (R-19) | the text of the activation's origin at the storage point | the same builders | B1 | key N (`n − start`); the presence window (§4.1) |
| `site_kind` (PR-3, Q-WR-8) | §4.3's kinds; 0 = UNSTATED | every PF/MLINE/PRE builder | B2 | D1 excludes the VM hat's seek (Q-R5); F0 excludes the give-up-exposed kinds; g\* is per kind (R5/R6) |
| `need` re-numbered (PR-4) | `{UNSTATED = 0, REQUIRED, OPTIONAL}`, stated on every span | every builder | B2 (stated), B3b (binds presence) | the EFFORT fact (C-14): REQUIRED exactly where dropping, narrowing or answering unconstrained could let a budgeted engine do more work on an input the denied build answers (D158) |
| `head_max` (PR-6) | bytes | the PRE builder; 0 elsewhere | B3a | §4.1 |

- **`consumer` is REPLACED, not dropped** (C-11, Q-WR-8 ruled): window_contract's S3
  retires `mf_site.consumer` (`MF_C_ENGINE` everywhere, unread) with `site_kind` as its
  replacement. Until S3 both exist and `consumer` stays `MF_C_ENGINE`.
- **What is NOT stated** (Q-WR-4, ruled): pcscope's three further consumer facts (one
  start, body decides presence, skipping barred) are not sent at B3; pcrec withholds
  presence on those sites instead. `use = DISCARD` already exists for the Q10 collapsed
  hybrid.

### 4.3 The consumer kinds

| `site_kind` | what consumes the candidates | budgeted? | sites |
|---|---|---|---|
| DFA_SCAN | a DFA body's forward scan (restart at the candidate) | no | PF, PRE on a DFA route |
| DFA_HAT | a seeded DFA scan that RE-SEEDS where the skip moved (`pf_emit_moved_reseed`) | no | `first-*-bounded` |
| HYB_PF | a VM hybrid's inner DFA prefilter (exact or count-collapsed) | the VM behind it is; the prefilter is not | PF inside a hybrid; PRE on a hybrid route |
| VM_ATTEMPT | the VM attempt loop (the hat's seek, and the entry of a no-DFA VM route) | YES (steps, frames, work per call) | VM hat; PRE on a no-DFA route |
| ATTEMPT_PRED | ENG_ATTEMPT's predecessor seek (MLINE) | no (a DFA attempt) | MLINE |

### 4.4 The reply: one stream, bound at range level (C-3, C-5, D161 add. 7 and 14)

- **The stream** (D161 add. 7): candidates are span 0's starts, COMPLETE, ASCENDING, no
  repeats; stateless (`result`) or stateful (`next_candidate(&state, lo)`), the same
  sequence.
- **Range-level binding (C-3 i).** If a REQUIRED presence span has no occurrence in
  `[start + omin, n)`, the stream is EMPTY.
- **EMPTY = NOMATCH** (D161 add. 14's clarification). On a site with a context
  predicate, NOMATCH for the covered positions; pcrec's edge attempt covers the rest
  (window_contract §2.4).
- **Decided first (C-3 ii, G-2).** EMPTY or the first element is returned only after every
  REQUIRED presence span is established over its whole window. Today's order already does
  this (the pre-check at the entry); the entry use renders it.
- **One verdict per activation** `[rev2]`: later uses in the same activation (the loop's
  next candidate, the handoff's re-entry) yield candidates only and never re-verify.
  pcscope §3.2's re-asked-range rule (from `lo′ − h_max`) is the ITERATOR's, where a
  verdict is carried across calls (§6), not a one-shot rule.
- **Per-candidate use is a PERMISSION (C-3 iii, Q-WR-6).** A candidate `c` whose implied
  match start `c − h` cannot reach an occurrence (no occurrence in
  `[c − head_max + omin, n)`) begins no match; the kit MAY end the stream after the last
  occurrence `p` at `c > p − omin + head_max`. Never required; exercised only by the
  iterator (§6), after D165's build.
- **The unconstrained reply is a range (C-3 iv).** "Every position in `[lo, hi′]`" with
  `hi′ = n` is legal iff span 0 is OPTIONAL or absent (G-4): it is F0 NONE on a DFA
  consumer, and it is a presence-only site's reply (today's VM entry runs every position
  after the pre-check). The tighter `hi′ = p − omin + head_max` is the permission above.
  No output hook is added: in this delivery `hi′ = n` everywhere, so the consumer runs to
  `n` as today; a `result_hi` hook is FILED with its trigger (the iterator's cut).
- **The handoff (C-5, Q-WR-5 (a)).** Origin = the landmark: span 0 is the landmark
  (D1 for one byte, D2 for a run), presence is fused into the stream (an exhausted
  stream is the landmark's absence), and pcrec keeps `max(lo, c − K)`, the utf8 round-up
  and the re-entry. The re-entry is a further USE of the same site at `scan_position`
  (C-5's row in window_contract §2.5 is rewritten accordingly).

### 4.5 The PROVEN-facts channel: what the kit reports at `mf_define` (PR-9, KW-4)

D161 add. 8: at compile time the kit states what every candidate of the site has PROVEN,
the same in every layer (§1.5 rule 1), and pcrec emits code from it. D161 add. 14's
clarification makes this the read-back for pcrec's readers of "the scan form": they read
FACTS, never a form name. `mf_result` gains (PROPOSED):

| fact | meaning | B-step |
|---|---|---|
| `proven0` | the byte set every candidate's byte at offset 0 is proven to lie in (all 256 = nothing proven) | B2 |
| `scan_exists` | 1 iff a search text precedes the consumer at the use (0 for NONE) | B2 |
| `includes` | the headers the site's text needs (R17-a's `mf_defined.includes`, ported at B0) | B0 |
| `pres_kept[i]` | per presence span: KEPT, DROPPED, or PICKED (with the kept member) | B3b |

pcrec's six readers, each mapped to one fact kind:

| reader (main) | reads today | reads after its step |
|---|---|---|
| G1 (`dfa_cand_scan`, `req_byte_dominated_by`) | pcrec's own scan row and byte | `proven0` at B2; at B3b G1 itself is the kit's row P2 and pcrec's reader retires |
| R4 (`pcrec_dfa_cand_ppm`) | the scan's candidate set, and "no scan means 10^6" | `scan_exists` + the mass of `proven0` under pcrec's prior; NONE reads 10^6 by the fact (a5inv's deliberate branch, now on the fact rather than on a row name) |
| the handoff K admission (`req_landmark_admits`) | the displaced start-byte row's scan | `scan_exists` + `proven0` of the start-set site |
| `landing` L4 (`start_landing_applies`) | whether the NEXT block stores `landing_position` | `scan_exists` (0 ⇒ L4 declines; sbscope §2's second option, chosen because it keeps no store on every byte) |
| `<string.h>` | whether `memchr` is emitted | `includes` |
| the stamps (`REQ_WHY`, `REQ_HANDOFF`, `dfa_prefilter_name`, `REQ_BYTE`, `REQ_RUN`) | pcrec's rows | `REQ_WHY` reads `pres_kept`; the rest stay pcrec ROW identities with unchanged values (sbscope F7) |

No reader receives a form name; the rename of the method-named count fact
(`DFA_PF_MEMCHR`, `use_memchr` → the count it is) rides B2 (PR-9). Through B1 the
readers run both ways in the trace build and must agree (the reader shadow, §3.1).

### 4.6 The K65 obligation, per consumer (C-10, C-12, C-13, C-14; G-1..G-5)

| consumer (§4.3), route | span 0 `need` | presence `need` | NONE (unconstrained) | what an EMPTY stream must preserve | give-up posture |
|---|---|---|---|---|---|
| DFA_SCAN, DFA body | OPTIONAL | OPTIONAL | legal (no budget) | nothing (the DFA proves absence itself) | — |
| DFA_HAT | OPTIONAL | OPTIONAL | legal | nothing | — |
| HYB_PF, exact or count-collapsed front | OPTIONAL | OPTIONAL: every DFA-scan front enforces the necessary set and run (W4; `nfa.c`'s `X{m,n} → X{min(m,1),}` keeps every `rmin ≥ 1` byte), held by PR-11's control | legal | nothing | — |
| ATTEMPT_PRED (MLINE) | OPTIONAL | — | answer-safe, but no row until measured (Q-WR-2) | — | — |
| VM_ATTEMPT, VM hat, no DFA front | REQUIRED (D148 Q6; G-4; W3) | REQUIRED (K64, K65, K66; W1, W2) | NOT legal (F0 excludes the kind; the applicability rule refuses it besides) | every give-up → NOMATCH conversion the pre-check makes today (G-1): every member, the WHOLE run | through B3b: no move in either direction (Q-WR-3); from B5: D158 per measured cell (answer → give-up never; give-up → answer allowed, direction-checked by GIVEUP1) |
| VM_ATTEMPT, presence-only (no hat) | — | REQUIRED | the range `[lo, n)` (today's reply) | the same | the same |
| framed one-attempt VM (K64) | — | REQUIRED | — | the same | the same |
| linear one-attempt VM (G2) and LOCATE `whole` | — | WITHHELD (Q-WR-4) | — | — | — |

The witnesses (pcscope §2.3) become the reach witnesses of §8.3's plants: W1
(`(x?)([a-z]+)+Z.@\1`, `a`×31+`Zb`: nomatch today, give-up under `-fno-req-byte`), W2
(the same under `(?m)^`: the verdict must precede the edge attempt, PR-8), W3
(`(?=(?:a|b|x)*c)x`, `--engine=vm --backtrack-frames=8`: a match today, `frames` under
`-fno-start-set`), W4 (the collapsed-front control: NOMATCH with `@` untested).

### 4.7 The measurement set's channel (R-20: R-MS1..R-MS5)

- **In (R-MS1):** `mf_art_begin(..., const mf_measures *ms)`: the `kit.` rows of the set
  pcrec LOADED (key, `value_e6`, unit, source) plus the set's `id`, `rev`,
  `values_digest`, `class`, `tier`, `composite` (measure_sets §4.1). No `status` (a NULL
  row is not handed over), no `pcrec.` rows, no provenance columns. NULL = no set. Per
  compile, not per site (rev 1's Q-R17P-5, answered by R-MS1).
- **Out (R-MS2):** `consulted` from `mf_art_end`: true iff any kit row of this compile
  resolved a key, found or absent. pcrec ORs it with its own readers to decide whether
  `<PREFIX>_MEASURES` is `""` (measure_sets §3.5). Through B3b no ROUTED row reads a key,
  so `consulted` is false on every default compile (the shadow's reads are trace-only
  and do not set it).
- **Form hashes (R-MS3):** `mf_form_hash(form_id)` over the canonical instance with
  scaffolding normalized out, for every form a card names: `walk`, `V1`, `libc`, the
  one-byte libc-free forms, `none`, the dispatch twin, `W64`. `[rev2]` The `libc` form's
  hash covers the CALL text only; the library's own code is outside it, which is why the
  libc rows need a third dependency owner (§5.3, Q-R17P-14).
- **Reader declarations (R-MS4):** per `fd_rows[]` row, the keys it reads and per
  threshold key its SAFE direction (`max`/`min`/`none`: the side of its `unpaid` or
  conservative pick), as data in [LIST-TABLES]' census shape; per artifact, the
  `--emit-facts` section `memfn` (§1.7). Keys at B1 (M0's listing); directions at M2.
- **Method cards (R-MS5):** one card row per quantity of §5.2, in a section TSV in the
  kit tree, versioned `kit-grid@N` (grid1 = `@1`, grid2 = `@2`).

### 4.8 winreq's C-items, each mapped

| C | change | implemented by | step |
|---|---|---|---|
| C-1 | the PRESENCE class: `omin`, no `omax`, its own binding; "below the origin" split into necessary-before-origin and CONTEXT | §4.1 (`mf_span_class`; `omin` from the match start, `[rev2]` refinement) | B3a |
| C-2 | presence carved out of "bounded only"; the unbounded sentinels and `window_stated 0` stay refused on window spans | §4.1 rules | B3a |
| C-3 | range binding; decided-first; per-candidate permission; the range form of an unconstrained reply | §4.4 | B3b |
| C-4 | delete "presence sites keep the VERDICT reply" | §4.1 | B3b |
| C-5 | the run pre-check row and the K82/L1 row rewritten (origin = landmark) | §4.4 | B3b |
| C-6 | T-PRES superseded: `dominated` is the kit's (P2), presence is not a separate site, `none` stays pcrec's sub-problem choice (Q-WR-4) | §1.4, §4.2 | B3b |
| C-7 | R-18's text and window_contract §11 changed in step | main's ledger edit | with window_contract rev 3 |
| C-8 | unlock (c) "presence as a chain link" becomes the contract | main's doc edit | with rev 3 |
| C-9 | the APPLICABILITY rule for REQUIRED spans | `fd_row.kinds` + P0's precedence (§1.3, §1.4) | B3b |
| C-10 | G-5's direction per consumer | §4.6's posture column (Q-WR-3) | B3b, B5 |
| C-11 | `consumer` replaced by the kind, not dropped | §4.2 | B2 (kind), S3 (retire) |
| C-12 | NONE's safety per consumer | §4.6 | B2 (stated), B5 (F0 reachable) |
| C-13 | the VM-route EXCLUSION | §4.6 rows 5-7 | B2/B3b |
| C-14 | the EFFORT fact is `need` | §4.2 | B2 |
| C-15 | an evidence-reading row reads only MEASURED provenance | §1.3 (F0, R5, R6, R8), §1.4 (P1) | B1 |
| C-16 | member order and per-member offsets as span fields | §4.1 (`member_order`, `omin`) | B3a |

### 4.9 `MF_SITE_ABI`, by step

Main's 10 (the kit branch's 11 and 12 are not on main). B0 → 11 (R17-a's window fields
and storage), B1 → 12 (`body`, the START hook; `mf_art_begin`'s `mf_measures` and
`mf_art_end`'s `consulted` change the art calls in the same bump), B2 → 13 (`site_kind`,
`need` re-numbered, the moved-candidate hook, `proven0`/`scan_exists`), B3a → 14 (the
presence class, `omin`, `member_order`, `head_max`; `pres_kept` read at B3b), B4 → 15
(R17-b's `needs_const_subject` and the W8 sub-block). Each is a kit contract event moving
no pcrec byte except B4's.

---

## 5. Measurements (D166)

### 5.1 The unit and the key (rev 1 §3.1, re-spelled per measure_sets §1.3)

- **Unit u** = β_walk(PF, one RANGE term) = **0.1892 ns/B** on grid1 (MEASURED, gridread
  §2.1 F3), the set's `unit_key`. Costs are stored in u·B ("walk-bytes"), per-byte rates
  as ratios to u, crossovers in bytes; absolute ns is provenance only (`abs_ns_e6`).
- **Key** `[rev2]`: measure_sets §1.3's one canonical string, `kit.<quantity>.<tokens>`,
  the tokens in the order the quantity's card declares in `dims` (form; compared form;
  site kind; shape; length class, as each card needs). Rev 1's keys
  (`kit.beta.V1.ANY.r2e0c0`) are conforming (measure_sets §1.3.3). The SUBJECT condition
  is a card field (measure_sets §1.2's `subject`), so a streamed and a repeated
  measurement of one quantity are two cards, never one key with a tag.

### 5.2 Every quantity the table reads `[rev2: M19-M23 added; the card column]`

"in grid1?" = the value exists in the one run grid1 (Zen 4 7700X, CPU 14, 2026-10-13,
read by `gridread.py` @ 540649453). Citations "§x" are to gridread_report.md.

| id | quantity | key dims (form / vs / kind / shape) | relative value (grid1) | absolute (provenance) | source | reader | in grid1? |
|---|---|---|---|---|---|---|---|
| M1 | β, the unit | walk / – / PF / (1,0,0) | 1.000 | 0.1892 ns/B | §2.1 F3 | all | yes |
| M2 | β walk by terms | walk / – / ANY / 2t, 3t, 4t | 0.992, 1.002, 0.999 | 0.1877, 0.1896, 0.1891 | §2.1 | R0 | yes |
| M3 | β V1 by shape | V1 / – / ANY / (1,0,0), (2,0,0), (2,0,1), (3,1,0), (0,1,1) | 0.572, 0.978, 1.132, 1.410, 0.731 | 0.1082, 0.1851, 0.2141, 0.2667, 0.1384 | §2.1; an. 2.3 | R0, T1 | yes |
| M4 | β S1 by shape | S1 / same five | 0.108, 0.177, 0.220, 0.285, 0.112 | 0.0205 … 0.0212 | §2.1; an. 2.3 | T1 (W16) | yes |
| M5 | β A1 by shape | A1 / same five | 0.056, 0.079, 0.101, 0.143, 0.057 | 0.0106 … 0.0107 | §2.1; an. 2.3 | T1 (W32) | yes |
| M6 | null floor ε | – | 0.031 | p90 A/A over 141 F1 groups | §1.2 | R0, T1-T3, F1 | yes |
| M7 | single-call fixed part F, n ≥ 64 | walk, V1, S1, A1 / – / PF | 25.1, 22.1, 24.8, 26.3 u·B | 4.74, 4.18, 4.70, 4.98 ns | §2.2 | T1, T2 | yes |
| M8 | F at n = 48 (sub-block tail) | walk, V1, S1, A1 / – / PF | 25.6, 22.0, 129.7, 77.9 u·B | 4.84, 4.17, 24.54, 14.73 ns | §2.2 | T1, T2 | yes |
| M9 | single-call crossover | V1 / walk / ANY / member-free | 36 B (bracket 32-48) | | §4.3 interp., §4.4 | R1 | yes |
| M10 | single-call crossover | S1, A1 / walk / ANY | 18 B, 20 B | interpolated | §4.3 | listed only | yes |
| M11 | block step | W64 / V1 / ANY | 64 B | DERIVED (W = 64), step MEASURED at n 63→64 | §4.4 | R2 | yes |
| M12 | single-call delta at N | V1 − walk / PF / N = 8, 32, 48, 63 | +12.2, +3.2, −23.8, −29.6 u·B | +2.3, +0.6, −4.5, −5.6 ns | §4.3, §4.4 | T1 | yes |
| M13 | c_cold per activation | V1, S1, A1 / walk / PF | +13.1, +15.3, +15.4 u·B | +2.47, +2.90, +2.91 ns | §2.4 | T1 checks | yes |
| M14 | per warm use, absolute | walk, V1, S1, A1 / – / PF | 8.8, 12.6, 11.7, 11.8 u·B | 1.67, 2.38, 2.22, 2.23 ns | §2.3 | T3 (w_min) | yes |
| M15 | g\* | V1, S1, A1 / walk / PF, DFA-hat, bounded | V1 10.8-16.7 / 3.0-3.3 / 21.5 B; S1 4.3-4.7 / 2.1-2.4 / 3.6-5.8; A1 4.2-4.4 / 2.1-2.3 / 2.4-3.0 | log2-interpolated | §4.1 | R5, R6 (and R8's g8) | yes |
| M16 | dispatch charge per activation | dispatch / none / ANY | — | — | — | T1, T2 | **ABSENT** |
| M17 | dispatch charge per use | dispatch / none / ANY | — | — | — | T3 | **ABSENT** |
| M18 | scaffold charge per use | walk-in-helper / walk-inline / PF, VM_ATTEMPT | — | asm differs by −3..+14 insns (`r17b_prime/out/walk_helper_asm.out`) | — | T3 (R0 sites) | **ABSENT** |
| M19 `[rev2]` | libc one-byte F and β | LIBC / – / DFA_SCAN (fwd, bounded), DFA_HAT, HYB_PF, ATTEMPT_PRED (back) / (0,1,0) | — | glibc F 3.24 ns (`linux_results.md`, method-mixed, not a set) | — | F1, D1's replacement | **ABSENT** |
| M20 `[rev2]` | libc-free one-byte F and β | V1 one-term, WALK at \|S\| = 1, the generic byte loop / – / the same kinds / (0,1,0) | — | — | — | F1 | **ABSENT** (grid1's sets are all ≥ 2 members or one RANGE term) |
| M21 `[rev2]` | one-byte dominance points | each libc-free form / LIBC / kind | — | DERIVED from M19, M20 | — | F1 | **ABSENT** |
| M22 `[rev2]` | NONE's gap threshold g_none | NONE / the next pick / DFA_SCAN, DFA_HAT, HYB_PF (ATTEMPT_PRED: measured only for Q-WR-2's decision) / shape | — | — | — | F0 | **ABSENT** |
| M23 `[rev2]` | the pre-scan gate: KEEP − DROP per presence shape, route and position (early, late, absent) | gate / – / DFA_SCAN, HYB_PF / one byte, set 2-4, run 2-8 | — | — | — | P1 | **ABSENT** (and P1 waits for Q-WR-9's trigger) |

- **15 of 23 families exist in grid1; 8 are ABSENT**: rev 1's three dispatch charges
  (M16-M18), the one-byte libc and libc-free costs and their crossover (M19-M21), NONE's
  effort (M22), the pre-scan gate (M23).
- **INTERPRETATION, recorded so the arm is built (not a value any row reads):** grid1's
  EXT arms put the DFA's own per-byte step at 0.1885 ns/B (armread), within 0.4% of u.
  So on a DFA consumer NONE costs about what WALK costs per byte, and its saving against
  WALK is only the per-landing exit and re-entry; against LIBC or V1 it loses on sparse
  text. That is why M22 is a GAP threshold (NONE pays below it) and why F0 needs E.

**The card each needs (R-MS5), `kit-grid@2`:**

| quantity | `dims` | `subject` | `lengths` | `deps` |
|---|---|---|---|---|
| `beta` (M1-M5, M19β, M20β) | form;kind;shape | streamed (Q-R17P-9) | the slope 64 KiB → 1 MiB, member-free single calls | `kit:form.<form>`; for LIBC also `libc:<name>@<ver>` (§5.3) |
| `eps` (M6) | — | streamed | the F1 groups' A/A pairs | — |
| `f` (M7, M8, M19F, M20F) | form;kind;lenclass | fresh buffers, member-free | n ∈ {8, 32, 48, 63, 64, 1 Ki} | as `beta` |
| `xover` (M9, M10), `block` (M11), `delta` (M12), `dom` (M21) | form;vs;kind | derived (registry formula, measure_sets §1.6) | — | the inputs' `deps` |
| `ccold` (M13), `wuse` (M14) | form;kind | streamed find-all | L ∈ {32, 1 Ki, 64 Ki}; g grid | as `beta` |
| `gstar` (M15), `gnone` (M22) | form;kind;shape | streamed find-all | g ∈ {2, 4, 8, 16, 32, 64, 256, 4096, absent} | as `beta`, plus `kit:form.none` for M22 |
| `cdisp_call`, `cdisp_use`, `cscaffold` (M16-M18) | kind | fresh buffers (call) / streamed (use) | M12's N points; F1 dense groups | `kit:form.dispatch-twin` (stale when the BUILT dispatch differs: §2.5) |
| `gate` (M23) | shape;kind;position | streamed find-all | 64 Ki, 1 Mi | `kit:form.libc`, `libc:<name>@<ver>`, `pcrec:<probe>` (the consumer is pcrec's emitted DFA) |

### 5.3 The libc rows' dependency owner `[rev2]`

measure_sets §2.4 has two dependency owners, `kit:` and `pcrec:`. The libc rows' measured
code includes the C library's `memchr`, which neither owns. D161 add. 14 names the
provenance `libc:<name>@<version>`; this note adds what it means for staleness:
- **The artifact runs against the CALLER's libc**, at run time, which pcrec cannot see
  at compile time. A `libc:` hash compared with the BUILD host's library (glibc's
  `gnu_get_libc_version()`, or `confstr(_CS_GNU_LIBC_VERSION)`) would stale a row on a
  box that is not where the artifact runs.
- **PROPOSED:** `libc:` deps are recorded as provenance in `deps`, and a mismatch with
  the build host's library is a SET-level listing flag `libc-mismatch`, exactly as
  measure_sets §2.4 treats `compiler-mismatch`, never row staleness. The kit-side half
  (the form hash of the CALL text) stays row staleness as for any form. Q-R17P-14 asks
  main, as measure_sets' owner, to take the third owner on these terms.

### 5.4 zen4-grid2: ONE slot spec `[rev2]`

One run under D166's rule: one box (the Linux dev box, Zen 4 7700X, CPU 14 via
`taskset`, governor `performance`), one method version (`kit-grid@2`), gcc 15.2 `-O2`,
the grid1 harness (`docs/dev/lanes/grid1/`, arm contract `grid1/README.md`) with
rotated interleaving, 7 rounds per launch, the per-launch median, LAUNCHES 3 (+2 by the
pre-registered rerun rule), the quiet gate at every group boundary. Costs use
regime_eval §2.1's own formula: groups × arms × 3.4 launches × 0.95 s.

| # | item | for | groups × arms | wall |
|---|---|---|---|---|
| 1 | the 149 fit groups (F1 141 + F3 8) re-timed STREAMED, every pickable arm at both layers plus `walk#b` and `walk#c` | regime_eval's in-sample reference R_in (E4b) AND, under Q-R17P-9 (B), the set's M1-M15 | 149 × ~7 | **56.1 min** |
| 2 | dispatch TWINS: the WALK+V1 scaffold with `f` forced to each form against the single-form artifact (`mkvar.py` gains the variant): F3's member-free points, 20 dense F1 groups, 6 R0-shaped scaffold groups (hex-run, word-eq, `\w`) | M16, M17, M18 | 8×3 + 20×3 + 6×2 | **5.2 min** |
| 3 | one-byte arms (LIBC, WALK at \|S\| = 1, V1 one-term, the generic loop, `walk#b`) at five kinds (DFA_SCAN fwd, DFA_SCAN bounded, DFA_HAT, HYB_PF, ATTEMPT_PRED back), over 6 gaps {2, 8, 32, 256, 4096, absent} find-all streamed + 4 member-free lengths {8, 32, 64, 1 Mi}. ATTEMPT_PRED takes LIBC-back and a hand back-walk only | M19, M20 (M21 derived) | 50 × 5 | **13.5 min** |
| 4 | NONE arms (the use's FIND statement deleted by `mkvar.py`: the consumer walks) at DFA_SCAN, DFA_HAT, HYB_PF and ATTEMPT_PRED over the 6 gaps | M22 | 30 × ~1.5 | **2.4 min** |
| 5 | build and the correctness gate first (`check.sh` legs R, L, C: every arm's answers and match lists equal the base's; the base equals libpcre2 10.46 through `tests/oracle/`'s local adapter); a pickable arm's answer failure FAILS the run | all | every arm | **~10 min** (INTERPRETATION: grid1's gate scaled) |
| | **required** | | | **≈ 88 min** |
| 6 | OPTIONAL: F2's perf pass on the K arms {walk, V1, A1} of every item-1 group (regime_eval §2.1 item 2) | CB corroboration (ungated) | | ~5 min |
| 7 | OPTIONAL: F2's streamed perf pass (hex-run, bounded, dfa-hat × 4 arms × prose/docs/code) | the panel's ask; no bar reads it | 36 rows × 0.6 s | < 1 min |
| 8 | OPTIONAL: a pre-scan TRIGGER PROBE: KEEP vs DROP (`-fno-req-byte`/`-fno-req-run` as the DROP arm) on DFA-route TUG cells with OPTIONAL presence | whether Q-WR-9's trigger fires (no row is built from it) | 36 group-arms | ~2 min |
| | **with the optional items** | | | **≈ 96 min**, plus quiet-gate waits |

- **Perf is never required** (D166 add. 1). Items 6-7 skip loudly when counters are
  unavailable (`F2_SKIPPED`, the set header's `counters skipped:perf_event_paranoid=N`),
  and nothing downstream changes. **The paranoid SUGGESTION** (D166 add. 1.1): when
  counters are unavailable, `slot.sh`, `time.sh` and `f2perf.sh` print, to the log and
  the pass's status file, the current `kernel.perf_event_paranoid` (`?` if unreadable),
  that 2 or lower enables the optional pass, what it adds (branch misses, the
  predictability diagnosis), and the commands (one-off `sudo sysctl
  kernel.perf_event_paranoid=2`; persistent `/etc/sysctl.d/99-perf.conf` with
  `kernel.perf_event_paranoid = 2`). The scripts never run `sysctl` or `sudo` and never
  write under `/etc`. `[rev2]` regime_eval §1.2 puts this change in E4; grid2 runs
  first, so it moves into grid2's PREP lane, with its check (the text appears when the
  probe is forced to fail; the skip reaches the provenance; no `sysctl`/`sudo` in the
  scripts). This box reads 2, so items 6-7 run here.
- **Prep (a lane, before the slot):** `mkvar.py`'s three new variants (dispatch scaffold
  with forced `f`, NONE, V1 one-term), the one-byte and NONE cell manifests, the streamed
  subject generator for item 1 (the same generator E4 uses), the suggestion text and its
  check. Nothing in prep moves pcrec bytes.
- **Outputs** stay in the kit's slot directory (gitignored); E4b reads the logs; the set
  file is written at M0 by the converter (`set_to_measures.py`, regime_eval E14), with
  each row's `deps` computed by R-MS3 then. A form changed between the slot and M0 makes
  its rows STALE, carried and flagged (D166 add. 2).
- **Option (A), for comparison (Q-R17P-9):** keep the constants in grid1's own subject
  condition (mostly repeated 64 KiB) by re-timing F1/F3 in it as well: +~80 min (grid1's
  own estimate, 79.9 min), ≈ 176 min in all.

### 5.5 How the set reaches the build

- **B0-B3b read no set** (§3.2). The shadow and `regime_pick` read the kit's interim TSV
  (Q-REVAL-10) as a test input.
- **B4 reads the LATEST committed set** (D166 add. 2: the latest until M2). If grid2 and
  M0 both precede B4, that is `zen4-grid2`, and B4's census contains its selections: ONE
  abi event. grid1 is never embedded (a provisional design-time set).
- **If B4 precedes grid2** (not recommended), B4 reads grid1 through M0: R0 fires, R1/R2
  are unpaid (M16-M18 absent), and grid2's later landing is a default-set change, its own
  abi event with its `MOVERS.tsv` (measure_sets §3.6).
- **Zen 1 (F5)** gets its own set through a bench window; selections for a Zen 1 target
  read that set, never Zen 4's. The generic envelope becomes the default only at M2
  (D166 add. 2, D161 add. 12).

---

## 6. R17-b″'s seam: the iterator rows, A3, H, the presence carry, the cut-off `[rev2]`

The D165 iterator (`rx_iter`, `<prefix>_next`, findall_iter.md) adds a body of kind
`MF_BODY_ITER`. Nothing in the table is rebuilt; the iterator makes rows reachable:

- **The H rows.** R3a, R3b and R4 (`needs ∋ KN_H`) are listed now and skipped in a one-shot
  body; in a `next` body H is available (the previous step's span; the block's popcount)
  and the same evaluation emits them, R3a/R3b as dispatch rows read at `next`'s entry, R4
  at the block's refill. R8 reads the step span L from H there instead of N. R3 stays
  PROVISIONAL (regime_tables rev 0.5) until F4/F7 measure the real iterator; their denies
  `fd-r3a`/`fd-r3b`/`fd-r4` are created then.
- **A3** is `__next_candidate__w32` over storage that persists in `rx_iter`'s buffer; the
  selector and per-form bodies are unchanged.
- **The presence carry.** A verdict "a REQUIRED presence span occurs at p ≥ start + omin"
  stays true for a later call while that call's `start ≤ p − omin`. One `size_t`
  `valid_until` = the minimum over REQUIRED spans of `p − omin` suffices; a single flag bit
  does not (winreq §2). Past it the next call re-verifies over `[start + omin, n)`, which
  finds the next occurrence or ends the stream (EMPTY = NOMATCH for the rest).
- **The per-candidate cut-off (Q-WR-6, a PERMISSION).** With the carry, find-all scans each
  presence span once in total rather than once per call, which removes walk_survey's K5
  quadratic; the stream may also end at a candidate `c > p − omin + head_max` (§4.4).
  Exercised only after D165's build; never required.
- **The kit's state row: 40 B, align 8:** `base`, `top` (`size_t`), the u64 mask (24 B,
  D165 add. 1), the previous step span (8 B, H) and `valid_until` (8 B). The form byte is
  RECOMPUTED at each `next` entry from N and H, not stored (storing it would pad to
  48 B). Zero-init writes the row's declared 40 B, never a memset of S (D165 item 5 and
  its add. 1 reading).
- **S** (findall_iter.md §1.3 sums the rows held at once on a path): today's table is
  kit-find 24 + kit-H 8 + pcrec's K5 pair hits 16 + the reseed hint 8 = 56 B. With the
  merge (§1.1) presence is the kit's from B3b, so pcrec's 16 B pair-hit row has no pcrec
  emitter left to own it, and the kit's 8 B carry replaces it: S = 40 + 8 = **48 B**. If
  pcrec keeps its row, S = 40 + 16 + 8 = 64 B. Q-WR-6's "S is raised once to 40 B" is
  read here as the KIT'S row; S itself is pcrec's (Q-R17P-10).
- **Acceptance** carries F4 (the iterator reproduces A3's hand-edit win), F7 (H's
  observation cost against its regret), D165's named parity gate (dense tiny matches at
  parity or better), and SW-16's plant (S979).

---

## 7. Questions

### 7.1 Revision 1's Q-R17P-1..8: CLOSED `[rev2]`

| id | question | closed by | outcome |
|---|---|---|---|
| Q-R17P-1 | `MEMFN_FORMS` vs forms-per-site | main's acceptance of the kit's revised proposal (kit journal 2026-10-14); R-20 R-MS4 | forms-per-site go to `--emit-facts` (the section `memfn`); `MEMFN_FORMS` keeps its ruled SIMD-only meaning (match_api §6.3.10¶3-4, D147 add. 10) |
| Q-R17P-2 | the `<PREFIX>_MEASURES` stamp | measure_sets rev 2.1 §3.5-§3.6 | `""` when nothing consulted, else `id@rev:digest16` (stamp-on-load), mirrored in `rx_info.measures`, ONE abi event at M0 that rides R17-b′'s (B4); rev 1's `"none"` withdrawn |
| Q-R17P-3 | the pay rule | D161 add. 13 (rows are the kit's until lockdown) | STANDS as the kit's design (§2.5); [REGIME-TWIN] measures the dispatch it gates |
| Q-R17P-4 | the acceptance gate | Q-REVAL-1 and Q-REVAL-11 (ruled) | [REGIME-EVAL]'s loose pre-registered per-regime bars replace D162 add. 1's no-loss gate for the routing commit, which waits for PASS or PROVISIONAL PASS; the official verdict stays the bench on targeted hardware (D144 add. 4) |
| Q-R17P-5 | the set's channel | R-20 R-MS1 | per compile, on `mf_art_begin`; the analysis object stays as D162 placed it |
| Q-R17P-6 | [MEASURE-SET] phasing | measure_sets §10.1 | [KNOW-SRC] K0-K3 first; M0 rides R17-b′ with R-MS1/2/3/5; M1 (`--measures=`) at the first second set; `--list-finder` withdrawn |
| Q-R17P-7 | the first set needs a run | regime_eval §2.1 (grid2 is the kit's next slot); D166 add. 2 | zen4-grid2; refined by §3.2: the first delivery needs no set at all |
| Q-R17P-8 | site kind, and R1/R2's transfer | R-19 (gated), then R-21 Q-WR-8 (ungated for categorical kinds; `consumer` replaced at S3) | `site_kind` stated at B2 (§4.2); R1/R2's PF-measured crossover applies to every kind, labelled "measured on PF", until per-kind keys exist (a card edit) |

### 7.2 New questions, each with a recommendation `[rev2]`

**Q-R17P-9 (main; the kit owns regime_eval but main ruled its questions). grid2's fit
condition.** D166's one-run rule forces a new run (rev 1 F8), and regime_eval §2.1 asks
grid2 to re-time the 149 fit groups STREAMED as the in-sample reference, while keeping the
constants from grid1's mostly repeated subjects (its streamed RE-FIT is filed behind
P-PRED).
- **(B) Recommended:** one condition. grid2's streamed cells give BOTH the set's constants
  and R_in. The fit then sits in the judge's own condition (the judge is streamed), R_in is
  in-sample in the literal sense, and the run is ~96 min.
- (A) Constants re-timed in grid1's condition AND a streamed pass for R_in: ~176 min, and
  the in-sample reference is computed on cells the constants were not fit on.
- What (B) costs: regime_tables §3's S0 row (reproduced exactly on grid1) is re-derived on
  grid2, and grid1's prototype figures stop being directly comparable. Nothing gated reads
  grid1 after B4.

**Q-R17P-10 (main, findall_iter's owner). S under the merge.** The kit's row goes 32 →
40 B (Q-WR-6). pcrec's 16 B K5 pair-hit row loses its owner when presence becomes the
kit's (§6). Recommendation: retire it, S = 48 B (from 56), one S change at the iterator's
own abi event. If a path the merge does not cover still needs it (the compound route is
the candidate; its parts inherit the merge), S = 64 B.

**Q-R17P-11 (main). The fifth priced pick.** KW-8 ports five picks into the kit. The
landmark admission (`req_landmark_admits`) chooses between the landmark and the start set,
which under framing (a) (Q-WR-5) is a choice of ORIGIN, pcrec's only choice (D161 add. 9).
Recommendation: it stays pcrec's; the kit computes it in the B3a shadow only, as evidence
for framing (b), where it becomes a span choice and the kit's.

**Q-R17P-12 (main). The PF comment's `-fcomments` move.** Q-WR-11 rules the comment
method-neutral in pcrec with no `-fcomments` byte move, but any change to its text moves
every `-fcomments` artifact carrying it, and emitted comments are scaffolding (an abi
event, D76). Recommendation: change it in B4's commit, so it rides the abi event that
happens anyway and B2 stays zero-mover on every arm.

**Q-R17P-13 (main). Routing before the judge.** Q-REVAL-11 says the routing commit waits
for PASS. Recommendation: read it as gating the first commit whose picks MOVE a byte
(B4); B2 and B3b route only rows that reproduce today and are gated by byte identity and
the shadow comparator, so the one-byte and presence migration proceeds while the judge
runs. LOCKDOWN stays at B4.

**Q-R17P-14 (main, measure_sets' owner). The `libc:` dependency owner.** §5.3:
recommendation, `libc:<name>@<version>` as provenance in `deps`, and a SET-level
`libc-mismatch` listing flag (as `compiler-mismatch`), never row staleness, because the
artifact runs against the caller's library.

---

## 8. Denies, controls and sabotage

### 8.1 G1: pcrec's gate, by step `[rev2]`

- **B0-B3b:** byte identity over emit_sweep's full population, every stream (incl.
  `--emit-facts`), the start arms, `-e utf8`, `--engine=vm`, the lowsize/lowboth variants,
  at SIMD-off and SIMD-on: 0 movers. The trace SET compare admits only the new `fd`
  shadow records. No timing.
- **B4 (rev 1 §6.2, kept):** the population is a pcrec-side artifact diff (the census
  reader extended), never the kit's `moved`. SIMD-off: default against
  `--memfn=no-pf-terms-mask` (the whole move against main's walk), against
  `--memfn=no-fd-r0` (R0's own effect on its population), against `--memfn=no-fd-ndisp`
  (the dispatch's, if paid). Kit tier on the Linux dev box (D144 add. 1): taskset-pinned,
  A/A, layout-perturbed pairs (the I-148 corrigendum's rule). Both layers reported.
- **B6:** `-fmemfn-simd` against `-fmemfn-simd --memfn=no-pf-terms-w32` (A1's effect) and
  against both W64 denies (the SIMD layer against the CURRENT scalar, D147).

### 8.2 G2 and the every-set answer test (rev 1 §6.3-§6.4, kept; `[rev2]` families added)

- **Thresholds and spans** (B4): generated sets × synthetic thresholds N1 ∈ {0, 1, 7, 8,
  35, 36, 63, 64, 65, SIZE_MAX} × (n, start) incl. `n − start` ∈ {N1−1, N1, N1+1} and
  `start > n`; every answer against the byte loop; the chosen form against an INDEPENDENT
  evaluation of the declared rows (the G2 script parses the set file and the listing
  itself, never the kit's resolver). D27-blinded, as before.
- **W64 candidate sequences** (B6): setfind §12.2's `lo` sequences at W = 64, guard
  pages, ASan, UBSan.
- **Form-independence of the cache** (B4): a test build flips `f` between uses; answers
  stay equal.
- `[rev2]` **One-byte family** (B2, KW-10): the count rule; NONE's answer identity at DFA
  consumers (through the shadow until B5); NONE refused where `need` is REQUIRED; MLINE's
  generic shape and its LOOP_EXIT refusal under `fd-d1`.
- `[rev2]` **Presence family** (B3b, KW-10): absent-at-end discovered lazily; REQUIRED-all
  on proof routes; EMPTY before the first element; re-asked ranges with `omin` ≥ 0 at a
  raised `start`; plants reach NON-DFA routes only.
- **`make test-memfn-sets`** (B4, in TEST_SECTIONS): the R17-b mover population 1 in 8
  plus every `.rxt` cell for those patterns, compiled under every committed set and the
  synthetic extremes `all-walk` (N1 = SIZE_MAX), `all-v1` (N1 = 0, R0 off), `all-wide`
  (N1 = N2 = 0) and measure_sets §8.1's dispatch-carrying set, reached through the harness
  lever (`build/pcrec-harness --harness=measures=FILE`) until M1. The answer arm runs the
  harness's oracle-verified expectations (a per-form corpus differential); the structural
  arm checks each artifact's `__form__*` literals against an independent parser of the set
  file, the stamp names the loaded set, and a REACH floor per dispatch arm is met on
  generated boundary subjects (measure_sets F7: 97.8% of corpus subjects are under 36 B).

### 8.3 Sabotage, by step `[rev2]`

Ids: S911-S922 (R17-b′, allocated; R-19's rows are inside it) and S964-S980 (R-21's
SW-1..SW-17, allocated). pcrec-side [MEASURE-SET] rows are S943-S963 (main's). Ports
carry their own: R17-a's rows at B0 and R17-b's (S820-S843, S850-S854, S867-S870) at B4,
re-aimed by `scripts/sabotage_anchors.py --step` at each build. Main's rows anchored on
pcrec's encoding (`cand_derive`, `find_site`, the pre-check and handoff sites:
S266/S288/S294, S457-S477, S800-S814 among them) are re-aimed or re-run by the same tool
at B2 and B3b; the list is derived there, not counted here. Every presence plant must
reach a route with NO DFA scan in front, or it reads green vacuously.

| id | plant | detector | step | reach witness |
|---|---|---|---|---|
| S911 | a dispatch literal off by one | §8.2's structural arm; G2's form-choice check | B4/B8 | a paid dispatch site; UNREACHED (declared) while no set pays |
| S912 | the dispatch compare inverted | the same | B4/B8 | the same |
| S913 | the form byte never written (always 0) | the REACH floor per arm; the trace | B4/B8 | the same |
| S914 | the bounded walk arm ignores `end_back` | answers (G2, corpus bounded cells); ASan over-read | B4 | a bounded set site (`[a-z]+\b`) |
| S915 | the walk arm passed the wrong table (`start_bytes` vs `can_begin_match`) | answers on dfa-hat cells | B4 | a DFA-hat set site |
| S916 | R0 counts EQ terms as RANGE | movers by ID against `census_shapes.py` | B4 | a (2,1,0)-shaped cover |
| S917 | an ABSENT set key read as 0 | the totality test (the key removed ⇒ the next row/R7) | B1 (regime_pick, shadow), B4 | R0's key |
| S918 | the pay rule ignores C_disp | the per-set expected-emission manifest | B4/B8 | a set with a failing C_disp |
| S919 | `body` UNSTATED read as ONESHOT | G2: N/M rows must skip (an oracle case; the trace) | B1 | a builder with `body` 0 (a G2 site) |
| S920 | the START hook's text replaced by `0` | the structural arm: `__form(`'s argument equals the builder's stated start; the trace | B1 (stated), B4 (read) | a relocate-path site (start ≠ 0) |
| S921 | the shadow call emits a byte | emit_sweep's 1-in-8 sample at SIMD-off | B1 | every FIND site |
| S922 | `fd_route` routes a SHADOW group early (the set group at B2) | emit_sweep: V1 movers appear | B2 | a one-RANGE-term set site (`[0-9]+x`) |
| S964 | SW-1 K65-narrow: a REQUIRED set answered by one member on a no-DFA route | give-up (W1) | B3b | W1 |
| S965 | SW-2 K66-window: a REQUIRED run answered by its window | give-up | B3b | K66's regression (`k66_precheck_whole_run.rxt`) |
| S966 | SW-3 decided-late: a candidate yielded before every REQUIRED span is verified | give-up (G-2) | B3b | W1 with the VM hat |
| S967 | SW-4 edge-first: the edge attempt emitted before the verdict | give-up (W2) | B3b | W2 |
| S968 | SW-5 an unconstrained reply where span 0 is REQUIRED (NONE at VM_ATTEMPT) | give-up (W3, GIVEUP1 F5) | B4 (the VM hat routes) | W3 |
| S969 | SW-6 `omin` mis-signed | answers | B5 (UNREACHED while every `omin` is 0, declared) | a true-`omin` site |
| S970 | SW-7 the unbounded one-byte row loses its `pos ≥ n` guard | ASan over-read | B2 | a `(NULL, 0)` subject on `memchr` PF |
| S971 | SW-8 the bounded row loses the `n − 1` clamp / wrapper | ASan | B2 | a `memchr-bounded` site |
| S972 | SW-9 the DFA hat's re-seed after a moved skip dropped | lost match (ssedge's mutants) | B2 | `first-memchr-bounded` |
| S973 | SW-10 the VM hat at \|S\| = 1 rendered with memchr per attempt | structural census only, declared (perf-only, Q-R5) | B2 (trace), B4 (bytes) | `(x[a-z]+)y\1` |
| S974 | SW-11 the read-back says "scan present" when NONE was chosen | give-up (K65) via G1 on a proof-only route | B5 (UNREACHED until F0 fires) | a NONE site beside a REQUIRED span |
| S975 | SW-12 `MEMFN_LIBC` omits a libc symbol the text still calls | C11 `nm -u` | B2 | any LIBC site |
| S976 | SW-13 the libc row used under a stale `libc:` key | the `libc-mismatch` listing flag (§5.3) | B5 | F1's keys |
| S977 | SW-14 MLINE's stream opens at the edge, reading `s[start − 1]` at offset 0 | ASan | B2 | a `(?m)^` site at `search_from` 0 |
| S978 | SW-15 the pre-scan row prices from a `prior-*` kind as if measured | the listing / per-set manifest | B5 (at Q-WR-9's trigger) | P1 |
| S979 | SW-16 a carried presence verdict not invalidated when `start > valid_until` | answers | B9 (R17-b″) | an iterator over a late occurrence |
| S980 | SW-17 member order swapped in a tie (PR-7) | the B3a shadow comparator, not answers | B3a | a tie between two set members |

Rev 1's SB6 (the W64 tail read), SB11 (the SIMD-on use differs; C18 already detects it)
and SB12 (w32 routes `f == 1` to W64) move to B6, which requests its own ids; SB10 (the
stamp names the wrong set) is [MEASURE-SET]'s (S943-S963).

---

## 9. Acceptance

### 9.1 The first delivery (B0-B3b) `[rev2]`

Accepted on structure, not on timing: 0 movers at both layers over the full population
(§8.1), the reader shadow's equality (B1-B2), the five-pick shadow at 100% (B3a), the G2
families green, every sabotage row of B0-B3b DETECTED solo (or UNREACHED with its
derivation), `make test` green through `scripts/perfrun`.

### 9.2 B4, the routing commit

1. [REGIME-EVAL]'s pre-registered bars (G0-G4 per layer and shipped filter) PASS or
   PROVISIONAL PASS on the judge populations (J1 open, J2a), the table's listing hash
   recorded (regime_eval §5.2).
2. G1 at both layers on the mover population: R0 cells NULL against the walk; every
   dispatch interval holds against its neighbour (if paid); the dispatch charge NULL on
   LINER and TUG cells; no cell worse than R17-b beyond the floor.
3. The named residual REPORTED, never gated: bounded dense find-all, dfa-hat on prose
   (F7), dig on digits, vm-hat prose1m.
4. The official verdict is a bench run on the targeted hardware (D144 add. 4).

### 9.3 Predictions (rev 1 §7.2, carried; re-stated on grid2 at B4)

- R0 turns hex-run and word-eq to NULL (−14 REG, −4 WIN; the OFF loss falls 67,741 ns,
  5.5%). R1, if paid, turns most of bounded short find-all. Everything else stays as
  R17-b had it, including the named residual (1.17 ms OFF).
- dfa-hat prose contradicts R6 (g = 10.2 B above every g\*, yet it loses: near-hit depth,
  F7).
- Regret on the grid stays S0's exactly (R0, R1, R2 change no find-all grid row).
- `[rev2]` The one-byte and presence steps carry no timing prediction: they move nothing.
  Their value is coverage: with D161 add. 14, 170 of 172 compiled rwquest questions have a
  start-search site under one window request (sbscope §7), against ~42 for the set-FIND
  table alone.

### 9.4 What refutes it

- A byte moved at B0-B3b, or the five-pick shadow disagreeing anywhere.
- A K65 conversion lost: W1 or W2 gives up where main answers.
- An R0 cell not NULL against the walk; a dispatch interval losing to its neighbour; a
  non-NULL dispatch charge on a cell the dispatch does not help; any cell worse than R17-b.
- At SIMD-on, a W64 interval losing to V1 (D147's check).
- On Zen 1 the crossovers move: that refutes nothing on Zen 4, and is why Zen 1 gets its
  own set.

---

## 10. Standing design questions (docs/design/CLAUDE.md)

1. **The measurement regime: RELEVANT** (from B4 on; B0-B3b read no measurement).
   - Every value B4 reads is one Zen 4 run (7700X, CPU 14, gcc 15.2 `-O2`, governor
     performance), `kit-grid@2`, streamed subjects under Q-R17P-9 (B); member-free single
     calls for F, crossovers and the dispatch twins; find-all passes for g\*, c_cold, the
     per-use cost and g_none.
   - Regimes that would flip a decision: Zen 1's 2×128 AVX2 moves every W64 row (F5, its
     own set); fresh irregular landings move g\* down 2-4× (gridread §5.3); single calls
     with landings move R1's crossover past 32 B (§4.3); near-hit text flips V1 against
     the grid (F7); repeated against streamed subjects moves the walk's branch misses from
     150-250 to 0.4-22 per KiB (gridread F2), which is why Q-R17P-9 fits on streamed cells.
   - The libc rows are measured against the build box's glibc while the artifact runs on
     the caller's library (§5.3): a different libc can flip F1, so the set says which one
     it measured.
   - NONE's effort depends on the consumer's own per-byte step (≈ u for the DFA on this
     box, INTERPRETATION): a box where the DFA step differs from the walk moves g_none.
   - The dispatch charges are twins until [REGIME-TWIN] measures the built dispatch
     (§2.5).
2. **The independent control: RELEVANT.**
   - **B0-B3b:** byte identity by emit_sweep (pcrec's tool, sharing nothing with the
     kit's renderers); the five-pick shadow compares the kit's PORTS against pcrec's own
     functions (subject: the port; expectation: pcrec's code); the reader shadow compares
     each pcrec reader fed by its own row with the same reader fed by the kit's facts;
     PR-11's census of collapsed hybrids shares no source with the req walk.
   - **The table's semantics** are checked against the D27-blinded oracle (E3b,
     regime_eval §5.4), never against itself; the E4 agreement check proves only the
     plumbing and says so.
   - **Answers**: G2 against the byte loop over a generated space; `test-memfn-sets`
     against the harness's libpcre2/python-verified expectations, with extreme sets that
     force each form so a wrong form cannot hide behind a dispatch.
   - **Populations** (K35): counted by pcrec-side readers of emitted C (`census_shapes.py`,
     sbscope's and pcscope's censuses), each step re-counting its own; never the kit's
     `moved`.
   - **Reach** ([MECH-REACH]): every plant in §8.3 names a witness that reaches its site;
     presence plants reach NON-DFA routes (W1-W3), since a DFA-route-only green is
     vacuous; rows whose site is unreachable before a step are declared UNREACHED with
     the step that reaches them.
   - **The unavoidable shared source** is the measured numbers' own truth: controlled by
     per-group A/A floors, the NULL rule and the held-out judge, not by this design.
3. **What moves when the data is regenerated: RELEVANT.**
   - **Through B3b, nothing:** no ROUTED row reads a measurement; the PRES picks read
     the frequency kind, so a FINDINGS bundle change moves them exactly as it moves
     today's pcrec picks, censused by [KNOW-SRC]'s one tool.
   - **From B4:** a new DEFAULT set moves the dispatch literals, R0's verdict per shape,
     and `<PREFIX>_MEASURES` on every consulting artifact: an abi event with its
     `MOVERS.tsv` in the same commit (D162 ruling 1, measure_sets §3.6). A new non-default
     set moves nothing. A kit form-body change stales its rows, carried and flagged
     (D166 add. 2). A libc version change is a set-level flag (§5.3).
   - **Spec (D80):** every step's hunks are in §3.4, including the registry event at B3b
     (bit 45 retired) that moves no artifact byte.

---

## 11. Findings

Rev 1's, as they stand now:
- **F1. One stateful site per artifact, corpus-wide** (996 byte / 2,910 byte-vm R17-b
  movers). `[rev2]` The merge keeps it: presence and find are one site (§1.1).
- **F2. The scaffold is not free in code** (−3..+14 instructions, 0 of 6 identical):
  C_scaffold is M18, measured, never assumed.
- **F3. Forms-per-site in `MEMFN_FORMS` conflicted with the ruled spec.** RESOLVED
  (Q-R17P-1): `--emit-facts`.
- **F4. M is fixed per entry body.** `[rev2]` Now a stated fact (R-19).
- **F5. A SIMD W64 arm can be added only where the SIMD-off text routes through
  `__next`.** Unchanged.
- **F6. R0 keyed by exact shape would miss `\w`** (179 of 219). Unchanged.
- **F7. ALPHA's residual is not all E's** (dfa-hat prose: near-hit depth). Unchanged.
- **F8. D166's one-run rule makes the dispatch impossible on grid1 data.** `[rev2]` Its
  consequence is narrowed by F10.
- **F9. Two R17-b statements hold only at SIMD-off.** Unchanged.

`[rev2]` New:
- **F10. The first delivery needs no measurement set** (§3.2). With a routing state per
  group, every routed row through B3b reads no set value, so B0-B3b ship before grid2,
  M0 and the judge.
- **F11. Presence `omin` measured from the MATCH START** (not from span 0) is what makes
  B3's window exactly today's `[posvar, n)` and keeps every read at or after the
  activation's start; measured from span 0 the window would widen to `[lo − h_max, n)`,
  a mover. It refines C-1 and is why PR-6's "0 is a sound under-estimate" holds for a
  landmark origin too (§4.1).
- **F12. Proven facts are decided once per site, at layer OFF** (§1.5 rule 1): D161
  add. 8 plus the floor rule. NONE is the first row it constrains.
- **F13. R1 must read the crossover against the TERMINAL pick.** Rev 1 read V1-vs-walk
  regardless, which would have attached a dispatch to one-byte LIBC sites the moment grid2
  paid the set sites; read against the terminal, the missing `LIBC`/`WALK` key keeps them
  zero-mover with no special case (§1.3).
- **F14. KW-8's fifth pick is an ORIGIN choice** under framing (a), so the kit ports four
  picks and shadows the fifth (Q-R17P-11).
- **F15. Q-WR-11's "no `-fcomments` byte move" cannot hold if the comment's text
  changes**; the change rides B4 (Q-R17P-12).
- **F16. findall_iter's S table lists a pcrec K5 pair-hit row** that loses its owner under
  the merge; S = 48 B if it retires (Q-R17P-10).
- **F17. `libc:` provenance cannot be row staleness**: the run-time library is the
  caller's (§5.3, Q-R17P-14).
- **F18. regime_eval puts the paranoid suggestion in E4, but grid2 runs before E4**; it
  moves into grid2's prep (§5.4).
- **F19. R-19's three FIND storage points omit the PRE composite's entry**
  (`pcrec_emit_req_byte_check`), which the merge needs as the site's first use; winreq
  §1.1 asked, and §2.1 assumes R-19's "every builder" covers it.
- **F20. One-byte sites are zero-mover against BOTH branches, set sites only against
  main**: the kit branch's R17-b already moved the set sites (its abi 77), so the
  baseline of every census in this plan is main (Q-WR-10).
- **F21. A row whose quantities grid2 measures cannot be source at B4 unless its movers
  are B4's.** grid2 measures M19-M22 so that F0/F1 can be judged; if those rows were
  source when grid2 becomes the default set, they would fire at B4 and fold one-byte and
  NONE movers into the routing commit's census. So F0, F1 and P1 are built at B5, after
  lockdown, as formal additions (§1.3).

---

## 12. Charter vs committed `[rev2]`

| brief item | where | status |
|---|---|---|
| Read BOILERPLATE, memfn/CLAUDE.md; design against MAIN | §0 preamble, §3 (B0 ports R17-a; MF_SITE_ABI from main's 10) | done |
| Fold R-19, R-20 (R-MS1..5), R-21 (PR-1..11, ST1-ST6, S964-S980) | §3.1 (every PR item placed), §4.2, §4.7, §8.3 | done |
| Fold D161 add. 11-15 (incl. Q-WR-1/2/3/6/9), add. 8/10, D166 + add. 1/1.1/2, [KNOW-SRC], D157, D162, D165 (+ add. 1), D147, D76/D94, D80 | §R2 maps each to its section | done |
| Fold winreq (lists, ids, Q-WR answers), sbscope/pcscope (facts, W1-W4, G-1..G-5, census), regime_eval rev 2.2 (E3/E4, grid2 needs, F2, the suggestion), finder_history, regime_tables rev 0.5, measure_sets rev 2.1, window_contract | §1, §3, §4, §5, §8 | done |
| 1. Scope and rows: set FIND, one-byte stops, presence + handoffs; R0-R8 + the libc row with `libc:` deps, libc-free one-byte forms, MLINE, NONE where safe, the pre-scan row; the Q-WR-1 defaults; each row's needs/condition/pick/unpaid/deny | §1.1, §1.3 (15 FIND rows), §1.4 (6 PRES rows), §5.3 | done (21 rows designed; 18 locked at B4, F0/F1/P1 formal additions at B5) |
| 2. The step plan: ST1-ST6, R-19, R-20, E3/E4 in one order; per step zero-mover status and why, abi event with readers by grep, spec hunks, denies and floor pins, G1/G2/sabotage, dependencies (E-1, D165, [KNOW-SRC]); first delivery zero-mover with the five-pick shadow; movers later, each censused | §3.1-§3.5 | done |
| 3. The contract: presence class, range binding, EMPTY = NOMATCH, the unconstrained reply as a range, the proven-facts channel with the six readers mapped and no per-form read-back, the K65 obligation per consumer, C-items cited | §4.1-§4.8 | done |
| 4. Measurements keyed (quantity, form, site kind), relative, present vs ABSENT, method cards; ONE grid2 slot spec with wall time incl. regime_eval's streamed cells, the optional F2 pass and the paranoid suggestion | §5.1-§5.5 (23 families, 8 ABSENT; ≈ 88 min required, ≈ 96 with optional) | done |
| 5. R17-b″'s seam: iterator rows, A3, H, presence carry, the cut-off (S = 40 B kit row) | §6 | done (S's total raised as Q-R17P-10) |
| 6. Only NEW questions (Q-R17P-9..); rev 1's closed with rulings | §7.1 (eight closed), §7.2 (six new) | done |
| 7. Standing questions answered; this checklist | §10, §12 | done |
| `[rev2]` markers, change log, memfn/CLAUDE.md + r17b_prime/CLAUDE.md, the lane report | §R2; `docs/design/memfn/CLAUDE.md`; `r17b_prime/CLAUDE.md`; `docs/dev/lanes/r17bp3_report.md` | done |
| DESIGN ONLY: no `src/`/`memfn/src/` change, no measured constants in source, no timing | nothing under `src/`, `memfn/`, `tests/`, `lib/` changed | done |
