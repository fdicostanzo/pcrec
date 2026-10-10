# S367 — [K73] THE OFFSET-0 START RULE IS NOT EMITTED, so a subject that
# begins with continuation bytes is searched from offset 0 again.
#
# `pcrec_emit_start_zero` (src/gen/emit_dfa.c) is the ONE primitive every
# caller-facing body calls for the rule — the unanchored DFA scan and the VM's
# first attempt SEEK, ENG_ATTEMPT SKIPs, the anchored bodies answer -1. The
# plant returns before writing anything, which is the whole of K73's defect
# restored at every site at once: `''`, `\B`, `x*` and `(?=)` report (0,0) on
# `\x80` where libpcre2 under PCRE2_MATCH_INVALID_UTF reports (1,1), and `^`
# and `\G` hold at an offset that is not a character start.
#
# WHAT SEES IT: the answer-level detectors, twice over. `run_startbnd_diff.sh`
# §5's seven [K73] rows are pinned to the 10.46 transcript and cover each
# spelling of the rule (DFA scan, ENG_ATTEMPT, VM, VM behind a -fprefilter
# hybrid, `^`, `\G` on both engines); `tests/utf8/k73_startskip.rxt`'s cells
# are the same oracle in corpus form (45 of 86 fail on the pre-fix compiler).
# The two-arm sweep itself stays green under the plant — both arms lose the
# rule together — which is why the §5 rows exist.
SAB_ID="S367-start-zero-rule-not-emitted"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="startbnd harness"
SAB_HARNESS_TARGET="tests/utf8/k73_startskip.rxt"
SAB_DESC="pcrec_emit_start_zero writes nothing, so every caller-facing body attempts a match at offset 0 on a subject that begins with a continuation byte — K73 restored at every site at once"
SAB_DOC_FIGURE="docs/dev/known_issues.md K73; docs/spec/match_api.md 9.3 (#offset-zero); docs/dev/lanes/k73utf_report.md"
SAB_COUNT=1
# REACH: a nullable pattern under -e utf8 must carry the rule at all.
SAB_REACH='"$PCREC" -p rx -e utf8 -o - --pattern "x*" | grep -c "search_from == 0 && !(" | head -1'
SAB_REACH_EXPECT='2'
SAB_BEFORE='    if (act != PCREC_START0_ROUNDUP && !pcrec_startgate_needed(cx)) return;
    if (!pcrec_enc_start_guard(pcrec_enc_by_id(cx->opt->encoding),
                               g, sizeof g, posvar, subjvar, lenvar, &trunc)) {'
SAB_AFTER='    if (act != PCREC_START0_ROUNDUP) return;   /* SABOTAGE S367 */
    if (!pcrec_enc_start_guard(pcrec_enc_by_id(cx->opt->encoding),
                               g, sizeof g, posvar, subjvar, lenvar, &trunc)) {'
# RE-ANCHORED 2026-10-05 ([K82] (B), lane k82hbuild), INTENT RE-VERIFIED: the
# function gained a SIBLING MODE, the handoff's round-up, which is not gated on
# nullability; the plant still suppresses the offset-0 rule at every site and
# leaves the round-up alone (which S471/S472 own).
