# EMITTED-VS-REPLACED — ic1b-code
critic: emitted-vs-replaced, model: opus; started 16:10; status: COMPLETE

BASE compiler: NOT available. The main tree's build/pcrec emits abi 86
(built 05:19, before SCANEDGE-SET's 86->87 and stage 1a); no rebuild per
COMMON. BASE-vs-SUBJECT emitted-C comparisons use that abi-86 binary as a
NEAR-BASE and attribute any delta to SCANEDGE-SET (scan edge over a class
set, ddd18d3df/9a4a5b597) or 1a only when the delta is that shape;
otherwise by reading BASE source (git show 43414ddac:...).
No denied file opened.

## EMIT-1 A check site is path-OPAQUE, so a repeat before it loses possessify/frameless even when the follow after the site is disjoint
- status: CONFIRMED (cost); the answer is unaffected
- severity: speed (design-level; the row is design-named, the breadth is the point)
- effort: M ; blast radius: every callout pattern with a site directly after a repeat (`\w+(?C"x")\s`, `a+(?C"x")b`, `x*(?C"x")\d+:`)
- where: src/core/kindrow.def (A_CALLOUT row, path OPAQUE); src/opt/possessify.c first_of/gk_build/pss_walk A_CALLOUT arms; design inline_c.md §1.8 table
- repro: `build/pcrec --features classes,callouts --engine=vm -p rx -o x.c --pattern P`, stamps:
    `a+b`          RX_VM_FRAMELESS 1, STRATS 0x1, PROGRAM_BYTES 815
    `a+(?C"x")b`   RX_VM_FRAMELESS 0, STRATS 0x2, PROGRAM_BYTES 2242
    `(?C"x")a+b`   RX_VM_FRAMELESS 1 (site before the repeat: no loss)
    `\w+(?C"x")\s` FRAMELESS 0 vs `\w+\s(?C"x")` FRAMELESS 1
  Answer argument: for a CHECK (W_PRED, no text), giving back an `a` of `a+`
  leaves `a` as the next byte, which `b` rejects whatever the callee says;
  the check only removes paths. The possessive and the backtracking program
  give the same answer for every pure callee; only fire counts differ
  (unspecified, §11.6).
- argument: §1.8's witness for OPAQUE is P7, `(\d+)(?C)` at the pattern's
  END: the unsound step there is "the rest surely succeeds" (may_end), not
  the disjointness proof. OPAQUE ("every byte, nullable") also kills the
  disjointness proof, which a vetoing zero-width node cannot break. A
  finer value ("veto gate": transparent to first-set disjointness, but
  never lets a path reader conclude that reaching the end/the rest is
  success) would keep P7 refused and give `a+(?C)b` its frameless
  program. pcrec's own lookarounds pay the same today (`a+(?!x)b` is
  FRAMELESS 0, `a+(?=x|y|b)b` is FRAMELESS 1), so the general form is one
  path value serving A_LOOK and A_CALLOUT (see GENERAL FORM). Not a
  defect of stage 1b: the design chose OPAQUE knowingly; filed as the cost
  and the unlock. Trigger: a bench/measured callout pattern with a site
  after a repeat, or [POSS-CTX-TABLE]'s next per-kind edit.

