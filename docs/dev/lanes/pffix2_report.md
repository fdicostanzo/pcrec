# pffix2 report

## STATE AT HANDOFF

STATE: delivered. Branch lane/pffix. Cloud run 43109025391 (sha 308433975) had four red shards; every
red is an EXPECTED consequence of pffix (28 pairs / 14 patterns become the empty engine; abi 99 -> 100).
No real regression found; no `src/` edit. Failing lines extracted with tests/ci/cloud_failures.sh.

1. **shard 3, test-compound** (3 checks, one cause). 14 never-match patterns (`ab\A`, `x\Ay`, `a\Gb`,
   `x\G`, `ab\Gcd`, `ab\Acd`, `(?m)^a(?-m)^b`, `(?m)^a(?-m:^b)`, `.{1,3}\Aa*`, `.{1,3}^a*`,
   `[a-]{1,2}\A-`, `[a-]{2}^a*`, `\s{2}^`, `a{2}^-`) are accept-free, so they no longer split into a
   compound. Class: expected consequence. Fixes: (a) tests/compound/admitted.tsv, the 28 (pattern, arm)
   rows removed (the list is check_admitted.py's own "no longer admitted" lines, each pattern checked
   above as never-match); (b) check_lever.py FLOOR 80 -> 60 (the population is 73 now, 97 at B4; the same
   ~0.8 ratio); (c) the E0 rank fixture row `gfloor` used `a\Gb`, itself now empty (no `rx__f_search`
   call, entry_rows[] says None): the witness is now `a\Gb|\Gz`, still a split compound with the
   `search -> comp_a` R2 edge. Local: test-compound, see below.
2. **shard 6, test-cpset-structure** ([3] manifest drift). Diff read: all 12 sample rows moved, only
   EMITTED_BYTES, each by exactly +5. The `--features all` artifact holds the abi number at five places
   (header comment, guard `#if`, `#error`, `#define PCREC_RX_ABI_H`, `.abi =`; grep of 100), each gaining
   one digit. No stamp moved. Class: expected (abi event). Fix: manifest re-recorded (+5 each) with a
   dated RE-RECORDED note in run_cpset_structure.sh. Local: green.
3. **shard 11, test-resource** `a{5,25000}` rung 767073 -> 767075: +2 = the abi digit at two places
   in that artifact (header comment, `.abi =`). Expected. Re-pinned with a dated comment.
4. **shard 13, test-partlayout** census "all 387 population patterns still carry a subject": 12 of the
   387 are never-match (empty engine: no parts, no subject by construction): `(?m)^a(?-m)^b`,
   `(?m)^a(?-m:^b)`, `.{1,3}\Aa*`, `.{1,3}^a*`, `[a-]{1,2}\A-`, `[a-]{2}^a*`, `\s{2}^`, `a\Gb`, `ab\A`,
   `a{2}^-`, `x\Ay`, `x\G` (measured by running the census's own loop, then each read by hand). The
   population rule is fixed, not the floor: a declared NEVER_MATCH set, and the lost set must EQUAL it
   (an unannounced loss fails, and so does a declared pattern that regains a subject); the subject floor
   is 370 of 380 (375 measured). Class: expected.

Local verdicts (single sections, `nice make -j4`; the three below ran concurrently, each its own
tree-local scratch): see VERDICTS appended below.

5. **axes run 43109089847, shard 8/20, `[COMPOUND] the lever's property`**: the same check as red 1
   (check_lever.py, "73 forced-off pairs, below the floor 80"), reached through run_axes.sh, which shells
   out to it (the AXIS FAIL line quotes it verbatim; nothing else failed in that shard's log). Same cause
   (14 never-match patterns became the empty engine), same fix (FLOOR 80 -> 60, population 73).

## VERDICTS (local, single sections, nice make -j4, 2026-11-11)
- test-compound: PASS (includes the lever check at floor 60, the admitted manifest at 73 and the E0
  rank fixture with the `a\Gb|\Gz` witness). Log scratch/pffix2/compound2.log.
- test-cpset-structure: green (cpset2.log). test-resource: green (resource1.log).
- test-partlayout: checks failed: 0 (partlayout1.log).
Cloud: test and axes dispatched after the final commit (see the handback).
