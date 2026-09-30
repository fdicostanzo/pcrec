# k67 report -- K67 compile time: [OPT-CLOSURE-CTX] + [OPT-RETRY-REUSE] (2026-09-29, lane k67, opus)

Branch `lane/k67`, based on `lane/ucpu3` (U2) and merged with `lane/u2land`
(main + U2) at `613e6352`. The identity reference throughout is `lane/u2land`
`23645945` (REF below): the branch point with main and U2 both in it, so a
mover is this lane's and nobody else's.

## Headline

`\p{L}+ -e utf8 --features all -fcomments` (K67's own repro), same Mac, same
evening, CPU seconds (user):

| binary | CPU | stamps |
|---|---|---|
| REF (before) | **78.43 s** (86.65 s wall, load ~23) | `dfa`, `size-cap-retry` |
| + closure hash only | 1.16 s | same |
| + no context on an acyclic loop ([OPT-CLOSURE-CTX] both) | 0.95-0.99 s | same |
| + machine memo ([OPT-RETRY-REUSE]) = lane tip | **0.37 s** | same |

The artifact is byte-identical at every step (`cmp` on `.c` and `.h`, same
`-o` basename), and it still takes the same two-rung drop ladder.

Other witnesses (CPU s, REF -> tip): `(?:\p{L}?)+ -e utf8` 26.57 -> 0.49
(nullable loop body: the context is genuinely needed, so this one is all
hash); `\P{L}+` 44.84 -> 0.26; `(?:\p{L}+)\z` (the bench's whole-subject form)
116.57 -> 0.57.

## 1. [OPT-CLOSURE-CTX] -- the measured mechanism was the HASH

The row said 466 ns per ctx!=0 visit against 6 ns for ctx 0. That is not a
hash probe; it is a probe CHAIN. Both tables in `src/ir/dfa.c` (the
(state, ctx) memo and the context intern table) hashed a key
`(hi << 32) | lo` as `(k * FNV_PRIME) >> 20 & (cap - 1)`. A multiply only
carries bits upward, so `hi` (the NFA state) reaches product bits 32+ only
and no table under 4,096 slots sees it at all; FNV's sparse prime
(0x100000001B3) leaves a small `lo`'s contribution to bits 20.. near zero.
Every key of a closure landed in a handful of home slots and linear probing
walked the cluster. `hash_slot` (the splitmix64 finalizer, then mask) fixes
both tables; `PCREC_HASH64_MUL` is deleted and its `limits_check.sh`
allowlist entry with it (37/0, unchanged count). This alone: K67 78.4 ->
1.16 s; `(?:\p{L}?)+` 26.6 -> 0.49 s.

The row's fix (1) was also built, because it is exact and still pays:
**a loop whose entry lies on no epsilon cycle opens no context.** The
context's only reader is the redirect, which fires when the walk arrives at
a loop entry the walk has open -- an epsilon cycle through that entry, by
construction (every open context was opened by this walk and everything
since is epsilon edges). `eps_cyclic` computes the flag per NFA state
(iterative Tarjan over exactly the closure's own continue-edges, every
assertion counted passable, so it can only over-keep a context); `clo_walk`
opens a context -- and tests for a redirect -- only on a flagged loop. The
exactness argument (projection of contexts onto their cyclic loops commutes
with every walk step; a merged second arrival can add nothing, not even
earlier, because that needs an epsilon cycle through the merged loop's
entry, which proper nesting forces) is written at `eps_edge`. One pass of
K67 (`--max-emit-bytes` raised, no ladder): 0.42 -> 0.34 s on top of the
hash; `[\p{L}\p{N}]+\s` 0.56 -> 0.46 s.

Neither change can move a byte by construction (a membership table's hash;
a memo key the walk provably cannot distinguish), and neither did:
cls_identity on the closure-only commit, 15,843/15,843 (below).

## 2. [OPT-RETRY-REUSE] -- one memo, keyed by content, no per-rung clause

`src/opt/dfamemo.c`: `pcrec_build_min_dfa` = `pcrec_build_dfa` +
`pcrec_minimize_dfa` (skipped on an overflowed optional machine, exactly as
`build_anchored_dfa` did), and all four DFA build sites in
`src/core/compile.c` go through it (forward, reverse, ENG_ATTEMPT, the
anchored machine). The memo is `compile_driver`'s local `DfaMemo`, lent to
every attempt via `Ctx.dfa_memo`, freed at all five exits after it exists;
its storage is its own arena (allocation failures route through the live
attempt's `pcrec_ctx_nomem`).

**The key is every input construction reads**, found by grep of `cx->`,
`nfa->` and `d->` reads in `dfa.c`/`minimize.c`: the NFA's states (compared
field by field -- `NState` has a padding byte nothing initializes) and
count; `prune`/`reverse`/`maxstates`/`root`/`optional`; `opt->encoding`,
`opt->engine`, `opt->max_subset_elems`, `opt->max_auto_dfa_elems`; and the
PRIOR `cx->subset_elems`, because the element budgets are cumulative and a
hit must mean "this build would have succeeded with this machine". A hit
restores a deep copy in a fresh build's ownership shape (`st` on the heap
for `job_cleanup`, per-state arrays in the attempt's arena, views that
shared a list still share one, no interning hash -- only `intern` reads it)
and charges the same `subset_elems`. Only clean builds are stored.
`pcrec_build_dfa`'s header now names the key beside the reads: a new input
read there must join it.

Nothing is keyed on the rung. A rung that changes a construction input (the
[OPT-4] collapsed NFA, a raised cap, [SEL-1]'s `dfa_disabled`) misses by
content and builds; a rung that does not (the drop ladder's two rungs, the
VM size-term ladder's K rungs, whose hybrid prefilter machines do not depend
on K) hits. That is the general mechanism the row asked for.

One ordering change, deliberate: the forward and reverse machines were built
then minimized (`build F; build R; min F; min R`) and are now
`build F; min F; build R; min R`. Minimization reads and charges nothing the
reverse build reads (no `subset_elems`, no option), so the machines are the
same; only arena interleaving moves, and the identity sweeps are the check
that nothing depended on it.

K67: 0.99 -> 0.37 s (a one-pass compile is 0.30-0.32 s, so the two drop
rungs now cost ~0.06 s where they cost two full passes). Peak RSS 15.9 MB
(REF 17.7 MB). `leaks --atExit`: 0 leaks on K67, on a VM unroll-ladder
witness, on two [SEL-1]/[OPT-4] fallbacks, on the K59 witness and on a
refused compile.

## 3. Correctness: byte identity

**`scripts/cls_identity.py --ref REF --bin <tip binary> --control --jobs 2`**
(tip = `273d2902`'s binary, i.e. both mechanisms):

    triples: 15843  {'identical': 13632, 'both-refuse': 2211}   movers 0 in every population
    populations (dedup'd): corpus-asw 3636, corpus-x 10149, bench 1228, classes 766, witnesses 64
    REACH: baseline 1425, candidate 1425 of 8294 utf8 triples (unmeasured 1440 / 1440)
    CONTROL 1 (instrument, one byte flipped): PASS
    CONTROL 2 (compiler plant, 1,619 triples): 750 movers, all utf8: PASS
    RESULT: PASS -- 15843/15843 identical or both-refused   (548 s)

**`scripts/emit_sweep.py --ref REF --bin <tip binary> --jobs 2 --no-self-check`**
(the self-check -- two builds of REF against each other -- was skipped for
box time; cls_identity's two controls are this lane's positive controls):

    c-default    population 4233  both_ok 3802  both_refuse 431  movers 0  asymmetric 0
    c-vm         population 4233  both_ok 3803  both_refuse 430  movers 0  asymmetric 0
    emit-ir-vm   population 4233  both_ok 3803  both_refuse 430  movers 0  asymmetric 0
    composition  351 files, 35 producing, 102 artifacts           movers 0  asymmetric 0
    dumps        7/7                                              movers 0
    DELIVER witness: OK       rc 0   (135 s)

REACH of the memo specifically (K35: identity over artifacts that never took
a ladder proves nothing about the memo): every artifact stamped
`size-cap-retry` or with a non-default `_UNROLL_K_WHY` ran two or more
attempts over an unchanged NFA, so its later attempts restored rather than
built -- the census below counts that population (LADDER_POP).

The closure-only commit (`a5e36d56`'s binary) was swept first on its own:
`cls_identity.py --ref REF`, 15,843/15,843 identical-or-both-refused
(13,632 identical, 2,211 both-refuse), 0 movers in every population, REACH
1,425/1,425, control 1 PASS, 539 s at 2 jobs.

## 4. Compile-time census

CENSUS_FINAL

A first corpus-only cut (3,378 distinct corpus pattern lines x {byte, utf8}
at `--features all`, the script's earlier population): REF 33.73 s -> tip
29.48 s in total, ladder population 15 rows (2.60 -> 2.30 s). The corpus is
cheap, so the corpus total moves by the hash's share of the ctx!=0 walks
(`k18_deep_nesting.rxt` 1.17 -> 0.27 s, `(*UCP)[^\s\d]+` 0.49 -> 0.04 s);
K67's shape lives in the classes population, which is why the census uses
cls_identity's triples.

## 5. Checks added

- `tests/resource/run_resource_tests.sh` **Section 1c** (`K67_CPU`, default
  20 s): `\p{L}+` (must still stamp `size-cap-retry`, [MECH-REACH]) and
  `(?:\p{L}?)+`, both `-e utf8 --features all`. Failing direction measured:
  REF is CPU-killed on both; the tip passes both. `tests/resource/CLAUDE.md`
  updated.
- `scripts/compile_time_census.py` (measurement, not a gate; scripts/CLAUDE.md).

No sabotage row. A plant that makes the memo key always match is detected by
every answer gate (the reverse build would get the forward machine); a plant
that drops ONE key field (say the prior `subset_elems`) has no corpus
witness I could construct, and the identity sweeps are what would see it.

## 6. What is not an event

- Not an `abi` event: no emitted byte moves (section 3).
- No `docs/spec/` hunk: nothing a caller observes changes except compile
  time, which `limits.md` §3.3 explicitly does not promise.
- `limits_check.sh`'s allowlist loses `PCREC_HASH64_MUL` (the define is
  gone); its pass count is unchanged at 37.

## 7. Validation

VALIDATION

## 8. Findings

1. **The row's diagnosis was right about WHERE and wrong about WHAT.** 99%
   of the time was the ctx!=0 path, but "~80x slower path" was a clustered
   hash, not the cost of carrying a context. The row's two candidate fixes
   were both context-shaped; the measured fix was a one-function hash
   change, and the context fix is worth ~20% on top.
2. **The same hash shape nearly bit a second table**: the context intern
   table used the identical `(k * FNV) >> 20`. It never mattered there (few
   contexts), which is how the first one survived: a hash that works on
   small tables and fails only on large ones.
3. **K67's REF time is load-sensitive in wall, not CPU**: 86.65 s wall /
   78.43 s CPU with load ~23 on this box; every number above is CPU.
