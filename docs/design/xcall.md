# [OPT-HYB-RESEED-XCALL]: what the O-81 slow cells pay, and the mechanism that reaches them

Lane `xcalldes`, 2026-10-03. DESIGN ONLY: nothing under `src/`, `lib/`,
`tests/` or `docs/spec/` changes in this lane. This is round 1 of the
[OPTLOOP] cycle opened under D144. The row is `docs/dev/plan.md`
`[OPT-HYB-RESEED-XCALL]`, which has two occurrences. The mechanism it extends
is `docs/design/hyb_reseed.md`. Its trigger is bench O-81
(`docs/dev/summaries/2026-10-03-bench-o79-o82-notes.md`). Every number in
§2-§4 is in `studies/hyb_reseed_cal/shape/results/shape_2026-10-03.md`, and
the probes that produced them are next to it.

## 0. Verdict

**The cross-call hint reaches none of the 14 O-81 cells' measured cost.**
The row assumes the slow cells pay for re-learning candidate density on
every call. They do not. The probes give three findings:

- **12 of the 14 cells are single-call cells, or cells where the retry tail
  practically never runs.**
  - One search per short subject (ss).
  - One anchored match per subject (mc).
  - A find-all with zero matches, which is one call.
  - A find-all whose attempts never fail.
  - An anchored pattern with no second attempt.
- **A cross-call hint needs a second call on the same subject, and needs
  that call to reach the re-seed branch.** Most of those cells have no
  second call. Where they do (grp-atomic-alt thr, 308 calls), the re-seed
  branch is never reached. So the hint has nothing to carry.
- **The measured cost is the SHAPE of the emitted retry, not its
  behaviour.** On the Mac, a variant whose re-seed branch can never execute
  is still as slow as the shipped form: qnt-poss-quest find-all ×1.19 and
  short-search ×1.17, against ×1.275 and ×1.205 for the shipped form. The
  executed path has the same attempts as `-fno-hyb-reseed`. What differs
  is the code gcc makes for it: the out-of-line second prefilter call site
  sits inside the hot step loop, along with the per-step counter.

The two cells that are not shape-dominated split as follows:

- **asr-lb-varwidth synth-dense** makes many calls. Its Mac loss (×1.040)
  goes away in a call-free step-loop form (×0.994-×0.997) with no hint.
- **The two mc cells** run byte-identical C on both arms. Their deltas are
  code layout and no mechanism reaches them.

**What the hint does reach** is the Mac scratch witness `item(?= done)` on
match-dense prose (`lka_dense`):

- It makes 6,536 calls and 16,507 re-seeds, about 2.5 per call. That is the
  per-call re-learning, and it costs ×1.62.
- A scratch emulation of the hint brings it to ×1.14.
- No bench cell has that shape today. O-81 item 2 says no density-controlled
  lka pair exists.

**Recommendation.** Round 1's slot goes to **[OPT-HYB-RESEED-FORM]** (§4),
a re-spelling of the shipped mechanism in two parts:

- **A1.** A selection row that stops emitting the adaptive tail on artifacts
  that can never make a second attempt. That is 48 corpus artifacts, which
  is 79% of `adaptive-dense`.
- **A2.** A call-free, counter-free step loop.

XCALL itself is designed in §5, so its API is settled when needed, but its
build stays HELD under D77. Its trigger is restated as a bench find-all cell
that pays more than one re-seed per call. The bench is asked for a
density-controlled lka pair (§7, Q6).

## 1. The population and the regimes, from the bench's own code

What each regime does, from pcrec-bench `testees/pcrec/driver.c` (timing
loop, l.775-858) and `testees/pcrec/adapter.py` l.4321-4326:

- **ss** (`search_short`): ONE `<p>_search(s, n, 0, caps)` per subject,
  repeated `iters` times on the same subject.
  - There is no find-all.
  - syntax@0.1 has 42 short subjects, mean 18.8 B, max 86 B.
- **mc** (`match`, record enum `match-compliance`): `<p>_match_caps` at 0 on
  the WHOLE-SUBJECT artifact, the `(?:P)\z` wrap (match_api.md §3.6).
  - An anchored entry never enters the search body's attempt loop.
  - So the re-seed code cannot run on this regime at all.
- **thr** (`throughput`): `--find-all` over t-64k / t-256k / t-1m. One call
  per match, plus the final no-match call.

The O-81 population is 14 cells:

