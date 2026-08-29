# The syntax registry's TSV column contract

This is the **spec**, not the design record, per `docs/spec/CLAUDE.md`'s
charter. `docs/spec/table_contract.md` states the WIRE FORMAT every
tabular pcrec command shares (`#` comments, one header row, append-only
columns, resolve-by-name); `docs/spec/cli.md` §2 states what each of the
three listing surfaces *answers*, in one paragraph apiece. This document
is the third leg: for `--list-syntax`, `--list-verbs` and
`--list-families`, **every column, by name, with its value set**, and
which values are a closed, stable vocabulary a consumer may switch on
versus which are free text a consumer may only display. Every value set
below was read live off a fresh build at this worktree's branch point
(`962e2de`); the command that produced each is given so a reader can
redo it.

## 1. The shape of the promise

`docs/spec/table_contract.md` rule 4 is the load-bearing one for this
document: **columns are added at the END; a consumer resolves a column
by its HEADER NAME, never by hardcoded position or field count; a
column is never removed or renumbered.** That freedom to append lasts
through pre-v1 (D40, `docs/dev/decisions.md`): after v1, the same rule
holds but backwards-compatibility becomes a binding promise rather than
a house habit. The rule exists because it was already broken once:
D65 appended the `built` column (below) to `--list-syntax`, and two
consumers that had hardcoded `NF != 15` broke while every consumer that
resolved by header name did not (`docs/design/registry_built_status_memo.md`'s
Correction section has the full survey). `tests/lib/table.sh` is the
shell/awk implementation of the resolve-by-name rule;
`tests/registry/compliance_section.py`'s `COLS` list is python's, and it
is itself cross-checked against the dump's live header every run (§4
below) so the two implementations cannot silently disagree about what
a header says.

The registry's own generating structure (`RegRow`, `src/core/internal.h`)
is the single declarative source SR-4 was built around: one row per
spelling, read by the parser, the reject-test suite, `--explain`, and
`docs/pcre2_compliance.md`'s generated index — never re-derived. This
document only describes what the THREE DUMPS built from that source
print; it does not re-describe the row struct itself.

## 2. `--list-syntax` — one line per construct spelling

`build/pcrec --list-syntax | head -1` shows the announcing comment;
the header line itself is the *last* `#` line before the first data
row:

    #kind  selector  syntax  module  feature  flavours  engines  status
    diag  flags  expect  note  roadmap  quantifiable  class_expect
    built  family

17 columns, confirmed live this pass. 128 data rows
(`build/pcrec --list-syntax | grep -vc '^#'`) — this is the number
`tests/registry/registry_check.c:575`'s exact-count assertion pins
today; **`tests/registry/CLAUDE.md`'s own prose still says "100 since
Q2/SR-9"**, which was true when that paragraph was written and has
since drifted behind six further row-adding modules — flagged here as
the drift the survey brief (A8) asked to name, not corrected in that
file by this pass.

