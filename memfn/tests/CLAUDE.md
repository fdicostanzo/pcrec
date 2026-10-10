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
Lane g2m7 brought G2 to MF_SITE_ABI 7 / MF_VOCAB 3 (R-8, M7: MF_OP_MISMATCH):
its report is **`G2M7_REPORT.md`**.
Lane g2m6 brought G2 to MF_SITE_ABI 8 (R-10, M6: the STRIDED ADVANCE, `MF_MAX_TERM` 32):
its report is **`G2M6_REPORT.md`**.

## The SIMD family (lane r13, R-13, R4e' batch 1; MF_SITE_ABI 10)

NOT written blinded: lane r13 wrote the kit's rows and this family both, so
its independence rests on the oracle (G2's own scalar byte loop over the
bytes the generator chose) and the compiler, not on the author.

- **g2/g2_simd_gen.c** — the generator: the batch-1 site space (an
  offset-skip FUNC whose predicate is one RUN term: length 2..32, offset
  0..3, per-position exact / letter-case / one-bit / arbitrary masks, the
  scanned position a two-member cube; 1 in 7 under `MF_D_RUN_OVERLAP`) and
  its negative controls (`fn-memchr` scan, short span, PORTABLE policy,
  each row's deny, a second term, a run past the shape bound, a sink with no
  bracket ops), rendered with policy 0 through a sink that OFFERS
  `simd_open`/`simd_close` and counts the bracketed bytes. A second render
  of every site at pcrec's placeholder prefix and longest FUNC name
  measures its guarded bytes. Sites 0 and 1 are the constructed worst cases
  of `guarded_max`. Since lane rankuse (D157) every site also STATES a
  generated position ranking (`mf_pred.rank_*`) in one of seven modes (none,
  one entry on or off the scanned position, whole permutations led by it or
  by any position, the second entry at the run's ends, partial), rates with
  ties, entries past `rank_n` filled with positions a reader would choose;
  one site in five also tries a MALFORMED copy, which must be refused; and
  a `deny-kb` class (`--memfn=no-vrun-kb`). Writes `g2v_sites.c` and
  `g2v_meta.tsv` (the stated entries, the copy's verdict, the tie count).
- **g2/g2_simd.h**, **g2/g2_simd_driver.c** — the site table and the
  driver: G2's reference (first c >= pos whose run holds, a plain byte
  loop) against every rendered function, at every span length 0..2*32+T+8,
  no-hit near-miss subjects, a single hit at every candidate, multi-hit
  subjects along their restart chain and every pos, in an END-guard layout
  (`s + n` at a PROT_NONE page), a START-guard layout and every alignment
  0..31 (POISONED under ASan); a fault is a failure.
- **run_g2_simd.py** — the runner (run_g2.sh section 4a; alone:
  `python3 memfn/tests/run_g2_simd.py [--quick]`): each class's MEMFN_FORMS
  against a hand table; THE RANKING CHECK (rankuse): every rendered
  helper's whole-block loads, in order, equal the filter the kit's rule
  gives from the GENERATED entries (KA, then the first stated entry other
  than KA; KA alone under the deny), every malformed copy refused, floors
  per ranking mode and per filter shape (a KB, none, KB not the first
  entry, KB at the run's ends, a rate tie);
  guarded bytes against `tests/memfn/simd_bounds.tsv`,
  answers at x86-64 / x86-64-v3 / x86-64-v4 / `-mgeneral-regs-only` and
  ASan+UBSan, per-path execution floors (its OWN text instrumentation of
  the rendered file: entry fall-through, whole block, final block, verify),
  five plants per level (final-block guard, lane mask, lane order, verify
  skipped, reach one short) red where the level is live and green where it
  is compiled out, and no PDEP/PEXT/gather in any object. Under `--rows`
  its generator's REACH lines join the per-row sum (the SIMD rows are
  reached nowhere else: G2's other sinks offer no bracket ops).

## The MF_SITE_ABI 8 contract, as G2 tests it (lane g2m6, `G2M6_REPORT.md`)

Written from memfn.h (the ADVANCE hooks, RULED Q-R10-2..5), integration.md section 14 and 15.9's
contract sentences, and the cell's G2 files alone (the kit's source was not read).

- **The site** (family **`stride`**, `G2_FAM_STRIDE`, `gen_fam_stride`, own RNG stream and id
  range 1000000): STMT / SKIP / ADVANCE over W in {1,2,3,7,8,9,16,31,32} REQUIRED SET terms, term i
  at offset i, forward, `end_back` 0, `empty` NOP or EXCLUDED. `G2_MAXT` is 32 (the header's
  `MF_MAX_TERM`, 32 since ABI 8). The cap (`span_hi`, ITERATIONS) takes 0, 1, a middle value, one
  under / at / one over the longest run a 130-byte window holds, a bounded value no run reaches, and
  unbounded; the counter is none / kit-owned from 0 / kit-owned from 1 or 3 / caller-owned
  (`count_by_caller`), and a cap with no counter named gives the kit a counter of its own. Per-position
  sets are singletons, ranges, sparse, all full, mixed, one EMPTY position (first, last, middle) or one
  FULL position; neighbours always differ, so a term tested against another position's set is caught.
  The member hook is absent, pcrec's own read (`s[cursor + i]`, ignoring the byte expression the kit
  offers) or the byte_expr form (so the kit must OFFER the right byte). The cursor is spelled five ways
  (`cur`, `(cur)`, `g2c.pos`, `g2cv[0]`, `*g2cp`), `more` / `step` / `peek` four texts each (two outside
  the lexical classes CONJ / EXPR_STMT / POSTFIX), `s` plain or not; W = 1 also with `s` and `cursor`
  unstated. Non-identifier `s` / `cursor` texts are the enforced class **`hook-nonident`** and, unlike
  the other families, a REFUSAL there is a failure (`STNONID`: the generic row parenthesizes).
