# pricesurvey: pricing STRATEGY as well as TACTICS (stage 1, the survey)

Lane `pricesurvey` (branch `lane/memfn-pricesurvey`), 2026-10-31, cut from main `a3cc4de82`.
DESIGN SURVEY ONLY: read-only on code, no make, no builds, no box runs, no timing. Every "today" is
main `a3cc4de82` unless a cite names another commit. The unmerged stop-ranking study is read from
`lane/memfn-stopstudy` `fc6735cdf` (`docs/design/memfn/stop_ranking_study.md` rev 2, cited below as
"SRS"). Facts carry a file:line or a doc § cite; anything not read directly off a source is marked
**INFERENCE**. No design is proposed: §7 states forces and options only.

The brief's frame (Frank, 2026-10-31, relayed by the manager): one row per STRATEGY (no search,
one position + verify, pair, skip/Horspool, ...); each row finds its own best concrete option;
the cheapest row wins, ties to the simpler strategy; the full per-strategy ranking visible in a
trace. D176 is the agreed shape this extends (`docs/dev/decisions.md` D176).

---

## Summary

1. **Tasks (§1).** pcrec's generated matchers ask about 15 distinct search/scan questions. Eleven
   are kit-delegated site kinds in ONE table (`src/gen/memfn_sites.def:59-87`: PRE, OFS, VMRUN, PF,
   STAY, EDGE, VMSPAN, VMSTRIDE, MLINE, N7, COVER). The rest are pcrec-side decisions that pick
   the ROUTE before any kit site exists: the start table `cand_rows[]`
   (`src/gen/emit_dfa.c:10154`, slots LOCATE, PRESENCE, FIRST, NEXT, RETRY, BOUND, RECOVER,
   FINISH, WINDOW, WIDTH), the stay-skip state pick (`emit_dfa.c:5063`) and the scan-edge pick
   (`src/opt/scanedge.c`, longest first).
