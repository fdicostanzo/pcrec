# K23 — the exact-minimum decomposition explosion, and the bound that deletes it

[M4.6c], design-first, 2026-08-17. Written on `k18_memo_design.md`'s
precedent: candidate mechanisms built as throwaway prototypes and measured
head to head, refutations recorded inline, every number re-runnable from
`probes/`.

**No engine code was written.** `src/` is untouched; the prototypes patch
ALREADY-EMITTED C, which is the only way this lane could measure the real
lowering without becoming the build lane.

---

## 0. How to read this

### 0.1 Claim marking (house style, inherited from `eng_brep_design.md` §0.1)

- **STRUCTURAL** — follows from the code or the design as it stands; an
  argument, checkable by reading.
- **MEASURED** — a number produced by a committed probe in `probes/`, with
  the command that produces it named. R24 M-F4: a number that cannot be
  re-run is not a measurement.
- **BELIEVED** — reasoned but not established. Every one is called out.
- **RULED** — someone else's decision, cited, not re-argued here.

`LC_ALL=C` is set in every shell probe in `probes/`, and said so in each
one, against R24 M-F1's collation defect.

### 0.2 The recommendation, in brief

**MINIMUM-REMAINING-LENGTH (MRL) pruning.** At every point where the emitted
VM is about to commit to a subject position, it already knows a compile-time
lower bound on how many bytes any accepting continuation from that point must
still consume. Where fewer bytes remain than that bound, no continuation can
succeed, and the position is cut before a choice point is pushed for it.

On K23's exemplar this is not an improvement, it is a collapse:

| arm | steps | forward scan work | answer |
|---|---|---|---|
| shipped emission | 10,621,636 | 55,684,363 | `RX_ERR_STEPS` against the 10⁶ budget |
| + MRL pruning | **1** | 190 | `(0,100)`, group 1 `(90,100)` |
| + MRL folded into the scan bound | **1** | **109** | same |

MEASURED (`probes/steps.sh`, and the inline work instrumentation reproduced
in §6.3). The oracle (python `re`) says `(0,100)` / group 1 `(90,100)`; all
three arms that answer, answer that.

And the exemplar is not the worst case in the corpus's own shape family.
`((a{2,4}){5,10}){5,20}` — three levels, 50-byte subject, again exactly the
minimum — costs **11,906,349,370 steps** as shipped, roughly twelve thousand
times the default budget, and **6 steps** under pruning, with a
byte-identical capture vector `(0,50) (40,50) (48,50)`. §2.6.

Three things make it the recommendation rather than one option of three:

1. **It is exactly tight where the problem is.** The explosion peaks when the
   subject is exactly the minimum length the pattern can match, and decays as
   slack grows (§2.1). The bound BITES when slack is small and is vacuous
   when slack is large — the same variable, opposite ends. §4.4.
2. **It costs no state.** Under today's replication the clamp is a
   compile-time CONSTANT per program point: two integer comparisons, no
   table, no allocation, nothing added to `rx_work`. The competing mechanism
   (memoization) needs Θ(program points × subject length) of memory, which is
   the one thing generated matchers may not have. §5.
3. **It cannot change an answer.** It removes only positions from which no
   accepting continuation exists, so the FIRST accepting path in preference
   order is untouched and PCRE2 leftmost-greedy captures are exact. Argued
   STRUCTURALLY in §4.2 and attacked with an 855-cell three-way differential
   in §7, which found 0 disagreements — after it found 44 in the prototype,
   §11.1.

### 0.3 Five things this note refutes, three of them the K23 entry's own

1. **"python `re` answers instantly"** (`known_issues.md` K23) is true of the
   exemplar and false of its mechanism. Python explores the SAME tree at a
   comparable per-node cost — 272 ms on the exemplar against pcrec's 222 ms
   with the budget lifted — and one size up it takes **32 s**, two sizes up
   **384 s**. §3.
2. **"The boundary is NARROW"** is right about the number and wrong about the
   variable. It is not narrow in `n`; it is narrow in SLACK (`n − p·m`), and
   the decay from the peak is geometric over ~50 bytes, not a cliff. §2.1.
3. **The step count is not merely characterizable, it has an exact CLOSED
   FORM** — the number of compositions of every subject prefix into parts
   drawn from the inner range, minus the accepting path. Nine measured
   instances, nine exact. §2.2, `probes/model.py --check`.
4. **A slice of the class the entry describes is already fixed** and the
   entry does not say so: an exact-count inner (`(a{6,6}){3,17}`) is
   possessified today, the OUTER takes the fixed-stride cursor rung, and the
   shape costs 0 steps. K23's live population is inner width ≥ 1 only. §2.4.
5. **This lane's own prototype was wrong about 44 cells before the
   differential caught it**, and the reason is item 4 — it patched a shape
   whose emitted form is not what it assumed. §11.1.

### 0.4 What this note is not

It is not a codegen spec, and it does not decide where in `src/` the analysis
lives. It answers "which mechanism, and what does it cost", with the
measurements a build lane would otherwise have to re-derive.

---

## 1. The ground: what the emitter actually does with the exemplar

STRUCTURAL, from `build/pcrec --emit-ir -- '(a{10,20}){10,50}'` and the
emitted C (both reproducible; the IR dump is produced by the emitter's own
walk, DD-8, so it cannot drift from the code it describes).

- Engine **vm**, forced by the capture group at offset 0.
- Prefilter **yes** — the capture-erased forward+reverse DFA pair hands the
  VM an exact window, and the VM never scans for the start (§6.1/§4.7).
- The OUTER `{10,50}` is on the **frames-bounded** rung and is
  **REPLICATED**: 50 body copies, "max replicas 50 (limit 64)".
- Each of the 50 replicas puts its inner `a{10,20}` on the **cursor** rung,
  stride 1, greedy — one span-loop low-water slot per replica, `stv[4]`
  through `stv[53]`.
- 332 labels, 90 resume points, `RX_BT_FRAMES 91`, `RX_TRAIL_FRAMES 151`.

