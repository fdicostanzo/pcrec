# READERS findings — round predspec29 (r54)

Method: every term of each reversed statement grepped over R/subject/predicates_draft.md (propagate, inherit, own flags, NO INHERITED,
exact width, padded, codepoint, class-order, TYPE ERROR, join, plus-operands, dollar-*, `% 0`, same-name-*, each open-question slug);
every hit read in context; a hit counts only if it states the OLD rule (or lists a ruled item as open) with no "[REV 29" mark in its
own cell/paragraph. Line numbers are lines of R/subject/predicates_draft.md. Records (§16, §R.11 rows, changelog, §R.9 old-rule
columns, §R.7 "was -> now") are excluded by design. No engine runs: this lens is textual (CONFIRMED = quoted sentence + line).

## Findings

### READERS-1 (CONFIRMED, doc/design-contract, small effort, blast: 1 table row) — §R.6 states "no exception remains for flags"; rev 29 makes one
- Location: §R.6 EXCEPTIONS table, row "a HOLE in a pattern position (rev 25)", line 2851 (cell 4): "[REV 28: the FLAGS half REVERSED by
  hole-flags and flags-propagate ...: the inserted pattern starts with the flags in force at the hole and its own written flags win, which IS
  regex's reading of `(?:foo)` written there, so no exception remains for flags; the own group numbering stays]". The row carries NO "[REV 29" mark
  (REV 29 marks in the region 2802-2893: none).
- Rev 29 says instead: only `i`, `m`, `s` are inherited; `U`, `x`, `xx`, `n` are not (line 2200-2202; flags-scope), and "as text" now means the literal
  spelt `(?^ims-subset:...)` at the hole, not `(?:foo)` (line 1926, REV 29 bracket: "'as text' now means the inserted literal spelt `(?^ims-subset:...)`").
  So the table that is the draft's list of EXCEPTIONS to "a hole is regex's own reading" says there is none for flags, while rev 29 introduces exactly a
  flags exception (`/(?x)x${/a b/}/` is not `/(?x)x(?:a b)/`, line 2207: WHOLE `xa b` HOLDS vs `xab` under the text paste).
- Fix: add a [REV 29] sentence to that cell: exception for `U`, `x`, `xx`, `n` (BY DESIGN, flags-scope); also name R.6 in §R.9's flags-scope row (3591 lists
  R.1.15, R.1.14 (1), §11, §0.1 L32, §R.8 but not §R.6, though 3568 listed §R.6 for rev 28).

### READERS-2 (CONFIRMED, doc, small, blast: 4 sentences) — present-tense "starts with the flags in force" / "its OWN flags" statements unmarked for rev 29
Each states the rev-28 form of the flag rule ("the inserted pattern STARTS with the flags in force at the hole", or older "OWN flags") with no rev 29 qualifier:
- Line 6392, §5.4 operator table, row `${ }`: "[REV 28: what it inserts STARTS with the flags in force at the hole, its own written flags winning (hole-flags,
  flag-propagate RULED)...]" - no REV 29 mark in that row. Under rev 29 it starts with only `i m s`. This is the operator table (the contract-bearing list).
- Line 5100, §8 `search` library text: "The hole `${x}` is one atom with its OWN flags and its OWN group numbering (§3.3, §11, §13 O32): a reader who splices
  the text by hand must write `(?:x)` with x's flags kept ..." - NO mark of any revision (stale since rev 28, now wrong in a second way: a hand splicer
  needs `(?^ims-<subset>:...)`-like scoping, not `(?:x)`, to match what rev 29 inserts when the outer has `(?x)`/`(?U)`/`(?n)`; and "x's flags kept" is the OLD rule
  reversed in rev 28).
