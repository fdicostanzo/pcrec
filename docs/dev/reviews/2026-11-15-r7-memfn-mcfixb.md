# 2026-11-15 r7 memfn-mcfixb — light code round on the r6 fix diff (DRAFT, dispositions PROPOSED)

## Subject
- SUBJECT 6ab3f485b9942606ebd5765fd68fd9a586804138 (lane/memfn-mcfixb; unchanged at hand-back).
- BASE ac097a76e2a85a5daef793dc2506ed6f6a13423b (stated: earlier code reviewed by r5, r6), plus the comment-only
  ac097a76e (S3198 respell) in scope.
- Promise: the r6 review's RULED FIX-NOW list (`docs/dev/reviews/2026-11-15-r6-memfn-mcfix.md`).
- Rulings frozen at main d64c3e822 (decisions.md/plan.md last touched 782502e99; no FREEZE DRIFT at hand-back).
  D197 at decisions.md:10219. FREEZE NOTE: main's rule conditions and kit ruling R1 have their record in the
  subject's d197_rule.tsv header (message-only elsewhere).
- Review tree built once (`nice make -j2`, rc 0). Run kit: a JMH dry run of the review tree, green (172 arms, gate +
  round check on 7 launches, `kit/dry_JMH.log`, rc 0); d197 drill `43 cases, 0 wrong`.

## Lenses as run
| lens | model | question | why |
|---|---|---|---|
| rule | opus | d197_rule.tsv drilled first-match from the TSV text on constructed records vs the script; every r6 guard refuses its plant and admits the valid pair (over-refusal counted); do the new pins break earlier windows' records/sets? + sibling-of-family, general form + unlocks | decision table + run record pins (launcher's lens 1) |
| checks | sonnet | TIMED-SHAPE allowlist + shape selftest plants, FF__COUNT sentinel, --sites<80, zero movers, S3198 anchors | checks/pins + emitted (launcher's lens 2) |
| verify | sonnet | re-ran all 5 CONFIRMED findings | §6 |

## Which lens caught what
rule: RULE-1 (answer-level, CLI), RULE-2 (earlier windows), RULE-3 (over-refusal), RULE-4 (family). checks: CHECKS-1, CHECKS-2. All five verified HOLDS.

## Findings (by id, PROPOSED disposition)

### Measurement / verdict level
- **RULE-1** (CONFIRMED, verified HOLDS; answer-level for the D197 verdict). `d197_rule.py:487` passes
  `"--second" in a` (a bool) as rule()'s `second`; rule() (:231-239) now takes the first run's two RUNDIRS and
  derives `is_second = second is not None`. So the CLI WITHOUT `--second` scores every first run as a SECOND run
  (an INCONCLUSIVE first pass reads `NOT-WIN (second-run-without-a-verdict)`, "never a third run"), and
  `--second A B` dies with an uncaught `TypeError: 'bool' object is not iterable` (not exit 2). The drill calls
  rule() directly, so it stays 43/43 green while the shipped entry point is wrong (a control sharing no source with
  the CLI: learnings §3). Repro: verify.md RULE-1 (critic's p1 record: CLI -> NOT-WIN x3; `rule(p1, avx2)` ->
  INCONCLUSIVE x3). LOSS/WIN/CONFIRM paths are unaffected. **FIX-NOW** (before the window's verdict is read; the
  01:00 window's TIMING is unaffected, the scoring is): parse `--second` like `--confirm` (two rundirs, refuse
  otherwise), pass the tuple or None; add CLI-level (subprocess) drill cases: no flag, --second pair, --confirm
  pair, --second + --confirm.

### Earlier windows (the launcher's named question)
- **RULE-2** (CONFIRMED, verified HOLDS; maintenance). est.py read_cells refuses any record without
  `cells_sha256_<job>` ("the record pins none"), i.e. EVERY record finalized before r6. Per workflow:
  est re-pricing an s2d1/s2d2 run dir (rows/draft): BROKEN; `rmax_drill.py RUNDIR` (the documented re-derivation
  of policy.tsv r_max_e6 over both windows, via est.compute): BROKEN; re-finalizing an old record to gain the pin:
  refused earlier by r5's libc probe (`the record's libc is 'glibc 2.43', this box's 'glibc 2.43 memchr=evex'`),
  not by this diff; draft regeneration from an old window: BROKEN. NOT broken: committed run_record.tsv bytes and
  zen4-grid3's PROVENANCE sha, measure_store, memfn/data, j1_rule.py, d197_rule (no mfcard/mfconfirm record exists
  anywhere). Practical exposure is small: the committed s2d dirs hold no cells files, so the refusal bites only when
  scratch cells are restored beside a record. **FIX-NOW (XS)** preferred: refuse a cells pin that is PRESENT and
  differs (the tamper case FIDELITY-3 targets); read an absent pin as "pre-r6, unpinned" with a printed note — the
  same policy manifest_check (r11) already uses. Alternative: DOC (rule the refusal deliberate and say in
  rmax_drill.py's header and s2d2/CLAUDE.md that old windows can no longer be re-priced). The libc-probe half is
  r5's and goes to PLAN if the kit wants old windows re-finalizable.

### Design / check quality
- **RULE-3** (CONFIRMED, verified HOLDS as a design finding; the code does what the tsv says). The shipped-arm
  guard (`d197_rule.py:57-59`, tsv row `memchr-variant-not-the-arms`) makes the shipped arm no-verdict whenever it
  bound `avx2`, even with no tunable. On an AVX2-only box (ubuntubudu's Zen 1; x86-64-v3's natural target, D144
  add. 4) the shipped memchr IS avx2, so every level is INCONCLUSIVE, then NOT-WIN, without a number read. The guard
  encodes the 7700X's ifunc landscape rather than the property (shipped arm: no tunable). **DOC** now (the tsv
  header says the mfcard window is 7700X-only), **PLAN** the general fix (refuse the shipped arm on tunables alone;
  when both arms bind the same variant, score one libc row / name them twins). Trigger: the first mfcard window
  planned off the 7700X.
