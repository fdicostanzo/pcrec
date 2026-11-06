# client critic: arev2

Question: does every client-dependent sentence of arev rev 1 (0f7d79795) and roadmap A-REV (de551e514)
hold under vlookbehind REV 3 (e20dee230)? Subject files extracted to this dir (arev.md, vlb3.md,
roadmap.md). Model: model/oneway.py (imports a copy of vlbrev3_evidence/candidates.py).

## Findings

### client-1 — the client row in force never took arev's proposals: rev 3 §5.4/§4/§6/§7 still spell rev 2's row
**CONFIRMED (text).** Severity: design (answers latent: S3 is not built). Effort: S (text, one owner
call). Blast radius: whoever builds S3 / vlookbehind stage 3 from the client doc.
arev §3.1 (lines 360-372) says rev 1 "adopts" vlookbehind's `reverse-dfa` row and that its differences
(1) `!has_bot` before the build, (2) `lang = same` not "exact", (3) per-branch verdicts, (4) cursor-rung
spelling, (5) no [LANDWALK-VM] / P-d prerequisite, are "PROPOSALS to the client's owner document, which
is vlookbehind's to change". Rev 3 changed (4) only. At e20dee230:
- vlb3 §5.4 (line ~1090-1096): admission still "Exact machine and no capture: EXISTENCE"; "Exactness is
  read from `Nfa.erased == 0`". No `has_bot` anywhere in rev 3 (grep: 0 hits; `lang =`: 0 hits).
  Following it, `(?<=\Ga{1,2})b` on `aab` answers nomatch (libpcre2 [2-3], re-probed today) and
  `(?<=^a{1,2})b` is an internal-error refusal (r5 F1/F2).
- vlb3 §5.4 prerequisites (line 1129-1130): "the three exits (§4 G1-G4), hosted in a VM body (G5,
  [LANDWALK-VM])"; trigger "(D77): a measured cell where the lookbehind's candidate tries dominate";
  §6 "Stage 3 (HELD)" (line 1454); §4 "Why not now" ties it to P-d (line 424) and "no measured need";
  §4 G4 existence "may stop at the first accept" (arev §2.2 dropped `first`). All contradict the owner
  addendum arev and roadmap A-REV carry ("no speed trigger", Frank 2026-11-06).
- vlb3 §7 "Stage 3's witnesses" WD1-WD6 (line 1486-1496) reuse arev's ids for DIFFERENT cells (rev 3
  WD2 = W10's cell, WD3 = W1's, WD4 = W5's gap cell; arev WD2 = `(?<=(a{1,2})|(aa{1,2}))c`, WD3 =
  `(?<=(a{1,2}))b`, WD4 = `(?<*(a{1,2}))b\1c`) and lack WD-G, WD-A, WD-B, WD8, W-restore.
- §16c's table says r5 F1/F2 "remain reverse-machine hazards, not the loop's" but its pickup list
  is one-way (arev picks up from vlookbehind); nothing says who carries arev's five proposals back.
Consequence: two documents in force state the same row with different admission, trigger and witness
lists; the one arev names as the owner is the wrong one for answers. Fix: either vlookbehind §5.4/§4/
§6/§7 adopt arev §3.1 (1)-(5) and its WD list (one id space), or arev states that §3.1 supersedes
vlookbehind §5.4 for the hand-off and the manager rules the row's owner. roadmap A-REV's ride-along
list ("[VLOOKBEHIND] stage 3") inherits the same ambiguity: S3 IS stage 3.

