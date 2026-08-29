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

## 0. The answer in twelve lines

1. **The r40 panel and its re-check refuted this note FOUR times, and the
   refutations are the most useful thing in it.** The instrument was blind to
   the hybrid prefilter's computed-goto machinery, so a pinned oversize pattern
   read 10× small and no mechanism engaged (§2.0, F1). The pre-emission node
   count the design assumed **does not exist** (§2.2a, S1/F6). "Every K is
   answer-identical" is false on the give-up surface (§6.1, S2). And **the
   ladder as first specified would have broken a pattern that compiles today**
   (§2.2b, R1) — the blocker, because `ctx_fail` is a `longjmp` and a trial
   cannot be "discarded".
2. Emitted size is described by **four** counts: VM nodes `N`, prefilter DFA
   states `S`, data-table entries `E`, and computed-goto **jump-table entries
   `J`** (§2.3). Median error 2.39 % over 2,487 corpus artifacts, 2.56 % above
   100 KB, −8.8 % and −23.2 % on the two K41 witnesses.
3. **The size a user ships and the cost gcc pays are different quantities.**
   Measured: a data entry costs gcc **0.905 µs**, a jump entry **8.7 µs**, a VM
   node **5.37 ms** — a node is ~5,930× a data entry. `a{1,31000}` is 1.38 MB
   and compiles in **0.34 s**; K41 witness 2 is 1.26 MB and costs **66.92 s**.
4. So D84 rules the charter's one cap into **two**: a **code-bytes cap** for
   D45's compile budget, and a **total-bytes cap** for usability — "a large
   byte count makes the artifact unusable" — which is **not** a proxy for
   compile time (§4.0a). `a{1,31000}` is why they are SEPARATE, not why either
   is wrong: 1.37 MB, gcc 0.34 s — cheap to compile, too large to ship.
5. The **total-bytes cap reads no model**: an exact post-emission check on the measured
   bytes, refusing **before the file is written** (D84 addendum). Predictable by
   construction — a fixed number and a loud refusal — which is the half Frank
   called worse than the size itself.
6. The **K rule**: above a threshold, `K` is chosen by DRY-EMITTING the ladder
   `[8,6,4,3,2,1]` and taking **`argmin N`, exact, with no model in it** (§3.3,
   S4). Both `N` and bytes are **non-monotone in K**, so it is evaluated, never
   descended.
7. It re-emits because **there is no pre-emission node count**, and a counting
   pre-pass would be a third party to an agreement the emitter's own header
   warns about (§2.2a). **The re-emissions are ATTEMPTS in `compile_driver`'s
   existing retry loop** — the shape [SEL-1] built a day earlier and the one
   `internal.h:1469` prescribes — which is why R1 needs no trial flag (a
   trial's `ctx_fail` is discarded at the one recovery point, the only place
   that can), R2's arena question dissolves (`job_cleanup` `arena_free`s per
   attempt) and R3's hazard cannot arise (each attempt re-parses). What remains
   is the EARLY ABORT (§2.2c — the ladder otherwise writes 55.4 MB on a
   worst-rung tower to select a 42,619-byte artifact) and the re-emission
   IDENTITY CONTROL that replaced R3's sabotage (§2.2d). Measured in-process:
   0.78 s on the worst pattern in the project.
8. **A cap refuses only if NO K on the ladder is under it** (§4.4, S5), and a
   K taken that way is stamped `cap-rescue` (R5). The materiality bar gates a
   THROUGHPUT preference, so without step 4 a declined bar could strand a
   pattern a lower K rescues — measured on witness 2, whose byte ratio 0.913
   declines the bar despite an 81 % node reduction.
9. **Both K41 witnesses are handled, by different mechanisms** (§4.8): witness
   1's size IS node replication, so the K rule takes it 2,015,585 → 116,371 B
   and gcc 55.13 s → 1.02 s; witness 2's is its PREFILTER, which K cannot touch,
   so **both** caps refuse it (code 670,650; total 1,220,606). **K41's pinned
   bucket moves 2 → 0**, one fixed
   and one refused — and witness 2 stays refused until **[OPT-4]/K39** shrinks
   the mechanism, which is that row's job, not this one's.
10. **Thresholds and caps:** threshold **120,000 B** (AR10 — the first
    version's 131,072 collided with a literal alias); **code-bytes cap
    500,000** (Frank, D84 addendum 2 — "then 500k is fine"); **total-bytes cap
    1,000,000**. Every one is comment-excluded emitted C SOURCE bytes, and the
    `.o` is ≈ 17 % of that — ≈ 20 KB / 85 KB / 170 KB respectively, quoted
    beside each constant so the limit reads in the unit a user ships.
    **0 of 2,487** corpus patterns refused by either, on all ten axes (worst
   code 283,083 = 1.77× headroom; worst total 651,415 = 1.54×). The **node cap
   an earlier pass proposed is DROPPED** (§4.2a): nodes are subsumed by code
   bytes and miss the CFG-shaped cost — witness 2 is 552 nodes and 66.92 s.
11. **Both caps are EMERGENCY FAILSAFES, not tuned thresholds** (D84 addendum
    3 — a gap-centred 850,000 was offered for the total cap and not taken:
    *"more of an emergency failsafe than a tuning"*). They are **NOT deniable
    but ARE overridable upward** (ruling 1), and **the place a real build
    raises one is the pattern-source file's `config` block**, per target and
    beside the pattern — the CLI flags serve the single-pattern case and the
    harness. Predictability is discharged by documentation: `limits.md` gains
    a "Handling an oversized artifact" section, drafted in §4.6.
12. **All three of census §7's levers are DECLINED** on measurements (§5; the
    best is worth a corpus median of 0.99 %), and `--unroll` is a VALUE axis so
    **no gate proves any K answer-identical today** — the new K sweep is that
    gate, and it EXCLUDES `budget`/`gu` cells by construction because §6.1
    measured them to be genuinely K-dependent (§6.2).

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

### 2.2 The inputs, and the mechanism the ladder needs (F6/S1, R1, R2, R3)

| input | what it is | where it comes from |
|---|---|---|
| `N` | VM nodes — one per `rx_L<N>:` label | **nowhere before emission — §2.2a** |
| `S` | prefilter DFA states — one per `rx_s<N>:` label (computed-goto form: `RX_DFA_SCAN "attempt"`, `RX_DFA_TABLE "none"`) | the DFA builder's state count |
| `E` | declared entries in DATA tables | `states × ncls`, bounded by `PCREC_MAX_TABLE_ENTRIES` |
| `J` | declared entries in POINTER tables (`static const void *const rx_targets_N[…]`) | `S × ncls` |

#### 2.2a There is no pre-emission node count

Every candidate source fails, and the first version asserted two of them:

- `vm_count_slots` (`emit_vm.c:2314`) **returns void** and accumulates SLOT
  categories plus `maxcopies` — not nodes;
- `Vm.nodes` (`:433`) is bumped only by `vm_charge` (`:692-696`) **during**
  emission (`:2304` and `limits.h:218-220` say so verbatim);
- `v.nlabel` is incremented by `vm_label()` during emission (`:690`);
- the pre-pass **mutates `v`**, can fail, and runs at `:7655` — ~200 lines
  after the `v.unroll_k` site at `:7461`.

**A counting pre-pass is rejected.** It would have to mirror
`vm_counter_fits`' K-dependence (S3), possessification, revdet, splice and the
MRL guard — a third party to the two-way agreement `vm_count_slots`' own header
warns about, with a silently-wrong count feeding a refusal as its failure mode.

**So the ladder DRY-EMITS**: `pcrec_emit_vm` run into a scratch buffer from
`src/core/compile.c:426`, its single call site. It cannot drift from the
emitter because it **is** the emitter. But dry emission is not free-standing —
it needs three things the emitter does not have today.

#### 2.2b How a trial fails — SUPERSEDED BY THE IMPLEMENTATION (R1)

**What r40 signed off, and why it is not what shipped.** The design this
section carried specified a `trial` flag threaded into five size guards so
they RETURN `OVER(which, value)` instead of `ctx_fail`-ing, because
`ctx_fail` ends in `longjmp` to the compiler's ONE recovery point
(`internal.h:1469-1475`) and a trial's failure would otherwise unwind past the
ladder and become the compile's answer. The BLOCKER that reasoning rests on is
real and is measured below. The MECHANISM is not what the code needed.

**What the implementation found.** `compile_driver` **already is** a retry loop
of exactly the required shape, built a day earlier by [SEL-1] for the same
reason: `compile.c`'s `for (volatile int attempt = 0; attempt < COMPILE_MAX_
ATTEMPTS; attempt++)` calls `setjmp` INSIDE the loop, re-entered fresh each
iteration, carrying state across attempts in `volatile` locals and a survived
copy (`overflow_why`, copied out precisely because `job_cleanup` has already
`arena_free`d the dead attempt).

**So the ladder is ATTEMPTS in that loop**, and three things follow:

- **R1 needs no trial flag and no change to any guard.** A ladder attempt's
  `ctx_fail` — for ANY reason: the node cap, the replication product, a
  repeat-copies refusal, the scratch abort — lands in the EXISTING recovery
  point, and the loop's own "should I retry?" decision records that K as out
  and moves to the next. A trial's refusal is discarded at the only place that
  CAN discard it. `internal.h:1469`'s own prescription is literally this shape:
  *"report as a RESULT the existing fixpoint consumes … a ONE-SHOT RETRY of the
  whole pipeline rather than a second recovery point"*.
- **R2's arena question dissolves** (§2.2c): `job_cleanup` ends in
  `arena_free` and runs on every retry path, so trials share nothing.
- **R3's hazard cannot arise** (§2.2d): each attempt re-parses, so the AST an
  emitter run annotates is a fresh one.

**The blocker is still real, and it is now a test cell.** Measured,
`--engine=vm`:

```
(?:(?:(?:(?:(?:(?:a|b){41}){41}){41}){41}){41}){41}
    K=8  COMPILES            (N = 118,098)
    K=6  REFUSES  "pattern too large (VM exceeds 131072 emitted nodes)"
