# S421 — [PF-DROP] (D135) `--fast-or-fail` DENIES NOTHING.
#
# The switch acts through ONE predicate, `fit_rung_denied`
# (`src/core/compile.c`): a row is transparent when the caller set its own
# deny bit OR set `PCREC_FAST_OR_FAIL` and the row is degrading. Drop the
# second half and the switch is accepted, masked out of `rx_info.flags`, and
# does nothing at all — every over-cap pattern is still shipped slower, the
# exact outcome the caller asked to be refused instead.
#
# SILENT BY CONSTRUCTION to every answer check: with the switch inert every
# artifact is the default one. WHAT SEES IT: the resource section's
# [PF-DROP/ff] cells, which require each rung's witness to refuse under the
# switch, and run_prefilter_collapse.sh's K41 `--fast-or-fail` control.
SAB_ID="S421-fast-or-fail-inert"
SAB_FILE="src/core/compile.c"
SAB_SUITES="resource pfcollapse"
SAB_DESC="fit_rung_denied ignores PCREC_FAST_OR_FAIL, so --fast-or-fail denies no degrading rung and every over-cap witness still ships slower instead of refusing"
SAB_DOC_FIGURE="PREDICTED (lane pfdrop, 2026-09-30): resource 4 [PF-DROP/ff] refusal cells red (prefilter drop, collapse, anchored, premul); pfcollapse's K41 --fast-or-fail control red. docs/spec/limits.md §8; docs/spec/cli.md --fast-or-fail"
SAB_COUNT=1
SAB_REACH='"$PCREC" -e utf8 --fast-or-fail -p rx -o - --pattern "(\p{Xwd})" 2>&1 | grep -o "pattern too large" | head -1'
SAB_REACH_EXPECT='pattern too large'
SAB_BEFORE='           (r->degrading && r->fof == FIT_FOF_IN && (flags & PCREC_FAST_OR_FAIL) != 0);'
SAB_AFTER='           (r->degrading && r->fof == FIT_FOF_IN && (flags & PCREC_FAST_OR_FAIL) != 0 && false);   /* SABOTAGE S421 */'
# RE-AIMED 2026-10-08 (lane decfbB2, [DEC-FALLBACK] B2): the predicate's line
# gained the `fof` reach (`--fast-or-fail` denies a degrading row only when
# it is inside the switch's reach); the plant still neuters the switch
# term, so the intent is unchanged. Re-verified with the plant: every size
# rung's `--fast-or-fail` witness compiles again where the unplanted build
# refuses.
