# memfn NOTES

History and lessons moved out of CLAUDE.md (orientation only).

## Deepest measured kit chain (stack), retired

Measured 2026-10-23 (gcc 15.2 x86_64 -O2, `tests/memfn/run_link_checks.sh`'s
`-fstack-usage` recipe): the deepest kit chain, `mf_form_hash` over both
canonical forms (which renders a site through `mf_emit`) and the since-deleted
`mf_set_terms` at K=4 on a painted stack, reached 13.7 KB; before R-28, 47.1 KB.
span_pick unit 1a deleted `mf_set_terms`, so the figure no longer describes any
chain in the tree; CLAUDE.md states the chain as UNMEASURED until re-measured.

## memfn/include/CLAUDE.md: MF_SITE_ABI 20-22 history (moved verbatim, lane b30b, 2026-11-12)

22: span_pick.md rev 5.2 unit 1g, lane sp1g: provenance leaves the seam, `mf_akind` is {tag, version, present, digest, payload}; `mf_prov` (source, bundle, bytes, fidelity), `mf_prov_source` and `mf_prov_fidelity` deleted, the digest moved to `mf_akind.digest`; read by no kit row, a layout move, no pcrec byte moved; 21: span_pick.md rev 5.2 unit 1f, lane sp1f: the finder rows R8, R1, R2 leave the listing (`MF_CLASS_V` 7) with their denies `fd-r8`/`fd-ndisp`, and the pay rule's entry `mf_finder_pay`, `mf_pay_operands` and `MF_PAY_MAXPT` are deleted; the listing's `unpaid` column stays, `-` on every row; no pcrec byte moved; 20: D172 S2 commit 6, lanes wsc5 and wsc6: a site stating alternatives is the window family's on every art, `mf_wdecide` on any art, the `"window-family"` preview step retired, finder row D2 out of the listing; THE OLD FIELDS RETIRE (wsc6, the kit manager's R1): W0-W2 (`window_stated`/`move_back`/`overshoot`, `MF_MOVE_UNBOUNDED`/`MF_OVER_UNBOUNDED`), the prefix facts (`prefix_stated`/`exact_len`/`consumable_len`, `mf_prefix`), `absent`/`consumable` (`mf_absent`, `mf_consumable`), `mf_site.consumer` (`mf_consumer`), `read_floor` (`mf_read_floor`) and `ctx`/`nctx` (`MF_MAX_CTX`) DELETED with their site_check rules and gate fields, a layout move; `plan_hint`, `plan_pos`, `rank_*`, `end_back`, `span_class` BOUNDED/CONTEXT and `need` STAY as THE RENDERER INTERFACE, written only by the family's translation (window.c `translate`) and by G2, never by a host: a window site (or a pre-check FUNC part) stating any of them is REFUSED; no MF_VOCAB or MF_CLASS_V move

## memfn/src: E-find (lane partd2, 2026-11-13)

Moved out of memfn/src/CLAUDE.md to keep it under its size limit (memfn/src/ holds no notes file: C16 holds
every file there to an SPDX line and a PROVENANCE.md row).


E-find (D172 S3, deny `window-search`) is the window family's own find-then-verify text on a STMT/ASSIGN site with a stop (B: T-FIND's pick, `fd_find`, by its renderer row (find, resume, file-scope text): B-fn the offset-skip function for PAIR on a plan that is its predicate (fn-pair, SIMD rows over it), B-pair, B-memchr, B-walk (resume c + 1), B-hors (D-hors, deny `window-skip`: probe and shift table); C: C-run's compares through runcmp; the floor and E-find share the frame, prologue and test, C9).
