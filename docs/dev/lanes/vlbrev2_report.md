# Lane vlbrev2 — vlookbehind design rev 2 (review 2026-11-05 r6 applied)

Lane vlbrev2, opus, 2026-11-05. Branch `lane/vlbrev2` from main `814fc1cb2`. TEXT ONLY: no edits
under src/, cli/, lib/, memfn/src/ or tests/. Subject: `docs/design/vlookbehind.md`, now
**PROPOSED rev 2**. Applies the RULED re-check `docs/dev/reviews/2026-11-05-r6-vlookbehind-recheck.md`
(every disposition ACCEPTED). Evidence: `docs/dev/lanes/vlbrev2_evidence/premise.out`.

## Premise test (the brief's)

`vm_cost_look` (src/gen/emit_vm.c) reads `c.frames += 1 + a->u.look.nbranch; c.trail += 2;`. The
constant 2 is CONFIRMED. `vm_plan_capacities` sizes a bounded pattern's trail at
`cost.trail + 1`. Today, `(?<=aa)x`, `(?<!aa)x`, `(?<*aa)x` and `(?<=a|bc)x` all emit
`RX_TRAIL_FRAMES 3` (measured, `premise.out` §2).

## V1, the trail sizing: stated EXACTLY (the STOP RULE did not fire)

The new term is `vm_cost_look`'s `trail += 2 + Σ_{i : lo_i < hi_i} (hi_i − lo_i + 1)` (note §5.5).
It is derived from the code:
- each `range` branch writes `D_i` once, plus once per decrement, and there are at most
  `hi_i − lo_i` decrements;
- no pop inside the evaluation removes these entries;
- exhausted branches' entries stay live;
- the body's trail is `vm_cost_alt`'s max on top.

How tight it is:
- **exact** on the witness: `(?<=a{1,2})x` on `bax` peaks at 4 entries (MARK, POS, `D = 2`,
  `D = 1`), and the term charges 2 + 2;
- a safe over-charge elsewhere;
- `1 + nbranch` frames stays a safe bound.

W12 is the witness:
- (a) with today's constant, `bax` overflows a capacity of 3 at the first decrement
  (`PCREC_ERR_FRAMES`; libpcre2 [2-3]);
- (b) one entry short per branch shows on `(?<=a{1,2}|b{1,2})x` / `abx` (peak 6, sized 5;
  libpcre2 [2-3]). One short on a SINGLE range branch is masked by the capacity's `+ 1`, which is
  why (b) needs two range branches.

## Two findings rev 2 adds beyond the review's list (fix-induced from V1; for the diff check)

1. **The `range` loop is a trail cycle, so K134's structural rule puts a trail checkpoint on its
   back edge.** The check is `vm_goto`'s `vm_jump_closes_trail_cycle`, and it fires on any spelling
   of the loop. An artifact with a `range` branch therefore gains `vm_emit_trail_compact`'s helpers
   (38 lines measured on `(?>(a)|b)+c`), and the margin `nset` grows by 2 per range branch.
   - Compaction does not relieve the sizing: the overflowing write precedes the checkpoint.
   - Under (A) this moves only new artifacts. Under (B) every lookbehind artifact gains the
     helpers, and §13's (B) cost list now says so.
2. **Beyond the 3072 auto-trail clamp** (about 12 full-width range branches on one path at the 255
   policy), D44.1's honest-stamp rule owes a ceiling. So `vm_cost_look` also sets `growable` and
   `pt += (number of range branches)`. This is the safe direction, and it changes no stamp where
   the requirement fits. It is a proposal for the re-check's diff-check critic to confirm or
   refute.

## What changed in the note (by finding; the note's §16b is the full map)

- **V1:** REVISION 2 block; G4 trail bound; §5.1 trail-growth bullet; §5.1b second table (trail
  column) and checkpoint bullet; §5.2's magnitude sentence scoped (control vs storage); §5.5 "Trail"
  derivation; gates 1/4 (FRAMES is a difference); W12; §11.2 lesson.
- **V2:** rewrite items 5 (negative end-check = SELECTION) and 6 (labels allocated only for
  `range`); §13 (B)'s benefit line corrected ("one loop, plus a one-column end-check choice").
