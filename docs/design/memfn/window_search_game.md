# Gaming out "search for the window" (D161) before any request is written

Lane `wingame`, 2026-10-11, from main `aa2ddb1d` (abi 75). This is a design study.
Nothing under `src/`, `memfn/` or `tests/` changes. Every number here is a COUNT
over subject bytes, and nothing reads a clock. The instruments are in
`window_search_game/` (see its CLAUDE.md). The population tables live in
`window_search_game/data/summary.md`, written by `chain.sh` and committed with
its TSVs.

Frank asked (D161, 2026-10-11):

> Come up with our potential kit responses, then see what it might choose on a
> bunch of patterns, or whether it could choose given that information. One
> concern: how does it weigh one span against another if it's not doing the
> forward search for the beginning? Perhaps that's part of it.

## 0. The answer in brief

- **The kit cannot rank spans from D161's inputs alone once the spans differ in
  window width.** It can rank the STOPS each span costs its own scan. The frequency
  table predicts a one-position stop count to within 0.3x-6.8x (median about 1.7x)
  on the bench subjects. What separates spans is the consumer's work per SURVIVOR: a
  forward DFA re-steps `move_back + len` bytes, while a backtracker makes
  `overshoot + 1` anchored attempts. Those two shapes rank spans in OPPOSITE
  orders on real patterns (§5.1, `wild-logparse-syslogbase-expanded`).
- **Per-span overshoot is necessary but not sufficient.** The contract also
  needs (a) a CONSUMER PRICE, which is a few numbers per route: a fixed cost per
  candidate, a cost per window byte, a cost per possible start, and the cost per
  byte of doing no window search at all. The last one is what any "is this span
  worth using" decline needs. It also needs (b) a MINIMUM offset beside each
  maximum, because pcrec's req facts carry maxima only, so an overshoot cannot be
  derived from them today. On the population, the consumer decides WHETHER to search
  far more often than WHICH span (18 decline flips against 1-3 span flips, §5.4).
