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

17 columns, confirmed live this pass. 138 data rows
(`build/pcrec --list-syntax | grep -vc '^#'`) — this is the number
`tests/registry/registry_check.c:614`'s exact-count assertion pins
today; **`tests/registry/CLAUDE.md`'s own prose still says "100 since
Q2/SR-9"**, which was true when that paragraph was written and has
since drifted behind six further row-adding modules — flagged here as
the drift the survey brief (A8) asked to name, not corrected in that
file by this pass.

| column | value set | stable? |
|---|---|---|
| `kind` | `esc` \| `group` \| `verb` \| `class-bracket` \| `quant-suffix` \| `bare` — the six `RegKind` doorways (`src/parse/syntax_dump.c` `kind_name`); `quant-suffix` and `bare` have no lexical doorway at all — a possessive suffix is recognised inside `p_rep` after the quantifier already parsed, and `^`/`$`/the plain capturing group `(...)` are parsed directly in `p_atom`/`p_group_body` (manager ruling, 2026-08-29: `RK_BARE`, `RK_QUANTSUFFIX`'s own no-doorway precedent a second time) | yes |
| `selector` | the byte/character after the doorway that selects this row, or `*` for "matches any remaining byte at this doorway" (`REG_SEL_ANY`); 58 distinct values observed (`cut -f2 \| sort -u \| wc -l`) | yes, but not enumerable as a short closed list — read per-row |
| `syntax` | a pattern that PROBES this construct — `tests/reject/` and `--explain` compile it | free text (but every row's value is itself a valid pcrec probe pattern, guaranteed by `registry_check`'s well-formedness pass) |
| `module` | one of 17 module names (`assertions`, `atomic-groups`, `backrefs`, `branch-reset`, `callouts`, `classes`, `comments`, `conditionals`, `extended-classes`, `lookaround`, `misc`, `modifiers`, `named-groups`, `quoting`, `recursion`, `unicode-props`, `verbs`), or empty for `status=base`/`rejected` rows with no owning module | yes |
| `feature` | a hex bitmask (`0x0000`..`0x10000`, 18 distinct values seen) | **not independently named.** `src/parse/syntax_dump.c`'s own header comment states why: `registry.c`'s `M_<module>` macros already pair each bit with a module name, and a second bit->name table here would be a second home for that mapping. Read `module` beside it for the name; `tests/registry/` separately proves the two are a bijection |
| `flavours` | `pcre2` (the only value today — one flavour exists, `--flavour` (`cli.md` §2) filters it; a second flavour is future work, SR-7) | yes |
| `engines` | empty \| `vm` \| `dfa\|vm` — which engine(s) can execute a produced node for this row; empty for rows with no producer yet or no engine question (`status != module`) | yes |
| `status` | `base` \| `module` \| `rejected` — `RegStatus`: is this base-tier grammar, gated behind a module, or a construct pcrec refuses outright | yes |
| `diag` | `none` \| `module` \| `module-octal` \| `fixed` — which diagnostic TEMPLATE this row's refusal uses (`RegDiag`); pairs with `expect` | yes |
| `flags` | empty \| `class-delim` \| `lexical` (mask; both bits can co-occur) | yes |
| `expect` | the SUBSTRING pcrec's diagnostic must contain when this row's syntax is refused — a substring of the doorway's template, not the whole message, so the template itself has one home; empty for the 11 rows that compile cleanly at base tier (127 of 138 rows are non-empty, `cut -f11 \| grep -vc '^$'`) | free text |
| `note` | one-line human description | free text |
| `roadmap` | `-` (the question doesn't arise, base rows) \| `planned` \| `never` — legal pairing with `status`/`diag` enforced by `registry_check` (K14/§17.2): a `never` row must not promise a module in its diagnostic | yes |
| `quantifiable` | `yes` \| `no` \| `form` \| `lexical` \| `-` — whether `<syntax>*` is grammatically legal after this construct, measured against libpcre2 and re-verified by `tests/spec_mod0/check10` | yes |
| `class_expect` | the measured class-POSITION behaviour, e.g. `char 0x08` / `set 246` / `err 137` (34 distinct values seen); **empty — not `-`** — on the 56 group/verb rows that cannot reach a class position at all, per the header's own "empty field = none" rule, distinct from `-` which means "not applicable, the question was asked and doesn't apply" elsewhere in this table | yes as a vocabulary shape (`char N` / `set N` / `err N`), values themselves are per-construct facts |
| `built` | `built` \| `unbuilt` \| `defect` \| `-` — **D65's column; see §3** | yes |
| `family` | the canonical `syntax` of the family this row is a spelling of, empty when the row is its own family — **D71 item 3's column; see §5** | free text (but its value, when set, is always another row's own `syntax`) |

Live counts this pass (`build/pcrec --list-syntax \| grep -v '^#' \|
cut -f16 \| sort \| uniq -c`): `built` 106, `unbuilt` 16, `-` 16, `defect`
0 — 138 total, matching `registry_check.c:2956`'s own pinned
`checked/built/unbuilt/na` tuple (138/106/16/16) exactly.

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
refusal shape (measured 0 of 138 rows today).

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

`build/pcrec --list-families | grep -vc '^#'` — 100 rows against
`--list-syntax`'s 138 (38 rows carry a non-empty `family`, collapsing
into their canonical row: `138 - 38 = 100`, confirmed). 7 columns:

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
are today's largest families; 88 of the 100 families have exactly one
member.

