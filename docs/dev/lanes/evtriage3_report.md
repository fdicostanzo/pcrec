# evtriage3 — TRIAGE of `tests/codegen/run_recursion_identity.sh` at abi 27

Lane `evtriage3`, branch `lane/evtriage3` from main `f3eb6f82` (abi 27,
emitted comments OFF by default — D112; the (B) file pin re-pinned to
`74c2192c`, the abi-27 merge commit). Opus. 2026-09-19.

The manager's run at the new pin read **7 passed / 11 failed**. This report
dispositions every FAIL line, plus the one non-standing red the concurrent
`make test` gate surfaced in another section.

---

## §0 — THE LESSON THE BRIEF ASKED FOR, AND IT IS SHARPER THAN IT LOOKS

**A known-red script masks every other FAIL in it**, and evtriage2's rubric
labelled this script "red by construction until the manager re-pins (B)".
That label was true and it hid the rest.

But the mechanism here is worse than a reader's attention lapsing, and it is
worth stating in its own right, because no amount of reading every FAIL line
would have recovered what was lost:

> **A check that `continue`s on a filter fault suppresses its own body, so
> every downstream count reads ZERO and every downstream assertion fails as
> a STALENESS claim about a population that was never measured.**

`run_recursion_identity.sh`'s sweep loop tests the D37 stamp count *before*
either comparison and `continue`s when it is wrong (line 1231 at the branch
point). With the stamp filter broken, all 2,535 artifacts skipped the body,
so `same`, `rsame`, `relided`, `rsizeterm`, `risland` and `rfold` all stayed
0 — and the script then reported, in its own voice:

- "only 0 patterns compared identical (floor 700)" — *true, and not a
  measurement*;
- "`SIZE_TERM_REGION_MOVERS` fired on NO axis: the two patterns it names no
  longer move their program region, so the list is stale" — **false, and
  stated as a fact about the emitter**.

Red 2 in the brief is therefore a CASCADE of red 1 and not an independent
finding. It is filed here as class 1-adjacent (`read the STAMP`) rather than
class 3, and the A/B in §2 is what establishes that rather than the
inference.

*Generalisation for the next check-writer*: a filter self-check that
`continue`s is a **fail-closed gate on the whole body**. If its own failure
message does not say "every count below this line is now vacuous", the
counts below it will be read as evidence. The two directions are not
symmetric: a filter fault should be loud about what it *invalidated*, not
only about itself.

---

## §1 — RED 1: the D37 stamp filter — **class 2, the comment IS the
instrument**. FIXED.

### The claim

> `[noprefilter]` / `[nocaptures]`: "the D37 stamp filter matched the wrong
> number of lines on 2535 artifacts — it must remove EXACTLY three" and,
> downstream, "only 0 patterns compared identical (floor 700)".

It fires on **all four axes**, not only the two the manager quoted; the two
named are simply the ones whose messages were read.

### The three lines, measured at both abis

`stamp_strip`/`stamp_count` match:

```
^/\* Feature set: |^#define PCREC_FEATURE_SET |^#define PCREC_FEATURE_MODULES
```

Measured on this lane's build of main `f3eb6f82`:

| build | lines matched |
|---|---|
| `pcrec --features all -p rx -o - -- 'a'` (default) | 2 |
| `pcrec --features all -p rx -fcomments -o - -- 'a'` | 3 |

The first of the three is `/* Feature set: all (modules: ...) */` — **a
comment**. [EMIT-VERB] event 2's default flip removes it, so `stamp_count`
reads 2 on the subject side *and* on the (B) file-pin side (`74c2192c` is
itself abi 27), both sides fail the `-ne 3` test, and the body never runs.

### Which class, and why it is NOT "re-derive the exact count to 2"

Because the script reads comments a **second** time, and that reading is the
gate's whole reason for existing. Its own (A) block says so:

> "NO filtering beyond the three D37 stamp lines, so comment sensitivity
> INSIDE the region is kept in full — the property that caught [M6.6.2] wave
> E's 37-byte prose change on 54 artifacts."

The program region (`goto rx_L0;` .. `rx_accept:`) is full of `vm_rolef`
role text. A default-axis subject emits none of it, while the pre-module
reference `ac4917d` predates the axis entirely and emits it unconditionally.
So a stamp-only filter narrowed to 2 would have left comparison (A)
comparing a comment-free region against a comment-bearing one — **every VM
artifact "differing", the gate red forever, and its most valuable property
silently retired**.

MEASURED (five call-free VM patterns, `--engine=vm`, region compared against
`ac4917d` after the stamp strip):

