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

1. **The r40 panel refuted the first version of this note, and the refutation
   is the most useful thing in it** (§2.0). The instrument that produced the
   model was blind to the VM hybrid prefilter's computed-goto machinery, so
   K41's SECOND witness — a real, already-pinned oversize pattern — was read
   at 118,240 B when it is 1,220,606 B, and NEITHER mechanism engaged on it.
   The classifier's own regexes were the population nobody counted.
2. Emitted size is predicted by **four** counts, from the corrected
   instrument: VM nodes `N`, prefilter DFA states `S`, data-table entries `E`,
   and computed-goto **jump-table entries `J`** (§2.3). Median error 2.39 % over
   2,487 corpus artifacts, 2.56 % on the population above 100 KB, and −8.8 %
   and −23.2 % on the two K41 witnesses, which are 2–5× outside the fit range.
3. **The size a user ships and the cost gcc pays are different quantities, and
   the row needs both.** Measured: a data-table entry costs gcc **0.905 µs**, a
   jump-table entry **8.7 µs**, and a VM node **5.37 ms** — a node is ~5,930×
   a data entry (§4.1). `a{1,31000}` is a 1.37 MB artifact that compiles in
   **0.34 s**; K41 witness 2 is 1.22 MB and costs **66.92 s**.
4. So the cap binds on **CODE bytes** — total bytes minus the measured table
   contribution — not on total bytes and not on nodes alone. Measured, that
   quantity separates the whole population cleanly: everything at or below
   320 KB of code costs ≤ 71 % of D45's budget, and the next measured point up
   is 837 KB at **669 %** of it (§4.2).
5. The **K rule**: above a threshold, the counter rung's `K` is chosen by
   re-emitting over a descending ladder `[8,6,4,3,2,1]` and keeping the
   smallest REALIZED artifact — evaluated, not descended, because the
   size-vs-K curve is **NON-MONOTONE** (§3.1). `--unroll=K` remains an
   explicit override the term never overrides.
6. It reads REALIZED counts, not predictions, because **there is no
   pre-emission node count in the compiler today** (§2.2, panel finding F6):
   `vm_count_slots` counts slot categories and `nlabel` is an emission-time
   counter. Since the emitter must walk to know `N`, the rule re-emits — which
   also removes the model's error from the decision. Measured ladder cost:
   **2.84 s** on the worst pattern in the project (which today costs gcc 55 s),
   0.01 s on an ordinary one, and it runs on 0.28 % of the corpus (§3.3).
7. **Threshold 120,000 B**, in the corpus's widest tail gap; a measured no-op
   on **2,480 of 2,487** patterns (99.72 %). **Cap
   `PCREC_MAX_VM_EMIT_CODE_BYTES = 500000`**, in the empty band between the
   corpus's worst (284,035) and witness 2's (836,621).
8. **Both K41 witnesses are now classified, by different mechanisms** (§3.3,
   §4.3): witness 1's size IS node replication, so the K rule takes it to K=1
   — 1,719,349 → 87,118 B, gcc 55.13 s → 1.02 s, no refusal. Witness 2's size
   is its PREFILTER, which K cannot touch (K=1 saves 8.7 %), so it is
   **REFUSED** by the cap — correctly, at 66.92 s against a 10 s budget.
   **This moves K41's pinned fuzz-gate bucket from 2 to 0** (§4.7).
9. **The three levers of census §7 are priced and all three are DECLINED**
   (§5), on measurements. The largest is worth a corpus median of **0.99 %**.
10. `abi` 9 → 10 (four sites), deny flag at **bit 17**, two new unconditional
    stamps, and an identity gap this row found by reading the gate: `--unroll`
    is a VALUE axis, so **no gate proves any K answer-identical today** (§6.2).


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
on essentially the whole corpus**, which is what §3.2's threshold and §6.2's
zero-cost obligation are for.

---

## 2. The size model

### 2.0 What the r40 panel refuted, and how

The first version of this note fitted a two-term model (`N`, `E`) and reported
a median 2.35 % error over the corpus. The panel ran the built compiler on
**K41's second witness** — a pattern already pinned as oversize by the fuzz
gate — and found:

| | first version | actual |
|---|---|---|
| predicted size | 118,240 B | — |
| comment-excluded size | — | **1,220,606 B** (10.3× under) |
| `N` seen | 552 | 552 |
| `S` seen | **0** | **3,108** |
| `J` seen | **0** | **34,188** |

