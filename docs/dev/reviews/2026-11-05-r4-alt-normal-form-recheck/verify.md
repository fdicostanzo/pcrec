# altnf2 verify (sonnet verifier). Compiles/probes run: see per-section counts.

## Verdicts

### SND-1
Verdict: HOLDS (answer moves under the merged forms the adjacency test would allow; pcrec and libpcre2 agree with each other).
Commands: `python3 -I cmp.py $W/build/pcrec snd1.tsv` (utf8-free, byte; libpcre2 10.46 vs pcrec --emit-main), cases in verify/snd1.tsv, snd1b.tsv:
- `(?:ab|a\Kd|ad)` on `ad`: pcre2=(1,2) pcrec=(1,2); merged `(?:a[bd]|a\Kd)`: pcre2=(0,2) pcrec=(0,2).
- `(?:ab|(a)d|ad)\1?` on `ada`: pcre2=(0,3)[(0,1)] pcrec=(0,3); merged `(?:a[bd]|(a)d)\1?`: pcre2=(0,2) pcrec=(0,2).
- `(?:ab|(a)d|ad)` on `ad`: group 1 (0,1); `(?:a[bd]|(a)d)`: no group 1 (pcre2=(0,2) no caps).
Caveat: the note's rule is only a text hazard (nothing is built); the merged forms are the ones the §3.2 equal-width shortcut would permit. Exit codes of pcrec compiles were 0 (cmp.py raises otherwise).

### SND-2 = FIX-2
Verdict: HOLDS.
Commands (each `$W/build/pcrec -e utf8 --engine=vm -fno-cls-kit -p rx --emit-main -o s2.c --pattern P`, then grep stamp; compiler exit 0 each):
- `x(?:[éà]1|q2|r3)y`: `#define RX_VM_ALT_ISLANDS 1`
- `x(?:[éè]1|q2|r3)y`: `#define RX_VM_ALT_ISLANDS 0`
- `x(?:[\x{100}-\x{17f}]1|q2|r3)y`: `#define RX_VM_ALT_ISLANDS 0`
Source: emit_vm.c:4011 `vm_isl_single` returns -1 unless A_CLASS, then `pcrec_cls_single(v->cx, a)` (exactly-one test); :4091-4092 `case A_WCLASS: return vm_isl_words(v, a->l, ...)` is transparent; :4098-4100 `case A_CLASS: b = vm_isl_single(v,a); if (b < 0) return false;`. A range box (multi-member A_CLASS) is declined today; the "read a set position as its members" sentence would admit it. Mover is real.

### SND-3
Verdict: HOLDS.
Commands: `$W/build/pcrec -e utf8 --emit-facts --pattern '(?i)xyzłw'` (exit 0): `utf8 req_whole_run ... 58595ac5/dfdfdfff` and `req_run ... 58595ac5@3/dfdfdfff`. Python arithmetic: Ł=c581, ł=c582, xor 0x03 (non-cube); bound-2 set run = 3*7 (xyz) + 8 (c5) + info{81,82}=8-ceil(log2 2)=7 + 7 (w) = 43; sabotaged (82 dropped) = 21+8+8+7 = 44. Answer: cmp.py (libpcre2 vs pcrec) `(?i)xyzłw` on `xyz\xc5\x82w` and `xyz\xc5\x81w`: both pcre2=(0,6) pcrec=(0,6). The sabotaged pre-check rejecting 82 is inferred from the arithmetic, not built (no mech run allowed).

### SND-4
Verdict: HOLDS.
Commands: libpcre2 via cmp.py's p2 (captures printed), plus cmp.py rows in verify/snd4.tsv:
- `(?:a(x)|b(x))` on `bx`: pcre2=(0,2)[- (1,2)] (group 2 set, group 1 unset); pcrec=(0,2).
- `(?:a|b)(x)` on `bx`: pcre2=(0,2)[(1,2)] (group 1).
- with `\2`: `(?:a(x)|b(x))\2` on `bxx` OK (0,3); `(?:a|b)(x)\2` pcre2=ERR115, pcrec: `\2 refers to capture group 2, but this pattern has 1`.

