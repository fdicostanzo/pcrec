# spandir: forward DFA spans vs reverse walks, where code and tables unify and where they do not

Lane spandir (opus, 2026-11-06), STUDY only (no build go; nothing under `src/`, `cli/`, `lib/`,
`memfn/`, `tests/` touched). Worktree `worktrees/spandir` at main ad4ead990. Evidence:
`docs/dev/lanes/spandir_evidence/` (the census script, its summary, the lookbehind-branch table,
the non-zero artifact rows). Line anchors are at ad4ead990; re-grep the symbol if they moved.

## The answer, in plain words (for Frank)

**Forward and reverse spans are already one mechanism in the DFA.** The "spans" of the forward DFA
are two things: the scan edge (a counted run of one class collapsed into a loop, `[OPT-5]`) and the
stay skip (a state that loops on most bytes, M2.1). Both already run on the reverse machines, and
through the same code: one analysis pass, one emitter, one kit site. Direction is a handful of
strings (which way the cursor moves, which byte is next, where the floor is) plus one yes/no fact in
the analysis. In the corpus today the reverse machines carry 857 spans against the forward side's
1,275, and the bench 171 against 253. Frank already ruled this structure for the reverse walk
(D161 addendum 17: the reverse DFA is the scaffolding, scan edges are the optimization inside it).

**Your reverse loop span needs no new mechanism.** `(?<=a{1,254}b)`'s reverse automaton is a
chain of states on `[a]`, and the existing pass turns it into "skip backward over `a`, at most 254".
I compiled that branch's reverse machine and the edge is there (a census plant). The span reaches
lookbehind for free when lookbehind uses the reverse DFA (A-REV's proof step, S3), provided the walk
goes through the shared renderer, which A-REV already requires. The one piece of real work is that
the floor of the backward span is written as a literal (`rewind_position > search_from`). A-REV's S1
already moves that literal into the record's `bound`, which a lookbehind needs anyway (its floor is 0,
then the last candidate + 1).

**Where unification would be wrong.** Prefilters and landmark searches exist only forward: they
choose where a forward scan starts, and a reverse walk always starts at a known position. The two
ends of the subject are not mirror images either. At the end of the subject no byte follows, so the
accept there is the plain one. At a reverse walk's floor a byte usually does exist (it is just outside
the window), so the accept must read it. The VM's span loops have no reverse twin, because the VM
never consumes backward except in revdet. Forcing any of these into one direction-parameterized
function would add flag checks for no shared behaviour.

**The real limit is the same in both directions, and it is not direction.** A scan edge today needs
every byte outside the run's class to go to ONE state. So it applies only where a run ends the
pattern (or ends the reverse walk). The bench's lookbehind body
`\bnot\s{1,3}(?:\w{1,12}\s{1,3}){0,3}` gets 0 reverse spans for that reason. `^[a-z]{2,12}(?:\s|;)`
gets none in either direction (probed). The emitter's own soundness argument looks like it needs
something weaker: the run's states must agree on where each outside byte goes, not send all of them to
one place. That is SUSPECTED, not verified (no build go). If it holds, it widens forward and reverse
together. It is the general form worth a measurement, not a reverse-specific span.

**Recommendation.** No unification lane. Ride along: fold the two stay-skip functions into one
renderer when S1 folds the `DfaDir` copies (deletes one function), and let S3 inherit the spans.
File the exit-row widening as a direction-neutral candidate, with a compile-only census as its
first step. Keep prefilters, the end accepts, VM spans and revdet apart (§4).

## 1. Premise test: forward DFA spans exist (confirmed)

