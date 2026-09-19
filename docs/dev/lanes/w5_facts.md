# [REVW.5] WAVE 5 (PUBLIC SURFACE) + [REVW.A1] — FACT SHEET

Lane `w5facts` (sonnet, read-only — no `make`, no edits under `src/`,
`cli/`, `lib/`, `tests/`). Branch `lane/w5facts` from `main` at `b1f0a430`
(the [PLAN-AUDIT] close; `abi` is 27, emitted comments OFF by default per
D112). Every number below was re-measured against that commit today
(2026-09-19) via `grep`/`nm`/`git show`/`wc`, following `w4_facts.md`'s own
method (§0's precedent, re-measure rather than copy a review number). Where
my count differs from the review or from a landed lane's own report, both
numbers are given and the newer one is marked.

This sheet answers the two items named in the brief: [REVW.5] wave 5
(public surface, `docs/dev/reviews/2026-09-17-code-review.md`'s "Wave 5"
paragraph and lens 9's §8 order) and [REVW.A1] (the abi change-log
reconciliation, the review's LAST item, lens 4's finding A1). It makes no
implementation decision; §7 lists what needs a ruling before an
implementing lane starts.

---

## 0. What the review sources got wrong or stale

Re-measuring against `b1f0a430` surfaced four corrections beyond what
`fixnow_report.md` already fixed:

1. **Lens 9's P1 export count is stale by more than the fix-now pile
   accounts for.** Lens 9 measured `libpcrec.a` at **259** exported
   definitions, **12** with no `pcrec_` prefix. Today's archive (built
   06:07 this morning at this pin) has **285** exports and **29**
   unprefixed names (30 counting `PCREC_DEFAULT_FEATURES`, which carries
   `PCREC_` but is P5's second unstated exception, not `pcrec_`). The
   growth is real, not measurement noise: waves 1/2 (`w2b`, `w2y`, `w2x`,
   `w1kit`) dropped `static` off ten new `src/core/sb.c` primitives so the
   emission kit's helpers could cross the `emit_dfa.c`/`emit_vm.c`
   translation-unit boundary (`sb_field`, `sb_fragf`, `sb_fragfv`,
   `sb_join`, `sb_row`, `sb_stamp_str`, `sb_stampf`, `sb_stampwf`,
   `sb_text`, `sb_textn`, `sb_upper` — eleven, not ten; I recount below),
   and wave U's L5-R2 sat-arithmetic check did the same to six functions
   (`cg_sat_add`, `cg_sat_mul`, `mrl_sat_add`, `mrl_sat_mul`, `vm_fadd`,
   `vm_fmul`) so `tests/core/sat_arith_check.c` could link against them.
   **D104 (2026-09-17) names and prices exactly 12 symbols and rules their
   rename order; 17 more collision-shaped exports exist today that D104
   never saw**, all landed on `main` between D104's ruling and this sheet.
   See §2.
2. **Lens 9's line citations for `match_api.md` §8.2 have drifted**
   (`:3319-3335` at review time; the struct block is at `:3399-3413`
   today) — a ~80-line shift from unrelated intervening doc growth
   (`docs/spec/CLAUDE.md`'s own revision-ledger entries). The FINDING
   (9 documented members against 19 shipped) is unchanged; only the
   citation moved. Re-aim by content, not by line, per `coding_guide.md`.
3. **P2/P7/P8 are CONFIRMED DONE**, not merely claimed done. `fixnow_report.md`
   states commit `9face833` "[REVW.FIX] L9-P2/P7/P8: lib/pcrec.h header
   sweep" landed them; I independently re-verified all three against the
   live header rather than trusting the report (§3). Wave 5 briefs should
   NOT re-open these — lens 9's own §8 wave order lists them as steps 1-2,
   but they are already off the board.
4. **`docs/spec/match_api.md` §6 (the `rx_info.abi` field's own
   contract paragraph, `:1999-2295` at this pin) is a de facto FOURTH,
   continuous, gap-free abi bump narrative that lens 4's A1 finding does
   not name as one of the "three homes."** It runs backward from `27`
   ([EMIT-VERB]) through every single transition to `2` (`[DD-14.FB]`)
   with NO missing link — including the two transitions (`20→21`,
   `21→22`) the review found recorded nowhere in the tree at review
   time. This changes REVW.A1's shape materially; see §6.

---

## 1. L9 §8 recommended wave order — done vs. open, re-measured

| # | item | lens9 severity | status TODAY | evidence |
|---|---|---|---|---|
| 1 | P2 (utf8 "not yet implemented" comment) | CORRECTNESS-RISK | **DONE** | `9face833`; §3 |
| 2 | P8 (order-of-magnitude ratio) + P7 (`RX_NCAPS`×5/`RX_PUSH`/`RX_SET` at default prefix) | POLISH | **DONE**, same commit | §3 |
| 3 | P3 (struct quotation 10/19 fields short) + §5.2 rider (`PCREC_TRACE`/`PCREC_VM_ENTRY_*` rows) + P6 (mask catalogue delegates to source, a D80 inversion) | MAINTAINABILITY | **OPEN** | §4 |
| 4 | P4 (11 limits constants cited, none declared; `pcrec_limits_tsv` exported, undeclared) | MAINTAINABILITY | **OPEN**, untouched since review | `grep -n "PCREC_MAX_NFA_STATES\|pcrec_limits_tsv" lib/pcrec.h` → 0 declarations, only prose mentions at `:645,863,889,935`; `git log --oneline --all -- lib/pcrec.h` shows nothing past `9face833` touching this |
| 5 | P5's spec/rider half (`PCREC_DEFAULT_FEATURES` → `pcrec_default_features`, keeping §8.2's exception list exhaustive) | MAINTAINABILITY | **OPEN**, but **RE-SCOPED BY D104**: "the P5 rider rides the same wave [as P1]" — a rename, not a spec sentence, folded into item 6 | §6 |
| 6 | P1 (unprefixed exports renamed to `pcrec_*`) | CORRECTNESS-RISK | **OPEN**, D104-ruled, **population grown 12→29** since the ruling | §2 |
| 7 | P5's structural half (separate the flat `PCREC_*` namespace into contract/internal) | MAINTAINABILITY | **DEFERRED, not wave 5's venue** | D104: "belongs to the v1 API-versioning event... this row deliberately does not pre-empt it" |

Deliverable (5) from the brief, the union mode membership, is not an L9
item — it is `w4_report.md`'s own recommendation for "wave 5's D80 batch."
See §5.

---

## 2. P1 / D104 — the unprefixed exports, re-priced

**D104** (`docs/dev/decisions.md:7081`) ruled: rename to `pcrec_*`, landed
NAME BY NAME, `nfa_*` first (37 sites, 1 test file, the pattern-prover),
`ctx_fail` last (249 sites, 30 files, 8 sabotage rows re-aimed
intent-verified), each its own mechanical commit with the battery between.
Localization refused on three grounds (D2 plain-make; archive-member
granularity; hides rather than fixes). Scope statement: "the other ~244
exports are `pcrec_`-prefixed and collision-safe by convention; their
over-export is NOT fixed by this row."

**The 12 D104 named, re-verified still present and still unprefixed**
(`nm -g build/libpcrec.a | awk '$2~/^[TDBSC]$/{print $3}' | grep -v pcrec_`):
`arena_alloc`, `arena_free`, `ctx_fail`, `ctx_nomem`, `sb_puts`,
`sb_putc`, `sb_printf`, `sb_free`, `sb_take`, `nfa_has_asserts`,
`nfa_has_bot`, `nfa_wrap_unanchored`. Site counts unchanged from lens9's
table (re-spot-checked `ctx_fail`'s `grep -rlw` file count: 30, matches).

**17 more exist today that D104 never named**, all landed after D104's
ruling (2026-09-17) by waves whose own reports never mention the public
linker surface (none of `w2b_report.md`, `w2y_report.md`, `w2x_report.md`,
`w1kit_report.md`, `waveu_report.md` — the lanes that dropped `static` off
these — discuss P1/D104 at all; the growth is a side effect none of them
were chartered to notice):

| name | src+cli files (`grep -rlw`) | tests files | sabotage rows | landed by |
|---|---:|---:|---:|---|
| `PCREC_DEFAULT_FEATURES` | — (lens9's own P5 second exception, not new) | — | — | pre-existing |
| `sb_field` | 5 | 2 | 1 | wave 1 (w1kit) |
| `sb_fragf` | 6 | 6 | 0 | wave 2 (w2b) |
| `sb_fragfv` | 5 | 0 | 0 | wave 2 (w2b) |
| `sb_join` | 8 | 0 | 0 | wave 1 (w1kit) |
| `sb_row` | 9 | 1 | 1 | wave 1 (w1kit) |
| `sb_stamp_str` | 6 | 3 | 0 | wave 2 (w2x) |
| `sb_stampf` | 6 | 6 | 3 | wave 2 (w2x) |
| `sb_stampwf` | 5 | 3 | 0 | wave 2 (w2x) |
| `sb_text` | 5 | 2 | 1 | wave 1 (w1kit) |
| `sb_textn` | 5 | 0 | 0 | wave 1 (w1kit) |
| `sb_upper` | 6 | 0 | 0 | wave 2 (w2x, "never `Vm.up`'s to retire but it is `sb_upper`'s") |
| `cg_sat_add` | 2 | 4 | 0 | wave U (waveu, L5-R2) |
| `cg_sat_mul` | 2 | 3 | 1 | wave U |
| `mrl_sat_add` | 6 | 9 | 3 | wave U |
| `mrl_sat_mul` | 5 | 6 | 2 | wave U |
| `vm_fadd` | 2 | 5 | 1 | wave U |
| `vm_fmul` | 2 | 3 | 1 | wave U |

All 17 are `src/core/`-internal helpers (the emission kit's text
primitives; the saturating-arithmetic pair) needed cross-TU by
`emit_dfa.c`/`emit_vm.c` or `tests/core/`'s unit checks — the same
structural reason the original 12 are unprefixed (a file-local `static`
would not link across `src/gen/`). **None of the 17 landed with a
"why is this unprefixed" note**, because none of their lanes were
chartered to look at the linker surface at all — a scope gap, not a
defect in any one lane's work.

**Emitted-byte question**: No, for the whole item. Every one of these 29
names (12+17) is a compiler-internal C identifier, called at compile time
to BUILD emitted text, never itself written into a `.c`/`.h` artifact.
Structurally cannot move a byte on any of `scripts/emit_sweep.py`'s five
streams — confirm with a sweep run per the coding guide's own discipline,
since "structurally can't" is an argument, not a substitute for the gate.

**Open question for the manager** (see §7 item 1): does D104's ruling
extend to the 17, or is D104 scoped strictly to the 12 it named by name?
The ruling's own text ("the twelve") and its per-name rename-order table
are exhaustive as written; nothing in D104 anticipates a growing
population. The mechanical cost of covering all 29 the SAME way is small
per name (most have single-digit-to-low-teens site counts) except
`mrl_sat_add` (15 sites total) and `sb_stampf` (12), still far below
`ctx_fail`'s 279.

---

## 3. P2 / P7 / P8 — confirmed done

**P2** (`lib/pcrec.h:24-27`): `PCREC_ENC_UTF8 = 1` now reads `/* UTF-8; a
character is 1-4 bytes ([M5.0] stage 2). docs/spec/match_api.md §8.2 is
the contract. */`, replacing "not yet implemented (arrives with milestone
M5)". Matches §8.2's own wording exactly, as lens9's suggested fix asked.

**P7**: `grep -n "RX_NCAPS\|RX_PUSH\|RX_SET\b" lib/pcrec.h` returns **zero
hits**. All five former `RX_NCAPS` sites now read `<PREFIX>_NCAPS`
(`lib/pcrec.h:40,1027,1053,1059,1061`); `RX_PUSH`/`RX_SET` are now
`<PREFIX>_PUSH`/`<PREFIX>_SET` (`:847-848`).

**P8**: `grep -n "order of magnitude" lib/pcrec.h` returns **zero hits**.
The warn-bytes comment (`:933-936`) now reads "chosen well under
`PCREC_MAX_EMIT_BYTES`" — no numeric ratio claim, matching lens9's second
suggested fix (they offered "delete the phrase" or "write 'well under'";
the landed fix took the latter).

All three: `git log --oneline --all -- lib/pcrec.h | head -3` shows
commit `9face833` "[REVW.FIX] L9-P2/P7/P8: lib/pcrec.h header sweep" as
the most recent touch besides `d3fd444b` ([EMIT-VERB] WIP, unrelated —
the axis/comment-gate work, not this header's prose). Nothing has
regressed either fix since.

---

## 4. P3 + §5.2 rider, and P6 — still open

**P3.** `match_api.md` §8.2 (`:3399-3413` today) still quotes
`pcrec_options` with exactly the same **9 members** lens9 found:
`prefix, encoding, flags, header_name, engine, step_budget, work_budget,
unroll_k, frame_capacity`. The shipped struct (`lib/pcrec.h:760-994`) has
**19 today** — I hand-counted every member: `prefix, encoding, flags,
header_name, engine, step_budget, work_budget, unroll_k, vm_entry_shape,
frame_capacity, max_emit_code_bytes, max_emit_bytes, max_nfa_states,
max_dfa_states_goto, max_subset_elems, max_auto_dfa_elems,
warn_emit_bytes, name, tune` — the identical count and the identical 10
missing fields lens9 named, unmoved by any of waves 3/4/EMIT-VERB (none
of them touch `pcrec_options`). `docs/spec/tuning.md:2436` still reads
"`docs/spec/match_api.md` §8.2 states the struct itself in full" — still
false.

**§5.2 rider**: `tuning.md` §4's mirror table still lists 14 of 26 flag
bits; the same seven tuning bits lens9 named
(`NO_SIZE_TERM`, `NO_PREFILTER_COLLAPSE`, `FORCE_PREFILTER_COLLAPSE`,
`NO_SCAN_EDGE`, `NO_START_PINNED`, `NO_CLS_FOLD`, `NO_STARTPOS_GUARD`)
have a §2 section but no §4 row; `PCREC_TRACE`/`PCREC_VM_ENTRY_*` still
have zero spec rows under their enum spellings (`grep -c "PCREC_TRACE"
docs/spec/tuning.md docs/spec/cli.md` → 0/0, `PCREC_VM_ENTRY_AUTO` → 0/0,
same as at review time). **Fold into one sweep of §8.2 + §4**, as lens9
recommended — one commit re-quotes the 19-member struct and completes
the mirror table.

**P6.** `match_api.md:3450-3455` (drifted from lens9's `:3450`, same
paragraph) still reads: "which bits those are, and why each is masked,
is documented per-flag in `lib/pcrec.h`'s own comments, which is the
place to look — this document does not duplicate that catalogue."
`tuning.md` §2 still carries the real mask catalogue (11 `masked out of
rx_info.flags`/`strategy_denials` sites re-confirmed: `:112, :155, :270,
:343, :410, :453, :683, :763, :864, :943` and one more, matching lens9's
count). Fix unchanged: one sentence in §8.2 pointing at `tuning.md` §2
instead of `lib/pcrec.h`.

**Emitted-byte question (both)**: No — `docs/spec/` prose only, zero
source or emitter touched. No `emit_sweep.py` stream can move.

---

## 5. The union mode membership — the D80 candidate (deliverable 5)

Source: `docs/dev/lanes/w4_report.md` §2 Item 3 (L11-F4), cross-referenced
at §5 item 4 as "a one-line D80 change with a ready-made instrument. Good
candidate for wave 5's spec batch."

**Current state (post-wave-4)**: `cli/main.c`'s six duplicated
mutual-exclusion checks were already collapsed into one
`CLI_MODE_TABLE` (14 modes) + `cli_modes_active` + **four named masks,
each a NARROWER subset of the one below it** (13/12/9/8 members),
preserving each site's original acceptance exactly per the manager's
ruling (narrowest-per-site).

**The proposal, not built**: replace the four named masks with ONE
13-member union mask applied at every site. Exact cost quoted from
`w4_report.md`: *"today's four memberships mean `--probe-ask
--flavour=pcre2` is ACCEPTED and `--source --flavour=pcre2` is REFUSED,
for no reason a reader of either site can give. The union (13 members
everywhere) is one line in this item's own table... It is a D80 change
that newly refuses combinations accepted today, and its population is
not measured here."*

**Instrument**: `docs/dev/lanes/w4_modesweep.py`, already committed on
`lane/w4` (merged to `main` with the rest of wave 4). Sweeps all 469
one/two/three-element subsets of the 14 mode flags × 3 operand shapes =
1,407 invocations, comparing rc/stdout/stderr against a build of the
branch point. Re-running it with the union mask substituted for the four
named ones and diffing against today's 1,407-invocation baseline **is**
the blast-radius measurement — "the diff IS the blast radius" per the
report.

**D80**: Yes, unavoidably (this is w4_report's own framing, unchanged) —
any invocation newly accepted or refused is caller-observable and needs
a `docs/spec/cli.md` hunk stating the new (single) membership.

**Emitted-byte question**: No — `cli` is the outermost layer (per
`coding_guide.md` §1.9), never touches `src/gen/`.

**Instrument gap**: none of `emit_sweep.py`'s five streams exercise CLI
mode-flag combinations at all (streams 1-4 are single-pattern argv
compiles or composition; stream 5 is `--list-*` registry dumps). The
union-mask change needs `w4_modesweep.py` specifically, not the emit
sweep — the same "an instrument only sees what it was built to reach"
class `w4_facts.md`'s own §5.2 rider observation and lens9's own §5
method-findings section both name.

---

## 6. P5 — both halves

**Spec/rider half** (open, re-scoped by D104). Lens9's finding: §8.2's
"the one stated exception" sentence (naming `PCREC_FEATURE_SET`/
`_MODULES` as the sole `PCREC_*`-without-being-in-`lib/pcrec.h` case) is
short one — `PCREC_DEFAULT_FEATURES` (`src/parse/enabled.c:112`,
`extern const char *const PCREC_DEFAULT_FEATURES;` at
`src/core/internal.h:4723`, confirmed still exported: `nm -g
build/libpcrec.a | grep PCREC_DEFAULT_FEATURES` → `S _PCREC_DEFAULT_FEATURES`)
is a second, undeclared exception.

**D104's own text changes the venue lens9 proposed** (lens9's §8 put this
at wave-order step 5, a standalone spec sentence, BEFORE step 6's P1
rename). D104 instead folds it into the P1 wave as an actual RENAME:
*"The P5 rider rides the same wave: `PCREC_DEFAULT_FEATURES` (an exported
data symbol, the naming rule's second unstated exception) renames to
`pcrec_default_features`, keeping match_api.md §8.2's exception list
exhaustive."* So the correct disposition is: rename the symbol (4 call
sites per lens9's earlier count), which makes §8.2's exception list
correctly exhaustive with NO sentence added — there is no longer a
second exception to state. Still unrenamed today (confirmed above).
Rider on `cli/CLAUDE.md:125`, unrelated to lens9 but met in the same
spot: it still describes the constant as `"currently \"none\""`; the
shipped value is `"std1"` — a one-line CLAUDE.md fix, lens 4's territory
per lens9's own note, unclaimed by any landed wave.

**Structural half** (deferred, NOT wave 5's venue): separating the flat
`PCREC_*` namespace (47 contract / 113 internal at review time — not
re-measured here, out of this sheet's item list) into two lexically
distinct namespaces. D104: *"A deliberate export-control story... belongs
to the v1 API-versioning event lens 9's P5 names as its trigger — this
row deliberately does not pre-empt it."* Revisit-when, per D104's own
clause: the v1 versioning event, or a new unprefixed export collision
(which §2 shows has already happened 17 times over — worth flagging to
the manager as a possible EARLY trigger, though D104's literal text names
"the v1 versioning event," not "another collision," as P5's structural
trigger; §7 item 2).

---

## 7. [REVW.A1] — the abi change log's homes, reconciled

**Lens 4's A1 finding** (`lens4_clarity_archaeology.md:198-260`) named
**three homes**, at review time (`.abi = 26` was current):

| home (lens4's own naming) | transitions named then | complete then? |
|---|---:|---|
| `src/gen/emit_dfa.c:1534-1964` (the code comment above `.abi = 26`) | 16 | no — missing 7→8, 10→11, 16→17, 17→18, 18→19, 19→20, 20→21, 21→22 |
| `tests/codegen/run_codegen_tests.sh:2795` (one 11,861-char failure-message string) | 22 | no — missing 20→21, 21→22 |
| `src/gen/CLAUDE.md` (per-milestone `##` sections) | partial | no — the only home THEN for 16→17/17→18 |

Lens4 found "20→21 and 21→22 recorded nowhere in the tree at all" at
review time, and recommended consolidating to ONE home,
`docs/spec/match_api.md` §6.3, with the code comment cut to ~8 lines and
the shell message cut to one sentence.

**Re-measured today (abi 27, six more bumps landed since the review:
`[K50]` 23→24, `[PORTFIX]` 24→25, `[OPT-DIAL]` 25→26, `[EMIT-VERB]`
26→27, plus the two the review already knew about at 22/23):**

| home | transitions covered today | complete? |
|---|---|---|
| `src/gen/emit_dfa.c` (code comment, now ending at `.abi = 27`) | 2-6, 8-9, 11-15, 22-25 (`sort -u` on `grep -oE "abi [0-9]+ *-> *[0-9]+"` over the file) | **no — STILL missing the original 8 gaps, PLUS the new 26→27 was never backfilled: 9 gaps now, worse than at review time** |
| `tests/codegen/run_codegen_tests.sh:2851` (`ABI_EXPECT=27`'s failure message, now grown further) | 2-19, 22-27 (verified: the string reads "...(19->20)... and by [FORM-CHAR]... (22->23..." — jumps straight over 20→21 and 21→22) | **no — the SAME two gaps as at review time, unfixed by any of the six intervening bumps; every later wave appended its own new transition instead of backfilling** |
| `src/gen/CLAUDE.md` | stops at 17→18 (nothing past it in 3,061 lines) | **no — frozen since 2026-09-03, none of the last ten bumps recorded here** |

**A fourth home lens4 never named, and it is the one that is actually
complete**: `docs/spec/match_api.md` §6 (`rx_info.abi`'s own field
paragraph, `:1999-2295` at this pin) is a continuous, gap-free narrative
running backward from `27` to `2` with **every single transition
present**, including both of the transitions lens4 found recorded
nowhere. It explains WHY the 20→21/21→22 gap exists in the other homes
without being a gap itself: `[DD-13b.W1.3]`'s composition change was
*written* as an in-branch 18→19 bump, but by merge time `[ENG-ISL]` and
`[OPT-EDGE]` STEP 1 had already taken 18 and 19, so it renumbered to 20
at the merge (the exact `src/gen/CLAUDE.md:2343` renumbering pattern
already documented for `[DD-13b.W1.2]`'s 13→14/14→15); `[OPT-EDGE]` STEP
1.1 then took 20→21, and `[CC-DIFF]` STEP 2 took 21→22. **This narrative
has been extended by every single bump since it was written** — the
`[EMIT-VERB]` lane's own citation table (`emitverb_report.md:324-325`)
lists `docs/spec/match_api.md:159` and `:1982` (now `:1999` at this
pin) as sites it re-pinned for 26→27, confirming this is a LIVE,
actively-maintained fourth home, not a fossil.

**What this changes for the implementing lane**: lens4's recommendation
("one home, and it is `docs/spec/match_api.md` §6.3") is **already
substantively built**, at §6 rather than exactly §6.3, and has been kept
current by every bump's own D76/D94 ritual since before the review. The
actual work is:
1. **Reconciliation, as lens4 said, is still a prerequisite** — before
   trimming the other two homes, verify §6's narrative against `git log`
   on `.abi` for the handful of transitions this sheet did not manually
   re-derive against commit history (I read the prose and cross-checked
   it against `src/gen/CLAUDE.md`'s independent record where they
   overlap; I did not re-run `git log -p` on every `.abi =` line).
2. **Cut `src/gen/emit_dfa.c`'s 431-line comment to ~8 lines** (what
   `abi` means, the ritual in one sentence, the current bump's own event,
   a pointer to §6) — lens4's original suggestion, unchanged.
3. **Cut `run_codegen_tests.sh:2851`'s failure message to one sentence +
   pointer** — same.
4. **`src/gen/CLAUDE.md`'s per-milestone sections stay** (they are design
   record for their own topics, not solely abi history — 16→17 and
   17→18's paragraphs there carry the `[CC-DIFF]`/`[ENG-ISL]` design
   reasoning, not just the number) — lens4 did not propose deleting this
   home, only naming `match_api.md` as the ONE canonical log; CLAUDE.md
   stays as a secondary, topic-scoped record the way it already is for
   every other subsystem.

**Emitted-byte question**: No — every home is a comment, a shell string,
or `docs/`; none reach `src/gen/`'s emitters. `emit_sweep.py` cannot
witness this item either way.

---

## 8. Coding-guide disciplines that apply, per item

- **P1/D104 (§2)**: `coding_guide.md`'s D76/D94 "readers found by grep"
  rule applies directly to the rename's OWN sabotage/spec re-aim sweep,
  not to the abi ritual — a symbol rename is not an abi event (it changes
  no emitted byte), so D76 itself does not fire; only the ordinary
  grep-for-callers discipline does.
- **P3/P6/P5-rider (§4, §6)**: D80 — every one is a `docs/spec/` hunk
  riding no code change; `coding_guide.md`'s note that `docs/spec/` is
  the contract and a reviewer rejects a contract edit without checking it
  against the shipped surface (which this sheet already did, first-hand,
  for every field/sentence cited).
- **Union mode membership (§5)**: `coding_guide.md`'s altitude rubric —
  this is the "variations looped/tabled rather than duplicated" case
  wave 4 already half-solved (one table, four masks); the union proposal
  is the SAME rubric applied one step further (one table, one mask).
- **A1 (§7)**: `docs/dev/learnings.md` §3 / memory
  `pcrec-check-design-lessons` shape — three homes sharing no source text
  is exactly "controls that share a source with what they control"
  inverted (here: DOCUMENTATION copies with no shared source), and the
  fourth home's existence is itself a "population nobody counted" finding
  (lens4 counted three homes without a census sweep for a fourth).

---

## 9. Open questions for the manager, numbered

1. **Does D104's rename ruling extend to the 17 newly-unprefixed exports
   found in §2, or is it scoped strictly to the 12 it named?**
   Recommendation: extend it — the ruling's REASONING (a consumer's
   `arena_alloc`/`sb_puts` collides; D2 plain-make; archive-member
   granularity) applies identically to `sb_stampf`/`mrl_sat_add`/etc.,
   and doing all 29 under one convention now is cheaper than re-opening
   the same design question in six months when the 30th appears. Rests
   on: §2's site-count table — none of the 17 exceeds 15 sites, all
   individually cheaper than `ctx_fail` alone.
2. **Does the 17-symbol growth since D104 count as the "second collision"
   that D104 names as one of P5's structural-half triggers?**
   D104's literal text names only "the v1 versioning event" as P5's
   trigger, not "another collision" — but P1 (the LINKER-namespace
   finding, ruled) and P5-structural (the SOURCE-namespace finding,
   deferred) are different surfaces, so a P1-population growth is not
   obviously evidence for P5-structural's trigger either. Recommendation:
   treat them as independent — extend D104's rename to cover 29 names (a
   P1-shaped fix) without treating that as satisfying or advancing P5's
   structural trigger, which the review scoped as an internal/contract
   namespace split, a different question from "does this specific name
   collide at link time." Rests on: D104's own text, quoted in §6.
3. **§7's fourth abi-log home — should `docs/spec/match_api.md` §6 be
   formally declared THE canonical home (discharging lens4's
   recommendation as already substantively done), or does the wave still
   need to explicitly consolidate onto a renamed/restructured §6.3?**
   Recommendation: declare §6 the home as-is (it is already complete,
   already the spec tier D80 wants, and already kept current by every
   bump) rather than moving its content into a differently-numbered
   subsection for cosmetic alignment with lens4's exact citation — the
   review's own text says "the docs home already exists," which §6 IS,
   just not at the exact §-number lens4 guessed before checking. Rests
   on: §7's transition table showing §6 complete for all 26 transitions
   this sheet checked (2→3 through 26→27).
4. **P4 (§1 item 4) was not deeply investigated by this sheet** — it
   rode along in the wave-order table but its own site/fix detail
   (lens9 §5.1, "6 of 19 fields are raise-only caps with no declared
   constant") was not independently re-measured beyond confirming it is
   still open. Recommendation: the implementing lane re-reads lens9 §5.1
   directly before scoping P4's own commit — it is LOCAL effort per
   lens9's own severity table and not blocked by anything in this sheet,
   but this sheet's budget went to P1/P3/P6/P5/A1 as directed by the
   brief's five named deliverables. Rests on: this sheet's own §1 table
   marking P4 "OPEN, untouched since review" without further detail.

---

## 10. Validation owed

None run — this is a read-only fact sheet, no `make`, no edits under
`src/`/`cli`/`lib`/`tests`. Every count above was produced by `grep`,
`sed -n`, `wc -l`, `nm`, or `git log`/`git show` against worktree
`w5facts` (content-identical to main tree `/Users/fdicostanzo/pcrec` at
`b1f0a430`, since nothing has been committed to the worktree branch
diverging from it) in this session, not delegated, not copied from a
stale artifact without saying so.