## EMIT-2 The shared ABI block's rx_matchfn comment in every callout artifact contradicts the artifact's own call site (INTERNAL "traps" vs propagates)
- status: CONFIRMED
- severity: doc (landing-order dependency)
- effort: S ; blast radius: every artifact's shared block; the contradiction is live only in callout artifacts
- where: emitted header, `typedef ptrdiff_t rx_matchfn` comment ("a generated call site that invokes an rx_matchfn traps on one" [PCREC_ERR_INTERNAL]) vs the emitted site `if (r == PCREC_ERR_INTERNAL) return r;` (src/gen/callsite_rows.c row `internal`, CS_PROPAGATE)
- repro: `build/pcrec --features classes,modifiers,callouts -p rx -o t1.c --pattern '(a(?C"see"))+b'`; t1.h lines 35-45 vs t1.c site (`return r` on -6). Probe: callee returning -6 -> rx_search rc=-6 (propagated, no trap).
- argument: design §1.6 D6 makes the comment fix ITS OWN abi event (88, ic0's) "landed before stage 1b"; SUBJECT bumps 87->89 without it, so SUBJECT on its own ships the stale text beside the first call site that contradicts it. Not a bug once ic0 lands first; the finding is that the merge order is load-bearing and nothing in ic1b checks it (a check: grep the emitted shared block for "traps on" in a callout artifact). Manager: land ic0 (abi 88) before ic1b, or ic1b's re-pin must carry the comment.

## EMIT-3 callee_gave_up is written but never read in an untiered artifact
- status: CONFIRMED
- severity: size (trivial)
- effort: S ; blast radius: frameless callout artifacts (no tier) and the `_in` paths
- where: src/gen/emit_vm.c vm_emit_storage (field gated on ncallouts>0 only), vm_callout `.giveup` edge
- repro: `--pattern '(?C"cx")a+b'` (RX_VM_FRAMELESS 1): `callee_gave_up` appears at the struct, the init and the site's store, and no tier test reads it (rx_search -> rx_search_in, no deep rung).
- argument: one int and one store per give-up path; gcc likely keeps the store (run is a pointer). The gate could be "ncallouts>0 AND a tiered entry is emitted". Mention only; no answer effect.

## Note (not a finding, contract lens's): `--engine=dfa` on `a(?C"x")` says "(?C1) requires the VM engine" — the registry row's probe spelling, not the site as written. D26 tier; mention only.

## PROBED-AND-HELD
Q1, the callout site (drivers: emitted/drv.c, drv2.c; oracle emitted/ora.c,
libpcre2-8 with NO_AUTO_POSSESS|NO_START_OPTIMIZE|NO_DOTSTAR_ANCHOR; answers
only, never fire counts):
- 58 check-only patterns x 1-3 subjects (batches b01-b25, c01-c20, d01-d10,
  n01-n04, m01-m03): pcrec == libpcre2 on every answer and every group,
  including P7 `(\d+)(?C"even")`, `(?s).*(?C"vstart")x`, lazy/possessive/
  atomic/lookahead/negative-lookahead sites, captures restored by the trail
  on backtrack (`(?:(a)x|ab)(?C"g1set")`), repeated groups (previous
  iteration visible, unset before first close), `\K` before a site
  (caps[0][0] = attempt start, PCRE2 10.46 agrees), numbered `(?C1)`/`(?C2)`.
  (b13 not run: conditionals unbuilt.)
- View: caps[0][1] was -1 at every fire of every probe (driver asserts);
  ncap = groups+1; under --no-captures the view still carries group 1
  (n02: NSLOTS 5, ncap 2, answer delivers RX_NCAPS 1 as specified).
- Slot 0: saved, set to ctx->pos (= attempt_position in the search loop,
  the caller's pos in _match), restored before routing; verified in t1.c
  and by the \K probes.
- Return routing (drv2 with a scripted callee): -1 backtracks; 0 continues;
  give-ups -2/-3 propagate out of rx_search with fires=1 (no tier replay for
  a callee FRAMES); -6, -8, -9 propagate; -7, -10, -11 and a positive return
  at a check trap (SIGILL); consume: r within bounds continues at pos+r,
  r > len-pos traps, -e utf8 mid-character (r=1 into U+00E9) traps, r=2
  continues. Propagation held across 10 search-body shapes (^, \G, $, (?m)^,
  .*, (?s).*, \z, \A..|b, lookahead site, alternation).
- Step charge: --step-budget=5 with a vetoing site, 9 attempts: STEPS after
  exactly 5 fires; --fno-step-budget emits no charge.
- Consumers vs start facts: start set all-bytes for a leading consumer
  (`(?C"cx,consume")b` matches at 0 on `xb`); REQ_RUN none across a
  consumer; END_WINDOW none; alternation dispatch, lookahead restore,
  nullable star with a consumer returning 0 (terminates), lazy, possessive
  and atomic around a consumer: 13 shapes, answers as hand-derived.
- once: 20 shapes, refused exactly where §11.8 class 3 says (choice point
  inside the same atomic/lookahead before the site refused; sealed ones
  accepted).
- asm (gcc -O2) of a check site: ~15 instructions of ctx build + one
  indirect call + `cmp $-1` on the hot path.
Q2, no-callout patterns, near-BASE (abi 86 main build) vs SUBJECT:
- 41 patterns compiled by both (DFA, VM, captures, --no-captures,
  -fcomments, --emit-main, utf8, lookaround, backrefs, recursion, vars,
  \K, compounds `^\s+|\s+$`, `^a+|b+$`, `^(?:a|b)c|\d+$`, `^(?=a)\w+|b$`):
  0 movers beyond the abi number EXCEPT 7 patterns whose deltas are all
  DFA scan-edge shapes (RX_DFA_SCAN_EDGE none->range/bitmap/mixed, reverse
  stop states renumbered), i.e. SCANEDGE-SET (abi 86->87), which the
  near-BASE predates; SUBJECT's emit_dfa.c diff touches only the
  ncallouts-gated surface and comments. Compound call-site lines
  byte-identical in all 6 compound artifacts (10/10/2/10/10/10 lines).
- Enabling module callouts with no site: only PCREC_FEATURE_MODULES moves.
- --emit-ir: the callouts section header 2 -> 7 columns and the empty-row
  note text move for every VM pattern (named by the ir_listing.md hunk).
Q3, cost: prefilter declined (pf_admits row; -fprefilter refuses), engine
forced VM (so no DFA, no compound), every group published at close and kept
under --no-captures (design §1.3 names it), revdet/islands/det-seq decline
a body holding a site, OPAQUE blocks possessify after a site (EMIT-1). The
start-set seek and req handoff stay (D4) and held in the probes. Nothing
broader than §1.8/§9.1 except EMIT-1's breadth, which the design chose.

## GENERAL FORM and unlocks
The change's general form is ONE CALL-SITE TABLE FOR EVERY CALL OUT OF A
GENERATED MATCHER, rows enabled by the callee's facts (conv, vm, guarded,
utf_check, pred, enc). Today: compound parts (part) and extern bindings
(matchfn, every row live). Unlocks, with triggers:
1. Fact-pruned rows for a KNOWN callee: a pcrec artifact bound as a
   callout (§6) or an embedded code segment (stage 2) supplies its facts
   (DFA: no give-up/internal/unset rows; no -futf-check: no UTF row), so
   its site drops dead compares and the trap set shrinks. Trigger: §6 /
   stage 2's first known-callee site.
2. A "veto gate" path value shared by A_LOOK and A_CALLOUT (EMIT-1): a
   zero-width node that can only remove paths is transparent to first-set
   disjointness but blocks "rest succeeds" conclusions. Unlocks frameless/
   possessified VMs for `a+(?C)b` and `a+(?!x)b` alike. Trigger: a measured
   callout or lookaround pattern losing FRAMELESS on the bench, or
   [POSS-CTX-TABLE]'s next edit.
3. Give-up provenance generalized: the callee-gave-up bit is the first
   "who gave up" fact the tier reads; any nested matcher with its own tier
   (a pcrec callee, a future out-of-line part) can set it. Trigger: the
   first nested matcher with its own escalation besides a callout.
