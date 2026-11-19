# CRITIC checks: predlint (r56)



## Method
Harness /var/tmp/pcrec-pcrec/scratch/crit-predlint/checks/h/mut.py and mut2.py (mutant = one exact-string substitution in a copy of
SUBJECT's pred_doc_lint.py; each run = `--selftest` plus `--root <sample> --require-all`, i.e. exactly scripts/tests/pred_doc_lint.py.test's
two steps). Full tables: h/out.txt (103 mutants) and h/out2.txt (27 mutants). Baseline: selftest 22 runs, 11/11; sample passed 120 failed 0.
"GREEN/GREEN" = the committed check (.test) would PASS with the clause broken. Every sample-red mutant was also selftest-red (the sample step
adds nothing the selftest's last `expect` does not already cover, except the CLI path, see CHK-9).
Mutants killed (selftest red): about 66 of ~100 rule mutants. The ones below SURVIVED. Mutant numbers are in out.txt (A) or out2.txt (B).

## Findings

### CHK-1  (silent-pass, maintenance; CONFIRMED by mutation) L2: three of its clauses can be deleted, selftest GREEN
Mutants A2 (malformed PIECE heading no longer fails, line 258), A4 (tag's file word must equal the file, line 264), A6 (section tag
must be `<file>/<kebab>`, line 234), A7 (malformed SECTION heading fails, line 231), A9 (4th path segment `/sub` of the grammar, line 48):
all selftest GREEN and sample GREEN. The L2 plants are only "upper case in a tag" and "tag path differs from its section"; the other
clauses of doc_format.md L2 ("tag grammar, and the tag's path equals the piece's file and section") have no plant. A9: no fixture tag has a
`/sub` segment, so the optional group is never exercised in either direction.
Fix: plants (malformed `### x` heading; `lib/..` tag in the core file; section `## X [core/Bad_Name]`; a `## Foo` section with no tag) and
one passing 4-segment tag in the sample. Effort: small. Blast radius: the lint's L2 accepts malformed headings once the clause rots.
file: scripts/pred_doc_lint.py:229-268, plants 649-671.

### CHK-2  (silent-pass; CONFIRMED) L1 duplicate SECTION tag, L3 two clauses, L11 both clauses
A1 (L1 duplicate section tag, line 239) GREEN/GREEN: only the piece-tag duplicate is planted.
A11 (L3 "details entry has no base piece", line 342) GREEN/GREEN, A13 (details file absent, line 330) GREEN/GREEN, A14 (malformed details
entry heading, line 333) GREEN/GREEN: the only L3 plants are "base piece without entry" and "order".
A82 and A83 (L11: "base file no pieces" line 320 and "details file no entries" line 322, each deleted ALONE) GREEN/GREEN: the one L11
plant empties base and details of the same file together, so either fail line alone satisfies "detected by exactly L11". Each clause
could be deleted with the selftest passing. Fix: split p_empty_file in two (base only, details only); add plants for the other L3/L1 clauses.
Effort: small.

### CHK-3  (silent-pass; CONFIRMED) L4: nine clause mutants survive
A15 (no status date), A16 (bad date like 2026-13-45), A18 (open: slug must be kebab; `open Bad_Slug`), A19 (open: needs the space, `openfoo`),
A21 (`parked` status only in the parked file), A23 (rulings item without `(record: "...")`), A24 (record file absent => fail), A26 (record
title whitespace normalisation) all GREEN/GREEN. Plants cover only: status outside set, `open` with no slug, ruled without rulings,
title not in record. Note A17 (drop the whole open check) IS killed, but only because of the one plant "open 2026-11-04"; its two halves are
independently deletable. B0 (`rstrip(".")` of titles, the `**Title.**` form) also survives, because the sample's bold title is
`**2026-11-02 bold words (Frank: "pad it").**` and the ` (` split masks it. Effort: small each (one plant per clause).
file: scripts/pred_doc_lint.py:278-293, 350-371.

### CHK-4  (silent-pass; CONFIRMED) L5: off-by-one and skipped-pair excuse untested
A32 (`tn >= own[1]` -> `>`: a piece needing ITSELF is accepted, line 394) GREEN/GREEN: the plant has a target LATER in the file, never the
same piece. A33 and A34 (the "its pair was skipped: unresolvable, not a fault" excuse, line 383-384, removed or applied also under
--require-all) GREEN/GREEN: the only skip case in the selftest (the "skip" control) deletes the parked pair, which no `needs:`/`by:` points
at, so the excuse's body is never reached in either direction. Also B7/B8 (needs: split on whitespace only; only first tag kept, lines
135-137) GREEN/GREEN: every fixture `needs:`/`by:` line holds exactly ONE tag, so the multi-tag and comma forms of the format
("needs: <tag> ...") are never exercised; the lint could check only the first tag of a list.
Fix: plant `needs: <own tag>`; a skip control where a core piece needs a lib tag with lib deleted; a two-tag `needs:` line (one bad) as a plant
and a comma list as a passing case.

