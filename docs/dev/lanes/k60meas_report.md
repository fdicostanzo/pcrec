# k60meas — DELIVERY REPORT

Lane `k60meas` (opus), 2026-09-18, branch `lane/k60meas` off `272bf970`.
**PARKED, not merged.** Task: MEASURE K60 so Frank can rule with numbers.
**K60 was not fixed and this branch contains no fix.**

The memo is `docs/dev/k60_measurement.md` and it is the deliverable; this
report is what a reader needs that the memo does not carry — the commit
list, the merge instructions, and the four things the lane found that the
brief did not anticipate.

---

## 1. Commits

| commit | what | disposition at merge |
|---|---|---|
| `1802364a` | `[K60MEAS]` the injector gains SUSTAINED mode + call-site attribution (`tests/core/alloc_inject.h`, `alloc_check.c`, `run_alloc_tests.sh`) | **merge** — the instrument is a deliverable |
| `e1789842` | `[K60MEAS]` W4, the size-term-ladder witness | **merge** |
| `a52bd9bf` | `[K60-PROBE]` measurement instrumentation in `src/core/compile.c` | **DROP** — the `dfam12_probe_m2.patch` / `[OPT5M2-PROBE]` precedent; the commit message says so in its first line |
| (this one) | the memo, this report, three CLAUDE.md rows | **merge** |

Dropping `a52bd9bf` is a clean `git revert` or a rebase drop: it touches one
file, `src/core/compile.c`, and nothing else in the branch depends on it —
the instrument commits build and run without it (they are `tests/` only).

## 2. The headline numbers

| | single-shot | sustained |
|---|---:|---:|
| W1 `[a-z]+` (DFA/auto), K=72 | 15 (20.8%) | 5 (6.9%) |
| W2 `[a-z]{2,10}` (`--engine=vm`), K=11 | 0 | 0 |
| W3 `\p{L}` (`-e utf8`), K=328 | 25 (7.6%) | **0** |
| W4 size-term ladder (**new**), K=158 | **108 (68.4%)** | **0** |

**Attribution: 148 absorptions, all 148 named.** 40 (27%) are
`emit_state_legend`'s documented silent degradation
(`src/gen/emit_dfa.c:3615-3618,3660`); 108 (73%) are the `[ART-SIZE]`
ladder's blanket catch swallowing `ctx_nomem`-routed failures
(`src/core/arena.c:14`, `src/core/sb.c:24`). **Zero** involve a stale
eligibility flag.

**Population: 2 of 3,159 corpus patterns (0.06%) at default axes; 17
(0.54%) under `-e utf8`.**

**Candidate fix (distinct `longjmp` value from `ctx_nomem`): eliminates 108
of 108 ladder absorptions and 0 of 40 legend absorptions — 73% of the
measured total, and the 27% it misses it cannot reach by construction.**

Recommendation (memo §6): take disposition (2) for the ladder; **strike
disposition (1) as refuted**; the legend is a separate defect none of K60's
three dispositions fits, and it is Frank's call (memo §6.2 gives three
options and recommends the cheapest).

## 3. Four things the brief did not anticipate

**3.1 K60's "ONE CONFIRMED MECHANISM" is wrong, and the refutation is three
lines.** The `Ctx` is declared *inside* the attempt loop and `memset` at the
top of every iteration (`compile.c:704-706`), so `cx.size_cap_refused` and
`cx.dfa_overflowed` are per-attempt by construction. There is nothing to
reset. The general form is worth more than the correction: **an entry that
names a mechanism by READING code should say which lines it read**, because
this one's diagnosis and its repro came from different places and only the
repro was checked. Memo §2.4 and §5.

**3.2 The mechanism K60 calls secondary has no witness in the tree and the
worst rate in it.** The ladder catch is excluded from W1 and W3 by
`fit.chosen == ENGM_VM` and from W2 by the `emit_code` threshold, so the
entry's 21%/8% figures are rates for a mechanism the ladder is not even
running during. Adding one witness (W4) moved the measured rate to 68.4%.
*A mechanism named in a defect entry and reached by none of that entry's
witnesses is a mechanism nobody has measured* — and the entry looked fully
witnessed because its witnesses were failing.

