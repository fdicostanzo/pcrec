# verify — critic round landwalk (design), 2026-10-29

Verifier (opus). Subject docs/dev/lanes/p1dsg_report.md @ 3afd1a439 (copy: verify/subject.md). Compiler build/pcrec @ main HEAD. Oracle libpcre2-8 10.46 via ctypes (verify/pcre2v.py). Every consequence re-run or re-read here.

## 1. SIM-1 and PREMISE-1 (UNIQUE rule) — both HOLD; the (state,class) rule is correct for both

**SIM-1: HOLDS.** `verify/perhit.py` (independent of simulate/; libpcre2 10.46 ctypes, starts(j) = every s where `(?:P)L` matches ANCHORED at s ending exactly at j+|L|, then one ANCHORED attempt of R at min):
- `\b(\w*)` `=x` `\1` on `"ab=x"`: libpcre2 `[(2,4),(2,2)]`; starts(2) = `[0, 2]`; per-hit at s*=0 → `None` (NOMATCH). python `re` agrees with libpcre2 ((2,4),(2,2)).
- control, non-nullable `\b(\w+)=x\1`: on `"ab=x"` starts `[0]`, both NOMATCH; on `"ab=xab"` both `(0,6),(0,2)`.
So the subject's sufficient form "`\b` with P's alphabet ⊆ `\w`" (subject.md:95) is false for nullable P.

**PREMISE-1: HOLDS.** `build/pcrec -p rw --features all -o verify/rw.c --pattern '\b\w+='` reverse tables (ncls 3; class 1 = `\w`, class 2 = `=`, class 0 = other):
`rw_reverse_next_state = {65535,65535,3, 65535,6,65535, 65535,6,65535}`, `rw_reverse_is_accepting_by_class = {0,0,0, 0,0,0, 1,0,1}`.
State 6 accepts by classes 0 and 2 and self-loops on class 1. Under the subject's wording (subject.md:92-93, "no accepting state of rev(P) is reachable from another accepting state") state 6 reaches itself, so the rule says NOT unique and declines dup-param, the design's own UNIQUE witness.

**Both true at once:** yes. The state-level rule is too strict (rejects dup-param); the syntactic `\b` form is too loose (admits nullable P). The census used the forms (subject.md:96), so it counts neither the rule nor the truth.

**The (state,class) rule** (UNIQUE iff for no reachable s, c with accepts_class(s,c) does step(s,c) reach any state with an accepting (state,class) pair; floor-0 plain accept is terminal):
- `\b\w+=`: accepting pairs (6,0),(6,2); step(6,0) = step(6,2) = 65535 (dead) → UNIQUE. Correct.
- SIM-1's nullable `\b\w*=` (`-p rw0`, verify/rw0.c): `rw0_reverse_is_accepting_by_class = {0,0,0, 0,1,0, 1,0,1}`; (3,1) accepts (empty `\w*`, `\b` holds when the byte to the left is `\w`), step(3,1) = 6, which has accepting pairs → NOT unique. Correct: it ALSO rejects SIM-1's witness.
Verdict: the correct rule is PREMISE-1's (state,class) form, transitively; it subsumes SIM-1's proposed form fix (non-nullable, `\b` first). The census should run that rule on W, not the forms.

## 2. SIM-2 (BOT-family positional accepts) — HOLDS (answer witness, stage 2 only)

