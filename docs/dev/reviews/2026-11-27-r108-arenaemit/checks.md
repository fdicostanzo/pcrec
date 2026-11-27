# checks findings (r108 arenaemit)

## Findings

### CHECK-1 (CONFIRMED) S3644 is SILENT in every net it declares; SAB_DESC/header claim a net that does not fire
severity: maintenance/doc (a sabotage row that cannot be red; r107 A). effort: small. blast: the mech matrix.
Repro: `kit.sh alloc plant:S3644 --both` (log checks/alloc_S3644.log): 13 PASS, 0 FAIL, W6 still 1057/1014-fallback, W7/W3 528 ok.
The planted body-on-parent edit (clskit.c:1209) leaves alloc_check fully green; `kit.sh scan plant:S3644` PASS; `kit.sh emit plant:S3644`
on '\p{L}+x' and '\p{Greek}z' is byte-identical to SUBJECT (md5 62645cc2f32f / 1c7da7c6033f). The row's SAB_SUITES="resource" runs the same
injected alloc_check (run_resource_tests.sh section 2), so the row scores NOT DETECTED there. Two causes: W6's pattern '^abc|x+$' is byte mode
(never reaches the utf8 whole-set matcher) and W7's `min_total` is a floor (264), not an exact pin, so a count move is invisible. The header
says W6/W7 "exact pins move ... read from a run, not assumed": the run says no. Also no SAB_EXPECT=UNDETECTED/SAB_REACH is declared, so the
matrix will score it a miss rather than a declared out-of-suite net. Fix shape: declare SAB_EXPECT=UNDETECTED with the reason, delete the
incidental-net sentence, or add an alloc witness on '\p{L}+x' (utf8, vm) with an exact count (a K35 population that reaches the site).

### CHECK-2 (CONFIRMED) test_verdicts.py MG_ENC/MG_ENG checks share a source with what they control (three silent mutations)
severity: maintenance. effort: small. blast: memgate population lever (the one that reaches the SCOPE-4 site).
Repro (copies of tests/core/memgate under checks/mg1..3, run `python3 -I mgN/test_verdicts.py`, all print "ok 19/19"):
 (1) memgate.py population(): `levers()[1]` replaced by `0` (MG_ENG never reaches the corpus items): ok 19/19. Only levers() is tested, never that
     population() consumes it.
 (2) mg_drv.c: the `getenv("MG_ENC")` line moved BEFORE pcrec_default_options (default_options overwrites the lever; MG_ENC dead): ok 19/19.
 (3) mg_drv.c: the lever turned into a comment containing both grep strings: ok 19/19. The "mg_drv.c reads MG_ENC" check is a substring grep of the
     very file it vouches for, so it passes on a comment and on a wrong order.
Fix shape: build mg_drv (prep) and assert behaviour on a fixed utf8 pattern under MG_ENC=0 vs 1 (differing emitted/peak line), and a unit call of population()
asserting corpus engine == MG_ENG.

### CHECK-3 (CONFIRMED, minor) lever visibility: instr/rungs do not print the levers; docstring says "peak and instr"
severity: doc/observability. `print("peak: levers ...")` is only in mode_peak (memgate.py:223); mode_instr/mode_rungs print nothing, though MG_ENC reaches
every driver (env inherited, mg_drv.c reads it for rungs too) so a `rungs` run under a stray MG_ENC is unlabelled. Both sides share one process env, so a
one-side-only lever cannot differ per side by construction (HELD); a stale side driver cannot happen (prep builds both from HERE/mg_drv.c). MG_ENG is
corpus-only as documented (population() only, a.mode in peak/instr); cells keep their engine (HELD).

### CHECK-4 (NOTE) S3613 re-anchor and S3643 floors hold
(no defect; see PROBED-AND-HELD)

## PROBED-AND-HELD
- scanner (`kit.sh scan`): subject PASS (7 scope sites); plant:S3613 FAIL L2-static clskit.c:1132; plant:S3643 FAIL L2-static clskit.c:1208; plant:S3644 PASS (expected: no L2/L4 rule sees which arena). MIN_SCOPE_OPENS=3 with 7 sites: floor is slack, but unchanged by the diff and the per-function L2 rule catches each plant (3 plants, 3 sites).
- runtime success-path check_closed (`kit.sh emit`, -e utf8 --engine=vm): plant:S3643 refuses '\p{L}+x' ("a scope left open at the end of a successful attempt"), accepts '\p{Greek}z' (kit form); plant:S3613 the inverse. The two rows partition the witnesses, so each row has its own reaching witness (4 emits).
- S3613 re-anchor: `pcrec_scope_close(&sc);` occurs twice in clskit.c now (lines 1140, 1210), so the OLD one-line anchor would match twice (SAB_COUNT=1 fail); the new two-line BEFORE (`pcrec_sb_puts "}\n"` + close) is unique; `m6read_check_sab_anchors.py`: 1438 sabotages / 1498 anchor sites, runner plants 81 apply, no failure. S3643 and S3644 BEFORE strings unique.
- S3643 SAB_DESC "core arm" + "harness" both true (scanner + runtime refusal).
- Largest witness: alloc --both with 2665 forced failures (W3), 1057 (W6); 4 emit compiles; 0 memgate runs (coordinator evidence dir empty at the time; the "108 movers" claim in S3644's header was not re-verified by me).
CRITIC COMPLETE
