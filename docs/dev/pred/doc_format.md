# The predicate documents: base + details, linked by tags (the format)

STATUS: PILOTED 2026-11-19 (lane preddoc1: the skeleton, `core/principles` and `core/holes` in full; lint clean,
1,828 checks). PROPOSED by the predicate manager 2026-11-19 on the owner's request and delegation (COND-FAMILY, "housekeeping:
organize the predicate documentation" and its two addenda: "keep, modify, or reject these instructions as you reason
it better"). Not built: the pilot (the skeleton and the holes section) follows revision 29.1. Modelled on the tracker
pair ([DOC-INDEX], D192, `docs/dev/doc_format.md`); the facts it rests on are in the census
`$PCREC_TMPDIR/scratch/predcensus/facts.md` (2026-11-19: 155 ruling entries, about 100 question slugs, 72 candidate
provided names, 17 recurring principles, 36 parked items; rejections marked by six different words with no uniform
reason field).

## What the files are for (the uses that shape them)

1. WAKE: a session reads the BASE files whole and knows the current language, the library and what is parked.
2. BEFORE ASKING the owner anything: every ruling bearing on a piece is reached from the piece, and from the SLUG he
   answered under.
3. WHEN HE SPEAKS: his words go into the record once, whole, the same hour; the pieces they touch are updated in the
   same commit.
4. WHEN FORMING A LEANING: what was REJECTED and why, and the PRECEDENTS (pieces decided by the same principle), are
   found by tag, without reading the record.

## The files (read in this order; a file uses only what is before it)

| base (current definition) | details (history, reasoning) | holds |
|---|---|---|
| `docs/design/predicates.md` | `predicates_details.md` | section `principles` first (his method), then the core language |
| `docs/design/predicates_library.md` | `predicates_library_details.md` | every PROVIDED name: a body in the core language, or "primitive" |
| `docs/design/predicates_parked.md` | `predicates_parked_details.md` | ideas and directions not in the language, each with a trigger |

