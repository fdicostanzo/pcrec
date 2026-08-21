# [M6-READ] sample stage — the style exemplar

**STATUS: PROPOSED.** This directory is the one sample commented artifact the
[M6-READ] plan row owes Frank before the emitter conversion. Nothing in
`src/` was touched. The samples are hand-edited emitted C: they show what the
emitter should produce, they are not produced by it.

The row's acceptance question, quoted from its INTENT CLARIFICATION, is the
one every choice below was made against:

> does this help a competent C programmer, new to regex engines, understand
> what is going on here

and its SCOPE RULED block sets the altitude: the artifact explains **itself**,
never regex-engine theory. Frank's frame — commentary restores the larger
picture that C strips away — is what the top-of-file orientation blocks are
for.

## What is here

| file | what it is |
|---|---|
| `dfa_before.c` / `.h` | emitted verbatim for `ERROR-[0-9]{3,5}: [a-z]+` |
| `dfa_after.c` / `.h` | the same artifact, hand-edited into the proposed style |
| `vm_before.c` / `.h` | emitted verbatim for `(\w+)@(\w+)\.(com\|org)` |
| `vm_after.c` / `.h` | the same, hand-edited |
| `check_neutrality.sh` | the object-code comparison; run it, it takes seconds |

Two samples rather than one because the two engines are genuinely different
artifacts. The DFA sample shows the prefilter, the forward scan, the reverse
pass and the state tables. The VM sample shows all of that as a *subroutine*
plus the compiled program, the resume stack, the capture trail and the
budgets — which is where the real comprehension gap is.

Patterns were chosen to exercise the machinery, not to be short:
`ERROR-[0-9]{3,5}: [a-z]+` produces a memchr prefilter and a bounded-repeat
table whose `{3,5}` bound is visible as distinct states;
`(\w+)@(\w+)\.(com|org)` produces three capture groups, two possessified span
loops, an alternation with a resume frame, and minimum-remaining-length
pruning.

**Read `dfa_after.c` first, top to bottom.** It is 388 lines and it is the
whole proposal.

## 1. The naming scheme

### The rules

1. **Names say the role in the machine, not the type or the C mechanism.**
   `last` becomes `last_accept_position`, not `last_size_t`.
2. **Full English words.** No abbreviations, no truncations. `sfound`,
   `stv`, `btn`, `rst`, `pp` all go.
3. **Qualify only where the artifact holds more than one of a kind.** The
   DFA scanner runs two passes, so it has `scan_position` and
   `rewind_position`; the VM body has exactly one subject cursor, so it is
   just `position`. This rule is what keeps names from bloating into
   `vm_subject_scan_position_cursor`, and the emitter can apply it
   statically — it knows which shape it is emitting.
4. **Harmonise with the vocabulary the artifact already publishes.** The
   emitted header's `rx_ctx` already names its fields `subject`, `len`,
   `pos`. Locals derived from them use the same words, so `subject` is the
   bytes and `..._position` is an offset into them.
5. **Anything with linkage keeps its name.** See §2, decision 1, for exactly
   where the frozen line is drawn.

### The mapping

DFA scanner (present in both artifacts — the VM's `rx_prefilter` is the same
code):

| before | after | role |
|---|---|---|
| `s`, `n` | `subject`, `subject_length` | the bytes being searched |
| `startpos` | `search_from` | earliest position the caller allows |
| `caps` | `capture_spans` | the reported spans |
| `pos` | `scan_position` | forward scan cursor |
| `last` | `last_accept_position` | best match end seen so far |
| `st` | `forward_state` | |
| `q` | `candidate` | the `memchr` hit |
| `end` | `match_end_position` | |
| `pp` | `rewind_position` | reverse walk cursor |
| `sfound` | `match_start_position` | |
| `rst` | `reverse_state` | |
| `rx_fcls` / `rx_rcls` | `rx_forward_byte_class` / `rx_reverse_byte_class` | |
| `rx_ftr` / `rx_rtr` | `rx_forward_next_state` / `rx_reverse_next_state` | |
| `rx_facc` / `rx_racc` | `rx_forward_is_accepting` / `rx_reverse_is_accepting` | |
| `rx_first` | `rx_can_begin_match` | first-byte set for the skip |

VM:

