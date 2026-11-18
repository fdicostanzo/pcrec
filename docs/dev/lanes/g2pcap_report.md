# g2pcap report

## STATE AT HANDOFF
OWED: none
Fix committed on lane/memfn-g2pcap; all checks green; no rulings entries beyond the brief applied; nothing owed.

## FIX
Cause verified: window.c:3204 refuses a derived run part of more than MF_MAX_TERM (32) terms (r27 READ-1 contract); g2_pres_gen.c derived G2P_MAXRUN = min(64, MF_WSPAN_POS) = 64 once MF_WSPAN_POS became 4095, so runs of 33..64 were drawn. Now G2P_MAXRUN = min(64, MF_WSPAN_POS, MF_MAX_TERM) (= 32), derived from kit constants, a _Static_assert per bound, comment citing READ-1; runtime record line also prints MF_MAX_TERM. NOTES.md sentence updated. No memfn/src change, no emitted-byte change.
Twins: G2W_MAXPOS (128 <= MF_WSPAN_POS, asserted), G2W_REACH (256 <= MF_WREACH, asserted), G2W_LO (== -MF_MAX_BACK, asserted), G2W_MAXSPAN 32 (= MF_WMAX_SPAN), long rows min(4095, spans*MAXPOS): none exceeds a bound; G2 win and full G2 ran green with no MF_MAX_* refusal. Re-pins: none needed (floors passed unchanged: old -> new none).

## CHECKS RUN
- make -j4, make strict: 0.
- run_g2_pres.sh: checks passed 8051517, failed 0.
- make test-memfn-g2 -j4: no test- Error lines; run_g2_win.sh: failed 0.
- m6read_check_sab_anchors.py: 1345 sabotages, all anchors resolve; cloud_mech_check.sh: PASS 90 shards.
- SABOTAGE: MF_MAX_TERM term removed from the min (in place, reverted by checkout): run_g2_pres.sh failed 58 again (checks failed: 58).

## FOR THE MANAGER
No tests/ci shard table changed, so only --kind test is dispatched.
