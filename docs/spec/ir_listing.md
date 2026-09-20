# `--emit-ir` — the VM program listing format

**[DD-8], 2026-09-19.** This document is the CONTRACT for what
`pcrec --emit-ir` prints: its sections, their columns, and what is and is
not promised about each. It conforms to `docs/spec/table_contract.md` (the
TSV producer/consumer contract) and adds only what is specific to this
listing. `docs/spec/cli.md` §2 is the flag's own reference entry.

## What this listing IS, and what it is not

It is a **DEBUG listing** (D106 addendum 2, Frank's ruling). It is complete
for CONTROL STRUCTURE — every label, every instruction, every branch target,
every choice point and its preference order — and it is LOSSY ON OPERANDS: a
class scan shows its rung role, not its class membership; MRL clamp
arithmetic, encoding-seam specifics and exact budgets are summarized rather
than serialized. A reader can reconstruct the SHAPE and the backtracking
behaviour of the emitted matcher; a reader cannot regenerate the matcher.

It is **NOT an IR** in the compiler sense. `--emit-ir` is a BYPRODUCT of the
emitter's walk, not an input anything consumes. A real internal
representation that a back-end consumes (D106 item 5 / addendum 2 — the
gcc-style split, possibly emitting Rust/C++/JS) is a different artifact, is
D77-gated, and must not be conflated with this.

It is **VM-only**. `--emit-ir` on a pure-DFA artifact REFUSES, naming
`--engine=vm` as the way to get a VM program. A DFA/prefilter listing section
is future work (D106 addendum items 3 and 4); `--emit-dot` is unbuilt.

It **derives from the emitter's own walk** and this is the format's one
absolute constraint (`docs/design/engine_m4.md` §10, D106, D108): every row
is rendered from the `VEvent` stream the emitting call itself appended. The
listing is never a second description of what the emitter does. A renderer
consumes that event stream; it does not re-walk the AST or the DFA — which
is what lets a future back-end producing the same stream reuse this
rendering unchanged (D108 rule 2).

## Framing

1. `docs/spec/table_contract.md` applies in full: TAB-separated values, `#`
   comment lines, the last `#` line before a section's first data row is
   that section's header, columns are APPEND-ONLY, an empty field means
   "none", a field never contains a TAB.
2. **Every table is a NAMED `#section`**, the PROGRAM body included. There
   is no anonymous section and no sibling line-oriented format: D106
   addendum item 1 settled that the body fits columns, so it is one
   mechanism.
3. **Column WIDTH is not a contract** (D106 addendum 3, resolving the code
   review's L10-6). Fields are unpadded. A consumer that depends on
   alignment is reading something this format does not promise.
4. **The section NAME set is the API**: append-only. A name, once shipped,
   keeps its meaning; new sections may be added. Same rule for each
   section's columns, independently (table contract, Sections rule 3).
5. **Cell escaping is `pcrec_sb_text`'s vocabulary**, the one every registry TSV
   dump uses: a byte below 0x20, and 0x7f, goes out as `\xNN`; every other
   byte — backslash and high bytes included — passes through as itself. It
   protects the FRAME and never transcodes content. It is NOT `pcrec_sb_field`'s
   round-trippable `.rxt` escape, and the two are not interchangeable.
6. **A multi-valued cell is comma-joined with no spaces** (`cursor,revdet`).
   Two cells use it today: `summary`'s `rungs` and `strategies` values.
   `summary`'s `possessify` value is the one SLASH-joined pair
   (`marked/total`).
7. **A `#` line never follows a section's data.** This is a producer
   obligation rather than a stylistic one: rule 3 above would make a
   trailing remark inside an empty section that section's header. An empty
   population is therefore a ROW whose cells are empty and whose `note`
   carries the sentence — never a comment.
8. The preamble before the first `#section` is free prose and belongs to no
   section.

## The sections

### `summary` — `fact | value | note`

One row per artifact-wide fact. `value` is the machine-readable half;
`note` is prose for a human and carries no promise of wording (D26's tier
rule applies: what a fact IS is exact, how it is worded is not).

| `fact` | `value` |
|---|---|
| `pattern` | the pattern text, framed per rule 5 |
| `engine` | always `vm` (this listing exists only for VM artifacts) |
| `prefilter` | one of the nine tokens below |
| `root-minw` | the root minimum width — **row present only when it reached the analysis ceiling** |
| `rungs` | comma-joined rung kinds anywhere in the program, or `none` |
| `strategies` | comma-joined strategy kinds, or `none` |
| `possessify` | `marked/total` source quantifiers, or EMPTY when `-fno-possessify` denied the pass |
| `caps` | the capture-slot pair count (`<PREFIX>_NCAPS`) |
| `step-budget` | the backtrack-resumption budget, or EMPTY under `--fno-step-budget` |
| `resume-frames` | the stamped resume-frame capacity |
| `trail-entries` | the stamped trail capacity |
| `subject-ceiling` | the declared subject ceiling in bytes, or EMPTY when the capacities are exact |
| `labels` | emitted label count |
| `events` | listing-event count |
| `resume-points` | the PRE-PASS count the resume-point cap is checked against — an ESTIMATE, and an OVER-count is the safe direction |
| `max-replicas` | body replications, against `PCREC_MAX_VM_REPEAT_COPIES` |
| `prune-ceiling` | `none` / `prefilter-window` / `subject-end` |
| `prune-bound-sites` | emitted MRL bound sites |
| `prune-retreats` | runtime-term length retreats |
| `islands` | DFA-island count |
| `callout-sites` | callout-site count |

**`prefilter` value vocabulary** (append-only; the ORDER the emitter tests
them in is load-bearing — the construct and analysis routes are decided
before the flag routes, so the listing never names a flag the caller did not
pass):

| token | means |
|---|---|
| `yes` | exact capture-erased forward+reverse DFA pair |
| `yes-collapsed` | built from the count-collapsed superset ([OPT-4]) |
| `no-backreference` | a backreference; no flag changes it |
| `no-linked-call` | a LINKED subroutine call; `-fprefilter` refuses |
| `no-nullable-collapsed` | a rung offered the collapsed filter and it was declined ([OPT-4.1]) |
| `no-nullable-exact` | the pattern's own exact language is nullable ([OPT-4.2]) |
| `no-dfa-overflow` | the auto-selected prefilter's DFA build hit a cap ([SEL-1]); the `note` carries the cap text |
| `no-fno-prefilter` | forced off by `-fno-prefilter` |
| `no-engine-vm` | the `--engine=vm` side effect (R21 E-6) |

**`prune-ceiling` uses the same three words as the artifact's own
`<PREFIX>_VM_PRUNE_CEILING` stamp, deliberately.** The two are computed
INDEPENDENTLY (R31 E3: the defect was a stamp disagreeing with the code
beside it, and this listing is one of `v.mrl_win`'s four readers), so a
consumer can compare them by EQUALITY. Note that this row's `none` means
`-fno-length-prune` — the stamp's `none` means no bound site was emitted —
so the two agree on every artifact that clamps, which is the population any
check about them is scoped to.

### `slots` — `family | slot | holds | note`

The `slot_values` layout (`docs/design/engine_m4.md` §2.4), derived from the
same accessors the emitter indexes with; "written" is derived from the
`VE_SET` events, so a slot the layout reserves and the program never writes
shows up as exactly that.

`family` is a fixed vocabulary, append-only: `group`, `guard`, `low`,
`mark`, `revdet`, `lookmark`, `lookpos`. **Every family contributes at least
one row**: a family with no slots emits one row with `slot` and `holds`
empty, carrying its explanation (where it has one) in `note`. That is what
makes "which families does this artifact use" a projection of a declared
column rather than a guess at prose.

`group` is the one family whose `slot` cell names a PAIR (`2,3`): a capture
group owns its start and its end together and the written verdict is a
property of the pair. Every other family's `slot` is a single number.

`revdet` is the one family with THREE rows per loop index, in the order a
reader needs them (entry, low-water, ceiling), which is why the section
reads entry/low-water/ceiling per loop rather than family by family.

### `rungs`, `strategies`, `pruning` — `label | kind | detail`

The PER-QUANTIFIER views of the `VE_RUNG` / `VE_STRAT` / `VE_PRUNE` event
streams — one row per emitted quantifier, in emission order, `label` naming
the label the decision was recorded against and `kind` the decision. Each is
appended by the same call that decided the emitted shape, so a row and the
code it describes are one fact recorded once rather than two that could
disagree. An empty population is one row with `label` and `kind` empty and
the reason in `detail`.

These are per EMITTED quantifier. `summary`'s `possessify` is per SOURCE
`A_REP`, and the two populations differ whenever a bounded repeat replicates
its body.

### `program` — `label | op | args | target | note`

The straight-line trace of what executes. `op` is the instruction word and
is the column a consumer selects on; `args` is its operand; `target` is the
label control reaches; `note` is the role text the walk recorded.

| `op` | `label` | `args` | `target` |
|---|---|---|---|
| `label` | the label (`L7`, or `accept` / `fail` for the two terminals) | — | — |
| `consume` | — | the class/character description | the next label |
| `assert` | — | the assertion's description | the next label |
| `push` | — | — | the RESUME label |
| `set` | — | `slot_values[N] <- scan_position` | — |
| `goto` | — | — | the target label |
| `fail` | — | — | — |
| `note` | — | — | — |
| `accept` | — | — | — |
| `call` | — | the CALLEE label | the RETURN label |
| `return` | — | `goto* frame.call_ret` | — |
| `cut` | — | `frames <- slot_values[N]` | — |

`op` is append-only as a vocabulary. Rung, strategy and prune events write
no C of their own and therefore appear in their own sections only, never
here.

### `choicepoints` — `label | resume | note`

One row per emitted resume-frame push: `label` is the site, `resume` is the
label the frame resumes. **Preference order**: the frame pushed at a site
resumes the LESS preferred alternative. A program that never backtracks
emits one empty row saying so.

### `islands` — `label | width | note`

One row per emitted DFA island (`docs/spec/tuning.md` §2.20). The COUNT is
`summary`'s `islands` row. Empty population: one empty row with the reason.

### `callouts` — `label | note`

One row per emitted callout site. The COUNT is `summary`'s `callout-sites`
row. Module `callouts` has no producer today, so this section is empty on
every artifact; the rows exist so it starts working the day one lands,
unchanged — the shape the `islands` section already proved.

## Consuming it

Use `tests/lib/table.sh` (the in-tree implementation of both contracts):
`table_section_rows FILE SECTION`, `table_field FILE SECTION COL`,
`table_lookup FILE SECTION KEYCOL KEY VALCOL`, `table_col_index`,
`table_check_truthfulness`. Each fails loudly on an absent section, column
or key. **Do not write a fixed-position `grep` against this listing.** D106
records that its consumers' fixed-position extractors went stale once
already and that declaration-based parsing is the durable fix; that is what
this format exists for.

## History

- **2026-09-19, [DD-8]**: first version. The listing adopted
  `table_contract.md` as machine-first TSV (D106 + its three addenda, D108),
  rendered through the [REVW.1] wave-1 emission kit's `pcrec_sb_row`. Before this
  it was a `;`-commented, column-aligned human listing whose consumers
  parsed it by remembered shape.