**Cause: the instrument, not the model.** `measure.py`'s `LABEL_RE` matched
only `rx_L<N>:`, and this artifact's prefilter uses `rx_s<N>:`; its
`TABLE_DECL_RE` required a `\w`-only type and could not cross the `*` in
`static const void *const rx_targets_N[11]`. So 3,108 jump tables and 3,108
state labels were invisible. Consequence: `B̂` sat below the threshold on a
pattern 10× the threshold, the node cap saw `N = 552`, and **neither mechanism
engaged on a real oversize artifact**. 368 of 2,487 corpus patterns emit this
form — the corpus simply never blows it up (its `J` tops out at 210 against
the witness's 34,188).

**The lesson, named because this project has recorded it before**
(`docs/dev/learnings.md` §3, memory `pcrec-check-design-lessons`): *the
classifier's own regexes were the population nobody counted.* A control that
recognises things by a spelling silently reports zero for every spelling it
does not know, and zero reads exactly like "this artifact does not have any".

**The two fixes, both structural rather than a widened pattern.** The
classifier is now anchored on the RIGHT-hand side (`= {`) and on the emitter's
own `rx_` prefix rather than on a type spelling, so a new element type cannot
drop out of the count again; and it counts label FAMILIES separately, so an
unrecognised family shows up as a nonzero `other` column instead of vanishing.

**One correction to the finding's own arithmetic.** The panel cited the actual
size as 1,214,333 B, which is the split form's `.c` **alone**; the `.h` sidecar
is 6,368 more. The true figures are **1,220,606 B** self-contained and
**1,220,703 B** for `.c`+`.h` — and this is the same sidecar undercount the
census recorded and corrected mid-lane for witness 1
(`artifact_size_census.md` §6). The finding is unaffected: the instrument was
blind to ~1.1 MB of the artifact either way.

### 2.1 What it predicts, and in what units

The model predicts **comment-excluded emitted bytes** — total source bytes
minus `[M6-READ]` prose — which is:

- the quantity `tests/lib/size_count.sh` already defines and
  `docs/dev/artifact_size_log.tsv` already logs for every corpus pattern;
- the quantity the census recommends. Census §5 measured prose at 42.1 % of
  aggregate source bytes but r = 0.43 against `.o`, versus r = 0.99 for
  program+tables: *"a size term that wants the number a user ships should
  price program+tables, not source bytes."*

**Provenance, and the control on it.** `artsize_impl/probes/measure.py`
reimplements `size_count.sh`'s three-state comment tracker in python. That is a
control sharing a definition with what it controls, so it is **verified, not
assumed**, at both ends of the range:

- six ordinary artifacts, agreeing to the byte with the shipped shell
  implementation (25,855 / 57,793 / 17,353 / 40,788 / 17,068 / 17,296);
- **K41 witness 2, agreeing to the byte in BOTH artifact forms** — 1,220,606
  self-contained and 1,220,703 for the split `.c`+`.h` pair, which is the form
  `docs/dev/artifact_size_log.tsv` itself logs. This is the control the panel
  asked for, and it is the one the first version should have run: it costs one
  command and it is the only check that would have caught §2.0 without a
  witness.

An independent cross-check of the DEFINITION: census §6's own depth-aware
five-bucket classifier puts witness 1 at program 1,657,633 + scaffold 60,792 +
tables 924 = **1,719,349 non-prose bytes**, and this lane's flat tracker
measures **1,719,349**. Two independently written classifiers, to the byte.

### 2.2 The inputs, and the one that does not exist (panel finding F6)

| input | what it is | where it comes from |
|---|---|---|
| `N` | VM nodes — one per `rx_L<N>:` label | the emitter's `vm_label()`, `v->nlabel` |
| `S` | prefilter DFA states — one per `rx_s<N>:` label, the computed-goto form (`RX_DFA_SCAN "attempt"`, `RX_DFA_TABLE "none"`) | the DFA builder's state count |
| `E` | declared entries in DATA tables (transition/accept/class) | `states × ncls`, already bounded by `PCREC_MAX_TABLE_ENTRIES` |
| `J` | declared entries in POINTER tables (`static const void *const rx_targets_N[…]`) | `S × ncls` |

**`N` is NOT available before emission, and the first version asserted that it
was.** The panel checked: `vm_count_slots` (`emit_vm.c:2314`) accumulates slot
CATEGORIES — `nguard_total`, `nlow_total`, capture and counter slots — not a
node count; and `nlabel` is incremented by `vm_label()` **during** emission
(`emit_vm.c:690`). There is no pre-emission node counter in the compiler.

**The design takes this as a constraint rather than building around it, and it
comes out better for it.** Adding a counting walk that mirrors the emitter's
structure would be a parallel mechanism with nothing keeping the two in sync —
the failure this project has a standing rule against
(`pcrec-general-mechanisms-not-special-cases`). Instead **the rule RE-EMITS**
(§3.3): the emitter already writes into a `StrBuf`, so emitting a candidate `K`
to a scratch buffer and reading `v->nlabel` and the realized byte counts is the
same code path, not a second one.

Two consequences, both good:

- **the selection consumes EXACT counts, not predictions** — the model's
  13–23 % tail error never reaches the decision (§2.5);
- **so does the cap** (§4.3).

The model's remaining jobs are to be the note's reviewable cost function, to
explain what drives size, and to serve the early refusal in §4.3.

### 2.3 The fit

Joint two-intercept least squares (`artsize_impl/probes/fit2.py` — panel
finding F5: the first version committed a single-intercept script that could
not produce its own quoted numbers) over the 2,487 corpus artifacts that
compile plus the 16-point `jfit` grid of §4.1:

```
    B̂  =  S(engine)  +  174.04 · N  +  197.13 · S  +  5.070 · E  +  11.184 · J
    S(vm) = 20,653 B        S(dfa) = 12,219 B
```

**`J`'s coefficient is confirmed twice, independently.** The joint fit puts it
at 11.184 B/entry; the direct measurement of §4.1's decorrelated grid — four
`n` values, differencing bytes against `J` at fixed `N` and `S` — gives
**11.08 B/entry on all four rows, to two decimals**. The corpus could not have
produced this coefficient at all: its `J` never exceeds 210 entries, where the
witness carries 34,188.

The per-DATA-entry coefficient is 5.070, essentially unchanged from the first
version's 5.064, and still fits at ~5.07 on VM and DFA artifacts separately —
disjoint populations, different emitter paths, one physical constant.

### 2.4 The error distribution — reported, including where it is worst

| population | n | median | p90 | p99 | max |
|---|---|---|---|---|---|
| corpus, all compiled | 2,487 | **2.39 %** | 13.48 % | 20.52 % | 33.65 % |
| corpus + `jfit` (the fitted population) | 2,503 | 2.38 % | 13.47 % | 20.52 % | 33.65 % |
| **corpus above 100 KB** | 7 | **2.56 %** | — | — | **6.85 %** |

The DFA-only maximum is **35.35 %** on `a\bb` under the first version's
two-term model — the global maximum, not the 35.29 % the first version quoted
from the 4th-worst row (panel finding F4). Under the four-term model the
global maximum is 33.65 %.

**The model is most accurate where the mechanisms bind**, which is the property
they need: 2.56 % median and 6.85 % worst over everything above 100 KB.

### 2.5 Where the model is WRONG — the two K41 witnesses

Both witnesses are far outside the fit range (witness 1 at 7,467 nodes against
a corpus maximum of 1,471; witness 2 at 34,188 jump entries against 210):

| case | actual B | predicted B | error |
|---|---|---|---|
| **witness 1**, K=8 | 1,719,349 | 1,320,831 | **−23.2 %** |
| witness 1, K=4 | 776,115 | 584,135 | −24.7 % |
| witness 1, K=1 | 87,118 | 75,775 | −13.0 % |
| **witness 2**, K=8 | 1,220,606 | 1,113,382 | **−8.8 %** |
| witness 2, K=1 | 1,114,780 | 1,035,587 | −7.1 % |

**The model UNDER-predicts the far tail by 7–25 % — the dangerous direction for
a refusal.** The mechanism is a per-node cost that rises with node count
(median `(B − tables)/N` is 199 B/node in the 401–2,000 band and 230 B/node on
witness 1) because identifier and constant widths grow with the count
(`slot_values[1301]` is a longer expression than `slot_values[7]`). An
`N·ln N` variant was fitted and rejected: it improves the in-sample maximum
only from 20.8 % to 18.0 % and still under-predicts witness 1 by 13.3 %.

**This is exactly why §2.2's re-emission matters.** Neither the selection nor
the refusal reads `B̂`; both read realized counts from an emission that has
already happened. The model's error is a property of the note's explanation,
not of the shipped decision.

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

### 3.1a The model ranks K correctly — evidence for the model, not the rule

The first version made this section load-bearing: it argued the rule consumes a
RANKING rather than an absolute prediction, so the model's absolute error did
not matter. §2.2 has since removed the model from the decision path entirely —
the rule re-emits and reads exact bytes — so this is now **evidence that the
cost function in §2.3 describes the emitter correctly**, not a defence of the
rule.

Measured over §3.1's fifteen subjects on the ladder `[8,6,4,3,2,1]`, ties to
the largest K: **the model picks the byte-optimal K on 15 of 15**, with
absolute error at the chosen K running −6.9 % to +15.9 % over the fourteen VM
subjects. A bias roughly constant across K for one pattern cannot change an
argmin, which is why the ranking survives an error the absolute prediction does
not.

(The fifteenth subject, `\d{4}-\d{2}-\d{2}`, is a DFA artifact with `N = 0`;
K is a no-op on it and it is included to show the rule leaves it alone.)

### 3.2 The threshold

**`PCREC_SIZE_TERM_THRESHOLD = 120000` bytes** (comment-excluded, §2.1's
quantity). Two derivations, both from the corpus:

- **The gap.** Sorted, the corpus's tail is 98,596 / 162,034 / 221,597 /
  225,862 / 288,314 / 384,611 / 465,818 / 651,412 B. The **widest
  multiplicative gap anywhere in the top 20 is 1.64×, between 98,596 and
  162,034**, and 120,000 sits inside it: the largest artifact below is
  98,596 B (the threshold is 1.22× it) and the smallest above is 162,034 B
  (1.35× the threshold).
- **The population.** 7 of 2,487 patterns (0.281 %) are above it; the corpus
  median is 23,650 B and p99 is 44,340 B.

**Why 120,000 rather than the first version's 131,072** (panel finding AR10).
The first version noted the numeric collision with `PCREC_MAX_VM_NODES` and
disclaimed it. The panel found the collision is worse than stated:
`limits.h:172,240` makes `PCREC_MAX_VM_REPLICATION_PRODUCT` a literal ALIAS of
`PCREC_MAX_VM_NODES = 131072`, so the same number would name three things in
two files. The note's own costless fix is taken: 120,000 sits in the same gap,
selects the same 7 patterns, and shares a value with nothing.

### 3.3 The rule

At VM emission, with `K_opt` = `--unroll=`'s value if given, else
`PCREC_DEFAULT_UNROLL_K` (8):

```
    emit at K_opt                            # the emission that happens anyway
    if --unroll= was given explicitly    ->  keep it; the term does not run
    if realized bytes <= THRESHOLD       ->  keep it; the term does not run
    else:
        for K_c in LADDER = [8,6,4,3,2,1] with K_c < K_opt:
            re-emit to a scratch buffer, read realized bytes
        K_best = argmin realized bytes , ties -> the LARGEST such K
        if  bytes(K_best) <= MATERIALITY * bytes(K_opt):  keep K_best's emission
        else:                                             keep K_opt's
```

- **It reads REALIZED bytes, not `B̂`** — §2.2: there is no pre-emission node
  count, the emitter must walk anyway, and an exact number is strictly better
  than a prediction with 7–25 % tail error. The model of §2.3 is what makes the
  rule predictable and reviewable; it is not what the rule consumes.
- **Evaluated, not descended.** The curve is non-monotone (§3.1), so a greedy
  descent stops at a local minimum.
- **Descending only**, so the term can only make an artifact smaller than
  today's; **ties to the largest K**, preserving the throughput default.
- **`MATERIALITY = 0.75`** — descend only for a ≥ 25 % saving.

**What it costs.** The ladder is up to five extra emissions, and only above the
threshold (7 of 2,487 patterns). Measured, best of one run each:

| pattern | default-K emission | full ladder | extra |
|---|---|---|---|
| K41 witness 1 | 0.59 s | 3.43 s | **2.84 s** |
| K41 witness 2 | 0.04 s | 0.22 s | 0.18 s |
| nested N=8 (corpus worst) | 0.01 s | 0.06 s | 0.05 s |
| `a(b\|c)+d` (ordinary) | 0.00 s | 0.01 s | 0.01 s |

The worst case in the project is 2.84 s of extra compiler time on a pattern
whose gcc compile it takes from **55.13 s to 1.02 s**. On the 99.72 % of the
corpus below the threshold the cost is zero emissions.

**What the rule does to every pattern above the threshold, and to both
witnesses.** Realized bytes; `ratio` = bytes(K_best)/bytes(K=8); `code` is
§4.2's quantity at the selected K:

| pattern | B(K=8) | B(best) | ratio | code(sel) | outcome |
|---|---|---|---|---|---|
| `((a)\|ab){4000}c` | 651,412 | 644,055 | 0.989 | 0 | K=8, unchanged |
| `((a)\|bc){0,4000}d` | 465,818 | 465,818 | 1.000 | 57,439 | K=8, unchanged |
| `((a)\|ab){0,4000}c` | 384,611 | 376,239 | 0.978 | 57,389 | K=8, unchanged |
| nested N=8 | 288,314 | 60,902 | **0.211** | 56,623 | **K=1** |
| nested N=6 | 225,862 | 60,902 | **0.270** | 56,623 | **K=1** |
| `((a)\|ab){0,2047}c` | 221,597 | 204,367 | 0.922 | 52,794 | K=8, unchanged |
| nested N=4 | 162,034 | 60,902 | **0.376** | 56,623 | **K=1** |
| **K41 witness 1** | 1,719,349 | 87,118 | **0.051** | 86,469 | **K=1** — gcc 55.13 s → 1.02 s |
| **K41 witness 2** | 1,220,606 | 1,114,780 | 0.913 | 836,621 | K declines → **REFUSED by §4's cap** |

Three things this table settles:

1. **The rule still reproduces the census's own hand-derived split with no
   nesting special case** — it selects on all three nested outliers and
   declines on all four table-dominated ones, because nesting reaches it only
   through what re-emission measures.
2. **Both K41 witnesses are handled, by DIFFERENT mechanisms, and that is the
   design.** Witness 1's size IS node replication, so K descent removes it
   entirely. Witness 2's size is its PREFILTER — 3,108 states and 34,188 jump
   entries against 552 VM nodes — which `K` cannot touch at all (K=1 saves
   8.7 %), so the materiality bar correctly declines it and the cap takes it.
3. **Separation is still wide**: selecting rows at 0.051–0.376, declining rows
   at 0.913–1.000, nothing in between.

**Witness 2's mechanism is not this row's to fix.** The hybrid prefilter's
inlined scan scaling with a bounded-repeat count is **[OPT-4]/K39**'s
mechanism; this row can PRICE it (the model now sees it) and REFUSE it (§4),
but shrinking it belongs to that row. Naming the owner is the point: a size
term that quietly grew a prefilter optimisation would be exactly the parallel
mechanism the project's standing rule forbids.

### 3.4 Where K must NOT descend

1. **An explicit `--unroll=K`.** The term never overrides a value the caller
   chose; `lib/pcrec.h` documents `unroll_k` as "A TUNING AXIS" and a tuning
   axis a size heuristic can silently overrule is not one.
2. **Below the threshold.** 99.72 % of the corpus, byte-identical.
3. **Below the materiality bar** — a small saving is not worth the census's
   measured (if small) throughput cost on single-level counts. Witness 2 is
   the case that matters: K=1 saves it 8.7 %, and taking that would trade a
   real (if unresolvable) throughput cost for a pattern the cap refuses
   anyway.
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
resolve. **Tightening it below 120,000 B requires that measurement first.**

---

## 4. The cap

### 4.1 Bytes, nodes and gcc cost are three different quantities — measured

The obvious reading of D45's consequence 1 is "cap the emitted bytes". The
first version refuted that and proposed a NODE cap instead. The panel then
refuted the node cap, with K41's second witness. Both refutations are right,
and together they say what the cap must actually bind on.

**Measurement 1 — the per-unit gcc costs.** `gcc -O2 -c`, this box, under
`scripts/watchdog`, `/usr/bin/time` rusage:

| unit | marginal gcc cost | derivation |
|---|---|---|
| a DATA table entry | **0.905 µs** | Δcpu 0.21 s over ΔE 232,000 (`a{1,2000}` → `a{1,31000}`) |
| a JUMP table entry | **8.7 µs** | Δcpu 0.160 s over ΔJ 18,446 (`jfit` n=800, k=2 → k=26, at fixed `N` and `S`) |
| a VM node | **5.37 ms** | Δcpu 6.48 s over ΔN 1,209 (nested family, `E` fixed at 844) |

A node costs gcc **≈ 5,930×** a data entry and **≈ 620×** a jump entry.
(The first version quoted "0.0009 µs per table entry" — a ms/µs slip, panel
finding F3. The corrected unit is 0.905 µs and the 5,930× ratio is unchanged.)

**Measurement 2 — what that does to real artifacts:**

| artifact | `.c` bytes | comment-excl. | N | S | E | J | gcc CPU |
|---|---|---|---|---|---|---|---|
| `a{1,31000}` | 1,380,303 | 1,367,865 | 0 | 0 | 248,520 | 0 | **0.34 s** |
| `a{1,25000}` | 1,116,303 | 1,103,865 | 0 | 0 | 200,520 | 0 | 0.24 s |
| `((a)\|ab){4000}c` | 675,586 | 651,412 | 80 | 0 | 128,544 | 0 | 0.29 s |
| nested N=8 (corpus worst) | — | 288,314 | 1,471 | 0 | 844 | 0 | 7.09 s |
| **K41 witness 2** | 1,261,948 | 1,220,606 | 552 | 3,108 | 320 | 34,188 | **66.92 s** |
| **K41 witness 1** | 2,015,585 | 1,719,349 | 7,467 | 0 | 128 | 0 | **55.13 s** |

**So a byte cap is wrong** (1.37 MB at 0.34 s and 1.22 MB at 66.92 s are the
same size and 197× apart in cost) **and a node cap is wrong too** (witness 2
has 552 nodes — fewer than 168 corpus patterns — and costs 6.7× the budget).

**A correction to the panel's premise, which strengthens its finding.** The
brief described witness 2 as compiling "inside the budget today, 7.8 CPU-s
against 10 s". That figure is at the fuzz harness's `-O0` default. **At `-O2` —
the level a user ships at, and the level every number in this note is measured
at — it costs 66.92 s CPU and 1.9 GB peak RSS**, i.e. 669 % of D45's budget.
K41's own entry records the same pattern for witness 1 (cheap at `-O0`, 52.9 s
at `-O2`) and says so in those words: gcc's outcome is "a CONSEQUENCE on a
given box", the artifact is the fact. So witness 2 is not a pattern the cap
would be refusing gratuitously — it is over budget by 6.7×.