`verify/perhit.py '(?:^|-)([\w-]+)' '=' '\1\b' 'ab-cd=cd'`: libpcre2 `[(2,8),(3,5)]`; starts(5) = `[0, 2]`; per-hit at s*=0 → NOMATCH. Same with `\A` in place of `^` (identical output) and `pcre2v.py '(?:\G|-)([\w-]+)=\1\b' 'ab-cd=cd'` → `(2,8),(3,5)`.
Today's routing (build/pcrec --features all --emit-facts): the backreference forms are `RX_ENGINE "vm"`, `RX_VM_START_SCAN "first-class"`; the capture-free `(?:^|-)[\w-]+=x` is `RX_ENGINE "dfa"`, `RX_DFA_SCAN "attempt"`, `RX_DFA_START "attempt-start"`, i.e. routed off the reverse pass by `pcrec_nfa_has_bot` (src/ir/nfa.c:1343-1352: N_GSTART or an N_CTX that "reads absent prev", "the reverse machine would need it at its termination boundary").
Scope: answer-relevant only where S reads P's groups (stage 2, VM hat). On the DFA route G4 holds, so two starts are harmless there. The subject's UNIQUE paragraph (subject.md:91-96) names "by-class accepts" only and its own `(?m)^` form is itself a BOT-family node that today never reaches a reverse machine, so the gap is real.
The (state,class) rule of item 1 rejects this witness IF the floor's plain (positional) accept is counted as an accepting pair (`c = none`, as PREMISE-1's fix says): the unconditional accept after `-` steps on `[\w-]` to the floor accept. Required wording: W either declines BOT-family P (a named row) or counts the floor accept in UNIQUE.

## 3. SLOT-1 (LOWER is not a FIN4 take cell on CAND_ROUTE_DFA) — HOLDS

src/gen/emit_dfa.c:10611-10624, `search-from`: `.take = { [CAND_ROUTE_DFA] = { CAND_HAND_AT, CAND_HAND_ENDSET }, [CAND_ROUTE_ATTEMPT] = { CAND_HAND_AT }, [CAND_ROUTE_VM] = { CAND_HAND_ENDSET, CAND_HAND_LOWER } }`. The other FINISH rows on DFA take ENDSET (`prio-const`), AT/ENDSET (`verify-at`), NOMATCH (`nomatch`), SPAN (`report`) — none takes LOWER on DFA. Selection is by take cell (emit_dfa.c:5579 / 5698 "only where the ask's hand is one of its take cells there"). The subject's guard (subject.md:201-202, "hand `s*(j)` as LOWER to FIN4 `search-from` on `composite`") therefore has no FINISH row on the DFA route as the table stands, and Build plan step 4 does not add the cell. Fix as SLOT-1 says (add the DFA LOWER cell with its relocate meaning, or hand an ENDSET-shaped relocate).

## 4. SLOT-4 (A not built → search-from's AT re-asks the selected LOCATE row) — HOLDS (design gap; run-time recursion, not a compile hang)

- `finish_available` (emit_dfa.c:9420-9423): `return s->route == CAND_ROUTE_VM || s->cx->job->anchored_ok;` — `verify-at` is unavailable on DFA when A was not built (`-fno-anchored-dfa` removes the build, emit_dfa.c:9409-9412; or the cap).
- `search-from` DFA needs: `{ 0, CN(CAND_SLOT_LOCATE) }` (emit_dfa.c:10616); its AT meaning: "the search entry's own LOCATE ask from the caller's position, filtered to a match starting there (E-FC)" (emit_dfa.c:10577-10579).
- `cand_path_finish` (emit_dfa.c:11897-11910): the relocate to the FALLBACK LOCATE row is taken only `if (... hand != CAND_HAND_AT)`; an AT hand goes to `cand_path_follow(cx, p, r, rt)`, i.e. the SELECTED LOCATE row on the same route — `landmark-walk` itself.
So with A absent the walk's AT hand selects FIN4, whose AT run is the walk again, from s*, which hands AT again: a cycle in what the emitted code runs. The static closure would NOT catch it: `cand_path_visit` visits each (slot, route) once (emit_dfa.c:11879-11887, "each cell is visited once, so it terminates") and the trace oracle checks only `needs & ~built`. Precedent for the fix: `cover_conj[]` row `{ "C4", "anchored-A", "machine", cc_anchored }` (src/gen/known.c:376). An `A built` admission row closes it (and, per SLOT-12, removes the rung's stated reason).

## 5. SIM-3 / PREMISE-2 (landmark choice unstated; pcrec's req_byte is `&`) — HOLDS

