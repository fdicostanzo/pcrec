# [D105] — `emit_state_legend`'s silent-degradation path, DELETED

Lane `d105`, 2026-09-18, opus. Branch `lane/d105` off `6c9dac09`.
Built as RE-RULED by Frank 2026-09-18: option (a), via the decision's own
algorithm rider, so the silent degradation is eliminated by construction
rather than announced.

**Status: DELIVERED, MERGED WITH `main`, VALIDATION COMPLETE. Nothing is
owed.**

**POST-MERGE (`050c2b83`): `main` moved to `2e019d20` while this lane ran —
lane `k60fix` landed D109, K60's other class — so `main` was merged in here
and W4 re-pinned from 108 to 0. `make alloc` is now GREEN on all four
witnesses and K60 is closed in both its classes.** §2.1's table and §4 carry
the merged numbers; §8 is the merge's own record.

---

## 1. What landed

Four commits, in order.

| commit | what |
|---|---|
| `6e14d210` | `src/gen/emit_dfa.c` — the restructuring, all three rider points |
| `409277b8` | `tests/core/run_alloc_tests.sh` — a defect found while validating |
| `198fa0ca` | `tests/core/alloc_check.c` — the pins, in their own commit as briefed |
| `58216d3c` | docs: `decisions.md`, `known_issues.md`, `docs/spec/match_api.md`, two `CLAUDE.md`s |

### 1.1 The three rider points

**(1) `path` is a fixed local and the `malloc(maxd + 1)` is deleted.**
The allocation was sized by the deepest BYTE distance, which is unbounded —
a scan edge costs its whole span, so `[a-z]{0,16384}`'s two-state machine
has a state 16,384 bytes deep, which the deleted comment said itself.

*The proof the brief asked for, by line, on this tree.* `path` has exactly
two uses in the function. It is READ at `emit_dfa.c:3728` —
`int b = d->rep[path[k]];` — inside `for (k = 0; k < shown; k++)` at `:3726`,
where `shown` is `len < LEGEND_MAX_EXAMPLE ? len : LEGEND_MAX_EXAMPLE`
(`:3720`). So every read is at an index in `[0, LEGEND_MAX_EXAMPLE)` and
there is no read past index 39 anywhere in the rendering code. It is WRITTEN
at `:3729` in the backtrack, which fills DOWNWARD from `len-1` to 0; the
write is now guarded `if (--k < LEGEND_MAX_EXAMPLE)`. Dropping the stores at
indices ≥ 40 cannot change a byte the renderer shows, because the low indices
the walk keeps do not depend on the high ones it drops — each iteration's
value comes from `via[s]` for the state it is standing on, not from the array.

One incidental hardening, worth recording because it is a behaviour
difference rather than a byte difference: the old code treated a NULL from
`malloc((size_t)d->n * sizeof(int))` as "drop the legend", so on a platform
where `malloc(0)` returns NULL a zero-state machine would have silently
dropped its legend. There is no such platform in play here (both this box
and the reference box return non-NULL), so no emitted byte moves; the new
code has no such path at all.

**(2) The four BFS arrays move to the arena, with the Ctx attached.**
`arena_alloc(&cx->arena, …)`. A NULL block `malloc` inside the arena calls
`ctx_nomem(a->cx)` (`src/core/arena.c:14-24`) and the `longjmp` lands in
`compile_driver`, which frees the arena wholesale — the EXISTING general
mechanism, no new state, no parallel path. The bespoke `free`-and-return arm
and all five `free()` calls are deleted rather than patched, because arena
storage dies with the attempt (coding guide §1.6).

A note on the brief's wording: there is no Job-owned arena in this tree. The
compile's one arena is `Ctx.arena` (`src/core/internal.h:2257`), attached at
`src/core/compile.c:773` before anything allocates from it, and the house
idiom at every other `src/gen/` allocation site is `arena_alloc(&cx->arena,
…)` / `arena_alloc(&v->cx->arena, …)`. That is what this uses.