- **The reference** (`g2_ref.c` `g2_ref_stride`, a plain scalar byte loop from the generated sets; it
  calls no kit function): from the cursor `lo` it advances by W while the cap (counter, starting at
  `count_start`, < span_hi), `cursor + W <= n` and every `s[cursor + i]` in set_i hold. It returns why it
  stopped (cap / `more` / failing term and its position). W1 defects 8 (the cap counted in BYTES, span_hi / W
  iterations), 9 (`more` strict: the last exactly-fitting block dropped) and 10 (the terms in reverse
  order) must fail.
- **The subjects** (`g2_driver.c` `run_stride`): the window `n - lo` takes every value 0..130 up to 40
  and, above that, the residues W-1, 0 and 1 modulo W and every fifth, at `lo` 0 and at a random small
  `lo`; per window one subject whose every whole block holds, one per position i whose set is not full
  with a block that fails at exactly i (three in four with every other position holding, so a kit that
  ignores one term runs on), the failing block rotating over the first, the last, the middle and the one
  at the cap, and random subjects whose bytes mostly hold. The bytes of a partial last block HOLD. EXCLUDED
  sites are run only where a whole block fits (the range is non-empty).
- **Reads** (contract: only `[cursor, cursor + W)` per iteration, only while `more` holds): the driver's three
  layouts (guard page at `s + n`, under `s + floor` with floor == lo, exact-size heap at alignment 0..15) and a
  fourth, TIGHT: when the oracle's run ends because `more` is false, the guard page starts AT THE CURSOR
  (`st_tight`, `call_on`'s layout 0), so a read of a byte of the partial last block, which lies inside n,
  faults. Where the run ends by the cap or a failing term the kit may read the whole block and the next one
  (`more` holding), so the guard stays at n. `s` is NULL on alternate n == 0 calls. A call that does not
  return (a kit loop that does not end) is stopped by a 10 s alarm and is a failure.
- **Refusals** (`st_refusals`, generator; every one asserted, the field named where the header names it):
  `reverse` at W > 1; offsets not 0..W-1 or out of order (`pred`); an OPTIONAL term, a RUN term, a REF
  term (`pred`); nterm 33 / 34 / 255 (`pred` or `nterm`); a non-ADVANCE SKIP with nterm > 1 (`pred`; four
  forms x W 2, 3, 32); MF_SITE_ABI - 1 and + 1; `s`, `cursor` and both unstated at W 2, 3, 9, 32 with the
  member hook absent AND present (`s`, `cursor`); `peek`, `more`, `step` unstated; `count_by_caller` with
  `count` unstated. Controls render (W = 32, W = 1 with `s` / `cursor` unstated, a zero cap, both counter
  owners, W = 1 reverse). The cases the header leaves open (the whole predicate OPTIONAL, `end_back` 1)
  are reported (`INFO probe stride`), never judged.
- **Poison**: the existing differential covers strided sites; at W > 1 `cursor` is not poisoned (it is
  used), nor is `count_start` under a cap with no counter named.
- **K1**: `g2_k1.c` checks `mf_ref_skip_blocks` against G2's own loop (every W, a cap as the caller's
  `min(n, K * w)`, W = 1 against `mf_ref_skip_in_set`, exact-size heap copies).
