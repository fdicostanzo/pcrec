# Critic SITES — round crit-condkind (design)

## Findings


### SITES-1  all(c) has no ruled definition; 17 rev 22 sites hang on it
STATUS: CONFIRMED (record + note quoted)
SEVERITY: answer
EFFORT: medium.  BLAST RADIUS: rev 22 0 (L431, L598, L651, L979, L997), 0.1 L36 and L93, 2.6 (L1503-1512), 4.2 (L2224-2232, L2320-2324, L2372-2375), 4.3 (the group-question table L2452-2468, the closing-example table L2470-2494, L2606), 7.1 (L3217), 8 (L3365), 13 (L4376, L4794, L5484-5489); sites S003 S009 S021 S030 S037 S050 S051 S068 S091 S096 S102 S106 S107 S112 S125 S144 S155 in sites.tsv.
WHERE: COND-FAMILY 21:49 ("MINE, to restate and have checked: the 'all' group question") and 22:30 ("MINE, restated without his word ... 'all' = every pass passes the condition, and there may be none"); condition_kind.md II.5 row all(c), III.3.
BODY: rev 22 defines all(c) only as "c with every label marked" (L2228-2232, L2453). The mark is out, and neither ruling defines all: the record marks the restatement as the manager's and unchecked, and the note only RECOMMENDS A2 (III.3: "THE LANE'S RECOMMENDATION: A2"; A1 = retire). All 17 sites need the same decision, and they are not equivalent: (1) A2 differs from the plain condition exactly on zero passes (10 of 1,110 on RZ) and on a default (with `h = 9` the 10 differ again, III.3), so L36's verdict (BY DESIGN) keeps a reason only under A2; under A1 all retires and L36, L93, L431, the SILENT entry at L651/L4669 and the (c) paragraph L2320 go. (2) A2's "none needed" needs an absent label in a PASS to fail that pass (UNKNOWN is not TRUE), which flips rev 22's closing example "all(((h, m): R)) accepts incomplete items" (L2468, L2494, 11 of 259) from "accepted" to "FAILS the item": the SILENT trap becomes a different trap and its row must be rewritten, not deleted. (3) Phase-1 scope: "all (IN, ruled)" (L997, L5485) was ruled when all meant the mark's group form; the ruling rested on the old meaning. (4) (e3) L2372-2375: all(c) was the ONLY way to mark every label of a passed condition (`t2 & all(office_c)`); without it there is no per-use way to give a passed condition a default, and the note does not say whether that loss is accepted.
FOR REV 23: do not write all(c) until the manager's restatement is checked and the owner answers or lets A2 stand; list L36 and L93 as OPEN, and say in (e3) that a passed condition carries only the defaults written in its body.