Plumbing: the function takes a leading `Ctx *cx`, matching
`emit_anchored_entries(Ctx *cx, StrBuf *c, …)` two hundred lines up. Neither
caller needed anything threaded to it — `emit_machine_tables` already holds
`f->cx` (`DfaForm.cx`, `:3923`) and `emit_attempt` already takes `Ctx *cx` as
its first parameter.

**(3) Brief mode allocates `dist` and `queue` only.** `from`/`via` are
neither allocated nor written when `n > LEGEND_MAX_STATES`; the BFS's own
writes to them are guarded by the same flag. The walk's reachability and
distances do not depend on either, and the summary reads neither, so the
emitted text is unchanged. The scratch halves exactly where the machines are
biggest, which is the rider's own argument.

**(4)** The `:3616` comment (*"a legend is never worth failing a compile
over"*) and the header sentence that carried the same policy are replaced by
a statement of what the function now does and a pointer to D105.

### 1.2 The defect found while validating

`alloc_check.c` writes `PASS` to stdout and `FAIL` to stderr;
`run_alloc_tests.sh` piped only stdout into `tee "$OUT"` and then reported
`"alloc_check: $(grep -c '^FAIL' "$OUT") witness(es) misbehaved"`. It was
grepping a pattern that structurally could not appear, so every red run said
**0 witnesses misbehaved** — the branch-point control's true count was four.
Fixed with `2>&1` before the pipe. This is the house's recurring shape
(`w23impl_report.md`, `dialimpl_report.md`): a check's failure MESSAGE is a
second, undeclared claim, and here the claim was a count derived from a
source that could not carry it.

---

## 2. The pins, and why there are two

The check had no per-witness expectation at all: every absorption was a FAIL
and nothing said which absorptions were the standing filed defect. A new one
would have landed in a sea of red, and a fix's landing would have moved a
number nobody compared.

Each `Witness` row now carries `expect_total`, `expect_absorbed_single` and
`expect_absorbed_sustained`, with `absorbed_why` naming the filed defect when
an expectation is non-zero. A mismatch fails in EITHER direction: above the
pin is a regression, below it means the defect moved or was fixed and the pin
is stale — the ratchet that makes a fix re-pin its own witness rather than
quietly turn a red line green.

**`expect_total` is not belt-and-braces, and the control proved it.** "No
absorption" is a claim this check can satisfy by not reaching the compile at
all (K35). W3's SUSTAINED sweep absorbs **zero even against the UNREPAIRED
library** (`k60_measurement.md` §1.2 measured this and the control reproduces
it), so the absorption pin alone reads PASS on that arm and only the
population pin catches the unrepaired tree. The population is also the direct
evidence the legend site is gone: W1 72 → 57 and W3 328 → 303, exactly the
five deleted raw allocations per emitted machine.

### 2.1 Before and after

| witness | | absorbed, single | absorbed, sustained | swept total |
|---|---|---:|---:|---:|
| W1 `[a-z]+` | at `6c9dac09` | 15 | 5 | 72 |
| | at `lane/d105` | **0** | **0** | **57** |
| W2 `[a-z]{2,10}` vm | at `6c9dac09` | 0 | 0 | 11 |
| | at `lane/d105` | 0 | 0 | 11 |
| W3 `\p{L}` utf8 | at `6c9dac09` | 25 | 0 | 328 |
| | at `lane/d105` | **0** | **0** | **303** |
| W4 ladder | at `6c9dac09` | 108 | 0 | 158 |
| | at `lane/d105` | 108 | 0 | 158 |

W1 and W3 are the pure legend class and every one of their absorptions is
gone. W4 is the LADDER class — `src/core/compile.c`, lane `k60fix`'s, not
touched here — and read 108 on this lane's pre-merge branch exactly as the
brief predicted. The two halves are disjoint by construction, which
`k60_measurement.md` §4.3 measured in advance (the `longjmp`-value
candidate: 108 of 108 ladder, 0 of 40 legend).

**AFTER THE MERGE (`050c2b83`), on the delivered branch, every cell is
zero:**

| witness | absorbed, single | absorbed, sustained | swept total | pinned |
|---|---:|---:|---:|---:|
| W1 `[a-z]+` | **0** | **0** | 57 | 57 / 0 / 0 |
| W2 `[a-z]{2,10}` vm | 0 | 0 | 11 | 11 / 0 / 0 |
| W3 `\p{L}` utf8 | **0** | **0** | 303 | 303 / 0 / 0 |
| W4 ladder | **0** | **0** | 158 | 158 / 0 / 0 |

`make alloc` exits 0: `checks passed: 8, checks failed: 0`. Two things are
worth reading off that table rather than just the zeros. **Every pinned
POPULATION held across the merge** — 57 / 11 / 303 / 158, unchanged — which
is the evidence that D109 added no allocation site, measured rather than
assumed. And **W4's pin going stale-low the moment `k60fix` landed is the
ratchet doing its job**: the pin at 108 failed against a tree where the
defect was fixed, which is exactly the signal that a re-pin was owed. All
four rows now pin zero and `absorbed_why` is NULL on all four, so any
absorption anywhere in this file is a regression.

### 2.2 The control, run rather than argued

The pinned check against a `git archive` build of the branch point
`6c9dac09` (coding guide §5 item 5 — a check needs a failing-direction story
before it is written):

```
FAIL: W1 (DFA): the swept POPULATION moved -- 72 forced allocations, pinned at 57 ...
FAIL: W1 (DFA): 15 of 72 forced allocations were SUCCEEDED THROUGH anyway -- first at N=57 ...
FAIL: W1 (DFA) [sustained]: the swept POPULATION moved -- 72 ... pinned at 57 ...
FAIL: W1 (DFA) [sustained]: 5 of 72 forced allocations were SUCCEEDED THROUGH anyway ...
FAIL: W3 (unicode-props/utf8): the swept POPULATION moved -- 328 ... pinned at 303 ...
FAIL: W3 (unicode-props/utf8): 25 of 328 forced allocations were SUCCEEDED THROUGH anyway ...
FAIL: W3 (unicode-props/utf8) [sustained]: the swept POPULATION moved -- 328 ... pinned at 303 ...
checks passed: 4   checks failed: 8
```

Eight failures against the fixed tree's one (W4's standing ladder defect),
on both pins and in both modes.