### 4.2 The quantity that does separate them: CODE bytes

Subtract the measured table contribution from the artifact:

```
    code_bytes  =  B  −  5.070 · E  −  11.184 · J        (clamped at 0)
```

That is "the bytes gcc has to compile as control flow", as opposed to the
`.rodata` initialisers it emits nearly linearly. Measured, against gcc's own
cost:

| artifact | code bytes | gcc CPU | % of D45's 10 s |
|---|---|---|---|
| `a{1,25000}` | 87,229 | 0.24 s | 2 % |
| witness 1 **at K=1** | 86,469 | 1.02 s | 10 % |
| `a{1,31000}` | 107,869 | 0.34 s | 3 % |
| `((a)\|ab){4000}c` | ~0 | 0.29 s | 3 % |
| **nested N=8 — the corpus's worst** | **284,035** | 7.09 s | **71 %** |
| `jfit` n800_k26 | 319,517 | 3.21 s | 32 % |
| — *no measured artifact between 320 K and 837 K* — | | | |
| **K41 witness 2** | **836,621** | 66.92 s | **669 %** |
| **K41 witness 1** at K=8 | 1,718,700 | 55.13 s | 551 % |

**Everything at or below 320 KB of code costs ≤ 71 % of the budget; the next
measured artifact up costs 669 %.** The band between them is empty.