- `build/pcrec --features all --emit-facts --pattern '\b(\w+)=[^&]*&(?:[^&]*&)*\1='`: `req_set 38,61`; `req_set_maxoff 38:unbounded,61:unbounded`; `req_byte 38 rate:builtin-prior`; `RX_REQ_BYTE "38"` (`&`); `req_run none`; `req_landmark_maxoff unbounded decline:unbounded`.
- `&` split (`verify/perhit.py '\b(\w+)=[^&]*' '&' '(?:[^&]*&)*\1=' 'a=1 b=2&b='`): libpcre2 `(4,10),(4,5)` (python `re` agrees); starts(7) = `[0, 4]`; per-hit at s*=0 → NOMATCH. Not unique, S reads `\1` → would be `excl-lower` (stage 2), not `excl-cand`.
- `=` split, same subject: starts(1) = `[0]`, starts(5) = `[4]`; per-hit → `(4,10),(4,5)`, correct. Only the `=` split gives the row the twin measured (subject.md:229 "memchr `=`").
The subject's facts row names "the landmark (which req fact, and its offset in the run)" (subject.md:127) without a choosing rule; `req_set` carries no per-member pattern position (`req_set_maxoff` is `unbounded` for both), so PREMISE-2's "the fact needs a new input" also holds. Severity as the critics state: selection/speed and doc (no answer risk, since the `&` split lands on `excl-lower`, which simulate found exact).

## 6. SIM-5 / PREMISE-4 / COST-4 (DFA movers already start from the landmark; the 15.4 instr/B baseline does not apply) — HOLDS

**Stamps** (`build/pcrec --features all -p rx -o verify/b_NAME.c --pattern "$(cat pcrec-bench/bench/{loglines,bounded}/patterns/NAME.rx)"`):

| row | RX_DFA_PREFILTER | RX_REQ_BYTE | RX_REQ_HANDOFF | RX_DFA_START |
|---|---|---|---|---|
| ipv4 | `handoff` | 46 `.` | 3 | reverse-pass |
| kv-quoted | `handoff` | 34 `"` | 32 | reverse-pass |
| stack-frame | `offset-set-bounded` | 97 `a` | 0 | reverse-pass |
| csv5 | `memchr` | 44 `,` | none | reverse-pass |
| dotted4 | `handoff` | 46 `.` | 3 | reverse-pass |
| (5b, control) | `byte-class` | — | — | reverse-pass |

All 5 match the critics' tables. **Measurement** (shipped artifacts, own find-all driver `verify/drv_NAME.c`, `taskset -c 7 perf stat -e instructions:u -r 3`, 0.00% variance; whole process incl. startup, ~0.13-0.18M at 16 KiB):

| row | subject (pcrec-bench loglines throughput) | bytes | landmark hits | instr | ≈ instr/B |
|---|---|---|---|---|---|
| kv-quoted | t-1024k-fail | 1,048,621 | 1,330 `"` | 288,929 | 0.28 (incl. startup) |
| kv-quoted | t-1024k-hit | 1,048,621 | 8,672 | 887,147 | 0.85 |
| ipv4 | t-1024k-fail | 1,048,621 | 20,503 `.` | 3,209,849 | 3.1 (≈157 / dot) |
| ipv4 | t-1024k-syslog | 1,048,651 | 5,089 | 1,020,473 | 0.97 (≈200 / dot) |
| ipv4 | synthetic dense log (verify/gen_log.py; 8 MiB − 4 MiB marginal) | 4,194,304 | 252k (1 / 16.6 B) | 38.28M | 9.1 (≈151 / dot) |

