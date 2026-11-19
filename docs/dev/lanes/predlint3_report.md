# predlint3 report: review r57 applied to the predicate-document lint (lane predlint3, sonnet, branch lane/predlint3)

## STATE AT HANDOFF

STATE: delivered. Rulings file `docs/dev/lanes/predlint3_rulings.md`: empty at every re-read (before each commit and before this report); no R-n applied.
Premise tests: the lint on the real documents printed `checks passed 2168, failed 0` (first command of the lane, before any edit); the two `.test` files passed; F1's reproduction gave rc 0 on the unchanged lint (see the table). Held.
OWED: none. No background job, nothing queued; the only `make` was `make -s test-plan-lint` (failed 0).
Branch tip: `git -C worktrees/predlint3 log -1`. Never pushed or merged. The lint is clean on the real documents: `checks passed 2278, failed 0`.
Documents touched under `docs/design/predicates/`: ONLY the added parked piece (below); no document needed repair for the stricter lint (the one candidate, F2 "every item", was resolved by taking the rule's weaker form, see F2).

## FINDINGS FIXED

Each: the plant (a `(rule, label)` row of PLANTS in scripts/pred_doc_lint.py, or an entry check in scripts/tests/entry_pieces.test) and rc before / after (before = the lint and `entry` of the tip I started from, ebeeaf3d3; after = this branch; same planted root, `--require-all`).

| id | what changed | plant (rc before -> after) |
|---|---|---|
| F1 | a `was:`/`formerly:` line no longer closes the open details field | "a rulings item after a formerly: line is still cited", "... after a was: line ...", "a slug continuation after a was: line is still a slug" (0 -> 1 each; the r57 repro is the first) |
| F2 | a `principle` piece needs one rulings item naming `(class: <word>)` (L4) | "a principle piece with no item naming the class", "... whose class is empty" (0 -> 1); controls: a second item without a class, `(class:x)` |
| F3 | `was:`/`formerly:` anywhere in a base file (any case, indent, blanks before the colon, preamble or piece) is L6 | `formerly:` in a piece body with the status date, `Was:`, indented `was:`, preamble `was: core/other` / `formerly:` (0 -> 1 each) |
| F4 | `module:`/`default:` in any details file, any field, any spelling, is L12 | "'module:' / 'default:' / 'Module:' / '  default:' inside a details history field", and inside a slugs field (0 -> 1; the slugs form no longer fails L9 by accident) |
| F5 (narrow form) | every field-looking line (needs, by, see, was, formerly, skeleton, module, default) must be a known field, spelled exactly, in its place (L2 base / L3, L12, L2 details); the old marker `modes: n/a (skeleton` in any case or blanks; `skeleton:` and `default:` at most once | `See:`, `  see:`, `see :`, a field in a section preamble (six fields), `Needs:` ..., `modes: n/a (Skeleton, later)`, blanks inside the marker, `skeleton: yes` twice, `default: yes` twice, a second value checked (0 -> 1 each) |
| F6 | `formerly:` name = the last dotted word (identifier), the rest the L12 module grammar or `?` | `text.Foo.Pad`, `text.2pad`, `.pad` (0 -> 1); control `text.sub.Pad_2` |
| F7 | a four-word tag needs its three-word parent as a live piece earlier in the same file | "no parent piece", "parent comes later" (0 -> 1); control: parent first |
| F9 | every tag on a record `tags:` line (L5) is a live piece, a section or a previous tag | "a was: line lost: the record still cites the previous tag", "a record tags: word names no piece" (0 -> 1); controls: previous tag, section, commas, a fence, an indented line, pilot mode skip and its `--require-all` twin |
| F10 | `entry -g` matches and ranks a previous tag as the item's id | `entry -g core/holes/word -p predicates`: rc 1 -> 0 (check "-g finds a piece by a previous tag", plus a rank check) |
| F11 | the live-tag arm answers EXIT_AMBIG when two pieces own a tag, as the previous-tag arm does | `entry lib/names/padded` on a duplicated live tag: rc 0 -> 2 |
| F13 | the mutation rows and their plants (see MUTATION GATE); floors set to the sample's exact counts so a dropped counter fails | mut.py |
| F14 | a control expecting {L1, L2, L3, L5} for a cross-file duplicate tag; the EQUIVALENT row is gone | mut.py: "L1 tag uniqueness per file" now killed |
| F15 | doc_format.md folded (SPEC FOLD) | the file |
| F16 | scripts/entry's header (the `predicates` profile and the previous-tag key), the lint docstring (item continuation lines, which sections, `--write-ratchet`), spec sentences for the CONTRACT-12 behaviours, a NOT CHECKED paragraph | the files |

Process change applied: every line field the lint parses is planted misplaced (preamble, wrong file), misspelled (case, indent, blank before the colon) and doubled where it has a cardinality; the block's existing items are planted AFTER a new line kind (F1). The plants come from a generator (GENERATED in pred_doc_lint.py) over the field list, so a new field is one row.

Judgement calls (mine, to be overruled by the manager if wrong):
- F2 "every item" would fail two real items (`core_details.md` lines 53 and 79 are principle pieces whose second item names no class), so the lint takes "at least one item names the class", matching L4's "at least one rulings item". No document was edited. A stricter "every" is one line.
- F9: `parked/import-symbols`, which eight record entries cite, is a two-word SECTION tag, not a piece tag (a piece tag has three or four words), so no piece could make it resolve. I made a record tag resolve to a live piece, a section or a previous tag, and added the section `parked/import-symbols` with the `?` piece `parked/import-symbols/import` (parked.md, parked_details.md; ratchet row `parked` raised 0 -> 1 BY HAND, as ruled). The record is untouched. The eight lines failed before that: COND-FAMILY.md lines 5312, 5334, 5356, 5388, 5404, 5424, 5434, 5452. library_details.md's history line "no parked piece on import exists to carry it" (line 72) is now stale; I left that document alone (the manager's to edit). The manager may prefer to retag the eight record entries to the piece tag.
- F9 cannot detect REUSE of a retired tag once its `was:` line is deleted (not checkable from the documents alone, as the ruling said); the spec's NOT CHECKED paragraph says so.

