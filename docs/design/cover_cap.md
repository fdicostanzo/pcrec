# cover_cap.md — lifting the `cover` route's 24-position cap ([COVER-CAP])

Status: PROPOSED, revision 0 (lane `covcap`, 2026-11-15). DESIGN ONLY: no build go.
Plan row: [COVER-CAP] (set S3), from [EARNED-SKIP]'s measurement (lane skipmeas,
2026-11-11). Built on: `kit_proof.md` §1.1 (the `cover_conj[]` table), `ctx_span.md`
§11 N-1 (which foresaw this cap), `offset_k_skip.md` §3.3 (where the 24 came from).
Compiler read: main `c7632c898` (`build/pcrec`, no `src/` change since it was built).

## 0. Goals

Ranked; the higher goal wins a conflict.

1. **G1, answer identity (every caller).** No search, match or group answer moves on any
   corpus pattern, any encoding, any deny-flag arm. Form: `make test`, `make test-axes`
   (the `--memfn=no-window-search` arm against the default) and the new `test-kitproof`
   boundary rows (libpcre2 10.46 answers) all green; 0 answer differences.
2. **G2, nothing else moves (every caller, reviewers).** Every artifact that does not
   change its `<PREFIX>_DFA_SCAN` to `"cover"` is byte-identical before and after.
   Form: `scripts/emit_sweep.py` main-before against candidate shows 0 changed bytes
   outside the predicted mover list, and the observed movers EQUAL the predicted list
   (§4.2).
3. **G3, no slower cell (bench users).** No mover cell is slower than before beyond the
   bench's A/A noise floor, in any regime, the first-byte-fail subjects (`fbf-l31`)
   included. Form: the re-timing of §5, before against after, same box and bench pin.
4. **G4, the engine finish leaves the long fixed shapes (bench users with literals,
   hashes and ids of 25 to 32 positions).** `lit-l31`'s match regime falls from 30.0M
   `instructions:u` to at most 6M (skipmeas measured 4.4M with the finish stubbed), and
   `mat-l31`/`lbf-l31`, `hex32`, `dig-exact-32` and `hex32-id` are faster beyond noise.
5. **G5, no seam event.** No memfn kit field, no `MF_SITE_ABI` bump, no pcrec `abi`
   bump; when the kit later raises its span bound, pcrec follows by editing one row.

Non-goals: shapes longer than 32 positions (`lit-l40`, the 36-position uuids,
`req-<uuid>`): those are bounded by the KIT (§1.3) and become a kit request that main
files (§2.4). Also not here: lookaround as a run ([REQ-LOOKAROUND], set S4), a trailing
`$`/`\z` as a length compare (kvcensus §5, "whole-cover once a trailing `$`..."),
captures inside a cover body (C1/C5 decline them today, unchanged), earned skip and
[MATCH-KNOWN] (PARKED, Frank 2026-11-11).

## 1. Where the cap lives

### 1.1 The binding bound: `PCREC_PREFIX_K_MAX` (24), a pcrec limit

The `cover` row admits an artifact when every conjunct of `cover_conj[]` holds
(`src/gen/known.c:369`). C8 (`cc_exact`, `src/gen/known.c:256`) needs the span slice's
exact prefix to reach the body's width `k`: `if (l->exact_len < k)` declines with
`exact/producer-short` (`src/gen/known.c:275`). The slice is the `span_facts` fact,
`pcrec_span_walk` (`src/facts/kset.c:853`), and its exact prefix loop stops at
`PCREC_PREFIX_K_MAX` (`src/facts/kset.c:911`); its liveness walk stops at twice that
(`src/facts/kset.c:891`); its storage is `MkLang.set[PCREC_PREFIX_K_MAX][32]`
(`src/facts/facts.h:306`). The value is the row at `src/core/limits.def:392`:

    PCREC_LIMIT(PCREC_PREFIX_K_MAX, 24, "count", "compile budget", NONE, "", ...)

