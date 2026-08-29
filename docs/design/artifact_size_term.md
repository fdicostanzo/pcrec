# [ART-SIZE] STEP 2 — ARTIFACT SIZE AS A SELECTION TERM, and the emitted-size cap

Lane `artsize3`, 2026-08-28. Written BEFORE the emitter, on
`docs/design/offset_k_skip.md`'s model: the derivation, the cost model and the
emitted form are fixed here with measurements, and the code is then written
against this document. The plan row `- [ART-SIZE]` in `docs/dev/plan.md` is the
charter; STEP 1's census (`docs/dev/artifact_size_census.md`) is the measured
input, and this note's own measurements are in `artsize_impl/` beside it.

Frank's concern, verbatim, is the reason the row exists: *"I'm concerned about
the 2 MB VM artifact. If our compiled artifacts are that big no one will want
to use them. It deserves an investigation as well as a size vs performance
tension that kicks in at some size."*

---

## 0. The answer in ten lines

1. Emitted size is predicted, to a median **2.4 %** relative error over the
   2,487 corpus artifacts that compile, by **two** pre-emission facts the
   compiler already computes: the expanded VM **node count** `N` and the
   declared **table entry count** `E` (§2).
2. Those two terms are not interchangeable, and that is the row's central
   finding. **`N` and `E` cost gcc completely different amounts.** The 2 MB
   witness is 96 % program (by comment-excluded bytes) and costs gcc
   **55.13 s**; `a{1,31000}` is a 1.38 MB artifact that is 92 % tables and
   costs gcc **0.34 s** — a **162× cost difference for a 1.5× size
   difference** (§4.1, measured this lane). A byte cap set to refuse the
   witness would refuse `a{1,31000}` too, and gcc compiles that one in a
   third of a second.
3. So there is **no single size cap**. The size term is two mechanisms over
   one model: a **K selection** that acts on `N`, and a **node cap** that
   refuses on `N`. Tables are priced by the model, reported by the stamps, and
   are **not** what either mechanism binds on (§4).
4. The **K rule**: when the model predicts the artifact is above a threshold,
   the counter rung's unroll factor `K` is chosen by EVALUATING the model over
   a descending ladder, not by descending greedily — because the size-vs-K
   curve is **NON-MONOTONE** (measured, §3.1: the N=8 nested outlier is
   195,443 B at K=3 and 163,386 B at K=4). `--unroll=K` remains an explicit
   override that the term never overrides.
5. The rule is a **general mechanism, not a nesting special case**: nesting
   enters only through `N(K)`, which the existing `vm_count_slots` pre-pass
   already computes. Measured, it reproduces the census's own hand-derived
   split with no `nested`-only clause — it SELECTS on all three nested-repeat
   outliers (K=1, 2.7×–4.7× smaller) and DECLINES all four table-dominated
   ones (K buys 1–8 %), §3.3.
6. The **threshold** is 131,072 comment-excluded bytes: it sits in the
   corpus's own widest tail gap (1.64×, between 98,596 B and 162,034 B), with
   the nearest pattern 33 % below and 24 % above, and leaves the term a
   measured no-op on **2,480 of 2,487** corpus patterns (99.72 %), §3.2.
7. The **cap** is `PCREC_MAX_VM_EMIT_NODES = 2000`, on the node count AFTER K
   selection, refusing with a `"pattern too large: ..."` diagnostic in the
   family `emit_vm.c` already uses. Derived from D45's 10 s budget against the
   measured `gcc_cpu ≈ 0.00054 · N^1.269` curve (§4.2), it refuses the witness
   at K=8 (7,467 nodes, 55.13 s) and refuses **0 of 2,487** corpus patterns.
   The K rule runs first and takes the witness to 313 nodes, so the cap never
   actually fires on it — that ordering is the design (§4.3).
8. **The three levers of census §7 are priced and all three are DECLINED**
   (§5), on measurements, with named triggers to revisit. The largest of them
   (the node-skeleton fold) is worth a corpus median of **0.99 %**.
9. **Identity**: `K` is the counter rung's chunking factor and not a semantic
   choice, so every `K` is answer-identical — but that claim is **NOT covered
   by any gate today** (`make test-axes` derives its axis list from
   `PCREC_(NO|FORCE)_* = 1u << N` and `--unroll` is a value axis, not a bit),
   which is a gap this row found by checking and must close (§6).
