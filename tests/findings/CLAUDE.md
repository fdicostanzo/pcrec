# tests/findings/ — the [FINDINGS] checks (steps B3/B6, B1 and B2)

Two halves, both run by `make test-findings`, which is part of `make test`
(`TEST_SECTIONS`) since B1:

- **B1, the compiler side** (`run_findings_tests.sh`, lane `findb1`): the
  findings seam's DATA, STORE, STAMP and STRUCTURE, each held to a source the
  compiler does not share (`docs/design/findings/design.md` §8.1, §11.4,
  §11.6, §11.7, §13 B1).
- **B3/B6, the analyzer** (`run_analyzer_tests.py`, design §10): determinism,
  sharding/merging, the k=1 shard exception and the cpfreq lead-byte seam
  ([r2 A-1]/[r2 A-2]), `--check`, R26, R27a (analyzer output round-trips
  through `pcrec --list-analysis`), and the collision-free declaration
  split ([r2 M-B1]). Built at B3 (lane `findb3`) against the python
  PROTOTYPE, `scripts/pcrec_analyze.py`; REPOINTED at B6 (lane `findb6`) to
  `build/pcrec-analyze`, the C END STATE — same suite, same population,
  different binary, own bundle-text reader (never the deleted prototype's;
  `learnings.md` §3's "a reader and its check must not share a source").
  `run_analyzer_pinned.py` is the golden-output regression check design.md
  §11.8's own "python ≡ C (implement-then-replace)" row became once the
  prototype was deleted — see its own header and
  `docs/dev/lanes/findb6_report.md`.
- **B5, the shipped bundles and `cpfreq`** (`run_findings_tests.sh` §12,
  lane `findb5`): every shipped bundle whose provenance names a
  `third_party/` source is that directory's `generate.py --check` output
  (found by the name, never listed here); each shipped bundle's byte-rate
  answers carry `findings_ref.py`'s digest in the listing AND the stamp;
  on the ASCII samples `cpfreq` via `encode-utf8` is exactly the `freq` view
  (design §11.4); both derivations equal an independent Python derivation
  over code points of every UTF-8 length; a Latin-1-text sample comes out
  0xC3-heavy; `encode-latin1` reports its drop count and an all-dropped
  block is refused. Sabotage S325/S326.
- **B2, resolution and the invariant** (`run_findings_tests.sh` §6-§11, lane
  `findb2`): the stops, the chain, the CLI and library surfaces and the
  listings against fixtures written fresh per run (§6, design §11.5 #1-#22);
  the fire bundles' REACH (§7), the reader witnesses (§8), GIVE-UP identity
  on K65's repro under bundles that move the pick (§9), the sampled
  answer-identity slice under every adversarial bundle with its give-up
  transition population required ZERO (§10, through `tests/axes/run_axes.sh`,
  ~3 minutes; `FINDINGS_SKIP_SLICE=1` skips it for a quick local run), and
  the table contract on both listings (§11).

## Files

- `run_findings_tests.sh` — [B1] five sections: §1 VALUES (the embedded
  default normalizes to `default_ppm.tsv`, sums to 1,000,000 with every byte
  at or above the floor, and the §2.5 test vectors agree with
  `findings_ref.py`); §2 EMBED (the store's names are exactly
  `src/findings/*.rxt`, and each embedded text is its file byte for byte);
  §3 AGREEMENT (the pre-parsed table a compile reads equals a fresh library
  parse of the embedded text); §4 STAMP (`<PREFIX>_FINDINGS` and
  `rx_info.findings` on DFA and VM artifacts under both encodings, the
  digest against `findings_ref.py`'s independent FNV, the empty stamp when
  nothing asks, and the offset-k-only ask that proves the stamp is written
  after the last reader); §5 STRUCTURE (`structural_check.py`). PASS:/FAIL:
  lines and a `checks passed`/`checks failed` trailer. Mech arm `findings`.
- `findings_probe.c` — [B1] reads the seam's data out of the built
  `libpcrec.a` (store names and texts, the pre-parsed table, a fresh parse,
  the normalization, the default's digest) for the script to judge. [B5]
  `derive VIA`: the library's `cpfreq` derivation of stdin's code points;
  a `cpfreq` block's table line carries `U+HHHH:count` rows.
- `findings_ref.py` — [B1] the INDEPENDENT reference: §2.5's normalization
  and §7's digest written from the spec text, never from the C (learnings
  §3), plus the three §2.5 test vectors. [B2] `bundle-digest RXT [NAME]`:
  the digest a compile reading that bundle would stamp, its rows read by a
  regex rather than pcrec's parser — every §6 expectation's source. [B5]
  `bundle-digest RXT NAME KIND VIA` (a `cpfreq` block through a derivation)
  and `derive VIA`, design §2.4's two code-point derivations with Python's
  own UTF-8 codec as the encoder — never pcrec's.
- `structural_check.py` — [B1] the structural rules: S1 no function that
  calls a `pcrec_find_*` tests a rate pointer or the encoding (the four
  primitives exempt — their bodies ARE the NONE answers), with the known
  readers as its REACH population; S2 no rate-table identifier outside
  `src/core/findings.c`; S3 no table pointer in a `*Sel` struct. Its header
  says what a brace-depth scan cannot see. Sabotage S301 is its failing
  direction.
- `default_ppm.tsv` — [B1] the PINNED oracle for the default's values:
  RUNEST's own dump of the table B1 replaced
  (`docs/dev/findings_measure/data/byte_freq_ppm.tsv`, copied verbatim;
  decimal byte, ppm).
- `b1_mover_answers.py` — [B1] §13 (2)'s acceptance instrument, NOT in
  `make test` (it needs the pre-change compiler): for every artifact an A/B
  mover manifest names, the pre- and post-change artifacts linked into
  `tests/possessify/possdiff_driver.c` and compared on span, every capture
  slot and the give-up surface at every start position. [OPT-LITSCAN] S2a
  reuses it and added `CFLAGS` (the driver build's flags, e.g. ASan+UBSan
  with `-DDIFF_EXACT_SUBJECT`) and `PREFIXES=1` (every prefix of every own
  subject and of every literal word: subjects ending INSIDE a literal run).
- `manifests/` — [B1] the named mover manifests (design §11.3):
  `b1_byte_movers.txt` and `b1_utf8_movers.txt`, one row per moved
  ARTIFACT naming every stamp that moved on it.
  [B5] `ship_weblog_movers.txt` and `ship_log_movers.txt`: R35's census of
  each shipped bundle against the default, both encodings, written by
  `docs/dev/lanes/findb5_evidence/make_manifests.py` from
  `ship_census.py`'s output.
- `run_analyzer_tests.py` — [B3/B6] the analyzer's standing acceptance
  suite (design §11.8), run against `build/pcrec-analyze` (INFO lines are
  OWED items or discharged-elsewhere pointers, never a silent skip); its
  own `parse_bundle`/`shard_bounds`/`is_continuation_byte` are a SEPARATE,
  independently-written reader (never the analyzer's own `analyze/count.c`
  parser, and no longer the deleted python prototype's either).
- `run_analyzer_pinned.py` — [B6] the golden-output regression check
  `run_analyzer_agree.py`'s python-comparison role became once
  `scripts/pcrec_analyze.py` was deleted (implement-then-replace): a fixed
  case population re-run against committed golden `.rxt` files under
  `golden/` (regenerate with `--write`), plus R26 and the two shipped
  bundles' own `generate.py --check`.
- `golden/` — [B6] `run_analyzer_pinned.py`'s committed golden outputs.
- `res_fixtures.py` — [B2] writes the RESOLUTION fixture tree (§6) into a
  directory: two `-I` dirs, compiling files, parse-refusal cases, each
  bundle's counts distinct so an answer is identifiable by its digest.
  Written per run, never committed, so a fixture cannot drift from the
  script that reads it.
- `gen_adversarial.py` — [B2] `gen` builds `adversarial/` from a census
  (slow, by hand, output committed); `reach` (§7) and `witness` (§8) are the
  fast make-test checks.
- `adversarial/`, `witness/` — [B2] see their own CLAUDE.md.
- `fixtures/` — [B3] small committed inputs for the analyzer: `basic.txt`,
  `ascii_only.txt` / `utf8_mixed.txt` (the two collision-free observed rows of
  design §10.2), `invalid_utf8.bin` (R26), `shard1_first_byte.bin` ([r2 A-1]),
  `cpfreq_seam.txt` ([r2 A-2]).

Maintenance: update this file when files are added/removed or their
roles change.
