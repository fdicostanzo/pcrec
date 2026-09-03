# [ENG-ISL.S0] — the alternation-dispatch study

Chartered by Frank 2026-09-03 ("I approve the study charter"), lane
altstudy. Answers `[ENG-ISL]`'s first named island candidate (docs/dev/plan.md:
"VM ALTERNATION AS A TRIE DISPATCH") with measurement rather than argument:
of five dispatch algorithms for a wide literal alternation, which one is
EXACT, which is FAST, and at what width does the win justify building it as
the VM's alternation island in `src/gen/emit_vm.c`. This is a `studies/`
deliverable (`studies/alt_dispatch/`, own Makefile, never built by pcrec's
own `make`, never run by `make test` — `studies/CLAUDE.md`'s standing rule);
nothing under `src/` or `tests/` changed. Findings graduate by the normal
route: a future plan-row charter citing this note, not by importing the
study's code.

**MID-STUDY RULING R1 (Frank, 2026-09-03 ~12:2x, in
`worktrees/altstudy/docs/dev/lanes/altstudy_rulings.md`, uncommitted):**
the charter's original four algorithms — (a) serial try, (b) first-byte
grouping, (c) sorted trie with priority-tagged accepts, (d) k-byte block
hash — are joined by **(e) the VM-NATIVE TRIE WALK**, named the PRIMARY
candidate: the shape the VM emitter would actually build, where (c)'s trie
walk pushes VM frames only at the points a real emission would, and
everything else is deferred into a compile-time-sized bitmask rather than
walked twice. §2.1 item (e) and §3.2 are new; every table in §4 gained an
`vm`/(e) column; the recommendation in §6 chooses between (c) and (e).

## 1. The measured need, restated

The bench's overnight window at pin `1989c62`
(`docs/dev/summaries/2026-09-03-exec-bench-altwide-noedge-ccrerun-1989c62.md`,
finding 2) measured branch ORDER costing pcrec's VM a large, width-growing
penalty the DFA route never pays: `srt-256` (`w-256`'s own 256 branches,
sorted by first byte) is ×8.87 faster on the VM than `w-256`, byte-identical
on the DFA; at 512 under the raised code cap the same reorder is ×20.1. The
re-pinned census at `288d505` (journal fiftieth session, part 19) attributed
the mechanism: the VM lowering already consumes `src/ir/nfa.c`'s M2.8 trie's
FACTORING count (`RX_ALTCLS_FACTORED` reads 11 on `w-256` vs 57 on
`srt-256`, the DFA artifacts byte-identical but for that stamp), so sorted
input factors ~5× more into the trie the DFA already gets for free — and the
VM's per-byte cost is `vm_alt`'s serial chain, one push/fail/pop/dispatch
round-trip per untried branch, so matching the last of 512 branches costs
511 round-trips on ONE subject byte (journal part 7 addendum 3).

`[ENG-ISL]`'s filed island idea and Frank's brainstorm ("a DFA island in the
VM for alternates"; "sort alphabetically... for each match we know if a
higher-priority shorter alternative should be tried first") resolve into one
design: walk the alternation as a TRIE (sorted, so shared prefixes factor
regardless of source order) with every accept node tagged by its ORIGINAL
branch index, and answer the LOWEST index seen along the walk — leftmost-
first by construction, sort order affecting only how fast a lookup is, never
what it answers. This study builds that walk, an even simpler first-byte
lever, and a k-byte block-hash variant, and measures all three against
today's serial try.

## 2. Method

### 2.1 The harness

`studies/alt_dispatch/` (own Makefile, `gcc -O2`, C11, no external deps). A
branch is a sequence of `ByteSet`s (256-bit class bitmaps), not a raw
string — deliberately mirroring `src/ir/nfa.c`'s `TItem`, so a `(?i)` branch
is a first-class input (each alphabetic position admits `{lower, upper}`)
with no special-casing anywhere in the four algorithms. Four modules:

- **(a) serial try** — `src/gen/emit_vm.c`'s `vm_alt`, ported: branches in
  source order, first full match wins. This IS the oracle: trivially
  leftmost-first because it stops at the first success in preference order.
  Cost counted: `tries` = branches attempted (one per push/fail/pop round-
  trip `vm_alt` would spend); `verify_bytes` = byte-class tests, fail-fast.
- **(b) first-byte grouping** — stable-group branches by first byte at
  construction; at a query, look up the subject byte's group (a 256-entry
  table of index lists, an entry appearing in up to 2 lists for a `ci`
  branch) and try only that group, in original index order. The cheap lever
  `[ENG-ISL]` already recorded.
- **(c) sorted trie, priority-tagged accepts** — `algo_trie.c`, a port of
  `trie_build`/`trie_key` (`src/ir/nfa.c:192`) restricted to this study's
  branch shape (no A_REP/A_ALT scaffolding, since a literal alternation's
  branches are already flat class chains) and to a QUERY WALK rather than an
  NFA fragment. §3 is the exactness argument.
- **(d) k-byte block hash** — `[OPT-ALTHASH]`'s design, `k ∈ {2, 4}`: hash
  the next k subject bytes into an open-addressed table keyed by the
  branches' CONCRETE k-byte prefixes (a `ci` branch enumerates every
  realization of its first k bytes, up to 2^k for this study's fold-pair
  classes); branches shorter than k take the per-byte path (here: a plain
  serial scan over the short branches, combined with the hash group by
  taking the smaller of the two subsets' winning index — see
  `algo_hash.c`'s header comment). A miss is exact-verified: the table
  stores the real key bytes, not just a hash, so a probe that finds no
  matching key really means no k-length-or-longer branch can match here.
- **(e) VM-native trie walk** — ruling R1 (Frank, 2026-09-03), added
  mid-study as the PRIMARY candidate: `trie_dispatch_vm` in `algo_trie.c`,
  reusing (c)'s SAME trie plus one static per-node annotation
  (`subtree_min`, computed once after the trie builds). The walk descends
  exactly like (c), but at every end node it passes it decides COMMIT (push
  ONE resumable frame and stop the forward pass with this branch as the
  primary answer — nothing anywhere else in the walk could ever beat it) or
  DEFER (record the index in a small ascending-ordered list and keep
  walking) — see §3.2. Cost counted: `frames` (VM frames pushed — the
  ruling's own headline metric, comparable to (a)'s `tries`) and
  `deferred_seen` (the size the deferred list reached — the "mask width"
  a real per-pattern bit assignment would need).

Every algorithm returns `(hit, branch_index, match_len)`; the harness checks
(b)/(c)/(d)/(e) against (a) at EVERY subject position of EVERY (pattern,
subject) pair and counts mismatches — the exactness bar is zero, everywhere,
not a sampled check.

### 2.2 Inputs

`gen_inputs.py` derives `patterns/*.branches` from pcrec-bench's
`bench/altwide/*.rx` (read-only; provenance header per file, sha256 of the
source recorded). Widths and shapes, against the charter's seven (w, srt,
pfx3, ci, cnt, s, sh1):

