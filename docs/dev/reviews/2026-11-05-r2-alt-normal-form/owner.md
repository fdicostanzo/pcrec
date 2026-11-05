# Critic lens `owner` — alt-normal-form (docs/design/alt_normal_form.md @ d202eae1)

Question: grade the note on Frank's 2026-11-05 criteria, in his order
(1 folds as alternations incl. alternation concatenation; 2 ASCII sets / UTF
tries-or-reductions; 3 byte result may stay; 4 kit hand-off stays SETS unless
a SIMD case is made; 5 VM decode-and-test not the target; 6 simplification is
a benefit), plus the goals question (§1 ranked, checkable?).
Compiles run: 9 single-pattern compiles on the review tree (no make, no suites).

## Findings

### OWN-1 — CONFIRMED — design — the owner cannot absorb altcls stage 2; "one owner" (G3, §3, §11) is false at stage 2b
- Where: §3 (the form: "width groups: unequal widths never share..."), §6 owner
  rule (1) "widths differ -> no merge", §5 stage 2b ("prefix AND suffix
  factoring, any identical capture-free factor as the key"), §2.2 merge (5).
- The owner's input is "capture-free, fixed-position literal branches" and its
  only rewrite is the one-position sibling merge inside a width group. altcls
  stage 2 (`src/opt/altcls.c` `altcls_branch_peel`/`altcls_extend_prefix`,
  lines ~180-250) peels a leading byte from ANY branch whose first atom is a
  single-byte class, whatever the rest (repeats, groups, unequal widths).
- Repro: `build/pcrec -e byte -p rx --pattern 'frank|fred'` -> `RX_ALTCLS_FACTORED 1`
  (widths 5 vs 4: owner rule 1 refuses); `--pattern 'frank|fr(?:x*)ed'` ->
  `RX_ALTCLS_FACTORED 1` (not fixed-position: outside the owner's input domain).
  altcls's own header example (`frank|fred` -> `fr(?:ank|ed)`, the measured
  -7.61% exemplar) is outside the owner.
- Consequence: either stage 2b keeps prefix/suffix factoring as a SECOND
  rewrite mechanism beside the owner (contradicting G3 "one owner" and §2.2's
  merge (5), and the note's "trie output" read by U3/U4 — see OWN-4), or it
  deletes the single-byte key as §5 says and loses altcls's measured win on
  unequal-width/non-fixed branches (G1 holds, but a byte-artifact regression
  with no D186 row to narrow). The note does not say which.
- Fix: define factoring (a common prefix/suffix factor, any width, any rest)
  as an owner rule in §6's table, with sibling merge as its one-position case,
  or state that factoring stays in altcls and drop merge (5) from G3's list.
- Severity design; effort small (note text) / medium (owner API); blast:
  every byte pattern with a factorable alternation.

### OWN-2 — CONFIRMED — design/doc — criterion 6 / G3: the "deleted" list is 1 real deletion out of 3; the "none added" claim is false (count: 1 deleted, 2 re-spelt, at least 6 added)
- Where: §1 G3 ("the special cases named in §2.2 deleted, none added"), §2.2.
- Against the code (review tree = main HEAD):
  - (1) `rr_alt`'s `o.all = false` (`src/facts/req.c` ~470-481). The note says
    its comment "calls the general case an unmeasured same-literal special
    case". It says the OPPOSITE: `all = false` IS the general fact ("these
    bytes are common"), and setting `all` for equal branches WOULD BE the
    special case, declined under D77 for an unmeasured population. Replacing
    it with §6's row 1 (every branch `all` AND equal untruncated width AND
    hull in domain) ADDS a three-condition row; nothing is deleted. The
    note must argue the D77 point the comment raises (stage 2's population
    "is NOT yet measured", §5 stage 2 Gates), not cite the comment as support.
  - (2) the seal in `lower_class_utf8` (`src/opt/lower_enc.c:369-384`): a
    REAL deletion (two nodes + comment). Held.
  - (3) `A_EMPTY` walked as an assertion (`req.c:698`): becomes its OWN arm
    returning `rr_unit`. A re-classification (arguably a bug-fix), not a
    deleted case; the switch gains an arm.
  - (4)/(5) "merged": (4) is real at stage 3 (two position spellings -> one);
    (5) does not hold as designed (OWN-1).
- Added by the note's own text, none in G3's ledger: owner rule (1) width
  groups; the `exact` obligation mode (rewrite vs facts, §3); `rr_alt` row 1's
  three conditions (§4.2/§6); stage 3m's affix-union rule (a second hull
  shape: union of FIRST/LAST positions across unequal groups, §4.5 — distinct
  from the equal-width hull); R2's census obligation and R3's second core
  fact (§4.4); the `info(S)` rounding row and the member-count bound that
  replaces `pos_set` (§4.4, §5 stage 3); altcls suffix factoring with "any
  identical factor" key (§5 2b). Several are general (fine under criterion 6
  as general rules), but G3 as written ("none added") is uncheckable-false
  and §2.2 overstates the simplification the owner is told he is getting.
- Fix: G3 as a two-column ledger (deleted/merged vs added, each with
  file:line), and drop (1) from "deleted" or re-argue it against D77.
