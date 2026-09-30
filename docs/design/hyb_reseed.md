# [OPT-HYB-RESEED] — when the VM hybrid's retry asks the prefilter again

Lane `reseed`, 2026-09-29. Chartered by Frank in the eighty-sixth session:
*"would it use freq or other data to decide? out-of-box: can it use live
stats to decide? if last run, or last 2 runs before next try < N, then don't
call dfa?"*, then *"charter it"*. The row is `docs/dev/plan.md`
`[OPT-HYB-RESEED]`. The defect and the first hand-twin are in
`docs/dev/utf8_attrib.md` (A) rows 1/10/11, the packaged twin in
`docs/dev/utf8_attrib_twin/I-114.md`, and the bench's x86 answer is O-68.
This note is the design section the brief asks for before the build. The
build and its measurements are in `docs/dev/lanes/reseed_report.md`.

## 1. The defect

A VM hybrid runs a DFA prefilter (`<p>_prefilter`) at the search ENTRY. The
prefilter hands the attempt loop the leftmost start of the capture-erased
language. When the VM attempt there fails, the loop advances one character.
It asks the prefilter again ONLY when an MRL clamp exists (`retry_win` in
`src/gen/emit_vm.c`, gated on `v->nclamp > 0`). That gate exists because the
clamp's window END must be recomputed (D51 ruling 2). It was never a
statement about speed.

So on a clamp-free hybrid, one failed attempt makes the loop step every
character boundary to the subject end, running a VM attempt at each.
A failed attempt can only follow a prefilter answer when the prefilter's
language is LARGER than the pattern's. The tree names exactly three such
sources: `src/ir/nfa.c` erases `A_ATOMIC` and `A_LOOK` to their bodies/ε,
and the `[OPT-4]` count collapse builds a superset. These are the three
conjuncts `Vm.mrl_win` already excludes.

## 2. D77: the census (measured before building)

`docs/dev/reseed/census.py`, every corpus `pattern` line, `--features all`,
both encodings, at the branch point (abi 46):

| encoding | hybrids | clamp-free exact | **clamp-free over-approx** | clamped exact | clamped over-approx |
|---|---:|---:|---:|---:|---:|
| byte | 1,082 | 309 | **439** (302 look, 100 atomic, 37 both) | 224 | 110 |
| utf8 | 1,101 | 304 | **455** (319 look, 99 atomic, 37 both) | 228 | 114 |

The defect's population is 439/455 artifacts, 40% of all hybrids. The
trigger is met. The 309/304 clamp-free exact hybrids are the population that
must NOT move. For them a failed attempt after a prefilter answer is the
span-equality claim R21 left "believed with gate", and re-asking would buy
nothing.

## 3. The measured crossover, and why it is per program class

Hand-twins of the emitted C, Mac M1, gcc-16 `-O2`. SCRATCH tier: these show
mechanism and ratio only. A subject family puts a FAILING candidate every
`g` bytes. At each g we compare always-step against always-re-seed:

| witness | frameless? | step ns/B | re-seed ns per call | crossover gap |
|---|---|---:|---:|---:|
| `(?<=é)x` (asr-lb-fixed) | yes | 1.65 | ~25 | ~16 B |
| `x(?=ab)` | yes | ~1.6 | ~25 | ~26 B |
| `(?<=ab)x` | yes | ~1.6 | ~25 | ~30 B |
| `(?<=a\|é)x` (asr-lb-varwidth) | no | 8.6 | ~25 | ~3 B |
| `(?<!日)本` (asr-lb-neg) | no | 2.8 (≈8.5 per char) | ~36 | ~3 chars ≈ 9-12 B |

The re-seed cost R is about constant, roughly one prefilter call. The step
cost S varies about five-fold, and the program's FRAME DISCIPLINE predicts
it. A frameless program (`<P>_VM_FRAMELESS 1`) fails a non-candidate
position in a few compares. A framed one pays a slot write, a trail entry, a
push and a pop per attempt. So there is no single N. There is ONE calibrated
constant per program class, read off `has_push`, the bool the frameless
stamp and the entry ladder already share:

| class | N (gap, bytes) | K (steps per step block) | first (probation steps) |
|---|---:|---:|---:|
| frameless | 16 | 64 | 8 |
| framed | 4 | 16 | 2 |

K = 4N and first = N/2 are rules, not separate fits. K*S is a few R, which
amortizes the probe re-seed in a dense run to under a quarter of R per step.
It also bounds the waste of one wrong step block to a few R. first = N/2 is
the ski-rental "rent for half the purchase price" start. These are
calibrated constants in one table (`vm_reseed_cal`, `src/gen/emit_vm.c`),
the `clskit.c` `PLACE` precedent. `--tune` does not move them today: the
dial's table is a pinned contract (D103), and a cell needs a measured
two-axis rate first. The table is where such a cell would point.

