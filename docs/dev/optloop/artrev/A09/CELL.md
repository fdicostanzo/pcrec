# Cell for artifact A09 (loglines_level_context)

loglines/level-context, hybrid (DFA gate + VM), LOSING cell (~x3.8).  Pin: pcrec main 57db5152 (abi 62), gcc-16 (Homebrew 16.2.0) on a Mac M1.  Scratch tier only:
Mac numbers steer iteration and are never reported (charter 3.1).

You work ONLY inside this directory.  There is no src/, no design docs, no tests/ here by construction; do not
look for them elsewhere on the machine.  (This directory is its own empty git repository on purpose.)

## Where things are
- `build-artrev/loglines_level_context/`  the artifact: `artifact.c` / `artifact.h` (the pin, never edit), `artifact.s`
  (gcc -O2 -S of the exact timed TU), `GENERATION.txt` (pin, abi, gcc, generation/asm/compile lines),
  `meta.json`, `arms/orig`, `arms/orig2` (the recompiled original), `iterations.tsv` (the bound ledger).
- `build-artrev/subjects/`  the subjects (below).
- `studies/artrev/`  the harness (README.md is the recipe); `docs/spec/`; `docs/dev/optloop/artrev/charter.md`
  (read sections 2, 3, 3.1, 3.2, 4 first); `docs/dev/optloop/artrev/notebook/` (earlier reviewers' notes; read
  every file present).
- `docs/dev/optloop/artrev/A09/`  YOUR deliverables: `review.md`, `leads.tsv` (header already there; the
  `origin` column is `fresh` or `notebook:<entry>`), the notebook entry goes to `notebook/loglines_level_context-<you>.md`.
  Copy your sealed twin patches from `build-artrev/loglines_level_context/twins/` next to them when you finish.

Subjects (build-artrev/subjects/loglines/):
  throughput/  t-{016k,064k,256k,1024k}-{fail,syslog,hit}.bin  -- the bench's TWELVE `large-subject-throughput`
               subjects for this set (the cell's number is the median over these twelve; `fail` = mixed log text with
               no member shape, `syslog` = single-source syslog stream, `hit` = same text with every member shape
               injected once per 4 KB), plus manifest_throughput.tsv.
  search/      s-000.bin .. s-111.bin -- the bench's 112 short-call (`search_short`, 279-3772 B) subjects, plus
               manifest.tsv. Not the pilot cell's regime; use them for identity and for a short-call sanity timing.
Provenance: regenerated with the bench's own gen_throughput_subjects.py / gen_subjects.py (committed default seeds),
run read-only with output to scratch; the regenerated manifests are BYTE-IDENTICAL to the bench's committed
manifest_throughput.tsv / manifest.tsv and all 124 files re-hashed to the manifest sha256 values.

## Commands (from this directory)
    export ARTREV_CC=gcc-16        # the Mac's bare `gcc` is clang and is REFUSED
    A="python3 -B studies/artrev/artrev.py"
    N=loglines_level_context
    $A twin $N null --null                       # the noise control, first
    $A twin $N L1 --new                          # copy of the original; edit build-artrev/$N/arms/L1/artifact.c
    $A twin $N L1 --seal                         # -> twins/L1.rN.patch, checked (SIMD/flag/artifact.h edits REJECTED)
    $A identity $N null --subject build-artrev/subjects/loglines/throughput/t-064k-fail.bin --subject build-artrev/subjects/loglines/throughput/t-064k-hit.bin --subject build-artrev/subjects/loglines/throughput/t-064k-syslog.bin --subject build-artrev/subjects/loglines/throughput/t-1024k-fail.bin --subject build-artrev/subjects/loglines/throughput/t-1024k-hit.bin --subject build-artrev/subjects/loglines/search/s-000.bin ...   # any/all of the 124 files --corpus --battery 3000 --block 16 [--san]
    $A identity $N L1   --subject build-artrev/subjects/loglines/throughput/t-064k-fail.bin --subject build-artrev/subjects/loglines/throughput/t-064k-hit.bin --subject build-artrev/subjects/loglines/throughput/t-064k-syslog.bin --subject build-artrev/subjects/loglines/throughput/t-1024k-fail.bin --subject build-artrev/subjects/loglines/throughput/t-1024k-hit.bin --subject build-artrev/subjects/loglines/search/s-000.bin ...   # any/all of the 124 files --corpus --battery 3000 --block 16 [--san]
    $A time $N --arms orig,null,L1 --subject fail64k=build-artrev/subjects/loglines/throughput/t-064k-fail.bin --subject hit64k=build-artrev/subjects/loglines/throughput/t-064k-hit.bin --subject syslog64k=build-artrev/subjects/loglines/throughput/t-064k-syslog.bin --subject fail1m=build-artrev/subjects/loglines/throughput/t-1024k-fail.bin --rounds 11
    $A ledger $N
`--corpus` finds 0 cases for this artifact (no corpus case carries this exact pattern/flags; measured in the full
tree at the pin), so identity rests on the supplied subjects, the generated battery and the libpcre2 sample.
`time` refuses without a PASS identity row for the arm's exact sha, refuses while the Mac suite lock exists
(`worktrees/.mac-suite.lock`, linked into this cell; ssbuild-class suites hold it for hours) and while load1 is
above 2.0 on this Mac; those refusals are correct behaviour, not bugs: wait or ask.  Timing runs are under
watchdog (10 min wall, 2 GB).  Bounds: 6 leads, 4 revisions per lead, 3 timing runs per revision, 6 hours total.
The cell is all twelve throughput subjects; for SCRATCH iteration a representative handful is fine (the confirmer re-times the full cell). Label the subjects; the first one given is the cell's own.
Known harness limit: the "two reviewers never time at once" lock lives under THIS cell's build-artrev, so it does
not see another cell's run; the manager sequences timing between cells.
