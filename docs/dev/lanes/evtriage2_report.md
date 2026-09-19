# evtriage2 — TRIAGE ROUND 2 on [EMIT-VERB]: the `make test` reds

Lane `evtriage2`, branch `lane/evtriage2` from `lane/evtriage` tip `26ef52ac`
(= `lane/emitverb`'s two events + evtriage's specimen fix). 2026-09-19, opus.

Scope: nothing under `src/`, `cli/`, `lib/` touched. Three test scripts and
this report. The evidence is the `make -k -j4 PROCS=3 test` running in
`worktrees/evtriage` at that same tip, launched 14:27 — this lane never
re-ran it and never touched that worktree.

---

## 0. THE TABLE — every FAIL in the full log

**The evidence run is COMPLETE**: `sections ran: 40/40`, `EV_MAKE_TEST_RC=2`,
**8 FAIL lines and no more**. The table below is the whole list, not a
snapshot — `grep -nE '^FAIL'` over the finished log returns exactly these
eight and nothing was added after the trailer landed.

| FAIL | class | disposition |
|---|---|---|
| `nm could not read arm_a.o (no rx_search symbol)` | **not yours** — standing darwin red, `docs/dev/wake.md` | none |
| `ir-listing[(a\|ab)(c\|bcd)]: the listing reports 1 island(s) but the artifact text contains no island at all` | **class 2** — the comment IS the instrument, no code-level twin | `45c70e8b` |
| `[M4.5c] a traced artifact carries no stamp saying so` | **class 1 + class 2 in one `if`** — split | `45c70e8b` |
| `§10: '^(a?)\1*b$' … the empty-iteration guard 0 time(s) … (S107)` | **class 1** — the guard has a slot declaration | `b03c94ef` |
| `§10: '^(a*)\1*$' …` | class 1 (same check, same commit) | `b03c94ef` |
| `§10: '^(a?)\1{2,}$' …` | class 1 (same) | `b03c94ef` |
| `§10: '^()\1+$' …` | class 1 (same) | `b03c94ef` |
| `'a{5,25000}' -fno-scan-edge -fno-start-pinned rescued at 762105 bytes, pinned 769835` | **stale pin the flip moved** — not a comment reader, not a regression | `bfb90bba` |

**Five distinct families, four of them this branch's and all four fixed.**
`rc=2` is fully explained by the standing `nm` probe alone once the other
seven lines are gone, which is the state `docs/dev/wake.md` already records
as "TEST_RC=2 on a green run".

Also present in the log and **not yours**, per evtriage's own rubric: the
`tests/thread` SKIPs, the resource suite's `sections skipped: 1`,
`run_recursion_identity.sh`'s (B) file pin (red by construction on any lane
branch until the manager re-pins at merge), and the three retired identity
gates.

---

## 1. THE ISLANDS TERM — class 2, and the reason is structural

`tests/codegen/run_ir_listing.sh` compares THREE surfaces per fixture: the
listing's `VE_ISLAND` event count, the artifact's `RX_VM_ALT_ISLANDS` stamp
(`Vm.nislands`, a different counter), and the emitted C's own text. The third
term is `grep -q 'island' gen.c`.

**Measured on `(a|ab)(c|bcd)`**: five `island` lines under `-fcomments`, zero
at defaults, and all five are `//` role lines written by `vm_rolef`. The code
an island emits is an ordinary first-byte `switch` over `subject[pos]` with
label targets — there is no token an island does not share with every other
dispatch in the program, and the one thing that IS island-specific,
`RX_VM_ALT_ISLANDS`, is already the block's SECOND term. So there is nothing
to convert to: this is D112's class (2) exactly, a per-site marker with no
code-level twin.

The repair generates a THIRD artifact per fixture, `$d/gen_cmt.c`, under
`-fcomments`, with **exactly one customer** — this term. Every other arm in
the loop reads a code-level surface (labels, `RX_PUSH` sites, `RX_SET` slots,
`#define` stamps) and still reads the default `$d/gen.c`, so no assertion
silently starts reading a non-default build. CALLOUTS is untouched: its
needle is code (`rx_callout_ref …(`, `->fn(`).