| column | value set | stable? |
|---|---|---|
| `kind` | `esc` \| `group` \| `verb` \| `class-bracket` \| `quant-suffix` — the five `RegKind` doorways (`src/parse/syntax_dump.c` `kind_name`); the fifth, `quant-suffix`, has no lexical doorway at all (a possessive suffix is recognised inside `p_rep` after the quantifier already parsed) | yes |
| `selector` | the byte/character after the doorway that selects this row, or `*` for "matches any remaining byte at this doorway" (`REG_SEL_ANY`); 54 distinct values observed (`cut -f2 \| sort -u \| wc -l`) | yes, but not enumerable as a short closed list — read per-row |
| `syntax` | a pattern that PROBES this construct — `tests/reject/` and `--explain` compile it | free text (but every row's value is itself a valid pcrec probe pattern, guaranteed by `registry_check`'s well-formedness pass) |
| `module` | one of 17 module names (`assertions`, `atomic-groups`, `backrefs`, `branch-reset`, `callouts`, `classes`, `comments`, `conditionals`, `extended-classes`, `lookaround`, `misc`, `modifiers`, `named-groups`, `quoting`, `recursion`, `unicode-props`, `verbs`), or empty for `status=base`/`rejected` rows with no owning module | yes |
| `feature` | a hex bitmask (`0x0000`..`0x10000`, 18 distinct values seen) | **not independently named.** `src/parse/syntax_dump.c`'s own header comment states why: `registry.c`'s `M_<module>` macros already pair each bit with a module name, and a second bit->name table here would be a second home for that mapping. Read `module` beside it for the name; `tests/registry/` separately proves the two are a bijection |
| `flavours` | `pcre2` (the only value today — one flavour exists, `--flavour` (`cli.md` §2) filters it; a second flavour is future work, SR-7) | yes |
| `engines` | empty \| `vm` \| `dfa\|vm` — which engine(s) can execute a produced node for this row; empty for rows with no producer yet or no engine question (`status != module`) | yes |
| `status` | `base` \| `module` \| `rejected` — `RegStatus`: is this base-tier grammar, gated behind a module, or a construct pcrec refuses outright | yes |
| `diag` | `none` \| `module` \| `module-octal` \| `fixed` — which diagnostic TEMPLATE this row's refusal uses (`RegDiag`); pairs with `expect` | yes |
| `flags` | empty \| `class-delim` \| `lexical` (mask; both bits can co-occur) | yes |
| `expect` | the SUBSTRING pcrec's diagnostic must contain when this row's syntax is refused — a substring of the doorway's template, not the whole message, so the template itself has one home; empty for the 1 row that compiles cleanly at base tier (127 of 128 rows are non-empty, `cut -f11 \| grep -vc '^$'`) | free text |
| `note` | one-line human description | free text |
| `roadmap` | `-` (the question doesn't arise, base rows) \| `planned` \| `never` — legal pairing with `status`/`diag` enforced by `registry_check` (K14/§17.2): a `never` row must not promise a module in its diagnostic | yes |
| `quantifiable` | `yes` \| `no` \| `form` \| `lexical` \| `-` — whether `<syntax>*` is grammatically legal after this construct, measured against libpcre2 and re-verified by `tests/spec_mod0/check10` | yes |
| `class_expect` | the measured class-POSITION behaviour, e.g. `char 0x08` / `set 246` / `err 137` (34 distinct values seen); **empty — not `-`** — on the 56 group/verb rows that cannot reach a class position at all, per the header's own "empty field = none" rule, distinct from `-` which means "not applicable, the question was asked and doesn't apply" elsewhere in this table | yes as a vocabulary shape (`char N` / `set N` / `err N`), values themselves are per-construct facts |
| `built` | `built` \| `unbuilt` \| `defect` \| `-` — **D65's column; see §3** | yes |
| `family` | the canonical `syntax` of the family this row is a spelling of, empty when the row is its own family — **D71 item 3's column; see §5** | free text (but its value, when set, is always another row's own `syntax`) |

Live counts this pass (`build/pcrec --list-syntax \| grep -v '^#' \|
cut -f16 \| sort \| uniq -c`): `built` 106, `unbuilt` 16, `-` 6, `defect`
0 — 128 total, matching `registry_check.c:2878`'s own pinned
`checked/built/unbuilt/na` tuple (128/106/16/6) exactly.

## 3. `built` vs. `status`/`roadmap` — two different questions

`status` and `roadmap` are **PCRE2/base-grammar facts**, fixed at the
row's authorship: is this real syntax, and does pcrec ever plan to
implement it. `built` (D65) is **orthogonal** and answers a question
`status`/`roadmap` cannot: has *this specific construct's* producer
actually landed, right now, in this build — derived live by driving
the row's own `syntax` through a gate-forced-open doorway call
(`pcrec_construct_built_status`, `src/parse/syntax_dump.c:707`), never
a hand-declared field (a second, hand-kept column was explicitly
declined — `ext.c`'s own `UNBUILT` comment gives the reason: it would
have to be kept in sync with the ports by hand, the exact two-homes
shape the registry exists to prevent). A row can be `status=module,
roadmap=planned` and `built=unbuilt` simultaneously — that pairing is
the *ordinary* case for a module mid-rollout, not a contradiction.

Confusing the two once cost a lane a whole review pass: `docs/CLAUDE.md`'s
wave-E incident record describes prose rows carrying the shipped
status while the generated index's `status`/`roadmap` columns were read
as though they meant the same thing, for 34 rows of already-shipped
modules. `built` exists precisely so a reader never has to re-derive
"is this actually built" from `status` plus a memorized module
rollout state.

`built`'s three-plus-one values, briefly: `built` (the row's producer
stamped a node), `unbuilt` (the gate-forced-open probe still refused —
with every module open, only a missing producer can refuse a
well-formed row), `-` (the question doesn't arise: `status` is `base`
or `rejected`), and `defect` — not a status a well-formed registry ever
prints, but a `registry_check.c` DEFECT ASSERTION for a row whose own
declared `syntax` produces neither a clean answer nor the unbuilt
refusal shape (measured 0 of 128 rows today).

