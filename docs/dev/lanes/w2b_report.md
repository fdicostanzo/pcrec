# [REVW.2] WAVE 2, SLICE C — EP2 step 11 / lens 10 STAGE 3, the fragment retirement

Lane `w2b` (opus, 2026-09-18), branch `lane/w2b` off `main` at `7f0d6cbf`
(which carries the w2a merge `0dd6d29c`). Charter: the brief's items 0–3 —
widen `run_ir_listing.sh`, land `sb_fragf`, retire the fixed scratch buffers
over BOTH emitters, re-aim the anchors.

**Nine commits. The census reads 7 declarators where `w2census.md`'s floor
was 91, and every one of the seven is on the named exclusion list below.
Every batch is byte-neutral on three independent artifact streams.** No
commit is an `abi` event: not one emitted byte moved, so no bump, no
identity re-pin, no `docs/spec/` hunk is owed.

---

## 1. The commits

| # | commit | what | declarators retired | anchors re-aimed |
|---|---|---|---:|---:|
| 0 | `82e73fc4` | widen `run_ir_listing.sh` 11 → 16 patterns, per-row `--features`; repair its resume-point block | — | 0 |
| 1 | `be7b64f8` | `sb_fragf` + `tests/core/sb_fragf_check.c` | — | 0 |
| 2 | `7b528fb3` | `sb_fragfv`; `vm_rolef`; the slot-naming family | **11** | **1** (S114) |
| 3 | `c116ecea` | `vm_cut`, `vm_isl_die`, `vm_cursor_rep`, `vm_rev_emit` | **11** | **1** (S37) |
| 4 | `bfcc4ff5` | `vm_revdet_rep` | **10** | 0 |
| 5 | `3beb364f` | the remaining `emit_vm.c` rung + listing sites | **13** | **3** (S106, S143, S53) |
| 6 | `5ae6a4a4` | `dfa_fragf`; `emit_dfa.c`'s name builders | **15** | **1** (S74) |
| 7 | `4bb5c94c` | `emit_dfa.c`'s remaining formatted scratch | **9** | 0 |
| 8 | `288068d2` | `pcrec_emit_vm`'s own scratch | **9** | 0 |

**Census** (`tools/review/fragment_census.py`, both files, the repaired
criterion — ANY size expression, `Vm.up` excluded by name):

| point | statements | declarators |
|---|---:|---:|
| `w2census.md`'s floor at `f6474777` | 80 | 91 |
| this lane's branch point (after w2a) | 70 | 81 |
| batch 2 | 61 | 70 |
| batch 3 | 50 | 59 |
| batch 4 | 44 | 49 |
| batch 5 | 32 | 36 |
| batch 6 | 21 | 24 |
| batch 7 | 13 | 15 |
| **batch 8 (delivered)** | **6** | **6** |

(The table's own numbers exclude `Vm.up`; the tool's raw totals are one
higher in both columns at every row, and the commit messages quote the raw
form. **75 of the 81 declarators this lane inherited are retired**; the other
six are §2's named family. w2a's slice accounts for the 91 → 81 step.)

---

## 2. ACCEPTANCE: the exclusion list, seven declarators, two reasons

The census does not read zero. It reads 7, and every one is here with its
reason — no silent residue.

| site | buffer | reason |
|---|---|---|
| `src/gen/emit_vm.c:376` | `Vm.up[80]` | **lens 10's own SCOPE NOTE.** A struct FIELD read at ~110 sites; retiring it is a data-flow change through the emitter's central struct, not a text change, and does not share this stage's byte-neutrality argument. Explicitly out of wave 1, and `w2census.md`'s repaired criterion already excludes it BY NAME. |
| `src/gen/emit_dfa.c:495` | `g[256]` | destination of `pcrec_enc_start_guard`, an `enc.h` SEAM ENTRY |
| `src/gen/emit_dfa.c:6662` | `sbnd[256]` | second direct call site of that same seam entry |
| `src/gen/emit_vm.c:11347` | `retry_adv[1024]` | destination of `pcrec_enc_advance`, the same seam |
| `src/gen/emit_dfa.c:529` | `t[..GUARD_TEXT_MAX]` | destination of `pcrec_startpos_guard_text`'s rendered text |
| `src/gen/emit_dfa.c:7217` | `probe[..GUARD_TEXT_MAX]` | same |
| `src/gen/emit_vm.c:11611` | `mguard[..GUARD_TEXT_MAX]` | same |