- **Witnesses**: W1 8-10 above; W2 **12-16** (generator `--mutate K`, strided sites only, `--stride-only 1`):
  12 / 13 / 14 force the last / first / middle term to ALWAYS hold (the member hook text and, for the kit's
  own test, the set), 15 hands the kit a `more` that admits a block one byte short, 16 a cap one iteration
  too many; a site is mutated only where that is not an equivalent mutant (`st_is_mutated`: no EMPTY set
  anywhere, the term's set not full, a run long enough, the cap not already stopping the loop), and EVERY
  mutated site must be killed. W3 `st-partial` / `st-over` / `st-under` / `st-clean`: planted functions
  of one W = 3 site; `st-partial` reads a byte of the partial last block INSIDE n, which only the tight
  layout can fault.
- **Rows**: no new row; `FLOOR_ROWS` stays 15. Check (g) runs a generator process for the strided sites
  alone (`--stride-only 1`) and holds `arms/generic` to a floor over it.

## The MF_SITE_ABI 7 contract, as G2 tests it (lane g2m7, `G2M7_REPORT.md`)

Written from memfn.h, integration.md section 14 and 15.8's contract sentences, and
the cell's G2 files alone (the kit's source was not read).

- **MISMATCH / ON_DIFF / REF** (`G2_OP_MISM`, `G2_H_ON_DIFF`, `G2_T_REF`; family
  **`mismatch`**, `gen_fam_mismatch`, own RNG stream and id range 800000). A STMT
  site inside the wrapper: one REQUIRED REF term at offset 0, `empty` NOP, forward,
  `end_back` 0, `on_miss_leaves` 1. The run-time operand is two globals
  (`g2_mm_ref`, `g2_mm_reflen`, g2.h) the driver sets before every call. `result`
  is a local `size_t`, `o->res`, or a local `ptrdiff_t`; `on_miss` is a returning
  block or a `goto`, and READS the result into `o->cnt`, so the check sees the value
  at the moment `on_miss` runs.
- **The reference** (`g2_ref.c` `g2_ref_mismatch`): k = the least j in [0, reflen)
  with lo + j >= n or map[s[lo + j]] != map[ref[j]]; EQUAL when none. On EQUAL
  `on_miss` must not run and the result is not looked at. `lo > n` is a difference
  at 0 (reflen > 0), `reflen == 0` is EQUAL. W1 defects 5 (the fold ignored), 6 (the
  loop one byte short) and 7 (the result k + 1) must fail.
- **The maps are G2's own** (`mm_build`): the identity (fold NONE), and, for the
  ASCII relation and a Latin-1 relation (UCP: the ASCII pairs plus 0xC0-0xDE <->
  0xE0-0xFE without 0xD7/0xF7), the lower / upper / per-pair random representative
  (idempotent) and a random bijection after a representative (NON-idempotent). Each
  is spelled in BOTH text shapes (FOLD_EXPR, FOLD_STMT) by table, arithmetic, with
  other punctuation, or with a `'@'` literal that must be left alone. The reference
  compares `map[a]` with `map[b]` over the generated table; `g2mmchk_<id>` (emitted
  with the batch, run by the driver) holds the HOOK TEXT to that table over all 256
  bytes, so the text and the reference cannot drift apart unnoticed.
- **Read limits, guard pages on BOTH operands** (`run_mismatch`, `mm_instance`):
  `s` in layouts U (guard after s[n-1]), L (guard below s + lo), A (exact heap),
  N (lo >= n: s in PROT_NONE memory) and NULL at n == 0; `ref` in its own guard
  region (RU, RL, RA), NULL or a PROT_NONE pointer at reflen 0. Subject bytes below
  lo are the complement of the true bytes in U and A. ALIAS instances put ref inside
  the subject (before lo, at lo, overlapping), over a periodic fill with one planted
  difference. W3 gains five planted functions (`mm-ref-over`, `mm-ref-under`,
  `mm-s-over`, `mm-s-under`, `mm-clean`).
- **Refusals** (`mm_refusals`, generator): the header-derived list (reverse, end_back,
  each disallowed `empty`, a second or non-REF term, a REF term off 0 or OPTIONAL,
  `on_miss_leaves` 0 or 2, `on_miss` LOOP_EXIT or unstated, every unstated hook,
  `fold_kind` outside its enum or on a non-MISMATCH site, `fold` stated under NONE or
  unstated under ASCII/UCP or without an `@`, a REF term in every other op,
  MF_SITE_ABI + 1) and every (op, handoff, term kinds) combination `mf_vocab_has`
  declares absent, in all three forms. A field the header names must be named in the
  text; others are reported (`[names the soft field]`).
- **Poison**: a REF term carries no data (set/run/mask/run_len/table_ref are not
  read); the rendering with junk in them must be byte-identical (`MMPOISON`).
