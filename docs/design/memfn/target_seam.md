# The target seam: per-target code paths between pcrec and the kit

STATUS: PROPOSED rev 0 (lane xarchseam, 2026-11-07, off main aeede1d16). Design only: no build
go. Nothing under `src/`, `cli/`, `lib/` or `memfn/` changes with this note. Owner row:
`[XARCH-DEV]` (docs/dev/plan.md). The kit asked for "the format of single-arch code paths" so it
can shape its SIMD forms now; this note is that format.

## 0. Ruled inputs (quoted)

- **D188 addendum 1** (owner, 2026-11-06): "availability no longer comes from `#if` arms over the
  target's compiler macros. The kit's ALGORITHM choice depends on SIMD, so an `#if` fall-through
  would run a plan chosen for another target. A code path is a per-target VARIANT, planned and
  priced for its declared target. One artifact may hold several variants (generic plus SIMD) as
  target-attributed functions behind a once-per-process CPU dispatch. The artifact's target set is
  an explicit caller-given LIST, with a declared, stamped default when none is given, never
  assumed. The pricing half of D188 (cpu-has / build-compiled / cost; timed only when both hold)
  stands, read per variant's target. The build of this end state waits for [XARCH-DEV]'s go."
- `[XARCH-DEV]` RULED text: "A variant is a complete matcher planned and priced for one target.
  [...] one artifact holds 2-3 variants (generic + 1-2 SIMD) as target-attributed functions, a
  once-per-process CPU dispatch entry, and each variant's own entry."
- D157 / D146: pcrec sends the kit FACTS, never methods; the kit chooses forms.
- D155 addendum 5: the dispatch decision is NEVER an artifact static (`match_api.md` §5.3¶1,
  ¶5); a one-shot search may pay the feature check per call; the iterator keeps it in its
  caller-held state (D165).
- Frank 2026-11-06: design the seam in planning/emitting-split terms, do not split the kit now;
  new SIMD forms are written emitter-shaped. Manifesto principle 9: every seam is a document.

## 1. Goals

| # | goal | who benefits | measurable form |
|---|---|---|---|
| G1 | the kit can write new SIMD forms now without waiting for the dispatch build | kit | a new form's text compiles inside a target-attributed function with zero `#if` lines; grep count 0 |
| G2 | one target (the default) emits today's bytes | every caller | `emit_sweep.py` over the corpus: 0 moved artifacts at the default list (§6) |
| G3 | several variants coexist in one artifact | callers shipping to mixed CPUs | two variants of the same pattern link in one `.o` with no duplicate symbol |
| G4 | the seam survives a text round trip | future planner/emitter split | every field in §2 is a value (no pointer, callback or language assumption except the C text itself) |

