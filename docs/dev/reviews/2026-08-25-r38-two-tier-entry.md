# r38 — D6 critic on [OPT-1]'s two-tier default entries (lane srTier at 1785a9d/cd1536e, abi 5)

Critic: critTier (opus; engine-semantics + check-design lens), read-only,
no make; compiles in its scratchpad. VERDICT: NO BLOCKERS. Identity
survived attack — 802 subjects on `((a)|(aa))+b` (FAST 62/94 vs
2048/3072), 377 ESCALATING, capture arrays prefilled and compared
byte-for-byte against `_in` at the default descriptor: 0 return diffs, 0
capture diffs; budgets genuinely restart on the deep run; TRAIL and
FRAMES exhaustion both report FRAMES so escalation covers both; the
fast attempt writes no capture on a give-up. `noinline` holds at -O0..-O3,
-Os, -fno-inline, forced inline limits (worst fast frame 3,264 B, 832 B
under a page) and under LTO (objdump: the fast entry has no probe
sequence; the deep function carries it). `-fno-tiered-entry` reproduces
main's artifact byte-for-byte apart from the two stamps and `.abi`.
The K33 re-derivation (entry + deep = 134,400 B) is the right quantity —
the fast frame IS live at the deep call.

## Findings and triage

| # | severity | finding | disposition |
|---|---|---|---|
| 5a | should-fix | limits.md §3.2 and match_api.md §3 pair the EMAIL specimen's timing (233.8 → 46.6 ns) with `^(a(?1)?b)$`'s frames (131,216 → 3,184); the email specimen's frames are 98,512 → 3,168 (design §1 correct) | FIXED 36c8234 (both paragraphs; the lane's own six-repetition timings replace srOpt1's single figure) |
| 5b | should-fix | design §7 and the spec understate the escalation cost and omit the CLIFF: the wasted fast attempt is bounded by the STEP/WORK budget, not by frame count; measured `((a)|(aa))+b` tiered vs single-tier: n=1 43 vs 241 ns (5.6× faster) … n=20 305 vs 499 … n=24 867 vs 560 (1.55× SLOWER) … n=64 1,772 vs 1,087 (1.63×) — a 2.8× discontinuity at the boundary, ~1.6× slower above it, and "deep" = a 22-byte subject there; an escalating call can do up to 2× STEP_BUDGET of work | FIXED 36c8234: design §7 opens by saying it was wrong; reproduced n=1 18.5 vs 207 (11× faster) … n=24 569 vs 373 (1.53× slower, a 3.05× jump across ONE byte — the boundary subject is 25 B, not 22) … n=64 873 vs 667; stated in design §7, match_api §3/§4/§10.9, limits §3.2; the exemplar-file escalation rate named as the follow-up |
| 5c | should-fix | tuning.md §2.12's transcript does not reproduce (the grep also matches RX_RESUME_/RX_TRAIL_ lines and the RX_TRAIL macro) | FIXED 36c8234 (anchored on `^#define RX_FAST_`; reproduces byte for byte) |
| 3a | should-fix | run_tiered_entry.sh bounds the fast tier from ABOVE only (§4 catches too-large); a too-SMALL fast derivation with stamp and bind moving together leaves every check green while the tier degrades to escalate-on-everything; VM_FAST_TIER_MIN asserted nowhere; §2's only floor is NTIER ≠ 0 (272 → 1 would be green) | FIXED 36c8234: three arms — A tiered population floored at 250 (272), B every tiered artifact FILLS its page budget to within one frame + one trail entry (derivation-independent: asserts the property, not the scaling), C nothing tiers below VM_FAST_TIER_MIN read off the artifact; VALIDATED by halving the derivation → floor B alone red on 271/271 with every answer and span still correct — the measured proof the degradation was invisible before |
| 3b | should-fix | tier_driver.c compares RETURNS only; design §6 promises returns AND SPANS; the specimen's single whole-match group is too weak anyway | FIXED 36c8234: the driver memcmps the whole RX_NCAPS-pair array against `_in`; `((a)\|(aa))+b` (RX_NCAPS 4) at 60 depths, 37 escalating, all span-identical |
| 6 | note | capture-heavy patterns (>~145 slots) get no tier at all (design §3.1 case 3, working as written); artifacts AT the cutoff (FAST=16) are the "escalate on nearly everything" case §3.1 warns of; no measurement says a 16-frame tier wins | recorded on [OPT-1] as a follow-up with the escalation measurement; a `--fast-tier=N` knob is the general lever if the number says the default is wrong |
| Q4 | note | rx_search_run (112 B) and rx_match_anchored (56 B) are separate frames on the deep path in neither the old nor the new number (168 B understated, symmetric); a musl thread also carries TLS/guard — the 3,328 B margin swamps both | recorded; K33 arm A stands |
| Q1/Q2 | no finding | see the verdict paragraph | — |

## What this changes
The ruling stands (Frank, 2026-08-25: the two-tier entry). The design's
BET — that the overwhelming majority of real calls hold on the fast
tier — now has its cost stated when it loses, and the measurement that
decides it (escalation rate over exemplar subjects via the
`-DRX_TEST_TIER_HOOK` counter) is [OPT-1] STEP 3, before any tuning of
the fast size. The check-design lesson, again: a check that can tell a
BROKEN mechanism from a working one may still not tell a USELESS one —
floors on the mechanism's own effectiveness are a separate arm.
