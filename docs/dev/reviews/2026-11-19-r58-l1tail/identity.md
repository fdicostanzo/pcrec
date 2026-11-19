# identity

## Findings

### IDENT-1 — the nested-lookaround family still overflows the compile-thread budget when the lookaround is QUANTIFIED (pre-existing, VM cost walk; outside the commit's code)
CONFIRMED. severity: answer (SIGSEGV in pcrec_compile on a PCREC_COMPILE_STACK_BUDGET=442368-byte thread, limits.md 3.10's contract). effort: medium (the same pointer-only-descent split on vm_cost's recursion) + small (two DEPTH rows). blast radius: any caller compiling on a budget-sized thread; patterns nested >=180 deep with a quantified lookaround.
- Repro (subject driver built by tests/thread/run_compile_stack.sh KEEP=1, against the subject libpcrec.a): `compile_stack_driver 442368 PAT all 0`, PAT = `(?=a|b` x N + `c` + `)*+` x N. Dies (exit 139) at N>=180 (bisected). `)?` x N dies at N>=219; NEGATIVE `(?!a|b` ... `)*` x N dies at N>=234. At N=250 on a 4 MB thread the subject's hw: `)*+` 607768, `)?` 503768, `)*` 471768, lookbehind `(?<=a|b`..`)*` 445312 (budget 442368).
- Not this commit's regression: the base dies on the same patterns earlier (req.c, hw 1305648 at 4 MB), and the negative form (no req item walk) is 471768 on BOTH trees. gdb bt at the overflow: ~210-250 levels of vm_cost -> vm_cost_rep -> vm_cost_atomic/look/alt/cat (src/gen/emit_vm.c:3031 vm_cost, :2440 vm_cost_rep -> vm_cursor_applies leaf at :2126). ~1.9-2.4 KB per nesting level.
- Also near the edge (fits, no margin): unquantified `(?=a|b` x250 `c` `)` x250 = 431768 (97.6%), `(?=a+|b`.. 438424 (99.1%), `(?=a|bc`.. 435880; worst frame there is vm_emit_node/vm_look/vm_alt/vm_cat (gdb).
- Why it matters for this review: the commit message's "stackdepth look@250 back to 204552 B" is true of the script's family `(?=` x250 `a` `)` x250 only; tests/thread/run_compile_stack.sh DEPTH_FAMILIES has no quantified-lookaround or lookaround-with-alternation row, so the family is not covered (a population nobody counts).
- Files: src/gen/emit_vm.c:3031, :2440; tests/thread/run_compile_stack.sh (DEPTH_FAMILIES).

### IDENT-2 — the new manifest comment calls all 10 entries zero-width-assertion patterns and "never-match by construction"; one has no assertion and two match under -e utf8
CONFIRMED. severity: doc. effort: trivial. blast radius: a reader reusing the manifest as a never-match list for utf8.
- `x[^\x00-\xff]y` contains no zero-width assertion (its emptiness is the byte universe's empty class).
- The census compiles at the DEFAULT encoding (byte; `--features all -p rx`, run_dfa_stamps.sh:635), where all 10 are never-match. Under UTF, libpcre2 (kit/oracle.sh ... 0 utf) MATCHES two of them: `(?i)(?=k)(?-i)[^kK]z` on U+212A KELVIN SIGN + `z` -> M 0 4; `x[^\x00-\xff]y` on `x`U+0100`y` -> M 0 4. pcrec -e utf8 (both trees) agrees (match 0 4) — so no answer bug, only the unqualified wording "each is a never-match pattern by construction". Suggest: "never-match under the byte encoding this census compiles at".
- File: tests/codegen/run_dfa_stamps.sh:951-954.

## PROBED-AND-HELD

- (a) source read: old order u=rr_unit() (pure, req.c:702) -> [look: ahead++, rb_walk(a->l,&t[0]), ahead--] -> item from t[0] -> rr_cat -> pd_cat; new order identical (descent then fin). rr_unit reads no walk state; rb_ctx_item path walks nothing and is unchanged. No local carried across the recursion in the old frame (only `behind`, recomputed). HELD.
- (a) -fstack-usage (Makefile default -O2 -g, -Ilib -Isrc): base rb_zero_item_into 6800 B (separate frame on the recursion path); subject rb_zero_item_into inlined into rb_walk (320 B both trees), rb_zero_item_fin 5648 and rb_look_item 1760 are noinline leaves off the path; objdump confirms rb_walk calls rb_zero_item_fin and itself. Every other req.c frame identical. HELD.
- (a) run_compile_stack.sh both trees (outputs identity/stk/): base FAIL look@250 and lookbehind@250 (exit 139), 37/39; subject 39/39, look@250 = lookbehind@250 = 204552; every other RECORD line identical between trees.
- (a) extra depth-250 shapes, both drivers, engine 0 and 2 (42 runs + 30 + 18 + bisect 24): lookbehind with content, alternating ahead/behind (two spellings), lookaround in capture/non-capture/atomic groups, (?:(?=a..)a)*, \b/\B/^/$ inside, caseless, classes, negative ahead/behind/mixed, alternation inside: all base-crash shapes now fit on the subject; all negative-only shapes identical between trees (204552). Exceptions are IDENT-1 (pre-existing VM walk).
- (a) identity: kit/cmp.sh base vs subject, 48 lookaround patterns x {default, -e utf8} = 96 calls (384 pcrec invocations) + 4 depth-250 patterns (look, lookbehind, alternating, lookbehind-with-content; 16 invocations): C, facts (byte,utf8) and stderr SAME on all; one c=DIFF is a kit artifact (`(?=\x{100})\x{100}` refused by both trees under byte, no rx.c written). Total ~400 compile/facts invocations + 20 + 20 for (b).
- (b) 10 new entries: subject AND base both emit RX_DFA_SCAN "empty" for each at the census flags (so base's manifest was red, the commit is correct). Oracle sweep: 10 patterns x {byte, utf} x 34 crafted subjects (incl. U+212A, U+0130, U+017F, U+0100, raw 0xe9/0xff, é UTF-8) = 20 compiles, 0 pcrec/oracle mismatches; oracle matches only in UTF mode, only the two in IDENT-2. Minimum witness: 2 code points + z / 3 code points.
- Minimum witness depth reached: 180 (IDENT-1); pool max nesting 250.
- Side effect disclosed: two driver segfaults left apport reports in /var/crash (system crash handler, not written by me; not deleted, outside my scope).

## Standing questions
- Sibling family: yes. This is the third instance of one rule ("the recursive frame holds only pointers; value-sized work in a PCREC_OWN_FRAME (noinline) leaf"): req.c's earlier [DD-10] split (rb_walk iterative spines + OWN_FRAME combining steps rb_cat_into/rb_alt_into/rb_gap_into/...), emit_vm.c's vm_cursor_applies/vm_cursor_try leaves, and now rb_zero_item_fin/rb_look_item. The open member is vm_cost's recursion (IDENT-1) and, near the edge, vm_emit_node's.
- General form + unlock: a stack-usage census gate — compile src/ with -fstack-usage, mark each function on a nesting-recursion path (a declared list or a call-graph SCC from objdump), and fail when any such frame exceeds a per-level budget (e.g. budget/250 minus the parser's share). Unlock: the DEPTH families stop needing a shape per construct (quantified lookaround slipped through). Trigger: the next DD-10 failure from an unlisted shape (IDENT-1 is one now). Cheaper interim: add `(?=a|b ... c)*+` and `(?=a|b ... c)` rows to DEPTH_FAMILIES.

CRITIC COMPLETE
