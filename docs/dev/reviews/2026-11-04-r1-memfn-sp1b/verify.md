# Verifier round memfn-sp1b

## Verdicts

### 1 CONTRACT-1 = CHECK-1 — HOLDS
`grep -cF` of each SAB_BEFORE anchor in worktree presence.c: 0 and 0. `python3 -I scripts/m6read_check_sab_anchors.py` (SUBJECT tree) prints `sabotages checked: 1102 ... STALE ANCHORS: 2  S1094 ... ANCHOR NOT FOUND; S1096 ... ANCHOR NOT FOUND`, rc nonzero. run_codegen_tests.sh (~3650-3657): `sab_anchor_out="$(python3 "$ROOT_DIR/scripts/m6read_check_sab_anchors.py" ...)"; ... elif [ "$sab_anchor_rc" -ne 0 ]; then bad "[SABANCHOR] ..."` so make test-codegen reads red.

### 2 CHECK-2 — HOLDS
Built verify/p2: SUBJECT presence.c copy with kit_mass capping each position's rate sum at 1e6 and leaving the rated total uncapped (NONE capped once); compiled `gcc -std=gnu11 -O1 -I memfn/src -I memfn/include -I lib -c`, swapped into a copy of SUBJECT build/libpcrec.a (`ar d`/`ar r` presence.o), linked with tests/memfn/mass_check.c. Control (unmodified presence.c same way): `checks passed: 20 / failed: 0`. Plant: `checks passed: 20 / checks failed: 0`, rc 0. So the golden test is blind to it. Callers: `grep -rn KIT_MASS_CAP memfn/src` -> window.c:435, 488, 1613; presence.c:217, 227, 230; every one passes `, 1,` (n == 1). Latent only, no emitted-byte effect today.

