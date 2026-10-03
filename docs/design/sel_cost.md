# [SEL-COST] step 1 — a measured cost model for auto's engine choice, with [SEL-SIZE] as the first instance

**DESIGN, NOTHING BUILT.** Lane selcostdes, 2026-10-03, base c231ffc1
(abi 54). [OPTLOOP] round 1 under D144. Inputs: the [SEL-COST] and
[SEL-SIZE] plan rows, `docs/dev/sel_cost_census.md` (STEP 0),
`docs/dev/summaries/2026-10-03-bench-o79-o82-notes.md`, bench outbox O-9
items 6-7 and O-19, `src/opt/select_engine.c`, `src/core/compile.c`'s retry
ladder and `fit_rungs[]`, D77, D119, D124, D141, D144. Evidence for this
document: `docs/design/sel_cost/` (a compile-only census and three Mac
scratch timing tables).

## 0. The answer

1. **No bucket clears D119's measured-gap bar as a compile-time selection
   term on current evidence.** Every loss large enough to matter changes
   sign with the subject or the call regime while the compile-time facts
   stay the same (buckets B, C, D, and [SEL-SIZE]). The one loss that keeps
   its sign in every regime (bucket A) is about 2.5 ns per call, and the
   only predicate that isolates it would regress the validators sharing
   its stamps by ×1.7-×5.1.
2. **[SEL-SIZE] is refuted as framed. Emitted size is anti-predictive.**
   170 auto-selected DFA artifacts are over the 250 KB warning. 108 of them
   are altwide wide alternations, where the DFA beats the VM by ×1.8-×2.0
   on the Mac (bench O-82 A4: forced VM ×25-×229 slower on altwide class
   tails). The witness's own loss (×6.7-×8.0) is the same at 67 KB
   (`{0,256}`) as at 477 KB (`{0,4096}`). It is a SHAPE: the `(?:P)\z` form
   of a counted class run loses its scan edge and takes a reverse pass.
   [OPT-VEDGE] already owns that mechanism and names this witness ladder as
   its customer.
3. **Recommendation: build nothing under [SEL-COST] in round 1.** Re-home
   each bucket's evidence to the row that owns its mechanism (§5). Keep
   [SEL-COST] open with a stated trigger: a population whose loss holds its
   sign in every regime (§3). §4 is the design of record for when that
   trigger fires, so the shape is settled now and not re-argued then.

## 1. Which buckets clear the bar

