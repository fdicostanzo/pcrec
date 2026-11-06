# crit-vlb2 lens `ready` — stage-1 build readiness of docs/design/vlookbehind.md rev 1

Subject: R/subject_vlookbehind.md (rev 1, bc9d1eb8f), cited as §/line of that copy. Review tree:
worktrees/crit-vlb2 at 7ddfbfa95 (all code cites below are file:line there). Rulings read at the
freeze (`git show 7ddfbfa95:docs/dev/{decisions,plan}.md`). Oracle: libpcre2-8 10.46 as a library
(R/tools/oracle_probe, plus my own `ready/mv0.c`, which compiles with `max_varlookbehind = 0`).
pcrec compiles: about 40, all under nice -n 19.

## Findings

### READY-1 — the cost pass under-sizes the trail for a `range` branch: give-up where libpcre2 answers (CONFIRMED; answer; both A and B)
- **Where:** §5.1 (lines 318-356), §5.1b's "Slot allocation"/"push count" bullets (lines 426-430), §5.5 "Frames"
  (lines 657-664). The code is `vm_cost_look`, src/gen/emit_vm.c:2858-2864: `c.trail += 2;`, a constant
  that its header calls "EXACT for the positive ATOMIC form" (lines 2834-2844).
- **Defect:** in the `range` row every candidate writes `D_i` with `VK_SET`: once at entry, then one
  decrement per retry. The design says correctly that `RX_SET` always trails (emitted `RX_SET` →
  `RX_TRAIL`, which checks `trail_depth >= trail_cap` and otherwise returns `RX_R_FRAMES`).
  - A pop rewinds only to the frame's mark, which sits ABOVE `D_i`'s latest entry. So one branch
    evaluation leaves up to (hi_i − lo_i + 1) live trail entries.
  - `RX_CUT` discards frames, not trail entries (header at emit_vm.c:2843), so the entries outlive the
    assertion.
  - The design never mentions `vm_cost` or trail sizing (grep of the subject for `vm_cost|trail
    capacity|TRAIL`: none).
