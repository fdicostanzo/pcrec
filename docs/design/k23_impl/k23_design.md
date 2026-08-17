# K23 — the exact-minimum decomposition explosion, and the bound that deletes it

[M4.6c], design-first, 2026-08-17. Written on `k18_memo_design.md`'s
precedent: candidate mechanisms built as throwaway prototypes and measured
head to head, refutations recorded inline, every number re-runnable from
`probes/`.

**No engine code was written.** `src/` is untouched; the prototypes patch
ALREADY-EMITTED C, which is the only way this lane could measure the real
lowering without becoming the build lane.

---

## PANEL OUTCOME — R26 (2026-08-17), read this before any section

`../../dev/reviews/2026-08-17-r26-k23.md`. Three read-only critics. **The
design core HELD and was STRENGTHENED; the EMITTED FORM was REFUTED and the
EVIDENCE was re-anchored.** Every disposition is applied in place — marked at
the point of the change, not edited away.

What held, and is now stronger than this note originally argued:

- **Soundness is PREFERENCE-BLIND**, and the panel's derivation is better
  than the one this note shipped: `minrest` bounds whether an accepting
  continuation EXISTS, which is a language property and therefore
  order-invariant. Adopted as §2.8, provenance recorded. The critic set out
  to break it and instead measured it — the lazy-outer exemplar explodes
  identically (10,621,635 steps) and prunes to **0**, captures identical to
  python (§2.7).
- **The closed form is exact OUT OF SAMPLE** — three new instances, diff 0.

What fell:

- **§4.1's clamp was UNSOUND on any cursor rung with stride > 1** (E1). It
  landed the cursor off the iteration lattice, which deletes the correct
  position from the choice set. 5 of 8 subjects wrong on
  `((?:ab){10,20}){10,50}` — a shape with the identical baseline step count
  to the exemplar, so squarely in K23's live population. **Fixed** by
  lattice-rounding the cap (§4.1), soundness re-derived over it (§4.2 step 3),
  rung-by-rung consequences stated (§4.5).
- **The 855-cell differential was structurally blind to that** (E2/E9): every
  body came from a single-byte alphabet, so every rung had stride 1, where
  the bug is invisible. **Fixed** by giving the generator STRIDE and RESIDUE
  axes (§7.2.1) — this note's own §11.1 lesson, which it had not applied to
  its own generator. Re-run: **1,059 cells, 0 disagreements**, with a
  committed failing-direction control (`--no-lattice`).
- **The forward-work numbers had no probe** (M2/E6) and were labelled as
  D49's meter when they are a lane proxy. **Fixed both ways**: a real
  counting probe now exists and is archived (`probes/work.sh`,
  `out/work.txt`), and the quantity is relabelled as a proxy with ruling
  request 5 WITHDRAWN (§4.6, §12).
- **§9.1's trailing-suffix residual was a curve reported as a point** (E4),
  and K23 RETURNS at a 16-byte suffix. The panel also found the tight bound
  already exists at run time and is discarded. **Both applied**: the curve is
  §9.1's table, and the prefilter-window ceiling is prototyped and MEASURED
  to close the residual entirely (1 step at every suffix length). New ruling
  request 6.
- Smaller corrections applied throughout: §6 re-measured at 5.6× the clamp
  density (E5), §7.2's two exclusion paths separated (M1), §3's untraceable
  timing pair dropped for the panel's stronger ratio-tracking argument
  (M3/E8), prediction 2 REFUTED and §4.3's contradictory bullets reconciled
  (E7), ruling 2 withdrawn (D1), the gcc finding reattributed to counter-K
  (D2), and four column-reading defects (E10/M4/M5/D4).

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
| + MRL folded into the scan bound | **1** | **100** | same |

MEASURED (`probes/steps.sh` and `probes/work.sh`, archived at
`out/steps_curve.txt` and `out/work.txt`). The oracle (python `re`) says
`(0,100)` / group 1 `(90,100)`; all three arms that answer, answer that. The
folded arm's 100 is exactly one forward pass over a 100-byte subject — the
floor. (The work column is a LANE PROXY, not D49's `RX_ERR_WORK`; §4.6 says
precisely what it counts and why the distinction is not pedantry.)

Two things the clamp must get right, both of which this note's first version
did not and R26 caught: it must land **on the cursor's iteration lattice**
(§4.1 — off-lattice is unsound, not merely loose), and its ceiling should be
the **prefilter's match-end window** rather than the subject end (§9.1 —
without that, K23 returns at a 16-byte trailing suffix).

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
   STRUCTURALLY in §4.2 and attacked with a **1,059-cell** three-way
   differential in §7 — across strides 1–3, residues, and all four
   greedy/lazy combinations — which found 0 disagreements. It found 44 in the
   prototype first (§11.1) and, after R26, a real unsoundness in the emitted
   FORM that no cell count could have caught without a stride axis (§4.1,
   §11.4).

### 0.3 Seven things this note refutes, three of them the K23 entry's own and three its own

1. **"python `re` answers instantly"** (`known_issues.md` K23) is true of the
   exemplar and false of its mechanism. Python explores the SAME tree — its
   measured times track the closed form's node counts within 5% across four
   size steps (§3) — and it takes **2.8 s** one size up, **31 s** two sizes
   up and **368 s** three sizes up.
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
5. **The explosion needs a GREEDY INNER, not a greedy outer.** A lazy outer
   explodes identically (10,621,635); a lazy inner costs one step. The note's
   first version measured only the all-greedy corner and said nothing about
   the other three. §2.7.
6. **This lane's own prototype was wrong about 44 cells before the
   differential caught it**, and the reason is item 4 — it patched a shape
   whose emitted form is not what it assumed. §11.1.
7. **This lane's own CLAMP was unsound at stride > 1, and its own randomized
   generator could not see it** — because the generator drew every body from
   a single-byte alphabet, and at stride 1 the broken clamp and the correct
   one are arithmetically identical. Found by R26 E1; fixed at §4.1; the
   generator lesson is §11.4.

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

Selected rows (the probe prints every width 0–12; these are the ones the
prose uses, and the omitted rows interpolate smoothly between them):

| inner width w | first m | n = m·m | steps |
|---|---|---|---|
| 0 | **none at m ≤ 39** — see below | — | — |
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
takes 400 bytes.

