# Review 2026-11-05 r6 — vlookbehind rev 1 (design, RE-CHECK)

(Round number: the next free rN on 2026-11-05 at commit time; drafted as "r5" because r4 is alt_normal_form.)

**Subject.** `docs/design/vlookbehind.md` rev 1 (PROPOSED) at `bc9d1eb8f5ec013972d76ee8b0d26e84a045e393`, byte-identical
on main `7ddfbfa95` (merge of lane/vlbrev1). **Build tree:** main HEAD at the freeze, `7ddfbfa95833b60f193c563cfdb820c5532b61af`;
no src/, lib/, cli/, tests/ or docs/spec/ drift between the two. **Rulings frozen** at `7ddfbfa95`.
**Freeze drift:** none in decisions.md, plan.md, the subject, src/ or docs/spec/ between `7ddfbfa95` and main `82d95943c`
at hand-back. Two things landed mid-round that are not rulings: `docs/design/stream/arev.md` (A-REV rev 0, merge
`f15f30f25`), which reads vlookbehind §4/§5.1 (its column L and G6 "the finisher ... built by vlookbehind stage 1's range
loop"), so a rev 2 that changes §5.1 is read there too; and a critic-skill line on relayed findings (`82d95943c`).
The main tree was mid-merge (arevdesign) at the freeze; COMMON confined critics to the review tree and `git show 7ddfbfa95:`.
**Round dir:** `$PCREC_TMPDIR/scratch/crit-vlb2/` (critic texts, verify.md, COMMON in `review/`).

## RULING (manager, 2026-11-05)

Every PROPOSED disposition is ACCEPTED (FIX-NOW V1-V10 and V12, text only; V15 PLAN at [IFACE-PUSH]). Verdict accepted: READY WITH LISTED TEXT FIXES under either answer to the owner's fixed-width-bytes question. V4 RULED (answer-free, manager's): D_i comes from the existing SLOT_COUNTER family. V6 RULED under D26's addendum (accepting more than PCRE2 is not a defect): pcrec keeps accepting `(?<=(?:)*a)x`, named as a stated divergence in the spec hunk. V10: stage 1 deliberately reverses [DD-14.LB]'s ruled refusal; the note and the decision entry at the build say so. Process change adopted: the fix-induced row traces new slot writes and frames to the pass that SIZES their storage (critic skill §4).

## Lenses as run

| lens | model | question | why chosen |
|---|---|---|---|
| fix-induced (+ sibling of a family, general form + unlocks) | opus | For each r3 fix: what read, hand, row, slot, operand or check does it add; trace each in today's code; sibling fields left unstated | A re-check; launcher named F1's retry frame and F12's table + slot allocation |
| readiness (+ goals, ruling check) | opus | Per stage-1 build unit: cites hold, witness can fail, separable, readers complete; overall verdict under owner-Q1 (A) and (B) | The last re-check before a build go |
| soundness | opus | Hand-execute §5.1/§5.1b literally over the machine's frames/trail/slots, composed with today's vm_look, over multi-branch witnesses; check §5.1c, the rewrite claim, every §7 witness red/green | Pseudo-code over real primitives (the r3-amended soundness row) |
| simulate-literal | sonnet | Implement §5.1/§5.1b literally as an interpreter (explicit frames and trail) and diff against libpcre2 over a generated population; recompute §5.5 | Mechanised complement to the hand-execution; §5.5 quotes numbers |
| verifier | sonnet | Re-check every CONFIRMED finding that changes the design | §6.2 |

No adversary lens (no trust boundary), no measurement lens (stage 1 has no measured selection input; §11 says so).

## Which lens caught what