Not converted, on purpose (the tracker design's own rule: an append-only raw log keeps its shape):
`docs/design/plan_row_bodies/COND-FAMILY.md` stays THE RECORD, one chronological log, the only source of rulings; each
new entry gains a line `tags: <tag> <tag>`. Evidence directories and filed reviews stay where they are. The old draft
`predicates_draft.md` is FROZEN at its last revision and is the source the details files are cut from.

## Tags, pieces, status

- A TAG is a path of lower-case kebab words: `<file>/<section>/<piece>[/<sub>]`, file one of `core`, `lib`, `parked`
  (`core/holes/class`, `core/principles/regex-default`, `lib/modifiers/padded`); three or four words, so every piece
  sits in a section. Tags are never renamed; a moved piece keeps its
  tag and the lint's path check reads a `was:` line. Cross-references are bare tags, never line numbers or § numbers.
- A base PIECE:

      ### <name>   [<tag>]   <status> <date>
      <statement: ONE sentence, at most 200 characters, present tense, the current rule>
      needs: <tag> ...            (what must be read first; all earlier in the order)
      by: core/principles/<p> ... (the principle(s) it was decided by; optional)
      <the definition: rule sentences, a table where the piece is one; no history>
      <one example, in WHOLE | SEARCHED | FIND-ALL, or "modes: n/a (<why>)">

  SCANNING the base = the heading and statement lines only; READING it whole = everything.
- STATUS: `ruled` (the owner ruled it) | `reading` (the draft's or the manager's, not ruled) | `open <slug>` (a
  question for him: the body is the current definition labelled as a reading, or a summary of the standing
  discussion, and the candidates) | `under-construction` (a direction acknowledged, not defined) | `parked` (parked
  file only) | `?` (converted, statement not yet written; counted by a ratchet that only shrinks).
- A details ENTRY, one per tag, in the same order as the base:

      ## <tag> — <name>
      slugs: <every question slug asked about this piece>
      rulings:   - <date> "<his words, verbatim>" (record: "<entry title>")
      rejected:  - <the candidate> — by <owner ruling | run | review rN> — <the reason, with its witness>
      readings:  - <a manager's or draft's reading> — SUPPORTED | NOT SUPPORTED | UNTESTED (<evidence pointer>)
      evidence:  <lane evidence dirs and PART names>
      history:   <dated blocks: what the piece used to say, review items, discussion>

## Rules of use

- A new ruling = the record entry (with its `tags:`), the base piece and the details entry in ONE commit; a ruling
  that changes an EARLIER piece rewrites that piece's status and statement in the same commit.
- The base never carries history: no revision marks, review ids, "withdrawn", "reversed", dates other than the
  status date. Everything of that kind is in the details entry.
- A principle piece quotes the owner; a name the manager gave it ("stated behaviour") is marked as the manager's.

## Lint (structure; requested from main, which owns `scripts/`)

L1 tags unique; L2 tag grammar, and the tag's path equals the piece's file and section (or a `was:` line); L3 base
pieces and details entries are in bijection, same order; L4 status in the set, `open` carries a slug, a `ruled`
piece's details has at least one `rulings:` line whose record title EXISTS in the record; L5 every `needs:` and
`by:` tag exists, and a `needs:` target is earlier in the read order (core before lib before parked); L6 no history
in a base file (the word list above; `[REV`); L7 caps: statement 200 characters and piece 40 lines HARD; base file
SOFT (core 64 KB, library 24 KB, parked 16 KB: reported, never refused); L8 an example line names the three modes or
says `modes: n/a` (not asked of a `parked` or `under-construction` piece, nor of a principle); L9 every slug in a details `slugs:` line is unique to one tag or listed on a `shared:` line at the head of a
details file; L10 the `?`
ratchet only shrinks; L11 a non-vacuity floor (a file with no pieces fails). A planted-fault selftest, one plant per
rule. Reader (one, review r56 ROBUST-11): the files registered as a profile of `scripts/entry` (`entry core/holes/class`: level 0 the heading and
statement, 1 the piece, 2 the details entry; `entry <slug>` finds the piece by slug).

### What the lint checks beyond the rule sentences (review r56, CONTRACT-4 and CONTRACT-10; ruled 2026-11-19)

- A SECTION heading is `## <name>   [<file>/<section>]`; section tags are unique (L1).
- Every piece heading carries an ISO date (`YYYY-MM-DD`), a `?` piece included; every piece except a `?` piece has
  a statement line (reported under L7).
- L4, `rulings:` items: a `ruled` piece's details entry has AT LEAST ONE item, and EVERY item, on any piece, cites a
  record title that exists. RULED by the predicate manager (the form is his by the owner's delegation): "every",
  because a quote that points at no record entry is the failure the rule exists to catch (a misattributed ruling);
  "at least one" alone would let a second, wrong citation ride on a first, right one.
- A RECORD TITLE is the text of a `## ` or `### ` heading of the record, or of a bold opener `**...**` that starts
  a paragraph AND begins with a date (`**YYYY-MM-DD ...`), JOINED across lines up to its closing `**`; a citation matches the whole title or the part before its
  first ` (`. In a `rulings:` item the cited title is the text from `(record: "` to the last `")` of the item (a
  title may itself contain a `"`; an item may wrap onto continuation lines).
- Slugs are lower-case kebab words. A details file with no entries fails L11 as a base file with no pieces does.
- L6's history words, matched case-insensitively and on word boundaries: `[REV`, `withdrawn`, `reversed`,
  `superseded`, `rev <digits>`, `revision <digits>`, `review r<digits>`, a bare `r<digits>` review id, and any ISO
  date other than the heading's status date. Text inside a fenced block or an inline code span (backticks) is
  exempt, so an example may use a date as its subject.
- L8 is not asked of a `?` piece either (nor, as above, of `parked`, `under-construction` and principle pieces).
- A `by:` target is a piece under `core/principles/`.
- PILOT MODE: a pair whose base file does not exist is SKIPPED with one line; `--require-all` makes it a failure. A
  `needs:` or `by:` into a skipped pair is not a failure without `--require-all`.
- THE READER is `scripts/entry` (the house accessor): the pairs are an entry profile that calls the lint's parser;
  the lint has no reader surface of its own.

### Changes ruled after the pilot (lane preddoc1's FORMAT PROBLEMS; the predicate manager, 2026-11-19; lint not yet changed)

- A status `principle`, legal only under `core/principles/`: the owner STATED it (a principle, a direction, a
  standing instruction), which is not always a slug ruling; its `rulings:` line carries the record's own class.
- A body line `skeleton: yes` on a piece whose statement is verified but whose body is not yet converted: exempt
  from L8, counted by the ratchet beside `?` pieces. It replaces "modes: n/a (skeleton ...)", which claimed the
  wrong thing.
- One piece, one status: a piece whose cells differ in status is SPLIT into sub-pieces (a fourth tag word), one per
  position (`core/holes/zero-values/<position>`).
- The date of a `?` or `skeleton` piece is its conversion date.

## Migration (after revision 29.1)

1. PILOT: the skeleton of all three base files (every section and tag with its status and statement, `?` where not yet
   written) and the section `core/holes` in full with its details; the owner looks at it.
2. The rest, section by section, the rulings made since revision 29's fold going straight into the new shape.
3. A critic round with a COMPLETENESS lens whose control does not share a source with the writer: the census's own
   lists (every ruling entry of the record, every slug, every provided name) each land on a tag; no ruled answer
   changes (the evidence models re-run).
