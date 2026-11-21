# covcap6 report — [COVER-CAP] design rev 4.1 (round covcap-r4 text fixes)

Lane covcap6 (opus), 2026-11-15. Branch `lane/covcap6`, from main `bf16c278f`. Design text
only: no edits under `src/`, `cli/`, `lib/`, `tests/` or `memfn/`.

## STATE AT HANDOFF

- Last ruling applied: R2 of `docs/dev/lanes/covcap6_rulings.md` (R1 and R2 both applied).
- PREMISE TEST held: `grep -c "REVISION 4" docs/design/cover_cap.md` printed 1 at the start;
  `src/gen/known.c` still has the loop FI-3 cites (`cc_eol`, lines 283-291 at `bf16c278f`):

      static bool cc_eol(CoverSt *st)
      {
          for (int j = 0; j <= st->w.k; j++)
              for (int i = 0; i < st->w.nlv[j]; i++) {

- DONE, committed on `lane/covcap6`:
  - `docs/design/cover_cap.md` REVISION 4.1: a 6-line "REVISION 4.1" block after the
    REVISION 4 block, header status and review list, and the per-finding edits below; no
    section restructured.
    SIZE: 51.1 KB / 671 lines against rev 4's 47.6 KB / 633 lines, NOT within R2's "aim to end
    no longer than rev 4". The eleven fixes each add a sentence or a list entry (READY-4's
    HISTORY list and FI-6's population sentence are the largest). No other text was cut,
    since R2 says to change only what the findings name.
  - Review `docs/dev/reviews/2026-11-15-r7-covcap-r4.md` (the draft with a "DISPOSITIONS
    (manager, 2026-11-15)" block holding R1 and R2 verbatim, and the title saying RULED)
    and the directory `docs/dev/reviews/2026-11-15-r7-covcap-r4/` (COMMON.md, fixinduced.md,
    readiness.md, verify.md, copied unchanged). Indexed in `docs/dev/reviews/CLAUDE.md`.
    None of these texts held a spec line cite or a plan line cite.
  - Two plan rows, filed as children of [COVER-CAP] (tags checked free in plan.md,
    plan_completed.md and decisions.md): [COVER-DEPTHS] and [NFA-PROV-CONJ]. `make
    test-plan-lint`: PASS (plan.md lints clean; selftest 45 plants, 0 failures).
  - Process edits (R1): `.claude/skills/pcrec-critic/SKILL.md` §4 (the premise lens row
    gained covcap-r3 lesson 1, "for each new LIMIT, find the existing limits on the same
    object ... does the object it limits exist at that size?"; the fix-induced lens row
    gained the depth-range mapping for a walk restructured into per-depth rules, with the
    guard-duplicate grep) and §5 (reuse the previous round's kit and trace compiler when
    `src/` is unchanged: repoint, sanity-run one known row). `docs/dev/guide/critics.md`
    "Lessons from review rounds" got a new r7 paragraph with the same three items.
- NOT applied: the review's DOC text nit on §3.3 ("a later part" vs "the compile's own
  re-ask after the key changed"). R1's FIX-NOW list does not name it. One open choice: READY-1
  offered `ac|bd` or `a[xy]c|b[xy]d` as S1131's facts witness. I picked `ac|bd` because
  `a[xy]c|b[xy]d` is plant (b)'s unique witness. Adding the row moves the facts floor 15 -> 16.
- `grep -rnE 'plan\.md:[0-9]'` over the review file, its directory and this report: no hit.
- OWED: nothing. No build, no run (design text only).

## FINDINGS APPLIED BY ID

- **FI-1** (owner example). §3.1 PAST THE CEILING: "The ceiling counts STATES, not
  positions: a straight line meets it at 4096 positions (`a{2047}b{2048}` is walked,
  `a{2048}b{2048}` is not), a machine with many paths meets it sooner (`[ab]*a[ab]{12}`, 13
  positions, gets no machine; `[ab]*a[ab]{11}` does)." §9 Q2: "... a pattern with many
  different paths meets it sooner (`[ab]*a[ab]{12}`, whose matches are 13 characters long,
  does)."
- **FI-2** (dead clause). §3.1 PAST THE CEILING: the `PCREC_MAX_TABLE_ENTRIES` clause is
  deleted. §8 THE BOUND THAT BINDS: "... derived in `limits.h` (§3.1). Nothing is added."
- **FI-3** (answer-relevant). §3.1 FORM rule 2: "Some row accepts in any form: the walk
  ends, `k = j`. C9 is checked on the rows at `k` too: C9 checks depths 0..k inclusive, as
  `cc_eol` does today (FI-3); C10/C11 then read them." §5.3 `verdict`:
  "`a(?:b|c)(?:$|q(?<=x))` decline `no-eol-view` (FI-3: its one non-identity eol view sits
  on the row at `k`, so a plant that drops depth `k` from C9 flips it; PCRE2 matches `ab\n`
  at (0,2))." §5.4: "S1136 and S1139 ... both re-anchor on the walk's C9 check at depths 0..k
  inclusive, the rows at `k` included (R-12, FI-3)."
- **FI-4** (listing `k`/`exact_len`). §3.3 THE RECORD: "`k` and `exact_len` (`uint16_t`,
  each with a known/not-known mark), `stop` (... ; `-` where no walk ran)". THE LISTING:
  "Where C1-C6 fail: the `why`, with `k` and `exact_len` by the rule below." WHERE A STRETCH
  IS STATED: "Other rows, C1-C6 declines included, read `exact_len` `-`; 0 is listed only
  where it is checkable. `k` is listed where `stop` is `accept` or `view`, else `-` (FI-4)."
  §4.5: "... the `k`/`exact_len` listing rule (§3.3 FI-4), and one sentence: a pattern whose
  anchored machine is not built lists `exact_len` 0 where its width is bounded, `-`
  otherwise."
- **FI-5** (x0.py horizon). §3.3 WHERE A STRETCH IS STATED: "(a stage-1 build item, FI-5:
  `x0.py`'s `stated()` gains a `wmax` column and passes `horizon=wmax` to `explore`, its
  header's row-format note says so; beside the `z2.py` re-point)".
- **FI-6** (`marked` guard). §3.1 THE SLICE'S THREE GUARDS: "rev 4 KEEPS two as lines at the
  top of `cc_anchored` ... (`erased`, `island`). The `marked` guard is C5's own test
  (`kset.c`'s guard is `dfa.c`'s `tagged`, which C5 `cc_unmarked` reads), so it is not
  repeated (FI-6). The build counts each over C4's population, which is larger than the one
  V-10 measured (compiles that reached C8): a count above 0 there is a `why` move from C5-C7
  into `anchored-A/erased|island`, listing-only (§5.2), not a lost cover." §5.2: "... or from
  C5-C7 into `anchored-A/erased|island` (§3.1 FI-6), moves no artifact (listing only)."
- **READY-1** (S1131's witness). §3.3 C8: "It is decision-redundant at rev 4: the rows at a
  branch stop never accept, so C10 declines whatever C8 declines; C8 names the `why`
  (READY-1, §5.4)." §5.4: "S1131 (C8 skipped): its `verdict` witness `ac|bd` cannot flip at
  rev 4 ..., so its witness becomes the `facts` row `ac|bd`, whose VALUE carries the `why`
  (`exact/machine-inexact` -> `end-at-k` under the plant), with the REACH record below." §5.3
  `facts`: the `ac|bd` row is added. The facts floor moves "by 10, to 16".
- **READY-2** (loader, VALUE). §5.3 `facts`: "The loader in `run_cover.sh` tracks the
  `#section cover` line (listing rows carry no section name) and keys each row on `$1`, the
  encoding (READY-2). A `facts` VALUE on this section is the row's `why | k | exact_len |
  sets` columns, tab-joined; the short forms above give `exact_len:sets`, and the build
  writes every value in full."
- **READY-3** (`MkEnd` fill bound). §3.3 THE RECORD: "`MkEnd` ... is filled from the record
  before C13 reads it (`cc_served` -> `pcrec_cover_site` -> `cover_window`), under §3.5's
  bound." §3.5 Stage 1: "Named build item (READY-3): the `MkEnd` fill from the record copies
  only for `k <= MF_MAX_SPAN_POS`, else the same named internal error, so plant (d) and
  `a{40}(?:b|cc)` (k = 41) never write past `MkEnd.set`."
- **READY-4** (cites, grep rule). §3.1: "(`compile.c`'s `build_anchored_dfa`; where it is
  absent, C4 `cc_anchored` in `known.c` declines)". Checked at the build tree:
  `build_anchored_dfa` is at `src/core/compile.c:382` and `cc_anchored` at
  `src/gen/known.c:194`. §5.5: "`docs/design/memfn/window_site.md`'s `MkLang` sentence
  (pcrec's design record for the kit: a pcrec edit), `docs/design/memfn/CLAUDE.md`,
  `scripts/NOTES.md`". Its line 635 names `MkLang`, checked. HISTORY is extended to
  "`plan.md` and `plan_completed.md`, the kit's ledgers (`memfn/docs/journal.md`,
  `responses.md`: pcrec cannot edit them), study data (`studies/selflip/sweep.tsv`), the Z2
  build's evidence kept as run (`docs/design/kit_proof/conj.py`, `witnesses.txt`,
  `x0/results.md`, `z2/stated_built.tsv`) and the fixture `scripts/tests/emit_sweep.py.test`".
- **READY-5** (INTO rule). §5.2: "`fixed-width` with the width's LOWER bound `wmin <= 32` at
  stage 1 (... READY-5: a dead short arm puts that depth above `wmin`, as in `a\z\W|b{32}`,
  width `[2,32]`, first accept 32)".
- **PLAN** (standing questions). Two rows, children of [COVER-CAP]:
  - [COVER-DEPTHS] — a `depths` column per conjunct in `cover_conj[]`, checked against the
    walk's record. Trigger: the next conjunct folded into the cover walk, or [MATCH-KNOWN]'s
    fraction case.
  - [NFA-PROV-CONJ] — one NFA-provenance conjunct kind shared by `cover_conj[]`,
    `lmwalk_conj[]` and `split_conj[]`. Trigger: the decisions-why section of §3.3 NOTED
    (R-14) is built.
  - Both name [ROWCONJ] in `refs:`.