The width-0 row is a search bound, not a proof: the probe sweeps `m` to 39
and reports "no crossing", which is why it reads `>39` in the raw output
(R26 E10 — the earlier label "never" overstated what the sweep establishes).
Width 0 never explodes for a stronger and independent reason anyway — an
exact-count inner is possessified and never reaches this search at all
(§2.4) — so nothing rests on the sweep's bound.

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
the multiplier stays bounded in general — two points is two points. All four
cells re-measured and archived at `out/multiplier.txt` (R26 M4: the
454,858 row had no archive in the first version).

**And the bound reaches it.** A choice-bearing body has no cursor range to
clamp, so §4.1's TEST form applies instead, at each iteration entry
(`probes/prune_proto.py --frames-sites`). MEASURED on
`((a|b){7,12}){7,20}`, against python `re` as oracle:

| n | 48 | 49 | 50 | 55 | 70 |
|---|---|---|---|---|---|
| baseline steps | 0 | 51,993 | 46,911 | 11,928 | 186 |
| pruned steps | 0 | **21** | 21 | 18 | 9 |
| span / g1 / g2 | nomatch | (0,49)(42,49)(48,49) | (0,50)(43,50)(49,50) | (0,55)(48,55)(54,55) | (0,70)(63,70)(69,70) |

The capture vectors are identical across baseline, pruned and oracle at every
length. This section was written as §13's prediction 3 ("fewer than 50
steps") and then measured; the prediction is kept there, marked CONFIRMED,
rather than quietly deleted.

**A separate finding from that family, reported because a timeout is a
finding.** `((a|b){10,20}){10,50}` emits in 0.105 s but produces a
20,941-line, 670 KB function, and **gcc cannot compile it**: `-O0` 4.0 s,
`-O1` 6.6 s, `-O2` still running past 120 s and past this lane's 300 s bound.
That is a downstream-compiler cost of replication × choice-bearing bodies,
adjacent to `eng_brep_design.md` §1.4's finding about pcrec's OWN cost but
about gcc rather than pcrec. **It belongs to COUNTER-K**, which D45 and the
plan already own for this class — not to [ENG-CLAMP], whose ruled charter is
the nested-tower K-downshift only (R26 D2 corrected the first version's
attribution; the manager forwarded the finding to the counter-K lane the same
session). Recorded so the next lane does not rediscover it as a hang.

### 2.6 THREE levels: the same defect, four orders of magnitude worse

MEASURED. `((a{2,4}){5,10}){5,20}` at its own exact minimum
`n = 5 × 5 × 2 = 50`:

| n | shipped steps | pruned steps | span / g1 / g2, BOTH arms |
|---|---|---|---|
| 50 | **11,906,349,370** | **6** | (0,50) (40,50) (48,50) |
| 51 | 9,609,677,279 | 6 | (0,51) (41,51) (49,51) |
| 55 | 2,379,665,827 | 6 | (0,55) (45,55) (53,55) |
| 60 | 363,901,065 | 6 | (0,60) (50,60) (58,60) |

Twelve thousand times the default budget, on a fifty-byte subject of `a`s.
The capture vectors are byte-identical between the arms at every row. **All
four baseline rows are now archived** (`out/three_level.txt`); the first
version claimed byte-identity at all four and had archived only 50 and 51
(R26 M17).

Three things follow.

- **The exemplar in the K23 entry is not the family's worst member**, and the
  entry's "100-byte ordinary input" framing understates the reach. Nesting
  multiplies: each level's decomposition space is explored inside every leaf
  of the level above it.
- **Python barely serves as the oracle here, and the number is the point.**
  `re.search` on this shape at n = 50 returns `(0,50) (40,50) (48,50)` — the
  same vector both pcrec arms give — after **451.6 s**. Seven and a half
  minutes on a fifty-byte subject. So the n = 50 row DOES have an independent
  oracle and all three arms agree on every slot; the n = 51/55/60 rows do
  not, and their check is pcrec-vs-pcrec — baseline replication as the ground
  truth, which is exactly the primary instrument `eng_brep_design.md` §5.1
  established for this territory. §10 keeps the remaining rows on the
  not-measured list.
- **The prototype needed a per-site `minrest` that is not one formula.** At
  three levels the constant at scan site `k` is
  `max(0, 5−(j+1))·2 + max(0, 5−(i+1))·10` with `i = k / 10`, `j = k % 10` —
  still pure compile-time arithmetic, but no longer indexable by a single
  rule, which is precisely why the real mechanism threads an ACCUMULATOR down
  the emitter's walk (§4.3) instead of indexing replicas. The prototype gets
  `--minrest-py` for this; the emitter does not need it.

### 2.7 The preference family: it is the INNER quantifier that explodes

MEASURED (`probes/steps.sh`), all four combinations at n = 100, and the
result is not what the note's first version assumed by omission:

| pattern | inner | outer | baseline steps | pruned |
|---|---|---|---|---|
| `(a{10,20}){10,50}` | greedy | greedy | 10,621,636 | 1 |
| `(a{10,20}){10,50}?` | greedy | **lazy** | **10,621,635** | **0** |
| `(a{10,20}?){10,50}` | **lazy** | greedy | **1** | — |
| `(a{10,20}?){10,50}?` | **lazy** | lazy | **0** | — |

**The explosion needs a GREEDY INNER and is indifferent to the outer.** A
lazy outer costs one step less than the all-greedy exemplar; a lazy inner
costs one step, full stop. §2.2 says why: the inner's preference is what
orders the decomposition search, and the unique all-minimum solution is the
LAST leaf only when the inner prefers maxima. Flip the inner and the same
solution is the FIRST leaf.

Two consequences.

- **The lazy-inner shapes need no fix**, and the prototype's structural
  inability to patch them (its scan-site pattern does not match the
  lazy cursor's emitted form, which walks UP from the minimum rather than
  down from the maximum) costs K23 nothing. It is still a coverage gap and
  §10 keeps it.
- **The lazy-OUTER shape is a live K23 instance that the note's first
  version did not contain**, and it is the one that matters: 10,621,635
  steps, `RX_ERR_STEPS` at the default budget, and the pruned arm answers in
  **0** steps with a capture vector identical to python's at every length.
  It is now in `cases_prune.tsv` with all four combinations.

**The lazy emitted form, for the build lane.** A lazy cursor rung emits the
mirror shape — consume exactly `rmin` iterations mandatorily, then EXTEND by
one stride per backtrack (`rx_L6` in the emitted listing:
`if (rx_cur >= low + rmax) goto rx_fail; rx_cur += W;`). The bound applies
unchanged in meaning and mirrored in form: rather than clamping the starting
maximum DOWN, it caps how far the extension may go, `cap` computed by the
same lattice-rounded expression of §4.1. It is the same `minrest`, the same
rounding, and the same soundness argument; only the direction of travel
differs. NOT MEASURED (§10) — the prototype cannot reach it, and there is no
explosion behind it to make the measurement urgent.

