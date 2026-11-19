# predlint2 report: review r56 applied to scripts/pred_doc_lint.py (lane predlint2, sonnet, branch lane/predlint2 off lane/pred-rev28)

## STATE AT HANDOFF

STATE: delivered. Rulings file `docs/dev/lanes/predlint2_rulings.md`: last entry applied = R1 (a record title may contain a quote; the cited title runs to the LAST `")` of the item, an item may wrap: applied, with a positive control for the inner quote, one for the wrapped item, and the missing-`(record:` plant kept). Nothing owed.
Premise tests: (1) the review file exists, ends in MANAGER RULINGS: held. (2) the unchanged lint's selftest ended "0 failures": I did not run it before editing (I read it and went straight to the rewrite). (3) the harness mut.py against the unchanged lint: NOT re-run; the critic's out.txt (checks_harness/out.txt) lists the survivors and my reading of the code agreed with it. Reported, not hidden.
OWED: none
Branch tip: see `git -C worktrees/predlint2 log -1`. Never pushed or merged.

## FINDINGS APPLIED

Every plant is `(rule, label)` in PLANTS of scripts/pred_doc_lint.py and asserts its exact rule id (and a count where one clause is isolated); `C:` is a CONTROLS row (expects no failure).

| id | what changed | proof (plant / control) |
|---|---|---|
| CONTRACT-1, CHK-5 | L6 words case-insensitive, one plant per word | L6 plants WITHDRAWN, withdrawn, REVERSED, reversed, SUPERSEDED, superseded, `[REV]`, Rev 29 |
| CONTRACT-2 | L6 date clause: any ISO date other than the piece's heading date | L6 "a date other than the status date", "another piece's status date"; C: the piece's own date |
| CONTRACT-3 | `\b` on every word; `revision N`, `review rN`, bare `rN` added | L6 revision 29.1, review r56, a bare r56; C: prev 2, r2d2 |
| CONTRACT-5 | the file part of a tag is always checked; `was:` must name the section path | L2 "tag in another FILE, excused by a was: line", "was: names another section"; C: was: excuses a moved piece's section |
| CONTRACT-6 | duplicate details entry fails L3 | L3 "duplicate details entry" |
| CONTRACT-7, ROBUST-3 | ratchet strict: every non-blank line `word<TAB>int`, known word, no duplicate, a row per present pair, absent file fails under --require-all | L10 space-separated, not a number, three fields, duplicated, unknown word, lacks a row, absent under --require-all; C: absent file is a note (note asserted) |
| CONTRACT-9 | record title = `## `/`### ` heading or a dated bold opener starting a paragraph, joined across lines; whole title or the part before ` (` | L4 plain bold paragraph, partial title, glued opener, fenced title; C: `##` title, whole `###` title, two-line opener, dotted title, doubled blanks |
| (pilot) | two-line bold opener joined to its closing `**` | C: "citation of a two-line bold opener" (the fixture record carries one) |
| CONTRACT-12 | the statement is the first non-blank line after the heading and must not be metadata or fenced | L7 "no statement line", "statement after a blank line", "a fenced block where the statement belongs" |
| CONTRACT-10(d) (ruled) | EVERY rulings item cites an existing title | L4 "a wrong item beside a right one", "a bad item on a non-ruled piece" |
| CONTRACT-4, CONTRACT-10 | code now equals the text of doc_format.md; L8 not asked of `?` | C: L8 exemptions (?, parked, under-construction, principle) |
| ROBUST-1, CONTRACT-8 | missing --root is usage error rc 2; no pair at all fails L11; an orphan details file fails L3 | .test (rc 2, not created); L11 "no pair at all"; L3 "details file with no base file" |
| ROBUST-2 | --write-ratchet only after a clean lint, lowers only, never creates a root | selftest wr/wr2/wr3/wr4/wr5; .test missing-root case |
| ROBUST-4 | non-UTF-8 reported as L11 "unreadable", pair dropped, CRLF and BOM handled | L11 base and details not UTF-8; C: BOM, CRLF (a load_pieces level-0 line has no `\r`) |
| ROBUST-5, CONTRACT-11 | one fence mask (marker-matched ``` / ~~~) for every scan; an unterminated fence fails (L2 base, L3 details) | L2/L3 unterminated fence; C: fenced needs:, fenced heading, fence in a details field, `~~~` not closed by ``` |
| ROBUST-6 | exit codes stated in the header (0/1/2); --selftest refuses other options; --write-ratchet with --require-all refused; the --show/--list surface is gone | .test: --selftest --require-all rc 2 |
| ROBUST-7 | the selftest's write_ratchet prints nothing | out= lambda |
| ROBUST-8 | scratch_dir uses getpass.getuser() | (one line) |
| ROBUST-10 | header holds the readings (no lane report), `#!/usr/bin/env -S python3 -I`, `.test` and fixture listed in scripts/tests/NOTES.md | scripts/tests/NOTES.md |
| CHK-1 | L2 clause plants | L2 five-segment tag, malformed piece, malformed section, section grammar, section in another file, 4th segment C |
| CHK-2 | L1 duplicate section; L3 extra entry, absent details, malformed entry heading; L11 clauses split by a count of 2 | L1 "duplicate section tag"; L3 plants; L11 "base and details with no pieces" (count 2) |
| CHK-3 | L4 date presence/validity, slug kebab, `openfoo`, parked placement, record form, record absent, normalisation | L4 plants no date, impossible date, Lib_Trim, 'openfoo', parked, item without record, record file absent; C: doubled blanks |
| CHK-4 | L5 self-reference, multi-tag lists, skipped-pair excuse | L5 "needs: itself", "second tag of a list"; C: skipped pair (pilot) and its --require-all twin ({L5, L11}); C: comma list |
| CHK-6 | L7 boundaries and constants | C: 200-character statement, 40-line piece; L7 201 and 41; selftest asserts CAPS == {64K, 24K, 16K}, 200, 40 |
| CHK-7 | L8 two-of-three mode plants | L8 three plants naming two modes; heading-names-the-modes plant |
| CHK-8 | L9 kebab, `none`/`-` | L9 "slug not kebab"; C: `none` on two tags and `-` |
| CHK-9 | the CLI failure path | scripts/tests/pred_doc_lint.py.test: planted fault rc 1 and an `L4 file:line:` line, timeout, PCREC_TMPDIR; a `main` that always returns 0 fails it (gate rows) |
| ROBUST-9 | `.test` bounded by `timeout` and sets PCREC_TMPDIR | the .test |
| CHK-10, CONTRACT-14 | header states what `checked:` counts (visits); floors re-set to the sample's real counts; NOTED | header |
| CHK-11, CONTRACT-13, ROBUST-11 shared model, scratch_dir third copy | NOTED / PLAN as ruled (nothing built) | |

## THE MUTATION GATE

`python3 -I scripts/tests/pred_doc/mut.py` (committed; `-v` lists kills; ~20 s, 8 threads). It edits the lint's text one place at a time (old text must match exactly once), writes the copy beside the .test, the fixture and tmpdir.sh in a scratch tree and runs `scripts/tests/pred_doc_lint.py.test` there; killed = that test fails. It imports nothing from the lint. It carries the checks critic's mutants (mut.py, mut2.py) re-aimed at the new text, plus mutants for every new clause (fences, record titles, strict ratchet, CLI exit codes, the parser the reader calls).

Final result (`docs/dev/reviews/2026-11-19-r56-predlint/checks_harness/fix_lane_final_out.txt`): `mut: total 176, killed 160, equivalent 16, SURVIVED 0, NOMATCH 0`.
- Always-0 `main`: two rows ("CLI main always 0", "CLI main always 0 (whole)") plus "exit code on fails -> 0" and "fails not printed": all KILLED by the .test's CLI step.
- 16 equivalent, each named with its reason in EQUIVALENT: (1) L1 per-file tag uniqueness (a cross-file duplicate always also fails L2: tags carry their file word); (2) `review r\d+` removed (the bare `r\d+` alternative covers it); (3) write_ratchet ignoring the old value (it writes only after a clean lint, so count <= old); (4) 13 "ST ..." rows that weaken one assertion of the selftest that holds on the unmutated lint: a correct lint cannot turn them red, they are killed only in combination with a lint mutant, and each such lint mutant is a row above.

## THE ENTRY PROFILE

Routing row added to `scripts/entry` (docs/dev/doc_format.md updated): row 6a, before the slug row 6: a predicate-document tag `(core|lib|parked)/<seg>/<seg>[/<seg>]` reaches the `predicates` profile; row 6 now also matches a details `slugs:` word of a predicate piece (2+ hits exit 2). The shape is appended to `doc_profiles.KEY_SHAPES` (PL18 then forbids a plan [TAG] shaped like it, so a tag is always reachable; plan_lint selftest and `make -s test-plan-lint` pass). Profile: `form="pieces"`, name `predicates`, in `scripts/doc_profiles.py`; items are built by `pred_doc_lint.load_pieces(src.read)` (so `--rev` works and one parser serves both); an absent file contributes no item (pilot mode), so existing `entry -g` calls are unaffected. Level 0 = heading + statement, 1 = the base piece, 2 = + the details entry. `-g` searches the pieces (profile `predicates`, included in the default set); `--state open` lists open pieces (`entry -g . -p predicates --state open`); `--work` is not wired for it (no work states).

Sample (the committed fixture, via scripts/tests/entry_pieces.test; real tree has no predicate files on this branch):
- `entry core/holes/class -l 0` -> the heading line, the statement, `entry: 1 items (profile predicates, level 0)`, rc 0
- `entry shared-q -l 0` -> two pieces, rc 2; `entry no-such-slug` rc 1; `entry core/holes/nowhere` rc 1
- `entry -g . -p predicates --state open` -> `### Trimmed ...`, `entry: 1 items`

The lint's CLI now exposes only: `[--root DIR] [--require-all]`, `--write-ratchet`, `--selftest`. No `--show`/`--list`. Python API for the reader: `load_pieces(read)`, `piece_text(piece, entry, level)`.
Tests: `scripts/tests/entry_pieces.test` (13 checks), `entry --selftest` (75 checks, 0 failures), plan_lint selftest (45 plants, 0 failures).

## WHAT WAS NOT DONE

- The critic skill process changes named in main's rulings (`.claude/skills/pcrec-critic/SKILL.md`): not touched, nothing under `.claude/` edited; the predicate manager returns that item to main.
- Wiring into `make` (main's, after the gate): not done. docs/dev/pred/doc_format.md not edited (no conflict found between it and the code; the one item I read as unstated: a piece heading with a malformed date but valid status still reports the status check separately, which the text does not forbid).
- CONTRACT-13 (attribution of a status-less heading), the shared tagged-piece model, a shared scratch-dir helper: PLAN/NOTED per the rulings.
- `entry --work` for the predicates profile; premise test (2) and (3) not re-run (see STATE AT HANDOFF).
- No box-queue job, no suite, nothing pushed. Open reading: a title inside `(record: "...")` that itself contains `")` would be cut at the last one on the item (R1 as written).

## EVIDENCE AND COMMANDS

    bash scripts/tests/pred_doc_lint.py.test        -> selftest: 119 runs, 11 rules with a detected plant of 11, 0 failures; PASS
    python3 -I scripts/pred_doc_lint.py --root scripts/tests/pred_doc/root --require-all -> checked: L1=13 L2=13 L3=3 L4=13 ...; failed 0
    python3 -I scripts/tests/pred_doc/mut.py        -> mut: total 176, killed 160, equivalent 16, SURVIVED 0, NOMATCH 0
    bash scripts/tests/entry_pieces.test            -> PASS
    python3 -I scripts/entry --selftest             -> 75 checks, 0 failures
    make -s test-plan-lint                          -> checks failed: 0
    python3 -I scripts/entry --lint-scripts         -> 68 index lines, 0 failures
    bash scripts/check_claudemd_size.sh --staged    -> within limits
    bash scripts/tests/hooks.test                   -> no_cd_worktree selftest 40 passed
Review filed: docs/dev/reviews/2026-11-19-r56-predlint.md, directory 2026-11-19-r56-predlint/, index line in docs/dev/reviews/NOTES.md.
