# [OPTLOOP.2] — READING THE ADMISSION FIX'S ACCEPTANCE LEDGER ([B84], O-52) AGAINST I-102

Lane `b84read`, 2026-09-25, branch `lane/b84read` from `4080ee34`.
Analysis plus compile-side and step-count measurement: nothing under `src/`,
`cli/`, `lib/` or `tests/`; nothing written in `/Users/fdicostanzo/pcrec-bench`
(read-only; its `git status` is clean after every step, and its Python modules
were imported with `sys.dont_write_bytecode`). **Every timing below is the
bench's Ryzen 1600 measurement** read from its own committed records, except
one darwin wall-clock reading used only as a cross-check and labelled where
it appears. Step counts, byte counts and stamps are exact.

**The bench REPORTS and does not diagnose (D78 / I-57). This file is the
diagnosis.** Template: `cycle2_batch2_reading.md` (stamps read off emitted
artifacts, cost models that predict absolute after-values, a null control).

**Sources.** pcrec-bench `docs/dev/outbox_to_pcrec.md` O-52 (commit
`9db4157`); the ledger `docs/dev/ledgers/2026-09-23-precheck-admit-after-6ef76820.md`
(685 lines); the ask I-102 as sent (bench `inbox_from_pcrec.md`) and as
drafted (`cycle2_batch2_reading.md` §8); the batch-1 ledger
`2026-09-23-optloop1-batch1-after-8d716693.md` (for the 29-cell list, §4); the
bench's own records for FOUR pcrec pins — `25b1984f` (batch-1 BEFORE),
`8d716693` (batch-1 AFTER), `b1885a83` (batch-2 AFTER = I-102's BEFORE),
`6ef76820` (the fix) — reduced with the bench's own `pcrecbench.reduce`
(`read_record` / `cells_from_record` / `reduce_set_cell`, Type-7 IQR), which
reproduces every ledger median I cross-checked to the printed digit.

**The two compilers this lane built**, by `git archive REV` into a gitignored
scratch tree and `make CC=gcc-16 build/pcrec`: `b1885a83` and `6ef76820`.
Every artifact pair was emitted to the same `-o` basename in two directories.
Instruments and transcripts: `docs/dev/optloop/admitfix/` (its own
`CLAUDE.md`).

Δ% convention throughout is the ledger's: **a positive Δ% is SLOWER.**

---

## FINDINGS FIRST

1. **The new give-up is real, and it is the fix's own defect.** It is also
   an old outcome coming back. Reproduced exactly on darwin: at `6ef76820`
   under `--features all --engine=vm`, `email-nested-plus` returns
   `PCREC_ERR_STEPS` on the same five subjects (500,000,001 steps each); at
   `b1885a83` all 75 subjects answer. **At `25b1984f`, the batch-1 BEFORE, the
   same five subjects gave up in the same way.** Batch 1's necessary-byte
   pre-check fixed them, without anyone intending it, and G2 removed that
   pre-check. Across all four pins this pair of cells is the only one whose
   pass/fail ever changed.
   - **The mechanism:** `^([a-zA-Z0-9._%+-]+)+@` backtracks exponentially over
     a leading run of class bytes. The step count is exactly `3·2^(L−2) − 2`
     at the end of a subject, so the 500M budget runs out at L = 30.
     `memchr('@')` used to prove no-match before the attempt ran. On the
     `auto` route a linear-time hybrid DFA with an exact language does the
     same job, so auto is unaffected.
   - **Classification:** a defect in the fix. The spec text G2 shipped with
     (`docs/spec/tuning.md` §2.29) states two things that are false on a
     step-budgeted backtracking VM: "the single attempt reads at most the same
     window", and "the check could only ever return the answer the engine
     below it then returns anyway". The engine can instead return a give-up.
     The outcome itself is still inside the resource contract: `limits.md` §1
     says a give-up is never a false answer. It is also a divergence from
     PCRE2. The 10.46 reference answers "No match" on these subjects because
     it applies its own last-code-unit check to anchored patterns on subjects
     shorter than 5,000 bytes. The boundary was measured on the reference box.
   - **Filed as K64** with a proposed fix, not built (§1.8).

2. **The (c) miss is noise. The cell was also never the mechanism's target.**
   `wild-codegrammar-json-array-begin`'s forced-VM artifact is
   **program-identical** across the pin: only the abi digit and the new stamp
   line differ. `REQ_WHY` reads `emitted` because the artifact has no
   candidate-start scan for G1 to find. `vm-caps` moved −0.25% and
   `vm-in-caps` +1.84% on one shared build. The null band for this pin pair
   at this scale runs −8.18% to +6.75%, and the move sits well inside it.
   I-102(c)'s "all four testees" over-reached: the two forced-VM cells should
   have been no-move controls.

3. **The grid.** Scored against I-102's own letters, with a scale-matched
   null band this lane computed for this pin pair (394 cells on 146
   program-identical artifact-configs):
   - (a) 4/4, (b) 8/8, (d) 8/8 meet.
   - (c) is 2/2 on the cells the mechanism can reach, and the two forced-VM
     cells are null.
   - (f)/(g), the six meeting targets used as no-move controls: 6/6 within
     band, on artifacts that are program-identical.
   - (h), router/keyword: 8/8 within band (all moves within ±0.18%), on
     program-identical artifacts, exactly as predicted.
   - The (b) forced-VM miss of the absolute prediction (7,207 ns, not ~47 ns)
     is finding 1's mechanism at small scale. The first attempt costs
     `2^(L+1) − 2` VM steps over each throughput subject's leading class run
     (L = 7, 5, 8), 826 steps in total. At the 7.9-9.2 ns/step solved from 20
     other subjects in the same record, that predicts **6,525-7,600 ns**
     against a measured 7,207/7,257.

4. **The 29 G2 cells, itemized** (§4). The count's section numbers refer to
   the BATCH-1 LEDGER's tables (its §1.2 carve-outs, §2.1 and §2.2), not the
   reading's. That is why the bench could trace only 12. **Scored: 27/29
   improve beyond the band and 2/29 fall inside it.** Every one of the 29
   lands at or below its batch-1 BEFORE value, apart from floor-scale noise.
   I-102(e) is **MET** on its own population. The 72-cell superset's 16
   band-clearing regressions (plus the 2 give-ups) are all the same mechanism
   as finding 1. G2 removed a pre-check that was a cheap no-match proof on
   short subjects. Against `25b1984f`, before any pre-check existed, every
   DFA-route superset regression sits within ±3.4%, and every forced-VM one
   is still 75-100% faster.

5. **Dispositions** (§6; Frank rules).
   - **[OPT-FREQPICK]: DEFAULT-ON, precondition met.** Its one hazard
     (`wild-validator-email-owasp`'s 500× floor jump) is gone on 4/4 configs,
     and its target stays unmoved.
   - **[OPT-REQPOS] tier 2b: DEFAULT-ON stands.** The router/keyword residual
     is unchanged to ±0.18%, because the fix was never going to reach it. It
     is now +82.8%/+69.4% over the batch-1 BEFORE on the DFA route, and
     [OPT-LITSCAN]'s "a DOMINATED pre-check is ELIDED" clause owns it.
   - **[OPT-PRECHECK-ADMIT]: keep merged, and keep the row `STATE:started`
     until K64's fix lands.** The G2 rule needs its VM arm narrowed. The
     search-regime value G2 gave back is a measured question for cycle 3,
     not a defect.

---

## 0. THE INSTRUMENT

### 0.1 Four pins from the bench's own records, with the bench's own reducer

`admitfix/cells.py` reduces all 16 records (4 pins × 4 testees) into 1,992
set cells. Checks against the ledger: `wild-validator-email-owasp` thr
`auto-caps` reads 23,158.8185 → 37.0030; `email-nested-plus` thr `vm-caps`
reads 7,206.878; `json-array-begin` thr `vm-in-caps` reads 1,114,970.975;
`email-nested-plus` srch `vm-caps` at `6ef76820` fails on the same five
subjects with `{'-2:PCREC_ERR_STEPS': 25}`. **Every value agrees to the
printed digit.** `25b1984f` has two windows per testee. The batch-1 ledger's
BEFORE is the later one (2026-09-22), which is the one read here, and it
reproduces that ledger's 492.620 / 19.930 exactly.

### 0.2 The null control — 146 of 192 artifact-configs are program-identical

`admitfix/nullctl.py` is `b2ledger/nullctl.py` re-pointed at this pin pair.
It ignores the generated-by comment, `.abi`, and the fix's own new
`RX_REQ_WHY` line.

| identity at 6ef76820 vs b1885a83 | artifact-configs |
|---|---|
| program-identical | **144** (+2, see below) |
| changed | 41 = **27 `one-attempt` + 14 `dominated`** — exactly the declining set |
| refused at both pins | 5 |

The two "changed" `emitted` artifacts are `wild-logparse-syslogbase-expanded`
on the two auto configs. Their only difference is the size figure inside
`RX_VM_PREFILTER_LANG_WHY` ("exact 1463264 > 1000000" → "1463293"), which
moves because the new stamp line adds 29 bytes to the counted C. That makes
them program-identical in substance, so **146** in all. **Every changed
artifact is a decline, and every decline is a change.** The `REQ_WHY` census
reproduces the ledger's and the reading's figures by value: `none` 79,
`emitted` 67, `one-attempt` 27, `dominated` 14. That makes it the sixth
derivation.

**The null band for this pin pair** (`admitfix/nullband.py`) is the Δ% over
394 cells sitting on those 146 artifacts, banded by regime and BEFORE scale
(I-104's bands):

| band | n | min | max |
|---|---|---|---|
| thr ≥ 1 µs | 160 | −8.18% | +6.75% |
| thr 100 ns-1 µs | 6 | −0.36% | +0.35% |
| thr < 100 ns | 33 | −29.68% | **+12.51%** |
| srch ≥ 1 µs | 130 | −7.07% | +2.56% |
| srch 100 ns-1 µs | 65 | −3.80% | **+11.85%** |

These are narrower than batch 2's (+41.09% at floor scale) and in line with
cycle 1's. Cells are scored below as `IQR / band`, where the band verdict
requires `|Δ| > max(IQR, band edge on the Δ's own side)`.

---

## 1. THE NEW GIVE-UP

### 1.1 Reproduced on darwin, both pins, the bench's flags and subjects

The 75 short subjects were regenerated from the bench's own
`gen_subjects.build()` (**sha256 75/75** against its `manifest.tsv`), and the
three throughput subjects from `captext.text` (**3/3** against
`manifest_throughput.tsv`). The pattern was compiled under the bench's configs
(`testees/pcrec/configs.toml`: `vm` = `--features all --engine=vm`, `auto` =
`--features all`). Each artifact was instrumented with one line after
`rx_search_run` returns (`g_steps = RX_STEP_BUDGET - run.steps_left`) so the
driver prints the VM steps each call consumed (`admitfix/giveup_repro.sh`,
transcripts in `admitfix/transcripts/`).

| pin | config | rc histogram over 75 subjects |
|---|---|---|
| b1885a83 | vm | 71 no-match, 4 match |
| b1885a83 | auto | 71 no-match, 4 match |
| **6ef76820** | **vm** | **5 × `-2` (PCREC_ERR_STEPS)**, 66 no-match, 4 match |
| 6ef76820 | auto | 71 no-match, 4 match |

The five are **the bench's five by name**: `sd-empty-alt-hit`,
`sd-empty-alt-miss`, `sec-github-pat`, `v-uuid-badnibble`, `v-uuid-valid`.
Each consumes **500,000,001 steps**, which is the default budget
(`RX_STEP_BUDGET 500000000LL`) plus the step that tripped it. The expected
answer, from `expectations.tsv` (the libpcre2 10.46 differential), is
`nomatch` for all five.

### 1.2 It is not new — the same five gave up at batch 1's BEFORE

| pin | `email-nested-plus` srch `vm-caps` / `vm-in-caps` |
|---|---|
| `25b1984f` (batch-1 BEFORE; no pre-check existed) | **the same 5 subjects, `gave-up`, `-2:PCREC_ERR_STEPS` ×25 per testee** |
| `8d716693` (batch 1: [OPT-REQBYTE] adds `memchr('@')`) | 75/75 pass |
| `b1885a83` (batch 2) | 75/75 pass |
| `6ef76820` (the fix: G2 declines the pre-check) | **the same 5, the same code** |

The batch-1 ledger recorded the first transition at its §2.4 ("expectation-
failing BEFORE only"). The B84 ledger's "the ONLY cell … where a subject that
passed BEFORE fails AFTER" is correct for its pin pair. A scan of all 1,992
cells over all four pins finds **exactly two cells whose pass/fail state ever
changed, and they are these two**, cured by batch 1 and reverted by the fix.

### 1.3 The mechanism, read off the artifact

The whole forced-VM diff between the pins, abi digit aside:

```
> #define RX_REQ_WHY "one-attempt"
< #include <string.h>
<     if (subject_length <= search_from ||
<         !memchr(subject + search_from, 64, subject_length - search_from))
<         return 0;
```

The artifact is `RX_VM_START "anchored"`, `RX_VM_PREFILTER "none"` and
`RX_VM_FRAMELESS 0`. With no pre-check, its one attempt runs
`([class]+)+` over the subject's leading run of class bytes and backtracks
through every partition of that run before failing on the absent `@`. The step
count is exact and exponential:

| subject | leading class run L | steps at 6ef76820 | form |
|---|---|---|---|
| throughput `t-256k` / `t-64k` / `t-1m` | 5 / 7 / 8, then a non-class byte | 62 / 254 / 510 | `2^(L+1) − 2` |
| `a`×8, 16, 20, 24, 28, 29 (to end of subject) | = length | 190; 49,150; 786,430; 12,582,910; 201,326,590; 402,653,182 | `3·2^(L−2) − 2` |
| `a`×30 | 30 | **500,000,001 → `-2`** | budget exhausted |
| the five bench subjects | 36 (uuid), 60-61 (`sd-empty-alt`: `a`s then a digit, which is in the class), 93 (`github_pat_…`, `_` in the class) | **500,000,001 → `-2`** | |

**Any subject whose leading class run is 30 bytes or more and which carries no
`@` gives up on the forced-VM route at `6ef76820`.** At `b1885a83` the same
subject returned no-match after one `memchr`.

**The cost model predicts the bench's absolute numbers.** Twenty subjects in
the same `6ef76820` `vm-caps` record now run the VM and complete. Their
measured per-subject medians divided by their exact step counts give
**7.9-9.2 ns/step** (proportional, no intercept), across 126 to 786,430 steps.
For example, the three 786,430-step subjects measure 6.31-6.38 ms, i.e.
8.03-8.12 ns/step. At ~8.1 ns/step, a give-up call costs about 4 s on the
Ryzen; the darwin reading is 3.17 s per give-up (6.3 ns/step), the one clock
this lane read. The same model prices §2's (b) miss.

### 1.4 Why the `auto` route is untouched, at both pins

`auto-caps` compiles the same pattern to `RX_ENGINE "vm"` with
`RX_VM_PREFILTER "hybrid"` and **`RX_VM_PREFILTER_LANG "exact"`**. A
linear-time DFA over the pattern's exact language runs in front of the VM, so
the no-match proof the pre-check provided is still there. On the five subjects
`auto-caps` goes from ~11 ns to 32-76 ns (a DFA walk of the class run at
~0.6-0.75 ns/byte), not to a give-up. `auto-nocaps` is `RX_ENGINE "dfa"`,
which is linear by construction.

**On the auto routes, all 18 one-attempt artifact-configs (9 patterns × 2)
are DFA or exact-hybrid VM. On the forced-VM route all 9 are unguarded VM, and
6 of those are framed (`RX_VM_FRAMELESS 0`: `email-nested-plus`,
`ipv4-near-miss`, `wild-datetime-moment-iso8601`, `wild-validator-email-owasp`,
`wild-validator-ipv4-owasp`, `winpath-near-miss`).** The frameless three
(`logparse-atomic`, `-removed`, `uuid-near-miss`) cannot backtrack.

### 1.5 The contract, and PCRE2

- `docs/spec/limits.md` §1: *"a give-up is never a false answer"*; §2:
  `PCREC_ERR_STEPS` fires when §3.1's budget is exhausted; §3.1: default
  500,000,000 (D51), a robustness bound "not a latency guarantee (D22)". The
  budget is **per call**: `rx_search_run` calls `rx_run_state_init` on entry,
  and here one call is one attempt. **The give-up is contract-legal.**
- `docs/spec/tuning.md` §2.29, G2's own statement, is **false** on this
  artifact in two sentences:
  - *"a pass over the whole window can only add work: the single attempt reads
    at most the same window, and the check that precedes it can at best
    replace an O(n) walk with an O(n) scan."* A backtracking attempt is not an
    O(n) walk.
  - *Answer-identity: "the check could only ever return the answer the engine
    below it then returns anyway."* The engine below it returns a GIVE-UP
    where the check returned NOMATCH.
- **PCRE2 answers these subjects.** Local 10.48 and **the 10.46 reference over
  the tailnet** (one light `pcre2test` probe, transcript
  `admitfix/transcripts/pcre2_reqcu_probe.10.46.out`) agree line for line.
  `pcre2test /I` reports `Overall options: anchored`, `Last code unit = '@'`.
  On `a`×36: `No match`. On `a`×4,999: `No match`. **On `a`×5,000 and longer:
  `error -47: match limit exceeded`.** PCRE2 applies its last-code-unit check
  to an anchored pattern, but only when the subject is under 5,000 bytes. That
  is a length-gated pre-check: the source of truth's own answer to G2's
  question. On `a`×36 followed by `!@` (the `@` present, so no pre-check can
  help), PCRE2 also hits its match limit, as does pcrec at **both** pins.

### 1.6 Classification

**A DEFECT IN THE FIX, which re-exposes PRE-EXISTING budget behaviour. It is
not a wrong answer.**

- **Defect in the fix:** G2's admission argument, as specified and as built
  (`req_route_one_attempt`'s VM arm in `src/gen/emit_dfa.c`, which reads
  `Job.start_anchor` alone), assumes the one attempt is linear. On a
  step-budgeted backtracking VM with no linear decider in front, the pre-check
  is also a **no-match proof that bounds the call**, and removing it changes
  the outcome. The spec's answer-identity claim (§2.29) is broken for
  give-ups.
- **Pre-existing budget behaviour:** the exponential attempt belongs to the
  pattern on the backtracking engine. It gave up at `25b1984f` before any
  pre-check existed, and at `b1885a83` it still gives up whenever the `@` is
  present, as it does in PCRE2.
- **Not a correctness-tier miscompile:** no wrong match, no wrong span. The
  divergence from PCRE2 is an answer-vs-give-up divergence on subjects under
  5,000 bytes. D26 makes what a pattern MATCHES exact, and `limits.md` makes
  give-ups honest but not exact.

**Filed as K64** (`docs/dev/known_issues.md`).

### 1.7 Why no check saw it — a check-design finding (learnings.md §3 candidate, not applied)

- `admitimpl_answerdiff.py`, the fix's REF-vs-TIP answer differential, ran
  two arms, `--features all` and default axes, and both select the **auto**
  route. Its subject list contains the witness (`b"a"*40`). The population it
  ran over contained no forced-VM artifact, and forced-VM is the one engine
  axis where G2's soundness argument is weakest. The differential also counts
  a subprocess timeout as `skipped` rather than `differing`.
- `tests/axes/run_axes.sh` classifies "a give-up/timeout on one side" as
  **budget-bound, never a failure** (`:780`). An answer → give-up transition
  is invisible to it by design, and admission has no axis bit anyway.
- The general form: **a check whose outcome classes include "the engine gave
  up" must count give-up TRANSITIONS as a population of their own**. Otherwise
  a change that trades answers for give-ups reads as clean on every
  instrument.

### 1.8 The fix — proposed, NOT built (D77 and the brief)

Three candidates, one recommendation:

- **A — narrow G2's VM arm to a linear-bounded attempt.** This is the
  recommended K64 fix: one predicate arm, soundness restored for every subject
  length. `req_route_one_attempt` returns one-attempt on the VM route only
  where the attempt is linear by a fact the emitter already holds: the hybrid
  runs with `RX_VM_PREFILTER_LANG "exact"`, or the program is frameless
  (`RX_VM_FRAMELESS 1`). On this population:
  - It re-emits the pre-check on the 6 framed forced-VM artifacts.
  - The give-up is gone, and the forced-VM search-regime cells return to
    `b1885a83`.
  - **Cost, stated plainly:** (a)/(b)'s forced-VM throughput wins on
    `wild-validator-email-owasp`, `winpath-near-miss` and `email-nested-plus`
    (6 cells) go back to the ~23,100 ns floor. That is `b1885a83`'s state, on
    a non-default config.
  - The auto routes do not change (§1.4), and neither do the three frameless
    forced-VM artifacts.
  - It needs a `tuning.md` §2.29 hunk (D80) that corrects both false
    sentences, plus a sabotage row whose witness is this pattern under
    `--engine=vm` on `a`×40 (the answer is detectable: `-2` vs `0`).
- **B — PCRE2's length gate.** Emit the one-attempt pre-check under
  `subject_length - search_from < T`. This keeps every throughput win and
  restores short-subject answers. It is **not sufficient alone**:
  - Past T the forced-VM give-up stays. That is PCRE2's own behaviour.
  - It hands back the (d) search wins on `uuid`/`ipv4`, where the end-window
    clamp makes the attempt free and the pre-check is pure cost at any length.
  - A cycle-3 candidate. T is a measured `limits.def` number, not 5,000 by
    citation.
- **C — the pre-check as the step budget's first refill (VM).** This is the
  general form, and it retires A's cost. Start the counter at a small K. When
  it first runs out, run the `memchr` once. If the byte is absent, return
  no-match, which is sound because the byte is necessary. Otherwise refill to
  the budget.
  - It costs nothing per step, because it rides the existing exhaustion
    branch.
  - It costs nothing where the attempt dies within K steps (all of
    (a)/(b)/throughput).
  - It bounds every call at K steps plus one pass wherever the byte is absent.
  - It applies to multi-attempt VM artifacts too, which could make eager VM
    pre-checks unnecessary.
  - Under `--fno-step-budget` (no counter) A's rule applies.
  - D77: **NOT triggered by this ledger**. The trigger is a measured VM
    population where A's give-back costs more than a cycle row. The 6
    forced-VM throughput cells above are that population's first entry.

---

## 2. THE (c) 3/4 MISS — `wild-codegrammar-json-array-begin` thr `vm-in-caps`, +1.84%

| testee | build | `REQ_WHY` | artifact across pin | before ns | after ns | Δ% | IQR% | verdict (IQR / band) |
|---|---|---|---|---|---|---|---|---|
| auto-caps | auto | dominated | changed (pre-check removed) | 349,719.5 | 263,314.2 | −24.71 | 0.01 | improve / improve |
| auto-nocaps | nocaps | dominated | changed | 349,629.1 | 263,573.7 | −24.61 | 0.20 | improve / improve |
| vm-caps | vm | **emitted** | **program-identical** | 1,101,475.4 | 1,098,667.1 | −0.25 | 0.20 | improve / within |
| vm-in-caps | vm (same build) | **emitted** | **program-identical** | 1,094,794.5 | 1,114,971.0 | **+1.84** | 0.27 | REGRESS / **within** (+6.75%) |

**Verdict: noise.** It is a real reading of an unchanged program:
- `vm-caps` and `vm-in-caps` are ONE compile (`configs.toml`), and they moved
  in opposite directions.
- +1.84% is 0.27× the pin pair's own µs-scale band edge.
- The artifact diff is the abi digit and `#define RX_REQ_WHY "emitted"`.

**Why G1 cannot reach it, which is the correction to I-102(c).** The
forced-VM artifact is `RX_VM_START "unanchored"` and `RX_VM_PREFILTER "none"`,
and it has **one** `memchr`: the pre-check itself (line 179). It has no
candidate-start scan, so there is nothing for G1 to find a duplicate of.
`dfa_cand_scan_byte` returns −1 when the artifact has no DFA scan. The
"duplicated pass" is the DFA route's shape only: two `memchr(…, 91, …)` per
call, which the auto artifacts lose here (−24.7%, landing within 0.2% of the
batch-1 BEFORE, 263,785 / 263,616 ns). **I-102(c) should have named 2
targets and 2 no-move controls.** Cycle 1 §4.3 also filed the forced-VM
+15.45/+14.39% under "duplicated pass (G1)". That label is wrong for those
two cells. What actually happened there is that the pre-check was ADDED in
front of a VM that walks the same bytes unaided: its `memchr` finds the next
`[`, and then the VM steps to it. It is still +14.96%/+16.41% over
`25b1984f` at this pin. The remedy is not G1. It is [OPT-LITSCAN]'s clause
"a literal run at a fixed offset from the candidate start goes to the
PREFILTER". A one-byte literal at offset 0 is the degenerate case: the
pre-check's hit should become the VM's start position.

---

## 3. THE I-102 GRID, PER CELL (the bench's lettering)

Full tables with REQ_WHY, IQR% and band edge per row:
`admitfix/score_tables.md` (rendered by `admitfix/score.py`). Summary:

| letter | cells | IQR bar | band bar | read |
|---|---|---|---|---|
| (a) `wild-validator-email-owasp` thr ×4 | 4 | 4 improve | 4 improve | 23,119-23,200 → **37.0 / 38.0 / 63.1 / 68.8 ns**; the batch-1 BEFORE was 40.4 (auto-caps), so the DFA route lands 8.5% below it. The pre-check is removed on all four (`one-attempt`); the auto route's attempt dies within a few bytes, and the VM's first attempt is a few dozen steps. |
| (b) `winpath-near-miss` thr ×4 | 4 | 4 improve | 4 improve | 18.8 / 18.9 / 27.7 / 36.4 ns, on the ~20 ns prediction |
| (b) `email-nested-plus` thr ×4 | 4 | 4 improve | 4 improve | DFA route 48.1 / 37.1 ns, on prediction; **forced VM 7,207 / 7,257 ns, prediction was ~47 — see below** |
| (c) `json-array-begin` thr ×4 | 4 | 3 improve, 1 regress | 2 improve, 2 within | §2: 2 targets meet, 2 controls null |
| (d) `uuid`/`ipv4` thr+srch DFA ×8 | 8 | 8 improve | 8 improve | thr 12.6-13.5 ns (−49 to −52%); srch −18.3 to −29.1%. Against `25b1984f`: thr −32 to −33%, srch −2.5 to −10.5%, **below the batch-1 BEFORE**, because batch 1's own byte check is gone too |
| (f) `nested-comment-rec` thr ×4 — control | 4 | 2 "regress", 2 within | **4 within** | +0.24 / +0.06% on program-identical artifacts (edge +6.75%); the 9.3 ms → 23.1 µs collapse is intact |
| (g) `wild-secrets-github-pat` thr vm ×2 — control | 2 | 2 within | **2 within** | program-identical; −0.03 / +0.04% |
| (h) router / keyword thr ×8 — negative control | 8 | 3 "regress", 2 "improve", 3 within | **8 within** | program-identical on all three builds; every move within ±0.18% |

**The six meeting targets as no-move controls:** 6/6 within the band, on
6/6 program-identical artifacts. The IQR-only "regressions" on (f) auto-caps
and auto-nocaps are 54 ns and 14 ns on 23.1 µs, 28× and 112× inside the band
edge. **Router/keyword as expected negative controls:** 8/8 within band, and
the stamps are exactly as predicted (`emitted`, the run form kept).

**(b) forced VM, the absolute prediction's miss, priced.** I-102 carried
`~47 ns` from the auto route's batch-1 BEFORE (47.279) to all four testees.
The forced-VM route never had an O(1) exit. At `25b1984f` this cell was
**4,480,502 ns** (before [OPT-ANCHOR-VM] made it one attempt). With the
pre-check gone, the one attempt backtracks over each throughput subject's
leading class run: `cache03`, `Queue`, `log.info` (L = 7, 5, 8), for
`254 + 62 + 510 = 826` steps (§1.3, counted). At §1.3's **7.9-9.2 ns/step**,
solved from 20 other subjects in the same record, that predicts **6,525-7,600
ns**. Measured: **7,207 / 7,257**. The step-matched check is closer still:
`t-1m`'s attempt is 510 steps, and the 510-step short subjects in the same
record measure 4,496-4,571 ns. **The prediction was the wrong route's number.
The mechanism is finding 1's at L ≤ 8.**

---

## 4. THE 29 G2 CELLS — itemized, cited, scored

**Where the bench lost the trail.** `cycle1_ledger_reading.md` §6 G2 says
"29 regressing ledger cells (8 carve-out rows, 8 of §2.1, 13 of §2.2)". The
**§-numbers are the batch-1 LEDGER's** (`2026-09-23-optloop1-batch1-after-8d716693.md`):
its §1.2 CARVE-OUT table, §2.1 "non-named REGRESSIONS, before ≥ 100 ns" and
§2.2 "floor-conversion cells, before < 100 ns". The count is every row of
those tables whose pattern is one of G2's nine. The B84 ledger read the
section numbers against the READING, whose §2.1 is [OPT-ANCHOR-VM]'s verdict.
Nothing in the reading said which document the numbers pointed at, so the
error was ours. `admitfix/score.py` carries the list with a source tag per
row and asserts 29 distinct cells.

| # | pattern | regime | testee | batch-1 source | 25b1984f | b1885a83 | 6ef76820 | Δ% vs b1885a83 | verdict IQR / band | vs 25b1984f |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | uuid-near-miss | thr | auto-caps | §1.2 | 19.93 | 27.57 | 13.48 | −51.11 | improve / improve | −32.37% |
| 2 | uuid-near-miss | thr | auto-nocaps | §1.2 | 19.91 | 27.58 | 13.35 | −51.60 | improve / improve | −32.98% |
| 3 | uuid-near-miss | srch | auto-caps | §1.2 | 561.96 | 671.53 | 547.93 | −18.40 | improve / improve | −2.50% |
| 4 | uuid-near-miss | srch | auto-nocaps | §1.2 | 565.55 | 671.45 | 548.55 | −18.30 | improve / improve | −3.01% |
| 5 | ipv4-near-miss | thr | auto-caps | §1.2 | 18.79 | 24.88 | 12.55 | −49.56 | improve / improve | −33.21% |
| 6 | ipv4-near-miss | thr | auto-nocaps | §1.2 | 18.74 | 24.90 | 12.62 | −49.33 | improve / improve | −32.67% |
| 7 | ipv4-near-miss | srch | auto-caps | §1.2 | 492.12 | 627.21 | 444.91 | −29.07 | improve / improve | −9.59% |
| 8 | ipv4-near-miss | srch | auto-nocaps | §1.2 | 497.03 | 627.43 | 444.82 | −29.10 | improve / improve | −10.50% |
| 9 | logparse-atomic-removed | srch | auto-nocaps | §2.1 | 492.62 | 649.86 | 517.75 | −20.33 | improve / improve | +5.10% |
| 10 | wild-validator-ipv4-owasp | srch | auto-nocaps | §2.1 | 498.64 | 626.72 | 446.29 | −28.79 | improve / improve | −10.50% |
| 11 | winpath-near-miss | srch | auto-caps | §2.1 | 499.93 | 644.90 | 488.95 | −24.18 | improve / improve | −2.20% |
| 12 | winpath-near-miss | srch | auto-nocaps | §2.1 | 499.77 | 644.86 | 494.22 | −23.36 | improve / improve | −1.11% |
| 13 | wild-datetime-moment-iso8601 | srch | auto-nocaps | §2.1 | 589.05 | 633.80 | 589.33 | −7.01 | improve / improve | +0.05% |
| 14 | logparse-atomic-removed | srch | auto-caps | §2.1 | 809.51 | 894.52 | 822.54 | −8.04 | improve / improve | +1.61% |
| 15 | logparse-atomic | srch | auto-caps | §2.1 | 852.18 | 830.51 | 843.86 | +1.61 | regress / **within** (+11.85) | −0.97% |
| 16 | logparse-atomic | srch | auto-nocaps | §2.1 | 838.73 | 815.73 | 840.72 | +3.06 | regress / **within** (+11.85) | +0.24% |
| 17 | winpath-near-miss | thr | auto-caps | §2.2 | 20.09 | 23,143.3 | 18.76 | −99.92 | improve / improve | −6.60% |
| 18 | winpath-near-miss | thr | auto-nocaps | §2.2 | 20.38 | 23,145.0 | 18.91 | −99.92 | improve / improve | −7.23% |
| 19 | email-nested-plus | thr | auto-nocaps | §2.2 | 31.98 | 23,133.8 | 37.07 | −99.84 | improve / improve | +15.91% (floor scale) |
| 20 | email-nested-plus | thr | auto-caps | §2.2 | 47.28 | 23,136.1 | 48.06 | −99.79 | improve / improve | +1.65% |
| 21 | wild-datetime-moment-iso8601 | thr | auto-nocaps | §2.2 | 19.68 | 36.91 | 18.78 | −49.08 | improve / improve | −4.58% |
| 22 | logparse-atomic-removed | thr | auto-nocaps | §2.2 | 18.77 | 35.61 | 18.91 | −46.90 | improve / improve | +0.77% |
| 23 | wild-datetime-moment-iso8601 | thr | auto-caps | §2.2 | 32.91 | 49.18 | 32.77 | −33.37 | improve / improve | −0.44% |
| 24 | logparse-atomic | thr | auto-caps | §2.2 | 30.02 | 44.43 | 30.12 | −32.21 | improve / improve | +0.35% |
| 25 | wild-validator-ipv4-owasp | thr | auto-nocaps | §2.2 | 18.70 | 24.99 | 12.50 | −49.99 | improve / improve | −33.17% |
| 26 | logparse-atomic-removed | thr | auto-caps | §2.2 | 30.32 | 43.86 | 30.12 | −31.34 | improve / improve | −0.66% |
| 27 | logparse-atomic | thr | auto-nocaps | §2.2 | 32.31 | 43.22 | 30.18 | −30.17 | improve / improve | −6.58% |
| 28 | wild-validator-email-owasp | thr | auto-nocaps | §2.2 | 38.95 | 23,119.5 | 37.99 | −99.84 | improve / improve | −2.48% |
| 29 | wild-validator-email-owasp | thr | auto-caps | §2.2 | 40.44 | 23,158.8 | 37.00 | −99.84 | improve / improve | −8.51% |

**I-102(e) on its own population: MET.** 27/29 improve beyond both bars,
2/29 regress by IQR only and sit inside the band, 0/29 regress beyond the
band. On I-102(d)'s literal clause "EXPECT improvement or flat, none
regressing", the two `logparse-atomic` srch cells are FLAT at 1.61%/3.06% on a
program-changed artifact. That is the fix's own mechanism at work: the
pre-check's `memchr` and a hybrid attempt that dies in a few bytes cost about
the same on these short subjects. **All 29 are on the DFA/auto route, and all
29 land within floor-scale noise of their batch-1 BEFORE**, which is the
recovery G2 was designed for. Row 19's +15.9% is a 5 ns move on a 32 ns cell,
inside the <100 ns band.

**The 72-cell superset** (9 patterns × both regimes × 4 testees) is the
bench's substitute for the 17 it could not name. Under this pin pair's band
it reads **43 improve, 11 within, 16 regress, 2 give-up**. All 16
regressions and both give-ups are **short-subject-search cells, or the
forced-VM `ipv4-near-miss` thr pair.** They are one mechanism, and
per-subject decomposition from the records shows it:

- On `wild-validator-email-owasp` srch `auto-caps`, +433.8 ns over 75
  subjects is concentrated on the subjects whose leading run is local-part
  class bytes with no `@`. `sec-github-pat` goes 9.7 → 72.7 ns (93 B),
  `sd-empty-alt-*` goes 8.3 → 53 ns (60-61 B). That is a walk of the class run
  at ~0.6-0.75 ns/byte, where `memchr('@')` used to reject in ~9 ns.
- The forced-VM srch cells are the same subjects walked by the VM:
  `sec-github-pat` +73 ns on `email-owasp` `vm-caps`, and at the limit,
  finding 1's give-ups.
- Against `25b1984f`, before any pre-check existed: every DFA-route superset
  regression is within ±3.4% (`email-owasp` srch +3.37/+3.39%,
  `email-nested-plus` srch −2.9/+2.4%, `iso8601` srch `auto-caps` −0.58%).
  Every forced-VM one is still 75-100% faster than it was there.
- **These are batch 1's search-regime wins handed back, not new
  regressions.** In the search regime the pre-check was a cheap no-match
  proof (§1.8 B/C are its keepers). The `ipv4-near-miss` thr forced-VM pair
  (+31.2/+23.8%, 8-9 ns over three calls on 28-34 ns cells) exceeds this pair's
  +12.51% floor band but not batch 2's +41.09%, and is not separately
  attributed.

### 4.1 Ready-to-append inbox entry (the bench's ASK — do NOT append from this lane)

Numbered at append time; I-106 if nothing has landed since I-105.

```
## I-106 (2026-09-25, pcrec manager; from cycle2_admitfix_reading.md §4) — O-52's ASK ANSWERED: the 29 G2 cells, itemized; the §-numbers were the BATCH-1 LEDGER's

Your B84 ledger §1.5 could name 12 of the 29. The fault is ours: in
cycle1_ledger_reading.md §6, "8 carve-out rows, 8 of §2.1, 13 of §2.2"
cites YOUR batch-1 ledger's tables
(docs/dev/ledgers/2026-09-23-optloop1-batch1-after-8d716693.md: §1.2
carve-outs, §2.1 non-named regressions >= 100 ns, §2.2 floor-conversion
cells < 100 ns), not the reading's own sections. The 29 = every row of
those three tables whose pattern is one of G2's nine. As (pattern, regime,
testee):

  §1.2 carve-outs (8):
    uuid-near-miss  thr  auto-caps | auto-nocaps
    uuid-near-miss  srch auto-caps | auto-nocaps
    ipv4-near-miss  thr  auto-caps | auto-nocaps
    ipv4-near-miss  srch auto-caps | auto-nocaps
  §2.1 (8):
    logparse-atomic-removed      srch auto-nocaps
    wild-validator-ipv4-owasp    srch auto-nocaps
    winpath-near-miss            srch auto-caps | auto-nocaps
    wild-datetime-moment-iso8601 srch auto-nocaps
    logparse-atomic-removed      srch auto-caps
    logparse-atomic              srch auto-caps | auto-nocaps
  §2.2 (13):
    winpath-near-miss            thr auto-caps | auto-nocaps
    email-nested-plus            thr auto-nocaps | auto-caps
    wild-datetime-moment-iso8601 thr auto-nocaps | auto-caps
    logparse-atomic-removed      thr auto-nocaps | auto-caps
    logparse-atomic              thr auto-caps | auto-nocaps
    wild-validator-ipv4-owasp    thr auto-nocaps
    wild-validator-email-owasp   thr auto-nocaps | auto-caps

All 29 are DFA/auto-route cells. Scored by us from your own eight
records with pcrecbench.reduce (your medians reproduce to the digit):
27/29 improve beyond IQR; the two logparse-atomic srch cells read
+1.61%/+3.06% (IQR "regress"), inside the pin pair's own null band
(+11.85% for srch 100 ns-1 us, computed over 394 cells on the 146
program-identical artifact-configs). No re-measurement asked. Please
record (e) as scored against this list. The 72-cell superset stays a
useful context table, but it is not I-102(e)'s population.

The new give-up (O-52 item 1) is pcrec's K64: a defect in the fix, and an
old outcome returning. The same five subjects gave up identically at
25b1984f (your batch-1 ledger §2.4). Mechanism and proposed fix are in
cycle2_admitfix_reading.md §1. Nothing asked of you for it yet.
```

---

## 5. WHAT THE LEDGER CONFIRMS, AND WHAT IT CORRECTS IN OUR OWN DOCUMENTS

- **The G2 prediction was exact where it was stated.** The 9 one-attempt
  patterns / 27 artifact-configs were predicted by name in cycle 1 §6,
  reproduced against the fix's compiler in batch-2 §5, and are now reproduced
  by the bench a fifth time and by this lane a sixth. Every declined artifact
  is a pure deletion (§0.2).
- **Corrections to our own asks**, each a "name targets FROM the mechanism"
  lesson ([OPT-REQPOS]'s plan row already records the I-95 instance):
  - I-102(c) named forced-VM cells that G1 cannot reach (§2).
  - I-102(b) carried an auto-route number to the forced-VM route (§3).
  - Cycle 1 §4.3's "duplicated pass (G1)" label on the two forced-VM
    `json-array-begin` cells was wrong (§2).
  - Cycle 1 §6's "29 cells" cited another document's section numbers without
    naming the document (§4).
  - Cycle 1 §6 claimed G2 "costs the batch nothing it won". Measured, it
    costs batch 1's search-regime pre-check wins on the G2 patterns (§4) and
    one outcome (§1).

---

## 6. RECOMMENDED DISPOSITIONS (Frank rules; recommendation only)

| mechanism | recommendation | the number that decides it |
|---|---|---|
| **[OPT-FREQPICK]** | **DEFAULT-ON — the stated precondition is met.** | Its target collapse holds (`nested-comment-rec` 23,118-23,153 ns on 4/4, program-identical, within band). Its one hazard, `wild-validator-email-owasp`'s floor jump, is removed on 4/4 (23,119-23,200 → 37-69 ns, the DFA route 8.5% under its batch-1 BEFORE). Nothing in this ledger is attributable to the pick. |
| **[OPT-REQPOS] tier 2b** | **DEFAULT-ON stands; the residual is [OPT-LITSCAN]'s, by charter.** | Its forced-VM targets hold (`wild-secrets-github-pat` vm 129,110 / 125,632 ns, program-identical). The router/keyword residual did not move (±0.18%, 8/8 within band, `REQ_WHY emitted`), exactly as I-102(h) predicted. It is **+82.8% / +69.4% over `25b1984f` on the DFA route** and +9.2-10.7% forced-VM. O-51 settled router's share as entirely the run form. D122 charters exactly this: "a DOMINATED pre-check is ELIDED (router-prefix-order +80.8% / keyword-prefix-order +59.7% are the witnesses)". Recommend that [OPT-LITSCAN]'s design take these 8 cells, plus §2's forced-VM `json-array-begin` pair (+15%/+16% over `25b1984f`, the pre-check-as-prefilter case), as its first acceptance cells. |
| **[OPT-PRECHECK-ADMIT]** (not asked; the finding needs a disposition) | **Keep merged; the row stays `STATE:started` until K64's fix (§1.8 A) lands with its spec hunk.** | G1 and G2 meet on every cell they reach (§3, §4). G2's VM arm is unsound for step-budgeted backtracking VM programs (§1). Its search-regime give-back on the auto routes (§4 superset, ≤ ±3.4% against `25b1984f`) is a cycle-3 measured question (§1.8 B/C), not a defect. |

---

## 7. NOT SETTLED HERE

- Whether A's forced-VM throughput give-back (6 cells) is acceptable until C
  exists. That is Frank's ruling. The numbers are in §1.8.
- T for §1.8 B, and K for C. Both are measured numbers, not citations.
- The `ipv4-near-miss` thr forced-VM +31.2/+23.8% (8-9 ns): unattributed,
  and inside the floor-scale band of the previous pin pair.
- The B84 ledger's whole-population sweep (133 IQR-only / 17 band-surviving
  regressions): not re-read here beyond one observation. Its top rows
  (`codegrammar-flat`/`-xflag` srch +27%, `floor-byte` srch +13-15%,
  `json-object-begin`, `mojibake-curly-quote`) are the 7 **`dominated`**
  patterns' search cells on the DFA route. G1's decline costs 1-3 ns per call
  there (the pre-check exited before the prefilter's own setup). That is the
  same "the removed check was a cheap reject on short subjects" shape, and it
  is recorded for whoever owns G1's cycle-3 revision.