### client-2 — S3 takes stage 1's own `range` witnesses and codegen fixture off `range` in the default build
**CONFIRMED (derivation from arev §3.1's admission table; counts INFERRED, the row is unbuilt).**
Severity: maintenance (checks lose reach, one fixture goes red at landing). Effort: S-M. Blast radius:
S3's landing; vlookbehind §7's rows.
arev §7.2 (Reach): "`range` is checked by stage 1's witnesses". Rev 3 grew that set (W6/W11/W12
re-aimed, W13-W16 new, S133/S134 `range` twins, fixture `residlbrange (?<=a{1,2}|bc)x` with
`back_step:3`). With rows 2-3 default-on, a branch with no backreference, no BOT node and a building
machine leaves `range`:
- row 2 (exact, no group): W2 `(?<=a{1,2})x`, W3b, W4 `(?<!ab?)x`, W7, W11(a) branch 0, W11(b),
  W12(a) `(?<=a{1,9})x`, W12(b), W13's second cell, W16's first cell, and the fixture's branch 0;
- row 3 (group): W1, W5, W6 `(?<=(é{0,2}))x` (the far retry is range's only), W13 `é(?<=(a?))`
  (row 3 has no bounded `advance` step), W15, W14's Kelvin cell.
Only cells the row declines keep reach (W14's `\G` cells via `has_bot`). The fixture's per-site count
becomes 1 (branch 0 emits no back-step), so `run_codegen_tests.sh` is red on S3's landing, and the
S133/S134 `range` twins' anchors are not emitted for it. Fix: S3's gate states that stage 1's
witness rows and the `range` fixtures run with the row's test-only lever DENIED (or are re-aimed to
declined bodies), and adds a positive control that each still reaches its site (MECH-REACH).

### client-3 — rev 3's "one row choice, read by every column" is a two-row predicate; arev's reader table needs it to become the recorded four-row selection
**CONFIRMED (text); consequence SUSPECTED (pass order unverified).** Severity: design/doc. Effort: S.
vlb3 §5.1b (line ~781-786): "The key is one predicate on the stored pair, `lo_i < hi_i` ... every
pass reads it: `vm_count_slots_look`, `vm_cost_look`, `vm_look_behind_branch` and the role texts"; the
trail term is "read off the stored width pairs through the table's one predicate" (§5.5); `LO_i` is
allocated by `v->nlow++` per `range` branch and `L_far/L_try/L_adv/L_n` "ONLY for range branches".
arev's reader table (line 436-438) gives row 3 "slot: none", "trail 0", labels without `L_far_i`/
`L_n_i`. That holds only if every one of those passes reads the SELECTED ROW, not the width predicate.
Pickup 5 treats only the trail column ("over-charged by one, which is safe"); with the predicate kept,
a row-2/3 branch also gets an unused `LO` slot (every family above `low` shifts) and unused labels.
And the selection's conjuncts (d) "builds under its own cap, rung not dropped" and `lang` are read
AFTER a machine build, so the machine build must precede the VM count passes. arev should state the
key change (predicate -> one recorded per-branch row, read by the same four passes plus label
allocation) and the ordering constraint.

### client-4 — pickup 4: the inequality holds per candidate (not only on totals), and one parenthetical is false under rev 3
**CONFIRMED (model + text).** Severity: doc. Effort: S.
- arev line 463-465: "the empty candidate at `lo_i = 0` charges nothing, as range's `d = 0` candidate
  does". Under rev 3 range reaches the empty candidate by `L_adv_i`'s step, charged 1, unless it is
  the only candidate. Rev 3 §5.5's own cell: `(?<=a{0,1})` charges 2 (far 1 + step 1). The
  conclusion survives; the comparison is false.
- §16c pickup 4 says the argument "no longer reads per candidate". It does, if the far-step charge
  (`lo + ΣK`) is attributed to the farthest candidate and each step's 1 to the candidate it reaches:
  model/oneway.py checks row 3's charge (1 per non-empty candidate, every range candidate accepted =
  row 3's worst case) against range's charge before each candidate's body, over candidates.py's
  8,583,480 cells (bytes and UTF-8, ill-formed included, far retry included): 0 violations, 923,070
  tight points. Recommend arev restate it as that prefix inequality (it also covers early success,
  which a totals statement does not).

### client-5 — pickup 3's "exactly row 3's" is false as sketched
**CONFIRMED (text).** Severity: doc. Effort: XS.
vlb3 §5.1 `L_try_i: RX_PUSH(&&L_adv_i, scan_position); goto L_body_i`. arev row 3 (line 409-410):
`L_try_i: RX_PUSH(...); RX_CHARGE_WORK(scan_position < POS)`. Row 3 shares `L_try_i` only if its
`VK_WORK` moves before the jumps into `L_try_i` (after `scan_position = t`, both sites), as range's
step charge sits before `goto L_try_i`. `L_body_i`/`L_end_i` are shared as stated.

### client-6 — rev-2 dependencies §16c missed (all doc-level)
**CONFIRMED (text).** Severity: doc. Effort: S.
- Header lines 9-11: "Client documents in force: `vlookbehind.md` rev 2".
- §2.6 heading "against vlookbehind rev 2 §4's checklist"; §3.1 "Vlookbehind rev 2 §5.4", "rev 2 §4
  'Why not now'", "rev 2 §5.1b's table gains two rows"; gate "rev 2 gate 1's harness", "rev 2 V6",
  "Rev 2 §5.4's evidence requirement"; §4.1 "vlookbehind rev 2 §3 predicts" (rev 3 text unchanged at
  each: citation only).
- §8 Q1 (line 734-740, "Spell the lookbehind loop the cursor-rung way?"): ANSWERED by the owner
  2026-11-06; §16c pickup 1 covers lines 401-402 only.
- §11 last row "vlbrev2 pickups 1-10 applied" and in-text "(pickup 6)", "(pickup 7)", "(pickup 8)",
  "(pickup 9)", "pickup 4" (line 244): rev 2's numbering, now ambiguous beside rev 3's 11-item list.
- Soundness (line 452): "Range tries every start whose distance lies in `[lo_i, min(hi_i, cursor)]`" is
  the reading rev 3 §5.1a/REVISION 3 refutes under UTF-8 (the farthest start is the farthest position
  `$_back_step` reaches within `hi` characters; an ill-formed run stops it). Conclusion unaffected
  (the byte machine accepts only valid spans, which `$_back_step` reaches), wording wrong.
- Gate answers (line 481-485): rev 3 gate 1 adds ill-formed UTF-8 subjects under
  `PCRE2_MATCH_INVALID_UTF` (W13, W15). arev's gate and W-UTF list have none for rows 2-3, which is
  exactly where pickup 9's replacement fact ("the byte machine accepts only at character boundaries
  of valid input") would be tested.
- Line 428-429: "its back edge closes a trail cycle only where the body itself writes the trail
  (captures)": rev 3 §5.1b's list is wider (a cursor/counter rung's `SET`, an atomic mark, a nested
  lookaround's mark and `POS`, a callee's park); `(?<=a{1,9})x` keeps the checkpoint. The reader
  table's "only where the body writes the trail" is right; the parenthetical is not.
- The reader table lacks rev 3's "matcher locals" (row 3: none, no `K_i`) and "seam sites" (row 3: 0
  back-steps, 0 `advance`) columns; the second matters for client-2's fixture count.

