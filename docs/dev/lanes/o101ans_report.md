# o101ans — facts for the four asks of bench O-101 (2026-10-13, lane o101ans, sonnet)

FACTS FIRST, NO RULINGS. Every DRAFT answer below is a draft for the manager to
rule on. Source: the "## O-101" section of `pcrec-bench` `docs/dev/outbox_to_pcrec.md`
(`git show origin/HEAD:`), ledger `docs/dev/ledgers/2026-10-13-req-handoff-l1-6b2dbd3e.md`
there (read-only). Pins built from `git archive` into `build/pins/<sha>/` (gitignored):
b8337c33 (BASE, abi 74), 00c97769 (L1, abi 75), 6b2dbd3e (seam, abi 76). Linux dev box
(Ryzen 7 7700X, Zen 4), gcc 15.2.0 (the bench box has the same gcc, 15.2.0-16ubuntu1,
Zen 1). Emitted with `--features all --emit-main` (possessive needs `atomic-groups`);
patterns from the bench's `bench/syntax/patterns/*.rx` and `bench/capability/curation/
designed/members.tsv`. Every number tagged SCRATCH is one core, `-O2`, a hand driver
(`build/drv/drv.c`, min of 7 rounds), light load, not a bench-tier number; the Zen 4
box is not the bench's box.

## Ask 1 -- K admission at K 0 for `(?i)cat` / `(?ir)cat` (x1.03 on landmark-absent subjects)

### Facts

1. **The design promised no +3%.** The "+3%" is the bench-facing check bound in
   pcrec's own I-147 ("any cell more than +3% slower than abi 74 with `REQ_HANDOFF` set
   is news to us", `inbox_from_pcrec.md` I-147 section 2). The ruled K admission
   (Frank, 2026-10-11, plan.md `[REQ-HANDOFF-L1]` at 48343196) says only: "K needs a
   ceiling ... admit only when K is small against L's expected hit gap (the byte-rate
   prior), with the cut-over derived, not hand-set; a hostile cell plus a sabotage
   row." The only measured expectation for a non-win mover was kv-quoted +1.2%
   (`rlhbuild_report.md` section 5.1 item 3). The report states that "the mean-gap
   point is where the jump stops PAYING in time is UNMEASURED" (`rlhbuild_report.md`
   section 0 item 3; `src/gen/emit_dfa.c:7860-7873` comment) and that the admission
   "reads the prior only" (section 7 item 3, K105).
2. **What the admission reads** (`req_landmark_admits`, `src/gen/emit_dfa.c:7874`,
   `rlhbuild_report.md` section 1.4): `h` = the landmark's hit rate under the default byte
   prior (a run's is the ceil-product of its positions' set masses), `m` = the mass of the
   start-byte set the displaced NEXT row scans (1.0 where none), K =
   `req_landmark_maxoff`. Admit iff `h == 0`, or `K*h < 1` and `(1-K*h)*m > h`, i.e.
   `1/h - K > 1/m`. Units are BYTES ADVANCED per stop. No time term, no run length
   other than through `h`, no cost per stop, no read of the subject.
3. **At K 0 for `(?i)cat` the test is vacuous.** `h = m_{cC} * m_{aA} * m_{tT}` (ceil at
   each step) and the displaced row scans `{c,C}` (its table `rx_can_begin_match` has
   exactly 'C' and 'c'), so `h <= m` by construction and `(1-0)*m > h` holds for every
   prior. Any run whose first position is the displaced row's whole start set, at K 0,
   is admitted whatever the prior says.
4. **BASE vs NEW emitted loop, `(?i)cat`** (`build/em/{b8337c33,00c97769}.modi.c`,
   diff above). Both pins already carry the ENTRY handoff (BASE `RX_DFA_PREFILTER
   "byte-class"`, entry `size_t handoff_position = rx_reqrun(...)`, `if (>= n) return 0`).
   The same kit-rendered `rx_reqrun__body` (two `memchr` streams for `C` (67) and `c` (99),
   `cand` = the nearer, a 2-byte masked-compare verify of `CA`/`AT`) is in both. The
   delta is only inside the DFA's restart: BASE deletes nothing but gains
   `while (scan_position < n && !rx_can_begin_match[subject[scan_position]]) scan_position++`
   (a 256-entry table walk, ~1 byte/iteration, no call); NEW replaces that with
   `if (landmark_position < scan_position) { landmark_position = rx_reqrun(...); if (>= n) return 0; }
   if (landmark_position - scan_position > 0) scan_position = landmark_position;`
   plus `size_t landmark_position = handoff_position;`. So the byte-class scan is
   replaced by a re-call of the run searcher (two `memchr` + a verify per candidate)
   at every restart.
5. **On a subject with ZERO occurrences of the landmark run the re-entry never
   executes.** Counted with `memchr` redirected to a counter (`build/drv/cnt.c`): NEW and
   BASE make IDENTICAL memchr call counts on landmark-absent text: 2 / 2 on a 64 KiB
   subject with no `c` at all, 3533 / 3533 on 64 KiB with 3531 `c`/`C` bytes and no
   `cat`, 12112 / 12112 on a c-dense one. Both return 0 from the ENTRY pre-check
   before the DFA (and so before the re-entry row) is reached. The bench's reading that
   x1.03 on `mod-i`/`mod-r` throughput subjects "is the re-entry's cost on landmark-ABSENT
   text" (O-101 finding (i)) therefore does not match the emitted program: on those
   subjects the executed path is the shared entry loop. What differs is the COMPILED FORM
   of that loop in `rx_search`: BASE `-O2` pushes six registers and a `0x18` frame, NEW a
   `0x28` frame with one more live value (`landmark_position`/`handoff_position`),
   different register assignment in the entry loop (`build/em/*.modi.dis`, first 40
   instructions compared), 148 vs 210 lines of `rx_search`. Whether that explains +3% on
   Zen 1 is NOT measured.
6. **Scratch timing, Zen 4 (SCRATCH).** Landmark-absent 64 KiB throughput, ns/call BASE ->
   NEW: c-dense 48,987 -> 49,064 (x1.002), c-normal 14,864 -> 14,846 (x0.999), no-c 765 ->
   762 (x0.995); `(?ir)cat` the same within 1%. So **x1.03 does not reproduce on Zen 4
   throughput.** Short subjects: 25 B no-`cat` 6.62 -> 7.30 ns (x1.10), 40 B 8.54 -> 9.08 (x1.06),
   200 B / 1000 B flat (x1.00). The short-call +0.5..0.7 ns is the shape the bench
   saw (x1.07), at fixed per-call scale.
7. **`ci-ascii-control` (utf8 set) was not built here** (the bench's utf8 roster compiles
   with `pcrec-auto-utf8`; nothing emitted for it). The same row family applies by the
   O-101 mover list (K 0, run `CAT`-style).

### What an admission term would need to know

(From the emitted code above, not from a design: the design says it is unbuilt.)
- Run length and its caseless-ness decide how many streams the searcher runs (a 3-byte
  caseless run is `2^1` memchr arms on the first byte, 2 per restart-stop) and what the
  verify costs; `h` already contains the later positions' masses but the cost per
  STOP does not enter.
- The cost of the alternative per stop: a table-walk byte vs a `memchr` call (the K82 /
  K88 / K90 family reads exactly this: a skip whose expected length is short still pays
  its call; `known_issues.md` K88, K90 L3, "Same family ... a skip whose expected skip
  length is ~0 still pays its call").
- Whether the landmark DOMINATES the displaced row: at K 0 with an identical first set,
  the re-entry buys nothing the start-byte row did not already (the run only narrows
  from 'c' to 'cat' by 2 verify bytes). A "same first set, K 0" row (displacement
  gains zero expected jump beyond the verify) is the structural gap.
- The admission is also a member of the prior-cost family (`rlhbuild_report.md` section 7
  item 2; plan `[PRIOR-COST-UNIFY]`, `plan.md:87`).

### DRAFT answer to ask 1 (draft, for the manager)

No, the design did not intend to admit it for benefit, but yes, the derived rule admits it:
the rule compares expected advance in bytes against the displaced row's, which is
vacuous at K 0 when the landmark's first set equals the displaced row's set; there is no
cost-per-stop or run-length term and none was promised (the +3% was pcrec's check bound,
not a design bound). Add: pcrec's own emitted programs show the re-entry never runs on
landmark-ABSENT subjects, so the x1.03 there is the entry loop's compiled form or
layout, not the re-entry; the short-subject x1.07 is the real per-call term (Zen 4
scratch +0.5..0.7 ns). The measurement that would settle the throughput x1.03 is a
same-binary pair with the deny (`-fno-req-handoff` removes the entry too, so it is not a
valid control for that: use a hand twin or the BASE arm).

## Ask 2 -- `qnt-poss-brace` (`a{1,2}+b`) on `f-tag` (`<b>bold</b>`, 11 B, x2.40, +17 ns)

### Facts

1. Subject `f-tag` = `<b>bold</b>` (bench `gen_subjects.py:116`); it contains no `a`, so
   the answer is no-match; `b` sits at offsets 1, 3, 9 (three `b` of 11 bytes).
2. **Emitted program** (`build/em/{b8337c33,00c97769}.qpb.c`): BASE (`RX_REQ_HANDOFF
   "none"`, prefilter `memchr`): `memchr(b)` gate (hit), then the DFA's start-state scan
   `memchr(a)` finds nothing: `return 0`. NEW (`RX_REQ_HANDOFF "2"`, prefilter
   `handoff`): the gate's `memchr(b)` becomes `handoff_position`, K = 2 clamp
   (`if (handoff_position - search_from > 2) handoff_position -= 2; else = search_from`),
   `scan_position = handoff_position`; then at each restart at s0 the row re-asks
   `memchr(b)` from `scan_position` (`if (landmark_position < scan_position)`), clamps
   `landmark_position - scan_position > 2`, and the DFA machine steps the bytes in
   between.
3. **Counted** (memchr redirected to a counter, `build/drv/cnt.c`): `f-tag` = **2 memchr
   calls BASE, 4 NEW** (the entry plus three re-entries, one per `b` landmark, the last
   returning n). The remaining added work, read from the source and not instrumented:
   the clamp arithmetic (compare, subtract, select, store of
   `landmark_position`/`scan_position`) at entry and at each restart, and the DFA's
   byte steps over `<b>bold</b>` where BASE's `memchr(a)` skipped everything at once.
4. **SCRATCH, Zen 4**: `f-tag` BASE 5.19 ns -> NEW 13.14 ns per call (+7.9 ns, x2.53);
   a 25 B `b`-free subject 2.87 -> 2.61 ns (x0.91, the win side). The bench read +17 ns on
   Zen 1: a ratio 2.2 to the Zen 4 +7.9, the same order as the unmeasured 1.6 short-call
   transfer factor in `revend.md` (:627, "UNMEASURED transfer terms").
5. **So the cost is not a fixed per-call term.** It scales with the number of landmark
   stops (three here); on a subject with no `b` NEW is cheaper or equal. Per call, the
   instructions added are: one extra `memchr` call per landmark hit (3 here, each
   preceded by the `landmark_position < scan_position` test and followed by the K clamp
   compare), plus the byte-wise DFA walk between hits that the BASE `memchr(a)` bulk skip
   replaced. The mechanism is the same family as K90 L3 ("per-call seek on a hit at offset 0
   ... +14..+17 ns", `known_issues.md:224`), K88, and K105 (a landmark denser than the
   prior; K105 trigger "a bench cell with a landmark denser than its prior" is what O-101
   reports).
6. **No tiny-subject floor exists in design or plan.** grep of `plan.md` and `known_issues.md`
   for floor/tiny/short-call: the neighbours are K103 (rev-end entry floor, a different
   path), K88 + `[K88-HANDOFF-DENSE]` (`plan.md:243`, not-started), K90/K91 and their
   plan row `[START-DENSE]` (`plan.md:469`, not-started, gated to round 3, "no row-specific
   trigger recorded"), and `[PRIOR-COST-UNIFY]` (`plan.md:87`, "FOR FRANK: schedule after
   [REQ-HANDOFF-L1] merges?"). `plan.md:474` (the peel row) names "hit-at-0 short calls
   +14..+17 ns" as evidence for the shared seek-property row. None mentions a tiny-subject
   floor. The prior (default byte rate for `b` ~ x27.6 rarer than this subject's density)
   is what makes this the density-vs-prior case, not the tiny size as such.

### DRAFT answer to ask 2 (draft)

The re-entry's cost is per landmark stop, not a fixed per-call term (4 vs 2 memchr calls
on `f-tag`, measured; +7.9 ns on Zen 4 scratch, +17 on Zen 1), so a tiny-subject floor is
not the finding: the finding is a landmark denser than the prior, which is K105's
D77 trigger ("a bench cell with a landmark denser than its prior") now met, plus the
K88/K90 family. No floor exists in the design or the plan today.

## Ask 3 -- the seam's four slower cells: does static-inline lengthen the VM quick-dismissal path?

### Facts

1. **The seam change is exactly one thing in these programs.** `diff` of the emitted C for
   `doubled-word` (`\b(\w+)\b\s+\1\b`), `tag-pair-match`
   (`<([a-zA-Z][\w:-]*)(?:\s[^>]*)?>.*?</\1\s*>`), `bak-k-named`
   (`<(?<t>\w+)>[^<]*</\k<t>>`) and `dup-param-detect` (`\b(\w+)=[^&]*&(?:[^&]*&)*\1=`),
   00c97769 -> 6b2dbd3e, is the same 27 lines each: the header `abi 75 -> 76`
   (comment, include, `.abi`), and `rx_span_match`. The hunk (dw; the same text in the
   other three):
   ```
   161a162,172
   > static inline ptrdiff_t rx_span_match(const unsigned char *s, size_t n,
   >                                      const unsigned char *ref, size_t reflen, size_t at)
   > { size_t i; for (i = 0; i < reflen; i++) { if (at + i >= n || s[at + i] != ref[i])
   >       return -(ptrdiff_t)i - 1; } return (ptrdiff_t)reflen; }
   401,410d411
   < ptrdiff_t rx_span_match(...)   (the same body, exported, at the file's tail)
   ```
   i.e. an exported function defined at the END of the file (declared in the `.h`) becomes
   a `static inline` defined before its first use. Source: lane commit 337f9a6ed
   ("span compares + back-step become inline_def (static inline, unexported)").
2. **Object code, gcc 15.2 `-O2`** (`build/em/*.nm.c` compiled with `-O2 -c`):
   `rx_search`, `rx_search_in`, `rx_match*`, `rx_search_run`, `rx_match_anchored` have
   BYTE-IDENTICAL instruction streams (addresses and relocs aside, 0 differing lines of
   `objdump -d --no-show-raw-insn` per function) and identical SIZES in both
   builds, and every `rx_*` symbol has the same offset: the removed out-of-line
   `rx_span_match` was the LAST symbol, so nothing shifts. At `-O3` also 0 differing
   lines. The only change is that the 68-byte out-of-line `rx_span_match` symbol is gone.
   At 00c97769 gcc ALREADY inlined it at both call sites (0 `call rx_span_match`), so
   the helper's inlining did not change. (Only at `-O1`/`-Os`, which the bench does not
   use, the streams differ: `-Os` rx_search 106-124 differing lines on dw/bakk.)
   .text totals (`size`), dw `-O2`: 7104 B (00c97769) vs 7012 B (6b2dbd3e), -92 B =
   the removed symbol plus alignment; tpm 4623 -> 4523, bakk 6290 -> 6198, dpd 4908 ->
   4816.
3. **SCRATCH, Zen 4, same code: noise.** `doubled-word` 25 B short-dismissal subject
   52.82/52.07/52.32 ns (00c97769) vs 52.95/51.94/51.96 (6b2dbd3e); bak-k-named
   18.46/18.34/18.73 vs 18.41/18.21/18.42 (three rounds each): within 1%.
4. **Context from the bench's own figures.** Program-identical cells (CANON vs NEW)
   run p5-p95 0.992-1.011 (O-101 seam section). The four slower cells (x1.066, x1.064, x1.041, x1.020) sit
   outside that band while their search-path machine code is byte-identical to the
   00c97769 cell, and 22 of 30 seam-changed set cells improved (`asr-lb-class` x0.704
   etc.; those are the programs where the back-step/span helper bodies actually changed
   the VM).

### DRAFT answer to ask 3 (draft)

No: the static-inline helper did not change the VM quick-dismissal path. At the bench's
`-O2` and gcc, `rx_search` is byte-identical between 00c97769 and 6b2dbd3e for all four
patterns (gcc already inlined the helper at 00c97769); only an unreferenced out-of-line
copy at the file's tail is dropped. The four slower cells therefore cannot be explained by
inlining growth, register pressure or layout inside the emitted translation unit. What
remains is bench-side: linking/placement of whatever follows the matcher object, or
measurement noise at the band's edge. Reasonable next step is the bench's own: a same-binary
re-time of the two artifacts (the owed follow-up window), since pcrec's emitted code
is provably the same for the hot path. The expected speedups of the seam are on the cells
whose back-step bodies actually changed (22 of 30 faster).

## Ask 4 -- rev-end, Zen 4 vs Zen 1, whole form `(?:P)\z`

### Facts

1. **pcrec's own measurement is Zen 4 only** (`rewtwin_report.md`, lane rewtwin,
   2026-10-11, scratch tier, 7700X, gcc 15.2, main 2f438878 abi 74, layout-controlled over
   8 pads; run 2 of record `docs/dev/optloop/rewtwin/summary_run2.txt`). Result
   (`rewtwin_report.md` section 0): **`-fno-rev-end` is 1.7-2.6x SLOWER than rev-end** on
   `alt-foo-tails`, `lit-l2/l4/l8/l31/l40`, aws, `abc$`, in caps and nocaps, short and
   long; the exception is `wild-secrets-github-pat` (rev-end x1.24 slower on short,
   x10 on class-tail subjects: K104). Per-call medians at the short regime: today
   1.9-2.6 ns vs `-fno-rev-end` 3.7-4.6 ns on the literal cells.
2. **The bench reads the opposite sign on Zen 1**, same pin 6b2dbd3e, by the O-101 report:
   rev-end / `-fno-rev-end` = 1.079 (`alt-foo-tails`), 1.02 on lit-l3..l31, median 1.013;
   `abc$` x0.69 (a win). The bench cell is a SUM over 27 subjects, 260-400 ns, i.e. ~10-15
   ns per call, vs 2-4 ns per call on Zen 4: consistent with the revend design's short-call
   transfer factor (x1.6 plus a 5 ns bench tax, `revend.md:627`), which is itself
   labelled "both UNMEASURED transfer terms".
3. K103's witness numbers are bench-side (Zen 1): "a rev-end search call costs ~9 ns where
   the forward route it replaced cost 3.8 ns ... 66 of 75 subjects +5.5 ns each" (K103,
   `known_issues.md:54`); rewtwin could not reproduce them on Zen 4 and named exactly the two
   explanations (box, or the a15fb77b-vs-7388f1c0 comparison; `rewtwin_report.md` section 4).
   The bench's same-pin O-101 arm settles the second: it is not the comparison.
4. **What pcrec does not have:** any measurement on Zen 1 of the rev-end entry or of the
   forward comparison route, any model of why a ~2 ns Zen 4 call becomes a +1..+8% loss
   instead of a win on Zen 1. rewtwin's layout lesson also applies: in one binary a second
   copy of IDENTICAL text read x1.21-1.30 off the first, i.e. the scale of every K103
   number is within layout noise unless pad-controlled (`rewtwin_report.md` section 3).
   The mechanism candidates in K103 ("the two-seed loop, the eol-view check and the tie
   bookkeeping, all before a walk that usually dies on the first byte") are read from
   the artifact, "not instrumented".

### DRAFT answer to ask 4 (draft)

Expectation (stated as an expectation, not a measurement on Zen 1): on Zen 4 rev-end is a
x1.7-2.6 WIN for the whole form (`abc$` plain the same direction as the bench's x0.69),
and the Zen 1 result of rev-end slightly SLOWER (median +1.3%, `alt-foo-tails` +7.9%) is
consistent with K103's fixed entry floor being larger relative to the forward route on a
slower, narrower core. That sign flip rests on one Zen 4 measurement (rewtwin) and the
bench's Zen 1 numbers; the floor's mechanism is read from the artifact, not instrumented,
and no pcrec measurement exists on Zen 1. K103 stays the owner (ACCEPTED/UNSCHEDULED;
`rev-end-width` would remove the entry floor on the fixed-width cells; github-pat's
class-tail is K104).

## Findings that could become K-entries or plan rows (NOT filed)

1. **K105's D77 trigger is met** ("a bench cell with a landmark denser than its prior"):
   O-101 ask 2, kv-quoted's 12 dense subjects (every one slower, x1.033-1.29), `f-tag` x2.40.
   Candidate: record the witnesses in K105 and route to `[PRIOR-COST-UNIFY]` (`plan.md:87`,
   which asks "FOR FRANK: schedule after [REQ-HANDOFF-L1] merges?"). `f-tag` is also the
   K90 L3 / `[START-DENSE]` shape (`plan.md:469`): consider listing it in that row's refs.
2. **A new K-entry candidate for the 7 cells over the +3% bound**
   (`mod-r` short x1.076 / thr x1.033, `mod-i` x1.069 / x1.031, `kv-quoted` short x1.035,
   `sfx-64/256` short x1.032/x1.031): two different causes, not one. (a) mod-i/mod-r
   (K 0, caseless run on the displaced row's set): admission vacuous (Ask 1 fact 3) and
   the throughput x1.03 is NOT explained by the re-entry (fact 5); the short-call term is
   +0.5..0.7 ns real on Zen 4. (b) kv-quoted/sfx short: not examined here. D77: measure
   first (a same-pin hand twin of the entry loop), do not build an admission term yet.
3. **Seam four cells (Ask 3):** pcrec-side the emitted hot path is proven identical, so no
   pcrec row; the follow-up window should re-time the two artifacts in one binary or with
   pad control (`rewtwin` method) before anything is filed.
4. **A misattribution to correct in the bench relay:** O-101 finding (i) says the re-entered
   run test "costs more than the byte-class scan it displaced" on landmark-ABSENT
   subjects. The counted memchr calls (2/2, 3533/3533, 12112/12112) show the re-entry does
   not run there at either pin. This is a fact to relay, not a ruling.
5. **K103 wants one line:** the Zen 4 vs Zen 1 sign flip is box-dependent and confirmed
   at a same pin by the bench (rewtwin asked for exactly this arm).

## Reproduce

`build/` under this worktree (gitignored): `pins/<sha>/build/pcrec`, `em/*.c` (emitted),
`drv/drv.c` (timing driver), `drv/cnt.c` (memchr counter via `#define memchr cnt_memchr`).
Emit: `pcrec -p rx --features all [--emit-main] -o OUT.c --pattern 'PAT'`.
Compare functions: `objdump -d --no-show-raw-insn X.o | awk '/<rx_search>:/{f=1;next} /^$/{f=0} f'`.
Commit citations: L1 merge 00c97769, seam 337f9a6ed (in 6b2dbd3e), BASE b8337c33.
