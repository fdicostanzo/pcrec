# tests/doc_lint — checks for the index + details ruling files ([DOC-INDEX])

Design: docs/design/doc_index_format.md (§2.2, §2.4, §5.2) and its appendix.

## Files

- `run_doc_index.sh` — unit 1.0's checks (NOT in `make test` yet): `scripts/doc_census.py --selftest` (P20, gates a/b/c), `--check` (the committed owner table equals a fresh census of docs/dev/decisions.md), `scripts/doc_control.py --selftest` (appendix B's plants P1-P21 each RED by its clause, the correct toy GREEN), `--witnesses-table` (appendix B's named witnesses), and a witness sabotage (D89's rulings flipped to D94 must fail). Ends `run_doc_index: DONE rc=N`.
- `fixtures/doc_control/` — the control's toy: `toy_old.md` (old form: id-less, plain-line foreign, one-line, `## Dn ADDENDUM`, note, D98 wrap, a heading with its body directly under it), `toy_rulings.tsv`, and its hand-written CORRECT conversion `toy_index.md` + `toy_details.md`. The plants are mutations of the correct details (doc_control.py PLANTS); the toy's owner table is derived by doc_census.py at test time.

## Rules

- A change to the census rules or the rulings re-emits the table in the same change: `python3 -I scripts/doc_census.py --emit` (then `--check`).
- The control derives what a converted pair must hold from the OLD file and the owner table only, never from a converter's output; the converter (unit 1) is not written here.