**The last six are ONE family and the reason is structural, not a
preference.** Three of them are the output buffers of `enc.h` seam entries
whose `buf` + `cap` + `trunc` contract belongs to the ENCODING MODULE
(DD-12), not to this stage; each already turns a would-be truncation into a
loud `ctx_fail`, and `retry_adv`'s own comment records that its guard FIRED
during bring-up at 512, so it is measured rather than assumed. The other
three hold the text `pcrec_startpos_guard_text` renders, and that text
contains only the caller's INDENT and the backend's own expression — **never
the `-p` prefix** — which puts the whole family outside the K38 class this
stage exists to retire. `src/core/limits.def:360` already says exactly that:
"sized by the ENCODING BACKEND's own guard text, not by the pattern."

One further reason not to take them here: retiring `t`/`probe`/`mguard`
leaves `PCREC_STARTPOS_GUARD_TEXT_MAX` with no reader while its
`--list-limits` note still names *"four call sites in the two emitters"*.
Correcting that note is a caller-observable dump change (D80) carrying its
own spec hunk, which this stage's not-an-`abi`-event charter excludes. §7
files it as the next unblocked step.

---

## 3. Byte-neutrality: three streams, every batch

All three run against a **pinned branch-point binary** built from
`git archive 7f0d6cbf` — a reference that does not move as the lane edits.
Rebuilt from `w2a_report.md` §2; the driver is
`…/scratchpad/w2b/sweep.py` (instrumentation, not a deliverable).

| stream | population | per batch |
|---|---|---|
| corpus argv sweep, `.c` at default engine | 3,938 rows (3,517 compile) | **BYTE-IDENTICAL** |
| corpus argv sweep, `.c` at `--engine=vm` | 3,938 rows (3,518 compile) | **BYTE-IDENTICAL** |
| corpus argv sweep, `--emit-ir` listing | 3,938 rows (3,518 compile) | **BYTE-IDENTICAL** |
| composition sweep, `--source` over every `.rxt`/`.rxtin` | 304 files, 32 producing artifacts | **BYTE-IDENTICAL** |

The **composition arm is mandatory and it is not redundant**: `vm_splice`'s
DELIVER block is gated on `a->u.call.deliver_n`, written only by
`src/parse/rxt_compose.c`, and no corpus `.rxt` declares an `export` —
w2a measured 0 of 3,938 argv rows reaching it against 2 of 304 source files.
This lane's batch 2 touched `vm_slot_ref`, which that block calls.

Plus, every batch: `make strict` clean; `run_ir_listing.sh` **128 passed /
0 failed**; anchor integrity **282 records across 266 rows, 0 mismatches**.
`make test-codegen` was run at batch 1: **8 of 9 scripts**, the sole FAIL
being `run_inline_capability.sh`'s `nm could not read arm_a.o`, the standing
darwin red recorded in `docs/dev/wake.md` and reproduced by w2a at its own
branch point.

### 3.1 `vm_rolef`'s truncation removal, measured BEFORE the edit

`vm_rolef` is the one buffer the charter names as *"the same function
already, built on a `char buf[160]` and **truncating anyway**"*. Removing
that truncation makes a long role come out LONGER, which is a byte move. So
it was measured first, with a probe printing `n` at every call over the whole
corpus at BOTH prefixes, `--features all`, default engine and forced VM:

| prefix | compiles | truncating calls | longest role |
|---|---:|---:|---:|
| `-p rx` | 7,876 | **0** | 135 |
| a legal 60-byte prefix | 7,876 | **0** | 135 |

25 bytes of margin, identical at both prefixes — the longest role carries no
prefix. This independently confirms lens 10 §4.1's "no fragment provably
truncates" for the single buffer the charter flagged as the exception.

---

## 4. Anchors

**The instrument** (rebuilt from w2a §3, `…/scratchpad/w2b/anchors.py`):
source every `tests/mech/sabotages/S*.sh`, count its `SAB_BEFORE`/
`SAB_BEFORE2` in the current tree with the same whole-file `content.count()`
the applier uses, compare to `SAB_COUNT`/`SAB_COUNT2`. **282 records across
266 rows**, 0 mismatches at the branch point — reproducing w2a exactly.

