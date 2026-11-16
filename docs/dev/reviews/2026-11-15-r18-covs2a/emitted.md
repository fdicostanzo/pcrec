# emitted findings

## Findings

### EMITTED-1 (CONFIRMED, maintenance, low; effort minutes; blast radius none at run time)
`PcrecCover` now carries two pointers to the SAME storage, `cv->sets` (the record, set in C7 `cc_width`, src/gen/known.c:324) and `cv->end.set` (set in C8 `cc_exact`, known.c:360), and two lengths for one fact (`cv->exact_len`/`cv->k` and `cv->end.k`). Nothing checks `end.set == cv->sets` (or `end.k == exact_len`) where `end.k > 0`. Today every writer is the one line in cc_exact (plus S1131's plant, which writes the same pair), so it holds by construction; the hazard is a later writer (stage-2 part B, or a re-walk) moving one and not the other. Options: drop `MkEnd.set` and pass `cv->sets` beside `const MkEnd *` to the three readers (`cover_window` known.c:609, `pcrec_cover_proof_diff` known.c:659, `req_run_in_cover` emit_dfa.c:16286), or keep it and say in known.h:27 that it is an alias set only by C8. Not a correctness defect.

### EMITTED-2 (CONFIRMED, doc, trivial)
src/gen/known.h:63 (PcrecCover record comment) still says "`MkEnd` is filled from it (C8)"; after A1 MkEnd POINTS at it (known.h:27 and known.c:353 say so). One-word fix ("points at").


## PROBED-AND-HELD

Matrix: 72 patterns x 2 option sets (default, -e utf8) x 2 trees = 288 compiles (cap 600), plus <=40 for listings/plants/matchers on any DIFF. Emitted C only (pcrec direct, gcc only on a DIFF).


### Held (sub-part a, emitted C BASE vs SUBJECT, default options)
- Batch 1: 72 patterns x {byte, -e utf8} x 2 trees = 288 compiles: 144/144 IDENTICAL after normalising the one `#include "<basename>.h"` line (my files had different basenames per side; nothing else differed); 144/144 same rc. Routes reached (subject stamp): cover 94, unanchored 43, rev-end 4, attempt 2, landmark-walk 1. Covers at k = 1..32 ([0-9a-f]{31}/{32}, a{32}, x[0-9]{30}y = 32, (?:ab){16}, a{10}b{10}c{12}, x(?:yz){15}w = 32) all `cover` on both; k = 33+ ([0-9a-f]{33}/{40}, a{33}/{64}, x[0-9]{31}y, .{33}, (?:ab){17}, a{10}b{10}c{13}) all `unanchored` on both; before/after context (\b, (?<![a-z]), (?![0-9]), (?=x), \b[0-9a-f]{32}\b vs {33}); branch stops (abc|abd cover; cat|cow, a(b|c)d, (?:abc|abd)e{30} unanchored); req-run inside a cover (abcd[0-9]abcd, abcdabcd, xabcdefghy, GET /[a-z]{5} HTTP, the ISO timestamp); caseless (?i); multi-byte classes and literals ([\x80-\xff]{4}, \xc3\xa9t\xc3\xa9, é{3}, [éa]b) in both encodings.
- Batch 2: 20 patterns x {-i, -i -e utf8} x 2 trees = 80 compiles: 40/40 identical (incl. lookaround/backref/VM-hybrid shapes and an rc=1 refusal, same on both).
- Batch 3: 8 alternations meant to produce compound parts x 2 enc x 2 trees = 32 compiles: 16/16 identical, but RX_COMPOUND "none" on all 8; a subject-only probe (8 compiles) showed the only compound kind is `split` with parts `attempt` + `rev-end`, so NO compound part reaches the cover route today: the "compound part compiles with its parent's value" path is unreachable by an emitted-C probe at the default (not a defect; noted so nobody counts it as covered).
- No emitted DIFF anywhere, so no matcher/oracle run was needed (identical C => identical answers).
- S1131 plant (pointer fill): `reach.sh <plant> - 'ac|bd' --facts --why` -> REACH-FACTS-DIFFER, why end-at-k (SUBJECT: exact/machine-inexact): the re-written plant still reaches and still moves the witness. 2-3 compiles.
- Compile total: 288 + 80 + 32 + 8 + ~4 = ~412 (cap 600), all finished by 23:50 box clock.

### Held (sub-part b, the equivalence argument)
- Same content: the old copy was `memcpy(end.set, st->w.set, k*32)`; the new pointer is `cv->sets`, which C7 (`cc_width`, known.c:324) assigns `= st->w.set` before C15 and C8 run (table order C7, C15, C8). Same base pointer, read over the same `d < k`.
- Filled before read / non-NULL: `w.set` comes from `kn_set_at` (known.c:144), an arena allocation of >= 32 slots made at depth 0 of every walk that reaches a byte step; `end.set` is only written in C8 together with `end.k`, and only on a non-BRANCH stop. Before C8 (or when C8 declines) `end.k == 0` and `end.set == NULL` (zeroing arena); every reader loops `d < e->k` / `o + len <= e->k`, so a NULL is never dereferenced. `cover_window` additionally fails loud on `k < 1`; `req_run_in_cover` returns -1 at k = 0 (whole_len >= 2 checked by its caller, emit_dfa.c:16296).
- Lifetime: `kn_set_at` doubles by fresh arena allocation and copies; the array `cv->sets` captures is the FINAL one (captured after `kn_walk` returns, no later walk on this CoverSt). The arena is the Ctx's, freed wholesale only at `pcrec_arena_free` (no rewind/mark API exists: grep arena_reset/rewind/mark = 0), and `cv` itself is in the same arena, so the pointer outlives exactly what the old inline copy did. A memo miss (`cover_key_holds` false) allocates a new `cv` and a fresh `CoverSt`/walk; the old record's sets are not reused or overwritten.
- No by-value copy: grep for `PcrecCover x;`/`MkEnd x;`/`= *...cover`/`->end =` finds none; readers take `const MkEnd *` / `const PcrecCover *`.
- The deleted internal error was unreachable: it fired at `k > MF_MAX_SPAN_POS`; C15 already required `k <= MF_WSPAN_POS`, and `MF_WSPAN_POS == MF_MAX_SPAN_POS == MF_MAX_TERM == 32` (memfn/include/memfn.h:277, 302, 653), and BRANCH stops return before it in both trees. So removing it changes no route; it is a pure simplification.
- Route identity of the new C15 clause at default: `cover_width_limit` = 32 (PCREC_DEFAULT_WINDOW_SEARCH_WIDTH) = MF_WSPAN_POS, and `k < MF_MAX_FWD (33)` already bounds k <= 32, so `k <= 32` adds no decline at the default; the only movement is the why's NAME (statement-fits -> width-limit), visible in the facts listing, not in emitted C (confirmed by the sweep). This identity is coincidental to the kit's MF_MAX_TERM being 32: if the kit raises it before part B, the two diverge and default routes move (expected by design, §11).
- `uint16_t k`: every printf reader (`%d` in KITPROOF and in emit_dfa.c:14510 `scan_position + %d`, `%u` casts in cover_window) promotes cleanly; the cast `(uint16_t)k` is exact for k <= 4095 (the anchored ceiling bounds the walk).

### Sibling of a family
The arena-pointer records here are: `KnWalk.set` (the OWNER, grown in the arena), `PcrecCover.sets` (the record, `const uint8_t (*)[32]` + `uint16_t exact_len`), and now `MkEnd.set` (same type + `uint16_t k`). So yes, it is the third member, and it ALREADY shares the family's form exactly (const pointer-to-[32] rows, a uint16 count, arena lifetime, no owned copy) — the same shape `pcrec_facts_hull_check(cx, const uint8_t (*sets)[32], int n)` and the VM's `seq` readers take. The one non-family trait is that it is not an independent producer but an alias of member two inside the same struct (EMITTED-1); the unified form would be a single `{ const uint8_t (*set)[32]; uint16_t n; }` span type both fields use, or MkEnd dropping its pointer. Worth a note on [COVER-CAP], not a fix in this branch.
