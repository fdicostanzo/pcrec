# l3r65 report: review r65's rulings applied to span_arms L3, and the cloud AXES reds

Lane l3r65 (opus), 2026-11-20. Branch `lane/l3r65`, cut from `lane/l3tri` 04b889b27. Review:
`docs/dev/reviews/2026-11-20-r65-l3feat.md` (its "Rulings (manager, 2026-11-20 19:25)"). Scratch:
`/var/tmp/pcrec-pcrec/scratch/l3r65/` (not committed). BASE = main's merge-base `694d91dc4`, exported with
`git archive` into `scratch/l3r65/base/` and built clean (`nice make -j8`).

## Summary

- **A (code): FIXED with a narrow pick rule.** TOP's BACK row gains a declared `displaces` column
  (`src/facts/req.c` `rb_top_back_displaces`). The run choice reads it before it compares the two runs. On a
  compile that may re-enter a forward scan, a BACK candidate displaces a consumed `best` only when that best is
  EMPTY or has no static bound. A candidate whose consumed extent is EMPTY displaces no consumed run. "May
  re-enter a forward scan" is a new walk parameter, `ReqWalkParams.fwd_reentry`. It is false only under
  `--engine=vm` and `-fno-req-handoff`. All six patterns the brief names now emit C that is byte-identical to
  BASE apart from the abi digits. Their instruction counts are at BASE (ratio 1.000 in every cell).
- **B: the measurement card is restated (doc).** The code half (back-findall-cost) is NOT built: the rulings
  file carries no owner answer.
- **C, D, F, G, H, I (doc), M, N, O, R: fixed as drafted.** J and K are recorded in the census comparison.
  L, P and I (speed) are plan rows, and so is A's step 2. Q is a register row 30 note. E is recorded as owed
  by a separate D27 lane.
- **The four process changes and the four guide lessons are applied** (critic skill + `docs/dev/guide/critics.md`).
- **The cloud AXES reds:** shards 8 and 9 were restored by A's fix; shard 1 (D3) is re-pinned once for this cause, with a reason for each pattern.
  - shard 8 (`precheck-assign-byte`): restored by A's fix.
  - shard 9 (`fd-pres-g1`): see "Axes floors".
  - shard 1 (D3 floor): see "Axes floors".
- abi stays 110. A's fix changes no emitted scaffolding: it is a fact change, and every moved artifact moves
  back to BASE's text.

## Finding A pick rule

PREMISE TEST (reproduced). At the base, `(?<=qz)x?a:` stamps `RX_DFA_PREFILTER "handoff"` (BASE) and `"memchr"`
(SUBJECT, the l3tri tip). Command: `scratch/l3r65/perf/premise.sh <pcrec>`, which runs
`pcrec --features all -p rx -o - --pattern P` and greps the RX_ stamps. The other five shapes move as the review
says (premise.sh output, BASE vs the l3tri tip):

| pattern | BASE | SUBJECT (l3tri tip) |
|---|---|---|
| `(?<=qz)x?a:` | `handoff` K 1 | `memchr`, K −2 |
| `-i (?<=foo)bar` | `handoff` K 0 | `byte-class`, K −3 |
| `-i (?<=item )done` | `handoff` K 0 | `byte-class`, K −5 |
| `(?<=a)\Kb` | `handoff` K 0 | `memchr-bounded`, K −1 |
| `(?>(?<=a)b)` | `handoff` K 0 | `memchr-bounded`, K −1 |
| `(?<=x)qzjv[a-z]*\d` | `handoff`, `emitted`, K 0 | `memchr-bounded`, `dominated`, `none` |

The x10 instruction ratio was measured by the review's EMITTED critic (225,064 -> 2,325,063 absent). My BASE
re-measure reads 225,059 on the same subject, which agrees.

THE RULE. The review ruled a declared row condition in the run choice, not an if-chain. TOP's candidate table
`rb_top_rows[]` gains a fourth column, `displaces(w, best, lo, hi)`. BACK's entry is:

    static bool rb_top_back_displaces(const RbWalk *w, const RbRun *best, int lo, int hi)
    {
        return !w->fwd_reentry || best->n == 0 || (lo < hi && best->off >= PCREC_W_UNBOUNDED);
    }