| before | after | role |
|---|---|---|
| `rx_work` | `rx_run_state` | everything one attempt can change |
| `stv` | `slot_values` | recorded group boundaries |
| `bt`, `btn` | `resume_stack`, `resume_depth` | alternatives not yet tried |
| `tr`, `trn` | `trail`, `trail_depth` | undo log for `slot_values` |
| `.k`, `.pos`, `.mark` | `.resume_label`, `.resume_position`, `.trail_mark` | |
| `.slot`, `.v` | `.slot_index`, `.saved_value` | |
| `budget`, `work` | `steps_left`, `work_left` | |
| `w` | `run` | |
| `rx_match_impl` | `rx_match_anchored` | says the thing that matters about it |
| `rx_unwind` | `rx_reset_for_next_attempt` | |
| `rx_caps_out` | `rx_report_captures` | |
| `rx_work_init` | `rx_run_state_init` | |
| `pos` | `position` | subject cursor |
| `rx_cur` | `rx_span_cursor` | |
| `rx_ceil` | `rx_window_end` | |
| `rx_k0` | `rx_class_bitmap_0` | |
| `start`, `ceil_`, `win` | `attempt_position`, `window_end`, `window` | |
| `r`, `rc`, `b_` | `result`, `search_result`, `frame_index` | |
| `RX_NSTATE` | `RX_NSLOTS` | it counts capture slots, not states |
| `RX_BT_FRAMES` | `RX_RESUME_FRAMES` | |
| `RX_WORK` | `RX_CHARGE_WORK` | it is an action, not a quantity |
| `RX_MRL_SHORT` / `RX_MRL_CAP` | `RX_TOO_SHORT` / `RX_CLAMP_SPAN` | |

## 2. Judgment calls — RATIFIED (Frank, 2026-08-21)

These are the places the row's letter did not decide and I did. **All five
were reviewed and ratified as embodied in the approved samples; none was
overruled.** They are recorded as reasoning, not as open questions.

**Decision 1 — where "ABI" stops.** The row says the emitted header's names
do not change. I read that as the names a *consumer writes*: exported
symbols, types, struct fields, macros. Parameter spellings in a prototype
have no linkage, cannot be written by a caller (C has no designated
arguments), and do not affect compilation or linking of any consumer — so I
renamed them, in the `.c` and the `.h` alike. The `check_neutrality.sh` gate
enforces the real boundary: exported symbols must be identical, and they are.

Frozen absolutely, and untouched in both samples: everything inside the
shared `PCREC_RX_ABI_H` block — `rx_ctx` and its fields, `rx_matchfn`,
`rx_renderfn`, `rx_group_entry`, `struct rx_info`, `PCREC_*`. That block is
spec §2's verbatim quote, so engineering note (ii)'s re-quote stays
body-text-only exactly as the row says.

*Consequence worth seeing before approving:* that block's prose still
describes `<prefix>_next_pos(const unsigned char *s, size_t n, size_t pos)`
in the old spelling while the declaration below it now reads
`(subject, subject_length, position)`. Freezing the block is right; the
mismatch is the price.

*If Frank rules the stricter reading*, the fallback is object-neutral and
already understood: keep the four parameters and open each body with
`const unsigned char *const subject = s;`. It costs one line per entry point
and no instructions. I did not do this because it leaves `s` and `n` — the
two most-referenced names in the file — in the signature a reader meets
first.

**Decision 2 — `rx_L<N>` labels keep their numbers.** This looks like the
biggest missed rename in the VM sample and it is deliberate. Those numbers
are not private: `pcrec --emit-ir` prints the same program with the same
labels, and `tests/codegen/run_ir_listing.sh` exists to hold the two in
correspondence. A label number is a documented cross-artifact identifier, so
it gets a legend and a per-label intent comment, not a new spelling. The
orientation block says so, so a reader is not left wondering.

**Decision 3 — five new emitted macros, beyond comments and renames.**
Engineering note (i) anticipates "state names via macros/enums resolving to
the same values"; these are that mechanism, and all are verified neutral:

- `RX_FORWARD_CLASSES` / `RX_REVERSE_CLASSES` — the row stride. `st * 9` is
  the single most opaque expression in a DFA artifact and `9` is a
  pattern-derived constant, not a magic number.
- `RX_FORWARD_START` / `RX_REVERSE_START` — the start state, the only state
  the emitted code names by number.
