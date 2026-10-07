# docs/design/poss_arms_measurements/build — CLAIM-vs-MARK against the BUILT compiler

[ART-POSS-ARMS] build precondition (lane `possbuild`, sub-lane `possbuild-cm`,
2026-10-07). Same frozen predicate generators as `../rev21/` (poss_arms.md
§8.3a), run against `build/pcrec`'s real arms instead of the prototype's env
switches. Nothing here is built or run by `make`.

## Reproduce

    make -j16 && docs/design/poss_arms_measurements/build/run_build_claimmark.sh

(~50 s at JOBS=8; scratch in `<worktree>/build/cm/`, gitignored.) The script
refuses to run unless the four rev21 sha1s equal §8.3a's final values.

## Files

- `claimmark_build.py` — the COMPARISON, derived from `../rev21/r21_claimmark.py`
  (sha1 d2288d1a…). Changes: base = both arms denied
  (`-fno-poss-ctx-follow -fno-poss-bref-first`), armed = default; configs
  `AB`, `AB_legacy` (the rev-2.1 target rule, kept as a control), `Aonly`
  (deny B), `Bonly` (deny A); the prototype's SAB_*/A1_NOCC plant configs are
  dropped (no such switches in the build); and the owed instrument item:
  replicated copies of one target are keyed as ONE target (>= 2 ordinals
  flipped by the possessive spelling with identical strategy detail; MARK =
  all copies flipped). The generators/predicate are untouched.
- `pcre2test_shim.c` — a minimal `pcre2test -q` stand-in over libpcre2-8
  (10.46 here) for the generators' membership probes; the box has the
  library but no pcre2test binary.
- `run_build_claimmark.sh` — the driver above.
- `results/claimmark_build.out.gz` — full per-row TSV + #SUMMARY lines.
  `results/summary_and_5rows.txt` — the #SUMMARY lines and the 5 formerly
  unresolved rows.

## Known differences from the prototype run

The generators ran against libpcre2 10.46 (the box), the rev-2.1 record used
10.48: 43 A-family `utf,i` rows (`(\b\w)\W+\1` and siblings; U+212A vs `\W`)
get claim `no` here instead of `yes`/hi=1; their expectation was 0 either
way, so they are simply not selected (computed rows compared 32,994 vs 33,037).
