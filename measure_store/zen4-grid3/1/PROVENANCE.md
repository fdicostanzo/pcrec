# zen4-grid3@1 — provenance

- **What it is.** The span_pick stage-2 card set (`docs/design/memfn/span_cards.md` §3.8, unit S2e; kit
  request R-35): format 2, method `kit-grid@3` (`memfn/data/cards/kit-grid.tsv`, ver 3, copied into the
  set's `cards` section), class `x86_64/zen4`, tier `scratch` (one box, a kit slot window, never an official
  bench run). 38 rows, 826 cells, outcome FULL (`partial` 0).
- **The run.** Run id `s2d-20261107a`: the second S2d timing window, 2026-11-07 01:34-01:59, AMD Ryzen 7
  7700X, CPU 7, gcc 15.2.0 `-O2 -march=x86-64 -mtune=generic`, glibc 2.43. The slot harness that timed it
  is `docs/design/memfn/span_cards/slot/` at the FROZEN commit `1e4999d1c3e88b98bff91d4a973c4a18ec3b4fdf`
  (the header's `code_commit`).
- **The run record.** `docs/design/memfn/span_cards/s2d2/run_record.tsv`, sha-256
  `d2c9fb97fb433d50b892731b8f28d315a6dccf70ff3b978ea78345721f15263b`, run id `s2d-20261107a`
  (`measures.md` §3.5¶8-¶9: the header's `run` value carries the same sha and run id). It holds the plan,
  every job's state (all six ran), J1's verdict (`c`) and its cells, the floor, the cards and policy the run
  pinned (`r_max_e6` 53751).
- **The per-round transcript.** Not committed (no row reads a round, `measure_sets.md` §1.5): kept at
  `/var/tmp/pcrec-pcrec/scratch/memfn/s2d/s2d-20261107a/transcript.tsv` on the dev box, sha-256
  `7d37b61dd7807150688815b3d0583f5675b50433b1e17b5ee9136693aba3e21c` (the record's `transcript_sha256`).
- **The estimator commit.** `fd75d411996d6bc5ec61cb4dd451211eedb3df61` (`slot/est.py` with review r11's
  fixes, span_cards §R1.5), the commit whose rules scored the record into the set (`measures.md` §3.5¶8a).
  Its draft's comment line: `# note est_commit: fd75d411996d6bc5ec61cb4dd451211eedb3df61, the estimator that
  scored the record (code_commit 1e4999d1c3e88b98bff91d4a973c4a18ec3b4fdf; the timed code unchanged between
  them)`. The draft refuses unless every path that differs between the two commits is non-timed by est's
  `NON_TIMED` table; it wrote the draft, so none is.
- **How it was written.** `python3 -I docs/design/memfn/span_cards/slot/est.py draft RUNDIR draft.tsv` at the
  est commit over a copy of the run directory (`diff -rq` equal to the original), then
  `pcrec --list-measurements=draft.tsv > set.tsv`, the canonical writer (canonical by construction; its
  comment lines, the est-commit note among them, are dropped). The draft's digest `2d2b3c0861443bec` equals
  window 2's re-score at review r11 (`span_cards/s2d2/r11_rows.txt`); the drafts differ in the est-commit
  note line only.
- **sha-256 of `set.tsv`:**
  `c84766ade779fda6867923d58e13a6aa7223ae7d9a48be8df1ab9b1593cee4e1`
  (also `../../index.tsv`; checked by `tests/knowledge/`).
- **The bound rows (fused-compare, `measures.md` §3.5¶3b).** `kit.verify_cmp.rc-memcmp.l1.p0`,
  `.l1.p50`, `kit.verify_cmp.settest.c1.p0`, `.c1.p50` carry the tag `fused-load-op`: in the timed code
  their compare is a load-op fused into the candidate load (`cmpl $imm,(%rdi,%rcx,1)`, `cmpb $imm,(...)`),
  so no base made by removing the compare is null. The fact was read by est from the object code of every
  launch executable the job's manifest pins (J4's manifest `b2a6af13...a98800`, not pinned by this record,
  which predates the pin: checked as it stands), by two readings (objdump's mnemonics and est's own byte
  decode) that agree, and it holds for no null base. Evidence: windows `s2d-20261106` and `s2d-20261107a`,
  two null bases, both negative; the arms-only fused/unfused step +0.14 wb
  (`docs/design/memfn/span_cards/s2d2/analysis.md`). All four medians are negative, so each value is 0 and
  each noise is `|med|` (116015, 105615, 119301, 107405 against `r_max` 53751). The STANDING RULE for these
  classes is span_cards §3.5 "Fused-compare classes".
- **`abs_ns_e6` beside a 0 value.** Five rows hold `value_e6` 0 beside a raw NEGATIVE `abs_ns_e6`: the
  four bound rows above (-22355, -20352, -22986, -20694) and the sub-resolution
  `kit.verify_cmp.settest.c2.p50` (-1942). `abs_ns_e6` is the UNCLAMPED `med(abs_l)` (ns x 10^6 per event),
  provenance only, read by no reader (`measures.md` §3.5¶3a, ¶3b): no digest, stamp, kit row or selection
  reads it (by grep at S2e: only the column-name table of `src/core/ks_measures.c`, the views that print
  it, `tests/knowledge/ks_ref.py`'s decode and the recompute's provenance compare).
- **D188's facts** (span_cards §2.7): one declared target, the generic one. (a) the box's cpuid list (the
  header's `isa`) holds the baseline's features; (b) every fixture was built for the declared target
  (`class x86_64/zen4`, inside the digest); (c) the rows price that target's scalar variant only. No SIMD
  variant is priced (S2g, HELD).
- **The embed.** `make gen-measures` embeds this set WITHOUT its `cells` rows (R-35 (d), `measures.md`
  §8¶2); `values_digest` never covered the cells, so the embed and this file share one identity
  `zen4-grid3@1:2d2b3c0861443bec`. `--list-measurements` reports the file's cell count (826) as
  `file_cells`. The recompute and `--measures=FILE` read this file.
- **What derives from it.** It is the `idk` default from DEFAULTS.log row 2 (span_cards §8.3, main's ruling
  (B)), with zero data movers (`../../movers/0002.tsv`). No kit row reads a set key in stage 2, so no artifact
  byte depends on its values and every `<PREFIX>_MEASURES` stamp stays `""`. Row 1 of span_pick is its first
  reader. `tests/knowledge/meas_recompute.py` re-derives every row, gate, drift verdict, J1's verdict, the
  floor and the outcome from this file and the run record.
