# R-46 reply, revision 2 (kit lane r46rev, 2026-11-20)

STATUS: REVISED DRAFT for the kit manager. It applies the design review
`/var/tmp/pcrec-pcrec/scratch/crit-memfn-r46/review.md` (light round; critic texts in its `review/`). Every FIX-NOW
finding was ACCEPTED as proposed (rulings.md 10:40) and MEAS-3 is noted. Main answered **bounded-horizon-scope** at
10:35: SUPER-DENSE. The bounded row therefore states NO horizon. This is main's reading and can be revisited. The
other branch has been cut, so this file contains no switch block. Finding ids are cited where each change lands; the
full map is in `v2_changes.txt`.
This is a read-only lane: nothing was committed, nothing was built, and no make or timing was run. The tree read is
main @ f8789cd2e, plus main's next REQ-PAST-LAST record commit 0384981c5 (the dense-not-target record). The kit branch
lane/memfn-k1108 differs from that tree only in the span-form text of window.c and vrun.c, which this reply does not
touch. The emitted-text witnesses are `unb.c` and `bnd.c` in this directory. Both come from `build/pcrec` (built
2026-11-19 19:09) on the two patterns in tuning.md §2.41¶8c.
The kit's ack (responses.md on lane/memfn-k1108) promised "a critic round on the reply before it is posted". That round
has now run (the review above). This revision is the text to post.

---------------------------------------------------------------------------------------------------------------

## (a) Draft responses.md entry (paste-ready)

