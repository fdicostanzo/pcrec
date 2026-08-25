# S32 — the 48-significant-character cap becomes 49, an off-by-one on
# PCREC_UPROP_NAME_MAX. libpcre2 10.46 measures the boundary at exactly 48
# (tests/probes/probe_uprops.c: n=48 significant chars is well-formed
# [err 147, unknown name], n=49 is malformed [err 146]) — this sabotage
# makes pcrec accept one MORE significant character than PCRE2 does before
# calling the body malformed, which is a tier-1 divergence (D26: what a
# pattern MATCHES/is-real is exact) at exactly the boundary this module
# exists to get right. Caught by the boundary reject-pins
# (tests/reject/run_reject_tests.sh's 48-A / 49-A rows).
SAB_ID="S32-uprops-offbyone-cap"
SAB_FILE="src/parse/mod_uprops.c"
SAB_SUITES="reject"
SAB_DESC="pcrec_modport_uprops: the significant-character cap check off by one (48 -> 49)"
SAB_DOC_FIGURE="measured at MOD-0.6 phase 2 landing: the 49-A boundary reject-pin (expects malformed at offset 52) flips to the well-formed generic message"
# [MECH-REACH, 2026-08-25] THIS ROW DECLARES ITS WITNESS'S REACH.
# THE WITNESS IS THE 48/49 BOUNDARY ITSELF, both sides, because an
# off-by-one is invisible from either side alone: 48 significant characters
# must read WELL-FORMED and 49 must read MALFORMED, both blamed at offset
# 52. Under the sabotage the boundary moves to 49/50 and the second line is
# what goes red -- so a reach check asserting only the first would be green
# on a tree where the row had nothing to detect.
SAB_REACH='"$PCREC" --features none -p rx -o "$REACH_TMP/o0.c" -- "\\p{AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA}"; "$PCREC" --features none -p rx -o "$REACH_TMP/o1.c" -- "\\p{AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA}"'
SAB_REACH_EXPECT="\\p requires module 'unicode-props' (pattern offset 52)
\\p: malformed property escape — requires module 'unicode-props' (pattern offset 52)"
SAB_COUNT=1
SAB_BEFORE="        if (sig_count == PCREC_UPROP_NAME_MAX)"
SAB_AFTER="        if (sig_count == PCREC_UPROP_NAME_MAX + 1)"
