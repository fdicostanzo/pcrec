# studies/n1budget/ — [LIM-2] N1's default-sizing measurement

See `n1_measure.c`'s own header for the full methodology, and this
directory's `CLAUDE.md` for the finding.

## Usage

    cd ../..            # repo root
    make CC=gcc-16       # build build/libpcrec.a first
    cd studies/n1budget
    make CC=gcc-16
    make sweep           # re-runs the full corpus + bench altwide sweep

`n1_data.tsv` (one row per pattern block: `id`, `route`, `refused`,
`subset_elems`, `raw_n_fwd`, `raw_n_rev`) and `n1_summary.txt` (the
population accounting and the MAX-over-non-refused-rows headline) are
regenerated in place by `make sweep`, not committed by that target — see
`studies/CLAUDE.md`'s "re-measure before load-bearing use" rule.

Machine/date context (D35 spirit): macOS arm64, gcc-16 16.2.0, measured
2026-09-04. Re-measure before load-bearing use elsewhere.
