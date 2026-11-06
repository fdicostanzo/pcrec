# Variable-width (bounded) lookbehind — design

**Status: PROPOSED rev 4 + erratum r3-1106** (the stage-1 build lane vlbbuild applies review r3's text fixes; block below) (lane vlbrev4, opus, 2026-11-06; plan row [VLOOKBEHIND]). Rev 4 applies
the RULED re-check `docs/dev/reviews/2026-11-06-r2-vlookbehind-recheck.md` (READY WITH LISTED TEXT
FIXES); read the REVISION 4 block first, then REVISION 3. Rev 4's evidence is
`docs/dev/lanes/vlbrev4_evidence/`. Rev 3 (lane vlbrev3, opus, 2026-11-06) re-spelled
§5.1's loop in the cursor-rung shape (Frank's ruling, 2026-11-06).
Rev 3's evidence is `docs/dev/lanes/vlbrev3_evidence/`. Rev 2 was lane vlbrev2's (opus,
2026-11-05). Rev 0 was lane vlbdesign's, rev 1 lane vlbrev1's. Rev 2 applies the RULED re-check
`docs/dev/reviews/2026-11-05-r6-vlookbehind-recheck.md` (READY WITH LISTED TEXT FIXES). It is text
only: no build go. Rev 1 applied the RULED review `docs/dev/reviews/2026-11-05-r3-vlookbehind.md`
(NOT READY, text-only rev 1). Rev 2's evidence is `docs/dev/lanes/vlbrev2_evidence/premise.out`.
Starts from the investigation `docs/dev/lanes/vlbinv_report.md`
(its §1 semantics are not repeated here) and its owner addendum (candidate D). Evidence: rev 0's
`docs/dev/lanes/vlbdesign_evidence/`, rev 1's `docs/dev/lanes/vlbrev1_evidence/` (`probe.c`, a
libpcre2 10.46 library probe; `cells.out`, every cell rev 1 adds). PCRE2 facts come from the
installed libpcre2-8 10.46 used as a library and from public docs. The pinned source copy was not
opened (D181). One question for a pcre2-reader is in §12.

## ERRATUM r3-1106 (review 2026-11-06 r3, ruled) — read first

A text pass applied by the stage-1 BUILD lane (vlbbuild) as its first commit, per the r3 RULING
(`docs/dev/reviews/2026-11-06-r3-vlookbehind-ready.md`: every disposition accepted). Changes are
marked inline as `[r3-1106 ID]`. No mechanism changes. Each item, and where it now lives:

- **FIXIND-1 (rule (b) keyed by what a row stands for).** DD12a(i)'s rule (b) cannot key presence
  by entry: byte's `SPAN_CASELESS_UCP` is a SUBSTITUTE entry (in the mask instead of
  `SPAN_CASELESS`, enc.h) and defines the same symbols. The reader prints a `stands-for` column
  (`SPAN_CASELESS_UCP` → `SPAN_CASELESS`); the counter key is the entry a row stands for, so a
  substitute and its original count as one key, and rule (b) admits one-sided presence only for a
  key that one backend alone carries. The head matcher accepts ANY return tokens, `unsigned char`
  included (the pre-existing excision hole the critic found) (§5.6 item 3).
- **FIXIND-2 (UCP witness).** `(*UCP)(?i)(a)\1x` joins DD12a(i)'s explicit witness list, so the
  derived floor reaches the byte-only UCP row on a default (250-block) run (§5.6 item 4).
- **FIXIND-3 / READY-2 (more hand lists, exact guards).** U6 gains: the [M5-SEAM] `resid_backdecl`
  exact guard 7 → 9 (`run_codegen_tests.sh`, the `-ne 7` line) with its header ("one per
  top-level branch" becomes "one per back-step SITE"); an exact `fwd_step` guard of its own (= 2:
  `residlbrange` and its `-e utf8` twin, the existing per-entry guard's precedent);
  `tests/partlayout/writers.tsv`'s A4 class map gains `fwd_step`; `run_partlayout.py`'s `sec_seam`
  name regex gains `fwd_step`; the [LOSS-REVIEW c1] `-fPIC` nm arm gains the `residlbrange`
  fixture (§6 U6).
- **FIXIND-4.** `size_t <p>_lb_count = 0;` (the `span_cursor`/`rv` precedent), not uninitialised
  (§5.6).
- **FIXIND-5 (W-low's plant).** W-low's sabotage row uses the 1-edit equivalent: `vm_set_line`
  renders an UNTRAILED write (`slot_values[x] = v;`) for `SLOT_LB_LO*` slots. Same semantics
  (untrailed `LO_i`); the answer cell and the codegen detector see it (§7 W-low).
- **FIXIND-6 (stated, not derived).** `pcrec_enc_entry_symbols` and the emitter share ONE predicate
  for the UCP side emission, so the condition has one spelling. The general per-row side-emission
  hook is FILED as a plan row, trigger: a second side emission (§5.6 item 1).
- **READY-1 (S133/S134 re-cut).** S133's `SAB_BEFORE` is a 6-line block (seek, note, sentinel branch
  to `pcrec_vm_tgt_fail()`); the `range` row's `lo_i` sentinel goes to `L_n_i` with its own note.
  So "one shared line, `SAB_COUNT=1` unchanged" is false: U8 re-cuts S133 and S134's
  `SAB_BEFORE`/`SAB_AFTER` and `SAB_DOC_FIGURE`s on the shared builder line (§5.6, §7).
- **READY-3 (oracle).** U6 owes in `pcre2_ctypes.py`: UTF-8 encoding of `str` patterns under
  `PCRE2_UTF` (the `utfcheck_arm.py` precedent), a `PCRE2_MATCH_INVALID_UTF` constant, and a
  compile context with `pcre2_set_max_varlookbehind` so gate 3's `max_varlookbehind = 0` control
  is askable; `tests/backrefs/CLAUDE.md` is a reader (§6 gate 1, U6).
- **READY-4 (owed items assigned).** W-low's asan confirmation + `--work-budget` compile → U8;
  gate 3's accept-set/classification harness and gate 4's budget cell → U6; DD12a(i)
  re-validation plants (§5.6 item 5) → U6; W-low's codegen detector and K49's member floor → U6.
- **READY-5.** Gate 6 runs under `make test-encoding-checks` (not `make test-codegen`).
- **READY-6 (function names).** The totals step is in `vm_plan`; `VmFrame` is built in
  `vm_emit_search_body`; the `$_back_step` mask OR is in `vm_look_behind` (§5.1b, §5.6, U3-U5).
- **READY-7 (U1 readers).** U1 changes the stored widths representation (`const int *widths`,
  internal.h, and its comment) to a pair per branch, and its readers move: `la_lb_raise`, the
  hook and `pcrec_lookaround_fix_widths`, `vm_look_behind`, `vm_count_slots_look`,
  `vm_cost_look`; `LA_MSG_MAX`'s comment is re-read (§6 U1).
- **READY-8 (U7 readers).** Flipped `refused.rxt` cells move `run_lookaround_diff.sh`'s exact
  `NPO` guard; S136's `SAB_DOC_FIGURE` moves (§6 U7).
- **READY-9 (U4/U6 readers).** `docs/design/stream/arev.md`'s "today's four" `VmSeek` members (five
  after); K49's header in `run_encoding_checks.sh` ("spelled TWICE", "linked next_pos").
- **READY-10 (K49 independence).** The utf8 `fwd_step` row is its OWN literal text, never built from
  `next_pos`'s text or a shared macro and never calling it, so K49's tie compares two sources
  (§5.6).
- **READY-11 (lblow, answer-neutral).** A `vm_slot_lblow` off-by-one or a collision with a span low
  has no answer witness. It is caught by the slot legend (`SLOT_LB_LO<j>` names) and by the
  emitter's check that the count pass's two sub-totals equal the emitter's own. Stated, not
  witnessed (§5.1b).

## REVISION 4 (review 2026-11-06 r2, ruled) — read first

Changes are marked inline as `[r2-1106 Fn]`. The review found no answer bug in rev 3's loop. Every
fix is text, plus harness work the build owes. In summary:

- **F1: the forward step is a seam ENTRY, `$_fwd_step` (the manager's ruling).** Rev 3 spliced the
  encoding's `advance` TEXT into the VM body. That was a second encoding splice inside the matcher,
  so DD12a(i) went red on every correct `range` build, the body's length (and so the entry shape)
  could differ by encoding, and the utf8 text carried a K49 comment that is false here and survives
  `-fno-comments`. Rev 4 makes the step a residual entry like `$_back_step`: one row per backend,
  `engine_callable`, `inline_def`, in the mask only when an artifact has a `range` branch. The body
  then holds one CALL line, the same text under both encodings. Its contract is `next_pos` over the
  prefix `[0, bound)`. No existing artifact moves a byte (the STOP RULE is not triggered, §5.6).
  - DD12a(i) reads its region (1) entry list FROM THE SEAM (a seam function names the symbols each
    entry defines; a test reader prints them), instead of the hand-written `SIG_RE` alternation.
    K49 reads its agreement sites from a seam-declared mask of the entries that spell the boundary
    rule. §5.6 states both concretely. The derivation is proportionate to stage 1, so the named-region
    fallback is not taken (§5.6 says why, and what the fallback would cost).
  - W14's byte-step arm gets two named detectors: the [M5-SEAM] per-site count and K49's tie (§7).
- **F2: W-low has an answer-level cell.** `(?:(?*.*(?<*a?))b)*$` on `bc` is [2-2] in libpcre2 (byte
  and UTF, every start; `vlbrev4_evidence/premise.out`). With `LO_i` untrailed, the loop runs away.
  Rev 3's "only a later evaluation on a forward path" argument was false: a non-atomic lookahead
  re-evaluates the lookbehind at an EARLIER cursor while an older evaluation's frame is live.
  Trailing `LO_i` is what keeps the loop sound (§5.1, §7).
- **F3:** `K_i` is ONE artifact-wide local, `<p>_lb_count`, declared from a `VmFrame` bool that the
  count pass's `range` count sets; its name has one source (§5.6).
- **F4:** `LO_i` slots are an ARITHMETIC SUB-BLOCK at the top of the `low` family, with no owner list
  (§5.1b).
- **F5:** sabotage anchors (S133, S123), the builder shapes, the W-low plant, S-U4's re-aim cell
  `(?<=ab)x` and W12(a)'s mechanism are spelled (§5.6, §7).
- **F6:** gate 1's harness gains three named modes, `byte`, `utf8` and `utf8-invalid`, each with its
  own counted population (§6).
- **F7:** [VMREC]'s member list lives in `docs/design/plan_row_bodies/VMREC.md`, written by the
  stage-1 build commit (§5.6). §13 Q5 and Q6 are ANSWERED (rulings 7 and 8).
- **F8, F9 (doc):** §5.1a's model claim is restated as "the candidate SEQUENCE"; the stale 160-byte
  note and the rev-1 sentence are corrected.
- **§6 gains the complete stage-1 build-unit list**, with every reader of what each unit changes.
- **§16d** maps every finding to its section.

## REVISION 3 (owner ruling 2026-11-06: the cursor-rung shape)

Changes are marked inline as `[r-cursor]`. The owner's ruling: "if it's able to always be true then
do it. if it's occasionally true then it should use a decision table". "It" is the CURSOR-RUNG
shape for §5.1's loop (`vlookbehind_pieces.md` §6): the candidate START POSITION lives in the retry
frame, and one trailed value is written per evaluation, instead of rev 2's trailed counter `D_i`
rewritten per candidate.

**Verdict: ALWAYS.** The cursor shape is sound for every lookbehind body this design admits, at
stage 1 and at stage 2. So it is the `range` row's one spelling, and no decision table between the
two shapes is needed (§5.1a). The manager's argument holds, with two refinements that are SPELLING
conditions, not body classes:
- **The farthest start is not "hi characters back, clamped at the subject start".** Under UTF-8 the
  back-step also stops at a run it cannot validate. The farthest start is the farthest position
  `$_back_step` reaches within `hi` characters. The loop finds it with rev 2's own retry
  (count − 1 on the sentinel), run once per evaluation instead of once per candidate.
- **The one-character step must be bounded by the cursor.** The encoding's own forward step (the
  `advance` text, K49; `[r2-1106 F1]` in rev 4 the seam entry `$_fwd_step`) skips continuation
  bytes up to a bound. With the subject length as the bound,
  a stray continuation byte AT the cursor makes the step jump past the cursor, and the loop never
  ends. Bounded by the cursor, the step lands exactly on the back-step's own character boundaries,
  on every input, ill-formed ones included.

Evidence (`vlbrev3_evidence/`, README in §15):
- an exhaustive byte-level check of the two loops' candidate sequences. It covers 8,583,480 cells
  (every subject over an 8-byte alphabet of UTF-8 leads, continuations and 0xFF up to length 5,
  and over 5 bytes at lengths 6-7, × every cursor × nine `[lo, hi]` ranges). Result: 0 differences
  between the cursor shape and rev 2's counter shape. Each of the three wrong spellings differs
  (unbounded step: 288,168 cells, a runaway among them; sentinel → subject start: 3,398,699;
  sentinel → nearest start: 591,194);
- the byte-mode model with a literal `cursor` evaluator. Over vlbpieces' two sweeps it differs from
  libpcre2 on 0 of 54,579 cells (the `range` control also 0);
- 52 libpcre2 cells (bytes, UTF-8, caseless multi-width, ill-formed subjects under
  `PCRE2_MATCH_INVALID_UTF`, `\G`, stage-2 backreferences), each a witness or a control (§7).

