# flagspell findings (read-only research, 2026-10-23)

## Reproduction
`build/pcrec --engine=vm --emit-ir` (main tree). (?i)abc: 88-line listing, labels 5, events 13, RX_VM_PROGRAM_BYTES 634.
(?i:abc): 86 lines, labels 4, events 11, 577. Emitted C differs only by pattern text/header and this:
(?i)abc has an extra program entry `L0 label "empty"; goto L2` (rx_L0 then `goto rx_L2`), and its labels shift by one;
(?i:abc) goes straight into `consume [Aa]`. Consumes ([Aa],[Bb],[Cc]), flags, prefilter/start choice: identical.
Difference = exactly one A_EMPTY node (label + goto) = 57 bytes of RX_VM_PROGRAM_BYTES, in every pair below.

## Divergence point
src/parse/mod_modifiers.c:~505-525 (the `p[i] == ')'` bare-run branch): the bare option run mutates *cx->mods and RETURNS A
real node, `pcrec_ast_node(cx, A_EMPTY)` with not_repeatable=true. The caller concatenates it, so the tree is
CAT(EMPTY, CAT(a,b,c)) for (?i)abc, vs CAT(a,b,c) for (?i:abc) (the `:` branch ~527-560 returns the body itself).
Nothing later removes it: gen/emit_vm.c:9029 case A_EMPTY emits vm_lbl(entry,"empty") + vm_goto(next) (an extra label and jump);
ir/nfa.c:612 builds an N_EPS fragment (harmless for the DFA, epsilon-closed).
Same mechanism for `a(?i)bc` vs `a(?i:bc)`, and any bare run (`(?:)abc` and `a(?:)bc` produce the same L0/L2 "empty").

## Table (RX_VM_PROGRAM_BYTES, --engine=vm; DFA column: artifacts identical except header/pattern text unless noted)
| bare | scoped | VM bytes bare / scoped | DFA |
|---|---|---|---|
| (?i)abc | (?i:abc) | 634 / 577 | same |
| (?s)a.c | (?s:a.c) | 580 / 523 | same |
| (?x)a b | (?x:a b) | 450 / 393 | same |
| (?U)a+b | (?U:a+b) | 870 / 813 | same |
| (?n)(a)b | (?n:(a)b) | 450 / 393 | same |
| (?s). | (?s:.) | 266 / 209 | same |
| (?-i)abc | abc | 369 / 312 | same |
| a(?i)bc | a(?i:bc) | 625 / 568 | DIFFERS (see below) |
| (?i:abc) | [Aa][Bb][Cc] | 577 / 577 | same program |
| a(?i:b)c | a[Bb]c | 559 / 559 | same program |
| (?m)^a$ | (?m:^a$) | not measurable: 'm' requires module 'assertions' in this build | - |
Constant +57 bytes everywhere.

DFA, mid-pattern case: a(?i)bc vs a(?i:bc) differ in the facts: bare gives RX_REQ_RUN "none" / WHY "dominated" /
prefilter "memchr", scoped gives RX_REQ_RUN "614243@1/ffdfdf" / "emitted" / prefilter "handoff". So the stray EMPTY
in the middle of the CAT hides the required run from the fact pass (likely src/facts/req.c handling of A_EMPTY in a CAT; not traced).
A leading EMPTY (e.g. (?i)abc) does not change the DFA artifacts.

## Answers
Built --emit-main matchers for both engines on 9 subjects (abc ABC aBc xxAbCyy "a b" a.c a\nc aab ab) for the pairs
(?i)abc, (?s)a.c, (?x)a b, (?U)a+b, (?n)(a)b, a(?i)bc and scoped twins: all outputs identical. Semantics agree.

## Which is larger / what the extra does
The BARE spelling is larger (634 vs 577). The extra is dead weight: a label plus unconditional goto to the next label, no
consume, no capture, no choice. (On the DFA mid-pattern case it costs real optimization: lost required-run/handoff prefilter.)

## Where a normalization belongs
One line: drop (or fold into the CAT) the A_EMPTY at mod_modifiers.c bare-run return / the CAT builder in parse.c, or
skip A_EMPTY in vm emission of CAT; the not_repeatable flag is its only job.