**3.3 Extending the injector's ABI produced 60 "killed by signal 11" trials
that were entirely an artifact of a stale build tree**, and the instrument
now defends against it. `alloc_inject.h` is `-include`d, and this tree has
no `-MMD` dependency generation — `$(BUILD_DIR)/obj/%.o` names its headers
by hand — so an edit to the injector header leaves `build-alloc/` stale.
The four injector functions are resolved at LINK time from a separate TU
with **no shared prototype**, so a stale one-argument call against a
four-argument definition is not a build error: it is a wild pointer and a
SIGSEGV *inside the injector*, which reads exactly like the abort/signal
outcome the check exists to detect. Fixed by giving the four symbols an
`_at` suffix with the signature change, so a stale object fails to **link**.
The transferable form: *an instrument whose ABI crosses a link boundary with
no prototype must change its NAMES when it changes its shape, or its own
failures are indistinguishable from its subject's.*

**3.4 The lane walked into this house's recorded `-o`-basename trap on its
own byte-identity sweep** — comparing artifacts written to different `-o`
basenames reports a false difference on the `#include` line, and the first
run read `identical=0 differing=1158`, which looks like a catastrophic
regression. Caught because `identical=0` is not a plausible shape for a
comment-only probe. Re-run with both sides writing the **same basename in
different directories**; §5 has the result. `w23fix_report.md` records this
as the third instance and this is the fourth — the durable fix is a shared
fixture, not another report entry, and the lane did not build one.

## 4. Rulings received

None. No ruling was requested: the brief's one escalation trigger (a
temptation to actually fix K60) never arose, and the two design questions
the measurement raised (memo §6.1's land-or-defer, §6.2's three options for
the legend) are **presented as Frank's**, not taken.

## 5. Validation

| | result |
|---|---|
| `make -j4 CC=gcc-16` | clean, at every commit |
| `make strict CC=gcc-16` | **clean** (`strict: whole tree compiles clean with -Werror -Wshadow`), including `-Wclobbered` on the probe's new `volatile` |
| `make alloc CC=gcc-16` (probe off) | four witnesses read 15/5, 0/0, 25/0, 108/0 — **identical to the pre-probe build**, which is the probe's behaviour-identity proof |
| `bash tests/rxtsource/run_rxtsource_tests.sh` | **212 passed / 1 recorded / 0 failed** (`INV-COMPAT holds over 211 files / 3938 blocks / 28949 expectation lines`). The one `RECORD:` line is this box's pre-existing darwin C3 non-native-pin behaviour — `btriage_20260917_report.md` |
| probe-OFF corpus byte identity vs `272bf970` | **1,158 identical / 0 differing / 2,001 both-refuse / 0 rc-mismatch** over all 3,159 distinct corpus `pattern` lines |
| probe-ON (`PCREC_K60_PROBE=1 PCREC_K60_FIX=1`) byte identity | **1,158 / 0 / 2,001 / 0** — identical to probe-off |

**VALIDATION IS COMPLETE. Nothing is owed.**

Full `make test` was **not** run (the brief forbade it without asking, and
the lane's `tests/core/` changes do not reach `make test` beyond
`tests/resource/` section 2b, which runs `alloc_check` argument-free — a
path deliberately left byte-for-byte unchanged in behaviour and output).

**Box discipline held**: nothing touched `ubuntubudu`; no `make
san`/`mech`/battery was run; every uncertain command was `timeout`-bounded.

## 6. Reproduction

```
make alloc CC=gcc-16 ALLOC_ARGS="--both --sites"      # §1, §2 of the memo
PCREC_K60_FIX=1 LIBPCREC=$PWD/build-alloc/libpcrec.a \
  ALLOC_ARGS="--both --sites" bash tests/core/run_alloc_tests.sh   # §4
```
The corpus population sweep (§3) is the `[K60-PROBE]` trace
(`PCREC_K60_PROBE=1`) over every distinct corpus `pattern` line at
`--features all`, once bare and once under `-e utf8`, counting
`[K60] attempt` lines. It needs the probe commit; once that is dropped the
numbers stand on this memo, as `dfam12`'s M2 numbers stand on theirs.
