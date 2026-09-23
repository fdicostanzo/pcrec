# [AXESREC] — reconciling O-47's three unreconciled facts against I-89 block (A)

2026-09-23, lane `axesrec`. Reads `docs/dev/optloop/runs/2026-09-23-i89A-8d716693/axes_full.log`
(the real transcript, fetched by this lane) against `docs/dev/optloop/
linux_ask_i89.md` block (A)'s own EXPECT text and pcrec-bench's O-47
outbox message (`docs/dev/outbox_to_pcrec.md`, the `## O-47` section).

## Verdict, stated first

**All three facts are ONE mechanism: O-47's own "Facts beside your stated
EXPECTs" paragraph mislabels its data.** It attributes each named axis's
sentence to the axis TWO POSITIONS LATER in the per-axis table's own run
order, consistently, throughout the paragraph. The verbatim per-axis
table that the SAME O-47 message also reproduces (and which this lane
confirms byte-for-byte against the raw transcript) is correct and reads
**IDENTICAL to darwin's restricted run and to I-89's own stated EXPECT**
for every axis the ask named. There is no script-version difference, no
box difference, and no real per-axis behavior difference anywhere in this
data. Nothing in `pcrec` needs fixing; the fix is textual, in the bench's
own report and in one paragraph of the (unsent-in-final-form) I-89 draft
that quoted it.

## Method

