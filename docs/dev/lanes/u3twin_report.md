# u3twin report -- [UCP] U3 island hand-twin (2026-09-30, sonnet, measurement only)

Branch `lane/u3twin`. Memo: `docs/design/ucp_measurements/u3_island_twin.md`.
Harness: `studies/u3_island_twin/`.

## Delivered
- Island twin generator (F1 computed from pcrec's flat byte tables; F2
  hand-derived), three vector producers, eight cases, oracle (local and 10.46
  over ssh), correctness driver, sanitizer mode, failing-direction controls,
  reach census, timing harness, bundle.
- Correctness COMPLETE: 8 cases x 31,168 cases, 0 differences against libpcre2
  10.46, today's artifacts, forced VM and each other; ASan/UBSan clean.

## OWED
- ubuntubudu timing and the D77 verdict: not run, "TIMING GO" not received
  before hand-off. Resume: memo section 5 (bundle at
  `studies/u3_island_twin/out/u3twin_bundle.tgz`, regenerable by `bundle.sh`
  after the gen/build steps in the study README).

## Findings so far
1. F1 twins fall out of the byte tables mechanically: 2 boundary states per
   direction for every consuming class tried (base 12-698 states).
2. The design's ⊥ rule and repaired back_step hold end to end against 10.46
   on a 31k-case ill-formed matrix, forward, reverse, seed and reverse
   boundary.
3. A twin without the artifact's own necessary-byte pre-check loses ~80x to it
   on text lacking the byte (Mac scratch, loaded box): the island's fair
   comparison keeps today's pre-checks in front, as ucp_design s3.6 says.
4. Local libpcre2 10.48 (Unicode 17) disagrees with pcrec's UCD 16 on new
   code points; use the 10.46 reference for any Unicode-set oracle.
5. Three of thirteen planted defects are unobservable for these patterns
   (memo s2); do not read the controls as covering surrogates or overlong
   ASCII.
