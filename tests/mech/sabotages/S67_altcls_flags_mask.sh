# S67 — [OPT-ALTCLS] PCREC_NO_ALTCLS_MERGE/PCREC_NO_ALTCLS_FACTOR DROPPED
# FROM THE rx_info.flags STRATEGY-DENIAL MASK.
#
# The same failure mode S65 encoded for the prefilter axis, one pass over:
# `emit_info_def` (src/gen/emit_dfa.c) masks every D47.3-family bit out of
# the emitted `rx_info.flags` because those flags are testing/tuning axes
# that change no answer, and two artifacts differing ONLY in whether a
# stage was denied must be byte-identical in every OTHER respect or the
# byte-identity gate that is the pass's own safety argument breaks. This
# sabotage drops `PCREC_NO_ALTCLS_MERGE`/`PCREC_NO_ALTCLS_FACTOR` back out
# of the mask, so the raw flags word -- including whichever deny bit was
# passed on the command line -- leaks straight into the artifact's `.flags`
# literal.
#
# WHAT ACTUALLY HAPPENS: `rx_info.flags` differs between two artifacts that
# behave IDENTICALLY (the whole point of a deny-only testing axis), purely
# because one was built with `-fno-altcls-merge`/`-fno-altcls-factor` and
# the other was not. Every MATCH-BEHAVIOR check in the tree stays silent --
# altcls.rxt, the vm oracle, and run_altdiff.sh's own span/capture/failure-
# surface sweep all still agree, because the match behavior really is
# unchanged. Only tests/altcls/run_altcls_tests.sh's check 5 (the byte-
# identity comparison between the pass-on and pass-off builds of a
# verdict-free pattern) reads the leaking bit as the byte difference it
# exists to rule out.
#
# RE-ANCHORED 2026-08-26 (lane srAnchor): srTier's two-tier default entry
# ([OPT-1]) added `PCREC_NO_TIERED_ENTRY` to the same `strategy_denials` mask
# this row edits, so the old anchor's closing `;` (which used to follow the
# ALTCLS pair directly) is now a `|` followed by a block comment and
# `PCREC_NO_TIERED_ENTRY;`. The anchor is narrowed to the ALTCLS pair'"'"'s own
# line -- still unique at SAB_COUNT=1 -- and the AFTER text drops it while
# preserving the trailing `|` the PREFILTER line already carries, so the mask
# still parses into the (unchanged) TIERED_ENTRY member that follows.
SAB_ID="S67-altcls-flags-mask"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="altcls"
SAB_DESC="PCREC_NO_ALTCLS_MERGE/PCREC_NO_ALTCLS_FACTOR dropped from emit_info_def's strategy_denials mask, so -fno-altcls-merge/-fno-altcls-factor leak into the emitted rx_info.flags literal even though the axis changes no match behavior -- two artifacts that answer identically now differ in their reflection surface over a knob with no observable effect"
SAB_DOC_FIGURE="lib/pcrec.h's PCREC_NO_ALTCLS_MERGE/PCREC_NO_ALTCLS_FACTOR comment; src/gen/emit_dfa.c's strategy_denials mask comment"
SAB_COUNT=1
SAB_BEFORE='                                          PCREC_NO_ALTCLS_MERGE | PCREC_NO_ALTCLS_FACTOR |
'
SAB_AFTER='                                          /* SABOTAGE S67: the two altcls deny
                                           * bits removed from the mask -- they
                                           * now leak into rx_info.flags */
'
