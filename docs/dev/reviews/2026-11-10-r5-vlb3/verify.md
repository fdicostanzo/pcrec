# VERIFY — vlb3

## V1 — FIX-1 (DEFINE skipped, `{0}` length-checked)
Cells: `printf ... | python3 -I VERIFY/ora.py` (COMMON ctypes snippet, info 15) and `VERIFY/pc.sh` (build/pcrec --features all -p rx).
- libpcre2: `(?<=a(?(DEFINE)(?<g>b+)))x` ACCEPT lb 1; `(?<=a(?(DEFINE)b+))x` ACCEPT lb 1; `(?<=a(?:b+){0})x` REJECT 125 "length of lookbehind assertion is not limited"; `(a(?(DEFINE)(?<g>b+)))(?<=\1)x` ACCEPT lb 1; `(?<=(?1))(a(?(DEFINE)(b+)))x` ACCEPT lb 1.
- pcrec HEAD: first two both rc0, `rx_VALID_LB 1`.
- mod_recursion.c:446-520 (read): "SO THIS PORT PRODUCES THE NODE THE `{0}` IDIOM PRODUCES AND NOTHING ELSE. An `A_REP` with `rmin == rmax == 0` over the parsed body"; the producer comment says "builds it as an A_REP `{0}` node". No flag distinguishes it from `(?:X){0}`.
- Whether rev 5's `hb` then refuses these is a design-text consequence (see V3 for the quoted bullet); the premise (DEFINE skipped vs `{0}` checked, AST identical, HEAD accepts today) is reproduced.
Verdict: HOLDS (premise); consequence depends on `hb` text, see V3.

## V2 — FIX-6/FIX-7 (DEFINE vs `{0}` under duplicate names, group-recursion)
Cells run via ora.py / pc.sh on VERIFY/p2.txt.
| pattern | libpcre2 | HEAD pcrec |
|---|---|---|
| `(?J)(?<n>a)(?<n>b)?(?<=x(?(DEFINE)\k<n>))y` | ACCEPT lb 1 | rc0 VALID_LB 1 |
| `(?J)(?<n>a)(?<n>b)?(?<=x(?:\k<n>){0})y` | REJECT 125 off 19 | rc0 VALID_LB 1 (HEAD accepts; stage-1 divergence) |
| `(a(?(DEFINE)(?<g>\1)))(?<=\1)x` | ACCEPT lb 1 | rc1 "a lookbehind containing a backreference, a variable or a consuming callout is not implemented ... (pattern offset 22)" |
| `((?<=x(?(DEFINE)(?1)))a)` | ACCEPT lb 1 | rc1 "every alternative of a lookbehind must have a bounded length (this one is unbounded) (pattern offset 1)" (HEAD over-refuses) |
| `((?<=x(?(DEFINE)\1))a)` | ACCEPT lb 1 | rc0 VALID_LB 1 |
| `((?<=x(?:\1){0})a)` | REJECT 125 off 1 | rc0 VALID_LB 1 |
- callgraph.c:921-928 comment and :941-944 (A_REP arm): `case A_CAP: case A_REP: case A_ATOMIC: case A_WCLASS: a = a->l; continue;` and the header "Lexical: a call under `{0}` counts, as it does for libpcre2 (`((?<=(?1){0})x)` is err 125)". A DEFINE (an A_REP{0,0}) is therefore counted like `{0}`, which is why `((?<=x(?(DEFINE)(?1)))a)` is refused at HEAD while libpcre2 accepts. A_BREF/A_VAR arm returns without marking.
Verdict: HOLDS (all libpcre2/HEAD cells reproduce; DEFINE and `{0}` diverge in libpcre2 and are one AST node in pcrec).

