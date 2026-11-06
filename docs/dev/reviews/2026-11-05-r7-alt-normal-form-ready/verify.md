# crit-altnf3 verifier (crit-verify) — independent re-runs
All pcrec compiles `nice -n 19 timeout 60 W/build/pcrec --features all ... -p rx -o verify/x.c`, stamps read as `grep` of the `#define`s in x.c. W = worktrees/crit-altnf3, R = scratch/crit-altnf3, S = R/subject_alt_normal_form.md.

## SND-1
**HOLDS** (real; distinct from RDY-1).
- Code, W/src/gen/emit_vm.c: `case A_WCLASS:` arm at :4091-4092 is reached only for a class in a raw slot; the A_ALT walk (:4114-4119) and A_CAT walk (:4137-4146) step `t = pcrec_ast_seethru(t->l)`; `pcrec_ast_seethru` (src/core/internal.h:2322-2326) is `while (a->k == A_WCLASS) a = a->l`. So a class at a spine head is replaced by its byte child before the arm is seen. After the merge the child is `CAT(c3, [a0 a9])`, which unrolls into the CAT spine and hits `vm_isl_single` on a 2-member class -> decline.
- Measured (utf8 `--engine=vm -fno-cls-kit`, today): `x(?:[éà]1|q2|r3)y` ISLANDS 1; `x(?:[éà]|q2|r3)y` 1; `x(?:q2|[éà]|r3)y` 1; `x(?:1[éà]|q2|r3)y` 1; `x(?:[éè]1|q2|r3)y` 0; `x(?:1[éè]|q2|r3)y` 0.
- Byte-spelled controls (`-e byte --engine=vm -fno-altcls-merge -fno-altcls-factor`): `x(?:\xc3\xa01|\xc3\xa91|q2|r3)y` 1; merged spelling `x(?:\xc3[\xa0\xa9]1|q2|r3)y` 0. Matches the critic's numbers exactly.
- Consequence for S-i/S-i2 (S l.924-934 area): witness has the class at a CAT head, so the walk never enters the set arm; S-i2 is 0 today and stays 0 under any sabotage of that arm. Critic's replacement `x(?:1[éà]|q2|r3)y` does reach the arm (raw `t->r` slot; today 1). Caveat: the controls are byte SPELLINGS of the merged child, not the stage-1 build itself (not built); the code reading is what makes the claim.

## RDY-1
**HOLDS** (real; a different mechanism from SND-1).
- Mechanism: `vm_isl_build` is called only from `vm_alt`/the A_ALT sites on an A_ALT node (emit_vm.c:2748, 3405, 4761; `wl.n < VM_ISL_MIN_BRANCHES` return at :4306). A bare `[éÉ]` today has an ALT as its byte child, so the child is an island. After the merge the child is one CAT box; there is no ALT left to hand to `vm_isl_build`, so the set-reading arm (which only governs an ENCLOSING alternation) cannot restore it.
- Measured today (utf8, vm, -fno-cls-kit): `a[éÉ]b` 1; `(?i)aéb` 1; `(?i)xé+y` ISLANDS 2 RUNGS 0x4u.
- Byte controls (`-e byte --engine=vm -fno-altcls-merge -fno-altcls-factor`): `a(?:\xc3\xa9|\xc3\x89)b` 1 vs merged `a\xc3[\x89\xa9]b` 0; `x(?:\xc3\xa9|\xc3\x89)+y` ISLANDS 2 RUNGS 0x4u vs `x\xc3[\x89\xa9]+y` ISLANDS 0 RUNGS 0x1u.
- So S l.865 ("VM islands: never") and U4's equality (l.907-910) are red on a correct build for these shapes. Distinct from SND-1 (that is a class INSIDE an enclosing alternation at a spine head); the two fixes differ (SND-1: island-local spine walk; RDY-1: state the predicted mover, there is no ALT to read a set from).

