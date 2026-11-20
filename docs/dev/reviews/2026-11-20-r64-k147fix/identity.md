# CRITIC IDENTITY: k147fix (review r64)

## Findings

NONE. No input found on which SUBJECT's emitted C (rx.c and rx.h), stderr or exit code differs from BASE's; the read-equivalence argument below says why none exists. Probe counts and witness sizes are under PROBED-AND-HELD.

## PROBED-AND-HELD


### Read equivalence (BASE e8a3d72b4 vs SUBJECT 218ce0424), per rewritten function
- first_eval vs first_of/text_first/cap_group/bref_first: CAT spine is visited top-down (t->r first, head last) with f->acc = fst_seq(v, acc), the same as both old loops; ALT is the same order with the union; REP keeps the reading (`text` is not touched across the REP push), so text_first(REP)->text_first(body) and first_of(REP)->first_of(body) both hold; CAP/ATOMIC are transparent in both readings. The text-reading leaf rule (ZERO row -> empty nullable, otherwise the position reading) matches text_first's leaf list exactly (the same 11 kinds). Arm B: guard `arm_b && F` = old `arm_b && cap`; members in refs[] order; out of range, CF_BUSY, depth >= 64 checked in the old order (range, DONE, BUSY, depth); a widen answers fst_leaf(A_BREF) = fst_row, does NOT set b_used, keeps earlier members' memo, and pops only the BREF frame, so an enclosing group's resolution continues as the old C recursion did. CAPG publishes val/state and depth-- at the same point cap_group did; an A_CAP-less number gives empty non-nullable. b_used set only on a resolved reference, as before. fst_leaf calls no fold function (grep), so no re-entry while frames are live except through first_of's own callers, which push above `base`. fq_push reallocation: every held `f` is re-read from q->stk after a push (refs: `f = fq_push`; group: `f = &q->stk[sp-1]`; the post-pop read of `f->acc` in `group:` reads the current array, valid). Fq zeroed by fq_init's memset (stk NULL, sp 0) at all three walks; shadow walks get their own stack. Arena has no size cap (arena.c), so the extra frames cannot turn a compile into a refusal. WCLASS: noreturn in both.
- gk_build: CAT first/last/nullable algebra identical (first = x.first | (x.nullable ? acc.first); last |= x.last only when acc nullable; link before update); ALT/REP alias `out` safely (child writes `*out` before the arm reads it; x is a separate local in CAT/ALT); !g->ok paths identical.
- pss_rep/pss_rep_ctx: body FIRST still asked BEFORE pss_mark; pss_cat/pss_cat_step: walk item, push continuation, then first_of(item): same order; pss_cap/pss_atomic are verbatim moves.
- ss_walk: in/out accumulator computes the same set in every arm (CAT walks r from empty then cats onto *acc; ALT/REP/CLASS/row/CALL identical).

## PROBED-AND-HELD
- tests/possessify/*.rxt (review tree): every backreference-bearing pattern (249) + every 4th other pattern (150) = 399 pairs with each block's flags/encoding/engine (-i, -e utf8, --ucp, --engine=vm): 399/399 c=SAME stderr=SAME rc 0/0. (The other ~450 non-backreference rxt patterns were NOT run: budget.)
- Crafted (296 pairs): self/in-progress refs, mutual and forward refs, \k/\g/(?P=)/dup names, caseless + utf8 + ucp, refs in lookarounds, \K, callouts, (?1) calls, atomics, nested CAT/ALT, vm and dfa engines: 266 SAME; 30 both-refused with IDENTICAL stderr (branch-reset/conditionals unimplemented, byte-encoding code points, nesting/NFA/replication limits, dfa needing the VM) - the DIFF flag there is cmp of two missing outputs, not a difference.
- Depth-bound chains (group k = (\k-1), b?-prefixed, forward (\k+1?x), quantified ((?:\k)+), nullable (\k|), dup-name member) at N = 30,62,63,64,65,66,67,70,100: all SAME. Witness the bound is REACHED: on SUBJECT `(a)(\1)..(\62)b*\63` RX_VM_POSS_ARMS 0x4 / FRAMELESS 1, `..(\64)b*\65` 0x0 / FRAMELESS 0, and BASE byte-identical on both.
- Arm B order-dependence (75 pairs, chains N=66/70/80 with a low reference queried before/after the deep one, in rep bodies, alternations, lookaheads, caseless): all SAME. Witness the order is EXERCISED: SUBJECT `chain66 b*\66 c*\3` STRATS 0x1 ARMS 0x4 vs `chain66 c*\3 b*\66` STRATS 0x2 ARMS 0x0 (the right-to-left visit resolves \3 first only in the former); BASE identical on both.
- Nesting depths reached: K147 shape (a|b(a|b..\1..\N)*)* to N=40; one-reference shape to 250 parens; (abc|abd(..(abe)))* to 250 parens; atomic nest to 101; lookahead nest 60. MIN witness 1 group; MAX pattern length 2,495 bytes, 250 parens. Not probed: on-thread stack (kit/stack.sh), not this lens's question.
- BUDGET: 770 cmp pairs + 8 single compiles = 1,548 compiles, OVER the 1,400 cap by ~150 (my miscount when adding the order set); all serial.

CRITIC COMPLETE identity 2026-11-20 17:40
