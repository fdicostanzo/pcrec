# TRADE lens: trailgc (SUBJECT 801ad12, BASE b05ccfc)

## Findings

### TRADE-1: abi bumped 91 -> 93 but the identity gate's (B) pin (`FILEPIN`) is still the abi-91 commit; the gate hard-fails
- status: CONFIRMED by reading the gate (not run; no suites allowed). `tests/codegen/run_recursion_identity.sh:1285` `FILEPIN=02229045e`; `git show 02229045e:src/gen/emit_dfa.c` has `PCREC_ARTIFACT_ABI 91`; SUBJECT has 93. Lines 1385-1393 compare the two compilers' `.abi =` stamps on the pattern `a` and, on mismatch, call `bad "the emitted scaffolding changed: bump abi ... and re-pin comparison (B) ... in the same change (D76)"` then `exit 1`. The file is not in the branch diff (diff --stat touches only run_codegen_tests.sh and run_tiered_entry.sh under tests/codegen). Makefile:1224 runs it.
- severity: design (process; the branch is red on `make test` until re-pinned)
- effort: one-line pin edit, but the pin must name a commit that carries abi 93 (the lane's last src commit, the self-pin convention the file's own comments describe: "`88d3c5209` is the lane's last src commit; the manager re-pins to the merge"). The branch did the first half for no earlier lane to copy here: nothing was self-pinned.
- blast radius: test-codegen / recursion-identity (B) whole-file axis; CLAUDE.md situation row "change emitted scaffolding" says abi bump AND re-pin in the same change.
- location: tests/codegen/run_recursion_identity.sh:1285.

### TRADE-2: D183's "+1.1-2.1 % instructions on the never-full path" does not reproduce on cscan, and is 10x off on the recursion specimen
- status: CONFIRMED. Reproduction (BASE compiler built in scratch/base, SUBJECT = review tree build; `--features all`-equivalent cscan feature list from cscan.rxt, `--engine=vm`, -O2 gcc, driver loops `rx_search` N times, `taskset -c 7 perf stat -e instructions:u`; every run rc=1 match, trail far below the floor so never-full). Instruction counts are deterministic (3 repeats within 50 insns):
  - cscan, 40-ident subject (271 B, 200k iters): 12,472,722,4xx -> 12,841,522,4xx = **+2.96 %**
  - cscan, 5x mixed-statement subject (236 B): 15,190,122,754 -> 15,533,922,796 = **+2.26 %**
  - cscan, 40-deep parentheses (88 B): 8,474,722,009 -> 8,826,922,144 = **+4.15 %**
  - `^(a(?1)?b)$`, n=100 (100k iters): 1,509,021,226 -> 1,805,121,241 = **+19.6 % instructions**; cycles 4 repeats 503-516 M -> 565-599 M = **+12 to +16 %**
  - `(?:(\d+),)*(\d+)` 25 numbers: 898.6 M -> 918.1 M = +2.2 %
  Cycle counts on the cscan cases are noisy (base 3.58-3.90 G across repeats; subj 3.75 G; one run subj < base) so no cycle claim is made for them.
