# Lane datad — [DATA-PLAN] design note (report)

Lane `datad` (opus), branch `lane/datad` from main `74ecca07a`, 2026-10-24.
Design only: no code, no plan rows, no spec. Deliverable:
`docs/design/data_plan.md` (PROPOSED), instruments in `docs/design/data_plan/`,
and an index line in `docs/design/CLAUDE.md`.

## STATE AT HANDOFF

- Note complete. It covers both problems the rulings asked for, each with
  goals, options, a recommendation and a staged plan: A (pcrec's own size)
  and B (Unicode data in matchers). Four questions for Frank are in §6.
- Rulings applied: R1 (two problems, A and B; project A's growth) and R2
  (A is a format question: measure the formats; for B, split data from code).
  The last entry applied is **R2**.
- Premise test: REPRODUCED with main's `build/pcrec`. `\p{L}` -e utf8:
  586,042 B of C, 184,392 B loadable. `\p{Greek}`: 14,275 B. A literal:
  4,130 B.
- No runs owed. Nothing was built in this worktree. All measurements are
  single-process size probes plus one µs-scale decode probe, taken while
  `610-substland-test` (not a timing job) held the box.

## Findings (what the manager needs)

1. **STOP RULE (partial):** a `\p{L}` matcher's 185 KB is the class spelled
   out as a UTF-8 byte DFA (a 299-state × 100-class transition table, forward
   and anchored, plus per-cell accept arrays). It is 3.9 KB of code and 180 KB
   of tables, and NO property data. That automaton is specific to the
   pattern, so it cannot be shared. The VM route of the same class is 8.5 KB
   (a 4.5 KB kit predicate). The lever for B is the FORM (22x). Sharing gives
   ~1x per extra matcher today.
2. `--tune=min-size` does not reach the small form (`\p{L}` 125 KB, still
   DFA). UCP `\w` under utf8 is refused today for exactly this cost.
3. General tables already repeat across matchers. The caseless-utf8
   back-reference `rx_span_ci_fold_pairs` is 11,872 B and byte-identical
   across patterns. The kit predicates are 4-6 KB. The subst case maps (23 KB)
   are already shared through the support unit.
4. Linker sharing works on gcc + GNU ld with no user flags: a section-name
   COMDAT, 3 copies → 1 (26,061 → 9,677 B). `weak` alone does not dedup
   without `--gc-sections`. Darwin is unverified.
5. **A is a format problem (R2).** [UPROP-MORE] (measured on `upropb`'s WIP)
   takes the interval pool from 87.7 KB to 208 KB and `mod_uprops.o` from 110
   to 255 KB: UCD data goes from ~11% to ~20% of the compiler. Delta-varint
   gives 3.6x (208 → 58 KB) with no dependency and ~1 µs per property.
   zlib/xz give 9-10x but need an inflater. Per-property compressed bitmaps
   are WORSE in total (168 KB). A naive shared two-stage table is 332 KB. The
   name table also pays ~32 B per row in pointer + PIE relocation.
6. Corrections to the D178/plan-row figure: the compiler's loadable size is
   1.42 MB (+141 KB of relocations), not 5.9 MB (that file is mostly debug
   info). D125 is not the [UCD-RECORD] decision (it is the close-out
   sequence); the plan row's "D125: filed" text is the source of that cite.

## Recommendation (from the note's §4)

- B: (1) measure the VM route against the DFA for wide classes on the utf8
  bench (1 sonnet lane + a night window); (2) route wide classes to the kit
  form at `--tune=size`/`min-size` only, with the default byte-identical (1
  opus lane); (3) the island (UCP U3, already designed with θ) brings the
  small form to the default route, and its size is measured at acceptance;
  (4) shared data parts (content-id COMDAT / support unit / static as one
  linkage table, the family of part-layout + support unit + [XART-TABLES]),
  triggered by the first ≥16 KB general table that repeats.
- A: one sonnet lane after `upropb` lands: delta-varint interval lists and a
  string-blob name table in `generate.py` + `mod_uprops`, with artifacts
  byte-identical. The trigger is already met (~20% > 15%). A data file
  beside pcrec, compression and build-time data groups are not recommended;
  each has a stated trigger.

## Questions for Frank (plain words; the note's §6)

1. The small form for big Unicode classes: opt-in (`--tune=size`) first, or
   the default once measured? It may cost up to ~1.5x speed on accented or
   mixed text.
2. Is there a size target (a device, a limit for pcrec), or is the aim
   "don't be wasteful"?
3. For pcrec's own tables: is "store small differences, no compression
   library" (3.6x) enough, or do you want zlib-level (9x) with a
   decompressor added?
4. Sharing across matchers: automatic through the linker (works on
   Linux/gcc, Mac unverified), or an explicit shared file like subst's
   support unit? Build it only when a big shared table arrives.

## Files

- `docs/design/data_plan.md` — the note.
- `docs/design/data_plan/` — `measure.sh`, `formats.py`, `dec.c`, CLAUDE.md.
- `docs/design/CLAUDE.md` — index line.
