# l1ffix — review r55's FIX-NOWs and the D27 dispositions on span_arms L1

Lane l1ffix (opus), 2026-11-19. Worktree `worktrees/l1ffix`, branch `lane/l1ffix`, base `3cfcb5210` (lane/l1feat at
its review subject plus main). Review: `docs/dev/reviews/2026-11-19-r55-l1feat.md`, MANAGER RULINGS. Evidence:
`docs/dev/lanes/l1ffix_evidence/` (compare and explain instruments, their outputs, `ident.sh`, `compare.sh`).

## Summary

Every r55 FIX-NOW is applied: A, B, C, D, E (CONTRACT-2), F (CHECK-1..4), G, H, and I's TABLE-3 text and TABLE-4 (c).
The DOC items (CONTRACT-4, CHECK-5, TABLE-4 (a)(b), EMITTED-4, TABLE-7) and r53's owed F2, F5, F11 and F13 are in
span_arms rev 3.3 §14.8. J's two unlocks are filed as plan rows, not scheduled. The D27 witnesses are wired into
`make test`. The five D27 findings F1-F5 are all STATED LIMITS, none in L1's scope, and each FAIL row names its limit
in a check that goes red when a limit is lifted.

- **B's rule** (`src/facts/kset.c`): the pin claims only what the k-set walk proves. The pick runs over the exact
  positions the walk proves a stretch around, and it pins the longest proved sub-stretch around that pick, ties to
  the smallest offset. Where nothing is narrowed this is BASE's pin. BASE's two lost pins are back
  (`xy(?=bc)[bc]c` `0:0+2`, `foo(?=b)[bc]{2,4}` `0:0+3`). The same rule answers L2's §14.1 A5.
- **The compare** (r55-H instrument, BASE `07c840368` vs this branch):
  - PIN-LOST 0 and LANDMARK-LOST/LOOSER 0.
  - All 412 rows are explained, 0 unexplained.
  - Every new `dead` claim is tested: 215 proved by `never_matches`, 36 by a libpcre2 sample; 0 refuted.
- **Movers outside lookaround.** 48 patterns without a lookaround GAIN a pin (`pin-substretch`), for example
  `((ab)+c)+` pins `ab` where BASE pinned nothing. These are performance movers, and the census did not predict them
  (D191 add. 1 (b)): they come from B's general rule, explained mechanically, and the identity job reads them as
  observed movers.
- No STOP fired, no scaffolding mover is expected, and no abi/D/K/R id was taken. No sabotage id from S3385-S3404
  was needed: every row change re-aims an existing row.

## Merges in

Each `git merge` was run alone:

- `9f7af0db2`: lane/l1tri2. One conflict in `docs/dev/history/claude_md/docs__dev__lanes.md`; both lines kept.
- `18f1339fc`: lane/l1ftri, clean.
- `5c9178166`: l1d27, clean.

## Fixes per finding