- done: R-46 (2026-11-20, kit manager) — DESIGN REPLY only (no build go either side; nothing built; critic round run).
  The re-asked pre-check on dense occurrences ([REQ-PAST-LAST], unit U1-k of docs/design/dense_hit_arch.md).
  - **(1) As it stands? NO.** ALL_PRESENT + ASSIGN answers one question, the LEFTMOST hit of preds[ret_pred] in [lo, n):
    sound for the weaker question but the costliest answer, and the bounded row's move (`landmark_position - K`) is
    sound only on the leftmost, so a weaker single answer breaks it. The site needs a SECOND answer beside the leftmost.
  - **Form: the leftmost stays; a HORIZON is added** (precedent `count_by_caller` + `count`). Define fact
    `mf_site.horizon_gap` (appended LAST, OBLIG, stated by NAME like `head_max`): 0 = no use asks a horizon (every
    site today) or MF_GAP_UNBOUNDED; a finite gap (the general form) is refused by site_check, no customer (D77). Use
    hook `mf_hooks.horizon` (appended LAST, an lvalue like `result`; NULL = not asked). On a hit `result` = the
    leftmost c as today, `horizon` = an occurrence f with c <= f < n, which f is the kit's (D157), f = c always
    correct; on a miss neither is promised and `on_miss` runs.
  - **Who states it (CONTRACT-2, SOUND-2):** only the VM `handoff-attempts-unbounded` row's re-entry use. The bounded
    row states none: its benefit falls only on hits within K + 1, read by main as SUPER-DENSE under the owner's
    working scope (discussion, slug dense-not-target; docs/design/plan_row_bodies/REQ-PAST-LAST.md; revisitable);
    its measured loss (§2.41¶8c) is NOT addressed here. The entry's use and the DFA/hybrid re-entry keep NULL.
  - **Safe (inference; pcrec's design confirms; the critic's exhaustive model held it):** the unbounded row never
    moves, so re-asking only once the attempt passes f runs today's attempt sequence exactly: answer- and
    give-up-identical on every subject and step budget.
  - **Kit's leading method (not the contract): FORWARD only** (CONTRACT-3/4): f = the last occurrence in (c, c + w],
    w = min(B, max(1, lo - start)) (MEAS-1): per search call, look-ahead the search never needed is at most the
    distance it already covered; O(log B) asks to reach B on dense occurrences; B = the page size (the owner's
    constraint). Scalar arm composes today's forward FIND (one call per occurrence in the window, MEAS-2); a
    one-pass forward "last occurrence in a range" form is NEW work with its own card and deny; no reverse form.
  - **(2) What moves.** `ret_pred`'s meaning: nothing. Two fields.def rows plus a class for MF_GAP_UNBOUNDED;
    non-serving rows declare `[FLD_horizon_gap] = CM(ZERO)` in the three shared serves macros, `horizon` needs no
    entry off the serving rows (CONTRACT-1); serving rows: the pre-check ASSIGN rows and generic, first text
    `horizon = result`. G2's leftmost reference UNCHANGED; NEW: a D27-blinded horizon reference and three fail-closed
    gate cases; the presence family's site-file pins re-pinned by name (CONTRACT-7). No MF_VOCAB/MF_CLASS_V move;
    DELEG_SITES `PRE` unchanged.
  - **(3) Seam event, no mover? YES:** MF_SITE_ABI (next number at landing), ZERO emitted-byte movers while every site
    states 0 (emit_sweep, arms.tsv, G2 quick verdicts, link/stack, the arch note's U1-k checks). Land it as U1-k's
    first commit under pcrec's build go, not ahead (D77). The METHOD is a byte mover: one pcrec abi event with the
    consumer step (new origin argument, CONTRACT-6; deny row + docs/spec hunk, D80; card; D144 alpha both layers),
    and only if pcrec's owed post-K38-2 re-measure still shows the dense loss above noise (CONTRACT-8).
  - **Card and controls (MEAS-4..7):** three arms (method; its own deny = today's text; the public deny); adversary
    cells named; cold verified by mincore, not tmpfs; a deterministic COUNT control; value sabotages land with the
    method row. Open: Q1-Q11 in the design notes (/var/tmp/pcrec-pcrec/scratch/memfn/r46/reply_v2.md, to move into a
    kit design note at the build go). Nothing filed, nothing built.

---------------------------------------------------------------------------------------------------------------

## (b) Supporting design notes (FACTS with file:line; INFERENCES labelled)

### B1. The question as it stands (FACTS)

- F1. The reply contract is the leftmost. `memfn/include/memfn.h:856-857` says "ALL_PRESENT: RETURN/ASSIGN the
  leftmost hit of preds[ret_pred]". See also `docs/design/memfn/integration.md:6931`, `:7114` ("LEFTMOST position of
  predicate `ret_pred` (as FIND would return it)") and `:7241`. G2's reference is `memfn/tests/g2/g2_ref.c:265-275`;
  its pins are `tests/memfn/run_arm_pins.sh:100` and `:762`.
- F2. `ret_pred`, `op`, `handoff` and `on_miss_leaves` are define-phase: `memfn/src/fields.def:189`, `:192`, `:211`,
  `:217`. `use` is in `mf_site` (`memfn.h:862`, "PER INSTANCE (§14.5)") and is not an MF_FIELD. Only site_check's
  enum check reads it (`compose.c:929-930`); no `serves` declaration gates it.
- F3. The re-entry REUSES the entry's site and handle. Its use hooks are `.lo = posvar`, `.n = "subject_length"`,
  `.result = "landmark_position"` and `.on_miss = REQ_ON_MISS` (`src/gen/emit_dfa.c:1762-1777`, in
  `emit_req_reentry_use`).
  - The PRE site is defined once, in `req_site_define` (`emit_dfa.c:1556`).
  - That define sets `s->use = MF_USE_ENTRY` (`:1639`).
  - It sets `head_max` to K or MF_HEAD_MAX_UNBOUNDED (`:1644`, `:1648`).
  - Its define hook is `.start = PCREC_MF_ORIGIN` (`:1657-1659`); `src/gen/memfn_sites.h:284` gives `"search_from"`,
    a parameter of the entry function (`bnd.c:258`).
- F4. DELEG_SITES `PRE` is at `src/gen/memfn_sites.def:59-60`: ALL_PRESENT; ON_MISS | ASSIGN; SET | RUN; DELEG_SCAN;
  MF_USE_ENTRY; DELEG_ENTRY_SELF.
- F5. The emitted loop (witness `bnd.c`, `[^@ ]{1,5}@x --engine=vm`, lines 309-317) runs as follows after each failed
  attempt:
  - `attempt_position++`;
  - `if (landmark_position < attempt_position) { landmark_position = rx_reqrun(...,
    attempt_position); if (landmark_position >= subject_length) return 0; }`;
  - then, UNCONDITIONALLY, `if (landmark_position - attempt_position > 5) attempt_position = landmark_position - 5;`.

  The unbounded witness (`unb.c:306-309`) has the ask and the stop but no move. The out-of-line function is
  `rx_reqrun(subject, n, pos)` (`bnd.c:250-252`), which has no origin argument.

  **SHARED TEXT (SOUND-2, CONTRACT-5):** `emit_req_landmark_move` (`emit_dfa.c:7952-7974`) and
  `emit_req_reentry_use` (`:1762`) have TWO consumers:
  - the VM attempt loop (`pcrec_emit_req_attempt_reentry`, `:7987-8004`), which is what R-46 asks about;
  - the DFA forward scan's handoff (`pf_emit_handoff`, `:7926-7938`, [REQ-HANDOFF-L1]). It asks only where the scan
    is back at its start state with no accept pending, and its move rounds up to a character start and reseeds the
    machine (`:7963-7971`).
- F6. The pre-check's ASSIGN renderer keeps the leftmost (`memfn/src/precheck.c:13-15`). Its rows' serves are at
  `precheck.c:438-457`, `:509-510` and `:527-528`. generic.c serves `MF_ANY` on ret_pred (`generic.c:818`) and
  renders ALL_PRESENT from `:305` on.
- F7. Reverse is unserved by every fast row (CONTRACT-3).
  - `MF_OP_FIND` has a backward reading in the VOCABULARY ("last, if reverse", `memfn.h:339-340`).
  - Every fast row serves `reverse` CM(NO): ofsskip.c:981 and :1071, pffind.c:359, vrun.c:730, precheck.c:439. Only
    the generic row serves it (generic.c:813, MF_ANY).
  - memfn.h refuses `reverse` at W > 1 (`:1118`, "no customer, D77").
  - ALL_PRESENT refuses `reverse` (`memfn.h:373-375`).
- F8. No row reads the start hook today: `memfn.h:1171-1181` says "No row reads it now". The `start` row is
  `fields.def:386-390`. It is MF_PH_DEFINE and is "Read at define (pcrec states it there and at its mf_locals, which
  binds it)". (CONTRACT-10: the draft cited `:313`, which is the `lo` row.)
- F9. Version macros at main: `MF_SITE_ABI 30` (`memfn.h:39`), `MF_VOCAB 4` (`memfn.h:277`).
- F10. The arch note's U1-k and the r49 rulings:
  - `docs/design/dense_hit_arch.md:276-295`: gate, instruments, separability. `:287-290` lists the checks that bind
    U1-k: G2 presence cases, `mf_vocab_has`, and `tests/memfn/run_presence.sh` over
    `tests/litscan/presence_deny.rxt`.
  - `:314-315`: the G2 reference is written by a D27-blinded kit author.
  - `:239`: A-PLAN.
  - `:419-421`: the budget column is handed to the design.
  - Review `docs/dev/reviews/2026-11-18-r49-archdense.md:95-149` (groups C, D, E, F).
- F11. The owner's record is `docs/design/plan_row_bodies/REQ-PAST-LAST.md`. It holds three items:
  - lookahead-home, RULED: how the position is obtained is the kit's method;
  - starts-or-occurrences: occurrences, a search loop, for now;
  - (added at 0384981c5, the commit after f8789cd2e) **dense-not-target**: DISCUSSION, not a ruling. This is the
    owner's WORKING SCOPE: "Dense for me could be defined as two+ hits in a single block if we use blocks. Super
    dense might be hits within some low N like 8. I don't know N", together with main's reading of
    bounded-horizon-scope ("hits within K+1 of each other ... are SUPER-DENSE, outside the target; the BOUNDED
    handoff row states no horizon, only the UNBOUNDED row uses it"; revisitable).

  NOTE 3's B constraint is quoted in R-46. NOTE 3 itself, as recorded at `dense_hit_arch.md:60-67`, is
  "blocks instead of doubling" with a forward-only candidate.
  (CONTRACT-2: the draft paraphrased this scope as a ruling and dropped "(hits within N)"; corrected here.)
- F12. Blockanalysis Q4 (`/var/tmp/pcrec-pcrec/scratch/memfn/blockanalysis/report.md`, section Q4; this is job 709,
  the "N" the scope discussion asks to be read first) measured the spacing at which a block span form stops beating
  today's:
  - about k for SWAR on hex/word;
  - none up to 64 for AVX2 on hex/word;
  - 2-4 (SWAR) or about k/2 (AVX2) for `[^\n]`.

  It measured a different site (window spans), on Zen 4 only, and only on hex, word and not-newline classes.
- F13. Sibling precedents (contract lens, standing questions):
  - `count_by_caller` (define, OBLIG) with `count` (use hook): fields.def:220-224 and :338-345. This is the same
    shape: a define fact that changes what a use hook means. Copy its documentation, NOT its MF_ANY serves.
  - `head_max` with `MF_HEAD_MAX_UNBOUNDED` (memfn.h:324-327, :947-966): the twin sentinel, stated by NAME.
  - `moved` (PR-2, fields.def:392-398): a define-read extra hook that fails closed onto a short list of serving rows.

### B2. Why a second answer, not a weaker first one (INFERENCE from F5; CONFIRMED by the soundness lens)

The bounded row's move test runs after every failed attempt, on whatever value sits in `landmark_position`. Suppose
the kit returned a far occurrence f in place of c.
- Then `f - attempt_position > K` would hold for most positions in [c, f - K).
- The loop would jump to f - K and skip starts in [c - K, f - K) that can match. That is an answer change.
- Witness: `[^@ ]{1,5}@x` on `@xaaaaa@x@x`. Today's loop gives `match 2 9`; the weak single answer gives `match 4 9`.
  The soundness lens counted 392 answer changes over subjects of length 0..11.

The unbounded row has no move (F5), so a weaker single answer would serve it alone. One contract for both rows
therefore keeps c, for the move and for the entry, and adds f. Under main's bounded-horizon-scope reading the bounded
row asks no horizon now. Because the form keeps c, a later revisit needs no contract change, only a finite-gap
admission (B3.2).

### B3. The identity argument

**B3.1 The unbounded row (the one that states a horizon; INFERENCE, held by the soundness lens's model).**
Today's unbounded loop (`unb.c:306-309`) does the following:
- An ask at attempt position a returns o, the leftmost occurrence >= a.
- It stops iff there is no such occurrence. It never moves.
- It re-asks when a passes o.

The new loop keeps H = f from the last ask and asks only when a > H. For any a in (c, f], an occurrence >= a exists
(f itself), so today's ask there neither stops nor moves; skipping it changes no attempt. At the first a > f, both
loops ask, because today's kept occurrence is at most f < a. By induction the attempt sequences are equal, and so are
the answers, give-ups, callouts and step counts.

The model's evidence: zero differences for every permitted f (the farthest, random choices, and f = c). It covered
exhaustive {a,@,x,space} subjects of length 0-11 (5,592,405 subjects) on 19 VM patterns, length 12 on four
patterns, 2M random subjects (length 13-60) and 20k long ones (length 500-3000) per pattern, and step budgets 1-32.
The variants skipped real asks, so the test was not vacuous.

**B3.2 The general form, kept for a revisit (the bounded row; NOT stated now).** For a loop that also moves to c - K
on an ask, a horizon f is safe when every two consecutive occurrences in [c, f] are at most G apart, with G = K + 1.
- For a between consecutive occurrences at most K + 1 apart, today's re-ask neither moves nor stops.
- **G = K + 1 is TIGHT (SOUND-1).** G = K + 2 changed attempt sequences on 7 of 14 bounded patterns. Under a step
  budget it also changes the ANSWER: `[^ ]{1,4}@@` on `@@ @@aaaa@@`, find-all, budget 8, gives `match 5 11` today
  and `PCREC_ERR_STEPS` at K + 2.
- Wording (CONTRACT-9): pcrec states G. For a loop of this shape the kit's inference is K + 1 with K >= 0 (`head_max`
  is signed in the kit; pcrec's handoff rows are gated k >= 0, `emit_dfa.c:9023`, `:9118`).
- When finite G is admitted, site_check should gain an agreement rule (G <= max(K, 0) + 1 where `head_max` is stated),
  or the design should say why none is needed. That is pcrec's design step.
- The finite gap stays refused by site_check until a customer exists.
- The bounded row's other remedy is a BATCH reply (the next m occurrences), which also covers spacing in (K + 1, B).
  Its trigger is in Q11.

**B3.3 Hazards for pcrec's consumer text (SOUND-2; the kit's text is unaffected).**
- (i) The move test must never run with `landmark_position < attempt_position`. `landmark_position -
  attempt_position` is a size_t and wraps. The soundness lens's witness: VM `[^@ ]{1,5}@x` on `b @x @x @x` loops
  forever with the unconditional move after a horizon, where today returns no match after 4 attempts.

  Today this cannot happen, because the ask precedes the move whenever L < a. Any later bounded horizon must keep the
  move, and in the DFA consumer also the round-up and the reseed, gated on the ask.
- (ii) `.horizon` must NOT be set inside the shared `emit_req_reentry_use`. Setting it there would silently change
  the DFA/hybrid consumer too. The DFA consumer's identity under the same rule was modelled and held
  (5.6M exhaustive + 2M random per pattern). It still stays NULL until pcrec argues its own case.

### B4. The leading method and its costs (INFERENCE; to be measured)

- **The window (MEAS-1).** w = min(B, max(1, lo - start)). `start` is the activation origin the site already states
  (F3), and the max(1, ·) never binds at a re-entry, because lo > start there.
  - The draft's max(G, ·) floor is gone. It made w >= G at the first re-entry (1001 bytes read after 11 covered at
    K = 1000), and w = B from the first ask on the unbounded row.
  - The gap G no longer enters the window at all: only the unbounded row states a horizon. Under a later finite G
    it would cap each chain step only, never the window.
- **The waste bound, re-checked against the new rule.** Look-ahead read past f by ask i lies in (f_i, c_i + w_i]. On
  the unbounded row f_i is the last occurrence in the window, so the next occurrence c_{i+1} > c_i + w_i.
  - If the search continues, its next forward scan re-reads that tail. That is a re-read, not waste.
  - Only the LAST ask of a search call can read bytes the call never reaches. Those bytes number at most
    w_last <= lo_last - start: the distance the call has already covered.
  - So "waste <= progress" now holds for every search call, including the first re-entry and the unbounded row.
- **Re-reads (MEAS-3, noted).** The draft's "at most about three reads per byte" and "O(log B) asks to reach B" held
  in the measurement lens's model: 300 layouts, maximum 3. That model used the draft's rule. The new rule has smaller
  windows, so the bound is expected to hold. The COUNT control below re-checks it.
- **Ramp.** On dense occurrences each ask lands its next lo just past c + w, so lo - start roughly doubles per ask.
  That gives O(log B) pcrec-visible asks to reach B, then one per B bytes. No floor and no tuning constant are
  involved (MEAS-6).
- **Forward only (CONTRACT-3, MEAS-4).** f = the last occurrence in (c, c + w], or c if there is none. Two arms are
  possible:
  - **The composed arm, no new form.** Repeat today's forward FIND inside the window, from each occurrence + 1, until
    it misses. This takes one FIND call per occurrence in the window, plus one.
  - **The one-pass arm, a NEW forward form.** One forward pass over the window keeps the last occurrence: a scalar
    byte loop, SWAR, or the block masks' highest set bit, per layer. It carries its own card cell and deny row inside
    the method commit, and is chosen only if the card shows that the composed arm's per-occurrence call cost eats the
    gain.

  No reverse form is needed, so the scalar-only reverse FIND of F7 never arises. The draft's backward FIND is
  dropped.
- **What falls and what does not (MEAS-2, CONTRACT-2).** pcrec-visible asks on the unbounded row fall from about one
  per occurrence to the ramp above. In the composed arm the kit's own FIND calls do NOT fall: they stay about one per
  occurrence. The composed arm's gain is only the difference between a kit-internal bounded FIND step and pcrec's
  out-of-line call, compare and loop turn per occurrence. That gain can be zero, which is why the one-pass arm is the
  expected winner. The COUNT control reports both counts.

  The bounded row is unchanged: it states no horizon, its text is today's, and so is its loss.
- **Sparse occurrences (one per window or fewer).** f = c, today's cadence. Extra cost per ask: one failed window
  scan of at most w bytes, which the next forward scan re-reads.
- **Early match (the find-all shape).** The waste is bounded as above. The worst layout is a kept hit, then no
  occurrence for w bytes, then a match: the last ask reads w <= the covered distance. It is a card cell (MEAS-5 i).
- **Cold memory-mapped subjects (MEAS-4).** The scan is forward, so pages are first touched in ascending order (the
  draft's backward scan, which faulted the window's LAST page first, is gone). The argument does NOT show that the
  look-ahead adds no NEW page faults:
  - The window can reach pages the search itself never touches when the match comes first.
  - With w <= B = one page, that is at most one extra page per search call.
  - At B = 16 or 64 KiB on this 4 KiB-page box it is up to 4 or 16 pages.
  - The kernel's mmap read-around may already hold them. That is a measurement, not an argument, and the cold cell
    decides it.
- **D149 (MEAS-6).** B is derived from a system constant. w's rule is derived from the cost bound above and now earns
  that label: the old unlabelled floor max(G, ·) is gone. No other number appears.

  PREDICTION, stated in advance: on the silent-window early-match cell the waste scales with B. Insensitivity across
  4/16/64 KiB is therefore likely to FAIL, and the owner's rule then selects `sysconf(_SC_PAGESIZE)` at run time. In
  that case comparator (1) becomes a per-platform property: this Linux 4 KiB box cannot measure a 16 or 64 KiB-page
  target.

### B5. The three standing questions (docs/design/CLAUDE.md)

1. **MEASUREMENT REGIME.** Relevant: a new method with a page-derived size.
   - Throughput per search call on the card's cells. Per-call cost dominates the sparse and early-match cells;
     per-byte cost dominates the dense ones.
   - Both kit layers, warm and cold, on the Linux dev box (Zen 4), taskset-pinned, with calibrated loops and absolute
     deltas against the floor.
   - A Zen 1 or Mac reading may flip the in-window form (composed or one-pass, per layer), not the contract.
   - **Cold (MEAS-4):** posix_fadvise DONTNEED before each mmap, with coldness VERIFIED by mincore before the timed
     call. The file lives on a disk filesystem, never tmpfs (where DONTNEED is a no-op).
   - Timing windows are main's, cleared with the owner (night preference).
   - **CELLS (MEAS-5).** Unbounded row:
     - dense spacing 2, 3, 8, 64, 512, 2048;
     - sparse (spacing > B);
     - early match after j = 1..64 failed attempts, on two layouts: passing hits (benign), and (i) a kept hit, then
       NO occurrence for B bytes, then a match, find-all;
     - (iv) the first re-entry at find-all rate;
     - B in {4, 16, 64} KiB.

     Bounded rows K in {5, 64, 1000}: one no-mover cell each, to confirm today's text and cost (they state no
     horizon). Cells (ii), spacing G+1..2G, and (iii), spacing 2 per K, are NOT needed now; they come back with any
     finite-G revisit, and spacing 2 stays in the unbounded list.
   - **ARMS (MEAS-5): THREE.**
     - (a) the new method;
     - (b) the method's own deny row, which renders `horizon = result`, i.e. today's cadence;
     - (c) the public deny of the handoff rows.

     Comparator (1) reads (a) against (b). Comparator (2) reads (a) against (c), cold included.
   - **BASELINE and TRIGGER (CONTRACT-8).** pcrec's owed post-K38-2 re-measure of §2.41¶8c. The method commit
     proceeds only if it reproduces a dense loss above noise on the unbounded row (D77).