**POPULATION BY GREP ON THIS TREE**, never cited from EP2:

| | records | rows |
|---|---:|---:|
| `SAB_FILE`/`SAB_FILE2` = `src/gen/emit_vm.c` | 95 | 86 |
| `SAB_FILE`/`SAB_FILE2` = `src/gen/emit_dfa.c` | 29 | 28 |
| **both emitters** | **124** | **114** |

### 4.1 Six re-aims, all measured in both directions

Each break was found by running the gate after the edit (so exactly which
row broke is a measurement, not a prediction) and the gate re-run after the
re-aim (so nothing else moved). Every row carries a dated `RE-AIMED` note
saying which batch moved it and that the plant and intent are unchanged.

| row | batch | what moved | driven solo |
|---|---|---|---|
| `S114-resolution-first-by-number` | 2 | its anchor's SECOND line was `char ns[144], ne[144];` | **DETECTED** |
| `S37-vm-wrong-span` | 3 | the `snprintf` continuation line now ends `,` not `);` | **DETECTED** |
| `S106-caseless-field-ignored` | 5 | `snprintf(fn, …)` became `fn = vm_rolef(…)` | **DETECTED** |
| `S143-call-return-no-restore` | 5 | the restore loop lost its `char val[192]` | **DETECTED** |
| `S53-counter-untrailed` | 5 | the anchored `vm_set` call carries the value expression | **DETECTED** |
| `S74-reverse-termination-blind` | 6 | `fold_arg` needs no caller buffer | **DETECTED** |

Verdicts, cells and the final-SHA re-drive are in §6.

### 4.2 Two re-aims that needed thought, not substitution

**`S37` keeps its COUNT-2 property, and the anchor keeps a 21-space prefix
to do it.** The row's own note says the defect exists in BOTH cursor
emission paths and that a plant reaching only one "would leave the other
silently unmeasured". `replace.py` matches a whole-file SUBSTRING, not a
line, and the two arms sit at different depths (32 and 28 spaces today, 25
and 21 before) — so the single anchor matches both only because it carries
the SHALLOWER arm's indent and is therefore a suffix of the deeper line too.
An anchor re-aimed to either arm's own column would have matched once and
quietly halved the row. Verified still `count=2`.

**`S53`'s AFTER had to change, not just its BEFORE.** The row replaces a
trailed `vm_set` with a plain untrailed store carrying the SAME value text —
and that text used to be the variable `val`. With the buffer gone, the AFTER
spells the value expression inline, so the plant stays identical in
substance rather than merely compiling.

### 4.3 What EP2 and the charter got wrong about the anchors

The charter's STAGE 3 section predicts *"Directly broken: 4 anchors in 4
rows"* and names them: `S106`, `S114`, `S143` and `S74`. **Measured: six
rows broke — those four exactly, plus `S37` and `S53`.**

The two it missed share a shape the prediction's own rule cannot see. The
charter counted rows *"quoting an `snprintf` or a `char NAME[…]`
declaration"*. `S37` quotes an ARGUMENT LINE of such an `snprintf` (not the
call's first line, and not the declaration), and `S53` quotes the CONSUMER —
a call that passes the buffer VARIABLE, which moves the moment the variable
becomes an inline expression. So the generalisable form:

> **A buffer's blast radius is not the lines that MENTION the buffer. It is
> the whole statement that writes it, every continuation line of that
> statement, and every call that reads the variable — because retiring a
> buffer replaces a NAME with an EXPRESSION at each of its readers.**

Predicted "blast radius requiring re-verification: 123"; measured 124
records across 114 rows in the two emitters, of which **6 (4.8%) broke
directly** and the rest were verified untouched by the gate on every batch.

**`S74`'s own history is the argument for the whole stage.** It carries FIVE
dated re-anchoring notes, four caused by a caller-sized buffer moving — and
one, `[CC-DIFF]` STEP 1(b) on 2026-09-03, caused by the `char ab[…]` local
being *added* to hold `fold_arg`'s result. This change deletes that local
again.

---

## 5. What EP2 / lens 10 / the brief got wrong about the tree

