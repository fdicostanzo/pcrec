# The table contract -- record of the removed history

FROZEN. Not normative. The history `docs/spec/table_contract.md` carried until its facts-only rewrite (lane specreg, `[SPEC-CLEAN]`), moved verbatim. The complete old text is `git show 43cec6c0:docs/spec/table_contract.md`. Each block is tagged with the old section and line range.


## [old preamble (charter and status), lines 3-12]

Chartered by Frank, 2026-08-21 (thirty-fifth session), generalizing
[SR-11]: "if it was meant to be read, it might be prep'd for it —
#comments are ignored and a #header:col1 col2... row." This document IS
the contract; [SR-11] tracks converting the in-tree consumers and landing
the checks. Status: CONTRACT RULED; [SR-11] parts 2-3 LANDED 2026-08-21 —
tests/lib/table.sh is the one implementation, tests/reject/
run_reject_tests.sh's row iterator and tests/cli/run_cli_tests.sh's case10
and tests/spec_mod0/check09_every_feature_toggles.sh are converted, and both
checks below (HEADER TRUTHFULNESS, GENERATOR AGREEMENT) are landed and
sabotage-validated.

## [old Scope table (status cells with dates and landing notes), lines 16-31]

Every pcrec command whose output is a DATA TABLE:

| command | table | status |
|---|---|---|
| `--list-syntax` | the syntax construct registry (SR-1/D24) | conforming producer today |
| `--list-verbs` | the (*VERB) name table | conforming producer today |
| `--list-definitions` | the replacement/definition table (D85/[DD-11.2]) | conforming producer today |
| `--list-families` | the construct-family index (D71 item 3) | conforming producer today |
| `--list-axes` | the optimization-axis registry ([CHK-2] piece 1) | conforming producer today; gained ONE named section after its anonymous main table at [MEMFN] R4a (`memfn`, the kit's option registry, `registry.md` §6) — `--list-source`'s shape |
| `--list-limits` | the numeric-limits table (D90/[LIM-1]) | conforming producer today |
| `--list-source` | the `.rxt` SOURCE file, as written ([DD-13b.W1.1], `docs/spec/rxt_format.md`) | conforming producer today; gained the Sections mechanism at [DD-13b.W23.4] (`provenance`/`variants`/`cases`/`aux`, emitted unconditionally when non-empty, always after the main table) |
| `--list-schema` | the `.rxt` FORMAT's own schema ([DD-13b.W23.1], `docs/spec/rxt_format.md`) | conforming producer today, and the FIRST to use the Sections mechanism below |
| `--emit-ir` | the VM program listing ([DD-8], `docs/spec/ir_listing.md`) | conforming producer since 2026-09-19; the mechanism's THIRD producer and the first whose every table is a named section |
| `--emit-facts` | the pattern-facts record listing ([PATFACTS] step 3.0, `docs/spec/facts_listing.md`) | conforming producer AT BIRTH (2026-09-26): two named sections, `facts` and `decisions`, no anonymous table |
| `--list-analyses` | the analyses built into the library ([FINDINGS] B2, `docs/spec/findings.md` §8) | conforming producer AT BIRTH (2026-09-27): one anonymous table (a single-table dump, rule 2) |
| `--list-analysis` | what one analysis NAME, or each target of one `.rxt` FILE, resolves to ([FINDINGS] B2, `docs/spec/findings.md` §8) | conforming producer AT BIRTH (2026-09-27): every table a named section (`chain`, `resolution`, one per data kind, `declarations`, `provenance`; or `targets`, `chain`, `resolution`). Its free-text columns — `question`, `reader`, `analyzer`, a provenance `value`, a `location` path — pass through the producer rule 5 escaping (`pcrec_sb_text`: a TAB or control byte becomes `\xNN`), since a user bundle's prose may carry a TAB; the hex `key` and decimal `count` columns need none by grammar. `tests/findings/run_findings_tests.sh` §11 checks HEADER TRUTHFULNESS on every section and the escaping on a TAB-bearing fixture |

## [old Scope, future surfaces and out-of-scope, lines 33-40]

Future tabular surfaces adopt this contract AT BIRTH — a new table
command that does not conform is a defect, not a style choice.

NOT in scope today, with different dispositions:

- `--trace` output — an EVENT STREAM from an instrumented matcher; its
  enrichment is [V-H]'s design territory. If a future trace mode emits a
  table, that table adopts this contract at birth.

## [old Sections, charter note, lines 75-80]

Added by Frank, 2026-08-21, same session: multi-table output — the
`--emit-ir` shape, where one command's output holds several tables with
DIFFERENT columns (a slot legend, a label table) — gets a SECTION
mechanism rather than forcing one flat schema.

1. A section is announced by a SECTION line: `#section NAME` (a `#` line

## [old Sections, adoption notes, lines 110-148]

`--emit-ir` ADOPTED, 2026-09-19 ([DD-8]); an enriched [V-H] trace table
would adopt the same way. The mechanism was ruled three steps ahead of its
hardest customer precisely so that no flat-schema contortion was needed when
that customer arrived, and none was: D106 addendum item 1's finding is that
the program BODY fits columns (`label|op|args|target|note`), so the
"sibling line-oriented contract" this document's earlier note reserved
judgement on was never needed.

**[DD-13b.W23.1] `--list-schema` IS THE MECHANISM'S FIRST PRODUCER**, and
it names BOTH its sections (`schema`, `surface`) rather than leaving the
first anonymous. Rule 2's backwards-compatible-by-absence shape means a
single-table dump may stay anonymous, but a multi-section one may not
leave one section unnameable: consumer rule 4 requires a reader to SELECT
its section by name, and an anonymous first section is the one table no
conforming consumer can ask for.

**[DD-8] `--emit-ir` IS THE MECHANISM'S THIRD PRODUCER AND THE FIRST WHOSE
EVERY TABLE IS A NAMED SECTION** (`summary`, `slots`, `rungs`, `strategies`,
`pruning`, `program`, `choicepoints`, `islands`, `callouts`), with no
anonymous table at all. It is also the first producer whose sections have
DIFFERENT column counts from one another (2, 3, 4 and 5), which is the shape
rule 3's "each section's columns follow the producer contract independently"
was written for and which `--list-schema`'s two ten- and four-column
sections only half exercised. Its own section-and-column contract —
including the vocabulary of its `prefilter` value and its `op` column, and
the rule that an empty population is a ROW rather than a comment (because
rule 3 would make a trailing comment inside an empty section that section's
header) — is `docs/spec/ir_listing.md`.

**[DD-13b.W23.4] `--list-source` IS THE MECHANISM'S SECOND PRODUCER, AND
THE FIRST WHOSE MAIN TABLE STAYS ANONYMOUS WHILE GAINING NAMED SECTIONS
AFTER IT** (`provenance`/`variants`/`cases`/`aux`) — a shape rule 2's own
wording already permits ("a single-table dump may stay anonymous") but
`--list-schema` never exercised, since both of ITS sections are named.
`--list-source`'s own main table pre-dates the Sections mechanism by two
steps ([DD-13b.W1.1]) and stays unnamed for the same backwards-
compatibility reason a pre-existing table always may; only the FOUR
BLOCKS APPENDED AFTER IT are named, per rule 3.


## [old The checks, heading, lines 149-150]

## The checks ([SR-11] lands these)


## [old History, lines 158-174]

## History

D65 appended the 16th column (`built`) and two consumers broke on
hardcoded field counts while six trailing-safe consumers did not; the
complete format-consumer survey and the CONTENT-vs-FORMAT consumer
distinction live in docs/design/registry_built_status_memo.md's
Correction section. This contract exists so the next append is a
non-event.

[DD-13b.W1.1] (r46sem finding 9, FIXED): `--list-source` landed
([DD-13b.W1.1]) claiming this contract in both `docs/spec/rxt_format.md`
and `docs/spec/cli.md` without a row here naming it, and `docs/spec/
cli.md`'s own "Six TSV dumps" had been true against the CLI (`--list-
syntax`, `--list-verbs`, `--list-definitions`, `--list-families`,
`--list-axes`, `--list-source`) while this Scope table listed only
three of the six — a pre-existing gap this fix closes in full rather
than adding one more row to a table already known short two others.