- **W2 mutations 9-11** (generator `--mutate`, MISMATCH sites only, no other family
  generated): 9 `reflen + 1` (must fault on the reference's guard page), 10 the subject
  as the reference, 11 a fold that does nothing (caseless sites). Every mutated site
  must be killed. `--mm-only 1` generates the MISMATCH family alone (the rows
  check (f) uses it to count the rows MISMATCH sites choose).
- **Rows**: `FLOOR_ROWS` 15 (`arms/mismatch_inplace`); check (f) floors
  `arms/generic` and `arms/mismatch_inplace` over the MISMATCH-only process.
- **Attribution of the guard-page witnesses**: an ALIAS puts `ref[reflen]` on the SUBJECT's
  guard page, and a NULL `ref` at reflen 0 faults on any read, so a fault alone does not
  say the REFERENCE's guard pages work. The W3 `mm-ref-*` witnesses and W2 mutation 9 therefore
  run without aliases (`mm_noalias`), and W2 9 is judged on `G2 mutants MISMATCH
  reference-guard faults` (non-alias, reflen > 0). Sabotage: a driver whose reference has no
  guard page turns W3 `mm-ref-over` / `mm-ref-under` and W2 9 red (`G2M7_REPORT.md`).

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
  (b) and (d) run each time. Cost over plain `--quick` is within noise. Lane g2m6 adds (g): a generator
  process for the strided sites alone (`--stride-only 1`), whose `arms/generic` count is held to a floor
  (`ST_ROW_FLOORS`); `FLOOR_ROWS` did not move. W1 is now defects 1-10, W2 mutations 1-16 (12-16 strided,
  judged "every mutated site killed"), and W3 gains the `st-*` witnesses.
- **G2M6_REPORT.md** — lane g2m6's report (the STRIDED ADVANCE): commands, totals, what is covered
  per charter item, rows, sabotage, the Q-G2M6 open questions, disclosure, charter checklist.
- **G2M7_REPORT.md** — lane g2m7's report (MISMATCH): commands, totals, rows,
  sabotage, the Q-G2M7 open questions, disclosure, charter checklist.
- **g2/g2.h** — G2's own site description (`g2_site`, `g2_pred`,
  `g2_term`; `G2_MAXT` 32), the per-call outcome (`g2_out`), the miss values, and the
  helpers the wrapped text calls (`g2_touch`/`g2_acc` for `on_cand`,
  `G2_EV` for the hook-purity style). It does NOT include `memfn.h`.
  Since lane g2m6: `G2_FAM_STRIDE` and the trailing `st_*` fields of `g2_site`
  (emitted as designated initializers, strided sites only).
- **g2/g2_gen.c** — the generator, and G2's only kit caller. It generates
  the original space (family `base`), the §15 shape families (`ofs`,
  `ofsrun`, `stmt`, `onebyte`, `gate`, `setrest`, `vmrun`, each with and
  without `MF_D_RUN_OVERLAP`, then again with non-identifier hook text as
  PENDING; and `pf`, the PF shape above, `mline`, the M4 shape, `mismatch`, the M7 shape, and `stride`,
  the M6 shape above), the semantic differential (`sem`,
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
  `--mutate K` is W2's text mutation (K 8, lane g2m4: LOOP_EXIT sites only). K 9-11 (lane g2m7) mutate MISMATCH sites' hooks and generate
  nothing else; `--mm-only 1` generates the MISMATCH family alone. K 12-16 (lane g2m6) mutate STRIDED sites
  only (the hard ones that mutation changes non-equivalently); `--stride-only 1` generates the strided family
  alone (and its refusal table).
- **g2/g2_ref.c**, **g2/g2_ref.h** — the REFERENCE, the independent
  control: one plain loop per operation, from §14.3-§14.7. It handles
  OPTIONAL terms by answering for every subset and keeping, per site, the
  subsets still consistent ("fixed when the site is emitted"). It calls no
  kit function, not even `mf_ref_*`. `--ref-defect K` (W1; K 4, lane g2m4, is the OLD range for a reads-below FIND;
  K 5-7 MISMATCH; K 8-10, lane g2m6, the strided ADVANCE's cap in bytes / strict `more` / reversed terms) makes it
  wrong on purpose. `g2_ref_stride` is the strided ADVANCE's oracle.
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
  `--mutants` (W2) are the witness modes. A strided site (`G2_FAM_STRIDE`) goes to `run_stride`
  instead (its own subjects, the fourth TIGHT layout, the `G2 stride ...` census lines and the
  `G2 stride census:` machine line the runner holds to floors).

- **g2/g2_k1.c** — K1: the kit's `mf_ref_*` reference functions against
  G2's own loops, written from the header's statement of what each
  answers. It covers every length 0..129 and alignment 0..15, with
  exact-size heap copies, so the ASan build sees an over-read. It is the
  only G2 file that links the kit's answers, and G2 never uses `mf_ref_*`
  as its oracle. Since lane g2m6 it also checks `mf_ref_skip_blocks` (the strided F5).

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
