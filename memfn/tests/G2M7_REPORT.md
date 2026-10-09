# G2M7 — G2 brought to MF_SITE_ABI 7 / MF_VOCAB 3 (lane g2m7, D27-blinded)

Lane g2m7, 2026-10-08, Linux dev box, in the cell `worktrees/g2u-cell/`. Serves the
kit's request R-8 (M7: `MF_OP_MISMATCH`). Written from `memfn/include/memfn.h`,
`docs/design/memfn/integration.md` (section 14, and 15.8's contract sentences) and the
cell's own G2 files; the kit's source was not read.

## Headline

`memfn/tests/run_g2.sh --quick --rows`, final tree, seed 20261005, gcc 15.2 (no clang on
this box, so the clang ASan+UBSan leg did not run, as in the baseline; see "ASan" below):

| | passed | failed | wall |
|---|---|---|---|
| before (this brief) | 47,436,029 | 1 (rows (b): `arms/mismatch_inplace` never chosen) | |
| after, final tree | **48,566,738** | **0** | **149 s** (152 s on the run before the last driver edit) |

Exit 0. Rows check (b) is green; `FLOOR_ROWS` is 15.

### The rows (and what the manager pins)

```
row-chosen arms generic 224416         row-chosen runcmp bytes 18882
row-chosen arms mismatch_inplace 2670  row-chosen runcmp memcmp 41420
row-chosen arms ofsskip 25757          row-chosen runcmp overlap 9234
row-chosen arms pf_memchr 4211         row-chosen runcmp words 17642
row-chosen arms pf_memchr_back 4566
row-chosen arms pf_memchr_bounded 3619
row-chosen arms pf_walk 4692
row-chosen arms pf_walk_bounded 4291
row-chosen arms precheck 2629
row-chosen arms precheck_assign 2856
row-chosen arms runcmp 22350
PASS (a) REACH_DROPPED 0 (13 lines); PASS (b) every row >= 1 (+ control); PASS (c) 15 >= 15; PASS (d) (+ control); PASS (f)
```

* **`arms/mismatch_inplace` chosen: 2,670** (summed over the 13 kit-selecting processes:
  the generator, the MISMATCH-only generator, W2 mutations 1-11). The mutation processes
  that generate MISMATCH sites alone (9, 10, 11) choose it too, so the tier sum depends on
  the W2 set, not only on the space.
* **The generic row on MISMATCH sites.** The generic row's tier sum (224,416) is shared with
  every other family, so G2 added a generator process of its own that makes the MISMATCH family
  ALONE (`g2_gen --mm-only 1`, linked against `libpcrec_mftrace.a`, its REACH lines counted
  separately in the new check (f)): **`arms/generic` chosen 673, `arms/mismatch_inplace`
  chosen 336**, and no other row. (The generic row's tier total moved from 218,676, the
  g2m4 report's figure, to 224,416: +5,740 is the MISMATCH sites' share over all processes,
  by difference.) Hard sites by form id (the generator's FORMID lines): `generic` 138,
  `mismatch_inplace` 69; 24 and 11 more as the enforced class hook-nonident.
* A selection is counted once per `mf_emit`/`mf_define`/`mf_use`, including the generator's
  trial renders, so these are selection counts, not site counts.

The shape each row took is what the kit reports, not an assumption of G2: no check judges an
answer by its row. The only row-dependent checks are floors that a family still reaches the
rows it reached (`FORM_FLOORS mismatch_inplace:62`, `QUICK_FORM_CHECK_FLOORS`/`FULL...`,
`MM_ROW_FLOORS`).

## Commands

```
cd /home/pcrec/projects/pcrec/worktrees/g2u-cell
TMPDIR=$PWD/.scratch/tmp taskset -c 12-15 gnutimeout 1500 memfn/tests/run_g2.sh --quick --rows
```
Run in the background, log polled; wall time from `date` around it (149 s). Nothing else ran
at higher parallelism; no full tier, no `make`. Sabotage runs: the same command with
`--no-rows --keep` in scratch copies under `.scratch/sab/m7{a,b,c}` (below). Extra, outside
the runner: the MISMATCH family alone under gcc ASan+UBSan (below).

## What was added

**Coverage of the op** (family `mismatch`, `gen_fam_mismatch`; own RNG stream and id range
800000, so every older family's sites are unchanged; 207 hard sites + 35 in the enforced
class hook-nonident, run in two passes: MF_D_RUN_OVERLAP off and on):

* STMT / MISMATCH / ON_DIFF over ONE REQUIRED REF term at offset 0, `empty` NOP, forward,
  `end_back` 0, `on_miss_leaves` 1, `fold_kind` NONE / ASCII / UCP.
* Result lvalue: a local `size_t`, `o->res`, a local `ptrdiff_t`. `on_miss` is a returning
  block or a `goto`; either READS the result into `o->cnt` at the moment it runs, so the
  check sees what `on_miss` sees (item 1: "result == k when on_miss runs"). On EQUAL
  `on_miss` must not run (`missed` is 0) and the result is never looked at.
* The operand is two globals (`g2_mm_ref`, `g2_mm_reflen`) set by the driver before every
  call, spelled plain, counted (`G2_EV`) or ternary.
* **Reference** (`g2_ref.c` `g2_ref_mismatch`, a plain loop): k = the least j in [0, reflen)
  with `lo >= n` or `j >= n - lo` or `map[s[lo + j]] != map[ref[j]]`; no such j = EQUAL.
  W1 defects 5 (the fold ignored), 6 (the loop stops at reflen - 1) and 7 (the expected
  result is k + 1): fail 92,958 / 47,001 / 147,048 checks on the sampled batches.
* **Folds, generated** (`mm_build`): identity (NONE); for the ASCII relation and a Latin-1
  relation: lower, upper, per-pair random representative (all idempotent) and a random
  bijection applied after the lower / the random representative (NON-idempotent: 47 hard
  sites). Each is spelled in BOTH text shapes: FOLD_EXPR and FOLD_STMT, by table, by
  arithmetic (the lower / upper maps), with other punctuation, with a statement block, and
  with a `'@'` character literal that must be left alone (a kit that rewrote the literal
  would change the answer). The reference uses the generated table, never the kit's text;
  `g2mmchk_<id>` (emitted into the batch, run by the driver) holds the very hook text to the
  generated table over all 256 bytes (242 texts checked, 0 bad), so text and reference
  cannot drift apart.
* **Read limits** (`mm_instance`): guard pages on BOTH operands. `s`: U (guard after
  s[n-1]), L (guard under s + lo), A (exact heap, alignment 0..15), N (`lo >= n`: s points
  into PROT_NONE memory, nothing may be read) and NULL at n == 0 (6,210 checks). `ref`: its
  own guard region RU / RL / RA, NULL or a PROT_NONE pointer at reflen 0 (92,559 NULL
  checks). Subject bytes below `lo` are the complement of the true bytes in U and A, so a
  compare that starts at the wrong place answers wrongly. **Aliases**: ref inside the
  subject (before lo 47,376 / at lo 46,233 / overlapping the window 46,344 checks), over a
  periodic fill (period = |ref - lo|) with one planted difference, so long equal runs are
  compared.
* **Subjects**: every n 0..129; n <= 4 exhaustively over (lo, reflen, equal/different);
  otherwise lo in {0, 1, n/2, n-1, n, past n, random}, reflen in {0, 1, window-1, window,
  window+1.., random, 130-190}, a difference at 0 / reflen-1 / random or none, bytes drawn
  from letters of both cases, the punctuation either side of the letters, Latin-1 letters
  and the signs among them (0xD7, 0xF7, 0xB5, 0xDF, 0xFF), NUL, 0x80, anything; the planted
  difference is a near-class byte (`^0x20`, `^0x80`, `+-1`, ...) when the map allows.
* **Refusals** (`mm_refusals`, in the generator; 565 cases, 516 of them the vocabulary-absent
  sweep): every case below is refused, and where the header names the field the refusal
  must name it (31 asserted, all named; the unnamed-field cases are reported, not asserted).
  `reverse` 1; `end_back` 1; `empty` MISS / EXCLUDED / AT_N / out of enum; two REF terms;
  REF + SET; SET alone; RUN alone; REF at offset +1 / -1; REF OPTIONAL; `nterm` 0;
  `on_miss_leaves` 0 / 2; `on_miss` LOOP_EXIT (`break;`) / unstated; `result`, `ref`,
  `reflen`, `s`, `n`, `lo` unstated; `fold_kind` 3 / 255 (on a MISMATCH site and on FIND);
  `fold` stated under NONE; `fold` unstated under ASCII and UCP; `fold` text with no `@`
  (two) and with `@` only inside a char literal; `count_by_caller` on MISMATCH;
  `guard_by_caller`; EXPR / FUNC form; denies not the art's; `fold_kind` ASCII / UCP on
  FIND/EXPR/RETURN, VERIFY/EXPR/BOOL, FIND/STMT/ON_MISS, SKIP/STMT/ADVANCE; a REF term in
  FIND, SKIP, VERIFY, ALL_PRESENT and mixed with a SET term in FIND; MF_SITE_ABI + 1 (no
  hard-coded 7/8). Controls: the NONE baseline and the ASCII/UCP x EXPR/STMT baselines
  render, so no case passes for the wrong reason. The vocabulary is held in both directions:
  `mf_vocab_has` agrees with the header for every MISMATCH combination and for every
  older op with a REF term or ON_DIFF (173 agree, 0 disagree), and every combination it
  declares absent is refused in all three forms (516).
* **Poison**: the REF term's `set`, `run`, `mask`, `run_len`, `table_ref` are not read
  (header: "it carries no data"); 207 renderings with junk in them are byte-identical to
  the clean rendering (0 differ, 0 unstable control).
* **New W2 mutations** (generator `--mutate`, which now generates MISMATCH sites only): 9
  `reflen + 1`, 10 `ref` = the subject, 11 a fold that does nothing. Every mutated site must
  be killed: 207/207, 207/207, 68/68. Mutation 9 must also FAULT on the reference's guard
  page: 28,924 faults on non-alias instances with reflen > 0.
* **New W3 witnesses**: planted functions that read one byte past `ref[reflen)`, one below
  `ref[0]`, `s[n]`, `s[lo - 1]` (never when that read would be at a NULL or at n/lo/reflen 0),
  plus a clean control: faults 2,520 / 2,537 / 4,602 / 3,089 and 0 failures on the control.
  A K1-style scratch function, as the brief asks, is exactly this: the planted function is
  linked into the real driver and the real guard pages.

## Per-population floors (K35), measured less ~10%

Hard sites that ran 207 (floor 185); answer checks 966,276 (870,000); equal 439,941
(395,000); difference 526,335 (470,000); difference at 0: 249,996 (225,000); at reflen-1:
168,735 (150,000); ended by the subject's end: 232,164 (208,000); reflen 0: 190,527
(170,000); lo >= n: 218,388 (195,000); answers the fold decided (differ from the
identity-fold answer): 218,580 (195,000); near-class decoys: 78,543 (70,000); ASCII sites
68 (61), UCP 69 (62), FOLD_EXPR 68 (61), FOLD_STMT 69 (62); non-idempotent-map sites 47
(42); aliased checks min of the three kinds 46,233 (41,000); NULL subject 6,210 (5,500);
NULL reference 92,559 (83,000); refusal cases 565 (510); poison renderings 207 (185);
W2 9/10 mutated sites 207 (185), W2 11 68 (61); generator `mismatch` family 207 (185);
`mismatch_inplace` hard sites 69 (62) and quick answer checks 322,092 (290,000; the full
tier's 725,000 is DERIVED, quick x 2.5, and owed a measurement); rows (f) generic 673
(600), mismatch_inplace 336 (300). The count lines are the census lines
`G2 mismatch (R-8)`, `G2 mismatch sites`, `G2 mismatch operands`, `G2 family mismatch`
and the generator's `MMSITES`, `MMVARS`, `MMREFUSE`, `MMPOISON`. The coverage-MISSING
mechanism holds a clause for every cell (a MISMATCH cell with a zero count prints
`G2 coverage MISSING` and the runner's count-vs-lines consistency check sees it).

## Sabotage (scratch copies, never left in place)

All three ran `run_g2.sh --quick --no-rows --keep` in `.scratch/sab/m7{a,b,c}` (a copy of
`memfn/{include,tests}` with `build` symlinked), after the last driver edit.

**(a) The reference without the fold** (`g2_ref_mismatch` compares raw bytes always):
exit 1, **251,616 failed checks**; `G2 family mismatch: ... failed-sites 137` = exactly the 68
ASCII + 69 UCP sites, while the 70 fold-NONE sites stay green (the fold is the only thing
that moved). The floors tripped too: "fold-decided answers 0 < floor 195000", and W2 mutation
11 (a fold that does nothing) is caught on 0 of 68 sites, as it must be when the reference
ignores the fold. In-suite twin: W1 defect 5 (92,958 failed checks every run).

**(b) A driver without the reference's guard page** (RU and RL placed in the middle of a
mapped page): exit 1, three reds: "W3 mm-ref-over did not fault" (faults 0, was 2,520),
"W3 mm-ref-under did not fault" (0, was 2,537), and "W2 mutation 9 ... never faulted on the
reference's guard page" (0, was 28,924). `mm-s-over`, `mm-s-under` and `mm-clean` are
unchanged (4,602 / 3,089 / 0). So the reference guard does catch a planted one-byte over-read
and a one-byte under-read, planted in a function linked into the real driver. FINDING made
by this very sabotage, fixed before delivery: the first sabotage run stayed GREEN, because
an alias instance with ref ending at the subject's end puts `ref[reflen]` on the SUBJECT's
guard page (659 faults), and at reflen 0 `ref` is NULL, which faults on any read
(W2 9's 71,802 faults). The reference witnesses and W2 9 now run without aliases
(`mm_noalias`) and W2 9 is judged on its own count (non-alias, reflen > 0). Without that
the check "the reference has a guard page" did not need the reference to have one.

**(c) The ON_DIFF check, `result` != k when `on_miss` runs** (the generator's `on_miss` text
reads `(result) + 1`): exit 1, **615,378 failed checks**, `G2 family mismatch: ...
positive 0 negative 439,941 failed-sites 207`: every difference outcome of every one of the
207 sites fails ("on_miss saw result 1, want k=0"), the EQUAL outcomes still pass. W1
defect 7 did not fire in that copy, correctly: it adds the same +1 on the reference's side
and the two cancel. In-suite twin: W1 defect 7 (147,048 failed checks every run).

**Kill list**: W2 9 (207/207), 10 (207/207), 11 (68/68), W1 5 / 6 / 7, W3 mm-ref-over /
mm-ref-under / mm-s-over / mm-s-under.

### ASan (outside the runner)

The runner's ASan+UBSan leg needs clang (absent here). The MISMATCH family alone was built
with gcc `-fsanitize=address,undefined` (`g2_gen --mm-only 1`, the batches, the driver, the
reference) and run `--quick`: 1,129,656 passed, 0 failed, no sanitizer report; the exact-size
heap layouts A for both operands are what lets ASan see an over-read.

## Findings (readings, not resolved by reading the kit)

* **Q-G2M7-1. `lo >= n` with reflen > 0.** The header's generic range rule makes the range
  empty iff `lo + end_back >= n`, and says MISMATCH's `empty` is NOP "because an empty reference
  is EQUAL". But k's definition makes `lo >= n` a DIFFERENCE at 0 (`lo + 0 >= n`), on_miss runs
  with result 0. G2 follows k (the more precise text): 218,388 checks with `lo >= n`, and
  it passes. If the intent were NOP-on-empty-window (nothing runs), the header should say so;
  `empty` NOP has two possible readings for MISMATCH ("reflen 0" vs "window empty").
* **Q-G2M7-2. How large may `lo` be?** `lo > n` is legal; G2 stops at n + 8. `lo + j` wraps for
  `lo` near SIZE_MAX (the kit's loops compute `lo + res >= n`); the contract does not bound `lo`.
* **Q-G2M7-3. The UCP relation.** `MF_FOLD_UCP` is "pcrec's Unicode simple fold restricted to
  single bytes (Latin-1)". G2 reads it as the ASCII pairs plus 0xC0-0xDE <-> 0xE0-0xFE except
  0xD7/0xF7, with 0xB5, 0xDF, 0xFF singletons (their simple folds leave Latin-1). The header
  does not enumerate it. Today no row reads `fold_kind` to avoid the text (the kit's rows use the
  hook), so the choice is not observable; the first row that does would be tested by these maps.
* **Q-G2M7-4. `result` on EQUAL, and `result_decl`.** "Holds no promised value (a form may have
  written it)": G2 never reads it on EQUAL (the kit's loops leave `res == reflen`). The header is
  silent on `result_decl` for ON_DIFF (a declaration the kit would have to place in a block that
  also holds the loop); G2 states none and tests nothing about it.
* **Q-G2M7-5. `pred.need` (a whole predicate OPTIONAL) on MISMATCH** renders without complaint.
  The header says only "one REQUIRED REF term"; `pred.need` is documented for ALL_PRESENT.
  G2 does not assert a refusal (it first did, and the kit's silent acceptance showed the
  header gives no basis).
* **Q-G2M7-6. Field names in the structural refusals.** The header names fields only for
  `reverse`, `end_back`, `empty`, `on_miss_leaves`, `on_miss`, `fold_kind`, `fold`, `ref`,
  `reflen`, and the hooks. For a second term, a non-REF term, a REF term off 0 or OPTIONAL, `nterm`
  0, the kit's text names `pred` (and "offset 0" in words); G2 asserts only the refusal and prints
  whether `nterm`, `kind`, `offset`, `need`, `form`, `guard_by_caller` appear (6 yes, 12 no, in
  `MMREFUSE soft_named/soft_unnamed`).
* **Q-G2M7-7. The lexical class of the fold text.** "FOLD_EXPR ... FOLD_STMT" are classes of
  `fields.def` (not in the cell). G2's STMT texts end in `;` or `}`, its EXPR texts have no
  trailing `;`; what the kit does with an EXPR text that ends in `;`, a STMT text without one, or
  one that is both, is not stated. Not tested.
* **Q-G2M7-8. `s` NULL.** The header says "never forms `s + lo`" and reads `s` only in
  [lo, n); the brief adds "NULL when n == 0". G2 passes NULL at n == 0 (any lo) and a
  PROT_NONE non-NULL pointer when `lo >= n`, n > 0. Both pass; the contract text does not say
  a NULL `s` with n > 0 and lo >= n is allowed (not tested).
* **Q-G2M7-9. How many times is each hook evaluated.** `ref`, `reflen` are "side-effect-free
  expressions"; G2's counted style (`G2_EV`) tolerates any number of evaluations and counts none.
  Whether `fold` is pasted exactly once per operand cannot be observed except through a non-
  idempotent map (which G2 has: a second application on one operand would disagree).
* **Q-G2M7-10. `on_miss` "may be pasted more than once".** G2's `on_miss` texts are a block and a
  `goto`; neither declares a local, so a duplicate paste cannot collide. A text that does
  (`int t = ...;`) is the caller's to brace; the header does not say so.
* **Q-G2M7-11. A guard page does not say who faulted.** A NULL `ref` at reflen 0 and an alias
  both fault where a reference guard would; the witnesses are attributed (see sabotage (b)). A
  kit that reads `ref[0]` when `reflen == 0` is caught only by the NULL / PROT_NONE pointer.
* No kit defect found: every check is green on the kit as delivered.

## Files changed in the cell

* `memfn/tests/g2/g2.h`: `G2_OP_MISM`, `G2_H_ON_DIFF`, `G2_T_REF`, `G2_FOLD_*`, family
  `G2_FAM_MISM` ("mismatch"), six appended `g2_site` fields, `g2_mm_ref`/`g2_mm_reflen`.
* `memfn/tests/g2/g2_ref.h` / `g2_ref.c`: `g2_ref_mismatch`, W1 defects 5, 6, 7.
* `memfn/tests/g2/g2_gen.c`: the maps and spellings, the `ON_DIFF` wrapper, the MISMATCH poison,
  `gen_fam_mismatch`, `mm_refusals`, the registry fields, `--mm-only`, W2 9-11.
* `memfn/tests/g2/g2_driver.c`: `run_mismatch` and the two-operand layouts, W3's five
  functions, the census lines, `mm_noalias`.
* `memfn/tests/run_g2.sh`: `FLOOR_ROWS` 15, `mismatch` family and form floors, `FLOOR_MM_*`,
  W1 1-7, W2 1-11 (9-11 unsampled), the W3 mm judge, check (f), the mm-only process.
* `memfn/tests/CLAUDE.md` (new section, file list), this report. `g2_k1.c` unchanged.

## Disclosure

Seen at spawn, not as inputs: the session-root `CLAUDE.md` (the pcrec working agreement,
including the scope mandate, the build/test section and the situation index), the manager's
memory index (`MEMORY.md`), the git status snapshot (branch `lane/memfn-m7`, clean, five
recent commit subjects, one of them "decisions: D58 addendum 2 — the residual text gains one
kit site token, no callback (R-8/M7 Q-R8-3)"), the environment note naming
`worktrees/memfn` as the primary directory (nothing was written there; one `rm` was
blocked by the safety check, whose message resolved the path under `worktrees/memfn/.scratch`;
it did not run and was redone with a fresh directory name), the skill and agent lists, and the
names of other active agents (main, g2m4, m7, m7scope, s513tri, s525tri). Read by the
brief's leave: `docs/dev/lanes/BOILERPLATE.md` and `docs/dev/learnings.md` section 3.
Read in the cell: `memfn.h` (the MISMATCH passages and the structs, whole where they matter),
`integration.md` (the greps for MISMATCH / ON_DIFF / REF and section 15.8 whole, which is the
kit's own as-built description of the site and its two rows; section 14 was NOT read in full:
the contract text G2 used is memfn.h's and the G2 files' accumulated readings), `trace_format.md`
(its head), the cell's G2 files and the previous lane's report (`G2M4_REPORT.md`). Not read: `memfn/src/`, `src/`, `tests/`, git history,
the kit's responses ledger. Output of the opaque binaries reached me as it came: refusal texts
(printed in `gen_results.txt`), the MFTRACE REACH lines, and the rendered text of a few sites
in the generated batches (two: a generic-row loop and a `goto` form) while checking the
wrapper compiled. The `.scratch/` directory held earlier lanes' files (logs, work trees); they
were not read.

## Charter checklist

| # | item | artifact |
|---|---|---|
| 1 | the op: `MF_OP_MISMATCH` / STMT / `MF_H_ON_DIFF` over one REQUIRED REF term at 0; k; `result` == k when `on_miss` runs; EQUAL runs nothing; reflen 0; `lo > n` and `empty` | `g2_ref.c` `g2_ref_mismatch`; `g2_gen.c` `gen_fam_mismatch`/`mm_cell`, the `G2_H_ON_DIFF` case of `wrap` (`on_miss` reads the result into `o->cnt`); `g2_driver.c` `run_mismatch`/`mm_instance` (census `G2 mismatch (R-8)`: equal / diff / diff-at-0 / at-reflen-1 / ended-by-subject / reflen-0 / lo-ge-n); refusal cases for every `empty` but NOP; Q-G2M7-1 |
| 2 | read limits, NULL operands, aliasing, guard pages on BOTH operands | `mm_layouts_init` (a second guard region), `mm_instance` (s: U/L/A/N/NULL; ref: RU/RL/RA/NULL/PROT_NONE; alias before/at/overlapping lo), W3 `mm-ref-over/under`, `mm-s-over/under`, `mm-clean`; sabotage (b) |
| 3 | folds NONE / ASCII / UCP, both text shapes, GENERATED maps (identity, ASCII, Latin-1, random idempotent, non-idempotent), reference uses the generated map | `g2_gen.c` `mm_build`/`mm_spell`/`mm_emit_tables` (`g2mm_<id>`, `g2mmchk_<id>`), `g2_ref_mismatch(map...)`, `g2_site.mm_map`/`mm_chk`; W1 5; sabotage (a) |
| 4 | refusals, each naming its field | `mm_refusals` (565 cases; `MMREFUSE`), `abi + 1` with no hard-coded number, the two-direction vocabulary sweep; Q-G2M7-5/6/7 |
| 5 | rows: `FLOOR_ROWS` 14 -> 15, (b) green, per-row counts | `run_g2.sh` `FLOOR_ROWS=15`, check (f) and the MISMATCH-only process (`--mm-only 1`); counts above |
| 6 | controls, witnesses, mutation killed | W1 5 / 6 / 7; W2 9 / 10 / 11 (and 1-8 now include MISMATCH sites); W3 mm witnesses; the baseline-renders controls; sabotage (a)(b)(c) |

Open questions: Q-G2M7-1 .. Q-G2M7-11 above.