| pattern | subject default | subject `-fcomments` |
|---|---|---|
| `(ab)+c` | MOVED | SAME |
| `a(b\|c)+d` | MOVED | SAME |
| `(foo)\1` | MOVED | SAME |
| `(?:ab\|cd)*x` | MOVED | MOVED |
| `[a-z]{2,10}` | MOVED | SAME |

The fifth moves for the [ENG-ISL] reason the script's own deny-build excuse
already handles, and is not a counter-example.

### The fix

Every **subject-compiler** generator takes `-fcomments` explicitly, with a
header block saying why (commit `36f2a0f9`):

- `gen_a` (subject), `gen_c` (`$FILEREF` = `74c2192c`, which HAS the flag);
- `gen_noisl`, `gen_nofold`, `gen_denyboth` — the three deny-axis excuse
  builds, because each is compared against `rb`, the pre-module region.

`gen_b` (`$REF` = `ac4917d`) deliberately does **not**: measured, that
compiler answers `pcrec: unknown option '-fcomments'`, and it emits the
comments unconditionally, which is exactly the side that needs no flag.

**The "exactly three" self-check is unchanged** (learnings.md §3: a filter
that stops matching must say so). It now has the axis that makes three lines
exist, rather than a count re-derived down to the new default.

Giving `gen_c` the flag is not incidental: both sides of comparison (B) are
abi-27 compilers, so (B) would have been *internally consistent* at 2 lines
and would have quietly stopped seeing whole-file comment changes. D76's (B)
pin is about emitted scaffolding, and comments are emitted scaffolding.

---

## §2 — RED 2: `[ART-SIZE] SIZE_TERM_REGION_MOVERS fired on NO axis` —
**CASCADE of red 1**. No re-derivation needed. The list is LIVE.

The brief asked whether the check's measurement had gone blind (fix the
measurement) or the region genuinely no longer moves (a finding about size
terms pricing comment bytes). **Neither.** `rsizeterm` is incremented inside
the sweep body that red 1's `continue` skips, so `SIZETERM_TOTAL` was 0 for
a reason with nothing to do with size terms.

### The mandated A/B, run on the two named patterns