### 4.3 The cap, and where it fires

**`PCREC_MAX_VM_EMIT_CODE_BYTES = 500000`**, on the REALIZED code-byte count of
the selected emission.

- **In the empty band**: 1.76× above the corpus's worst (284,035) and 1.67×
  below the lowest refused artifact (836,621) — centred, so neither ordinary
  corpus growth nor measurement noise moves a pattern across it.
- **Refuses 0 of 2,487** corpus patterns; the largest code count among the
  seven above the threshold is 57,439.
- **Refuses K41 witness 2** (836,621 → 66.92 s) and would refuse witness 1 at
  K=8 (1,718,700), which the K rule has already reduced to 86,469.

Order:

```
    1.  emit at K_opt                     -- happens anyway
    2.  K selection (§3.3) if above the threshold  -- re-emission ladder
    3.  code_bytes of the SELECTED emission
    4.  if code_bytes > CAP  ->  ctx_fail, REFUSE
```

- **The cap reads a realized count, never `B̂`.** §2.5 measured the model
  under-predicting by up to 25 % at the tail; a refusal must not inherit that.
  By step 3 the emission exists and the count is exact.
- **K selection runs FIRST**, so the cap only ever sees what selection could
  not reduce — which is what makes witness 1 compile and witness 2 refuse.
