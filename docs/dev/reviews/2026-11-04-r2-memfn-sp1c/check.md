# CHECK lens (check-adequacy) -- memfn-sp1c, SUBJECT 3ecb647c7

### findings, PROBED-AND-HELD
(sections below: Findings CHECK-1..5, then PROBED-AND-HELD)

Method: private export `check/tree` (git archive 3ecb647c7); kit objects rebuilt per plant
(`check/plant.sh`, driver = mass_check.c) or a pcrec relinked with one replaced kit member
(`check/cplant.sh`, emitted bytes compared SUBJECT-vs-plant with `check/cmp.sh`). ~60 gcc
compiles + ~170 pcrec compiles (under the 400 cap). No suites run.

## Findings

### CHECK-1 (design / test gap) translate's run ranking has no persistent check; the 1c row's "rank_pos[0] asserted against run_member" is not an assertion
CONFIRMED. window.c:1361-1370 states "rank_pos[0] IS the run member by construction" in a comment only;
no assert and no test compares rank_pos[0] (or any rank_pos[k]) to anything. rank_check.py (run_rank.sh)
checks only that pcrec hands NO ranking (rank_n 0, wsc6); memfn/tests g2_simd_gen.c states its own
rankings; no sabotage row plants window.c's translate loop (S750/S751/S752/S754/S794/S1420 plant vrun.c,
compose.c rank_ok or pcrec's side). Repro (consumer plant, check/c_rk1): in translate replace
`k ? &r : NULL` by NULL-and-reverse (`r.pos = n-1-k` for k>0). Emitted bytes MOVE vs SUBJECT:
`(?i)enzyme`, `(?i)union.*?select.*?from`, `foo.*barbazqux` under `-fmemfn-simd` (3/7), and the last two at
default flags (2/7); control (no-op plant) 0/3. Answer-identical (a different KB filter), so every
answer oracle/.rxt corpus stays green; only a byte-identity sweep against BASE (a one-off, stage-1
gate) sees it. SUSPECTED corollary: the "by construction" claim is not generally true. run_member
(window.c:~815) passes `exact = verify==NO`, translate passes exact 0, so for a verify-NO run whose
least-mass position is a masked (case-folded) one, rank_pos[0] != the run member. A 25-case probe
(debug print of plan_pos vs rank_pos[0] at default, -fmemfn-simd, -e utf8; check/c_dbg) found no
divergence, so I cannot confirm it; what is confirmed is that nothing would notice.
Severity: speed (filter choice), design (a ratchet row text unmet). Effort: small (a sabotage row on the
`after` plumbing + an `assert(p->rank_pos[0] == plan_pos)` in a trace build, or the byte-pin of the 3 patterns above).
Blast radius: translate -> vrun KB (vrun.c:237).