- `RX_NO_POSITION` — replaces bare `(size_t)-1` used as "nothing found yet".
- `RX_SLOT_GROUP1_START` … — the slot legend, in the VM. `RX_SET(2, ...)`
  becomes `RX_SET(RX_SLOT_GROUP1_START, ...)`. This is requirement (5)
  applied to the one place in the VM where a bare number *is* an identity,
  and it is the single largest readability gain in that artifact.

I deliberately did **not** emit an enum naming all 15 DFA states. For a
non-trivial pattern those names would be machine-generated noise, and only
the start state is ever referenced by number. The legend in the comment
carries the rest.

**Decision 4 — the existing developer commentary stays.** Both artifacts
already carry good comments (`K24`, `D49`, the prefilter's `engine_m4.md`
citation). They are written for a *pcrec developer* — they cite documents the
reader does not have and justify choices rather than explaining behaviour.
The reader-facing layer is added around them rather than replacing them. If
Frank wants the doc-citations trimmed for an external audience that is a
separate, easy pass; I did not assume it.

**Decision 5 — byte literals left as decimal.** `subject[position] == 99`
gets `/* consume 'c' */` above it rather than becoming `== 'c'`. Emitting
the character literal would be strictly better and is object-neutral, but it
is a codegen change rather than a comment or a rename, so it is offered as a
follow-on rather than smuggled in.

## 3. Style choices — where comments earned their place, and where they did not

### Comment form — RULED (Frank, 2026-08-21)

The samples were approved with one cosmetic ruling, applied here and binding
on the emitter conversion:

- **`/* */` = STRUCTURAL.** The file orientation block, section banners, data
  structure and table blocks with their legends, macro-definition comments,
  and function header blocks.
- **`// ` = LINE-LEVEL INTENT.** Any comment attached to a statement, a small
  group of statements, or a program label. Line comments stand out better
  against the code in this form.

Applied to 12 comments in `dfa_after.c` and 36 in `vm_after.c`; re-verified
neutral (`.text`/`.rodata` byte-identical, exported symbols unchanged) rather
than assumed. **The headers are untouched by the ruling** — every comment in
them is either a doc block or a frozen-ABI field annotation, and neither is
line-level intent.

Two boundary calls, both trivially flippable if Frank wants them the other
way. The multi-paragraph mechanism blocks at `rx_accept` and `rx_fail` keep
`/* */`: they are the VM's two exits and read as header documentation for
them, not as intent on a statement — whereas the short per-label comments
(`// group 1 opens`, `// consume 'c'`) took `//`. And trailing annotations
inside data initialisers (`.engine = 2, /* PCREC_ENGINE_VM */`) keep `/* */`,
since `//` inside a braced initialiser reads poorly and these annotate data
rather than code.

### Density and placement

The row names blind quota compliance as the failure mode, so it is worth
being explicit about the density that resulted.

**The orientation block is the load-bearing piece.** It is the manager's
(c) proposal, re-scoped as the row's SCOPE RULED block directs: a map of
*this* artifact's sections and how one match attempt flows through them. In
the DFA sample it is 50 lines for a 388-line file. That ratio is the point —
a reader who has read it can then follow code that needs very few local
comments, whereas per-line commentary can never deliver "why is there a
second backwards pass at all". The VM's version additionally spends one
paragraph on backtracking, because it is the only mechanism in that file
whose effect is non-local and no amount of local commentary would convey it.

**Self-evident code got nothing.** `if (search_from > subject_length)
return 0;` has no comment. Neither do the wrapper bodies, the `rx_info`
initialiser fields, or most of `main`. Measured on the samples: of 60
statements in `dfa_after.c`, **5 carry an attached comment** — 92% carry
none; in `vm_after.c` it is 22 of 180, or 88% with none. Nearly all of the
commentary is in the orientation block and the table legends, where it
serves the whole file, rather than beside individual statements. That
distribution *is* the proposal: if a per-line quota had been applied these
numbers would be near zero, and the artifact would be worse.

**Line comments say intent and are anchored to a *decision*, not a
statement.** The comments that survived are the ones a reader would
otherwise have to reverse-engineer:

- `/* Prefilter: nothing found yet and still at the start, so skip ahead to
  the next byte that could begin a match. */` — the condition
  `forward_state == RX_FORWARD_START && last_accept_position ==
  RX_NO_POSITION` is not self-explaining.
- `if (forward_state < 0) break;   /* dead: no match can continue */` —
  `-1` is a sentinel, and the trailing form keeps it on the eye-line.