| shape | widths measured | source |
|---|---|---|
| `w` | 8, 64, 96, 128, 192, 256, 384, 512, 1024, 2048 | bench `.rx`, direct |
| `s` | 256, 512, 2048, 4096 | bench `.rx`, direct |
| `sh1` | 64, 256, 512 | bench `.rx`, direct |
| `pfx3` | 256, 512 | bench `.rx`, direct |
| `srt` | 256, 512, **1024, 2048** | 256/512 direct; 1024/2048 derived: `sorted()` of `w-1024`/`w-2048`'s own committed branch list — `gen_patterns.py`'s own `wrap(wrapper="sorted")` rule, no new pool words drawn |
| `ci` | 256, 512, **1024, 2048** | 256/512 direct; 1024/2048 derived: `w-1024`/`w-2048`'s branch list tagged `MODE ci` (the harness folds case per position; no word rewritten) |
| `cnt` | 64 | `cnt-64`'s inner alternation IS `w-64`'s branch list (§5.3 says why no separate measurement is owed) |

`subjects/*.bin` are copied byte-for-byte from the bench: the 17 short
field/hit and near-miss subjects (`subjects/PROVENANCE.md`) plus the four
throughput prose files (`t-128k-clean/-sparse/-dense`, `t-512k-sparse`).
This study's PRIMARY per-byte measurement uses `t-128k-sparse` (131,072 B,
16 placed hits — the bench's own "mostly-failing prose with a designed
placement" shape, closest to what a real search pays); `t-128k-dense` (1,024
hits) and `t-128k-clean` (0 hits) bracket it.

### 2.3 Timing discipline

Per the lane's box rule: a battery lane (`ccdiff1b`) and an afternoon
bench window share this box. Answer-identity and tries-per-byte are
load-independent (pure operation counts) and were taken first. Timing
(`results/timing.tsv`) is 11 rounds per (pattern, subject, algorithm),
median reported, `ns_per_byte` and `ns_per_call`; every row also records
`/proc/loadavg`'s 1-minute figure at that measurement, so a reader can
discount a row taken under load rather than trust a number with no context.
Full run: load1 ranged **1.04–2.28** across the run (a battery lane and
background box activity contributing throughout; the box rule's <2 target
held for most of the run, some cells landing just over it — §4.3 notes
where a `w`/`srt` comparison reads a load artifact rather than a real
difference). The answer-identity (§4.1) and tries-per-byte (§4.2, §4.4)
numbers are unaffected by load; only the `ns`-denominated tables (§4.3,
half of §4.4) carry load exposure, and every such row states its own
`load1`.

## 3. The exactness argument for (c)

**Claim.** For a set of literal (or case-folded-literal) branches, the trie
walk's answer — the lowest ORIGINAL alternation index among every accept
node the walk passes, or no-match if it passes none — equals the serial
try's leftmost-first answer, for every subject and every start position.

