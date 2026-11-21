# covcap5 report — [COVER-CAP] design rev 4 (round covcap-r3 applied)

Lane covcap5 (opus), 2026-11-15. Branch `lane/covcap5`, from main `ac91d48bb`. Design only:
no edits under `src/`, `cli/`, `lib/`, `tests/` or `memfn/`.

## STATE AT HANDOFF

- DONE, committed on `lane/covcap5`:
  - `docs/design/cover_cap.md` revision 4 (PROPOSED; REVISION 4 block first; changed
    sections edited in place). SIZE: 47.6 KB against rev 3's 42.4 KB, NOT shorter. R-1's
    deletions (outcome 4, the derivation block, plant (e), the `a{4097}` row) were about
    3 KB; the FIX-NOW text items R-2..R-13 added more (the memo record and listing columns,
    the controls table, the declared-gone/new sweep text, the guards, the re-anchors and the
    stale-text list). To compensate the rev 3 header block, §2's listing bullet, §3.1's
    "why this walk", §9's corrections and §10 were condensed.
  - The review `docs/dev/reviews/2026-11-15-r6-covcap-r3.md` with a "DISPOSITIONS (manager,
    2026-11-15)" block (R1 and R2 copied verbatim from the rulings file), and its directory
    `docs/dev/reviews/2026-11-15-r6-covcap-r3/` (COMMON, fixinduced, readiness, soundness,
    verify). Indexed in `docs/dev/reviews/CLAUDE.md`. Four spec LINE cites
    (`docs/spec/cli.md` plus a line number) in fixinduced.md, readiness.md and verify.md were
    rewritten as section cites (§2.6¶1) so `test-spec-history` stays green; nothing else
    changed. `grep -rnE 'plan\.md:[0-9]'` over the file, the dir and this report: no hit.
  - Process edits (R1): `.claude/skills/pcrec-critic/SKILL.md` §5 (design-mode run kit for a
    walk over a built machine: a script applying the unbuilt rule at any bound, plus the
    trace compiler's decision record; and the kit round's three drills) and
    `docs/dev/guide/critics.md` (two dated lessons entries: this round's change, and the
    kit round memfn-mfindcomb's lessons 1-3).
- Rulings file: R1, R2 read at start and before each commit; last entry applied: **R2**.
- `make test-plan-lint` and `scripts/lanecheck`: see the handback message (run last).
- STOP RULE: did not fire. Every FIX-NOW item went in as text; no third mechanism. One
  choice inside R-2 is mine and flagged under QUESTIONS: on a walk stopped at a branch, C7
  passes it on and C8 declines (`exact/machine-inexact`).

### PREMISE TEST (R-1's fact, reproduced)

The round's command (`kit/kp.sh`) on the round's trace compiler, built at `917a3c522`
(`git diff --stat 917a3c522 ac91d48bb -- src lib cli` is empty, so it is today's code):

    T=/var/tmp/pcrec-pcrec/scratch/crit-covcap-r3/trace/pcrec
    PCREC_KIT_PROOF_TRACE=1 $T -p rx --features all --emit-main -o x.c --pattern 'a{4095}'
      -> KITPROOF  fixed-width  k=0  routed=0  -     x.c: RX_DFA_MATCH "unwrapped"
    ... --pattern 'a{4096}'
      -> KITPROOF  anchored-A   k=0  routed=0  -     x.c: RX_DFA_MATCH "search-filter"
    ... '[ab]{4095}' -> fixed-width / "unwrapped";  '[ab]{4096}' -> anchored-A / "search-filter"

Just under the ceiling the anchored machine exists and the walk runs (C7 is reached:
`fixed-width` is today's `KN_CAP` decline); at the ceiling there is no anchored machine
(`anchored-A`, the artifact keeps the search-and-filter form). R-1 holds.

### The walk-cost witnesses (R-2), and the script that measured them

`python3 -I /var/tmp/pcrec-pcrec/scratch/covcap5/rowcost.py build/pcrec PATTERN` on this
worktree's `build/pcrec` (built once, `nice make -j8`, rc 0). It applies rev 4's stop rule
to the EMITTED `-fno-scan-edge` anchored machine through `docs/design/kit_proof/conj.py`:

| pattern | states | depth walked | stop | max rows | byte steps |
|---|---|---|---|---|---|
| `a{4095}` | 4096 | 4095 | accept | 1 | 1,048,320 |
| `[ab]*a[ab]{10}-{2000}` | 4048 | 11 | branch (L) | 1024 | 524,032 |
| `[ab]*a[ab]{8}-{300}` | 812 | 9 | branch (L) | 256 | 130,816 |

(rev 3's uncapped walk: 1.56 G byte steps on the second, per the round.) A rows-heavy
family with a long exact stretch (`w[ab]{n}w` over all `w` of 5-6 bytes) routes to the VM:
no anchored machine, so no witness of that shape was found. The script, in full:

    import subprocess, sys
    W = "/home/pcrec/projects/pcrec/worktrees/covcap5"
    sys.path.insert(0, W + "/docs/design/kit_proof"); sys.path.insert(0, W + "/docs/dev/kvcensus")
    import conj
    B, pat = sys.argv[1], sys.argv[2]
    a = [B, "-p", "rx", "--features", "all", "-fno-scan-edge"] + (["-e", "utf8"] if "-u" in sys.argv else [])
    p = subprocess.run(["timeout", "300"] + a + ["-o", "-", "--pattern", pat], capture_output=True)
    M = conj.machine(p.stdout.decode("latin-1"))
    Q = set(r for r in M.starts() if r in M.live); d = mx = tot = 0; stop = "empty"
    while Q:
        if any(M.acc_any[q] for q in Q): stop = "accept"; break
        sets = {q: frozenset(b for b in range(256) if M.step(q, b) is not None and M.step(q, b) in M.live) for q in Q}
        if len(set(sets.values())) > 1: stop = "branch(L)"; break
        mx = max(mx, len(Q)); tot += len(Q)
        Q = set(M.step(q, b) for q in Q for b in sets[q]); d += 1
    print(len(M.live), d, stop, mx, tot, tot * 256)

## FINDINGS APPLIED BY ID

- **R-1** (FIX-NOW, R1 (a)-(d)): `PCREC_MAX_EXACT_SPAN` deleted everywhere (title, R5 block,
  §0, §1 table, §1.1, §3.1, §3.3, §3.5, §3.6 Q3, §4.3, §4.5, §5.2-§5.4, §8, §9). (a) §3.1
  quotes the `limits.def` row: LABELLED (`compile budget`, `-D`); its row text has no
  derivation, which lives in `limits.h`'s [ENG-ABS] block (summarised, not invented); a
  `desc` pointer text is proposed for stage 1. (b) §3.1 "PAST THE CEILING": no machine,
  `anchored-A`, `exact_len` 0, today's behaviour, and the fraction case needs another
  producer ([MATCH-KNOWN], also in §1.1 (iii)); the step 4095 -> 0 and the states-not-
  positions caveat are stated. (c) outcome 4, `over-max`, plant (e), `a{4097}` gone; the
  bound's witness pair is `a{4095}` / `a{4096}` (§5.3). (d) §9 Q2 opens with the
  correction. The kit request's number is 4095 by derivation. §8 names the bound that
  binds. Also noted: `compile.c`'s comment calling the ceiling equal to
  `PCREC_MAX_DFA_STATES_TABLE` contradicts `limits.h`; listed as stale text (§5.5).
- **R-2** (FIX-NOW): §3.1 FORM: stamp dedup; the walk ends at `min(L, first accept)`;
  `exact_len` = `L` on a branch, else `k`; C7 passes a branch and C8 declines; the
  "keeping only the sets past L" sentence is gone. TERMINATION AND COST restated in bytes
  (256 per row), with the bound and the measured witnesses above; §5.1's compile-cost row
  carries them with the watchdog command.
- **R-3** (FIX-NOW): §3.3 THE RECORD (fields, 16-bit counts, arena set store, Job lifetime,
  written on every decision, `MkEnd` filled from it on `cover`, last decision per
  encoding) and THE LISTING (columns `encoding | why | k | exact_len | sets`, the `unasked`
  row, no kit ask from the listing, [5¶2]); §4.5 adds the [3¶3] hunk; §5.3 names the
  loader's `$2 == "cover"` selection.
- **R-4** (FIX-NOW): §3.3 WHERE A STRETCH IS STATED: covers and bounded-width decisions,
  X0 given `wmax`; other rows read `-`; stated/checked/unstated counted (K35). §3.6 Q2
  names `z2.py` `records()` as the re-pointed instrument.
- **R-5** (FIX-NOW): §3.6 Q2 is a per-control table (shares / sees); the hull containment
  is re-pointed into `pcrec_cover`'s trace block with plant (f) (§5.4).
- **R-6** (FIX-NOW): §5.2: declared-gone fact and declared-new section in the facts
  stream, judged both ways; the dumps stream's declarations named.
- **R-7**: moot (no new limits row); §4.5 says the `kind` vocabulary is untouched.
- **R-8** (FIX-NOW): §5.2 predicts by the width's lower bound, with the two named movers.
- **R-9** (FIX-NOW): §3.1 THE SLICE'S THREE GUARDS: believed subsumers named (C1, C5,
  character-stepping), not claimed; kept as three lines in `cc_anchored` with their own
  details, counted (expected 0); `exact/producer-unstated` in §5.2's INTO list;
  `PF_WHY_ERASED`/`PF_WHY_MARKED` on the deletion list.
- **R-10** (FIX-NOW): §3.1 deletion list and §5.5 stale-text list extended with every reader
  the round named; the two non-existent sites struck; `INTERNAL_H` home; the history rule
  (which dirs are history; living design notes keep a dated supersession note).
- **R-11** (FIX-NOW): `a(?:b|c\z\W)` `2:97,98` added to §5.3's facts rows; facts floor 6 ->
  15 (7 new rev-3 rows minus `a{4097}`, plus this row and the ceiling pair).
- **R-12** (FIX-NOW): §5.4: S1131, S1136, S1139 re-anchors; S1149's cloud-table
  regeneration; the facts-plant REACH rule.
- **R-13** (FIX-NOW, stage-1 build item, text now): §3.5 names the `cover_window` reorder;
  plant (d)'s row says its red is the named internal error after it.
- **R-14** (NOTED/PLAN): §3.3's NOTED bullet; the general decisions-why section is PLAN for
  main with its trigger.
- Process change (R1): SKILL.md §5 and critics.md, as listed above; the kit round's three
  lessons added to both.

## QUESTIONS

For the owner, in plain words, the corrected fact first:

1. **The maximum span length.** Correction: rev 3 said that past its 4096 limit the first
   4096 positions would stay proven. That was false. The exact stretch is read from the
   compiled anchored machine, and pcrec already refuses to build that machine past 4096
   states, so the most it can prove is 4095 positions; a pattern needing more gets no
   proven positions from this reading and runs exactly as today. Wide patterns hit the
   ceiling sooner, because it counts machine states, not positions. Rev 4 adds no new
   number and treats that existing ceiling as the maximum. Leaning: accept it; proving
   part of a longer pattern is a later item that needs a different reading.
2. **Reading the stretch from the compiled machine** (unchanged from rev 3): one reading,
   checked against PCRE2 in the tests, instead of two readings compared on every compile;
   no current cover lost, 18 small ones gained, about 430 lines deleted. Leaning: accept.
3. **The earlier ruling that keeps one test pattern's cover** (unchanged): it stands.
   Leaning: keep it.
4. **Build go for stage 1** (pcrec only, spans up to 32), after the one readiness check
   that follows this revision. Leaning: go if that check finds no design-level item.

For the manager (not the owner):

- R-2's ordering choice: on a walk stopped at a branch, C7 passes and C8 declines, so the
  listed `why` moves from `fixed-width` to `exact/machine-inexact` on such compiles (no
  artifact moves). The alternative (C7 reads the `width` fact) keeps today's `why`s but
  adds a second reading of the width to C7. Leaning: as written.
- The round's two proposed guide lessons (name every existing limit on the object a new
  limit bounds and run its witness; run a re-pointed instrument on true values first) were
  not in R1's accepted list, so they are not in the guide. Leaning: accept lesson 1 into
  the premise lens.
- The stage-1 `desc` pointer on `PCREC_ANCHORED_MAX_STATES` (§3.1) moves `--list-limits`
  output by one cell. Leaning: include it (it makes the cover's bound discoverable).