## 4. The mechanism: ONE first-match table, rows as data

`vm_reseed_rows[]` in `src/gen/emit_vm.c` is selected once per hybrid
artifact in the plan phase and stamped as `<P>_VM_RESEED`:

| # | row | deny | predicate | action |
|---|---|---|---|---|
| 1 | `exact` | — | the prefilter's language is exact (`Vm.mrl_win`: no cut, no lookaround, no collapse) | today's retry, unchanged: the clamp recompute where a clamp exists, else step |
| 2 | `adaptive-dense` | `-fno-hyb-reseed` | the prior's MASS on the candidate scan predicts a gap under N | ADAPTIVE, starting in STEP mode |
| 3 | `adaptive` | `-fno-hyb-reseed` | always | ADAPTIVE, starting after a `first`-step probation |
| 4 | `fixed` | — | always | today's retry (the deny's landing row) |

Row 2 is the brief's "a findings bundle present" row, rewritten to obey D126
Q4: a reader never tests the prior's NONE. The predicate hands the candidate
scan's byte set to the MASS primitive. Under NONE that primitive answers
CARDINALITY, so a singleton scan under `-e utf8` never looks dense and a
64-byte class does. That is the no-information answer, and it is spelled
once inside the primitive. The rate comes from `pcrec_dfa_cand_ppm`
(`src/gen/emit_dfa.c`): the MASS of the set the emitted scan tests, read off
the same derivations the scan is emitted from. It is 1,000,000 when the scan
tests nothing.

**ADAPTIVE** is two per-CALL locals in `<p>_search_run`. There are no
globals and no `rx_ctx` fields, so the matcher stays stateless and
reentrant.

- `reseed_steps_left`: failed attempts to STEP before the next re-seed.
- `reseed_short_gaps`: consecutive re-seed gaps under N, saturating at 2.

After each failed attempt's encoding advance, the loop does one of two
things:

- **Step mode** (`reseed_steps_left > 0`): decrement the counter and retry
  at the next character.
- **Otherwise, re-seed**: ask the prefilter from the current position, jump
  to its answer, and record the gap. The gap counts as short when it is
  under N. Two consecutive short gaps enter a step block of K.

Each step block ends in exactly one re-seed. That re-seed is the PROBE, so a
dense-then-sparse subject cannot stay stuck in step mode. Requiring TWO
short gaps is what defeats the alternating adversary (`xx` then a long gap,
repeated): its gaps read 0, L, 0, L and never enter step mode.

Soundness is today's on both arms. Stepping is today's clamp-free
behaviour. Re-seeding is today's clamped retry, and D51 ruling 2 already
states it as sound: the prefilter answers for `[attempt_position, n)` and
L(P) ⊆ L(erase(P)). Where a clamp exists and the row is adaptive, the
ceiling is `subject_length` on both arms (`mrl_win` is false on every
over-approximating artifact), so stepping cannot carry a stale window.

What can change is the GIVE-UP boundary, because the step budget is shared
across a call's attempts (f3search):

- On a clamp-free artifact, adaptive only removes attempts, so it can only
  turn a give-up into an answer.
- On a clamped over-approximating artifact, a step block runs attempts that
  today's always-re-seed skips, so it could turn an answer into a give-up.

The answer-identity sweep counts both directions.

## 5. Scratch results (full table in the report)

The two-gap rule with the class calibration stays near min(step, re-seed)
on every witness family. The worst measured cell is 1.75x min, on the
alternating adversary sitting exactly at the crossover. A per-call rule
cannot see ACROSS calls, so find-all over a match-dense subject re-learns
the density on every call. That is `asr-lb-fixed`/synth-dense, the one cell
where today's pure stepping stays ahead. The cross-call "last run" hint is
out of scope and filed as its own row, with this cell as the measurement
that would trigger it.

## 6. Out of scope, filed

- **The cross-call hint** (`[OPT-HYB-RESEED-XCALL]`). Its trigger is a
  measured short-subject / find-all cell losing to the per-call probe.
- **A cheaper re-seed.** R is a whole forward+reverse prefilter call, about
  25 ns, where the candidate scan alone would be a `memchr`. Seeding from
  the candidate scan without the verifying DFA would shrink R and move every
  crossover, and it is a change to the DFA emitter's interface.
- **`--tune` cells** for N and K (§3).
