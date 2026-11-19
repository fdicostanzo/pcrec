# The predicate documents: base + details, linked by tags (the format)

STATUS: PILOTED and IN USE (lint L1-L12 built, scripts/pred_doc_lint.py; the reader is a profile of scripts/entry);
last amended 2026-11-19 by lane predlint3 (review r57). Modelled on the tracker pair ([DOC-INDEX], D192,
`docs/dev/doc_format.md`). Where this file and the lint disagree the lint's selftest plants and this text were written
together: a disagreement is a bug in one of them, reported. How the format came about: "History of this format", at the end.

## What the files are for (the uses that shape them)

1. WAKE: a session reads the BASE files whole and knows the current language, the library and what is parked.
2. BEFORE ASKING the owner anything: every ruling bearing on a piece is reached from the piece, and from the SLUG he
   answered under.
3. WHEN HE SPEAKS: his words go into the record once, whole, the same hour; the pieces they touch are updated in the
   same commit.
4. WHEN FORMING A LEANING: what was REJECTED and why, and the PRECEDENTS (pieces decided by the same principle), are
   found by tag, without reading the record.

## The files

Three base/details pairs in `docs/design/predicates/`, listed in the READ ORDER (`needs:` points only backward in it, so
the core reads whole without the library; `see:` is not an ordering claim):

| base (current definition) | details (history, reasoning) | holds |
|---|---|---|
| `core.md` | `core_details.md` | section `principles` first (his method), then the core language: primitives only, every provided name that is primitive |
| `library.md` | `library_details.md` | every PROVIDED name whose definition is a BODY written in the core language |
| `parked.md` | `parked_details.md` | ideas and directions not in the language, each with a trigger |

