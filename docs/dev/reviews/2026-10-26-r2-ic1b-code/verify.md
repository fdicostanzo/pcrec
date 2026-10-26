# VERIFY — ic1b-code
status: COMPLETE

Compiler: worktrees/crit-ic1b-code/build/pcrec, features classes,modifiers,callouts (+lookaround/all as needed). Scratch: verify/.

## ADV-1 HOLDS
`a(?C"ref")b` -> rc 0; `gcc -O2 -c` -> `ref.h:276: 'rx_callout_ref' redeclared as different kind of symbol`. Severity answer-level as filed (emits uncompilable C, no refusal).

## CON-2 HOLDS
`(?*a+)(?C"x,once")a+c` (features +lookaround): rc 0, IR row `once-per-start`. Driver (rx_search, "aaabc", counting stub): fires `pos=0 start=0` THREE times in one attempt, then start 1 twice, start 2 once. co_choice (callout.c:87-90) lists `case A_LOOK` among false-returning kinds, never reads atomic. Contradicts class-2 bound and once refusal; fire counts only (no match-answer change), so "answer" = refusal-contract.

## CON-8 HOLDS
`--emit-facts --callout 1:consume --pattern 'a(?C1)b'` req_set_maxoff `97:0,98:1`; named twin `a(?C"x,consume")b` gives `98:unbounded`. `--emit-facts --callout 9:bogus` rc 0 (silent); `--count-groups --callout 9:consume` prints 0 rc 0.

## ADV-3 HOLDS
bash `=~` of run.sh:2790 regex on `callout 13once` matches, captures `13:once`. `pcrec -o o c.rxt` -> `[value-shape] c.rxt:3: 'callout' wants ... (got '13once')`. rxt_source.c:3803 requires ' '/'\t' after digits. Harness passes a file pcrec refuses.

