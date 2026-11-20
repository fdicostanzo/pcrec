# CRITIC RECOUNT: r60 preddoc5

## Findings


### RECOUNT-1  CONFIRMED   severity: doc   effort: S
where: list (a) row record 1329 "2026-11-16 RULING — a compare over looped labels warns" and row 1493 "2026-11-16 OWNER RULING — joint-loops: agreed, all three parts" parts (2)-(3); core_details core/conditions/pass-start-read (history + rejected), core/labels/labels-vs-captures (rejected), core/diagnostics/warnings
what: of r59's 144 ruling entries, ONE still lands nowhere by the test (cited, or a CITED later entry supersedes it): 1329 looped-compare ("looped-compare: warn"). Its only supersessor is 1493 joint-loops (3) (the warning MOVED onto a hand `|` of conditions), and 1493 is itself cited by no `rulings:` item. 1493 is held only through after-loop-read (cited), and only for its part (1) (bare joints read the last pass's own tuple; after-loop-read's "MINE: joint-last-pass dissolves"); after-loop-read says nothing of part (2) (sibling loops a compile error) or part (3) (the moved warning). The documents' account of the end of the warning is "withdrawn by the manager (the draft §R.2, with `compare.looped`)" (core_details pass-start-read rejected) — a MANAGER withdrawal of an OWNER-RULED warning; the record's only words on it are the manager's "`compare.looped` and the manager's withdrawn looped-warning go to the next review as told" (record 2830-2831, inside "2026-11-17 OWNER RULING — warnings: the list accepted ..."), which sends it to review, it does not retire it. `compare.looped` appears nowhere in core.md (grep), so a ruled warning has no live statement, no rulings item, and no owner supersessor.
evidence: `timeout 60 python3 -I recount/a_rulings.py S` -> "expected 144 cited directly 135 held by cited supersessor 8 STILL MISSING 1" + "MISSING 1329 ... supersessor '2026-11-16 OWNER RULING — joint-loops' UNCITED"; record 1495-1500 (joint-loops (1)-(3)), 2454-2475 (after-loop-read: no word on sibling loops or the warning); `grep -n compare.looped core.md` = 0 hits; draft 1353 ("Pass forms whose labels sit in SIBLING loops stay UNSPECIFIED, NOT RUN") — part (2) is also unstated in the documents.
proposed fix: cite 1329 and 1493 as `rulings:` items on core/diagnostics/warnings (or pass-start-read) and state the warning's status there: either it stands (a row in the warnings table) or it is an open question to the owner (the manager's withdrawal is not a ruling); state part (2) (sibling loops) as the one-rule reading with its source, or as open.

