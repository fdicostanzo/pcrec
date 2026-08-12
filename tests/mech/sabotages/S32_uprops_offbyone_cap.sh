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
SAB_COUNT=1
SAB_BEFORE="        if (sig_count == PCREC_UPROP_NAME_MAX)"
SAB_AFTER="        if (sig_count == PCREC_UPROP_NAME_MAX + 1)"
