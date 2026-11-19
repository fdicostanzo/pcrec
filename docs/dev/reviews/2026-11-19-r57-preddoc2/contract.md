# r57 preddoc2 critic: contract

## Findings


### CONTRACT-1 (CONFIRMED; reader; effort S; blast: entry rc only when a document slipped past the lint) — the two arms of route 6a disagree on ambiguity
scripts/entry:475-481. A LIVE tag with two pieces returns `Result(hits)` (rc 0, no note), while a PREVIOUS tag with two
owners returns rc 2 (`EXIT_AMBIG`) with `entry: was X -> A, B`. The header (entry:22) documents "2 ambiguous".
Repro (lens root w/p6 = sample with `[core/holes/name]` -> `[core/holes/class]` in core.md and its details heading):
lint fails L1 (good); `entry core/holes/class -l 0` prints BOTH pieces, `entry: 2 items`, **rc 0** (expected rc 2 + a
"tag names N pieces" note, as the slug arm at entry:491 and the was: arm do). Same root shape for a was: tag retired
under two entries (w/p3: `was: core/holes/word` added to parked/ideas/zip): rc 2, both pieces, `entry: was core/holes/word
-> lib/names/word, parked/ideas/zip` - correct. Fix: `EXIT_AMBIG if len(hits) > 1` on line 477 too.