### CHK-5  (silent-pass; CONFIRMED) L6: four of six history words untested; partial scans survive
A37 (REVERSED), A38 (SUPERSEDED), A39 (`[REV`), A40 (`review rN`) removed from HIST_RE: GREEN/GREEN. Plants use only `WITHDRAWN` and `Rev 29`
(A36 and A41 killed). doc_format.md's "word list above" includes reversed/withdrawn/review ids/`[REV`. Also B17 (L6 scans only the first 30
lines of each base file) and B18 (skips the last 2 lines) GREEN/GREEN: the sample's L6 count is 49, the hand floor is 30 (line 699), so a
loop that stops early passes the floor. A single table-driven plant (one line per word, each must fire) would do. Effort: small.

### CHK-6  (silent-pass; CONFIRMED) L7: neither limit is tested at its boundary; soft cap defaults never run
A45 (piece cap 40->41), A46 (40->39), A48 (statement cap 200->199) and A49 (line count off by one: `p["end"]-p["line"]` for `+1`) all
GREEN/GREEN. The plants are 201 characters and a 43+ line piece, far above both limits, and no fixture sits AT 200 chars or AT 40 lines
(the passing side). The spec says "statement 200 characters and piece 40 lines HARD"; whether 40 passes is untested, so an off-by-one in
either direction is invisible (A47, 200->201, is killed only because the plant is exactly 201). A50/A51 (`no statement line` fail, line 302)
GREEN/GREEN: a non-`?` piece with no statement is accepted. A53/A54/A55: the SOFT caps CAPS = core 64K, lib 24K, parked 16K can each be
changed to 1K and everything stays green: the "soft" control passes its own `caps=` override and tests only the core word; the real constants
(spec: 64 KB, 24 KB, 16 KB) are never compared with anything. Fix: boundary pairs (200 ok / 201 bad; 40 ok / 41 bad), a no-statement plant,
and one assertion `CAPS == {...}` written from the doc. Effort: small.

### CHK-7  (silent-pass; CONFIRMED) L8: two of three mode names untested
A64 (drop FIND-ALL from the required names) and A65 (drop SEARCHED) GREEN/GREEN: the plant is "Example: WHOLE only." (one name). Spec: "an
example line names the three modes". A line naming WHOLE and SEARCHED but not FIND-ALL passes if the check is weakened. (Exemptions held:
`?`, parked, under-construction, principles each killed their mutant, A58-A62 red; `all`->`any` A63 red.) Fix: plants naming two of three.

### CHK-8  (silent-pass; CONFIRMED) L9: kebab check and the "none"/"-" skip untested
A68 (slug must be lower-case kebab, line 412) and A72 (the `none` / `-` placeholders are skipped, line 408) GREEN/GREEN; B16 (same tag
listing a slug twice counts as two tags) GREEN/GREEN though irrelevant to a real fault. A68 means a slug like `Hole_Class` passes. Effort: small.

### CHK-9  (silent-pass; CONFIRMED) the CLI failure path is never run by the check
B24 (`return 1 if rep.fails else 0` -> `return 0` in main, line 818) and B25 (the failing lines not printed in `report`, line 459) are
GREEN/GREEN. The .test wrapper runs the CLI only on the CLEAN sample (`|| FAIL` is reached only on non-zero), and every plant goes through
`lint()` in-process. So the lint's actual exit code on a faulty tree and the `RULE file:line: msg` output format (the contract of header
lines 12-14) are unverified; a lint that exits 0 on every fault passes `.test`. Fix: one plant run through a subprocess asserting rc 1 and a
`L5 ` prefixed line. Related and minor (A85): `--root` pointing at an empty dir without --require-all prints a note and exits 0 ("nothing linted").

### CHK-10  (maintenance; CONFIRMED) selftest's own machinery: verified, with caveats
- "exactly its rule" is REAL: `got == {rule}` (line 711). The mutants that weaken it (A87 `rule in got`, A88 `if got`) are GREEN only because
  no CURRENT plant trips a second rule, i.e. nothing in the suite would notice if exactness were weakened. Same for the 12 positive controls
  and the clean-fixture control, floors, covered-check (A89-A102): each, deleted alone, is GREEN by construction (they only matter when a
  rule is wrong). I paired them: breaking a rule so it fires on clean input (A27, A35, A44, A58, A66, A70, A71, A75, B19, B20, B26) IS
  caught by the clean-fixture control; so that control works. Not a defect; recorded to stop a repeat of this question.