- 10 syntax cells: qnt-poss-quest ss ×1.2281 and thr ×1.1939; lka-verb ss
  ×1.0974 and mc ×1.0770; lka-pos ss ×1.0949 and mc ×1.0897; lka-neg ss
  ×1.0874; grp-atomic-alt ss ×1.0640 and thr ×1.0536; lka-nonatomic ss
  ×1.0566.
- capability logparse-atomic ss ×1.0690.
- 3 synthetic cells: asr-lb-varwidth gcc synth-dense 7.4%, asr-lb-fixed
  clang synth-1m 6.7%, asr-lb-fixed clang synth-64k-asc 6.5%.

## 2. What each cell pays

The counts come from an instrumented copy of each shipped artifact (`cnt.c`):

- main c231ffc1, abi 55, `--features all`.
- The bench's subjects were regenerated from its own generators into the
  scratchpad, writing nothing in the bench checkout. 45/45 match its
  manifests' sha256.
- The stamps are read off the artifact.

| O-81 cell | stamp (row, frame) | regime facts (calls / reaching VM / failed attempts / re-seeds) | XCALL reach | what it pays |
|---|---|---|---|---|
| qnt-poss-quest `a?+a` ss | adaptive, frameless | 42 / 22 / 465 / **2** | none: one call per subject | shape (§3) |
| qnt-poss-quest thr | same | t-64k: **1 call**, 61,157 failed, 350 re-seeds | none: zero matches, one call | shape, plus re-seeds at near-crossover gaps (§3) |
| lka-pos `item(?= done)` ss | adaptive, frameless | 42 / 9 / 104 / **0** | none | shape: the tail never re-seeds |
| lka-pos mc | — | anchored entry, no attempt loop | none | layout: executed C is byte-identical |
| lka-verb `item(*pla: done)` ss / mc | adaptive, frameless | same as lka-pos | none | as lka-pos |
| lka-neg `item(?! done)` ss | adaptive, framed | 42 / 9 / 6 / 2 | none | shape |
| lka-nonatomic `(?*item)item` ss | adaptive, frameless | 42 / 9 / **0** / **0** | none | shape: no attempt ever fails |
| grp-atomic-alt `(?>a\|ab)c` ss | adaptive, framed | 42 / 3 / 3 / 1 | none | shape |
| grp-atomic-alt thr | same | t-64k: 308 calls, **0** failed, **0** re-seeds | none: nothing to learn | shape/layout (Mac ×1.01, flat) |
| logparse-atomic `^(?>…): (.*)$` ss | **adaptive-dense, anchored** | at most one attempt per call (`RX_VM_START "anchored"`) | none | **dead text**: the retry is unreachable (§4 A1) |
| asr-lb-fixed `(?<=é)x` clang synth-1m / synth-64k-asc | adaptive, frameless | 0 matches: **one call** | none | not probed; a clang-only sign points at shape |
| asr-lb-varwidth `(?<=a\|é)x` gcc synth-dense | adaptive, framed | 22,505 matches: many calls | **the one reachable cell** | Mac ×1.040, which form F1 removes with no hint (×0.994-×0.997) |

So the population pays the shape of the text, not its decisions. The
mechanism itself barely runs on these cells. That is consistent with O-81's
own read that answers never moved, and with the bench's cells sitting at the
×1.05-×1.23 scale rather than the per-call model's ×1.6.

## 3. The shape, measured (Mac M1, gcc-16 `-O2`, SCRATCH, directional)

**Method.**

- Each binary is launched 6 times round-robin with the deny binary, and
  each launch is the median of 7 passes.
- Short-search cells are summed over the 42 subjects. Find-all cells are
  summed over t-64k plus t-256k.
- "deny" is the `-fno-hyb-reseed` artifact: the `fixed` row, today's
  pre-reseed retry.
- The box was at load 2-5 with other lanes running.

**The noise reference** is the match regime. Its executed C is
byte-identical between arms, and it still reads ×0.98-×1.05. A ±5% reading
on a ~1-15 ns-per-call cell is therefore layout, not mechanism.