Replica *k* emits, in the shape `engine_m4.md` §2.5 and D44/D44.1 describe:

```c
rx_L…:  RX_SET(2, (ptrdiff_t)pos);          /* group 1 open */
rx_L…:  RX_SET(4+k, (ptrdiff_t)pos);        /* the cursor's low-water mark */
        { unsigned long it_ = 0; rx_cur = pos;
          while (rx_cur + 1 <= n && it_ < 20UL && (s[rx_cur] == 97))
              { rx_cur += 1; it_++; } }     /* greedy to the furthest end */
rx_L…:  if ((ptrdiff_t)rx_cur < stv[4+k] + 10) goto rx_fail;   /* below min */
        RX_PUSH(&&rx_L…, rx_cur);           /* the retreat is the resume */
        pos = rx_cur; goto rx_L…;           /* group 1 close, next replica */
rx_L…:  rx_cur = pos;                       /* the retreat */
        if ((ptrdiff_t)rx_cur < stv[4+k] + 10 + 1) goto rx_fail;
        rx_cur -= 1; goto rx_L…;
```

So each replica offers 11 inner lengths (20 down to 10), and the outer's
exit alternative first appears after replica 9 — the tenth — because the
outer minimum is 10. Nothing here is a defect. Every rung was correctly
selected; the explosion is the product of correct local choices.

---

## 2. The defect, measured rather than described

### 2.1 The curve, and what the boundary is actually narrow IN

MEASURED, `probes/steps.sh '(a{10,20}){10,50}' 95,99,100,…`:

| n | 95 | 99 | 100 | 101 | 105 | 110 | 120 | 130 | 140 | 150 | 160 | 200 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| steps | 0 | 0 | **10,621,636** | 10,260,900 | 8,018,776 | 1,957,091 | 360,728 | 66,512 | 12,228 | 2,241 | 416 | 1 |

Two readings the K23 entry does not have:

- **Below the minimum the VM never runs at all.** n = 95 and 99 cost ZERO
  steps, not "a fast nomatch": the capture-erased DFA prefilter answers, and
  `engine_m4.md` §4.7's ordering rule keeps the VM out of it. So the
  whole-pattern minimum-length test already exists in pcrec — as a global
  prefilter. MRL pruning is that same reasoning applied at every interior
  program point instead of only at the boundary. That framing is the design's
  strongest argument and it is not a new idea in this codebase, it is an
  existing idea moved inward.
- **The peak is at slack 0 and the decay is geometric in slack, not sharp.**
  The count is still 8.0 M at 5 bytes of slack and still over the 10⁶ budget
  at ~15 bytes of slack. "The boundary is NARROW: 99 → nomatch, 150+ →
  instant" is a correct description of two endpoints and a misleading one of
  the interval, which spans about 50 bytes.

### 2.2 The step count in CLOSED FORM — MEASURED, 9 of 9 exact

For `(C{m,M}){p,P}` with a single-byte body `C`, greedy throughout, `P ≥ p`,
against a subject of exactly the minimum length `n = p·m`:

> **steps = ( Σ_{s=0..n} Comp\[m,M\](s) ) − p**

where `Comp[m,M](s)` is the number of compositions of `s` into parts drawn
from `[m, M]` — that is, the number of distinct decomposition PREFIXES the
search can be sitting on. The subtracted `p` is the accepting path itself,
whose nodes are reached by forward progress and therefore never charged
(`engine_m4.md` §4.2: a step is one backtrack resumption).

`probes/model.py --check` validates it against nine independently measured
instances and prints the difference column:

| m | M | p | n | measured | law | diff |
|---|---|---|---|---|---|---|
| 10 | 20 | 10 | 100 | 10,621,636 | 10,621,636 | 0 |
| 10 | 15 | 10 | 100 | 1,329,312 | 1,329,312 | 0 |
| 10 | 12 | 10 | 100 | 24,150 | 24,150 | 0 |
| 11 | 22 | 11 | 121 | 111,354,519 | 111,354,519 | 0 |
| 7 | 12 | 7 | 49 | 8,626 | 8,626 | 0 |
| 8 | 14 | 8 | 64 | 70,731 | 70,731 | 0 |
| 5 | 10 | 5 | 25 | 346 | 346 | 0 |
| 3 | 6 | 3 | 9 | 13 | 13 | 0 |
| 2 | 3 | 2 | 4 | 2 | 2 | 0 |

Nine of nine exact. The check is written so that a nonzero diff is a
REFUTATION and not a residual — the `−p` term is already applied, so there is
nothing left to absorb an error.

**Why the exact minimum is the WORST case, not merely a bad one** —
STRUCTURAL. At `n = p·m` the only decomposition is all-minimum, and the
minimum is the LEAST preferred inner length at every level (the inner is
greedy). So the unique solution is the very LAST leaf in preference order,
and the whole tree is explored before it is reached. One byte of slack and
the solution moves inward; the measured decay in §2.1 is that movement.

**Why the outer maximum drops out of the law** — STRUCTURAL, and it derives
D27's black-box observation rather than restating it. At `n = p·m` no
composition can have more than `floor(n/m) = p` parts, so the `P` constraint
is never active. D27 measured that `{10,30}` and `{10,50}` behave
identically; §7's differential reproduces that (both 10,621,636), and the law
says why.

### 2.3 Where the default budget is crossed — a predictive table

`probes/model.py --grid` evaluates the law over the family
`(a{m,m+w}){m,P}` at its own exact-minimum length `n = m·m`, and reports the
first `m` at which the 10⁶ default budget is exceeded:

| inner width w | first m | n = m·m | steps |
|---|---|---|---|
| 0 | never (m ≤ 39) | — | — |
| 1 | 20 | 400 | 1,048,556 |
| 2 | 14 | 196 | 1,902,423 |
| 3 | 12 | 144 | 1,990,783 |
| 4 | 11 | 121 | 2,427,977 |
| 5 | 10 | 100 | 1,329,312 |
| 8 | 10 | 100 | 6,254,283 |
| 12 | 9 | 81 | 1,693,525 |

