# memfn ideas log — raw observations of possible optimizations

Append-only, newest at the bottom. Entries are UNEDITED observations as they
were noticed: a pattern, what the kit emitted, and what might be better. None
is a request, a plan row or a decision. Each waits to be evaluated later
against a measured trigger (D77). When one is evaluated, add a dated
`-> evaluated:` line under it (filed as R-n / plan row X, or dropped and why).
Never rewrite the original text.

Format: `## YYYY-MM-DD — short title`, then the observation, the evidence
(pattern, build, emitted text), and a first guess at impact.

## 2026-10-10 — vrun end bound uses the run's length, not the pattern's minimum remaining length

Seen while answering Frank's questions about vrun-w32 (lane/memfn-r13 build,
`build/pcrec -p rx -fmemfn-simd`). `(?i)cat\d{20}` emits the same end guard as
`(?i)cat`: `if (i + 2 >= n) return n;` (scalar body `cand + 2 >= n`), even
though no match can start in the last 22 bytes. The scan stops at the RUN's
span, not at the pattern's minimum length from the run's start to the
pattern's end. Using that minimum would stop the search earlier and skip
candidates the matcher rejects anyway.
- Answers: unchanged (pure early-out).
- Saving: at most ~min-length bytes of tail per search call. It matters for
  many short subjects with a long fixed tail; it is negligible on long
  subjects.
- It is a general fact, not a vrun one: every search form (scalar and SIMD)
  could use it. Under D157 pcrec would supply it to the kit as a FACT, e.g.
  "min bytes from run start to pattern end", so it starts as a request from
  main.
- First guess: low impact; a BOONIES-class row unless a short-subject
  workload shows it.

## 2026-10-10 — vrun with a repeated byte emits duplicate constants in the C text

`(?i)azzb`: the kit picks KA = `z`@2 and KB = `z`@1 and declares
`ma/va/mb/vb` with the second pair identical to the first. gcc -O2 -mavx2
merges them (one mask register ymm3, one compare register ymm2 for both
loads), so there is no machine-code cost. The cost is text only (artifact
bytes, readability). It could be cleaned up in the kit's renderer if a text
size budget ever needs the bytes.
- Related: when the two picks are the same byte at adjacent offsets
  (`zz`), the second filter still pays for itself (it needs `zz`, not
  just `z`). Worth checking whether the ranking ever picks the same byte
  at a far offset, and whether a different second byte would filter better.

## 2026-10-10 — plain-case literals take no vrun form

`qeeeez`, `azzb` (no `(?i)`): `MEMFN_FORMS "none"`; they stay on the existing
scalar/libc path (memchr on one byte). vrun's two-position vector filter
might beat memchr when the first-picked byte is common in the subject. Open:
was plain-case excluded from batch 1 deliberately (memchr/memmem already
strong), or is it simply not reached yet? Check integration.md §R4.9 before
evaluating.
-> evaluated 2026-10-10: answered, deliberate. integration.md §R4.9.7.1
   ("the glibc-inside trap") excludes `fn-memchr` bodies from batch 1. A
   case-sensitive run scans ONE byte (pcrec's rarest pick: `z` at offset 5 in
   `qeeeez`) with glibc `memchr`, which is already SIMD inside, picked by
   CPU at load time. There is no measured cell showing a w16/w32 row beating
   it. The form is FILED as the `vrun` over `fn-memchr` row, with three
   trigger cells: exact window with a rare pick, exact window with a dense
   pick, and OFS run-pinned (`/user|/users`). This entry adds nothing new
   beyond that row.

## 2026-10-10 — a vector filter over a byte plus a class at another offset (ipv4 shape)

Frank's question: what if the picks differ, e.g. `.` plus a digit (an ipv4
regex)? Can the class be checked in SIMD?
- What pcrec emits today (lane/memfn-r13 build, `-fmemfn-simd`):
  - `[0-9]\.[0-9]`: OFS `offset-set`. A scalar `memchr('.')` runs, then a
    256-entry table checks the byte before it for a digit (`rx_ofs_k0`), and
    each failure restarts `memchr`. `MEMFN_FORMS "none"`: offset-set is
    out of batch 1 ("set terms only, no run", integration.md §R4.9
    site table).
  - `\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}` and `\b\d+\.\d+\.\d+\.\d+\b`: only an
    entry check that some `.` exists (`!memchr(..., 46, ...)`), then the DFA
    with `byte-class` prefilter and inline digit-run loops
    (`(unsigned)(c - 48) <= 9u`). There is no candidate filter that combines
    `.` with digits at all.
- The vector form is cheap:
  - A range class is 3 ops per block in SSE2:
    `t = sub_epi8(x, '0'); cmpeq(min_epu8(t, 9), t)`.
  - A small union of ranges is a few more.
  - An arbitrary class is a nibble-table shuffle (pshufb lo/hi lookup, AND):
    SSSE3+, so a w16-level question.
  - Combined per block: `cmpeq(load(i+k), '.') & digit(load(i+k-1)) &
    digit(load(i+k+1))`, then movemask, then verify. This is the vrun shape
    with cubes generalised to classes.
- Why this may beat the scalar twin even though `.` alone is the glibc trap:
  `.` is DENSE in text, so scalar `memchr('.')` restarts on every dot that is
  not between digits. The vector filter rejects those in-register. That is
  the same restart-churn argument that made `fn-pair` batch 1's site.
- Two layers:
  - Kit: a set-capable vrun (class predicate per position) over OFS
    offset-set FUNCs, which already exist.
  - pcrec: for the ipv4-style patterns there is no such site today, only
    "a `.` exists". pcrec would have to state a multi-position
    candidate fact (D157) for the DFA prefilter.
- First guess: medium for log/text scanning workloads (ipv4, dates
  `\d+-\d+`, versions `\d+\.\d+`). Needs a dense-dot cell to judge against
  memchr + table.

## 2026-10-10 — hold the candidate mask across calls (dense subjects, wide registers)

Frank: in a dense subject one w32 block can yield several candidate bits.
Keep the mask after returning a candidate. The next search then pops the
next bit instead of reloading, and once the mask is empty it resumes after
the BLOCK, not after the candidate.
- What already happens WITHIN one call: candidates that fail the run verify
  are rolled off the mask (`while (m) { ...; m &= m - 1; }`), and an empty
  mask advances `i += 32` to the next block. The idea is only about what
  is lost when a candidate VERIFIES and the FUNC returns it: the rest of
  the mask is discarded, and the next call from `cand + 1` reloads and
  recompares the same block.
