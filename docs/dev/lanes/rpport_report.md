# rpport report: [REQ-PAST-LAST] ported onto main's K38-2 run API (lane rpport, opus, 2026-11-13)

Branch `lane/rpport` from main a07f76d6c. Brief: re-implement lane/rpfix's
[REQ-PAST-LAST] (tip 5dd83294d + rpland's report commit) on main after
K38-2 (abi 104), not a textual merge. No rulings file was named.

## STATE AT HANDOFF

DONE (code, spec, pins); local validation below; cloud OWED (manager).

The STOP RULE did not fire. Every reqpast decision has a direct spelling on
K38-2's API, with K38-2's semantics unchanged:

- reqpast already read the WHOLE run (`pcrec_fact_req_whole_run`,
  `whole_maxoff`) in every predicate. K38-2's change to these sites was
  limited to the `run` local of `emit_req_handoff_rest` (`req_run(cx)->len`
  became `req_whole_run(cx)->whole_len`) and the [K82] comment's wording
  (`whole || run ? "whole run" : "landmark byte"`). The port keeps main's
  text on the bounded branch, so bounded artifacts move only in the abi
  digits.
- Candidate semantics (K38-2: the site returns the LEAST CANDIDATE, which
  holds the stretch the kit verifies) are sound for the unbounded stop.
  A miss means no candidate, so no occurrence: NOMATCH is still exact. The
  row keeps `req_parts_in_whole`, which on main requires the run reply's
  verified extent to be the whole run (`ver_lo == 0 && ver_len ==
  whole_len`). So on this row a candidate IS an occurrence, and the
  linearity argument stands as written. The spec text says so in one clause
  (`match_api.md` §6.3.7¶11, `tuning.md` §2.41¶8c).
- The kit side: `presence.c`'s fifth port reads `head_max` as
  `k = max(head_max, 0)` (K38-2), and `k * h` with k = 2^40 and h <= 10^6
  cannot overflow (< 2^60). The TH-5 interim pin is kept as rpfix left it:
  `tests/memfn/c10_presence.tsv` `(a+)+zq` REQUIRED 1099511627776, with its
  comment (R-41 replaces it in S2).

Method: `git merge --squash lane/rpfix` in the worktree. The 12 conflicted
files were each resolved by hand on main's vocabulary (list under CHANGES).
The auto-merged hunks were read against main's API: `req_handoff_vm_run`,
the unbounded predicate, the stamp, the row, and the test files. None reads
a retired name. reqpast's lane reports and review record travel with it.

Validation (local, PCREC_BOXLOCK=0, nice 19, -j2, on da027915e unless named):

- `make strict`: GREEN.
- Sections `make test-codegen test-registry test-rxtsource test-memfn-deleg
  test-startset test-compound test-recursion-identity`: SEE THE VERDICT LINE
  BELOW (log `$PCREC_TMPDIR/scratch/rpport/sections.log`).
- `REACH_ONLY=1 bash tests/mech/run_sabotage_matrix.sh S463 S470 S471 S3074
  S3075 S3076 S3077`: `mech-reach-only: DONE rc=0 rows=7 reached=7
  unreached=0`.
- `python3 -I scripts/m6read_check_sab_anchors.py`: 1255 sabotages, 1301
  anchor sites, all anchors resolve (0 stale).
- Smoke (`--engine=vm`): `a+xyz`, `[^@ ]+@x`, `(a|aa|b)+cxyz`, `b*xx(?=q)`
  and `(a+)+zq` stamp `"unbounded"` with `handoff_position = search_from;`
  and the kept re-ask; `(?m)^x{2,5}(?i:cat)` still stamps `"3"`.
- `scripts/emit_sweep.py --ref a07f76d6c` (log
  `$PCREC_TMPDIR/scratch/rpport/sweep.log`): SEE BELOW.

## CHANGES

One port commit (76fea82d8) and two pin commits:

- `src/gen/emit_dfa.c`: abi 105. `emit_req_handoff_rest` takes reqpast's
  unbounded branch (no subtraction, `handoff_position = posvar`, the
  [REQ-PAST-LAST] comment) over main's bounded branch (K38-2's `run` and
  comment wording; the `round` buffer built only there, EMIT-4).
  `emit_req_landmark_move`, `pcrec_emit_req_attempt_reentry`,
  `req_handoff_vm_run`, `req_handoff_entry_applies`,
  `req_handoff_unbounded_applies`, the `"unbounded"` stamp and the
  `handoff-attempts-unbounded` row (req-use 4; `scan-from-startpos` 5) are
  as on rpfix. Public deny: `-fno-req-handoff` (R1, no new bit).
  `src/core/compile.c`, `src/core/internal.h`: comment lines.
- Spec (D80): `match_api.md` abi 105 at the four sites. §6.3.7¶11 keeps
  main's LEAST CANDIDATE text and gains the `"unbounded"` sentence in
  candidate words. §3.1¶15a is as on rpfix. `facts_listing.md` §4.1.2¶8
  (K38-2's one-listing text plus reqpast's "occurs at or after the attempt
  start whatever K is" sentence) and ¶8b (¶8c cited; `"unbounded"`).
  `tuning.md` §2.41¶8b is main's text plus the "can be slower" sentence;
  ¶8c cites `req_whole_run` only (`req_run` is retired) and says "candidate".
  `limits.md` is as on rpfix.
- `docs/dev/history/abi_changelog.md`: the 105 entry over K38-2's 104 entry
  (104 -> 105; 104 is now "was").
- Pins: `run_codegen_tests.sh` ABI_EXPECT 105 plus a 104->105 line in its
  history message. `run_recursion_identity.sh` FILEPIN and ABASEPIN are
  self-pinned to 76fea82d8 (the lane's last src commit; the rpfix self-pin
  7ddf68c71 never landed), and the manager re-pins them to the landing merge.
  S693: BEFORE 105, AFTER 104. S463 is re-anchored on K38-2's `whole_len`
  context line, with the same rpfix2 bounded-only plant. rxtsource census is
  main's plus rpfix's handoff_vm.rxt deltas: 7041/98459, C3 PASS 23180,
  VERIFIABLE 25593 (the check printed 336/7041/98459). The registry axes
  count is 248 (main still at 245, rpfix's +3).
- `plan.md`: one [REQ-PAST-LAST] row (rpfix's started row in Active, status
  re-dated for the port) carrying main's three 2026-11-12 NOTEs (the queued
  dense-hit remedy, the no-loss condition, blocked look-ahead). The
  not-started duplicate was removed.
- The lanes history index takes both sides' lines, plus this one.

## OWED

- For the manager (not run here, per brief): cloud test + axes + mechrows on
  lane/rpport.
- The identity-gate landing re-pin (FILEPIN/ABASEPIN 76fea82d8 -> the
  landing merge).
- reqpast's timings in `tuning.md` §2.41¶8c (1.38/0.81 ms, 1.56/0.71 ms,
  0.009/1.47 ms) were measured on the pre-K38-2 base. K38-2 changed the
  pre-check's run part, so they are not re-measured here. They are a
  re-measure candidate if the dense-hit remedy row runs.
