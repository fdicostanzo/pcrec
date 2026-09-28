# Phase-3 reassessment — dormant `STATE:started` + parked rows

D125 close-out PHASE 3 (docs/dev/decisions.md D125; memory `pcrec-closeout-sequence`).
Read-only survey of `docs/dev/plan.md`, `docs/dev/decisions.md`, `docs/dev/dev_journal.md`,
`docs/dev/backlog_triage_2026-09-22.md` and the lane-report index in
`docs/dev/lanes/CLAUDE.md`. No measurement performed; every claim below is
either quoted from the row's own text or traced to a cited commit/report.

Six of these eleven rows were already surveyed once by `[BACKLOG-TRIAGE]`
(2026-09-22, lane backtri, `docs/dev/backlog_triage_2026-09-22.md`). Where
that survey's finding still holds six days later I say so and move on;
where something has shipped since 09-22 that changes the picture (chiefly:
`[REL-1]` fully landed and tagged `v0.1.0-beta` on 2026-09-21/22, and
`[VAR]`'s feature-column MVP shipped and closed out by 2026-09-25) I note
it explicitly.

---

## 1. `[TT-4M]` (plan.md:310) — STATE:started, dormant

**(a) Charter, one sentence:** re-open `[TT-4]`'s closed batched-compilation
levers on darwin, where `[TT-14]`/`[XARCH]` show the Mac's cost is
process-dispatch spawn tax rather than gcc CPU — validate a batch of N
patterns compiled into one gcc call / one dispatching executable, then
adopt it in `tests/harness/run.sh`.

**(b) Delivered / remaining:** Everything chartered is DELIVERED. STEP 1
(prototype+validate, `docs/dev/tt4m_darwin_validation.md`, merged
`51106544`): 2.41x/3.63x/4.28x wall at N=4/16/64, 413/413 answer-identical.
STEP 2a/2b (parallel N×P sizing + design note, `docs/dev/tt4m_step2a_
parallel_sizing.md`): N=64/P=8 recommended, 18.65x isolated. STEP 2c
(`HARNESS_BATCH=N` built in `run.sh`, lane tt4m3,
`docs/dev/lanes/tt4m3_report.md`). STEP 2d (the clean quiet-box acceptance
timing, `docs/dev/tt4m_time.md`, lane tt4mtime, 2026-09-12/13): **only
~9.5% wall / ~8-10% CPU** whole-suite saving — an order of magnitude below
the isolated prototype ratios, attributed structurally to `HARNESS_BATCH`
reaching only 3 of `make test`'s 38 (now 40) sections.

**(c) Still valid given what shipped since:** Yes, and the row says so
itself. Frank's 2026-09-16 ruling (recorded verbatim in the row): the
default is **not** flipped; the next step is a **per-section timing
attribution** to find out whether the whole-suite gap is fully explained
by unreached sections or whether the win is being eaten somewhere inside
the reached ones — explicitly **"NOT SCHEDULED — do not charter without
Frank's word."** Nothing in the six days since `[BACKLOG-TRIAGE]`
(2026-09-22) touches this; `HARNESS_BATCH=N` itself keeps shipping small
fixes as a side effect of other lanes (`w231_report.md`,
`k60meas_report.md`'s alloc-injector note, `axes2fix`'s `${var}` exclusion
fix 2026-09-25) but none is the re-attribution investigation.

**(d) Disposition: RE-PARK.** D77 trigger = Frank's own word to charter
the per-section timing attribution (already named verbatim in the row).
Not a measurement gap on pcrec's side — a scheduling gate only Frank can
lift.

**(e) Dependency:** none stated; the investigation would reuse
`tests/harness/run.sh`'s existing instrumentation.

---

## 2. `[DD-8]` (plan.md:1015) — STATE:started, dormant

**(a) Charter:** adopt `docs/spec/table_contract.md` for `--emit-ir`'s
output (D106) — a narrow "TABLE-MECHANISM ADOPTION" sub-task inside a
wider filler-era row that originally promised `--emit-ir`/`--emit-dot`
tracer facilities (`APPROACH.md` §6, never built).

**(b) Delivered / remaining:** The chartered sub-task is **DONE**:
"DELIVERED 2026-09-19 (lane dd8)" — `--emit-ir` renders as nine named
`#section` TSV blocks through the wave-1 emission kit, `docs/spec/
ir_listing.md` is the new format contract, 11 readers converted to
declaration-based parsing, not an `abi` event (0 movers on 2,803/2,804
corpus rows). MERGED `b99d0eed`. Explicitly named as **STILL
NOT-STARTED WITHIN THIS ROW**: `--emit-dot`, the DFA/prefilter listing
section (D106 addendum items 3-4), and the enriched `[V-H]` trace.

**(c) Still valid:** The row's own text keeps it `STATE:started` "for its
future sub-parts" — but none of those sub-parts have ever been separately
chartered, and `[V-H]` (STATE:not-started, plan.md:563) is **already its
own row** covering the enriched-trace half. Nothing has shipped since that
changes this; no lane report after `dd8_report.md` touches `--emit-dot` or
a DFA/prefilter listing section.

**(d) Disposition: CLOSE-AND-FILE.** Close `[DD-8]` — its D106-scoped
charter (the table-contract adoption) is complete and merged. File the
residual as a new row (e.g. `[EMIT-DOT]`): `--emit-dot` graph output +
the DFA/prefilter listing sections (D106 addendum items 3-4). Do **not**
re-file the trace half — `[V-H]` already owns it.

**(e) Dependency:** none for the closure; the filed residual has no
stated dependency either (D106 called both "FUTURE").

---

## 3. `[DD-11]` (plan.md:1072) — STATE:started, dormant

**(a) Charter:** replace the ad hoc option-conditional definitions
(`$`, `\Z`, POSIX classes, …) with a predicate-scanned DATA table
(`docs/design/definitions_table.md`) and a `--list-definitions` registry
surface, so the compiler's own replacement rules are inspectable instead
of hand-copied prose.

**(b) Delivered / remaining:** `[DD-11.1]`-`[DD-11.4b]` MERGED `0f5a98f`
(2026-08-29, lane dd11b) and BATTERY-PROVEN (battery 3, pin `96e44c2`,
2026-08-30): the table, `--list-definitions`, the 354-cell option-matrix
self-oracle (0 disagreements), the base-tier literal-escape rows. The row's
own text: **"everything chartered for this row is DONE."** Left gated:
`[DD-11.5]` ("wire the substitution into real compilation" —
`definitions_table.md` §"[DD-11.5]") and `[DD-11.6]` (the tranche-C
customers, D63's second prefilter instance + DD-7's reverse BOT variant),
both stated as "a follow-on row when M6.6 lands, now carrying S3's
precondition" — S3 being a per-call-site `pcrec_ast_stamp` on every
lookaround-shaped builder.

**(c) Still valid given what shipped since — and this is the sharpest
finding in the whole survey:** `[M6.6]` (module `lookaround`) closed
**2026-08-24**, i.e. **five days before** this DD-11 row's own text was
even written (2026-08-29/30) — the gate was already satisfied at the
moment the row was authored, and has now sat unactioned for over a month.
`[BACKLOG-TRIAGE]` (2026-09-22) already flagged this exact staleness
("the gate condition appears to have been met for nearly a month without
the follow-on being reopened"); six more days have passed with no action.
`pcrec_ast_stamp(` has 10 live call sites in `src/` today (grepped), so
S3's precondition reads as already discharged in practice, though nobody
has run `definitions_table.md`'s own design pass to confirm it against the
full lookaround-builder population.

**(d) Disposition: RE-CHARTER.** Trigger long met. Next concrete step:
charter `[DD-11.5]` per `definitions_table.md`'s own design ("wire the
table-driven substitution into real compilation," with the `pcrec_ast_stamp`
precondition verified first as its own short design-check step) —
admin-structural column, S-M size, sonnet fits.

**(e) Dependency:** `[DD-11.6]`'s own gate is "`[DD-11.5]` landed and
answer-identical on the corpus" — sequential, not parallel.

---

## 4. `[CC-CLANG]` (plan.md:1198) — STATE:started, dormant

**(a) Charter:** validate clang as a second compiler for pcrec's emitted
C (Frank: "we should do some basic compatibility testing and consider a
partial bench axis").

**(b) Delivered / remaining:** STEP 1 (compatibility survey) + STEP 2
(`CLANGGEN=1` opt-in corpus sweep) "DELIVERED GREEN 2026-09-01... branch
`lane/cc` 19 commits... codegen 106/106... CLANGGEN=1 shipped." `[BACKLOG-
TRIAGE]` (2026-09-22, open question 4) independently confirmed via
`git merge-base --is-ancestor origin/lane/cc HEAD` that `lane/cc` **is**
merged and later commits build on its mechanism — the row's own text
("awaiting merge review") is simply stale prose, not an open state.
Remaining: STEP 3, "the bench's PARTIAL cc axis (their build, our ask;
goes in I-22)," scoped as **"behind Frank's perf hold."**

**(c) Still valid given what shipped since:** The "perf hold" is a
2026-08-31/09-02-era gate (`docs/dev/dev_journal.md` lines ~18671-18877,
all from that window; no mention anywhere after). It was superseded
wholesale by **D119** ("THE OPTIMIZATION LOOP," ruled 2026-09-21), which
opens bench measurement windows continuously and by design — cycle 1 and
cycle 2 of the optimization loop have run one after another since, with
their own inbox/outbox traffic (`b1ledger_report.md`, `b2ledger_report.md`,
`o64read_report.md`, …). There is no standing "perf hold" left to be
behind.

**(d) Disposition: RE-CHARTER.** The gate is dissolved, not merely lifted.
Next concrete step: relay the STEP 3 ask (a clang-vs-gcc partial axis on a
few bench cells) to the bench dev via the now-standing inbox channel
(D78) — admin column, tiny (one inbox item), no lane needed on pcrec's
side beyond drafting the ask.

**(e) Dependency:** the bench's own scheduling, via `inbox_from_pcrec.md`.

---

## 5. `[OPT-3]` (plan.md:1416) — STATE:started, dormant

**(a) Charter:** speed up the DFA scan edge/transition loop (originally
framed as "SIMD the candidate-start skip loop"; STEP 1 measurement
corrected the frame).

**(b) Delivered / remaining:** STEP 1 (measurement, `docs/dev/
opt3_dfa_scan_measurement.md`) found the skip loop is not the loss and
SIMD is not the fix; all the cost is the transition loop, latency-bound.
STEP 2 (premultiplied transition table, `docs/design/
premultiplied_dfa_table.md`, abi 6→7) shipped: **1.794x** measured,
putting pcrec **ahead of PCRE2-JIT on all three bench subjects** (0.819x).
Two STEP 3 candidates were named and priced but explicitly **"D77: not
chartered"**: (i) generalizing the skip loop from state-0-only to every
self-looping state (branch-predict a run's end), blocked on **a
non-periodic subject (I-10)** because the bench's own t-a/t-b subjects are
periodic and flatter every branch-cost number; (ii) a two-byte transition
table, ruled out by the same guess-and-verify branch-cost argument and
gated on STEP 2's size rule regardless.

**(c) Still valid given what shipped since:** I-10 (a non-periodic subject
from the bench) has never been delivered — grepped the journal and
`docs/dev/optloop/` for "I-10", "period-k", "non-periodic subject": no hit
past the original 2026-08-26 mentions. `[BACKLOG-TRIAGE]` reached the same
conclusion ("D77: not chartered — needs a non-periodic subject, I-10").

**(d) Disposition: RE-PARK.** Trigger unmet: the bench has not yet
supplied a non-periodic scan subject. Worth flagging to the OPTLOOP
process as a small, cheap ask (a subject-pool addition), since the
mechanism itself (branch-checked run-end skip) is fully designed and
priced already.

**(e) Dependency:** the bench's subject pool (I-10), via the inbox
channel.

---

## 6. `[OPT-5]` (plan.md:1446) — STATE:started, dormant

**(a) Charter:** the `{0,n}` class-count DFA-vs-VM selection knee — why
the counted DFA loses to pcrec's own VM on in-class letter runs, and what
to do about it.

**(b) Delivered / remaining:** STEP 0 (mechanism profile,
`docs/dev/opt5_step0_profile.md`): the gap is a dependency-chain SHAPE
(DFA pointer-chasing vs VM address-only), flat across a 64x n range — no
count crossover, no limits.def row. STEP 1 (the scan edge,
`src/opt/scanedge.c`, abi 13): letters 2.71x-3.03x, VM gap 6.00x→2.03x,
battery-proven. STEP 2 (start-pinned search elision — the reverse-pass
elision that actually closed the residual VM gap, `docs/design/
opt5_step2_twopass.md` rev 2, abi 16, lane opt5i): merged and
battery-proven, pin `288d505`. Two further named candidates remain
explicitly un-built: the **period-k scan-edge collapse** (Frank's
`(?:ab){1,100}` idea, with the m/n split, cap refinement and batch
refinement all designed in prose) — D77 trigger stated as "a measured
counted-string-repeat cell (the bench's `nest` family is the candidate
instrument)" — and **construction-time scan-edge synthesis** (collapsing
a counted single-class repeat before subset construction ever materializes
the states), which has no independent trigger of its own beyond the
period-k mechanism's need being established.

**(c) Still valid given what shipped since:** No later mention of
"period-k" or "counted-string-repeat" anywhere in the journal or
`docs/dev/optloop/`. The sibling row `[OPT-VMFL]` (the direct-branch VM
dispatcher) **did** close (`STATE:completed`, 2026-09-26, lane closetails)
but on its own separate D77 trigger, unrelated to OPT-5's period-k
question. `[OPT-VEDGE]` (view-tolerant edge) is a separate not-started
row. Nothing discharges OPT-5's own remaining trigger.

**(d) Disposition: RE-PARK.** D77 trigger unmet: no measured
counted-string-repeat cell from the bench's `nest` family has been
reported since it was named (2026-08-31).

**(e) Dependency:** the bench's `nest` family subjects, via the inbox
channel (same shape as OPT-3's I-10 ask — worth bundling the two asks).

---

## 7. `[ENG-ABS]` (plan.md:1455) — STATE:started, dormant

**(a) Charter:** two mechanisms under one row — (1) absorb `^` into
`ENG_UNANCH`, (2) an unwrapped-forward-DFA anchored-match engine.

**(b) Delivered / remaining:** Mechanism 2 MERGED `dfd112b` (2026-08-29),
panel-reviewed (r41), abi 10, `-fno-anchored-dfa` bit 17: "NO MISCOMPILE
over 148,917 cells," 1.031x/1.036x vs the VM, 0.482x on short emails.
Battery-proven. Mechanism 1 (`^`-absorption) was **never opened**: "stays
gated on `[BENCH-1]`'s `^`-on-some-branches case... is NOT opened" —
verbatim in the row.

**(c) Still valid given what shipped since:** `[BENCH-1]` closed
2026-09-22 (`closefold_report.md`) and folded its outstanding dependency
text into `[OPTLOOP]` at seven rows found by grep — `[ENG-ABS]` is one of
the seven, re-pointed rather than left dangling. I checked both
`cycle1_analysis.md` and `cycle2_batch2_reading.md`/`cycle2_admitfix_
reading.md` (and the `b1ledger`/`b2ledger` readings) for a `^`-on-some-
branches losing cell: none surfaced. The trigger is genuinely unmet, not
merely un-revisited.

**(d) Disposition: RE-PARK.** Trigger restated per the 2026-09-22
re-pointing: an OPTLOOP cycle analysis (any future cycle over `capability`
or a successor subbench) surfacing a `^`-on-some-branches losing cell.

**(e) Dependency:** `[OPTLOOP]` cycle ranking (was `[BENCH-1]`).

---

## 8. `[ENG-ISL]` (plan.md:831) — STATE:started, PARKED

**(a) Charter:** DFA/VM "islands" — regions of one engine's shape spliced
into the other; the first concrete instance chartered is the VM
alternation-as-trie dispatch island (replacing N-way serial branch tries
with a sorted-trie dispatch).

**(b) Delivered / remaining:** STUDY `[ENG-ISL.S0]` STATE:completed
(2026-09-03, `docs/design/alt_dispatch_study.md`): up to 120x on w-2048,
zero mismatches over 25.7M subject positions. STEP 1 (the real emitter
mechanism, `emit_vm.c`'s sorted-trie alternation lowering) MERGED
`cee7c741` (abi 18), panel r53, "27,256 answer cells, 0 divergences."
OWED at merge: `[CC-DIFF]` STEP 2 (the always-inline gate's size term —
STEP 1's own §4.2 finding is that every ladder artifact is frameless and
gets fully inlined, ×3.8 `.text`/×4.3 gcc time on w-256, needing a size
term the always-inline gate does not have); `[OPT-DIAL]` pricing; and two
named STEP 2 shapes (the `ab[cd]|abx` "tail form"; class-member
expansion).

**(c) Still valid given what shipped since:** Explicitly PARKED 2026-09-21
into `[BACKLOG-TRIAGE]` (Frank: "the bench matrix ranks it against
everything else; not before `[REL-1]`"). `[REL-1]` **has now fully
landed** — tagged `v0.1.0-beta` 2026-09-22 (`plan_completed.md:4265`), all
eleven `[REL-1.n]` children completed. The second half of the trigger —
bench-matrix ranking — is not separately satisfied: `cycle1_analysis.md`
itself (cited inline in a nearby, unrelated `[M4.6]`-adjacent paragraph on
the same page of plan.md) scores this row's own mechanism at **0** on the
capability subbench — "not in this matrix, not refuted." No cycle since
has re-scored it upward.

**(d) Disposition: RE-PARK.** `[REL-1]` trigger discharged; bench-matrix
trigger not. Restate: an OPTLOOP cycle analysis assigning this row a
nonzero score (a real losing cell attributable to serial alternation-try
cost) is what reopens it — not simply the calendar clearing `[REL-1]`.

**(e) Dependency:** `[CC-DIFF]` STEP 2 (the inline-gate size term) is a
real prerequisite for STEP 2's tail-form/class-expansion work even once
reopened, since both would land more frameless code onto the same
uncapped always-inline gate.

---

## 9. `[DD-13]` (plan.md:1016) — STATE:started, PARKED (parent row)

**(a) Charter:** the unified pattern-source/test-file format — one `.rxt`
successor serving compilation source ([V-E]), test carrier, and
pcrec-bench's set format, with library-style named-pattern composition.

**(b) Delivered / remaining:** An enormous amount has shipped under this
umbrella: `[DD-13a]` (requirements, completed), `[DD-13b]` (grammar/
semantics design, completed `daa6b6c`), `[DD-13b.panel]` (completed),
`[DD-13b.W1]` (head grammar + parser + composer, completed 2026-09-19 per
`plan_audit_2026-09-19.md`), `[DD-13b.W1.1]`/`[DD-13b.W1.2]` (both
merged+battery-proven), `[DD-13b.W1.3]` (see row 10 below), and the much
later `[DD-13b.W23]` wave (schema table, fourteen productions, `include`,
`--list-source` sections — five steps, all merged 2026-09-13/15,
delivered as a stacked chain per `docs/dev/lanes/w231_report.md` through
`w235_report.md`). `[PLAN-AUDIT]` (2026-09-19) found DD-13's own real
remainder is "M[edium], same chain" as `[DD-13b.W1.3]`'s remainder — i.e.
the composed-path / `[PFX-1]` dependency described in row 10. Beyond
that: `[DD-13b.W1.4]` (PCRE2 grouplist semantics) has never been started,
and W2/W3 waves are deliberately deferred ("no W2/W3 production is built
ahead of its consumer" — e.g. `[LIB]`, not started).

**(c) Still valid given what shipped since:** Explicitly PARKED 2026-09-21
"not before `[REL-1]`" (landed, as above) "the bench matrix ranks it
against everything else" (not separately re-ranked). One relevant
sequencing fact: the FEATURE column's other live row, `[VAR]` (pattern
variables), got chartered and fully shipped its MVP in the same window
(`varmvp_report.md` 2026-09-23 through `varfollow_report.md` 2026-09-25) —
i.e. the feature lane picked `[VAR]` over `[DD-13]` post-`[REL-1]` and has
now cleared it, so the feature lane is free again.

**(d) Disposition: RE-PARK**, but flagged as the **readiest** of the
parked rows: `[REL-1]` cleared, the feature lane that was occupied by
`[VAR]` is now free, and the only hard remaining blocker on the row's own
immediate residual is `[PFX-1]` (see row 10) rather than any open design
question. Still Frank's sequencing call per his own ruling, not a
measurement gap.

**(e) Dependency:** `[PFX-1]` STEP 0 (not started) for the composed-path
residual; `[LIB]` (not started) for W2/W3.

---

## 10. `[DD-13b.W1.3]` (plan.md:1052) — STATE:started, PARKED (child of DD-13)

**(a) Charter:** the composer proper — named-definition composition,
`export`/site-qualified delivery, the name grammar, the altwide dogfood,
and a composition identity proof.

**(b) Delivered / remaining:** MERGED `8d68ddc2` (2026-09-04, abi 20).
Fully validated: `make test` 33/33 sections, `make test-axes` 21 axes
0 mismatches, `make test-definitions` 22/0, `make test-rxtsource` 121/0
with the corpus census unmoved, the identity gate 16/0 at both (A) and
(B), `make strict` clean. Frank's D89 addenda 1-4 landed in full. Exactly
**one** item was carved out at merge: **W1.3.1**, "the run.sh
composed-block path" — four sites in `flush_block`'s tail assume the `rx`
prefix, which the format's per-block prefix-mapping (`-`/`.` → `_`)
breaks. Frank ruled the shape (OPTION 1: the harness carries the target's
prefix through `flush_block`'s tail) the same day, but explicitly said
**"build it AFTER `[PFX-1]` STEP 0 (D96) so the four prefix sites are the
exported set only."**

**(c) Still valid given what shipped since:** `[PFX-1]` (plan.md:1453,
"the only items getting the prefix should be the exported items", D96) is
**still `STATE:not-started`** — never chartered, confirmed by grep against
both `plan.md` and `plan_completed.md`. So the one concrete blocking
dependency this row's own residual names has not moved since 2026-09-04.
Everything else about the row (D89's data model, the name grammar, the
altwide dogfood) is done and stable; nothing since has touched it.

**(d) Disposition: RE-PARK.** The parent's `[REL-1]`/bench-matrix park
applies, AND there is a genuinely unmet prerequisite specific to this
row's own residual: `[PFX-1]` STEP 0 has not landed. Re-open only after
`[PFX-1]` STEP 0, or on Frank's sequencing word for the parent.

**(e) Dependency:** `[PFX-1]` STEP 0 (hard blocker, unmet); parent
`[DD-13]`'s own sequencing gate.

---

## 11. `[CLS-TREE]` (plan.md:1561) — STATE:started, PARKED

**(a) Charter:** the general class-matcher KIT — a class matcher composed
per-section from a small set of representations (mask compare / range
compares / bound check / tree-page-table-bitmap), statically selected by
a sectioning DP, replacing the single automaton-structure encoding that
makes huge Unicode classes (`\p{L}`) cost hundreds of KB.

**(b) Delivered / remaining:** THE STUDY delivered+merged 2026-09-11
(`docs/dev/cls_tree_study.md` + `studies/cls_tree_study/`, lane clstudy):
kit-not-per-class-form is the headline finding, the sectioning DP with
lambda as the dial, D77 verdict = Constraint 2's pre-analysis cache is
**NOT** triggered (25.86ms worst-set discovery vs 144ms compile budget),
1.885B compared answers / 0 mismatches. The ns/char timing arm (the second
half Frank's 09-11 ruling required before a design note) is cited as done
in the row's own text. **Remaining:** the design note itself (candidate
layouts scored against the real 312 script sets + the K53 six + a
byte-class sample; the sectioning rule; dial integration) + a light panel
— explicitly stated as the next step, never chartered.

**(c) Still valid given what shipped since — and this row is the most
ACTIVE of anything surveyed here:** Explicitly PARKED 2026-09-21 "not
before `[REL-1]`" (landed). But Frank kept extending this row's own
scope **after** that park: a "+2 PLACEMENT DIRECTION" ruling on
2026-09-16 (before the park, already superseding the study's own caution),
and — three days before this survey — a **SCOPE ADDITION on 2026-09-25**:
"hit everything class related at the same time like the class tree work,"
naming a fresh measured need, **K67** (`\p{L}+` under `-e utf8`: 77s
pcrec compile time), with part of K67 already carved off into two other
filed rows (`[OPT-RETRY-REUSE]`, `[OPT-CLOSURE-CTX]`) and the class's own
share staying here. Frank also supplied a concrete new design direction
the same day (a single indexed bit array at the `--tune` speed end,
engine-external kit predicate vs. a compact prefix/suffix-shared byte
automaton for the DFA side — bare `\p{L}`'s whole DFA is 299 states vs.
the shipped 2,711-node flat NFA alternation). The `[K53-SELRETRY]`
alternative trigger ("opens after K53-SELRETRY lands or on Frank's word")
is independently satisfied too — K53-SELRETRY closed 2026-09-10.

**(d) Disposition: RE-CHARTER.** Every stated trigger is met
(`[REL-1]`, `[K53-SELRETRY]`), the design has a fresh, specific, and
recent (2026-09-25) direction from Frank himself, and there is a real
measured need (K67) rather than a speculative one. Next concrete step:
the design note (candidate layouts scored against the three real
populations, the sectioning rule, `--tune` dial integration, the
engine-external-kit-vs-DFA-automaton split Frank named 09-25) + a light
panel before implementation — opus tier per the row's own stated
engine-tier choice, size L.

**(e) Dependency:** none blocking; `[OPT-RETRY-REUSE]`/`[OPT-CLOSURE-CTX]`
are siblings carved off the same K67 measurement, not prerequisites.

---

## Summary table

| Row | Charter status | Trigger state | Disposition |
|---|---|---|---|
| `[TT-4M]` | Steps 1/2a/2b/2c/2d all delivered; re-attribution investigation named, unscheduled | Frank's word — unmet | **RE-PARK** |
| `[DD-8]` | Table-contract adoption delivered+merged | n/a (scope complete) | **CLOSE-AND-FILE** (`--emit-dot` + DFA/prefilter listing → new row; `[V-H]` already exists) |
| `[DD-11]` | `.1`-`.4b` delivered+battery-proven | M6.6 — met **2026-08-24**, over a month stale | **RE-CHARTER** (`[DD-11.5]`) |
| `[CC-CLANG]` | STEP 1/2 delivered+merged (confirmed by `git merge-base`) | "Perf hold" — dissolved by D119 (OPTLOOP, 2026-09-21) | **RE-CHARTER** (STEP 3, one inbox ask) |
| `[OPT-3]` | STEP 1/2 delivered+merged, ahead of PCRE2-JIT | I-10 non-periodic subject — unmet | **RE-PARK** |
| `[OPT-5]` | STEP 0/1/2 delivered+merged+battery-proven | Measured counted-string-repeat cell (bench `nest` family) — unmet | **RE-PARK** |
| `[ENG-ABS]` | Mechanism 2 delivered+merged; mechanism 1 never opened | `^`-on-some-branches OPTLOOP cell — unmet | **RE-PARK** |
| `[ENG-ISL]` | Study + STEP 1 delivered+merged | `[REL-1]` met; bench-matrix score still 0 | **RE-PARK** |
| `[DD-13]` (parent) | Huge delivery history (a/b/panel/W1/W1.1/W1.2/W1.3/W23 all shipped) | `[REL-1]` met; bench-matrix ranking pending; feature lane now free (VAR MVP shipped) | **RE-PARK** (readiest of the parked set) |
| `[DD-13b.W1.3]` (child) | Fully delivered+validated; one carve-out (W1.3.1) | `[PFX-1]` STEP 0 — unmet, still not-started | **RE-PARK** |
| `[CLS-TREE]` | Study delivered+merged; design note is the sole remaining step | `[REL-1]` + `[K53-SELRETRY]` both met; K67 supplies a fresh 2026-09-25 measured need | **RE-CHARTER** |

## RE-CHARTER candidates, ranked

1. **`[DD-11.5]`** — smallest, most overdue (M6.6 gate has sat stale for
   over a month), design already written (`definitions_table.md`),
   admin-structural, sonnet-sized. Cheapest correct-the-record win in the
   whole survey.
2. **`[CC-CLANG]` STEP 3** — trivially small (one bench inbox ask), the
   blocking gate no longer exists as a concept.
3. **`[CLS-TREE]` design note** — largest (L, opus), but the freshest and
   most actively Frank-steered of anything here (scope additions as
   recently as 2026-09-25), with a real measured need (K67) behind it.

`[DD-8]`'s residual is a filing action, not a charter, and is listed
separately above.
