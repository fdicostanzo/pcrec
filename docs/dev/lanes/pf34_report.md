# pf34 — [PATFACTS] step 3.4, "E3: the k-set walk + pin" (lane report)

Lane pf34, 2026-09-27, opus. Branch `lane/pf34` off main `02db9c1b` (abi 41,
PATFACTS 3.0-3.2, B1 and S2a merged). Charter: `docs/design/patfacts/design.md`
§9's 3.4 row and "Why 3.4 is flagged" [r1 A2], §9.1, §3, §4.2, §4.5, R14.
**Not merged.**

## 1. Pre-lane deliverable: every reader of `run_pinned` / `run_o`, and its kind gate

Design §9 (3.4 row) requires this BEFORE any `src/` edit, because the step
widens the pin's domain: today `pcrec_prefix_ksets` (hence the pin) runs only
where `unanch_start`'s prefilter kind is not `DFA_PF_NONE`
(`src/gen/emit_dfa.c:3773-3774`), so `run_pinned` is 0 on every `DFA_PF_NONE`
artifact by accident of call order. A pure NFA+window pin is TRUE on some of
those. No byte moves only if every reader carries the kind gate.

Command (tree at `02db9c1b`), then each hit classified by reading it:

    grep -rn "run_pinned\|run_o\b" src cli lib tests docs/spec \
        --include=*.c --include=*.h --include=*.def --include=*.sh \
        --include=*.py --include=*.md | grep -v "^tests/mech"

plus `tests/mech/sabotages/` separately (one hit, S280) and pcrec-bench
read-only (no hit).

| site | what it is | reads the pin? | kind gate |
|---|---|---|---|
| `src/core/internal.h:1698-1704` | `PrefixKSets.run_pinned`/`run_o`, the declaration and its comment | no (declaration) | — |
| `src/opt/prefix_k.c:40-41, 386-399` | the header prose and THE WRITER (the pin loop) | no (writer) | — |
| `src/gen/emit_dfa.c:5343-5366` `pf_run_applies_common` | the run-pinned rows' predicate: reads `o->run_pinned` (`:5350`) and `o->run_o` (`:5351`) | **yes** | **EXPLICIT**: `:5348` `if (!s->forward \|\| u->kind == DFA_PF_NONE) return false;` precedes both reads |
| `src/gen/emit_dfa.c:5393-5434` `ofs_test_of`, run branch (`:5404-5416`) | reads `o->run_o` (`:5407`) and `o->run_pinned` (`:5416`, the drift assertion) | **yes** | **TRANSITIVE**: the branch is taken only when `pf->run_term`, and `pf` is at every caller (`:5897` `dfa_cand_scan`, `:6985` `dfa_form_derive`, `:8976` `dfa_prefilter_offsets`) the row `DFA_SELECT` chose (`dfa_pf_of` or the form's own `DFA_SELECT`). `dfa_select` (`:4533-4543`) returns a row only if its `applies` is true — there is no force override on axis B — and the only two `run_term` rows (`dfa_pfs[]`, `:5788-5791`) have `applies` = `pf_run_bounded_applies`/`pf_run_applies`, both of which are `pf_run_applies_common`, which gates |
| `src/gen/emit_dfa.c:5465-5476` `ofs_test_verifies_run` | reads `o->run_pinned` (`:5468`) and `o->run_o` (`:5472`) | **yes** | **TRANSITIVE**. Two callers: `:5361`, inside `pf_run_applies_common` AFTER its explicit gate; and `:5899` `dfa_cand_scan`, on a `t` filled by `ofs_test_of` returning true, which needs `pf->emit_block != NULL` — the four offset rows only, whose `applies` are `pf_ofs_applies_common` (`:5318-5322`, `u->kind != DFA_PF_NONE` explicit) or `pf_run_applies_common` (explicit) |
| `src/gen/emit_dfa.c:334, 5410, 5446-5447, 5545-5547, 5606` | `OfsTest.run_o` — a DIFFERENT field: the selected row's own copy of the offset, written only by `ofs_test_of`'s run branch (`:5410`) | reads `OfsTest`, not the pin | inherits `ofs_test_of`'s transitive gate |
| `src/gen/emit_dfa.c:7531` `anch_start` | `memset(&o->ofsk, 0, ...)` with `kind = DFA_PF_NONE` — the anchored match-here form | no (zeroes it) | its `kind` is `NONE`, so every pin reader above declines |
| `src/gen/CLAUDE.md:3216`, `src/opt/CLAUDE.md:321`, `tests/CLAUDE.md:549`, `tests/offsetskip/CLAUDE.md:3,53`, `tests/rxtsource/run_rxtsource_tests.sh:311,384` | prose / the `run_pinned.rxt` FILE name | no | — |
| `docs/spec/tuning.md:2414` | spec prose: `-fno-req-byte` leaves `u->ofsk.run_pinned` false | no (prose; updated by this step, D80) | — |
| `tests/mech/sabotages/S280_run_pin_bytes_ignored.sh` | plants into the WRITER | no | — |
| `docs/dev/optloop/s1/probe*_patch.py` (scratch probes) | compute their OWN pin from the walk, gated `nwalk` (i.e. only where the selection ran) | own pin | not an in-tree reader |

**Verdict: every reader carries the gate — two explicitly, the rest
transitively through `dfa_select`'s `applies`. No semantic mover is waiting
in a reader.** The transitive gates are exact today but they are a property
of three call chains, not of the read. So this step moves the gate to the
READ, where the design's §4.5 obligation says it belongs: the emitter reads
the pin through ONE helper that returns "unpinned" unless the prefilter kind
is not `DFA_PF_NONE`, and every reader above calls that helper. A future
reader in `emit_dfa.c` then cannot skip the gate. A reader in another file
(S2b, not built) still brings its own, as §4.5 states.