### 3 CONTRACT-2 — HOLDS
Recipes from roadmap.md R22/R23 (rows at lines 641-642, unchanged by SUBJECT), applied via `git show REV:memfn/src/{presence,window}.c | grep -c PATTERN`: R22 BASE 1+1+1+1 = 4 variants (minus 1 = 3); SUBJECT 0 (minus 1 = -1, delta -4 vs design's -2/-3). R23 BASE wf_ties 1 + tie_over 1 = 2 (minus 1 = 1); SUBJECT 1+0 = 1 (minus 1 = 0). Recipes name only the deleted functions (kit_mass not counted). Does any script read them: `grep -rln 'roadmap.md'` over scripts/ tests/ Makefile tools/ -> only tests/vars/gen_corpus_plan.md (a prose mention); no script counts R22/R23. Doc-level only.

### 4 CONTRACT-4 — HOLDS
window.c:112-114 (SUBJECT): `return to == TIE_HIGHER ? c > b : to == TIE_LOWER || to == TIE_LEFTMOST ? c < b : 0;` so LOWER and LEFTMOST give the same `c < b`. LEFTMOST rows: only T_WINDOW (window.c:99-101: `[T_WINDOW] = {... TIE_LEFTMOST, "pcrec_find_run_window_start's strict <", "today's" }`). `grep TIE_LEFTMOST|TIE_LOWER memfn/src`: LOWER used by T_MASS_SET (:90) and T_MODEL (:92); LEFTMOST by T_WINDOW only (:101) plus the enum (:78). Naming duplication only.

### 5 CONTRACT-3 and CONTRACT-5 — HOLDS
kit.h:340-342: "every comparison in the kit that can tie reads its row through the answer below". Contradicting lines: window.c:498 `if (wf_ties[T_CMODEL].to == TIE_EXCHANGE)` and :699 `return l < r || (l == r && wf_ties[T_MARGIN].to == TIE_RESEED);` read rows directly; presence.c:158-162 `for (unsigned k...) /* rightmost first: a tie stays */ ... if (scan < 0 || c < sm)` (tie-able, no TIE row); presence.c:190-192 `set_leads = kit_mass(..qp..) < kit_mass(..sp..)`; presence.c:205 `dom = rate && lead >= 0 && rate[proof->byte] <= rate[lead];`.
window_site.md §2.1 table (lines ~222-233) has 6 data rows (mass-stretch, mass-set, A-model, C-model, MARGIN, truncation window) and calls itself "the ONE place every tie rule ... lives"; wf_ties[] at SUBJECT (window.c:84-108) has 7 rows (T_PRES_MEMBER missing from the doc; T_WINDOW row there has no kit-reader note). Doc drift confirmed.

### 6 EMIT-1 — HOLDS
verify/e1.c, linked against SUBJECT build/libpcrec.a (kit.h included, `gcc -std=gnu11 -I memfn/src -I memfn/include -I lib e1.c libpcrec.a`). Output:
```
NONE omitted-mask: 1000000      kit_mass(NULL,&(kit_pos){.t='a'},1,KIT_MASS_SUM)
NONE mask=0xFF: 3906
rated omitted-mask: 301056 (byte 'a' alone = 1097)   (rate[b]=1000+b)
```
An omitted mask is 0, so f = ~0 & 0xFF = 255: the whole 256-byte alphabet is priced, not the byte 'a'. A footgun for a future caller (all current callers set mask or set), no current effect.

### 7 HOUSE-6 — REFUTED (within the limit)
`wc -c` at SUBJECT: memfn/src/CLAUDE.md 11389 (BASE 11253), tests/memfn/CLAUDE.md 11944 (BASE 11765). scripts/check_claudemd_size.sh limit table (lines 18-25): `*) echo 12288 ;;   # every directory guide` (1 KB = 1024; not 12000); the check is `[ "$2" -gt "$lim" ]`. 11944 < 12288 by 344 bytes (also under 12000 by 56). Not over the limit; only a thin margin (tests/memfn/CLAUDE.md).

### 8 CONTRACT-6 / HOUSE-1 — PARTLY (pcrec guarantees canonical; the kit does not)
Kit side: compose.c `kit_presence_check` (SUBJECT :534-600), the RUN branch checks only `member_order`, `run_len < 2`, at most one run; no line tests `run[j] & ~mask[j]`. memfn.h:608-614 says a run[j] with a bit mask[j] clears "is IN the vocabulary: ... it never holds" (RULED Q-G2-13). Other kit files do handle it: gate.c:728 `if (t->run[j] & ~t->mask[j] & 0xFF) return CL_UNSAT;`, runcmp.c:345 same. Presence.c's landmark loop (:222-224 `if ((b & mask) == t->run[j]) set |= ..`) would build an EMPTY set on such a byte; kit_mass's cube would count 2^popcount(~mask).
pcrec side: src/facts/facts_derive.h:90-94 "CANONICAL: `bytes[i] & ~mask[i] == 0` at every position ... (src/facts/req.c's one position constructor refuses any other pair)", so every run pcrec states is canonical. In the canonical case {b : (b&mask)==run[j]} == {run[j] | f : f submask of ~mask}, all distinct, so replacing the landmark set-building loop (presence.c :222-224) and translate's cube[] loop (window.c :1341-1349) by `run_pos(t, j)` cube positions yields identical kit_mass values (same members, same multiplicity; kit_pos mask default 0xFF when t->mask NULL = run_pos). By reading: byte-identical for pcrec-stated runs. Not probed by compiles. The guarantee lives in pcrec's statement, not in kit_presence_check; a non-canonical caller (tests/other front end) would see differing answers (set empty vs cube nonempty) - a latent definitional gap, no current effect.

### 9 CHECK-5 — PARTLY (real, but it is 3 FAILs not 2)
run_finder.sh `part` (:63-73): when the log lacks `checks passed:`/`checks failed:` it echoes `FAIL: $1 printed no checks passed/failed counts` and `tf+1`. For a segfaulting masschk (log empty or only `ok` lines; the part's FAIL echo goes to stdout, not mass.log): (1) `part` +1; (2) line 94 `[ rc -eq 0 ] || [ grep -c '^FAIL' mass.log -gt 0 ] || { echo "FAIL: masschk exited $rc with no failed check"; tf+1 }` +1 (mass.log has no FAIL line); (3) `mp` empty -> `${mp:-0} -ge 20` false -> `FAIL: mass: 0 cases passed < floor 20` +1. Total 3 FAILs for one crash (critic counted 2, missing the floor line). Still red, so verdict unaffected; noise only. Same shape exists for provenchk (pre-existing). No timeout wrapper on masschk (:91), as critic said.

VERIFY COMPLETE