CORE HOLDS PRIMITIVES ONLY: a piece whose definition is a body in the core language is a LIBRARY piece ("there is nothing
particular about peek() other than its a useful transform"). A core piece points at a library name with `see:`.

Not converted, on purpose (the tracker design's own rule: an append-only raw log keeps its shape):
`docs/design/plan_row_bodies/COND-FAMILY.md` stays THE RECORD, one chronological log, the only source of rulings; each
entry gains a line `tags: <tag> <tag>` (blanks or commas between). Evidence directories and filed reviews stay where they
are. The old draft `predicates_draft.md` is FROZEN at its last revision; the details files were cut from it.

## Tags

- A TAG is a path of lower-case kebab words: `<file>/<section>/<piece>[/<sub>]`, file one of `core`, `lib`, `parked`
  (`core/holes/class`, `core/principles/regex-default`, `lib/modifiers/padded`); three or four words, so every piece
  sits in a section. A SECTION tag has two words (`core/holes`). Cross-references are bare tags, never line numbers or §
  numbers (not checked).
- The tag's path always equals the piece's file and section. A moved or renamed piece takes a NEW tag (below).
- A fourth word SPLITS a piece whose cells differ in status into sub-pieces, one per position
  (`core/holes/zero-values/<position>`). The parent (the three-word tag) stays as the hub: it is a live piece EARLIER in
  the same file. A split that dropped its hub would have no legal `was:` form.
- MOVE AND RENAME: a tag MAY change. The details entry of the new tag carries one line per previous tag,
  `was: <previous tag> (<YYYY-MM-DD>, <why>)`; a function whose name or module changed carries
  `formerly: <module>.<name> (<YYYY-MM-DD>, <why>)` (`<module>` is a module name as in `module:` below or `?`; `<name>`
  is the LAST dotted word, an identifier). A previous tag is retired for good: it equals no live tag and is named by one
  entry only (a merge puts several `was:` lines on one entry). A reference (`needs:`, `by:`, `see:`) names the LIVE tag,
  never a retired one.

## Pieces and status

- A base PIECE:

      ### <name>   [<tag>]   <status> <date>
      <statement: ONE sentence, at most 200 characters, present tense, the current rule>
      needs: <tag> ...            (what must be read first; all earlier in the read order)
      by: core/principles/<p> ... (the principle(s) it was decided by; optional)
      see: <tag> ...              (a pointer, a core piece to a library name; any file, forward allowed; optional)
      module: <name> | ?          (library file only; exactly once on every library piece that is not `?`)
      default: yes                (library file only, at most once: a member of the default-imported set)
      skeleton: yes               (at most once: the statement is verified, the body is not yet converted)
      <the definition: rule sentences, a table where the piece is one; no history>
      <one example naming WHOLE, SEARCHED and FIND-ALL, or "modes: n/a (<why>)">

  The field lines are exactly these spellings, in lower case at the start of a line, inside a piece body. `needs:`,
  `by:`, `see:` take blank- or comma-separated tags. SCANNING the base = the heading and statement lines only; READING it
  whole = everything. The date is the status date; a `?` or `skeleton` piece's date is its conversion date.
- STATUS (one per piece): `ruled` (the owner ruled it) | `principle` (the owner STATED it: a principle, a direction, a
  standing instruction, which is not always a slug ruling; legal only under `core/principles/`) | `reading` (the draft's
  or the manager's, not ruled) | `open <slug>` (a question for him: the body is the current definition labelled as a
  reading, or a summary of the standing discussion, and the candidates) | `under-construction` (a direction
  acknowledged, not defined) | `parked` (parked file only) | `?` (converted, statement not yet written; counted by a
  ratchet that only shrinks, as `skeleton: yes` pieces are, in a second row).
- A details ENTRY, one per tag, in the same order as the base:

      ## <tag> — <name>
      was: <previous tag> (<YYYY-MM-DD>, <why>)           (one per previous tag; optional)
      formerly: <module>.<name> (<YYYY-MM-DD>, <why>)     (optional)
      slugs: <every question slug asked about this piece>
      rulings:   - <date> "<his words, verbatim>" (record: "<entry title>")
                 - <date> (class: <the record's word>) "<his words>" (record: "<title>")      (a principle)
      rejected:  - <the candidate> — by <owner ruling | run | review rN> — <the reason, with its witness>
      readings:  - <a manager's or draft's reading> — SUPPORTED | NOT SUPPORTED | UNTESTED (<evidence pointer>)
      evidence:  <lane evidence dirs and PART names>
      history:   <dated blocks: what the piece used to say, review items, discussion>

  A `was:` or `formerly:` line in column 0 is a move line wherever it sits in the entry (even under `history:`); a move
  line does not close the field above it. No other field-looking line (the base fields above) belongs in a details file.
  A `shared: <slug> ...` line may head a details file before its first entry.

## Rules of use

- A new ruling = the record entry (with its `tags:`), the base piece and the details entry in ONE commit; a ruling
  that changes an EARLIER piece rewrites that piece's status and statement in the same commit.
- The base never carries history: no revision marks, review ids, "withdrawn", "reversed", `was:`/`formerly:` lines, dates
  other than the status date. Everything of that kind is in the details entry.
- A principle piece quotes the owner; a name the manager gave it ("stated behaviour") is marked as the manager's.

## The lint (scripts/pred_doc_lint.py)

`python3 -I scripts/pred_doc_lint.py [--root DIR] [--require-all]`; `--write-ratchet` lowers the ratchet (only after a
clean lint, creating the file and missing rows from the counts); `--selftest` runs the planted-fault selftest (one or
more plants per clause, each failing exactly its own rule) and its controls. Exit 0 clean, 1 failures, 2 usage. Each
failure is `Ln file:line: message`. A FENCED block (``` or ~~~, closed only by the same mark) is exempt from every
line scan; an unterminated fence fails (L2 in a base file, L3 in a details file).

- L1 UNIQUENESS. Piece tags and section tags are unique. A `was:` tag equals no live tag and is retired under one entry
  only, across all three files.
- L2 FORM. A section heading is `## <name>   [<file>/<section>]`. A piece heading is `### <name>   [<tag>]   <status>
  <date>` with a real ISO date, a `?` piece included. The tag has the grammar and its path equals the piece's file and
  section. A four-word tag has its parent piece earlier in the same file. A `was:` line is `was: <tag> (<date>, <why>)`
  and a `formerly:` line is `formerly: <module>.<name> (<date>, <why>)`, the date real, the why non-empty. A
  field-looking line (the base fields, `was`, `formerly`; any case, any indent, blanks before the colon) in a base file
  must be spelled exactly and lie inside a piece body; in a details file `was:`/`formerly:` must be spelled exactly
  and lie inside an entry.
- L3 BIJECTION. Base pieces and details entries are in bijection, in the same order; an entry heading is
  `## <tag> — <name>`; no duplicate entry; a details file with no base file fails; a base file with no details file
  fails. A base-file field (`needs:`, `by:`, `see:`, `skeleton:`) in a details file fails.
- L4 STATUS AND RULINGS. The status is in the set; `open` carries one kebab slug; `principle` only under
  `core/principles/`; `parked` only in the parked file; every piece has a date. A `ruled` or `principle` piece's
  details entry has AT LEAST ONE `rulings:` item, and a `principle` piece at least one item naming
  `(class: <word>)`. EVERY item, on any piece, cites a record title that exists (a quote that points at no record
  entry is the failure this rule exists to catch). A RECORD TITLE is the text of a `## ` or `### ` heading of the
  record, or of a bold opener `**YYYY-MM-DD ...**` that starts a paragraph (the line above is blank or a heading) and
  begins with a date, joined across lines up to its closing `**`; a trailing `.` is dropped and blanks collapse; a
  citation matches the whole title or the part before its first ` (`. In an item the cited title is the text from
  `(record: "` to the last `")` of the item (a title may contain a `"`; an item may wrap onto continuation lines). An
  absent record fails L4 for every item.
- L5 REFERENCES. Every `needs:` and `by:` tag names a piece; a `needs:` target is earlier in the read order (core
  before lib before parked, and earlier in its file). `by:` names a piece under `core/principles/`. `see:` names a
  piece in ANY file, never the piece itself. Every tag on a record line that begins exactly `tags:` (outside a fence)
  is a live piece, a section, or a previous tag. PILOT MODE: a pair whose base file does not exist is SKIPPED with
  one line; `--require-all` makes that a failure; a reference into a skipped pair is no failure without it.
- L6 NO HISTORY IN A BASE FILE. Case-insensitively and on word boundaries: `[REV`, `withdrawn`, `reversed`,
  `superseded`, `rev <digits>`, `revision <digits>`, `review r<digits>`, a bare `r<digits>`, any ISO date other than
  the heading's status date, and a `was:` or `formerly:` line anywhere. Text inside a fenced block or an inline code
  span is exempt.
- L7 CAPS. Statement at most 200 characters and piece at most 40 lines (from heading to last non-blank line): HARD. The
  base file SOFT (core 64 KB, library 24 KB, parked 16 KB): reported, never refused. The statement is the first
  non-blank line after the heading; it is not a field line and not fenced; every piece except a `?` piece has one.
  ("One sentence, present tense" is not checked.)
- L8 EXAMPLE. A body line after the heading names WHOLE, SEARCHED and FIND-ALL, or starts `modes: n/a`. Not asked of a
  `?`, `parked` or `under-construction` piece, of a piece whose tag is under `core/principles/`, nor of a `skeleton:
  yes` piece. `skeleton:` takes the one value `yes`, once, never on a `?` piece. The old line `modes: n/a (skeleton
  ...)` (any case or blanks) fails.
- L9 SLUGS. A slug in a `slugs:` line is lower-case kebab; `none` and `-` mean no slug; list words are blank- or
  comma-separated. A slug is unique to one tag or listed on a `shared:` line at the head of ANY details file.
- L10 RATCHET (`docs/dev/pred/doc_ratchet.tsv`, one `<word><TAB><count>` per line, a row per present file for its `?`
  pieces and a row `<word>-skeleton` for its skeleton pieces): every line well-formed, no duplicate row, a row for
  every present file, a count never above its row. The ratchet only shrinks; a `?` piece that becomes a skeleton piece
  raises the skeleton row by a hand edit, visible in the diff.
- L11 NON-VACUITY. A base file with no pieces and a details file with no entries fail; no pair at all fails; a file
  that is not UTF-8 fails (a BOM and CRLF line ends are accepted).
- L12 LIBRARY FIELDS. Every library piece that is not `?` has exactly one `module:` line (`module: <name>` or
  `module: ?`; a name is lower-case words joined by dots, `[a-z][a-z0-9_]*`); a `?` piece may have it, once.
  `module:` and `default:` appear only on a library piece, never in a details file; `default:` at most once, its one
  value `yes`.

NOT CHECKED, said plainly: one sentence and present tense; that an example line is an example (the three words anywhere
on a body line pass, the statement included); a bare `modes: n/a` without its `(<why>)`; `§` or line numbers in a
reference; a date's range; that a retired tag is not REUSED by a new piece once its `was:` line is deleted (the record's
`tags:` check catches a tag the record cites).

THE READER is `scripts/entry`: the pairs are its profile `predicates` (it calls the lint's parser, so there is one
parser): `entry core/holes/class` (level 0 the heading and statement, 1 the piece, 2 the details entry), `entry <slug>`
(the piece named by a `slugs:` word), `entry <previous tag>` (resolves to the current piece and says `entry: was OLD ->
NEW` first; two owners give exit 2); `entry -g REGEX -p predicates` also matches previous tags; `--state open` lists
the open pieces.

## Migration

1. PILOT (done): the skeleton of all three base files and the section `core/holes` in full.
2. The rest, section by section, the rulings made since going straight into the new shape.
3. A critic round with a COMPLETENESS lens whose control does not share a source with the writer: the census's own
   lists (every ruling entry of the record, every slug, every provided name) each land on a tag; no ruled answer
   changes (the evidence models re-run).

## History of this format

- 2026-11-19, the owner asked for the predicate documentation to be organized and delegated the form (COND-FAMILY,
  "housekeeping: organize the predicate documentation" and its two addenda). Proposed by the predicate manager; the
  facts it rests on were a census of the record (155 ruling entries, about 100 question slugs, 72 candidate provided
  names, 17 recurring principles, 36 parked items).
- PILOT (lane preddoc1, 2026-11-19; 1,828 checks): the skeleton, `core/principles` and `core/holes` in full. Its FORMAT
  PROBLEMS, ruled by the manager: the `principle` status, `skeleton: yes`, one status per piece (the split), the
  conversion date of a `?` or skeleton piece.
- Review r56 (lane predlint2): the lint's readings made the spec ("What the lint checks beyond the rule sentences"): every
  rulings item cites a record title, the record title form, L6's word list, the fenced blocks, pilot mode, the reader.
- The owner after reading the pilot (COND-FAMILY "2026-11-19 OWNER, after reading the pilot documents", lane preddoc2): the
  directory `docs/design/predicates/`, core holds primitives only (the library, `see:`), `module:` and `default:`,
  move and rename (`was:`, `formerly:`, the previous-tag reader key).
- Review r57 (lane predlint3, 2026-11-19; the manager's rulings): field-looking lines (misplaced, misspelled, doubled), a
  move line does not close a field, `was:`/`formerly:` anywhere in a base file, `module:`/`default:` never in a details file,
  a principle's class item, the `formerly:` module grammar, a fourth tag word's hub parent, the record's `tags:` check
  (L5), `entry -g` and the ambiguity exit of the live-tag arm; this fold of the three post-pilot sub-sections into the
  rules above, so each rule is said once.
