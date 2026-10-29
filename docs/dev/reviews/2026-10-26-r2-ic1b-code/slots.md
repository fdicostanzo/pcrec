# SLOT — ic1b-code
critic: slots (slot-tracing + ruling-check), model: opus; started 2026-10-26; status: COMPLETE

## SLOT-1 Firing class counts a never-run group's choices as live: `once` refused on a valid site
- status: CONFIRMED
- severity: design (a correct program refused; class over-reported)
- effort: S ; blast radius: every callout pattern with a `(?(DEFINE)...)` group or an `X{0}` holding an alternation/quantifier/call BEFORE a site (lib definitions compose to the same `A_REP{0,0}` shape)
- where: src/opt/callout.c:67-94 (`co_choice`, `A_REP` arm recurses into the body when rmin==rmax, incl. 0..0) vs :99 `co_inert` (the same fact, used only for `tail`)
- repro: `build/pcrec --features all --emit-ir --pattern '(?(DEFINE)(?<d>a|b))x(?C1)'` lists the site `repeated`; with `(?C"f,once")` it is refused "a quantifier, alternation or call before it can be backtracked into"; `(?:a|b){0}x(?C"f,once")` likewise. `(?(DEFINE)(?<d>a))x(?C"f,once")` is accepted (once-per-match). Expected per §1.10: a group that never runs holds no choice point the engine can resume (it is never entered), so class 1 and `once` accepted.
- argument: §1.10 defines a choice point as one the engine "can resume ... and reach the site again"; a `{0}` body is never entered. The walk already has the fact (`co_inert`) and uses it for one of its two questions only: two answers to one structural question in one file (coding.md "one table per slot" in miniature). Fix: `co_choice` returns false for `co_inert(a)` (one line), plus a listing/`once` expectation row with a DEFINE group. Sound direction today (over-conservative), so no answer moves; Frank's ruling (2) "refused with the reason" is broken because the printed reason names a construct that cannot be backtracked into.