`rb_top` asks `displaces(w, &root->best, clo, chi) && rn_cmp(...) < 0`.

THE ROUTE. The ruling says "on a route that declines the forward-scan handoff at K < 0". The run choice is a
FACT, and facts sit below gen in the layer order, so the route (`cand_route_of`, the engine selection) cannot be
read there. The condition therefore reads what the facts layer can see: `ReqWalkParams.fwd_reentry`, filled in
`pf_derive_req_walk` from the options. It is false exactly where no forward scan's re-entry can exist whatever
route is chosen:
- `--engine=vm`: the hybrid prefilter is off;
- `-fno-req-handoff`: no handoff row.

This direction is conservative. A default-engine VM artifact without a prefilter (`(?<=a)a(\w)\1`) keeps BASE's
run. It does not lose L3's signed move to a K >= 0 run, so it ends up at BASE.

A first version had no route clause. It kept BASE's run on every compile, `--engine=vm` included. I measured it
(commit a6f80d2fd) and then made it route-aware (85333f2e6). The route-free version would have taken L3's whole
effect away from the VM attempt loop, which has no forward re-entry to lose.

MEASURED, BASE -> SUBJECT (lane tip). Method: `perf stat -e instructions:u`, `taskset -c 7`, 5 repeats,
median. Each pattern runs a find-all over 1 MB subjects: absent, rare, common (a match every 64 bytes) and decoy.
The subjects come from the critic's `mksubj.py`, plus a `qzjv` case. Files: `scratch/l3r65/perf/results.tsv`,
`run.sh`, `build.sh`. Answers were identical in every cell.