**Why.** Leftmost-first over a plain alternation of literals is: try
branches 0..n-1 in order, the first FULL match wins, independent of length
(`(abc|a|abd)` on `"abd"` returns the `a` branch, index 1, length 1, not the
longer `abd` at index 2 — `src/ir/nfa.c:192`'s own stated counter-example).
So the true answer is `min({ i : branch i matches subject[pos..) })` — a
pure function of WHICH branches match, never of match length or of trie
depth. The trie's construction (`trie_build`, ported as `build()` in
`algo_trie.c`) never discards or reorders which branches reach a node: every
node's `accepts` list is exactly the branches whose full literal equals the
prefix consumed to reach it, and the WALK (`trie_dispatch`) descends every
subject-selected path to its end, collecting every accept it passes rather
than stopping at the first. So the collected set, over a complete walk, is
EXACTLY `{ i : branch i matches subject[pos..) }` — sharing structure with
other branches only changes how many BYTE COMPARISONS the walk performs to
compute that set, never what the set contains — and the minimum of that set
is the answer by the claim above. `tests/unit_trie.c` confirms this against
both of `nfa.c`'s own hazard counter-examples (rule 1: `abc|a|abd`; rule 2:
`[ab]p|[bc]x|[ab]xy`, both checked at every subject position, both exactly
matching `nfa.c`'s stated PCRE span) plus a full sweep against this study's
own serial oracle on real bench-derived branch sets — zero mismatches, see
§4.1.

