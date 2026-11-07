# The target seam's build, as ordered units

STATUS: rev 0 (lane xarch1, 2026-11-07, off main 49bdd374d). The unit split of
`target_seam.md` rev 1 under Frank's [XARCH-DEV] build go (2026-11-07). The
design is the note; this file only orders it. Rulings: the note's §0/§11, the
review `docs/dev/reviews/2026-11-07-r1-xarch.md` RULING block, the brief (the
dispatch step that puts `x86-64-v3` into the x86-64 default list waits for a
bench speed verdict, D144 add. 4; new caller-facing names get working
spellings, F17/[STAMP-REVIEW]).

## 1. Cite check at main HEAD 49bdd374d

The note's cites were taken at 6fc4b6912. Re-held here; drift is listed.

| cite | holds? |
|---|---|
| levels.def:41-46 (the two `MF_LEVEL` rows, guards) | holds |
| ofsskip.c `fn_level_block` 568-575, `fn_selector` 590-611, the rung loop 686-687 | holds |
| vany.c `vany_level` 157, 178; `vany_selector` 184-198 | holds |
| vany.c `mf_kernel_find_any` 210-215 | holds (the function starts at 201; 210-215 is its level-mask check) |
| runcmp.c word load ":533-535 on main, :542-544 on 5b6cf41aa" | DRIFT: S2e is merged (03ddf925d), so main has it at :542-543 |
| §4 "lane/memfn-s2e's form-hash entry table (formhash.c, 5b6cf41aa)" as in flight | DRIFT: formhash.c is on main; its entry table still keys every row by the policy word (`MF_P_PORTABLE_ONLY` in each row), so the `target` column it needs is unchanged |
| §4 the `MF_P_PORTABLE_ONLY` reader list | DRIFT: one more reader, sabotage S2930 (`S2930_formhash_two_ids_one_text.sh`); `memfn/CLAUDE.md` names it too (doc) |
| §4 "the `[FLD_policy]` column of 10 kit rows" | grep finds 9 sites (two of them, window.c and finder.c, are row macros) plus the reader in gate.c:769; the row count behind the macros is not re-counted here |
| §2 the `x86-64-v3` additive list | DRIFT, the table check's first finding: `gcc -march=x86-64-v3` defines `__LAHF_SAHF__`, which the listed attributes do not enable. With `sahf` added, `gcc -march=x86-64 -mno-sse -m<each>` defines exactly the macros `-march=x86-64-v3` does (whole `-dM` output, gcc 15.2). Unit 1 adds it |
| spec anchors: match_api §1¶2, §3.8, §5.3, §6.3.2, §6.3.10¶3/¶8, §6.3.12, §10.7; cli.md §1.6¶2, §1.16¶5 | hold |
| PREMISE TEST: §2's target rows against what pcrec knows of `-fmemfn-simd` | holds: src knows only the axes.def force pair and `pcrec_memfn_policy` (one bit); the kit's `levels.def` `test_march` column names `x86-64` (w16) and `x86-64-v3` (w32), §2's two x86 rows |
| NOT IN THE NOTE: C4, the arch-blindness detector (`test-memfn-arch`, D146/D147, integration.md §10.4) | the note's D146 addendum puts ISA vocabulary into pcrec (the target table); C4 forbade it outside an allowlist that "only descends". RULED (xarch1 R1): C4 exempts `src/gen/targets.def` by exact path, with a scratch control; the allowlist does not grow. Recorded in integration.md §10.4 `[xarch1 R1]` and D146 addendum 1. A later C4 scope fix keeps the exemption |

## 2. The units

Owner: P = the pcrec main lane, K = the memfn kit (it owns `memfn/`). "Bytes"
is at the default (`{generic}`) and at `-fmemfn-simd` (the family's default
list, `x86-64` alone).

