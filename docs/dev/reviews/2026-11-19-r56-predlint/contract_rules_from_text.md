# Rules L1-L11 as read from doc_format.md ALONE (written before opening the script)

Source: R/subject/doc_format.md (SUBJECT 7ace76e8f). Line refs are that file's.

## Definitions the rules depend on

- FILE SET (§The files, l.23-27): base core = `docs/design/predicates.md`, lib = `docs/design/predicates_library.md`,
  parked = `docs/design/predicates_parked.md`; details = `predicates_details.md`, `predicates_library_details.md`,
  `predicates_parked_details.md` (directory not stated; presumably `docs/design/`). RECORD = 
  `docs/design/plan_row_bodies/COND-FAMILY.md` (l.30). READ ORDER: core < lib < parked (l.21, l.77).
- TAG (l.36-39): `/`-joined lower-case kebab words; first word in {core, lib, parked}; exactly 3 or 4 words.
  Predicate: `^(core|lib|parked)(/[a-z]+(-[a-z]+)*){2,3}$`. OPEN: are digits allowed in a "word"? text says
  "lower-case kebab words" — digits unstated.
- SECTION: "every piece sits in a section" — the section's syntax in the base file is NOT stated (presumably a `## <section>`
  heading whose name equals tag word 2). OPEN.
- `was:` line (l.38-39, l.74): a moved piece's path check reads it. Placement/format not stated (presumably in the piece,
  `was: <old path>` or old tag). OPEN.
- BASE PIECE (l.42-47): heading `### <name>   [<tag>]   <status> <date>`; next line = statement; optional `needs:`
  line; optional `by:` line whose tags are `core/principles/<p>`; definition; example line.
  Date format not stated (presumably YYYY-MM-DD). Whether `?` carries a date: not stated.
- STATUS (l.50-53): `ruled` | `reading` | `open <slug>` | `under-construction` | `parked` (parked file only) | `?`.
- DETAILS ENTRY (l.56-62): heading `## <tag> — <name>`, one per tag, same order as the base; fields `slugs:`,
  `rulings:` (items `- <date> "<words>" (record: "<entry title>")`), `rejected:`, `readings:`, `evidence:`, `history:`.
- RECORD TITLE: "record title EXISTS in the record" — what counts as a title in COND-FAMILY.md is not stated (presumably
  an entry heading). OPEN.
- SHARED line (l.80): a `shared:` line "at the head of a details file", listing slugs exempt from L9.
- RATCHET (l.53, l.81): a stored count of `?` pieces that may only go down. Storage not stated. OPEN.

## The rules as predicates, with crafted cases

L1 tags unique: no tag appears on two base pieces (across all three base files).
  bad: two `### x [core/a/b] ruled 2026-11-19` (same file or different files). good: distinct tags.
  edge: is a duplicate details heading an L1 or L3 fault? (either is acceptable; must be caught by one.)

L2 (a) every base tag and details-heading tag matches the TAG grammar; (b) a base piece's tag word 1 equals its file
  (predicates.md->core, _library->lib, _parked->parked) and word 2 equals its enclosing section, UNLESS a `was:` line
  explains it.
  bad: `[core/Holes/class]`, `[core/holes]` (2 words), `[core/a/b/c/d]` (5), `[lib/x/y]` in predicates.md,
  `[core/other/y]` under section `holes` without `was:`. good: same with a `was:` line; 4-word tag.

L3 for each base/details pair: the sequence of base tags == the sequence of details-entry tags (bijection AND order).
  bad: details missing a tag; details extra tag; same set in swapped order; details entry in the wrong file's details.

L4 (a) status in the set; (b) `open` followed by a slug; (c) `parked` only in the parked file; (d) a `ruled` piece's details
  entry has >=1 `rulings:` item whose `(record: "<title>")` title exists in the record.
  bad: `ruled-ish`, bare `open`, `parked` in predicates.md, ruled with no rulings item, ruled whose only item names a
  title absent from the record. good: ruled with one existing title plus one missing? (text: "at least one ... EXISTS"
  -> passes literally.)

L5 (a) every tag on a `needs:` or `by:` line exists as a base piece; (b) a `needs:` target is earlier in read order
  (file rank core<lib<parked; template l.44 "all earlier in the order" may also mean an earlier piece within the same file —
  ambiguity). (c, template l.45 not in L5) `by:` tags are `core/principles/*`.
  bad: `needs: core/x/missing`; core piece `needs: lib/a/b`; `by: core/x/missing`. edge: core piece needs a LATER core
  piece; `by: lib/a/b` (exists, not a principle).

L6 no history in a base file: none of revision marks (`[REV`), review ids (e.g. `r56`, `review r12`), "withdrawn",
  "reversed", dates other than the heading's status date.
  bad: "withdrawn" in a definition; `[REV28]`; "review r12"; `2026-01-01` in a body line. good: dated heading only.

L7 statement length <= 200 chars (HARD); piece <= 40 lines (HARD, extent presumably heading to next heading);
  base file sizes core 64 KB, lib 24 KB, parked 16 KB: SOFT — reported, exit status unaffected.
  bad: 201-char statement; 41-line piece. soft: 65 KB core reports but passes. boundary: 200 chars, 40 lines pass.

L8 every piece not exempt has an example line naming all three of WHOLE, SEARCHED, FIND-ALL, or saying `modes: n/a`.
  Exempt: status `parked`, status `under-construction`, principle pieces (tag core/principles/*). NOT exempt per text:
  `ruled`, `reading`, `open`, `?`.
  bad: ruled piece with only WHOLE and SEARCHED; `?` piece with no example (literal text says bad). good: `modes: n/a (x)`.

L9 every slug on any details `slugs:` line belongs to one tag only (across all details files), unless the slug is on a
  `shared:` line at the head of a details file.
  bad: slug `foo` under two tags. good: same, with `shared: foo` at head. edge: `shared:` not at the head (mid-file) ->
  should not exempt; shared in a different details file than the duplicate.

L10 count of `?`-status pieces <= the stored ratchet value (only shrinks).
  bad: one more `?` than recorded. good: equal or fewer.

L11 each base file has >=1 piece (non-vacuity); presumably a missing file also fails.
  bad: an empty predicates_parked.md; a base file with only section headings.

Not linted per the text (by omission from L1-L11): "ONE sentence, present tense"; principle quotes the owner; one
commit rule. Selftest: one plant per rule (l.82).
