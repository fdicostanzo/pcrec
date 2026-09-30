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
SAB_BEFORE='           (r->degrading && (flags & PCREC_FAST_OR_FAIL) != 0);'
SAB_AFTER='           (r->degrading && (flags & PCREC_FAST_OR_FAIL) != 0 && false);   /* SABOTAGE S421 */'
