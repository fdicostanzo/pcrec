# memfn/include/ — the kit's one public header

- **memfn.h** — the ONLY file pcrec's sources include from the kit (R4a,
  integration.md §8.2/§8.3/§14.0). It carries `MF_SITE_ABI` 9 (3: Q-G2-18, R4c; 4: M1b; 5: R4h prep,
  `mf_site.count_by_caller`, the caller-owned ADVANCE counter, Q-R4h-1 (a);
  6: M4 prep, R-7: a reads-below FIND's range bounded by its reads
  (Q-R7-1, at `MF_OP_FIND`), `MF_EMPTY_AT_N` (Q-R7-2) and `on_miss`'s
  LOOP_EXIT class (Q-R7-3), no layout moved; 7: M7 prep, R-8:
  `mf_site.fold_kind` and `mf_hooks.ref`/`reflen`/`fold`, each appended
  last; 8: M6 prep, R-10: the STRIDED ADVANCE, W REQUIRED SET terms at
  offsets 0..W-1 (Q-G2-9 relaxed on ADVANCE only, Q-R10-2), `MF_MAX_TERM`
  8 -> 32 (`mf_pred.term[]` grows, Q-R10-3), a strided site's kit-owned
  reads at `s[cursor + i]` (Q-R10-4) and ADVANCE's `span_hi` an ITERATION
  count (Q-R10-5); no MF_VOCAB move; 9: RQ-2 (D157, pcrec's lane rq2):
  `mf_pred.rank_n`/`rank_pos`/`rank_ppm`, a predicate's RUN-term positions
  ordered by pcrec's prior rate with each one's rate, and `MF_RANK_MAX`,
  appended last; no kit row reads them yet), `MF_VOCAB` 3 (M7 prep: `MF_OP_MISMATCH`, F8, the compare loop
  of the subject against a run-time reference span; `MF_H_ON_DIFF`, k
  written and then `on_miss`, which may read it; `MF_T_REF`, a term with
  no data; the `mf_fold` fact NONE/ASCII/UCP, Q-R8-4/5) and `MF_NS(name)` (→ `pcrec_mf_name` in-tree, `mf_name` under
  `MF_STANDALONE`); the site description (`mf_site`, `mf_pred`, `mf_term`
  and the form/op/handoff/empty/need enums); the sink (`mf_sink`), the
  arena (`mf_arena`) and the hooks (`mf_hooks`); the result and the
  per-artifact state (`mf_result`, `mf_art`) with the entry points
  `mf_art_begin`/`mf_art_end`/`mf_art_error`, `mf_define`/`mf_use`/
  `mf_emit`/`mf_call`, `mf_flush_helpers`/`mf_includes`/`mf_stamps`, `mf_art_note_libc` (R4a′, the libc record's writer) and
  `mf_vocab_has`; the option registry's view (`mf_option`, `mf_options()`,
  which `--list-axes` prints as its `memfn` section, and `mf_opts_check()`,
  which validates the opaque `--memfn=` string); and K1's reference
  functions (`mf_ref_*`; `mf_ref_mismatch`, F8, since M7 prep;
  `mf_ref_skip_blocks`, F5 strided, since M6 prep). Every entry-point name is a `#define` onto its
  `MF_NS` symbol, so callers write `mf_emit`. Where the design left a
  spelling open the header says CHOSEN, and
  `docs/dev/lanes/memfnskel_report.md` lists each choice. Where the kit
  session ruled one of G2's contract questions, the header says RULED
  Q-G2-n (integration.md §R4.7.0 is the table); Q-G2-5 (ADVANCE's range
  is `more`, its empty range NOP, no kit empty test) is marked RULED at the
  ADVANCE hooks (Q-R4h-2, recorded 2026-10-08), with the ADVANCE hooks'
  text-shape classes (`more` CONJ, `peek` POSTFIX, `step` EXPR_STMT); the
  `member` hook is OPAQUE there (pasted parenthesized), and the comment names
  R4h's frozen target render (tests/memfn/pins/r4h_target/, lane advtarget)
  and, since M6 prep, the strided render (tests/memfn/pins/m6_target/).

No ISA names appear in it: pcrec must learn no architecture fact from the
header (C4). An `MF_SITE_ABI` change is a layout or meaning change of a
struct here; an `MF_VOCAB` change adds an op, handoff or term kind.