D119 item 4 sets the bar: the target cells' median improvement exceeds
their IQR, AND no carve-out cell regresses by more than its IQR. A
selection term runs at compile time. It sees only facts about the pattern,
and one artifact serves every call regime (sel_cost_census.md, "What a
measured selection term would need to see"). So the bar's second half
reads, for a selection term: **no pattern sharing the row's compile-time
predicate may lose in any regime.**

| bucket | population | absolute size | keeps its sign across regimes? | compile-time separable? | verdict for SELECTION |
|---|---|---|---|---|---|
| D: `(?:P)\z` wrapper | 60/80 caps match-compliance cells (abi 39) | mean 102 ns/call | NO: on the Mac, VM ×6.7 on short whole-subject, DFA ×1.44-×1.58 on 64 KiB prose (T1) | partly (the `\z` view) | does not clear. The form is the defect: [OPT-VEDGE] for counted runs; [OS-4]/D77 hold the end-anchored entry |
| A: one-attempt DFA | 3 start-anchored patterns (the end-anchor trio no longer loses on the Mac: T3 `done$` 2.9/3.1) | 2.5 ns/call (T3: 3.7 vs 1.2) | YES on its witnesses | only via a new "VM program cannot backtrack" fact: `dfa_scan=attempt` alone also selects the validators, DFA ×5.1/×1.7 (T3 controls) | clears the relative bar on 3 cells; the prize is tiny; the fix belongs to the DFA attempt entry, not to selection (Q5) |
| B: class run | 4 patterns × 2 regimes (abi 39, VM ×1.08-×1.38); persists at abi 54 (T2: VM ×1.10-×1.47 on prose, ×1.53-×3.08 inside long runs) | ms-scale on 1 MiB | NO: `\p{L}+` utf8 is DFA ×17 on a letter-free subject (the byte-class prefilter skips), VM ×3.08 inside runs (T2) | yes (prefilter + edge stamps), but the verdict depends on the subject | does not clear. The DFA's in-run loop is the defect: [OPT-3-RUNEND] (a), plus the missing utf8 scan edge |
| C: hybrid prefilter | 17 patterns, 11 VM wins / 22 auto wins | up to 1.62× / 14.7× | NO: lka-pos/lka-neg have identical stamps and opposite verdicts; O-82 Q4 makes it density (lka-neg dense, lka-pos sparse, ~60-110×) | NO | does not clear. A runtime fact: [OPT-HYB-RESEED] (landed) and -XCALL (round 1) |
| reverse (forced DFA beats auto) | O-82 Q2/Q3: 191 syntax cells, 0 movers >5%; 83 capability cells, 2 movers at the timer floor on identical programs | — | — | — | empty |
| O-74 email whole-subject | forced VM ×0.648 / ×0.856 | — | same shape as D | — | does not clear, for D's reason |
| [SEL-SIZE] | §2 | — | NO (T1, the witness ladder) | size, yes; but size is anti-predictive | refuted |

**What the table says about the cost model itself.** STEP 0 proposed a
per-call constant plus a per-byte term for each engine form. The data
shows the per-byte term depends on the SUBJECT, not only on the pattern.
The DFA's in-class-run cost (B, [SEL-SIZE]) and the prefilter's skip rate
(B's sparse column, C) are both subject properties, and they decide the
winner. A compile-time model can only price one assumed subject mix.
Wherever the measured winner flips within the bench's own regimes, any
assumed mix loses a carve-out. The model is sound only on a population
whose winner is the same in every regime. None of real size exists today.

## 2. The [SEL-SIZE] census

`docs/design/sel_cost/census.py`, compile-only, on the Mac with each
compile under `timeout 120`. The population is every corpus block as
written with an auto engine (3,668 compiles), plus every pcrec-bench
pattern (339), both raw and as `(?:P)\z`, at byte and utf8 (1,356). That
is 5,024 compiles. 2,719 select the DFA, 1,747 the VM, and 558 refuse
(unbuilt modules, encoding refusals). **Every DFA-selected pattern has a
VM form**, because the VM compiles everything the DFA can
(select_engine.c's `PCREC_ENGINE_VM` arm). So "warned DFA with a VM form"
is just "warned auto-DFA".

| auto-DFA emitted size | artifacts | by source |
|---|---|---|
| 100-250 KB | 50 | corpus 22, bounded 10, utf8 7, capability 5, email 4, altwide 2 |
| ≥ 250 KB (WARNED) | **170** (96 `selected`, 74 `size-cap-retry`) | **altwide 108**, corpus 34 (utf8 `\p{..}` single classes), utf8 10, bounded 8, capability 6, syntax 4 |
| distinct bench patterns among the warned | 41 | |
| routed to the VM by the [LIM-2] N1 budget | 12 | all `bounded` `\z` forms: cls-upto-8192/16384/32768, cls-lazy-16384, nest2-64, nest3-16 |

The forced-VM artifact is smaller on every row, 24-367 KB against
300-997 KB (`census_large.tsv`). Size alone would therefore always pick
the VM.

**What the timing says (T1, Mac scratch):**
- The witness itself (cls-upto-8192 `\z`) is already on the VM through
  N1, as the row said. Its siblings at 2048 and 4096 are still auto-DFA,
  WARNED at 310 KB and 477 KB, and they lose ×6.7 (40-letter whole subject)
  and ×8.0 (4 KiB of letters).
- **The 256 rung, at 67 KB and below every size threshold, loses by the
  same ratios** (×6.7 / ×7.5). A size knee would miss it.
- On 64 KiB of word-separated prose, all three `\z` rungs are DFA wins
  (×1.44-×1.58). The loss is regime-dependent.
- The plain (un-wrapped) `[a-z]{0,4096}` is a tie or a DFA win everywhere.
  It carries the `range` scan edge that [OPT-5] built after bench O-9
  measured this same ladder (O-9 item 7: auto÷vm 1.98-2.05 at
  256/4096/16384, mechanism "a premultiplied table … on a run that stays
  inside the class"). The `\z` form's stamps read
  `RX_DFA_SCAN_EDGE "none"`, `RX_DFA_START "reverse-pass"`, and
  `RX_DFA_MATCH "search-filter"` at 4096. That is exactly the condition
  [OPT-VEDGE]'s scanedge.c precondition (3) excludes ("a counted
  single-class chain whose every state carries ONLY the END view"). Its
  row predicts both effects: "the whole-subject `[a-z]{0,n}\z`-shaped
  ladder collapses like the plain ladder did", and the search-filter band
  shrinks.
- The altwide control, warned at 985 KB, is a DFA win in all three
  regimes (×1.8-×2.0).

So the warned population is mostly DFA WINS. The real loss sits below the
warning. The predictor is the counted-chain-under-a-view shape, which an
emission change removes. [SEL-SIZE]'s own text asked for "a measured knee,
never a warned-size special case". The measurement finds no size knee:
the ×6.7 holds flat from 256 to 4096.

## 3. The admission rule this produces (the D77 trigger)

A selection-cost row may be built only for a population where:

1. **the sign holds in every regime.** Forced-form beats auto past the
   noise floor in whole-subject, short-search AND throughput, on at least
   one match-dense and one match-sparse subject (O-82 Q4's lesson). A
   flip in any regime sends the population to the form that loses, not to
   selection;
2. **the predicate is compile-time and exact.** No pattern that satisfies
   it loses under the row (the bucket-A controls are the test case);
3. **the gap clears D119 item 4** on the Linux scratch tier (§4.8).

This rule is the [SEL-COST] row's trigger text. Today it is met by
nothing except bucket A's three witnesses, with a predicate that does not
yet exist and a prize of a few ns.

## 4. The mechanism, when the trigger fires (design of record)

**4.1 What it predicts.** Not an absolute cost per engine. A VERDICT per
(compile-time shape, engine form), each backed by a fitted
per-call/per-byte pair measured in every regime. A row exists only where
both fitted terms favour the same form (§3.1). So the shipped artifact
holds no arithmetic, only predicates and their provenance, and the
fitted numbers live with the row's measurement record. This is the honest
form of "per-call constant + per-byte term" once §1 has shown that the
per-byte term is subject-dependent. If a future row needs a real
threshold (a knee in a machine fact), it carries one named constant
(§4.5).

**4.2 Inputs: compile-time facts only.** Two stages, because some facts
exist only after the DFA build:
- *pre-build*: everything `[PATFACTS]`/E1 holds (`pcrec_fact_kinds`,
  widths, start-anchoring, req byte/run), the registry rows, the call
  graph. These are the same facts select_engine.c already reads.
- *post-build*: the built machine (state count, class count, table form,
  scan edges found, anchored-machine reach). This is what a [SEL-SIZE]-like
  row would need. The DFA build reports these to selection through the
  one existing channel ([SEL-1], below).

**4.3 Where it slots: rows in existing tables, not a parallel selector.**
- *pre-build rows* go in `pcrec_select_engine`'s `default:` (auto) arm.
  Today that arm is one line, `fit.chosen = (mask & ENGM_DFA) ? ENGM_DFA :
  ENGM_VM;`. It becomes a first-match table (memory rule; the
  `fit_rungs[]`/`dfa_pfs[]` idiom), `sel_auto_rows[]`. Each row is
  `{name, deny bit, applies(cx, mask), chosen}`. The last two rows are
  "DFA excluded → VM" and "default → DFA", which reproduce today's line
  exactly, so the table lands identity-neutral before any cost row
  exists. `--engine=dfa|vm` never reaches the table: the override switch
  above it is do-or-die and unchanged.
- *post-build rows* reuse [SEL-1]'s rung. The DFA build (or the step
  right after it, under `--engine=auto` with `fit.chosen == ENGM_DFA`)
  evaluates the post-build rows. A firing row is reported exactly as an
  N1 over-budget is: `cx->dfa_disabled` plus a reason, then
  `compile_driver`'s existing one-shot retry. `forces_dfa_overflow`
  already consumes that bit as a selection outcome, so it grows a reason
  field rather than a sibling row. That function's own header calls it
  "THE GENERAL MECHANISM": the DFA build reports a result the selection
  pass consumes. A cost decline is a second kind of that result.
  `COMPILE_MAX_ATTEMPTS` does not move, because the retry is the same
  single retry.
- D124 lens: the question is "which emission strategy serves this shape".
  The engine is the row's answer and its predicate column, not a separate
  mechanism per engine.

**4.4 Deny flags.** D144 item 4 gives every optimization its own flag, and
each cost row is one optimization. So each row gets `-fno-sel-<row>`, an
`axes.def` row (deny-only; `--engine=dfa` is already the force), and its
`deny` bit in the table. `-fno-sel-cost` denies the whole family for
batch-gate triage (one flag to flip, D144's purpose). Rows are not
degrading under `--fast-or-fail`: a row exists only because it is faster.
`--tune`: no dial interaction unless the row trades size. A size-trading
row gets a `--tune` position (D119 item 4), not the default.

**4.5 Constants (D141).** A row's predicate is structural. Its provenance
(witness cells, box, date, the per-regime ratios and floors) goes in the
row's comment and in a committed timing record, the `timing_mac.md`
pattern. A row that needs a threshold adds it as a `limits.def` row of
kind `"selection knee"`, override `NONE` until a measured need. That kind
is already the home of every selection knee (`PCREC_SIZE_TERM_*`,
`VM_ISL_*`, `PCREC_MIN_SCAN_CHAIN`), and the D107 detector already guards
it against bare literals. Those rows head [EST-REGISTRY]'s fold list. Until
D141 is scheduled they go there rather than into a new `estimates.def`
that would exist for one row.

**4.6 Stamps, spec, abi.** A post-build decline gets a distinct
`<PREFIX>_ENGINE_SEL` value, `"cost-declined"`, in `esel_of`'s ladder
between `ESEL_SELECTED` and the overflow range. Reusing
`"overflowed-dfa"` would hide it from a fallback bucket, the O-10 defect
D-line 6408 fixed. A pre-build row stamps `"selected"` and names its row
in `<PREFIX>_ENGINE_WHY` (an existing free-text stamp). **No abi bump**:
a new value of an existing stamp is a value, not scaffolding (D76;
precedent at decisions.md:6408). Spec hunks in the same change (D80):
`docs/spec/tuning.md` (the value list and the axis row),
`docs/spec/limits.md` §3 if a knee row lands, and `match_api.md`'s
`ENGINE_SEL` paragraph. Readers are found by grep for the value list per
D94, never by a hand list. Artifacts of patterns that flip change
program, not scaffolding. Grep the identity gates' pinned populations
(recursion-identity FILEPIN, codegen pins) for flipped witnesses and
re-pin with the row's name as the reason.

**4.7 Answer identity: selection changes engines, never answers.**
- `make test-axes AXES="-fno-sel-<row>"`: the whole corpus is
  answer-identical denied vs default.
- The existing engine axis already proves the VM and DFA forms agree on
  every corpus pattern that both compile. A cost row only moves a pattern
  between two forms that axis holds equal.
- Sabotage (mech row, highest S-id on main at the time): force the row's
  `applies` true for every pattern. The whole `.rxt` corpus must still
  pass, because every DFA-routable pattern goes through the retry/VM path.
  A broken retry then shows as a wrong answer or a refusal, and the
  sabotage is detected by identity rather than timing.
- Reach witness ([MECH-REACH]): one `.rxt` case per row whose expectation
  pins `ENGINE_SEL`/`ENGINE_WHY` to the row, so the witness fails loudly
  the day the row stops firing.

**4.8 Alpha witnesses and the Linux scratch-timing protocol (D144 item 1).**
Tooling that already exists: `studies/hyb_reseed_cal/` (`drv.c` find-all;
`table.py` round-robin launches × reps, median of medians; the base / new
/ deny columns) and `docs/design/sel_cost/percall.c` (whole-subject).
Protocol:
- three binaries per cell: base (branch point via `git archive`), new, and
  new with `-fno-sel-<row>`. Base/deny are the same program, so their
  ratio IS the noise floor for that cell (`docs/dev/reseed/timing_mac.md`'s
  method);
- on ubuntubudu, through the pcrecdev2 executor (lanes never ssh a heavy
  run), `taskset -c 2` (tests/bench's `BENCH_CPU` default), 5 launches × 7
  reps, artifacts compiled at `-O2` ([GUIDE-OPT-LEVEL]);
- per witness: whole-subject per call (short and 4 KiB), short-search,
  and 1 MiB find-all on one match-dense and one match-sparse subject. A
  cell counts only if |new/base − 1| exceeds both 3% and its own base/deny
  floor, and the median gain exceeds the IQR (D119 item 4);
- carve-out controls are compulsory: the nearest patterns that share the
  row's stamps but must not flip (for bucket A: the capability
  validators).

**4.9 Size.** The pre-build table conversion (identity-neutral) is S:
about 40 lines, plus a list hook for [LIST-TABLES]. Each cost row is S:
the predicate, reason plumbing, an axes row, an `ESEL` value for a
post-build row, spec hunks, one reach `.rxt`, one mech row. The
measurement is M and dominates: three regimes × dense/sparse × controls,
on Linux.

## 5. Where each bucket's evidence goes instead

| evidence | owning row (exists) | what to add |
|---|---|---|
| [SEL-SIZE] witness ladder: `\z` counted class run, VM ×6.7-×8.0 flat from 256 to 4096, DFA wins on prose | **[OPT-VEDGE]** (its own predicted customer) | T1 as its fresh pcrec-side measurement. Its "first step: opt5d §7 item 3's one-command measurement" is partly done here |
| B: DFA in-class-run loop loses to the VM's span loop (×1.5 `\w+` bitmap edge; ×3.1 `\p{L}+` utf8, no edge) while winning ×17 on a letter-free subject | **[OPT-3-RUNEND]** (a) run-end skip; the utf8 class-run edge absence | T2. The DFA must win both columns, so selection cannot help |
| A: one-attempt DFA ~2.5 ns/call fixed cost vs the VM (literal anchored prefixes) | none fits ([OPT-ATTEMPT-SPLIT] is the partially-anchored case) | annotate [SEL-COST] with T3 and the controls; D77, no row until a workload where 2.5 ns/call is measurable (Q5) |
| C: hybrid prefilter density | [OPT-HYB-RESEED-XCALL] (round 1) | nothing new |
| D / O-74: whole-subject wrapper cost | [OS-4] (D77 hold), [OPT-VEDGE] for counted runs | nothing new |

## 6. Lenses

- *General vs special case* (memory): a size knee would be a warned-size
  special case, wrong on 108 of 170 warned artifacts and blind to the
  67 KB loser. The re-homed fixes are general emission mechanisms.
- *D77*: no selection mechanism without a population meeting §3; the
  table conversion in §4.3 is not built ahead of its first row either.
- *D119*: unit = mechanism; the measured-gap bar applied with the
  regime-invariance reading (§1); algorithmic; inside the engine
  architecture.
- *D124*: one question ("which strategy serves this shape"), the engine
  as the answer column, and post-build facts fed back through the
  existing channel.
- *Build what won't be rolled back*: a selection row routing B or
  [SEL-SIZE] to the VM would be rolled back the day [OPT-3-RUNEND] or
  [OPT-VEDGE] lands. A form fix is never rolled back.

## 7. Reproduce

`REPO=<tree> PCREC=<tree>/build/pcrec python3
docs/design/sel_cost/census.py out.json` (compile-only, about 5 min, Mac
OK). Timings: `docs/design/sel_cost/timing_mac.md` names the subjects;
link `percall.c` or `studies/hyb_reseed_cal/drv.c` with each `-p rx`
artifact.

## Questions for the manager

1. **Does [SEL-COST] step 1 close round 1 with no build?** Recommendation:
   yes. Round 1 proceeds with two optimizations. If you want a third, the
   evidence points at [OPT-VEDGE]: it is the same witness ladder, has a
   measured ×6.7-×8.0, a mechanism already designed (opt5_step2_twopass.md
   §2), and also retires two size warnings.
2. **[SEL-SIZE] disposition.** Recommendation: close it as
   REFUTED-ON-EVIDENCE (size is anti-predictive: §2), with its witness
   re-homed to [OPT-VEDGE] (§5). Frank's direction ruling, which the row
   was blocked on, is then moot. It is his to confirm, since he chartered
   the question.
3. **[SEL-COST]'s state.** Recommendation: keep it not-started, with §3 as
   its D77 trigger and §4 as the design of record. Annotate it with this
   document and with A's T3 numbers.
4. **Annotate [OPT-3-RUNEND] with T2**, including that `\p{L}+` under utf8
   has no scan edge at all. Recommendation: yes, as an annotation, not a
   new row. Its own measurement need (a non-periodic 1 MiB subject) still
   governs.
5. **Bucket A.** Recommendation: no row now (D77: 2.5 ns/call, no workload
   shows it). Record that a future fix belongs in the DFA attempt entry
   (a literal-prefix fast path), not in selection: a
   `dfa_scan=attempt → VM` row regresses the validators by ×1.7-×5.1.
6. **When a row is built: the stamp value and flag names.** Recommendation:
   `ENGINE_SEL "cost-declined"` for post-build declines, placed between
   `selected` and the overflow range; `-fno-sel-<row>` per row plus
   `-fno-sel-cost` for the family; no abi bump (decisions.md:6408).
7. **Runtime (per-call) selection.** This is the only shape that could
   capture regime-flipping wins: both forms in one artifact, dispatched on
   subject length or a caller hint. Recommendation: record it as a
   deferral, with no row. It roughly doubles the artifact, and the
   density-driven flips (B, C) are not predictable from length. D119 calls
   that kind of architecture change a deferral at best. The caller-hint
   half already lives in [OPT-HYB-RESEED-XCALL].
8. **Bench asks.** Recommendation: none new. The open syntax asks
   (vm-nocaps measured records, the density-controlled pair) are already
   in [BENCH-ASKS-PENDING]. The re-homed rows can be measured on the
   pcrec scratch tier.