## SLOT-2 The `once` refusal names no construct and no offset (§1.10 asks for both)
- status: CONFIRMED
- severity: doc/design (diagnostic content ruled by FR6 / Frank's 10-26 ruling 2 "refused with the reason")
- effort: S-M ; blast radius: every `once` refusal
- where: src/opt/callout.c:151-158
- repro: `\w+(?C"f,once")` -> "callout at offset 3 is marked once but can fire again: a quantifier, alternation or call before it can be backtracked into; make the quantifier possessive (X*+) or wrap it in (?>...)". §1.10's ruled text: "naming the construct that breaks it and the fix: '... the quantifier \d+ at offset 1 can be backtracked into ...', or '... is inside the repeat at offset 0'".
- argument: `co_choice` returns a bool, so the culprit node is lost; the generic three-way noun ("a quantifier, alternation or call") and the possessive hint are wrong for an alternation or a call (neither has a possessive form; for the DEFINE case of SLOT-1 nothing at all can be fixed). Returning the first live choice node (or recording it on the walk) gives the offset and the right noun from one place. D26 tiering does not cover this: it is pcrec's OWN diagnostic for its own construct, whose wording the design fixed.

## SLOT-3 `PF_KIND_CALLOUT` has no name: `--emit-facts` renders a callout pattern's kinds as `none`
- status: CONFIRMED
- severity: doc (a caller-observable query states a false fact; the decision it reports on reads the bit)
- effort: S ; blast radius: `--emit-facts` `kinds` row of every callout pattern; any fact-level gate or reader of the rendered kinds
- where: src/facts/facts.c:683-690 (`pf_kind_name[]`, 7 names; `_Static_assert(PF_KIND_COLLAPSIBLE_REP == 1u << (n-1))`), src/facts/facts.h:282 (the new bit 7)
- repro: `build/pcrec --features all --emit-facts --pattern 'a(?C1)'` -> `kinds ... none`; `(a)\1(?C1)` -> `bref,live_capture` (no `callout`). The prefilter's `callout` row (select_engine.c `pfa_callout`) reads the same mask and declines, so the listing and the decision disagree.
- argument: the static assertion was meant to tie the name table to the enum, but it is pinned to the then-last member by NAME, so a new last bit passes it silently (learnings §3: a control anchored to a fixed member stops reaching the population; memory pcrec-check-design-lessons). §1.8 D4 names `src/facts/kinds.c`'s switch as the "alarm" for the new bit; the alarm that would have fired is this one, and it was mis-anchored. Fix: add `"callout"`, and assert against a `PF_KIND_COUNT`/last-bit enumerator (or build the names and bits from one .def) so the next bit is a compile error.

## SLOT-4 The binding table of §1.4 is four copies of one ternary, not a table
- status: CONFIRMED
- severity: maintenance/design
- effort: S ; blast radius: stage 2 (`CO_CODE`, §1.4 row 1) must edit all four; a missed one makes the listing, the header's extern list and the call disagree on the callee
- where: src/gen/emit_vm.c:9008-9010 (`vm_callout`), :10055-10057 (IR listing), src/gen/emit_dfa.c:2649-2651 (`emit_callout_surface`), src/opt/callout.c:319-326 (`--emit-main` refusal)
- repro: `grep -n 'rx_callout_%' src` -> the `bind == CO_NAME ? "rx_callout_%s" : "rx_callout_%d"` choice written four times; `user` (`<sym>.user`) and the callee expression (`<sym>.fn`) are hand-written in `vm_callout` only.
- argument: §1.4: "The emitter reads the callee from a declared first-match table" (code / named / numbered, with callee expression, `user`, width default). architecture.md/coding.md "one table per slot" and memory pcrec-decisions-as-first-match-tables. Stage 2 adds row 1 (a direct static call, `user` NULL), which is exactly the row whose callee expression differs from `<sym>.fn` - the place the copies diverge. One `pcrec_callout_binding(cx, a)` -> {symbol, callee expr, user expr, needs_extern} serving the four readers is the table; do it before stage 2.

## SLOT-5 `-fprefilter`'s refusal for the construct rows is a hand-written chain beside the `pf_admits` table; the callout adds a fourth member by negation
- status: CONFIRMED
- severity: maintenance/design
- effort: S-M ; blast radius: prefilter_decision (select_engine.c:1005-1022); every future construct row
- where: src/opt/select_engine.c:707-719 (row `callout` in `pf_admits[]`: "no flag changes this, and -fprefilter refuses") and :1005-1022 (`has_callout` + `if (force_on && has_callout && !(has_bref || has_call || has_var))` before the old `pf_noun` ternary)
- repro: read; the refusal's priority (bref > call > var > callout) is encoded twice, once as table row order and once as the ternary plus the `!(...)` guard.
- argument: the table already says, per row, that `-fprefilter` refuses; the refusal TEXT and the decision live in a parallel if-chain whose comment ([VAR]) accepted "a third one in the shape of the first two" pending [PATFACTS]. The callout is the FOURTH member and does NOT take that shape (its own sentence, its own guard). memory pcrec-forest-for-trees: propose unification at ~3 members. General form: a `refuse` column on the construct rows (`pf_admits`), and the first matching construct row under `force_on` refuses in its own words - deletes `pf_noun`, `has_callout`'s guard and the three-way negation. No answer moves.

## SLOT-6 "Does this construct constrain which attempts run?" now answers YES for a callout in the registry column and NO in the two conjuncts
- status: CONFIRMED (inconsistency); its consequence SUSPECTED (a narrowing, sound)
- severity: design
- effort: M (a ruling, then S code) ; blast radius: compound admission A3 (callout patterns can never be compound parts), emit_dfa.c start-set seek and req-handoff conjunct (g)
- where: src/core/internal.h:4498-4510 (`RF_CROSSES_ATTEMPTS`: "the CALLOUT rows ... declined for now under D163 add. 6 Q2's purity contract ... a ruling on one relabels it"), src/parse/registry.c:286 (`GROUP_XA_CALLOUT` still sets it), src/opt/derive.c:388-403 (A3 reads it); vs src/gen/emit_dfa.c:7925-7934 and :8689-8700 (the callout half RETIRED: skipped attempts are unspecified, FR1)
- repro: read. The D4 argument recorded at both conjuncts ("fires on attempts the engine skips are unspecified; a pattern with vetoes matches a subset of the erased superset") is exactly the argument that a callout does not observe the attempt SEQUENCE; the column's own note says a ruling relabels it, and 1b did not touch the note or the row flag.
- argument: three sites decide one fact (the attempt-scope family): the registry column and two hand-written conjuncts in emit_dfa.c whose remaining verb halves read NOTHING ("structurally absent ... the kind that adds one must decline here"). After 1b the callout is in the column and out of the conjuncts, with no recorded reason for the split (the firing-class bound "per attempt within one engine run" or D8's tier rule would be candidate reasons for the compound, but none is written). Ask: either re-rule the callout's column membership with its reason, or relabel it; and make the two conjuncts read the column (a `PF_KIND_CROSSES_ATTEMPTS` bit derived from `RF_CROSSES_ATTEMPTS`) so the next verb producer is decided once. (Not a 1b scope miss in itself; the D4 ruling created the asymmetry.)

## SLOT-7 Stage 0 (D6) has not landed under this subject: every callout artifact's ABI block says a call site TRAPS on `PCREC_ERR_INTERNAL`, while its own call site propagates it
- status: CONFIRMED
- severity: doc (emitted contract text contradicts emitted code) / process (ruled order)
- effort: S (landing order) ; blast radius: every artifact's shared ABI block; most visibly every callout artifact
- where: emitted header, e.g. `build/pcrec --features all -p rx -o b.c --pattern '(\d+)(?C"see")x'` -> b.h:41-44 "a generated call site that invokes an rx_matchfn traps on one", and b.c's site: `if (r == PCREC_ERR_INTERNAL) return r;` (callsite_rows.c:109, row "internal", CS_PROPAGATE)
- argument: inline_c.md §1.6 D6 and §9.1 "Order: 0 and 1a before 1b": the comment is stale against D163 add. 6 Q3 and is "ITS OWN abi event, landed before stage 1b". The subject is based on main without lane ic0 (abi 88 reserved for it; abi_changelog entry says so). Consequence: if 1b lands first, the first producer of the propagate row ships beside a comment saying the opposite, and ic0 must then re-pin on top of 89 (renumbering 88/89). Land ic0 first, or re-base 1b on it before merge.

## SLOT-8 A second, dead implementation of the READS column in derive.c
- status: CONFIRMED (by reading; the arm is unreachable per its own comment)
- severity: maintenance
- effort: S ; blast radius: src/opt/derive.c `qf_walk`
- where: src/opt/derive.c:75-80 (`case A_CALLOUT: for (g = 0; g <= ncap; g++) kept[g] = true;`) vs src/opt/atomic.c:651-667 (`bref_mark_reads`, the row read, marking 1..nmark-1)
- argument: §1.8 gives `reads` ONE reader family (the marked set). `qf_walk` already hand-codes A_BREF's refs (1a left it); 1b adds a third hand-coded reads answer (ALL) that differs in range from the row reader (includes group 0) and is, per its comment, unreachable (admission A3 declines first). A row read via an exported `bref_mark_reads`-shaped helper keeps one answer; or delete the arm's body to an internal error like revdet's, since the claim is "never reached".

## SLOT-9 The consume variant of A_CALLOUT's row lives in code, not in kindrow.def
- status: CONFIRMED (design observation; no answer moves today)
- severity: maintenance
- effort: S ; blast radius: any reader that calls `pcrec_kind_row(a->k)` instead of `pcrec_ast_row(a)` gets TEXT ZERO for a `consume` site (none does today: all 11 readers use `pcrec_ast_row`)
- where: src/core/internal.h:2333-2343 (`if (a->k == A_CALLOUT && a->u.callout.consume) r.text = KTEXT_ANY;`), src/core/kindrow.def:76-81
- argument: §1.8 declares TWO rows for A_CALLOUT (W_PRED: zero/opaque/refs; W_ANY: any/opaque/refs). The implementation keeps one row and patches one column in the accessor; the .def's header claims "every kind has exactly one" row and the table is "complete by construction", which is no longer the whole truth for this kind, and `pcrec_kind_row` stays callable. Low cost now; stage 2 (code sites, `verify` in stage 4) is where a second per-node patch would land in the same `if`. A variant row in the .def (e.g. `KIND_ROW_VARIANT(A_CALLOUT, consume, ANY, OPAQUE, ALL, NFA_ERASED_CALLOUT)`) or making `pcrec_kind_row` file-private would keep the table the one source.

## SLOT-10 callout.c adds two hand-written whole-tree walks where `pcrec_ast_visit` already fits
- status: CONFIRMED
- severity: maintenance
- effort: S ; blast radius: src/opt/callout.c only (two more -Wswitch leaf lists to keep)
- where: src/opt/callout.c:221-244 (`co_targets`, read-only: marks call targets) and :248-276 (`co_apply_decl`, sets attributes on matching sites); vs src/core/internal.h:5423 `pcrec_ast_visit` (same traversal, same back-edge rule) and mod_callouts.c:104-115, where the lane itself used the visitor for `pcrec_has_callout`
- argument: each walk restates the leaf list and the spine loop; `co_targets` is a visitor callback verbatim, `co_apply_decl` one with a const-dropping cast or a mutable visit (or: collect `cx->callout_nodes` FIRST, which the pass builds anyway, and apply declarations by iterating sites, deleting the walk). `co_walk`/`co_choice` carry context and are justified walks.

## Slot trace: the 67 `case A_CALLOUT` arms, classified
| class | count | where |
|---|---|---|
| ROW READ (arm routes to `pcrec_ast_row`) | 8 | req.c `rb_row_into`; startset.c `ss_row`; mrl.c `row_cwmax`; possessify.c `text_first`, `first_of`->`fst_row`, `gk_build`->`gk_row`; nfa.c `frag_row`; atomic.c `pcrec_bref_mark`->`bref_mark_reads` (KREADS_ALL) |
| JUSTIFIED code (kind-specific behaviour) | 9 | emit_vm.c `vm_emit_node`->`vm_callout`; callout.c `co_choice`, `co_walk`; revdet.c `rd_reverse` (loud internal error, shape scan declines first); select_engine.c `earliest_dfa_excluding` (VM_ONLY via the registry row, as §1.1 asks: no callout clause); definitions.c `pcrec_ast_is_core`; endwin.c x2 / startanch.c (decline beside A_LOOK; zero-width checks are skipped upstream by `pcrec_cwmax == 0`, a row read, so a check site does not narrow the end/start facts) |
| SHOULD-BE-ROW (restates a row fact by hand) | 7 | widths.c `em_set`, `rw_node` (nullable / min 0 = TEXT != OWN); mrl.c `pcrec_minw`, `pcrec_nullable` (`return true`), `pcrec_cwmin`; derive.c `qf_walk` (READS ALL by hand: SLOT-8); select_engine.c `-fprefilter` refusal (SLOT-5). All but SLOT-5/8 are stage 1a's left-as-code arms that 1b joined; answers are correct for both width classes |
| LEAF / no-descent arms (house -Wswitch enumeration) | 43 | atomic.c x9, emit_vm.c x9, possessify.c x4, revdet.c x4, lower_enc.c x3, derive.c x2, rxt_compose.c x2, callout.c x2 (SLOT-10), and one each in callgraph.c, altcls.c, ctxnode.c, definitions.c, mod_backrefs.c, mod_lookaround.c, mod_vars.c, parse.c, internal.h (`pcrec_ast_visit`) |
No arm DUPLICATES a row read with a different answer, none is UNREACHABLE except derive.c:78 (stated) and revdet.c:384 (an internal error by design), and no `default:` swallows the kind (68 AKind switches scanned: none with a `default:` lacks an A_CALLOUT arm; no `== A_VAR`/`== A_BREF` test lacks its callout counterpart).

## Ruling check (docs/design/plan_row_bodies/INLINE-C.md)
| ruling | code | consequence |
|---|---|---|
| FR2/FR5 check by default, `consume` opts in; numbered declares in .rxt / `--callout` | agrees: `pcrec_callout_attrs` one grammar for string and declaration (mod_callouts.c:64), applied before any reader (callout.c step 1); stale/duplicate declarations refused | - |
| FR3 read-only `const rx_ctx *` | agrees: `rx_matchfn(const rx_ctx *)`, `caps` cast to `const ptrdiff_t (*)[2]` over the live slot array | the callee sees the VM's working slots by pointer (valid for the call only, §5¶7); a const-casting callee can corrupt the match, which is the user's contract break, not pcrec's |
| FR4 budget: each fire one step, no budget access | agrees: `if (--run->steps_left < 0) return R_STEPS` before the call when a budget exists; nothing in `rx_ctx` | with `--step-budget` none, fires are unmetered (as every step is) |
| one attribute grammar for named and numbered | agrees | - |
| FR6 firing class + `once` (incl. atomic groups); Frank: `once` needs a non-retryable prefix | agrees on all 11 §1.10 examples (probed, listing matched) and on `\w+(?C"f,once")` refused / `(?>\w+)` accepted | SLOT-1 (DEFINE/{0} narrowing), SLOT-2 (reason not named) |
| D4 retire the callout half of the conjuncts | agrees: the conjuncts read no callout bit, `PF_KIND_CALLOUT` exists, argument recorded at both | SLOT-3 (bit unnamed in --emit-facts), SLOT-6 (registry column still says the opposite) |
| manager: prefilter erased per site by width class; 1b declines | agrees: `frag_row` (check -> epsilon, consume -> any*), `NFA_ERASED_CALLOUT` on both, `pf_admits` row `callout` declines, `-fprefilter` refuses | the any* branch of `frag_row` is unreachable at 1b (prefilter declined); fine as stage 4's input |
| FR1 backtracking-order answer, oracle = libpcre2 with NO_AUTO_POSSESS/NO_START_OPTIMIZE/NO_DOTSTAR_ANCHOR | agrees: tests/callouts/co_oracle.c:19-20, 88-89 | §9.1's "backtracker leg" is superseded by the ruling (no separate backtracker), as ruled |
| verify refused | agrees: "module 'callouts' is enabled but the callout attribute 'verify' is not implemented yet" | - |
| D6 stage 0 before 1b | NOT met on this base | SLOT-7 |
| D8 callee give-up does not escalate | agrees: `run->callee_gave_up` set on the give-up row only, read by the tiered wrapper's `result != FRAMES || run.callee_gave_up` (emit_comb.c:261) | - |

## PROBED-AND-HELD
- callsite_rows lift (callsite_rows.c:104-117): ONE table, `conv` on the callee facts, row order for `matchfn` = §1.6's emitted order (-1, give-up, internal, utf, startpos, unset-var, reserved, width(9), bound(10), success); for `part` the old text by construction (span, give-up..reserved, then no-match fall-through; `.vm = !f->dfa` as before; `giveup` NULL -> prop). Read, and the emitted block of `(\d+)(?C"see")x` matches row-for-row.
- §1.10 table: 11/11 examples list the ruled class and tail (`--emit-ir` callouts section); utf8 `.`, `[^a]`, `(?i)k`, `\x{100}`, `\p{L}` before a site stay once-per-match (the class runs before encoding lowering).
- §1.9 rows: lookbehind, `(?1)`, `(?R)`, called DEFINE refused by name; uncalled DEFINE site accepted; lookahead site supported (once-per-start, no tail).
- `ncap` = pattern groups + 1 under `--no-captures` (`(a)(?:(b)|c)(?C"g")(d)` -> ncap 4, NCAPS 1).
- Spellings: `(?C"a__b")`, repeated attribute, `verify`, `(?C256)`, `(?Cx)`, `(?C1)?` refused as designed; `(?:(?C1))*` repeated.
- Not probed: §1.9 row 4 (a delivering lib import) through a real .rxt; runtime class-bound counting (another lens's).

## STANDING QUESTIONS
**Siblings.** (1) The `pf_admits` construct rows + the `-fprefilter` refusal chain: the callout is the FOURTH construct row (backref, linked-call, var, callout) and the first to break the shared shape; unification proposed in SLOT-5 (a `refuse` column). (2) The attempt-scope family (SLOT-6): `RF_CROSSES_ATTEMPTS` (registry column, read by compound A3), the start-set seek conjunct and req-handoff conjunct (g) in emit_dfa.c - three sites for one fact, now giving the callout two answers; unify by deriving a kind bit from the column and having both conjuncts read it. (3) Per-kind facts outside kindrow.def: `pcrec_ast_is_core` (definitions.c), `PF_KIND_*` (kinds.c's eight `pcrec_has_*` walks, each its own whole-tree recursion), the leaf list repeated in 43 switches, `vm_cost`'s zero-cost list, and the nullable/min-0 arms - all family 8 ([DEC-KINDATTR]) members that 1a left as code.
**General form + unlocks.** One per-kind row (kindrow.def) grown by three columns: ARITY (leaf / l / l+r spine / call back-edge), CORE (definitions.c), and a PF_KIND bit name; plus one declared row VARIANT mechanism (SLOT-9). Unlocks: the 43 leaf arms collapse to `pcrec_ast_visit` or a row read (the -Wswitch alarm moves to the .def's static count, which 1a already built), `pcrec_pattern_kinds` becomes ONE walk OR-ing each node's row bit (eight walks -> one; SLOT-3's name table generated from the same .def, so it cannot drift), nullable/minw read TEXT. Triggers: the next AST kind (verbs: `(*COMMIT)` etc., which also need the attempt-scope bit of SLOT-6) or the next per-kind edit touching three or more of these walks; stage 2 (`code-c`) reuses A_CALLOUT and is NOT a trigger. Cost argument: 1b paid ~43 leaf arms for one leaf kind; the next leaf kind pays the same again.