2. **INDEPENDENT CONTROL.** Relevant.
   - **(i) VALUE.** G2's horizon property reference: f is an occurrence, and c <= f < n. It enumerates occurrences
     with the scalar byte loop (no kit row text) over a GENERATED space: run lengths 2..8, byte sets of 1..4 bytes,
     spacings 1..2B, lo at and around occurrences and block edges, n near the window end. The author is D27-blinded
     (r49 group D).
   - **(ii) GATE (CONTRACT-7).** Three fail-closed cases:
     - a site stating MF_GAP_UNBOUNDED declines every non-serving row and selects a serving one;
     - a stated `horizon` on a gap-0 site is refused at mf_use;
     - a stated `horizon` through a non-serving row is refused.

     These are the seam commit's real control. The value reference is vacuous there, because every row renders
     `horizon = result` (MEAS-7).
   - **(iii) COUNT (MEAS-7).** A deterministic count of pcrec-visible asks, kit FIND calls and bytes read per search
     call, from an instrumented build or the measurement lens's python model, over the constructed layouts above. It
     is gated on the structural bounds claimed in B4 (waste <= covered distance, <= 3 reads per byte, the O(log B)
     ramp). Counts do not depend on box noise; the f = c reply passes (i) but fails (iii).
   - **(iv) POPULATION.** pcrec's artifact diff for G1, plus the suggested step-budget sweep over the handoff corpus.
     The identity claim predicts equal results at every budget. Never the kit's `moved`.
   - **SABOTAGE ([MECH-REACH], MEAS-7):** a horizon one past an occurrence, f < c, and a horizon past a non-occurrence.
     These land WITH THE METHOD ROW, not at the seam commit, because no row computes f before it. The finite-gap
     sabotage ("gap of G + 1 accepted", SOUND-1) belongs to a finite-G revisit. It needs a STEP-BUDGET arm to be
     observable as an answer, and B3.2's witness is that arm.