## V3 — FIX-2/RDYW-3/RDYR-3 (rule 0 unreachable as written)
Design copy lines: §6.2.1 L1993-2000 "`hb`, the LEXICAL bound: `hi`'s recurrence with a repeat's maximum of 0 counted as 1. Only the unbounded refusal reads it" and "`hs`: `hb` with every match-time length (a variable, a consuming callout) counted as one character ... Rule 0 reads it, so `(${v})(?<=\1)x` is still "not implemented" and not "unbounded"". §6.2.2 table row 4: "`la_widths` rules 1-3 | rule 1 reads `hb` (the branch's lexical bound ...)"; row 5: "rule 0 | after rules 1-3, a branch whose `hb` is unbounded and whose `hs` is finite". Header: "the first that holds refuses".
HEAD la_widths (src/parse/mod_lookaround.c:~316-347): `if (hi >= PCREC_W_UNBOUNDED) { if (pcrec_cwmax_static(br[i]) >= PCREC_W_UNBOUNDED) return LBW_UNBOUNDED; notbuilt = true; continue; }` i.e. HEAD's rule 1 reads the STATIC (match-time = 1) value.
HEAD pcrec (pc.sh, `${v}` literal as in the critics):
- `(?<=${v})x` rc1 "a lookbehind containing a backreference, a variable or a consuming callout is not implemented (its length is known only when matching) (pattern offset 0)"
- `(${v})(?<=\1)x` rc1 same "not implemented" sentence (offset 6)
- `(?<=a(?C"c,consume"))x` rc1 same "not implemented" (offset 0)
- `(?<=a+|${v})x` rc1 "every alternative of a lookbehind must have a bounded length (this one is unbounded)" (offset 0)
As written: `hb` is `hi`'s recurrence, and `hi`'s ANY row answers PCREC_W_UNBOUNDED for a variable (that is what "`hs` = `hb` with ... counted as one" distinguishes), so a variable branch has `hb` unbounded; rule 1 (row 4, reads `hb`) holds before row 5 and row 5's condition (`hb` unbounded) implies row 4's, so rule 0 can never be reached and `(${v})(?<=\1)x` would print the "unbounded" sentence. Contradicts the §6.2.1 sentence quoted.
Verdict: HOLDS (reading of the text; HEAD cells reproduce the sentences the design promises to keep).

## V4 — FIX-3/RDYW-4 (`{0}`/DEFINE around a variable)
HEAD pcrec: `(?<=(?:${v}){0}x)y` rc0 `rx_VALID_LB 1`; `(?<=(?(DEFINE)${v})x)y` rc0 `rx_VALID_LB 1`. Both compile and are VALID_LB today.
By the quoted rev 5 text: hi = 0+1 = 1 (0 x UNBOUNDED = 0), `hb` counts {0} as 1 so 1 x UNBOUNDED + 1 = UNBOUNDED, `hs` = 2; row 4/5 would refuse a pattern HEAD builds. The `(?(DEFINE)` form is the same A_REP{0,0} node (V1).
Verdict: HOLDS.

## V5 — FIX-4 (ceiling 187 lexical under `{0}`)
ora.py / pc.sh on VERIFY/p5.txt.
| pattern | libpcre2 | HEAD pcrec |
|---|---|---|
| `(?<=(?:a{30000}b{35536}){0}x)y` | REJECT 187 off 0 "lookbehind assertion is too long" | rc0 VALID_LB 1 |
| `(?<=(?:a{30000}b{35535}){0}x)y` | ACCEPT lb 1 | rc0 VALID_LB 1 |
| `(?<=(?:a{30000}){0}(?:b{30000}){0}(?:c{30000}){0}x)y` | ACCEPT lb 1 | rc0 VALID_LB 1 |
| `(a{40000}b{40000})(?<=\1{0}x)y` | REJECT 187 off 18 | rc0 VALID_LB 1 |
| `(a(?:b{40000}c{40000}){0})(?<=\1)x` | REJECT 187 off 26 | rc1 "not implemented" (rule 0, offset 26) |
Boundary 65535 vs 65536 reproduced; the check is per `{0}` body, not summed (cell 3 accepts). pcrec HEAD accepts where libpcre2 gives 187 (cells 1, 4).
Verdict: HOLDS (cells). The rev 5 prediction (rule 2 reads `hi`, `{0}` = 0) is the design text quoted in V3's section, not re-run.

