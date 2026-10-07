# memfn/tests/ — G2, the kit's own tests

G2 (integration.md §10.2, §14.6) checks the kit's rendered code against
G2's OWN scalar byte loop over a GENERATED predicate space, never against
another output of the kit's generator. Written D27-blinded (lane memfng2),
from the contract (integration.md §8.3, §14) and `memfn/include/memfn.h`
only, without the kit's source. The lane's report is `docs/dev/lanes/memfng2_report.md` (the
kit session moves it). Lane g2x extended it to the §15 site shapes (INTERIM,
`G2X_REPORT.md`, superseded); lane g2u folded that work onto the current G2
and added the row-contract checks: its report is **`G2U_REPORT.md`** here.

## The row contracts, as G2 tests them (lane g2u)

- **PENDING-ENFORCE.** A case whose correct outcome depends on the kit's
  SCHEDULED row-contract enforcement is counted in its own bucket, printed
  (`PENDING-ENFORCE cases: N`, per class), never a failure and never
  dropped. Classes (`g2.h` `G2_PEND_*`): `hook-nonident` (F1: non-identifier
  `s`/`n`/`lo`/`floor` text on a §15 shape), `miss-unstated` (`miss` NULL on
  a RETURN/ASSIGN site), `refusal-unnamed` (a missing-hook refusal whose text
  does not name the hook), `fn_ref-unstated` (a FUNC site with no `fn_ref`
  whose form still asks `fn_name`). PENDING sites render in PENDING-only
  batches (header `N sites, pending N`), so a rendering that does not
  compile costs only its own batch.
- **`G2_STRICT_HOOKS=1`** turns every PENDING case into a hard check:
  render + compile + answer as the reference, or a loud refusal naming the
  field (`miss-unstated`: the refusal only). It is the enforcement step's
  acceptance test.
- **The poison differential** (generator): per site, every field the
  contract says the site does not use is set to junk; the rendering must be
  byte-identical, or refused. A difference is bisected to the field
  (`FAIL poison`). The "does not use" table, with the clause per field, is
  in `G2U_REPORT.md`.
- **The semantic differential** (family `sem`): a seed site cloned once per
  value class of ONE field (miss's every spelling, hook style, floor
  NULL/"0"/text, on_miss_leaves, result_decl, use, table_ref, fn_ref,
  plan_hint, a term's need, empty, policy, consumer, comment gate, via),
  every variant answer-checked.
- **Per-form floors**: hard sites rendered and answer checks per reported
  form id (`FORMID` lines; ids opaque, only counted).

## Files

- **run_g2.sh** — the one command. It:
  - builds the generator against `build/libpcrec.a` with only
    `-I memfn/include`, then generates and renders the sites;
  - compiles the rendered text with gcc and clang, plus an ASan+UBSan
    build on the quick subject tier, and runs the driver;
  - runs the three planted-defect witnesses (W1-W3).
  It checks the `MF_MISS_N` token (miss_mode 4: every second text-"n" site
  by id) like any other miss value, against G2's reference (`g2_missv`),
  with its own floors (`FLOOR_MT_*`: sites by shape, answer checks) and a
  `G2 miss token` census line. Since g2u it also holds: the family floors
  (`FAM_FLOORS`), the per-form floors (`FORM_FLOORS`, `*_FORM_CHECK_FLOORS`),
  the poison and semantic floors, the libc leg (`MEMFN_LIBC` against `nm -u`
  of each batch at `-O0 -fno-builtin`, §R4.3.3), and W2 mutation 7 judged
  over the sites that read below the candidate (`*FLOOR_MUT7_NEG`, G1).
  It prints `checks passed: N` / `checks failed: M` and the population
  against its floors (K35). The floors are literals at the top of the
  script and share no source with the generator or the driver. It exits 0
  only when M is 0, every floor holds and every witness fired. Work files
  go under `$TMPDIR`; `--keep` keeps them; `--seed N` changes the
  generated space. Every step runs under GNU timeout.
  **`--quick`** (lane memfnfix) is `make test-memfn-g2`, a `make test`
  section, at 52-62 s wall on the Mac (two runs). It runs the same checks,
  judged by the same code, on a smaller population:
  - one compiler (gcc), every generated site, the quick subject tier;
  - ASan+UBSan and the witnesses W1-W3 on every `QUICK_STRIDE`-th
    (3rd) batch, through a runner-written `g2_all.c` that lists only
    those batches, all launched concurrently and judged afterwards;
  - the floors that scale are the `QUICK_*` literals beside the others.
    The alignment axis, which the quick subject tier samples 4 of 16,
    is the one coverage cell it does not require.
  The whole run, gcc + clang at full subjects with every witness on
  every batch (about 25 min on the Mac), is `make test-memfn-g2-full`,
  OPT-IN and never part of `make test`.
- **g2/g2.h** — G2's own site description (`g2_site`, `g2_pred`,
  `g2_term`), the per-call outcome (`g2_out`), the miss values, and the
  helpers the wrapped text calls (`g2_touch`/`g2_acc` for `on_cand`,
  `G2_EV` for the hook-purity style). It does NOT include `memfn.h`.
