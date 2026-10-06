# Cell for artifact A07 (capability_doubled_word)

capability/doubled-word, VM with captures (backreference), LOSING cell (~x1.9).  Pin: pcrec main 57db5152 (abi 62), gcc-16 (Homebrew 16.2.0) on a Mac M1.  Scratch tier only:
Mac numbers steer iteration and are never reported (charter 3.1).

You work ONLY inside this directory.  There is no src/, no design docs, no tests/ here by construction; do not
look for them elsewhere on the machine.  (This directory is its own empty git repository on purpose.)

## Where things are
- `build-artrev/capability_doubled_word/`  the artifact: `artifact.c` / `artifact.h` (the pin, never edit), `artifact.s`
  (gcc -O2 -S of the exact timed TU), `GENERATION.txt` (pin, abi, gcc, generation/asm/compile lines),
  `meta.json`, `arms/orig`, `arms/orig2` (the recompiled original), `iterations.tsv` (the bound ledger).
- `build-artrev/subjects/`  the subjects (below).
- `studies/artrev/`  the harness (README.md is the recipe); `docs/spec/`; `docs/dev/optloop/artrev/charter.md`
  (read sections 2, 3, 3.1, 3.2, 4 first); `docs/dev/optloop/artrev/notebook/` (earlier reviewers' notes; read
  every file present).
- `docs/dev/optloop/artrev/A07/`  YOUR deliverables: `review.md`, `leads.tsv` (header already there; the
  `origin` column is `fresh` or `notebook:<entry>`), the notebook entry goes to `notebook/capability_doubled_word-<you>.md`.
  Copy your sealed twin patches from `build-artrev/capability_doubled_word/twins/` next to them when you finish.

Subjects (build-artrev/subjects/capability/): t-64k.bin, t-256k.bin, t-1m.bin. These ARE the bench's
`large-subject-throughput` subjects for this cell (the cell's number is the find-all over these three).
Provenance: copied unmodified from the bench checkout's bench/capability/throughput/; sha256 equal to the
bench's own manifest_throughput.tsv (t-64k d2e4f134..., t-256k 3cf7b248..., t-1m ccbdf7eb...).

## Commands (from this directory)
    export ARTREV_CC=gcc-16        # the Mac's bare `gcc` is clang and is REFUSED
    A="python3 -B studies/artrev/artrev.py"
    N=capability_doubled_word
    $A twin $N null --null                       # the noise control, first
    $A twin $N L1 --new                          # copy of the original; edit build-artrev/$N/arms/L1/artifact.c
    $A twin $N L1 --seal                         # -> twins/L1.rN.patch, checked (SIMD/flag/artifact.h edits REJECTED)
    $A identity $N null --subject build-artrev/subjects/capability/t-64k.bin --subject build-artrev/subjects/capability/t-256k.bin --subject build-artrev/subjects/capability/t-1m.bin --corpus --battery 3000 --block 16 [--san]
    $A identity $N L1   --subject build-artrev/subjects/capability/t-64k.bin --subject build-artrev/subjects/capability/t-256k.bin --subject build-artrev/subjects/capability/t-1m.bin --corpus --battery 3000 --block 16 [--san]
    $A time $N --arms orig,null,L1 --subject t64k=build-artrev/subjects/capability/t-64k.bin --subject t256k=build-artrev/subjects/capability/t-256k.bin --subject t1m=build-artrev/subjects/capability/t-1m.bin --rounds 11
    $A ledger $N
`--corpus` finds 0 cases for this artifact (no corpus case carries this exact pattern/flags; measured in the full
tree at the pin), so identity rests on the supplied subjects, the generated battery and the libpcre2 sample.
`time` refuses without a PASS identity row for the arm's exact sha, refuses while the Mac suite lock exists
(`worktrees/.mac-suite.lock`, linked into this cell; ssbuild-class suites hold it for hours) and while load1 is
above 2.0 on this Mac; those refusals are correct behaviour, not bugs: wait or ask.  Timing runs are under
watchdog (10 min wall, 2 GB).  Bounds: 6 leads, 4 revisions per lead, 3 timing runs per revision, 6 hours total.
The three subjects are the whole cell; time all three (cell = the find-all over them).
Known harness limit: the "two reviewers never time at once" lock lives under THIS cell's build-artrev, so it does
not see another cell's run; the manager sequences timing between cells.
