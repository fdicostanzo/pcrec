# lxread — the 2026-10-05 Linux results, read and archived (lane lxread, opus, read-only)

Read lane lxrun's serial quiet-box driver on ubuntubudu (`scratch_lx/run_lx1005.sh`: K82 alpha, the
[MEMFN] `linux_run.sh` + twins, L-4/L-2, the x86 survey; all RC 0) and landed it. Nothing was run on the
box beyond light reads (two artifact diffs, one python match count over the alpha's subjects, an
`objdump` recount of the L-2 binaries, tool versions); its `make mech` was left untouched.

Deliverables:
- `docs/dev/lanes/k82alpha_report.md` + transcript `docs/dev/optloop/s4/k82alpha_lx.txt`. K82 (A)+(C):
  `userpass` cured (-0.93 ns/B, = pre-C3), `alt-shared` ~80% recovered, C3's customers and cause (B)
  unchanged, one regression past the floor — `cls-n-uc` +0.025..+0.031 ns/B (the set-leads `memchr('m')`
  never rejects on match-dense text) — drafted there as K85 for the manager to file.
- `docs/design/memfn/linux_results.md` — every owed [MEMFN] Linux question answered beside its Mac
  number, a <=12-line decision-inputs summary for Q2/Q4-Q17, per-question answers (§8) and the
  corrections owed to requirements/isa_evaluation/twins/survey (§9, not edited by this lane).
- Archive: `docs/design/memfn/probes/out/linux/` (+ `twins/`), provenance-headed; lxrun's scripts in
  `docs/design/memfn/probes/lxrun/`; CLAUDE.md entries in each.

Instrument defects found and read around (not fixed — the scripts are archived verbatim):
`isanote.sh`'s source-note bits are one level too high (`(1 << (lv + 1)) - 1`); `memfn_l2.sh`'s `ev()`
is called with one argument under `set -u`, so its ymm/BMI counts printed nothing (recounted).

Open for the manager: file K85 (or not); the L-2 `paren-rec` +34.5% v3 loss is undiagnosed; PCRE2-JIT
10.46 not vectorizing `[XYZ]`/`[0-9]` on this build contradicts survey.md §4.12 and wants one light probe.
