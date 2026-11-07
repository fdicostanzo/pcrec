# The target seam's build, as ordered units

STATUS: rev 1 (lane xarch1, 2026-11-07, off main 49bdd374d), over rev 0. The
unit split of `target_seam.md` rev 1 under Frank's [XARCH-DEV] build go
(2026-11-07), REVISED for the lane's rulings R3 and R4 (Frank's direction,
2026-11-07; `docs/dev/lanes/xarch1_rulings.md`): **pcrec carries no CPU
knowledge.** Targets are OPAQUE TOKENS in pcrec; the target table lives in
the kit; an unknown token fails at option parse with the kit's reason. This
supersedes the note's §2 placement ("pcrec owns ONE target table") and its
§6.4 D146 addendum text (§4 below drafts the replacement). CODE WAITS until
the manager has read this revision (R3).

Other rulings in force: the note's §0/§11; the review
`docs/dev/reviews/2026-11-07-r1-xarch.md` RULING block; the brief (the
dispatch step that grows the x86-64 default list waits for a bench speed
verdict, D144 add. 4; new caller-facing names get working spellings,
F17/[STAMP-REVIEW]).

## R1. What rev 1 changed

| ruling | change | § |
|---|---|---|
| R3 | the table (families, targets, features, `needs`, the region and guard text, the run-time CPU predicate, the host default) moves to the kit; pcrec keeps the structure (list, parts, stems, controller, entries, stamps, CLI) | §2, §3 |
| R3 | C4 needs no exemption; R1 (the `src/gen/targets.def` exemption) is withdrawn | §1 |
| R3 | the kit's table unit K0 is FIRST | §2 |
| R4 | pcrec asks the kit to parse each token at option parse; the refusal text is the kit's | §2 (P1), §3 |
| R2 | `sahf` moves with the table into the kit's `x86-64-v3` row | §2 (K0) |

Rev 0's pcrec unit U1 was built on lane/xarch1 under R1 (commit 171bdb343)
and reverted under R3 (commit 05d713ac6). Its parts are reference material
for K0: the rows as checked, the table check against gcc's `-march`
(`scripts/check_targets.sh`), and the compile-cell harness
(`tests/memfn/run_targets.sh`, `targets_check.c`). §5 lists what they
measured.

## 1. Cite check at main HEAD 49bdd374d

The note's cites were taken at 6fc4b6912. Re-held here; drift is listed.

| cite | holds? |
|---|---|
| levels.def:41-46 (the two `MF_LEVEL` rows, guards) | holds |
| ofsskip.c `fn_level_block` 568-575, `fn_selector` 590-611, the rung loop 686-687 | holds |
| vany.c `vany_level` 157, 178; `vany_selector` 184-198 | holds |
| vany.c `mf_kernel_find_any` 210-215 | holds (the function starts at 201; 210-215 is its level-mask check) |
| runcmp.c word load ":533-535 on main, :542-544 on 5b6cf41aa" | DRIFT: S2e is merged (03ddf925d), so main has it at :542-543 |
| §4 "lane/memfn-s2e's form-hash entry table (formhash.c, 5b6cf41aa)" as in flight | DRIFT: formhash.c is on main; its entry table still keys every row by the policy word, so the `target` column it needs is unchanged |
| §4 the `MF_P_PORTABLE_ONLY` reader list | DRIFT: one more reader, sabotage S2930 (`S2930_formhash_two_ids_one_text.sh`); `memfn/CLAUDE.md` names it too (doc) |
| §4 "the `[FLD_policy]` column of 10 kit rows" | grep finds 9 sites (two of them, window.c and finder.c, are row macros) plus the reader in gate.c:769; the rows behind the macros are not re-counted |
| §2 the `x86-64-v3` additive list | DRIFT, the table check's first finding: `gcc -march=x86-64-v3` defines `__LAHF_SAHF__`, which the listed attributes do not enable. With `sahf` added, `gcc -march=x86-64 -mno-sse -m<each>` defines exactly the macros `-march=x86-64-v3` does (whole `-dM` output, gcc 15.2). R2: it goes into the kit's row |
| spec anchors: match_api §1¶2, §3.8, §5.3, §6.3.2, §6.3.10¶3/¶8, §6.3.12, §10.7; cli.md §1.6¶2, §1.16¶5 | hold |
| PREMISE TEST: §2's target rows against what pcrec knows of `-fmemfn-simd` | holds: src knows only the axes.def force pair and `pcrec_memfn_policy` (one bit); the kit's `levels.def` `test_march` column names `x86-64` (w16) and `x86-64-v3` (w32), §2's two x86 rows |
| C4, the arch-blindness detector (`test-memfn-arch`, D146/D147, integration.md §10.4) | the note's §2 placement would have broken it; under R3 its premise ("pcrec carries no architecture knowledge") HOLDS unchanged, and memfn/ is already exempt |
| §6.1's region pair (`#if defined(__clang__)` ...) | a compiler-capability test, but its text names `target(...)` (C4 class 5), so under R3 the kit renders it too |

