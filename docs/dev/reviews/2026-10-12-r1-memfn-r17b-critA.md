# r17b critic A: correctness of the emitted code (R17-b, `pf_terms_mask`)

Subject: commit 174f3e320 (lane/r17b) against 010b612c9. Read-only; no `make`
was run. Probes were compiled with gcc 15.2 under `gnutimeout`, against the
lane's own `build/pcrec` (it already contains `pcrec_mfk_w8`) and
`build/libpcrec.a`. The probe sources are in
`/home/pcrec/projects/pcrec/worktrees/memfn-slot/r17b_critA_scratch/`
(probeA-F.c).

**Verdict: 0 BLOCKER, 1 SHOULD, 3 NIT.** I found no wrong answer, no
over-read and no UB in any emitted text the commit produces. The one SHOULD
is a kit contract gap that no live pcrec site reaches today.

## What was checked, with the evidence

| claim | evidence | result |
|---|---|---|
| W8 term masks are EXACT (no lane above a member is ever flagged, so no verify is needed) | probeA, exhaustive. `eq` over all b, `range` over all (L, W in 1..128) and `cube` over all 3^8 (M, V), each with every x in every lane and 4 neighbour fills (random, 0x00, 0xff, x+1). It also checks that the low 7 bits are clear and that `lane_mask` carries nothing above bit 7 | 0 bad |
| `lane_mask` pack and `first_lane` give the lowest address | probeA: a member at each byte k of memory gives `first_lane` == k. The multiply's 64 partial products land at distinct bits (8i + 7j + 7 is injective on 0..7 squared), so no carry is possible | ok |
| stateful == stateless for ANY `lo` sequence, both `end_back` values, direct and complement covers, wrapping ARC, a 4-term `\w` cover with a CUBE | probeB: 7 real artifacts (`[0-9]+abc`, `[a-z]\b` (eb 1), `\w+@`, `x\|[0-9]`, VM `[^x]yz`, VM `[\x00-\x10\xf0-\xff]b` (ARC 0xf0 width 33), VM `[^0-9]+q`). Each takes 16M uses with non-monotone `lo`, `lo` jumping past the cache, `lo = got`, `lo` near `n`, `lo > n`, n = 0..300. Buffers are exact-size heap allocations under ASan+UBSan, then repeated at -O3. The reference set is hard-coded per pattern, never the kit's cover | 0 bad, no ASan or UBSan report |
| the same, COMPLETE at small n | probeD, exhaustive. The helper's control flow reads only membership, so every 2^n membership pattern was run for n <= 20, with every `lo` sequence of length 3 (n <= 11) or 2 (n <= 20) over [0, n+1] | 980M uses per artifact, 0 bad (d.c, eb.c, nd.c) |
| the probes can see a fault | sabotage: (a) the word loop reads `i + 7 <= hi`: ASan catches it; (b) the fill writes `top = i + 9`: 49,137 mismatches; (c) the inverted BE ternary under the BE simulation: 3.6M mismatches. The mutant `<` to `<=` in the cache test is EQUIVALENT (the shift by `top - base` yields 0 and falls to `i = top`), so it is not a gap | sensitive |
| endianness, with no `#if` in the body | probeB with `-U__BYTE_ORDER__ -D__BYTE_ORDER__=__ORDER_BIG_ENDIAN__` and `__builtin_memcpy` replaced by a reversing copy, on d.c, w.c and nd.c | 0 bad (a real BE target stays UNREACHED, as §6 says) |
| end-to-end answers: artifact vs its `--memfn=no-pf-terms-mask` twin, every `search_from` in 0..n+1, ASan+UBSan | probeC/E: 25 stateful artifacts (DFA, VM, the bounded DFA hat, `\b`, `\G`, lookbehind) plus 4 rev-end RELOCATE artifacts (`-fno-anchored-dfa`, `[a-c]\n?$` and others: the storage sits after the `if (!revend_tie) {` block, and the head is const) | 0 diffs |
| `goto` past the declaration (§7.2) | `gcc -Wjump-misses-init` over all 25 stateful artifacts plus the 4 relocate artifacts; `_run` holds no `goto` | clean |
| over-read and under-read | the word loop reads only while `i + 8 <= hi`; the tail word reads `[hi-8, hi)` only when `hi >= 8`, otherwise byte by byte. Reads go below `lo` (down to `hi - 8`, never below 0): this is §4.3's floor row ("read below lo, down to 0"), and a stated floor declines | in bounds (ASan, plus G2's mprotect guard pages) |
| n = 0, `s == NULL`, `lo >= n`, and `hi` formed only where it cannot wrap | the initialiser copies the pointer and the length only; both guard spellings (`lo < c.n`, `lo < c.n && c.n - lo > 1`) precede the call; inside, `lo < hi`. Every `ctzll` argument is tested nonzero; every shift is < 8 | ok |
| strict aliasing, alignment, -O2/-O3 | the loads are `__builtin_memcpy` into `unsigned long long`; the probes are clean at -O1 under the sanitizers and at -O3 | ok |
| the guard on the bound `<stem>__c.n` and the trace trap | `pf_mask_use` (pffind.c:433-460) pastes only `lo`. The trace form traps on a mismatch between the bound and the live `s`/`n`, and G2's TRAP fixture is S853's detector | ok, but see S1 |

