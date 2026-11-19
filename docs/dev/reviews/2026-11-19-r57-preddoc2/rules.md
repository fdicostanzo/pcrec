# r57 preddoc2 critic: rules

## Findings


### RULES-1 CONFIRMED - a `was:`/`formerly:` line ends the open details field, so every `rulings:` item or slug after it goes unchecked (regression vs BASE)
- severity: wrongness (the lint passes a forbidden document; L4 "EVERY item cites a record title that exists" and L9 uniqueness both escape). Also part (b): BASE rejects these documents, SUBJECT accepts them.
- where: scripts/pred_doc_lint.py:212-216 (parse_details: `mv = MOVE_RE.match(ln)` ... `field = None; continue`). In BASE a `was:` line was a continuation line of the open field, so the next `- item` stayed in `rulings:`; now it falls into no field and is silently dropped.
- repro (sample root, library_details.md, entry lib/names/padded):
      rulings:
      - 2026-11-02 "pad it" (record: "2026-11-02 bold words")
      formerly: text.pad (2026-11-02, renamed)          <- or a `was:` line
      - 2026-11-09 "never said" (record: "2026-11-09 NO SUCH ENTRY")
  `python3 -I scripts/pred_doc_lint.py --root <root> --require-all`: SUBJECT rc 0 (clean); BASE (same plant, old layout) rc 1
  `L4 ...library_details.md:8: record title "2026-11-09 NO SUCH ENTRY" not found`. Same with a `was:` line (F1b), and a
  ruled piece's second, misattributed citation below a `was:` (F3). Slugs: `slugs: hole-class shared-q` / `was: ...` /
  `  regex-q` (a continuation slug duplicating core/principles/regex-default's) passes SUBJECT; BASE fails that entry.
- why it matters: the spec places `was:` lines anywhere in the entry (it gives no position); the misattributed-ruling
  failure L4's "every" exists to catch (doc_format.md "What the lint checks beyond...", L4 bullet) is exactly what
  hides here. The real documents put `was:` first in the entry, so they are not affected today.
- fix (small): either keep `field` unchanged across a move line (a move line is not field text but does not close the
  field), or fail L3/L2 on any `- ` line that belongs to no field. Add both plants to the selftest.
- blast radius: every details entry carrying a `was:`/`formerly:` line after its first field.

### RULES-2 CONFIRMED - a `principle` piece's rulings item need not name the record's class
- severity: wrongness (spec-vs-lint). Spec doc_format.md "Changes ruled after the pilot", bullet 1: "its `rulings:` line
  carries the record's own class"; "How the lint checks the changes above", bullet 1: "Its item names the record's
  class: `- <date> (class: <the record's word>) "<his words>" (record: "<title>")`". Code: scripts/pred_doc_lint.py:527-533
  checks only that a `principle` piece has >= 1 rulings item; nothing looks for `(class:`. The docstring (line 30) and
  the selftest plants ("principle piece with no rulings item") only cover presence.
- repro: sample root core_details.md, entry core/principles/stated: replace
  `- 2026-11-01 (class: a principle) "stated" (record: ...)` by `- 2026-11-01 "stated" (record: ...)`. Lint rc 0.
- which side is right: the spec (the class is the whole point of `principle` over `ruled`: "the owner STATED it ...
  which is not always a slug ruling"). Fix: on a `principle` piece, at least one (or every) rulings item matches
  `^- \d{4}-\d{2}-\d{2} \(class: [^)]+\)`; one plant. Whether "every" or "at least one" is the manager's form call.
- blast radius: core/principles only; the real file's items do carry `(class: ...)` today.

### RULES-3 CONFIRMED - `formerly:` in a BASE file passes (it is details-only history), and `was:` in a base file escapes L6 when not spelled exactly `was:` at column 0 of a piece body
- severity: wrongness (low-to-medium). Spec "How the lint checks...", bullet 4: "`was:` and `formerly:` (details only)";
  "A `was:` line in a BASE file fails L6 (history)". Code: parse_base (scripts/pred_doc_lint.py:180) collects only
  `^(was|skeleton|module|default):` inside a piece body; `formerly:` is never looked for in a base file, and a `was:`
  line in a section preamble (between `## Section [x/y]` and the first `###`), indented, or spelled `Was:` is not seen.
- repros (sample root, each rc 0):
  (a) library.md, piece lib/names/padded (status date 2026-11-02): add `formerly: text.pad (2026-11-02, renamed)` -
      the date equals the status date, so L6's foreign-date clause does not catch it either.
  (b) core.md after `### Name [core/holes/name] ? 2026-11-03`: `Was: core/holes/old (2026-11-03, moved)`.
  (c) same place: `  was: core/holes/old (2026-11-03, moved)` (two-space indent).
  (d) core.md right after `## Holes   [core/holes]`: `was: core/other` (no date, so L6's date clause is silent).
- fix: in a base file, fail L6 on any non-fenced line matching `^\s*(was|formerly):` case-insensitively, wherever it
  sits (pieces and preambles alike). Plants for (a) and (d).

### RULES-4 CONFIRMED - L12 "`module:` and `default:` appear only in the library file" is checked on base PIECE BODIES only: in any details file, and in a base file's section preamble, they pass with any value
- severity: wrongness (low). Spec "How the lint checks...", last bullet. Code: L12 reads p["module"]/p["default"], which
  parse_base fills only from piece bodies (pred_doc_lint.py:180, 446-462); parse_details never looks at them.
- repros (sample root, each rc 0): core_details.md after `- 2026-11-01 first written.` add `module: Bad Name` and
  `default: no` (M1b); library_details.md under `## lib/names/trimmed — Trimmed` the same two lines (M2: grammar and value
  both wrong, still clean); parked_details.md `module: x` (M10); core.md right under `## Holes   [core/holes]`:
  `module: Junk` / `default: nope` (M5). (When the plant lands inside a `slugs:` field it fails L9 by accident, not L12.)
- which side: the spec; "the library file" is library.md. Fix: fail L12 on `^(module|default):` in any details file and
  outside a library piece body; one plant each side.

### RULES-5 CONFIRMED - field lines outside a piece body are invisible to every new rule (section preambles; details header before the first entry)
- severity: wrongness (low). The new fields are parsed only between a `###` heading and the next heading (base) or
  after a `## <tag> —` heading (details); a line elsewhere is not text the reader shows under any piece, but it is also
  not refused, so a misplaced field silently does nothing.
- repros (sample root, each rc 0): core.md under `## Holes   [core/holes]`: `see: lib/names/nowhere` (V2),
  `skeleton: maybe` (S10); core_details.md after `shared: shared-q`, before the first entry:
  `was: core/holes/class (2026-11-01, x)` - a was: naming a LIVE tag, which L1 refuses inside an entry (W5).
- fix: fail (L2 base / L3 details) on any non-fenced `^(needs|by|see|was|formerly|skeleton|module|default):` line that
  belongs to no piece/entry. Same gap exists for `needs:`/`by:` at BASE (not a regression).

### RULES-6 CONFIRMED - near-miss spellings of the new fields are silently body text (no rule sees them)
- severity: wrongness (low; each is a typo the lint was in a position to catch). The field regexes are exact,
  case-sensitive, column-0 (pred_doc_lint.py:71-74, 180, 183, 212).
- repros (sample root, each rc 0):
  - old skeleton marker variants: `modes: n/a (Skeleton: body later)` (S6) and `modes: n/a  (skeleton ...)` (S7) pass
    L8 as a normal `modes: n/a`; spec "How the lint checks", bullet 2: "the old line `modes: n/a (skeleton ...)` FAILS".
    Fix: match `modes:\s*n/a\s*\(\s*skeleton` case-insensitively.
  - `See: lib/names/nowhere` in a piece body (V4): a dangling cross-reference, not checked.
  - `Was: Core/Junk` in a details entry (W15), `  was: core/holes/class (...)` indented inside a rulings field (W16):
    neither a retirement (the reader will not resolve it) nor a failure.
  - duplicates: `default: yes` twice (M3), `skeleton: yes` twice (S3) pass; `  module: other` indented under
    `module: text` (M7) passes "exactly one module". Spec says "one value", "exactly one" for module only; duplicates
    of default/skeleton are a nit.
- fix: one case-insensitive, leading-blank-tolerant field regex for "looks like a field" that FAILS when it is not
  exactly a known field spelled correctly.

## PROBED-AND-HELD

Method: (a) 60 planted documents over a copy of the SUBJECT sample root (driver rules/probe.py, cases rules/c1-c4.txt),
each run with `pred_doc_lint.py --root <copy> --require-all`; (b) rules/cmp.py: every BASE selftest PLANT and CONTROL
(118) plus 10 hand plants (128 cases) applied to the BASE sample, linted by the BASE lint, then the same files moved to
the new layout and linted by the SUBJECT lint (L12 failures and the new `<word>-skeleton` missing-row messages filtered,
since the BASE sample has neither); per-rule failure counts compared.

(a) held, by rule:
- principle (3 + RULES-2): `principle` outside core/principles fails L4 (core and, in the selftest, lib); `Principle`
  (case) fails L4 as an unknown status; a principle piece with no rulings item fails L4.
- skeleton (8 held): `skeleton: yes` on a `?` piece fails; `skeleton: yes (later)` fails; `Skeleton: yes` and a fenced
  `skeleton: yes` give no exemption (L8 fails, the safe side); the old marker inside a fence is exempt (correct, fences
  are text); a new skeleton piece in core / a lib skeleton moved to parked raise that file's `-skeleton` count and fail
  L10 against a 0 row (counted in the right file).
- ratchet (5 held): all three `-skeleton` rows missing -> three L10 failures; `lib-skeleton <SP><TAB>1`, `+1`, an
  unknown key, a duplicated row, three fields, a space-separated row all fail. `lib-skeleton<TAB>١` (Arabic-Indic digit)
  is accepted as 1 by str.isdigit/int: a nit, not filed.
- see: (5 held): a section tag, a retired (`was:`) tag, a second `see:` line naming the piece itself, a nonexistent tag
  all fail L5; a `see:` in a details file happens to fail L9 when it lands in `slugs:` (incidental).
- was:/formerly: (11 held): a SECTION tag (2 words), a 5-word tag, trailing text after `)`, the same tag twice in one
  entry, a tag equal to a live FOURTH-word tag, a tag equal to a live tag of another file (parked entry retiring
  lib/names/padded), and the selftest's across-files case all fail. A was:-tag equal to a live SECTION tag is
  impossible (the was: grammar wants 3-4 words, a section tag has 2). Accepted as legal by my reading of the spec:
  why `-` (non-empty), `formerly: text.Pad` (the spec does not say the name is lower-case), `formerly: rx.sub.pad`
  (dotted module, consistent with L12's dotted module), a fenced `was:` in a base file (L6 exempts fences).
- L12 (4 held): module missing, two module lines, `Text`, `te xt`, default: no, module/default in core/parked base
  pieces (selftest), `module: ?` on a non-`?` piece (legal), trailing blanks after `module: text` (stripped; legal).
- not lintable and not claimed by the spec's lint section: "one piece, one status" (cells) beyond the single heading
  status (`ruled reading` fails L4), and "the date of a `?`/skeleton piece is its conversion date".

(b) 128 cases: 124 fail the SUBJECT at least as often per rule as the BASE. The 4 that check LESS: three are RULES-1
(a rulings item after `was:`, after `formerly:`, a slug continuation after `was:`); the fourth (`skeleton: yes` lifting
L8 from a piece with no example) is the deliberate relaxation, gated by the `-skeleton` ratchet row (S9 confirms a new
skeleton piece fails L10 against the committed 0). Removal of BASE's explicit "tag not in file" L2 clause lost nothing:
the section tag carries the file word, and a piece before any section, a lib tag in core with or without a base `was:`,
still fail L2 (the base `was:` now additionally fails L6). The `needs:` line in a section preamble passes in BASE and
SUBJECT alike (RULES-5, not a regression). Ratchet-row parity verified after excluding a filter artefact of mine.

Counts: 60 (a) plants, 128 (b) cases; 6 findings (RULES-1..6), RULES-1 is the one regression.

CRITIC COMPLETE