- "11 of 11" (line 790) = `len(covered)` / `len(RULES)`. `covered` comes from the PLANTS tuple list (hand-written) and RULES is a separate
  constant, but RULES is ALSO what builds `Rep.checked`, so adding a rule means editing RULES and PLANTS in the same file as the lint; only
  the hand `floors` dict is a third list. Deleting L11 from RULES, PLANTS and floors in one edit leaves "10 of 10". Acceptable, low.
- `Rep.checked` counts VISITS, incremented before the check runs (e.g. `rep.ok("L6")` line 250, `rep.ok("L8")` line 308): a mutant that
  disables the check keeps the same count (all "fail off" mutants kept their counts). So a printed `checked: L6=49` proves a line was visited,
  not that the word list works; the `checked:` line cannot witness check strength (see learnings §3: a control sharing a source with what it
  controls). The floors (line 699) are loose against actual counts: L6 30/49, L4 9/13, L1 9/13, L9 4/7, so B17/B18 pass.

### CHK-11  (design; CONFIRMED) the sample step of .test is redundant with the selftest
No mutant was caught by the sample run (step 2) that the selftest (step 1) missed: all sample-red mutants were also selftest-red (selftest's
last `expect` lints the same directory). Step 2 adds only argv parsing, `--require-all` wiring and exit code 0 on clean. Not a defect, but the
second step does not buy "checks the lint on a second population"; its real value would be CHK-9's failing-direction subprocess run.

## Population (part 2)
Sample `checked:` L1=13 L2=13 L3=3 L4=13 L5=4 L6=49 L7=9 L8=3 L9=7 L10=3 L11=3. Nothing is ZERO, but trivially small:
- L3=3, L10=3, L11=3: one per file-pair, with exactly 3 entries per file; so order is tested only on 3-element lists (parked file: 2 entries swapped).
- L5=4: two `needs:` and two `by:`, all single-tag; one cross-file needs (lib->core, the passing later-file direction), one same-file earlier.
  No tag with a missing-pair target, no self reference, no list.
- L8=3: exactly one line carrying the three-mode form (lib/names/trimmed `WHOLE: t; SEARCHED: t; FIND-ALL: t.`), two `modes: n/a`. The
  principle piece (exempt) and the `?`/parked pieces carry the exemptions; exemptions ARE exercised in the passing direction, in the sample
  itself (A58 `?` exemption red on sample) and by selftest controls (parked, under-construction, principles).
- L4 rulings: 2 items, 2 ruled pieces, record titles: one `###` form and one `**..**` form (both killed, B1-B3). The `open <slug>` form: 1 piece.
- L9: 7 slugs, ONE shared slug on three tags (killed: A69, A70, A71). Passing direction of `shared:` present. OK.
- L10: ratchet at EQUALITY (core 1 vs 1 '?') is in the sample (A75 `>=` red). Held.
- NOT in the sample in any direction: `was:` (only a selftest control), fenced code in a base file (only a selftest control), a 4-segment tag,
  multi-tag needs/by, comma lists, a piece exactly at a cap, a base file near a soft cap, bad dates, `--list`/`--show` of anything but
  the fixtures (reader is covered by 7 hand-written expectations; mutants B21-B23 killed).

## PROBED-AND-HELD
- Killed by selftest (red): L1 dup tag; L2 TAG_RE, section membership, `was:` excuse; L3 missing entry, order; L4 open-slug (whole), status
  set, ruled-no-rulings, title not found; L5 names-no-piece, by-not-principle, later file, later in file; L6 WITHDRAWN, `rev N`, case flag, fence
  exemption; L7 statement 201, soft-cap warning present, soft cap not hard; L8 fail, all four exemptions, all->any; L9 shared-exempt always /
  never / cross-file / tags>2; L10 fail off, equality, slack, qcount, absent-note, per-word lookup, write_ratchet max/ignore-old; L11 require-all
  absent, `checked` count; reader ambiguity, list status, level 2; record-title parsing (3 forms). About 66 of 103 + 14 of 27 killed.
- Clean-fixture control reacts to false positives (11 mutants). Selftest `got == {rule}` is genuine.
- L10 ratchet only shrinks (A80, A81 killed), at equality passes.
CRITIC COMPLETE
