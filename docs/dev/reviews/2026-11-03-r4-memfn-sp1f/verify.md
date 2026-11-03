# Verify, round memfn-sp1f

## CONTRACT-1
HOLDS. SUBJECT options.def:53-65 group comment still says "At B1 NO row is routed, so every one is ASSERT_ZERO"; fd-d1 doc ends "(ASSERT_ZERO until it routes at B2)". `--list-axes | grep ^fd-d1` shows it on SUBJECT and BASE. `--memfn=no-fd-d1` on pattern `x` moves bytes (cmp: differ at byte 532). Pre-existing doc staleness (BASE prints same text); 1f left a one-member group whose header comment describes four denies (comment partly 1f-touched).

## CONTRACT-2
HOLDS (doc/maintenance). memfn.h:1015-1020 (start hook: N, "dispatch row routes (B4/B8)"), memfn.h:1530 needs "P E A I M N H" (BASE :1519 same, H stale since 1a), memfn.h:1507 "W64 rows at B6" (BASE :1496). finder.c:60-61 KN_A/I/M/N still defined, FL_N gone (finder.c:108). Mostly pre-existing text; 1f removed the last consumers (N, W64 row R8), so it WORSENED/exposed staleness. No ABI number affected.

## CHECK-1
HOLDS (as a coverage gap; behaviour claims not re-run beyond CHECK-2/3 probes, which agree). Gone-logic exists (emit_sweep.py:1466,1499); no scripts/tests control for it is claimed by diff. Introduced by 1f (new feature, untested).

## CHECK-2
HOLDS, latent. emit_sweep.py:3381 `real = label != "selfcheck"`; variant path calls run_full_sweep with label f"selfcheck-{vname}" (:2065), dumps in VARIANT_STREAMS (:641). Repro: sweep_dumps(SUBJECT bin, SUBJECT bin, 60, (), ("--list-axes:fd-r8",)) -> movers [('--list-axes','declared gone row fd-r8 is still listed (surface identical)')]. So a variant selfcheck with the gone flag would false-RED. Introduced by 1f (exact-string exemption is its own). Not exercised by default runs.

## CHECK-3
REFUTED. dumps_declared_delta with REF lines a,x,x,b and HEAD a,b, gone={x} returns ['--list-axes: line count 4 -> 2'] (also with tab-separated variants). The line-count check demands exactly one removal. Critic's "[]" not reproduced.

## CHECK-4
HOLDS. S919 REACH_POP `tests/memfn/finder_check.py|"body:R1:UNSTATED" in ln|1`: count of `"body:R1` in finder_check.py is 1 at BASE (probe live at BASE? BASE literal "body:R1:UNSTATED" in ln: grep for `"body:R1` gave 1, the critic said BASE had `"body:R1" in ln`, so BASE probe was already not matching the exact literal, not independently re-checked) and 0 at SUBJECT. S919 untouched by 1f (identical lines both trees); header line 7 "(R1, R2, R8)" and line 21 "R1's gate record" stale. R1 is deleted, so the probe cannot flip. Mostly pre-existing vacuity; 1f made R1 non-existent, worsening it.

## CHECK-6
HOLDS. finder.c:141 `fd_form unpaid` kept "FF_UNSTATED on every row"; finder_check.py:208 asserts "-"; LATER_FORMS (finder_check.py:128) still has W64 "B6", NONE "B5", dispatch-twin "B4/B8", emitting R-MS3 UNREACHED strings (:260). Unpaid column is 1f's deliberate ratchet (introduced by 1f); LATER_FORMS staleness pre-existing, worsened by R8 removal.

VERIFY COMPLETE
