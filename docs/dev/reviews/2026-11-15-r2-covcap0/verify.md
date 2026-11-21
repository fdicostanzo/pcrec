# verify
## 1. COST-1 (identity gate / abi)
- Population: gate line 1539-1542 = every `^pattern ` line of every tests/**/*.rxt, sort -u; so litrun.rxt:1204 (31-byte `ABCDEFGHIJKLMNOPQRSTUVWXYZabcde`) and :1320 (32-byte, + `f`) ARE in the population (call-free).
- Compiled with the gate's flags (`--features all -p rx -o -`) base vs V2 (premise/pcrec.v2): both 31- and 32-byte literals go RX_DFA_SCAN "unanchored" -> "cover"; whole file differs (cmp). So comparison (B) (whole file vs FILEPIN, same abi number) goes RED on these two patterns.
- (A) does NOT move: prog_region_raw (line 1531) = `goto rx_L0;`..`rx_accept:`; DFA-selected artifacts have an EMPTY region (comment at :1521-1525), md5 of region identical (empty) on base and V2. So COST-1's "(A) goes red" is wrong; only (B) moves.
- D76 (decisions.md 41b65ea00 :5600): pin = commit introducing the abi number; within an abi number whole file byte-exact; "ANY change to the emitted scaffolding ... is an abi bump". A route/selection move changes the search body and stamps, not scaffolding. Precedent is mixed: abi_changelog.md:226-233 (cover route's own landing, abi 92 "its search body, stamps ... move"); D148 :8379 accepts "the abi bump it costs (offset-k selections move under utf8)"; but the gate's FILEPIN history records re-pins WITHOUT a bump when artifacts moved (span-arms R1 landing f7eb10528 "abi 98 (no bump), (B) moved because ... call-free artifacts gain a longer RX_REQ_RUN define"; XARCH-DEV "abi 98 unchanged ... (B) moves only to name the tip").
- Gate itself only hard-requires equal abi stamp between subject and pin (lines 1394-1396); nothing forces a bump, but (B) does force a FILEPIN re-pin.
- Verdict: PARTLY. The design's "(B) need not move"/"not an abi event" is wrong in the sense that FILEPIN must be re-pinned (2 corpus patterns flip, plus bench-derived ones if present); (A) pin does not move. Whether it is an abi BUMP is a ruling (route selection moving has gone both ways: abi 92 bumped, R1 re-pinned without bump); design §2.3 "no bump" is not refuted but "no re-pin" would be.

## 2. SOUND-3 (sabotage plants)
- known.c: C7 `cc_width` (:247-251) requires `w.k <= KN_CAP-1`; C8 `cc_exact` (:256-279) declines `exact/producer-short` when `l->exact_len < k` (:275). Any k=32 admission therefore needs both C7 admitting 32 and exact_len >= 32.
- run_cover.sh verdict rows (:67-78) read only `RX_DFA_SCAN == cover` or not; the `why` column is a comment, never compared. So a verdict row cannot tell WHICH conjunct declined.
- Plant (b) (C7 stays at <=31, slice 32) is exactly the scratch binary premise/pcrec.v1 (V1 = slice bound 32 without the C7 fix): run: `pcrec.v1 --features all -p rx -o - --pattern '[0-9a-f]{32}'` -> RX_DFA_SCAN "unanchored" and 32-byte literal -> "unanchored" (V2 gives "cover" for both): both 32-position verdict witnesses flip under (b). Facts under V1/V2 for the 32-literal read 32:... (see below): the facts rows STAY under (b).
- Plant (a) (EXACT_MAX 31, C7 fixed) was not built (no compiler); by reading, exact_len caps at 31 so C8 declines every k=32 body -> both 32-position verdicts flip, and the facts row `32-literal -> 32:` reads 31:. Not empirically run.
- Hence: every 32-position verdict flips under both plants (verified for (b), by reading for (a)); only plant (a) moves facts rows (facts under (b) verified to stay 32:).
- Verdict: HOLDS for (b) empirically, HOLDS for (a) by reading only (partly not built).

## 3. SOUND-2 + SOUND-1 (horizon)
Commands: `$B --features all -p rx --emit-facts --pattern LIT` (LIT = a..z cycled to n bytes), field 7 of the span_facts row; B = review build/pcrec vs premise/pcrec.v2.
- Literals n=49,50,64: base `0`, V2 `32:97,...`; n=65: `0` on both. So V2's liveness horizon IS 2x32 = 64 (64 lists, 65 does not).
- `a{30}(?:b{30}c|d)`: base `24:`, V2 `31:` (as claimed). Also `a{30}(?:b{33}c|d)`: 24 -> 31; `b{35}`/`b{40}`: base 24, V2 30.
- SOUND-1: HOLDS (0 -> 32 for widths 49..64). SOUND-2: HOLDS (a half-applied build leaving horizon at 48 would list 0 for 50-byte literal; `a{30}(?:b{30}c|d)` separates 31 from 30; not built here, by V2 vs base values).

## 4. PREMISE-1 (size)
Commands: `$B --features all -p rx -e ENC -o t.c --pattern PAT; gcc -O2 -c t.c; size` .text (B = base vs V2):
- `\b[0-9a-f]{32}\b` byte 3809 -> 4683; utf8 5216 -> 6402 (both flip to "cover", grow ~23%).
- `[0-9a-f]{32}` byte 3076 -> 2903 (shrinks); utf8 4771 -> 4886 (grows).
- Matches the critic's numbers exactly. The mover grows (hex32-id both encodings; hex32 utf8). HOLDS.

## 5. PREMISE-6 + SOUND-4 (`ended` at KN_CAP-1)
known.c kn_walk :126-163 (review tree): `w->k = KN_CAP` initialiser (:132); loop j < KN_CAP (:138); the exit test `if (w->nlv[j]==0 || ended) { w->k = j; break; }` (:141) runs at the top of iteration j, so `ended` set during iteration j (:160, `kn_vnl` -> `ended = true`) yields k = j+1 for every j <= 30 via the next iteration; at j = 31 the loop ends before the test at j = 32, so k stays at the initialiser KN_CAP = 32. Therefore YES: `ended` at depth 31 reaches w->k = KN_CAP today, the same value as the "no accept below the cap" sentinel (today declined by cc_width `k <= KN_CAP-1`, :250).
Design §2.2 step 5 (design lines 153-158): "tests the rows at depth KN_CAP for an accept after its loop ... records 'no accept up to the cap' as its own flag instead of the value KN_CAP; cc_width reads 1 <= k <= KN_CAP and the flag". It does not mention `ended` / the view-gated newline at depth 31. SILENT: HOLDS (both critics' point; outcome is a decline via C7 nlv[k]>0 or C10 either way, only the `why` string can differ - not executed).

## 6. PREMISE-3 (`(?i)permission is hereby`)
`$B --features all -p rx -e ENC -o t.c --pattern PAT`, RX_DFA_SCAN: base/V2: `(?i)permission is hereby` byte cover/cover, utf8 unanchored/unanchored; `... granted` byte unanchored -> cover (V2), utf8 unanchored/unanchored. HOLDS (utf8 neither covers; byte only moves).

## 7. COST-5 vs PREMISE size probe
Commands: `build/pcrec [--features all] -p rx -o FILE --pattern LIT; wc -c FILE` (base, `-o` file name matters: bytes vary by the name length, +1 per char, e.g. t.c 32773, ab.c 32774, out.c 32775).
- `ABCDEFGHIJKLMNOPQRSTUVWXYZabcde` (the litrun.rxt:1204 literal, uppercase A..Z + abcde): 32,773 (-o t.c) / 32,775 (-o out.c) -> reproduces the design's 32,778 within the output-name header (premise's 32,784 used a longer name); with `--features all` 32,961.
- `abcdefghijklmnopqrstuvwxyzabcde` (all lowercase, what COST-5 used): 29,871 default / 30,059 `--features all` -> COST-5's 29,873 (their file name); this is a DIFFERENT literal from the design's.
- `the quick brown fox jumps over x`: 26,763 / 26,951. 24-byte a..x: 17,407.
So the contradiction resolves: size depends on literal content (letter case; likely the case-pair/class partitioning); the design's number is the uppercase-start corpus literal (litrun:1204), COST-5's is the lowercase one. Premise's 32,784 vs design 32,778 is the file-name header. COST-5 HOLDS as a doc finding (design should name the literal; the 31-byte number is for the corpus literal and does not fail to reproduce); the "does not reproduce" part is REFUTED for the corpus literal. Verdict: PARTLY.

## 8. PREMISE-2 (stale comments, FIND-site exact_len reader)
- known.c:31-33 (review tree): "The deepest fixed end the reading states (kit_proof.md section 1.1 C7): `1 <= k <= MF_MAX_SPAN_POS`; C8 then needs the slice's exact prefix, which is bounded by `PCREC_PREFIX_K_MAX`." (stale after option B).
- facts.h:530-533: "the span slice over the wrapped NFA (`MkLang`). No deny of its own: its readers (the `cover` row, the FIND sites' `exact_len` statement) state what it gives."
- `grep -rn exact_len` over memfn/include memfn/src src lib cli (*.[ch]): readers of MkLang.exact_len in code: facts.c:391,403-404,945-948 (trace/listing), known.c:264,275 (cover C8), known.c:544 (`pcrec_known_derive`, which the premise/ design say has no caller), kset.c:934 (writer). memfn.h:141,164 mention exact_len only in history/changelog comments (deleted `mf_pred.prefix_stated/exact_len/consumable_len`); `grep prefix_stated|consumable_len` in src and memfn/src: no hits. So no FIND-site reader of exact_len exists in code; the facts.h comment's "FIND sites' exact_len statement" is stale. HOLDS (the cover is the only live consumer; pcrec_known_derive is a latent second).

## Findings
Items 1 and 7 PARTLY (see above); no new finding.

## PROBED-AND-HELD
Items 2, 3, 4, 5, 6, 8 held (about 60 single compiles).
VERIFY COMPLETE
