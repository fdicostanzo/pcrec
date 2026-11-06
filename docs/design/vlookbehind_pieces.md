# Variable lookbehind as fixed and variable pieces — design probe

**Status: PROPOSED rev 0** (lane vlbpieces, opus, 2026-11-05; plan row [VLOOKBEHIND]). Design and
probes only: no build go, no edits under src/, cli/, lib/, memfn/ or tests/. It tests the owner's
idea (Frank, 2026-11-05) against `docs/design/vlookbehind.md` rev 2 (PROPOSED, READY WITH TEXT
FIXES). Evidence: `docs/dev/lanes/vlbpieces_evidence/` (README in §9). PCRE2 facts come from the
installed libpcre2-8 10.46 used as a library (`probe.c`); the pinned source copy was not opened
(D181).

**The owner's idea.** "There is a fixed portion and a variable portion. Always jump to the fixed
portion, then loop the variable portion." Read the body BACKWARD from the cursor as a sequence of
pieces. A fixed piece is reached by one jump and checked straight-line. A variable piece loops, as
a greedy bounded quantifier walked backward (longest first), on the VM's rung ladder. Captures that
cross from a variable piece into a fixed one are resolved when the loop's extent is known.

**The verdict, in one paragraph.** (b), in a narrowed form. The backward piece walk answers exactly
like PCRE2 on a stated class that a compile-time test detects cheaply. Outside it, three
counter-examples change captures or the overall match (§3). Inside the class it is not a new
mechanism. With one variable piece it IS rev 2's candidate loop, with the fixed tail checked once
instead of per candidate. With two or more it is one loop per piece where rev 2 has one loop, for the
same answers. So the range loop stays the one mechanism and the total fallback. What the idea gives
stage 1 is the ladder's other loop discipline (§5): the CURSOR rung's (the candidate start lives in
the retry frame; one trailed slot is written once per evaluation) in place of the COUNTER rung's
(a trailed counter rewritten per candidate). That removes rev 2's V1 trail growth instead of
sizing it. Two later rows are filed as HELD with triggers: the fixed-tail hoist ("jump to the fixed
portion"; exact on every atomic and negative cell measured) and the backward span count (a
candidate source beside `reverse-dfa`). Today's fixed-width bytes stay under every option (ruling A).

## 0. Goals

Ranked: the higher goal wins a conflict. These are the probe's goals; the feature's are
vlookbehind.md §0 and are not restated.

