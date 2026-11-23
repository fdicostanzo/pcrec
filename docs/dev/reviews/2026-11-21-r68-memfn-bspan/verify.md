# verify.md: round memfn-bspan (r67), verified INLINE by the coordinator (2026-11-21 01:05-01:10)
Every CONFIRMED finding that would change code or design was a quote/grep claim or a one-call repro, or was re-run below
(skill §6.2 allows inline verification in that case). Commands ran on the build tree (03ce1ee3b) / the round kit.

## V1 (SOUND-2, PREMISE-1, MEAS-11: C18 cannot parse the subject's selector) — HOLDS
`sed -n 120,126p tests/memfn/simd_floor_check.py`: `SELECTOR = ^static inline size_t (\w+)\([^)]*\)\n\{\n    return (\w+)__w(\d+)...`,
`HELPER = ^static inline size_t (\w+)__w(\d+)\(`. The subject's §4.1/§5 spelling `static inline __attribute__((always_inline)) int` matches neither.
C9-x86 leg (:366-381) reads `nm` of the -O0 object. Probe: a 3-function file (always_inline `f__body`, `f__w32`, caller `g`),
`gcc -O0 -c; nm` -> only `T g` (no `f__w32` symbol). HOLDS on both legs.

## V2 (SIM-1, MEAS-1, SIZE-1: the corpus's one routed site is LIBC) — HOLDS
`site.py --width 4095 -- '(?:ab|ba|aa|bb){24}c'` -> fd D1, loop lo=0 end=48 k=48, hors=0. finder.c D1 row: `FF_LIBC` ("fd-d1").

## V3 (SOUND-4, PREMISE-6: D1w is a second FF_WALK row) — HOLDS
finder.c D1w row: `FF_WALK`, FB_UNMEASURED_DEFAULT. `site.py -- 'x[0-9]{26}' --memfn=no-fd-d1` -> fd D1w, loop lo=1 end=27 k=26 (inside T-vscan's 24..64).

## V4 (SOUND-1: set_epi8 order) — HOLDS by reading
`_mm256_set_epi8(e31, ..., e0)`: the first argument is the highest lane. §4.1's `bit` table is written in that order
(`-128, ..., 1`: lane 0 = 1); `lo_t[l]` is defined by index, so writing it index-first reverses it. Critic's 16-set unit run stands.

## V5 (SOUND-3: clang errors on the unreferenced __body) — HOLDS
Same 3-function file: `clang -O2 -Wall -Wextra -Werror -c` -> "error: unused function 'f__body' [-Werror,-Wunused-function]", rc 1; gcc same flags rc 0.

## V6 (MEAS-2: plant (b) benign on HORS) — HOLDS by reading the emitted text
`[0-9a-f]{17}` (build/pcrec default): the walk tests `rxa_mf1_s[rxa_mf1_c + 16]` (the probe) after `if (!(rxa_mf1_c + 16 < rxa_mf1_n)) break;`
and before the chain over +0..+15; one byte past the stretch is the probe: in bounds and a member.

## V7 (MEAS-3: no B <= K for K < 16) — HOLDS by reading §4.2 ("the largest of 32, 16 that is <= K").

## V8 (MEAS-6: Hspk's one-level wrapper vs the shipped two-level shape) — HOLDS
Critic's files meas/f2/num64.H64rec.c and num64.Hspk2.c plus 710's work/src/num64.Hspk.c, `kit/objfn.sh ... -march=x86-64-v3`:
H64rec vs Hspk 47 diff lines; H64rec vs Hspk2 (two inline levels) 0.

## V9 (PREMISE-7: `skip` is a head-renderer output) — HOLDS
window.c `d_hors_head` `*skip = ih >= 0 && w->grp[ih] < 0 ? ih : -1;` and `find_head` `*skip = rc->w->stop_alone ? rc->w->stop_ix : -1;` (renderers).

## V10 (PREMISE-4: no class carries a level bit) — HOLDS
`git grep 'includes |= \|includes = ' 03ce1ee3b -- memfn/src`: window.c sets `w->includes = w->libc ? MF_INC_STRING_H : 0` (2468/2478/2585);
the only level bit is `ofsskip.c:712 art->includes |= kit_level(...)->includes` (the ART, at define).

## V11 (PREMISE-5: a reader the `grep -i abi` filter drops) — HOLDS
docs/spec/match_api.md [6¶17]: "It is `109` on every artifact pcrec emits today" (no "abi" token on that line).

## V12 (PREMISE-9: 710 measured the wrapper's walk change on 47 of 130) — HOLDS
R/710/decision.md: "the control on the 83 identical-walk patterns' readable cells, Hspk's rxa_search == H64@on's". 130 - 83 = 47.
(Read with V8: Hspk is a ONE-level wrapper, so 47/130 is an upper-bound signal for the shipped two-level shape, not its count.)

## V13 (PREMISE-10: formhash has six shapes, none a long one-class window stretch) — HOLDS
memfn/src/kit.h `mf_form_shape_id` ends `MF_FH_OFS }`; entry fields are kit facts (cls, shape, row, bytes, ...), not a pcrec pattern.

## V14 (SIM-4: utf8 moves HORS to WALK) — HOLDS
`site.py --width 4095 -- '[0-9a-f]{20}' -e utf8` -> fd R7w (WALK), k=19 (T-vscan needs 24: not V; byte encoding is D-hors k=19: V).

## V15 (MEAS-12: no `.H64` arm source) — HOLDS
work/src/: 130 each of avx2-loop, avx2-ool, Hspk, Hspk-ool, prof; no H64.

## V16 (SIZE-5: "Scalar wrap:" inside the verbatim quote) — HOLDS
block_span.md §2 and §15.1: "Scalar wrap: the function goes inline ..."; decisions.md D201 add. 2: "the function goes inline ...".

## V17 (SIZE-9: D201's provenance pointer) — HOLDS
`git grep -c 'build with simd layer' 29e893818 -- memfn/docs/responses.md` -> no hit (rc 1).

## Not re-run (held on the critic's repro; no code/design change rests on the number alone)
SIZE-2's 3-site wrapper census (agrees with MEAS-5's independent probe of `[0-9a-f]{32}`, `\d{32}`: 0 lines); SOUND-5's per-site
line counts (agree in sign with MEAS-6/MEAS-PROBED and SIZE-2; disagree with §16 item 6b; V8 explains one cause);
MEAS-5's rule drill (a property of the rule text: a uniform effect below the floor reads TIE by construction).
CONTRADICTIONS: none. SIZE-2 (drop T-keep: 0 instruction differences on the population) and MEAS-5 (the census population cannot
see the known differing shapes) agree on the facts and differ on the remedy: one item for the manager (R-5 below in the draft).

VERIFY COMPLETE