## V6 — FIX-5 (`--engine=dfa` diagnostic precedence)
HEAD pcrec `--engine=dfa`: `(a)(?<=\1|b+)x` rc1 "every alternative of a lookbehind must have a bounded length (this one is unbounded) (pattern offset 3)"; `(a)(?<=(?1)|b+)x` rc1 "(?<=...) requires the VM engine, which --engine=dfa excludes (pattern offset 3)". Control `--engine=vm`: both print the "unbounded" sentence at offset 3. So the call-bearing (already deferred) twin takes the engine-override path today; the reference form takes the parse-time width path. That after stage 2 the reference form follows the twin is a consequence of the deferral (not re-run: nothing built).
Verdict: HOLDS (premise cells); consequence not verified (needs the stage-2 build).

## V7 — FIX-8/RDYW-5 (readers and sabotage anchors)
grep -rn over src/ cli/ lib/ (build tree):
- readers of `u.call.cwmin`: src/opt/mrl.c:754 (`pcrec_cwmin`'s A_CALL arm: `pcrec_sat_add(acc, a->u.call.cwmin, MRL_MINW_MAX)`) only; the writer is callgraph.c:353 (`((Ast *)a)->u.call.cwmin = ... m->val[i]`). mrl.c:710/750 are comments.
- callers of `pcrec_cwmin` (code): mrl.c:756, 772, 779 (own recursion), callgraph.c:860 (the cwmin fixpoint), mod_lookaround.c:321 (`la_widths`); declaration internal.h:8156.
Sabotages (tests/mech/sabotages):
- S171_cwmax_fixpoint_one_round.sh: SAB_FILE src/opt/callgraph.c; SAB_HARNESS_TARGET tests/recursion/inlookaround.rxt; SAB_COUNT 1; SAB_BEFORE starts `pcrec_ast_visit(root, cg_cwmax_publish, &m);` ... `if (!changed) break;`
- S-U10_cwmin_fixpoint_one_round.sh: same file/target/count; SAB_BEFORE starts `pcrec_ast_visit(root, cg_cwmin_publish, &m);`
- S1454_lookbehind_recursion_unchecked.sh: src/opt/postresolve.c; target tests/recursion/inlookaround_self.rxt; BEFORE `pcrec_callgraph_lookbehind_recurses(cx, p.at[i]));`
- S1455_...follows_lookaround.sh and S1490_...skips_nested_lookbehind.sh: src/opt/callgraph.c; target inlookaround_self.rxt; BEFORE begins `case A_LOOK:` (the cg_length_calls arm).
- S170_deferred_recheck_never_refuses.sh: src/parse/mod_lookaround.c; target inlookaround.rxt; BEFORE `const LbVerdict why = la_widths(cx, a->l, nbr, w, &bad);`
- No S1456 etc. named S1455 variants for references exist (ls: only S1454/55/1490 in that family).
S171/S-U10: SAB_SUITES="harness" with the single target tests/recursion/inlookaround.rxt (176 lines). Its cells are call-in-lookbehind patterns (e.g. line 44 `^(?:(?<g>ab)){0}ab(?<=(?&g))$`, line 57 the two-hop chain) which route through la_widths via pcrec_cwmax/pcrec_cwmin on A_CALL, i.e. the lookbehind rule. They are the only witness named for those rows.
Verdict: HOLDS (anchors and targets as FIX-8/RDYW-5 state; grep of design copy for S1454/S1455/S1490 not re-run here).
- Follow-up: `grep -n "S1454\|S1455\|S1490" vlookbehind_rev5.md` prints nothing (re-run): the design copy names none of these three rows. Verdict stays HOLDS.

## V8 — FIX-9 (saturation at 2^40 = UNBOUNDED)
- limits.def:394 `PCREC_LIMIT(PCREC_MINW_MAX, (1LL << 40), ...)` ("saturation ceiling (== PCREC_W_UNBOUNDED)"); internal.h:8262 `#define PCREC_W_UNBOUNDED PCREC_MINW_MAX`. So 2^40 is both the sentinel and the largest finite value.
- libpcre2 on the 25-doubling reference chain `(a{65535})(\1\1)...(\25\25)(?<=\26)x` (VERIFY/p8.txt line 1): REJECT 187 offset 192 "lookbehind assertion is too long" (65535 x 2^25 ~ 2^41 > 2^40).
- HEAD pcrec on that reference form: rc1 "a lookbehind containing a backreference ... is not implemented (...) (pattern offset 192)" (stage-1 rule 0, expected).
- Call version (copied from FIX/c12.txt line 2, `(?(DEFINE)(?<g0>a{65535})(?<g1>(?&g0)(?&g0))...(?<g25>(?&g24)(?&g24)))(?<=(?&g25))x`): libpcre2 REJECT 187 offset 547; HEAD pcrec rc1 "every alternative of a lookbehind must have a bounded length (this one is unbounded) (pattern offset 547)". Reason differs (187 vs unbounded).
The rev 5 reference-form outcome ("unbounded" sentence) follows from the saturation arithmetic, not run (not built).
Verdict: HOLDS for the HEAD/call premise and constants; reference-form consequence is by construction (not verified by run).

## V9 — FIX-11 (branch reset `(?|` and group-root first-wins)
libpcre2: `(?|(a)|(bc))(?(DEFINE)(?<g>\1))(?<=(?&g))x` REJECT 125 off 31; `(?|(a)|(bc))(d\1)(?<=\2)x` REJECT 125 off 17; `(?|(a)|(bc))(?<=(?1))x` ACCEPT lb 1; `(?|(bc)|(a))(?<=(?1))x` ACCEPT lb 2. The two `(?1)` cells differ in the accepted lb by branch order, i.e. libpcre2 resolves the duplicated number to a different group's width (first branch's group) while refusing references to it. pcrec refuses `(?|` entirely today, so no pcrec cells.
callgraph.c:149-158 (`cg_roots`): "records the FIRST A_CAP (or the AST root ...)" and "FIRST occurrence wins. A group number occurs once in a well-formed ..." (quoted below).
    /* FIRST occurrence wins. A group number occurs once in a well-formed
     * tree; the guard is here because `--no-captures` deletes wrappers and a
     * future branch-reset construct would legitimately reuse a number, and a
     * silent second binding is the shape §4.4c's "two programs for one group"
     * warns about. */
    if (g > 0 && g <= r->ncap && !r->root[g]) r->root[g] = a;
