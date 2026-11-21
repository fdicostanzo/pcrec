# covcap — lane report ([COVER-CAP], set S3, design only)

## STATE AT HANDOFF

STATE: delivered (design only, NO BUILD GO; nothing under `src/`, `cli/`, `lib/` or
`memfn/` changed). Branch `lane/covcap` at main `c7632c898`. Deliverable:
`docs/design/cover_cap.md` rev 0 (GOALS first, the three standing questions, the
answer-identity plan, the movers estimate, the re-timing plan, the owner's
questions), plus a one-line entry in `docs/design/CLAUDE.md` (trimmed two words
elsewhere in it to stay under the 12,288-byte limit; `check_claudemd_size.sh --all`
clean). Rulings file `docs/dev/lanes/covcap_rulings.md`: empty at every read (no
entry applied). Box use: about 25 single-pattern `build/pcrec` compiles
(`--emit-facts` and `-p rx`) and 4 `gcc -O2 -S`, scratch in
`/var/tmp/pcrec-pcrec/scratch/covcap/`; no make, no suite, no timing. Compiler read:
the main tree's `build/pcrec`, which is current (no `src/`/`memfn/`/`lib/`/`cli/`
commit since it was built, 2026-11-14 16:49). Nothing owed by this lane.

## WHERE THE CAP LIVES

- **The 24 is pcrec's, not the kit's** (so the STOP RULE did not fire for it):
  `PCREC_PREFIX_K_MAX`, `src/core/limits.def:392`, value 24. The `cover` row's C8
  (`cc_exact`, `src/gen/known.c:256`) declines `exact/producer-short` when the span
  slice's `exact_len` is below the body's width (`src/gen/known.c:275`). The slice
  (`pcrec_span_walk`, `src/facts/kset.c:853`) stops its exact prefix at
  `PCREC_PREFIX_K_MAX` (`src/facts/kset.c:911`) and its liveness at twice that
  (`:891`); storage `MkLang.set[PCREC_PREFIX_K_MAX]` (`src/facts/facts.h:306`).
- **Premise test passed:** `--emit-facts` on the 31-byte `lit-l31` prints
  `span_facts 24:...`, `width [31,31]`, `RX_DFA_SCAN "unanchored"`. The 24-byte
  literal reads `"cover"`, the 25-byte one `"unanchored"`. The 24-wide versions of
  every bench mover cover today (`[0-9a-f]{24}`, `\d{24}` byte and utf8,
  `\b[0-9a-f]{24}\b`, a 24-position uuid prefix).
