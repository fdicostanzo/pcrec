# [RUN-POS-SET] stage 3 + R-38 Part D: readiness memo (set S2)

**Status: READINESS MEMO, no build go** (lane s2prep, opus, 2026-11-12; base
main `a1d7743bf`, abi 103; kit branch read: `lane/memfn-k382` @ `f95739f5f`,
K38-2, abi 104, `MF_SITE_ABI` 27, `MF_CLASS_V` 9, NOT landed at this base).
Design of record: `docs/design/alt_normal_form.md` rev 3, §5 stage 3, §4.2-§4.4,
§11, §13. Plan row [RUN-POS-SET]; kit request `memfn/docs/requests.md` R-38
Part D. Evidence: single compiles at main (`build/pcrec` in this worktree),
listed in §3; everything about K38-2 is READ from the branch, not run (no second
build in Frank's evening hold). Cites into K38-2 are `lane/memfn-k382:FILE:LINE`.

## 0. Goals of this memo

| # | goal | who benefits | measurable form |
|---|---|---|---|
| R1 | the stage-3 build lane can start the minute K38-2 lands | manager, Frank | §4's brief has every field filled; every design cite checked at `a1d7743bf` and against K38-2 (§1) |
| R2 | no surprise at the seam | the kit | §2 names every pcrec reader and every kit site that assumes "one member or a two-member cube" (grep, file:line) |
| R3 | the owner sees the scope before the build | Frank | §6 lists every question with a leaning |

Non-goals: any code; the kit's method (D157); re-deciding ruled points.

## 1. Stage 3, unit by unit: do the cites hold, what K38-2 changes, verdict

The rulings that moved since rev 3 was written, and which this memo applies:
- **Member bound SUPERSEDED** (plan row note, Frank 2026-11-09): no member cap;
  "the run stops only where a position carries no information (or the walk's
  own reach)"; what to scan and how far to verify is the kit's. So §4.4's
  "keeps 2 as its starting value", §13 q2 and every "at bound 2/3" figure are
  history. With `info(S) = 8 - ceil(log2 |S|)` (§4.4, kept) "no information"
  is `|S| > 128`.
- **§13 q5 REPLACED by D187 addendum 1** (owner 2026-11-06): a covering cube is
  a READER's private spelling, rebuilt from the set, never a second shape, lossy
  only where an exact finish follows. §4.2's "(r4: FIX-5, FIX-8) OPEN owner
  question" and §13 q5's A/B are closed by it.
- **K38-2 moves the pre-check to the kit** (`MF_SITE_ABI` 27): the run crosses
  the seam already in SET form, `mf_wspan.set[j][32]` per position
  (`lane/memfn-k382:memfn/include/memfn.h:650`), uncut (the `PCREC_MAX_REQ_RUN_EMIT`
  window retired, `limits.def` row deleted), and the kit's run decision
  (`mf_class.run`: `has_scan`, `scan`, `ver_lo`, `ver_len`, `memfn.h:1214-1219`)
  is read at every pcrec reader. pcrec's own `req_run` row, `pcrec_req_window`,
  `req_run_tests`, `req_part_window` and `req_run_member` are gone; `req_byte`
  stays pcrec's own pick (`lane/memfn-k382:src/facts/req.c:1210-1220`).