This is D27's "inner-range WIDTH and total interact" as a function. The
practical reading: at inner width ≥ 5 the budget is crossed by
**81-to-100-byte subjects** — non-adversarial sizes — while at width 1 it
takes 400 bytes and at width 0 it never happens at all.

### 2.4 Width 0 is already fixed, and the entry does not say so

MEASURED, and it narrows the live class. `(a{6,6}){3,17}` and
`(a{2,2}){3,42}` do NOT take the shape §1 describes:

```
; possessify   1 of 2 source quantifiers possessified
; max replicas 0
RUNGS
  at L0      cursor    span-loop cursor {3,17}, stride 6, greedy
```

The exact-count inner is possessified by `src/opt/possessify.c` under
`eng_brep_design.md` §2.2's repaired rule, which makes the outer body a
DETERMINISTIC FIXED-LENGTH item, which puts the OUTER on the fixed-stride
cursor rung with stride 6 and zero replicas. There is no decomposition space
left to explore, and the measured step count is 0 at every subject length.

So K23's live population is **inner width ≥ 1**, and the [ENG-BREP] ladder
already disposes of the width-0 edge. That is worth recording in the entry:
it is the difference between "nested bounded quantifiers explode" and the
true statement, which is narrower.

### 2.5 The class extends past the cursor rung — MEASURED

A choice-bearing inner body cannot take the cursor rung; it lands on frames.
The explosion is the same class there, multiplied by a bounded factor:

| shape | n | steps | single-class twin | twin steps | ratio |
|---|---|---|---|---|---|
| `((a\|b){7,12}){7,20}` | 49 | 51,993 | `(a{7,12}){7,20}` | 8,626 | 6.03 |
| `((a\|b){8,14}){8,20}` | 64 | 454,858 | `(a{8,14}){8,20}` | 70,731 | 6.43 |

The alternation contributes its own choice points as a roughly constant
multiplier; it does not change the class or the law's shape. BELIEVED that
the multiplier stays bounded in general — two points is two points.

**A separate finding from that family, reported because a timeout is a
finding.** `((a|b){10,20}){10,50}` emits in 0.105 s but produces a
20,941-line, 670 KB function, and **gcc cannot compile it**: `-O0` 4.0 s,
`-O1` 6.6 s, `-O2` still running past 120 s and past this lane's 300 s bound.
That is a downstream-compiler cost of replication × choice-bearing bodies,
adjacent to `eng_brep_design.md` §1.4's finding about pcrec's OWN cost but
about gcc rather than pcrec, and it belongs to [ENG-CLAMP]/counter-K
territory rather than to K23. Recorded so the next lane does not rediscover
it as a hang.

### 2.6 THREE levels: the same defect, four orders of magnitude worse

MEASURED. `((a{2,4}){5,10}){5,20}` at its own exact minimum
`n = 5 × 5 × 2 = 50`:

| arm | steps @ n=50 | span | group 1 | group 2 |
|---|---|---|---|---|
| shipped | **11,906,349,370** | (0,50) | (40,50) | (48,50) |
| MRL pruning | **6** | (0,50) | (40,50) | (48,50) |

Twelve thousand times the default budget, on a fifty-byte subject of `a`s.
The pruned arm's capture vector is byte-identical to the baseline's at
n = 50, 51, 55 and 60, and its step count is 6 at every one of them.

Three things follow.

- **The exemplar in the K23 entry is not the family's worst member**, and the
  entry's "100-byte ordinary input" framing understates the reach. Nesting
  multiplies: each level's decomposition space is explored inside every leaf
  of the level above it.
- **Python cannot serve as the oracle here.** `re.search` on this shape at
  n = 50 did not return inside 100 s; the correctness check above is
  therefore pcrec-vs-pcrec — baseline replication as the ground truth,
  which is exactly the primary instrument `eng_brep_design.md` §5.1
  established for this territory, with python demoted to the shapes it can
  still answer. Stated rather than hidden: for the three-level rows the
  independent oracle is missing, and §10 keeps it on the not-measured list.
- **The prototype needed a per-site `minrest` that is not one formula.** At
  three levels the constant at scan site `k` is
  `max(0, 5−(j+1))·2 + max(0, 5−(i+1))·10` with `i = k / 10`, `j = k % 10` —
  still pure compile-time arithmetic, but no longer indexable by a single
  rule, which is precisely why the real mechanism threads an ACCUMULATOR down
  the emitter's walk (§4.3) instead of indexing replicas. The prototype gets
  `--minrest-py` for this; the emitter does not need it.

---

## 3. Why python is fast, answered — and it is not fast

The brief asked for one cheap measurement of why python `re` answers
instantly, on the theory that its mechanism might be a hint. It is a hint,
but not the one expected.

MEASURED (`python3 -c` timing, reproduced in `out/python_growth.txt`):

| shape | n | python `re` |
|---|---|---|
| `(a{10,12}){10,50}` | 100 | 1.11 ms |
| `(a{10,15}){10,40}` | 100 | 48.5 ms |
| `(a{10,20}){10,50}` | 100 | **272 ms** |
| `(a{11,22}){11,50}` | 121 | **2.90 s** |
| `(a{12,24}){12,50}` | 144 | **32.4 s** |
| `(a{13,26}){13,50}` | 169 | **384 s** |

Python has **no pruning rule**. It explores the same tree, and the growth is
the law of §2.2. Its per-node cost is comparable to pcrec's: pcrec with the
budget lifted answers the exemplar in **0.222 s** against python's 0.272 s,
on 10.6 M resumptions — pcrec is marginally the faster of the two, on the
same work.

Three consequences, and they matter to how K23 is framed:

- **pcrec is not slower than python here.** The entire observed difference is
  that pcrec has a budget and stops at 10⁶, and python does not and grinds.
  The K23 entry's "python answers instantly, pcrec returns RX_ERR_STEPS"
  reads as an algorithmic gap; it is a policy difference at one instance size.