- **An early refusal for the pathological case**: if the FIRST emission's
  realized code bytes already exceed **2 × CAP**, the ladder is skipped and the
  refusal is immediate. 2× is chosen because the largest K-descent saving
  measured anywhere is 19.7× on witness 1 — so this shortcut can in principle
  skip a pattern K would have rescued, and it is therefore set where no
  measured artifact sits: no artifact in the corpus, the `jfit` grid or either
  witness has code bytes between 836,621 and 1,718,700. **Stated as the
  approximation it is**, not as a free optimisation.
- **It cannot ship an uncompilable artifact**: the only outcomes at step 4 are
  refuse and emit-the-smallest-K, and step 2 has already found that.

### 4.4 The diagnostic

Joining the family `emit_vm.c` already uses (`"pattern too large: …"`, two
existing members, `ctx_fail(v->cx, 0, …)`):

> `pattern too large: the emitted matcher would contain %lld bytes of code
> (limit %d), which gcc cannot compile in reasonable time. A bounded repeat's
> body is replicated and repetition counts MULTIPLY through nesting -- lower a
> count, or reduce the nesting`

**D26 tier:** pcrec's own wording; PCRE2 has no emitted C and therefore no
analogous diagnostic, so there is nothing to match and no effort is spent
trying. `docs/spec/limits.md` gains the constant and the refusal in the same
change (D80).

