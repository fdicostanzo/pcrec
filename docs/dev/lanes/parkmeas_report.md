# parkmeas — D137: parked rows' measurement/bench needs, and the [OPTLOOP] umbrella

Lane `parkmeas` (2026-09-30, docs only: `docs/dev/plan.md` edited, this report
written; no `src/`, no `make`, nothing sent, nothing pushed). Branch
`lane/parkmeas` from `045f92c7`. pcrec-bench was NOT read (unreachable); every
bench ask below rests on what pcrec's own docs record, and section A9 lists the
questions only the bench can answer, for relay.

Sources read: decisions.md D137/D119/D125, plan.md (all rows named below, in
full), `docs/dev/ph3_reassessment_2026-09-28.md`, `opt3_dfa_scan_measurement.md`,
`optloop/cycle1_analysis.md` §M5, `optloop/cycle1_profile.md` §M5,
`optloop/cycle2_close.md` §2/§4, `sel_cost_census.md`, `tt4m_time.md`,
`tt4m_batch_customers.md`, `design/dd13_format/format_design.md` §wave table.

## 0. Findings the brief did not anticipate (read first)

1. **[ENG-ABS]'s `^`-on-some-branches gate was already satisfied, and the
   phase-3 reassessment said the opposite.** `ph3_reassessment_2026-09-28.md` #7
   reads "genuinely unmet" after grepping cycle-1/cycle-2 readings for a
   `^`-on-some-branches losing cell. cycle 1 named exactly that cell:
   `wild-waf-crs-942360-concat-sqli` (thr 5.41x vs re2-longest, srch 1.53x;
   `^(?:json\.)?...` in one branch of a 1,460-byte alternation;
   `RX_DFA_SCAN attempt`, prefilter/table/edge all `none`, start_max =
   subject_length, 8.83 ns/B) — `cycle1_analysis.md` §M5, RATIFIED as
   `[OPT-ATTEMPT-SPLIT]`, whose row the ENG-ABS text itself cites. cycle 1's
   profile (`cycle1_profile.md` §M5.b) then measured the upper bound: deleting
   the `^` arm gives x3.51 (8.42 -> 2.40 ns/B, still 48% short of the 1.62 target)
   at a summed artifact size of 537,078 B. So BENCH-1's job for this row ("add a
   `^`-on-some-branches case and measure an actual loss") is done; what is unmet
   is a SELECTION (batch 2 and 3 took other mechanisms) and a SIZE decision (the
   row's own argument against a default landing).
2. **What [BENCH-1] was.** Chartered 2026-08-13 (sixteenth session): "feature-
   spanning benchmark expansion + the prioritizer" — grow the 9-case basic bench
   into a capability map that ranks engine work by measured loss. It was
   CLOSED 2026-09-22 (lane closefold, Frank; `plan_completed.md`:
   "FOLDED into D119's [OPTLOOP] (the bench repo D78 + the cause-ranked analysis
   are its two jobs)"). Its gate text in seven rows was re-pointed at [OPTLOOP]
   (ENG-ABS, ENG-CUT, ENG-PGO, OPT-SIMD, SIMD-META, ENG-ISL/M4.6, BENCH-CEIL).
   Satisfied? In substance yes: `capability@0.1` (128 cells), `cycle1_analysis.md`
   ranking and the standing bench repo are the instrument it asked for. The
   per-row "witness" is now produced by an OPTLOOP cycle's analysis, and cycle 1
   produced the `^` witness (finding 1).
3. **[TT-4M-TIME] is stale `not-started`**: its charter (the clean quiet-box
   timing pair, the customer enumeration, the san feasibility note) was
   DELIVERED by `docs/dev/tt4m_time.md` (lane tt4mtime, 2026-09-12/13) and
   `docs/dev/tt4m_batch_customers.md`. It is retagged completed here; what
   remains is the per-section attribution Frank ruled "NOT SCHEDULED" on
   2026-09-16, refiled as `[TT-4M-ATTRIB]`.
4. **[DD-13b.W1.3]'s gate `[PFX-1]` STEP 0 is a MEASUREMENT (a census), not a
   build.** Its own text: "the CENSUS — every prefixed identifier in a
   representative artifact set classified EXPORTED vs INTERNAL against the spec;
   every harness/test site that reads an INTERNAL prefixed name; the emitted-bytes
   saving per artifact." No `src/` change. STEP 1 is the build (one abi event).
   So the gate is satisfiable now by a light lane (A7).
5. **[OPT-3]'s I-10 is partly answered on the record.** `dev_journal.md`
   ~16855 records the bench measuring "I-10's confound ... 1.64x on the DFA
   loop (parity with the JIT on real failing prose, 0.74x on the periodic
   subject)". What has never been supplied is a non-periodic subject usable for
   the branch-cost instrumentation (same-state fraction, run-end mispredict).
   The ph3 reassessment's "no hit past 2026-08-26" is true of the plan and
   `optloop/`, not of the journal. Relay question Q1 asks the bench for the
   subject.
6. **[ENG-ISL]'s two "OWED" items are already discharged**: `[CC-DIFF]` STEP 2
   and `[OPT-DIAL]` both shipped (`ccd2_report.md`, `dialimpl_report.md`, abi
   25-26). Only the two named STEP 2 shapes remain.

## 1. `grep -n STATE:started docs/dev/plan.md` — before and after

Before (`grep -n STATE:started docs/dev/plan.md | cut -c1-120`; line 20 is the
recipe text):

```
20:    grep -n "STATE:started" docs/dev/plan.md
311:- [TT-4M] STATE:started (CHARTERED by Frank 2026-09-08, fifty-seventh session, re-opening [TT-4]'s closed levers ON 
329:- [OPTLOOP] STATE:started (next cycle HELD (Frank 2026-09-26, close-out sequence D125): finish the in-flight cycle-1
356:  - [OPT-LITSCAN] STATE:started (**S1 STEPS 1-5 BUILT 2026-09-25 on lane/s1build (pending merge), per litscan_s1.md 
371:- [UCP] STATE:started (U2 MERGED 2026-09-30 (u2land, via land3b/main a527ebb4); U3 CHARTERED 2026-09-30 AS A CAPABIL
372:- [VAR] STATE:started (CHARTERED by Frank 2026-09-23 ~09:2x, seventy-seventh session — the feature hold LIFTED for t
494:- [BENCH-UTF8] STATE:started (RULED by Frank 2026-09-22 ~23:4x, seventy-seventh session: "Build the utf bench. But m
734:- [ENG-ISL] STATE:started **PARKED 2026-09-21 into [BACKLOG-TRIAGE] (Frank, seventy-fourth session: "agree on sequen
930:- [DD-13] STATE:started **PARKED 2026-09-21 into [BACKLOG-TRIAGE] (Frank, seventy-fourth session: "agree on sequenci
974:  - [DD-13b.W1] STATE:completed (CLOSED 2026-09-19, seventy-first session, per docs/dev/plan_audit_2026-09-19.md: de
975:  - [DD-13b.W1.3] STATE:started **PARKED 2026-09-21 into [BACKLOG-TRIAGE] (Frank, seventy-fourth session: "agree on 
981:  - [DD-13b.panel] STATE:completed (CLOSED 2026-08-29 ~17:4x: docs/dev/reviews/2026-08-29-r44-dd13b-format.md — r44-
1370:- [OPT-3] STATE:started — **STEP 1 MEASURED 2026-08-26** (lane srOpt3, docs/dev/opt3_dfa_scan_measurement.md; measu
1409:- [OPT-5] STATE:started (STEP 0 MEASURED 2026-08-31, lane opt5m, docs/dev/opt5_step0_profile.md, merged a2a9e0d, I-
1417:- [ENG-ABS] STATE:started (SECOND MECHANISM BATTERY-PROVEN 2026-08-29 ~05:4x on 808740c (code 517be95 = merge dfd11
1535:- [CLS-TREE] STATE:started **S3 MERGED 2026-09-30 (a0886a08 via land3b, main a527ebb4 era; cls_identity 15,905/15,9
```

After (`grep -n STATE:started docs/dev/plan.md | cut -c1-120`; line numbers moved by the inserted rows; line 20 is the recipe text):

```
20:    grep -n "STATE:started" docs/dev/plan.md
330:- [OPTLOOP] STATE:started (D137, Frank 2026-09-30: every optimization row outside this umbrella now sits UNDER it as
391:  - [OPT-LITSCAN] STATE:started (**S1 STEPS 1-5 BUILT 2026-09-25 on lane/s1build (pending merge), per litscan_s1.md 
406:- [UCP] STATE:started (U2 MERGED 2026-09-30 (u2land, via land3b/main a527ebb4); U3 CHARTERED 2026-09-30 AS A CAPABIL
407:- [VAR] STATE:started (CHARTERED by Frank 2026-09-23 ~09:2x, seventy-seventh session — the feature hold LIFTED for t
529:- [BENCH-UTF8] STATE:started (RULED by Frank 2026-09-22 ~23:4x, seventy-seventh session: "Build the utf bench. But m
1009:  - [DD-13b.W1] STATE:completed (CLOSED 2026-09-19, seventy-first session, per docs/dev/plan_audit_2026-09-19.md: d
1018:  - [DD-13b.panel] STATE:completed (CLOSED 2026-08-29 ~17:4x: docs/dev/reviews/2026-08-29-r44-dd13b-format.md — r44
1572:- [CLS-TREE] STATE:started **S3 MERGED 2026-09-30 (a0886a08 via land3b, main a527ebb4 era; cls_identity 15,905/15,9
```

Remaining `started`: [OPTLOOP] (parent, D125 hold noted), [OPT-LITSCAN] (open), [UCP], [VAR], [BENCH-UTF8], [CLS-TREE] (live builds/other lanes). Two `STATE:completed` hits above ([DD-13b.W1], [DD-13b.panel]) are pre-existing resident completed rows, matched by the unanchored recipe grep. Anchored counts (`^\s*- \[[^]]*\] STATE:started` / `:not-started`): started 13 -> 6; not-started 106 -> 112 (+7 refiled rows [OPT-3-RUNEND], [OPT-5-PERIODK], [ENG-ABS-CARET], [ENG-ISL-S2], [DD-13b.W1.3.1], [DD-13b.W1.4], [TT-4M-ATTRIB]; -1 [TT-4M-TIME] retagged completed).

## A. Per-row measurement / bench needs

Legend. **Owner**: `pcrec` = a pcrec lane (heavy timing on ubuntubudu via
pcrecdev2's executor channel, per BOILERPLATE); `bench` = an I-note to pcrecdev2
through `inbox_from_pcrec.md` (D78, single-file `[inbox]` commit). All I-note
numbers (`I-NN`) and pins (`<PIN>`) are the manager's to fill at send time.

| # | row | exact need | owner | decides |
|---|---|---|---|---|
| A1 | [OPT-3] | non-periodic 1 MB DFA-scan subject; same-state fraction + run-end branch cost on it | bench (subject) then pcrec (scratch measurement) | whether STEP 3 (b) run-end skip / two-byte table is worth chartering |
| A2 | [OPT-5] | a measured counted-STRING-repeat cell (`(?:lit){m,n}`) from the bench's `nest` family, plus the corpus population census | bench (cell) + pcrec (census, hand-twin) | period-k scan edge; construction-time synthesis |
| A3 | [ENG-ABS] | census of `ENG_ATTEMPT` with `start_max = subject_length` (the ATTEMPT-SPLIT precondition) and a size-priced choice between the two constructions; witness gate MET (finding 1) | pcrec (compile-only, Mac OK) + one bench relay | build [OPT-ATTEMPT-SPLIT] vs absorb `^` vs decline on size |
| A4 | [ENG-ISL] | corpus/bench-pattern census of the two named STEP 2 shapes; a bench cell losing to serial alternation-try cost | pcrec (census) + bench (cell) | nonzero OPTLOOP score reopens it |
| A5 | [OPTLOOP] parent | a CURRENT-PIN re-rank input (cycle 3 needs it); the hold itself is Frank's word | bench (re-measure) | cycle-3 analysis when the D125 hold lifts |
| A6 | [DD-13] | no measurement; hard blocker is A7; W1.4/`(?&site.group)` wait for a consumer | pcrec (A7) + bench (Q9) | sequencing |
| A7 | [DD-13b.W1.3] (gate [PFX-1] STEP 0) | the PFX-1 STEP 0 census (a MEASUREMENT); then W1.3.1's build | pcrec (light census lane) | unblocks W1.3.1 |
| A8 | [TT-4M] (+[TT-4M-TIME]) | per-section timing attribution of `make test`, batched vs unbatched, on Linux | pcrec (executor, heavy) | why 9.5% and not 4.28x; flip HARNESS_BATCH or not |

### A1. [OPT-3] — STEP 3 candidates

State of the row: STEP 1 (measurement) + STEP 2 (premultiplied table, abi 6->7,
1.794x, ahead of PCRE2-JIT on all three bench subjects) shipped. Two STEP 3
candidates are priced and not chartered (D77): (a) the "exact form" — the skip
loop generalised from state 0 to every self-looping state (scan for the run end
with the state's stay-set, transition once), gain ~0.62 x (7.75 - 1.2) ~ 4 c/B on
t-a MINUS one data-dependent exit branch per run (every 2-6 bytes, ~19 c per
mispredict) so a net LOSS on non-periodic text unless predicted; (b) the
two-byte transition table (small machines only, states x ncls^2 <= ~16K entries;
`\w+@\w+\.\w+` 96, IPv4 980, orig 249x18^2 = 80K out of L1). BLOCKER recorded in
the row: the bench's t-a/t-b are PERIODIC (period 26/55), so every branch-cost
figure is flattered. The deciding measurement is "the same instrumented artifact
on a non-periodic 1 MB subject, after STEP 2 lands" — STEP 2 landed 2026-08-26.

**Need**: (1) a non-periodic 1 MB subject with the email alphabet (real failing
prose with sparse addresses; a shuffled-token synthetic is the fallback);
(2) on it, the same-state transition fraction, the run-length distribution, and
ns/B for the shipped premultiplied loop vs hand twins of (a) and (b).
**Owner**: subject = bench (I-10 was never delivered as a usable file); the
measurement = pcrec (scratch tier), because it needs the instrumented artifact.
The pcrec lane can start on a self-generated non-periodic subject; the bench
subject only upgrades the number to pinned tier.

**Lane brief (pcrec) — `opt3s3` (sonnet, measurement only, nothing under `src/`
or `tests/`)**. Read BOILERPLATE first; scope mandate: only
/Users/fdicostanzo/pcrec + your own worktree; pcrec-bench read-only or not at
all. Task: reproduce `opt3_dfa_scan_measurement.md` §2's in-tree `orig` artifact
(pattern text: `tests/codegen/run_premul_table.sh`; subjects t-a/t-b/t-c:
`docs/design/subroutines_measurements/email_specimen/gen_throughput_subjects.py`),
then add three NON-PERIODIC 1 MiB subjects: (i) seeded-PRNG token sampler over
t-a's alphabet with irregular separators and address density matched to t-a;
(ii) the same at t-b's density; (iii) real prose (concatenate `docs/**/*.md`
until 1 MiB, embed addresses at random sparse offsets). Method: the instrumented
scratch copy of the artifact (counter in each loop, as §1 of the memo) gives, per
subject, steps/byte, the fraction of steps whose next state equals the current
state, and the run-length histogram of same-state runs. Then two hand twins of the
shipped artifact (answer-gated: match spans and captures identical to the
unmodified artifact over every subject you use): (a) branch-checked run-end skip
(stay-set scan at self-looping states, bitmap form), (b) two-byte transition table
built for a SMALL machine (`\w+@\w+\.\w+` and the IPv4 pattern from the memo's
size table, since `orig` is out of L1). Box: ubuntubudu via the executor (Ryzen
5 1600, `taskset -c 3`, median of 5, >=1 s per trial, load1 recorded, effective
clock calibrated as in §1); Mac numbers are scratch and must say so. **Result that
decides**: (a) is viable only if its net ns/B beats the shipped loop by more than
the trial IQR on subjects (i)-(iii) — i.e. the same-state fraction stays high
enough that run-end skipping beats one mispredict per 2-6 bytes; (b) is viable
only where the machine is L1-resident and gains more than the IQR. If neither
clears the IQR, refile [OPT-3-RUNEND] as REFUTED-ON-EVIDENCE with the numbers.
Deliver a report at `docs/dev/lanes/opt3s3_report.md`; long timing runs are the
lane's LAST act (DO-THEN-FINISH).

**I-note (bench) — text for pcrecdev2**:

> I-NN — [OPT-3] STEP 3 subject request (small; pool addition). pcrec has never
> received a NON-PERIODIC 1 MiB subject for the email DFA-scan family. t-a/t-b
> are periodic (period 26/55), which flatters every branch-cost figure we can
> take (I-10's confound; your own measurement had it at 1.64x on the DFA loop,
> parity with the JIT on real failing prose vs 0.74x on the periodic subject).
> Ask: (1) the file (or the generator + seed) of the real failing-prose subject
> you used for that measurement, with sha256 and size; (2) if it has a known
> match structure (count of matches, or "no matches"), that number; (3) if you
> would add one non-periodic 1 MiB address-bearing subject to the email
> sub-bench's throughput set, say so — we would time `orig` `auto` on it at pin
> `<PIN>` (cell: email `orig`, large-subject-throughput, find-all; engines:
> pcrec-auto, pcre2-jit, re2; nothing new to build on your side). The result
> that decides: ns/B on it vs on t-a/t-b tells us whether the periodic subjects
> overstate the DFA loop's win; nothing is being asked to change in the pinned
> tier.

### A2. [OPT-5] — period-k scan edge, construction-time synthesis

State: STEP 0 (mechanism: dependency-chain shape, no count crossover), STEP 1
(scan edge, abi 13: letters 2.71x/3.03x, VM gap 6.00x->2.03x), STEP 2
(start-pinned search elision, abi 16, 175 pinned artifacts, net -311,811 B) all
shipped and battery-proven. Un-built, named candidates: STEP 2 candidate =
PERIOD-k scan edge (`(?:ab){1,100}`; the {m,n} split, cap refinement and batch
refinement all designed in the row's prose) — D77 trigger "a measured counted-
string-repeat cell (the bench's nest family is the candidate instrument)";
STEP 3 candidate = CONSTRUCTION-TIME scan-edge synthesis (no independent trigger
beyond the period-k need being established; would make `[a-z]{0,65535}` compile
trivially); RESIDUAL = multi-edge reverse-pass elision (matures with STEP 3);
follow-up = higher minimum-chain floor (I-32 (iv), three loglines patterns with
chains of 2-4 pay x1.03-1.09 with no win possible).

**Need**: (1) POPULATION — how many corpus/bench-export patterns carry a counted
repeat over a multi-character literal or period-k group (`(?:ab){m,n}`), and how
many are DFA-route; (2) TIMING — a hand twin of the period-k floor (one
constant-length compare against the compile-time-expanded m*k-byte string + a
counted loop) vs today's chain on the bench's nest family; (3) the min-chain-
floor measurement (`-fno-scan-edge` on loglines, I-32 (iv)) which is a small
bench read. **Owner**: (1) pcrec, (2) pcrec hand twin + bench cell, (3) bench.

**Lane brief (pcrec) — `opt5pk` (sonnet, measurement only)**. Task: (1) census
over `tests/**/*.rxt` (all `pattern` lines, `scripts/` style as
`docs/dev/optloop/b2ledger/` used) plus `tests/rxtsource/fixtures/bench_*.rxtin`
and `docs/dev/optloop/` stamp data: which patterns contain a counted quantifier
whose body is a non-single-class sequence of singleton bytes (period-k with
singleton classes = a string), by (k, m, n); for each, `RX_ENGINE` and
`RX_DFA_SCAN_EDGE` at the current tip. (2) Hand twin (scratch tier; Linux via
executor for timing) of `(?:ab){10,100}` and `(?:abc){1000,2000}` under the row's
cap rule (block of B copies in an outer loop of q iterations + one r-copy
remainder), answer-gated against the shipped artifact over every startpos on 30
subjects including all-match, all-fail, and off-by-one boundary counts. **Result
that decides**: the population count (zero on corpus AND on every bench-export
pattern the tree holds = the D77 trigger is not met and only a bench cell can
meet it); if non-zero, the twin's ns/B vs the shipped chain at m = 10, 100,
1000; period-k is worth chartering only if it beats the shipped chain by more
than the IQR on a cell the bench also carries. Report
`docs/dev/lanes/opt5pk_report.md`.

**I-note (bench) — text for pcrecdev2**:

> I-NN — [OPT-5] period-k trigger: which `nest`-family cells are counted-STRING
> repeats. pcrec has a designed-but-unbuilt mechanism for `(?:ab){m,n}`-shaped
> patterns (a chain whose per-step classes cycle with period k, singleton bytes =
> a string) and its trigger has waited since 2026-08-31 on "a measured counted-
> string-repeat cell (the nest family is the candidate instrument)". Ask, at pin
> `<PIN>`: (1) list every pattern id in ANY sub-bench whose text is a counted
> repeat of a multi-character literal or of a group whose every element is a
> single byte (regex form `\(\?:[^()]*\)\{\d+,?\d*\}` with singleton members), with
> pattern text and subject regime; (2) for those cells, pcrec-auto vs pcrec
> `--engine=vm` vs pcre2-jit vs the fastest algorithmic engine, ns/B, so we can see
> whether the DFA scan-edge ladder is losing to the VM's counter loop on them;
> (3) separately: loglines with pcrec built `-fno-scan-edge` vs default (I-32
> (iv)), to price a higher minimum chain length. The result that decides: any cell
> in (1) where pcrec-auto is behind by more than its IQR meets the D77 trigger;
> none means the row stays a candidate with no cell.

### A3. [ENG-ABS] — first mechanism (`^` absorption)

State: mechanism 2 (unwrapped forward anchored DFA) merged `dfd112b`, abi 10,
battery-proven, 1.031x/1.036x vs VM, 0.482x on short emails. Mechanism 1
(`^` absorption into ENG_UNANCH; the DD-7 half) never opened, gated on
[BENCH-1]'s `^`-on-some-branches witness. Finding 0.1/0.2: the gate is met; what
remains is [OPT-ATTEMPT-SPLIT]'s own owed precondition and the size decision.
Two constructions target the same slow shape and must be compared before either
is built: (i) [OPT-ATTEMPT-SPLIT] (ratified, batch 2 or later): one attempt of the
original machine at `search_from`, then ENG_UNANCH built from the pattern with the
anchored branches removed — up to 2x table bytes (cycle-1 M5.b measured the sum
537,078 B for the one witness); (ii) this row's absorb-`^` (the reverse machine
gains a position-dependent BOT variant) — smaller in principle, an engine change.

**Need**: (1) the ATTEMPT-SPLIT PRECONDITION census — the shipped corpus's own
`ENG_ATTEMPT`-with-`start_max = subject_length` population (D81's 2026-08-25
census counted 180 of 995 DFA artifacts on the attempt scan and did NOT split by
start_max) and the same over the capability stamp data; (2) a size/speed bound for
(ii) on the witness (a hand twin or an estimate from the reverse-machine state
count); (3) any second bench cell with `^` in some branches. **Owner**: (1),(2)
pcrec (compile-only; Mac is fine, no timing); (3) bench.

**Lane brief (pcrec) — `attemptcensus` (sonnet, measurement only, no timing)**.
Task: compile every corpus `pattern` line (byte and `-e utf8`, default axes,
`--features all`) and read `RX_ENGINE`, `RX_DFA_SCAN`, `RX_DFA_PREFILTER`,
`RX_DFA_TABLE`, `RX_DFA_SCAN_EDGE`, and the emitted `start_max` (`grep -m1 'const
size_t start_max'`). Report: (a) patterns with `RX_DFA_SCAN` `attempt` split by
start_max = 0 (fully anchored, free) vs start_max != 0 (the slow shape); (b) for the
slow-shape set, the artifact bytes (`.c` and `.o -O2`), state counts, and whether
`--engine=vm` is available (the VM alternative for the same cell); (c) for each
slow-shape pattern, the pattern with its `^`-arms deleted (script it: split
top-level alternation, drop arms whose first element is `^`) compiled the same way
so the summed size = the ATTEMPT-SPLIT price on the whole population (the M5.b
method, `cycle1_analysis.md` lines ~1049-1075, scaled from one pattern to all).
Method note: same `-o` basename on both sides when byte-diffing; never grep an
emitted comment for a fact (use the stamps). **Result that decides**: if the
slow-shape population is <= the concat-sqli witness plus a handful, and the size
sum is >= 1.5x on it, the row becomes a `--tune` position candidate only (D119 item
4) and (ii) is declined as not worth an engine change; if the population is larger
(> ~2% of DFA artifacts) the panel-eligible design (split vs absorb) is
chartered. Report `docs/dev/lanes/attemptcensus_report.md`.

**I-note (bench) — text for pcrecdev2** (small):

> I-NN — `^` inside an alternation branch (or any `^` not at the pattern's top
> level). pcrec routes any pattern containing `^` to its per-start-position
> attempt shape, which loses the prefilter, premultiplied table and scan edge; the
> one capability cell we know is `wild-waf-crs-942360-concat-sqli` (thr 5.41x,
> srch 1.53x vs re2-longest). Ask, at pin `<PIN>`: list every pattern id in ANY
> sub-bench (capability, syntax, utf8, loglines, bounded, altwide, email, others)
> whose text contains `^` inside an alternation branch or inside a group that is
> not the whole pattern, with the sub-bench, regime, and pcrec-auto vs the fastest
> algorithmic engine ratio for each. No new build on your side. The result that
> decides: a second losing cell outside the WAF family raises the row's weight in
> the next cycle's ranking; none leaves it a single-witness size-dial candidate.

### A4. [ENG-ISL] — the STEP 2 shapes

State: study `[ENG-ISL.S0]` (2026-09-03, up to 120x on w-2048, zero mismatches
over 25.7M positions) and STEP 1 (VM alternation island, `cee7c741`, abi 18, panel
r53, 27,256 answer cells) shipped; `[CC-DIFF]` STEP 2 and `[OPT-DIAL]` (its owed
items) shipped (finding 0.6). Remaining: two named STEP 2 shapes (the
`ab[cd]|abx` tail form; class-member expansion), and the bidirectional
"islands of VM in DFA" framing (M4.6's strength-1 emitter, gated on capture-free
VM fallback fragments being hot). cycle 1 scores the mechanism at 0 on
capability@0.1 ("not in this matrix, not refuted").

**Need**: (1) POPULATION — how many corpus/bench-export alternations decline the
island only because of a class-tail or class-member (`scripts/alt_census.py`, the
isl1 census: 429 of 1,003 corpus alternations qualify; count the decliners by
decline reason); (2) a bench CELL where serial alternation-try cost loses
(altwide `w`/`srt`/`pfx3` are literal words and already island-served, so a
class-tail cell would be new); (3) the OPTLOOP score (analysis, held). **Owner**:
(1) pcrec, (2) bench.

**Lane brief (pcrec) — `islcensus` (sonnet, measurement only, Mac OK)**. Task: run
`scripts/alt_census.py` (committed at `scripts/alt_census.py`) over the corpus + `tests/rxtsource/fixtures/bench_altwide_0_2.rxtin`
and bucket every alternation the island declines by decline reason (class-leading
branch, class-tail branch `ab[cd]|abx`, capture/backref/lookaround body, budget,
words<4 with pushes>0), reporting counts and, for the class-tail and class-member
buckets, the artifact `.text` and the chain-vs-island estimate the census already
computes. Also list which decliners are DFA-route at `auto` (the island is a VM
mechanism; DFA-route decliners are not its customers). **Result that decides**: a
class-tail/class-member population under ~1% of VM-route alternations = STEP 2 stays
a candidate with no trigger; a population of real weight (>~5%) plus a bench cell
(A9 Q4) charters STEP 2. Report `docs/dev/lanes/islcensus_report.md`.

**I-note (bench) — text for pcrecdev2**:

> I-NN — alternation with class tails / class members (ENG-ISL STEP 2 shapes).
> pcrec's VM alternation island serves literal-word alternations (your altwide
> `w`/`srt`/`pfx3` families). Two shapes are declined: a class tail
> (`ab[cd]|abx`, `foo[0-9]|bar`) and class-member branches (`[ab]x|[ac]y`).
> Ask, at pin `<PIN>`: any cell, in any sub-bench, whose pattern is a >=8-branch
> alternation with class tails or class members, with pcrec-auto vs pcrec
> `--engine=vm` vs `--engine=dfa` vs the fastest engine. If the bench has none,
> say so; a small altwide-style set (`w`-shaped words with a trailing `[a-z]` /
> `[0-9]` class on each word, widths 64/256/1024) added as a new altwide variant
> would give us the cell. The result that decides: a cell where the VM route loses
> by more than the IQR to the serial-try cost meets the D77 trigger.

### A5. [OPTLOOP] parent — stays started, D125's hold noted

The parent's own text records D125's hold (next cycle HELD until Frank lifts it).
The hold is not a measurement. What cycle 3 needs as INPUT is listed in
`optloop/cycle2_close.md` §4; the measurement halves are bench-side re-reads at
the CURRENT pin, commissioned now so the data exists when the hold lifts:

**I-note (bench) — text for pcrecdev2**:

> I-NN — standing re-measure at pin `<PIN>` (cycle-3 analysis input; nothing
> is being scheduled, the D125 hold on the next cycle stands — this is so the data
> is on the shelf). Please run, on the current main pin, the full arms already
> defined (auto, auto-nocaps, forced-vm caps, and where they exist forced-dfa /
> forced-vm-nocaps; see Q2/Q3 in the syntax-roster questions below) for:
> capability@0.1 (re-read of O-62's standing losses: trim-nested-star, evil-alt-
> nested, aws-access-key-id ...), utf8@0.1 (the [B104] re-measure; attributes the
> 12 unattributed large-subject losses against the current tree), syntax@0.1, and
> the loglines/bounded/altwide/email sub-benches once each. Report in the usual
> ledger form with pcrec's stamps per row. The result that decides: it is the cycle-
> 3 ranking's input table; nothing decided by it now.

Also filed in the candidate list: `[CAPS-VIEW-RERENDER]` (rendering task, no
measurement), `[CAPTURES-DFA-MB]` (M-B at larger subject sizes) — see A9 Q5.

### A6. [DD-13] parent

No measurement. Frank's park: "not before [REL-1]" (discharged, `v0.1.0-beta`
2026-09-22), "the bench matrix ranks it against everything else" — bench-side
ranking is not a measurement pcrec can take. `format_design.md` says "after W23
the format has no designed-but-unbuilt production a real consumer is waiting on";
what remains is W1.3.1 (A7), `(?&site.group)` (free, measured, unbuilt), W1.4
(grouplist semantics; owes three readers an answer, w1_impl §9), the `gap` member
(unearned), and [V-E]'s multi-pattern unit. **Retagged completed; W1.4 refiled as
its own not-started row with the consumer-trigger written in.** Bench-side: Q9.

### A7. [DD-13b.W1.3] and its gate [PFX-1] STEP 0

W1.3 is MERGED (`8d68ddc2`, abi 20, `make test` 33/33, test-axes 21 axes 0
mismatches). Exactly one item was carved out: W1.3.1 (the run.sh composed-block
path; 4 sites in `flush_block`'s tail assume the `rx` prefix; Frank ruled OPTION 1
on 2026-09-04 and said "build it AFTER [PFX-1] STEP 0 (D96)"). **[PFX-1] STEP 0 is
a measurement, not a build** (finding 0.4); [PFX-1] itself is `not-started`, never
chartered. **Lane brief (pcrec) — `pfx0` (sonnet, no `src/`, Mac OK)**. Task: the
census exactly as the [PFX-1] row states it: (a) pick a representative artifact set
(a VM artifact, a DFA artifact, a hybrid, a composed one — compile with `-p rx` and
`-p zz`), and classify every prefixed identifier in the emitted `.c`/`.h` as
EXPORTED (link-visible or in the `.h`, per `docs/spec/match_api.md`) or INTERNAL;
(b) enumerate every harness/test site that READS an internal prefixed name
(`tests/harness/run.sh` `flush_block`'s tail — the four W1.3.1 sites —, the
`tests/codegen/*` greps, the identity gates' region markers `<p>_L0`/`<p>_accept`,
`tests/mech/sabotages/*` anchors quoting a prefixed name) BY GREP, each with
file:line; (c) the emitted-bytes saving per artifact if the internals took a fixed
spelling (measure by sed on a scratch copy, then `gcc -c` `.text`/`.rodata` and file
size); (d) the two-header-in-one-TU check the row names (already measured clean
under `-Werror`; record the byte-identity pin on the shared block). **Result that
decides**: the internal-reader list (short = W1.3.1's four sites shrink to the
exported set and the row proceeds; long = an abi event with a wide reader sweep, so
STEP 1 needs its own design) and the bytes-saved figure (the size dial's input).
Report `docs/dev/lanes/pfx0_report.md`. W1.3.1 itself is refiled below and waits
on this report.

### A8. [TT-4M] (+ [TT-4M-TIME])

State: everything chartered is delivered (STEP 1 prototype 4.28x/18.65x isolated;
STEP 2a/2b sizing + design; 2c `HARNESS_BATCH=N` in `run.sh`; 2d timing
`tt4m_time.md`: ~9.5% wall / ~8-10% CPU whole-suite). Frank (2026-09-16): default
NOT flipped; the next step is a per-section timing attribution — "NOT SCHEDULED
— do not charter without Frank's word". D137 item 3 now commissions the
measurement, so this is the lane brief, to be sent when the manager reads D137 as
Frank's word for it. `tt4m_time.md` §206 records why it has never been done:
no per-section timestamps survive in either log. Method needs no `src/` edit:

**Lane brief (pcrec, executor — exact commands for pcrecdev2 on ubuntubudu;
darwin arm optional)** — `tt4mattrib`. Box: ubuntubudu, quiet (bench window
handshake first; one heavy suite at a time); `gnutimeout`, not `timeout`; the
two runs back to back, same tree, same load1 band. Setup in a scratch worktree at
`<PIN>`, `make -j4`. Then

```
S=$(make -pn test 2>/dev/null | sed -n 's/^TEST_SECTIONS := //p')
for arm in unbatched batched; do
  if [ "$arm" = batched ]; then export HARNESS_BATCH=64 PROCS=8
  else unset HARNESS_BATCH; export PROCS=8; fi
  : > build/tt4mattrib_$arm.tsv
  for s in $S; do
    t0=$(date +%s.%N); l0=$(cut -d' ' -f1 /proc/loadavg)
    /usr/bin/time -f "%U %S %M" -o build/tt4m_t.$$ \
       gnutimeout 7200 make $s > build/tt4mattrib_${arm}_$s.log 2>&1; rc=$?
    t1=$(date +%s.%N)
    printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$s" "$rc" \
       "$(echo "$t1 - $t0" | bc)" "$(cat build/tt4m_t.$$)" "$l0" \
       "$(cut -d' ' -f1 /proc/loadavg)" >> build/tt4mattrib_$arm.tsv
  done
done
```

(sections run serially, one `make sN` at a time, so the sum of per-section walls
is the serial baseline `tt4m_time.md` measured at 5124 s on darwin; detach it
`nohup ... & disown`, DO-THEN-FINISH.) Analysis (docs only, after the run):
per-section wall/CPU in both arms; ratio per section; mark each section as
REACHED (calls `tests/harness/run.sh`, per `tt4m_batch_customers.md` Category 1) or
NOT; the sum of (unbatched - batched) over reached sections vs the whole-suite
delta. **Result that decides**: (i) if the saving is confined to the reached
sections and equals the sum of their per-section deltas, the 9.5% is fully
explained by structure (3 of the then-38, now 47, sections reached) and the flip decision is "flip:
the ceiling is the unreached sections' cost, not batching"; (ii) if a reached
section's batched/unbatched ratio is far below the prototype's 4.28x, the win is
being eaten inside it and the report names where (SIZELOG's `-c` caveat, the solo
relink fallback, the routed/perr/H11 exclusions); (iii) either way it names the
sections that dominate wall and are unreached — the next lever. Report
`docs/dev/lanes/tt4mattrib_report.md`.

**I-note (bench)**: none — pcrec-side, and the executor channel is not the bench.
(Bench hold handshake: the run occupies the Linux box for ~2 x 40 min; request a
slot per memory `pcrec-bench-status`.)

### A9. Questions only the bench can answer (for relay; nothing here reverse-
engineers the bench's ledgers — each is asked, not assumed)

1. (OPT-3) Is there a non-periodic real-prose subject in the email sub-bench pool
   (the one behind the "1.64x confound" measurement); if so, path/generator +
   seed + sha256 + match count?
2. (SEL-COST, `sel_cost_census.md` Q1) Could syntax@0.1 add `pcrec-vm-nocaps`(-in)
   testees mirroring the existing caps pair, so a like-for-like nocaps census is
   possible?
3. (SEL-COST Q2) Is a `pcrec-dfa` (-caps/nocaps) forced-DFA testee feasible for
   syntax@0.1, so the reverse population (auto picks VM, a forced DFA would have
   won) can be checked?
4. (SEL-COST Q3) For `lka-pos`/`lka-neg` (identical compile-time stamps, opposite
   large-subject-throughput verdicts): the generated subject's match density
   (fraction of subject bytes covered by a match) for each?
5. (SEL-COST Q4) Do the four `other`-bucket short-subject-search cells near
   1.03x-1.23x (`esc-octal-0` 1.047x especially) sit above the per-launch
   bimodality floor (O-69), or inside it?
6. (ENG-ABS) Every pattern in any sub-bench with `^` inside an alternation branch
   (A3's I-note); and does any cell's pattern text contain a non-top-level `^`?
7. (OPT-5) The `nest`-family cells that are counted-string repeats (A2's I-note);
   loglines under `-fno-scan-edge` (I-32 (iv)).
8. (ENG-ISL) Any >=8-branch alternation with class tails / class members in any
   sub-bench (A4's I-note).
9. (DD-13) Does the bench have a consumer waiting on a DD-13 residual: composed
   delivery (W1.3.1), `(?&site.group)`, or grouplist semantics (W1.4)? Its exporter
   rules were relayed in `w13_report.md` §7; is the exported-set prefix collision
   `floor` still cross-set only?
10. (CAPTURES-DFA-MB) `date-nested-plus`'s `search_short`/`match` subject lookup
    returned no row during M-B's reduction (cycle2_close.md §2 item 6): missing
    data, or a lookup key mismatch? And for the 17 capture-forced hybrid patterns,
    is there a realistic-size match-regime subject (1 KiB - 64 KiB, not the 5-93
    byte hand literals) available, or shall one be added?
11. (OPT-HYB-RESEED-XCALL / CTX-PREFILTER) Does `lka-pos` stay a losing cell after
    `[OPT-HYB-RESEED]`'s landing (abi 49), i.e. the bench's own answer to "x0.62 on
    match-dense prose"?
12. (A5) The re-measure cadence: which pin will the standing re-measure use, and
    what is the window that does not collide with a night blocking window?

## B. The [OPTLOOP] umbrella (D137 item 2)

Method: grepped plan.md for every `[OPT-`, `[ENG-`, `[SEL-`, `[CTX-`, `[TIE-`,
`[WORD-`, `[XART-`, `[EMIT-` row, then every `STATE:not-started`/`started` row in
the file (list read in full, ~100 ids), keeping rows whose purpose is run-time
speed, artifact size, or compile time of the artifact. Left where they are (the
brief's live builds and rows under [OPTLOOP] already): [OPT-LITSCAN] (open),
[CLS-TREE] (started), [UCP] (started), [UTF-VALID] (not-started, feature), the
D135 rung; and already under [OPTLOOP]: [OPT-FIRSTSET], [OPT-ATTEMPT-SPLIT],
[OPT-VMSEED], [CAPS-VIEW-RERENDER], [CAPTURES-DFA-MB].

Considered and NOT moved, each with the reason: [EDGE-STAMP] (an instrument/stamp
row, no speed or size effect), [SIZE-CMT-CLASS] (fixes the size classifier, a
measurement tool), [FORM-CHAR2] (RULED 2026-09-11: SUBSUMED into the [CLS-TREE]
design, i.e. it stays with [CLS-TREE]), [BENCH-CEIL] (a bench arm, not a
mechanism), [MULTI-PAT] (a capability), [ENG-CLAMP]'s compile-tractability half is
a capability but kept (see the list, it opens only on a Frank event),
[AXES-DENY-MASK] (structural), [K50-DD12AI-MANIFEST] (a check).

Moved (pointer added; the row's text is not rewritten): 27 not-started rows plus the 4 closed parked rows, indexed by the
"Candidates for the next cycle (D137)" list under [OPTLOOP] in plan.md.
Close-and-refile (new not-started candidate rows created under that list):
[OPT-3-RUNEND], [OPT-5-PERIODK], [ENG-ABS-CARET], [ENG-ISL-S2].
Close-and-refile outside [OPTLOOP] (their own homes): [DD-13b.W1.3.1] and
[DD-13b.W1.4] (after their parents in the DD-13 block), [TT-4M-ATTRIB] (after
[TT-4M]).

## C. Rows moved/retagged (exact)

Retagged `STATE:started` -> `STATE:completed [CLOSED 2026-09-30 ...]` in place
(precedent [DD-11], [OPT-CLSPACK]; not archived): [OPT-3], [OPT-5], [ENG-ABS],
[ENG-ISL], [DD-13], [DD-13b.W1.3], [TT-4M]. Retagged `not-started` ->
`completed`: [TT-4M-TIME] (stale, finding 0.3). [OPTLOOP] stays `started`, its
first line gains the D137 sentence, the D125 hold text is untouched.

Refiled as new `not-started` rows, under the [OPTLOOP] "Candidates for the next
cycle (D137)" list: [OPT-3-RUNEND], [OPT-5-PERIODK], [ENG-ABS-CARET],
[ENG-ISL-S2]. Refiled at their own homes: [DD-13b.W1.3.1], [DD-13b.W1.4] (after
[DD-13b.W1.3]), [TT-4M-ATTRIB] (after [TT-4M]).

Pointer "(under [OPTLOOP] candidates per D137)" added directly after the STATE tag
of 27 moved not-started rows (nothing else in them edited): [SEL-SIZE],
[SEL-COST], [ENG-TACTICS], [ENG-THIN], [ENG-PGO], [ENG-DIRECT], [ENG-COUNT],
[ENG-CLAMP], [ENG-LOOK], [ENG-CUT], [OPT-A], [OPT-VEDGE], [OPT-NEG], [OPT-ALTHASH],
[OPT-VMLIT], [OPT-SIMD], [SIMD-META], [OPT-B], [OPT-C], [OPT-D], [WORD-FOLD],
[TIE-ALIGN], [CTX-PREFILTER], [XART-TABLES], [EMIT-ALIGN],
[OPT-HYB-RESEED-XCALL], [OPT-ENDWIN-ENC]; each also has one index line in the
list (evidence, need, STATE). The four closed parked rows carry the same pointer
inside their close note. The index lines are deliberately NOT `- [ID] STATE:x`
shaped (`STATE x`, no colon) so the anchored row counts are not double-counted.

Verified by script: every one of the 27 ids has exactly one pointer-bearing row and
exactly one index line.

## D. What is owed / not done

- Nothing sent; the I-notes and briefs above are drafts for the manager. The
  I-numbers, `<PIN>`, and the bench window handshake are the manager's.
- `docs/dev/plan_completed.md`: the seven rows retagged STATE:completed stay
  RESIDENT in plan.md (docs-only brief: plan.md + this report); archiving them is
  the manager's `admin` sweep (precedent: [DD-11], [OPT-CLSPACK] retagged in place
  by lane retag).
- The ph3 reassessment (`ph3_reassessment_2026-09-28.md` #7) is a committed
  document that is wrong on [ENG-ABS]; per the lanes/CLAUDE.md rule ("historical
  once merged; never edited") it is not edited here — this report's finding 0.1 is
  the correction, and the [ENG-ABS-CARET] row cites it.
- The measurement lanes A1-A4, A7, A8 are not launched. Nothing here touches
  `src/`, `tests/`, or `docs/spec/`.
