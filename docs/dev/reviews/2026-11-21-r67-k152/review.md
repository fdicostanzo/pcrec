# Review r67 — k152 (code, LIGHT): the NFA builder's arms in their own frames (K152)

Date: 2026-11-21. Mode: code. Size: LIGHT (3 critics). Coordinator: opus (crit-k152). Dispositions are PROPOSED; the manager rules.

## Subject
- SUBJECT 62752e60cee6fe68143c217a1d4b439f3b99d30a (lane/k152fix tip; the last two commits are report-only).
- BASE 2b4e56eab6f6c24411f165f861ae76ad6790fbc4 (merge-base with main). main at freeze 047c5195f; decisions.md, plan.md,
  plan_completed.md, guide/coding.md and core/internal.h unchanged on main through hand-back (no FREEZE DRIFT).
- Scope: src/ir/nfa.c (compile_ast's arms moved into `PCREC_OWN_FRAME` functions nfa_cat/nfa_alt/nfa_rep/nfa_class/
  nfa_eol/nfa_ctx/nfa_wclass/nfa_splice/nfa_erase_by_row, trie_key marked, nfa_cat's two loops merged into one recursion
  site), tests/thread/run_compile_stack.sh (rows nclitrep, litpost, nclitpost, litcompound; the reach check looped over
  compound + litcompound), new sabotage S3470, docs/spec/limits.md §3.10¶1-¶5, the limits.def PCREC_COMPILE_STACK_BUDGET
  text, known_issues K152, plan row [K152-NFA-DEPTH], one history line.
- Rulings relied on: [K152-NFA-DEPTH] trigger (plan.md (line 2472 at the freeze) at the freeze: "same general depth mechanism, [DD-10]
  PCREC_OWN_FRAME on the NFA builder's recursive arms; with DEPTH_FAMILIES rows for the plain and the compound-route
  shape"); coding.md:198 and internal.h:366 (the mark's two uses); D80 (spec in the same change). All have records at the freeze.
- Kit: SUBJECT review tree + BASE archive built once at `nice make -j2`; one planted compiler (S3470, both pairs exact);
  stack driver = tests/thread/compile_stack_driver.c linked per tree. The coordinator's sanity run reproduced the lane's
  three headline figures (witness: BASE DIED 139, SUBJECT 306,032; plain nest 440,176 to 293,744; litpost 440,560 to 317,744).

## Lenses as run
| lens | model | question | why chosen |
|---|---|---|---|
| EQUIV (emitted vs replaced + the two standing questions) | opus | is the new NFA builder byte-identical to BASE for every pattern class; does the restructure reorder any side effect | profile: zero-mover claim on a restructured recursive builder |
| CONTRACT | opus | does restated §3.10 and the limits.def row hold figure by figure; is 317,744 B really the new worst | profile: caller-facing contract restated from measurement |
| CHECKS (check adequacy + house rules; owns the plants) | sonnet | do the new rows and S3470 fail when the fix is undone, and only then; coding.md/internal.h compliance | profile: new sabotage + DEPTH_FAMILIES rows; plain C structure |

Compile shares: 400 / 300 / 100 (used: about 368 / 185 / 26).

## Which lens caught what
EQUIV: nothing (175 BASE/SUBJECT byte-identity pairs, all SAME; the reading held line by line). CONTRACT: the §3.10 figures
that did not move with the fix, and the new worst being a pre-existing unnamed shape (F2-F5). CHECKS: three sabotage
anchors the move broke (F1), rows green at BASE (F6), partial-undo invisibility (F7), the mark comments (F8).

## Findings and PROPOSED dispositions

### F1 — the move left three mech sabotage anchors stale (CHECK-1) — maintenance/check — FIX-NOW
`python3 -I scripts/m6read_check_sab_anchors.py` in the review tree: STALE ANCHORS: 3 — S1100_collapse-drops-rmin and
S14_nbr_threshold (ANCHOR NOT FOUND), S1176_ctx_row_frag_drops_fn (ANCHOR COUNT 1, SAB_COUNT 2), all src/ir/nfa.c. BASE:
all anchors resolve. Cause: the moved arm bodies lost one indent level, so the anchors' indented text no longer matches.
Those three rows cannot apply, so mech cannot show that their suites still detect. Verified (verify.md). Reason: a moved
body's readers include the sabotage rows quoting it (the [MECH-REACH] family lesson). Fix: re-anchor the three rows on the
new text, re-check each one's count (S1176's two sites are now in nfa_ctx), and run the anchor checker plus those three
rows in the matrix.

### F2 — ¶3's "`+` or `{2}` refused after at most 312,560 bytes" is a BASE figure (CONTRACT-1) — doc — FIX-NOW
SUBJECT: `(a|b…c)+d` 190,224, `{2}d` 188,560 (BASE 314,224 / 312,560). Verified. Restate it as "at most 190,224".

