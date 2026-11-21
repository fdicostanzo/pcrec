# verify.md — r65 l3feat (coordinator, inline: every CONFIRMED finding is a stamp, quote or one-call perf claim)

Calls recorded; outputs in .coord/verify/ where files were made.

- EMIT-1 HOLDS. Fresh compiles (`kit/pc base|subject --features all -p rx -o ... --pattern '(?<=qz)x?a:'`, gcc -O2 with emitted/perf/bench.c), `taskset -c 7 perf stat -e instructions:u`, 3 repeats, subject emitted/perf/subj/qzxa.absent: base 225,064 / subject 2,325,063 (x10.3, spread 0); answers equal ([0 0]). Stamps: base `RX_REQ_RUN "613a@1"`, `RX_REQ_HANDOFF "1"`, `RX_DFA_PREFILTER "handoff"`; subject `"717a@1"`, `"-2"`, `"memchr"`. qzxa.common: 6,468,719 -> 6,589,273 (+1.9%).
- EMIT-2 HOLDS. `(?<=foo)bar` on foo.common (16,381 matches): 5,141,264 -> 6,063,827 (+17.9%); foo.decoy 4,371,786 -> 2,063,553 (0.47). Answers equal.
- EMIT-3 HOLDS. `--emit-facts '(?<=xyz)a+xyz'`: base `req_byte 122` / subject `97`.
- EMIT-4 HOLDS. base `req_whole_run none dead`, `RX_REQ_WHY "dominated"`, `RX_REQ_HANDOFF "none"`; subject `6263 dead`, `"emitted"`, `"-1"`. span_arms.md (subject) cites `(?<=ab)(?<=cb)c` as W-D2 (guard against guard, dead); the §14.2 row quote is the critic's (not re-read line by line).
- EMIT-5 HOLDS. `RX_DFA_PREFILTER_OFFSETS` base 0..19 (8*), subject 0..11.
- WALK-1 HOLDS. `(?<=(?<=x)a)b`: run none, K 0; `(?<=(?<=x)a)b(?<=..b)`: run 786162 at -2.
- CONTRACT-1 HOLDS. run_recursion_identity.sh:1261 at subject `FILEPIN=...d68a1294c ... abi 109 (no bump)`; `git diff --stat 694d91dc4 3f02ca8ab -- tests/codegen/run_recursion_identity.sh` empty; :490 "requires their `rx_info.abi` stamps to agree".
- CONTRACT-2 HOLDS. tuning.md §2.41¶8b at subject: "The first attempt starts at `max(startpos, c − K)`, `c` the least candidate at or after the startpos (¶1)" and "(the candidate last found while it is still ahead, ...)" (quoted from the review tree).
- CONTRACT-3 HOLDS. emit_dfa.c:1547 `p[i].omin = 0;` inside the loop over every entry, :1550 overwrite of `p[np - 1].omin`.
- CONTRACT-5 HOLDS. `(?<=x)qzjv[a-z]*\d`: base `emitted`/`"0"`/`handoff`; subject `dominated`/`"none"`/`memchr-bounded`.
- HOUSE-1 HOLDS. emit_dfa.c:9443 the [REQ-HANDOFF-L1] header block ends at :9467, `req_k_reentry_sound` :9468, `pf_handoff_applies` :9473 with no header.
- CHECK-1 HOLDS. plant S3405 artifact (Pattern header checked) :236 `size_t landmark_position;` then 3 lines of req_byte presence, the `(search_from >= 6 ? search_from - 6 : 0)` ask at :240; run_prechecks.sh:2065 greps `-A1` after the declaration.
- CHECK-2 / CONTRACT-4a HOLD. `git diff --name-status 694d91dc4 3f02ca8ab -- tests` (non-sabotage): 12 modified files, no added file, no tests/lookaround change.
- CHECK-3 / CONTRACT-4b HOLD. S3407 `SAB_EXPECT=UNDETECTED`, no SAB_REQUIRE.
- MOVE-1 / HOUSE-2: by construction (critics' read) + the probes of two critics (no `size_t landmark_position;` in ~350 subject artifacts); not re-probed.
- HOUSE-3..7: code/text reads; not re-verified beyond HOUSE-1's lines (no code change of answers rests on them).
VERIFY COMPLETE
