# VERIFY memfn-sp1c (SUBJECT 3ecb647c7, BASE 7b671bc2c)

Own plants under verify/ (archive of 3ecb647c7). Pcrec relinks reuse check/main.o as the CLI main only.

## CONTRACT-1
HOLDS (doc claim). integration.md:2726 (SUBJECT tree) reads: "| Q-G2-13 | a run byte with bits outside its mask | **IN the vocabulary, literal formula; constant-false rendering allowed.** The term never holds. ... (First ruled REFUSED; REVISED, because G2's generated space exercises the shape and §14.6's totality ...)". The 3ecb647c7 diff touches no integration.md (diffstat over docs/memfn.h: window_site.md, lanes history, include/CLAUDE.md, memfn.h only), so the row has no presence exception. memfn.h:616-622 and :799-804 do state the carve-out. compose.c:585-587 message cites "Q-G2-13" ("the span would never hold, Q-G2-13; D187, MF_SITE_ABI 23"): confirmed as quoted. Did not re-run edge.c (reading-only claim for the doc part).

## CONTRACT-2
HOLDS as to the missing assertion; the "by construction" claim itself is not demonstrated false (critic marked SUSPECTED, I agree). span_pick.md:363 1c row: "translate's run rank reads T_MASS_STRETCH, `rank_pos[0]` asserted against `run_member`". window.c:1356-1369 has only the comment "rank_pos[0] IS the run member by construction"; the loop (kit_run_member over w->set[hint_at], exact 0, cursor) has no assert/compare. window.c run_member (:808-829) uses r->set with exact = verify NO, so the two may differ in principle. Not reproduced as a divergence.

## CONTRACT-3
HOLDS. Same mechanism as SLOT-1; see SLOT-1 for the re-run. Additional structural claim: kit_tie_takes returns 0 for non-HIGHER/LOWER/LEFTMOST (window.c:~112-116: `to == TIE_HIGHER ? c > b : to == TIE_LOWER || to == TIE_LEFTMOST ? c < b : 0`), and the `after` filter (window.c:776-778) is built on it. Claim that S1095 plants only the pick spelling (window.c:780) and not the `after` filter: line 780 is the pick's `kit_tie_takes(...)`, line 777-778 is the `after` one; matches. Mechanism-of-detection remark not run.

