# [K53-SELRETRY] — the optional-contributor drop ladder (lane utf8k53, 2026-09-10)

Branch `lane/utf8k53`, worktree `worktrees/utf8k53`, base `9e436d31`.
`docs/dev/known_issues.md` K53 is marked **FIXED**.

---

## 0. What shipped, in one paragraph

`compile_driver`'s retry loop gains a rung. On an emitted-size cap refusal
with the OPTIONAL anchored match-here machine present, the driver raises
`Ctx.size_drop_rung` and re-attempts; `build_anchored_dfa` reads that rung on
the same line it already reads `-fno-anchored-dfa`, so the machine is not
built, the artifact fits, and the caller gets a matcher instead of a
diagnostic. The outcome is stamped `RX_DFA_MATCH "search-filter"` plus
`RX_ENGINE_SEL "size-cap-retry"`. **No new macro. No `abi` bump.** All
fourteen `\p` spellings K53 named compile; the sixteen parked corpus blocks
are back at their authored positions; every artifact that compiled before is
byte-identical.

---

## 1. The three design questions the brief assigned, answered

### 1.1 Where the retry lives — the DRIVER, and it could not live anywhere else

Not the selection layer: emitted size is not knowable before emission, so
nothing at selection time can predict it. Not the emit layer either, in the
sense of a local recovery point — this compiler has **one** `setjmp`, and
`[SEL-1]`'s charter explicitly ruled out "a try/catch-shaped clause at the
`ctx_fail` site". So the rung goes where the other two size-and-overflow rungs
already are: in the `setjmp`-catch chain of `compile_driver`, as one more pass
of the existing loop with one more input bit set.

**That is instantiating the general mechanism, not building a parallel one.**
The catch chain already had [SEL-1]'s two overflow rungs and [OPT-4]'s size
rung, each shaped `(eligibility) -> latch -> job_cleanup -> set an input bit ->
continue`. This is a fourth of the same shape.

### 1.2 The general "drop optional contributors" ladder — YES, and the K53 instance is built

The brief asked whether a general ladder is the right shape. **It is, and it
is spelled as one**: `Ctx.size_drop_rung` is an ORDINAL (`SDR_NONE`,
`SDR_NO_ANCHORED`, `SDR_MAX`), not a bool, and a rung's value means *"every
contributor up to and including this one is dropped"*, so a second rung
composes with the first rather than replacing it.

**One rung is built, and the reason a second is not is D77 rather than
laziness.** What a two-rung ladder needs and this row could not supply is an
**ORDER**, and the order is a measurement: rungs must be ordered by what
dropping each costs the artifact at run time, cheapest first. With exactly one
contributor there was nothing to order and no way to derive the rule from a
sample of one. The obligation is stated at the `SDR_*` enum rather than left
for a future author to rediscover, along with the membership rule: a
contributor may join only if dropping it is **answer-preserving**,
**observable in the artifact's own stamps**, and **smaller** — the three
properties the anchored machine has and that make its loss strictly better
than a refusal.

I deliberately did **not** build a contributor table, a registry, or a
per-contributor callback. At N=1 those are machinery designed around one
customer, which D18/OS-0/D53 forbid and which this tree has recorded going
wrong before.

### 1.3 Interaction with [OPT-4]'s size rung, [LIM-2] and N1

