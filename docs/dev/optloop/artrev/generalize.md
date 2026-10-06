# [ARTREV] S5: the generalizer (pilot)

Lane `artgen`, 2026-10-06, opus, not blind (charter §3, §4 S5; D150). Inputs: the four pilot reviews at
pin `57db5152` (abi 62): `A01/`, `A07a/`, `A07b/`, `A09/`, `pilot_index.md`, the notebook entries,
and `docs/dev/lanes/artcollect_report.md` (hardened identity and repair counts). The emitter read is
`lane/artgen` at `6a0b7953`. Its `src/` is identical to the pin, and all three pilot artifacts
regenerate sha256-identical. START-SET stage 3 is read at `lane/ssbuild3` tip `c9154808` (built in
scratch, abi 64).

**The Linux confirmer (S4) had not run when this was written.** Every table below has a `confirmed`
column that is left EMPTY. The join rule is in §1.4. Nothing here is a measured gain. "Expected
effect" is the reviewer's own scratch or work-count estimate, as `pilot_index.md` records it.

## 0. Findings first

1. **The pilot's 25 counted leads are 15 distinct ideas** (§2, I1-I15). The A07 pair contributes 7
   ideas, with both reviewers' ids kept. Of the 15:
   - **4 are KNOWN with a shipped or in-flight home**: I2, I8, I11, and partly I13.
   - **5 generalise a known mechanism**: I1, I3, I5, I6, I12.
   - **4 are NEW**: I7, I14, I15, and I4 as a mechanism candidate for K88.
   - **2 are codegen-micro** (D119: recorded, flagged, not for the loop): I9, I10.
2. **Two leads the reviewers measured as the biggest are partly ALREADY SHIPPED behind a missing
   analysis.**
   - Compiling A07's pattern in possessive spelling, `\b(\w++)\b\s++\1\b`, at the pin gives
     `RX_VM_FRAMELESS 1`, `RX_VM_ENTRY_SHAPE "inline"`, `rx_fail: return -1` and zero `RX_PUSH`.
     That is A07b's L2 (scratch -45%) plus the inline half of L4 (scratch -72% cumulative).
   - So the emitter-side change is the POSSESSIFY ANALYSIS (I6: two declining arms in
     `src/opt/possessify.c`), not new codegen. The [CC-DIFF] entry shapes then follow by themselves
     (I8).
   - The residual codegen the shipped frameless form still lacks is the trailed `RX_SET` (I7) and
     the word-start filter (I5).
3. **I6's population is tiny**: 1 bench pattern (A07's own `doubled-word`) and 2 corpus patterns,
   counted with the possessified spelling's frames actually dropping.
   - It is the highest-ratio lead on its own cell and the lowest-population lead in the pilot.
   - K35 says to file it with that population, not with A07's -45%.
   - Parser coverage caveat: 56% on bench, 37% on corpus. The 19 unparsed framed bench VM patterns
     were hand-checked and none has the shape.
4. **The CTX group is the pilot's real population story.** One bench family carries I11 (start
   component), I13 (mid-run stay set), I14 (count-collapsed hybrid with no captures) and I15
   (framed lazy step): `level-context` and the four `ctx-*`.
   - That family is the gap report's rank-2 group: level-context ×3.8 (gapreport_2026-10-05).
   - I11 IS START-SET stage 3. It is verified on the ssbuild3 compiler: A09's prefilter becomes
     `first-class-bounded` with the conditional re-seed, which is A09's L2 shape.
   - So a CTX round after stage 3 lands would read I13 + I14 + I15 on those five cells.
5. **I2 needs no emitter change.**
   - A01 L2's `'t'` pick is what the shipped emitter emits when given a findings bundle analyzed
     from the cell's own subjects: `pcrec-analyze --scan freq` over the three 1 MiB loglines
     subjects gives `RX_REQ_RUN "617420@1"` and `RX_REQ_BYTE "116"`.
   - The shipped `log`/`weblog` bundles still pick `'a'`, as does the prior.
   - Across the population, the pick moves under a shipped bundle on 33 of 109 bench run-bearing
     artifacts and 112 of 559 corpus ones.
   - The lead is a statement about exemplar data ([FINDINGS], D83), not about the emitter.
6. **I1 is [ENG-TACTICS] (b), "reverse-inner", on the DFA route**, and has a real population.
   - 17 bench DFA artifacts have an inner necessary byte at least 2× rarer by the prior than what
     the scan keys on today (8 at ≥8×, `stack-frame` among them).
   - On 12 of the 17 the emitter ALREADY knows the byte: K82's `set-leads` presence `memchr`. It
     uses the byte only to say no, never as the scan anchor.
7. **Give-up surface.** Leads whose twins repair (artcollect §3) are tagged `changes-giveup-surface`:
   - I6: A07 L2, 5,380 repairs.
   - I7: the L3 stacks, 294,884 repairs.
   - I14's superseded r2: 5,562 repairs. The sealed r3 is exact, and is the shape to build.

   Each tagged lead moves a give-up in ONE direction only: a give-up becomes a correct answer. That
   matches the existing precedents in tuning.md §2.20 (alt-island) and §2.35 (hyb-reseed), and each
   needs that precedent's spec sentence and a K65-style check (§2, item 5 of each idea).

## 1. Method

### 1.1 The census (K35): `gen/census.py`, output `gen/summary.txt` + `gen/rows.tsv.gz`

- **Populations.** The bench is every `pcrec-bench/bench/*/patterns/*.rx`, read-only at `eb634d9d`
  (345 patterns, 321 compile), compiled as the `pcrec-auto` testee does: `--features all`, plus
  `-e utf8` on set `utf8`.
- The corpus is every `pattern`/`pattern-esc` block of `tests/**/*.rxt` (`pcrec --list-source`),
  with the block's encoding and `i` flag, `--features all`. It is deduplicated on
  (pattern, encoding, icase): 3,704 distinct, 3,333 compile; the 371 refusals are module-gated or
  budget refusals.