- **By D22's own standard pcrec's current behaviour is the BETTER of the
  two.** A 384-second answer on a 169-byte subject is the hang D22/DD-2 exist
  to prevent. Python is the one failing that bar.
- **That is not a reason to leave K23 open.** The oracle proves a match
  exists; pcrec does not deliver it on a 100-byte non-adversarial input; the
  fix costs two comparisons. The defect is real. What changes is the
  JUSTIFICATION: K23 is not "catch up to python", it is "answer a question we
  can answer cheaply".

**No python defect found.** Nothing here belongs in
`docs/dev/upstream_issues.md`: python's behaviour is exponential but correct,
and `re` makes no complexity promise. Reported to the manager as a
no-finding, per the brief.

---

## 4. MRL pruning, designed

### 4.1 The bound

For each program point `q`, define

> `minrest(q)` = the minimum number of subject bytes that any ACCEPTING
> continuation from `q` must still consume.

A position `pos` at `q` with `n − pos < minrest(q)` is DOOMED: no
continuation from it can accept. The emitted check is

```c
if ((size_t)(n - pos) < MINREST_q) goto rx_fail;   /* frames rung */
```

and, at a cursor rung — where the engine is choosing among a RANGE of
positions rather than one — the same test is expressed as a clamp on the
range's upper end, which cuts the whole doomed suffix in one operation:

```c
if (n < MINREST_q) goto rx_fail;
if (rx_cur > n - MINREST_q) rx_cur = n - MINREST_q;
```

That second form is the one that matters for K23, and it is why the exemplar
collapses to a single step rather than merely to a smaller number: the
clamp deletes ten of the eleven inner choices at every replica at once.

### 4.2 Soundness — STRUCTURAL

The claim: pruning changes no answer, including no capture.

1. `minrest(q)` is a LOWER bound on the bytes consumed by any accepting
   continuation. So `n − pos < minrest(q)` implies that no accepting
   continuation exists from `(q, pos)`.
2. Every position the clamp removes is therefore a position whose subtree
   contains no accepting leaf.
3. Preference order among the SURVIVING positions is untouched — the clamp
   removes leaves, it never reorders alternatives, never converts greedy to
   lazy, never changes which branch is the fallthrough.
4. PCRE2 leftmost-first is "FIRST COMPLETE MATCH WINS" (`engine_m4.md` §3.1),
   so the answer is determined by the first accepting leaf in preference
   order. Removing non-accepting leaves cannot move it.
5. Therefore span and every capture slot are unchanged.

The single failure mode is an UNSOUND analysis — a `minrest` that
OVER-estimates. Under-estimating is always safe (it prunes less), which is
the direction every conservative case below takes, and which is what the
prototype's `--follow-min 0` default does (§7.3).

### 4.3 Computing `minrest` — a small AST walk, and a threading rule

The minimum-width function over the AST (`src/core/internal.h`'s seven node
kinds):

