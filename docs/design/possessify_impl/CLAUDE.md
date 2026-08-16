# docs/design/possessify_impl — the possessification lane's own measurements

[ENG-BREP]'s POSSESSIFICATION rung (docs/design/eng_brep_design.md §2, D47.1)
was designed in `eng_brep_design.md` and built by the implementation lane; this
directory holds what the IMPLEMENTATION measured, kept separate from
`eng_brep_measurements/` (the design lane's territory) so the two are never
confused for one another.

## Files

- **`census.sh`** — the corpus census, held against §7's predictions. A
  COMMITTED PRODUCER rather than a number in prose, and it sets `LC_ALL=C`
  explicitly, because R24 M-F1/M-F2 found every "distinct" figure in the
  original rung census to be an undercount with one shared cause: an
  uncommitted `sort -u` under a UTF-8 locale whose collation merges strings
  differing only in punctuation. That is close to a worst case for a corpus of
  regexes, and this lane reproduced the same bug in its own test script before
  the census caught it — 470 patterns reported where there are 793.

  It reports BOTH denominators on purpose. Under the DEFAULT engine choice a
  capture-free pattern routes to the DFA and never reaches the pass, so
  "possessified patterns / corpus" measures the ENGINE ROUTING as much as the
  rule; under `--engine=vm` every pattern reaches it and the rate is the
  analysis's own. It also reports SOURCE quantifiers (A_REP nodes, from the
  pass's own count) separately from EMITTED ones (rung marks), because a
  bounded repeat replicates its body and the emitter marks a rung per COPY —
  a census read off the emitted marks measures replication as much as it
  measures the rule.

- **`census.txt`** — an archived run (D35's stable-name convention: same name
  across re-runs, so a re-measurement is a diff).

## The numbers, and how they sit against §7

Read them from `census.txt`, not from here. The two comparisons worth knowing:
§7 predicted 613 of 756 corpus patterns capture-free and untouched, and the
measurement is the same shape on a corpus that has since grown; §2.6's
post-R24 census found 183 of 1,725 quantifiers possessifiable, and this lane
measures 226 of 1,784 source quantifiers. The denominators are close but not
identical populations — §2.6 counted quantifiers in the PATTERN TEXT with
python's parser and reported the 112 patterns python cannot parse rather than
dropping them, while this counts A_REP nodes in pcrec's own tree over the
patterns pcrec compiles. The rate is the comparable figure, not the raw
difference.

Maintenance: update this file when files are added/removed or their roles
change.
