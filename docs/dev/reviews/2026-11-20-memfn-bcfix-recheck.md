# Re-check crit-memfn-bcfix: the bcfix fixes to job 710 (block-confirm). One critic (opus) plus its own verifier.

2026-11-20, 18:50-19:00. Read-only. Every probe ran on PRIVATE copies under this directory (pw/, pw2/), nice 19,
taskset 0-5, under scripts/watchdog for the plant batch. Nothing was written to the subject, either repo or the queue.

## Freeze (sha256 at the start, re-checked at the end: ALL HOLD)
confirm.py f153a19f, decision_rule.md 24ee21c5, synth.py 801c0b2c, work/check.pass efb4bfff, job 710 e8c9bf48, common.sh
4f4e5a39, 711 a4f93359, 712 fcf9077d, cpuquiet/spec.md dedf99bd, rulings file (kit worktree) 605b0abe. Full list:
freeze.sha256. bconf-night is at f8789cd2e with no tracked changes, before and after.
- RULE_SHA b7dbbafff6d43441: confirm.rule_sha() == the sha in decision_rule.md line 1, and rule_file_ok() is None (the file
  holds the code's DECISION_RULE verbatim).
- The marker check.pass == src_hash(meta) of the live work/ (True). The mtimes are in order: rule/confirm.py 18:18:58, then
  check's profile/walkid/marker 18:41:24-25, then dry 18:49.
- There is no run-* directory (and no quiet/ directory) under blockconfirm/: no timing has happened since the last
  amendment, or ever.
- Denied files were not opened.

## Per-id verdicts (FIX-NOW and DOC ids, plus the round-2 ruling)

| id | verdict | evidence (probe, not the fix's claim) |
|---|---|---|
| GATES-1 (cycle) | CLOSED | 712 WAIT_KEYS="kit-checkorder"; 711 has none; 710 waits on kit-checkorder and kit-rampchunk. The graph 710->{711,712}, 712->711 has no cycle |
| GATES-9 (cap) | CLOSED | the job hands measure DEADLINE = min(STOP_AT, JOB_T0 + (2 est + 1800) - 600). est 8392 gives cap 18584, the same as the dry run's decl. Mock drill (drills/mock.py): with the deadline already past, 0 rows and 60/60 NOT-RUN; with it mid-run, whole groups only (5 rows, 55 NOT-RUN). reps.tsv/voids.tsv are appended as repeats happen. A scale_cap raise only makes the deadline earlier (conservative) |
| MEASUREMENT-1 | CLOSED | drills d2/d3/d4: a WIN whose re-time is a TIE, NOT-RUN or noisy counts 0 (0 of 144). d1: a repeated WIN counts (144/144). The A/A line is printed (seen in drills/out/*/decision.md) |
| MEASUREMENT-2 + round 2 | CLOSED as written (see NEW-1) | d5: same direction voids (HARNESS). d6: opposite stands (CONFIRMED). d7: a TIE beside a control WIN is VOID (96 listed). d8: a TIE beside a control LOSS STANDS (96 listed). d9: a WIN not repeated beside a control WIN is voided as a TIE. d22: a LOSS opposite a control WIN gives the verdict LOSS. d23: a LOSS in the same direction as a control LOSS is voided. d18: the >25 % banner. Both TIE kinds are listed with counts |
| MEASUREMENT-4 | CLOSED | VARIANTS_RE [10,11,12] gives ALIGN_VARIANTS (default, off, default), the same 2:1 parity as [6,7,8]; POOL_N 13; check covers v6-8 and v10-12 (3900 gate exes, 3120 guard exes) |
| MEASUREMENT-5 | CLOSED | d15a: 72 of 144 NEW with all 116 OLD WIN gives no majority. d15b: 73 gives CONFIRMED. d15c: 14 NEW (the old 10 % case) gives no majority. The REPLICATION LINE is printed separately |
| MEASUREMENT-7, -6 (CLAIM text, byte-heavy line) | CLOSED | CLAIM is rewritten in the rule; the "byte-heavy pick cells outside S" line is in every decision (33 cells) |
| GATES-3/4 (spec 2') | CLOSED | mock (drills/mock.out): a sample max of 15 % gives raw 0.30, CPU7_MAX 0.200, capped True, and the banner text printed. A repeat at 25 % is void; one at 15 % is valid. A quiet sample of 0.5 % gives the 5 % floor. With every repeat above the cap: n 0 of need 3, voids 9 per cell-arm, so NOISE downstream. OBS_MIN 0.1 s is enforced in timed_pass_a. d16: the "QUIET SAMPLE BUSY ... (sample max 30.0 %)" banner is in decision.md |
| GATES-7 (LOSS first) | CLOSED | d10: a LOSS outside S, with every verdict-population cell control-void, gives LOSS. d12: a LOSS whose re-time is NOT-RUN stands. d11: a LOSS not repeated clears |
| GATES-6 (cause word) | CLOSED | d5 gives HARNESS, d14 all-NOISE gives NOISE, d13 with 0 rows gives NOT-RUN, d19 control NOISE gives NOISE |
| GATES-8 (DOC + expect line) | CLOSED | "TRUNCATED: " prefix and banner (d17); rc 4 leads to "kit-blockconfirm: TRUNCATED..." and the `truncated=0` expect line, which is distinct from the done line |
| FIDELITY-1 | CLOSED | re-planted at the TIMED values, timed text only. tailm1t is CAUGHT 5/5 at hex1000, af500, word256, ident1000, nonl500: the timed unit fails (wrong 398-522, and 2 at nonl) AND the staircase gate fails (2/14). My own plant skipfar (the block at offset 10B = 320 never tested, timed text only) is CAUGHT 3/3 at hex1000, af500, word1000: the timed unit is wrong 12.7k-16.7k and the gate fails 6-9/14. The unplanted control hex1000 passes |
| FIDELITY-4 | CLOSED | isspk is CAUGHT 3/3 (hex32, dig24, af1000) by the guard, on source + register, 12/24. My own plant inl2ool (the avx2-loop arm made noipa: answer-correct, so the timed unit and the gate pass) is CAUGHT 3/3 (hex32, word256, dig24) by the guard (no ymm/xmm in rxa_search). Its premise was probed: H64@on, Hspk-ool and avx2-ool rxa_search have 0 xmm/ymm at 10 patterns. The guard runs in check over every variant, with rc 1 |
| FIDELITY-2 | CLOSED | drills/decide.py: a wrong rule_sha in the run's meta is refused, and a wrong src_hash is refused. Editing one profile entry moves src_hash, so the marker goes stale. measure snapshots profile/walkid/marker/exes and decides on the copies |
| GATES-5 | CLOSED | values at the floor boundary (1/1.15 - 1e-9): the in-memory verdict == the verdict from results.tsv via cmd_decide (True) |
| GATES-2 | CLOSED | synth.py (private copy) runs: clean and ctrl give CONFIRMED, loss gives LOSS, and need/voids are carried |
| MEASUREMENT-3, -8, -9 (DOC) | CLOSED | PREMISE line, void split by A/A vs differing-walk, AXES_NOTE section; walkdiff.md line 6 carries the MEASUREMENT-8 note |
| OUT OF LANE nice -n 5 | as ruled | the job says 708 ran the same way. I did not check this beyond the job's own comment, because 708's done record is a job log, which is denied |

Probe sizes: 26 constructed decide drills plus 2 more (d25), 0 code/text divergences against my reading of the rule. 6 mock
drills. 17 plant runs over 5 plant kinds (3 of them mine or new: skipfar, inl2ool, none), every planted pattern built
x 5 arms x 6 variants. Minimum witness reach: the plants covered k = 24..1000, and tailm1t/skipfar targeted positions >= 255
(the old blind zone).

## NEW findings

### NEW-1 (answer, toward CONFIRMED; CONFIRMED by drill): voiding a TBL TIE beside a control WIN raises the WIN share
The round-2 ruling voids a TBL TIE beside a standing control WIN ("it may hide a LOSS") and excludes it from every count.
That cell is a non-WIN, whatever it hides. Voiding it removes a non-WIN from the CONFIRMED denominator. It cannot affect
the LOSS check, because a TIE is never a LOSS whether it stands or not. Its only effect is therefore toward CONFIRMED.
Repro (drills/d25.py, d25.out): 70 WIN + 5 TIE beside a control WIN + 69 TIE in the 144 verdict cells gives **CONFIRMED,
70 of 139**. The same rows without the control WIN give **NO LOSS but no WIN majority, 70 of 144**. The void share is
3.5 %, so no banner fires. d7 shows the larger form: 48 WIN + 96 such TIEs gives CONFIRMED 48 of 48 (the banner does fire).
The sibling ruling, a TIE beside a control LOSS, STANDS, and that one is conservative. The conservative counterpart for
a positive claim is the same treatment: the TIE stands as a non-WIN.
PROPOSED: **FIX-NOW (manager's ruling, form only)**: a TBL TIE beside a control WIN stays LISTED as "may hide a LOSS"
(the purpose) and counts as a non-WIN (TIE) in the majority denominator, not VOID. This is one branch in
write_decision's tie_beside loop plus the rule sentence, then a re-stamp and re-check. Alternative if the manager keeps
the VOID: print beside CONFIRMED the verdict with those cells counted as TIE, and headline the weaker of the two.

### NEW-2 (design/doc): CONFIRMED has no floor on the readable share of the verdict population
d24: 1 readable verdict cell (WIN) and 143 INCONCLUSIVE-NOISE gives "CONFIRMED (... 1 of the 1 readable ...)". The NOISY RUN
banner fires, but the headline word is CONFIRMED. Voids behave the same way (d7: 48 of 48 after 96 voids, under the
VOID SHARE banner). The counts are in the verdict text, so this is visible, not hidden. TRUNCATED cannot reach CONFIRMED
in practice: a main-pass truncation means the deadline has passed, so the whole re-time is NOT-RUN and every WIN is "not
repeated" (d3). d17's TRUNCATED CONFIRMED needed re-time rows I supplied. The main pass runs the NEW classes last
(index 2540 of 4200), so this matters only through the re-time.
PROPOSED: **FIX-NOW (small) or DOC, the manager's choice**: CONFIRMED needs its readable cells >= half of the verdict
population's non-N/A cells, else the INCONCLUSIVE word with the cause. One clause, then a re-stamp.

### NEW-3 (NOTED): a refused measure leaves a run directory
measure copies the SNAP files into --out before its own deadline refusal (rc 77). The job maps 77 to "DONE rc=1", and
run-<ts>/ then holds the snapshots plus the log but no meta.json. decide refuses such a directory (no meta, so
rule_sha None differs from the live one), so it cannot be decided wrongly. It is clutter only.

## The other checks the brief named
- STOP_AT 2026-11-21T12:00: --ready refuses at or after it, and also when now + est + 600 passes it. The body re-checks
  before and after the quiet wait. measure refuses when now + est passes the deadline. HELD (code read; the
  mock deadline drills).
- Wait keys: no cycle (above). A failed or cancelled upstream lets 710 proceed (75 only while pending|running), as before.
- The dry run does no real work: the job's --dry-run runs check_tree, `perf stat -- true`, `confirm.py dry` and decl,
  with no wait_quiet and no measure. A faithful private copy (pw2/: real exes by symlink, re-paths in exes.json) ran dry
  to rc 0 in 4.0 s with est 8392. `find -newer` shows 0 files written there and 0 in the real subject dir.
- No run-* directory exists (above).

## PROBED-AND-HELD
- 26 decide drills (d1-d24 + d15a-c) and d25 x2: the code's verdict equals my reading of the rule text in all of them.
- 6 mock drills of quiet_sample/void_reason/run_cells (cap, floor, all-void, deadline past, deadline mid-run, pass order).
- Plants: tailm1t 5/5, skipfar 3/3, isspk 3/3, inl2ool 3/3 CAUGHT; the unplanted control 1/1 PASS.
- decide: TSV round trip exact; rule and src mismatches refused; a profile edit makes the marker stale.
- synth.py on the amended code: 3 cases, verdicts as designed.
- Freeze: 10 files re-hashed at the end, all OK; bconf-night HEAD and status unchanged.

## Overall: READY TO TIME after NEW-1 is ruled
Every FIX-NOW and DOC id is CLOSED by probe. No fix opened a hole in the gates, the deadline, the wait keys or the dry
run. The one new answer-level item is NEW-1, which the round-2 ruling itself introduced. It biases toward CONFIRMED by
construction: 5 cells flip a no-majority to CONFIRMED with no banner. If the manager rules NEW-1 as proposed (or the
alternative), the fix is one branch plus a re-stamp. src_hash includes DECISION_RULE, so the marker goes stale and check
must re-run (~1350 s), then dry. After that the job is READY TO TIME. If the manager keeps the
VOID knowingly, the harness is READY TO TIME as frozen. NEW-2 does not block: its cases are visible in the verdict text
and banners.

Files: drills/{drill.py,drill.out,mock.py,mock.out,decide.py,d25.py,d25.out}, plants/{plant.py,run.sh,plants.log,out_*.txt},
freeze.sha256.

## RULING (kit manager, 2026-11-20 19:0x)
READY TO TIME after these changes:
- NEW-1: FIX-NOW. The manager REVERSES his round-2 ruling, which was biased toward CONFIRMED (the critic is right). A TBL TIE beside a control WIN counts as a TIE and is listed as "may hide a LOSS".
- NEW-2: FIX-NOW. CONFIRMED needs at least half of the NEW-population S-pick cells to be readable; below that, INCONCLUSIVE, named for its cause.
- NEW-3: NOTED.
- Sized check after the fix: the manager verifies the round-3 diff and the drills (the critic's NEW-1 repro must read NO MAJORITY), with no further critic round.
Lesson: a ruling that voids readings must be checked for which direction it pushes a positive claim. Voiding non-WINs inflates the WIN share.
