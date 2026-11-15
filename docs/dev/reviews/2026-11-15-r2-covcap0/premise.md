# PREMISE critic, covcap

## Findings

### PREMISE-1 — hex32-id (and hex32 under utf8) get LARGER when they move; "Movers SHRINK" holds only for literals and some classes
CONFIRMED. Severity: size / doc. Effort: S (fix §2.3's sentence; re-pin size tripwires in both directions). Blast radius: §2.3 "Artifact size", §3 Q3, the build's size re-pins. Cite: §2.3 ("Movers SHRINK ... any size tripwire covering a mover move DOWN").
Repro: a scratch compiler built from the review tree with the design's change PLANTED (span walk bound 32 at kset.c:891/:911, `MkLang.set[32]`, plus step 5's C7 fix; `premise/build.sh`, `premise/pcrec.v2`). Each artifact `-p rx --features all`, then `gcc -O2 -S` lines and `gcc -O2 -c` `.text` bytes, before (review build/pcrec) -> after (V2):
- `\b[0-9a-f]{32}\b` (bench hex32-id) byte: C 18,851 -> 18,890; .s 957 -> 1,337; text 3,809 -> 4,683 (+23%). utf8: C 22,595 -> 21,558, but .s 1,404 -> 1,928; text 5,216 -> 6,402 (+23%).
- `[0-9a-f]{32}` (hex32) utf8: .s 1,237 -> 1,529; text 4,771 -> 4,886 (grows); byte: .s 738 -> 836 (grows), text 3,076 -> 2,903 (shrinks).
- `[0-9a-f]{25}`: .s grows both encodings (738 -> 776, 1,237 -> 1,361), text shrinks.
- `\d{32}` and the 31-byte literal shrink on every measure (literal: text 8,815 -> 5,282 byte).
The §2.3 numbers were taken on the literal only and generalised. The build must not pre-state "down"; any size pin over a class mover may need raising, and G3's re-timing should know hex32-id's matcher got ~23% more code (an icache-sensitive regime question, §3 Q1).

### PREMISE-2 — §1.2's "every reader" table misses readers; one (known.c:31-33) is a code comment the split makes FALSE and step 7 does not list
CONFIRMED (grep of the review tree: `grep -rn PCREC_PREFIX_K_MAX` minus build/worktrees, plus readers of `exact_len`/`MkLang`/`KN_CAP`). Severity: maintenance / doc. Effort: S. Blast radius: §1.2, §2.2 step 7. Missing rows:
- `src/gen/known.c:31-33` (the KN_CAP comment): "C8 then needs the slice's exact prefix, which is bounded by `PCREC_PREFIX_K_MAX`". After option B that is wrong (it is `PCREC_SPAN_EXACT_MAX`). Step 7's text list does not name it.
- `src/facts/facts.h:530-533` (the `span` field's comment): "its readers (the `cover` row, the FIND sites' `exact_len` statement)". The FIND-site reader no longer exists: memfn.h's history (version 20, lane wsc6) DELETED `mf_pred.prefix_stated/exact_len/consumable_len`, and `pcrec_fact_span_stated` has one caller (known.c:260). So the design's "the cover row is one reader" holds in code, but the header claims a second reader. Fix it in the same change, or a later reader of the comment will think raising the bound moves FIND sites.
- Docs naming the bound or the 24 the design leaves out: `docs/design/ctx_span.md:209`, `:247-248` (the MkLang sketch), `:265-266` (`PCREC_CTX_ITEM_TERMS` is "DERIVED from" `PCREC_PREFIX_K_MAX`; that limit exists in design only, no code); `docs/design/memfn/span_runs_sheet.md:497`; `docs/design/patfacts/inventory.md:438`; `src/facts/CLAUDE.md:17` (the step 7 list does name this one).
- Spec readers of the VALUE 24 (not the name): `tuning.md` §2.30¶4 and `facts_listing.md` §4.1.2¶7 both state `run_pin`'s `0:0+24` ("clipped to the k-set walk's reach"). Option B leaves them as they are, which is right. But the table claims to list every reader, and option A (rejected here, and a likely later proposal) would move both. They belong in the table as "no (k-set walk keeps 24)".
- `memfn/include/memfn.h:656` says "pcrec asserts its own bound <= this where it states spans". That check is a RUNTIME internal error (`src/gen/memfn_sites.c:584`), not a `_Static_assert`. Option A's "pcrec's own assert" is right only in that weaker sense.