3. **WHAT MOVES ON REGENERATION.** B is a page size, not measured data. If a build-time constant per target is
   chosen, it lives in the kit's target facts, and moving it moves bytes: a pcrec abi event (integration.md §21.3).
   The card's own data moves nothing emitted.

### B6. Comparators and the owner's allowances

- **(1) No subject slower than today's rows.** By B3.1 the attempt work is identical, so a loss can come only from
  the kit's extra reading (the sparse failed window, the early-match tail) and, in the composed arm, from per-occurrence
  FIND calls that cost more than today's per-occurrence ask. All of these are bounded by the call's own progress
  (B4). Whether they stay inside "a few percent on rare forms" is the card's question, read as arm (a) against (b).

  A residual loss has a lever: the method's deny row gives `horizon = result`, today's text. The bounded rows are
  unchanged, so comparator (1) holds there by construction.
- **(2) Not slower than the rows denied, cold included, for the demotion (MEAS-2).** Today's dense loss against the
  deny is the per-occurrence ask.
  - On the unbounded row the form removes pcrec-visible asks. In the composed arm it does NOT remove the kit's
    per-occurrence FIND calls, so the card's dense cells CAN fail comparator (2) by arithmetic. If they do, the
    one-pass arm is the fix.
  - A subject where each ask is soon followed by a match still pays asks the denied loop never makes. Those cells
    are in the card.
  - The bounded row's comparator (2) loss (1.56 against 0.71 ms, pre-K38-2) is NOT addressed by this unit (B3.2, Q11).

