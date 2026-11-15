# covcap2 — lane report ([COVER-CAP] rev 1, set S3, design only)

## STATE AT HANDOFF

STATE: delivered. Design only, NO BUILD GO: nothing under `src/`, `cli/`, `lib/` or
`memfn/` changed. Branch `lane/covcap` (worktree `worktrees/covcap`), on main `1b75dba61`.
Deliverable: `docs/design/cover_cap.md` rev 1, committed `86e9d11f4`, plus this report.

Rulings file `docs/dev/lanes/covcap2_rulings.md`: one entry, MAIN 2026-11-15 02:21 (read
the finished rev 0 round's `review.md`; answer PREMISE-1 and COST-1 explicitly), APPLIED
in §3.4 and §4.4 and in the §9 table.

Premise test passed: `limits.def:392` still has `PCREC_PREFIX_K_MAX` 24, and
`memfn.h:277` still has `MF_MAX_TERM` 32.

Box use: about 130 single-pattern `build/pcrec` compiles (main tree binary, current) and
72 `gcc -O2 -S`, all under `timeout`, mostly at `nice 19`. Scratch:
`/var/tmp/pcrec-pcrec/scratch/covcap2/` (`bench_pats.tsv`, `size.tsv`). No make, no
suite, no timing. Nothing owed by this lane.

## WHAT ELSE IS BOUNDED

The full inventory is design §1: about 30 bounds, each with a verdict (OWN / INHERITED /
BUDGET / SCRATCH). The ones that matter:

- **pcrec, removed by rev 1.**
  - The slice's exact loop at 24 (`kset.c:911`) and its liveness horizon at 48
    (`kset.c:891`). Both are borrowed from the k-set walk, and the horizon is why a
    49-byte literal lists `span_facts 0` today.
  - `MkLang.set[24]` and `uint8_t exact_len` (`facts.h:305-306`).
  - `KN_CAP = MF_MAX_SPAN_POS` and its arrays in `kn_walk` (`known.c:34`, `:41-45`).
  - The sentinel off-by-one (`known.c:132`, `:250`).
  - The guessed rows-per-depth cap `d->n * 4 + 8` (`known.c:129`).
  - `MkEnd`'s `uint8_t k` and `set[32]` (`known.h:24`, `:28`).
- **pcrec, kept.** `PCREC_SPAN_WALK_SUBSETS` (512), the one compile budget. It is a
  sound under-statement and labelled UNMEASURED, with a census owed. NEW FACT: it is a
  CLIFF, not a cut. Past it `exact_len` is 0, not a shorter prefix, so it acts as a
  length bound near 511 positions on a literal (design §3.3).
- **The seam, inherited.**
  - `MF_WSPAN_POS = MF_MAX_SPAN_POS = MF_MAX_TERM` = 32, which comes from emit_vm.c's
    `VM_MAX_STRIDE`, a VM stride. A REPORT window is never translated to terms.
  - `mf_wspan`'s `uint8_t len/core` and fixed `set[]`/`table_ref[]`.
  - `MF_WREACH` 64.
  - The proof range `[-8, 33)` and `mf_class.proven[]` (MF_CLASS_V).
  - `MF_WPLAN_MAX`, with `mf_wreply.plan[]` and `nplan`.
- **The kit's own.** `WF_NPOS`, D-hors's `uint8_t` shift (window.c:1850's static
  assert), and `run_bytes`' `2 * MF_WSPAN_POS` buffer. These are listed for the kit,
  which decides how they move (D157).
- **A hazard found.** If pcrec stated `k` > 32 against today's seam, `cover_window`
  would WRITE PAST `mf_wspan.set[32]` (`pcrec_memfn_wpos_bits`, no index check) before
  `window_bounds_check`'s loud failure ran (`memfn_sites.c:559`, `:590`). That is why
  stage 1 keeps one capacity row.

## DESIGN REV 1

Design §3.

1. **The slice states as far as it proves.** No depth bound; the budget alone ends
   exploration. Monotone: the critics' depth-order argument holds with no horizon, so no
   set stated today changes and `exact_len` only grows. `MkLang` becomes a counted arena
   list.
2. **The machine reading walks to the slice's `exact_len`** and no further: C8 cannot
   admit past it. That gives one bound for both producers and no constant. There are
   three explicit outcomes (k found, `ended`, past the slice), which replace the sentinel
   (SOUND-4/PREMISE-6). Rev 0's C7 fix survives in substance.
3. **Two stages.** Stage 1 is pcrec only. It adds a conjunct `C15 statement-fits` that
   reads the KIT's present capacity (k ≤ 32), so pcrec has no bound of its own and the
   overflow above cannot happen. Stage 2 comes with the kit's counted seam: C15 is
   retired.
4. **abi.** Both stages are pcrec abi events: a bump and a re-pin. The recursion
   identity gate's D76 block defines (B)'s pin as "the commit that introduced the
   CURRENT `abi`". The movers `litrun.rxt:1204`/`:1320` are in its call-free population.
   Stage 2 also moves kit bytes (D146/D147).
5. **Size (PREMISE-1, measured like-for-like at k = 4..24, cover against
   `--memfn=no-window-search`).** The cover's text is LINEAR in `k` on every shape:
   - distinct-letter literal: 30 / 33 `.s` lines per position (byte / utf8), against
     the engine's 61, so literals win more as they grow;
   - `[0-9a-f]{k}`: 8 / 25 lines per position, against a FLAT engine (scan edges);
   - `\b[0-9a-f]{k}\b`: 20 / 31 lines per position, against the engine's 6.

   Class runs cross over near k = 20. The fact that answers the growth is one pcrec
   holds: which positions share ONE set. It is offered to the kit as `(set, count)` runs
   plus table offers, with no form named.
6. **Spec (D80).** The `facts_listing.md` §4.1.2¶7c hunk is REQUIRED. `limits.def` gains
   no row, and P4's description changes.

## SEAM CHANGE

Design §4.1-§4.2.

- **What crosses.** pcrec states one span of `k` positions, with contexts at -1 and at
  `k`. It reads the proof at every offset in `[-1, k]` (C14 equality) and the reply's
  `stop`. Nothing else on this path.
- **Stage 2, pcrec's side.**
  - `cover_window` and `pcrec_cover_proof_diff` read and write counted lists.
  - `window_bounds_check` mirrors the kit's new check.
  - The other window sites (OFS, reseed, the run pre-check) state what they state today
    and must sweep byte-identical.
  - `pcrec_known_derive` (no caller) is bounded by the counted range, or deleted.
- **Events.** An `MF_SITE_ABI` event, an `MF_CLASS_V` event where the reply moves, and
  a pcrec `abi` event, all in one landing.

## ANSWER IDENTITY PLAN

Design §5.

- **The suites.** `make test`, `make test-axes` (the deny arm against default), and
  `test-kitproof` new rows against libpcre2 10.46. The rows cover lengths 24/25/32/33/40/
  100/1000 for a literal and `[0-9a-f]{n}`, and 32/40/100 for `\b[0-9a-f]{n}\b`.
  Verdict, facts and answer rows are expected per stage, and the budget's cliff L* is
  bisected by the build, never pre-stated.
- **Byte identity.** `emit_sweep.py`, predicted == observed from the BASELINE's
  `KITPROOF` records and `width` facts, with the `abi` stamp normalized. A listing-only
  population is widened (SOUND-1).
- **Other controls.**
  - The default build's proof-diff internal error.
  - The trace build's C8 assert, and X0 on movers.
  - `make asan` over the kitproof and litscan sections (counted arrays replace fixed
    ones).
  - The `REACH_ONLY` sabotage matrix.
- **Sabotage.** Four plants, each with a UNIQUE witness (SOUND-2/3):
  - (a) the exact loop bounded again: `facts` 40-literal;
  - (b) the horizon left at 48: `facts` 50-literal, `50:` → `0`;
  - (c) the machine walk one depth short: `verdict` 25-literal;
  - (d) stage 1 with C15 removed: the 40-literal compile's internal error.

## MOVERS ESTIMATE

Design §6.

- **Stage 1.** Bench `lit-l31`, `hex32`, `dig-exact-32` and `hex32-id`, each in both
  encodings: OBSERVED on the rev 0 premise critic's planted compiler. Corpus
  `litrun.rxt:1204` and `:1320`.
- **Stage 2 (PREDICTED).** Adds bench `lit-l40`, `loglines/uuid` and
  `wild-validator-uuid-grok` (36), and corpus `a{500}` (below the cliff if L* ≥ 500) and
  `(?:ab|ba|aa|bb){24}c` (49).
- **Not moving.** `wild-secrets-github-pat` (93 positions, a capture; its uncaptured
  twin covers), `uuid-near-miss` (attempt route), `slack-webhook` and `line-80`
  (variable width), `[ab]{1000}` (past the budget), and `(ab){300}` (a capture).
- **Rulepilot.** `(?i)permission is hereby granted` moves under byte only (PREMISE-3).
- **kvcensus.** The query is stated (status ok, exact, span ≥ 25): bench 14/13, corpus
  48/17.

## KIT REQUEST DRAFT

This is the full text of design §4.3, for main to file (facts only, D157). Its parts:

- FACT 1: pcrec states a span of any `k`. The population is listed, from 31 to 500.
- FACT 2: pcrec reads the proof over `[-1, k]` with an EQUALITY check. Today the range
  ends at 33.
- FACT 3: the measured per-position text slopes. pcrec can state `(set, count)` runs,
  and whether to use them is the kit's call.
- FACT 4: a table offer per distinct set.
- The bounds on the path, as pcrec reads them. Which of them move is the kit's call.
- ASK: (1) can the seam carry any length, and in what form; (2) confirm the slopes, and
  can a long one-set run render without per-position text, and at what cost; (3) G2
  cases past 32.
- Deliver: a kit branch, for one landing with pcrec's stage 2.
- GO: none yet.

## QUESTIONS

Owner questions are in design §8, in plain words:

1. One step or two (leaning two: stage 1 now, which covers up to 32).
2. Do we accept code growth on long class shapes at stage 1, with stage 2's landing
   held on the kit's size answer? Leaning yes, and the answer is not a length limit.
3. Keep the 512 compile budget and count where it binds? Leaning yes.
4. A build go for stage 1, at opus tier.

For main:

- [DD-11.5] rebases on the counted `MkLang`.
- [DEC-LIMITS] does not fire (no new row).
- A plan row for PREMISE-7's family of borrowed bounds (`run_pin`'s 24 clip, K38-2's
  verified extent, `MF_WMAX_SPAN`'s derivation), proposed at BOONIES.

Contradictions with the brief are listed in design §10:

- the budget is a cliff;
- stage 1 cannot be bound-free against today's seam;
- the 1000 row declines at every stage;
- rev 0's C7 fix changes form.