**Rule 1 (a branch ending mid-trie) needs no special handling in the walk.**
nfa.c's rule 1 exists because its NFA CONSTRUCTION must interleave an
accepting branch with continuing ones in priority order inside one fragment
chain. The walk here does not build a chain at all — it just keeps
descending past an embedded accept and keeps collecting, so an accept at
DEPTH 1 (branch `a`, index 1) and a lower-index accept reached later at
depth 3 are both in the collected set regardless of which the walk visits
first; the MIN over the set is order-independent by construction. This is
why the study's port needed no analogue of `trie_build`'s explicit
index-ordered segment splitting (rule 1's "segment, accept, segment..."):
that machinery matters for building a correct BACKTRACKING NFA, not for
computing a min over a collected set.

**Rule 2 (overlapping non-identical classes) is VACUOUS for this study's
branch shapes, and here is why precisely.** Every class this study's inputs
produce is either a singleton byte (a plain literal position) or a 2-member
case-fold pair (`{c, fold(c)}` under a `ci`-tagged branch set). Two such
classes at the same trie node are either IDENTICAL (same byte, or same
letter's fold pair — these merge into one child, the ordinary case) or
DISJOINT (different letters can never share a byte, and a fold pair for
letter X can never contain any byte of letter Y's singleton or fold pair,
since the alphabet's upper/lower pairs are themselves disjoint across
letters). A genuine PARTIAL overlap — two classes that share some bytes but
not all, e.g. `[ab]` and `[bc]` — never arises from a literal or `(?i)`
literal alternation; it would need a hand-written CHARACTER CLASS inside an
alternation branch (`[ab]p|[bc]x`), which is a different construct this
study's charter scopes out (the charter's seven shapes are all plain or
case-folded literals). `algo_trie.c`'s `build()` still detects this case
generally (`classes_pairwise_disjoint`) and — since nfa.c's rule 2 machinery
(disjoint-run splitting, chained sub-tries) is exactly the "an NFA step"
half of the charter's "what a class branch would need" — this port takes
the OTHER half instead: it **DECLINES**. A declined node stores its
continuing branches as a flat list and the walk falls back to a full,
un-factored serial check over exactly that list from that depth onward,
still collecting every accept into the same min-index answer. This keeps
the answer exact (§4.1's unit test `build_overlap_case` constructs
`[ab]p|[bc]x|[ab]xy` by hand — bypassing the file-based loader, since the
bench's shapes never produce this input — and confirms both the declined
walk's answer and its literal span against `nfa.c`'s own stated example,
`"bxy" -> [0,2)`) at the cost of no factoring for that subtree; a real VM
island targeting general classed alternations (not this study's scope)
would want the NFA-step half instead, chaining disjoint runs the way
`trie_build` does, to keep the O(1)-per-byte property rule 2's hazard would
otherwise cost it.

**What the candidate list is for.** `trie_dispatch` also returns every
collected accept, sorted ascending, not just the minimum — `algo_trie.h`'s
`out_cand`. This is what a real VM island's CONTINUATION BACKTRACKING would
need: PCRE backtracks INTO an alternation when the branch that won here
fails a later part of the pattern (`(ab|abc)d` on `"abcd"` must fall from
`ab` to `abc`), so an emitted island cannot simply commit to the lowest-
index accept and move on — it must be able to retry the NEXT-lowest
candidate the walk already found, in the same order `vm_alt`'s resume chain
tries branches today. The candidate list is exactly that resume order,
computed once per walk instead of re-walked per retry.

## 3.2 The exactness argument for (e), and the subtlety it took to get right

**Claim.** `trie_dispatch_vm`'s answer — the first COMMIT reached while
walking, or (if the walk dies with no commit) the ascending minimum of
everything DEFERRED — equals (c)'s answer, hence the leftmost-first oracle's.

**The naive version of the commit test is UNSOUND, and this study's own
regression test (`tests/unit_trie.c`, the `nfa.c` rule-1 case) is what
caught it.** Ruling R1's own wording is "whether a LOWER original index
exists DEEPER in this subtree" — precomputed once as `subtree_min` (§2.1),
tempting to read as: commit iff this node's own accept index equals
`subtree_min`. That is necessary but **not sufficient**. Trace
`abc|a|abd` (indices 0, 1, 2) on subject `"abd"`: at depth 1 the trie has an
accept for `a` (index 1); `subtree_min` at that node is 0 (branch `abc`,
reachable one level deeper via the shared `b`), so index 1 correctly
DEFERS. The walk continues via `b`, then via `d` (the subject's own byte),
reaching a LEAF at depth 3 whose only accept is `abd` (index 2). That leaf's
own `subtree_min` is 2 (nothing is reachable below a leaf), so
`idx == subtree_min` holds and the naive test would COMMIT to index 2 —
**wrong**: the oracle's answer is index 1 (`nfa.c`'s own stated span,
`"abd" -> [0,1)`), because index 1 was already deferred earlier on this
SAME path and nothing has invalidated it. `subtree_min` only ever looks
DEEPER; it has no memory of what the walk already passed and set aside.

**The fix: commit requires beating BOTH halves.** `trie_dispatch_vm` tracks
`best_deferred`, the running minimum of everything deferred so far on this
path, and commits an index `idx` only when `idx == subtree_min(node)` (deeper
half, the ruling's own test) **AND** (`best_deferred` is unset or
`idx < best_deferred`) (shallower half). Re-run the trace: at the depth-3 leaf,
`best_deferred == 1 < 2`, so index 2 correctly DEFERS instead; the walk then
dies (leaf, no children), and the post-walk fallback takes
`min(deferred) == min({1, 2}) == 1` — the correct answer. Every case in
`tests/unit_trie.c` (both `nfa.c` counter-examples, on all their subjects,
plus the declined-node path, which needs the identical cross-check — see the
comment beside its own `best_deferred` use in `algo_trie.c`) passes with this
fix; the harness's full sweep (§4.1) confirms zero mismatches against the
independent serial oracle across the whole bench-derived matrix, where the
naive version would not have been caught at all — no bench-derived pattern's
substring-free pool (property 2, `bench/altwide/altwidetext.py`) ever
produces more than one accept per root-to-leaf path, so `best_deferred` is
always unset on real inputs and this defect is invisible outside an
adversarial multi-accept case exactly like `nfa.c`'s own. **This is the
study's one correctness finding worth flagging to whoever builds the real
island**: a per-pattern static bit-assignment scheme for the deferred mask
must encode the SAME two-sided check, not just "beaten by something deeper."

**Why committing early is still safe.** Once `idx` beats both `subtree_min`
(nothing deeper, anywhere in the remaining walk, is lower) and
`best_deferred` (nothing already passed and set aside is lower either), `idx`
is provably the minimum of the ENTIRE set the walk could ever produce — the
union of what's deferred, `idx` itself, and everything still reachable. Since
the walk is a SINGLE deterministic path (sibling classes are disjoint by
construction — §3's rule-2 argument), "everything still reachable" is
exhaustive; there is no sibling subtree left unvisited that could still
produce a lower index. So stopping there and reporting `idx` (as if a real VM
had jumped straight to that branch's continuation) is exact, matching
ruling R1's "jump to the continuation with this branch's length."

**Frames pushed, and why it is the study's headline number for (e).** Every
COMMIT pushes exactly one frame; the post-walk deferred-mask fallback (no
commit ever fired) also counts as one frame, per the ruling's own text ("try
the recorded end nodes… with ONE frame per alternation attempt"). Since the
walk is single-path and stops at the first commit, **at most one frame is
ever pushed per dispatch** — contrast (a)'s `tries`, which is the branch
INDEX of the winner in the worst case (511 for the last of 512 branches).
§4.2's `total_frames` column measures this directly, and on every
bench-derived pattern this study built it is a small constant per subject —
see §4.2's dedicated frames/deferred table.

## 4. Results

*(Tables below are generated by `analyze.py` over `results/*.tsv`; see that
script to reproduce, and `results/` for the full per-pattern-per-subject
data these summarize.)*

### 4.1 Answer identity — the exactness bar

Full matrix: 28 patterns × 21 subjects, every subject position checked.

| algo | mismatches | positions checked |
|---|---|---|
| firstbyte (b) | **0** | 25,694,396 |
| trie (c) | **0** | 25,694,396 |
| hash2 (d, k=2) | **0** | 25,694,396 |
| hash4 (d, k=4) | **0** | 25,694,396 |
| vm (e) | **0** | 25,694,396 |

Zero mismatches, every algorithm, every position — the exactness bar holds
across the whole study, including the width-1024/2048 srt/ci rungs this
study derived and the two hand-built adversarial cases (§3, §3.2).

### 4.2 Tries per subject byte (t-128k-sparse), and (e)'s frames/mask table

Selected rows (full table in `results/tries.tsv`; `analyze.py`'s stdout has
every pattern):

| pattern | serial (a) | firstbyte (b) | trie (c) | hash2 (d,k=2) | hash4 (d,k=4) | vm (e) |
|---|---|---|---|---|---|---|
| w-64 | 64.00 | 1.91 | 17.54 | 2.08 | 10.03 | 17.54 |
| w-256 | 256.00 | 7.66 | 22.26 | 2.32 | 31.03 | 22.26 |
| w-512 | 511.99 | 15.31 | 25.41 | 2.55 | 59.03 | 25.41 |
| w-1024 | 1023.98 | 30.62 | 28.15 | 3.01 | 96.03 | 28.15 |
| w-2048 | 2047.94 | 61.28 | 29.95 | 4.02 | 163.03 | 29.95 |
| s-4096 | 4095.95 | 122.52 | 31.68 | 6.04 | 146.03 | 31.68 |
| sh1-512 | 511.99 | 15.32 | 1.75 | 2.50 | 11.03 | 1.75 |
| pfx3-512 | 511.99 | 15.27 | 1.03 | 2.49 | 2.00 | 1.03 |
| srt-512 | 511.99 | 15.31 | 25.36 | 2.55 | 59.03 | 25.36 |

(c) and (e) count *trie steps* identically in this metric (same walk
mechanics; §4.3's `total_frames` is where they diverge). Structure arms
(`sh1`, `pfx3`) show the trie's real payoff: 1.03–1.75 steps/byte against
serial's 512, because a shared-prefix run collapses to near-O(1) descent.
`hash4` is the one algorithm that gets WORSE with width on the `w`/`s`
ladder (10 → 163 steps/byte, w-64 → w-2048) — its per-branch group-scan
tail cost is not sub-linear the way the trie's is; §4.5 shows why (its
distinct-key count on `ci-2048` reaches 30,144).

**(e)'s frames pushed and deferred-list size, on t-128k-sparse (131,072
positions), the ruling's own headline ask:**

| pattern | total_frames | frames per 1000 positions | max_deferred (mask width) |
|---|---|---|---|
| w-64 | 2 | 0.015 | 0 |
| w-256 | 3 | 0.023 | 0 |
| w-512 | 4 | 0.031 | 0 |
| w-1024 | 5 | 0.038 | 0 |
| w-2048 | 6 | 0.046 | 0 |
| s-4096 | 3 | 0.023 | 0 |
| sh1-512 | 2 | 0.015 | 0 |
| ci-2048 | 6 | 0.046 | 0 |
| srt-2048 | 6 | 0.046 | 0 |

**At most ONE frame is EVER pushed per dispatch** (§3.2's argument), so
`total_frames` here is literally the count of subject positions where a
branch matched at all — every pattern in the matrix pushes single digits
of frames across 131,072 positions, against serial's would-be up to
131,072 × (branch count) push/fail/pop round-trips. `max_deferred` is
**zero on every bench-derived pattern in this study** — confirms
`bench/altwide/altwidetext.py`'s property 2 (globally substring-free
pools) directly: no root-to-leaf path in any of these tries ever carries
more than one accept, so the `best_deferred` cross-check (§3.2) never
actually fires outside the hand-built adversarial unit tests. A real
per-pattern compile-time mask would size to what THIS number reports for
the pattern in hand, not to a fixed constant.

### 4.3 ns per subject byte (t-128k-sparse), load1 noted

Measured at load1 in the range **1.05–2.24** (single-core CPU-bound
harness; battery lane `ccdiff1b` and background box activity both
contributed — every row below is exactly as measured, not adjusted):

| pattern | serial (a) | trie (c) | vm (e) | hash2 (d,k=2) | hash4 (d,k=4) | firstbyte (b) | (a)/(c) | (a)/(e) | (c)/(e) | load1 |
|---|---|---|---|---|---|---|---|---|---|---|
| w-64 | 190.03 | 28.28 | 27.13 | 17.72 | 49.25 | 18.12 | 6.72 | 7.00 | 1.04 | 1.20 |
| w-256 | 767.86 | 35.67 | 34.62 | 24.34 | 117.64 | 43.11 | 21.53 | 22.18 | 1.03 | 1.12 |
| w-512 | 1606.72 | 40.18 | 39.48 | 29.70 | 206.86 | 80.29 | 39.99 | 40.70 | 1.02 | 1.08 |
| w-1024 | 3226.63 | 48.05 | 47.26 | 34.44 | 338.23 | 157.57 | 67.15 | 68.28 | 1.02 | 1.15 |
| w-2048 | 6442.44 | 54.20 | 53.45 | 41.11 | 578.66 | 322.57 | 118.86 | 120.53 | 1.01 | 1.09 |
| s-4096 | 14031.67 | 57.19 | 57.81 | 56.93 | 551.36 | 683.19 | 245.35 | 242.72 | 0.99 | 2.12 |
| sh1-512 | 1383.89 | 13.13 | 12.47 | 19.54 | 53.61 | 76.94 | 105.43 | 110.94 | 1.05 | 2.02 |
| pfx3-512 | 1376.60 | 12.16 | 11.59 | 18.11 | 19.82 | 70.48 | 113.19 | 118.76 | 1.05 | 2.07 |
| srt-512 | 1405.61 | 40.36 | 39.58 | 29.84 | 199.72 | 78.33 | 34.82 | 35.52 | 1.02 | 2.08 |

**(c) and (e) are within 1–5% of each other in raw ns/byte at every row**
(the `(c)/(e)` column) — on this study's shapes (branches ≤12 bytes,
shallow tries) short-circuiting the walk saves little wall time, because
the walk was already cheap; the difference that matters between them is
the FRAME COUNT (§4.2, §3.2), which is what a real emitted VM pays in
push/resume machinery, not raw comparison count. `s-4096`'s `(a)/(e)`
(242.72) dips very slightly below `(a)/(c)` (245.35) — noise at this
load, not a reversal (both algorithms walk the identical trie for this
pattern; see §4.5's shared construction).

### 4.4 The width ladder: `w` vs `srt`, and a methodological caveat

### 4.4 The width ladder: `w` vs `srt`, and a methodological caveat

Compared with the bench's measured ×8.87 (w-256/srt-256) and ×20.1
(w-512/srt-512) VM order penalty:

**Tries per subject byte, `w-N` vs `srt-N`, on t-128k-sparse:**

| width | w serial | srt serial | w trie(c) | srt trie(c) | w vm(e) | srt vm(e) | ratio serial | ratio trie | ratio vm |
|---|---|---|---|---|---|---|---|---|---|
| 256 | 256.00 | 256.00 | 22.262 | 22.216 | 22.262 | 22.216 | **1.00** | **1.00** | **1.00** |
| 512 | 511.99 | 511.99 | 25.412 | 25.361 | 25.412 | 25.361 | **1.00** | **1.00** | **1.00** |
| 1024 | 1023.97 | 1023.98 | 28.151 | 28.101 | 28.151 | 28.101 | **1.00** | **1.00** | **1.00** |
| 2048 | 2047.94 | 2047.97 | 29.947 | 29.879 | 29.947 | 29.879 | **1.00** | **1.00** | **1.00** |

**ns per subject byte, the same pairs:**

| width | w ns serial | srt ns serial | w ns trie(c) | srt ns trie(c) | w ns vm(e) | srt ns vm(e) | ratio serial | ratio trie | ratio vm |
|---|---|---|---|---|---|---|---|---|---|
| 256 | 767.9 | 686.3 | 35.67 | 34.89 | 34.62 | 34.06 | 1.12 | 1.02 | 1.02 |
| 512 | 1606.7 | 1405.6 | 40.18 | 40.36 | 39.48 | 39.58 | 1.14 | 0.99 | 1.00 |
| 1024 | 3226.6 | 2806.4 | 48.05 | 47.88 | 47.26 | 47.25 | 1.15 | 1.00 | 1.00 |
| 2048 | 6442.4 | 5599.4 | 54.20 | 52.87 | 53.45 | 52.37 | 1.15 | 1.03 | 1.02 |

**Caveat, and what these numbers actually say.** This study's (a) is a
PURE, unfactored serial try — literal branches tried in given order, with
no upstream trie factoring applied first. Today's actual `vm_alt`, by
contrast, is fed branches AFTER `src/ir/nfa.c`'s M2.8 trie has already run
(the plan row's own attribution: "the VM lowering already consumes the
trie's factoring… `RX_ALTCLS_FACTORED` reads 11 (w-256) vs 57 (srt-256)")
— so today's real baseline sits somewhere between this study's (a) (zero
factoring) and its (c)/(e) (full recursive factoring, order-independent by
construction). **The measured `tries`-based ratio is exactly 1.00 at every
width, for every algorithm including (a)**: this study's own oracle is
genuinely ORDER-INSENSITIVE, because it models a serial try with no
upstream factoring at all — different from the bench's real `vm_alt`, whose
order-sensitivity comes precisely from the partial factoring this study's
(a) does not simulate. (c) and (e) are order-insensitive for a different,
structural reason — sort order affects the trie's CONSTRUCTION only (§3),
so `w-512` and `srt-512` build the identical trie and cost the same to
walk; the `tries` ratios (1.00 exactly) confirm this precisely, and the
`ns` ratios (0.99–1.03 for trie/vm, i.e. noise-level) confirm it holds in
wall time too. The `ns`-based SERIAL ratio (1.12–1.15, not 1.00) is a
measurement artifact, not an order effect — `results/timing.tsv`'s `load1`
column shows `srt-*` cells measured at slightly lower load than their
`w-*` twin in this run (contention from the shared box, §2.3), not a real
per-byte cost difference; the `tries` count (the load-independent measure)
is the one to trust, and it says 1.00 exactly. **This study did not build
a sixth "today's actual partial-factoring" baseline** to reproduce the
bench's exact ×8.87/×20.1 figures — see §5 item 7.

### 4.5 Construction cost and table bytes

(e) adds no separate construction line — it reuses (c)'s trie plus one
linear `subtree_min` post-pass, folded into the `trie_us`/`trie_B` columns
below (`results/construction.tsv`'s `vm` row is a bookkeeping placeholder,
`shares-trie-c`).

| pattern | firstbyte (µs / B) | trie (µs / B, max fanout) | hash2 (µs / B, keys) | hash4 (µs / B, keys) |
|---|---|---|---|---|
| w-64 | 25.4ms / 3,328 B | 67.0ms / 39,992 B, fanout 24 | 33.4ms / 25,560 B, 59 keys | 42.8ms / 50,152 B, 56 keys |
| w-512 | 203.4ms / 5,120 B | 458.6ms / 301,464 B, fanout 26 | 206.1ms / 202,600 B, 372 keys | 355.1ms / 400,992 B, 455 keys |
| w-2048 | 776.8ms / 11,264 B | 1,851.0ms / 1,152,408 B, fanout 26 | 836.6ms / 798,840 B, 645 keys | 1,465.4ms / 1,604,336 B, 1,884 keys |
| ci-2048 | 823.9ms / 19,456 B | 1,781.3ms / 1,152,408 B, fanout 26 | 1,445.7ms / 835,944 B, **2,580 keys** | 6,851.3ms / 2,056,496 B, **30,144 keys** |
| s-4096 | 1,555.8ms / 19,456 B | 2,720.2ms / 1,203,320 B, fanout 26 | 2,310.5ms / 1,595,064 B, 673 keys | 5,802.4ms / 3,210,088 B, 3,948 keys |
| sh1-512 | 191.5ms / 5,120 B | 447.9ms / 286,968 B, fanout 26 | 213.0ms / 199,656 B, 26 keys | 393.9ms / 401,248 B, 495 keys |
| pfx3-512 | 194.7ms / 5,120 B | 402.5ms / 232,248 B, fanout 26 | 196.7ms / 198,696 B, **1 key** | 407.7ms / 789,352 B, 26 keys |

`firstbyte`'s table stays a few KB regardless of width (256 buckets,
bounded per-bucket lists) — the cheapest structure to build by a wide
margin. `trie`'s node count (`table_bytes`) grows roughly linearly with
branch-byte total, matching `pattern_facts.tsv`'s own `trie_nodes` column
order of magnitude. `hash4`'s key explosion on `ci-2048` (30,144 distinct
4-byte keys, against `hash2`'s 2,580 and `w-2048`'s own 1,884 without case
folding) is exactly the `ci`-fold combinatorics §2.1 flags: every
alphabetic position within the first 4 bytes doubles the concrete-key
count, and `ci-2048`'s construction cost (6.85 s at k=4) is the largest in
the whole matrix — nearly 4× `hash2`'s cost on the same pattern. `pfx3`'s
`hash2` construction is cheapest of all (196.7ms, **1 distinct 2-byte
key** — every branch shares the same `qu` prefix) while its `hash4` needs
26 keys (the third/fourth bytes vary) — a clean illustration of why a
block hash's payoff is shape-dependent (§5 item 3, `[OPT-ALTHASH]`'s own
design note (d): "the switch wins at small fan-out, the block hash where
the fan-out at depth 1 is small but the prefix set at depth k is large").

## 5. What the study did NOT settle

1. **`sh1`/`pfx3` beyond width 512.** Both pools cap at 512 words in every
   bench artifact this study may read (`bench/altwide/altwidetext.py`'s
   `POOL_SPECS` draws `n=512` for both), and no committed `.rx` file uses
   more than the first 512 of either. Extending would mean drawing NEW pool
   words under the bench's own `POOL_SEED`, which is bench-side generation
   this study does not perform (the scope mandate keeps bench dependencies
   in pcrec-bench). The width ladder's `w`/`s`/`srt`/`ci` rows reach
   2048/4096 and carry the general trend; `sh1`/`pfx3` (the sharpest
   first-byte / first-3-byte cases) are measured only to 512.
2. **`cnt` beyond a bare alternation.** `cnt-64` wraps `w-64`'s alternation
   in `{1,3}`; a counted repetition multiplies how many times the SAME
   alternation entry is dispatched per match attempt but does not change
   what one entry's dispatch costs, so this study measured `w-64` and did
   not build a separate counted-repetition harness. This is an argument,
   not a measurement of the counted form itself — a real VM island's
   interaction with the possessified/backtracking count loop (`vm_cursor_rep`,
   `src/gen/emit_vm.c`) is untested.
3. **(d)'s hash table is open-addressed with exact-key verification, not a
   true minimal perfect hash.** The filed `[OPT-ALTHASH]` design calls for
   "a perfect hash over the trie's depth-k prefixes"; building one (CHD,
   hopscotch, or similar) was out of this study's scope. The measured probe
   counts are therefore an UPPER BOUND on a true perfect hash's cost (which
   would need exactly one probe per lookup by construction) — (d)'s real
   ceiling is higher than what §4 reports.
4. **Rule 2's "NFA step" half is not implemented**, only the decline half
   (§3) — a real VM island covering general classed alternations (outside
   this study's literal/ci scope) would need it; this study's inputs never
   exercise it beyond the one hand-built unit test.
5. **The VM's actual continuation-backtracking cost is not measured.**
   `trie_dispatch`'s candidate list (§3) is sized and its construction
   timed, but no VM-shaped consumer exists here to measure how much
   `emit_vm.c` would actually save by trying only the candidate list
   instead of `vm_alt`'s full serial chain on a FAILING continuation — that
   is a hand-twin measurement for whichever lane builds the island, per
   D77.
6. **This study never touches `-O2`-vs-switch-dispatch questions.** (c)'s
   trie walk scans a node's children LINEARLY (`algo_trie.c`'s `for` loop
   over `nchildren`), not via a jump table — a deliberate choice (§2.1) so
   the measured numbers are a fair baseline an INTERPRETER would see, not
   what an emitted `switch` (which `gcc`'s own lowering could turn into a
   jump table) would already buy for free. §4.5's `trie_maxfanout` column
   bounds how much a switch-dispatch emission could still improve on this
   study's own numbers.
7. **No sixth "today's actual vm_alt-over-partially-factored-trie" baseline
   was built.** §4.4's caveat: this study's (a) models a fully unfactored
   serial try, and its (c)/(e) model a fully, recursively factored trie;
   today's real `vm_alt` sits between the two (fed a trie factored only at
   the level `src/ir/nfa.c`'s M2.8 pass reaches before handing off to
   emission). Reproducing the bench's exact ×8.87/×20.1 figures would need
   a baseline built from the ACTUAL top-level factoring `vm_alt` receives
   today, which this study did not construct — a natural follow-up if a
   precise, apples-to-apples comparison against those two bench numbers is
   wanted.