- **Why it bites:** for a statically bounded pattern the emitter sizes the trail EXACTLY from
  `vm_cost` (limits.md §3.2¶1). Measured today: `(?<=a{3}|b)x` emits `#define RX_TRAIL_FRAMES 4` and
  `RX_FAST_TRAIL 4` (ready/y.h:271).
  - A literal build of §5.1 gives `(?<=a{1,255}|b)x` the same +2 charge. On `b`×300 + `x`, branch 0
    writes `D_0` 255 times before branch 1 matches, so it returns `PCREC_ERR_FRAMES` where libpcre2
    matches.
  - The tier cannot rescue it: the stamped default IS the 4-entry size.
  - Smaller cells hit it too: W2 (`(?<=a{1,2})x` on `abx`: 2 look slots + 2 `D` writes, plus the
    pattern's own entries) is at or over a 4-entry trail. So a correct-by-design build would fail its
    own witnesses or gate 1 (as give-ups, not wrong answers).
- **Fix (text, small):** §5.1b/§5.5 add the cost-pass row: `vm_cost_look` charges
  `+ Σ_range (hi_i − lo_i + 1)` trail entries, plus the frame count it already over-charges
  (`1 + nbranch` stays ≥ exact, since a `range` last branch pushes `L_adv`).
  - Name `vm_cost_look` beside `vm_count_slots_look` as the two passes that must agree with the emitter.
  - Add a sabotage row that drops the term: a give-up on W2's cell.
  - G4 should state the trail bound beside the frame bound.
- **Effort:** one line plus a comment and a witness. **Blast radius:** only artifacts with a `range` branch.

### READY-2 — G1's accept-set clause and gate 3 have a SECOND exception class the design does not name (CONFIRMED; design; both)
- **Where:** §0 G1 (lines 64-77) says the clause is false today only through the 65535 ceiling, which
  "Stage 1 restores". §6 gate 3 (lines 727-737) requires 0 exceptions, plus the classification
  control "pcrec's one-length judgment = libpcre2's accept at `max_varlookbehind = 0`".
- **Evidence (libpcre2 10.46):** a lookbehind containing an UNBOUNDED repeat of a zero-width body is
  refused with err 125, at the default AND at 0.
  - Refused: `(?<=(?:)*a)x`, `(?<=(?:\b)*a)x`, `(?<=(?:)+a)x`, `(?<=(?:(?=b))*a)x`, `(?<=(?:a{0})*b)x`
    and `(?<=(?:)*a|bc)x`.
  - Bounded twins are accepted (`(?<=(?:){2,5}a)x`, `(?<=(?:\b){0,3}a)x`). Evidence: ready/zw.txt,
    `oracle_probe c` and `ready/mv0`.
  - pcrec compiles `(?<=(?:)*a)x` and `(?<=(?:\b)*a)x` TODAY as one-length (ready/shapes_pcrec.out).
    That is by design: mrl.c:660-666, "a lookbehind branch made of them is legitimately fixed-width".
- **Consequence:** gate 3's "0 exceptions" and its classification control go red on a CORRECT stage-1
  build as soon as the gate-1/3 generator crosses "nested lookaround" or "bounded quantifier" with an
  unbounded zero-width repeat. G1's measurable also stays false after stage 1.
  - Nothing in the population uses the class (corpus grep: none). It is a gate-design hole, not a
    demand item.
- **Fix (text plus a manager choice; answer-free for every pattern in the corpus):**
  - (i) Keep accepting. This is the design's own §5.2 reading of D26's addendum: accepting more is not
    a defect. G1 and gate 3 then name the class as a stated divergence, with its cells counted on
    their own line (gate 1's D142 pattern).
  - (ii) Refuse it. That is a second G1-over-G2 exception, and `pcrec_cwmax`'s A_REP arm changes.
  - Leaning (i): (ii) refuses patterns that compile today, for no user.

### READY-3 — gate 2's home is unnamed, and the existing identity gate goes RED on the flips by construction (CONFIRMED; maintenance; both, worse under B)
- **Where:** §6 gate 2 (line 725): "Every corpus artifact containing a lookbehind is byte-identical".
  §13 Q1(B) (line 1010) counts "826 lookbehind lines in 40 `.rxt` files feed the identity gate".
- **Code:** tests/codegen/run_recursion_identity.sh compares every call-free corpus pattern
  whole-file against `$FILEPIN` (B) and by program region against `$ABASEPIN` (A).
  - A pattern accepted by one build and refused by the other is a hard FAIL (lines 2163-2166:
    "`$mism` call-FREE patterns are accepted by one build and refused by the other").
  - Stage 1 flips 24 distinct call-free corpus patterns from refused to compiled under EITHER answer
    (population.tsv, the `B_loop=yes` rows). So the gate is red on the landing commit until it is
    re-pinned, and that re-pin is not an abi bump under (A).
  - run_lookaround_identity.sh (default `STRICT_ALL=0`) compares only the lookaround-FREE bucket. It
    does not carry G2 at all.
- **Fix (text):** gate 2 names its instrument and procedure.
  - Run run_recursion_identity.sh against the pre-landing pins.
  - Require `differing = 0`, and `refusal-mismatch` = EXACTLY the flipped set (a manifest counted
    from population.tsv, K35).
  - Then re-pin FILEPIN/ABASEPIN in the landing's own commit, the gate's documented "moves on
    purpose" route.
  - Under (B), the same re-pin carries the abi number, and the `differing` population is every
    lookbehind artifact.

### READY-4 — the new `D_i` slot family has more readers than "the count pass" (CONFIRMED by grep; maintenance + doc/spec; both)
- **Where:** §5.1b "Slot allocation" (lines 426-428) names only `vm_count_slots_look`. §5.6 (lines
  667-689) maps the records.
- **The slot-family readers in emit_vm.c**, each of which a new family must join:
  - the slot naming function (`SLOT_LOOK_POS%d`, :1079-1085);
  - the base-offset chain (:1213, :10611-10633, the `*_total` resets);
  - `VmSnap`/`vm_snap` (:7566-7579) and the W builder's per-family `vm_w_range` calls (:7802-7820);
  - the listing (`vm_listing_slots`, :9857).
- **Spec reader, a D80 hunk §10 omits:** docs/spec/ir_listing.md §3.2¶2: "`family` is a fixed
  vocabulary, append-only: `group`, … `lookmark`, `lookpos`". The new family needs an appended name
  there.
  - `vm_listing_slots` prints a "none" row for an empty family (:9493-9495). So if the family is
    listed unconditionally, EVERY VM listing moves, including the 18 baselines in
    tests/codegen/manifests/ir_listing_baseline/ (run_ir_listing.sh:593).
  - G2 covers artifacts, not listings, but the baselines are readers. The design should choose
    between "listed only when non-empty" and "re-baseline".
- **W disposition:** S153's header (tests/mech/sabotages/S153_w_drops_look.sh:11-16) states the house
  rule that W is "every family … rather than a list somebody curated". By my trace, `D_i` needs no W
  entry for correctness: every read follows its own `VK_SET` in straight-line code, or follows a pop
  that rewinds the trail. But the design must SAY which choice it makes. Either it joins W (the rule),
  or the exclusion is argued at `vm_w_range`.
- **Fix:** list these readers in §5.1b and add the ir_listing.md hunk to §10.

### READY-5 — sabotage rows that move are under-listed; S136's re-aim must name its branch (CONFIRMED by trace; test; both)
- **Where:** §7 "Existing rows that move" (lines 840-863).
- **S-U4 is missing.** tests/mech/sabotages/S-U4_width_rule_byte_units.sh sets `pcrec_cwmax(A_CLASS)`
  to 4. Its stated detector is that every class-bearing lookbehind REFUSES (`SAB_DOC_FIGURE`), in
  suites `harness lookaround`.
  - After stage 1, `(?<=a)x` becomes `range` [1,4]. Candidates 4..2 fail the end-check, and candidate
    1 answers as today. Captures and answers are identical, so the refusal-based detector is gone.
  - Only the identity gate (READY-3; not in its `SAB_SUITES`) or gate 3's classification control
    would see it.
  - Fix: re-aim S-U4 to gate 3's suite and update its figure. SUSPECTED residual: another `cwmax`
    consumer may still turn some cell red. Confirm by running the row.
- **S136 re-aim (lines 845-858)** says "the STORED one-length pair of ONE branch becomes K+1 at both
  ends". Both cells discriminate only if the sabotaged branch is `bc` (branch 0), or every branch.
  - Trace: with only `d` sabotaged (k=2), the positive `(?<=bc|d)x` on `abcx` still matches through
    `bc`. The negative `(?<!bc|d)x` on `bcax` holds: `d` from 1 reads `c` and fails, and `bc` from 1
    reads `ca` and fails. Both cells stay GREEN.
  - The natural edit (la_widths' loop, which is today's S136 anchor) sabotages every branch, which
    works. Say "every branch, or branch 0, never only the last".
- **Under (B) only:** S133/S134/S135's `SAB_BEFORE` anchors (`pcrec_vm_b_seek(v->sb, VSK_BACKSTEP,
  NULL, k)`, the `BACK_STEP_NONE` branch, `if (k > 0)`) sit in the code (B) rewrites. Their re-anchor
  belongs in the unit's list.

### READY-6 — §10's reader list misses the D27 extracts and D27-owned corpora, and a prior RULING is reversed unstated (CONFIRMED by grep; doc + ruling; both)
- **Missing readers** of the "variable-length lookbehind is refused" rule (grep of the review tree
  for the refusal text and "fixed length"):
  - docs/design/la_d27_extract.md:157,171,225,323. Its G2 row tells the blinded author "pcrec REFUSES
    these too … must not write a match expectation".
  - docs/design/sr_d27_extract.md §3.4(d) (lines 341-377).
  - The D27-authored corpora tests/lookaround/d27/{gen_refusals.py, refusals.rxt (18 of the 76
    probed rows), spellings.rxt}.
  - tests/recursion/d27/{sr_interactions.rxt:233-246, sr_wrapped.rxt}.
- docs/design/CLAUDE.md: extracts are "regenerate ONLY by re-cutting from the source". The design
  plans a NEW `vlb_d27_extract.md` (§9). It does not say that the two existing extracts must be
  re-cut, nor who flips D27-owned cells and generators (a blinded author's files).
- **Ruling reversed:** sr_d27_extract.md:356-371 records the **[DD-14.LB] amendment (2026-08-24) "as
  a RULING"**. Its second bullet reads "a single call that is the lookbehind's one top-level branch,
  whose callee has different fixed widths, is REFUSED by pcrec even though PCRE2 accepts it".
  plan_completed.md [DD-14.LB] calls it "a RULED perr (tier 2)". The test is
  `^(?(DEFINE)(?<g>a|ab))ab(?<=(?&g))$`, which libpcre2 accepts with maxlookbehind 2 and which flips
  at stage 1 (population.tsv, two rows).
  - The ruling was a consequence of the missing loop, so reversing it is right. The design should
    still name it as superseded (§10 / §13.3) so the extract and corpus comments move with it.
- **Fix:** add these readers, the re-cut of both extracts, and the owner of the D27-file flips to §6
  stage 1 and §10.

### READY-7 — stage 1's scope says "36 rows flipped"; the design's own §8 says 32 (CONFIRMED; doc; both)
- §6 stage 1 scope (line 703): "the 36 real corpus rows flipped". §8 (line 871): "Stage 1 covers
  32 rows (24 distinct)".
- population.tsv: rows with `B_loop=yes` sum to 32 (24 distinct). The 4 backreference rows
  (`(a)(?<=\1)x` ×2, `(a|bc)(?<=\1)x` ×2) are stage 2 (owner ruling 3).
- Fix: "32 rows (24 distinct); the 4 backreference rows stay refused until stage 2".

### READY-8 — the two `limits.def` rows are not spelled in the table's own vocabulary (CONFIRMED; doc/maintenance; both)
- **Where:** §5.2 (lines 509, 517) and §10 (lines 917-922).
- **Names:** `lookbehind_branch_max` / `lookbehind_var_max` are given lowercase. limits.def's `name`
  column is "the C symbol, spelled exactly as it appears at its use sites" (src/core/limits.def:20).
  Home: `MOD_LOOKAROUND`, beside `LA_MSG_MAX` (:424).
- **Kind:** "a LANGUAGE limit" (line 921) is not one of the five kinds in limits.def's closed list
  (:45-56). Its readers move with a new kind: that header, and the legend printed by
  src/dump/limits_dump.c:93.
- **Readers of the listing:** tests/registry/limits_check.sh's `EXPECT_NAMES` manifest and its
  "all 78 named rows" count (:97-180). Also its anchored-value arm, which looks for the value
  COMMA-GROUPED in the section text (`group()`, :192-198). §3.11 must therefore write "65,535", not
  "65535".
- The old `hi > INT_MAX` arm ("this lookbehind is too long", mod_lookaround.c:382-383) becomes
  unreachable under the 65535 ceiling. Say "deleted" (and fix the LA_MSG_MAX length comment,
  :349-353).

### READY-9 — "shape 7" does not describe a length limit (CONFIRMED; doc; both)
- pattern_language.md §2.4's table defines shape 7 as "grammar | a PCRE2-like sentence | the pattern
  is not well-formed; PCRE2 refuses it too".
- §5.2 (lines 550-563) puts the cap and the ceiling there. The design's own §10 calls them a limit
  with a `limits.def` row and owner ruling 1 calls the cap POLICY, so they are not "not well-formed".
- Fix: the §2.4 hunk widens shape 7's "means" cell ("…or over a PCRE2 length limit"), or the hunk
  states why not.
- §2.4¶2's courtesy (follow PCRE2's wording where pcrec has one) is available for all three sentences.
  That is D26 tier 3, so it is optional.

### READY-10 — four cites that do not hold (CONFIRMED; doc; both)
1. **Gate 1 (line 707)** says "PC-3's harness". PC-3 is tests/registry/pcre2_check.c, the REGISTRY
   compile check against libpcre2, not a match differential. The lookaround match differential
   against libpcre2 (every startpos, every group span) is tests/lookaround/run_lookaround_diff.sh.
   Name it, or name a new section in it.
2. **§14 (line 1041)** cites match_api.md §6¶19 for "no bump is owed when no previously compiling
   pattern moves". §6¶19 is "what is fixed within one abi". The bump rule is §6¶18 ("any change to the
   emitted scaffolding for identical inputs").
3. **§5.2 (lines 559-565)** retires the "free" over/under-estimate premise only in `la_widths`' comment.
   The same premise is the stated contract of `pcrec_cwmax`'s header (src/opt/mrl.c:508-520, "This
   function may OVER-estimate for free") and of `pcrec_cwmin`'s header. Stage 1 must correct both
   headers, not only the A_BREF sentence that stage 2 changes.
4. **Stage 2 (line 760)**: "[branch-reset] lands". `branch-reset` is a MODULE name
   (pattern_language.md §8.1 table), not a plan row. There is no `- [branch-reset]` row in plan.md at
   the freeze.

### READY-11 — goals and ruling check: two unstated dependencies (CONFIRMED; design/plan; both)
- **G1 depends on owner Q2, not only G2 on Q1.** §0 says only G2 waits on an owner answer (lines
  78-83). G1's measurable (0 accept-set exceptions "plus the boundary cells of both limits", lines 68-71)
  holds after stage 1 only if the 65535 ceiling RIDES stage 1. If Q2 gives the ceiling its own row,
  G1's measurable is false at stage 1's landing. Say so in §0 and in gate 3.
- **Owner ruling 1's deferred item has no home row.** The `max_varlookbehind` setting waits for
  [IFACE-PUSH] (§5.2 line 530, §13.3), but the frozen [IFACE-PUSH] row (plan.md row [IFACE-PUSH] and its
  continuation lines) never mentions lookbehind. The manager files it there when stage 1 lands
  (PLAN), or the deferral has no trigger.
- [LB-EXIST] IS filed as the design says (plan.md row [LB-EXIST]): HELD in its status line, trigger "a
  real pattern needing unbounded or over-255 lookbehind, from the [UTF-RW] harvest or a user", refs
  D156/D77, the O(n³) and oracle notes. Held.

## Per-unit verdicts

The units, in a landable order:
- U0 first.
- U1a may land alone, before or after the rest (owner Q2).
- U1b, U2, U3, U4, U5, U6 and U7 are ONE landing. They cannot be split across commits that reach
  main:
  - U1b without U2 stores pairs that the emitter reads as `int` (emit_vm.c:7122).
  - U2 without U1b is unreachable.
  - U5, U6 and U7 must ride in the same change (D80, the corpus ratchet, the S136 premise).
  - WIP commits inside the lane are fine.

| unit | (a) cites at 7ddfbfa95 | (b) witnesses can fail | (c) separable / order | (d) readers complete | verdict |
|---|---|---|---|---|---|
| U0 stage 0: D27 extract + author | `tests/lookaround/d27/` exists; the docs/design/CLAUDE.md extract rule holds | n/a (the author writes cells) | first; independent | NO: the two EXISTING extracts (la_, sr_) also need a re-cut, and the D27-owned corpora need a named owner (READY-6) | ready with text fix |
| U1a the 65535 ceiling (refusal only) | `la_widths` and its three arms hold (mod_lookaround.c:293-387); oracle boundary cells hold (W9b, 8 cells) | W9b reaches: pcrec compiles all four ceiling cells today, so a missing ceiling is red | separable (refuses only, moves no bytes); Q2 decides whether it rides | NO: limits.def name and kind, limits_check manifest, comma grouping (READY-8) | ready with text fix |
| U1b the width pair + the 255 cap + refusal texts | `u.look.widths` has two readers (emit_vm.c:7122, mod_lookaround.c); `la_lb_raise` takes the widest max; the K127 `recurses` arm shares `la_width_refusal`; deferral via `pcrec_has_call`/`fix_widths` holds | W8, W9 reach (oracle: 200 at 256, accept at 255, UTF é{1,255}/{1,256}) | with U2 | NO: mrl.c's "free" headers (READY-10.3); the zero-width-repeat class (READY-2); shape-7 wording (READY-9) | ready with text fixes |
| U2 the loop + emission table | `vm_look_behind_branch` order (guard, push, work, back-step, sentinel) holds (:7117-7243); `VK_SET` trails; `VK_SEEK` has `slotx` (vm_stmt.h:224); `VSK_BACKSTEP` renders a literal; `VK_WORK.count` is a string; "fixed width %d" is listing-only (checked in emitted C) | W1, W3, W3b, W5, W6, W10, W11 traced: each red under its sabotage and green under §5.1 (READY PROBED below) | core; lands with U1b | NO: `vm_cost_look` trail (READY-1, answer level); slot-family readers, W, ir_listing.md (READY-4) | ready with text fixes (READY-1 is mandatory) |
| U3 end-check split | negative arm `RX_R_INTERNAL` site (:7225-7237); match_api §4¶6 still names `pcrec_maxw` (stale, as the design says); D72 is the D-row behind INTERNAL and agrees | W4 red/green by trace (`(?<!ab?)x` on `acx`); S136 re-aim reaches INTERNAL only if branch 0 is sabotaged (READY-5) | part of U2's `range` row | yes (the INTERNAL producer has one site) | ready with text fix |
| U4 budgets / gate 4 | `RX_CHARGE_WORK` skips n ≤ 0; 1e9/32,640 = 30,637 ≥ 30,600 holds; limits.md §3.1¶2 holds | gate 4 is a measurement, not a witness | with U2 | NO: trail capacity missing from the budget story (READY-1) | ready with text fix |
| U5 spec hunks + refusal-text readers | pattern_language §7.4¶5, §9¶2, §7.11¶3, §7.3¶5/¶6, §2.4 shapes 5/7; limits.md §3 (3.11 free); match_api §4¶6, §9.4¶2, ¶8 all exist | n/a | same change as U1b/U2 (D80) | NO: ir_listing.md §3.2¶2 (READY-4); §6¶18 not ¶19 (READY-10.2); D27 extracts (READY-6) | ready with text fixes |
| U6 corpus rows flipped | population.tsv holds | each flipped row becomes a match cell against libpcre2 | same change | NO: 32 not 36 (READY-7); run_recursion_identity.sh refusal-mismatch re-pin (READY-3) | ready with text fixes |
| U7 sabotage rows / S136 re-aim | S136/S133/S134/S135 anchors read; S-U4 read | W1-W11 OK; S136 OK only for branch 0 or all branches; S-U4 loses its detector | same change as U1b | NO: S-U4 (READY-5); under (B), S133-S135 re-anchors | ready with text fixes |
| U-gates: gate 1 / gate 3 | gate 1's harness is mis-cited as PC-3 (READY-10.1) | gate 3's classification control is red on a correct build if the generator spells `(?:\b)*` in a lookbehind (READY-2) | n/a | n/a | ready with text fix + one manager choice (READY-2) |

### Overall verdict
- **Under owner-Q1 answer (A): READY WITH LISTED TEXT FIXES** (READY-1 to READY-11).
  - READY-1 is the one a literal build would get wrong: a give-up instead of an answer on new
    artifacts.
  - READY-2 needs a one-line manager choice. Leaning (i): keep accepting and name the divergence.
  - None needs a redesign or another critic round. A diff check of the edited sections is enough.
- **Under answer (B): READY WITH LISTED TEXT FIXES, plus the (B)-only items:**
  - the abi event's readers, found by grep at landing. At the freeze they are match_api.md §6¶17,
    tests/codegen/{run_codegen_tests,run_recursion_identity,run_facts_checks,run_cpset_structure}.sh
    and tests/mech/sabotages/S693_abi_not_bumped.sh;
  - the FILEPIN re-pin carrying every lookbehind artifact (READY-3);
  - S133-S135's re-anchors (READY-5);
  - the per-site back-step count fixtures re-measured (unchanged count, moved text).
- Either way the build go waits on owner Q1, which the design says is open. G1's measurable also
  waits on Q2 (READY-11).

### Stage 2 as a FUTURE unit (not blocking stage 1)
- **Cites hold:**
  - `pcrec_has_call` and the deferral (mod_lookaround.c:591-620);
  - `pcrec_lookaround_fix_widths` via `pcrec_postresolve` (postresolve.c header);
  - the mrl.c A_BREF sentences ("answers 0 EXACTLY", :534; "never fixed-width — which is the answer
    libpcre2 gives too", :540), both refuted at 10.46 as the design says;
  - the A_CALL memo `u.call.cwmax_known` (mrl.c:625-627).
- **Re-probed acceptance-table cells, all as tabled** (12 cells): varying back-ref, cap through a
  fixed group, before-its-group, `\g{+1}`, unset group, numbered reference to a duplicate name,
  by-name reference to a duplicate (125), `(?|` anywhere (125), recursive group (125),
  self-reference (125), `{1,256}` group (200), inside `(a|bc)\1` lb 4.
- **One cite slip:** "[branch-reset] lands" (READY-10.4).
- **Readiness:** the per-group memo and the deferral widening are designed in text only. The stage
  needs its own §10 hunk set (§7.3¶5/¶6, §9¶2's second clause), which the design lists.
- **READY-2's class recurs:** a reference to a group under an unbounded zero-width repeat. Fold it
  into the same choice.

## PROBED-AND-HELD
- **Oracle answers** of every stage-1 witness and boundary cell: 13 match cells (W1-W5, W10, W11a/b/c,
  W3b, S136 ±, F1's three), 1 UTF cell (W6), 11 compile cells (W8, W9, W9b ×4, the cap pair through a
  fixed branch, UTF é{1,255}/{1,256}). All equal to the design's stated answers.
- **The ceiling** counts characters under UTF (`é{65535}` accepted, `é{40000}` accepted). Nested
  lookbehinds are not summed (3 cells). The cap is not triggered by a nested varying lookbehind or
  lookahead (4 cells). Matches §5.2's rule text.
- **pcrec compiles today** all four ceiling cells (sizes 23-35 KB), so W9b's "compiles" halves are
  reachable on a correct build.
- **The "one length" judgment vs libpcre2 at `max_varlookbehind=0`:** 24 shapes (ready/shapes.txt).
  - It agrees on every shape both compilers can parse, except the zero-width-repeat class (READY-2).
  - Shapes pcrec refuses for other reasons (`\R`, `\X`, `(?#`) are out of the population.
- **§5.1c's four hand-executions re-done literally:** all hold. The sentinel path pops `L_adv_i`.
  Exhaustion of a non-last `range` branch reaches `L_b_(i+1)` at the cursor. The last branch's
  exhaustion is `rx_fail` (for `(?<!`, the `L_neg_ok` pop).
- **Possessify does not enter lookaround bodies** (possessify.c:997, :1856), and `vm_count_slots_look`
  passes `under_atomic = false` (the lift is not applied). So W3b's correct build keeps the body's
  give-back frame. Held.
- **`D_i` needs no W entry for correctness** (trace in READY-4). Only the disposition text is owed.
- **Plan and decision rows the design relies on exist at the freeze:** [VLOOKBEHIND], [LB-EXIST],
  [ENG-LOOK], [GIVEUP-DIFF], [UTF-RW], [IFACE-PUSH], [VMREC], [CTX-PREFILTER], [CONDITIONALS],
  [LANDWALK-ALLACC]/[LANDWALK-VM] (referenced). Also D26, D42, D58, D76, D80, D94, D142, D153, D156,
  D181, D182, D185, D186.
- **Owner rulings 1-5 are reflected:** cap = policy at 255, setting deferred; ceiling added;
  backreferences at stage 2; reverse-dfa HELD under A-REV; the r3 dispositions mapped in §16.
- **D72** (INTERNAL minted for the end-check) agrees with §5.3's narrowing.
- **Goals:** §0 is ranked G1>G2>G3>G4>G5, each goal with a measurable form, and stage 1 serves them in
  that order: G1 accept/answers, G2 bytes via (A), G3 one loop, G4 counts. G2's dependence on Q1 is
  stated. G4's 8-line/one-slot bound is UNMEASURED and labelled so.
