# pagebyte report

## Summary
CI red: `entry -g .` printed 4102 B (limit 4096) because a -g page was capped by count (15) and a per-line clip (200 chars), not by bytes; two-line level-0 items with long lines overran. Pages are now byte-bounded.

## Change
- scripts/doc_profiles.py: `PAGE_BYTES = 4000`.
- scripts/entry: `clip_page()` clips lines to LINE_CLIP, then narrower (down to 8 chars) until page + footer bytes fit PAGE_BYTES; cut lines end in "…". Applies to the paged -g listing only (single lookup, -l 1/2, --all untouched). Ranking and tiling unchanged. Threshold 4096 not raised. `-g .` now prints 3991 B.
- docs/dev/doc_format.md: -g contract states the byte bound.
- selftest: plant of 20 rows with 400 multibyte chars each stays under PAGE_BYTES with a cut marker and page note.

## Checks run
make -s test-doc-lint (0 failed), make -s test-plan-lint (0 failed), entry --selftest (76 checks, 0 failures).

## STATE AT HANDOFF
Committed on lane/pagebyte. No rulings applied (rulings file empty). Nothing in flight.
OWED: none
