# 2026-11-15 r5 memfn-mfindcomb — code round on the inline one-member finder + slot harness ver-6 (DRAFT, dispositions PROPOSED)

Coordinator draft for the kit manager to rule. Critic texts and verify.md are in the sibling dir `review/`.

## Subject

- Mode: code. SUBJECT = `1e3d4a17bda57ebe1f59fb9e1cfaa33dd28c2b0c` (merge "lane/memfn-slotx into lane/memfn-mfind", on
  lane/memfn-mfind; the commit, not the moving branch head). BASE = `git merge-base main SUBJECT` =
  `04fe41c924869a4773aaebe4cd93dd5ce68e5acc` (as expected). 58 commits, 49 files, ~3.2k lines (denylist excluded).
- The unit: the kit's inline one-member finder (`fn-mfind` SWAR BODY row; `mfind-w16`/`mfind-w32` SIMD prefix rows;
  memfn/src/vrun.c `mfind_text`, ofsskip.c `fn_rows[]`/`ofs_fn_fits`, formhash.c), reached only by the test-only
  lever `--harness=mfind`, unpicked by default; the slot harness changes (per-arm target region + ISA check,
  `reject` dim, ver-6 planning JMB/JMH, per-ISA-level draft sets); kit-grid@6 cards; G2 one-member family; plants.
- Claimed: zero emitted-byte movers under default flags, no abi event. **HELD** (EMITTED, below).
- Rulings frozen at main `4ccd97ca7` (decisions/plan last touched 9e63a8b23). D197 at decisions.md:10219.
- FREEZE NOTES: the ISA-level draft-set ruling and the §7.2 card-binding ruling had no main record at the freeze
  (message only); their homes are in the subject (span_cards.md §2.7 ~803; measure_sets.md ~1244).
- FREEZE DRIFT (re-diffed at each return and at hand-back): main moved to 917a3c522; decisions.md gained **D198**
  ([COVER-CAP], not this subject). Its item (f), the owner's "if the inline form causes the artifact to bust the
  L1/L2 cache then they might turn out slower", bears directly on EMITTED-1 (a one-site timing cannot see text size).
  plan.md unchanged.

## Owner questions

### Q1 — what does the prepared timing `kit-mfcard-time` (JMB/JMH, window `mfcard`) time?