The verdict strings other readers depend on are unchanged: section 2b of
`tests/resource/run_resource_tests.sh` greps `KILLED THE PROCESS BY SIGNAL`,
and the leading sentence of the SUCCEEDED-THROUGH line is the one
`k60_measurement.md` quotes.

---

## 3. Byte identity — the bar

**Not an abi event**, as ruled: no emitted byte moves. Two arms, both
full-corpus, both comparing artifacts written to the **same basename in
different directories** — this house's recorded `-o`-basename trap, which has
now bitten four lanes and read as `identical=0` for `k60meas` on a
comment-only probe. I reused the committed driver
`docs/dev/dialtrain_byteid_evidence/byteid_sweep.py` rather than rebuilding
one; it already enumerates every `pattern`/`pattern-esc` line through
`--list-source`, decodes the format's escape vocabulary to raw bytes, passes
them through `argv` directly, and gets the basename right.

### 3.1 Arm A — default axes, `-p rx`

| | |
|---|---:|
| `.rxt` files | 211 |
| `pattern`/`pattern-esc` lines | 3,938 |
| compiled by BOTH, byte-identical | **1,500** |
| **differing** | **0** |
| newly fixed / newly broken | 0 / 0 |
| both refuse (module-gated at default flags) | 2,438 |

The population matches `dialtrain_byteid.md`'s own sweep at a nearby pin
(3,938 / 1,500 / 2,438), which is a useful cross-check that the extraction
reached the same corpus. An independent confirmation of the mover count falls
out of the driver's own housekeeping: it deletes both artifacts of an
identical pair and keeps a mover's, and the output directory ends with 1,500
`.h` sidecars and **zero** `.c` files left behind.

### 3.2 Arm B — `--features all`, plus a LEGEND-REACH census

Arm A compiles at default flags, where 2,438 lines are module-gated and never
reach an emitter at all. Arm B re-runs the whole corpus at `--features all`
so the gated population compiles too, and — because **byte identity over
artifacts that contain no legend proves nothing** ([MECH-REACH], coding guide
§5 item 3) — counts, for every artifact compared, whether it carries a state
legend and which arm of the rewritten function produced it.