Four subject cells against one fixed reference (a scratch `git archive`
build of `ac4917d`, the gate's own (A) pin), region = `goto rx_L0;` ..
`rx_accept:` after the stamp strip:

- **(a)** `4af16eb7` — lane/w4 tip, pre-[EMIT-VERB]
- **(b)** `385f3cab` — emitverb event 1 (flag present, default ON)
- **(c)** main `f3eb6f82`, default
- **(d)** main `f3eb6f82`, `-fcomments`

P1 = `((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,8}(){2,3}){1,2}){2,3}`
P2 = `(?:(?:(?:(?:(?:(?:a|b){41}){41}){41}){41}){41}){41}`

| pattern | axis | (a) preEV | (b) event1 | (c) main dflt | (d) main `-fcomments` |
|---|---|---|---|---|---|
| P1 | default | MOVED | MOVED | MOVED | MOVED |
| P1 | `--engine=vm` | MOVED | MOVED | MOVED | MOVED |
| P1 | `-fno-prefilter` | MOVED | MOVED | MOVED | MOVED |
| P1 | `--no-captures` | both-empty | both-empty | both-empty | both-empty |
| P2 | default | both-empty | both-empty | both-empty | both-empty |
| P2 | `--engine=vm` | MOVED | MOVED | MOVED | MOVED |
| P2 | `-fno-prefilter` | both-empty | both-empty | both-empty | both-empty |
| P2 | `--no-captures` | both-empty | both-empty | both-empty | both-empty |

**Four fires, on every tree, identically** — so `SIZETERM_TOTAL` is expected
to read 4 once red 1 is fixed, and the `--no-captures` arm's own assertion
(`rsizeterm` must be 0 there, because no VM body is emitted) holds by the
same table.

The region's comment-free byte count is visibly smaller at (c) than at (a),
(b) and (d) (P1: 875 lines against 1,137; P2: 95 against 127) — the comment
axis acting, and the only difference the flip makes to this population.

### The open question D112 left

**It is not landed by this evidence, and that is the honest answer.** The
brief's hypothesis was that the size term's decisions might have been driven
by comment bytes before the flip. They were not *here*: the size term picks
the same K on all four trees. The one place a length-based decision *did*
read comment bytes is the emitter's VM entry-shape AUTO rung, which
[EMIT-VERB] already found and fixed by making the gate read
`sb_len_uncut()` (`emitverb_report.md` §3a). This lane found no second
instance and did not go looking beyond its own population — so "should a
size term price comment bytes at all" stays open with its population
unchanged (D77: no build ahead of a measured need).

---

## §3 — RED 3 (not in the brief's list, found in the concurrent gate):
`run_vm_identity.sh` `[SEL-1]` population 1 -> 2. **A CORPUS event, not a
compiler one.** RE-PINNED.

`build/battery_gate_f3eb6f82/test.log:2430`:

```
FAIL: [SEL-1] the --no-captures DFA-cap-overflow fallback population MOVED to 2:
  (1{0,30}?[^]abc][^abc]){28,30}0+|a (dfa overflowed: >32000 states at pattern offset 0)
  (?:ab){0,16000} (dfa overflowed: >32000 states at pattern offset 0)
```

A/B across the same three compilers as §2:

| compiler | `(?:ab){0,16000}` | `(1{0,30}?...){28,30}0+\|a` |
|---|---|---|
| `4af16eb7` (pre-EMIT-VERB) | vm / `dfa overflowed: >32000 states` | vm / same |
| `385f3cab` (event 1) | vm / same | vm / same |
| main `f3eb6f82` | vm / same | vm / same |

Identical on all three, so neither the comment axis nor the abi 27 bump is
implicated. `git log -S` names the cause: **`e021b982` ([ADM71.4], the same
day) added `tests/base/opt41_rung_nullable_decline.rxt`**, whose
`(?:ab){0,16000}` is a nullable counted repeat built to reach exactly this
cap (`PCREC_MAX_DFA_STATES_TABLE`, 32000, `src/core/limits.def:147`). It
joins the population by construction, and the lane that added it owed the
re-pin.

Re-pinned 1 -> 2 with the provenance and the A/B recorded in the check's own
header (commit `b9b91bcd`). Both directions of the assertion are kept: 0 is
still "the witness stopped reaching its site", anything other than 2 is
still a deliberate re-pin event.

---

## §4 — RED 4: `run_resource_tests.sh`'s `[K59-PREMUL]` byte pin, and
## RED 5: `run_cpset_structure.sh` CHECK 3's manifest — **the SAME reader
## class, one merge later**. Both RE-PINNED.

The concurrent gate surfaced two more reds after the ones above, and they
are one story: **the [EMIT-VERB] RIDER (`74c2192c`, emitverb2) put the abi
into the ESSENTIAL generated-by line** — the line every artifact carries
whether or not comments are on — and its own sweep measured the delta as
"movers by exactly 9 bytes each". Two readers of that byte count were not
re-pinned with the rest, because **their text cites a byte count and no abi
digit**, which is exactly what the D76/D94 grep over the abi number cannot
reach. `battriage_report.md`'s SECOND READER CLASS; this is its fourth and
fifth recorded instances.

### RED 4 — `tests/resource/run_resource_tests.sh`, the `a{5,25000}` rescue

```
FAIL: 'a{5,25000}' -fno-scan-edge -fno-start-pinned rescued at 762114 bytes,
      pinned 762105
```

The arithmetic reconciles exactly, measured on scratch builds of each commit
**with this cell's own `-o` basename** (the trap `evtriage2` recorded and
`dd8_report.md` §3.1 named):

| tree | bytes |
|---|---|
| `385f3cab` (event 1) under `-fno-comments` | 762,104 |
| + event 2's own added blank line | 762,105 — the previous pin |
| + the rider's ` (abi 27)` insertion | **762,114** — today |

Confirmed by **diffing the two artifacts**, not inferred from the size: the
only differing lines are the generated-by header (+9), one blank line (+1),
and `.abi = 26` -> `.abi = 27` (same length). `74c2192c` and main `f3eb6f82`
read 762,114 identically. Re-pinned, with the arithmetic in the cell's own
header (commit `a6264d6f`). The `-fcomments` figure quoted in that note
re-measures to 769,844 and was updated with it.

The row's own reasoning survives untouched: the pin is a raw `wc -c` and is
comment-INCLUSIVE, while `PCREC_MAX_EMIT_BYTES` is comment-EXCLUDED, so D112
item 3's guarantee that no comment setting can rescue or refuse a pattern is
still what makes this a pin move rather than a finding.

### RED 5 — `tests/codegen/run_cpset_structure.sh` CHECK 3

```
FAIL: [3] the recorded manifest has drifted from this run.
```

**The message showed 5 drifted rows. There are 12, and all 12 moved by
exactly +9.** The other seven were cut off by the message's own
`diff ... | head -20`: twelve changed rows are 48 diff lines. Both readers
of the battery log — the manager's brief and this lane's first pass —
counted the population from the message and got 5.

That is a finding in its own right, and it is this house's recurring shape
seen from a new side:

> **A check that says "this is a DIFF TO REVIEW" must print the diff it
> wants reviewed.** An evidence window sized for a typical failure silently
> becomes a claim about the SIZE of the drift, and it is read as one.

Measured directly against the manifest, all twelve sampled patterns:

