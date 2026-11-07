# qspeed report (lane qspeed, 2026-11-06)

## For Frank, in plain words

**Where the hours went (done records, 2026-10-30 .. 11-06, 263 jobs).** The queue
ran 81.6 h of green jobs in 7 days (about 48% of the wall clock), plus 83
cancelled jobs that never ran (0.5 h, so cancellations cost almost no box time;
they cost lane time and re-queues). Three jobs are 28 h of that: the full battery
(12.3 h), one bench monitor window (9.9 h) and one bench window (5.4 h).
Without bench, the dev-blocking share is roughly 50 h in the week.

| kind (by job-name suffix) | n | box hours |
|---|---|---|
| fullsuite (battery) | 1 | 12.3 |
| bench windows | 3 | ~15 |
| mech (full + shards) | ~35 | ~12 |
| ident (kit identity, 3 shards per unit) | ~30 | ~12 |
| make test | ~10 | ~4 |
| time2 / rulepilot timing | 15 | 3.7 |
| other (checks, axes, reach, sweeps) | rest | ~20 |

(Kind is read from the job name; the table is approximate by design.)

**Premise test.** Partly confirmed. The box is NOT saturated (48% busy over the
week; a live sample at 11:32 read 53% busy with one ident job running), so the
dominant cost is not hours of box time but WAITING behind serial occupancy:
the 181 jobs with an add record waited 848 h in total against 82 h run. Most of
that is deliberate (dependency chains, bench windows, evening hold), so it is an
upper bound; but at 11:22 today five vlbfix jobs sat "ready" for 1900 s behind
one id1 job, which is the shape you described.

**CPU use per job.** Only `make test` records it (perfrun): 79-81% mean busy on
16 threads over 24 min (40% on one run, 10-31). That section is already tuned
(TT-JTUNE); no quick win left there. ident/mech shards record no CPU; the one
live sample (53%) is a single point, not a measurement.

**What I changed (one small thing).** `scripts/boxqueue batch --snapshot`:
the batch freezes HEAD at add time and every stage runs in one detached worktree of
that commit in scratch (created by the first stage, removed after the last). Later
commits or edits in the lane's worktree cannot reach the job, which removes the
job-212 contamination class and the cancel/re-queue cycle that followed it.
Demonstrated: the generated job body's dry run reports the snapshot, and a real
run built the commit with `make -j16` in the snapshot and removed it afterwards
(rc 0). Documented: testing.md [QSPEED-SNAPSHOT], scripts/CLAUDE.md. Default
behaviour without the flag is byte-for-byte unchanged. Cost: the job sees
committed work only (a NOTE prints at add time if the tree is dirty), and each
batch rebuilds from scratch (about 2 s `make -j16` on this box, more for a cold
cache). Not tried: a full `make test` inside a snapshot (a gitignored generated
file a suite expects could be missing); the first real use should be a
`make test` batch, watched.

**Expected saving.** Not box hours; it saves the re-run after a contaminated job
(three cancelled jobs after job 212; each cancelled-before-start costs little, but
a contaminated RUN that completes is a full job of wasted wall: ~25 min for make
test, ~50 min per ident shard).

## Not built, and why

1. **Light jobs share the box with one heavy job.** Payoff unmeasured and
   probably small: only make test records CPU, and the long jobs (ident, mech,
   bench) are the ones that matter. It also touches the timing-quiet gate, which
   is the STOP RULE here. Needs a per-kind CPU measurement first: add the
   existing `scripts/cpusample.sh` to ident and mech shard jobs for a week, then
   decide. I would not build it without that.
2. **Ident shard sizing.** Each unit queues 3 ident + 3-4 mech shards (about 50
   and 20 min each, serial). 7 units in 5 days = about 12 box hours. If the
   cpusample shows ident at ~50% busy, running two shards at `--jobs 8` side by
   side is the larger candidate (one half-day of work, no verdict change).
3. **Duplicate builds**: only `make -j16` (about 2 s); nothing to gain.
4. **Cancelled jobs**: 0.5 h box time; not worth work.

## STATE AT HANDOFF
No rulings file entries (qspeed_rulings.md absent). Numbers: scratch
`$PCREC_TMPDIR/scratch/qspeed/{jobs,starts,adds}.tsv`. Live queue untouched
(read-only reads of done/ and queue.log).
