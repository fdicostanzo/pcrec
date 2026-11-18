# memfn kit — wake-up brief

Rewritten 2026-11-17 23:05 by the kit session (pcrec-memfn), closed at Frank's /close. Main (session 138) also closed;
a NEW main wakes from its own brief. Tonight's timing set 1 runs from 01:00 without either session.

## Who you are
The kit manager (`/pcrec-memfn-manager`). Main = session `pcrec-main`. Frank rules, mostly via main.
Ledger/journal branch: worktrees/memfn on lane/memfn-k1108. Heartbeat cron `17,47` (OWNER=kit; DELETED at close,
recreate on wake). Waiting list worktrees/.mgr/waiting_on.kit. Sabotage ids worktrees/.mgr/sabotage_ids.txt (next S3335).

## Read in order
1. This file. 2. memfn/docs/journal.md, 2026-11-17 entries (the forms rounds r35-r41 and their rulings).
3. docs/design/memfn/r45_reply.md rev 12 on lane/memfn-forms. 4. docs/dev/lanes/formsfixk_report.md on lane/memfn-forms.

## Box rules (binding)
Evening hold 20:00-01:00 is Frank's; lane CPU ends 19:30. Timing only in windows main cleared with Frank. If the quiet
gate refuses on Frank's processes: REPORT to main, never retry around it. Queue + cloud verdicts only via
`scripts/monread kit` (one `--wait` armed with run_in_background). Lanes wait in the FOREGROUND with a bound (they keep
idling on background notifications: say so in every brief). Never merge to main or push main.

## FIRST ON WAKE
1. `scripts/session_role kit`; recreate the heartbeat; `scripts/monread kit`; `scripts/boxqueue status`.
2. SET 1 VERDICT (jobs 600-609, RUN_ID mfcard-zen4-3, FROZEN f6274c11b, job set
   /var/tmp/pcrec-pcrec/scratch/memfn/mcfixa/jobs/; pre-window reading 23:19: no watched app, load 0.93 vs 2.0).
   609 gives the d197 verdict per ISA level. Rules: CONFIRM -> set CONFIRM_CELLS, queue 610 only; INCONCLUSIVE -> the ONE
   re-run with FIRST_RUNDIR(_AVX2)=mfcard-zen4-3 and a new RUN_ID (may share the 11-19 night; ask main for the window);
   LOSS settles span_pick row 1 at that level; WIN -> the ruled split shape under its own go. Gate refusal -> tell main.
   Any RED -> a triage lane. Afterwards: unpin worktrees/mfind from .wtprune.keep; r24 SR-1..SR-4 owed.
3. FORMS (R-45 plan A): lane/memfn-forms @ 27b18e75c = frozen candidate (cloud test + axes GREEN). Rounds r35-r41 all
   ruled and fixed; r41 replaced the layout twins by SETUP RANDOMIZATION (pools of 4 layout variants per text, per-launch
   draws, per-text layout term, variant-aware bimodal test). selftest 205/0, class drill worst 0.017. Power is RECORD
   (5 % win seen 170/300 at tau 1 %, 7 at 2 %; a missed win keeps 64). h=64 shipped UNMEASURED.
   NEXT, once set 1 leaves the box: round 7 (sized: 2 critics; both simulate rules + the PERTURBATION lens, all in
   docs/dev/guide/critics.md on main) on 27b18e75c via the pcrec-critic skill, topic memfn-forms7. Judge K6's drill win
   re-centring 0.955 -> 0.953 (formsfixk report). Fixes if any, then cloud on the new tip.
4. BY 10:00 11-18: tell main whether the 14:00 delivery holds; if not, the cards move a night (main asks Frank).
   A new main may not be up: SendMessage AND a `[responses]` notice.
5. BY 14:00 11-18, DELIVER to main: a `[responses]` done line (tip, report, validation), the pcrec-side readers that
   move (abi number, stamps, spec sentences, pins, test expectations: FOUND BY GREP), expected conflicts vs lane/covs2b
   @ 28af649c9 (docs; tests/ci/cloud_axes_shards.tsv; tests/ci/cloud_mech_shards.tsv was REGENERATED wholesale by
   formsfixj: main regenerates after merging, keeping every id once, never a line merge), h=64 UNMEASURED, known limits
   (power RECORD; the rho share is the body's own speed and is printed). Also: the layout pool is ARM-GENERIC at the TU
   level (main's width arms could use it via a shared helper; nothing built), and cover_cap.md §11.4's A/A floor gets
   checked WITH main before main's width cells are timed.
6. AFTER main sends the frozen covs2b sha (by 20:00 11-18): `worktrees/fcards-night` at FROZEN, clean, pinned in
   .wtprune.keep; window.vars RUN_ID=fcards-zen4-1, FROZEN=<sha>; queue 700-704 from
   /var/tmp/pcrec-pcrec/scratch/memfn/fcards/jobs/README.md (not before 2026-11-19T01:00; total est 3,224 s, cap 9,672 s;
   700 runs G2 head passes -> g2_heads.txt + g2_defective.txt; 701 makes one `cards.py rule --g2` call first); send main
   the keys; after 702 tell main "h* frozen". 704 identity runs only at h*=64 (h*<64 = a kit commit + abi event after
   the night). The cards MUST time on covs2b WITH the forms merged.

## Hygiene owed
Prune with `scripts/wtprune` (dry run, then --apply / --force NAME): forms fix lanes formsfixa..k, formsland*,
fcards-dry*, scanrow, tri-span4kax, raisefix. Never rm -rf. Also owed: ADQ-3-3, the mfind-long-run witness.

## Lessons (2026-11-17)
- A noise estimator must be drilled at EVERY level it pools over AND by the PERTURBATION each side of a ratio carries
  (what differs between the two objects, read with nm/readelf); six rounds each found one more level until the general
  form (randomize the nuisance factor for every arm) closed the class and deleted the special machinery.
- A lane's idle on a background notification stalls it: brief foreground bounded waits explicitly.
- A finished lane's `NAME.done`/`.stopped` marker in a shared worktree blocks the next lane's lanecheck: remove it.