| node | `minw` |
|---|---|
| `A_CLASS` | 1 (the encoding's minimum unit; 1 byte for both ascii and utf8, since a class may hold ASCII) |
| `A_EMPTY`, `A_BOL`, `A_EOL` | 0 |
| `A_CAT(l,r)` | `minw(l) + minw(r)` |
| `A_ALT(l,r)` | `min(minw(l), minw(r))` |
| `A_REP(l,rmin,·)` | `rmin · minw(l)` |
| `A_CAP(l)` | `minw(l)` |

`minrest` at a point is then the `minw` of everything after it, which the
emitter can thread DOWN its existing walk as an accumulator rather than
computing per point:

- emitting `A_CAT(l, r)` with follow-min `F`: emit `l` with `minw(r) + F`,
  then `r` with `F`;
- emitting `A_REP(l, rmin, rmax)` as replicas with follow-min `F`: replica
  `k` (0-based) gets `max(0, rmin − (k+1)) · minw(l) + F`.

That second line is the whole of K23's fix, and under replication it is a
COMPILE-TIME CONSTANT — no counter is read, nothing is added to `stv`, and
`rx_work` does not grow.

Two implementation notes that are design decisions, not details:

- **`minw` must not recurse on pattern structure.** D10/DD-10 exist because
  `compile_ast` and `clo_visit` did, and R1's fix flattens `A_CAT`/`A_ALT`
  spines iteratively (`src/ir/nfa.c`). `minw` must follow the same discipline
  — it is the same walk over the same trees, and it would inherit the same
  bug at the parser's 250-paren cap.
- **The threading seam already exists.** `src/opt/possessify.c`'s `pss_walk`
  threads a FOLLOW first-set down the same tree for the same reason.
  `minrest` is the arithmetic sibling of that analysis and should ride the
  same walk shape rather than inventing a second one.

Conservative cases, all in the safe (under-estimating) direction: a
lookaround or assertion contributes 0; a backreference contributes 0 (the
referenced group may be empty); an unbounded `A_REP` contributes
`rmin · minw(l)` like any other.

**Prior art, D26-adjacent and not a compatibility obligation.** PCRE2's
`pcre2_study.c` computes exactly this minimum length — but uses it only as a
WHOLE-PATTERN prefilter ("subject shorter than the minimum ⇒ no match"),
which is the same use pcrec's DFA prefilter already makes of the same fact
(§2.1). Applying it at interior program points is the step neither takes.

### 4.4 Why the mechanism is tight exactly where the problem is

STRUCTURAL, and this is the argument that makes MRL the recommendation
rather than a heuristic.

Both the explosion and the bound's tightness are functions of the SAME
quantity, slack `= n − p·m`:

- At slack 0 the bound is exactly binding at every replica: replica `k` may
  end only at `pos = (k+1)·m`, so the surviving choice set is a SINGLE
  position and the tree collapses to one path. Measured: 1 step.
- As slack grows the bound loosens and prunes less — and the explosion
  shrinks at the same rate, because slack is precisely what lets greedy
  succeed early.

So the mechanism does not need to be tuned to the shape: it is strongest at
the shape's worst point and irrelevant at the point where it would cost
without paying. §2.1's curve and §7's `prune_steps` column are the two halves
of that claim, measured.

### 4.5 Interaction with counter-K, possessify and the rung ladder

- **Counter-K** (sibling lane, `counterk_design.md` §3). When the outer stops
  being replicated, the per-replica constant becomes a runtime expression
  `max(0, rmin − stv[ctr]) · minw(body) + F` — one load, one subtract, one
  multiply, one compare. Its natural home is the trip guard
  (`L_mtrip`/`L_trip`), which already reads `stv[ctr]`. Checking once per
  TRIP rather than per iteration prunes slightly less and stays sound (a
  check omitted is pruning forgone, never an answer changed). BELIEVED that
  once-per-trip is enough for K23's class; NOT MEASURED, because counter-K is
  being built as this is written.
- **Possessify** already deletes the width-0 slice entirely (§2.4). MRL and
  possessification are complementary and do not overlap: possessification
  removes retreats that provably cannot succeed for a LANGUAGE reason;
  MRL removes positions that cannot succeed for a LENGTH reason.
- **The cursor ladder.** MRL is expressible on every rung. On disjoint-follow
  there is nothing to prune (no machinery is emitted). On fixed-stride and
  reverse-deterministic it is the clamp form of §4.1. On frames it is the
  test form. Nothing in the ladder has to move.

### 4.6 The refinement that also cuts FORWARD work (D49)

D49 landed a SECOND bound yesterday — `RX_ERR_WORK`, metering the forward
work the step counter is blind to, with a bring-up default near 10⁹. MRL has
a variant aimed straight at it: fold the clamp into the greedy scan's own
bound instead of applying it after the scan runs.

```c
const size_t cap_ = (n < MINREST_q) ? 0 : n - MINREST_q;
while (rx_cur <= cap_ && rx_cur + 1 <= n && it_ < 20UL && s[rx_cur] == 97)
    { rx_cur += 1; it_++; }
```

MEASURED on the exemplar at n = 100 (scan-loop iterations, instrumented at
the loop body; `probes/prune_proto.py --clamp-scan`):

| arm | steps | scan work |
|---|---|---|
| shipped | 10,621,636 | 55,684,363 |
| MRL, clamp after the scan | 1 | 190 |
| MRL, clamp folded into the scan bound | 1 | **109** |

109 on a 100-byte subject is one forward pass plus the nine clamp
evaluations. The work bound's metric drops by five and a half orders of
magnitude, and the shipped arm's 5.24 work-per-step ratio on this shape is
itself a data point for [M4.6]'s calibration of D49's default.

### 4.7 The symmetric half, designed and NOT recommended for v1

`maxrest(q)` — the maximum bytes an accepting continuation can consume — is
the mirror bound, and it prunes when the pattern must reach a fixed endpoint
(`…$`, or a caller demanding the whole subject). It is the same walk with
`max` and `rmax` substituted, and `rmax == -1` makes it infinite and the
check vacuous, which is most patterns.

It is NOT recommended for v1: K23 does not need it, no measured shape in this
lane needs it, and it adds a second constant per program point for a
population nobody has counted. Recorded so the build lane knows it was
considered, and named as an [ENG-*] candidate if evidence appears — the
[ENG-ABS]/[ENG-ISL] pattern (D50).

---

## 5. The candidates, head to head

All three prototypes patch the same emitted matcher; `probes/head2head.sh`
builds and runs all three arms and prints the table.

### 5.1 MEASURED — `(a{10,20}){10,50}`

| arm | .c bytes | gcc −O2 | steps @ n=100 | @101 | @110 | @150 | memo table |
|---|---|---|---|---|---|---|---|
| baseline | 80,356 | 0.77 s | 10,621,636 | 10,260,900 | 1,957,091 | 2,241 | — |
| MRL prune | 81,661 (+1.6%) | 0.74 s | **1** | 1 | 1 | 1 | — |
| memoization | 86,544 (+7.7%) | 0.94 s | 2,071 | 2,026 | 1,621 | 371 | 25,650 B |

### 5.2 MEASURED — `(a{11,22}){11,50}`, one size up

| arm | steps @ n=121 | @122 | @130 | @200 |
|---|---|---|---|---|
| baseline | 111,354,519 | 108,024,204 | 49,674,598 | 488 |
| MRL prune | **1** | 1 | 1 | 1 |
| memoization | 3,081 | 3,031 | 2,595 | 206 |

### 5.3 Candidate 1 — MEMOIZATION, and why it loses

The mechanism (`probes/memo_proto.py`): mark `(program point, position)` on
arrival; a second arrival fails immediately.

**It is sound, and the reason is worth stating** — STRUCTURAL. The VM is a
pure depth-first backtracker, so a second arrival at the same
`(point, position)` can only happen after the first arrival's entire subtree
was explored and failed; had it succeeded the matcher would have returned.
"Visited" therefore implies "failed" and no success/failure bookkeeping is
needed. Two conditions, both real:

- the future must be a function of `(point, position)` alone. It is here,
  because captures are write-only with respect to control flow. A
  **backreference breaks it** — the future would then depend on a captured
  substring — so a memo would have to be disabled for module `backrefs`,
  which is precisely one of the constructs `select_engine`'s socket is
  designed to admit later (`engine_m4.md` §5.2).
- the memo must survive across the search's start-position attempts, and
  soundly does, for the same reason.

**It works — 5,100× on the exemplar — and it still loses on all three axes
that matter here:**

1. **Memory it cannot have.** The table is Θ(memo points × subject length)
   bits. Measured: 50 replicas × a 4,096-byte subject cap = 25,650 bytes.
   The law is `q·n/8` bytes. Against D19's recorded 128 KB thread stack, an
   allocation-free stack-resident memo caps the subject at
   `128 KB × 8 / 50 ≈ 20,971 bytes` for THIS pattern — three orders of
   magnitude below where the step budget would notice, and the same shape of
   ceiling D44.1/D44.5 already had to stamp for frames. A heap memo is not
   available: generated matchers are allocation-free by mandate
   (`COPY_MATCHED_SUBJECT=NEVER`'s precedent, `engine_m4.md` §2.2).
   K18's memo precedent does not transfer — that one was COMPILE-time, where
   allocation is ordinary.
2. **It does not actually fix the exemplar.** 2,071 steps is under the budget
   today, but it is 2,071 against pruning's 1, and it is a per-subject-byte
   quantity: the memo turns exponential into polynomial, while pruning turns
   it into linear-in-`p`. On a subject at the memo's own ceiling the counts
   would be three orders of magnitude larger again.
3. **It costs on the common path in a way pruning does not.** Every loop
   entry does a table read, a table write, and a bounds test against the cap,
   on the FORWARD path, for every pattern that carries a memo — where MRL's
   clamp is two comparisons against a constant. §6.

**Not refuted, re-homed.** Memoization is the right mechanism for a defect
MRL cannot reach — an explosion driven by CONTENT ambiguity at constant
length rather than by length ambiguity. No such defect is open today. If one
appears, this section is the pricing.

### 5.4 Candidate 2 — ENGINE-SELECTION ROUTING, and the honest version of "elsewhere"

MEASURED: `--no-captures` on the exemplar routes to the DFA (`engine 1,
ENGM_DFA`) and answers in 0.12–0.14 s of process time at **every** subject
length tried, including n = 100,000. The DFA has no difficulty with this
pattern at all.

That is the whole of the good news, and it does not help:

- The exemplar HAS a capture, and captures are on by default (D42.1). A
  DFA-compiled artifact emits `RX_NCAPS 1` and `--engine=dfa` REFUSES a
  captures-default pattern (D44.6, `engine_m4.md` §5.7). Routing this pattern
  to the DFA means not answering the question that was asked.
- A refuse-fast — recognize the shape at compile time and decline — is
  D22-honest and is strictly WORSE than what ships today, which at least
  tries and diagnoses at run time. It also fails the oracle: a match exists.
- **DFA islands would not have helped either**, and are in any case deferred
  (D50, [ENG-ISL]). An island runs a capture-free FRAGMENT as a DFA; here the
  ambiguity is *between* iterations of a capture-bearing group, which is the
  part an island cannot own.

Routing is therefore not a candidate for K23. It is recorded because the
brief named it and because the `--no-captures` measurement is the honest
statement of what the alternative engine can and cannot buy.

### 5.5 Candidate 3, unnamed in the entry — RAISE THE BUDGET

Rejected, and it is worth one paragraph because it is the cheapest thing
anyone could do. 10⁶ → 10⁸ would answer the exemplar. It would not answer
`(a{11,22}){11,50}` (111 M), it would not answer `(a{12,24}){12,50}`, and the
law in §2.2 says the family climbs about 11× per unit of `m`. Raising the
number moves the boundary by one shape and costs every genuinely pathological
pattern two orders of magnitude more grinding before it refuses — which is
the D22 trade in the wrong direction. The budget is a robustness backstop,
not a fix.

---

## 6. What it costs on the common path (D18)

D18's speed mandate and D22's "must not be traded against execution speed"
apply to the clamp, which sits on the FORWARD path.

### 6.1 MEASURED, with a placebo control

The measurement has a control, because the difference between "the clamp
costs" and "inserting any code at all moves the layout" is not visible
otherwise. `--placebo` emits the clamp at the same sites with the same
instruction shape and `minrest` forced to 0, so it can never fire.
`probes/throughput.sh`, best of 9 runs per arm, benign matching subject (so
the clamp is pure added work with nothing to save):

| shape | n | base | placebo | prune | prune vs base |
|---|---|---|---|---|---|
| `(a{10,20}){10,50}` | 300 | 1969.4 ns | 1989.5 ns | 2027.8 ns | **+3.0%** |
| `(a{2,4}){10,50}` | 200 | 1588.1 ns | 1586.1 ns | 1572.6 ns | −1.0% |
| `(a{1,2}){10,50}` | 60 | 597.1 ns | 600.0 ns | 600.3 ns | +0.5% |

Read honestly: the effect is inside a ±3% band whose sign varies by shape. On
the one shape where a penalty appeared, **+1.0 point of the +3.0 is code
LAYOUT** (base → placebo), not the clamp's own instructions; the clamp itself
accounts for +1.9 points there and for a small negative or nothing on the
other two.

Run-to-run variation is of the same order as the effect: an earlier
nine-repetition run of the identical harness gave +3.7% / +1.7 layout on the
first shape and −1.6% / −0.8% on the others. The archived numbers are the
ones in `out/throughput.txt`; both runs support the same reading and neither
supports a tighter one.

MEASURED, not extrapolated: this is three shapes on one box, on a harness
built for this question rather than `make bench`. What it supports is "the
clamp is not a throughput event"; it does not support a claim that the clamp
is free, and §10 lists the benchmark this lane did not run.

### 6.2 Compile-time and code size

From §5.1: +1.6% of emitted C, and gcc −O2 got marginally FASTER
(0.79 s → 0.74 s), which is noise at this scale. The clamp adds three lines
per site and no new symbols, macros or struct members.

### 6.3 Forward work

§4.6's table. The clamp REDUCES forward work by five and a half orders of
magnitude on the exploding shape and adds a bounded constant elsewhere.

---

## 7. Validation

### 7.1 The instrument

`probes/diff3.py` is a THREE-WAY differential: baseline pcrec, MRL-pruned
pcrec, python `re`. It compares the FULL capture vector, not the span — the
soundness claim is about where the groups land, and a span-only instrument
would have missed exactly the class of error §4.2 exists to exclude
(`eng_brep_design.md` §6's disclosed instrument gap, avoided here by having
read it).

Both pcrec arms are emitted with an effectively infinite step budget, so a
budget refusal can never masquerade as a difference in what the engine
explores. The budget is applied afterwards, on paper.

### 7.2 The populations, and the result

| corpus | shapes | measured | cells | AGREE | DIFFER |
|---|---|---|---|---|---|
| `cases_prune.tsv` (chosen around known boundaries) | 16 | 13 | 93 | 93 | **0** |
| `cases_random.tsv` (seeded, `gen_cases.py --seed 23`) | 120 | 78 | 762 | 762 | **0** |

**855 cells, 0 disagreements, on the full capture vector.**

Both corpora exist because either alone misleads. The hand-chosen one
contains the defect — 28 of its 93 cells exceed the 10⁶ default budget in the
baseline arm, up to 111,354,519 steps, and every one of those 28 costs
between 1 and 4,996 steps under pruning. The randomized one contains almost
none of it (its parameter box is capped at `p·m ≤ 60` so that python can
serve as oracle at all, and its worst cell is 416,662 steps) but it samples
the shape space the hand-chosen one cannot, which is where a soundness bug
would hide. Aggregate over the random corpus: 2,179,620 baseline steps →
528 pruned.

The random corpus is what caught this lane's own defect (§11.1); the chosen
corpus never would have.

### 7.3 The axes deliberately included

- **Unanchored search that must skip bytes.** The clamp is stated against the
  SUBJECT END, so a match that starts late is the case that catches an
  off-by-a-prefix. `bbbbb` + `a`×n rows: correct, 1 step.
- **A non-empty follow.** `(a{10,20}){10,50}b` rows. The prototype passes
  `--follow-min 0`, i.e. it deliberately UNDER-estimates `minrest` here; the
  rows show the safe direction is the one it takes (46 steps rather than 1 —
  a real fix computes `minw` of the follow and gets 1).
- **Trailing bytes the match need not consume.** `bbbbb` suffix rows: 4,996
  steps rather than 1, because the clamp measures to the subject end and the
  match ends five bytes earlier. Sound, and honestly less tight — a 2,100×
  reduction rather than a 10,600,000× one. This is the mechanism's real
  limit and §9.2 states it as a residual rather than burying it here.
- **Nullable and unit-minimum inners** (`(a{0,3}){2,4}`, `(a{1,20}){1,50}`):
  `minrest` is 0 everywhere and no clamp is emitted. These shapes have ≤ 1
  baseline step anyway — declining them costs nothing.
- **Class bodies and a non-`a` literal** (`([ab]{10,20}){10,50}`,
  `(b{10,20}){10,50}`), and a nomatch subject against a matching pattern.

### 7.4 What a build lane owes on top

- `make test` in full, which this lane did not run (§10).
- The pcrec-vs-pcrec differential `eng_brep_design.md` §5.1 established as
  the primary instrument for this territory: replication with pruning against
  replication without, over the `.rxt` corpus, byte-identical expected.
- `tests/known_fail/d27_nested_min_boundary.rxt` will START PASSING. That is
  the ratchet's loud case by design; the test moves to `tests/base/` and K23
  closes.
- A `tests/codegen/` structural assertion that the clamp is PRESENT in the
  emitted C for a known shape — D46's observability half applied to this
  optimization, and the thing that stops it from being silently disabled.

---

## 8. Blast radius, predicted

- **Patterns with no bounded quantifier: zero change.** `minrest` is nonzero
  at plenty of points in an ordinary pattern (`\d{3}-\d{4}` has one at every
  position), so clamps WILL be emitted for them — the prediction is that they
  never fire and never change a verdict. BELIEVED, and it is the prediction
  most worth attacking; §6's throughput measurement is its only support and
  is three shapes wide.
- **The `.rxt` corpus: zero changed cells.** STRUCTURAL from §4.2 if the
  analysis is sound, and the pcrec-vs-pcrec differential is how it gets
  checked rather than asserted.
- **The known-fail ratchet fires** (§7.4).
- **`RX_VM_RUNGS` and the D46 stamp family**: a new strategy-selection point
  exists (clamped vs not, per quantifier), and D46 says every one must be
  OBSERVABLE and FORCEABLE. A build lane owes a stamp bit and a
  `--fno-length-prune` escape, on D46's terms, not on this note's.
- **`rx_info`**: nothing. No new field, no new error code, no ABI event —
  which is worth saying explicitly in a week where D47/D49 opened three.

---

## 9. Residuals, stated plainly

### 9.1 The bound is measured to the SUBJECT END, not to the match end

When the match need not consume the whole subject, `minrest` under-counts by
however many bytes trail the match, and pruning is correspondingly looser.
Measured at §7.3: 4,996 steps instead of 1 with a five-byte trailing suffix.
Still sound, still a 2,100× reduction, and no fix is proposed — a tighter
bound would need the match end, which is what the search is looking for.

### 9.2 It bounds LENGTH, and only length

An explosion driven by content ambiguity at constant total length is
untouched. No such open defect exists today; §5.3 is the pricing if one
appears.

### 9.3 The check frequency under counter-K is unmeasured

§4.5. Once-per-trip prunes less than once-per-iteration by a factor of K, and
BELIEVED to be enough. The lane building counter-K can measure it in an
afternoon once the rung lands; this lane could not, because it did not exist.

### 9.4 The prototype is not the analysis

Everything measured here inserts constants computed BY HAND from the
pattern's own numbers. The real mechanism computes them from the AST (§4.3).
The arithmetic is the same arithmetic; what is not established is that the
emitter's walk can thread the accumulator without restructuring. STRUCTURAL
argument in §4.3 (possessify already threads a follow set through the same
walk); no code written.

### 9.5 `minw` for UTF-8

Stated as 1 byte per `A_CLASS`, which is correct-and-loose for utf8 (a class
containing only non-ASCII code points has a minimum of 2). Loose is the safe
direction. A tighter `minw` for utf8 classes is available from the class
bitmap and is not designed here.

---

## 10. What I did NOT measure

1. **`make test`.** Not run. No `src/` change exists to test, and running the
   suite would have measured the unmodified compiler.
2. **The bench matrix.** §6's throughput probe is a purpose-built harness on
   three shapes, not `make bench`, which gates on load average and must run
   alone (D12/D17).
3. **libpcre2 as a third oracle.** python `re` only, per the base-tier rule.
   `eng_brep_design.md` §8 item 6 disclosed the same gap and R24 closed it
   from outside; the same is available here and would cost one lane-hour.
4. **The frames rung under pruning.** §2.5 measures that the class EXISTS
   there; the prototype patches cursor scan sites only, so no pruned
   measurement of a choice-bearing body exists. This is the largest single
   gap and the one a build lane will close first by construction.
5. **An independent oracle for the three-level rows.** §2.6's correctness
   check is pcrec-vs-pcrec; python did not return inside 100 s and libpcre2
   was not used. The small three-level shape `((a{1,2}){1,2}){1,2}` is in the
   corpus, was DECLINED by the prototype's guard, and costs ≤ 1 step anyway.
6. **Lazy and possessive outer quantifiers.** Every measured shape is greedy
   throughout. `eng_brep_design.md`'s R24 outcome is the standing warning here
   — the lazy half of that note's rule was the half that fell, and for a
   reason (`§2` there) that a length bound should be immune to but that
   nobody has checked.
7. **Subjects above ~300 bytes**, and the interaction with D49's work bound
   at the scale where that bound actually binds.
8. **Whether the clamp changes gcc's ability to compile the large replicated
   functions** of §2.5's family. The one shape that matters there could not be
   compiled at all.
9. **Anything about `(*ATOMIC)`, backrefs, or lookaround**, none of which have
   producers.

---

## 11. This lane's own instrumentation defects

Recorded because each produced numbers that would otherwise have entered this
note as findings — the discipline `k18_memo_design.md` §7 and
`eng_brep_design.md` §10 set.

### 11.1 The prototype mis-patched 44 cells, and the RANDOM corpus caught it

The first randomized run reported **44 DIFFER** — the pruned arm returning
`nomatch` where baseline and oracle both matched, and in one case returning a
9-byte match for a pattern whose lengths are multiples of 2.

Cause: `prune_proto.py` assumed every span-loop scan site it found was the
INNER loop of a replicated outer, and computed `minrest` from a per-replica
formula. For an exact-count inner that assumption is false — the inner is
possessified and the OUTER takes the cursor rung with ZERO replicas (§2.4),
so the single scan site is the outer's own cursor and the per-replica
arithmetic is simply the wrong arithmetic applied to the wrong loop.

Every one of the 44 was a shape whose baseline cost is 0 steps. The prototype
was breaking patterns that never had the bug.

The fix is an ASSUMPTION GUARD, not better arithmetic: `--replicas N` makes
the prototype REFUSE any file whose scan-site count is not what a replicated
outer must produce, and `diff3.py` passes the pattern's outer maximum. After
the guard: 14 shapes DECLINED, 762 cells, 0 DIFFER.

Two things this cost, both worth stating:

- The hand-chosen corpus would never have found it. Every shape in it was
  chosen because it exhibits K23, so every shape in it has an inner width ≥ 1,
  so none of them takes the mis-parameterized path. This is D27's lesson
  arriving from a different direction: a corpus derived from the defect
  inherits the defect's alphabet.
- It is also how §2.4 was discovered. The bug and the finding are the same
  observation.

### 11.2 `echo` with a `\n` inside a `sh` probe

Two probes were written with `echo 'fprintf(stderr,"STEPS %lld\n",…)'`, which
dash's `echo` expands, producing an unterminated string literal and a
`cc-fail` that reads exactly like "this pattern cannot be compiled". It
cost two false `cc-fail` rows before being caught. Every probe now uses a
quoted here-document for injected C, and `steps.sh` asserts both
substitutions landed exactly once before compiling — a silent no-op patch
would have reported 0 steps for every pattern, which is the check-design
failure mode this project keeps rediscovering: a control that shares a source
with what it controls.

### 11.3 A timeout that was a finding

`((a|b){10,20}){10,50}` hung a probe for 28 minutes. It was not the search —
it was gcc, on a 20,941-line function (§2.5). The lane's `timeout` discipline
turned it into a data point instead of a dead agent, which is the whole
reason the brief mandates it.

---

## 12. Rulings requested

None are blocking; the recommendation stands without them.

1. **Adopt MRL pruning as [M4.6c]'s answer to K23?** The measured case is
   §0.2/§5; the residuals are §9; the cost is §6.
2. **Does the clamp need a D46 forcing switch in v1** (`--fno-length-prune`),
   or is the observability bit enough? D46 says both halves; §8 assumes both;
   the build lane needs to know before it emits.
3. **`--follow-min`, i.e. computing `minw` of the follow, in v1 or deferred?**
   It is the difference between 46 steps and 1 on `(…){10,50}b` (§7.3), it is
   the same AST walk, and it is strictly more analysis. Recommend v1: the
   walk that computes one computes the other.
4. **Is the width-0 correction owed to `known_issues.md` K23?** §2.4 narrows
   the entry's stated class. This lane did not edit the entry.

---

## 13. Predictions, for the panel to attack

1. Emitting the clamp at every program point with `minrest > 0` changes ZERO
   cells of the `.rxt` corpus. (§8; the pcrec-vs-pcrec differential is the
   test.)
2. The `minw` walk written recursively overflows at the parser's 250-paren
   cap, exactly as `clo_visit` did. (§4.3; R23's own re-measurement is the
   precedent and the reason this is stated as a prediction rather than a
   caution.)
3. On the frames rung, the test form of §4.1 reduces `((a|b){7,12}){7,20}` at
   n = 49 from 51,993 steps to fewer than 50. (§2.5, §10 item 4.)
4. There is no greedy two-level bounded shape, of any inner width, for which
   pruning leaves more than `p` steps at `n = p·m` with an empty follow.
   (§4.4; 855 cells consistent, no proof.)
5. Raising the step budget to any value that answers `(a{11,22}){11,50}`
   answers no more of the family than that: the next size up needs ~11× more.
   (§2.2, §5.5.)