| finding | commit | what |
|---|---|---|
| A (TABLE-1, CONTRACT-3) | ec0210422, e4e1cd2b1 | `rb_top_set_step` deleted. CAT-SET is a fixed step of `rr_cat` again (`rr_cat_set_side`): a consumed position the meet narrows to one byte joins at its own offset if the set lacks it, and an empty set takes it as pick. `rr_pow` threads the copies' set. `x(?=y)[yz].*qr` gives `113,114,120,121` in byte AND utf8. `walk_arms.def`: `rep` and `empty` now name `req_set`/`req_set_maxoff`; measured, both move it (`x(?:[ab](?=b)){2}`, `x[ab](?=b)()[ab]`), while `tie` and `alt` move no set. `[facts-arm]`'s negative control moved to `kset_walk`. EMITTED-1 unchanged, as ruled. |
| B (EMITTED-2) | cd94ff65d | `pin_proved`/`pin_around` in `pcrec_run_pin` (the rule above); tuning §2.30¶4 in e4e1cd2b1. |
| C (TABLE-2, TABLE-5 item 2) | 140564e2f | `rb_never_pos`, one never leaf on an empty position. Both the class (out of domain: a gap carrying the bit through `rr_cat`) and the `A_CTX` item read it. `x(?=[^\x00-\xff])y` lists `dead` with and without `-fno-ctx-node`. W-D9 is in spanarms.rxt. |
| D (CONTRACT-1) | e4e1cd2b1 | tuning §2.27¶2 (the set gains narrowed one-byte positions) and §2.28¶3 (the body is read; `dead`). |
| E CONTRACT-2 | e4e1cd2b1 | **One clause in facts_listing §4.1.3¶4a** (chosen over letting `harness:` co-exist): a dead `req_whole_run` lists `dead` by ¶1's order, and its derived facts carry the token. Cell `x(?:ab){2}(?=c)d` under `rep`. |
| E CONTRACT-4 (DOC) | e4e1cd2b1 | ¶1a: `dead` on a derived `req_whole_run` only; independent of `never_matches`. |
| F CHECK-1 | 9989cccb0 | S1927 SAB_AFTER `rb_zero_into(w, acc, a, t)`. |
| F CHECK-2 | 9989cccb0 | S1915 anchored on `o.tail = tl.tail;`. |
| F CHECK-3 | 9989cccb0 | S3368: own witness W-L6b `[xy](?:(?=apq)a.?)[pq][qz]zz`. The plant gives `71[717a]7a7a`, red on 2 of 3 cells. |
| F CHECK-4 | 9989cccb0 | S3366: own witness W-L2b `x(?:(?=abcd)ab)cd`. The plant gives `78616263646364`, red on 2 of 3 cells. The design's leftmost groups flatten and never reach CAT-EDGE. |
| F (A/B re-anchors) | 9989cccb0 | S280 (pin, red on run_pinned.rxt 51/4), S1916, S1917, S3375. Every plant was built with ALL its `SAB_*n` edits and the copied binaries deleted, and each moved its witness. |
| CHECK-5 (DOC) | f8e38102b | W-D7 dropped from §5.7's flag-sabotage claim. |
| G (CHECK-6) | 7f595db00 | W-T1 moved into `gen_presence_deny.py`'s CASES. A `routes` field keeps its VM copy, and W-T1 now has cells at every start. The first 721 lines regenerate identical; regenerating twice is byte-identical. |
| H (EMITTED-3, TABLE-7) | 58d8832fe, 3c0ff8477 | Compare: judges `run_pin`/`req_landmark_maxoff` (PIN-LOST, LANDMARK-LOST/LOOSER are disagreements) and labels the other positive-lookaround spellings. Explain: reads every row kind and tests each new `dead` claim (two planted false deads → DEAD-REFUTED). `rep-copy` only on a value move, so r55's vacuous row is no longer taken by it. Classes `look-item`, `pin-substretch`, `route-row`, `dead-both`, `offset-looser`, `d27-limit`. |
| I TABLE-3 | f8e38102b | §12 D168 addendum rev 3 text: member sets, not hulls (D187 add. 1); no form/absent cell at L1 (D77); assembled in req.c until a second reader. **For the manager to file**: decisions.md not touched. |
| I TABLE-4 (a)(b), EMITTED-4, TABLE-7 (DOC) | f8e38102b | span_arms §14.8 items 1, 6, 7, 10, with markers at D-3, D-1, §14.4 L1 abi and common (1). |
| I TABLE-4 (c) | e4e1cd2b1 | the stale `rb_walk_at` comment rewritten. |
| J UNLOCKS | f8e38102b | `[LOOK-STARTSET]`, `[NEVER-DEAD]` (STATE:not-started, triggers), plus a NOTE on [NEVER-MATCH]; plan lint 0. |
| r53 F2, F5, F11, F13 | f8e38102b | span_arms §14.8 items 9, 12, 10, 11. |
| process | 5a2e5198f | pcrec-critic skill §3.2: apply every `SAB_*n` edit and delete the copied pcrec/pcrec-harness before make. |

## D27 findings dispositions

All 88 witnesses answer as libpcre2 on both engines (corpus run). 29 list less than the promise allows. None is in
L1's stated scope; each is recorded per row in `tests/lookaround/d27_l1/l1d27_limits.tsv`. `check_listing.py`
(`make test-lookaround`) requires every FAIL row to name a declared key and no PASS row to name one, so a lifted
limit is red, never a silent pass.

- **F1 `domain`** (A01-A04, A07-A11, A14, A16, A18, A21, A23-A26, A30, B07, B17). A consumed class outside the run
  domain (`.`, `[^z]`, more than `PCREC_MAX_REQ_RUN_POS_SET` = 128 members) is a gap, not a position, so no guard
  meets it. Rests on span_arms §5.1 "The guard" (positions are the sets the domain admits, D187 add. 1). Unlock
  §10 U-descguard.
- **F2 `guard-domain`** (A26, B14, B15, B22). A guard is read term by term outward and ends at its first term
  outside the domain (§5.1 "The guard"). Same unlock.
- **F3 `rep-wall`** (A26k, A31, B14, B14k). The head's REP arm is a wall until R2 (§14.3 D-10, "WHY THE REP WALL
  STAYS UNTIL R2"). Unlock [REPEAT-RUN] R2.
- **F4 `nested-item`** (A11, A11k, A11w). A nested positive lookaround is its own item, conjoined, never merged
  (§5.1 ITEM, ctx_span §3.6), and its narrowing of the body stays in the body (D-1). The general rule that would
  lift it is to meet the head-guard with the body's consumed head run. Not built (D77); new §10 U-nesteditem.
- **F5 `edge-drop`** (B05, `(?=xy)(?=xz)\w+`). The concatenation nests right, so `(?=xz)` meets `\w+` first and
  CAT-EDGE drops its leftover across a non-`all` neighbour (D-3); `(?=xy)` then meets a consistent `x`. The general
  rule is associative guard composition. New §10 U-assoc (not U-exactwidth: `\w+` is not fixed-width).