`--list-families` takes no `--flavour` filter — `cli.md` §2 states why
(a family is a grouping OF rows; filtering members mid-grouping would
make one invocation's `built` answer a different question than
another's, `cli/main.c:517-523`'s own comment).

## 6. `--list-axes` — the optimization-axis registry (the FOURTH surface, [CHK-2])

`build/pcrec --list-axes | grep -vc '^#'` — 47 rows / 19 axes at abi 11
(this moves with every axis landing — [OPT-4]'s pending merge is the
next one — so it is stated as a live count rather than a number to
trust), 12 columns, confirmed live this pass. Where the first three surfaces describe
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
| `axis` | 19 values today: `table`, `prefilter`, `view`, `seed`, `accept`, `direction`, `match` (the seven DFA layer-1 axes, `docs/design/emitter_form.md` §3 and, for `match`, `docs/design/anchored_match_unwrapped.md` §5.1) plus `possessify`, `revdet`, `counter`, `length-prune`, `vm-prefilter`, `altcls-merge`, `altcls-factor`, `atomic-discharge`, `splice-calls`, `tiered-entry`, `size-term`, `engine` (the twelve VM/engine-selection axes, `docs/spec/tuning.md` §2 — `size-term` is [ART-SIZE]'s `--unroll=K` re-selection axis, added after this section was first written) | yes, but append-only — a new axis is a new value, never a renumbering |
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
  EXACT row count (138, §2), the `roadmap`/`quantifiable`/`class_expect`
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

## 9. `--list-definitions` — the replacement/definition table (the FIFTH surface, D85/[DD-11.2])

`build/pcrec --list-definitions | grep -vc '^#'` — 49 rows today (grows
as the remaining census items land, see below), 7 columns:

    #kind  selector  syntax  order  predicate  definition  applies

| column | value set | stable? |
|---|---|---|
| `kind`/`selector`/`syntax` | the SAME three columns §2 prints for the owning row — reused through the SAME rendering helpers (`src/parse/syntax_dump.c`'s `kind_name`/`put_selector`/`put_str`), not a second independent rendering, which is what makes joining the two dumps on these columns safe rather than merely convenient | yes |
| `order` | a positive integer, 1-based, dense per row (a row with N `definitions` entries uses 1..N) | yes |
| `predicate` | the option-scope TAG's own name (`DEF_ALWAYS`, `DEF_MULTILINE`, `DEF_NOCAP`, `DEF_UCP`, `DEF_ENCODING_UTF8`, `DEF_NEWLINE_CONV`, `DEF_LIB_NAME_BOUND` — the closed enum `DefTag`, `src/core/internal.h`), never hand-authored prose — the predicate column and a stored callable were two derivations of one fact (r43's ruling), and the tag name is the one that survives | yes, closed vocabulary |
| `definition` | the core-syntax TEXT for a `DEFK_STR` entry (itself a valid pcrec probe pattern, `syntax`'s own convention); a human-readable TEMPLATE for a `DEFK_TEXTFN` entry (e.g. `\cX = byte (X xor 0x40)` — never spliced, never a live evaluation); the row's OWN `syntax` restated for a `DEF_IDENTITY` entry (nothing substitutes); or the literal text `<builder>` for a `DEFK_BUILDER` (AST-operand) entry, which has no pattern text to show | free text for `DEFK_STR`/`DEFK_TEXTFN`; `<builder>` is a fixed literal; `DEF_IDENTITY` echoes `syntax` |
| `applies` | `active` (this entry substitutes a different construct) or `identity` (restates the row's own primitive form) | yes, closed vocabulary — **read directly from the entry's `DefKind`** (manager ruling: identity is an explicit `DEF_IDENTITY` entry, never inferred from absence); two rows use `identity` today — `^`'s non-multiline `DEF_ALWAYS` entry (the row's own primitive form, `A_BOL`, genuinely is core — `\A`'s alias) and the `(?n)`-scoped capturing group's `DEF_ALWAYS` entry (an ordinary `A_CAP`, unaffected by `(?n)` outside its scope). `$`'s non-multiline `DEF_ALWAYS` entry is deliberately NOT `identity`: the structural check (`tests/registry/definitions_check.c`'s `check_str_entry(owner, r->syntax)` extension) proved `A_EOL` is not core under full reduction — it aliases `\Z`, which itself reduces to `(?=\n?\z)` — so that entry carries the real substitution instead, matching `\Z`'s own row |

**BOUNDARY, stated once here because it governs every column above**:
this dump shares its source with the resolver it describes.
`kind`/`selector`/`syntax`/`predicate`/`definition` are read live off
the SAME `RegRow.definitions` arrays `pcrec_def_resolve`
(`src/parse/definitions.c`) walks at option-resolution time — one
derivation, two readers, `--list-definitions`'s own instance of the
principle `--list-axes` (§6) and `--list-syntax` (§2) already state.
**This dump therefore proves what the table THINKS its definitions
are; it is not independent evidence that a definition string parses to
core-only vocabulary, or that it MATCHES the same strings as the
construct it stands for.** The first is
`tests/registry/definitions_check.c`'s structural check (every
`DEFK_STR`/POSIX definition parses under `--features all`, every
builder's and `DEFK_TEXTFN`'s output passes `pcrec_ast_all_core`,
`src/parse/definitions.c`'s own exhaustive `AKind` switch — plus a
static well-formedness sweep: every non-NULL `definitions` list ends
in a `DEF_ALWAYS` entry, so `pcrec_def_resolve`'s fallthrough path is
an `assert`, never a silent NULL); the second is [DD-11.3]'s
option-matrix self-oracle, not yet built — see docs/design/
definitions_table.md §3/§6 for both. `tests/registry/
run_definitions_tests.sh`'s containment grep is a third, narrower
claim: that the tag evaluator (`pcrec_def_tag_applies`) is reached
from exactly one call site, so `predicate`'s values cannot be
second-guessed by a hidden second evaluator anywhere in the tree.

`--list-definitions` takes `--flavour` exactly as `--list-syntax` does
(r43 K6, reversing the design note's first-pass "no"): it walks the
same `RegRow`s, filtered identically, so an unfiltered dump would
print a definition for a construct `--list-syntax --flavour=X` says
does not exist under that flavour. It takes no pattern/`-o` — a syntax
query, `cli.md` §1.

**Four `DefKind`s reach this dump today**, two more than the design
note's first pass: `DEFK_STR` (a fixed core-syntax string — the
class-escape family, `\R`, `\b`/`\B`, the fixed literal escapes, and
the POSIX named-class row's 14 names, each its own entry since the
family is a FINITE enumerable set rather than an unbounded operand
space); `DEFK_BUILDER` (an AST-operand function — the possessive-suffix
family, `(?n)`); `DEFK_TEXTFN` (manager ruling: the general shape for
"a binding parameterized by TEXT AT THE OCCURRENCE" — `\cX`, bare `\x`,
`\o{}`, octal/`\0`, `\N{U+}` — each carries a human-readable TEMPLATE
for this column plus a function that calls the EXISTING decoder where
one exists, becomes the first decode site where none does yet, per
`\R`'s own precedent for an unbuilt construct); and `DEF_IDENTITY`
(manager ruling: the row's own primitive form, an EXPLICIT entry never
inferred from an absent one — [DD-13]'s stamp-design lesson applied
here). Now used by three rows, all on `RK_BARE` (below).

**`RK_BARE` (manager ruling, 2026-08-29): a new no-doorway `RegKind`,
on `RK_QUANTSUFFIX`'s own precedent** — consulted by the dumps and by
this table's own definitions machinery, by nothing on the live parse
path. Three rows: `^`, `$`, and the plain capturing group `(...)`,
which is what closes the gap the paragraph below used to describe as
open. `^`, `$` and `(...)` are base grammar parsed directly in
`p_atom`/`p_group_body` with no doorway, unlike the literal escapes
(which route through the real `\` doorway even when answered before
reaching the registry); `RK_BARE` gives them a table row without
adding a lookup to that path — the dumps and `pcrec_def_resolve` reach
these rows by iterating `all_kinds`/`pcrec_registry()`, never by a
parse-time dispatch, exactly as `RK_QUANTSUFFIX` already does not cost
the base tier a lookup on every quantifier. `RK_COUNT` bumped; every
`RK_COUNT`-shaped guard in the tree re-measured from a live run rather
than computed by hand (`tests/registry/CLAUDE.md`'s own count
citations, `tests/registry/registry_check.c`'s row/family/built-status
tuples, `tests/registry/pcre2_check.c`, `compliance_section.py`,
`tests/cli/run_cli_tests.sh` case10's noroute set).

Each `RK_BARE` row's `definitions` carries a real option matrix
rather than a single entry: `^`'s `DEF_MULTILINE` substitution is
`\A|(?<=\n)(?!\z)`, falling through to a `DEF_IDENTITY` `DEF_ALWAYS`
entry (`A_BOL`, `^`'s own non-multiline form, genuinely is core —
`\A`'s alias, per the design note's full-reduction census). `$`'s
`DEF_MULTILINE` substitution is `(?=\n)|\z`, falling through to a
`DEFK_STR` `DEF_ALWAYS` entry, `(?=\n?\z)` — **not** `DEF_IDENTITY`:
the structural check (`tests/registry/definitions_check.c`'s
`check_str_entry(owner, r->syntax)` extension for `DEF_IDENTITY`
entries) FAILED here, proving `A_EOL` is not core under full
reduction — it aliases `\Z`, which itself reduces to `(?=\n?\z)`, so
this row's `DEF_ALWAYS` entry is a real substitution matching `\Z`'s
own row, not the identity the manager's original ruling assumed. The
capturing-group row's `DEF_NOCAP` entry is `DEFK_BUILDER`
(`pcrec_def_build_identity`, `(?n)`'s existing no-op builder — reused
rather than duplicated), falling through to a `DEF_IDENTITY`
`DEF_ALWAYS` entry (an ordinary `A_CAP`, unaffected by `(?n)` outside
its scope).

`\x{...}` (braced hex) still has no row of its own, but not for the
reason this paragraph used to give: the manager's `RK_BARE` ruling
also settled that a definitions row costs no lookup on the base path
(`src/parse/CLAUDE.md`'s "no LOOKUP on the base path" rule is about
dispatch, not about a table entry dispatch never consults), so `\x{...}`
and bare `\xHH` are declared ONE construct with two spellings, sharing
ONE row — the pre-existing bare-`\x` `RK_ESC`/`RS_BASE` row, whose
`DEFK_TEXTFN` template now names both forms (`\xHH or \x{HHHH} = byte
HH..HHHH (hex)`) and whose textfn (`pcrec_def_text_hex`) is the one
decode site for both. `parse.c`'s own braced-form diagnostic is
unmoved — it stays exactly where it was, a base `\x` special case with
no doorway, per `src/parse/CLAUDE.md`'s registry section.

`\Q...\E` stays excluded from this table, and by a different rule than
either of the above: it is LEXICAL — a delimiter pair the lexer strips
before any construct is recognised, never itself a construct with a
core-syntax equivalent — so it earns no row and no `DefKind` at all
(manager ruling, distinguishing it from `(?x)`, the design note's other
excluded item, in `docs/design/definitions_table.md` §1).

Neither is `[DD-11.5]`'s wiring-into-real-compilation step, which stays
gated on M6.6's exact one-byte-fixed-lookbehind lowering per the design
note's own §4.

**This pass**: `build/pcrec --list-definitions` read live at this
worktree's own HEAD; `bash tests/registry/run_registry_tests.sh` and
`tests/registry/run_definitions_tests.sh` both green (the latter still
standalone — see tests/registry/CLAUDE.md's note — pending the table's
population settling); `make strict` clean.
