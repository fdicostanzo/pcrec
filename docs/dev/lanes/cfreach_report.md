# cfreach: triage of job 704-corefix-reach (corefix @ eb0f223d9)

## Verdict
The red is mostly a job-script artifact. ONE real finding remains, and it is
not a stale anchor.

1. BASE RUN INVALID (rc=2). `build/cf/base` is a git-archive copy with no
   `.git`; the matrix measured the lane's SHA (eb0f223d9), cloned a "clean
   reference tree" from it and failed `make: No rule to make target 'all'`
   (FATAL: CLEAN reference tree does not build). So "base unreached: 0" is
   meaningless. Fix for a re-run: base must be a real git worktree of a53296894.
2. 15 OF THE 16 NAMED ROWS ARE FALSE POSITIVES. The job greps `UNREACHED`
   and so also counts rows printed as `declared-UNREACHED` (expected, by
   design: S1029 S1126 S1160 S121 S475 S479 S496 S497 S685 S891 S895 S901
   S904 S917 S919). The lane's own trailer: `rows=907 reached=456
   unreached=1 declared-unreached=15 now-reached=0`. The stray `***` line is
   the "NOT declared UNREACHED" banner. The job should compare on the
   `NOT declared UNREACHED` list (or trailer `unreached=`), not the word.
3. THE ONE REAL ROW: S191-sizeterm-greedy-descent
   (`reach:MISSING(1/2)`; probe expects `RX_UNROLL_K 1`, lane stamps 2).
   NEST8 (`((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,8}(){2,3}){1,2}){2,3}`,
   contains the K128 shape `(){2,3}`) now gets K=2 from the size term;
   main a53296894 gets K=1. Same stamp why (`size-model`). Artifact bytes
   on the lane: K=1 50035, K=2 94953, K=3 192340, K=4 158380; main K=1 48940.
   So the term picks the rung that ships 1.9x the bytes of K=1.

## Not a stale anchor
Not a moved plant site (compile.c's argmin loop is untouched). The witness
moved because the chosen K moved. The same shift fails
`tests/codegen/run_size_term.sh` section 3 on the lane:
`FAIL: the size term chose a K the artifact does not carry: '2'`
(log: build/cf/size_term.log). The 704-corefix-test job will be red there.

## STOP (per the brief's stop rule)
I did not re-pin K to 2: that would accept a size regression nobody ruled
on. `vm_emitted_nodes` (the trial-emission node count the argmin reads,
compile.c ~3067/3119) apparently no longer ranks K=1 below K=2 although the
bytes do, after K128 (last mandatory copy seeds the guard). Needs a ruling:
either K=2 is the accepted K128 mover (then re-pin run_size_term.sh section 3,
S191's SAB_REACH_EXPECT and SAB_DOC_FIGURE to K=2, and re-run S191/S192/S701
whose docs also name NEST8's K) or the node accounting needs a look.
No source or test file was changed by this lane.