```

A ladder that let a trial's refusal escape would make a pattern that **compiles
today** refuse, citing a limit its own artifact never reached, at a K the user
never asked for. §9 row 9 pins it.

**The retry composition, in one order.** [SEL-1]'s DFA-overflow retry decides
the ENGINE and always resolves first — it is a property of the pattern, not of
K. The ladder then runs, and only on the VM. `--unroll=K` given, the deny flag
set, a DFA artifact, or a size below the threshold: no ladder attempts at all.
If no ladder K passes both caps, the FINAL attempt re-emits the DEFAULT so the
refusal quotes the figures the caller's own options produce, never the last
rung the ladder happened to try.

**`COMPILE_MAX_ATTEMPTS` is DERIVED** — `2 + SIZE_TERM_LADDER_N + 1`, from the
ladder's own definition — so adding a rung cannot silently truncate the search.

#### 2.2c The early abort (R2)

**The ladder's cost is bounded by its WORST rung, and K=6 is routinely the
worst** — `vm_counter_copies`' mandatory `K + m%K` term is non-monotone.
Measured on `{17}` towers, `--engine=vm`, raw emitted bytes:

| tower | K=8 | **K=6** | K=4 | K=3 | K=2 | K=1 |
|---|---|---|---|---|---|---|
| 5-deep | 1,749,937 | **3,135,570** | 346,163 | 345,919 | 109,579 | 41,491 |
| 6-deep | 16,252,391 | **35,511,862** | 1,647,486 | 1,638,076 | 265,236 | **42,619** |

Unbounded, the 6-deep ladder writes 55.4 MB of scratch to discover that the
answer is 42,619 bytes.

**What shipped:** `StrBuf.abort_over`, checked in `sb_grow` — the ONE place a
buffer's length grows, so no append path can miss it — armed only on a LADDER
attempt. The DEFAULT and FINAL attempts leave it zero and always run to
completion, because their figures are what a refusal quotes.

**The factor is 3 and it is DERIVED, not chosen.** The bound is on RAW bytes
(what a `StrBuf` knows) while the cap is on comment-excluded bytes, so aborting
too early would discard a K that would in fact have fitted. Measured over the
2,487-artifact corpus, prose is at most **47.8 %** of raw emitted bytes (median
43.7 %), so comment-excluded ≥ 0.52 × raw and **raw > 1.92 × cap already
implies over-cap**. 3× leaves margin for an emitted form more comment-heavy
than anything measured: a trial aborted at 3× would need its artifact to be
two-thirds prose to have been viable.

#### 2.2d Re-emission and the shared AST (R3 — dissolved, and what replaced it)

R3 found that `pcrec_emit_vm` annotates the AST it is handed
(`a->u.call.nonnullable` at `:5691`; `a->u.call.save`/`.nsave` at `:5726-5727`,
pointers into THAT run's arena) and that repeated emission was benign only
because every publisher happens to precede its readers within a run — a
property nothing stated and nothing checked.

**As attempts, the hazard cannot arise**: every attempt re-parses, so each
emitter run gets a FRESH AST and there is no previous run's annotation to read.
The proposed sabotage (moving `vm_publish_saves` after `vm_cost`) would test a
property the mechanism no longer depends on.

**What replaced it is a stronger check, because it tests the conclusion rather
than one route to it** (the manager's condition 2): the FINAL attempt asserts
that re-emitting the chosen K reproduces the ladder's recorded figures for that
K — node count exactly, and bytes exactly once each side's own
`_UNROLL_K_WHY` string length is subtracted. Any state leaking across attempts,
by any route, moves one of those numbers.

**It earned itself on its first run.** Un-adjusted it fired on K41 witness 1
with a 3-byte delta — exactly `strlen("size-model") − strlen("default")`. A
ladder trial stamps `"default"` because the decision has not been made yet, and
the final attempt stamps the verdict, so the trial had been measuring an
artifact three bytes smaller than the one that ships. The fix is to subtract
the known term on both sides rather than to add a tolerance: a tolerance would
have hidden this AND would hide a real leak of the same size.

#### 2.2e What this buys, and what it cost

The selection and both caps consume EXACT counts from an emission that has
already happened, so the model's 7–25 % tail error (§2.5) reaches neither.

**Measured IN-PROCESS, with the abort on** (the figures elsewhere in this note
are separate-process runs — a bound, not a measurement):

| pattern | wall | peak RSS | result |
|---|---|---|---|
| an ordinary pattern (the term never runs) | 0.13 s | 9 MB | unchanged |
| K41 witness 1 (ladder runs, takes K=1) | **0.78 s** | 30 MB | 116,380 B; gcc 55.13 s → ~1 s |
| the 6-deep `{17}` tower (worst rung) | **0.75 s** | 64 MB | 42,619 B |

The ladder's marginal cost on the worst pattern in the project is about
**0.65 s** of compiler time, against a gcc compile it takes from 55 s to 1 s.

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

### 3.1a Why the ladder is `argmin N(K)` and not `argmin B̂` (finding S4)

The first version reported that the model picks the byte-optimal K on 15 of 15
subjects and offered it as validation. **critic-sem showed the test cannot
fail**: `E` is built from the AST and is constant in `K`, `S` and the intercept
are constant in `K`, so

```
    argmin_K B̂(K)  ≡  argmin_K N(K)      for any positive node coefficient
```

The 15/15 therefore validates that **`N` ranks bytes**, which is worth knowing
and is not nothing — but it is not evidence about the fitted model, and quoting
it as such was the first version's error.

**So the ladder is specified as `argmin N(K)`, exact, with no model in it** —
and §2.2's dry emission supplies that `N` directly. What the fitted model of
§2.3 remains load-bearing for is exactly two things, and they are both
thresholds rather than choices:

- the **threshold gate** (§3.2) — does this artifact deserve a ladder at all;
- the **materiality bar** (§3.3) — is the best K's saving worth taking.

Nothing else in the design reads `B̂`.

**`N` is non-monotone in `K`, which is why the ladder is evaluated rather than
descended** — measured on three families:

| subject | K=8 | K=6 | K=4 | K=3 | K=2 | K=1 |
|---|---|---|---|---|---|---|
| K41 witness 1 | 7,467 | 6,407 | 3,234 | **3,248** | 1,364 | 313 |
| nested, 4 levels | 2,936 | **2,960** | 1,592 | **1,952** | 990 | 530 |
| K41 witness 2 | 552 | 552 | 558 | **566** | 387 | 105 |

Every bolded cell is larger than the K to its left. A greedy descent stops at
the first of them.

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
        for K_c in LADDER = [8,6,4,3,2,1]:
            DRY-EMIT into a scratch buffer (§2.2); read exact N and bytes
        K_best = argmin N(K_c) , ties -> the LARGEST such K
        if  bytes(K_best) <= MATERIALITY * bytes(K_opt):  keep K_best's emission
        else:                                             keep K_opt's
```

- **The ladder runs only when the COUNTER rung is live**, and that is a
  structural fact rather than a heuristic: `K` is the counter rung's chunking
  factor and affects nothing else, so an artifact that never took that rung is
  byte-identical at every `K`. The emitter already computes the rung mask and
  already stamps it (`<PREFIX>_VM_RUNGS`); the term reads bit 0x10 of it.
- **The threshold is on CODE bytes, not on the total**, for the same reason one
  level up: `K` moves code and cannot move a table by a byte, so gating on
  total size would run the ladder on artifacts it provably cannot shrink. The
  corpus's largest artifacts are exactly that shape — `((a)|ab){4000}c` is
  651,540 bytes of which 32,428 are code.
- **The ladder is `argmin N`, exact, with no model in it** (§3.1a, finding S4).
  §2.2's dry emission supplies `N` directly; the fitted model is load-bearing
  only for the THRESHOLD above and the MATERIALITY bar below.
- **Evaluated, not descended.** Both `N` and bytes are non-monotone in K
  (§3.1, §3.1a), so a greedy descent stops at a local minimum.
- **Ties to the largest K**, preserving the throughput default.
- **`MATERIALITY = 0.75`** — descend only for a ≥ 25 % byte saving. The bar
  gates a THROUGHPUT preference and nothing else; finding S5's point is that a
  cap must not inherit its verdict, which is what §4.4's ladder re-run closes.
- **No `K_c <= K_opt` guard** (finding S10): the ladder runs only when
  `--unroll=` was NOT given, so `K_opt` is always the default 8 and every
  ladder value is already ≤ it. The guard the first version wrote was
  unreachable; if it is kept in the code it is marked defensive, not load-bearing.
- **A trial NEVER fails by `longjmp`** (§2.2b, finding R1): under the `trial`
  flag the size guards return `OVER(which, value)`, the ladder consumes it, and
  a trial's refusal is never the compile's answer. The first version said a
  failing trial was "discarded", which was false and would have broken a
  pattern that compiles today.

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
witnesses.** All figures are comment-excluded emitted C source bytes (§4.0).
`B` is the whole artifact — the threshold's, the bar's and the total-cap's
quantity; `code` is §4.2's. The byte ratio is what the materiality bar reads.