### RECOUNT-2  CONFIRMED   severity: doc   effort: S
where: list (c) row 43 `where`; library.md lib/structural/each (heading "each, each_group, where_group"); library_details lib/structural/each history line 751; draft §5.3 (line 5706 "`where(p, X)` = SELECT entries by a compile-time STRUCTURAL property (the selecting twin of `each` ...)") and the draft's name table (line 7727 "`where`, `where_group`, `each_group` | none | LEAN (§3.2, §5.3); candidate cut")
what: `where(p, X)`, a provided structural macro of the draft (the selecting twin of `each`), lands nowhere: no library piece names it (heading or body), no `rejected:` or reading gives a reason; its only mention in the six documents is the history line "a new piece (census rows `each`, `each_group`, `where`)", which claims a piece the piece does not carry. r59 graded it F on that same history line; under COMMON's rule (every call-form name a LIBRARY piece with `defined:`) it is the one call-form name of the 98 with neither a piece nor a stated reason.
evidence: `timeout 60 python3 -I recount/c_names.py` row 43 -> ELSE {'library_details.md': 1}; `grep -nP '(?<![\w._])where\(|`where`' docs/design/predicates/*.md` -> library_details.md:751 only.
proposed fix: add `where` to lib/structural/each (heading + one body line: "`where(p, X)` selects the entries of a spelled array by a structural property", `defined: native` as its siblings), or a `rejected:`/reading line stating why it is not provided (the draft's "candidate cut").

### RECOUNT-3  CONFIRMED   severity: doc   effort: S
where: list (c) rows 55 `@warn` (`@warn.off(...)`, `@warn.error(...)`), 56 `@export(...)`, 57 `@options.strict(...)`; core.md core/operators/statements (line 1042-1044), core/modules/export, core/diagnostics/warnings
what: the three compile-time effects are written as calls (`@export(names)`, `@warn.off(/.../)`, `@options.strict(...)`) and are homed only in CORE pieces, with no library piece and no `defined:` line; yet core/operators/statements says of exactly these: "the effects `@warn`, `@export`, `@options` and the assertions of the `assert` module ... Every provided name written as a call has its piece in the library (`library.md`), these included." The assert effects got library pieces (lib/assert/assert, lib/assert/each); these three did not. Either the sentence is false or three library pieces are missing (COMMON's rule: every call-form `x(...)`/`m.x(...)` is a LIBRARY piece; the core holds no call-form name).
evidence: `c_names.py` rows 55-57 -> no library piece; core.md 1043-1044 quoted; core.md 1132 "A library file exports with `@export(names)`" is the statement line of core/modules/export (a core piece); `grep -c '@warn\|@export\|@options' library.md` = 1 (lib/builtin/import body, "as `@export`'s is").
proposed fix: library pieces lib/builtin/export, lib/builtin/warn (`.off`, `.error`), lib/builtin/options (`defined: native (a compile-time effect on the compiler)`), core/modules/export and core/diagnostics/warnings keeping the meaning with `see:`; or, if an `@` effect is ruled not a "call-form name", say so in doc_format.md and correct the core.md sentence.

### RECOUNT-4  CONFIRMED   severity: doc   effort: S
where: core_details core/filters/complement (`slugs: nested-complement source-row searched-complement`; the `rulings:` item "Source-row: yes"); core/model/match; record 1949-1967 (source-row) and 2036-2050 "2026-11-16 OWNER RULING — row-is-match"
what: the slug searched-complement (newly homed since r59, lane preddoc5 L7) sits on core/filters/complement, and that piece cites "Source-row: yes" as a live ruling with the gloss "a row of the source is the whole subject; ... the complement is per subject". But searched-complement was the question that source-row's per-subject complement contradicted the same-stretch tie, and the owner's answer that closed it is row-is-match (23:46), which the record says "SUPERSEDES the 21:49 source-row wording ("a row of the source is the whole subject; the complement is per subject"), which was the manager's framing" and "Review r31 finding A is closed by this ruling". So the slug is homed on a piece whose `rulings:` carry the SUPERSEDED wording as current, with no `rejected:`/history line naming row-is-match; the deciding piece (core/model/match, which homes row-is-match) does not carry searched-complement. The base statement ("`!B` holds on a stretch") already follows row-is-match, so the details contradict their own base.
evidence: core_details.md 766 and 771 (quoted); record 2000-2002 (searched-complement asked: "source-row YES makes a complement per subject, which in a SEARCHED program contradicts the ruled same-stretch tie"), 2043-2050 (row-is-match SUPERSEDES source-row's wording; finding A closed).
proposed fix: move searched-complement to core/model/match (or keep it here with a `rejected:` line "the complement per subject (source-row's wording) — by owner ruling — row-is-match"); mark the source-row item's gloss as the superseded wording, citing row-is-match.

### RECOUNT-5  CONFIRMED   severity: maintenance   effort: S
where: list (b) rows numbered-duplicate, sequence-numbers, hole-member-kind (draft changelog 177-178, 1912, 1927; draft R.8 row 74 line 4017), doc-shape, definition-lane (record)
what: 5 of r59's 188 slugs are on no `slugs:` line and no document records their retirement: `entry numbered-duplicate` -> "no item" (exit 1). Three are language questions the draft says were REPLACED: numbered-duplicate and sequence-numbers by number-names (draft 1927 "rev 25 asked two, **numbered-duplicate** and **sequence-numbers**; review r43 ..."), hole-member-kind folded into value-is-pattern (draft 4017); the documents mention none of the three words, so the use-2 route "from the SLUG he answered under" fails for them. doc-shape and definition-lane are process slugs (no language piece decides them; doc-shape is referred to as "the doc-shape entry" in lib/control/peek and core/modules/default-set) — r59 held all five; this re-count agrees they are harmless but they are still "landing nowhere" by the test as worded.
evidence: `timeout 60 python3 -I recount/b_slugs.py` -> "population 188 homed 183 NOT homed 5"; `grep -c 'numbered-duplicate\|sequence-numbers\|hole-member-kind' docs/design/predicates/*.md` = 0 in every file.
proposed fix: add numbered-duplicate and sequence-numbers to the number-names piece's `slugs:` line and hole-member-kind to value-is-pattern's (each with a history line "replaced by ..."); leave the two process slugs, or put them on a `shared:` line.

### RECOUNT-6  CONFIRMED   severity: doc   effort: S
where: list (d) r59's five PARTIAL rows, draft §R.9 rows 37, 41, 68, 100, 102 (by r59's position count); core_details core/labels/backreferences, core/values/computed-labels, core/holes/flags/in-filter, core/holes/same-name; library_details lib/search/occurrences
what: every r59 MISSING row of list (d) now has a `rejected:` line, but the five PARTIAL rows were left exactly as r59 found them (the fix lane's own row for 68 says "ALREADY HOMED (partial) ... not changed"), and in each the candidate itself is still named on no `rejected:` line of the piece it was a candidate for:
 - 68 "a computed label's value "a VALUE, not a pattern"" (CHANGED to a one-string rx known at run time): core/values/computed-labels, the piece for it (new since r59), has an EMPTY `rejected:`; the only carrier is #55 on core/values/one-type, which rejects "a value in a pattern position is a STRING" — the general value, not the computed label's.
 - 100 "the manager's m2 (operands keep their own flags) as the draft's flags-in-filter reading", SUPERSEDED by REACH: core/holes/flags/in-filter has an EMPTY `rejected:`; #97 (core/holes/flags, "NO INHERITED FLAGS") is a different, older candidate.
 - 41 "R.1.9's 'its hits are those of a plain search'", NARROWED by hit-carry: lib/search/occurrences' only near item (#168) is the empty-hit claim; the narrowing is stated in the base, but the old sentence is not rejected.
 - 37 "inside rx text a backreference already reads the last-set capture" (WITHDRAWN: false under `(?J)`): backreferences rejects the namespace reading and rev 27's candidates, not this sentence.
 - 102 "`\k<h>` across a hole read as the last mention" (NARROWED by same-name-count): core/holes/same-name carries the rival and the manager's extension, not the narrowed sentence.
evidence: `timeout 120 python3 -I recount/d_rejected.py` (rows R9:37/41/68/100/102: the r59 items found unchanged at ratio 1.00, keyword search over today's `rejected:` items NONE for 37, 41, 68); draft R.9 rows printed by `awk 'NR>=3563 && NR<=3740 && /^\|/' predicates_draft.md | awk '{n++; if (n==37||...) print}'`; `awk '/^## core\/values\/computed-labels/,...' core_details.md` shows `rejected:` empty.
proposed fix: one `rejected:` line each on the five pieces, "<the old sentence> — by <owner ruling | the draft> — <the narrowing ruling>", with the draft R.9 row as the pointer.

### RECOUNT-7  CONFIRMED   severity: doc   effort: S
where: the fix lane's list-(a) claim SA-55 (sample/lens2_sample.md): "1329 ... SUPERSEDED by joint-loops (3), then after-loop-read (2323, cited on core/labels/labels-vs-captures); quoted in core/conditions/pass-start-read `history:` (slug looped-compare)"
what: the claim is WRONG on two counts. (1) Record line 2323 is "2026-11-17 OWNER RULING — last-pass-default: regex", not after-loop-read (which is 2454). (2) Neither named entry supersedes the warning: joint-loops (3) MOVES the ruled warning onto a hand-written `|` of conditions (it keeps it, and joint-loops is itself uncited), and after-loop-read (2454-2475) says nothing about the warning or `compare.looped`; the only removal on record is the manager's ("`compare.looped` and the manager's withdrawn looped-warning go to the next review as told", record 2830-2831), which is not an owner entry. The history line on pass-start-read exists (the quote is there), so the item is MENTIONED, but the SUPERSEDED disposition does not hold (RECOUNT-1).
evidence: `grep -n 'last-pass-default: regex (Frank\|after-loop-read: the last' COND-FAMILY.md` -> 2323, 2454; record 1495-1500 (joint-loops (3)); 2454-2475.
proposed fix: as RECOUNT-1 (cite 1329 + 1493; state the warning's status or ask).

## Appendix S — sample audit of the fix lane's claims (25 rows of sample/lens2_sample.md)

Method: each claim read against the record (entries in order; a supersessor must postdate and override), the subject at d8634250a (`recount/a_rulings.py`, `b_slugs.py`, `c_names.py`, grep of the six documents), and, for "by preddoc4 (79729024c)" / "c331717a6" claims, `git -C <repo> show <commit>:docs/design/predicates/<file>` grepped for the piece / slug / citation (read-only).

| row | claim (short) | verdict | evidence |
|---|---|---|---|
| SA-51 | 1223 tuple names SUPERSEDED by retire-paused (1573, cited on core/values/tuples); in tuples history; names on rejected | HOLDS | 1573 (11-16 12:51) postdates 1223 (11-15 23:06) and says "RETIRED ... the `lex_` names (CF:1226)"; 1573 cited on core/values/tuples (+ field-count, other-side-sigil); tuples history quotes "tuple_names: a"; the six names on tuples `rejected:` |
| SA-52 | 1250 argument order, same | HOLDS | 1573 "RETIRED ... the argument order (CF:1253)"; tuples history quotes "tuple-arg-order: subject low high"; "their argument order subject, low, high — by owner ruling — retire-paused" on tuples `rejected:` |
| SA-55 | 1329 looped-compare SUPERSEDED by joint-loops (3), then after-loop-read (2323, cited) | WRONG | RECOUNT-7: 2323 is last-pass-default; joint-loops (3) moves, not retires, and is uncited; after-loop-read is silent on the warning; history quote present |
| SA-56 | 1362 tuple-value ALREADY HOMED by preddoc4 (79729024c), core/values/tuples | HOLDS | 79729024c core_details core/values/tuples cites "2026-11-16 OWNER RULING + REQUEST — the tuple as a value: OK, to be fleshed out" |
| SA-58 | 1441 set-arity, same | HOLDS | cited there at 79729024c; slug set-arity on its `slugs:` line (line 851 of that version) |
| SA-61 | 1503 two-orders, same | HOLDS | cited there at 79729024c |
| SA-66 | 1727 match-context SUPERSEDED by drop-mark (1949, cited on defaults); defaults history; remark on parked/ideas/explainer | HOLDS | 1949 (21:49) postdates 1727 (16:13) and RETIRES match-context by name ("they lose their subject; none is reversed"); 1949 cited on core/conditions/defaults (and core/filters/complement); defaults history quotes "match-context: anywhere ..."; 1727 cited on parked/ideas/explainer `rulings:` |
| SA-67 | 1739 zero-pass-empty, same | HOLDS | retired by name in 1949; quoted in defaults history |
| SA-68 | 1759 domain-scope, same | HOLDS | retired by name in 1949; quoted in defaults history |
| SA-69 | 1776 mark-narrows, same | HOLDS | retired by name in 1949; quoted in defaults history |
| SA-70 | 1817 mark-in-none, same, "with the 1812 correction said" | HOLDS | retired by name in 1949; defaults history quotes 1817 and cites "2026-11-16 CORRECTION — mark-in-none is NOT ruled" (1812). Nit: the history says "his 17:29 "yes agree"", but 17:29 is the CORRECTION's clock; his "yes agree" was in the earlier entry |
| SA-72 | 2004 all-question ALREADY HOMED by preddoc4, lib/counting/some | HOLDS | 79729024c library_details lib/counting/some cites "2026-11-16 OWNER RULING — all-question: retire"; slug on line 480 of that version |
| SA-74 | 1384 tuple-anywhere ALREADY HOMED by preddoc4, core/values/tuples | HOLDS | cited there at 79729024c ("OWNER CLARIFICATION + ANSWER — "left/right" was about the binding sign; tuple-anywhere: yes") |
| SB-104 | record-is-product ALREADY HOMED by preddoc4, tuples | HOLDS | 79729024c core_details 851 `slugs: tuple-value tuple-anywhere set-arity two-orders record-is-product` |
| SB-105 | not-is-complement ALREADY HOMED by preddoc4, core/filters/negation | HOLDS | 79729024c core_details 762 `slugs: not-is-complement`; the piece core/filters/negation exists there (`ruled 2026-11-18`) |
| SB-108 | read-out ALREADY HOMED by preddoc4, core/labels/export/caller-ambiguous | HOLDS (attribution PARTLY) | 79729024c core_details 509 `slugs: caller-ambiguous read-out` — homed at 79729024c, but the piece itself already existed at 65bd0f4de; whether preddoc4 or an earlier commit added the slug was not traced |
| SB-113 | set-arity ALREADY HOMED by preddoc4, tuples | HOLDS | as SB-104 |
| SB-119 | tuple-parts ALREADY HOMED, core/modules/positional `open tuple-parts` (c331717a6) | HOLDS | c331717a6: core.md heading `open tuple-parts`, core_details `slugs: tuple-parts`; today the same, citing 1411 (REOPENED) |
| SC-175 | `some` ALREADY HOMED by preddoc4, lib/counting/some | HOLDS | 79729024c library.md has `### some [lib/counting/some] ruled 2026-11-15`; today `defined: native (...)` |
| SC-177 | `assert.some` ALREADY HOMED by preddoc4, lib/assert/assert | HOLDS | 79729024c library.md `### assert.some, assert.none, assert.same [lib/assert/assert]` |
| SC-182 | `pattern()` ALREADY HOMED by preddoc4, lib/builtin/pattern | HOLDS | 79729024c library.md `### pattern [lib/builtin/pattern] reading` |
| SC-198 | blessed callouts NOT A call-form name; a LEAN with its own plan row; ALREADY in core/modules/standard-library (preddoc4) | HOLDS | record 461 "2026-11-14 — a standard library of blessed callouts (Frank)" is a family/initiative, no call form; core_details readings of core/modules/standard-library (line 1602 today; 1547 at 79729024c) |
| SC-199 | `occurrences` label= setting NOT A call-form name; on lib/search/occurrences with its ruling (preddoc4) | HOLDS | it is an argument of `occurrences(x, label = "foo")`; 79729024c library_details occurrences cites "2026-11-15 RULINGS — a per-call hit name; ..." with his words `occurrences(x, label = \"foo\")`; today's base body states it |
| SD-242 | E19 `@each(...)` NOT A rejected candidate: OPEN by ruling (§13 O22); on lib/assert/each `readings:` (cbf0c88d6) | HOLDS | draft 8224 "**O22.** ... the `@each(...)` per-entry assertion spelling (both OPEN by ruling)"; lib/assert/each `readings:` carries it; base statement says the spelling is open |
| SD-246 | R9 68 a computed label a VALUE: ALREADY HOMED (partial) at compB's core #55; not changed | PARTLY | true that it was not changed; but #55 (core/values/one-type) rejects "a value in a pattern position is a STRING", the general value, not the computed label's; core/values/computed-labels (the piece it was a candidate for) has an empty `rejected:` (RECOUNT-6) |

TOTALS: 25 rows; HOLDS 22 (one with an attribution caveat, SB-108; one with a clock nit, SA-70), PARTLY 1 (SD-246), WRONG 1 (SA-55). (SB-108 counted HOLDS.) — correction: HOLDS 23, PARTLY 1, WRONG 1.

Note on SB-108: r59 appendix B listed read-out as NOT homed at 65bd0f4de, and it is homed at 79729024c; every commit between them on this path is a preddoc4 commit (`git log --oneline 65bd0f4de..79729024c`), so the attribution HOLDS too.

## Appendix A — list (a), r59 compA appendix A: 144 owner RULING entries

Command: `timeout 60 python3 -I /var/tmp/pcrec-pcrec/scratch/crit-preddoc5/recount/a_rulings.py S` (add `-v` for the per-entry CITED lines). Population: r59's own rule (its match.py logic, copied verbatim) over r59's record copy (`crit-preddoc3/R/subject/COND-FAMILY.md`; the r60 record differs only by appended entries, checked by a `diff` ignoring `tags:` lines) -> 144. A row is HOMED if a `rulings:` item at d8634250a cites its title (whole, or the part before " (", the lint's rule), or if a hand-named LATER entry that overrides it is so cited (`recount/a_supersede.json`, each supersessor read in the record).

| | count |
|---|---|
| expected | 144 |
| cited directly by a `rulings:` item | 135 (r59: 111) |
| held by a cited later superseding entry | 8: 1223, 1250 (retire-paused); 1739, 1759, 1776, 1817 (drop-mark); 2423 (after-loop-read); 1493 (after-loop-read, its part (1) ONLY — parts (2)-(3) have no owner supersessor, RECOUNT-1) |
| STILL MISSING | 1: 1329 "2026-11-16 RULING — a compare over looped labels warns" (its supersessor 1493 is uncited; RECOUNT-1). Strict count with 1493's parts (2)-(3): 2 |

## Appendix B — list (b), r59 compA appendix B: 188 question slugs

Command: `timeout 60 python3 -I /var/tmp/pcrec-pcrec/scratch/crit-preddoc5/recount/b_slugs.py`. Population: r59's `slugs.json` (192 candidate tokens from the frozen draft and the record) minus r59's 4 spelling variants -> 188; homes = every word on a `slugs:`/`shared:` line of the three details files at d8634250a.

| | count |
|---|---|
| expected | 188 |
| homed on a `slugs:` line | 183 (r59: 128; 55 newly homed, 14 moved, listed by the script) |
| STILL NOT HOMED | 5: numbered-duplicate, sequence-numbers, hole-member-kind (replaced questions, replacement unrecorded: RECOUNT-5), doc-shape, definition-lane (process slugs) |
| homed on a piece that does not decide it | 1 found: searched-complement on core/filters/complement (RECOUNT-4); the 55 new homes were checked by reading the line each lands on, not each deciding entry in full |
| on two or more pieces | 2, both on the `shared:` line of core_details.md (legal by L9): other-holes (core/holes/class, range-end, option), when-peek (core/diagnostics/consuming-test, lib/control/peek); `entry other-holes` / `entry when-peek` list all owners and exit 2 (the reader's ambiguity exit). No slug is on two `slugs:` lines without a `shared:` line. default-set now has ONE home (core/conditions/defaults); the 11-19 question is renamed default-imports (COMPA-12 fixed). |

## Appendix C — list (c), r59 compB appendix A: 98 provided-name rows

Command: `timeout 60 python3 -I /var/tmp/pcrec-pcrec/scratch/crit-preddoc5/recount/c_names.py` (per row: a library heading, a library body, a core heading, other mentions; then each row read by hand). COMMON's rule: a call-form name lands on a LIBRARY piece with `defined:` (all 53 library pieces carry exactly one `defined:` line: `grep -c '^### '` = `grep -c '^defined:'` = 53), or on a stated reason.

| disposition | count | rows |
|---|---|---|
| a library piece names it (heading or member list), `defined:` present | 62 | 1-10, 12-19, 22, 23, 25-28, 30-33, 36-42, 44-54, 58, 60, 62, 63, 66-71, 80-83, 88, 89 |
| a member stated on its family's library piece (body or details reading) | 3 | 61 rx.alnum (details reading on lib/rx/classes), 95 hit, 97 the label= setting (lib/search/occurrences body) |
| a stated reason (cut, retired, renamed, parked, example binding, not provided, no meaning) | 25 | 11, 20, 21, 24, 29, 34, 35, 59, 64, 65, 72, 73-79, 84, 85, 86, 87, 90, 91, 96 |
| not a call-form name, on a core piece | 4 | 92 blessed callouts, 93 `.index`, 94 `.label` (core/values/metadata), 98 the standard library |
| call-form effects homed only in the CORE (no library piece, contrary to core/operators/statements' own sentence) | 3 | 55 `@warn`, 56 `@export`, 57 `@options.strict` (RECOUNT-3) |
| STILL NOWHERE | 1 | 43 `where` (RECOUNT-2) |

Expected 98 = 62 + 3 + 25 + 4 + 3 + 1. Still missing under COMMON's rule: 1 (where), or 4 counting the three core-only effects.

## Appendix D — list (d), r59 compB appendix B: 100 rejected candidates

Command: `timeout 120 python3 -I /var/tmp/pcrec-pcrec/scratch/crit-preddoc5/recount/d_rejected.py > recount/d_out.txt` (92 table rows = 100 candidates: r59's 70 R.9 candidates with its correction row 23, + 30 beyond R.9; for each, r59's carrying items #N looked up among today's 241 `rejected:` items by difflib >= 0.80, and a keyword regex over them; every hit for a MISSING/partial row read by hand).

| r59 verdict | r59 count | today |
|---|---|---|
| carried | 68 | 68 still carried (all old items found at ratio >= 0.80, except E1, E2, E10 whose pieces were deleted and whose lines now stand on lib/modifiers/quoted, lib/modifiers/padded, lib/rx/repeat — read) |
| partial | 7 | T9 and E14 now full (core/conditions/form + parked/ideas/other-side-sigil; lib/counting/some "`all` as a group question"); 5 UNCHANGED partial: R9 rows 37, 41, 68, 100, 102 (RECOUNT-6) |
| MISSING | 25 | 24 now homed (R9 7 labels-vs-captures, 8 no-absence, 12 alternation, 14 sequence, 31 warnings, 42 numbers, 43 flow, 75 holes/flags, 79 backreferences, 106 dollar-form; T1-T6, T7, T8, T10 core/values/tuples (+ defaults, arrays/lift for T10); E15 defaults; E16 core/modules/map; E17, E18 lib/assert/assert; E20 padded + quoted); E19 reclassified OPEN, not rejected (sample SD-242 HOLDS) |
| total | 100 | landed 94, partial 5, not a rejected candidate 1, STILL MISSING 0 (5 if a partial counts as missing) |

Cross-check (asked): `rulings:` items whose cited title does not resolve. Command: `timeout 60 python3 -I /var/tmp/pcrec-pcrec/scratch/crit-preddoc5/recount/titles.py` -> "items 360 exact whole title 55 prefix-before-( only 305 NO MATCH 0 no (record:) at all 0"; no prefix citation matches two record titles (0 ambiguous); the 12 "under its bold line "..."" sub-titles all exist verbatim as bold openers in the record.

## PROBED-AND-HELD

- (a) 144 entries: 135 cited directly, every citation resolving; the 8 supersessions read in the record in order (each postdates and names the retired item, except 1493's parts (2)-(3)); r59's 27 MISSING reduced to 1.
- (b) 188 slugs: 183 homed; of the 14 moved slugs, default-set (core/conditions/defaults), nullable-meaning (lib/search/occurrences) and pass-list-read (core/values/reads), r59's COMPA-12/13, now land on the pieces that decide them; the other 11 were checked for their landing line only; retired slugs (drop-mark's five, mark-range, tuple-names/arg-order/compare, library-not-syntax, retire-paused) sit on the piece whose `rejected:`/history records the retirement; tuple-parts on core/modules/positional with status `open tuple-parts` and both 1411-era entries cited.
- No slug on two `slugs:` lines without `shared:`; `entry default-set` resolves to one piece.
- (c) 98 rows: 94 land per COMMON's rule; every one of the 53 library pieces has one `defined:` line; the new under-construction pieces (assert.each, any_order, file_literals, sort/unique, sorted/distinct, json members, planned standard) carry `defined: ?`.
- (d) 100 candidates: 0 strictly missing; 68 carried items unchanged.
- 360 `rulings:` items: 0 unresolved titles, 0 ambiguous prefixes, 12 nested bold sub-titles all exist.
- Sample: 25 claims checked, 23 HOLD; every "by preddoc4 (79729024c)" claim verified at that commit.
- Not probed: the verbatim accuracy of quotes (the RULING lens's); whether each of the 55 newly homed slugs' piece is the single best deciding piece beyond reading its line (one misplacement found, RECOUNT-4); r59's population rules themselves (re-used, not re-derived); no `re` runs (longest witness: none).

CRITIC COMPLETE
