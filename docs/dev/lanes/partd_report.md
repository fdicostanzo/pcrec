# Lane partd: R-38 Part D (D0-D2) and R-41, build report

STATE: stopped. D0, D1, D2 and R-41 are BUILT and checked in-tree. D3 (the measurement's record:
`collect.py` summarize, the census parser, the `settest_cls` bounds, the G2SITE print, plants
p11/p12/p14/p15) is NOT built. Branch `lane/memfn-partd`, worktree `worktrees/partd`, base
a6054c124 (main f066e84ee plus the design branch, docs only). Design of record: `part_d.md` rev 4.

## Summary

- **The kit side of R-38 Part D is built.** Run positions may hold 1-128 members. The scan is findable-only: one member, or a two-member
  cube. A new row PD declines, after P2, an OPTIONAL run with no findable position. A REQUIRED run with
  no findable position is verified whole without a scan (P0's scan-less reply, K66), through ofsskip's new
  `fn-every-pos` body. That body's card is `kit-grid@5`, UNMEASURED.
- **The derived run part is a direct translation of the reply.** The scan stretch is one RUN term. Each wide position is its own
  tableless SET term, tested by `kit_set_test`. ofsskip admits both only through a scoped admission.
- **Window sites now identify R by role** (verify NO, two or more positions). The deny is `run-verify-wide`.
- **R-41 is built**: `MF_HEAD_UNBOUNDED` (2^40) declines the landmark on every ASSIGN site.
- **One MF_SITE_ABI event (to 29: 3.0b took 28 on main; the bump re-done by grep on the kit manager's word) and one MF_CLASS_V event (9 to 10).** No pcrec emitter was edited. Expected
  pcrec byte movers: zero (the box gate proves it, below).
- **G2's presence family gains a WIDE stream on its own rng.** Today's site file stays byte-identical: seven
  sha-256 literals, reproduced.
- **Plants S3106-S3119.** The four window plants (S3116-S3118, plus S1409 re-anchored) were run here: all RED.
  The ten presence plants run in the box gate.

## Built vs designed

| unit | designed (§5.1) | built | divergence (logged reading) |
|---|---|---|---|
| D0 | G2 wide stream, own rng, today's sites byte-identical, base counts | `g2_pres_gen.c` wide stream (rnd2, layouts 0-7, set positions), `g2_pres_run.c` set-aware classifier (EXACT over every non-member of a wide position), SITE_HASHES literals, floors | The wide sets ride a WEAK side table `g2p_wides[]` (g2_pres.h), not a trailing `g2p_site` field. A trailing field breaks the `-Werror` compile of today's initializers, and filling it moves today's site file. |
| D1 | `findable` column; PD after P2 with SF_RUN_NOSCAN; P0 scan-less; run span first; P3 member / head rule / `pres_layout_check` read `trun` | as designed (finder.c, presence.c, compose.c, window.c `kit_run_member` KIT_CAND_*) | none |
| D2 | direct translation, scoped ofsskip, `fn-every-pos`, R by role, the deny, card | as designed; card `kit-grid@5` `every_pos` UNMEASURED; formhash.c fifth shape `MF_FH_RUNPART` (asserts arm `precheck` and BODY row `fn-every-pos`, read off the new `mf_art.fn_body`) | `CARD_FORMDEP_COUNT` 17 to 18; `every-pos` joins the form-hash fixtures (rename/edit/foldedit) |
| D3 | `run_part_terms` record kept by summarize, parser, `settest_cls` cn+ bounds, G2SITE print, check + floors, p11/p12/p14/p15 | NOT BUILT | Scope: stopped here; the `MFTRACE run_part_terms` print exists (D2), nothing reads it yet |
| R-41 | MF_HEAD_UNBOUNDED, declined in presence.c's landmark (h == 0 included), a G2 case, same ABI event | as designed; G2 case in `twin_check` | none |

Readings taken where the design was ambiguous, each chosen to keep its check able to fail:
- **p2 (S3107)**: "the row deleted" is the row removed under `#if 0`. A row that merely never fires could hide behind a contract check.
- **p6' (S3111)**: "one range dropped" is the set test's lowest MEMBER dropped. That drops a range where the member stands alone, and
  shrinks one otherwise. Detector: the occurrence oracle.
- **p10 (S3113)**: built as two edits, not three. Once the no-scan fact reads as a scan of byte 0, `fn-every-pos` stops holding and
  `pair_holds` (`b >= 0`) takes the part, so the row swap the design names is implied. The matrix allows two edits per row.
- **p9 (scope dropped from `ofs_fn_applies`)**: no sabotage-matrix arm runs `run_g2.sh`, so p9 has no row and was HAND-MEASURED here.
  g2_gen at seed 20260917 gave `OFSSCOPE rendered=1232 scoped=0` clean and `rendered=1410 scoped=178` planted, so the two-sided pin
  (`scoped == 0`) reds. To re-run: plant `derived = 1;` at the top of `ofs_fn_applies`, then `make test-memfn-g2`.

## R-41

`memfn.h`: `#define MF_HEAD_UNBOUNDED ((int64_t)1 << 40)`, stated by name. In presence.c's landmark rule, a stated
unbounded K sets `landmark = 0` before the `h == 0` branch, so the admission an `h == 0` member would get is declined
too. G2 case (`g2_pres_gen.c` `twin_check`): on every ASSIGN twin, `head_max = MF_HEAD_UNBOUNDED` must give landmark 0. Measured:
729 of 729 sites, all 729 of which have bit 1 at K 0 (so every case moves). Floors `r41:656 r41_flip:656`. Plant S3119 (the
decline dropped) is detected by `: R-41: `.

## MF_SITE_ABI and MF_CLASS_V

MF_SITE_ABI to 29 (28 is 3.0b's on main, not in this branch's base; R by role on window spans; `MF_HEAD_UNBOUNDED`). MF_CLASS_V 9 to 10 (`mf_class.run` with `has_scan` 0
and `ver_len` > 0: the scan-less whole-run reply). I grepped every reader of both numbers across memfn/, tests/, scripts/,
docs/spec/, src/, cli/ and requests.md (`MF_SITE_ABI ... 27|28`, `MF_CLASS_V ... 9|10`, `.abi = 27`, `== 27`). Every hit
is a historical citation ("since MF_SITE_ABI 27"); none pins the value. All tests read the symbol. The pcrec abi number
is unchanged: no emitted byte moves (the gate proves it). The re-bump to 29 (at the kit manager's word: 3.0b took 28 on main) was re-checked after the fact: make
strict, test-memfn-finder and test-codegen are green, and today's G2 site file still hashes 7e3cfc6c... (the site
files name the ABI by symbol). The g2 quick tier and the presence family ran at 28.

D27 contract excerpt (memfn.h, for a spec-first author):

```
#define MF_HEAD_UNBOUNDED ((int64_t)1 << 40)   /* mf_site.head_max's stated "unbounded" K (R-41,
   MF_SITE_ABI 29): equal to pcrec's PCREC_W_UNBOUNDED, 2^40, a width no subject reaches; stated by NAME */
mf_wspan.verify: In a window site's alternative a verify-NO span of two or more positions IS the run R
   (any sets; at most one per alternative, MF_SITE_ABI 29); a presence site's run span is not R.
mf_class.run.has_scan: 0: no single find position (since MF_CLASS_V 10, with ver_len > 0: every
   candidate position is tested, no find; P0's REQUIRED run with no position the kit finds, whose
   extent is the whole run)
```

## The decline

PD (finder.c), after P2: facts `SF_RUN_NOSCAN`, contract OPTIONAL only, basis DERIVED, no deny. Its link is untested
(verify 0, proven_by 0), and the set's pick is laid out as on a run-less site. In the run-less layout the head need is
MF_REQUIRED (`pres_layout_check` reads `trun`). P2 reads a no-scan run as run-less (`rsc`). G2 checks each site's
decline against its own rule ("OPTIONAL, no findable position, not P2"), the twin's landmark on a declined run (F1),
the HEAD (F2), and proof on dominated no-scan sites (F3). Measured per target pass (6 passes, identical):
declines 45 = PD route sites 45; dec_member 18, dec_assign 29, dec_twin 18; dec_untested 45 = dec_refused 45;
dec_rendered 18; dec_noprecheck 27; dom_noscan 7; scanless_req 9. finder_history.md has the PD row.

## Witnesses

Presence family (`run_g2_pres.sh`, seed 20261110, 400 sites plus 300 wide): 8,051,492 checks, 0 failed, about 250 s wall.
Wide-stream floors are pinned at the least over the six target passes less about 10% (a count under 10 keeps its
measure): wide_sites 300, wide_ver 197, nofind 61, nobg 13, f24 32, f24_3 27, scan_findable 194; driver declined 18,
scanless 9, scanless_match 151, nobg 10, exact_wide 399,844. The deny pass (generic, `no-run-verify-wide`) measured
deny_sites 576 and deny_one 81, and every verified extent was findable-only. Window family: 11,250 checks, 0 failed;
FIX-9 populations r_yes 105 (floor 94) and r_wide 129 (floor 116). `run_g2.sh` gets OFSSCOPE's two-sided pin (scoped
== 0, rendered >= 1; measured 1232 / 0). The family's plant mode now also runs the site-file hashes and the wide
floors, so a plant whose detector is a hash (S3115) or a floor (S3114) can red.

## Sabotage rows

| id | plant | detector | state |
|---|---|---|---|
| S3106 | p1 `findable` ignored | G2: the run's scan is a WIDE position | mech row; plant runs in the gate |
| S3107 | p2 PD deleted | G2: mf_ask refused / the decline | mech row; gate |
| S3108 | p3 decline on a cube scan | G2: PD declined a findable run | mech row; gate |
| S3109 | p4 head rule `run >= 0` | pres_layout_check: first part not the HEAD | mech row; gate |
| S3110 | p5 cube hull | C2 classifier EXTENT | mech row; gate |
| S3111 | p6' set-test member dropped | the occurrence oracle | mech row; gate |
| S3112 | p7 stretch widened | run_bytes refusal (no (T, K) spelling) | mech row; gate |
| S3113 | p10 every-pos read as byte 0 | scanless_match floor / SOUND / EXTENT | mech row; gate |
| S3114 | p13 P2 `rs && !proof->run` | dom_noscan floor | mech row; gate |
| S3115 | rate rule on cubes (generator) | SITE_HASHES (shown here: c356661c..., base 7e3cfc6c...) | mech row (g2pres) |
| S3116 | p8 `run_shaped` for verify-NO | window DECIDE | family plant: RED here (142 fails) |
| S3117 | p16 merge takes the YES span | window DECIDE | family plant: RED here (112 fails) |
| S3118 | YES-uniqueness dropped | window two-runs control | family plant: RED here |
| S3119 | R-41 decline dropped | G2 `: R-41: ` | mech row; gate |

Every new and changed row was checked: all plants apply exactly once and compile (dry run), anchors resolve (1272 rows,
1322 sites), and `make test-memfn-arch` passes 17/0 (the prose is arch-free; no allowlist rows needed).

Re-anchored, same plants:
- **S3006**: onto `run_rank`. Planted, the decider census reds (2 fails); clean, it passes 86/0.
- **S1409**: onto the role wording of `wf_check`'s refusal. RED here.
- **Earlier in the lane**: S1095, S1107, S278, S286, S288, S3008, S3009, S3045, S454 (each carries a RE-ANCHORED note).

## Identity and movers

- Today's G2 presence site file is pinned by seven sha-256 literals, one per pass (base a6054c124). The tip reproduces
  all seven, and adding the R-41 case kept them (7e3cfc6c... re-checked).
- **The zero-mover proof is box gate job `597-kit-partd-gate`** (key `kit-partd-gate`). It builds BASE fresh from
  a6054c124 by `git archive` (REF = its `build/pcrec`) against the lane tip, over every declared identity arm plus the four
  CPU targets. The new arm `memfn-run-verify-wide` is SKIPPED there, logged, because REF predates the option. The deny's
  four `emit_sweep` cells are ASSERT_ZERO: the gate runs them on the tip alone (byte and utf8 bases), then the 14 plants.
  Script: `/var/tmp/pcrec-pcrec/scratch/memfn/partd/jobs/gate.sh`. No pcrec emitter was edited, so the expected movers are
  zero.
- `DIFFER_PINS`/`ASSERT_ZERO` cells for `--memfn=no-run-verify-wide` hold at all four (base, stream) pairs. They become
  floors with a stage-3 manifest at the joint landing. `IDENT_MEMFN` gains `run-verify-wide`.

## Checks

| check | result |
|---|---|
| make strict | green |
| make test-codegen | green |
| test-memfn-finder | green: finder_check, proven, mass, rundec, census, purity, reach all 0 failed |
| test-memfn-rows / link / targets / arch / forms | green (arch 17/0) |
| test-memfn-g2 (quick tier: run_g2.sh, window, presence) | 70,358,670 / 0 after the fix below (first run RED: fn-every-pos never chosen by a traced process; run_g2.sh now traces the presence generator in its rows unit, chosen 9) |
| run_g2_pres.sh (wide stream, deny pass, hashes, floors) | 8,051,492 / 0 |
| run_g2_win.sh | 11,250 / 0; plants S3116, S3117, S3118, S1409 RED |
| registry (axes_registry_check.sh) | 248 / 0 (memfn section floor 12 to 13, `run-verify-wide` row in registry.md §6¶8a) |
| anchors (m6read_check_sab_anchors.py) | all resolve |
| check_claudemd_size --all | within limits |
| decider census, planted S3006 | red (2); clean 86/0 |

## Owed runs

OWED: box gate `kit-partd-gate` (queued as 597-kit-partd-gate: identity vs fresh BASE a6054c124, the deny's ASSERT_ZERO
cells, the 14 G2 plants); cloud kinds test, axes, ubsan, asan on the lane tip; cloud mechrows over S3106 S3107 S3108
S3109 S3110 S3111 S3112 S3113 S3114 S3115 S3119 (new; S3116-S3118 are window-family plants with no row file) and
the re-anchored S3006 S1095 S1107 S278 S286 S288 S3008 S3009 S3045 S454 (all exist as files); D3 (unbuilt, above);
the `every_pos` card's measurement (UNMEASURED; a timing run in an owner-cleared window).

Note: `docs/dev/lanes/partd_deliver.txt` says `owed: none`, while this report has an OWED line. The gate and the cloud
kinds above are owed by design (the cloud suites are the kit manager's, and the gate is the lane's last act). The
deliver file's line predates that and conflicts with it.

## Charter-vs-committed checklist

| charter item | committed |
|---|---|
| D0-D3 per the content/check/plant/sabotage columns | D0, D1, D2 yes; D3 NO (STATE: stopped) |
| R-41 (define, decline incl. h == 0, G2 case, same ABI event) | yes |
| MF_SITE_ABI to 29 (re-bumped), MF_CLASS_V 9 to 10; readers by grep | yes; no value-pinning reader |
| zero emit_sweep movers; no pcrec emitter edits | no emitter edits; proof = the queued gate |
| every-pos card UNMEASURED | yes, kit-grid@5 |
| sabotage rows at S3106+, arch-free prose, `make test-memfn-arch` | S3106-S3119; arch 17/0 |
| D27 contract excerpt | yes (above) |
| make strict, test-codegen, memfn quick families, anchors, claudemd size | yes, green (g2 quick: see Checks) |
| ONE box gate: zero movers vs fresh BASE + the new plants | queued, the lane's last act |
| report with exact sections, OWED line, deliver.txt conflict | yes |
| CLAUDE.md files updated | memfn/tests, memfn/src, memfn/data/cards |