| pattern | B(K=8) | B(best) | byte ratio | code(sel) | B(sel) | outcome |
|---|---|---|---|---|---|---|
| `((a)\|ab){4000}c` | 651,412 | 644,055 | 0.989 | 32,300 | 651,412 | K=8, unchanged |
| `((a)\|bc){0,4000}d` | 465,818 | 465,818 | 1.000 | 25,693 | 465,818 | K=8, unchanged |
| `((a)\|ab){0,4000}c` | 384,611 | 376,239 | 0.978 | 33,359 | 384,611 | K=8, unchanged |
| nested N=8 | 288,314 | 60,902 | **0.211** | 55,668 | 60,902 | **K=1** |
| nested N=6 | 225,862 | 60,902 | **0.270** | 55,668 | 60,902 | **K=1** |
| `((a)\|ab){0,2047}c` | 221,597 | 204,367 | 0.922 | 42,217 | 221,597 | K=8, unchanged |
| nested N=4 | 162,034 | 60,902 | **0.376** | 55,668 | 60,902 | **K=1** |
| **K41 witness 1** | 1,719,349 | 87,118 | **0.051** | 86,194 | 87,118 | **K=1** — gcc 55.13 s → 1.02 s |
| **K41 witness 2** | 1,220,606 | 1,114,780 | 0.913 | 670,650 | 1,220,606 | bar declines; §4.4 step 4 finds **no ladder K under either cap** → **REFUSED** |

Every corpus row clears both caps by a wide margin — largest `code` 55,668
against 500,000, largest `B` 651,412 against 1,000,000. Witness 2 is refused by
**both** caps at **every** K on the ladder, which is why §4.4 step 4 cannot
rescue it and why the refusal is the right answer rather than a missed
selection.

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

## 4. The two caps (D84)

### 4.0 The unit, stated once and repeated beside every constant

**Every size constant in this row is bytes of the EMITTED C SOURCE,
comment-excluded** — `tests/lib/size_count.sh`'s definition, the quantity
`docs/dev/artifact_size_log.tsv` already logs (D84 addendum 2). The `.o` a user
actually links is **≈ 17 %** of it (r = 0.99, census §5), so each constant is
quoted with its `.o` equivalence, because the limit should read in the unit a
user ships:

| constant | value | ≈ `.o` |
|---|---|---|
| `PCREC_SIZE_TERM_THRESHOLD` (§3.2) | 120,000 | ≈ 20 KB |
| `PCREC_MAX_VM_EMIT_CODE_BYTES` (§4.2) | 500,000 | ≈ 85 KB |
| `PCREC_MAX_EMIT_BYTES` (§4.3) | 1,000,000 | ≈ 170 KB |

### 4.0a Why TWO caps

D84 ruling 2 splits the charter's single "hard emitted-size cap", because this
note's own measurements showed the question is two questions:

| cap | bounds | because | how it is checked |
|---|---|---|---|
| **code-bytes cap** | `B − 5.070·E − 11.184·J` — the bytes gcc compiles as CONTROL FLOW | **D45's compile budget.** gcc's cost is superlinear in code and nearly linear in table data | on the ladder-chosen emission |
| **total-bytes cap** | the whole comment-excluded artifact | **usability.** "A large byte count makes it unusable" — a concern in its own right, NOT a proxy for compile time | an EXACT post-emission check, refusing **before the file is written** |

**`a{1,31000}` is why they are separate, not why either is wrong.** It is
1,367,865 bytes and gcc compiles it in **0.34 s**: cheap to compile, too large
to ship. The code-bytes cap correctly passes it (11,655 code bytes); the
total-bytes cap correctly refuses it. A single cap would have to get one of
those two answers wrong.

**Neither cap reads the model.** The code-bytes quantity is computed from the
realized emission's own counts, and the total-bytes cap is a plain byte count
(D84 addendum). §2's fitted model survives only for the K rule's threshold and
materiality bar (§3.1a).

### 4.1 Bytes, code and gcc cost are three different quantities — measured

**Measurement 1 — the per-unit gcc costs.** `gcc -O2 -c`, this box, under
`scripts/watchdog`, `/usr/bin/time` rusage:

| unit | marginal gcc cost | derivation |
|---|---|---|
| a DATA table entry | **0.905 µs** | Δcpu 0.21 s over ΔE 232,000 (`a{1,2000}` → `a{1,31000}`) |
| a JUMP table entry | **8.7 µs** | Δcpu 0.160 s over ΔJ 18,446 (`jfit` n=800, k=2 → k=26, at fixed `N` and `S`) |
| a VM node | **5.37 ms** | Δcpu 6.48 s over ΔN 1,209 (nested family, `E` fixed at 844) |

A node costs gcc **≈ 5,930×** a data entry and **≈ 620×** a jump entry.
(The first version quoted "0.0009 µs per table entry" — a ms/µs slip, panel
finding F3. The corrected unit is 0.905 µs; the ratio is unchanged.)

**Measurement 2 — what that does to real artifacts.** The full table, with the
CODE column that decides the cap, is **§4.2**; the two facts it turns on are:

- `a{1,31000}` is **1,367,865 bytes and compiles in 0.34 s**;
- **K41 witness 2 is 1,220,606 bytes and costs 66.92 s** — 669 % of D45's
  budget.

Same order of size, **197× apart in cost**. Whatever the caps bind on, it
cannot be total bytes alone (that would refuse the first) and it cannot be
nodes (witness 2 has 552 of them). §4.2 is the quantity that separates them.

**A correction to the brief's premise, which strengthens the case.** Witness 2
was described as compiling "inside the budget today, 7.8 CPU-s against 10 s".
That is the fuzz harness's **`-O0`** default. At **`-O2`** — the level a user
ships at, and the level every number here is measured at — it costs **66.92 s
CPU and 1.9 GB peak RSS**. K41's own entry records the same `-O0`/`-O2` split
for witness 1.

### 4.2 The quantity: CODE bytes, exact and emitter-counted

```
    code_bytes  =  comment-excluded emitted bytes  OUTSIDE table initializers
```

**Exact, not modelled.** ONE post-emission scan of the finished buffer yields
this and the total (§4.3); they differ only by which bytes are skipped. **No
`5.070·E + 11.184·J` coefficients appear in any refusal** — an earlier draft
derived code bytes from the fitted model, and a refusal must not inherit a
fit's error.

**A scan, not an accumulator threaded through the emitter.** An accumulator
would be a SECOND implementation of a definition `tests/lib/size_count.sh`
already owns, and the two would drift — exactly what F1 found when this row's
own instrument disagreed with the artifact it was measuring. The scan reads the
bytes actually written, so a new table form or comment style cannot escape it
by forgetting to call something. The shipped implementation is validated
against `size_count.sh` and this lane's python before it is trusted.

**THE BLIND SPOT THAT CONTROL CAUGHT — the same defect twice.** The first cut
of the shipped scan required a table declaration to END with `{`, true of the
DFA's multi-line transition tables and FALSE of the computed-goto jump tables
the emitter writes on ONE line
(`static const void *const rx_targets_7[11] = { &&rx_s1, … };`). It counted
**548,024 bytes of jump table as CODE** on K41's second witness — 1,218,674
instead of 670,650. Same class as F1: an instrument that cannot see one emitted
form, caught by diffing against `size_count.sh` and this note's own figures
before shipping.

**And it explains the r40 discrepancy.** The re-check reported witness 2 at
**1,248,680** code bytes where this note says 670,650, and the manager closed
it as "every decision identical under either reading". The cause is now
concrete: 1,248,680 is within 2.5 % of the buggy 1,218,674 and nowhere near
670,650, so the critic's instrument almost certainly had **the same one-line
jump-table blind spot**. The note's definition — all initializers excluded — is
the definition of record and is what the compiler implements.

**Both caps apply to BOTH ENGINES.** An earlier draft scoped this one to VM
artifacts, a leftover from when it was a NODE cap: a cap on emitted CODE has no
reason to care which emitter wrote the code, and a limit that applies to one
engine only is the special case the standing rule is against. Measured,
generalising costs nothing — the largest DFA artifact in the corpus carries
11,655 code bytes against a 500,000 limit.

Two boundary rules, both stated because each could otherwise move a refusal:

- **A computed-goto jump table is a table initializer**, so its bytes are NOT
  code, even though the states it dispatches to are. The prefilter's `rx_s<N>:`
  labels and `goto *rx_targets_N[…]` lines are code and are counted.
- **`--emit-main`'s appended `main()` is excluded** (R4). It is a diagnostic
  convenience the user never ships, and a diagnostic flag must not be able to
  move a refusal.

**The separation this quantity produces**, against gcc's own cost:

| artifact | comment-excl. total | CODE bytes | gcc CPU | % of D45's 10 s |
|---|---|---|---|---|
| `a{1,25000}` | 1,103,865 | **11,655** | 0.24 s | 2 % |
| `a{1,31000}` | 1,367,865 | **11,655** | 0.34 s | 3 % |
| `((a)\|ab){4000}c` | 651,412 | **32,300** | 0.29 s | 3 % |
| witness 1 **at K=1** | 87,118 | **86,194** | 1.02 s | 10 % |
| **nested N=8 — the corpus's worst** | 288,314 | **283,080** | 7.09 s | **71 %** |
| `jfit` n800_k26 | 562,993 | **280,240** | 3.21 s | 32 % |
| — *no measured artifact between 283 K and 671 K of code* — | | | | |
| **K41 witness 2** | 1,220,606 | **670,650** | **66.92 s** | **669 %** |
| **K41 witness 1** at K=8 | 1,719,349 | **1,718,425** | 55.13 s | 551 % |

**Everything at or below 283 KB of code costs ≤ 71 % of the budget; the next
measured artifact up costs 669 %.** The band between is empty, and the two
`a{1,…}` rows are the reason the quantity is code and not bytes: they differ by
264 KB of TOTAL and by **zero** code, and gcc charges 0.10 s for the
difference.

### 4.2a Why the node cap is dropped

