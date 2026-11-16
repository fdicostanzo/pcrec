# VERIFY — covs2d

## Verdicts

### 1. PREMISE-1 + READYSEAM-1 — HOLDS
known.c:649 `for (int d = MF_PROOF_LO; d < MF_MAX_FWD; d++)`, else-branch `memset(want, 0xff, 32)` for every d > k (d==k only when the after-context is stated); mismatch -> `over/under@d`. Subject §11.1 item 4 (cover_cap.md ~l.740): "loops over `[MF_PROOF_LO, k + 1)`", so offsets k+1..32 are no longer compared. The words "the reply's counted range" are ambiguous but the formula as written drops the check.

### 2. PREMISE-2 — HOLDS
memfn_sites.c:544 `w->len = (uint8_t)len;` :548 `w->core_len = (uint8_t)len;` :553-554 `core_lo = (uint8_t)(len ? lo : 0); core_len = (uint8_t)len;` :565-568 `pcrec_memfn_wpos_bits` = `memcpy(w->set[j], bits, 32)` with no bound. cover_window (known.c:600-601) calls pcrec_memfn_wspan and pcrec_memfn_wpos_bits.

### 3. PREMISE-7 + READYSEAM-3 — HOLDS
known.c:336 `return k <= MF_WSPAN_POS && k + 1 <= MF_WREACH && k < MF_MAX_FWD;` (three bounds). memfn_sites.c:596-597 `w->len < 1 || w->len > MF_WSPAN_POS || ... || w->start + w->len > MF_WREACH`. known.c:594-606 after-context side span `{ e->k, e->ctx_after ...}` -> `pcrec_memfn_wspan(&sp[n], side[i].off, 1, ...)`, start = k. §11.1 items 1-5 (l.728-745) change no window_bounds_check text (item 3: "states the counted span through the kit's new carrier; its length check stays FIRST").

### 4. PREMISE-3 (list) — HOLDS
grep MF_MAX_TERM in src/cli/lib: memfn_sites.h:347 (comment), memfn_sites.c:630, :948, :951, emit_vm.c:234 (_Static_assert); memfn.h:277 `#define MF_MAX_TERM 32`, :302 `MF_MAX_SPAN_POS MF_MAX_TERM`, :658 `MF_WMAX_SPAN MF_MAX_TERM`. By-value mf_class: known.h:67 `mf_class cls;` (PcrecCover); emit_dfa.c:7121 `struct CandAsked { bool held[2][2]; mf_class cls[2][2]; }`, :7157 stack `mf_class cls;`, :8443 `CandScan.cls`; stack CandScan at 8620, 8755, 9240, 9991, 11280, 11489, 12171 (7). Arithmetic: `echo $((4104*32))` = 131328; today 41*32 = 1312 (memfn.h:1340 `proven[MF_MAX_FWD - MF_PROOF_LO][32]`; FWD 33+8=41). Budget limits.def:177 PCREC_COMPILE_STACK_BUDGET 442368. (The stack hazard itself stays SUSPECTED, as the critic said.)

### 5. PREMISE-4 — HOLDS
`R/kit/emit.sh OUT def '[0-9a-f]{24}'` -> `rc=0 scan=cover c_bytes=17707 text=2695`; `{32}` -> `c_bytes=18915 text=2903`. Delta +208; neither pair is 1,752/1,960.

### 6. PREMISE-5 — HOLDS
emit_dfa.c:16281-16283 (in req_run_in_cover): `for (int o = 0; o + r->whole_len <= e->k; o++) { if (m < o || m >= o + r->whole_len) continue;` before the `j`/`b` loops. So only <= whole_len placements reach the len x 256 compare.

### 7. READYSEAM-2 (sizes) — HOLDS
memfn.h:1340 `uint8_t proven[MF_MAX_FWD - MF_PROOF_LO][32];` (41 rows today); memfn.h:671 `uint8_t len;` and :682 `uint8_t set[MF_WSPAN_POS][32];` in mf_wspan. (Its lane-ordering conclusion is a design inference, not re-run; the size facts hold.)