Priority G2 > G1 > G4 > G3. Non-goals: the dispatch mechanism per platform (pcrec's, §5); pricing
(D188's half, unchanged); splitting the kit; a mixed-family artifact (§10 Q1).

## 2. What crosses the seam

The unit is ONE VARIANT = one `mf_art` (today's per-artifact kit state, `mf_art_begin`). pcrec
opens one art per target in the list; nothing in an art knows the others exist.

**pcrec -> kit (facts), per art:**

| field | owner | value | today |
|---|---|---|---|
| `target.features` | pcrec (from its target table) | the instruction-set facts the target guarantees, as a sorted token list (`sse2,ssse3,...,avx2,bmi2`); empty = generic (portable C) | implied by `MF_P_PORTABLE_ONLY` + the consumer's macros |
| `target.family` | pcrec | `x86-64`, `aarch64`, or `generic` | implied by `__x86_64__` |
| `target.tag` | pcrec | an opaque token for traces and refusals only; the kit never derives text from it | none |
| `prefix` | pcrec | the variant's name stem (§3) | `prefix` (D143 placeholder) |
| `ms` | pcrec | the measurement set for THIS target (D188 per variant) | `ms` |
| site facts, hooks, denies | pcrec | unchanged, identical in every variant | unchanged |

The kit maps features to the levels it may use by a column it owns (levels.def's `guard` becomes
`needs`: the features a level requires; a level is admitted iff `needs` is a subset of
`target.features`). The tag is a name, not a fact: the kit must not branch on it (D157). The
`MF_P_PORTABLE_ONLY` bit becomes redundant with an empty feature list (a simplification at the
build: one fact replaces the bit; `-fno-memfn-simd` stays as pcrec's deny and maps to the generic
target).

**kit -> pcrec (facts + text), per art:**

| field | owner | content |
|---|---|---|
| text | kit | C valid inside a function compiled for the art's target: no `#if`/`#elif`/`#ifdef` on CPU or ISA macros, no CPU checks, no `#include` |
| `headers` | kit | the compiler headers the text needs (`immintrin.h`), as a fact like today's `MF_INC_*` bits; pcrec writes them once at file scope |
| MEMFN_FORMS / RUN_WORDS / MEMFN_LIBC | kit | the art's stamp values, unchanged in format, now read per variant (§4) |
| bracket marks | kit | the target-dependent byte ranges (today's `simd_open`/`simd_close`), so pcrec's length decisions stay target-neutral (RQ-3, §10 Q3) |

Function attributes, names, the variant list, the dispatcher and the stamps' line names are
pcrec's. The kit writes `static inline` function heads exactly as today and never an attribute.

**Round-trip test (G4).** Every pcrec->kit field is a token list or a string; every kit->pcrec
field is text, a token list or a byte range. The one callback today, `simd_open`/`simd_close` on
the sink, is a bracket marker in serialized form (an offset pair in the returned text). So the
seam is a document in principle 9's sense, and the planning half (target -> admitted levels ->
form) can later sit on one side of it with the emitting half on the other: a new SIMD form is
written as (a) an admission predicate over `target.features` and site facts, and (b) a renderer
that takes the chosen form and writes target-agnostic text. That is "emitter-shaped" in practice.

## 3. Names: unique per variant without the kit knowing

Premise checked by grep (main aeede1d16): every name the kit declares at file scope is built from
a pcrec-given string:
- `<fn>__body`, `<fn>__<stamp>` from pcrec's `fn` (memfn/src/ofsskip.c:547-555, memfn/src/vany.c:146-158);
- `<prefix>_w<W>` word loads (memfn/src/runcmp.c:533-535) and `<prefix>_mf<handle><suffix>` window
  tables (memfn/src/window.c:2107-2112) from `art->prefix`;
- table names through pcrec's `table_name` hook (memfn/src/ofsskip.c:158-164).
The exceptions are block-scope (`rq_set`, memfn/src/precheck.c:318) or test-only
(`mf_tbl`, memfn/src/formhash.c:232).

So pcrec gives each variant a distinct stem and the kit changes nothing about naming. The default
variant keeps today's stem (`rx`), so its names and bytes do not move. A non-default variant's stem
is `<prefix>_<vtag>` (e.g. `rx_v3`), where `vtag` comes from pcrec's target table. pcrec's own
names follow the same stem, since a variant is the WHOLE matcher. With several variants, the
public entries (`rx_search`, ...) become pcrec's dispatchers, and each variant keeps its own entry
(`rx_v3_search`). Shared header types and `PCREC_*` macros are emitted once.

## 4. Today's CPU conditionals, and what each becomes

Premise counts (grep over memfn/, main aeede1d16): `#if __AVX2__` literally 1 (a quote in
memfn/docs/responses.md:3194); `__AVX2__` 3; `__SSE2__` 4; `__builtin_cpu_supports` 6;
`target(` 3; `__builtin_cpu_init` 2. None of the `__builtin_cpu_*` or `target(` hits is in
emitted text: they are in test drivers (run_g2_*.py) and responses.md prose. The emitted guards
all come from ONE place:

| site | today | becomes |
|---|---|---|
| memfn/src/levels.def:41-46 | the `guard` column: `defined(__x86_64__) && !defined(__ILP32__) && defined(__SSE2__)` / `...__AVX2__` | a `needs` column (feature tokens); `header` stays as the fact returned in `headers`; `test_march` stays |
| memfn/src/ofsskip.c:568-575 (`fn_level_block`) | `#if <guard>`, `#include <hdr>`, helper, `#endif` | the helper alone; the header goes to `headers` |
| memfn/src/ofsskip.c:590-611 (`fn_selector`) | `#if`/`#elif` per rung, `#else` call to `__body`, `#endif` | ONE call to the variant's top admitted rung (or to `__body` when none is admitted: today's SIMD-off bytes) |
| memfn/src/vany.c:157, :178 (`vany_level`) | `#if <guard>\n#include <hdr>` ... `#endif` | the helper alone |
| memfn/src/vany.c:184-198 (`vany_selector`) | the `#if` chain | one call, as `fn_selector` |
| memfn/src/vany.c:210-215 (`mf_kernel_find_any`'s `levels` mask) | the caller passes a level mask | the mask is derived from the target's features (the kernel's argument becomes the target fact) |

The rung chain itself survives inside a variant: a w32 helper whose range is too short still falls
to the w16 helper (memfn/src/ofsskip.c:686-687). That is a length test, not a CPU test, and both
rungs are valid code on an `x86-64-v3` target. pcrec's own `#if __has_attribute(noclone)` lines
are compiler-capability tests, not CPU tests, and are out of scope.

**MEMFN_FORMS per variant.** The token format stays `<form>@<rung>+<rung>` (memfn/src/ofsskip.c:617-622,
e.g. `vrun@w32+w16` today at `-fmemfn-simd`). Each variant has its own value, the forms ITS art
rendered. pcrec stamps the default variant as today (`RX_MEMFN_FORMS`) and every other variant under
its stem (`RX_V3_MEMFN_FORMS`). D188's fact (b), "the build compiled it", becomes true by
construction: a variant's helpers are compiled under its target attribute, so there is no
fall-through for a stamp to misreport. Fact (b) now reads "the variant is in the artifact's list".

## 5. pcrec's half (named, not designed)

- **Attributes.** One region per variant, `#pragma GCC push_options` / `#pragma GCC
  target("arch=<t>")` ... `pop_options`, or the same attribute on every function head. The pragma
  form needs NO kit change, because the kit's heads stay as they are. Probe (scratch, gcc 15.2
  -O2 -Wall -Wextra, default `-march`): an AVX2 helper with no `#if`, `immintrin.h` included at
  file top, inside a `target("arch=x86-64-v3")` pragma region, compiled clean. It inlined into
  its variant entry (no out-of-line helper symbol, 3 `ymm` instructions), and a
  `__builtin_cpu_supports("x86-64-v3")` dispatcher returned the right answers.
- **Dispatch.** At the public entry only, never per site. Inside a variant every site runs at the
  variant's target. So D155's FREQUENT/INFREQUENT site classes and the per-site `freq` column of
  `[MEMFN-RTDISPATCH]` are no longer needed, and that is a deletion to count as a benefit. "Once
  per process" is the CPU probe, which libgcc runs once (its `__cpu_model`). The artifact holds
  no state: a one-shot call reads the probe (0.4-0.6 ns, linux_results.md), and the iterator
  keeps the choice in its caller-held state (D155 add. 5, D165). Per platform (ELF ifunc,
  Darwin, where `__builtin_cpu_supports` answers 0 for every feature): isa_evaluation.md's
  table. That is pcrec's choice and does not touch this seam.
- **The list.** It is caller-given; the default list is `generic` alone, declared and stamped
  (§6). pcrec owns the target table (tag, family, features, attribute string, probe string).

## 6. One target = today's bytes (G2), and how to check it

With the default list `{generic}`: there is one art, the stem is the prefix, the features are
empty, so no level is admitted. The kit text is today's SIMD-off text: `fn_selector` with no rung
is already the one plain call (memfn/src/ofsskip.c:596-611, `nr == 0`). There is no pragma, no
dispatcher and no extra stamp. **Check:** `scripts/emit_sweep.py --ref <main before the build>`
over all streams at the default flags. Expect 0 moved artifacts. A second run with `--extra
-fno-memfn-simd` should also show 0 moved, since it maps to the same generic target.

**The one conflict, resolved rather than a stop:** "a declared, STAMPED default" adds a line
(`<PREFIX>_TARGETS "generic"`) to every artifact, so the default bytes cannot be exactly today's
bytes. The resolution: land that stamp ALONE as its own abi event (D76/D94: bump, readers found by
grep, identity re-pin, spec hunk in `docs/spec/`) before any variant work. From then on, G2's
claim is "one target = the bytes of the stamp commit", and the sweep checks it against that
commit. `-fmemfn-simd` artifacts DO move: their `#if` arms go away. This is an opt-in axis
that is OFF by default, and the move is a SIMD-on abi event of its own.

## 7. Tests: every variant on its own arch

- Each variant has its own entry (ruled), so the harness calls `rx_<vtag>_search` directly, and
  every `.rxt` case runs once per variant whose target the box's CPU has. The CPU check lives in
  the TEST driver, never in the artifact (the shape of today's G2 gate: memfn/tests/run_g2_simd.py:345-357,
  skipped arms reported by name with a count).
- The dispatcher gets one cell: its answer equals the answer of the variant it should pick on
  this CPU.
- A variant the box lacks is counted SKIPPED by name, and the skip count is a pin (K35: someone
  counts the population). The dev box (Zen 4) runs generic, v2, v3 and v4. The Mac runs aarch64.
  Zen 1 runs up to v3.
- Independent control: every variant is checked against the same oracle answers (libpcre2 10.46
  / the corpus expectations), never against another variant.

## 8. Cost, and the first measurement (D77: named, not built)

An artifact with N variants carries N complete matchers plus one dispatcher. Text scales about
xN; the const tables are duplicated unless identical ones are shared, and sharing is a later,
measured option. One data point (scratch, `(?i)cat`, gcc 15.2 -O2, `size` text/data): SIMD-off
2386/224; `-fmemfn-simd` at default 2618/224; at `-march=x86-64-v3` 2922/224. So {generic, v3} is
about 5.3 KB of text against 2.4 KB, about 2.2x, before dedupe. This is ONE pattern and
UNMEASURED in general.

**The first measurement that prices it:** over the corpus at `-fmemfn-simd`, compile each
artifact at -O2 at the default `-march` and at `-march=x86-64-v3`, then report per artifact:
(text+data of both) / (text+data of the SIMD-off build), as median, p95 and max; plus the count of
artifacts whose two objects are byte-identical in `.text`, because those carry a variant that buys
nothing. This is a stand-in priceable on today's tree, and it is the plan row's "count of
disagreeing picks" in size form. It is a heavy sweep (>50 compiles), so it goes through the box
queue. Trigger: [XARCH-DEV]'s go.

## 9. Standing questions

1. **Measurement regime.** Relevant only to §8: `.o` size, gcc 15.2, Linux dev box, -O2. A
   different compiler or -O3 changes the ratio but not the shape (xN). This note prices no
   speed, and D188's per-variant pricing is unchanged.
2. **Independent control.** Relevant. G2 is checked against a reference build of an earlier
   commit (emit_sweep's `--ref`), which shares no source with the change. Variant answers are
   checked against the oracle (§7).
3. **What moves on regeneration.** Relevant. The `<PREFIX>_TARGETS` stamp is an abi event once
   (§6). Re-measuring a target's set moves only that variant's picks and its MEMFN_FORMS value
   (D188, per variant). levels.def's `needs` column is kit-private (C4), so it is not a pcrec abi
   event. A kit byte move under a non-default target is a pcrec abi event only for artifacts that
   list that target (D146/D147).

## 10. Ruled vs open

RULED: per-target variants, no `#if` arms, target-attributed functions, once-per-process dispatch,
an explicit list with a stamped default (D188 add. 1); facts only (D157); no artifact static
(D155 add. 5); a split-shaped seam with no split now (Frank, 2026-11-06).

PROPOSED here: the art as the variant unit; `target.features` as the fact; levels.def `guard` ->
`needs`; headers as a returned fact; per-variant stems from pcrec; dispatch at entries only (which
retires the per-site frequency class); the stamp as its own first abi event; the §8 measurement.

OPEN: (Q1) mixed-family lists (x86 + aarch64 in one artifact need a family `#if`; leaning: refuse,
one family per artifact, since one compiler run targets one family); (Q2) whether `rx_info` lists
the variants (leaning: yes, at [IFACE-PUSH]); (Q3) whether length decisions keep subtracting
target-dependent bytes (leaning: yes, so a variant's plan differs only by priced facts, never by
its own text size); (Q4) pragma region vs per-head attribute (leaning: pragma, since it needs no
kit change); (Q5) whether requirements.md RB-3 ("compile-time ISA selection" by predefined macros)
is amended to "selection by the declared target" (leaning: yes, at the build).
