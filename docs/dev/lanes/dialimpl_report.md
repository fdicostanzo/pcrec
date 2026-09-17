# [OPT-DIAL] THE IMPLEMENTATION — lane `dialimpl`, 2026-09-16/17

Branch `lane/dialimpl`. Built from `docs/design/opt_dial_design.md` REVISION 3
(D103's governance revision) with its §9 item 2 table as the ratified contract.

**Read §1 first.** It is the one thing in this delivery that is not an
implementation detail: the ratified `−2` cell VIOLATES the design's own
eligibility gate, the check the design chartered found it on its first run,
and the disposition is Frank's rather than a lane's.

---

## 1. THE FINDING — the ratified `−2` cell moves the refusal set (K59)

**`--tune=min-size` compiles a pattern the other four positions refuse.**

```
$ build/pcrec -e utf8 --features unicode-props -o OUT.c '[^\p{C}\p{M}\p{P}]'
pcrec: pattern too large: 1027195 bytes of emitted C source (limit 1000000, …)

$ build/pcrec --tune=min-size -e utf8 --features unicode-props -o OUT.c '[^\p{C}\p{M}\p{P}]'
$                                          # compiles, 616,523 bytes
```

`balanced` / `size` / `speed` / `max-speed` all refuse at 1,027,191-1,027,195
bytes against `PCREC_MAX_EMIT_BYTES` = 1,000,000; `min-size` compiles.

**Design §6.2's rule is one sentence and this breaks it**: *no dial position
may select a switch value that moves the refusal set, in either direction.* A
pattern that gains an answer is as much a break as one that loses it, because
"refused" is an answer a caller can observe and because a dial whose positions
accept different LANGUAGES is not a tuning knob.

**THE CAUSE IS `-fno-premul-table`'s UNCONDITIONAL DENIAL AT `−2`, AND IT IS
INDEPENDENT OF THE DIAL** — the bare flag alone does the same thing, at the
identical 616,523 bytes. The dial did not create the lever; it made a position
pull it.

**WHY THE RATIFIED TABLE DID NOT CATCH IT.** §3.1 gate 2 is asked of three
rows and answered: `-fno-altcls-merge` fails it (K45) and is flat, `--engine`
fails it (D44.6) and is flat, `-fno-anchored-dfa` passes ONLY because
`[K53-SELRETRY]`'s drop ladder already drops the optional machine on a
size-cap refusal — which §3.3 records as a DEPENDENCY rather than a property.
**Gate 2 was never asked of `-fno-premul-table` at all.** That row's citation
argues `y`, `x₂` and `φ_scan`, which are the size and time gates; the refusal
gate is simply absent from it. The premultiplied table is a `.rodata` cost
counting toward `PCREC_MAX_EMIT_BYTES` exactly as the anchored machine's bytes
do — the same hazard, and only one of the two rows was examined.

**The general shape, which is worth more than the cell**: *any size lever large
enough to matter can rescue a pattern the caps refuse, so gate 2 is a question
every size-side cell must be asked, not one that a few rows happen to raise.*
§3.3 applies the gate three times out of a possible five.

**THREE DISPOSITIONS, all of them Frank's** (the cell is his ratified ruling,
so this lane FILED rather than narrowed it — k49fix's precedent):

1. **Narrow the cell** — drop `-fno-premul-table` from `−2`, leaving
   `min-size` with the two ladder parameters and costing the column its
   largest measured saving (`σ` = 22-25%).
2. **Give it `-fno-anchored-dfa`'s treatment** — admit it as a DEPENDENCY on a
   drop-ladder rung that does not exist yet. `[K53-SELRETRY]`'s ladder has ONE
   rung; the general form covers a premultiplied table exactly, and this would
   be its second customer and therefore the second sample `utf8k53_report.md`
   §1.2 says a second rung has been waiting for. **This is the disposition I
   would recommend**: it closes the hazard by mechanism rather than by
   subtraction, and it discharges a named D77 trigger the tree already owes.
3. **Amend §6.2's rule** to permit the gaining direction. The design
   considered and rejected this; re-opening it is a ruling against a stated
   position rather than a gap.

**POPULATION: ZERO on the shipped corpus.** `tests/axes`' DIAL-S3 arm measures
0 gained / 0 lost across all five positions on every slice run so far. The
witness is constructed — which is exactly why the design bought the synthetic
near-cap family (§6.2a, the r53 precedent that *synthetic ladders are corpus
members*). **With no synthetic F3 this hazard had no witness anywhere in the
tree and would have shipped unobserved.**

Filed as `docs/dev/known_issues.md` **K59**. Detected permanently by
`tests/codegen/run_tune_dial.sh` §6 and `tests/size/tune_dial_fixtures.rxtin`'s
F3, both of which assert TODAY'S SHAPE so they go red the day any disposition
lands, in whichever direction.

---

## 2. WHAT SHIPPED

### 2.1 The option and the table

`pcrec_options.tune`, an ordinal in −2..+2 appended to the struct. `--tune=N`
takes the ordinal or one of five aliases on equal terms; the `=` form is
REQUIRED for a negative value (`--tune -2` is refused BY NAME rather than
accepted by look-ahead, because a look-ahead that guessed would make
`--tune -o out.c` mean something nobody typed); out of range is REFUSED, never
clamped.

`src/core/tune.c` is the PINNED TABLE's one home. The five rows are §9 item
2's ratified table exactly:

| pos | token | ladder bar | ladder threshold | entry-chain term | denies |
|---|---|---|---|---|---|
| −2 | `min-size` | 95 | 40,000 | — | `-fno-premul-table` |
| −1 | `size` | 85 | 80,000 | — | — |
| 0 | `balanced` | — | — | — | — |
| +1 | `speed` | — | — | 8,192 | — |
| +2 | `max-speed` | — | — | 8,192 | — |

**THE EM-DASH SENTINEL IS 0 AND EACH SITE RESOLVES IT AGAINST ITS OWN
DEFAULT**, which is the choice worth knowing: the defaults stay where they
already lived (`PCREC_SIZE_TERM_THRESHOLD` in `limits.def`,
`VM_INLINE_CHAIN_MAX_BYTES` in `emit_vm.c`'s own home, the materiality bar
beside `size_term_choose`), so this file adds a dial without becoming a second
home for any of them.

**WHICH MAKES POSITION 0 A STRUCTURAL NO-OP BY CONSTRUCTION**: every cell of
the `balanced` row is the sentinel and its deny mask is empty, so there is no
code path on which a `balanced` artifact can differ from a no-flag one.
MEASURED byte-identical on seven witnesses; `--tune=balanced` likewise.

`+2` ships DECLARED VACUOUS (identical to `+1` on every cell) with its
become-reachable condition recorded in three places — the table's own comment,
the spec, and the axes arm's printed output: the day either λ lands
(`[CLS-TREE]`) or the speed floor `s` is ruled below 1.03.

### 2.2 The `tune` config directive

A CONFIG-scope schema row, parsed and validated by the ONE parser
(`src/core/tune.c`) in both legs rather than by a second list of five tokens.
`--list-source` gains **column 20**, APPENDED, so every positional reader of
columns 1-19 survives.

**PRECEDENCE: THE FILE WINS**, per Frank's D93 addendum — the general rule
unchanged, with a loud non-fatal diagnostic naming both sources and both
values, in `--engine`'s wording shape with the OPPOSITE winner. Verified live
in all three directions (conflict reports and the file wins; agreement is
silent; a bad value is refused by name, class `value-shape`). No
`--force-tune`.

### 2.3 The stamp and the abi event

`<PREFIX>_TUNE`, a closed five-token string, UNCONDITIONAL on every artifact of
both engines, in the shared prologue. No `rx_info` mirror and no
`pcrec_options.flags` bit — both are recorded decisions (§5.2), not gaps.

**abi 25 → 26**, the D76/D94 ritual as TWO SEARCHES. Search 1 (readers of the
NUMBER) found three sites, all updated: `run_codegen_tests.sh`'s `ABI_EXPECT`
plus its bump narration, `match_api.md`'s two sentences plus its history, and
`run_recursion_identity.sh`'s (B) FILEPIN, re-pinned to this lane's last `src`
commit. Search 2 (the D94-addendum class — manifests whose rows cite no abi
digit but whose byte VALUES move) found `m5_stage1_stamps.tsv`.

**THE MANIFEST CARRIES TWELVE `EMITTED_BYTES` ROWS, NOT THE TEN THE DESIGN'S
§5.3a NAMES BY NAME** — `(?<=foo)bar` and `(a(?1)?b)` are the two the design's
own list missed. All twelve moved by **exactly +27 bytes**, the computed stamp
line at the default prefix and token, so the re-record is a POSITIVE
ASSERTION rather than a re-baseline.

`check_size_tripwire.sh` needs NO edit and the reason is measured rather than
assumed: `MAX_SIZE_BYTES` (1,400,000) sits far above the log's own max
(651,344 → 651,371 B) and above the tree's largest artifact
(1,336,143 → 1,336,170 B, ~64,000 B of headroom).

**THE NAMED REAL WITNESS MOVED +31 BYTES, NOT 27**, and the difference is the
design's own instruction working: `tests/utf8/axis12_scripts.rxt:296` goes
999,925 → **999,956** bytes, leaving **44 bytes** of headroom under
`PCREC_MAX_EMIT_BYTES`. The extra four bytes are its longer target prefix,
which is precisely why §5.3a says to compute the delta PER READER rather than
once.

---

## 3. THE CHECKS

| id | where | what | state |
|---|---|---|---|
| DIAL-S1 | `run_tune_dial.sh` §1 | stamp well-formedness, closed set, token matches the position, BOTH spellings | 10 cells green |
| — | §2 | position 0 byte-identical to no flag, 7 witnesses + the alias | green |
| DIAL-S2 | §3 | the MECHANISM-STATE CROSS-CHECK, 3 recoveries × 5 positions | green |
| DIAL-S6 | §4 | nesting, with its own non-vacuity guard | green |
| — | §5 | §6.1b's ladder population, `−2` reaches strictly more | green (0 → 2 over an 8-member family) |
| — | §6 | K59 asserted as measured | green (asserts the violation) |
| DIAL-S3 | `tests/axes/run_axes.sh` | the refusal set as a SET of `file:line` keys, BOTH directions, five positions | green on slices; full sweep OWED |
| DIAL-S4 | `tests/size/tune_dial_fixtures.rxtin` | F1/F2/F3 + the named real witness | F1/F2 green, **F3 is K59** |
| DIAL-S5 | `run_size_term.sh` | the ladder's acceptance at `−2`'s threshold | see §5, OWED |

**The cross-check's two sides come from as far apart as they can be made to.**
The RECOVERED side is emitted matcher TEXT — the step accessor's own subscript
expression, the `always_inline` attributes on the entry chain, the ladder's
selected K — never a stamp and never `src/core/tune.c`. The EXPECTED side is
parsed out of `docs/spec/tuning.md` §5.4's table, THE CONTRACT. A check reading
the compiler's own table would compare the implementation to itself, and this
design has already been bitten by exactly that shape once.

**Validated in three failing directions** (planted in the policy table, rebuilt,
run, reverted; clean baseline 17/0):

| plant | result | what it shows |
|---|---|---|
| SWAP adjacent position columns (S249) | **9/8** | §3a red in BOTH directions at once; §1 and §2 stay GREEN — the check LOCALISING, not going uniformly red |
| WRONG DENY BIT at one position (S250) | **11/5** | two cells wrong in opposite directions, so a COUNTING arm would pass; §3a identifies |
| DROP one ladder parameter (S251) | **14/2** | the narrowest, and why §3.5's fold needs its own row |

S249 was then re-run through the REAL mech driver and scores
`tunedial:8fail/9pass`, `reach:ok(4/4)`, **DETECTED** — the same numbers the
hand-plant measured.

### 3.1 A defect the validation found in the check's own failure messages

Under plants 2 and 3, two arms went red with messages saying the arm was
VACUOUS and the WITNESS should be re-chosen — while the witness was perfectly
good and the TABLE was the thing that was wrong.

*A check's failure message is a SECOND, UNDECLARED CLAIM about the space of
causes, and it goes stale independently of the assertion it accompanies.* That
is `w23impl_report.md`'s own generalisation met from the other side: there a
stale message named a TAB as the only possible cause of a field-count failure;
here a fresh message named the witness as the only possible cause of a
non-discriminating arm. Both messages now name BOTH causes and say which other
arm discriminates between them.

### 3.2 A finding about the mech arm shape, and it is PRE-EXISTING

The first S249 run scored **DETECTED with `tunedial:ERRfail/?pass`** — a FALSE
detected. The suite script was uncommitted, so `git archive HEAD` produced a
tree without it, the arm's `bash "$tree/.../run_tune_dial.sh"` found nothing,
and the verdict came from `[ "${f:-1}" -gt 0 ]` defaulting a MISSING count to
1.

**Every existing arm has that shape** (`searchpinned`, `vmframeless`,
`sizeterm`, …): a suite whose script is missing, unbuildable or dying before
it prints its trailer reads as DETECTED rather than as ANOMALY. Not this
lane's to fix and not fixed here — flagged because the day a suite script is
renamed, every row on its arm goes on scoring DETECTED while certifying
nothing, which is [MECH-REACH]'s failure one level up in the harness. The
distinguishing evidence is already printed (`ERRfail/?pass`) and nothing reads
it.

---

## 4. THE SPEC (D80)

`tuning.md` §1 gains the profile concept and the NARROWED property — Frank's
ruled option (3): *explicit per-switch flags beat the dial WHERE A SPELLING
EXISTS* — with the five cells that have no spelling named (three deny-only
bits with no force twin, two ladder parameters with no CLI spelling at all).
A new §5 is THE CONTRACT: the five positions, both spellings, the full 27-row
table, §3.0's σ/m conventions, the seven reason codes, the stamp's token set,
and the D93 precedence rule. All twenty-three §2 entries gain a policy line.
`cli.md` gains `--tune=N` and the sentence that `tune` is NOT a second
file-wins exception. `limits.md` makes the two knees dial-dependent and records
§6.2b's gap (a `+2`-induced overflow has no drop-ladder rung; the trigger is F2
going red). `rxt_format.md` gains the directive and column 20.