- **RULE-4** (design/maintenance; general form + unlock). Three "record pins a file, a reader must match"
  mechanisms with three absent-pin policies (manifest r11: allowed; cells r6: refused; rule r6: refused) plus
  cards/policy/transcript pins, each with its own code. Side effect: record.window() writes D197's rule pins into
  EVERY window (s2d, j1 too), so an edit to d197_rule.tsv inside an unrelated window refuses that window's next job.
  General form: one declared PIN table in record.py (key, files, written at window|finalize, windows it applies to,
  absent policy) and one check_pins() est and d197_rule call. Unlocks: RULE-2 becomes a column; window-scoped pins
  a column; the next pin a row. **PLAN** (trigger: the next pin added, or RULE-2's ruling if it wants a code change
  beyond the XS one).
- **CHECKS-1** (CONFIRMED, verified HOLDS; low). TIMED-SHAPE's indirect-branch refusal fires before the per-form
  callee allowlist, so under `-fno-plt` the valid fn-memchr control (`jmp/call *memchr@GOTPCREL`) is refused.
  link.py:38's CC carries no -fno-plt, no env/CFLAGS path reaches it, gcc's specs do not default it. Fails closed.
  **NOTED** (or a one-line comment beside CC that -fno-plt is unsupported by TIMED-SHAPE).