### SND-5
Verdict: HOLDS (shape CONFIRMED; the build-time consequence stays SUSPECTED, nothing is built). Needs `--features all` (default features refuse lookbehind: "(?<...) requires module 'lookaround'").
Commands: `pcrec --features all -p rx --emit-main` exit 0 for `(?<=ab|a)x`, `(?<=xab|xc)y`, `(?<=aab|a(b))x`; exit 1 "variable-length lookbehind is not implemented: every alternative of a lookbehind must have a fixed length" for `(?<=a(?:b|))x`, `(?<=x(?:ab|c))y`, `(?<=a(?:ab|(b)))x`. cmp.py (verify/snd5.tsv): originals pcre2==pcrec ((1,2), (2,3), (2,3)); factored forms pcre2 accepts with (1,2), (2,3), (2,3)[(1,2)], pcrec CERR.
Source altcls.c:440-458: "THE BODY IS NOT WALKED EITHER ... Normalising an alternation INSIDE a lookaround body would be sound ... and is declined ... no producer exists" ... `case A_LOOK:` leaf arm.

### FIX-1 = RDY-1
Verdict: HOLDS.
Quoted at $W (569c57d3a): internal.h:2480-2481 `#pragma GCC diagnostic push` / `error "-Wswitch"` wrap ONLY `pcrec_kind_row(AKind k)`'s `switch (k)` (to :2492 `pop`); the TEXT-column readers are `switch (...text)` with no `default:` at req.c:581-584, startset.c:82-85, nfa.c:596-610, mrl.c:486-489 (plain -Wswitch warning only; Makefile:25 `WARN = -Wall -Wextra`, -Werror not default) and three `==` tests: possessify.c:446 `pcrec_ast_row(a).text == KTEXT_ZERO ? fst_empty(true)`, :501 `if (row.text == KTEXT_ZERO) return fst_empty(true);`, :924 `if (row.text == KTEXT_ZERO) return gk_parts_empty(true);`. The note's §3.6 line 329: "The row is `-Wswitch`-complete, so a missed reader is a compile error." -> false for a new TEXT value (grep `KTEXT_` over src/ shows exactly these sites; KTEXT_ readers outside internal.h: req.c, startset.c, nfa.c, mrl.c, possessify.c). Not built, so the "silent decline" consequence is by reading.