Verdict: HOLDS (libpcre2 cells; first-wins comment as quoted).

## V10 — FIX-12 (`(*ACCEPT)` inside the referenced group)
libpcre2 `(?=(a(*ACCEPT)bc))\w+(?<=\1)x`: ACCEPT lb 1 (the group is sized by its text up to the ACCEPT, 1, not 3). Search `abcax` -> match (0,5), group 1 (0,1); `zzzax` -> match (3,5), group 1 (3,4). So at match time group 1 has length 1 although its structural width is 3.
Verdict: HOLDS (cells).

## V11 — FIX-13 (`--count-groups` and deferred width refusals)
HEAD `build/pcrec --features all --count-groups --pattern P`: `(a)(?<=\1|b+)x` prints "pcrec: every alternative of a lookbehind must have a bounded length (this one is unbounded) (pattern offset 3)" (refused at parse); `(a)(?<=(?1)|b+)x` prints `1` (the call form is deferred past parse-only, so the unbounded pattern is NOT refused). Note: `-p rx -o` combination errors "--count-groups takes no -o", so the cells were run without them.
docs/spec/cli.md:446 [2.13¶1]: "Runs the real parser, parse only, nothing emitted, and prints the capturing-group count (`--count-groups --pattern 'a(b)(c(d))'` prints `3`). A pattern pcrec refuses is refused with the diagnostic a compile would give."
So the sentence is already false for the deferred call form at HEAD, and widening the deferral to references would extend that.
Verdict: HOLDS.