### CONTRACT-2 (CONFIRMED; reader; effort S) — `entry -g` does not know previous tags at its default level, and the relevance "id" row omits them
scripts/entry:724-731 `fields()["id"]` = id + slugs, no `was` list; level 0/1 text holds no `was:` line. Repro (sample root):
`entry -g core/holes/word -p predicates` -> `entry: 0 items`, rc 1; `-in 1` same; only `-in 2` finds lib/names/word
(ranked by the "body" row, last). Meanwhile `entry core/holes/word` resolves it. A reader who greps for an old tag seen in
the record (whose `tags:` lines are never rewritten) is told it does not exist. Fix: put `it.was` into the "id" field
(it IS an id of the piece, as a slug is). Not specified either way by doc_format.md ("Reader: `scripts/entry <previous
tag>` resolves" names only the KEY form) - spec should say whether -g sees previous tags.

### CONTRACT-3 (CONFIRMED; wrongness + reader; effort M; blast: every `tags:` line of the append-only record) — "a retired tag is never reused" holds only while its `was:` line survives; deleting the line is silent, and the tag can then be reused
Spec: doc_format.md "Changes after the owner read the pilot", MOVE AND RENAME: "appears under one entry only (a retired tag
is never reused)"; "How the lint checks": "a `was:` tag equals no live tag and is retired under one entry". Code:
pred_doc_lint.py:553-573 derives the retired set ONLY from the `was:` lines present now; nothing persists it.
Repro (lens root w/p11b): rename lib/names/word -> lib/names/term, and in its details entry REPLACE
`was: core/holes/word (...)` by `was: lib/names/word (2026-11-06, renamed)` (the first line dropped, as a hand edit of the
moved entry easily does); then add a new core piece `[core/holes/word]` + details entry (+ ratchet core 2). Lint: rc 0,
0 failures. `entry core/holes/word` now prints the NEW piece, rc 0, no `was` line. Expected: L1 failure (retired tag
dropped / reused).
Why it matters now: the record is append-only and is never retagged, so its `tags:` lines become previous tags the
moment a piece moves. The record's ONLY `tags:` line today (COND-FAMILY.md:5260) names `core/conditional/peek` and
`core/conditional/when`, both already retired (library_details.md:56,75) - they resolve (`entry: was core/conditional/peek
-> lib/control/peek`) only through those two lines. Drop one and the record's citation silently points at nothing, or
at a later unrelated piece. Chain with lines KEPT works (w/p11: `entry core/holes/word -> lib/names/term`, held).
Fix (GENERAL FORM, see CONTRACT-G1): a committed only-grows ledger of retired tags (the ratchet file's sibling: one row
`retired<TAB><tag>`, or a section of doc_ratchet.tsv), checked as the `?` row is - a retired tag missing from every
`was:` line, or equal to a live tag, fails L1; `--write-ratchet` appends. Cheaper alternative: lint every record
`tags:` word to resolve (live or `was:`) - that turns the record itself into the ledger (see CONTRACT-5).

### CONTRACT-4 (CONFIRMED; wrongness; effort S) — a base-file `was:` outside a piece, and any base `formerly:`, pass
Spec: "How the lint checks": "A `was:` line in a BASE file fails L6 (history)"; "`was:` and `formerly:` (details only)";
MOVE AND RENAME: "the base heading may NOT carry a `was:` line". Code: pred_doc_lint.py:180 collects `was:` only inside a
PIECE's body (parse_base never looks at the file preamble or a section's lines before its first piece), and
`formerly:` is not collected in a base file at all (only MOVE_RE in parse_details).
Repros (sample root, each lint rc 0, 0 failures; expected 1 L6 failure each):
 (a) w/p13: `was: core/oldholes/x` on the line after `## Holes   [core/holes]` in core.md;
 (b) w/p13b: `was: core/old/x` after the core.md title line;
 (c) w/p14: `formerly: text.pad (2026-11-02, renamed)` in the library piece Padded, whose status date is 2026-11-02
     (the L6 foreign-date check is the only thing that would have caught it, and the status date is exempt).
Fix: in lint(), scan every non-fenced base line for `^(was|formerly):` (as L6 already scans every line), not p["was"].

### CONTRACT-5 (CONFIRMED; sentence with no check; effort S-M) — the record's `tags:` lines are never checked
Spec: "The files": "each new entry gains a line `tags: <tag> <tag>`"; "Cross-references are bare tags". Code: no reader
of `tags:` anywhere in pred_doc_lint.py or entry (grep `tags:`: none). Repro w/p12: append to the sample record
`### 2026-11-08 extra` / `tags: core/holes/nowhere Not_A_Tag` -> lint rc 0. Expected: L5 (names no piece) and L2
(grammar). A `tags:` word should be allowed to be a PREVIOUS tag (the record is never retagged) - so this check is also
the cheapest enforcement of CONTRACT-3: a retired tag the record cites cannot lose its `was:` line. Note the record has
ONE `tags:` line today (COND-FAMILY.md:5260), so the gate costs ~4 lookups; the "a ruling's commit carries record +
base + details" rule (Rules of use) stays process-only, but the `tags:` <-> rulings-citation pairing (every `tags:` tag's
details entry cites that record entry in `rulings:`) is a mechanical consequence the lint could also check (trigger:
the first ruling folded under the new shape).

### CONTRACT-6 (CONFIRMED; wrongness, small; effort S) — a `was:` the parsers do not see is silently dropped by BOTH lint and reader
pred_doc_lint.py:207-216: a details `was:` counts only at column 0 inside an entry. (a) w/p15: `  was: core/holes/word (...)`
(two leading blanks) -> lint rc 0, and `entry core/holes/word` -> "no item", rc 1: the retirement vanished with no
failure. (b) w/p16: `was: core/holes/class (bad` in a details file's preamble (before the first entry) -> lint rc 0
(an ill-formed AND live-colliding line, ignored). Contrast w/p17: a prose line `was: a literal default in the draft` under
`history:` fails L2 - so column-0 `was:` is reserved in every field (good, strict) but the spec never says so, and a
near-miss spelling is not caught. Fix: fail any non-fenced details line matching `^\s*(was|formerly)\s*:` that is not a
well-placed column-0 move line (L2), and add one sentence to the spec: "`was:`/`formerly:` at the start of a line is
reserved in a details entry, in any field".