1. Fetched the real transcript: `scp duxevents@100.69.121.107:/tmp/
   optloop2/axes_full.log` → `docs/dev/optloop/runs/
   2026-09-23-i89A-8d716693/axes_full.log` (491 lines; see that
   directory's README.md for provenance).
2. Extracted every `axes: axis ...`/`axes: --engine=...` announcement line
   and its paired `  agree=N budget-bound=N refused-documented=N (floor F)
   ...` summary line, in transcript order (`grep -n "^axes: axis \|^axes:
   --engine\|^  agree="`).
3. Read `tests/axes/run_axes.sh`'s classification rule (§"THE
   DOCUMENTED-REFUSAL LOOKUP", `run_axes.sh:374-561`): `REFUSAL_PATTERN`
   has entries for exactly `-fno-counter`, `-fprefilter`,
   `--engine=dfa`, `-fno-altcls-merge`, `-fno-size-term`, `--engine=vm`
   (all with a live-verified diagnostic substring); `REFUSAL_FLOOR`
   (`:562-566`) has exactly three entries: `-fno-counter`=180,
   `-fprefilter`=12000, `--engine=dfa`=8000. Every other axis promotes ANY
   `REFUSED` case to a hard failure — so a clean axis's `refused-
   documented` is structurally always 0.
4. Diffed `tests/axes/run_axes.sh` between the O-47 pin (`8d716693`) and
   `main`: `git diff 8d716693 main -- tests/axes/run_axes.sh` — 30
   insertions / 11 deletions, entirely the `[b2fix]` `PCREC_BIT(N)`
   respelling of the bit-derivation regex (widening 31→63 bits for
   `PCREC_NO_REQ_RUN`). **Zero lines touch `REFUSAL_PATTERN`,
   `REFUSAL_FLOOR`, or the per-axis output format.** Ruled out as an
   explanation for any of the three facts.

## The per-axis table, ground truth (verified against the raw log)

Position in the 35-row run order · axis · `agree/budget-bound/refused-
documented (floor)` · transcript line of the summary:

```
25. bit 28 -fno-vm-anchor-bound   24343/0/0      (none)   log:195
26. bit 29 -fno-end-window        24343/0/0      (none)   log:199
27. bit 30 -fno-req-byte          24343/0/0      (none)   log:203
28. --engine=vm                   24274/10/59    (none)   log:237
29. --engine=dfa                  14711/0/9632   (8000)   log:263
```

```
 1. bit 4  -fno-possessify        24343/0/0      (none)   log:21
 2. bit 5  -fno-revdet            24343/0/0      (none)   log:25
 3. bit 6  -fno-counter           24113/0/230    (180)    log:49
 4. bit 7  -fno-length-prune      24298/45/0     (none)   log:74
 5. bit 8  -fno-prefilter         24341/2/0      (none)   log:81
 6. bit 9  -fprefilter            8915/2/15426   (12000)  log:108
 7. bit 10 -fno-altcls-merge      24341/0/2      (none)   log:116
 8. bit 11 -fno-altcls-factor     24343/0/0      (none)   log:121
```

## Fact (1) — bits 28-30

**Claim (O-47):** "bit 29 end-window 24,274 agree + 10 budget-bound + 59
refused-documented; bit 30 req-byte 14,711 agree + 9,632
refused-documented (floor 8000)" vs. darwin's restricted-run 24,343/0/0
for all three.

**Evidence:** the real per-axis lines for bits 28/29/30 (positions
25/26/27 above) are ALL `24343/0/0/0`, matching darwin's restricted run
and I-89's own stated EXPECT (*"separately verified RESTRICTED ...  at
24,343/24,343 agree, 0 mismatches, each"*, `linux_ask_i89.md`, the ¶
right before block (A)'s command) exactly. The numbers O-47's prose
attributes to bit 29/bit 30 are `--engine=vm`'s and `--engine=dfa`'s real
numbers (positions 28/29 — exactly two rows later). `--engine=vm` and
`--engine=dfa` are the family's own separately-documented "ENGINE-
SELECTING pair" (`run_axes.sh:387-389`, tuning.md §2.11); both have
`REFUSAL_PATTERN`/`REFUSAL_FLOOR` entries and are EXPECTED to show a
nonzero population — they are not an anomaly at all, on either box.

**Verdict:** no Linux/darwin divergence exists for bits 28-30. O-47's
prose cited the wrong two rows under the right two names.

## Fact (2) — the four documented exceptions

**Claim (O-47):** "`-fno-length-prune` matches the stated shape (15,426
refused-documented, floor 12,000); `-fno-counter` read 2 BUDGET-bound
(not refused-documented); `-fno-prefilter` read 2 refused-documented;
`-fprefilter` read CLEAN 24,343/0/0 (no refusal/budget population at
all)."

**Evidence:** every one of these four sentences is the DATA belonging to
the axis named at position N+2 (using the table above): `-fno-length-
prune` (pos 4) named but `-fprefilter`'s (pos 6) 15,426/12,000 quoted;
`-fno-counter` (pos 3) named but `-fno-prefilter`'s (pos 5) budget=2
quoted; `-fno-prefilter` (pos 5) named but `-fno-altcls-merge`'s (pos 7)
refused=2 quoted; `-fprefilter` (pos 6) named but `-fno-altcls-factor`'s
(pos 8) clean 24343/0/0 quoted. Read against the CORRECT row for each
named axis, **all four of I-89's own documented-exception shapes hold
exactly**: `-fno-counter` REFUSED-DOCUMENTED 230 (floor 180, matches
`REFUSAL_FLOOR["-fno-counter"]=180`); `-fno-length-prune` BUDGET-bound 45;
`-fno-prefilter` BUDGET-bound 2; `-fprefilter` REFUSED-DOCUMENTED 15,426
(floor 12,000, matches `REFUSAL_FLOOR["-fprefilter"]=12000`) plus
BUDGET-bound 2.

**Verdict:** `-fprefilter` is NOT clean on Linux — the "CLEAN" reading in
O-47 is `-fno-altcls-factor`'s data under `-fprefilter`'s name. Every one
of I-89's four documented exceptions is reproduced on Linux exactly as
stated, once read off the correct row.

## Fact (3) — `-fno-possessify`

**Claim (O-47):** "`-fno-possessify` (bit 4) read 230 refused-documented
(floor 180), an exception population your I-89 list did not name."

**Evidence:** position 1 (`-fno-possessify`, bit 4) reads `24343/0/0/0`
CLEAN in the raw log (`log:21`) — there is no `REFUSAL_PATTERN` or
`REFUSAL_FLOOR` entry for `-fno-possessify` anywhere in
`tests/axes/run_axes.sh`, so a real 230-row exception population at this
axis is structurally impossible without the run FAILING (any undocumented
`REFUSED` case is promoted to a hard failure, and O-47 itself reports
zero `*** [` lines). The 230/floor-180 figure belongs to position 3
(`-fno-counter`, bit 6, `log:49`) — `-fno-counter` IS one of I-89's four
named exceptions, and 230/floor-180 is exactly its number, cited a second
time under `-fno-possessify`'s name.

**Verdict:** there is no new, undocumented exception population at
`-fno-possessify`. It is `-fno-counter`'s already-documented exception,
mislabeled.

## Root cause (evidence-backed, not asserted as certain)

The offset is a clean, constant **+2 rows** for every one of the seven
sentences above — never +1, +3, or variable — which rules out
coincidence. A plausible mechanical cause is visible in the transcript
itself: two PROSE sentences at `log:15-16`, both beginning `axes:
--tune=-1 (size) is NOT declared vacuous...` and `axes: --tune=2
(max-speed) is DECLARED VACUOUS...`, sit between the baseline line and
the first real per-axis announcement (`log:19`, `-fno-possessify`). Both
start with the literal substring `axes: --tune=`, textually
indistinguishable at a glance (or to a naive `grep "^axes: --"` /
`grep "^axes:"`-style extraction) from the real per-axis announcement
lines (`axes: axis --tune=-2 (min-size, ...)`, `log:274` onward). A
listing built by counting EVERY `axes:` line matching that shape — rather
than only lines containing the literal `axis ` token `run_axes.sh`
itself always emits — would insert these two non-axis sentences as two
phantom entries ahead of the real per-axis list, shifting every
subsequently-read NAME two positions behind the DATA it was paired with.
This is offered as the likely mechanism, not verified against whatever
tool or manual process actually produced O-47's prose paragraph (out of
scope: that process lives in pcrec-bench, read-only to this lane).

## What does NOT need reconciling

`--engine=vm`'s real population (24,274/10/59) and `--engine=dfa`'s
(14,711/9,632, floor 8000) are both real, both documented in
`run_axes.sh`'s own `REFUSAL_PATTERN` comments (K55 for `--engine=vm`'s
`\P{Unknown}` witness; K45/[axtriage]'s four accumulated shapes for
`--engine=dfa`), and were never claimed clean by anything — I-89's own
text asks the executor to "report" these two rather than stating an
EXPECT for their exact counts, since they are the family's own documented
"engine-selecting pair" with no restricted-run precedent to compare
against. Nothing about them is anomalous.

## Disposition

- No `src/`, `tests/`, or `docs/spec/` change — the mechanism under test
  answered identically on both boxes for every axis I-89 asked about.
- Annotated `linux_ask_i89.md` in place (dated correction note, history
  preserved per the file's "it is a sent ask" rule).
- This memo is the citable record; O-47 itself is pcrec-bench's and is
  read-only to this lane (per the scope mandate) — its own correction, if
  any, is pcrec-bench's call.