### PREMISE-3 — `(?i)permission is hereby granted` moves under byte ONLY; under utf8 neither it nor its 20-wide analog covers
CONFIRMED. Severity: doc (mover prediction). Effort: XS. Blast radius: §1.1's analog list, §4.3's "outside both" row. Repro: `build/pcrec -p rx --features all -e utf8` on `(?i)permission is hereby` gives RX_DFA_SCAN "unanchored", prefilter "handoff", start "reverse-pass", span_facts 6, width [20,23]. The 28-wide one gives the same with width [28,31], on both the review build and the planted V1/V2. Under byte, both cover (20 today; 28 under V1/V2). §1.1 lists `(?i)permission is hereby` among the analogs that "already cover" with no encoding named, and §4.3 says the 28-wide one "moves". Both statements hold for byte only. The cause is caseless `s`/`k` folding to multi-byte characters in utf8 (width not fixed, C7), not the cap. The rulepilot count is 1 byte artifact, not 2.

### PREMISE-4 — five file:line cites in known.c are off by 1-6 lines at 9e0d5be69
CONFIRMED (`sed -n` at each cite in the review tree). Severity: doc. Effort: XS. Blast radius: §1.1, §1.3, the build brief. §1.1 `cover_conj[]` at known.c:369 is really :375 (:369 is a struct field comment). §1.3 C7 at :249 is really :250 (`cc_width` starts at :247; :249 is the `kn_walk` "rows" call). The sentinel `w->k = KN_CAP` at :131 is really :132. `cover_window` at :466 is really :462. `pcrec_cover_proof_diff` at :509 is really :510. Every other cite holds at 9e0d5be69: known.c:34, :256, :275; kset.c:252, :578, :853, :891, :911; facts.h:213, :296, :305-306; facts.c:391; known.h:28; emit_dfa.c:6804, :7552; memfn.h:277, :302, :309-315, :656; window.c:481; limits.def:392-393; limits_check.sh:154; litrun.rxt:1204, :1320.

### PREMISE-5 — §4.3's kvcensus counts do not reproduce from patterns.tsv.gz with the obvious query
SUSPECTED (the design does not state its query). Severity: doc. Effort: XS (state the query). Blast radius: §4.3's last row and corpus row. Query: rows with `span >= 25` and `exact` true in `docs/dev/kvcensus/patterns.tsv.gz`. Result: bench 14 native / 13 utf8, corpus 48 native / 17 utf8. The design says bench 14/11, corpus 43/14. Confirmed if the design's own filter (status? `whole`? dedup by id?) gives its numbers. If it does not, the "listing values that change" population is under-stated. The bench native list is: dig-exact-32, hex32, line-80, uuid-near-miss x2, wild-secrets-github-pat x2, wild-secrets-slack-webhook-url, wild-validator-uuid-grok, lit-l31, lit-l40, hex32-id, uuid, qnt-poss-plus. None of the extras is an ARTIFACT mover: each is wider than 32, variable-width or has a capture. The artifact prediction (4 bench patterns) is unaffected.

### PREMISE-6 — step 5 (C7 to k <= KN_CAP) does not say what happens when `kn_walk`'s `ended` flag is set at depth KN_CAP-1
SUSPECTED. Severity: design (a gap in the build brief; probably answer-safe because C9-C11 still gate). Effort: XS. Blast radius: §2.2 step 5, the C7 sabotage row. Today a view-gated newline met at depth 31 sets `ended` (known.c:160) and the loop then ends with `w->k = KN_CAP`. That is the same sentinel as "no accept found", so it is declined. Step 5 replaces the sentinel with a flag for "no accept up to the cap". The walk's span is defined as "the first depth some row accepts ... or one past a view-gated newline" (known.c:120-121), so `ended`-at-31 is a SECOND way to reach k = 32, and the design does not say whether the flag covers it. The build must decide explicitly. My plant admitted it (k = 32 when `ended`); a build that forgets `ended` either admits it silently or declines it silently. Add a verdict witness: a 31-position body with a `(?m)$`-style newline view at its end.

