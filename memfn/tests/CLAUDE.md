# memfn/tests/ — G2, the kit's own tests

G2 (integration.md §10.2, §14.6) checks the kit's rendered code against
G2's OWN scalar byte loop over a GENERATED predicate space, never against
another output of the kit's generator. Written D27-blinded (lane memfng2),
from the contract (integration.md §8.3, §14) and `memfn/include/memfn.h`
only, without the kit's source. The lane's report is `docs/dev/lanes/memfng2_report.md` (the
kit session moves it).

## Files

- **G2X_REPORT.md** — lane g2x's (INTERIM) report: the shape families, their counts, findings F1/F2, the owed mutation-7 remedy.

- **run_g2.sh** — the one command. It:
  - builds the generator against `build/libpcrec.a` with only
    `-I memfn/include`, then generates and renders the sites;
  - compiles the rendered text with gcc and clang, plus an ASan+UBSan
    build on the quick subject tier, and runs the driver;
  - runs the three planted-defect witnesses (W1-W3).
  It prints `checks passed: N` / `checks failed: M` and the population
  against its floors (K35). Lane g2x added two legs:
  - the SHAPE FAMILIES' census: per family, sites rendered / refused /
    edge-refused, the form ids the kit reported (opaque: counted, never
    parsed), each family held to a rendered floor and a run floor
    (`FAM_FLOORS`), and a floor on distinct form ids (`FLOOR_FAM_FORMS`);
  - the libc record: each batch's `MEMFN_LIBC` stamp against `nm -u` of
    its `-O0 -fno-builtin` object (§R4.3.3's own control), `memcpy`
    aside.
  A batch whose rendered text does not compile fails every site in it
  and is linked as an empty batch, so the other batches still run. The floors are literals at the top of the
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
  the ORIGINAL space (family `base`):
  - term cells: every SET offset −8..8 × 12 set kinds; every RUN offset
    −3..8 × length 1..33 × mask NULL/0/1/2 free bits, plus offsets −8..−4
    at lengths 1..3;
  - the combo grid: 20 (op, form, handoff) combinations × empty outcomes
    × reverse × end_back;
  - ALL_PRESENT at widths up to 256 predicates;
  - random fill;
  - `on_miss_leaves` at both values on its ON_MISS/ASSIGN sites, drawn
    from a second random stream so the space is otherwise unchanged.
  Then the SHAPE FAMILIES (lane g2x, `g2.h` `G2_FAM_*`): the site shapes
  integration.md §15 says pcrec sends, generated densely, each once
  without and once with `MF_D_RUN_OVERLAP` (in batches whose art carries
  the same deny):
  - `ofs` (§15.1/§15.2): FUNC/FIND/RETURN over pcrec's SET+RUN
    conjunctions, offsets 0..~40, `miss` = the `n` hook's text or NULL,
    no floor, every plan_hint/plan_pos placement;
  - `ofsrun` (§15.1): one RUN term, every length 1..40 × offset 0..7,
    exact and case-folded, masked at one offset per length, sparse
    offsets to 40;
  - `stmt`: the same predicates as STMT ON_MISS/ASSIGN sites,
    `on_miss_leaves` 0 and 1;
  - `onebyte` (§15.3), `gate` (§15.5, the composite K82 gate),
    `setrest` (§15.4);
  - `vmrun` (§15.6, §R4.8.1 item 4): EXPR/VERIFY/BOOL,
    `guard_by_caller`, EXCLUDED, every length 1..40 × offset 0..8,
    exact, plus folded/masked/unsatisfiable.
  The families run again, sampled, with non-identifier hook text (styles
  1 and 2), one family per batch. A `miss` NULL site the kit refuses is
  counted EDGE (memfn.h names no default), never checked.
  Each site is rendered through `mf_emit`, or `mf_define` + `mf_use`
  (+ `mf_call`), wrapped in a test function, and written to a batch TU.
  The generator also runs the REFUSAL table:
  - out-of-enum values, bounds, and form/handoff mismatches;
  - missing hooks;
  - every (op, handoff, kinds) that `mf_vocab_has` declares absent;
  - the define/use lifecycle, and `mf_opts_check`.
  `--mutate K` is W2's text mutation.
- **g2/g2_ref.c**, **g2/g2_ref.h** — the REFERENCE, the independent
  control: one plain loop per operation, from §14.3-§14.7. An ALL_PRESENT
  ASSIGN whose `on_miss` leaves may miss with its result unwritten
  (§15.5: only the returned predicate's line writes it). It handles
  OPTIONAL terms by answering for every subset and keeping, per site, the
  subsets still consistent ("fixed when the site is emitted"). It calls no
  kit function, not even `mf_ref_*`. `--ref-defect K` (W1) makes it wrong
  on purpose.
- **g2/g2_driver.c** — the driver. Per site it builds subjects: lengths
  0..129, a planted hit at every offset or at sampled ones, near-misses,
  and random subjects, each with two (lo, floor) pairs. Every instance
  honours `floor <= lo` (RULED Q-G2-6, the caller's precondition on every
  site kind): an instance with a higher floor is brought to `lo`, counted,
  and no answer is checked past the contract's edge. It runs each in
  three layouts:
  - U: a guard page at `s + n`;
  - L: a guard page just below `s + floor`;
  - A: an exact-size heap copy at alignment 0..15.
  It captures faults and prints the census: combinations × empty ×
  reverse × end_back, term cells, positive/negative outcome floors,
  lengths, hit offsets and alignments, `on_miss_leaves` 0/1, and per shape
  family the sites, checks and positive/negative outcomes. `--witness-overread` (W3) and
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