## CONTRACT-5
HOLDS. span_pick.md:388-389: "stage 1 ends at 4 or 5 (R20 2, R24 1, R25 1, R22 0-1)" unchanged by the subject. Recipe (docs/design/stream/roadmap.md:643, NOT memfn/roadmap.md; the critic's path name is loose): `^static void run_member(` + `p->rank_pos\[j\] = \(uint16_t\)i;` + `out->run_scan = \(int16_t\)scan;` minus 1. Ran grep -c on window.c/presence.c: BASE 1,1,1 -> 2; SUBJECT 1,0,0 -> 0. So R24 ends 0, stage 1 end is 3 or 4 on the 1c allowance. R25 not re-run.

## SLOT-1
HOLDS. Own plant: private archive of 3ecb647c7 memfn/, window.c:87 `TIE_HIGHER` -> `TIE_EXCHANGE` on the T_MASS_STRETCH row; driver = the critic's slot/walk.c (4 identical single-byte sets, rate NULL, repeated kit_run_member with the `after` cursor, printing r.pos).
Command: `gcc -O1 -std=gnu11 -Itree/memfn/src -Itree/memfn/include -Itree/memfn walk.c tree/memfn/src/*.c -o walk_plant && ./walk_plant`
Observed: `rank[0] pos=0 / rank[1] pos=-1 as uint16=65535 / rank[2] pos=0 / rank[3] pos=-1 as uint16=65535`.
Control (unplanted): pos 3,2,1,0. Source: kit.h:351-352 says only "asking again from each answer walks the whole order"; no precondition on the row (kit.h:358 area), translate casts `(uint16_t)r.pos` (window.c:1366) with no pos>=0 check. Key-space claim (run-relative j vs a_mass_choose's `k + WF_LO`, window.c:~573) confirmed by reading; BASE's run_member keyed `r->start + j` (base window.c:793).

## SLOT-2
HOLDS, with one nuance. window.c:86-89 basis reads "today's; on REPORT literal stretches UNMEASURED DEFAULT", no cross-seam obligation. compose.c:664-675: `pk.run_scan < at ...` and `part_is_run(..., (unsigned)pk.run_scan, 1)` -> "its run part is not the WINDOW its presence link verifies ...". emit_dfa.c:1070-1074 internal-error on `w.run_member != r->idx`. Nuance: the pk.run_scan compare in pres_layout_check ALREADY existed at BASE (base compose.c:670-678), so 1c does not add a pinned reader; what it changes is that P3's scan now follows the TIE row (it was a hard-coded rightmost strict `<` at base presence.c:203) so a row flip now moves P3 against the pcrec pin. Flip consequence not run (reading only).

## SLOT-3
HOLDS (reading). Quoted: kit_run_set presence.c:87-93 `(b & mask) == t->run[j]`; memfn_sites.c:517-522 `(b & mask) == (byte & mask)`; findings.c:631-640 cube_mass uses `rate[t | b]`; findings.c:~795 `bytes[j] | b`. Three conversions differ on a non-normal position (empty / normalised / stray bit counted). span_pick.md:424-425 lists scan_index, _window_start, run_pin; grep -c wpos_cube span_pick.md = 0, so it is not filed there. Not run (no divergence is reachable today).

## SLOT-4
HOLDS (reading). gate.c:725-731 `if (t->run[j] & ~t->mask[j] & 0xFF) return CL_UNSAT;`; runcmp.c:341-347 run_cmp_sat the same test; generic.c:195-201 `if (tm->run[j] & (uint8_t)~m) { kb_puts(b,"0"); ...}`. compose.c:585 reuses run_cmp_sat (also ofsskip.c:116, runcmp.c:547). Three independent spellings of the predicate, one reused: as the critic says.

## CHECK-1
HOLDS. Plant (own, private copy of 3ecb647c7 window.c; compiled against the subject's libpcrec.a, check/main.o as CLI main): after `r = kit_run_member(...)` in translate insert `if (k) r.pos = (int)(n - 1 - k);`. Compare against build/pcrec emitted C (`-p rx --features all`):
 plant, default flags: `(?i)enzyme` same; `(?i)union.*?select.*?from` MOVED; `foo.*barbazqux` MOVED.
 plant, `-fmemfn-simd`: all three MOVED.
 control (unplanted window.c rebuilt the same way): 6/6 same.
No check catches it: grep for rank_pos in tests/ and scripts/ finds only run_rank.sh, rank_check.py (hands-no-ranking check, per critic) and sabotages S750/S751/S794, all of which plant vrun.c. No sabotage row anchors window.c's translate rank loop. window.c:1361 comment says "rank_pos[0] IS the run member by construction" with no assert. The answer-neutrality claim (different KB filter only) was not re-tested.

## CHECK-2
PARTLY. Witness table: tests/memfn/pres_pick_witnesses.tsv lines 26-27: `scan 1 3 -e utf8 --memfn=no-window-search abcd` and `scan 1 - --memfn=no-window-search (?i)hello world`. Note the table's real check is the MFPICK agree comparator in a CAND_TRACE build (header lines 3-12), not byte identity; I did not run that build, so byte identity is only a proxy.
 p3b (run_at returns only the run byte's bit): `abcd` same, `(?i)hello world` same, `x.*(?i)abcdef` MOVED at default and `-e utf8`, `(?i)union.*?select.*?from` same. Claim holds for p3b on bytes (union differs from critic's 1/8 note only in that I got same).
 p3a (`exact` 1 at presence.c:161): `abcd` same, but `(?i)hello world` with `--memfn=no-window-search` MOVED (also with the critic's own check/c_p3a/pcrec: `cmp.sh` printed MOVED). So the critic's statement that plants "leave BOTH scan witnesses byte-identical" is REFUTED for p3a: command `verify/cmp.sh check/c_p3a/pcrec "--memfn=no-window-search" '(?i)hello world'` -> MOVED. `x.*(?i)abcdef` and union MOVED under p3a. Net: the `abcd` witness is blind to both; the hello-world witness sees p3a on bytes and is blind to p3b.

## CHECK-3
HOLDS. Own plant: runcmp.c:344 loop bound `j < t->run_len` -> `j < 1` (anchor count 1), kit src copy linked with tests/memfn/mass_check.c from the archive. Control and plant both: `checks passed: 40`, `checks failed: 0` (verify/pl.sh ctl / r1). mass_check.c:242-243 `lower = { 'a', 'B', 'C' }` violates only position 0.

## CHECK-4
HOLDS. S458 SAB_REACH (tests/mech/sabotages/S458_set_leads_tie_leads.sh): `"$PCREC" --features all -p rx -e utf8 ... --pattern "é@" && grep -q '^#define RX_REQ_RUN "c3a940@2"' && ! grep -q "!memchr(subject + search_from, 64,"` at default flags. Own plant: presence.c set_leads `KIT_MASS_SUM) <` -> `<=`. Subject output: RX_REQ_RUN line 1, memchr(...,64, count 0; plant output: identical counts (0 / 1), and `cmp` says same bytes (`verify/cmp.sh cp_s458/pcrec "-e utf8" 'é@'` -> same). So the probe passes with and without the plant. With `--memfn=no-window-search` the plant MOVES the bytes. Probe is vacuous for the plant site at default flags. (Pre-existing, as the critic says: 1c's diff touches only comment/figure lines of this file's header.)

## CHECK-5
HOLDS. decider_census.py:43-44 BACKSTOP = ["kit_walk(", "< best", "< bm", "< lo", "< sm", "< wl", "> c)", "tie_takes", "TIE_", "< inc"]. Grep -cF over memfn/src/*.c, BASE vs SUBJECT: `< sm` 1 -> 0, `> c)` 1 -> 0, `< inc` 0 -> 0, `< bm` 2 -> 1, `tie_takes` 6 -> 7. kit_run_member itself is matched only through its tie_takes call. The twin-passes-census claim (53/53) not re-run.

## EMIT-1
HOLDS. window.c:777 and :780 key T_MASS_STRETCH with run-relative `(int32_t)j` / `b.pos`; a_mass_choose (window.c:~573) uses `(int32_t)k + WF_LO`; BASE window.c:793 keyed `r->start + (int32_t)j`; kit.h:365 "Keys are offsets, except T_PRES_MEMBER's". Equivalent today only because the row is TIE_HIGHER (a plain `c > b`). No mover.

VERIFY COMPLETE