### 2.8 Why preference does not enter the soundness argument at all

STRUCTURAL, and stated explicitly because R26's engine critic derived it more
sharply than this note originally did — the argument is theirs, recorded with
provenance.

`minrest(q)` bounds **whether an accepting continuation EXISTS** from a
program point. Existence is a property of the LANGUAGE, not of the search
order: the set of accepting continuations from `(q, pos)` is the same set
whichever arm the engine tries first. So a subtree with no accepting leaf has
no accepting leaf under greedy, under lazy, and under any future preference
spelling; deleting it cannot move the first accepting leaf in ANY order,
because it contained no leaf that any order could have selected.

That is why §4.2 never mentions greedy or lazy and does not need to. It is
also the strongest available answer to R24's standing warning that the lazy
half is where rules fall: the possessification rule R24 refuted was
order-DEPENDENT (it reasoned about which position a loop stops at, which is
exactly what preference decides), where this one is order-INVARIANT by
construction. The measurement in §2.7 is a check on that argument, not its
basis — 155 cells across all four preference combinations, 0 disagreements.

---

## 3. Why python is fast, answered — and it is not fast

The brief asked for one cheap measurement of why python `re` answers
instantly, on the theory that its mechanism might be a hint. It is a hint,
but not the one expected.

MEASURED (`python3 -c` timing, reproduced in `out/python_growth.txt`):

| shape | n | python `re` |
|---|---|---|
| `(a{10,12}){10,50}` | 100 | 0.86 ms |
| `(a{10,15}){10,40}` | 100 | 34.8 ms |
| `(a{10,20}){10,50}` | 100 | **265 ms** |
| `(a{11,22}){11,50}` | 121 | **2.75 s** |
| `(a{12,24}){12,50}` | 144 | **30.8 s** |
| `(a{13,26}){13,50}` | 169 | **368 s** |

(The archived figures. An earlier run of the same code gave 1.11 ms /
48.5 ms / 272 ms / 2.90 s / 32.4 s / 384 s — same shape, ±10%, and the ratio
between consecutive rows is ~11× in both.)

Python has **no pruning rule**. It explores the same tree, and the growth is
the law of §2.2. Its per-node cost is comparable to pcrec's: pcrec with the
budget lifted answers the exemplar in **0.222 s** against python's 0.272 s,
on 10.6 M resumptions — pcrec is marginally the faster of the two, on the
same work.

**The evidence that python walks the SAME TREE is the ratio column, not a
wall-clock pair** (R26 M3/E8; the first version of this section compared
"pcrec 222 ms vs python 272 ms", which was untraceable — no pcrec wall-clock
probe exists — and silently mixed an unarchived run's figure with the
archived one. The pair is DROPPED; the argument it was supporting is
stronger without it, and the panel supplied the better form):

MEASURED, `probes/model.py --ratios` (which reads the archived python times
and the law side by side, so the comparison is re-runnable rather than
retyped):

| step from → to | python time ratio | closed-form step ratio (§2.2) | agreement |
|---|---|---|---|
| (10,15,10) → (10,20,10) | 7.61× | 7.99× | 4.7% |
| (10,20,10) → (11,22,11) | 10.38× | 10.48× | 1.0% |
| (11,22,11) → (12,24,12) | 11.19× | 11.27× | 0.7% |
| (12,24,12) → (13,26,13) | 11.96× | 12.04× | 0.7% |

Python's measured times track the composition law's predicted NODE COUNTS
within 5% across four size steps. A shared per-node constant is the only
simple explanation for that, and it is far better evidence than any single
timing pair could be: the law was derived from pcrec's emitted search, and it
predicts python's wall clock.

Two consequences, and they matter to how K23 is framed:

- **The difference is a policy difference, not an algorithmic one.** pcrec
  has a budget and stops at 10⁶; python does not and grinds. The K23 entry's
  "python answers instantly, pcrec returns RX_ERR_STEPS" reads as an
  algorithmic gap. It is not one.
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
if ((size_t)(CEIL - pos) < MINREST_q) goto rx_fail;   /* frames rung */
```

where `CEIL` is the subject end `n` in the plain form and the prefilter's
match-end window in the tighter one (§9.1). The frames form needs no lattice
rounding — it tests a single position the engine has already reached, rather
than selecting one from a range.

and, at a cursor rung — where the engine is choosing among a RANGE of
positions rather than one — the same test is expressed as a clamp on the
range's upper end, which cuts the whole doomed suffix in one operation.

**The clamp must land ON THE CURSOR'S ITERATION LATTICE. (R26 E1 — this
note's first version got it wrong, measurably.)** A stride-W span loop
admits only the positions `pos, pos+W, pos+2W, …`. The obvious clamp,

```c
if (rx_cur > n - MINREST_q) rx_cur = n - MINREST_q;   /* WRONG for W > 1 */
```

lands the cursor between two lattice points whenever `n − MINREST_q − pos`
is not a multiple of `W`, and an off-lattice cursor poisons the entire
retreat chain: the retreat walks down by `W` from a position that was never
an iteration boundary, so every position it visits is also off-lattice and
the CORRECT cursor value is deleted from the choice set. That is not pruning
— it is substitution, and it breaks §4.2's soundness step 3 in the
introducing direction (it adds a candidate that was never there). MEASURED
on `((?:ab){10,20}){10,50}`, which has the same rung structure and the
IDENTICAL baseline step count as the exemplar (10,621,636), so it is
squarely in K23's live population: **5 of 8 subjects answered `nomatch`
where baseline and python match.** At W = 1 the defect is invisible, which
is why 855 cells of single-byte corpus never saw it (§7.2.1).

The repair is to round DOWN onto the lattice, and it is cheap arithmetic:

```c
if (CEIL < MINREST_q || CEIL - MINREST_q < pos) goto rx_fail;
{ const size_t cap = pos + W * ((CEIL - MINREST_q - pos) / W);
  if (rx_cur > cap) rx_cur = cap; }
