# Verifier file, round memfn-s3-final
Method: instructions:u via perf stat, taskset -c 7, min of 3; drivers emit/cnt2.c (unit repeated, find-all by rx_search) and cnt3.c; artifacts rebuilt by me in verify/. "off" = SUBJECT compiler with --memfn=no-wf-find.

### EMIT-1  HOLDS (speed); the "population widened" framing also HOLDS
`(?i)xq`, unit "xq"+60 spaces (63 B), instr/byte BASE / SUBJ / OFF:
256 KiB 9.65 / 203.6 / 9.65; 1 MiB 8.19 / 796.7 / 8.19; 4 MiB 7.83 / 3174.6 / 7.83 (matches equal, 4228/16912/67650). Quadratic in SUBJ, linear in BASE and OFF.
`x[Q%]y`, unit "x%y"+60 spaces: 1 MiB BASE 3.46 / SUBJ 784 instr/B; 4 MiB BASE 3.10 / SUBJ 3124.
BASE `(?i)hello`, unit "hello"+60 spaces: 256 KiB 197, 1 MiB 763, 4 MiB 3032 instr/B (SUBJ the same within 0.5%). So BASE already had the same quadratic mechanism on the (?i) literal; SUBJ widens the population (any PAIR stop), not a new mechanism.

### EMIT-4 (= SLOT-1)  HOLDS (speed)
find-all (cnt3) over docs/dev/dev_journal.md (1,828,608 B), total instr BASE -> SUBJ (OFF == BASE; match counts equal), instr/byte:
`[<>&]x` 1.13M -> 20.6M (0.62 -> 11.3, 18x); `[xqz]ab` 1.66M -> 22.5M (0.91 -> 12.3, 13.6x); `[.,;]\d` 12.6M -> 20.9M (6.9 -> 11.4); `[QXZ]{2}` 11.5M -> 20.6M (6.3 -> 11.3). Matches 2/2/4233/6 identical.

### SLOT-4  REFUTED on instruction counts (caveat: instructions, not time; libc memchr is SIMD so instr under-count its cost less than a byte loop)
Same text, total instr BASE / SUBJ / OFF (OFF==BASE), matches equal:
`[st][hr]` 17.36M / 10.19M / 17.36M (33927); `[et][hr]e` 10.14M / 9.43M; `[et][ao]` 17.90M / 10.74M; `[ae][nt]d` 4.10M / 3.25M. SUBJ executes fewer instructions on every common-pair stop tried. A cycles/wall cell is still the only way to settle a time loss; no instruction-count evidence for one.

### EMIT-2  HOLDS (adversarial only; real-text control is a SUBJ win)
`[0-9a-f]{8}` over "aaaaaa-" repeated to 1,048,572 B (0 matches), total instr BASE 12.64M / SUBJ 20.96M / OFF 12.64M = 12.06 -> 19.99 instr/B (1.66x; critic had 16.68 -> 24.61, 1.48x; mine has less fixed overhead, same direction).
Control, dev_journal.md 1.83 MB, 784 matches both arms: BASE 20.23M (11.06/B) -> SUBJ 4.80M (2.62/B).

### EMIT-3  HOLDS
Emitted text (SUBJ, `(?<=x)foo`, quoted from verify/lb.c): `for (;;) { if (rx_mf1_c < 1) rx_mf1_c = 1; { ... memchr(rx_mf1_s + rx_mf1_c - 1, 120, ...) ... rx_mf1_c = (size_t)(q - s) + 1; } if (!(rx_mf1_c + 2 < rx_mf1_n)) break; if (rx_mf1_c >= 1 && rx_w2(...) == rx_w2("fo") && ...`.
gcc -O2 -S: per iteration (.L4) `testq %rcx,%rcx; movl $1,%eax; cmovne %rcx,%rax; subq $1,%rcx; cmovc %r12,%rcx` (the clamp/arg setup) and in the loop `movq %rax,%rdi; addq $1,%rdi; je .L13` (the c>=1 wrap test) both survive.
Hand edit (clamp hoisted above the loop, `c >= 1 &&` deleted), find-all of "xfox"x262144 (1 MiB, 0 matches), instr/B: SUBJ 23.31 -> edited 19.31 (-17%; critic said 31.88 -> 27.88 on their driver, -4 instr/B both).

### CONTRACT-1  HOLDS
`foobar`, `\bcat\b`, `abcd`, `a|b`, `[a-z]` all stamp at SUBJ `RX_DFA_SCAN "cover"` + `RX_DFA_PREFILTER "none"` (BASE: unanchored + run-pinned / offset-set-bounded / byte-class). Spec match_api.md §6.3.4¶3 (SUBJ) defines `"none"` as: "no candidate-start filter: the start state accepts (`start_acc` ...), every position is a candidate, or the artifact provably matches nothing". A cover artifact is none of the three (its window search is the candidate mechanism); the `"cover"` row (line 2036) and ¶3 carry no prefilter clause (grep of the cover row for PREFILTER: empty). Only ¶8 (table stamp) has a cover clause.

### CONTRACT-2 (= EMIT-5 doc half)  HOLDS
SUBJ vs BASE REQ_WHY/REQ_HANDOFF: `\bcat\b` "dominated"/"none" vs "emitted"/"0"; `(?<=x)cat` same; `(?i)hello` same. Spec match_api.md ~2370 (`"dominated"`): "declined: the artifact's own candidate-start `memchr` (or run-pinned test) already scans a byte at least as rare, or its locator decides presence itself (`<PREFIX>_DFA_SCAN "rev-end"` or `"empty"`)" -- cover is not named; tuning.md 2.29¶5 line 694/710 names "a `rev-end` or `empty` body" likewise. Stale closed enumeration.