10. It is an `abi` bump (9 → 10, four sites), a new deny flag at **bit 17**
    (bit 16 is [OPT-K]'s), and two new unconditional stamps (§7, §8).

---

## 1. The measured need

Three separate obligations converge on this row, and only one of them is
Frank's opening concern.

**(a) D45's consequence 1 is an open assignment.** `docs/dev/decisions.md`
D45, ruled after `((a)|b){0,4000}c` pegged cc1 for 100+ minutes, attaches two
consequences and names them as different obligations:

> The cap must ALSO bound total replicated output size — assigned with the
> bigbounded follow-up; the compile-time bound is the harness-side guard, the
> **size bound is the compiler-side one**, and they are different obligations.

The harness-side guard shipped (`tests/lib/gen_timeout.sh`). The compiler-side
size bound is this row. It has been open since 2026-08-15.

**(b) The census found the existing caps structurally cannot do it.**
`artifact_size_census.md` §6 asked which of `PCREC_MAX_VM_REPEAT_COPIES` (64)
or `PCREC_MAX_VM_REPLICATION_PRODUCT` (131,072) should have refused the
witness, and measured that neither comes close: the witness's worst single
quantifier factor is 30 (47 % of the first cap) and its realized node count is
7,467 (5.7 % of the second). Both caps are calibrated against *runaway*
blowup; the witness is cap-compliant by a wide margin and still 2 MB.

**(c) The corpus is fine, and that is itself the design input.** Over 2,487
compiled artifacts the shipped `.o` is small (census §3: median 6,760 B, p99
14,364 B) and gcc's worst case is 6.995 s — 70 % of D45's budget, on one
deliberate stress pattern. Nothing in the corpus is refused today and nothing
should be. **Every mechanism in this note must therefore be a measured no-op
on essentially the whole corpus**, which is what §3.2's threshold and §7.3's
zero-cost obligation are for.

---

## 2. The size model

### 2.1 What it predicts, and in what units

The model predicts **comment-excluded emitted bytes** — total source bytes
minus `[M6-READ]` prose — which is:

- the quantity `tests/lib/size_count.sh` already defines and
  `docs/dev/artifact_size_log.tsv` already logs for every corpus pattern, so
  the model is fitted and validated against a population the project already
  maintains;
- the quantity the census recommends. Census §5 measured prose at 42.1 % of
  aggregate source bytes but r = 0.43 against `.o`, versus r = 0.99 for
  program+tables: *"a size term that wants the number a user ships should
  price program+tables, not source bytes."*

**Provenance, and the control on it.** This lane's measurement
(`artsize_impl/probes/measure.py`) reimplements `size_count.sh`'s three-state
comment tracker in python. That is a control sharing a definition with what it
controls, so it was **verified rather than assumed**: on six artifacts
(`a(b|c)+d`, `(ab){300}`, `\d{4}-\d{2}-\d{2}`, `((a)|ab){0,12}c`,
`foo|bar|baz`, `[a-z]+@[a-z]+\.com`) the python and the shipped shell
implementation agree to the byte — 25,855 / 57,793 / 17,353 / 40,788 /
17,068 / 17,296. The first run disagreed by exactly 1 on all six (a phantom
final record from `str.split`, which `awk` does not emit); that is recorded
here rather than silently fixed, because an unverified reimplementation
agreeing to within 1 byte would have looked like agreement.

### 2.2 The inputs are pre-emission facts, deliberately

| input | what it is | who already computes it |
|---|---|---|
| `N` | the expanded VM node count — one emitted node per `rx_LN:` label | `vm_count_slots`, in the pre-pass that walks the copy tree **before a byte is emitted** (`emit_vm.c`; limits.h's `PCREC_MAX_VM_REPLICATION_PRODUCT` comment states this ordering explicitly) |
| `E` | the total declared entry count over every emitted `static const` table (`states × ncls`, forward and reverse) | the DFA builder, which already bounds it at `PCREC_MAX_TABLE_ENTRIES = 2,000,000` |

Both are available **as a function of K** before emission, which is what makes
a selection over K possible at all.

**Why `E` is the declared entry count and not the emitted table bytes.** Table
*bytes* are what the emitter produces; using them as a model input would make
the model circular (it would "predict" a number by reading it). The declared
entry count is the pre-emission quantity, and the model's job is to convert it
to bytes. This lane's measurement extracts `E` from each artifact's array
declarations and was checked against a hand count on `((a)|ab){0,500}c`:
`256 + 8 + 8 + 256 + 4008 + 4008 = 8,544`, matching exactly.

### 2.3 The fit

Least squares over the 2,487 corpus patterns that compile
(`artsize_impl/corpus_sizes.tsv`; 2,771 distinct `^pattern ` lines under
`tests/`, 284 refused — all of them the corpus's own ordinary `perr` negative
material, none size-related, matching the census's own 284):

```
    B̂  =  S(engine)  +  173.53 · N  +  5.064 · E
    S(vm) = 20,831 B        S(dfa) = 12,374 B
```

Two intercepts (the fixed scaffolding differs per engine — a DFA artifact has
no VM node machinery), two shared slopes.

**The per-entry coefficient is the same in both engines, and that is a
structural check, not a coincidence.** Fitted independently on the 1,488 VM
artifacts and the 999 DFA ones, the entry coefficient comes out at 5.064 and
5.073 B/entry respectively — the two populations share no patterns and the
tables are emitted by different code paths, but a table entry is decimal ASCII
plus a separator either way. A model whose coefficients drift between
populations is overfitted; this one does not.

The node coefficient fits only on VM artifacts, as it must: fitted over the
999 DFA artifacts the node term comes out at **0.000** (they have no nodes).

### 2.4 The error distribution — reported, including where it is worst

Absolute relative error `|B̂ − B| / B`:

| population | n | median | p90 | p99 | max |
|---|---|---|---|---|---|
| all compiled | 2,487 | **2.35 %** | 12.40 % | 18.21 % | 35.35 % |
| VM only | 1,488 | 2.28 % | 11.44 % | 15.84 % | 20.80 % |
| DFA only | 999 | 2.50 % | 13.13 % | 20.66 % | 35.29 % |
| **above 50 KB** | 18 | **4.18 %** | 6.26 % | — | **6.91 %** |
| top 20 by bytes | 20 | 5.26 % | 6.91 % | — | 20.80 % |
| below 50 KB | 2,469 | 2.29 % | 12.41 % | — | 35.35 % |

**The model does not degrade at the tail — it improves.** That is the property
the K rule needs, because the K rule only ever runs on artifacts above
131,072 B. Above 50 KB the worst error over the whole corpus is 6.91 %.

The top of the corpus, predicted against actual:

| actual B | predicted B | err | N | E | pattern |
|---|---|---|---|---|---|
| 651,412 | 685,692 | +5.3 % | 80 | 128,544 | `((a)\|ab){4000}c` |
| 465,818 | 433,625 | −6.9 % | 28 | 80,552 | `((a)\|bc){0,4000}d` |
| 384,611 | 362,968 | −5.6 % | 88 | 64,544 | `((a)\|ab){0,4000}c` |
| 288,314 | 280,367 | −2.8 % | 1,471 | 844 | nested-repeat N=8 |
| 225,862 | 223,102 | −1.2 % | 1,141 | 844 | nested-repeat N=6 |
| 221,597 | 218,082 | −1.6 % | 165 | 33,296 | `((a)\|ab){0,2047}c` |
| 162,034 | 162,714 | +0.4 % | 793 | 844 | nested-repeat N=4 |
| 97,857 | 96,035 | −1.9 % | 0 | 16,520 | `a{1,2000}` (DFA) |

Note the two mechanisms visible in the `N`/`E` columns: the top three
artifacts are **tables** (tens of thousands of entries, tens of nodes) and the
nested family is **nodes** (hundreds to thousands of nodes, 844 entries). §4.1
is about why that distinction decides the whole design.

### 2.5 Where the model is WRONG — the extrapolation limit

Fitted on artifacts up to 651,412 B and 1,471 nodes, the model is then applied
to the witness at 7,467 nodes — 5× beyond the fit range. Measured:

| witness at | actual B | predicted B | error |
|---|---|---|---|
| K = 8 (default) | 1,719,349 | 1,317,226 | **−23.4 %** |
| K = 4 | 776,115 | 582,674 | −24.9 % |
| K = 2 | 328,473 | 258,174 | −21.4 % |
| K = 1 | 87,118 | 75,794 | −13.0 % |

**The model UNDER-predicts the far tail by 13–25 %, which is the dangerous
direction for a refusal** — it says "fine" about something 23 % larger than it
claims. The mechanism is visible in the per-node cost, which rises with node
count (median `(B − 5.064·E)/N`: 199 B/node in the 401–2,000 band, 230 B/node
on the witness) because identifier and constant widths grow with the node
count (`slot_values[1301]` is a longer expression than `slot_values[7]`).

An `N·ln N` variant was fitted and is **not adopted**: it improves in-sample
max error only from 20.80 % to 18.00 % and still under-predicts the witness by
13.3 %, which does not buy a second term's worth of complexity.

**The consequence is a design constraint, and §4.3 obeys it: the model is
never the thing that refuses.** It selects K — a comparison between two
predictions of the same pattern, where the bias largely cancels — and the cap
is checked on `N` itself, which is exact and needs no model at all.

---

## 3. The K rule

### 3.1 The K curve, which nobody had

Census §9 records `--unroll=K` "swept across its full 1..4096 range" as NOT
measured — *"only K=1 (the minimum) is in the tension curves ... A STEP-2
design that wants K as a continuous dial needs that curve, not just the two
endpoints."* This lane took it: 15 subjects × K ∈ {1,2,3,4,6,8,12,16,32}
(`artsize_impl/ksweep.tsv`, `probes/ksweep.py`). Comment-excluded bytes:

| subject | K=1 | K=2 | K=3 | K=4 | K=6 | K=8 | K=16 | K=32 |
|---|---|---|---|---|---|---|---|---|
| nested N=8 | **60,902** | 103,586 | 195,443 | 163,386 | 288,963 | 288,314 | 288,244 | 288,244 |
| nested N=6 | **60,902** | 103,586 | 131,954 | 227,229 | 226,578 | 225,862 | 225,862 | 225,862 |
| nested N=4 | **60,902** | 103,586 | 163,697 | 163,386 | 162,034 | 162,034 | 162,034 | 162,034 |
| nested N=2 | **60,902** | 103,586 | 98,596 | 98,596 | 98,596 | 98,596 | 98,596 | 98,596 |
| `((a)\|ab){4000}c` | 644,055 | 645,106 | 647,368 | 647,208 | 654,010 | 651,412 | 659,932 | 677,052 |
| `((a)\|bc){0,4000}d` | 465,818 | 465,818 | 465,818 | 465,818 | 465,818 | 465,818 | 465,818 | 465,818 |
| `((a)\|ab){0,2047}c` | 204,367 | 206,809 | 208,005 | 211,693 | 211,593 | 221,597 | 241,487 | 281,263 |
| `(x(?:ab){2,4}){0,12}c` | **32,139** | 33,230 | 34,321 | 35,412 | 37,594 | 44,340 | 44,323 | 44,323 |
| `(a{10,20}){10,50}` | 70,596 | 72,878 | 77,468 | 79,795 | 91,513 | 88,988 | 107,242 | 125,338 |
| `(ab){300}`, `a(b\|c)+d`, `\d{4}-\d{2}-\d{2}` | flat — byte-identical at every K | | | | | | | |

Three facts the rule is built on:

1. **The curve is NON-MONOTONE.** N=8 is 195,443 B at K=3 and 163,386 B at
   K=4; N=4 is 163,697 at K=3 and 162,034 at K=6. `K` divides the quantifier's
   bound, so divisibility — not magnitude — decides how much remainder body a
   given K forces (`emit_vm.c`'s own comment at the counter rung: a `{20,22}`
   "unrolls its mandatory half and replicates when it does not"). **A greedy
   descent would stop at a local minimum. The rule must EVALUATE a ladder.**
2. **The curve saturates** past the quantifier's own factor: every subject is
   flat from some K onward. So the ladder needs no values above the default.
3. **Where the counter rung is not live, K is exactly a no-op** — `(ab){300}`,
   `a(b|c)+d`, `\d{4}-\d{2}-\d{2}` and `((a)|bc){0,4000}d` are **byte-identical
   across all nine K values**. That is D82's zero-cost property, measured
   directly on the axis this row moves, before any code is written.

### 3.2 The threshold

**`PCREC_SIZE_TERM_THRESHOLD = 131072` bytes** (comment-excluded, the §2.1
quantity). Two independent derivations, both from the corpus:

- **The gap.** Sorted, the corpus's tail is 98,596 / 162,034 / 221,597 /
  225,862 / 288,314 / 384,611 / 465,818 / 651,412 B. The **widest
  multiplicative gap anywhere in the top 20 is 1.64×, between 98,596 and
  162,034** — and 131,072 sits inside it, 33 % above the pattern below and
  24 % below the pattern above. No ordinary emitter or corpus movement flips
  a pattern across it.
- **The population.** 7 of 2,487 patterns (0.281 %) are above it; the corpus
  median is 23,650 B (5.5× below) and p99 is 44,340 B (3.0× below).

**A coincidence, named before a reader finds it:** 131,072 is also the value
of `PCREC_MAX_VM_NODES` and `PCREC_MAX_VM_REPLICATION_PRODUCT`. That is
**numerically a coincidence and semantically unrelated** — those cap a NODE
COUNT, this is a BYTE COUNT, and reusing a number derived for one role in
another is exactly the hygiene failure r39 punished ([OPT-K] finding S1). The
threshold is derived above from the byte distribution alone; it would be
131,072 if the node cap were any other number. If a reviewer prefers the
coincidence gone, 120,000 B sits in the same gap and nothing in this note
changes.

### 3.3 The rule

At VM emission, with `K_opt` = `--unroll=`'s value if given, else
`PCREC_DEFAULT_UNROLL_K` (8):

```
    if  --unroll= was given explicitly        ->  K = K_opt, term does not run
    if  B̂(K_opt) <= THRESHOLD                 ->  K = K_opt, term does not run
    else:
        for K_c in LADDER = [8, 6, 4, 3, 2, 1] with K_c <= K_opt:
            evaluate B̂(K_c)                    # N(K_c) from the existing pre-pass
        K_best = argmin B̂ , ties -> the LARGEST such K
        if  B̂(K_best) <= MATERIALITY * B̂(K_opt):   K = K_best
        else:                                       K = K_opt
```

- **Descending only.** The ladder never exceeds `K_opt`, so the term can only
  make an artifact smaller — it can never make one bigger than today's.
- **Ties go to the largest K**, preserving the throughput default wherever the
  size is the same.
- **`MATERIALITY = 0.75`** — descend only for a ≥ 25 % predicted saving. This
  is what keeps the term from paying the census's measured "~1–3 % slower on
  single-level large counts" for a 1–8 % size win.

**What the rule DOES, measured against every corpus pattern above the
threshold.** The ratio column is `B(K=1)/B(K=8)` from §3.1's actual bytes:

| pattern above threshold | B at K=8 | B at K=1 | ratio | rule |
|---|---|---|---|---|
| `((a)\|ab){4000}c` | 651,412 | 644,055 | 0.989 | **declines** |
| `((a)\|bc){0,4000}d` | 465,818 | 465,818 | 1.000 | **declines** |
| `((a)\|ab){0,4000}c` | 384,611 | 376,239 | 0.978 | **declines** |
| nested N=8 | 288,314 | 60,902 | **0.211** | **selects K=1** |
| nested N=6 | 225,862 | 60,902 | **0.270** | **selects K=1** |
| `((a)\|ab){0,2047}c` | 221,597 | 204,367 | 0.922 | **declines** |
| nested N=4 | 162,034 | 60,902 | **0.376** | **selects K=1** |

**This is the row's central result.** The rule selects on exactly the three
patterns where the census measured K=1 as free-or-faster (§8 item 1: 75–79 %
smaller, 12× faster gcc, "no measured throughput cost", and on N=8 *faster* —
13.4 µs → 5.9 µs) and declines on exactly the four where the census measured
it as a 1–3 % no-op — **without a `nested` clause, a depth test, or any
special case.** Nesting reaches the rule only through `N(K)`, because nesting
is what makes the node count K-sensitive; a table-dominated artifact has a
K-insensitive `N` and the model sees that by itself.

The witness: `B̂(K=8) = 1,317,226` > threshold, ladder gives
`B̂(K=1)/B̂(K=8) = 0.058`, so **K=1 is selected** — 1,719,349 B → 87,118 B, and
census §6's measured consequence at that K is 28,104 B `.o` and **1.015 s**
gcc, from 503,344 B and 55.13 s.

### 3.4 Where K must NOT descend

1. **An explicit `--unroll=K`.** The term never overrides a value the caller
   chose; `lib/pcrec.h` documents `unroll_k` as "A TUNING AXIS" and a tuning
   axis a size heuristic can silently overrule is not one.
2. **Below the threshold.** 99.72 % of the corpus, byte-identical.
3. **Below the materiality bar** — a small predicted saving is not worth the
   census's measured (if small) throughput cost on single-level counts.
4. **Never below K = 1.** K = 1 is one body copy; there is no K = 0.
5. **`PCREC_NO_SIZE_TERM`** (§7) denies the whole selection.

### 3.5 The speed side, stated honestly

The census's own STEP 1 caveat governs here and is not talked around: its
tension-curve throughput cells are **micro-scale** (2–13 µs subjects, 30
iterations × 5 trials) and **could not separate ±50 % effects** — a stated
size-no-op flag swung 2× between the loaded and quiet passes, and
`-fno-premul-table` read direction-inconsistent across five patterns. The
plan row records this verbatim.

So what this note claims about speed is only what survives that: **on the
patterns the rule selects, K=1's measured throughput is at parity or better**
(N=8: default 13.4/9.0 µs vs K=1 5.9/3.7 µs; N=6 at parity; the witness
6.03/5.60 µs vs 0.13/0.17 µs), and the census's contrary "~1–3 % slower"
finding is on the single-level large-count family, which the rule declines.

**What the bench must measure before this threshold is tightened** (I-15
ask (c), the pcrec-bench inbox channel, D78): pcrec-VM throughput on real
1 MB subjects, K=1 against K=default, for the patterns the rule selects. The
threshold is deliberately set where the term is a no-op on 99.72 % of the
corpus precisely so that it does not depend on a number this box cannot
resolve. **Tightening it below 131,072 B requires that measurement first.**

---

## 4. The cap

### 4.1 Why a byte cap is the wrong instrument — measured

The obvious reading of D45's consequence 1 is "cap the emitted bytes." That
reading does not survive measurement, and this is the finding that shaped the
design.

`gcc -O2 -c`, this box, this lane (`scripts/watchdog -s 300 -c 280 -m 4000m`,
`/usr/bin/time` rusage, **best of 3 trials**, load1 0.65 at start):

| artifact | `.c` bytes | comment-excl. | N | E | gcc CPU | `.o` |
|---|---|---|---|---|---|---|
| the witness (K=8) | 2,015,585 | 1,719,349 | 7,467 | 128 | **55.13 s** (census §6) | 503,344 |
| `a{1,31000}` | 1,380,303 | 1,367,865 (92 % tables) | **0** | 248,520 | **0.34 s** | 376,824 |
| `a{1,25000}` | 1,116,303 | 1,103,865 (92 % tables) | 0 | 200,520 | 0.24 s | 304,824 |
| `((a)\|ab){4000}c` | 675,586 | 651,412 (99.9 % tables) | 80 | 128,544 | 0.29 s | 202,904 |

**A 1.38 MB artifact costs gcc 0.34 s and a 2.0 MB one costs 55.13 s — a 162×
difference in cost for a 1.5× difference in size.** Table bytes are `.rodata`
initializers gcc lexes and emits nearly linearly; program bytes are basic
blocks it must analyse superlinearly. **A byte cap set anywhere that refuses
the witness would refuse `a{1,31000}` and `a{1,25000}` too, and both compile
in under half a second** — well inside D45's budget.

This is precisely r39's own lesson (finding S1: *"a set derived for one ROLE
reused for another"*). Bytes are the right quantity for the **user-facing**
size question Frank asked; they are the wrong quantity for the **compile-budget
refusal** D45 assigns. The model prices both; the cap binds only on the one
that predicts the budget.

**A second measured fact the cap must respect: the table term is already
bounded, and non-monotonically.** `((a)|ab){12000}c` emits **28,865 B with
zero table entries** — its prefilter DFA overflowed `PCREC_MAX_DFA_STATES_TABLE`
(32,000) and was dropped, so the artifact is 23× *smaller* than
`((a)|ab){4000}c`'s 651,412 B. Likewise `a{1,31000}` is 1,367,865 B and
`a{1,40000}` is **17,938 B**. Table growth therefore has a ceiling that an
existing cap already enforces, and the band in which it can produce a large
artifact is bounded above and below. Nothing new is needed for it.

### 4.2 The number, from D45's budget

The cap is on `N`, the post-K-selection node count. The relation to gcc CPU,
measured this lane across a spread chosen to DECORRELATE `N` from `E`
(`artsize_impl/probes/gccfit.py`; node-heavy subjects carry 844 entries,
table-heavy ones carry 0 nodes):

**Node-driven** (the nested family across N and K; `E` held at 844 throughout,
so every difference in the column is nodes):

| N | 262 | 445 | 498 | 793/799 | 1,141/1,147 | 1,471 | 7,467 |
|---|---|---|---|---|---|---|---|
| gcc CPU | 0.59–0.61 s | 1.09–1.13 s | 1.21–1.26 s | 2.33–3.13 s | 3.61–3.87 s | **7.09 s** | **55.13 s** |

**Entry-driven** (`a{1,n}`, pure DFA, `N = 0` throughout):

| E | 16,520 | 64,520 | 120,520 | 160,520 | 200,520 | 248,520 |
|---|---|---|---|---|---|---|
| gcc CPU | 0.07 s | 0.10 s | 0.16 s | 0.19 s | 0.25 s | **0.28 s** |

Fitted over the 20 node-driven points (log-log, the census's own witness
measurement included as the top point):

```
    gcc_cpu_s  ≈  0.00054 · N^1.269          residuals −20 % … +18 %
```

and the marginal costs, which is the whole argument:

- **5.37 ms per node** (from 262 → 1,471 nodes, measured)
- **0.0009 µs per table entry** (from 16,520 → 248,520 entries, measured)
- **a node costs gcc ≈ 5,930× what a table entry costs.**

**Provenance of the two gcc runs in this section.** §4.1's four rows are a
best-of-3 re-measurement; §4.2's curve is `gccfit.tsv`, one trial per row.
They overlap on `a{1,31000}` at 0.34 s and 0.28 s respectively — inside the
±20 % scatter §4.2's own residuals report, and stated here rather than left
for a reader to notice. An earlier draft of §4.1 quoted 0.56 s / 0.49 s /
0.53 s for these rows; those numbers wrapped `/usr/bin/time` around
`scripts/watchdog` instead of around `gcc`, so they measured the watchdog's
own startup as well. Recorded rather than silently corrected — it is the same
"the instrument measured itself" class `docs/testing.md` records for the
`timeout` wrapper's own launch cost inside two bench budgets.

D45's plain-axis budget is **10,000 ms CPU**. Two estimates of where it is
exhausted: the global fit says 2,305 nodes; anchoring at the measured worst
corpus point instead (1,471 nodes → 7.09 s, scaled by the same exponent) says
**1,929 nodes**. The fit under-predicts at the top (−20 % at 1,471, −19 % at
the witness), so the anchored, lower number is the one to use.

**`PCREC_MAX_VM_EMIT_NODES = 2000`**, derived as:

- **the measured budget crossing**, ~1,929 nodes anchored / 2,305 fitted,
  rounded to 2,000 — a cap whose number IS D45's budget expressed in the units
  that predict it;
- **above every corpus pattern**: the corpus max is 1,471 nodes, so **0 of
  2,487 are refused**;
- **above every corpus pattern AFTER K selection by 4.5×**: with §3.3's rule
  the three nested outliers drop to 262 nodes, and the largest node count
  remaining anywhere in the corpus is **445** (nested N=2, at 98,596 B, below
  the threshold and so untouched) — measured over all 2,487;
- and it **refuses the witness at K=8** (7,467 nodes, 55.13 s, 5.5× the
  budget), which is the pattern D45's founding incident is about.

**The tension the K rule resolves, stated rather than smoothed.** *Today* the
corpus's worst pattern sits at 1,471 nodes / 7.09 s — 71 % of D45's budget —
so a cap derived from that budget has only 1.36× node headroom over shipped
material, which would be uncomfortably tight for a refusal. What buys the
headroom is not the cap but the **K rule running first**: it takes that same
pattern to 262 nodes and 0.61 s, dropping the corpus's worst compile from 71 %
of budget to **11 %** and leaving the cap 4.5× clear of anything shipped. The
cap is only ever the backstop for what K descent cannot reduce.

### 4.3 Where it fires, and in what order

```
    1.  K selection (§3.3)                 -- the model, cheap, pre-emission
    2.  N = vm_count_slots(K_selected)     -- already computed, exact
    3.  if N > PCREC_MAX_VM_EMIT_NODES  ->  ctx_fail, REFUSE
    4.  emit
```

- **The cap is checked on `N`, not on `B̂`.** §2.5 measured the model
  under-predicting by up to 25 % at the tail; a refusal must not depend on
  that. `N` is a count the pre-pass already produces exactly.
- **K descent runs FIRST**, so the cap only ever sees what selection could not
  reduce. On the witness this is decisive: 7,467 nodes at K=8 would be
  refused; the rule reaches K=1 at 313 nodes and it compiles in 1.02 s.
- **The refusal happens before emission**, so a refused pattern costs the
  pre-pass and nothing else.
- **It cannot ship an uncompilable artifact**, because the only alternatives
  at step 3 are "refuse" and "emit something smaller" — and step 1 has already
  taken the smallest K. There is no path that emits a known-oversize artifact.

### 4.4 The diagnostic

Joining the family `emit_vm.c` already uses (`"pattern too large: ..."`, two
existing members at the repeat-copies and replication-product caps), inside
`pcrec_error.msg`'s 256 bytes on purpose:

> `pattern too large: the emitted matcher would contain %lld nodes (limit %d),
> which gcc cannot compile in reasonable time. A bounded repeat's body is
> replicated, and repetition counts MULTIPLY through nesting -- lower a count,
> or reduce the nesting`

**D26 tier.** This is pcrec's own wording and there is nothing to match:
PCRE2 has no emitted C and therefore no analogous diagnostic. D26's "requires
module 'X'" precedent does not apply either — the construct is real and
implemented, it is the *size* that is refused. No effort is spent on PCRE2
wording here, per D26.

`docs/spec/limits.md` gains the constant and the refusal in the same change
(D80: a caller-observable limit is a contract change).

### 4.5 The [SEL-1] interaction

The case: `auto` selects DFA; the DFA build overflows
`PCREC_MAX_DFA_STATES_TABLE`; [SEL-1] falls back to the VM; the VM's node
count then trips the cap. **This is a live shape, not a hypothetical** —
census §2 found it in the corpus (`bench:loglines:level-context`) and the
witness itself is one (its `RX_VM_PREFILTER` is `"none"` for exactly this
reason).

Two obligations:

1. **The user must not be told the wrong story.** As specified above, the
   refusal names repetition counts and nesting — but after a DFA-overflow
   fallback the real story is "this pattern needed a DFA, the DFA overflowed,
   and the VM fallback is too large." So: **when `RX_ENGINE_WHY`'s reason is a
   fallback, the cap's diagnostic appends it.** Without this the diagnostic is
   actively misleading on the one path most likely to reach it.
2. **The fallback can never ship an uncompilable artifact**, which it cannot
   by §4.3: the cap is checked on the VM path regardless of how that path was
   reached. The fallback does not bypass it, and there is no third engine to
   fall back to — the result is a refusal, which is the correct outcome.

**Open question for the panel or Frank (§10, Q2):** the cap is **not
deniable** — `-fno-size-term` denies the K selection but not the cap, because
a safety refusal a flag turns off is not a safety refusal, and D45's
consequence 1 is a compiler-side obligation. The cost is that a user who
genuinely wants a 5-minute gcc compile cannot have one. This note takes the
non-deniable position; it is a ruling, not a measurement.

---

## 5. The three levers, priced and all three DECLINED

Census §7 named three candidates from the manager's line-kind attribution of
the witness and explicitly left them unpriced against the corpus. They are now
priced. Method: a measurement-only subagent, read-only, over the witness, 12
of census §4's top outliers (population B), and a reproducible 200-pattern
sample of corpus patterns (seed 20260828; 120 landed on the VM engine and were
measured, 62 on DFA, 18 refused) — population C. load1 0.08–0.26 throughout.

**The measurement's own control:** its label/goto extraction reproduces census
§7's independently-taken counts **exactly** on all five outliers the census
measured (rxt-00127 80/81, rxt-00143 28/38, rxt-00118 88/97, rxt-00030
1471/1525, rxt-00029 1141/1177) and the witness's §6 counts exactly
(7,467 labels / 7,681 gotos / 1,861 `RX_PRUNE_TOO_SHORT`).

### 5.1 Lever 1 — a shared span-loop helper per (class, stride, greediness) shape

| population | sites | distinct shapes | saving |
|---|---|---|---|
| witness | 1,434 | 11 | 1,362,639 B (**67.6 %**) |
| nested family (rxt-00027..30) | 72–288 | 3 | **37.8–58.9 %** |
| `((a)\|ab){N}c` family (corpus ranks 1–3) | **0** | — | **0 %** |
| corpus sample (n=120) | — | — | **median 0 %, p90 0 %** |

**DECLINED.** Only 16 of 120 sampled VM patterns have a single span-loop site,
and the median saving among *those* 16 is still 0 %. The corpus's three
largest artifacts have **zero** sites — the lever is inapplicable to exactly
the patterns whose size prompted the row. Its real wins (the witness, the
nested family) are the same population §3.3's K rule already shrinks by
2.7–4.7× using a shipped mechanism, no new emitted form, and no new answer
surface.

**Trigger to revisit:** a measured pattern above the threshold where the K
rule is declined by the materiality bar AND span loops exceed 30 % of its
comment-excluded bytes. None exists in the corpus today.

### 5.2 Lever 2 — the node-skeleton fold (singly-referenced labels)

The census measured only the label:goto RATIO (~1:1) and called it *"suggestive,
not proof"*. The actual predecessor walk was done: a label is a fold candidate
iff it has exactly one incoming `goto`, no fall-through, **and its address is
never taken** (`&&rx_LN` — this emitter uses computed goto, so a label in a
jump table is not foldable at any predecessor count).

| population | labels | fold candidates | address-taken | saving |
|---|---|---|---|---|
| witness | 7,467 | 31.3 % | **31.8 %** | 158,442 B (**7.86 %**) |
| population B | 28–1,471 | 34–100 % | varies | 0.12–7.6 % |
| corpus sample | median 10 | 57.0 % | 10.6 % overall | **median 0.99 %, p90 2.20 %, max 10.6 %** |

**DECLINED — and the 1:1 ratio the census flagged was indeed misleading.**
Nearly a third of the witness's labels are computed-goto resume targets and
structurally unfoldable, which no ratio could have shown. A corpus median of
0.99 % is far below any materiality bar this project has used ([OPT-K]'s was
2×). This is the only one of the three with a general, positive effect, and it
is worth ~1 %.

**Trigger to revisit:** if a future emitted form pushes fold candidates above
25 % of comment-excluded bytes on a measured pattern.

### 5.3 Lever 3 — hoisting the MRL prune-guard's per-copy constant

| population | guard calls | groups after factoring the constant | saving |
|---|---|---|---|
| witness | 1,861 (avg 62 B) | 20 (largest 734 members) | 38,463 B (**1.91 %**) |
| population B | 0–21 | mostly none | **0.00–0.09 %** |
| corpus sample | 33 of 120 have any | — | **median 0 %, p90 0 %** |

**DECLINED, and it is not even free at runtime.** The corpus's typical guard
is 32 B — already shorter than a per-site comparison would be after hoisting.
And the sites are spread across the artifact's backtracking control flow, not
a straight-line region, so the hoisted value would have to survive arbitrary
pushes and retreats: a trailed slot, not a register. The byte model above does
not price that, and it is a cost, not a saving.

### 5.4 What else is NOT built

- **Per-quantifier K.** D47's ADDENDUM rules K one-per-artifact in v1 and
  moved the downward clamp whole to plan row **[ENG-CLAMP]** (`STATE:not-started`).
  This row holds that ruling: it changes WHICH single K an artifact gets, not
  how many K values it has. Nothing here forecloses [ENG-CLAMP]; §3.3's ladder
  becomes its per-quantifier inner loop if it is ever built.
- **A continuous K dial.** §3.1 measured the curve as non-monotone and
  saturating — a fixed ladder is the honest shape for it.
- **`--engine=vm` as an automatic size lever.** It is the largest size lever
  the census found (`.o` to 4–9 %) and it is never automatic: the measured
  price is up to **173,580×** on the failing path, and D46's ordering rule
  (`src/gen/CLAUDE.md`, "prefilter-before-VM is an ORDERING RULE, not a tuning
  knob") forbids it. It stays a user-chosen engine axis.
- **Anything that reduces prose.** Census §5 measured prose at 42 % of source
  bytes and r = 0.43 against `.o`. [M6-READ] is a deliberate convention and
  the bytes it costs are not the bytes a user ships.

---

## 6. Identity

### 6.1 The argument

**Claim: for any K ≥ 1, the artifact's answer — span, capture slots, failure
surface — is identical.**

`K` is the counter rung's **chunking factor** and not a semantic choice. The
rung compiles a bounded repeat to `ceil(n/K)` copies of the body plus an
iteration counter whose arithmetic makes the realized iteration count exact
for any K ≥ 1 (`emit_vm.c`, the counter rung; `docs/design/counterk_impl/
counterk_design.md` §4.1). Varying K changes how many source-level copies the
same loop is written as. It does not change:

- **which rung is selected** — rung selection runs before K is consulted, and
  §3.1's stamps confirm it: the rung bits are identical across the ladder on
  every subject measured;
- **the choice points or their preference order** — one per body iteration
  either way;
- **capture, trail or cut behaviour** — per iteration, not per chunk;
- **the step/work budgets charged** — per iteration.

### 6.2 The gate, and the GAP this row found

**`make test-axes` does not cover `--unroll`.** `tests/axes/run_axes.sh`
derives its axis registry mechanically from `lib/pcrec.h`:

```
    grep -oE 'PCREC_(NO|FORCE)_[A-Z_]+ *= *1u << [0-9]+' lib/pcrec.h
```

`--unroll=K` is a **value** axis (`pcrec_options.unroll_k`), not a deny/force
bit, so it has never been swept. **The claim in §6.1 — that every K is
answer-identical — is not proven by any gate today.** That is the check the
row owes, and it was found by reading the script rather than trusting the
brief's summary of it.

Three controls, in the order they must land:

1. **The K sweep (NEW, and the load-bearing one).** The corpus run at each
   `K ∈ {1,2,3,4,6,8}`, answers compared case-by-case against the default
   build. This proves §6.1 for the ladder the rule can actually choose from.
   Without it the rule is selecting among values nobody has verified.
2. **`-fno-size-term` (bit 17)** joins `make test-axes` **by construction** —
   it is a `PCREC_NO_*` bit and the script's own `grep` finds it, sweeping the
   whole `.rxt` corpus by answer against the default build.
3. **Zero cost where not selected (D82), proved as [OPT-K] §7.3 proved it,
   not inferred**: at least four declined patterns spanning both engines,
   compiled with this compiler and with one built from `main`, disassembled,
   requiring **0 differing instructions**, with the source differing by exactly
   the expected stamp and `abi` lines.

**And one control this row specifically owes, from the census's own lesson.**
For every pattern where the term BINDS, the size-term build and an explicit
`--unroll=<the K the model chose>` build must be **byte-identical apart from
the two stamp lines**. This is what proves the term only *chooses K* and does
not quietly do anything else — the check that would catch a general mechanism
degenerating into a special case.

**What the controls do NOT prove: byte identity.** D81 makes selection stamps
unconditional, so the `-fno-size-term` build differs from today's compiler by
exactly the new stamp lines on every artifact. [OPT-K]'s r39 finding A1 was
precisely a draft claiming byte identity that D81 made false; this note does
not repeat it.

---

## 7. Stamps, flags, and the axis registry

### 7.1 Stamps (D81: selection facts are unconditional)

| stamp | value | on |
|---|---|---|
| `<PREFIX>_UNROLL_K` | the chosen K, an integer | **every VM artifact**, unconditionally |
| `<PREFIX>_UNROLL_K_WHY` | `"default"` \| `"size-model"` \| `"option"` | **every VM artifact**, unconditionally |

Unconditional is the point: D81 splits the D46 family so that a selection fact
is stamped **whether or not it fired**, which is what makes the stamp readable
as evidence rather than as a hint. `"default"` is a fact, not an absence.

VM artifacts only, matching `RX_VM_RUNGS` and `RX_VM_PREFILTER`: a DFA
artifact has no counter rung, so there is no K to have selected. (D81's
unconditional rule is about not conditioning a stamp on its own outcome, not
about stamping VM facts on DFA artifacts.)

**Not stamped: the realized byte count.** An artifact cannot carry its own
size — writing the number changes it. Recorded here because it is the obvious
thing to ask for and the reason it is absent is not obvious.

**`rx_info` mirror:** the chosen K is a compile-time selection fact with no
run-time consumer — nothing in the match API's behaviour depends on it. It is
NOT mirrored into `struct rx_info`. ([OPT-K]'s precedent stamps a sibling
macro, not an `rx_info` field, for the same reason.)

### 7.2 The deny flag

`PCREC_NO_SIZE_TERM = 1u << 17` / `-fno-size-term`. **Bit 16 is taken** —
[OPT-K]'s `PCREC_NO_OFFSET_SKIP`, verified in `lib/pcrec.h`. `docs/spec/
tuning.md` gains a §2.15 in §2.13's deny-only shape, and §2's count moves
from fourteen to fifteen.

It denies **the K selection only**, never the cap (§4.5, Q2).

### 7.3 The registry

`tests/registry/run_registry_tests.sh` pins the axis-registry check count at
**59** (moved from 53 when [OPT-K]'s bit 16 joined). This row moves it again.
The note deliberately **does not guess the new number**: it is the count
`axes_registry_check` produces once the candidates are registered, read from
the run and pinned in the same change. Site named, value measured — the
inverse of pinning a number and then making the code agree.

### 7.4 The five things every axis gets ([CHK-2]'s convention)

| # | thing | this row's |
|---|---|---|
| 1 | stamp | `<PREFIX>_UNROLL_K` and `<PREFIX>_UNROLL_K_WHY` (§7.1) |
| 2 | deny flag | `-fno-size-term` / `PCREC_NO_SIZE_TERM` (bit 17), `docs/spec/tuning.md` §2.15 |
| 3 | identity gate | `make test-axes` bit 17 by construction, **plus** the K sweep §6.2 owes |
| 4 | structural check | `tests/codegen/run_size_term.sh` — reads the ARTIFACT (the emitted body-copy count against the stamped K, and that the stamp's `_WHY` matches which path ran), never the stamp alone |
| 5 | sabotage row | `tests/mech/` — the ladder reduced to a greedy descent (must be caught by the non-monotone subject, §3.1); the materiality bar removed; the cap's comparison inverted |

Sabotage row 1 is the one worth naming: a greedy descent passes every
answer-identity check ever written, because it is answer-identical. Only a
SIZE assertion on the non-monotone subject can see it.

---

## 8. The `abi` bump — FOUR sites, one change (D76)

`rx_info.abi` moves **9 → 10**: the emitted text gains two file-scope stamp
lines. D76 is explicit that emitted-scaffolding changes ARE a bump.

| # | site |
|---|---|
| 1 | `src/gen/emit_dfa.c` — `.abi = 10` |
| 2 | `tests/codegen/run_codegen_tests.sh` — `ABI_EXPECT=10` and its `[DD-14.FB]` §10.4 message |
| 3 | `docs/spec/match_api.md` §6 — the "`rx_info.abi` is `10`" sentences (currently `9`) |
| 4 | `tests/codegen/run_recursion_identity.sh` — comparison (B)'s `FILEPIN`, re-pinned to this change's last `src` commit |

`make test-codegen` before delivering. Two lanes in one night have missed
sites 2 and 3.

**Size estimate for the new scaffolding, before the fact** (r39 finding P3 —
`abi` 7 overshot its own estimate sixfold): two `#define` lines, `_UNROLL_K`
plus `_UNROLL_K_WHY`, **≈ 55 bytes** on every VM artifact and 0 on DFA
artifacts. To be measured after and compared here.

---

## 9. The measurement plan for the code phase

**Discipline** (r39 finding P2 — the box carries lanes): idle box, `load1`
recorded per row and waited down below 2, `taskset -c 3`, median of ≥ 5
trials, every command's provenance recorded. Sizes and gcc times are
deterministic and load-independent; throughput is not, and §3.5 governs what
may be claimed from it.

**The numbers to beat, named before measuring** (r39 finding P1 — a stated
prediction with a tolerance, so a 5× real gain on a 20× prediction cannot pass):

| # | subject | predicted | tolerance |
|---|---|---|---|
| 1 | the witness | K=1 selected; ≤ 30 KB `.o` and ≤ 1.1 s gcc (census: 28,104 B, 1.015 s) | must not exceed either |
| 2 | nested N=8 / N=6 / N=4 | K=1 selected; comment-excluded 288,314 → 60,902 B (−78.9 %), 225,862 → 60,902 (−73.0 %), 162,034 → 60,902 (−62.4 %); `.o` 75–79 % smaller (census §8) | ±5 % on the byte figures |
| 3 | the four declining patterns above the threshold | K unchanged at 8; **`.o` byte-identical**; source differs by exactly the two stamp lines | exact |
| 4 | D82 zero cost | ≥ 4 declined patterns, both engines, **objdump 0 differing instructions** vs a `main`-built compiler | exact |
| 5 | the corpus size log | regenerated on `main`; **exactly the 3 selecting patterns move**; every other row differs by exactly the stamp constant | exact |
| 6 | the cap | 0 of 2,487 corpus patterns refused | exact |
| 7 | `abi` scaffolding | +55 B/VM artifact (§8's estimate) | measured and compared |

**Answer identity**, before any of the above: §6.2's three controls plus the
byte-identity-against-explicit-`--unroll` control, and `make test-axes` green
under bit 17.

---

## 10. Open questions for the panel or Frank

1. **The materiality bar at 0.75.** It separates the measured population
   cleanly (selecting rows at 0.211/0.270/0.376, declining rows at
   0.922–1.000 — an enormous gap, nothing between 0.376 and 0.922). Any value
   in (0.38, 0.92) gives identical behaviour on today's corpus, so the corpus
   cannot choose within that range. 0.75 is a judgement inside a measured gap,
   not a measured number, and is stated as such.
2. **The cap is not deniable** (§4.5). `-fno-size-term` denies the K
   selection but not the refusal. This is a ruling — a safety refusal a flag
   turns off is not one — with a real cost: a user who wants a 5-minute gcc
   compile cannot have one, and their only recourse is to change the pattern.
   Frank's call.
3. **The threshold's numeric collision** with `PCREC_MAX_VM_NODES` (§3.2).
   Semantically unrelated, derived independently, named here so no reader
   infers a shared source. 120,000 B sits in the same gap if the collision is
   judged too confusing to keep.
4. **`a{1,25000}`-shaped artifacts are left alone** (1.12 MB, gcc 0.49 s).
   They are large for a user to ship and cheap for gcc to compile, so neither
   §3 nor §4 touches them: the K rule sees a K-insensitive `N` and the cap is
   not about bytes. If Frank's concern is the SHIPPED SIZE rather than the
   compile budget, this is the population that answers it, and the instrument
   would be a third mechanism (a byte-based *warning*, or a table-form
   selection) that this note does not propose. **Flagged because the row's
   founding quote is about size, not compile time.**

---

## 11. What STEP 2's code phase builds

1. The model (§2.3) as a function over `(engine, N, E)` in the emitter,
   integer arithmetic (coefficients 174 and 5 with the intercepts; nothing
   rounds to zero at any corpus magnitude — r39 finding S-D5's lesson).
2. The K selection (§3.3) at the one site that resolves `v.unroll_k`
   (`emit_vm.c:7461`).
3. The node cap (§4.3) and its diagnostic (§4.4), plus `docs/spec/limits.md`.
4. The two stamps (§7.1), the deny flag (§7.2), the registry re-pin (§7.3).
5. The `abi` bump, four sites (§8).
6. The checks: structural, sabotage, the K sweep, the byte-identity control
   (§6.2, §7.4).

It does **not** build any of census §7's three levers (§5), per-quantifier K
(§5.4, [ENG-CLAMP]'s), or any table-form change (§10 Q4).
