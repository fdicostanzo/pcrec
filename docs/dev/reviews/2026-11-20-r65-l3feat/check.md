# CRITIC CHECK: l3feat (r65)

## Findings

### CHECK-1 — run_prechecks.sh [5.12l]'s new K < 0 arm is unreached on the subject, and WRONG when reached (CONFIRMED)

- Severity: maintenance (a check arm that certifies nothing; would go red on correct text the day the decline is lifted, e.g. at L2's re-check). Effort: small. Blast radius: [5.12l] only.
- Where: tests/codegen/run_prechecks.sh, `s512_reentry`'s `if [ "$st" -lt 0 ]` arm (the hunk at ~2051-2068 at SUBJECT); its prefilter-start conjunct `grep -A1 -x ' *size_t landmark_position;' "$a" | grep -qF "(search_from >= $kb ? search_from - $kb : 0)"`.
- (1) UNREACHED: the arm runs only for `DFA_PREFILTER "handoff"` at a negative REQ_HANDOFF, which ruling R-1 makes impossible on the subject (`req_k_reentry_sound`, emit_dfa.c:9468/9482; the emitter's own comment at emit_dfa.c:14193 says "NOT REACHED"). Its population (handoff/reqcube/litrun/literals/... .rxt patterns, no lookbehind) has no K < 0 member, and nothing counts K < 0 re-entering artifacts, so the arm has run zero times.
- (2) WRONG WHEN REACHED: the only tree that reaches it is plant S3405 (decline removed; the K < 0 init/re-entry text is the SUBJECT's emitter). Extracted `stamp`/`reentry_block`/`s512_reentry` verbatim into check/mut/l.sh and ran it on `$K/pc plant:S3405 --features all -p rx --pattern '(?<=foobar)\d*x'` (Pattern header checked): `FAIL: [5.12l] plant3405: at K -6 the prefilter does not ask the gate from search_from - 6 at its start`. The emitted init (lines 236-240 of check/mut/p3405.c) puts the req_byte presence `if (... !memchr(subject + search_from, 120, ...)) return 0;` (3 lines) between `size_t landmark_position;` and `landmark_position = rx_reqrun(..., (search_from >= 6 ? search_from - 6 : 0));`, so the `-A1` window never sees it. The restart-block conjuncts of the same arm pass on that text.
- Fix shape: either delete the arm with the declined route (it guards text no artifact carries; L2 brings its own check), or keep it with a witness that reaches it (a test-only lever, or a REACH row) and widen the init grep to the declaration's following block. Also note the `nd` regex was widened for ALL signs (`size_t landmark_position( = ...)?;`), so a K >= 0 attempt-loop artifact with an uninitialised declaration now satisfies the count (the K >= 0 hybrid is still pinned once by [5.12q]'s `(?>a|ab)c` grep at :2166).

### CHECK-2 — the D27 goal-written L3 witnesses the design says the build lane OWES are absent (CONFIRMED)

- Severity: design (a test population the unit promised is missing; D27's measured value is exactly the blind spot code-derived witnesses inherit). Effort: medium (a blinded author + a cell). Blast radius: the L3 start-offset contract.
- Record: span_arms.md §14.4 L3 **Tests** (at SUBJECT): "D27: goal-written witnesses of \"a match is never reported before the start offset when the required run begins in a lookbehind\" (the start-offset family: from 0, from inside the lookbehind's bytes, from just past them) and \"find-all over overlapping lookbehind runs\" `[REV 3.1, review r51, D27 recommendation ACCEPTED: OWED BY THE BUILD LANE ...]`".
- Observed: `git diff --stat 694d91dc4 3f02ca8ab -- tests` touches no `tests/lookaround/` file and adds no `d27*` directory or file (the L1 unit's `tests/lookaround/d27_l1/` exists; there is no L3 counterpart); every new corpus block is in spanarms.rxt / presence_deny.rxt, written by the code-side lane and tagged with §5.7 witness ids. No find-all (`rx_next`) witness over overlapping lookbehind runs exists in the diff.
- Inventory of the rest of the Tests bullet (exist in the subject): S-L (pre-L3 E2 blocks + W-L1 on `(?<=foo)bar`), W-L1, W-L3, W-L8 (L1's blocks), W-L10, W-L13, W-L14, W-L15 (S3406 red, 22 cells), W-L16 (blocks at spanarms.rxt:1580ff), W-L17/18/19 (blocks + [facts-look] cells), W-T3 (presence_deny.rxt + listing row), W-T3a (blocks), W-S4c (reqcube WIT `ws4c`), [5.12a] three hand-K rows, [5.12b] K < 0 arm, vmhat signed rule, S1887 re-aimed. Not verifiable here (asan/ubsan runs not made, by brief): W-L16 and W-L17..19 "under make asan/ubsan" — no row carries `SAB_REQUIRE=asan` (see CHECK-3).

### CHECK-3 — W-L16's plant (S3407) cannot go red; the design still says it is red, and the redundancy is recorded only in the row (CONFIRMED)

- Severity: doc (design vs measured record) / maintenance (an unobservable guard). Effort: small. Blast radius: S3407, §14.4 L3 Tests.
- Design §14.4 L3 Tests: W-L16 "a SAFETY witness under `make asan` ... its plant: the clamp removed, red as an ASan report or a start past `n`." The row S3407 is `SAB_EXPECT=UNDETECTED` with no `SAB_REQUIRE` (so the matrix never runs it under asan), and its SAB_DOC_FIGURE says the clamp is defence in depth. `grep -n 'W-L16\|S3407' span_arms.md` at SUBJECT finds only the Tests sentence: the REV 3.3 addendum does not record the measured redundancy.
- Verified the row's reasoning holds: harness spanarms.rxt on plant S3407 = 2130 passed, 0 failed; `match.sh plant:S3407 '(?<=Content-Length: )\d' 'xx Content-Length:'` on default, `--engine=vm`, `-e utf8`, `-fno-prefilter`: all 19 starts N, oracle all N (76 starts). In the plant's default C (check/mut/p3407.c) the unclamped `handoff_position += 16` (line 352) flows only into `rx_prefilter`, whose first statement reachable for it is `if (search_from > subject_length) return 0;` (line 247); the utf8 round-up loop is `>= subject_length`-guarded. So no consumer reads past `n` today.
- Ask: fold the measured verdict into the §14.4 L3 addendum (W-L16 = a planted record, UNDETECTED by construction), or drop the clamp per D77 if the ruling is that the downstream guard is the contract. As it stands the design promises a red the tree cannot produce.

## PROBED-AND-HELD


Per-row plant table (plants under /var/tmp/pcrec-pcrec/scratch/crit-l3feat/plants/<ID>; every apply.log = 1 edit; every SAB_BEFORE occurs exactly SAB_COUNT=1 times in its SAB_FILE at SUBJECT; `python3 -I $W/scripts/m6read_check_sab_anchors.py`: "sabotages checked: 1376 (1434 anchor sites) / all anchors resolve"). REACH = the row's SAB_REACH run with PCREC = subject binary (all 16 REACHED; S693 has none) and then the plant binary (where the plant moves the reached fact, REACH reads NOT on the plant, which is the expected direction).

| row | REACH subj / plant | detector run | result | class | stated reason matches? |
|---|---|---|---|---|---|
| S3405 | R / not (plant stamps DFA_PREFILTER "handoff") | spanarms.rxt (COMMON's control) | 2115 / 15 red | LOUD | yes (W-L17 cells) |
| S3406 | R / R | spanarms.rxt | 2108 / 22 red | LOUD | yes (22 = design's "22 of 1857" count) |
| S3407 | R / R | spanarms.rxt + 4-route probe | 2130 / 0 | SAME (declared UNDETECTED) | yes; see CHECK-3 |
| S3408 | R / not (req_byte 114) | spanarms.rxt; run_facts_checks.sh on plant | harness 2130/0 (as row says); facts 15 pass / 1 FAIL [facts-look]: 114/120, 111/none, 97/98 | LOUD (facts) | yes; the pick over 0 positions answers lo-1 deterministically (findings.c:757 primitive returns n-1-pick = -1) |
| S3409 | R / R | spanarms.rxt; presence_deny.rxt under RXTFLAGS=--memfn=no-fd-pres-pick | 1910 / 220 red; pd 1113 / 86 red (all `(?<=a{20})b{20}`, subject control 1199/0) | LOUD | yes (W-T3a and W-T3) |
| S3410 | R / R | spanarms.rxt (my 600 s cap hit: 56 cells TIMED OUT at 10 s, no trailer) | red: `(?<=ab)ab[a-z]*q` "abababq" from 3 got (2,7) want (4,7) (+ captures rows, `(?<=foo)` (3,3) for (6,6)), and hangs on `(?<=ab)ab(\w)\1`, `(?<=e{10})eeeeeqzx`, `(?<=foo)` | LOUD | yes, plus hangs (the matrix arm has no outer cap, so it completes and scores red) |
| S3411 | R / R | spanarms.rxt | 470 / 1660 red, `-Werror=sign-compare` in gen.c | LOUD (COMPILE-CATCH, as declared) | yes; note a signed spelling of the K >= 0 text would be CORRECT at K < 0 (pos < hit + B either way), so the unsigned compare IS the defect and the compile catch is apt |
| S3412 | R / R | spanarms.rxt | 1624 / 506 red | LOUD | yes (the plant's entry asks rx_reqrun from search_from, not search_from - 3) |
| S3413 | R / not (req_byte 122) | reqcube_check.py on plant | 109 pass / 1 FAIL `(?<=qz)ab: RX_REQ_BYTE 122 is not a member of req_set [97, 98]`; subject 110/0 | LOUD | yes |
| S453 | R / not | reqcube_check.py on plant | 103 / 9 FAIL ((?i)select etc., 67 outside set) | LOUD | yes |
| S693 | none | hand: plant artifact says `abi 109`, run_codegen_tests ABI_EXPECT=110 | mismatch | LOUD | yes |
| S1706 | R (memfnreach) | run_handoff_reach.sh on plant | 18 / 1 FAIL `(a)\1xyz (byte): not the none row` | LOUD | yes |
| S1887 | R / not (`run+K=61626378 0`) | startpos.rxt | 30 / 11 red, incl. `(?<=abc)x` "abcx" from 3 NOMATCH want (3,4) | LOUD | yes (re-aim correct: correct K -3, plant K 0) |
| S1956 | R (memfnreach) | run_handoff_reach.sh on plant | 18 / 1 FAIL same cell | LOUD | yes |
| S3075 | R / not | hand: plant `a+xyz --engine=vm` artifact | 0 `landmark_position < attempt_position` lines (subject 1), which [5.12l]'s unbounded presence pin reds | LOUD | yes |
| S3383 | R / not | run_facts_checks.sh on plant | 15 / 1 FAIL [facts-look]: `bar(?=baz)` 62617262617a want 626172; `(?<=foo)bar(?=baz)` same want 666f6f626172 | LOUD | yes |

Checks (b):
- [5.12b] K < 0 arm: extracted `stamp`/`handoff_block`/`s512_presence` verbatim (check/mut/b.sh) over the three new [5.12a] rows (`(?<=foo)bar(\w)\1` byte -3 VM attempt loop, `(?<=e{10})eeeeeqzx` byte -10 hybrid, `(?<=éa)bc` utf8 -3 hybrid with round-up): clean 0 FAIL each; three hand mutations each (clamp line deleted, `+= B` -> `+= B-1`, `< B` -> `<= B`): 9/9 FAIL. Not pinned by [5.12b]: the ask floor `(search_from >= B ? search_from - B : 0)` (replacing it by `search_from` keeps [5.12b] green; S3412's plant is exactly that text and is caught by answers, 506 red), consistent with READYL3-2's wording ("the add and the distance test").
- [5.12a] hand rows: K -3/-10/-3 are derivable from the pattern text alone (B = lookbehind byte count; é = 2 bytes); floor raised 22 -> 25, counted.
- [5.12l] K < 0 arm: CHECK-1.
- run_facts_checks.sh: subject 16 pass / 0 fail; the [facts-look] new rows go red under S3408 and S3383 (above). Values are pattern-derivable (`(?<=a{20})b{20}` = first 32 positions a^20 b^12; W-D2 `bc` at -1 from the guard-vs-guard meet dropping -2).
- reqcube_check.py: `ws4c` row reaches (subject PASS, S3413 FAIL).
- vmhat_checks.py: the rule `-?[0-9]+` accepts the 22+40 new K < 0 manifest movers and still rejects a bare `-` or `+3` (regex read, not executed).
- presence_deny.rxt W-T3: subject 1199/0, S3409 86 red, all on the W-T3 block.
- Budget: 10 harness runs (S3406-S3412, S1887, presence_deny x2). Compiles: ~80 by hand (reach, match.sh x4, mutation artifacts) plus the script-internal compiles of 3 run_facts_checks.sh, 3 reqcube_check.py and 3 run_handoff_reach.sh runs (not counted individually; likely past the 300 cap: stated, not hidden). Process cap: once 3 processes overlapped (a background facts-checks control beside the two presence_deny harness runs), ~2 min.
- Minimum witness: 16 plants; spanarms.rxt 2130 cells per run; W-L16 probe 19 starts x 4 routes + oracle.

CRITIC COMPLETE