2. **Where pricing exists today.** Only INSIDE one kit site kind, the window family's stop choice
   (`memfn/src/window.c` Table A), and there in three different units (SRS §1.1: A-parked by
   member count, A-model by prefix_k's 1/100-cycle model, A-mass by rarity) plus one threshold
   (HORS_MIN, `memfn/src/plan_cost.def`, PROVISIONAL). Every other choice in §1 is first-match
   on applicability, a count proxy, or a structural threshold (e.g. `>= 192` stay bytes,
   `emit_dfa.c:5063`; `|S| == 1` for libc, `memfn/src/finder.c:281-285`).
3. **The strategy level is pcrec's today, and unpriced.** "No search" vs "search then verify" vs
   "reverse from the end" is decided by `cand_rows[]` first-match (LOCATE `empty`, `rev-end`,
   `cover`, `composite`; NEXT `run-pinned` ... `next-none`). `cover` wins wherever it applies
   (`emit_dfa.c:4846`), never against the composite's DFA scan on price; SRS §5.1 names this as
   the reason three acceptance witnesses (`[.,;]\d`, `[QXZ]{2}`, dense hex) cannot be fixed by
   the kit's price alone.
4. **Couplings (§4)** that make "best per strategy, then best strategy" inexact: the presence
   fold (D176 Q4), the consumer's per-false-entry cost `A_entry` and the MARGIN bar between
   alternatives (SRS §4.1, `window.c:669`), the verify term V(c) that depends on the stop, the
   joint survivor rate (`window_search_game.md` §5.3: independence under-predicts by 21x-1,750x),
   the engine route (no-search cost per byte differs 8-24x between DFA and VM consumers,
   costmodel §0.1), and pcrec-side readers of the chosen stop (G1, R4, landmark K; SRS §3.2).
5. **Data (§5-§6).** MEASURED today on the dev box (Zen 4): the walk's per-byte and per-use
   terms and the SIMD mask forms' (`measure_store/zen4-grid1/1/set.tsv`), the engines' C_call,
   c_byte and C_match (`docs/dev/lanes/armread_report.md` §1-§2), the consumed-byte terms per
   site kind (`docs/dev/lanes/costmodel_report.md` §0.1). Measured on ANOTHER box (Zen 1) and
   stale against the set's unit: every `plan_cost.def` scan row. UNMEASURED: libc memchr on
   Zen 4, the two-stream PAIR, the Horspool probe, verify per hit, the `vany` kernel (card exists,
   `memfn/data/cards/kit-kernels.tsv`), and above all the cost per byte of NOT searching, as a
   card. The rates are a single AUTHORED prior (`src/findings/default.rxt`), marginal only.
6. **The sharpest open question (§7)** is the one D161 addendum 6 closed: a "no search" row
   needs the CONSUMER's price, which was DROPPED from the kit contract ("it removes levers").
   Pricing strategies re-opens it, or moves the strategy choice to where the consumer price
   already lives (pcrec). Either way the multi-variable risk (§7.4) lands on three or four
   terms: `A_entry`, V, the survivor rate, and the noise band.

---

## Tasks

Columns: WHERE = the pcrec emitter that states the site (or decides without one) and the kit
code that answers; DECIDER = where a method/strategy is chosen, and in what form; FREQ = how
often the emitted code runs it (CALL = once per match call or activation; CAND = per candidate
or stop; BYTE = inside the per-byte engine loop; ATT = per anchored attempt); CONSUMES = what the
consumer reads from the answer.

| # | task | WHERE (pcrec / kit) | DECIDER | FREQ | CONSUMES |
|---|---|---|---|---|---|
| T1 | START CANDIDATE, DFA route ("next position a match can begin") | `pf_site_of` `emit_dfa.c:7095` (PF), `ofs_site_define` `:7586` (OFS), `window_reply_ask` `:7568` (the window site's phase-1 ask) / kit `window.c` Tables A-E (`mf_wdecide`), `finder.c` FIND slot (`fd_find`), `pffind.c`, `ofsskip.c` | pcrec: NEXT slot first-match (`cand_rows[]` rows `run-pinned-bounded` ... `next-none`, `emit_dfa.c:10154` + offsets 174-273 of the table); kit: Table A argmin-ish in three units + MARGIN + TIE (`window.c:406-700`), Table B first-match by member count/role (`finder.c:249-354`), Table D `D-hors`/`D-one` (`window.c:1587-1640`) | CAND (re-entered each time the machine returns to its start state, `memfn.h` MF_ENTRY_PARKED/RESEED, `memfn.h:541`) | a position, `CT_CAND` "next position that can start a match" (`emit_dfa.c` CT_* enum after `:9790`); entry PARKED or RESEED |
| T2 | REPORT / cover (find-then-verify the whole sub-problem, no engine) | `pcrec_cover_site` `src/gen/known.c:484`, `emit_cover` `emit_dfa.c:13860` / kit window family E-find + D-hors (`window.c` header lines 26-34) | pcrec: LOCATE slot `cover` row, predicate `locate_cover_applies` `emit_dfa.c:4846` (first-match, ahead of `composite`); kit: same Tables A-D as T1 | CALL (the whole walk once per call, budget 1, `memfn_sites.def:79-87`) with a CAND loop inside | the match START (`CT_START`), the whole match proven (D161 add. 8, add. 16) |
| T3 | PRESENCE pre-check (is every required byte/run in the subject at all) | `req_site_define` `emit_dfa.c:1531`, `req_pres_site` `:8692`, `req_run_member` `:1055` / kit `precheck.c` (ALL_PRESENT composite), `presence.c` (P3/P4/P2 ports), `finder.c` PRES slot P0-P9 (`:325-353`) | pcrec: PRESENCE slot rows `presence-none`, `one-attempt`, `dominated` (G1, `req_byte_dominated_by` `:8546`), `set-leads` (`req_set_leads_applies` `:8620`), `emitted`; kit: PRES rows, rarity picks (`presence.c` header: rarest member, ties to pattern order) | CALL (once per activation, before the first element, G-2: `memfn.h` MF_USE_ENTRY comment, lines 416-428) | a BOOL (absent -> NOMATCH; K65), or under ASSIGN the landmark's leftmost position (`memfn_sites.def` `entry` column, lines 39-57) |
| T4 | HANDOFF / landmark re-entry (start the scan at the required landmark minus K) | FIRST slot rows `handoff`, `handoff-attempts`, `handoff-attempts-entry` (table offsets 130-151); NEXT `handoff-reentry`, `pf_handoff_applies` `emit_dfa.c:9040`; landmark admission `req_landmark_admits` `:9016` / kit `precheck.c` (`precheck_assign*` rows) | pcrec: first-match, plus ONE inline prior comparison (`:9016-9025`: `(1e6 - k*landmark_ppm) * start_ppm > 1e6 * landmark_ppm`) | CALL (the pre-check's hit), then CAND | a lower bound `CT_LOWER` / `CT_HIT` |
| T5 | VM attempt SEEK (next position an attempt may start) | `vm_hat_find_of` `emit_dfa.c:8050`, NEXT row `first-class` (`pf_vm_start_applies` `:8026`) / kit `finder.c` D1w (one member: the walk) and R7w (set: the walk), `finder.c:291-326` | first-match by member count; the VM-seek role excludes libc (`D1` `SF_SEEK_ROLE` forbidden, `finder.c:281`) | ATT | a position; a VM attempt (C_match VM 0.2-1.5 ns at dense m, armread §2) |
| T6 | MLINE: `(?m)^` line-start seek | `mline_find_of` `emit_dfa.c:8353` / kit `pffind.c` `pf_memchr_back`, finder row D1c `finder.c:286-290` | one candidate row (D1c, libc back search, UNMEASURED-DEFAULT); Q-WR-2: "No NONE row for MLINE until measured" (D161 add. 15) | ATT | a position; context check `\n` at -1 is pcrec's edge (D161 add. 7) |
| T7 | ENG_ATTEMPT predecessor-byte skip (N12) | NEXT row `pred-memchr`, `cand_pred_memchr_applies` `emit_dfa.c:10070` (table offset 268) | first-match. **INFERENCE**: rendered through the MLINE/PF find path (`find_site` `emit_dfa.c:6864` accepts only DELEG_PF and DELEG_MLINE; the row "STAMPS memchr", table offset 263) | ATT | a position |
| T8 | DFA STAY-LOOP skip (forward and reverse) | `dir_fwd_skip` `emit_dfa.c:9171`, `dir_rev_skip` `:9202` (DELEG_STAY) / kit SKIP+ADVANCE through the generic arm (`memfn/src/generic.c:285`, `compose.c:1411`) | pcrec: `pick_skip_states` `emit_dfa.c:5063`: up to 4 states that stay on `>= 192` of 256 bytes (structural, "M2.10 ... REGRESSION ... Do not re-attempt without measuring the REVERSE machine", `:5054-5062`); kit: one arm, no choice | BYTE (inside the engine loop; budget LOOP, `memfn_sites.def:67`) | the position past the run of stay bytes (ADVANCE) |
| T9 | SCAN EDGE advance (a state that loops on a class runs as a scan) | `emit_scan_edge` `emit_dfa.c:12513` (DELEG_EDGE) / kit generic SKIP | pcrec: `src/opt/scanedge.c` "selection: longest first, no overlaps" (`:538`), at most `PCREC_MAX_SCAN_EDGES` 4 (`src/core/limits.def:395`, "an emitted-bytes budget awaiting a measured re-choice") | BYTE | position past the class run; reverse case = D161 add. 17's family |
| T10 | VM SPAN scan (cursor past a class run, stride 1 or W) | `vm_emit_span_scan` `src/gen/emit_vm.c:4839` (DELEG_VMSPAN / VMSTRIDE) / kit generic SKIP | pcrec: stride class; kit: one arm | BYTE (per VM step) | position |
| T11 | VERIFY a literal run at a known position | `vm_run_site` `emit_vm.c:4538` (DELEG_VMRUN); inside the window family as Table C (the verify plan, `window.c` header lines 19-21); inside `ofsskip.c` / `precheck.c` as the run compare | kit `runcmp.c` first-match rows `words`, `overlap`, `bytes`, `memcmp` (DERIVED from gcc's lowering, `runcmp.c` header); Table C's C-model is prefix_k's greedy verify pick (`window.c:834`) | CAND (window) / per VM step (VMRUN, budget LOOP) | a BOOL |
| T12 | MISMATCH: span compare against a run-time reference (backreference) | `residual_sites` `emit_dfa.c:3556` (DELEG_N7) / kit `mismatch.c` | one renderer, two rows by fold kind (`compose.c` comment lines 129-133) | per backref step (budget LOOP, `memfn_sites.def:24-27`) | the first differing offset |
| T13 | START RECOVERY / reverse search (find the match start from a known end or landmark) | RECOVER slot rows `pinned`, `end-minus-width`, `landing` (`start_landing_applies` `emit_dfa.c:9662`), `reverse-pass`; LOCATE `rev-end` (`locate_rev_end_applies` `:4835`) | pcrec first-match (`pcrec_fact_end_pin` for rev-end); D161 add. 17: "the walk is the kit's ... backward and forward", reverse DFA as scaffolding, not yet a kit site | once per match (CALL for rev-end) | `CT_START` |
| T14 | HYBRID RESEED policy (where the VM restarts after a DFA candidate) | RETRY slot rows `exact`, `clamped`, `retry-anchored`, `adaptive-dense` (`cand_rs_dense_applies` `emit_dfa.c:10087`: `cand_ppm * reseed_gap > 1e6`), `adaptive`, `fixed` | pcrec first-match; one prior comparison | CAND | a restart policy |
| T15 | REQUIRED-RUN check (SIMD prefilter over a run) | ofsskip FUNC PREFIX rows `vrun-w16`/`vrun-w32` (`memfn/src/vrun.c` header; `options.def` rows at lines 31-45) inside T1 (OFS) and T3 (pre-check FUNC parts) | kit `fn_rows[]` walk; KB second filter position from pcrec's ranking (`vrun.c` header "SECOND FILTER POSITION") | CAND / CALL | position (leftmost whole-run hit) |
| T16 | END WINDOW / bounds (not a search, a limit on where one runs) | WINDOW slot `window`/`window-none`, BOUND slot rows (table offsets 79-88, 342-369) | first-match | CALL | a clamp |

Notes on the table:
- The kit decides FORMS by first-match tables everywhere except Table A (`finder.c` header lines
  8-20: "one declared first-match table over (stop, form)"; `compose.c:134-147` `arms[]`; SKIP sites
  have no alternative to the generic arm today). **INFERENCE**: T8-T10 and T12 have no method choice
  to price yet, only pcrec's strategy-level choice (whether to emit the skip at all).
- D161 addendum 3 already reads T1, T2, T3, T4 and T6 as DEGENERATE CASES of one "search for the
  window" contract; D161 add. 14 ("the kit decides whether to scan at all, and libc is one optional
  row") puts "no pre-scan" inside that contract for T1/T3/T6, but no NONE row exists
  (`finder.c:249-326`: no row picks `FF_NONE`; MLINE "No NONE row ... until measured", D161 add. 15).
- Population sizes (D161 add. 14's kit correction, sbscope 2026-10-14, 177 blinded questions): 170
  have a start-search site; one-byte FIND 74; RUN-PRE 76; RUN-HANDOFF 50; NEXT-HANDOFF 25; OFS 46.
  b4close2 (plan row [MEMFN-POSCOST], `docs/dev/plan.md`): 603 walk-routed set sites.

---

## Strategies per task

Layer key: S = scalar layer (portable C, SWAR, libc; D147); V = SIMD layer (`-fmemfn-simd`,
off by default, `memfn/CLAUDE.md` "The layers"); S+V = both. Status key: BUILT (routed),
BUILT-UNROUTED, DESIGNED (a design doc, not built), FILED (a plan row with a trigger), IDEA
(`memfn/docs/ideas.md` only), CLOSED (measured and ruled out), BOONIES.

### 2.1 The strategy families, as the brief names them, mapped onto today

| strategy | what it is | where it exists today | status | layer |
|---|---|---|---|---|
| NO SEARCH | the engine reads every byte from the start state | NEXT `next-none` (`cand_rows[]` offset 271); LOCATE `composite` with no prefilter; PRESENCE `presence-none`; Table D's floor; the window family's floor row (`window.c` header lines 35-38) | BUILT (as the fall-through, never as a priced choice) | S |
| ONE POSITION + VERIFY | find one position's set, verify the rest | Table B D1 (libc memchr, one member), D1w / R7w (the walk), `pf_memchr*`, `pf_walk*` (`pffind.c`); OFS `memchr` stream + verify chain (`ofsskip.c` header); E-find (T2) | BUILT | S (libc is scalar, Q50) |
| ONE POSITION, wide mask | V1 SWAR (8 B), M64 / A1 / S1 / W64 (64 B), A3 (state kept across iterator calls) | `finder.c` rows R8, R2, R3b (forms not built: "hold no fact any compile states", `finder.c` header lines 21-27) | CLOSED as a default (`walk_vs_v1_record.md` §5); FILED under [MEMFN-REGIME] (`plan.md`) for a measured or stated regime | V1 = S (SWAR); A1/S1/W64/A3 = V |
| PAIR (two positions or two bytes) | (a) two memchr streams for a two-byte stop set ("leapfrog"); (b) a SIMD filter ANDing two positions (KA, KB) | (a) Table B `PAIR` (`finder.c:299-310`, UNMEASURED-DEFAULT, "no PAIR cost constant"); `ofsskip.c` PAIR leapfrog for a two-member cube; (b) `vrun.c` KB second filter | (a) BUILT for two-member stops; any-two-bytes widening FILED [MEMFN-PAIRSTOP] (`plan.md`); (b) BUILT | (a) S; arbitrary-pair kernel FILED [MEMFN-PAIRSIMD] (`plan.md`) V; (b) V |
| K-OF-SET kernel (find any of 2-3 bytes) | compare per member, OR, movemask | `memfn/src/vany.c` | BUILT-UNROUTED ("NOT ROUTED. No mf_site row", `vany.c` header); how pricing offers it is open (`docs/dev/lanes/simdset_report.md` "Open questions" 1) | V (body is a scalar byte loop) |
| k-STREAM memchr (3 members) | one memchr stream per member | SRS §6.4 unlock list | FILED in SRS only (trigger: step 0 shows `[jqz]`-shaped sites) | S |
| TWO-POSITION FILTER at fixed distance (needs joint rates) | test position i and j together before verifying | costmodel A.6's P2/P3 (SRS §6.4); `ideas.md` 2026-10-10 "a vector filter over a byte plus a class at another offset (ipv4 shape)" | IDEA / FILED-in-study (needs JOINT rates, D157's revisit clause) | S+V |
| SKIP (Horspool) | probe the window's last position, shift by a table | Table D `D-hors` (`window.c:1587-1640`), admission by `HORS_MIN` | BUILT (S3, deny `window-skip`, `options.def:103`); D176 Q2 RULED it becomes a priced METHOD, HORS_MIN deleted; not built | S |
| CHAIN (rare later span, then search back for the head span) | D161 add. 5: "a chain of 1-2 simple searches" | `window_search_game.md` §8 (P6 `refine`) | DESIGNED/studied; "rarely finds a plan" (§8.2); longer chains FILED as the chain's extension (D161 add. 5) | S |
| SUPERSET COVER (search a cheaper hull, verify exact) | `\w` through `[0-9]\|[A-z]` | [MEMFN-POSCOST] part 2 (`plan.md`); SRS §6.4 "one more GENERATOR row" | FILED (408 hulls counted, price never computed) | S+V |
| UNBOUNDED / PRESENCE-ONLY spans folded into the stop decider | D176 Q4 | [MEMFN-UNBOUNDED-SPANS] (`plan.md`) | FILED (an MF_SITE_ABI event) | S |
| REVERSE: from the end (rev-end) | seed the reverse DFA at `n` | LOCATE `rev-end` (`emit_dfa.c:4835`; [OPT-REVEND] `plan.md`) | BUILT | S |
| REVERSE: from a landmark (start recovery by a reverse walk) | reverse span / reverse DFA seeded at a landmark | D161 add. 17; RECOVER `landing`; rev-inner G3 (`where_to_start.md` §2.4, SRS §3.1 last row) | partially BUILT (one-run case: EDGE/STAY/VMSPAN `reverse`, D161 add. 17); rev-inner HELD ([ENG-TACTICS] `plan.md`) | S |
| HANDOFF (presence hit becomes the scan start) | T4 | FIRST/NEXT handoff rows | BUILT | S |
| BIT-PARALLEL locator (bitstreams, Parabix) | one u64 per condition per 64 B block | [SPAN-ISEL] (`plan.md`), [POS-PARALLEL] (`plan.md`) | FILED, "starts only on Frank's word" | V (portable IR) |
| ADAPTIVE run-time switch (walk <-> mask) | per-stretch or per-call mode switch | [MEMFN-SKIPSWITCH] | BOONIES (`plan.md`); adatwin −2.2% (`walk_vs_v1_record.md` §2) | S+V |
| BATCH matches / candidate ring / mask carry | keep a vector pass's mask across candidates | D161 add. 2; `ideas.md` 2026-10-10 "hold the candidate mask across calls", 2026-10-13 "BATCH MATCHES" | flattening CLOSED (`walk_vs_v1_record.md` §6); A3 row designed, form unbuilt | V |

### 2.2 Per task: what exists, what is filed

- **T1 start candidate.** BUILT: NEXT rows `run-pinned(-bounded)`, `offset-set(-bounded)`,
  `handoff-reentry`, `first-memchr-bounded`, `first-class(-bounded)`, `memchr(-bounded)`,
  `byte-class(-bounded)`, `next-none` (`cand_rows[]` offsets 174-273); inside the kit, Table A's
  stop rows A-parked / A-model / A-mass (`window.c:620-622`), Table B methods D1, D1w, PAIR, R7w
  (+ SIMD PREFIX rows `vrun-w16`/`w32`), Table D D-hors / D-one. FILED: priced argmin (D176 Q1),
  SKIP as a method (Q2), PAIRSTOP, PAIRSIMD, POSCOST, REGIME, UNBOUNDED-SPANS, k-stream, two-position
  filter. CLOSED: V1/M64 as default, flatten, adaptive (`walk_vs_v1_record.md` §6).
- **T2 REPORT/cover.** BUILT: E-find over Tables A-D; S3's witnesses where no kit method beats the
  composite's DFA scan (SRS §5.1 rows `[.,;]\d`, `[QXZ]{2}`, dense hex). FILED in SRS §5.1 item 1:
  "The old path is a priced candidate" (declining the window search as one more method row with
  its card). Not filed as a plan row (**INFERENCE** from a grep of `docs/dev/plan.md` for
  `old path`/`decline` near the D176 rows: none found).
- **T3 presence.** BUILT: memchr on the rarest necessary byte, the run's window, set-leads order,
  G1 drop (`presence.c` header). D176 Q4 RULED one decider with the stop; FILED
  [MEMFN-UNBOUNDED-SPANS]. Q-WR-9: "default KEEP unless the span's `need` is OPTIONAL and E is
  `measured`; pricing waits for ... a TUG cell measured losing for want of it" (D161 add. 15). The
  P9 row is "the total default: verify (Q-WR-9)" (`finder.c:349-353`).
- **T4 handoff.** BUILT; its K admission is a prior comparison (`emit_dfa.c:9016`). [PRIOR-COST-UNIFY]
  (`plan.md`, BLOCKED) lists it with G1, set-leads and R4 as one family of four dispersed
  prior-reading admissions.
- **T5 VM seek.** BUILT: the walk (D1w, R7w). FILED: V1 on the VM hat waits for [MEMFN-REGIME]
  ("it'll have its day", D169 addendum note).
- **T6/T7 MLINE, N12.** BUILT: libc back search (D1c), `pred-memchr`. FILED: "a measured libc-free
  back FIND beating libc on (?m)^ (B7, Q-WR-7)" (`finder.c:290`).
- **T8-T10 in-engine skips.** BUILT: scalar SKIP through the generic arm. IDEA: "rev-end's run loop:
  a backward vector scan" and "reverse class-run scans are scalar-only; the vector run could read
  backwards" (`ideas.md` 2026-10-10, 2026-10-29); D161 add. 17 withdrew the kit's sequence-scan
  widening "until a measurement asks for fused runs".
- **T11 verify.** BUILT: `runcmp.c` rows; vrun VERIFY TRIM (`vrun.c` header). FILED: verify order and
  form ([MEMFN-POSCOST] part 3); IDEA: "a vrun hit is checked three times; verify only what the
  filter did not prove" (`ideas.md` 2026-10-11); proofs from the find ([KIT-VERIFY] `plan.md`,
  D161 add. 16).
- **T13 reverse.** See 2.1's two REVERSE rows.
- **T14 reseed.** BUILT rows; R4 `adaptive-dense` is one of [PRIOR-COST-UNIFY]'s four.

---

## Variations per strategy

Split as the brief asks: **RATE** variations change how many stops (candidates) the strategy
yields; **SCAN** variations change only the cost of producing the same stops. A few change both
and are marked BOTH.

| strategy | RATE variations (stop rate moves) | SCAN-ONLY variations (same stops, different cost) | source |
|---|---|---|---|
| no search | none (every byte is "examined") | which engine/route consumes (DFA, hybrid, VM, attempt); table form (premultiplied, `emit_dfa.c` near `:4870` "[OPT-3] WHICH TABLE FORM"); in-engine stay skips (T8) and scan edges (T9) | costmodel §0.1 b_cons per site kind |
| one position + verify | which position d; which alternative (PARKED k0 vs RESEED walked offsets vs core); which set at d (exact, superset hull: POSCOST part 2); which byte of a run is "the member" (`@idx`, P2 in SRS §3.1); the statement's truncation (PCREC_MAX_REQ_RUN_SCAN 32, `memfn.h` comment lines 550-553 per SRS §2.4) | method row: libc / walk / PAIR / vany / V1 / W64 (S+V); layer; block width and unroll (D149: measured, derived, or `UNMEASURED DEFAULT:`); one-shot vs iterator (M key) and kept state (H key, A3); bounded vs unbounded range (`pf_memchr_bounded`, `pffind.c` header); verify ORDER (moves V, not stops: SRS §6.4 part 3); verify FORM (`runcmp.c` rows) | SRS §4.1-§4.2; `regime_tables.md` §2 |
| pair / two positions | which two positions and their distance; joint rate of the pair (unknown: independence errs 21x-1,750x, `window_search_game.md` §5.3) | two memchr streams (leapfrog) vs SIMD two-compare AND (KB) vs arbitrary-pair OR kernel; KB on/off when KA is very rare (`ideas.md` 2026-10-11, hypothesis) | `ofsskip.c` header; `vrun.c` header |
| K-of-set | which set (all members of one position) | k streams vs vany w16/w32 vs walk | `vany.c`; `kit-kernels.tsv` |
| skip (Horspool) | BOTH: the probe position (window's last core position) fixes which byte is examined; the shift table sh[] fixes how many bytes are never examined (E[sh] = Σ rate[b]·sh[b]) | probe cost c_probe; window width (`ideas.md` 2026-10-23 "widen it to the contiguous tested core run"); priced probe choice (`ideas.md` 2026-10-23) | SRS §4.1 skip formula; `s3_report.md` §6.5 |
| chain | which head span and which later span; gap bound | the tool per link | D161 add. 5; `window_search_game.md` §8 |
| superset cover | the hull (more stops: up to 8 extra members counted) | hull form (≤ 2 terms SWAR) | [MEMFN-POSCOST] |
| reverse / rev-end | origin choice (end, landmark); D161 add. 4/9: pcrec chooses the ORIGIN | reverse DFA vs reverse span vs reverse vector run | D161 add. 17 |
| presence | which necessary byte or run window (rarity is its price: SRS §3.2 "Rarity is therefore already its price") | memchr (fixed method) ; fold into the stop's first find (D176 Q4) | `presence.c` header |
| any strategy, call shape | none | DINGHY / TUG / LINER regime: per-call (C_call, `ccold`), per-use, per-byte terms dominate differently (costmodel §0.1: L* ≈ 13.8 B walk, g* ≈ 18.5 B); short calls can flip memchr vs walk at ~28,500 ppm (SRS §8 item 1) | costmodel §0.1; SRS §8 |

What the split shows (facts from the sources above): the prior's RATE side is what errs on real
text (one-position stop count within 0.3x-6.8x, multi-position survivors 21x-1,750x,
`window_search_game.md` §0 and §5.3); the SCAN side is what the measurement sets hold, at
noise bands of 0.17%-3.4% (`kit.eps.*` rows, `measure_store/zen4-grid1/1/set.tsv`).
**INFERENCE**: a price's error budget is dominated by the rate term, not the method term,
whenever two candidates differ in stop position.

---

## Couplings

A coupling is a place where one choice's price depends on another choice. "Best per strategy,
then best strategy" is exact only where the strategies' prices are separable; each row says
whether the coupling crosses strategy rows (CROSS) or stays inside one (INSIDE).

| # | coupling | what depends on what | crosses? | source |
|---|---|---|---|---|
| C1 | PRESENCE FOLD | the presence pass is dropped when the chosen stop's first find, scanned from the subject start, covers the presence byte: the presence price depends on the stop chosen (and its method's first-find reach) | CROSS (presence x every stop strategy) | D176 Q4; SRS §2.4 "The fold, one general rule" |
| C2 | CONSUMER COST PER FALSE ENTRY (`A_entry`) | a PARKED/RESEED candidate's price adds r(S)·π(c)·A_entry; 0 where the plan verifies every core position. So a strategy that verifies fully and one that hands candidates to the engine are priced in different terms | CROSS (verify-everything strategies vs engine-verify strategies) | SRS §4.1 formula; `plan_cost.def` C_ENTER (MEASURED x ASSUMED, Zen 1) |
| C3 | MARGIN between alternatives | a RESEED alternative wins only at `best·2 < base` (ARGUED); a bar, not a price | CROSS (PARKED vs RESEED) | `window.c:669-683`; `plan_cost.def` MATERIAL_NUM/DEN |
| C4 | VERIFY TERM V(c) | the expected verify per stop depends on the chosen stop's position (which positions remain to verify, in Table C's order) and on the verify plan (C-model's greedy pick) | INSIDE a strategy, but its size differs per strategy (skip divides V by E[sh]) | SRS §4.1 (V(c) = Σ v_i Π p_j); `window.c:834` |
| C5 | JOINT SURVIVAL | the survivor count of a multi-position plan is not the product of marginals; it cancels "inside one window whose plan verifies every core position" but NOT across alternatives or for partial plans | CROSS | SRS §4.1 "Why the survivor problem does not block this"; `window_search_game.md` §5.3 |
| C6 | ROUTE BEFORE PRICE | pcrec's LOCATE/NEXT/PRESENCE/FIRST rows are first-match; the kit prices only inside the route pcrec chose. `cover` applies whenever `pcrec_cover(cx)->why == NULL`; the composite's DFA scan is then never a candidate of the kit's price | CROSS (no-search vs every kit strategy) | `emit_dfa.c:4846`; SRS §5.1 item 1 |
| C7 | ENGINE DECIDES THE NO-SEARCH COST | the per-byte cost of consuming bytes is ~0.56 ns/B (DFA prefilter site), ~0.22 (DFA hat), ~4.6 (VM hat) against the walk's 0.185-0.189 skip; the same pattern declines a search under the DFA consumer and must search under the VM (syslogbase) | CROSS | costmodel §0.1 table (b_cons); `window_search_game.md` §5.4 |
| C8 | IN-ENGINE SKIPS vs START SEARCH | a stay skip is excluded on the start state when the prefilter owns it (`pick_skip_states(d, dir->prefilter_owns_start ? d->s0 : -1, ...)`, `emit_dfa.c:12690`); a state carrying a scan edge is not skip-eligible (`:5091-5095`). So "no search" still gets in-engine skips, and their presence changes no-search's price | CROSS | `emit_dfa.c:5063-5100`, `:12690` |
| C9 | HANDOFF K vs the row it displaces | the landmark admission compares the landmark's ppm with the start set's ppm at distance K | CROSS (handoff vs plain start search) | `emit_dfa.c:9016-9025` |
| C10 | READERS OF THE CHOSEN STOP | G1 (`req_byte_dominated_by` `:8546`), R4 (`cand_rs_dense_applies` `:10087`), the landmark K, `@idx` recompute "which byte is scanned"; after D176 they READ the reply. A different stop moves their verdicts (and the presence drop) | CROSS (downstream of the stop) | SRS §3.1 rows P5, P7, P8, K10; §3.2 |
| C11 | CALL SHAPE | one-shot vs iterator (M), call span (N), history (H) select rows; short calls make per-call terms dominate; the find-all iterator's fixed setup ~1.8-3.9 ns accepted | CROSS (all scan strategies) | `regime_tables.md` §2; D171 |
| C12 | PROOF / consumable_len | what the find proves (proven sets per offset) is not re-tested by the consumer; a method that proves more lowers the consumer's cost | CROSS (kit method x consumer) | D161 add. 8, add. 16 |
| C13 | STATEMENT LIMITS | what pcrec states bounds the candidates: run truncation to 32 positions, `MF_WREACH` 64, `MF_WMAX_SPAN`, one or two alternatives; Frank ruled positions beyond the verify slice MAY be stated as cheap candidate spans ("Yes unless it has reason not to") | INSIDE (bounds the search space) | `memfn.h:562-571` (MF_WSPAN_POS, MF_WMAX_SPAN, MF_WMAX_ALT, MF_WREACH); [MEMFN-UNBOUNDED-SPANS] charter, `plan.md` |
| C14 | ORIGIN | pcrec chooses the sub-problem's origin (e.g. send `aaa.{2,5}zxq`, recover `a.*` by reverse DFA); every span price is relative to that origin | CROSS (reverse strategies vs forward) | D161 add. 4, add. 9 |
| C15 | SIMD LAYER | changes which methods are AVAILABLE, never their cost (ruled) | INSIDE (applicability only) | D176 Q1 |
| C16 | HYBRID RESEED | the reseed policy reads the candidate rate times the reseed gap; a different stop changes the candidate rate it reads | CROSS (T1 x T14) | `emit_dfa.c:10087` |

**Where "best per strategy, then best strategy" is exact (INFERENCE from the rows above):** within
one window site whose plan verifies every core position, with the route fixed, presence absent,
and no downstream reader (C4 and C5 cancel there per SRS §4.1). It is NOT exact wherever C1, C2,
C3, C6, C7, C9, C10, C14 or C16 apply: each makes one strategy's best option depend on another
choice. C1 and C10 are the cases where the same option ranks differently depending on which
other row wins.

---

## Data we have

| input | what it measures / holds | units | box | date / commit | generator | staleness / limits |
|---|---|---|---|---|---|---|
| byte-rate prior (default) | 256 ppm rates, AUTHORED (etaoin-shrdlu letters, space 15%, digits 0.9% each, structural punctuation raised, floor 2) | ppm, sum 1,000,000 | none (authored) | `src/findings/default.rxt` header | hand-authored, "the one bundle with no generator" | marginal only; English-log-shaped; dense hex invisible by construction (SRS §5.1 item 3); utf8 prior authored per D160 |
| named analysis bundles `log`, `weblog` | measured byte counts (and bigram blocks the analyzer can count) off exemplar corpora | counts -> ppm | n/a (data) | `third_party/synth-log-lines-v1`, `third_party/elastic-examples-apache-logs-bc53b584` | `third_party/*/generate.py` via `build/pcrec-analyze` (`analyze/count.c` `kind_block_add_bigram` `:141`) | used only when named (`--analysis`); the query vocabulary is `byte-rate`, `run-rarity` (`src/core/findings.h:195`); no pair-at-distance query |
| `mf_pred.rank_*` | pcrec's ranking of a RUN term's positions by prior, rarest first | positions + ppm | — | D157 | pcrec | retired on window sites ("no ranking (`rank_n` 0)", `memfn.h:533`); still read by vrun's KB |
| `measure_store/zen4-grid1@1` | walk, V1, S1, A1 per-byte slopes (beta), per-use (wuse), cold activation (ccold), fixed costs (f), crossovers (xover), savings, g* thresholds, noise (eps) | relative to u = beta_walk(DFA_SCAN, r1e0c0) = 0.1892 ns/B, value_e6; raw abs_ns kept | 7700X Zen 4, CPU 14, gcc 15.2.0 -O2 | slot grid1 2026-10-13, code `540649453` | `memfn/data/sets/generate.py` -> `measure_store/from_interim.py` | tier `scratch`; "No routed kit row reads a set key before the kit's B4" (`measure_store/zen4-grid1/1/PROVENANCE.md`); 68 rows; no libc, PAIR, SKIP, verify, vany or engine rows; interp-log2 rows not recomputable (no cells) |
| method cards `kit-grid@1` | the method for each quantity (subject, lengths, launches, rounds, A/A rule, gate) | — | — | `memfn/data/cards/kit-grid.tsv` | — | `ver 2` (grid2's dispatch charges, libc rows, NONE, pre-scan gate) "NOT written here" (card header) |
| card `kit-kernels@1` | vany2/3 w16/w32/body vs WALK/LIBC | same quantities as kit-grid@1 | — | 2026-10-29 | — | UNMEASURED (card header); form-hash deps OWED |
| `memfn/src/plan_cost.def` | C_MEMCHR 0.06 c/B, C_BITMAP 1.16 c/B, C_VERIFY 2.5 c, C_ENTER 20 c, C_MISPRED 15 c, MATERIAL 2/1, MAX_SET 4, HORS_MIN 145,822 ppm | 1/100 cycle per byte or per candidate; ppm | scans: ubuntubudu Zen 1; HORS_MIN: dev box | prefix_k @ `7050f8652`; HORS_MIN job 581 | transcribed | MIXED BOXES and units with the set (SRS §4.3 "The boxes mix"); integer 1/100-cycle unit TRUNCATES (`\d\dxyz` tie, SRS §4.3); C_VERIFY UNMEASURED DEFAULT; C_ENTER MEASURED x ASSUMED; HORS_MIN PROVISIONAL, in-sample on one winning cell |
| Table B rows' `basis` | per row MEASURED / DERIVED / UNMEASURED-DEFAULT and a refutation sentence | — | — | `finder.c:249-353` | — | D1, D1c, D1w, PAIR, P2-P4, P9 are UNMEASURED-DEFAULT; R7w MEASURED (the walk ruling) |
| engine terms (armread) | C_call (2.05-2.44 ns DFA/VM, 3.55 hybrid), c_byte (DFA skip 0.1884 ns/B, VM 0.184-0.186), C_match (DFA 3.2-7.7 ns, VM ~0-7.8, depends on m), in-match byte (DFA ~1.4 ns/B, VM ~0.43, DERIVED) | ns | Zen 4, taskset 14 | 2026-10-13 | `armread/fit.py` over the kit's EXT slot | three patterns; C_match is not constant in m; L2-resident 64 KiB only |
| costmodel per-site-kind decomposition | F/call, u/use, b_skip, b_cons (consumed bytes) for PF, DFA hat, VM hat; regimes DINGHY/TUG/LINER | ns | Zen 4 | lane costmodel (kit, `lane/memfn-r17` per `regime_tables.md` header) | least squares over 116 spike groups | median relative residual 0.33 for PF (`costmodel_report.md` §0.1) |
| `window_search_game` | stop counts (no clock) per span over bench subjects: prior vs measured one-position stops (0.3x-6.8x), survivors (21x-1,750x; population p50 1.6, p90 240) | counts | none (counting) | 2026-10-11, main `aa2ddb1d` | `window_search_game/chain.sh` | bench subjects read; illustrative consumer prices only |
| `walk_vs_v1_record` | V1/M64/flatten/adaptive vs walk on real held-out text (E8: V1 wins 46, loses 35, null 13 of 94 cells) | % of walk | Zen 4 | 2026-10-21 | e8min, flat, adatwin lanes | CLOSED record; the loss mechanism is dense predictable stops |
| `twins.md` | tailored vs generic kernels (T-A classifier, T-B fused caseless scan+verify, T-C descriptor kernel) | ns | Mac M1 Max, "directional only" | 2026-10-04, main `8a41efd2` | `probes/twins/` | not the target box; not under the measure-set format |
| job 588 E[sh] table | D-hors vs D-one alpha on 12 sites, E[sh] 1.0-6.0 | ratio | dev box | S3 (`s3_report.md` §6.5) | S3 timing job | 12 sites, one per E[sh] point; SRS §4.4 fits one c_probe in (0.664, 2.506) ns, in-sample |
| `regime_tables.md` / `regime_eval.md` | the knowledge keys (P, N, M, E, H, A, I) and the regime pick rows with regrets per DINGHY/TUG/LINER | % of walk | Zen 4 | rev 0.5 | kit lanes | rows mostly withdrawn after the walk ruling (`finder.c:312-322`) |
| census instruments | mover/identity sweeps (`emit_sweep.py`, the pcrec-side diff named by SRS §8 item 2), the kit's sbscope/b4close2 counts, `tests/startset/manifests/` | counts | — | — | — | count populations, not prices; SRS step 0 (the post-C1 census of pick changes) has NOT been run (`memfn/docs/wake.md:27` lists it as next kit work) |

---

## Data we could have

What each strategy row needs to be priced honestly, the gap today, and how it could be obtained.
"Card" = a method card + a set revision (D166, [MEASURE-SET]); "census" = a compile-only count
over the emit_sweep corpus and bench; "exemplar" = a named analysis bundle via `pcrec-analyze`.

| strategy row | needs | have | missing | how (source of the idea) |
|---|---|---|---|---|
| NO SEARCH | the consumer's cost per subject byte per route (DFA, hybrid, VM, attempt), measured in the walk's unit | costmodel b_cons per site kind; armread c_byte / in-match per-byte (DERIVED) | a CARD in the set; per-artifact variation (VM attempt cost varies 5x with frame discipline, `window_search_game.md` §5.5 last paragraph) | a "no-search" card: time the artifact with the start search denied (`-fno-start-set` / `--memfn=no-window-search` OFF arms exist: `locate_cover_applies` comment `emit_dfa.c:4840-4845`) over member-free and dense subjects; SRS §5.1 item 1 |
| ONE POSITION, libc | β_libc, s_libc on the target box | Zen 1 only (`plan_cost.def` C_MEMCHR; SRS §4.3) | Zen 4 | the LIBC card SRS §4.3 names ("a kit-grid LIBC card on the dev box") |
| ONE POSITION, walk | β_walk, s_walk | MEASURED Zen 4 | other boxes (F5 Zen 1) | [MEASURE-SET] library |
| PAIR (two streams) | β_pair, s_pair | none ("no PAIR cost constant", `finder.c:310`) | everything | PAIR card (SRS §4.3) |
| PAIR / two positions (filter) | JOINT rate of the two positions at their distance | none (prior is marginal; analyzer counts adjacent bigrams only, `analyze/count.c:141`) | a pair-at-distance rate per stated span | exemplar bundle query (D83 addendum's run-rate family, `window_search_game.md` §5.5 item 3); or a conservative floor (rarest single position) |
| K-of-set (vany) | β, per-use for w16/w32 | card written, unmeasured | measurement; form hash deps | run `kit-kernels@1` (simdset Q3) |
| SKIP (Horspool) | c_probe, and verify per probe hit | bracket (0.664, 2.506) ns from 11 in-sample sites | a measurement over an E[sh] x mass grid | the SKIP card (SRS §4.3, step 1) |
| VERIFY (all strategies) | v_i per test, mispredict per failed verify | C_VERIFY UNMEASURED DEFAULT; C_MISPRED DERIVED on Zen 1 | measured verify per hit, especially dense-candidate cells (model priced dense hex SKIP at 0.71 ns/B vs measured 2.23, SRS §5.1 item 2) | [MEMFN-POSCOST] part 3's verify-cost reading |
| CONSUMER per false entry | A_entry per route | C_ENTER MEASURED x ASSUMED (Zen 1, "~2 bytes a false start survives") | Zen 4; per route | armread-style EXT slot (C_match is the nearest measured quantity, armread §2) |
| SURVIVORS (multi-position plans) | joint survival per span | none | the 21x-1,750x gap | exemplar run-rarity/run-rate per span, or a floor (window_search_game §5.5 item 3) |
| ALL, per box | the same cards on Zen 1, Mac, Intel | Zen 4 only | the library | [MEASURE-SET] (a)-(d), `plan.md` |
| ALL, subject regime | the subject's own rates (dense hex, non-English) | default prior only | per-deployment rates | named analysis (`pcrec-analyze`), caller hint ([MEMFN-REGIME] trigger) |
| census of WHERE pricing would move picks | per site: today's pick vs priced pick at both c_probe bracket ends; fold-eligible presence sites; two-byte non-case-pair stops; F0-at-0 and unit-tie sites | none run | SRS step 0 | census after C1 (SRS §7 step 0), heavy -> boxqueue |

---

## Open questions for the requirements step

Forces and options only; no decisions (brief). Each question names the place in this survey that
raises it.

### 7.1 One table, or one per task?

- **Forces.** D176 Q1 put "which stop, found how" in ONE kit table for the window family. The
  strategy rows the brief names (no search, one position, pair, skip) apply to T1, T2, T3, T5,
  T6 (§1), but T8-T10 (in-engine skips) and T11-T12 (verify, mismatch) have different consumers and
  frequency classes (BYTE, per backref step). T3 (presence) has a different objective ("rejects a
  subject by ABSENCE", SRS §3.2) yet one decider (D176 Q4). The house model allows "first-match,
  combining or priced-argmin" tables (memory `pcrec-decisions-as-first-match-tables`).
- **Options.** (a) one strategy table over every task with a task key column; (b) one strategy
  table per frequency class (CALL, CAND, BYTE); (c) one table for the window-family tasks only
  (T1-T6), the others stay first-match until a measured need (D77).
- **What decides it:** whether any coupling in §4 crosses task boundaries. C1 (presence x stop),
  C7 and C8 (engine/no-search x in-engine skips) and C16 (start x reseed) do.

### 7.2 Where the strategy choice lives: kit or pcrec?

- **Forces.** The kit owns method choice and must not carry pcrec's consumer price (D161 add. 6:
  "CONSUMER PRICE is DROPPED ... it removes levers"; re-entry only "as a new filed row if a real
  cell shows the kit's choice wrong for want of it"; D161 add. 11: a per-route per-candidate
  constant FILED with a TUG trigger; Q-WR-9: if the trigger fires, "the consumer's cost enters as
  a per-route MEASURED constant in the D166 set, never a pcrec price model"). The no-search row
  (C6, C7) cannot be priced without that cost. pcrec owns the route (`regime_tables.md` §0:
  "pcrec's own decisions over the same knowledge (the origin, engine and route ...) live in
  pcrec's tables (`cand_rows[]`)").
- **Options.** (a) the kit prices every strategy, given per-route consumer constants in the set;
  (b) pcrec prices strategies (it owns the consumer and route) and asks the kit only for each
  kit strategy's best price (Table B's DECISION question, SRS §6.1, extended); (c) split by
  strategy: kit strategies compete in the kit, "no search" and reverse strategies compete in
  pcrec against the kit's best.
- **Lens.** D157 (facts, not methods) and D146 (pcrec does no cost comparison of the kit's forms)
  constrain (b): a price QUOTED by the kit is a fact about its forms; whether pcrec comparing it
  with its own consumer cost is "cost comparison" in D146's sense is open.

### 7.3 How prices of different strategies stay comparable WITHOUT a tuning factor

- **Forces.** Frank is not a fan of tuning constants (memory `pcrec-suspect-tuning-constants`;
  D149). D176 Q1/Q5 fix the unit: relative to the walk's per-byte cost on the same box,
  fixed-point integers, ties inside the noise band go to declared tie rows. Today two non-price
  bars remain: MARGIN 2/1 (ARGUED) and HORS_MIN (PROVISIONAL), each a de facto tuning factor
  (`plan_cost.def`).
- **What makes prices comparable without a factor:** every term in the same unit, measured by the
  same harness, on the same box, with its noise band (`kit.eps.*`). The strategies differ in
  WHICH terms they have: per byte (β), per stop (s), per false entry (A_entry), per verify (v_i),
  per call (C_call / ccold). A strategy row that has no measured value for one of its terms is
  not comparable (the standing rule: "until a box is re-measured the row reads UNMEASURED
  visibly", D176).
- **Options for the "simpler strategy wins ties" rule.** (a) a declared simplicity ORDER over
  strategy rows, consulted only inside the noise band (a tie row, as `window.c` `wf_ties[]` does
  today); (b) a band wider than noise for more complex rows (that is a margin, i.e. a factor);
  (c) a code-size term priced in the same unit (no measured exchange rate exists:
  `walk_vs_v1_record.md` §4 states Frank's "10% ... less so at double the code size" as a
  judgment, not a rate).
- **Open:** what the noise band is for a COMPOSITE price (a sum of measured terms each with its
  band, multiplied by prior rates that err 0.3x-6.8x).

### 7.4 The multi-variable risk: where it bites in this design

Once a model exists it is hard to make the numbers give the result believed correct. Concrete
places in this design where that risk is live (each a fact from §4-§6):

1. **`A_entry` (C_ENTER).** Its value is "10.7 c/B times an ASSUMED ~2 bytes a false start
   survives" (`plan_cost.def`). It multiplies every PARKED/RESEED price (SRS §4.1). Moving it
   moves the PARKED-vs-RESEED and verify-everything-vs-engine-verify boundaries without any
   pattern-visible reason.
2. **V (verify per stop).** A placeholder `v0 = 0.5 ns` priced dense hex SKIP at 0.71 ns/B against
   a measured 2.23 (SRS §5.1 item 2). A free V can be tuned until any witness passes.
3. **The survivor rate.** Under independence it is wrong by up to 1,750x (`window_search_game.md`
   §5.3); any multi-position strategy (pair filter, chain, superset) is priced through it. A
   "floor" substitute (rarest single position) is itself a modelling choice.
4. **c_probe fitted in-sample.** SRS §4.4: eleven sites fit one c_probe in (0.664, 2.506) ns; the
   study itself says "This is in-sample ... not a measurement".
5. **The prior.** It is authored and English-log-shaped (`default.rxt` header); E[sh], r(S) and
   π all read it. SRS §5.1 item 3: under the shipped prior "a dense-hex subject is invisible, so
   the default build keeps SKIP there by construction".
6. **Bars that survive a pricing build.** MARGIN 2/1 (ARGUED) and the noise band; if the model
   disagrees with a measured cell, adjusting a bar is the path of least resistance.
7. **Per-route consumer constants.** If the no-search row needs one number per route, the
   route-level number hides a per-artifact 5x variance (`window_search_game.md` §5.5 last
   paragraph).

Options that bound the risk (as listed in the sources, not chosen): an independent control
whose population comes from a pcrec-side diff, never from the price's own `moved` (SRS §8 item 2,
K35); the step-0 census used only to LOCALIZE movers, never as acceptance (same); every constant
MEASURED before it is read, with a predicted sign on sites outside the fitting sample (SRS §8
item 2: "Step 1's grid must predict signs on sites outside job 588's before step 2 relies on
it"); pre-registered witnesses with expected outcomes stated before the build (SRS §5.1).

### 7.5 How future additions are measured

- **Fact.** The standing rule: "Any new find/scan/skip/verify method adds its measurement card in
  the same change" (D176). `vany` did (`kit-kernels.tsv`), unmeasured.
- **Open.** (a) Does a new STRATEGY (not a method) also need a card, e.g. "no search" or "chain"?
  A strategy's price is composed from method cards plus consumer and verify terms; whether a
  composite needs its own end-to-end card is not ruled. (b) What runs a card: the canned script is
  [MEASURE-SET] (a), not built; until then each card is run by a lane in a night window (D176 Q3).
  (c) What the trace prints: the brief wants "the full per-strategy ranking visible in a trace";
  `window.c` already has an MF_TRACE build (`gate.c` header) and `--list-measurements`; whether the
  ranking is a compile-time listing, a stamp, or a trace-only record is open ([LIST-TABLES],
  `plan.md`).

### 7.6 Smaller open points raised by the survey

- **Strategy vs tactic boundary for Horspool.** A skip changes WHICH bytes are examined (BOTH in
  §3); is it a strategy row or a method of the one-position row? D176 Q2 made it a METHOD.
- **Presence as a strategy row?** D176 Q4 keeps two questions with one decider; under a strategy
  table, is presence a row, a column (a cost added to each stop row), or a separate table (C1)?
- **No NONE row anywhere in Table B** (`finder.c:249-326`) though D161 add. 14 rules "the kit
  decides whether to scan at all". Is "no search" the kit's NONE row or pcrec's `next-none`?
- **The step-0 census and step-1 cards are prerequisites** of D176's build (SRS §7); they are
  also the data a strategy table needs (§6). Whether the census is widened now to count strategy
  flips (e.g. sites where no-search would win under b_cons) is a scope question.
- **Standing design questions for the coming design** (`docs/design/CLAUDE.md`). (1) Measurement
  regime: RELEVANT (§3 last row; DINGHY/TUG/LINER; the target box selects the set). (2)
  Independent control: RELEVANT (§7.4's options). (3) What moves when data is regenerated:
  RELEVANT, since a strategy flip moves bytes and is a pcrec abi event (`memfn/CLAUDE.md`
  standing question 3; integration.md §21.3, cited there).

---

## Sources read

- Decisions: `docs/dev/decisions.md` D161 (+ addenda 1-17), D169 (+ addendum), D170, D171, D172 (+
  addendum), D176, D160.
- Stop-ranking study: `git show lane/memfn-stopstudy:docs/design/memfn/stop_ranking_study.md`
  (`fc6735cdf`, rev 2, all sections).
- Design: `docs/design/memfn/window_search_game.md` §0, §5.3-§5.5; `walk_vs_v1_record.md` (all);
  `twins.md` §0 header; `docs/design/regime_tables.md` §0-§2; `window_site.md` §0-§1.1;
  `integration.md` §R4.9.5, §R4.9.6 (headings of R4.9 read).
- Kit code headers and tables: `memfn/CLAUDE.md`; `memfn/src/window.c` (header, TIE table, Table D,
  cost table include); `finder.c` (header, `fd_rows[]` 249-354); `presence.c`, `vrun.c`, `vany.c`,
  `gate.c`, `ofsskip.c`, `pffind.c`, `precheck.c`, `runcmp.c`, `terms.c` headers; `compose.c`
  `arms[]`; `options.def` row list; `plan_cost.def` (all); `memfn/include/memfn.h` op/kind enums and
  the WINDOW SITE block (232-300, 405-440, 480-600).
- pcrec code: `src/gen/memfn_sites.def` (all); `src/gen/emit_dfa.c` `cand_rows[]` (10154-10720),
  the predicates cited in §1, `pick_skip_states`; `src/gen/emit_vm.c` VMRUN/VMSPAN builders;
  `src/gen/known.c:484`; `src/core/findings.h` (query vocabulary); `src/findings/default.rxt`
  header; `src/core/limits.def:395`; `analyze/CLAUDE.md`, `analyze/count.c`.
- Data: `measure_store/index.tsv`, `DEFAULTS`, `zen4-grid1/1/set.tsv` and `PROVENANCE.md`;
  `memfn/data/CLAUDE.md`; `memfn/data/cards/*.tsv` headers.
- Reports: `docs/dev/lanes/armread_report.md` §0-§4; `costmodel_report.md` §0.1;
  `simdset_report.md` "Open questions"; `s3_report.md` §6.5.
- Plan rows: `docs/dev/plan.md` [OPT-REVEND] 47, [PRIOR-COST-UNIFY] 84, [ENG-TACTICS] 107,
  [MEASURE-SET] 183, [MEMFN-REGIME] 882, [MEMFN-POSCOST] 888, [MEMFN-UNBOUNDED-SPANS] 894,
  [MEMFN-PAIRSTOP] 900, [MEMFN-PAIRSIMD] 906, [MEMFN-SKIPSWITCH] 1489, [SPAN-ISEL] 1667,
  [POS-PARALLEL] 1695; `memfn/docs/ideas.md` entry headings; `memfn/docs/journal.md` tail;
  `memfn/docs/wake.md:27`.
- Not read: `regime_eval.md` beyond its role line in `memfn/CLAUDE.md`; `integration.md` outside
  §R4.9; `docs/design/where_to_start.md`; `prior_cost_unify.md`. Cited facts from them come via
  the documents above.

Process note: three read-only fact-gathering subagents were launched at the start; all three
ended without delivering a report, so every fact here was read directly by this lane.

---

## STATE AT HANDOFF

- STATE: done. Report complete; nothing owed (DELIVER block `owed: none`).
- No rulings file was named in the brief.
- No code, no build, no make, no timing, no box runs.
- A fresh agent resuming from here would start at §7 (open questions) for the requirements step,
  and at §6 for the data inventory stage.