| | |
|---|---:|
| `pattern`/`pattern-esc` lines | 3,938 |
| compiled by BOTH, byte-identical | **3,517** |
| **differing** | **0** |
| newly fixed / newly broken | 0 / 0 |
| both refuse (at `--features all`) | 421 |

Reach, measured over those 3,517 compared artifacts:

| | artifacts |
|---|---:|
| carry a state legend at all | **3,024** (86.0%) |
| ... took the FULL per-state listing (reads `path`/`from`/`via`) | 3,014 |
| ... took BRIEF mode (the arm that now skips `from`/`via`) | 23 |
| ... carry a TRUNCATED example (the arm the fixed 40-int local bounds) | 14 |
| carry no legend | 493 |

The three arm counts OVERLAP and do not sum to 3,024: an artifact emits up to
three machines, so one file can carry a full listing for its forward machine
and a summary for another. The 493 with no legend at all are the VM-engine
artifacts plus the DFA artifacts whose transition table was uniform-folded,
which drops the table and its legend together ([CC-DIFF] (b)).

So the identity claim rests on **3,024 artifacts that actually contain the
text this change rewrote**, with all three arms of the rewritten function
represented, rather than on a population that might have contained none.
Arm A's 1,500 is a subset of this by construction and is reported separately
because default axes are the axis every identity gate pins.

### 3.3 The arms exercised, by hand

Each arm of the rewritten function has a cheap witness, verified
byte-identical against the branch-point binary before any sweep was launched.
They are recorded in `src/gen/CLAUDE.md` so the next editor does not have to
re-derive them:

| witness | what it exercises | result |
|---|---|---|
| `x[0-9]{500}y` | a 502-byte example, the drop path 462 stores deep | identical |
| `(?i)a{2,40}Z` | a 41-byte example — the first store past the bound | identical |
| `((a)|b){0,4000}c` | brief mode, 4,002 accepting states | identical |
| `[a-z]{0,16384}` | a 16,384-deep SCAN EDGE, the unbounded `maxd` | identical |
| `^ab(c|d)e$` | the "no path through the transitions" row | identical |
| `a(b|c)+d`, `[a-z]+` | the ordinary full listing | identical |

---

## 4. Validation

| | result |
|---|---|
| `make -j4 CC=gcc-16` | clean, at every commit |
| `make strict CC=gcc-16` | **clean** — whole tree with `-Werror -Wshadow` |
| `make alloc CC=gcc-16`, pre-merge | W1 **0**, W2 0, W3 **0** absorbed in both modes; W4 108 (the ladder class, then open) |
| `make alloc CC=gcc-16`, POST-MERGE | **rc 0 — 8 checks passed, 0 failed.** All four witnesses, both modes, zero absorbed; every pinned population held |
| `make alloc` control at `6c9dac09` | 8 failures vs the fixed tree's 1 — §2.2 |
| `make test-codegen CC=gcc-16` | **8 of 9 scripts** (222 PASS), one red: `run_inline_capability.sh` — same before and after the merge |
| `bash tests/rxtsource/run_rxtsource_tests.sh` | **212 passed / 1 recorded / 0 failed** (211 files / 3,938 blocks / 28,949 expectation lines) |
| full-corpus emit-diff, arm A | 1,500 identical / **0 differing** |
| full-corpus emit-diff, arm B | §3.2 |

**`run_inline_capability.sh` is PRE-EXISTING and A/B verified**, not
attributed by assumption: run from a `git archive` build of `6c9dac09` it
fails identically — `FAIL: nm could not read arm_a.o (no rx_search symbol)`
on the same witness. It is the standing darwin red this file's other reports
name.

The `RECORD:` line in `rxtsource` is this box's known darwin C3
non-native-pin behaviour (`btriage_20260917_report.md`), and the count
matches `k60meas`'s own 212/1/0 at the same pin.

