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

## §4 — The other reds in the gate's `test.log`

Scanned the whole surviving log for `FAIL`/`ERROR`/`ANOMALY`/`checks failed:
[1-9]`/`exited [1-9]`.

| line | red | disposition |
|---|---|---|
| 2298 | `FAIL: nm could not read arm_a.o (no rx_search symbol)` (`run_inline_capability.sh`) | STANDING darwin red, `docs/dev/wake.md`; not ours |
| 2430 | `[SEL-1]` population moved to 2 | §3, fixed |
| 1265 | `*** SKIP: libpcre2-8-0 not present` (PC-3) | the documented loud SKIP (root CLAUDE.md); not a red |

No other section had failed at the point the log was read; the gate was
still running.

---

## §5 — Validation

(filled at hand-off — see the handback message for the live numbers)

---

## §6 — Commits

- `36f2a0f9` — D112 class 2: `-fcomments` on the subject-side generators.
- `b9b91bcd` — `[SEL-1]` fallback population re-pinned 1 -> 2.
