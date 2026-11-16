# Lane absfix: review r28's rulings applied to joint_condition.md (§4H)

Lane absfix (opus), 2026-11-16, branch `lane/absfix` cut from main 6f480b35b. Design text only: the note
`docs/design/joint_condition.md` (new §4H plus in-place "[§4H]" tags) and the evidence script
`docs/dev/lanes/absfix_check.py` / `.out`. No file under src/, cli/, lib/, memfn/ or tests/ was touched;
`predicates_draft.md` (rev 19, the client) was not edited.

Every count below comes from ONE command, run from the worktree root:
`timeout 300 python3 -I docs/dev/lanes/absfix_check.py` (under 1 s; libpcre2-8 10.46, Python 3.14.4), whose output
is the committed `docs/dev/lanes/absfix_check.out`. Each count names its `.out` block in brackets. Total: 14,014
engine-run cases, 0 differ, 0 engine disagreements, 58,976 probes; (GF) 233,574 comparisons, 0 differ. Sabotage:
`ABSFIX_SABOTAGE=1 timeout 300 python3 -I docs/dev/lanes/absfix_check.py` makes VALUES read the group's text; the
two-spellings drill then splits under VALUES (5 of 310 per pair), so the check can fail. Premise test passed before any
edit: `git log -1` printed 6f480b35b, and `timeout 300 python3 -I docs/dev/lanes/absfold_check.py` reproduced
absfold_check.out byte for byte (its (AR) and (ZE) lines included).

## STATE AT HANDOFF

