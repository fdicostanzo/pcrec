# famdef3 report

## STATE AT HANDOFF

- tests/fuzz/fuzz.py: the [VLOOKBEHIND] stage-2 clean refusal ("a lookbehind containing a backreference, a variable or a consuming callout is not implemented", direction pcrec REJECTS / pcre2 ACCEPTS) is a named known class (`vlb_stage2`, printed, not a divergence). Any other mismatch stays a divergence. The class retires when [VLOOKBEHIND] stage 2 lands (comment at `_VLB_STAGE2_MSG` lists what to delete).
- `fuzz.py --self-test` covers: known class counted; other refusal, wrong direction, empty/None message all NOT known. Passes.
- Seed 1 (extended, 1500 patterns, nice, --jobs 2): rc 0, class count 8, accept/reject divergences 0, content divergences 0.
- OWED: queued job `424-famdef3-fuzzext` (self-test + seeds 1-4 x 1500). Completion: `scripts/boxqueue state famdef3-fuzzext` exit 0; log under worktrees/.boxqueue/.
