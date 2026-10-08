# memfn/tests/ — G2, the kit's own tests

G2 (integration.md §10.2, §14.6) checks the kit's rendered code against
G2's OWN scalar byte loop over a GENERATED predicate space, never against
another output of the kit's generator. Written D27-blinded (lane memfng2),
from the contract (integration.md §8.3, §14) and `memfn/include/memfn.h`
only, without the kit's source. The lane's report is `docs/dev/lanes/memfng2_report.md` (the
kit session moves it). Lane g2x extended it to the §15 site shapes (INTERIM,
`G2X_REPORT.md`, superseded); lane g2u folded that work onto the current G2
and added the row-contract checks: its report is **`G2U_REPORT.md`** here.
Lane g2m4 brought G2 to MF_SITE_ABI 6 (R-7, M4): its report is
**`G2M4_REPORT.md`**.

## The MF_SITE_ABI 6 contract, as G2 tests it (lane g2m4, `G2M4_REPORT.md`)

Written from memfn.h and integration.md (Q-R7-1/2/3) alone.

- **Q-R7-1, the read-bounded range.** `g2_ref.c`'s `g2_ref_range` /
  `g2_ref_readsbelow` are the ONE statement of the range: a FIND (not
  ON_CAND) whose every term has offset + len <= 0 (a SET term's len is 1; E
  the largest) takes candidates c in [lo, n] with c + d <= n, d = max(0,
  end_back + E), empty iff lo + d > n; every other site keeps [lo, n -
  end_back). The reference, the driver's `admit()`, its planting windows and
  the PF positive test all call it. The driver plants hits AT c == n on such
  sites and puts `lo` at the planted hit's edge (counted: `G2 read-bounded
  range`). The generator makes the contract's other facts true of such a site
  (render(): `miss` never `n`/`n - 1`, no span fact). W1 defect 4 is the OLD
  range in the reference: it must fail.
- **Q-R7-2, `MF_EMPTY_AT_N`** (`G2_EMPTY_AT_N`). The driver never calls an
  AT_N site with lo > n (`admit()`, counted) and never with a NULL subject
  (none of its layouts has one). The outcome on an empty scan is MISS's, so
  the reference needs no new branch. Reached by family **`mline`**, by the
  semantic field `empty` (class 3) and by two refusal cases (AT_N on ADVANCE;
  the value past AT_N out of the enum).
- **Q-R7-3, LOOP_EXIT** (`g2_site.loopx`, enforced class **`loop-exit`**).
  `on_miss` exactly `break;`. `wrap_loopx` (g2_gen.c) runs the rendered site
  inside a `for (;;)` THE WRAPPER owns and reports `missed` iff control did not
  fall off the end of the site: a break the kit's text pasted inside a loop or
  switch of its own leaves that one, the statements after it run, and the
  reference (a miss expected) fails the call. Outcomes: a site is rendered by a
  non-generic row and answers (rendered, run, hard), or refused naming
  `on_miss`; the GENERIC row rendering one is a failure (the form id is
  `generic`, as FORM_FLOORS already names it). W2 mutation 8 wraps the kit's
  text of every LOOP_EXIT site in a loop of its own: all must be killed. Seven
  refusal-table shapes (`LCASE`) are LOOP_EXIT sites G2 expects only the generic
  row to serve.
- **Family `mline`** (`gen_fam_mline`, own RNG stream and id range 700000):
  integration.md 15.7 [R-7]'s site, STMT / FIND / ASSIGN, one REQUIRED one-byte
  SET at -1, end_back 0, empty AT_N, floor the SAME text as lo (`floor_lo`; the
  driver passes fl == lo), a leaving on_miss (goto / return, or `break;`),
  no `miss`, no result_decl, no note; plus 14 one-thing-changed variants
  (`MLV_*`). The rows check (b) is green because this family reaches
  `arms/pf_memchr_back`; `FLOOR_ROWS` is 14.

## The row contracts, as G2 tests them (lane g2u)

- **ENFORCED CLASSES** (G2u3; formerly "PENDING-ENFORCE", renamed because
  nothing is pending: the kit's row-contract enforcement is in force; the
  `G2_PEND_*` identifiers and the batch header's `pending N` keep the old
  spelling). Four classes (a fifth, `pf-edge`, is the PF shape's, below, and a sixth, `loop-exit`, the LOOP_EXIT sites', above), each a named population with a floor
  (`FLOOR_CLS_*`) and a printed count (`ENFORCED-CLASS cases: N`, `class X: n`,
  generator `PENDBUCKET` lines, driver `G2 pending X:` lines):
  `hook-nonident` (non-identifier `s`/`n`/`lo`/`floor` text: must render and
  answer, or be refused naming the field), `miss-unstated` (`miss` NULL on
  RETURN/ASSIGN: refusal naming `miss`), `refusal-unnamed` (a missing-hook
  refusal must name the hook), `fn_ref-unstated` (a FUNC site with
  `site.pred.fn_ref` 0, any op: refusal naming `fn_ref`; where `miss` is also
  unstated on RETURN/ASSIGN, naming `miss` serves too). Sites of a class render
  in their own batches (a non-compiling rendering costs only its batch).
- **`G2_STRICT_HOOKS`**: the default is now ENFORCED (every class case is a hard
  check). `G2_STRICT_HOOKS=0` is a diagnostic only (bucket, never a failure).
  Base-space FUNC sites state a nonzero fn_ref (the term-cell sites always;
  others 15 in 16); the 1-in-16 explicit fn_ref-0 sample is class 4's population.
- **The poison differential** (generator): per site, every field the
  contract says the site does not use is set to junk; the rendering must be
  byte-identical, or refused. A difference is bisected to the field
  (`FAIL poison`). The "does not use" table, with the clause per field, is
  in `G2U_REPORT.md`.
  (g2pf) An UNSTATED (NULL) `note` hook is never poisoned: stating it makes a
  different site (the PF `stated-note` edge). `ret_pred` / `npred+preds` on a
  PF site moved the kit's text (KIT FINDING 1, `G2U_REPORT.md` section 9.5); fixed in the kit, green since G2pf2.
  Since the G2u2 addendum: a FUNC site's own name is ALWAYS `site.pred.fn_ref`
  (memfn.h K-1 ruling), so on ALL_PRESENT FUNC sites `pred.fn_ref` is never
  poisoned; every other member of `pred` there still is.
- **The semantic differential** (family `sem`): a seed site cloned once per
  value class of ONE field (miss's every spelling, hook style, floor
  NULL/"0"/text, on_miss_leaves, result_decl, use, table_ref, fn_ref,
  plan_hint, a term's need, empty, policy, consumer, comment gate, via),
  every variant answer-checked. Field `site-fn_ref` (G2u2): an ALL_PRESENT
  FUNC seed cloned over nonzero `site.pred.fn_ref` values; the rendered
  `g2f_<id>_<ref>` name must follow `fn_name(fn_ref)` (generator-side text
  check, `SITEFN checked=` line, `FLOOR_SITEFN`) and answers equal the
  reference.
- **Per-form floors**: hard sites rendered and answer checks per reported
  form id (`FORMID` lines; ids opaque, only counted).

## The PF shape (lane g2pf, `G2U_REPORT.md` section 9)

Family `pf`: the site shape integration.md 15.7 `[R4g]` says pcrec sends the
PF rows (FIND / STMT / ASSIGN over ONE REQUIRED SET term at offset 0, forward,
`result` the position), in four CELLS, each filled in a batch of its own (so
`MEMFN_LIBC` is judged and printed per cell):
1. one-member set, end_back 0, EXCLUDED, a LEAVING `on_miss` that reads no
   result (`on_miss_leaves` 1; goto or return), any miss spelling (NULL
   included: the miss is a wildcard there);
2. one-member set, end_back 1, EXCLUDED, no `on_miss`, miss the text `n - 1`;
3. multi-member set through `table_ref`, empty NOP, end_back 0, `result` the
   SAME text as `lo` (in place; `lo` > `n` is run too, Q-G2-1), miss
   `MF_MISS_N` or `n`'s text;
4. as 3 with end_back 1 and miss `n - 1`.
EDGES are the same cells with one thing stated that the cell leaves unstated
or in another class (a miss that is not the range's end, `result` not `lo`, a
stated floor / note / `result_decl` / `on_miss`). Which edge a site is comes
from G2's own fields (`pf_edge_mask`), so semantic-differential variants of a
PF seed classify the same way. An edge is the class `pf-edge` (the fifth
ENFORCED class): rendered and answer-equal, or refused naming the field.
The edge `table-disagrees` (table contents differ from the set bits) is a
caller defect: its answer is UNDEFINED, so the driver checks only that the
rendered code does not fault (`tabbad`), and a refusal is as lawful as a
rendering. The in-place reference is `g2_ref.c`'s `inplace` branch (empty NOP
leaves `lo` as passed; a miss leaves the miss value). PF sites draw from their
own RNG stream and id range (`pf_enter`/`pf_leave`), so no older site moved.

## The two entry paths (G2pf2, `G2U_REPORT.md` section 10)

They differ BY CONTRACT (memfn.h ROW CONTRACTS). `mf_emit` holds the use hooks at
selection and picks a serving form; `mf_define` + `mf_use` selects with the define
hooks and `mf_use`/`mf_call` REFUSE, naming the field, a use the form does not serve.
For a site with `via` 1/2 the generator tries define+use in a scratch art: a refusal
at use naming a field is LAWFUL and counted (`USEREFUSE`, `USEREFUSE-TOTAL`, floors
`FLOOR_USEREFUSE*`, unnamed must be 0); the site is then rendered and answer-checked
through `mf_emit`. A refusal at `mf_define` of a site `mf_emit` rendered fails.
Also (amended contract): with `on_miss_leaves` 1 on ASSIGN, `result` is UNSPECIFIED
on a miss: such sites take an `on_miss` that reads no result and `g2_ref.c` judges the
miss by `on_miss` having run.

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
  - ASan+UBSan and the witnesses W1-W3 (W2 mutation 8 runs on every pending-only batch,
    where the LOOP_EXIT sites live) on every `QUICK_STRIDE`-th
    (3rd) batch, through a runner-written `g2_all.c` that lists only
    those batches, all launched concurrently and judged afterwards;
  - the floors that scale are the `QUICK_*` literals beside the others.
    The alignment axis, which the quick subject tier samples 4 of 16,
    is the one coverage cell it does not require.
  The whole run, gcc + clang at full subjects with every witness on
  every batch (about 25 min on the Mac), is `make test-memfn-g2-full`,
  OPT-IN and never part of `make test`.
  **`--rows`** (implied by `--quick`; `--no-rows` opts out; report
  `G2ROWS_REPORT.md`): the per-ROW floor. Every kit-selecting process (the
  generator, once per W2 mutation) is linked against
  `build/libpcrec_mftrace.a`; its `MFTRACE REACH ... chosen=N` stderr lines are
  summed and printed as `row-chosen <table> <row> <n>`, derived from the trace
  only. Checks: (a) REACH_DROPPED 0, (b) every row n >= 1, (c) distinct rows >=
  the literal `FLOOR_ROWS`, (d) every process printed REACH lines; controls for
  (b) and (d) run each time. Cost over plain `--quick` is within noise.
- **g2/g2.h** — G2's own site description (`g2_site`, `g2_pred`,
  `g2_term`), the per-call outcome (`g2_out`), the miss values, and the
  helpers the wrapped text calls (`g2_touch`/`g2_acc` for `on_cand`,
  `G2_EV` for the hook-purity style). It does NOT include `memfn.h`.
- **g2/g2_gen.c** — the generator, and G2's only kit caller. It generates
  the original space (family `base`), the §15 shape families (`ofs`,
  `ofsrun`, `stmt`, `onebyte`, `gate`, `setrest`, `vmrun`, each with and
  without `MF_D_RUN_OVERLAP`, then again with non-identifier hook text as
  PENDING; and `pf`, the PF shape above, and `mline`, the M4 shape), the semantic differential (`sem`,
  with four PF seeds), and the PENDING queue. The
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
  `--mutate K` is W2's text mutation (K 8, lane g2m4: LOOP_EXIT sites only).
- **g2/g2_ref.c**, **g2/g2_ref.h** — the REFERENCE, the independent
  control: one plain loop per operation, from §14.3-§14.7. It handles
  OPTIONAL terms by answering for every subset and keeping, per site, the
  subsets still consistent ("fixed when the site is emitted"). It calls no
  kit function, not even `mf_ref_*`. `--ref-defect K` (W1; K 4, lane g2m4, is the OLD range for a reads-below FIND) makes it wrong
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