| span | chosen by | emitted by | kit site |
|---|---|---|---|
| scan edge ([OPT-5]): a counted (`{m,n}`) or unbounded (`*`/`+`) chain of states over one class SET, collapsed to one loop carrying only the cursor | `src/opt/scanedge.c` (`pcrec_scanedge_dfa` :568), a property of the final transition table, run on every walked machine | `emit_scan_edge` (src/gen/emit_dfa.c:12841), reached from `emit_scan_loop` (:13244) | `DELEG_EDGE` (src/gen/memfn_sites.def:69), MF_OP_SKIP / MF_H_ADVANCE, built by `edge_advance` (:12818) |
| stay skip (M2.1): a state that stays put on ≥ 192 of 256 bytes | `pick_skip_states` (emit_dfa.c:5092), called once per form in `dfa_form_derive` (:13018) | `DfaDir.emit_skip`: `dir_fwd_skip` (:9218), `dir_rev_skip` (:9249) | `DELEG_STAY` (memfn_sites.def:67), built by `stay_advance` (:9195) |

Emitted forward spans were counted in the census (§3): corpus 1,275 edges and 117 stay skips over
4,804 compiled artifacts.

## 2. Inventory and the overlap verdict per piece

Verdict words: **UNIFIED** (already one piece, direction a parameter), **UNIFY** (same semantics, two
spellings today, fold), **SHARE** (one table or rule, two renderers), **KEEP** (genuinely different),
**SUSPECTED** (rests on reasoning not checked by a build or a run).