kv-quoted's shipped baseline is at the find floor's order (0.28 instr/B, the subject's lwbyte 0.13); ipv4 is 1-3 instr/B on bench subjects. Both are 5-50x below the 15.4 instr/B c(dfa, byte-class) the rarity price uses (subject.md:307, 423). On ipv4 the shipped cost per landmark hit (~150-200 instr) is already BELOW the design's lwhit ≈ 294 per hit (measured on 5b's 8-byte walk, so not directly ipv4's; ipv4's walk is ≤ 3 B, but the verify remains). The "up to 9 DFA movers" (subject.md:461) is unsupported until c(route) is the selected path's prefiltered per-byte cost and a twin runs on a handoff row. Not measured: the twin side (denylisted; not rebuilt).

## 7. PREMISE-5 / MEAS-5 (rarity is compile-time; fz-me is 5b's pattern; the negative-control cell cannot be met) — HOLDS

- fz-me is not a pcrec-bench name: `grep -rln 'fz-me'` over pcrec-bench bench/ docs/ catalogue/ reports/ and over pcrec (excluding the denylisted lanes/ and session files) finds nothing. It is a lane-made SUBJECT, and the subject places it under "## mask-email twin" (subject.md:262-290): "fz-me per line ... identical" and "NEGATIVE control, dense `@` ... the twin is SLOWER: per line 150.9M vs 120.9M". The pattern is 5b's (`pcrec-bench/bench/subst/cases/5b-mask-email/PATTERN.rx` = `[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}`).
- Nothing reads the subject at decision time: the rarity row's inputs are `p(L)` = "the landmark's prior from the byte table F already uses" and `wlen̂` = "P's max width when bounded, otherwise the class-run prior" (subject.md:418-420); the only run-time switch is the reach guard, which trips on `j < reach` (overlap), not density (subject.md:201-202). The compiled artifact for 5b is one artifact, admitted at ratio 1237 "at any F" (subject.md:354).
- So "fz-me per line as the NEGATIVE control (it must DECLINE or not lose)" (subject.md:428) cannot pass: the same pattern cannot DECLINE for fz-me and SELECT for acc-main, and the twin measured a loss. The cell must become a stated, bounded loss (PREMISE-5's option 1), since run-time density switching is the BOONIES-filed adaptive method.

## 8. PREMISE-3 (`compound_place[]` row 1 `different-tree` would send W to a compound PART) — HOLDS (as a design question the subject never asks)

- src/core/compound.c:288-300: `compound_place[] = { "different-tree", place_tree }, { "different-options", place_options }, { "erasure-only", place_always }`, with `place_tree` = `p->derive && p->derive != &pcrec_derive_none`; header (:276-281): "a part on row 3 is an in-Job row (a `cand_rows[]` LOCATE or FINISH row: P's tree under erasure, P's options) ... Review asks it of every in-Job candidate."
- docs/design/compound.md §A.2 table row 1: "`different-tree` | the second machine's tree is not P's tree under erasure (a derivation other than `pcrec_derive_none`: split's Q, 4c's per-class searches) | compound PART"; row 3 `erasure-only` lists "the hybrid's prefilter, `rev-end`, a FINISH `verify-at`".
- No concat-prefix derivation exists: `grep -n 'prefix\|concat' src/opt/derive.c` → nothing; its only derivation is `Ast *pcrec_derive_split_q(Ctx *cx, Ast *root)` (derive.c:354; internal.h:8442/8461). `pcrec_build_nfa(Ctx *cx, Ast *root, ...)` (src/ir/nfa.c:1064) takes an AST node, so `nfa_of(P·L)` (subject.md:143) needs a new tree cut.
W's tree (a prefix of a concat) is not P's tree under erasure, so as the table reads it lands on row 1. The subject cites only locate_finish §4.6's older in-Job filing (subject.md:12-14). Whether a locator's internal machine with no part entry should be asked at all is a fair counter-argument, but the subject must make it and amend §A.2 (PREMISE-3's fix); and the derivation is missing from Build plan step 3.

## 9. Flag bits (PREMISE-6b, COST-3 "7"; SLOTS PROBED-AND-HELD "8") — 7 is right; SLOTS' reason is stale

- `lib/pcrec.h`: every `PCREC_BIT(n)` for n in 0..63 checked by loop; undefined: **55, 57, 58, 59, 60, 61, 62, 63** (8 physically free). Bit 56 = `PCREC_NO_REV_END_ONEWALK` (pcrec.h:1197), whose comment ends "Bit 55 is the kit's (`-fno-kit-size-drop`, R17-b)" (pcrec.h:1196).
- docs/dev/decisions.md:9681, D164 addendum 5 Q1: "`-fno-rev-end-onewalk` takes PCREC_BIT(56) (bit 55 went to the kit's `-fno-kit-size-drop`, R17-b); 7 bits remain, above [IFACE-PUSH]'s <= 4 trigger."
- SLOTS' source, D163 addendum 2 item 2 (decisions.md ~9606: "no flags bit (bit 55 stays free)"), is recorded as STALE by docs/design/compound.md:65/128/1477 ("bit 55 went to the kit and bit 56 to B3, D164 add. 5").
- Nuance: the kit's bit is reserved, not yet built (docs/design/memfn/r17b_prime.md:1368, B4p "Not built: ... the `drop-kit-bytes` rung and bit 55").
- plan.md [IFACE-PUSH] (row at plan.md:930, its 2026-10-22 CANDIDATE line) also files bit 57 for the cover locator's deny (`PCREC_NO_WINDOW_REPORT`, deferred to the push).
**Settled:** 7 free (57-63) with 55 reserved to the kit by ruling, so the subject's "about 8" (subject.md:167) is wrong and SLOTS' PROBED-AND-HELD is REFUTED on this point. After `PCREC_NO_LANDMARK_WALK`: 6, or 5 if cover's filed bit-57 candidate is counted. Both are above the ≤ 4 trigger, so COST-3's "state it exactly" is right.

## 10. SIM-4 (cls-s-nbsp `a\sb` is fixed width under utf8; row 3 should decline it) — HOLDS

- pcrec-bench/bench/utf8/patterns/cls-s-nbsp.rx = `a\sb`; manifest.tsv:12 "`a\sb` ascii-scoped (cls-s-nbsp) MISSES" NBSP.
- `build/pcrec --features all -e utf8 --emit-facts --pattern 'a\sb'`: `width [3,3]` (E3, src/facts/kset.c), `req_landmark_maxoff 2`, `RX_DFA_PREFILTER "offset-set"`, `RX_DFA_PREFILTER_OFFSETS "0,2*"`, `RX_DFA_START "end-minus-width"`; identical in byte mode. P = `a\s` (L = `b`) is fixed width, so row 3 `fixed` decides it and it already lives on `offset-set`.
- Control `cls-s-ucp.rx` = `(*UCP)a\sb` under utf8: `width [3,5]`, `req_landmark_maxoff 4`, `RX_DFA_START "reverse-pass"`: variable, stays.
The subject's bench DFA excl-cand list (subject.md:341, "cls-s-nbsp / cls-s-ucp (5.5, utf8, ASCII `L`)") over-counts by one, and one of the "five rows at 5.5-7.5" (subject.md:354) is row 3's.

## 11. SLOT-6(b) (row 3 restates NEXT's predicate; cases land on neither mechanism) — PARTLY

Structure HOLDS: `pf_ofs_applies_common` (src/gen/emit_dfa.c:7300-7304) = `s->forward && u->kind != DFA_PF_NONE && next_key_holds(s, NK_OFFSET_SET)` (the kit's RESEED reply), not "P fixed width"; src/gen/NOTES.md:9: "a slot's predicate asks another slot's row, never restates it". Row 3 (subject.md:82) is a restatement.
Repro (`build/pcrec --features all --emit-facts`, 3 compiles):
- `[a-z]{3}@[a-z]+` → `RX_DFA_PREFILTER "offset-set"` (row 3's target taken);
- same with `-fno-offset-skip` → `"handoff"`, `RX_REQ_HANDOFF "3"`;
- `x[0-9]{4}=[a-z]+` → `"memchr"`, `RX_REQ_BYTE "120"` (`x`), `width [7,inf)`.
The last two are fixed-width-P (with L = `@` / `=`) and get no EXACT-k row, so under row 3 they get neither mechanism: HOLDS literally. But the consequence is weaker than stated: both still start from a landmark today (handoff at hit − 3; memchr of `x`, which is at offset 0, so its hit IS the start), so no speed loss is shown; and for the third, with pcrec's own req_byte `x` the split has empty P (row 1), which is item 5's landmark-choice issue again. Fix as SLOT-6 says (row 3 as `CAND_READ` of NEXT), but the severity is maintenance, not a measured miss.

## 12. SLOT-2 / COST-1 (`RX_VM_START_SCAN` is NEXT's stamp; a LOCATE row writes `RX_DFA_SCAN`) — HOLDS

src/gen/emit_dfa.c:12157-12175 `cand_list_stamp`: `case CAND_SLOT_LOCATE: return "RX_DFA_SCAN";` (every route) ... `case CAND_SLOT_NEXT: return rt == CAND_ROUTE_VM ? "RX_VM_START_SCAN" : "RX_DFA_PREFILTER";`. A LOCATE row's selection can never be reported through `RX_VM_START_SCAN`; the subject's stamp line (subject.md:222-223) conflates slots. Stage 2 needs a named VM-route LOCATE stamp ruling (and per SLOT-2, `RX_VM_START_SCAN`'s value when `first-class` leaves the path). Stage 1's `RX_DFA_SCAN "landmark-walk"` is consistent.

## 13. MEAS-1 (a card with unit `instr` is not producible) — HOLDS

- docs/spec/measures.md:109-117 [3.1¶1]: "A row's unit and status are each one of a closed list ... a new unit ... is a new row with a new byte": units `ratio 0x01`, `walkbytes 0x02`, `bytes 0x03`, `count 0x04`. No `instr`.
- docs/design/measure_sets.md:1295-1302 §7.4a: "No set, method, card, gate or tool may REQUIRE perf counters ... Every set must be producible from TIMING ALONE, and every gate in §7.3 reads timing only".
The card rows (subject.md:406-408, `unit instr`) violate both. (A spec could add a unit row, but §7.4a forbids requiring counters for a card, so instr can only be lane evidence.)

## 14. SLOT-12 vs COST's held placement (rung before 3 `drop-anchored`) — PARTLY (SLOT-12's reason point holds; neither placement is settled by ¶2 alone)

- docs/spec/limits.md §8.4¶2: "The order is by measured cost, cheapest first, and the engine scope makes it bind only within one engine: rows 1, 2, 4a and 5 are the VM's ..., rows 3 and 4 the DFA's." ¶2a: "Rung 3 applies only where dropping the anchored machine leaves a strict subset of the artifact's machines" (the rev-end precedent: there the rung is skipped). Table row 3 gives up "`<prefix>_match`'s one-pass form"; row 4 "one add per step".
- Subject (subject.md:389-397): rung before 3 because dropping A under a selected walk "would leave `needs ⊄ built`, which is a defect".
- Judgment: (1) HOLDS — with item 4's `A built` admission conjunct the walk simply declines when A is dropped, so the defect the subject cites cannot arise and ¶2a needs nothing new; COST's "held" checked only ¶2a consistency, so it is REFUTED as a reason. (2) The order: placing the walk's drop first gives up the largest measured gain (x70 on 5b) before cheaper rungs, against ¶2's cheapest-first. But a consequence neither critic drew: under the `A built` conjunct, rung 3 firing ALSO removes the walk (it declines), so a W-only rung placed after rung 3 is moot on the DFA; the real choice is "drop W only, keep A" (before 3) vs "rung 3 drops A and W together". Which is cheaper is a measurement, so the rung's place should carry the D149 UNMEASURED label rather than the subject's structural argument. COST-6's point (the VM half of the rung is unreachable in stage 1) is consistent with this.

## 15. COST-7 ([PRIOR-COST-UNIFY] names the landmark cut-over family) — HOLDS

plan.md:84 `- [PRIOR-COST-UNIFY] STATE:blocked — ONE primitive for the landmark cut-overs (expected hit gap vs the work it saves)`; trigger line: "FOUR dispersed members of one decision family that read the byte-rate PRIOR to admit a scan: G1 `req_byte_dominated_by`, set-leads `pcrec_find_pick`, R4 `cand_rs_dense_applies`, and the new `req_landmark_admits`", plus "EIGHT further members" (lrrev) and the 2026-10-27 subtri note on the prior keying a landmark. The rarity row (`p(L)·lwhit < c(route) − lwbyte` from "the landmark's prior from the byte table", subject.md:417-419) is a further member; the subject never cites the row (grep of subject.md: no `PRIOR-COST`). Note the row is STATE:blocked (paused by D161, re-scope pending), so "use the primitive" is not available; "cite it and say which side it sits on" is the actionable part.

## 16. SLOT-13 / COST-8 ([ENTRY-TABLE], [FINDALL-NEXT], [MEASURE-SET] started and absent from the overlap list) — HOLDS

- plan.md:64 `- [ENTRY-TABLE] STATE:started` (nested child; status 2026-10-18 "E0, E0c and E1 MERGED", next E1-prime);
- plan.md:198 `- [FINDALL-NEXT] STATE:started` (status 2026-10-23, remaining I2 "the kit's `st`", I3);
- plan.md:183 `- [MEASURE-SET] STATE:started` (status 2026-10-23 M0 on main; deliverables include the set format, `--list-measurements`, the install-time tool).
The subject's "Remodel overlap" (subject.md:482-493) names only [OPT-REVEND], [COMPOUND]/[MATCH-SPLIT], [DD-11.5], [INLINE-C]. Strongest of the three: [MEASURE-SET], since the subject's card "creates" `measure/cards.tsv` (subject.md:402-404) inside that row's scope; [ENTRY-TABLE]/[FINDALL-NEXT] are plausible touch points (new LOCATE→FINISH edge; per-hit state across find-all calls) rather than shown conflicts.

## 17. Quick structural checks

**SLOT-8 (W's build condition unstated; cited site is the ENG_UNANCH branch) — HOLDS.** subject.md:140-152 names WHERE (beside the optional machines, `revend_build_one`'s pattern) but no WHEN. The cited site, src/core/compile.c:3062-3103, is inside `if (!pcrec_nfa_has_bot(&cx.job->nfa)) { cx.job->engine = PCREC_ENG_UNANCH; ... build_notempty_dfa(&cx); build_anchored_dfa(&cx); if (pcrec_revend_form_asked(&cx)) revend_choose_form(&cx, root); }`; the else arm is ENG_ATTEMPT. Stage 2's VM W has no named site. The sibling `revend_choose_form` gate (built only where asked) is the precedent.

**SLOT-9 — (a), (b) HOLD; (c) PARTLY.** (a) subject.md:92 "decided at build time on rev(P)", :134 "UNIQUE needs rev(P)", :466 "UNIQUE, decided on W" (W = rev(P·L)): two machines named. (b) decisions.md:9226 (D151 add. 4): "On the DFA route G4 holds by construction (no references)", so on stage 1 row 6's `G4 ∨ UNIQUE` is always G4. (c) the vacuity holds (LF-E1 `(a+)X\1` and DUPNAMES are VM-routed; stage 1 is CR_DFA), but SLOT-9's "declined by row 2" is wrong: row 2 `g1` (subject.md:81) tests P, and LF-E1's P = `(a+)` has no backreference (it is in S). They are declined by the ROUTE, which has no admission row (SLOT-5's point).

**SLOT-10 (member folds are F/R/A-shaped) — HOLDS.** src/gen/emit_dfa.c:4893-4901 `dfa_member_machines(Ctx *cx, const Dfa *out[3])` fills only `CAND_MF`/`CAND_MR`/`CAND_MA`; `cand_path_of` (:11920-11923) builds `p.built` from F|R / ATT / A / VM; `always_built[3]` at :11404. A W bit must be added at each. Naming collision with D164's walk "form W" not re-checked (endmark.md not opened).

**SLOT-11 — (b) HOLDS; (a) PARTLY.** (b) decisions.md:9511ff, D161 add. 14 title "the kit decides whether to scan at all" and its clarification "the pre-scan and the candidate search are ONE request"; the subject keeps PRESENCE in `.needs` (subject.md:170) and a separate "kit's find of `L`" (:188). (a) measure_sets.md:1196-1197 "A kit quantity is measured by the kit's harness mode: the forms and their timing arms are the kit's"; `lwbyte` ("the find floor per byte", owner `pcrec`, subject.md:408/415) is a find cost, so it is the kit's quantity. Whether `lwhit` (walk + verify, pcrec's machine) also contains a kit-priced edge advance was not checked.

**SLOT-15 (back_walk epoch 2 vs E3 width) — HOLDS.** src/facts/facts.def:60 `PF_FACT(WIDTH, "width", 3, PF_CORE, ...)`, :57 `KSET_WALK` epoch 3, :15 "E3 is per branch"; the subject's row (subject.md:123-124) is epoch 2 with depends `req_set req_run req_set_maxoff req_landmark_maxoff`, and its value list (:126-132) has no width, yet row 3 and the fixed-width UNIQUE form read P's width.

**SIM-6 (one per-hit rarity price applied to per-call `excl-lower`) — HOLDS structurally; number not re-run.** Row 5 `rarity` precedes rows 6/7 (subject.md:84-86) and the price is per hit (`lwhit`, :412-413), while row 7 hands LOWER(s*(j₀)) once (:86, :210). bak-1's 6.6 B/hit density was not re-measured here.

**MEAS-3 (instr break-even is not the cycle break-even) — arithmetic HOLDS; consequence not verified.** From subject.md:24, 276-277: shipped 5,477.6M instr / 2,370M cyc = IPC 2.31; twin 77.8M / 58M = IPC 1.34. The x70 instr vs x40 cycles gap is real, so a break-even priced in instructions is off in time. The "~35-40 B per hit" projection needs the twin's crossover sweep in cycles (twin denylisted; not rebuilt).

**MEAS-4 — (a) HOLDS; (b) HOLDS.** (a) subject.md:292-293: every crossover point uses "8-byte class words", so `lwhit(route, wlen)` over {2,8,32} (:412-414) is one point. (b) with c ≈ 15.4 instr/B over 4 MiB, shipped ≈ 64.6M at q = 0.001; ratio 0.008 → ≤ 0.55M even rounded up to 0.0085, vs the floor alone 0.13 × 4,194,304 = 0.545M, plus q = 0.001 of ~466k words ≈ 466 hits × 294 = 0.137M → predicted ≈ 0.68M, ratio ≈ 0.0106. The printed 0.008 is inconsistent with lwbyte 0.13 + H 294 even at rounding. (c) not checked.


## Tally

HOLDS 21 (SIM-1, PREMISE-1, SIM-2, SLOT-1, SLOT-4, SIM-3/PREMISE-2, SIM-5/PREMISE-4/COST-4, PREMISE-5/MEAS-5, PREMISE-3, COST-3/PREMISE-6b, SIM-4, SLOT-2/COST-1, MEAS-1, COST-7, SLOT-13/COST-8, SLOT-8, SLOT-10, SLOT-15, SIM-6, MEAS-3 arithmetic, MEAS-4) · PARTLY 4 (SLOT-6b, SLOT-12, SLOT-9c, SLOT-11a) · REFUTED 2 (SLOTS' 8-bit PROBED-AND-HELD; COST's held rung-placement reason) · not verified: twin-side numbers (denylisted), MEAS-3's cycle projection, SLOT-10's naming collision.