### CHECK-2 (test gap) the consumer wiring of kit_run_member is untested by mass_check; P3's scan has TWO witnesses
CONFIRMED. mass_check defines its OWN `sets_at`; window.c's `sets_at` (stride 32*j), presence.c's `run_at`,
P3's `exact=0`, run_member's `exact`, translate's `n` and `w->set[hint_at]` are covered only by byte sweeps and
pres_pick_witnesses.tsv, whose `scan` picks are `abcd` (-e utf8) and `(?i)hello world`. Plants in presence.c
(check/c_p3a: `exact` 1 at P3; check/c_p3b: run_at ignores the mask) leave BOTH scan witnesses byte-identical
and move `x.*(?i)abcdef` and `(?i)union.*?select.*?from` (2/8 and 1/8, default and -e utf8). A shadow
comparator on only those two witnesses (run_pres_picks.sh; run_cand_oracle.sh hands it the same table)
would not see them; I could not run the CAND_TRACE corpus census (pick_census.py), so SUSPECTED for the
census. Plant `run_scan = sc.pos-1` is caught (7/7 and 5/7 moved incl. both witnesses); window loop
plant (`w+j` -> `w`) caught by `(?i:x)abcdefg(?i:y)`. Plant `scan_mask = t->mask[0]` (P2's lead) moved 0/14: unchecked by my sample.
Severity: speed. Effort: small (add a masked-run scan witness with a hand-written expected position to the table).

### CHECK-3 (test gap, low) NORMAL refusal case violates only position 0
CONFIRMED. mass_check.c `lower = {'a','B','C'}`: the byte outside its mask is at j=0. Plant (check/p_r1)
run_cmp_sat's loop bound `j < t->run_len` -> `j < 1`: masschk 40/40 still passes. A refusal that checked only the
first (or only the last: j+1<len with violation at 0 is caught) position would ship. The positions after 0
are the ones a loop-bound bug loses. run_cmp_sat is shared (ofsskip.c:116), but the presence refusal is only exercised here.
Severity: maintenance. Effort: trivial (a second span with the violation at the last position).

### CHECK-4 (maintenance, pre-existing, re-anchored by 1c) S458's SAB_REACH is vacuous for the plant site
CONFIRMED. SAB_REACH compiles `é@` at `-e utf8` with default flags and requires "no `memchr(...,64`". At default
flags `é@` is a fixed-width `cover` artifact (no pre-check, no pick): SUBJECT and the planted binary emit
IDENTICAL bytes (check/c_s1097, `<=`), so the probe passes whether or not the plant site is reached. With
`--memfn=no-window-search` the plant moves it (memchr count 0 -> 1, as run_prechecks.sh:1006 compiles it). The
row is still DETECTED (prechecks, flagged compile), so the verdict stands; the REACH line certifies nothing.
Unchanged by 1c (diff touches only BEFORE/AFTER/figure); noted because 1c rewrote the row. Fix: add the deny flag to the probe.

### CHECK-5 (maintenance, low) decider_census BACKSTOP not updated for 1c's shapes
CONFIRMED. kit_run_member's deciders compare `ms < b.mass` / `ms < after->mass`; BACKSTOP is
`"< best","< bm","< lo","< sm","< wl","> c)","tie_takes",...`. `< sm`, `> c)` now match 0 lines in the
subject (1 each at BASE), `< inc` 0. An unlisted twin of kit_run_member's loop that keeps `<=` and no
tie_takes passes the census (check/srccopy: 53/53 pass; the header admits "a NAME-style filter"). The
two plants were re-pointed to `ms < bm ||` (a_mass_choose) and `wm < wl`; the kit_run_member shape itself is
never planted. Deleting the kit_run_member row alone is red (3 failures, as designed); MEMBER_COUNT 50 is exact. Low.

## PROBED-AND-HELD
- mass_check.c at 3ecb647c7: 40 passed / 0 failed; MASS_FLOOR 40 equals the case count exactly (a lost case reads red).
- Kit plants against mass_check (10, check/plant.sh): kit_run_set ignores mask -> 2 FAIL; tie to lower (S1095 shape) -> 3 FAIL;
  `exact` dropped -> 1; `after` tie inverted -> 2; `after` strictness off -> 1; `after` ignored -> 2; max instead of min -> 6;
  refusal deleted -> 1 (all red).
- Goldens re-derived by hand (rate1=1000+b, rate3): 2162 ('A' 1065 + 'a' 1097), 4070 (4000+16+17+18+19), 10054 (7*1122+1126+1074),
  4391, 5423, 23437 (23437.5 floored), 62500, 655000; rank orders (1,2,0,4,3) and equal-mass (3,2,1,0) all match.
- Rows: `python3 -I scripts/m6read_check_sab_anchors.py` -> 1102 rows (1143 sites) "all anchors resolve" (check/anchors.out);
  my own count check of SAB_BEFORE occurrences == SAB_COUNT over all 134 kit-source rows: 0 mismatches.
- S1095 plant (kit_run_member tie swap) moves bytes on 4/4 incl. `abcd` -e utf8; S1097/S458 plant (`<=`) moves `x.*abc`, `zq.*the` (-e utf8) and `é@` with --memfn=no-window-search.
- Refusal is loud end to end: forced-always refusal (check/c_rf) makes pcrec exit 1 "internal error: the memfn kit refuses the pre-check's presence spans" at default, -e utf8 and no-window-search, so the corpus population for "pcrec never hands a non-normal presence run" is every compile of make test; removal of the KITMASS informational count (reach_equal.py, presence.c) loses no verdict. Fold patterns probed (16 x 4 flag sets): no refusal.
- decider_census.py clean run: 56 passed, hits 37 >= 30; deleting the kit_run_member row -> red; reach_equal.py compiles, no KITMASS reader left (grep).
- No-mover on rank-consumed patterns: SUBJECT vs BASE 8 patterns x 3 arms (default, -fmemfn-simd, -e utf8 -fmemfn-simd) 0 moved; 66-char literal run with ranking identical to BASE.
- rank_pos[0] vs plan_pos: equal on 25 compiles (see CHECK-1).
- Landmark path (kit_run_set in the h loop) plant `+999999u` dropped: 0/3 moved -- not reached by my sample (unchecked, not shown unchecked).

CRITIC COMPLETE