The first version of this pass proposed a NODE cap at 2,000 for the D45 half.
It is withdrawn, because **nodes are one mechanism and code bytes are the
quantity**:

- **Nodes are subsumed.** Witness 1's 7,467 nodes ARE 1,718,425 bytes of code —
  a node cap and a code cap refuse it identically, and the code cap's number is
  the one D45's budget is actually about.
- **Nodes miss the CFG-shaped cost.** K41 witness 2 has **552 nodes** — fewer
  than 168 corpus patterns — and costs gcc **66.92 s**. Its size is 3,108
  prefilter states, which are code and are not nodes. A node cap admits it; the
  code cap refuses it at 670,650.
- **Its blind band is stated** (below), where a node cap's blind spot was a
  whole mechanism.

`PCREC_MAX_VM_NODES` (131,072) stays exactly as it is — a different limit, on a
different quantity, doing a different job.

### 4.2b What the code cap does NOT bound

gcc's cost is not a function of any count the compiler can produce. The
ordering inverts between the two witnesses:

| | code bytes | gcc CPU |
|---|---|---|
| K41 witness 2 | 670,650 | **66.92 s** |
| K41 witness 1 | 1,718,425 (2.56×) | **55.13 s** (18 % less) |

Witness 2's prefilter is one function carrying a 3,108-way computed-goto CFG
(peak RSS 1.9 GB against witness 1's 540 MB). No additive byte count reproduces
that, and a curve fitted through it would be fitting CFG shape it cannot see —
the earlier `N^1.269` fit had a **−43.3 % … +18.3 %** residual (F2) on the
easy, node-decorrelated data.

So the cap is derived the way `PCREC_MAX_VM_REPEAT_COPIES` was: **a measured
SEPARATION with the cap in an empty band.** It claims a BOUND, not a
prediction — every artifact measured at or below it compiled in ≤ 71 % of the
budget — and **the population it cannot speak for is code bytes in
(283 KB, 671 KB)**, empty today and the first thing to measure if one appears.

### 4.2c The value — `PCREC_MAX_VM_EMIT_CODE_BYTES = 500000` (≈ 85 KB `.o`)

**Ruled by Frank** (D84 addendum 2, "then 500k is fine"). Re-derived on the
exact quantity above:

- **in the empty band**: **1.77×** above the corpus's worst (283,080) and
  **1.34×** below the lowest artifact that blows the budget (670,650);
- **refuses 0 of 2,487** corpus patterns on every axis (§4.6b);
- **refuses** witness 1 at K=8 (1,718,425 — the K rule reduces it first) and
  **witness 2 at every K on the ladder**;
- **admits** `a{1,25000}` and `a{1,31000}` (11,655 each) — correctly: they are
  cheap for gcc, and it is the TOTAL cap that refuses them.

### 4.3 The total-bytes cap — `PCREC_MAX_EMIT_BYTES = 1000000` (≈ 170 KB `.o`)

An **exact post-emission check** on the artifact's whole comment-excluded byte
count, refusing **before anything is written to disk**. No model, no
prediction — a fixed number and a loud refusal, which is what makes the outcome
predictable by construction (D84 addendum).

**Derivation — "what size is unusable to ship", not "what gcc can compile".**
Each leg is on the quantity the cap actually reads:

- **the corpus gap**: the corpus's largest artifact is **651,412** and the next
  measured artifact up is `a{1,25000}` at **1,103,865** — a 1.69× gap;
- **the tripwire stays independent**: `check_size_tripwire.sh` pins
  1,400,000 B on this same comment-excluded quantity, so the cap sits BELOW it
  and the tripwire remains a backstop rather than sharing a constant with what
  it checks;
- **the fuzz gate's 1,000,000** (`K41_OVERSIZE_BYTES`) is the same number, and
  **this leg applies to the TOTAL cap only** — it is a bytes-of-artifact
  threshold, which is what this cap is. It is measured on RAW `.c` bytes,
  comments included, so **this cap is the stricter of the two** and an artifact
  it admits is always one `fuzz.py` admits.

**RULED: 1,000,000 stands, and the framing is the ruling's own** (D84 addendum
3). This lane offered a gap-centred 850,000 — 1,000,000 sits 1.54× above the
corpus max but only 1.10× below `a{1,25000}`, so it is not centred — and Frank
did not take it: *"we can adjust the number but it's really more of an
emergency failsafe than a tuning."*

**Both caps are EMERGENCY FAILSAFES, not tuned thresholds**, and the note is
written that way from here on. The consequence is a design one, not a wording
one: a failsafe is judged by whether it fires on the right SHAPES, not by how
much headroom it leaves either side, so **a gap-centred value is not a goal**
and the asymmetry above is not a defect to fix. What a failsafe does owe is
that nothing legitimate hits it silently — which is §4.6's refusal text and
handling section, and §4.6b's zero-refusal sweep, not a better number.

**What the two caps refuse today, together:**

| artifact | code bytes | total bytes | code cap | total cap |
|---|---|---|---|---|
| every one of the 2,487 corpus patterns | max 283,083 | max 651,415 | **admits** | **admits** |
| K41 witness 1, after the K rule picks K=1 | 86,194 | 87,118 | **admits** | **admits** |
| K41 witness 1 at K=8 | 1,718,425 | 1,719,349 | refuses | refuses |
| **K41 witness 2**, at every ladder K | 670,650 | 1,220,606 | **REFUSES** | **REFUSES** |
| `a{1,25000}` | 11,655 | 1,103,865 | admits | **REFUSES** |
| `a{1,31000}` | 11,655 | 1,367,865 | admits | **REFUSES** |

The last two rows are the **intended** reading of D84 ruling 2 (R4), not a side
effect: those artifacts are cheap for gcc and too large to ship, and Frank
ruled shipped size a concern in its own right. Neither is a corpus pattern, and
`--max-emit-bytes=N` exists for the caller who wants them anyway.

### 4.3a Every pattern in the tree whose ACCEPTANCE moves

An acceptance change has to be recorded, not discovered. Surveyed over the
`.rxt` corpus, `tests/resource`'s K7 shape list and the two K41 fuzz witnesses
— each compiled BEFORE this row (caps raised out of the way, term denied) and
AFTER:

| pattern | population | before | after |
|---|---|---|---|
| all 2,487 compiling corpus patterns | `tests/**/*.rxt` | compile | **compile, unchanged** |
| `a{0,25000}` | resource K7 | 1,103,367 B | **REFUSED** (total cap) |
| `[a-z]{0,30000}` | resource K7 | 1,323,371 B | **REFUSED** (total cap) |
| `(a|b){0,30000}` | resource K7 | 1,333,109 B | **REFUSED** (total cap) |
| the other 8 K7 shapes | resource K7 | unchanged | unchanged (±7 B, the stamps) |
| **K41 witness 1** | fuzz gate | 1,719,349 B | **compiles at 87,118 B** — the K rule |
| **K41 witness 2** | fuzz gate | 1,220,606 B | **REFUSED** (both caps) |

**The three resource shapes are the row's real acceptance cost**, and all three
are TABLE-dominated — their code is tens of KB, so `--unroll` cannot shrink
them and only raising the cap or reducing the count will. That is the intended
reading of D84 ruling 2, and `tests/resource/run_resource_tests.sh` §1b pins
each of them as an EXPECTED refusal beside a second cell proving
`--max-emit-bytes=N` re-accepts it — which is also the only end-to-end test of
the override.

