# FAITH critic — docfmt
## Findings
### FAITH-1 — an addendum moved into the WRONG entry passes every converter check (CONFIRMED; answer/design; effort S-M; blast: every unnamed inline addendum, ~45)
Doc §2.2, §5 unit 1, §5.1(2), C6. Real case: `### D89 addendum` (decisions.md:6590) and its three continuations `**Addendum 2/3/4**` (6639, 6661, 6667) sit INSIDE D94. The continuations name no id, so the only rule a converter can apply is the enclosing entry. They then become D94.a2-a4. Tree cites prove the owner is D89: `D89 addendum 4` at src/parse/rxt_compose.c:117, src/gen/emit_vm.c:8679, tests/definitions/run_definitions_tests.sh:270,334, tests/rxtsource/run_rxtsource_tests.sh:4146.
Repro: mock of 17 real entries (faith/mock/orig.md), a converter written from the design text (faith/conv.py), the §5.1 control (faith/control.py) and C6 (faith/c6.py), all run with `python3 -I`. Output: `ids=ok census=ok multiset=ok`, and C6 flags no D94 line (D94.a1 is dated 09-16 and a2-a4 09-03; C6 checks numbers, not dates). Expected: a FAIL. The whole-file multiset cannot see lines that move between entries, and C6 is satisfied by construction because the converter wrote the heading inside the entry it chose.
Fix: (a) make the multiset per OWNER entry. (b) An owner table for every addendum label in the original (named ones from the heading; the ~45 unnamed ones ruled by hand once), kept as the control's input, written by someone other than the converter's author. (c) The tree-wide cite resolver of FAITH-2.

