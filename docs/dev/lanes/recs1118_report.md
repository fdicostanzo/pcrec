# recs1118 report

## STATE AT HANDOFF
OWED: none
Rulings file recs1118_rulings.md: empty, none applied. Premise dc6a40dfb is an ancestor of main (yes). `make -s test-plan-lint` PASS (364 rows, 0 violations).

## CHANGES
- docs/dev/plan.md: [LANDWALK] STATE:started, moved with its ten children (nine LANDWALK-* plus SEL-WORLD, which was nested under it) verbatim into Active, before the Candidates heading; status (2026-11-18) names stage 1 landed at dc6a40dfb (abi 95, D184), children open.
- docs/dev/plan.md: [CTX-SIDES-PRODUCER] stays not-started; status (2026-11-18) says trigger fired (cover B1 = bc675b020, 2026-10-23, on main) and the proved-ending-scope owner question is open.
- docs/dev/decisions.md: new D199: (1) owner's "Go on all stages" 2026-11-15 14:50 (verbatim, journal); (2) other-sites-at-32 as the manager's ruling "other-sites-at-32 YES", 2026-11-16, quoted from memfn/docs/requests.md line 968.

## NOT DONE
- [LANDWALK-CARD] left not-started: the commit says "built" but that is the card SCRIPT (tests/landwalk/card_lwalk.sh); its status says the first --timed run is queued, so the row is not complete.
- [LANDWALK]'s old `trigger:` line (rev-2 check, build go) is stale but left, as only tag/location/status were ruled.
- The covs2b assert for other-sites-at-32 (8eca79baf) is not on main; D199 says so.
