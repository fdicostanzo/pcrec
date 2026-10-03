# S442 ([OPT-LITSCAN] S4 C0, lane s4build) -- THE BYTE-DOMAIN CUBE READER
# PASSES THE SECTION FORM'S BASE.
#
# `pcrec_cube_of` is ONE definition parameterized by its domain
# (litscan_s4.md §1.2): clskit passes a section's own span, where offsets are
# relative to the section's low member, and `pcrec_cls_cube` -- the reader the
# run facts use -- passes the ABSOLUTE byte domain, base 0 and width 256. The
# plant hands the absolute reader the section form's base (the class's low
# member) instead of 0. Every set still reads as a cube, but T comes back
# relative to its low member: {S, s} gives K = 0xDF, T = 0x00 where the mask a
# caseless run compares against is T = 0x53. The detector is the fold
# agreement check's (b) arm (tests/backrefs/fold_agreement_check.c, run by
# run_backref_diff.sh §9), which asserts T = c & K on all 256 fold sets; no
# emitter reads pcrec_cls_cube at C0, so the corpus is green by construction.
SAB_ID="S442-cls-cube-section-relative"
SAB_FILE="src/core/cpset.c"
SAB_SUITES="brefdiff"
SAB_DESC="pcrec_cls_cube passes the class's low member as the cube's base instead of the absolute byte domain's 0, so every fold set's T comes back relative to its low member (K=0xDF, T=0x00 for {S,s}) and a caseless mask would compare against the wrong constant"
SAB_DOC_FIGURE="Read the current figure from a run (predicted: brefdiff §9 red, 'CUBE 0x41 ... T=0x00, expected ... T=0x41')."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (!pcrec_cube_of(a->u.cls.iv, 0, a->u.cls.n - 1, 0, 256, &care, &val))'
SAB_AFTER='    if (!pcrec_cube_of(a->u.cls.iv, 0, a->u.cls.n - 1, a->u.cls.iv[0].lo, 256, &care, &val))   /* SABOTAGE S442 */'