- Where that loss happens today (lane/memfn-r13 build): nowhere inside a
  search. Every batch-1 vrun site is called ONCE per `rx_search`. On the
  DFA route it is a skip to the first candidate, after which the DFA scans
  itself (`(?i)cat`: `handoff_position = rx_reqrun(...)`). On the VM routes
  it is an entry existence check (`(?i)\d+cat --engine=vm`:
  `if (rx_reqrun(...) >= subject_length) return 0;`). integration.md's
  site table marks these INFREQUENT.
- Where it would matter:
  - FREQUENT sites, where a FUNC is re-called inside one search loop.
    Example: OFS `<p>_ofsskip` on every DFA re-seed (`/user|/users`),
    which is the filed vrun-over-fn-memchr / offset-set territory (entry 4).
    Without a held mask a dense subject redoes up to 32 bytes of compare
    per candidate, i.e. work O(n * density) instead of O(n).
  - Global iteration ACROSS `rx_search` calls (all matches in a buffer):
    each call starts fresh. Holding the mask there means caller-held state,
    which is a public-API question (a cursor / iterator entry), not a kit
    one.
- Shape: the FUNC gets a small cursor `{ size_t blk; uint32_t m; }`. On
  entry with `pos`: if `pos` is inside the held block, mask off the bits
  below `pos` (`m &= ~0u << (pos - blk)`) and pop. Otherwise reload. The
  stale-state rule is that the subject and `n` are unchanged. The same
  idea applies to the scalar twin: the two-stream body could keep its
  `ha`/`hb` memchr hits across calls the same way.
- It changes the site contract (integration.md §14: FUNCs are pure
  `(subject, n, pos)` today), so it is a pcrec-side change and an abi event
  when a FREQUENT site first adopts it.
- First guess: no value for batch 1's INFREQUENT sites. Real value at the
  first FREQUENT vector site on dense subjects, so evaluate it together
  with entry 4 / the vrun-over-fn-memchr row. The API-level form (cross-call
  iteration) is a separate, bigger question.

## 2026-10-10 — the VM attempt loop's start-set skip: a scalar, re-entered, undelegated prefilter

Follow-up to entry 5 (Frank: "while (notdone) { if s = find_cand then
match(s) }"; the DFA is fine on dense subjects; the VM may still want it).
- The VM's no-DFA search (`(?i)\d+cat --engine=vm`, lane/memfn-r13 build)
  is exactly that loop. After every failed attempt it runs:
  `attempt_position++; while (attempt_position < subject_length &&
  !rx_start_set[subject[attempt_position]]) attempt_position++;`
  This is a byte-at-a-time table walk over the start set (digits here),
  re-entered per attempt. The vrun FUNC (`rx_reqrun`, the `cat` run) runs
  ONCE at entry, as an existence check, and never drives the attempt
  loop.
- This skip is NOT a kit site: it is absent from
  tests/memfn/site_manifest.tsv (PF, PRE, OFS, SETREST, VERIFY, VMRUN, STAY,
  EDGE, VMSPAN, MLINE, VMSTRIDE, N7 delegated; VALID pending). pcrec
  still emits it inline. Delegating it is main's call (DELEG_SITES).
- Candidate forms, in rough order:
  1. a start set of one byte: `memchr` (glibc SIMD);
  2. a small set or range: the vector class test of entry 4 (3 ops for a
     range), with a HELD MASK across attempts (entry 5). This site really
     is re-entered per attempt, so on dense starts (digits in a log line)
     the held mask saves the reload;
  3. use the required run to bound the starts: with `\d+cat`, an attempt
     can only succeed if a `cat` follows. Jumping to the next run hit and
     walking back over the start class is a reverse-anchor idea; pcrec's
     REVEND work may already cover it.
- Frank's "islands" note for the DFA: that is how the DFA prefilter route
  already works. The DFA dies, re-seeds, and the OFS skip FUNC finds the
  next island (the FREQUENT site of entry 5). A held mask helps there only
  when the next island lies in the same block. For one ipv4 per log line
  (~100+ bytes apart) it usually does not, and that is plain memchr /
  vector-scan territory.
- First guess: the VM start-set skip may be the highest-value item in this
  file. It is scalar today, re-entered on every attempt, and
  `--engine=vm` / no-DFA patterns depend on it. Needs a census of how
  often the no-DFA route runs on the bench, and a dense-start cell.

## 2026-10-10 — fixed-length class spans as constructed instruction sequences (Frank, discussion with main)

Pattern shape: a long mixed fixed-length span, e.g. `abc(?i)def\d{3}[a-z]{2}`
(11 bytes, every position a byte set). Today the VM emits one bounds check +
compare + dispatch per byte (the [WORD-FOLD] baseline).

- Per-position form `((x & K) - L) <=u R`: exact byte (FF, c, 0); caseless
  letter (DF, upper, 0); `\d` (FF, '0', 9); `[a-z]` (FF, 'a', 25);
  `[a-zA-Z]` = fold then range (DF, 'A', 25), exact; past the span's end
  (00, 0, 0). One SSE2 block: load, and, sub, min_epu8+cmpeq (or
  subs_epu8 vs R, then zero test), movemask against the span mask, so about
  5 ops for the 11-byte example. SWAR works too, but sub borrows across lanes,
  so it needs the high-bit trick (a few ops more).
- "Single masked interval" is a COMPUTED class property, not a list: for each
  K in 0..255 take the folded image of the class and test whether the
  pre-image of [min, max] is exactly the class (about 64K byte ops per class
  at compile time). `\w` fails (0x7F & 0xDF = '_'); hex fails (two
  intervals). Ladder: one masked interval -> union of k intervals ->
  nibble-table shuffle (shufti, SSSE3, up to 8 distinct classes per span
  with per-position class bits).
- Frank: with mask registers (AVX-512BW k-masks) the explicit mask step goes
  away. vpcmpub has an unsigned-LE predicate (sub + cmp straight to k, no
  min/cmpeq), unions of ranges are kor, and per-position constants ride
  masked ops. VBMI vpermi2b is a 128-entry lookup, which gives an arbitrary
  ASCII class in one op. Some forms that are expensive in SSE2/AVX2 (ORing
  ranges) become cheap.
- Frank's framing: this is not one specific output. It is a SELECTOR that
  CONSTRUCTS the instruction sequence from the span's composition (per-
  position byte sets) plus a COST MODEL per ISA tier (SWAR / SSE2 / SSSE3 /
  AVX2 / AVX-512BW+VBMI). "Needs a spike or something."