### EMIT-5 (stamp half)  see below, after check
EMIT-5 stamp half HOLDS: SUBJ `[<>&]x` stamps `RX_REQ_BYTE "120"`, `RX_REQ_WHY "dominated"`, `RX_MEMFN_LIBC "none"`, and `grep -c memchr` of the artifact = 0 (walk over {&,<,>}); BASE's artifact had `memchr(subject + pos + 1, 120, n - pos - 1)`. `(?<=x)foo` SUBJ: `RX_REQ_RUN "666f6f@0"` (f) while the only memchr scans 120 (x, `rx_mf1_c - 1`). Spec "dominated" text (quoted above) says "the artifact's own candidate-start memchr ... already scans a byte at least as rare": false for the first. Severity doc.

### CONTRACT-3  HOLDS
SUBJ: `abcd`, `a|b`, `[a-z]` -> `RX_DFA_SCAN "cover"`, `RX_DFA_START "attempt-start"` (BASE "end-minus-width"). tuning.md 2.47¶2 (line 1007): "`abcd`, `a|b`, `[a-z]`, ``, `(?!a)` and `$`-free fixed-width patterns take it ... nor on a body with no reverse pass to replace (`"attempt"`, `"empty"`)" -- no `cover`. match_api.md 3.1¶21 (line 546-548) in the hunk's own paragraph: "where every match has the same byte width `W` (`abcd`, `[a-z]`), the start is the end minus `W` (`"end-minus-width"`)" two sentences before the added cover sentence (lines 557-559) that says cover "takes none of the four".

### CONTRACT-5  HOLDS
`cat\z -fno-rev-end`: SUBJ `RX_DFA_SCAN "cover"` (BASE "unanchored"); `cat$ -fno-rev-end`: SUBJ "unanchored". tuning.md 2.46¶4 (line 998): "the denied build reads `"unanchored"`" -- false for the `\z` shape at SUBJ.

### HOUSE-1  HOLDS
`grep -rnw pcrec_fact_span` over SUBJ src/ cli/ lib/ memfn/ tests/: only the decl `src/facts/facts.h:529` and the def `src/facts/facts.c:616`. The sole caller is `known.c:261`, which calls `pcrec_fact_span_stated`. (Other hits are docs/lanes and docs/history only.)

### HOUSE-6  HOLDS (spelling differs; defect status is not shown)
memfn/src/gate.c:476 (line is new in the diff): `if (in->s->nalt || in->s->alts) return -1;`
memfn/src/compose.c:941: `if (!site->nalt && !site->alts && !site->wfloor) return 0;`
memfn/src/window.c:1875: `return p->nalt || p->alts || p->wfloor;`
`wfloor` is a uint8 field of mf_site (include/*.h:681). gate.c omits it. Whether a wfloor-only site reaches cl_table_ref was not exercised; NOT VERIFIED as a behavioural defect.

### HOUSE-7  HOLDS
window.c:2538-2552: `static int d_hors_head(wf_rc *rc, kb *b, const char *bound, int *skip)` then `(void)bound;` then `kb_printf(b, "if (%s + %d >= %s) break; ", rc->C, w->chi, rc->N);` -- the parameter is voided and the bound re-spelled (`C + chi >= N`).

### SLOT-8  HOLDS (reading)
window.c:1672-1683 `b_fn_holds`: requires `b->pick == FF_PAIR` (FIND slot), then separately runs `translate`, `ofs_fn_scan(p,&k,&lo,&hi)` and `ofs_fn_serves(...)`. ofsskip.c:210-216 header: BODY slot "fn-pair (the scanned position is a two-member cube) above fn-memchr (otherwise)"; rows at ofsskip.c:912-918 share `FN_BODY_SERVES`. So the body re-decides pair vs memchr from the scan's mask after the finder picked PAIR. The "agree by construction, nothing checks it" part is a reading, not tested.

### SLOT-2  HOLDS (reading; 8 lines, critic said 7 sites)
Row-id tests outside the walk, window.c: 1771 `if (fx->bren == B_FN)`; 1839 `if (r == E_FIND && !quiet && wf_find_decide(...))`; 1843 `if (r == E_FIND && wf_find_prepare(...))`; 1848 `r == E_FIND && fx->drow < WF_NDROWS ? wf_drows[fx->drow].path : ""`; 1850 `if (r == E_FIND || r == E_GENERIC)`; 2611 `if (w->bren == B_FN) return wf_find_fn(rc, o);`; 2619 `if (w->bren == B_PAIR)`; 2644 `if (w->bren == B_FN)`. Whether Goal 3 requires none is a design reading, not tested.

### CHECK-1  HOLDS for the reader (extracted functions only, suite not run); consequence for the suite NOT VERIFIED
Extracted `cover_pick` and `cover_pick_stamped` (+ the three regexes, lines 1037-1105 of tests/codegen/run_encoding_checks.sh) into verify/cp.py and ran them on SUBJ `(?i)foobar` byte (fb.c) and `-e utf8` (fu.c) artifacts, both `RX_DFA_SCAN "cover"` with one `scan_position = ({` line whose find is `rx_mf1_ofsskip(...)` (helper `rx_mf1_ofsskip__body` at file scope, not in the line):
byte: stamped (K=3, {66,98}) picks [] ; utf8: stamped (K=5, {82,114}) picks [].
So stamps differ (line 1543-1544 condition true) and the reader finds 0 clauses on each side: at lines 1549-1550 that branch is `len(picks) != 1` -> "carries 0 search clause(s), not 1". Whether the corpus contains such a pair (red) or not (silent gap) was not checked.
