# S59 — [M4.6d] MRL's MINIMUM WIDTH OVER-REPORTS: a bounded repeat contributes
# its MAXIMUM.
#
# The UNSOUND direction, and the only one that deletes real matches. §4.2's
# failure mode 1: `minrest` must be a LOWER bound on what an accepting
# continuation still consumes. Reading `rmax` instead of `rmin` makes it an
# upper one for every range quantifier, so the clamp cuts positions from which
# a match genuinely existed and the matcher reports `nomatch`.
#
# It is exactly the direction that is invisible without a differential:
# subjects with slack still match (the over-estimate does not bite until the
# remaining bytes fall below the inflated bound), so a corpus assembled from
# comfortable inputs stays green. `run_mrldiff.sh` sees it because its ground
# truth is the SAME pattern built `-fno-length-prune`, and its subject sweep
# walks every length up to 24 rather than a handful of chosen ones.
#
# THE UNBOUNDED ARM IS WHY THE EXPRESSION IS WRITTEN WITH A CONDITIONAL rather
# than as a bare `a->rmax`: `rmax == -1` means unbounded, and a bare
# substitution would multiply by -1 and land the saturating helper on 0, which
# is the SAFE direction and would leave `X*`-shaped follows undetected. The
# sabotage keeps `rmin` where there is no maximum so that what it tests is the
# over-estimate and nothing else.
SAB_ID="S59-mrl-minw-overreports"
SAB_FILE="src/opt/mrl.c"
SAB_SUITES="mrldiff harness"
SAB_DESC="pcrec_minw uses a bounded repeat's MAXIMUM count instead of its minimum, making minrest an upper bound: the clamp then cuts positions a real match needed and the matcher answers nomatch"
SAB_DOC_FIGURE="docs/design/k23_impl/k23_design.md §4.2 failure mode 1"
SAB_COUNT=1
SAB_BEFORE='            return mrl_sat_add(acc, mrl_sat_mul(a->rmin, pcrec_minw(a->l)));'
SAB_AFTER='            return mrl_sat_add(acc, mrl_sat_mul(a->rmax >= 0 ? a->rmax : a->rmin, pcrec_minw(a->l)));  /* SABOTAGE S59 */'