- **V3:** back-step and work render `(size_t)slot_values[<slotx>]`; `slotx` stays an index (§5.6).
- **V4 (RULED):** `D_i` is a `SLOT_COUNTER` slot. Each counter-family reader is dispositioned: base
  chain shift in range artifacts only, name/legend/sum/VmSnap already there, no listing row today
  (pre-existing gap), so no `ir_listing.md` hunk, no new `Vm` fields, one `vm_slot_ctr` comment
  widened, independent of `-fno-counter`. One shared row predicate read by count pass, cost pass,
  emitter and texts.
- **V5:** role/note texts are `-fcomments` C plus listing; the seven `range` replacements listed;
  gate 3 reads the label role.
- **V6 (RULED (i)):** the zero-width-repeat class is a stated divergence in G1, gate 3, stage 2,
  §9's extract list and a §10 hunk sentence for `pattern_language.md` §7.4¶5.
- **V7:** gate 2 = `tests/codegen/run_recursion_identity.sh`, `differing = 0`, refusal-mismatch =
  the flipped manifest (22 distinct / 30 rows call-free at this freeze, counted by the build from
  population.tsv), re-pin in the landing commit.
- **V8:** S133/S134 range twins; codegen fixture `residlbrange (?<=a{1,2}|bc)x`, `back_step:2`
  (libpcre2 ACCEPT lb 2); S-U4 re-aimed at gate 3 (figure; run at build); S136 "every branch or
  branch 0"; S135 re-anchor under (B).
- **V9:** new §5.2a: `LA_LOOKBEHIND_BRANCH_MAX` 65535 / `LA_LOOKBEHIND_VAR_MAX` 255, unit
  `"chars"`, EXISTING kind `"compile budget"` (precedent `PCREC_MAX_GROUP_DEPTH`, so no schema
  hunk), override `NONE`, anchor `3.11`, home `MOD_LOOKAROUND`; `limits_check.sh` manifest +2 and
  78 → 80; "65,535" comma-grouped; the `hi > INT_MAX` arm deleted.
- **V10 (RULED):** stage 1 deliberately reverses the [DD-14.LB] ruled perr (both deferred rows
  re-probed: ACCEPT lb 2, [0-2] on `ab`). The decision-entry text the build owes is in §10. Both
  extracts are re-cut by the manager. The D27-owned corpora are flipped by stage 0's D27 author,
  or else by named manager rulings in the landing commit.