---------------------------------------------------------------------------------------------------------------

## (c) Open questions, each with a recommendation

- **Q1 (field placement).** The define must pick a form that serves the horizon before any use asks it: mf_use
  re-checks and refuses, it never re-selects (memfn.h:1555-1569, :1567-1569). So the gap is a DEFINE-phase site fact
  and the lvalue is a USE hook. Two alternatives fail:
  - a new `mf_use_kind`: an MF_VOCAB move, and `use` is not gated by serves (F2), so it would not fail closed;
  - a second define of PRE: a pcrec mover and an H-SITES row.

  RECOMMEND the site fact plus the use hook, with the CM(ZERO) declarations of CONTRACT-1. The edit sites are kit.h
  `MF_SERVES_WINDOW_ONLY`, window.c `WF_SERVES_FRAME`/`WF_SERVES_REST`, and finder.c `FD_SERVES_COMMON`. Add a
  class row for MF_GAP_UNBOUNDED, or widen CL_UNBOUNDED's doc, which today says "span_hi == MF_SPAN_UNBOUNDED"; the
  class space has room.
- **Q2 (who states the gap).** pcrec states it, as a fact of its loop (D157). Today the domain is {0,
  MF_GAP_UNBOUNDED}, and a finite G is refused. RECOMMEND recording B3.2 (G = K + 1, tight, the agreement rule) in the
  kit's design note for a revisit, with no code (CONTRACT-9).