### F3 — the stated worst (317,744 B) is not the worst; the capturing compound route and long distinct-letter atoms cost more (CONTRACT-3, CONTRACT-4) — doc + test coverage — FIX-NOW
At depth 250 on the budget thread, SUBJECT = BASE: `^(abcdefghijklmnopqrstuvwxyz|abcdefghijklmnopqrstuvwxy_(…abe)*)*|b$`
319,504; `^(abc|abd(…abe)*)*|b$` (the capturing compound route) 318,032. With `-e utf8` (measured with the test's own
driver plus one line setting the encoding, since the driver has no encoding parameter), `([é-ü]bc|[é-ü]bd(…abe)*)*d` costs 317,808
(BASE 440,560). These are PRE-EXISTING shapes, never the K152 peak, but the subject restated the worst. The margin
sentences hold (442,368 / 319,504 = 1.385 >= 1.2), but limits.def's "1.39x today, 317,744 bytes" and ¶3's "measured worst
… 317,744" are false by up to 1,760 B. The critic's figure for the utf8 nest ("~4-8 KB over") came from CLI runs under `ulimit -s` and was PARTLY
refuted: it is 64 B over (verify.md). Fix: restate the worst as measured (319,504; say what it depends on: the
compound route and distinct letters in the atoms), "1.38x"; name the capturing compound shape in ¶3; add a DEPTH_FAMILIES row for
the capturing compound nest (¶2 says test-stackdepth compiles the families ¶3 names). For utf8: PLAN (below, F9).

### F4 — ¶3's search-code figures do not reproduce on either tree (CONTRACT-2) — doc, pre-existing — FIX-NOW (cheap; ¶3 is being restated anyway)
`abc` / `a` / `(a)` at depth 0: 38,448 / 36,864 / 40,848 on SUBJECT and BASE (features all or NULL; engine 2 about 41 KB). Stated:
24,120 / about 62 KB, and in the opposite order. The text dates from d11814f49 (2026-10-22) and the tree has changed since. The conclusion
(paid after the parse, a compile uses the larger of the two) is unaffected. Re-measure and restate.

### F5 — ¶4's lookahead item reaches 88 only with the element, but is written without it (CONTRACT-5) — doc, pre-existing — FIX-NOW (trivial)
`(?=a|b(?=a|b…c)*+)*+` on 131,072: depth 87 passes, 88 dies; with `d` 88 passes. Spell it with the `d` like the other items.

### F6 — three of the four new rows are green at BASE and on the S3470 plant (CHECK-2) — check/doc — DOC
At 442,368: nclitrep, litpost and nclitpost pass on SUBJECT, BASE and plant:S3470 (440,176 / 440,560 / 440,560 at
BASE). Only litcompound dies at BASE and on the plant (exit 139, confirmed). The three rows guard headroom against another
compiler (litpost died on CI before the fix), not the undo. The S3470 header is honest about this, but the
DEPTH_FAMILIES comment does not say it. Fix: one clause in the comment ("green at BASE: these guard headroom; litcompound is the undo witness").
Headroom now: 28-34% on all four.