**The license was re-verified locally on this exact witness**, rather than
inherited from the branch's corpus-wide claim: `(a|ab)(c|bcd)` compiled both
ways and assembled at `-O1` gives **byte-identical object files**. So the
`-fcomments` build the term reads is the same program the default build is,
on the one artifact where that has to be true for the term to mean anything.

**Dropping the term instead was the alternative and it is worse.** The block
would then compare the event stream against the counter with nothing
witnessing the emitted C at all — and the block's own header says why that
matters, since the two remaining terms are both emitter-side bookkeeping.

### 1.1 The control, and it is a POPULATION guard

learnings.md §3 asks what would have to be true for a converted absence
assertion to fail. Here the term is a biconditional, and the answer is that
**fifteen of the sixteen fixtures exercise only its empty direction**. One
pattern, `(a|ab)(c|bcd)`, carries the whole other half. Edit that pattern, or
let the island lowering stop firing on it, and every per-pattern arm reads
green while the only term that looks at the emitted C stops being reached —
[MECH-REACH]'s shape.

So a sweep-wide arm asserts at least one fixture produces an island. **Pinned
as a FLOOR, not an equality**, so that adding an island-bearing fixture later
is not a failure. Measured 1 of 16 on this tree, and the check prints it:

    ir-listing: 1 of 16 fixtures produce an island, so the islands
    biconditional is exercised in BOTH directions

The `-fcomments` arm needs no separate liveness control of its own, because
it fails SAFE: if the flag stopped working, `art_isl` would read 0 on the
island-bearing fixture and the block would go RED, not green.

---

## 2. `[M4.5c] TRACED ARTIFACT` — one `if`, two classes, so it SPLIT

The check required, of ONE default build, both `#define RX_TRACE 1` and the
`TRACED ARTIFACT` prose block. **The stamp was there the whole time**; only
the prose went. A single `&&` had bound a code-level fact to a comment, and
the failure message — *"a traced artifact carries no stamp saying so"* —
named the half that was fine.

- The **stamp** is unconditional, so D37's claim is now asked of the DEFAULT
  artifact and is STRENGTHENED: `--trace` is unambiguous with no emitted
  comment at all, which is what a caller building at defaults needs.
- The **prose** is NON-ESSENTIAL by D112 item 2 — precisely the class the
  flip removes — so its own arm asks for it under `-fcomments`, keeping the
  claim that the artifact also explains itself to a human reading it.
- A **third arm** asserts the DEFAULT build does NOT carry the prose. Without
  it, a compiler that ignored the comments axis entirely would read green on
  both arms above, which is the vacuity the conversion could have introduced.

---

## 3. §10's GUARD — class 1, the strongest kind

`tests/backrefs/run_backref_diff.sh` §10 counted the role-text phrase
`empty-iteration guard`. It read zero on every fixture, and **all four
guard-bearing rows failed naming sabotage row S107** — the exact regression
the section exists to catch, produced by a check that had gone blind. That is
the shape worth recording from this round: *a comment reader does not fail
vaguely; it fails as the defect it was written for.*

The twin is written under the same condition that writes the phrase
(`src/gen/emit_vm.c`, `vm_star`):

    bool guard = vm_nullable(a->l);
    int gslot = guard ? vm_slot_guard(v, v->nguard++) : -1;

The guard exists iff the slot is assigned, and the slot is emitted as its own
`#define <PREFIX>_SLOT_EMPTY_GUARD<n>` line. Counting the declaration is the
STRONGER reading — a comment about a slot is one remove from the slot — and
the count is still exactly one per guard.

**The population did not have to be re-based**, which is what makes the
conversion checkable. Measured at this tree, default axes, over all seven
fixtures:

| fixture | want | `#define …SLOT_EMPTY_GUARD<n>` |
|---|---|---|
| `^(a?)\1*b$` | bear | 1 |
| `^(a*)\1*$` | bear | 1 |
| `^(a?)\1{2,}$` | bear | 1 |
| `^()\1+$` | bear | 1 |
| `^(a?)\1{3}$` | free | 0 |
| `^(a)\1{2}$` | free | 0 |
| `^(a?)(?:\1){2}x$` | free | 0 |

— identical to the phrase's own historical 4/3/7 under comments-on.

---

## 4. THE RESOURCE PIN — not a comment reader at all

