# [OPTLOOP.2] — READING THE BATCH-2 LEDGER (O-49) AGAINST THE D119 BAR

Lane `b2ledger`, 2026-09-23, branch `lane/b2ledger` from `3e58d700`.
Analysis + compile-side measurement only: nothing under `src/`, `cli/`,
`lib/` or `tests/`; nothing written in `/Users/fdicostanzo/pcrec-bench`
(read-only reference). **No clock was read on this box.** Every number
below is either the bench's Ryzen 1600 measurement, or a structural fact
read off emitted C, or an exact arithmetic count (subject bytes, find-all
call counts, `memchr` call counts, stamp values).

**The bench REPORTS and does not diagnose (D78 / I-57). This file is the
diagnosis.**

**Sources.** `pcrec-bench/docs/dev/outbox_to_pcrec.md` O-49; the ledger
`pcrec-bench/docs/dev/ledgers/2026-09-23-optloop2-batch2-after-b1885a83.md`
(698 lines); the ask `inbox_from_pcrec.md` I-95; the design records
`docs/design/reqbyte_freq_pick.md` and `docs/design/reqpos_2b.md`; the
admission fix's delivery `docs/dev/lanes/admitimpl_report.md` (read via
`git show lane/admitimpl:...`, branch head `cb437f26`, abi 31, NOT merged).
BEFORE = pcrec `8d716693` (abi 29), AFTER = pcrec `b1885a83` (abi 30).
Δ% convention throughout is the ledger's: **positive is SLOWER.**

Archived sources: `docs/dev/optloop/runs/2026-09-23-o49-b1885a83/`.
Reproduction instruments: `docs/dev/optloop/b2ledger/` (its own `CLAUDE.md`).

**The three compilers this lane built**, each by `git archive REV` into the
session scratchpad and `make -j2 CC=gcc-16` (`scripts/emit_sweep.py`'s own
`build_from_rev` method): `8d716693` (BEFORE), `b1885a83` (the measured
AFTER), `cb437f26` (the admission fix). Every artifact pair below was
emitted to the **same `-o` basename** in two directories — this house's
recorded `-o`-basename trap, whose sixth instance is still one lane away.

**The compiler this lane read is the compiler that was measured.**
`git diff b1885a83..main -- src/ cli/ lib/` is **empty**, so nothing in the
emitter has moved since the measured pin; `8d716693` and `b1885a83` are
both ancestors of `main`, and `cb437f26` is NOT (lane `admitimpl` is
parked, not merged), which is why the fix's side of every comparison below
had to be built from its branch rather than read off the tree.

---

## 0. THE INSTRUMENT, AND WHY ITS NUMBERS ARE THE BENCH'S OWN

### 0.1 The subjects

`bench/capability`'s `large-subject-throughput` regime has three subjects
(`t-64k` 65,536 B, `t-256k` 262,144 B, `t-1m` 1,048,576 B, **1,376,256 B
in total**) and a set-grain cell is the SUM over the three. All three were
regenerated here from `captext.text(n, seed)` and their **sha256 checked
against the committed `manifest_throughput.tsv`: 3 of 3 match.**

The regime is **FIND-ALL**, so `<prefix>_search` is called once per match
plus once to fail, and a per-call pre-check is paid once per call. The
floor rate, from cycle 1 §0 and reconfirmed by two independent cells in §4
below: **0.016794 ns/byte**, i.e. one `memchr`-class pass over the three
subjects is **23,113 ns**. Every "≈23,100 ns" in the ledger is that number.

### 0.2 The stamp instrument agrees with the bench's own census, by value

Before any of it is used: all 64 `capability` patterns were compiled at the
AFTER pin under the bench's three distinct build configs
(`auto-caps` = `--features all`; `auto-nocaps` adds `--no-captures`;
`vm-caps` and `vm-in-caps` SHARE one `--features all --engine=vm` build and
differ only in entry point — `testees/pcrec/configs.toml`), and the
`RX_REQ_BYTE`/`RX_REQ_RUN` values compared against the ledger's §3.3 census
row by row. **20 of 20 checked rows agree by value**, run text and scan
index included (`winpath-near-miss`'s `":\"@1` reads as a markdown-escaping
difference only). The ledger derived its census from the bench's own
`engine_metadata` compile rows; this lane derived it from `#define` lines in
emitted C. Two independent routes, one answer.

The byte-occurrence census agrees too, and the agreement locates a
convention rather than an error: the design notes' own counts (`/` 30,000,
`r` 54,781, `.` 14,826) are **`t-1m` only**, and this lane's `t-1m` counts
reproduce all three **exactly**. The set-grain counts used below are the
three-subject sums.

---

## 1. THE NULL CONTROL — 34 OF 34 NAMED NON-TARGET REGRESSIONS DID NOT CHANGE PROGRAM

This was not asked for, it re-reads everything that follows, and it is a
larger result this cycle than last, so it is first.

All 64 `capability` patterns were compiled at BOTH pins in all three build
configs and the artifacts compared line by line, ignoring only the
generated-by comment, the `.abi` integer and batch 2's own new
`RX_REQ_RUN` stamp line:

| outcome | artifact-configs |
|---|---|
| **program-identical across the pin** | **131** |
| changed | 56 |
| refused at both pins | 5 |

**43 of the 64 patterns are program-identical on all three configs.**

Joined against the ledger's own regression tables:

| ledger table | cells named | on a program-identical artifact |
|---|---|---|
| §2.1, the 20 largest non-named regressions (before ≥ 100 ns) | 20 | **20** |
| §2.2, the floor-conversion cells (before < 100 ns) | 14 | **14** |

**34 of 34.** Not a majority — all of them. The two the ledger singles out
for comment are both in it:

| cell | before (ns) | after (ns) | Δ% | program |
|---|---|---|---|---|
| `ipv4-near-miss` / srch / `vm-in-caps` | 1,021.419 | 1,135.363 | **+11.16%** | identical |
| `date-nested-plus` / thr / `vm-caps` | 52.214 | 73.670 | **+41.09%** | identical |