- Severity design (the benefit claim criterion 6 is graded on); effort small.

### OWN-3 — CONFIRMED (text) / design — criterion 1's "considering alternation concatenation" is quoted once (line 14) and never designed; the owner sees ONE alternation at a time
- Where: §3 (owner input = one branch list), §4.1 (byte call inside
  `lower_class_utf8`, per leaf class, in-place splice), §4.5/stage 3m, §10.
  `grep -n concaten` on the note: one hit, the ruling's own quotation.
- What the design actually does with a concatenation:
  - fold next to fold (`(?i)αβγ`) and fold inside literals
    (`(?i)abcdÀefgh`): each class is lowered and reduced ALONE (the splice
    argument of §4.1 structurally forbids the byte-level owner from seeing a
    neighbour); the concatenation is composed only by `req.c`'s `rr_cat` in
    the FACTS, after stage 2/3 lets an alternation be `all`. That is a
    defensible answer — but the note never states it as its answer to the
    criterion, never says rewrites (tables, G5) get no cross-alternation
    reduction, and never says why that is enough.
  - concatenation THROUGH an unequal-width alternation (the case where
    concatenation matters most: the run must cross the alternation): only
    stage 3m's ONE affix byte each side. The per-group runs that distributing
    the neighbours into the groups would give are deferred "until
    [SEQ-FOLD] needs more" (§4.5). But the population is simple-fold, here
    now, and on the bench: `ci-moskva` = `(?i)москва` (о, с, в mixed-width
    via U+1C80-1C83), `ci-kelvin` = `(?i)k`, `ci-long-s` = `(?i)s`, 37 classes
    by the note's own count. Today: `-e utf8 (?i)москва` -> `RX_REQ_RUN "none"`,
    `(?i)xk` -> `"none"` (measured). Stage 3m gets ci-moskva to 4 of 12 bytes.
    The trigger is assigned to the wrong row: [SEQ-FOLD] (1:n full folds) is
    not what blocks these cells; they are criterion 1's concatenation case.
- Fix: a §3 paragraph "concatenation": state that the owner's unit is one
  alternation, that concatenation is composed by the facts walk (rr_cat over
  `all` alternations / affixes), and either design the per-group run across a
  mixed-width alternation (a concatenation of length groups = its own small
  width-group product) or give it its own trigger on `ci-moskva`'s numbers,
  not [SEQ-FOLD]'s.
- Severity design; effort small (text) / medium (per-group facts); blast:
  every caseless utf8 pattern with k, s, о, с, в, ... (37 classes).