- `/* Never rewind past where the caller allowed the search to begin. */`
- In the VM, `/* consume 'c' */` above each byte test — eight of them, and
  they are the difference between reading a pattern and decoding ASCII.

**Loop invariants got a sentence at the loop, not per iteration.** "the
loop keeps the LAST accepting position rather than stopping at the first,
because `[a-z]+` can always run further" appears once, above the forward
scan, and explains four lines.

**A genuinely subtle mechanism got a fuller block than any per-line rule
would produce**, exactly as the clarification permits: the possessive span
loop, `rx_fail`'s two-part rewind (position *and* trail), and
minimum-remaining-length pruning each get three to eight lines, because each
is a mechanism whose *existence* is the puzzle.

**Data structures got block comments and no per-row commentary**, per
requirement (3)'s clarification. Every table has: what it is, how it is
indexed, what a cell means, and a legend.

### State legends

Requirement (5)'s legends are derived by breadth-first search over the
transition table *the emitter is about to write*, labelling each state with
the shortest input that reaches it:

```
 *   0  (start) nothing matched yet
 *   1  E                    8  ERROR-DD
 *   ...
 *   9  ERROR-DDD    -- 3 digits, ':' now allowed
 *  12  ERROR-DDDDD  -- 5 digits, no 6th exists
```

This is worth dwelling on because it decides engineering note (iv). It needs
no NFA semantics, no tagging pass and no after-the-fact inference — it is a
walk over emitter-owned data, so it *cannot* drift from the table it
describes. And it happens to make the pattern's structure legible: the
`{3,5}` bound shows up as states 9/10/12 with and without an onward digit
transition, which is the kind of "larger picture" the row is asking for.

The reverse machine's legend lists bytes **in the order that walk consumes
them**, with the comment saying so — the examples read as the match
backwards, which is itself the clearest available statement of what the
reverse pass does.

## 4. Object-code neutrality — result

`./check_neutrality.sh` — **PASS on both pairs.** Also verified
behaviourally: both binaries produce byte-identical output for every subject
tried (matches, non-matches, empty subject, boundary lengths).

But the naive form of this check gives a **false alarm**, and that is a
finding the landed gate must be built around:

- **(a) Executed code is byte-identical.** `.text` and `.rodata` compare
  equal for both artifacts at `-O2`. This is the property that matters and
  the one the gate enforces.
- **(b) Internal symbol *names* change, necessarily.** Renaming a static
  function or a function-local static array renames its internal-linkage
  symbol. It shows up in `objdump -d` annotations, `nm`, and debug info —
  12 symbols in the DFA sample, 18 in the VM. It is not executed code and
  does not survive `strip`, but **a gate that diffs disassembly *text* will
  fail on it**, and my first version of this script did exactly that,
  producing 200 lines of diff in which every single line was
  `rx_match_impl` → `rx_match_anchored`.
- **(c) Exported symbols are unchanged**, checked separately. Any difference
  there would be a real ABI break, and this is the check that actually
  enforces the row's zero-ABI-change promise.

So: no rename in this scheme is non-neutral in the sense that matters, and
"object-code-neutral" needs to be *defined as (a) plus (c)* rather than left
as "compare object code", or the conversion lane will burn a day on (b).

## 5. Implementation plan for the emitter conversion

Not the conversion — the shape of it, with the budget.

### Files touched

| file | why |
|---|---|
| `src/gen/emit_dfa.c` (2,420 lines, 213 emit sites) | the DFA scanner, its tables, and the emitted header |
| `src/gen/emit_vm.c` (5,254 lines, 256 emit sites) | the VM program, run state, macros, and its own header emission |
| `src/gen/enc/enc.c` (1 emit site) | `rx_next_pos`'s parameter names |
| `src/gen/CLAUDE.md` | new emitted identifiers and the legend mechanism |

Both emitters write headers, so the `.h` parameter renames of decision 1 land
in the same two files. Nothing outside `src/gen/` emits identifiers.

### How the legends are emitted

Engineering note (iv) requires the emitter to *tag* what it emits rather than
infer it afterwards. Both legends already exist inside the emitter:

- **DFA state legend** — a BFS over the transition table in the emitter's own
  hands, immediately before it writes that table. Same data, same function,
  no new analysis, no drift possible.
- **VM slot legend** — this is already computed and printed. `--emit-ir`'s
  `SLOTS` section renders exactly `slot 2,3 → group 1, written on traverse`
  today, from the emitter's own walk. The conversion routes the same facts to
  a second sink (a C comment plus the `RX_SLOT_*` macros) rather than
  computing anything new.