The ledger calls the second "the one genuine outlier here (+41.1%, a real
~21.5 ns move on an already-tiny baseline)". It is a real 21.5 ns move and
nothing in the artifact moved to cause it.

**What this measures.** The D119 bar's noise model is the cell's own
within-window IQR over 5 trials. It is applied across two windows eight
hours apart (03:19Z and 11:47Z). The IQR cannot see the between-window
component, and this pin pair's null population says that component reaches:

| cell scale | worst null cell | band |
|---|---|---|
| throughput, before-median ≥ 1 µs | `phone-palindrome-6` thr `vm-caps` | **+8.77%** |
| throughput, before-median < 100 ns | `date-nested-plus` thr `vm-caps` | **+41.09%** |
| short-subject-search | `ipv4-near-miss` srch `vm-in-caps` | **+11.16%** |

Cycle 1 measured +8.46% one-sided and O-48 later made it two-sided at
−5.74%..+8.46%. This cycle's own population is wider, and it is wider in
the way that matters: **at floor scale it reaches ±41%**, because a 21 ns
move on a 52 ns cell is 41% and 21 ns is what a cache line costs.

Every eight-record hygiene reading is clean (X13 `agree`, attempt 1,
worst gate-scope 7.01%). This is not a hygiene failure. It is the wrong
noise model, and the instrument that measures the right one was sitting in
the ledger's own records for free — for the second cycle running.

**Applied.** Ledger finding 5 says "82 of 360 non-named cells regress at or
above their before-IQR". Of the 34 it names, **zero** have a mechanism.
The reading below therefore scores every cell against its
**scale-matched null band** as well as its IQR, and says so each time.

---

## 2. THE D119 VERDICT, PER MECHANISM

D119 rule 4: *a mechanism lands only if its target cells' median improvement
exceeds their IQR AND no carve-out cell regresses by more than its IQR.*
The ledger computes the bar per CELL and I-95 states it per PATTERN; the
bar is owed per MECHANISM, so the 28 target rows are attributed to their
mechanism here using the design notes' own §6.1/§7.1 tables and §5's stamp
census.

**The two mechanisms are separable on this population and the ledger does
not separate them**, because I-95 named seven patterns without saying which
mechanism owns each. Read off the stamps: `nested-comment-rec`'s and
`wild-validator-email-owasp`'s movements are PICK moves (the run is absent
at both pins and contributes nothing), `wild-secrets-github-pat`'s is a pure
RUN addition (its byte 95 did not move), and `router-prefix-order`'s and
`logparse-atomic`'s are BOTH at once.

### 2.1 [OPT-FREQPICK] — the necessary byte by argmin over the frequency prior

| | rows | result |
|---|---|---|
| target (`reqbyte_freq_pick.md` §7.1: `nested-comment-rec` ×2 regimes) | 8 | **4/4 thr MEET at −99.75%**; srch not scored by I-95 |
| carve-out `router-prefix-order` thr | 4 | **4/4 MISS** — but §4.1 shows the cost is the RUN, not the pick |
| carve-out `dup-param-detect` ("THE ONE THAT COULD BREAK") | 8 | thr at the floor within noise, srch improves −24.7% to −26.5% — **holds** |
| carve-out `floor-byte` | 8 | unmoved (§5: its byte did not move) |
| un-named consequence `wild-validator-email-owasp` thr | 4 | **+27,010% to +52,757%** — §4.2 |

**VERDICT: THE TARGET MEETS SPECTACULARLY AND THE MECHANISM CARRIES ONE
UNPRICED HAZARD THE NOTE CLASSIFIED AS A GAIN.** The `nested-comment-rec`
collapse is the largest clean win in either cycle and the cost model
predicts its ABSOLUTE after-value, not just its direction (§4.4). Against
that, §4.2 is a 500× regression the note's own §7.1 lists among the effects
that "are gains".

### 2.2 [OPT-REQPOS] tier 2b — the necessary literal run

| | rows | result |
|---|---|---|
| targets (`reqpos_2b.md` §6.1: 4 patterns, thr) | `wild-secrets-github-pat` is the only one in I-95's named set | **2/4 MEET** (`vm-caps`/`vm-in-caps`, −97.6%/−97.9%); the DFA route's +3.3%/+3.8% is inside the null band |
| carve-out `logparse-atomic`/`-removed` (**the named falsifier**) | 8 + 8 | regresses — but §4.3 shows the cell cannot answer the question it was chosen for |
| carve-out `keyword-prefix-order` thr | 4 | **+59.6%/+59.7% DFA route, +8.0%/+8.3% VM** — far outside any null band. **The carve-out clause FAILS here, and this is the cell that should have been the falsifier** |
| carve-out `tag-depth3-bound`/`tag-pair-match` | 8 | unchanged work at both pins (§4.5) |
| carve-out `floor-byte` | 8 | byte-identical as designed |

**VERDICT: TARGETS MEET, CARVE-OUT CLAUSE FAILS.** Two carve-out cells
(`keyword-prefix-order` thr DFA route ×2) regress by 5-7× the scale-matched
null band, and `router-prefix-order` thr DFA route ×2 regress by 9× it. All
four are one mechanism, §4.1.

---

## 3. THE 17 MISSES, CLASSIFIED

I-95 named 7 `(pattern, regime)` cells; × 4 testees = 28 rows; 11 MEET
(improve beyond IQR), 17 MISS (13 regress, 4 read within-bar, and a target
that does not improve is a miss).

Classification per the brief: **(A)** EXPECTED-FIXED by
`[OPT-PRECHECK-ADMIT]` (lane `admitimpl`, `cb437f26`) — verified by
compiling the row's pattern under the ledger's exact config flags with BOTH
compilers and diffing the stamps and the emitted pre-check; **(B)** the
mechanism's OWN defect, which the admission fix does not reach; **(C)**
unattributed, with the measurement that would attribute it named.

