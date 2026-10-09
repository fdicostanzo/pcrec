# studies/revend_twin/ — [OPT-REVEND]'s hand-twin (lane revdes, 2026-10-09)

The first owed step of the `[OPT-REVEND]` plan row: take emitted artifacts at
main (`de6acf09`, abi 70), replace the forward pass of `<prefix>_search` by
the reverse walk seeded at the subject end, check answer identity, and time
both. Backs `docs/design/revend.md` §6-§7. SCRATCH TIER: Linux dev box
(Ryzen 7700X, gcc 15.2, `-O2`), pinned to one core, load1 about 4 from a
concurrent chain. Never built or run by pcrec's `make`.

## Files

- `mktwin.py IN.c OUT.c PREFIX EOL`: the twin generator. Asserts every
  marker in the artifact's text and refuses rather than half-transforming.
  Since revision 2 (lane revrev) the walk sits at the HEAD of the search (the
  K50/K75 entry guards stay first; a PRESENCE pre-check is deleted under forms
  A/C and moved after the walk under form B) and a DEAD seed is skipped (X1).
  Forms (`TWIN_FORM`):
  - `exact` (form A, default): no forward pass; `<p>_match` from `s*` gives
    the end;
  - `lower` (form B, revision 1's choice): the walk sets `search_from = s*`
    and the body is untouched;
  - `walk` (form C, revision 2's primary): no forward pass; the seed that
    reaches `s*` is the end; a tie (both seeds) runs `<p>_match` once, or,
    where `_match` is the `search-filter` wrapper, hands `s*` to the body.

  Controls (`TWIN_SABOTAGE`): `noeol` drops the `n-1` seed; `firstseed`
  keeps the first accepting seed instead of the minimum; `nodead` drops the
  dead-seed check (run under ASan); `tien`/`tien1` (form C) take end `n` /
  `n-1` on a tie without the anchored run.
- `check.c`: answer-identity driver. It links artifact (`o`), twin (`t`) and
  libpcre2-8.
  - It covers every `search_from` in `[0, n+1]` on subjects ≤ 512 B. Longer
    subjects get a sample, with the oracle asked only at 0 and the last 8
    (libpcre2's interpreter is quadratic on the nullable shapes).
  - It runs a find-all loop for each subject.
  - utf8 oracle flags: `PCRE2_UTF | PCRE2_MATCH_INVALID_UTF`, no UCP.
  - Mid-character startpos cells (pcrec refuses them, K50) are compared twin
    vs artifact only.
- `timedrv.c`: interleaved artifact/twin timing. 20 calls x 15 rounds, min
  and median, and an answer-identity assert.
- `mksubj.py REPO OUT`: deterministic subjects, written to `work/subj/`:
  - pools harvested from `tests/assertions`, `tests/base` and `tests/utf8`
    `.rxt` subjects, plus hand edges;
  - ~1 MiB synthesized bodies;
  - the timing stand-ins for the bench's `t-tail-*-1m`, `t-1m` and
    `t-trim-nearmiss-16k`. They use the bench MANIFEST's described tails, not
    its bytes.
- `patterns.tsv`: 43 rows (name, encoding, eol, pattern). They are the
  bench's five tail patterns, the census's 24 DFA-routed class-U corpus
  witnesses, 6 edge shapes and 8 utf8 shapes.
- `controls.tsv`: the four patterns the sabotage controls run on.
- `run_check.sh`, `run_timing.sh`, `run_all.sh`: the drivers. Run them with
  `PCREC=build/pcrec ./run_all.sh`. They regenerate everything into the
  gitignored `work/`.
- `results/`: the verbatim outputs.
  - `check.txt`: form A, byte.
  - `check_utf8.txt`: form A, utf8. It supersedes `check.txt`'s utf8 rows,
    which used a UCP oracle by mistake.
  - `check_lower.txt`: form B, all rows.
  - `control_noeol.txt`, `control_firstseed.txt`: must be red, and are.
  - `timing.txt`: form A, 3 repeats, with load1 per line.
  - `timing_lower.txt`: form B.
- `.gitignore`: `work/` (generated artifacts, binaries, ~25 MB of subjects).

## Q1 (lane revq1, 2026-10-09): bounded patterns, W1 vs form B

Backs `docs/design/revend.md` section 10 Q1. Verdict and table: `q1_bounded.md`.

- `q1_patterns.tsv`: the 13 bounded end-pinned patterns with per-pattern tails.
- `mksubj_q1.py PATTERNS OUTDIR`: 1 MiB / 64 KiB prose bodies x {long, short, non, nl} tails.
- `timedrv3.c`: three-arm interleaved timing (`o` default/W1, `t` form B, `d`
  `-fno-end-window`) with a three-way answer assert.
- `run_q1.sh [CPU] [REPEATS]`: builds the three artifacts per pattern (B is twinned from the
  W1-denied artifact), runs `check.c` identity, then the timing passes into `work/q1/`.
- `q1_table.py TIMING.tsv`: renders the markdown table (medians, pass-median ranges, flags).
- `mktwin.py` (form B) now also twins artifacts that carry a REQ handoff: the
  `<p>_reqrun` pre-check (and its `c - K` back-off block) moves to after the walk.
- `results/q1_timing.tsv`, `q1_identity.txt`, `q1_table.md`: the verbatim outputs.

## Revision 2 (lane revrev, 2026-10-09): form C (walk-only), the panel fixes, four-arm timing

Backs `docs/design/revend.md` revision 2 (§6). Scratch tier, Linux dev box.

- `r2_patterns.tsv`: 18 new rows: six X1 trailing-lookaround shapes, eleven
  tie witnesses (one utf8), and `[a-z]{0,4096}\z` (the widest DFA-routed
  bound; 8192 falls back to the VM).
- `controls_r2.tsv`: the 9 patterns the five form-C controls run on.
- `run_r2_check.sh`: identity of forms C/A/B (and form C on
  `-fno-anchored-dfa` artifacts, label `walkNA`) over patterns.tsv +
  r2_patterns.tsv + q1_patterns.tsv (74), against the artifact and libpcre2;
  then the controls. Parallel (`P=`), per-job result files.
- `mksubj_r2.py OUTDIR`: the bench tail stand-ins on a body with NO `.txt`
  before the tail (X7), plus the `\s+$` tie cell, the `[a-z]{0,4096}\z`
  and `[a-z]{0,60000}\z` tails.
- `timedrv4.c`: four-arm (W1-today `o`, C `c`, A `a`, B `b`) interleaved
  timing; per-arm call count calibrated to ~100 us per round; the arm order
  rotates per round; answer assert across arms.
- `run_r2_timing.sh [REPEATS] [CPU]`: builds the arms (twins from the
  `-fno-end-window` artifact), picks the idlest SMT core pair, and runs
  REPEATS passes; each pass waits up to 5 min for load1 <= 2, and every row
  records load1 and the SMT sibling's busy fraction.
- `r2_table.py TIMING.tsv`: the markdown table (median of pass medians,
  [min-max of pass medians], C/W1, C/B, C/A).
- `results/r2_identity.txt`, `r2_controls.txt`, `r2_timing.tsv`,
  `r2_table.md`, `r2_meta.txt`: the verbatim outputs.
