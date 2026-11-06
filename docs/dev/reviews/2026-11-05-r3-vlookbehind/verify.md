# verify.md (crit-vlookbehind verifier)

## PREMISE-1
Ran oracle_probe c and my own verify/mv.c (pcre2_set_max_varlookbehind 65535/70000/100000):
`(?<=a{65535}b)x` and `(?<=(?:a{1000}){66})x` REJECT err 187 "lookbehind assertion is too long" at every setting;
`(?<=(?:a{1000}){65})x` ACCEPT maxlookbehind=65000. Review-tree `build/pcrec --features all -p rx --emit-main -o verify/p1.c --pattern ...` returned rc=0 for all three.
Verdict: HOLDS

## SOUND-1
Oracle (oracle_probe m): `(?<=a{1,2}|b)x`/`bx` [1-2]; `(?<=a{2,3}|b)x`/`bx` [1-2]; `(?<=a{1,2}|bc)x`/`bcx` [2-3].
Today's vm_look_behind_branch (src/gen/emit_vm.c:7117-7220) back-steps from `scan_position` (guard `scan_position < k`, then VSK_BACKSTEP seek), not from a POS slot; its NEXT-BRANCH push happens BEFORE the back-step so it records the cursor. POS slot is read only in the end-check.
Hand execution of §5.1 literally (push after back-step, records candidate):
- cell1: cursor 1, d=1 -> scan_position 0; push(L_adv0,0); body a{1,2} fails on 'b'; pop -> L_adv0 with scan_position=0; d==lo -> L_b1 at scan_position 0; guard 0<1 -> rx_fail. NOMATCH (oracle: match).
- cell2: cursor 1, d=1<lo=2 -> goto L_b1 with scan_position=0 (already stepped back); guard fails. NOMATCH.
- cell3: cursor 2, d=2, pos0 fails; adv: pos1,d=1; push(adv,1); body fails; pop -> L_adv0, d==lo -> L_b1 with scan_position=1; bc needs 2 > 1 -> fail. NOMATCH (oracle [2-3]).
Unless L_b(i+1) re-reads the cursor from the POS slot (not stated in §5.1, and today's code does not), the design as written miscompiles all three.
Verdict: HOLDS

## SOUND-2
`build/pcrec --features all -p rx --emit-main -o verify/s2.c --pattern '(?<=a|bc)x'` (rc 0). Branch 1 prologue (s2.c:263-267): `if (scan_position < 1) goto rx_L7; RX_PUSH(&&rx_L7, scan_position); RX_CHARGE_WORK(1); scan_position = rx_back_step(...,1); if (scan_position == rx_BACK_STEP_NONE) goto rx_fail;`. Last branch (276-279): guard, CHARGE_WORK(2), back-step, sentinel check; no push.
vs §5.1 with lo==hi: §5.1 order is back-step, clamp test, then RX_PUSH(&&L_adv, scan_position) (position AFTER the step), then RX_CHARGE_WORK(...). Emitted order is guard, PUSH (at cursor), CHARGE_WORK(k, full width once), back-step, sentinel. So statement order, push position (cursor vs cursor-k) and charge amount (k once vs unstated "per candidate") all differ; byte identity is not a pure compile-time fold. (Charge amount: §5.1 says "per candidate tried", unspecified amount, so "differs" is about the unstated amount.)
`grep -c 'fixed width' verify/s2.c` = 0 (and `grep -ci lookbehind` = 0 per-branch comments in the C); `--emit-ir` listing lines 66 and 79 carry "lookbehind branch N of 2, fixed width K". So the claim that the comment is in the emitted C is mislocated; it is in the IR listing.
Verdict: HOLDS

## RULING-2
Oracle c: `(a{300})(?<=\1)x`, `(a)(?<=\1|b{300})x`, `(?<=\1)(a{300})x` all ACCEPT maxlookbehind=300.
src/opt/mrl.c pcrec_cwmin, A_BREF arm (line ~708-714): "A backreference's minimum is 0 EXACTLY ... `case A_BREF:` ... return acc;" (cwmin=0). Its cwmax counterpart (mrl.c:528-541 header) says A_BREF is unbounded "deliberately".
Design stage 2 sentence (subject line 297): "`pcrec_cwmax(A_BREF)` = the widest group it can name (union over duplicate names; unbounded if any is)". `grep -n cwmin subject` finds only line 184 (the generic `[lo_i,hi_i]` source); nothing says cwmin(A_BREF) changes. So under §5.2 a ref to a fixed group of width 300 is range [0,300]: it VARIES, 300>255, REFUSED, while libpcre2 accepts. The design is silent about cwmin.
Verdict: HOLDS

## RULING-1
Oracle c: `(?J)(?:(?<n>a)|(?<n>b))(?<=\k<n>)x` REJECT 125; `(?J)(?<n>a)|(?<n>bc)(?<=\k<n>)x` REJECT 125; `(?|(a)|(b))(?<=\1)x` REJECT 125; `(?|x)(a)(?<=\1)x` REJECT 125 (branch reset anywhere); `(?J)(?<n>a)|(?<n>bc)(?<=\1)x` ACCEPT maxlookbehind=1 (numbered ref OK).
`man pcre2pattern` (installed), Lookbehind section: "there must be no use of (?| in the pattern (it creates duplicate group numbers), and if the backreference is by name, the name must be unique." Design stage 2 says "union over duplicate names" i.e. accepts what libpcre2 refuses (tier-1/2 divergence in the accept direction; the design neither states it as intended nor mentions (?|).
Verdict: HOLDS

## RULING-3
Oracle c: `(?<=\1)(a)` ACCEPT maxlookbehind=1; `(?<=\1(a))x` ACCEPT 2; `(?<=(a\1))x` REJECT 125 (self reference); `(a)(?<=\1)x` ACCEPT 1.
pcrec_cwmax header (src/opt/mrl.c ~535-541): "a lookbehind branch containing a backreference is therefore never fixed-width — which is the answer libpcre2 gives too." The oracle contradicts it: libpcre2 accepts backreference lookbehinds when the group is bounded, with the 125 limited to self reference/duplicates/(?|.
src/parse/mod_lookaround.c:591: the deferral is `else if (pcrec_has_call(body))` only; its comment says "`pcrec_has_call` IS THE TEST AND NOT 'is any width unbounded'". No A_BREF / forward-group / self-reference predicate; a forward `(?<=\1)(a)` has the group unparsed at the hook, and `(?<=(a\1))x` needs a self-reference refusal the design does not state.
Verdict: HOLDS

## RULING-4
`git -C <review tree> grep -n "variable-length lookbehind is not implemented" -- tests scripts docs/spec src cli lib`: producers src/parse/mod_lookaround.c:375 and :385 (two sentences); readers: tests/recursion/run_lookbehind_call_sweep.py:105 (regex alternation `variable-length lookbehind is not implemented|this lookbehind is too long`, a live reader), tests/recursion/inlookaround.rxt:120 (a MEASURED comment quoting it). None in scripts/ or docs/spec/ under the exact text. Related non-literal mentions: tests/lookaround/lookbehind_group_alt.{rxt,gen.py} (cells described as "variable-length lookbehind ... pcrec refuses by capability (§7.4)"), tests/recursion/gen_corpus.py:1851.
docs/spec/pattern_language.md §9¶2 (line 625) says: "a lookbehind alternative of varying length, or containing a backreference (§7.4), including a group of alternatives of different lengths (`(?<=(?:a|bc))x`), which libpcre2 accepts as a variable-length lookbehind"; and the refusal-shape table row 5 (line 150) names "variable-length lookbehind, §7.4". docs/spec/match_api.md §4¶6 (line 1300): "a compile-time width analysis (`pcrec_maxw`) disagreeing with what the emitter walked ... module lookaround's negative-polarity lookbehind end-check". Confirmed. (Note `pcrec_maxw` was renamed `pcrec_cwmax` per the mrl.c header, so that spec mention is also stale.)
Verdict: HOLDS

## SOUND-3
Oracle (UTF): `(?<=(é{1,2}))x` on `aééx` [5-6,1-5]; on `éx` [2-3,0-2]. (Byte mode for contrast: `aééx` [5-6,3-5].)
Hand-execution of "d = min(hi, bytes before cursor)": 
- W6 `aééx` (bytes a=0, é=1-2, é=3-4, cursor 5): d=min(2,5)=2; stepping 2 characters back from byte 5 reaches byte 1; body é{1,2} consumes both é to 5; end-check ok; g1=(1,5). Identical to the oracle and to the correct clamp (3 characters precede, 3>=hi=2, d=2): the sabotage is GREEN, W6 does not catch it.
- `éx` (é=0-1, cursor 2): correct d=1 (1 character precedes) -> back 1 char -> byte 0 -> match [2-3,0-2]; byte clamp d=min(2,2)=2 -> a 2-character step runs off the start -> rx_fail -> nomatch. This cell distinguishes (needs fewer characters than hi but at least hi bytes).
So W6 as written cannot fail under its named sabotage; `éx` is the discriminating cell.
Verdict: HOLDS

## SOUND-4
Design §7 (subject lines 330-339): S136 re-aim = "the analysis reports a ONE-POINT branch's width one too large", cells `(?<=bc|d)x`/`abcx` and `(?<!bc|d)x`/`bcax`; §5.3: hard return only when lo_i == hi_i ("the end-check can fail on a correct compiler iff lo_i < hi_i"). Oracle: both cells [3-4].
Sabotage = pcrec_cwmax +1 only (cwmin untouched), so bc = [2,3] (and d = [1,2]), both varying, so a failed end-check is an ordinary decline on both polarities:
- positive `abcx`, cursor 3: bc: back up to 3, d=3, pos 0, body bc vs 'a' fails; adv to pos 1, d=2: bc matches 1-3, end==cursor, match [3-4] = oracle. GREEN.
- negative `bcax`, cursor 3: bc: d=3 pos 0, bc matches 0-2, end 2 != 3 -> DECLINE (not INTERNAL); adv pos 1 d=2: 'c' fails 'b'; exhausted; d branch tries 'd' at pos1,2: fails; all branches fail -> negative holds -> [3-4] = oracle. GREEN.
Both cells stay equal to the oracle, so the re-aimed S136 does not detect an over-reporting cwmax; it detects only a sabotage that edits the stored one-point pair at both ends.
Verdict: HOLDS

## SIM-1
Own probe verify/sp.c (pcre2_match at offset, optional PCRE2_UTF), pattern/subject/offset 3: `(?<=\ba{1,2})x` on `baax`: byte nomatch, UTF [3-4]. Fixed twin `(?<=\baa)x`: byte nomatch, UTF [3-4] (same divergence already exists today for fixed width).
Documented divergence (frozen tree 9f077685a): docs/dev/decisions.md D142 item 3 "PCRE2_UTF's backward-read clipping is a STATED DIVERGENCE ... libpcre2 treats startpos - LB as the subject start for lookbehind/`\b` reads ... That is 4 cells per config, pinned exactly"; docs/spec/match_api.md §9.4¶8: "A stated divergence: `PCRE2_UTF` clips backward reads at `f`; pcrec does not ... only for patterns whose backward reach exceeds LB (three patterns in the pinned set). The class is 4 cells per configuration, pinned EXACTLY (`CLIP` in tests/utfcheck/check.py)". The design neither mentions this class nor says gate 1's "0 differences" excludes UTF x startpos>0 x `\b`/nested-lookbehind-in-varying-body cells; a varying body widens the exposed set, so gate 1 as written is unreachable there (I did not re-count the critic's 7776/19.7M figure).
Verdict: HOLDS

## SIM-2
Oracle m: `(?<=a{1,2})a` on `aaa` [1-2][2-3]; `(?<=(?:ab){1,2})a` on `ababa` [2-3][4-5]. For contrast the possessive body (what a tail-possessified body computes): `(?<=a{1,2}+)a` on `aaa` [2-3] only; `(?<=(?:ab){1,2}+)a` on `ababa` [4-5] only.
Hand-execution of the §5.1 loop with the body's tail quantifier possessified, `(?<=a{1,2})a` on `aaa`: cursor 1: d=1, pos 0, body takes aa (ends 2) != cursor 1 -> decline, no frame inside the possessive body to retreat to; L_adv: d==lo -> exhausted -> fail: the (1,2) match is lost. Cursor 2: d=2, pos 0, body takes aa, ends 2 == cursor -> (2,3). Result [2-3]; oracle has [1-2][2-3]. Same shape loses (2,3) on `ababa`. Correct body (greedy, with frame) would backtrack to one iteration and end at the cursor.
W3 (`(?<=(a|ab)(b|))x`): alternations, no quantifier, so not affected by the sabotage. Checked the other rows by hand: W2 `a{1,2}` on `abx` (nomatch either way), W4 `ab?` on `acx` (b? same greedy/possessive), W5 `(a{1,3})` on `aaaca` (candidate length 1 matches without needing shorter body), W7 `a{1,2}` from 2 (body consumes exactly to cursor), W1/W6/W8-W10 no tail-backtrack dependence. No witness W1-W10 reaches a tail quantifier that must give back, so the sabotage stays green (by hand execution; I did not run the witnesses against a build, none exists).
Verdict: HOLDS (suspected-coverage gap confirmed by hand-execution; W3 does not catch it)

VERIFY COMPLETE
