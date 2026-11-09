## Findings
- checks-1 (SUSPECTED, maintenance, effort S): no plant for T3's E-5 row arm (req.c:773 `rb_zero_look_pos ... ARM(ZERO)`). S1928 drops only the E-4 row (775); with 775 dropped the fall-through makes the lookbehind a unit too, so the planted ZP listing is the full 7 bytes `78797a61626364` (not the `abcd` the run_facts_checks.sh comment / S1928 header predict: stale comment, doc). A plant on 773 alone would leave `xyzab` under restore=zero; the ZP expectation `78797a` would catch it by my reasoning, but it is not planted/measured (no rebuild allowed).
- checks-2 (SUSPECTED, maintenance, effort S): `restore=zero` (and `restore=empty`) in run_axes.sh INTERNAL_ARMS has no counted reach control; only `no-compound` has a post-loop property check (line ~2327, lever_ran). Reach is hosted only by [facts-arm] (3 hand witnesses). Corpus answers are identical by design, so the axes sweep alone cannot fail if the arm stopped changing facts (K35 population uncounted).
- checks-3 (SUSPECTED, design-gate, effort S): spanarms.rxt has no witness for kind A_CALLOUT (ZERO kind; design E-4 names 'a check callout') nor a quantified zero-width body at E2's site; no plant would notice a callout falling to a gap (speed-only loss).
- checks-4 (CONFIRMED, minor): S1925's `(?<=foo)bar` witness is blind on vm (plant answers match 3 6 on --engine=vm; only AUTO goes nomatch). `xyz(?<=yz)abc` catches both engines, so the row holds; the header's 'search from 3 finds no attempt' claim is AUTO-only.

## PROBED-AND-HELD
- S1925 reach: subject and plant print expected token form (run 78797a616263@2 clean; plant 78797a797a616263@4). Plant `xyz(?<=yz)abc`/xyzabc: nomatch both engines (SILENT-MOVE, rc 1 vs 0), (?<=foo)bar AUTO nomatch.
- S1926: reach OK (78796364@0 clean, planted 787961626364@0); xy(?<!ab)cd/xycd nomatch both engines.
- S1927: reach OK (616278@2 vs 61627879@2); (ab)x\1y/abxaby nomatch both engines.
- S1928/S1929 reach regexes match on subject, and planted output differs exactly as the detectors expect; [facts-arm] ZP and EP expectations go red under plants 28 and 29 (zr/er values mismatch).
- All 63 distinct m/n lines added to spanarms.rxt agree with libpcre2 (pcre2_bounds.py); ms/ns lines hand-checked.
- m6read_check_sab_anchors.py (pure grep, read-only): 1207 rows, all anchors resolve.
- run_lever_fence ALLOW `S192[89]_` correct: only S1928/S1929 name the lever.
- Gate E2 hosting: S-L=S1925, W-E3=S1926, zero arm=[facts-arm]+axes; all hosted (S-g S1927 extra).
- Population: 23 distinct patterns x2 engines = 46 blocks; zero-width 22: lookbehind pos 2, lookbehind neg 1, \b 1, \B 1, $ 1, (?m)$ 1, (?m)^ 1, \K 1, \G 1, \A 1, \z 1, neg lookahead 1, 1-char (?=)/(?<=)/(?!)/(?<!) 4, pos lookahead 1, two negs 1, empty group 1, (?:|) 1, (?:|x) 1; backref 1 (non-zero control).