**[OPT-4]'s size rung and this one are MUTUALLY EXCLUSIVE, and it is derived
rather than observed.** That rung requires `fit.chosen != ENGM_DFA` (it
collapses a VM hybrid's prefilter); this one requires `Job.anchored_ok`, which
`build_anchored_dfa` sets only under `fit.chosen == ENGM_DFA`. No pattern can
take both. Three consequences, all recorded at the code:

* their relative position in the catch chain is **free** today;
* `COMPILE_MAX_ATTEMPTS` grows by `SDR_MAX` (one) and not by a ladder's worth,
  because the size-term ladder runs only for `ENGM_VM` and a drop attempt can
  therefore never enter it;
* the size-term ladder's cross-attempt state is **not** reset by this rung
  (unlike [OPT-4]'s, which must), for the same exclusivity reason — an attempt
  eligible here has never entered that ladder.

A future droppable contributor on the VM side ends all three at once, and is
the event that makes rung ORDER a real question.

**[LIM-2] N1** (the auto-route work budget) is untouched: it is scoped to
`!d->optional` at its own check site, so the optional machine's construction
never triggers it, and it fires before emission where this rung fires after.

**[LIM-2]'s projected-size bail is the interesting one and it is a WARNING, not
a conflict.** That row projects the table part DURING subset construction and
refuses early with the same stamped reason. Two things follow and both are the
manager's to relay:

1. **The projection must route an OPTIONAL machine's contribution to the
   OPTIONAL arm** (`d->overflowed = true`, the §5.2 shape), never to
   `ctx_fail`. If it refuses on a projection that includes the optional
   machine's bytes, it re-introduces K53 one pass EARLIER than this retry can
   see — the post-emission rung never runs, because the compile died during
   construction.
2. **[LIM-2]'s own acceptance control has to be re-based.** Its charter reads
   *"the refusal set moves NOT AT ALL — a check, not a hope: the corpus + the
   bench's altwide@0.1 refusal table are the before/after"*. This row MOVES the
   refusal set, and (see §3) moves it on exactly the altwide family. Its
   before/after must be taken against this tip.

---

## 2. The stamp question (D77 discipline on new stamps)

**No new stamp.** `ESEL_SIZE_CAP_RETRY` — [LIM-1]'s value — already means
*"an emitted-SIZE cap forced a retry and the retry shipped"*, which is exactly
this event. Its comment's "Reachable ONLY from `collapse_reason == CR_SIZECAP`"
clause was a description of the one rung that existed when it was written, not
part of the meaning; it is corrected in place.

**Which contributor was dropped is answered by the artifact's own axis stamps,
and the pair is EXACT rather than merely suggestive**, because the two rungs
are mutually exclusive by engine:

| rung | engine | what the artifact stamps |
|---|---|---|
| [OPT-4] prefilter collapse | VM hybrid | `_DFA_PREFILTER` set, `_PREFILTER_LANG_WHY "count-collapsed"` |
| [K53-SELRETRY] optional drop | DFA | `_DFA_MATCH "search-filter"` |

**Minting a second value would have put one event in two homes**, which is the
drift `ESEL_*`'s whole comment history is about (K35's "closed value set
silently losing a member", twice already in that enum).

**The one conjunct that did NOT carry over, and why.** The existing arm reads
`collapse_reason == CR_SIZECAP && fit.prefilter`. That `fit.prefilter` guard
exists because a size-refused VM compile can end with no prefilter and
stamping "a prefilter survived" would name a decision the artifact did not
take. A DFA-engine artifact has no prefilter to survive — `fit.prefilter` is
false on **every** member of this rung's population — so requiring it would
have made the arm unreachable on exactly the patterns it exists for.

### 2.1 FINDING — a force form spends this macro, and it was already true

**The rung is deliberately NOT gated on `--engine=auto`**, unlike [SEL-1]'s
engine fallback. That one must be: it hands the caller a different ENGINE from
the one they demanded. This one changes only an entry-point FORM *inside* the
engine they asked for, and no flag lets a caller demand the dropped machine
(`-fno-anchored-dfa` is deny-only, with no force counterpart), so honouring the
request and dropping the machine are compatible. The payoff is concrete:
`--engine=dfa --features unicode-props -e utf8 -- '\p{L}'` compiles too.

**But it stamps `RX_ENGINE_SEL "forced"`, not `"size-cap-retry"`** — `ESEL_FORCED`
is tested first and wins outright — so on a forced compile the drop is legible
as `RX_DFA_MATCH "search-filter"` with **no** attribution.

**I checked whether I introduced that and I did not.** MEASURED on a
branch-point compiler: [OPT-4]'s own size rung has the same blind spot, and its
witness `(a|b){1,30000}` stamps `"forced"` under `--engine=vm` where `auto`
gives a value that names what happened. So this is a pre-existing property of
`ESEL_FORCED`'s precedence that the new rung INHERITS.

**Left as it stands, and recorded rather than fixed**, for two reasons: no
consumer has asked (D77), and re-ordering the arms would move an existing stamp
on every forced artifact that has ever hit a cap — a caller-observable change
outside this row's charter that would need its own re-pin and its own battery.
`docs/spec/match_api.md` §6.3 now states it so a reader of the new table row is
not misled.

**No stderr note.** [LIM-2] N1's precedent prints one, but its event is a NEW,
lower, surprising limit. This one is fully stamped, strictly better than the
refusal it replaces, and every artifact in its population is already over
`PCREC_DEFAULT_WARN_EMIT_BYTES` (250,000) and therefore already carries the
large-artifact warning line.

**No `abi` bump.** Nothing in the emitted scaffolding moved: the artifact a
drop-rung compile produces is the `-fno-anchored-dfa` build's, byte for byte,
apart from the `RX_ENGINE_SEL` string — a stamp VALUE, which is [LIM-1]'s own
precedent under D76 ("a VALUE, not scaffolding, no `abi` bump either time").
Asserted rather than argued: §6a of `run_anchored_match.sh` byte-compares the
two.

---

## 3. Acceptance, measured

| the brief's bar | result |
|---|---|
| the 16 known_fail blocks FLIP and go green oracle-verified | **578 cases / 0 failed / 0 compile failures** over the two restored files |
| moved out of known_fail, ratchet updated | `tests/known_fail/k53_uprops_oversize.rxt` **deleted**; 12 blocks to `axis04_p_categories.rxt`, 4 to `axis12_scripts.rxt` |
| `\p{L}` at `-e utf8` default axes compiles | **yes**, 772,418 raw bytes (refused at 1,076,638 comment-excluded before) |
| K53 gains its FIXED marker | done |
| `abi` bump only if scaffolding changed | **no bump** — nothing changed (§2) |
| byte-encoding identity unaffected | **3,348 / 3,348 identical** (§3.2) |
| targeted suites green | §3.3 |

### 3.1 All fourteen spellings, measured at default axes under `--features unicode-props -e utf8`

Every one refused at the branch point; every one compiles now, each stamping
`RX_ENGINE_SEL "size-cap-retry"` and `RX_DFA_MATCH "search-filter"`:

`\p{L}` 772,418 · `\P{L}` 755,005 · `\p{C}` 764,578 · `\P{C}` 768,496 ·
`\p{Cn}` 715,255 · `\P{Cn}` 752,640 · `\p{Unknown}` 729,903 ·
`\p{sc=Unknown}` 729,912 · `\p{scx=Unknown}` 729,915 · `\p{Zzzz}` 729,893 ·
`\p{Xan}` 912,007 · `\P{Xan}` 899,188 · `\p{Xwd}` 1,003,979 ·
`\P{Xwd}` 970,323 (raw bytes; the cap is on comment-excluded bytes).

Each is **exactly 6 bytes** larger than the same pattern's
`-fno-anchored-dfa` build — `strlen("size-cap-retry") - strlen("selected")`.
That arithmetic agreeing is a small independent confirmation that the two
artifacts differ in the stamp and nothing else.

### 3.1a The three axes that could have interacted, spot-checked on `\p{L}` under `-e utf8`

| axis | outcome | why it is the right one |
|---|---|---|
| `--no-captures` | compiles, `ENGINE_SEL "size-cap-retry"` | the flag routes MORE patterns to the DFA, so it can only widen this rung's population |
| `-fprefilter` | REFUSES, unchanged | it is refused in `select_engine` ("requires the VM engine; this pattern compiles to the DFA engine"), above and before the rung — the flag never reaches it |
| `-fno-anchored-dfa` | compiles, `ENGINE_SEL "selected"` | **the control that makes the stamp story real**: the caller asked, so no retry happened and the macro says so. Same artifact, different provenance, and `RX_ENGINE_SEL` is what tells them apart |

### 3.1b The size tripwire is safe, and the HEADROOM is the number to worry about

`tests/size/check_size_tripwire.sh` pins `MAX_SIZE_BYTES` 1,400,000 and
`MAX_GCC_CPU_S` 8.0, and the corpus gained sixteen large artifacts, so both
were measured rather than assumed (under load1 3.0, i.e. the CONSERVATIVE
direction for an "is it under the pin" question):

| pattern | comment-excluded bytes | gcc CPU at `-O1` |
|---|---:|---:|
| `\p{Xwd}` (largest of the fourteen; not in the corpus) | 992,257 | **0.19 s** |
| `\p{L}` (largest corpus member) | 760,852 | **0.17 s** |

Both pins have large margins — the gcc CPU one enormously so, which the
[ART-SIZE] census already predicts (a data-table entry costs gcc ~0.905 µs
against a VM node's 5.37 ms, and these artifacts are almost all table).

**THE HEADROOM AGAINST THE CAP ITSELF IS THE FRAGILE NUMBER, AND IT IS
0.7 %.** `\p{Xwd}` fits under `PCREC_MAX_EMIT_BYTES` (1,000,000) by **7,743
bytes**. Any future change adding ~8 KB of scaffolding to a DFA artifact
re-refuses it — and an `abi` bump adds lines to every artifact by definition.
The drop rung buys these patterns a compile; it does not buy them room.
`[CLS-TREE]` is the row that would, by emitting a huge class as DATA rather
than as automaton structure, and this measurement is a direct argument for it:
the rescue is a reprieve at single-digit-percent margin, not a solution.

**A COST NOTE FOR THE BATTERY.** Sixteen blocks that previously did not
compile now emit ~715-760 KB artifacts each, so `tests/utf8`'s harness section
is measurably slower than before this change — the price of the patterns
working. `make test`'s own timing is the manager's to re-read at the battery.

### 3.2 Byte-identity: 3,348 of 3,348

Every distinct `(pattern, encoding, features)` triple in the corpus, compiled
by a compiler built from the branch point and by this one, hashed and
compared: **0 differing, 0 that stopped compiling, 0 that started** (the 416
identical-and-refused are `perr` blocks). The rung is reached only from a
refusal, so it cannot move an artifact that already existed.

**THE SWEEP IS THE DEFAULT ENGINE AXIS, AND THE OTHERS FOLLOW BY ARGUMENT
RATHER THAN BY MEASUREMENT — stated so a reviewer does not have to ask.**
`--engine=vm` cannot reach the rung at all (`build_anchored_dfa` returns
before anything under `fit.chosen != ENGM_DFA`, so `anchored_ok` is false on
every VM artifact and the eligibility test can never hold). `--no-captures`
and `--engine=dfa` route MORE patterns to the DFA and can therefore reach it
MORE often — but still only from a refusal, so the same argument covers them:
an artifact that compiled under any axis before compiles to the same bytes
now. The three spot-checks in §3.1a exercise two of those axes directly.
What no argument covers is a pattern that REFUSED under one of those axes and
now compiles, which is the intended change and is what §4 counts.

**The sweep found two of its own defects before it found none of mine**, and
both are worth carrying:

* **A stale reference.** The main tree's `build/pcrec` was older than main's
  own HEAD, and the first run reported 2,703 of 2,800 differing. Rebuilding the
  reference from `git archive 9e436d31` fixed it. *A checked-in build directory
  is not a compiler at a commit.*
* **The `-o` basename trap, met again.** The emitted `.c` carries
  `#include "<basename>.h"`, so comparing `b.c` against `a.c` makes every
  artifact differ. This is the third time this tree has recorded it
  (`run_trie_identity.sh`'s `gen_a`/`gen_b`, `run_vm_identity.sh`, the opt5m2
  memo). Fixed by same basename in different directories, and the fix is
  commented in the script.

### 3.3 Suites

Run on the delivered tip. Numbers are OWED for the batch still running at
write time; see §8.

* `make strict` — **green** ("whole tree compiles clean with `-Werror -Wshadow`").
* `tests/codegen/run_anchored_match.sh` — **20 passed / 0 failed**, including
  the new §6 and the restored overflow-bucket ceiling of 0.
* `tests/rxtsource/run_rxtsource_tests.sh` — census and denominators
  **reconcile** at 210/3936/28943 and 209/3933/28932 (§5). Its legs B/C stay
  red on this box: BSD `xargs -a`, catalogued as `[MACPORT-XARGS]`, predates
  this lane.
* `tests/harness/run.sh tests/utf8/axis04_p_categories.rxt
  tests/utf8/axis12_scripts.rxt` — **578 / 0**.

---

## 4. FINDING — the corpus population is not the `\p` family

**Eight corpus patterns that REFUSED at default axes now compile, and not one
of them is a `\p` pattern.** All eight are wide literal alternations from
`tests/rxtsource/fixtures/bench_altwide_0_2.rxtin` — pcrec-bench's own
`altwide` witnesses.

The reason is mechanical and worth stating so nobody re-derives it: the codegen
census compiles each corpus `pattern` line at DEFAULT axes with **no
encoding**, so the six `\p` names that motivated the row are compiled under
`byte`, where a property set is clamped to Latin-1 and is tiny. They are not in
this count at all.

**This is K53's own filing discharged rather than merely asserted.** The entry
says, in its first line, *"Filed as an ENGINE issue, not a Unicode one. `\p{L}`
is where it was found and is not where it lives."* The corpus population is the
evidence: the mechanism reaches a family that has nothing to do with Unicode
properties, and would have reached it whether or not module `unicode-props`
existed.

**Two consequences for other lanes**, both relayed to the manager:

1. The **bench's altwide refusal table moves**. Eight of its witnesses stop
   refusing at default axes.
2. **[LIM-2]'s before/after control must be re-based** onto this tip (§1.3).

---

## 5. FINDING — the check that went red was the finding, twice

### 5.1 A bucket defined by elimination

`run_anchored_match.sh` §5 buckets every DFA artifact by
`(RX_DFA_MATCH, RX_DFA_SCAN)`, and its fourth bucket — *"the anchored machine
exceeded a DFA STATE cap"* — was defined **by elimination**: it was the last
way left to reach `search-filter` on an `ENG_UNANCH` machine. The eight
rescued patterns landed in it, and the check reported:

> `§5 8 corpus artifacts now reach the OVERFLOW fallback, where the pin says 0
> … A corpus pattern has grown past the 4,096 ceiling: re-derive the ceiling
> from the new maximum, do not simply re-pin this line`

**The right alarm with the wrong cause**, on a population that never went near
the 4,096 state ceiling — and the advice it gives (re-derive the ceiling) would
have been wasted work. A fifth bucket keyed on `RX_ENGINE_SEL` fixes it, and
the two pins are deliberately opposite in kind: the overflow bucket keeps its
**ceiling of 0** (its population is out-of-corpus and §4 tests it), the
size-drop bucket gets a **floor of 6** (8 measured), because an empty
population there means the mechanism is unreached and no answer check in the
tree would say so.

**The transferable rule**: *a bucket reached by elimination is a bucket that
will one day hold something else.* That is K35's shape in a classification
rather than in a count.

The A/B discipline is what made this attributable rather than guessed:
the same check is **15/0 green** at the branch point and red here, so the red
was mine and not pre-existing.

### 5.2 The census pin caught a defect in my own corpus move

The `tests/rxtsource` census reported **+4 blocks** where the arithmetic said
0. Cause: the script I used to cut the known_fail file into groups let its
**last group run to end-of-file**, so the four `\p{Unknown}` script blocks were
dragged into `axis04_p_categories.rxt` as duplicates *and* written to
`axis12_scripts.rxt` as intended.

**No test failed.** The duplicated blocks compiled and answered correctly; the
corpus run was 590/0 with them and 578/0 without. Only a count could see it —
which is precisely the argument that pin's own header makes for existing.
Fixed, and `axis04` now reads 148 `pattern` lines against 148 `# axis4 block`
headers and against its own header's stated 148.

---

## 6. FINDING — how §5.2's promise came to be broken

Recorded in `docs/design/anchored_match_unwrapped.md` §5.2a rather than only
here, because it is a lesson about writing that kind of promise.

`anchored_match_unwrapped.md` §5.2 enumerates the budgets the optional machine
is charged against by **walking `pcrec_build_dfa`'s parameters** — the state
cap, the table-entry narrowing, the per-compile subset-element budget — and
every one of them is checked at a site the `optional` flag reaches. **The
emitted-BYTES cap is not charged by the build at all.** It is charged to the
artifact's SIZE, three machines downstream, at a site where *"whose bytes are
these"* is not a question anything can ask.

So the enumeration was complete **in the code it read** and incomplete **in the
property it claimed**.

> **The general form: "this component is optional" is a claim about every
> resource the component consumes, and the resources a component consumes are
> not all charged where it is built.**

---

## 7. The other design annotation the row required

`docs/design/utf8_design.md` §3.3 concludes *"the 'table-size problem' the
charter names is, for the DFA route, measured not to be a problem"*, on the
strength of `\p{L}` being 283 minimized states. That is annotated in place as
**REFUTED**, with the mechanism named: emitted size is
`states × byte-equivalence-CLASSES × digits-per-cell`, and the section measured
**states**. Under a multi-byte encoding the class count is ~100 where an ASCII
pattern's is a handful.

> **A sizing argument must name every factor of the product it is bounding**,
> and this one named the factor that was easiest to measure on the oracle.

The annotation is careful about what the fix does and does not buy: the
refusals are gone, but the surviving artifacts sit at **72–100 % of the cap**,
so the charter's concern was real and this section's answer to it was wrong.
`[CLS-TREE]` is the row that answers it properly.

---

## 8. What is OWED, and what is not

**COMPLETE**: the implementation, the spec hunks (D80 — `limits.md` §8's new
"optional-contributor drop" subsection plus its [ENG-ABS] exception paragraph,
`tuning.md` §2.15, `match_api.md`'s `ENGINE_SEL` and `DFA_MATCH` tables), the
two design annotations, the corpus move and both census re-pins, the K53 FIXED
marker, the plan row, five `CLAUDE.md` files, `make strict`,
`run_anchored_match.sh` 20/0, byte-identity 3,348/3,348, and both sabotage
rows **validated in the failing direction** (§9).

**OWED to the manager**: the FULL BATTERY, which is the manager's at merge by
standing policy. Nothing else.

**OWED and marked as such at write time**: the targeted batch launched at the
end of this lane's working period — `run_anchored_match.sh` re-run on the
corrected corpus, `tests/utf8` in full, `make test-uprops`, `make test-codegen`,
`make test-encoding-checks ENC_MAX_BLOCKS=250`, and a 3-axis
(`--engine=vm`, `--engine=dfa`, `-fno-anchored-dfa`) axes SLICE over the two
flipped files. **Log: `<scratchpad>/targeted.log`, per-suite logs
`<scratchpad>/t_<label>.log`; the completion line is `TARGETED BATCH
COMPLETE`.** Each suite prints `=== END <label> rc=N`. A non-zero `rc` on
`utf8corpus`, `uprops`, `codegen` or `encchk` is a finding; `rxtsource`'s BSD
`xargs -a` reds are pre-existing ([MACPORT-XARGS]) and are not in this batch.

---

## 9. Sabotage rows, validated

Two rows on the `anchoredmatch` mech arm, both carrying `SAB_REACH` from birth
(the probe reads `RX_ENGINE_SEL "size-cap-retry"` off `\p{L}` under `-e utf8`,
so if `[CLS-TREE]` ever makes that pattern fit unaided both rows score
UNREACHED honestly instead of certifying nothing).

**S237 — the rung never fires.** Eligibility forced false. Measured:
`17 passed / 6 failed` — the three §6a witnesses REFUSE, §6a's summary reads
`0 of 3`, §6b's refusal quotes **23,720** bytes (the artifact WITH the machine,
23,716 plus the four digits of the stamped cap) instead of the dropped 19,188,
and §5's floor reads 0 against 6. The census line shows `refused 396` where the
clean run reads 388, and `size-drop 0`.

**S238 — the rung fires and says nothing.** The drop rung's term removed from
the `ESEL` arm; the artifact still ships and every answer is right. Measured:
`17 passed / 6 failed` — §6a's `wrongsel` arm fires on all three witnesses, and
**the census fires by a second, independent mechanism**: with the stamp gone,
the eight corpus artifacts fall back into the state-cap OVERFLOW bucket by
elimination, breaking its ceiling of 0. That is §5.1's fifth bucket
demonstrating exactly why it exists.

The two rows are separate rather than one edit with two hunks because their
symptoms are disjoint — S237's is a **refusal**, S238's is a **silence** — so a
check reading only "did it compile" passes S238 completely.

Anchor tripwire after both rows: `sabotages checked: 246 (259 anchor sites) /
all anchors resolve`.

---

## 10. Files changed

**Compiler.** `src/core/internal.h` (`Ctx.size_drop_rung`, the `SDR_*` enum,
the `ESEL_SIZE_CAP_RETRY` reachability correction), `src/core/compile.c`
(`build_anchored_dfa`'s rung read, the driver's local + seed + rung,
`COMPILE_MAX_ATTEMPTS`), `src/opt/select_engine.c` (the widened `ESEL` arm).

**Spec (D80).** `docs/spec/limits.md`, `docs/spec/tuning.md`,
`docs/spec/match_api.md`.

**Design.** `docs/design/anchored_match_unwrapped.md` §5.2a (new),
`docs/design/utf8_design.md` §3.3 (annotated REFUTED).

**Tests.** `tests/codegen/run_anchored_match.sh` (fifth census bucket + §6),
`tests/mech/sabotages/S237_*.sh`, `S238_*.sh`,
`tests/rxtsource/run_rxtsource_tests.sh` (both census pins),
`tests/utf8/axis04_p_categories.rxt` (+12), `tests/utf8/axis12_scripts.rxt`
(+4), `tests/known_fail/k53_uprops_oversize.rxt` (deleted).

**Process.** `docs/dev/known_issues.md` (K53 FIXED), `docs/dev/plan.md` (row
completed), `src/core/CLAUDE.md`, `src/opt/CLAUDE.md`,
`tests/known_fail/CLAUDE.md`, `tests/utf8/CLAUDE.md`, this report.

---

## 11. One residual I found and did NOT fix

`tests/utf8/CLAUDE.md`'s block census reads *"336 real / 219 `perr`"* summing
to 555, where `cat tests/utf8/*.rxt | grep -c '^pattern '` gives **577** and
`grep -c '^perr'` gives **67**. My change accounts for +16 of the 22-block gap
and none of the `perr` gap. The likeliest cause is [M5.0] stage 4's `fold.rxt`
plus promotions that turned `perr` blocks into live ones without moving the
sentence — but I did not investigate, because nothing this lane touched could
have caused it and quietly rewriting a number whose derivation I cannot
reproduce is how such a number goes wrong a second time. The measured pair is
recorded above the stale one, with the commands that produced it and an
explicit note that the split below does not reconcile.