### 8. READYSEAM-4 + READYLIMIT-3 — HOLDS
grep -n statement-fits tests/kitproof/cases.tsv: :38-48 (why notes), :65 `facts a{40}(?:b|cc) statement-fits|41|41|...`, :72 `facts a{4095} statement-fits|4095|4095|...`; run_cover.sh:90-93 compares the facts VALUE verbatim (`[ "$got" = "$val" ]`), run with `$P` (build/pcrec, no lever). S3220/S3223 line 12 `REACH-WHY=[statement-fits]`. known.c:349 (error text), :439 (comment), :455 (`{ "C15", "statement-fits", "seam", cc_fits }`); kit_proof.md:239; facts_listing.md:144 example list. §11.2 (l.779-781) names only facts_listing.md. (predict.py is denylisted; that sub-claim not checked.)

### 9. READYSEAM-6 — HOLDS
Re-emitted `[0-9a-f]{32}` (def, byte; scan=cover, 18915 C bytes) into R/verify/p9/base; planted offset 20 of the 31-term `&&` test (single occurrence confirmed by python `count == 1`) in copies; built `gcc -O1 -include rx.h tests/kitproof/drv.c rx.c`; answers vs R/kit/oracle (libpcre2).
- NARROW (offset 20 -> `a-f` only): drv build exit=0; DIFF on 4 of 6 subjects: the 32-hex hit, hit+`0`, `x`+hit, hit+`01234567` (e.g. pcrec `-` vs libpcre2 `0:32`); OK on `xxH`-style non-match and the 31+`g` near miss (those have no digit at offset 20 / fail anyway).
- WIDEN (offset 20 -> `a-g`): drv build exit=0; DIFF on 0 of the 6 §5.3-shaped subjects (hit, prefix, hit+`0`, near miss at last position, two adjacent); DIFF only on the extra subject `0123456789abcdef0123g56789abcdef` (pcrec `0:32` vs libpcre2 `-`).
Matches the critic's claim exactly.

### 10. READYSEAM-7 + READYLIMIT-2 — HOLDS
S3223 (tests/mech/sabotages/S3223*.sh:17) SAB_AFTER = `if (st) return true;   /* SABOTAGE S3223 */` at the top of cc_fits, SAB_SUITES='kitproof', witness = verdict 40-letter literal. That is C15-always-passes, i.e. the same site/effect as §11.6's new "limit bypassed (C15 always passes)" row (cover_cap.md ~l.891-892). §11.1 item 2's assertion is a build-time check on PCREC_ANCHORED_MAX_STATES vs the kit bound; it reads nothing of cc_fits, so S3223's plant leaves a `-D` raise test unchanged (that test would be a new check; §11.1's answer-identity list names none). §11.6 l.895-896: "plant (d) (C15 removed): its witness becomes the build-time assertion's `-D` raise test".

### 11. READYLIMIT-1 — HOLDS
tests/codegen/run_anchored_match.sh:423 `-DPCREC_ANCHORED_MAX_STATES=6 \` (reference build; :425 `bad "§4b could not build the ... reference compiler"`); tests/endmark/run_b3_checks.sh:303 `if refbuild "$WORKDIR/pcrec_anch" -DPCREC_ANCHORED_MAX_STATES=3; then` (:310 "did not build"); S889_lowered_overflow_refuses.sh:3 names run_b3_checks.sh §5 as detector. Legal range per §11.2 (l.774-775) is `1 .. PCREC_ANCHORED_MAX_STATES - 1` = 1..5 / 1..2, the default 32 is outside both. Neither script is in §11.1/§11.6 lists. (Whether the lane would refuse the DEFAULT, vs only a -D value, is exactly the unstated mechanism; the literal text makes the critic's reading the safe one.)

### 12. READYLIMIT-4 — HOLDS (code fact); effect stays SUSPECTED as the critic said
compound.c:74 `.facts = facts, .harness = NULL, .meas = meas };` ; compound.c:172-175 `const PcrecMeasInherit meas = { job->meas, ..., ? w->cx->emit_in->harness->walk_arms : 0 };`. So the only harness field a part sees is walk_arms via PcrecMeasInherit.

### 13. READYLIMIT-5 — HOLDS
src/dump/limits_dump.c ~:113-114 `#define PCREC_LIMIT(name, value, unit, kind, override, anchor, desc, home) limit_row(&sb, #name, (long long)(value), ...)` over `#include "core/limits.def"`: prints limits.def's literal; limits.h:723-747 builds the in-force macro separately (`#ifndef PCREC_ANCHORED_MAX_STATES` -> `..._DEFAULT`), so a -D build's dump still shows 4096.