## 2. The units

Owner: P = the pcrec main lane, K = the memfn kit (it owns `memfn/`). Bytes
at the default (`{generic}`) and at `-fmemfn-simd` (the family's default
list, `x86-64` alone).

| unit | owner | what | checks it lands | bytes | unblocks |
|---|---|---|---|---|---|
| **K0** FIRST | K | THE TARGET TABLE in the kit: tokens `generic`, `x86-64`, `x86-64-v3`, `aarch64`; families with their default lists and the host default (the kit is compiled into libpcrec, so its build host is pcrec's); per token: family, sorted features, the region text (open, close), the family guard text, the run-time CPU predicate text (for U4); and the entries pcrec calls: parse a target token, parse a family token (each: valid + canonical form, or the kit's named refusal, R4), the default list for a family or for the host, the portable token, the region and guard text for a token | the table check against gcc's own `-march` (rev 0's `check_targets.sh` shape); the compile cells (rev 0's harness shape); C4 unaffected (memfn/ is exempt) | none (pcrec calls nothing yet) | P1 |
| **P1** | P | THE STRUCTURE, 0 bytes: the target-list and family options (CLI, `pcrec_options`, `.rxt` directive; working spellings), each token parsed by the kit AT OPTION PARSE (an unknown token fails there, with the kit's text, before any compile work; R4); the first-match list table over opaque tokens (deny -> the kit's portable token; a list -> as given, the kit confirming one family; force -> the kit's default list for the family given, else the host's; neither -> the portable token); the kit's one policy bit read off the set (portable iff the set is the portable token); one-member sets only (a multi-member list refused until U4) | the list table's rows; the early-fail cells (an unknown target and an unknown family each refused at parse with the kit's text, before any compile work); `emit_sweep --ref` at the default and `--extra=-fmemfn-simd`: 0 moved | 0 at both | U3 |
| **U2** | K | `levels.def` `guard` -> `needs`; admission `family && needs ⊆ features` against the art's token; level blocks lose `#if`/`#endif` (the include stays); the selector is one call to the top admitted rung, or `__body`; `mf_kernel_find_any`'s mask from the features; the `FLD_policy` SIMD reading -> a gate field; formhash.c's entry table gains `target`; the kit's `MF_P_PORTABLE_ONLY` readers retire | the kit's G1 compile at each level's target with zero CPU `#if` | moves `-fmemfn-simd` only (lands WITH U3) | the kit's SIMD forms are `#if`-free from here on (S2g and later) |
| **U3** | P, landing with U2 in ONE merge and ONE abi event | pcrec passes the art's token across the seam; places the kit's family guard text at file scope and the kit's region text around the part; `<PREFIX>_TARGETS` on every artifact (F16's ride-along: the first unit that moves bytes); pcrec's `MF_P_PORTABLE_ONLY` readers retire (lib/pcrec.h, src/core/internal.h, src/gen/memfn_stamps.c, src/gen/memfn_sites.h, tests/memfn/{proven_check,arm_fixtures,proof_check}.c, run_proof.sh, S722, S1224, S2930) | §7's source-move arm and the `.text` compare at default `-march` (G2b); §8's compile cells on real artifacts; pins (tests/cli MEMFN_FORMS, tests/memfn row_floors/simd_accept, emit_sweep DIFFER_PINS) taken with the family explicit | default: the abi digits and the TARGETS line only (declared); `-fmemfn-simd`: guard, region, the `#if` arms gone, and `vrun@w32+w16` -> `vrun@w16` (`x86-64` admits w16 only) | w32 forms reachable through the one-member list `x86-64-v3` |
| K2 | K | per art: the `target_dependent` (elision) fact; stamps per art | its own | none alone | U4 |
| **U4** | P | multi-member lists in one family: `<prefix>__<T'>` stems from the token, one part per target-dependent art, the compound controller's `cpu` column calling the kit's predicate text per call, the §5 surface table, `rx_buffers` once, the continuation rule | §8 per-part answers, WHICH part ran, the target-code census, the RAN floor; D165 item 5's parity measurement; PROBE-8 if S has landed; F15's test-time measurement; the D27 spec-first tests | moves only multi-member artifacts (new) | the kit's w32 forms run beside w16 in one artifact |
| M1 | P (queue) | §9's first size measurement, `{x86-64}` vs `{x86-64, x86-64-v3}` | n/a | none | U5's evidence |
| U5 | K (row) + P (pins), HELD | the x86-64 family's default list becomes `x86-64,x86-64-v3` (now a KIT table row) | an abi event of the SIMD-on axis | every SIMD-reaching `-fmemfn-simd` artifact | HELD for a bench speed verdict (§9, D144 add. 4) |

Order: K0 -> P1 -> (U2 + U3, one landing) -> K2 -> U4 -> M1 -> U5 (held).
The kit needs nothing from pcrec to build K0; P1 is pcrec's first unit and
waits for K0's entries.

## 3. The seam, revised (facts only, D146/D157)

- pcrec -> kit: the art's target TOKEN (opaque; pcrec reads no part of it),
  and the family token when the caller gave one. The site facts are
  otherwise unchanged.
- kit -> pcrec: per token at option parse, valid + canonical form or the
  refusal text (R4); per family, the default list; the portable token; per
  token at emission, the region text (open, close) and the family guard
  text, which pcrec places where the note's §5 puts them (once per artifact,
  around a part); at U4, the CPU predicate text the controller calls.
