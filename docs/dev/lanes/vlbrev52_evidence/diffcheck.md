# Diff check: lane/vlbrev51 -> lane/vlbrev52 (docs/design/), vlookbehind rev 5.2

Critic: one read-only diff check, as the r6 vlb4 RULINGS asked. Subject: lane/vlbrev52 @ da5e3a3a3
(vlookbehind.md, vlb_d27_extract.md, docs/design/CLAUDE.md). Build tree read at main d600e06fc.
Blinded to docs/dev/lanes/vlbrev52_report.md (not read). PCRE2 facts come from libpcre2 10.46 via
ora2.py and from the prose note lookbehind_check_order.md. The source copy was not opened.

## Per RDY item

- **RDY-1 (ruled: first fault in written order). LANDED.** §6.2.2 "Which lookbehind is reported"
  says "a refused pattern reports the FIRST fault in WRITTEN order, as libpcre2 does. Post-order is
  dropped." The judging walk (steps 1-6) puts that into the design. The counter-cells, the inner-first
  cells, the reached-group cells and the innermost-blame cells are all pinned (§6.2.5 rows, gate 7,
  SV16/SV18/SV19), and so is the stage-1 offset move. I traced every pinned cell by hand and each
  one gives libpcre2's offset. The REVISION 5.1 G7 bullet is marked SUPERSEDED. Gaps: DC-2 (where a
  running sum is checked), DC-3 (the parse-time hold moves HEAD-agreeing cells into G5's class),
  DC-5 (no parse-time rule for lookbehinds the walk never meets), DC-8 (gaps in the mapping).
- **RDY-2 (clamp at PCREC_W_UNBOUNDED-1, honest figure). LANDED IN INTENT, the text is wrong in
  one place:** DC-1. The figures are right: 131070 = 2x65535; 262140 = 4x65535; the 25-step chain
  is 65535x2^25 = 2.199e12, above 2^40 = 1.0995e12 (step 24, 1.0995e12, is just below), so "about
  2^41" holds; 65535^3 is about 2^48. The clamp does not contradict §6.2.3's scoping, since global
  `pcrec_cwmax` keeps `pcrec_sat_add`/`_mul`. No reject-table pin is affected: no existing pin has a
  finite lookbehind past 2^40 (grep), and the "(this one has 80000)" pin is unchanged.
- **RDY-3 (ruled: walk meets lookbehinds in lookaheads). LANDED.** §6.2.1 "Lookbehinds met on the
  way" (any depth, either polarity, DEFINE inside a lookahead searched, a lookahead's own references
  and calls not followed). The §6.2.5 rows include the accept-set cell refused @4, the call twin as a
  K-row, and the controls. Also present: gate 3 EXTRA, gate 7, SV17, the ¶5a/¶5c hunks, and the
  extract. I traced all the RDY-3 cells and they match libpcre2. SV17's second witness is wrong
  (DC-6).
- **RDY-4 (S172). LANDED** (§6.2.7 first bullet; V3 reader list). Under the ruled order the
  ascending sort stays, so the anchor stays. That is consistent with S172's witnesses, which I read:
  two lookbehinds that do not reach each other.
