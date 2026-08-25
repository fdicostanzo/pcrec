# S31 — K10 reopened: RF_CLASS_INVALID restored on the `\N{U+` row after
# MOD-0.6's fix removed it. Measured (by hand, before this file existed):
# [\N{U+41}] reverts to "\N is not valid inside a character class", losing
# the module promise libpcre2's error 193 warrants in every class position.
# Caught by tests/reject/'s seven offset-pinned [\N{U+41}]-shaped rows AND
# by tests/registry/registry_check.c's check_class_syntax_reach (the
# in-class tail-sweep extension this same slice added — D33 §9.2's own
# "matched pair" requirement made checkable).
SAB_ID="S31-uprops-reflag-class-invalid"
SAB_FILE="src/parse/registry.c"
SAB_SUITES="reject"
SAB_DESC="the \\N{U+ row: RF_CLASS_INVALID restored, re-breaking K10"
SAB_DOC_FIGURE="measured by hand at K10's fix (2026-08-12): 7 reject failures ([\\N{U+41}]-shaped pins); registry_check.c's check_class_syntax_reach also fails outside make test's reject-only suite"
# [MECH-REACH, 2026-08-25] THIS ROW DECLARES ITS WITNESS'S REACH.
# THE WITNESS IS THE IN-CLASS POSITION, which is the one
# `RF_CLASS_INVALID` governs. K10's fix is that `[\N{U+41}]` promises the
# MODULE rather than being refused as an invalid class member; restoring
# the flag re-breaks it. A probe at the ATOM position would be green under
# the sabotage and is not the witness.
SAB_REACH='"$PCREC" --features none -p rx -o "$REACH_TMP/o0.c" -- "[\\N{U+41}]"'
SAB_REACH_EXPECT="\\N in a class requires module 'unicode-props' (pattern offset 1)"
SAB_COUNT=1
SAB_BEFORE="{RK_ESC, 'N', \"{U+\", \"\\\\N{U+0041}\", M_unicode_props, FLAV_PCRE2, ANY_ENGINE,
 RS_MODULE, RD_MODULE, NULL, NULL, 0,"
SAB_AFTER="{RK_ESC, 'N', \"{U+\", \"\\\\N{U+0041}\", M_unicode_props, FLAV_PCRE2, ANY_ENGINE,
 RS_MODULE, RD_MODULE, NULL, NULL, RF_CLASS_INVALID,"