One house-way edit to the author's `.rxt`: its `description`/`oracle` HEAD lines are `#` comments, because both
words are guarded by tests/rxtsource's keyword census. As a result C3 cross-checks the file with python `re`: 719
PASS, 56 `# pcre2-only` skipped.

## Compare and pins

The compare is `l1ffix_evidence/compare.sh`, frozen build `f8e38102b`; code is unchanged after it. Outputs:
`compare.txt`, `explain.txt`, `observed.tsv`.

- **Population:** 5932 texts (7613 rows); 413 byte movers, 9 utf8-only; model movers 93, 89 agreeing.
- **Route facts:** PIN-LOST 0, PIN-GAIN 48, PIN-MOVED 0, LANDMARK-LOST 0, LANDMARK-LOOSER 0, LANDMARK-GAIN 26,
  LANDMARK-TIGHTER 4.
- **Explain, 412 rows:** leaf-dead 192, rep-copy 49, spelling 48, pin-substretch 48, route-row 48, look-item 20,
  utf8-only 3, offset-looser 2, dead-both 1, d27-limit 1 (B14k rep-wall). **0 UNEXPLAINED.**
- **The 3 DIFFER rows:**
  - `[ac][ac](?<=ac(?=cc))cc` and `ab[xy][xy](?=(?<=xx)y)[xy]` are EMITTED-1's family: the same set, with a looser,
    sound offset.
  - `(?=xy)(?=xz)\w\w` is dead in both; its run value differs only by the guards' meet order (F5).
- **Pins re-measured by their checks:**
  - **rxtsource census:** 341/7072/98624 → 342/7224/99815. 58 of the blocks are l1feat's spanarms/presence_deny
    rows, landed unpinned.
  - **C3 counts:** PASS +1129, pcre2-only +56, no-python-expression +6.
  - **startset vm manifests:** +30 auto, +147 forced. One forced row, `\w*(?=a)\w`, is no longer a mover: L1 gives
    it a required `a`, so the VM takes a req-byte prefilter (LANDMARK-GAIN).

## Validation

Run here, all green:

- `make strict`.
- `tests/codegen/run_facts_checks.sh`: [facts-look] 33 cells, [facts-arm], [facts-rep].
- `tests/rxtsource/run_rxtsource_tests.sh`: INV-COMPAT over 342/7224/99815.
- `make test-startset`: vm-movers auto/forced and dfa-movers 0 off-diagonal.
- `make test-memfn-manifest test-lookaround`, including `[d27-l1-listing]` 88 rows / 29 named limits.
- `m6read_check_sab_anchors.py`: 1329 rows, all anchors resolve.
- `make test-spec-history`, `make test-doc-lint`, plan lint 0.
- Harness on d27_l1 + spanarms: 1247 passed, 0 failed (before W-L2b/W-L6b); the new blocks are oracle-written.

Queued via `scripts/boxqueue batch` (owner l1ffix, batch `b202611191530161591938`), each waiting for the one before
it to go green; worst-case caps total about 5.8 h from 15:30, so all of it finishes before the 00:30 limit:

- `200-l1ffix-b202611191530161591938.ident`: identity, l1ftri's fixed shape; `ident_check.py` against
  `l1ffix_evidence/observed.tsv` is the verdict, never emit_sweep's rc.
- `201-l1ffix-b202611191530161591938.mechA`: S3365-S3383 (S3384 does not exist).
- `202-l1ffix-b202611191530161591938.mechB`: S1925-S1929, S1653, S1887, S1907, S465, S474, S1930, S280, S1915-S1917,
  S1921, S1922, S899.
- `203-l1ffix-b202611191530161591938.axes`: `AXES="--harness=restore=look --harness=restore=zero"`.
- `204-l1ffix-b202611191530161591938.test`: make test (PC-3 included) via perfrun.

The tail can reach Frank's 20:00 evening hold; the manager may want to hold it (`boxqueue`).

## STATE AT HANDOFF

- Branch `lane/l1ffix` committed; nothing uncommitted of the lane's.
- Rulings file `l1ffix_rulings.md`: empty at every checkpoint. Last ruling: none.
- OWED: l1ffix-b202611191530161591938.ident l1ffix-b202611191530161591938.mechA l1ffix-b202611191530161591938.mechB l1ffix-b202611191530161591938.axes l1ffix-b202611191530161591938.test (queue keys; the job files carry prefixes 200-204)
- For the manager:
  - File the D168 addendum (span_arms §12 rev 3 text, as fixed per TABLE-3).
  - Note the 48 non-lookaround pin gains (B's general rule; a performance mover the census did not predict).
  - The deliver file's `owed:` names the five queued keys (it read `none`; the brief asks the keys be named OWED).