`limits_check.sh` green (22/22) before and after.

---

## 5. WHAT IS OWED

| item | exact command / trigger |
|---|---|
| **FULL `make test`** | launched at delivery; log path in the handback |
| **the full axes sweep** | `AXES="--tune" bash tests/axes/run_axes.sh` — ~12 min, background + poll. The four arms and DIAL-S3 are slice-verified only (3 slices, 0 mismatches, 0 gained, 0 lost) |
| **S250 / S251 through the mech driver** | `bash tests/mech/run_sabotage_matrix.sh S250` (and S251). Both hand-verified (11/5, 14/2); S249 is confirmed DETECTED through the real driver and the other two are the same shape |
| **DIAL-S5, the ladder's own acceptance at `−2`'s threshold** | `run_size_term.sh` re-run per position. §6.1b's population is 167 patterns against 86 — **81 shapes the ladder has never run on** — and the two things to watch are §7b's zero-inhabitant pin (which may go red for a LEGITIMATE reason: lowering the threshold is precisely an "inhabitant appears" event) and the trial/abort machinery, whose sufficiency argument is structural and unmeasured at this population. `run_tune_dial.sh` §5 asserts the DIRECTION of the population move; it does not run the ladder's own arms |
| **F2's mechanism is not exercised** | the F2 witness's VM program (~499 KB) is far past even the raised 8,192-byte term, so it pins the CAP but not the mechanism §6.2b names. A witness combining a term-straddling program with a near-cap artifact was not constructed |
| **`run_inline_capability.sh`** | PRE-EXISTING red, see §5.1 — not this lane's, A/B'd against the branch point |
| **the end-to-end dial measurement** | nobody has built one artifact at `−2` and at `0` and compared them (design §6.3). Every rate in the table is a per-switch measurement from its own ledger, and the composition of individually correct rates can still be wrong |
| **`-fno-anchored-dfa`'s owed A/B** | `rx_match` default against `-fno-anchored-dfa` on `opt2`'s own 85 subjects. Cheap, and the single owed measurement most likely to move a cell |