### 14. READYLIMIT-6 — HOLDS
limits.def header (l.62-73): "anchor ... or \"\" ... limits_check.sh verifies every §3 number that DOES exist is one of these rows' values, and every anchored row's value appears at its named section — not that every row has an anchor." limits_check.sh:190 "DUMP -> docs/spec/limits.md, forward (anchored rows only)", :227 `awk -F'\t' '$6 != ""'`. limits.md §3 subsections: 3.1 Step and work budgets, 3.2 Frame/trail, 3.3 Compile-time budgets, 3.4 buffer sizing, 3.4a pcrec_limits_tsv, 3.5 .rxt parser caps, 3.6 vars, 3.7 Findings data, 3.8 ucp, 3.9 DFA context sets, 3.10 C stack, 3.11 Lookbehind length: none is a search-route knee. §11.2 names no anchor.

### 15. READYLIMIT-8 — HOLDS
limits.h:723 `#define PCREC_LIMIT_LIMITS_H_BUILD_D(name, value, default_name) enum { default_name = (value) };` and the `#ifndef PCREC_ANCHORED_MAX_STATES / #define ... PCREC_ANCHORED_MAX_STATES_DEFAULT` block; so the default is an enum constant (0 in `#if`). Precedent `_Static_assert` at emit_dfa.c:1446 cited by the critic and present (readyseam also saw it).

### 16. MEASURE-1 + RULINGS-4 — HOLDS (not contradictory: they are two different scenarios)
§11.2 rule (cover_cap.md l.790-793): "default is the LONGEST cover width `k` among the timed movers such that every timed mover with width `<= k` is not slower than its engine route beyond the A/A noise floor in ANY regime". Timed movers (§11.4 A/B): lit-l31 (31), hex32/dig-exact-32/hex32-id (32), uuid + uuid-grok (36), lit-l40 (40); lit-l16 is an A/A CONTROL, not a mover.
(a) all class 32s slower in near-miss, lit-l31 clean: k=31 -> movers with width<=31 = {lit-l31}, clean -> qualifies; k=32 -> includes the slower 32s -> fails; k=36/40 contain 32s -> fail. Result 31 (RULINGS-4 right).
(b) lit-l31 AND all 32s slower: k=31 fails (lit-l31 slower); 32, 36, 40 all contain lit-l31 -> fail. No k qualifies: EMPTY (MEASURE-1 right). (Only if the A/A control lit-l16 were counted a mover would k=16 qualify.)
Neither reaches "24 or below": no timed mover has width 17..30, so 24 is never a candidate; the l.808-809 sentence "it would land at 24 or below" is false for the rule as written in both.