### CONTRACT-7 (CONFIRMED; reader wrongness; effort S) — an `open <slug>` piece need not list its slug, so `entry <slug>` misses it or lands on ANOTHER piece
Spec: STATUS "`open <slug>` (a question for him ...)"; use 2 "every ruling bearing on a piece is reached ... from the SLUG
he answered under"; L4 "`open` carries a slug". Code: pred_doc_lint.py:436-438 checks only the slug's SHAPE; nothing ties
it to the entry's `slugs:` line (the reader's ONLY slug source, entry:489 / load_pieces `slugs`).
Repros: w/v15 (sample; lib/names/trimmed is `open lib-trim-q`, its details `slugs: lib-trim-q` emptied): lint rc 0;
`entry lib-trim-q` -> "no item", rc 1. w/v16 (same, plus `lib-trim-q` added to parked/ideas/skip's `slugs:`): lint rc 0
(L9 sees one owner); `entry lib-trim-q` -> **parked/ideas/skip**, rc 0 - the open question's slug resolves to the wrong
piece, silently. Fix: L4 (or L9): an `open <slug>` piece's details `slugs:` contains <slug> (then L9's uniqueness covers
the second case). This is the base-heading sibling of the `slugs:` family - see CONTRACT-G2.

### CONTRACT-8 (CONFIRMED; spec vs code, value set; effort S) — `formerly:`'s module part is not the L12 module grammar, and the module/name boundary is undefined
Spec: "`formerly: <module>.<name> (...)` with `<module>` a name or `?`"; L12 "`module: <name>` (a dotted lower-case
name)". Code: FORMERLY_NAME_RE (pred_doc_lint.py:77) = one lower-case word or `?`, then ONE OR MORE `.IDENT` with IDENT
allowing upper case; MODULE_RE (78) is the L12 grammar. Repro w/v5: `formerly: text.Foo.Pad (2026-11-02, renamed)` ->
lint rc 0, though `module: text.Foo` fails L12. The selftest CONTROL even blesses `formerly: ?.pad.inner`. With dotted
modules legal (`module: rx.sub`, a control), `rx.sub.pad` cannot say whether the module was `rx` or `rx.sub`. Which is
right: the spec's intent (the module half must be something `module:` could have said). Fix: split at the LAST dot, check
the left half with MODULE_RE and the right half as one name; say "the name is the last dotted word" in the spec.