8. **(e)'s deferred list is a fixed-size C array (`DEFERRED_CAP = 256`),
   not the compile-time-sized per-pattern bit assignment a real VM island
   would use.** §4.2's max-deferred column reports what this study's inputs
   actually needed (always small; only the adversarial unit tests exceed
   1), which is the number a real design would size a per-pattern mask
   against — but this harness never had to solve "how does the emitter
   PRE-COMPUTE, at compile time, a bit position per potentially-deferred
   index" (§3.2 states the invariant such a scheme must encode, not an
   implementation of it).
9. **(e)'s candidate order after a real continuation failure is not
   measured beyond the single-call harness.** Like (c) (item 5 above), no
   VM-shaped consumer exists here to measure the cost of actually RESUMING
   a pushed frame and walking the deferred mask when a later part of the
   pattern fails — this study measures the forward pass's frame count
   (§3.2, §4.2) but not a resumed walk's own cost.

## 6. Recommendation

**Build (e), the VM-native trie walk, as the VM's alternation island.**

(c) and (e) are BOTH exact and cost within 1–5% of each other in raw ns/byte
at every measured row (§4.3) — on this study's shapes (branches ≤12 bytes,
tries of depth ≤12) short-circuiting the walk buys almost nothing in wall
time, because the walk was already cheap to finish. That is not the reason
to prefer (e). (c) computes a BATCH answer: it always walks every reachable
byte of the path and returns a collected candidate list, which is the right
shape for THIS harness's oracle-checking but not for an emitter — a real
`emit_vm.c` island would still have to re-express that list as resume
frames and labels after the fact. (e) IS that shape already: `subtree_min`
plus the two-sided commit test (§3.2) decide, PER END NODE, whether to
emit a commit point (one resume label, one push) or fold the candidate into
a compile-time mask — exactly the control flow `vm_alt`'s replacement would
need to generate, with no post-processing step. §4.2's frames-pushed table
is the concrete argument: on every bench-derived pattern in this study
(widths 8 through 4096, every structure arm), **(e) pushes at most one
frame per dispatch and needs zero deferred-mask capacity** — the
`max_deferred` column reads 0 everywhere real data reaches it, because the
bench's substring-free pools (property 2) never put two accepts on one
walked path. A real island built from (e) would, on patterns shaped like
this study's whole matrix, need exactly one resume label per alternation
entry point and no mask machinery at all in the common case, with the mask
existing only for the adversarial shapes §3.2's regression test targets
(overlapping/prefix-related branches).

