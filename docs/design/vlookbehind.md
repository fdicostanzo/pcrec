# Variable-width (bounded) lookbehind — design

**Status: PROPOSED rev 0** (lane vlbdesign, opus, 2026-11-05; plan row [VLOOKBEHIND]). Design only:
no build go. A critic round follows this note. Starts from the investigation
`docs/dev/lanes/vlbinv_report.md` (its §1 semantics are not repeated here) and its owner addendum
(candidate D). Evidence of this lane: `docs/dev/lanes/vlbdesign_evidence/`. PCRE2 facts come from
the installed libpcre2-8 10.46 used as a library and from public docs; the pinned source copy was
not opened (D181); one question for a pcre2-reader is in §12.

**The decision, in one paragraph.** One mechanism: per top-level branch, in written order, try
CANDIDATE STARTS FARTHEST FIRST; at each, run the branch's body FORWARD through `vm_emit` and keep
it only if it ends exactly at the cursor (the end-check, which now backtracks into the body). B and
D are the same mechanism with two different SOURCES of candidate starts: B takes every position
whose distance is inside the branch's width range; D takes the accepting positions of a reverse DFA
of the branch, run back from the cursor. So the source is a declared first-match CHOICE ROW (D186):
`range` (B) ships in stage 1 and is the total fallback; `reverse-dfa` (D) is a HELD row with a
written evidence requirement and two prerequisites (§5.4). D is not a second client of the landmark
walk ROW today, but it is made of the same PARTS (reverse NFA of a subtree, optional machine build,
`emit_reverse_block` over a `DfaDir`), and its home is the stream's one reverse `AUTO` kind
(roadmap A-REV) hosted in a VM body (§4). Today's fixed-width lookbehinds are the range row's
one-point case and keep their exact bytes, as a constant fold of the loop, not a second branch
(§5.1; owner question 1).

## 0. Goals

Ranked; the higher goal wins a conflict.

1. **G1 Answers (PCRE2 users porting patterns).** Every lookbehind libpcre2 10.46 accepts at its
   default `max_varlookbehind` (255) compiles in pcrec with the `lookaround` module and answers
   identically. Measurable: a libpcre2 differential over the generated cell set of §6 (every
   spelling × body shape × subject class), 0 differing answers (match, every group, nomatch); and
   the accept set stays inside PCRE2's: 0 patterns pcrec compiles that libpcre2 refuses, over the
   same generator plus the cap boundary cells.