- Uses: (1) verifying a candidate after an anchor hit; (2) fusing VM literal
  and class chains (precondition: no live resume target inside the span);
  (3) scan filters through the shift-and-across-blocks shape (ipv4 entry
  above).
- First guess at impact: unknown until a census counts the spans (length,
  per-position rung) over the bench's patterns. Cost-model constants must be
  derived (uops tables per uarch) or measured, never hand-set. AVX-512 is
  not on the bench box (Zen 1), only the dev box (Zen 4).

## 2026-10-10 — rev-end's run loop: a backward vector scan for the first byte OUTSIDE the class

Seen in main's artifacts (abi 74) for `\s+$` / `\w+\z`, answering bench O-96 (b)
(lane o96ans). Once the reverse walk enters its self-loop state, it steps back one
byte at a time over a 256-entry run table:
`while (rewind_position > search_from && rx_reverse_scan2[subject[rewind_position - 1]]) rewind_position--;`.
On a 61,440-byte body that matches from byte 0 this is ~0.354 ns/B
(21.8 us/call on the bench box). It is throughput-bound (no dependent state chain),
inside K87's loop-alignment band.
- A backward vector scan for the first byte NOT in the class (the class test of
  entry 4, complemented, movemask, clz) replaces the loop at 16/32 B per step.
- It is a scan-site shape, so it would be a kit request, not a REVEND edit.
- First guess at impact: only long matching runs to the subject end (trim-like
  `\s+$`, `\w+\z` on long bodies). That is the tail family's whole remaining cost
  (O-96 (b)), but only on one subject per cell.

## 2026-10-11 — a vrun hit is checked three times; verify only what the filter did not prove

Frank, on the KB losses ("they look like overhead; for `cat` the filter is two
thirds of the pattern; does it recheck the whole span?"). Yes. For `(?i)cat`
(lane/memfn-r13 build, `-fmemfn-simd`):
1. The vector filter proves `c` (KA, offset 0) and `a` (KB, offset 1) for
   every set bit.
2. The scalar verify re-reads ALL of `cat` for each bit:
   `(rx_w2(s+cand) & 0xDFDF) == "CA" && (rx_w2(s+cand+1) & 0xDFDF) == "AT"`.
   That is two 2-byte loads, and only `t` is new information.
3. On the DFA route `rx_search` then starts the DFA at state 0 at
   `handoff_position` and steps `c`, `a`, `t` again.
- Ideas, smallest first:
  - Verify only the positions the filter did not cover: for `cat`, just
    `t`. This is kit-local and has no contract change. It only helps the
    KB arm (KB-DENY must still verify `a`), so it moves DEFAULT-KB-DENY in
    KB's favour exactly in the dense-hit regime where KB lost (179 small
    losses, rq4h_report addendum). Re-time before re-ruling.
  - When the run is short enough that the filter can cover every position
    (3 for `cat`), the mask IS the verify. The cost is an Nth load + AND
    per block, against zero verify per hit. rankuse §5 already files "N >= 3
    positions"; this is its natural trigger cell.
  - Hand the DFA a state AFTER the run (start at `cand + len` in the state
    reached by the run) instead of re-stepping it from state 0. pcrec-side,
    cheap per hit, and it matters only for dense hits.
- Note: (2) is shared by every SIMD arm and by the scalar body, so it is
  part of the pc16 per-call loss against OFF as well.

## 2026-10-11 — from the vrun loss survey: KB off when KA is very rare at w32 (hypothesis)

Lane losssurv (report kept at worktrees/memfn-slot/losssurv/report.md;
read-only over slot20/slot21). This is the one emit-time predicate with a
reason behind it. At w32, render KA alone when 32 * rank_ppm[KA] / 1e6 <
theta, with theta about 0.035 (rank_ppm[KA] up to ~1,100). KB costs a fixed
load + AND per block and pays only through the KA false candidates it
removes. When KA almost never fires, there is nothing to remove. Support is
ONE cell (`sp`, `(?i)azqb`), with v17 at break-even. Promoting it needs a
ladder of cells whose KA rates span ~1k-11k ppm, timed at w32. Frank ruled
2026-10-11: accept the survey, build nothing now.

## 2026-10-11 — 16-byte calls under w32 pay ~0.3 ns, systematically

Survey residue. At w32, 26-30 of 41 cells lose about +0.3 ns on pc16 in
BOTH runs (at w16 it is a coin flip). Unverified guess: a 16-byte call
under the w32 dispatcher goes through two nested length checks, `__w32`'s
`n - pos < 34` and then `__w16`'s `n - pos < 18`, before reaching
`__body`. One check that routes straight to the body for spans below the
smallest arm's minimum may remove it. Cheap if true; check the emitted text
first.

## 2026-10-11 — pcrec could tell the kit more of what it already knows about the workload (density and more)

Frank: the survey's unexplained losses are mostly about the SUBJECT, which
the kit cannot see. pcrec could pass more of what is known about it as
facts (D157: facts, never methods). Today the only prior is `rank_ppm`,
each candidate position's byte rate from a reference profile. Examples of
facts that would have split the losses the survey could not:
- **Hit density / candidate density prior**: expected run (or KA) hits per
  KiB, beyond the per-byte rate. KB at w32 loses +3..+9% on dense-hit
  subjects and wins 30-45% on sparse ones. Same cells, same kit facts; only
  density separates them.
- **Subject-length class**: typical call span (short calls of 16 bytes vs
  1 MiB scans). pc16 losses (entry above) and the w16-vs-w32 cut-over both
  depend on it. A caller that only ever matches short fields would want
  the scalar body.
- **Alphabet / byte-frequency profile of the actual workload**, not a
  generic text prior: the `(?i)azqb` w16 loss (+33..+83% on sparse subjects,
  -75..-95% on dense) flips on whether `z`/`q` are rare in THIS data.
- **Call pattern**: first match only vs all matches (find-all). A held
  candidate mask (entry 5) pays only under find-all, and re-entry
  (REQ-HANDOFF-L1) changes which sites are hot.
- **Min bytes from run start to pattern end** (entry 1) and the post-run
  DFA state (2026-10-11 entry). These are pattern facts pcrec already has.
Where the data could come from: pcrec already has a measured source.
`pcrec-analyze` (analyze/, [FINDINGS] B6) counts an exemplar file into an
`analysis` bundle (shipped `log` / `weblog` bundles). A user-supplied
exemplar, or a named bundle (`--analysis NAME`), could carry the density,
length class and byte profile into `mf_pred`, the same way rank priors
travel. The kit's distance rules then pick per workload, not per guess.
- Shape: new `mf_pred` fields (an `MF_SITE_ABI` bump, a request to main).
  Unset = unknown, and the kit falls back to today's rule (no silent
  defaults: unknown is a stated value, not a guess).
