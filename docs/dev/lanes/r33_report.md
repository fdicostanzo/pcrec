# r33 — R-33: a cheap simulation of the inner-first "find the span" pick (2026-11-02)

Lane r33 (opus), branch `lane/memfn-r33` from main 99d6cc7ef. Request: memfn/docs/requests.md "## R-33"
(the owner: "not a prescription but an example for discussion"). A study: nothing under `src/`, `cli/`,
`lib/` or `memfn/src/` changed; no timing was run. Instruments: `docs/dev/lanes/r33_sim/` (own CLAUDE.md).
Outputs committed under `r33_sim/out/`; the raw sweep (9.5 MB JSONL) stays in
`/var/tmp/pcrec-pcrec/scratch/memfn/r33/sweep/` and `.../r33/rp/`.

**Short answer.**
- On today's default compile the simulation agrees with the kit on 3,092-3,097 of 3,443 decision
  units (90 %), and differs on 346-351, depending on the key.
- Almost all disagreements come from TWO rules, not from the stop pick itself:
  - R1, the local method rule "2 members = PAIR" (225 units). It forces a PAIR where the kit walks
    today, including on dense two-member sets, where the sim's own key prices the PAIR above the walk
    (139-154 units).
  - R2, the RESEED alternative being admitted on every site (95-100 PF units). Today the kit cannot
    price RESEED unless one walked offset has exactly one member (A-model's `scan_ok`).
- smp20 `(?i)x/1234` flips only under KEY B, the key that also charges each memchr stream its
  per-byte scan, and only with the per-hit cost at or below 20 c. Under the request's literal key
  (KEY A) the sim keeps {x,X} as today, because the default byte-rate prior rates {x,X} at 1,097 ppm
  against '/' at 4,154 ppm. Job 588 measured that choice 1.58-4.03x slower than '/' on every class.
- **Does the sim pick something measured slower?** Yes, in two places:
  - The 6 D-hors sites of job 588: the sim has no Horspool method, so it renders DEF's walk, which
    was measured 0.57-0.78x of RTE's time in RTE's favour.
  - 4 rule-pilot sites (C11, C14, S20, B20): the arms that render the sim's stop sets were measured
    0.8-41 % slower. Every one of these arms also changes the route, so the evidence is confounded.

## Method

**Today's answer, observed rather than approximated.** `r33_sim/build.sh` builds a scratch traced
pcrec (`-DMF_TRACE -DPCREC_CAND_TRACE`, no source edit) and links `r33_sim/probe.c` into it with
`-Wl,--wrap` on the kit's `mf_define`/`mf_emit`/`mf_art_begin`. For every site pcrec hands the kit,
the probe prints:
- the stated facts: the frame, the predicate's terms, the window alternatives with every span's
  sets, core and verify;
- for each window site, and for each window-stating FUNC part of a pre-check, the kit's own phase-1
  decision through the public query `mf_wdecide`: alt, stop, stop set, plan, path;
- each art's byte-rate table.

`r33_sim/collect.py` groups three more streams per define:
- the kit's `MFTRACE` selection records (Table A/M/E/D rows, the finder's FDROUTE, WPATH, the fn
  BODY rows);
- pcrec's own `MFROUTED` record (the delegated-site id: COVER, OFS, PF, PRE, LMHIT, MLINE);
- the art's byte-rate digest.

Today's METHOD for each unit is read as follows:
- E-find: the FDROUTE row (D1/D1w = memchr, PAIR, R7w = walk), or D-hors where Table D chose it.
- E-stmt: the FDROUTE row.
- E-func: the fn BODY row (fn-memchr, fn-pair).

**Sources** (5,492 compiles in job 240-kit-r33-sweep; 623 in job 241-kit-r33-rp; both green):
- **corpus**: 5,014 distinct .rxt patterns (`emit_sweep.enumerate_corpus`), of which 460 refused.
- **bench**: 392 pcrec-bench patterns (`bench/*/subbench.toml`, read-only), of which 26 refused.
- **s588**: job 588's 8 §6 cells, its 24-row mover sample and its 11-row two-stream sample, each as
  RTE (default) and DEF (`--memfn=no-window-search,no-window-skip`).
- **rp**: the rule-list pilot's 623 census arms, with each arm's own deny set.

