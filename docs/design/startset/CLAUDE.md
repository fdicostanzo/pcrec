# docs/design/startset/ — START-SET's census and hand twins

Reproduction pieces for `../startset.md` (lane `startset`, 2026-10-05, abi 61).
Compile-side and answer-only, except `twin/tdrv.c`, which gives Mac SCRATCH
timings (directional only, D144 addendum 1). pcrec-bench is read, never
written.

- `fs_probe.c` — the AST START SET probe. It links `build/libpcrec.a` and
  reconstructs the pipeline prefix (parse, altcls, discharge_atomic,
  lower_enc). It prints, per `id<TAB>hexpattern` line: nullable, popcount, the
  256-bit set, and the continuation-byte count. Zero-width nodes are ∅ and
  nullable; backreferences, calls and variables are all-256 and nullable (the
  note's §3.1 table). Build:
  `gcc-16 -O1 -std=gnu11 -Ilib -Isrc -o fs_probe docs/design/startset/fs_probe.c build/libpcrec.a`.
- `census.py` — the D77 census. For every bench export and every DISTINCT
  corpus pattern it records: `--emit-facts` stamps and facts at `auto` and at
  `--engine=vm`, the auto artifact's `can_begin_match` set and seededness, and
  `fs_probe`'s set. Env: `PCREC PROBE CORPUS OUT [BENCH JOBS]`. It passes
  pattern BYTES on argv. Its first run passed a latin-1-decoded str, which
  Python re-encoded as UTF-8, so 33 non-ASCII patterns compiled as different
  patterns. The control below caught it.
- `summarize.py` — classifies `census.tsv` into the populations in the note's
  §1. It runs THE INDEPENDENT CONTROL: `E ⊆ S` on every unseeded machine, plus
  a drop-one-member failing-direction twin. It checks capability `t-1m`'s
  sha256 against the bench manifest before reading densities. [Rev 2,
  review r4 sound-F2/checks-F2: the drop-one twin is a tautology, since
  `min(E) ∈ E`. The population has no seeded machine, so it cannot reach
  either hat's movers. Superseded as a control by `rev2/control.py`. Its
  DFA_NARROW count also included 14 rows where `S ∩ E = ∅`.]
- `census.tsv`, `census_summary.json`, `census_summary.txt` — its output at
  `a4c752a2` (abi 61). No check reads these.
- `twin/` — the hand twins, all answer-checked every-startpos differentials:
  - `hybtwin.py` + `drv_hyb.c` → `hybtwin_out.txt`: the VM hybrid's inlined
    prefilter, narrowed with and without the re-seed;
  - `dfatwin.py` + `drv3.c` + `run_dfatwin.sh` → `dfatwin_out.txt`: the DFA
    hat (narrowed to `T = S ∩ E`, with and without the re-seed). [Rev 2:
    every pattern here has `S ⊆ E`, and the script computes `T` by the
    formula under test, so it could not see sound-F1. See `rev2/`.]
  - `vmtwin.py` + `drv2.c` + `run_vmtwin.sh` → `vmtwin_out.txt`: the VM hat's
    entry/retry seek. It is encoding-agnostic: it inserts the seek after the
    backend's own advance. It carries the drop-one-member CONTROLS;
  - `tdrv.c`: the find-all scratch timer, base against twin, best of R.

  Env for the `run_*.sh` scripts: `PCREC PROBE W` (a scratch dir) `[CC]`.
  [Rev 2, sound-F5: `vmtwin_out.txt`'s `(?i)stra\x{df}e` CONTROL line reads
  `diffs=0` but re-runs as 1. The `(a+)x\1catdog` row is vacuous at maxlen
  6. Every driver here reads subjects with `fgets`, so no newline is
  reached.]
- `rev2/` — revision 2's instruments (lane `ssrev`): the seeded-machine
  sweep of the DFA-hat set options (a)/(b)/(c), the start-byte oracle on
  both hats, and C-SS\* with planted walk defects; `out/` has the
  transcripts. Own CLAUDE.md.
- `edge/` — §6.4's instruments (lane `ssedge`): the DRAFT edge cells (80
  blocks, 2,070 cells, every answer libpcre2's, 10.48 == 10.46), the
  option-aware start-set probe, the hand twins of the correct hats and of
  every wrong variant D148 addendum 1 lists, the mutation run, the re-seed
  form searches and their transcripts. Own CLAUDE.md.
- `s1/` — STAGE 1's census (lane `ssbuild01`): the D77 census re-run on the
  BUILT `start_set` fact with per-block options, and the generator of the
  stage-2/3 mover manifests (`tests/startset/manifests/`). Own CLAUDE.md.

- `s2/` — the census re-run at stage 2 (lane ssbuild2), which regenerated
  `tests/startset/manifests/` when the stage-2 fixtures joined the corpus.
  Own CLAUDE.md.
- `s3/` — the census re-run at stage 3 (lane ssbuild3) with the PRE-STAGE-3
  compiler, which regenerated `tests/startset/manifests/` when the DFA-hat
  fixtures (`dfahat.rxt`, `reseed.rxt`, `hybrid.rxt`, `dfahat_paths.rxt`)
  joined the corpus. Own CLAUDE.md.
