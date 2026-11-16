# predspec15 — predicates_draft.md rev 14 -> rev 15, review r16 filed (lane predspec15, opus, 2026-11-15)

Design only, no build go. Branch `lane/predspec15` (cut from local main at f126537e1). Rulings: COND-FAMILY.md on
main through CF:1162 (the 21:21 entry, arriving during the lane as rulings R-1), plus rulings R-2 (the owner's usage
question on word boundaries).

## STATE AT HANDOFF

- STATE: done. Rev 15 committed on `lane/predspec15`; review r16 filed; this report, the evidence script
  `docs/dev/lanes/predspec15_anchor.py` and its output `predspec15_anchor.out` committed beside it.
- Rulings file `docs/dev/lanes/predspec15_rulings.md`: last entry applied **R-2** (read before each commit and before
  this report; R-1 and R-2 both applied).
- R-1's check ("if ANY row shows `x & anchored(r)` differing from `x & r` ... report it FIRST"): NO such row. Table
  (I) tried r = `/foo/`, `/foo$/` and `/foo\n?/` on a trailing newline, `/(?m:a$\n^b)/`, an `&` chain
  (`/\d+/ & <256`, by derivation: the inner `&`'s role is the hole's text, which `\A`/`\z` pin to the stretch), a
  `label:` condition, and a side of `&` in a hole: SAME in every one. They differ only around a whole FINAL program
  (`/\d+/ & anchored(<256)` vs `anchored(/\d+/ & <256)` on `x300 12`: 1-3 vs no match) and in a hole (no role).
- Mergeable into main: YES. `git merge-tree --write-tree main lane/predspec15` reports no conflict (main is one
  commit ahead, d2496010e, COND-FAMILY.md only, which this branch does not touch).