- **Q3 (the window's inputs; CONTRACT-6).** The method reads `start`, which PRE already states (F3) but no row reads
  (F8). `start` is the matcher local `search_from`, so a file-scope out-of-line function cannot read it.
  - The method commit therefore changes the re-entry call text. Either the call gains the origin (and the `horizon`
    lvalue's address) as arguments, or the re-entry calls a second function. The spelling is the kit's.
  - This is a byte move inside the method's abi event, never at the seam commit.
  - The row pastes the define's `start` text at the USE. That binding holds for PRE at both uses (R-19's assertion,
    emit_dfa.c:1657-1658; fields.def:386-390, "at its mf_locals, which binds it").

  RECOMMEND no new pcrec fact; the design note states the binding.
- **Q4 (B's home and spelling).** RECOMMEND: measure 4/16/64 KiB.
  - If insensitive: a build-time page constant per CPU target in the kit's target FACTS (targets.def), with no libc
    call.
  - If sensitive, which B4 PREDICTS for the silent-window cell (MEAS-6): `sysconf(_SC_PAGESIZE)` read once per search
    call, listed in `<PREFIX>_MEMFN_LIBC`. Comparator (1) is then per-platform.

  Never the /sys readahead window or glibc cache sizes (the owner's exclusions). A stream chunk replaces B only if
  subject streaming is ever scheduled.
- **Q5 (PRE's budget column; arch note S6).** PRE is DELEG_SCAN while asked inside the attempt loop. RECOMMEND
  keeping DELEG_SCAN. The look-ahead lives in the out-of-line function at file scope, and the in-loop text stays one
  call (with Q3's extra argument or the second function) plus one compare. The card reports .text so pcrec can rule
  otherwise.
- **Q6 (A-PLAN's ride-along trigger, r49 group F).** The site, its op and its DELEG row do not change; only the kit's
  form inside the site changes, for a site stating a horizon. RECOMMEND: the trigger does not fire. The manager rules.
- **Q7 (the entry's use).** The horizon is additive, so the entry could ask it too. RECOMMEND not now (no measured
  need, D77); the field already permits it later with no contract change.
- **Q8 (the hook is C text).** `horizon` is an lvalue name, like `result`, so this seam keeps carrying C text
  (manifesto principle 9). RECOMMEND accepting that; converting the reply to a value protocol is A-PLAN's job.
- **Q9 (when to land; CONTRACT-8).** RECOMMEND two commits:
  - The seam event lands as U1-k's first commit (zero movers) under pcrec's build go.
  - The method commit follows ONLY if pcrec's post-K38-2 re-measure reproduces the dense loss above noise. It is one
    abi event with pcrec's consumer text and carries: its deny row `--memfn=no-<name>` with its docs/spec hunk (D80:
    tuning.md §2.41 and the memfn deny listing), its card, the gate and value sabotages, the count control, and D144
    alpha at both layers.
- **Q10 (critic round).** DONE: review 2026-11-20 memfn-r46 (light, three lenses), applied in this revision.
  RECOMMEND the review file's lessons go to the critic guide, as the coordinator proposed.
- **Q11 (the bounded row, revisit; NEW).** Main's reading of bounded-horizon-scope leaves the bounded row's measured
  loss unaddressed. The two kit forms that would serve it are a finite-gap horizon (B3.2) and a BATCH reply (the next
  m occurrences, covering spacing in (K + 1, B)). RECOMMEND neither now. Two things would trigger it:
  - the dense-not-target discussion closing with "within K + 1" counted as dense;
  - pcrec's re-measure showing the bounded row's per-occurrence ask above noise against the deny.

## Facts vs inferences, at a glance

FACTS: B1 (F1-F13) and the emitted witnesses. INFERENCES: B2 (confirmed by the soundness lens's model), B3.1
(identity; held by that model; pcrec confirms), B3.2 (the general form, held including tightness), B4 (method costs,
waste bound re-derived for the new rule, cold argument), and the comparator readings in B6.
NOT MEASURED: everything in B4 and B6; the card and the count control are the measurement.