- First guess: medium-high value if users supply exemplars. It turns
  "accept the residue" into a choice per workload. It needs a [FINDINGS]
  owner decision about what a bundle carries; that is main's design.

## 2026-10-11 — a "memcasecmp" for runtime folded spans (caseless backreferences and variables)

Frank asked whether there is a memcmp replacement for folded spans.
- CONSTANT folded runs (a `(?i)` literal) are served: runcmp's `words` row
  renders masked word compares, e.g. `(rx_w8(s+cand) & 0xDF..DF) ==
  rx_w8("JKLMNOPQ")`, and R-14 adds the padded single word inside vrun.
- RUNTIME folded spans are not. The byte-encoding caseless backreference
  (`(?i)(\w+) \1`, current main build) calls `rx_span_match_caseless`, a
  per-byte loop with two branchy A-Z folds and a compare per byte. It
  returns the first mismatch index as `-(i)-1`. It is an encoding residual,
  not a kit site.
  - Filed so far: only the utf8 ASCII fast path ([MEMFN-CI-ASCII],
    D147 add. 14, trigger: a measured cell) and [BREF-FOLD-ONCE]
    (boonies). The byte-mode loop itself is not filed.
- Obvious form, SWAR first (D144):
  - Load 8 bytes of each side.
  - Fold A-Z in-register with the classic range test:
    `((x + 0x3F..3F) ^ (x + 0x25..25)) & ~x & 0x80..80` marks A-Z, then
    shift right by 2 to get 0x20 per marked lane, and OR it in.
  - XOR the two folded words. If nonzero, the first mismatch index is
    ctz/8 (little-endian).
  - Finish the tail bytewise, with the subject-end guard handled exactly as
    today.
  - SIMD (16/32 lanes: cmpgt range mask, OR 0x20, cmpeq, movemask) as a
    later candidate under -fmemfn-simd.
  - It must keep the contract: the first mismatch index, and the miss when
    the subject ends.
- First guess: niche (caseless backrefs/variables are rare in the bench).
  It becomes worth it when a measured cell shows the compare cost. The same
  trigger as [MEMFN-CI-ASCII], so file them together. If delegated, it is a
  kit site (a byte-domain masked span compare), which is main's call
  (DELEG_SITES).

## 2026-10-11 — a fixed-width MIXED span compare: bytes, folded letters and classes in one vector test

Frank: given a static span of mixed items, e.g. `abcd[0-9]{4}(?i)xyz` (11
positions: 4 exact bytes, 4 digits, 3 folded letters), load the stretch
once, mask to fold or hide what needs it, do one compare, and check the
class positions with a parallel range test. "More than memfn's usual, less
than a bit-vector regex engine."
- Unifying observation (kit manager): every position kind is a MASKED
  RANGE.
  - exact byte b: mask 0xFF, range [b, b];
  - folded letter: mask 0xDF, range [B, B];
  - a contiguous class such as `[0-9]`: mask 0xFF, range [0x30, 0x39];
  - a folded range such as `(?i)[a-f]`: mask 0xDF, range [A, F];
  - don't-care and lanes past the span: range [0, 255].
  So one per-lane formula covers the whole span, with constant vectors
  M, LO and W = hi - lo:
  `t = sub(and(x, M), LO); ok = cmpeq(min_epu8(t, W), t)`, then movemask
  == all-ones. On SSE2 that is 4 ops + movemask for up to 16 positions; at
  w32 it is 32 positions. Today's padded word (R-14) is the special case
  W = 0.
- What the unification does not cover: non-contiguous sets (`[aeiou]`,
  `[\w-]` as several ranges). Those take a nibble-table shuffle (pshufb,
  SSSE3+; vtbl on NEON), or a two-range OR when there are only two ranges.
- The arch arms differ completely, as Frank expects, which is why the
  method stays the kit's:
  - SSE2/AVX2: the min_epu8 trick (no unsigned byte compare);
  - AVX-512BW: `vpcmpub` with per-lane predicates straight into a k-mask;
  - NEON: `vcleq_u8` directly, `vtbl` for sets;
  - scalar SWAR: the same masked range on 8 lanes with borrow isolation,
    exact for 7-bit data.
- Where it plugs in, smallest first:
  1. As the VERIFY of a candidate the kit already found (vrun / memchr),
     when the run grows into a fixed-width span around the anchor. A date
     `\d{4}-\d{2}-\d{2}`, a UUID or hex id, a timestamp or a log prefix
     becomes one load + one span test per candidate instead of a DFA or
     VM walk over those bytes.
  2. As the candidate FILTER itself: the vrun shape with KA/KB generalised
     from cubes to ranges (entry 4, the ipv4 `.` + digit case, is the
     2-position version).
  3. Not a matcher: the span must be fixed-width and contiguous. `\d+` or
     alternation ends it. That is the line between this and a bit-vector
     engine (shift-and / Glushkov), which handles variable width but is
     an engine.
- What pcrec would have to state (D157 facts): today a run is a sequence of
  CUBES (mask + value), with the classes elsewhere (SETREST / offset-set
  terms as separate predicates). The span form needs ONE fact: a fixed-length
  sequence of per-position byte sets, anchored at a known offset from the
  candidate. That is a new `mf_pred` shape (an `MF_SITE_ABI` event and a
  request to main). The kit classifies each set (masked range / two ranges
  / table) and picks the arm.
- First guess: potentially high value for log/structured-text workloads (the
  same family as entries 4 and 6, and the [REQ-HANDOFF-L1] ipv4/ipv6/dotted4
  cells). It is a design item (contract shape, pcrec facts, D6 panel)
  before any build, triggered by a measured cell where verifying a
  fixed-width structured token is the cost.