| unit | owner | what | files | checks it lands (§7/§8) | bytes | unblocks for the kit |
|---|---|---|---|---|---|---|
| **U1** (BUILT, lane xarch1) | P | the target table (family rows, target rows), the make-time table check, the first-match list table, the policy word read off the resolved set, the region and family-guard renderers | `src/gen/targets.def`, `src/gen/targets.c`, `src/gen/memfn_stamps.c` (`pcrec_memfn_policy`), `src/core/internal.h`, `scripts/check_targets.sh`, `Makefile`, `tests/memfn/{run_targets.sh,targets_check.c,arch_blind_check.py}`, `tests/ci/shards.tsv` | §2's table check; §8's compile cells and family-guard cells on a kit-shaped fixture; the host-resolution cell | 0 at both | **FIRST**: the feature tokens and family names its `needs` column and admission are written against, and the region harness its `#if`-free forms are compiled in (G1's measurable form), before any switch |
| **U2** | K | the request carries `target` (family, sorted features); `levels.def` `guard` -> `needs`; admission `family && needs ⊆ features`; level blocks lose `#if`/`#endif` (the include stays); the selector is one call to the top admitted rung, or `__body`; `mf_kernel_find_any`'s mask from the features; the `FLD_policy` SIMD reading -> a gate field on `needs ⊆ features`; formhash.c's entry table gains `target`; the kit's `MF_P_PORTABLE_ONLY` readers retire | `memfn/include/memfn.h`, `memfn/src/{levels.def,levels.c,ofsskip.c,vany.c,gate.c,fields.def,vrun.c,formhash.c}`, `memfn/tests/g2/*_gen.c` | the kit's own G1 compile at each level's target with zero CPU `#if` | moves `-fmemfn-simd` only (lands WITH U3) | its SIMD forms are written `#if`-free from here on: S2g (vrun) and every later form |
| **U3** | P, landing with U2 in ONE merge and ONE abi event | pcrec fills `target` from a ONE-member set; emits the family guard and the region pair; `<PREFIX>_TARGETS` on every artifact (F16's ride-along: this is the first unit that moves bytes); a one-member target list and the family as caller inputs (working spellings, §3); pcrec's `MF_P_PORTABLE_ONLY` readers retire; the RB-3/M-5 amendments are filed | `src/gen/{memfn_sites.c,memfn_stamps.c,emit_*.c}`, `lib/pcrec.h`, `cli/main.c`, `src/parse/rxt_schema.def`, `tests/memfn/{proven_check,arm_fixtures,proof_check,targets_check}.c`, `run_proof.sh`, sabotages S722/S1224/S2930, pins (tests/cli MEMFN_FORMS, tests/memfn row_floors/simd_accept, emit_sweep DIFFER_PINS) re-taken at the x86-64 family | §7's source-move arm and the `.text` compare at default `-march` (G2b); §8's compile cells on real artifacts; pins taken with the family explicit | default: the abi digits and the TARGETS line only (declared); `-fmemfn-simd`: guard, region, the `#if` arms gone, and `vrun@w32+w16` -> `vrun@w16` (w32 is not admitted at `x86-64`) | w32 forms reachable again through the one-member list `x86-64-v3` |
| **U4** | P (+ K2) | multi-member lists in one family: `<prefix>__<T'>` stems, one part per target-dependent art (the elision fact), the compound controller's `cpu` column, the per-call probe with `__builtin_cpu_init()`, the §5 surface table (controller MAX/union stamps, per-part stamps INSIDE the region = D188 fact (b)), `rx_buffers` once, the continuation rule | `src/gen/emit_compound.c`, `entries.c`, `emit_*.c`, `lib/pcrec.h`, spec | §8 per-part answers, WHICH part ran (harness hook + forced-probe lever), the target-code census (objdump), the RAN floor; D165 item 5's parity measurement; PROBE-8 if S has landed; F15's test-time measurement; the D27 spec-first tests | moves only multi-member artifacts (new); one-member lists unchanged | the kit's w32 forms run beside w16 in one artifact |
| K2 | K | per art: the `target_dependent` (elision) fact; stamps per art | memfn/ | its own | none alone | needed by U4 |
| M1 | P (queue) | §9's first size measurement over the corpus, `{x86-64}` vs `{x86-64, x86-64-v3}` | scratch, report | n/a | none | the evidence for U5 |
| U5 | P, HELD | the dispatch step: the x86-64 family default list becomes `x86-64,x86-64-v3` | `src/gen/targets.def` (one row), spec, pins | an abi event of the SIMD-on axis | moves every SIMD-reaching `-fmemfn-simd` artifact | HELD for a bench speed verdict (§9 benefit, D144 add. 4); not in this go |

Order: U1 -> (U2 + U3, one landing) -> K2 -> U4 -> M1 -> U5 (held). U1 is
pcrec-owned and is the one the kit needs first; this lane builds it.

## 3. What each later unit carries for the contract (D80) and the log

**Spec hunks.**
- U1: tuning.md §2.43¶3, one sentence: on a host pcrec knows no target family
  for, `-fmemfn-simd` resolves to the generic target (so the one bit is set)
  rather than to a family's list. No other caller-observable change.
- U3: tuning.md §2.43¶2-4 (the flag is an alias of the family's default list;
  "carries no ISA axis of its own" becomes false; ¶3a's `#if` chain becomes
  the region; `test-memfn-simdfloor` loses its subject); match_api §6.3.2,
  §6.3.10¶3-4/¶8-9 (TARGETS; MEMFN_FORMS' levels; SIMD_GUARDED_BYTES read as
  "bytes inside the region"), §10.7 (the baseline region compiles under
  `-mno-sse2`/`-mgeneral-regs-only`; a consumer that forbids vector registers
  uses the default); cli.md for the two new options.
- U4: match_api §1¶2, §3.x (part entries), §3.8 (continuation), §5.3 (the
  libgcc probe is not an artifact static), §6.3.12, §10.7 (libgcc "allowed,
  guarded and stated", D155 Q-R9-8); cli.md §1.6¶2 (stems), §1.16¶5.

**Requirements amendments (the note's §6.3, `requirements.md`), drafts.**
- U3, RB-3: "The inline forms select their ISA by the art's DECLARED TARGET:
  pcrec states the target's family and features, and the kit renders the
  levels whose needs those features cover. The text carries no CPU `#if` and
  no CPU detection; pcrec's region supplies the target's ISA. The scalar or
  SWAR fallback always compiles. The baseline vector tier needs no `-m` flag
  (the family's baseline region supplies it)."
- U3, M-5: "ISA selection by the declared target at compile time, scalar
  fallback present, no mutable static; a run-time choice only in pcrec's
  controller (N-4)."
- U4, N-4: the sentence "no `__builtin_cpu_supports`" becomes "no
  `__builtin_cpu_supports` in kit text; pcrec's controller alone probes,
  per call, through libgcc (target_seam.md §6.2)".

**Decision addenda** (filed into decisions.md only in the unit named):
- U1 filed the D146 addendum (as D146 addendum 1), the note's §6.4 text
  verbatim: U1 builds the table it rules on, and C4's exemption cites it.
  Its "pcrec hands the kit feature tokens" sentence is first exercised at U3.
- U4 files D155 addendum 6 / [MEMFN-RTDISPATCH], the note's §6.4 text
  verbatim.

## 4. Choices this lane made, and the open question

- LANE CHOICE (answer-free): `sahf` joins the `x86-64-v3` additive list
  (§1's drift row).
- LANE CHOICE (answer-free): the table check's control is the compiler's
  whole `-dM` set: for each target of the host's family, `gcc -march=<family
  floor> -m<each attribute>` must define exactly what `gcc -march=<name>`
  does. The floor (`-march=x86-64 -mno-sse` for x86-64) belongs to the
  check, not to the table, so the baseline row `sse2` is a real comparison
  and not `x86-64` against itself. A target of another family is SKIPPED and
  counted.
- LANE CHOICE (answer-free): the table check runs at `make` and a mismatch is
  a loud warning plus a status file that `make strict` and the check's test
  section fail on. A plain `make` does not fail on it: a newer gcc's own
  `-march` definition is exactly the case R5-Q1 keeps from breaking a
  stranger's build.
- LANE CHOICE (answer-free): on a host with no family row, rule 3 of the list
  table resolves to `{generic}`. Today `-fmemfn-simd` there renders x86 arms
  under `#if`s that host never takes. No box or check runs such a host.
- LANE CHOICE (answer-free): U1's resolved set feeds today's one policy bit
  (set iff the set is `{generic}`), so the table is live from U1 and the flag
  is an alias from U1 (§2 "never a second gate").
- RULED (R1, manager): C4 and the target table: one named scope exemption
  in C4 for `src/gen/targets.def`, beside memfn/'s, proved by a scratch plant
  in another src/gen file; the renderers read the .def and spell no ISA word.
  A mech sabotage row for the exemption needs an S-id this lane was not given
  (the brief names none): OWED to the manager's range.
- FOR U3 (not ruled here): the family option is needed at U3, not later,
  because the `-fmemfn-simd` pins must read the same on the Mac (§8, F2(c));
  the one-member list option is needed at U3 too, or the w32 forms have no
  route through pcrec. Both take working spellings at U3 (Q4 stays
  [EMIT-ENTRIES]'s); multi-member lists are refused until U4.
