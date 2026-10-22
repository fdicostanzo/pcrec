# memfn/include/ — the kit's one public header

- **memfn.h** — the ONLY file pcrec's sources include from the kit (R4a,
  integration.md §8.2/§8.3/§14.0). It carries `MF_SITE_ABI` 19 (3: Q-G2-18, R4c; 4: M1b; 5: R4h prep,
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
  appended last; no kit row reads them yet; 10: R-13, R4e′ batch 1: `mf_sink.simd_open`/`simd_close`, appended last, renumbered from 9 when RQ-2 landed first; 11: R17-a, R-17's zero-mover seam (setfind.md §11.1, lane r17a): the WINDOW fields `mf_pred.window_stated`/`move_back`/`overshoot` (W0-W2, with the reserved `MF_MOVE_UNBOUNDED`/`MF_OVER_UNBOUNDED`; stated on every forward FIND and only there, the window today the candidate) and `mf_site.decl_point` (W4, the host capability: pcrec calls `mf_locals` once at a dominating point), each appended last; `MF_OP_FIND`'s result named the window's beginning (W3); `fn_ref`'s STMT reading, the storage stem (W5); `mf_result.reads_table`/`includes`; the entries `mf_locals` (the storage point, binding `s`/`n`) and `mf_defined` (what the define chose); 12: R17-b′ B1 (lane fdb1, r17b_prime.md rev 3 §3.1): `mf_site.body` (the call mode, `mf_body`: UNSTATED 0 / ONESHOT / PARAM, PARAM refused until B8) and `mf_hooks.start` (the activation's START hook, bound by `mf_locals` as `s`/`n` are), `mf_result.cls`, each appended last; the define-time QUERY `mf_ask` and its `mf_class` (exists, libc_free, proven0, includes, presence links); the measurement set's channel `mf_measures` on `mf_art_begin` with `mf_art_end`'s `consulted` (R-MS1/R-MS2); the DECLARED `mf_analysis` (E-1, read by no row before B3a); `mf_form_hash`/`mf_form_hash_text` (R-MS3); the finder table's listing `mf_finder_rows` into a caller-owned `mf_finder_listing` (R-MS4) and the pay rule's arithmetic `mf_finder_pay`; no pcrec byte moved; 13: R17-b′ B2 (lane fdb2, r17b_prime.md rev 3 §3.1 row B2): `mf_need` RE-NUMBERED with an UNSTATED zero (refused wherever read), `mf_site.site_kind` (the consumer kind, `mf_site_kind`, PR-3), `mf_hooks.moved` (the moved-candidate statement, PR-2) and `mf_result.row` (the finder row whose ROUTED decision chose the text), each appended last; `mf_class.proven_prev` (`MF_CLASS_V` 2); the finder rows D1, D1c, D1w routed; the arm-entry counter `mf_reach`/`mf_reach_table` (R-MS6, harness-only); no pcrec byte moved; 14: R-23 (lane r23): `mf_site.body` a STATED fact, its zero UNSTATED and refused by `site_check`, no layout move, no pcrec byte moved; 15: R-24 (lane r24): `mf_prov.bytes` and `mf_prov.fidelity` (`mf_prov_fidelity`, an UNSTATED zero), appended last, read by no kit row before B3a, no pcrec byte moved; 16: R17-b′ B3a (lane b3a, r17b_prime.md rev 3 §3.1 row B3a): PRESENCE STATED, PRES unrouted — `mf_span_class` (UNSTATED 0 / BOUNDED / CONTEXT / PRESENCE) with `MF_ORDER_UNKNOWN`, `mf_pred.span_class`/`omin`/`member_order` and `mf_site.head_max`/`npspan`/`pspans` (PR-5 one span per necessary-set member + the whole run; PR-6 omin 0; PR-7 member order), each appended last; `mf_class.npres` (`MF_CLASS_V` 3, `MF_MAX_PRES` 257); KW-8's ports `mf_pres_ports` over `mf_pres_proof`/`mf_pres_picks` (`MF_PRES_WINDOW` 8), read by pcrec's trace build only; no pcrec byte moved; 17: R17-b′ B3b (lane b3b): THE PRES ROWS ROUTED — `mf_pres_proof` moves above `mf_site` and gains `stated`, `mf_site.pres_proof` (the start search's proof P2 reads, stated wherever presence spans are), each appended last; `mf_class.pres[]` answered by `mf_ask`/`mf_defined`; `mf_define` refuses parts that are not the links' layout; `MF_USE_ENTRY` (MF_VOCAB 4); `mf_class.pres_row`/`pres_led`, each link's deciding rows, appended last (`MF_CLASS_V` 4, the b3brev fix round, inside 17 since 17 is unreleased); no pcrec byte moved; 18: R-26.1-R-26.5 (lane r26z1, kit_proof.md rev 2.1 §4, §7 Z1): span 0's class STATED (`mf_span_class` BOUNDED on a forward FIND's `pred`, CONTEXT on a context stop: both reservations lifted), `mf_pred.prefix_stated`/`exact_len`/`consumable_len` (`mf_prefix`) and `absent`/`consumable` (`mf_absent`, `mf_consumable`), `mf_site.read_floor` (`mf_read_floor`) and the context spans `mf_site.ctx`/`nctx`, each appended last, every one with an UNSTATED zero refused where read; `MF_SK_REPORT` (refused at selection while no row serves it); `mf_class.proven[]` (`MF_CLASS_V` 5) with proven0/proven_prev copied from it; the bounds `MF_MAX_SPAN_POS`, `MF_MAX_AHEAD`, `MF_MAX_CTX`, `MF_PROOF_LO`, `MF_MAX_FWD`; no pcrec byte moved; 19: B4′ (lane b4p, the LOCKDOWN under the walk ruling): `mf_finder_row` loses its `routed` and `locked` columns, no MF_VOCAB move, no pcrec byte moved; R-26.6, lane r26zk, moved no number: the harness-only entry `mf_preview` (one routing step previewed on an art, refused twice, after the first define or for a step the kit does not name; no options.def row) and the REPORT kind's text, no layout or field meaning moved), `MF_VOCAB` 4 (4: R17-b′ B3b's `MF_USE_ENTRY`, the presence verdict's use; 3, M7 prep: `MF_OP_MISMATCH`, F8, the compare loop
  of the subject against a run-time reference span; `MF_H_ON_DIFF`, k
  written and then `on_miss`, which may read it; `MF_T_REF`, a term with
  no data; the `mf_fold` fact NONE/ASCII/UCP, Q-R8-4/5) and `MF_NS(name)` (→ `pcrec_mf_name` in-tree, `mf_name` under
  `MF_STANDALONE`); the site description (`mf_site`, `mf_pred`, `mf_term`
  and the form/op/handoff/empty/need enums); the sink (`mf_sink`), the
  arena (`mf_arena`) and the hooks (`mf_hooks`); the result and the
  per-artifact state (`mf_result`, `mf_art`) with the entry points
  `mf_art_begin`/`mf_art_end`/`mf_art_error`, `mf_define`/`mf_use`/
  `mf_emit`/`mf_call`, `mf_locals`/`mf_defined` (MF_SITE_ABI 11), `mf_flush_helpers`/`mf_includes`/`mf_stamps`, `mf_art_note_libc` (R4a′, the libc record's writer) and
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

D172 S2 commit 1 (lane wsc1) appended, with NO `MF_SITE_ABI` number move (the number moves at commit 6, when the old fields retire): THE WINDOW SITE's facts `mf_wspan` (start, len, verify `mf_verify`, core `mf_core` + core_lo/core_len, per-position sets and table offers), `mf_walt` (entry `mf_entry`, spans), `mf_site.nalt`/`alts`/`wfloor` (`mf_wfloor`), the bounds `MF_WSPAN_POS`, `MF_WMAX_SPAN`, `MF_WMAX_ALT`, `MF_WREACH`, `MF_WPLAN_MAX`, the phase-1 reply `mf_wreply` and its entry `mf_wdecide`, and the preview step `"window-family"`; all read only on an art previewing it.

No ISA names appear in it: pcrec must learn no architecture fact from the
header (C4). An `MF_SITE_ABI` change is a layout or meaning change of a
struct here; an `MF_VOCAB` change adds an op, handoff or term kind.