- Follow-up the same day (Frank): with ANCHORED CORES (from a required
  literal, extend through each neighbouring repeat's MANDATORY part only:
  `\d{2,3}\.\d{2,3}` has the core `\d\d\.\d\d` at -2..+2 from the `.`), a
  bounded-repeat token becomes a short sequence of span tests:
  1. try the core span;
  2. on a miss, try again shifted by one digit (the {m,n} slack);
  3. eat `\d?\.`;
  4. repeat 1-2 for the next group;
  5. eat the trailing `\d?`.
  Kit manager's addition: ipv4's maximum width is 15, so the WHOLE token fits
  one 16-byte load. Classify the window once into per-class bitmasks (D =
  digit lanes, P = dot lanes; pshufb or the masked range), and the steps
  above become bit arithmetic: the digit-run length before a dot is
  `ctz(~D >> p)`, then check 1 <= len <= 3, P at the next bit, and so on,
  with no reloads. That is the simdjson "classify, then reason on masks"
  pattern, sized to one token.
  - Semantics: leftmost-first start (`1234.5.6.7` matches from `234`)
    falls out of choosing the earliest start whose run lengths fit. The
    captures and the exact end follow greedy {m,n}.
  - Where it sits: this is no longer a fixed span compare. It is a FINISH
    or verify form for a bounded token (D156 LOCATE x FINISH). Either pcrec
    renders it, or pcrec states the token (a sequence of (set, m, n)
    items, max width <= register) as a new fact and the kit renders it.
    That is a design question for main, and its trigger is a bench cell
    where such a token's finish is the cost (the R-15 ipv4/ipv6/dotted4
    cells are the obvious first look).
  - The survey (lane spansurv) also counts these BOUNDED TOKENS: max width
    <= 16 / 32, the number of distinct sets, and the slack sum (n - m).
- Kit manager's note the same day: the fixed-length class span above IS
  plan.md [SPAN-ISEL]'s "special case, the original filing" (Frank,
  2026-10-10: per-position byte sets as a pcrec fact, a kit-side selector
  builds the check). These entries add the masked-range unification, the
  anchored cores and the bounded-token walk to it; they do not open a new
  row. [SPAN-ISEL] is SAVED FOR LATER, after the low-hanging fruit (Frank).