The `w1kit_report.md` §8 shape: short, so a later lane carries it.

1. **The listing-reach gap was the INSTRUMENT, and the reach target is
   stale.** The brief says "target reach 39 of 41 `vm_rolef` sites". On this
   tree the population is **44** (w2a's slice added sites), and the widened
   arm reaches **42 of 44** — measured 30 of 44 before. The residual 2 are
   `vm_counter_phase`'s two role texts, whose format strings begin with a `%`
   conversion and so present an EMPTY literal-prefix needle to the census's
   own hit test: instrument-blind by construction, closed by a different
   instrument and never by a longer array. Recorded in the array's own
   comment so a later lane does not hunt for the two patterns.
2. **The widening immediately found TWO defects in the resume-point check,
   neither reachable by the old eleven patterns.** Its `.c` side counted
   `&&rx_L<n>` ANYWHERE, and `RX_CALL(&&rx_L<n>, …)` has that spelling too —
   a call RETURN address, which `vm_count_slots`'s `A_CALL` arm deliberately
   does NOT charge to `npush` — so module `recursion` read 4 against a
   correct pre-pass of 2. And it asserted EQUALITY where the cap's soundness
   is an INEQUALITY: `v->npush` is an ESTIMATE (`emit_vm.c:7230` says so, and
   the `[CC-CLANG]` fix records it measured NEGATIVE), the hazard the block
   names is an UNDER-count, and `(?<=a|bc)x` is a witness where the estimate
   is legitimately high (2) and the artifact correct (1) — with `(?<!a|bc)x`
   (3 vs 2) a second off-sweep witness against three lookbehind shapes where
   it is exact. **The equality held for eleven patterns by luck of
   population.** Repaired to `pre-pass >= emitted`, reporting the slack.
3. **`sb_fragf`'s no-truncation promise is enforced by the SIZE ARGUMENT,
   and the exactness of the ALLOCATION is unobservable.** Two plants were
   tried against `tests/core/sb_fragf_check.c`. A wrong `vsnprintf` size
   turns 5 of its 6 sub-checks red. An allocation one byte short moves
   NOTHING — not the check, and not AddressSanitizer: `arena_alloc` rounds
   every request to 16 and zeroes the slice, so the terminator lands in
   already-zero storage, and ASan sees only the arena's own 64 KiB block
   `malloc`, never the intra-block slice bounds. A standalone
   `-fsanitize=address` probe over lengths 0..599 reported "content correct
   at every length" against BOTH builds. Recorded in the check's header, in
   `coding_guide.md` §2.2 and in both CLAUDE.md files, because the natural
   reading of "sized exactly to the result" is that both halves are checked
   and only one of them is.
4. **A FIFTH hand-rolled slot-ref.** `vm_cap`'s publish-at-close built
   `slot_values[` + `vm_slot_expr` + `]` by hand — exactly what `vm_slot_ref`
   builds. EP2's E1 retired four such sites and all four were in
   `vm_call`/`vm_splice`, so this one was never reached by w2a's grep.
5. **The `-Wformat-truncation` second-order sizing.** Two `vm_revdet_rep`
   buffers carry a comment saying they were widened *"not because their real
   content grew"* but because gcc sizes an argument's worst case off ITS
   buffer CAPACITY — so a destination had to cover a worst case nothing ever
   produces, purely because its SOURCE was a fixed buffer. That whole class
   of widening disappears with the buffers; an arena fragment has no
   capacity to propagate. Neither EP2 nor the charter names this cost.
6. **Not every buffer is a format.** `emit_header`'s include guard is a
   per-byte transform (`isalnum ? toupper : '_'`) whose loop carried its own
   truncation bound; what it needed was an allocation the INPUT sizes, not a
   fragment. And `vm_cls_describe`'s `a[8]`/`b[8]` were written through a
   `char *dst = k ? b : a` alias, which arena fragments cannot be.
7. **The two CLAUDE.md-visible signature facts.** `DfaForm.cx`'s comment
   said "for `ctx_fail` alone" and cannot any more; `emit_stay_table` gained
   a `Ctx` parameter. Both are consequences of the retirement, not of taste.

**HELD:** the charter's `sb_fragf` design (signature, semantics, arena
ownership, the `ctx_nomem` route) verbatim; its "NOT an `abi` event, and if
a byte moves the stage has a bug" verdict (measured on three streams per
batch, not assumed); its JUDGED/MECHANICAL split, with the conditionally-
written `""`-default sites named correctly in advance; its per-call-site
rollback shape; its four predicted anchor rows, all four of which did break;
and its decision that `Vm.up` stays.

