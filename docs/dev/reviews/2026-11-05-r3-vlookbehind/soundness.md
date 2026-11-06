# crit-soundness findings (vlookbehind, design rev 0 frozen copy)

Lens: apply §5.1/§5.3/§5.5 as written to the review tree's real emitter
(worktrees/crit-vlookbehind, src/gen/emit_vm.c `vm_look_behind_branch` :7117-7280,
`vm_look_behind` :7400-7455, `vm_cut` :3687, `vm_set` :3589, count pass
`vm_count_slots_look` :3038) and to libpcre2 10.46 via R/tools/oracle_probe.
Emitted texts: soundness/f1.c, g.c, u.c.

## Findings

### SOUND-1 — §5.1's loop leaves the cursor at the last candidate when it moves to the next branch: a varying branch followed by any branch answers wrong (CONFIRMED by hand-execution of the pseudo-code; severity answer if built as written / design; effort small; blast: every multi-branch lookbehind with a varying non-last branch)

§5.1 pushes the retry frame at `L_try_i` AFTER the back-step, `RX_PUSH(&&L_adv_i, scan_position)`,
so the frame records the CANDIDATE position (RX_PUSH stores the position it is given; fail label
restores it, emit_vm.c's rx_fail, emitted at f1.c's `rx_fail:`). Both exits to the next branch then
run with `scan_position` = a candidate start, not the assertion's cursor:
`L_adv_i: if (d == lo_i) goto L_b(i+1)` (scan_position = cursor - lo_i) and
`L_bi: ...; if (d < lo_i) goto L_b(i+1)` (scan_position = cursor - d, already moved). `L_b(i+1)`
then "back-steps from the cursor"; today's code (and the fold §5.1 claims) back-steps from
`scan_position` (f1.c: `if (scan_position < 2) ...; rx_back_step(..., scan_position, 2)`).
Witnesses (oracle, libpcre2 10.46):
- `(?<=a{1,2}|b)x` on `bx`: oracle [1-2]. Hand-run at cursor 1: L_b0 steps back d=1 to 0; body
  `a{1,2}` fails on `b`; pop -> L_adv0 at 0, d==lo -> L_b1 with scan_position 0; branch `b`'s
  guard `0 < 1` -> rx_fail -> NOMATCH.
- `(?<=a{2,3}|b)x` on `bx` (the clamp exit): oracle [1-2]; L_b0 steps back d=1 < lo=2 -> L_b1 at
  scan_position 0 -> NOMATCH.
Neither cell is in §2/§7, and gate 1's generator list does not name "a varying branch BEFORE
another branch" as an axis (it would likely catch it, but nothing pins it).
Fix options, each of which moves the fold (SOUND-2): (a) `L_b(i+1)` back-steps from
`slot_values[POS]` instead of `scan_position` (every fixed branch's guard and back-step text
changes); (b) emit `scan_position = slot_values[POS]` at each branch transition after a varying
branch (a conditional statement, i.e. a shape decided by the predecessor's width); (c) keep
today's NEXT-BRANCH push at the cursor BEFORE the back-step AND add the per-candidate L_adv frame
(two live frames per varying branch, contradicting §5.5's "one per branch" and G4).
Repro: R/tools/oracle_probe m on the two cells above; hand-execution against §5.1 lines 188-196.

### SOUND-2 — The fold claim (§5.1 ¶2, G2/G3, owner question 1) does not hold against the emitted bytes: the one-point case of §5.1 is a different statement ORDER, push POSITION and work charge, so byte identity needs a second emission shape (CONFIRMED by reading emitted text; severity design/maintenance; effort small-medium; blast: every artifact with a lookbehind, i.e. G2's whole population)

Today's per-branch bytes (f1.c, `(?<=a|bc)x`, byte; same shape in g.c for `(?<!a|)x` and
`(?<*(a)|bc)x`, and u.c under `-e utf8`):
```
if (scan_position < K) goto L_next;          // guard
RX_PUSH(&&L_next, scan_position);            // NEXT-BRANCH frame, at the CURSOR (non-last only)
RX_CHARGE_WORK(K);                           // the width, once
scan_position = rx_back_step(subject, subject_length, scan_position, K);
if (scan_position == rx_BACK_STEP_NONE) goto rx_fail;
goto L_body;
```
§5.1 with lo==hi=K and every compile-time-decidable test folded:
`back-step; [d = K]; (d < K -> next); L_try: RX_PUSH(&&L_adv, scan_position /*= cursor-K*/);
RX_CHARGE_WORK(...); body; ... L_adv: goto L_next`. Bytes the fold would move:
1. ORDER: the push follows the back-step in §5.1 and precedes it today; the work charge follows
   the push in both but precedes the back-step only today.
2. PUSH POSITION: §5.1's frame records cursor-K; today's records the cursor. Threading the jump
   `&&L_adv -> &&L_next` (what "targets L_b(i+1) directly" needs) is a jump-thread, not a constant
   fold, and still leaves the wrong position (this is SOUND-1's mechanism; with today's position
   the general loop cannot advance from the candidate).
3. GUARD: today's guard is a separate `scan_position < K` BEFORE anything; §5.1's clamp is
   `d < lo` AFTER a back-step "up to hi". Folding "back-step up to K, d<K" into "guard, then exact
   back-step, then the sentinel check" is a rewrite of the statement sequence, not an evaluation
   of a test at compile time.
4. WORK: today charges the compile-time width K once ("the back-step, charged as the compile-time
   width", emit_vm.c :7215-7220); §5.1 charges "per candidate" with an unstated amount, and §5.5's
   "a {1,255} branch charges up to 255 per evaluation" implies 1 per candidate. Folded: 1, not K.
   Either today's K moves or the range case charges hi per candidate (255x255 for `{1,255}`,
   contradicting §5.5). The design must name the amount.
5. SENTINEL: today's `== rx_BACK_STEP_NONE -> rx_fail` has no counterpart in §5.1 (the "up to"
   back-step cannot return NONE).