## 4. `--list-verbs` — the `(*VERB)` name tables

`build/pcrec --list-verbs | grep '^#'` shows PCRE2 keeps TWO
case-selected tables; 6 columns, 50 rows total (31 `upper`, 19
`lower`, `cut -f1 | sort | uniq -c`):

| column | value set | stable? |
|---|---|---|
| `table` | `upper` \| `lower` — which of PCRE2's two tables, selected by the case of the name's first byte | yes |
| `name` | the verb's bare name, e.g. `ACCEPT`, `COMMIT`, `fail` | free text (fixed vocabulary of 50 names, not independently enumerated here) |
| `forms` | a `\|`-joined subset of `(*N)` / `(*N:a)` / `(*N:)` / `(*N=d)` / `arg-is-subpattern` / `start-of-pattern-only` — 5 distinct combinations observed live | the token vocabulary is fixed; which subset applies is per-name |
| `unknown` | the fixed diagnostic text pcrec gives for an unrecognised name in this table | free text, identical for every row in the file today |
| `roadmap` | `planned` \| `never` (never `-` — every verb name has an opinion) | yes |
| `quantifiable` | `yes` \| `no` \| `not-askable` — `not-askable` is a THIRD outcome, distinct from `no`: the unquantified form itself does not compile (e.g. a start-of-pattern-only verb away from position 0), so the question "is `X*` legal" cannot even be posed | yes |

The `forms` column is, in the dump's own words, "what libpcre2
ACCEPTS, measured, not what pcrec implements" — **pcrec implements
none of the fifty rows** (`--list-verbs`' own header says so); every
row still ends a compile. A consumer reading `forms` as "what pcrec
will parse" is reading the wrong column.

## 5. `--list-families` — the grouping index (D71 item 3)

`build/pcrec --list-families | grep -vc '^#'` — 90 rows against
`--list-syntax`'s 128 (38 rows carry a non-empty `family`, collapsing
into their canonical row: `128 - 38 = 90`, confirmed). 7 columns:

| column | value set | stable? |
|---|---|---|
| `syntax` | the family's KEY, which is always some row's own `syntax` — the canonical spelling | free text, but always traceable to a `--list-syntax` row |
| `module` | taken from the family's first member in table order | yes (one of the same 17 names) |
| `engines` | taken from the first member | yes |
| `status` | taken from the first member | yes |
| `built` | **ANDed over every member** — a family reads `built` only if EVERY member does; `-` if none of the question applies (`nna == nmem`) | yes; see below |
| `nmembers` | integer count of spellings in the family (min 1 — a family of one prints exactly what `--list-syntax` prints for that row) | count |
| `members` | every spelling, space-separated, canonical member first | free text |

`module`/`engines`/`status` are read off the family's first member
rather than elected independently, because `registry_check.c` already
asserts every member of a family agrees on all three — if that
assertion ever fails, it fails loudly there, not silently here by
picking a different member.

`built`'s AND-over-members rule is D71 item 3's rule stated exactly,
and the direction matters: a family whose canonical spelling compiles
while one alias does not is **not** a built family — saying otherwise
would be the same lie D65's row-level column exists to prevent, one
layer up. Grouping is an INDEX-layer fact only and never changes a
row's own dispatch identity (R6) — `--list-syntax` still gives every
alias its own line and its own probe, because `tests/reject/` needs
each one tested independently.

Example, read live this pass (`build/pcrec --list-families | grep -v
'^#' | awk -F'\t' '$6==11'`): the family keyed `(?1)` has 11 members —
`(?1)` through `(?10)` plus the relative-alpha spelling `(?01)` — all
module `recursion`, engines `vm`, `built`. A second family of 11 groups
the corresponding negative/relative back-reference spellings. These
are today's largest families; 78 of the 90 families have exactly one
member.

`--list-families` takes no `--flavour` filter — `cli.md` §2 states why
(a family is a grouping OF rows; filtering members mid-grouping would
make one invocation's `built` answer a different question than
another's, `cli/main.c:517-523`'s own comment).

## 6. `--list-axes` — the optimization-axis registry (the FOURTH surface, [CHK-2])

`build/pcrec --list-axes | grep -vc '^#'` — 45 rows today, 12 columns,
confirmed live this pass. Where the first three surfaces describe
SYNTAX pcrec accepts, this one describes the compiler's own TUNING
machinery: for every axis where `src/gen/emit_dfa.c` or
`src/opt`/`select_engine.c` chooses among two or more emitted
strategies for a pattern, one row per (axis, candidate), in the
emitter's own PREFERENCE order (order 1 is tried first; the last
candidate of an axis always applies).

    #axis  order  candidate  kind  stamp_macro  stamp_value  deny_macro
    deny_bit  force_macro  force_bit  cli_flag  applies