- STATE: done. Branch `lane/absfix`; the tip is the commit that carries this report (named in the handback).
- Rulings file: R1, R2 and R3 applied. The last entry applied is R3 (15:29: the principle's wording, with an asterisk).
  - R1: optional-as-loop ANSWERED, stated as a ruling.
  - R2: mark-domain ANSWERED as a principle. The domain is VALUES (the manager's reading), and the computability
    table was added.
- OWED: none (no box-queue jobs; the script is light and was run directly).
- The note cites the three 15:2x COND-FAMILY entries on MAIN (CF:1696-1720 there). This branch's copy of
  COND-FAMILY.md was cut at 6f480b35b and ends at CF:1694, before them. The merge brings them together.

## DISPOSITIONS APPLIED

One line per item, with line numbers in the revised note. Every item is done. There is no STOP: neither C's nor K's
stop condition fired.
- A, MARK-DOMAIN. Done, then superseded by R2: the domain is stated ONCE as DOM(h) = the values h can take in some
  match (the manager's reading of the owner's 15:27 principle). Sites:
  - §4H.1 (:1995-2075);
  - (AR) :1798; the F1 sentence :1802;
  - §4G.4 corner 2 :1873; §4G.6 (3) :1918-1921, (8) :1954;
  - §4B.6 :1423; §8 PARKED :2441; §8 item 3 :2500;
  - §9 rows 55 :2613, 64 :2622, 65 (f) :2623.
  - All three candidates were still run as evidence (THE THREE DOMAINS RUN).
- B, (AR) RECORD CELL. Done: one cell, F1, for one label, record and joint alike (:1798; row 55 :2613).
- C, `all(c)`. Done: `all(c)` := c with every label marked, read F1 (§4H.3 :2097-2113).
  - (6)'s parenthesis and the (LI) count corrected (:1943). The L36 boundary corrected in D23 :1578, row 58 :2616
    and §4G.6 (6).
  - Row 56 :2614. 14:50 (a)'s one-line form restated (§4H.3, §4H.7).
  - The vacuous `al0` was replaced by the definition, and the counts were re-run.
  - STOP conditions checked, neither met: record = `&` under `all` 0 of 1,110; the `?`/`*` split 0 of 11 groups
    [(ALL)].
- D, `?` AS A LOOP. Done, then superseded by R1: stated as RULED 15:23 with the manager's reading of how (§4H.5
  :2130-2156). Sites: J7 :219, item 5 :479 and :503, §3 errors row, §6 B4, §8 item 6, row 67. The both-readings run
  is kept as evidence.
- E, THE MARK INSIDE `some`/`count`. Done: COUNTED by F1, 14:50 (d) WITHDRAWN, and 14:31's "not counted" superseded.
  - Sites: §4H.4 :2115-2128; row 56; row 65 (g); §8 item 4; §4G.6 (4) :1928; §4B.7 :1446; §3 group-questions row.
  - 14:50 (f) restated: `occurs.none(((h, m?): !R))` gives 0 of 259 under each domain. Its dependence on the domain
    is stated in one line.
  - No diagnostic row.
- F, THE 14:50 READINGS. Done.
  - The map is §4H.7 :2176-2185. It covers RULING-3..7 and CHANGETAB-5 with (a), (c), (d), (f) moved.
  - RULING-4: zero-pass-empty is "the manager's reading, told 14:50", kept on the owner's list. Sites: header :13,
    §4G.4 corner 1 :1872, §8 item 3, rows 44 and 65 (f).
  - (e) is glossed against point (2) in §4H.2 and row 55.
- G, NEGATION OVER A MARKED LABEL. Done.
  - "Unmarked" added at item 3 :409, item 8 :595, D8 and §4G.3 :1858.
  - New look-alike row :596, DIFFERENT: BY DESIGN, with the answer under each domain candidate.
  - Row 61 is scoped to zero passes (:2619). §4H.8 :2187-2197.
- H, UNTAGGED SUPERSEDED SENTENCES.
  - Done: §9 rows 14 :2572 and 28 :2586, both moved off J7's zero-pass sentence. Caveat (6) of row 28 restated.
  - Tag pass done at each site H names:
    - item 3 (:403-411); §4A (the O28 sentence); §7 items 4 :2339 and 14;
    - §4B.2 :1318; D14 :1569;
    - §4E change log, its table note :1642, and "no wording contradicts" :1682;
    - §2 N1-N6 :283; §3 "Read" :303; item 8 census :607.
- I, §9 GAPS AND CITES. Done.
  - CHANGETAB-1: rows 57 and 63. CHANGETAB-2: new row 69 :2627. CHANGETAB-3: new row 70 and row 2. CHANGETAB-4:
    row 28.
  - CHANGETAB-6: cites widened or marked in rows 56, 57, 62, 45, 54. CHANGETAB-7: row 8 and new row 71.
    CHANGETAB-8: row 63.
- J, SMALL TEXT ERRORS. Done.
  - (UP) witness `''` (:1844). "55-68" (:1865), plus the places missing from §4G.3 (:1866).
  - §4G.5 marks the bound and `list_of` as the lane's, and names LEAVES' fourth item (:1885).
  - Row 55's STATUS quotes REVERSES whole.
- K, THE GENERAL FORM. Done: the re-run gives 0 differ (GENERAL FORM RE-RUN), so the rule is STATED in that form
  (§4H.6 :2158-2174; new row 73 :2631; §7 item 18 :2383). No new spelling. The merged warning is NOTED only (row 72
  (e)).
- L, GOALS. Done.
  - Goals pointer :75. §4H.9 :2199-2211 lists the owner's criteria, UNRANKED: "simplifying semantics", "saving people
    from themselves", the 13:52 principle, and (R2) the 15:27 principle with its provisional wording (*) (R3).

## THE THREE DOMAINS RUN

The candidates:
- ANY: any text.
- GROUP: the texts the group can match, read from its own text.
- VALUES: the values the label can take in some match, computed by RUNNING the pattern.

All three were run over the same populations [(DOM-AR) .. (DOM-SET), (DOM-SUMMARY)].

| candidate | (i) a never-holdable value witnesses an answer | (ii) splits two spellings of one pattern | (iii) splits two spellings of one set | (iv) record = `&` |
|---|---|---|---|---|
| ANY | YES, 112 answers in 7 tables | no (0) | no (0); two DIFFERENT sets that agree on every holdable value, `(h?: <0)` / `(h?: !(<10))`, part on 10 of 1,110 | kept (0) |
| GROUP | YES, 5 (the lookbehind spelling) | YES, 10 (5 of 310 per pair) | no (0) | kept (0) |
| VALUES | no (0) | no (0) | no (0) | kept (0) |

The drills:
- Complement drill, `t2 & ((h, m?): !office)` on `10`: ANY HOLDS (m = `x`), GROUP and VALUES FAIL. ANY and GROUP
  differ on 9 of 11,110 (`9`..`16`, `09`). [(DOM-TM2)]
- `((h, m?): R)` and `((h, m?): !R)` both hold: ANY 92 of 11,110, GROUP 2, VALUES 2 (`9`, `09`). [(DOM-TM2)]
- Two-spellings drill: P1 `(?:;(?<h>\d)(?<=[0-4]))*`, P2 `(?:;(?<h>[0-4]))*` and P3 `(?:;(?=[0-4])(?<h>\d))*` give
  the same match and the same captures on all 1,110 subjects. Under `(h?: 5..9, k: 3..7)`, the zero-pass subjects
  that HOLD:
  - ANY: 5, 5, 5.
  - GROUP: 5, 0, 5 (P1 and P3 vs P2 split on 5 of 310 each, smallest `3`).
  - VALUES: 0, 0, 0. [(DOM-2SP)]
- Where the candidates agree, they agree everywhere checked: (TM2) `((h, m?): R)` 0 differ; (RZ) `<5` and `5..9` 0;
  (ZJ) every set except `(("x", 3) | (0, 5))` on `3` (ANY HOLDS); (ZE) C1 and C2 0. [(DOM-*)]
- R2 (3) STOP check: VALUES splits neither equal spellings nor equal sets on any population run. No STOP.

R2 (4): where VALUES is not read off the group's text. Each case was RUN by enumeration in PCRE2 [(DOM-COMP)]. What the
compiler does in each case is not decided here; it is open for rev 20 (row 72).

| construct | example | VALUES (run) | the lane's classification |
|---|---|---|---|
| lookaround | `/(?<h>\d)(?<=[0-4])/` | `0`..`4` (text `\d`) | regular, by intersection |
| atomic / possessive | `/(?<h>\d++)5\|x/` | EMPTY (text `\d++`) | regular in the case run |
| conditional on another label | `/(?<a>x)?(?<h>(?(a)[0-4]\|[5-9]))/` | both branches over the pattern, one per match | regular; per match it depends on a |
| backreference | `/(?<h>(?<a>a+)b\k<a>)/` | a^n b a^n (checked to length 7) | NOT regular |
| recursion | `/(?<h>\((?:x\|(?&h))*\))/` | balanced parentheses (checked to length 6) | context-free |
| CONTEXT (a reading, not a limit) | branch reset `/(?\|(?<k>a)(?:;(?<h>\d))*\|(?<k>b)(?:;(?<h>[5-9]))*)/` | `0`..`9` over the pattern; `5`..`9` given k = `b`; `(h?: <5)` on `b`: HOLDS vs FAILS | both readings follow behaviour; the principle does not choose |

Not run: subroutine calls without recursion, and backtracking-control verbs (`(*COMMIT)`, `(*ACCEPT)`), which change
which matches exist.

## OPTIONAL AS LOOP RUN

Answered by the owner during the lane (R1, CF 15:23). The run is kept as evidence only [(LOOP)].
- (OP), 259 lists. These forms differ on 0 of 259 between "`?` a loop" and "not a loop": the plain record, `(h?, m?)`,
  `(h?, m = 0)`, `(h, m = 0)`, `all(...)` by C, and `occurs.none(((h, m?): !R))`.
- The withdrawn `all` readings A2v / A2z vs the wanted answers: 0 / 0 when `?` is not a loop, 36 / 11 (`3,`) when it
  is. This reproduces SIMULATE-4.
- Sibling drill, `/(?<k>\d)?-(?<h>\d)?/` vs `/(?:(?<k>\d)|)-(?:(?<h>\d)|)/` with `(h: <5, k?: 3..7)`:
  - Not a loop: 0 of 121 differ, and record vs `&` 0 of 121.
  - A loop: the first is the sibling-loop compile error on all 121, while the second answers.
- `/(?:(?<a>\d)?-(?<b>\d)?,)*/ & (a?: <5, b?: 3..7)`, 43 lists: answers when `?` is not a loop (engine-run), the
  sibling error on all 43 when it is.

## GENERAL FORM RE-RUN

The form is "an absent label has a candidate set D: unmarked {}, `h = v` {v}, `h?` DOM(h)". It was written without
`part()`/`tup()` and compared with absfold's `cond()` [(GF)].
- (AR): 4 kinds x 4 controls x 3 shapes. (TM2): 11,110 x 3. (ZJ): 10 x 4 sets x 2. (ZE): 11,100 x 2 x 2.
- Each under ANY, GROUP and VALUES: 233,574 comparisons, differ 0.
- The two programs share subjects and absence kinds, so this agreement is close to definitional. The independent
  controls are the engine-run regexes: 14,014 cases, 0 differ.
- Disposition K's condition is met, and the note states the rule in this form (§4H.6, row 73).

## QUESTION DRAFTS

- optional-as-loop: ANSWERED, R1 (CF 15:23, "I agree both spellings should answer alike"). The draft was dropped as
  the ruling instructs.
- mark-domain: ANSWERED, R2 (CF 15:27, a principle). The wording is provisional, "two patterns that match the same
  subjects and set their labels the same way answer every condition alike" (*) (R3, CF 15:29).

  What remains open is computability: in plain words, for the owner if the manager puts it.

  The mark lets a missing field pass when "some value would do". We now take "some value" to mean a value the field
  can really hold in some match of the pattern. For most patterns that set is easy to work out. Three cases are
  harder:
  - Lookarounds, atomic groups and conditionals change it from what the group's own text says, but it can still be
    computed exactly.
  - Backreferences make it a set no finite automaton describes. Example: `/(?<h>(?<a>a+)b\k<a>)/` gives h the values
    `aba`, `aabaa`, ...
  - Recursion makes it context-free.

  Rev 20 must say what the compiler does in those cases. Under the manager's reading, an approximation must never
  change an answer silently. Nothing is decided here.

  A second, smaller point: "some match of the pattern" could mean ANY match, or a match that agrees with the labels
  this match already set. On `/(?|(?<k>a)(?:;(?<h>\d))*|(?<k>b)(?:;(?<h>[5-9]))*)/ & (h?: <5)`, the subject `b` HOLDS
  under the first reading (h = 0 occurs only with k = a) and FAILS under the second. Both readings follow the pattern's
  behaviour, not its spelling, so the principle does not choose between them.

## LEFT OPEN

All of these are in the note's §9 row 72:
- What the compiler does where DOM(h) cannot be computed exactly: backreferences, recursion, and the unrun verbs.
  This is R2 (4) and is for rev 20.
- The CONTEXT reading of "some match": any match of the pattern, or one agreeing with this match's other labels
  (§4H.1).
- A DEFAULTED label inside `all`. By C's definition, `all((m = 0: S))` is `(m? = 0: S)`, which is the not-both error,
  unless rev 20 says the default stands. This is the lane's finding, not decided.
- zero-pass-empty: F1 is the manager's reading 14:50 (b). It stays on the owner's list until he assents.
- NOTED, not decided: one merged warning for the never-absent mark and `default.unused` (a).
- The zero-pass case in the group questions: zero passes give no pass to count. This is the lane's statement in
  §4H.4, consistent with review r28's verify derivation, and not separately ruled.
- §9 rows are the lane's reading of what rev 20 must change. The manager drafts rev 20, and `predicates_future.md` is
  not edited here (row 64).