| # | pattern | regime | testee | Δ% | `REQ_WHY` under the fix | pre-check under the fix | class |
|---|---|---|---|---|---|---|---|
| 1 | logparse-atomic | thr | auto-caps | +7.02 | `one-attempt` | **REMOVED** | **A** |
| 2 | logparse-atomic | thr | auto-nocaps | +7.13 | `one-attempt` | **REMOVED** | **A** |
| 3 | logparse-atomic | thr | vm-caps | +35.09 | `one-attempt` | **REMOVED** | **A** |
| 4 | logparse-atomic | thr | vm-in-caps | +41.82 | `one-attempt` | **REMOVED** | **A** |
| 5 | logparse-atomic | srch | vm-caps | +2.92 | `one-attempt` | **REMOVED** | **A** |
| 6 | logparse-atomic | srch | vm-in-caps | −0.10 (wb) | `one-attempt` | **REMOVED** | **A** |
| 7 | router-prefix-order | thr | auto-caps | **+80.83** | `emitted` | kept | **B** |
| 8 | router-prefix-order | thr | auto-nocaps | **+80.59** | `emitted` | kept | **B** |
| 9 | router-prefix-order | thr | vm-caps | +9.89 | `emitted` | kept | **B** |
| 10 | router-prefix-order | thr | vm-in-caps | +9.69 | `emitted` | kept | **B** |
| 11 | wild-secrets-github-pat | thr | auto-caps | +3.85 | `emitted` | kept | **B** |
| 12 | wild-secrets-github-pat | thr | auto-nocaps | +3.33 | `emitted` | kept | **B** |
| 13 | tag-depth3-bound | thr | vm-in-caps | −0.004 (wb) | `emitted` | kept | **C** |
| 14 | tag-pair-match | thr | auto-caps | +0.14 | `emitted` | kept | **C** |
| 15 | tag-pair-match | thr | auto-nocaps | +0.04 (wb) | `emitted` | kept | **C** |
| 16 | tag-pair-match | thr | vm-caps | +0.34 | `emitted` | kept | **C** |
| 17 | tag-pair-match | thr | vm-in-caps | −0.04 (wb) | `emitted` | kept | **C** |

**A = 6, B = 6, C = 5.**

**The A rows are verified by the emitted text, not by the stamp alone.**
`logparse-atomic` under the fix, diffed against the ledger pin's artifact:

```
> #define RX_REQ_WHY "one-attempt"
< #include <string.h>
<     if (subject_length <= search_from) return 0;
<     {
<         size_t rp_pos = search_from;
<         for (;;) {
<             const void *rp_q = memchr(subject + rp_pos, 58, subject_length - rp_pos);
<             ...
<             if (rp_c + 2 <= subject_length
<                 && !memcmp(subject + rp_c, ": ", 2)) break;
<             ...
```

The whole tier-2b scan loop AND `<string.h>` are gone, on all three configs,
because `RX_VM_START` reads `"anchored"` and G2 declines a pre-check that
precedes a one-attempt exit. The `REQ_BYTE`/`REQ_RUN` values are byte for
byte unchanged (the stamps name the ANALYSIS — `admitimpl_report.md` §0 F1),
which is what makes the decline readable rather than inferred.

**Scale-matched null band applied to the same 17 rows**, which is the second
reading every one of them needs:

| rows | band for their scale | outcome |
|---|---|---|
| 7, 8 (router thr DFA, 398 µs baseline) | +8.77% | **OUTSIDE, 9.2×** — real |
| 9, 10 (router thr VM, 4.05 ms baseline) | +8.77% | borderline, 1.13× |
| 1-4 (logparse thr, 41-70 ns baselines) | +41.09% | inside |
| 5, 6 (logparse srch, 836-951 ns) | +11.16% | inside |
| 11, 12 (github-pat thr, 124 µs) | +8.77% | inside |
| 13-17 (tag-*, 23 µs, ‖Δ‖ ≤ 0.34%) | +8.77% | inside, by 25× |

**Two of the seventeen are outside this pin pair's own null band. Both are
`router-prefix-order`'s DFA route, and both are class B.**

Row 4 deserves its own sentence. `logparse-atomic` thr `vm-in-caps` moves
49.179 → 69.745 ns, +41.82%. `date-nested-plus` thr `vm-caps` — a null cell
whose program did not change — moves 52.214 → 73.670 ns, +41.09%. Same
box, same testee class, same baseline to within 6%, same absolute move to
within a nanosecond, and one of them has no code change at all. **The
falsifier's largest regression is numerically indistinguishable from a null
cell of its own size.**

---

## 4. THE MOVEMENTS THAT ARE REAL, EACH WITH ITS COST MODEL

The model is exact, clock-free, and is the emitted loop's own semantics
walked over the bench's own subjects (`docs/dev/optloop/b2ledger/costmodel.py`).
The emitted tier-2b loop is, verbatim from the artifact:

```c
    rp_pos = search_from;
    for (;;) {
        rp_q = memchr(subject + rp_pos, SCAN, subject_length - rp_pos);
        if (!rp_q) return 0;
        rp_c = rp_q - subject;
        if (rp_c + L <= subject_length && !memcmp(subject + rp_c, RUN, L)) break;
        rp_pos = rp_c + 1;
    }
```

**It makes one `memchr` CALL per occurrence of the SCAN BYTE until the RUN
is found.** The batch-1 one-byte check made exactly one call per
invocation. That difference is the whole of §4.1 and §4.3's VM rows.

| pattern | matches | BEFORE calls | AFTER calls | amplification | BEFORE scan (B) | AFTER scan (B) |
|---|---|---|---|---|---|---|
| `router-prefix-order` | 312 | 315 | **39,098** | **124.1×** | 18,260 | 1,375,008 |
| `keyword-prefix-order` | 9,467 | 9,470 | **44,135** | **4.7×** | 328,216 | 1,376,256 |
| `wild-secrets-github-pat` | 0 | 3 | 7,864 | 2,621× | 617 | 1,376,256 |
| `logparse-atomic` | 0 | 3 | 3 | 1.0× | 43 | 303 |
| `wild-validator-email-owasp` | 0 | 3 | 3 | 1.0× | 218 | 1,376,256 |
| `tag-pair-match` | 0 | 3 | 3 | 1.0× | 1,376,256 | 1,376,256 |