- **g2/g2_gen.c** — the generator, and G2's only kit caller. It generates
  the original space (family `base`), the §15 shape families (`ofs`,
  `ofsrun`, `stmt`, `onebyte`, `gate`, `setrest`, `vmrun`, each with and
  without `MF_D_RUN_OVERLAP`, then again with non-identifier hook text as
  PENDING), the semantic differential (`sem`), and the PENDING queue. The
  original space is:
  - term cells: every SET offset −8..8 × 12 set kinds; every RUN offset
    −3..8 × length 1..33 × mask NULL/0/1/2 free bits, plus offsets −8..−4
    at lengths 1..3;
  - the combo grid: 20 (op, form, handoff) combinations × empty outcomes
    × reverse × end_back;
  - ALL_PRESENT at widths up to 256 predicates;
  - random fill.
  Each site is rendered through `mf_emit`, or `mf_define` + `mf_use`
  (+ `mf_call`), wrapped in a test function, and written to a batch TU.
  The generator also runs the REFUSAL table:
  - out-of-enum values, bounds, and form/handoff mismatches;
  - missing hooks;
  - every (op, handoff, kinds) that `mf_vocab_has` declares absent;
  - the define/use lifecycle, and `mf_opts_check`;
  - (g2u) every refusal §R4.7 lists, the missing-hook refusals asserting
    the hook is NAMED, the sticky error, `mf_art_note_libc`, and F2's
    libc-record reproducer.
  It also runs the poison differential on every hard site.
  `--mutate K` is W2's text mutation.
- **g2/g2_ref.c**, **g2/g2_ref.h** — the REFERENCE, the independent
  control: one plain loop per operation, from §14.3-§14.7. It handles
  OPTIONAL terms by answering for every subset and keeping, per site, the
  subsets still consistent ("fixed when the site is emitted"). It calls no
  kit function, not even `mf_ref_*`. `--ref-defect K` (W1) makes it wrong
  on purpose.
- **g2/g2_driver.c** — the driver. Per site it builds subjects: lengths
  0..129, a planted hit at every offset or at sampled ones, near-misses,
  and random subjects, each with two (lo, floor) pairs. It runs each in
  three layouts:
  - U: a guard page at `s + n`;
  - L: a guard page just below `s + floor`;
  - A: an exact-size heap copy at alignment 0..15.
  It captures faults and prints the census: combinations × empty ×
  reverse × end_back, term cells, positive/negative outcome floors,
  lengths, hit offsets and alignments; per family, per semantic field, per
  form id; and the PENDING sites' own counts (never in the census).
  `floor <= lo` holds on every instance (Q-G2-6; clamped, counted). `--witness-overread` (W3) and
  `--mutants` (W2) are the witness modes.

- **g2/g2_k1.c** — K1: the kit's `mf_ref_*` reference functions against
  G2's own loops, written from the header's statement of what each
  answers. It covers every length 0..129 and alignment 0..15, with
  exact-size heap copies, so the ASan build sees an over-read. It is the
  only G2 file that links the kit's answers, and G2 never uses `mf_ref_*`
  as its oracle.

Triage: `G2_TRACE=<site id>` makes the driver print every call of that
site (layout U), with the subject.

## Not here yet

- The `moved` property test and the arm-differs property (§10.2). At R4a
  the kit has one row, so there is no second arm to differ from.
- Cross-target `-fsyntax-only` (`--target=`) and the kit's timed suite
  (K-5). No SIMD-on form exists to need them.
- The agreement check against `pcrec_cls_cube`, which needs pcrec's
  `tests/`.

The pcrec-side checks of the kit (C4, C5, C9-C17, the pins under
`tests/memfn/`) live in pcrec's `tests/`, not here.
