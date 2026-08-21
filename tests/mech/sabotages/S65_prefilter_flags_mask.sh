# S65 — [M4.6f] PCREC_NO_PREFILTER/PCREC_FORCE_PREFILTER DROPPED FROM THE
# rx_info.flags STRATEGY-DENIAL MASK.
#
# `emit_info_def` (src/gen/emit_dfa.c) masks every D47.3-family bit out of
# the emitted `rx_info.flags` because those flags are testing/tuning axes
# that change no answer -- two artifacts differing ONLY in whether a
# strategy was denied or forced must be byte-identical in every OTHER
# respect, or the byte-identity gate that is each such pass's own safety
# argument breaks (the reasoning is stated in full at the mask's own
# comment). `PCREC_NO_PREFILTER`/`PCREC_FORCE_PREFILTER` joined that mask
# at [M4.6f] for the identical reason, even though the PREFILTER axis is a
# FORCE pair rather than a deny-only flag: the rule is about OBSERVABLE
# EFFECT, not spelling. This sabotage drops both new bits back out of the
# mask, so the raw `pcrec_options.flags` word — including whichever of the
# two force bits was passed on the command line — leaks straight into the
# artifact's `.flags` literal.
#
# WHAT ACTUALLY HAPPENS: `rx_info.flags` (and therefore anything a caller's
# code branches on after reading it) now differs between two artifacts that
# behave identically, purely because one was built with `-fprefilter` or
# `-fno-prefilter` and the other was not. Every existing correctness check
# in the tree is silent to this, because the MATCH BEHAVIOR is genuinely
# unchanged -- .rxt corpora, the vm oracle sweep, and the S3.7 differential
# all still agree. tests/prefilter/run_prefilter_tests.sh check 6 (the
# `flags_of` numeric read against the 0x100/0x200 bit values) is the only
# thing that reads `rx_info.flags` as a NUMBER rather than trusting the mask
# is complete, so it is also the only thing that can see this leak. Its
# byte-identity checks (5) catch it too, as a side effect: the leaking flag
# bit is exactly the byte difference they exist to rule out.
SAB_ID="S65-prefilter-flags-mask"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="prefilter"
SAB_DESC="PCREC_NO_PREFILTER/PCREC_FORCE_PREFILTER dropped from emit_info_def's strategy_denials mask, so -fprefilter/-fno-prefilter leak into the emitted rx_info.flags literal even though the axis changes no match behavior -- two artifacts that answer identically now differ in their reflection surface over a knob with no observable effect"
SAB_DOC_FIGURE="lib/CLAUDE.md's [M4.6f] entry; src/gen/CLAUDE.md's STRATEGY-DENIAL mask paragraph"
# RE-ANCHORED 2026-08-21 (sabanchors lane): [OPT-ALTCLS] appended
# PCREC_NO_ALTCLS_MERGE | PCREC_NO_ALTCLS_FACTOR to strategy_denials after
# this row was written, so the mask no longer ends at PCREC_FORCE_PREFILTER
# with a terminating `;` — it now continues with a `|` into the two new
# ALTCLS bits on the next line (this file's own tests/mech/CLAUDE.md records
# the finding). Anchor and replacement updated to keep the trailing `|` so
# the ALTCLS bits stay attached to the expression; S65's own two bits are
# still the ones dropped, S67 (a separate row) is what drops the ALTCLS
# pair. Intent (PCREC_NO_PREFILTER/PCREC_FORCE_PREFILTER leak into the
# emitted rx_info.flags) unchanged.
SAB_COUNT=1
SAB_BEFORE='                                          PCREC_NO_LENGTH_PRUNE |
                                          PCREC_NO_PREFILTER | PCREC_FORCE_PREFILTER |
'
SAB_AFTER='                                          PCREC_NO_LENGTH_PRUNE |
                                          /* SABOTAGE S65: the two prefilter
                                           * force-pair bits removed from the
                                           * mask -- they now leak into
                                           * rx_info.flags */
'