- Frank, on the bounded-token walk: it is a FOURTH engine type, the VM
  analog to the vector engine's DFA analog. The two axes:

  | | simulate a set of states (no backtracking) | control flow per candidate (choices, greedy, captures) |
  |---|---|---|
  | sequential over bytes | DFA (shift-and is its state-bit form) | the backtracking VM |
  | parallel over positions (class bitmasks) | the bitstream engine, [SPAN-ISEL] / [Cam14+] (MatchStar, Advance) | classify once, then walk the masks (this entry) |

  Both position-parallel cells share stage 1: classify a block into per-class
  bitmasks (SIMD compares + movemask). They differ in stage 2: the bitstream
  engine is straight-line bit algebra over all positions and outputs match
  ENDS (a LOCATOR in D156's locate x finish). The mask walk is control
  flow on one candidate's masks and outputs the leftmost-greedy span and
  captures (a FINISHER). So they complement each other: bitstream locate,
  then mask-walk finish. The interim wins (span verify, class filters,
  ideas entries 4 and 6 and this one) all build stage 1, so they are
  groundwork for either engine, not throwaway.
- Survey result (2026-10-11; lanes spansurv and spansurv2, read-only; reports
  kept at worktrees/memfn-slot/spansurv/), over pcrec-bench (336 patterns)
  and the test corpus:
  - STRICT fixed spans: 38 bench patterns. loglines uuid (36), hex32-id
    (32), iso-ts (19) and http-5xx (14) cover ~36% of loglines cells, plus 6
    `wild-*` capability patterns. Mostly the FILTER form: uuid, hex32 and
    iso-ts have no req_run, and only 9 of 41 spans contain the anchor.
    Tiers: masked range alone 44%, +1 ORed range 80%, table 20%.
  - ANCHORED CORES: 28 bench patterns, 2,884 cells, and 26 of the 28 are
    VERIFY-READY today (anchored on pcrec's stated req_run or req_byte).
    New over strict spans: bounded/dotted4, float-literal-bound,
    tail-ext-lower-txt and 5 syntax cells. Cores are short (3-5 positions)
    = verify-after-candidate.
  - NOT reached by either: loglines/ipv4 (unequal-width octet
    alternations) and loglines/ipv6 (a top-level alternation).
  - BOUNDED TOKENS (max width <= 32): 46 bench patterns, 4,820 cells, but
    realworld only loglines/bignum (`[0-9]{10,19}`). Only 5 tokens use
    exactly 2 sets. A full ipv6 is max 39.
  - Facts gap: pcrec states exact/cube bytes only; `kset_walk` covers the
    leading path up to 24 offsets and stops at an any-byte. The kit needs
    per-position sets at an offset from the anchor (-26..+90 measured) and
    a union-vs-exact flag.
- Frank, same day: negated classes belong in a span too (`[^a]`,
  `[^\d]`, `[^"]`). In the masked-range form a negated range is ONE more
  op: a per-lane invert vector N (0xFF on negated lanes, 0x00 elsewhere),
  `ok = cmpeq(min_epu8(t, W), t) ^ N`. So the complement of any single
  masked range is tier A, not tier B. That moves the survey's `[^"]`-style
  spans from B to A and raises the "masked range alone" share above 44%.
- Frank's ruling (2026-10-11): gather information, but the span work does
  not take kit build time; better candidates come first. Everything here
  goes to an UNSCHEDULED item under [SPAN-ISEL]: the surveys (done), the
  ideas above, and a DESIGNED SPIKE to put real numbers on it.
  - The spike: on loglines/uuid, hex32-id and iso-ts (the strict-span
    filter form) and on bounded/dotted4 (the anchored-core verify form),
    time today's search against a hand-written span filter/verify (SSE2
    and AVX2, masked range + invert), at tier U, both layers.
  - It needs no pcrec change (hand-written twin, the rlhtwin way). Run it
    when a quiet box and spare capacity coincide. It is not scheduled.
- Frank's better form for negation (same day): treat the complement as a
  WRAP-AROUND range. `[^lo-hi]` is the range [hi+1, lo-1] mod 256, so use
  LO = hi+1 and W = 255 - (hi - lo + 1), with the subtraction wrapping
  mod 256. Then it is the SAME `t = sub(and(x, M), LO); ok = cmpeq(min_epu8(t,
  W), t)` with different constants: ZERO extra ops, and no invert vector.
  Every lane is then one formula: exact, folded, range, folded range, and
  their complements; don't-care is W = 255. Edge cases fall out modularly
  (`[^\x00]`, `[^\xff]`). With mask 0xDF a folded complement such as
  `(?i)[^a]` stays exact, because only 0x41/0x61 map to 0x41 under 0xDF.
  This supersedes the XOR form above.
- Frank, same day: `abcd(\d{4})` must not split at the group. A span is
  "prove a run of x bytes", and capture boundaries inside it are just
  constant OFFSETS (group 1 = [cand+4, cand+8)). So a fixed-width span also
  FINISHES its own captures with no walk. Checked: the survey's parser
  (spanlib.py: capture groups parse to ('grp', body) and are emitted
  inline) already treats groups as transparent, so its counts did not split
  at captures. For the pcrec fact design, the span (and pcrec's own run
  extraction) must be computed THROUGH groups, with the capture marks
  stated as offsets in the span, not as span boundaries.

## 2026-10-11 — the VM reads precomputed class truth vectors instead of testing bytes

Frank: for ipv4-like patterns, run two wide "proofs" over a stretch of the
subject: A = "is `.`" and B = "is a digit", each giving a truth vector (one
bit per position). The VM then looks up the bit for the current position
instead of re-testing the byte every time it visits it.
- One test: no gain. `(D >> (p - blk)) & 1` costs about the same as
  `(unsigned)(c - '0') <= 9`.
- Where it does gain:
  1. RUNS: "eat `\d+`" or `\d{1,3}` becomes `ctz(~D >> p)`, one op for the
     whole run instead of a byte loop (the VMSPAN/VMSTRIDE advance sites);
  2. RE-VISITS: backtracking and the attempt loop re-test the same positions
     many times, and the classification is paid once per block;
  3. EXPENSIVE classes: large sets, `\w` tables and utf8 classes cost more
     per test than a bit lookup.
- Why it differs from the per-call SIMD advance that was measured to lose on
  short spans (integration.md: AVX2 without a 16 B tier costs 8-16 ns at
  16): there the vector setup is paid on EVERY call. Here a block is
  classified ONCE, lazily, the first time the VM touches it, and the masks
  stay valid for every later instruction and attempt in that block. The
  cost is amortised over the search, not per instruction.
- Costs and limits: classifying a 64-byte block per hot class even if the VM
  visits only a few positions in it (the prefilter often lands the VM on a
  short match); keep it to the classes the program actually tests in loops;
  block-boundary handling; k classes x n/64 words of state (or a small ring
  of recent blocks).
- Placement: pcrec's VM (engine work), or the kit if the VMSPAN/VMSTRIDE
  advance sites gain a "cached block mask" contract (the site would need
  state across calls, like entry 5's held mask). Either way it is the
  fourth-engine idea (classify once, walk masks) applied to the whole VM,
  not just to one bounded token.
- Ruling context: the span thread is UNSCHEDULED under [SPAN-ISEL] (Frank,
  2026-10-11). This entry joins it. The designed spike could add one cell:
  ipv4 through the VM with and without cached digit/dot masks.

## 2026-10-13 — exact repeats hide literal runs and spans from the analysis (`A{4}` vs `AAAA`)

- Observation (manager probe, abi 76): `AAAA` and `A{4}` compile to the same
  DFA table, but only `AAAA` gets the required-run fact (memchr+memcmp
  search start) and the VM's single literal compare; `A{4}` gets a plain
  memchr start and a counter-rung span loop.
- Why it matters to the kit: any span or run delegated to the kit is only
  as long as pcrec's analysis reads it. An exact repeat of a fixed-width
  atom (`b{3}`, `[0-9]{4}`) is a fixed-width span member today's analysis
  does not see, so the mixed-span entry (2026-10-11) would miss
  `abcd[0-9]{4}` written as a counted repeat unless the reading is fixed.
- pcrec row: [REPEAT-RUN] (filed for Frank's later review). Span thread
  stays UNSCHEDULED under [SPAN-ISEL].
## 2026-10-12 — R-18 anchor choice: a rarer far span against its overshoot (Frank)

- Frank's case: three spans with overshoot 0, 20 and 100. The third span has
  the rarer bytes, but anchoring on it costs more. How do we weigh that, given
  the cost may depend on how expensive span 1's scan is?
- Overshoot is the SLACK, `omax - omin` (window_contract.md §2), not the
  distance. So a span-3 hit at p places the origin anywhere in a 100-byte
  range, and finding it means a back-search for span 1 over about 100 bytes.
- Per subject byte, roughly:
  - direct on span 1: `c1(f1) + f1*V`;
  - span 3, then back to span 1: `c3(f3) + f3*(W3*b1 + V')`, with W3 about
    the overshoot (100).
  Here `c(f)` is a scan form's cost at hit frequency f (it rises with f), `b1`
  is span 1's per-byte cost over a short back window, and V/V' are the rest
  of the verify (V' skips span 3, a proven fact, D161 add. 8).
- Span 1's cost appears on BOTH sides: as the forward scan c1, and as b1
  inside every back window. A costly span 1 (a wide set) therefore favours the
  far anchor, since its cost is then paid only f3 of the time. A cheap span 1
  (memchr of a rare byte) favours direct. Span 2 (window 20) is the middle
  choice when f2 is close to f3.
- The ascending, no-repeat stream (D161 add. 7) adds little in find-all: no
  byte is scanned twice. It does mean bookkeeping, overlapping back windows to
  merge, and up to W bytes scanned past the first answer when the caller stops
  early. That is the only regime-sensitive term, bounded per call, and it
  matters only for subjects near W in length.
- All the inputs are known at compile time: frequencies always arrive (D162
  add. 2), the kit has its own form costs (D161 add. 6), and the overshoots
  are stated. So this is the kit's priced choice over 1-2 link chains, as rows
  of one table, not a special rule.
- Twin cell for R-18 (twin first): spans at overshoot 0/20/100; f3 swept;
  span 1 as memchr vs a set FIND; the crossover read on both layers.

## 2026-10-12 — the mixed span test without a subtract: XOR, AND, saturating compare to 0 (Frank)

Follow-up to the 2026-10-11 mixed-span entry, from Frank's discussion of
`(?i)abc\d\d\dxyz`. He proposed folding the letters with a mask and checking
the `\d` lanes with no extra subtraction.
- Masking a digit lane to its low nibble alone (`x & 0x0F <= 9`) is NOT
  exact. It also accepts every byte whose low nibble is 0-9 (`@`, `A`..`I`,
  `P`..`Y`, `` ` ``, `a`..`i`, `p`..`y`, controls). The high nibble must be
  pinned too.
- Frank's refinement pins it: the letters already compare against a constant,
  so that compare also requires the digit lane's upper nibble to equal 0x3.
  Per lane, with constant vectors C, M, W:
  `t = (x ^ C) & M;  ok = (t <=u W)`.
  - Letter lane: C = the letter, M = 0xDF, W = 0. `a ^ A` is 0x20, so it is
    exact.
  - Digit lane: C = 0x30, M = 0xFF, W = 9. XOR leaves 0-9 only for
    0x30-0x39; every other byte keeps a nonzero high nibble.
  - Exact byte: C = b, M = 0xFF, W = 0. Don't-care lane: W = 0xFF.
- SSE2/AVX2 (no unsigned byte compare):
  `u = subs_epu8(t, W); ok = cmpeq(u, 0)`, then movemask against the span
  mask. The saturating subtract by W is the "mask out the digit's low
  nibble" step; what remains is a compare to the constant 0. That is 4 ops
  plus movemask, with no subtract by '0'.
- AVX-512BW: `vpcmpub` LE against W straight into a k-mask (3 ops). The
  no-subtract alternative is the chained range `k1 = x >= LO; k2{k1} = x <= HI`,
  which costs the same at one position. Its real gain is unions of ranges
  (`kor`).
- XOR replaces SUB only when the range starts on a boundary with zero low
  bits across its width (`0`..`9` at 0x30 qualifies). `[a-z]` (0x61) does
  not, and keeps `t = (x & M) - LO`. Both forms then share the `<=u W` step.
- Where it pays: SIMD is a wash (XOR and SUB cost the same). In SWAR, XOR
  never carries across lanes, so only the final `<=u W` needs lane
  isolation (the high-bit trick), not the subtract as well.
- Status: a design note under the mixed-span entry, not a build. AVX-512 is
  not filed (the bench box is Zen 1). The span form still waits for a
  measured cell where verifying a fixed-width token is the cost.

## 2026-10-13 — R17-b's losses: align the serial head, keep the find vector across calls (Frank)

From the ALPHA reading (slot25c; facts in docs/dev/lanes/r17loss_report.md).
The stateful set FIND loses 2-4 ns per use on near hits, and every find-all
call restarts cold.
- Serial head by alignment: test positions one at a time only until the load
  pointer reaches the vector boundary, then take aligned loads. Alignment
  decides the head's length, so there is no tuning constant.
- Keep the find vector between searches. It saves rebuilding the mask, and it
  also lets the next search skip every candidate test already known to miss.
  Frank wants this tested by a hand-edit spike before any design.
- Test the same at the wider SIMD widths (16/32 B), where both effects are
  larger.
- `[a-z]+\b` should scan for `\W` (the boundary's other side), not `[a-z]`.
  Frank: "not your issue". It is pcrec's choice of what to scan for, passed
  to main.
- Caveat from Frank: the ALPHA subjects are contrived, so real-world reach is
  unknown. The spike adds real-text subjects.
- Spike: lane vecspike (variants V0-V4 plus SSE2/AVX2), timing in a quiet slot.

## 2026-10-13 — one class-vector producer for the multi-position FIND and the VM (Frank)

- The multi-position FIND without unaligned loads takes one aligned load per
  block, runs every position's class test on that vector, and lines the
  positions up by shifting the hit bitmasks: candidate i =
  m0[i] & m1[i+1] & m2[i+2], carrying bits in from the next block (shift-or).
  vecspike2's P variants use shifted loads instead; compare the two if P wins.
- Frank: this is the same object as the VM class-truth-vector idea
  (2026-10-11, [VM-CLSMASK]). Under backtracking, a class test becomes a bit
  test at the position, and once a window is computed the NFA never loads the
  subject bytes again. This does not extend to the DFA, which is a separate
  question.
- Leaning: ONE producer. pcrec states the class set (the atoms, already
  de-duplicated by [OPT-CLSPACK]); the kit owns how vectors are made (term
  compares, shufti, VBMI). Vectors are lazy per block and cached by block
  index, in the same state the kept vector would carry. It pays under
  re-testing; a linear single-test VM loses. Build the FIND's shift-or form
  as this producer, not as a FIND-only helper.
- Follow-up (Frank, same day): careful construction saves work. If pcrec asks
  for every class at once ([agz] and [a] together, not separately), [a]'s
  vector is built once and reused inside [agz]. Complements are free (NOT),
  and a union of classes is ORs of vectors already built. The kit's problem
  becomes a multi-output cover: minimize the distinct terms across the
  batch, which can choose a different cover for a set than it would choose
  alone. The building blocks are atoms (pcrec already has them for
  [OPT-CLSPACK]) or shared cover terms; the kit picks. Contract consequence:
  the request unit is the batch (the window's or the artifact's whole class
  set, the FIND span's positions and the VM's classes together), stated as
  facts.
- Follow-up (Frank, same day): give each class in the batch its LIVE RANGE,
  the [min, max] offsets from the attempt start where the pattern can test
  it. Example: a{2,3}[bz]{4,8}[bc]{2,4}c needs [a] near the start and c only
  near the end, so [a] and c can share one vector register. This does not
  save time but avoids spills when registers run short. The kit treats it as
  interval coloring. pcrec can derive the ranges by the k-set walk extended
  to per-class intervals ([x, inf) after an unbounded repeat). Facts only:
  pcrec states the ranges, the kit decides sharing. The ranges are relative
  to one attempt; with several candidates in flight the live set is their
  union. A side benefit: no vector needs building for blocks outside every
  live range.

## 2026-10-13 — Frank: BATCH MATCHES (find every match in a stretch, as a set, in one call)

- Frank: "an option to switch to batch matches. For this stretch of subject,
  find all the matches as a set. Then it's all internal." The block mask,
  the kept vector, the re-seed hint and the retry bit all live in locals for
  the whole stretch. No state crosses an exported call, and the per-call fixed
  cost is paid once per stretch rather than once per match.
- History: D41 ruling 5(c) (2026-08-14) REJECTED batch find-all as a
  primitive: the match count is data-dependent; negotiating capacity
  "reinvents the cursor with worse ergonomics"; (a) emitted loops plus (b) a
  cursor leave it no customer. What changed since: (b) now exists as D165's
  `rx_iter`. A BOUNDED batch ("fill up to K match records from the
  iterator's position, return the count, the iterator holds the resume")
  is the cursor with a batch size, so capacity is the caller's K, not a
  negotiation. D41's objection does not reach that form. The open cost is the
  captures: K x groups x 2 offsets of caller memory (cf. [CAPTURE-ARRAY],
  filed 2026-10-13).
- Why it matters for the kit (manager reading, pending costmodel2's regimes):
  the losses that survive every spike variant are mostly PER-CALL and
  PER-USE fixed costs on dense, short or tiny-match rows (the "dinghy"
  regime). Batch amortizes exactly those costs. It also removes the D165
  parity risk for dense tiny matches. Keep form's +0.2-2.9 ns
  with-nothing-to-reuse becomes zero, because nothing is stored or reloaded.
- Companion (manager): inside a batch, the SIMD block mask's popcount IS a
  measured hit density per 64 B, for free. The runtime-adaptive switch that
  setfind.md §9.1 did not build (it paid to OBSERVE density, at 0.63
  mispredicts per call) gets its observation for nothing. A batch could
  choose walk vs block per stretch from the data it already holds, with no
  prior, exemplar or hint for within-regime choices.
- Companion (manager): a batch is also the natural home for the two-pass
  form. Pass 1 builds the stretch's candidate bitmap (the one class-vector
  producer, multi-position shift-or). Pass 2 verifies set bits in order.
  Scanning and verifying no longer interleave per candidate. This is
  [SPAN-ISEL]/bitstream territory (filed, unscheduled). Note only.
- pcrec side: an API surface ([FINDALL-NEXT] / D165 / [IFACE-PUSH]) that
  main owns. The kit's interest is a fact: a batch entry lets the kit's
  find state be function-local. Relayed to main; discussion before any
  design.

## 2026-10-21 — partial covers: a span need not be searched all or nothing (Frank)

- Frank's example: `x\w\dabc\d{20}`. The span's front is costly, but a few bytes in it drops to cheap terms. Today's position grain already partly does this. The search reads one chosen position (here `x`, required byte `b`, run `abc`) and verifies the rest; `\w`/`\d` are never scanned. The 2-term rule (D169 add.) applies only to the byte SET at the position actually scanned.
- The open half is at the SET grain: search a SUPERSET of the position's set that has fewer terms, then verify the exact set on each candidate. Example: `\w` = 4 terms (walk), but `[0-9]|[A-z]` = 2 terms admits only 5 extra bytes (`[\]^` and backquote), so it can route to V1. A 1-term hull `[0-z]` admits 12 extra bytes.
- Trade-off: the false-candidate rate from the extra members, priced with the byte prior, against the term-count saving (grid2's per-shape V1 savings). Verification is already paid by the consumer, so a superset filter is sound for FIND, never for a REPORT proof.
- Not built and not timed. Trigger: a measured set-FIND site of ≥ 3 terms whose ≤ 2-term superset adds a low-rate member set. Bench or grid cells would show it.
- Frank's clarification (same day): the point is the V1-vs-walk decision. The term count need not be the span head's. The FIND can filter at a cheaper position a few bytes into the span, where the set has ≤ 2 terms, so V1 applies. It then verifies the costly head positions per candidate. Shape: price the scan POSITION by the form its set would take (V1 at ≤ 2 terms, else the walk) together with its rate, not by rate alone. Who picks: the kit has RQ-2's position ranking (rates) and the per-position sets; the offset-skip FIND already scans at offset k. Open fact to check before any design: whether every set-FIND site the B4 manifest routes to the walk has a ≤ 2-term position within its span.

## 2026-10-23 — D-hors's window: widen it to the contiguous tested core run (S3 review unlock)

- From the D172 S3 review (lane s3, D-hors as built: `memfn/src/window.c` `hors_window`). D-hors's window is the core of the first verify-YES span whose core holds the stop. Its shift is bounded by that window's length, so a pattern whose tested core continues past the span (an adjacent span, or positions C-bound keeps) gets shorter shifts than the tested positions would allow.
- The general form: the window is the longest CONTIGUOUS run of tested core offsets around the stop, across spans; the shift table is the same computation (`hors_table`) over it.
- Answers: unchanged (the table's invariant holds over any run of tested offsets). Saving: longer skips on dense stops with long fixed tails.
- Trigger: a measured cover cell whose tested core run is longer than its D-hors window (a two-span window with both cores tested), where D-hors already fires.

## 2026-10-23 — priced probe choice for D-hors under the byte-rate (S3 review unlock)

- From the D172 S3 review. D-hors probes the window's LAST position, always. Horspool's classic choice is that, but the expected skip depends on which position is probed: E[shift] = sum over bytes b of rate(b) x sh_probe[b]. A position whose tested set is rare (low mass) gives longer skips more often.
- The general form: price each candidate probe offset by its expected shift under pcrec's byte-rate (the same `kit_set_mass` input the D-hors gate already reads), and take the probe with the largest expected shift (the review's "argmin": the least expected probes per byte). A TIE rule goes in `wf_ties[]`.
- Answers: unchanged where the shift table is built for the chosen probe. Saving: unknown; plausible on windows whose last position is dense and an earlier one sparse (hex then a delimiter).
- Trigger: a measured D-hors cell where the last position's set is denser than another tested position's (a declared row table, never an if-ladder).

## 2026-10-23 — D-hors at non-REPORT E-find sites (S3 review unlock)

- From the D172 S3 review. E-find renders any STMT/ASSIGN window site with a stop, and Table D's D-hors applies to every E-find plan, but today E-find only renders sites the legacy rows decline: REPORT (cover) and none else on a default artifact. So D-hors reaches only cover artifacts.
- The general form: let E-find (and so D-hors) serve a DFA_SCAN/ADVANCE site the legacy rows serve today, where a dense stop and a window of two or more tested positions make Horspool's skip pay. That would be a per-site choice between the legacy text and E-find+D-hors, priced, in Table E's order.
- Answers: unchanged (E-find is find-then-verify of the same plan). Saving: the 581 hex8 result (2-6x on real and no-hit text) at scan sites with the same shape.
- Trigger: a measured scan site (not REPORT) with a dense stop and a >= 2-position tested window, losing to a Horspool form in a G1 or bench reading.

## 2026-10-23 — D-hors admission priced on E[sh] (Frank's ruling on the S3 review's fix C)

- D-hors admits today on the stop set's mass alone (HORS_MIN, PROVISIONAL) and a window of two or more positions. The review's fix C (decline where max(sh) == 1) was withdrawn as a byte move without a measurement.
- The general form: D-hors admission priced on E[sh] = sum over bytes b of rate[b] x sh[b] (the expected shift per probe under the byte-rate), as ONE declared row replacing or joining HORS_MIN: D-hors pays where its skip outweighs its per-candidate overhead relative to D-one.
- Answers: unchanged (D-hors and D-one are both exact find-then-verify). Saving: the D-hors sites where E[sh] is near 1 (`(?s)[^a]..`, `[aeiou]..[aeiou]`) would stop paying the probe.
- Trigger: job 588's "D-hors admission (E[sh])" reading (s3_report.md Part 4; esh_588.tsv's 12 sites, alpha sorted by E[sh]).