## Findings

### S1 (SHOULD): a use over a DIFFERENT subject or length is accepted and silently searched over the bound one

- **Where:** `memfn/src/compose.c:604-637` (`mf_use`) and
  `memfn/src/pffind.c:433-460` (`pf_mask_use`). `miss_is_end` at
  `pffind.c:123` compares the miss text with the USE's `n`, not with the bound
  `n`.
- **What happens:** `mf_locals` refuses a storage point whose `s`/`n` text
  differs from the define's (compose.c:665-670). Nothing compares a USE's
  hooks with that binding. The stateful use reads only the bound
  `<stem>__c.n` and `<stem>__c.s`.
- **Concrete sequence** (probeF.c, linked against the lane's libpcrec.a):
  1. define with `s="subject"`, `n="subject_length"`;
  2. `mf_locals` with the same texts;
  3. `mf_use` with `s="other_subject"`, `n="window_end"`, miss `MF_MISS_N`.

  Every call returns rc=0, `mf_art_end` too. The use renders
  `if (lo < t_pf__c.n) lo = t_pf__next_candidate(&t_pf__c, lo);`, a search of
  `subject[lo, subject_length)`. The walk row, given the same hooks, searches
  `other_subject[lo, window_end)`: the two answers differ, and the miss value
  differs too (`subject_length` instead of `window_end`). With `end_back` 1,
  a miss of `"window_end - 1"` also passes `miss_is_end`.
- **Why only SHOULD:** every live pcrec site passes
  `subject`/`subject_length` at define, locals and use. The const head stops
  a write to those names, and the trace trap catches a live mismatch in the
  probe build. So no artifact moves today.
- **Why it is still worth fixing:**
  - rev 2.3 (setfind.md §7.4, line 1188, r5 K3-2) dropped rev 2.2's
    "`mf_use` refuses a use whose `s` or `n` hook text differs". Its
    reasoning was "the use pastes no `s`/`n`".
  - But the use's hooks are still the host's statement of the range it is
    asking about. The kit answers a different question without a word, and
    only a trace-build run over a corpus that happens to reach the site would
    notice.
  - The `[OPT-ENDWIN]` clamp (`window_end`) is exactly the kind of `n` a
    future host change could hand to a use.
- **Fix (one comparison):** on a `decl_point` site, `mf_use` refuses a stated
  `s`/`n` whose text differs from `def_s`/`def_n`, through the same
  `same_text` that `mf_locals` uses. This is a static, define-time-class
  refusal. The trace trap stays as the run-time line.
- **Sabotage:** the plant renames the use's `n` in one pcrec emitter; the
  refusal must fire.

### N1 (NIT): a false comment on the stateful row's floor cell

`memfn/src/pffind.c:487`: `PF_AT_ZERO`'s `[FLD_floor] = 0` says "nothing
below lo is read". `pf_terms_mask_ct` includes `PF_AT_ZERO`, and its overlapped
tail word DOES read below `lo` (setfind.md §4.2's floor row says so). The
cell's value is right (a stated floor must decline); its reason is wrong for
this row. Restate the cell in `pf_terms_mask_ct` with the true reason: "reads
below lo, down to 0: a stated floor declines".

### N2 (NIT): the trace's re-probe shares its source with what it checks, and skips fresh answers

`memfn/src/pffind.c:332-383` (`mask_render`):
- The trace re-probes only the CACHE answers. The word-loop, tail-word and
  byte-loop returns are not re-probed.
- Its oracle, `<stem>__member`, is rendered from the same cover as
  `<stem>__mask` (`mf_cover_member` and `mf_cover_mask_w8`).
  `mf_cover_check` holds `term_bits` to the set, but it never holds either
  RENDERING to it.

The exhaustive probes show both renderings are right today, so this is a gap
in the net, not a bug. Two cheap extensions:
- re-probe every return in the trace form, not only the cache's;
- under `MF_P_TRACE`, render the set's 256-entry bitmap (the site's own
  bits) as the trace's `__first` oracle instead of `__member`.

The second gives the trace an oracle that does not come from the cover.

### N3 (NIT): the "header-free" W8 block names `size_t`

`memfn/src/mfk.c:77`: `pcrec_mfk_w8_first_lane` returns `size_t`, so the
block compiles only after `<stddef.h>`. Every artifact gets it from its own
header first (checked: sp.h line 5 precedes the block), so no artifact
breaks. But the comment and `mf_shared_block`'s "artifact-independent
reference" text are not self-standing. Either say "needs `size_t` in scope",
or return `unsigned` (a lane index < 8) and cast at the use.

## Unlocks (general forms, each with its trigger)

1. **The membership-pattern model check as a standing test (probeD's
   form).**
   - The general fact: the helper's control flow and answer depend only on
     the membership bit of each byte, never on the byte values. So every
     2^n pattern times every `lo` sequence of length L is a COMPLETE
     verification at size n, not a sample.
   - It is independent of the author's sequence families. G2's setfind
     family says it was "NOT written blinded"; this check needs no blinding,
     because it enumerates.
   - It takes about 1 s per artifact at n <= 20 and L <= 3 (about 1e9 uses),
     and it reaches every path: the cache hit, the cache miss to `top`, the
     word loop, the tail word and the byte tail.
   - Trigger: any byte change to `next_candidate`'s control text, or any new
     width behind the same body. At a SIMD width W, take n up to about 3W.
     The §8.3 ring form needs it before it is built.
2. **The exhaustive per-lane primitive check (probeA's form).**
   - 256 x 128 x 256 x 8 lanes runs in under a minute and is complete for
     `eq`/`cube`/`range`. A test of the identity reference
     (`mf_shared_block(8)`) is the natural home.
   - Trigger: any byte change to the W8 block, or the first W16/W32 sub-block,
     each checked lane by lane against the same scalar predicate.
3. **"Bound hooks" as a row column, not one row's special case (S1's general
   form).**
   - A row that keeps storage declares the hooks its storage BINDS, today
     `{s, n}`.
   - The composer then refuses, in one place, a locals or a use whose bound
     hook text differs. It also refuses a stated `miss` that is not
     expressed over the BOUND `n`.
   - Trigger: the second stateful row (the ring or the adaptive switch,
     §8.3/§9), or the first host whose `n` hook is not a const parameter
     (the `inputs_const` unlock, §17).