**NOT OWED, and named so nobody goes looking**: the λ row (`[CLS-TREE]` is
unbuilt, so that column is a reservation), and the two disclosed dependencies
the ladder rows rest on (the declared-capacity floor, `[K53-SELRETRY]`'s drop
ladder) — no check here would notice either being narrowed, which §6.3 already
says.

---

## 5.1 A PRE-EXISTING RED, A/B'd rather than assumed

`make test-codegen` is **7/8** at this delivery, and the one red is
**`run_inline_capability.sh`**, [CC-DIFF] STEP 2's capability probe:

```
FAIL: nm could not read arm_a.o (no rx_search symbol) — no verdict is evidence here
```

**IT IS NOT THIS LANE'S.** A/B'd the way `BOILERPLATE.md` asks — a scratch
`git archive` of this branch's own base commit (`5b79927d`), built with the
same `CC=gcc-16`, running the same script — and it **fails identically
there**. The probe is red on main.

Two things that make the attribution safe rather than merely convenient. The
dial cannot reach this at all: position `balanced` is a structural no-op and
the probe drives `--engine=vm --vm-entry-shape=4` explicitly, so the only
byte of the artifact this lane moves is the `RX_TUNE` stamp line. And the
symbol the probe says is missing IS PRESENT — compiling the probe's own
witness by hand (`\d{1,16}`, same flags, `gcc-16 -O2 -c`) and running `nm`
finds `_rx_search` along with every sibling entry, so the failure is inside
the script's own arm rather than in the emitted artifact.