### CONTRACT-9 (CONFIRMED; spec sentences the lint does not check, or checks with a different value set; effort S each; each lint rc 0 on the plant)
 (a) principle item form: "How the lint checks" `principle` bullet: "Its item names the record's class: `- <date> (class:
     <the record's word>) ...`". No check. w/v4: `(class: a principle) ` deleted from the sample's principle item -> rc 0.
     Either check it (L4) or say "convention, not checked".
 (b) `modes: n/a (<why>)`: the base template and L8 say a why; code (485) accepts `t.startswith("modes: n/a")`. w/v1 bare
     `modes: n/a` -> rc 0. (Sibling: `was:`/`formerly:` DO require a non-empty why - same field shape, different rule.)
 (c) "the old line `modes: n/a (skeleton ...)` FAILS": code matches the exact prefix `modes: n/a (skeleton` (183).
     w/v2 `modes: n/a (Skeleton, later)` and w/v2b `modes: n/a  (skeleton, later)` -> rc 0 and the piece counts as having
     its example (and is NOT counted by the skeleton ratchet).
 (d) an example line "names the three modes": code accepts the three words on ANY body line, the statement included
     (485 iterates text[1:]). w/v3: example removed, statement rewritten "A hole works in WHOLE, SEARCHED and FIND-ALL
     alike." -> rc 0. The r56 plant "the heading names the modes" covers only the heading.
 (e) the fourth tag word: "a piece whose cells differ in status is SPLIT into sub-pieces (a fourth tag word)". No rule
     ties a 4-word tag to a 3-word parent. w/v8 `[core/holes/nothing/name]` with no `core/holes/nothing` piece -> rc 0.
     The real documents keep the parent live as a hub (core.md:364-400, `needs: core/holes/zero-values` on each sub) -
     the spec should say so and the lint check "a 4-word tag's 3-word parent is a live piece earlier in the file".
 (f) `see:` "A core piece points at a library name with a line `see:`": code allows `see:` on any piece in any file
     (w/v12: `see: parked/ideas/zip` on a library piece -> rc 0). Likely fine (the code's wider reading is harmless) but
     the spec sentence should be the general one.
 (g) `default:` "for a member of the default-imported set ... takes the one value `yes`": two `default: yes` lines, or
     `default: yes` on a `module: ?` piece (a default-imported member of an unnamed module), pass (w/v6). `module:`
     has an exactly-once rule; `default:` none.
 (h) `was:` why "non-empty": `(2026-11-05, ))` passes (why = ")") - cosmetic (w/v13). Dates: a `was:` date in 2099
     passes (w/v14); no rule bounds it (e.g. not after the piece's status date of the move commit) - spec silent, fine.
 (i) "Cross-references are bare tags, never line numbers or § numbers" (Tags section): no check (`§` is not an L6 word).
 (j) statement "ONE sentence, ... present tense": only the 200-character cap is checked (acceptable; say so).

### CONTRACT-10 (CONFIRMED; spec gap; effort S to state, M to build) — a piece retired into SEVERAL pieces has no legal `was:` form
Spec MOVE AND RENAME: "one line per previous tag ... appears under one entry only". A SPLIT that retires the parent (the
"One piece, one status" rule's natural end state if the hub is not kept) would put `was: <parent>` on each sub-piece:
L1 fails ("already retired under", repro shape = w/p3, lint rc 1). Yet the reader already does the right thing for that
shape (w/p3: `entry core/holes/word` -> both owners, `entry: was core/holes/word -> A, B`, rc 2). So the lint forbids the
one case where the reader's ambiguous answer is the CORRECT answer. Today the documents dodge it by keeping the parent live
(zero-values hub). Rule wanted (trigger: the first split that drops its hub, or a merge N->1 which is already legal):
either "a split keeps its parent piece as the hub" (check: CONTRACT-9e), or `was: <parent> (<date>, split)` allowed on
several entries when the why says split, and the reader's rc 2 documented as the split answer. Merges (N previous tags
on one entry) are legal and resolve (one line per previous tag) - held.

### CONTRACT-11 (CONFIRMED; doc; effort S) — stale or missing reader/lint self-descriptions
 (a) scripts/entry header (lines 2-22): no word about the `predicates` profile or the previous-tag key form; line 19
     "Profiles (-p): plan, completed (the archive), decisions, known, upstream (dormant until their unit), scripts" omits
     `predicates`; no example `entry core/holes/class` / `entry <old tag>`; the `entry: was OLD -> NEW` first line and its
     rc 2 on two owners are documented only in a doc_profiles.py comment.
 (b) pred_doc_lint.py:23 "a `rulings:` item is a line starting `-`; its `(record: "<title>")` must be on that line" -
     contradicted by the spec ("an item may wrap onto continuation lines") and by the code (ruling_items joins
     continuations; CONTROL "a rulings item wrapped onto a second line" is clean).
 (c) pred_doc_lint.py:26 "doc_format.md, its last two sub-sections" - three sub-sections carry the post-pilot changes
     and the brief's own rule is "the last three win"; the r56 section ("What the lint checks beyond the rule sentences")
     is the one the docstring at line 5 points to.
 (d) pred_doc_lint.py:7-9 usage omits that `--write-ratchet` CREATES the ratchet file and missing rows from the counts
     (wr4/wr5 in the selftest); the spec says only "`--write-ratchet` lowers both".

### CONTRACT-12 (CONFIRMED; spec vs code: checks with NO sentence in doc_format.md; doc; effort S) — the lint does these, the spec does not say them
(each is a reasonable reading; the r56 section claims to be "What the lint checks beyond the rule sentences", so each
belongs there or in the lint docstring's "Readings" list, which carries only the first four):
 1. an unterminated fence fails L2 (base) / L3 (details) - docstring only;
 2. `slugs: none` and `slugs: -` mean no slug; commas separate list words in `needs:`/`by:`/`see:`/`slugs:`/`shared:`;
 3. the statement may not be a metadata line (`needs|by|see|was|modes|skeleton|module|default:`) - docstring only;
 4. `shared:` must come before the first entry, and a slug listed in ANY details file's `shared:` is shared in all three;
 5. a record title's trailing `.` is dropped and its blanks collapsed (citations likewise); a bold opener counts as a
    paragraph start when the line above is a heading, not only blank (record_titles:249);
 6. a details file with no base file fails L3; an absent record fails L4 for every item;
 7. `--write-ratchet` writes missing rows from the counts and suppresses "no ratchet row" while writing;
 8. a column-0 `was:`/`formerly:` anywhere in a details entry (inside `history:` too) is a move line (CONTRACT-6);
 9. `module:` twice fails even on a `?` piece; `module:`/`default:` on a `?` library piece are allowed;
10. a `see:` to a retired (`was:`) tag fails L5 as "names no piece" (good; say that references must use the live tag);
11. the L8 principle exemption is by TAG prefix `core/principles/` (any status), not by status `principle` - the spec's
    "nor of a principle" does not say which.

### CONTRACT-13 (CONFIRMED; doc; effort S-M; the FULL list asked for) — stale sentences in doc_format.md's upper half that the last three sub-sections (lines 113-159) supersede or contradict
Line numbers are R/subject/docs/dev/pred/doc_format.md.
 1. STATUS (l.5-7): "PROPOSED by the predicate manager 2026-11-19 ..." and "Not built: the pilot (the skeleton and the
    holes section) follows revision 29.1." - contradicted by l.3-4 "PILOTED ... APPLIED 2026-11-19 ... lint L1-L12" in the
    same paragraph.
 2. STATUS (l.9): "the facts it rests on are in the census `$PCREC_TMPDIR/scratch/predcensus/facts.md`" - a temp-root
    (uncommitted, cleanable) path cited as the spec's evidence; not superseded but stale-by-construction.
 3. "The files" heading (l.23): "(read in this order; a file uses only what is before it)" - superseded by `see:` (l.130-132,
    152): "the tag must exist, in ANY file; it is not an ordering claim" (core now points forward at library tags).
 4. "The files" table (l.27-29) is ALREADY on the new paths, so the DIRECTORY bullet (l.126-127) "This supersedes the paths
    in the table above" is itself stale; and the table's core row "the core language: primitives only" vs library row
    "every PROVIDED name: a body in the core language, or \"primitive\"" leaves a primitive provided name's home
    ambiguous (CORE HOLDS PRIMITIVES ONLY, l.129, says core).
 5. Tags (l.40-41): "Tags are never renamed; a moved piece keeps its tag and the lint's path check reads a `was:` line." -
    contradicted by MOVE AND RENAME (l.135: "a tag MAY change"; l.140 "This replaces 'Tags are never renamed' above"),
    by L2's own "(always: a moved piece takes a new tag, below)" (l.76), and by the code: the selftest plant "a moved
    piece's section is not excused by a details was: line" (pred_doc_lint.py:819). Also "a moved piece keeps its tag"
    is the opposite of the rule. Both halves stale.
 6. Base PIECE template (l.44-50): lacks `see: <tag> ...`, `module: <name>|?`, `default: yes` (library), `skeleton: yes`;
    the example line's alternatives lack `skeleton: yes`.
 7. STATUS set (l.52-55): lacks `principle` (l.115, 145); "`?` ... counted by a ratchet that only shrinks" lacks the
    skeleton row (l.117, 149).
 8. Details ENTRY template (l.58-64): lacks `was: <tag> (<date>, <why>)` and `formerly: <module.name> (<date>, <why>)`
    (l.136-137, 154); `rulings:` item shape lacks the principle's `(class: <word>)` (l.146-147).
 9. Lint heading (l.74): "(structure; requested from main, which owns `scripts/`)" - built and run since preddoc1/2.
10. L1 (l.76): "tags unique" - lacks the retired-tag clause now under L1 (l.138, 155-156).
11. L2 (l.76): "tag grammar, and the tag's path equals the piece's file and section" - lacks the `was:`/`formerly:` line
    grammar now under L2 (l.154-155). (Its "(always: ...)" wording is current.)
12. L4 (l.77-78): "a `ruled` piece's details has at least one `rulings:` line" - lacks `principle` (l.145-146) and the
    "EVERY item cites" clause (l.93-96 - already in the r56 section, but L4's own sentence still says only "at least one").
13. L5 (l.78-79): "every `needs:` and `by:` tag exists" - lacks `see:` (l.152).
14. L6 (l.79): "(the word list above; `[REV`)" - lacks "a `was:` line in a BASE file" (l.138, 156).
15. L8 (l.81-82): exemption list "not asked of a `parked` or `under-construction` piece, nor of a principle" - lacks `?`
    (l.106) and `skeleton: yes` (l.117, 148); "a principle" ambiguous (CONTRACT-12.11).
16. L10 (l.83-84): "the `?` ratchet only shrinks" - lacks the per-file skeleton row (l.149-151).
17. L1-L11 list: no L12 (l.157-159; STATUS l.5 says "lint L1-L12").
18. Reader sentence (l.85-86): lists `entry <tag>` and `entry <slug>` only - lacks `entry <previous tag>` (l.139).
19. r56 section, L4 bullet (l.93): "a `ruled` piece's details entry has AT LEAST ONE item" - lacks `principle`.
20. r56 section, L8 bullet (l.106): "L8 is not asked of a `?` piece either (nor ... parked, under-construction and
    principle pieces)" - lacks `skeleton: yes`.
21. r56 section, PILOT MODE (l.108-109): "A `needs:` or `by:` into a skipped pair is not a failure" - lacks `see:` (l.152-153).
22. MOVE AND RENAME (l.138-139): "the base heading may NOT carry a `was:` line any more" - "heading" is narrower than
    the later "A `was:` line in a BASE file fails L6" (l.156); "any more" implies an earlier rule the upper half never
    states (the upper half's only `was:` is l.41's).
23. Migration (l.161-168): "(after revision 29.1)"; step 1 "PILOT ... the owner looks at it" - done (STATUS l.3); step 2
    status unrecorded although STATUS says the change set was "APPLIED".
Recommendation: fold the three sub-sections into the upper half (templates, STATUS set, L1-L12 list, reader sentence)
and delete them, leaving one rule list; the "last three win" convention is what produced 1-23.

## Standing question: siblings and general forms

### CONTRACT-G1 (GENERAL FORM; maintenance; effort M) — one committed MONOTONE LEDGER per document set: the `?` and skeleton ratchets and the retired-tag set are the same mechanism
Siblings today: the `?` row and the `-skeleton` row (counts that only shrink, doc_ratchet.tsv) and the retired tags
(a set that must only GROW, enforced by nothing - CONTRACT-3). Counts are a lossy ledger: w/g1 (sample) turns the full
piece lib/names/trimmed INTO a skeleton (`skeleton: yes` replacing its example) while finishing lib/names/padded (skeleton
line replaced by an example): lint rc 0 - a piece regressed full -> skeleton, hidden by a count-preserving swap; and the
spec's own note "A `?` piece turned into a skeleton piece raises the skeleton row: that is a hand edit" is a forward move
the count form must treat as a raise.
General form: doc_ratchet.tsv (or a sibling) holds PER-TAG rows `<tag><TAB><state>` with an order `?` < skeleton < full,
plus `retired<TAB><tag>` rows; the lint fails any tag that moves backward, any retired tag that is live or lost its `was:`
line; `--write-ratchet` records forward moves and new retirements only after a clean lint. Unlocks: CONTRACT-3 (no
reuse, no lost retirement) for free; `?` -> skeleton becomes a legal forward step (no hand edit); the count rows become a
derived summary; the same ledger can carry retired SLUGS (a slug he answered under is never reused for a new question -
today nothing stops it). Trigger: NOW for the retired half (4 `was:` lines exist, and the record's one `tags:` line already
depends on two of them); the per-tag state half when the first skeleton piece is promoted or demoted.

### CONTRACT-G2 (GENERAL FORM; maintenance; effort M) — the line fields are four ad-hoc families; one declared FIELD TABLE would drive parse and lint
Families today, each with its own regex and placement code: base metadata (META_RE/REF_RE + the `was|skeleton|module|default`
regex, parse_base:177-184), details fields (FIELD_RE), details move lines (MOVE_RE, a separate path that bypasses
FIELD_RE and ends the current field), the `shared:` preamble line, and the record's `tags:` line (no parser at all). The
`was:`/`formerly:` lines are a sibling of `rulings:`/`rejected:` items (all "<what> (<date>, <why>)"-shaped history
records) but share none of their machinery; `modes: n/a (<why>)` has the same "(why)" shape with a DIFFERENT rule
(CONTRACT-9b). The bugs CONTRACT-4 (placement in base outside a piece), -6 (near-miss spellings ignored), -9(b,c,g)
(why required here not there; exact-prefix match; no cardinality for `default:`) are all "a field whose placement /
cardinality / value grammar is coded in one family and not the next".
General form (Frank's first-match-table rule): rows `(field, files: base|details|record, scope: piece|entry|preamble,
cardinality: 0..1|1|*, value grammar, rule id)`; the parser recognises ANY `^\s*<word>\s*:` at line start, looks it up,
and an unknown or misplaced field is a failure of the row's rule. Unlocks: CONTRACT-4/6/9 as table rows instead of
code; the next field (the record's "importing symbols" request - an `import:`-like line - is already in the 2026-11-19
OWNER entry) becomes a row; a `-l 1` working-field view for the reader generated from the same table.
Trigger: the next field added (the import request), or the CONTRACT-4/6 fix, whichever first.

### CONTRACT-G3 (GENERAL FORM; reader + lint; effort M) — reference resolution exists twice (lint `index`, entry `route` 6a/6) with different answers; one resolver with a per-site policy row
Sites that name a piece: base `needs:`/`by:`/`see:` (lint: live only), the record's `tags:` (unchecked; must accept
previous tags since the record is never retagged), `open <slug>` in a heading (unchecked against `slugs:` - CONTRACT-7),
details `slugs:` (L9 uniqueness), `entry KEY` (live, then previous; rc 0 vs 2 inconsistently - CONTRACT-1), `entry -g`
(id row blind to previous tags - CONTRACT-2). Each site decides "live? previous? slug? ordered? ambiguous?" in its own code.
General form: `pred_doc_lint.resolve(word) -> [(piece, how)]` with how in {live, previous, slug}, and a policy table
`(site, accepts, ordering, on-many)`; the lint's L5, the record `tags:` check, the open-slug check and entry's route 6a/6
and -g's id field all call it. Unlocks: CONTRACT-1/2/5/7 at one site each; a rename helper that rewrites every LIVE
reference and leaves the record alone (the move rule's missing tool: today a rename is a hand grep across three files);
a `--dangling` view listing every reference that resolves only through `was:`. Trigger: the CONTRACT-5 build (first new
reference site) or the first rename after the pilot.
Held, not a sibling to unify: `see:` vs `needs:`/`by:` already share one loop and one existence check (L5, 585-604),
differing only by the ordering row - that IS the table form, keep it.

### CONTRACT-14 (CONFIRMED; test coverage; effort S) — the reader's previous-tag arm is tested on its happy path only
scripts/tests/entry_pieces.test:47-53 checks one previous tag (rc 0, first line, level 2) and that a live tag prints no
`was` line. Untested: two owners (rc 2 + both listed; w/p3), a previous tag that is also live (live wins, no `was`
line; w/p4), a malformed `was:` line (the reader still resolves it: entry_was falls back to the first word, while the
lint fails L2 - say so or drop the fallback), and the live-duplicate rc (CONTRACT-1). mut.py's 212 mutants are of
pred_doc_lint.py; a mutant of entry:477-481 (e.g. `EXIT_AMBIG if len(hits) > 1 else 0` -> `0`) is not in its population
(K35 shape: a population nobody counts).

## PROBED-AND-HELD
All roots under contract/w/<name> (copies of R/subject/scripts/tests/pred_doc/root + scripts/), edits by contract/ed.py.
Reader (scripts/entry, 14 probes held):
- prefix, both directions (2): retired `core/holes/word` vs live `core/holes/word/sub` (w/p1), retired
  `core/holes/class/old` vs live `core/holes/class` (w/p2): lint clean, each key resolves exactly (list membership, no
  prefix match).
- retired twice in ONE entry (w/p3b): L1 fails; entry one item rc 0. In two entries / two files (w/p3 + selftest plants):
  L1 fails; a slipped document gives both owners, `entry: was X -> A, B`, rc 2 (correct).
- `was:` = live tag (w/p4): L1 fails; entry returns the live piece with no `was` line (live first) - right precedence.
- `was:` = section tag: impossible by grammar (TAG_RE 3-4 words, section 2); `was:` = slug word: impossible (a slug has
  no `/`) and route 6a runs before route 6 - by construction (2).
- chain kept (w/p11): A -> B -> C with both lines kept, `entry A` and `entry B` reach C (2).
- fenced `was:` (selftest control): not a move, held.
- `-l 0/1/2` (3) and odd `-l 5`/`-l -1` with a previous tag: the `entry: was` line precedes the items at every level.
- exit codes: 0 found, 1 none (w/p15 "no item" rc 1), 2 two owners - as the header says (except CONTRACT-1).
- route ORDER (5 rows): routes 1/2/3/5 regexes cannot fullmatch a slash tag; route 4 (plan [TAG]) is guarded by PL18
  (doc_profiles KEY_SHAPES includes PIECE_TAG_SHAPE); route 6b is an exact scripts path and scripts/ has no
  core|lib|parked dir. A previous tag neither shadows nor is shadowed.
- NOT findings, noted: `entry [core/holes/class]` (brackets, as written in a heading) -> no item rc 1 (route 4 strips
  brackets only for plan tags); `--state` is silently ignored on a KEY lookup (pre-existing entry behaviour).
Lint (8 held): a `see:`/`needs:` naming a retired tag fails L5 (2; w/c10, w/c11); a `was:` prose line under `history:`
fails L2 (w/p17, strict); live tag + `was:` collision and double retirement fail L1 (3, above); `skeleton`/`?` ratchet rows
share one key table and one loop (held as the right sibling form).
Gates re-run from contract/s: selftest 154 runs, 12/12 rules, 0 failures; pred_doc_lint.py.test PASS; entry_pieces.test
PASS (0 failures); mut.py total 212, killed 196, equivalent 16, SURVIVED 0; the real documents 2168 passed, 0 failed.
Counts: 34 planted roots (16 reader, 18 lint), 17 findings filed (CONTRACT-1..14, G1..G3), 22 probes held.

CRITIC COMPLETE