**And the corpus was not the whole population.** The first version of this
note claimed "0 of 2,487 corpus patterns refused" and stopped there; the three
shapes above are in `tests/resource`, which that sweep never covered. The same
gap cost a real regression during the code phase (§3.3's counter-rung gate) —
a population nobody counted, one more time, and this time it was this lane's.

### 4.3b One lesson, learned three times: WHICH QUANTITY does this act on?

Every wrong answer this row produced came from measuring a quantity ADJACENT
to the one that mattered, and it happened three times in three different
places:

| # | the mechanism | the wrong quantity | the right one | how it showed up |
|---|---|---|---|---|
| 1 | the **cap** | total bytes, then nodes | **code bytes** | a byte cap refuses `a{1,31000}` (gcc 0.34 s); a node cap admits witness 2 (552 nodes, gcc 66.92 s) |
| 2 | the **early abort** | comment-excluded bytes | **raw bytes, with a derived factor** | the bound is checked on what a `StrBuf` knows, so the cap's own quantity was not available there |
| 3 | the **threshold** | total bytes | **code bytes** | the ladder ran on the corpus's largest artifacts, which are table-dominated and cannot shrink — five wasted pipeline runs that blew three CPU ceilings |

The recurring shape is that each mechanism has a quantity it can actually
ACT ON, and using the one next to it looks right in every summary and fails on
the population where the two diverge. It is worth stating as a question to ask
of a new mechanism rather than as three separate corrections:
**what can this change, and am I measuring that?**

Recorded in `docs/dev/learnings.md` §3 as well, because it is not specific to
this row.

### 4.4 Where the caps fire, and the ladder re-run (finding S5)

The first version claimed the design "cannot ship an uncompilable artifact
because step 1 has already taken the smallest K". **critic-sem refuted it**:
when the materiality bar DECLINES, step 1 keeps `K_opt`. Measured on witness 2
— K=1 is 1,114,780 B / `N` = 105 against K=8's 1,220,606 B / `N` = 552, a byte
ratio of **0.913** that declines the bar **despite an 81 % node reduction**.

**The fix: the materiality bar gates the THROUGHPUT preference; the caps get
the WHOLE ladder.**

```
    1.  emit at K_opt                                   (happens anyway)
    2.  if bytes > THRESHOLD and no explicit --unroll:
            ladder: dry-emit K in [8,6,4,3,2,1] with trial=1        (§2.2b)
                    a trial ABORTS and returns OVER as soon as its
                    scratch buffer passes either cap                (§2.2c)
            among the trials that returned OK, take argmin N        (§3.1a)
            keep it only if bytes(K_best) <= 0.75 * bytes(K_opt)    (the bar)
    3.  let K_sel be the kept emission
    4.  if code_bytes(K_sel) > CODE CAP  or  bytes(K_sel) > TOTAL CAP:
            consider every ladder trial that returned OK, BAR BYPASSED
            if some K passes BOTH caps  ->  take it; stamp `cap-rescue`
            else                        ->  REFUSE, write nothing
    5.  write the file
```

Step 4 needs no second ladder run: step 2's trials already recorded each K's
exact `code_bytes` and `bytes`, and a trial that returned `OVER` is by
construction over a cap and cannot be a rescue.

- **The caps are checked on the artifact the ladder CHOSE** (smallest realized),
  never on a greedily-descended one — `N` and bytes are both non-monotone in K
  (§3.1a).
- **Step 4 can rescue a pattern step 2's bar declined**, and must: a refusal
  outranks a throughput preference. A K taken this way is stamped
  **`cap-rescue`** (§7.1, finding R5) — neither `size-model` nor
  `size-model-declined` is true of it.
- **A trial's own refusal is never the compile's answer** (§2.2b): the ladder
  runs only after the default-K emission succeeded, so if every trial returns
  `OVER`, step 3 keeps that artifact and step 4 judges it. Without it, witness-2-shaped patterns with
  a viable K would be refused for a reason the bar has no business deciding.
- **Nothing is emitted silently past either cap** (D84 addendum): the outcomes
  are a written artifact under both caps, or a refusal and no file.

### 4.5 The overrides (D84 ruling 1)

The caps are **NOT deniable** — `-fno-size-term` denies the K selection and
never reaches either, because a safety refusal a flag turns off is not one.
They **ARE overridable upward**:

| flag | option field | semantics |
|---|---|---|
| `--max-emit-code-bytes=N` | `pcrec_options.max_emit_code_bytes` | RAISE-ONLY |
| `--max-emit-bytes=N` | `pcrec_options.max_emit_bytes` | RAISE-ONLY |

**Where a real build raises a limit is the PATTERN-SOURCE FILE, not the command
line** (D84 addendum 3). The grown `.rxt` format's `config` block
(`dd13_format/usecases_and_outline.md` §2 wave 3) carries pcrec option lines,
and these two overrides belong there:

```
config big
  pcrec --max-emit-bytes=4000000
use big

pattern <the pattern that needs it>
```

A `config` raises the cap **for every target built `with` that config, per
target, declared beside the pattern** — which is the form that survives review,
gets committed, and is visible to the next reader. **The CLI flags exist for
the single-pattern case and for the harness**, not as a command-line habit; a
build that needs a raised cap should say so in the file, not in a shell
history. (The DD-13 note already carries the reciprocal line.)

Both **effective values are STAMPED** as selection facts (D81, §7.1), so a
reader of any artifact can see which caps it was built under. A value BELOW the
default is refused as a malformed option rather than honoured: a lower cap is
not a use case this row has a measurement for, and a raise-only flag cannot be
used to manufacture a refusal.

Rationale, from critic-sem and ruled by Frank: every other resource limit in
pcrec has a per-compile override (`--step-budget`, `--work-budget`,
`--backtrack-frames`; `limits.md` §3); this would be the first without one; its
whole cost falls on the caller's own gcc on the caller's own box; and on the
[SEL-1] fallback path "change the pattern" is not available to a caller whose
pattern came from a config file.

### 4.6 What a user sees BEFORE a large file appears

D84's predictability half is discharged by **a loud refusal and
documentation**, not by machinery. Each refusal names measured-vs-cap and the
lever that would pass:

> `pattern too large: the emitted matcher is 1,114,780 bytes of C source
> (limit 1,000,000; about 190 KB of .o). This artifact is 92% prefilter
> tables, which --unroll does not shrink. Raise the limit with
> --max-emit-bytes=N if that size is acceptable to you, or see
> docs/spec/limits.md "Handling an oversized artifact".`

> `pattern too large: the emitted matcher contains 670,650 bytes of CODE
> (limit 500,000; about 85 KB of .o), which gcc cannot compile in reasonable
> time. A bounded repeat's body is replicated and repetition counts MULTIPLY
> through nesting -- lower a count, reduce the nesting, or raise the limit with
> --max-emit-code-bytes=N.`

On the [SEL-1] fallback path the message additionally appends
`RX_ENGINE_WHY`'s reason (§4.7), because otherwise it tells a user to lower a
repeat count when the real cause is a DFA overflow.

**D26 tier:** pcrec's own wording; PCRE2 has no emitted C and so no analogous
diagnostic — nothing to match, no effort spent.

**`docs/spec/limits.md` gains a "Handling an oversized artifact" section** — a
D80 hunk, drafted here so the code phase transcribes rather than invents it.
([GUIDE-1] owes the use-case paragraph when it exists.)

> **Handling an oversized artifact.** pcrec REFUSES rather than emitting an
> artifact past `PCREC_MAX_EMIT_BYTES` (total) or
> `PCREC_MAX_VM_EMIT_CODE_BYTES` (code). Nothing is written when it refuses.
> Both limits are in bytes of emitted C source excluding comments; the `.o` you
> link is roughly 17 % of that, so the 1,000,000-byte total limit is about
> 170 KB of object code. Your options, in the order most callers want them:
>
> 1. **Raise the limit** — `--max-emit-bytes=N` or `--max-emit-code-bytes=N`
>    if the size is acceptable to you. Both are raise-only, and the effective
>    values are stamped on the artifact. **For a real build, put the override in
>    the pattern-source file's `config` block rather than on the command line**:
>    it then applies per target, beside the pattern, to everything built with
>    that config, and it is visible to whoever reads the file next. The CLI
>    flags are for one-off compiles and for the test harness.
> 2. **Let the size term choose `K`, or force it.** `--unroll=1` emits one body
>    copy per counter-rung iteration and is the largest size lever for a
>    replication-dominated pattern — measured 17× on the fuzz gate's own
>    witness. It costs 1–3 % throughput on single-level large counts. It does
>    NOT shrink a table- or prefilter-dominated artifact.
> 3. **Change the engine or the output** where the pattern admits it.
>    `--no-captures` and `--engine=dfa` remove the VM body; `--engine=vm`
>    removes the hybrid DFA prefilter, which is most of the size when the
>    stamps say the artifact is table-dominated — at a large cost on
>    non-matching subjects.
> 4. **Split or rewrite the pattern.** Repetition counts MULTIPLY through
>    nesting, so lowering one count INSIDE a nest is worth far more than
>    lowering an outer one.
> 5. **Read the stamps to see which term produced the bytes.**
>    `RX_UNROLL_K`/`RX_UNROLL_K_WHY` and `RX_VM_RUNGS` for node replication;
>    `RX_DFA_TABLE`/`RX_VM_PREFILTER` for the prefilter and its tables. A
>    table-dominated artifact does not shrink with `--unroll`, and option 2
>    will not help it.

`limits.md` §7's sentence that compile TIME is not a compiler-side contract is
a **named spec hunk in this change** (finding S7): the code-bytes cap makes it
one, in the units that predict it.

### 4.6b The zero-refusal claim, re-measured off the default axis (finding S11)

"0 of 2,487 refused" was measured on the DEFAULT axis only, and the emitted
counts depend on more than `(AST, K)` — critic-sem measured `-fno-length-prune`
moving `N` from 121 to 117 on `((a)|ab){12}c`. A claim about the caps has to
hold across every axis `make test-axes` sweeps, or the first denied build to
exceed a cap turns an identity sweep red for a reason nobody predicted.

`artsize_impl/probes/axsweep.py` re-emits the whole corpus under `--engine=vm`
and each deny flag (emit only, no gcc):

| axis | max N | max CODE bytes | max TOTAL bytes | over code cap | over total cap | compiled / refused |
|---|---|---|---|---|---|---|
| default | 1,471 | 283,080 | 651,412 | **0** | **0** | 2,487 / 284 |
| `--engine=vm` | 1,471 | 280,138 | 280,600 | **0** | **0** | 2,487 / 284 |
| `-fno-counter` | **1,489** | 283,010 | 465,818 | **0** | **0** | 2,480 / **291** |
| `-fno-possessify` | 1,471 | 283,080 | 651,412 | **0** | **0** | 2,487 / 284 |
| `-fno-revdet` | 1,471 | 283,080 | 651,412 | **0** | **0** | 2,487 / 284 |
| `-fno-length-prune` | 1,471 | 283,080 | 650,557 | **0** | **0** | 2,487 / 284 |
| `-fno-splice-calls` | 1,471 | **283,083** | **651,415** | **0** | **0** | 2,487 / 284 |
| `-fno-tiered-entry` | 1,471 | 283,080 | 649,459 | **0** | **0** | 2,487 / 284 |
| `-fno-premul-table` | 1,471 | 283,044 | 404,285 | **0** | **0** | 2,487 / 284 |
| `-fno-offset-skip` | 1,471 | 283,080 | 651,412 | **0** | **0** | 2,487 / 284 |

**The claim holds on every axis, with margin.** The worst CODE count anywhere
is **283,083** against a 500,000 cap (**1.77×** headroom) and the worst TOTAL
is **651,415** against 1,000,000 (**1.54×**). Three axis facts worth recording:

- **`-fno-counter` is the only axis that moves `N`** (1,471 → 1,489) — the
  expected direction, since denying the counter rung restores literal
  replication — and it refuses **7 more patterns** (291 vs 284) because without
  the rung they exceed `PCREC_MAX_VM_REPEAT_COPIES`. That is pre-existing
  deny-flag behaviour, not something this row introduces, and it is the axis a
  future emitter change would push over the code cap first.
- **`--engine=vm` and `-fno-premul-table` roughly halve the worst TOTAL**
  (280,600 and 404,285) while leaving the worst CODE within 3,000 bytes — the
  cleanest confirmation in the note that the two caps measure different things:
  both flags remove prefilter TABLES, which is total-byte weight and almost no
  code.
- **No axis moves the worst code count by more than 0.03 %** (283,010 →
  283,083), which is what makes 1.77× headroom a real margin rather than a
  default-axis artifact.

**Method note, recorded rather than smoothed:** the first attempt at this sweep
ran into another lane's `make mech` (load1 **49**). It was killed with
`scripts/safekill` by PID and requeued behind a `load1 < 8` check, per the
one-heavy-suite-at-a-time rule (memory `pcrec-box-concurrency`) — the sweep
records COUNTS and not times, so its own numbers were never at risk, but a
timing-sensitive suite was running and this one was adding to it. The axes
measured before the kill reproduce exactly in the completed run.

### 4.7 The [SEL-1] interaction

`auto` selects DFA → the DFA overflows `PCREC_MAX_DFA_STATES_TABLE` → [SEL-1]
falls back to the VM → the VM's size trips a cap. **This is K41's own story**
("[SEL-1] is what UNHID it rather than caused it"), and witness 1 is a live
instance — its `RX_VM_PREFILTER` is `"none"` for exactly this reason.

1. **The user must not be told the wrong story.** When `RX_ENGINE_WHY`'s reason
   is a fallback, the refusal appends it. Without that the message names
   repetition counts on the path where the real cause is a DFA overflow.
2. **The fallback cannot bypass either cap** — both are checked on the VM path
   however it was reached, and there is no third engine. The result is a
   refusal, which is what D45's consequence 1 and D84 both ask for.

### 4.8 K41's pinned bucket — and the bucket a REFUSAL actually lands in

`tests/fuzz/fuzz.py` classifies "K41 oversize artifact" by emitted `.c` size
alone (`K41_OVERSIZE_BYTES = 1_000_000`, checked before and independently of
gcc) and `run_capturediff_gate.sh` pins that bucket at **exactly 2**.

**Under this design both witnesses leave that bucket, by different routes:**

| witness | route | after |
|---|---|---|
| 1 | the K rule selects K=1 | **87,118 B** — an order of magnitude under the classifier; it **re-enters the ordinary accept/compare pipeline** |
| 2 | every ladder K is over BOTH caps (code 670,650 > 500,000 at K=8, and no lower K gets under; total 1,114,780 > 1,000,000 at its best) | **REFUSED** — no artifact exists to classify |

So the oversize bucket goes **2 → 0**. (critic-sem's S6 computed 2 → 1, which
was right for the design as reviewed — before D84 added a cap that reaches
witness 2.)

**But "not oversize" is not the same as "counted correctly", and this is the
part that would have bitten silently.** `fuzz.py` classifies a pattern pcrec
rejects and PCRE2 accepts as **`pcrec_reject_only` — an accept/reject
DIVERGENCE**, which the gate reads as an actionable finding. A size refusal is
not a divergence; it is pcrec's own documented ceiling doing its job.

The precedent for handling exactly this already exists in the same file.
`state_cap` (`fuzz.py:930-945`) is diverted out of the divergence bucket **by
matching the diagnostic text** — `"too complex for the DFA engine"` /
`"NFA exceeds"` — with a comment saying it is kept in its own bucket "so it
doesn't masquerade as an actionable divergence on every run". `engine_limit`
does the same for PCRE2's err 120, "own bucket, like state_cap".

**So the landing change owes `fuzz.py` a `size_cap` bucket on that precedent**,
recognised by the `"pattern too large: "` diagnostic prefix, checked in the
same place `state_cap` is, and printed with the same "not a divergence"
wording. Without it, refusing witness 2 turns the gate red as a semantic
divergence and the next reader either weakens the gate or spends a day on a
non-defect.

**A pre-existing instance of the same gap, found while checking this.** The
`"pattern too large: "` family already has TWO members that ship today — the
`PCREC_MAX_VM_REPEAT_COPIES` and `PCREC_MAX_VM_REPLICATION_PRODUCT` refusals —
and `fuzz.py` does not divert either. A generated pattern hitting one of them
lands in `pcrec_reject_only` right now. It has not fired at the pinned seed, so
nobody has seen it; the `size_cap` bucket fixes the whole family, not just this
row's two caps. Recorded here rather than filed separately because the hunk
that fixes it is this row's.

**The counts, re-derived rather than asserted.** K41 records three counts as
arithmetically coupled to pulling both witnesses out of the pipeline
(both-accept 183 → 181, subject pairs 2,745 → 2,715, oracle-inconclusive
3 → 0), which implies `--subjects 15` and one both-accept slot per witness.
Under this design the movement is:

- **witness 1 re-enters** the accept/compare population: both-accept
  181 → **182**, subject pairs 2,715 → **2,730** (+15);
- **witness 2 becomes a size refusal**: it leaves the oversize bucket and
  enters the new `size_cap` bucket, pinned at **1**;
- **oracle-inconclusive** is NOT predictable from arithmetic — it depends on
  what witness 1's re-entered subjects do — and must be **read from a gate
  run**, not derived.

K41's own text says a movement of the oversize bucket to 0 means "re-derive, do
not silently widen", so the landing change runs the gate and pins what it
reports, with the reading written into the EXPECT comment: **not "K41 closed by
disappearance" — one witness is FIXED and one is REFUSED.**

**K41 is re-scoped, not closed.** Witness 1 is fixed by the K rule. Witness 2
is refused, not fixed, and its mechanism — the VM hybrid's inlined prefilter
scaling with a bounded-repeat count — is **[OPT-4]/K39's** to shrink. D84's own
revisit clause says witness 2 should pass under the default cap once [OPT-4]
lands, which is the trigger to re-check both pins.

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

### 6.1 The argument, and the two places it is NARROWER than the first version claimed

**Claim: for any K ≥ 1, the artifact's MATCH RESULTS — the span and the capture
slots, on every subject, from every start position — are identical.**

`K` is the counter rung's **chunking factor**. The rung compiles a bounded
repeat to `ceil(n/K)` copies of the body plus an iteration counter whose
arithmetic makes the realized iteration count exact for any K ≥ 1
(`emit_vm.c`, the counter rung; `counterk_impl/counterk_design.md` §4.1).
Varying K changes how many source-level copies the same loop is written as.

**NARROWING 1 — the give-up and capacity surface is NOT invariant (finding
S2).** The first version said "the step/work budgets charged — per iteration"
and §0 said "every K is answer-identical". Both are refuted, measured on
`((a)|ab){12}c` against `"ab"×12`:

| K | 1 | 2 | 3 | 4 | 6 | 8 |
|---|---|---|---|---|---|---|
| minimum `--step-budget` that completes | 89 | 89 | 97 | 98 | 107 | 110 |
| minimum `--backtrack-frames` | **39** | | | | | **28** |
| `RX_TRAIL_FRAMES` in the emitted header | 62 | 56 | 54 | 53 | 52 | 51 |

The rung is 0x10 at every K, so this is chunking, via the once-per-trip MRL
guard (`:4245-4260`). Note the direction on frames: **descending K RAISES the
frame requirement by 39 %**, so the size term can make a tuned caller's
capacity verdict worse, not only better. And `RX_TRAIL_FRAMES` is a macro
`match_api.md:1083` names as caller-read.

**Answers under the DEFAULT budgets are identical** (checked). So the claim is
exactly: *match results and captures are invariant; the give-up surface and the
emitted capacities are not.* This is a caller-observable change and it gets a
**D80 hunk in `limits.md`** recording that the size term may change a tuned
caller's budget verdict.

**NARROWING 2 — rung selection is NOT before K (finding S3).** The first
version said "rung selection runs before K is consulted". False:
`vm_counter_fits` (`:1034-1036`) reads `v->unroll_k`
(`rmin >= K || (rmax - rmin) >= K`). Measured on `((a)|ab){3}c`: rung 0x10 at
K=1,2,3 and **0x2 at K=4,8** (`RX_NSLOTS` 7→6, `RX_FAST_TRAIL` 17→13). It
reaches the corpus: `^(?R){0,2}$` (`tests/recursion/d27/sr_depth.rxt:180`)
flips 0x2↔0x10 between K=3 and K=2, with its `gu frames` answer holding at
every K. §3.1's "identical at every K" subjects all had counts ≫ 8, which is
why this lane saw no flip — a population artifact, not a property.

So rung answer-identity under a changed K is **not** a consequence of "the rung
was already chosen"; it is gated TODAY by `make test-axes`' `PCREC_NO_COUNTER`
bit, which sweeps the corpus with the counter rung denied against the default
build. That is the existing evidence, and §6.2's new K sweep extends it across
the ladder.

What K does NOT change, and these survive both narrowings:

- **the choice points and their preference order** — one per body iteration
  either way;
- **capture, trail and cut behaviour** — per iteration, not per chunk;
- **which quantifier is possessified, revdet'd or spliced** — those verdicts
  read the AST, not K.

### 6.2 The gate, the GAP this row found, and what the sweep must EXCLUDE

**`make test-axes` does not cover `--unroll`.** `tests/axes/run_axes.sh`
derives its axis registry mechanically from `lib/pcrec.h`:

```
    grep -oE 'PCREC_(NO|FORCE)_[A-Z_]+ *= *1u << [0-9]+' lib/pcrec.h
```

`--unroll=K` is a **VALUE** axis (`pcrec_options.unroll_k`), not a deny/force
bit, so it has never been swept. **The claim in §6.1 is not proven by any gate
today** — found by reading the script rather than trusting a summary of it.

Four controls, in the order they must land:

1. **The K sweep (NEW, and the load-bearing one).** The corpus at each
   `K ∈ {1,2,3,4,6,8}`, answers compared case-by-case against the default
   build. **Its comparison is SPECIFIED, not discovered** (finding S2): it
   compares under DEFAULT budgets, and it **excludes `budget` and `gu` cells by
   construction** — because §6.1 measured those to be genuinely K-dependent, a
   sweep that included them would fail on a TRUE property and the next person
   would weaken the gate to make it green. The exclusion is written into the
   check with §6.1's table as its citation, so it reads as a scoped claim and
   not as an allowlist.

   **The excluded cells are not left ungated** (finding R6). An exclusion with
   nothing behind it is how a real defect hides, so on every excluded cell the
   sweep still asserts the weaker property that IS K-invariant: **where two K
   values both give up, they give up with the same CODE** (`RX_ERR_STEPS` vs
   `RX_ERR_WORK` vs `RX_ERR_FRAMES`) — only the threshold at which they do so
   moves. And the check **records the excluded population's size** in its
   output, so an exclusion that silently grows to cover the corpus is visible
   as a number rather than as a green run.
2. **`-fno-size-term` (bit 17)** joins `make test-axes` by construction — it is
   a `PCREC_NO_*` bit and the script's own `grep` finds it.
3. **Zero cost where not selected (D82), proved as [OPT-K] §7.3 proved it, not
   inferred**: at least four declined patterns spanning both engines, compiled
   with this compiler and with one built from `main`, disassembled, requiring
   **0 differing instructions**, with the source differing by exactly the
   expected stamp and `abi` lines.
4. **The control this row specifically owes.** For every pattern where the term
   BINDS, the size-term build and an explicit `--unroll=<the K the ladder
   chose>` build must be **byte-identical apart from the stamp lines**. This is
   what proves the term only CHOOSES K and does nothing else — the check that
   would catch a general mechanism degenerating into a special case.

**AR3 — why the K sweep is a hand-written one-off, and what it waits for.**
`--unroll` is a value axis and `src/parse/axes_dump.c` has no `kind=value`
support, so the registry cannot describe it and `make test-axes` cannot derive
it. [CHK-2] item (c), "test-axes-from-dump", is the row that would fix that and
is **not built**. So the K sweep ships NOW as a standalone check and is the
gate; `--unroll` is registered as a value axis when [CHK-2] (c) is built, and
**this row is that item's named trigger** (D77).

**What the controls do NOT prove: byte identity.** D81 makes selection stamps
unconditional, so the `-fno-size-term` build differs from today's compiler by
exactly the new stamp lines **and the `abi` line** on **every artifact,
DFA included** — `.abi = 9,` sits in the emitted BODY of every artifact
(finding S8), so the bump moves every artifact by at least one byte. [OPT-K]'s
r39 finding A1 was precisely a draft claiming byte identity that D81 made
false; this note does not repeat it, and §8/§9 are written to agree with this
paragraph rather than with the first version's "0 on DFA artifacts".

## 7. Stamps, flags, and the axis registry

### 7.1 Stamps (D81: selection facts are unconditional)

| stamp | value | on |
|---|---|---|
| `<PREFIX>_UNROLL_K` | the K this artifact was emitted at, an integer | **every VM artifact**, unconditionally |
| `<PREFIX>_UNROLL_K_WHY` | see the five values below | **every VM artifact**, unconditionally |
| `<PREFIX>_MAX_EMIT_CODE_BYTES` | the EFFECTIVE code-bytes cap (default, or the `--max-emit-code-bytes=N` override) | **every VM artifact** |
| `<PREFIX>_MAX_EMIT_BYTES` | the EFFECTIVE total-bytes cap (default, or the `--max-emit-bytes=N` override) | **every artifact**, both engines — the total cap is engine-independent |

**`_UNROLL_K_WHY` has SIX values, not three** (findings S9, R5). The first
version's `{default, size-model, option}` hid four reachable states behind
`"default"`, so a check could not tell "the term never ran" from "it ran and
declined" — which is exactly the distinction a structural check needs:

| value | meaning |
|---|---|
| `option` | `--unroll=K` was given; the term did not run |
| `denied` | `-fno-size-term`; the term was denied |
| `default` | the term ran the threshold test and the artifact was BELOW it |
| `size-model` | the ladder ran and its K was TAKEN |
| `size-model-declined` | the ladder ran, and the materiality bar rejected its K |
| `cap-rescue` | the bar declined the ladder's K, then §4.4 step 4 took a ladder K anyway to get under a cap (finding R5 — neither of the two above is true of it) |

Unconditional is the point: D81 splits the D46 family so a selection fact is
stamped **whether or not it fired**, which is what makes the stamp evidence
rather than a hint.

`_UNROLL_K` and `_UNROLL_K_WHY` are VM-only, matching `RX_VM_RUNGS` and
`RX_VM_PREFILTER`: a DFA artifact has no counter rung, so there is no K to have
selected. `_MAX_EMIT_BYTES` is on both engines because the total-bytes cap applies to
both; `_MAX_EMIT_CODE_BYTES` is VM-only, like the quantity it bounds.

**Not stamped: the artifact's own size.** An artifact cannot carry its own byte
count — writing the number changes it. D84's addendum drops the
`_EMIT_SIZE_PREDICTED` idea for the same reason it drops the model from the
byte axis: the cap is exact and post-emission, so a predicted number on the
artifact would be a second, weaker source for a fact the refusal already states
exactly. What IS readable from any artifact is which caps it was built under
and which term chose its K — which is what §4.6 option 5 tells a user to do.

**`rx_info` mirror:** none. The chosen K and the effective caps are
compile-time selection facts with no run-time consumer — nothing in the match
API's behaviour depends on them. ([OPT-K]'s precedent stamps sibling macros,
not `rx_info` fields, for the same reason.)