- Line 8196, §13 O32 resolution: "[REV 28: RESOLVED by flags-propagate: the inserted `q` starts with `m` ... as the text inlined does]" - still true for `m`
  but O32's heading is "Flags of a pattern inserted in a hole" and the item is not marked for flags-scope, so a reader of §13 O32 gets "propagate" with no
  scope; the §R.9 flags-scope row (3591) does not list §13 O32 (3568's rev 28 row does).
- Line 8852 (§13 O70 (ii)): "[REV 28: ... what remains of (ii) is the FILTER ROLES inside the argument (an `&` operand, a `label:` condition), which the
  ruling does not reach (§2.7, A19)]" - rev 29's REACH reading reaches them (line 2217-2219 and T-c at 5487: filter-role arguments 0/0/0 vs the primitive).
  No REV 29 mark; and line 8883-8884 repeats "which today's rule forbids [REV 28: forbade ...]".
- Fix: one mark per site, or point them all to R.1.15's flags-scope paragraph.

### READERS-3 (CONFIRMED, doc, small, blast: 3 answer-table rows) — R.1.16's ANSWERS CHANGED table: A18, A19, A24 unmarked though rev 29 changes what they say
- A18 (line 2601, [REV 28]): the reversed-rule answer is stated "`i`, `m`, `s`, `x` each (rev 28's PART FL)". Rev 29: `x` is NOT inherited (A29, line 2612, is the new row
  that reverses it). A18's own cell still lists `x` as one of the four that follow flags-propagate; nothing in A18 points to A29.
- A19 (line 2602, [REV 28]): "for a FILTER-ROLE argument (`any_case(quoted("ho"))`) it still differs, 3 of 781 ..., while an `&` operand keeps its own flags (the manager's m2: the
  ruling speaks of holes), 0 if propagation reached it (NOT ruled)". Rev 29 adopts exactly "propagation reaches it" as THE DRAFT'S READING (flags-in-filter REACH; §2.7 T-c
  line 5487: filter-role arguments 0 / 0 / 0 of 781) and §R.9 row 3594 says m2 is "SUPERSEDED". A19 carries a rev 28.1 mark but no REV 29 mark, and the §R.9 rows
  do not list A19.
- A24 (line 2607): "the lifted order is enumerate's (lift-order)" with a rev 28.1 mark only. §R.9 row 3592 (class-order) names A24 as a site changed by rev 29
  ("§5.5, T8, A24, §R.8 class-order") yet A24 carries no REV 29 mark; class-order means the lifted order is now "longer first per class position", which is NOT enumerate's
  (codepoint) order for class members. Same for line 2347 (R.1.15 (7) "lift-order is answered by construction-line: enumerate's order ...") which has the class-order
  note only at the end of the paragraph (2351) - acceptable - but A24 has none.
- Fix: add the mark in each cell, or add A18/A19/A24 to §R.9's marked list.

### READERS-4 (CONFIRMED, doc, small) — plus-operands still counted as open by the draft's own §R.8 arithmetic and in two rows
- §R.8 line 3298 ("STILL ASKED after rev 29: as after rev 28.1, LESS the six RULED, PLUS the new rows"). "After rev 28.1" is "as after rev 28 ... PLUS the new rows" (line 3253-3256), and
  "STILL ASKED after rev 28" (line 3232) begins with **plus-operands**. Rev 29 rules SEVEN (the changelog line 3 and R preamble line 750 say six plus plus-operands), but this line
  subtracts "the six". By the draft's own recipe plus-operands is still asked after rev 29. Should read "the seven RULED" (or name plus-operands).
- §R.8 rx-module row, line 3386: "[REV 26: ... open: **value-hole**, **other-holes**, **plus-operands**, **anything-text**, **backref-label**, **zero-in-sequence**] [REV 27.1: **value-hole** and
  **backref-label** ANSWERED in rev 27]" - plus-operands is marked answered in NO mark in that row (REV 29 marks: 0 on line 3386, confirmed by grep). Same for line 3848 (§R.11 row 14:
  "**plus-operands** asks `+` on non-numbers", 0 REV 29 marks; this one is a record-status column "in rev 25.1" so lower weight).
- Line 88 (changelog rev 27: "plus-operands kept open") is a historical record: excluded.

