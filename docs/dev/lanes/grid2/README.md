# grid2 — the zen4-grid2 timing slot (r17b_prime.md §5.4 REVISION 3, D166, D167 option (B))

**Status (lane grid2r3, 2026-10-16): the harness matches the REV 3 slot spec and is built and
checked, NOT RUN; the timed slot is the kit manager's.** Rev 3 added item 2a (the N = 33..46
staircase), item 3a (three cover shapes), item 3v (VM_ATTEMPT, the VM hat at |S| = 1), NONE as an
extra arm inside item 3 (item 4 deleted), the cross-launch rerun trigger and a recorded compiler
provenance; `../grid2r3_report.md` carries the item list, the re-judged deviations, the estimate
and the verdicts.

One run, one box, one method version (`kit-grid@2`), ONE subject condition: STREAMED. This
directory extends grid1 (`../grid1/`, whose `README.md` is the arm contract and stays
runnable as it was); it reuses grid1's driver, loader, checker, arm tables reader and legs
and adds the arms, the cells, the oracle and the harness changes below. The design of what
the slot measures and why is `r17b_prime.md` §5 (on `lane/memfn-r17`); what the prep lane
built, checked and could not build as written is `../grid2p_report.md`.

## The launch command

    setsid nohup bash /home/pcrec/projects/pcrec/worktrees/grid2r3/docs/dev/lanes/grid2/slot.sh \
        /home/pcrec/projects/pcrec/worktrees/memfn-slot/grid2 >/dev/null 2>&1 </dev/null &

(or the same path in whichever worktree the kit manager merges `lane/grid2r3` into; the timing CPU is 14, the build and the gate work run on 12-15). The one
argument is the SLOT DIRECTORY; everything the slot writes is under it, nothing is committed.
`slot.sh` builds, runs the correctness gate FIRST, then times; the manager reads
`<slot>/slot.status`. A quiet box is the manager's to arrange: the slot waits up to
`START_WAIT` (1800 s) for load1 < 1.5, records what it saw, and the harness holds the same
gate at every group boundary.

    PCREC=<compiler>    the KIT-BRANCH compiler (default worktrees/memfn-r17/build/pcrec, lane/memfn-r17,
                        abi 77); it must know --memfn=no-pf-terms-mask, which main's does not, or build.sh
                        stops. Its COMMIT, abi, sha256 and staleness are recorded in provenance.txt
                        (`compiler_*` lines) and in the COMPILER status line; a compiler whose build inputs
                        are dirty or newer than the binary FAILS the slot (ALLOW_DIRTY_COMPILER=1 records
                        and proceeds); EXPECT_ABI=N / EXPECT_COMMIT=sha fail on a mismatch when set
    CPU=14 LAUNCHES=3 RERUN_EXTRA=2 LOADMAX=1.5 START_WAIT=1800 JOBS=4
    ALLOW_EXCLUDED=1    time on although an INSTRUMENT arm (tw0-2, sc0) failed the gate
    SKIP_BUILD=1 SKIP_CHECK=1    resume after a build / a green check (SKIP_CHECK refuses a stale check.log)
    DRY=1               see "DRY"

## The status file `slot.status`

One line per event; it ENDS with exactly one of:

    COMPLETE <date> required=ok optional=<done|skipped:counters>      exit 0
    FAILED <why> <date>      exit 1 (3 = a pickable arm failed the gate; 4 = provenance or manifest census)

Progress: `SLOT_START`, `COMPILER compiler_sha256= compiler_abi= compiler_commit= compiler_branch=`, `COUNTERS unavailable (...)` (then the SUGGESTION text), `BUILD_START` /
`BUILD_END rc=` / `BUILD <last build line>`, `CHECK_START` / `CHECK_END rc=` / `CHECK <verdict>`,
`EXCLUDED`, `CHECK_OK`, `QUIET load1= waited= ok|NOT-QUIET-proceeding`, `COUNTS`, `ESTIMATE`, then per
phase `<P>_START`, `<P>_PROGRESS groups=N` (every 60 s), `<P>_END rc=`, `<P> <the phase log's completion line>`.
Phases, in order:

| phase | items | what | log | raw launches |
|---|---|---|---|---|
| `F1` | 1+2+2a | the fit groups' streamed twins (+ the dispatch-twin arms on 20 dense groups) + the N = 33..46 staircase | `time_F1.log` | `time/raw_F1.tsv` |
| `F3` | 1+2+3a | the member-free F3 groups (+ twins, the R0 scaffold arm `sc0`) + the three cover shapes | `time_F3.log` | `time/raw_F3.tsv` |
| `OB` | 3+3v | five DFA one-byte cells (NONE an extra arm of their gap groups) + the VM_ATTEMPT cell, each x (6 gaps find-all + 4 member-free lengths) | `time_OB.log` | `time/raw_OB.tsv` |
| `F2` | 6 (optional) | F2 perf on {walk, V1, A1} of every item-1 group | `f2.log`, `f2/raw.tsv` | |
| `F2S` | 7 (optional) | F2's streamed perf pass (hex-run, bounded, dfa-hat x prose/docs/code) | `f2s.log` | |
| `TRIG` | 8 (optional) | the pre-scan trigger probe, KEEP vs DROP | `time_TRIG.log` | `time/raw_TRIG.tsv` |

`F2_SKIPPED <why>` (then the SUGGESTION) or `F2_DONE item= rows=` for the perf passes. A phase
log ends `time.sh: COMPLETE rows=N groups=G reruns=R xreruns=X requeued=Q wall=Ns` (X = the groups the cross-launch trigger fired in, a subset of R). The three required
phases failing, or a launch whose answer differs from its base (`# ANSWER MISMATCH`), fails the
slot; the optional passes never do.

## What the slot does, by step

1. **Build** (`build.sh`; ~30 s dry). Design (`design2.py`), then `../grid1/build.sh` for the six
   grid1 cells and the new R0 cell `wcls` (`\w+=`, emitted by the kit compiler through
   grid1/build.sh's `EMIT_CELLS` hook) with every grid1 arm and its G1 control; the ext sets
   `ext/ob/` (`ext_ob/build.sh`) and `ext/trig/` (`ext_trig/build.sh`); the item-2 arms
   (`mkvar2.py disp|scaf`); the streamed subjects (`design2.py gen`, `streamgen.py`).
2. **Check** (`check.sh`) — first, and a gate: grid1's legs O, R, L, C (+ U reach, G landing
   fidelity) over the merged tables; leg O is **libpcre2 10.46** through `tests/oracle/`'s local
   adapter (`design2.py oracles`; any other version is refused unless `ORACLE_VERSION=` says so);
   leg U2 (the one-byte sites are reached); **leg P** (`provcheck.py check`: the compiler's provenance,
   every cell re-emitted by the compiler and compared to `art/`, every timed arm's signature, the ext cells'
   ROUTE stamps, the cover shapes) and **leg M** (`provcheck.py census`: the rev-3 items in the arm tables
   against literal expectations) fail the run with exit 4; **a pickable arm in `excluded` fails the run**. The
   deep legs (E N F A) are off: they are grid1's, on grid1's subjects. `plants.sh` is the
   gate's failing direction for the new arms; `paranoid_check.sh` the suggestion's check.
3. **Time** (`time.sh`, method `kit-grid@2`): CPU 14 via `taskset`, rotated interleaving, LAUNCHES
   3 (each launch = the driver's 7 rounds), the base launched THREE times (`base`, `base#b`,
   `base#c`), the rerun rule (a group in which any launch has |base_i - base#b_i| > 0.031 x
   median(base), OR in which any arm's per-launch medians spread by more than max(the group's own
   A/A floor, 0.031 x median(base)) [rev 3 C7, the cross-launch trigger], gets +2 launches, once;
   the share rerun is reported), the quiet gate at every group
   boundary (a group whose end load1 reached 3.0 is re-queued once at the end of its phase).

## The arms, cells and subjects