| unit (alt_normal_form §5 stage 3) | cites at `a1d7743bf` | what K38-2 changes underneath | verdict |
|---|---|---|---|
| U-a CHANGE: `RbRun` positions become sets; cube derived where a reader wants one; `info` per reader; the member bound | HOLD: `RbRun` (bytes/mask) `src/facts/facts_derive.h:103-115`; one constructor `rn_put` `src/facts/req.c:304`; class gate `rb_class_into` `req.c:760-786` (`rn_members(k) > w->pos_set` at :770); `pcrec_cube_of` `src/core/cpset.c:411`; floor `PCREC_MIN_REQ_RUN_BITS` `limits.def:410`, cap `limits.def:411`; walk parameter `src/facts/facts.c:231` | the seam side is DONE: the run span takes any non-empty set per position (`lane/memfn-k382:memfn/src/compose.c:575-583` refuses only the empty set); pcrec still fills it from cubes (`pcrec_memfn_wpos_cube`, `lane/memfn-k382:src/gen/emit_dfa.c:1428`) and `pcrec_memfn_wpos_bits` already exists (`src/gen/memfn_sites.c:559` on the branch). The "cube reader" population of §4.2/§4.4 shrank: pcrec emits no run compare of its own any more | READY WITH TEXT FIXES: (1) delete the member bound (cap superseded; stop at `info = 0`); (2) replace §4.2's hull-or-decline paragraph and §13 q5 by D187 add. 1; (3) §4.4 "per reader" now applies to pcrec's remaining in-process readers (§2.1) and to the kit's own (its business), not to a pcrec pre-check; (4) state the representation: positions as arena-interned 32-byte sets referenced by pointer (as stage 2p's `rb_pos_set` already does, `req.c:746`), NOT `unsigned char[32][32]` by value: `RbRuns` is passed by value through `rr_cat`/`rr_alt`/`rn_better` and recursion depth follows group nesting, so a by-value 1 KB position array per run multiplies frame size (coding.md §2.4, DD-10) |
| U-b deny lever: bit 44 `-fno-req-run-fold` re-specified "every multi-member position, cube or set" | HOLD: `tuning.md` §2.39¶1, ¶4 | none (K38-2 rewrote §2.28¶5/¶7, not §2.39) | READY WITH TEXT FIX: with no cap, the lever's two values are "positions up to `info >= 1`" and "single byte" (today: 2 vs 1). Retire `PCREC_MAX_REQ_RUN_POS_SET` (its RULED reason is superseded) and its `tests/registry/limits_check.sh:163` reader, or keep it as the derived constant 128 with a new reason; leaning: retire |
| U-c `rr_alt`'s common head/tail over sets IS the mixed-letter affix (3m folded in) | HOLD: `rn_hull_mask` `req.c:460`, `rn_common_head` :471, `rn_common_tail` :484, `rr_alt` :586 | none | READY WITH TEXT FIX: over sets the "hull" is the per-position UNION (the smallest SET holding both), not a cube hull; `rn_hull_mask` deletes. And a DEPENDENCY the rev 3 text hides: `rr_alt` still sets `all = false` (:595) because stage 2a's ALT half never ran (census-first). Without it a run cannot pass THROUGH a non-product alternation, so alt_normal_form §5's "ci-greek-run 0 -> 6" needs 2a rule (1) as well as stage 3 (see §3 and §6 q1) |
| U-d predicted movers | figures at bound 2 (1403) and 3 (1416) | n/a | NOT READY AS STATED: the counts assume a cap of 2 or 3 and stage 2a, and count only the 1454 utf8 simple fold classes. The re-ruled stop moves EVERY class of 3..128 members in EVERY encoding (byte `\d{3}-\d{4}`, `[0-9a-f]{8}`, `[a-z]{8}`, `\w+@...`) and the superset head/tail of unrelated alternations (`cat|dog` -> `{c,d}{a,o}{t,g}`, 21 bits, a run where none existed). The build's first step is a census over corpus + bench at the stage-3 rule (with and without 2a rule (1)), counted by an independent model (§7 q2) |
| U-e gates: every §4.2 membership reader moves to sets (one detector); R2 listing; per-regime evidence incl. real Cyrillic/Greek text | §4.2's reader table: STALE at K38-2 (5 of its rows name functions K38-2 deleted) | the run's emitted tests are the kit's | READY WITH TEXT FIXES: the reader list is §2.1 below (re-grepped on the K38-2 tip); the regimes must ADD the byte regimes (bench byte suite + a random-like regime, D186 add. 2), because U-d's movers are not utf8-only |
| U-f sabotage witnesses S-e, S-e2, S-f | S-e2's today value HOLDS (measured `req_whole_run 58595ac5/dfdfdfff`); S-f's today run `58595a/dfdfdf` HOLDS | the position is tested by the KIT's run part, inside the extent the kit replies; REACH per position now depends on the kit's `ver_lo/ver_len` | READY WITH TEXT FIXES: S-e2 and S-f stand without a bound (S-f no longer "at either bound": it is live); S-e's "correct run" `[xX][yY][zZ]{ce,cf}{90,92,b2}[wW]` needs 2a rule (1) (β is a non-product ALT); without 2a its run ends at β's head, `[xX][yY][zZ]{ce,cf}{90,92,b2}` (34 bits by `info(S)`), still a witness of a dropped member. Each witness's REACH is checked against the kit's reply after Part D |
| U-g existing mech rows | `tests/mech/sabotages/S451_req_hull_keeps_left.sh` exists | K38-2 added/moved run rows | READY: the anchor list is S451 (hull), S453 (`req_pick_takes_pair`), S3048 (`k66_run_mask_dropped`), S3042 (`req_run_at_is_pcrec_index`), S267/S268 (run memcmp / alt overclaim): every row reading `whole_mask` or `rn_hull_mask` on the K38-2 tip re-anchors on the set constructor, REACH re-run |
| rides with: [POS-ONE-DETECTOR] (three meanings of a run position across the seam) | row cites hold (`pcrec_memfn_wpos_cube`, `pcrec_cube_of`, findings.c `cube_mass` `lane/memfn-k382:src/core/findings.c:631`) | K38-2 removed the kit-side cube copy for the run (sets); pcrec's `findings.c` still prices the pick by `cube_mass` (`t | b` double count) | READY: stage 3 closes the pcrec half (pick mass over the set), the kit half is gone |
| R-38 Part D (the kit) | `requests.md` R-38 Part D holds; its example's "64-member continuation-byte set" is the cube HULL; the SET has 25 members (`80-89` and `b1-bf`, measured kset `[2],[25]`) | see §2.2: three kit sites assume one member or a two-member cube | NOT READY: the kit needs a BUILD, not only an answer; text fix to the example |

