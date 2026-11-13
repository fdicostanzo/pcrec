# Lane partd2: R-38 Part D finished (merge, rename, D3, the F1 overlap)

STATE: delivered (in-tree validation below; the box gate and the cloud kinds OWED). Branch `lane/memfn-partd`,
worktree `worktrees/partd`, base main c5b3c2c22 (merged here). Design of record: `docs/design/memfn/part_d.md`
rev 4. Starting state: `partd_report.md` (D0-D2 and R-41 built, D3 not).

## Summary

- **Main merged** (c5b3c2c22, unit 3.0b, MF_SITE_ABI 28). The branch keeps **MF_SITE_ABI 29**. Every reader was
  re-grepped: all hits are history citations. Nine conflicts were resolved; two of them needed code.
- **R-41's constant is now `MF_HEAD_MAX_UNBOUNDED`**, the name agreed with main. Five files changed (code, plant,
  mech row); journal and history text unchanged.
- **D3 is built** per part_d.md §5.1 D3:
  - the record is kept by `collect.py`'s `summarize`;
  - census0.py holds the census's ONE parser of it, a `deleg:runpart` population branch, and the `settest_cls`
    cn+ bound (both copies, vcls.py too);
  - the `G2SITE` join and G2's own counts (`G2PRP`);
  - the check `memfn/tests/g2/run_part_census.py`, run per target in `run_g2_pres.sh`, with floors;
  - the production-path check `runpart_prod.py`;
  - plants p11/p12/p15 (S3120-S3122, each RED by its own detector) and p14 (RED, run in the gate).
- **d27fix's F1 is honoured.** `run_rank` takes its caller's run options. `translate` ranks a pinned R's term under
  its member's tie (`member_opts`, d27fix's form).
  - Probe (partd + d27fix, scratch worktree): `make test-memfn-d27frame` passes 6,937,301 checks, 0 failed.
  - Control (the tie line removed): RED, 160 failures, F1's own message.
- **One semantic conflict from the merge, fixed in G2:** 3.0b's window `table_name` check against Part D's sites
  (site 878, Checks). In-tree validation is all green.
- **Expected pcrec movers: zero.** No pcrec emitter was edited. The proof is the box gate, `597-kit-partd2-gate`
  (OWED).

## Merge

`git merge main` (c5b3c2c22) was run alone. Its conflicts, and how each was resolved:

| file | resolution |
|---|---|
| `docs/dev/history/claude_md/docs__dev__lanes.md`, `memfn/docs/journal.md` | append-only: both sides kept |
| `memfn/tests/CLAUDE.md` | main's lines (b30bland trimmed them into NOTES.md) plus Part D's additions, folded in; 11,534 bytes |
| `memfn/include/memfn.h` | `MF_SITE_ABI 29` kept; the history comment holds main's 28 text, then 29's |
| `memfn/src/ofsskip.c` | main's new `fn_row.pick` column: `fn-every-pos` takes **FF_NONE** (no find: every candidate tested; never served through `ofs_fn_serves`, whose `derived` is 0); `ofs_fn_serves` takes main's `fd_form *pick` with Part D's three-argument `ofs_fn_applies(p, h, 0)`. kit.h's comment names the new row |
| `memfn/src/window.c` | `build_runs` takes BOTH the art (for `run_bytes`' refusal, Part D) and main's allocator: `build_runs(d->art, al, w)` |
| `memfn/tests/g2/g2_win_gen.c` | main's framed `mf_wdecide(.., NULL, MF_WCALL_NONE, ..)` with Part D's messages and `mf_art_error` |
| `memfn/tests/run_g2_win.sh` | PLANTS: the union (3.0b's S3084, S3089-S3093, S3096, plus S3116-S3118) |
| `tests/memfn/decider_census.py` | main's `MEMBER_COUNT = 70` with Part D's run_rank comment (Part D renamed a member and added none) |

- `tests/ci/cloud_mech_shards.tsv`: main's version taken, then regenerated with `cloud_units_plan.py mech --measured
  ... --shards 90 --write`. It was regenerated again after rows S3120-S3122: 50 rows unmeasured.
- `memfn/src/CLAUDE.md` came out of the merge at 12,341 bytes, over its 12,288 limit. E-find's renderer detail moved
  to `memfn/NOTES.md` (not `memfn/src/`: C16 holds every file there), and the file is now 12,162 bytes.
- `make strict` was green after the merge (commit 737715f5a).
- MF_SITE_ABI readers were grepped (`MF_SITE_ABI ... 28|29`, `.abi = 28|29`) across memfn/, tests/, scripts/,
  docs/spec/, src/ and cli/. Every hit cites history ("MF_SITE_ABI 28: ..."); none pins the value.
- r33_sim's `probe.c` called the pre-3.0b `mf_wdecide(art, s, &r)` and no longer built. It now asks the decision
  alone (`NULL, MF_WCALL_NONE`). D3's production path needs it.

## Rename

`MF_HEAD_UNBOUNDED` became `MF_HEAD_MAX_UNBOUNDED`. Every reader was found by grep:
- `memfn/include/memfn.h`: the define and four comment mentions;
- `memfn/src/presence.c`: the decline and its comment;
- `memfn/tests/g2/g2_pres_gen.c`: the R-41 case;
- `memfn/tests/run_g2_pres.sh`: S3119's plant text;
- `tests/mech/sabotages/S3119_unbounded_head_not_declined.sh`: its anchor; the anchor check resolves.

Not renamed: `memfn/docs/journal.md`, `docs/dev/lanes/partd_report.md` and the history index, which stay as written.
D27 contract excerpt (memfn.h):

```
#define MF_HEAD_MAX_UNBOUNDED ((int64_t)1 << 40)   /* mf_site.head_max's stated "unbounded" K (R-41,
   MF_SITE_ABI 29) */
```

## D3 built

Each part_d.md §5.1 D3 item, as built:

- **The record.** It already existed: D2's print, `MFTRACE run_part_terms`, on the define path only.
  - `docs/dev/lanes/r33_sim/collect.py`'s `summarize` keeps each record raw in `trace.parts` (RDY-1).
  - Each compile line now also carries pcrec's own `_REQ_RUN`/`_REQ_WHY` stamps (`req`), read off the emitted text.
- **The census's ONE parser** lives in `docs/design/memfn/span_pick/census0.py`:
  - `run_part_record` (the line), `run_part_classes` and `run_part_unspelled`;
  - `spelled`: one member, or two members one bit apart;
  - `runpart_pop` (a site's records into verify (form, cls) pairs).
  - Classes: each multi-member SET term is (`settest`, `settest_cls`); the RUN term is (`rc-<row>`, its class); a
    scan-less part is (`every-pos`, `-`).
  - `units()` gains the NEW branch, one `deleg:runpart` unit per record (RDY-3). `sweep`/`forecast` count those
    units apart; they price only window alternatives.
  - The vcls fold (`vcls_lines`) and `slot/vcls.py` both read `runpart_pop`, so both use one parser.
- **settest's classes are bounded**: c1, c2, cn = 3 to 7 compares, cn+ above 7, UNMEASURED.
  - Both copies changed in one commit (census0.py and vcls.py).
  - `slot/plan.py` lists cn+ and `every-pos` in a new `UNPLANNED` table. It prints them as UNREACHED and never
    schedules them: `plan.py report` shows `UNREACHED verify_cmp.settest.cn+: UNMEASURED ...`.
- **The goldens** were re-pinned over the J0 sweep they were cut from (sha256 b88599f6..., swept at 71cad723e):
  - `vcls.out`: one site moves from cn to cn+ (cn 7 became cn 6 plus cn+ 1).
  - `census0_cards.out`: the same verify line. At each gap, 12 units that cn's row used to price are now
    `unpriced: no card kit.verify_cmp.settest.cn+.p0` (as designed), and the mover counts drop by 1.
  - `census0.out`: byte-identical.
  - Control: `census0_cards.out`'s data lines equal `vcls.out`'s, byte for byte (re-checked).
  - READING: the J0 sweep holds no records (it was collected before D3), so the new population branch adds nothing
    to these goldens. Re-collecting J0 at today's tree would move every golden for reasons that have nothing to do
    with D3. The re-collected sweep with records is the gate's production-path step instead (below).
- **`r33_sim/sim.py`** was read, as the design asks. It builds units from a site's `alts` and from parts that carry
  `alts`. A derived part has none, so sim.py skips it, as census0's `units()` did before D3. It simulates window
  picks, and a derived part has no window pick, so it was not changed. The reader list is complete.
- **The join (RDY-4).**
  - `g2_pres_gen.c` prints `G2SITE id=N` on stderr after each site's define, under `G2P_G2SITE`.
  - `g2_pres_run.c` (recording build) prints `G2PRP id=N unspelled=U scanless=S measured=M` per classified part:
    - `unspelled` counts the positions in C2's MEASURED extent whose set G2's own generator cannot spell;
    - `scanless` is 1 where the reply states no scan;
    - `measured` is 0 on a no-background site, whose extent is the reply's.
- **The check** is `memfn/tests/g2/run_part_census.py`, run by `run_g2_pres.sh` on each target's default pass.
  - It runs the trace generator (the kit built `-DMF_TRACE`) over the same arguments. The trace kit's site file must
    be byte-equal to the plain kit's pass.
  - Population (RDY-2): sites whose define chose an ofsskip FUNC BODY row (`END table=fn phase=define chosen=fn-*`).
  - Per site in the population:
    - exactly ONE record;
    - the census's unspelled count EQUALS G2's (measured sites);
    - the census's every-pos count EQUALS G2's scan-less count;
    - the join holds both ways.
  - Sites whose define chose no fn row are counted apart: declined sites, and the whole generic pass.
  - Floors (literals, first green run): `FLOOR_D3="pop:502 unspelled:750 everypos:9"`.
  - Measured on each of x86-64-v3, x86-64 and generic: pop 558; unspelled 833 = G2's 833; everypos 9 = G2's 9;
    nobg 10; 18 no-fn sites.
  - The generic pass: 576 sites, 558 records, counted apart, 0 failures.
- **The production path (RDY-1)** is `docs/dev/lanes/r33_sim/runpart_prod.py`. Every compile whose artifact stamps
  `_REQ_RUN` other than `none` AND `_REQ_WHY` "emitted" must carry exactly one record.
  - READING: the design says "`_REQ_RUN` not `none`". Measured, a "dominated" stamp has no derived part: `hello`,
    `ab\dcd` and `xy/users\d+` stamp a run with WHY `dominated` and print 0 records, while `foo\w+bar` and
    `qq[a-z]+zz\d` stamp `emitted` and print 1. The literal reading would red a correct build, so the check keys on
    "emitted", which is also read off pcrec's text.
  - Sample of the first 600 corpus patterns (lane tip): 37 emitted, 37 with exactly one record, 0 records without
    the stamp: GREEN.
  - p14 planted, first 300: 16 emitted, 0 with a record: RED.
  - The whole corpus (5,489 compiles) is the gate's step (4).
- **RDY-5** (the pcrec-artifact floor, census >= `DIFFER_PINS` movers) is ARMED AT THE JOINT LANDING, per the design
  (0 on the kit branch). It is NOT built here.

Plants. Each was run with `run_g2_pres.sh --plant ID`; the logs are in `/var/tmp/pcrec-pcrec/scratch/memfn/partd2/`.

| id | plant | detector | measured |
|---|---|---|---|
| S3120 | p12: no record for a scan-less part (`!quiet && q->plan_hint != MF_NO_PRED`) | D3 EVERY-POS | RED: `x86-64-v3.0: D3 EVERY-POS: site 440: the census counts 0 every-pos part(s), G2 rendered 1` |
| S3121 | p15: the record printed on the quiet path too (`if (1)`) | D3 RECORDS | RED: `site 0 (fn row fn-memchr) carries 2 run_part_terms records, not 1` |
| S3122 | p11: the census parser skips SET terms (a census0.py plant, `@c0/` in plant_spec) | D3 UNSPELLED | RED: `site 430: the census counts 0 unspelled SET terms, G2's measured extent holds 3` |
| p14 | collect.py's `summarize` drops the record | runpart_prod.py | RED by hand (16 fails over 300); in the gate over 600. No mech row: no suite runs collect.py |

- p15's REACH: the trace build's `mf_define` re-asks its own site quietly (compose.c `ask_sel`, rule 2), so the plant
  reaches every site carrying the part. No re-aim was needed.
- S3120-S3122 are also mech rows (suite `g2pres`). The main run's D3 step reads the planted tree's `memfn/src` and
  `census0.py`. The anchor check resolves (1,289 rows).

## Part D overlap with d27fix

- **d27fix's F1**: `translate` ranks the RUN term under the art's tie, while the verify-NO member uses the stretch
  row's tie. Under `run-tie-left` the ranking's first position is then not the member, and the loud check
  fires: "the run ranking's first position ... is not the run member".
- Part D had moved the ranking into one shared function, `run_rank` (translate and run_part_terms). The fix keeps
  d27fix's form:
  - `member_opts(d, r)` is the one home of the member's options; `run_member` asks it.
  - `run_rank` takes `kit_run_opts o` from its caller.
  - `translate` passes the art's options, with `ro.tie = member_opts(..).tie` when `d->pinned`.
  - `run_part_terms` passes the art's options (a presence site has no member).
  - S3006 is re-anchored onto run_rank's one-line call (commits a7d3f6322, c775d6514).
- **Proof.** I made a scratch worktree, `worktrees/partd2-probe` (`--detach`, at c775d6514), merged
  `lane/memfn-d27fix` into it (scratch commit 669b70153, never on a branch), and ran `make test-memfn-d27frame`.
  - Merge conflicts in the probe: window.c's three hunks and S3006 were resolved to OUR side (it subsumes d27fix's
    F1 in Part D's shape); the history index kept both sides. **The real merge of d27fix will meet the same
    conflicts: take lane/memfn-partd's side in window.c and S3006.**
  - Result: `PASS d27frame: 6937301 checks passed, 0 failed, floors held (floor 6500000)`; the control and empty
    runs are red as designed.
  - CONTROL (the `if (d->pinned) ro.tie = ...` line removed in the probe): `FAIL d27frame: passed=6935532
    failed=160`. The failures are F1's message: "the run ranking's first position 0 is not the run member".
  - The probe was removed with `scripts/wtprune --apply --force --quiet-min 3 partd2-probe`; the diff was saved
    under `worktrees/.wtprune.force/`.
- lane/memfn-d27fix was NOT merged into lane/memfn-partd.

## Identity and movers

- No pcrec emitter (`src/`, `cli/`, `lib/`) was edited by partd or partd2. The expected pcrec movers are zero.
- **The proof is box gate job `597-kit-partd2-gate`** (OWED; script
  `/var/tmp/pcrec-pcrec/scratch/memfn/partd2/jobs/gate.sh`). BASE = c5b3c2c22, the main merged here, built FRESH by
  `git archive`; REF is its `build/pcrec`.
  - (1) emit_sweep REF vs the tip on every declared identity arm. That is 68 from `--list-ident-arms c5b3c2c22`,
    plus 4 CPU-target arms, 72 in all. `memfn-run-verify-wide` is SKIPPED and logged (REF predates the option),
    so 71 arms run.
  - (2) the deny's ASSERT_ZERO cells (`--memfn=no-run-verify-wide`, byte and utf8 bases, c-default/c-vm) on the
    tip alone.
  - (3) every G2 plant: presence S3106-S3114, S3119-S3122; window S3116-S3118, S1409.
  - (4) D3's production path: whole corpus GREEN, then p14 RED.
- The old partd gate (597-kit-partd-gate) shows `cancelled_by_hand` in the queue; it never ran.

## Checks

In-tree, on the lane tip:

| check | result |
|---|---|
| make strict | after the merge: green; after the rename: green; after F1: green |
| run_g2_pres.sh (the presence family with D3) | 8,051,517 passed / 0 failed; RPCENSUS equal on all 3 targets; EXIT 0 |
| run_g2_pres.sh --plant S3120 / S3121 / S3122 | RED / RED / RED, each by its own detector (rc 0) |
| runpart_prod.py over 600 corpus compiles | green (37 emitted, 37 exactly one); p14 RED |
| d27frame on partd + d27fix (probe) | 6,937,301 / 0; control red (160) |
| anchors (scripts/m6read_check_sab_anchors.py) | 1,289 rows, 1,339 sites, all resolve |
| nice make -j8 | rc 0 |
| make strict | rc 0 (again after the G2 fix) |
| make test-codegen | rc 0 |
| test-memfn-finder | first run RED: purity row `+C-member(verify-NO)` no longer matched once (member_opts took d27fix's `return ... ?` form); re-anchored to d27fix's own text; rerun rc 0 |
| test-memfn-link | first run RED: C16 flagged `memfn/src/NOTES.md` (every file there needs SPDX + a PROVENANCE row); moved to `memfn/NOTES.md`; rerun rc 0 |
| test-memfn-rows / targets / arch / forms | rc 0 each |
| test-memfn-g2 (the quick tier: window plain + traced, presence with D3, the rest) | first run RED at window site 878 (below); after the fix rc 0: 70,358,671 passed / 0 failed |
| anchors | rc 0 |
| `CLAUDEMD_ROOT=... check_claudemd_size.sh --all` | rc 0 |

**The merge's one semantic conflict: window site 878.**
- Both parents were run in scratch archives: main c5b3c2c22 passes 11,266 / 0, and partd before the merge
  (f345966f9) passes 11,250 / 0. The merge commit fails: `site 878: table_name: plan[5] (offset 4, offer 1):
  plan_test 1`.
- Three spans cover offset 4: span0 (3 members, offers table 1), span1 (verify NO) and span3 (1 member each).
  The tested set is their MEET. The kit takes a covering span's offer only where that span's own set IS the set
  tested (C-table), so OWN is correct.
- 3.0b's G2 check took the first covering span's offer. 3.0b's generator never made such an overlap; Part D's
  generator, which changes the rng stream, made one.
- Fix (G2 only, `g2_win_gen.c`): `offer_at` reads G2's OWN decision's tested set (`g2w_dec.tset`, from the
  reference, never the kit). Withheld offers are counted (`meet`) and floored at their measure (`meet:2`).
- CONTROL: a kit planted to take any covering offer (the set compare dropped) reds sites 642 and 878.

## STATE AT HANDOFF

- Branch `lane/memfn-partd` at the commit carrying this report, merged with main c5b3c2c22. In-tree validation is
  all green. No rulings file.
- OWED: kit-partd2-gate (queued as 597-kit-partd2-gate, pending behind 593-kit-d27fix-gate); cloud test, axes,
  ubsan, asan; cloud mechrows (list below); the every_pos card's timing (an owner-cleared window).

## Owed runs

OWED: kit-partd2-gate (box job 597-kit-partd2-gate: identity vs fresh BASE c5b3c2c22, the deny's ASSERT_ZERO
cells, the G2 plants S3106-S3114 S3119-S3122 S3116-S3118 S1409, D3's production path and p14); the cloud kinds test,
axes, ubsan, asan on the lane tip; cloud mechrows over S3006 S1095 S1107 S278 S286 S288 S3008 S3009 S3045 S454
S3106 S3107 S3108 S3109 S3110 S3111 S3112 S3113 S3114 S3115 S3119 S3120 S3121 S3122 (each exists as a file under
tests/mech/sabotages; S1409 and S3116-S3118 are window-family plants with no row file); the `every_pos` card's timing
(kit-grid@5, UNMEASURED: an owner-cleared window).

## Charter-vs-committed checklist

| charter item | committed |
|---|---|
| 1. merge main alone, keep MF_SITE_ABI 29, readers by grep, indexes both sides, shard table regenerated, make strict | yes (737715f5a; strict green) |
| 2. rename to MF_HEAD_MAX_UNBOUNDED, readers by grep, history text unchanged | yes (9cd4f451e) |
| 3. D3: summarize keeps the record, the parser, settest cn+ bounds (both copies), G2SITE, the check and floors, p11/p12/p14/p15 able to fail | yes; S3120-S3122 RED, p14 RED (by hand; in the gate) |
| 4. F1 overlap: Part D's ranking honours the member's tie; probe merge in a scratch worktree, d27frame result, removed by wtprune | yes: green, control red; probe removed |
| 5. validation: make, strict, codegen, memfn quick families, G2 quick tier, anchors, claudemd size | all green (Checks), after three fixes found by it: purity row re-anchor, NOTES.md out of memfn/src (C16), G2 window offer vs meet (site 878) |
| 6. ONE box gate, dry run first, then END | queued as 597-kit-partd2-gate |
| report with the deliver file's sections; OWED line; CLAUDE.md files | yes: memfn/tests, memfn/src (+ NOTES.md), r33_sim, span_pick, slot |