**One sentence:** The mfcard window (no job script named `kit-mfcard-time` exists in the subject tree; slot/jobs/
holds only the s2d window's 480-489 jobs, so the job is defined outside it) times, per arm, a noinline find-all loop
`_time` over ONE offset-skip site, i.e. the one-byte finder INCLUDING its two-byte check `xy` and, at reject > 0,
the MASK stream's continue-after-reject path (re-entering at hit+1 after each accepted hit), on seeded 16 MiB pools,
for four forms (mfind-swar generic, mfind-w16 x86-64, mfind-w32 x86-64-v3, fn-memchr generic, i.e. libc memchr +
restart) on find_byte@6 (miss-only slope, lengths 64Ki/256Ki/1Mi) and find_hit@6 (landing periodic, split one, gaps
2,4,8,16,32,64,256,1024,65536 x reject 0/100, plus 50 at gaps 4/32/256; length 1Mi; 4 + 84 rows); each row is priced
only against the walk unit (J2) and its own miss-only `base.<form>`, NO code compares any mfind row with
fn-memchr/libc/pair; and the thing timed IS the thing gated and keyed at dry time EXCEPT that the w16/w32 finders are
compiled OUT OF LINE in the timed TU (a call per accepted hit that pcrec's emitted matcher does not pay, FIDELITY-1),
and the RECORD (manifest, cell_text, cells) is not re-verified by est for this window (FIDELITY-2/-5).

Evidence (fidelity.md "Q1 answer", verify.md FIDELITY-1/-2/-4):
- Timed loop: link.py:224-261 WRAP_FIND, `_time` = `for (p = 0; p < n && step(s, n, &p); p++) k++` (link.py:246);
  `step` = the site body `pos = mf_fn(subject, n, pos)` from `arm_fixtures --site-parts`; `_gate` (link.py:254) runs
  the same `step` + sum/FNV. Site text: `mf_fn__w32 -> __w16 -> __body`, candidate loop `if (!memcmp(subject + cand,
  "xy", 2)) return cand; m &= m - 1;`; fn-memchr: `memchr` + memcmp + `pos = cand + 1`.
- Cells: plan.py:142-154, 436-451; gen.c:90-139 plants hits at k*gap+(gap-2) and floor(E*R/100) rejected; drv.c
  gate + sentinel; run.py:101-125 REJECT-RATE; KEY-ARM over all five find_hit dims (link.py:364-367).
- Comparison: est.py:595-743: v = a/u (the job's ctl), x = v/W (J2's walk), delta rows D = cell(arm) - cell(base).
  J2 and J2p ride the window for W and the ver-3 anchor only. mfind-w32 rows land in zen4-grid6-v3, fn-memchr in
  zen4-grid6, so D197's comparison is cross-set by construction (FIDELITY-4).
- Gated = timed: same `step`, same subjects (gate population asserted against the plan, run.py:84-98). Keyed: cell
  id carries the key; cell-text hash = instance hash (frame not hashed). Recorded: est reads the finalized record,
  not a live recomputation, but no manifest check on this window (FIDELITY-2).
- The out-of-line shape (verify.md FIDELITY-1, reproduced): arm24.c compiled with link.py's own line has `call
  mf_fn__w32` inside `a24_time`; delete `_gate` and it inlines (0 calls); pcrec's lever matcher at x86-64-v3 inlines
  the finder into rx_search. +8 instructions per accepted hit (call/ret/vzeroupper/re-broadcast), biasing the fused
  cost UP, i.e. toward D197's "loss" branch, most at small gaps. Magnitude untimed (clock forbidden).

### Q2 — per-ISA-level draft sets: is a mixing set refused, and does identical generic/x86-64 text share one cell?

**Answer:** PARTLY. A set mixing ISA levels is refused ONLY when est.py's two hand-written tables (TARGET_SET,
TARGET_LEVEL) disagree with each other: plants P1-P3 (one-table edits) were REFUSED `DRAFT-ISA-LEVEL MIXED`, but P4
(both tables edited consistently), P5 (a row labelled generic whose code needs AVX2) and P11 (a post-run cell_text
edit) were silently WRITTEN into the x86_64/zen4 set (DRAFTSETS-1, FIDELITY-2; verifier re-ran P4, P5, P11: HOLDS).
Identical text from generic and x86-64 does land in one cell, but only by construction (a key names a form with one
instance and one target; est keeps the last cell_text line per key), and nothing checks it; DIFFERENT text under one
key collapses the same way (DRAFTSETS-4, P8/P9). Base and ctl cells are also filed in sets of another ISA level
(FIDELITY-3). The ruled ids/classes are right (P0: zen4-grid6 x86_64/zen4 = swar+w16+fn-memchr; zen4-grid6-v3 =
w32). Separately, neither ver-6 draft set can LOAD: its header `unit_key kit.find_byte.walk` names no row in it
(contract-2, verifier loaded both: rc 1 `unit_key ... names no row`).

## Lenses as run

| lens | model | one question | why chosen | file |
|---|---|---|---|---|
| harness fidelity | opus | Q1: what JMB/JMH time; timed = gated/keyed/recorded; four plants | a measurement harness + the owner's Q1 | fidelity.md |
| draft sets + ruling check | opus | Q2 by plants; D197 / draft-set / §7.2 agreement and consequences | owner's Q2; rulings relied on | draftsets.md |
| emitted vs replaced | opus | zero-mover claim BASE vs SUBJECT; lever text vs fn-memchr (answers first, then cost) | emitted C | emitted.md |
| check adequacy | opus | each new kit-side check / plant: fails on what, reaches, counted | >5 sabotage rows | checks.md |
| contract + house rules | sonnet | written promises vs code; coding.md | caller-facing docs/cards; new C | contract.md |
| verifier | opus | re-run every CONFIRMED finding that would change code or design | — | verify.md |

Standing questions (sibling of a family; general form + unlocks) were asked of every critic.

## Which lens caught what

- Fidelity: the out-of-line timed shape (FIDELITY-1), unverified record on this window (2), cross-level base cells
  (3), no D197 rule (4), cells unpinned (5).
- Draft sets: self-referential guard (1), manifest/cell_text unchecked (2 = FIDELITY-2), KeyError (3), §2.7 doc
  contradiction (4), D197 consequences in prose (5).
- Emitted: zero movers HELD (~1,030 compiles, 116 fixtures, ~15M lever answer cases, 0 wrong); size (1); swar-vs-libc
  confound (2); wsearch table (3).
- Checks: G2 counts no forms (1), one-sided lists (2), lever-capped floor (3), axes arm host pin (4), cap has no
  plant (5), held-constant fields (6), --sites floor scaling (7).
- Contract: rows.tsv status (1 = DRAFTSETS-5), unit_key unloadable (2, the only critic to find it), lane-report
  pointers (3), guard parallel table (4 = DRAFTSETS-1), lying reply (5), names/side-effecting predicate/gen.c (6).

## Findings (consolidated) with PROPOSED dispositions

Severity per the critic; verifier verdict in brackets.

| id | lenses | sev | finding | verify | PROPOSED | reason |
|---|---|---|---|---|---|---|
| FIDELITY-1 | fidelity | answer (of the instrument) | w16/w32 finders out of line in the timed TU because `_gate` is a second caller of `step`; pcrec's matcher inlines them; +8 instr/hit, biases toward D197's "loss" | HOLDS | **FIX-NOW** | the run exists for a one-sided per-hit verdict; a timed shape the artifact does not have invalidates exactly that side. Fix: gate from a separate TU (or a noinline wrapper symmetric for every form) so `_time` holds the only call site, plus a dry-run check that `_time` calls no local symbol |
| contract-2 | contract | design (answer of the set) | ver-6 draft sets' `unit_key kit.find_byte.walk` names no row; both drafts refused by the loader; est selftest pins the refused shape (shape pre-exists for ver 4 at BASE, never committed) | HOLDS (by load) | **FIX-NOW** (shape needs the manager's call) | a draft that cannot load cannot become a set; choose: repeat the unit's ratio-1 row in each set, or a ver-6 unit among its own forms; fix the selftest to load-check |
| FIDELITY-2 = DRAFTSETS-2 | fidelity, draftsets | answer (record integrity) | est runs manifest_check only for verify jobs; mfcard jobs never checked; cell_text (which decides the set) read unpinned; duplicate keys collapse | HOLDS (P11) | **FIX-NOW** | small; check every ran job's manifest incl. `cell_text`; refuse a key seen twice |
| DRAFTSETS-1 = contract-4 | draftsets, contract | design | ISA-level guard compares two literal dicts; never reads target facts / `target_isa`; P4/P5 accepted | HOLDS | **FIX-NOW** | the owner's Q2 condition, literally; derive the level from the kit's `--target-facts` / the cell's `target_isa` vs the floor, one table; TARGET_LEVEL deleted (a simplification) |
| FIDELITY-3 | fidelity | maintenance/design | base.<form> and ctl cells filed in sets of another ISA level (in_set True for non-row arms) and another ver | HOLDS | **FIX-NOW** (with DRAFTSETS-1) | same function; the ruling says a set never mixes levels; bases already have cell_text lines |
| DRAFTSETS-3 | draftsets | maintenance | unknown target -> KeyError traceback | HOLDS | **FIX-NOW** (folds into DRAFTSETS-1) | XS; the owed mfind-w64 arm reaches it |
| FIDELITY-4 (+ EMITTED-2) | fidelity, emitted | design | no declared rule computes D197's loss/win (which cells, forms, gaps, rejects, margin); the two sides land in different sets; a swar loss confounds fusion with search width (8 B vs libc's ifunc AVX2/EVEX); fn-memchr in the baseline-class set runs above-baseline libc code | HOLDS (ifunc variant not verified) | **FIX-NOW** (a declared rule, before the window) | D197 is one-sided; fix the deciding cells before the numbers exist (j1_rule.py precedent), e.g. mfind-w32 vs fn-memchr at x86-64-v3 on find_hit@6; record the libc variant |
| FIDELITY-5 | fidelity | answer (record integrity) | cells.<job>.tsv pinned by nothing; duplicate lines and reject-token swaps move rows silently | HOLDS, pre-existing at BASE | **FIX-NOW** (XS part) / PLAN (pin) | refuse duplicate (job, arm, length, launch) now; pin cells sha in finalize as a plan row (every window) |
| EMITTED-1 | emitted | size | lever text 2.9x (SWAR) to 6x (v3) the fn-memchr body: the verify chain written 2-4 times, the mask twice | HOLDS | **DOC** now + PLAN | the one-site timing cannot see it (D198 (f)); state in the ver-6 card that size is not timed and report emitted size beside the timing; chain-once renderer only on D197's WIN branch |
| EMITTED-3 | emitted | maintenance | window.c `wf_wsearch[FF_HORS + 1]`: FF_MFIND's NONE comes from the bounds branch, no size assert | HOLDS | **FIX-NOW** | trivial; protects the next real pick |
| DRAFTSETS-5 = contract-1 | draftsets, contract | doc/design | rows.tsv `pending-site:span_pick-row-1` promises a reaching site D197 forbids; "picks yet / until a selection table picks / replaces this predicate" in six places; card calls the split cells "owed" | PARTLY (D197 not in the subject tree, so its cite is a landing item) | **FIX-NOW** (doc) | a token/wording change; rows_check reason (e.g. `contract-reach:mfind` or a new `instrument:` reason); cite D197 at landing |
| DRAFTSETS-4 | draftsets | doc | §2.7 "a set is one target" / "one-target rule" contradict the new paragraph; `and base_tg` dead conjunct | HOLDS | **FIX-NOW** (doc + XS) | restate as one ISA level per set |
| CHECKS-1 | checks | maintenance | G2 one-member family counts subject populations, not forms; w32->w16 selector plant green (verifier: 150 -> 0 ymm compares, identical output) | HOLDS | **FIX-NOW** | small: a selector-calls-top-rung structural check per target (or a path census with floors) |
| CHECKS-5 | checks | maintenance | the r2 F1 cap (`return ofs_fn_fits(x, d);`) has no sabotage row; G2 never reaches the cap | HOLDS (red-on-removal argued, not re-run) | **FIX-NOW** | one mech row, suite simdguarded |
| CHECKS-3 | checks | maintenance | `lever-capped` floor counts "no SIMD form", not "fit test declined"; S3170 raises it | HOLDS | **FIX-NOW** | small: count only where the body is fn-mfind (`memcpy(&w`) and helpers absent |
| CHECKS-7 | checks | maintenance | POP_FLOOR scales linearly below 80 sites; `--sites 48` 6 false reds | HOLDS | **FIX-NOW** | trivial: refuse < 80 or scale on (sites - 40) |
| CHECKS-2 | checks | maintenance | run_g2_mfind.py PLANTS/BUILDS/POP/DRV lists: deleted line green; LEVER_ARMS invented line green | HOLDS (code) | **PLAN** | the sibling G2 runners share it; a literal id pin per list across the family, trigger: next runner change |
| CHECKS-4 | checks | maintenance | axes mfind x SIMD arm pins x86-64-v3 on any host, no skip, no reach count | PARTLY (the pin is the pre-existing U3 rule) | **PLAN** | fix with the existing `--memfn=` SIMD arm, trigger: first non-amd64 test-axes run; add a `mfind@` reach count |
| CHECKS-6 | checks | design | fields G2 holds constant; hidden branches (REACH decline, cap decline, precedence vs fn-pair, refusal path, RUN_OVERLAP, use side) | — | **NOTED** | none an answer risk today |
| contract-3 | contract | doc | card file and public header point at a lane report / review file for contract content (timing plan, owed list) | — | **DOC** | state the owed list in the card / span_cards; drop the review pointer from memfn.h |
| contract-5 | contract | design (low) | the kit knowingly replies search NONE / stream RESTART under the lever (no reader, EMITTED probed) | — | **NOTED** | acceptable for an instrument; must go at any build of the split shape |
| contract-6 | contract | maintenance | `ofs_fn_fits` renders into a counting sink: wused/includes idempotent today, a kit_fail inside it is sticky; fn_in positional init; slot gen.c random landing with gap ~<1.34 L never terminates (unreachable today) | HOLDS (read) | **PLAN** | document the idempotence / snapshot the art; tighten gen.c's guard when a random ver-6 landing is planned |
| contract-6b (D174) | contract | maintenance | `mfind-swar` etc. name the technique; persisted card deps, respellable until binding (§7.2) | — | **NOTED** | instrument-only names; decide before first merge to main if at all |

FIX-NOW ids (proposed): FIDELITY-1, contract-2, FIDELITY-2, DRAFTSETS-1, FIDELITY-3, DRAFTSETS-3, FIDELITY-4,
FIDELITY-5 (duplicate refusal), EMITTED-3, DRAFTSETS-5, DRAFTSETS-4, CHECKS-1, CHECKS-5, CHECKS-3, CHECKS-7.
Natural fix grouping: (A) slot timed shape: FIDELITY-1; (B) est record/draft: FIDELITY-2/3/5, DRAFTSETS-1/3/4 code,
contract-2; (C) the D197 rule: FIDELITY-4; (D) kit/test: EMITTED-3, CHECKS-1/3/5/7; (E) docs: DRAFTSETS-4/5,
EMITTED-1 card note, contract-3. (A)-(C) gate the mfcard timing window; (D)-(E) gate the landing only.

## Answer-level and speed-level summary

- No wrong match answer anywhere: zero movers under default flags HELD (BASE vs SUBJECT 204 SAME + 144 SIMD-target
  SAME + 15 harness SAME, 0 DIFF/RCDIFF; 116 pre-existing fixtures byte-identical); lever answers vs libpcre2 0
  disagreements over ~15M cases incl. guard pages, -march=native, x86-64/x86-64-v3, plus ~3.7M UTF-8 lever on==off.
- Measurement-answer level (the instrument's verdict): FIDELITY-1 (timed shape differs from shipped), FIDELITY-2/-5
  (record moves silently), contract-2 (draft sets unloadable), FIDELITY-4 (no declared decision).
- Speed/size level: EMITTED-1 (2.9-6x text), EMITTED-2 (swar vs libc measures width, not fusion; SUSPECTED).

## PROBED-AND-HELD (consolidated; case counts in the critic files)

- Zero-mover claim (emitted.md): ~1,030 compiles, 116 fixtures, `--hash` lines, 11 `--site-text` ids; every
  lever-free code path read; no path reaches the new text without the lever.
- Lever answers (emitted.md): ~15M + ~3.7M cases, two self-sabotages of the differential both LOUD.
- D197 code reach (draftsets.md): every setter of KIT_LEVER_MFIND traced; no default reach; plain build/pcrec
  refuses `--harness=mfind` (contract.md).
- §7.2 (draftsets.md): ver-6 rows 0/0/2 at BASE/main/SUBJECT, no ver-7, measure_store holds grid1/grid3 only:
  the `reject` respelling is allowed.
- Slot code-side identity (fidelity.md): KEY-ARM over 5 dims, CELL-TEXT hash, ISA check per target, REJECT-RATE,
  sentinel, round ACC: all code-side plants refused at dry time (P1, P1b, P2a/b, P3a, P4a, P4c; P4b SAME harmlessly).
- G2 reach (checks.md, by hand-instrumented census): every form entered and both accept/reject paths at every
  target; 6/6 unplanted mutants killed; each of S3150-S3159, S3173, S3174, S3170, S2930, S686 reaches its site and is
  caught by its intended detector (S3153 rightly SAME).
- Declared lists two-sided: rows.tsv, row_floors.tsv, simd_bounds.tsv, finder_check FORM_IDS, pins/arms.tsv.
- Contract (contract.md): card dims/deps match plan keys and formhash ids; counts consistent; no docs/spec hunk
  needed (lever test-only).

## By-id completeness

FIDELITY-1..5; DRAFTSETS-1..5; EMITTED-1..3; CHECKS-1..7; contract-1..6: every id has a disposition above
(DRAFTSETS-2 -> FIDELITY-2; contract-1 -> DRAFTSETS-5; contract-4 -> DRAFTSETS-1; EMITTED-2 -> FIDELITY-4).

## Standing questions (merged)

- **Sibling of a family** (three families found at three members each): (1) block-mask renderers vrun-w16/w32,
  vany, mfind (the final-block masking and the `ctz; m &= m-1` stream written a third time; emitted.md, contract.md);
  (2) G2 kernel runners run_g2_simd.py, run_g2_any.py, run_g2_mfind.py (scaffold copied; checks.md, contract.md);
  (3) "which ISA level is this" spelled three times (est TARGET_SET/LEVEL, record.py's cpuid ladder, the kit's
  targets.def; draftsets.md), and est checks timed-code facts per job KIND, not per fact (fidelity.md).
- **General form + unlocks** (proposed PLAN rows, build only on the trigger): one block-mask renderer table, whose
  (search, stream) factorisation IS D190's split shape (trigger: D197's WIN, or a fourth hand-rolled loop); a
  declared "timed-code facts" table est iterates for every ran job (trigger: now, via FIX group B); draft-set level
  derived from target facts (trigger: now, DRAFTSETS-1; unlocks mfind-w64's v4 set, non-x86 targets); a shared G2
  family runner with a path census and pinned lists (trigger: next kernel family or runner change); the timed shape
  as a cell fact compared with the emitted matcher's (trigger: now, FIDELITY-1).

## Recommendation (D27)

No new contract for a caller; a spec-first test author is not recommended for this subject. For the slot harness, a
D27-blinded author of the D197 decision rule (written from D197's text, before the numbers) would fit FIDELITY-4.

## Lessons for the guide (proposed)

1. harness fidelity lens, add a drill: compile the timed TU as the harness does and check that the site has ONE
   caller in it (`_time`); a gate in the same TU can change the timed code (FIDELITY-1: a second caller outlined a
   static inline finder). Compare against the emitted matcher's shape at the same target.
2. readiness/measurement: LOAD every draft set the harness writes with the tree's loader before the window
   (contract-2: two sets unloadable, the selftest pinned the refused shape).
3. check adequacy: a guard that compares two literals in one file is a control sharing its source; plant the
   CONSISTENT edit of both, not only one (DRAFTSETS-1: the selftest's mf_mixed planted one half).

## RULED (kit manager, 2026-11-15 ~12:40)

- Every PROPOSED disposition is accepted as drafted (FIX-NOW, PLAN, DOC, NOTED), with these rulings on the items left to the manager:
  - **contract-2 (unit row of the ver-6 sets):** each draft set REPEATS the unit's ratio-1 row (`kit.find_byte.walk`) so that it loads. The ISA-level guard exempts exactly that one row, the row the header's `unit_key` names. It is the set's normaliser, measured on the same box in the same run, not a priced form. §2.7 states the exemption in one sentence. The est self-test LOADS every draft it writes with the tree's loader (lesson 2). A new walk arm compiled at each level was rejected: more harness for no answer (the harness stays minimal, Frank 2026-10-21).
  - **DRAFTSETS-1:** the level comes from ONE source, the kit's own target facts (`--target-facts` / targets.def, through the cell's recorded `target_isa`). TARGET_LEVEL is deleted, and the guard fails a row whose recorded ISA needs exceed its set's class. Plants: the consistent two-table edit (P4), a mislabelled row (P5), a post-run cell_text edit (P11), each REFUSED.
  - **FIDELITY-4 (the D197 decision rule):** a DECLARED rule table, written now, before any number exists: the deciding cells, forms, the comparison, and the margin taken from the A/A floor. The default reading of D197: on find_hit@6, the best fused form at the box's ISA level (mfind-w32 on x86-64-v3, the timing box) against fn-memchr (libc as shipped: record the ifunc variant actually run, plus the AVX2-tunable arm the plan already holds) on the per-hit slope. A WIN needs a gain beyond the floor on the per-hit term; anything else is a LOSS. The rule goes to main (and Frank) for a yes BEFORE the window opens. EMITTED-2 is stated in the rule's notes: a swar-vs-libc row measures search width, not fusion, so it does not decide.
  - **FIDELITY-1:** gate from a separate TU, or call every form through a symmetric noinline wrapper; `_time` must hold the ONLY call site. Add a dry-run check that `_time` calls no local symbol, plus a plant that fails it.
  - **FIDELITY-5:** the duplicate refusal is FIX-NOW; the cells sha pin is a PLAN row for main.
  - **EMITTED-1:** a DOC note in the ver-6 card, and the emitted size reported beside the timing. The chain-once renderer is built only on D197's WIN branch.
- Groups (A)-(C) gate the mfcard window; (D)-(E) gate the landing.
- Lessons 1-3 and the proposed skill/COMMON text are ACCEPTED, and relayed to main: the skill and guide files are in main's tree.