### 4.5 The [SEL-1] interaction

`auto` selects DFA → the DFA overflows `PCREC_MAX_DFA_STATES_TABLE` → [SEL-1]
falls back to the VM → the VM's size trips the cap. **This is exactly K41's
own story** (its entry: "[SEL-1] is what UNHID it rather than caused it"), and
witness 1 is a live instance — its `RX_VM_PREFILTER` is `"none"` for precisely
this reason.

1. **The user must not be told the wrong story.** The diagnostic above names
   repetition counts and nesting; after a DFA-overflow fallback the real story
   is "this pattern needed a DFA, the DFA overflowed, and the VM fallback is
   too large". So **when `RX_ENGINE_WHY`'s reason is a fallback, the cap's
   diagnostic appends it.** Without that the message is actively misleading on
   the path most likely to reach it.
2. **The fallback cannot bypass the cap** — it is checked on the VM path
   however that path was reached, and there is no third engine. The result is a
   refusal, which is the correct outcome and is what D45's consequence 1 asks
   for.

### 4.6 Three corrections carried from r40, recorded rather than absorbed

- **F3 (unit).** The first version's "0.0009 µs per table entry" was a ms/µs
  slip; the measured value is **0.905 µs/entry** (Δcpu 0.21 s over ΔE 232,000).
  The 5,930× node-to-entry ratio it supported is unchanged — the slip was in
  the printed unit, not in the ratio.
- **F4 (population).** "DFA only … max 35.29 %" was the 4th-worst row; the
  DFA maximum under the two-term model is **35.35 %** (`a\bb`), which is also
  the global maximum. §2.4 now reports the four-term model's 33.65 %.
- **F2 (residual range), and why the curve it belongs to is GONE.** The first
  version quoted the gcc log-log fit's residuals as "−20 % … +18 %", omitting
  the three mixed `alt` points that are in the fitted population; the true
  range over those 20 points is **−43.3 % … +18.3 %**. That fit
  (`gcc_cpu ≈ 0.00054 · N^1.269`) was the derivation of the NODE cap, and the
  node cap is withdrawn — §4.2 derives the cap from a measured separation
  between two populations instead of from an extrapolated curve, precisely
  because a curve with a −43 % residual is not something a refusal should rest
  on. The fit and its data stay in `artsize_impl/gccfit.tsv` as the evidence
  for §4.1's per-unit costs, which is all they are now used for.

### 4.7 What this does to K41's pinned bucket (panel item 4)

`tests/fuzz/fuzz.py` classifies "K41 oversize artifact" by emitted `.c` size
alone (`K41_OVERSIZE_BYTES = 1_000_000`), and
`tests/fuzz/run_capturediff_gate.sh` pins that bucket at **exactly 2** — the
two witnesses. This design moves it to **0**, by two different routes:

