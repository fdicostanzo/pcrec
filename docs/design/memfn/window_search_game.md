# Gaming out "search for the window" (D161) before any request is written

Lane `wingame`, 2026-10-11, from main `aa2ddb1d` (abi 75). This is a design study.
Nothing under `src/`, `memfn/` or `tests/` changes. Every number here is a COUNT
over subject bytes, and nothing reads a clock. The instruments are in
`window_search_game/` (see its CLAUDE.md). The population tables live in
`window_search_game/data/summary.md`, written by `chain.sh` (§4.2 says which
numbers were taken before the box hold lifted and which come after).

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
  derived from them today.
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

### 4.1 Hand-picked cells (taken during the box hold: 8 single compiles)

These are the bench patterns where a span choice exists, simulated on the bench's
own 256 KiB throughput subjects (sha256-checked against the bench manifests).
The columns are stops, survivors, window bytes (`move_back + len` per survivor)
and possible starts (`overshoot + 1` per survivor). `work` applies §3's illustrative
consumer coefficients to the MEASURED counts.

| pattern (subject) | span | mb / ov | stops | survivors | window bytes | starts | work dfa | work vm |
|---|---|---|---|---|---|---|---|---|
| `wild-logparse-syslogbase-expanded` (capability) | `[16]` prefix | 0 / 0 | 58,874 | 58,874 | 58,874 | 58,874 | 2.40 M | **7.05 M** |
| | `\x20` inner | 9 / 7 | 30,634 | 30,634 | 306,336 | 245,072 | 1.24 M | 16.25 M |
| | no window search | | | | | | **0.26 M** | 15.7 M |
| `level-context` (loglines hit) | `[EFC][RAR][RTI][OAT]` prefix | 0 / 0 | 1,209 | 96 | 384 | 96 | 0.40 M | 0.41 M |
| | `timeout…` hull, inner | 205 / 201 | 23,385 | 48 | 10,128 | 9,696 | 1.11 M | 1.68 M |
| `ipv4` (loglines hit) | `\d\.` #0 | 2 / 2 | 5,863 | 4,050 | 16,200 | 12,150 | 0.37 M | 1.16 M |
| | `\d\.` #1 | 6 / 4 | 5,863 | 4,050 | 32,400 | 20,250 | 0.39 M | 1.65 M |
| | `\d\.` #2 | 10 / 6 | 5,863 | 4,050 | 48,597 | 28,350 | 0.40 M | 2.14 M |
| `http-5xx` (loglines hit) | `"[GPD..][EOUA..][TSA..]` prefix | 0 / 0 | 2,168 | 144 | 576 | 144 | 0.27 M | 0.28 M |
| | `\x20[^ "]` inner | 7 / 3 | 25,455 | 23,203 | 208,827 | 92,812 | 0.99 M | 6.81 M |
| `kv-quoted` (loglines hit) | `[a-z_]` prefix | 0 / 0 | 122,979 | 122,979 | 122,979 | 122,979 | 3.88 M | 13.6 M |
| | `="` inner | 32 / 31 | 2,279 | 96 | 3,264 | 3,072 | 0.27 M | 0.45 M |
| `qnt-quest` (syntax) | `colo` prefix | 0 / 0 | 8,221 | 565 | 2,260 | 565 | 0.29 M | 0.34 M |
| | `r` inner | 5 / 1 | 14,150 | 14,150 | 84,900 | 28,300 | 0.66 M | 2.55 M |

What the policies chose (`build/wg/mini/out/choices.tsv`, reproduced by the
chain into `data/choices.tsv`):
- **syslogbase**: P1-P4 pick the inner `\x20` (rarer by the table: 0.125 against
  0.276). P5-dfa DECLINES (neither span beats stepping every byte). P5-vm picks the
  prefix, which is also pcrec's shipped choice (`first-class-bounded`, a VM hybrid).
  Under the VM consumer, the consumer-blind pick costs 2.3x the shipped one.