### 4.1 `router-prefix-order` — the worst miss, and the run's call amplification

`/user|/users`. Byte moved 114 `r` → 47 `/`; run `"/user"@0` added.
Route `dfa` on both auto configs. Read off the ledger-pin artifact:

```
 line  18:  #define RX_DFA_PREFILTER "memchr"
 line  53:      rp_q = memchr(subject + rp_pos, 47, subject_length - rp_pos);   <- pre-check
 line  58:          && !memcmp(subject + rp_c, "/user", 5)) break;
 line 127:      const void *q = memchr(subject + scan_position, 47, ...);       <- prefilter
```

**Two `memchr` passes per call, on the SAME byte, in one function** — and
the pre-check's pass restarts at every one of them.

**The cost, counted exactly.** `/` occurs 39,095 times in the three
subjects and `/user` 312 times, so the pre-check makes **39,098 `memchr`
calls where batch 1 made 315** — a 124× amplification — and scans
1,375,008 bytes where batch 1 scanned 18,260. Predicted added cost:

```
   (39,098 − 315) calls × c_call  +  (1,375,008 − 18,260) B × 0.016794 ns/B
 = 38,783 × c_call + 22,786 ns
```

Measured: 398,422.8 → 720,485.6 ns, **+322,062.8 ns**. Solving,
**c_call = 7.72 ns** — squarely inside the 7-12 ns band cycle 1
independently established for a short `memchr` call on this box. **The
model reproduces the single worst miss in the ledger with one free
parameter taken from the previous cycle.**

**And the pick alone would have been an improvement.** Compiled at the
AFTER pin with `-fno-req-run`, the pre-check collapses to one
`memchr(subject + search_from, 47, …)`. Counted over the same subjects:

| pre-check form | `memchr` calls | bytes scanned | per call |
|---|---|---|---|
| batch 1, byte 114 `r` | 315 | 18,260 | 58.0 B |
| batch 2 pick only, byte 47 `/` (`-fno-req-run`) | **315** | **1,363** | **4.3 B** |
| batch 2 as shipped, run `/user` | **39,098** | **1,375,008** | 35.2 B |

Same call count as batch 1 and 13.4× less scanning — **the pick alone is
strictly cheaper than the check it replaced, on both axes**. So on this
pattern the PICK is an
improvement and the RUN is the entire +80.8%. The design note's own §7.2
scored this cell as "MOVES `r`→`/` (54,781→30,000): fewer candidate hits" —
correct about the hits, and the hits were never the cost.

**Why the admission fix does not reach it, and why that inverts the cost
ordering.** Compiled with the fix's compiler:

| build | `REQ_WHY` | pre-check | its cost on these subjects |
|---|---|---|---|
| `--features all` (as shipped) | `emitted` | **kept** | 39,098 `memchr` calls |
| `--features all -fno-req-run` | **`dominated`** | **removed** | 315 `memchr` calls |