### READERS-5 (CONFIRMED, doc/design-contract, small-medium) — §7.1 NAMED WARNINGS table has no row for the two warnings rev 29 adds
- Rev 29 adds (a) the form-keyed `$x & S` warning (§R.2 line 2661: "the placeholder: `pcrec.dollar.filter`, selected like every warning (§7.1)") and (b) plus-operands'
  "a warning where the compiler KNOWS the whole result is nothing" (line 2042-2043; T8 line 2561: `"a" + "b"`, `[a-z] + 1`). §7.1's table (lines 6664-6680: `test.never`, `test.always`,
  `empty.search`, `dead.branch`, `label.unset`, `default.unused`, `compare.*`, `label.numbered`, `match.never`, `label.ambiguous`, `warn.unused`, `anchor.whole`, `label.both_sides`,
  proposed `precedence.section`/`array.hole`/`flag.hole`) has NO row for either and no REV 29 mark; the R preamble (line ~746) says the warning names are "one list, §R.8", and §R.8 has no row for them either
  (only in R.2 and the T8 cell). Precedent: rev 25.1 added two rows "the row rev 25 omitted" (lines 6693-6694). Note also `flag.hole` stays listed "proposed, NOT adopted" - consistent, since
  rev 29's inheritance leaves it unneeded, but `flag.hole` could be re-asked for the non-inherited flags (a binding that relies on `(?x)` of its context silently differs): rev 29 says DIFFERENT, BY DESIGN
  (L32, line 4383) and adds no warning - a design question, not a reader miss, listed here only so the row is consciously not added.
- Related reader: §R.2's dollar row says "A warning, never an error ... Its NAME and wording and whether it can be silenced are THE MANAGER'S CALL, not made here" - §7.1 and §R.8's spellings
  list should carry that unnamed state as an open spelling; they do not.

### READERS-6 (CONFIRMED, doc, small) — the revision's own bookkeeping sections stop at rev 28.1
- §R.9 MARKED SECTIONS (lines 3600-3647): lists "rev 24's", "rev 27's", "rev 27.1's", "rev 28's", "rev 28.1's" but NO "rev 29's" entry, though the revision adds [REV 29] to ~120 lines in
  §R.1.13-R.1.16, §2.7, §5.4, §5.5, §R.2, §R.7, §R.8, §R.9, §R.11, §0.1 L26/L28/L32, §4.1. (The file says each such list names "what is superseded"; a reader cannot find the rev 29 sites from here.)
- §R.10 Evidence (3648+): has REV 27, 27.1, 28, 28.1 entries (3676 "REV 28.1 (lane predspec281 ...)", 3693 "REV 28 ...") and NO REV 29 entry: the PARTs the draft cites everywhere ("rev 29's
  PART PO, FF, CO, DD, NE, SC, PL, TA, AC") are described only in the changelog (line 23) and R preamble (752); R.10's one-per-revision convention lapses at rev 29.
- §R.8: the "Nothing STOPPED / STOP RULE" paragraphs run REV 24.4, 25, 26, 26.1, 27, 27.1 (lines 3436-3490) and none for REV 28, 28.1 or 29; the rev 29 changelog entry (lines 7-23) has no
  STOP RULE sentence either (rev 28, 27.1, 27 changelog entries do: lines 57, 74, 90). A reader cannot tell whether the rev 29 fold found two rulings deciding an answer differently.
- §R.11's own header (line 3831) says "rev 28: rows 125-148, the 2026-11-18 evening" and has no mention of rows 155-175 for rev 29 (the rows exist, lines 3991-4011).

### READERS-7 (CONFIRMED, doc, small) — the §5.4 `+ - * %` semantic row and §2.7's bodies table were not brought to rev 29
- Line 6387: the operator row `+` `-` `*` `%` says "between numbers ... numbers = THE NUMBER DOMAIN (R.1.16)" and its error cell says "`+`, `*`, `%`: no case". Rev 29's rule (non-numeral operand = nothing, warning if
  known) is stated in the precedence-table rows (6371-6372 are marked) but not in this row, which is the one that states what each operator DOES. No REV 29 mark in the row; its "no case" census
  cell is now incomplete (a warning case exists). Also line 7618 (the census row "| `+` | none | RULED (CF:782 (1)...)") has no REV 29 mark.