`tests/resource/run_resource_tests.sh`'s [K59-PREMUL] cell pins the rescued
artifact's size as a raw `wc -c`, which is **comment-INCLUSIVE**, while the
cap the cell is about (`PCREC_MAX_EMIT_BYTES`) is comment-EXCLUDED. D112 item
3's guarantee that no comment setting can rescue or refuse a pattern is
intact and is exactly what makes this a pin move rather than a finding:

| build | bytes |
|---|---|
| default (comments off) | 762,105 |
| `-fcomments` | 769,838 |
| old pin | 769,835 |

and the compiler's own note still reports the same 12,636 code bytes.

**AND THE SAME LOG CARRIES AN INDEPENDENT CONFIRMATION** that nobody had to
construct: the two rows of the refusal loop immediately above this cell print
the CAP's own byte figure, and in this comments-off run they read 1,034,778
and 1,335,605 — the numbers they have always read. If the cap counted comment
bytes, a 36% source reduction would have rescued both patterns and both rows
would have gone red as ACCEPTED. They passed. So the cap is comment-invariant
by measurement in the very run that moved the pin, which is what separates
"the instrument moved" from "the thing being measured moved".

This is `battriage_report.md`'s **SECOND READER CLASS** — a pin citing no abi
digit, no comment and no axis, whose VALUE moves anyway — so the D76/D94 grep
sweep over the old abi number structurally could not reach it. Third recorded
instance, and the second one this axis produced: the emitverb lane
re-recorded `run_cpset_structure.sh`'s twelve `EMITTED_BYTES` rows for the
same reason, and this cell is not in that manifest.

**The two-byte gap between the failure message (762,105) and a naive re-run
(762,107) is the `-o`-basename trap**, fourth recorded instance
(`dd8_report.md` §3.1): the emitted `#include "<basename>.h"` makes the byte
count basename-sensitive, and the re-measurement had to use this cell's own
`o.c`. A lane re-pinning from a differently-named scratch file would have
pinned a number the check can never produce.

