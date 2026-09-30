# [SEL-COST] STEP 0 — the syntax subbench, read exhaustively

Charter: `docs/dev/plan.md` [SEL-COST] STEP 0 (D131 item 8 pulled it
forward). The row's own question: auto's engine choice has no measured
cost model. This is the mandated first step — an exhaustive read of the
bench's syntax subbench (every row, auto vs each engine form, the
population where a non-auto form wins and by how much, grouped by
cause) — before any mechanism is designed.

**Scope discipline (memory `pcrec-ask-bench-dev`):** everything below is
read from the bench's own committed reports, records and generator
source under `/Users/fdicostanzo/pcrec-bench` (read-only; nothing written
there). Nothing here reverse-engineers the bench's internal reduction —
every number is either copied from a `rank_yes`/`rank_no` row of a
committed report, or read from the `engine_metadata` block pcrec's own
compiler already stamps into the bench's per-record JSONL (the same
stamps `--emit-facts`/`--list-*` would show locally). Where the bench
alone can answer a question, it is listed under "Questions for the bench
dev" rather than guessed.

**Data window:** `syntax@0.1` at pin `751b9c6d` (abi 39), report
`pcrec-bench/reports/2026-09-27-syntax-0.1-budu-ryzen1600-fullroster-751b9c6d.{md,tsv}`
— the bench's own quiet-box, trial-agreement-checked run (7 records, all
`agree`, `x13_rules: v1.4 X13` on every record). 95 named patterns
(`bench/syntax/gen_patterns.py`); 12 do not compile at this pin (unbuilt
modules: comment groups, branch-reset, callouts, `(?(DEFINE))`-adjacent
condition group by itself is fine but `cnd-group` refuses, `\R`/`\X`/`\C`
control escapes, verbs `(*ACCEPT)`/`(*SKIP)`, `[a--b]` extclass minus) —
excluded from every count below, they carry no engine choice to census.

## Method

The report's roster for this pin carries exactly four pcrec testees:
`auto-caps`, `auto-nocaps`, `vm-caps` (`--engine=vm`, which **also
disables the DFA hybrid prefilter** — `testees/pcrec/configs.toml`'s own
description: "the VM forced, which also disables the DFA prefilter so
the VM derives the whole span independently"), and `vm-in-caps` (the
same forced VM, with a caller-provided frame/trail buffer instead of the
default). **There is no forced `--engine=dfa` testee and no forced-VM
`nocaps` testee in this roster** — see "Questions for the bench dev".
So this census can only measure, per (pattern, regime), **auto-caps vs.
the better of {vm-caps, vm-in-caps}** — the population where forcing the
VM (and losing its DFA-front prefilter) beats what `auto` picked. It
cannot measure the reverse direction (auto picks VM, does forced DFA do
better) or the nocaps population's non-auto comparator at all.

Three regimes, every pattern that compiles: `large-subject-throughput`
(subjects `t-64k`/`t-256k`/`t-1m`, a scan/search cost), `short-subject-
search` (42 short subjects, sum of per-subject `ns/call`), and
`match-compliance` (one `whole-subject` artifact per engine form — the
`(?:pattern)\z`-shaped wrapper — timed once).