## V12 — RDYW-1 (who reads `cx->callgraph`)
`grep -rn 'cx->callgraph\|->callgraph' src` (build tree, code lines): callgraph.c:691/754 (writes), :979 (`pcrec_callgraph_lookbehind_recurses`), ir/nfa.c:1041 (`pcrec_callgraph_ntargets(b->cx->callgraph)`), opt/lower_enc.c:698 (`if (root != was && cx->callgraph)`), gen/emit_vm.c:10770 (`v->cg = cx->callgraph;`). `grep -n callgraph src/opt/select_engine.c` finds only comments (lines 231, 234, 240, 1383), no code read. Design copy line 1965: "`cx->callgraph` stays NULL for a call-free pattern: select_engine and the VM emitter read it, and setting it would move their bytes". compile.c order (2939-2968 per FIX/RDYW; callgraph_build at ~2915 then select_engine then postresolve).
Verdict: HOLDS (select_engine is not a reader; nfa.c and lower_enc.c are the unlisted ones).

## V13 — RDYW-2 (postresolve early return; END_WINDOW values)
postresolve.c:129-135 comment: "ONE COUNTING WALK FIRST, and the early return is what makes this pass free for every pattern that records nothing ... a lookbehind is only ever recorded when its body carries an `A_CALL`" (the code is `if (p.n == 0) return;` per RDYW; comment read here).
HEAD `--emit-facts`: `(a|bc)(?:a|bc)$` -> RX_END_WINDOW "5"; `(a|bc)(?:a|bc)\z` -> RX_END_WINDOW "4".
Verdict: HOLDS ($ gives 5, \z gives 4, so the design's predicted "4" for the `$` form is wrong; early return confirmed by comment, no lookbehind -> nothing runs).

## V14 — RDYW-6/RDYT-1 (SV2 plant also trips the cap)
libpcre2: `(a{1,255})(?<=\1)x` ACCEPT lb 255; `(a{1,127})(?<=\1\1)x` ACCEPT lb 254.
mod_lookaround.c:~331-338 (`la_widths`): `varies |= lo < hi;` then `if (varies) for ... if (out[i].hi > LA_LOOKBEHIND_VAR_MAX) { *bad = out[i].hi; return LBW_CAP; }`. limits.def:428 LA_LOOKBEHIND_VAR_MAX = 255.
Design SV2 (copy line 2269): "the column's `hi` + 1 on a varying row (`lo < hi`) | `(a|bc)(?<=\1)x`: `rx_VALID_LB` 3, libpcre2 2 | ONLY gate 3's VALID_LB compare (F10); answers stay green".
Plant on group 1 (`lo` 1 < `hi` 255 / 127): first cell `hi` 256 > 255 -> cap refusal (answer moves, "answers stay green" false); second cell branch `\1\1` becomes [2,256] > 255 -> cap refusal. Both cells are in the cap-boundary population.
Verdict: HOLDS (arithmetic against the quoted cap test; the refusal itself is stage-2 behaviour, not run).

## V16 — RDYR-1/RDYR-2 (deferral moves which diagnostic wins)
libpcre2 (code, offset) vs HEAD pcrec (first diagnostic):
| pattern | libpcre2 | HEAD pcrec |
|---|---|---|
| `(a)(?<=\1\|b+)(?<=c+)x` | 125 @3 | "every alternative ... unbounded" @3 |
| `(a)(?<=\1\|b+)x\2` | 125 @3 | "unbounded" @3 |
| `(a)(?<=\2\|b+)x` | 115 @8 (non-existent group) | "unbounded" @3 |
| `(a)(?<=(?1)+)(?<=c+)x` | 125 @3 | "unbounded" @13 (call-deferred first lookbehind loses to the parse-time second one: the precedent) |
| `(a)(?<=(?1)\|b+(?C1))x` | 125 @3 | "a callout inside a lookbehind is not supported" @14 |
| `(a)(?<=\1\|b+(?C1))x` | 125 @3 | "unbounded" @3 |
The call-deferred rows (4, 5) show what the widened deferral will do to the reference rows (1, 2, 6): the later parse-time/callout error wins, off libpcre2's first-lookbehind order. Row 3 is a HEAD-side offset difference unrelated to deferral (115 vs 125).
compile.c order (build tree): parse :2829, `pcrec_callout_sites` :2876, callgraph_build :2913, facts_seal_e1 :2923, select_engine :2950, postresolve :2968. callout.c:701-703: `if (behind) pcrec_ctx_fail(cx, at, "a callout inside a lookbehind is not supported");`.
Verdict: HOLDS (HEAD precedent cells; post-stage-2 reference behaviour is the extrapolation from the call rows, not run).

## V17 — RDYR-4 (call to a group holding a variable, HEAD)
HEAD pcrec: `(${v})(?<=(?1))x` rc1 "every alternative of a lookbehind must have a bounded length (this one is unbounded) (pattern offset 6)"; `(?(DEFINE)(?<g>${v}))(?<=(?&g))x` rc1 same "unbounded" sentence (pattern offset 21). The "not implemented" sentence is NOT printed, because the call's published cwmax is UNBOUNDED in both walks (the K127 residual quoted in la_widths' rule-0 comment).
Verdict: HOLDS.