- **CHECKS-2** (CONFIRMED, verified HOLDS; maintenance). window.c:1904's `_Static_assert(FF_MFIND < 31 && ...)`
  guarding `REN_PICK(f) = 1u << f` is still keyed to the last real member, not FF__COUNT, the bound the r6 fix
  introduced for exactly this. **FIX-NOW (trivial, rides RULE-1's lane)**: `FF__COUNT <= 31`. No emitted byte moves.

## Proposed FIX-NOW
RULE-1 (the CLI's --second; plus CLI-level drill cases), RULE-2 (absent cells pin = unpinned + note), CHECKS-2
(one assert). DOC: RULE-3 (7700X-only in the tsv header). PLAN: RULE-3 general fix, RULE-4 pin table. NOTED: CHECKS-1.

## PROBED-AND-HELD (details in review/)
- rule: an independent first-match reading of d197_rule.tsv agreed with the script on the drill's 31 outcome cases
  (RULE-1 ordering: NOT-WIN second-run-without-a-verdict first; R1: --confirm re-scores CONFIRM levels only; RULE-5:
  a refused/absent confirmation -> INCONCLUSIVE, never re-issued); 14 provenance plants refused (own records as
  confirmation, pre-r6 pin, other rule table, code_commit, plan, fold, run-id reuse, wrong JMHC cells); a REAL
  synth mfconfirm pair (both arms) ADMITTED and priced FULL; RULE-7's ratio regex can fail on "-"; pin timing (rule
  pinned at every job start, before numbers) held.
- checks: shape-selftest 7/0; 12 plant shapes x 4 flag sets = 48 (memchr in an mfind arm, external tail-jmp, PLT,
  indirect call/jmp, section symbols, cold split, other-section local fn, unknown form) all as expected except
  -fno-plt (CHECKS-1); FF__COUNT: an undeclared member after FF_MFIND fails both asserts, a declared one compiles;
  --sites 79/40/0/-5 refused, 80 admitted, --quick = 80, no env path; zero movers: memfn/src diff is enum +
  static_assert only, all 18 memfn/src TUs BASE vs SUBJECT -O2 disassembly + data identical, no src/ cli/ lib/
  change (the 400-compile sweep was judged redundant); ac097a76e: m6read_check_sab_anchors.py 1301 sabotages, all
  anchors resolve.

## By-id completeness
rule: RULE-1..4 (all dispositioned). checks: CHECKS-1, CHECKS-2. verify: 5/5 HOLDS (RULE-2 with a scope note,
RULE-3 as design). r6 FIX-NOW promise: RULE-1 ordering, RULE-2/5/6 provenance, RULE-3 + FIDELITY-3 pins,
FIDELITY-2, FIDELITY-1, RULE-7, CHECKS-A1, CHECKS-A3 all HELD at the API level; RULE-6's "--second derived from
records" is broken at the CLI (RULE-1 here).

## Recommendation
The 01:00 window's TIMING may proceed on this subject (dry run green, zero movers, guards hold); the VERDICT must
not be read with the CLI until RULE-1 lands. RULE-1 + CHECKS-2 + RULE-2 are one XS lane.

## Lessons for the guide (proposed)
- A rule script whose drill calls its Python function must ALSO drill its CLI (subprocess): a signature change
  (bool -> pair) left the drill green and the entry point wrong (RULE-1). Proposed text for critics.md / the
  harness-fidelity lens: "drill the entry point the window runs, not only the function it calls".
- A new pin needs an absent-pin policy stated beside it, and the readers of every committed earlier record re-run
  (RULE-2: the launcher's named question found it in minutes).

## RULED (kit manager, 2026-11-15 ~14:05)
- All PROPOSED dispositions accepted: FIX-NOW RULE-1 (parse `--second` as the first run's pair; drill the CLI by subprocess), RULE-2 (refuse a cells pin only when present and different; a missing pin is a NOTE, as manifest_check does, so s2d1/s2d2 re-pricing keeps working), CHECKS-2 (window.c:1904 assert to FF__COUNT <= 31). DOC RULE-3 (the window is 7700X-only: the shipped-arm guard refuses an AVX2-only box). PLAN RULE-3's general fix, RULE-4 (one pin table). NOTED CHECKS-1.
- One XS fix lane (mcfixc, sonnet) on lane/memfn-mcfixb; its diff gets a one-critic sized round before landing.
- Lesson accepted: drill the entry point the window runs (the CLI, by subprocess), not only the imported function.