Not run, deliberately, per the brief: full `make test` (the emit-diff sweep
is this lane's heavy item and the box takes one at a time), `make mech`,
`make san`, and anything on `ubuntubudu`. The manager runs `make test`
locally and `make san` on `ubuntubudu` after the merge.

### 4.1 Re-run after the merge

Every light target above was re-run on the merged branch `050c2b83`, not
inherited from the pre-merge run: `make -j4` and `make strict` clean,
`make alloc` **green (8/0, rc 0)**, `make test-codegen` 8 of 9 with the same
single pre-existing red, `rxtsource` **212 / 1 recorded / 0** over the same
211 files / 3,938 blocks / 28,949 expectation lines. The emit-diff was
re-run too, and against the NEW `main` rather than the old branch point —
§3.4 — so the identity claim is about this lane's delta on the tree as it
stands, not on a base that no longer exists.

### 3.4 Both arms, re-run against `main` at `2e019d20`

Arms A and B above compare against the branch point `6c9dac09`, which is
this lane's delta in isolation. After merging `main` (lane `k60fix`'s D109),
both arms were re-run with `main` at `2e019d20` as the baseline, so what is
being measured is this lane's delta **on the tree as it stands**:

| arm | lines | compared | **differing** | newly fixed / broken | both refuse |
|---|---:|---:|---:|---:|---:|
| A, default axes | 3,938 | 1,500 | **0** | 0 / 0 | 2,438 |
| B, `--features all` | 3,938 | 3,517 | **0** | 0 / 0 | 421 |

Identical to the pre-merge arms in every cell, including arm B's reach
census (3,024 artifacts carrying a legend; 3,014 full, 23 brief, 14
truncated). That the two baselines give the same answer is itself worth one
line: `k60fix`'s D109 changes only what happens at the arrival of a
`ctx_nomem`-routed `longjmp`, which no successful compile reaches, so it
moves no emitted byte either and the two lanes' deltas do not interact.

---

## 5. Findings

**5.1 The brief's "the Job's arena" does not exist; the compile's arena is
`Ctx.arena`.** Not a problem — the general mechanism is the same one — but a
reader of D105's rider will go looking for a Job field and not find one. The
Job owns six `StrBuf`s and no arena.

**5.2 No sabotage row S260 — the trade-off in one line: putting the
population pins into `make test` would tax every future refactor that
legitimately moves an allocation count, and leaving them out leaves this
plant undetectable.** Frank's call; not built here. The long form: A plant reverting this function to raw `malloc` with the silent
return would ship **UNDETECTED**, because no arm `make mech` runs can see it.
The nearest arm is `resource`, which runs `run_resource_tests.sh`, whose
section 2b runs `alloc_check` **argument-free and greps only for
`KILLED THE PROCESS BY SIGNAL`** — deliberately, so that `make test` does not
go red for K60, which was open when that section was written. A silent
absorption produces no signal, so the plant passes.

Making it detectable means section 2b asserting the population pin, which
puts allocation COUNTS into `make test` and taxes every future refactor that
legitimately moves one. When this was written the trigger was "once K60's
ladder class lands and `make alloc` is green end to end" — **that trigger has
now been MET** (`050c2b83`: both classes fixed, all four witnesses green,
every witness pinning zero), so section 2b asserting the pins is now
technically available and the decision is purely the `make test` tax. Still
not built here: choosing to tax `make test` is Frank's call, not a lane's,
and it should be made on the tax rather than on this one plant.

Note also that `make alloc` is not a battery stage (`scripts/battery.sh` has
no `alloc` stage), so these pins have no automatic home at all today — which
is the same gap from the other side.

**5.3 The merge collision with `k60fix` resolved itself, and the way it did
is the pin's own argument.** Both lanes edited `tests/core/alloc_check.c`'s
W4 expectation. `k60fix` landed first and added no competing expectation
shape, so the merge kept this lane's struct and re-pinned W4's number from
108 to 0 — and the mechanical signal that the re-pin was owed was the pin
itself failing stale-low against a tree where the defect was gone. A check
that goes red when a defect is FIXED sounds perverse until it is the thing
that stops a landing from silently turning a red line green.

**5.4 `tests/resource/run_resource_tests.sh` section 2b's success message
says "three witnesses" and there are four** (W4 was added by `k60meas`).
Cosmetic, untouched here to keep the merge surface away from a file another
lane may be editing, and named so it is not lost.