- Validation, in the worktree (the box in the owner's evening hold: no suites, no queue jobs): `make
  test-plan-lint` GREEN (2 passed, 0 failed; also GREEN before the merge and after it); `make test-spec-history`
  GREEN (11 passed, 0 failed); `scripts/check_claudemd_size.sh --all`: 370 files within limits. Evidence: `timeout
  300 python3 -I docs/dev/lanes/predspec15_anchor.py` (run from the lane scratch dir) -> `predspec15_anchor.out`,
  rc 0, **engines disagree on 0 rows** (libpcre2-8 10.46 via ctypes vs Python 3.14 `re`).
- Index: one line added to `docs/dev/history/claude_md/docs__dev__lanes.md` (this report) and one to
  `docs/dev/reviews/CLAUDE.md` (review r16).
- Owed: none.

## MERGE OF lane/predspec14

`git merge --no-ff lane/predspec14` run alone (9d942fb82). One conflict, in the index file
`docs/dev/history/claude_md/docs__dev__lanes.md` (main's six lane lines vs predspec12/13/14's three): both sides
kept, markers removed, no line lost (checked: the merge's diff against the first parent deletes nothing).
COND-FAMILY.md did not conflict. Nothing else conflicted. `make test-plan-lint` GREEN before and after.

## REVIEW FILED

- `docs/dev/reviews/2026-11-15-r16-predspec14.md`: the coordinator's draft, retitled, with "DISPOSITIONS RULED
  (manager, 2026-11-15)" carrying the brief's ruling text verbatim and the note that COND-FAMILY.md binds for the
  owner's rulings. No `plan.md` line cite and no spec line cite (checked by grep; `make test-spec-history` GREEN).
- `docs/dev/reviews/2026-11-15-r16-predspec14/`: the three critic files, `verify.md`, the repro scripts and outputs
  (`sim.py`/`.out`, `bodies_check.py`/`.out`, `tuple_check.py`/`.out`, `marks12.py`), `COMMON.md`, `process.md`.
- Indexed in `docs/dev/reviews/CLAUDE.md` (9,263 bytes, under 12 KB; nothing moved to NOTES.md).
- Process changes (both ACCEPTED), applied as worded: `.claude/skills/pcrec-critic/SKILL.md` simulate row (a
  diagnostic's semantic claim gets a counter-case per place it fires) and fix-induced row (a restated decision is
  diffed against the earlier sentence); `docs/dev/guide/critics.md` "Lessons from review rounds" (r16 entry, newest
  first); `docs/dev/meta/coordinator_framework.md` (the round's framework note).

## FINDINGS FIXED

By id (review r16; every id applied in rev 15 of `docs/design/predicates_draft.md`):

| id | disposition | where in rev 15 |
|---|---|---|
| W1 (= SIMULATE-2 + FIXIND-8) | FIX-NOW | §11 THE WARNING: one criterion, the "i.e." gloss deleted; holes excluded from the role's own text by statement |
| W2 (= SIMULATE-1) | FIX-NOW (edge criterion ADOPTED) | §11 THE WARNING (rule + counter-case table), §7.1, §0.1 REV 15 paragraph, DECIDED (36) |
| W3 (= SIMULATE-3) | RULED by the owner during the lane (R-1, CF:1154 on main) | §11 THE ROLE TABLE (macro-body text clause), §8 ANCHORED AND THE TIE, L69, §0 rulings table; no longer an owner question |
| W4 (= SIMULATE-4) | FIX-NOW (doc) | §11 THE WARNING "the silence in a hole is the hole ruling", THE ROLE TABLE row 5, §2.7, L13 |
| SIMULATE-5 | FIX-NOW | THE ROLE TABLE's fix-hint column; THE MESSAGE names the row's hint |
| SIMULATE-6 | DOC | §11 THE WARNING (per occurrence); §13 O66 trigger witness `tagged(/^a/)` |
| SIMULATE-7 | DOC | §0.3 record row; THE ROLE TABLE row 7; §12 REV 15 |
| FIXIND-1 | FIX-NOW | §13 O69: 3-field entries padded throughout; re-oracled 448 cases, 0 differ (2-field 2208, 0 differ), table (T) |
| FIXIND-2 | FIX-NOW | §2.7, §8, L13, rulings table row, decision (32) WITHDRAWN, E-CTX-5, §11: bodies verbatim, the group only spells out the hole |
| FIXIND-3 | FIX-NOW | §2.7 bodies table: `length`, `month_numbered` bodies with the three caveats; two remain |
| FIXIND-4 + CENSUS-1 + CENSUS-3 | FIX-NOW | §2.7 (body-scoped sentence; a bodyless argument stated once, LEAN), THE ROLE TABLE as the one list (§0.3 x2, §5.4, §7.1, STRING SETS, rule bullet point at it), §2.1/§2.2/§2.3/§2.7 "parameter is a filter" respelled |
| FIXIND-5 | FIX-NOW | rulings table row, §2.7 BODIES heading, §13 O67: the record's sentences attributed to the manager |
| FIXIND-6 | FIX-NOW | O68, O69, changelog: "preferred" = the manager's judgment (CF:1144); §9: the owner's reason and the record's, apart |
| FIXIND-7 | FIX-NOW | rulings table rev 13 row: `anchor.whole`, reach RULED, criterion rev 15 |
| CENSUS-2 | FIX-NOW | §0.3 filter modifier row (by body or by the pullback; "pullback" = the primitive); §2.7 heading |
| CENSUS-4 | FIX-NOW | G4, L16, L18, §2.6 STATUS (2), §5.6, §5.6 STATUS, §11 (2), O36: own-voice "search" respelled |
| CENSUS-5 | FIX-NOW | §0.3 "anchored" row (`\A`/`\z` RULED, the rest LEAN; "whole-subject mode"); L19, §7, O10, O57 sites |
| CENSUS-6 | FIX-NOW | §0.3 scoped match row; "scope" -> "scoped match" (§8, §11, L68), "group namespace" (§11 literals), "extent" (§11, STATUS) |
| CENSUS-7 | DOC | §0.3 span/stretch row |
| CENSUS-8 | FIX-NOW | §5.4 MARK TABLE `${ }` row: E-HTTP dropped (3 cases) |
| CENSUS-9 | NOTED | nothing to change in the spec |
| CENSUS-10 | DOC | E-NEAR's input `anchor` -> `ref` (code, prose, §6.1 error text, §13) |
| CENSUS-11 | FIX-NOW (cheap form) | §11 THE ROLE TABLE |

THE WARNING'S FINAL RULE (§11 THE WARNING `anchor.whole`): it fires exactly on an explicit `^`, `$`, `\A`, `\z` or `\Z`
(with or without `(?m)`) that (1) stands in the OWN TEXT of a filter role after macros are expanded (INCLUDING text a
macro body writes, whoever wrote it, RULED CF:1154; EXCLUDING text inside a hole, a hole being no role) and (2)
provably sits at the EDGE of that role's stretch (no path from the role's start to `^`/`\A` consumes text; the mirror
for `$`/`\z`/`\Z`). A non-edge anchor never warns; an edge anchor in a hole is silent by the hole ruling; a parameter
used twice is judged per occurrence.

THE ROLE TABLE (§11; the one list of positions; fires = on an edge anchor in the row's own text):

| # | position after expansion | opens a scoped match over | fires | fix hint |
|---|---|---|---|---|
| 1 | a side of `&` in a final program | the reported match | yes | put the anchor around the WHOLE final pattern, `/^(?:...&...)$/` (`anchored(...)` writes it); else drop it |
| 2 | a side of `&` inside a hole | the text the hole takes | yes | put the anchor or `\b` in the rx AROUND the hole |
| 3 | a `label:` condition | the label's text | yes | "starts with": `startsWith(...)`; "exactly": drop the anchor |
| 4 | a compile-time set | each whole string | yes | as row 3 |
| 5 | a hole | nothing | never (hole ruling) | |
| 6 | a final pattern | the subject | never | |
| 7 | a `records` item rx | its file text | never (a narrowed item is a one-string set) | |
| 8 | the argument of `any_case` / `json.quoted` | the transform's reading | yes (LEAN, O67) | drop the anchor |

Macro-body text standing in row 1 (`x & anchored(r)`): fires, hint "here `\A`/`\z` are the ends of the stretch both
sides already match whole, so `anchored` changes nothing; write r". Counter-cases for the message's claim in every
place it fires: `predspec15_anchor.out` table (W) (19 rows; claim true at every warning; every non-edge plant changes
the answer).

THE any_case RESULT (§2.7 table; `predspec15_anchor.out` table (A), 781 strings over `hHoO1`, lengths 0-4):
`any_case(rx) := /(?i:${rx})/` is NOT a plain body. Under this document's hole rule (a hole keeps its own flags, §11
NO INHERITED FLAGS, §13 O32) the body is S itself: it differs for every argument with a cased letter (one literal
`/ho/`: 3 differ) and passes only a number filter (`<12`: 0 differ), trivially. Even under a raw textual paste
(`(?i)` reaching every pasted hole) it passes one literal and a gap-bodied nested transform (`startsWith("h")`: 0
differ) but fails any argument holding a FILTER ROLE, a separate whole match with its own literal: an `&` (155
differ), a `label:` condition (3 differ), hence also `quoted`, `left`/`right`/`mid`, and the new `length` /
`month_numbered` bodies. TWO transforms remain without a body: `any_case`, `json.quoted`.

ROWS THAT MOVED (look-alike rows and §12 cases, re-applied under rev 15): ANSWER MOVES: none. DIAGNOSTIC MOVES: L69
(SAME; the warning now also fires on `anchored(r)`, RULED). REWORDED: L13 (body verbatim; silence stated as the hole
ruling), L68 ("scoped match"), L16, L18, L19 (words). UNCHANGED, re-checked under the edge criterion: L7, L11, L15,
L41, L70, L71 (every anchor they warn on is an edge anchor), L13, L17, L63 (hole: silent), L20, L66, every row
without an anchor in a filter role. §12: no answer moves; E-NEAR's input renamed `ref`; E-CTX-1/7 still warn,
E-CTX-5 silent, E-HTTP's `anchored(block)` a final pattern (row 6), E-FILE's item anchors never reach a role.

ALSO IN REV 15: §8 ANCHORED AND THE TIE (R-1: the owner's "is that an identity?" answered with oracle rows, table
(I)); `anchored` written as a library convenience for the outer edge, its definition check moved from §11 to §8, no
rule or table depending on it (the owner's remark, CF:1151-1152); §11 WORKED EXAMPLE: LOOKING FOR WORDS (R-2,
table (B)): `/\b(a|boo|great)\b/` alone is plain PCRE (`a` at 0-1 on `a boo greatness`, nothing on `xboo`, `boo` at
0-3 on `boo.`); with a filter the `\b` stay outside a hole, `/\b${ /a|boo|great/ & F }\b/` (`boo` at 2-5, nothing,
0-3); `/\b(?<w>a|boo|great)\b/ & (w: F)` and `/\b(a|boo|great)\b/ & F` are the EDGE-ASSERTION ERROR (a `\b` at the
edge of an `&` side), each with a one-step rewrite giving the same answers, so **word-boundary-with-filter** is NOT
raised. Changelog rev 15; DECIDED (36)-(43); §15 provenance row.

## QUESTIONS FOR THE OWNER

- **tuple-compare** (open). Should the first library carry fixed-size tuple compares, for 2 and 3 fields? Example:
  a time range 9:00 to 10:00 written `t & tuple_between2(/\d{1,2}/, ":", /\d\d/, 9, 0, 10, 0)`: accepts `9:00`,
  `09:30`, `10:00`, rejects `10:01`. Both sizes are plain macros with nothing new in the language (the 3-field one
  corrected in rev 15 and checked on 448 cases). Lean: yes, the fixed sizes now; any number of fields later.
- **primitive-transforms** (open, premise corrected). Only TWO library transforms read text that is neither in the
  subject nor produced by the match: `any_case` (letter case ignored) and `json.quoted` (the decoded string).
  Example: `any_case("host")` must accept `HOST`, which no body over the subject can say (the obvious
  `/(?i:${rx})/` was tested and fails). `length` and `month_numbered` turned out to have ordinary bodies. Should
  those two rest on ONE primitive ("S matched whole on what the transform reads"), so every rule talks about roles
  only? Lean: yes.
- **warn-in-macro-body**: ANSWERED during the lane (CF:1154 on main): no exemption; `x & anchored(r)` warns. His
  follow-up "is that an identity?" is answered in the draft (§8 ANCHORED AND THE TIE): only where `anchored(r)`
  stands directly beside `&` or in a label condition; around a whole program or inside a hole it is different.