- Line 5480, §2.7 bodies table: only `padded(S)` | `/0*${S}/`. The two-parameter `padded(rx, n)` is declared (line 5435) a "PLAIN MACRO" whose body is given; per the section's own "bodies" convention
  (line ~5476: "its body in the language") it should have a row (or the row should say "one parameter") - the body appears only in a prose bracket. (Rev 28 had the same gap; rev 29 makes the body RULED.)

### READERS-8 (SUSPECTED, doc, tiny) — bracket nesting inside §2.7's THE ORDER passage
- Lines 5428-5455: the "[REV 28.1, review r52 A (TABLES-3) THE ORDER: ..." bracket is not closed before "[REV 29: **padded-order** RULED ..."; the REV 29 bracket closes at "(rev 29's PART PO;
  sabotages t1, t3 caught).]" (5453) and then the 28.1 sentence "The `0*` arm checked against `0?` (review r52 FIXIND-14) ... caught).]" closes the OUTER 28.1 bracket. The result is that the rev 28.1
  FIXIND-14 sentence reads as if it were still a rev 29 text and rev 28.1's retracted "lazy infinite argument needs the body as written" shares a bracket with its withdrawal. Confirm by counting
  brackets in lines 5428-5455.

### Not findings (checked, stated for the record)
- Reversal (4) TYPE ERROR: all live hits (2041-2042, 2103, 2110, 2157, 2422-2423, 2563, 3423, 5050, 6371-6372) carry a [REV 29 ...] mark; the remaining plain "TYPE ERROR" hits are in records (§R.9 3541/3560, A8 2591, changelog).
- Reversal (2) padded-body: all live hits (5413-5453, 2603, 2611, 3357, 3425, 3590) are marked; A20 (2603) is marked at its end.
- Reversal (3) codepoint: 6429, 6442, 4377, 7795, 2351, 2561, 2584, 2589 all carry marks; line 6440 "Codepoint order is extensional ... (G0)" is the REASONING for the array only and stays true for the array interface (class-index).
- Reversal (5): 4379 (L28), 5057, 5684, 2661, 2584, 2615, 3345, 3362 all marked; 2994 is a rev 28.1 change-list ("was -> now") record.
- Reversal (6)/(7): number-edges 2532/2616/3361, same-name-count 1780/2613/2617/3363 marked.

## PROBED-AND-HELD
- Terms grepped over the whole 10,160-line draft: propagat (51 hits), inherit/flags in force/own flags/STARTS with (88 line numbers), exact width/exact-first/exactly-n/two-case/argument's own order, padded( (about 80 hits),
  codepoint/class-order/longest first/lift-order (40), TYPE ERROR/type error (27), join (50, mostly join-order unrelated), plus-operands (37), dollar-warning/dollar-diagnostic/stands for its group/dedicated warning (50),
  `% 0`/negative (12), (?J)/same-name (60), each of the eight slugs in "open" position (unmarked, non-RULED lines: flags-scope 6, flags-in-filter 7, padded-order 10, class-order 7, plus-operands 9, number-edges 5, same-name-count 5, dollar-diagnostic 8 - all but the
  ones in READERS-1..7 are records, lists that name the rulings, or REV-marked).
- Min witness length: n/a (textual lens; no engine run; no counts are claimed).
- §R.9's REV 29 rows (3590-3596): seven rows for seven rulings; every row's site list checked against the draft: flags row's R.1.15, R.1.14 (1), §11, §0.1 L32, §R.8 all marked (2198, 1926, 7093, 4383, 3359-3360); padded row's §2.7, A20, §R.8 marked; class-order row's §5.5, T8, §R.8 marked but A24 not (READERS-3);
  dollar row's §R.2, §0.1 L28, A21, §R.8 marked; plus-operands row's R.1.14, A8, §R.8 marked; same-name-count row's R.1.13 marked.
- Header (line 3), R preamble (748-752), changelog (7-23) all say six + plus-operands consistently; §R.11 rows 155-175 present at 3991-4011.
- §R.2's dollar row and §0.1 L28, §4.1 (5684), §2.5 (5057) agree with each other (form-keyed warning, legal, DIFFERENT BY DESIGN).
- Not checked: the evidence model (other lenses), the correctness of any printed answer.

CRITIC COMPLETE
