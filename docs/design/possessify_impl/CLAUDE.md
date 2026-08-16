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

- **`throughput.sh`** / **`throughput.txt`** — two archived cells and NOT a
  bench floor: possessification removes machinery, so there is nothing here a
  floor could guard, and a floor would only pin a number the next ladder rung
  moves. Cell 1 is throughput inside both artifacts' declared limits; cell 2
  is the CAPABILITY BOUNDARY, which is the more interesting one and was found
  by cell 1 going wrong — run past the denied build's ceiling, the two builds
  returned different answers, which is not a divergence but the feature. They
  agree on every length the denied build declares it can handle and part at
  exactly its stamped `subject_ceiling`.

- **`make_corpus.py`** / **`gen_rxt.py`** — the PRODUCER of
  `tests/possessify/possessify.rxt`, committed for R24 M-F1/M-F2's reason: a
  corpus whose expectations were hand-written, or produced by a script nobody
  kept, cannot be re-derived when the oracles move. Running it reproduces that
  file BYTE-IDENTICALLY. `gen_rxt.py` asks both oracles per cell and carries
  its own instrument note — `pcre2_match` returns the number of ovector PAIRS
  it filled, not the pattern's group count, and reading only `rc` pairs made
  every trailing UNSET group vanish rather than read as unset, which showed up
  as seven phantom "oracle disagreements" on this generator's first run.

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