- **The trail under-charge (answer level)**: soundness, fix-induced and readiness, independently, all by reading
  `vm_cost_look` against §5.1's `VK_SET` order. The 76.7M-case literal interpreter did not: it modelled frames and
  the trail but not their CAPACITY, which the cost pass sizes (same shape as r3's lesson 1, one level down).
- **The rewrite claim's negative-arm and label gaps**: soundness.
- **The record/operand traps** (`slotx` is an index; role texts are emitted C; the slot family's readers; limits schema;
  INTERNAL's second producer): fix-induced, with readiness overlapping on the slot readers and the limits schema.
- **Gate holes** (zero-width unbounded repeats; the identity gate red on the flips; mis-cited harnesses and paragraphs;
  32 vs 36; D27 extracts and a superseded ruling): readiness.
- **Wiring the sketch leaves to the emitter**: simulate-literal (it had to import it to run).

## Findings with PROPOSED dispositions

Every finding sent to the verifier came back HOLDS, except READY-3 and READY-5 (PARTLY, details below) and
READY-10 items 2-3 (PARTLY). None REFUTED.

### Answer level

**V1 = SOUND-1 + FIX-1 + READY-1: the `range` row's `D_i` writes are never charged to the trail; a literal build gives
up with `PCREC_ERR_FRAMES` where libpcre2 matches.** CONFIRMED, verified HOLDS (hand trace against today's cost/capacity code).
- `vm_cost_look` (src/gen/emit_vm.c:2858-2864) charges `trail += 2`, constant. `vm_plan_capacities` (:8040-8041) sizes a
  bounded pattern's trail to `cost.trail + 1`; the emitted `RX_TRAIL` returns `RX_R_FRAMES` at capacity. Storage is a
  fixed array; no tier grows it for a bounded pattern.
- §5.1's order: each `L_adv_i` pop rewinds the trail to a mark taken AFTER the previous `D_i` write, then
  `D_i = D_i - 1` (`VK_SET`, trailed) writes a new entry above every later mark. One live entry per candidate tried,
  Σ over range branches of (min(hi_i, cursor) − lo_i + 1) per evaluation; an atomic cut does not rewind the trail.
- Smallest witness: `(?<=a{1,2})x` on `bax`, libpcre2 [2-3]. Trail capacity 3 (MARK, POS, `D_0 = 2`); the first
  decrement overflows → `PCREC_ERR_FRAMES`. Also `abx` (FRAMES instead of nomatch) and `(?<=x|[ab]{1,3})y` on `caay`.
- Second reader: a lookbehind in a growing loop under-charges the per-iteration trail, so the stamped
  `subject_ceiling` over-promises. And §5.2's "nothing in §5.1 depends on `hi_i`'s magnitude" is false for the trail.
- Gate 1 would catch a literal build red, so the blast radius is build time; the design still owes the term.
- **PROPOSED FIX-NOW (design text, rev 2):**
  - §5.1b's table gains a "trail entries per evaluation" column (`range`: hi_i − lo_i + 1; `one-length`: 0), and
    §5.5 a "Trail" bullet beside "Frames".
  - Name `vm_cost_look` beside `vm_count_slots_look` as the passes that must agree with the emitter; its trail term
    becomes `2 + Σ_range (hi_i − lo_i + 1)`. The frames term `1 + nbranch` stays a safe bound (say so).
  - Or argue a `D_i` spelling that does not grow the trail; leaning the cost term, which keeps the trail discipline
    every lens hand-traced as sound.
  - A witness row: drop the term → W2's or `bax`'s cell gives up.
  - §5.2's magnitude sentence is scoped: the trail is linear in `hi − lo` (bounded by the policy cap).

### Design / text that a build would follow wrongly

**V2 = SOUND-2: §5.1b's "rewrites 1-4 give exactly the `one-length` row" misses two differences.** Verified HOLDS.
- The negative arm's end-check: `range` declines, `one-length` returns `RX_R_INTERNAL`. No rewrite 1-4 touches that
  cell, and it is not answer-preserving in general (S136's re-aim is exactly where the two differ). It is a
  SELECTION, as §5.3 half-says.
- Labels: `vm_look_behind` allocates `bl/bodl/endl` per branch in one loop (emit_vm.c:7404-7408). If `L_try_i`/`L_adv_i`
  join that loop for every branch, every later label renumbers in an all-fixed artifact and G2 moves under (A).
- §13 (B): "the hard error stays tied to one length" and "Benefit: ... no table" contradict each other.
- **PROPOSED FIX-NOW (text):** list a 5th item as a selection, not a rewrite; add a label column ("`L_try_i`,
  `L_adv_i`: allocated only for `range` branches"); correct (B)'s benefit line ("one loop, plus a one-column
  end-check selection", or retire INTERNAL as the further contract change).

**V3 = FIX-5: `VK_SEEK.slotx` holds a slot INDEX; §5.6 says the back-step arm "renders `slotx`".** Verified HOLDS.
- `VSK_RESTORE` renders `slot_values[<slotx>]` (vm_stmt.c:457-460); its producer passes a bare number. Rendered
  verbatim, the back-step steps back by the slot's NUMBER, warning-free. Any W-row catches it at build.
- **PROPOSED FIX-NOW (text):** the arm renders `(size_t)slot_values[<slotx>]`; the same for `VK_WORK`'s amount.

**V4 = FIX-3 + READY-4 (+ FIX-8): the new `D_i` slot family has seven readers the design names one of.** Verified HOLDS.
- Readers (emit_vm.c): the base chain (placement decides whether splice's base moves), `vm_slot_name` (no arm → a
  bare number, which its header calls a bug), the totals and `RX_NSLOTS` sum (a missed term is K27's out-of-bounds
  write), `VmSnap`/`vm_w_range` (S153's "every family" house rule), `vm_listing_slots` (prints a "none" row for an
  empty family, so an unconditionally listed family moves every listing baseline), the `Vm` fields, and one shared
  count-pass/emitter predicate.
- Spec reader §10 omits: `docs/spec/ir_listing.md` §3.2¶2's append-only family vocabulary.
- FIX-8: `SLOT_COUNTER<n>` is already "one TRAILED iteration counter per counter loop", written by `VK_SET`; reusing it
  deletes five of the seven readers (verified: semantics equivalent). Cost: a varying artifact's
  pending/look/splice bases shift (new artifacts only under (A)).
- **PROPOSED FIX-NOW (text):** rev 2 chooses and states: either `D_i` is a `SLOT_COUNTER` slot (leaning: no parallel
  family, a simplification), or the new family's seven readers, its placement (top), its W disposition with the
  reason, the listing rule, and the ir_listing.md hunk.

**V5 = FIX-6: the role texts are emitted C under `-fcomments`, and seven sibling texts become false on a `range`
branch.** Verified HOLDS (`(?<=ab|c)x -fcomments`: lbc.c:450, :468).
- False on `range`: "(the LAST branch: no retry frame)", the negative END-CHECK role and its note ("a hard return"),
  the back-step note's `%d characters`, the "dead because the guard is exact" note, "charged as the compile-time
  width", the guard note with `k`.
- Gate 3's classification control reads the per-branch judgment through exactly this text or the slot legend; name it.
- **PROPOSED FIX-NOW (text):** a role/notes column in §5.1b; "not emitted C" becomes "a comment under `-fcomments`,
  a listing label always". Under (B) these comment moves are inside the abi event.

**V6 = READY-2: a second accept-set exception class: unbounded repeats of a zero-width body.** Verified HOLDS.
- libpcre2 refuses `(?<=(?:)*a)x` and `(?<=(?:\b)*a)x` (err 125) at the default and at `max_varlookbehind = 0`;
  pcrec compiles them today as one-length, by design (src/opt/mrl.c:660-666).
- Gate 3's "0 exceptions" and its classification control go red on a CORRECT build once the generator crosses
  "nested lookaround"/"bounded quantifier" with an unbounded zero-width repeat. Nothing in the population uses it.
- **PROPOSED FIX-NOW (text) + a manager choice:** (i) keep accepting and name the class in G1 and gate 3 as a stated
  divergence counted on its own line (the design's own D26-addendum reading); or (ii) refuse it (a second G1-over-G2
  exception). Leaning (i). Stage 2 inherits the same choice for references to such groups.

**V7 = READY-3: gate 2 has no named instrument, and the existing identity gate is red on the flips by construction.**
Verified PARTLY (mechanism holds; count corrected).
- `tests/codegen/run_recursion_identity.sh:2163-2166` hard-fails a call-free pattern accepted by one build and refused
  by the other. Stage 1 flips 22 distinct call-free corpus patterns (30 rows; the verifier's count — the critic said 24,
  which includes the 2 call-bearing deferred rows).
- **PROPOSED FIX-NOW (text):** gate 2 names that instrument: `differing = 0`, the refusal-mismatch set equals the
  flipped manifest counted from population.tsv (K35), then the re-pin in the landing commit. Under (B) the same re-pin
  carries the abi number.

**V8 = FIX-2 + READY-5: sabotage rows that move are under-listed.** Verified HOLDS / PARTLY.
- S133/S134 anchor the one literal-`k` back-step and its sentinel (`SAB_COUNT=1`); a `range` site is a second,
  unanchored `pcrec_vm_b_seek`. Every codegen `residlb*` fixture is fixed-width, so §5.1's "[M5-SEAM] per-site count
  unchanged" is unchecked for `range`. Under (B), S133-S135's anchors sit in rewritten code.
- S-U4 (A_CLASS width ×4) loses its stated detector: `(?<=a)x` becomes `range` [1,4] with today's answers. The verifier
  notes it likely still goes red on the cap/ceiling boundary cells (×4 crosses 255/65535), so its figure is wrong
  rather than its detection gone (not run).
- S136's re-aim: sabotaging only the LAST branch leaves both cells green (verified by trace); the natural edit
  (`la_widths`' loop) hits every branch, which works.
- **PROPOSED FIX-NOW (text):** §7 "Existing rows that move" gains S133/S134 (a `range` twin or re-anchor) and S-U4
  (re-aim + figure), plus a `range` codegen fixture (e.g. `(?<=a{1,2}|bc)x`, `back_step:2`); S136 says "every
  branch, or branch 0, never only the last".

**V9 = FIX-4 + READY-8: the two `limits.def` rows are spelled outside the row schema.** Verified HOLDS.
- `name` is the C symbol (upper case, e.g. `LA_*` under `MOD_LOOKAROUND`); the unit vocabulary has `"chars"`, not
  "characters"; `kind` is a closed list of five, printed in the public `--list-limits`/`pcrec_limits_tsv` header
  (src/dump/limits_dump.c:93-101); `tests/registry/limits_check.sh` carries a name manifest and the literal 78, and
  finds anchored values COMMA-GROUPED (so §3.11 writes 65,535). The `hi > INT_MAX` arm becomes unreachable.
- **PROPOSED FIX-NOW (text):** symbol names, `"chars"` with the byte-mode reading in `desc`, an existing kind or an
  explicit three-text schema hunk, the manifest +2 and 78 → 80, "65,535", the dead arm deleted.

**V10 = READY-6: §10 misses the D27 extracts and D27-owned corpora, and a prior RULING is reversed unstated.** Verified HOLDS.
- `docs/design/la_d27_extract.md` (:155-158, :171, :225, :323: "the author must not write a match expectation") and
  `sr_d27_extract.md` §3.4(d) state the refusal; D27-owned cells in `tests/lookaround/d27/` and `tests/recursion/d27/`
  pin it. Extracts are re-cut only from source (docs/design/CLAUDE.md).
- The [DD-14.LB] amendment (2026-08-24), recorded "as a RULING", refuses a call to a callee of different fixed widths
  that PCRE2 accepts; stage 1 flips it (`^(?(DEFINE)(?<g>a|ab))ab(?<=(?&g))$`, libpcre2 ACCEPT lb 2). Reversing it is
  right; the design should name it as superseded.
- **PROPOSED FIX-NOW (text):** §6 stage 1 / §10 list both extract re-cuts, the D27-file owner, and the superseded
  [DD-14.LB] ruled perr (§13.3 records it). The manager acknowledges the supersession when ruling.

### Doc

**V11 = FIX-7: `PCREC_ERR_INTERNAL` has a second producer (D72's region-exit guard, vm_stmt.c:345-353).** Verified HOLDS.
match_api.md §4¶6's "one producer" is pre-existing drift that §10's hunk carries forward; two comments
(enc_utf8.c:255-278, emit_vm.c:7319-7356) read the end-check's redundancy. **PROPOSED DOC** (rev 2: the hunk names both
producers; the two comments join the reader list).

**V12 = READY-10 + READY-7 + READY-9: cites and counts.** Verified HOLDS (items 2-3 PARTLY).
- Gate 1's "PC-3's harness" is the registry compile check; the match differential is
  `tests/lookaround/run_lookaround_diff.sh`.
- §14's `match_api.md` §6¶19 should be §6¶18 (¶19 is "fixed within one abi"; the no-bump reading follows from ¶18).
- The "free" premise lives in `pcrec_cwmax`'s header (mrl.c:509-510, about both functions); stage 1 corrects it, not
  only stage 2's A_BREF sentence.
- "[branch-reset] lands": `branch-reset` is a module, not a plan row.
- §6 stage 1 says "36 rows flipped"; §8 and population.tsv say 32 (24 distinct); the 4 backreference rows are stage 2.
- Shape 7 means "not well-formed"; the cap and ceiling are limits. The §2.4 hunk widens the cell or says why not.
- **PROPOSED FIX-NOW (text)** (one pass of small edits).

**V13 = SIMLIT-2: §5.1 does not state how it composes with the negative arm, the atomic cut and non-atomic `(?<*`.**
The interpreter imported today's `vm_look` wiring (negok below every `L_adv`, `L_ok` cuts to the mark, last-branch
exhaustion is `rx_fail`) and got 0 diffs. **PROPOSED DOC** (one sentence in §5.1 citing vm_look).

**V14 = SOUND-3:** §5.1c's framing sentence "the others fail before the lookbehind or at its first guard" is false for
cells 3 and 4 (the four traces hold literally). **PROPOSED DOC.**

**V15 = READY-11: goal and ruling dependencies.** Verified HOLDS.
- G1's measurable holds at stage 1 only if the 65535 ceiling rides stage 1 (owner Q2). Say so in §0 and gate 3.
- The frozen [IFACE-PUSH] row never mentions the `max_varlookbehind` setting the owner ruling defers to it.
- **PROPOSED DOC** (§0) **+ PLAN** (the manager adds the setting to [IFACE-PUSH] when stage 1 lands, or now).

**V16 = SOUND-4: latent — libpcre2's branch length stops at `(*ACCEPT)`** (`(?<=a(*ACCEPT)b{1,2})x` ACCEPT lb 1);
pcrec refuses `(*` today ("requires module 'verbs'"). **PROPOSED PLAN/DOC:** one line in §14 owned by the verbs module;
the pcre2-reader question in `review/sound.md` rides that module.

**V17 = fix-induced's standing questions.** The width-selected two-row table is the fourth member of "fact-selected
emission with a total fallback" (the rung ladder `vm_rep`, an if-chain whose count-pass twin re-derives the choice;
alternation island/chain; clskit `ROWS`; DFA `cand_rows`), and the first VM-body member to be DECLARED. General form: a
reference emission plus admission rows, each row declaring its columns for EVERY reader (slots, pushes, trail, frames,
work, role text, listing), with one memoised row choice per node; V1 and V4 are both instances of the hazard the rung
ladder's header already names. **PROPOSED NOTED + PLAN (manager's call):** stage 1 takes the per-row columns (V1,
V2, V4, V5 already ask for them); a trigger-gated row for the rung ladder's migration (trigger: the next rung, or the
next count/emit disagreement found in the ladder).

**SIMLIT-1, SIMLIT-3: NOTED** (holds; see PROBED-AND-HELD).

## PROBED-AND-HELD (summary; counts in each critic file)

- **§5.1's semantics, literally:** simulate-literal's interpreter (explicit frames and trail, §5.1/§5.1b as written)
  over 8,592 patterns (1-3 branches, 14 templates in every order, `(?<=`/`(?<!`/`(?<*`, retry-forcing follows),
  37,409,568 byte cases and 39,274,032 UTF-8 cases, start offsets 0-3: 0 diffs against libpcre2. Self-check sabotages
  (candidate-saving frame, shortest-first, rev-0 hard return, exhaustion to rx_fail): 0.43M-11.8M diffs each. The
  sentinel fired 17.1M times under UTF-8 and 0 under byte. D142's class: 3,714 cases, all `\b` with start > 0.
- **Hand-executions over the real primitives:** soundness, 58 byte + 15 UTF-8 multi-branch witnesses (range/one-length
  in every order, varying last branch, `lo = 0`, both arms, atomic/non-atomic, outer backtrack into the assertion,
  nested lookbehinds, loops, `startpos > 0`): 58/58 and 15/15 equal to libpcre2; a 3,000-pattern random differential:
  2,866 compiled, 0 diffs.
- **§5.1c's four cells** hold literally (three lenses); step-level nits only.
- **§5.1b's rewrite claim on the positive arm:** statement order, saved operand, charge, count, sentinel and the last
  branch's missing frame all coincide with today's C (except V2's two items).
- **Every §7 witness** (W1-W11, W3b, W9b, S136's re-aim spelled for all branches) is red in its sabotaged build and green
  in the correct one, by trace (soundness, readiness).
- **§5.5 numbers:** 32,640, 1,320, ≥ 30,600 (30,637) and the per-branch formula agree with the interpreter's charges
  (8 cases).
- **F13's record claims:** `VK_WORK` takes a string amount; `VK_SEEK` has `slotx`; `$_back_step` takes `size_t k` in
  both encodings: no new seam entry, no D58 addendum.
- **`D_i` needs no W/VmSnap membership** for correctness (read only after its own set or a trail-restoring pop).
- **Possessify never enters a lookaround body**, so W3/W3b's give-back frames exist.
- **Stage 2 as a future unit:** cites hold; 12 acceptance-table cells re-probed, all as tabled.
- **Rulings:** owner rulings 1-5 reflected; [LB-EXIST] filed HELD as stated; every relied-on D-row and plan row exists
  at the freeze; D72 agrees with §5.3's narrowing.

## By-id completeness

| id | → | id | → |
|---|---|---|---|
| SOUND-1 | V1 | READY-1 | V1 |
| SOUND-2 | V2 | READY-2 | V6 |
| SOUND-3 | V14 | READY-3 | V7 |
| SOUND-4 | V16 | READY-4 | V4 |
| FIX-1 | V1 | READY-5 | V8 |
| FIX-2 | V8 | READY-6 | V10 |
| FIX-3 | V4 | READY-7 | V12 |
| FIX-4 | V9 | READY-8 | V9 |
| FIX-5 | V3 | READY-9 | V12 |
| FIX-6 | V5 | READY-10 | V12 |
| FIX-7 | V11 | READY-11 | V15 |
| FIX-8 | V4 | SIMLIT-1 | NOTED |
| standing questions | V17 | SIMLIT-2 | V13 |
|  |  | SIMLIT-3 | NOTED |

All 27 critic ids are dispositioned.

## Recommendation

- **Under owner-Q1 answer (A): READY WITH LISTED TEXT FIXES** (rev 2, text only). V1 is the one a literal build gets
  wrong (a give-up, not a wrong answer); V2-V10 are text a builder would otherwise follow into a defect or a red gate.
  No mechanism change. Two choices for the manager: V4 (counter family vs new family; leaning counter) and V6 (keep
  accepting zero-width repeats as a named divergence; leaning yes).
- **Under (B):** the same, plus the abi event's readers by grep, the FILEPIN re-pin of every lookbehind artifact, and
  S133-S135's re-anchors.
- **The build go also waits on** owner Q1 and, for G1's measurable at stage 1, owner Q2.
- **No further full round.** A short diff check of rev 2's §5.1b/§5.5 (V1, V2, V4) by one critic is enough.
- A D27 spec-first author stays RECOMMENDED (§9), with V10's extract re-cuts.

## Lessons for the guide (proposed)

1. **A model that omits a resource bound validates answers, not the build.** The literal interpreter modelled frames and
   the trail but not their capacity; three reading lenses found that the cost pass never charges the new trail writes.
   Proposed text for the fix-induced row: "When a fix adds a slot write, a frame or a trail entry, trace it to the pass
   that SIZES that storage (`vm_cost_*`, `vm_plan_capacities`), not only to its readers (2026-11-05 vlb2: `D_i`'s
   decrements outgrew a trail sized from a constant)." And for the simulate row: "a literal interpreter reports the
   peak frame and trail depth per evaluation beside its answers, and compares it with the cost pass's charge."
2. **A new slot family or row is checked against every reader of its siblings, by grep** (fix-induced already says this
   for fields; this round's slot family had seven readers and the design named one).