**Considered and declined**: making the pin read the comment-EXCLUDED count
(`tests/lib/size_count.sh`'s `size_count_row`) so it is invariant under this
axis. That changes what the cell measures, nobody chartered it, and the
cell's own failure message prescribes re-measure-and-re-pin. Named here as a
candidate, not taken.

---

## 5. Validation

| what | result |
|---|---|
| `tests/codegen/run_ir_listing.sh` | **147 passed / 0 failed**, rc 0 (was 144 / 2) |
| `tests/backrefs/run_backref_diff.sh` | **12 passed / 0 failed**, rc 0 (was 11 / 4) |
| `tests/resource/run_resource_tests.sh` | **27 passed / 0 failed**, 1 section skipped (the standing darwin `ulimit -v` skip), rc 0 |
| `make test-codegen` | rc 2, and the **sole FAIL is the standing darwin `nm` probe** — every constituent script green (22/0, 31/0, 7/0, 14/0, 13/0, 9/0, **65/0** for `run_comments_axis.sh`) |
| `tests/registry/run_registry_tests.sh` | **rc 0, zero FAIL lines**: 225/0, PC-3 209/0, PC-4 273 patterns / 62,872 match cells / **0 disagreements**, 108/0, 24/0, 54/0, definitions-oracle 354 cells / 101,244 + 101,244 comparisons / **0 disagreements** |
| sabotage `S107`, solo | **DETECTED** — `1 rows (unexpected: 0, undetected: 0, unreached: 0, anomalies: 0, oracle-skipped: 0)`, rc 0 |
| the evidence `make test` | `sections ran: 40/40`, rc 2, **8 FAIL lines**, all in §0 |

**The backrefs count reconciles exactly and that is the check on the
conversion**, not the green itself: §10 emits one `ok` for the whole
population and one `bad` PER FAILING FIXTURE, so 11 passed + 4 failed
collapses to 11 + 1 = 12 passed. No check was added, removed, or made
vacuous.

### 5.1 One pre-existing drift found while validating, NOT fixed here

`S107`'s `SAB_DOC_FIGURE` records *"Clean tree: numeric.rxt 88/0, brefdiff
11/0"*, measured 2026-08-22. `run_backref_diff.sh` reads **12/0** on a clean
tree today, and the extra check is §9b — the `utf8` fold-agreement arm
[M5.0] stage 4 added on 2026-09-08, three weeks after the figure was taken.
So the drift predates this branch and has nothing to do with the comments
axis or with this conversion. Left alone deliberately: a `SAB_DOC_FIGURE` is
a DATED measurement record, and re-stamping it with today's number inside a
triage commit would erase the only evidence of when it was last actually
run. Flagged for the manager as a one-line re-record if wanted.

The 16 `irsb` byte-neutrality baselines were **not** recaptured and must not
be: nothing here touches `--emit-ir`'s output, and `run_ir_listing.sh`'s own
byte-neutrality block passing on all 16 is the proof.

---

## 6. NOTHING IS OWED — and the triage order if the axis produces another red

Every item this report marked OWED has run and is recorded in §5's table.
The evidence run's trailer landed at `sections ran: 40/40` with eight FAIL
lines, exactly the five families §0 covers; **nothing new arrived after the
snapshot the work was done from.**

**S107 is the one that had to come back green in the FAILING direction, and
it did.** The plant makes `vm_nullable` answer FALSE for `A_BREF`; the slot
is then never assigned, the converted count reads 0 exactly as the phrase
did, and the row scores DETECTED with `brefdiff: 4fail/11pass` — the same
four §10 failures the phrase produced. The conversion did not soften the
detector.

**What a fresh reader does if the comments axis produces another red.** Ask
D112's question in this order:

1. Does the fact have a `#define RX_*`, an `rx_info` field, or another
   code-level artifact? Read it. (§3 is the worked example, and note that the
   twin is usually written under the SAME `if` as the comment — that is what
   makes it the same fact rather than a proxy.)
2. Is the comment itself the thing under test, or the only instrument at that
   resolution? Pass `-fcomments` for that term ALONE, generating a separate
   artifact rather than switching the shared one, and say why at the site.
   (§1.)
3. Does the check bind a stamp to a comment with one `&&`? SPLIT it — the
   failure message will have named the half that was fine. (§2.)
4. Is it a pin whose VALUE moved with no comment, axis or abi digit in its
   text? Re-measure with the check's OWN `-o` basename and re-record. (§4.)

**No gap D112 created was found, and that is a result rather than an
absence.** The brief allowed for a fact that used to be readable and is now
readable in no form, with a one-line `#define` stamp riding the open abi 27
bump as the remedy. The traced-artifact red LOOKED like exactly that and was
not: `RX_TRACE 1` was present throughout. So **no stamp was built and the
abi 27 bump takes no rider from this lane**, which also means no D94 grep
sweep and no identity re-pin are owed on its account.

---

## 7. Commits

- `45c70e8b` — `run_ir_listing.sh`: the islands term on a `-fcomments`
  artifact with its population floor, and the traced-artifact split.
- `bfb90bba` — `run_resource_tests.sh`: the [K59-PREMUL] pin, 769835 ->
  762105.
- `b03c94ef` — `run_backref_diff.sh` §10: the guard read off its slot
  declaration.
- `eb92ba2f` — the two directories' `CLAUDE.md` entries.
- this report.

## 8. One thing the manager may want, and it is one line

`S107`'s `SAB_DOC_FIGURE` records `brefdiff: 4fail/10pass` sabotaged and
`brefdiff 11/0` clean, measured 2026-08-22. The solo re-drive here reads
`4fail/11pass` and a clean tree reads `12/0` — **+1 on both sides**, which is
§9b, the `utf8` fold-agreement arm [M5.0] stage 4 added on 2026-09-08. The
drift predates this branch and is unrelated to the comments axis or to this
conversion. Deliberately not re-stamped: a `SAB_DOC_FIGURE` is a DATED
measurement, and rewriting it inside a triage commit erases the only record
of when it was last actually run. If it should carry today's figures, the
replacement is `corpus:9fail/79pass, brefdiff:4fail/11pass` sabotaged and
`numeric.rxt 88/0, brefdiff 12/0` clean, measured 2026-09-19 at `eb92ba2f`.

## 9. Rulings received

None. Nothing in this lane's work was blocked, and no question was sent
beyond the interim status message to the manager.
