# ANSWERS findings: crit-memfn-forms

## Findings

### ANSWERS-1: the form changes the COMPILE VERDICT at wide windows: I (`--memfn=no-span-loop`, and H(h) with large h) refuses as "pattern too large" patterns that L and the default H(64) compile
- status: CONFIRMED. comb tree (lane/covs2b + subject, 757bc00f7). Pattern file holds `[0-9a-f]{3400}` (no newline).
  `kit.sh comb OUT PATFILE /dev/null --window-search-width=4095` -> PCREC_RC=0 ROUTE=cover LOOPS=1;
  `kit.sh comb OUT PATFILE /dev/null --window-search-width=4095 --memfn=no-span-loop` -> PCREC_RC=1
  "pattern too large: 510342 bytes of emitted code (limit 500000)". Threshold for this class lies in 3000..3400
  (3000 compiles under I). Also `[0-9a-f]{4095}` (I and `--harness=span-head=4094` refused at 612507 B; L, default, H(8), H(64) compile and answer
  SAME vs libpcre2 on 19 subjects), `\b\w{4000}\b` and `\w{4094}\B` with `--features all` (I refused at ~1.02-1.05 MB; default/L/H(8)/H(64) SAME).
  Expected (the promise's lens "answer-identical across forms"): every form yields the same answer for every pattern, or the
  spec names where a form refuses.
- severity: answer (the caller-visible verdict compiled/refused differs by form; no wrong match was seen)
- effort: S (state it) to M (budget the I text, or make the refusal form-independent); blast radius: only `--window-search-width` >= ~3000 on the landing tree (default width 32 cannot reach it); the deny option, the axes sweep's I cell, and the cards' H(h) for h near the width (C1/C2 cannot time H(h) where it is refused).
- where: memfn/src/window.c wf_span_head / wf_test_to (I renders every position inline); the 500000-byte emit cap (src/core/limits.def); r45_reply rev 6 §3 "The option" and "Answers, controlled by G2" say nothing about a form-dependent refusal.
- argument: the deny `no-span-loop` is documented as "today's text"; today's text at width 4095 is exactly what the emit cap refuses, so the deny is a refusal switch at wide widths, and any answer-identity sweep at those widths (axes cell I vs default) will report a refusal, not an answer. Either the spec names it (I at wide widths may exceed the emit cap) or the axes/cards matrix bounds its widths. Ruling D198 add. 1 ("the width limit bounds the route") is the hook: the width limit could be set so that I never crosses the cap, or the cap is acknowledged per form.

## PROBED-AND-HELD

Method: kit/kit.sh only (plus one ASan copy of tests/kitproof/drv.c, below). Each "subject line" is drv's full
answer: rx_search at EVERY startoffset 0..n plus the find-all loop, compared to libpcre2 (kit's SAME/DIFF), and
the raw pcrec answers of all forms of one case compared byte for byte (sha1 per run). Every emitted a.c's
`Pattern:` header was checked against the case's pattern file. Driver: ANSWERS/run.py, ANSWERS/gen.py,
case files ANSWERS/cases{1,2,3,4,5}.py, results ANSWERS/m{1,2,3,3b,4,5}/results.jsonl and m*.out.
Budget used: 537 kit compiles in the matrices + ~45 single-pattern route probes + 11 ASan gcc builds (~593, cap 600).

Totals over the matrices: 98 cases, 470 compiled runs (67 refused: 61 "requires module" before I added
`--features all`, re-run in m3; 6 emit-cap refusals = ANSWERS-1), 234 runs whose a.c holds at least one span
loop, 25,963 subject-line answers SAME vs libpcre2, 0 DIFF, 0 cross-form answer differences.

- (a) subject tree, default width 32, forms default / I / L / H(1) / H(16) (+ H(24), H(h) at stretch edges):
  hex/digit/\w/./[^a]/[^\n\r]/[ab]/[ac]/[abc]/[[:xdigit:]] repeats 16..32; caseless (-i, oracle i) hex and
  literal+digit; utf8 (-e utf8, oracle u) \w, hex, [^x], literal é + digits; mixtures (`[a-z]{5}[0-9]{5}...`,
  `[0-9]{3}[0-9a-f]{20}`, `[a-z]{12}[0-9a-z]{3}[a-z]{12}`, `[0-9a-f]{10}x[0-9a-f]{10}`); non-core neighbours
  `\w{32}\B`, `\w{31}\B`, `\b[0-9a-f]{30}\b`, `\B[0-9]{29}\B`, `\b\w{20}\b` (also utf8, caseless),
  `(?m)[0-9]{10}$`, `[a-z]{10}\b[0-9 ]{3}`: all SAME, all forms identical. Default == I byte-for-byte in answers
  and LOOPS=0 at width 32 on every case (the "nothing moves at 32" ruling holds on answers).
- (a) comb tree at widths 40, 64, 65, 100, 128, 256, 1001, 4095 under default / I / L / H(1,2,8,16,24,29..39,
  59..71,98..100,127,150,999,2000,3999,4093,4094): `[0-9a-f]{40,63,64,65,100,4095}`, `\b[0-9a-f]{40}\b`,
  `\w{64}\B` (w65 and w128), `\B[0-9]{99}\B`, `(?m)[0-9]{70}$`, `[^\n]{200}`, `[0-9]{1000}x`,
  `[0-9]{4094}x`, `[a-z]{2000}[0-9]{2000}`, `[^a]{4000}b`, `\b\w{4000}\b`, `\w{4094}\B`, utf8 `\w{80}`,
  `\b\w{100}\b`, caseless `[a-f]{100}`, `[a-z]{30}[0-9]{40}[a-z]{30}`, `\d{64}\d{64}`: all SAME.
- Subjects per case (gen.py): exact match touching START and END, +1 before/after, doubled/tripled hits, the
  match truncated by one at the end, a non-member at offsets {0,1,2,h-1,h,h+1,L/2,L-2,L-1} for heads
  1,2,8,16,24,32,64, dense near-miss ((k-1 members + non-member) x3, both phases), miss-heavy, random with
  planted hits; long patterns (>=1000) a reduced set (bad byte at 0,1,7,8,9,63,64,65,L/2,L-2,L-1 and the
  stretch edges).
- (b) the skip entry: loops observed to start right after an E-find skip at offset 0 (`\d{8}\d{8}` [1,16),
  `[0-9]{10}[0-9a-f]{10}` [1,10)) and end right before one at the last offset (`[0-9a-f]{32}` [0,31),
  `.{25}` [0,24)); head straddles that split a stretch into inline prefix + loop (H(16) on the mix case, H(9..12)
  on `[a-z]{8}[0-9]{3}[a-z]{8}`, H(29..31,69..71) on the comb a30d40a30); stretches abutting a different-set
  stretch ([0,12)[12,15)[15,26)); a head inside a 1-entry tail (no loop, correctly). All SAME.
- (b) the hoisted bound / reads past the end: 11 L artifacts (hex32, [^\n\r]{30}, .{25}, the mix,
  \b[0-9a-f]{40}\b, \w{32}\B, a12x3a12, h20n5, [0-9a-f]{4095}, \w{4094}\B) rebuilt with -fsanitize=address
  against a copy of drv.c that gives each subject an exact-size malloc buffer (ANSWERS/asan/drv_asan.c): 0
  ASan errors, answers byte-identical to the kit's. Loop text at 4095 (`size_t j = 0; j < 4095`, `%d`) compiles
  and answers SAME.
- (b) negative offsets: never loop by construction (head >= 0; off < head returns 0); lookbehind/lookahead patterns
  route `unanchored` (no window search) in both trees, so no witness reaches a negative core offset beside a loop.
- (b) C-table offers (`table`) inside a loop: NOT REACHED. pcrec offers window tables only on the prefilter's
  reseed/parked spans (emit_dfa.c pf_window_of, find_window), one position each with a per-offset table id;
  ~25 route probes found span loops ONLY on the `cover` route, whose spans carried no table. By reading,
  wf_loop_len breaks on a table change and wf_loop renders through wf_member_of with entry i's table, so a
  loop is answer-identical to its inline positions; untested at run time.
- Patterns the prompt named that never reach a loop in either tree (route `unanchored`): `x[a-z]{20}y`,
  `x[a-z]{100}y`, fixed-width alternations, the UUID shape, `[a-z]{12}(?:[0-9]{8}|[A-F]{8})`. Not a defect; it
  bounds what this differential covers.
- Randomized sweep (cases5.py, seed 4517): 9 subject-tree + 4 comb(128) concatenations of 2-4 class/literal
  segments under I, L and two random H(h): 52 runs, 24 with loops, 2,896 subject lines SAME.
- Harness note: my first m3 batch wrote the shared pattern file concurrently and compiled an empty pattern for
  3 runs of `\w{32}\B` (caught by the cross-form hash and the header check); fixed in run.py and re-run (m3b).

CRITIC COMPLETE