## 2. The exact seam change

### 2.1 pcrec side: no new field; every reader of the run's positions

The fields that carry a wide position's byte set ALREADY EXIST at K38-2:
`mf_wspan.set[MF_WSPAN_POS][32]` (`MF_WSPAN_POS` = `MF_MAX_SPAN_POS`, the
stored run's bound `PCREC_MAX_REQ_RUN_SCAN` 32, asserted at
`lane/memfn-k382:src/gen/emit_dfa.c:1403`), filled per position by a
`pcrec_memfn_wpos_*` helper. Size limits: 32 positions per run (unchanged);
any 1..256-member set per position at the seam (`compose.c:575-583`); pcrec's
own stop at `info(S) = 0` (`|S| > 128`).

pcrec's internal value changes: `ReqRun.whole`/`whole_mask`
(`lane/memfn-k382:src/facts/facts.h:59-75`) and `RbRun.bytes`/`mask` become
position sets. Every reader, found by
`git grep -n -E 'whole_mask|->whole\[|PCREC_MAX_REQ_RUN_POS_SET' lane/memfn-k382 -- src tests`
(function names from `git grep -p`):

| reader (K38-2 tip) | reads | stage-3 form |
|---|---|---|
| `src/facts/req.c` `rn_*`, `rr_alt`, `rb_class_into` (:460-500, :586, :760) | the cube domain, `pos_set` | position sets; union at ALT; class gate `info(S) >= 1` |
| `src/facts/facts.c` `pf_derive_req_walk` (:225, bits at :242) | `popcount(mask)` vs the floor | `Σ info(S)` |
| `src/facts/facts.c` `pcrec_fact_render`, `pcrec_fact_stamp_req_run` (:755, :955) | hex + `/mask` | the new spelling (§2.3) |
| `src/facts/req.c` `pcrec_req_pick` (:1210-1220) | exact position (`mask == 0xFF`) | one-member set (unchanged meaning) |
| `src/core/findings.c` `pcrec_find_run_scan_index` (:745) + `cube_mass` (:631) | cube mass | set mass ([POS-ONE-DETECTOR]) |
| `src/facts/kset.c` `pcrec_run_pin` (:301-326) | exact positions | one-member sets (unchanged) |
| `src/gen/emit_dfa.c` `req_note_run` (:1150) | renders bytes/mask in the comment | the new spelling |
| `src/gen/emit_dfa.c` `req_pres_spans` (:1405, :1428) | `wpos_cube` | `wpos_bits` |
| `src/gen/emit_dfa.c` `pf_window_of` + `walk_proves` (:6784-6849) | R's stretch grown over walk-proven CUBES; `wpos_cube` | subset-of-set test; `wpos_bits` (see §2.2 K-2) |
| `src/gen/emit_dfa.c` `ofs_test_pos_in_cube` (:7481) | members within a cube | members within the set |
| `src/gen/emit_dfa.c` `req_whole_holds_byte` (:8848) | exact positions | one-member sets |
| `src/gen/emit_dfa.c` `req_landmark_hit_ppm` (:8996, set built at :9012) | set from cube | the set |
| `src/gen/emit_dfa.c` `req_set_leads_own` (:11109-11121) | scan index's cand/care | set |
| `src/gen/emit_dfa.c` `req_rest_own_sig` (:11133-11143) | exact positions | one-member sets |
| `src/gen/emit_dfa.c` `req_run_in_cover` (:16033-16042) | cube membership | set membership |
| tests: S451, S453, S3042, S3048 (mech); `tests/registry/limits_check.sh:163` | anchors / the limit row | re-anchor / retire |

