# s2prep — [RUN-POS-SET] stage 3 + R-38 Part D readiness (set S2)

Lane s2prep (opus), 2026-11-12, branch `lane/s2prep` from main `a1d7743bf`
(abi 103). Readiness and brief only: NO BUILD GO, no edit under `src/` or
`memfn/`. Memo of record: `docs/design/run_pos_set_stage3_readiness.md`.

## STATE AT HANDOFF

- Delivered: the memo (units and verdicts §1, the seam change §2, witnesses
  §3, the draft build brief §4, the draft kit request §5, questions §6,
  standing questions §7); its pointer in `docs/design/CLAUDE.md` (the file is at
  its 12,288-byte limit exactly; the `alt_normal_form.md` line was shortened to
  make room); this report and its lanes history index entry.
- Premise test HELD with a correction: `build/pcrec -e utf8 --emit-facts -p rx
  --pattern '[α-ω]foo'` at main lists `req_whole_run 666f6f`, `RX_REQ_RUN
  "666f6f@2"`, `kset_walk [2],[25],102,111,111`: the run starts at `foo`, cut at
  the continuation byte. The continuation SET has 25 members (`80-89`, `b1-bf`);
  "64-member" in R-38 Part D's example is its cube hull.
- Evidence: single compiles only (Frank's evening hold), 23 patterns, outputs
  `$PCREC_TMPDIR/scratch/s2prep/wit.out` (not committed; the memo's §3 table
  carries every value). K38-2 (`lane/memfn-k382` @ `f95739f5f`) was READ, not
  built or run; its effects are stated as read, with file:line on the branch.
- Rulings file `docs/dev/lanes/s2prep_rulings.md`: empty at every checkpoint
  (no entry applied).
- OWED: none (no runs; no build).

## FINDINGS

1. **The seam side of stage 3 is already done by K38-2; the kit side is
   not.** K38-2 states the run in SET form (`mf_wspan.set[j][32]`, uncut, up
   to 32 positions; the input check admits any non-empty set) and pcrec
   already has `pcrec_memfn_wpos_bits`. So stage 3 adds no seam FIELD. But
   three kit sites assume "one member or a two-member cube" (memo §2.2): the
   derived run part renders through one `(T, K)` RUN term and is refused
   otherwise (K-1, a loud refusal: pcrec cannot land wide positions first);
   the window site's R is recognized by its shape (K-2, a silent loss of R,
   a seam-meaning question); runcmp reads `(T, K)` (K-3). R-38 Part D needs a
   kit BUILD landing with stage 3, one pcrec abi event.
2. **Two rulings already replace design text.** The member cap is superseded
   (Frank 2026-11-09: stop only where a position carries no information,
   i.e. `|S| > 128` under `info(S) = 8 - ceil(log2|S|)`), and §13 q5 is
   replaced by D187 addendum 1. Every "at bound 2/3" figure in
   alt_normal_form rev 3 is history; text fixes per unit in memo §1.
3. **Stage 3 depends on stage 2a's alternation half, which never ran.**
   `rr_alt` still sets `all = false` (`src/facts/req.c:595`), so a run cannot
   pass through a non-product alternation (β, с, ι, `[α-ω]` in mid-pattern).
   ci-greek-run reaches 4 positions with stage 3 alone, 6 with 2a's row (1);
   ci-moskva about 3 vs about 7; `abc[α-ω]defg` 6 vs 9. 2a's EMPTY half
   already landed with span_arms E1/E2 (D191). Question 1.
4. **The mover population is far wider than the design counted.** With no
   cap every class of 3-128 members in every encoding joins runs: byte
   `\d{3}-\d{4}` (none -> 8 positions, 36 bits), `[0-9a-f]{8}-[0-9a-f]{4}`
   (13, 56), `\w+@example\.com` (+ a 63-member position, 2 bits), and
   alternation unions make runs where none existed (`cat|dog` ->
   `{c,d}{a,o}{t,g}`, 21 bits; `[a-z]{8}`, 24 bits: NEW sites). The design's
   predictions counted only the 1454 utf8 fold classes. The census becomes the
   build's step 0, and D186's evidence must add byte regimes. Questions 2-3.
5. **The design's reader table (§4.2) is stale at K38-2**: five named
   functions are gone (`pcrec_req_window`, `req_run_tests`, `req_part_window`,
   `req_run_member`, the window start). The re-grepped list on the K38-2 tip is
   memo §2.1 (15 readers + 4 mech rows + the limits registry check).
6. **Representation:** positions should be arena-interned set POINTERS
   (as stage 2p's `rb_pos_set` already does), not `[32][32]` arrays: `RbRuns`
   is passed by value through the walk and recursion follows group nesting
   (coding.md §2.4, DD-10).
7. **Caller-observable spelling moves**: `<PREFIX>_REQ_RUN` and
   `req_whole_run` cannot spell a non-cube position as `hex/mask`. Proposed:
   keep today's spelling wherever every position is a cube (no churn), a
   bracketed hex class per wider position (`[cecf][80-89b1-bf]666f6f@4`).
   Spec hunks listed in memo §2.3 (tuning §2.28¶4/¶5/¶7, §2.30¶4,
   §2.39¶1-¶4; match_api §6.3.7¶6; facts_listing §4.1.2¶1; limits §3.4a¶4;
   `limits.def` rows).
8. **Sabotage witnesses**: S-e2 (`(?i)xyzłw`) and S-f (`(?i)xyzk`) hold
   without a bound (today's values re-measured); S-e needs 2a's row (1) for its
   written run, and without it is still a witness on a shorter run. REACH now
   depends on the kit's verified extent.
9. **Unit verdicts** (memo §1): set positions, deny lever, affix rule, gates,
   witnesses, mech rows, [POS-ONE-DETECTOR]: READY WITH TEXT FIXES or READY;
   the predicted movers: NOT READY AS STATED (census first); R-38 Part D: NOT
   READY (needs a kit build).
10. **Cross-lane notes**: minw's draft R-40 (PRE `k = max(len(R), W -
    maxoff(R))`) cites `req_run_maxoff`, which K38-2 retired (use
    `req_landmark_maxoff`); stage 3 lengthens R and so raises that k. kclose
    (SEAM-2, R-13) touches nothing in the run. span_arms L2/L3 also rewrite
    `req.c`'s run after R-38 (set S4): their briefs re-grep memo §2.1.

Questions for the manager or Frank, each with a leaning: memo §6 (fold 2a's
row (1) into S2: yes; accept the every-encoding scope and widen the regimes:
yes; keep the 16-bit floor and list new weak-run sites, narrow by a choice row
on a loss: yes; the stamp spelling: as proposed; one landing with Part D: yes;
retire `PCREC_MAX_REQ_RUN_POS_SET`: yes; stage 3 before L2/L3: yes).
