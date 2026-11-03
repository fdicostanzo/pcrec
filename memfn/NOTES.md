# memfn NOTES

History and lessons moved out of CLAUDE.md (orientation only).

## Deepest measured kit chain (stack), retired

Measured 2026-10-23 (gcc 15.2 x86_64 -O2, `tests/memfn/run_link_checks.sh`'s
`-fstack-usage` recipe): the deepest kit chain, `mf_form_hash` over both
canonical forms (which renders a site through `mf_emit`) and the since-deleted
`mf_set_terms` at K=4 on a painted stack, reached 13.7 KB; before R-28, 47.1 KB.
span_pick unit 1a deleted `mf_set_terms`, so the figure no longer describes any
chain in the tree; CLAUDE.md states the chain as UNMEASURED until re-measured.