| cell(s) | arms | notes |
|---|---|---|
| `dig bounded dfa-hat` + `f3-` `dig hex-run word-eq quad wcls` | `walk` (base) `V1 S1 A1` (+ `A3` in find-all) | item 1: pickable arms at both layers; `walk#b`, `walk#c` are the harness's copies |
| `dig` member-free n = 33, 34, 36, 38, 40, 42, 44, 46 | `walk` (base) `V1` | item 2a [rev3 C5]: the crossover staircase (M9, M12) |
| `f3-c020 f3-c001 f3-c110` (`[ad]+=` `[xy]+=` `[0-9_]+=`) member-free, 64 KiB and 1 MiB | `walk` (base) `V1` | item 3a [rev3 C3]: cover shapes (range,eq,cube) = (0,2,0), (0,0,1), (1,1,0); `provcheck.py` asserts each V1 mask holds exactly that shape |
| the same, on 20 dense groups and the member-free points | `tw0 tw1 tw2` | item 2: the dispatch scaffold with `f` forced to WALK / V1 / A1 (`mkvar2.py disp`); `f` is produced through an opaque compare so gcc cannot fold the dispatch |
| `hex-run word-eq wcls` member-free | `sc0` | item 2: the walk moved into a helper reached through a struct (M18) |
| `o-fwd o-bnd o-hat o-hyb o-back` | `walk` (base; o-back: the hand walk) `libc loop v1 none` | item 3 (+ NONE, rev3 C8: an extra arm of the gap groups, no item 4): DFA_SCAN fwd / bounded, DFA_HAT, HYB_PF, DFA_ATTEMPT back (rev 3's name for ATTEMPT_PRED); `libc` is the artifact as the compiler emits it, the others replace only the `memchr` call (`mkvar2.py ob`); `none` deletes the use's FIND |
| `o-vm` (`xy+z`, `--engine=vm`) | `walk` (base: `--memfn=no-pf-terms-mask`, the table walk) `libc v1` | item 3v [rev3 A7]: VM_ATTEMPT, the VM hat's seek at \|S\| = 1 (`RX_VM_START_SCAN "first-class"`); `v1` is the compiler's own default V1 text (stateful), `libc` is evidence only (Q-R5's per-attempt memchr); 6 gaps + 4 lengths (`mkvar2.py vm`) |
| `trig-dig trig-word` | `keep` (base) `drop` | item 8: default compile vs `-fno-req-byte -fno-req-run` |

Subjects are directories of distinct buffers under `subj/` (`.manifest.tsv` carries every
buffer's sha256): `streamgen.py` fixes the size at 4 MiB of distinct data per subject (64 x 64 KiB;
16 buffers at 1 MiB; at most 1024 buffers for tiny n; `GRID2_STREAM_MIB=64` restores grid1's 64 MiB, ~0.95 s per launch instead of ~0.63 s), the same generator `regime_eval` E4
imports (`write_stream`, `verify_stream`, `disjoint`, `window_stream`, `nbuf_for`).
`fit_map.tsv` maps every grid1 fit group to its grid2 streamed group.

## DRY

`DRY=1 bash slot.sh <dir>` runs the WHOLE pipeline on a tiny subset (2-3 groups per item,
`design2.py --dry`), 1 launch, no rerun, no quiet wait (`LOADMAX=999`: a dry reading is NOT a
measurement), clocked end to end, in a few minutes; then `estimate.py` prints the wall estimate
of the full slot from its own per-launch costs into `dry_estimate.txt`. `NOCLOCK=1` (time.sh)
is grid1's old DRY: the loop with no clock.

## The suggestion (D166 add. 1.1)

When user-space counters are unavailable, `slot.sh`, `time.sh` and `f2perf.sh` print to their
log and to the pass's status file the current `kernel.perf_event_paranoid` (`?` if unreadable),
that 2 or lower enables the optional pass, what it adds, and the two commands, and write
`counters skipped:perf_event_paranoid=N` to `provenance.txt`. They never run `sysctl` or `sudo`
and never write under `/etc`. `paranoid_check.sh` holds all of it (forced probe failure through
all three scripts, the provenance line, the positive control, a scan of every script, four plants).

## Files

| file | role |
|---|---|
| `slot.sh` | the slot: build, check, phases, status |
| `build.sh`, `check.sh`, `time.sh`, `f2perf.sh` | the stages (wrap or fork grid1's) |
| `design2.py` | the design (items), subjects, the libpcre2 oracle, counts |
| `streamgen.py` | the streamed subject generator (also E4's) |
| `mkvar2.py` | the new variants: `disp`, `scaf`, `ob` (libc/walk/loop/v1/none) |
| `ext_ob/build.sh`, `ext_trig/build.sh` | the ext sets' builders (copied into `<slot>/ext/<name>/`) |
| `paranoid.sh`, `paranoid_check.sh` | the counter suggestion and its check |
| `provcheck.py` | [rev3] the compiler record, the arm-signature leg P, the manifest census M |
| `plants.sh` | the failing direction of the gate for the new arms and the rev-3 items (13 plants) |
| `estimate.py` | the full-slot wall estimate from a dry run |
