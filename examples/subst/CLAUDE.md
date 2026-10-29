# examples/subst — compiled substitution, built and run

A tested example of `docs/spec/subst_api.md` (lane substb2): `Makefile`
(the rx, two templates and the support unit as build steps), `main.c` (the
§6¶9 setup wrapper verbatim, sizing, a by-name map, the §6 recipes),
`expected.txt` (its output), `README.md`. Checked by
`tests/examples/run_examples_tests.sh`. When the spec's §6¶9 wrapper text
changes, change `main.c`'s copy in the same commit.
