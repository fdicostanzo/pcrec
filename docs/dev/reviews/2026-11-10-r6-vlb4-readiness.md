# crit-vlb4 readiness — vlookbehind rev 5.1 stage 2 (V1-V7)

Subject: lane/vlbrev51 @ 53c9c9561 (diff base lane/vlbrev5 @ 5a2595601). Build tree: main 3a190b8d7.
Status: COMPLETE.

## Findings

### RDY-1 — The post-order is not libpcre2's order either: libpcre2 reports the FIRST fault in written order, descending into nested lookbehinds where they occur. Rev 5.1 regresses HEAD-agreeing call cells. CONFIRMED (libpcre2 10.46 + HEAD build), severity MEDIUM (D26 tier 2: offsets only, no answer). Unit V3 (§6.2.2 "Which lookbehind is judged first", SV16, gate 7).
- The doc says inner-first post-order "is the order the parse hook itself finishes lookbehinds in", and the REVISION block says "so the refusal lands at libpcre2's offset". The first part is true. The second is true only when the inner's fault is written BEFORE the outer's first own fault. Every §6.2.2/§6.2.5 G7 cell has that shape.
- Counter-cells, where the outer's own fault is written FIRST (libpcre2 / HEAD pcrec):
  - `(a(?<=b+(?<=(?1))))x`: libpcre2 125 @2; HEAD @2 (AGREES today: the deferred pass is ascending). Under rev 5.1 the inner `(?<=(?1))` is judged first (re-entry) at its own offset (8). That is a REGRESSION of a cell that agrees at HEAD, in the call population rev 5.1 says it improves.
  - `(a(?<=c+|(?<=(?1))))x`: libpcre2 @2, HEAD @2 (agrees). Rev 5.1 gives the inner's offset. Also a regression.
  - `(a(?<=b+(?<=\1)))x`: libpcre2 @2. HEAD @8 (rule 0 at parse). Rev 5.1 gives @8 (re-entry, the inner). Still divergent.
  - `(a)(?<=b+(?<=\1+))x`: libpcre2 @3, HEAD @9, rev 5.1 @9 (inner, order 4).
  - `(?J)(?<n>a)(?<n>b)?(?<=c+(?<=\k<n>))x`: libpcre2 @19, HEAD @25, rev 5.1 @25.
  - `(a(?<=b+(?=(?<=\1))))x`: libpcre2 @2. A lookbehind nested in a LOOKAHEAD in the outer is in libpcre2's walk too. HEAD @11.
  - stage 1, reference-free, parse time: `(?<=b+(?<=c+))x` libpcre2 @0, HEAD @6; `(?<=b+(?<=c+)d)x` @0 vs @6. A pre-existing stage-1 offset divergence of the same class, nowhere stated.
- And the other direction, where post-order is right: `(a(?<=(?<=(?1))|c+))x` libpcre2 @6 (HEAD @2); `(a(?<=b(?<=(?1))c+))x` libpcre2 @7 (HEAD @2).
- So neither ascending order nor post-order is libpcre2's. libpcre2's order is the outer's own written-order walk, with a nested lookbehind's verdict taken at the point where it is written. That is the same family as G5 (a refusal raised earlier wins) and G17 (branch order): "pcrec reports a different item's fault than libpcre2's first in written order".
- Fix (text): withdraw "lands at libpcre2's offset" and the G7 "closes HEAD's offset divergence" claim as unqualified. State the class with the counter-cells above, including the two HEAD-agreeing call cells that rev 5.1 moves, and pin them in gate 7 with pcrec's post-stage-2 answers. Keep post-order if the manager wants it, with its real reason (one order for both timings, the parse hook's). Better: put G5, G17 and this class on ONE K-row. G7's own cells stay correct under post-order.
- Probes: scratch/crit-vlb4/probe/c1.txt, c2.txt (libpcre2 via ora2.py; HEAD via head.sh).

