# CRITIC SOUND: memfn-bspan

## Findings


### SOUND-1 (CONFIRMED; severity answer-if-built-literally / doc; effort trivial; blast radius every V stretch except sets whose tables are symmetric)
§4.1 spells the `bit` table in `_mm256_set_epi8` argument order (`-128, 64, ..., 1`: element 31 first) but the two nibble
tables only as `_mm256_set_epi8(<lo_t x2, 32 bytes>)` / `(<hi_t x2>)`, and the bullet defines `lo_t[l]` by INDEX l. Read
literally (lo_t[0] as the first argument, the order the text gives it), the shuffle reads lo_t[15-l]: wrong answers.
Repro (my own prototypes from the note's text, /var/tmp/pcrec-pcrec/scratch/crit-memfn-bspan/sound/a/gen_unit.py, the class
written in the test, python `re` per-byte membership, windows flush against PROT_NONE at both ends): `index` reading ->
DIFF on 14 of 16 sets (e.g. `[0-9]`: 126 wrong results of 10320; `[^\n]` 1563); only the empty set, `[\x80-\xff]` and
`[\x00-\x7f]` (tables constant over l) pass. `reversed` reading (element 15 first, as spike708 `nib_blk` does via
`reversed(v * n)`) -> 0 differences on all 16 sets, gcc 15.2 and clang, -O2 -march=x86-64-v3. Fix: write the
placeholders as `<lo_t[15], ..., lo_t[0]> x2` (or say "in set_epi8 order, element 15 first"), and state that table
values > 127 are written as signed (`v - 256`, spike708 `sc`) - the note is silent on that too. G2-V unit (§10) would catch
the literal build, so this is a text fix, not a design fault.

### SOUND-2 (CONFIRMED; severity design/maintenance (a check the build cannot pass as written); effort small-medium; blast radius every V mover at x86-64-v3, the C18 gate)
§10 says C18/simdfloor is "unchanged; it now meets `vs<j>` selectors" (only its floor re-pinned), and §2 calls the shape
"exactly vany's". It is not the shape C18 parses, on two legs:
1. tests/memfn/simd_floor_check.py:123-124 recognise a SIMD FUNC only as `^static inline size_t (\w+)(...)\n{\n    return
   \1__w(\d+)(...);\n}$` (HELPER likewise `static inline size_t`). §4.1/§5 spell `static inline __attribute__((always_inline))
   int rxa_mf1_vs0...`. Repro: my hand-built V artifact for `[0-9]{25}` (sound/b/c/dig25/onv.c, §4.1+§5 applied to the
   shipped build/pcrec x86-64-v3 artifact): SELECTOR finds 0 selectors, HELPER 0 helpers, while FLOOR_CALL does match the
   replaced `    return rxa_mf1_vs0__body(rxa_mf1_s, rxa_mf1_c);` -> leg (c) reports "a deleted line that is no SIMD FUNC's
   floor call" on every V mover.
2. C9-x86 (simd_floor_check.py:366-381) requires `<fn>__w<VW>` to be DEFINED (nm ` t `) in the `gcc -O0` object, "the region,
   not the consumer's flags, supplies the ISA". §4.1's `__w32` is `always_inline`: `gcc -O0 -c onv.c; nm | grep vs0` -> 0
   symbols (inlined away). Once leg 1 is widened, this leg fails on every V mover.
The always_inline is load-bearing for G-2/F2 (§6: the timed shape), so the fix is in C18 (widen SELECTOR/HELPER to the
`int`/attribute spelling; re-express the -O0 nm proof for always_inline helpers, e.g. nm on a noinline-forced copy or
check the inlined ymm use in rxa_search) and §10 must say C18 CHANGES, with its own controls (a check change is a check
design: learnings §3). Not answer-affecting.