## CON-1 / ADV-5 HOLDS (same defect)
`a(?C"x,")b` rc 0, binds rx_callout_x. (CON-1's extra: `--callout 1:` empty list accepted - spec-silent, not re-checked.)

## SLOT-1 HOLDS
`(?(DEFINE)(?<d>a|b))x(?C"f,once")` and `(?:a|b){0}x(?C"f,once")` refused ("a quantifier, alternation or call before it can be backtracked into"); `(?(DEFINE)(?<d>a))x(?C"f,once")` accepted. Over-conservative only; sound.

## SLOT-3 HOLDS
`--emit-facts --pattern 'a(?C1)'` kinds `none`; `(a)\1(?C1)` kinds `bref,live_capture`. facts.c:683-690 name table has 7 names; _Static_assert pins `PF_KIND_COLLAPSIBLE_REP` (bit 6) as last, so the new bit 7 (facts.h:282) passes it silently.

## CON-5 HOLDS
`(?:a(?C1)){0}b`: header RX_CALLOUTS 1, RX_CALLOUT_BINDINGS "rx_callout_1", e.c references rx_callout_1 0 times, IR `callout-sites 0`; `--emit-main` refused ("cannot define the binding rx_callout_1"). Doc/design-level.

## CON-6 HOLDS
`(?C"x")` (IR class `once-per-match tail`), rx_iter over "ab": `fire pos=0` / `match [0,0)` / `fire pos=0` (not-empty retry, no match) / `fire pos=1`... Second fire at one start is real. Contract-text only today.

## CON-3 HOLDS (and the gate would catch it)
`--list-syntax | grep -vc '^#'` = 143; page line 2275 says 142 rows, line 2346 `(?C1)` is `unbuilt`/PLANNED; `(?Cx)` row absent from page. compliance_section.py --check is read-only (reads the doc, runs build/pcrec --list-syntax); I ran it: `FAIL: ... generated construct index has drifted` (142 vs 143 rows). So `make test` would fail on SUBJECT until `--write` is run. Fix is mechanical.

## CON-4 HOLDS
`grep -rn no-callout docs/spec` -> 0 hits; ir_listing.md §3.1.1¶1 token table (lines ~83-95) lists no-backreference/no-linked-call/no-variable/... but not no-callout. (Note text with "[INLINE-C]" seen in earlier IR output.)

## CON-9 HOLDS
`a(?C` with callouts -> "malformed callout: ..."; without -> "(?C...) requires module 'callouts'". Low.

## CON-7 HOLDS
lib d.rxt (`zzzz(?C"inlib")`, name d) + t.rxt `target t2 = foo` pattern `x(?C1)y(?&d)`: refusal "t.rxt:4: target 't2': a callout inside a group reached by a subroutine call ... (pattern offset 4)". Offset 4 is the `1` in t2's own `(?C1)` (the d site also happens to sit at offset 4 in d.rxt, so my probe cannot show which; the message names neither the lib nor d.rxt, which is the finding). Fine as doc.

## ADV-2 HOLDS
od -c of the refusal shows raw 033 and \a inside the quotes: `unknown callout attribute ' 033 [ 3 1 m R E D \a '`.

## ADV-4 HOLDS
`.rxt` `callout 13 consume once` -> `pcrec: a callout declaration is N ATTRS (... got '13 consume once')`: no file:line, no [value-shape] tag (unlike the 13once refusal, which has both).

## ADV-6 HOLDS (read, not replicated)
run.sh:1652-1677: `src="$mdir/$arg"` (no `/` check); `obj=".../manifest_$(basename "$arg" .c).o"` + `[ ! -f "$obj" ]` skip, so same-basename sources alias; `read -r kw arg rest` never tests `rest`. Matches the finding. Maintenance.

## SLOT-2 HOLDS
`\w+(?C"f,once")` -> "callout at offset 3 is marked once but can fire again: a quantifier, alternation or call before it can be backtracked into; make the quantifier possessive ..." - names no culprit construct/offset (the offset is the site's), and the possessive hint is generic.

## CHK-2 HOLDS (read)
verify_callouts.py:75 and gen_diff.py:154 return 3 on ANY nonzero gcc status of co_oracle.c; run_callouts_tests.sh:55 and :67 map 3 to a `note` (SKIP). A broken oracle driver skips green.

## CHK-3 HOLDS (read)
run_callouts_tests.sh:120 `[ "$rc" -gt 128 ] && [ "$rc" -ne 124 ]` accepts any fatal signal.

## EMIT-1 HOLDS (cost only)
--engine=vm: `a+b` FRAMELESS 1 STRATS 0x1 BYTES 815; `a+(?C"x")b` FRAMELESS 0 STRATS 0x2 BYTES 2242; `(?C"x")a+b` FRAMELESS 1; `\w+(?C"x")\s` 0 vs `\w+\s(?C"x")` 1. Speed/size cost of the design-chosen OPAQUE path; no answer effect.

## EMIT-2 / SLOT-7 HOLDS; a rebase fixes the text
SUBJECT src/gen/emit_dfa.c:2084 says "...a generated call site that invokes an rx_matchfn traps on one." Main (`git show main:src/gen/emit_dfa.c`) says "...propagates one." (stage 0 merged). So rebasing/merging onto main resolves the comment; the abi number then needs re-pin (main is at 88, SUBJECT claims 87->89), a merge-order matter, not a code defect.

## EMIT-3 HOLDS (read)
emit_vm.c:11971 field emitted when ncallouts>0, :12749 init, :9055 store in the give-up edge; no tier read of it found in the callout path. Trivial size.

## SLOT-4 HOLDS
rx_callout_%s/%d ternary at emit_vm.c:9009-9010, :10056-10057, emit_dfa.c:2650-2651, callout.c:322/325 (the refusal text, two format strings).

## SLOT-5 HOLDS (read)
select_engine.c:1005-1022: `has_callout` guard `!(has_bref||has_call||has_var)` before the pf_noun ternary - parallel if-chain beside the table.

## SLOT-6 PARTLY (read)
registry.c:1031 GROUP_XA_CALLOUT still sets the crosses-attempts flag (derive.c:390-396 reads it, internal.h:4510 defines it); emit_dfa.c:7925-7934 says "A CALLOUT IS NOT A CONJUNCT". The asymmetry exists as described; the "consequence" (compound admission A3 declines callout patterns) is plausible and sound. Not probed at run time.

## SLOT-8 HOLDS (read)
derive.c:77-80 `case A_CALLOUT: for (g...) f->kept[g] = true;` with comment saying A3 declines first.

## SLOT-9 HOLDS
internal.h:2333-2343 pcrec_ast_row patches `.text` for consume; kindrow.def keeps one row.

## SLOT-10 HOLDS (read)
callout.c:221-244 co_targets and :248-276 co_apply_decl are hand-written recursive walks; callout_nodes (callout.c:124, :302) already built.

## CHK-1 HOLDS (read)
gen_diff.py:304 prints "N artifacts with a checked firing-class bound"; the only floor test is `len(compared) < a.floor` (:309).

## CHK-6 HOLDS (read)
mech arm `callouts)` at run_sabotage_matrix.sh:1882; the header vocabulary list near :185-200 does not mention it (grep of that range: no 'callouts').

## Not verified
EMIT-3 read-sites beyond the cited grep; SLOT-6 consequence; ADV-6 not replicated; CON-1's `--callout 1:` empty-list sub-claim; CON-10 not in my list.

## Severity notes
- CON-2: no match answer moves, only fire counts and the `once` acceptance; "answer" in the refusal-contract sense.
- CON-3: gate WOULD fail `make test` (compliance_section.py --check run, FAIL), so it is a must-fix-before-landing, not a silent drift.