## SND-2
**HOLDS.** Hand-execution of S §3.3 (l.311-336) on `(?:abx|aby|abz)q`: step M, w=3, p=2 first: all three share key `ab`; `aby` reaches head `abx` (nothing between) and folds; `abz` folds into `ab[xy]` -> single branch `ab[xyz]`. Step P: no run of 2 branches. Step S: none. Round changes nothing -> stop. Result `ab[xyz]q`, rule-P/S factorings 0 (the predicted `FACTORED 1`, S l.1109-1111, is the TODAY value: I measured today `MERGES 0 FACTORED 1`). So the predicted narration (P then M on rests) is the order the procedure rejects. "Rests not re-run" sabotage cannot change any stamp on this witness: S-m (S l.1147-1149) is dead as written.
- Critic's live witness `(?:ab\b|ad\b)`: `\b` is not a class node, so M does not fold (not fixed-position set sequences); P: equal first position `a`, key `a` -> `a(?:b\b|d\b)`; rests run: S sees run `b\b`,`d\b` with common tail `\b` -> `(?:b|d)\b`; M on heads `b`,`d` -> `[bd]` -> `a[bd]\b`. Correct build MERGES 1; with rests not re-run P's output `a(?:b\b|d\b)` stays, MERGES 0. HOLDS as a live witness (today's stamps for it: MERGES 0 FACTORED 1). Not built, hand-executed only.
- Also noted: the re-run rule (step 4) re-runs on L only, not inside nested nodes, so "rests not re-run" is exactly the recursion into P's rests list.

## RDY-2
**PARTLY.** The unit gap is real; the claim "S-m still fails its sabotage" is REFUTED for the stated witness.
- Real: S l.1095-1096 says MERGES "counts rule-M folds"; today's stamp counts alternation RUNS (verified: `x(?:a|b|c)y` MERGES 1; `x(?:a|b|cd|e|f)y` MERGES 2; match_api.md :2897 "alternation runs merged into one class"). `abx|aby|abz` is two folds, one run: predicted `MERGES 1` fits only the per-alternation reading.
- Refuted part: RDY-2 says S-m's sabotage (0) vs correct count differs. By SND-2's trace (which I redid from the text), M folds before P exists, so the "rests not re-run" sabotage changes nothing on `(?:abx|aby|abz)q` in either unit reading. SND-2 is right; RDY-2's S-m survival claim is wrong. RDY-2's FACTORED value is also wrong for the same reason (0, not 1).

## RDY-3
**HOLDS.**
- `scripts/emit_sweep.py` docstring :35-41: stream 5 is "registry dumps: the seven `--list-*` surfaces, whole-file byte comparison ... Always identity-required"; :1462 lists `--list-axes` among them; `--dumps-declared-rows` exists (:3133), the mechanism the fix names.
- `src/dump/axes_dump.c:629-631` (altcls-merge row 1): "a maximal run of single-character alternation branches qualifies (runs before either engine is built)". S l.791-793 and §11 (l.1359-1363) re-specify bit 10 at stage 1 and require "its `--list-axes` text ... in the stage that moves it" (D80). B0 part 1 (S l.831-836) runs `--streams ...,dumps` identity-required with no declared row. So a correct stage 1 either leaves false text (§11 broken) or turns the dumps stream red. Nothing built; this is a reading of the two texts, both quoted.

## RDY-4
**HOLDS.**
- `git log --oneline 64ab880aa` subject lines: last span_pick landing is 1d (`39e7b20c5 Merge lane/memfn-sp1d: span_pick stage 1 unit 1d ...`, `b04160586 journal: span_pick 1d landed`); earlier 1c/1b/1g/1f merges (`509c94908`, `cb24c5aa5`, `94f37cfd5`, `a33ca7b0a`). No subject names 1e. `memfn/docs/wake.md` (section "After 1d merges"): "Cut 1e (the phase-2 tables; it reads T-VERIFY's step list) from main" = not yet cut at the freeze.
- `docs/design/memfn/span_pick.md` 1e (the unit row, l.365): "T-FRAME (legacy first) at text time; T-FIND as ONE walk with the asker fact ...; the renderer row (B-fn/B-pair ...); compose `arms[]` and `fd_find`'s text become renderers ...; no MF_SITE_ABI event"; readers (l.377): "a DECLARED `wfD` -> `fd` row map: rows.tsv, row_floors.tsv, rows_check.py ..., the MFTRACE names"; witness "REACH EQUALITY through that map". `grep -n emit_dfa span_pick.md` finds no emit_dfa window-walk rewrite attached to 1e (hits are in the rev-notes, l.50, 92, 137, 185, 426-448, none in the 1e rows).
- S §4.7 (l.740-745) claims "1e rewrites the window walk in `emit_dfa.c`, where most §4.2 reader rows live". Not supported by span_pick.md. The real fence (REACH EQUALITY across 1e's window) is as the critic says.

## RDY-5
**HOLDS** (by code and text; nothing built).
- `src/facts/req.c:650-662` (`case A_REP`): "At `rmin >= 1` the body's BEST run survives and its head and tail do NOT" and `rb_rep_into` (:538) keeps only the best run. S §3.5 arm table (l.487-489): REP{m,n} head/tail "[REPEAT-RUN] (later)", positive LOOKAROUND "[REQ-LOOKAROUND] (later)". Measured `--emit-facts` utf8: `ax+` req_whole_run empty (none); `zax+qq` req_run `7171@1` (the `za` before the repeat is not joined with the body).
- S-h's control `(?:ab|ax+|ad)` is described (S l.1144-1146) as head `a x`, length 2, "passes row 1". With today's arms the head is `a` (h=1): row 1 cannot pass (only p=0, `a` meets `a`), row 3 refuses. Answer unaffected, mechanism text false. The second horn (a REP head arm in the shared module moves runs, contradicting "TREE-level, not runs", l.1105) follows from S l.511-516 making the run walk a reader of the module.

## SND-3
**PARTLY.** Answer consequences reproduce; the premise ("the text permits that reading") is weaker than stated.
- libpcre2 (probe.py, byte): `(?:x\Kac|xab)` on `xac` = (1,3); `xa(?:c|b)` = (0,3); `x(?:\Kac|ab)` = (1,3); `(?:x(?=ab)ac|xab)` on `xac` = nomatch, `xa(?:c|b)` (0,3). So a P that drops `\K` or crosses a lookahead is wrong, as claimed (pcrec agreed on all).
- But S §3.3 step 1 (l.318) defines mergeable branches as "fixed-position set sequences (each position one class node; effect-free by construction)" and step 2 (l.335-338) says the key is "each a class node". `\K` and a lookahead are not class nodes, so the literal text already ends the key before them. Only §3.5's "head read through zero-width nodes" (for the adjacency test) can be mis-borrowed. So: a one-sentence disambiguation is worthwhile; an answer risk exists only for a lane that ignores "class node".

## SND-4
**PARTLY / latent.** libpcre2: `(?:ab|(?=ad)a|ad)` on `ad` = (0,1); the merged `(?:a[bd]|(?=ad)a)` = (0,2). Real, but only when the positive-LOOKAROUND arm (S l.489, "[REQ-LOOKAROUND] (later)") exists and row 2 reads group width; not reachable in stages 1/2p/2b as scheduled. The fix (row 2 reads CONSUMED width) is a cheap text change. Lookbehind offset sub-claim not run.

## SND-5
**HOLDS** (libpcre2 half measured; pcrec half not re-run).
- Spec: `docs/spec/match_api.md:3961` §11.6¶1: a PURE callee gets "the pattern's BACKTRACKING-ORDER answer ... every fire on every tried path honoured"; §11.5¶1 (:3950): a callee's give-up propagates unchanged.
- libpcre2 10.46, callee returning -50 on every fire (`verify/giveup.py`): `(?:ab|(?C1)x|ad)` on `ad` -> rc -50, fires 1; merged-style `(?:a[bd]|(?C1)x)` -> (0,2), fires 0. `(?:ab|a(?C1)x|ad)` -> rc -50 fires 1; `(?:a[bd]|a(?C1)x)` -> (0,2) fires 0. So S §3.2 l.255-262 "the spans agree on every P3 row" holds only for pass/fail returns. pcrec's own behaviour with a give-up callee: not verified (needs a callee driver).

## RDY-6
**PARTLY.** The ambiguity is real but narrower than stated. S §3.5 l.508-512 says a position is "a 256-bit byte set ... D187's position form", which reads as the exact union set, and §3.4 l.435 says "a hull per width" for equal-width merging; what is missing is how a piece position is RENDERED (set list vs val/mask) and the EMPTY arm choice. Arithmetic: byte set {85,99,b9} has val/mask hull mask 0xc3 = 16 members; {cd,ce} hull mask 0xfc = 4 members, so cube hull and exact set differ for iota's width-2 group. EMPTY: S l.484 (unit, stage 2a) vs l.1033-1034 (2p keeps today's single-run rules); not reconciled in the text. Not run beyond arithmetic.

## RDY-7
**HOLDS.** S stage 2p block (l.1026-1070): gates are the piece-list model (l.1060-1063) and the S-p fact witness; `grep B0|emit_sweep|identity` over those lines finds only the `--dumps-declared-rows` clause (l.1057). S §5 preamble (l.770-775) gives `make test`/`make strict`/`make test-axes` (answer identity). 2p claims "no pcrec artifact moves" (l.1029-1030) with no instrument that sees a moved `RX_REQ_RUN` or table that keeps answers. Reading only.

## RDY-10
**HOLDS** (text). S §3.3 steps 2-3 (l.324-333) say "maximal runs" with no minimum; a run of one branch equals its key and becomes `K(?:)`, adding an empty and removing no position, so the re-run rule (step 4) could loop and the termination sentence (l.341-342, "every rule strictly lowers the number of position occurrences") is false for it. Obvious intended reading is runs of at least two; the text should say so. Not executed.

## SIM-1
**HOLDS.** Hand-execution of §3.3 M on `bba|bb|bba|bb`: w=2: second `bb` (slot 4) must pass the test against `bba` (slot 3) -> row 1 no disjoint position (b/b, b/b), row 2 width 3 != 2 -> row 3 refuse, so the copy reaches no head and becomes one; same for the second `bba` against `bb`. M leaves 4 branches. P: all start `b`, key `bb` -> `bb(?:a||a|)` (duplicate arm, two empties). Oracle (probe.py, 5 subjects): `(?:bba|bb|bba|bb)c?` == `bb(?:a||a|)c?` == `(?:bba|bb)c?` on all (answers identical; pcre2 = pcrec). So size/quality only, not an answer bug. (Random-grid counts 1335/6000 not re-run.)

## SIM-2
**HOLDS** (as a design gap, not unsoundness). S §3.2 l.201-202 ("prefix and suffix factoring ... reorder nothing"); P/S act on CONSECUTIVE branches only. Hand-execution on `frank|xyz|fred`: M no folds (different widths/keys), P: runs by first position f / x / f are not consecutive-equal, S none -> unchanged; pcrec today agrees (`RX_ALTCLS_FACTORED 0` for `frank|xyz|fred`, `1` for `frank|fred`). The 1286/6000 grid counts not re-run.

## SIM-3
**HOLDS.** My own implementation of M's walk counting adjacency calls (`verify/cost.py`, mixed widths 3-7, alphabet 10): n=200/400/800 -> 994 / 5327 / 35719 calls (per branch 5.0 / 13.3 / 44.6): quadratic growth, same shape as the critic's (1294/4937/36857, different tie rules). S l.358-367's O(1) path covers same-width writer-free spans only (the text says so); mixed-width word lists are the case outside it. "Computed once per round" vs slot shifts after each fold: reading only.

## FIX-n
`R/fixind/` contains only DELIVER, no findings.md: nothing to verify.


## FIX-1
Duplicates RDY-5 (verified above: `req.c:650-662` REP keeps no head; S §3.5 l.487-489 stages the arm "later"; S-h control text false as written).

## FIX-2
**HOLDS** (citation drift: the soundness sentence is at `req.c:59`, not :47-52).
- W `req.c:59`: "deliberately not descended into: a LOOKBEHIND's bytes sit BEFORE the ..."; `req.c:698-716`: `case A_EMPTY, A_EOL, A_CTX, A_GSTART, A_KRESET, A_LOOK ... A_BREF, A_VAR, A_CALLOUT:` -> `rb_row_into(acc, a); return;` (a cut). `req.c:628-637`: `A_CAP`/`A_ATOMIC`/`A_WCLASS` transparent, no WRITES notion.
- Subject l.522-530: columns "the head/tail affixes and min/max width; and WRITES (... a lookaround's body included)"; "The head is read through zero-width nodes for the adjacency test ...; the run reader keeps cutting at ZERO kinds". One head column is named, with two opposite rules at A_LOOK/A_KRESET/A_CTX. Real text gap; the leak sabotage witness is not in S-p/S-d/S-w/S-h/S-k (S l.1128-1147, 1062). Callout per-node row point (`internal.h:1290-1300`) not re-read.

## FIX-3
**HOLDS** (text gap).
- W `req.c:96-102`: "maximum width in BYTES (`RbRuns.maxw` ...)... It is NOT `pcrec_cwmax`, which counts characters: on the lowered tree a `(?i)s` under utf8 is up to two bytes (U+017F)" (the "deletes matches" clause is on the next lines). `src/facts/CLAUDE.md:7`: "Known wrong-way edge: `facts -> opt` call-level back-edge (`pcrec_minw`/`pcrec_cwmax` in `src/opt/mrl.c` ...)". `internal.h:2036-2060`: "a walker may legitimately run BEFORE the fixpoint does ... EVERY ONE IS WRITTEN SO THE ARENA'S ZERO IS THE SOUND ANSWER".
- Subject l.507-512 / 526: "a position is a set over the level's alphabet", "min/max width", no statement of the unit (characters vs bytes) per level and none on reuse of mrl.c. Pass order cites hold (`compile.c` altcls before callgraph).

## FIX-4
**HOLDS** (doc). W `src/facts/CLAUDE.md:7`: "A derivation depends on the sealed IR, node-grain pure functions ...". Subject l.509 puts the module "under `src/facts/`" and l.513 calls it from altcls "before the call graph" (E1 seals after `pcrec_callgraph_build`), so the carve-out is unstated. The interface-shape point (combinators vs whole-subtree call, req.c's iterative spine walk) is also unstated in §3.5; consistent with S l.1031-1034 "one walk, no parallel copy". Not built.

## FIX-5
**HOLDS.**
- W `lib/pcrec.h:194-227`: "D46's controllability half for the ALTERNATION->CLASS NORMALIZATION pass (... src/opt/altcls.c)", "stage 1 (single-char runs -> one class)", "What the pass DID is recorded in `<PREFIX>_ALTCLS_MERGES`". `src/dump/axes_dump.c:625-631`: "a maximal run of single-character alternation branches qualifies (runs before either engine is built)". `internal.h:3510-3520`: "Zero under `-fno-altcls-merge` ... by construction"; `lib/CLAUDE.md:12` lists the deny family as masked-out of `rx_info.flags` (the cited "asserted by the artifact stamp" wording is on the neighbouring lines, not re-quoted).
- Subject: stage 1 names only `tuning.md` §2.6 hunks (via §11 l.1359); the `pcrec.h` bit-name hunks are listed under stage 2b (l.1088-1093), not stage 1; `grep axes_dump` in S finds nothing. §11 l.1376 promises the `--list-axes` and stamp text "in the stage that moves it". Whether the lowering's folds count in `ALTCLS_MERGES` is unstated at stage 1 (same as RDY-2).

## FIX-6
**HOLDS.**
- W `cli/main.c:3108-3111`: `pcrec_emit_facts(pattern, &opt, &pin, encs, nenc, &err)`; `main.c:2866-2878`: `pin` initializer has `.bound .callout_decls ... .code_headers` and no `.harness`; `main.c:3451-3453`: `PcrecEmitIn cin = pin; cin.harness = hopt;` only on the compile path. `src/facts/facts.c:203`: `pcrec_opt_has(cx->opt, PCREC_NO_REQ_RUN_FOLD) ? 1 : ...` (no harness read anywhere in `src/facts/*.c`: grep empty). `--harness=pres-window` etc. at main.c:1428-1439 are emission-side.
- Subject l.990-995 and l.1361: the 2a lever "restores today's ALT outcome and today's EMPTY cut" in the run, a fact. So `build/pcrec-harness --harness=<lever> --emit-facts` would list the default fact, and S-c must be stated on emitted artifacts. Not built.

## FIX-7
**PARTLY.** Text-unstated items hold by reading S: no member/interval bound on the description's code-point position (§3.3 l.313 "sets compared by equality"; SIM-5 bound counts branches/positions, l.358-367, as SIM-3 showed); 2p's EMPTY arm meaning (S l.484 vs l.1031-1034; same gap as RDY-6); WRITES for A_CALL unstated (S l.1031 row 3 refuses A_CALL anyway). The island-predicate budget item is SUSPECTED by the critic itself and I did not read `vm_isl_single`'s counter: not verified.

VERIFY COMPLETE