The script's own CLAUDE.md entry says it is red on exactly two things, both
failures of the PROBE rather than verdicts — the witness ceasing to be
frameless, and a symbol table that cannot be read — and this is the second.
Triage belongs to whoever owns that probe; it is named here so the merge
battery's `test-codegen` red is not attributed to this lane.

## 6. FINDINGS, collected

1. **K59** — the ratified `−2` cell moves the refusal set (§1). The largest
   item in this delivery.
2. **The design's §5.3a manifest list is short by two.** It names ten
   `EMITTED_BYTES` rows; the file carries twelve.
3. **The named real witness moves +31 bytes, not the design's 23-28.** Its
   prefix is longer than `rx`. The design's own "compute it per reader"
   instruction is what caught it.
4. **A check's failure message is a second, undeclared claim about causes**
   (§3.1), found by this lane's own failing-direction validation.
5. **The mech arm's `${f:-1}` default reads a MISSING suite as DETECTED**
   (§3.2). Pre-existing across every arm.
6. **S192's anchor was staled by this change and is re-anchored**, its intent
   re-verified through the real driver (`sizeterm:3fail/28pass`,
   `corpus:0fail/21pass`, DETECTED). The bar's decline gains no second witness
   from the dial, for two independent reasons: a HIGHER bar is a WEAKER gate,
   so `−1`/`−2` move away from a decline; and cap-rescue additionally needs a
   fixed emit-size cap to force it, which no dial position touches.