| pattern | recorded | actual | delta |
|---|---|---|---|
| `a` | 21,283 | 21,292 | +9 |
| `abc` | 21,932 | 21,941 | +9 |
| `a(b\|c)+d` | 29,774 | 29,783 | +9 |
| `(a)(b)(c)` | 29,411 | 29,420 | +9 |
| `[a-z]+@[a-z]+` | 25,108 | 25,117 | +9 |
| `^foo$` | 16,421 | 16,430 | +9 |
| `\bword\b` | 25,637 | 25,646 | +9 |
| `(?i)HeLLo` | 27,986 | 27,995 | +9 |
| `cat\|dog\|cow\|calf\|camel` | 26,089 | 26,098 | +9 |
| `(\w+)\s+\1` | 24,914 | 24,923 | +9 |
| `(?<=foo)bar` | 29,759 | 29,768 | +9 |
| `(a(?1)?b)` | 27,967 | 27,976 | +9 |

Re-recorded the way r49 requires — by deleting the file and letting the
check write it, then REVIEWING the diff rather than bumping numbers: **24
changed lines, every one an `EMITTED_BYTES` row, zero other stamps moved**
(no `RX_ENGINE`, no `RX_ENGINE_SEL`, no rung, no prefilter). The window was
widened to `head -200` in the same commit (`541856ef`), sized to hold a
whole-manifest rewrite.

---

## §5 — Sabotage anchors

No sabotage row anchors on any line this lane touched — checked by grep over
`tests/mech/sabotages/` for the generator definitions, `dfafallback`, the
762105 pin, the manifest and the diff line. Two rows name files this lane
edited (`S174` anchors in `src/opt/atomic.c`, `S40` in
`src/opt/select_engine.c`), so neither needed a re-aim.

**`S40` was re-driven SOLO anyway**, because its suite is `vmidentity` — the
script whose `[SEL-1]` pin §3 moved:

```
== mech run COMPLETE: 1 rows (unexpected: 0, undetected: 0, unreached: 0,
   anomalies: 0, oracle-skipped: 0) at 440e2c35 ==
```

DETECTED.

---

## §6 — Validation (COMPLETE)

| what | before | after |
|---|---|---|
| `tests/codegen/run_recursion_identity.sh` | 7 passed / **11 failed** | **16 passed / 0 failed** |
| `tests/codegen/run_vm_identity.sh` | 9 / **1** | **10 / 0** |
| `tests/resource/run_resource_tests.sh` | (1 failed in the gate) | **0 failed, 0 inconclusive, 1 platform skip** |
| `tests/codegen/run_cpset_structure.sh` | 27 / **1** | **28 / 0** |
| `tests/recursion/run_specimen_identity.sh` | — | **13 / 0** |
| `tests/codegen/run_comments_axis.sh` | — | **65 / 0** |
| `make test-codegen` | — | **9/10 scripts**, sole red the standing darwin `nm arm_a.o` probe, reproduced solo |
| `make mech S40` (solo) | — | **DETECTED**, 0 undetected / 0 anomalies |

`run_recursion_identity.sh`'s own per-axis tallies after the fix:

| axis | (B) same / differing / stamp-filter-bad | (A) same / differing / elided / size-term-moved |
|---|---|---|
| default | 2535 / 0 / 0 | 2309 / 0 / 4 / 1 |
| `--engine=vm` | 2536 / 0 / 0 | 2289 / 0 / 0 / 2 |
| `-fno-prefilter` | 2535 / 0 / 0 | 2310 / 0 / 4 / 1 |
| `--no-captures` | 2535 / 0 / 0 | 2333 / 0 / 0 / 0 |
| linkage | 2535 / 0 / 0 (flags-filter-bad 0) | — |

`[ART-SIZE] the size term's named region movers fired (4 across the axes)` —
**the number §2's A/B predicted before the run**, and the `--no-captures`
arm's own "must be 0 here" assertion holds in the same table.

---

## §7 — Commits

- `36f2a0f9` — D112 class 2: `-fcomments` on the subject-side generators of
  `run_recursion_identity.sh`.
- `b9b91bcd` — `run_vm_identity.sh`: `[SEL-1]` fallback population re-pinned
  1 -> 2 (a corpus event, `[ADM71.4]`'s).
- `440e2c35` — this report (draft).
- `a6264d6f` — `run_resource_tests.sh`: the `[K59-PREMUL]` rescue byte pin
  re-pinned 762105 -> 762114.
- `541856ef` — cpset CHECK 3 manifest re-recorded (+9 x 12) and its diff
  window widened.

## §8 — Nothing owed

Every number above is measured on this branch. Not merged; not run: the full
`make test`, which is the manager's at merge.