1. **G1 Answer identity (PCRE2 users).** Any form adopted answers like libpcre2 10.46 on every
   generated cell: match, every group, nomatch. Measurable: 0 differing cells, over the sweeps of §2,
   for the class the form is admitted on. The CONTROL (rev 2's loop, modelled) must show 0 too.
2. **G2 Stability (callers with today's artifacts).** Today's fixed-width lookbehind bytes do not
   move (Frank's ruling A). Measurable: rev 2's gate 2 (identity over every corpus artifact with a
   lookbehind), unchanged.
3. **G3 One mechanism (maintainers).** No second candidate loop beside rev 2's. Measurable: the
   emission table of rev 2 §5.1b keeps two rows (`one-length`, `range`); anything else is a HELD row
   with a trigger.
4. **G4 Bounded storage (every caller).** The trail a lookbehind evaluation owns does not grow with
   `hi − lo`. Measurable: the `vm_cost_look` term, derived from the emitted statements (§5.3).

Non-goals: a reverse VM (Frank: "not going to try a reverse vm just for this"); speed claims (no
timing was taken; §8); backreferences inside the body (stage 2, ruled); unbounded lookbehind.

## 1. Premise test

- `VmRungKind` is in src/gen/emit_vm.c: `VM_RUNG_CURSOR` 0, `VM_RUNG_FRAMES_BOUNDED` 1,
  `VM_RUNG_FRAMES_UNBOUNDED` 2, `VM_RUNG_REVDET` 3, `VM_RUNG_COUNTER` 4. `vm_rep` tries them in the
  order cursor, revdet, counter, frames. CONFIRMED.
- `VK_CONSUME_BACK` is in src/gen/vm_stmt.h: `if (C) { <p>_rv<i>_cursor--; goto <p>_L<n>; }`, built
  by `pcrec_vm_b_consume_back` (src/gen/vm_stmt.c). Its ONE producer is `vm_rev_emit`, the revdet
  rung's backward walk over `revdet.c`'s reversed AST, reached only for bodies that analysis
  approved. CONFIRMED.
- The atomic cell reproduces with libpcre2 10.46: `(?<=(?>a|ab)b)x` on `abbx` is nomatch;
  `(?<=(?:a|ab)b)x` is [3-4] (`control_cells.out`). CONFIRMED.

## 2. The probes

`model.py` is a small backtracking matcher for a PCRE subset (literals, classes, `\b`, `^`, `$`,
groups, alternation, bounded and unbounded greedy, lazy and possessive quantifiers, atomic groups,
lookahead, all three lookbehind forms, backreferences outside the body). Its lookbehind has three
evaluators:

| mode | what it is |
|---|---|
| `range` | rev 2 §5.1: per branch, candidate starts farthest first, the whole branch run forward, end-check at the cursor. **The control.** |
| `pieces` | the owner's walk. The branch is flattened into pieces: non-capturing groups dissolve, capture groups become open/close MARKERS. From the cursor, right to left: a fixed piece is one jump of its width, run forward; a variable piece tries its lengths longest first, each run forward with a local end-check. A marker takes the boundary the walk is at. |
| `trim` | rev 2's loop with the branch's TRAILING fixed run hoisted out of it: that run is reached by one jump and run forward once, and the loop covers only the rest, end-checked at the run's start. |

Every cell is run through all three and through libpcre2 (`probe.c`, the oracle). Subjects are every
string over {a, b} up to length 6 (127 per pattern) or 7 (255).

- **Main sweep** (`sweep.py`): 71 bodies × {`(?<=B)`, `(?<!B)`, `(?<*B)` + a follow} = 30,099 cells.
  The non-atomic follow is `\1` (and `\2` where it exists) for bodies with groups, else `b`. Body
  classes: fixed only; one variable piece; one variable piece with a varying inside; two or more
  variable pieces; groups crossing from a variable piece into the fixed tail; groups only right of
  the last variable piece; `\b`, `^`, nested lookahead and lookbehind (with and without groups);
  atomic and possessive pieces beside variable ones; lazy pieces.
- **Retry sweep** (`sweep_retry.py`): 6 bodies whose fixed piece has equal-width alternatives with
  distinct groups × 8 back-reference follows × {`(?<*`, `(?<=`} = 24,480 cells.
- **Spot cells**: the 22 control cells of rev 0-2 plus W12's re-aimed cell (`control_cells.out`, 23), UTF and caseless cells
  (`utf_cells.out`, `fold_cells.out`), stage-2 cells (`stage2_cells.out`).

**The control holds: `range` differs from libpcre2 on 0 of 54,579 sweep cells and 0 of 23 control
cells.** So the matcher is faithful on this subset, and a difference in `pieces` or `trim` is the
walk's, not the model's.

## 3. Question 1 — candidate order

Results by class, main sweep (`sweep_summary.txt`; "group 0" = the overall match list):

| form | groups | variable pieces | cells | `range` | `pieces`: any group / group 0 | `trim` |
|---|---|---|---|---|---|---|
| negative | any | any | 9,017 | 0 | 0 / 0 | 0 |
| positive | none | any | 2,286 | 0 | 0 / 0 | 0 |
| positive | some | ≤ 1 | 3,429 | 0 | 0 / 0 | 0 |
| positive | some | ≥ 2, every group right of the last | 508 | 0 | 0 / 0 | 0 |
| positive | some | ≥ 2, a group at or left of the last | 2,794 | 0 | **342** / 0 | 0 |
| non-atomic | none | any | 2,286 | 0 | 0 / 0 | 0 |
| non-atomic | some | ≤ 1 | 4,826 | 0 | 0 / 0 | 0 |
| non-atomic | some | ≥ 2, every group right of the last | 508 | 0 | 0 / 0 | 0 |
| non-atomic | some | ≥ 2, a group at or left of the last | 4,445 | 0 | **274** / **136** | 0 |

The retry sweep adds 16 differing cells, all non-atomic with ONE variable piece, and `trim` differs
on the same 16 (`retry_summary.txt`). Every other retry-sweep cell agrees, the positive form on all
of them.

**What this answers.**
- **Yes/no is order-free (MEASURED).** No negative cell and no capture-free cell differs, for any
  number of variable pieces, adjacent ones (`a{1,2}b{1,2}`, `a{0,2}b{0,2}`), alternation inside
  the body (`(?:a|b)?(?:b|ab)?`), nested quantifiers (`(?:a{1,2}b){1,2}`), `\b`, `^` and nested
  lookarounds. The reason: an existence answer does not depend on which successful path is found
  first, and a capture-free success leaves the same state whatever the path.
- **The match END is the same.** The lookbehind is zero-width, so the positive form's group 0 never
  differs (0 of 342).
- **The overall result can differ, through captures.** On the non-atomic form a different first
  success feeds a different group to the follow, and the overall match moves (136 cells).
- **The walk does not find PCRE2's start first.** PCRE2 tries starts farthest first. The walk takes
  the LAST piece longest first, which need not give the farthest start: `(?<=((?:ab)?)(b?))` on `ab`
  at cursor 2 is libpcre2 g1=(0,2), g2=(2,2); the walk gives g1=(1,1), g2=(1,2).

**The counter-examples** (libpcre2 first, then the walk):
1. Captures, positive: `(?<=(a{1,2})(a{1,2}))x` on `aaax` is [3-4, 0-2, 2-3]; the walk gives
   [3-4, 0-1, 1-3]. PCRE2's forward run gives the FIRST quantifier its longest share; the backward
   walk gives it to the LAST.
2. Overall match, non-atomic: `(?<*(a{1,2})(a{1,2}))\1` on `aaaaa` is [2-3,0-1,1-2][3-5,0-2,2-3];
   the walk gives [2-3,0-1,1-2][3-4,0-1,1-3][4-5,1-2,2-4].
3. Retry order with ONE variable piece, non-atomic: `(?<*(a{1,2})(?:(a)|(a)))(?:\3|\1b)` on `aaaab`
   is [2-3,0-1,-,1-2][3-4,0-2,-,2-3]; the walk gives [2-3,0-1,-,1-2][3-5,1-2,2-3]. The walk runs the
   fixed piece FIRST, so its choices become the OUTER loop; PCRE2 retries them innermost.

**UTF-8 and caseless widths (MEASURED on the libpcre2 side, the walk INFERRED).** PCRE2 counts
characters, not bytes: `(?<=(é{1,2})b)x` on `aébx` is [4-5, 1-3]; the Kelvin sign (3 bytes) folds to
`k` as one character: `(?i)(?<=(k)a{0,1})x` on `Kax` (Kelvin) is [4-5, 0-3]. Counter-example 1
recurs unchanged in characters (`(?<=(é{1,2})(é{1,2}))x` on `éééx` is g1=(0,4), g2=(4,6), PCRE2's
forward split) and under byte-mode caseless (`(?i)(?<=(a{1,2})(A{1,2}))x` on `aAAx`: libpcre2
g1=(0,2), the walk g1=(0,1), MEASURED with `model.py`). Widths in characters are fold-invariant
(PCRE2 folds character to character), so the class boundary of §4 does not move under UTF or `(?i)`.

## 4. Question 2 — captures, and the cheap test

**Frank's rule holds (MEASURED).** A group that crosses from a variable piece into the fixed tail is
resolved from boundaries, once the loop's extent is known. Five crossing bodies (`(a{1,2}b)`,
`(a?(b))a`, `(b{0,1}a)a`, `((?:a|ab)b)`, `(?:(a)|(ab))(b)a`), 2,159 cells: 0 differ under `pieces`
and under `trim`. The markers make it general: a group is an open and a close marker, each takes the
boundary the walk is at, and nothing else is needed once every boundary is fixed.

**Which shapes the rule covers.** The walk's captures equal PCRE2's iff the walk's FIRST success is
PCRE2's first success. With at most one variable piece, every boundary is fixed by that piece's
length. Lengths are tried longest first, which is starts farthest first. Each fixed piece's choices
are independent of the others at fixed boundaries. So the first success is PCRE2's: 0 of 3,429
cells. A group wholly right of the last variable piece sits at a cursor-relative offset, so it is
exact whatever the walk does: 0 of 508. Everything else needs the forward run from the found start
(the hand-off form, which is rev 2's loop).

**The cheap test, at compile time, per branch.** Flatten the branch into pieces, as `model.py`'s
`flatten` does. Count the variable pieces (`lo ≠ hi` from `pcrec_cwmin`/`pcrec_cwmax`, which rev 2
already makes exact for this consumer). Find the index of the last one. The walk is exact when:

| first match | lookbehind form | condition | walk exact? |
|---|---|---|---|
| 1 | any | the branch reads a group: a backreference or a group condition (stage 2) | **no**: right-to-left reads a group before it is written |
| 2 | negative | — | yes (existence) |
| 3 | any | no group in the branch | yes (existence; same state on every success) |
| 4 | positive, atomic | ≤ 1 variable piece, or every group right of the last one | yes |
| 5 | non-atomic, with groups | — | **no** (counter-example 3, even with one variable piece) |
| 6 | otherwise | — | **no** (counter-examples 1 and 2) |

The test is one walk over the flattened branch and the stored widths. No run-time fact is needed. So
the STOP RULE does not fire: the safe class IS cheap to detect.

## 5. Question 3 — atomic, possessive, negative, nested, backreferences

- **Atomic and possessive pieces: honoured, because each piece is run FORWARD.** The walk finds
  candidate POSITIONS backward; it never consumes backward. A piece run forward from a known start
  with a local end-check is exactly PCRE2's behaviour for that piece. `(?<=(?>a|ab)b)x` on `abbx`:
  `b` is the tail at 2; `(?>a|ab)` at length 2 from 0 commits to `a`, ends at 1, not 2, and cannot
  retry; at length 1 from 1 it fails; nomatch, as libpcre2 (MEASURED, control cells). The main
  sweep's atomic and possessive bodies (`(?>a|ab)b`, `(?>a|ab)`, `a{1,2}+`, `(?>(a)|(ab))`,
  `(?>a|ab)(b?)`, `(?>a{1,2})(b{0,1})`, `(a{1,2}+)(a?)`, `(?>(a|ab))(b?)`, `(a?+)(a{0,2})`): 0 cells
  differ in any form.
- **A backward-CONSUMING walk cannot honour them.** Consuming right to left over a reversed body is
  the reverse machine of rev 2 §3, which drops atomicity and is a SUPERSET: it accepts `abbx` above.
  `VK_CONSUME_BACK` is that kind of walk (revdet's, over `revdet.c`'s reversed AST, approved only for
  deterministic bodies), and so is a reverse DFA. Such a walk can only FILTER candidates, never
  answer, wherever the body has an atomic or possessive part or a nested lookaround. This is rev 2
  §3's `Nfa.erased` rule, reached from the other side.
- **Negative lookbehind:** existence, so any walk order is exact (0 of 9,017).
- **Nested lookarounds:** zero-width pieces, evaluated at their boundary against the whole subject.
  `a{1,2}(?=b)`, `(?<=b)a{1,2}`, `(?<=(b))a{0,2}`, `(?!a)(?:a|b){1,2}`, `(?<=(a|bb))(a?)(b?)`: 0
  cells differ under the cheap test's admitted forms. The last one is exposed (two variable pieces,
  groups left of the last), so row 6 excludes its positive form, correctly: its cells happen to
  agree on this alphabet, which is luck, not a proof.
- **Backreferences (stage 2).** libpcre2 accepts `(?<=(a)\1)x`, `(?<=(a{1,2})\1)x` (max lookbehind
  4), `(?<=(a{1,2})b\1)x` and a group condition `(?<=(a)(?(1)b|c))x` (`stage2_cells.out`). A
  right-to-left walk meets `\1` before group 1 is written, so row 1 excludes every branch that reads
  a group it writes. The same holds for the `trim` hoist: a tail containing `\1` runs before the
  rest has written group 1. A reference to a group OUTSIDE the lookbehind is a run-time-width piece:
  stage 2's business.

## 6. Question 4 — fit to the rung ladder

**No rung hosts a backward body as it is.** Each rung's own reading:
- **Cursor rung** (`vm_cursor_rep`): a FORWARD scan of a fixed-stride byte-class body from a known
  start, one resume frame re-pushed per retreat, one trailed low-water slot written once per loop
  ENTRY. A backward twin would be a new mirrored scan kernel.
- **Counter rung** (`vm_counter_rep`): forward iterations of one body copy with a TRAILED iteration
  counter. Rev 2's `D_i` already is this rung's shape: a `SLOT_COUNTER` slot (rev 2 §5.1b, V4).
- **Revdet rung** (`vm_revdet_rep`): a FORWARD deterministic scan, then a backward walk
  (`VK_CONSUME_BACK`) over the reversed body, floored at the forward scan's start, to recover the
  retreat point and the last iteration's groups. It walks back over bytes a forward scan already
  matched; it is not a backward matcher, and it is limited to bodies `revdet.c` reverses.
- **Frames rung**: forward replication.

So "the variable piece walked backward on the ladder" needs either a reverse matcher for the piece
(the owner's non-goal; and atomic-unsound, §5) or what the walk actually does in §2: find the
piece's CANDIDATE lengths backward and run the piece forward. The second is rev 2's loop applied to
the piece.

**What the ladder DOES give: the cursor rung's discipline for the loop itself.** Rev 2 spelled its
candidate loop in the counter rung's shape: a trailed counter rewritten per candidate, with the
cursor saved in the frame. That shape is exactly why V1 happened: one live trail entry per candidate,
`2 + Σ (hi_i − lo_i + 1)`, a K134 checkpoint on every range loop, and a ceiling proposal beyond the
3072 clamp. The cursor rung's header names the fix it was built around: "the cursor is a plain
local; the resume frame's own `pos` field is its save point ... the trailed low-water slot ... is
written once per loop ENTRY, so the mechanism designed to avoid per-iteration trail entries does not
quietly reintroduce one". Applied to the lookbehind:

```
L_b_i:    if (scan_position < lo_i) goto L_b_(i+1)        // guard, as rev 2 (not emitted at lo_i = 0)
          k = min(hi_i, scan_position)                     // VK_LSET: an UNTRAILED local
L_pre_i:  scan_position = $_back_step(.., POS, k)          // the farthest start
          if (scan_position == $_BACK_STEP_NONE) {         // UTF-8 only (dead under bytes):
              if (k == lo_i) goto L_x_i;  k = k - 1;        //   fewer than k characters precede
              goto L_pre_i; }
          RX_CHARGE_WORK(k)
          LO_i = $_back_step(.., POS, lo_i)                // VK_SET: the NEAREST start, trailed,
                                                           //   written ONCE per evaluation
L_try_i:  RX_PUSH(&&L_adv_i, scan_position)               // the frame saves the CANDIDATE START
L_body_i: <B_i forward, vm_emit unchanged>
          if (scan_position != POS) goto rx_fail           // end-check, as rev 2's range row
          goto L_ok
L_adv_i:  // popped: scan_position = this candidate's start
          if (scan_position == LO_i) goto L_x_i            // nearest start tried: exhausted
          scan_position = $_next_pos(.., scan_position)    // one CHARACTER nearer
          RX_CHARGE_WORK(1)
          goto L_try_i
L_x_i:    scan_position = POS                              // VSK_RESTORE: back to the cursor
          goto L_b_(i+1)                                   // last branch: rx_fail
```

- **Same candidates, same order, same body runs, same end-check** as rev 2 §5.1, so the answers are
  rev 2's: §5.1c's four hand-executions go through unchanged in outcome. The cursor F1 asked for is
  restored from `POS` at `L_x_i` instead of being carried by every frame (rev 2 kept the
  "every exit leaves the cursor" invariant by frame; this keeps it by one restore).
- **What is DELETED from rev 2 §5.1:** `D_i` (the `SLOT_COUNTER` slot) and its two write sites; the
  per-candidate back-step and its run-time count operand (rev 2 §5.6, V3); the per-candidate
  `RX_CHARGE_WORK(D_i)`; the sentinel's per-candidate pop; the trail term `Σ (hi_i − lo_i + 1)`;
  the K134 checkpoint on a CAPTURE-FREE range branch (`L_adv_i`'s back edge crosses no `SET` once
  `LO_i` is written before `L_try_i`: `vm_jump_closes_trail_cycle` reads "a `SET` written since the
  label"); rev 2 report finding 2's `growable` + `pt` ceiling proposal.
- **What it ADDS:** one `LO_i` slot per range branch (the cursor rung's low-water family,
  `vm_slot_low`, whose contract it is: trailed, written once per entry); the untrailed local `k`; one
  `$_next_pos` call per advance; one `VSK_RESTORE` at exhaustion. `$_next_pos` is the encoding
  seam's existing entry 1 (src/enc/enc_utf8.c); whether the VM body may call it today, and the
  [M5-SEAM] per-site count it moves, are build-time reads (INFERRED).
- **Why rev 2 rejected the neighbouring form.** Rev 2 §5.5 named "a second trailed slot holding the
  candidate, plus a one-character forward step per retry" and said it grows the trail too. That is
  right for a SLOT holding the candidate. Holding it in the FRAME's position, as the cursor rung
  does, is the difference.

**The sizing, traced to each pass** (INFERRED: derived from the code read above, not built):

| reader | rev 2 `range` row | cursor-discipline `range` row |
|---|---|---|
| `vm_count_slots_look` | +1 `SLOT_COUNTER` per range branch | +1 low-water slot per range branch (`v->nlow`) |
| `vm_cost_look` trail | `2 + Σ_range (hi_i − lo_i + 1)` | `2 + (number of range branches)` |
| `vm_cost_look` frames | `1 + nbranch` (safe bound) | unchanged: one loop frame per branch live, re-pushed |
| count-pass push sites | 1 per range branch | 1 per range branch (the push stays at `L_try_i`) |
| work per evaluation, per branch | Σ d over the candidates, ≤ (hi+lo)(hi−lo+1)/2 | k + (candidates − 1), ≤ 2·hi; `LO_i`'s back-step charged as `lo_i` |
| K134 checkpoint | on every range branch | only where the body itself writes the trail |
| trail at a raised cap (65,536 at the ceiling) | above the 3072 clamp; `growable` owed | one entry per branch: the cap stays POLICY in storage too |

**The family member.** The per-branch table is the fifth member of [DEC-RUNG]'s
"fact-selected emission + total fallback" family (review 2026-11-05 r6 V17), and this changes no
row of it: `one-length` and `range` stay, keyed on `lo_i < hi_i`. The cursor discipline is the
`range` row's spelling. The two HELD rows of §7 are a column and a candidate source, not rungs. A
backward span rung WOULD be "the next rung proposal", which is [DEC-RUNG]'s own trigger; this note
does not propose one.

## 7. Question 5 — verdict and what stage 1 becomes

**Verdict: (b), narrowed.**
- (a) is refuted by counter-examples 1-3: the backward walk does not replace the loop in general.
- (c) is not the case: on the class of §4's table the walk is exact (0 differing cells), and that
  class is detected at compile time.
- But inside that class the walk is either rev 2's loop (one variable piece, plus the hoisted tail)
  or several of them nested (two or more), for the same answers. Admitting it as its own row would be
  a second mechanism with no answer gain and no measured speed need (G3, D77). So the range loop
  stays the one mechanism, and the decomposition's contributions are a spelling and two HELD rows.

**Stage 1, recommended** (owner question 1 below): rev 2 unchanged except the `range` row's spelling
(§6). The table rows:

| row | applies when | spelling | bytes |
|---|---|---|---|
| `one-length` | `lo_i == hi_i` | today's code, verbatim | unchanged (ruling A, gate 2) |
| `range` | `lo_i < hi_i` | §6's cursor-discipline loop | new artifacts only |

**Stage 1's new or changed witnesses** (each must fail on a planted defect in the byte build AND the
UTF-8 build; rev 2's other witnesses stand):
- **W12 re-aimed (the trail term).** `(?<=a{1,9})x` on `bbbbbbbbbax`, libpcre2 [10-11] (rev 2's
  `(?<=a{1,2})x`/`bax` shape, widened so a per-candidate write overflows the O(1) term: nine writes
  plus two against a capacity of 2 + 1 + 1). A build that keeps a per-candidate trailed write with
  the new term gives `PCREC_ERR_FRAMES`. UTF-8 twin: `é` for `b`, libpcre2 [19-20] (MEASURED, `utf_cells.out`).
- **W-restore (exhaustion restores the cursor).** Rev 2's cells 1 and 3, `(?<=a{1,2}|b)x` on `bx`
  [1-2] and `(?<=a{1,2}|bc)x` on `bcx` [2-3]. A build that omits `L_x_i`'s restore starts branch 2
  at the nearest candidate (0 or 1) and answers nomatch.
- **W-advance (one character, not one byte).** The planted defect is a byte step for `$_next_pos`.
  On valid UTF-8 most such cells give the same answer (a candidate at a continuation byte fails its
  body), so this witness is the [M5-SEAM] fixture-declared per-site count, S133's shape, plus a
  `range` codegen fixture (rev 2 V8). INFERRED: the answer-level cell is a build-time search.
- **W-low (the low-water slot is trailed).** Two evaluations of one NON-ATOMIC site where an outer
  backtrack resumes the OLDER evaluation's frame after the newer one rewrote `LO_i`. An untrailed
  `LO_i` exhausts the older loop at the wrong start. The shape is the cursor rung's own reason for
  its trailed low-water slot; the concrete cell is owed by the build (INFERRED).

**abi treatment.** Under ruling A the `one-length` row is today's bytes, so no existing artifact
moves and no abi bump is owed for them. A `range` artifact is new; it is not an abi event for any
existing artifact. Gate 2 (rev 2 §6) is the check, unchanged.

**The HELD rows (filed in this note; plan ids are the manager's to assign):**
1. **Fixed-tail hoist** ("always jump to the fixed portion"). Per branch: the trailing fixed run
   (markers included) is checked once by a jump from the cursor, before the loop, and the loop covers
   the rest, end-checked at the run's start. MEASURED exact on every atomic and negative cell (0 of
   30,099 main-sweep cells; 0 of the 12,240 positive retry cells). Not exact for a non-atomic form
   whose tail writes a group (the 16 retry cells), nor for a tail that reads a group (stage 2). It
   composes the two existing rows (tail = `one-length`'s code; rest = `range`'s loop); a branch that
   is ALL tail is today's `one-length` row. Costs: a next-branch frame before the tail, so a failed
   loop rewinds the tail's writes; a trailed slot for the tail's start; an admission predicate.
   Benefit: a branch whose tail fails is rejected with one straight-line check instead of one per
   candidate. Trigger: a measured pattern where lookbehind evaluation shows in a profile and its
   branch has a trailing fixed run. No population row has one today (rev 2 §8: widths ≤ 3, and the
   bench body ends in a variable piece).
2. **Backward span count** (the variable piece "walked backward, greedy, longest first", literally).
   For a branch `F_left · x{lo,hi} · F_right` with `x` a fixed-stride byte-class sequence: count
   `x` backward from `cursor − |F_right|`, at most `hi` steps, and the candidates are exactly the
   counted lengths, longest first. It is a CANDIDATE SOURCE, a third row of rev 2 §5.4 beside
   `reverse-dfa` and `range`, with the forward finisher unchanged, so captures stay exact. It is the
   cheapest instance of A-REV's reverse walk (one class sequence, no automaton). Trigger: the same
   as `reverse-dfa`'s (rev 2 §5.4), or a wide `x{lo,hi}` lookbehind (hi in the tens) measured hot.

## 8. Standing questions (docs/design/CLAUDE.md)

1. **The measurement regime: NOT RELEVANT for timing.** No timing number is read or produced.
   Every number is an answer comparison: libpcre2 10.46 (the installed library on the Linux dev box)
   against a Python model, byte mode, plus UTF and caseless spot cells. A different regime cannot
   flip an answer comparison; the speed claims of §7's HELD rows are explicitly unmeasured.
2. **The independent control: RELEVANT.** The walk's answers are checked against libpcre2, which
   shares no source with the model. The model's own fidelity is checked by its `range` mode against
   libpcre2 (0 of 54,579 cells): a model bug common to all three modes would show there. Population:
   the sweep scripts count their own cells and print them (`sweep_summary.txt`, `retry_summary.txt`).
   Limit, stated: the bodies are hand-chosen and the alphabet is {a, b}. Several "exposed" bodies
   (`(a{1,2})(b{1,2})`, `(?<=(a|bb))(a?)(b?)`) agree only because their letters force one split;
   the cheap test excludes them anyway. A D27 author would widen the alphabet. The sabotage
   witnesses of §7 reach their sites by construction of the cell; W-advance and W-low are INFERRED
   and owed by the build.
3. **What moves when data is regenerated: NOT RELEVANT.** No table, calibration, stamp or generated
   file is introduced. The evidence files regenerate from `sweep.py`/`sweep_retry.py` with no
   effect on any build.

## 9. Evidence (`docs/dev/lanes/vlbpieces_evidence/`)

- `probe.c` — the libpcre2 probe (rev 1's, copied): stdin `pattern<TAB>subject`, argv `m`/`c`, `u`
  for UTF.
- `model.py` — the matcher and the three evaluators. `sweep.py`, `sweep_retry.py` — the sweeps.
  `tab.awk` — the per-class summary.
- `sweep_summary.txt`, `sweep_diffs.tsv` (every differing cell, 616), `retry_summary.txt`,
  `retry_diffs.tsv` (16).
- `control_cells.txt/.out`, `utf_cells.txt/.out`, `fold_cells.txt/.out`, `stage2_cells.txt/.out`.

Reproduce: `gcc -O1 -o $S/probe probe.c -lpcre2-8`, then
`PYTHONDONTWRITEBYTECODE=1 python3 -I sweep.py $S/probe $S/sweep.tsv` (about 10 s) and
`awk -F'\t' -f tab.awk $S/sweep.tsv`.

## 10. Measured vs inferred

- MEASURED (libpcre2 10.46 against the model): every cell count and counter-example of §3-§5; the
  control's 0; the crossing-group result; the `trim` results; the UTF and caseless libpcre2 cells;
  libpcre2's acceptance of the stage-2 cells.
- MEASURED by reading the code at main `783a45ec0`: §1's premise; the rungs' readings in §6;
  `vm_cost_look`'s `trail += 2`; `vm_jump_closes_trail_cycle`'s rule.
- INFERRED: the walk's UTF answers (from the byte twins and character-counted widths); the
  cursor-discipline loop's sizing table (derived, not built); whether the VM body may call
  `$_next_pos`; W-advance's and W-low's concrete cells; every speed statement.

## 11. Questions for Frank (plain words; leanings are not rulings)

1. **Re-spell rev 2's loop the cursor rung's way before the build go?** The loop would keep the
   candidate start in its retry frame and write one trailed value per evaluation, instead of a
   counter rewritten per candidate. Same answers. It deletes rev 2's trail growth (and the fix that
   sized it), most of the loop's trail checkpoints, and the ceiling proposal past 3,072 entries; it
   adds one slot, one forward character step per candidate and one restore. Cost: a rev 3 of
   vlookbehind.md and a re-check of §5.1 and §5.5. Leaning: yes, before the build, because it removes
   a hazard instead of sizing it, and it is what makes raising the 255 cap a one-row change in
   storage as well as in acceptance.
2. **File the fixed-tail hoist as HELD, not in stage 1?** It is your "jump to the fixed portion",
   and it is exact wherever it is admitted, but nothing in the population has a trailing fixed run
   after a variable part, so there is nothing to measure it on. Leaning: HELD with the trigger in §7.
3. **File the backward span count as a third candidate source beside the held reverse DFA?** It is
   your "loop the variable portion backward, longest first", taken literally, for a repeated
   character class. Leaning: yes, HELD, under the same home (A-REV) as the reverse DFA.
4. **Atomic groups ("Idk").** Answered: they work as long as each piece is run forward after the
   jump, which is what the walk does; only a walk that consumes backward breaks them. Nothing to
   rule unless you want the backward-consuming form, which would also need a reverse matcher.
