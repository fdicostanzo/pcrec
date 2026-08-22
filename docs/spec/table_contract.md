# The table contract — tabular output from pcrec commands

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

## Scope

Every pcrec command whose output is a DATA TABLE:

| command | table | status |
|---|---|---|
| `--list-syntax` | the syntax construct registry (SR-1/D24) | conforming producer today |
| `--list-verbs` | the (*VERB) name table | conforming producer today |

Future tabular surfaces adopt this contract AT BIRTH — a new table
command that does not conform is a defect, not a style choice.

NOT in scope today, with different dispositions:

- `--emit-ir` — TO BE CONSIDERED (Frank, 2026-08-21): the body is a
  program LISTING (checked by tests/codegen/run_ir_listing.sh), but its
  tabular SECTIONS (the slot legend, the label table) are candidates for
  this contract, and the listing as a whole may deserve a sibling
  line-oriented contract (a header declaring its section structure, so
  its consumers — run_ir_listing.sh's extractors, which have already
  gone stale once this session — parse by declaration rather than by
  remembered shape). Decided when [DD-8] (the row that owns --emit-ir)
  next opens; DD-8's standing constraint holds regardless: the listing
  derives from the same walk the emitter does, never a parallel
  description.
- `--trace` output — an EVENT STREAM from an instrumented matcher; its
  enrichment is [V-H]'s design territory. If a future trace mode emits a
  table, that table adopts this contract at birth.

## The producer contract

1. Output is TAB-separated values, one row per record, `\n` line ends.
2. Lines beginning `#` are COMMENTS — free prose, ignored by parsers.
3. The LAST `#` line before the first data row is the HEADER: `#` followed
   immediately by the column names, tab-separated, in on-the-wire order
   (today: `#kind<TAB>selector<TAB>syntax<TAB>...`).
4. Columns are APPENDED ONLY — never inserted, renamed, or reordered
   (SR-4's rule, generalized). A new column lands after the last existing
   one, with a `#` comment line above the header describing it (the D65
   `built` column's comment is the model).
5. An empty field means "none"; a field never contains a TAB (which is
   what makes rule 1 checkable per row).

## The consumer contract

1. Resolve columns BY HEADER NAME, never by hardcoded field count and
   never by bare position. (An awk consumer builds a name->index map from
   the header row; a C consumer reads the header line first. The house
   exemplar is tests/spec_mod0/spec_common.h's loader — written blind,
   years before D65, and the only consumer that survived the D65 column
   unchanged.)
2. Unknown trailing columns MUST be ignored — trailing-safety is what
   rule 4 above buys, and a consumer that breaks on an appended column
   has violated this contract, not been broken by the producer.
3. A consumer MAY assert the field count only as EQUALITY WITH THE
   HEADER's declared count (an integrity check: no tab leaked into a
   field) — never as a literal number. The D65 incident is the evidence:
   two consumers hardcoding `NF != 15` broke on a legitimate append;
   the header-deriving consumer did not.

## Sections (optional, backwards-compatible)

Added by Frank, 2026-08-21, same session: multi-table output — the
`--emit-ir` shape, where one command's output holds several tables with
DIFFERENT columns (a slot legend, a label table) — gets a SECTION
mechanism rather than forcing one flat schema.

1. A section is announced by a SECTION line: `#section NAME` (a `#` line
   whose first word is `section`; NAME is a bare word, the section's
   stable address). It is followed by that section's own comments and its
   own HEADER line (rule 3 applies per section: the last `#` line before
   a section's data is that section's header), then its data rows, until
   the next `#section` line or end of output.
2. BACKWARDS COMPATIBLE BY ABSENCE: output with no `#section` line is a
   single anonymous section — byte-for-byte today's format, and existing
   consumers are untouched. `--list-syntax`/`--list-verbs` stay
   sectionless unless a real second table ever needs to join them.
3. Section NAMES are the API: append-only as a set (a name, once
   shipped, keeps its meaning; new sections may be added), and each
   section's columns follow the producer contract independently
   (append-only within the section).
4. Consumer rules: a section-aware consumer SELECTS its section by name
   and parses within it under the ordinary consumer contract; a consumer
   reading a multi-section stream without selecting MUST fail loudly
   rather than silently parse rows across section boundaries (rows from
   a section whose header it never read are not data, they are someone
   else's data).

`--emit-ir` remains [DD-8]'s adoption decision; this section exists so
that when it (or an enriched [V-H] trace table) adopts, the mechanism is
already ruled and no flat-schema contortion is needed.

## The checks ([SR-11] lands these)

- HEADER TRUTHFULNESS: every data row's field count equals the header's
  declared count (this is the correct final form of tests/cli case10).
- GENERATOR AGREEMENT: any checker that carries its own column list
  (tests/registry/compliance_section.py's COLS) cross-checks it against
  the emitted header, so the generator and its checker cannot disagree
  silently.

## History

D65 appended the 16th column (`built`) and two consumers broke on
hardcoded field counts while six trailing-safe consumers did not; the
complete format-consumer survey and the CONTENT-vs-FORMAT consumer
distinction live in docs/design/registry_built_status_memo.md's
Correction section. This contract exists so the next append is a
non-event.