## V18 — RDYR-5 + addendum (offset of nested-lookbehind refusals)
libpcre2 / HEAD pcrec:
| pattern | libpcre2 | HEAD pcrec |
|---|---|---|
| `(a(?<=b(?<=\1)))x` | 125 @7 | "not implemented (backreference...)" @7 |
| `(a(?<=b(?<=(?1))))x` | 125 @7 | "unbounded" @2 (the OUTER lookbehind's offset) |
| `(a)(?<=b(?<=\1+)c+)x` | 125 @8 | "unbounded" @8 |
| `(a)(?<=b(?<=(?1)+)c+)x` | 125 @8 | "unbounded" @3 |
libpcre2 blames the inner lookbehind in all four. HEAD's call-deferred rows blame the outer lookbehind (@2, @3) while the reference rows blame the inner (@7, @8); a deferred pass that reports the assertion it fixes inherits the call rows' offset, which differs from libpcre2.
Verdict: HOLDS (cells). The claim that stage 2 moves reference rows to the outer offset is an extrapolation of the call rows.

## V19 — RDYR-6 (nested lookahead referencing the group inside a lookbehind)
`(a(?<=b(?=\1)))x`: libpcre2 ACCEPT lb 1; HEAD pcrec rc0 `rx_VALID_LB 1`.
mrl.c: `pcrec_cwmin`'s `case A_LOOK: return acc;` (:747-748, adds 0); `cwmax_walk`'s A_LOOK arm (:585, in the group `A_EMPTY/A_EOL/A_CTX/A_GSTART/A_KRESET/A_LOOK`, comment ":561-584": "a lookaround consumes nothing on EVERY path ... 0 is exact at the maximum as well as at the minimum ... The body is not descended into") answers 0. So both walks give a lookahead body 0 and do not read the reference inside it.
Verdict: HOLDS (value 0 at both ends; a lookahead body is off the width path).

## V20 — RDYR-7 (branch order of the refusals)
| pattern | libpcre2 | HEAD pcrec |
|---|---|---|
| `(?<=(?:b{60000}){2}\|c+)x` | 187 "too long" @0 | "unbounded" @0 |
| `(?<=c+\|(?:b{60000}){2})x` | 125 "not limited" @0 | "must match at most 65535 characters (this one has 120000)" @0 |
la_widths (mod_lookaround.c:~320): `for (int i = nbr - 1; i >= 0; i--) { long long lo = pcrec_cwmin(br[i]), hi = pcrec_cwmax(br[i]); ... if (hi >= PCREC_W_UNBOUNDED) ... return LBW_UNBOUNDED; ... if (hi > LA_LOOKBEHIND_BRANCH_MAX) return LBW_CEILING;` i.e. last-written branch first (header: "checked per branch LAST-WRITTEN FIRST (the walk's historical order)"); libpcre2 reports the FIRST-written branch's error. The two engines pick opposite branches, so the two-branch mixed cells give different codes at HEAD already.
Verdict: HOLDS.

## V21 — RDYT-2 (`(?<=(?|(a)|(b)))\1x` under vlb_accept FEATS)
tests/lookaround/vlb_accept.py:41-42: `FEATS = ("lookaround,backrefs,atomic-groups,assertions,classes,modifiers," "named-groups,recursion")`.
pcrec HEAD with `--features $FEATS -p rx`: `(?<=(?|(a)|(b)))\1x` -> "pcrec: (?|...) requires module 'branch-reset' (pattern offset 4)". libpcre2: ACCEPT lb 1. So a gate-3 style compare over this cell counts it as pcre2-only (+1) until the module exists. Related: `(${v})(?<=\1)x` under FEATS -> "${...} requires module 'vars' (pattern offset 1)"; libpcre2 reads `${v}` literally: ACCEPT lb 3.
Verdict: HOLDS.

## V22 — RDYT-3/4/6/7 (spec/extract text)
- pattern_language.md (build tree) :460 §7.3¶6: "A backreference inside a lookbehind is refused (§7.4)." :480 §7.4¶5: "... So is a lookbehind containing a backreference, a module `vars` variable or a consuming callout (`(a)(?<=\1)`, `(?<=${v})`, `(?<=a(?C"c,consume"))`, shape 5: libpcre2 accepts the first), unless an alternative is unbounded without them (`(a)(?<=a+|\1)`, `(?<=(a)\1{2,})`: shape 7 ...)" and the `(?:)*` zero-width divergence sentence; no `{0}` sentence in ¶5.
- match_api.md:1944-1947 §6.3.1¶10: "**Other `.c` macros** (slot indices ..., `<prefix>_VALID_LB`) are internal to the artifact and not part of this contract."
- vlb_d27_extract.md line 7: "The blinded author (D27) gets THIS FILE and `pattern_language.md` §7.4 as revised by stage 2."; line 12: "pcrec's `<PREFIX>_VALID_LB` stamp is promised to equal it for every pattern both accept." The extract contains no §7.3/§7.4 hunk text (its only §7.4 mentions are lines 108, 111 pointing at ¶5 / §9.4¶8).
- §6.2.8 (design copy 2285-2335): the §7.3¶6 hunk (2293-2296) says only "by name, to a duplicated name, it is refused (`(?J)(?:(?<n>a)|(?<n>b))(?<=\k<n>)x`)", a direct reference; ¶5c's refusal list (2307-2315) has no group/call-reached duplicate-name case (§6.2.2's `(?J)...(?&g))` / `(c\k<n>)(?<=\3)` cells are not in any hunk). The reference-free `(?<=(?:a+){0}x)y` appears only in ¶5c's `{0}` bullet (line 2312), which is a backreference paragraph; the ¶5 hunk (2300-2305) edits the member list and says nothing about `{0}`.
Verdicts: RDYT-3 HOLDS (spec at stage 0 still says refused; extract promises revised text that arrives with V4). RDYT-4 HOLDS. RDYT-6 HOLDS. RDYT-7 HOLDS.

## V15 — RDYW-7 (re-entry per lookbehind, not the union)
libpcre2: `(a(?<=\2))(b)(?<=\1)x` ACCEPT lb 1; `(a)(b(?<=\1))(?<=\2)x` ACCEPT lb 1; `(?<=\2)(a)(b(?<=\1))x` ACCEPT lb 1.
All three accept, so a re-entry check run over the union of rows (outer lookbehind adds the group that contains the inner one) would over-refuse them; the design text ("It walks the column's rows"; "Rows: the closure of those edges from every deferred lookbehind's body") does not say per-lookbehind.
Verdict: HOLDS (libpcre2 cells; the union reading is text-level).

VERIFY COMPLETE