### PREMISE-7 — standing questions: yes, this is one member of a family; general form and unlocks
Severity: design (a lens, not a defect). Effort: M for the general form, XS for its first unlock.
**The family: "a bound sized for one walk, borrowed by another reader".** Members found in the review tree:
1. The cover (this design): the span slice takes the k-set walk's 24 (kset.c:891/:911).
2. The run pin: `pcrec_run_pin` clips a run (up to `PCREC_MAX_REQ_RUN_SCAN` = 32) to the k-set walk's reach (kset.c:320-325, `l = min(e0 - s0, nwalk - ro)`). The spec states the result as `0:0+24` (tuning.md §2.30¶4, facts_listing.md §4.1.2¶7). So a 25-32-position exact run pins only its first 24 positions, because of a bound chosen for the offset-k skip.
3. The run pre-check's verified extent (emit_dfa.c:7549-7553, K38-2): the stored run is 32 but the walk reaches 24, the same mismatch handled there by hand.
4. The kit's `MF_WMAX_SPAN` (memfn.h:654-657) is derived from `PCREC_PREFIX_K_MAX` + 1. It is tied by a runtime check only (memfn_sites.c:584), not the `_Static_assert` shape `PCREC_MAX_REQ_RUN_SCAN <= MF_WSPAN_POS` uses (emit_dfa.c:1446).
5. `MF_MAX_SPAN_POS = MF_MAX_TERM` (memfn.h:302): the kit's span bound borrowed from its term bound. §2.4 meets this coupling at 33.
6. `PCREC_SPAN_WALK_SUBSETS`' liveness depth is 2 x the borrowed 24 (limits.def:393).
7. Design only: `PCREC_CTX_ITEM_TERMS` "DERIVED from" `PCREC_PREFIX_K_MAX` (ctx_span.md:265).
Option B fixes member 1 only. It is the right first step: memory `pcrec-ninety-percent`, and member 1 is the one with a measured gain.
**General form.** Every per-offset walk bound is a `limits.def` row named for what it bounds (D174), with a stated DERIVATION: a reader constant plus a relation (`<=`, `==`, `2x`). The relation is checked at compile time where both constants are visible, and by `limits_check.sh` otherwise (a "derived-from" column in the D90 table; memory `pcrec-decisions-as-first-match-tables`). Raising a reader's carrier then names every bound that must follow, and no walk silently caps another's reader. The two walks over the wrapped NFA (k-set hull and span slice) become two projections of one walk whose depth is the max over its readers.
**Unlocks, with triggers:**
- U1, XS, any time: replace check 4's runtime test with a `_Static_assert(PCREC_PREFIX_K_MAX + 1 <= MF_WMAX_SPAN)`. That is the house shape, and it would have made option A's cost visible at compile time. Trigger: the next change touching either constant (this build qualifies).
- U2: the run pin reads the slice (32) instead of the hull (24), so a 25-32-position exact run pins whole. Trigger: a bench cell where a run-pinned literal of 25-32 positions that does NOT cover (a capture or VM route, e.g. rulepilot's `<action-date date="(\d{8})">`, 29 positions, VM today) loses to its own whole-run compare. D77: measure first. Remodel overlap: run_pin and the K38-2 pre-check (member 3).
- U3: one walk, two projections (hull + slice). Trigger: a third per-offset reader (ctx_span's items, member 7), or a compile-time measurement showing the double walk costs. It deletes a parallel mechanism (memory `pcrec-general-mechanisms-not-special-cases`).
- U4: the kit decouples `MF_MAX_SPAN_POS` from `MF_MAX_TERM` (§2.4's request). Trigger: as the design states (lit-l31's re-timing gain). Under the general form, pcrec's side is one row plus its derivation check.

## PROBED-AND-HELD

Method: one scratch compiler built from the review tree's sources (9e0d5be69), using no `make`, at -O1 and nice 19 (`premise/build.sh`, ~100 TUs, reusing the review tree's memfn/shared objects). Two plants:
- V1: `pcrec_span_walk` bound 32 (kset.c:891 liveness 2x, :911 exact loop), `MkLang.set[32]`. This is option B steps 2-3.
- V2: V1 plus step 5's C7 fix (`kn_walk` tests depth KN_CAP for an accept; `cc_width` takes `k <= KN_CAP`).
Each compared against the review tree's `build/pcrec`.
- **§1.1 "the cap is the only conjunct that stops their longer twins": HELD** (byte AND utf8, 3 binaries; 146 pattern x encoding x binary probes):
  - literals of 24/25/31/32/33/40 positions;
  - `[0-9a-f]{n}`, `\d{n}`, `\b[0-9a-f]{n}\b` for n = 24, 25, 31, 32, 33.
  - Under V1, every 25-31 shape flips to "cover" (prefilter none, start attempt-start) and nothing at 32 or 33 flips.
  - Under V2, every 32 shape flips too, and 33 never does.
  - So for these shapes, C9-C14 (including the kit's C13 PURE ask and `pcrec_cover_proof_diff` at k = 32, which would be an internal compile error on any proof difference) admit every longer twin.
  - Bench uuid, lit-l40 and uuid-near-miss stay on the engine on all binaries.
  - The 4 predicted bench movers (lit-l31, hex32, dig-exact-32, hex32-id) move in both encodings under V2. Only lit-l31 moves under V1, as §4.3's last sentence says.
- **G1 premise (answer identity) on V2 cover artifacts: HELD.** 5 patterns (`[0-9a-f]{32}`, `\b[0-9a-f]{32}\b`, `\d{32}`, the 31-byte literal, `[0-9a-f]{25}`), each `--emit-main` x 400 random subjects against python `re`: 0 mismatches.
- **G2 premise (nothing else moves): HELD on a sample.** 46 patterns (40 shuffled corpus `pattern` lines of 20+ chars, plus 6 constructed: variable-width bodies with exact prefixes of 28-32, a 16-literal control), byte and utf8, review build vs V2: 80 byte-identical. The only 4 diffs are the two fixed-width bodies of 28 and 31 positions, both moving to cover, as predicted. 8 compile errors were identical on both. Variable-width long-prefix bodies (`[a-z]{30}x*`, `\d{28}(?:ab)?`, `abc..ABCDEF\d+`) change their span_facts listing only, and their artifacts are byte-identical.
- **§2.3 soundness of the deeper walk: HELD by reading** kset.c:888-938. Exploration is breadth first and a budget break leaves a subset unexpanded (live -1). Known liveness values never change, so a stated set is unchanged and `exact_len` only grows. Listing values observed: 24 -> 25..32, never shrinking.
- **§1.3 kit bounds: HELD.** `MF_MAX_SPAN_POS = MF_MAX_TERM = 32` (memfn.h:277, :302). `MF_WSPAN_POS` 32 (window.c:481). The proof range [-8, 33) (memfn.h:314-315) covers the after-context at 32. `MkEnd.set[32]` (known.h:28). `lv[KN_CAP + 1]` (known.c:41). C10/C11 read `lv[k]`, which exists at k = 32. The `- 1` in `cc_width` (known.c:250) is the walk's sentinel, as stated (known.c:132, :138: the loop never tests depth 32).
- **`pcrec_known_derive` has no caller: HELD** (grep: only its declaration in known.h:48 and its definition).
- **§2.3 "no docs/spec/ text states 24 for the cover or the slice": HELD** (grep of docs/spec for 24/32/PREFIX_K_MAX near cover/span_facts). match_api §6.3.4¶2 and facts_listing §4.1.2¶7c name no bound. The only 24s in the spec are run_pin's `0:0+24` (k-set walk, unchanged; see PREMISE-2) and tuning §2.14¶2 by name.
- **§4.3 corpus movers: HELD as cited** (litrun.rxt:1204 and :1320 are the 31- and 32-byte literals). A rough grep of `pattern` lines found 4 occurrences, of which :1281 and :1399 are `engine vm` and cannot take the DFA cover. Nothing else in the corpus is a fixed 25-32 counted body except a 32-wide `[0-7]{32}` inside a backreference pattern (VM).
- **§1.2 storage readers: HELD apart from the comments in PREMISE-2.** `exact_len`/`MkLang.set` are read in code only at facts.c:391-411 (trace), facts.c:945-951 (listing), kset.c:934 and known.c:260-280. `KN_CAP` is read only inside known.c. `KsetWalk.k` is untouched by option B.
- §2.3 size numbers for the literal: HELD within the 6-byte output-name header difference (24-literal 17,415 vs the design's 17,409; 31-literal 32,784 vs 32,778).
Compiles used: about 270 pattern compiles, ~20 gcc of generated files, plus the one scratch compiler build.