What rev 3 changes, in summary:
- **§5.1 re-sketched.** One trailed slot `LO_i` (the nearest start) per `range` branch, and one
  untrailed local `K_i` (the far step's count). The frame saves the candidate start, and exhaustion
  restores the cursor from `POS`. §5.1c re-traces the four F1 cells, W12, and three UTF-8 and
  ill-formed cells.
- **Deleted:** `D_i` and its `SLOT_COUNTER` slot (V4's ruling has no object). Also: the
  per-candidate back-step and its run-time count rendered from a slot (V3); the per-candidate
  `RX_CHARGE_WORK(D_i)`; the trail term `Σ_range (hi_i − lo_i + 1)` (V1); the `growable` and `pt`
  ceiling proposal; the trail checkpoint on every `range` loop (it remains only where the body
  itself writes the trail, §5.1b); and §5.5's "alternative" paragraph (it is now the design).
- **The trail term is `2 + (number of range branches)`**, independent of `hi − lo`. So a raised cap
  is a one-row change in storage as well as in acceptance (§5.2, §5.5).
- **Work per evaluation** is at most `hi + (hi − lo)` back-step and step units, instead of
  `(hi + lo)(hi − lo + 1)/2` (§5.5).
- **The seam:** no new entry. It uses `$_back_step` twice per `range` branch (`lo` literal, and the
  far count from a local) and the encoding's existing `advance` text, bounded by the cursor. That
  is a new caller of an existing field, and `advance`'s `@N` operand comment widens (§5.1a, §5.6).
  `[r2-1106 F1]` SUPERSEDED: the step is a new entry, `$_fwd_step`, and `advance` is untouched.
- **Record vocabulary** (§5.6): one new `VmLocalKind` member, one new `VmSeek` member and a local
  count operand on `VSK_BACKSTEP`. No new `VmKind`. Whether D153's remodel-first ruling covers
  sub-kind members is the manager's call (§13 Q5). The slot's family is the manager's answer-free
  call too (§13 Q6; leaning: the `low` family).
- **Witnesses re-aimed:** W6, W11, W12. New: W13-W16 (§7).
- Owner questions 1 and 2 are ANSWERED (A; the ceiling rides stage 1), and §13 records them.
- **§16c** maps the ruling to every section it changed. **arev.md's pick-up list** is §16c's tail.

## REVISION 2 (review 2026-11-05 r6) — read first

Corrections are marked inline as `[r6 Vn]`. No mechanism changes: §5.1's statements, their order
and §5.1c's traces stand. In summary:

- **The trail is sized for the loop (V1, answer level).** Each `range` candidate leaves one live
  trail entry (`D_i`'s write), and today's cost pass charges the lookbehind a constant 2. A literal
  rev 1 build gives up with `PCREC_ERR_FRAMES` on `(?<=a{1,2})x` / `bax`, where libpcre2 answers
  [2-3]. `vm_cost_look`'s trail term becomes `2 + Σ_range (hi_i − lo_i + 1)` (§5.5, derived from the
  code). §5.1b's table gains a trail column, and §7 gains witness W12. The loop is also a trail
  cycle, so K134's rule puts a trail checkpoint on its back edge (§5.1b).
- **§5.1b's table declares every reader (V2, V4, V5).** The rewrite claim gains a 5th item, the
  negative end-check, which is a SELECTION and not a rewrite. The table gains columns for labels
  (allocated only for `range` branches) and for role texts (which are C comments under
  `-fcomments`). `D_i` is a `SLOT_COUNTER` slot (RULED, V4): no new slot family.
- **Operand meanings (V3).** The back-step and the work charge read `D_i`'s VALUE,
  `(size_t)slot_values[<slot>]`, never the slot index.
- **Accept set (V6, RULED).** pcrec keeps accepting an unbounded repeat of a zero-width body inside
  a lookbehind (`(?<=(?:)*a)x`), which libpcre2 refuses. It is a stated divergence: G1, gate 3 and a
  spec hunk name it.
- **Gates and rows that move (V7, V8, V12).** Gate 1 names its harness (`run_lookaround_diff.sh`).
  Gate 2 names its instrument and the re-pin. S133/S134, S-U4 and S136's branch are listed, and a
  `range` codegen fixture is added.
- **Limits rows in the table's own schema (V9).**
- **Rulings and readers (V10).** Stage 1 deliberately reverses [DD-14.LB]'s ruled refusal. The two
  D27 extracts are re-cut, and the D27-owned corpora get an owner.
- **Doc items (V11, V13-V16).** INTERNAL's second producer; how §5.1 composes with `vm_look`;
  §5.1c's framing sentence; G1's dependency on owner Q2, and the `max_varlookbehind` candidate filed
  at [IFACE-PUSH]; a verbs line in §14.
- **§16b** maps every r6 finding to its section.

Owner question 1 (keep today's bytes by a declared selection, or the loop everywhere plus an abi
event) stays OPEN (§13). Rev 2 states each fix under both answers.

## REVISION 1 (review 2026-11-05 r3)

Corrections are marked inline as `[r3 Fn]`. Rev 0's refuted claims are recorded where they stood,
not edited away. In summary:

- **§5.1 re-sketched (F1).** The retry frame is pushed BEFORE the back-step and saves the CURSOR.
  Each candidate re-steps `d` back from that cursor, and the next branch always starts from it.
  Rev 0's frame saved the candidate, which sent the next branch the wrong cursor. Three libpcre2
  cells (`(?<=a{1,2}|b)x` on `bx` = [1-2], and two more) were nomatch under rev 0's sketch. §5.1c
  hand-executes the new sketch literally on four cells.
- **The fold is a declared selection, not a constant fold (F12).** The one-length emission (today's
  bytes) is SELECTED by the width fact `lo == hi`, a row of a declared two-row emission table
  (§5.1b). The table states the work amount per candidate and the slot allocation. Owner question 1
  is RE-ASKED with this (§13).
- **Two lookbehind limits (F4).** PCRE2's absolute 65535-character branch ceiling joins the 255
  cap. The cap is restated as accept-set POLICY, per the owner's answer: correctness needs no cap
  (§5.2). Each limit gets a `limits.def` row.
- **Stage 2 rewritten (F2, F3, F5).** A reference counts its group's exact [min, max] at both
  ends. Duplicate-name references, any `(?|`, unbounded or recursive groups and self-reference are
  refused. Forward references need DD-14.LB's deferral and a per-group width memo. The acceptance
  table is the ruling lens's (§6). The fixed-group half needs none of stage 1's loop.
- **Gate 1 names D142's stated UTF divergence (F7).** Spec hunks are completed (F6). Witnesses are
  repaired or added: W6 (F8), S136 (F9), W3b (F10), W11 (F1). WD6 is noted (F11).
- **Text fixes.** The consequences of D58 and D153/[VMREC] (F13), the goals and population text
  (F14), R03 as in-body precedent (F15), and the LOCATE × FINISH family with the [ENG-LOOK]
  existence form plus a HELD plan row [LB-EXIST] (F16).
- **§16** maps every finding to its section.

**The decision, in one paragraph.** There is one mechanism. For each top-level branch, in written
order, try CANDIDATE STARTS FARTHEST FIRST. At each candidate, run the branch's body FORWARD through
`vm_emit` and keep it only if it ends exactly at the cursor. This test is the end-check, and it now
backtracks into the body.

B and D are the same mechanism with two different SOURCES of candidate starts:
- B takes every position whose distance from the cursor is inside the branch's width range.
- D takes the accepting positions of a reverse DFA of the branch, run back from the cursor.

So the source is a declared first-match CHOICE ROW (D186), and this is a LOCATE × FINISH instance
(D156) `[r3 F16]`. `range` (B) ships in stage 1 and is the total fallback. `reverse-dfa` (D) is a
HELD row with a written evidence requirement and two prerequisites (§5.4). Its home is the stream's
one reverse `AUTO` kind (roadmap A-REV), hosted in a VM body. Lookbehind is A-REV's first client
(Frank, 2026-11-05).

Today's fixed-width lookbehinds keep their exact bytes because the emitter SELECTS the one-length
emission by the declared width fact `lo == hi`. This is a declared row, not a constant fold
`[r3 F12]` (§5.1b; owner question 1, re-asked).

## 0. Goals

Ranked: the higher goal wins a conflict.

1. **G1 Answers (PCRE2 users porting patterns).**
   - The promise: every lookbehind that libpcre2 10.46 accepts at its default `max_varlookbehind`
     (255), and whose body uses only constructs pcrec implements in a lookbehind, compiles in pcrec
     with the `lookaround` module and answers identically.
   - Out of scope `[r3 F14]`: pcrec refuses callouts, `(?|` and verbs inside a lookbehind today,
     and they stay refused.
   - Measurable: a libpcre2 differential over the generated cell set of §6 has 0 differing answers
     (match, every group, nomatch), outside D142's stated class (§6 gate 1). The accept set stays
     inside PCRE2's: 0 patterns that pcrec compiles and libpcre2 refuses, over the same generator
     plus the boundary cells of both limits, outside the one stated accept-set divergence below.
   - **G1's accept-set clause is false TODAY** `[r3 F4, F14]`. pcrec compiles `(?<=a{65535}b)x` and
     `(?<=(?:a{1000}){66})x`, which libpcre2 refuses (err 187). Stage 1 restores it with the 65535
     ceiling (§5.2). G1 outranks G2, so this refuses patterns that compile today. There are none in
     the population.
   - **That holds at stage 1 only if the ceiling rides stage 1** `[r6 V15]` (owner question 2). If
     the ceiling gets its own row, G1's measurable is false when stage 1 lands, and gate 3's
     ceiling cells move to that row.
   - **The stated accept-set divergence** `[r6 V6, RULED]`. A lookbehind branch containing an
     UNBOUNDED repeat of a body that matches no characters (`(?<=(?:)*a)x`, `(?<=(?:\b)*a)x`,
     `(?<=(?:)+a)x`) is refused by libpcre2 (err 125, at every `max_varlookbehind`). pcrec compiles
     it today as one-length, by design (the zero-width repeat consumes nothing:
     `pcrec_cwmax`'s A_REP arm, src/opt/mrl.c), and keeps accepting it. D26's addendum: accepting
     more than PCRE2 is not a defect. Gate 3 counts the class on its own line, and the spec says so
     (§10). No pattern in the population uses it. Stage 2 inherits the same choice for references
     to such groups.
2. **G2 Stability (callers with today's artifacts).**
   - The promise: no pattern that compiles today changes bytes. The one exception is G1's ceiling.
   - Measurable: the identity gate over every corpus artifact containing a lookbehind shows 0 bytes
     differ.
   - This holds only if owner question 1 is answered "keep the bytes" (§13). That question must be
     closed before the build go `[r3 F14]`. `[r2-1106 F9]` CLOSED: answered (A), 2026-11-06.
3. **G3 One mechanism (maintainers, Frank's general-mechanisms rule).**
   - The promise: one candidate loop, and fixed width is its one-length case. The one-length bytes
     are a declared emission row selected by the width fact (§5.1b) `[r3 F12]`, not a second
     mechanism, and the stream ratchet does not grow. (Rev 0 said "no parallel path" with no
     qualifier; the review showed the bytes need a selection.)
   - Measurable: stage 1 adds no new row to `docs/design/stream/roadmap.md` §5's inventory. The
     refusal arm for bounded bodies is deleted: the deleted special case is the benefit.
4. **G4 Bounded cost (every caller).**
   - Body runs: a lookbehind evaluation runs a branch's body at most (hi − lo + 1) times.
     `[r-cursor]` The loop's own charge per evaluation is at most `hi + (hi − lo)` units: the two
     back-steps once, then one unit per one-character step (§5.5). Rev 2 charged `d` per candidate.
   - Frames: at most ONE LOOP FRAME per branch is live `[r3 F14]`. A non-atomic `(?<*` also
     leaves the body's own choice points live, as today.
   - Trail `[r-cursor]`: ONE lookbehind-owned entry per `range` branch per evaluation (its `LO_i`
     write), beside today's two, whatever `hi − lo` is. The cost pass charges exactly that (§5.5).
     Rev 2's `hi_i − lo_i + 1` per branch `[r6 V1]` is retired with the counter it counted.
   - Compile time: no blow-up. Per site there is one body copy per branch, as today, plus a
     constant number of records.
   - Measurable: the work charge in the emitted text. `[r-cursor]` A varying branch's emission is
     within **one slot, one local and about 20 emitted C lines** of the same branch made
     one-length. `[r2-1106 F1]` The forward step is one call line under both encodings; the
     `$_fwd_step` definition (about five code lines, its doc halves only under `-fcomments`) comes
     once per artifact, ahead of the program, as `$_back_step`'s does. Rev 3 said "under UTF-8, the
     encoding's step adds two more lines"; the spliced text was about eight. Rev 1's "8 lines" bound
     `[r3 F14]` was the counter shape's. A trail checkpoint appears on the loop's back edge only
     where the body itself writes the trail. Where one does, K134's helpers come once per artifact:
     38 lines measured on an existing checkpoint artifact (`vlbrev2_evidence/premise.out`). The
     per-branch figure is an UNMEASURED design bound, checked from the emitted text at build.
5. **G5 Speed where measured (later, D).**
   - The `reverse-dfa` source ships only where per-regime evidence shows no regime slower than
     `range` beyond noise (the D186 choice bar).

**Non-goals.**
- A reverse VM (Frank, 2026-11-05: "I'm certainly not going to try a reverse vm just for this").
- Speed of variable lookbehind beyond the loop in stage 1 (one bench pattern uses it).
- Exposing the 255 cap as a setting: owner ruling, deferred to [IFACE-PUSH]. That row now carries
  it as a dated CANDIDATE line in its long-form body,
  `docs/design/plan_row_bodies/IFACE-PUSH.md` `[r6 V15]`.
- Lookaround inside the DFA engine ([ENG-LOOK]).
- `\K` inside a lookaround: both libraries refuse it (err 199).
- Unbounded lookbehind. Its reason is restated `[r3 F16]`: PCRE2 refusing it (err 125) is the
  weakest argument after D26's addendum. The real reasons are zero demand and the `range` row's
  O(n³) worst case without an automaton filter. It is filed HELD as [LB-EXIST] (§5.4), with the
  trigger "a real pattern needs it".

## 1. Premise, verified on this branch

Rev 0 (`vlbdesign_evidence/premise.txt`, `build/pcrec --features all` at `4e35534af`):
- `(?<=a|bc)x` compiles.
- `(?<=a{1,3})b` is refused, with "variable-length lookbehind is not implemented ... (this one can
  match 1..3 characters)".

Rev 1 premise test (`vlbrev1_evidence/premise.out`, libpcre2 10.46): F1's three cells match in
libpcre2, so rev 0's sketch was wrong where the review says it was:

| pattern | subject | libpcre2 |
|---|---|---|
| `(?<=a{1,2}\|b)x` | `bx` | [1-2] |
| `(?<=a{2,3}\|b)x` | `bx` | [1-2] |
| `(?<=a{1,2}\|bc)x` | `bcx` | [2-3] |

The code facts rev 1 adds were READ at main `2056360d7`:
- `vm_look_behind_branch`'s prologue order in `src/gen/emit_vm.c`: guard, NEXT-BRANCH push at the
  cursor, `vm_work(k)`, `VSK_BACKSTEP`, sentinel.
- `VSK_BACKSTEP` renders a literal count (`vm_r_seek`, src/gen/vm_stmt.c), while `VK_SEEK` already
  carries a `slotx` operand.
- The seam's `$_back_step` takes a run-time `size_t k` in both encodings (src/enc/enc_byte.c,
  src/enc/enc_utf8.c).

The STOP RULE was not triggered: every fix is sound in text.

## 2. Semantics to reproduce (new cells only; vlbinv §1 has the rest)

All MEASURED with libpcre2 10.46. Rev 0's cells are in `vlbdesign_evidence/d_match.out`,
`d_utf.out`, `w_match.out` and `startpos.out`. Rev 1's are in `vlbrev1_evidence/cells.out`.

- **Atomic and possessive parts SHRINK the body's set of strings.** So a machine built over the body
  with the atomicity dropped is a SUPERSET.
  - `(?<=(?>a|ab)b)x` on `abbx` is nomatch; the non-atomic `(?<=(?:a|ab)b)x` matches (3,4).
  - `(?<=a{1,2}+a)x` on `aax` is nomatch where `(?<=a{1,2}a)x` matches.
  - The negative forms flip: `(?<!(?>a|ab)b)x` on `abbx` matches.
- **Context before the candidate start is read.**
  - `(?<=\ba{1,2})x` matches on ` aax`, not on `aaax` or `baax`.
  - `(?<=^a{0,2})x` matches on `aax`, not on `aaax`.
  - These are byte-mode facts at startpos 0. Under `PCRE2_UTF` with startpos > 0, see the D142
    bullet below `[r3 F7]`.
- **A nested lookahead may look past the cursor**: `(?<=a{1,2}(?=xy))x` matches on `aaxy`, not on
  `aaxz`.
- **Non-atomic retry walks every viable length, gaps included**: `(?<*(a|aaa))c\1` on `aaaca` is
  (3,5) g1=(2,3), trying length 3 first, then length 1. The atomic `(?<=` form is nomatch.
- **Branch order beats length.**
  - `(?<=(ab)|(b{1,2}))c` on `abbc` is g2=(1,3): branch 1 fails, branch 2 matches at its longest.
  - `(?<=(a)|(aa))c` on `aac` is g1=(1,2): branch 1 wins though branch 2 is longer.
- **The next branch starts from the cursor, after a varying branch** `[r3 F1]`:
  - `(?<=a{1,2}|b)x` on `bx` is [1-2]: branch 1 exhausts its candidates.
  - `(?<=a{2,3}|b)x` on `bx` is [1-2]: too little subject for branch 1's minimum.
  - `(?<=a{1,2}|bc)x` on `bcx` is [2-3]: branch 1 exhausts at length 1, and branch 2 needs 2.
- **Before `startpos`**: from offset 2, `(?<=a{1,2})b` on `aab` is (2,3) and `(?<!a{1,2})b` is
  nomatch.
- **UTF-8 counts characters.**
  - `(?<=(é{1,2}))x` on `aééx` (UTF) is (5,6) g1=(1,5).
  - `(?<=(é{1,2}))x` on `éx` is [2-3,0-2] `[r3 F8]`. Fewer characters than `hi` precede the
    cursor, but at least `hi` bytes do.
- **The end-check's witnesses.**
  - `(?<=a{1,2})x` on `abx` is nomatch: at length 2 the body ends at 1, not 2.
  - `(?<!ab?)x` on `acx` matches (2,3): length 2's body ends early, and length 1 fails.
- **The body backtracks into its trailing greedy quantifier** `[r3 F10]`:
  - `(?<=a{1,2})a` on `aaa` is [1-2][2-3]. At cursor 1, `a{1,2}` from 0 takes two characters and
    must give one back.
  - `(?<!a{1,2})a` on `aaa` is [0-1].
- **D142's stated UTF divergence (not new semantics)** `[r3 F7]`:
  - `(?<=\ba{1,2})x` on `baax` from offset 3 is nomatch in byte mode and [3-4] under `PCRE2_UTF`.
    libpcre2 clips backward reads at `startpos − LB`; pcrec deliberately does not (D142 item 3,
    `match_api.md` §9.4¶8).
  - The fixed twin `(?<=\baa)x` diverges the same way today.
  - A varying body widens the exposed set. Any candidate at distance `hi` whose `\b`, `\B` or
    nested lookbehind reads one character further is exposed.

## 3. The two candidates, side by side

**B, the step-back loop** (vlbinv §3; `lookaround_design.md` §2.5's sketch). For each branch, the
candidate starts are the positions `lo..hi` characters before the cursor, farthest first. They are
clamped by the subject start: absolute, never `startpos` (S135). Each candidate is tried in three
steps: back-step, forward body, end-check. A failure resumes the next candidate through a retry
frame, then the next branch.

**D, reverse DFA then forward VM** (owner addendum).
- A reverse DFA of the branch runs back from the cursor, at most the branch's width. It gives the
  positions where the branch can start.
- The farthest is tried first: one forward anchored VM run from it, required to end at the cursor,
  sets the captures.
- The addendum proposed that capture-free and negative lookbehinds need the DFA only.

| vetting item | B (range source) | D (reverse-dfa source) |
|---|---|---|
| **order** (branch, then longest) | The loop's order, by construction. | Per-branch machines work: the farthest accept IS the longest step-back, the output today's reverse block already records (`emit_reverse_block`: the smallest accepting position). One machine for all branches needs priority tags (`alt_dispatch_study.md` (c)). The union without tags is WRONG: `(?<=(a)\|(aa))c` on `aac`. |
| **non-atomic retry** | The retry frame stays live; the next candidate is one character nearer. | Needs EVERY accepting start in order ([LANDWALK-ALLACC]'s output, "every accepting start ascending" = farthest first). Two forms: a re-walk from the cursor to the last tried start (stateless, O(width) per retry), or a 255-bit set per evaluation (frame storage). Re-walk recommended: retries happen only on a non-atomic form whose follow fails. |
| **captures inside** | Trail rewind per failed candidate, as today. | The forward VM run sets them; the DFA cannot. |
| **atomic / possessive inside** | `vm_emit` as today. | The machine is a SUPERSET (`Nfa.erased` & `NFA_ERASED_ATOMIC`, src/ir/nfa.c `compile_ast`'s A_ATOMIC arm), so its accepts are candidates to CONFIRM, never answers. Witness: §2 row 1. |
| **nested lookaround** | `vm_emit` as today. | Erased (`NFA_ERASED_LOOK`): a superset, confirmed by the VM. A lookahead can read past the cursor (§2). |
| **capture-free, negative "DFA only"** | n/a | TRUE only where the machine is EXACT (`erased == 0`) and the body has no observable side effect. Otherwise the DFA is a sound FILTER for both polarities (no accept in the superset means none in the truth), never the answer. pcrec refuses callouts in a lookbehind today (`pattern_language.md` §7.11¶3), so the side-effect conjunct guards a refused construct. It is kept as a fact for the day callouts are admitted there `[r3 F14]`. |
| **backreference inside** (stage 2) | The group's exact width at both ends; DD-14.LB's deferral for references not yet parsed; refusals (§6 stage 2) `[r3 F2, F5]`. (Rev 0: "needs only a width": refuted.) | No machine: the NFA builder has no lowering for `A_BREF` (src/ir/nfa.c, `compile_ast`'s A_BREF arm, "NO MACHINE"). The row declines and `range` serves. |
| **`\K` inside** | Refused by both libraries (err 199), unchanged. | Same. |
| **UTF-8** | `[r-cursor]` The nearest start is `lo` characters back; the far step's count is clamped to `min(hi − lo, LO)`, an upper bound (bytes ≥ characters). A far step that returns the seam's sentinel is retried one shorter, once per evaluation. Each later candidate is one character nearer, by the encoding's own forward step bounded at the cursor. The EXISTING `$_back_step` entry; `[r2-1106 F1]` the forward step is a new entry, `$_fwd_step` (rev 3 said "the `advance` text, so no new seam entry") (§5.1, §5.1a, §5.6; `[r3 F13]`). | Byte machine over UTF-8. Accepts fall on character boundaries for valid input. The 255 cap is a compile-time character count, so no run-time count is needed. |
| **start of subject** | The clamp, absolute. | The walk's floor is 0, not `search_from` (the landmark walk's floor, `dfa_dir_landmark`'s `at_bound`): §4 G3. |
| **context at the start** (`\b`, `^`) | The forward body reads it. | The reverse machine's views at the floor, as the RECOVER pass reads them (`rx_reverse_accepts_class`, an emitted name). |
| **budgets / give-ups** | `[r-cursor]` The two back-steps charged once per evaluation, then 1 per candidate step (§5.5). Frames are visible to D42's bound. | Fewer body runs, so fewer give-ups: a ONE-WAY give-up change, which [GIVEUP-DIFF] must cover before the row ships. |
| **machine size per site** (proxy, `revdfa_sizes.tsv`) | None. | Bench body `\bnot\s{1,3}(?:\w{1,12}\s{1,3}){0,3}`: ~61 states × 6 classes. `(?:a\|bc)`: 3 × 4. `a{1,255}`: ~257 × 3. `é{1,255}`: ~511 × 3 (byte). |
| **compile cost** | None beyond today. | One optional subset construction per variable branch, under its own state cap with the subset budget restored (`revend_build_one`'s shape, src/core/compile.c). |
| **host in a VM artifact** | VM record kinds that exist today: `VK_BRANCH`, `VK_PUSH`, `VK_SEEK`, `VK_SET` (TRAILED: `LO_i` must be restored by a pop), `VK_LSET` (the far count `K_i`, untrailed, dead before the first push), `VK_WORK`. `[r3 F13]`: rev 0 used `VK_LSET` for the LOOP slot, which is wrong. `[r-cursor]` Two new sub-kind members, one `VmSeek` and one `VmLocalKind`, and no new kind (§5.6). | No record kind runs an automaton (`VmKind`, src/gen/vm_stmt.h); see §4 G5. |
| **speed, short bodies** (every population row but the `1..255` cap pin: widths ≤ 3, four rows with minimum 0) `[r3 F14]` | ≤ 3 tiny body runs. | A walk of ≤ 3 bytes plus one run, plus tables. No expected win (INFERRED). |
| **speed, the bench pattern** (negative, 4..51) | Up to 48 candidates per evaluation, but each fails at the body's first byte unless it is `n`. | One walk of ≤ 51 bytes. INFERRED small difference, since the lookbehind is evaluated only where `\bavailable\b` can follow. |
| **stream ratchet** | Adds no parallel mechanism. | If built now, a reverse walk inside the VM body would be a new hand-written walk beside R03/R10 (roadmap §5). D185's ratchet rejects it unless it IS the reverse `AUTO` kind. |

**What the table shows.** D needs B's finisher on every body it cannot answer alone: captures,
atomic parts, nested lookaround and backreferences. Callouts are not on this list, since pcrec
refuses them here `[r3 F14]`. D's finisher is exactly B's per-candidate step: back-step to a
position, run forward, end-check. So B is not a parallel path to D. It is D's second half plus the
trivial candidate source. D's own contribution is the candidate filter (fewer body runs) and, on
exact side-effect-free bodies, an existence answer with no VM run.

## 4. Is D a second client of the landmark walk?

**Not of the walk as it stands. Yes of its parts. And its true home is the reverse `AUTO` kind.**

**The family** `[r3 F16]`.
- The candidate-source row is a LOCATE × FINISH instance (D156, `docs/design/locate_finish.md`):
  - `range` is the trivial LOCATE: every position in a window of `[lo, hi]` characters before the
    cursor.
  - `reverse-dfa` is a reverse LOCATE.
  - §5.1's back-step + forward body + end-check is an anchored FINISH with a REQUIRED end.
- The per-branch width range `[lo_i, hi_i]` is the RANGED sibling of the landmark walk's fixed
  K-back distance. A one-length range IS a K-back: roadmap P-d asks "whether FIND takes the landmark
  and K-back position as operands".
- So D's later home is a row in an existing family, with D156's vocabulary (finisher route, give-up
  posture through [GIVEUP-DIFF]), not a new mechanism.
- The general EXISTENCE form is [ENG-LOOK]'s forward `Σ*·L` machine. It is a third candidate-source
  or filter row (§5.4).

**The walk today (D184).**
- `emit_landmark_walk` (src/gen/emit_dfa.c) is the body of the LOCATE row `landmark-walk`. It is
  registered for the DFA route only (`.u.locate.emit = { [CAND_ROUTE_DFA] = emit_landmark_walk }`)
  and emitted into the DFA artifact's search entry.
- Its machine is a Job singleton: `Job.lmnfa`/`Job.lmdfa`, built once by `lmwalk_build` in
  src/core/compile.c from the cut `PcrecLmwalk.pl` that `lmwalk_conj[]` chose (src/gen/lmwalk.c).
- Its admission is about landmark soundness (`exclusion`: P never consumes a byte of L), which has
  no meaning for a lookbehind.
- Its finisher is the anchored DFA `Job.adfa` (`dfa_dir_lmverify`), not a VM.

So D cannot call the walk. What D shares is what the walk is MADE of:

| part | where | reusable by D as is? |
|---|---|---|
| reverse NFA of an AST subtree | `pcrec_build_nfa(cx, ast, nfa, true, ...)` (src/ir/nfa.c), used by `lmwalk_build` on the cut | Yes: the lookbehind branch is a subtree. |
| optional machine build with its own cap, budget restored | `revend_build_one` (src/core/compile.c) | Yes. It is static today; this would be one more call site. |
| exactness as a recorded fact | `Nfa.erased` (internal.h, `NFA_ERASED_*`) | Yes: it is D's "answer vs filter" fact. |
| the reverse scan renderer | `emit_reverse_block` → `emit_scan_loop` over a `DfaForm` (src/gen/emit_dfa.c). Its callers are RECOVER's pass, the rev-end walk and the landmark walk. | Yes in kind, but needs G2-G4 below. |
| the walk's direction strings | `struct DfaDir` (`statev`, `posv`, `recv`, `at_bound`, `seed_cond`, ...), one `static const` per direction (`dfa_dir_landmark`) | Needs G3. |
| the farthest-accept output | `match_start_position` = the smallest accepting position | Yes: it is the longest step-back. |

**What would have to be generalized.** Each item is already named somewhere; none is built.

- **G1 machine per site.** `Job.lmdfa` is one machine per artifact. D needs one machine (or one
  tagged machine) per variable lookbehind branch, keyed by the `A_LOOK` node. Roadmap A-REV's "one
  reverse `AUTO` kind" is where this becomes an operand rather than a Job field.
- **G2 floor and seed as operands.** The landmark walk floors at `search_from` and seeds one past a
  hit. A lookbehind floors at 0 (S135's lesson: never `startpos`) and seeds at the VM cursor.
  `DfaDir.at_bound` and the caller's seed already carry both as strings; they become operands.
- **G3 names per instance.** `DfaDir`s are file-scope constants, and `emit_reverse_block`'s comment
  says "the names stay RECOVER's spellings: the one caller that would need others (rev-inner, D151)
  is filed". Two lookbehinds in one artifact need two name sets.
- **G4 the exits.** Today there is one: the farthest accept. D needs three:
  - farthest (atomic);
  - every accept, farthest first ([LANDWALK-ALLACC]);
  - existence (exact negative or capture-free bodies), which may stop at the first accept.

  These are three of the manifesto's declared automaton exits (manifesto §2: "commit to one end,
  enumerate ends in preference order, act as a gate, test existence, or report a tagged end").
- **G5 hosting in a VM body.**
  - The VM body is written only by typed records (D182).
  - There is an in-body precedent for a REVERSE CURSOR between choice points `[r3 F15]`: R03's
    backward walk renders through `VK_CONSUME_BACK` (src/gen/vm_stmt.h), emitted by `vm_revdet_rep`
    over `revdet.c`'s reversed AST. So a backward cursor written by records is not new.
  - What is new is an AUTOMATON (table-driven) step there, and `VmKind` has no automaton kind.
  - The precedent for DFA TEXT in a VM artifact is the hybrid prefilter (`pcrec_emit_dfa_engine`
    emitted with `static` storage as a separate part, called from the search loop; src/gen/emit_vm.c's
    entry shape `.hybrid`). It is outside the matcher body.
  - D sits INSIDE the body, between choice points. So it needs either a record kind (the reverse
    `AUTO` kind generalizing R03's in-body walk) or a per-site static helper part called from an
    expression record. Either is a new crossing between the VM body and DFA text. That is exactly
    the question of roadmap A-REV and [LANDWALK-VM] (the walk with a VM finisher, "the VM hat").
- **G6 the finisher on the VM route.** The walk's finisher is the anchored DFA. D's is the VM body
  with the end-check, which is B's per-candidate step. B builds it.

**Why not now.**
- Building G1-G5 for this one row, ahead of roadmap A-REV's P-d step, would add a third hand-written
  reverse walk beside R03 (`revdet.c`) and R10 (`emit_landmark_walk`). P-d is the landmark walk as
  records, with prerequisites P-b and [VMREC] (b). D185's ratchet rejects such a walk.
- There is no measured need (§3's speed rows, D77).
- Built after A-REV, D is the reverse `AUTO` kind's first VM-hosted client, with
  [LANDWALK-ALLACC]'s enumerate exit, and it costs one choice row.
- R03 already shows the record shape for a backward cursor. That is consistent with the owner's
  "no reverse VM": R03 is a restricted reverse walk over a mirrored AST, not a reverse VM
  `[r3 F15]`.

## 5. The mechanism

### 5.1 One branch, candidate starts farthest first `[r3 F1: re-sketched]` `[r-cursor: re-spelled]`

Per top-level branch `i`, with character range `[lo_i, hi_i]` from `pcrec_cwmin`/`pcrec_cwmax` (an
EXACT range, §5.2), in written order. `POS` is the lookbehind's position slot, which the entry
records (today's `pslot`). `L_b(m)` for the last branch means `rx_fail`. `[r-cursor]` The loop owns
two values per `range` branch:
- `LO_i`, the NEAREST candidate start (`lo_i` characters back). It is a matcher slot written by
  `VK_SET`, so it is TRAILED, and it is written ONCE per evaluation (§5.1b: the slot family).
- `K_i`, the far step's character count. It is an untrailed matcher local written by `VK_LSET`. It
  is read only before the loop's first push, so no frame ever needs it restored.

The candidate start itself is not stored anywhere but `scan_position` and the retry frame's own
position field. That is the cursor rung's discipline (`vm_cursor_rep`'s header: "the cursor is a
plain local; the resume frame's own `pos` field is its save point ... written once per loop ENTRY,
so the mechanism designed to avoid per-iteration trail entries does not quietly reintroduce one").
`[r-cursor: PREMISE, read]` That rung's frame saves the span cursor (`VPOS_SPAN`). Its retreat
re-seeds from the popped position and steps one stride. Its one trailed slot, the low-water mark,
is written once per entry, and the reach test reads it after every retreat. The lookbehind loop is
the same three parts, mirrored: the frame saves the candidate start, a retry steps one character
nearer, and the trailed `LO_i` is the bound the step tests against.

**How it composes with `vm_look` `[r6 V13]`.** The branch chain sits inside today's `vm_look`
wiring, unchanged (src/gen/emit_vm.c):
- the assertion's mark and `POS` writes come first;
- the negative form's `L_neg_ok` frame is pushed below every `L_adv_i` frame;
- `L_ok` is today's success label, where the atomic and negative forms cut to the mark;
- the last branch's exhaustion is `rx_fail`, which on the negative form pops `L_neg_ok`.

The literal interpreter of review r6 imported exactly this wiring and got 0 differences.

```
L_b_i:    if (scan_position < lo_i) goto L_b_(i+1)       // guard; not emitted when lo_i == 0
          RX_CHARGE_WORK(lo_i)                            // not emitted when lo_i == 0
          scan_position = $_back_step(subject, subject_length, scan_position, lo_i)
                                                          // VSK_BACKSTEP, the literal lo_i
          if (scan_position == $_BACK_STEP_NONE) goto L_n_i
                                                          // fewer than lo_i characters precede
                                                          //   (UTF-8 only; dead under byte)
          RX_SET(LO_i, scan_position)                     // VK_SET: the NEAREST start, trailed,
                                                          //   once per evaluation
          K_i = min(hi_i - lo_i, scan_position)           // VK_LSET: exact (byte), an upper
                                                          //   bound (UTF-8)
L_far_i:  RX_CHARGE_WORK(K_i)
          scan_position = $_back_step(subject, subject_length, scan_position, K_i)
                                                          // VSK_BACKSTEP, count from the local
          if (scan_position != $_BACK_STEP_NONE) goto L_try_i
          scan_position = (size_t)slot_values[LO_i]       // VSK_RESTORE    } the far retry:
          K_i = K_i - 1                                   // VK_LSET        } UTF-8 only, dead
          goto L_far_i                                    //                } under byte
L_try_i:  RX_PUSH(&&L_adv_i, scan_position)               // the retry frame saves the CANDIDATE
          goto L_body_i
L_body_i: <B_i forward, vm_emit unchanged>  -> L_end_i
L_end_i:  if (scan_position != (size_t)slot_values[POS]) goto rx_fail
                                                          // decline: backtracks into B_i, then
                                                          //   L_adv_i
          goto L_ok
L_adv_i:  // reached ONLY by popping L_try_i's frame: scan_position = that candidate's start
          if (scan_position == (size_t)slot_values[LO_i]) goto L_n_i
                                                          // the nearest start was tried: exhausted
          scan_position = $_fwd_step(subject, (size_t)slot_values[POS], scan_position)
                                                          // VSK_STEP_CHAR [r2-1106 F1]: the seam
                                                          //   entry, one character nearer, never
                                                          //   past the cursor (byte: `pos + 1`)
          RX_CHARGE_WORK(1)
          goto L_try_i
L_n_i:    scan_position = (size_t)slot_values[POS]        // VSK_RESTORE: back to the cursor
          goto L_b_(i+1)                                  // the LAST branch: `goto rx_fail` alone
```

**Properties of the sketch** `[r-cursor]`:
- **Same candidates, same order, same body runs, same end-check as rev 2.** The candidates are
  `$_back_step(POS, d)` for `d` from the farthest reachable down to `lo_i`, farthest first. Rev 2
  stepped `d` characters back from the cursor once per candidate. This loop steps back once and
  then forward. §5.1a shows the two sequences are equal on every input. Each candidate runs `B_i`
  from the same start and state, so the answers are rev 2's.
- **Every way out of branch `i` leaves `scan_position` at the cursor**, as rev 2 required. The guard
  moves nothing. The two exits through `L_n_i` (`LO_i`'s sentinel, exhaustion) restore it from
  `POS`, which is trailed and holds this evaluation's cursor (the next bullet). So `L_b_(i+1)` needs
  no re-read. Rev 2 kept this invariant through the frame. This loop keeps it with one restore,
  which is not emitted on the last branch: there `rx_fail` pops a frame that restores its own
  position.
- **Trail.** `LO_i` is written once, BEFORE the first push. So every frame of the loop has its trail
  mark above `LO_i`'s entry. A pop inside the evaluation never rewinds `LO_i`, and a pop below the
  assertion (an outer backtrack) restores the older evaluation's value. That is the cursor rung's
  reason for trailing its low-water mark. `[r2-1106 F2]` The trail is NECESSARY, not a discipline
  kept for its own sake. An older evaluation's `L_adv_i` frame can stay live (a non-atomic form)
  while a NEWER evaluation of the same site runs at an EARLIER cursor: backtracking into a
  non-atomic lookahead's `.*` re-evaluates the lookbehind nearer the subject start. Untrailed, that
  evaluation's `LO_i` survives the pops back to the older frame, whose candidates are then past
  the stale bound: the exhaustion test never fires and the step runs past the cursor. W-low's cell
  (§7) is exactly this. The body's own writes sit above the frame's mark and are
  rewound at each pop. So the loop adds ONE live entry per `range` branch tried, whatever
  `hi_i − lo_i` is. An exhausted branch's entry stays live while the next branch runs. §5.5 sizes
  this.
- **`K_i` is untrailed, safely.** It is written and read only between `L_b_i` and the first push,
  which is straight-line code with no choice point or call. No pop ever lands where `K_i` is read,
  so no frame needs it.
- **Atomic forms** cut every frame at `L_ok` (`vm_cut`, unchanged).
- **Non-atomic forms** leave `L_adv_i`'s frame live, which IS PCRE2's measured retry-shorter
  behaviour. A pop from the follow lands at `L_adv_i` with that candidate's start, and with `LO_i`
  and `POS` as this evaluation wrote them.
- **The last branch** sends its exhaustion to `rx_fail`, as today.

**The UTF-8 far step `[r3 F13]` `[r-cursor]`.**
- `K_i`'s first value is `min(hi_i − lo_i, LO_i)`. That is exact under the byte encoding (so the
  first far step never returns the sentinel, and the retry is dead code, as today's sentinel is). It
  is an upper bound under UTF-8, because a character is at least one byte. Rev 2 clamped with
  `min(hi_i, cursor)`. Counting from `LO_i` saves `lo_i` steps per try.
- Where the far step returns `$_BACK_STEP_NONE`, the count drops by one and the step is retried
  from `LO_i`. This is rev 2's sentinel retry, run before the first candidate instead of as
  candidates. It terminates: `$_back_step(·, 0)` never returns the sentinel.
- The back-steps go through the EXISTING seam entry. Its C signature already takes `size_t k` in
  both encodings. So:
  - no new BACK-step entry is introduced;
  - the [M5-SEAM] per-site count is TWO back-step calls per `range` branch (the `lo_i` step and the
    far step), one per `one-length` branch as today (§7 S133/S134);
  - `[r2-1106 F1]` the one-character FORWARD step is a new entry, `$_fwd_step` (§5.6), one call
    per `range` branch. Rev 3 spliced the existing `advance` text (enc.h, K49) instead; that
    splice is withdrawn. Like `$_back_step` in [M6.6.2] wave D, the new entry is one enumerator
    and one row per backend: no field of `PcrecEncEntry`, no signature of the seam's functions and
    no line of the third-encoding recipe changes.
- Rev 0 left two spellings open: a loop of one-character steps, or a new `back_step_upto` entry.
  Rev 1 retired both. Rev 3 keeps them retired. `back_step_upto` would replace the far retry with one
  call, and it is filed as a measured-trigger candidate in §5.5. A new entry would need a measured
  reason (D77), plus the D58 contract change in the same commit. (`$_fwd_step` is not that entry: it
  replaces no loop and changes no contract; it is the step's home, ruled for the reasons of §5.6.)

**What rev 3 removed from rev 2's sketch** (it is in git at main `7feb7d641`, §5.1): the `D_i` slot
and its two write sites, the per-candidate back-step with its count rendered from a slot (V3), the
per-candidate `RX_CHARGE_WORK(D_i)`, and the sentinel's per-candidate pop. What it added: `LO_i`,
`K_i`, the far retry, `L_adv_i`'s exhaustion test against `LO_i`, the one-character step and
`L_n_i`'s restore. Rev 4 changes the step's SPELLING only (a call of `$_fwd_step` for the spliced
`advance` text); its result is the same position on every input (§5.1a).

### 5.1a Totality: is the cursor shape sound for every body? `[r-cursor]` (new)

The owner's rule asks whether the shape is ALWAYS sound, else for a declared table. The answer is
always. The argument has three parts: the candidates, the state at each candidate, and the exits.

**1. The candidates are positions, and both loops produce the same list.** A lookbehind candidate
is a start position whose character distance to the cursor is in `[lo_i, hi_i]`. It is not an
iteration count of anything in the body. So nothing about the BODY can make the list depend on the
loop shape. What can is the encoding. The claim, with `back_step` and `advance` the emitted text:

> On every subject (any bytes), every cursor `POS` and every `lo < hi`: the list
> `[back_step(POS, d) for d = min(hi, POS) .. lo, skipping NONE]` (rev 2) equals the list the
> cursor loop tries: `far`, then `advance` bounded at `POS`, repeatedly, ending at `LO`.

Why it holds:
- `back_step`'s sentinel is MONOTONE in its count. A walk of `k + 1` characters repeats the first
  `k` steps, so if `k` fails, every longer count fails too. So rev 2's list is a contiguous range of
  `d` values, from `d*` (the largest that succeeds, capped at `hi`) down to `lo`, and the far retry
  finds exactly `d*`.
- If `back_step(POS, d*)` returns `q`, then `s[q .. POS)` is exactly `d*` length-consistent runs
  (the entry's own invariant, enc_utf8.c's entry-4 block). Each run is a non-continuation lead
  byte followed by its declared continuation bytes. So from a run's lead, "one byte, then skip
  continuation bytes, but never past `POS`" lands on the next run's lead, or on `POS`. That is the
  next candidate in rev 2's list.
- The bound matters only at the LAST run. A stray continuation byte AT the cursor
  (`é` + `0xA9`, with the lookbehind evaluated after `é`) is skipped by an advance bounded at the
  subject length. The step then jumps past `POS`, never equals `LO`, and runs away. Bounded at
  `POS`, it stops on `LO`. This is W13.
- MEASURED: `vlbrev3_evidence/candidates.py`, 8,583,480 cells, 0 differences. It uses literal ports
  of `$_back_step` (enc_utf8.c, entry 4) and `advance_utf8`, over every subject of an 8-byte
  alphabet (ASCII `a`, the 2/3/4-byte leads `C3`/`E2`/`F0`, the continuations `A9`/`82`/`9F`, and
  `FF`) up to length 5, and of a 5-byte alphabet at lengths 6-7, × every cursor × nine ranges with
  `lo` 0..2 and `hi` up to 4. The control: the three wrong spellings each differ (unbounded
  advance 288,168 cells; sentinel mapped to the subject start 3,398,699; sentinel mapped to the
  nearest start 591,194). So the check can fail. The NONE-monotone premise: 0 violations.
- `[r2-1106 F1]` The check still covers rev 4's spelling. The utf8 `$_fwd_step` body is
  `next_pos`'s body with the bound as its length (`i = pos + 1; while (i < bound && (s[i] & 0xC0)
  == 0x80) i++; return i;`), and the ported `advance_utf8` with `@N` = `POS` computes the same
  position statement for statement (`@P++`, then the same bounded skip). The byte body is
  `pos + 1`, as the byte `advance` was.
- Under the byte encoding, `back_step(p, k) = p − k` and the advance is `p + 1`, so the claim is
  arithmetic. The byte-mode model's `cursor` evaluator differs from libpcre2 on 0 of 54,579 cells
  of vlbpieces' two sweeps (`sweep_cursor_summary.txt`; the `range` control also 0).
  `[r2-1106 F8]` Rev 3 said the evaluator "runs the sketch's statements in order". It runs the
  CANDIDATE SEQUENCE only: no frames, trail, `POS`/`LO` slots, `L_n_i` restore or charges, byte mode
  only (`model.py` `cursor_branch`). So it validates which candidates are tried, in which order, and
  cannot move under W11-W15 or W-low. The stronger evidence for the statements themselves is the
  review's literal interpreter of §5.1 (frames, trail, `POS`, the ported `$_back_step`, the bounded
  step): equal to libpcre2 on rev 3's 52 cells, 33,000 byte and 15,000 UTF-8 fuzz cells, and about
  12,800 ill-formed ones (review r2 `sound.md`).

**2. The state at each candidate is the same.** At `L_try_i`, before candidate `p`, both loops have
`scan_position = p` and the same groups, marks and slots below the frame's trail mark. A body run
that fails is undone by the pop: the trail rewinds to the mark, and the frame restores `p`. The
loops differ only in what they keep below the mark: rev 2 keeps `D_i`, this loop keeps `LO_i`. Each
is read only by its own loop's exhaustion test. The body never reads either. So each candidate's
body run starts from identical state, and its outcome (match, groups, end position) is identical.
This holds for every body `vm_emit` produces, because it rests only on the engine's frame
discipline (a pop restores its position and rewinds the trail to its mark). It does not rest on what
the body contains. Checked against each body class the design admits:
- **alternation, nested quantifiers, possessive and atomic parts**: their frames and cuts sit above
  the loop's frame (an atomic group's mark is taken after the push), so they never cut it;
- **nested lookarounds, including a nested `range` lookbehind**: its own `POS`, `LO` and `K` are its
  own slots and local, written inside the body and rewound with it;
- **`\b`, `^`, `\A`, `(?m)^`, `\G`**: they read the subject or `startpos` at a candidate start, which
  is the same position in both loops. `\G` (review r5 F1) and `^`/`\A` (r5 F2) are reverse-MACHINE
  hazards. They do not arise here, since no machine runs (cells: `(?<=\Ga{1,2})b` from 0/1/2,
  `(?<=^a{0,2})x`, `(?<=\Aa{0,2})x`, measured against libpcre2 directly). `[r2-1106 F8]` Rev 3 said
  "all equal to libpcre2" of the model too; it is not: the model cannot express `\G` (n/a) and
  answers `(?<=\Aa{0,2})x` on `aax` nomatch where libpcre2 answers [2-3]
  (`cells_byte_model.out`). The review's literal interpreter equals libpcre2 on all of them;
- **`\K`**: refused in a lookaround by both libraries (err 199). Unchanged;
- **stage-2 backreferences**: a reference inside the body is a forward compare from the candidate
  start, exactly as in rev 2. Its group's width only feeds `lo_i`/`hi_i` (§6 stage 2). If a later
  stage ever needs a width known only at run time, both counts here are already run-time operands
  of the existing entry. So the cursor shape takes it with no new mechanism;
- **caseless and multi-width characters**: candidates count SUBJECT characters, whatever the pattern
  folds. The Kelvin sign (3 bytes) is one step (cell `(?i)(?<=(k{1,2})|(b))x` on `b` + U+212A + `x`:
  libpcre2 [4-5,1-4]).

**3. The exits are the same.** Exhaustion goes to the next branch at the cursor (restored from
`POS`), the last branch's to `rx_fail`, and success to `L_ok`. These are rev 2's targets with rev 2's
cursor. The non-atomic re-entry pops into `L_adv_i` with the popped candidate and continues from it.

**The limits.** The 255 cap bounds every `range` branch's `hi` at stage 1. The 65535 ceiling then
bites only on `one-length` branches, which this loop never runs (ruling A). Neither limit enters the
loop's storage: one `LO_i` and one `K_i` per branch whatever `hi` is. The work does grow with `hi`
(§5.5).

**One corner the shape does not improve, stated.** The far retry runs where fewer than
`hi − lo` characters precede `LO_i`, or a run the back-step rejects lies within reach (UTF-8 only).
Let `e` be the number of characters the far step can take (`d* − lo`) and `K_0 ≤ hi − lo` the
first count. Then the retries take `K_0 − e` failing walks of about `e + 1` steps each, and they
are charged `Σ K` from `K_0` down to `e`, at most `(hi − lo)(hi − lo + 1)/2` units. Rev 2 paid the
same retries, inside its candidate loop. At the 255 cap that is at most about 16,000 steps
(32,640 charged) per evaluation, and only within `hi` characters of the subject start or of an
ill-formed run. §5.5 files the one-call alternative with its trigger.

**What the totality does NOT cover:** answers. It shows the cursor shape answers as rev 2's loop
does. That rev 2's loop answers as libpcre2 does is gate 1's job, which stage 1's build runs. The
cells of §7 are measured against libpcre2 directly.

**STOP RULE:** not triggered. No class needs the counter shape, so no detectable-class table is
proposed (owner ruling's second arm). For the record, if one had: lookbehind's rows would have been
a member of [DEC-RUNG]'s "fact-selected emission with a total fallback" family (review r6 V17). §5.1b's
two-row table already is that member.

### 5.1b The emission table: one-length or range, selected by the width fact `[r3 F12]`

**Rev 0's claim, refuted.** Rev 0 said: "the fold for `lo_i == hi_i` is natural ... the emitter
evaluates that test at compile time". The review showed that today's bytes differ from the loop at
`lo == hi` in several ways (SOUND-2):
- statement order;
- the pushed position;
- the work amount;
- the sentinel;
- a new slot family.

It also showed that "fixed width %d" is an `--emit-ir` LISTING label. `[r6 V5]` corrects that: the
same role string is ALSO emitted as a C comment under `-fcomments` (`vm_lbl` writes both in one
call), so it is emitted C in a commented artifact and a listing label always.

The rev 1 sketch closed the order and position differences: at `lo == hi` it had today's order and
pushed at the cursor. (`[r2-1106 F9]` HISTORY: that was rev 1's sketch. Rev 3's cursor shape pushes
at the CANDIDATE, after the back-step; rewrite 3 of the `[r-cursor]` list below is what reconciles
it with today's order.) Even so, today's bytes follow from the loop only after four rewrites that the
emitter does NOT perform in general:
1. `D_i` becomes the constant `k`. The guard makes `min(k, scan_position) = k`.
2. `L_adv_i`, whose test is then always true, is threaded to its target `L_b_(i+1)`.
3. A frame whose continuation is only `rx_fail` (the last branch's) is elided.
4. The slot is dropped.

`[r-cursor]` Those four rewrites were the counter shape's. The cursor shape at `lo = hi = k` reduces
to today's bytes by these instead:
1. `K_i = min(0, LO_i) = 0`, so the far step is the identity and the far retry is unreachable. Both
   are dropped, and so is `K_i`.
2. `LO_i` is the only candidate. `L_adv_i`'s test is then always true, so `L_adv_i` is threaded to
   `L_n_i`, and the `LO_i` slot is dropped.
3. A frame `(L_n_i, candidate)` whose target first restores `POS` is the same frame as today's
   `(L_b_(i+1), cursor)` pushed before the back-step. (The order of push and back-step changes, not
   the state at any pop.)
4. A frame whose continuation is only `rx_fail` (the last branch's) is elided.

And two differences that are NOT rewrites `[r6 V2]`:
5. **The negative arm's failed end-check.** `one-length` returns `RX_R_INTERNAL`; `range` declines.
   This preserves answers only on the premise that a one-length end-check cannot fail on a correct
   compiler. S136's re-aim is exactly where the two spellings give different answers. So it is a
   SELECTION by the same fact, the table's "end-check fail, negative arm" column (§5.3), not a
   rewrite.
6. **Labels.** After rewrite 2, `L_try_i` has no referrer, but the renderer emits every label it is
   given (`rx_Ln: __attribute__((unused));`). The table's label column covers this: `L_try_i` and
   `L_adv_i` are allocated ONLY for `range` branches. `vm_look_behind` allocates `bl`/`bodl`/`endl`
   per branch in one loop. If the two new labels were allocated in that loop for every branch,
   every later label in an all-fixed artifact would renumber, and G2 would move under answer (A).

So the emitter SELECTS the one-length bytes by the width fact. Stated honestly, this is a DECLARED
emission row chosen by a fact that is already stored (`u.look.widths`, a pair per branch from
stage 1). It is not a constant fold, and not a hidden `if`. The table, in two parts. The first part
is what the branch executes:

| row (first match) | applies when | guard | retry frame (target, position) | work per candidate | back-step count | end-check fail, negative arm | `L_adv_i` block |
|---|---|---|---|---|---|---|---|
| `one-length` | `lo_i == hi_i` (= k) | `scan_position < k` (not emitted when k = 0) | `L_b_(i+1)` at the cursor, not pushed on the last branch | `k` (one candidate), today's `RX_CHARGE_WORK(k)` | the literal `k` | `RX_R_INTERNAL` (§5.3) | none |
| `range` `[r-cursor]` | `lo_i < hi_i` | `scan_position < lo_i` (not emitted when lo_i = 0) | `L_adv_i` at the CANDIDATE, pushed per candidate on every branch including the last | per evaluation: `lo_i` and `K_i` (each try); then 1 per candidate step | `lo_i` (literal), then `K_i` (the local) | decline (`rx_fail`) | emitted: exhaustion test against `LO_i`, the bounded one-character step |

The second part is what every OTHER reader sees `[r6 V1, V2, V4, V5]`. Each column names the pass
that reads it:

| row | loop slot (count pass, layout) | matcher locals | push sites (count pass `npush`) | trail entries per evaluation (`vm_cost_look`) | labels (`vm_look_behind`) | trail checkpoint (`vm_goto`, K134) | seam sites ([M5-SEAM] per-site count) | role and note texts (`vm_lbl`/`vm_ev`: `-fcomments` C and the listing) |
|---|---|---|---|---|---|---|---|---|
| `one-length` | none | none | 1 if not last, else 0 | 0 (beyond the assertion's own 2, charged once per lookbehind) | `bl`, `bodl`, `endl` (today's) | none | 1 back-step | today's seven texts, unchanged |
| `range` `[r-cursor]` | one `LO_i` slot (the `low` family, RULED (ruling 8), in its lookbehind sub-block `[r2-1106 F4]`; below) | the ONE artifact-wide `<p>_lb_count` (`VL_LB_COUNT`), declared iff the count pass found a `range` branch (`VmFrame.lb_count`, §5.6) `[r2-1106 F3]` | 1 (the `L_try_i` push, last branch included) | 1 (`LO_i`), whatever `hi_i − lo_i` is | today's three plus `L_far_i`, `L_try_i`, `L_adv_i`, `L_n_i` (`L_n_i` not on the last branch) | NOT declared by the row: `vm_goto`'s rule places one on `L_adv_i`'s `goto L_try_i` iff the body writes the trail (below) | 2 back-steps and 1 `fwd_step` `[r2-1106 F1]` | the `range` texts listed below |

The table's properties:
- **Answer-free.** Substituting `lo = hi = k` into the `range` row and applying rewrites 1-4 (the
  `[r-cursor]` list above) gives the `one-length` row's statements. Every rewrite preserves answers. Item 5 is a selection, and
  item 6 is the label column.
- **Not cost-free.** The elided frame changes the frame and step counts by one per evaluation, and
  the `one-length` row is the cheaper side. It is also today's row, so nothing moves for today's
  patterns.
- **Checked against libpcre2, not by construction.** Both rows run §7's shared witnesses and gate 1's
  differential. Gate 2's identity check proves the `one-length` row is today's bytes.
- **One row choice, read by every column `[r6 V4, V17]`.** The key is one predicate on the stored
  pair, "branch `i` of this lookbehind varies" (`lo_i < hi_i`). It follows the
  `vm_look_needs_mark`/`vm_look_needs_pos` precedent, and every pass reads it rather than re-deriving
  it: `vm_count_slots_look`, `vm_cost_look`, `vm_look_behind_branch` and the role texts. This is the
  hazard the rung ladder's header names ("the SAME rung decision read a second time"). Here the
  decision is made once.
- **Work amount `[r-cursor]`.** Each back-step is charged its character count, which is today's
  rule ("the back-step, charged as the compile-time width"): `k` for a one-length branch; `lo_i`
  and each far try's `K_i` for a range branch, once per evaluation. Each one-character step is
  charged 1. §5.5 gives the totals. `RX_CHARGE_WORK` charges only a positive amount, so a zero
  count charges nothing. (Rev 2 charged `D_i` per candidate.)
- **Slot allocation `[r-cursor]`.** Rev 2's ruling V4 (`D_i` in the `SLOT_COUNTER` family) has no
  object any more: there is no counter. `LO_i` is a POSITION, written once per evaluation, which the
  loop's retry tests against and an outer backtrack must restore. That is word for word the `low`
  family's contract (emit_vm.c's layout comment: "what a span loop cannot recover from its own
  resume frame ... written once per loop ENTRY ... O(1) trail per entry"). The choice is
  answer-free, so it was the manager's (§13 Q6). RULED (ruling 8, 2026-11-06): the `low` family.
  - `[r2-1106 F4]` **An arithmetic sub-block, no owner list.** Rev 3 proposed "one owner record per
    `low` index" so the legend could name a lookbehind's slot. That is the parallel list
    `vm_slot_name`'s header forbids ("deliberately not a second table ... a parallel list would be a
    second source of truth"). Instead the family is two sub-blocks, read off the index:
    - indices `0 .. nlow_total − nlblow_total − 1` are span-loop lows, allocated as today
      (`vm_slot_low(v, v->nlow++)`);
    - indices `nlow_total − nlblow_total .. nlow_total − 1` are lookbehind lows, one per `range`
      branch, through a new `vm_slot_lblow(v, j) = vm_slot_low(v, v->nlow_total − v->nlblow_total
      + j)` with `j = v->nlblow++`.
  - The count pass keeps two counters: `vm_count_slots_rep` adds to `v->nlow` (span loops, today)
    and `vm_count_slots_look` adds to a new `v->nlblow` per `range` branch (the table's one
    predicate). The totals step (`vm_plan` `[r3-1106 READY-6]`, where `nlow_total` is saved today) sets
    `nlow_total = nlow + nlblow` and `nlblow_total = nlblow`, and resets both running counters.
    `nlow_total` keeps its meaning (the WHOLE family), so every base above `low` keeps its formula.
    The two SUB-totals must each agree between the count pass and the emitter.
  - `[r3-1106 READY-11]` A `vm_slot_lblow` off-by-one or collision has no answer witness: it is
    caught by the slot legend (`SLOT_LB_LO<j>` names in the artifact) and the emitter's check that
    the count pass's two sub-totals equal the emitter's. Stated, not witnessed.
  - An artifact with no varying branch has `nlblow_total = 0`: its slot legend and numbering are
    unchanged (ruling A).
- **The `low` family's readers, by grep (src/gen/emit_vm.c), and what each needs:**
  - the base chain: `low` sits just above `guard`, so in an artifact WITH a `range` branch every
    family above it shifts by the number of `range` branches (`mark`, `revdet`, the counter, look
    and splice families). New artifacts only;
  - `vm_slot_name` `[r2-1106 F4]`: today names every `low` slot `SLOT_SPAN_LOW<i>`. Its `low` arm
    splits on the sub-block boundary, by the same arithmetic read backwards: below
    `base_low + nlow_total − nlblow_total`, `SLOT_SPAN_LOW<i>` as today; at or above it,
    `SLOT_LB_LO<j>`. It is emitted C, in new artifacts only;
  - the `--emit-ir` `slots` section (`vm_listing_slots`, family `low`): today one call for the whole
    family with one `holds` text ("span-loop low-water / the loop's entry position"). It becomes two
    calls, the span sub-block as today and a second over `nlblow_total` through `vm_slot_lblow`,
    label "lookbehind nearest start", holds "a `range` lookbehind branch's nearest candidate start
    (vlookbehind §5.1)", no "none" note. The family name stays `low`, so `ir_listing.md` §3.2¶2's
    vocabulary does not grow (no hunk). The first call's "none" note ("no cursor rung in this
    program") stays true, since it now counts span lows only;
  - the totals block and `RX_NSLOTS`: `nlow_total` is the whole family, summed as today;
  - `VmSnap`/`vm_w_range` `[r2-1106 F4]`: a region's per-copy ranges are read from the RUNNING
    counters, so the lookbehind sub-block needs its own: `VmSnap` gains `lblow` (`vm_snap` reads
    `v->nlblow`), and `vm_build_region_saves` gains one `vm_w_range` over
    `vm_slot_lblow(before.lblow) .. vm_slot_lblow(after.lblow)`. Without it a callee's `LO_i` would
    fall outside its save set; with it `LO_i` rides there, which is harmless and keeps S153's
    "every family" rule. The call arm's `2·|W|` term reads `W`, so it counts `LO_i` with no further
    change;
  - the listing stamp (`VmStamp.nlow`): counts `LO_i` too. Listing only;
  - one comment widens: the layout comment's `nlow` paragraph, from "cursor low-water marks" to
    "loop bound positions: a span loop's entry, or a `range` lookbehind branch's nearest start".
  - The alternatives, for the ruling: the counter family needs no new reader, because it has no
    listing row and a generic legend. But it holds a position under a counter's name and contract.
    The `lookpos` family (the assertion's own cursor) is a position, but its contract is "the cursor
    at the assertion's entry", one per lookaround, and its readers count it per lookaround
    (`vm_look_needs_pos`).
- **The count pass's push count** becomes: one per non-last `one-length` branch (today's
  `nbranch − 1`) plus one per `range` branch. A varying LAST branch pushes `L_adv`.
- **The trail checkpoint `[r6 V1]` `[r-cursor: now derived, not declared]`.** `vm_goto` places a
  K134 checkpoint on a backward jump iff a trailed write (`SET`, `SNAPSHOT` or `RESTORE`) was
  emitted between the target label and the jump (`vm_jump_closes_trail_cycle`, reading
  `lbl_nset`). The loop's two backward jumps:
  - `L_far_i`'s retry `goto`: its span holds a `VSK_RESTORE` seek and a `VK_LSET`, neither of which
    is a trailed write. So it never gets a checkpoint, and none is needed: that cycle writes no
    trail;
  - `L_adv_i`'s `goto L_try_i`: `LO_i`'s write precedes `L_try_i`, so the loop itself contributes
    none. The span holds the BODY, so a checkpoint appears exactly when the body's emission writes
    the trail. That includes a capture group, a quantifier on the cursor or counter rung (their
    `low`/counter `SET`), an atomic group's mark, a nested lookaround's mark and `POS`, and a
    callee's park. It excludes literals, classes, fixed alternations, anchors and possessified
    span loops.

  So the brief's "K134 helpers on capture-free bodies" is narrower than it sounds. EXACTLY: an
  artifact whose `range` bodies write no trail, and which has no other checkpoint, gets no
  `vm_emit_trail_compact` helpers (`ncheck == 0`). `(?<=(?:ab|c))x` is one: its `range` body is
  an alternation of literals, which pushes frames and writes no slot. A capture-free body with a backtracking quantifier
  (`(?<=a{1,9})x`) still writes its rung's `low` slot and keeps the checkpoint. That checkpoint is
  structurally harmless: the pop before the jump has already rewound the body's writes, so the
  trail does not grow around this cycle, and compaction finds nothing to do. Rev 2's checkpoint on
  EVERY `range` loop (it counted the `D_i` decrement) and the two `D_i` sites it added to the
  margin `nset` are gone. CAVEAT (INFERRED, checked at build): which rung a body quantifier
  inside a lookbehind takes is the ladder's choice, so "this body writes the trail" is read off
  the emitted text, not predicted here.
- **Role and note texts `[r6 V5]`.** These are C comments under `-fcomments` and listing text
  always. Under (B) their moves are inside the abi event. Seven of today's texts in
  `vm_look_behind_branch` are false on a `range` branch, so the `range` row writes its own:
  1. label: "lookbehind branch %d of %d, width %d..%d: candidates farthest first". It never carries
     the suffix "(the LAST branch: no retry frame)", because a `range` last branch pushes `L_adv_i`;
  2. the negative END-CHECK role: the positive role's text on both polarities ("... this candidate
     declines"). The "FALSE MATCH ... returns HARD" text stays `one-length`'s;
  3. the end-check note: "end-check FAILED -- this candidate declines";
  4. the back-step notes `[r-cursor]`: "the ENCODING SEAM's back-step to the NEAREST start, %d
     characters" (`lo_i`), and "... to the FARTHEST start, `K_i` characters (a run-time count)";
  5. the sentinel notes `[r-cursor]`: for `lo_i`'s step, "fewer than %d characters precede: try the
     next branch -- dead under the byte backend, where the guard above is exact"; for the far
     step, "retry one shorter -- dead under the byte backend, where the count `min(hi - lo, LO)` is
     exact";
  6. the work role: "charged as the back-step's count", not "as the compile-time width";
  7. the guard notes: printed with `lo_i`, not `k`.

  New `range` texts `[r-cursor]`: the `LO_i` set, the `K_i` set and decrement, the `L_far_i`,
  `L_try_i`, `L_adv_i` and `L_n_i` labels, the exhaustion test, the one-character step ("one
  CHARACTER nearer, never past the cursor") and the restore. `[r2-1106 F9]` Rev 3 said "the
  160-byte `vm_rolef` limit and its truncation note apply to each": there is no such limit
  (`vm_rolef` is arena-owned, over `pcrec_sb_fragfv`, which measures then allocates). The stale
  comment saying so in `vm_look_behind_branch` (src/gen/emit_vm.c, above its label text) is one of
  the texts the `range` row's text-1 rewrite touches, so it is corrected in the same change.
  - **Gate 3's classification control reads the per-branch judgment through text 1** (the listing
    label, present without `-fcomments`): "fixed width %d" against "width %d..%d". `ir_listing.md`
    §3.4¶1 specifies role text only as "the role text the walk recorded", so this needs no spec
    hunk. The control pins the two phrasings itself, and a rewording is a re-pin of that control.

**The alternative (owner question 1, ANSWERED (A) 2026-11-06 `[r-cursor]`).** One loop shape for
every branch: the `range` row everywhere, plus an abi event. §13 gives both costs. Under Frank's open "VM base" frame
(roadmap.md A-VERDICT, used here as a lens, not a rule), the `range` row is the reference matcher
and `one-length` is an admission row substituting a cheaper section where it is sound. That is
exactly this table's shape.

### 5.1c Hand-execution of §5.1, literally `[r3 F1]` `[r-cursor: re-traced]`

Each cell lists what each pushed frame SAVES and what popping it RESTORES. Subject positions are
byte offsets. The matcher attempt shown is the one that matches. The other attempts fail
elsewhere `[r6 V14]`. In cells 1 and 2 they fail before the lookbehind or at its first guard. In
cell 3, the attempt at 1 runs branch 0, exhausts it, and fails at branch 1's guard. In cell 4, the
attempts at 1 and 2 pass the lookbehind and fail at the follow's `c`, after the non-atomic retries.
(Whether a prefilter skips those starts depends on the artifact.) `[r-cursor]` Trail depths ARE
traced now, because the loop's sizing is one line (§5.5). "Trail n" counts the lookbehind-owned
entries: the atomic positive form writes the mark and `POS` (2), the non-atomic form `POS` only (1,
`vm_cost_look`'s header).

**Cell 1: `(?<=a{1,2}|b)x` on `bx`, libpcre2 [1-2].** Cursor 1, `POS = 1`, trail 2. Branch 0 is
`range` [1,2]; branch 1 (`b`) is `one-length` k=1, last.
1. `L_b_0`: guard `1 < 1` is false. Charge 1. Back-step 1 → 0, not the sentinel. `LO_0 = 0`
   (trail 3). `K_0 = min(2 − 1, 0) = 0`.
2. `L_far_0`: charge 0 (nothing). Back-step 0 → 0, not the sentinel: goto `L_try_0`.
3. `L_try_0`: push F1 = (`L_adv_0`, saves 0; trail mark 3). Body `a{1,2}` at 0 reads `b` and fails:
   `rx_fail` pops F1, restoring position 0 and trail 3.
4. `L_adv_0`: `0 == LO_0`, so goto `L_n_0`: `scan_position = POS = 1`, goto `L_b_1`.
5. `L_b_1` (one-length): guard `1 < 1` is false. Last branch, so no push. Charge 1. Back-step 1 → 0.
6. Body `b` matches → 1. End-check `1 == POS` → `L_ok`. `x` at 1 matches → **[1-2]**, equal to
   libpcre2.

Under rev 0's sketch, branch 1 started at 0 and its guard `0 < 1` failed: nomatch. Under the
cursor shape the same failure is W11(a): drop `L_n_0`'s restore, and branch 1 starts at 0.

**Cell 2: `(?<=a{2,3}|b)x` on `bx`, libpcre2 [1-2].** Cursor 1. Branch 0 is `range` [2,3].
1. `L_b_0`: guard `1 < 2` is true, so goto `L_b_1` with `scan_position = 1`. Nothing was pushed,
   written or moved.
2. Branch 1 runs as in cell 1 → **[1-2]**.

**Cell 3: `(?<=a{1,2}|bc)x` on `bcx`, libpcre2 [2-3].** Cursor 2, trail 2. Branch 0 is `range`
[1,2]; branch 1 (`bc`) is `one-length` k=2, last.
1. `L_b_0`: guard false. Charge 1. Back-step 1 → 1. `LO_0 = 1` (trail 3). `K_0 = min(1, 1) = 1`.
2. `L_far_0`: charge 1. Back-step 1 → 0: goto `L_try_0`.
3. Push F1 = (`L_adv_0`, saves 0; mark 3). Body `a` reads `b` and fails. Pop F1: position 0.
4. `L_adv_0`: `0 ≠ 1`. Step one character → 1. Charge 1. Goto `L_try_0`, with no checkpoint: the
   body `a` writes no trail.
5. Push F2 = (`L_adv_0`, saves 1; mark 3). Body `a` reads `c` and fails. Pop F2: position 1.
6. `L_adv_0`: `1 == LO_0`, so `L_n_0`: `scan_position = 2`, goto `L_b_1`.
7. Guard `2 < 2` is false. No push. Charge 2. Back-step 2 → 0. Body `bc` → 2. End-check `2 == POS`.
   `x` matches → **[2-3]**.

The trail never exceeds 3 plus the body's own entries. Rev 2's loop reached 4 here (`D_0` = 2, 1).

**Cell 4 (non-atomic retry from OUTSIDE, with a gap): `(?<*(a|aaa))c\1` on `aaaca`, libpcre2
[3-5,2-3].** Cursor 3, `POS = 3`, trail 1. One branch, `range` [1,3], last.
1. Guard false. Charge 1. Back-step 1 → 2. `LO = 2` (trail 2). `K = min(2, 2) = 2`. Charge 2.
   Back-step 2 → 0.
2. Push F1 = (`L_adv`, saves 0; mark 2). The body opens g1. Alternative `a` (body frame Fb1 saved
   at 0 for `aaa`) → 1. End-check `1 ≠ 3`: pop Fb1.
3. `aaa` → 3, g1=(0,3). End-check passes. `L_ok` (non-atomic: no cut).
4. The follow: `c` at 3 → 4. `\1` (`aaa`) at 4 runs off the end and fails. Pop F1: position 0,
   trail 2 (g1 rewound; `LO` stays).
5. `L_adv`: `0 ≠ 2`. Step → 1. Charge 1. Checkpoint, because the body wrote g1 (§5.1b). Goto
   `L_try`.
6. Push F2 = (`L_adv`, saves 1). `a` (Fb2 saved at 1) → 2. End-check `2 ≠ 3`: pop Fb2. `aaa` from 1
   reads `c` at 3 and fails. Pop F2: position 1. This is the gap at length 2.
7. `L_adv`: `1 ≠ 2`. Step → 2. Charge 1. Checkpoint. Push F3 = (`L_adv`, saves 2).
8. `a` → 3, g1=(2,3). End-check passes. `L_ok`. `c` → 4. `\1` = `a` at 4 → 5.
9. **[3-5, g1 2-3]**, equal to libpcre2. Peak lookbehind-owned trail: 2 (`POS`, `LO`) under g1's
   pair.

**Cell 5 (W12): `(?<=a{1,9})x` on `bbbbbbbbbax`, libpcre2 [10-11].** The matching attempt is at
10, trail 2.
1. Guard `10 < 1` is false. Charge 1. Back-step 1 → 9. `LO = 9` (trail 3). `K = min(8, 9) = 8`.
   Charge 8. Back-step 8 → 1.
2. For `p` = 1 .. 8: push (`L_adv`, saves p; mark 3). Body `a{1,9}` at `p` reads `b` and fails. Its
   rung's low-water write sits at trail 4 and is rewound by the pop. Pop → p. `p ≠ 9`: step → p+1.
   Charge 1. Checkpoint (the rung's `SET` is in the body). Goto `L_try`.
3. `p` = 9: push. The body reads `a` → 10. End-check passes. `L_ok` cuts. `x` → **[10-11]**.

The peak is 4 entries (mark, `POS`, `LO`, the body rung's low-water). The cost term charges
`2 + 1 + body (1) = 4`, and the capacity is 5 (§5.5). A spelling that writes one trailed value per
candidate (rev 2's `D_i`, or `LO` written at `L_try` instead of before it), sized by the new term,
reaches 2 + 9 entries and gives up with `PCREC_ERR_FRAMES`. That is W12(a).

**Cell 6 (W6, the UTF-8 far retry): `(?<=(é{0,2}))x` on `éx` (UTF-8), libpcre2 [2-3,0-2].** Bytes
`C3 A9 78`. Cursor 2. Range [0,2], one branch, last.
1. No guard and no charge at `lo = 0`. Back-step 0 → 2. `LO = 2`. `K = min(2, 2) = 2`: two bytes,
   but one character.
2. `L_far`: charge 2. Back-step 2: the first character → 0, then `pos == 0` → the sentinel. Restore
   `scan_position = LO = 2`. `K = 1`. Goto `L_far`. Charge 1. Back-step 1 → 0: goto `L_try`.
3. Push (`L_adv`, saves 0). The body opens g1, `é{0,2}` takes `é` → 2 (a second `é` fails at `x`),
   and closes g1 = (0,2). End-check `2 == POS`. `x` → **[2-3, g1 0-2]**.

Sabotaged with the sentinel ending the branch: nomatch. Sabotaged with the sentinel taken as "start
at `LO`": the one candidate is 2, g1 = (2,2), so [2-3,2-2]. Rev 2's W6 cell
(`(?<=(é{1,2}))x` on `éx`) no longer reaches the retry: there `LO = 0` and `K = min(1, 0) = 0`.

**Cell 7 (W13, the step's bound): `é(?<=(a?))` on `C3 A9 A9` (`é` and a stray continuation byte),
`PCRE2_MATCH_INVALID_UTF`, libpcre2 [0-2,2-2].** The attempt at 0 takes `é` → 2. Cursor 2, `POS = 2`.
Range [0,1].
1. `LO = 2`. `K = min(1, 2) = 1`. Charge 1. Back-step 1: back over `A9` to the lead `C3` at 0, which
   declares 2 bytes = the run walked, so → 0.
2. Push (`L_adv`, saves 0). Body `(a?)` at 0: `C3` is not `a`, so zero iterations, g1 = (0,0),
   ending at 0. End-check `0 ≠ 2`: pop → 0.
3. `L_adv`: `0 ≠ 2`. The step: `P = 1`; `s[1]` is a continuation byte and `1 < POS`, so `P = 2`;
   `2 < POS` is false, so stop at 2. Charge 1.
4. Push (`L_adv`, saves 2). Body `(a?)` at 2: `A9` is not `a`, so g1 = (2,2), ending at 2 = `POS`.
   **[0-2, g1 2-2]**.

With the step bounded by the subject length (3) instead, step 3 goes on over `s[2] = A9` to 3. 3 is
never `LO`, every later step adds one, and the loop runs until the work or step budget gives up.

**Cell 8 (W15, the back-step's own clamp): `(?<=(a{0,2}))b` on `FF 61 62`,
`PCRE2_MATCH_INVALID_UTF`, libpcre2 [2-3,1-2].** Cursor 2. `LO = 2`. `K = min(2, 2) = 2`.
Back-step 2: `a` → 1, then the lead `FF` → the sentinel. Retry `K = 1` → 1. Push (`L_adv`, saves
1). `a{0,2}` takes `a` → 2, g1 = (1,2). End-check passes. `b` → **[2-3, g1 1-2]**. Sabotaged with the
sentinel taken as "start at `LO`": g1 = (2,2). Taken as "start at the subject start" (the naive
"clamped at the subject start" reading): candidate 0 fails (no body consumes `FF`), the step lands
on 1, and the answer is the same. That spelling is answer-neutral, but it can cost O(subject) per
evaluation after an ill-formed byte. So it is excluded by the work, not the answer (§5.1a).

### 5.2 The width rule and the two limits `[r3 F4, F2]`

`la_widths` (src/parse/mod_lookaround.c) stores a range per branch (`lo`, `hi`) instead of one
`int`. It refuses exactly what libpcre2 refuses. PCRE2's rule has two tiers, both measured
(premise lens; `vlbrev1_evidence/cells.out`):

1. **The absolute ceiling: 65535 characters per branch, on EVERY lookbehind, fixed or varying.**
   - libpcre2 gives err 187 "lookbehind assertion is too long", at every `max_varlookbehind`
     setting. It is NOT a caller setting in PCRE2.
   - Boundary cells: `(?<=a{65535})x` and `(?<=(?:a{1000}){65})x` ACCEPT (maxlookbehind 65535 /
     65000). `(?<=a{65535}b)x` and `(?<=(?:a{1000}){66})x` REJECT 187.
   - pcrec compiles the refused two today (`la_widths` refuses only unbounded and `> INT_MAX`).
     Stage 1 refuses them: G1's exception to G2 (§0).
   - New `limits.def` row `[r6 V9]`: `LA_LOOKBEHIND_BRANCH_MAX`, 65535 (§5.2a).
2. **The variable cap: 255 characters, on every branch's MAXIMUM once ANY branch of that
   lookbehind varies.**
   - libpcre2 gives err 200 "branch too long in variable-length lookbehind assertion".
   - Examples: `(?<=a{300}|b{1,2})x` REJECT, `(?<=a{300}|b)x` ACCEPT (all branches fixed).
   - How widths count: in characters under UTF and bytes in byte mode; nested quantifiers
     multiply; sums add; a nested lookbehind is capped on its own and never summed into the outer
     branch; a nested lookahead contributes 0.
   - New `limits.def` row `[r6 V9]`: `LA_LOOKBEHIND_VAR_MAX`, 255 (§5.2a). No override until
     [IFACE-PUSH] (owner ruling).

What the rows mean:
- **Both are POLICY, not mechanism (owner's answer, review r3).** Correctness needs no cap, not even
  boundedness. `[r-cursor]` §5.1's candidate start strictly moves toward `LO_i`, which is clamped
  by the subject start (and by the back-step's own validation), and the emission is one body copy
  per branch whatever `hi_i` is.
- So nothing in §5.1's CONTROL depends on `hi_i`'s magnitude:
  - `K_i` is a local as wide as a subject position (`size_t`);
  - nothing is unrolled per length;
  - both back-step counts are operands (`lo_i` literal, `K_i` run-time).
- **Nor does its STORAGE `[r-cursor]`.** The loop writes one trailed entry per `range` branch per
  evaluation, whatever `hi_i − lo_i` is (§5.1, §5.5). So raising the cap at [IFACE-PUSH] is a
  one-row change in ACCEPTANCE and in storage alike. Only the work grows with the cap (§5.5).
  Rev 2's `[r6 V1]` storage paragraph is retired: it sized a counter written once per candidate,
  up to 65,536 entries per branch at a raised cap, above `VM_MAX_AUTO_TRAIL_FRAMES` (3072).
- The 255 cap exists for accept-set EQUALITY with PCRE2's default (G1, gate 3). Under D26's addendum,
  accepting more than PCRE2 would not be a defect, so 255 is a choice. The setting (PCRE2's
  `max_varlookbehind`) waits for [IFACE-PUSH], where raising it is a one-row change.
- In pcrec the run-time work budget, not the cap, bounds the work (§5.5). PCRE2's cost grows with
  the cap: measured O(n·hi²) per scan, 0.22 s at hi=255 and 22.6 s at hi=4000 on a 4000-byte
  subject.
- `lb_max` takes the widest branch maximum (`la_lb_raise`), which is PCRE2's `max_lookbehind`.
- The refusal sentence for bounded bodies is deleted: the special case is retired.

**The range must be EXACT wherever it decides the cap or the emission row `[r3 F2]`.**
- `la_widths`' comment says that `pcrec_cwmin` may UNDER-estimate "for free". That premise is RETIRED
  for this consumer. Under the old fixed-only rule, looseness could only refuse.
- The same premise is the stated CONTRACT of both width functions' headers in src/opt/mrl.c
  `[r6 V12]`: `pcrec_cwmax`'s ("This function may OVER-estimate for free"), which also restates
  `pcrec_cwmin`'s ("`pcrec_cwmin` may under-estimate for free"). Stage 1 corrects both headers and
  `la_widths`' comment, not only stage 2's A_BREF sentence. New text: exact for the lookbehind
  consumer; a loose answer is the wrong emission row and a wrong cap.
- Now an under-estimated `lo` (or an over-estimated `hi`) makes a fixed branch "varying", which
  has two effects:
  - it switches the 255 cap on for EVERY branch of the lookbehind, refusing patterns libpcre2
    accepts;
  - it moves the branch from the `one-length` row to `range`, so G2's bytes move.
- Stage 1's constructs already agree with libpcre2: 57/57 cells (premise lens, pcrec's judgment
  against libpcre2 at `max_varlookbehind = 0`).
- Gate 3 adds that comparison as a permanent control (§6). Stage 2 makes `A_BREF` exact at both
  ends.

**Refusal shapes `[r3 F6]`.** After stage 1, every lookbehind width refusal that remains is one
libpcre2 also makes:
- unbounded (err 125);
- the variable cap (err 200);
- the ceiling (err 187);
- a call that re-enters its own lookbehind, §7.4¶5a (err 125).

So all four are shape 7 of `pattern_language.md` §2.4's refusal-shape table ("PCRE2 refuses it
too"), not shape 5, and none names a raise flag. Shape 7's "means" cell says "the pattern is not
well-formed", which the cap and the ceiling are not: they are length LIMITS (§5.2a). So the §2.4
hunk widens that cell to "not well-formed, or over a PCRE2 length limit; PCRE2 refuses it too"
`[r6 V12]`. Their sentences change to say what is refused, per D26's functional tier:
- unbounded: "every alternative of a lookbehind must have a bounded length (this one is unbounded)";
- the cap: "... at most 255 characters once any alternative's length varies (this one can match
  up to N)";
- the ceiling: "... at most 65535 characters (this one has N)".

The unbounded arm's current text, "variable-length lookbehind is not implemented", becomes false at
stage 1. K127's `recurses` refusal prints the same text and moves with it. The readers of the old
text are listed in §10.

`la_widths`' `hi > INT_MAX` arm ("this lookbehind is too long") becomes unreachable under the 65535
ceiling, which refuses first. It is DELETED `[r6 V9]`, not kept as a dead arm, and `LA_MSG_MAX`'s
length comment in mod_lookaround.c is re-read with it.

### 5.2a The two `limits.def` rows, in the table's schema `[r6 V9]`

The row shape is `PCREC_LIMIT(name, value, unit, kind, override, anchor, desc, home)`
(src/core/limits.def's header):

| name | value | unit | kind | override | anchor | home |
|---|---|---|---|---|---|---|
| `LA_LOOKBEHIND_BRANCH_MAX` | 65535 | `"chars"` | `"compile budget"` | `NONE` | `"3.11"` | `MOD_LOOKAROUND` |
| `LA_LOOKBEHIND_VAR_MAX` | 255 | `"chars"` | `"compile budget"` | `NONE` | `"3.11"` | `MOD_LOOKAROUND` |

- **Name and home.** C symbols beside `LA_MSG_MAX`, in the module file that reads them
  (`la_widths`). The `MOD_LOOKAROUND` home expands each row to a constant there.
- **Unit.** `"chars"` is in the unit vocabulary (`PCREC_UPROP_NAME_MAX` uses it). "Characters under
  UTF, bytes in byte mode" goes in `desc`, since one cell cannot carry the reading.
- **Kind: an existing token, no schema change.** `"compile budget"` reads "crossing it can REFUSE a
  pattern". The precedent is `PCREC_MAX_GROUP_DEPTH`, PCRE2's own nesting ceiling, which carries
  that kind with `NONE`. The `desc` says these are PCRE2's language limits (the ceiling) and policy
  matching PCRE2's default (the cap), not a resource bound. A sixth kind would be a schema change to
  three texts: limits.def's header, the dump's printed header (`src/dump/limits_dump.c`, the public
  `--list-limits`/`pcrec_limits_tsv` self-description), and `limits.md`. Rev 1's "a LANGUAGE limit"
  is withdrawn.
- **Readers that move in the same change:**
  - `tests/registry/limits_check.sh`: its `EXPECT_NAMES` manifest gains the two names, and its
    literal row count 78 becomes 80;
  - the new `limits.md` subsection (§10 of this note) spells each anchored value the way the check
    finds it, comma-grouped:
    "65,535" and "255".

### 5.3 The end-check and the negative arm

The end-check is load-bearing for a varying branch: on a correct compiler, a body may end before
the cursor.
- On the negative arm today, a failed end-check returns `RX_R_INTERNAL` (ASK 2: a decline would be
  a false match).
- For a `range` branch, a failed end-check is an ordinary decline on both polarities.
- For a `one-length` branch it stays the hard return. It cannot fail on a correct compiler, and it
  is part of the byte-identity row.

The predicate is the emission table's own key: "this branch's end-check can fail on a correct
compiler" iff `lo_i < hi_i`. `PCREC_ERR_INTERNAL`'s spec sentence narrows accordingly (§10).

**`PCREC_ERR_INTERNAL` has TWO producers today, not one `[r6 V11]`:**
- this end-check;
- D72's region-exit guard (`if (<p>_call_frame >= run->resume_cap) return <P>_R_INTERNAL;`,
  rendered by src/gen/vm_stmt.c at every subroutine region exit).

`match_api.md` §4¶6's "its one producer" is pre-existing drift, and so is `emit_vm.c`'s comment
naming the end-check as "its one producer today". The §10 hunk repairs it rather than carrying it
forward. Two comments read the end-check's redundancy, and both are scoped to `one-length` in the
same change:
- `src/enc/enc_utf8.c`, the back-step's header ("the end-check's redundancy argument ...
  unconditional and RX_R_INTERNAL unreachable");
- `vm_look_behind`'s header, note 3 ("THE END-CHECK IS PROVABLY REDUNDANT FOR THE SUBSET THIS
  MODULE SHIPS"). The build rewrites it. S136's anchor is in mod_lookaround.c, not here.

### 5.4 The candidate source: a declared choice row (D186; LOCATE rows, D156 `[r3 F16]`)

| order | row | applies when | exit | status |
|---|---|---|---|---|
| 1 | `reverse-dfa` | The branch varies (`lo < hi`); its reverse machine builds under its own cap; no backreference or variable in the body; no side-effecting construct (none reaches a lookbehind today, §3); the host can run it (G5). | Exact machine and no capture: EXISTENCE (no VM run). Otherwise candidates farthest first, each confirmed by §5.1's step. | HELD (not built) |
| 2 | `range` | Always: the total fallback. | §5.1 | stage 1 |

- Fixed branches never take row 1: there is one candidate, so nothing to filter. Row 1's first
  conjunct is a fact, not a special case.
- Exactness is read from `Nfa.erased == 0`, the existing fact.

**The general existence form `[r3 F16]` (HELD, plan row [LB-EXIST]).**
- [ENG-LOOK]'s forward machine answers `(?<=L)` at `p` iff `subject[..p] ∈ Σ*·L`, unbounded `L`
  included. As a filter row in front of `range`'s finisher (`forward-existence`) over the superset
  machine, it is sound for both polarities: no accept means the positive fails and the negative
  holds, with no candidate run.
- On exact capture-free bodies it is the answer.
- Its cost model differs from row 1's. It does not depend on the width, but it pays one forward pass
  whether or not the lookbehind is reached. So it loses on early-match calls and wins on scans that
  evaluate the lookbehind at many positions.
- **Unlocks**, each with its trigger:
  - (a) unbounded lookbehind, linear per scan for exact bodies and filtered for the rest. Trigger: a
    real pattern needing `(?<=X+)` or a width over 255, from the [UTF-RW] harvest or a user.
  - (b) one machine per body shared with [ENG-LOOK]'s DFA-engine product construction. Trigger:
    that row opens.
- Unbounded semantics are the bounded semantics continued: `(?<=a+)` on n characters is
  `(?<=a{1,n})`. So libpcre2 at `max_varlookbehind = 65535` on the bounded twin is its oracle.
- Not proposed for any stage here (D77).

**Evidence requirement for row 1 (the D186 choice bar).** Per regime, `reverse-dfa` versus `range`
must be answer-identical, with no regime slower beyond noise:
- (a) short bodies: every population row but the `1..255` cap pin `[r3 F14]`, hit and miss;
- (b) the bench pattern `negation-scope-lookbehind-var` on the bench's own subjects;
- (c) a wide body whose candidates do NOT fail at the first byte (e.g. `(?<=\w{1,64}x)y`);
- (d) a random-like subject regime (D186 addendum 2's condition).

A losing regime narrows the row's condition (e.g. a minimum width), never adds a parallel path. If
the row can be slower anywhere, it also gets a public deny flag (the flag follows the caller
effect).

**Prerequisites and trigger.**
- Prerequisites:
  - roadmap A-REV's reverse `AUTO` kind, with operands for machine, seed and floor and the three
    exits (§4 G1-G4), hosted in a VM body (G5, [LANDWALK-VM]);
  - [GIVEUP-DIFF], since the row removes work: a one-way give-up change.
- Lookbehind is A-REV's first client (Frank, 2026-11-05).
- Trigger (D77): a measured cell where the lookbehind's candidate tries dominate. For example, the
  bench's `negation-scope-lookbehind-var` slower than libpcre2 with the lookbehind as the cause, or
  any regime (c) cell in a real workload.

**One tagged machine instead of per-branch machines** is a later refinement of row 1: one walk per
evaluation instead of up to m. It would ride [LANDWALK-ALLACC]'s multi-branch form and the
priority-tagged accepts of `alt_dispatch_study.md`. Not designed here.

### 5.5 Budgets and frames `[r3 F12, F14]` `[r-cursor: work and trail re-derived]`

**Work `[r-cursor]`.** Each back-step is charged its count, and each one-character step 1. For a
`one-length` branch that is today's `k` per evaluation, unchanged. For a `range` branch, per
evaluation:
- `lo_i` for the nearest step, then `K_i` per far try, then 1 per step to the next candidate.
- On the common path (at least `hi_i` characters, all well-formed, precede the cursor) there is
  one far try, so the charge is at most `lo + (hi − lo) + (hi − lo) = 2·hi − lo`. `{1,255}`: 509.
  The bench pattern (4..51): 98. Rev 2 charged `(hi + lo)(hi − lo + 1)/2` here: 32,640 and 1,320.
- In the far-retry corner (§5.1a: near the subject start, or just after an ill-formed run, UTF-8
  only), the far tries add at most `(hi − lo)(hi − lo + 1)/2`. That is rev 2's own bound, paid in
  the same place.
- On SMALL ranges the new charge can exceed rev 2's by one unit (`(?<=a{0,1})` charges 2 where
  rev 2 charged 1). MEASURED over the candidate check's cells (`workdiff.out`): 852,406 of
  8,583,480 cells charge more, every one by exactly 1; 3,138,528 charge less, by up to 9 at these
  small widths. The work budget is a give-up bound, not an
  answer. The give-up it sets is the cursor shape's own, and gate 4 measures it.
- The BODY runs are charged by the body, as today. Up to `hi − lo + 1` runs of up to `hi`
  characters each remain the inherent O(hi²) per evaluation, which PCRE2 also pays (measured
  O(n·hi²) per scan, §5.2).
- At the default work budget of 1,000,000,000 (`limits.md` §3.1¶2), the loop's own charge allows
  about 1,960,000 worst-case `{1,255}` evaluations per match call on the common path. The bodies'
  charge, not the loop's, is what gate 4's cell gives up on.
- Gate 4 states the subject size at which a worst-case leading `{1,255}` gives up.
- **Filed as a measured-trigger candidate (D77), not proposed:** a seam entry `back_step_upto`
  ("the farthest position at most `k` characters back"). It would replace the far retry with one
  call of at most `hi − lo` steps. It is a D58 contract change (two backends, the third-encoding
  recipe, the [M5-SEAM] fixture). Trigger: the 255 cap is raised at [IFACE-PUSH] (the corner's
  `(hi − lo)²/2` grows with it), or a measured cell gives up in the corner where libpcre2 answers.
- Rev 2's "alternative" paragraph (a second trailed slot plus a forward step) is retired. The cursor
  shape IS that alternative, minus the slot: the candidate lives in the frame.

**Trail `[r6 V1]`: the term, derived from the code.**
- Today, `vm_cost_look` (src/gen/emit_vm.c) returns the body's cost plus `frames += 1 + nbranch`
  and `trail += 2`. The 2 is the assertion's own two trailed writes, the cut mark and the `POS`
  save. That constant is CONFIRMED on this branch: `(?<=aa)x`, `(?<!aa)x`, `(?<*aa)x` and
  `(?<=a|bc)x` all emit `RX_TRAIL_FRAMES 3` (`vlbrev2_evidence/premise.out`).
- The body's cost is `vm_cost_alt`'s field-wise MAX over the branches.
- `vm_plan_capacities` sizes a bounded pattern's trail at `cost.trail + 1`, clamped at
  `VM_MAX_AUTO_TRAIL_FRAMES` (3072).
- The emitted `RX_TRAIL` returns `RX_R_FRAMES` when `trail_depth >= trail_cap`, BEFORE the write.
  No tier grows a bounded pattern's trail.

**The new term `[r-cursor]`:** `trail += 2 + (the number of range branches)`, read off the stored
width pairs through the table's one predicate (§5.1b). Rev 2's `2 + Σ_range (hi_i − lo_i + 1)`
`[r6 V1]` is retired. The derivation, from every write the loop makes (the r6 lesson: size the
storage from the writes, not from the slot's readers):
1. `LO_i` (`VK_SET`, trailed): written once per evaluation per `range` branch tried, at `L_b_i`,
   before the first push.
2. `K_i` (`VK_LSET`): a local, not the trail. `scan_position`: the cursor, not the trail.
3. The retry frame: one push per candidate, a frame and not a trail entry. Each push takes its trail
   mark ABOVE `LO_i`, and each pop rewinds to it, so the body's writes never accumulate across
   candidates.
4. Branches run in order, and an exhausted branch's `LO_i` stays live. So the lookbehind-owned
   peak, `2 + (range branches tried)`, is bounded by `2 + (number of range branches)`.
5. The body's own entries sit on top. They are charged as the max over branches, which is a safe
   bound, since the branch running at the peak need not be the widest.

How tight the term is:
- **Exact** where it can be. `(?<=a{1,2})x` on `bax` peaks at 3 lookbehind-owned entries (mark,
  `POS`, `LO`), and the term charges 2 + 1. Cell 5 of §5.1c (W12) peaks at 4 with its body's one.
- A safe OVER-charge elsewhere: a branch that exits at its guard writes no `LO_i`, and the
  negative and non-atomic forms over-charge the 2 by one, as today.

**The frames term `1 + nbranch` stays a safe bound** (say so in its header). At most one
lookbehind-owned retry frame is live at once, `L_adv_i` or today's next-branch frame, plus
`L_neg_ok` on the negative form. The last `range` branch now pushes, so the term is still at least
the exact count. Rev 1 named only `vm_count_slots_look`. `vm_cost_look` is the second pass that
must agree with the emitter, and its header gains the `range` paragraph.

Further consequences:
- **A lookbehind inside a loop.** `vm_cost_rep`'s arms read `body.trail` per iteration, so the
  same term corrects the per-iteration charge (one more entry per `range` branch than today's
  constant). Without it, the stamped `subject_ceiling` of a pattern like `(?:(?<=a{1,9})b)+`
  over-promises.
- **Beyond the clamp `[r-cursor]`: no longer a lookbehind question.** Rev 2 proposed `growable` and
  `pt += (number of range branches)` because its term could pass the 3072 clamp with about twelve
  full-width branches. The new term grows with the number of BRANCHES on a path, as today's
  constant 2 grows with the number of lookbehinds. So the existing sizing and its honest-stamp rule
  cover it, and the proposal is withdrawn.

**Frames.**
- The retry frames are ordinary frames, counted by D42's frame bound.
- Live LOOP frames: at most one per branch per active lookbehind. `[r-cursor]` Each candidate's
  frame is popped before the next candidate's is pushed, and branch exhaustion moves on without a
  frame.
- A non-atomic `(?<*` also keeps the body's own choice points live past `L_ok`, as today's fixed
  `(?<*` does.
- Steps: every retry is one backtrack resumption, counted by the step budget.

**The per-position note.** `lookaround_design.md` §3.7's per-position note grows from `n·Σk_i` to
`n·Σ(hi_i − lo_i + 1)·hi_i` in the worst case. The long-subject leading-lookbehind cell it asked
for gains a variable twin (stage 1, gate 4).

### 5.6 Overlap with the VM record remodel (D153, [VMREC]) `[r3 F13]` `[r-cursor: re-mapped]` `[r2-1106 F1, F3, F5, F7]`

Stage 1 is a capability row, so D153's sequencing rule does not bind it formally. It does add a VM
body shape that [VMREC] steps (b) and (c) must model `[r-cursor]`:
- a trailed bound slot `LO_i`, written once per evaluation;
- an untrailed local `K_i`, dead before the first push;
- a retry frame that saves a CANDIDATE position, whose target steps it one character.

Every statement maps to an existing KIND. Three need a new member or operand inside one:

| statement | kind | new? |
|---|---|---|
| guard, both sentinel tests, exhaustion test | `VK_BRANCH` | no |
| `LO_i`'s write | `VK_SET`, trailed, slot `vm_slot_lblow(v, j)` (§5.1b) | no |
| `K_i`'s writes | `VK_LSET` on a new `VmLocalKind` member, `VL_LB_COUNT`: ONE artifact-wide local `<p>_lb_count` `[r2-1106 F3]`. The first write is `VLO_ASSIGN` with a src text that names no local (`scan_position < D ? scan_position : D`, `D` the literal `hi_i − lo_i`); the decrement is `VLO_ASSIGN` with src `<name> - 1` | a sub-kind MEMBER |
| the frame | `VK_PUSH` at `VPOS_CURSOR` | no |
| the charges | `VK_WORK`: the literal `lo_i`, the local's name, the literal 1 | no |
| the `lo_i` back-step | `VK_SEEK` `VSK_BACKSTEP`, literal count (today's record), built by the SAME builder line as the `one-length` row's back-step `[r2-1106 F5]` | no |
| the far back-step | `VK_SEEK` `VSK_BACKSTEP` with a LOCAL count operand `[r2-1106 F5]`: the `seek` operand gains `bool byloc; VmLocal x;`, set only by a new builder `pcrec_vm_b_seek_local(sb, sk, x)`; `vm_r_seek` renders `x`'s name iff `byloc`, else `k` as today | an OPERAND |
| the two restores | `VK_SEEK` `VSK_RESTORE` from `LO_i` and from `POS` (today's record) | no |
| the one-character step | `VK_SEEK` with a new `VmSeek` member, `VSK_STEP_CHAR` `[r2-1106 F1]`: rendered `scan_position = <p>_fwd_step(subject, (size_t)slot_values[<slotx>], scan_position);` with `slotx` = `POS`, the same text under every encoding | a sub-kind MEMBER |

Notes on the three:
- **No new `VmKind`.** The review r5 ruling ("the step adding a VM record kind waits for the
  remodel's analysis stage") is about a new KIND (`VK_AUTO`). `[r2-1106 F7]` RULED (ruling 7,
  2026-11-06): new members of the closed lists `VmSeek` and `VmLocalKind` are row additions and do
  not wait for [VMREC], but [VMREC] must list them (below).
- **Rev 2's `slotx`-as-value arm on `VSK_BACKSTEP` `[r6 V3]` is not needed.** The far count lives in
  a local, so the operand is typed as a local, and `slotx` keeps its one meaning (an index, as
  `VSK_RESTORE` reads it). V3's warning still applies to the new operand: render the local's VALUE
  (its name), never an index.
- **The `one-length` row's records are unchanged** (ruling A).

**Builder shapes and the two sabotage anchors that read builder TEXT `[r2-1106 F5]`.**
- S133's `SAB_BEFORE` is the exact line `    pcrec_vm_b_seek(v->sb, VSK_BACKSTEP, NULL, k);`, with
  `SAB_COUNT=1`. Stage 1 keeps exactly one such line: `vm_look_behind_branch` computes the first
  back-step's literal count once (`k` for `one-length`, `lo_i` for `range`) and emits it through
  that one line, so the existing builder's signature and its six call sites do not move. S133's
  sabotage then inlines the first back-step of BOTH rows, and the `residlbrange` fixture's
  per-site count sees it (§7). The far step is the new builder's only call, so it has an anchor of
  its own (S133's `range` twin).
- S123's `SAB_BEFORE` is `            pcrec_vm_b_seek(v->sb, VSK_RESTORE, sl, 0);` in `vm_look`,
  `SAB_COUNT=1`. The `range` row's two restores live in `vm_look_behind_branch` and name their
  slot through their own variables (`posx`, `lox`), never `sl`, so S123's exact line still matches
  once. The build confirms both counts with the matrix's field validation (`VALIDATE_ONLY=1`).

**`K_i`'s declaration and name `[r2-1106 F3]`.**
- ONE local serves every `range` branch of the artifact. It is written and read only between
  `L_b_i` and the branch's first push, which is straight-line code with no choice point and no
  call, so no two `K` values are ever live at once, in any nesting, recursion or splice. So there
  is no `<n>` and no per-branch numbering (rev 3's `<p>_lb<n>_count` is withdrawn).
- Its sizing pass: `VmFrame` gains `bool lb_count` (the `span_cursor` precedent). `vm_emit_search_body`
  `[r3-1106 READY-6]` sets it from the count pass's `nlblow_total > 0`, the SAME count that sizes the `LO_i`
  sub-block (§5.1b), so the local exists exactly when a `LO_i` slot does. `pcrec_vm_stmt_frame`
  declares `size_t <p>_lb_count = 0;` `[r3-1106 FIXIND-4]` from it. Every `range` branch reads the local, so no `(void)`
  suppression row is needed.
- Its name has ONE source: `vm_local_name` gains the arm `VL_LB_COUNT` → `<p>_lb_count`
  (`VmLocal`'s `loop`/`j`/`half` unused, 0). The frame's declaration row and the two TEXT reads (the
  decrement's src, the far `VK_WORK` count) take the name from the same function, exported from
  `vm_stmt.c` as `pcrec_vm_local_name` and declared in `vm_stmt.h`. That closes the
  declaration/use split [M6-READ] records as a past break ("the rename moved the uses and left the
  declarations").

**The forward step is a seam ENTRY, `$_fwd_step` `[r2-1106 F1]` (the manager's ruling).** Rev 3
spliced the encoding's `advance` text into the VM body as a new caller of an existing field. The
review traced its readers: DD12a(i) went red (a second encoding splice, outside every named
region); the advance-agreement check never read the new site, so W14's byte-step arm had no
detector; the body's length, which the entry-shape knee reads (`pcrec_vm_stmt_program_bytes` →
`pcrec_sb_len_decide` against `VM_INLINE_CHAIN_MAX_BYTES`), would differ by encoding; and the utf8
text carries a K49 comment that is false at a lookbehind and survives `-fno-comments` (measured,
`vlbrev4_evidence/premise.out`). Rev 4's form:

- **The entry.** `PCREC_ENCE_FWD_STEP` (the next free bit, `1u << 8`), one row in `entries_byte[]`
  and one in `entries_utf8[]`, placed after `PCREC_ENCE_BACK_STEP`. `engine_callable` true,
  `inline_def` true, `requires` 0. Contract (its `decls_doc`, the inline entry's contract doc):
  `$_fwd_step(s, n, pos)` returns the position one CHARACTER after `pos`, never past `n`; the
  caller guarantees `pos < n <= subject_length`; it reads `s` only in `[pos + 1, n)`. It is
  `next_pos` over the prefix `[0, n)`, which is what K49's tie checks. Bodies:
  - byte: `(void)s; (void)n; return pos + 1;`
  - utf8: `size_t i = pos + 1; while (i < n && (s[i] & 0xC0) == 0x80) i++; return i;` (`[r3-1106 READY-10]` its own
    literal, never `next_pos`'s text or a call of it; `next_pos`'s body; §5.1a shows it equals rev 3's bounded `advance` on every input).
- **Why it may be engine-callable when `next_pos` is not.** `next_pos`'s `false` rests on
  unanchoredness being the automaton's own self-loop, so an engine has no external advance to route
  through (enc.h). A lookbehind's candidate step has no automaton representation, which is exactly
  `$_back_step`'s and the span compare's case. The entry's id comment says so.
- **The mask, and the STOP RULE.** `vm_look_behind_branch` consults
  `pcrec_enc_entry_engine_callable(..., PCREC_ENCE_FWD_STEP)` and ORs the bit only when it emits a
  `range` branch (the `$_back_step` precedent in `vm_look_behind` `[r3-1106 READY-6]`). Inline definitions are emitted only
  for entries in the mask (`enc_emit_inline_defs` tests `mask & t->id`), and a lookbehind-free
  artifact carries no `rx_back_step` today (measured, `premise.out`): the same gate keeps
  `$_fwd_step` out of every artifact without a `range` branch. Every such artifact is a pattern
  refused today. So NO EXISTING ENCODING'S OUTPUT MOVES A BYTE, and the STOP RULE is not triggered.
  The build confirms by grep that no emitted text reads the mask's numeric value (none is known).
- **What the entry form removes from the owed list.**
  1. The second splice: the matcher body holds one CALL line, the same text under `byte` and
     `utf8`, so DD12a(i)'s body comparison is satisfied as it is for `$_back_step` today.
  2. The entry-shape knee: the body's length counts the call line only. The definition is emitted
     ahead of the program by `pcrec_enc_emit_inline_defs`, outside `VmBody`, as `$_back_step`'s
     is: `(?<=a|bc)x` stamps `RX_VM_PROGRAM_BYTES 2628ULL` under both encodings today
     (`premise.out`). So the entry-shape decision never reads the step's encoding-dependent
     length. A regression would change the body text or the `<PREFIX>_VM_PROGRAM_BYTES` stamp
     line, and DD12a(i) compares both.
  3. The K49 comment: the step's prose is its own D112 doc pair (`decls_doc`, `defs_doc`), emitted
     through `PCREC_CMT_NONESSENTIAL`, so a `-fno-comments` artifact carries none of it. The retry
     loop's `advance` text and its comment are untouched.
  4. The "one splice" sentences stay TRUE (DD12a(i)'s header item (2), emit_vm.c's K49 comment,
     enc.h's `advance` contract, src/gen/CLAUDE.md), and rev 3's widening of `advance`'s `@N`
     comment is withdrawn. None of them is edited.
- **What it adds:** a third spelling of the boundary rule (`next_pos`, `advance`, `fwd_step`), tied
  by K49 below; one bullet in `match_api.md` §3¶2 (§10); src/enc/CLAUDE.md's entry list; a
  decision-log line at landing recording the entry (the `$_back_step` precedent: no D58 contract
  change, since no `PcrecEncEntry` field, seam signature or recipe line moves).

**DD12a(i) reads region (1) FROM THE SEAM `[r2-1106 F1]`.** Today region (1) is `SIG_RE`
(`tests/codegen/run_encoding_checks.sh`, the DD12a(i) Python block): a hand-written alternation of
ten entry and helper NAMES and of nine RETURN TYPES, plus the hand lists `TWINNED`, the
`span_ci_helper` mapping, and the residual keys of `agg` and of the floor tuple. Its own comments
record three drifts of those lists ([VAR]'s `int` return type, the `span_ci_` rename's KeyError,
[CLS-TREE]'s `decode`). Stage 1 replaces them with the seam's own answer:
1. **A seam function** (enc.h/enc.c) `[r3-1106 FIXIND-6: the side-emission condition is one predicate both the emitter and this function call]`: `void pcrec_enc_entry_symbols(const PcrecEnc *e, unsigned id,
   void (*each)(const char *sym, void *u), void *u)`. It names every file-scope symbol entry `id`'s
   emission DEFINES: each `$_<ident>` that opens a column-0 declarator (a function head or a table)
   in the row's `defs` text, plus what enc.c itself emits beside a row (today only
   `SPAN_CASELESS_UCP`'s Latin-1 fold table, written by `enc_emit_latin1_fold_table`). It sits beside
   the code that emits those symbols, so the list cannot drift from the emission.
2. **A test reader**, `tests/codegen/enc_entry_list.c`, linked against `build/libpcrec.a` (the
   `tests/utf8/startbnd_backend_check.c` precedent, which reads backend rows directly). For every
   backend in the registry and every row it prints `backend <TAB> id <TAB> inline|outline <TAB>
   symbols...`, and a member column for `PCREC_ENC_BOUNDARY_ENTRIES` (K49, below).
3. **DD12a(i)'s Python reads that table** (its path is an argument) and derives:
   - the head matcher: a column-0 line whose declarator is `<prefix>_<sym>` or `<prefix>__<sym>`
     followed by `(` or `[`, after ANY return-type tokens. Both of `SIG_RE`'s alternations go;
   - `TWINNED` = the `outline` entries' symbols;
   - the counter KEY = the entry, so a helper symbol counts under the entry whose text defines it
     (the `span_ci_helper` mapping goes);
   - `[r3-1106 FIXIND-1]` rule (b) is keyed by the entry a row STANDS FOR (the reader's `stands-for`
     column: `SPAN_CASELESS_UCP` → `SPAN_CASELESS`), so a substitute row and its original count as
     one key. As first written: rule (b)'s per-pair symmetry compares, per entry, PRESENCE on each side, and admits presence on
     one side only where the reader lists the entry in that backend alone (today `var_valid` and
     `decode`, utf8 only, and the UCP caseless compare, byte only);
   - rule (a)'s floor: every entry the reader lists is reached at least once across the run, on the
     side(s) that carry it. The residual keys of `agg` and of the floor tuple come from the reader.
   Regions (2)-(5) are fields, stamps and selections, not entries, and are unchanged.
   The legacy `span_ci_decode` alias goes too: DD12a(i) re-emits every pair from the current
   compiler, so no artifact from before [CLS-TREE] S4 reaches it.
4. **One witness joins the explicit list:** `(?<=a{1,2})x` (and `[r3-1106 FIXIND-2]` `(*UCP)(?i)(a)\1x`, for the byte-only UCP row). It reaches `back_step` and `fwd_step`
   under both encodings. Without it the derived floor is red, which is the point: a new entry
   cannot pass DD12a(i) without a witness.
5. **Re-validation (the section's own (d))**, in a throwaway tree: the existing plant before
   `_accept:` stays red; a plant that drops one symbol from `pcrec_enc_entry_symbols` turns the
   section red (the unexcised definitions differ); the `fwd_step`-inlined plant of §7 turns it red
   under `-e utf8`.
- **Proportion.** About 40 lines in enc.c, a reader of about 60 lines, and one Python block whose
  hand lists shrink. That is proportionate to stage 1, and it deletes the lists whose drift the
  file records three times, so the named-region fallback is NOT taken. Had it been, the entry
  form would still make the step a member of region (1): the fallback is "add `fwd_step` to
  `SIG_RE`, `agg` and the floor tuple by hand", the `$_back_step` precedent, not a region (6).

**K49 reads its agreement sites FROM THE SEAM `[r2-1106 F1]`.**
1. enc.h declares, beside the entry enum, `PCREC_ENC_BOUNDARY_ENTRIES` = `PCREC_ENCE_NEXT_POS |
   PCREC_ENCE_FWD_STEP`: the entries that spell the boundary rule, with the contract each member
   meets, `entry(s, n, pos) == next_pos(s, n, pos)` for every `pos < n`. A new boundary-spelling
   entry joins the mask where its contract is written. (A `PcrecEncEntry` column was the
   alternative; a mask does not touch every positional row of both backends, D58 addendum 2 item
   2's reason.)
2. The reader prints the mask's members and their symbols per backend.
3. The check compiles one witness per encoding that carries every member (`(?<=a{1,2})x`,
   `--engine=vm`; `next_pos` is always in the mask). Its driver `#include`s the artifact rather
   than linking it, so the `static inline` members are callable. For every cell of today's
   alphabet sweep and every member other than `next_pos`, it sweeps every bound `b` in `(pos, n]`
   and requires `member(s, b, pos) == next_pos(s, b, pos)`.
4. Non-vacuity per member, as today per encoding: under `byte` every answer is `pos + 1`; under
   `utf8` at least one is not. The member count is printed and floored (2 per encoding today), so
   a member that leaves the witness's mask is red (K35).
5. The retry advance keeps its own extraction, anchored on the retry loop's guard line. `advance`
   is a FIELD, not an entry, and making it one would move every byte artifact (enc.h's own reason
   it is text). This is the one site K49 still finds by anchor, and it is the one splice DD-12 (7)
   admits.

**Other readers of the new entry.**
- DD12a(ii) (the signature-identity check, same file): its `sigs_of` name list comes from the same
  reader (entries both backends carry), and a second witness, `(?<=a{1,2})x`, is compared beside
  `(?i)(?<=ab)(b)\1x`, so `fwd_step`'s signature is compared too.
- [M5-SEAM] (`tests/codegen/run_codegen_tests.sh`): `INLINE_RESID` gains `rx_fwd_step` BY HAND.
  That check states its expectation from the test on purpose (its header, R32 E7/C2: "the
  expectation comes from the test, not from the artifact"), so it is not derived. The new fixture
  `residlbrange` declares `fwd_step:1` (§7); existing fixtures are unchanged, since the entry is
  absent from their masks.

**[VMREC]'s member list, and its home `[r2-1106 F7]`.** Ruling 7 makes the list a condition. Its
home is a new long-form body, `docs/design/plan_row_bodies/VMREC.md`, written directly as a body
(the `BOXQUEUE.md` and `CAP-SPAN.md` precedent) by the stage-1 build commit, when the members
exist. The same commit adds it to the [VMREC] row's refs line and to that directory's CLAUDE.md.
Its entries, each with the declared effect (c) will read:
- `VSK_STEP_CHAR`: writes the subject cursor; reads the cursor, one slot (`POS`) and the subject;
  calls the seam entry `$_fwd_step`;
- `VL_LB_COUNT`: an untrailed local, one per artifact, live only between a `range` branch's guard
  and its first push;
- the `VSK_BACKSTEP` local count operand (`byloc`, `x`): reads that local;
- two operands that read the local through TEXT rather than as a record field: the decrement's
  src and the far `VK_WORK` count. Existing `rv` locals have the same shape, so (c)'s rule "every
  analysed operand is printed by its renderer or carried as a record field" lists them with the
  `rv` reads rather than treating them as new.

## 6. Staging and acceptance gates

**Stage 0 (no code): D27 extract and tests first.** A spec-first author (D27, recommended: §9)
writes the cells from §7.4's revised spec text and a `vlb_d27_extract.md` cut from this note. The
oracle is libpcre2 10.46.

**Stage 1: `range` (B), capability.** Scope:
- the width rule (§5.2), with both lookbehind ceilings;
- the loop (§5.1) and the emission table (§5.1b);
- the end-check split (§5.3) and budgets (§5.5), the trail term included `[r6 V1]` (`[r-cursor]`:
  `2 + range branches`);
- the two `limits.def` rows (§5.2a);
- spec hunks (§10);
- 32 corpus rows (24 distinct) flipped from refusal to match cells (vlbinv §4; population.tsv's
  `B_loop` = `yes` and `yes(deferred path)`) `[r6 V12]`. Rev 1 said 36, which counted the 4
  backreference rows (`(a)(?<=\1)x` ×2, `(a|bc)(?<=\1)x` ×2). Those stay refused until stage 2. The
  `${v}` row stays refused;
- **the [DD-14.LB] amendment's ruled refusal is REVERSED, deliberately** `[r6 V10]`. The
  amendment (2026-08-24, `sr_d27_extract.md` §3.4(d), recorded "as a RULING";
  plan_completed.md [DD-14.LB]: "a RULED perr (tier 2)") refuses a call that is a lookbehind's one
  top-level branch when its callee has different fixed widths, though PCRE2 accepts it. That
  refusal was a consequence of the missing candidate loop. With the loop, the two deferred-path
  rows compile and answer as libpcre2 does: `^(?(DEFINE)(?<g>a|ab))ab(?<=(?&g))$` (ACCEPT, lb 2)
  and `^(?:(?<g>a|ab)){0}ab(?<=(?&g))$` (ACCEPT, lb 2; both [0-2] on `ab`). The build owes a
  decision entry that says so (text in §10);
- **the D27 material that states the refusal moves, through its owners** `[r6 V10]`:
  - both existing extracts are RE-CUT from their sources (docs/design/CLAUDE.md: never edited
    independently). They are `docs/design/la_d27_extract.md` (the G2 row, "pcrec REFUSES these
    too ... the author must not write a match expectation", and its §2.5 refusal lines) and
    `docs/design/sr_d27_extract.md` §3.4(d) (the amendment). The manager cuts them, as for the
    existing extracts, beside the new `vlb_d27_extract.md`;
  - the D27-owned corpora pin the refusal: `tests/lookaround/d27/` (`gen_refusals.py`,
    `refusals.rxt`, `spellings.rxt`) and `tests/recursion/d27/` (`sr_interactions.rxt`'s
    [DD-14.LB] cell and its `sr_gen.py`/`sr_check.py` entries, `sr_wrapped.rxt`). They are
    flipped by stage 0's D27 author from the re-cut extracts, not by the build lane. If no author
    is chartered, the manager rules each flip in the landing commit and names the cells.

Gates:
1. **Oracle differential, libpcre2 10.46**, run by `tests/lookaround/run_lookaround_diff.sh` (every
   start offset, every group span), extended by a section for these cells `[r6 V12]`. Rev 1 said
   "PC-3's harness". PC-3 is `tests/registry/pcre2_check.c`, the registry's COMPILE check, not a
   match differential.
   - The cell set: every spelling × {capturing, non-capturing} × {group alternation, bounded
     quantifier, nested quantifier, nested lookaround, atomic/possessive inside, call to a bounded
     group}. Subjects hit:
     - each length, and the clamp;
     - the end-check backtrack, including a greedy tail quantifier (W3b);
     - the non-atomic retry;
     - a varying branch followed by another branch (W11);
     - `startpos > 0`;
     - byte and UTF-8;
     - `[r-cursor]` ill-formed UTF-8 subjects: a stray continuation byte AT the cursor, and an
       ill-formed run within `hi` characters before it. These are compared against libpcre2 under
       `PCRE2_MATCH_INVALID_UTF`, which is pcrec's own reading of an ill-formed subject
       (utf8_design.md §2.6). The cells are W13 and W15's (§7).
   - 0 differences, outside one named class `[r3 F7]`: `PCRE2_UTF` × `startpos > 0` × a body whose
     backward reach exceeds LB (`\b`/`\B` or a nested lookbehind at a candidate's far edge). That is
     D142 item 3's STATED DIVERGENCE (`match_api.md` §9.4¶8; `CLIP` in `tests/utfcheck`).
   - Those cells stay IN the population as expected-divergent. They are compared against D142's
     rule (pcrec gives the byte-mode answer) and counted on their own line, so the population count
     stays honest. The simulate lens measured 7,776 such cells at offset 3 and 5,012 at offset 4.
   - The generator counts its own population and its expected-divergent subset (K35). Both are
     pinned with floors.
   - `[r2-1106 F6]` **The harness's encoding modes.** `run_lookaround_diff.sh` and its shared oracle
     `tests/backrefs/bref_oracle.py` have no encoding option today (rev 3 named them anyway). The
     build extends the shared oracle with a per-cell MODE column and the diff script with the
     matching pcrec flag. Three modes, named:
     - `byte`: libpcre2 options 0, pcrec `-e byte`. Today's behaviour, and the default when the
       column is absent, so the backrefs and atomic-groups callers of the oracle do not move;
     - `utf8`: libpcre2 `PCRE2_UTF`, pcrec `-e utf8`, well-formed subjects only (the generator
       asserts each subject is valid UTF-8 in this mode; an oracle UTF error is a harness failure,
       not a cell);
     - `utf8-invalid`: libpcre2 `PCRE2_UTF | PCRE2_MATCH_INVALID_UTF`, pcrec `-e utf8`, the
       ill-formed subjects (W13, W15 and the generated ill-formed cells), pcrec's own reading
       (utf8_design.md §2.6).
     The ctypes binding (`pcre2_ctypes.py`) already takes compile `options`; its `PCRE2_UTF`
     constant is marked "not used" today. In both UTF modes the start-offset sweep covers
     character boundaries only (a mid-character start is K50's domain, `tests/utf8`), and the
     skipped offsets are counted. The population is counted and floored PER MODE (K35), with the
     D142 expected-divergent subset counted per UTF mode.
   - A `PCREC_ERR_FRAMES` is a difference, not a give-up to excuse `[r6 V1]`: no gate-1 cell is
     near the trail clamp, so the trail term makes every cell fit.
2. **Identity, by `tests/codegen/run_recursion_identity.sh`** `[r6 V7]`. Every corpus artifact
   containing a lookbehind is byte-identical (G2; owner question 1). That instrument compares every
   call-free corpus pattern against `$FILEPIN` (whole file) and `$ABASEPIN` (program region). It
   HARD-FAILS a call-free pattern that one build accepts and the other refuses. Stage 1 flips 22
   distinct call-free patterns (30 rows) from refused to compiled, so the gate is red BY
   CONSTRUCTION on the landing until it is re-pinned. The procedure:
   - run it against the pre-landing pins;
   - require `differing = 0`;
   - require the refusal-mismatch set to equal EXACTLY the flipped manifest. The build counts that
     manifest from `vlbinv_evidence/population.tsv` (K35), and 22/30 is the expected value at this
     freeze. The 2 call-bearing deferred rows are compared by the gate's call-bearing arm;
   - then re-pin `$FILEPIN`/`$ABASEPIN` in the landing's own commit, the gate's documented
     "moves on purpose" route. Under (A) that is not an abi bump.
   - Under (B), the same re-pin carries the abi number, and the `differing` population is every
     lookbehind artifact.
   - `tests/lookaround/run_lookaround_identity.sh` (default `STRICT_ALL=0`) compares only the
     lookaround-FREE bucket, so it does not carry G2.
3. **Accept set ⊆ PCRE2's, and the classification control `[r3 F2, F4]`.**
   - Every cell pcrec compiles, libpcre2 compiles: 0 exceptions, outside the one stated
     divergence `[r6 V6]`. That is an unbounded repeat of a zero-width body in a lookbehind branch
     (`(?:)*`, `(?:\b)*`, `(?:)+`, `(?:(?=b))*`, `(?:a{0})*`), which pcrec accepts and libpcre2
     refuses (err 125). The generator crosses "nested lookaround" and "bounded quantifier" with
     such a repeat, so the class is IN the population. Its cells are counted on their own line, like
     gate 1's D142 cells. The classification control excludes them by the same rule, since
     libpcre2 at `max_varlookbehind = 0` refuses them for a reason that is not width.
   - **G1's accept-set measurable holds at stage 1 only if the 65535 ceiling rides stage 1**
     `[r6 V15]` (owner question 2). If it does not, the ceiling cells move to the ceiling's own row,
     and G1 is stated false until that row lands.
   - The boundary cells are in the set:
     - cap: `a{1,255}`/`a{1,256}`, `a{255}|b{1,2}`/`a{256}|b{1,2}`, UTF `é{1,255}`/`é{1,256}`;
     - ceiling: `(?<=a{65535})x`/`(?<=a{65535}b)x` and `(?:a{1000}){65}`/`{66}`.
   - For every cell, pcrec's per-branch "one length" judgment must equal libpcre2's accept/refuse at
     `max_varlookbehind = 0`. libpcre2 at 0 accepts exactly the lookbehinds with no varying branch.
     This is the independent check that §5.2's range is exact. pcrec's judgment is read from the
     `--emit-ir` label role (§5.1b, role text 1: "fixed width %d" against "width %d..%d")
     `[r6 V5]`.
4. **Budget cell.** The variable twin of §3.7's long-subject leading-lookbehind cell gives the same
   answer as libpcre2, or a documented `PCREC_ERR_WORK` at a stated subject size (§5.5). It never
   gives `PCREC_ERR_FRAMES` (the trail term, §5.5) `[r6 V1]`.
5. **Sabotage.** The rows of §7 are each red in their sabotaged build and green in the correct one.
   S136 is re-aimed as §7 spells it (F9). S133, S134 and S-U4 move as §7 lists `[r6 V8]`.
   `[r2-1106 F5]` S123 keeps its one anchored site (§5.6), and the new `fwd_step` rows of §7 are
   in the set.
6. **`[r2-1106 F1]` The encoding checks.** `make test-encoding-checks`'s `run_encoding_checks.sh` `[r3-1106 READY-5]` is green
   with the derivations of §5.6: DD12a(i) (region (1) from the seam reader, the derived floor met
   by `(?<=a{1,2})x`, the re-validation plants red), DD12a(ii) (`fwd_step`'s signature identical),
   and K49 (both boundary members agree with `next_pos`, member count 2 per encoding).

**The stage-1 build units, complete `[r2-1106]`.** Each unit names what it changes and every
reader of that change. "New" means a file the unit adds. The landing is one change (D80: the spec
hunks ride it).

| unit | changes | readers that move with it |
|---|---|---|
| U1 width rule and limits | `pcrec_cwmin`/`pcrec_cwmax` as an exact range per branch; the 255 cap and 65535 ceiling (§5.2); two `limits.def` rows (§5.2a) | `src/parse/mod_lookaround.c`'s refusal arm (deleted for bounded bodies) and the refusal TEXT readers of §10; `--list-limits`/`pcrec_limits_tsv`, `limits_check.sh`'s name manifest and its count 78 → 80; the mrl.c header sentences of §5.2; `[r3-1106 READY-7]` the stored widths representation (`const int *widths` → a pair per branch, internal.h and its comment) and its readers `la_lb_raise`, the hook, `pcrec_lookaround_fix_widths`, `vm_look_behind`, `vm_count_slots_look`, `vm_cost_look`; `LA_MSG_MAX`'s comment |
| U2 the loop and the emission table | `vm_look_behind_branch` (the `range` row: guard, `lo_i` back-step through the one existing builder line, `LO_i`, `K`, far step and retry, `L_try`/`L_body`/`L_end`/`L_adv`/`L_n`), `vm_look_behind`'s label allocation (`range` branches only), the end-check split (§5.3) | the count pass (`vm_count_slots_look`: push count, `nlblow`), `vm_cost_look` (trail `2 + range branches`, header paragraph), the role and note texts (§5.1b) and the stale 160-byte comment, gate 3's label phrasing, `match_api.md` §4¶6's INTERNAL comments (§10) |
| U3 slot sub-block | `nlblow`/`nlblow_total`, `vm_slot_lblow`, the totals step (§5.1b) | `vm_slot_name`'s `low` arm, the listing's second `low` call, `VmSnap.lblow` and `vm_build_region_saves`' range, the layout comment's `nlow` paragraph, `VmStamp.nlow` (counts both, listing only) |
| U4 record vocabulary | `VSK_STEP_CHAR`, `VL_LB_COUNT`, the `seek` operand `byloc`/`x` and `pcrec_vm_b_seek_local`, `VmFrame.lb_count`, `pcrec_vm_local_name` exported (§5.6) | `vm_r_seek` (two arms), `vm_local_name`, `pcrec_vm_stmt_frame`'s declarations, `vm_emit_search_body` (the frame's producer) `[r3-1106 READY-6]`, `docs/design/stream/arev.md`'s VmSeek member count `[r3-1106 READY-9]`, `vm_stmt.h`'s enum comments; NEW `docs/design/plan_row_bodies/VMREC.md` + the [VMREC] refs line + that directory's CLAUDE.md |
| U5 the seam entry | `PCREC_ENCE_FWD_STEP`, a row in each backend, `PCREC_ENC_BOUNDARY_ENTRIES`, `pcrec_enc_entry_symbols` (§5.6) | the mask OR in `vm_look_behind_branch`; src/enc/CLAUDE.md; `match_api.md` §3¶2 (§10); the landing's decision entry |
| U6 checks | DD12a(i) derivation, DD12a(ii) list and witness, K49 boundary sites (§5.6); NEW `tests/codegen/enc_entry_list.c`; [M5-SEAM]'s `INLINE_RESID` and the `residlbrange` fixtures (§7); gate 1's oracle modes (`bref_oracle.py`, `run_lookaround_diff.sh`) and its new cell section | tests/codegen/CLAUDE.md (the new reader), tests/lookaround/CLAUDE.md, `docs/testing.md` where it describes DD12a(i), K49 or gate-1's harness; `[r3-1106 FIXIND-3, READY-2..4, READY-9]` the `resid_backdecl` guard 7 → 9 and its header, an exact `fwd_step` guard (= 2), `writers.tsv` A4, `run_partlayout.py`'s `sec_seam`, the c1 nm arm's fixture list, K49's header; `pcre2_ctypes.py` (UTF-8 pattern encoding, `PCRE2_MATCH_INVALID_UTF`, a compile context for `max_varlookbehind`) and `tests/backrefs/CLAUDE.md`; gate 3's accept-set/classification harness, gate 4's budget cell, DD12a(i)'s re-validation plants, W-low's codegen detector, K49's member floor |
| U7 corpus and pins | 32 rows (24 distinct) flipped from refusal to match cells; gate 2's re-pin of `$FILEPIN`/`$ABASEPIN` (§6 gate 2) | the start-set mover manifests, axes allowances and size tripwires a corpus change moves (found by `make test`, BOILERPLATE's delivery bar); the D27 extracts and corpora (§6 stage 1, owned as stated there); `[r3-1106 READY-8]` `run_lookaround_diff.sh`'s exact `NPO` guard, S136's `SAB_DOC_FIGURE` |
| U8 sabotage rows | §7's new rows (W1-W16, W-low, the `fwd_step` rows), S133/S134 twins, S136 re-aimed, S-U4 re-aimed, W12's mechanism confirmed | `tests/mech/` row headers and their `SAB_DOC_FIGURE`s; `REACH_ONLY=1` run for moved witnesses; `[r3-1106 READY-1]` S133/S134's `SAB_BEFORE`/`SAB_AFTER` re-cut; `[r3-1106 READY-4]` W-low's asan confirmation and `--work-budget` compile |
| U9 spec hunks | §10's list | `make test-spec-history`, the spec's own anchors |

**Stage 2: backreferences in a lookbehind (B+) `[r3 F2, F3, F5]`.** Rev 0 said: "`pcrec_cwmax(A_BREF)`
= the widest group it can name (union over duplicate names)". That is refuted: it sets one end
only, and it accepts what libpcre2 refuses. Rev 1:

- **Width: both ends from the named group.** Inside a lookbehind body, an `A_BREF` counts its
  group's own `[cwmin, cwmax]`. A reference to a FIXED group is a FIXED item, outside the 255 cap.
  An unset group fails rather than matching empty (absent `PCRE2_MATCH_UNSET_BACKREF`), so it does
  not pull the minimum to 0. The width is EXACT (§5.2). The mrl.c header sentence that
  "`pcrec_cwmin` answers 0 EXACTLY" for `A_BREF` is retired for this consumer.
- **Timing: the deferral and a memo.**
  - A reference may name a group not yet parsed at the parse hook: a forward reference
    (`(?<=\1)(a)`) or one written before its group inside the body (`(?<=\1(a))x`).
  - So DD-14.LB's deferral predicate widens from "the body has a call" (`pcrec_has_call`,
    src/parse/mod_lookaround.c) to "the body has a call or a backreference". The pending state is
    `widths == NULL`, filled by `pcrec_lookaround_fix_widths` in `pcrec_postresolve`.
  - That pass reads a per-group `[cwmin, cwmax]` memo. Callgraph computes callee widths today, but a
    group named only by a reference has no memo, so stage 2 adds it.
- **Refusals (libpcre2 err 125, shape 7), each with its cells:**
  - a BY-NAME reference whose name is duplicated (`(?J)`). A NUMBERED reference to such a group is
    accepted. Documented in `man pcre2pattern`; not a PCRE2 bug, so D26's addendum does not apply;
  - ANY reference in a pattern that uses `(?|` anywhere. Latent until the `branch-reset` MODULE
    lands (`pattern_language.md` §8.1's table; it is not a plan row) `[r6 V12]`, but the rule is
    written now so it refuses then;
  - a reference to an unbounded group;
  - a reference to a recursive group (K127's `recurses` is the existing home);
  - a reference inside the group it names (self-reference, directly or through a call). Without this
    rule, a naive "width of group 1" recurses or reads a half-built memo.
- **The acceptance table** (the ruling lens's, re-run in `vlbrev1_evidence/cells.out` where marked
  †):

  | shape | cell | libpcre2 10.46 | stage 2 |
  |---|---|---|---|
  | back, varying group | `(a\|bc)(?<=\1)x` † | ACCEPT, lb 2 | accept, `range` [1,2] |
  | back, fixed group | `(a)(?<=\1)x` | ACCEPT, lb 1 | accept, `one-length` 1 |
  | back, fixed group over the cap | `(a{300})(?<=\1)x` † | ACCEPT, lb 300 | accept, `one-length` 300 |
  | fixed reference beside a long fixed branch | `(a)(?<=\1\|b{300})x` † | ACCEPT, lb 300 | accept (no branch varies) |
  | fixed reference beside a varying branch | `(a{300})(?<=\1\|b{1,2})x` † | REJECT 200 | refuse (cap) |
  | back, cap boundary | `(a{1,255})(?<=\1)x` / `(a{1,256})…` | ACCEPT 255 / REJECT 200 | same |
  | inside | `(?<=(a\|bc)\1)x` † | ACCEPT, lb 4 | accept, [2,4] |
  | inside, fixed | `(?<=(a)\1)x` † | ACCEPT, lb 2 | accept, `one-length` 2 |
  | inside, written before its group | `(?<=\1(a))x` † | ACCEPT, lb 2 | accept (deferral) |
  | forward | `(?<=\1)(a)` †, `(?<=\g{+1})(a)x` | ACCEPT, lb 1 | accept (deferral) |
  | forward, fixed over the cap | `(?<=\1)(a{300})x` † | ACCEPT, lb 300 | accept (deferral) |
  | unset group | `(a)?(?<=\1)x` † | ACCEPT, lb 1 | accept, [1,1] |
  | numbered reference to a duplicate-named group | `(?J)(?<n>a)\|(?<n>bc)(?<=\1)x` † | ACCEPT, lb 1 | accept |
  | duplicate name | `(?J)(?:(?<n>a)\|(?<n>b))(?<=\k<n>)x` †, `(?J)(?<n>a)(?<n>b)?(?<=\k<n>)x` †, `(?J)(?<n>a)\|(?<n>bc)(?<=\k<n>)x` † | REJECT 125 | refuse |
  | branch reset anywhere | `(?\|(a)\|(b))(?<=\1)x` †, `(?\|x)(a)(?<=\1)x` †, `(?\|(a)\|(b))(c)(?<=\2)x` † | REJECT 125 | refuse (latent) |
  | unbounded group | `(a+)(?<=\1)x` † | REJECT 125 | refuse |
  | recursive group | `(a(?1)?)(?<=\1)x` † | REJECT 125 | refuse |
  | self-reference | `(?<=(a\1))x` † | REJECT 125 | refuse |

  The full 40-row table with match answers is `docs/dev/reviews/2026-11-05-r3-vlookbehind/ruling.md`.
  Every row there matches this rule. Gates 1-3 run over these cells plus generated reference cells.
  A reference to a group made only of an unbounded zero-width repeat inherits stage 1's stated
  divergence (§0 G1, `[r6 V6]`): accepted, and counted on its own line.
- **The fixed-group half needs none of stage 1's loop.** A branch made only of one-length items and
  references to fixed groups is a `one-length` branch: today's emission. Only the width memo, the
  deferral and the refusals are new. Stage 2 also closes a gap on FIXED-width lookbehinds: pcrec
  accepts no backreference lookbehind today, though libpcre2 accepts 23 of the 29 shapes probed.
  The owner's ordering ruling stands (the range loop first); this records that the order is a
  choice, not a dependency.
- **The `pcrec_cwmax` header comment** (src/opt/mrl.c) claims a lookbehind branch containing a
  backreference "is therefore never fixed-width — which is the answer libpcre2 gives too". That is
  false at 10.46: `(a)(?<=\1)x` is accepted, lb 1. The fix rides the stage-2 build (PLAN).

**Stage 3 (HELD): `reverse-dfa`**, under §5.4's evidence and prerequisites. It brings its own abi
event (new emitted text in artifacts that took `range`), a tuning.md section, a deny decision and
witnesses WD1-WD6.

## 7. Sabotage witnesses (each can fail; floors and domains stated)

Every witness is a lookbehind, so it routes VM in both builds (all lookaround rows are `VM_ONLY`).
No admission floor applies to `range`, the total fallback. Each row names the fact that makes it
fail.

| id | sabotage | witness (libpcre2 10.46 answer) | why it reaches and fails |
|---|---|---|---|
| W1 | candidates shortest first | `(?<=(a\|aa))c` on `aac`: (2,3) g1=(0,2) | Range 1..2 varies (the `range` row). The capture makes the chosen length observable: sabotaged g1=(1,2). A capture-free order sabotage changes no answer and is NOT a witness. |
| W2 | end-check removed | `(?<=a{1,2})x` on `abx`: nomatch | At length 2 the body succeeds ending at 1. Without the check: a false match (2,3). |
| W3 | end-check without backtracking into the body | `(?<=(a\|ab)(b\|))x` on `abbx`: (3,4) g1=(0,2) g2=(2,3) | The first path at length 3 ends at 2; only a later path ends at 3. |
| W3b `[r3 F10]` | the body's trailing greedy quantifier gives nothing back (tail possessified: no frame inside it) | `(?<=a{1,2})a` on `aaa`: [1-2][2-3] | At cursor 1, `a{1,2}` from 0 takes two characters and ends at 2. Only giving one back ends at 1. Sabotaged: [2-3] only. W3's alternation does not reach this site. |
| W4 | negative arm keeps the hard return on a varying branch | `(?<!ab?)x` on `acx`: (2,3) | Length 2's body ends at 1. Sabotaged: returns `PCREC_ERR_INTERNAL`. |
| W5 | non-atomic retry frames cut | `(?<*(a{1,3}))c\1` on `aaaca`: (3,5) g1=(2,3); `(?<*(a\|aaa))c\1` on `aaaca`: (3,5) g1=(2,3) | The follow `\1` fails at length 3; only a retry reaches length 1. The second row has a gap at length 2, which distinguishes "every length" from "next accept" (§5.1c cell 4). |
| W6 `[r3 F8]` `[r-cursor: re-aimed]` | the UTF-8 far retry broken: (a) a far step that returns the sentinel ends the branch; (b) it is taken as "start at `LO_i`" (no retry) | `(?<=(é{0,2}))x` on `éx`, `-e utf8`: [2-3, g1 0-2] | Two bytes but one character precede the cursor, so `K = min(2, 2) = 2` and the far step returns the sentinel; only the retry at `K = 1` reaches 0. (a) nomatch; (b) [2-3, g1 2-2] (§5.1c cell 6). Rev 2's cell (`(?<=(é{1,2}))x` on `éx`) no longer reaches: `LO = 0` makes `K = 0`. UTF-8 only: under bytes the count is exact and the retry dead (S134's status). |
| W7 | clamp relative to `startpos` (S135 carried) | `(?<=a{1,2})b` on `aab` from 2: (2,3) | The body's bytes lie before `startpos`. |
| W8 | cap applied only to varying branches | `(?<=a{300}\|b{1,2})x`: refused (err 200) | Sabotaged compiles a pattern libpcre2 refuses (gate 3). |
| W9 | cap off by one | `(?<=a{1,255})x` compiles, `(?<=a{1,256})x` refused | The boundary cell pair. |
| W9b `[r3 F4]` | ceiling missing or off by one | `(?<=a{65535})x` compiles, `(?<=a{65535}b)x` refused (err 187); `(?<=(?:a{1000}){65})x` compiles, `{66}` refused | The ceiling boundary pairs: fixed, and through a product. |
| W10 | branch order lost (longest over all branches) | `(?<=(a)\|(aa))c` on `aac`: g1=(1,2) | Branch 2 is longer. Sabotaged: sets g2. |
| W11 `[r3 F1]` `[r-cursor: re-aimed]` | (a) exhaustion does not restore the cursor (`L_n_i`'s `VSK_RESTORE` dropped on the exhaustion path); (b) the same restore dropped on `LO_i`'s sentinel path | (a) `(?<=a{1,2}\|b)x` on `bx`: [1-2], and `(?<=a{1,2}\|bc)x` on `bcx`: [2-3]; `(?<=a{2,3}\|b)x` on `bx`: [1-2] stays as the guard's control. (b) `(?<=é{2,3}\|é)x` on `éx`, `-e utf8`: [2-3] | (a) The next branch starts from the nearest candidate, and its guard fails: nomatch (§5.1c cells 1 and 3). (b) Two bytes, one character: the guard passes, `LO`'s back-step returns the sentinel, and without the restore branch 1 back-steps from `(size_t)-1`. UTF-8 only (under bytes the guard is exact). Rev 2's (a) "the frame saves the candidate" is now the DESIGN: the restore at `L_n_i` is what replaces the frame's cursor. |
| W12 `[r6 V1]` `[r-cursor: re-aimed]` | (a) a trailed write per candidate under the O(1) term (rev 2's `D_i` kept, or `LO_i` written at `L_try_i` instead of before it); (b) the term charged one short per `range` branch (today's constant 2) | (a) `(?<=a{1,9})x` on `bbbbbbbbbax`: [10-11]; UTF-8 twin `(?<=a{1,9})x` on `éééééééééax`: [19-20]. (b) `(?<=a{1,2}\|b{1,2})x` on `abx`: [2-3] | At default options, a bounded pattern's trail is `cost.trail + 1`. (a) Nine candidates: 2 + 9 live entries against a capacity of 5 (§5.1c cell 5): `PCREC_ERR_FRAMES`. `[r2-1106 F5]` THE MECHANISM, stated: under the "`LO_i` at `L_try_i`" spelling the write sits inside the cycle, so `goto L_try_i` carries a K134 checkpoint, and `<prefix>_trail_compact` drops later same-slot entries once (depth 4 → 3) and then declines to re-arm (its trigger stops after one round), so the fourth candidate's write hits `RX_R_FRAMES`. Red, but because the trigger stops; a K134 change that re-arms compaction would turn (a) green. The build confirms (a) red, and the row's header names this dependency so a K134 change re-aims it. Rev 2's `bax` cell has two candidates and no longer overflows under a per-candidate write (2 + 2 against 4 + 1). (b) Both branches write `LO`: peak 2 + 2 plus the body's; one short per branch sizes it two short, past the `+ 1`. A single `range` branch one short is MASKED by the `+ 1`, so (b) keeps two `range` branches. The exact body share is INFERRED (the ladder picks the body's rung), so (b)'s margin is confirmed at build. |
| W13 `[r-cursor]` | the one-character step bounded by the subject length instead of the cursor | `é(?<=(a?))` on `C3 A9 A9`, `-e utf8`: [0-2, g1 2-2]; `é(?<=a{0,1})` on the same: [0-2] (libpcre2 under `PCRE2_MATCH_INVALID_UTF`) | A stray continuation byte sits AT the cursor. The unbounded step jumps from 0 past the cursor to 3, never meets `LO = 2`, and runs until a budget gives up (§5.1c cell 7). UTF-8 only: the byte step `pos + 1` reads no bound. `[r2-1106 F1]` The plant is now "the call passes `subject_length` as `$_fwd_step`'s bound instead of `POS`" (one argument in `vm_r_seek`'s `VSK_STEP_CHAR` arm). |
| W14 `[r-cursor]` | the step skips a candidate (two characters, or two bytes under UTF-8 where it should be one character) | `(?<=\Ga{1,2})b` on `aab` from 1: [2-3] (from 0: [2-3]; from 2: nomatch); `-e utf8` `(?<=\Gé{1,2})b` on `ééb` from 2: [4-5]; `-e utf8` `(?i)(?<=(k{1,2})\|(b))x` on `b` U+212A `x`: [4-5, g1 1-4] | `\G` pins the ONE candidate that can succeed to the second one tried, so a skipped candidate is nomatch. The Kelvin cell needs one step over a 3-byte character from `b` to the Kelvin sign. A BYTE step under UTF-8 only adds mid-character candidates, which fail (no body starts inside a character): answer-neutral, so no cell sees it. `[r2-1106 F1]` Rev 3 named the advance-agreement check as its detector; that check never read the lookbehind site. The byte-step arm now has two plants, each with a named detector: (i) the emitter writes `scan_position += 1` (`VSK_ADVANCE 1`) instead of calling `$_fwd_step`, and drops the mask bit: [M5-SEAM]'s per-site count on `residlbrange` and its `-e utf8` twin (`fwd_step:1` → 0, and the declared inline-entry set), S133's shape; (ii) the utf8 backend's `$_fwd_step` body returns `pos + 1`: K49's boundary tie (§5.6) disagrees with `next_pos`, and its utf8 non-vacuity fails. |
| W15 `[r-cursor]` | the back-step's own clamp lost: a far-step sentinel taken as "start at `LO_i`" | `(?<=(a{0,2}))b` on `FF 61 62`: [2-3, g1 1-2]; `(?<=(é{0,2}))b` on `A9 C3 A9 62`: [3-4, g1 1-3] (both under `PCRE2_MATCH_INVALID_UTF`) | An ill-formed run lies within `hi` characters before the cursor. The retry finds the farthest VALID start (§5.1c cell 8). Sabotaged: g1 = (2,2), (3,3). The other naive reading, "start at the subject start", is answer-neutral here (no body consumes an ill-formed byte). It is excluded by work (§5.1a), not by a witness. |
| W16 `[r-cursor]` | the nearest candidate never tried (exhaustion tested after the step, or `LO_i` one character too far) | `(?<=a{1,2})x` on `bax`: [2-3]; non-atomic re-entry into the next branch: `(?<*(a{1,2})\|(aa))\2` on `aaaa`: [2-4, -, 0-2] | Only the nearest candidate (`a` at 1) matches in the first cell. In the second, the follow `\2` fails for both of branch 0's candidates (g2 unset), the exhaustion restores the cursor, and branch 1 sets g2. |
| W-low `[r-cursor]` `[r2-1106 F2, F5]` `[r3-1106 FIXIND-5: the plant is `vm_set_line` rendering an untrailed write for `SLOT_LB_LO*`]` | `LO_i` held in an untrailed LOCAL (a second `VmLocalKind` member beside `VL_LB_COUNT`, written by `VK_LSET` and read by the exhaustion test), the natural mistake, since `K_i` is held that way. (Rev 3 spelled the plant "`LO_i` written by `VK_LSET`", which the vocabulary cannot build: an LSET targets only a `VmLocal`, never a slot.) | ANSWER LEVEL: `(?:(?*.*(?<*a?))b)*$` on `bc`: [2-2] (libpcre2 10.46, byte and UTF, every start; `vlbrev4_evidence/premise.out`). Second detector: a codegen check on `residlbrange` that `LO_i`'s write is an `RX_SET` of an `SLOT_LB_LO<j>` slot | Iteration 1 evaluates the non-atomic lookbehind at cursor 2 (`LO = 2`) and leaves its `L_adv` frame live. Iteration 2's `b` fails, so its lookahead's `.*` backtracks and re-evaluates the lookbehind at cursor 1, writing `LO = 1`. When iteration 2 and then `$` fail, the pop returns to iteration 1's frame at candidate 2. Trailed, `LO` is rewound to 2 and the branch is exhausted. Untrailed, `LO` stays 1: the exhaustion test never fires and the step runs past the cursor and the subject. Rev 3's argument ("a stale bound only comes from a later evaluation on a forward path") was false: a non-atomic lookahead moves the cursor BACKWARD. The review's literal interpreter: 652 of 2,904 such cells move. What a real artifact does on the overrun: each step charges 1 work unit and each retry is one backtrack resumption, and the body's character tests guard `scan_position < subject_length`, so the EXPECTED outcome is a give-up (`PCREC_ERR_STEPS` or `PCREC_ERR_WORK`, whichever budget ends first), never an out-of-bounds read. The build confirms that under `make asan`'s compilee axis, and compiles the witness with a small `--work-budget=N` (limits.md §3.1¶2) so the sabotaged run ends fast. |

**Stage 3's witnesses** (row `reverse-dfa`). Admission floor: each body below varies and its machine
is a few states, far under any cap, so the row reaches in both builds.
- WD1 (exactness conjunct dropped): `(?<=(?>a|ab)b)x` on `abbx` is nomatch (sabotaged: a false
  match), and `(?<!(?>a|ab)b)x` on `abbx` is (3,4) (sabotaged: missed).
- WD2 (one untagged machine for all branches): W10's cell.
- WD3 (nearest accept instead of farthest): W1's cell.
- WD4 (farthest only on the non-atomic form): W5's gap cell.
- WD5 (floor at `search_from`): W7's cell.
- WD6 (context at the floor ignored): `(?<=\ba{1,2})x` on ` aax` is (3,4), and on `baax` is
  nomatch. `[r3 F11, NOTED]`: only the `baax` cell discriminates (the ` aax` cell is green under
  the sabotage). Keep the pair together; never split it.

**Existing rows that move.**
- **S136** (design row S-LA11, "the width rule accepts a branch that is not fixed width") tests a
  premise that stage 1 removes: its `perr` cells become match cells.
  - Its header says it is the ONLY thing in the tree that exercises the negative arm's
    `RX_R_INTERNAL` return, which stage 1 keeps for `one-length` branches (§5.3). It is re-aimed so
    that it still does.
  - **The sabotage is spelled exactly `[r3 F9]`: the STORED one-length pair of one branch becomes
    K+1 at BOTH ends.** This is an edit to `la_widths`' stored pair, not to `pcrec_cwmin` or
    `pcrec_cwmax` alone. An over-reporting `pcrec_cwmax` alone (the "free" direction S136 chose
    today) makes the branch `range` [K, K+1]. It then declines instead of returning INTERNAL, and
    both cells stay green.
  - Positive cell: `(?<=bc|d)x` on `abcx`, libpcre2 (3,4). The sabotaged body starts at `a` and
    fails, so nomatch.
  - Negative cell: `(?<!bc|d)x` on `bcax`, libpcre2 (3,4). The sabotaged body matches `bc` from 0
    and ends at 2, not 3. The end-check fires and the matcher returns `PCREC_ERR_INTERNAL`.
  - A negative cell where the body fails outright, such as `abcx`, would not reach the end-check.
    It declines before it: a false match, not the hard return.
  - **Which branch `[r6 V8]`: every branch, or branch 0, never only the last.** Sabotaging only `d`
    (the last branch) leaves both cells green: the positive cell still matches through `bc`, and in
    the negative cell `d` from 1 reads `c` and `bc` from 1 reads `ca`, so both decline. The natural
    edit, `la_widths`' loop (today's S136 anchor), hits every branch, which works.
- **W1** then catches the variable-branch half (`hi` reported as `lo`).
- **S135** carries unchanged; W7 is its variable twin. Under (B) its anchor (`if (k > 0)`) sits in
  rewritten code and is re-anchored.
- **S133 and S134** `[r6 V8]` anchor the one literal-`k` back-step
  (`pcrec_vm_b_seek(v->sb, VSK_BACKSTEP, NULL, k)`) and its sentinel branch, each with
  `SAB_COUNT=1`. Their detector is `tests/codegen/run_codegen_tests.sh`'s fixture-declared per-site
  count, and every `residlb*` fixture is fixed-width.
  - `[r-cursor]` Under (A), the `range` row adds TWO back-step sites (the `lo_i` step, a literal
    count, and the far step, a local count) and two sentinel sites, which no anchor names.
    Inlining either step (`scan_position - lo_i`, `- K_i`) changes no byte-mode answer, and
    dropping the far sentinel is caught only by W6, a UTF-8 cell. So each row gains a `range` twin
    per site (`SAB_COUNT` on each site's own anchor). `[r2-1106 F5]` Exactly: the `lo_i` step shares
    S133's one builder line (§5.6), so S133 itself now covers it and keeps `SAB_COUNT=1`; the twin
    S133 owes is the FAR step's, anchored on the new builder's one call
    (`pcrec_vm_b_seek_local(v->sb, VSK_BACKSTEP, ...)`). S134's sentinel branch is anchored the
    same way: today's `== $_BACK_STEP_NONE` test carries both rows' `lo_i` sentinel, and its twin is
    the far step's `!=` test. A fall-through spelling of "drop the far sentinel" underflows `K` and
    breaks every `range` cell, so the twin's plant is the `goto L_try_i` spelling, which only W6
    sees (review r2 `sound.md`).
  - Codegen gains a `range` fixture: `residlbrange (?<=a{1,2}|bc)x --features lookaround`, with
    `back_step:3` (the `range` branch's two sites and the `one-length` branch's one; libpcre2
    ACCEPT, lb 2) and `[r2-1106 F1]` `fwd_step:1`. That makes §5.1's per-site counts checked
    statements. `[r-cursor]` A UTF-8 twin (`-e utf8`) carries the same counts. `[r2-1106 F1]` Rev 3
    said the twin "gives the advance-agreement check the bounded step to read, and it is W14's
    byte-step detector": false, since that check compiles only `a*`. W14's detectors are now the
    `fwd_step` count here and K49's boundary tie (§5.6, W14 row). W-low's codegen check (`LO_i`
    written by an `RX_SET` of a `SLOT_LB_LO<j>` slot) reads the same fixture.
  - `[r2-1106 F1]` **Two new rows for the entry** (ids from the build lane's range): (i)
    "`$_fwd_step` inlined": the `VSK_STEP_CHAR` arm renders `scan_position += 1;` and the mask
    bit is dropped (S133's shape; detector: [M5-SEAM]'s `fwd_step` count and declared inline set on
    `residlbrange`, both encodings; answers green); (ii) "utf8 step by one byte": the utf8 row's
    body returns `pos + 1` (detector: K49's boundary tie and its utf8 non-vacuity; DD12a(i) stays
    green, since the region is excised either way).
  - `[r2-1106 F5]` **S123** (`vm_look`'s `VSK_RESTORE`, `SAB_COUNT=1`) is not moved: the `range` row's
    two restores are spelled through their own slot variables (§5.6), so its anchor matches once.
    The build's field validation confirms the count.
  - Under (B), both anchors sit in rewritten code and are re-cut.
- **S-U4** `[r6 V8]` (`pcrec_cwmax(A_CLASS)` × 4) loses its STATED detector. Its
  `SAB_DOC_FIGURE` predicts that every class-bearing lookbehind refuses. After stage 1, a
  class-bearing lookbehind of two characters or more becomes `range` with today's answers: the
  extra candidates fail the end-check and the true one answers.
  - `[r2-1106 F5]` Rev 3 re-aimed it on `(?<=a)x`, which cannot carry it: a ONE-character body is a
    T3 context node, built before any width rule (src/parse/mod_lookaround.c, "T3 FIRST ... No
    width rule is asked of it"), and its `--emit-ir` has no lookbehind label at all (measured,
    `vlbrev4_evidence/premise.out`). Re-aimed on `(?<=ab)x`: its label reads "lookbehind branch 1
    of 1, fixed width 2" today, and under S-U4 (×4) the judgment becomes "width 2..8".
  - It is re-aimed at gate 3's classification control on that cell. Its figure is updated, and so
    is its own `SAB_DESC`/header text ("`(?<=a)x` included"), which is already stale today for the
    same T3 reason.
  - The verifier notes that it likely still goes red on the cap and ceiling boundary cells, where ×4
    crosses 255 or 65535. So the figure is wrong rather than the detection gone. The row is run at
    build to confirm.
- **W12** is new (the trail term). Its sabotage edits `vm_cost_look`, a site no existing row
  reaches. `[r-cursor]` W13-W16 are new with the cursor shape. W13 and W15 are UTF-8 cells over
  ill-formed subjects, and their oracle mode is `PCRE2_MATCH_INVALID_UTF`, so the harness that runs
  them needs that option. W14 and W16 have byte and UTF-8 cells. Every row of W1-W16 was measured
  against libpcre2 10.46 (`vlbrev3_evidence/cells_*.out`; rev 0-2's cells as cited before).
- Ids are the build lane's, from the range its brief names.

## 8. The population

vlbinv §4, unchanged in its counts:
- The 37 corpus rows are pcrec's OWN refusal pins: 27 distinct patterns, 36 real, and 1 false
  positive (`(?<=${v})x`, pcrec's own variable syntax).
- Widths: one row is the `1..255` cap pin, four rows have a 0 minimum, and the rest are ≤ 3
  `[r3 F14]`.
- Outside demand: ONE bench pattern (`negation-scope-lookbehind-var`, widths 4..51).
- The case is completeness against PCRE2 (the scoreboard's rank 1 gap), not measured demand.

Stage 1 covers 32 rows (24 distinct) and the bench pattern. Stage 2 brings 36. Stage 2 also closes
the FIXED-width backreference lookbehinds, a population the corpus count does not separate
(§6 stage 2).

## 9. A D27 spec-first author: recommended

- **Why.** The level-2 order (longest first) runs against the emitter's usual preference-first
  direction. It is the rule that tests derived from code inherit wrong (`lookaround_design.md` §2.5
  reason 1: the [M4.6d] counter-rung defect a blinded author found).
- **Where.** `tests/lookaround/d27/` exists to extend.
- **What the author gets.** The revised §7.4 text and a `vlb_d27_extract.md`, re-cut from this note
  and never edited independently (docs/design/CLAUDE.md rule). The author does not get this note's
  §5.
- **What the extract must carry `[r3 review recommendation]`:**
  - stage 2's refusal list (duplicate names, `(?|`, unbounded or recursive groups,
    self-reference);
  - D142's UTF startpos class (§6 gate 1);
  - `[r6 V6, V10]` the zero-width-repeat accept-set divergence (§0 G1), and the reversal of
    [DD-14.LB]'s ruled refusal, which the re-cut `la_`/`sr_` extracts carry too (§6 stage 1).

  Without them, the author writes red cells for ruled divergences.

## 10. Spec impact (D80; hunks the build owes) `[r3 F6: completed]`

- **`pattern_language.md` §7.4¶5.** The rule becomes: "each alternative may match a bounded number
  of characters, at most 65535; at most 255 once any alternative's length varies". Three sentences
  move with it:
  - the shape-5 refusal examples `(?<=(a|bc))x` and `(?<=(?:a|bc))x` become match examples;
  - `(?<=a+)x` stays as the unbounded refusal (shape 7);
  - the backreference sentence (`(a)(?<=\1)`) changes at stage 2.

  The preference order (written order, then longest first, the body backtracking until it ends at
  the position) and the non-atomic retry each get a paragraph with an example.

  **The stated divergence `[r6 V6, RULED]`** gets a sentence in the same paragraph: "An alternative
  containing an unbounded repeat of something that matches no characters, such as `(?:)*` or
  `(?:\b)*`, counts as zero characters, so `(?<=(?:)*a)x` is accepted. PCRE2 refuses such a
  lookbehind (its error 125); accepting it is a deliberate divergence." This is D26's addendum:
  accepting more than PCRE2 is not a defect.
- **`pattern_language.md` §9¶2.** Stage 1 deletes the clause "a lookbehind alternative of varying
  length ... including `(?<=(?:a|bc))x`". Stage 2 deletes the clause "or containing a backreference
  (§7.4)". Both clauses are refusals of accepted syntax that the stages retire.
- **`pattern_language.md` §7.11¶3.** The parenthetical "a `consume` site there is refused first, as
  a lookbehind whose length is not fixed" is re-read against the width the analysis gives a consume
  site. If that width is unbounded, the parenthetical says "... whose length is unbounded". If it is
  bounded, the site now passes the width rule and reaches the callout-in-lookbehind refusal itself,
  and the parenthetical is deleted. Either way the refusal stands. Only the reason it names moves.
- **`pattern_language.md` §7.3¶5 and §7.3¶6** (stage 2).
  - §7.3¶6 ("A backreference inside a lookbehind is refused") becomes the stage-2 rule with its
    refusals.
  - §7.3¶5 (duplicate names) gains: "inside a lookbehind, a by-name reference to a duplicated name
    is refused".
- **`pattern_language.md` §2.4's refusal-shape table.** Shape 5's "variable-length lookbehind"
  example is removed. The unbounded, cap, ceiling and lookbehind re-entry refusals are shape 7 (PCRE2
  refuses them too), with the sentences of §5.2. None names a raise flag. Shape 7's "means" cell
  widens to "not well-formed, or over a PCRE2 length limit; PCRE2 refuses it too" `[r6 V12]`.
  §2.4¶2's courtesy (follow PCRE2's wording where pcrec has some) is available for the three
  sentences. That is D26 tier 3, so it is optional.
- **`limits.md` §3.** A new subsection, §3.11 "Lookbehind length", holds the two rows (§5.2a)
  `[r6 V9]`:
  - `LA_LOOKBEHIND_BRANCH_MAX` = 65,535 and `LA_LOOKBEHIND_VAR_MAX` = 255, spelled comma-grouped as
    `limits_check.sh` finds them;
  - unit `chars`: characters under UTF, bytes in byte mode;
  - kind `compile budget`, override none (the `PCREC_MAX_GROUP_DEPTH` precedent): crossing either
    refuses the pattern;
  - the cap's setting is [IFACE-PUSH]'s (a dated CANDIDATE line in
    `docs/design/plan_row_bodies/IFACE-PUSH.md`).

  `--list-limits`/`pcrec_limits_tsv` gain the two rows. The table's kind vocabulary is unchanged,
  so the dump's header is unchanged.
- **`match_api.md` §4¶6** (`PCREC_ERR_INTERNAL`) `[r6 V11]`.
  - It has two producers: the end-check of a `one-length` branch on the negative arm, and D72's
    subroutine region-exit guard. This repairs the pre-existing "its one producer" drift rather
    than carrying it forward.
  - The stale `pcrec_maxw` becomes the stored width pair (`pcrec_cwmin`/`pcrec_cwmax`).
  - "Redundant for the width class the module ships" becomes "redundant for one-length branches; a
    varying branch's end-check declines instead".
  - The code comments that read it move in the same change (§5.3): `src/enc/enc_utf8.c`'s back-step
    header, `vm_look_behind`'s note 3, and the `emit_vm.c` comment naming the end-check as INTERNAL's
    "one producer today".
- **`match_api.md` §9.4¶2.** LB is the widest branch's maximum. The wording already covers the
  variable case; re-read it.
- **`match_api.md` §9.4¶8** (D142's clip divergence). Re-read: its class grows with varying bodies,
  and its "three patterns in the pinned set" count is a reader (gate 1).
- **Readers of the refusal TEXT** that move in the same change, found by grep at build time:
  - exact text: `tests/recursion/run_lookbehind_call_sweep.py` (a classifier whose population flips
    when bounded-call cells start compiling) and `tests/recursion/inlookaround.rxt`;
  - mentions without the exact text: `tests/lookaround/lookbehind_group_alt.{rxt,gen.py}` and
    `tests/recursion/gen_corpus.py` (a `kind='capability'` cell);
  - also `tests/reject/run_reject_tests.sh` and `tests/mech/sabotages/S172_postresolve_walk_order.sh`
    (the ruling lens's grep);
  - the D27 material `[r6 V10]`: the two extracts (`la_d27_extract.md`, `sr_d27_extract.md`
    §3.4(d)) are re-cut from their sources, and the D27-owned corpora (`tests/lookaround/d27/`,
    `tests/recursion/d27/`) are flipped by their owner (§6 stage 1).
- **No `ir_listing.md` hunk** `[r6 V4]` `[r-cursor: same conclusion, new reason]`. `LO_i` joins the
  `low` family (RULED, ruling 8; its own sub-block, §5.1b `[r2-1106 F4]`), which the `slots` section lists, so the listing gains rows in
  new artifacts. The family NAME stays `low`, so §3.2¶2's vocabulary is not extended, and `holds`
  is "the role text" class of cell, not specified per family. Under the counter-family alternative
  there would be no listing row at all, as rev 2 said.
- **`limits.md` §3.1 `[r-cursor]`.** §3.1 states per-construct work charges (§3.1¶4's literal runs).
  The lookbehind's charge becomes caller-visible in the give-up point, so the build adds one
  sentence: "a lookbehind alternative is charged each back-step's character count and, when its
  length varies, one unit per further candidate start". Rev 2 changed the charge too and owed the
  same sentence.
- **Not spec: enc.h's `advance` contract** `[r-cursor]` widens `@N` to "the bound the step never
  passes" (§5.6). enc.h is internal, so this is a comment change in the same commit.
  `[r2-1106 F1]` WITHDRAWN: `advance` gains no caller, so its contract does not change.
- **`match_api.md` §3¶2** `[r2-1106 F1]`. The paragraph names the `static inline` encoding-residual
  helpers an artifact may carry. It gains `<prefix>_fwd_step` ("a lookbehind-bearing artifact
  whose lookbehind has an alternative of varying length"), beside `<prefix>_back_step`, under the
  same terms: defined ahead of the engine body, declared nowhere, not exported, not a caller entry.
  Every artifact that carries it is new output for a newly compiling pattern, so this moves no
  existing artifact and is no abi event (§14).
- **The decision entry the build owes** `[r6 V10]` (the next D-number at landing; text to adapt):
  "[VLOOKBEHIND] stage 1 SUPERSEDES the [DD-14.LB] amendment's ruled refusal (2026-08-24,
  `sr_d27_extract.md` §3.4(d)). That ruling refused a call that is a lookbehind's one top-level
  branch to a callee of different fixed widths, which PCRE2 accepts. It was a consequence of the
  missing candidate loop. With the loop, `^(?(DEFINE)(?<g>a|ab))ab(?<=(?&g))$` compiles and answers
  as libpcre2 10.46 does (ACCEPT, lb 2). The extracts are re-cut and the D27 cells flipped in the
  same landing. The same entry records the zero-width-repeat accept-set divergence (V6, D26
  addendum) and the loop's cursor-rung shape (rev 3: one trailed bound per alternative, the trail
  term `2 + range alternatives`)." The manager acknowledges the supersession when ruling.
- **Stage 3 only:** a `tuning.md` §2 section for the row and its stamp, and the abi event.
- **`docs/pcre2_compliance.md`**, via the compliance-refresh skill after landing (not spec). It
  records that pcrec answers at libpcre2's DEFAULT `max_varlookbehind` only.

## 11. The standing questions

1. **Measurement regime.**
   - Stage 1: RELEVANT ONLY AS A BOUND, not a decision input. No number selects anything: the
     emission row is selected by a width fact, not a measurement. G4 is a count of body runs and
     work units in the emitted text.
   - §5.5's give-up arithmetic is a worst case per evaluation, at the default budgets. Gate 4
     measures the leading-lookbehind subject size on the dev box (7700X, gcc 15.2, glibc), and a
     different box moves only time, not the count.
   - Stage 3: RELEVANT. The row's evidence is the per-position cost of a lookbehind evaluation, hit
     vs miss, throughput over a subject, on the dev box, through both VM entries (the tiered default
     entry and `_search_in`; the architecture rule for VM capacity changes).
   - Two regimes would flip the row: candidates that fail at the first byte (the bench pattern)
     versus candidates that do not. That is why both are required.
2. **Independent control.** RELEVANT.
   - Answers are checked against libpcre2 10.46, a separate implementation sharing no source with
     pcrec.
   - The new classification control (gate 3) checks pcrec's one-length judgment against libpcre2's
     accept at `max_varlookbehind = 0`. It is independent of `pcrec_cwmin`/`pcrec_cwmax`, which is
     what makes §5.2's exactness checkable.
   - Who counts: the cell generator is written from the spec and §2's cells. It counts its own
     population and its D142 expected-divergent subset (K35), each against a pinned floor.
   - Witness reach: each witness in §7 states why it reaches its site in both builds (all VM, no
     admission floor on `range`). W6, W3b, W11 and S136's spelling were re-derived in rev 1 so that
     each can fail. The stage-3 witnesses state the row's admission they clear, and WD6 names its
     one discriminating cell.
   - The rev 1 sketch was hand-executed literally (§5.1c), per the review's lesson 1: a simulation
     of the rule's intent does not validate the sketch.
   - `[r6 V1]` review r6's lesson: a model that omits a resource bound validates answers, not the
     build. The trail term is derived from the passes that SIZE the storage (`vm_cost_look`,
     `vm_plan_capacities`), not only from the slot's readers (§5.5). W12 is its witness, and it
     fails on today's constant.
   - `[r-cursor]` The cursor shape's totality has two controls, neither derived from rev 3's
     sketch:
     - libpcre2 10.46, over vlbpieces' two sweeps re-run through a literal `cursor` evaluator
       (`vlbrev3_evidence/sweep_cursor.py`: 54,579 cells, 0 differences), plus 52 hand-picked
       cells (`cells_*.out`);
     - rev 2's counter loop as the reference candidate sequence (`candidates.py`: 8,583,480 UTF-8
       cells, exhaustive over its alphabet, with literal ports of the emitted `back_step` and
       `advance` text). Rev 2's sketch was hand-executed and libpcre2-checked in rev 2. The control
       can fail: three one-line variants differ on 288,168, 3,398,699 and 591,194 cells. Its
       population is the generator's own count, printed in its output.
   - `[r2-1106 F1]` **The encoding checks' own controls.** DD12a(i)'s region (1) and K49's boundary
     sites now come from the SEAM (§5.6), which is what declares what is encoding-owned. That is
     not a shared source with what DD12a(i) controls: the subject is the SHARED emitter text, which
     the seam does not write, and anything outside the seam's declared symbols that differs by
     encoding is still red. The derivation can fail in both directions, and each has a plant: a
     symbol dropped from the seam's list turns DD12a(i) red, and an entry with no witness fails the
     derived floor (K35). K49 ties each boundary member to `next_pos` through a compiler, as it
     ties `advance` today, and counts its members.
   - `[r2-1106 F2]` W-low is now an ANSWER witness, found by literal execution (review r2): a
     model that has no trail could never have moved under a trail sabotage, which is why rev 3
     found "no cell".
3. **What moves when data is regenerated.** MOSTLY NOT RELEVANT: stage 1 adds no table, calibration
   or generated file.
   - The new data are the two `limits.def` rows (§5.2a). `--list-limits` and `pcrec_limits_tsv`
     gain two lines, so their readers move in the same change: `limits_check.sh`'s name manifest
     and its count 78 → 80, plus any other pin found by grep at build time.
   - The refusal text's readers (§10) are text readers, not data, and also move in the same change.
   - Owner question 1 was answered (A) (2026-11-06), so no existing lookbehind artifact moves.
   - Stage 3's reverse machines are generated per artifact from the pattern, so a rebuilt machine
     moves only that artifact's bytes.

## 12. The question for a pcre2-reader (D181)

Kept from vlbinv §7. One question: "In PCRE2 10.46, when a lookbehind has at least one variable-length
branch, which branches does `max_varlookbehind` limit, and how does the matcher run a variable-length
branch: does it try each step-back length from longest to shortest, re-running the branch forward
each time and backtracking inside it until it ends at the assertion point?"

Its answer confirms the cap rule that §5.2 copies and the cost model that §5.5 assumes. Every
observable behaviour is already measured, including the 65535 ceiling (rev 1). No second question is
needed: D's vetting rests on measured cells (§2), not on PCRE2's internals.

## 13. Questions for Frank (plain words; leanings are not rulings)

1. **ANSWERED (A), 2026-11-06 `[r-cursor]`. Kept as asked, for the record.** The (A)/(B) costs
   below are rev 2's. Under rev 3 the range loop carries a position slot, not a counter slot, and
   a trail checkpoint only where its body writes the trail (§5.1b). (B)'s per-branch extras change
   accordingly; nothing about (A) does.

   RE-ASKED `[r3 F12]`: should today's fixed-width lookbehinds keep their exact code?

   **What changed since you were asked.** The earlier answer assumed the new loop turns into today's
   code by itself when a branch has only one possible length. The review showed it does not. The
   compiler has to CHOOSE the old code when it sees "this branch has one length". So it comes down
   to two honest choices.

   **(A) Keep today's code, and write the choice down as a two-line table.**
   - The table: "one length → today's code; a range of lengths → the loop" (§5.1b).
   - Cost: one declared choice in the lookbehind emitter, read off a fact the compiler already
     stores, with both lines tested by the same witnesses and the libpcre2 comparison.
   - Nothing that compiles today changes, and no abi event is owed.
   - The "one mechanism" goal holds for the mechanism (one candidate loop), not for the text.
   - `[r6]` The table now lists, for each line, every place the compiler reads it: the counter
     slot, the frames, the trail size, the labels and the comments. So the two lines cannot drift
     apart unnoticed. New patterns that use the loop also carry a trail checkpoint and about 38
     lines of trail-compaction helpers, which today's code already has for other loops.

   **(B) Use the loop for every branch, fixed ones too, and take an abi event.**
   - Every artifact with a lookbehind changes: about 826 lookbehind lines in 40 `.rxt` files feed
     the identity gate, and all are re-pinned.
   - Each changed artifact gains one counter slot per lookbehind branch, which renumbers the slots
     after them.
   - The last branch keeps one more frame per evaluation, which shifts frame and step counts by one.
   - Each fixed branch emits about 4-5 more C lines, plus a trail checkpoint `[r6 V1]`.
   - Every lookbehind artifact gains K134's trail-compaction helpers (about 38 lines), and its trail
     grows by at least one entry per branch.
   - Sabotage rows S133, S134 and S135 are re-anchored, because the code they point at is rewritten.
   - The negative-lookbehind hard error stays tied to "one length". Retiring that too would remove
     one of `PCREC_ERR_INTERNAL`'s two producers, and S136, which is a further contract change.
   - Speed: unmeasured, expected negligible.
   - Benefit `[r6 V2]`: one loop for every branch, plus a one-column choice for the negative
     end-check (hard error at one length, decline otherwise). Rev 1 said "no table", which was
     wrong unless the hard error is retired too.

   **Leaning: (A).** Stability outranks textual unity in the goals. The choice is declared, keyed on
   an existing fact and answer-free. Under your open "VM base" frame it is exactly an admission row:
   the plain loop is the reference, and the one-length code is a cheaper section substituted where
   sound.
2. **ANSWERED: stage 1, 2026-11-06 `[r-cursor]`.** The 65535 ceiling. It refuses two patterns pcrec compiles today, which nobody uses: fixed
   lookbehinds longer than 65535 characters. Does it ride stage 1, or get its own small row?
   Leaning: stage 1, since nothing in the population comes near it. `[r6 V15]` The goal "pcrec
   accepts nothing PCRE2 refuses" is only true at stage 1 if the ceiling rides stage 1. With its
   own row, that goal is stated false until the row lands.
3. **Answered (review r3; recorded, not re-asked).**
   - The 255 limit is a policy for matching PCRE2's default: correctness needs none. 255 stays the
     default, and a setting waits for [IFACE-PUSH].
   - Backreferences inside a lookbehind follow the acceptance table of §6 stage 2: back, inside and
     forward are accepted; duplicate names, any `(?|`, unbounded or recursive groups and
     self-reference are refused.
   - The loop ships first. The reverse-DFA row stays HELD, with its home in the stream roadmap's
     A-REV area, and lookbehind is its first client.
   - Unbounded lookbehind, with the automaton filter that makes it cheap, is filed HELD as
     [LB-EXIST].
4. **Answered (review r6, manager rulings; recorded, not re-asked).**
   - The loop's counter uses the existing counter slots. No new kind of slot is added.
     `[r-cursor]` SUPERSEDED: there is no counter. The loop's one slot is a position (Q6 below).
   - pcrec keeps accepting a lookbehind with an unbounded repeat of something that matches nothing,
     like `(?<=(?:)*a)x`, which PCRE2 refuses. The spec says so as a deliberate difference.
   - Stage 1 deliberately undoes the 2026-08-24 ruling that refused a call to a group like `(a|ab)`
     inside a lookbehind. That refusal existed only because the loop did not. The decision entry
     at the build says so.

5. **ANSWERED `[r2-1106 F7]` (manager, ruling 7, 2026-11-06): no.** New members of `VmSeek` and
   `VmLocalKind` are row additions and do not wait for [VMREC]; [VMREC] must list them, in
   `docs/design/plan_row_bodies/VMREC.md` (§5.6). Kept as asked:
   **NEW `[r-cursor]`, the manager's call: does the "wait for the remodel" rule cover a new member
   of an existing statement family?** The loop needs no new kind of VM statement. It needs a new
   member in two closed lists that existing kinds carry: one more kind of cursor move (step one
   character, never past the cursor) and one more kind of matcher-local variable (the far count),
   plus one optional operand on the existing back-step (§5.6). The review r5 rule held back a new
   KIND until the remodel's analysis stage. Leaning: it does not cover members, because each is a
   one-row addition to the effects table that stage will read.
6. **ANSWERED `[r2-1106 F7]` (manager, ruling 8, 2026-11-06): the span-loop low-water family**, its
   legend and listing text owed by the build (delivered arithmetically, §5.1b). Kept as asked:
   **NEW `[r-cursor]`, the manager's call (answer-free): which slot family holds the loop's one
   position?** Every choice gives the same answers and the same cost. Leaning: the span-loop
   low-water family, because its stated contract (a position the frame cannot carry, written once
   per entry, trailed) is exactly this slot's. It costs per-slot legend and listing text, so a
   lookbehind's slot is not called a span-loop low-water mark. The counter family needs no reader
   changes but names a position as a counter. §5.1b lists every reader.

## 14. What this note does not decide

- Whether stage 1 owes an abi bump at all.
  - Under question 1 (A), `match_api.md` §6¶18 says a bump is owed for "any change to the emitted
    scaffolding for identical inputs", so none is owed when no previously compiling pattern moves
    `[r6 V12]`. Rev 1 cited §6¶19, which says what is fixed WITHIN one abi. The 65535 ceiling
    only refuses; it moves no compiled bytes. A `range` artifact's new text (the loop, the
    checkpoint, K134's helpers) is new output for a newly compiling pattern, not a change for an
    identical input. The manager confirms at landing, with readers found by grep.
  - Under (B), it is an abi event: the next number at landing.
- The `reverse-dfa` row's design detail: tagged vs per-branch machines, re-walk vs stored set for
  non-atomic retries, record kind vs helper part. These are A-REV's and [LANDWALK-VM]'s.
- [LB-EXIST]'s design (the existence filter and unbounded lookbehind).
- [ENG-LOOK] (lookaround inside the DFA engine), [CTX-PREFILTER] and conditional groups
  ([CONDITIONALS]) are untouched; vlbinv §5's overlap check stands.
- S-ids, the file layout of tests, the generator's cell count.
- Rev 1 retires one item from this list: rev 0 left the UTF-8 clamp's spelling open. It is now the
  existing `$_back_step` entry with a run-time count (§5.1).
- **Verbs in a lookbehind body `[r6 V16]`** (latent; owned by the `verbs` module). libpcre2's branch
  length stops at `(*ACCEPT)`: `(?<=a(*ACCEPT)b{1,2})x` is ACCEPT, lb 1, a fixed length and not
  [2,3]. pcrec refuses `(*` today ("requires module 'verbs'"). When that module meets a lookbehind,
  its width rule stops at the verb, and an `(*ACCEPT)` that jumps to `L_ok` must not bypass the
  end-check. The pcre2-reader question in review r6's `sound.md` rides that module.
- **The rung ladder's migration to the same declared shape `[r6 V17, the manager's call]`.** The
  quantifier rung ladder (`vm_rep`) re-derives its choice in `vm_count_slots_rep`, which is the
  hazard §5.1b's one-row-choice rule avoids. A trigger-gated row (trigger: the next rung, or the
  next count/emit disagreement found in the ladder) is the manager's to file.

## 15. Measured vs inferred

- MEASURED, libpcre2 10.46 as a library on the dev box:
  - rev 0: every cell in §2 and §7's witness answers (`vlbdesign_evidence/*.out`) and the premise
    (`premise.txt`);
  - rev 1: F1's cells, the ceiling cells, W3b, the new W6 cell, the D142 cell and the stage-2
    acceptance cells marked † (`vlbrev1_evidence/cells.out`, `premise.out`, probe `probe.c`);
  - rev 2 (`vlbrev2_evidence/premise.out`, with rev 1's probe): W12's cells, the codegen fixture's
    accept, the zero-width-repeat refusals (err 125), and the two [DD-14.LB] rows.
- MEASURED from pcrec at this branch (`build/pcrec --features all`), rev 2:
  - today's trail capacity of four fixed lookbehind spellings (`RX_TRAIL_FRAMES 3`), confirming
    `vm_cost_look`'s constant 2;
  - pcrec compiling the zero-width-repeat class today;
  - the 38-line K134 helper span on an existing checkpoint artifact.
- MEASURED PROXY: reverse-machine sizes (`revdfa_sizes.tsv`). These are the whole-pattern reverse DFA
  of a pattern equal to the body, from pcrec's own artifact tables. A lookbehind machine is the same
  language reversed and anchored at the cursor, so the proxy is close but not the object.
- READ from code, not executed:
  - §4's evidence (file:function), §3's host and erasure rows;
  - rev 1's prologue order, `VK_SEEK`'s `slotx` operand and the seam's run-time `k` (§1);
  - the count-pass and slot-family facts (§5.1b);
  - rev 2: the trail term's derivation (`vm_cost_look`, `vm_cost_alt`, `vm_plan_capacities`, the
    emitted `RX_TRAIL`), the counter family's readers, K134's checkpoint rule (`vm_goto`,
    `vm_jump_closes_trail_cycle`, `vm_emit_trail_compact`), `VSK_RESTORE`'s rendering of `slotx`,
    and the `limits.def` schema.
- HAND-EXECUTED: §5.1c's four cells; rev 2: W12's trail peaks (4 and 6 entries).
  `[r-cursor]` Rev 3 re-traced §5.1c under the cursor shape: eight cells (the four F1 cells, W12,
  W6's UTF-8 retry, W13's bound, W15's clamp), each with its trail depth.
- `[r-cursor]` MEASURED, rev 3 (`docs/dev/lanes/vlbrev3_evidence/`, README below):
  - libpcre2 10.46: 52 cells (`cells_byte.out` 30, `cells_utf.out` 14, `cells_fold.out` 3,
    `cells_invalid.out` 5, the last under `PCRE2_MATCH_INVALID_UTF`); the model's cursor evaluator
    agrees on every cell it can express (`cells_byte_model.out`; `\1` inside a lookbehind and `\A`
    are outside the model and marked n/a);
  - the vlbpieces sweeps re-run through the cursor evaluator: 30,099 + 24,480 cells, 0 differences
    from libpcre2 (`sweep_cursor_summary.txt`);
  - the exhaustive UTF-8 candidate check: 8,583,480 cells, 0 differences, `back_step`'s sentinel
    monotone in its count, and the three refuting variants (`candidates.out`);
  - the work-charge difference distribution (`workdiff.out`).
- `[r-cursor]` READ from code, not executed: the `low` family's readers (§5.1b), `vm_goto`'s
  checkpoint predicate, `vm_r_seek`'s arms, enc_utf8.c's `back_step` and `advance` texts (ported
  line by line into `candidates.py`).
- `[r2-1106]` MEASURED, rev 4 (`docs/dev/lanes/vlbrev4_evidence/premise.out`; libpcre2 10.46
  through `tests/lib/p2probe.c`, pcrec built at this lane's worktree, main `a8f5d4721`):
  - F2's cell `(?:(?*.*(?<*a?))b)*$` on `bc`: [2-2] at every start, byte and UTF (with
    `PCRE2_MATCH_INVALID_UTF`); pcrec refuses it today (0..1 characters);
  - S-U4's re-aim: `(?<=a)x` has no lookbehind label in `--emit-ir`, `(?<=ab)x` has "fixed width
    2";
  - the retry advance's `[K49]` comment is emitted under `-e utf8 -fno-comments` (`a*`);
  - `(?<=a|bc)x` stamps `RX_VM_PROGRAM_BYTES 2628ULL` under both encodings, with `rx_back_step`
    defined ahead of the matcher; a lookbehind-free pattern carries no `rx_back_step`.
- `[r2-1106]` READ from code, not executed: the seam's entry table, `enc_emit_inline_defs`' mask
  test, `next_pos`'s utf8 body, DD12a(i)'s `SIG_RE`/`TWINNED`/`agg` lists and K49's extraction,
  `VmSnap`/`vm_build_region_saves`, `vm_slot_name`, the S133/S123/S-U4 anchors.
- INFERRED:
  - `[r2-1106]` that the new seam function and the derived DD12a(i)/K49 fit in the sizes §5.6 gives
    (estimates);
  - the speed rows of §3 (no timing was run);
  - the `one-length` row's answer equivalence to the `range` row, argued by four rewrites (§5.1b)
    and checked by gates 1-2 at build;
  - `[r-cursor]` the work totals of §5.5 (arithmetic, with the small-width difference measured);
  - G4's line and one-slot bound (UNMEASURED);
  - `[r-cursor]` which rung the body quantifier inside a lookbehind takes, so whether a given
    body writes the trail (§5.1b caveat, confirmed at build); W12(b)'s exact margin;
  - the "4-5 lines per branch" and "speed negligible" costs of question 1's option (B).

**Evidence README (`docs/dev/lanes/vlbrev3_evidence/`) `[r-cursor]`.**

| file | what it is |
|---|---|
| `probe.c` | the libpcre2 probe (vlbrev1's, plus flag `i` = UTF + `PCRE2_MATCH_INVALID_UTF`, `x` = `\xNN` subject decoding) |
| `model.py` | vlbpieces' model plus the `cursor` evaluator (byte mode, rev 3's statements literally) |
| `sweep_cursor.py`, `sweep_cursor_summary.txt` | vlbpieces' sweeps re-run through `cursor` and `range` |
| `candidates.py`, `candidates.out` | the exhaustive UTF-8 candidate-sequence check and its refuting variants |
| `workdiff.py`, `workdiff.out` | the cursor-minus-counter work distribution over the same cells |
| `mrun.py` | runs the model per cell line (n/a where it cannot express the cell) |
| `cells_*.txt`, `cells_*.out`, `cells_byte_model.out` | the hand-picked cells and their libpcre2 / model answers |

Reproduce: `gcc -O1 -o $S/probe probe.c -lpcre2-8`; `(cd $S && python3 -I .../sweep_cursor.py
$S/probe $S/out.tsv)`; `python3 -I candidates.py`; `python3 -I workdiff.py <evidence dir>`.

## 16. Disposition table (review 2026-11-05 r3)

| finding | disposition | where in rev 1 |
|---|---|---|
| F1 (SOUND-1, PREMISE-3) | FIX-NOW: re-sketched in today's order, frame saves the cursor; three cells added | §5.1, §5.1c, §2 (branch-transition bullet), §7 W11, §6 gate 1 |
| F2 (PREMISE-4, RULING-2) | FIX-NOW: both ends from the group; exactness stated, "free" premise retired; classification control | §5.2 (exactness), §6 stage 2 (width), §6 gate 3 |
| F3 (RULING-1) | FIX-NOW: duplicate-name and `(?|` refusals, five cells | §6 stage 2 (refusals, table), §10 (§7.3¶5) |
| F4 (PREMISE-1) | FIX-NOW: 65535 ceiling, `limits.def` row, gate-3 cells; owner sub-question kept | §5.2 tier 1, §0 G1, §6 gate 3, §7 W9b, §10, §13 Q2 |
| F5 (RULING-3) | FIX-NOW: deferral, per-group memo, self-reference and recursive refusals; PLAN: the mrl.c comment fix rides stage 2 | §6 stage 2 (timing, refusals, comment), §3 backref row |
| F6 (RULING-4) | FIX-NOW: hunks completed, shape 7, cap/ceiling sentences, refusal-text readers | §10, §5.2 (refusal shapes), §11.3 |
| F7 (PREMISE-2, SIM-1) | FIX-NOW: gate 1 names the D142 class, cells kept as expected-divergent, §9.4¶8 cited | §6 gate 1, §2 (D142 bullet), §9, §10, §11.2 |
| F8 (SOUND-3) | FIX-NOW: W6 cell replaced (`éx`), "why" corrected | §7 W6, §2 (UTF bullet) |
| F9 (SOUND-4) | FIX-NOW: the S136 re-aim spelled as the stored pair K+1 at both ends | §7 (existing rows that move) |
| F10 (SIM-2) | FIX-NOW: W3b added | §7 W3b, §2, §6 gate 1 |
| F11 (SOUND-5) | NOTED: WD6's discriminating cell named, pair kept | §7 (stage 3 witnesses) |
| F12 (SOUND-2, PREMISE-3(a)) | FIX-NOW: the declared emission table (selection by the width fact), work amount, slot allocation; owner Q1 re-asked | §5.1b, §5.3, §5.5, §0 G3, §13 Q1, §14 |
| F13 (RULING-5) | DOC: existing seam entry with a run-time count (no new entry, no D58 change); [VMREC] overlap, `D_i` as a record field; `VK_SET` not `VK_LSET` | §5.1 (UTF-8 clamp), §5.6, §3 host row |
| F14 (PREMISE-6/7/9) | DOC: G1 scoped and stated false today; G2's dependency on Q1; G4's constant and "one loop frame"; the population text; the callout conjunct | §0, §3 (capture-free and short-bodies rows), §5.4, §5.5, §8 |
| F15 (PREMISE-5) | DOC: R03's `VK_CONSUME_BACK` cited as in-body precedent | §4 G5, §4 "why not now" |
| F16 (PREMISE-8) | DOC: LOCATE × FINISH and the K-back sibling named; [ENG-LOOK] existence form; PLAN: HELD row [LB-EXIST] filed | §4 (the family), §5.4, §0 non-goals, docs/dev/plan.md [LB-EXIST] |
| review lesson 1 | applied: the pseudo-code hand-executed literally | §5.1c, §11.2 |
| review D27 recommendation | applied: the extract carries the stage-2 refusals and the D142 class | §9 |

## 16b. Disposition table (review 2026-11-05 r6)

Every disposition was ruled ACCEPTED by the manager (the review's RULING block).

| finding | disposition | where in rev 2 |
|---|---|---|
| V1 (SOUND-1, FIX-1, READY-1) | FIX-NOW: trail term `2 + Σ_range (hi_i − lo_i + 1)` derived from the code (exact on `bax`), trail column, "Trail" bullet, frames term stated safe, `vm_cost_look` named beside `vm_count_slots_look`; K134 checkpoint and the beyond-clamp `growable` rule (fix-induced, for the diff check); witness W12 | REVISION 2, §0 G4, §5.1 (trail bullet), §5.1b (second table, checkpoint), §5.2 (storage), §5.5 (Trail), §6 gates 1/4, §7 W12, §11.2 |
| V2 (SOUND-2) | FIX-NOW: item 5 (negative end-check) is a selection; item 6 labels, allocated only for `range`; (B)'s benefit line corrected | §5.1b (items 5-6, label column), §13 Q1 (B) |
| V3 (FIX-5) | FIX-NOW: the back-step and the work charge render the slot's VALUE, `(size_t)slot_values[<slotx>]` | §5.1b (first table), §5.6 |
| V4 (FIX-3, READY-4, FIX-8) | FIX-NOW, RULED: `D_i` is a `SLOT_COUNTER` slot; each counter-family reader and its disposition; one shared predicate; no `ir_listing.md` hunk | §5.1, §5.1b (slot allocation, readers, one row choice), §10 |
| V5 (FIX-6) | FIX-NOW: role and note texts are C comments under `-fcomments`; the seven `range` texts; gate 3 reads the label role | §5.1b (role texts), §6 gate 3 |
| V6 (READY-2) | FIX-NOW, RULED (i): keep accepting; a stated divergence in G1, gate 3, the spec hunk, the extract; stage 2 inherits it | §0 G1, §6 gate 3, §6 stage 2, §9, §10 (§7.4¶5), §13 Q4 |
| V7 (READY-3, PARTLY: 22 distinct / 30 rows) | FIX-NOW: gate 2 names `run_recursion_identity.sh`, `differing = 0`, the refusal-mismatch set = the flipped manifest (K35), the re-pin in the landing | §6 gate 2 |
| V8 (FIX-2, READY-5, PARTLY) | FIX-NOW: S133/S134 `range` twins, the `residlbrange` fixture, S-U4 re-aimed (figure, run at build), S136 "every branch or branch 0", S135 under (B) | §5.1 (UTF-8 clamp), §6 gate 5, §7 (existing rows) |
| V9 (FIX-4, READY-8) | FIX-NOW: symbols, `"chars"`, existing kind `compile budget` (`PCREC_MAX_GROUP_DEPTH` precedent), manifest +2, 78 → 80, "65,535", dead `INT_MAX` arm deleted | this note's §5.2, §5.2a, §10 (the new limits subsection) and §11.3 |
| V10 (READY-6) | FIX-NOW, RULED: [DD-14.LB]'s refusal reversed deliberately; decision-entry text; both extracts re-cut; D27 corpora flipped by their owner | §6 stage 1, §9, §10, §13 Q4 |
| V11 (FIX-7) | DOC: two INTERNAL producers; three comments join the reader list | this note's §5.3, §10 (the INTERNAL hunk) and §13 Q1 (B) |
| V12 (READY-7/9/10, PARTLY items 2-3) | FIX-NOW: gate 1's harness; §6¶18; both mrl.c headers; `branch-reset` is a module; 32 rows (24 distinct); shape 7 widened | §5.2, §6 stage 1, gate 1, stage 2, §10, §14 |
| V13 (SIMLIT-2) | DOC: one paragraph on composing with `vm_look` | §5.1 |
| V14 (SOUND-3) | DOC: §5.1c's framing sentence corrected per cell | §5.1c |
| V15 (READY-11) | DOC: G1 at stage 1 depends on owner Q2; PLAN: a dated CANDIDATE line in [IFACE-PUSH]'s long-form body (the row's own charter is at plan_lint's 6-line limit) for the `max_varlookbehind` setting | §0 G1 and non-goals, §6 gate 3, §13 Q2, docs/design/plan_row_bodies/IFACE-PUSH.md |
| V16 (SOUND-4) | DOC/PLAN: latent `(*ACCEPT)` width line, owned by the verbs module | §14 |
| V17 (standing questions) | NOTED: stage 1 takes the per-row columns and one row choice; PLAN (manager's call): the rung ladder's trigger-gated row | §5.1b (one row choice), §14 |
| SIMLIT-1, SIMLIT-3 | NOTED | none |
| review lesson 1 (size the storage) | applied: the trail term is derived from the sizing passes | §5.5, §11.2 |

## 16c. Disposition map (owner ruling 2026-11-06: the cursor-rung shape) `[r-cursor]`

The ruling, quoted in the REVISION 3 block, has one object: the loop's shape. Its condition ("able
to always be true") was tested (§5.1a): ALWAYS, so the second clause (a decision table) has no
object, and [DEC-RUNG]'s general table is not grown by this note.

| what changed | disposition | where in rev 3 |
|---|---|---|
| the loop's shape | APPLIED: cursor rung; the frame saves the candidate, `LO_i` trailed once per evaluation, `K_i` untrailed | REVISION 3, §5.1 |
| totality | MEASURED ALWAYS, with two spelling conditions (the far retry; the step bounded by the cursor) | §5.1a, §15 |
| `D_i` and V4's counter-family ruling | DELETED (no object); slot family re-asked as an answer-free manager's call | §5.1b, §13 Q4/Q6 |
| V3 (render the slot's value) | its arm on `VSK_BACKSTEP` DELETED; the rule kept for the new local operand | §5.6 |
| V1 (trail term) | RE-DERIVED from every write: `2 + range branches`; growable/`pt` withdrawn; §5.2's storage paragraph retired | §5.2, §5.5 |
| K134 checkpoint on every `range` loop | DELETED; derived by `vm_goto` from the body's trailed writes (exactly which bodies: §5.1b) | §0 G4, §5.1b |
| work charge | RE-DERIVED: `2·hi − lo` on the common path; corner bound unchanged; +1 at small widths measured | §5.5, `workdiff.out` |
| §5.5's alternative (second slot + forward step) | RETIRED: it is the design, minus the slot | §5.5 |
| a `back_step_upto` seam entry | FILED as a measured-trigger candidate, not proposed | §5.5 |
| record vocabulary | one `VmSeek` member, one `VmLocalKind` member, one local operand; D153 coverage asked | §5.6, §13 Q5 |
| `advance`'s `@N` | a new caller; enc.h comment widens (`[r2-1106 F1]` WITHDRAWN in rev 4: the step is `$_fwd_step`) | §5.6, §10 |
| `limits.md` §3.1 | one sentence on the lookbehind's work charge | §10 |
| §5.1b rewrites 1-4 | RE-STATED for the cursor shape at `lo = hi` | §5.1b |
| §5.1c | RE-TRACED: 8 cells with trail depths | §5.1c |
| witnesses | W6, W11, W12 RE-AIMED; W13-W16 NEW; W-low becomes a codegen row; S133/S134 twins per site, `back_step:3` | §7 |
| gate 1 | ill-formed UTF-8 subjects added, under `PCRE2_MATCH_INVALID_UTF` | §6 |
| owner Q1, Q2 | ANSWERED (A), stage 1 | §13 |
| `\K`, `\G`, `^` (review r5 F1/F2) | checked per body class: `\K` refused (err 199); `\G`/`^` cells pass; F1/F2 remain reverse-machine hazards, not the loop's | §5.1a |
| the fixed-tail hoist, the backward span count | still HELD (the ruling did not lift them) | none |

**What `docs/design/stream/arev.md` must pick up** (main at `0f7d79795`, arev rev 1; line numbers
are that file's; this lane did not edit it):
1. **Lines 401-402, "NOT YET RULED by Frank"**: RULED 2026-11-06 and adopted by vlookbehind rev 3. The
   paragraph "Under rev 2's spelling, if the cursor-rung spelling is NOT adopted" (lines 422-430)
   becomes history, and the reader table's bracketed rev-2 entries (line 438) can go.
2. **Line 379, row 4 `range`: "rev 2 §5.1"** → rev 3 §5.1. The reference's candidates are
   unchanged; its statements are not (`LO_i`, `K_i`, `L_far_i`, `L_n_i`).
3. **Line 259, the finisher contract, "rev 2 §5.1's body and end-check"**: still true, but the
   finisher's operand is a POSITION carried by the frame (`L_try_i`'s push), not a count. Rev 3's
   `L_try_i`/`L_body_i`/`L_end_i` are exactly row 3's, so row 3 shares them, not just their shape.
4. **Line 462, work: "`k + (candidates − 1)` (cursor-rung spelling)"** → `lo_i + Σ K (the far
   tries) + (candidates − 1)`: at most `2·hi_i − lo_i` on the common path, plus the far retry's
   `(hi − lo)(hi − lo + 1)/2` only in the UTF-8 corner (rev 3 §5.5). The one-way give-up argument
   then needs restating on TOTALS: row 3 charges at most its non-empty candidates, a subset of
   range's, and range's total is at least its number of non-empty candidates (`2K + lo ≥ K + 1`
   when `K ≥ 1` or `lo ≥ 1`; when both are 0 the one candidate is empty and both charge 0). The
   argument "every range candidate below the cursor is charged at least one" no longer reads
   per candidate, because the cursor shape's charges are per step, not per candidate.
5. **Line 438, the reader table's trail column**: range now charges 1 per branch (`LO_i`), and row 3
   writes no `LO_i`. If the term stays `2 + (number of varying branches)`, a row-3 branch is
   over-charged by one, which is safe. A per-row term (row 3: 0) is the exact form. Either way the
   column for row 3 is "0", and rev 2's "`hi_i − lo_i + 1`" bracket is dead.
6. **Lines 243-244, "vlookbehind rev 2 §5.6 V3's rule, pickup 4"**: rev 3 deleted V3's `slotx`-value
   arm. The RULE (render a reference as its value, never its index) survives in rev 3 §5.6, for the
   back-step's local operand. Cite rev 3 §5.6.
7. **Line 249, "vlookbehind rev 2 §5.5's own spelling"** (`VK_WORK` beside the call): unchanged in
   rev 3. Only the citation's revision moves.
8. **Line 667, "Moving floors, three members (..., the lookbehind's bound, ...)"**: in rev 3 range's
   own floor is not a moving `bound` but a FIXED nearest start `LO_i` with a one-character step
   toward it. Row 3's moving `bound = scan_position + 1` is unaffected. The member is row 3's, not
   range's.
9. **Line 458, soundness of row 3**: "candidates replace the back-step, so the `$_back_step` sentinel
   and `$_next_pos` are not used": add the bounded `advance` step (rev 3 §5.6 `VSK_STEP_CHAR`),
   which row 3 does not use either. `[r2-1106 F1]` In rev 4 that step is the seam entry
   `$_fwd_step` (rev 4 §5.6), not the `advance` text; cite it by that name. Under rev 3 the UTF-8
   far clamp (the sentinel retry) is range's only, so row 3's "the byte machine accepts only at character boundaries of valid input" is the
   fact that replaces both.
10. **Lines 526-528, W-trail "the concrete cell is owed by the build"**: range's own cell is now rev
    3's W12(a) (`(?<=a{1,9})x` on `bbbbbbbbbax`). Row 3's cell is still owed, and it needs a
    superset machine with at least four accepts that fail the confirm (an exact capture-free body
    takes row 2), so W12(a)'s pattern is not it.
11. **Line 424, "a trailed candidate-POSITION slot ... no existing family's contract fits it
    (... the low-water family is written once per entry)"**: rev 3's `LO_i` IS written once per
    entry, which is why rev 3 recommends the low-water family for it (§5.1b, §13 Q6). That is a
    different slot from the one line 423 rejected (a per-candidate one), so the sentence stays true;
    only its neighbourhood should not read as "the low family was rejected".
12. `[r2-1106]` **Any arev text that says the lookbehind adds "no new seam entry"** (rev 3's
    claim): rev 4 adds one, `$_fwd_step`, in the mask only for `range` branches. A row-3 producer
    does not use it (its candidates come from the machine).

## 16d. Disposition table (review 2026-11-06 r2) `[r2-1106]`

Every FIX-NOW (F1-F7) was ruled ACCEPTED by the manager (the review's RULING block), with F1's
design choice made by the manager: a seam entry, and DD12a(i)/K49 derived from the seam.

| finding | disposition | where in rev 4 |
|---|---|---|
| F1 (FIXIND-1, READY-1/2, SOUND-1/2) | FIX-NOW, RULED form: the step is the entry `$_fwd_step` (engine-callable, inline, masked per `range` branch; no existing byte moves); DD12a(i) region (1) from `pcrec_enc_entry_symbols` via a test reader; K49 sites from `PCREC_ENC_BOUNDARY_ENTRIES`; the knee reads a call line only; the step's prose obeys `-fno-comments`; W14's byte-step arm has two named detectors; the "one splice" sentences stay true; fallback stated, not taken | REVISION 4, §0 G4, §5.1, §5.1a, §5.1b (seam column), §5.6, §6 gate 6 and the build units, §7 (W13, W14, S133/S134, new rows), §10, §11.2 |
| F2 (SOUND-4) | FIX-NOW: W-low's answer cell (premise reproduced), trailing stated as necessary, the plant made buildable, the overrun's expected outcome and its build check | §5.1 (trail bullet), §7 W-low, §11.2, §15 |
| F3 (FIXIND-2, READY-5) | FIX-NOW: one artifact-wide `<p>_lb_count`, `VmFrame.lb_count` from the count pass's `nlblow_total`, one name source (`pcrec_vm_local_name`) | §5.1b (locals column), §5.6 |
| F4 (READY-6) | FIX-NOW: the arithmetic sub-block (`vm_slot_lblow`, two sub-totals), and its readers (`vm_slot_name`, the listing, `VmSnap.lblow`) | §5.1b |
| F5 (FIXIND-3/4, READY-3/9) | FIX-NOW: S133 keeps one builder line (the far step has its own builder and twin), S123's anchor kept at one, the operand's absent spelling (`byloc`), W-low's plant, S-U4 on `(?<=ab)x`; DOC: W12(a)'s K134 mechanism stated, confirmed at build | §5.6, §6 gate 5, §7 |
| F6 (READY-4) | FIX-NOW: gate 1's oracle and diff script gain the `byte`, `utf8` and `utf8-invalid` modes, populations counted per mode | §6 gate 1 |
| F7 (FIXIND-3, READY-8) | FIX-NOW: `docs/design/plan_row_bodies/VMREC.md`, written by the build commit, with the entries and effects; §13 Q5/Q6 ANSWERED, "recommended" → "ruled" | §5.1b, §5.6, §13 |
| F8 (SOUND-3) | DOC: the model validates the candidate SEQUENCE; the literal interpreter cited as the stronger evidence | §5.1a |
| F9 (READY-7, FIXIND P&H) | DOC: the 160-byte claim deleted and the stale comment listed; rev 1's sentence marked history; G2's question closed | §0 G2, §5.1b |
| F10 (sound P&H) | NOTED (out of delta; the compliance page check is the manager's) | none |
| completeness ask (brief) | the stage-1 build units with every reader | §6 |
