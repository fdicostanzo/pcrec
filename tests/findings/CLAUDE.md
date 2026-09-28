# tests/findings/ — the [FINDINGS] checks (steps B3, B1 and B2)

Two halves, both run by `make test-findings`, which is part of `make test`
(`TEST_SECTIONS`) since B1:

- **B1, the compiler side** (`run_findings_tests.sh`, lane `findb1`): the
  findings seam's DATA, STORE, STAMP and STRUCTURE, each held to a source the
  compiler does not share (`docs/design/findings/design.md` §8.1, §11.4,
  §11.6, §11.7, §13 B1).
- **B3, the analyzer prototype** (`run_analyzer_tests.py`, lane `findb3`,
  `scripts/pcrec_analyze.py`, design §10): determinism, sharding/merging, the
  k=1 shard exception and the cpfreq lead-byte seam ([r2 A-1]/[r2 A-2]),
  `--check`, R26, and the collision-free declaration split ([r2 M-B1]).
  R27a (analyzer output round-trips through `--list-analysis`) is
  discharged by B2 (§6 #21), the python≡C item is B6's
  (`docs/dev/lanes/findb3_report.md`).
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
  the normalization, the default's digest) for the script to judge.
- `findings_ref.py` — [B1] the INDEPENDENT reference: §2.5's normalization
  and §7's digest written from the spec text, never from the C (learnings
  §3), plus the three §2.5 test vectors. [B2] `bundle-digest RXT [NAME]`:
  the digest a compile reading that bundle would stamp, its rows read by a
  regex rather than pcrec's parser — every §6 expectation's source.
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
- `run_analyzer_tests.py` — [B3] the analyzer's checks (INFO lines are OWED
  items, never a silent skip).
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