### F7 — a partial undo is invisible to every check (CHECK-3, SUSPECTED for the partial plants) — check — NOTED, + PLAN note on [LINT-FRAME]
SAB_COUNT 10 / COUNT2 1 are exact. The lane's own plant measurements say each piece alone (marks dropped, or nfa_rep alone
inlined) leaves the deepest row at 408,560 B, 7.6% under the budget. run_compile_stack.sh reads the budget, not headroom, by
design (the family's stance), so such a regression is silent. EQUIV's unlock 1 is the general answer: a per-function
`-fstack-usage` frame census of recursive dispatchers (compile_ast 384 to 32 B is measurable directly). Proposed: a note on
[LINT-FRAME] naming compile_ast's frame as a witness, trigger as that row's own. No build now.

### F8 — two marks name no use, and one header undercounts (CHECK-5) — doc — FIX-NOW (trivial)
internal.h:366 says "Mark an arm for either reason, and say which in its header". `trie_key` (nfa.c:588) is newly marked and its header names
no use. The leaves nfa_class/nfa_ctx/nfa_wclass share a group comment ("the others are leaves") that is neither stated use: they are
kept out of the dispatcher's frame, which is the second use read for a leaf; say so. nfa_cat's header says "these three arms" while
ten functions are marked. "Bodies moved verbatim" is false for nfa_cat (its own header admits the merge) and, after F1, false in
whitespace for all of them. One clause each.

### F9 — test-stackdepth cannot measure `-e utf8` (CONTRACT-4, coverage part) — test coverage — PLAN
compile_stack_driver.c sets features and engine only, so no DEPTH_FAMILIES row can reach island/wide-class builds. Its utf8
class nest is today 64 B over the stated worst (F3), and it reached 440,560 at BASE. An ENCODING argument to the driver
(one line) and one utf8 row would close it. Propose as a row note under [GROWTH-SWEEP], or fold it into F3's fix lane if the
manager prefers (it is a test-harness edit, not a product change).

### F10 — sibling: vm_rev_emit has the same inlined-dispatcher shape (EQUIV, standing question) — NOTED
src/gen/emit_vm.c:5668 `vm_rev_emit`: a kind switch with CAT/ALT/REP arms inlined, 288 B frame, plus vm_revdet_rep 720 B,
on the lookbehind-body path. Measured: `x(?<=(?:a … b …))y` at depth 100 peaks at 66,960 B, and depth 250 is refused by the
group-depth limit, so it is not over budget. Other recursive walks over 200 B (ps_node 288, co_walk 304, anf_list 320,
item_first 352, req_site_define 672): six depth-250 probes all at or under 257,792 B. No witness. Trigger to mark
vm_rev_emit: a DEPTH_FAMILIES row through a lookbehind body above half the budget, or a raise of PCREC_MAX_GROUP_DEPTH.
List it on [LINT-FRAME].

## General form and unlocks (EQUIV)
General form: no recursive walk's frame holds more than its own arm's locals, a per-function invariant that `-fstack-usage`
already measures. Unlock: the frame census on [LINT-FRAME] makes the marking checked rather than trusted (internal.h: "nothing
checks the marking itself"), and it catches F7's partial undo, which the budget-thread check cannot. Trigger: the next
K-row of this family, or a new kind-switch walk.

## PROBED-AND-HELD
- Byte identity BASE vs SUBJECT, `cmp` of rx.c: default 65/65, `--engine=vm` 33/33, `--engine=dfa` 28/28 (+5/5 identical
  refusals), `-e utf8` 20/20 (N_WCHAR reached), K152/neighbour nests at depths 2/10/60 20/20 (+4 identical refusals, incl.
  the NFA-state cap raised inside nst): 175 pairs, all SAME. Every moved arm and both build directions reached
  (nfa_eol, nfa_splice, nfa_erase_by_row, nfa_ctx, nfa_wclass, reverse machines). Oracle: 3 matchers, 20/20 subjects agree with libpcre2.
- Reading: nfa_cat's merged loop reproduces the old forward and reverse orders exactly (nsp >= 1 always); every other body
  verbatim including in_tail/splice_depth brackets, ctx_fail paths, the island early return, and the A_WCLASS/A_CALL fall-throughs. Frames
  (gcc -O2 -fstack-usage): compile_ast 384 to 32 B; nfa_cat 176, nfa_alt 160, nfa_rep 224.
- §3.10 on SUBJECT: 43 ¶3 figures reproduce exactly (bar F2/F4); per-level rates hold as approximations; ¶4's 26
  depth/depth+1 pairs at 131,072 hold (bar F5); "at least 20%" holds over every shape found (worst 319,504). 0 of 149
  SUBJECT shapes at depth <= 250 died on the budget thread.
- S3470: both pairs exact, the plant rebuilds the BASE frame (440,176 plain), litcompound dies on it (139). The litcompound reach
  grep discriminates (15 `"compound"` hits vs 0 on the uncompounded control).
- Depth 251 refusals identical on all three trees (122,152 B).
- Witness depth range: 0 to 251; byte-compared nests up to 60, stack probes up to 251.

## By-id completeness
EQUIV: none (sibling/general form -> F7, F10). CONTRACT-1 F2; CONTRACT-2 F4; CONTRACT-3 F3; CONTRACT-4 F3 + F9 (PARTLY);
CONTRACT-5 F5. CHECK-1 F1; CHECK-2 F6; CHECK-3 F7; CHECK-4 held (PROBED-AND-HELD); CHECK-5 F8.

## Recommendation
No answer-level or speed-level findings; zero emitted-byte movers held. Proceed to landing after one fix lane (sonnet) for
F1 (gating: stale anchors break mech's coverage of three rows), F2-F5, F6 and F8 (doc text plus one DEPTH_FAMILIES row), with the anchor
checker, `make test-codegen` unaffected (no abi), and test-stackdepth re-run. F7/F9/F10: plan notes.

## Lessons for the guide
- A MOVE of a function body (re-indent) is a sabotage-anchor event: the code-mode check lens ran the anchor checker
  because the skill says to "when the subject deletes or respells kit or src text"; a move IS a respell. Worth saying in
  coding.md's PCREC_OWN_FRAME paragraph: "moving an arm out re-indents it; re-run m6read_check_sab_anchors.py".
- When a fix makes one shape cheaper, the "measured worst" becomes whichever pre-existing shape was second, and nobody
  has measured that one. A contract lens should hunt the NEW worst over pre-existing variants (letters, wrappers,
  encoding), not only re-run the stated figures. F3 was found that way.