| pattern | absent | rare | common | decoy | emitted C vs BASE |
|---|---|---|---|---|---|
| `(?<=qz)x?a:` | 225,059 -> 225,059 (1.000) | 1.000 | 1.000 | 1.000 | abi digits only |
| `-i (?<=foo)bar` | 2,588,088 -> 2,588,088 | 1.000 | 1.000 | 1.000 | abi digits only |
| `-i (?<=item )done` | 2,438,162 -> 2,438,162 | 1.000 | 1.000 | 1.000 | abi digits only |
| `(?<=a)\Kb` | 2,459,062 -> 2,459,060 | 1.000 | 1.000 | 1.000 | abi digits only |
| `(?>(?<=a)b)` | 2,471,706 -> 2,471,707 | 1.000 | 1.000 | 1.000 | abi digits only |
| `(?<=x)qzjv[a-z]*\d` | 1,518,587 -> 1,518,588 | 1.000 | 1.000 | 1.000 | abi digits only |
| `(?<=foo)bar` | 1.000 | 1.000 | 1.000 | 1.000 | abi digits only |
| `(?<=foobar)\d*x` | 1.000 | 1.000 | 1.000 | 1.000 | abi digits only |
| `(?<=qz)ab` | 1.000 | 1.000 | 1.000 | 1.000 | abi digits only |
| `(?<=xyz)a+xyz` (BACK kept) | 0.561 | 0.432 | 0.824 | 0.325 | moves (wins) |
| `(?<=foo)` (BACK kept) | 12,712,033 -> 1,518,991 (x8 faster) | x8 | x4 | x9 | moves (wins) |
| `(?<=foo)bar --engine=vm` (BACK kept) | 1.019 | 1.004 | 1.071 | 0.861 | moves (B's cost) |

Every listed pattern is at or better than BASE. The one loss is the forced-VM row, which is B's mechanism
(the owner question back-findall-cost).

THE CENSUS, BASE -> SUBJECT. Population: all 428 corpus `(?<=` patterns (the critic's `lb.txt`) over 4 streams,
byte, `--engine=vm`, `-e utf8` and `-i`. Script `scratch/l3r65/census.py`, output `census_lb.tsv`.

| stream | SAME | ABI-ONLY | DIFF |
|---|---|---|---|
| byte | 41 | 385 | 2 |
| `-i` | 41 | 385 | 2 |
| utf8 | 37 | 389 | 2 |
| `--engine=vm` | 41 | 294 | 93 |

- The default-route movers are `(?<=foo)` and `(?<=xyz)a+xyz`. Both keep BACK, and both win.
- `RX_DFA_PREFILTER` moves on NO cell.
- The program region (`goto rx_L0;` .. `rx_accept:`) is identical on all 1,712 cells.
- The 93 forced-VM movers are L3's whole effect there: no run (or a K >= 0 run) becomes a signed K.
- The l3feat census counted 57 movers (no-decline vs decline). Against BASE, the default route now moves 2.

THE REV 3.3 ADDENDUM. Restated in span_arms §14.4 L3 as a REV 3.4 addendum. It records:
- the loss as measured against BASE;
- the pick rule;
- the re-measurement and the census;
- "the entry move still applies", limited to where the start-byte row does not dominate the pre-check
  (`(?<=xyz)a+xyz`);
- C, E, F, J, K and O;
- R-1 and R-2, copied VERBATIM from `worktrees/l3feat/docs/dev/lanes/l3feat_rulings.md` as a blockquote.

The two REV 3.3 sentences the review falsified carry struck-through REV 3.4 tags.

PLANT: S3455 removes the `displaces` column. It is DETECTED: reach ok, facts suite 1 fail of 15
(`[facts-look]`'s default-route cells).

## Finding B

- **Doc (FIX-NOW): done.** The span_arms §14.4 L3 measurement card is restated. The cost row is a SECOND SCAN per
  call (the emitted pre-check runs in front of an equivalent run-pinned prefilter that BASE judged dominating),
  not "§5.5's step back". `lb_bytes` does not bound it.
- **After A, the cost remains only where BACK is still chosen:** `--engine=vm`, `-fno-req-handoff`, and a
  consumed part with no run or an unbounded one. Re-measured on `(?<=foo)bar --engine=vm`: +1.9% absent, +7.1%
  common, 0.86 decoy.
- **Code (the dominance row): NOT BUILT.** The rulings file (`docs/dev/lanes/l3r65_rulings.md`) is empty at every
  read, so it carries no owner answer to back-findall-cost.

## Other findings

- **C:**
  - Deleted `emit_unanchored`'s K < 0 kept-hit init and `pf_emit_handoff`'s K < 0 sentence.
  - At both states the compile now refuses with the house's internal error (`pcrec_ctx_fail`, "internal error:
    ..."). As a result S3405 (the decline removed) refuses `(?<=xyz)a+xyz`. That is detected by prechecks [5.12a],
    which reports the row refused.
  - Deleted run_prechecks.sh [5.12l]'s K < 0 arm and restored `nd` to the K >= 0 form.
- **D:** run_recursion_identity.sh (B) FILEPIN is self-pinned to `f487fbd0f`, the lane's last src commit (abi
  110), with the SELF-PIN comment. ABASEPIN stays `b2d73b6b1`: the program region does not move on any lookbehind
  pattern (census) and L3 moves no lookbehind-free artifact. The abi grep checklist (lesson 4): every reader of
  109 had already moved except this pin (review CONTRACT's list), and this pin is now ticked. **The manager
  re-pins to the landing merge.**
- **F:** D-8's "WHY THE CLAMP" and the §14.4 W-L16 sentence now carry the measured verdict (REV 3.4): the clamp is
  defence in depth, and S3407 is UNDETECTED by construction.
- **G:** tuning §2.41¶7a says `max(0, start + min(0, K))`. §2.41¶8b states the floor, the per-sign stale test and
  the end clamp.
- **H:** `req_pres_spans` has one writer per `omin` entry. S3412 is re-anchored.
- **I (doc half):** the `lb_bytes` comment says that a nested lookbehind's guard can reach further and is then
  declined.
- **M:** `req_k_reentry_sound` has its own header and sits above `pf_handoff_applies`.
- **N:** added `pcrec_bound_negative` (facts.h). It is used at the stale test, the D-16 VM sentence, the decline
  and the two new internal errors. The other K-sign tests read a plain `long long` after a `pcrec_bound_bounded`
  test, so they are not this predicate.
- **O:** the emitted comments now read "after the start of (its whole run)". There are two live sites; the third
  was deleted under C. abi 110 already moves in this change.
- **R:** match_api §6.3.7¶11 and tuning §2.41¶1 now read `max(0, startpos + min(0, K))`.
- **A's spec hunk (D80):**
  - facts_listing §4.1.2¶8 states when a lookbehind run is chosen (the pick rule), with examples measured by
    `--emit-facts`: `(?<=foo)bar` default `626172` K 0 and `--engine=vm` `666f6f626172` K −3; `(?<=xyz)a+xyz`
    `78797a61` K −3; `(?<=foo)` `666f6f` K −3.
  - tuning §2.41¶1 and match_api §6.3.7¶10's `"-3"` example now name `--engine=vm`.
- **J, K:** recorded in §14.2 (REV 3.4 paragraph) and in the addendum's census. W-D2 lists `none`/dead by default
  and `bc` at −1 under `--engine=vm`. `(?<=xyz)a+xyz` `RX_REQ_BYTE` 122 -> 97 is kept, and measured faster.
- **L, P, I (speed), A step 2:** new plan rows (tags below). Q and O (shared clause) are a register row 30 note in
  architecture.md, triggered by A-POSDOM's landing.
- **E:** recorded in the addendum: owed before landing by a SEPARATE blinded D27 cell lane. Nothing else done.
- **Process changes:**
  - pcrec-critic SKILL.md: budgets as products inside one total cap, and abi normalization on abi-naming lines
    only (§5); a ruled loss re-measured against BASE (the emitted-vs-replaced lens row).
  - critics.md: lessons 1-4, tagged "(r65 l3feat ...)". The two lessons for critics.md are lessons 2 and 3 there.

**Re-aimed witnesses** (A's rule moved them back to BASE by default). In every case the L3 site is still reached
under `--engine=vm`, through the detector's vm blocks:
- `[facts-look]`: the L3 rows run under `--engine=vm` (run_pin rows under `-fno-req-handoff`, since the pin is
  an E3 fact). Ten default-route pick-rule cells were added.
- prechecks [5.12a]: three rows moved to `--engine=vm`, and two pick-rule rows were added (floor 25 -> 27).
  [3.1r] `(?<=xyz)ab` is back to BASE's `6162`.
- reqcube WIT ws4c runs under `--engine=vm`.
- DD12a(i)'s explicit presence-order witness is now `ab(c)\1x` (K 1).
- REACH probes for S1887, S3405, S3406, S3409, S3410, S3411, S3413 and S3450, plus S3408 and S3381's comments.

## Axes floors

The red run is 44838664814 at eb95f904a (`lane/l3feat`, before A). The floors were re-measured on this lane's tree
with `AXES=<deny> MEMFN_REACH_ONLY=1 bash tests/axes/run_axes.sh` (`scratch/l3r65/axes.log`):

- **shard 8, `precheck-assign-byte` (default and simd), FIXED by A's fix.** byte/c-default corpus 118 -> 125
  (floor 122); utf8/c-default 188 (floor 176). No floor file touched.
- **shard 9, `fd-pres-g1`, FIXED by A's fix.** byte/c-default corpus 927 -> 1012 (floor 949), utf8/c-default 844 -> 931 (floor 878), default and simd alike. No floor file touched.
- **shard 1, the D3 floor, RE-PINNED (one re-pin, this cause).** No member was LOST, so nothing was short. The red was the gate's two-sided population and census pins, which rose:
  - population 5147 -> 5163 (l3feat's new `.rxt` rows);
  - default cells +1 member, `(?<=ab)ab(\w)\1`, a NEW corpus pattern (l3feat's `tests/litscan/spanarms.rxt`, absent at BASE);
  - c-vm cells +22 (byte) and +23 (utf8) members, all EXISTING lookbehind-alternation patterns (`(?<=ab|cd)z`, `(?<=(?:ab|cd))x`, `(*plb:(?:ab|cd))x`, ...). Their run now begins inside the lookbehind at a signed K under `--engine=vm`, which is L3's designed effect there.
  - Before re-pinning I ran `git log --since=14.days` on d3_floor.tsv/d3_census.tsv. The only re-pin in that window is 47ba76682 (L1, a different cause), so this is the first re-pin for this cause and below the stop count.
  - Re-pinned with `D3FLOOR_REPIN=1` and a per-pattern note (the patterns are listed in d3_census.tsv). The re-run is green on all 4 cells, 60 plants ok.

## Records

- Plan tags created: [L3-CONS-REENTRY] (A step 2), [L3-BACK-CLIP] (L), [REQ-CAND-STRUCT] (P), [LB-NEST-CAP]
  (I speed, Boonies).
- Sabotage id used: S3455 (A's pick rule). No new K/D numbers.
- Design: span_arms §14.2 REV 3.4 paragraph; §14.3 D-8 (F) and D-16 (O); §14.4 L3 measurement card (B), Tests
  W-L16 (F), the REV 3.3 strikes and the REV 3.4 addendum (A, C, E, J, K, R-1, R-2).
- Spec: facts_listing §4.1.2¶8; tuning §2.41¶1, ¶7a, ¶8b; match_api §6.3.7¶10, ¶11.
- Guide: architecture.md register row 30; critics.md lessons; .claude/skills/pcrec-critic/SKILL.md.
- **Scope note, a slip I am reporting.** One `REACH_ONLY` sabotage sweep ran before I sourced
  `scripts/tmpdir.sh`, so its scratch went to `/tmp/pcrec-mech-sabotage.RYaYu2`. The matrix removed it on exit:
  no such dir remains. The five other `/tmp/pcrec-mech-sabotage.*` dirs are older and not this lane's. Every
  later run sourced tmpdir.sh.

## Validation dispatched

Local (this lane's tree, `nice`, PROCS=6):
- **`make strict`:** clean.
- **`make -k test-codegen test-startset test-lookaround`:**
  - test-codegen: green.
  - test-startset: green.
  - test-lookaround: one red, `[d27-l1-listing]`. A22 `(?<=nop)st` and C07 `(?<=a)(?<=[ab])c` listed BASE's runs again. I reverted l3tri's c424cd262 re-pin of those two rows to their pre-l3tri values. `check_listing.py` then PASSes on 88 rows.
- **Before that:**
  - prechecks: rc 0.
  - `[facts-look]`: 63 cells pass.
- **`make -k test-plan-lint test-spec-history test-claudemd-size`:** rc 0.
- **The sabotage matrix over every row I added, re-aimed or re-anchored:** DETECTED on all 12 rows: S3455, S3405 (prechecks 1 fail), S3406, S3409, S3410, S3411 (DETECTED-BUILD), S3413, S3450, S1887, S3408, S3381, S3412. My first S3405 run read FATAL because of the fields my edit lost; I restored them and re-ran.
- **The axes arm reach (`precheck-assign-byte`, `fd-pres-g1`)** and **the D3 floor**: as above.
- **NOT run locally:** the full `make test`. It goes to the cloud.

Cloud: `scripts/cloudrun --owner main --kind test --name l3r65-test` and `--kind axes --name l3r65-axes`, both on the tip that carries this report (the sha is in the lane's reply to main). Dispatched as the lane's last acts and not waited on.

## STATE AT HANDOFF

- **Rulings file:** `docs/dev/lanes/l3r65_rulings.md` was EMPTY at every read, so the last R-n applied is **none**.
- **B's code half (back-findall-cost):** not built.
- **E:** owed by a separate D27 lane.
- **For the manager:**
  - re-pin the identity gate's FILEPIN to the landing merge;
  - the D3 re-pin is on this branch.

OWED: none

Nothing is owed by this lane. E belongs to a separate D27 lane, and B's code half waits on the owner's answer to back-findall-cost.