### SOUND-3 (CONFIRMED; severity build (clang -Werror consumers, CLANGGEN=1); effort trivial; blast radius every V artifact at a w32 target compiled by clang)
At a w32 target §5's selector calls `__w32`, and §4.1's `__w32` never falls back to `__body` (K >= B by construction), so
`rxa_mf1_vs0__body` is an UNUSED `static inline` function in the main file. gcc says nothing; clang warns
`-Wunused-function`, an ERROR under `-Wall -Wextra -Werror` (the house GENCFLAGS, tests/codegen/run_codegen_tests.sh:424
with CLANGGEN=1; run_targets.sh's clang cells use the same flags). Repro: `clang -O2 -Wall -Wextra -Werror -c
sound/b/c/dig25/onv.c` -> "error: unused function 'rxa_mf1_vs0__body'"; the same file under gcc -Werror: clean. vany's
`__body` is always referenced (its helpers fall through to it on short spans), so V would be the first unreferenced
floor. C18 (c) needs `__body` to stay in the ON text, so the fix is an `__attribute__((unused))` (or `maybe_unused`) on
`__body`'s header at EVERY layer (the OFF and ON lines must stay identical), stated in §5. Not answer-affecting.

### SOUND-4 (CONFIRMED; severity design (scope, not answer); effort trivial; blast radius E-find sites whose FIND row is D1w)
§3.3/§15.2 key T-vscan on `pick WALK` because "every scan cell it timed was a WALK" (`scan-scope`, manager 2026-11-21:
"nothing else was measured"). But `FF_WALK` is the pick of TWO finder rows (memfn/src/finder.c:279-283 D1w and :309 R7w).
710's four scan classes were set walks (R7w); D1w is the one-member walk (a literal stop) and was not timed. Repro:
`site.py --head 0 -- '[0-9]{26}xyz' --memfn=no-fd-d1` -> wfE E-find, fd D1w, stretch lo=0 k=26 (the walk probes `z` at +28,
the stretch sits beside a C-run `memcmp(... "xy", 2)`), so T-vscan as written routes it to V. Answers held (SOUND (b) run
`d1wlit`: 176 subjects, gcc/-march=native/clang, OFF wrapped and ON V, 0 differences), so only the D77 claim is unsupported.
Fix: key T-vscan on the finder ROW (R7w) rather than the pick, or say D1w is admitted on purpose. VM-engine D1w sites are
E-stmt in my probes (`x[0-9]{30}` --engine=vm), so unrouted.

### SOUND-5 (SUSPECTED; severity doc (the U2b census's input); effort trivial; blast radius U2b (a)'s site list)
§2/§16 item 6b: "At width 4095 ... `[+.0-9]{65}` differs by 440 lines and `\w{501}` by 1 line"; default width "`\w{20}` and
`\w{32}` DIFFER (97 lines)". §5's literal shape (two-argument always_inline `__body(s, c)` + always_inline selector at file
scope ahead of `rxa_search`, today's H64 chain moved verbatim) applied by hand to the shipped build/pcrec artifacts, gcc 15.2
-O2, kit/objfn.sh: `[+.0-9]{65}` w4095: 0 lines differ (OFF and x86-64-v3); `\w{501}` 2; `\w{20}` 24 (both widths);
`\w{32}` 26; 0 on the other 15 sites. The sign agrees (the `\w` sites move, machine code only), the counts do not, and
`[+.0-9]{65}` flips from DIFFERS to IDENTICAL. I cannot see the probe (denied), so the cause is open: a different wrapper text,
diff counting, or the `span-head` lever. What would confirm it: U2b (a) states the EXACT wrapper text and command it
censuses (the §5 text, at default head) and re-derives these counts. If U2b inherits §16's list, it times a site that
does not move and could put a non-loser on T-keep. Answers identical on all of these (PROBED below).

## PROBED-AND-HELD

Reach: k = 16..1000 in the unit test (K in {16,17,24,31,32,33,48,63,64,65,100,500,999,1000}); real sites k = 16..1000
(16, 19, 20, 24, 25, 26, 30, 31, 39, 64, 99, 500, 1000); subjects 0..~6 KB (hex1001: 3092 subjects). Budgets: about 145 pcrec
compiles (cap 400). About 338 gcc/clang compiles of my own C, OVER the 300 cap by about 38: each real-site case cost 12
compiles (8 answer builds + 4 objdump) and I counted too late. No timing was run.

(a) §4.1 hand-executed from the note's text (sound/a/gen_unit.py; prototypes built from §4.1, compared with spike708 only afterwards):
- 16 classes written in the test (`[0-9]` `[0-9a-f]` `\w` `[^\n]` `[\x80-\xff]` `[\x00-\x7f]` `[\x7f-\x81]` `[^\x00]` `[^\xff]`
  `(?!)` (empty) `[^A]` `[A-Z]` `[+.0-9]`, a 6-byte odd set, an 8-range set and its complement) x 14 K x LO in {0, 1, -24}.
- About 10k windows per class: a failing byte at EVERY index, every non-member byte at the last index, and random windows.
  Each window was placed flush against PROT_NONE at its top AND at its bottom.
- Result with the set_epi8-order tables: 0 differences against python `re` per-byte membership. gcc 15.2 and clang,
  -O2 -march=x86-64-v3.
- Controls: a final block 1 B past (K=33) SEGVs; a first block 1 B below SEGVs. So the guard pages reach.
- Held:
  - B's choice ("32 where k >= 32, else 16" = §4.2's "largest of 32, 16 <= K").
  - `i + B < K` plus the overlapped final block `K - B`: no read outside [p, p+K) at any K tested.
  - The bit table `-128..1 x4` is correct in set_epi8 order.
  - The empty set, 255-member sets and sets with bytes >= 0x80 all held.
  - The 16-B SSSE3 rung inside the v3 region (gcc pragma and clang `attribute push` alike).
  - A negative LO in `rxa_mf1_s + rxa_mf1_c - 24`.
- Afterwards against spike708: `nibble_tables` is the same formula; `nib_blk` reverses its tables (as SOUND-1's fix
  does); `span_body` "loop" is the same loop with tail `k - B`. The only differences are the dropped `target()`
  attributes and the base computed in `__w32`.
- K = k, never k+1. The probe/stop is excluded, and LO is the stretch's first offset. site.py --head 0 shows:
  - HORS `[0-9a-f]{17}` lo0 k16, `\w{20}` lo0 k19, `[^\n]{40}`@4095 lo0 k39, `[0-9a-f]{1001}` lo0 k1000;
  - WALK `[0-9]{25}` lo1 k24 (stop at 0), `[0-9a-f]{30}\d` lo0 k30 (stop AFTER the stretch, at 30),
    `[A-Z]{3}[0-9]{25}` (first stretch k2 is ineligible, second lo3 k25 is the first eligible), `[0-9]{65}`@4095 lo1 k64;
  - boundary flips at k 15/16 and 23/24 (`[0-9a-f]{16}` k15, `[0-9]{24}` k23) match §11.
- The hoisted bound (`if (!(c + chi < n)) break;`, chi = the probe/stop) precedes the test on every HORS/WALK site
  examined, and every stretch offset is <= chi.
- No negative-offset stretch reached an E-find HORS/WALK site in 7 lookbehind/`\K` probes (those sites are VM D1/R7w with
  no loop). The unit test covers a negative LO anyway.
- Window table offers carry a distinct ref per offset (src/gen/emit_dfa.c:6956-7002, WIN_OFFER_OFS + k), so
  wf_loop_len's same-offer rule keeps an offered stretch at length 1 or less. No V stretch reads a pcrec table. Reasoned
  from the code, not compiled.

(b) The §5 wrapper applied by hand to shipped build/pcrec artifacts (sound/b/wrap.py, case.sh). There were 20 real sites:
- HORS and WALK, default width and 4095: `[0-9]{25}` x2, `[0-9a-f]{17}` x2, `\w{20}` x2, `\w{32}`, `[^\n]{17}`,
  `[^\n]{40}`@4095, `[0-9a-f]{20}[g-z]`, `\b[0-9a-f]{20}\b` (non-core guards beside), `[0-9a-f]{30}\d`, `[A-Z]{3}[0-9]{25}`,
  `[0-9]{25}[a-z]{2}`, `[0-9]{65}`, `[+.0-9]{65}`, `[0-9a-f]{100}` (H64 lone tests + loop), `\w{501}`, `[0-9a-f]{1001}`;
- `[0-9]{26}xyz` --memfn=no-fd-d1 (beside a C-run memcmp, D1w);
- plus 2 hex-17-shaped extras compiled from backslash-stripped spellings (`[^n]{17}`, `[0-9a-f]{30}d`), counted
  separately.

The chain references ONLY `rxa_mf1_s`, `rxa_mf1_c`, and `rxa_mf1_j` (the latter declared inside its own statement
expression). It references no frame local (`_n`, `_lo`, `_f`, `_b`, FL) and no file-scope table. Every chain was one
contiguous run of top-level conjuncts covering exactly [LO, LO+K). Types are identical (const unsigned char *, size_t),
so no conversion occurs.

Answers on every site: OFF base, OFF wrapped and ON V (§4.1 + §5), each built with gcc -O2, gcc -O2 -march=native and
clang -O2. The x86-64 (w16) wrapper was checked on 3 sites with gcc and clang. Find-all ran over 140..3092 subjects per
site (exact instances, one short, a near-miss staircase at every index at the start / after a match / overlapping,
random, and 0..255 noise), each flush against PROT_NONE at both ends. Result: 0 differences from python `re`, 0
crashes.

No answer-relevant difference is possible from the wrapper. The function is a pure conjunction over in-bound reads with
the same parameter types and the same && short-circuit position in the test. gcc -Werror is clean on all of them.
Machine code (rxa_search) is IDENTICAL on 16 of 20 sites; the `\w` sites differ (layout and compare order), see SOUND-5.

CRITIC COMPLETE