| # | piece | forward | reverse | verdict | why, concretely |
|---|---|---|---|---|---|
| 1 | scan-edge shape analysis | `pcrec_scanedge_dfa(cx, &job->dfa, …, true)` (src/core/compile.c:3154), `adfa` (:421), `nedfa` (:444), the lowered `xdfa`/`xadfa` (`revend_build_one` :454, called :493/:498) | `rdfa` (compile.c:3156), lowered `xrdfa` (:495), landmark `lmdfa` (:555) | **UNIFIED** | One pass, one criterion (preconditions (1)-(8), scanedge.c header). Direction enters as ONE fact, `end_is_exit` (scanedge.c:562-578): only a walk that ENDS at `n` may admit END-viewed members ([OPT-VEDGE]). It is a fact about the walk, not a `reverse` flag. Under the record it is read from the walk's direction and bound. |
| 2 | scan-edge emitter | `emit_scan_edge` with `dfa_dir_forward`/`anchored`/`lmverify` strings | the same function with `dfa_dir_reverse`/`landmark` strings | **UNIFIED** | The `DfaDir` comment (:5832-5843, at `scan_more`) says why only two direction strings were needed: `scan_more` (the bound test) and `scan_back` (`pos - 1` forward, `pos + 1` reverse: the last chain position once the cap is reached). Plus the existing `advance`, `peek`, `posv`, `statev`. No `emit_scan` method per direction. |
| 3 | edge/skip kit site | `DELEG_EDGE`, `DELEG_STAY` with `.reverse = 0` | the same sites with `.reverse = 1` (`edge_advance` :12829, `stay_advance` :9210) | **UNIFIED** (contract); the SIMD forms do not exist yet in either direction | The kit's ADVANCE contract is direction-neutral: its range IS pcrec's `more` text (memfn.h ADVANCE note, Q-G2-5), so the kit tests no bound of its own. Only the generic row renders ADVANCE (memfn/src/generic.c:704). `reverse` is refused only at stride > 1 (memfn/src/compose.c:524, "no customer", D77). The SIMD rows (`vrun.c`) refuse reverse ("the blocks ascend", vrun.c `VRUN_SERVES`), but they are FIND rows, not ADVANCE rows. |
| 4 | stay-skip selection | `pick_skip_states(d, prefilter_owns_start ? s0 : -1, …)` | same call | **UNIFIED** | The only asymmetry is `prefilter_owns_start`, a ROLE fact (the search scan's prefilter owns `s0`), already split from direction at [ENG-ABS] (DfaDir comment :5798-5806). |
| 5 | stay-skip emitters | `dir_fwd_skip` (:9218): the D11 view bound inside the run's `more` (`scan_position + 1 < subject_length` under a view) | `dir_rev_skip` (:9249): the view bound as an ENTRY guard (`rewind_position + 1 < subject_length`), because the reverse cursor only decreases; `more` = `scan_more` | **UNIFY** (small) | Same skip, same kit site, same accept store. They differ only in where the view bound sits: inside the loop going forward, once at entry going backward (a monotone cursor needs one test). That is a fact of (direction, bound), so one renderer can place it. Carrier: S1, which folds every `DfaDir` function member into the record's renderer. Deletes one function. It does not move R28' (R28' counts `DfaDir` DEFINITIONS, not member functions). |
| 6 | the accept at the bound | `dir_fwd_bound_accept` (:9274): at `pos == n` the accept is SCALAR (no byte follows) | `dir_rev_bound_accept` (:9297): at `search_from` it is CLASS-INDEXED on `subject[search_from − 1]`, scalar only at `search_from == 0` | **KEEP as two rows of one rule** (do not parameterize the function) | Semantically ONE rule: "does a byte exist beyond the bound? then read its class, else the plain accept". Going forward the bound is always `n`, so the answer is always no. Going backward it is yes except at 0. A forward walk bounded short of `n` (a kit window, a lookahead-as-check part) would need the class-indexed arm too. So the rule belongs to the BOUND REFERENCE's kind, not to direction. Unify the RULE when that first forward-bounded-short walk appears (trigger, §5 U5); until then the two functions are honest. |
| 7 | seeds / entry | `seed_cond`/`seed_byte` NULL (the seed reads `subject[from − 1]`, [K82]) | `match_end_position < subject_length` / `subject[match_end_position]` | **UNIFIED by strings; S1 types them** | The context byte is the one AFTER the start going backward and BEFORE it going forward. Same mechanism 4; the position is the record's `from`. arev.md §2.1 already lists these strings among the five floor spellings S1 moves. |
| 8 | the shared walk body | `emit_scan_loop` for forward scan, anchored, lmverify, retry | `emit_scan_loop` via `emit_reverse_block` (:13409; RECOVER, rev-end two-seed, landmark) and directly from `emit_rev_end_one_seed` (:14022) / `_tagged` (:14081) | **UNIFIED** (the body); the seed code outside it is A-REV's R28' (ii) | Already arev.md §1's finding. Spans ride the body, so every reverse walk has them. |
| 9 | prefilter / landmark finds (`PF`, `OFS`, `PRE`, `MLINE`, `COVER`, `LMHIT`) | forward FIND sites | none | **KEEP** | A prefilter chooses where a forward scan BEGINS. A reverse walk begins at a known position: a forward accept, a hit + 1, a seed, a cursor. The kit rows say the same (`pffind.c`, `ofsskip.c`, `precheck.c`, `window.c` all refuse `reverse`). A reverse "prefilter" would be a backward FIND for a rare byte below the cursor. No walk has a role for one (`memrchr` has no client). |
| 10 | VM span loops (`VMSPAN`, `VMSTRIDE`; `vm_span_advance` emit_vm.c:4799, the cursor rung) | forward, structural (AST), strided | none | **KEEP apart from reverse**; A-SKIP owns DFA↔VM | The VM consumes backward only in revdet (W4). A-SKIP's end state (roadmap A-SKIP) unifies the two HOSTS (one SKIP record, one renderer body), not the two directions. |
| 11 | revdet's backward step (W4, `vm_rev_emit` emit_vm.c:5521) | n/a | one `if (cur > floor && TEST) { cur--; goto …; }` per reversed node; an exact count is REPLICATED (`A_REP` arm) | **SHARE the kit site if ever; no build** | A run of k identical backward steps is a reverse ADVANCE at stride 1 capped at k: the kit's existing `reverse = 1` W=1 contract. Census: 4 corpus artifacts carry a run of ≥ 2 identical backward steps (all 2 bytes: `(a\|bb)+`), 0 bench (§3). No population. Trigger in §5 U4. |
| 12 | the lookbehind branch L (A-REV S3) | n/a | a TABLE walk through the record's renderer (arev.md §2.1, `rendering = table`) | **UNIFIED by construction**, if S3 keeps that rendering | Its edges come from item 1's pass on the branch's reverse machine and item 2's emitter. Census plant `a{1,254}b`: the reverse machine carries a bounded edge (MEASURED). Two conditions: (a) the floor strings become the record's `bound` (`ZERO`, then `CANDIDATE + 1`), which is S1's fold; (b) the lookbehind's `from` selects views by position (arev.md A3), so precondition (6) (no head may be a view target) and (3) apply exactly as on RECOVER's machine. Nothing new to argue. |
| 13 | vlookbehind_pieces' HELD backward span count | n/a | a table-free count of `x` backward from `cursor − \|F_right\|` | **SHARE (a rendering row), never a second mechanism** | It is the scan edge with the automaton elided: one class, a count bound, a moving floor. arev.md §5 already files it as a constant rendering of the A-REV kind. If built, it must be a row of the record's rendering axis that emits through the same kit ADVANCE site (`reverse = 1`, `span_hi = hi`). It must not be a second analysis that finds `x{lo,hi}` on the AST while scanedge.c finds the same chain on the table. That would be the parallel mechanism the general-mechanisms memory forbids. Its HELD trigger is unchanged. |

