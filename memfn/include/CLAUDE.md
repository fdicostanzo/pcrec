# memfn/include/ — the kit's one public header (planned; empty today)

Planned at R4a (integration.md §22): `memfn.h`, the ONLY file pcrec's
sources include from the kit. It carries `MF_SITE_ABI`, `MF_VOCAB`,
`MF_NS(name)` (→ `pcrec_mf_name` in-tree), the `mf_site`/`mf_pred`/
`mf_result`/`mf_art` shapes and the hook types (integration.md §8.2,
§8.3, §14.0), `mf_vocab_has`, `mf_options()` (the kit's published option registry,
which `--list-axes` prints as its `memfn` section) and `mf_opts_check()`
(validates the opaque `--memfn=` string). No ISA
names appear in it: pcrec must learn no architecture fact from the
header (C4).