### OWN-4 — CONFIRMED (text) — design — criterion 2's "tries" are named but never produced; readers are wired to a "trie output" the owner does not have
- Where: §3 owner definition (output = "width groups, each a list of merged
  branches, plus each group's hull"); §6 rule table (sibling merge only);
  §3 relation table row "VM island, string-set fact | readers of the owner's
  trie output"; §9 U4 ("read from the owner"); §2.2 (7).
- Sibling merge collapses one-position differences; it never shares a
  PREFIX, so its output is not a trie (`ce [92 b2] | cf 90` is two flat
  branches). The only prefix-sharing rewrite in the tree is altcls stage 2,
  which the owner cannot express (OWN-1). For UTF-8 — where Frank named
  "tries or other reductions" — the note delivers the "other reduction"
  (sibling merge + hull) and silently drops the trie, while U3/U4 presume it.
- Fix: either add prefix factoring as an owner rule (then its output IS a
  trie with set edges, and OWN-1 closes too), or re-word U3/U4 and the
  relation table to read width groups, and say in §1/§3 that tries are not
  produced and why criterion 2 is still met.
- Severity design; effort small (text) or folds into OWN-1's fix.

### OWN-5 — CONFIRMED (text) — design — §4.6's evidence bar presumes a kit method (D157) and is a build-before-the-case bar stricter than criterion 4
- Where: §4.6 items 1-3, "Folds alone never make the case", §9 U3.
- Criterion 4: the hand-off stays sets "unless a case is made that something
  richer lets SIMD do better". The note:
  - item 2 requires "a kit kernel of the F10 class" to EXIST and beat the
    sets kit; F10 is `find_multi (Teddy class)`
    (`docs/design/memfn/requirements.md:145`). Naming the kernel family the
    fact must serve is presuming the kit's method — what D157 ("pcrec states
    FACTS and the kit chooses FORMS ... implies no use of them") forbids in
    fields, briefs and design text. It is also circular: the kit cannot build
    and measure a kernel consuming a fact pcrec does not send. D157's own
    precedent ships a fact inertly ("zero pcrec movers ... until a kit row
    consumes it"); the note does not consider that route.
  - all three conditions are REQUIRED, including scalar AND SIMD each against
    its bar; Frank's criterion is a case for SIMD. A SIMD-only win (D186
    add. 2 C9: a SIMD build may pick its own form as its own choice row) would
    fail the note's bar.
  - "Folds alone never make the case" pre-judges the evidence the same
    section defines, and contradicts its own preceding sentence that
    mixed-width folds are exactly where a string set carries correlation
    the per-position sets lose (k/K/K, OWN-3's population).
- Fix: state the case as pcrec-side facts only (item 1: the hull's candidate
  rate vs the string set's rate on a bench cell, measured from text), hand
  the kit the question via a request (the kit decides whether a form
  exists), drop "F10/Teddy" from the bar, drop "folds never", and let a
  SIMD-layer-only win qualify as criterion 4 says.
- Severity design; effort small.

### OWN-6 — CONFIRMED (text) — design/doc — goals: ranked, mostly measurable, but four are not checkable as written and one stage is mis-kinded
- G2 "stage 1 moves ZERO byte-encoding artifacts (emit diff empty)":
  CHECKABLE in principle (Gate B0; see PROBED-AND-HELD), but the population
  "every corpus and bench pattern compiled -e byte" does not say whose flags
  (.rxt options/encodings) and what to do with patterns `-e byte` refuses
  (e.g. `(*UTF)` -> "requires --encoding=utf8"). Name the pattern list
  generator and the options source, as K35 requires of a counted population.
- G2 "each stage meets its declared kind's bar": stage 1 is declared a UNIT
  change, yet its own Gate U4 predicts a scan-pick flip (`ci-greek-run`
  offset-set -> handoff). Under D186 which-unit-is-used-where is a CHOICE;
  a losing regime is answered by narrowing a row, and stage 1 has no row
  to narrow (only revert). Declare stage 1's utf8 effect as feeding the
  choice table and say what narrows on a loss.
- G4 says "at least 766 after stage 1"; Gate U2 says "= 766 exactly". Pick
  one (the exact form is the stronger control; the goal should match it).
- G4 has no number after stage 2, and stage 2 has no predicted-mover set
  ("population is NOT yet measured ... first deliverable"), unlike every
  other stage — stage 2 is the one stage built ahead of its measurement
  (D77, the very ground the `rr_alt` comment declines it on).
- G5 "no utf8 mover's DFA next-state table grows" vs Gate U3 ("growth is a
  finding to explain") and §8 (k/s table direction "not predicted", cause of
  the 60-72 vs 48 discrepancy "not traced"): `ci-kelvin`/`ci-long-s` are
  predicted movers with no G5 verdict possible. Trace the discrepancy before
  the goal is stated as checkable.
- Order vs Frank's: G3 (one mechanism) sits above G4/G5 (the fold payoffs);
  defensible since G3 carries criterion 1 as well as 6, but given OWN-1/2
  G3 is the goal the design currently misses.
- Severity doc/design; effort small.

### OWN-7 — CONFIRMED (text) — doc — §2.2 (8) cites "§6's affix facts"; §6 has none (they are §4.5 / stage 3m)
- Severity doc; effort trivial.

## PROBED-AND-HELD

- Criterion 3 / G2 premise: stage 1 cannot reach `-e byte`. `lower_ops[]`
  dispatches per encoding and `(*UTF)` under `-e byte` refuses the compile
  (probe: `pcrec -e byte --pattern '(*UTF)(?i)é'` -> "(*UTF) requires
  --encoding=utf8"); the emitted header carries version + abi only, no
  commit/build stamp (`/* Generated by pcrec 0.2.0-beta (abi 95) ...`), so a
  base-vs-stage emit diff is a meaningful, independent control. 2 compiles.
- Criterion 2 (ASCII is sets): `lower_class_utf8` returns NULL for an
  all-ASCII class before any branch building (`src/opt/lower_enc.c` ~330), so
  ASCII stays a class/set under utf8. Held by reading.
- Criterion 5: the VM decode-and-test is a stated non-goal (§1) and no stage
  edits it; the VM only sees the lowered byte child under `-fno-cls-kit`,
  which stage 1's `make test-axes` gate names. Held by reading.
- Criterion 6, seal: the `A_CAT(A_EMPTY, alt)` seal and its "redundant since
  K123 ... stays because ... abi event" comment exist as described
  (`lower_enc.c:369-384`). Real deletion.
- §4.2 "superset hulls already exist": `frank|fred` -> `RX_REQ_RUN
  "667261@0/fffffb"` (f, r, [a e]) — a position holding a byte one branch
  never has. Held. 1 compile.
- §2.1/§5 2b non-composition: `(?:ab|aB)xy` -> FACTORED 1, MERGES 0, run 3
  positions; `a(?:b|B)xy` -> MERGES 1, run 4. Held. 2 compiles.
- §5 stage 3m / OWN-3 premise: `-e utf8 (?i)xk` and `(?i)москва` both
  `RX_REQ_RUN "none"` today. Held. 2 compiles. `-e byte xk` -> `786b@0`.
- Bench cell identities: ci-moskva `(?i)москва`, ci-greek-run `(?i)αβγ`,
  ci-kelvin `(?i)k`, ci-long-s `(?i)s`, ci-strasse `(?i)straße` (read-only
  from pcrec-bench/bench/utf8/patterns). Held.
- Criterion 4 headline: §4.6 and §11 keep the hand-off as SETS (D187
  positions as sets). Held as a decision; its evidence bar is OWN-5.

Total compiles: 9.

END OF FINDINGS