G1 fires on the one-byte form by identity (`q == p == 47`) and is scoped by
`admitimpl_report.md` §0 F3 to the one-byte form only, on the sound ground
that a run check dismisses strictly more windows than a `memchr` on its scan
byte and is therefore not dominated by it. The consequence, stated plainly:
**on `router-prefix-order` the admission fix declines the form of the
pre-check that costs 315 calls and admits the form that costs 39,098.**
F3 anticipated the cell ("`router-prefix-order` keeps its pre-check under
this change") and named the trigger for widening as a run-rate analysis.
This is that trigger, with a population and a number: §6.

### 4.2 `wild-validator-email-owasp` — the floor jump, from below, and the sign was predicted backwards

O-49 item 4, the ledger's largest movement: throughput 43.7-85.3 ns →
23,118.8-23,200.5 ns on all four configs, **+27,010% to +52,757%**.

Stamps: byte moved **46 `.` → 64 `@`**, no run. Route `dfa` on both auto
configs, `RX_DFA_PREFILTER "none"`, `RX_VM_START "anchored"`. Occurrences
in the three subjects: `.` = 19,436, **`@` = 0**.

**The model.** The pattern is `^`-anchored, so find-all makes 3 calls.
BEFORE: `memchr(46)` finds a `.` 218 bytes in across all three calls, then
the anchored machine's one attempt fails in O(1) — ~44-85 ns for the cell.
AFTER: `memchr(64)` reads all **1,376,256 bytes** and returns NULL, which is
the correct answer, at one full pass. Predicted added cost
`(1,376,256 − 218) × 0.016794 = 23,109.6 ns`; measured added cost
**23,033.5 to 23,156.8 ns**. The prediction sits inside the measured range.
**This is cycle 1 §5's floor-from-below mechanism exactly, at a new
pattern, reached by a different route — there the pre-check was newly added,
here it was newly re-aimed.**

**The prediction had the sign backwards, and the reason is general.**
`reqbyte_freq_pick.md` §7.1 lists this cell among "two effects [that] are
gains and are NOT bar cells, because both rows already win":
"`wild-validator-email-owasp` throughput (`.`→`@`, 14,826→0)". Its counts
are exactly right — this lane reproduces 14,826 and 0 on `t-1m`. What is
wrong is the inference. **On an artifact that runs ONE attempt, an absent
required byte is the worst case and not the best**: the whole-window scan
replaces an exit that was already O(1). The note read "0 occurrences" as
"the whole call answers in one pass", which is true, and the call it
answers in one pass previously answered in twenty nanoseconds.

The same note's §7.2 states the hazard one-directionally — "the rule can
move a pick from a byte that is ABSENT to one that is PRESENT" — and makes
the acceptance measurement "**no cell's picked byte goes from absent to
present**". This cell passes that check and regresses 500×. The check is
sound and its converse is missing:

> **A pick move is a hazard in BOTH directions, and which direction is
> which depends on the artifact, not on the byte.** On an artifact whose
> attempt loop is real, absent is best. On a one-attempt artifact, absent
> is worst, because the pre-check's own pass is then the entire cost of the
> call. The admitting predicate, not the picking predicate, is what tells
> the two apart.

**Class: (A).** The fix reads `REQ_WHY "one-attempt"` on all three configs
and emits no `memchr` at all, so the cell returns to its ~44-85 ns shape.
That is the cleanest single confirmation in this reading that
`[OPT-PRECHECK-ADMIT]` is aimed at the right defect: the floor jump O-49
flags as its largest movement is removed by a predicate designed before it
was measured, for a reason stated before it happened.

### 4.3 `logparse-atomic` — the falsifier that cannot answer its own question

I-95 named this cell FIRST, as "the no-decline-rule falsifier: its run gain
was 1.00× in the census while its pick moves from SPACE to COLON", and
`reqpos_2b.md` §6.2 makes it explicit: *"THE CELLS THIS MECHANISM CAN HURT.
Gain 1.00×… If either regresses beyond its IQR, §4.3's no-decline-rule
recommendation is refuted."* It regressed on all four throughput configs.
**The trigger fired and the cell cannot discharge it**, for two independent
reasons.

**First, the run really is 1.00× and the model says it costs ~4 ns.**
Byte 58 `:` occurs 11,812 times; the run `": "` occurs 11,812 times — every
colon in the corpus is followed by a space, so the run's selectivity is
exactly 1.000, as the census said. But the loop BREAKS at the first success,
so it runs **one iteration**, not 11,812: the call count is unchanged at 3,
and the scan grows by 260 bytes. Predicted added cost **+4.4 ns**; measured
on the DFA route **+2.9 ns** (41.518 → 44.433) and **+2.9 ns** (40.344 →
43.222). The model predicts the DFA rows to within 1.5 ns. `reqpos_2b.md`
§4.3 reason 1 priced this at "9,070 two-byte compares per MiB"; the emitted
loop performs **one**, because a decline rule's cost is paid only until the
run is found.

**Second, and decisively: the artifact is anchored, so the fix deletes the
whole construct.** `RX_VM_START "anchored"` on all three configs; under
`cb437f26` the pre-check — byte check, run loop and `<string.h>` — is gone
and `REQ_WHY` reads `one-attempt`. A run-rate decline rule would be
choosing whether to emit a loop that the admission predicate does not emit
at all. **The cell chosen to falsify the no-decline-rule is confounded by
the admission defect, and after the fix it has no run check to have a rate
about.**

The VM rows' +35.1%/+41.8% (15.3 ns and 20.6 ns on 43.6 and 49.2 ns cells)
are 3-5× larger than the 4.4 ns the work accounting predicts. That residual
is inside the floor-scale null band (§3, row 4) and is not separately
attributed here. `logparse-atomic-removed` is the same pattern without the
atomic group, carries the same stamps, is likewise `one-attempt`, and
regresses on 6 of 8 carve-out cells for the same reason.

**The falsifier's real home is `keyword-prefix-order`**, which I-95 did not
name and `reqpos_2b.md` §6.2 lists under "do not regress" with its own
reasoning ("gain 4.2×: a real but modest win, and the row where a small gain
must still exceed the added compare's cost"). Measured here: byte 110 `n`
occurs 44,132 times, run `"in"` 9,467 — **gain 4.66×**, close to the
predicted 4.2× — and the run loop makes **44,135 `memchr` calls where batch
1 made 9,470**, a 4.7× amplification over 9,467 find-all calls. It regresses
**+59.6%/+59.7%** on the DFA route, the largest carve-out regression in the
ledger, far outside any null band, and its `REQ_WHY` under the fix reads
`emitted` — the admission fix does not reach it either. **Class (B).**
Its mechanism is §4.1's, and the two together are the run mechanism's whole
measured cost on this set.

### 4.4 The clean meets, confirmed by predicting their ABSOLUTE after-values

Two of the meets are not merely large; the cost model predicts where they
land, which is what separates a mechanism from a coincidence.

| cell | before (ns) | after, measured | after, predicted | mechanism |
|---|---|---|---|---|
| `nested-comment-rec` thr ×4 | 9,275,952 - 9,746,259 | 23,118 - 23,152 | **23,113** (one full pass) | pick `/` (39,095 hits) → `*` (0) |
| `wild-secrets-github-pat` thr `vm-caps`/`vm-in-caps` | 5,387,513 / 5,857,018 | 129,145 / 125,586 | **~125,300** (7,864 calls + one pass) | run `hub_pat_` absent |

`nested-comment-rec` lands on the floor to within 0.2%, because an absent
byte makes the whole find-all call one `memchr` pass and the VM never runs.
`wild-secrets-github-pat`'s forced-VM route lands within 3% of
`7,861 × 13 ns + 23,113 ns`. Both are exactly what
`reqbyte_freq_pick.md` §7.1 and `reqpos_2b.md` §6.1 predicted, by name and
by mechanism, before the measurement.

**One correction to I-95's prose.** It calls `nested-comment-rec` "the
pick's one losing cell". The design note names its two cells as **THE
TARGET CELLS** (§7.1, rank 9 and rank 20, "the largest gain this note can
claim"), and the phrase "losing cell" appears nowhere in either design note.
O-49 item 1 observes the sign was backwards; the sign was backwards in the
ask, not in the design.

`wild-secrets-github-pat`'s two DFA-route misses (+3.8%/+3.3%) are a
different shape and worth one line, because the cost model appears to fail
on them by 17× until the shape is read. There the run is ABSENT, so the
pre-check **returns 0 and the prefilter and VM below it never run** — the
pre-check REPLACES a pass of almost exactly its own cost (the
`offset-set-bounded` prefilter scans the same byte 95 over the same
subject) rather than adding one. The measured +4.8 µs on a 124.6 µs cell is
the difference between two nearly identical passes, not the price of a new
one. **A whole-window pre-check's cost is additive only where it passes
through**; where it answers the call, it is a substitution and the model
must compare two passes, not add one.

### 4.5 `tag-depth3-bound` / `tag-pair-match` — one non-event, scored twice with opposite signs

Both stamp the identical `REQ_BYTE 60` and `REQ_RUN "</"@0`. Byte 60 `<` and
the batch-1 byte 62 `>` **both occur ZERO times** in the three subjects (the
capability throughput grammar is log + http + source + prose and contains no
angle brackets). So at BOTH pins these artifacts do the same thing: one full
`memchr` pass, no match, return 0 — which is why all eight cells sit at
23,093-23,195 ns, the floor, on both sides. The run's `memcmp` never
executes, because its scan byte is never found.

Their measured movements are −0.29% to +0.34%. The ledger scores
`tag-depth3-bound` as 3 MEETS and `tag-pair-match` as 2 MISSES and notes
that "the two 'identical run' patterns diverge on their D119 verdict". They
do not diverge on anything: **it is one non-event read twice, and the sign
is noise at 25× below the scale-matched null band.** Class (C) for all five
rows, and what would attribute them is the null band the ledger already
has the records to compute (§7, ask I-104).

`reqpos_2b.md` §6.2 classifies both patterns as **carve-outs** ("batch 1's
five improve cells… the run form must not make them slower"), not targets,
and predicts no improvement: "both bytes of `</` are ABSENT from `t-1m`, so
their whole-call answer is already won at `L = 1`". I-95 promoted them to
named TARGETS. **A cell already at the floor cannot improve**, so five of
the seventeen misses are rows the design never claimed and could not have
won. Scored against the design's own classification, the target population
is 5 cells and 20 rows, of which 8 meet and 12 miss.

---

## 5. THE CENSUS RECONCILIATION

O-49 item 5 reports 14 of 62 compiled patterns stamping a run, 14 moving
`req_byte`, union 18 (4 run-only / 4 pick-only / 10 both), engine routes
unchanged on all 62, and all three named expectations exact by value. This
lane derived the same census from emitted `#define` lines rather than from
the bench's `engine_metadata`, and **reproduces it** — 20 of 20 spot-checked
rows agree by value (§0.2), including the three named expectations
(`hub_pat_`@3 with scan byte 95; `REQ_BYTE 58` for `logparse-atomic`;
`114 → 47` with run `/user`@0 for `router-prefix-order`). That is now
**three independent derivations in agreement** — the bench's, the re-pin
lane's item 7, and this one.

The engine-route claim is confirmed structurally as well as by value: the
`RX_ENGINE` stamp is unchanged at both pins on every pattern in the
program-identity census, and every one of the 56 changed artifact-configs
changes only within the pre-check region.

**The census this reading adds is the one the ledger could not compute**,
because it needs the unmerged fix's compiler — `REQ_WHY` over all 64
patterns × 3 configs at `cb437f26`:

| `REQ_WHY` | artifact-configs | patterns | meaning |
|---|---|---|---|
| `none` | 79 | 27 | no necessary byte was derived |
| `emitted` | 67 | 27 | pre-check kept |
| `one-attempt` | 27 | **9** | **G2 declines** — pre-check removed |
| `dominated` | 14 | 7 | **G1 declines** — pre-check removed |

The nine `one-attempt` patterns are `email-nested-plus`, `ipv4-near-miss`,
`logparse-atomic`, `logparse-atomic-removed`, `uuid-near-miss`,
`wild-datetime-moment-iso8601`, `wild-validator-email-owasp`,
`wild-validator-ipv4-owasp`, `winpath-near-miss` — **exactly the nine
patterns and 27 artifact-configs `cycle1_ledger_reading.md` §6 G2 predicted
by name**, reproduced here against a compiler built from the fix rather than
from the prediction. A rule stated from one cycle's evidence and measured
unchanged against the next cycle's population is the strongest form the
loop has produced.

---

## 6. WHAT THE FIX REACHES, AND THE ONE PLACE ITS SCOPING INVERTS THE COST

`[OPT-PRECHECK-ADMIT]` as parked at `cb437f26` reaches, on this population:

- **all 6 class-A misses** (`logparse-atomic`, both regimes, all configs) —
  removed, verified in the emitted text;
- **O-49's largest movement** (`wild-validator-email-owasp`'s +27,010% to
  +52,757% floor jump) — removed, §4.2;
- **the two batch-1 regressions still live in this ledger's carve-out
  population** (`winpath-near-miss` srch on all four testees, +4.9% to
  +10.3%; `ipv4`/`uuid` DFA route) — removed;
- **7 more patterns by G1 dominance**, including
  `wild-codegrammar-json-array-begin`, the duplicated-pass witness cycle 1
  §4.3 named.

It does **not** reach the two cells that are outside this pin pair's own
null band, and does not reach `keyword-prefix-order`. All three are the same
mechanism and the same predicate:

> **G1's one-byte scoping declines the cheap form of a pre-check and admits
> the expensive one.** Measured on `router-prefix-order`: the one-byte form
> G1 removes costs **315** `memchr` calls over these subjects; the run form
> G1 keeps costs **39,098**. On `keyword-prefix-order` the same comparison
> is 9,470 against 44,135.

F3's reasoning for the scoping is sound and is not challenged here: a run
check dismisses strictly more windows than a `memchr` on its scan byte, so
it is not DOMINATED by one, and D77 forbids widening a rule past its
measurement. What has changed is that the measurement now exists. The
right form of the widened rule is not "treat a run like a byte" — it is the
run-rate comparison `reqpos_2b.md` §4.3 item 2 already names as tier 2b's
own missing instrument, evaluated against the prefilter:

> **Candidate rule (NOT built here — D77).** Where the artifact already
> emits a candidate-start `memchr` for byte `p` and the pre-check's run has
> scan byte `q`, the pre-check's `memchr` CALL COUNT is the occurrence count
> of `q`, not of the run. Admit the run check only where that count is
> strictly lower than the prefilter's own. On this population the rule
> declines `router-prefix-order` (both scan byte 47, identical counts) and
> `keyword-prefix-order` (scan byte 110 against an `offset-set` prefilter on
> the same byte), and leaves every meeting target untouched — the four
> `nested-comment-rec` rows and both `wild-secrets-github-pat` VM rows carry
> `RX_*_PREFILTER "none"` and have no prefilter to be dominated by.
> **The statistic it needs is not a corpus rate; it is a comparison between
> two counts the compiler already has.** The measurement that would trigger
> building it is I-103 (§7).

Two further notes for whoever takes that row:

1. **The run loop's cost is O(occurrences of the scan byte), and the design
   note prices it as O(occurrences of the run).** `reqpos_2b.md` §4.3
   reason 1 — "the added cost is one constant-length `memcmp` per occurrence
   of the RAREST member under the prior" — is right about the `memcmp` and
   silent about the `memchr` restart that precedes each one. On
   `router-prefix-order` the `memcmp`s are 39,095 cheap inlined compares and
   the restarts are 38,783 library calls at 7.72 ns each; the calls are
   **97% of the measured regression**. A per-occurrence cost model must
   price the loop's re-entry, not only its comparison.
2. **`REQ_BYTE` reports the run's scan member**, so a reader looking for
   "which byte does this artifact `memchr` for" gets the right answer and a
   reader looking for "how many times will it call `memchr`" gets no signal
   at all. The count is derivable from the byte and the subject, which the
   compiler does not have — but the artifact could state its own scan byte's
   relationship to the prefilter's, which is what the candidate rule needs.

---

## 7. RECOMMENDED DISPOSITIONS

| mechanism | recommendation | the number that decides it |
|---|---|---|
| **[OPT-FREQPICK]** | **DEFAULT-ON, and it is a precondition on [OPT-PRECHECK-ADMIT] merging** | Its target collapses 9.3 ms → 23.1 µs on 4 of 4 configs, predicted to 0.2% of its absolute value. Its one severe hazard (§4.2, +27,010%) is on a one-attempt artifact and is removed by the admission fix, which is already built. Shipping the pick without the fix ships that hazard. |
| **[OPT-REQPOS] tier 2b** | **DEFAULT-ON WITH THE ADMISSION FIX, and open a row for the run-form dominance rule** | Targets meet (−97.6%/−97.9% where the run is absent). Against that, the two cells outside this pin pair's own null band and the largest carve-out regression (+59.7%) are all one predicate away, and the fix as scoped does not reach any of them. |
| **the no-decline-rule question** (`reqpos_2b.md` §4.3) | **NOT ANSWERED by this ledger; do not treat the trigger as fired** | The named falsifier is anchored and loses its whole pre-check under the fix (§4.3). `keyword-prefix-order` is the cell that can answer it, and what it shows is not a run-RATE problem but a run-vs-prefilter DOMINANCE problem. |

A `--tune` position remains the wrong instrument for both mechanisms, for
cycle 1's reason: the losses are not a size/speed trade but an admission
defect with a named predicate. **Size**: `reqpos_2b.md` §6.3 predicted "a
loop of roughly ten emitted lines plus a string literal of L bytes" per
run-carrying artifact and one stamp line everywhere; the fix REMOVES that
text from 41 of 192 artifact-configs on this set. No `--tune` consequence.

**The one thing this reading does not settle.** Rows 9 and 10
(`router-prefix-order` thr, forced VM, +9.89%/+9.69%) sit 1.13× outside the
µs-scale null band — real if the band is right, noise if it is 10% wider.
They are the only rows in the table whose verdict a better null control
would change, and I-104 asks for it.

---

## 8. OWED LINUX MEASUREMENTS — ready to append to the bench inbox

Highest inbox item at this writing is I-101, so these are I-102..I-104.

```
## I-102 (2026-09-23, [OPTLOOP.2] ledger reading) — THE ADMISSION FIX'S
   ACCEPTANCE CELLS, extended by what batch 2 adds

Pin: pcrec lane/admitimpl cb437f26 (abi 31) against b1885a83 (abi 30) as
BEFORE. capability@0.1, four pcrec testees, both regimes, D119 bar per cell.
The fix removes the whole-window pre-check from 41 of 192 artifact-configs
(27 one-attempt + 14 dominated); every cell below is one where the emitted
text provably changes, verified on darwin by stamp and by diff.

  BATCH-1 CELLS (carried from the pre-drafted I-102):
    (a) winpath-near-miss thr, email-nested-plus thr: EXPECT a return to
        ~20 ns and ~47 ns from the ~23,100 ns floor (the pre-check is
        removed; REQ_WHY reads one-attempt).
    (b) wild-codegrammar-json-array-begin thr, all four testees: EXPECT the
        duplicated memchr gone (REQ_WHY "dominated"), one pass not two.
    (c) uuid-near-miss / ipv4-near-miss, thr + srch, DFA route: EXPECT the
        batch-1 +18.7%..+38.5% recovered.
    (d) the 29 regressing cells cycle1_ledger_reading.md §6 G2 named, and
        the 4 G1 cells: EXPECT improvement or flat, none regressing.

  BATCH-2 CELLS ADDED BY THIS READING:
    (e) wild-validator-email-owasp thr, ALL FOUR testees — O-49's largest
        movement. EXPECT a return from 23,118-23,200 ns to 43-85 ns, i.e.
        the +27,010%..+52,757% fully recovered. This is the single most
        discriminating cell in the ask: it is a 500x move with a one-line
        structural cause and a predicate built before it was measured.
    (f) logparse-atomic thr + srch and logparse-atomic-removed, all configs
        — EXPECT all of batch 2's +7.0%..+41.8% recovered AND the cell to
        land BELOW the 8d716693 BEFORE as well, since batch 1's own byte-58
        check goes with it. A cell that recovers to the BEFORE and no
        further would mean the pre-check was not what cost it.
    (g) CONTROLS that must NOT move: nested-comment-rec thr x4 and
        wild-secrets-github-pat thr vm-caps/vm-in-caps — the six meeting
        target rows. All six carry RX_*_PREFILTER "none" and read
        REQ_WHY "emitted" under the fix, so their artifacts are unchanged
        but for the abi digit and the new stamp line. Any movement here is
        a null-band reading, not a mechanism.
    (h) router-prefix-order thr and keyword-prefix-order thr: EXPECT NO
        CHANGE (REQ_WHY "emitted"; the fix does not reach them). Named so
        the ledger records them as a negative control rather than as an
        unexplained non-recovery.

## I-103 (2026-09-23, [OPTLOOP.2] ledger reading §6) — the ONE measurement
   that decides whether G1 should cover tier 2b's RUN check

This is admitimpl_report.md §9's open design question, and it needs one
timing block, not a corpus statistic.

  Patterns: router-prefix-order (auto, --no-captures) and
  keyword-prefix-order (auto, --no-captures). Subjects: the capability
  throughput set. Regime: find-all throughput, 5 trials, interleaved.
  At pin b1885a83 build THREE artifacts of each:
    (a) default                       -- pre-check = run loop
    (b) -fno-req-run                  -- pre-check = one memchr on the
                                         SAME byte the prefilter scans
    (c) -fno-req-byte                 -- no pre-check at all
  EXPECT, from this reading's exact call counts (b2ledger/costmodel.py):
    router:  (a) 39,098 memchr calls, (b) 315, (c) 0
             so (a) - (c) ~ +322,000 ns and (b) - (c) ~ 0
    keyword: (a) 44,135, (b) 9,470, (c) 9,467 in the prefilter alone
  If (b) is within IQR of (c) on both patterns, the run form is the whole
  cost and the widened rule is worth building; if (b) is materially worse
  than (c), the one-byte form costs something too and G1's existing
  dominance rule is under-measured rather than the run form over-admitted.
  NO new pcrec build is needed -- both axes already ship.

## I-104 (2026-09-23, [OPTLOOP.2] ledger reading §1) — CARRY A NULL-CONTROL
   BAND IN THE CAPABILITY REPORT (re-ask of I-91 block B, now with a
   population this side can hand you)

I-91 block B asked for this and O-48 answered it for ONE pin pair. This
reading finds the same result again, larger: 131 of 192 capability
artifact-configs are PROGRAM-IDENTICAL across 8d716693 -> b1885a83, and
34 of the 34 non-target regressing cells the ledger NAMES sit on them,
up to +11.16% (search) and +41.09% (throughput, sub-100 ns baselines).

  ASK: compute, per report, the Δ% distribution over the cells whose
  artifact did not change between the two pins, and print it as a
  NULL-CONTROL BAND beside the IQR -- banded by regime and by baseline
  scale (>= 1 us / 100 ns - 1 us / < 100 ns), since this cycle's band is
  5x wider at floor scale than at microsecond scale. Then state D119's
  bar as |D| > max(IQR, null band).
  WE CAN HAND YOU THE POPULATION: docs/dev/optloop/b2ledger/nullctl.json
  is the per-(pattern, config) identity verdict for this pin pair, derived
  by compiling both pins on darwin; docs/dev/optloop/b2ledger/nullctl.py
  regenerates it for any pin pair in about four minutes. If it is easier
  for you to read the artifact hashes your own build step already has,
  that is the same census and we would rather you computed it than
  trusted ours.
  WHY IT MATTERS THIS CYCLE: without it, this ledger reads "17 of 28
  target rows miss"; with it, 2 of the 17 are outside the band and 5 more
  are cells the design note classifies as carve-outs rather than targets.
```

---

## 9. EXEC SUMMARY ADDENDUM

**Findings.** Batch 2's two mechanisms both land on their own targets and
both carry one real defect apiece, and neither defect is what O-49's
headline names. `[OPT-FREQPICK]`'s target collapses 9.3 ms to 23.1 us on
4 of 4 configs, predicted to 0.2% of its absolute value; tier 2b's forced-VM
targets collapse 5.4 ms to 129 us. Of the 17 missing target rows,
**6 are removed outright by the already-built admission fix,
6 are the run mechanism's own defect, and 5 were at the floor before the
batch started and could not have improved.** Only **2 of 17** lie outside
this pin pair's own null band, both `router-prefix-order`'s DFA route.

**Surprises.** Three, each a prediction whose sign or scope was wrong before
any measurement. (1) The ledger's largest movement, a 500x floor jump on
`wild-validator-email-owasp`, is a cell the design note lists among effects
that "are gains" -- it read an absent required byte as a one-pass answer
without asking whether the artifact had an attempt loop to skip, and on a
one-attempt artifact absent is worst. (2) The named no-decline-rule
falsifier, `logparse-atomic`, is anchored, so the fix
deletes its entire pre-check: **the cell chosen to answer the run-rate
question has no run check left to have a rate about**, and the cell that
can answer it (`keyword-prefix-order`, +59.7%) was never named. (3) The
fix's dominance rule, scoped to the one-byte form on sound reasoning,
**declines the form of `router-prefix-order`'s pre-check costing 315 memchr
calls and admits the form costing 39,098.**

**Impact.** The run scan loop costs one `memchr` CALL per occurrence of its
SCAN BYTE, not of the run, which the design note prices the other way; on
`router-prefix-order` that is a 124x call amplification and 97% of a +80.8%
regression, reproduced by an exact clock-free model with one parameter
carried from cycle 1. Separately, cycle 1's free null control is larger this
cycle: 131 of 192 artifacts program-identical, **34 of 34 named non-target
regressions sitting on them**, one at +41.09%. For the second cycle running
the within-window IQR is the wrong noise model for a two-window comparison,
and the records to fix it are already in the bench's own store.

**Next steps.** Merge `[OPT-PRECHECK-ADMIT]` -- a precondition on shipping
the pick, not an improvement on it. Open a cycle-3 row for the run-form
dominance rule, whose statistic compares two counts the compiler already
holds. Send I-102 (acceptance cells, the six meeting targets as controls),
I-103 (the run-form timing block), I-104 (carry a null-control band).