| cell | shipped | never-re-seed control | forced-inline prefilter | F1 | F2 | F3 |
|---|---:|---:|---:|---:|---:|---:|
| qnt-poss-quest ss | ×1.205 | ×1.174 | ×1.103 | ×1.053 | ×1.407 | ×1.151 |
| qnt-poss-quest thr | ×1.275 | ×1.193 | — | **×1.086** | ×1.742 | ×1.242 |
| lka-pos ss | ×1.018 | ×1.020 | ×0.946 | ×1.072 | ×1.049 | ×1.013 |
| lka-pos thr (sparse: a win) | ×0.888 | ×1.335 | — | ×0.882 | ×0.887 | ×0.885 |
| lka-neg ss / thr | ×1.032 / ×0.988 | — | — | ×0.968 / ×0.944 | ×0.938 / ×0.981 | ×1.013 / ×0.989 |
| lka-verb ss / thr | ×1.016 / ×0.884 | — | — | ×1.072 / ×0.883 | ×1.048 / ×0.886 | ×1.015 / ×0.892 |
| lka-nonatomic ss | ×1.008 | ×1.009 | ×0.915 | ×1.047 | ×1.035 | ×1.005 |
| grp-atomic-alt ss / thr | ×1.007 / ×1.011 | — | — | ×0.971 / ×1.011 | ×0.979 / ×0.994 | ×1.002 / ×1.015 |
| asr-lb-varwidth synth-dense | ×1.040 | — | — | **×0.997** | ×0.994 | ×1.035 |
| asr-lb-varwidth synth-1m (a win) | ×0.382 | — | — | ×0.363 | ×0.364 | ×0.382 |
| lka_dense (scratch, per-call) | ×1.619 | — | — | ×1.528 | — | ×1.533 |

(Ratios are form / deny; lower is faster.)

The forms:

- **The never-re-seed control** is the shipped text with `steps0` set to 4e9,
  so the re-seed branch is present and never runs.
- **F1** has one prefilter call site in an outer seed loop, and an inner
  step loop whose only exit test is `attempt_position >= step_end`. There is
  no call and no counter in the inner loop.
- **F2** is F1 with the run-state init moved onto the entry pass only.
- **F3** keeps today's entry. The step budget becomes a position bound, and
  the re-seed sits in a cold `__builtin_expect` branch inside the loop, so
  there are two call sites.

What the table says:

1. **The cost is the text's presence, not its execution.** The control
   reproduces qnt-poss-quest's loss with zero extra re-seeds. On lka-pos thr
   the control is ×1.335 slower than deny: a branch that never fires made
   gcc's hot loop that much worse.
2. **Where the second call site goes decides most of it.** F1 restores
   qnt-poss-quest thr from ×1.275 to ×1.086, and asr-lb-varwidth
   synth-dense from ×1.040 to ×0.997. It keeps every win: lka-pos thr
   ×0.882, varwidth synth-1m ×0.363. F3 keeps two call sites and does not
   fix qnt-poss-quest.
3. **gcc's codegen of this loop is FRAGILE.** F2 is semantically identical
   to F1 and differs only in where four stores sit, yet it takes
   qnt-poss-quest to ×1.742. One form's numbers on one compiler do not
   predict the next. The form must be chosen by measurement on the bench's
   compilers (x86 gcc AND clang), not on this Mac. The asr-lb-fixed
   clang-only cells say the same thing.
4. **F1's cost on short search** (lka-* ×1.05-×1.07, about +0.8 ns per call)
   comes from hoisting the run-state init above the entry prefilter. 33 of
   42 subjects return from that prefilter with "no candidate" and now pay the
   init. F2 avoids that and breaks the loop. A form that has both properties
   is the build's first task (§4 A2).
5. **The residual ×1.086 on qnt-poss-quest thr is policy, not shape.**
   - It comes from 350 re-seeds at gaps around the 16 B crossover, because
     one long gap disarms the block.
   - It is a candidate tuning (halve rather than reset). It is unmeasured,
     so it is not part of this round.
6. **A first-byte `memchr` per step is not a substitute** (×1.51 slower
   than deny on lka_dense: one library call per position in a dense
   region). The candidate-start skip belongs to [OPT-FIRSTSET]'s VM
   consumer, at the inline-test grain, if anywhere.

## 4. The mechanism that reaches the population: [OPT-HYB-RESEED-FORM]

Two parts, one abi event each or one together. Both keep `-fno-hyb-reseed`
as the deny, both leave answers unchanged, and both keep the attempt set
unchanged on every artifact under `-e byte`. A2's unit change under `-e utf8`
(below) moves where re-seeds happen; answers stay unchanged there too.

### A1. A `single-attempt` row: no adaptive tail where no second attempt exists

