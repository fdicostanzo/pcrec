# mechund -- UNDETECTED/ANOMALY rows of the post-S2 cloud mech run 43595592265

## STATE AT HANDOFF
All four rows fixed tests-only and DETECTED locally at 812637dd5 (`scripts/boxlock run --label mechund -- bash tests/mech/run_sabotage_matrix.sh S3012 S711 S288 S3042`: unexpected 0, undetected 0, unreached 0, anomalies 0). The rxt re-pins are committed after it. No case (c) found. Rulings file read: no entries. Cloud re-run OWED: `scripts/cloudrun --owner main --kind mechrows --rows S3012,S711,S288,S3042 --name mechund`. Full `make test` OWED (see OWED).

## ROWS
The run's complete failed list: S686 (already fixed by lane s686), S3012, S711, S288 UNDETECTED, plus S3042 ANOMALY (not in the brief; build failure of the plant). No other FAIL kind. `m6read_check_sab_anchors.py`: all anchors resolve, so no case (a).
- S3012 -- case (b)/(d). Since [RUN-POS-SET] stage 3 the derived run part is a direct translation of the reply (part_d.md §2.1), so g2pres never reaches a_mass_choose's in-run filter. Not a coverage loss: G2's WINDOW family (memfn/tests/run_g2_win.sh) still sees the plant (in-run sites, DECIDE: stop differs from the reference; 86 fails with asan, 43 without) but no matrix arm ran it.
- S711 -- case (b). Stride-1 witness `a{2,}?[ab]` / `z(a){3,}?c?` is shadowed by the required-run pre-check (`REQ_RUN "6161[6162]@1"`), so a short run never reaches the reach test; the "no oracle" note is only the recidentity arm (SKIPPED-no-git-history by design), not an infra fault.
- S288 -- case (b). A `[0-9]{3}` between the two bytes is now a set-position run with a scan; P2 reads `else if (rsc) dom = 0` first, so the plant (drops `else if (!proof->stop) dom = 0;`) was never reached.
- S3042 -- case (a)-like (plant drift): the plant text no longer compiled (`ReqRun` has `pos`/`whole_len`, no `whole`/`whole_mask`; `pcrec_find_run_scan_index` takes 3 args). The anchor checker passes because the BEFORE text resolves; only the AFTER text was stale.

## FIXES
- S3042: plant AFTER text uses `r_->pos, r_->whole_len`.
- S288: witness re-aimed to `[ab]\x80[0-9]*\x81` (no run; offset-set scan of 0x80; clean REQ_WHY "emitted", plant "dominated"); tests/codegen/run_prechecks.sh row §5.10 and the row's SAB_REACH/SAB_DESC follow.
- S3012: new matrix arm `g2win` (tests/mech/run_sabotage_matrix.sh: vocabulary entry + case; G2W_NOASAN=1), `--reach` added to memfn/tests/run_g2_win.sh (REACH-G2W-INRUN: the in-run sites render), row's SAB_SUITES=g2win. (memfn/tests is test code; no src.)
- S711: two alternative-wrapped lazy-prefix blocks appended to tests/base/vm_lazy_rmin_prefix.rxt (`(?:a{2,}?|x)[ab]`, `z(?:a{3,}?|x)c?`, engine vm; no necessary run, so the pre-check does not stand in front). Oracle: python re (checked by hand: ab/zaac nomatch, others as written). Re-pinned in the same change: rxtsource CENSUS/RUNSH blocks 7069 and lines 98612, C3_PASS 23332, C3_VERIFIABLE 25745; startset manifests auto and forced +2 rows each (lines 268, 276).

## VALIDATION
- Matrix, 4 rows, local (log `$PCREC_TMPDIR/scratch/mechund/run2.log`): S288 prechecks 1fail/401pass; S3012 g2win 43fail/5626pass; S3042 codegen 4fail/343pass; S711 corpus 4fail/186pass (recidentity SKIPPED by design). All reach:ok.
- `make test-startset test-rxtsource` (re-run, `pins2.log`): test-rxtsource green (300/0). test-startset still red on 6 auto + 25 forced MOVER-NOT-IN-MANIFEST rows, ALL in tests/litscan/d27/partd_required.rxt and partd_decline.rxt (lane s2d27land's files), none mine: a pre-existing red on this base, for the manager.
- m6read_check_sab_anchors.py: all 1295 sabotages resolve.

## OWED
- Cloud confirmation (the last act below).
- A full `make test` for the .rxt addition (axes allowances, size tripwires, CI shard tables were not run); the partd manifest red above is independent of this lane.
