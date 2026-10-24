# examples/subst — compiled substitution

One pattern (`date`, a day/month/year date with named groups), two
templates (`iso`, `${y}-${m}-${d}`, by name; `num`, `$3.$2.$1`, by number)
and the support unit, each a build step of a plain Makefile, and a program
that substitutes with them. The contract is `docs/spec/subst_api.md`.

    make PCREC=/path/to/pcrec CC=gcc
    ./example

`main.c` shows, in order:

- the setup wrapper `sub_all` (§6¶9), copied verbatim: one call per
  substitution, returning the number of matches;
- sizing with `out == NULL`, `cap == 0` and a buffer that is too small
  (`PCREC_SUBST_NOSPACE` with the length that suffices);
- a template with names: with no map the setup refuses it
  (`PCREC_SUBST_MISSING_REF`), and `pcrec_subst_map_names` builds the map;
- the recipes the support unit does not write for you: per match to a
  stream (§6¶2), stopping after one match (§6¶3), in batches into a growing
  buffer (§6¶4), and a loop over the record's `next` with replacements
  only (§6¶5, §6¶6).

`expected.txt` is its output; `tests/examples/run_examples_tests.sh` builds a
scratch copy with `-Werror` and compares.
