# Lane altrev2 — alt_normal_form.md rev 2 (review 2026-11-05 r4 applied)

Lane altrev2 (opus), 2026-11-05, branch `lane/altrev2` from main 82d95943c.
Text and probes only: no edit under `src/`, `cli/`, `lib/`, `memfn/src/`,
`tests/`. Subject: `docs/design/alt_normal_form.md` rev 1 → rev 2, applying the
RULED re-check `docs/dev/reviews/2026-11-05-r4-alt-normal-form-recheck.md` (its
RULING block, every finding, the critic texts, `verify.md`'s PARTLY verdicts).

## Premise test (done first)

SND-1 reproduced with libpcre2-8 10.46 and pcrec before any text was written
(`docs/dev/lanes/altrev2_evidence/snd1.out`, rows P0): `(?:ab|a\Kd|ad)` on
`ad` = (1,2), the merge rev 1 allowed `(?:a[bd]|a\Kd)` = (0,2);
`(?:ab|(a)d|ad)` sets group 1, the merge leaves it unset; with `\1?` on `ada`
(0,3) → (0,2). Both engines agree on every row.

## What changed (by finding; the note's §15 is the full id → section table)

- **SND-1 (the answer-level hole): closed soundly, 2b ready on the text.** The
  adjacency test is re-derived (§3.2). Only a merge moves a branch; the test
  reads the MOVED branch `j` against each branch `m` it passes (testing `i` is
  not needed, probed). Three first-match rows: (1) a head position of `m`
  disjoint from `j`'s → pass; (2) `m` of `j`'s exact width and writing nothing
  (no capture, no `\K`, no lookaround holding a capture) → pass; (3) refuse.
  The refusal set, derived and probed: a proper prefix/extension; a same-span
  writer (capture anywhere, `\K`, a capture inside a lookahead); anything the
  description cannot decide (backref, variable, call, consume callout,
  empty-able). Held and probed: assertions, capture-free lookarounds, atomic,
  and check callouts (their fire COUNT changes, which `match_api.md` §11.6¶1
  leaves unspecified; spans agree). Verbs move answers even when row 1 passes
  (`a(*COMMIT)x`), but pcrec refuses them permanently; a future verbs module
  adds a refuse row (P4 rows its witnesses). New witnesses S-w, S-h.
  Probes: 72 rows in `snd1.tsv` (57 OK, 14 libpcre2-only verb rows CERR in
  pcrec by design, 1 DIFF = a callout COUNT on `(?:(?:a|a)(?C1)b|...)` that
  altcls's existing `a|a` merge explains, `p7_altcls.out`, allowed by §11.6¶1),
  4 in `sh.tsv`, 2 in `se2.tsv`, 0 answer mismatches between the engines.
- **SIM-1: one procedure.** §3.3 now has THE PROCEDURE (rounds of merge →
  prefix → suffix to a fixpoint; last-position-first merge; fold into the
  earliest reachable head; duplicates absorbed; re-run after factoring;
  termination argued). §6's rule table withdrawn. The review's three cells
  recomputed from the text (`altnf_proc.py`, 0 mismatches vs a brute-force
  oracle): `aaa|aab|aba|bba` → `aa[ab]|[ab]ba`; `aab|bbb|bab` → `aab|b[ab]b`
  then `(?:aa|b[ab])b`; `ab|ab` → `ab`.
- **FIX-7 (phase), chosen:** the description is ONE pure function over a
  subtree with the alphabet a parameter, its own module, two call sites (owner
  at code point inside altcls; run walk at byte). Argued: the adjacency test
  needs the head of arbitrary branches, which is the description's arm table;
  a "smaller owner test" would become a second copy. It carries a WRITES bit
  for SND-1.
- **FIX-1/FIX-9: the kind row is untouched.** No `UNIT` TEXT value (it would
  have one member forever and seven readers to teach, three of them `==` tests
  nothing catches); the unit lives in the description's EMPTY arm.
- **SND-2/FIX-2 (G-2 adopted for the reading):** the island's wide-class arm
  reads the class's code-point set with TODAY's admission stated as a
  predicate on the set (every box of its canonical split a single string), so
  the island census is an equality again; widening it is [ENG-ISL-S2]'s
  class-member shape (an existing, untriggered row). Count witness S-i2.
- **FIX-3 (flag bits), by the standing rule:** 0 new public bits. Bit 10
  (`-fno-altcls-merge`) re-specified to the owner's merge at both callers
  (stages 1 and 2b), bit 11 to prefix+suffix factoring (2b), bit 44
  (`-fno-req-run-fold`) to every multi-member run position (stage 3); one
  harness-only lever (stage 2a's exact-ALT/EMPTY change); 58 of 64 used, 6
  free before and after, [IFACE-PUSH]'s ≤ 4 trigger not reached.
- **FIX-5 (info per reader), G-3 adopted:** a run is ranked and admitted with
  the figure of the reader that tests it (set: `info(S)`; cube: the hull's
  popcount); the member bound counts `|S|`; a hull is tested, never scanned.
- Also fixed: RDY-3 (rung flips listed, `RX_VM_RUNGS` census), FIX-4/RDY-2 (B0
  in three runnable parts), SIM-2 (U1 per observable, mover defined), SIM-4
  (U1b pins 67/39/330/8; "76 vs 66" withdrawn), RDY-6 (2p's contract readers;
  2p builds its own equal-width hull merge, so it does not depend on 2a),
  FIX-6 (altcls's key is already the longest literal prefix; 2b adds remainder
  re-merge, set keys, suffix factoring; `ALTCLS_FACTORED` to count both;
  witnesses S-m/S-s with measured baselines), SND-5 (no lookaround bodies until
  [VLOOKBEHIND]; reproduced), RDY-8 (per-stage existing mech rows), SND-3
  (S-e2 `(?i)xyzłw`, the bound-2 witness), SND-4, SIM-3, FIX-10, RDY-4, RDY-9,
  SIM-6, the O4/D77 sentence, SIM-5 (the bound), G-1..G-4 (named with
  triggers, no new plan row).
- `docs/dev/plan.md` [RUN-POS-SET] status line updated (plan_lint 0
  violations); `docs/design/CLAUDE.md` entry says rev 2.

## Open questions for Frank (plain words, with leanings)

1. **Covering cube (OPEN, yours).** After stage 3 a run position is a set of
   byte values, but some of pcrec's own checks can only test a "cube". For a
   set that is not a cube: (A) let those checks test the smallest covering
   cube, a named, lossy shape written as a D187 addendum (always sound, but
   weaker: Kelvin k 4 bits instead of 6, long s 3 instead of 6); or (B) have
   those checks treat such a position as a gap (no second shape; the kit's
   set-reading side still gets everything, pcrec's own pre-check keeps
   today's cuts until it reads sets). Leaning (A): sound, keeps pcrec's own
   pre-check continuous across caseless letters, temporary by construction.
2. **Switches (decided by your rule; for you to see).** No new public "turn
   this off" switch: the lowering's merge shares the existing altcls-merge
   switch, factoring keeps its switch, wider run positions reuse the run-fold
   switch, and one test-only switch covers stage 2a. Six bits stay free. The
   one trade-off: a single switch turns off merging both in user alternations
   and in the UTF-8 lowering. Leaning: fine, since each slow-down that merge
   could cause already has its own switch.
3. Unchanged from rev 1 and still yours: per-length pieces with no reader yet
   (rev 2 adds in plain words that your "now" overrides the "build only under
   a measured need" rule for that stage), wider sets per position after
   stage 3, and counting stage 2a before building it.

## Readiness after rev 2

Stage 1 and stage 2p: every listed text fix applied, ready for the readiness
re-read and a build go (after span_pick 1e). Stage 2b: SND-1 and SIM-1 closed
in text with probes; with FIX-7, FIX-6, SND-5, SND-4 and the lever/reader
lists it reads ready on this text (it needs the description module from
whichever of 2p/2b lands first). Stage 2a: census first. Stage 3: with
[POS-ONE-DETECTOR] and question 1.

## STATE AT HANDOFF

STATE: delivered. Branch `lane/altrev2`, everything committed (note rev 2,
evidence, plan status line, design index). Rulings file
`docs/dev/lanes/altrev2_rulings.md`: EMPTY at every checkpoint (no entry to
apply; last read before this report). No DELIVER block exists for this lane
(`docs/dev/lanes/altrev2_deliver.txt` absent in the worktree and the main
tree). Validation: probes only (about 85 single-pattern compiles + gcc builds,
one worktree `make -j4`); `tests/spec_history/run_spec_history.sh` 11/11 PASS;
`scripts/plan_lint.sh` 0 violations. Nothing owed: no suite run was in scope.
A resuming agent starts from the note's §15 and this report.