Every compile used `--features all -p rx` (pick_588's and measure_588's flags). All 6,115 compiles
read ONE byte-rate table, the default PRIOR_AUTHORED one, digest `a322116b1b87f9f6`.

**The simulation** (`r33_sim/sim.py`) follows the request's ordering for each decision unit.
1. **Fixed facts:** the frame and the stated alternatives.
2. **Candidates:** per alternative, every stated offset after the kit's own C-meet (the AND of the
   covering spans' sets, window.c `merge`) that is core and not the full set. This is A-mass's
   domain. On a PARKED alternative, only the verify-YES core positions over their YES sets: what
   `rd_set` lets a non-reseeding parked plan read.
3. **Local rules per candidate:**
   - The method by member count: 1 = memchr (1 stream); 2 = two-stream PAIR (2 streams);
     3+ = table walk, which is NOT a stream.
   - The verify: the other readable non-full offsets, in ascending mass, with early exit.
   - Then the matcher is entered on a pass.
4. **The pick, last:** the least key over all complete plans, then the alternative one level up
   (the least; today's 2x MARGIN is not applied).

**The keys** are in cycles per 1e6 subject bytes. Mass follows `kit_set_sum` semantics (ppm summed
over the set's members).
- **KEY A**, the request's words:
  - a stream method: mass x streams x H_HIT + mass x VERIFY_PER_HIT;
  - a walk: 1e6 x C_WALK + mass x VERIFY_PER_HIT;
  - where VERIFY_PER_HIT = E[tests] x C_VERIFY + P(pass) x C_ENTER.
- **KEY B** = KEY A + streams x 1e6 x C_SCAN (each memchr stream also pays its per-byte scan).

| constant | value | basis |
|---|---|---|
| H_HIT (one stream hit: memchr return + restart) | 20 c | **ASSUMPTION**, nothing on file; swept 10 / 20 / 40 |
| C_WALK (table walk per byte) | 1.16 c | plan_cost.def C_BITMAP, MEASURED on Zen 1 (not this box) |
| C_SCAN (memchr per byte per stream) | 0.06 c | plan_cost.def C_MEMCHR, MEASURED on Zen 1 |
| C_VERIFY (one tested offset) | 2.5 c | plan_cost.def C_VERIFY, UNMEASURED DEFAULT |
| C_ENTER (one matcher entry) | 20 c | plan_cost.def C_ENTER, MEASURED x ASSUMED on Zen 1 |

The per-byte walk cost is the request's labelled ASSUMPTION: the walk is priced per subject byte,
never per hit. Positions are assumed independent.

A unit AGREES when the sim's (offset, set) is today's and its method is today's. memchr-back counts
as memchr, and a D-hors or unobserved method is compared on the stop alone. Otherwise it is:
- `differ-stop`: another stop, same alternative;
- `differ-alt`: another stop, in another alternative;
- `differ-method`: same stop, other method.

The **gap** is today's plan priced by the same key with TODAY's method, divided by the sim's pick.
A gap above 1 means the key prefers the sim's pick. A gap below 1 means the sim's own key prices
today's plan cheaper: the local method rule forced the sim's choice.

## Today vs simulated

Today's default compile (RTE arm), all sources. Per-source counts: `r33_sim/out/summary_<tag>.tsv`.

KEY A:

| kind | units | agree | agree-stop(hors) | agree-stop(unobserved) | differ-stop | differ-alt | differ-method |
|---|---|---|---|---|---|---|---|
| COVER | 1021 | 1004 | 14 | 0 | 3 | 0 | 0 |
| LMHIT | 80 | 77 | 0 | 0 | 0 | 0 | 3 |
| MLINE | 38 | 38 | 0 | 0 | 0 | 0 | 0 |
| OFS | 371 | 349 | 0 | 0 | 22 | 0 | 0 |
| PF | 1742 | 1420 | 0 | 0 | 0 | 100 | 222 |
| PRE:part | 191 | 185 | 0 | 5 | 1 | 0 | 0 |
| all | 3443 | 3073 | 14 | 5 | 26 | 100 | 225 |

KEY B:

| kind | units | agree | agree-stop(hors) | agree-stop(unobserved) | differ-stop | differ-alt | differ-method |
|---|---|---|---|---|---|---|---|
| COVER | 1021 | 1000 | 14 | 0 | 7 | 0 | 0 |
| LMHIT | 80 | 77 | 0 | 0 | 0 | 0 | 3 |
| MLINE | 38 | 38 | 0 | 0 | 0 | 0 | 0 |
| OFS | 371 | 354 | 0 | 0 | 17 | 0 | 0 |
| PF | 1742 | 1425 | 0 | 0 | 0 | 95 | 222 |
| PRE:part | 191 | 184 | 0 | 5 | 2 | 0 | 0 |
| all | 3443 | 3078 | 14 | 5 | 26 | 95 | 225 |

Sensitivity (H_HIT swept; the walk and scan constants fixed):

| setting | units | agree (incl. agree-stop) | differ | sim pick priced above today's own (gap < 1) |
|---|---|---|---|---|
| keyA (H 20) | 3443 | 3092 | 351 | 140 |
| keyB (H 20) | 3443 | 3097 | 346 | 155 |
| A_h10 | 3443 | 3092 | 351 | 86 |
| A_h40 | 3443 | 3079 | 364 | 225 |
| B_h10 | 3443 | 3096 | 347 | 111 |
| B_h40 | 3443 | 3078 | 365 | 228 |

The counts move by 15-20 units across a 4x range of the one assumed constant. The classes below do
not change.

## Disagreements

Every differing unit is listed, with pattern, today vs simulated, all candidates with score inputs,
and the gap, in `r33_sim/out/differ_keyA.tsv` (351 rows) and `r33_sim/out/differ_keyB.tsv`
(346 rows). By class:

| class (KEY B) | units | corpus / bench / s588 | gap < 1 | gap >= 1.5 |
|---|---|---|---|---|
| R1 two-member stop: today walk, local rule PAIR | 225 | 220 / 5 / 0 | 154 | 23 |
| R2 PF: the RESEED alternative's stop over PARKED k0 | 95 | 80 / 14 / 1 | 1 | 64 |
| R3 OFS: a stop outside A-model's walked one-member domain | 17 | 11 / 6 / 0 | 0 | 10 |
| R4 COVER: A-mass's stop vs the priced one (smp20's class) | 7 | 5 / 0 / 2 | 0 | 3 |
| R5 pre-check part | 2 | 2 / 0 / 0 | 0 | 0 |

(KEY A: R1 225, R2 100, R3 22, R4 3, R5 1.)

- **R1 (225).** A PF or LMHIT start set of two bytes. Today it is rendered as a walk: `fd_route`
  never offers PAIR, because the gate is `SF_WINDOW_STOP`, units_inventory §3 N4. The sim's local
  rule says PAIR. On 154 of them (KEY B) the sim's own key prices the walk cheaper, for example
  `cat|dog`: {c,d} at 46,603 ppm, gap 0.585 under KEY A. The rule "2 members = PAIR" without a price
  is wrong for dense pairs. The other 71 are rare pairs where PAIR wins by the key, for example
  `(["'])...` with {",'} at 4,569 ppm, gap 3.8.
- **R2 (95).** Today: A-parked, then A-floor for RESEED (no walked offset of one member), then
  M-parked. The sim prices the RESEED alternative's rarer stop instead, for example:
  - `(?i)hello.*world`: today PARKED {H,h} walk; sim RESEED @2 {L,l} PAIR.
  - `\b(?:ERROR|FATAL|CRIT)\b...` (loglines/level-context): today {C,E,F} walk; sim RESEED @1 {A,R}
    PAIR, gap 2.7.
  - altwide's 64/96/128-way alternations: a 24-byte set at k0 against a 21-byte walked set.
- **R3 (17).** OFS RESEED. Today A-model picks a walked offset (it excludes offset 0, the F0 span).
  The sim includes the core offset 0 and picks it where it is rarer, for example:
  - `frank|fred`: {r}@1 to {f}@0, gap 2.4.
  - `(?<=item )done`: {n}@2 to {d}@0, gap 1.5.
  - `colou?r`: {l}@2 to {c}@0, gap 1.4.
  - The two long literals (litrun lit-l31/l40, corpus `ABC..`): {j}@9 to {q}@16 and {B}@1 to
    {Q}@16, gaps 1.1-1.3.
- **R4 (7 under KEY B; 3 under KEY A).** COVER, the A-mass row ("by mass alone").

  | pattern | today | sim (KEY B) | gap B | KEY A |
  |---|---|---|---|---|
  | smp20 / corpus c02129 `(?i)x/1234` | @0 {X,x} PAIR | @1 {/} memchr | 1.086 | agrees with today (gap 1.0) |
  | pr09 `x[Q%]y` | @1 {%,Q} PAIR | @0 {x} memchr | 1.704 | agrees |
  | `a[\18]b` | @1 {\x01,8} PAIR | @2 {b} memchr | 1.55 | 1.43 |
  | `a[*/]b` | @1 {*,/} PAIR | @2 {b} memchr | 1.10 | agrees |
  | `x[\x{e0}-\x{ff}]y` | @1 32-byte walk | @0 {x} memchr | 14.1 | 51.7 |
  | `\B(?<!a)[de]` | @0 {d,e} PAIR | @-1 62-byte walk | 1.39 | 1.57 |

  The last row's -1 position is a lookbehind context byte. Under H_HIT 40, smp20 goes back to {X,x}
  under both keys. So smp20's flip is fragile: it rests on the per-byte scan term and on an assumed
  hit cost.
- **R5 (2).** Pre-check parts: `(a(b|c)(d|e))` {b,c} PAIR to {a} memchr; `(a(?i)b)c` {B,b} PAIR to
  {c} memchr.

## Cross-check against timings on file

No new timing. Tables: `r33_sim/out/xcheck_588.tsv`, `xcheck_rulepilot.tsv`, `xcheck_bench.tsv`
(`r33_sim/xcheck.py`).

**Job 588 (bar588's re-read, `/var/tmp/pcrec-pcrec/scratch/memfn/bar588/new_bar.md`; scalar layer,
RTE/DEF per regime and class).** DEF changes the whole route (OFS/PRE/PF instead of COVER), so each
reading is confounded beyond the stop.

- **smp20 first.** RTE is {X,x} PAIR; DEF is {/} memchr. Measured RTE/DEF: throughput real 1.663,
  none 2.793, random 4.028; search_short real 1.578 (gmean over its cells 2.251).
  - KEY A keeps {X,x}: the sim reproduces the measured loss.
  - KEY B picks '/', DEF's stop. The measured evidence supports it on every cell.
  - Why KEY A misses: the prior's masses (x 997 + X 100 ppm against / 4,154) say {x,X} is rarer.
    t588tri counted the opposite on real subjects (x 2,338 against / 1,026 candidates). Only the
    per-byte cost of the second stream tips the key.
- **The sim agrees with RTE where RTE and DEF differ** (cat-bounded, done-eol, smp07, smp14, smp17,
  smp19, smp24, word-digit). RTE/DEF gmean is 0.32-0.87 (max cell 0.78-1.27): this **supports** the
  sim's (and today's) pick.
  - On smp14 `[a-]` and smp24 `[:a]` the PAIR keeps one losing cell, search_short/real 1.267 and
    1.259.
- **D-hors sites** (hex8-bounded, smp03, smp08, smp13, smp18, smp23). The sim has no Horspool
  method, so it renders DEF's walk. RTE/DEF gmean 0.57-0.78: **the sim picks something measured
  slower** on all six (hex8-bounded's throughput/dense cell is 1.53 the other way). D176 Q2 (Horspool
  as a priced method) is the missing candidate.
- **smp04 `[a[:b]`** (4.475x random). The sim agrees with today: walk on the same set. This is the
  compare-chain FORM (t588tri §a), invisible to a stop or method pick.
- **The two-stream sample** (pr01-pr11) is timed RTE/BASE (bounded vs unbounded streams), not a stop
  comparison: no evidence either way. pr09 (KEY B: {x} memchr instead of {%,Q} PAIR) has no DEF
  timing.

**The rule-list pilot (`/var/tmp/pcrec-pcrec/scratch/rulepilot/slot/dataset.json`, 138 sites, per-arm
medians against a0, floor = the site's own a0/a0#b/a0#c spread).** The sim, on a0's facts, differs
from a0 on 13 sites (KEY B; 14 under KEY A).
- On 8 of them, no census arm renders the sim's (set, method) multiset.
- On 5 an arm does. Every one of those arms also flips route flags (`-fno-offset-skip`,
  `-fno-req-handoff`), so these are **confounded**:

  | site | difference | arms and ratio to a0 | reading |
  |---|---|---|---|
  | C11 `\bfunction\s+(\w+)\s*\(` | OFS {u}@1 to {f}@0 | a5/a7/a10 1.13-1.17 | **against** |
  | C14 `\bfn\s+...` | {n} to {f} | a5/a7/a10 1.38-1.42 | **against** |
  | S20 `\bSection\s+...` | {c}@2 to {S}@0 | a3 1.253 | **against** |
  | B20 `permission is hereby granted` | — | a4 1.008 | against, at the floor's edge (0.47 %) |
  | L19 | — | a6 1.058 | against, KEY A only |
  | P23 `\bwas\s+\w+ing\b` | — | a1 0.896 | **supports** |

  The three clear AGAINST rows (C11, C14, S20) are all R3: the RESEED stop moved to offset 0. The
  evidence against R3 is therefore three confounded sites.
- Where the sim agrees with a0, 10 sites have an arm with a different search measured faster than
  a0 beyond the floor (B01, B13, B17, C17, C25, L25, L26, M12, M17, P27; best 0.87-0.99). These are
  wins the sim does not see, mostly route changes rather than stop changes.

**The bench ledgers (pcrec-bench reports, latest ryzen7700x matrix per subbench, read-only).** No
ledger times pcrec against itself with another stop, so this is context only. The differing bench
units (KEY B) where pcrec already loses to the best engine:
- loglines/level-context: R2, 3.6x off on throughput;
- loglines/stack-frame: R3, 3.1x;
- altwide w-8/w-64/w-96/w-128/clsa/clsd/cnt: R2 walk to walk, 1.6-25x;
- utf8/alt-cyr-64: R1, 421x;
- utf8/alt-distinct-lead: R2, 202x.

On the rest (capability, litrun, syntax) pcrec is already the row's best. The two utf8 rows were
compiled as bytes, with no encoding flag. There the prior rates every non-ASCII byte at 2 ppm, so
{\xd0,\xd1} reads as 4 ppm and the sim's PAIR would hit on most bytes of Cyrillic text: a facts
problem (the prior), not an ordering one.

## Facts not observable

Each item: what could not be observed without a code change, and how it was approximated.

- **The part-to-BODY mapping.** A pre-check part's fn BODY row carries no part index in the trace.
  The i-th chosen BODY row is ASSUMED to be part i's; 5 parts past the count are `unobserved` and
  compared on the stop only.
- **Subject-class byte rates.** The kit reads one prior (`a322116b1b87f9f6`, PRIOR_AUTHORED) at
  compile time. The real/none/random rates job 588 timed are not compile-time facts.
- **H_HIT.** The cost of one memchr return and restart is not on file: an ASSUMPTION, swept 10-40 c.
  C_WALK, C_SCAN and C_ENTER are Zen 1 measurements from plan_cost.def, not this box's. C_VERIFY is
  an UNMEASURED DEFAULT.
- **Positions are treated as independent** in E[tests] and P(pass).
- **Not modelled:**
  - Horspool (D-hors) as a method;
  - C-pin's whole-run compare;
  - the bounded look-ahead windows of the two-stream find;
  - SIMD forms;
  - the reseed obligation of a PARKED stop away from k0. PARKED's candidates were restricted to its
    verify-YES positions instead.
  - Whether a RESEED stop at offset 0 is a legal plan for the kit's renderers was not checked; the
    sim admits it (R3's source).
- **Compile options.** Corpus patterns were compiled without their .rxt file's own options
  (pick_588's convention). Bench patterns had no per-subbench encoding flag. Rule-pilot arms were
  re-compiled at 99d6cc7ef, while their timings came from builds at e0d716c7d; an arm's bytes may
  have moved since.
- **The decision unit's identity across arms** is matched by its (set, method) multiset, not by site
  identity: approximate where arms change the route.

## STATE AT HANDOFF

OWED none. Jobs `kit-r33-sweep` (240, 5,492 compiles) and `kit-r33-rp` (241, 623 compiles) are both
GREEN with their populations met. Instruments, outputs and this report are committed on
`lane/memfn-r33`. No `src/`, `cli/`, `lib/` or `memfn/src/` change; no timing run; no re-pin.
Re-running the analysis needs no compile: `sim.py`, `xcheck.py` and `tables.py` over the scratch
JSONL (paths in `r33_sim/CLAUDE.md`).