- **kv-quoted**: every policy picks the inner `="`, and so does pcrec's shipped
  handoff (K = 32). The default table anchors on `=` (2,279 stops), while the
  subject's own rates anchor on `"` (346 stops in the fail subject, 2,168 in the hit
  subject). The handoff anchors on `"` as well, through its req pick.
- **ipv4**: the three `\d\.` spans have IDENTICAL stops and survivors, because a stop
  is the same `.` whichever octet the kit says it is. Only move-back and overshoot
  separate them. The tie-break on move-back is right, but only because it happens
  to coincide with the consumer cost.
- **http-5xx**: the inner span's verify is weak (91 % of stops survive), so its window
  cost dominates: 209 K window bytes against 576.

### 4.2 Population (after the hold)

`chain.sh` builds this worktree's `pcrec` and runs `run_game.py` over 327 patterns.
That is 177 bench (capability, loglines, syntax) plus 150 corpus, the corpus sample
simulated on capability's `t-256k`. Its output, `data/summary.md`, carries:
- §A, the census above recomputed with the k-set control;
- §B, how often each policy picks the same span as P1, the declines, and inner-span picks;
- §B2, P4 against P5-dfa against P5-vm span flips, with every flipping pattern listed;
- §C, the summed counts per set and subject for every policy and for SHIPPED;
- §D, span-vs-span argmin flips: prior against measured stops, scan-only against
  dfa-priced against vm-priced, and the measured-to-predicted survivor
  distribution;
- §D2, every pair of spans whose stops are within 2x but whose windows differ by
  >= 3x or by >= 4 in overshoot.

**Status: see `../../dev/lanes/wingame_report.md`** for whether the chain had run
when this lane ended. If it is OWED, the report names the log and the completion line.

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
30,634 stops against 58,874. The DFA price agrees (1.24 M against 2.40 M). The
VM price reverses it (16.25 M against 7.05 M). pcrec's shipped artifact is a VM
hybrid, and it chose the prefix. A kit that knew only overshoot could not have
told these two consumers apart: it would need to know that the consumer is a
backtracker and what an attempt costs relative to a scanned byte.

### 5.2 Similar stops, very different windows

- **`ipv4`**: three spans with identical stops and survivors (5,863 / 4,050) and
  windows of 16 K, 32 K and 49 K bytes. The table cannot separate them at all, while
  move-back and overshoot separate them completely.
- **`level-context`**: the inner `timeout|refused|…` hull SURVIVES LESS often than the
  prefix (48 against 96 on the hit subject). A survival-only ranking would prefer it,
  and its window is 211 bytes with 202 possible starts. Priced, it costs 2.8x (dfa)
  or 4.1x (vm) the prefix.
- **`qnt-quest`**: `colo` (8,221 stops) against `r` at 5/1 (14,150 stops). These are
  close on scan cost (0.279 M against 0.290 M). Priced, the gap is 2.3x (dfa), because
  every `r` survives and opens a 5-byte window.

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
3,257x), now on the term that decides span-vs-span. The population figure is
`data/summary.md` §D's survivor-ratio line.

### 5.4 Does the choice flip once the beginning-search cost is included?

Yes, on these cells, and in both directions:
- **scan-only to priced**: `level-context`'s and `http-5xx`'s inner spans lose
  outright once priced. They were already worse on stops, but the gap grows 3-25x.
  `qnt-quest`'s near-tie becomes 2.3x.
- **DFA-priced to VM-priced**: syslogbase, as above.
- **Decline**: whether to search at all also flips with the consumer. On
  syslogbase the DFA consumer is better off with no window search (0.26 M), while the
  VM consumer must search (15.7 M without one). D161 makes "when a span is worth
  using" the kit's call, but that call is a comparison against the consumer's
  no-search cost, which the kit is not given.

The population frequency of each flip is `data/summary.md` §B2/§D.

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
