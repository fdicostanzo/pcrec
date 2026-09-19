# [REVW.2] WAVE 2, SLICE D — EP2 step 10 / lens 1 X8, THE STAMP PAIR

Lane `w2x` (opus, 2026-09-18), branch `lane/w2x` off `main` at `fa70bf84`
(which carries the w2b merge `c87c7919`). Charter: EP2 sequence step 10 —
the hand-typed `#define %s_…` emission sites in `src/gen/emit_vm.c`
replaced by one helper, `Vm.up` taken if it falls out.

**Eight commits. X8 is COMPLETE ACROSS BOTH EMITTERS — 73 of 74 stamp sites
retired, one named residue. `Vm.up` IS RETIRED and the fragment census reads
6. Every batch is byte-identical on four independent streams, so NO `abi`
event: no bump, no identity re-pin, no `docs/spec/` hunk is owed.**

---

## 0. THE HEADLINE FINDING: "52 sites" is 52 LINES over 44 STATEMENTS

EP2 §2.1 reports X8's `emit_vm.c` population as *"confirmed EXACT — 52
`"#define %s_` format literals, all 52 at line ≥ 8539"*, and lens 11 and the
synthesis each re-confirm the number independently. **The number is right and
what it counts is not what step 10 can convert.** `grep -c '#define %s_'`
counts LINES. Walking each hit back to its statement:

| | statements | `#define %s_` lines |
|---|---:|---:|
| **VALUE stamps** — `#define <UP>_NAME <value>`, one line | **37** | 37 |
| **FUNCTION-LIKE MACROS** — multi-line bodies with `\` continuations | **7** | **15** |
| total | **44** | **52** |

The seven are `_TIER_NOTE` (4 lines: an `#ifdef`/`#else` pair), `_CHARGE_WORK`,
the `_PRUNE_TOO_SHORT`/`_PRUNE_CLAMP_SPAN` pair, the two `_TRAIL`/`_SET`/
`_PUSH`/`_CUT` spellings (plain and tracing, 4 lines each) and the two `_CALL`
spellings. **Their emitted text is a PROGRAM, not a value**: a
`sb_stamp_str(c, up, "CHARGE_WORK", …)` is not a thing that can exist.

So X8's real `emit_vm.c` population is **37**, and the report of 52 makes the
step look 40% larger than it is while hiding that 15 of those lines are
untouchable. The count was verified three times by three readers and never
decomposed, which is this tree's own recurring shape: *a census that counts
the RIGHT thing can still be counting a different UNIT than the work item
that cites it.*

**And it explains EP2's anchor figure.** Its table gives step 10 "4 abutting"
anchors. Measured: **three** sabotage rows (S224, S225, S226) anchor on a
stamp line, and all three anchor on the SAME ONE — `_VM_FRAMELESS`. The four
rows that DO sit in the stamp block's span (S89, S155, S168, S182) are all on
the function-like macro statements, which this step must not touch. EP2 almost
certainly counted anchors inside the SPAN rather than anchors on convertible
lines; the two answers differ because the span contains both kinds.

---

## 1. The commits

| # | commit | what | sites | anchors |
|---|---|---|---:|---:|
| 1 | `576b936d` | the primitives + `tests/core/sb_stamp_check.c` | — | 0 |
| 2 | `f3a4d589` | `emit_vm.c`'s string-valued stamps | **11** | 0 |
| 3 | `d506c281` | `emit_vm.c`'s integer / hex / suffixed stamps | **19** | 0 |
| 4 | `8d7f9128` | `_VM_FRAMELESS`, alone | **1** | **3** (S224, S225, S226) |
| 5 | `d35df1a5` | the `_R_*` sentinel family + `_CALL_TOP_NONE` | **6** | 0 |
| 6 | `f49aa988` | `sb_upper`; `Vm.up` and `GenNames.upper` retired | — | 0 |
| 7 | `4602b773` | `emit_dfa.c`'s stamps — X8 complete | **20** | 0 |
| 8 | `3fd6d688` | coding_guide §2.6, `src/gen`/`src/core`/`tests/core` CLAUDE.md | — | — |

