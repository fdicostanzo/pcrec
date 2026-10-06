# [ARTREV] S4 confirm plan (lane artcollect, 2026-10-06)

The exact procedure for the FRESH confirmer lane (charter S4; sonnet; not the reviewer, not blind to
the harness, blind to the reviewers' timing numbers until its own are written). Nothing here has been
run on ubuntubudu: the collector only built and tested the tooling (`--dry-run` is refused by the
harness outside 08:00-19:00 local, and was not forced). The block below is executed by the confirmer
from a worktree of main + this lane's branch, on the Mac, BY DAY; the Linux box is touched only
through `artrev.py time --remote ubuntubudu`.

## 0. Before anything (gates the harness cannot see)

1. Ask the manager for a bench slot: the harness checks only the HOUR (08:00-19:00 local), never a
   declared bench window (memory `pcrec-bench-status`, window handshake). Read
   `/home/duxevents/pcrec-bench/docs/dev/outbox_to_pcrec.md`-equivalent on the Mac
   (`/Users/fdicostanzo/pcrec-bench/docs/dev/outbox_to_pcrec.md`) for a declared window; no write there.
2. Light, read-only probe (one ssh, tailnet address only): 
   `ssh -o BatchMode=yes duxevents@100.69.121.107 'cat /proc/loadavg; df -h ~ | tail -1; ls -d ~/scratch_lx/artrev/.timing.lock 2>&1; gcc --version | head -1; command -v gnutimeout python3'`
   Proceed only if load1 < 0.5, free disk > 2 GB, no `.timing.lock`, and `gnutimeout`/`python3`/`gcc` exist
   (the gcc version goes in the report: the bench compiles with the box's gcc, not the Mac's gcc-16).
3. Mac: no `worktrees/.mac-suite.lock` (the harness refuses local `time` under it; identity does not care,
   but do not run it beside a suite). Pre-flight of everything below with `--dry-run` at 08:00 or later:
   it prints the exact remote commands and runs nothing.

## 1. Rebuild the four pilot roots from the pin, import the final twins

    WT=/Users/fdicostanzo/pcrec/worktrees/<confirmer-worktree>      # merged main + lane/artcollect
    export ARTREV_CC=gcc-16 ARTREV_REMOTE_CC=gcc ARTREV_HOST_ROOT=/Users/fdicostanzo/pcrec
    export ARTREV_ROOT=$WT/build-artrev/confirm
    A="python3 -B $WT/studies/artrev/artrev.py"
    bash $WT/studies/artrev/confirm_prep.sh /Users/fdicostanzo/pcrec/build/pcrec $ARTREV_ROOT

`confirm_prep.sh` regenerates `loglines_stack_frame`, `capability_doubled_word`,
`loglines_level_context` with main's `build/pcrec` (abi 62) and ABORTS unless every regenerated
`artifact.c` has the sha256 in `pilot_pins.tsv` (verified in this lane: all three match), then imports
each reviewer's FINAL revision of every lead as an uncounted arm. Arms: A01 `L1..L4`; A07 `a_L1..a_L6`
(rvA07a) and `b_L1..b_L6` (rvA07b; `b_L4` is its r2); A09 `L1..L6` (`L1` = r2, `L4` = r3). Controls and
`null.*` patches are not imported; `null` is made by the script. Subjects (read-only; provenance and
sha256 in `pilot_setup.md`):

    LL=/Users/fdicostanzo/pcrec/worktrees/rvA09-cell/build-artrev/subjects/loglines      # A01 and A09 (same files)
    CAP=/Users/fdicostanzo/pcrec/worktrees/rvA07a-cell/build-artrev/subjects/capability  # A07
    # if the cells are gone: regenerate with the bench generators exactly as pilot_setup.md says, and
    # check the sha256 against its table before using them.

## 2. Identity, hardened, on the Mac, for every arm that will be timed

`time` refuses an arm without a PASS identity row for its exact sha. The hardened identity (shrunken
resources + the give-up rule, the window-start differential, the livelock bound) is the default. Run
PLAIN and `--san` for every arm; ZERO failures is the bar (a give-up REPAIR that equals libpcre2 is a
note, not a failure; report its count). Per the collector's table (`artcollect_report.md` section 3)
only the arms marked PASS go on.

    ss() { local s=""; for f in "$@"; do s="$s --subject $f"; done; echo "$s"; }
    D=$WT/docs/dev/optloop/artrev
    # A01
    for arm in L1 L2 L3 L4; do for san in "" --san; do
      eval $A identity loglines_stack_frame $arm $(ss $LL/throughput/*.bin $LL/search/s-*.bin $D/A01/edge_subjects/*.bin) \
        --battery 3000 --block 16 --match-example "'at a.b.c(Native Method)'" --match-example "'at com.x.Y.z(Y.java:42)'" $san; done; done
    # A07 (both reviewers' arms)
    for arm in a_L1 a_L2 a_L3 a_L4 a_L5 a_L6 b_L1 b_L2 b_L3 b_L4 b_L5 b_L6; do for san in "" --san; do
      $A identity capability_doubled_word $arm $(ss $CAP/t-64k.bin $CAP/t-256k.bin $CAP/t-1m.bin) --battery 3000 --block 16 $san; done; done
    # A09
    for arm in L1 L2 L3 L4 L5 L6; do for san in "" --san; do
      eval $A identity loglines_level_context $arm $(ss $LL/throughput/*.bin $LL/search/s-*.bin $D/A09/edge_subjects/*.bin) \
        --battery 3000 --block 16 --match-example "'ERROR x timeout'" --match-example "'CRIT timed out'" $san; done; done

Expected shape of the results (from the collector's own re-verification, `artcollect_report.md`
section 3): the A07 arms other than `a_L1`, `a_L6`, `b_L1` answer correctly where the original GIVES
UP under 0/1 frames or a shrunk step budget (they drop the frames or the steps), so they print a
large `give-up repair(s) of which N checked against libpcre2` count (hundreds of thousands under the
shrunk budgets): that is the permitted repair direction and is a PASS. Run each such arm ONCE more with
`--strict-giveup --skip-window` and record that it FAILS there: the report states "changes the limits
behaviour" for it (a caller who relies on `PCREC_ERR_FRAMES`/`_STEPS` giving up where the original did
sees a different answer; the rule treats the answer as the contract). A09 `L4`/`L6` should show 0 repairs at r3.

Expected wall on the Mac M1: about 1 min per plain call, 2-4 min per `--san` call; roughly 40-60 min in
all. Run it in the background with a log and read the `IDENTITY` lines, never a grep for words
(learnings section 3). Also `null` and a `--san` identity of `null` per artifact.

## 3. Variants (one dense, one sparse per artifact)

    V=$WT/build-artrev/confirm_variants; mkdir -p $V
    $A variants loglines_stack_frame    --subject $LL/throughput/t-1024k-hit.bin --out-dense $V/ls_dense.bin --out-sparse $V/ls_sparse.bin
    $A variants loglines_level_context  --subject $LL/throughput/t-1024k-hit.bin --out-dense $V/ll_dense.bin --out-sparse $V/ll_sparse.bin
    $A variants capability_doubled_word --subject $CAP/t-1m.bin                  --out-dense $V/cw_dense.bin --out-sparse $V/cw_sparse.bin

(dense = the original's own matches with 32 bytes of context each, cycled to the subject's length;
sparse = the subject with all but every 16th match broken; deterministic; the sha256 of both is printed
and goes in the report.) The cell's own `fail` and `syslog` subjects are the natural sparse points for the
loglines cells and stay in the cell.

## 4. Timing, in TWO passes per artifact (bounds: at most 3 timing runs per arm revision; this uses 2)

Pass 1 finds candidates cheaply (no pads); pass 2 re-times orig plus every pass-1 WIN/LOSS candidate
with the layout control, and ONLY pass 2 can produce a reportable verdict. `--cell` names the subjects
that form the bench's cell (the median over its subjects; the `CELL` row is the verdict row); dense and
sparse are extra rows (generality), never part of the cell. Rounds: 11, interleaved, load gate 0.5 on
Linux, `gnutimeout` and `scripts/watchdog` inside the remote wrapper, remote lock
`~/scratch_lx/artrev/.timing.lock`, cleaned up even on failure.

    # -- A01 (4 lead arms; combined twin: none, L1 subsumes L2-L4 per its reviewer)
    S=(); L=()
    for f in $LL/throughput/t-*.bin; do b=$(basename $f .bin); S+=(--subject "${b#t-}=$f"); L+=("${b#t-}"); done
    S+=(--subject dense=$V/ls_dense.bin --subject sparse=$V/ls_sparse.bin); CELL=$(IFS=,; echo "${L[*]}")
    $A time loglines_stack_frame --arms orig,orig2,null,L1,L2,L3,L4 "${S[@]}" --cell $CELL --rounds 11 \
        --remote ubuntubudu --wall 1500 --tag pass1
    #   candidates = arms whose CELL verdict (plain rule) is WIN or LOSS, or whose dense/sparse rows are
    #   (pass 2 for a lead that is NOISE on the cell but WIN on dense only is allowed, labelled 'regime-only')
    $A time loglines_stack_frame --arms orig,orig2,null,<candidates> "${S[@]}" --cell $CELL --rounds 11 \
        --pads 16,32,48,64,80,96,112 --pad-arms orig,<candidates> --remote ubuntubudu --wall 1500 --tag pass2

    # -- A07: both reviewers' twins in ONE run per pass (13 arms + orig2 + null; a_L4 = L1+L3 fused and
    #    b_L4 = L1+L2+L3+inline are the "combined" twins; b_L5/b_L6 and a_L5 are cumulative on top)
    S=(--subject t64k=$CAP/t-64k.bin --subject t256k=$CAP/t-256k.bin --subject t1m=$CAP/t-1m.bin \
       --subject dense=$V/cw_dense.bin --subject sparse=$V/cw_sparse.bin)
    $A time capability_doubled_word --arms orig,orig2,null,a_L1,a_L2,a_L3,a_L4,a_L5,a_L6,b_L1,b_L2,b_L3,b_L4,b_L5,b_L6 \
        "${S[@]}" --cell t64k,t256k,t1m --rounds 11 --remote ubuntubudu --wall 1500 --tag pass1
    $A time capability_doubled_word --arms orig,orig2,null,<candidates> "${S[@]}" --cell t64k,t256k,t1m --rounds 11 \
        --pads 16,32,48,64,80,96,112 --pad-arms orig,<candidates> --remote ubuntubudu --wall 1500 --tag pass2

    # -- A09 (six arms; L6 is the combined twin = L1 r2 + L3 + L4 r3 + L5)
    S=(); L=()
    for f in $LL/throughput/t-*.bin; do b=$(basename $f .bin); S+=(--subject "${b#t-}=$f"); L+=("${b#t-}"); done
    S+=(--subject dense=$V/ll_dense.bin --subject sparse=$V/ll_sparse.bin); CELL=$(IFS=,; echo "${L[*]}")
    $A time loglines_level_context --arms orig,orig2,null,L1,L2,L3,L4,L5,L6 "${S[@]}" --cell $CELL --rounds 11 \
        --remote ubuntubudu --wall 1500 --tag pass1
    $A time loglines_level_context --arms orig,orig2,null,<candidates> "${S[@]}" --cell $CELL --rounds 11 \
        --pads 16,32,48,64,80,96,112 --pad-arms orig,<candidates> --remote ubuntubudu --wall 1500 --tag pass2

Expected wall time on the box (each timed unit is about 0.05-0.08 s; arms x subjects x 11 rounds, plus
compiling every arm there first, about 2-3 s each, and the bundle copy): A01 pass 1 about 5 min, pass 2
about 10 min; A07 pass 1 about 6 min (15 arms), pass 2 up to 15 min (orig + candidates x 7 pads);
A09 pass 1 about 7 min, pass 2 about 15 min; so roughly 1 h 15 min of box time in all, all of it
inside one 08:00-19:00 day. The remote wrapper kills a run at `--wall` (1500 s) + 60 s; a firing
watchdog is a FINDING (say so), not a retry (a failed run still counts toward the 3-run bound). Run
each `time` command in the background with a log and poll the run dir (`timing/NNN_<tag>/`) for
`summary.txt`; never an idle wait beyond the cache window (BOILERPLATE DO-THEN-FINISH).

## 5. The verdict rule (the only numbers that enter the report)

On the `CELL` row of the pass-2 summary (and, as generality rows, on each subject):

- WIN: the arm's pad-median beats the original's pad-median by MORE than the largest of: the null
  twin's deviation from the original, the arm's IQR, the original's IQR, the arm's spread across pads,
  the original's spread across pads; AND the plain (unpadded) delta has the same sign; AND every PAIRED
  pad (`orig@pK` vs `arm@pK`) has the same sign. `summary.txt` prints all of these ("layout:" lines).
- LOSS: the mirror image.
- NOISE: anything else, including a plain-rule WIN that the layout control downgrades (the summary says
  "the pad control downgrades it": that sentence is itself a result worth a row in `confirmed.md`).
- A pass-1-only verdict is never reported as a WIN or LOSS; a lead that was NOISE in pass 1 is
  reported NOISE without pads. `orig2` and `null` must read NOISE on every row; if either does not, the
  run is invalid (load or layout), say so and re-run within the bound.
- Combined twins (`a_L4`, `b_L4`, `L6` of A09) are judged by the same rule; their per-mechanism shares
  come from the single-lead arms, as the reviewers asked (A07b: time L1 and L2 alone as well as the stack).
- Deliverables: per artifact `docs/dev/optloop/artrev/<A>/confirmed.tsv` (arm, lead id, CELL median
  ns/B, delta vs orig, threshold, spread, verdict, dense/sparse verdicts, the run dir) and one row per
  lead appended to `notebook/confirmed.md` (charter 3.2). Keep the raw `raw.tsv` of every run
  (committed under the artifact's directory; they are small).

## 6. What the confirmer must not do

No writes outside its own worktree (BOILERPLATE); no second timing run on the box while another holds
`.timing.lock`; no `--gate-override`/`--hour-override` (self-test only, refused otherwise); do not edit
a reviewer's twin (report FAIL/NOISE as it is); do not change flags (the one compile line is fixed:
gcc -O2 -fPIC, the box's `gcc`); never time a twin whose identity row is not PASS.
