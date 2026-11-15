# verify (fixposts2)

## CONTRACT-1
HOLDS. SUBJECT src/facts/req.c rb_row_scan: `for (; i + 1 < n; i++) { ... memcpy(&arm, row + armoff, sizeof arm); if (!(arm & w->restored) && hit(row, ctx)) break; } return i;` -- the loop bound is `i + 1 < n`, so the last row's arm is never read and `hit` never called on it; header comment: "the caller applies the last row itself". The arm-0 catch-all is by convention only (rn_choice_rows ends `{ rn_first, 0 }`, line ~484). Behaviour identical to BASE as the critic says; the finding is a design/maintenance proposal.

## CONTRACT-2
HOLDS (latent). BASE rn_better (req.c:466-474): `for (size_t i = 0; i < N; i++) { if (rn_choice_rows[i].arm & w->restored) continue; int c = rn_choice_rows[i].row(w, &a, &b); if (c) return c > 0 ? a : b; } return a;` -- a 0 answer anywhere falls to `return a`.
SUBJECT rn_better: `RnChoiceCtx x = { w, a, b, 0 }; size_t i = RB_ROW_SCAN(w, rn_choice_rows, rn_choice_hit, &x); if (i + 1 == N) x.c = rn_choice_rows[i].row(w, &a, &b); return x.c > 0 ? a : b;` -- a last-row 0 now gives `b`. SUBJECT rn_first: `(void)w;(void)a;(void)b; return 1;` and its row is `{ rn_first, 0 }`, so unreachable today (always `a`), as claimed.

## CONTRACT-3
HOLDS. grep -c __typeof__ SUBJECT req.c = 5 (rn_choice_hit, rr_alt_hit, rb_rep_hit, rb_zero_hit casts etc.); `grep -rn __typeof__` over SUBJECT src cli lib = 5 (all req.c), BASE = 0. rn_choice_hit writes `x->c` (side effect) and rr_alt (req.c:~700) repeats `if (i + 1 == N) rr_alt_rows[i].row(w, &x.l, &x.r, &x.o);` by hand; rb_zero_into passes `(void *)a` (cast away const, req.c:~1139). memcpy of `arm` trusts the `unsigned arm` comment (rb_row_scan header). Design/maintenance proposal; no bug.

## CHECKS-1
HOLDS. Re-ran checks/g2/gen.clean and gen.plant once each (seed 20261022, 1500 sites, into verify/g2c, g2p):
- clean: exit 0, `REACH-G2W-INRUN rendered=200 agree=200`
- plant: exit 0, `REACH-G2W-INRUN rendered=200 agree=157`
Gate (memfn/tests/run_g2_win.sh:369-372): `[ "${r:-0}" -ge 100 ] && echo "REACH-G2W-INRUN rendered=$r agree=${m:-0}"` -- floors only rendered>=100; agree is printed, never gated. S3012: `SAB_REACH_EXPECT="REACH-G2W-INRUN"` (bare prefix), so the planted build (agree=157) still satisfies the reach; the plant's detection is by the driver's fails, not the reach. Plant exit code 0 (generator), token identical in prefix.

## CHECKS-2
HOLDS. checks/arms/probe.sh (sed from run_axes.sh:1784 vs gcc -E reading), run by me:
- base: sed [empty zero rep tie alt] | cpp [same]
- indent (`    WALK_ARM(LOOK, "look", 1u)`): sed drops, cpp reads `look`
- `WALK_ARM (` space: sed drops, cpp `look`
- hyphenated name `"look-behind"`: sed drops, cpp `look-behind`
- split row (`WALK_ARM(LOOK,\n "look", 1u)`): sed drops, cpp `look`
- del (ALT removed): both drop (SAME).
Silent drop confirmed on 4 of 4 variants; the guard (CHECKS-3) does not catch it. (Whether a hyphenated name would be accepted by the CLI not tested.)

## CHECKS-3
HOLDS. run_axes.sh:1783-1790: `INTERNAL_ARMS=("--harness=no-compound")` then the sed loop appends; `if [ "${#INTERNAL_ARMS[@]}" -lt 2 ]; then ... FATAL`. Starts at 1, so it fires only when zero rows read; four of five read rows missing passes.

## CHECKS-4
HOLDS (by reading; the 340-compile witness population claim not re-run, budget). SUBJECT memfn_arm.py:~208-211 comment: "the utf8 floors count CORPUS patterns only now ... (the old 15/15 and pad's 13/14 counted both, so a corpus loss of up to the witness count passed). Each is the old floor less the witnesses it contained (4; pad 3), a PROVISIONAL bound until `--measure` ... owed, see lane fixposts2's report." Floors now 11/11 (kb,trim,w16,w32) and pad 10/11 (BASE 15/15, 13/14). The recorded counts (comment :203-204 in both trees): "utf8 12/13 against floors 15/15, pad 10/12 against 13/14" -> slack vs new floors 1,2 (pad 0,1). Check code: `nc = sum(1 for d in differ if d in corpus); check(nc >= fl ...)` and the witnesses loop still checks each witness separately, so the old form already required the 4 witnesses to differ: old 15 == new 11 on corpus, and the "corpus loss of up to the witness count passed" statement is wrong. grep of SUBJECT docs/dev/plan.md for FLOORS-3|FLOORS-2|memfn_arm: 0 hits (owed measure only in a lane-report pointer).

## CHECKS-5
HOLDS. Recompiled all 9 `pattern` blocks of tests/litscan/d27/partd_r_by_role.rxt with `build/pcrec -p rx --features all [-i for the `flags i` block] -o - --pattern P` with and without `-fno-run-prefilter`, sha256 compared: blocks 1-7 MOVE, block 8 `[a-z]{4}\d+` SAME, block 9 (`xy/users\d+`, flags i) SAME => 7 of 9; file line 9 says "moves 8 of 9". 18 compiles.

## CHECKS-6
HOLDS. `grep -rIn 'arms:'` over SUBJECT tests, scripts, Makefile, docs/testing.md, docs/spec/rxt_format.md finds `# arms:` only as the first line group in the five partd_*.rxt files (partd_r_by_role, required, deny_stretch, decline, dominated); other `arms:` hits (scripts/emit_sweep.py:188 "arms: REF predates", trace_diff.py:109) are unrelated tokens; no reader parses the header.

VERIFY COMPLETE