## FINDINGS NOT FIXED

All as ruled (PLAN), with the review's reason:
- F8 (L8 accepts the three mode words on any body line, the statement included; a bare `modes: n/a` without its `(<why>)` passes): pre-existing, not this diff; the spec now says it plainly (NOT CHECKED).
- F12 (an `open <slug>` piece need not list its slug on its details `slugs:` line, so `entry <slug>` misses it): pre-existing; a resolver question, with G3.
- G1 (one committed monotone ledger: `?`/skeleton counts and the retired-tag set); trigger: the first skeleton promotion or demotion, or the retired half if the `tags:` check proves too weak. Known hole it would close: a full piece demoted to skeleton while another is promoted keeps the count.
- G2 (one declared field table drives parse and lint); trigger: the next field (the import request already in the record) or the first F5 follow-up. The narrow F5 form is built; GENERATED is the seed of that table.
- G3 (one resolver with a per-site policy row for every place that names a piece); trigger: the first rename after the pilot.
Nothing did not reproduce: every FIX-NOW finding reproduced by verify.md's command (rc 0 before) and fails now.

## MUTATION GATE

`python3 -I scripts/tests/pred_doc/mut.py` -> `mut: total 316, killed 301, equivalent 15, SURVIVED 0, NOMATCH 0` (was 212 / 196 / 16 / 0).
- about 105 new rows: META_RE per word (8), FIELDLIKE per word and per clause (11), OLD_SKEL (5), the base and details field-line handlers (16), the move line (F1), the principle class (4), `formerly_ok` and IDENT / MODULE_RE character classes (11), the fourth-word parent (3), the record `tags:` check (11), doubled fields, `[:1]` and counter mutants (the critic's survivors), and 11 rows of the reader side.
- The reader is now in the population: rows of kind `me` mutate scripts/entry and the lint's reader functions and run `scripts/tests/entry_pieces.test` (previous-tag arm off / by prefix / one owner / rc 0 on two owners, `entry_was` on an entry-less piece, the ungrammatical `was:` fallback, only the first `was:`, `-g` blind to a previous tag, id rank).
- The review's about 30 survivors: all killed (MUTANTS-1 five META words, MUTANTS-2 six character classes, MUTANTS-3 the crash and fallback, MUTANTS-5 the `[:1]` and counter rows, MUTANTS-6 the rc rows, the three the coordinator verified).
- 15 equivalent, each named with its reason in EQUIVALENT: 13 selftest-assertion rows (killed only combined with a lint mutant, by construction) and two argued: "L6 word review r\d+ removed" (the bare `r\d+` alternative covers it) and "L10 write: ignores old" (write_ratchet writes after a clean lint, so count <= row). "L1 tag uniqueness per file" LEFT the list (F14).
- Eight rows first survived and were killed with new plants or controls: a blank before the colon, one blank after `modes:`, fenced field lines (base, details), a class written `(class:x)`, a record tag in a skipped pair under `--require-all`, a previous-tag prefix.
- `rep.ok` counters: the floors now equal the sample's counts (L1 15, L2 27, L3 3, L4 16, L5 8, L6 58, L7 10, L8 4, L9 7, L10 6, L11 4, L12 10), so a dropped counter fails.

## SPEC FOLD

docs/dev/pred/doc_format.md rewritten once, top to bottom: the three post-pilot sub-sections are folded into the upper half and gone; no rule changes meaning (where two sentences disagreed the later sub-section won). Sections: What the files are for; The files; Tags; Pieces and status; Rules of use; The lint (L1-L12 each said once, the r56 "beyond the rule sentences" bullets folded into their rules, plus a NOT CHECKED paragraph and the reader); Migration; History of this format (the STATUS provenance: pilot, r56, the owner's changes, r57). The 23 stale sentences of CONTRACT-13 are gone: the PROPOSED / "Not built" STATUS and the census path (temp-root) dropped; "read in this order; a file uses only what is before it" replaced by `needs:` backward / `see:` any; "Tags are never renamed ..." and "supersedes the paths in the table above" gone; the templates carry `see:`, `module:`, `default:`, `skeleton:`, `was:`, `formerly:`, `(class: ...)`; the status set carries `principle`; L1, L2, L4, L5, L6, L8, L10 and the reader carry their clauses; L12 is listed; "requested from main" gone; the PILOT MODE and L8 bullets are inside L5 and L8. New sentences (the manager's to confirm): a split keeps its parent as hub (F7), a principle needs a class item (F2), record `tags:` resolve (F9), the move line closes no field, a field-looking line must be exactly spelled and placed, `entry -g` sees previous tags, `module:`/`default:` never in a details file. Critic texts cite the file by line (l.40 etc.): they name the pre-fold file; no hook objected, none was edited.
Review filed: docs/dev/reviews/2026-11-19-r57-preddoc2.md (dispositions RULED 2026-11-19, an "applied in lane predlint3" line per fixed item), line added to docs/dev/reviews/NOTES.md; this report added to docs/dev/lanes/NOTES.md.
Not touched: `tests/doc_lint/run_doc_lint.sh` line 64's comment still says "rules L1-L11" (under tests/, outside this lane's scope); the review's guide-lesson text (`.claude/skills/pcrec-critic`) is main's.

## EVIDENCE AND COMMANDS

    python3 -I scripts/pred_doc_lint.py                        -> checks passed 2278, failed 0 (real documents)
    python3 -I scripts/pred_doc_lint.py --selftest             -> selftest: 245 runs, 12 rules with a detected plant of 12, 0 failures
    bash scripts/tests/pred_doc_lint.py.test                   -> PASS (sample: checks passed 168, failed 0)
    bash scripts/tests/entry_pieces.test                       -> entry_pieces: 0 failures; PASS
    python3 -I scripts/entry --selftest                        -> 75 checks, 0 failures
    python3 -I scripts/tests/pred_doc/mut.py                   -> mut: total 316, killed 301, equivalent 15, SURVIVED 0, NOMATCH 0
    make -s test-plan-lint                                     -> checks failed: 0
    python3 -I scripts/entry --lint-scripts                    -> 68 index lines, 0 failures
Before/after rc: /var/tmp/pcrec-pcrec/scratch/predlint3/cmp.py (old lint from ebeeaf3d3 against the new plants) and cmp2.py (old and new `entry`); the table above carries the numbers.
