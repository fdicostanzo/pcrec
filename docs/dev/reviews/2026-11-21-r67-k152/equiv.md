# CRITIC EQUIV — r67 k152

## Findings

NONE. No EQUIV-n finding: the reading (a) and 175 BASE/SUBJECT byte-identity pairs (b) both hold. Details are under PROBED-AND-HELD; the vm_rev_emit sibling note is under SIBLING OF A FAMILY (measured under budget, so it is not a finding).

## PROBED-AND-HELD


(EQUIV lens: no defect found. No EQUIV-n findings; everything checked is below under PROBED-AND-HELD.)

### PROBED-AND-HELD (EQUIV)

Compile matrix, stated before running: 65 default + 33 x --engine=vm + 33 x --engine=dfa + 20 x -e utf8 + 24 nests (8 families x depths 2/10/60) = 175 BASE/SUBJECT pairs = 350 pcrec compiles, plus 3 subject --emit-main matchers and 14 subject stack.sh probes + 1 emit = 368 pcrec compiles in total (budget 400). Separately, gcc -fstack-usage -c of src/*.c (100 files) plus nfa.c at BASE, output under equiv/su/. No make was run.

(a) Read line by line (diff 2b4e56eab..62752e60c, src/ir/nfa.c):
- nfa_cat: forward is j=0 -> t, then j -> rs[j-1]. Reverse is j=0..nsp-1 -> rs[nsp-1-j], then j=nsp -> t. That is exactly the old order (rs[nsp-1], rs[nsp-2..0], t). Each compile_ast still runs before its frag_cat2 join; in the old code it was an argument of frag_cat2, and the local f it copied cannot be changed by the callee. nsp>=1 always holds (the arm is only reached with a->k==A_CAT), so the j==0 / j==nsp branches cover every case. Arena allocations (rs) and the ast_bare spine calls are unchanged. The `{-1,{0}}` initializer is dead (j==0 overwrites it).
- nfa_alt, nfa_rep, nfa_class, nfa_ctx, nfa_wclass, nfa_eol, nfa_splice: bodies are verbatim. That includes the order of nst/patch_push/frag_cat2 calls, the b->in_tail++/-- bracket, the ++b->splice_depth check and its pcrec_ctx_fail, the pcrec_ctx_fail in nfa_ctx, the early `return f` in the island branch, and the NFA_ERASED_COUNT set before any nst.
- A_WCLASS: the non-island path still reaches `break` (the old fall-through is kept). A_CALL: a non-splice call still reaches the LINKED-call fail.
- A_ATOMIC: the erase bit is set from the same bare `a` before recursing.
- ast_bare: it is re-applied once at compile_ast entry as before, and no arm is reached without it.
- PCREC_OWN_FRAME is only __attribute__((noinline)), so it has no semantic effect.
- Measured frames (gcc -O2 -fstack-usage): BASE compile_ast 384 B. SUBJECT compile_ast 32 B, with nfa_cat 176, nfa_alt 160, nfa_rep 224, frag_star 128 (unchanged), trie_key 96, trie_build 256 (unchanged).

(b) Byte identity, `cmp` of BASE vs SUBJECT rx.c (kit/emit.sh, --features all):
- default: 65/65 SAME, all rc=0. Covers every concatenation length (1, 2, 3, 8); trie-eligible and ineligible alternation runs (mixed in one alternation); */+/?/{n}/{m,n}/{m,} both greedy and lazy; nested-optional {0,n} tails; tail-$ bodies (nfa_eol); (?m) anchors; \b, \B and one-character lookarounds (nfa_ctx); lookbehind and end-anchored patterns (reverse machines); atomic and possessive (nfa_erase_by_row); (?1) and \g<n> splices (nfa_splice); empty branches; (a*)*.
- --engine=vm: 33/33 SAME.
- --engine=dfa: 28/28 SAME, plus 5/5 where both trees reject with identical messages.
- -e utf8: 20/20 SAME (island/wide-class builds; N_WCHAR reached: 2 artifacts carry island text).
- K152 nest families (litpost, nclitpost, litcompound, altnest, lookrep, atomic {1,2}? with y$, lookbehind+, \b{0,2}$) at depths 2/10/60: 20/20 SAME. The 4 deep rows where both trees refuse (emitted-size limit; NFA >131072 states, a pcrec_ctx_fail raised inside nst) refuse with identical messages, so the state-count path is equal.
- Oracle: 3 subject matchers ((?:ab|a){0,2}?b; the K152 witness at depth 3; (?<=ab|c[d])e) against kit/pcre2_oracle, 20/20 subjects agree.
- Witness depth reached: minimum 1 (flat patterns), maximum 250 on the stack.sh probes; byte-compared nests reached a maximum of 60.

### SIBLING OF A FAMILY
This is the K146/K147 mechanism (the mark's second use, each recursive arm in its own frame), applied faithfully. The dispatcher's own frame went from 384 to 32 B.
- The same shape is still unmarked in src/gen/emit_vm.c:5668 vm_rev_emit: a kind switch with CAT/ALT/REP arms inlined, 288 B, plus vm_revdet_rep at 720 B. It sits on the lookbehind-body path.
- Measured there: x(?<=(?:a ... b ...))y at depth 100 peaks at 66,960 B on the 442,368 B thread. Depth 250 is refused by the group-depth limit. So it is not over budget today.
- Other self-recursive walks found with 200 B or more of frame: ps_node 288, co_walk 304, anf_list 320, item_first 352, req_site_define 672. Six probes through possessify, callouts, atomic and alternation nests at depth 250 all peaked at or under 257,792 B.
- No sibling witness was found.

### GENERAL FORM + UNLOCKS
- General form: no recursive walk's frame may hold more than its own arm's locals. That is a measurable per-function invariant, and -fstack-usage already measures it.
- Unlock 1: a stack-usage census that lists every recursive dispatcher's .su figure, so marking is checked rather than trusted (internal.h says "nothing checks the marking itself"). Trigger: the next K-row of this family, or a new kind-switch walk.
- Unlock 2: mark vm_rev_emit's arms. Trigger: a DEPTH_FAMILIES row through a lookbehind body reaching more than half the budget, or a raise of PCREC_MAX_GROUP_DEPTH.

CRITIC COMPLETE