```

`pos` is the iteration start, which the emitted scan block already has in
hand — it is what the low-water slot was just written to (§1) — so nothing
new has to be tracked. A ceiling below `pos` means the continuation is
infeasible outright and the replica fails.
At W = 1 the rounding is the identity, so every stride-1 measurement in this
note is unchanged by it (verified: exemplar still 1 step).

This form is why the exemplar collapses to a single step rather than merely
to a smaller number: the clamp deletes ten of the eleven inner choices at
every replica at once, and now does so at every stride.

### 4.2 Soundness — STRUCTURAL

The claim: pruning changes no answer, including no capture.

1. `minrest(q)` is a LOWER bound on the bytes consumed by any accepting
   continuation. So `n − pos < minrest(q)` implies that no accepting
   continuation exists from `(q, pos)`.
2. Every position the clamp removes is therefore a position whose subtree
   contains no accepting leaf.
3. Preference order among the SURVIVING positions is untouched. The clamp
   deletes candidates and the subtrees below them; it never reorders
   alternatives, never converts greedy to lazy, never changes which branch is
   the fallthrough, and **never introduces a candidate that was not there.**
   That last clause is load-bearing and is exactly what the unrounded clamp
   violated (§4.1, R26 E1): substituting an off-lattice position for a real
   one satisfies "removes only doomed candidates" and still changes the
   answer, because the candidate it leaves behind is not in the loop's choice
   set at all. Re-derived over the lattice form: `cap` is `pos + W·j` for an
   integer `j ≥ 0`, so `cap` is a real iteration boundary; clamping `rx_cur`
   to it therefore selects an EXISTING member of the choice set, and the
   retreat chain below it visits exactly the members it would have visited
   anyway. Soundness needs both halves — the bound must be a lower bound AND
   the clamped value must be a position the loop could have reached.
4. PCRE2 leftmost-first is "FIRST COMPLETE MATCH WINS" (`engine_m4.md` §3.1),
   so the answer is determined by the first accepting leaf in preference
   order. Deleting subtrees that contain no accepting leaf cannot move it.
5. Therefore span and every capture slot are unchanged — including the
   capture spans D44.1 derives FROM THE CURSOR at loop exit rather than
   writing per iteration, since the cursor's surviving preferred value is by
   (3) the same value it would have taken unclamped.
6. The clamp is stated against the absolute subject end `n`, not against the
   attempt's start position, so it is unchanged by the search entry's
   start++ retry loop. §7.3 exercises that axis.

The single failure mode is an UNSOUND analysis — a `minrest` that
OVER-estimates. Under-estimating is always safe (it prunes less), which is
the direction every conservative case below takes, and which is what the
prototype's `--follow-min 0` default does (§7.3).

### 4.3 Computing `minrest` — a small AST walk, and a threading rule

The minimum-width function over the AST (`src/core/internal.h`'s eight node
kinds — `A_CLASS`, `A_CAT`, `A_ALT`, `A_REP`, `A_EMPTY`, `A_BOL`, `A_EOL`,
`A_CAP`; the prose said seven, the table was always complete, R26 D4):

| node | `minw` |
|---|---|
| `A_CLASS` | 1 byte (see the note below the table — R26 E10) |
| `A_EMPTY`, `A_BOL`, `A_EOL` | 0 |
| `A_CAT(l,r)` | `minw(l) + minw(r)` |
| `A_ALT(l,r)` | `min(minw(l), minw(r))` |
| `A_REP(l,rmin,·)` | `rmin · minw(l)` |
| `A_CAP(l)` | `minw(l)` |

`A_CLASS` is **1 byte, unconditionally**, in both encodings. That is exact
for ascii and deliberately LOOSE for utf8, where a class holding only
non-ASCII code points has a true minimum of 2 or more; loose is the safe
direction (§4.2) and §9.5 keeps the tightening as an unbuilt option. The
table row and this prose said slightly different things in the first version
— the row read as though the value varied with the encoding, and it does not
(R26 E10).

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

**A second compile-time quantity has to reach the clamp site: the cursor's
STRIDE** (R26 E1). The emitter already computes it — it is what the rung
selection printed as "stride 2" in §1's dump and what the scan block
increments by — so this is a value already in hand at the emission point,
not a new analysis. It is nonetheless a second thing the clamp depends on,
and a clamp emitted without it is unsound rather than merely weak, which is
why it is called out here rather than left to the codegen step.

Two implementation notes that are design decisions, not details. **The first
one is CORRECTED here — as first written the two contradicted each other
(R26 E7), and the one that was wrong was mine.**

- ~~`minw` must not recurse on pattern structure.~~ **Refuted by the shipped
  compiler.** `src/opt/possessify.c`'s `pss_walk` recurses on pattern
  structure today, and `build/pcrec` compiles a 249-paren-deep pattern
  without trouble (MEASURED: depths 100, 200 and 249 all compile). The real
  rule, which is what D10/DD-10 and K18 actually teach, is narrower:
  **the walk's C-stack depth must be at most LINEAR in pattern depth.** K18's
  `clo_visit` was not a problem because it recursed; it was a problem because
  it recursed **Θ(d²)** — 31,377 frames at the parser's cap
  (`k18_memo_design.md` §2a's own re-measurement). `minw` is a single
  post-order pass with one frame per node on the path, i.e. Θ(d), and is in
  the same class as the walk that already ships.
- **The threading seam already exists**, and this is now consistent with the
  bullet above rather than in tension with it: `pss_walk` threads a FOLLOW
  first-set down the same tree for the same reason, recursively and safely.
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
- **The cursor ladder.** MRL is expressible on every rung, and each rung
  fixes which FORM applies — this is the list R26 E1 found the note leaning
  on without stating:
  - *disjoint-follow*: nothing to prune, no machinery is emitted.
  - *fixed-stride cursor*: the clamp form, rounded to `W` = the stride.
  - *reverse-deterministic cursor*: the clamp form, but the iteration
    boundaries are NOT an arithmetic lattice — they are recovered by walking
    the reversed body automaton (`engine_m4.md` §2.5). Rounding "down to the
    nearest boundary" is therefore a WALK, not a division, and the
    lattice argument of §4.2 step 3 has to be re-made in terms of that walk.
    **NOT MEASURED — no reverse-deterministic shape was pruned in this lane**
    (§10), and this is the rung where a build lane should expect the E1 class
    of bug to recur in a new spelling.
  - *frames*: the test form, at each iteration entry (§2.5, measured).
  - *variable-length with a boundary record*: the record IS the lattice;
    clamp to the largest recorded boundary that satisfies the bound.

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

**What is being counted, stated before the numbers (R26 M2/E6 found the
first version of this section asserting more than it had).** This is a LANE
PROXY, not D49's meter:

> one unit = one iteration of a span-loop scan body, i.e. one stride of
> greedy forward walking.

That is the forward work the step counter is structurally blind to, which is
the *quantity* D49 exists to bound. It is **not** `RX_ERR_WORK`'s number:
that meter charges at emitter-chosen sites and landed in the counter-K build
after this lane measured, so no matcher this lane can produce contains a
single one of its charge points. Any ratio below is a proxy ratio.

MEASURED by `probes/work.sh`, archived at `out/work.txt` — the probe the
first version of this section did not have:

| shape | n | arm | steps | scan work |
|---|---|---|---|---|
| `(a{10,20}){10,50}` | 100 | shipped | 10,621,636 | 55,684,363 |
| | | clamp after the scan | 1 | 190 |
| | | clamp folded into the scan bound | 1 | **100** |
| `(a{11,22}){11,50}` | 121 | shipped | 111,354,519 | 624,582,267 |
| | | folded | 1 | **121** |
| `((?:ab){10,20}){10,50}` | 200 | shipped | 10,621,636 | 55,684,363 |
| | | folded | 1 | **100** |
| `((?:abc){7,14}){7,30}` | 147 | shipped | 15,499 | 63,190 |
| | | folded | 1 | **49** |

The folded arm costs exactly one scan step per iteration of the accepting
decomposition — 100 at n = 100, 121 at n = 121, 49 for a 147-byte subject
walked in 3-byte strides. That is a single forward pass, and it is the
strongest form of the argument for the folded emission: the proxy drops by
five to six orders of magnitude and lands on its floor.

**Ruling request 5 is WITHDRAWN** (§12). The shipped arm's work-per-step
ratio here is 5.24, and it is a proxy ratio measured on a proxy quantity; it
is not a defensible calibration input for D49's default, and the manager's
provisional adoption of it is correctly retracted. Re-anchoring against the
real meter costs one lane-hour once counter-K lands on main — the probe and
the shapes already exist, only the counting site changes. The DESIGN
argument for the folded form does not depend on the number and stands.

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
| baseline | 80,356 | 0.80 s | 10,621,636 | 10,260,900 | 1,957,091 | 2,241 | — |
| MRL prune | 82,921 (+3.2%) | 0.76 s | **1** | 1 | 1 | 1 | — |
| memoization | 86,544 (+7.7%) | 0.93 s | 2,071 | 2,026 | 1,621 | 371 | 25,650 B |

(The prune arm's size is the POST-R26 figure: the lattice rule added a line
and an expression per site, taking it from +1.6% to +3.2%. Still under half
the memo arm's, and gcc is unchanged.)

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
   The law is `q · ceil((n+8)/8)` bytes — the `+8` is the row padding the
   prototype allocates, which the first version's `q·n/8` dropped; it
   accounts for 50 bytes of the 25,650 and changes no argument (R26 M5).
   Against D19's recorded 128 KB thread stack, an
   allocation-free stack-resident memo caps the subject at
   `128 KB × 8 / 50 ≈ 20,971 bytes` for THIS pattern — three orders of
   magnitude below where the step budget would notice, and the same shape of
   ceiling D44.1/D44.5 already had to stamp for frames. A heap memo is not
   available: generated matchers are allocation-free by mandate
   (`COPY_MATCHED_SUBJECT=NEVER`'s precedent, `engine_m4.md` §2.2).
   K18's memo precedent does not transfer — that one was COMPILE-time, where
   allocation is ordinary.
2. **It does not actually fix the exemplar, it bounds it.** The memo caps
   total steps at `q·n` — 50 × 100 = 5,000 here, and 2,071 measured, which is
   the consistency check on the mechanism. But that bound GROWS WITH THE
   SUBJECT where pruning's does not: at the memo's own ~20,971-byte ceiling
   from item 1 the cap is `50 × 20,971 ≈ 1.05 M`, which is the default step
   budget again. The memo trades an exponential for a linear-in-`n`
   quantity; pruning trades it for a linear-in-`p` one, and `p` is a property
   of the pattern.
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

**At the RECOMMENDED clamp density** (R26 E5: the first version measured
three shapes with an EMPTY follow, where `minrest` is 0 at the last
`outer_min − 1` replicas and only **9 of 50** sites carry a clamp — 18% of
what the note proposes shipping). These rows use a real non-empty follow so
that every replica is clamped, **50 of 50**, and they carry the lattice
rule's integer division:

| shape | W | base | placebo | prune | clamp only | total |
|---|---|---|---|---|---|---|
| `(a{2,4}){10,50}b` | 1 | 1726.5 ns | 1749.7 ns | 1757.7 ns | +0.46% | **+1.8%** |
| `((?:aa){2,4}){10,50}b` | 2 | 3003.0 ns | 3019.5 ns | 3061.0 ns | +1.37% | **+1.9%** |
| `((?:aaa){2,4}){10,50}b` | 3 | 4276.2 ns | 4246.5 ns | 4270.5 ns | +0.57% | **−0.1%** |

At 5.6× the clamp density and with the division the lattice rule adds, the
cost is **≤ 2%**, and on the stride-3 shape the pruned build is marginally
faster than the unpruned one. "clamp only" is prune-vs-placebo, i.e. the
clamp's own instructions with code-layout drift subtracted.

**The sparse-density rows, kept** (empty follow, 9 of 50 sites), because they
are what the note originally reported and dropping them would hide the
correction:

| shape | n | base | placebo | prune | total |
|---|---|---|---|---|---|
| `(a{10,20}){10,50}` | 300 | 1969.4 ns | 1989.5 ns | 2027.8 ns | +3.0% |
| `(a{2,4}){10,50}` | 200 | 1588.1 ns | 1586.1 ns | 1572.6 ns | −1.0% |
| `(a{1,2}){10,50}` | 60 | 597.1 ns | 600.0 ns | 600.3 ns | +0.5% |

Read honestly across both tables: the effect is inside a ±3% band whose sign
varies by shape, and DENSITY DOES NOT DRIVE IT — the densest rows are not the
most expensive ones, which is the useful thing this correction produced. Half
or more of the largest observed penalty is code LAYOUT rather than the
clamp's instructions, which is what the placebo arm exists to separate.

Run-to-run variation is of the same order as the effect: an earlier
nine-repetition run of the identical sparse harness gave +3.7% / +1.7 layout
on the first shape. Both runs support the same reading and neither supports a
tighter one.

MEASURED, not extrapolated: six shapes on one box, on a harness built for
this question rather than `make bench`. What it supports is "the clamp is not
a throughput event"; it does not support a claim that the clamp is free, and
§10 lists the benchmark this lane did not run.

### 6.2 Compile-time and code size

From §5.1: **+3.2%** of emitted C (it was +1.6% before the lattice rule
added a line and an expression per site), and gcc −O2 marginally FASTER
(0.80 s → 0.76 s), which is noise at this scale. The clamp adds five lines
per site and no new symbols, macros or struct members — except the one
`size_t` in `rx_work` if ruling 6's prefilter ceiling is taken (§8).

### 6.3 Forward work

§4.6's table, measured by `probes/work.sh` and archived at `out/work.txt`.
The clamp REDUCES the forward-work proxy by five to six orders of magnitude
on the exploding shapes and adds a bounded constant elsewhere; in its folded
form it lands on exactly one forward pass over the subject.

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

Two properties added after R26, both of them about the instrument rather
than the result:

- **It can be run in the FAILING direction.** `K23_PRUNE_EXTRA=--no-lattice`
  re-emits the pre-R26 unrounded clamp across the whole corpus, so the
  corpus's power against the lattice rule is a measured number rather than
  an assumption (§7.2.1). This is what the note's first version had no way
  to state, and its absence is why 855 green cells read as reassurance.
- **A zero exit with no output file is a hard failure**, not a crash later.
  It happened for real mid-revision (§11.5), and without the check the
  harness could have compared the baseline arm against itself and reported
  agreement — the exact check-design failure this project keeps
  rediscovering.

### 7.2 The populations, and the result

**These are the POST-R26 populations**, over corpora that gained stride and
residue axes (§7.2.1) and the lazy preference family (§2.7). The pre-R26
figures were 855 cells over single-byte-body corpora, and they were blind by
construction to the defect R26 E1 found.

| corpus | shapes | measured | guard-declined | no-clamp | cells | AGREE | DIFFER |
|---|---|---|---|---|---|---|---|
| `cases_prune.tsv` (chosen around known boundaries) | 25 | 19 | 0 | 6 | 155 | 155 | **0** |
| `cases_random.tsv` (seeded, `gen_cases.py --seed 23`) | 140 | 95 | 15 | 30 | 904 | 904 | **0** |

**1,059 cells, 0 disagreements, on the full capture vector.**

**The two exclusion paths are different things and the first version of this
note ran them together (R26 M1).** They are separated above:

- *guard-declined* — the shape reached `prune_proto.py`'s assumption guard
  and was REFUSED as out-of-shape (§11.1). 15 of 140 random shapes.
- *no-clamp* — the shape was patched successfully and the arithmetic put
  `minrest` at 0 everywhere, so no clamp was emitted and the pruned arm is
  byte-identical to the baseline. 30 of 140. These cells are real AGREEs but
  they exercise nothing.

So the randomized corpus exercises the mechanism on **95 of 140 shapes
(68%)**, not the ~88% a single "excluded" bucket would have implied. Neither
path can inflate the AGREE count — an excluded shape contributes no cells at
all — but the coverage narrative was overstated and is corrected here.

Both corpora exist because either alone misleads. The hand-chosen one
contains the defect: **64 of its 155 cells exceed the 10⁶ default budget in
the baseline arm**, up to 111,354,519 steps, and the worst pruned cell among
them is 4,996 (the trailing-suffix residual, §9.1). The randomized one
contains far less of it — its box is capped at `p·m ≤ 60` iterations so that
python can serve as oracle at all, and only 9 of its 904 cells cross the
budget — but it samples the shape space the hand-chosen one cannot, which is
where a soundness bug hides. Aggregate over the random corpus: 28,768,539
baseline steps → **619** pruned, maximum 1.

The random corpus is what caught both of this lane's own defects (§11.1,
§11.4); the chosen corpus would have caught neither.

### 7.2.1 The two axes R26 E2 added, and why 855 cells could not see E1

Every inner body in the first version's corpora was drawn from a single-byte
alphabet, so every cursor rung it produced had **stride 1** — and at stride 1
the lattice rounding is the identity. The corpus could not distinguish the
correct clamp from the broken one under any subject, because the two emit
arithmetically equal code there.

- **STRIDE.** Bodies of width 1, 2 and 3 (`a`, `[ab]`, `(?:ab)`, `(?:abc)`,
  `(?:[ab][cd])`). The regenerated random corpus is 81 stride-1, 42 stride-2,
  17 stride-3 shapes.
- **RESIDUE.** The subject is now built as a UNIT repeated and TRUNCATED to
  the requested byte length, so a length that is not a multiple of the stride
  leaves a half-unit tail; and non-empty prefixes shift the lattice origin off
  zero. Without a residue axis every length is a multiple of `W` and agrees
  with the broken clamp by parity accident — which is precisely how the one
  row that DID agree in E1's eight (`z`+`ab`×100) agreed.

**Validated in the failing direction over the WHOLE corpus, which is the
part that makes it a check.** `K23_PRUNE_EXTRA=--no-lattice` re-emits the
pre-R26 clamp for every shape and re-runs the differential. MEASURED:

| stride | cells DIFFER | shapes with ≥1 DIFFER |
|---|---|---|
| 1 | **0 of 506** | **0 of 57** |
| 2 | 51 of 290 | **29 of 29** |
| 3 | 30 of 108 | **9 of 9** |
| all | 81 of 904 | 38 of 95 |

The hand-chosen corpus goes red the same way: 20 of its 155 cells, spread
over all four of its stride > 1 shapes (including the lazy-outer one).
**101 of 1,059 cells across both corpora, and not one of them stride 1.**

Two readings, and the first is the more important:

- **Zero of 506 stride-1 cells go red.** That is not a weak result, it is the
  PROOF of this section's premise: at stride 1 the broken clamp and the
  correct one are arithmetically the same code, so no subject of any length
  can separate them. The old corpus was not unlucky, it was structurally
  incapable, and this row measures that rather than asserting it.
- **Every single stride > 1 shape goes red** — 29 of 29 and 9 of 9,
  independently reproducing E9's "12 stride>1 shapes, EVERY one wrong
  somewhere". The axis is not merely present, it is decisive on every member
  of the population it was added for.

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
  match ends five bytes earlier. Sound, and less tight — and §9.1 now shows
  that "less tight" is a CURVE that puts K23 back over the budget at sixteen
  bytes, plus the fix for it. These rows are the corpus's five-byte sample of
  that curve.
- **STRIDE > 1 and subject-length RESIDUES** (added R26 E2, §7.2.1). The
  `((?:ab){10,20}){10,50}`, `((?:abc){7,14}){7,30}` and
  `((?:[ab][cd]){10,20}){10,50}` rows, at lengths on and off the stride
  lattice, with prefixes that shift the lattice origin. These are the rows
  that go RED under `--no-lattice`, which is what makes them a check.
- **All four GREEDY/LAZY combinations** on both quantifiers (added R26 E3,
  §2.7), including the lazy-outer explosion that costs 10,621,635 baseline
  steps and 0 pruned.
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
  is six shapes wide.
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
- **`rx_work` gains ONE `size_t`** if ruling 6 is taken (§9.1's prefilter
  window). That is a local struct in the emitted matcher, not an ABI type, so
  the line above still holds; it is called out because "nothing changes" was
  easier to say before the panel improved the design.
- **The stride becomes load-bearing at the clamp site** (§4.3). A rung that
  reports its stride wrongly now produces a WRONG ANSWER rather than a slow
  one, which raises what D46's per-quantifier rung stamp is worth: it is the
  observability half of a value that correctness now depends on.

---

## 9. Residuals, stated plainly

### 9.1 The bound is measured to the SUBJECT END — and that is not a residual, it is a CURVE with a break-even

**Corrected per R26 E4; the first version of this section reported one data
point and called it a limit, and the point it chose was the flattering one.**

When the match need not consume the whole subject, `minrest` under-counts by
however many bytes trail the match, and pruning loosens accordingly. Sweeping
the trailing-suffix length `t` on the exemplar at n = 100 (MEASURED, the
lattice build):

| t | 0 | 2 | 5 | 8 | 11 | 14 | **16** | 18 | 20 | 25 | 40 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| steps | 1 | 211 | 4,996 | 48,611 | 218,303 | 579,515 | **1,153,352** | 2,220,924 | 4,066,274 | 6,163,467 | 10,619,634 |

**K23 RETURNS at a 16-byte trailing suffix** — 1,153,352 steps is
`RX_ERR_STEPS` against the default budget — and by t = 40 the pruned matcher
is back within 0.02% of the unpruned one. Reporting this as "4,996 instead of
1, still a 2,100× reduction" was true and misleading: the mechanism has a
break-even, and it is at sixteen bytes.

**The tight bound already exists at run time and is thrown away.** This is
the panel's finding, adopted, provenance recorded (R26 E4 — the same shape as
R25's settlement 4, where the critic's option was the better one). The
emitted `rx_search` contains:

```c
ptrdiff_t win[1][2];
if (rx_prefilter(s, n, startpos, win) != 1) return 0;
start = (size_t)win[0][0];          /* win[0][1] is never read */
```

The capture-erased forward+reverse DFA pair computes the match-END window
and the next line discards it. Threading `min(n, win[0][1])` as the clamp's
`CEIL` (§4.1) closes the residual on the default path.

**MEASURED, as a prototype** (`probes/prune_proto.py --prefilter-ceiling`,
which plumbs `win[0][1]` through a file-scope variable — a prototype
shortcut; TS-1 forbids mutable globals in generated code, so a real version
carries it in `rx_work`, which every entry already threads):

| t | 0 | 5 | 14 | 16 | 20 | 25 | 40 |
|---|---|---|---|---|---|---|---|
| subject-end ceiling | 1 | 4,996 | 579,515 | 1,153,352 | 4,066,274 | 6,163,467 | 10,619,634 |
| prefilter-window ceiling | **1** | **1** | **1** | **1** | **1** | **1** | **1** |

The curve does not flatten, it disappears — one step at every suffix length,
answers unchanged. The whole residual is closed.

**POSITION, since the manager asked for one: adopt it in v1.** The window is
already computed on the default path, so the run-time cost is carrying one
`size_t` in `rx_work` and reading it instead of `n`; the correctness argument
is unchanged (a tighter CEIL is still an upper bound on what an accepting
continuation can consume, so §4.2 goes through verbatim with `CEIL` in place
of `n`). Three things a build lane must handle, none of them large:
- the entries that run NO prefilter (`rx_match`, and `--engine=vm`, which
  disables it) must default `CEIL` to the subject end, or the clamp reads a
  stale window;
- the window is per-SEARCH-ATTEMPT, and `rx_search`'s retry loop advances
  `start` without recomputing it — a build lane must confirm `win[0][1]`
  stays valid across those retries or recompute it;
- it makes the prune's tightness depend on the prefilter being ON, which is a
  D46 strategy-selection interaction and should be visible in the stamp.

If any of those turns out to bite, the fallback is the subject-end ceiling
already measured — strictly weaker, never wrong.

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
   six shapes, not `make bench`, which gates on load average and must run
   alone (D12/D17).
3. **libpcre2 as a third oracle.** python `re` only, per the base-tier rule.
   `eng_brep_design.md` §8 item 6 disclosed the same gap and R24 closed it
   from outside; the same is available here and would cost one lane-hour.
4. **The frames rung beyond ONE shape, and beyond iteration ENTRIES.** §2.5
   measures `((a|b){7,12}){7,20}` pruned (51,993 → 21) and that is the whole
   of the evidence: one pattern, five lengths. The prototype's frames mode
   also tests only at iteration ENTRIES — it does not push the bound down
   into the alternation's own choice points inside a body, which a real
   emitter threading the accumulator would reach. Both of those are more
   pruning, not less, so the measured 21 is an upper bound on what the
   mechanism achieves there; that direction is argued, not measured.
5. **An independent oracle for the three-level rows above n = 50.** Python
   answered n = 50 (in 451.6 s, agreeing on every slot) and was not run to
   completion on 51/55/60; libpcre2 was not used at all. The small three-level shape `((a{1,2}){1,2}){1,2}` is in the
   corpus, was DECLINED by the prototype's guard, and costs ≤ 1 step anyway.
6. ~~**Lazy and possessive outer quantifiers.**~~ **CLOSED for lazy** by R26
   E3 and §2.7/§2.8: all four greedy/lazy combinations are measured and in
   the corpus, the lazy-outer explosion is the same size and prunes to 0, and
   §2.8 states why preference cannot enter the soundness argument at all.
   What remains open here is narrower: the **lazy cursor rung's own emitted
   form** (§2.7's last paragraph) is designed and unmeasured, because the
   prototype's scan-site pattern cannot match it and there is no explosion
   behind it; and **possessive** quantifiers are untouched.
7. **The REVERSE-DETERMINISTIC cursor rung** (§4.5). Its iteration boundaries
   are recovered by a backwards walk rather than by arithmetic, so §4.1's
   division does not apply and the lattice argument has to be re-made. No
   shape on that rung was pruned. This is the successor to item 4 as the
   likeliest place for the E1 class of bug to recur, and §13's new
   prediction 6 says so.
8. **Subjects above ~600 bytes**, and the interaction with D49's work bound
   at the scale where that bound actually binds — which needs the real meter
   (§4.6), not this lane's proxy.
9. **The prefilter-window ceiling beyond the exemplar** (§9.1). One shape,
   seven suffix lengths, and a prototype that plumbs the window through a
   file-scope variable rather than `rx_work`. The three obligations §9.1
   names for a build lane are stated, not tested.
10. **Whether the clamp changes gcc's ability to compile the large replicated
    functions** of §2.5's family. The one shape that matters there could not
    be compiled at all.
11. **Anything about `(*ATOMIC)`, backrefs, or lookaround**, none of which
    have producers.

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
the guard: 14 shapes declined, 762 cells, 0 DIFFER. (Those are the
PRE-R26 figures, kept because they are what the guard was validated against;
the corpus has since gained two axes and the current populations are
§7.2's.)

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

### 11.4 The generator inherited the defect's alphabet — the same lesson, one level up

Recorded because it is §11.1's lesson recurring against the lane that had
just written §11.1, which is worth more than either instance alone.

§11.1 ends by saying that a corpus derived from the defect inherits the
defect's alphabet, and that the randomized generator is the cure. It was —
for the axis it varied. But the generator drew every inner body from a
SINGLE-BYTE alphabet, so every cursor rung it produced had stride 1, and at
stride 1 the correct clamp and the broken one emit arithmetically equal code.
855 cells could not distinguish them under any subject. R26 E1 found the bug
in ten minutes with a two-byte body.

The generalisation, sharper than §11.1 reached: **randomising a corpus
protects only the axes the generator can express.** The fix was not more
cells — it was two new AXES (§7.2.1), and the check that they work is the
failing-direction control (`--no-lattice`), not the cell count.

### 11.5 A truncating edit destroyed the prototype mid-session

While applying R26's dispositions, a scripted edit to `prune_proto.py` opened
the file for writing and then raised before writing anything, leaving it
zero bytes. The file was restored from the last commit and the intervening
work redone — about twenty minutes.

It is recorded for two reasons. First, the failure was silent in exactly the
shape this directory's CLAUDE.md warns about: an empty python file exits 0
and writes no output, so `diff3.py` saw a SUCCESSFUL prune step and then died
on a missing file, and a differently-written harness would have reported the
baseline arm twice and called it agreement. `diff3.py` now asserts the output
file exists after a zero exit, which is a real check the harness lacked.
Second, the lesson is the boring one: commit after each measured result, not
after each section. Every WIP commit in this lane's history is there because
of the watchdog; this is the first time one earned its keep as a backup.

---

## 12. Rulings requested

None are blocking; the recommendation stands without them.

1. **Adopt MRL pruning as [M4.6c]'s answer to K23?** The measured case is
   §0.2/§5; the residuals are §9; the cost is §6.
2. ~~**Does the clamp need a D46 forcing switch in v1?**~~ **WITHDRAWN**
   (R26 D1). D46 is unconditional and this note's own §8 already says so, so
   the question was re-asking Frank something ruled. The prune gets a stamp
   bit AND a `--fno-length-prune` forcing switch, on D46's terms.
3. **`--follow-min`, i.e. computing `minw` of the follow, in v1 or deferred?**
   It is the difference between 46 steps and 1 on `(…){10,50}b` (§7.3), it is
   the same AST walk, and it is strictly more analysis. Recommend v1: the
   walk that computes one computes the other.
4. **Is the width-0 correction owed to `known_issues.md` K23?** §2.4 narrows
   the entry's stated class. This lane did not edit the entry.
5. ~~**The scan-bound form, and the 5.24 ratio as a D49 calibration
   input.**~~ **WITHDRAWN** (R26 M2/E6). The ratio is a LANE PROXY on a
   lane-defined quantity, not D49's `RX_ERR_WORK`, and it is not a defensible
   calibration input; the manager's provisional adoption is correctly
   retracted. §4.6's design argument for the folded emission survives on its
   own terms — it lands on exactly one forward pass, measured and archived —
   and is a build-lane emission choice rather than a ruling.
6. **NEW, and it matters more than the two withdrawn items did: adopt the
   PREFILTER-WINDOW CEILING (§9.1) in v1?** Without it K23 RETURNS at a
   16-byte trailing suffix (measured curve); with it the residual is gone at
   every suffix length measured, one step throughout. The window is already
   computed and discarded on the default path, so the cost is carrying one
   `size_t` in `rx_work`. Recommend v1, with the three build-lane obligations
   §9.1 names and the subject-end ceiling as a strictly-weaker fallback.
   Panel-contributed (R26 E4), provenance recorded.

---

## 13. Predictions, for the panel to attack

1. Emitting the clamp at every program point with `minrest > 0` changes ZERO
   cells of the `.rxt` corpus. (§8; the pcrec-vs-pcrec differential is the
   test.)
2. **REFUTED by the shipped compiler** (R26 E7; kept and marked rather than
   deleted, per house style). The prediction was: *the `minw` walk written
   recursively overflows at the parser's 250-paren cap, exactly as
   `clo_visit` did.* It does not. `src/opt/possessify.c`'s `pss_walk`
   recurses on pattern structure today and `build/pcrec` compiles patterns at
   depths 100, 200 and 249 without trouble (MEASURED). The prediction
   generalised K18's finding one step too far: `clo_visit` overflowed because
   it recursed **Θ(d²)**, not because it recursed. §4.3's first bullet, which
   this prediction was the caution for, is corrected there.
3. **CONFIRMED, 21 steps** (written as a prediction, then measured — §2.5).
   On the frames rung, the test form of §4.1 reduces `((a|b){7,12}){7,20}` at
   n = 49 from 51,993 steps to fewer than 50.
4. There is no two-level bounded shape, of any inner width, stride or
   preference, for which pruning leaves more than `p` steps at the
   exact-minimum length with an empty follow. (§4.4; 1,059 cells consistent
   across strides 1–3 and all four preference combinations, no proof.)
6. **NEW.** The reverse-deterministic cursor rung (§4.5) will need its own
   lattice argument and will not get it from §4.1's division — its iteration
   boundaries are recovered by a backwards walk, not by arithmetic — and that
   is where the E1 class of bug recurs if anywhere.
5. Raising the step budget to any value that answers `(a{11,22}){11,50}`
   answers no more of the family than that: the next size up needs ~11× more.
   (§2.2, §5.5.)
