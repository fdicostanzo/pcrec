# pinbis report: what moved the fd-pres-pick differ pin (OWED)

## Counts
OWED. Pins to explain: byte 167 (scripts/emit_sweep.py:594), utf8 231 (:595), set by 99f310c49. Main 564db08c5 reads byte 154 (sp1atri/report.md).
Measurement job queued, not yet read: five commits (99f310c49, 657e23231^1, 657e23231, dc6a40dfb, 564db08c5), byte and utf8, c-default, arm --memfn=no-fd-pres-pick, each commit's own corpus.
Table to fill (commit, byte, utf8): from the `PINROW` lines of the job log.

## Cause
OWED. Per drop: the delta between adjacent commits, 2-3 patterns that left the differing set (compare per-pattern outputs with and without the deny at the two bracketing builds), one sentence why the deny no longer changes them, and a verdict (intended consequence vs lost reach). If R-30 (657e23231) and P1 (dc6a40dfb) do not sum to the whole drop, bisect the other first-parent code merges in `git log --first-parent 99f310c49..564db08c5 -- src memfn/src cli lib`.

## Proposed pins
OWED. Proposed new values for lines 594-595 with a one-line cause comment each. Do not edit scripts/emit_sweep.py (main's call).

## STATE AT HANDOFF
- Queue key: main-pinbis-count (job 320-main-pinbis-count), queued behind 312-kit-sp1a-ident2b.
- Job file: /var/tmp/pcrec-pcrec/scratch/pinbis/job1.sh (cap 3000 s, expects 10 PINROW lines).
- Logs: job.log in the job's run dir under /home/pcrec/projects/pcrec/worktrees/.boxqueue/{done,failed}/*320-main-pinbis-count/; per-run sweeps /var/tmp/pcrec-pcrec/scratch/pinbis/<sha7>-<enc>.log and .../<sha7>-<enc>/arms.tsv; builds build-<sha7>.log.
- Completion line: `pinbis-count: DONE`; `result` file there carries the verdict.
- Detached worktrees to remove afterwards: worktrees/pinbis-<sha7> for 99f310c, the 657e232 parent, 657e232, dc6a40d, 564db08 (`scripts/wtprune --apply --force --quiet-min 0 pinbis-<sha7>`; never rm -rf).
- Rulings file pinbis_rulings.md: empty, no entries applied.