**Trace and identity.** Nothing above moves a byte unless built. Item 5's fold is byte-identical by
construction: the text each direction prints is unchanged, only the function that prints it changes.
It rides S1's 0-mover gate (`emit_sweep.py`). Item 12 moves bytes only inside S3's own abi event.

## 3. The census (compile-only, MEASURED at ad4ead990)

`docs/dev/lanes/spandir_evidence/census.py`, run single-process under `nice -n 19` (the brief
forbade the box lock; a make test held the box and no timing job ran). It compiles each pattern once
and counts emitted spans in the C text. Final line: `spandir-census: COMPLETE plants=8 corpus=5242
bench=356 lb_branches=150` (8 plants, 0 red). Populations: every `tests/**/*.rxt` pattern block
(`--list-source`) and pcrec-bench's patterns, read-only, deduplicated within each population
(scensus's loader).

**T: spans emitted today, by direction** (artifacts-with / total distinct (machine, state)):

| | corpus (4,804 compiled; 2,597 DFA, 2,207 VM) | bench (330 compiled; 244 DFA, 86 VM) |
|---|---|---|
| forward edges, bounded | 253 / 376 | 74 / 203 |
| forward edges, unbounded | 439 / 899 | 29 / 50 |
| **reverse edges, bounded** | 212 / 278 | 51 / 154 |
| **reverse edges, unbounded** | 490 / 579 | 14 / 17 |
| forward stay skips | 64 / 117 | 20 / 46 |
| **reverse stay skips** | 35 / 38 | 20 / 26 |
| edges by machine | forward 600, anchored 479, retry 190, lmverify 6; **reverse 800, landmark 57** | forward 85, anchored 154, retry 14; **reverse 169, landmark 2** |

The reverse machine carries MORE edges than the forward search machine in the corpus (800 vs 600).
That matches r48sem's finding quoted in [OPT-5]'s closed row: the forward search machine's
start-anywhere threading breaks its chains, and the reverse and anchored machines keep them. A VM
artifact's spans here are those of its capture-erased prefilter pair (same emitter).
APPROXIMATION: the count is of EMITTED spans. A route that emits no reverse walk (`pinned`,
`end-minus-width`, `landing`) hides its reverse machine's chains, so the reverse numbers are a floor.

**R: revdet backward walks (W4).** 61 corpus artifacts carry 62 walks; 1 bench artifact. A run of ≥ 2
line-adjacent identical backward steps (an exact count of one class, or a repeated literal) appears in
**4 corpus artifacts** (`(?:(a|bb)x)+\1`, `(?:(a|bb)x)+\1y`, `(a|bb)+`, …; every run is 2) and **0
bench**. APPROXIMATION: text adjacency, plant `(?:(a)bb|(c)d){1,8}e` checked.

**L: lookbehind branches** (each top-level branch of each lookbehind body, compiled alone with
`--engine=dfa --no-captures` and the start rows that skip the reverse pass denied, so the branch's
reverse machine is always walked; a PROXY, the script header says why):

| | corpus | bench |
|---|---|---|
| distinct branches | 139 (117 compiled, 22 refused: `\x{…}` past U+00FF in byte mode, etc.) | 11 (10 compiled, 1 refused) |
| with a REVERSE bounded edge | **4**: `a{1,255}`, `a{2,3}`, `a{0,3}`, `a{2,}` | **0** |
| with a REVERSE unbounded edge | 6, all unbounded refusal pins (`a*`, `a+`, `a*+`, `(?>a*)`, `a*?`, `a{2,}`) | 0 |
| with a FORWARD edge (same branches) | 17 bounded, 5 unbounded | 1 bounded (the bench body, 2 edges) |
| with a stay skip, either direction | 0 | 0 |

So the reverse automata of today's lookbehind population have almost no span-able shapes, and those
they have are toy widths. Stay skips cannot appear on a lookbehind branch: its language is finite, so
its machine has no self-loop. The only outside-demand body (`negation-scope-lookbehind-var`) gets 2
forward edges and 0 reverse ones: in its reverse machine every counted run exits to more than one
state (the plain-words answer above; §5 U1). vlbinv's widths agree: every corpus row but the 1..255 cap pin has width ≤ 3
(vlookbehind.md §8).

**Measured vs read.** MEASURED: every number in this section, the plants, the probe that
`^[a-z]{2,12}(?:\s|;)` and `(?:\s|;)[a-z]{2,12}$` get no edge in any machine under `--engine=dfa`.
READ (code at ad4ead990): every verdict in §2. INFERRED: the exit-row generalization's soundness
(SUSPECTED, §5 U1); the speed of a reverse edge on its own (never measured separately: [OPT-5]
STEP 1's letters win (2.71x/3.03x) was whole-search with both passes scanning, and O-14 attributed
the ×2.0 residual to the reverse PASS, not its loop form).

## 4. How this lands relative to A-REV

- **S1 (the record) carries the unified span's only owed change.** The reverse edge's `scan_more`
  (`rewind_position > search_from`), the stay skip's view guard and the two bound-accept spellings
  are among the five floor strings S1 moves into `bound`/`from` (arev.md §1, §2.1). After S1 a span
  reads its floor from the record, which is what a lookbehind's `ZERO` / `CANDIDATE + 1` floor needs.
  Item 5's fold (one stay-skip renderer) belongs in the same step. Deletes: `dir_fwd_skip` or
  `dir_rev_skip` (one of the two), and the literal floors inside the span emitters. Bytes: 0.
- **S1M (the machine table).** No span work. The scan-edge pass runs per machine at build time, so
  every entry the table holds carries its edges. The `end_is_exit` argument becomes a read of the
  entry's direction (all walked machines go through `pcrec_scanedge_dfa` today, item 1).
- **S3 (the proof step).** The lookbehind branch inherits edges with no span code of its own. Its
  gate already includes `emit_sweep.py` and the four regimes. Its census reality: 4 corpus branches
  and 0 bench branches would carry one. So the proof step will exercise the reverse span on synthetic
  cells only, unless U1 lands first.
- **S2 / S4 / S5.** No span content. S2 puts revdet's STEP on the record. A reverse W=1 ADVANCE for
  a replicated exact count would be a rendering choice inside it (U4, no population).
- **Ratchet** (roadmap §5). R28' (5), R03' (3), R10' (1) do not move from anything here: spans add
  no `DfaDir` definition, no reverse seed code and no host loop. No row counts "direction-specific
  span analyses", and none is needed while there is one (item 1). If a reverse-only span mechanism
  were ever proposed (the backward span count as its own analysis, item 13), it would be R02's
  family (A-SKIP: two shape analyses), and R02 must not rise for it.
- **The kit seam (D157 facts, not methods).** For a span in either direction pcrec already states,
  through `PcrecAdvance` → `mf_site`: the byte set (`set`), the direction (`reverse`), the count cap
  (`span_hi`, MF_SPAN_UNBOUNDED for `*`), who owns the counter (`count_by_caller`, `count_start`), the
  stride, and the hooks `more`/`peek`/`step`/`cursor`. Nothing names a method. The one fact a FUTURE
  SIMD ADVANCE form would lack, in BOTH directions, is the bound as a POSITION (`n` going forward,
  the floor going backward) rather than opaque `more` text: a block load must know how far it may
  read. That is a direction-neutral addition to request when the kit first proposes a SIMD ADVANCE
  row (D77: not now). Backward loads, `memrchr`-style forms and last-set-bit scans are the kit's choice
  under that fact (D146), never pcrec's.

## 5. Recommendations, the general form, unlocks with triggers

**Unify (ride-along, no lane of its own):** item 5, the two stay-skip renderers → one, with the view
bound placed by (direction, bound). Carrier: S1. Trigger: S1's own (the first change opening a DFA
walk).