- The decision text gives the cscan figure only as a range with no pattern or subject named; the first three cscan subjects here are 2.3-4.2 %, outside it, and the recursion specimen the spec uses as its worked example pays ~20 % instructions because every region return is a checkpoint. D183 does not mention the recursion-heavy cost. Judged by: D183 (Frank's go) against option 1's +5.3-12.8 %; the specimen's +20 % was not in the comparison as far as D183 states.
- severity: speed
- effort: re-state D183/known_issues with the measured per-pattern range; whether to accept +12-16 % cycles on recursion-heavy never-full runs is Frank's call, D183 only prices cscan.
- location: docs/dev/decisions.md D183 Decision line; known_issues.md K134 Fixed line ("+1.1-2.1%").

### TRADE-3: code size and matcher stack frame grow, neither is priced or in the spec's stack numbers
- status: CONFIRMED. `size` of the compiled driver (.text): cscan 30,289 -> 31,205 B (+916, +3.0 %); `(?:(\d+),)*(\d+)` 9,204 -> 9,844 B (+640, +7 %). Artifacts with no trail-writing cycle (`a(b|c)+d`, `(\w+)\s(\w+)`, `^(?:(a)|b)*c`): diff is 6 abi lines only, as the changelog says.
- `gcc -fstack-usage`: `rx_match_anchored` 56 -> 128 B (cscan), 56 -> 112 B (specimen); new `rx_trail_compact` frame 160 B (cscan, 83 slots) / 80 B (specimen), nesting under the matcher when it runs. `seen[RX_NSLOTS]` is 1 B per slot, so a many-capture VM artifact adds that many bytes on top at compaction time. Entry frames are unchanged (`rx_search` 3,184, `rx_search_in` 144 on the specimen; cscan 3,168), so limits.md §5¶2 / ¶6 and the thread tests' 128 KB bound are still true as written; the deep-tier frames (131,2xx) are unchanged. Not re-pinned and no spec sentence mentions the matcher frame, so nothing is contradicted; the cost is un-judged.
- severity: size (small); stack (small, one extra callee frame on the already-deep path)
- location: src/gen/emit_vm.c vm_emit_trail_compact; match_api §10 / limits §5 are silent.

### TRADE-4: the abi number 93 rests on a claim ("92 is the memfn kit's S3") that nothing in the tree supports
- status: SUSPECTED. changelog top entry and D183 say 92 is S3's and not yet on main; memfn/docs/wake.md and journal.md in the same tree say S3 holds **85** (reserved since EMIT-BIDI took 86; changelog line for abi 88 still says "85 stays RESERVED by S3"). grep of memfn/docs, owner.md, wake.md for abi 92 finds nothing. Precedent exists for skipping a reserved number (86 over 85, 89 over 88), and the entry is labelled provisional/renumberable, so the harm is a renumber, not a wrong answer; but the judge of "92 is S3" is nobody in the tree.
- all other readers of the number moved: grep of the branch for `abi 91`, `ABI 91`, `PCREC_RX_ABI_H 91`, `=91` leaves only S693 (intentionally 91 as the "not bumped" value, correct), historical comments, and the FILEPIN (TRADE-1). match_api.md §1/§6¶17 and the info table, tests/codegen ABI_EXPECT=93 all moved.
- severity: doc
- effort: confirm with main's wake/owner what number the kit holds; trivial renumber.

### TRADE-5: framebuffer 64 MB check changed from a range to an exact formula whose "17" is the implementation's output, and no longer exercises the trail-binding side at scale
- status: SUSPECTED (judgement). Old check (d): ceiling lies between n=466,000 and n=470,000 (a range, derived from the 8.98/level design measurement). New: exact `min(nframes/2, (ntrail-17)/4)` at n=838,860 / 838,861. Tighter, not looser, and the formula is derived in limits.md §4 paragraph 3 (lane/trailgc) from `L(n)=3n-2`, quarter rule and the artifact's 15-site margin (17 = 15 + 2 rounding), and fb_exact_driver.c checks `4n+17` exact with one-short arms at n = 761..765 (and the report says 7..5000), which I did not rerun. But at the 64 MB reservation the frames bind (838,860 < 1,048,571), so the "trail is the array that binds, predictable from ntrail" half of the old check is now only covered at small n by fb_exact. Also `17` is the specimen's margin; the spec states it as the specimen's constant, and the check computes it as a literal, so a changed margin (site count) moves both without independent evidence. No cell dropped; one in-between gu cell (n=500 in sr_depth) became 1000 and n=500 is now an unasserted match depth.
- severity: maintenance
- effort: low (add a trail-binding row at scale, e.g. frames=2x trail so the trail binds).

## PROBED-AND-HELD
- Reach: `^(a(?1)?b)$` default `--emit-main` engine=vm, a^n b^n, BASE vs SUBJECT, n in {342,343,512,513,763,764}: BASE matches only 342 (frames from 343); SUBJECT matches through 763 (1,526 B) and gives PCREC_ERR_FRAMES at 764. Boundary 342 -> 763 reproduced; 764 gives up as documented (6 subjects x 2 compilers).
- K134 cscan: the 5 K134 subjects from cscan.rxt (idents 2,661 B, splices 2,107, parentheses 607, mixed 2,816, braces 131): BASE returns frames on all 5, SUBJECT matches all 5 with span 0..len; libpcre2-8 (default limits, same pattern, compiled from the rxt's unescaped text) matches the same spans on all 5 (rc=2, offsets equal). 5/5 identical, 5 BASE give-ups answered.
- Non-trail-writing VM artifacts byte-identical bar abi lines (3 patterns, 6 diff lines each); trail cycle patterns get 2 TRAIL_CHECK sites and ~43 diff lines (2 patterns).
- Spec/doc hunks moved consistently with 763/764, 1,526/1,528, 4n+17, 838,860/838,861: limits.md §4¶1-3 and §5¶6, match_api.md §10.1¶1/§10.6, guide, tuning §2.11¶2, ts4 TS4_N=763 with its 3,069 trail bound (4*763+17), run_frame_buffer.sh giveup subject a^764 b^764, fb_mmap defaults, S155/S179/S180 comment re-aims (comment-only; S179/S180 cell now 2048,8192 with a swapped-capacities case the file argues still fails: 2,048 < 3,073). No check was loosened: fb_exact 8.982-ratio slack replaced by an exact boundary; gu cells moved up with the ceiling (343->764, 500->1000, 2000 kept); thread-stack bound (128 KB) not raised.
- Stack: entry frames unchanged (rx_search 3,184 / 3,168, rx_search_in 144, deep tiers 131,2xx); only matcher-local and compact frames move (TRADE-3).
- Remaining stale 342/343/684/686 hits under tests/ and docs/spec are historical comments or unrelated numbers (swept grep, ~40 hits looked at).