- **V11:** INTERNAL has two producers (D72's region-exit guard); three comments join the readers.
- **V12:** gate 1's harness is `tests/lookaround/run_lookaround_diff.sh`; `match_api.md` §6¶18;
  both mrl.c width headers; `branch-reset` is a module; 32 rows (24 distinct); shape 7 widened.
- **V13-V14:** §5.1's composition with `vm_look`; §5.1c's framing sentence per cell.
- **V15:** G1's stage-1 dependency on owner Q2 (§0, gate 3, §13 Q2). The PLAN line went into
  `docs/design/plan_row_bodies/IFACE-PUSH.md` as a dated CANDIDATE. The row has a candidate list,
  but its plan.md charter is at plan_lint's 6-line limit (PL11 fired when I added it there).
- **V16:** the `(*ACCEPT)` width line in §14, owned by the verbs module.
- **V17:** NOTED. Stage 1 takes the per-row columns and the one row choice. The rung-ladder row is
  named in §14 as the manager's to file (not filed).
- `docs/design/CLAUDE.md`: the status line now says rev 2.

## The §5.1 change list arev.md's rev 1 must pick up (arev.md not edited)

arev.md reads vlookbehind §5.1 as its finisher contract (§2.3, "L: vlookbehind §5.1's per-candidate
step"), its row 2 `gate` finisher ("the `range` row's loop, unchanged"), row 3 `commit` ("§5.1's
per-candidate step"), G6 ("built by vlookbehind stage 1's range loop") and G10 (the work charge on
a VM host). Rev 2 changes these, and each is a pickup:

1. **The finisher writes the trail.** Each candidate leaves one live trail entry (`D_i`), and the
   cost pass charges `2 + Σ_range (hi_i − lo_i + 1)` (§5.1 trail bullet, §5.5).
   - arev's §2.3 says `VK_AUTO` "never touches frames or the trail". That stays true of the walk.
   - The FINISHER does touch the trail, so G10's "work charge on a VM host" becomes "work AND
     trail charge". The `gate` row admits a branch to the same loop, so its static trail charge is
     unchanged (the gate removes runs, not the bound).
   - `commit` (row 3) hands candidates from the machine instead of decrementing. It must state its
     own trail term, or it re-steps from a frame-saved hand.
2. **`D_i` is a `SLOT_COUNTER` slot** (§5.1, §5.1b), not a new family. arev's operand list for the
   finisher's loop slot should name it.
3. **The loop is a K134 trail cycle.** Its back edge carries a checkpoint, and the artifact gains
   K134's compaction helpers (§5.1b). If `commit`'s moving-floor loop writes the trail, it is a
   cycle too. arev's byte-identity and size statements for S3/S5 inherit this.
4. **Operand meaning.** The back-step and work charge read `(size_t)slot_values[<slot>]`, never
   the index (§5.6). A `commit` hand passed as an operand follows the same rule.
5. **The end-check is a declared selection, not a rewrite** (§5.1b item 5). A `range` branch
   declines on both polarities, and only `one-length` keeps `RX_R_INTERNAL`. arev's `gate`
   "negative branch cannot match" decision sits beside a declining finisher, never a hard return.
6. **Labels.** `L_try_i`/`L_adv_i` exist only for `range` branches (§5.1b item 6). A `gate`/`exist`
   row that bypasses the loop for a branch must not allocate them, or all-fixed artifacts renumber.
7. **The composition with `vm_look`** (§5.1, `[r6 V13]`): `L_neg_ok` sits below every `L_adv_i`
   frame, and `L_ok` cuts to the mark. arev's `exist` row (no VM run) must leave the same frames
   state as a loop that exhausted or succeeded.
8. **The per-row reader table** (§5.1b's second table): arev's §3.1 exit rows should declare the
   same columns (slot, push sites, trail, labels, checkpoint, texts) for each row it adds. This is
   review r6 V17's "each row declares its columns for every reader".
9. **Gate 1's instrument** is `tests/lookaround/run_lookaround_diff.sh` (§6). arev's S3 gate
   ("libpcre2 differential 0 differences outside D142's class") should name it, and should count
   the zero-width-repeat divergence (V6) on its own line.
10. **Under owner Q1 (B)**, every lookbehind branch is `range`, so "Stage 1's range artifacts are
    the base" covers every lookbehind artifact. That includes K134's helpers.

## Validation (text lane)

- `scripts/plan_lint.sh`: 0 violations over 300 rows (after moving the candidate line to the row
  body; my first spelling in plan.md raised PL11, and that edit was reverted).
- `scripts/check_claudemd_size.sh --all`: 349 files within limits.
- Pre-commit spec checks: 52 passed, 0 failed. Two dangling-cite failures on the first attempt
  (the new limits subsection does not exist yet; this note's own § numbers sat beside spec file names) were
  rephrased.
- Probes:
  - libpcre2 10.46 as a library (rev 1's `probe.c`): 10 match cells, 5 compile cells, 2 DD-14.LB
    rows;
  - pcrec at this branch (`make -j4` once, then `build/pcrec --features all`): 5 capacity reads,
    3 zero-width/refusal compiles, the K134 helper span.
  - All of it is in `premise.out`.
- No suite run. None is owed (text only).

## STATE AT HANDOFF

STATE: delivered. Branch `lane/vlbrev2` is committed: the rev 2 note, `docs/design/CLAUDE.md`,
`plan_row_bodies/IFACE-PUSH.md`, evidence, and this report. The rulings file
`docs/dev/lanes/vlbrev2_rulings.md` was EMPTY at every checkpoint, so no entry was applied. Owner
question 1 stays OPEN ((A) declared selection vs (B) loop everywhere plus abi), and so does
owner Q2. Next, per the review: a short diff check of rev 2's §5.1b/§5.5 by one critic (V1, V2,
V4), including the two fix-induced items above. Then the build go waits on owner Q1 (and Q2 for
G1 at stage 1).
