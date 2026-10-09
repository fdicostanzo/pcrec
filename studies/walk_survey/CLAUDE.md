# studies/walk_survey/ — the gratuitous-walk survey (lane walksurvey, 2026-10-09)

Frank, 2026-10-09: "do a survey of existing patterns and see if there is another
class where we are doing gratuitous walks besides the end anchored ones."
SURVEY + MEASUREMENT ONLY: nothing under `src/` changes. The findings, the
ranked class table and the filing suggestions are `docs/dev/walk_survey.md`;
this directory is its instrument, populations, drivers and verbatim results.
Never built or run by pcrec's `make`. Box: the Linux dev box (Ryzen 7700X,
gcc 15.2), pcrec at the lane's main (`5e23b90c`, abi 71); pcrec-bench read only
(a `git archive` of it, with its subject generators run IN THE COPY).

## The instrument

- `wsdrv.c` — the per-phase SUBJECT-LOAD counter. The artifact is compiled
  `-O0 -fsanitize=kernel-address --param asan-instrumentation-with-call-threshold=0`
  so every load becomes a call to `__asan_loadK_noabort`; this file defines
  those hooks (and interposes `memchr`/`memrchr`/`memcmp`/`memmem`, counted by
  the bytes their semantics examine). A load inside the subject buffer is
  counted and attributed to a PHASE through its call site (the hook's return
  address, looked up in the map wsbuild.py writes; a load inside a small
  non-inlined helper is attributed through the helper's caller). Per subject
  it prints: total loads `T`, unique bytes `U`, per phase `T_/U_/lo_/hi_/A_`
  (`A_` = bytes read past the call's match end, summed over calls), the
  pairwise phase overlaps, `T_scan` (bytes through the interposed scanners),
  `land_rev`/`land_calls` (reverse-pass bytes of calls whose match began
  where the forward machine first stepped). Regimes: `search` (one call at
  0), `findall` (the bench's loop), `match` (`rx_match_caps` at 0).
- `wsdrv5.c` — `wsdrv.c` plus `m_gap` (forward-machine bytes stepped before
  the call's match start; K12's measure). Selected by `WSDRV=wsdrv5.c`.
- `wsbuild.py PCREC OUTDIR [pcrec args]` — one instrumented artifact: pcrec
  (or a hand-made `WS_SRC`/`WS_HDR` pair), gcc, link, then the PHASE MAP from
  objdump call sites + `addr2line -i` + the emitted line's text
  (`classify()`; phases pre skip fwd rev anc vm endw misc up unk).
  `sites.tsv` lists every site with its phase, so the map is auditable.
- `validate.sh` -> `results/validation.txt` — the instrument's validation
  (a known gratuitous walk, its [OPT-REVEND] twin, two known tight walks,
  two PLANTED controls, gcov line counts as an independent count).

## Populations and runs

- `pop_bench.py BENCHCOPY` — every bench pattern export x its set's regimes x
  the subjects each regime sees (the loader's rule).
- `pop_corpus.py PCREC REPO SUBJDIR` — every distinct `.rxt` pattern block
  (own encoding and `i` flag) with its own m/n subjects and three synthesized
  16 KiB subjects (match near the end, at the start, none).
- `run_pop.py POP OUT [JOBS]` — builds and runs every pattern under the configs
  `default` and `nocaps` (`--no-captures`), plus `anch` (`\A(?:P)`, the
  anchored-attempt reference) where the match regime runs. Env: `PCREC`,
  `PROBE` (`docs/dev/optloop/revend/revend_probe.c` built against
  `build/libpcrec.a`: end view and widths), `WSDRV`, `CONFIGS`.
- `run_all.sh` — both populations at -j4 (writes `work/`).
- `bench_times.py REPORTS` — the bench's own set-grain pcrec medians per cell
  (newest report per set), used only to weight impact.
- `analyze.py RES_BENCH RES_CORPUS TIMES OUTDIR` — the classes K1-K12, their
  gratuitous-byte counts, the residual, the impact estimate; writes
  `summary.txt` and `cells_<pop>.tsv`. Its docstring defines every class.

## Hand-twins (scratch-tier timing)

- `landtwin.py IN.c OUT.c [--fixed W]` — K4 (start = the skip loop's landing)
  or K3 (start = end - W) twin of a DFA artifact; exact only under the stated
  pattern property, so every timing line carries a span checksum.
- `fatime.c` — uninstrumented find-all/search timing with a span checksum.
- `run_twins.sh` -> `results/twin_timing.txt` — K3/K4 twins vs today's
  artifacts, and the K5 cliff (the folded required-run gate vs
  `-fno-req-run-fold`).

## Results (verbatim)

- `results/validation.txt`, `results/twin_timing.txt`
- `results/summary.txt`, `results/cells_bench.tsv`, `results/cells_corpus.tsv`
  — analyze.py's outputs over the committed run (`results/res_*.tsv.gz` are
  the raw rows).

`work/` (gitignored) holds the artifacts, subjects and raw rows; regenerate
with `run_all.sh`. Regenerating moves every number in `docs/dev/walk_survey.md`.
