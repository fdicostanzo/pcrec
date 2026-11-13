# flagprep report (lane flagprep, 2026-11-12, sonnet; design map only, NO build go)

Deliverable: `docs/design/flag_demote_map.md` (the internal deny word design, the
per-flag site table for the 20 + the drop, the commit order, the bench inbox draft,
the rulings needed). Read it first; this report is the handoff and the findings.

## STATE AT HANDOFF

- STATE: complete. Design map written and committed on lane/flagprep (from main
  a1d7743bf). No file under src/, cli/, lib/ or memfn/ was edited; pcrec-bench was
  read only. No build, no suite run (evening hold; greps and `build/pcrec
  --list-axes` from the main tree only). OWED runs: none.
- Rulings file `docs/dev/lanes/flagprep_rulings.md`: absent at handoff (nothing
  to apply).
- Premise test: the main tree's `build/pcrec --list-axes` lists the public deny
  flags; all 21 flags of the task are rows of `src/core/axes.def` and appear in it.
- Needs rulings before a build go (map section 5): R1 the lever fence, R2 the
  tuning.md "(bit N)" headings, R3 `rx_info.flags` for 12 and 50, R4 the sweep
  tool's two-sided `--extra`, R5 freed-bit policy.

## FINDINGS

1. The internal word: recommended design is tagged keys (`PCREC_XTAG` = bit 63 of
   the public word, internal keys `XTAG | bit n`) with one `uint64_t xdeny` in
   `Ctx`, assembled per attempt from the harness lever, the dial and the ladder,
   read through one accessor `pcrec_cx_has` and one primitive `pcrec_key_has` in
   the FLAG-ACCESS block (`src/core/internal.h:553-570`). Tagged keys let
   `axes.def`, `axes_dump.c`, `--list-axes`, `facts.def`, `DfaCand`, `ctxnode.c`
   and `clskit.c` keep carrying a key as a `uint64_t`; only three evaluators
   (`src/gen/emit_dfa.c:6014`, `:10977`, `:13994`) and about 50 direct readers
   change, once each. Alternatives rejected in the map: keep the bits in place
   (cheap, but the positions are not free), a second column per table, 128-bit keys.
2. Only two of the 20 are written by the ladder or dial: premul (15,
   `src/core/compile.c:1445`, `src/core/tune.c:81`) and alt-island (23,
   `src/core/compile.c:1486`). They are the proving pair of the enabling commit.
3. Compound parts drop the lever: `part_compile` (`src/core/compound.c:58-76`)
   builds its emit input with `.harness = NULL` and copies only `parent->flags`, so
   a harness-set denial would silently stop at the compound shell. The map carries
   the word through `PcrecEmitIn.xdeny`.
4. NO abi bump expected, against the audit: a default artifact's `.flags` never
   carries bits 12 or 50 (`src/gen/emit_dfa.c:3300` masks all axis bits not in
   `kept`), so removing them from `kept` changes only artifacts built under the
   lever. The spec hunk is owed (tuning.md §2¶3). The build lane must prove it with
   the identity gate and stop if it moves.
5. The lever fence blocks the plan as written: `tests/compound/run_lever_fence.sh`
   check (c) forbids `--harness=` in docs/spec, docs/guide, README, examples, lib,
   tests, scripts and cli outside an allowlist. 118 files under tests/ and 3 in
   scripts/ name the 21 flags. Ruling R1 (split the fence by lever family) is the
   first commit.
6. STOP-RULE CASE, pcrec-bench contract break (flagged, rest of the map done):
   `testees/pcrec/adapter.py:3421` `DENY_FLAGS` names 12 of the 21 and the
   spelling feeds the derived `testee_id`; `tools/selfcheck.py` runs about 25
   sites of these flags against a pin's `build/pcrec`; `configs.toml:630,695,701`
   pin `-fno-alt-island` and `-fno-cls-fold`; `testees/pcrec/list_axes.tsv` is
   the verbatim registry archive under the [B18] gate. Old pins are unaffected.
   The audit counted only 2 pinned configs. Inbox draft is in map section 4.
7. The sweep tool: `scripts/emit_sweep.py --extra` appends an arm to BOTH sides of
   a cross-revision compare, and the old side has no `--harness=no-X`; 16
   `DIFFER_PINS` cells (length-prune, start-pinned, vm-anchor-bound, end-window)
   are affected (R4).
8. `run_axes.sh` skips a `cli_flag` beginning `--` (written for `--engine=`) and
   derives its bit list by grepping `lib/pcrec.h`, so the demoted axes would drop
   out of the sweep's coverage guard silently unless it also derives the internal
   keys. The map's re-aim keeps the hard-fail on zero (learnings §3).
9. Not unsafe to demote after all: none of the 20 fails. Judgment notes for Frank:
   29 (end-window) is today the only field-usable bisect for a suspected
   end-window miscompile (the rule's intended consequence); 17 and 15 are the
   strongest size knobs (15 stays reachable via `--tune=-2`). Bit 55 has no
   macro and no reader: safe to release (comment only).
10. Commit order: C0 fence ruling; C1 the word plus premul and alt-island with
    five sabotage rows; C2 direct readers (5, 6, 7, 42); C3 possessify and atomic
    (4, 12, 50, 51) with the KEPT change; C4 DFA candidate tables (17, 22, 53, 54,
    56, 28, 29); C5 clskit, ctxnode, memfn deny map (24, 35, 43); C6 the alias
    drop (45), bit 55 and the freed-position block. A spec hunk per batch.