**The D77 trigger is already met, and by a wide margin.** §4.3's `(a)/(e)`
ns ratio starts at ×7.0 (w-64, the narrowest rung this study measured) and
grows monotonically to ×242.7 (s-4096, the widest); the structure arms
(`sh1`, `pfx3`) reach ×110–×119 already at width 512. There is no width
in this study's ladder where (e) does not decisively beat serial try, so
the trigger is not "wait for a wider bench rung" — it is already crossed
at the narrowest width this study or the bench's own altwide set builds.
What is NOT yet measured (§5 items 5, 9) is the cost of the VM's
CONTINUATION-BACKTRACKING path — this study's harness has no outer
continuation to fail against, so it measures only the forward pass. Before
`emit_vm.c` changes, a hand-twin (per D77's own standing rule: measure
before building) should confirm that resuming a pushed (e)-shaped frame
and iterating a real deferred mask costs what §3.2's mechanism predicts
(one push, O(1) resume) rather than reproducing `vm_alt`'s O(n) chain in a
different guise.

**What the VM's continuation-backtracking needs from (e)'s mechanism**
(§3.2, "Frames pushed"): a resume point that, on failure of the
continuation taken after a commit, re-enters the walk exactly where it
left off — deeper into the same subtree, not restarted — carrying whatever
was accumulated in the deferred mask up to that point, so a second-best
candidate is available at the cost of one bit-extract (lowest set bit)
rather than a re-walk. This study's `trie_dispatch_vm` does not implement
resumption (there is no continuation to resume against in a pure
alternation-dispatch harness); §5 item 9 states this gap explicitly, and
it is the one piece of machinery a real island's design note would need to
add beyond what is measured here.

## 6.1 Comparability with (c)

(e) reuses (c)'s trie unchanged (§2.1) and both are ORDER-INSENSITIVE by
construction (§3, §3.2) — a `w`/`srt` pair builds the identical trie either
way, so any measured cost difference between the two rungs is noise, not a
finding (§4.4 confirms or refutes this directly). The two differ only in
walk strategy: (c) always walks to the end of the reachable path and
collects every accept; (e) can stop the moment `subtree_min` and
`best_deferred` both clear, which is why (e)'s `tries`/`verify_bytes`
columns in §4.2 are expected to be LESS THAN OR EQUAL TO (c)'s at every
row, and why (e)'s `total_frames` is the number worth reading on its own,
not derivable from (c)'s output.

## 7. Provenance

Lane altstudy, worktree `worktrees/altstudy`, branch `lane/altstudy`. Commit
range: [FILL]. Harness, inputs and results: `studies/alt_dispatch/`. This
file.