- **Instruments.** One `--emit-facts` call (facts + the artifact's own decision stamps) and one
  `-o -` compile per pattern. The per-idea readers are as follows.
  - **K1** reads the byte-rate prior (`tests/findings/default_ppm.tsv`, the normalized default
    bundle).
  - **K2** recompiles under `--analysis log|weblog`.
  - **K6** recompiles the hand-possessified spelling and counts `RX_PUSH`.
  - **K11** recompiles with the stage-3 compiler and reads `RX_DFA_PREFILTER`.
  - **K13** reads the forward premultiplied transition table off the emitted C. This is
    `A09/tools/dfa_dump.py`'s reading, generalised to "1-local stay sets"; see `stay_sets()`'s
    docstring for the two wrong first versions.
  - K6, K12 and K15 use a small pattern reader that declines (and counts) anything outside its
    grammar: it parsed 1,512 of 3,333 corpus and 212 of 321 bench patterns.
- **Controls.** `census.py --selftest` runs a positive and a negative control per classifier (31
  controls). The transcript is `gen/selftest.txt`: **31/31 pass**.
  - The first run failed 5. Four were wrong control choices or a misread stamp: `RX_REQ_RUN`'s `@N`
    is the scan member's INDEX, not the run's offset, so K3 now reads the `req_run_maxoff` fact.
  - The fifth was a wrong K13 instrument: an SCC reader that cannot see A09's {406,435} set because
    keyword-prefix states return into it.
- **What a count is not.** A count is the shape's PRESENCE, not its share of any cell's time. A
  necessary-condition classifier (K3, K11, K12) is an upper bound and is labelled as one.

### 1.2 The emitter read

- Each idea's site is cited as `file:line` at `6a0b7953`.
- The claim "the shipped emitter already does X" was checked by compiling a variant spelling with
  the pin compiler and reading the emitted text. It was never inferred from source alone.

### 1.3 Known vs new

Each idea was matched against `plan.md` (the D137 candidate list and the [OPTLOOP] tree),
`plan_completed.md`, `known_issues.md` and `docs/design/` (startset.md, eng_brep_design via
`possessify.c`'s header, hyb_reseed.md, litscan_*). The row cited is the nearest one. "Generalises"
means the same mechanism with a wider precondition.

### 1.4 How the confirmer's verdicts join

`confirmed` is keyed by idea. Fill it with every `artifact:lead=VERDICT` the S4 tables report for the
leads listed in that idea's `artifacts` cell, for example `A07b:L2=WIN, A07a:L2=WIN`. A stacked twin
(A07b L3-L6, A09 L6) is reported against the idea that ADDS it: L3 goes under I7 and L6 under I9.
The stack's base ideas are named in the same cell. An idea with no timed lead, such as I2, stays
`n/a`.

## 2. The ideas

Each idea answers, in order: 1. emitter site; 2. population; 3. known vs new; 4. interactions;
5. give-up surface; 6. cost and class.

### I1. Inner rare-byte anchor ("reverse-inner" on the DFA route): A01 L1 (rvA01)

1. **Site.** The search shape is `emit_unanchored` (`src/gen/emit_dfa.c:8565`). Today it runs the
   pre-check, then a forward scan from the handoff, then the reverse pass.
   - The pre-check is `pcrec_emit_req_byte_check` (`emit_dfa.c:1362`). Its K82 `set-leads` arm
     (`:1386`) already emits a presence `memchr` of a necessary byte rarer than the run's scan
     member: A01's `memchr(')')`.
   - The candidate row table is `dfa_pfs[]` (`:6658`).
   - To emit the twin's shape the emitter must know three things:
     - (a) a necessary byte `r` whose occurrences bound match starts;
     - (b) a reverse machine over the PATTERN PREFIX before `r` (A01's back-walk over
       `[A-Za-z0-9_$.]` plus `"at "` is that machine, hand-collapsed; in general a reverse DFA of
       `P` where the pattern is `P·r·S`);
     - (c) the uniqueness argument: the first `r` after a start is the one the match uses. A01's
       `(` is outside the run class. In general this needs leftmost-start selection across
       several `r` occurrences, which is rust's reverse-inner quadratic guard.
2. **Population** (K1: DFA engine, unanchored, the prior's rarest necessary byte not in the start set
   and ≥2× rarer than today's scan key; the 2× is an UNMEASURED DEFAULT):
   - bench 17 (8 at ≥8×), among them `stack-frame`, `uuid`, `iso-ts`, `ipv6`, `orig` and
     `waf-942160-sleep-benchmark`; 12 of the 17 are already presence-checked;
   - corpus 90 (31 at ≥8×), 50 presence-checked.
   - Hybrids are not counted (their DFA is the prefilter).
3. **Known vs new: GENERALISES [ENG-TACTICS] tactic (b)** (REVERSE-DFA START, "APPROACH.md:1032's
   lead"). That row frames it VM-side, from K66's witness, and boonies-tiers it.
   - The DFA route is the cheaper host: its reverse machine already exists, and only a
     prefix-restricted copy is new.
   - Relation to [OPT-FREQPICK]/[OPT-REQPOS] (closed): they pick WHICH necessary byte or run the
     pre-check scans. They never move the SCAN ANCHOR off the prefix. Not the same mechanism.
4. **Interactions.**
   - Stage 3 does not move A01. The ss3 compile is byte-identical apart from the abi stamp: A01
     sits on `offset-set-bounded`, above the new first-* rows.
   - startset.md finding 4 already re-buckets `stack-frame` out of START-SET ("per-candidate cost,
     another group"). I1 is that other group.
   - This is a scan site, so it is a [MEMFN] request (D146/D147).
5. **Give-up surface.** None: a DFA route, and 0 repairs.
6. **Cost.** M-L, risk M-H. It needs a new candidate row, a prefix reverse machine, the
   leftmost-start argument, a deny flag and an abi event. Class: ALGORITHMIC.
   - Reviewer's expected effect: the largest of A01 (`memchr` calls 33,377 → 3,820 per MiB on the
     fail subjects, which set the cell's median).

### I2. Pick the run's scan member by the subject's byte rate: A01 L2 (rvA01); A09 L1's O/T byte choice (rvA09, notebook transfer)

1. **Site.** No emitter change. The pick is `pcrec_find_run_scan_index` (`src/core/findings.c:522`)
   through `pcrec_req_window` (`src/facts/req.c:644`).
   - Measured: with a bundle analyzed from the cell's own three 1 MiB loglines subjects
     (`build/pcrec-analyze --name ll --retrieved … --scan freq`, then `-I . --analysis ll`), A01
     emits `RX_REQ_RUN "617420@1"` and `RX_REQ_BYTE "116"`, which is exactly the twin's `memchr('t')`.
   - Under the built-in prior, and under the shipped `log` and `weblog` bundles, it stays `'a'`.
   - A09's per-alternative O/T choice has no single-byte home (see I12).
2. **Population** (K2: run-bearing artifacts): bench 109, corpus 559. The pick moves under at least
   one shipped bundle on bench 33 and corpus 112. This is sensitivity to data, not a defect count.
3. **Known.** [OPT-FREQPICK] (closed, default-on 2026-09-25) plus [FINDINGS] (D83: "the REAL prior
   is a findings file measured off the deployment's own exemplar"). Same mechanism, already shipped.
4. **Interactions.** None in flight. Note D83's control rule: a bundle fitted to the bench's own
   subjects is the "control that shares a source" `src/findings/default.rxt` refuses on purpose.
   This lead must never become a default-prior change.
5. **Give-up surface.** None (0 repairs). Pick moves on no-DFA-front VM routes were K65's hazard,
   which is fixed there.
6. **Cost.** 0 emitter work. Class: data. Reviewer: -17% `memchr` on fail, superseded by I1.

### I3. Start from a forward marker instead of the reverse pass: A01 L3 (rvA01), A09 L4 r1 (rvA09)

1. **Site.** Axis J, `dfa_search_starts[]` (`emit_dfa.c:7659`). Its rows are `pinned` and
   `reverse-pass`. The reverse pass itself is emitted by `emit_unanchored` (`:8565`, the
   `rewind_position` walk around `:7342-7355`).
   - A third row, call it "marker", would record the position at which the forward machine finishes
     a leading literal run and take it as the start.
   - The emitter would have to know that the run occurs exactly once per match, at its start (A01:
     no space inside the run class; A09 r1: the after-level region is entered only from state 319).
   - That is a uniqueness fact over the pattern's language. No pass computes it today.
2. **Population** (K3, a NECESSARY condition: `RX_DFA_START "reverse-pass"` and a necessary run
   starting every match, i.e. the `req_run_maxoff` fact is 0): bench 71 of 285 reverse-pass
   artifacts (59 DFA, 12 hybrid); corpus 389 of 2,783. The uniqueness half is NOT counted, so these
   are upper bounds.
3. **Known vs new: GENERALISES axis J's `pinned` row** ([OPT-5] STEP 2, which proves the reverse
   pass's answer is `startpos`). I3 proves it is "the last marker". It also overlaps
   [CAPTURES-DFA-MB]/`captures_via_dfa_survey.md` candidate (c) in miniature: a one-tag TDFA for
   slot 0 only. NEW as a row.
4. **Interactions.** Stage 3 does not touch axis J. Under I1 the reverse pass leaves A01 anyway
   (rvA01: "subsumed by L1"). On hybrids, I3 is the first half of I14.
5. **Give-up surface.** None (0 repairs; the DFA route has no budgets).
6. **Cost.** M, risk M: the uniqueness analysis is the risk. Class: ALGORITHMIC, but HIT-path only.
   - rvA01: ~10-15% of the hit subjects, cell median unmoved.
   - rvA09: 12.4k reverse steps per MiB on hit go to 0.

### I4. The first loop iteration re-runs the skip at the handoff: A01 L4 (rvA01)

1. **Site.** `pf_open` (`emit_dfa.c:5809`) emits the state-0 skip test. The offset-set skip bodies
   are `pf_emit_ofs`/`pf_emit_ofs_bounded` (`:6501`, `:6521`). The handoff is
   `emit_req_run_check`'s `handoff_position` (`:1124-1143`).
   - The twin adds `scan_position != handoff_position` to the first test. The emitter already knows
     the handoff is a verified candidate: the K82 handoff exists precisely because it is.
2. **Population** (K4: `RX_REQ_HANDOFF` set and an `<p>_ofsskip` call): bench 36 (of 49 with a
   handoff), among them `stack-frame`, `lit-l31`, `lit-l40`, `github-pat` and `slack-webhook-url`;
   corpus 114 (of 183).
3. **NEW as a mechanism, KNOWN as a symptom.**
   - K88 / [K88-HANDOFF-DENSE] says "the handoff costs ~4.6 ns per search call on a back-to-back-
     match literal where it cannot skip … the mechanism is not measured … re-measure with a
     `cnt_pre.h`-style twin before designing anything", and its second witness is `lit-l31`.
   - A01 L4 IS such a twin: one redundant `memchr` + test per call, counted at 659 per MiB on hit.
   - Recommend it as K88's first candidate mechanism, not as a new row.
4. **Interactions.** This is a scan site (MEMFN). It is unaffected by stage 3.
5. **Give-up surface.** None.
6. **Cost.** XS, risk L: one conjunct, plus an abi event. Class: CODEGEN-MICRO per call (flagged),
   but it is the measurement K88 asked for.
   - rvA01: NOISE on this cell (~2% of hit `memchr`s). It weighs more in the short-call regime,
     which is K88's own regime.

### I5. Fold a leading context assertion into the VM start scan, and restart past a failed attempt's dead span: A07a L1 + L4's resume (rvA07a), A07b L1 + L5 (rvA07b)

1. **Site.**
   - The VM hat's row is `vm_start_row` (`emit_dfa.c:6697`); its seek is `pcrec_emit_vm_start_seek`
     (`:6727`), called from `vm_emit_search_body` (`emit_vm.c:12552`, the attempt loop at
     `:13440-13530`).
   - The set comes from the `start_set` fact (`src/facts/startset.c`), which by design treats a
     zero-width node as ∅ (startset.md §3.2). That is exactly where `\b` drops out, leaving S = `\w`.
   - To emit the twin, the emitter must keep the leading context as a PREDICATE ON THE PREVIOUS BYTE
     (not in `\w`), not merely the first-byte set. This is the VM analogue of the DFA hat's re-seed.
   - The post-failure restart (A07b L5) additionally needs the matcher to report the furthest
     proven-dead position. In A07 that is subsumed by the predicate (positions inside a word fail
     it).
2. **Population** (K5: VM route with no prefilter whose attempt's first label reads
   `subject[scan_position-1]`): bench 2 (`doubled-word`, `dup-param-detect`); corpus 1. Both bench
   rows already take `first-class` (stage 2).
3. **GENERALISES [START-SET] stage 2** (the VM hat, `first-class`). startset.md lists the six
   `\b(\w+)…\1` bench shapes as VM-hat movers at "63, 77%: dense, guard cells". This lead is why
   they stay dense: the hat scans S and ignores the context.
4. **Interactions.**
   - The same table (`dfa_pfs[]`, VM-route rows) that stage 3 edits. Sequence it after stage 3
     lands, as its own row.
   - startset.md §8 stage 5 ("offset-k sets from the AST") is the nearest filed neighbour. A
     context predicate is a different extension.
5. **Give-up surface.** None: A07a L1 and A07b L1 have 0 repairs. The skipped attempts fail at the
   first instruction, before any budget charge. The L5 restart was measured only stacked on
   frameless twins and inherits their repairs.
6. **Cost.** S-M, risk L-M: a predicate column on the VM route rows plus the seek's extra test. abi
   event. Class: ALGORITHMIC.
   - A07b run 001 measured L1 at -19..-21% (scratch).
   - rvA07a counts attempt calls falling from 809,635 to 184,595 per MiB.

### I6. Possessify through a `\b` follow and through a backreference follow: A07a L2 (rvA07a), A07b L2 (rvA07b)

1. **Site.** `src/opt/possessify.c`.
   - `first_of`'s `A_BREF` arm (`:213`) widens a backreference to all 256 bytes, nullable.
   - Its `A_CTX` arm (`:377`) widens `\b` to all bytes and declines.
   - The verdict is `pss_verdict`/`pss_rep` (`:823`, `:857`). The emitter consumer is
     `vm_cursor_rep` (`emit_vm.c:4672`): the greedy give-back `RX_PUSH` at `:4968` and the retreat
     at `:5009`.
   - Two arms would close it.
     - **(B)** A greedy single-class repeat with m ≥ 1 whose class is ⊆ `\w` or ⊆ `\W`, followed by
       `\b`. Every retreat position has the class on both sides, so `\b` is false there. `\B` and
       m = 0 stay declined: the census's negative controls confirm the reader declines them.
     - **(R)** A backreference to a group that is closed on every path to it and non-nullable. Its
       FIRST is that group's FIRST (folded under `(?i)`), and an unset group fails.
   - Measured: the emitter then does the rest. `\b(\w++)\b\s++\1\b` compiles frameless with the
     `inline` entry shape (I8).
2. **Population** (K6: VM route, pattern reader finds an arm; the possessified spelling's
   `RX_PUSH` count drops):
   - bench 1 (`doubled-word` = A07, both arms, 2 → 0 frames, becomes frameless);
   - corpus 2 (`wordb_vm.rxt:339` arm B, `startset/vmhat.rxt:381` arm R, both becoming frameless);
   - 7 more DFA-route rows carry an arm, where frames are moot.
   - Coverage caveat as §0 item 3.
3. **GENERALISES [ENG-BREP] rung 1** (possessify, eng_brep_design.md §2). Both arms are exactly the
   cases the file's header documents as WIDEN-AND-DECLINE.
   - `\b`: "closed in NEITHER direction" is true in general but false for word-pure bodies with
     m ≥ 1.
   - Backreference: "not a compile-time fact".
   - **Soundness history warning.** The header records three earlier "obvious" rules refuted by
     measurement (U1, U2, the lazy conjunct). Each new arm needs `tests/possessify/run_possdiff.sh`
     extended and a D6 panel before it is built.
4. **Interactions.** It moves possessify's `ENGINE_WHY`-independent stamps (`RX_VM_STRATS`, frame
   capacities). It is untouched by stage 3.
5. **Give-up surface: `changes-giveup-surface`.** A07a L2 and A07b L2 each have 5,380 repairs. The
   original gives up (frames 0/1, shrunk step budget) and the twin answers; every repair equals
   libpcre2.
   - What moves for a caller: FRAMES/STEPS give-ups on the affected artifacts can only disappear.
   - The frameless form charges WORK per span (counter-K) instead of STEPS per pop, so which budget
     binds changes too. `<PREFIX>_RESUME_FRAMES` and `_FAST_FRAMES` shrink, and FRAMES escalation
     (match_api.md §10.9, limits.md §3.2) is never triggered.
   - Spec hunk: tuning.md §2.1 (`-fno-possessify`) gains the one-way give-up sentence in §2.20's
     form, and limits.md §7 gains a bullet beside the `--unroll=K` one.
   - Check: a K65-style `.rxt` with cells that give up under `-fno-possessify` and shrunk budgets
     and must answer the libpcre2 answer with the arm on, plus the reverse direction asserted
     absent.
6. **Cost.** S (two arms), risk M (soundness, see 3). Class: ALGORITHMIC.
   - A07b run 001: -45% alone (scratch). rvA07a: medium, ~0.89 pops per subject byte removed.

### I7. Slot writes no backtrack can observe need no trail: A07a L3 (rvA07a), A07b L3 (rvA07b)

1. **Site.** The macros come from `vm_emit_storage` (`emit_vm.c:11737`, `RX_TRAIL`/`RX_SET` text at
   `:12108`). Each write goes through `vm_set` (`:3464`), and the per-attempt unwind is
   `<p>_reset_for_next_attempt` (`:12651`, called at `:13515`).
   - The twin's plain store needs a per-slot fact: on every path, every READ of the slot (a
     backreference, or `rx_report_captures` on accept) is dominated by a WRITE in the same attempt,
     and no resume frame is live across the write.
   - On a frameless program the second half is trivially true. Then the trail only restores slots
     for the NEXT attempt, which the dominance half makes unnecessary.
   - tuning.md §2.21 states the opposite design premise: "the trail is real storage even on a
     frameless artifact ((abc)(def) pushes nothing and saves two capture slots)". That is true
     today and is what I7 would change.
2. **Population** (K7: VM matcher with `RX_SET`): bench 66 (27 frameless, 39 framed); corpus 1,454
   (623 frameless, 831 framed). The frameless half is the population where only the dominance fact
   is needed. The dominance fact itself is not counted, so this is an upper bound.
3. **NEW.** No row or design note proposes trail elision. The nearest is the [CC-DIFF] forward rung
   (tuning.md §2.21), which needs "no `RX_SET`" for a NULL descriptor. I7 would widen that rung's
   reach as a side effect.
4. **Interactions.** It compounds with I6, which makes A07 frameless. It is untouched by stage 3.
5. **Give-up surface: `changes-giveup-surface`.** The A07a/b L3-L6 stacks show 294,884 repairs,
   which is every original give-up in the shrunk run. I7 alone removes the trail's FRAMES give-up
   (trail capacity 0 or 1).
   - Spec hunk: limits.md §3.2 (trail capacity is reached by fewer artifacts), the
     `<PREFIX>_TRAIL_FRAMES` sizing text (§5), and the one-way sentence.
   - Check: K65-style trail-capacity-0 cells.
6. **Cost.** M (a dataflow fact, two `RX_SET` spellings), risk M. Class: ALGORITHMIC (an
   analysis-driven elision, not a micro-tweak).
   - A07b run 001: -53% for L2+L3 together, about 8 points over L2 (scratch).

### I8. Inline the now-straight-line matcher, `rx_fail` = `return -1`: A07b L4 (rvA07b), A07a L4 fusion (rvA07a)

1. **Site.** ALREADY EMITTED for frameless programs. The [CC-DIFF] entry-shape ladder is
   `<PREFIX>_VM_ENTRY_SHAPE`, stamped around `emit_vm.c:11432-11534`; the frameless `rx_fail`
   return is in the same file.
   - Verified on the possessified A07 spelling: `inline`, `always_inline` on all statics,
     `rx_fail: return -1;`.
   - The emitter needs nothing new. It needs I6 to make the program frameless.
2. **Population** (K8, context only): frameless VM bench 30 (`inline` 24, `forward` 3, `plain` 44
   of all VM); corpus 660.
3. **KNOWN**: [CC-DIFF] STEP 1/2 (tuning.md §2.21). It is MOOT as a lead: it is I6's consequence.
4. **Interactions.** None.
5. **Give-up surface.** It inherits I6/I7's. It adds none of its own.
6. **Cost.** 0. A07a L4's fusion (the search loop walks words itself) is I5 + I8.

### I9. 256-byte class tables instead of 32-byte bitmaps: A07a L5 (rvA07a), A07b L6 (rvA07b)

1. **Site.** `vm_cls_test` / `vm_cls_read` (`emit_vm.c:1656`, `:1615`), and the bitmap emission
   (`:12692`). A07 also carries `rx_start_set[256]` from the VM hat beside `rx_class_bitmap0`, which
   is the same set twice ([OPT-D]).
2. **Population** (K9: VM matcher with bitmap tests): bench 44 (185 test sites); corpus 67 (646).
3. **KNOWN**: [OPT-A]'s "byte-test spelling menu (`[a-zA-Z]`, `\w`, hex all pay the 256-bit bitmap)",
   [CLS-TREE]/[OPT-CLSPACK], and [FORM-CHAR]. `form_char_step0.md` recommends AGAINST the 256-byte
   table form "everywhere measured", on size; its speed half stays open. Same mechanism.
4. **Interactions.** [CLS-TREE] S-stages own class emission. The kit (`clskit.c`) is the host.
5. **Give-up surface.** None of its own. Its twins were measured only stacked on I6/I7.
6. **Cost.** XS-S. Class: **CODEGEN-MICRO (flagged; D119: recorded, not a loop lead).** Reviewers:
   small, "perhaps noise". Never timed.

### I10. Run counters in locals for the attempt: A07a L6 (rvA07a)

1. **Site.** The `run->` counter traffic comes from the macros at `emit_vm.c:12108-12160` and the
   fail label. The twin copies `resume_depth`, `trail_depth`, `steps_left`, `work_left` and the
   stack pointers into locals, with an `RX_RET` write-back on every return.
2. **Population** (K10: framed VM matcher): bench 41; corpus 837.
3. **KNOWN** territory: [OPT-B] ("PROFILED code-level optimization … branch behaviour and memory
   layout"). No row names this transform. rvA09 rejected it for A09 (the VM is ~2% of the work).
4. **Interactions.** None.
5. **Give-up surface.** None: 0 repairs, same operations in the same order.
6. **Cost.** S-M. Class: **CODEGEN-MICRO / compiler-hint (flagged).** rvA07a: small-medium. Never
   timed.

### I11. Skip the seeded DFA's start component: A09 L2 (rvA09); the scan half of A09 L1

1. **Site.** START-SET stage 3, the DFA hat: `pf_dfa_start_set`, the `first-class-bounded` row and
   `pf_emit_moved_reseed` on `lane/ssbuild3`.
   - Verified: the ss3 compiler emits A09's prefilter as `first-class-bounded` over `rx_start_bytes`
     = {C,E,F} with `if (scan_position > skip_from) forward_state = seed[...]`. That is L2's table
     loop with the predecessor decided by the re-seed.
2. **Population** (K11: seeded unanchored forward machine): bench 30 (18 DFA, 12 hybrid); corpus 138.
   Stage 3 takes a first-* row on **bench 18**, equal to startset.md §1's DFA-hat count of 18
   (independent agreement), and on corpus 31.
3. **KNOWN**: [OPT-FIRSTSET]/[START-SET] stage 3. Same mechanism.
4. **Interactions.** MOOT once stage 3 lands. It is parked on `lane/ssbuild3`, with panel fixes
   delivered.
5. **Give-up surface.** None.
6. **Cost.** 0 new. Reviewer: ~3× on the prefilter (L2).

### I12. Per-alternative rare-byte streams for a leading literal alternation: A09 L1 (rvA09)

1. **Site.** A new candidate row in `dfa_pfs[]` (`emit_dfa.c:6658`). The existing
   `offset-set`/`<p>_ofsskip` (`:6501`) tests one offset set. L1 runs two `memchr` streams (`O` at
   ERROR+3; `T` at FATAL+2 and CRIT+3), each with its own cached next hit, verified by compares and
   the `\W` predecessor test.
   - The emitter would need, per alternative, an offset at which a chosen byte sits. The k-sets of
     `src/facts/kset.c` hold the bytes but not a per-alternative choice. It would also need a cost
     rule choosing the stream set, which is data-dependent: under the prior, the streams are not
     cheaper than {C,E,F}.
2. **Population** (K12: a leading literal alternation with no shared necessary byte): bench 21 (the
   altwide `w-*`, `nar4-*`, `s-*`, `srt-*`, `wb-*` families, `json-constant`, `level-context`);
   corpus 11.
   - Only 3 bench (`w-8`, `w-64`, `json-constant`) and 2 corpus rows are predicted cheaper by the
     shipped prior.
   - So on the realistic population the win, as on A09, is a property of the SUBJECT, and the
     selection belongs to findings data as in I2.
3. **GENERALISES [OPT-A]** ("memchr2/memchr3 for the 2-3 escape-byte gap", "Teddy/SIMD multi-pattern
   prefilter for the keyword-alternation shape", scalar half only) and startset.md §8 stage 5
   ("offset-k sets from the AST … the pair filter", filed, D77).
4. **Interactions.** It competes with I11. After stage 3, A09's scan is a 3-byte class loop and L1's
   increment over it is L1 vs L2 (rvA09: ≥10× vs ~3× on the prefilter). This is a scan site
   (MEMFN). [OPT-ALTHASH] owns the wide-alternation end (altwide).
5. **Give-up surface.** None (0 repairs; the window differential showed 0 differences).
6. **Cost.** M, risk M: stream caching across calls, verify, and a data-driven choice. Class:
   ALGORITHMIC. rvA09: ≥10× on the prefilter; on fail/syslog, DFA steps go from 1.0M per MiB to 0.

### I13. Skip a multi-state stay set in mid-run: A09 L3 (rvA09)

1. **Site.** `dir_fwd_skip` (`emit_dfa.c:7213`) emits OPT-3's in-loop STAY skip for ONE self-looping
   state. A09 already carries `rx_forward_stay14` for state 406.
   - L3 covers the two-state set {406, 435}: `[^\n]*` split by word context. It scans with the
     set's exit table, then picks the state by the predecessor.
   - The emitter would need the 1-local stay-set computation that `gen/census.py`'s `stay_sets()`
     performs: every member self-loops on a wide class, every staying class has one target, and
     exits are the classes on which any member leaves.
2. **Population** (K13: ≥2-state 1-local stay set, ≤32 exit bytes; the 32 is an UNMEASURED
   DEFAULT):
   - bench 7: `ctx-greedy-256`, `ctx-lazy-64`, `ctx-lazy-256`, `ctx-lazy-1024`, `level-context`,
     `iso-ts`, `wild-validator-uuid-grok`. That is the CTX group plus two.
   - corpus 7 (six `view_edge.rxt` blocks and `offset_skip.rxt:43`).
3. **GENERALISES [OPT-3-RUNEND] (a)**, "the skip loop generalised from state 0 to EVERY self-looping
   state", from one state to a stay set.
   - That row's own pricing warns that a run-end skip is "a net LOSS on non-periodic text unless
     predicted", at about one mispredict per run. Its D77 measurement (a non-periodic 1 MiB subject,
     now existing per bench O-82 A1) gates I13 as well.
4. **Interactions.** Untouched by stage 3 (mid-run). This is a scan site (MEMFN).
5. **Give-up surface.** None (0 repairs).
6. **Cost.** S-M, risk M (the OPT-3-RUNEND loss risk). Class: ALGORITHMIC. rvA09: hit only, ~5-15%
   of the post-L1 hit (~14k DFA steps per MiB).

### I14. A count-collapsed hybrid re-proves the DFA's window with the VM: A09 L4 r2/r3 (rvA09)

1. **Site.**
   - The hybrid attempt loop is `vm_emit_search_body` (`emit_vm.c:12552`; the entry prefilter call
     and `window_end = subject_length` "cut-bearing artifact" at `:13429`; the retry at
     `:13283-13300`).
   - The language stamp `RX_VM_PREFILTER_LANG "count-collapsed"` comes from engine selection's
     overflow retry (`src/opt/select_engine.c`).
   - To skip the VM, the emitter must know three things.
     - (a) The collapse is the ONLY inexactness. Here the count `.{0,200}?` was widened to `.*?`.
     - (b) A cheap check restores it: the gap between the level's end and the keyword's start is
       ≤ 200. r2 finds the keyword by suffix match at the window end.
     - (c) No capture beyond group 0.
   - r1 replaces the reverse pass by the marker (I3).
2. **Population** (K14): count-collapsed hybrids with `NCAPS 1`: bench 5 (`level-context` and the
   four `ctx-*`), corpus 0. All hybrids: bench 50, corpus 1,133, and nearly all corpus hybrids are
   `exact`-language lookaround/atomic/possessive patterns that the VM must still verify.
3. **NEW.**
   - [OPT-HYB-RESEED] (shipped) and [OPT-HYB-RESEED-POLICY] change WHERE the VM re-attempts, not
     whether it runs.
   - `captures_via_dfa_survey.md` candidate (c) (one-pass DFA captures) is the general "DFA answers
     without the VM", and needs no counter.
   - I14 is the counter-restoring special form for the collapsed language, as a first-match row
     (hybrid verify: `vm` | `counted-gap`).
4. **Interactions.** It is downstream of I3 (it needs the window start without the reverse pass) and
   of stage 3 (same cells). It is the CTX group's third lever.
5. **Give-up surface: `changes-giveup-surface` IF built in r2's form.** r2 had 5,562 repairs: it
   answered where the original gives up with 0 frames or trail. The sealed r3 is exact: its guard
   `trail_depth < trail_cap && resume_depth < resume_cap` (and `steps_left > 256`,
   `work_left > 2048`, DERIVED bounds) keeps the surface.
   - Build r3's form. If a future version drops the guard: a limits.md §3.2 sentence and a
     K65-style check (artcollect's shrunk-resources identity is that check's prototype).
6. **Cost.** M, risk M-H: r2 passed default-buffer identity while wrong (charter §4). Class:
   ALGORITHMIC.
   - rvA09: on hit, 193 VM attempts per MiB go to 0, about 30% of post-L1 hit.

### I15. A lazy step that needs no frame: A09 L5 (rvA09, notebook transfer from rvA07a)

1. **Site.** `vm_cursor_rep`'s lazy arm (`emit_vm.c:4672`): the push "longer run is the resume
   (extend one stride)" at `:4968`, and the extend at `:5011-5020`.
   - When the continuation after the lazy loop is capture-free and fails without leaving frames
     (A09: an alt-island keyword dispatch, `RX_VM_ALT_ISLANDS 2`), the twin points the
     continuation's failures at the extend label. It keeps the capacity check and the per-position
     step charge.
   - The emitter would need a "continuation is frameless up to accept" fact for the lazy loop's
     follow.
2. **Population** (K15: a VM-route lazy quantifier in a framed matcher): bench 5 (`ctx-lazy-64`,
   `-256`, `-1024`, `level-context`, `tag-pair-match`); corpus 54. The "frameless continuation"
   half is not counted, so these are upper bounds.
3. **NEW.** possessify's LAZY conjunct covers the opposite case (a lazy loop that may not be made
   possessive). [ENG-BREP]'s counter-K rung is the nearest "loop without frames".
4. **Interactions.** It is moot on hit under I14 (rvA09: "moot under L4 r3"); it matters for VM
   attempts that fail or whose gap does not fit. Untouched by stage 3.
5. **Give-up surface.** None: 0 repairs. The twin kept the capacity check and the step charge
   exactly, and the budget/capacity differential (6 budget pairs × 4 buffer shapes) showed 0
   differences.
6. **Cost.** S, risk M. Class: ALGORITHMIC (frame elision). rvA09: ~45 → ~25 instructions per lazy
   position.

## 3. Summary table

Population counts are bench/corpus from `gen/summary.txt`. `pos` means counted on the possessified
spelling, and "≤" marks a necessary-condition upper bound. Class: ALG = algorithmic, MICRO =
codegen-micro (flagged), DATA = no emitter change. The `confirmed` column is EMPTY until S4 (§1.4).

| idea | artifacts / leads | class | known/new + row | population bench/corpus | give-up tag | cost / risk | expected effect (reviewer) | confirmed |
|---|---|---|---|---|---|---|---|---|
| I1 inner rare anchor | A01 L1 | ALG | generalises [ENG-TACTICS] (b) to the DFA route | 17 / 90 (≥2× prior; 8 / 31 at ≥8×) | — (0) | M-L / M-H | rvA01: largest; memchr 33,377→3,820 per MiB fail | |
| I2 run member by subject rate | A01 L2; A09 L1 (byte choice) | DATA | known: [OPT-FREQPICK] + [FINDINGS] (D83) | 109 / 559 run-bearing; bundle moves 33 / 112 | — (0) | 0 / — | rvA01: -17% memchr on fail; superseded by L1 | |
| I3 forward marker start | A01 L3; A09 L4 r1 | ALG (hit) | generalises axis J `pinned` ([OPT-5] S2); new row | ≤71 / ≤389 | — (0) | M / M | rvA01: ~10-15% of hit, median unmoved; rvA09: 12.4k rev steps per MiB → 0 | |
| I4 handoff re-skip | A01 L4 | MICRO (flagged) | candidate mechanism for K88 [K88-HANDOFF-DENSE] | 36 / 114 | — (0) | XS / L | rvA01: NOISE here; short-call regime | |
| I5 VM context start filter (+restart) | A07a L1, L4 resume; A07b L1, L5 | ALG | generalises [START-SET] stage 2 (VM hat) | 2 / 1 | — (0) | S-M / L-M | A07b: -20% (run 001); rvA07a: ~3/4 of calls removed | |
| I6 possessify `\b` / backref arms | A07a L2; A07b L2 | ALG | generalises [ENG-BREP] rung 1 (possessify) | 1 / 2 (pos) | **changes-giveup-surface** (5,380) | S / M | A07b: -45% alone (run 001) | |
| I7 trail elision | A07a L3; A07b L3 | ALG | NEW | ≤66 / ≤1,454 (frameless 27 / 623) | **changes-giveup-surface** (294,884, stacked) | M / M | A07b: -53% with L2 (+8 pts) | |
| I8 inline frameless matcher | A07b L4; A07a L4 fusion | — | known, SHIPPED: [CC-DIFF] entry shapes; moot via I6 | 30 / 660 frameless today | inherits I6/I7 | 0 | A07b: -72% cumulative L1-L4 | |
| I9 byte tables | A07a L5; A07b L6 | MICRO (flagged) | known: [OPT-A] menu, [CLS-TREE], [FORM-CHAR] | 44 / 67 | none own (stack inherits) | XS-S / L | small, perhaps noise | |
| I10 counters in locals | A07a L6 | MICRO (flagged) | known territory: [OPT-B] | 41 / 837 | — (0) | S-M / L | rvA07a: small-medium | |
| I11 start-component skip | A09 L2 (+ L1's scan half) | ALG | known: [START-SET] stage 3 (lane/ssbuild3); MOOT on landing | 30 / 138 seeded; stage 3 takes 18 / 31 | — (0) | 0 new | rvA09: ~3× on prefilter | |
| I12 per-alternative rare streams | A09 L1 | ALG | generalises [OPT-A] memchr2/3 + startset §8 stage 5 | 21 / 11 (prior-cheaper 3 / 2) | — (0) | M / M | rvA09: ≥10× on prefilter | |
| I13 multi-state stay-set skip | A09 L3 | ALG | generalises [OPT-3-RUNEND] (a) | 7 / 7 | — (0) | S-M / M | rvA09: hit only, ~5-15% | |
| I14 counted-gap hybrid verify | A09 L4 r2/r3 | ALG | NEW (nearest: captures_via_dfa candidate (c)) | 5 / 0 | tagged for r2 form (5,562); r3 exact | M / M-H | rvA09: ~30% of post-L1 hit | |
| I15 frameless lazy step | A09 L5 | ALG | NEW | ≤5 / ≤54 | — (0) | S / M | rvA09: ~45→25 insns per lazy position | |

Combined twins (A07b L4/L5/L6 stacks, A09 L6) are not ideas. Their verdicts join under the idea
they add (§1.4).

## 4. DRAFT candidate plan rows (filed-not-scheduled, D137; drafts only, plan.md NOT edited)

Each line is meant to go under [OPTLOOP]'s "Candidates for the next cycle (D137)". Row ids are
proposals; naming is the manager's call.

- **[ART-POSS-ARMS]** STATE:not-started (under [OPTLOOP] candidates per D137) (FILED 2026-10-06 from
  [ARTREV] S5, generalize.md I6; D125: filed, not scheduled)
  - **What:** two declining arms of `src/opt/possessify.c` widened soundly:
    - a `\b` follow after a greedy word-pure (⊆`\w` or ⊆`\W`) single-class repeat with m ≥ 1;
    - a backreference's FIRST taken as its closed, non-nullable group's FIRST.
  - The shipped emitter then makes the matcher frameless and inline ([CC-DIFF]); verified on
    `\b(\w++)\b\s++\1\b`.
  - **EVIDENCE:** A07b scratch -45%; population 1 bench (`doubled-word`) / 2 corpus.
  - **changes-giveup-surface** (one-way; spec tuning.md §2.1 + limits.md §7; K65-style check).
  - **NEED:** the S4 verdict on A07 L2; a D6 panel (possessify's refutation history); then
    `run_possdiff.sh` extended with both arms' witnesses.
- **[ART-TRAIL-ELIDE]** STATE:not-started (same filing) — untrailed `RX_SET` where every read of the
  slot is dominated by a write in the same attempt and no frame is live across the write; first on
  frameless matchers.
  - **EVIDENCE:** A07b L2+L3 scratch -53% (+8 pts over L2); population ≤27 / ≤623 frameless with
    `RX_SET`.
  - **changes-giveup-surface** (trail FRAMES).
  - **NEED:** S4 on A07 L3; the dominance fact's own census; ranks after [ART-POSS-ARMS], which
    makes A07 frameless.
- **[ART-VMCTX-START]** STATE:not-started (same filing) — the START-SET VM hat keeps a leading
  context assertion as a previous-byte predicate (the VM analogue of the DFA hat's re-seed).
  - **EVIDENCE:** A07b L1 scratch -20%; population 2 bench (`doubled-word`, `dup-param-detect`) /
    1 corpus.
  - **NEED:** S4 on A07 L1; sequenced after START-SET stage 3 lands (same `dfa_pfs[]` table).
- **[ENG-TACTICS] addendum (no new row)** — tactic (b) REVERSE-INNER has a DFA-route instance with
  its reverse machine already built.
  - **EVIDENCE:** A01 L1 (rvA01: largest A01 lead); population 17 bench / 90 corpus with an inner
    byte ≥2× rarer (prior), 12 / 50 of them already presence-checked by K82 `set-leads`.
  - **NEED:** S4 on A01 L1; a MEMFN request for the scan site; a design note for the leftmost-start
    argument.
- **[ART-START-MARK]** STATE:not-started (same filing) — axis J row "marker": the start is where the
  forward machine finishes a leading literal run proven to occur once per match.
  - **EVIDENCE:** A01 L3 and A09 L4 r1 (hit-only); population ≤71 bench / ≤389 corpus (uniqueness
    uncounted).
  - **NEED:** a uniqueness-fact census; S4 on A01 L3. Low priority while I1 subsumes it on A01.
- **[K88-HANDOFF-DENSE] cross-note (no new row)** — candidate mechanism: the state-0 skip re-runs
  `<p>_ofsskip` at the handoff on the first iteration (A01 L4: one redundant `memchr` + test per
  call). This is the `cnt_pre.h`-style twin K88 asked for. Reach: 36 bench / 114 corpus.
- **[OPT-3-RUNEND] addendum (no new row)** — (a) generalised to 1-LOCAL STAY SETS (A09 L3:
  `[^\n]*` split by word context).
  - Population 7 bench (the CTX group + `iso-ts`, `uuid-grok`) / 7 corpus; instrument
    `artrev/gen/census.py` `stay_sets()`.
  - Same D77 gate as the row (non-periodic subject; mispredict risk).
- **[ART-HYB-COUNTED]** STATE:not-started (same filing) — a count-collapsed, capture-free hybrid
  verifies the collapsed count on the DFA window and skips the VM, in r3's form with the capacity
  and budget guard.
  - **EVIDENCE:** A09 L4 (rvA09 ~30% of post-L1 hit); population 5 bench (level-context, ctx-*) /
    0 corpus.
  - **NEED:** S4 on A09 L4 r3, after START-SET stage 3 (same cells); r2 is the
    `changes-giveup-surface` counter-example to cite in the design.
- **[ART-LAZY-FRAMELESS]** STATE:not-started (same filing) — a lazy span loop whose continuation is
  capture-free and frameless extends without a frame (capacity check and step charge kept).
  - **EVIDENCE:** A09 L5, 0 repairs; population ≤5 bench / ≤54 corpus.
  - **NEED:** the frameless-continuation census; S4 on A09 L5. Moot on hit under [ART-HYB-COUNTED].
- **[OPT-A] / START-SET stage-5 cross-note (no new row)** — per-alternative rare-byte `memchr`
  streams for a leading literal alternation (A09 L1).
  - Population 21 bench / 11 corpus, but only 3 / 2 predicted cheaper by the prior: the selection is
    findings data (as I2).
- **[OPT-B] cross-notes, CODEGEN-MICRO (flagged, D119: not loop leads)** — I9 (byte tables; note
  `form_char_step0.md`'s size recommendation against them) and I10 (run counters in locals).
- **No row**: I2 ([FINDINGS] already delivers it, measured), I8 (shipped, follows I6), I11 (START-SET
  stage 3 itself).

**Suggested order (population × reviewer expectation ÷ cost; a ranking without S4 numbers).**

1. START-SET stage 3 landing (I11, in flight).
2. The CTX trio [ART-HYB-COUNTED] / [OPT-3-RUNEND] addendum / [ART-LAZY-FRAMELESS] on the 5 CTX
   cells.
3. The [ENG-TACTICS] (b) DFA instance (17 bench).
4. [ART-POSS-ARMS] + [ART-TRAIL-ELIDE] + [ART-VMCTX-START] as one VM-body batch: tiny population,
   large per-cell ratio.

K88's twin is the cheapest measurement in the list.

## 5. Standing questions (docs/design/CLAUDE.md), answered for this document

- **Measurement regime:** relevant only as the join. This document measures populations, not time:
  compile-side, the Mac, the pin compiler. Time is S4's (Linux) and is joined per §1.4.
- **Independent control:**
  - Each classifier's positive and negative control (`gen/selftest.txt`).
  - For "already shipped" claims, the shipped compiler's own output on a variant spelling.
  - For I11, the ssbuild3 count agrees independently with startset.md's 18.
  - The prior-based classifiers (K1, K12) share their source with the emitter's own pick on
    purpose: they ask what the EMITTER can see.
- **What moves on regeneration:** every count. Re-run `gen/census.py` at the new pin; the
  `SS3`-dependent K11 column goes stale the moment stage 3 lands on main, when SS3 = PCREC. Line
  numbers in §2 are at `6a0b7953`.
