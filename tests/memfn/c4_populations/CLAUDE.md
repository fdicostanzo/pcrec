# tests/memfn/c4_populations/ — C4's committed compiler populations

C4 (`../arch_blind_check.py`, `make test-memfn-arch`) plants each class's
vocabulary from the compiler it runs with. The Mac's compiler cannot show
gcc's own x86 target, and that blind spot let C4 pass on the Mac and fail on
ubuntubudu twice (2026-10-06: ABM/LAHF_SAHF; 2026-10-07: FP_FAST_FMA*). Each
directory here is one (compiler, target, box) population. `population_controls()`
plants classes 1-2 from it on EVERY run, on any box.

One directory per population, named `<compiler><version>-<target>-<box>`:
- `march_x86-64.txt` — the BASELINE `gcc -march=x86-64 -dM -E - </dev/null`,
  sorted;
- `march_*.txt`, `m_*.txt` — one `-dM -E` dump per ISA flag set. Everything
  a dump declares beyond the baseline is ISA vocabulary;
- `VERSION` — `gcc --version | head -1`;
- `native_target.txt` — `gcc -march=native -Q --help=target`, provenance only
  (not read).

- `gcc15.2-x86_64-ubuntubudu/` — gcc (Ubuntu 15.2.0-16ubuntu1), dumped on
  ubuntubudu by the pcrec manager's executor, 2026-10-07 (R4c, memfn R-4).

Add a population when a new verdict box or compiler joins. Regenerating one
moves nothing emitted; it can only add plants. The probe command is in
docs/dev/lanes/r4clx_report.md's addendum 2.
