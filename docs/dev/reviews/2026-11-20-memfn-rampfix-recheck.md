# Re-check 2026-11-20 memfn-rampfix (one critic, sized): the fixes to the rampchunk timing-spike harness

## Subject (frozen)
- Branch lane/memfn-rampfix = 1936fb19116b99c19a721a1016c6b14322316ede (rev-parsed at start and at hand-back).
- Harness docs/dev/lanes/rampchunk_bench/ on that worktree is byte-identical to scratch/memfn/rampchunk/{h/*, decision_rule.md,
  counts.tsv, pairs.tsv, smoke.out, smoke-rampfix.out, check/record.txt}. The job scratch/memfn/fcards/jobs/712-kit-rampchunk is
  byte-identical to the branch's 712-kit-rampchunk.sh. build/src/rc_window.h and rc_count.h equal h/'s.
- RULE_SHA: sha256(decision_rule.md)[:16] = 5f4851edba7f6589 = rule_sha.txt. VERIFIED.
- Build tree worktrees/bconf-night at f8789cd2e (= TREE_SHA). `rampchunk.py dry` on the subject: rc 0, marker f6111c9a5b7694d9,
  est 1402 s.
- Every plant ran on a COPY (scratch/crit-memfn-rampfix/rc/). No file in the subject's scratch is newer than the freeze, and
  there is no __pycache__ anywhere.
- Main moved f55b3bdc6 -> 694d91dc4 during the round. No ruling on this subject is involved.

## Overall: READY TO TIME
Every FIX-NOW and DOC id from the prior round is CLOSED, each confirmed by a probe. The new findings below are NOTED or DOC, and
none of them can make the run read RAMPCLIP vs ALIGN, RAMP vs ALIGN or STREAM-SAFE wrongly on today's frozen build. One
finding, N1, is closed for today only by this critic's own rebuild; it is not a harness gate.

## Prior ids

| id | status | evidence (probe, not the fix's claim) |
|---|---|---|
| MEAS-6 | CLOSED | The restart cells rs1000/rs20000 are timed as find-all sequences. Each pair is decided only over pairs.tsv DIFFER cells, and IDENTICAL cells are named. I re-derived pairs.tsv for 5 row-cells x 30 pair rows from fresh traces: 150 rows, 0 differ. Drill D7: a 30% RAMPCLIP win placed only in dense (IDENTICAL) gives EQUAL, not PREFERRED. RAMPCLIP4096 vs ALIGN4096 is decided over unb/early, unb/rs1000 and bnd/early, x2 modes. See N3 on bnd/rs1000. |
| FID-5 | CLOSED | The record carries 192 PLANT lines at B 8/64/4096 and 0 NOT CAUGHT. I re-planted bug3 myself at the timed B 16384 and 65536, in 6 builds (unb align/rampclip/palign/fixed, bnd ramp/align), and every one is caught by check's corpus gates: counts vs model 176..1359 differ, attempts vs ON 174..814 differ. On the 1 MiB timed cells, bug3 at 65536 for unb align/fixed NEVER fires (counts = model, attempts = ON on all 8 cells), so it could not move a timing either. |
| FID-3 | CLOSED | The model runs at every B on the whole corpus (record: e.g. unb.align65536.c counts vs model 0) and at the timed B on every timed cell (count). Key-swap plant, RAMPCLIP4096 built with ALIGN's rule: count's model mismatches on dense, early and rs1000, and its dense counts equal ALIGN4096's, so "rules differ on dense" also fires. B-swap plant, RAMPCLIP4096 built at B=16384: model mismatch on dense, rs1000 and sp4096. |
| FID-6 | CLOSED | Attempts vs ON are gated in check (corpus) and in count (timed cells). The OFF arm is not vacuous: the record shows unb.off.c with 1153 differ. In my bug3 re-plants, attempts differed on 174..814 corpus subjects. |
| FID-1 | CLOSED | Drill D4: one wrong rc in 6,264 launch rows makes decide.py exit 3 and print a HARNESS-RED line. On the real exes, my deadline-cut smoke had no rc red. |
| MEAS-2 | CLOSED | Drill D1: with every arm at 2 valid launches, all 44 cells are INCONCLUSIVE-NOISE. Every (a) and (b) verdict is NO-VERDICT, the VERDICT line holds no EQUAL, NO-LOSS or PREFERRED, and the 10% line is printed. Drill D5, both modes A/A-inconclusive, gives NO-VERDICT too. The rule text was amended (amendment 3). |
| MEAS-4 = GATES-1 | CLOSED | A real `measure --smoke --deadline now+7` on the copy gave notrun.tsv bnd/rs1000/cold, a TRUNCATED line in decision.md and in the measure output, the 10% line, the TRUNCATED tag on the VERDICT line, "valid launches per cell" showing 0, and rc 4. The job maps rc 4 to "kit-rampchunk: TRUNCATED" and "DONE rc=4", which the expect line `DONE rc=0$` does not accept. Drill D2: a 20% RAMPCLIP win in unb/early/warm with round 6 NOT-RUN is excluded (EQUAL); the same data with the round present gives rampclip4096-PREFERRED. |
| MEAS-3 | CLOSED | Drill D3: AL is 15% off ON in one cold cell, so cold is MODE INCONCLUSIVE (floor 15%). RAMPCLIP4096's 30% cold loss is printed on the "(A/A-INCONCLUSIVE modes, printed, not counted)" line and kept out of the VERDICT line (NO-LOSS from warm). See N4. |
| MEAS-5 | CLOSED | Every (a) and (b) line and the VERDICT line carry "INCONCLUSIVE-NOISE x, NOT-RUN y of z" (D1, D2, the smoke cut). |
| MEAS-10 | CLOSED | Drill D8: RAMPCLIP4096 on unb/text/warm is bimodal (rounds 0-3 at 1.00, rounds 4-6 at 1.25). The median gives NO-LOSS, and the line lists "straddling 1+thr: unb/text/warm [1.00..1.25]". |
| MEAS-1 | CLOSED | ZERO and AL are in timed_arms. build.out: AL's .text differs from ON's (unb e109e7.. vs eb1355..; bnd 038348.. vs 36645c..), and AA's equals ON's. The floor takes max(\|AA/ON-1\|, \|AL/ON-1\|) (D3 shows AL alone setting it). |
| MEAS-7 | CLOSED | The RAMP vs ALIGN pair is present at each B and method. STREAM-SAFE is computed from the trace against python's own block end, and the 135 re-derived counts.tsv rows (xcross column) differ in 0. On the real counts: ramp* and fixed* are NOT-STREAM-SAFE, rampclip* and align* are STREAM-SAFE, over 22 row-cells each. The caveat is printed. See N2. |
| MEAS-9 | CLOSED | ALIGN vs FIXED and RAMP vs FIXED are in PAIRS for both methods (pairs.tsv lists their DIFFER cells). |
| FID-2 | CLOSED | The lane's twinA plant is CAUGHT in the record. My own four timing-only plants are all CAUGHT by twin_differs: ALIGN's end halved under `#if !RC_COUNT`, PASS lim halved, the timing hook RC_FIND shortening n, and RC_B redefined in the timing hook block. A .t-only defines swap in the declared list fails the twins() assert. The residual is N1. |
| FID-7(i) | CLOSED | The crossing count uses rc_count.h's own `(c+1) \| (B-1)` and python's `((c+1)//B+1)*B`, never rc_blockend. The bug6 plant (rc_blockend itself off by one) is CAUGHT in the record with crossing asks 1025/1135. |
| FID-4 | CLOSED | Module-level assert TIMED_B ⊆ CHECK_B and PLANT_B ∩ TIMED_B. preflight() is re-run in measure, writes preflight.txt and refuses on any problem. |
| FID-8 | CLOSED | counts.tsv and pairs.tsv carry `# manifest .. subjects ..`, and preflight compares it. I re-derived a subset: 135 counts rows and 150 pair rows identical. counts.tsv is complete: 27 arms x 22 row-cells. See N2(b). |
| GATES-2 | CLOSED | A plant of one comment line in my copy's decide.py makes dry print "PROBLEM correctness marker missing or stale, or a harness file moved since check". Restoring the file returns dry to clean. |
| MEAS-11 (DOC) | CLOSED | `git show b927dd9ae:` (committed 15:09:47) already holds Amendments 1 and 2, as amendment 3's correction says. |
| GATES-3 (DOC) | CLOSED | The job prints `DONE rc=5` after wait_quiet fails and `DONE rc=1` after mkdir fails. |

## New findings (PROPOSED dispositions)
- **N1 (FID, NOTED): a post-build swap of TIMED binaries is invisible to every gate.** No gate ties a .t file to its declared
  source and defines. The twin diff re-preprocesses the DECLARED source+defines. check's only .t gate is answers vs OFF, which
  is window-neutral: a swapped align4096.t under rampclip4096's name differs on 0/4490 subjects. count runs only the .c builds,
  and the rc check is window-neutral. The manifest records whatever is on disk, and a check re-run then re-marks it. The swap is
  not live today: I rebuilt all 48 timed window exes from their declared source+defines, and all 48 are byte-identical to the
  manifest. PROPOSED NOTED, with this rebuild as the record. A cheap later form (PLAN, not before 712) is a key string compiled
  into each binary and printed by the driver on every launch.
- **N2 (MEAS-2 analog on STREAM-SAFE, NOTED): (a) with 0 counts rows for an arm, decide prints "STREAM-SAFE over 0 row-cells"
  and a STREAM-SAFE token on the VERDICT line** (drill D9). (b) The counts/pairs key covers manifest+subjects but not the harness
  pins, so a counts.tsv written by different count code against the same build would still pass preflight. Neither is live:
  counts.tsv has all 27 arms x 22 row-cells, and the re-derived subset matches. PROPOSED NOTED, not a blocker. If decide.py is
  touched for any other reason, require seen == the planned row-cells (else NO-VERDICT) and add the harness pins to key_line.
- **N3 (DOC): the bounded row's restart cells are not alike.** In rs1000 the gap from the last " @x" to the match's "@x" is 7,
  above the bounded row's chain cap G=6, so every window chain stops at the match. In rs20000 the gap is 5 and the chain
  continues. The gap comes from (k-4) mod 3, not from k. So bnd/rs1000 is IDENTICAL for RAMPCLIP vs ALIGN at every B (share
  0.0296 at 4096), and the bounded row enters the owner's pair at 4096 only through bnd/early. This is honest: the cell is
  excluded and named. A reader must not take rs1000 vs rs20000 as "k alone". PROPOSED DOC: one sentence beside the pair
  verdicts in the report.
- **N4 (DOC): the VERDICT summary line does not mark an A/A-inconclusive mode.** Drill D3: RAMPCLIP4096 loses by 30% in every
  cold cell, and the VERDICT token is NO-LOSS. This follows the rule, but the only signs are the A/A line at the top and the
  per-arm sub-bullet. PROPOSED DOC: the run's report states which modes were counted.
- **N5 (NOTED): the smoke plan's two cells (unb/dense, bnd/rs1000) are IDENTICAL for every RAMPCLIP/ALIGN pair, so the smoke
  never produces a (b) verdict.** The decide drills above cover (b). It is no input to 712.

## Reading notes for the owner's pairs (not findings)
- By construction, RAMPCLIP's window lies inside ALIGN's. The pair can therefore come out only as RAMPCLIP PREFERRED, EQUAL, or
  noise-driven ALIGN wins, and it is decided over 3 row-cells at 4096 and 5 at 16384/65536 (x2 modes).
- Asks and windows differ in IDENTICAL cells: on rs20000, RAMPCLIP4096 makes 895 asks to ALIGN4096's 361 with the same
  coverage. This is per-call work the coverage metric ignores. My estimate is under ~1% of a 1 MiB sequence. I did not measure
  it.
- EQUAL means "within thr", and thr = max(5%, 2 x the A/A floor, AL included). Under today's load the smoke floors were 6-10%
  warm and 40-50% cold (1 launch, box busy with a make test), so cold may well go INCONCLUSIVE on the real run.
- On sp4096 at B=4096 every RAMPCLIP/ALIGN window is degenerate (each occurrence ends its block), so those arms equal ON there.

## PROBED-AND-HELD (counts)
- Twin diff: 4 new timing-only plants, all CAUGHT. 48/48 timed window exes are key = code (rebuilt byte-identical).
- bug3 at 16384/65536: 6 builds, all CAUGHT on the corpus. Key/B swaps: 2 builds CAUGHT in count. A .t-only defines swap is
  refused by twins().
- counts.tsv: 135 rows re-derived, 0 differ. pairs.tsv: 150 rows re-derived, 0 differ. counts.tsv is complete (27 x 22).
- decide.py drills D0-D9 on full-plan constructed outcomes (6,264 launch rows each): null gives EQUAL/NO-LOSS; zero counted
  cells give NO-VERDICT; NOT-RUN is excluded and tagged; an A/A-inconclusive mode is printed and not counted; both modes
  inconclusive give NO-VERDICT; a wrong rc gives exit 3; the direction case gives align PREFERRED; an IDENTICAL-only win gives
  EQUAL; a bimodal cell is flagged as straddling; STREAM-SAFE with 0 rows is N2.
- One real deadline-cut smoke run gave rc 4 with every TRUNCATED surface present. Dry on the subject passed; GATES-2's plant
  was refused.
- Probe scripts: scratch/crit-memfn-rampfix/probes/. Drill outputs: drill/. The cut run: run-cut/.

## RULING (kit manager, 2026-11-20 16:2x)
READY TO TIME is accepted.
- N1, N2, N5: NOTED.
- N3, N4: DOC, to be read with the results.
- Cold A/A floor risk: noted; a cold-mode INCONCLUSIVE is a valid outcome.
- ORDER CHANGE: 712 runs SECOND, after 711 and before 710. It is ready now, while 710 still needs its CPU control and a critic round. 712 is queued right after 711, so its --ready waits on kit-checkorder (GATES-4: 711 must be queued first). 710's fresh lane will make 710's --ready wait on kit-rampchunk.