- **VM label intents** — likewise: `--emit-ir`'s per-label annotations
  (`; group 1 opens`, `; alternation entry (2 branches)`) are the comments
  the sample writes by hand.

That last point is the strongest argument for the whole approach: the
readable C and the IR listing become two renderings of one walk, which is
the property `--emit-ir` was built to have ("produced by the emitter's own
walk, so it cannot drift from the code it describes"). **The conversion must
rename the listing's prose in lockstep with the C** — the listing prints
`stv[N]` and `pos` today.

### Pin budget

Measured, not estimated (full survey by file is available; headline
numbers):

| what | count |
|---|---|
| test **pins** — assertions that break on a rename | **~77** (range 76–78) |
| — `tests/codegen/` | 45 |
| — `tests/mech/sabotages/` | 14 (of 87 files; the rest anchor `src/parse`, `src/opt`, `src/ir`) |
| — `tests/mrl/`, `tests/assertions/`, `tests/possessify/`, `tests/prefilter/` | 18 |
| sibling tables not in the sample (`rx_fs`, `rx_rs`, `rx_facc2`, `rx_fendv`, `rx_rendv`) | **+~17** |
| **working budget** | **~94 pins** |
| doc/prose mentions (stale, not breaking) | 64, mostly `tests/codegen/CLAUDE.md` (20) and `tests/mech/CLAUDE.md` (16) |

`scripts/`, the `.rxt` corpus and `tests/harness/` carry **zero** pins — the
`.rxt` format encodes only patterns, subjects and spans, and the harness
touches only the public ABI. The six `*_identity.sh` byte-identity checks
also cost nothing: they diff two artifacts from the *same* compiler, so a
consistent rename passes them unchanged.

**The dangerous pin is not any of the 94.** It is
`tests/codegen/run_ir_listing.sh:132`, which greps the IR listing's own prose
for `"set stv[N]"`. Rename the emitter's C *and* the listing's format string
consistently — which the previous section says the conversion must do — and
leave this grep alone, and **both sides go empty and the `diff -q` passes
vacuously**. That is precisely the failure this project has already recorded
in its own memory: a control sharing a source with the thing it controls.
The conversion owes this check a non-empty assertion, and it should be
written *before* the rename, not after. `run_ir_listing.sh:102-103,122-123`
(the `sed 's/^L/rx_L/'` glue) and `:286-287` (the `-p myrx` prefix control)
are the same file's other three-way sync points.

Two mech sabotages reproduce multi-identifier emitted lines verbatim and need
re-deriving rather than token-swapping: `S36_vm_undo_neutered.sh:20-21`
(`w`/`trn`/`bt`/`b_`/`mark` on one line), `S73_accept_indexed_at_end.sh:37-43`
and `S74_reverse_termination_blind.sh:45-48`.

### Where the compile-before/after gate lives

The neutrality property has no "before" once the conversion has landed, so
the gate is a **tool taking two pcrec binaries**, not a self-contained
`make test` check:

```
tests/codegen/run_object_neutrality.sh  REFERENCE_PCREC  [CURRENT_PCREC]
```

For each pattern in the corpus it emits with both compilers, builds both at
`-O2 -g0`, and compares `.text` + `.rodata` bytes and the exported symbol
list — the (a)+(c) definition from §4, with the (b) internal-symbol delta
reported as information. Run during the conversion with the pre-conversion
build as reference, sweeping all ~1,500 corpus patterns; that run *is* the
gate the row asks for, and its output is the close evidence. Afterwards it
stays in the tree as the reusable answer to "this change should be
neutral" — the same shape as the existing `*_identity.sh` checks, which is
why `tests/codegen/` is its home.

It does **not** join `make test`'s default path: it needs a second compiler
to compare against, which `make test` has no way to produce.

### Sequencing

1. Land the non-vacuous replacement for `run_ir_listing.sh:132` **first**,
   against today's names, and watch it fail on a deliberately broken build.
2. Land `run_object_neutrality.sh` and record a baseline with the current
   compiler against itself (must be trivially green).
3. Convert `emit_dfa.c` — renames, comments, legends, header params — and
   run the gate against a pre-conversion reference build.
4. Convert `emit_vm.c` and the `--emit-ir` listing prose together.
5. Update the ~94 pins and the 64 doc mentions.