### FIX-3 = RDY-7 (+RDY-5)
Verdict: PARTLY. The conclusion (hard trigger crossed) HOLDS under either count; the two critics' counts are each half right.
Count: `grep -o 'PCREC_BIT([0-9]*)' lib/pcrec.h | sed 's/[^0-9]//g' | sort -nu`: 57 distinct values, 0-54, 56, 57 (bit 55 absent). pcrec.h:1196 says "Bit 55 is the kit's (`-fno-kit-size-drop`, R17-b)" (reserved, defined elsewhere/not in pcrec.h; `git grep BIT(55)` finds nothing else). So 57 defined + bit 55 reserved by the kit = 58 of 64 used (FIX's 58/6 free is right; RDY's "55 free, 7 free" counts the kit's reserved bit as free). Frozen plan.md @569c57d3a line 1282, [IFACE-PUSH]: "HARD TRIGGER added 2026-10-10 by Frank, session 105: the push opens when <= 4 flag bits remain in the 64-bit `flags` word (55 of 64 used after [START-LANDING])". Four new public bits: 6 free -> 2 (RDY: 7 -> 3), either way <=4 reached by the 2nd (6 free) or 3rd (7 free) new bit. Note §11 (f7fd1a759 lines ~836-839): "Stage 1 can make a pick slower (a choice cell), so it gets a public deny; 2a, 2b and 3 likewise; 2p has none while inert. Spelled at build." No mention of the bit budget or [IFACE-PUSH]/[FLAG-ACCESS].
tuning.md (at $W): §2.6¶1 "Denies stage 1 of the alternation-to-class pass ... merging a maximal run of single-character alternation branches into one class"; §2.7¶1 "Denies stage 2 ... prefix-factoring a maximal run of branches that share a literal first byte"; bits 10, 11 (table rows :117-118). §2.6¶2: "Its denial moves the refusal set" (K45). RDY-5's claim that the two existing flags' text becomes false under stage 2b is textually correct; the note names no remap.

### FIX-4 = RDY-2
Verdict: HOLDS.
Quoted at $W/scripts/emit_sweep.py: help :212-213 `--bases LIST  the bases each variant runs at (default byte,utf8); facts and dumps run at the first only.`; `bases` is read only in `run_variants` (def :2042, call :3400, which :3216-3221 requires `--ref` AND `--tree-rev`: "--variant builds BOTH sides ... needs --ref and --tree-rev") and `run_data_census` (:2903); :3227-3229 only validates it. Stream 6, :1073-1076 `compile_stream_facts`: docstring "the facts listing for BOTH encodings in one call", argv `[pcrec_bin, "--features", "all", "--emit-facts=byte,utf8"]`; header :44-48 "Both encodings in one call, so `--extra` never reaches it. Identity-required." Note line 526: "`scripts/emit_sweep.py --ref BASE --bases byte` (its pinned streams ...". Earlier today's measure: `pcrec -e utf8 --emit-facts --pattern '(?i)xyzłw'` lists utf8 req_whole_run etc., so a correct stage 1 moves stream 6's utf8 half. Not executed (the sweep is a suite; not run).

### FIX-5
Verdict: HOLDS.
Own python3 script (hull K = AND of ~(a^b), T = first member & K; info(S) = 8-ceil(log2 |S|)): 
- Kelvin {4b,6b,e2}: info 6, hull popcount 4, hull members 16
- long s {53,73,c5}: info 6, hull popcount 3, hull members 32
- beta 2nd byte {92,b2,90}: info 6, hull popcount 6, hull members 4
- sigma 2nd byte {a3,83,82}: info 6, hull popcount 6, 4 members.
(?i)s utf8 does include c5: `pcrec -e utf8 --emit-facts --pattern '(?i)s'` start_set `3:0000..08..08..20..` decodes to members 0x53, 0x73, 0xc5 (exit 0); cmp.py `(?i)s` on `c5 bf` pcre2=(0,2) pcrec=(0,2) (ſ = c5 bf; lower/upper/fold of ſ = 73/53/c5bf). limits.def:410 PCREC_MIN_REQ_RUN_BITS "the sum over its positions of popcount(K)" (RULED); :411 PCREC_MAX_REQ_RUN_POS_SET "the largest member set one position ... may have" (does not say |S| vs hull). Three {53,73,c5} positions: 3*6 = 18 (>= 16) by info(S) vs 3*3 = 9 by hull popcount.

### FIX-6
Verdict: HOLDS.
Commands (compiler exit 0 each): `$W/build/pcrec -p rx --emit-main -o f6.c --pattern '(?:abx|aby|abz)q'` -> `#define RX_ALTCLS_MERGES 0`, `#define RX_ALTCLS_FACTORED 1`. `--engine=vm --emit-ir` program: `L0 consume 'a'`, `L2 consume 'b'`, then `L3 alternation entry (3 branches)` over `consume 'x'|'y'|'z'` then `consume 'q'`: the 2-byte prefix `ab` is already factored once (events 28 vs 30 under `-fno-altcls-factor`). Source altcls.c:200-209: `altcls_extend_prefix` "Grows a group's shared literal prefix ITERATIVELY as far as every one of the `n` members keeps agreeing on the next byte ... prefix LENGTH is pattern-shaped"; :255-262 `altcls_factor_run` splits into "maximal ADJACENT runs sharing a first literal byte" (only the GROUPING keys on byte 0). Note lines 113/127/210/652/660 call it a "one-byte key"/"key widened". tuning.md §2.7¶1 and the claim that no stamp counts suffix factoring: RX_ALTCLS_FACTORED defined as prefix factoring only (§2.7¶1 text "prefix-factoring"); not separately re-run.

### FIX-7
Verdict: HOLDS (text contradiction and pass order confirmed; whether the build resolves it by a two-level description is a design choice).
Pass order at $W/src/core/compile.c: :2819 `root = pcrec_altcls(&cx, root);` ; :2854 `pcrec_callgraph_build(&cx, root);` ; :2962 `root = pcrec_lower_enc(&cx, root);` (altcls 143 lines before the lowering). req.c:107 "THE WALK IS OVER THE LOWERED TREE ..." and :134 "over the LOWERED tree the E2 seal recorded". Note rev 1: §3.5 (line 297) "built bottom-up over the lowered tree"; line 313 readers "altcls/the owner (the `exact` bit and the fixed-position sequence decide whether a rewrite is legal)"; §3.3 table line 211 "`req.c` | NOT a reader of the owner"; line 846-847 owner "called above the call graph (altcls, code points) and inside the lowering's new subtree (bytes)". So the code-point-level caller runs before any lowered tree exists.

### FIX-10
Verdict: HOLDS.
`population/rpsurvey_evidence/foldsweep.py` (25 lines, read in full): args `WORKTREE FOLD_CLASSES.tsv OUT.tsv`; compiles `(?i)abcd<X>efgh` with `-e utf8 --emit-facts`; writes columns `shape members utf8 pos_hulls whole_positions whole_run`, `n = len(wr.split('/')[0]) // 2`; there is no comparison of n to `8 + width` (grep for "keep"/"8 +" finds nothing but the header). The threshold appears only in rpsurvey_report.md line 26 ("`req_whole_run` position count vs the 8+width a cut-free run would have: 513 ... (24 ASCII + 210 + 279)", 210+279 = 489, matching the note's "24 + 489"). Note §U2 (lines 547-549): "`foldsweep.py` on the stage build: classes keeping the `abcd<X>efgh` run = 766 EXACTLY (24 + 489 + 253, predicted from CaseFolding.txt by `shapes2.py`)". Script not run (it needs FOLD_CLASSES.tsv + a ~1454-compile loop).

### RDY-3
Verdict: HOLDS for the measurements and the reader; PARTLY for the consequence (the stage-1 tree was not built; the byte spelling is a stand-in).
Commands (compiler exit 0 each; grep stamps): `-e utf8 --engine=vm -p rx --emit-main --pattern '(?i)xé+y'`: default `RX_VM_RUNGS 0x4u`, `RX_VM_PROGRAM_BYTES 1877ULL`; with `-fno-cls-kit`: `0x4u`, `3319ULL`; `-e byte --engine=vm --pattern 'x(?:\xc3[\xa9\x89])+y'`: `RX_VM_RUNGS 0x1u`, `1078ULL`. Source emit_vm.c:1885-1928 `vm_det_seq`: `case A_WCLASS: return vm_det_seq(cx, a->l, out, cap);` (descends to the child; the comment says the cursor rung "takes it on ANY quantifier body"), `A_CLASS` returns 1 byte, `A_CAT` sums, and `case A_ALT: case A_EMPTY: ...` are declined. So today a multi-box class (an A_ALT of boxes) declines, a merged single `c3 [a9 89]` is a CAT of two classes and would be accepted. Rung flip by stage 1 is a reasoned inference (0x4 -> 0x1 between today's tree and its byte spelling).

### RDY-4
Verdict: PARTLY. Frozen decisions.md @569c57d3a:9846-9850 "D168 addendum 3 -- `\A`/`\z` fold at both layers, staged": its Ruling/Why/Cost rule the A_CTX fold and "P2e is a second abi event with its own mover census"; it says nothing in general about what keys the abi (RDY-4's literal claim HOLDS). But the "D168 addendum 3 note -- P2e built" (line 9858) says: "The heavy chain measured ZERO emitted-byte movers ... so there is no abi event per D76/D94: abi stays 81, and D168 add. 3's 'own abi event' was conditional on movers" -- so addendum 3 (via that note) is an instance of the movers-key-the-abi reading, not its source. Note line 478 (f7fd1a759) "the ruled reading (D168 add. 3) keys the abi on emitted text" over-credits it; D76/D94 and match_api.md §6¶18-19 are the rulings. Doc-only.

### RDY-6
Verdict: (a) HOLDS; (b) the arithmetic HOLDS, the "not separable" conclusion is a reading of the note (SUSPECTED, not tested).
(a) tests/codegen/run_facts_checks.sh lines 34-49: "3. COMPLETENESS -- one `facts` row per `facts.def` row per encoding ... PLAIN-TEXT row count (`PF_FACT(` line markers)"; "4. WHY-TRUTHFULNESS -- for every DENY flag `src/core/axes.def` spells, a compile under that flag lists `deny:<flag>` on EXACTLY the facts `docs/spec/tuning.md`'s 'Facts emptied' line for that flag names". tuning.md:662 §2.27¶5 `Facts emptied ... req_set, req_set_maxoff, req_whole_run, req_run, req_byte` (the run-derived facts' line, so a new run-derived fact must be added there).
(b) CaseFolding 16.0.0: `0421; C; 0441`, `1C83; C; 0441`. UTF-8: с U+0441 = d1 81; С U+0421 = d0 a1; U+1C83 = e1 b2 83. d1 81 vs d0 a1 differ at BOTH bytes (so the two width-2 branches are not a one-position merge). cmp.py `(?i)с` (utf8): on `d0 a1` pcre2=(0,2)=pcrec; on `e1 b2 83` (0,3)=(0,3); on `d0 81`, `d1 a1` both nomatch.

### RDY-8
Verdict: PARTLY. All named rows exist; `grep -n 'SAB_FILE\|SAB_BEFORE' /home/pcrec/projects/pcrec/worktrees/crit-altnf2/tests/mech/sabotages/<row>`: S366 src/gen/emit_vm.c anchor `case A_WCLASS:` (arm); S268 src/facts/req.c `o.head = rn_common_head(w, l.head, r.head);`; S66 src/opt/altcls.c (`PcrecCpSet u;` ...); S67 src/gen/emit_dfa.c (`PCREC_FORCE_UTF_CHECK;` ...); S451 src/facts/req.c `int k = rn_hull_mask(a.bytes[o.n], a.mask[o.n], b.bytes[o.n], b.mask[o.n]);`; S302 and S303 src/opt/lower_enc.c (`if (repl) *slot = repl;`, `res = seal;`); S-U3 src/core/fold.c; S-U7/S-U8 src/opt/lower_enc.c; S1653 src/facts/req.c `case KTEXT_ANY:  rb_gap_into(acc, PCREC_W_UNBOUNDED); return;` (+ startset.c SAB_FILE2). Correction: S1638/S1640 anchor `KIND_ROW(A_LOOK, ZERO, GATE, NONE, NFA_ERASED_LOOK)`, S1639 `KIND_ROW(A_VAR, ANY, OPAQUE, NONE, 0)`, S1641 `KIND_ROW(A_BREF, ANY, OPAQUE, REFS, 0)` -- rows of OTHER kinds than A_EMPTY, so they only break if the row's column set/spelling changes (a fifth field or a value rename would; a new KTEXT_UNIT value on A_EMPTY alone would not move these anchors). "Whether a stage's edit removes an anchor" is a build-time fact, not tested (nothing built). The note's $5 REACH demand is for new mech rows only: not re-quoted here.

### SIM-1
Verdict: PARTLY. My own model (verify/sim1.py; python3 -I; equal-width literal lists as per-position sets; the table = first-match per adjacent pair of (2) shared first position -> prefix-factor the maximal run and recurse on the rests, (3) shared last position -> suffix-factor, (4) differ at exactly one position -> merge, repeated to a fixpoint; the strategy = position-major, last position first, hashing on the all-but-p key, repeated sweeps):
- `aaa|aab|aba|bba`: table `a(?:a[ab]|ba)|bba` = 3 leaf paths; strategy `aa[ab]|[ab]ba` = 2 branches. REPRODUCES the claim (rule 2 beats rule 4 at the first pair).
- `aab|bbb|bab`: my table reading gives `(?:aa|b[ab])b` (suffix then merge, 2 paths), strategy `aab|b[ab]b` (2). Does NOT reproduce "leaves a legal merge": the result depends on whether rules re-run after a factoring (a one-sweep reading would leave it).
- `ab|ab`: my fixpoint model dedups (X==Y) to `ab`; without that dedup rule the table (2) would factor to `a(?:b|b)`; the note's table has no duplicate rule, so the output is reading-dependent (the claimed `ab(?:|)` is one such reading).
So the existence of divergence (list 1) is confirmed; the table is under-determined (the two other lists show reading-dependence), which supports the finding's core point (name one order) while the exact lists are not all reproduced. Soundness not at issue.

### SIM-3
Verdict: HOLDS for the three mis-listed cells; the three "omitted" cells are confirmed non-ASCII multi-byte but their box counts (71->39 etc.) were not re-measured here except cls-d-ucp (see SIM-4, Nd 71 -> 39 by my own model).
Patterns (bench/utf8/patterns/*.rx) compiled `pcrec --features all -e utf8 -p rx --emit-main` (7 compiles + 4 `--emit-facts`):
- cls-neg-allhigh `[^\x{80}-\x{10FFFF}]+`: exit 0; `--emit-facts`: start_set 128 members, all ASCII bytes (`ffff..ffff 00..00`), width [1,inf) -> ASCII-only, no wide class (listed under the note's `cls-neg-*` glob but not a mover).
- prp-ingreek `\p{InGreek}`: exit 1 "module 'unicode-props' is enabled but \p{...}: this Unicode property is not implemented yet".
- prp-l-anchored `^\p{L}{4}$`: exit 1 "pattern too large: 1559485 bytes of emitted C source (limit 1000000 ...".
- cls-w-ucp `(*UCP)\w+`: exit 1 "UCP \w is a wide set (930 intervals) and is refused under encoding 'utf8' until a kit-sized class route exists".
- cls-d-ucp `(*UCP)\d{4}`: exit 0, width [4,16], start_set 18 lead bytes -> non-ASCII multi-box.
- cls-s-ucp `(*UCP)a\sb`: exit 0, width [3,5] -> non-ASCII, multi-byte.
- ci-class-range `(?i)[a-z]+`: exit 0, start_set 54 bytes (ASCII letters + c5 + e2), width [1,inf): non-ASCII members U+017F, U+212A, each a separate box.
Note line 569: "20 of 76 bench/utf8 patterns (`cls-dot*`, `cls-neg-*`, `prp-*`, `qnt-dot-bounded`, `lit-mixed-ascii`, `ci-neg-fold`)" -- globs; the 20 count itself was not recounted (it depends on which `cls-neg-*`/`prp-*` files exist; 76 files under bench/utf8/patterns not recounted here beyond the 7).

### SIM-4
Verdict: PARTLY. 664 / 67 / 105 / 39 reproduce; the note's "76 vs 66" does not.
Own script verify/sim4.py (python3 -I; unicodedata 16.0.0 = the repo's UCD; UTF-8 range->aligned-box splitter, positions as byte SETS; merge = per-width, for p in order: group boxes identical except at p, union at p; sweeps to a fixpoint; no adjacency test; box counts by my own splitter, not by pcrec's u8_box):
- `Lu`: 651 intervals, 664 boxes before merge; last-position-first: 67 boxes; first-position-first: 105 boxes.
- Over all 24 position-order permutations: counts {67, 68, 81, 82, 90, 91, 104, 105}; neither 76 nor 66 appears.
- `Nd`: 71 intervals/boxes -> 39 under both orders.
So the declared strategy (last-first) is the best of the 24 orders on `\p{Lu}`; the note's "76 vs 66" cannot be reproduced by this model (it may reflect a different box splitter or UCD).

Budget: about 60 single-pattern compiles/probes (pcrec + gcc -O1 in cmp.py), 0 make, 0 suites, 0 sweeps run (emit_sweep.py and foldsweep.py read, not run).

## VERIFY COMPLETE
