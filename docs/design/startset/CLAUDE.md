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
  sha256 against the bench manifest before reading densities.
- `census.tsv`, `census_summary.json`, `census_summary.txt` — its output at
  `a4c752a2` (abi 61). No check reads these.
- `twin/` — the hand twins, all answer-checked every-startpos differentials:
  - `hybtwin.py` + `drv_hyb.c` → `hybtwin_out.txt`: the VM hybrid's inlined
    prefilter, narrowed with and without the re-seed;
  - `dfatwin.py` + `drv3.c` + `run_dfatwin.sh` → `dfatwin_out.txt`: the DFA
    hat (narrowed to `T = S ∩ E`, with and without the re-seed);
  - `vmtwin.py` + `drv2.c` + `run_vmtwin.sh` → `vmtwin_out.txt`: the VM hat's
    entry/retry seek. It is encoding-agnostic: it inserts the seek after the
    backend's own advance. It carries the drop-one-member CONTROLS;
  - `tdrv.c`: the find-all scratch timer, base against twin, best of R.

  Env for the `run_*.sh` scripts: `PCREC PROBE W` (a scratch dir) `[CC]`.