### 2.2 kit side: where K38-2's kit assumes one member or a two-member cube

Read on the branch, NOT run (no build with wide positions exists). Facts about
the kit's text at that tip, for the kit to confirm; how to change them is the
kit's (D157).

- **K-1 the derived run part.** `derive_run_part` copies the verified extent's
  sets into a window statement (`lane/memfn-k382:memfn/src/window.c:2543-2569`);
  the window family translates it, grouping only stretch positions
  (`in_stretch` = one member or a two-member cube, :353-357, `find_groups`
  :1719) into ONE `MF_T_RUN` term `(run, mask)` (`run_bytes` :1459-1474,
  `build_runs` :1743-1767); `wf_parts_prepare` then REFUSES the compile unless
  the result is one RUN term at `ver_lo` with the scan inside
  (:2614-2620). `kit_run_decide`'s `KIT_RUN_WHOLE` row verifies the whole run
  (`presence.c:217-252`, `ver_len = n`). INFERRED consequence: a run stated
  with one non-cube position inside the extent does not render (a loud
  refusal, not a miscompile).
- **K-2 the window site's R.** R is "identified by its SHAPE alone: two or
  more positions, each one member or a cube" (`window.c:271-281`, `run_shaped`;
  the F-8 ruling). pcrec states R in the PARKED/RESEED alternatives from the
  same run (`emit_dfa.c:6813-6849`). INFERRED: a wide position inside R's
  stretch makes the span NOT R-shaped, silently (no refusal; the plan just
  loses R's rows). This is a seam MEANING question, so it is an
  `MF_SITE_ABI` question.
- **K-3 the run compare.** `runcmp.c`'s rows read a RUN term as `(T, K)`
  (`rc_of` :148-150, the `words` row's masked compare, `tuning.md` §2.38);
  `kit_run_set` rebuilds a set from `(T, K)` (`presence.c:85-90`). A set that
  is not one cube has no `(T, K)` spelling.
- Not affected: the run span's input check (any non-empty set), `kit_mass` (a
  set's mass), `kit_run_member` (reads positions as sets through `kit_wspan_at`).

### 2.3 The abi event and the spec hunks

- **pcrec abi event**: yes (emitted bytes move: `<PREFIX>_REQ_RUN`, the run
  note, the kit's rendered run part and every pick that moves). The NEXT
  number at landing (K38-2 takes 104). D94 ritual by grep.
- **`MF_SITE_ABI` event**: the kit's call; K-2 suggests one (R's recognition
  changes meaning). One landing for both (§6 q5).
- **Spec hunks** (found by `git grep -E 'two-member|PCREC_MAX_REQ_RUN_POS_SET|popcount\(K\)|req-run-fold' -- docs/spec`
  on the K38-2 tip): `tuning.md` §2.28¶4 (a position is any set; info
  `8 - ceil(log2|S|)`; a class with no information breaks contiguity),
  §2.28¶5 (a set counts all its members in the mass), §2.28¶7 (the stamp
  spelling), §2.30¶4 (the pin: unchanged meaning, "exact" = one member),
  §2.39¶1-¶4 (bit 44 re-specified), §2.38's `words` row only if the kit's
  Part D changes it (the kit's hunk); `match_api.md` §6.3.7¶6 examples and
  the "two-member cube" sentence of §6.3.7 just before ¶7; `facts_listing.md` §4.1.2¶1 (the run's spelling);
  `limits.md` §3.4a¶4 (`bits` = information); `limits.def`'s
  `PCREC_MIN_REQ_RUN_BITS` text and the retired `PCREC_MAX_REQ_RUN_POS_SET`
  (`--list-limits` reader).
- **The spelling** (a caller-observable string; manager's call, §6 q4):
  keep today's `hex@idx` and `hex@idx/mask` exactly where every position is
  one member or a two-member cube (no churn on today's artifacts), and spell a
  wider position as a bracketed hex class at its place, e.g. `[α-ω]foo`
  -> `[cecf][80-89b1-bf]666f6f@4`; the `/mask` suffix is then not used. The
  listing (`req_whole_run`) uses the same spelling without `@`.

## 3. Witnesses (single compiles at main `a1d7743bf`, `--emit-facts`)

"today" is MEASURED (`$PCREC_TMPDIR/scratch/s2prep/wit.out`). "stage 3" is
INFERRED by hand from `req.c`'s rules with the cap removed, info by
`8 - ceil(log2|S|)`; "+2a" adds alt_normal_form §6's `rr_alt` row (1).
At K38-2 the today column's run is the same (the walk is unchanged); only the
`RX_REQ_RUN` stamp names the whole run instead of an 8-position window
(`(?i)Ελληνικά` `95ce9bce9bce97ce@7/...` at main).

| enc | pattern | today `req_whole_run` | stage 3 (no 2a) | stage 3 + 2a |
|---|---|---|---|---|
| utf8 | `[α-ω]foo` (Part D's driver) | `666f6f` (24 bits; kset `[2],[25],f,o,o`) | `{ce,cf}{80-89,b1-bf}foo`, 5 pos, 34 bits | same |
| utf8 | `abc[α-ω]defg` (Part C's example) | `defg` (32) | `{ce,cf}{25}defg` 42 bits (the ALT stops the head at `abc{ce,cf}{25}`, 34) | `abc{ce,cf}{25}defg`, 9 pos, 66 |
| utf8 | `(?i)αβγ` (ci-greek-run) | `ce91ce/ffdffe` = `ce{91,b1}{ce,cf}`, 22 | `ce{91,b1}{ce,cf}{90,92,b2}`, 4 pos, 28 | 6 pos, 43 |
| utf8 | `(?i)xyzłw` (S-e2) | `58595ac5/dfdfdfff`, 29 | `[xX][yY][zZ] c5 {81,82} [wW]`, 43 | same |
| utf8 | `(?i)xyzk` (S-f) | `58595a/dfdfdf`, 21 | `[xX][yY][zZ]{4b,6b,e2}`, 27 | same |
| utf8 | `(?i)xyzβw` (S-e) | `58595ace/dfdfdffe`, 29 | `...{ce,cf}{90,92,b2}`, 34 | `+[wW]`, 41 |
| utf8 | `(?i)москва` (ci-moskva) | none (kset `208,[2],[2],[3],...`) | `d0{9c,bc}{d0,e1}` 22 (о is mixed width; its head) | longer (с is an equal-width ALT): about `{9e,be,82}{d0,d1}{81,a1}d0{9a,ba}{d0,e1}`, 42 |
| utf8 | `(?i)straße` | `545241/dfdfdf`, 21 | +1 affix each side of the mixed letters (altthink e) | same |
| utf8 | `[\x{400}-\x{4FF}]{4,16}` (qnt-class-run) | none (kset `[4],[64]`x4) | 8 pos of `{d0-d3}{80-bf}`, 4x(6+2) = 32 | same |
| byte | `\d{3}-\d{4}` | none (`req_byte` 45) | 8 pos, 36 bits | same |
| byte | `[0-9a-f]{8}-[0-9a-f]{4}` | none | 13 pos, 56 | same |
| byte | `[a-z]{8}` | none, no pre-check (`RX_REQ_WHY "none"`) | 8 pos of 26 members, 24 bits: a NEW site | same |
| byte | `cat\|dog` | none, `RX_REQ_WHY "none"` | `{c,d}{a,o}{t,g}`, 21: a NEW site, a superset run | same |
| byte | `GET /[a-z]+ HTTP` | `2048545450` (` HTTP`, 40) | `[a-z] HTTP` or `GET /[a-z]`, 43 (a stamp mover, scan likely unchanged) | same |
| byte | `\w+@example\.com` | `@example.com` (96) | `[\w]@example.com`, 98 (a 63-member position joins: a churn mover worth 2 bits) | same |

## 4. Draft BUILD BRIEF (stage 3 + 2a rule (1), pcrec side)

    LANE s2build (opus): [RUN-POS-SET] stage 3, set positions in the run
    Read docs/dev/lanes/BOILERPLATE.md FIRST and follow it.
    Scope: ONLY the pcrec and pcrec-bench repos (pcrec-bench read-only) plus
    $PCREC_TMPDIR (scratch under scratch/s2build/); never /tmp; memfn/ READ
    only (the kit's Part D is its own branch). Worktree:
    worktrees/s2build (branch lane/s2build, from main AFTER K38-2's merge).

    TASK: the necessary run's positions become byte SETS (D187), the walk
    stops only where a position carries no information (|S| > 128) or at
    its reach, an alternation's affix is the per-position union, and
    [ALT rule (1) if ruled] an alternation whose branches are all `all` and
    of equal untruncated width is `all` with the union as its run. Every
    reader in docs/design/run_pos_set_stage3_readiness.md §2.1 moves to
    sets in the same change (one detector, [POS-ONE-DETECTOR]'s pcrec
    half). Built against the kit's Part D branch (named in the rulings
    file), landed together, one abi event. Staged: (0) census FIRST at the
    stage-3 rule, with and without ALT rule (1), over corpus + bench, by an
    independent model (no pcrec code), listing new pre-check sites and the
    R2 picks (alt_normal_form §4.4) — a measurement, no gate; (1) build;
    (2) spec hunks (memo §2.3); (3) gates.  TIER: opus.
    INPUTS: docs/design/alt_normal_form.md rev 3 §3.5, §4.2-§4.5, §5 stage 3,
    §6, §11 (AS AMENDED by the readiness memo §1); the readiness memo;
    D186, D187 (+ add. 1), D191; span_runs_sheet.md (the run's seam form);
    docs/dev/lanes/s2prep_report.md.

    RULINGS ALREADY MADE: Frank's go for stage 3 + Part D, 2026-11-11 (set
    S2, "starting when K38-2 lands"); the member cap superseded (Frank
    2026-11-09, plan row note): "pcrec states every position's set ...; the
    run stops only where a position carries no information (or the walk's
    own reach); what to scan and how far to verify is the kit's priced
    choice"; no per-position exact mark (Part C's ranges, owner
    2026-11-09); D187 add. 1 (a covering cube is a reader's private
    spelling, never a second shape); D157 facts not methods; flag follows
    caller effect (bit 44 re-specified, no new public bit, §11);
    [manager to add: the answers to the memo's §6 questions].

    RULINGS FILE: worktrees/s2build/docs/dev/lanes/s2build_rulings.md.
    IDS YOU MAY USE: abi = the next number at landing (after K38-2's 104);
    sabotage ids from worktrees/.mgr/sabotage_ids.txt [range]; no D/K/R ids.
    BUILD GO: [the manager quotes Frank's 2026-11-11 go verbatim here].
    STOP RULE: if the census (step 0) shows a mover class the memo did not
    name, or the kit's Part D branch refuses a stated run, stop and report.
    PREMISE TEST: on main after K38-2, `build/pcrec -e utf8 --emit-facts
    -p rx --pattern '[α-ω]foo'` lists `req_whole_run 666f6f` and kset
    `[2],[25],102,111,111`; after the change, 5 positions, 34 bits.
    OWED RUNS: make test, make test-axes, mech (REACH_ONLY first, then
    full), identity jobs with the declared movers, the census job; per-regime
    timing (bench utf8 ci-*/qnt-*/lit-*, real Cyrillic/Greek text, the bench
    byte suite, a random-like regime) through main's Frank-cleared window.
    DELIVER: report=docs/dev/lanes/s2build_report.md; sections: STATE AT
    HANDOFF; CENSUS; CHANGE; GATES; OWED; nonempty: all; commit: yes.
    REPLY: under 2k chars, SendMessage to main, then END.

## 5. Draft kit request text: R-38 Part D, scheduled (facts only, D157)

    ### R-38 Part D, SCHEDULED (2026-11-?, pcrec manager; set S2; GO Frank 2026-11-11)
    - FACT. pcrec's necessary run (the run presence span, and R inside the
      window site's PARKED/RESEED statements) will carry positions of ANY
      byte set of 1 to 128 members (today: one member or a two-member
      cube). A position with more than 128 members ends the run on pcrec's
      side. Correction to the filed example: utf8 `[α-ω]foo` states
      `{CE,CF}`, then the 25-member set `{80-89, B1-BF}` (its cube hull
      has 64 members), then `foo`.
    - FACT. A position may be a SUPERSET of what the matches hold there,
      jointly with its neighbours: every successful attempt's byte at
      offset j lies in set j, but not every combination of members occurs
      (`cat|dog` states `{c,d}{a,o}{t,g}`). No per-position exactness mark
      (Part C's ranges, when scheduled).
    - FACT. The new runs reach patterns in every encoding, not only utf8
      folds: `\d{3}-\d{4}` (eight positions, ten-member digit sets, byte
      encoding), `[0-9a-f]{8}-[0-9a-f]{4}`, `[a-z]{8}` (a run where none
      was stated before), `\w+@example\.com` (a 63-member position joins).
      Witness list: docs/design/run_pos_set_stage3_readiness.md §3.
    - FACT. pcrec reads your run reply (`mf_class.run`) at every reader, as
      since K38-2, for every run it states; pcrec states such runs on every
      site where it states a run today and needs a reply (or your stated
      decline) for each; a refused site fails the compile.
    - Read on your K38-2 tip, for you to confirm (your text, not a method):
      the derived run part renders through one RUN term `(T, K)` and is
      refused otherwise (window.c `wf_parts_prepare`); R is recognized by
      its shape, one member or a cube per position (window.c `run_shaped`);
      runcmp reads `(T, K)`. Which of these move, and whether that is an
      `MF_SITE_ABI` event, is yours.
    - Deliver: a kit branch built on main after K38-2, for one landing with
      pcrec's stage 3 (one pcrec abi event). Say what pcrec must read from
      any new reply field.

## 6. Questions (each with a leaning)

1. **Stage 2a's alternation half rides with stage 3?** Without `rr_alt`'s row
   (1) (every branch `all`, equal width -> `all`, run = the union) a run cannot
   pass through a non-product alternation: ci-greek-run stays at 4 positions
   (not 6), ci-moskva at about 3 (not about 7), Part C's `abc[α-ω]defg` at 6
   (not 9). With sets the row is a few lines in the same function, and 2a's
   EMPTY half already landed with span_arms E1/E2 (D191). Leaning: yes, in the
   same lane, behind the harness-only lever §11 already assigns to 2a, its
   census in step 0; row (1b) stays out.
2. **Scope: every class, every encoding.** The superseded cap makes stage 3
   move byte-encoding patterns (digits, hex, `[a-z]`, `\w`) and superset heads
   of unrelated alternations, many more than the 1454 utf8 fold classes the
   design counted. Leaning: accept (it is the same sound fact, and Frank's
   ruling names no encoding), and widen the D186 evidence to the byte regimes
   and a random-like regime; the census counts movers per class kind.
3. **New pre-check sites from weak runs.** `[a-z]{8}` (24 bits) and `cat|dog`
   (21) clear the 16-bit floor (RULED, in information units) and gain a run,
   so possibly a pre-check where none ran before; on prose its candidate rate
   is high. Leaning: keep the floor; the census lists "new sites" as their own
   row; a D186 loss there narrows by a choice row (alt_normal_form §4.4 R3),
   not by a new constant.
4. **The stamp/listing spelling** (manager's call, answer-free): today's
   `hex@idx[/mask]` where every position is a cube, a bracketed hex class per
   wider position (§2.3). Leaning: as stated.
5. **One landing for stage 3 and Part D.** K-1 refuses a stated wide run, so
   pcrec cannot land first. Leaning: one landing, one pcrec abi event; the
   kit's `MF_SITE_ABI` move is the kit's.
6. **`PCREC_MAX_REQ_RUN_POS_SET`.** Its ruled reason is superseded. Leaning:
   retire the row (the stop is `info(S) = 0`, a property of the information
   measure, not a knob); bit 44's denied value stays 1.
7. **Order against span_arms L2/L3** (also `req.c`'s run, after R-38): L2/L3
   are set S4, after S2. Leaning: stage 3 first as planned; L2/L3's briefs
   re-grep §2.1 at their base.

## 7. Standing questions (docs/design/CLAUDE.md)

1. **Measurement regime: RELEVANT.** The numbers in §3 are compile-time facts
   of this box's compiler (gcc 15.2); bit counts are computed, not timed. The
   speed evidence is owed by the build per regime (utf8 bench strata, real
   Cyrillic/Greek text, the byte bench suite, a random-like regime); a regime
   can flip a run pick (R2) and, new here, can make a new weak-run site lose
   (§6 q3).
2. **Independent control: RELEVANT.** The census (step 0) uses a model that
   shares no code with `req.c` (python over the lowered pattern, or the stage
   2p piece description's independent model, K35: the population is corpus +
   bench, counted); the sabotage witnesses S-e/S-e2/S-f each fail in the
   sabotaged build (§1 U-f) and are REACH-checked against the KIT's extent.
3. **What moves when data is regenerated: RELEVANT.** A UCD bump moves fold
   classes and so set positions (as alt_normal_form §7.3); a byte-rate prior
   change moves equal-information picks. Both are abi events by emitted bytes;
   no extra spec change.