37 (`emit_vm.c`) + 20 (`emit_dfa.c`) = **57 sites converted**, against lens 1
X8's census of 73 — the difference being the 15 macro lines above and the one
residue in §4.

---

## 2. What was built, and the three places the charter's design did not survive contact

```c
void sb_stampf  (StrBuf *c, const char *upper, const char *name,
                 const char *valfmt, ...)            /* format(printf,4,5) */
void sb_stampwf (StrBuf *c, const char *upper, const char *name, int namew,
                 const char *valfmt, ...)            /* format(printf,5,6) */
void sb_stamp_str(StrBuf *c, const char *upper, const char *name,
                  const char *value);
const char *sb_upper(Arena *a, const char *s);
```

Three entry points over one file-static body (`sb_stampv`), plus a file-static
`sb_vprintf` split out of `sb_printf` so the stamps reach it through a
`va_list` — `sb_fragf`/`sb_fragfv`'s own shape, one destination over, rather
than a third copy of measure-grow-format. No new public surface for either
static.

**(a) THE TYPED PAIR IS REFUTED BY THE EMITTED TEXT.** Lens 1 X8 proposes
`emit_stamp_str(…, const char *value)` / `emit_stamp_int(…, long long value)`
and the lens 10 charter adds `_bool`. A stamp's value is EMITTED C, so its
spelling is part of the contract. `emit_vm.c`'s 37 value stamps use **seven**
spellings — `%d`, `%lld`, `%llu`, `%lluULL`, `%lldLL`, `0x%xu` and a bare `1` —
plus six raw C expressions (`((ptrdiff_t)PCREC_ERR_STEPS)` and its family).
`%lluULL` and `0x%xu` are not renderings of a number; they are tokens with
meanings to the artifact's own compiler. A typed integer helper covers **9 of
37** and silently moves the emitted bytes of the other 10 numeric ones. So the
value is a FORMAT, the NAME is the literal argument a grep enumerates, and
`sb_stamp_str` exists only because QUOTING is a real shared decision (11 sites
in `emit_vm.c`, 9 more in `emit_dfa.c`).

**(b) `sb_stampwf` IS NOT IN EITHER DESIGN AND THE TREE REQUIRES IT.** Two
stamp families align their value column by typing a different number of spaces
into each format string: the five `_R_*` sentinels (`_R_STEPS` three spaces,
`_R_FRAMES` two, `_R_WORK` four, `_R_RECURSE` one, `_R_INTERNAL` one-by-
overflow) and the per-slot table at `%-24s`. That is one fact — a name field
of 9, and of 24 — written six times as six different-looking literals. It is
now a `const int sentw = 9` and a `24`. Without a width parameter those seven
sites stay hand-written, which is a 19% residue in a 37-site population and
exactly the silent-residue shape this house rejects.

**(c) `sb_name` IS DECLINED, AGAIN, AND THE REASON HELD ON RE-TEST.** The
charter's item 2 is a PAIR: `sb_name(a, prefix, suffix)` → `<prefix>_<suffix>`
and `sb_upper(a, prefix, suffix)` → `<PREFIX>_<SUFFIX>`. w2b §7 declined
`sb_name` on the ground that `sb_fragf(a, "%s_%s", p, s)` already is it. Re-
tested against step 10's own sites and the finding holds: the stamp primitives
compose `<UPPER>_<NAME>` themselves, `vm_slot_expr` and `derived_name` each
already build their join with one `sb_fragf`, and a named joiner would add a
name to learn and nothing else. **What DOES need a name is the CASE
TRANSFORM alone** — the one half of that pair two readers could implement
differently — so `sb_upper` ships with the signature `(Arena *, const char *)`
and no suffix. The charter's signature bundles a derivation with a join; only
the derivation is one.

---

## 3. `Vm.up`: RETIRED, and not by the stamp helper

**The brief's conditional is "if the helper's natural home for the uppercased
prefix RETIRES `Vm.up`, take it." The stamp helper does not, and `sb_upper`
does.** Stating the distinction, because it is the whole answer:

The stamp primitives take `upper` as a PARAMETER — they must, since
`pcrec_emit_dfa_stamps` and friends are already written that way and
re-deriving an uppercase per stamp would be 57 derivations of one fact. So
w2b's reading is right: **nothing about the stamps touches `Vm.up`.**

What retires it is building the DERIVATION as a primitive. Before:
`emit_dfa.c`'s `prefix_upper` wrote a per-byte `toupper` into
`GenNames.upper`, a `char upper[80]` in `internal.h`; `pcrec_emit_vm` then did
`memcpy(v.up, g.upper, sizeof v.up)` into `Vm.up`, a SECOND `char up[80]`.
One derivation, two hand-sized buffers, **one of them a copy of the other**.
After: `sb_upper(&cx->arena, cx->opt->prefix)` is called once, in
`pcrec_gen_names`, and both fields are `const char *` pointing at its result.

**Every reader is unchanged and that was checked, not assumed.** `v.up` has
87 readers in `emit_vm.c` and `g->upper`/`g.upper`/`gn.upper` 13 in
`emit_dfa.c`; all 100 pass it to a `%s` or to a `const char *upper` parameter.
The only two WRITERS in the tree were the two `sizeof` sites, and both are
gone. Lens 10's warning that retiring `Vm.up` is "a data-flow change through
the emitter's central struct, not a text change" is about DELETING the field;
moving its STORAGE needs none of it.

`toupper` is kept verbatim rather than swapped for an ASCII table — that
would be a locale-behaviour change smuggled inside a refactor, and it is said
so at the primitive.

**FRAGMENT CENSUS** (`tools/review/fragment_census.py`, both emitters):

| point | statements | declarators |
|---|---:|---:|
| w2b's delivery (6 + `Vm.up`) | 7 | 7 |
| **this lane** | **6** | **6** |

The six are exactly w2b §2's named ENCODING-SEAM GUARD/ADVANCE family
(`g`, `sbnd`, `retry_adv` — `enc.h` seam outputs — and `t`, `probe`,
`mguard` — `pcrec_startpos_guard_text` destinations). **Zero unexplained
residue in either emitter**, and the exclusion list is now closed rather
than closed-plus-one.

---

## 4. The one stamp that stays hand-written, and why it is structural

`emit_dfa.c`'s `<PREFIX>_DFA_PREFILTER_OFFSETS`. **Its value is STREAMED**:
`dfa_prefilter_offsets(cx, c)` writes the offset list straight into the
destination buffer between the opening and closing quote, so no caller ever
holds a value to hand a primitive. Routing it through would mean building the
list into a scratch `StrBuf`, taking it, and freeing it — more machinery than
the line it replaces, and a new allocation on the emission path.

It is recorded **at its own site**, not only here, so a later pass reads it as
a decision rather than a miss. It is the tree's only instance, and it is now a
fourth entry on coding_guide §2.2's "not for" list.

---

## 5. Byte-neutrality: four streams, every batch

All four run against a **pinned branch-point binary** built from
`git archive fa70bf84` — a reference that does not move as the lane edits.
Driver: `…/scratchpad/w2x/sweep.py` (instrumentation, not a deliverable),
rebuilt from w2a §2 / w2b §3.

| stream | population | per batch |
|---|---|---|
| corpus argv, `.c` default engine | 3,938 rows (3,517 compile) | **BYTE-IDENTICAL** |
| corpus argv, `.c` `--engine=vm` | 3,938 rows (3,518 compile) | **BYTE-IDENTICAL** |
| corpus argv, `--emit-ir` listing | 3,938 rows (3,518 compile) | **BYTE-IDENTICAL** |
| composition, `--source` over every `.rxt`/`.rxtin` | 304 files, 30 producing 72 artifacts | **BYTE-IDENTICAL** |

**THE INSTRUMENT WAS VALIDATED BEFORE IT WAS TRUSTED**: run against this
lane's own branch-point build (same source as the reference), all 4,284 rows
came back identical, so a green means "no byte moved" rather than "the
instrument is blind".

