# memfn/include/ — the kit's one public header (planned; empty today)

Planned at R4a (integration.md §22): `memfn.h`, the ONLY file pcrec's
sources include from the kit. It carries `MF_SITE_ABI`, `MF_VOCAB`,
`MF_NS(name)` (→ `pcrec_mf_name` in-tree), the `mf_site`/`mf_pred`/
`mf_result`/`mf_art` shapes and the hook types (integration.md §8.2,
§8.3, §14.0), `mf_vocab_has`, and `mf_switches()` (the kit's published
deny switches, which become `--memfn-deny=NAME` axis rows). No ISA
names appear in it: pcrec must learn no architecture fact from the
header (C4).
