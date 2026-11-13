# yespin report

STATE: stopped

## STATE AT HANDOFF

No re-pin made. The measurement is OWED: the one emit_sweep run this lane needs
is queued behind the box lock (held by kit job 450-main-k382-maketest, a make
test, from 23:32; the lane waited 14+ min with no end in sight, per
DO-THEN-FINISH it hands back instead of idling).

OWED run (started detached, waiting on the lock; it runs on its own when the
lock frees):
`nice -n 19 python3 scripts/emit_sweep.py --ref 233e0af5d --tree-rev 233e0af5d --tree worktrees/yespin --out $PCREC_TMPDIR/scratch/yespin/out1 --variant plain --variant lowthr --bases byte --no-self-check --emit-pins $PCREC_TMPDIR/scratch/yespin/pins1.py --jobs 4`
Log: /var/tmp/pcrec-pcrec/scratch/yespin/run1.log; completion = the report's
final verdict line plus pins1.py written.

Known so far (reading only): the 'yes': 1740 floors are the four cells
VARIANT_PINS ('lowthr','byte') and ('plain','byte'), keys 'emit-ir-auto' and
'emit-ir-auto[-fno-prefilter-collapse]' (scripts/emit_sweep.py near the lines
that hold 'yes': 1740). They were last pinned by 646a8c0be (kclose4). 647
commits lie between it and 233e0af5d; named candidates: S1 never-match
51481d1b3 (merged via 004a7849e / a60681ae2 nevermatch, f1304934d pffix) and
K38-2. Cause not yet established; no bisect built.

Next steps for a fresh agent: read pins1.py for the tip count, then bisect the
plain/byte emit-ir-auto 'yes' count over the never-match commits.

## CHANGES

None committed besides this report.
