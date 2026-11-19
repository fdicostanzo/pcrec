# CRITIC CHANGETABLE: predspec26 (review r47, 2026-11-18)

## Findings

### CHANGETABLE-3 (CONFIRMED, doc, effort S, blast radius: one cite; subject line 2258, §R.8 RULED list)
"**label-mark** closed by entailment, its spelling remains (R.1.14 table)." R.1.14 has no table any more: line 1593-1594
"(The rev 25 / 25.1 position table stood here ...)"; and rev 26 itself places label-mark in R.1.13: line 1767 "[REV 26]
CLOSED by entailment ... | R.1.13 EXPORT AND VISIBILITY" and line 2318 (same). The cite at 2258 lands on nothing (no
"[REV 26" within 8 lines either, though §R.8's RULED list is marked elsewhere). Fix: "(R.1.13 EXPORT AND VISIBILITY)".
Line 675 ("this fix (R.1.1 PLACES, predicates_future.md item 22)") likewise names R.1.1's PLACES paragraph, which rev 26
replaced by a pointer (line 784); history text, doc-only, same fix.

### CHANGETABLE-4 (SUSPECTED, doc, effort S, blast radius: two readers; subject lines 4372-4374 (§4.1) and 4912-4913 (§5.3))
Export-rule (R.1.13 line 1415-1436: "A label is public unless its name begins with `_`"; "5. The caller's captures are what
is visible from the top-level program by these rules") has two readers outside R.1.13/R.1.0 that state the older picture
unmarked. (i) §4.1 line 4372-4374: "x is looked up in the other operands of the chain ... a label in both is AMBIGUOUS
(error naming both)" says nothing of visibility: a `[_ = A]` operand's labels are invisible to the lookup (ruling (7)), so
a name in a private operand and a public one is NOT ambiguous. (ii) §5.3 line 4912-4913: "Caller-visible captures are a
library macro: `capture(x) := /(?<${x.label}>${x})/` ... exported like any binding (§7)" contradicts statement (5): the
caller's captures are every public label, no macro needed; `capture` becomes either redundant or the way to rename.
(iii, minor) §5.4 line 4994 and §0.1-adjacent census line 6210 state `+ - * %` "between numbers" without array-lift's
"alternations combine on the product" (§2.5 heading carries the mark; the operator row does not). Confirm by grep
'Caller-visible' (1 hit, 4912, no mark within 8 lines). Fix: a [REV 26] pointer in each.

## PROBED-AND-HELD

### CHANGETABLE-1 (CONFIRMED, doc, effort S, blast radius: one reader; §5.4 `${ }` row, subject line 5000-5002)
The §5.4 `${ }` row still says "the typed positions follow the position table, one copy of the literal per combination
(R.1.14)]" inside a bracket marked only "[REV 25.1" (line 4999 start; mark at 5000 "since rev 25 the inserted PATTERN..."). Rev 26 WITHDREW exactly this
("rev 25.1's 'one copy per combination' is WITHDRAWN as a rule", line 768; "[REV 26] rev 25.1's position table's single
product column ... NARROWED", §R.9) and made R.1.14's table a pointer to R.1.0 HOLE POSITIONS. Repro:
`grep -n 'one copy$\|one copy of the literal per combination' predicates_draft.md` -> 5002 (unmarked, no "[REV 26" within
8 lines; the row's "[REV 26" count is 0 for this cell). The sentence also lists group name/option/class together as
"one copy per combination" positions, while name-hole (array in a name = compile error) and other-holes (OPEN) say otherwise.
§5.4 is named in the changelog (line 25) only for "two operator rows", so this reader was never swept. Fix: replace by a
pointer to R.1.0 HOLE POSITIONS with a [REV 26] mark.

### CHANGETABLE-2 (CONFIRMED, doc, effort S, blast radius: three §2.6 readers; lines 3829-3830, 3992-3993, 4010-4012)
§2.6's refusals were WITHDRAWN as errors (marked at 3838-3855, "kept below as the record"), but three readers outside that
marked block still state them as live: line 3829-3830 "That is PCRE2's find-all order ... for every argument that passes
THE TWO ARGUMENT REFUSALS below; for the arguments they refuse, the loop and find-all differ" (a pointer to the marked
heading, but its own claim "for the arguments they refuse" no longer has a refused set); line 3992-3993 "The two refusals
keep 'the hits are find-all order' true for every argument that compiles, so one sentence describes what `occurrences`
finds." (live rule, no mark: after rev 26 a nullable or hit-carrying argument compiles and the hits are NOT find-all order
for the carrying one, per hit-carry); lines 4010-4012 "The refusal of a nullable argument and the scoped `(?s:...)` gaps:
LEAN (manager, rev 9; §13 O53); the refusal of an argument reading its own group ..." (a status ledger stating both refusals as
standing LEAN). Also 3888-3889 "The same root as the second refusal above, which is why that one is a refusal" (stale
reason, inside THE ITERATION'S OWN VALUES). Repro: `grep -n 'two refusals\|second refusal' predicates_draft.md` and look for
"[REV 26" within the paragraph: none for 3992, 4010, 3888. Fix: mark each "[REV 26: withdrawn as errors, hit-carry]".

Method: a script (changetable/g.sh) printed every hit of each ruled/withdrawn rule's terms with a flag for "[REV 26" within
4 lines; every unflagged hit outside §R's own marked records was read in context. Terms swept (over the whole 8,750-line
subject): value-is-pattern/one-member pattern; nearest pattern/ambiguous-reference/numbers-not-subject; `0`/group 0/number
names ($1, (1:), by NUMBER); plain search/hits are those/TWO ARGUMENT REFUSALS/refusal/second refusal/nullable (all 45
nullable hits); cartesian/cross product/per member/copy per/one copy per combination/illegal combination/REMOVED/join of
name copies/branch reset; first slowest/product's order; ordinary type error/adding two patterns/arithmetic/`+` rows;
LEFT side/last set/already reads it/across parts/free-name/backreference (45 hits)/ambiguous (all 54 hits after line
2690)/export/`_`/private; quantifier-on-condition; sequence operand; lookahead/lookbehind; complement/lone/`anything`;
hole-in-filter/filter-hole; `${$` value holes; cites R.1.0, R.1.1 PLACES, R.1.14 (n)/table/RX/hole-reading, R.1.15.
Counts: about 520 hits checked; 14 affected-unmarked readers in 4 findings (3 in finding 2 plus 3888, 1 in finding 1, 2 in
finding 3, 3 in finding 4 incl. the minor); the rest UNAFFECTED, reasons in groups: (a) hits inside rev-history/changelog
text or inside a block the subject marks "kept below as the record" (3856-3880, 6990-7003, 7113-7125, 5605, 6123, 7250,
the rev 7-25 journal-style paragraphs); (b) hits in §R.9/§R.11 tables, which are the change table itself; (c) hits whose
paragraph carries a "[REV 26" within 4 lines (about 200 of the hits); (d) R.1.4's zero-place paragraph (897-906) which
defers to R.1.13 for chains ("which pattern a number names in a chain is R.1.13") and is consistent with the zero
addendum; (e) §R.2's numbered-label warning (1896-1899): a bound name is one pattern, so number-names' ambiguity error
does not touch it; (f) §0.1 L18/L53/L62 rows and §2.6 3845 marked; (g) §2.2 complement text (3612-3650) marked at 3616 and
the REASONING is about searched programs; (h) the value-hole readers 3068, 3743, 4294, 5889, 6715, 6791, 7049 all marked;
(i) 3764-3767 "for an UNFILTERED argument the hits are those of PCRE's own matching": consistent with hit-carry's narrowing
(a condition before its group makes the argument filtered); (j) 5334 `match.never`'s "THE MANAGER'S PROPOSAL" still true
(1679 keeps the nothing-left warning as MINE, not ruled); (k) cites R.1.14 (4), (b), (c), hole-reading (5), RX4 and
R.1.15, R.1.0 in §0.1/§R.11 land on the item named (R.1.14 (4)=hole-reading (4) at 1568, parse readings (a)-(c) at 1720,
R.1.0 rows at 741-772). The "every reader fixed or marked" claim (lines 609-611) is therefore FALSE as stated: findings 1-4.
Withdrawn-rule check (b): single product column (one hit unmarked: finding 1), name join (none unmarked), §2.6 refusals
(finding 2), R.1.1 PLACES paragraph (line 675 only, finding 3), the two nearest-pattern readings (history only).

CRITIC COMPLETE