- **witness 1 leaves by shrinking**: the K rule takes it to 87,118 B, an order
  of magnitude below the 1,000,000 B classifier;
- **witness 2 leaves by refusing**: no artifact is emitted, so there is nothing
  to classify.

K41's own text says a movement to 0 "means neither witness reaches its shape
any more (K41 closed, or the generator/seed changed — **re-derive, do not
silently widen**)". So the landing change owes, in the same commit: the bucket
re-pinned to 0 with this note cited, the three counts K41 records as
arithmetically coupled to it re-derived (both-accept 181, subject pairs 2,715,
oracle-inconclusive 0 — witness 1 now re-enters the ordinary compare pipeline,
witness 2 becomes a refusal), and **K41 itself closed or re-scoped**, since its
stated fix direction ("a VM-side emitted-PROGRAM-SIZE cap in
`src/core/limits.h`, refusing before emission") is what §4.3 builds.

**One honest wrinkle, flagged rather than buried:** §4.3 refuses *after* the
selected emission, not "before emission" as K41's fix direction words it. The
compiler still does its own work (0.04–3.4 s); what is never paid is gcc's
(55–67 s). §2.2 explains why — there is no pre-emission node count to refuse
on — and the early refusal at 2× CAP recovers the "before emission" property
for the pathological case only.

---

## 5. The three levers, priced and all three DECLINED

Census §7 named three candidates from the manager's line-kind attribution of
the witness and explicitly left them unpriced against the corpus. They are now
priced. Method: a measurement-only subagent, read-only, over the witness, 12
of census §4's top outliers (population B), and a reproducible 200-pattern
sample of corpus patterns (seed 20260828; 120 landed on the VM engine and were
measured, 62 on DFA, 18 refused) — population C. load1 0.08–0.26 throughout.

Classifier and data archived at `artsize_impl/levers/` (panel finding F7 —
the first version quoted these numbers with nothing committed to check them).

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
**AR3 — why the K sweep is a hand-written one-off, and what it waits for.**
`--unroll` is a **VALUE** axis, not a `PCREC_(NO|FORCE)_*` predicate bit, and
`src/parse/axes_dump.c` has no `kind=value` support — so the axis registry
cannot describe it and `make test-axes` cannot derive it. [CHK-2] item (c),
"test-axes-from-dump", is the row that would fix that, and it is **not built**.
So: the K sweep ships NOW as a standalone check and is the gate; `--unroll` is
registered as a value axis when [CHK-2] (c) is built, and **this row is that
item's named trigger** (D77 — the measured need, recorded where the trigger
fires rather than built ahead of it).

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
tuning.md` gains a §2.15 in **§2.14**'s deny-only shape (`-fno-offset-skip`,
bit 16 — the closest precedent, panel finding AR11), and §2's count moves
from fourteen to fifteen.

It denies **the K selection only**, never the cap (§10 Q2).

**The D80 spec hunks, complete** (panel findings AR1/AR2 — the first version's
list was short by two):

| # | file | hunk |
|---|---|---|
| 1 | `docs/spec/tuning.md` | new §2.15 in §2.14's deny-only shape; §2's count fourteen → fifteen |
| 2 | **`docs/spec/cli.md:218-224`** | the hand-enumerated `-fno-` axis list, which runs through `-fno-offset-skip` and must gain `-fno-size-term` |
| 3 | **`docs/spec/match_api.md` §6.3** | a per-mechanism bullet for the two macros, on the `_DFA_SCAN`/`_DFA_PREFILTER` precedent at `match_api.md:1659-1720`, scoped VM-artifact-only |
| 4 | `docs/spec/match_api.md` §6 | the `abi` sentences, 9 → 10 (§8) |
| 5 | `docs/spec/limits.md` | `PCREC_MAX_VM_EMIT_CODE_BYTES`, its value, and the refusal (§4.4) |

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
| — | *(and see AR3 below on why the K sweep is a one-off today)* | |
| 4 | structural check | `tests/codegen/run_size_term.sh` — reads the ARTIFACT (the emitted body-copy count against the stamped K, and that the stamp's `_WHY` matches which path ran), never the stamp alone |
| 5 | sabotage row | `tests/mech/` — the ladder reduced to a greedy descent (must be caught by the non-monotone subject, §3.1); the materiality bar removed; the cap's comparison inverted |

Sabotage row 1 is the one worth naming: a greedy descent passes every
answer-identity check ever written, because it is answer-identical. Only a
SIZE assertion on the non-monotone subject can see it.

---

### 7.5 What K selection does to [ART-SIZE.1b]'s size log and tripwire (AR4)

The tripwire (`tests/size/check_size_tripwire.sh`) pins the corpus's worst
logged artifact at **1,400,000 B** and its worst gcc CPU at **8.0 s**, against
a measured baseline max of 651,344 B and 5.462 s. K selection moves three
corpus rows DOWN (288,314 → 60,902 B and the two smaller nested outliers), so
**headroom grows and neither pin is affected** — the largest logged artifact is
unchanged at 651,344 B, since `((a)|ab){4000}c` is a declining row. The pins
stay where they are; a design that shrinks the tail must not be the reason a
blowup detector is loosened.

`docs/dev/artifact_size_log.tsv` is regenerated on `main` in the landing
change, and **`scripts/size_diff`'s output is a delivery number**: exactly
three rows may move, each downward, and every other row must differ by at most
the two stamp lines' constant.

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
| 1 | **K41 witness 1** | K=1 selected; 1,719,349 → 87,118 B, ≤ 30 KB `.o`, ≤ 1.1 s gcc (census: 28,104 B, 1.015 s) | must not exceed either |
| 1b | **K41 witness 2** | K DECLINED (ratio 0.913); **REFUSED** by the cap at 836,621 code bytes | exact — it must refuse, and name the fallback reason (§4.5) |
| 2 | nested N=8 / N=6 / N=4 | K=1 selected; comment-excluded 288,314 → 60,902 B (−78.9 %), 225,862 → 60,902 (−73.0 %), 162,034 → 60,902 (−62.4 %); `.o` 75–79 % smaller (census §8) | ±5 % on the byte figures |
| 3 | the four declining patterns above the threshold | K unchanged at 8; **`.o` byte-identical**; source differs by exactly the two stamp lines | exact |
| 4 | D82 zero cost | ≥ 4 declined patterns, both engines, **objdump 0 differing instructions** vs a `main`-built compiler | exact |
| 5 | the corpus size log | regenerated on `main`; **exactly the 3 selecting patterns move**; every other row differs by exactly the stamp constant | exact |
| 6 | the cap | 0 of 2,487 corpus patterns refused; largest corpus code count 57,439 against a 500,000 cap | exact |
| 6b | **K41's fuzz-gate bucket** | 2 → **0**, re-pinned with the three coupled counts re-derived (§4.7) | exact |
| 6c | the instrument | `measure.py`'s byte column agrees with `size_count.sh` on every pattern it is run against, both artifact forms | exact — the control §2.0 did without |
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
2. **The cap is not deniable** (§7.2). `-fno-size-term` denies the K
   selection but not the refusal. This is a ruling — a safety refusal a flag
   turns off is not one — with a real cost: a user who wants a 5-minute gcc
   compile cannot have one, and their only recourse is to change the pattern.
   Frank's call.
3. **CLOSED by r40 AR10** — the threshold is 120,000, not 131,072; the
   collision was worse than the first version said
   (`PCREC_MAX_VM_REPLICATION_PRODUCT` is a literal alias of
   `PCREC_MAX_VM_NODES`), and the note's own costless fix was taken (§3.2).
3b. **The cap's 500,000 sits in an EMPTY measured band** (§4.2): the highest
   admitted artifact is 320 KB of code and the lowest refused is 837 KB, with
   nothing measured between. So any value in roughly (330,000, 830,000) gives
   identical behaviour on everything measured — 500,000 is centred in that
   band, which is a judgement, not a measurement, and is stated as one. The
   band is 2.6× wide; narrowing it needs an artifact nobody has written.
4. **`a{1,25000}`-shaped artifacts are left alone** (1.10 MB comment-excluded, gcc 0.24 s).
   They are large for a user to ship and cheap for gcc to compile, so neither
   §3 nor §4 touches them: the K rule sees a K-insensitive `N` and the cap is
   not about bytes. If Frank's concern is the SHIPPED SIZE rather than the
   compile budget, this is the population that answers it, and the instrument
   would be a third mechanism (a byte-based *warning*, or a table-form
   selection) that this note does not propose. **Flagged because the row's
   founding quote is about size, not compile time.** r40 AR9 rules this real
   but outside the row as chartered — a shipped-size instrument would be a new
   row.
5. **Witness 2's mechanism belongs to [OPT-4]/K39, not here** (§3.3). This row
   PRICES the hybrid prefilter's inlined scan (the model now sees its states
   and jump tables) and REFUSES it past the cap; it does not shrink it. If
   Frank wants that population made compilable rather than refused, [OPT-4] is
   the row and this note's §4.2 numbers are its measured need.

---

## 11. What STEP 2's code phase builds

1. The realized-count instrumentation the selection and the cap both read
   (§2.2): the emitter already knows which bytes it is writing into a table
   literal, so `code_bytes` is an accumulator, not an analysis. The model of
   §2.3 ships only as the early-refusal shortcut (§4.3) and as this note's
   cost function; integer arithmetic, nothing rounding to zero at any corpus
   magnitude (r39 S-D5).
2. The K selection (§3.3) as a RE-EMISSION ladder at the one site that
   resolves `v.unroll_k` (`emit_vm.c:7461`) — no counting walk, no second
   traversal to keep in sync with the emitter.
3. The code-byte cap (§4.3) and its diagnostic (§4.4), plus
   `docs/spec/limits.md`.
4. The two stamps (§7.1), the deny flag (§7.2), the registry re-pin (§7.3).
5. The `abi` bump, four sites (§8).
6. The checks: structural, sabotage, the K sweep, the byte-identity control
   (§6.2, §7.4).

It does **not** build any of census §7's three levers (§5), per-quantifier K
(§5.4, [ENG-CLAMP]'s), or any table-form change (§10 Q4).