| column | value set | stable? |
|---|---|---|
| `axis` | 18 values today: `table`, `prefilter`, `view`, `seed`, `accept`, `direction`, `match` (the seven DFA layer-1 axes, `docs/design/emitter_form.md` §3 and, for `match`, `docs/design/anchored_match_unwrapped.md` §5.1) plus `possessify`, `revdet`, `counter`, `length-prune`, `vm-prefilter`, `altcls-merge`, `altcls-factor`, `atomic-discharge`, `splice-calls`, `tiered-entry`, `engine` (the eleven VM/engine-selection axes, `docs/spec/tuning.md` §2) | yes, but append-only — a new axis is a new value, never a renumbering |
| `order` | a positive integer, 1-based, dense per axis (an axis with N candidates uses 1..N) | yes |
| `candidate` | free text, but always one axis's own stamp vocabulary where a stamp exists (§3's `built`-style closed sets, one per axis) | yes as a vocabulary shape, values are per-axis |
| `kind` | `list` (a real candidate-list-of-objects exists in `emit_dfa.c` and this row's `candidate`/`deny_macro` came straight off it) \| `both` (axis `direction` only — not a preference list; both candidates are ALWAYS emitted, once each, per machine) \| `predicate` (no candidate-list-as-data exists yet; hand-stated from `lib/pcrec.h`'s enum symbols and `tuning.md`'s prose) | yes |
| `stamp_macro` | the `#define` this candidate is reported through (e.g. `RX_DFA_TABLE`, `RX_VM_STRATS`), or empty when no such macro exists — axes `view`/`seed`/`accept`/`direction` have none (emitter-internal decisions with no observable trace), and a few `predicate` axes stamp an ACTIVITY COUNT rather than a named value (`RX_ALTCLS_MERGES`, `RX_VM_CALL_SPLICED`/`_LINKED`, `RX_FAST_FRAMES`) | yes as a vocabulary shape |
| `stamp_value` | the value `stamp_macro` takes when this candidate is chosen — empty when `stamp_macro` is empty OR is a count rather than a name (D82: "the chosen object's name IS the stamp value" holds exactly where this column is non-empty) | free text, but always another column's own value when non-empty |
| `deny_macro` / `deny_bit` | the `PCREC_NO_*` bit (`lib/pcrec.h`) that removes this candidate from the emitter's selection walk, empty when none exists. **Axis `prefilter`'s own missing deny flag is a documented FINDING** (`docs/design/emitter_form.md` §3: the DFA scan's own candidate-start filter has no `-fno-*` knob and no axis sweep), not an omission in this dump | yes |
| `force_macro` / `force_bit` | the `PCREC_FORCE_*` bit that forces this candidate over auto-selection — populated on exactly one axis today (`vm-prefilter`, `PCREC_FORCE_PREFILTER`, `tuning.md` §2.5's one force pair), empty everywhere else | yes |
| `cli_flag` | the `-f`/`-fno-`/`--engine=` spelling that reaches `deny_macro`/`force_macro`, empty for a candidate reached only as a fallback (no flag REQUESTS a fallback; it is what remains when nothing else applies) | free text (an existing CLI spelling, `cli.md` §1) |
| `applies` | a one-line English summary of the candidate's selection condition | free text, hand-authored (see below) |

**BOUNDARY, stated once here because it governs every column above**:
this dump shares its source with the emitter it describes — for the six
`kind=list`/`both` axes, `candidate`/`deny_macro`/`deny_bit` are read
live off the SAME arrays `src/gen/emit_dfa.c`'s own `dfa_select` walks
(`src/parse/axes_dump.c`'s accessor calls), so a new candidate landing
in one of those arrays appears here with no edit to the dump. The
`applies` column, for every row, is HAND-AUTHORED prose (`emitter_form.md`
§3's own "applies when" column, transcribed by a human, for the
`kind=list`/`both` rows; `tuning.md` §2's prose for the `kind=predicate`
rows) — evaluating a real candidate's predicate needs a live pattern a
context-free listing command does not have, so the text is a
description, never a live evaluation. **This dump therefore proves what
the compiler THINKS its own axes are; it is not independent evidence
that a stamp or a flag behaves as described** — `tests/codegen/
run_dfa_stamps.sh` (reads emitted artifacts) and `docs/spec/tuning.md`
§2's own differentials (compile twice, compare answers) are the
independent side of THAT claim. `tests/registry/`'s axis registry check
(§7) is the independent side of THIS dump specifically: it reads this
TSV against `docs/spec/tuning.md` and `cli/main.c`, two files this dump
never opens.

`--list-axes` takes no `--flavour` (§5's own reason: it answers what
THIS BUILD thinks its machinery is, never a claim about PCRE2 syntax)
and no pattern/`-o` — a syntax query, `cli.md` §1.

## 7. What the tests pin, and what they don't

- **`registry_check.c`** (`tests/registry/`) is **pcrec checking
  pcrec** — table-vs-parser self-consistency in both directions, an
  EXACT row count (128, §2), the `roadmap`/`quantifiable`/`class_expect`
  legal-pairing rules, kind coverage, and the D65/D71 derived-column
  assertions (the `defect` outcome, the family AND-rule). It is the
  suite that catches a row naming the *wrong* module or a malformed
  pairing; it cannot catch a row that is plausibly wrong on both sides
  at once, because the wrongness is what both sides read (its own
  `CLAUDE.md`, "pcrec checking pcrec" section, states this as a
  measured limit, not a hedge).
- **PC-3** (`pcre2_check.c`, same directory) is the check that closes
  that gap: it asks **libpcre2**, independently, whether an `RS_MODULE`
  row's construct really exists in PCRE2 and whether an `RS_REJECTED`
  row's diagnostic really matches PCRE2's own rejection — plus several
  generated differentials (byte sweeps, class-bracket doorway,
  POSIX names) with populations in the tens of thousands. This pass
  (`PROCS=4 make test-registry`): registry_check 207/0, PC-3 191/0, pc4
  (the semantic differential, what a produced construct MATCHES cell
  by cell) 0 disagreements over 62,872 compared cells. What PC-3
  guarantees a consumer: every `RS_MODULE`/`RS_REJECTED` row's
  existence-or-non-existence claim against PCRE2 is independently
  checked, not merely self-consistent. What it does NOT guarantee: it
  says nothing about `built` (a pcrec-only fact PCRE2 has no opinion
  on) and nothing about `class_expect`'s exact measured value beyond
  what its own generated cells happen to cover.
- **`compliance_section.py`** (`docs/pcre2_compliance.md`'s generator,
  [SPEC-1.9]) is the same 17-column dump rendered as the page's
  "Registry construct index" — component 1 of that page's three-
  component model (`docs/CLAUDE.md`). Its `COLS` list is a
  transcription of the header, cross-checked against the dump's own
  header line every run (`tests/registry/compliance_section.py:344-383`)
  so the generator and its own column list cannot silently disagree —
  the [SR-11] GENERATOR AGREEMENT check `docs/spec/table_contract.md`
  names, applied to this specific consumer.
- **`axes_registry_check.sh`** (`tests/registry/`, [CHK-2] piece 1) is
  §6's own independent-side check: it reads `--list-axes`'s TSV against
  `docs/spec/tuning.md` §2 (every documented `(bit N)` heading has a
  dumped row at that bit, and vice versa), `cli/main.c` (every
  dumped `cli_flag` is a spelling the parser actually accepts and pairs
  with the dumped `deny_macro`/`force_macro`) and `docs/spec/match_api.md`
  §6.3 (every dumped `stamp_value` is a value that macro's own
  value-set table or string-literal pair lists there, and vice versa —
  the STAMP-VALUE half of the charter's own direction (a), added on
  manager review; the nine D46 bit constants' own value set is read from
  `src/gen/emit_dfa.c`'s literal `#define` block instead, since they are
  emitted-artifact text `lib/pcrec.h` never declares), in BOTH
  directions, every discrepancy named by name rather than by count alone
  (`docs/dev/learnings.md` §3; two named, cited exceptions to the
  spec->dump value sweep, stated in the script's own header). See
  `docs/testing.md` "the axis registry check" for its runtime and
  sabotage validation (53 checks total).

## 8. Landing note

Every column's name and value set above was read from a live
`build/pcrec` at `962e2de` (`gnutimeout 600 make -j4`, clean); no
registry data, source, or `tests/lib/table.sh` resolver was touched to
produce this document. `PROCS=4 make test-registry` ran once this pass:
green (registry_check 207/0, PC-3 191/0, pc4 clean). `make strict`:
clean.

§6 (`--list-axes`) and §7's `axes_registry_check.sh` bullet were added
by [CHK-2] piece 1 (lane `chk2p1`), read from a live `build/pcrec` at
this lane's own branch point; not re-verified against the commit above.