### SITES-2  Two defaults for one label: rev 22's one-witness rows need a verdict and a G0 diagnostic
STATUS: CONFIRMED (22:30 record; note III.8 "not designed")
SEVERITY: design
EFFORT: small.  BLAST RADIUS: 0.1 L104 (L779), 4.2 ONE WITNESS (L2361-2371, S101), 13 one-witness (L5459-5462), changelog L376, 7.1 (a new warning name or none); G0 (L630).
WHERE: COND-FAMILY 22:30 ("two different defaults on one label stay legal ... holds on the h-absent subjects"); condition_kind III.5 cost (1), III.8.
BODY: rev 22 states one-witness as a rule about two MARKED conditions and classes L104 DIFFERENT: BY DESIGN. The 21:49 ruling retires the manager's reading "one-witness", and 22:30 brings the same behaviour back for DEFAULTS (11 of 21 hold with no single fitting value; `(h = 1: <$k) & (h = 8: >$j)` is the only way to rewrite rev 22's own one-witness program, III.7). The record does not say how rev 23 must class the row. G0 (L630, the owner's standing criterion) says forms that look like one test must either agree or be told apart by the compiler; `(h = 0: <5) & (h = 9: >7)` beside `(h = v: <5 & >7)` is that pair. BY DESIGN needs the legend of S023 (SITES-7); WARNING needs a named warning that III.8 says is not designed; ERROR is the (b) reading the owner did not take.
FOR REV 23: carry L104 as DIFFERENT with the class left OPEN (or BY DESIGN with a stated reason), cite 22:30, and do not claim an error or a warning name.

### SITES-3  L101 and (e2.1): under the per-entry reading a record no longer equals its joint spelling, and nothing says so
STATUS: CONFIRMED (rev 22 L776 quoted; note III.2 row 866)
SEVERITY: design (answer on 9 of 110 subjects)
EFFORT: small.  BLAST RADIUS: 0.1 L101 (L776), 4.2 (e2.1) (L2342-2354), 13 default-reaches-dollar (L5470), 4.1 record text L1920, G0 + SIMPLIFYING SEMANTICS (L658).
WHERE: COND-FAMILY 22:30 (default-reaches-dollar REVERSES); condition_kind III.2 row 866, III.5 cost (2).
BODY: rev 22 L101 says `(a = 0: <10, b: >$a)` vs `((a = 0, b): {(x, y): x < 10, y > x})` is SAME, resting on (e2.1). Under 22:30 a `$a` reads the real label, so the record FAILS on `-1` (b's test sees NULL) while the joint spelling HOLDS (54 vs 45 of 110, III.2 row 866). The record names the reversal but not the row's new verdict, and no diagnostic is proposed for the silent shape "a record defaults a and reads $a in the same record". The note offers only prose advice (write the joint). The trap is one a G0 reader will meet: the default is written next to `$a` and has no effect on it.
FOR REV 23: L101 becomes DIFFERENT with a class (BY DESIGN with the 22:30 reason, or a warning if one is designed); rewrite (e2.1) as "a `$a` reads the real label; the question with a default is the joint condition", and drop the "same with `a?`" clause.

### SITES-4  Complement per subject versus rev 22's filter-role complement, which reads its stretch and narrows "matches"
STATUS: CONFIRMED (quoted lines; the behaviour rests on the note's own S1/S2 numbers, not a run of mine)
SEVERITY: answer (searched mode only)
EFFORT: medium.  BLAST RADIUS: 2.2 RULE and WHAT ! TAKES (L1199-1229) and complemented pattern (3) (L1234-1240), 5.4 prefix-! row (L2949), 11 THE ONE WHOLE-MATCH RULE (L470, L3645, L3870), 0.1 MODE OF THE ANSWERS (L820-830), L11 L30 L95; sites S057 S058 S060 S117.
WHERE: COND-FAMILY 21:49 source-row ("a searched pattern gives several result rows per subject; the complement is per subject"); condition_kind 1.1 (S1 vs S2, `9:30`).
BODY: rev 22 says a FILTER role matches its stretch whole (L470, L3870) and `!q` is "a label-free FILTER on subjects: it narrows the outside program's matches like any filter" (L1234-1235), and a searched program retries a shorter span when a filter rejects (D196, L820-822). That is S2: on `t2 & !q` searched, subject `9:30`, the span `9:30` is rejected (q holds), the span `9` is a non-row of q, so `!q` admits it and the program reports `9`. 21:49 rules S1: the complement is per subject, `9:30` FAILS (note 1.1: S1 1,970 vs S2 11,110 of 11,110). So `!q` becomes the one filter whose input is the subject, not its stretch, which contradicts "the ONE rule: a filter matches its stretch whole" and "A & !B = A minus B" (L1206-1207) in searched mode, and makes D196's retry useless for `!q`. Neither the record nor the note states this exception to the ONE WHOLE-MATCH RULE or what the source row of `!q` is when `!q` stands inside a nested filter role (see SITES-6).
FOR REV 23: state that in a searched program `!q` reads the SUBJECT (S1), list it beside the one whole-match rule as the exception, and re-word 2.2 (3) ("filter on subjects" now means the subject, not the stretch).

### SITES-5  when(c, p): the note equates it with per-row case-when; rev 22's body is per source row
STATUS: CONFIRMED (derived from the note's own rows 156 and 185; no run)
SEVERITY: answer (searched mode only)
EFFORT: small.  BLAST RADIUS: 8 when (L3338-3346), 0.1 look-alike rows on when, FIXIND-1.
WHERE: condition_kind 3 row `when(c, p)` (line 185) versus 2 table row "several result rows" (line 156).
BODY: line 185 says `(x & c & p) | (x & !(x & c))` = SQL `case when c then p else true end`, "the rows of x where (c TRUE and p) or (c not TRUE)". Line 156 says `!(x & c)` is per SOURCE row. In whole-value mode (one row per subject) they agree. In searched mode a subject with two result rows r1 (c TRUE, p FALSE) and r2 (c FALSE) keeps r2 under case-when but is dropped by the formula (the subject has a c-TRUE row, so `x & !q` rejects it, and `x & c & p` has no row). rev 22 L3338 and rev 23 will write the formula; the note's equivalence claim is wrong for searched subjects.
FOR REV 23: define when by the formula (per source row), say it is NOT case-when per result row in searched mode, and keep the consequent reading the row (III.2 row 879: 45 vs 54).

### SITES-6  Vocabulary and the STRING SETS foundation versus source row / result row / statement
STATUS: CONFIRMED (words quoted); SUSPECTED for the role-table mapping
SEVERITY: design
EFFORT: medium.  BLAST RADIUS: 0.3 Words (L1017-1050: subject, span/stretch, scoped match, filter role, searched), 11 STRING SETS (L3597, L3679, L3850-3868) and THE ROLE TABLE (rows 6, 7), 13 rows O25 C9 C15 C27 (L4324-4348); 187 "subject" and 160 "span" hits otherwise unaffected (S158).
WHERE: COND-FAMILY 21:49 source-row; 20:41 (a)(b); condition_kind 1.1 and 2.
BODY: rev 22 §0.3 defines "subject = the run-time TEXT being matched" and "span/stretch = the text a set position filters"; §11 founds patterns on STRING SETS ("the strings it matches ENTIRELY", RULED CF:713). The model says a pattern is a statement and the source row is "the whole subject", the value a program is applied to (1.1). The record fixes the source row only for the final program. A pattern in a nested role (a `records` item rx, `contains(r & (g: "x"))`'s argument, a filter on a transform's output, an `each` entry) is applied to a stretch or an item; the note never says that such a role has its own source row (the stretch), or that "subject" in §0.3 and "source row" are two words for one thing at the top and different things inside. In whole-value mode the answers coincide (one row per source row), so no answer moves there; the mapping is what rev 23's §0.3 and the role table must carry.
FOR REV 23: add "source row" and "result row" to §0.3 with the role table's source per row (final program: the subject; filter role: its stretch; records item: the item), and re-found STRING SETS as "the source rows that have a result row" for whole-value roles.

### SITES-7  Look-alike legend, standalone complement and cross-references
STATUS: CONFIRMED
SEVERITY: doc
EFFORT: small.  BLAST RADIUS: 0.1 legend (L669), 13 BY DESIGN legend (L4660-4669), 2.2 REASONING (L1271-1272), joint_condition.md (258 mark/DOM hits; rev 22 cites its tables), predicates_future.md items 3, 6, 8, 11, 12 (24 hits).
WHERE: rev 22 L669; condition_kind 2 line 157 and 3 row `!` on a pattern.
BODY: (a) The legend defines BY DESIGN as "a mark's stated meaning (5.4)"; with the mark gone the class needs a new one-line definition (what is by design now: the default's per-test scope, the sequence rule, searched-mode bounds). (b) The model gives standalone `!Q` a meaning (line 157: "`!(P & c)` ALONE returns it"); rev 22 forbids a standalone `!B` where an rx is needed (L1207-1208, L1271-1272). Nothing in 21:49 or 22:30 lifts that, so rev 23 must not import it. (c) rev 22 cites joint_condition.md tables (TM2), (GF), (AR) as evidence; those tables carry the mark, and the file is RULED, so rev 23 should say which parts are superseded rather than leave the citations live.
FOR REV 23: redefine BY DESIGN, keep the standalone-`!` error, add a superseded-in-part note for joint_condition.md and predicates_future items that quote the mark.

### SITES-8  "A label no match can set": the error's reason (an empty DOM) is gone
STATUS: SUSPECTED (what would confirm: run the DEFINE witness `/(?(DEFINE)(?<o>\d{1,3}))(?&o)\.(?&o)/` with `(o: <5)` and `(o = "1": <5)` and see which answer it gives)
SEVERITY: design
EFFORT: small.  BLAST RADIUS: 4.2 (L2301-2307), 7.1 label.unset and default.unused (L3205-3218), 5.2 empty-intersection error (L2854).
WHERE: rev 22 L2301-2307 (review r29 SIMULATE-5 FIX-NOW); condition_kind II.5 (silent on it).
BODY: rev 22 makes it a COMPILE ERROR on "the mark (or default)" because DOM(h) is empty and every `(h?: S)` would fail whatever S says. Without the mark: an unmarked `(o: S)` FAILS everywhere, quietly (`label.unset` warns); a default `(o = "1": <5)` HOLDS everywhere (the default is always read), which is the silent wrong answer SIMULATE-5 was filed for. II.5 says the per-label value-set reader (§5.2) "stays" but does not mention this error. The new reason would be: the label's regex value set is empty, so any condition and any default on it is dead (default.unused (a) says "never ABSENT", the opposite case, "always absent", is not named).
FOR REV 23: keep an error or a named warning for a condition or default on a label no match can set, with its reason restated from the per-label regex value set; do not delete the paragraph with the mark.

### SITES-9  A second reader of domain-scope: "repeated label" and "can be absent" are read from the PROGRAM
STATUS: CONFIRMED for loop-ness (quoted); SUSPECTED for "can be absent" (7.1 does not say regex or program)
SEVERITY: design (can change which programs draw the sibling-loops error or need a group question)
EFFORT: small-medium.  BLAST RADIUS: 4.3 repeated-label definition (L2437-2441), pairing-loop paragraph (L2564-2570), 7.1 label.unset / default.unused (a) (L3205-3218), §0.3 `set once / repeated` (L1050).
WHERE: condition_kind II.5 ("the PER-PROGRAM value set (DOM, domain-scope, mark-narrows) is read by the mark and by nothing else"; "ONE OTHER READER" is the §5.2 error) versus rev 22 L2437-2441.
BODY: rev 22 defines a repeated label as one that "CAN BE SET MORE THAN ONCE IN SOME MATCH OF THE PROGRAM (rev 21, review r29 group E: loop-ness by behaviour, as DOM is; 'of the program' by **domain-scope**, CF 16:31)", and the pairing rule repeats it (L2564-2570). domain-scope is retired by 21:49 because "no reader but the mark"; this is a second reader the note's grep list (lines 2077-2090, 2092-2122, 2042-2049, 2066-2075, 1036, ...) does not include. Whether a condition that narrows the program can turn a loop into "not repeated" (`P & (k: "b")` on a branch-reset program where only the `a` track loops) decides the bare-`$x` error, sibling loops and the group-question requirement. The same question applies to "a label can be absent where the condition reads it" in label.unset and default.unused (a) (L3205, L3214).
FOR REV 23: say loop-ness and absence are read from the regex (conditions never narrow), or from the program with its conditions, and cite which; do not leave "of the program" hanging on a retired ruling.

## PROBED-AND-HELD
- Term census over rev 22 (copy `R/subject/predicates_draft_rev22.md`, 5,952 lines): 584 lexical hits of the term list (optional mark / `?` after a label / marked / some value / could have / value set / domain / DOM( / zero-pass / match-context / one-witness / absent-rule / stand-in / (e2.1) / all( / sentinel / dollar / string set / complement), by region: changelog 47, 0 and 0.1-0.3 93, 1-3 56, 4.1-4.5 233, 5 13, 6-7 12, 8-10 15, 11 14, 12 header 8 (0 in 12.1-12.12), 13 81, 14-16 12. Grouped into 158 sites in `R/SITES/sites.tsv`: COVERED 83, AFFECTED-UNCOVERED 35, UNAFFECTED 40. The 35 uncovered sites fall in nine findings (SITES-1 17, SITES-2 4, SITES-3 2, SITES-4 4, SITES-5 1, SITES-6 3, SITES-7 3, SITES-8 1, SITES-9 4 sites, counting cross-referenced covered rows).
- "default" has 196 hits; most are macro-head defaults, `default level`, `LEVEL: default` or `default OFF` (a different concept, §0.3 row L1034 says so); only the label-default sites were classed (S054, S073, S082, S099-S101).
- The twelve worked examples (12.1-12.12): all UNAFFECTED, none writes a mark, a label default or `all(`; their claim "0 of the twelve worked answers move" (L3971, L4041) stays true; only coverage rows L4057, L4061 need rewording.
- not-is-complement (`!` on a condition stays an error, 22:30 STATE) and `!some(c)` vs `occurs.none(c)` (L102): COVERED, nothing to decide.
- The mark table row (5.4 L2933), the glossary rows (L1033-1036), table (AR) columns, the DOM candidate tables, the "mark inside none" block and the mark-narrows paragraphs: all COVERED by the 21:49 retirement list and II.5.
- Warnings: never-absent-mark retired; default.unused (a)(b) already means "a default that can never change an answer", which is the 21:49 "can never be used"; label.unset's fixes drop to two (II.1.3 G). COVERED.
- Searched-mode default (L2057-2064, L820-830): COVERED by II.8 (unchanged, not re-run); the mark counts (1,698) just drop.
- I ran no code and wrote only under `R/SITES/` and this file.

CRITIC COMPLETE