### RDY-2 — G10's clamp makes the ceiling sentence print a FALSE figure: "No reader tells values above the ceiling apart" is false. CONFIRMED by reading plus a HEAD repro of the figure. Severity MEDIUM (the F8 class G10 itself was raised to remove). Units V1/V3.
- `la_width_refusal`'s `LBW_CEILING` arm (src/parse/mod_lookaround.c ~:400) prints "(this one has %lld)" with `bad = hi`. HEAD: `(?<=(?:a{40000}){2})x` gives "... at most 65535 characters (this one has 80000)".
- With row values clamped at 65536:
  - `(a{65535})(\1\1)(?<=\2)x` (row 2 = 131070) prints "this one has 65536";
  - the 25-step chain also prints "this one has 65536" (its true length is about 2^41).
  - The sentence's figure is then false. Gate 7's G10 row ("the 25-step chain with the CEILING sentence") does not say which figure it pins, and SV15 cannot tell a clamped figure from an honest one.
  - Branch SUMS are not clamped: `(a{40000})(?<=\1\1)x` still prints 80000. So the figure is honest for some cells and not for others.
- Fix (text, choose one): (a) the ceiling arm prints "more than 65535" when the value is the clamp; (b) clamp just below the sentinel (`PCREC_W_UNBOUNDED - 1`), so no realistic value changes and only the >2^40 case reads a capped figure, printed as "more than"; (c) the sentence drops the figure for a clamped value. Name `la_width_refusal`'s ceiling arm as a reader of the clamp in V1/V3, and pin the figure in gate 7.
- Related (LOW, stated nowhere): the same saturation hits STAGE 1 with no reference. `(?<=(?:(?:a{65535}){65535}){65535})x` is libpcre2 187 @0, and HEAD prints the unbounded sentence. The clamp is specified only for the table's column, so this twin survives stage 2. Say so in §0 G1/G10, or put the clamp in the walk's saturating arithmetic (one place, both timings). Probe: c3.txt.

### RDY-3 — The re-entry walk misses a cycle that runs through a lookbehind nested in a LOOKAHEAD. Stage 2 adds a NEW pcrec-only accept, and HEAD already compiles the call twin. CONFIRMED (libpcre2 10.46; HEAD compile + matcher run; the rev 5.1 verdict traced by hand from §6.2.1/§6.2.2's rules). Severity HIGH: accept-set tier, and gate 3 counts no such cell. Units V1 (the walk), V5/V6 (cells), V4 (¶5a).
- §6.2.2 order 3: "the closure from THIS lookbehind's own body (§6.2.1's edges; nested lookbehind bodies followed; lookahead and definition-only bodies not)". libpcre2 does follow a lookbehind written INSIDE a lookahead. It does not follow a lookahead's own references or calls.
  - `((?<=\2))(a(?=\1))` ACCEPT, lb 1 (the reference directly in the lookahead is not followed: rev 5.1 agrees).
  - `((?<=\2))(a(?=(?<=\1)))` REJECT 125 @1; `((?<=\2))(a(?!(?<=\1)))` @1; `((?<=\2))(a(?=(?=(?<=\1))))` @1; `((?<=\2))(a(?=x|(?<=\1)))` @1. The lookbehind inside the lookahead IS followed, and the FIRST lookbehind is blamed.
  - `((?<=\2))(a(?(DEFINE)(?<=\1)))` ACCEPT (inside a DEFINE it is not followed: rev 5.1 agrees).
- **The accept-set hole.** `((?=(?<=\2)))(a(?=(?<=\1)))`: libpcre2 REJECT 125 @4. Under rev 5.1:
  - L1 `(?<=\2)` @4 reaches row 2. Row 2's body is `a` plus a lookahead, which is not followed. Row 2 does not contain L1. Bound: `hs` 1. L1 passes, one-length 1.
  - L2 `(?<=\1)` reaches row 1, whose body is only a lookahead. Row 1 does not contain L2. L2 passes.
  - So the pattern COMPILES: a pcrec-only accept that is not one of the two stated divergence classes. HEAD refuses it (rule 0, @4).