A ratio `auto_ns / best_forced_vm_ns` is computed per (pattern, regime);
**> 1 means forcing the VM would have been faster than what `auto`
picked.** The bench's own noise-floor ruling (`docs/dev/ledgers/
2026-09-29-b115-findings-tiers-f7f5a143.md`, "The noise floor, measured":
"a ±1% difference between two arms is NOT a finding... every effect
named above is ≥3%, and each coincides with a program change") is
applied here too: only ratios past 1.03x (or below 1/1.03x) are called a
win/loss, and every bucket below is cross-checked against pcrec's own
`engine_metadata` stamps to confirm the two arms really compiled a
*different program* (not just launch jitter) — every bucket does.

Reproduction: `docs/dev/sel_cost_census/` (own CLAUDE.md) — the five
extraction/tagging scripts and their derived data
(`patterns.json`, `engine_meta.json`, `census_full.tsv`, `wins.json`).

## The census table

`docs/dev/sel_cost_census/census_full.tsv` is the full table: every
(pattern, regime) cell with `auto_ns`, the winning forced-VM testee and
its `ns`, the ratio, a cause tag, and the four compile-time stamps that
justify the tag (`auto_engine`, `dfa_prefilter`, `dfa_scan`, `req_why`).
243 caps-class cells (95 patterns × up to 3 regimes, minus refusals and
a few regime-inapplicable patterns).

Population overview, caps class (the only class with a non-auto
comparator):

| regime | cells | auto wins/ties | forced-VM wins (>1.03x) |
|---|---|---|---|
| `large-subject-throughput` | 80 | 70 | 10 |
| `short-subject-search` | 83 | 64 | 19 |
| `match-compliance` | 80 | 20 | 60 |

Read plainly: on the regime that looks most like real traffic (scanning
a subject for a match), `auto` already wins or ties 70 of 80 times — a
result the D131 framing already predicted ("with a few exceptions, pcrec
has an engine that beats most in the syntax subbench outside
large-subject-search"). The two regimes where forcing the VM wins more
often (`short-subject-search`, and overwhelmingly `match-compliance`)
are dominated by one already-filed, non-selection mechanism — see cause
D below — not by a fresh defect in `auto`'s own choice.

## Cause groups

Every group below is a **within-caps-class** comparison: `auto-caps`
against the best of `vm-caps`/`vm-in-caps`, so a captures/no-captures
mismatch never enters into it (D119/I-99's rule against cross-class
comparison is honored throughout this document).

### D — the `match-compliance` regime artifact (OS-4). Dominant by row count, NOT a selection defect.

60 of 80 caps `match-compliance` cells show forced-VM "beating" auto, by
a strikingly uniform ~1.5-1.9x, on almost every DFA-selected pattern
regardless of family (anchors, classes, escapes, modifiers, quantifiers,
groups — the ratio clusters tightly around 400-460ns auto vs. 260-290ns
forced-VM). This is **already filed** on the bench's side: `docs/dev/
outbox_to_pcrec.md` "Standing items owed to pcrec ... The `(?:P)\z`
whole-subject artifact's skip-loop last-byte cost — the match-compliance
regime artifact ([OS-4])" and the report's own per-group caption ("the
ratio between forms is a regime artifact until an end-anchored entry
exists (pcrec [OS-4])"). The mechanism: `match-compliance` times a
SEPARATE `(?:pattern)\z`-wrapped artifact (pcrec has no native
end-anchored entry point yet — [OS-4]/[OS-4]'s own row), and the DFA's
wrapper form carries a fixed per-call cost the VM's native whole-subject
entry does not. **This is not a new [SEL-COST] finding** — it is the
bench's own named, already-tracked artifact of a missing engine feature
(a real end-anchored entry), and building that entry is [OS-4]'s charter,
not a selection-term question. It is called out here in full because it
is the majority of the raw "wins" population and a naive count would
have overstated [SEL-COST]'s prize by roughly 6x. In absolute terms it
is also tiny — ~150-200ns per call — dwarfed by every other bucket's
absolute cost on a real subject.

### A — anchored/bounded-position DFA forms pay a fixed per-call cost a short call cannot amortize

Patterns: `anc-caret` (`^item`), `anc-a-uc` (`\Aitem`), `anc-g-uc`
(`\Gitem`) — auto picks `engine=dfa`, `dfa_scan=attempt`,
`req_why=one-attempt` (no prefilter at all: the DFA is run once at a
fixed start position). Forced VM beats auto by **1.20-1.27x on BOTH**
`large-subject-throughput` and `short-subject-search` — the fixed cost
here is not amortized even at 1 MB, so it is a true per-call dispatch
cost of the "one-attempt DFA" form, not a warm-up cost.

A related, smaller population: `anc-dollar` (`done$`), `anc-z-lc`
(`done\z`), `anc-z-uc` (`done\Z`) — auto picks `engine=dfa`,
`dfa_prefilter=offset-set-bounded`, `req_why=emitted`. Forced VM beats
auto by **1.15-1.23x, but only on `short-subject-search`** — at
`large-subject-throughput` this form is a tie-to-auto-favored (0.77-0.90x,
i.e. auto 11-30% faster), so unlike the start-anchor trio, the end-anchor
form's fixed cost IS amortized once there is real scan work to do. Six
+ six cells total (12), all `short-subject-search`/`large-subject-
throughput`, ratio range 1.05-1.27x.

**Pcrec-side fact that distinguishes this group**: `dfa_scan` is
`attempt` (not `unanchored`) for the start-anchor trio, and `req_why` is
`one-attempt` or `emitted` (never `dominated`) throughout — i.e. this is
a plain DFA one-shot/bounded form, with no hybrid-prefilter pricing
question at all. The cost is in the DFA "attempt" entry/dispatch
machinery itself, which the VM's own attempt-loop entry apparently
undercuts, at small but consistent margins.

### B — unanchored class-run DFA (byte-class prefilter) losing to a plain VM. Same family as the already-filed [OPT-5] finding.

Patterns: `cls-w` (`\w+`), `mod-a` (`(?a)\w+`), `cls-posix`
(`[[:alpha:]]+`), `unp-p-lc` (`\p{L}+`) — auto picks `engine=dfa`,
`dfa_prefilter=byte-class`, `dfa_scan=unanchored`, `dfa_scan_edge=bitmap`
(the premultiplied class-run DFA). Forced VM (no prefilter) beats auto
by **1.08-1.38x** on both `large-subject-throughput` and
`short-subject-search` (8 cells).

This is the SAME mechanism `docs/dev/opt5_step0_profile.md` already
measured and filed: the DFA's premultiplied walk is a
pointer-chasing, loop-carried-dependency chain (`next_state`'s load
address is the previous iteration's loaded value), while the VM's
possessified span-loop over a class run is address-only/independent
loads — that memo measured a much larger 5-6x gap on its own witness;
here, on the bench's own subject content, the same direction shows up at
a smaller 1.08-1.38x. **Not a new finding** — filed evidence that
[OPT-5]'s mechanism reaches this population too, at a real but modest
margin on these specific subjects.

### C — the hybrid DFA-prefix prefilter's cost is mispriced against the plain `req_byte`/`req_run` precheck it suppresses. NEW, and genuinely mixed-direction.

This is the one population in this census that is not already filed
elsewhere and is not dominated by a single amortization/dispatch-cost
story. It covers every pattern where `auto` picks `engine=vm` **with a
DFA-front hybrid prefilter attached** (`dfa_prefilter` one of
`run-pinned`/`byte-class`/`offset-set`/`memchr`) and `req_why=dominated`
or `req_why=emitted` marks whether the plain `req_byte`/`req_run`
precheck was suppressed because the prefilter was assumed to subsume it.
Forcing `--engine=vm` **deletes the prefilter and re-emits the plain
precheck directly** (confirmed from the forced testee's own record:
`prefilter: "none"`, `req_why: "emitted"` where auto's record read
`dfa_prefilter: "run-pinned"`, `req_why: "dominated"` — a real program
difference, not noise).

17 patterns, 34 non-`match-compliance` cells (`large-subject-throughput`
+ `short-subject-search`). **The direction is NOT uniform**, and that is
the finding:

- **11 of 34 cells are forced-VM wins**, 1.04-1.62x: all seven of
  `grp-cap`/`grp-named`/`grp-named-quote`/`lka-nonatomic`/`asr-k-uc`
  on `short-subject-search` (1.12-1.62x — the fixed cost of building the
  small DFA-prefix scan is pure overhead on a short, one-shot search),
  plus `lka-pos`/`lka-verb` on **both** regimes (1.06-1.30x, including
  `large-subject-throughput` — the one place in this whole census where
  a large-subject scan does NOT amortize away a hybrid-prefilter cost).
- **22 of 34 cells are auto wins**, 1.09-14.68x, concentrated in
  `large-subject-throughput`: `rec-back`/`rec-py`/`rec-g-angle`/`rec-fwd`
  (backreference/recursion patterns whose DFA-front byte-class prefilter
  is a genuine 5.9-12.5x win — a sparse candidate byte class over a
  mostly-non-matching subject), `grp-atomic-alt`/`qnt-poss-plus`/
  `lka-neg`/`lkb-neg` (8.3-14.7x), `lkb-pos` (a tie, 1.003x).

**Read side by side, `lka-pos` (`item(?= done)`) and `lka-neg`
(`item(?! done)`) are the sharpest pair**: same construct family, same
prefilter kind (`run-pinned`), same `req_why=dominated`, and opposite
verdicts at `large-subject-throughput` — `lka-neg` is an 8.0x AUTO win,
`lka-pos` is a 1.30x forced-VM win. The compile-time stamps read
identically between the two; nothing in `engine_metadata` distinguishes
them. The only difference visible from pcrec's side is the pattern's own
match semantics interacting with the subject's byte content (a negative
lookahead matches far more of a generated subject than the paired
positive one, changing how much work the DFA-front prefilter actually
prunes) — a **runtime/subject-shape fact**, not a compile-time one. This
is exactly the boundary the next section names.

## Bench-supplied context this row asked for by name

**O-74 ([FINDINGS] B115 ledger, `docs/dev/ledgers/
2026-09-29-b115-findings-tiers-f7f5a143.md`, email-specimen@0.2, a
DIFFERENT subbench from the syntax one this census reads)**: ORACLE-BEST
selector headroom is ~0 on loglines but real on email's whole-subject
forms — `floor` compliance (whole-subject) runs **×0.648 under `vm tune
0`**, `orig` compliance runs **×0.856 under `vm tune 2`**, both cases
where "the forced-VM route beats what `auto` selects: an input for
[SEL-COST]." Structurally this is the SAME shape as cause D above
(a whole-subject/compliance-regime cell, DFA-wrapper-vs-VM), on a
different, larger corpus — corroborating evidence that the OS-4 wrapper
cost generalizes past the syntax subbench's own tiny patterns.

**O-63 finding 5 (`docs/dev/outbox_to_pcrec.md`, 2026-09-27, "a rider
finding, for pcrecdev1's own auto-selection-on-short-whole-subject-
matches question")**: on syntax's OWN `grp-cap`/`grp-named`/
`grp-named-quote` whole-subject cells, the bench compared `auto-caps`
(VM, `req_why=dominated`, `prefilter=run-pinned-bounded`) against
`auto-nocaps` (DFA, `unwrapped`, same prefilter kind) and found
`auto-caps` ≈5.61 ns/subject vs. `auto-nocaps` ≈9.74 ns/subject, ×1.74 —
and the same shape on `rec-back`/`rec-py`/`rec-g-angle`/`rec-fwd`,
×1.48-1.54. **That is a captures-vs-nocaptures comparison** (D119/I-99
forbids ranking it), answering a different question from this census's
within-caps-class one — but it is worth stating plainly that it points
the SAME direction as cause D here (the DFA route costs more per call on
a whole-subject/compliance-shaped check than the VM route does), on the
identical three patterns this census's own bucket C flags for
`short-subject-search`. Three independent readings (this census's
within-caps bucket C, O-63's caps-vs-nocaps comparison, and O-74's
email-specimen finding) now agree that a whole-subject/single-search
check is the shape where pcrec's engine-selection cost model is weakest.

## What a measured selection term would need to see

**Available at compile time** (every field this census used to
distinguish causes is one): the engine `auto` would pick and why
(`RX_ENGINE`/`RX_ENGINE_WHY`), the DFA-prefix prefilter kind if any
(`RX_DFA_PREFILTER` — `none`/`memchr`/`offset-set[-bounded]`/
`byte-class`/`run-pinned[-bounded]`), whether the plain `req_byte`/
`req_run` precheck was suppressed as dominated (`RX_REQ_WHY`), the DFA
scan/entry shape (`RX_DFA_SCAN`, `attempt` vs `unanchored`), capture
count, emitted size. All of it is a property of the PATTERN alone — it
is what `[PATFACTS]` already computes and what `--emit-facts`/the
registry dumps already surface. None of it says anything about what
regime a given call will run in.

**Only available at run time, and this census's own bucket C shows it
matters**: the regime itself (a one-shot whole-subject check vs. a
search over a short subject vs. a throughput scan over a large one — the
exact three-way split this subbench's own regimes encode, and the exact
axis on which cause D and half of cause C flip sign), and the subject's
own byte content/match density (the `lka-pos`/`lka-neg` pair, identical
compile-time stamps, opposite verdicts). **A single compiled artifact
serves calls in ALL of these regimes** — pcrec has no signal at compile
time for which one a given `pcrec_search`/`pcrec_match` call belongs to,
and the subject is by definition not available until the call. So a
selection term built only from compile-time facts can, at best, pick the
engine that is right on AVERAGE over an assumed call-mix — it cannot
reproduce the per-regime optimum this census measured, because that
optimum genuinely disagrees with itself between regimes on the same
pattern (bucket A's end-anchor trio; bucket C's asymmetric direction).

## Recommended mechanism SHAPE (not designed in full)

Frank's rule: every selection is a first-match predicate-row table, no
if-then spiderweb. On this census's evidence, that table's rows would be
keyed on the compile-time facts above (a pattern shape signature: engine
candidate, prefilter kind, `req_why`, `dfa_scan` shape), each row's VALUE
being a per-regime cost estimate (or, more conservatively, a per-regime
WINNER bit) rather than one always-active decision — because bucket A
and bucket C both show the same pattern shape wanting a DIFFERENT winner
in different regimes. Concretely, a row would need to answer "for
[compile-time signature X], is the DFA-front prefilter/anchored-attempt
form worth its fixed per-call cost" as a function that a CALLER-side
knob (or a declared expected call shape, à la `--tune`) can select
between, rather than as a single build-time constant — the same shape
`[OPT-DIAL]`'s `--tune` axis already gives the size/speed trade, extended
to a regime axis. Whether that knob is a new `--tune`-like dial, a
`match_api.md`-level call-shape hint, or something else is exactly the
open design question this STEP 0 does not answer.

## Questions for the bench dev

1. **No forced-`nocaps`-VM testee exists in `syntax@0.1`'s roster**
   (`vm-caps`/`vm-in-caps` are both `captures="on"`). This census
   therefore cannot measure the nocaps population's own auto-vs-forced-VM
   margin at all — every nocaps row in `census_full.tsv`/`wins.json`
   carries `auto_ns` only, no comparator. Could the syntax subbench add
   `pcrec-vm-nocaps`(-in) testee(s), mirroring the existing caps pair, so
   a like-for-like nocaps census is possible without resorting to a
   cross-class (caps vs. nocaps) comparison?
2. **No forced-`--engine=dfa` testee exists** in this roster either, so
   this census cannot check the reverse population — patterns where
   `auto` picks VM but a forced DFA would have won. Is a `pcrec-dfa`(-caps/
   nocaps) testee feasible for `syntax@0.1`, to close that gap?
3. Bucket C's `lka-pos`/`lka-neg` pair (identical compile-time stamps,
   opposite `large-subject-throughput` verdicts) — is the generated
   subject's match DENSITY for the two patterns known/available (e.g.
   fraction of subject bytes covered by a match), so the subject-shape
   half of that asymmetry can be confirmed rather than inferred from the
   pattern text alone?
4. Confirm (or refute) that the four `other`-bucket short-subject-search
   cells this census flagged near the 1.03x-1.23x edge (`esc-octal-0`
   at 1.047x especially) sit above the per-launch bimodality floor
   (O-69) rather than inside it — this census applied the ledger's
   stated ≥3% convention mechanically and did not re-derive it.

## Size of the prize per group (summary)

| cause | population | ratio range | already filed? |
|---|---|---|---|
| D — OS-4 match-compliance wrapper cost | 60/80 caps match-compliance cells | 1.05-1.91x | YES — [OS-4], bench-tracked |
| A — anchored/bounded DFA fixed per-call cost | 12 cells (6 patterns × ≤2 regimes) | 1.05-1.27x | no |
| B — class-run DFA pointer-chasing | 8 cells (4 patterns × 2 regimes) | 1.08-1.38x | YES — [OPT-5] `opt5_step0_profile.md` |
| C — hybrid-prefilter mispricing (mixed direction) | 34 cells (17 patterns × 2 regimes), 11 forced-VM wins / 22 auto wins | 1.04-1.62x (VM win) / 1.09-14.68x (auto win) | no — genuinely new, and the win direction itself is the open question |

The only two GENUINELY OPEN, not-already-filed causes are A (small,
consistent, single-direction — a plausible near-term `[OPT-DIAL]`-style
fixed-cost fix) and C (larger population, but the win direction flips
by regime on the same pattern shape — the harder design problem, and
the one this row's mechanism must actually solve).