### FAITH-2 — G4's "every `Dn add. k` cite resolves, 0 renumbered" has NO check (CONFIRMED; answer; effort S; blast: 2,708 addendum cites)
Doc §0 G4, §2.4 C7/C8, §6 "Addendum renumbering". C7 resolves ids cited in INDEX lines only, and C8 is about file:line cites. Nothing compares an addendum's number before and after conversion.
Repro: in the converted mock, D163.a7..a12 renumbered to a8..a13 (faith/mock/out_shift.md). Result: `ids=ok census=ok multiset=ok`, and C6 is unchanged (the numbers still rise and are unique). The build tree holds 107 cites of `D163 add. 7-12` (grep `D163 add(endum|\.) ?(7|8|9|1[012])\b`). A swap that breaks the rising order (D94.a1<->a2) is caught by C6, but only by accident of order.
Fix: the control records, from the ORIGINAL, (id, old number or label, hash of the first body line) for every addendum and checks the converted mapping row by row. Add a tree-wide resolver: every `Dn add. k` / `Dn addendum k` / `Dn.ak` resolves to an existing `### Dn.ak` (G4's measurable form, made a check).

### FAITH-3 — "an addendum already numbered keeps its number" cannot be honoured for four real shapes; the design rules none (CONFIRMED; answer/design; effort S, ruling; blast: ~40 cites)
Doc §2.2 bullet 2, C6 ("numbers unique and rising"), `### ID.aN` grammar.
(1) A DUPLICATE number: `### D162 addendum 4` appears twice, at decisions.md:9579 ("kit KEEPS its own derived data") and 9801 ("provenance is the answering BLOCK's own declaration", inside D167). The tree holds 31 cites of `D162 add. 4` (e.g. src/core/findings.h:51,316 and tests/mech/sabotages/S1030_provenance_by_link.sh:5). Some cite one addendum, some the other.
(2) SUB-numbers: `Addendum 4.1` (D155, :9350) and `Addendum 1.1` (D166, :9743), both cited (`D155 add. 4.1` in window_contract.md:445,1645 and setfind.md; `D166 add. 1.1` in regime_eval.md and r17b_prime.md). An integer N cannot hold 4.1. My converter read it as a1.
(3) `### D168 addendum 3 note` twice (:9858, :9862; 5 cites): is a note an addendum, a3 again, or a new number?
(4) "In date order" is undefined for undated labels ("same day", "same exchange, 18:3x EDT": D89, D60, D150, D163.a1, D166).
C6 catches (1) and possibly (2) after the fact, but the converter must break either "keeps its number" or C6, and the design does not say which.
Fix: a declared rule in §2.2. Suggested: a collision keeps the first and gives the second the next free number with a `(was: "D162 addendum 4", second of two)` line; dotted numbers allowed (`D155.a4.1`) in the grammar and in C6; notes nest under their addendum. Plus a cite census of the affected labels, re-pointed by hand.

### FAITH-4 — §5.1's byte check as written fails on a CORRECT conversion, so its relaxation gets written by the converter's author (CONFIRMED; design; effort S; blast: the unit-1 control)
Doc §5.1(2): "the multiset of non-heading body lines is identical before and after". A correct conversion adds non-heading lines: §2.2 and §2.5 add `(was: "D26 addendum (owner, 2026-11-06)")` lines, and each inline bold label (`**Addendum (DOC-1, ...)**`, `**RULING-5 ADDENDUM**`) either becomes a heading or stays as a body line beneath a new heading.
Repro: faith/control.py `literal` mode on the correct-shape mock output: `multiset=FAIL`. Only the `relaxed` mode passes (it skips label and `(was:` lines). Learnings §3: whoever writes that relaxation decides which lines the control ignores. If that is the converter's author, the control and the thing it checks share one source.
Fix: state the exact exclusion set in the design: lines matching the §2.2 `(was: ...)` form plus, per FAITH-1(b), the label lines listed in the owner table. Better, make the multiset per owner entry (FAITH-1), which also catches moves.

### FAITH-5 — the mixed-file re-run double-converts inline-label addenda, and its control has no baseline (CONFIRMED in mock; answer; effort S; blast: every landing-time re-run of units 1-4)
Doc §5 ("the converter accepts a MIXED file"), §2.2 (body verbatim; the old label stays on its first line). Inline labels stay verbatim in the body (D47's `**RULING-5 ADDENDUM ...**`, D26's `**Addendum (DOC-1 ...)**`), so a re-run reads them again as unnumbered addenda.
Repro: `python3 -I faith/conv.py out_none.md rerun.md` gives NOT-IDEMPOTENT: D47 gains a5 and a6 (copies of a3 and a4). The census caught it in my mock only because the "original" counts were taken from the converted file with a different regex. §5.1's numbers (191 ids, the §1.1 census) are fixed at 6638e3679, and the landing re-run is on HEAD with more entries, so the design gives no independent baseline for the run that actually lands.
Fix: (a) acceptance test `convert(convert(x)) == convert(x)` on the real file. (b) The converter recognises an addendum as converted when a `### ID.aN` heading sits directly above it (state it in §2.2). (c) The re-run's control recomputes the ids, the census and the owner table from the old-form part of HEAD by the §5.1 route, and checks that the converted part is byte-identical to the previous run's output.

### FAITH-6 — the "17 misplaced addenda" acceptance number is the design author's own census, it undercounts, and C6 cannot run on the old grammar (CONFIRMED; doc/maintenance; effort XS)
Doc §0 G2, §1.1, §5 unit 1 ("C6 finds 0 addenda outside their entry (17 before)"). My census (faith/census.py, `python3 -I`) finds 21 NAMED addenda outside their entry: the 17 `###` ones, plus `## D47 ADDENDUM`/`SECOND` after D48 (:4208, :4256) and `## D58 ADDENDUM` in D96 (:6832) and in D154 (:9283). It also finds 3 UNNAMED ones that no census counts (D89's Addendum 2-4 inside D94, FAITH-1). The two D58 top-level cases are not mentioned anywhere in the design. C6 reads only `### ID.aN`, so "17 before" cannot come from C6. It is the writer's number, and the control shares its source (K35: a population nobody counts).
Fix: the census becomes a committed list (line, label, owner), produced by its own script, which the unit-1 control reads. Count 24 (21 named + 3 unnamed), not 17.

### FAITH-7 — a statement that is faithful to its OWN entry but blind to a later entry's override passes every check (CONFIRMED by reading; answer; effort M; blast: every cross-entry supersession, at least 6 marked, unknown unmarked)
Doc §5 "Faithfulness" (critic "reads each details entry and its statement"), §6 "read `scripts/entry` before quoting". Real cases:
- D49 (decisions.md:4299, 4312) "SUPERSEDES D42.3's collapse". D42's own text (:3661) never mentions D49.
- Line 3202 "supersedes D33". D33's text has 0 mentions of it.
- Line 2968 supersedes D32. Line 9383 (inside D157) "amends D155".
Plant: `- D42 m4-engine-contract live — M4 engine contract: captures default ON; ...; an engine error collapses to −1.` The writer reads only D42, and the fresh critic reads only D42 plus this statement. All four questions answer "no", so it passes, though the state should be `part>D49` and the −1 rule should be gone. a<k> does not apply (no addendum). The §6 rule does not help either: `scripts/entry D42` prints D42 only. Writer and critic read the same single entry, so the check has no independent source.
Fix: before each statement batch, a mechanical pass lists for each id every LATER entry that cites it (`Dn` or `Dn.k` tokens in other entries' bodies, plus the supersedes/replaces/reverses/amends verbs). The writer and the critic both get that list, and the critic gets a fifth question: "does any listed later entry change this ruling? Then the state and the statement must show it." Optionally the accessor's level 1 prints "cited later by: D49".

### FAITH-8 — the critic's four questions leave the STATE field, a too-large `(+n)`, and keywords unchecked (CONFIRMED by reading; answer; effort XS; blast: every index line)
Doc §5 (the four questions), §2.1 (state, `(+n more)`, keywords), §7 answer 1 ("`(+n more)` right"). The questions cover add, contradict, replaced rule, and omit-uncounted. None of them asks:
(a) whether the state is right. Plants: `D33 ... live` (truly sup or part, FAITH-7); `D47 ... sup>D49` (D49 only cites D47's rider).
(b) whether n is too LARGE. Plant: D47 `(+5 more)` when 3 rulings are left out. "Omit without counting" catches only a count that is too small, yet answer 1 asks for n to be RIGHT.
(c) whether a keyword is false. Plant: D47 `{per-quantifier K}`. That is the rule D47.a1 rejected, and a `-g` recall then lands on it.
No linter rule (C1-C10) reads meaning, and C7 only checks that `D49` in `sup>D49` exists.
Fix: add three questions: the state is right (with FAITH-7's later-entry list); n EQUALS the number of rulings left out; every keyword is true of the current ruling.

### FAITH-9 — the `a<k>` check shares its source with the converter (CONFIRMED by reading; design; effort XS)
Doc §2.1 a<k>, §6 mitigation 1. The linter checks that k equals the count of `### ID.aN` headings, and both come from the converter's output. It catches a writer's mistyped k and forces a touch at a new addendum, as designed. It cannot catch a MISATTRIBUTED addendum. In the FAITH-1 mock, D94 shows a5 and D89 a1, both "correct" to the linter, against a truth of a2 and a4. §6 lists a<k> as the drift mitigation, but it controls only the writer's arithmetic.
Fix: none needed for a<k> itself. The independent owner table of FAITH-1(b) is what covers attribution. Say in §5.1 that a<k> is not a faithfulness control.

## PROBED-AND-HELD
Statement plants: one wrong index line per row. "Indep" says whether the catching check has a source independent of the writer.

| # | entry | plant (wrong in one way) | caught by | indep |
|---|---|---|---|---|
| S1 | D47 | `... counter-K; K is one named constant (8).` (the work-bound ruling dropped, no `(+n)`) | §5 critic Q4 | yes (fresh reader of details) |
| S2 | D47 | `... K may vary per quantifier` (a rule D47.a1 replaced) | §5 critic Q3, but only if D47 ADDENDUM is inside D47. Named top-level headings are guaranteed there by C2 (a stray `## D47` duplicates the id) and by C6 | yes |
| S3 | D26 | `matching is exact for the base tier only` (scope narrowed) | §5 critic Q1/Q2 | yes |
| S4 | D26 | `follow PCRE2 even where PCRE2 has a bug` (inverts a2) | §5 critic Q2/Q3 | yes |
| S5 | D163 | `parts are chosen at run time` (a rule the details do not make) | §5 critic Q1 | yes |
| S6 | D163 | `every exported entry shares one controller` (contradicts a12) | §5 critic Q2 | yes |
| S7 | D94 | statement from D94's own 09-01 text only, `a2` (misses the "run the suites" addendum filed in D112) | C6 + a<k> once the converter moves it in; the critic then sees it | yes for the move (named heading) |
| S8 | D94 | after the naive conversion, folds D89's call-syntax rulings (`(?&*=name)`) into D94 | NOTHING (FAITH-1) | — |
| S9 | D89 | `a1`, no `(+n)`; faithful to what the converter left (the flat-import spelling is missing) | NOTHING (FAITH-1) | — |
| S10 | D42 | `live`, keeps the −1 collapse (D49 supersedes it) | NOTHING (FAITH-7) | no: writer and critic read the same entry |
| S11 | D33 | `live` (superseded at :3202) | NOTHING (FAITH-7/8a) | — |
| S12 | D162 | `a4` when the details hold 5 headings | a<k> linter | no (shares the converter's source, FAITH-9), but adequate for this typo |
| S13 | D47 | `(+5 more)` when 3 are left out | NOTHING (FAITH-8b) | — |
| S14 | D47 | `{per-quantifier K}` keyword | NOTHING (FAITH-8c) | — |
| S15 | any | `?` replaced by the old title, state left `live` | `?` ratchet: no (the count fell). Critic: yes when the title states the first ruling, not the current one (D47's title names no rule, so Q4 fires) | yes |

Converter plants (mock, `python3 -I`, 17 real entries, 1,1xx lines):

| plant | §5.1 ids | census | multiset (relaxed) | C6 | caught? |
|---|---|---|---|---|---|
| D89 add. 2-4 attributed to D94 (enclosure) | ok | ok | ok | ok | NO (FAITH-1) |
| D163 a7-a12 shifted +1 | ok | ok | ok | ok | NO (FAITH-2) |
| D94 a1<->a2 swapped | ok | ok | ok | FAIL | yes, by order accident |
| line duplicated in one entry, same line dropped in another | ok | ok | ok | ok | NO, but only for identical lines. Across the real file just 2 non-blank lines over 20 chars occur in two entries (D32/D33, D161/D162), so a dup/drop of DIFFERENT lines is caught by the multiset (HELD) |
| misplaced addendum left outside (`### D47.a1` inside D48) | ok | ok | ok | FAIL | yes (C6). Left as `## D47 ADDENDUM`: C2/C10 fail. HELD |
| mixed re-run double-converts | ok | FAIL* | ok | ok | *only with a census recomputed from the converted file (FAITH-5) |
| D162 duplicate add. 4 | ok | ok | ok | FAIL | yes, but the design has no rule for the resolution (FAITH-3) |
| provisional `?` survives forever | — | — | — | — | the ratchet refuses only an increase; `--stale` reports the count, nothing forces it to 0 (no unit gate says "0 `?` after 1.S8"). SUSPECTED gap, minor: add 0 `?` as 1.S8's acceptance |
| an id dropped or duplicated | FAIL | — | FAIL | — | yes (HELD) |

HELD: the critic's four questions catch add, contradict, replaced and omit-uncounted for S1-S6 (6 of 6 in-entry meaning plants), and that check is independent: a fresh opus reads the details, never the writer's reasoning. C2/C6 hold for NAMED misplaced addenda (21 of 21 move correctly in my converter and would FAIL C6 if left out). Distinct ids hold (17/17 in the mock).