**The census** (byte, `--features all`, 3,424 corpus patterns, at c231ffc1):

| `RX_VM_RESEED` × `RX_VM_START` | anchored | gstart | unanchored |
|---|---:|---:|---:|
| adaptive | 0 | 0 | 378 |
| adaptive-dense | **47** | **1** | 13 |
| clamped | 11 | 0 | 99 |
| exact | 99 | 4 | 445 |

- **All 48 start-anchored adaptive artifacts are `adaptive-dense`.** The
  dense predicate reads `pcrec_dfa_cand_ppm`, which is 1,000,000 "when the
  scan tests nothing", and an anchored pattern's scan tests nothing.
- On those artifacts `[OPT-ANCHOR-VM]`'s bound (`attempt_max =
  search_from`) returns before the retry tail can run. gcc cannot prove it,
  because the seed comes from the prefilter, so it emits the text anyway.

**The row.** Add `anchored` to `pcrec_reseed_rows` after `clamped`:

- Predicate: `pcrec_fact_start_anchor(v->cx) != PCREC_SANCH_NONE`. That is
  the shared fact `att_max` already reads, so there is one derivation, not
  two.
- Action: FIXED. Undeniable, for the reason `exact` is: the choice does not
  exist.
- The result is that 79% of `adaptive-dense` artifacts stop carrying dead
  text. That is logparse-atomic's ss cell.
- Under this row an artifact's C equals its `-fno-hyb-reseed` artifact's C,
  except for the stamp string. That makes "parity with deny" true by
  construction, and the codegen block can CHECK it.

**The ritual.**

- The `RX_VM_RESEED` value set gains `"anchored"`: spec `tuning.md` §2.35,
  `match_api.md` §6.3's value set, and the registry value-set leg.
- abi bump (the 48 artifacts' text moves) and identity re-pin.
- The reseed census (`docs/dev/reseed/census.py`) is re-run.
- Sabotage: delete the row, and the codegen equality check goes red.

### A2. The call-free step loop

Replace the adaptive tail (`emit_vm.c` `retry_seed`/`reseed_decl`) with a
form that meets three requirements:

- **(R1)** The inner step loop is today's fixed loop with ONE changed
  operand. Its exit test `attempt_position >= subject_length` becomes
  `attempt_position >= step_end`, and step mode sets
  `step_end = min(seed + block, n)`. No counter and no call sit inside it.
- **(R2)** The prefilter keeps the call-site count that lets gcc treat it as
  the fixed arm does. F1 achieves this with one site, by making the entry
  and the re-seed the same call in an outer seed loop. The emitter already
  wants one spelling of "ask the prefilter", per the D51 ruling 2 comment.
- **(R3)** A call the entry prefilter answers "no" does no more work than
  the fixed arm. Neither F1 nor F2 satisfies both R2 and R3 cleanly on gcc-16
  arm64, so the build's first step is a 2-3-form bake-off on x86 gcc and
  clang (§6). Starting points:
  - F1;
  - F1 with the init as a guarded first-pass block written so gcc keeps
    `ctx` in registers;
  - F3 plus a forced-inline prefilter.

The machine is unchanged: the same gap, arm, double and cap rules, and the
same start columns. Two consequences:

- **Under `-e byte` the attempt set is IDENTICAL** to the shipped machine's.
  `step_end` counts the same positions the counter did, so answers and the
  one-direction contract (match_api.md §6, the abi-49 paragraph) are
  untouched.
- **Under `-e utf8` the block becomes a BYTE budget, not a character
  budget.** The gap column is already in bytes. This needs a `tuning.md`
  §2.35 sentence and a re-run of the utf8 calibration witnesses (`cjk*`,
  `asr-lb-*`). The alternative, keeping a character count, puts the counter
  back in the loop (Q3).

**Ritual.**

- abi bump.
- The `[OPT-HYB-RESEED]` calibration check in
  `tests/codegen/run_codegen_tests.sh` re-reads the literals from the new
  spelling.
- S370/S371/S372 anchors are re-aimed: grep `tests/mech/sabotages/` for
  `reseed_steps`/`reseed_block`, and treat the hit count as a floor
  (coding_guide §3.5).
- Re-run the identity sweep (rows: adaptive moves, deny == base).

**Size.** A1 is S. A2 is S-M: one emitter site (about 40 lines of emitted
text), plus the form bake-off, which is the real cost.

## 5. XCALL itself: the design, HELD

### What it reaches

A find-all over a subject whose failing-candidate density is stable across
matches, on an over-approximating hybrid. The witness is `lka_dense`:

- 2.5 re-seeds per call, ×1.62 shipped.
- Emulated hint ×1.14.
- The emulation leaves the sparse wins intact (lka_sparse ×0.786 vs ×0.790;
  t-64k+256k ×0.884 vs ×0.888).

Its D77 trigger, restated: **a bench find-all cell whose calls average more
than one re-seed**, which is the measured signature (§2), losing to
`-fno-hyb-reseed`. No O-81 cell meets it.

### API options

These are ranked; the recommendation is (B2).

| | shape | verdict |
|---|---|---|
| B1 | a field in `rx_buffers` (the `_in` descriptor) | **rejected**: `const`, per-prefix type, a storage role, and reaches only `_in` callers |
| B2 | ONE new entry `<p>_search_ex(subject, n, from, caps, const rx_buffers *buffers, pcrec_search_state *state)`, both pointers nullable | **recommended**: one entry rather than a hint×`_in` cross-product; NULL/NULL is `_search` |
| B3 | a find-all iterator entry `<p>_find_next(pcrec_find *it, caps)`, caller-owned, carrying subject, position and state | strongest binding of the hint to "same subject, next position", and it would own §3.1's advance (the KB-17 hazard every caller re-implements); but it CONTRADICTS match_api.md §3.1's "no batch find-all primitive … none is planned for v1", so it is a Frank ruling |
| B4 | a global or thread-local | **forbidden**: §5.3's reentrancy contract and TS-1 |

### The state: `pcrec_search_state`

- It goes in the unprefixed pcrec-contract namespace (match_api.md §2's
  fixed ABI types), so ONE type serves every artifact. It is two `uint32_t`.
- The contents are UNSPECIFIED to the caller. The rule is "zero-initialize
  it; pass the same object to consecutive calls; any value is safe".
- Opaque contents let the machine change without a type change.

### Update rule (adaptive artifacts only)

All other artifacts ignore the pointer.

- **Entry.** If `state` is non-NULL and its block is nonzero, the call
  starts INSIDE an armed block of that length, clamped to the class `cap`.
  Otherwise it takes the row's own start columns.
- **Every return.** Write the call's final `reseed_block` back. That is 0
  when the last gap disarmed it.

**Safety.** No value can change an answer, because both arms are sound
(hyb_reseed.md §4). A garbage or foreign hint therefore costs at most one
`cap` block of steps before the probe re-seed. A hint carried to a new
subject costs the same.

### Thread safety

The state is caller-owned, exactly like `caps`. Two concurrent calls sharing
one state object is a data race in the CALLER, which §5.3 gains one sentence
to say. The matcher still holds no mutable state of its own, so TS-1/TS-2 are
unchanged.

### Zero cost when absent

- The un-suffixed `_search` passes a constant NULL into the search body. On
  frameless artifacts that body is `always_inline`, so both branches fold
  away.
- On framed artifacts (a `static int` body) it costs two predictable
  branches per call. That is unmeasured, and §6's ss witnesses carry it.

### Deny

`-fno-search-state` takes the next free bit (42 at c231ffc1). The entry is
still exported, for a stable ABI, and ignores the pointer.

### Contract and abi

Every item here is caller-observable (D80), so all of it is in the same
commit:

- A new entry: §3, and the "Eight is what an artifact exports" sentence
  becomes nine.
- The new type in §2.
- §5.3's sentence.
- §10's descriptor note.
- The abi changelog in §6.
- The TS-1 scan list.
- The CLI `--emit-main` scaffold, if it demonstrates find-all.

**pcrec-bench must opt in**, because its shim calls `_search`/`_search_in`.
That is an inbox item, and without it no bench cell can ever show the gain.

### Tests

- **Answer identity.** A driver runs find-all through `_search` against
  `_search_ex` with NULL, zeroed, persistent and garbage (`0xFFFFFFFF`)
  states, at every startpos, over the corpus subjects.
- **The deny axis** goes in `test-axes`.
- **A round-trip check.** After a dense find-all the caller-visible state is
  nonzero, and after a sparse one it is zero.
- **Sabotage, two rows.**
  - Write-back deleted: the round-trip check goes red.
  - Read deleted: the codegen structural check (the adaptive body reads
    `state`) goes red.

**Size: M.** One entry, one ABI type, five spec sections, a bench shim
change, and checks.

## 6. Alpha witnesses and the pcrec-side timing protocol (D144 item 1)

**Improve:** qnt-poss-quest ss and thr, lka-pos ss, lka-verb ss, lka-neg ss,
lka-nonatomic ss, grp-atomic-alt ss and thr, logparse-atomic ss (A1),
asr-lb-varwidth synth-dense, and asr-lb-fixed synth-1m and synth-64k-asc
(clang).

**Keep** each within the floor of its shipped win: lka-pos and lka-verb thr,
asr-lb-varwidth synth-1m, asr-lb-neg synth-1m, and the gap64/bursty
families. For XCALL only, add lka_dense.

**Protocol** (Linux box, through the manager's pcrecdev2 channel; never a
lane's own ssh suite run):

- **Builds.** base = main, new = the branch, deny = the branch with
  `-fno-hyb-reseed`. Each witness artifact is built with `gcc -O2` AND
  `clang -O2`, the bench's two compilers.
- **Subjects.** syntax@0.1 from `shape/regen_bench_subjects.py` (sha-verified
  against the bench manifests), capability's logparse subjects regenerated
  the same way, and `../subjects.py` for synth-* and lka_*.
- **Running.**
  - `taskset -c N` on one core, the same core for all arms.
  - 15 fresh launches per binary, round-robin (I-114: the x86 bimodal
    per-process state).
  - Loops calibrated to at least 50 ms (the bench's pinned-record rule,
    O-82 Q5).
  - The `rr.sh`/`sdrv.c` regimes (s/m/f), so ss and mc are timed the way
    the bench times them.
- **Noise floor.**
  - base/deny for A2: under the deny both are the fixed row, the same
    program.
  - A1's own equality (new == deny text).
  - The mc regime, which runs byte-identical executed code.
- **Accept.**
  - Answers are identical on every row.
  - Every improve-cell reads new/deny ≤ the floor's upper edge on BOTH
    compilers.
  - No keep-cell loses more than its floor.
- **Mac.** Mac numbers are directional only and never accept.

## 7. Questions for the manager

1. **Re-point round 1's slot from XCALL to [OPT-HYB-RESEED-FORM] (A1+A2)?**
   Recommendation: yes. XCALL reaches 1 of 14 cells (varwidth synth-dense),
   and F1 already recovers that cell without an API.
2. **A1 as an undeniable row with no flag of its own?** D144 item 4 says
   every optimization carries its own deny. A1 is a selection correction
   whose landing text equals the deny's. Recommendation: no new flag;
   `-fno-hyb-reseed` remains the kill switch.
3. **A2 under `-e utf8`: a byte budget (a spec sentence plus a utf8
   re-calibration), or keep a character count (the counter returns to the
   loop on utf8 only)?** Recommendation: a byte budget. The gap is already
   bytes, and one spelling serves both encodings.
4. **A2's form is chosen by an x86 gcc+clang bake-off before the emitter
   text is written.** That spends one pcrecdev2 run on hand-rewritten
   artifacts (this study's `mkbound.py` and `mkb3.py`) first. Recommendation:
   yes. F2's ×1.742 shows the Mac cannot pick the form.
5. **XCALL's API, when its trigger is met: B2 `_search_ex` with an opaque
   `pcrec_search_state`, or B3, a find-all iterator?** B3 needs Frank to
   lift §3.1's "no batch find-all … for v1". Recommendation: B2 now as the
   design of record, B3 raised with Frank as the better long-term shape.
6. **Ask the bench (inbox) for a density-controlled lka pair**, the same
   pattern on a match-dense and a match-sparse throughput subject (O-81 item
   2 says none exists), so XCALL's restated trigger can be read on the
   bench tier. Recommendation: yes, after A1+A2 land, so the pair reads
   the per-call cost rather than the shape cost.
7. **File the re-seed policy residual** (qnt-poss-quest thr ×1.086 under F1:
   one long gap disarms; halve instead) as its own unmeasured candidate,
   not part of round 1? Recommendation: yes. It needs a sweep, not a guess.
8. **Note to the bench:** on hybrids the mc regime's deltas are code layout.
   The executed function is byte-identical between arms, and the Mac reads
   ±5% on it. Should that go in the next inbox as a noise-model input?
   Recommendation: yes, one sentence.