- **Its other readers** (by grep): the k-set walk `pcrec_kset_walk`
  (`src/facts/kset.c:252`, the offset-k skip's hull), `KsetWalk.k[]`
  (`src/facts/facts.h:213`), `win_offer_name` (`src/gen/emit_dfa.c:6804`), a comment at
  `src/gen/emit_dfa.c:7552`, `memfn/include/memfn.h:656` (the comment deriving
  `MF_WMAX_SPAN`: 24 offsets + the run fit in 32 spans), the
  `PCREC_SPAN_WALK_SUBSETS` row's text (`limits.def:393`), `limits_check.sh:154`,
  `docs/spec/tuning.md` §2.14¶2 (by name, the offset-k skip), and the design notes
  `kit_proof.md`, `ctx_span.md` §11 N-1, `offset_k_skip.md` §3.3/§4.6. The cover is
  one reader of a bound that belongs to another walk.
- **Why 24:** chosen 2026-08-28 for the offset-k skip as a walk bound with headroom
  ("past two dozen bytes a still-narrow prefix is vanishingly rare", largest useful
  offset on the corpus 13: `offset_k_skip.md` §3.3). The span slice inherited it when
  `kit_proof.md` built the slice as "the k-set walk, extended". It was never measured
  for the cover; `ctx_span.md` §11 N-1 already named this exact choice.
- **The next bound IS the kit's:** `MF_MAX_SPAN_POS = MF_MAX_TERM = 32`
  (`memfn/include/memfn.h:277`, `:302`), read by C7 as `KN_CAP`
  (`src/gen/known.c:34`), by `MF_WSPAN_POS` (window span length, `memfn/src/window.c:481`)
  and by the proof range `[-8, 33)` (`memfn.h:309-315`). So pcrec alone reaches 32;
  past 32 (`lit-l40`, the 36-position uuids) is a kit request, which main files.
- **A code/design mismatch found on the way:** `kit_proof.md` §1.1 states C7 as
  `1 ≤ k ≤ MF_MAX_SPAN_POS`; `cc_width` (`src/gen/known.c:249`) admits
  `k ≤ KN_CAP - 1` because the walk uses `KN_CAP` as its "no accept found" value
  (`src/gen/known.c:131`). Sound (stricter), and it is what keeps every 32-position
  shape (`hex32`, `dig-exact-32`, `hex32-id`) on the engine.

## DESIGN

`docs/design/cover_cap.md` §2. Four options weighed: raise the shared row to 32
(rejected: moves the offset-k skip and every `kset_walk` reader, and the reseed
window statement would need 33 spans, over the kit's `MF_WMAX_SPAN` of 32); a cap that
scales with the pattern (rejected: the kit's 32 still binds and the walk still needs a
bound); removal (rejected); and the CHOSEN one, **split the bound**:

1. A new `limits.def` row `PCREC_SPAN_EXACT_MAX` = 32 ("positions", compile budget, no
   override), DERIVED from its reader; the span slice uses it (exact prefix, and
   liveness to twice it); `MkLang` is sized by it. The k-set walk keeps 24.
2. `src/gen/known.c` asserts `PCREC_SPAN_EXACT_MAX <= MF_MAX_SPAN_POS` (the same shape
   as `emit_dfa.c`'s `PCREC_MAX_REQ_RUN_SCAN <= MF_WSPAN_POS`); the facts layer still
   includes nothing of the kit.
3. C7 brought to the design's `k ≤ MF_MAX_SPAN_POS`: the walk tests the rows at depth
   `KN_CAP` for an accept and keeps "not found" as its own flag (about 6 lines).
4. Text in the same change: the `PCREC_SPAN_WALK_SUBSETS` row's description,
   `src/facts/CLAUDE.md`, `kit_proof.md`'s slice paragraph, `ctx_span.md` N-1 closed;
   one recommended spec clause in `facts_listing.md` §4.1.2¶7c saying the listing
   states at most `PCREC_SPAN_EXACT_MAX` positions.

Costs: compile time bounded by the unchanged 512-subset budget; the deeper walk is
breadth first with only the depth limit moved, so every set stated before is stated
the same and `exact_len` can only grow. Movers' artifacts SHRINK (today: 24-byte
literal as a cover 17,409 B of C / 1,293 asm lines; 25-byte unanchored 26,479 B /
2,115; 31-byte 32,778 B / 2,819). No kit field, no `MF_SITE_ABI` bump, no pcrec abi
bump (a route flip is a selection, not scaffolding; the build confirms no gate pins a
mover's bytes). `--list-limits` +1 row. One kit-side unknown: C13 (the kit's PURE ask)
on a 32-position REPORT site never seen before; a refusal only declines (sound).

## ANSWER IDENTITY PLAN

`cover_cap.md` §4.1-§4.2 and §4.4. Each check and what it is checked AGAINST:

- `make test`: the corpus's oracle-verified expectations.
- `make test-axes`: the same compiler under `--memfn=no-window-search` (the cover row's
  deny, read from `--list-axes` by `tests/axes/run_axes.sh`): cover against the engine
  route on every corpus subject.
- `test-kitproof`: new boundary rows at widths 24/25/31/32/33 (verdict, facts, answer),
  answers regenerated from libpcre2 10.46 (`gen_answers.sh`); K35 floors 24/6/55 raised.
- The default build's `pcrec_cover_proof_diff` internal error (kit class == stated sets).
- Trace build: C8's two-producer assert (NFA slice against the anchored DFA) and X0
  (libpcre2's sets) on the new positions 24..31, which the hull control cannot reach.
- `scripts/emit_sweep.py` main-before vs candidate: 0 changed bytes outside the movers;
  movers PREDICTED from the BASELINE trace build's `KITPROOF` records
  (`exact/producer-short`, plus `fixed-width` with width `[32,32]`) and required to
  equal the observed set both ways.
- `REACH_ONLY=1 bash tests/mech/run_sabotage_matrix.sh` (the row fires in new places),
  plus two new sabotage rows with distinct witnesses: the new bound planted at 31, and
  C7 planted back to `KN_CAP - 1`.
- Pins the build re-pins: `tests/startset/manifests/manifest_s3_dfa.tsv` (new covers
  leave the DFA-hat movers, as 25 rows did at s3fix600), `docs/dev/artifact_size_log.tsv`
  and size pins over movers, `limits_check.sh`'s manifest, the kitproof floors.

## MOVERS ESTIMATE

Estimated, not swept (single compiles only on this box tonight); the build lane's
`emit_sweep.py` run is the count of record. Sources: today's compiler on the bench
patterns, and kvcensus's per-pattern data (`docs/dev/kvcensus/patterns.tsv.gz`,
2026-10-18), which caps spans at 32.

- **Bench, artifacts that become covers:** 4 patterns x 2 encodings: `lit-l31` (31),
  `hex32` (32), `dig-exact-32` (32), `hex32-id` (32, with `\b` contexts). Each reads
  `span_facts 24`, a fixed width and `"unanchored"` today. With C7 left at 31, only
  `lit-l31`.
- **Bench, not moving:** `lit-l40` (40), `uuid` and `wild-validator-uuid-grok` (36):
  the kit's bound; `uuid-near-miss` (attempt route).
- **Corpus:** about 2 patterns x 2 encodings, `tests/litscan/litrun.rxt:1204` (31-byte
  literal) and `:1320` (32-byte literal), plus any fixed-width 25..32 body added after
  2026-10-18 (likely a handful). kvcensus's other 41 native / 13 utf8 bodies with an
  exact span of 25 or more are variable width (possessive/counted tests), which C7
  declines.
- **Outside both:** rulepilot's `(?i)permission is hereby granted` (28) would move;
  `<action-date date="(\d{8})">` (29, a capture) would not (its 19-wide analog does not
  cover either).
- **`span_facts` listing values** (text, not artifacts) grow past 24 on every body whose
  exact prefix passes 24: bench 14 native / 11 utf8, corpus 43 / 14 (kvcensus). No
  test pins such a value today (`tests/kitproof/cases.tsv`'s facts rows are all short).

**Re-timing plan** (`cover_cap.md` §5; not run): litrun `mat-l31`, `fbf-l31`, `lbf-l31`
and l31's match/search_short cells, `bounded/hex32`, `bounded/dig-exact-32`,
`loglines/hex32-id`; `lit-l16` (cover on both) and `lit-l40` (engine on both) as A/A
controls. One variable: main-before against main-after, same 7700X, bench pin, gcc and
night (the sweep proves only movers differ). `fbf-l31` is read first, since skipmeas saw
`fbf` WORSE with the finish stubbed. Cell list confirmed with the bench dev; a
Frank-cleared night window outside 20:00-01:00, after the build lands. The row's "~6
litrun cells" included `l40`'s three, which do not move under this design.

## QUESTIONS

1. **Include the 32-position shapes?** The design says the cover goes up to 32
   positions; the code stops at 31 because of how the walk marks "not found". Fixing
   that in the same change adds `hex32`, `dig-exact-32` and `hex32-id` for about six
   lines. Leaning: yes, same change.
2. **Longer than 32 (`lit-l40`, the uuids at 36): ask the kit now or wait?** That bound
   is the kit's, so it would be a kit request (facts only: "a REPORT span of up to N
   exact positions with the after-context at offset k proven"; N = 40 on the bench, the
   corpus count comes free with the build's sweep). Leaning: main files it now, scheduled
   only once the re-timing shows the gain on `lit-l31`.
3. **Build go** for the split design (`cover_cap.md` §2.2), sonnet tier, with §4's
   checks as its delivery bar and §5's re-timing in a later night window.
</content>
</invoke>
<invoke name="Bash">
<parameter name="command">W=/home/pcrec/projects/pcrec/worktrees/covcap; cat $W/docs/dev/lanes/covcap_rulings.md | wc -c; git -C $W add docs/dev/lanes/covcap_report.md && git -C $W commit -q -m "covcap: lane report

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01EedbhdRc2sW2S8SZviFBbz" && (cd $W && timeout 120 scripts/lanecheck --deliver docs/dev/lanes/covcap_deliver.txt covcap 2>&1 | tail -15)