# Executive summary: pcrec-bench altwide@0.2, noedge, and cc re-run night, pin 1989c62

Overnight window 2026-09-02 23:58 to 2026-09-03 06:26 EDT, four passes back
to back at pcrec pin `1989c62` (abi 15): `altwide@0.2`'s first sample (six
pinned testees), the raised-cap pair (`auto-bigcap`, `vm-bigcap`), the
`-fno-scan-edge` counterfactual on `loglines@0.1`, and a clang-only re-run
of the one `bounded@0.3` cell pcrec's `[CC-DIFF]` disputes. Eleven cells,
eleven measured, every one at attempt 1, no retries, no cap kills; store
grew to 122 (112 measured). This reads pcrec-bench's ledger
`docs/dev/ledgers/2026-09-03-altwide-0.2-noedge-ccrerun-1989c62.md` and
outbox O-15, with pcrec's own answer I-39 cited where it settles an ask.

## 1. Findings

- **The refusal boundary is one rung wide, on both engine routes.**
  `w-256` compiles with 2.3% headroom on the DFA route's 1,000,000-byte
  source cap and 31.8% headroom on the VM route's 500,000-byte code cap;
  `w-384` refuses on both, 43% over on the DFA side, 1.7% over on the VM
  side (ledger §3.1). **Means:** the two caps bound different things, the
  DFA cap bounds emitted C source, the VM cap bounds straight-line branch
  code, and they exist for different reasons. That both routes refuse at
  the same width is a coincidence of the two cap values, not a shared
  mechanism: extrapolating `w-256`'s per-branch rate, the DFA route would
  cross near width 262 and the VM route near 375 under the other's cap
  value. **Changes:** retires the 0.1-era "at or above 512 refuses" with a
  bracketed rung, and is candidate 3's evidence base; the refusals sit
  between pcrec and this bench's largest measured wins (ledger §7).

- **Branch order costs the VM engine a large, width-growing penalty the
  DFA route never pays.** `srt-256` (`w-256`'s branches sorted by first
  byte) produces a byte-identical DFA artifact but a VM artifact 11.5%
  smaller and **×8.87 faster**; at 512 under the raise the same reordering
  is worth **×20.1** (ledger §2.5, §4.4). **Means:** the VM tries an
  alternation's branches one at a time, one live frame, so matching the
  last of 512 branches costs 511 push/fail/pop/dispatch round-trips on one
  subject byte. The DFA route never pays this: the NFA builder already
  composes a flat alternation into a priority-preserving prefix trie, and
  the DFA is that trie determinized, so branch order cannot affect it
  (journal part 7 addendum 3; I-33, I-39 (i)). **Changes:** this is
  `[ENG-ISL]`'s first named island candidate, now with a measured need;
  I-39 (i) confirms the attribution stamps (`RX_ALTCLS_MERGES`,
  `RX_ALTCLS_FACTORED`) already exist in the common stamp block
  (`src/gen/emit_dfa.c:285-286`, `docs/spec/match_api.md:2429`), so
  candidate 2's mechanism can now be attributed, not just observed.

- **Under the raised cap the flat DFA line holds to the widest rung
  tested, against an extraordinary JIT margin.** Over 8..2048,
  `pcrec-auto`'s throughput rises ×2.21 while interp rises ×643 and the
  JIT ×939; at `w-2048` auto is **×627 faster than the JIT** on
  throughput, and at `s-4096` the ratio reaches **×3,496**, the largest
  this bench has recorded (ledger §4.2). **Means:** a determinized trie
  walks one table lookup per byte regardless of branch count, so width is
  absorbed once, at construction, not re-paid per match; a backtracker
  without that structure re-tries branches per candidate start, so its
  cost scales with branch count directly. **Changes:** the headline
  evidence for candidate 3, that the size caps, not per-byte cost, are
  what stands between pcrec and this bench's largest wins.

- **The flat line eventually breaks, and two independent stamps explain
  why, one rung apart.** Throughput steps ×1.42 from `w-384` (3.07 ms) to
  `w-512` (4.16 ms), where `RX_DFA_TABLE` moves `premultiplied` to
  `mixed`; the match regime steps ×16.2 one rung later, at `w-1024`,
  where `match=` moves `unwrapped` to `search-filter` (ledger §4.2).
  **Means:** these are two separate representation choices triggered by
  the automaton's state and class counts, not by width itself; width is
  only the variable used to reach the thresholds. I-39 (ii) confirms a
  raised cap moves no DFA-side size term: the DFA route has no
  unroll-style ladder, only these count-driven choices. **Changes:**
  future DFA size work should target the table-encoding and match-entry
  transitions directly, not "width" as a proxy.

