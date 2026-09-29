# clsdes88 — [CLS-TREE] design note: lane report

Lane clsdes88 (opus). Branch `lane/clsdes88`, worktree `worktrees/clsdes88`,
from `main` at `73590d19`, 2026-09-28. **Design only.** Nothing under
`src/`, `tests/` or `docs/spec/` changed. I ran no `make`, test suite or
heavy run. Study-harness work was Mac-side and box-independent: sizes,
automaton counts and exhaustive answer checks, with no timing.

## Deliverables

- `docs/design/cls_tree_design.md` — the design note, PROPOSED, revised
  after the light D6 panel r1. It has a row in `docs/design/CLAUDE.md`.
- `docs/dev/reviews/2026-09-28-r1-cls-tree-design.md` — the panel's
  findings and my dispositions. There was no BLOCKER; the two MUST-FIX and
  six SHOULD/NIT findings are all applied.
- New `studies/cls_tree_study/` pieces, each listed in its CLAUDE.md/README:
  - `wholeset.py`: whole-set 2- and 3-stage tables, plus a TS sweep.
  - `verify_whole.py`: an exhaustive verify with object sizes.
  - `automaton.py`: the UTF-8 byte automaton measured flat, minimal
    forward, minimal reverse, and reversed-forward.
  - `timefit.py`: tests the op model against the ubuntubudu ns/char data.
  - `bench.py --whole`, which adds the `runs` regime, and a `make bench2`
    target.
  - Results: `whole_k53.tsv`, `whole_uprops.tsv` (312 sets, 0 mismatches),
    `automaton_k53.tsv`, `page3_ts_k53.tsv`, `timefit_20260928.txt`.

## The decisions (note §0, CT-1..CT-9)

1. **The ops model is refuted, and λ is re-proposed.** The DP's `λ·Σops`
   term is a code-size proxy, not a time model. Against the committed
   ubuntubudu run (`bench_ubuntubudu_20260911.tsv`), which no document had
   read against the model, it predicts nothing among kit policies: on member
   subjects r = −0.00, and pairwise it ranks correctly 17 of 36 times
   (16/33 with the noisy `^C` dropped). So the five λ constants
   (4/16/16/64/256) that `opt_dial_design.md` §4 pinned select among
   matchers of equal speed. The DP stays, but its speed term becomes a
   per-probe time calibrated on ubuntubudu, and the constants are
   re-proposed as one ruled diff (D103).
2. **Whole-set tables are the fast form.** The one much faster arm has no
   dispatch tree: `bitmap1` is 3.8-4.6× faster than the kit. `MAXK = 64`
   made every whole-set table unreachable. A three-stage whole-set table is
   about the kit's size (`\p{L}` 4,249 vs 4,359 B; +3.4% over the 28 large
   sets) and has no branches. Whole-set sections become ordinary DP
   candidates. +2's huge-bitmap content comes from the DP at a high λ, not
   from a +2 special case.
3. **A wide class becomes one new AST node.** `A_WCLASS` is a new kind, not
   a flag on `A_CLASS`: 49 `case A_CLASS` arms and 6 comparisons assume a
   class is bytes, and r54 E1 would silently miscompile. During
   implement-then-replace it carries today's lowered alternation as a child.
4. **The VM uses decode plus the kit predicate.** The VM decodes with a new
   `static inline` `PCREC_ENCE_DECODE` entry, which is stage 4's ill-formed
   decoder verbatim; `SPAN_CASELESS`'s copy retires into it. The byte
   backend gets no row. This retires K55 and makes every captured wide class
   buildable, which is UCP's prerequisite.
5. **Byte DFA, compile-time half.** Splicing in the class's minimal
   automaton (299 forward / 453 reverse states, exactly the emitted DFAs'
   counts) cuts closure fan-out from 827 to 30 forward and 65 reverse, but
   shrinks no table. That build is gated behind [OPT-CLOSURE-CTX] and a K67
   re-measure. Its gate is DFA isomorphism, not byte identity.
6. **Byte DFA, island half.** The DFA-side consuming island is left to
   [ENG-ISL]/[UCP]. The note fixes only its interface and its trigger.
7. **Caseless** folds at construction and never at runtime.
8. **Retires:** K55's axes entry, captured wide-class refusals,
   `vm_cls_shape`/`-fno-cls-fold`, [OPT-CLSPACK] (proposed CLOSE), and K67's
   class share. **Stays:** [K53-SELRETRY]. The K53 known_fail rows were
   already gone on 2026-09-10.
9. **Staging:** S0 measure → S1 kit in `src/` → S2 byte tier on the VM (abi
   event) → S3 `A_WCLASS` byte-identical refactor → S4 VM decode+kit (abi
   event) → S5 splice (gated).

## Measurements owed

**(a) Mac, box-independent:**

- a1: byte-class whole-set sizes. The 312-set arm is done.
- a2: a classified census of the `A_CLASS` readers, with each "reads bytes"
  site's `A_WCLASS` answer.
- a3: S5's DFA-renumbering population.
- a4: K67 re-timed after [OPT-CLOSURE-CTX].
- a5: [FORM-CHAR2](i) asm counts for the kit's byte forms.

**(b) ubuntubudu, relayed to the pcrecdev2 executor:**

- **b1 is ready now.** The exact-command brief is note §7(b):
  `gnutimeout 7200 make -C studies/cls_tree_study bench2 CC=gcc`. It writes
  only `results/bench2.tsv`, expected 4,620 rows, and has its own load gate.
  Run it after this branch merges. It calibrates CT-2 and feeds the CT-3
  re-proposal.
- b2: byte-tier timing in the VM through pcrec-bench, after S2.
- b3: code-point tier in the VM through pcrec-bench, after S4.

## Questions for Frank (note §8; my recommendation in each)

- **Q1:** re-propose the λ constants after calibration, and keep the λ row
  at "reservation" until then. **YES.**
- **Q2:** retire `-fno-cls-fold`, add one `-fno-cls-kit`, and replace
  `RX_VM_CLS_FOLDS` with one activity stamp. **YES.**
- **Q3:** +2 means the same DP at a high λ, with whole-set tables as
  candidates. **YES.**
- **Q4:** keep S5 gated behind [OPT-CLOSURE-CTX]. **GATED.**
- **Q5:** close [OPT-CLSPACK]. **YES.**
- **Q6:** the island is out of this row's staging. **YES.**
- **Q7:** if UCP is next, order S0→S1→S3→S4 before S2.

## Findings outside the brief

- **The ns/char data had never been analysed.** The ubuntubudu timing run
  landed on 2026-09-11 and was cited as "the design gate's last input", but
  its data had never been compared against the model. It refutes the model.
- **One cell in that run is noisy.** `^C`/member is bimodal in the run
  (disclosed, and bounded by recomputing without it).
- **`(\p{L})` is refused today** at 1,187,962 B of emitted source against
  the 1,000,000 limit (probe at `73590d19`).
- **A minor inaccuracy in `ph3_reassessment_2026-09-28.md` §11(b).** It says
  the ns/char arm "is cited as done in the row's own text". The run is done,
  but the row still says "gated on". This is harmless now; noted for the
  manager.

## Resume point

Ask me or a fresh agent for follow-up once Frank rules §8 and b1 returns.
The next step is S0: fit CT-2's per-probe model from `bench2.tsv` and write
the λ re-proposal diff.
