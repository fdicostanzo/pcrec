# S368 — [K73] THE DFA's UNWRAPPED `<prefix>_match` LOSES ITS CALLER-STARTPOS
# GUARD, the state it shipped in from [ENG-ABS] until K73's site survey.
#
# §3.1 promises the anchored entries carry K50's guard. The search-and-filter
# form reaches it through `<prefix>_search`; the unwrapped form calls no
# search, so its body must emit the guard itself. The plant deletes that one
# call: `x*` at `ctx->pos == 1` of `C3 A9` answers 0 (an empty match) instead
# of PCREC_ERR_STARTPOS.
#
# WHAT SEES IT: `run_startbnd_diff.sh`'s two-arm driver, which sweeps
# `<prefix>_match` as well as `<prefix>_search` since K73 — every DFA-routed
# witness reports GUARD MISSING on the anchored entry, and the anchored
# entry's own refused floor (150) goes red. MEASURED with the pre-fix
# compiler, which is this plant's state: five of the ten witnesses (the
# DFA-routed ones) refused 0 of 15 mid-character `_match` cells, total 75.
SAB_ID="S368-unwrapped-match-guard-deleted"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="startbnd"
SAB_DESC="the DFA's unwrapped <prefix>_match stops emitting the K50 caller-startpos guard, so a mid-character ctx->pos is answered instead of refused (the state the form shipped in until K73)"
SAB_DOC_FIGURE="docs/spec/match_api.md 9.2's anchored-entries bullet (#startpos); docs/dev/known_issues.md K73's fix paragraph"
SAB_COUNT=1
# RE-ANCHORED [UTF-VALID] (lane uvbuild, 2026-09-30): the call gained its
# `anchored` argument (the align value's NOMATCH form); the plant still
# deletes the one call, and with it this body's whole caller-position
# prologue — the intent (the K50 guard gone from the unwrapped form) is
# unchanged and re-verified by the same startbnd detector.
# REACH: a utf8 DFA artifact must still take the unwrapped match form.
SAB_REACH='"$PCREC" -p rx -e utf8 -o - --pattern "x*" | grep -o "RX_DFA_MATCH \"unwrapped\"" | head -1'
SAB_REACH_EXPECT='RX_DFA_MATCH "unwrapped"'
SAB_BEFORE='    pcrec_emit_startpos_guard(cx, c, "    ", "search_from", "subject",
                              "subject_length", true);
    pcrec_emit_start_zero(cx, c, "    ", "search_from", "subject",
                          "subject_length", PCREC_START0_NOMATCH);'
SAB_AFTER='    /* SABOTAGE S368 */
    pcrec_emit_start_zero(cx, c, "    ", "search_from", "subject",
                          "subject_length", PCREC_START0_NOMATCH);'