PREMISE TEST, passed: `build/pcrec --emit-facts` on the 31-byte literal `lit-l31` prints
`span_facts 24:97,...,120` with `width [31,31]` and `RX_DFA_SCAN "unanchored"`; the
24-byte literal reads `"cover"`, the 25-byte one `"unanchored"`. At width 24 every
analog of the bench's movers already covers: `[0-9a-f]{24}`, `\d{24}` (byte and utf8),
`\b[0-9a-f]{24}\b`, a 24-position uuid prefix, `(?i)permission is hereby`. So the cap
is the only conjunct that stops their longer twins.

### 1.2 Every reader of `PCREC_PREFIX_K_MAX`

| reader | what it bounds | moves if the ROW is raised |
|---|---|---|
| `src/facts/kset.c:252` `pcrec_kset_walk` | the k-set walk (`kset_walk` fact: the HULL) | yes: the offset-k skip ([OPT-K]) and every hull reader |
| `src/facts/kset.c:891`, `:911` `pcrec_span_walk` | the span slice (`span_facts`): liveness depth 2x, exact prefix | yes: this is the cap |
| `src/facts/facts.h:213` `KsetWalk.k[]`; `:305-306` `MkLang` | storage of both | — |
| `src/gen/emit_dfa.c:6804` `win_offer_name` | the offset-k verify tables' id range | yes (more offers) |
| `src/gen/emit_dfa.c:7552` (comment) | the run pre-check's verified-extent argument | text only |
| `memfn/include/memfn.h:656` (comment) | `MF_WMAX_SPAN`'s derivation: the reseed alternative states one span per walked offset (at most 24) plus the run, inside `MF_MAX_TERM` (32) | yes: 32 + 1 > 32 |
| `src/core/limits.def:393` `PCREC_SPAN_WALK_SUBSETS` (description) | names "2 x PCREC_PREFIX_K_MAX levels" | text |
| `tests/registry/limits_check.sh:154` | the limits manifest (the name) | no (the value is not pinned there) |
| `docs/spec/tuning.md` §2.14¶2 | "the walk looks at most `PCREC_PREFIX_K_MAX` offsets deep" (the offset-k skip) | spec text, by name |
| `docs/design/kit_proof.md` (the slice section), `ctx_span.md` §11 N-1, `offset_k_skip.md` §3.3, §4.6 | design text | text |

The cover row is one reader of a bound that belongs to another walk.

### 1.3 The next bound: the kit's `MF_MAX_SPAN_POS` (32)

Past 24 the cover meets the KIT's shape bound, which pcrec already reads:

- C7 (`cc_width`, `src/gen/known.c:249`) bounds `k` by `KN_CAP - 1`, with
  `KN_CAP = MF_MAX_SPAN_POS` (`src/gen/known.c:34`); `MF_MAX_SPAN_POS = MF_MAX_TERM = 32`
  (`memfn/include/memfn.h:277`, `:302`). `MkEnd.set[MF_MAX_SPAN_POS][32]`
  (`src/gen/known.h:28`).
- The REPORT site states span 0 as ONE window span of `k` positions
  (`cover_window`, `src/gen/known.c:466`), refused by the kit past `MF_WSPAN_POS = 32`
  (`memfn/src/window.c:481`); the after-context sits at offset `k` and must be PROVEN,
  inside `[MF_PROOF_LO, MF_MAX_FWD) = [-8, 33)` (`memfn/include/memfn.h:309-315`;
  `pcrec_cover_proof_diff`, `src/gen/known.c:509`, checks every offset in it).

So pcrec alone can reach `k = 32`. `k > 32` needs the kit: a STOP-RULE case, and it is
reported, not designed, here (§2.4).