- What pcrec still decides: the list table's rows (which input wins), the
  one-family rule's enforcement point (it asks the kit each member's family
  token and compares tokens), parts, stems, the controller, entries,
  stamps, the CLI. All of it on strings.

## 4. What each unit carries for the contract (D80) and the log

**Spec hunks.**
- P1: cli.md (the two options, refusal at parse); the `pcrec_options` field
  in the library contract; rxt_format.md (the directive); tuning.md
  §2.43¶1/¶3 (the flag pair is an alias of the list table; the policy bit
  reads the set; the default list is the kit's).
- U3: tuning.md §2.43¶2-4 (¶3a's `#if` chain becomes the region; "carries no
  ISA axis of its own" stays true of pcrec: the axis's values are the kit's);
  match_api §6.3.2, §6.3.10¶3-4/¶8-9 (TARGETS; MEMFN_FORMS' levels;
  SIMD_GUARDED_BYTES as "bytes inside the region"), §10.7 (the baseline
  region compiles under `-mno-sse2`/`-mgeneral-regs-only`; a consumer that
  forbids vector registers uses the default).
- U4: match_api §1¶2, §3.x (part entries), §3.8 (continuation), §5.3 (the
  libgcc probe is not an artifact static), §6.3.12, §10.7 (libgcc "allowed,
  guarded and stated", D155 Q-R9-8); cli.md §1.6¶2 (stems), §1.16¶5.

**Requirements amendments** (the note's §6.3, `requirements.md`), drafts:
- U3, RB-3: "The inline forms select their ISA by the art's DECLARED
  TARGET, a token pcrec passes and the kit's target table resolves: the kit
  renders the levels whose needs the target's features cover. The text
  carries no CPU `#if` and no CPU detection; the target's region supplies its
  ISA. The scalar or SWAR fallback always compiles. The baseline vector tier
  needs no `-m` flag (the family's baseline region supplies it)."
- U3, M-5: "ISA selection by the declared target at compile time, scalar
  fallback present, no mutable static; a run-time choice only in pcrec's
  controller, through the kit's predicate text (N-4)."
- U4, N-4: "no `__builtin_cpu_supports` in a form's text; the kit's
  per-target predicate text is called only by pcrec's controller, per call,
  through libgcc (target_seam.md §6.2)".

**Decision addenda** (filed into decisions.md only in the unit that
implements them):
- The note's §6.4 D146 addendum text is SUPERSEDED by R3. Replacement draft,
  filed at K0 (the kit's table) or P1 (the first pcrec reader), whichever
  lands first: "D146 addendum (target tokens): targets are opaque tokens in
  pcrec. The target table (families, targets, features, the region and guard
  text, the run-time CPU predicate, the host default) is the kit's, returned
  per token as facts and text; pcrec validates a token only by asking the
  kit, at option parse, and passes it across the seam. pcrec keeps the
  structure: the list, parts, stems, the controller, entries and stamps."
- U4 files D155 addendum 6 / [MEMFN-RTDISPATCH], the note's §6.4 text, with
  one change: the controller's `cpu` predicate is the kit's text.

## 5. Lane choices, and what rev 0's withdrawn U1 measured

- LANE CHOICE (answer-free): pcrec names no token at all, `generic`
  included; the default set is the kit's portable token, asked once.
- LANE CHOICE (answer-free, for K0 to adopt or refuse): the table check's
  control is gcc's whole `-dM` set at the family floor (`-march=x86-64
  -mno-sse`) plus each attribute, against `-march=<name>`; gcc whatever CC
  is (clang's set differs by CPU-name macros alone, `__k8`); at `make`, a
  mismatch warns (R5-Q1) and `make strict` fails.
- Rev 0's U1 measured (gcc 15.2, clang 21.1.8, dev box), as K0's starting
  evidence. The table check passed with `sahf` added, and its two failing
  directions were seen (a dropped `sahf`; a baseline of the wrong family).
  The compile cells (a kit-shaped `#if`-free fixture in the region pair):
  9 of 9 ran (gcc default, native, x86-64-v4, `-mno-sse2`,
  `-mgeneral-regs-only`, x86-64-v2; clang default, native, v4), 40,602
  answer checks each, 0 bad. objdump at default `-march`: the v3 part 3 ymm,
  the baseline part 7 xmm, the generic part 0 ymm. The family guard refused
  `gcc -m32` and `clang --target=aarch64-linux-gnu` with its own message.
  With the region lines stripped, the fixture failed under both compilers.
  These held the note's §6.1 claims at 9 cells.
- FOR P1 (not ruled here): the family option is needed by P1, because the
  `-fmemfn-simd` pins must read the same on the Mac (§8, F2(c)), and the
  one-member list option too, or U2 leaves the w32 forms no route through
  pcrec. Both as working spellings (Q4 stays [EMIT-ENTRIES]'s).

## 6. Manager rulings at the merge (2026-11-07)

- R1 (C4 exemption for a pcrec target table) SUPERSEDED by R3 (Frank: opaque tokens; the kit owns the table) and R4 (Frank: the kit parses each token at option parse, early fail with the kit's text). Full text: docs/dev/reviews/2026-11-07-xarch1-rulings.md.
- WORKING SPELLINGS for P1 (D174 binds; final names at [IFACE-PUSH]/[STAMP-REVIEW]): `--cpu-family=NAME` and `--cpu-targets=LIST` (a one-member list is the build-time single variant). NOT `--family`/`--targets`: "family" already names the feature families ([FEAT-FAMILIES], basic/extended/pcre2), so the bare word would read as that.
- Order adopted: K0 (kit) first, then P1 (pcrec). The REPLACEMENT D146 addendum is filed with K0's landing.