---

## 6. Validation — what is COMPLETE and what is OWED

**COMPLETE at handback:**

- Per batch (all 8): corpus argv sweep 3,938 × 3 streams BYTE-IDENTICAL;
  composition sweep 304 files / 32 producing artifacts BYTE-IDENTICAL;
  `run_ir_listing.sh` 128/0; `make strict` clean; anchor integrity 282/266
  with 0 mismatches.
- `make test-codegen` at batch 1: 8/9, the FAIL set identical to the
  standing darwin baseline.
- `tests/core/run_core_tests.sh`: **2 passed / 0 failed** (6 `sb_fragf`
  sub-checks green), with the two-plant failing-direction transcript in §5.3.
- Item 0's sabotage verification, both directions: a one-byte change in
  `vm_look_behind`'s per-branch role text takes the widened arm RED
  (127 passed / 1 failed, naming the lookbehind row and quoting the byte)
  while the pre-widening arm at `HEAD` stays GREEN (93/0). Plant removed;
  `git diff` on `src/gen/emit_vm.c` empty.
- Interim solo mech runs, each `unexpected: 0, undetected: 0, unreached: 0,
  anomalies: 0`:

| row | at | cells |
|---|---|---|
| S114 | `7b528fb3` | `dupnamesdiff:5fail/1pass, corpus:26fail/62pass` |
| S37 | `c116ecea` | (DETECTED) |
| S106 | `3beb364f` | `codegen:7fail/107pass, brefdiff:12fail/4pass, corpus:21fail/14pass` |
| S143 | `3beb364f` | `corpus:110fail/1580pass, recdiff:121fail/8pass` |

**OWED**, and launched as the lane's last act per `BOILERPLATE.md`'s
DO-THEN-FINISH:

- **All six re-aimed rows re-driven SOLO at the FINAL SHA.** Log:
  `…/scratchpad/w2b/mech_final.log`. Completion line to look for:
  `== mech run COMPLETE: 1 rows (unexpected: 0, …) at <final SHA> ==`,
  six times. The criterion is the driver's own `unexpected: 0` /
  `anomalies: 0`, read against each row's `SAB_EXPECT` — all six default to
  DETECTED and all six were DETECTED on their interim runs; `S53` and `S74`
  have not yet been driven at all and are the two to watch.
- The full battery is the manager's at merge, as always.

---

## 7. The NEXT unblocked step

**EP2 sequence step 10 — X8, the stamp pair, 52 sites in `emit_vm.c` and 21
in `emit_dfa.c`.** EP2 places it AFTER stage 3 because it depends on
`sb_name`/`sb_upper`, and the brief asks whether stage 3 naturally produced
them. **It did not, and deliberately.** `sb_fragf(arena, "%s_%s", p, s)` and
`sb_fragf(arena, "%s_%s", up, s)` are what every site here needed;
`sb_name`/`sb_upper` add nothing over that except a NAME for the convention,
and their stated purpose in the charter is to make the uppercased prefix ONE
derived fact — which is a `Vm.up` retirement, explicitly out of wave 1. So
step 10 should land them on its own terms, as the substrate for the stamp
helpers, and X8 remains the only item in the sequence with an `abi` question
attached.

**A second, smaller item this lane opened:**
`PCREC_STARTPOS_GUARD_TEXT_MAX`'s `--list-limits` note names "four call
sites in the two emitters" and will be wrong the day the exclusion list's
last three buffers are retired. Retiring them plus correcting that note is
one small commit with its `docs/spec/` hunk (D80) and its
`--list-limits`-reader re-pins — a contract change, deliberately not folded
into a stage whose whole claim is that nothing observable moved.

**Rollback.** Nine independent commits, each mergeable on its own in order.
Reverting batch 2, 3, 5 or 6 requires reverting its anchor re-aims with it.

---

## 8. Rulings received

None — no ruling was requested or issued during this lane's run.