**A discrepancy, found on the way.** `kit_proof.md` §1.1's C7 says `1 ≤ k ≤
MF_MAX_SPAN_POS`; the code admits `k ≤ MF_MAX_SPAN_POS - 1`. The `- 1` is the walk's
own sentinel (`w->k = KN_CAP` means "no accept found below the cap",
`src/gen/known.c:131`), not a kit limit: `lv[]` has `KN_CAP + 1` rows, `MkEnd.set` holds
32 positions, and offset 32 is inside the proof range. It is sound (stricter than the
design), and it is exactly the bound that keeps every 32-position shape on the engine.

### 1.4 Why 24

A judgement, not a measurement, and made for a different reader.
`offset_k_skip.md` §3.3 condition 5 (2026-08-28) chose it for the offset-k skip: "A walk
bound, not a tuning knob: past two dozen bytes a still-narrow prefix is vanishingly rare
on the corpus (the largest useful offset any corpus pattern produces is 13)". The span
slice inherited it when `kit_proof.md` made the slice "the k-set walk, extended": "The
walk's own bound, `PCREC_PREFIX_K_MAX` (24, `limits.def`), is the slice's: an
`exact_len` beyond it is never stated, so a body with `k` > 24 declines C8".
`ctx_span.md` §11 N-1 already named the choice now taken: "Either the walk's limit is
raised to a value derived from `MF_MAX_SPAN_POS` (a compile-budget re-measure, D90) or
the four decline." For the cover, 24 is an unmeasured guess (memory
`pcrec-suspect-tuning-constants`); for the offset-k skip it is a reasoned bound with
headroom over a measured maximum of 13, which this design leaves alone.

## 2. Design

### 2.1 The options

| option | what moves | cost | verdict |
|---|---|---|---|
| A. raise `PCREC_PREFIX_K_MAX` to 32 | the cover AND the k-set walk: the offset-k skip's sets and verify offers, every `kset_walk` reader, the reseed window statement (24 + 1 spans becomes 33, over `MF_WMAX_SPAN` 32: pcrec's own assert, a kit derivation reopened) | movers far outside the cover; a second re-timing population (OFS/reseed cells); a kit comment and possibly a kit bound | REJECTED: couples two walks whose bounds have different readers |
| B. SPLIT: the slice gets its own bound, derived from its reader (the kit's span bound, 32); the k-set walk keeps 24; C7 admits `k = 32` as `kit_proof.md` states | the cover row on bodies of 25..32 positions; the `span_facts` listing value on bodies whose exact prefix passes 24 | one `limits.def` row, ~6 code sites, one `_Static_assert`; no kit change | CHOSEN |
| C. a cap that scales with the pattern | — | dynamic `MkLang`/`MkEnd`; the kit's 32 still binds, so nothing longer is gained; the walk still needs a bound (pcrec has segfaulted its own compiler on a 20,000-byte literal, `limits.def`'s PCREC_MAX_REQ_RUN_SCAN row) | REJECTED: buys nothing B does not |
| D. remove the cap | — | unbounded walk; the kit refuses past 32 anyway | REJECTED |

"A cap that scales" survives in B as a cap that follows the KIT: when the kit raises its
span bound (§2.4), pcrec's row is raised to match, and the assert says where.

### 2.2 The change (option B)

1. **A new `limits.def` row** beside `PCREC_PREFIX_K_MAX`:
   `PCREC_SPAN_EXACT_MAX`, value 32, unit `"positions"`, kind `"compile budget"`,
   override `NONE`. Description: how many positions from the match start the span slice
   (the `span_facts` fact) may state exact; DERIVED from its reader, the `cover` row,
   whose window statement the kit bounds at `MF_MAX_SPAN_POS` (asserted where it is
   read); its liveness walk looks twice as deep. It is "a value a pattern can be measured
   against" (`coding.md` §1.8: a body's exact prefix length), so it is a row, not a
   scratch size. It is not a `limits.md` promise: crossing it declines an optimization
   and refuses nothing (`offset_k_skip.md` §4.6's reasoning, unchanged). Name per D174:
   it says what it bounds, never the kit.
2. **`src/facts/kset.c`** `pcrec_span_walk`: the exact-prefix loop and the liveness depth
   read `PCREC_SPAN_EXACT_MAX` (`:911`, `:891`); the header comment (`:578`) follows.
   `pcrec_kset_walk` is untouched.
3. **`src/facts/facts.h`** `MkLang`: `exact_len` 0..`PCREC_SPAN_EXACT_MAX`,
   `set[PCREC_SPAN_EXACT_MAX][32]` (770 bytes become 1,026, one per Job). The
   facts layer still includes nothing of the kit (layer order, `src/facts/CLAUDE.md`).
4. **`src/gen/known.c`**: `_Static_assert(PCREC_SPAN_EXACT_MAX <= MF_MAX_SPAN_POS, ...)`
   at `KN_CAP` — the same shape as `emit_dfa.c`'s `PCREC_MAX_REQ_RUN_SCAN <=
   MF_WSPAN_POS`. It also guards `pcrec_known_derive`, which indexes `proven[d]` for
   `d < exact_len` and needs `exact_len < MF_MAX_FWD` (no caller today).
5. **C7 to the design's bound.** `kn_walk` tests the rows at depth `KN_CAP` for an
   accept after its loop (no step past it), and records "no accept up to the cap" as its
   own flag instead of the value `KN_CAP`; `cc_width` reads `1 ≤ k ≤ KN_CAP` and the
   flag. `cc_end` (C10) and `cc_after` (C11) already read `lv[k]`, which exists at
   `k = KN_CAP`. A ~6-line change; it is the step that brings `hex32`, `dig-exact-32` and
   `hex32-id` in. It could ride separately; it should not (§6 Q1).
6. **`src/facts/facts.c`** trace-build control (the ONE-WALK hull check, `:391`): it
   already compares only `d < hull.nwalk`, so positions 24..31 of the slice have no
   hull check. Leave the loop as it is and say so in its comment: past the hull's reach
   the slice's independent controls are C8's machine equality and X0 (§4.1).
7. **Text, same change:** `limits.def:393`'s `PCREC_SPAN_WALK_SUBSETS` description
   ("2 x PCREC_SPAN_EXACT_MAX levels"); `src/facts/CLAUDE.md`'s span-slice line;
   `kit_proof.md`'s slice paragraph and `ctx_span.md` §11 N-1 (a revision mark: N-1
   CLOSED by the split); `memfn.h:656`'s comment is unchanged (it describes the k-set
   walk, which keeps 24).

### 2.3 What it costs

- **Compile time.** The slice's exploration is bounded by `PCREC_SPAN_WALK_SUBSETS`
  (512), unchanged, so the worst case is unchanged; a long literal walks 64 levels where
  it walked 48 (one subset per level). No measurement is owed beyond the build lane's
  `make test` wall time.
- **Soundness of the deeper walk.** Exploration is breadth first and only the depth limit
  moves, so every subset at depth < 48 is created and expanded exactly as before; deeper
  levels can only turn an UNKNOWN liveness into a known one. A set stated before is
  therefore stated identically, and `exact_len` can only grow (an under-statement was
  already sound, `facts.h:296`).
- **Artifact size.** Movers SHRINK: the cover replaces the forward DFA, the reverse
  start recovery and the prefilter. Measured on today's compiler (`-p rx`, C text):
  the 24-byte literal (cover) is 17,409 bytes and 1,293 lines of `gcc -O2 -S`; the
  25-byte literal (unanchored) 26,479 bytes and 2,115 lines; the 31-byte literal
  32,778 bytes and 2,819 lines. `docs/dev/artifact_size_log.tsv` and any size tripwire
  covering a mover move DOWN; re-pin them in the build.
- **Seam.** No kit field, no new kit fact, no `MF_SITE_ABI` change: the REPORT site's
  shape is the same, with longer spans inside the kit's stated bounds (`len ≤
  MF_WSPAN_POS`, `start + len ≤ MF_WREACH` 64, the after-context at 32 `< MF_MAX_FWD`).
  The one kit-side unknown is C13: the kit's PURE ask may refuse a 32-position REPORT
  site it has never seen. A refusal declines the row (sound), so the movers would be
  fewer, never wrong; the build lane reads C13's `why` on each predicted mover.
- **pcrec `abi`.** No emitted scaffolding changes; a route flip on more patterns is a
  selection, not a layout (D76/D94). The build must still grep the current abi number's
  readers to CONFIRM no gate pins a mover's bytes (the recursion identity gate's (B) pin,
  the codegen pins), and run the suites that count (registry, codegen, rxtsource).
- **Spec (D80).** No `docs/spec/` text states 24 for the cover or the slice
  (`match_api.md` §6.3.4¶2's `"cover"` row and `facts_listing.md` §4.1.2¶7c name no
  bound). The caller-visible changes are values inside promised vocabularies: more
  artifacts read `"cover"` and longer `span_facts` values. Recommended spec hunk, one
  clause in `facts_listing.md` §4.1.2¶7c: "at most `PCREC_SPAN_EXACT_MAX` positions
  (`--list-limits`)", so the listing's range is a stated fact rather than an unstated
  one. `--list-limits` gains one row (`cli.md` §2.6; `limits_check.sh`'s manifest +1).

### 2.4 Past 32: a kit request (main files it; STOP RULE)

`lit-l40` (40 positions), `wild-validator-uuid-grok` and `uuid` (36), and the rulepilot
inventory's `req-<uuid>` (40) need a REPORT span longer than the kit states and proves.
The request is facts only (D157): "pcrec will state a REPORT window site whose span 0 is
`k` exact positions, `k` up to N, with one context position after it at offset `k`;
it needs the class proven over `[-1, k]`." N from the population: 40 on the bench;
the corpus count is owed (§4.3 gives it for free). How the kit holds it (a wider
`MF_MAX_SPAN_POS` decoupled from `MF_MAX_TERM`, several spans, a wider proof range) is
the kit's. Trigger (D77): this design's re-timing shows `lit-l31`'s gain (§5), so the
same gain is real for `lit-l40`; until then, filed not scheduled. pcrec's side would then
be one row edit (`PCREC_SPAN_EXACT_MAX`) behind the kit's new bound.

## 3. The standing questions

1. **Measurement regime: RELEVANT** (G3, G4 are measured). The numbers read here are
   skipmeas's `instructions:u` (match regime, dense subjects, the 7700X dev box, gcc 15.2,
   glibc) and the two compile-side counts (artifact bytes, `gcc -S` lines). The decision
   (split, admit 25..32) does not depend on the regime: the cover is answer-identical by
   proof, so the only regime question is G3's, whether some regime makes the kit's window
   find slower than the unanchored prefilter + DFA. skipmeas saw `fbf` WORSE with the
   finish stubbed, which is why §5 times every regime and `fbf` explicitly. A regime
   where the cover loses beyond noise is a finding against this design, handled by the
   one-pass rule (memory `pcrec-one-pass-loss-chasing`), not by a width cut-over chosen
   by hand.
2. **Independent control: RELEVANT** (a selection widens). §4.1 lists each check and what
   it is checked AGAINST: libpcre2 10.46 (kitproof answers, X0), the engine route of the
   same compiler (`test-axes`' deny arm), and the anchored DFA against the NFA slice
   (C8's two producers, from different machines). The mover prediction (§4.2) comes from
   the BASELINE compiler's decline records, not from the candidate. K35: the population
   is counted by the sweep (every committed pattern) and the kitproof floors (24/6/55)
   rise with the new rows. [MECH-REACH]: each new sabotage row names its witness and the
   witness's REACH is checked on the clean tree (`tests/kitproof/reach.sh`).
3. **What moves on regeneration: RELEVANT** (a limits row, generated listings).
   `--list-limits` and `internal.h`'s generated block gain the row; `limits_check.sh`'s
   manifest +1. Re-measurement moves nothing: the value is derived, not measured.
   Regenerated by the build: `tests/kitproof/answers.tsv` (`gen_answers.sh`, new rows),
   the start-set mover manifest (`tests/startset/manifests/manifest_s3_dfa.tsv`: a pattern
   that becomes a cover leaves the DFA-hat movers, as 25 rows did at s3fix600),
   `docs/dev/artifact_size_log.tsv` and any size pin over a mover. Not an abi event (§2.3).

## 4. Answer-identity plan

### 4.1 The checks, and what each is checked against

| check | against | proves |
|---|---|---|
| `make test` (`.rxt` corpus) | the oracle-verified expectations (python `re` / libpcre2) | every mover's existing cases answer as before, now through the cover |
| `make test-axes` | the same compiler with `--memfn=no-window-search` (the cover row's deny, `tuning.md` §2.43¶3d), whose artifact is the `"unanchored"` one | cover against engine on every corpus subject, every mover |
| `test-kitproof`, NEW rows (§4.4) | libpcre2 10.46 (`oracle.c`, committed `answers.tsv`) | the boundaries 24/25/31/32/33 at every startoffset and the find-all loop |
| the default build's `pcrec_cover_proof_diff` (internal error on any difference) | the kit's returned class against the stated sets | the kit proves exactly what pcrec states, at k up to 32 |
| trace build: C8 `producers-disagree` assert; X0 (`kit_proof/x0`) on the `SPANSET` records | the anchored DFA's walk; libpcre2's own sets | the slice's positions 24..31, which the hull control does not reach (§2.2 step 6) |
| `REACH_ONLY=1 bash tests/mech/run_sabotage_matrix.sh` | the clean tree | every kitproof witness still reaches its site after the row fires in new places (BOILERPLATE: a widened admission) |

### 4.2 Byte identity and the mover list

`scripts/emit_sweep.py` with main-before as baseline and the candidate, over the
committed population, `--trace`: every artifact byte-identical except the movers, and
each mover differs by its route (`RX_DFA_SCAN` to `"cover"`, `RX_DFA_PREFILTER` to
`"none"`, `RX_DFA_START` to `"attempt-start"`) and the text that follows from it. The
PREDICTED list comes from the BASELINE trace build's `KITPROOF` records
(`PCREC_KIT_PROOF_TRACE`): every decision whose `why` is `exact/producer-short`, plus
every `fixed-width` decline whose `width` fact is `[32,32]`. The check is
predicted == observed, both directions; a mover outside the prediction, or a predicted
pattern that stays (C9..C14 declining it, C13's refusal named), is read before landing.

### 4.3 Movers estimate (counted where cheap; the sweep is the count of record)

Not swept here (the brief allows single compiles only). Sources: today's compiler on the
bench patterns, and the kvcensus per-pattern data (`docs/dev/kvcensus/patterns.tsv.gz`,
2026-10-18, main `2523cfe4b`), which caps its span at 32 and cannot tell a 32-wide body
from a wider one.

| population | movers, expected | evidence |
|---|---|---|
| bench, native | 4: `lit-l31` (31), `hex32` (32), `dig-exact-32` (32), `hex32-id` (32 + `\b` contexts) | each today: `span_facts 24`, `width [k,k]`, `"unanchored"`; each 24-wide analog covers |
| bench, utf8 | the same 4 | kvcensus lists each in utf8 too |
| bench, NOT moving | `lit-l40`, `uuid`, `wild-validator-uuid-grok`, `uuid-near-miss` (`^...$`, attempt route) | width > 32 (§2.4) or another route |
| corpus | about 2 patterns x 2 encodings: `tests/litscan/litrun.rxt:1204` (31-byte literal), `tests/litscan/litrun.rxt:1320` (32-byte literal); plus whatever fixed-width body of 25..32 positions joined the corpus after 2026-10-18 (likely a handful) | kvcensus: 43 native / 14 utf8 corpus bodies have an exact span of 25 or more, nearly all variable-width (possessive and counted tests) which C7 declines |
| outside both (rulepilot inventory) | `(?i)permission is hereby granted` (28) moves; `<action-date date="(\d{8})">` (29, a capture) does not | its 20-wide analog covers; the capture's 19-wide analog does not |
| `span_facts` listing values (not artifacts) | every body whose exact prefix passes 24: bench 14 native / 11 utf8, corpus 43 / 14 (kvcensus) | the listing shows up to 32 positions where it shows 24 |

With C7 left at 31 (Q1 answered no), the bench movers are `lit-l31` alone and the
corpus mover `litrun.rxt:1204`.

### 4.4 New witnesses (`tests/kitproof/cases.tsv`)

- `verdict`: a 24-, 25-, 31- and 32-position literal and `[0-9a-f]{32}` read `cover`; a
  33-position literal and `[0-9a-f]{33}` read decline (C7, the kit's bound); `\d{32}`
  under `u`.
- `facts`: the 32-byte literal lists `32:...`; the 33-byte literal lists `32:...` (the
  bound reached, sound).
- `answer`: `[0-9a-f]{32}` and the 32-byte literal on subjects of 31, 32 and 33 bytes,
  a last-position near miss, a match at the subject end, and one with two adjacent
  matches (find-all).
- Floors 24 / 6 / 55 rise by the rows added.
- Sabotage (mech arm `kitproof`): (a) `PCREC_SPAN_EXACT_MAX` planted at 31: the
  32-position verdict witness flips (detector `run_cover.sh`); (b) C7 planted back to
  `KN_CAP - 1`: the same witness flips, and the plant must not also trip (a), so the
  two rows need distinct witnesses (the 32-wide class `[0-9a-f]{32}` for (b), the
  32-byte literal for (a), with the plant for (a) leaving C7 at 32).

## 5. Re-timing plan (not run; a night window later)

- **Cells.** Litrun throughput `mat-l31`, `fbf-l31`, `lbf-l31` and the l31 match /
  search_short cells (`bnd-l31` included); `bounded/hex32` and `bounded/dig-exact-32`;
  `loglines/hex32-id`. The row's "~6 litrun cells" counted `l40`'s three, which do not
  move under this design (§2.4). The cell list is confirmed with the bench dev before
  booking (memory `pcrec-ask-bench-dev`).
- **One variable.** Before: main at the build's base. After: main with the build. Same
  dev box (7700X), same bench pin, same gcc and glibc, same night. §4.2 proves the two
  builds' artifacts differ only on movers, so any difference on a non-mover control
  cell is noise; include `lit-l16` (cover on both) and `lit-l40` (engine on both) as the
  A/A controls.
- **Read.** G4's margin on `lit-l31` match (`instructions:u` at most 6M; skipmeas's stub
  read 4.4M) and throughput beyond noise; G3 on every cell, `fbf-l31` first. A loss
  beyond noise gets one bounded effort, then a ruling.
- **Window.** Night, cleared with Frank, outside 20:00-01:00, booked through main and the
  bench inbox after the build lands (the kit's timing run holds tomorrow night).

## 6. Open questions for the owner

1. **Include the 32-position shapes?** The design says the cover handles up to 32
   positions; the code stops at 31 because of how the walk marks "not found". Fixing
   that in the same change brings in `hex32`, `dig-exact-32` and `hex32-id` (three more
   bench patterns) for about six lines. Leaning: yes, same change.
2. **Longer than 32 (`lit-l40`, the uuids at 36): ask the kit now or wait?** It is the
   kit's bound, so it would be a kit request. Leaning: file it now as a facts-only
   request, scheduled only once this change's re-timing shows the gain on `lit-l31`.
3. **Build go** for option B (§2.2), sonnet tier, with §4's checks as its delivery bar.
</content>
</invoke>
