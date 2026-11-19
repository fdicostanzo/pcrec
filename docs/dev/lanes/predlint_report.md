# predlint report: scripts/pred_doc_lint.py

## STATE AT HANDOFF
OWED: none

Complete incl. ruling R1 (L8 exemptions, applied); branch lane/predlint, committed. The rulings file predlint_rulings.md was empty (no entry applied). No owed runs. Not wired into make (see WHAT WAS NOT BUILT).

## WHAT WAS BUILT
- `scripts/pred_doc_lint.py` (stdlib only, runs under `python3 -I`): the L1-L11 structure lint, a planted-fault `--selftest`, `--write-ratchet`, and the reader (`--show`, `--list`). Paths follow the spec defaults, `--root DIR` (default: the repo), `--require-all`.
- `scripts/tests/pred_doc/root/`: the committed sample, a valid 3-piece base + details file per pair, a fixture record (COND-FAMILY.md with two titles) and a fixture ratchet. The selftest copies it into `$PCREC_TMPDIR/scratch/predlint/` and plants faults by hand-written text substitutions (each asserts its target text occurs once).
- `scripts/tests/pred_doc_lint.py.test` (runs on `make testscripts`), INDEX.md line, scripts/CLAUDE.md list, scripts/tests/NOTES.md line, lanes CLAUDE.md index line. `entry --lint-scripts` 0 failures; `check_claudemd_size.sh --all` within limits.
- Output: `RULE file:line: message`, `WARN ...` for soft caps, `note:` lines (skipped pair, absent ratchet), a `checked: L1=n ...` line so a rule that checked nothing is visible, and `pred_doc_lint: checks passed P, failed F`. Exit 0 clean, 1 on failure.

## RULES AND THEIR PLANTS
Each plant is asserted to fail exactly its own rule (the set of failed rule ids must equal the one expected), not just a non-zero exit.

| rule | what it checks | the plant | detected |
|---|---|---|---|
| L1 | tags (and section tags) unique | a second piece takes an existing tag | yes |
| L2 | tag grammar; tag file+section equal the piece's, unless `was:` | upper-case tag; tag in the wrong section | yes, yes |
| L3 | base pieces and details entries in bijection, same order; details file present | entry deleted; entries reordered | yes, yes |
| L4 | status in set, date valid, `open` has a slug, `parked` only in parked; ruled piece has a `rulings:` item; every item's record title exists | `blessed`; `open` no slug; ruled with no item; title absent from record | yes x4 |
| L5 | `needs:`/`by:` exist; needs earlier (file order, then position); by under core/principles | missing target; later in file; later file; by not a principle | yes x4 |
| L6 | history words outside code fences | `WITHDRAWN`; `Rev 29` | yes, yes |
| L7 | statement <= 200, piece <= 40 lines, statement present (WARN: file size over soft cap) | 201-char statement; 45-line piece | yes, yes |
| L8 | piece (not `?`, parked, under-construction, or under core/principles/) has an example naming WHOLE, SEARCHED, FIND-ALL, or `modes: n/a` | example names only WHOLE | yes |
| L9 | a slug on 2+ tags must be listed `shared:` | the `shared:` line removed | yes |
| L10 | `?` count not above the ratchet file's | ratchet lowered below the count | yes |
| L11 | an existing base (or details) file has pieces (entries); `--require-all` makes an absent base fail | base and details with no pieces | yes |

Positive controls (all pass in the selftest): `was:` excuses the path check; a history word inside a fenced block is exempt; an absent pair is skipped with a note, and fails L11 under `--require-all`; an absent ratchet is one note; a soft-cap overrun is a WARN with exit 0; `--write-ratchet` lowers and never raises. Clean-sample per-rule floors (hand-written): L1 9, L2 12, L3 3, L4 9, L5 4, L6 30, L7 9, L8 3, L9 4, L10 3, L11 3; the clean run reads `L1=13 L2=13 L3=3 L4=13 L5=4 L6=49 L7=9 L8=3 L9=7 L10=3 L11=3`.

Selftest output:

```
selftest: plant L1  duplicate tag                            detected
selftest: plant L2  tag grammar (upper case)                 detected
selftest: plant L2  tag path differs from its section        detected
selftest: plant L3  base piece with no details entry         detected
selftest: plant L3  details entries out of order             detected
selftest: plant L4  status outside the set                   detected
selftest: plant L4  open without a slug                      detected
selftest: plant L4  ruled piece with no rulings line         detected
selftest: plant L4  record title absent from the record      detected
selftest: plant L5  needs: names no piece                    detected
selftest: plant L5  needs: target later in the file          detected
selftest: plant L5  needs: target in a later file            detected
selftest: plant L5  by: target not a principle               detected
selftest: plant L6  WITHDRAWN in a base file                 detected
selftest: plant L6  'Rev 29' in a base file                  detected
selftest: plant L7  statement of 201 characters              detected
selftest: plant L7  piece of 41+ lines                       detected
selftest: plant L8  example line names one mode              detected
selftest: plant L9  slug on two tags, not shared             detected
selftest: plant L10 more '?' pieces than the ratchet         detected
selftest: plant L11 base file with no pieces                 detected
pred_doc_lint: wrote docs/dev/pred/doc_ratchet.tsv: core=1, lib=1, parked=1
pred_doc_lint: wrote docs/dev/pred/doc_ratchet.tsv: core=0, lib=1, parked=1
selftest: 22 runs, 11 rules with a detected plant of 11, 0 failures
```

## THE READER
`--show KEY [-l 0|1|2]`: KEY is a tag or a slug of a details `slugs:` line; level 0 heading + statement, 1 the whole base piece, 2 plus the details entry. Exit 0 found, 1 none, 2 a non-shared slug on 2+ tags (all printed); a slug listed shared prints all and exits 0. `--list [STATUS]` prints level 0 of every piece (`open` matches `open <slug>`); exit 1 if none. Both skip absent pairs and do not lint. Checked in the selftest by hand-written expectations (level-0 text, 6-line level 1, slug at level 2, none, shared, ambiguous, list ruled/open).

## WHAT WAS NOT BUILT
- A `scripts/entry` profile: `doc_profiles.py` profiles are one `index` + one `details` file with one `id` regex and `form` single/pair/archive/list/dormant. Three pairs, path-tag keys (`core/holes/class`) and slug lookup through a `slugs:` field are none of those; it would need new accessor code (multi-file pair form, a tag-grammar id, a slug index, a read-order rule). Not written; main decides. `pred_doc_lint.py --show/--list` covers the reading meanwhile.
- The `make` target: `test-plan-lint` is named in two `.PHONY`-style lists and the `test:` prerequisite list, so a target is not a two-line change. The Makefile is untouched. The lint is run by `scripts/tests/pred_doc_lint.py.test` (`make testscripts`); a make target would be: `python3 -I scripts/pred_doc_lint.py --selftest && python3 -I scripts/pred_doc_lint.py` (absent pairs are skipped).
- The ratchet file `docs/dev/pred/doc_ratchet.tsv` (not created, per the brief; `--write-ratchet` creates it).

## SPEC AMBIGUITIES (stricter reading taken)
1. The spec's example tag `lib/padded` has two segments; its grammar says `<file>/<section>/<piece>`. The lint requires 3 or 4 segments, so `lib/padded` fails L2.
2. "Listed shared" (L9) has no syntax: chosen a `shared: slug ...` line in any details file before its first entry.
3. L8's scope (R1, ruled by the predicate manager): every piece except status `?`, `parked`, `under-construction` and pieces under `core/principles/`; one positive control per exemption (an exempt piece with no example line passes).
4. A record title: matched against a `### ` heading or a `**...**` opener, exactly or the part before the first ` (`; every `rulings:` item must carry a record title and it must exist, not only a ruled piece's. A ruled piece with no items fails.
5. A non-`?` piece with no statement line fails (filed under L7); every heading needs a date; `parked` status outside the parked file fails L4.
6. A `needs:`/`by:` whose pair is skipped (absent) is not a failure, unless `--require-all`.
7. A malformed heading is reported as L2 (base) or L3 (details).

## EVIDENCE AND COMMANDS
- `python3 -I scripts/pred_doc_lint.py --selftest` -> rc 0 (output above).
- `bash scripts/tests/pred_doc_lint.py.test` -> PASS; sample lint: `checks passed 123, failed 0`.
- `python3 -I scripts/pred_doc_lint.py --root <worktree>` (no documents exist yet) -> notes only, rc 0.
- `scripts/entry --lint-scripts` -> 68 index lines, 0 failures; `scripts/check_claudemd_size.sh --all` -> within limits.