### client-7 — the zero-width-repeat gate cell is capture-free, so it reaches row 2, not row 3
**SUSPECTED.** Severity: doc. Effort: XS. arev line 483: "`(?<=(?:)*a{1,2})x` reaches row 3, since it
varies". No group; unless `(?:)*` sets an `erased` bit or `has_bot`, `lang = same` sends it to row 2
(arev's own table). Confirm by reading the NFA builder's empty-star arm at build. Not rev-dependent.

## PROBED-AND-HELD

**Pickup-by-pickup (vlb3 §16c, against rev 3's body, arev lines verified: 16/16 citations land on the
quoted text).**
1. 401-402 / 422-430 / 438 brackets: NEEDS ONLY WORDING (ruled; paragraph becomes history).
2. 379 "rev 2 §5.1" -> rev 3 §5.1: CITATION ONLY.
3. 259: body + end-check shared: HOLDS; "exactly row 3's" for `L_try_i`: see client-5.
4. 462: arithmetic HOLDS. Byte mode: total `lo + 2K0 <= 2hi - lo`; UTF-8 corner adds
   `Σ_{k=e}^{K0} k <= (hi-lo)(hi-lo+1)/2`; `2K + lo >= K + 1` iff `K + lo >= 1` (both 0: one empty
   candidate, both 0). Per counter: work (prefix model, 0/8,583,480), steps (one pop per failed
   candidate; row 3's candidates ⊆ range's; far retries are gotos, no step), frames (one loop frame
   live per branch in both; row 2 none), trail (range +1 `LO_i`, rows 2-3 0): HOLDS per evaluation.
   Empty candidate: row 3 0 vs range 0 or 1: HOLDS. Wording: client-4.
5. 438 trail column: HOLDS (row 3 = 0; the shared term over-charges safely); broader key: client-3.
6. 243-244: CITATION ONLY (rev 3 §5.6 keeps the value-not-index rule for the local operand).
7. 249: CITATION ONLY (rev 3 §5.6 lists `VK_WORK` for the charges).
8. 667: HOLDS AS WRITTEN: arev's "lookbehind's bound" is the `AUTO` record's `bound`
   (`ZERO`, then `CANDIDATE + 1`, §2.1), already row 3's; range's fixed `LO_i` was never the member.
9. 458: NEEDS WORDING (add `VSK_STEP_CHAR`); also line 452, client-6.
10. 526-528: NEEDS WORDING. Nuance: a row-3 cell need not be a superset machine; a non-atomic exact
    body with a group and a failing follow hands every accept to the confirm (e.g. `(?<*(a{1,5}))bz`
    on `aaaaab`: five candidates, each confirmed, follow fails; libpcre2 nomatch, probed), so W12(a)'s pattern with a group and a
    failing follow is one.
11. 424: HOLDS (the rejected slot is per-candidate; rev 3's `LO_i` is per-entry).

**Code anchors (question 3).** `git diff --stat fd1a32021 e20dee230 -- src lib cli tests scripts` is
EMPTY; fd1a32021 is an ancestor of e20dee230; the review tree is at e20dee230. Re-grepped in
worktrees/crit-arev2: the 69 premise.out anchor lines plus `if (formw) rev.seed` :14269, the
`VM_PREFILTER_LANG` "exact" stamp :11311, `fit_rungs[]` :1309/:1360/:1402, `.u.locate.emit` :10354,
`lmwalk.c:181` (path is src/gen/lmwalk.c), `CAND_HAND_*` :9901-9907, `VK_WORK`/`VK_SEEK`/
`VK_CONSUME_BACK` in vm_stmt.h, emit_comb.c :576/:580): every symbol at its cited line, every claim
unchanged. `VK_WORK`'s operand is a C-text count (`pcrec_vm_b_work(sb, const char *)`), so row 3's
`RX_CHARGE_WORK(scan_position < POS)` needs no new operand type.

**Evidence re-run (question 3).** cells.txt's 37 byte cells through tools/probe `m`: 37/37 equal to
premise.out; the 3 UTF cells (`m u`): 3/3 equal. Every witness answer quoted in arev §1 and §3.1
(WD1, WD-G, WD-A, WD-B, WD2-WD6, WD8, W-restore, W-UTF, the atomic counter-example) matches.

**Row 3's candidate subset under ill-formed UTF-8 (pickup 9's replacement fact).** pcrec forward VM
and forward DFA on `^.$` (`-e utf8`) vs libpcre2 (`i` mode) on C0 80, ED A0 80, F4 90 80 80, E0 80 80
(overlong/surrogate/out-of-range) and C3 A9: VM = DFA = libpcre2 on 5/5. So a forward confirm and a
byte machine from the same builder agree on invalid runs here; `$_back_step` (length-consistent runs)
admits a superset of valid spans, so row 3 ⊆ range holds on these shapes. Rows 2-3 still need gate
cells (client-6).

**Roadmap A-REV (question 4).** Summary row and `### A-REV`: steps S0-S5, prerequisites (S3: stage 1
shipped, [VMREC] (c), S1, S1M, [GIVEUP-DIFF], D27 author), answer-level admission and "no speed
trigger" all agree with arev rev 1 §4.1/§3.1; roadmap at de551e514 is byte-identical at e20dee230;
nothing in it depends on the loop shape (stage 1 is named, not its spelling). Disagreements are
vlookbehind's (client-1: stage 3 HELD + D77 trigger + [LANDWALK-VM]). Ratchet: R28' has no row in §5's
table, and R03/R10 keep their old recipes (`revdet.c` present / `emit_landmark_walk` present); the
roadmap states §5 is the manager's to restate, so this is a known pending item, not a client finding.