- **RDY-5 (order 4 tests `hs` first). LANDED** (§6.2.2 paragraph before the table, order 4 row, the
  G17/RDY-5 K-row note, and §6.2.5's G17 row with the two within-branch cells).
- **RDY-6 (second DEFINE builder). LANDED** (§6.2.1 bullet, V2 reader list). The cited comment exists
  at main: rxt_compose.c:765 "Not a new shape", and :776 "... identical trees and a check can ASSERT
  that".
- **RDY-7 (`cx->job`, not `want_caps`). LANDED** (§6.2.4). Cites hold: `compile_driver` is
  compile.c:2038; `pcrec_count_groups` is :3795 with `want_caps = false` at :3821;
  `cx->job->altcls_*` is at altcls.c:83-84; `job->pf` is read in facts.c; `pcrec_bref_mark` is
  atomic.c:685. The extract §0 carries the cli.md §2.13¶1 hunk.
- **RDY-8 (rows, publish). LANDED** (§6.2.1, V1). `cg_index` is callgraph.c:174, `cg_minw_publish`
  :262, `cg_cwmax_publish` :317.
- **RDY-9 (extract re-cut). LANDED** (written-order rule, two-fault rule with its exception, the
  lookahead cells, ¶5a's text, the DEFINE-bug divergence, the 2^40 cell). No src/ or tests/ path
  leaks (grep), and `_VALID_LB` is named internal. It inherits DC-2's ambiguity (its "met at the
  item that crosses it") and depends on DC-1 for its 2^40 promise.
- **RDY-10 (¶5a). LANDED** (§6.2.8 ¶5a bullet; extract §0 ¶5a).
- **RDY-11 (pcre2only pin; SV9). SV9 LANDED. The pin does not hold as written:** DC-4.

## Fix-induced findings

**DC-1. MEDIUM. CONFIRMED by reading (HEAD `la_widths` control flow, mod_lookaround.c:313-330).**
§6.2.1 "Finite values clamp ...", second sub-bullet: "it lives in the lookbehind walk's arithmetic
(§6.2.3), under the lexical flag". Under §6.2.1's "Values per row" and §6.2.3 (G3), the lexical flag
is what makes `hs` lexical. `hi` is the NON-lexical recurrence (it counts `{0}` as 0, so
`(?<=(?:${v}){0}x)y` keeps compiling), so a clamp "under the lexical flag" never reaches `hi`.

Take the 25-step chain, or stage 1's `(?<=(?:(?:a{65535}){65535}){65535})x`. Read literally, the
design gives:
- `hi` = PCREC_W_UNBOUNDED (saturated);
- `hs` = PCREC_W_UNBOUNDED-1 (clamped);
- so order 5 marks the branch (hi unbounded, hs finite), and order 8 prints rule 0's sentence:
  "depends on a variable or a consuming callout".

That is a false sentence, worse than HEAD's, and it contradicts §6.2.5's two RDY-2 rows, gate 7's
figure pins and the extract's §2/§6 promise. The ceiling arm, the reader RDY-2 was about, reads
`hi`.

§6.2.3 itself, which the bullet cites as the clamp's home, says nothing about the clamp.

Fix: the clamp belongs to the lookbehind ENTRY (every column it computes: `lo`, `hi` and `hs`, with
or without a table), not to the lexical flag. Add that bullet to §6.2.3 and correct the V2 row
("under the lexical flag" -> "in the lookbehind entries"). Also say what `lo` saturates to: today
`pcrec_cwmin` saturates at PCREC_MINW_MAX, which equals PCREC_W_UNBOUNDED, so lo > hi is possible.
No reader is harmed, because order 6 refuses first, but it is unstated.

**DC-2. MEDIUM. CONFIRMED by probe.** §6.2.2 "The judging walk" step 2 ("each branch's items in
written order, descending into groups ... the branch's running `hi` passes 65535 at it") and the
note's §5 do not say WHICH branch's running sum is meant once the walk descends into a group.
libpcre2 measures a group (inline or reached) on its own: each branch at every level has its own
running sum, and a group's maximum is added to the enclosing branch only when the group item is
complete.

The natural reading, L's sum carried down into the group, gives 187 @0 on each of these:
- `(?<=a{30000}(?:a{40000}(?<=c+)))x`: libpcre2 125 @23, HEAD @23 (agrees today);
- `(?<=b{30000}\1)(a{40000}(?<=c+))x`: libpcre2 125 @24;
- `(a{40000}(?<=c+))(?<=a{30000}\1)x`: libpcre2 125 @9;
- `(?<=a(?:b(?:c{40000}(?<=d+))c{30000}))x`: libpcre2 125 @20.

The group's own sum is checked inside it: `(?<=(?:a{40000}a{40000}(?<=c+)))x` is 187 @0. The pinned
cells (`(?<=a{60000}b{6000}(?<=c+))x`, `(?<=(?:a{60000}|b)c{6000}(?<=d+))x`) do not tell the two
readings apart.

Fix: one sentence in step 2. Every branch walked, L's or a group's, has its own running sum. A group
item adds its maximum to the enclosing sum after the group's walk returns, and the 65535 check runs
there. Add a group cell to gate 7 (`(?<=a{30000}(?:a{40000}(?<=c+)))x` @23). Put the same sentence
in the extract §2 ("a group's length counts when the group is complete"). Also drop "the walk reads
them and computes none": it computes running sums.

**DC-3. LOW-MEDIUM. SUSPECTED (libpcre2 and HEAD measured; pcrec's post-stage-2 answer predicted from
§6.2.4's own mechanism).** §6.2.2 step 5: "A lookbehind nested in a DEFERRED outermost is judged in
that one's walk at postresolve". Under that rule, a nested parse-settled lookbehind's refusal waits
until postresolve, so it loses to every diagnostic raised before postresolve (G5's class). That
moves cells that agree at HEAD:
- `(a)(?<=\1(?<=c+))x\2`: libpcre2 125 @9, HEAD @9. After stage 2: the `\2` resolution error.
- `(a)(?<=(?1)(?<=c+))x\2`: libpcre2 125 @11, HEAD @11. Same.
- `(a)(?<=\1(?<=c+)(?C1))x`: libpcre2 125 @9, HEAD @9. After stage 2: the callout sentence.
- `(a)(?<=\1|(?<=c+))x\3`: 125 @10 on both today.

Step 6 names only the top-level case. A smaller twin is `(?<=(?<=c+)(?|a))x` (libpcre2 125 @4, HEAD
@4), which becomes the `branch-reset` module refusal; D26 discharges that one.

Fix (text): step 6 and the one K-row gain the nested-in-a-deferred-lookbehind case. Gate 7 pins one
cell with pcrec's predicted answer and a comment naming the K-row. If the manager wants these to keep
agreeing, the K-row's own mechanism (record the first parse-time fault offset, compare at
postresolve) would do it. That is not stage 2's work.

**DC-4. LOW. CONFIRMED (probe + reading).** §6.2.6 gate 3, `pcre2only=3`. There are two problems.

(a) The pin calls the `(*ACCEPT)` row a "latent REFUSE row". It is libpcre2 ACCEPT, lb 1 (probed),
and pcrec refuses it by module `verbs`. So it is a latent-ACCEPT row, and "EVERY latent-accept row"
gives 4.

(b) The new stated PCRE2-bug class `(?<=a(?(DEFINE)(?<=b+)))x` and
`(?<=a(?(DEFINE)(?<g>(?<=b+))))x(?&g)` (libpcre2 ACCEPT; pcrec refuses) are §6.2.5 cells that gate 3
neither excludes nor declares. Its "two DECLARED divergent classes" omit it, so EXTRA built
mechanically counts both as pcre2-only.

Fix: declare the DEFINE-bug class as a third declared class, counted on its own line. Then either pin
4 or exclude `(*ACCEPT)` by name with its reason. This is the "pin depends on a reading" defect again.

**DC-5. LOW. CONFIRMED by reading.** Step 1 ("One that no walk met is judged at its own turn") is
postresolve's pass. Step 5 says the parse hook judges at the outermost close "by the same walk". The
walk never enters a DEFINE on the length path, so at parse nothing says who judges a lookbehind
inside a DEFINE inside a parse-settled outermost (`(?<=a(?(DEFINE)(?<=b+)))x`, pinned refused).

Fix: step 5 adds "then every lookbehind in its subtree that the walk did not meet, ascending". With
that rule, `(?<=a(?(DEFINE)(?<=b+))c+)x` reports @0 (libpcre2 @0, HEAD @15). That is one more
stage-1 offset move, unlisted; add it to the stage-1 row.

**DC-6. LOW. CONFIRMED by hand trace.** §6.2.7 SV17's witness says "`((?<=\2))(a(?=(?<=\1)))` moves
from @1 to the second lookbehind's offset". Under the plant that is not what happens:
1. L1 passes, because the lookahead is skipped.
2. L2 enters group 1 and finds L1 already judged, so it skips L1.
3. L2 passes, and the pattern COMPILES.

It still goes red at gate 3, so detection holds. Fix the witness text to "compiles".

**DC-7. LOW. CONFIRMED by reading.** §0 G2 lists the refusal-only exceptions (G1's ceiling and the
lexical-bound class). It does not list the RDY-3 call twin `((?=(?<=(?2))))(a(?=(?<=(?1))))`, which
compiles today and is refused after V1. Gate 2's "newly-refused set ... (the lexical-bound class)"
leaves it out too. Fix: one clause in G2 and gate 2: the lookahead-nested call cycle, counted.

**DC-8. LOW. CONFIRMED by reading.** §6.2.2 step 3, "Every stop kind is covered by a row":
- The mapping omits the latent `(?|` stop (order 2).
- It omits a running-sum stop on a branch whose `hs` is unbounded, where order 4 is the first row.
  The invariant still holds, but the mapping sentence is incomplete.
- A variable or consuming-callout item has `hi` unbounded, so it trips "running `hi` passes 65535 at
  it" and stops the walk at the item (mapped to order 8). Step 2's last line puts rule 0 after the
  branches. The two disagree on pcrec-only cells such as `(?<=${v}(?<=c+))x`: rule 0 @0, or the
  inner @N? No oracle answers this; pick one and say it.

**DC-9. LOW. CONFIRMED by reading.**
- §6.2.1's "followed ONLY by the re-entry walk and the judging walk", and V1's "walked only by the
  re-entry and judging walk", read as two walks. §6.2.2 says they are one. S1454 re-anchors "to the
  re-entry query", which is now the judging walk.
- The walk's home is V1 (callgraph.c), but V3's parse hook calls it at parse with no table and no
  callgraph. State the entry point and its no-table form, in V1 and V3, so the two lanes' boundary is
  clear.

Checked and held:
- No stale post-order, inner-first, 65536, "No reader tells", `pcre2only=1` or closure-based re-entry
  sentence survives as a live claim. The ones left are in superseded REVISION blocks and the §16f
  history.
- The parse-time change contradicts no pin: no reject or .rxt row pins a nested stage-1 offset
  (grep).
- Every name the diff cites exists at main. One cosmetic point: rxt_compose.c's "structurally
  identical" quote spans :765-776.

## Design-level problems

None. DC-1 is the closest: read literally, the clamp misses `hi`. The fix is one bullet in §6.2.3 and
needs no new mechanism.

## Per-unit verdicts V1-V7

- **V1 the table: READY WITH TEXT FIXES.** DC-9 (one walk, its home and parse entry); DC-7 (G2/gate 2
  clause for the K-row cell V1 refuses).
- **V2 the scoped walk + mark: READY WITH TEXT FIXES.** DC-1 (the clamp covers `lo`/`hi`/`hs` in the
  lookbehind entries, and lives in §6.2.3).
- **V3 the rule + describe path: READY WITH TEXT FIXES.** DC-2 (per-branch running sums), DC-3
  (state the hold's G5 widening, pin one cell), DC-5 (parse rule for unmet lookbehinds), DC-8
  (mapping and rule-0 timing).
- **V4 spec: READY.**
- **V5 corpus and pins: READY WITH TEXT FIXES.** DC-4 (the pin's count and the declared DEFINE-bug
  class).
- **V6 checks: READY WITH TEXT FIXES.** DC-4, DC-6 (SV17 witness), DC-2's gate 7 group cell.
- **V7 D27: READY WITH TEXT FIXES.** DC-2's sentence in extract §2. The 2^40 promise stands once DC-1
  is fixed in the design.

## Probes run

Scratch: /var/tmp/pcrec-pcrec/scratch/vlbrev52/critic/ (p1-p3 .txt/.out; p1/p2 .head = pcrec
HEAD). 30 libpcre2 cells (ora2.py) and 24 pcrec HEAD single compiles (head.sh); no suite, no make.

Key results (libpcre2 / HEAD):
- Group running sums:
  - `(?<=a{30000}(?:a{40000}(?<=c+)))x`: 125 @23 / @23
  - `(?<=b{30000}\1)(a{40000}(?<=c+))x`: 125 @24
  - `(a{40000}(?<=c+))(?<=a{30000}\1)x`: 125 @9 / @9
  - `(?<=a(?:b(?:c{40000}(?<=d+))c{30000}))x`: 125 @20
  - `(?<=(?:a{40000}a{40000}(?<=c+)))x`: 187 @0 / @23
  - `(?<=a{30000}(?:a{40000}|b)(?<=c+))x`: 187 @0 / @26
- Hold cells:
  - `(a)(?<=\1(?<=c+))x\2`: 125 @9 / @9
  - `(a)(?<=(?1)(?<=c+))x\2`: 125 @11 / @11
  - `(a)(?<=\1(?<=c+)(?C1))x`: 125 @9 / @9
  - `(a)(?<=\1|(?<=c+))x\3`: 125 @10 / @10
  - `(?<=(?<=c+)(?|a))x`: 125 @4 / @4
  - `(?<=(?<=c+)a{2,1})x`: 104 @16 / 125 @4
- `(*ACCEPT)` row: `(?=(a(*ACCEPT)bc))\w+(?<=\1)x`: ACCEPT lb 1 / verbs module refusal.
- DEFINE:
  - `(?<=a(?(DEFINE)(?<=b+))c+)x`: 125 @0 / @15
  - `(?=(?<=a(?(DEFINE)(?<=b+))))x`: ACCEPT (the bug class again)
  - `(?<=a(?(DEFINE)(?<g>(?<=b+))))(?<=(?&g))x`: 125 @20 / @20
- Walk model, accepts: `(a(?(DEFINE)(?<=\2)))((?<=\1))`, `(?<=\3)(a(?<=\2))(b)((?<=\1))` (plus a
  trailing `(?<=\1)`) and `(a)(?<=b(?<=\1))(?<=\1)x` all ACCEPT, as the walk predicts.
- Walk model, refusals: `(a(?<=\2))(b(?<=\1))(?<=\2)x` is 125 @2, as the walk predicts.
- Clamp, stage 1: `(?<=(?:(?:a{65535}){65535}){65535}|b+)x` 187 @0 and its swapped twin 125 @0
  (reason K-row as stated); `(?<=(?:(?:a{65535}){65535}){0}x)y` 187 @0 / COMPILES (G4 class, stated).
- Hand traces, each matching libpcre2's offset: every §6.2.2/§6.2.5 cell of the RDY-1 and RDY-3
  rows, the re-entry and accept rows of §6.2.5, the DEFINE rows and the duplicate-name rows.