### 7.2 The deny flag

`PCREC_NO_SIZE_TERM = 1u << 17` / `-fno-size-term`. **Bit 16 is taken** —
[OPT-K]'s `PCREC_NO_OFFSET_SKIP`, verified in `lib/pcrec.h`. `docs/spec/
tuning.md` gains a §2.15 in **§2.14**'s deny-only shape (`-fno-offset-skip`,
bit 16 — the closest precedent, panel finding AR11), and §2's count moves
from fourteen to fifteen.

It denies **the K selection only**, never either cap — D84 ruling 1, §4.5,
where the raise-only overrides live.

**The D80 spec hunks, complete** (panel findings AR1/AR2 — the first version's
list was short by two):

| # | file | hunk |
|---|---|---|
| 1 | `docs/spec/tuning.md` | new §2.15 in §2.14's deny-only shape; §2's count fourteen → fifteen |
| 2 | **`docs/spec/cli.md:218-224`** | the hand-enumerated `-fno-` axis list, which runs through `-fno-offset-skip` and must gain `-fno-size-term` |
| 3 | **`docs/spec/match_api.md` §6.3** | a per-mechanism bullet for the two macros, on the `_DFA_SCAN`/`_DFA_PREFILTER` precedent at `match_api.md:1659-1720`, scoped VM-artifact-only |
| 4 | `docs/spec/match_api.md` §6 | the `abi` sentences, 9 → 10 (§8) |
| 5 | `docs/spec/limits.md` | `PCREC_MAX_VM_EMIT_CODE_BYTES` and `PCREC_MAX_EMIT_BYTES` with their units and `.o` equivalences (§4.0), both refusals (§4.6), the note that the size term can change a tuned caller's budget verdict (S2), §7's compile-time sentence (S7), and the new "Handling an oversized artifact" section |

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
| 1 | stamp | `_UNROLL_K`, `_UNROLL_K_WHY` (five values), `_MAX_EMIT_CODE_BYTES`, `_MAX_EMIT_BYTES` (§7.1) |
| 2 | deny flag | `-fno-size-term` / `PCREC_NO_SIZE_TERM` (bit 17), `docs/spec/tuning.md` §2.15 |
| 3 | identity gate | `make test-axes` bit 17 by construction, **plus** the K sweep §6.2 owes |
| — | *(and see AR3 below on why the K sweep is a one-off today)* | |
| 4 | structural check | `tests/codegen/run_size_term.sh` — reads the ARTIFACT: the emitted body-copy count against the stamped K, `_WHY` against which path ran, and the two effective caps against the flags. **It must handle the NO-COUNTER-RUNG case** (finding S3): where `vm_counter_fits` declines, the copy count is `count` and K is inert, so a check that asserts `ceil(count/K)` unconditionally fails on a correct artifact |
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
`abi` 7 overshot its own estimate sixfold), **corrected for finding S8**: the
first version said "0 on DFA artifacts", which is wrong twice over. `.abi = 9,`
sits in the emitted BODY of *every* artifact, DFA included, so the bump alone
moves every artifact by ≥ 1 byte; and `_MAX_EMIT_BYTES` (§7.1) is stamped on
both engines. The estimate is therefore:

| artifact | added |
|---|---|
| VM | `_UNROLL_K` + `_UNROLL_K_WHY` + `_MAX_EMIT_NODES` + `_MAX_EMIT_BYTES` + the `abi` digit — **≈ 130 B** |
| DFA | `_MAX_EMIT_BYTES` + the `abi` digit — **≈ 35 B** |

To be measured after and compared here. §6.2 and §9 rows 3 and 5 are written to
agree with this rather than with "byte-identical".

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
| 1b | **K41 witness 2** | bar declines (byte ratio 0.913); no ladder K is under EITHER cap (code 670,650; total 1,114,780 at its best); **REFUSED** | exact — it must refuse, name measured-vs-cap and the levers (§4.6) |
| 2 | nested N=8 / N=6 / N=4 | K=1 selected; comment-excluded 288,314 → 60,902 B (−78.9 %), 225,862 → 60,902 (−73.0 %), 162,034 → 60,902 (−62.4 %); `.o` 75–79 % smaller (census §8) | ±5 % on the byte figures |
| 3 | the four declining patterns above the threshold | K unchanged at 8; **`.o` byte-identical**; source differs by exactly the new stamp lines AND the `abi` digit, on VM and DFA alike (§8, finding S8) | exact |
| 4 | D82 zero cost | ≥ 4 declined patterns, both engines, **objdump 0 differing instructions** vs a `main`-built compiler | exact |
| 5 | the corpus size log | regenerated on `main`; **exactly the 3 selecting patterns move**, all downward; every other row differs by exactly the per-engine stamp+`abi` constant of §8 | exact |
| 6 | the caps | 0 of 2,487 corpus patterns refused by EITHER cap, **re-measured across `--engine=vm` and every deny flag** (§4.6b): worst code 284,038 vs 500,000, worst total 651,415 vs 1,000,000 | exact |
| 6d | the overrides | `--max-emit-code-bytes=N` / `--max-emit-bytes=N` raise-only; a value below the default is refused as a malformed option; both effective values stamped | exact |
| 6e | **the `size_cap` fuzz bucket** | a size refusal lands in the NEW `size_cap` bucket, not in `pcrec_reject_only`; verified by running the gate, not by reading the patch (§4.8) | exact |
| 6b | **K41's fuzz-gate bucket** | 2 → **0**, re-pinned with the reading in §4.8 and the coupled counts re-derived (witness 1 RE-ENTERS the compare population; witness 2 becomes a refusal) | exact |
| 6c | the instrument | `measure.py`'s byte column agrees with `size_count.sh` on every pattern it is run against, both artifact forms | exact — the control §2.0 did without |
| 8 | **the identity sweep's scope** | the K sweep is green with `budget`/`gu` cells EXCLUDED BY CONSTRUCTION and default budgets in force (§6.2 control 1); a run that includes them and passes means the exclusion was not wired; the excluded population's SIZE is printed, and on those cells the give-up CODE still matches where both K give up (R6) | exact |
| 9 | **R1's witness — the one the ladder would have broken** | `(?:(?:(?:(?:(?:(?:a\|b){41}){41}){41}){41}){41}){41}` under `--engine=vm` still COMPILES, at K=8, artifact unchanged. Today: K=8 compiles (N=118,098), K=6 refuses "VM exceeds 131072 emitted nodes" | exact — a `.rxt` cell, not a note claim |
| 10 | **R2's worst-rung cost** | MEASURED in-process: the 6-deep `{17}` tower compiles in **0.75 s / 64 MB peak RSS** with the abort on, against 55.4 MB of scratch written without it | measured before and after |
| 11 | **the re-emission identity control** | 0 internal errors over the whole corpus, and it must FIRE when the final attempt's node count or adjusted bytes differ from the ladder's record (§2.2d — it fired for real on its first run) | exact |
| 12 | **`cap-rescue`** | the sixth `_UNROLL_K_WHY` value must be REACHED by some cell; if no natural pattern reaches it, a test-only cap override is what exercises it (§10 item 6) | a value no test can produce is a value no check guards |
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
2. **RULED — D84 ruling 1.** The caps are not deniable but ARE overridable
   upward (`--max-emit-code-bytes=N`, `--max-emit-bytes=N`, raise-only,
   stamped); §4.5 is written to that shape. The first version's cost objection is
   answered by the override, not by the deny flag.
3. **CLOSED by r40 AR10** — the threshold is 120,000, not 131,072; the
   collision was worse than the first version said
   (`PCREC_MAX_VM_REPLICATION_PRODUCT` is a literal alias of
   `PCREC_MAX_VM_NODES`), and the note's own costless fix was taken (§3.2).
3b. **BOTH cap values are RULED and the question is CLOSED.** D84 addendum 2:
   the code-bytes cap is 500,000 (≈ 85 KB `.o`), inside the empty band between
   the corpus's worst 283,080 and witness 2's 670,650. D84 addendum 3: the
   total-bytes cap stays at 1,000,000 — this lane's gap-centred 850,000 was
   offered and **not taken**, because *"it's really more of an emergency
   failsafe than a tuning"*. Recorded because it settles a whole class of
   future question: **these are failsafes, so centring one in its gap is not an
   improvement**, and a proposal to move either needs a SHAPE it fires or fails
   to fire on, not a better ratio.
4. **RULED — D84 ruling 2 / Q4.** `a{1,25000}`-shaped artifacts are NO LONGER
   left alone: shipped size is a concern in its own right, so the total-bytes cap
   refuses them (1,103,865 and 1,367,865 bytes) even though gcc compiles them in under
   half a second. **K41 witness 2 is the pinned counter-example** the ruling
   names — 1.26 MB, 92 % prefilter, refused here and [OPT-4]/K39's to shrink.
   The first version's framing of this population, retained because the
   measurement behind it stands:

4b. *(superseded framing)* **`a{1,25000}`-shaped artifacts** (1.10 MB comment-excluded, gcc 0.24 s).
   They are large for a user to ship and cheap for gcc to compile, so neither
   §3 nor §4 touches them: the K rule sees a K-insensitive `N` and the cap is
   not about bytes. If Frank's concern is the SHIPPED SIZE rather than the
   compile budget, this is the population that answers it, and the instrument
   would be a third mechanism (a byte-based *warning*, or a table-form
   selection) that this note does not propose. **Flagged because the row's
   founding quote is about size, not compile time.** r40 AR9 rules this real
   but outside the row as chartered — a shipped-size instrument would be a new
   row.
6. **`cap-rescue` is implemented but currently UNREACHABLE, and that is a real
   gap.** The sixth `_UNROLL_K_WHY` value fires when the materiality bar
   declines a K and a cap then takes it anyway (§4.4 step 4). Reaching it needs
   a pattern whose byte ratio exceeds 0.75 while some ladder K brings CODE
   under 500,000 — and on node-replication patterns bytes and code move
   together, so a ratio above 0.75 keeps code above the cap. Five candidate
   shapes were probed and none reached it. **The overrides being RAISE-ONLY
   means the case cannot be forced by lowering a cap either**, so there is a
   shipped branch no test can currently drive. A test-only cap override is the
   proposed fix; it is a decision, not a measurement, because it adds a
   test-only surface to `limits.h`.

5. **Witness 2's mechanism belongs to [OPT-4]/K39, not here** (§3.3). This row
   PRICES the hybrid prefilter's inlined scan (the model now sees its states
   and jump tables) and REFUSES it past the cap; it does not shrink it. If
   Frank wants that population made compilable rather than refused, [OPT-4] is
   the row and this note's §4.2 numbers are its measured need.

---

## 11. What STEP 2's code phase builds, in cost order

**The largest piece is the plumbing, not the policy** (finding S1). The rule
itself is a loop; making the emitter runnable more than once into a
caller-chosen buffer is the work.

1. **The ladder as attempts in `compile_driver` (§2.2b).** Not the trial flag
   the design first specified: the loop [SEL-1] built already has the shape,
   so this is a phase machine over the existing `setjmp`, plus carried state
   in the style `overflow_why` established. It is NOT a new analysis, and
   deliberately so — a counting pre-pass would have to mirror
   `vm_counter_fits`' K-dependence (S3), possessification, revdet, splice and
   the MRL guard, with nothing keeping it in sync.
1b. **The early abort (§2.2c)**: `StrBuf.abort_over`, checked in `sb_grow`,
   armed on ladder attempts only.
1c. **The re-emission identity control (§2.2d)**, which replaced R3's
   sabotage and is what catches state leaking across attempts.
2. **The K selection (§3.3)** at that call site: the ladder, `argmin N`, the
   threshold gate and the materiality bar. Small, once (1) exists.
3. **The two caps (§4)**: the code-bytes cap on the ladder-chosen emission, the
   total-bytes cap as an exact post-emission check before the file is written,
   and §4.4's ladder re-run with the bar bypassed — which is the part a reviewer should
   read first, because it is what makes "cannot ship past a cap" true.
4. **The overrides (§4.5)**: two `pcrec_options` fields, two CLI flags,
   raise-only validation with a below-default value refused as malformed.
5. **The four stamps (§7.1)** including `_UNROLL_K_WHY`'s five states.
6. **The deny flag (§7.2)**, bit 17, and the registry re-pin (§7.3).
7. **The `abi` bump, four sites (§8).**
8. **The checks (§6.2, §7.4)**: the K sweep with its specified exclusions AND
   its give-up-code assertion on the excluded cells (R6), the structural check
   including the no-counter-rung case, the sabotage rows — including R3's
   `vm_publish_saves` row — R1's witness as a `.rxt` cell, and the
   byte-identity-against-explicit-`--unroll` control.
9. **The spec hunks (§7.2's table)**: `tuning.md` §2.15, `cli.md:218-224`,
   `match_api.md` §6.3 and §6, `limits.md`'s constants, its §7 sentence
   (finding S7) and its "Handling an oversized artifact" section (§4.6).
10. **The K41 and fuzz-gate hunks (§4.8)**, re-derived by RUNNING the gate,
    not widened — including `fuzz.py`'s new `size_cap` bucket on the
    `state_cap` precedent, without which a size refusal is counted as an
    accept/reject divergence.

It does **not** build any of census §7's three levers (§5), per-quantifier K
(§5.4, [ENG-CLAMP]'s), any prefilter-shrinking change ([OPT-4]/K39's — this
row prices and refuses, it does not shrink), or any model on the byte axis
(D84's addendum removed it).
