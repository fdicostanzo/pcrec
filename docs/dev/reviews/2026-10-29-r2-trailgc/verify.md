## Verdicts

### CON-2 / EMIT-3: HOLDS
Pattern `(?:a|ab)*(?:(\w+)=(\d+);)*+end`, subject emitted/perf/frm.txt (100k a + 100k "k=1;" + end), rx_search_in 1M frames, trail T, -O2, fresh BASE/SUBJECT builds in verify/frm.
BASE T=64: rc -3 (FRAMES), 0.097 s. SUBJECT T=64: match, 3.31 s; T=128: 1.20 s. Doubled subject (frm2.txt, 200k+200k) T=64: 10.41 s (3.1x for 2x input: ~quadratic). Matches the critic (3.54 / 10.12 s). Answer is right, cost is the frame walk.

### CON-1 / EMIT-6: HOLDS
Fresh cscan builds (BASE and SUBJECT, -O2), emitted/perf/seg20.txt, rx_search_in 1M frames, trail T (rc -3 = FRAMES):
T=184 subj -3; T=185 subj answer; T=199 subj answer; T=200 subj -3; T=201 subj answer. BASE gives up (-3) at all of 184/185/199/200/201. Non-monotone in T, though no answer is lost versus BASE.

### Cost conflict (item 3): HOLDS, and the two critics measure different entries
perf stat -e instructions:u -r 3 taskset -c 7, -O2, fresh builds in verify/{cscan,ab,par}. Subjects: verify/ident270.txt (221 B of identifiers inside `(?{ ... })`, cscan matches), verify/ab100.txt (a^100 b^100), emitted/perf/parens.txt. Mode 0 = rx_search_in 1M frames / 4M trail, mode 1 = default rx_search. Answers identical BASE vs SUBJECT (checked caps for ab; cscan checksums equal). Tier hook (-DRX_TEST_TIER_HOOK): fast tier escalates exactly once per call on BOTH sides for cscan ident270, ab100 and seg5.

| pattern / subject | (b) rx_search_in BASE -> SUBJ | (a) default rx_search BASE -> SUBJ |
|---|---|---|
| cscan / ident270 (3000 reps) | 173.60 M -> 175.73 M = +1.23 % | 177.68 M -> 182.78 M = +2.87 % |
| `^(a(?1)?b)$` n=100 (20000 reps) | 274.94 M -> 285.10 M = +3.70 % | 303.86 M -> 363.08 M = +19.5 % |
| `(\((?:[^()]++\|(?1))*\))` / parens.txt (100 reps) | 4785.6 M -> 4968.6 M = +3.82 % | not run |

Mechanisms: the mode-0 column is the checkpoint cost on the never-full path (cscan ~1.2 %, inside D183's +1.1-2.1 %; ab100 +3.7 % and parens +3.8 % are OUTSIDE it; EMIT-1's parens row reproduces: +3.82 %). The extra in mode 1 over mode 0 (cscan +1.6 points, ab +15.8 points) is the fast-tier compaction before the same escalation (see EMIT-4). So D183's 1.1-2.1 % holds for cscan via rx_search_in only; TRADE-2's 19.6 % is the default entry on a recursion pattern whose fast tier escalates anyway.

### EMIT-4: HOLDS
cscan, emitted/perf/seg5.txt (18 B file), 80000 reps: default rx_search 739.60 M -> 851.28 M = +15.1 % instructions:u; rx_search_in big buffers 586.16 M -> 591.60 M = +0.93 %. Tier hook over 1000 calls: esc 1000 on BASE and SUBJECT (escalates once per call on both), same checksum.

### SLOT-2 / TRADE-1: HOLDS
Review tree tests/codegen/run_recursion_identity.sh:1285: `FILEPIN="${RECURSION_IDENTITY_FILEPIN:-02229045e}"   # [REQRUN-VM] merge commit ... abi 91 ...`. `git cat-file -p 02229045e:src/gen/emit_dfa.c | grep PCREC_ARTIFACT_ABI` -> `#define PCREC_ARTIFACT_ABI 91`; review tree src/gen/emit_dfa.c:55 `#define PCREC_ARTIFACT_ABI 93`. The gate (lines ~1383-1393 in file; the abi block compares `.abi = N` of the subject's and the pin's artifacts for pattern 'a') calls `bad "the emitted scaffolding changed: bump abi ... and re-pin comparison (B) ..."` on mismatch; `bad` counts a failure. The branch does not touch FILEPIN. Gate not run.

### SLOT-1 / CHK-4: PARTLY
`python3 -I tests/vm/trail_checkpoints.py --corpus build/pcrec <tree>` (review binary, watchdog): "4984 corpus patterns, 4531 VM artifacts checked, 747 with a checkpoint; heaviest checkpoint-free path 251 (margin 251)", 10.08 s wall. Time claim HOLDS (docstring/header says minutes). Wiring: HOLDS in that no make target / script / mech arm passes TRAIL_CORPUS=1 (grep of Makefile, scripts/, tests/: only the `TRAIL_CORPUS` reads in run_trail_compact.sh:11,32,161 and tests/vm/CLAUDE.md:23, which says "TRAIL_CORPUS=1 adds the corpus-wide check"); the corpus mode is reachable only by env opt-in through run_trail_compact.sh (which IS in `make test-vm`, Makefile:903). So "wired into no ... target" is true for the corpus mode, not for the script. The SLOT-1 first half (cycle rule enforced on 2 of ~31 goto sites) was not re-derived.