**AND ITS `--emit-ir` ARM NEEDED `--engine=vm`, which is worth recording for
the next lane that rebuilds it.** `--emit-ir` at the DEFAULT engine REFUSES
on any pattern the DFA wins (*"--emit-ir lists a VM program; this pattern
compiles to the DFA engine…"*), so the first build of this sweep reached
**1,754** of 3,938 rows against w2a/w2b's reported 3,732/3,518 — a 53% reach
loss that reads as a perfectly healthy green. Forcing the VM restores 3,518,
matching w2b's figure exactly. The reach figure, not the pass count, is what
caught it.

The **composition arm is not redundant**: `vm_splice`'s DELIVER block is
written only by `rxt_compose.c` and no corpus `.rxt` declares an `export`.
Both DELIVER-reaching fixtures (`compose_delivers.rxtin`, `deliver_forms.rxtin`)
are confirmed present in this sweep's producing set.

Plus, every batch: `make strict` clean; `run_ir_listing.sh` **128 passed / 0
failed**; anchor integrity **282 sites across 266 rows, 0 mismatches**.
`make test-codegen` at batches 1 and 7: **8 of 9 scripts**, the sole FAIL
being `run_inline_capability.sh`'s `nm could not read arm_a.o` — the standing
darwin red recorded in `docs/dev/wake.md` and reproduced by both w2a and w2b
at their own branch points.

---

## 6. Anchors

**Three rows re-aimed, all on the one `_VM_FRAMELESS` line**, all by
SUBSTITUTION with the column kept (the statement's 4-space indent is
unchanged, which is what `replace.py`'s whole-file line-agnostic match needs —
coding_guide §3.4). Each row's `SAB_AFTER` is re-spelled on the same helper so
the PLANT is unchanged: swapped arms stay swapped arms (S224), the `v.npush`
derivation stays the `v.npush` derivation (S225), the conditional stays
conditional (S226). Intent re-verified per row rather than inferred from the
substitution.

| row | re-aim | solo verdict |
|---|---|---|
| S224 | `SAB_BEFORE` + `SAB_AFTER` + one `SAB_DESC` sentence | §9 |
| S225 | `SAB_BEFORE` + `SAB_AFTER` | §9 |
| S226 | `SAB_BEFORE` + `SAB_AFTER` + one header sentence | §9 |

**TWO PROSE SENTENCES MOVED TOO, and an anchor checker cannot see either.**
S224's `SAB_DESC` said *"the two arms swapped at the sb_printf call"* and
S226's header *"This plant wraps the `sb_printf` call in"*. Both name the
MECHANISM'S SPELLING rather than its behaviour, so both went stale the moment
the site changed helper, and `m6read_check_sab_anchors.py` stays green through
it by construction — prose is not an anchor. This is the pinned-number-in-
prose class (`w23implfix_report.md`'s ten wrong citations) one step sideways:
*a row's prose can name an implementation detail of its own target, and
nothing in the tree checks that it still holds.*

**S179 was checked and needs nothing**: its `SAB_AFTER` names `v.up`, but
passes it to a `%s`, which a `const char *` satisfies identically.

**A MEASURED PROCESS CONSTRAINT, learned by walking into it.** The first solo
drive of S224/S225/S226 was launched with the re-aims in the working tree and
NOT COMMITTED. All three returned `APPLY-FAILED … ANOMALY (anchor drifted from
HEAD)`, because `run_sabotage_matrix.sh` takes its source from
`git archive HEAD` while reading the sabotage DEFINITION from the working
tree — so a re-aim is measurable only after it is committed. `BOILERPLATE.md`
states the `git show HEAD:` half; the consequence for ORDERING (commit the
re-aim, then drive) is what this lane paid for. The scorer behaved correctly
throughout: ANOMALY, never a false DETECTED.

**AND A PRE-EXISTING DRIFT FOUND IN PASSING, not fixed here.** S224's
`SAB_DOC_FIGURE` records `vmframeless:7fail/4pass`, i.e. an 11-check suite;
`tests/codegen/run_vm_frameless.sh` has **6** checks today and reads 6/0 on
this tree. The figure has been stale since some change between 2026-09-03 and
now, unrelated to this lane. Flagged rather than re-recorded, because
re-recording a doc figure is a claim about a measurement this lane did not
take.

---

## 7. What EP2 and lens 1 got wrong about the tree

`w2a_report.md` §4's shape — short, so a later lane carries it.

1. **"52 sites" is 52 LINES over 44 STATEMENTS**, of which only 37 are value
   stamps. §0. Three readers confirmed the number and none decomposed it.
2. **"4 abutting" anchors is 3, and they are not abutting** — they are three
   rows stacked on ONE line. The four rows genuinely inside the span
   (S89/S155/S168/S182) are on the macro statements X8 must not touch. §0.
3. **Lens 1's typed `emit_stamp_int`/`_bool` cannot be built byte-neutrally.**
   §2(a): seven integer spellings and six raw C expressions in one file.
4. **The charter's `sb_upper(a, prefix, suffix)` signature bundles two facts.**
   §2(c): only the case transform is a derivation; the join is `sb_fragf`.
5. **`Vm.up` was never the stamp helper's to retire** — w2b is right — but it
   is `sb_upper`'s, at a cost of three lines and zero reader changes. §3. Both
   documents treat "retire `Vm.up`" as inseparable from a 110-site data-flow
   change; moving its STORAGE is not that change.
6. **`emit_dfa.c` has 21 stamp lines and one of them cannot be converted.** §4.
   Lens 1's census names 21 as a flat number; the streamed-value case is
   invisible to `grep -c`.

**HELD:** EP2's placement of X8 at step 10 rather than step 1 (it really does
need a substrate, just not the one named — `sb_stampwf` had to be designed
against the tree's own alignment, which only reading the sites gives you);
its `abi` verdict for the step (*"if the helper reproduces each line byte for
byte it is also not an event, but that is a claim to verify rather than
assume"* — verified on four streams per batch, and it is not an event); its
instruction that the site list is found by the grep `"#define %s_` (it is, and
running it is what produced §0); and lens 10 §4.3's recommendation that X8
ride stage 3's blast radius rather than pay it twice.

---

## 8. `tests/core/sb_stamp_check.c`, and why its justification is the CONVERSE of its neighbour's

`sb_fragf_check.c` exists because no answer-level check in this tree can see
`sb_fragf`'s promise — the corpus runs at `rx`, where nothing truncates.
**The stamp primitives are not in that position, and the check says so in its
first paragraph**: every byte they write lands in the emitted `.c`, so the
four identity gates and the full-corpus emit-diff DO see a defect, immediately
and on thousands of artifacts. *A check whose justification is borrowed from
its neighbour is a check nobody can size.*

What it adds is two things the gates cannot: **which property broke** (a gate
says "byte 4,117"), and **the parameter space the shipped sites do not reach**
— they use two padding widths and one two-byte prefix, where this sweeps
widths 0..64 against name lengths 1..64 (4,160 cells, 2,016 of them actually
padding) and builds one stamp at `PCREC_MAX_PREFIX_LEN`.

**FOUR PLANTS, AND THEY DO NOT BEHAVE ALIKE.** Measured, before the file was
committed:

| plant | verdict |
|---|---|
| the separator space deleted | sub-checks 1,2,3,4,5 RED (512/512 and 4160/4160 rows); **6 GREEN, correctly** — still one newline-terminated line, the wrong one |
| `%-*s` written `%*s` | **ONLY 2 and 5 RED**, and 2 on exactly the 2,016 padding rows. **SUB-CHECK 1 STAYS GREEN** |
| the trailing newline dropped | all six RED |
| `sb_stamp_str` emitting `%s` not `\"%s\"` | **ONLY sub-check 4** |

**The second one is the result worth carrying.** At field width 0, `%-*s` and
`%*s` are byte-identical, so **30 of `emit_vm.c`'s 37 call sites could not
have caught that defect** and neither could a sweep that did not carry the
width. It is the reason the cross product exists rather than a list of the two
widths the tree uses — and a sweep built from the shipped population would
have been that list.

Sub-check 5's own reach guard also fired on its first run (*"the max-prefix
witness is ≤ 160 bytes, so it clears no retired scratch size"*) and was
answered by making the witness a genuinely maximal REAL value — `_VM_PREFILTER
_LANG_WHY`'s `PFLW_SIZECAP` arm at both `%llu` maxima, 162 bytes — rather than
by padding it to clear the bar.

---

## 9. Validation — what is COMPLETE and what is OWED

**COMPLETE at handback:**

- Per batch (all seven code batches): corpus argv sweep **3,938 × 3 streams
  BYTE-IDENTICAL**; composition sweep **304 files / 72 artifacts
  BYTE-IDENTICAL**; anchor integrity **282/266, 0 mismatches**;
  `run_ir_listing.sh` **128/0**; `make strict` clean.
- `make test-codegen` at batches 1 and 7: **8/9**, FAIL set identical to the
  branch-point baseline.
- `tests/core/run_core_tests.sh`: **3 passed / 0 failed** (`sb_stamp_check`
  6 sub-checks green), with the four-plant transcript in §8.
- The four suites that read stamps directly, at the final tree:
  `run_dfa_stamps.sh` **31/0**, `run_search_pinned.sh` **17/0**,
  `tests/vm/run_vm_tests.sh` **48/0**, `run_vm_frameless.sh` **6/0**.
- Fragment census: **6 statements / 6 declarators**, `Vm.up` gone.
- The instrument's own self-check: reference build vs branch-point build,
  4,284 rows, **0 differing**.

**OWED**, launched as the lane's last act per `BOILERPLATE.md`'s
DO-THEN-FINISH:

- **S224, S225 and S226 re-driven SOLO at the final SHA.** Log:
  `…/scratchpad/w2x/mech_final.log`. Completion line to look for:
  `== mech run COMPLETE: 1 rows (unexpected: 0, undetected: 0, unreached: 0,
  anomalies: 0, oracle-skipped: 0) at <SHA> ==`, **three times**. The
  criterion is the driver's own `unexpected: 0` / `anomalies: 0` read against
  each row's `SAB_EXPECT` (all three default to DETECTED). **The one to watch
  is `anomalies`**: the earlier uncommitted run read ANOMALY on all three for
  the ordering reason in §6, and a repeat of that would mean an anchor is
  genuinely stale rather than merely uncommitted.
- The full battery is the manager's at merge, as always.

---

## 10. The NEXT unblocked step

**EP2 sequence step 12 — F7 (`vm_wordb` / `vm_cap` / `vm_cat` / `vm_bref`),
8 anchors, depends on step 11 which is landed.** Steps 13, 14 and 15 have no
dependency on anything in flight and 13 (`vm_count_slots`'s two fat arms, 2
anchors) is the cheapest of the four.

**Two smaller items this lane opened:**

1. **`PCREC_STARTPOS_GUARD_TEXT_MAX`'s `--list-limits` note is now the only
   thing standing between the emitters and a ZERO fragment census.** w2b §7
   already filed it: the note names *"four call sites in the two emitters"*
   and the census's remaining six declarators are three guard-text
   destinations plus three `enc.h` seam outputs. Retiring the three guard-text
   buffers plus correcting that note is one small commit with its
   `docs/spec/` hunk (D80) and its `--list-limits`-reader re-pins. The
   `enc.h` seam trio is DD-12's contract and is a different question.
2. **A sabotage row's PROSE can name its target's implementation and nothing
   checks it** (§6). Two instances found here, ~24 already recorded as drifted
   `SAB_DESC` text. If that is ever worth a check, the shape is a grep of each
   row's prose for identifiers that no longer occur in its `SAB_FILE` — which
   is cheap, and would have found both of this lane's before they were fixed.

**Rollback.** Eight independent commits, each mergeable on its own in order.
Reverting batch 4 requires reverting its three anchor re-aims with it; batch 7
is separable if the manager wants EP2's literal `emit_vm.c`-only scope.

---

## 11. Rulings received

None — no ruling was requested or issued during this lane's run.