**Share (a rule or a site, two renderers):** item 6, the bound accept as one rule keyed on "a byte
exists beyond the bound". Trigger U5: the first FORWARD walk bounded short of `n`. Item 13: the
backward span count, only as a rendering row of the A-REV record over the EDGE/ADVANCE site.

**Keep apart:** prefilters and landmark finds (item 9, forward roles), VM span loops (item 10, no
reverse VM), revdet's step (item 11, no population).

**Already unified, nothing to do:** items 1-4, 7, 8, 12.

**The general form.** A span is "advance the cursor over a byte set, at most N times, toward a
bound". It is stated as (set, direction, cap, bound, counter owner) and found as a property of a
transition table (scanedge.c) or of a structural body (the VM's `vm_det_seq`). Direction is one
field of that statement, and its only semantic consequences are the step-back sign, whether the walk
ends at `n` (the END-view relaxation) and whether a byte lies beyond the bound (item 6). That form
exists today for the table walks. A-REV's record makes the bound a typed reference, and A-SKIP makes
the host (DFA or VM) a parameter.

**Unlocks, each with its trigger:**
- **U1, the exit-row scan shape (both directions; SUSPECTED sound).** Precondition (1) today
  requires every byte outside the set C to go to ONE state E. The emitter's own argument (scanedge.c
  header, (1)) needs only that the head can stand in for any member at the step that follows the
  scan. That holds when all members AGREE on the target of each outside class (equal rows outside
  C) and on the accept bit. It does not need every outside class to share one target. Under that
  reading `^[a-z]{2,12}(?:\s|;)`, `\w{1,12}\s`-style runs and the bench lookbehind body's runs would
  become edges (all probed today: 0 edges). It is direction-neutral, so it widens forward and reverse
  together. That makes it the real answer to "more reverse spans". Not verified: preconditions (6),
  (7) (cascades: a fall-through that is another head) and (8), and the `is_stop` sentinel layout,
  must be re-argued, and a sabotage row planted (S213 is the current criterion's loosening witness).
  Trigger: a measured cell where a counted class run FOLLOWED BY A CONTINUATION is hot (bench
  `bounded`/`loglines`). First step: a compile-only census on a scratch probe build (never landed)
  counting the chains the relaxed test admits, by direction and by machine. Owner: [OPT-5]'s
  successor rows ([OPTLOOP] candidates). Check plan.md for a row first; none was found under
  "uniform exit", "multi-exit", "exit row" or "scan-shaped" at ad4ead990.
- **U2, lookbehind spans.** Free at S3 (item 12). Trigger: S3's own.
- **U3, a SIMD ADVANCE row (either direction).** Kit-owned ([OPT-SIMD]; the scan-edge's named SIMD
  slot, emit_dfa.c axis I comment). pcrec adds the bound-as-position fact (§4). Trigger: the kit's
  measurement of a run-extension form beating the scalar ADVANCE (D147 layers).
- **U4, revdet's replicated counts as a reverse ADVANCE.** Trigger: a revdet widening that admits an
  exact count m ≥ PCREC_MIN_SCAN_CHAIN of one class with a measured cost. Today 4 corpus artifacts,
  all m = 2, 0 bench.
- **U5, the bound accept as one rule.** Trigger: the first forward walk whose bound is short of `n`
  (a kit window part, or lookahead-as-check, arev.md §5).
- **The caution on record.** M2.10 measured a REVERSE stay skip (a backward byte-at-a-time skip loop)
  27% slower than the reverse table walk on one case and reverted it (emit_dfa.c:5082-5091, D13: "do
  not re-attempt without measuring the REVERSE machine specifically"). Any widening that adds reverse
  stay skips (U1 does not; it adds edges) owes that reverse-specific measurement.

## 6. Open questions (leanings are not rulings)

1. **File U1 (the exit-row scan shape) as an [OPTLOOP] candidate row, held on its trigger?** It is
   the one change that would give lookbehind (and the forward DFA) real spans. Leaning: yes, held,
   with the compile-only census as its first step. The census is cheap and answers whether the
   population is worth a soundness round.
2. **Put item 5 (one stay-skip renderer) into S1's scope explicitly?** Leaning: yes. It is the same
   kind of fold S1 already does to the `DfaDir` copies, and it costs no bytes.
3. **Re-word vlookbehind_pieces' HELD backward span count as a rendering row of the A-REV record (not
   a candidate source with its own analysis)?** Leaning: yes, at vlookbehind's adopting revision
   (arev.md §3.1, ruling 1), which is where its home is already written.

## 7. Standing questions (docs/design/CLAUDE.md)

1. **Measurement regime: NOT RELEVANT for timing.** No time was measured. The census is compile-only
   and counts emitted text. The one speed fact cited (M2.10's reverse-skip regression) is quoted, not
   re-measured.
2. **Independent control: RELEVANT.** The census counts spans in the EMITTED C, not in the pass's own
   annotation, so it does not share a source with scanedge.c's decision. Eight plants (both
   directions, a negative control `([a-z]|[0-9]X){0,8}`, a revdet run, two lookbehind branches) are
   compiled by the same code and turn the run RED on a mismatch. Limits, stated: text regexes, and the
   reverse counts are a floor (§3).
3. **What moves when data is regenerated: NOT RELEVANT.** No table, set or stamp is introduced. The
   evidence regenerates from `census.py --root <worktree> --out <dir>`, and nothing reads it.

## STATE AT HANDOFF

- **STATE: delivered.** Study complete; no code touched; nothing owed.
- Commits on lane/spandir: the census script (WIP), then this report, its evidence and the history
  index line.
- Evidence: `docs/dev/lanes/spandir_evidence/census.py` (the instrument),
  `summary.txt` (its output at ad4ead990), `lookbehind_branches.tsv` (150 branches),
  `artifacts_nonzero.tsv` (artifacts with any span or revdet walk; the full per-artifact table stayed
  in scratch). Reproduce: `python3 -I docs/dev/lanes/spandir_evidence/census.py --root <worktree>
  --out $PCREC_TMPDIR/scratch/spandir/full` after `make` (about 4 minutes single-process). Count it
  as a sweep over 50 compiles when the box is busy.
- Rulings file `docs/dev/lanes/spandir_rulings.md`: empty at every read (last read before this
  report); no ruling applied.
- No DELIVER block (`spandir_deliver.txt`) exists for this lane, so lanecheck was not run against
  one.