- **The survivor rate is where the frequency table fails.** Under independence it
  under-predicts the survivors of a multi-position span by 21x to about 1,700x on
  the bench subjects (§5.3), and survivors are exactly what the window cost
  multiplies. Either pcrec states a joint rate per span (a findings-family run
  rate, which D83's addendum already permits), or the kit's choice among
  similar-stop spans is a guess.
- **The kit does not need to own the look-forward.** It needs its PRICE. The look-forward
  is the engine, and moving it into the kit would move the engine. A
  three-coefficient consumer price plus a minimum offset is enough for every flip
  this study found.
- **The contract's biggest miss is not span ranking but the UNBOUNDED move-back.**
  On 15-22 % of the unanchored bench and corpus patterns that have a span, the
  rarest position sits behind an unbounded repeat (`\w+@`, `key\h*=`).
  Today pcrec serves those through the reverse pass or a set-lead. D161 cannot
  express them (§2).

## 1. The span list, derived

### 1.1 Definition used here

A pattern flattens to a sequence of consumed POSITIONS (one byte set each) and
GAPS (a variable width `[lo, hi]`, `hi` possibly unbounded). A SPAN is a maximal
run of consecutive positions. Every span is necessary: on every path, every match
carries those bytes at those positions relative to the span's own start. If
the span's start lies `[omin, omax]` bytes after the match start, then

    move_back = omax          (window beginning = span start - omax <= match start)
    overshoot = omax - omin   (how far before the match start the window may begin)

A prefix span has `0/0`. `[a-z]{1,8}@example\.com` has a second span
`@example.com` with `move_back 8, overshoot 7`. This is exactly D161's "an inner
span might be 7".

### 1.2 Where pcrec's facts already supply pieces of it

| piece of the span list | pcrec fact today | what is missing for D161 |
|---|---|---|
| prefix span classes | `kset_walk` (E3, the NFA walk from `anch_start`) | `--emit-facts` prints wide offsets as `[N]` (a count). The walk keeps going past the first gap as UNIONS, which is no longer a span |
| offset-0 class | `start_set` | none (it is the prefix span's first class) |
| one inner literal span | `req_run` window (+ cube masks) | its CLASSES beyond 2-member cubes |
| its move-back | `req_run_maxoff` / `req_landmark_maxoff` (the handoff's K) | the MINIMUM offset, so no overshoot (§0) |
| single-byte inner spans | `req_set` + `req_set_maxoff` | minimum offsets again; every member is a 1-position span |
| a fixed-offset run | `run_pin` | none (a pinned run is part of the prefix span) |

So pcrec already produces a prefix span, one literal inner span with its move-back,
and the necessary single bytes with theirs. It does not produce full classes for
inner spans, minimum offsets, or more than one multi-byte inner span. D161's
"ONE producer of span facts" is therefore a NEW walk, a generalization of the req
walk's `RbRun.off` bookkeeping to `(classes, omin, omax)` per span, and not a
re-labelling of existing facts.

### 1.3 The extractor and its control

`spans.py` derives the list independently of pcrec. It uses Python's own regex
parser after a small PCRE-to-Python spelling pass, in byte mode with ASCII
classes (pcrec's `byte` encoding). Its control is pcrec's own k-set walk: every
fixed prefix position's class SIZE must equal the walk's size at that offset
(`run_game.py`'s `kset_agree` column, summary §A3). The extractor shares no code
with pcrec. Where it loses information it says so in a `notes` column and never
widens silently (§2.2).

## 2. What the contract cannot express

### 2.1 Census

Parse-only (no compile), the bench's capability/loglines/syntax sets plus a
deterministic sample of 150 corpus `pattern` lines. The chain recomputes this table
in `data/summary.md` §A beside the k-set control.

| set | patterns | unparsed | anchored `^` | unanchored with a bounded inner span | inner span with overshoot > 0 | >= 2 bounded spans | has an unbounded span | rarest POSITION in an unbounded span | an unbounded span >= 2x rarer than every bounded one |
|---|---|---|---|---|---|---|---|---|---|
| capability | 71 | 1 | 19 | 5 | 5 | 2 | 19 | 11 | 8 |
| loglines | 11 | 0 | 0 | 4 | 4 | 4 | 3 | 2 | 2 |
| syntax | 95 | 12 | 3 | 6 | 6 | 4 | 20 | 12 | 9 |
| corpus (150) | 150 | 19 | 21 | 16 | 16 | 8 | 25 | 15 | 6 |

Two readings:
- **Span-vs-span choice among bounded spans is rare.** Only 18 of the 327
  patterns have two or more bounded spans. The common choice is "the prefix span
  or one bounded inner span" and, more often, "a bounded span or a rarer
  UNBOUNDED one".
- **Every bounded inner span here has overshoot > 0.** No inner span sits at a
  fixed offset; if it did, it would have merged into the prefix span. So "inner"
  and "overshoot > 0" are the same population, and the overshoot question is never
  vacuous.

### 2.2 The cases, one by one

| case | example | what D161 can say | consequence |
|---|---|---|---|
| unbounded move-back | `\w+@example\.com`, `key\h*=\h*value`, `ERROR: [a-z]+ failed` | nothing: `move_back = inf` | The rarest landmark is unusable. Today's reverse pass / set-leads / `rev-inner` serve it, and these are all look-BACK, which D161 leaves out. |
| a span on some paths only | `x(?:foo\|barbaz)?y`, `(?:GET\|POST) ...` | only the common head/tail (cube hull) survives | `alt-dropped` on 27/71 capability patterns. A per-branch span is a DISJUNCTION of windows, and there is no field for it. |
| variable distance between two spans | `ERROR.{0,200}?timeout` | two independent spans, each with its own move-back | The kit cannot ask for "span A, then B within 200". The conjunction is look-forward. |
| lo copies of a `{lo,hi}` repeat on the right | `\d{2,5}x` | `x` with no `\d\d` before it | `rep-right`, small (5/71). It is a producer choice and not a contract gap: both attachments are necessary. |
| anchors | `^abc` | the window search is moot (one start) | 19/71 capability. `(?m)^` line anchors are a different window kind (`[MATCH-SPLIT]`). |
| zero-width assertions, lookaround | `\bfoo\b`, `(?<=x)y` | ignored: a superset, so sound | A lookbehind's own bytes are a span BEFORE the match start (a negative move-back), which the contract cannot state. |
| backreference / recursion / `\K` | `(\w+)\s+\1` | an unbounded gap | Sound. `\K` moves the reported start, so the window's meaning shifts. |
| utf8 | `\p{L}+@`, `é` | not measured (the utf8 set is excluded) | A multi-byte character is a SPAN of byte classes only when its width is fixed. A class like `[aé]` has variable width and breaks the span, so the encoding has to be in the producer. |

## 3. Plausible kit policies

Each policy reads only D161's inputs (the spans and the frequency table) except
where a parameter is named. The candidate FORMS are: one anchor position scanned
(memchr / class scan) with the whole span verified at each stop, or two anchor
positions at their fixed distance (a packed pair), over BOUNDED spans only.

| policy | chooses by | extra input it needs |
|---|---|---|
| P1 `rare-pos` | the single rarest position anywhere | none |
| P2 `rare-span` | the smallest joint (independence) span rate, scanning its rarest position | none |
| P3 `pair` | the two rarest positions of one span (smallest stop rate) | none |
| P4 `selfprice` | its own scan price + stops x verify price; declines above a stop rate of 0.25 | kit-own constants only (form prices, `SELF_DECLINE`, all UNMEASURED, D149) |
| P5 `window(consumer)` | P4 + survivors x consumer price; declines when not cheaper than the consumer meeting every byte | `consumer`: per-candidate, per-window-byte and per-start costs, and the no-search cost per byte (NOT in D161) |
| P5 under the subject's own rates | P5-dfa with the subject's byte histogram as the table | a control for prior mismatch, not a policy |

`game.CONSUMERS` holds two consumer shapes. `dfa` = 20 per candidate + 1 per
window byte: a forward DFA started at the window beginning. `vm` = 40 per
candidate + 60 per possible start: anchored attempts. Both are illustrative and
UNMEASURED. They are parameters on purpose, so that a reader can see which
choices depend on them.

## 4. Results

### 4.1 Hand-picked cells

These are the bench patterns where a span choice exists, simulated on the bench's
own 256 KiB throughput subjects (sha256-checked against the bench manifests). They
were first run during the box hold (8 single compiles); the numbers below are the
population run's (`data/spanforms.tsv`, same counts). The columns are stops,
survivors, window bytes (`move_back + len` per survivor) and possible starts
(`overshoot + 1` per survivor). `work` applies §3's illustrative prices, in units of
one DFA step, to the MEASURED counts. "No window search" is the consumer meeting
every byte: 0.26 M (dfa) and 15.7 M (vm) on every 256 KiB subject.

| pattern (subject) | span | mb / ov | stops | survivors | window bytes | starts | work dfa | work vm |
|---|---|---|---|---|---|---|---|---|
| `wild-logparse-syslogbase-expanded` (capability) | `[16]` prefix | 0 / 0 | 58,874 | 58,874 | 58,874 | 58,874 | 2.01 M | **6.66 M** |
| | `\x20` inner | 9 / 7 | 30,634 | 30,634 | 306,336 | 245,072 | 1.23 M | 16.24 M |
| | no window search | | | | | | **0.26 M** | 15.7 M |
| `level-context` (loglines hit) | `[EFC][RAR][RTI][OAT]` prefix | 0 / 0 | 1,209 | 96 | 384 | 96 | 0.03 M | 0.04 M |
| | `timeout…` hull, inner | 205 / 201 | 23,385 | 48 | 10,128 | 9,696 | 0.43 M | 1.00 M |
| `ipv4` (loglines hit) | `\d\.` #0 | 2 / 2 | 5,863 | 4,050 | 16,200 | 12,150 | 0.16 M | 0.96 M |
| | `\d\.` #1 | 6 / 4 | 5,863 | 4,050 | 32,400 | 20,250 | 0.18 M | 1.44 M |
| | `\d\.` #2 | 10 / 6 | 5,863 | 4,050 | 48,597 | 28,350 | 0.20 M | 1.93 M |
| `http-5xx` (loglines hit) | `"[GPD..][EOUA..][TSA..]` prefix | 0 / 0 | 2,168 | 144 | 576 | 144 | 0.03 M | 0.04 M |
| | `\x20[^ "]` inner | 7 / 3 | 25,455 | 23,203 | 208,827 | 92,812 | 0.94 M | 6.76 M |
| `kv-quoted` (loglines hit) | `[a-z_]` prefix | 0 / 0 | 122,979 | 122,979 | 122,979 | 122,979 | 4.00 M | 13.7 M |
| | `="` inner | 32 / 31 | 2,279 | 96 | 3,264 | 3,072 | 0.04 M | 0.22 M |
| `qnt-quest` (syntax) | `colo` prefix | 0 / 0 | 8,221 | 565 | 2,260 | 565 | 0.10 M | 0.15 M |
| | `r` inner | 5 / 1 | 14,150 | 14,150 | 84,900 | 28,300 | 0.52 M | 2.41 M |

What the policies chose (`data/choices.tsv`):
- **syslogbase**: P1-P4 pick the inner `\x20` (rarer by the table: 0.125 against
  0.276). P5-dfa DECLINES (stepping every byte, 0.26 M, beats both spans). P5-vm picks
  the prefix, which is also pcrec's shipped choice (`first-class-bounded`, a VM
  hybrid). Under the VM consumer, the consumer-blind pick costs 2.4x the shipped one.
- **kv-quoted**: every policy picks the inner `="`, and so does pcrec's shipped
  handoff (K = 32). D161's span is exactly what pcrec already searches here. The
  default table anchors a one-position scan on `=` (2,279 stops), while the subject's
  own rates anchor on `"` (346 stops in the fail subject, 2,168 in the hit subject).
- **ipv4**: the three `\d\.` spans have IDENTICAL stops and survivors, because a stop
  is the same `.` whichever octet the kit says it is. Only move-back and overshoot
  separate them. The tie-break on move-back is right, but only because it happens
  to coincide with the consumer cost.
- **http-5xx**: the inner span's verify is weak (91 % of stops survive), so its window
  cost dominates: 209 K window bytes against 576.

### 4.2 Population

`chain.sh` built this worktree's `pcrec` and ran `run_game.py` over 327 patterns:
177 bench (capability, loglines, syntax) plus 150 corpus, the corpus sample simulated
on capability's `t-256k`. The whole run took about 30 s. `data/summary.md` is its
output.

- **§A**: the census reproduces §2.1's parse-only table. The k-set control reads
  **582 of 582** fixed-prefix positions agreeing over 166 patterns. Its first run
  found three extractor defects (POSIX classes, `\v`, and `(*UCP)`'s wider byte
  classes), all fixed before these numbers; `(*UCP)` patterns are now declined as
  unparsed.
- **§B**: P1, P2 and P3 pick the same span on every one of the 249 unanchored
  patterns with a bounded span. Only the priced policies differ, and they differ
  mostly on WHETHER to search. P5-dfa declines 41 times and P5-vm 23. P4 declines 25
  times on its own kit-only threshold.
- **§B2**: 19 patterns differ between P5-dfa and P5-vm. In 18 of them the difference
  is the decline. In one, `corpus/c134`, it is the span (below).
- **§D**: there are 22 pattern x subject cells with two or more bounded spans. On 3
  of them the span argmin flips between the DFA price and the VM price:
  `wild-logparse-syslogbase-expanded`, and the corpus test patterns
  `((a)|b){1,3}?c` and `[a-]{1,3}?(?:\B|)a`. Ranking by the table's predicted stops
  and ranking by measured stops disagree on 1 cell.
- **The survivor-ratio line**: measured/predicted survivors over 329 forms are p10
  0.14, p50 1.6, p90 240, max 469 (+1-smoothed, so the large ratios read low).
- **§C**: summed counts per set and subject, with SHIPPED beside every policy. The
  work columns depend on §3's unmeasured prices, so §C is evidence of which COUNTS
  move and not of a winner.

## 5. Frank's concern: weighing one span against another

### 5.1 What the kit can and cannot see

A window search's total cost is

    scan(form) * n  +  stops * verify  +  survivors * consumer(move_back, overshoot, len)

D161 gives the kit everything in the first two terms. The table predicts the stop
count of a one-position anchor to within 0.3x-6.8x on these subjects (§5.3), and the
kit knows its own form prices. The third term needs two things D161 does not
carry: the consumer's PRICE FUNCTION and the SURVIVOR rate.

The consumer's shape decides the ranking:
- **A forward DFA** started at the window beginning pays per WINDOW BYTE
  (`move_back + len`). An inner span with a modest move-back is cheap for it.
- **A backtracker** (the VM, or any anchored-attempt consumer) pays per POSSIBLE
  START (`overshoot + 1`), and each start costs an attempt. The same inner span
  costs it 8x the attempts.

On `wild-logparse-syslogbase-expanded`, scan-only ranks `\x20` (inner, 9/7) first:
30,634 stops against 58,874. The DFA price agrees (1.23 M against 2.01 M). The VM
price reverses it (16.24 M against 6.66 M). pcrec's shipped artifact is a VM hybrid,
and it chose the prefix. A kit that knew only overshoot could not have told these
two consumers apart: it would need to know that the consumer is a backtracker and
what an attempt costs relative to a scanned byte.

### 5.2 Similar stops, very different windows

- **`ipv4`**: three spans with identical stops and survivors (5,863 / 4,050) and
  windows of 16 K, 32 K and 49 K bytes. The table cannot separate them at all, while
  move-back and overshoot separate them completely.
- **`level-context`**: the inner `timeout|refused|…` hull SURVIVES LESS often than the
  prefix (48 against 96 on the hit subject). A survival-only ranking would prefer it,
  and its window is 211 bytes with 202 possible starts. It loses here on stops anyway.
- **`qnt-quest`**: `colo` (8,221 stops) against `r` at 5/1 (14,150 stops). These are
  close on scan cost (0.09 M against 0.15 M). Priced, the gap is 5x (dfa) and 16x
  (vm), because every `r` survives and opens a 5-byte window.
- **`[a-]{1,3}?(?:\B|)a`** (corpus): 10,323 against 9,607 stops. The DFA price ties
  them (0.336 M against 0.335 M), and the VM price separates them 1.9x.

So two spans with similar stop rates do differ hugely in window width, and also in
how often a stop survives (`http-5xx` 91 % against 7 %; `ipv4`'s last span 100 %).
Both differences reach the total only through the consumer's price.

### 5.3 The survival rate is not in the table

On the hand-picked cells, a ONE-position stop rate predicted by the default table
lands within 0.3x-6.8x of the measured count (worst: `slack-webhook`'s `/`,
predicted 1,088, measured 7,379). A multi-position span's SURVIVOR count predicted
under independence is off by:

| span | predicted survivors | measured |
|---|---|---|
| `ipv4` `\d\.` (hit) | 195 | 4,050 (21x) |
| `msc-r-uc` `done` | 1.4 | 665 (480x) |
| `qnt-quest` `colo` | 0.32 | 565 (1,750x) |
| `level-context` prefix (hit) | 0.007 | 96 |
| `kv-quoted` `="` (hit) | 2.9 | 96 (33x) |

Real text is made of words and real partial matches, and the hit subjects' survivors
are mostly true matches (`qnt-quest`'s 565 survivors are its 565 matches). This is
`reqpos_2b.md`'s finding again (run density is joint, the table is marginal, 5x to
3,257x), now on the term that decides span-vs-span. Over the population's 329
simulated forms the measured/predicted survivor ratio is p50 1.6 and p90 240
(`data/summary.md` §D). The median form is a one-position or broad-class span the
table prices well; the tail is every literal-ish multi-position span.

### 5.4 Does the choice flip once the beginning-search cost is included?

Yes, and the population says where:
- **Which span**: 3 of the 22 multi-span cells flip between the DFA price and the VM
  price (syslogbase and two corpus test patterns). On the others the stop counts
  already separate the spans by more than the window prices do. Span-vs-span is a
  real but RARE decision, mostly because two bounded spans are rare (18 of 327
  patterns).
- **Whether to search at all**: this is the consumer-dependent decision that
  happens most often. P5-dfa and P5-vm disagree on 19 patterns, 18 of them on the
  decline. syslogbase is the clean case: the DFA consumer is better off with no
  window search (0.26 M against 1.23 M for the best span), while the VM consumer must
  search (15.7 M without one, against 6.66 M). D161 makes "when a span is worth
  using" the kit's call, but that call is a comparison against the consumer's
  no-search cost, which the kit is not given.
- **The size of a loss when the kit guesses wrong**: 2.4x on syslogbase (VM), and 5x
  (dfa) to 16x (vm) on `qnt-quest`'s near-tie, on the illustrative prices.

The decline counts depend on §3's unmeasured prices. What does not depend on them
is the shape: the same pattern declines under one consumer and searches under the
other.

### 5.5 What the contract needs, as facts

Each item is a fact about the artifact, never a method (D157):

1. **Per span: `omin` beside `omax`** (equivalently move-back AND overshoot). Both
   are in D161's text already. pcrec's producer has to compute the minimum,
   which today's req walk does not carry.
2. **A consumer price, per route of the artifact**: fixed cost per candidate,
   cost per window byte, cost per possible start, and the no-search cost per byte.
   These are pcrec's to state, because pcrec builds the consumer. Today's nearest
   relatives are `[PRIOR-COST-UNIFY]`'s operation-kind table and its CONTRACT/
   MEASURED planes. This is that table's consumer half, handed over as data, and it
   is why rev 2's pause for re-scope fits: the consumer price is the piece of
   `[PRIOR-COST-UNIFY]` that stays on pcrec's side.
3. **Optional, the one that decides near-ties: a joint survival rate per span**,
   from an exemplar bundle (D83 addendum's run-rate family). Without it the kit
   should treat survivor counts as unknown and rank by stops + `consumer(mb, ov)`
   with a conservative survival guess. That is P5 with the independence product
   replaced by a floor such as the span's rarest single position.

**Not needed**: the kit owning the look-forward. Every flip above is reproduced by
P5 with a three-number consumer price, and the look-forward is the engine itself.
**Not answered by this study**: whether one consumer price per ROUTE is fine-grained
enough. A VM attempt's cost varies 5x with frame discipline (`hyb_reseed.md` §3),
so the price may have to be per artifact, not per route kind.

## 6. The three standing questions (docs/design/CLAUDE.md)

1. **Measurement regime: RELEVANT.** Everything here is counts (stops,
   survivors, window bytes, starts) on the bench's 256 KiB throughput subjects
   (capability `t-256k`, syntax `t-256k`, loglines `t-256k-fail`/`-hit`), regenerated
   from pcrec-bench `d359564f` and sha-checked. No timing. The consumer coefficients
   (§3) and the kit form prices are ILLUSTRATIVE and UNMEASURED (D149). They are
   exposed as parameters so that a reader can see which flips survive other values.
   A throughput regime (find-all over the whole subject) is what the counts model. A
   latency regime (one search, early exit) would weight the first stop, and the
   ranking could differ. That was not studied.
2. **Independent control: RELEVANT.** The span extractor is held against pcrec's own
   k-set walk (§1.3, shares no code). The subjects are held against the bench's
   manifests by sha256. The simulated counts are checked by a hand witness
   (`game.simulate` on a 44-byte subject, recorded in the CLAUDE.md). The python
   `re` match counts are a sanity column only (python is a tripwire under D26, and
   `\h`, `\R`, `\K` are respelled for it).
3. **What moves on regeneration: NOT RELEVANT to emitted bytes.** Nothing here is
   read by the compiler. A regeneration moves only `data/`. A future producer of
   span facts would be an abi event, through any stamp it adds and through the
   kit's emitted text (D146/D147), but that belongs to the request, not to this study.

## 7. Questions for Frank, framed for discussion

- **The consumer price.** Should it be a declared fact pcrec hands with the spans
  (my leaning: yes, as data: three coefficients plus the no-search cost, per route),
  or should the kit receive a consumer KIND and own a price table per kind? The first
  keeps D157's facts-only line, and the second puts engine knowledge in the kit.
- **The unbounded move-back.** On 15-22 % of the unanchored patterns with a span, the best landmark is
  unreachable under D161. One reading is that it belongs to the look-back half,
  together with look-forward, outside "search for the window". Another is that a span
  could carry a move-back of the form "back over class C, at most until the previous
  stop", which the kit can implement as a reverse class scan. My leaning is the
  former, so the window category stays bounded and simple, with a revisit trigger
  when a request needs it.
- **Joint survival rates.** These are worth carrying only where two bounded spans
  have stops within 2x. On this population that is a handful of patterns (`data/
  summary.md` §D2). My leaning: the kit ranks by stops + priced window with a
  conservative survival floor, and joint rates wait for a measured loss.

## 8. [wingame2] P6 `refine`: scan the rare span, locate the tight one locally

Lane `wingame2`, 2026-10-11, same population, subjects and prices as §3-§5 (the
prices are still UNMEASURED, D149; counts only). Frank's policy, which the first
lane did not include:

> Span 1 is the best (smallest overshoot, tightest window) but has no rare target
> (a digit class), so it cannot be scanned cheaply. Span 2 has a rare target. Scan
> for span 2's target; on each hit, use the two spans' move-backs and overshoots
> (their relative distance and its uncertainty) to bound where span 1 must lie, and
> run a LOCAL search for span 1's class over that region. Span 1's hit fixes the
> window with its small overshoot. Where the gap is unbounded (`\d+.*#`), span 2's
> hit cannot bound span 1: just search forward for span 1's class.

### 8.1 What P6 is, and the one derivation it needs

Call span 1 `A` (the window span) and span 2 `B` (the scan span). P6 scans a form
over `B` (§3's forms: one anchor or a pair, whole span verified), and at each B
survivor tests every start of `A` in a bounded REGION; each A hit becomes a window
`[s_A - move_back_A, s_A + len_A)` with `overshoot_A + 1` possible starts.

The region needs the relative distance of the two spans, and **D161's inputs
already carry it.** With `omin = move_back - overshoot` and A before B,

    start(B) - start(A)  in  [omin_B - omin_A,  move_back_B - move_back_A]
    uncertainty = overshoot_B - overshoot_A          (order from omin and len)

Control: a direct walk of the items between the two spans (`spans.rel_from_items`)
agrees with this on **152 of 152** span pairs (`data/relcontrol.tsv`). The LOOSE
bound a reader gets by treating each span independently against the match start has
uncertainty `overshoot_A + overshoot_B`. It is sound but wasteful when A itself sits
behind a variable gap: witness `.{0,6}\d.{0,3}#` has a region of 3 starts exact and
15 loose, and the loose region costs P6 1.4x-2x more on that witness (§8.3).
Where the gap is unbounded (either span has `move_back = inf`) there is no region
and P6 is exactly P5: its candidates are P5's forms plus the local plans, so the
fallback "search forward for A's class" is P5's own form over A.

`game.pol_refine(consumer)` picks the cheapest of P5's forms and every local plan
over ordered pairs of bounded spans under the same independence estimate, with P5's
decline rule. Two more things were measured beside it, and are not in the policy:
`local-merge` (one window per B survivor: first hit to last hit) and a forced
`fwd` / `fwd-gate` / `fwd-tail` for Frank's setting (`game.refine_pair`: A = the
bounded span with the smallest overshoot, B = a rarer span).

### 8.2 Population: P6 rarely finds a plan, and only one is a real pattern

Of the 327 patterns P6 picks a plan on 9 (dfa) and 10 (vm); every other pattern
gets P5's pick or its decline (E1). The plan patterns are `wild-logparse-syslogbase-
expanded` and eight tiny test patterns (`(?>a|ab)c`, `a{1,2}+b`, `colou?r`,
`((a)|b){1,3}?c`, `[a-]{1,2}(?<!a)b` ...). On those cells P6 is better than P5 in 7
of 9 (dfa) and 8 of 10 (vm) and summed work falls 2.4x (dfa: 1.49 M -> 0.63 M) and
2.3x (vm: 13.2 M -> 5.8 M). Those sums are driven by the toy patterns, where A and B
are one frequent letter each and the local search turns a stop on a common byte into
a 2-position look. The one real bench pattern with a plan, syslogbase-expanded, gains 1.40x under the VM
consumer over P5 and SHIPPED (4.77 M against 6.66 M: scan the rare `\x20`, then look 8
starts back for the 16-byte prefix class), and P5-dfa declines it anyway. The loss
cell is `colou?r` (0.97x dfa, 0.71x vm: the prefix `colo` is already rare enough).
P6 does not change a single choice among the bench's loglines patterns.

### 8.3 Witnesses (the shapes Frank named; `data/refine.tsv`, §E3-E4 of `data/summary.md`)

Eleven two-span witnesses run on all four subjects (`run_game.WIT2`). Work as in §4.1
(one DFA step = 1), capability / log-fail subjects:

| witness | gap | consumer | P5 | P6 | P6 merged | reference |
|---|---|---|---|---|---|---|
| `\d{3}.{0,4}#` | region 4 | vm | 269 K / 180 K | **86 K / 108 K** | 86 K / 90 K | no-search 15.7 M |
| `\d{3}.{0,4}#` | region 4 | dfa | 36 K / 27 K | 34 K / 36 K | 34 K / 26 K | no-search 262 K |
| `\d{2,4}.{0,12}#` | region 14 | vm | 717 K / 475 K | **165 K / 211 K** | 138 K / 154 K | |
| `\d{2,4}.{0,12}#` | region 14 | dfa | 43 K / 31 K | 54 K / 61 K | 40 K / 35 K | |
| `.{0,6}\d.{0,3}#` | A has overshoot 6 | vm | 493 K / 328 K | 702 K / 895 K (worse) | 673 K / 838 K | |
| `\d{3}-.{0,4}#` | A has a semi-rare `-` | vm | 15 K / 79 K | 15 K / **13 K** | | |

Reading it:
- **P6 wins where A's own overshoot is ~0 and B's is large, and the consumer pays per
  START.** Under the VM consumer P5's B-window opens `overshoot_B + 1` = 5 to 15 starts
  per hit; P6 hands over 1 start per A hit. Gains: 3.1x (`\d{3}.{0,4}#`, cap), 4.3x
  (`\d{2,4}.{0,12}#`, cap), 5.2x merged, 6.2x on the semi-rare `-` witness (log).
- **Under the DFA consumer P6 is not better, and unmerged it is worse** (0.5x-0.76x on
  the log subjects): the DFA pays per window BYTE and P5's single B window is only
  8-17 bytes. P6 hands over 1.9 to 3.9 A windows per B stop (`E4`: digits cluster
  next to a `#`), each paying the per-candidate cost. Merging them into one window
  per B hit repairs it to P5's level (0.88x-1.07x) and no further. The honest summary
  is that a DFA consumer sees no gain from P6 on a digit-shaped A; the exceptions
  are cells where the A hit is rare (the semi-rare witness: 1.9x-2.4x).
- **P6 loses when A is itself far from the match start** (`.{0,6}\d.{0,3}#`): each A
  window carries 7 starts, there are 2-4 of them per B hit, and the region is only 3
  wide. The gain condition is `overshoot_A << overshoot_B`, a pure function of D161's
  fields, so the kit can test it without the subject.
- **The table cannot price the local hits.** A windows per B stop were measured at 0.9
  to 3.9; the independence model predicts 0.002 (`\d{3}`), 0.08 (`\d{2}`) and 0.3 (`\d`) (E4),
  so it is 7x to 900x low. Same failure as §5.3, now on the local-search term. It is why
  the policy's pick lost to P5 on 8 of 20 witness cells (dfa; 4 of 20 vm) and why merging,
  which makes the hit count immaterial, lands within 0.88x-1.07x of P5 on every dfa cell.

### 8.4 The unbounded fallback and the presence gate

Witnesses `\d+.*#`, `[0-9]+ x{2}`, `\d+\w*@`, `\d+.*timeout` and the population's 29
unbounded-gap refine cells. P6 = P5 there by construction. Findings:

- **The forward search for A's class does not always pay.** For the DFA consumer,
  the forward `\d` search costs 0.74 M-2.37 M against 0.26 M for stepping every byte
  (digits are 7-27 % of these subjects' bytes): `fwd < nosearch` in **0 of 16** witness cells (dfa)
  and 9 of 29 population cells. For the VM consumer it pays in 16 of 16 (0.74 M-7.9 M
  against 15.7 M) and in 19 of 29 population cells. So Frank's fallback is right for a backtracker, and for a DFA the
  right fallback is to decline unless A's class is rarer than a digit. P5-dfa already
  declines `\d+.*#`.
- **A presence gate for the rare span pays only when that span is ABSENT.** On the
  syntax subject (no `#`) the gate turns the whole pattern into one scan: 7.9 K
  against 0.74 M (dfa fwd) or 2.1 M (vm fwd) or 15.7 M (vm no-search). It pays by more
  than 2% in exactly the cells where the subject holds no byte of B's class: 4 of 16
  witness cells and 3 of 29 population cells; with B present it never lowers the work
  (`gate < fwd` with B present: 0). A CONTINUOUS gate (a memchr between A candidates,
  total <= n bytes) is a net loss in 13 of 29 population cells (dfa), because it adds
  a fixed 0.03 n (7.9 K) to forward searches that cost 15 K-60 K. The TAIL form (one
  reverse scan from the end for the last B, cost = the bytes after it, then the forward
  search ends there) never loses (`tail > fwd`: 0 of 158 consumer x subject cells) and keeps the
  whole saving. A gate in front of a forward search is therefore "is there a `#`
  anywhere" and nothing finer; unbounded `.*` gives it no per-hit use.
  pcrec's existing required-byte pre-check (`facts_listing` 4.1.2¶8b) is the same
  existence test, so what remains for the kit is whether a kit-built forward search
  needs its own copy of it.

### 8.5 Does this change §5.5's list of facts the contract needs?

- **No new fact is needed for the bounded region.** `(move_back, overshoot, len)` per
  span already give the relative distance AND its exact uncertainty
  (`overshoot_B - overshoot_A`), which is tighter than the independent bound
  (`overshoot_A + overshoot_B`) a reader would use. §5.5 item 1 (`omin` beside
  `omax`, i.e. overshoot) is now load-bearing for two reasons: the window cost and
  this region.
- **The scan span and the window span are different spans.** D161's text reads as
  "the kit scans a span and hands that span's window". P6 scans B but hands A's window.
  The contract must say the kit may do that: the list gives it everything, but the
  kit's reply is "window of A, found by scanning B", so the REPLY needs to name which
  span's `(move_back, overshoot)` the window has.
- **The consumer price is needed more, not less.** P6 beats P5 only under a
  per-start consumer, loses or ties under a per-byte one, and the merge/not-merge
  choice moves the DFA verdict by 1.5x-2x. It is the §5.5 item 2 coefficients
  (per candidate, per window byte, per start), unchanged.
- **The survivor rate matters more.** Local hits per B stop are the term the table
  misses by 450x. §5.5 item 3 (a joint rate per span) becomes a rate CONDITIONAL on a
  hit of another span: "digits near a `#`" is far denser than digits at large. A
  conservative floor (each B hit costs at least one A window, not the independence
  product) is the cheap defence; it was not simulated as a policy here.
- **Unbounded gaps need nothing new** (as before), and the presence gate is not a
  contract fact.

### 8.6 Limits

Eleven witnesses and nine plan patterns (eight of them toys) are thin evidence; the
claim is about the SHAPE (when does the region or the starts count win), not a
population rate. The DFA/VM prices are still illustrative. The gate is modelled as a
byte-class scan (`scan_price`) on the last occurrence of B's rarest position; B
before A uses a looser sound offset. `.`'s newline exclusion is not modelled: on the
log subjects an unbounded `.*` is in fact bounded by the line end, which a look-back
to the previous newline could use; that is outside this study.