- **Compiling the widest VM artifacts is gcc's problem, not pcrec's.**
  gcc time on emitted VM code grows superlinearly: 3.21-4.71 s at
  `w-384`/`w-512`, 165.92 s at `s-4096`, 304.55 s on its whole-subject
  form; the DFA route's cost stays bounded by pcrec's own subset
  construction (0.5-19.8 s, gcc under 1 s throughout) (ledger §4.3).
  **Means:** the VM route emits one large flat function, exactly the
  shape gcc's compile time scales badly against; the DFA route's
  expensive step is pcrec's own construction, bounded and already paid
  before gcc sees the file. **Changes:** `[LIM-2]`'s projected-size bail
  must live inside DFA construction, not as a post-emission check; the
  ledger prices the alternative at ×190 (113.8 s of refusal cost per pass
  vs the VM route's 0.6 s) (ledger §3.3).

- **The scan edge's real cost is measured for the first time, smaller
  than the earlier scratch reading.** `pcrec-auto` vs `pcrec-auto-noedge`
  on `loglines@0.1`: `iso-ts` (8 edge blocks in search, 4 in match) is
  ×1.089 faster with the edge removed; zero-edge patterns are flat within
  the 1.32% same-pin floor (ledger §5.2, §5.6). **Means:** the scan edge
  is a per-iteration `if` block the DFA loop pays once per edge, per
  byte, whether or not a run is there (journal part 6, from
  `emit_dfa.c`'s `emit_scan_loop`); `iso-ts` pays most because it has the
  most edge blocks. The earlier ×1.70 was a three-trial scratch reading;
  pinned, five-trial, it is ×1.089. **Changes:** replaces the scratch
  figure as `[OPT-EDGE]`'s formal BEFORE; the cost is sublinear in edge
  count (eight edges buy ×2.8 what one buys, not ×8), so an O(1) rewrite
  may recover less than the full 8.2%.

- **The one disputed cell reproduces on the arm that was re-measured, and
  stays open on the arm that was not.** `floor`/match/`auto` under clang
  reads 217.5 ns tonight vs 217.6 ns on 2026-09-02 (0.05% apart); the
  disputed ratio against gcc reproduces to 0.432, but that gcc column is
  the SAME 2026-09-02 record, not re-run tonight, so pcrec's own reading
  of 307 ns on the byte-identical artifact stays unresolved (ledger §6,
  §6.3). **Means:** a two-arm ratio needs both arms re-measured in one
  window before it is settled; one stable arm is evidence against a
  transient, not an arbiter of a disagreement in the other arm. I-39 (v)
  proposes a concrete probe: build the gcc arm twice, with and without
  `-falign-functions=64`, since a 48-instruction loop straddling a
  64-byte line boundary can cost close to the observed ×1.6. **Changes:**
  bench-side follow-up 1 (both arms, one window, alignment probe folded
  in); pcrec's answer stays "layout, not content" until that runs.

- **The structure-arm predictions mostly held, with one clean refutation
  answered from source.** `sh1-256` gets the predicted single-byte
  `memchr` prefilter; `pfx3-256` (shared 3-byte prefix) was predicted an
  offset-set prefilter but also gets `memchr`; `ci-256` (`w-256` under
  `(?i)`) is the only sample pattern whose scan class compiles a `bitmap`
  edge where 31 of 34 siblings compile `range` (ledger §2.8, §2.9).
  **Means:** I-39 answers both. `memchr` is the correct selection
  whenever offset 0 has exactly one candidate byte, and any shared prefix
  makes offset 0 a singleton; the offset-set prefilter is for a different
  shape (wide early offset, narrow later one). The `range` body applies
  only to one contiguous byte range; `(?i)[a-z]` folds to `[A-Za-z]`, two
  disjoint ranges, so it falls to `bitmap`. **Changes:** asks (iii) and
  (iv) close; P15 is retired as mis-predicted; `[OPT-NEG]`'s filed row
  (a cheaper multi-range test) is where a `ci`-style improvement would
  land if chartered.

- **The one shape where the JIT still wins closes by the very next
  rung.** `pfx3-256`/throughput is the only cell in the 33-pattern set
  where the JIT beats `pcrec-auto` (×1.04); pcrec's cost is flat 256 to
  512 while the JIT's doubles, so `pfx3-512`, reachable only under the
  raise, has auto winning ×2.22 throughput / ×5.88 search (ledger §4.5).
  **Means:** the 2026-09-02 ledger flagged this shape as the JIT's one
  measurable edge on something pcrec could not even compile; the raise
  removes that, and width closes the rest on its own. **Changes:**
  candidate 6 stays lowest-ranked, smallest margin, self-closing.

## 2. Surprises

- **The 0.1 cell-time anchor was mislabeled, and correcting it reverses
  this window's own comparison.** The NOTES said the measured 0.1 auto
  cell was 30 minutes against the VM's 4.9; the raw log shows 30.0
  minutes was `pcre2-jit`'s cell, auto's was 4.8 (ledger §1.6). **Why
  invisible:** the two testees ran back to back and nobody checked which
  cell line named which testee until this window's audit. **Changes:** at
  0.2's widths the true ordering flips, the VM route's successful
  compiles now cost ×5.1 what the DFA route's do (334.0 s vs 65.5 s per
  pass), because 40 VM artifacts up to 474 KB cost gcc more than the DFA
  route's 15-37 KB ever does, even though DFA refusals are individually
  far pricier (ledger §3.3). Follow-up 2 corrects the NOTES file.

- **The JIT does not scale the way the ladder predicted.** interp rises
  with slope near 1.0, as predicted; the JIT rises with slope 1.39 in
  irregular jumps (×2.24 from 64 to 96, only ×1.10 from 96 to 128, ×1.98
  from 128 to 192) (ledger §2.2). **Why invisible:** 0.1's three-point
  ladder was too coarse to separate step behavior from a smooth slope.
  **Changes:** nothing is chartered, this is a libpcre2 fact, but a
  single-width JIT comparison can now land on an unrepresentative step.

- **The DFA route's source size sits below every model the bench
  proposed.** `s-512`/`w-512` and `s-256`/`w-256` both measure smaller
  than both a trie-node model and a branch-byte model (0.534 vs a 0.71
  prediction; 0.464 vs a 0.61 prediction) (ledger §2.6, §2.7). **Why
  invisible:** 0.1 never reached a compiling pair at this length. **Changes:**
  the raised-cap arm confirms the same direction a third time (`s-4096`
  smaller than `w-2048`, where both models predicted the reverse), a
  pattern no single-quantity size model fits (ledger §4.2).

- **`pcrec-auto` is not indifferent to search structure.** `sh1-256` and
  `pfx3-256` run ×5.8 and ×8.0 faster than auto's own flat throughput
  band, so the prefilter helps a DFA-selecting config too, just less than
  it helps a backtracker (ledger §2.8). **Why invisible:** the flat-line
  finding (P9) was read as "auto doesn't care about structure," but 0.1
  never tested structure arms wide enough to separate that from "doesn't
  care about width." **Changes:** P15's auto-band clause is retired as
  refuted; future flat-line claims about auto must name the axis.

- **The branch-order penalty worsens with width, and produces the only
  cells where pcrec's VM beats the JIT.** ×8.87 at 256, ×20.1 at 512;
  `srt-512` on the raised VM beats the JIT ×2.18 throughput / ×2.13
  search, the only two cells in the set (ledger §4.4). **Why invisible:**
  0.1 had no compiling `srt` rung at all; 0.2's twinned pair at two
  widths is what makes the trend readable. **Changes:** follow-up 5 adds
  `srt-1024` under the raise for `altwide@0.3`, since two points cannot
  fix whether the curve is linear or steeper.

## 3. Impact

What was a coarse boundary is now bracketed. The 2026-09-02 ledger could
only say both routes refuse somewhere at or above width 512; this window
brackets both to the same single rung and prices what each refusal costs
on either side of it. The branch-order effect was a named mechanism
(I-33) with no number; it now has two, at two widths, growing with
width, and produced the only cells where pcrec's own VM beats a mature
JIT. The scan edge's cost went from a scratch three-trial smoke reading
to a pinned, five-trial figure roughly two-thirds the earlier estimate.

Priorities move. `[OPT-EDGE]` is now sized on ×1.089, not ×1.70, capping
how much its dispatch rewrite can be worth on `iso-ts` alone, and the
sublinear-in-count finding warns an O(1) rewrite may not recover the
whole cost. `[ENG-ISL]`'s alternation-as-trie-dispatch candidate, filed
as a hypothesis on 2026-09-02, now carries a measured need (×8.87 at 256,
×20.1 at 512, growing with width), and I-39 closes the one gap that stood
between it and acceptance, the ALTCLS attribution stamps already exist.
`[LIM-2]`'s bail is priced at recovering up to 113.8 s of refusal cost
per pass. `[OPT-ALTHASH]`'s block-hash idea stays unchartered but now
sits beside a concrete measured curve to judge its trigger against.
`[CC-DIFF]`'s gcc-side question is narrower, a specific testable
mechanism (code alignment across a 64-byte line) rather than an open
"something differs."

What is fragile or unknown: the gcc half of `[CC-DIFF]` is unresolved
after two windows, and the alignment hypothesis is a proposal, not a
finding. The scan edge's per-edge cost is confirmed in kind but not in
shape, three points fit a fixed-entry-plus-shallow-per-edge model better
than a pure per-edge one, too few points to be confident of the form.
Whether a raised cap moves a DFA-side size term is answered negative for
the stamps this bench can read (I-39 (ii)), but the DFA route prints no
size-term stamp at all, so that answer rests on absence of evidence.

What the instrument proved: eleven cells measured on the first attempt,
with the window's worst interference reading (70.93% other-core busy)
landing on the one cell this window existed to settle and visibly not
moving its numbers, the clang re-run agreed with the prior window to
under 1% on all 126 comparable cells. The cell-time anchor correction is
itself proof of the instrument's value, a plan-level estimate built on a
mislabeled log line would have budgeted the wrong cell as expensive, and
only a raw-log audit caught it.

## 4. Next steps

**(a) The bench's five asks, with I-39's answer:**

- (i) ALTCLS stamps: already exist (`src/gen/emit_dfa.c:285-286`,
  `docs/spec/match_api.md:2429`); no pcrec change owed.
- (ii) Does a raised cap move a DFA-side size term: no; the DFA route has
  no unroll-style ladder, only count-driven choices a cap cannot move.
- (iii) Does `(?i)` select the bitmap edge on `ci-256`: yes, confirmed
  from `scan_range_applies`; filed under `[OPT-NEG]`, not chartered.
- (iv) Is `pfx3-256`'s `memchr` selection right: yes, any shared prefix
  makes offset 0 a singleton by construction.
- (v) The gcc half of `[CC-DIFF]`: unresolved; pcrec proposed the
  `-falign-functions=64` probe, owned jointly with the both-arms re-run.

**(b) The bench's own follow-ups (ledger §9).** Re-run the I-37 cell with
both arms in one window plus the alignment probe. Correct the NOTES
cell-time anchor (auto's 0.1 cell was 4.8 minutes, not 30). Record that
`s-512` is not a wide rung (twelve need the raise, not thirteen). Take a
second noedge sample for `http-5xx`/`ipv6`, near the reproducibility
floor. Add `srt-1024` under the raise to `altwide@0.3`. Give the
raised-cap arm a standing cell-cap note (`pcrec-vm-bigcap` needed
14,400 s against the 5,400 s default).

**(c) pcrec's own queue, as the journal states it today.** The bench's
`bounded@0.3` STEP 2 AFTER runs tonight, Frank's go confirmed directly to
the bench (journal part 16). `[TT-12]` STEP 1 (pairwise test-axes timing)
is in flight (lane tt12b). `[CC-DIFF]` STEP 1 (both spellings,
`always_inline` on frameless VM helpers and uniform-table constant
folding in the DFA step/accept bodies, one abi event) is chartered and in
flight (lane ccdiff1). `[OPT-EDGE]`, `[LIM-2]`, and the strengthened
`[ENG-ISL]` island candidate stay queued behind the emitters `[CC-DIFF]`
STEP 1 and `[OPT-5]` STEP 2 already touch, per the standing rule that
emitted-scaffolding changes ride one abi event at a time.