2. **G2 Stability (callers with today's artifacts).** No pattern that compiles today changes bytes.
   Measurable: the identity gate over every corpus artifact containing a lookbehind, 0 bytes
   differ (conditional on owner question 1, leaning yes).
3. **G3 One mechanism (maintainers, Frank's general-mechanisms rule).** Fixed width is the one-point
   case of the general loop; no parallel path; the stream ratchet does not grow. Measurable: no new
   row in `docs/design/stream/roadmap.md` §5's inventory from stage 1; the refusal arm for bounded
   bodies is deleted (the deleted special case is the benefit).
4. **G4 Bounded cost (every caller).** A lookbehind evaluation runs its branch body at most
   (hi − lo + 1) times per branch, each charged to the work budget, live retry frames at most one
   per branch; no compile-time blow-up (per site: one body copy per branch, as today, plus a
   constant number of records). Measurable: the work charge per evaluation in the emitted text;
   artifact size of a variable lookbehind within a stated constant of the same pattern made fixed.
5. **G5 Speed where measured (later, D).** The `reverse-dfa` source ships only where per-regime
   evidence shows no regime slower than `range` beyond noise (D186 choice bar).

**Non-goals.** A reverse VM (Frank, 2026-11-05: "I'm certainly not going to try a reverse vm just
for this"); speed of variable lookbehind beyond the loop in stage 1 (one bench pattern uses it);
exposing the 255 cap as a setting (owner question 2); backreferences inside lookbehind in stage 1
(stage 2, owner question 3); lookaround inside the DFA engine ([ENG-LOOK]); `\K` inside a
lookaround (both libraries refuse it, err 199); unbounded lookbehind (both refuse it, err 125).

## 1. Premise, verified on this branch

`build/pcrec --features all` at `4e35534af` (`vlbdesign_evidence/premise.txt`): `(?<=a|bc)x`
compiles; `(?<=a{1,3})b` is refused, "variable-length lookbehind is not implemented ... (this one
can match 1..3 characters)". The investigation's code reading (vlbinv §2) was spot-checked against
`src/gen/emit_vm.c` (`vm_look`, `vm_look_behind`, `vm_look_behind_branch`) and holds; nothing in the
code contradicts a point this design rests on (STOP RULE not triggered).

## 2. Semantics to reproduce (new cells only; vlbinv §1 has the rest)

All MEASURED with libpcre2 10.46 (`vlbdesign_evidence/d_match.out`, `d_utf.out`, `w_match.out`,
`startpos.out`):

- **Atomic and possessive parts SHRINK the body's set of strings**, so a machine built over the
  body with the atomicity dropped is a SUPERSET: `(?<=(?>a|ab)b)x` on `abbx` is nomatch, the
  non-atomic `(?<=(?:a|ab)b)x` matches (3,4); `(?<=a{1,2}+a)x` on `aax` is nomatch where
  `(?<=a{1,2}a)x` matches. The negative forms flip: `(?<!(?>a|ab)b)x` on `abbx` matches.
- **Context before the start is read**: `(?<=\ba{1,2})x` matches on ` aax`, not on `aaax` or
  `baax`; `(?<=^a{0,2})x` matches on `aax`, not on `aaax`.
- **A nested lookahead may look past the cursor**: `(?<=a{1,2}(?=xy))x` matches on `aaxy`, not on
  `aaxz`.
- **Non-atomic retry walks every viable length, gaps included**: `(?<*(a|aaa))c\1` on `aaaca` is
  (3,5) g1=(2,3) (length 3 first, then length 1); the atomic `(?<=` form is nomatch.
- **Branch order beats length**: `(?<=(ab)|(b{1,2}))c` on `abbc` is g2=(1,3) (branch 1 fails, branch
  2 at its longest); `(?<=(a)|(aa))c` on `aac` is g1=(1,2) (branch 1 though branch 2 is longer).
- **Before `startpos`**: `(?<=a{1,2})b` on `aab` from offset 2 is (2,3); `(?<!a{1,2})b` is nomatch.
- **UTF-8 counts characters**: `(?<=(é{1,2}))x` on `aééx` (UTF) is (5,6) g1=(1,5).
- **The end-check's two witnesses**: `(?<=a{1,2})x` on `abx` is nomatch (at length 2 the body ends
  at 1, not 2); `(?<!ab?)x` on `acx` matches (2,3) (length 2's body ends early, length 1 fails).

## 3. The two candidates, side by side

**B, the step-back loop** (vlbinv §3, `lookaround_design.md` §2.5's sketch). Per branch, candidate
starts are the positions `lo..hi` characters before the cursor, farthest first, clamped by the
subject start (absolute, never `startpos`: S135). Each is tried by back-step, forward body, end-check;
a failure resumes the next candidate through a retry frame, then the next branch.

**D, reverse DFA then forward VM** (owner addendum). A reverse DFA of the branch, run from the cursor
back at most the branch's width, gives the positions where the branch can start; the farthest is
tried first; one forward anchored VM run from it, required to end at the cursor, sets the captures.
Capture-free and negative lookbehinds were proposed to need the DFA only.

| vetting item | B (range source) | D (reverse-dfa source) |
|---|---|---|
| **order** (branch, then longest) | the loop's order by construction | per-branch machines: the farthest accept IS the longest step-back, the output today's reverse block already records (`emit_reverse_block`: the smallest accepting position). One machine for all branches needs priority tags (`alt_dispatch_study.md` (c)); the union without tags is WRONG: `(?<=(a)\|(aa))c` on `aac` |
| **non-atomic retry** | the retry frame stays live; next candidate = one character nearer | needs EVERY accepting start in order ([LANDWALK-ALLACC]'s output, "every accepting start ascending" = farthest first). Two forms: a re-walk from the cursor to the last tried start (stateless, O(width) per retry) or a 255-bit set per evaluation (frame storage). Re-walk recommended: retries happen only on a non-atomic form whose follow fails |
| **captures inside** | trail rewind per failed candidate, as today | the forward VM run sets them; the DFA cannot |
| **atomic / possessive inside** | `vm_emit` as today | the machine is a SUPERSET (`Nfa.erased` & `NFA_ERASED_ATOMIC`, src/ir/nfa.c `compile_ast`'s A_ATOMIC arm), so its accepts are candidates to CONFIRM, never answers. Witness §2 row 1 |
| **nested lookaround** | `vm_emit` as today | erased (`NFA_ERASED_LOOK`): superset, confirm by the VM; a lookahead can read past the cursor (§2) |
| **capture-free, negative "DFA only"** | n/a | TRUE only where the machine is EXACT (`erased == 0`) and the body has no observable side effect (no callout: `NFA_ERASED_CALLOUT` already marks it; a callout's firing count would differ). Otherwise the DFA is a sound FILTER for both polarities (no accept in the superset means none in the truth), never the answer |
| **backreference inside** (stage 2) | needs only a width (B+) | no machine: the NFA builder has no lowering for `A_BREF` (src/ir/nfa.c, `compile_ast`'s A_BREF arm, "NO MACHINE"): the row declines, `range` serves |
| **`\K` inside** | refused by both libraries (err 199), unchanged | same |
| **UTF-8** | back-step "up to hi characters" reports how far it got (a new seam entry or a loop of one-character steps: §5.1), then one character forward per retry | byte machine over UTF-8; accepts fall on character boundaries for valid input; the 255 cap is a compile-time character count; no run-time count needed |
| **start of subject** | the clamp, absolute | the walk's floor is 0, not `search_from` (the landmark walk's floor, `dfa_dir_landmark`'s `at_bound`): §4 G3 |
| **context at the start** (`\b`, `^`) | the forward body reads it | the reverse machine's views at the floor, as the RECOVER pass reads them (`rx_reverse_accepts_class`) |
| **budgets / give-ups** | `RX_CHARGE_WORK` per candidate; frames visible to D42's bound | fewer body runs, so fewer give-ups: a ONE-WAY give-up change, which [GIVEUP-DIFF] must cover before the row ships |
| **machine size per site** (proxy, `revdfa_sizes.tsv`) | none | bench body `\bnot\s{1,3}(?:\w{1,12}\s{1,3}){0,3}` ~61 states × 6 classes; `(?:a\|bc)` 3 × 4; `a{1,255}` ~257 × 3; `é{1,255}` ~511 × 3 (byte) |
| **compile cost** | none beyond today | one optional subset construction per variable branch, under its own state cap with the subset budget restored (`revend_build_one`'s shape, src/core/compile.c) |
| **host in a VM artifact** | VM records that exist today (`VK_BRANCH`, `VK_PUSH`, `VK_SEEK`, `VK_LSET`, `VK_WORK`) | no record kind runs an automaton (`VmKind`, src/gen/vm_stmt.h); see §4 G5 |
| **speed, short bodies** (widths 1..3, the whole corpus population) | ≤ 3 tiny body runs | a walk of ≤ 3 bytes plus one run, plus tables; no expected win (INFERRED) |
| **speed, the bench pattern** (negative, 4..51) | up to 48 candidates per evaluation, but each fails at the body's first byte unless it is `n` | one walk of ≤ 51 bytes; INFERRED small difference, since the lookbehind is evaluated only where `\bavailable\b` can follow |
| **stream ratchet** | adds no parallel mechanism | built now, a reverse walk inside the VM body would be a new hand-written walk beside R03/R10 (roadmap §5): rejected by D185's ratchet unless it IS the reverse `AUTO` kind |

**What the table shows.** D needs B's finisher on every body it cannot answer alone (captures,
atomic, nested lookaround, callouts, backreferences), and its finisher is exactly B's per-candidate
step: back-step to a position, run forward, end-check. So B is not a parallel path to D; it is D's
second half plus the trivial candidate source. D's own contribution is the candidate filter (fewer
body runs) and, on exact side-effect-free bodies, an existence answer with no VM run.

## 4. Is D a second client of the landmark walk?

**Not of the walk as it stands; yes of its parts; and its true home is the reverse `AUTO` kind.**

The walk today (D184): `emit_landmark_walk` (src/gen/emit_dfa.c) is the body of the LOCATE row
`landmark-walk`, registered for the DFA route only (`.u.locate.emit = { [CAND_ROUTE_DFA] =
emit_landmark_walk }`), emitted into the DFA artifact's search entry. Its machine is a Job
singleton (`Job.lmnfa`/`Job.lmdfa`, built once by `lmwalk_build` in src/core/compile.c from the cut
`PcrecLmwalk.pl` that `lmwalk_conj[]` chose, src/gen/lmwalk.c). Its admission is about landmark
soundness (`exclusion`: P never consumes a byte of L), which has no meaning for a lookbehind. Its
finisher is the anchored DFA `Job.adfa` (`dfa_dir_lmverify`), not a VM. So D cannot call it.

What D shares is what the walk is MADE of:

| part | where | reusable by D as is? |
|---|---|---|
| reverse NFA of an AST subtree | `pcrec_build_nfa(cx, ast, nfa, true, ...)` (src/ir/nfa.c), used by `lmwalk_build` on the cut | yes: the lookbehind branch is a subtree |
| optional machine build with own cap, budget restored | `revend_build_one` (src/core/compile.c) | yes (static today; one call site more) |
| exactness as a recorded fact | `Nfa.erased` (internal.h, `NFA_ERASED_*`) | yes: it is D's "answer vs filter" fact |
| the reverse scan renderer | `emit_reverse_block` → `emit_scan_loop` over a `DfaForm` (src/gen/emit_dfa.c); its callers are RECOVER's pass, the rev-end walk and the landmark walk | yes in kind; needs G2-G4 below |
| the walk's direction strings | `struct DfaDir` (`statev`, `posv`, `recv`, `at_bound`, `seed_cond`, ...), one `static const` per direction (`dfa_dir_landmark`) | needs G3 |
| the farthest-accept output | `match_start_position` = the smallest accepting position | yes: it is the longest step-back |

**What would have to be generalized** (each already named somewhere, none built):

- **G1 machine per site.** `Job.lmdfa` is one machine per artifact; D needs one (or one tagged)
  machine per variable lookbehind branch, keyed by the `A_LOOK` node. Roadmap A-REV's "one reverse
  `AUTO` kind" is the place this becomes an operand rather than a Job field.
- **G2 floor and seed as operands.** The landmark walk floors at `search_from` and seeds one past a
  hit; a lookbehind floors at 0 (S135's lesson: never `startpos`) and seeds at the VM cursor.
  `DfaDir.at_bound` and the caller's seed already carry both as strings; they become operands.
- **G3 names per instance.** `DfaDir`s are file-scope constants and `emit_reverse_block`'s comment
  says "the names stay RECOVER's spellings: the one caller that would need others (rev-inner, D151)
  is filed". Two lookbehinds in one artifact need two name sets.
- **G4 the exits.** Today: farthest accept only. D needs three: farthest (atomic), every accept
  farthest first ([LANDWALK-ALLACC]), and existence (exact negative or capture-free bodies; may stop
  at the first accept). These are three of the manifesto's declared automaton exits (manifesto §2:
  "commit to one end, enumerate ends in preference order, act as a gate, test existence, or report
  a tagged end").
- **G5 hosting in a VM body.** The VM body is written only by typed records (D182) and `VmKind` has
  no automaton kind. The precedent for DFA text in a VM artifact is the hybrid prefilter
  (`pcrec_emit_dfa_engine` emitted with `static` storage as a separate part, called from the search
  loop, src/gen/emit_vm.c's entry shape `.hybrid`); it is outside the matcher body. D sits INSIDE
  the body, between choice points, so it needs either a record kind (the reverse `AUTO` kind) or a
  per-site static helper part called from an expression record. Either is a new crossing between
  the VM body and DFA text, which is exactly roadmap A-REV's and [LANDWALK-VM]'s question (the walk
  with a VM finisher, "the VM hat").
- **G6 the finisher on the VM route.** The walk's finisher is the anchored DFA; D's is the VM
  body with the end-check, which is B's per-candidate step. B builds it.

**Why not now.** Building G1-G5 for this one row, ahead of roadmap A-REV's P-d step (the landmark
walk as records, prerequisites P-b and [VMREC] (b)), would add a third hand-written reverse walk
beside R03 (`revdet.c`) and R10 (`emit_landmark_walk`), which D185's ratchet rejects; and there is
no measured need for it (§3's speed rows, D77). Built after A-REV, D is the reverse `AUTO` kind's
first VM-hosted client, with [LANDWALK-ALLACC]'s enumerate exit, and it costs one choice row.

## 5. The mechanism

### 5.1 One branch, candidate starts farthest first

Per top-level branch `i` with character range `[lo_i, hi_i]` (from `pcrec_cwmin`/`pcrec_cwmax`, as
today), in written order:

```
L_bi:     back-step up to hi_i characters from the cursor; d = characters actually stepped
          if (d < lo_i) goto L_b(i+1)                 // the clamp: not enough subject
L_try_i:  RX_PUSH(&&L_adv_i, scan_position)            // the retry frame (one live per branch)
          RX_CHARGE_WORK(...)                          // per candidate tried
L_body_i: <B_i forward, vm_emit unchanged>  -> L_end_i
L_end_i:  if (scan_position != POS) goto rx_fail       // decline: backtracks into B_i, then L_adv_i
          goto L_ok
L_adv_i:  if (d == lo_i) goto L_b(i+1)                 // candidates exhausted
          advance one character; d--; goto L_try_i
```

`d` is a matcher slot written by `vm_set` (trailed, so a retry frame restores it). The last branch
sends its exhaustion to `rx_fail` as today. Atomic forms cut every frame at `L_ok` (`vm_cut`,
unchanged); non-atomic forms leave `L_adv_i`'s frame live, which IS PCRE2's measured retry-shorter
behaviour.

**The fold for `lo_i == hi_i` is natural, not a special case.** With a one-point range: "back-step
up to k, d < k → next branch" is today's guard plus back-step (`scan_position < k`, then the seam's
`$_back_step` of exactly k); `L_adv_i`'s first test `d == lo_i` is true on entry, so the retry frame
targets `L_b(i+1)` directly, which is today's "NEXT-BRANCH continuation" push. A loop whose
remaining trip count is statically zero has no back edge; the emitter evaluates that test at compile
time as it evaluates the `k > 0` guard test today (`vm_look_behind_branch`'s zero-width note). The
emitted COMMENT is the one place the shape is named: the one-point case keeps "fixed width %d" (it
describes what was emitted); the range case gets its own role text. Identity on today's corpus is
the gate that proves the fold (§6 stage 1, gate 2).

**The UTF-8 clamp.** Under the byte encoding `d = min(hi_i, scan_position)`. Under UTF-8, "back-step
up to k characters and report how many" is not today's seam entry (`$_back_step` returns
`_BACK_STEP_NONE` when fewer than k precede). Two spellings: a loop of one-character back-steps
through the existing entry, or a new residual entry `back_step_upto`. The seam's [M5-SEAM] per-site
count moves either way; the build lane picks by the seam's rules (D58), not this note.

### 5.2 The width rule and the cap

`la_widths` (src/parse/mod_lookaround.c) stores a range per branch (`lo`, `hi`) instead of one
`int`, and refuses only: an unbounded branch (as today, and as PCRE2, err 125), and PCRE2's cap
measured in vlbinv §1: once ANY branch varies, EVERY branch's maximum must be ≤ 255 characters
(`(?<=a{300}|b{1,2})x` refused, `(?<=a{300}|b)x` compiles). The cap is a new `limits.def` row
([LIM-1]), visible in `--list-limits`. `lb_max` takes the widest branch maximum (`la_lb_raise`),
which is PCRE2's `max_lookbehind`. The refusal sentence for bounded bodies is deleted (the
special case retired).

### 5.3 The end-check and the negative arm

The end-check is load-bearing for a varying branch: a body may end before the cursor on a correct
compiler. On the negative arm today a failed end-check returns `RX_R_INTERNAL` (ASK 2: a decline
would be a false match). For a varying branch a failed end-check is an ordinary decline on both
polarities; for a one-point branch it stays the hard return (it cannot fail on a correct compiler,
and it is the byte-identity case). One predicate decides it, "this branch's end-check can fail on a
correct compiler" iff `lo_i < hi_i`; `PCREC_ERR_INTERNAL`'s spec sentence narrows accordingly.

### 5.4 The candidate source: a declared choice row (D186)

| order | row | applies when | exit | status |
|---|---|---|---|---|
| 1 | `reverse-dfa` | the branch varies (`lo < hi`); its reverse machine builds under its own cap; no backreference/variable in the body; no callout (side effects); the host can run it (G5) | exact machine and no capture/callout: EXISTENCE (no VM run); otherwise candidates farthest first, each confirmed by §5.1's step | HELD (not built) |
| 2 | `range` | always (the total fallback) | §5.1 | stage 1 |

Fixed branches never take row 1 (one candidate; nothing to filter): its first conjunct is a fact,
not a special case. Exactness is read from `Nfa.erased == 0`, the existing fact.

**Evidence requirement for row 1 (D186 choice bar).** Per regime, `reverse-dfa` versus `range`,
answer-identical and no regime slower beyond noise: (a) short bodies, widths ≤ 3 (the whole corpus
population), hit and miss; (b) the bench pattern `negation-scope-lookbehind-var` on the bench's own
subjects; (c) a wide body whose candidates do NOT fail at the first byte (e.g. `(?<=\w{1,64}x)y`);
(d) a random-like subject regime (D186 addendum 2's condition). A losing regime narrows the row's
condition (e.g. a minimum width), never a parallel path. If the row can be slower anywhere it also
gets a public deny flag (flag follows caller effect).

**Prerequisites and trigger.** Prerequisites: roadmap A-REV's reverse `AUTO` kind with operands
for machine, seed and floor and the three exits (§4 G1-G4), hosted in a VM body (G5, [LANDWALK-VM]),
and [GIVEUP-DIFF] (the row removes work, a one-way give-up change). Trigger (D77): a measured cell
where the lookbehind's candidate tries dominate, e.g. the bench's `negation-scope-lookbehind-var`
slower than libpcre2 with the lookbehind as the cause, or any regime (c) cell in a real workload.

**One tagged machine instead of per-branch machines** is a later refinement of row 1 (one walk per
evaluation instead of up to m), riding [LANDWALK-ALLACC]'s multi-branch form and the priority-tagged
accepts of `alt_dispatch_study.md`. Not designed here.

### 5.5 Budgets and frames

`RX_CHARGE_WORK` per candidate tried (not per branch), so a `{1,255}` branch charges up to 255 per
evaluation per position, the same order as PCRE2's own work (vlbinv §5; PCRE2's cost not measured).
The retry frames are ordinary frames, counted by D42's frame bound; live frames: at most one per
branch per active lookbehind. `lookaround_design.md` §3.7's per-position note grows from `n·Σk_i` to
`n·Σ(hi_i − lo_i + 1)·hi_i` in the worst case; the long-subject leading-lookbehind cell it asked for
gains a variable twin (stage 1, gate 4).

## 6. Staging and acceptance gates

**Stage 0 (no code): D27 extract and tests first.** A spec-first author (D27, recommended: §9)
writes the cells from §7.4's revised spec text and a `vlb_d27_extract.md` cut from this note; the
oracle is libpcre2 10.46.

**Stage 1: `range` (B), capability.** Width rule + cap (§5.2), the loop (§5.1), the end-check
split (§5.3), budgets (§5.5), spec hunks (§10), the 36 real corpus rows flipped from refusal to
match cells (vlbinv §4; the `${v}` row stays refused). Gates:
1. **Oracle differential**, libpcre2 10.46 (PC-3's harness): a generated cell set, every spelling
   × {capturing, non-capturing} × {group alternation, bounded quantifier, nested quantifier, nested
   lookaround, atomic/possessive inside, call to a bounded group} × subjects hitting each length,
   the clamp, the end-check backtrack, the non-atomic retry and `startpos > 0`, byte and UTF-8.
   0 differences. The generator's population count is pinned with a floor (K35: the generator
   counts, not the harness), and the cap boundary cells (255/256, fixed+variable) are in it.
2. **Identity**: every corpus artifact containing a lookbehind, byte-identical (G2).
3. **Accept set ⊆ PCRE2's**: every cell pcrec compiles, libpcre2 compiles (0 exceptions).
4. **Budget cell**: the variable twin of §3.7's long-subject leading-lookbehind cell gives the same
   answer as libpcre2 or a documented `PCREC_ERR_WORK` at a stated subject size.
5. The sabotage rows of §7, each red in its sabotaged build, green in the correct one; S136 re-aimed.

**Stage 2: backreference width (B+).** `pcrec_cwmax(A_BREF)` = the widest group it can name (union
over duplicate names; unbounded if any is); gates 1-3 over backreference cells (`(a|bc)(?<=\1)x`,
`(?<=(a|bc)\1)x` = 4, the sum).

**Stage 3 (HELD): `reverse-dfa`** under §5.4's evidence and prerequisites; its own abi event (new
emitted text in artifacts that took `range`), tuning.md section, deny decision, witnesses WD1-WD6.

## 7. Sabotage witnesses (each can fail; floors and domains stated)

Every witness is a lookbehind, so it routes VM in both builds (all lookaround rows are `VM_ONLY`;
no admission floor applies to `range`, the total fallback). Each names the fact that makes it fail.

| id | sabotage | witness (libpcre2 10.46 answer) | why it reaches and fails |
|---|---|---|---|
| W1 | candidates shortest first | `(?<=(a\|aa))c` on `aac`: (2,3) g1=(0,2) | range 1..2 varies (not the one-point fold); the capture makes the chosen length observable: sabotaged g1=(1,2). A capture-free order sabotage changes no answer and is NOT a witness |
| W2 | end-check removed | `(?<=a{1,2})x` on `abx`: nomatch | at length 2 the body succeeds ending at 1; without the check it is a false match (2,3) |
| W3 | end-check without backtracking into the body | `(?<=(a\|ab)(b\|))x` on `abbx`: (3,4) g1=(0,2) g2=(2,3) | the first path at length 3 ends at 2; only a later path ends at 3 |
| W4 | negative arm keeps the hard return on a varying branch | `(?<!ab?)x` on `acx`: (2,3) | length 2's body ends at 1: sabotaged returns `PCREC_ERR_INTERNAL` |
| W5 | non-atomic retry frames cut | `(?<*(a{1,3}))c\1` on `aaaca`: (3,5) g1=(2,3); `(?<*(a\|aaa))c\1` on `aaaca`: (3,5) g1=(2,3) | the follow `\1` fails at length 3; only a retry reaches length 1. The second row has a gap at length 2 (distinguishes "every length" from "next accept") |
| W6 | clamp counts bytes, not characters | `(?<=(é{1,2}))x` on `aééx`, `-e utf8`: (5,6) g1=(1,5) | multibyte body under the utf8 encoding: a byte back-step lands mid-character and fails |
| W7 | clamp relative to `startpos` (S135 carried) | `(?<=a{1,2})b` on `aab` from 2: (2,3) | the body's bytes lie before `startpos` |
| W8 | cap only on varying branches | `(?<=a{300}\|b{1,2})x`: refused (err 200) | sabotaged compiles a pattern libpcre2 refuses (gate 3) |
| W9 | cap off by one | `(?<=a{1,255})x` compiles, `(?<=a{1,256})x` refused | the boundary cell pair |
| W10 | branch order lost (longest over all branches) | `(?<=(a)\|(aa))c` on `aac`: g1=(1,2) | branch 2 is longer; sabotaged sets g2 |

Stage 3's witnesses (row `reverse-dfa`), admission floor: each body below varies and its machine is a
few states, far under any cap, so the row reaches in both builds:
WD1 exactness conjunct dropped: `(?<=(?>a\|ab)b)x` on `abbx` nomatch (sabotaged: false match) and
`(?<!(?>a\|ab)b)x` on `abbx` (3,4) (sabotaged: missed); WD2 one untagged machine for all branches:
W10's cell; WD3 nearest accept instead of farthest: W1's cell; WD4 farthest only on the non-atomic
form: W5's gap cell; WD5 floor at `search_from`: W7's cell; WD6 context at the floor ignored:
`(?<=\ba{1,2})x` on ` aax` (3,4) and on `baax` nomatch.

Existing rows that move: S136 (design row S-LA11, "the width rule accepts a branch that is not fixed
width") tests a premise stage 1 removes: its `perr` cells become match cells. Its header says it is
the ONLY thing in the tree that exercises the negative arm's `RX_R_INTERNAL` return, which stage 1
keeps for one-point branches (§5.3). Re-aim it so that it still does: the analysis reports a
ONE-POINT branch's width one too large. Positive: `(?<=bc|d)x` on `abcx`, libpcre2 (3,4); the
sabotaged body starts at `a` and fails, so nomatch. Negative: `(?<!bc|d)x` on `bcax`, libpcre2
(3,4); the sabotaged body matches `bc` from 0 and ends at 2, not 3, so the end-check fires and the
matcher returns `PCREC_ERR_INTERNAL`. (A negative cell where the body fails outright, such as
`abcx`, would not reach the end-check: it declines before it, a false match, not the hard return.)
W1 then catches the variable-branch half (`hi` reported as `lo`). S135 carries unchanged (W7 is its
variable twin). Ids are the build lane's, from the range its brief names.

## 8. The population

vlbinv §4, unchanged: the 37 corpus rows are pcrec's OWN refusal pins (27 distinct patterns; 36
real, 1 false positive `(?<=${v})x`, pcrec's own variable syntax). Outside demand: ONE bench pattern
(`negation-scope-lookbehind-var`, widths 4..51). The case is completeness against PCRE2 (the
scoreboard's rank 1 gap), not measured demand. Stage 1 covers 32 rows (24 distinct) and the bench
pattern; stage 2 brings 36.

## 9. A D27 spec-first author: recommended

The level-2 order (longest first, against the emitter's usual preference-first direction) is the
rule tests derived from code inherit wrong (`lookaround_design.md` §2.5 reason 1: the [M4.6d]
counter-rung defect a blinded author found). `tests/lookaround/d27/` exists to extend. The author
gets the revised §7.4 text and a `vlb_d27_extract.md` (re-cut from this note, never edited
independently, docs/design/CLAUDE.md rule), not this note's §5.

## 10. Spec impact (D80; hunks the build owes)

- `pattern_language.md` §7.4¶5: the rule becomes "each alternative may match a bounded number of
  characters; at most 255 once any alternative varies"; the preference order (written order, then
  longest first, the body backtracking until it ends at the position) and the non-atomic retry get
  a paragraph with an example each; §7.3¶6 and §7.4¶5's backreference sentence change at stage 2.
- `pattern_language.md`'s refusal-shape table (shape 5's "variable-length lookbehind" example) loses
  the bounded case; unbounded stays.
- `limits.md` §3: the new cap row (value 255, unit characters, not overridable; [IFACE-PUSH] owns a
  setting).
- `match_api.md` §4¶6: `PCREC_ERR_INTERNAL`'s producer is the end-check of a one-point branch only.
- `match_api.md` §9.4¶2: LB is the widest branch's maximum (check the wording; the fact already is).
- Stage 3 only: a `tuning.md` §2 section for the row and its stamp, and the abi event.
- `docs/pcre2_compliance.md` via the compliance-refresh skill after landing (not spec).

## 11. The standing questions

1. **Measurement regime.** Stage 1: RELEVANT ONLY AS A BOUND, not a decision input: no number
   selects anything; G4 is a count of body runs in the emitted text. Stage 3: RELEVANT: the row's
   evidence is per-position cost of a lookbehind evaluation, hit vs miss, throughput over a
   subject, on the dev box (7700X, gcc 15.2, glibc) and through both VM entries (the tiered default
   entry and `_search_in`, architecture rule for VM capacity changes); a regime where candidates
   fail at the first byte (the bench pattern) versus one where they do not would flip the row,
   which is why both are required.
2. **Independent control.** RELEVANT. Answers are checked against libpcre2 10.46, a separate
   implementation sharing no source with pcrec; the cell generator is written from the spec and
   §2's cells, and it counts its own population (K35) against a pinned floor. Each sabotage witness
   in §7 states why it reaches its site in both builds (all VM, no admission floor on `range`); the
   stage-3 witnesses state the row's admission they clear.
3. **What moves when data is regenerated.** MOSTLY NOT RELEVANT: stage 1 adds no table, calibration
   or generated file. The one new datum is the cap row in `limits.def`: `--list-limits` gains a line,
   so its readers (the limits listing's pins, found by grep at build time) move in the same change.
   Stage 3's reverse machines are generated per artifact from the pattern; a rebuilt machine moves
   that artifact's bytes only.

## 12. The question for a pcre2-reader (D181)

Kept from vlbinv §7, one question: "In PCRE2 10.46, when a lookbehind has at least one variable-length
branch, which branches does `max_varlookbehind` limit, and how does the matcher run a variable-length
branch: does it try each step-back length from longest to shortest, re-running the branch forward
each time and backtracking inside it until it ends at the assertion point?" Its answer confirms the
cap rule §5.2 copies and the cost model §5.5 assumes; every observable behaviour is already measured.
No second question is needed: D's vetting rests on measured cells (§2), not on PCRE2's internals.

## 13. Questions for Frank (plain words; leanings are not rulings)

1. **Should today's fixed-width lookbehinds keep their exact code?** Leaning: yes. The general loop
   with one possible length folds to today's code by itself (§5.1: the loop's retry test is decided
   at compile time), so nothing moves and no abi event is owed. If the reverse-DFA form later proves
   faster for some fixed shapes, that is its own measured choice with its own abi bump (manager's
   clarification, rulings file 2026-11-05 19:45).
2. **The 255 limit**: PCRE2 lets a caller change it. Leaning: the default only, as a listed limit;
   a setting waits for the interface push ([IFACE-PUSH]).
3. **Backreferences inside a lookbehind** (`(a|bc)(?<=\1)x`): leaning: a second small step after the
   loop, since it changes a width answer other passes read.
4. **Your reverse-DFA idea (D)**, new from this note. Vetted: it works, it is the same mechanism as
   the loop with a smarter list of places to try, and it still needs the forward run whenever the
   lookbehind has captures, atomic parts, nested lookarounds or callouts. Leaning: build the loop
   now; keep D as a held choice ("where to try") that is built when the reverse-walk unification
   (roadmap A-REV) gives it a home inside the VM, and only if a measurement shows the loop is slow
   somewhere. Building it now would add a third separate reverse walk, which the stream ratchet
   forbids, for a pattern population where it is not expected to be faster.

## 14. What this note does not decide

- The UTF-8 clamp's spelling (a loop of one-character steps or a new seam entry; §5.1): the build
  lane's, under D58.
- Whether stage 1 owes an abi bump at all: by `match_api.md` §6¶19 no bump is owed when no
  previously compiling pattern moves; the manager confirms at landing with readers found by grep.
- The `reverse-dfa` row's design detail (tagged vs per-branch machines, re-walk vs stored set for
  non-atomic retries, record kind vs helper part): A-REV's and [LANDWALK-VM]'s.
- [ENG-LOOK] (lookaround inside the DFA engine), [CTX-PREFILTER], and conditional groups
  ([CONDITIONALS]) are untouched; vlbinv §5's overlap check stands.
- S-ids, file layout of tests, the generator's cell count.

## 15. Measured vs inferred

- MEASURED (this lane, dev box, libpcre2 10.46 as a library): every cell in §2 and §7's witness
  answers (`vlbdesign_evidence/*.out`); the premise (`premise.txt`).
- MEASURED PROXY: reverse-machine sizes (`revdfa_sizes.tsv`): the whole-pattern reverse DFA of a
  pattern equal to the body, from pcrec's own artifact tables; a lookbehind machine is the same
  language reversed and anchored at the cursor, so the proxy is close but not the object.
- READ from code (not executed): §4's evidence (file:function), §3's host and erasure rows.
- INFERRED: the speed rows of §3 (no timing was run), the fold's byte identity (proved only by
  stage 1's gate 2), the work bound of §5.5.