### 17. MEASURE-2 — HOLDS
§11.4 outcome table (l.843-847): "(declared, first match): every cell not slower -> default per §11.2; a stage-1 class cell slower in near-miss only -> ...; any cell slower in not-warm -> report size beside it, owner's call (§9 Q5); A/A noise above the floor -> night void, re-run." The A/A row is last. Also confirmed the row-3 vs §11.2 conflict (rule excludes a cell slower in ANY regime; row 3 says owner's call) as stated.

### 18. MEASURE-4 — REFUTED (critic's pattern lost its backslashes)
Critic's own artifact header: `R/measure/o/hex32id-b/def/rx.c:1  Pattern: b[0-9a-f]{32}b` (not `\b...\b`; shell quoting ate the `\`), and its def==eng files are that wrong pattern. Re-run with the real pattern, `R/kit/emit.sh R/verify/p18/b-def def '\b[0-9a-f]{32}\b'`:
byte def `rc=0 scan=cover c_bytes=18891 text=4683`; byte eng `scan=unanchored c_bytes=18852 text=3809`; utf8 def `scan=cover c_bytes=21559`; utf8 eng `scan=unanchored c_bytes=22596`. `cmp` def vs eng: DIFFER (both encodings). `R/kit/facts.sh '\b[0-9a-f]{32}\b'` (both): `cover 32 32 ...`. So hex32-id IS a cover mover in the default build; the consequence chain of MEASURE-4 (declined control, cannot carry the default) does not follow. (The "check RX_DFA_SCAN before timing" suggestion is still sound practice, but its premise is refuted. The critic's uuid-shape remark was not re-run.) 4 compiles + 2 facts.

### 19. MEASURE-5 — HOLDS
lit-l31 pattern taken from the critic's artifact header (`abcdefghijklmnopqrstuvwxyzABCDE`, intact): def `scan=cover c_bytes=21993 text=5282`, eng (`--memfn=no-window-search`) `scan=unanchored c_bytes=32965 text=8815`. diff of `#define`s: RX_REQ_WHY dominated->emitted, RX_REQ_HANDOFF none->0, RX_DFA_SCAN cover->unanchored, RX_DFA_PREFILTER none->offset-set ("0,9*"), RX_DFA_START attempt-start->end-minus-width; 238 differing lines in all; `rx_mf1_` kit site present only in def. Numbers identical to the critic's. So §11.4 B is not "one variable" in the strict sense. 2 compiles.

### 20. RULINGS-1 — PARTLY
HOLDS: plan_completed.md:4548 `[OPT-DIAL] STATE:completed (CLOSED 2026-09-19 ... delivered, tag stale`; tuning.md §1¶8 `--tune=N` profile, §5.4 table live, with limits.def knee cells (tuning.md:1347 `PCREC_SIZE_TERM_BAR` 0.95/0.85/0.75; :1352 `VM_INLINE_CHAIN_MAX_BYTES` 4,096 -> 8,192) and §1¶9 stating a dial cell may set a row with no CLI spelling. Subject §11.3 (cover_cap.md l.822-824): "[OPT-DIAL] is CLOSED as a plan row; the dial carrying kit options is a later item, and until then an all-inline option would ride the existing `--memfn=` carrier".
NOT as stated: the §5.4 "λ (class-matcher kit)" row (tuning.md:1346) is `src/gen/clskit.c`'s class-matcher kit, NOT the memfn search kit the owner's "options for the kit"/inline-vs-loop concerns; grep of tuning.md finds no memfn/search-kit dial row. So "the dial already carries a kit row" is true only of a different kit; "dial carrying (search-)kit options is a later item" is accurate. The sound core (the dial is live and could carry the width limit as a knee row, like VM_INLINE_CHAIN_MAX_BYTES) stands.

### 21. RULINGS-2 — HOLDS
plan.md [IFACE-PUSH] row (line ~1575): "a capability/optimization row that needs a new field or stamp adds it the usual way (D76 ritual), not a remodel". memory pcrec-iface-push-later.md: "CLARIFIED 2026-10-13 ... it is NOT a gate that new features wait for ... Never tell Frank a feature 'goes in the push' / waits for it." limits.def:56-58: `-D` = "only a build-time `-D` at pcrec's OWN compile time moves it; never a caller lever". Subject §11.5 l.862-863: "(default set by measurement, user-raisable per compile)" while §11.2 gives only the build `-D` + a test-only lever and defers the flag to the push, and the joint-landing default is 32 UNMEASURED. All as the critic says. (Its counter-precedent claims, unit/`LA_LOOKBEHIND_VAR_MAX` etc., were not re-checked.)

### 22. RULINGS-3 — HOLDS
cover_cap.md: title l.1 "bounded by that machine's own state ceiling, no budget"; l.37 "No new constant is added."; G4 l.42-53 "no budget, no tuning constant and no limit of its own ... `limits.def` loses `PCREC_SPAN_WALK_SUBSETS` and gains nothing ... No goal below may be met by adding a bound"; §1 table l.88 "no new limi[t]" (and "stage 2 retires C15"); §4.2 l.427 "`window_bounds_check` mirrors the kit's new statement check; C15 retires."; §8 l.628 "Nothing is added."; §9 Q2 l.655-671 "Leaning: accept the existing ceiling as the maximum, and no new limit." D198 Consequences (decisions.md:10238): "per (g) it carries ONE safety limit on its length (a `limits.def` row ..., the number confirmed by the owner), shared by the walk, the cover and the seam, with no cliff: past it the first positions up to the limit are still stated." Rev 5 §11.2 adds a row but gives a cliff (cover declines whole). All present; whether 14:10 "2." answers Q2 against its leaning is interpretation, but the stale text is real.

### 23. RULINGS-7 — HOLDS
limits.def:28 unit vocabulary: `"bytes" | "states" | "entries" | "elements" | "nodes" | "copies" | "groups" | "levels" | "positions" | "chars" | ...` (positions present); limits.def:171 `PCREC_MAX_POSSESS_POSITIONS, 256, "positions"`. §11.2 (cover_cap.md l.771) "unit `bytes`" for k, a count of positions; the width counts positions (documented as `k` positions throughout §11).

VERIFY COMPLETE