- **HEAD divergence, unnamed:** the call twin `((?=(?<=(?2))))(a(?=(?<=(?1))))` is libpcre2 REJECT 125 @4, and HEAD COMPILES it (K127's walk does not descend into the lookahead). Its matcher (`--emit-main`, gcc -O1) answers "nomatch" on `a` and GIVES UP ("frames", rc 3) on `aa`: the call cycle at match time stops at the frame budget. Rev 5.1's walk is K127's, widened, so it keeps this hole. Another twin: `((?<=(?2)))(a(?=(?<=(?1))))` is libpcre2 @1, HEAD @16 (offset only).
- Offset cells that also move to the inner's offset under rev 5.1 (libpcre2 blames the first): `((?<=\2))(a(?=(?<=\1)))`, `((?<=\2))(a(?!(?<=\1)))` and the two above. HEAD agrees on these @1 only by accident (rule 0 refuses L1 at parse).
- Fix (text, before briefing): the re-entry edge walk descends into a lookahead body ONLY to reach the lookbehinds nested in it (at any depth, either polarity), and follows THEIR bodies. It never follows the lookahead's own references or calls. That is libpcre2's measured rule. Add to §6.2.5 and gate 7: the accept-set cell `((?=(?<=\2)))(a(?=(?<=\1)))` (REJECT @4), its call twin as a HEAD divergence closed, and the controls `((?<=\2))(a(?=\1))` and `((?<=(?2)))(a(?=(?1)))` (ACCEPT). Re-word spec ¶5a's "a call inside a nested lookbehind is" to include a lookbehind nested in a lookahead. Give SV6/S1455 a witness for it: a plant that stops the descent must turn `((?=(?<=\2)))(a(?=(?<=\1)))` into a compile.
- The bound and the duplicate-name rules are unaffected: `(?J)(?<n>a)(?<n>b)?(?<=\3)(c(?=(?<=\k<n>)))x` is libpcre2 @31, the inner's offset, as rev 5.1 predicts. Probes: c6.txt, c7.txt, c8.txt; matcher: scratch/crit-vlb4/run/.

### RDY-4 — S172 moves and is not on the "existing rows that move" list. CONFIRMED (grep). Severity LOW-MEDIUM (delivery bar; a stale anchor fails loudly at mech, not silently). Unit V3/V6.
- `tests/mech/sabotages/S172_postresolve_walk_order.sh` plants postresolve.c's insertion sort by `u.look.at` (its SAB_BEFORE is that loop). G7 replaces that sort with post-order ("sort by the assertion's end"), so S172's anchor and its header ("ascending pattern offset ... what libpcre2 does") both move. SV16 plants the same site.
- §6.2.7 lists S171, S-U10, S1454, S1455, S1490, S170 and S1981, but not S172. Add it: re-anchor it to the post-order sort, and either keep it distinct from SV16 (its witnesses are two NON-nested lookbehinds, which tells "walk order" from both sorts) or fold SV16 into it. Fix its header's libpcre2 claim per RDY-1.
- Others checked, and their anchors are untouched by the text as written: S1968, S1969, S1967 (cap/ceiling lines in `la_widths`), S136 (`out[i].lo = (int)lo;`; it holds only if the build keeps those names), S-U4, S169, S1987. The build re-greps (K35) as §6.2.9 says.

### RDY-5 — Order 4 is NOT "HEAD's own control flow with cwmax → hi, cwmax_static → hs". A literal substitution misses the lexical class. CONFIRMED by reading. Severity LOW (gate 3/SV3 would catch it red, not silently). Unit V3.
- HEAD (mod_lookaround.c ~:322-327) tests `hi >= UNB` FIRST, and only inside that branch tests the static width. Substituted literally, a branch with `hi` finite and `hs` unbounded (`(?<=(?:a+){0}x)y`: `hi` 1, `hs` UNB) passes. Order 4's own row ("a branch's `hs` is unbounded", unconditional) refuses it.
- Fix: say that order 4 tests `hs` first, regardless of `hi` (a change from HEAD's nesting), then rule 0 on `hi`. Drop "HEAD's own control flow" or qualify it.
- Same family as RDY-1/G17: within ONE branch libpcre2 reports the first fault in written order. `(?<=(?:a+){0}(?:a{40000}){2})y` is 125 and `(?<=(?:a{40000}){2}(?:a+){0})y` is 187 @0. pcrec (order 4 before order 6) says "unbounded" for both. Tier 2; add it to the one K-row.

### RDY-6 — G1's mark: a SECOND builder of the DEFINE node exists, and rev 5.1 says "set by `pcrec_rcport_define` and nowhere else". CONFIRMED (grep). Severity LOW (no reachable answer difference found). Unit V2.
- src/parse/rxt_compose.c ~:765-786 (the `.rxt` definitions injection) builds `A_REP{0,0}(A_CAP{base}(body))`. Its comment says it is "Not a new shape — mod_recursion.c's `(?(DEFINE)…)` port builds exactly this" and that the two "produce structurally identical trees and a check can ASSERT that". After G1 they would differ by the mark.
- The fact is the same (a body that exists only to be called), so the mark belongs there too: one fact, every builder. Today the injection is concatenated at the ROOT (~:1126), so it lies only on group 0's path. A lookbehind reaching group 0 is refused by re-entry anyway. No answer moves that I could construct.
- Fix: the V2 reader list gains rxt_compose.c's injection and its comment. The mark is set there too, or the doc argues why not.

### RDY-7 — G14's premise about `want_caps` is wrong (harmless), and the describe path's real obstacle is unnamed. CONFIRMED (reading). Severity LOW. Unit V3.
- §6.2.4 says that because `pcrec_count_groups` parses with `want_caps = false`, the table would lack `A_CAP` region roots. Under `want_caps = false`, `pcrec_bref_resolve` (mod_backrefs.c ~:834) keeps the `A_CAP` of every group a reference or a call names (`pcrec_bref_mark`'s keep set, atomic.c ~:685). Those are exactly the table's rows and the re-entry walk's regions. The parse.c ~:1705 comment: wrappers are built unconditionally.
- The real obstacle: the passes need a `cx->job` (`pcrec_altcls` ~:83 writes `cx->job->altcls_*`; facts.c reads `cx->job->pf`), and `pcrec_count_groups` has none. So "drive `compile_driver`'s front half" is the route, not "re-parse with the compile's settings". Say that, and the brief is unambiguous.
- Also: the D27 extract's §0 does not carry the cli.md §2.13¶1 hunk, a caller-visible change (`--count-groups` now refuses `(a)(?<=(?1)|b+)x`; HEAD prints `1`, verified).

### RDY-8 — G11 landed. Two sentences leave the shape open for the build. SUSPECTED ambiguity, severity LOW. Unit V1.
- "Callgraph's per-target arrays become rows of it, and `cg_index` keeps answering 'which row is target t'". With a group-number key, target t's row IS t. `cg_index` stays only for `struct CallGraph`'s own target-indexed arrays (`reach`, `site`, `splice`, `exp`, `body`). Say which.
- The existing columns PUBLISH onto `A_CALL` every round (`cg_minw_publish` / `cg_cwmax_publish`, then `pcrec_minw` / `pcrec_cwmax` read the node). The new column passes the table. "ONE loop function" must therefore serve two read mechanisms. State whether the opaque columns keep per-round publishing (no V2 change to `pcrec_minw`) or move to the table parameter, which would touch `pcrec_minw`, not listed in V2. Either is G11-compatible. The ruling ("same table, not a second loop") is met.
- Over which rows each column is filled (opaque: call targets; followed: the closure from deferred lookbehinds, call targets included) should be one sentence.

### RDY-9 — D27 extract (V7) carries RDY-1/2/3's false promises. CONFIRMED (reading + the cells above). Severity MEDIUM for V7 (a blinded author writes to the promise).
- §2's last paragraph promises "the inner one's fault is reported at the inner one's offset" as a rule. That is false when the outer's own fault is written first (RDY-1: `(a(?<=b+(?<=\1)))x` @2). Its own listed cell `(a)(?<=b(?<=\1+)c+)x` has TWO faults, against §6's "write each refusal cell with ONE fault". Re-word it to "a fault inside a nested lookbehind written before any fault of the outer". Better: put nested multi-fault cells under §6's known-issue rule.
- §6's "a finite length over a limit never says 'unbounded'" is false for the single-fault stage-1 cell `(?<=(?:(?:a{65535}){65535}){65535})x` (RDY-2's related case) unless that case is closed.
- After the RDY-3 fix, §0 ¶5c/¶5a and §2's "contains it" row need the lookahead-nested-lookbehind clause and the cell `((?=(?<=\2)))(a(?=(?<=\1)))`.
- Held: G20's restorations are all present (the through-a-call cap refusal, `(a{65535})(?<=\1b)x`, the three call HEAD-divergence cells, `(a)(?<=\1${v})x`, `(?<=a+|${v})x`). LB is promised via `max_lookbehind`/`_valid_upto`, and `_VALID_LB` is named internal. No src/tests path leaks.

### RDY-10 — spec ¶5a keeps "has no length" for re-entry, the claim G9 ruled false. CONFIRMED (spec text). Severity LOW. Unit V4.
- pattern_language.md §7.4¶5a: "A lookbehind whose call re-enters a group containing that lookbehind ... has no length and is refused". G9's rationale is that its length is finite and "unbounded" is false. §6.2.8's ¶5a bullet adds only the `{0}` twin. Re-word ¶5a to the re-entry fact ("its length depends on a group that contains it"), and add RDY-3's lookahead clause.

### RDY-11 — Gate 3's `pcre2only` pin vs its exclusion list. CONFIRMED (reading). Severity LOW. Unit V6.
- Gate 3 excludes "the LATENT rows (branch reset, `(*ACCEPT)`)" from EXTRA, then pins `pcre2only=1` for `(?<=(?|(a)|(b)))\1x`, which §6.2.5 marks latent. Also latent-accept: G13's calls-only cells `(?|(a)|(bc))(?<=(?1))x` and `(?|(bc)|(a))(?<=(?1))x` (libpcre2 ACCEPT; pcrec refuses by module). Include all three latent-accept rows (pin 3) or none (pin 0). As written the pin depends on a reading.
- SV9's second witness (`(a)(?<=\1)x` refused) does not follow from the plant "rule 0 keeps references": `hi` comes from the table and is finite. The first witness suffices. Drop the second or define the plant.

## Ruling check (did each land as ruled)
- G1 (DEFINE mark as a node fact): LANDED (§6.2.1, the A_REP payload field set by the port; edge walks skip it, region searches enter it; atomic.c re-argued). Gap: RDY-6 (second builder).
- G4 (stated divergence): LANDED (§0 G1, §6.2.1, §6.2.5 row, gate 3 declared class, ¶5 spec clause, extract §5.2).
- G9 (re-entry sentence): LANDED (own `la_width_refusal` arm, K127's call arm included, gate 7 row). Gap: RDY-10 (¶5a).
- G11 (one table, cwmin retired): LANDED (one table keyed by group number at `pcrec_callgraph_build`'s position, one loop function, cwmin fixpoint + `cg_cwmin_publish` + `u.call.cwmin` + S-U10 retired as a simplification; reader claims verified: `u.call.cwmin` read only at mrl.c ~:754; `pcrec_cwmin` callers are callgraph ~:860, `la_widths` ~:321, `tests/mrl/cwmax_check.c` parse-only). Text: RDY-8.
- G14 (describe path runs postresolve's checks): LANDED as a choice with a measured cost and the manager's fallback. HEAD hole verified (`(a)(?<=(?1)|b+)x` prints 1). Text: RDY-7.
- G7 claim "the proposed fix broke K127, so re-entry still follows nested lookbehinds": TRUE. With nested lookbehinds off the re-entry path, `((?<=(?2)))(a(?<=(?1)))` would pass both lookbehinds (each closure stops at the other's group), where libpcre2 refuses @1. The existing S1490 row defends exactly that edge. Consequence: consistent under post-order (a group containing the outer contains the inner, so a cycle reached through the inner refuses the inner first). But the same libpcre2 rule extends into LOOKAHEADS, which rev 5.1 does not follow: RDY-3. Ordering consequences: RDY-1.

## Per-unit verdicts
- **V1 the table — READY WITH TEXT FIXES:** RDY-3 (the re-entry walk descends into lookaheads to reach nested lookbehinds; MUST land before briefing, accept-set tier), RDY-2 (the clamp's figure reader), RDY-8 (row/column/publish wording). Cites hold at 3a190b8d7: `sc.ncall == 0` ~:701, the three fixpoints ~:829-890 (three copies of one text, verified), `cg_roots` first-wins ~:153, `cg_length_calls` ~:929, `if (n == 0) return false;` ~:981, the `cx->callgraph` readers (emit_vm.c :10770, nfa.c :1041, lower_enc.c assert), compile.c's pass order :2876-2968.
- **V2 the scoped walk + mark — READY WITH TEXT FIXES:** RDY-6. Cites hold: `cwmax_walk(a, any)` :545, `pcrec_cwmax_static` :698 (one caller, `la_widths` :324), `row_cwmax` :485, the `A_CALL` cwmin arm :750-754, the header's "TWO UNITS" :20, `pcrec_rcport_define` :517/:567.
- **V3 the rule + describe path — READY WITH TEXT FIXES:** RDY-1 (the order claim plus the HEAD-agreeing call cells it regresses; a manager choice: keep post-order with its stated reason, or not), RDY-4 (S172), RDY-5 (order 4 tested first on `hs`), RDY-7 (`want_caps` premise; the `cx->job` obstacle). Cites hold: `la_widths` :313, `la_width_refusal` :394, the `recurses` arm :466-470, the deferral `pcrec_has_call(body)` :624, `pcrec_count_groups` :3795 with `want_caps = false` :3821.
- **V4 spec — READY WITH TEXT FIXES:** RDY-10 (¶5a "has no length"), plus the RDY-3 and RDY-1 clauses if adopted. Hunk targets verified verbatim: §2.4 shape 5 (:150), §7.3¶6 (:460), §7.4¶5 (:480), ¶5a (:481), §9¶2/¶2a (:626-627), vars.md §6 row (:154), cli.md §2.13¶1 (:446), match_api §9.4¶2.
- **V5 corpus and pins — READY WITH TEXT FIXES:** add RDY-3's accept-set and control cells and RDY-1's counter-cells. The flip counts were verified by a whole-tree scan: refused.rxt ×2, gated.rxt ×1, d27/refusals.rxt ×2, and no other reference-lookbehind `perr` row. The DEFINE/`{0}` perr rows (`((?<=(?1){0})x)`, `(?(DEFINE)(?<g>a(?<=(?&g))))x(?&g)`) stay refused under rev 5.1.
- **V6 checks — READY WITH TEXT FIXES:** RDY-11 (`pcre2only` pin, SV9's second witness), RDY-4 (S172), a witness for RDY-3. SV1-SV16 hand-traced: each has a witness that goes red under its plant (SV9's FIRST witness only).
- **V7 D27 — READY WITH TEXT FIXES (re-cut after the above):** RDY-9.

## Ordered rule table (§6.2.2): the emptiness drill, witnessed
Each row's own cell is taken by no earlier row, checked against the rule text:
- order 1: `(?J)(?<n>a)(?<n>b)?(?<=\k<n>)x`;
- order 2: EMPTY by declaration, the module refuses `(?|`;
- order 3: `(a(?<=\1))x` (no duplicate name, `(?|`-free);
- order 4: `(a+)(?<=\1)x` (group 1 does not contain the lookbehind);
- order 5: a mark, not a refusal;
- order 6: `(a{65535})(?<=\1b)x` (`hs` finite);
- order 7: `(a{1,256})(?<=\1)x`;
- order 8: `(?<=${v})x`.
The drill passes. The one ordering defect is RDY-5 (how order 4 is phrased against HEAD's nesting). The libpcre2 cells spot-checked independently (9/9 match the table): `(\2)(\3)(a)(?<=\1)x` lb 1, `(a(?<=\2))(b)(?<=\1)x` lb 1, `(?<=(?:\1+){0}x)(b)y` 125@0, `(a{65535})(\1\1)(\2\2)(?<=\3)x` 187@22, `(?|(a)|(bc))(d\1)(?<=\2)x` 125@17, `(a(?(DEFINE)(?<g>(?<=\1)b)))x` 125@17, `(a(?1){0})(?<=\1)x` 125@10, and the G7 cells @7/@24/@7/@12/@6/@5/@1/@1.

## PROBED-AND-HELD
- G7's seven pinned cells and the two "cycle through the first" cells: libpcre2 offsets reproduce exactly (c2.txt). Post-order gives each one correctly.
- G1: DEFINE-skipped cells, the DEFINE region-search @17, and `((?<=\2))(a(?(DEFINE)(?<=\1)))` / `((?<=(?2)))(a(?(DEFINE)(?<=(?1))))` both ACCEPT. Rev 5.1's "not entered" is right there, and the second closes one more HEAD refusal (HEAD @1).
- VALID_LB == max_lookbehind over 19 stage-1 shapes (`\b`, `^`, `\G`, nested lookarounds, two lookbehinds, alternation in two lookbehinds, `{0}`, atomic, possessive): all equal. Gate 3's new compare will not go red on pre-existing stage-1 cells (c4.txt). Call into a group holding a lookbehind: libpcre2 and pcrec agree (lb 2, lb 3; c5.txt).
- The duplicate-name walk with the name in a lookbehind nested in a lookahead of a reached group: libpcre2 @31 = the inner's, as rev 5.1 predicts.
- `lb_max` raise timing: only emit_dfa/emitters read it, after postresolve. The wider deferral moves no byte through it.
- `u.look.widths` readers between parse and postresolve: none (emit_vm.c's readers NULL-guard or fail loudly).
- The reject table's unbounded-sentence pins (`run_reject_tests.sh` :1931-1937, :1961-1962): none is a re-entry cell, so G9's sentence move hits no existing pin (the doc's claim holds).
- Spec targets and quoted code comments: all exist at 3a190b8d7.
- Compiles run: about 60 single `build/pcrec` compiles, about 75 libpcre2 cells, one emitted matcher (gcc -O1) run on 4 subjects. No suite, no make.

## OVERALL
NOT READY to brief as written. READY WITH TEXT FIXES (a rev 5.2 text pass, no new mechanism). One finding is answer-tier: RDY-3, the lookahead-nested lookbehind cycle (a new pcrec-only accept, plus an unnamed HEAD call divergence that gives up "frames" at match time). One is a manager choice: RDY-1's order (state the class; post-order is not libpcre2's order). The rest are text. A one-critic diff check of rev 5.2 suffices, not a round.

## RULINGS (manager, 2026-11-10)
- RDY-1: refusals report the FIRST fault in WRITTEN order, as libpcre2 does (keeps `(a(?<=b+(?<=(?1))))x` agreeing as at HEAD); inner-first is dropped.
- RDY-3: the re-entry walk follows lookbehinds nested inside lookaheads, as libpcre2 does; `((?=(?<=\2)))(a(?=(?<=\1)))` is refused (125); the call twin that compiles at HEAD is a known_issues row (K-n) whose fix rides V1.
- All other RDY items as proposed: a rev 5.2 text pass, then ONE critic diff check, then the build lane.
