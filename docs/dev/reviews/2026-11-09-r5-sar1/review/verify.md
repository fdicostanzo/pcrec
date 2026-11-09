# verify — crit-sar1
## Verdicts

### EMIT-1 — HOLDS (emission re-run; speed re-measured, larger than claimed on my text)
- `--emit-facts 'A{33}x'`: B req_whole_run none, req_byte 120; S req_whole_run = 32 x 41, req_byte 65, RX_REQ_RUN 4141414141414141@7, HANDOFF 33->24. Unrolled 33-char literal `A..Ax` on S and B: whole_run ends `78`, req_byte 120 (so literal != repeat spelling, as claimed). `Q(?:ab){20}Z`: B RUN 6162@1 WHY dominated PREFILTER memchr SCAN landmark-walk; S RUN 6162616261626162@7 WHY emitted PREFILTER handoff SCAN unanchored; whole_run S = ab^16 (Q and Z gone).
- Speed (perf stat -e instructions:u, taskset -c 7, nice, 3 repeats, 20 reps over my 2 MB English-frequency text with 6 Q / 5 Z / 10 A, gcc -O2, matches=0 both): `Q(?:ab){20}Z` B 3,886,354 vs S 27,695,960 = 7.1x more. On a text where ab/A is common (no Q): B 2,126,697 vs S 2,126,517 (no difference). `A{33}x` eng: 3,892,272 vs 3,893,572; ab-text 2,126,517 vs 2,126,517 (no loss measured; critic's "SUSPECTED" for these stays unconfirmed). `qA{40}` eng: B 6,909,193 vs S 3,896,392 (S FASTER 1.8x), ab-text 2,126,856 vs 2,126,516 -- so the claim that the q/x BASE byte "would win" is REFUTED for qA{40} on my texts (S moved WHY dominated->emitted and is faster).
- Net: the repeat-vs-literal inconsistency and the Q..Z slowdown HOLD; only `Q(?:ab){20}Z`-shaped loss measured.

### EMIT-2 — HOLDS
- Emission `x(?:a[bc]){2,3}y`: B RUN none WHY dominated PREFILTER memchr BYTE 120 HANDOFF none; S RUN 6162616279@4/fffefffeff WHY emitted PREFILTER handoff BYTE 121 HANDOFF 3 (exact as claimed).
- Speed (same method, eng text, 20 reps, 3 repeats identical): `x(?:a[bc]){2,3}y` B 8,596,974 vs S 34,259,082 (4.0x); `x(?i:ab){2,3}y` B 8,596,074 vs S 44,293,640 (5.2x); `x(?i:ab)+y` B 8,596,073 vs S 17,050,073 (2.0x). 

### SLOT-1 — HOLDS
- `S/build/pcrec --features all --engine=vm --emit-facts --pattern '(?:(?:(?:(?:ab){65535}){65535}){65535}){65535}|yz'` -> S line: `req_pieces derived no -2251748274601982:[97][98]...|2:[121][122]` (negative width). Same call on B: `declined ... none decline:not-fixed-width`. Site desc.c:163 `g->w += (long long)(k - i) * d.g[0].w;` (raw multiply, no saturation). Compiler rc=0 (no crash; UB itself not observed under a sanitizer).

### SLOT-2 — HOLDS
- `S/build/pcrec-harness --features all --emit-facts --harness=restore=empty`: `ab(?:c{0}){1}de` req_whole_run 61626465 (abde); `ab(?:c{0}){3}de` 6465 (de). Both `harness:empty`. req.c:581-582 comment "every count gives it the same value, so it takes 1" and desc.c:~150 "bounded by the two bounds, never by `k`" are the claimed false sentences (the latter: for a width-0 single group the shortcut condition `o.g[0].n < o.g[0].w` is 0<0 false, so the loop does run k times; not timed by me).

### SLOT-3 — HOLDS (reading)
- Frozen design (90ab55fd3 span_arms.md:335): "a power combinator, `pcrec_pd_cat` applied c times with the same saturation"; code: req.c:649 `pcrec_pd_pow(..., b->desc, m)` and desc.c loop `for (i < k)` with its own bound (m copies, closed-form once a single group is full/truncated). Design :310 lists `trunc` among fields that stop changing; req.c:575 same. Probe `(?:abcdefghijklmnop){3}z` on S lists req_whole_run 16-byte body twice (32 bytes), consistent with the c·w==32, c<m case. Sentence-level doc claims confirmed by quote; harmlessness of trunc not re-derived.

### SLOT-4 — HOLDS (reading)
- req.c:635-641 `rb_rep_copies_into`: `acc->set = rb_union(rmin>=1 ? b->set : rb_empty(), acc->set, rep->maxw); acc->runs = rr_cat(*rep, acc->runs); acc->desc = pcrec_pd_cat(.., desc, acc->desc);` vs req.c:532-537 `rb_cat_into`: `rb_union(r->set, acc->set, r->runs.maxw); rr_cat(r->runs, acc->runs); pcrec_pd_cat(.., r->desc, acc->desc)`. Same three statements; `rb_rep_unit_into` (:753-760) builds a value and calls rb_cat_into. Re-spelling confirmed.

### CONTRACT-1 — HOLDS
- `build/pcrec --features all --emit-facts --pattern 'xy(?:ab){0}zw'` (and `{0,0}`): S req_whole_run 78797a77 (xyzw), req_landmark_maxoff 0; B 7a77, 2. cmp1.sh vs libpcre2 on S, subjects qxyzw / xyabzw / xyzxyzw: 3 SAME (sound). tuning.md:670 §2.28¶3 says "a quantifier admitting zero iterations of a body that consumes breaks it": `{0}` admits only zero iterations yet joins. Wording defect confirmed.

### CONTRACT-2 — HOLDS (all cited cells reproduced, byte and utf8 as stated)
- S vs B req_pieces why: `(?:a|bc){10}x+` over-bound (B not-fixed-width), byte and utf8; `(?:ab|cde){11}|q*` over-bound (B nfw); `(?:a|bc){10}x*` over-bound. Order-swapped `x+(?:a|bc){10}` and `q*|(?:ab|cde){11}` -> not-fixed-width. `(?:a|bc)` written 10 times then `x*` -> not-fixed-width vs `(?:a|bc){10}x*` over-bound (one language, two reasons). Ruling-2 mover `(a.){10}xyz` utf8: S over-bound, B not-fixed-width. Not re-derived: the proposed pd_dropped fix. `(a.){10}x*`/`(a.){10}(?:b|cd)*` utf8 not re-run.

### CHECK-1 — HOLDS (probe + reading; no plant built by me; compiler exit code of any row-3 plant: none exists, PLANT_STATUS covers S1921 row-2 only)
- `S/build/pcrec-harness --features all --emit-facts --pattern 'xy(?:ab){1,2}zw'` req_whole_run `61627a77` default vs `6162 harness:rep` under `--harness=restore=rep` (B default: 6162), so a cell could separate the arm. run_facts_checks.sh RPEOF block (:~700-716): the only `h rep` cells are `$RP`=`xy(?:ab){2}zw` (whole_run, pieces, set) and `(?:a|bc){2}` pieces: all exact repeats (row 2); the one variable-repeat cell `xy(?:ab){1,2}zw req_pieces none decline:not-fixed-width` is a `p` (default build) cell. req.c:809-810 row 3 `{ rb_rep_any, RB_REP_SPLIT, PCREC_WALK_ARM(REP) }`. Whether a row-3 plant is caught elsewhere (answer-sensitive) not run.

### CHECK-2 — HOLDS (plant S463 build rc=0 per PLANT_STATUS)
- run_handoff_reach.sh:153 `(ab)c?userpass byte 3 entry -`; corpus tests/litscan/handoff_vm.rxt:847-870: `ms 0..18 "userpass userpass abuserpass" 18 28`, `ns 19..22`; no `abcuserpass` subject. cmp1.sh on plants/S463 with `--engine=vm`: starts 0,5,10,15,17,18 on that subject all SAME vs libpcre2; `0:abuserpass` SAME; `0:abcuserpass` DIFF (pcrec N, pcre2 M 0 11). The reach script's `x{2,5}(?i:cat)` is `re` (line 150).

### CHECK-3 — HOLDS
- S1919 line 16: SAB_REACH probes only `(a.){10}xyz` (REACH-WR6-K20). DFA twin `(?:a.){10}.?xyz`: RX_REQ_HANDOFF "21" on S, "5" on plants/S1919 (both compiles rc=0), and no REACH line for it in the file (grep of the sabotage for `xyz` shows only the VM witness). The twin is a corpus witness (spanarms.rxt:128,136) but has no REACH.

### CHECK-4 — not verified (needs a plant build)
- By probe/reading: no listing cell asserts the run of a non-`all` exact repeat. [facts-rep] cells use all bodies (`ab`, `abc`) and pieces of `(?:a|bc){2}`; `xy(?:a[bc]){2/3/5}zw` lists a cube run growing with m (an all body, sat=ceil(32/2)), `(?:a.){3}xyz` lists only `xyz` (the `.` breaks the run so a 1-for-2 change shows no difference there). Whether a `1` plant is observable on some non-all body is not established.

VERIFY COMPLETE
