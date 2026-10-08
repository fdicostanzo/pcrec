# memfn/include/ — the kit's one public header

- **memfn.h** — the ONLY file pcrec's sources include from the kit (R4a,
  integration.md §8.2/§8.3/§14.0). It carries `MF_SITE_ABI` 5 (3: Q-G2-18, R4c; 4: M1b; 5: R4h prep,
  `mf_site.count_by_caller`, the caller-owned ADVANCE counter, Q-R4h-1 (a)), `MF_VOCAB`
  2 and `MF_NS(name)` (→ `pcrec_mf_name` in-tree, `mf_name` under
  `MF_STANDALONE`); the site description (`mf_site`, `mf_pred`, `mf_term`
  and the form/op/handoff/empty/need enums); the sink (`mf_sink`), the
  arena (`mf_arena`) and the hooks (`mf_hooks`); the result and the
  per-artifact state (`mf_result`, `mf_art`) with the entry points
  `mf_art_begin`/`mf_art_end`/`mf_art_error`, `mf_define`/`mf_use`/
  `mf_emit`/`mf_call`, `mf_flush_helpers`/`mf_includes`/`mf_stamps`, `mf_art_note_libc` (R4a′, the libc record's writer) and
  `mf_vocab_has`; the option registry's view (`mf_option`, `mf_options()`,
  which `--list-axes` prints as its `memfn` section, and `mf_opts_check()`,
  which validates the opaque `--memfn=` string); and K1's reference
  functions (`mf_ref_*`). Every entry-point name is a `#define` onto its
  `MF_NS` symbol, so callers write `mf_emit`. Where the design left a
  spelling open the header says CHOSEN, and
  `docs/dev/lanes/memfnskel_report.md` lists each choice. Where the kit
  session ruled one of G2's contract questions, the header says RULED
  Q-G2-n (integration.md §R4.7.0 is the table); Q-G2-5 (ADVANCE's range
  is `more`, its empty range NOP, no kit empty test) is marked RULED at the
  ADVANCE hooks (Q-R4h-2, recorded 2026-10-08), with the ADVANCE hooks'
  text-shape classes (`more` CONJ, `peek` POSTFIX, `step` EXPR_STMT).

No ISA names appear in it: pcrec must learn no architecture fact from the
header (C4). An `MF_SITE_ABI` change is a layout or meaning change of a
struct here; an `MF_VOCAB` change adds an op, handoff or term kind.