### SLOT-3 / EMIT-5: HOLDS
`(\w+)(?:,(\w+))*;` --features all --emit-ir: BASE and SUBJECT outputs both 121 lines, `cmp` identical. Generated C: BASE 0 `TRAIL_CHECK();`, SUBJECT 1 (`RX_TRAIL_CHECK();` at line 420 of c_s.c). emit_vm.c: `v->ncheck++` at two sites with two spellings: vm_trail_check (line 3489, `pcrec_sb_printf(v->b, "    %s_TRAIL_CHECK();\n", v->up)`) and vm_jump (line 3509, `vm_rolef(v, "{ %s_TRAIL_CHECK(); goto %s_L%d; }", ...)`).

### SLOT-4 / CHK-3: HOLDS
trail_checkpoints.py check_text: margin = the `const size_t margin = N;` in the emitted floor function; verdict (2) is `worst > margin`, where worst is the max over match functions of the heaviest checkpoint-free path (`_SET(` weight 1). Emitted margin vs count of non-#define `_SET(` lines: `(\w+)(?:,(\w+))*;` margin 4 / 4 sites; frm pattern margin 7 / 7 sites. Verdict (1) (no SCC containing a SET) makes the graph acyclic over SETs, so a simple path crosses each site at most once and worst <= site count == margin: (2) cannot fail while (1) passes. (Per-function counting: a function with fewer sites only lowers worst.) Not re-derived for artifacts where the margin is not the site count (none found in two).

### CON-3: HOLDS
docs/pcre2_compliance.md:1671 (review tree): "2048/3072 by default ... measured 2.0 frames vs 9.0 trail entries per nesting level of `^(a(?1)?b)$`, so the default gives up at n = 342, a 684-byte subject". Lines 1745-1747: "2.0 frames against 9.0 trail entries per nesting level ... gives up at n = 342, a 684-byte subject".

### CON-4: HOLDS
`grep -rn TRAIL_MARGIN src tests docs lib` in the review tree: one hit, src/gen/emit_vm.c:551 (the nset comment, "the trail margin (<PREFIX>_TRAIL_MARGIN)"). The emitted text names the margin as `const size_t margin` inside `<p>_trail_gc_floor`; no `_TRAIL_MARGIN` is emitted.

### CHK-2: HOLDS (two witnesses), with a note
Ran tests/vm/run_trail_compact.sh standalone (TMPDIR=verify/tmp, PCREC=review binary, watchdog -s 120, 3.9 s, 34 pass / 0 fail; it uses mktemp -d and writes nothing into the tree). `greedy-frames: ref 1 hw 601 runs 315 answered 0 below_hw 0 gaveup 315 mismatch 0`; `empty-guard: ref 1 hw 1503 runs 376 answered 0 ... gaveup 376 mismatch 0`: every ladder capacity gave up, so "mismatch 0" compares nothing. Note: the third identity witness `backref-loop` has answered 1 below_hw 1, so it is not vacuous. The driver only counts a mismatch on answered runs (trail_compact_driver.c lines ~97-104).

### CHK-5: HOLDS
tests/vm/trail_compact_driver.c:42 `#define REF_TRAIL ((size_t)1 << 22)`, :80 `trail = malloc(REF_TRAIL * (size_t)RX_TRAIL_FRAME_SIZE);`, :60-66 `run(...)`: `b.trail = trail; b.ntrail = ntrail;` called as `run(s, n, frames, REF_FRAMES, trail, nt, got)` with the ladder's nt. Capacity nt is declared but the buffer behind it holds 4M entries, so an overrun past nt lands in spare memory unseen (consequence not exercised by me; only the setup was verified).

### TRADE-4: PARTLY
"92 = kit S3" per main: docs/dev/owner.md:25 "S3 gets abi 92 (landing order)"; docs/dev/wake.md:15 "kit S3, abi 92", :17 "S3 holds 92; numbers go in LANDING order: if trailgc lands before S3 it takes 92 and tell the kit", :20 "S3 (abi 92)", :35 "abi 91 on main; 92 = kit S3; 93 = trailgc (provisional)". The kit's own memfn/docs/wake.md:29 still says "main is at 84 ... S3 holds **85**" (stale); memfn/docs/journal.md:2857-2892 says S3 renumbered 84 -> 85 and was at abi 85 (2026-10-24); no memfn doc says 92. requests.md/responses.md name no S3 abi number. So 92 is main's reservation, not stated by the kit's docs, and main itself says it is landing-order dependent ("if trailgc lands before S3 it takes 92").