**5.5 The population pin caught what the absorption pin could not, and that
was not the argument for adding it.** It was added for K35's reason — count
the population, fail on an empty one. It then turned out to be the ONLY arm
that fails on W3's sustained sweep against the unrepaired library, because
that sweep absorbs zero even when the defect is present. A check written for
one reason earning its place for a different one is worth recording in a file
whose §3 is about checks that pass for the wrong reason.

---

## 6. Rulings received

None. No escalation was needed: the ruling was already made and the brief's
one forbidden move (re-litigating the "announce the dropped legend" option)
never came up, because the restructuring leaves nothing to announce.

## 7. Reproduction

```
# the branch-point baseline, for every control and both sweep arms
git archive 6c9dac09 | tar -x -C <scratch>/base && make -C <scratch>/base -j4 CC=gcc-16

# the pins' failing direction
LIBPCREC=<scratch>/base/build-alloc/libpcrec.a bash tests/core/run_alloc_tests.sh

# arm A (the committed driver, reused unchanged)
python3 docs/dev/dialtrain_byteid_evidence/byteid_sweep.py \
    <scratch>/base/build/pcrec ./build/pcrec . <outdir>
```
Arm B's driver adds `--features all` and the reach census around that same
driver's extraction; it lived in the session scratchpad and is not committed,
its numbers standing on this report as `dfam12`'s and `k60meas`'s do on
theirs.

---

## 8. The merge with `main` (`050c2b83`)

`main` moved to `2e019d20` while this lane ran: lane `k60fix` landed D109,
K60's LADDER class. Merged in here at the manager's instruction.

**One true conflict, `docs/spec/match_api.md` §8.1** — both lanes wrote the
same paragraph about the same promise, each from its own half. Resolved into
one statement that the promise had TWO exceptions and now has none, keeping
both lanes' history text and adding the sentence neither could write alone:
*because the legend path never reached the recovery point, D109's fix could
not reach it either*, which is why one entry needed two fixes. Everything
else auto-merged, and was then read rather than trusted.

**The re-pin.** W4's expectation goes 108/0 → 0/0. The pin failing stale-low
the moment `k60fix` landed IS the mechanism working: a check that goes red
when a defect is fixed sounds perverse until it is the thing that stops a
landing from silently turning a red line green. All four witnesses now pin
zero and `absorbed_why` is NULL on all four.

**Stale wording, corrected in tense and status only.** Each of these was
written by the other lane before this fix existed; the history text is kept
in every case:

| site | was | is |
|---|---|---|
| `src/core/compile.c:855` | "0/40 legend absorptions reached — a different, UNFIXED mechanism" | a mechanism this arrival cannot see (it never called `ctx_nomem`, so it never arrived), closed separately and by deletion in D105; K60 closed between the two |
| `known_issues.md` K60 status | "PARTIALLY FIXED … the LEGEND class is still filed, assigned to lane d105" | "FIXED — BOTH CLASSES", both commits, both dispositions, the green four-witness table |
| `known_issues.md`, k60fix's note | "W1 and W3 are UNCHANGED, on purpose … that class is D105's, building in parallel" | "were UNCHANGED BY THIS FIX", with the landing named and the original preserved as that lane measured it |
| `known_issues.md`, the k60meas amendment | "that 27% IS D105'S OWN UNBUILT RULING" | left standing — a dated historical statement — with a parenthetical that it was built later the same day |
| `alloc_check.c`'s `[K60FIX]` header | "W1 and W3 … are EXPECTED to keep failing until that mechanism's own fix lands" | a `[D105]` paragraph: every witness is expected to PASS, and any FAIL is now a real regression whichever witness it names |
| `tests/core/CLAUDE.md`'s `[K60FIX]` note | "W1/W3 ARE THE EXPECTED RESIDUAL … EXPECTED to stay red" | the same correction, plus the point that the pins are what make "`make alloc` is green" checkable rather than remembered |

**`src/core/internal.h` needed no change** — checked rather than assumed.
Its `failed_nomem` comment cites K60's measured 108-of-148 mechanism as
history and makes no claim about the legend's status.