6. SLOT: `d` is "a matcher slot written by vm_set"; a new slot family moves the slot legend and
   numbering of every later family (emit_vm.c :1061-1085 layout; `vm_count_slots_look` :3038)
   unless it is allocated only when some branch varies — again a width-decided shape. The count
   pass's exact `npush = nbranch - 1` (:3044-3050) also changes: a varying LAST branch pushes
   L_adv.
7. "COMMENT": the emitted C carries no per-branch comment at all (`grep -c 'fixed width' f1.c` =
   0); "fixed width %d" is the `--emit-ir` LISTING's label role (listing line 66). §5.1's "the
   emitted COMMENT is the one place the shape is named" mis-locates it; the listing rows
   (NEXT-BRANCH continuation, the work-charge note) are also outside G2's artifact gate.
Conclusion: identity is reachable only by an emitter `if (lo == hi) <today's sequence> else
<loop>` (or by making today's sequence the loop's prologue, which is SOUND-1's option (c) with
two frames). "A constant fold, not a second branch" is false in this emitter; it is an if by
another name. This does not make the design wrong to keep the bytes (owner question 1 may still
be yes), but G3's "no parallel path" and the leaning's "nothing moves and no abi event is owed
... by itself" must be re-argued: the honest options are (i) two declared shapes selected by the
width fact, or (ii) one loop shape and an abi event re-pinning every lookbehind artifact.

### SOUND-3 — W6 cannot fail under its stated sabotage: `aééx` has 3 characters before the cursor, so a byte-counted clamp gives the same d (CONFIRMED by hand-execution + oracle; severity answer-coverage (witness); effort trivial; blast: the UTF-8 clamp is unguarded)

Sabotage "clamp counts bytes": d = min(hi, scan_position) = min(2, 5) = 2 = the character answer
(3 characters precede). Back-step 2 characters -> byte 1 -> g1=(1,5): GREEN in the sabotaged
build. The stated reason ("a byte back-step lands mid-character") describes a different sabotage
(stepping bytes; and even that lands on byte 3, a character boundary, giving g1=(3,5), not a
failure for the stated reason). A cell that reaches the clamp needs fewer characters than hi but at
least hi bytes before the cursor: `(?<=(é{1,2}))x` on `éx` (UTF): oracle [2-3,0-2]; byte clamp
d=min(2,2)=2 -> 2-character back-step runs off the start -> nomatch. Also `aéx` does NOT reach
(oracle [3-4,1-3], same under the sabotage). Repro: `printf '%s\t%s\n' '(?<=(é{1,2}))x' 'éx' |
R/tools/oracle_probe m u`.

### SOUND-4 — The S136 re-aim reaches the hard return only if the sabotage moves BOTH ends of the range; "the analysis reports ... one too large" read as `pcrec_cwmax` makes the branch varying and both cells go green (CONFIRMED by hand-execution; severity witness; effort trivial; blast: the only exerciser of RX_R_INTERNAL)

