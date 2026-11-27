# CRITIC checks: arenaf3 (r107)

## Findings

- CHECK-1 (CONFIRMED, doc/design, effort small, blast: one sabotage row + two doc sentences). S3572's plant does NOT demonstrate S11 is single-control. `kit.sh alloc plant:S3572 --sites`: W1,W2,W3,W4,W6,W7/W3 all FAIL at the N=0 profiling pass ("profiling pass did not succeed cleanly", LIVE blocks from sb.c:64) because the planted heap `tail` is never freed on the SUCCESS path (scope close frees only scope entries). The row (SAB_SUITES=core) is red by the scanner, but alloc_check also reads it, via a normal-path leak, not refusal-stranding. The claim "no dynamic witness reaches that window; scanner only" holds only for the refusal window. A genuinely single-net plant needs a heap tail freed on the normal path that strands only on refusal. File: tests/mech/sabotages/S3572_scratch_tail_back_to_heap.sh header; arena_scopes.md "F3 BUILT" bullet. Classification: scanner FAIL + alloc stranded/profile FAIL (6 witnesses).
- CHECK-2 (CONFIRMED, design/maintenance, effort small). S12 `o` (render_buf) has no sabotage row and no dynamic witness. plant:Vo (`StrBuf o_heap = { .cx = cx }, *o = &o_heap;`): scanner FAIL (part_layout.c:605), alloc_check --sites PASS (8 witnesses, W6 1014 of 1057). Cause: render_buf returns early unless the buffer holds PCREC_PREFIX_LEAD marks, no witness compiles a layout-marked artifact, and adopt leaves the heap `o` empty on success. Declared SINGLE-CONTROL (D-8), so by design; its only net is the generic heap-builder rule, which plant:Vo proves fires. Suggest a one-line note that no row aims at S12.
- CHECK-3 (CONFIRMED, nit, effort trivial). scratch_builder_check.py scope_self_test message still reads "(floor is half of 3)" though MIN_SCOPE_OPENS is now 3 of 6. Wording only; the trip logic still works.
- CHECK-4 (CONFIRMED, observation, no action). S10 `nb`: plant:Vnb is caught by the scanner (memfn_stamps.c:372) AND alloc_check (W1 1 of 2542 trials at N=2532, W2 1 of 30, W3 1 of 2664, W4 7 of 450, W6 1 of 1056; "forced failure at sb.c:64", 16392 B live). Dynamic net reaches the site through about one trial per witness (narrow but present). Vnb and Vo disagree (nb dual-control, o scanner-only), as D-8 predicts.

## PROBED-AND-HELD


- Scanner on subject/base/4 plants: subject PASS (92 files, 21 allowlisted sites, 6 scope sites); base PASS (24 sites, 3 scope sites); S3572, S3584, Vnb, Vo each FAIL on the planted line (6 runs). Floor 3 vs 6 observed sites (grep count 6 matches the comment).
- alloc_check --sites on subject: PASS 8 witnesses, W6 NOTE 1014 of 1057 pinned; W7 control still reads STRANDED (code 4) without known_stranded.
- Deleted per-name narrowing and stack recording: remaining ALLOW rows are file+function scoped, per-declarator fixtures kept (S3584 plant FAILs); nothing reads known_stranded now (grep src/tests: prose only).
- scripts/m6read_check_sab_anchors.py on the review tree: 1436 sabotages, all anchors resolve, all runner plants apply (S3572/S3584 included).
- Trade audit: W6 1014/1057 and 1010/1045 consistent in alloc_check.c comment and docs/testing.md; MIN_SCOPE_OPENS=3 consistent with scanner comment and design bullet; K155 status consistent. Design lines 51 and 611 ("waits for F6") are history; F6 already landed. Largest witness: W1, 2542 forced allocations; W6, 1057.

CRITIC COMPLETE
