# R-9 D6 panel — critic: CORRECTNESS AND OVER-READ

Subject: `worktrees/r9d/docs/design/memfn/integration.md` rev 4.9 (§R4.9 and
the `[rev4.9]` marks) and `worktrees/r9d/docs/dev/lanes/r9d_report.md`.
Read-only. Context read: memfn/src/{precheck,ofsskip}.c, memfn/include/memfn.h,
src/gen/memfn_stamps.c, docs/spec/match_api.md (stamps), D147 addendum 11,
R-1's probe `docs/design/memfn/probes/twins/tb_r4b.c` (`f_ffl`, `f_swar`).
Scratch probes (gcc 15.2, this box) are in `probe/` beside this file.

Totals: BLOCKER 0, MAJOR 5, MINOR 7.

---

## C-1 (MAJOR) — `T` has two definitions; one of them under-sizes the reach and over-reads past `n`

**Where:** §R4.9.3 "The short-span path": "`VW + T`, where T is the run
term's extent beyond the scanned byte". Contrast F-R9-1 ("T = run length − 1")
and the §R4.9.5 item 10 D149 table ("T | run length − 1").

**Failure.** "Extent beyond the scanned byte" reads as `L − 1 − KA`. On
union-select (`SELECT`, L = 6, KA = 4, KB = 5) that gives T = 1 and a w16
reach of 17 instead of 21. The body's real need is set by its highest read:
the KB load at block base `i` reads `[i+KB, i+KB+VW)`, and the in-block
verify of lane VW−1 reads up to `i+VW−1+L−1`. Both need `n − i ≥ VW + L − 1`.
With reach 17, a span of 17..20 enters the helper and the first block reads
up to 4 bytes at or past `n`, the READ LIMIT (memfn.h: "no byte at or past it
is read"). The overlapped final block `f = n − T − VW` is also placed wrong,
and the lane mask `lane_from(i − f)` is sized wrong, so candidates are dropped.

**Fix.** Define T once as `L − 1` (or as the maximum over all byte reads
relative to the block base, minus VW + 1). State reach = VW + L − 1 and derive
it from the highest read. Delete "extent beyond the scanned byte". Add a G2
plant "reach one short", red against the end guard page.

## C-2 (MAJOR) — the SIMD row's APPLIES is wider than the floor shape it decorates

**Where:** §R4.9.2, the batch-1 table rows 1-2 ("any mask") and "The ladder"
("It stops at the first passing SCALAR row … the generic row guarantees one
exists"). The FUNC-part shape is the only one batch 1 specifies.

**Failure.** The dispatch prefix needs a scalar FUNCTION to go into. At a PRE
site that function exists only when the floor is `precheck`/`precheck_assign`
and the window is a `run_part`. That requires `fn_ref`, `plan_hint == 0`, and
`ofs_fn_applies` (precheck.c `run_part`; ofsskip.c: the scanned position is
exact or a two-member cube whose run byte is the lower member). "Any mask"
also admits a scanned position with a 4-member cube, where `ofs_fn_applies`
declines. The floor is then `generic`, which has no FUNC part. The design
gives no rendering for that case. It ends either in `kit_fail` (a
SIMD-on-only REFUSAL, which would also turn C-SEL red) or in a shape outside
C18's model.

Second hole: the collect step takes "each later SIMD row … whose level is the
chosen level's `implies` chain". That does not require the SAME FORM. In a
later batch, a `vfoo-w16` row would join a `vrun-w32` ladder, and the stamp
`vrun@w32+w16` would name it wrongly.

**Fix.** Compute the floor row first, then gate:
- a SIMD row declares the floor ids it can decorate (an `over` column), and
  its APPLIES includes that floor's predicate;
- the ladder collects only rows of the same form stem.

## C-3 (MAJOR) — C-SEL goes red on its own named witness family, and its exemption would blind it

**Where:** §R4.9.8, the C-SEL row ("every stamp except `MEMFN_FORMS` … the
near-cap size witnesses"); F-R9-5; RQ-3.

**Failure.**
- Some stamps quote MEASURED SIZES:
  - `<PREFIX>_VM_PREFILTER_WHY "size cap retry, hybrid 1026588 > 1000000"`
    (match_api.md §6.3 example, `§6.3.5¶3`);
  - the K-ladder's "`%zu nodes %zu/%zu bytes, the ladder measured`"
    (compile.c:2724).
- memfn_stamps.c: "The pass runs on every attempt, before the size
  measurement". So those sizes include the SIMD text, and they differ ON vs
  OFF on exactly the near-cap witnesses C-SEL names.
- `RUN_WORDS` is an activity count of run compares written. It moves if the
  helper's in-block verify renders through `runcmp`, and the design does not
  say whether it does (see C-12).
- C-SEL as written is therefore red by construction. The obvious repair,
  exempting those stamps, removes detection exactly where F-R9-5 lives.
- Beyond that, C-SEL is a census over corpus + bench + witnesses. It cannot
  show that no user pattern sits within the SIMD delta of the 4,096-byte
  knee or the 500k/1M caps.

**Fix.**
1. Compare stamps as KEYS, with byte and node counts normalised (the rule it
   already applies to refusals). Declare `RUN_WORDS`'s and `MEMFN_LIBC`'s
   behaviour under ON.
2. Make neutrality hold by construction now, not after a census: the kit
   knows exactly how many guarded bytes it wrote, so the SELECTION readers
   (`pcrec_sb_len_uncut`'s knee, `fit_rungs[]`) read length minus guarded
   bytes.
3. Rule SEPARATELY whether D84's code-bytes REFUSAL cap counts guarded
   bytes. Its purpose is the compile budget, and at `-march=L` the guarded
   text IS compiled. RQ-3's "size-neutral to every length decision" conflicts
   with that purpose.
4. Note that C18 already detects a moved selection on every MOVER, since a
   moved rung changes the unguarded text.

## C-4 (MAJOR) — the run-time cascade's negated guard escapes C18 and runs AVX2 in no-vector builds

**Where:** §R4.9.3 "The run-time cascade (K-6)": guard
`defined(__x86_64__) && defined(__linux__) && defined(__GNUC__) && !defined(__AVX2__)`;
"It sits above the w16 rung, so the floor rule holds"; Q-R9-8.

**Failure (measured, probe/).**
- Under `gcc -E -P -mgeneral-regs-only` that guard is TRUE: `CASCADE_TEXT`
  survives. C18 is therefore red on every cascade mover, and the
  floor-rule claim for the cascade cannot be checked.
- The same guard admits TUs built with `-mgeneral-regs-only`, `-mno-sse`,
  `-mno-sse2` or `-mno-avx`. The probe compiles cleanly under all four.
  Such an artifact runs a `target("avx2")` helper on any AVX2 CPU, which
  clobbers ymm state in exactly the kernel/freestanding builds the floor
  rule promises run the floor.
- `__cpu_model` is also an undefined symbol in a build without libgcc.
- The applies test ("the compile-time ladder's top level being ABSENT and
  the cascade's level being available to the toolchain") is not a fact the
  kit has at render time. pcrec and the kit are arch-blind.
- At `-march=x86-64-v3` the cascade is compiled out, and the compile-time
  w32 row is not collected (w32 is not in w32's own `implies` chain). So v3
  runs w16 only, and the stamp `vrun-rt@w32+w16` misreports.

**Fix.**
- Add `defined(__SSE2__)` to the cascade guard. Then `-mgeneral-regs-only` /
  `-mno-sse` builds drop it, C18 holds, and kernel builds get the floor.
- State the libgcc link dependency in Q-R9-8.
- Restate applies as a kit-table fact (row order), and render the cascade
  ABOVE the full compile-time ladder (cascade, w32, w16, floor) so v3 keeps
  w32.

## C-5 (MAJOR) — neither the answer sweep nor G2 as planned is able to catch most wrong vector arms

**Where:** §R4.9.6 item 4 (answer sweep "with a planted wrong arm red at its
own level"); §R4.9.7 G2; §R4.9.8 rows "the answer sweep per level" and "G2
per level".

**Failure.**
- **(a) The sweep is blind to whole defect classes, by construction.** The
  FUNC's contract is the LEFTMOST position ≥ `pos`, or `n` (ofsskip.c header,
  litscan_k82h.md §1.1a). At ON_MISS the value is only compared with `n`, so
  a false positive or a LATE hit changes no answer. At ASSIGN the value is a
  lower bound (`lo = max(search_from, c − K)`), so a false positive (too
  early) changes no answer either. The sweep only sees "returned `n` with a
  run present", and at ASSIGN "returned later than a match's `c − K`".
- **(b) Its reach is one whole-arm plant per level.** Nothing shows that the
  2× loop, the 1× loop, the overlapped final block, the lane mask or an
  m1-only hit is ever executed. The vector body needs `n − lo` ≥ 18..39
  bytes, and corpus subjects are mostly shorter.
- **(c) G2's planned space is "lengths 0..158, alignments 0..31, a hit at
  every offset and none".** It omits:
  - MULTIPLE hits: leftmost among two or more in one block, across m0/m1,
    and in the final block's already-covered lanes;
  - NEAR-MISSES: pair filter passes at KA and KB, the run fails, the TRY
    loop continues. R-1's own `--check` used near-miss filler;
  - a `pos` sweep (restart at hit + 1, as R-1's check did).

  Nor does it state exact returned-position equality as the oracle relation.
- **(d) w16 has no x86 level where it is compiled out.** So the "green where
  compiled out" half of the [MECH-REACH] proof is unavailable for it.

**Fix.**
- G2 adds the multi-hit, near-miss and `pos` axes, with oracle = exact
  returned value.
- Plants per level:
  - final-block off-by-one (R-1's PLANT 1);
  - lane-mask off-by-one;
  - m0/m1 order swap;
  - pair filter accepting a near-miss without verify;
  - reach one short (C-1).
- The sweep gets per-path execution counters (a counting or gcov build) with
  floors, as its [MECH-REACH].
- Use `-mgeneral-regs-only` as the compiled-out level for w16.
- State that the answer sweep is a smoke check and G2 carries the contract.

## C-6 (MINOR) — C18 proves off-target equality only; guarded text can still change the on-target floor

**Where:** §R4.9.2 "What the rule buys" ("The short path, the `#else` and
the off-target build are all that one text"); §R4.9.8 C18.

**Failure (measured).** `#if defined(__SSE2__)` / `#define memchr my_memchr` /
`#endif` leaves the `-mgeneral-regs-only` output unchanged, while at a live
level the floor expands to `my_memchr`. C18 also has two other gaps:
- it accepts text under ANY guard that is false there (`#if 0`, non-level
  macros);
- it strips comments, so "byte for byte" is stronger than what it checks.

**Fix.**
- Add a second C18 leg at each live level L: `gcc -E -P -march=L` of OFF vs
  ON must be an INSERTION-ONLY diff.
- Add a lint that every `#if` in the ON−OFF text diff is a `levels.def`
  guard string.
- Restate the rule as "preprocessed-equal".

## C-7 (MINOR) — where the intrinsic `#include` goes is unspecified, and the obvious path breaks C18 or C4

**Where:** §R4.9.2's FUNC-part sketch; the kit's `MF_INC_*` bits / `mf_includes`.

**Failure (measured).** Without a guard, `<emmintrin.h>` adds 3,291 lines
and `<immintrin.h>` adds 45,912 lines to the `-mgeneral-regs-only` output.
Routed through `MF_INC_*`, which pcrec writes unguarded at the top, it turns
C18 red on every mover. pcrec writing the guard itself breaks C4.

**Fix.** State that the kit writes the include inside the level guard at
file scope, just before the helper. No new `MF_INC_` bit.

## C-8 (MINOR) — the guards omit the architecture, and C9-x86's march set misses a guard that is too weak

**Where:** `levels.def` sketch (guard `defined(__SSE2__)`, family column
`x86_64` not in the guard); §R4.9.8 C9-x86 (x86-64, v3, v4).

**Failure.**
- On i686 with `-msse2`, and on x32, w16 is live, but nothing compiles,
  runs or sweeps it there.
- A guard that is too weak (`__AVX__` over an AVX2 body) passes all three
  C9 levels but fails to compile at `-march=sandybridge`. The probe: AVX2
  ops error with 3 errors at x86-64; AVX-only ops compile at v2+`-mavx`.

**Fix.**
- Guard `defined(__x86_64__) && …`, or add `-m32 -msse2` to C9/G2.
- Add x86-64-v2 and sandybridge (AVX without AVX2) to C9-x86, or derive
  "each level minus each implied feature".

## C-9 (MINOR) — the stamp names RENDERED levels, not live ones; the `.h` must stay guard-free

**Where:** §R4.9.2 "The stamp"; §R4.3.3 `[rev4.9]`.

**Failure.** At the bench recipe (`-O2`, no `-march`), `vrun@w32+w16` names
a w32 arm that is compiled out. A level guard in the `.h` would be
evaluated under the CONSUMER TU's flags, not the `.c`'s.

**Fix.** The match_api.md §6.3 hunk says levels are rendered, not live. The
design states that no level guard appears in the `.h`.

## C-10 (MINOR) — "no aligned-down load, checked by ASan" holds only if the bytes below `s` are poisoned

**Where:** §R4.9.7 G2 ("the rule is checked by ASan").

**Failure.** G2's alignments 0..31 come from offsets inside a larger buffer.
`[buf, s)` is addressable, so an aligned-down load is invisible to ASan
(malloc is 16-aligned). The corpus sweep's ASan cannot see reads past `n`
either: driver subjects sit in larger buffers with a NUL at `s[n]`. Only G2's
end guard page can.

**Fix.** G2 poisons `[buf, s)` and `[s+n, end)` (`ASAN_POISON_MEMORY_REGION`)
per case. State that the sweep's ASan does not cover past-`n` reads.

## C-11 (MINOR) — the bin key cannot exclude the VM hybrid route that §R4.9.7 says is excluded

**Where:** §R4.9.6 item 3 (bins = handoff, masked/exact, run length);
§R4.9.7 "Not in the evidence … VM hybrid route's window … excluded unless the
alpha reaches them".

**Failure.** The route is not a bin dimension. A VM-hybrid ON_MISS masked
L = 6 site lands in union-select's bin and is admitted on its timing.

**Fix.** Add `consumer` (`mf_consumer`) to the bin key and to APPLIES, or
drop the claim.

## C-12 (MINOR) — the in-block verify's spelling is unspecified

**Where:** §R4.9.7 ("The form is R-1's `ffl` … an in-block verify").

**Failure.**
- R-1's `run_eq` is its own masked compare, valid for L ≤ 8 only.
- If the kit re-spells it, that is a parallel run compare. The floor's
  `denies` class `RUN_OVERLAP` (bit 43, which precheck/ofsskip serve) then
  does not reach the vector text, and the row's `serves` must say so.
- If the kit renders it through `runcmp` / `rc_row`, `RUN_WORDS` moves
  (C-3), and the run-length cap comes from `rc_row`, not "at most 8".

**Fix.** Choose `runcmp` (one run compare). Declare its effect on
`RUN_WORDS`, and declare the SIMD row's `denies` serves.

---

## Checked and found sound

- **C18's macro premise.** `-mgeneral-regs-only` leaves only `__x86_64__` of
  the x86 ISA macros. Even with `-march=x86-64-v3` added it clears
  `__SSE2__`/`__AVX2__` (0 matches), so inherited GENCFLAGS cannot defeat C18.
- **C18 cannot fail spuriously on whitespace or line numbers.**
  - `gcc -E -P` collapses the blank lines a removed block leaves: a
    40-line guarded block in a function body preprocesses identical to the
    OFF text.
  - Emitted C uses no `__LINE__`/`__COUNTER__`, so the shifted lines do not
    leak into `-E`.
  - `#define` stamp lines vanish, and `MEMFN_FORMS` is not referenced by
    code.
- **C18's independence for its stated claim.** The preprocessor decides what
  survives. That OFF also comes from the kit is correct for a RELATION check;
  the scalar text's correctness is I2/C5's.
- **C9-x86's plant.** An AVX2 body under the w16 guard fails at
  `-march=x86-64`, at -O2 and at -O0 (target-mismatch errors).
- **The read argument when T = L − 1.**
  - R-1's `f_ffl`/`f_swar`: every load is in `[pos, n)`; the final
    overlapped block has `f ≥ pos`, and its lanes below `i` are masked.
  - Blocks ascend, lanes go lowest first, m0 before m1, so the returned
    value is the LEFTMOST hit, as the ASSIGN handoff contract requires.
  - No page or alignment assumption is needed.
- **The dispatch.** `pos < n && n − pos ≥ reach` is underflow-safe, and
  `lo > n` stays EMPTY (scalar loop guard and prefix agree).
- **Static decline.** `MF_SPAN_UNBOUNDED = UINT64_MAX` passes walk test 6,
  so an unbounded site is not falsely declined.
- **Deny arithmetic.**
  - `no-vrun-w32` makes w16 the top.
  - `no-vrun-w16` alone gives w32 → floor.
  - Both denied renders the floor alone, so DENY == OFF and `MEMFN_FORMS`
    is `"none"` by its own definition (§R4.3.3).
- **Policy plumbing.** Walk tests 1-2 read only the policy word, and I2's
  plant (a SIMD row under `MF_P_PORTABLE_ONLY`) is the right failing
  direction.
- **Two multi-`-march` cases.**
  - A consumer `#pragma GCC target("avx2")` ahead of the artifact defines
    `__AVX2__` (probe), so the guard and codegen stay consistent.
  - One artifact compiled into two TUs at different `-march` keeps static
    helpers TU-local; its exported entries clash, as they always did.
- **The cascade's failure direction.** A zero `__cpu_model` (a call before
  libgcc's constructor) answers 0 and falls to w16/floor, which is safe.
  libgcc gates AVX2 on OS YMM support (BELIEVED, from libgcc's
  `avx_usable`; not re-read here). The cascade compiles under every
  restricted flag tried; the defect is at run time (C-4).
- **G2's comparator.** The scalar byte loop shares no code with the kit, and
  its length bound 158 covers two w32 2× iterations plus the 1× loop and the
  tail at T = 7.
- **F-R9-1's mechanism.** `f_ffl` returns `f_swar` when `n − pos < VW + T`,
  and at pc16 every cell satisfies that at both widths.