After stage 1 the hard return is selected by `lo_i < hi_i` (§5.3). The natural sabotage at "the
analysis" is an over-reporting `pcrec_cwmax` (mod_lookaround.c :282-283 calls cwmax
over-estimation the FREE direction, and S136's own header :37-42 chose cwmax for that reason).
Then `bc` is range 2..3, not one-point: positive `(?<=bc|d)x` on `abcx`: d=3 at 0 fails, d=2 at
1 matches `bc` -> [3-4] = oracle; negative `(?<!bc|d)x` on `bcax`: d=3 body ends at 2 -> DECLINE
(not INTERNAL), d=2 `ca` fails, `d` fails -> holds -> [3-4] = oracle. Both GREEN. The re-aimed row
must be specified as "the stored one-point width K becomes K+1 at both ends" (an edit to
`la_widths`'s stored pair, not to cwmin/cwmax), and §7 should say so. Under that spelling the
design's hand-run holds (positive nomatch; negative reaches the end-check at 2 != 3 -> INTERNAL).
Oracle: both cells [3-4].

### SOUND-5 — WD6's first cell cannot fail (minor; stage 3, HELD; severity witness; effort trivial)

`(?<=\ba{1,2})x` on ` aax`: the walk stops at position 1 (hi=2 from cursor 3); a sabotage that
ignores the preceding context there and treats it as subject-start (non-word before) still finds
`\b` true -> [3-4] = oracle. Only the second cell, `baax` (oracle nomatch; sabotaged: false
match), discriminates. Harmless while it is paired; worth noting so the pair is not split.

## PROBED-AND-HELD

- Oracle answers of every §2/§7 witness re-run on libpcre2 10.46 (17 cells + 4 compile cells):
  W1 [2-3,0-2], W2 nomatch, W3 [3-4,0-2,2-3], W4 [2-3], W5 both [3-5,2-3], W6 [5-6,1-5],
  W8 REJECT 200, W9 255 ACCEPT / 256 REJECT 200, `(?<=a{300}|b)x` ACCEPT 300, W10 [2-3,1-2],
  S136 cells both [3-4], WD1 nomatch/[3-4], WD6 [3-4]/nomatch, `(?<=\ba{1,2})x`: all as stated.
- Sabotaged-build hand-executions that DO go red (given SOUND-1's cursor fixed): W1 (g1=(1,2)),
  W2 (false (2,3)), W3 (nomatch: d=3 first path ends at 2, skipping to d=2/d=1 fails), W4
  (INTERNAL: `ab?` from 0 ends at 1), W5 both rows (nomatch; the gap row walks d=3 -> 2 (fails)
  -> 1), W7 (min(2, pos-startpos)=0 < 1 -> nomatch), W8 (compiles), W9 (pair catches both
  off-by-one directions), W10 (g2=(0,2)); WD1 (both polarities flip), WD2, WD3, WD4, WD5. 15
  witnesses/cells reach and fail as stated.
- §5.1 trail discipline for `d`: SET at L_b before the push, `d--` SET after the pop and before
  the next push: every frame's trail mark is above d's current entry, so a pop restores d to its
  value at that push; an outer pop below the assertion rewinds it. A recursive re-entry through
  `(?n)` inside the body writes d above the outer frame's mark, so the outer pop restores it (d is
  read only after a pop) — d does NOT need the `VmSnap` save-set that POS needs. Held (3 shapes
  reasoned: retry, outer backtrack, nested activation).
- Atomic `vm_cut` at L_ok (mark taken at entry before every push, :7440): cuts only the
  assertion's own L_adv and body frames. Negative arm: L_body_won's cut also removes L_adv and
  L_neg_ok (as today's S124 argument); exhaustion pops L_neg_ok with the cursor restored. Held.
- §5.3 split: a varying negative branch that declines falls through to the next candidate/branch
  and finally L_neg_ok = "assertion holds" — correct whenever the body cannot end at the cursor
  from any candidate. Held (W4 cell).
- Non-atomic `(?<*`: L_adv frame stays live past L_ok; follow failure re-enters the body's own
  frames first, then L_adv (W5 hand-runs, 2 cells). Held. Live retry frames: one per activation
  (L_adv_i replaces itself; branch exhaustion transfers without a frame), so §5.5's "one per
  branch" is a true upper bound; in a repeated group, one per live iteration's activation. Held.
- Clamp absolute (floor 0, not startpos): W7 cell. UTF-8 forward advance has a seam entry
  (`VSK_ADVANCE`/`PCREC_ENCE_NEXT_POS`, vm_stmt.h :134). Held.
- Emitted shapes read (6 compiles): one branch, two branches of different widths, zero-width
  branch `(?<!a|)x`, negative, non-atomic with capture, UTF-8 `-e utf8` (`(?<=(é)|ab)x`): all
  share the 6-statement prologue SOUND-2 lists.
