# findb5src — [FINDINGS] B5, the SOURCING half (2026-09-27, lane
`findb5src`, sonnet, on `lane/findb5src` from main `65482b45`)

Charter: `docs/design/findings/design.md` §13's B5 row (sourcing part) +
§10 (the analyzer it feeds), D123-8 item 6, `[r2 A-4]`. Scope: nothing
under `src/`, `cli/`, `tests/`, no Makefile change. The BUILD half
(`src/findings/{weblog,log}.rxt`, `GEN_TABLES` wiring, `--check` against
the shipped files) is a later lane.

## 1. `weblog` — re-pinned (D123 addendum 6)

`third_party/elastic-examples-apache-logs-bc53b584/`:

| | |
|---|---|
| source | `elastic/examples`, `Common Data Formats/apache_logs/apache_logs` |
| pinned commit | `bc53b584c0f9f574d4373193334bf03541a54936` (the LAST commit to touch this file's path, 2017-11-06; found via `GET /repos/elastic/examples/commits?path=...`, not guessed) |
| licence | Apache License 2.0 (`GET /repos/elastic/examples/license`; `LICENSE` vendored unmodified at the pin) |
| vendored | `apache_logs.txt`, first 1,000,000 bytes of the pinned file — **byte-identical** to the pinned commit's own prefix and to the ALREADY-committed `docs/dev/findings_measure/corpora/web_request.txt` (cross-checked: the pinned commit's full-file SHA-256 `f15c31e9...` matches what `manifest.tsv`'s stale `master`-URL row already recorded, so re-pinning changed the CITATION, not the bytes) |
| SHA-256 (vendored, 1,000,000 B) | `43cfdc461a4ccecd3e93bbe0e30fd022a416e6fbe0ad2e613b1a13b85bee0e47` |
| SHA-256 (full pinned file, 2,370,789 B) | `f15c31e905f86c7b4b6ab44aee74d0a2086dce89f010187d983edea7ef0364ef` |

`PROVENANCE.md` states the trim rationale (matches `weblog`'s existing
measured-corpus size and `design.md` §8.3's own size estimates) and the
alternative considered (full 2.3 MB file — not larger than
`ucd-16.0.0/UnicodeData.txt`'s own 2.18 MB precedent, but declined to avoid
two differently-sized copies of "the `web_request` sample").

## 2. `log` — ONE sourcing attempt, then synthesized (D123-8 item 6)

~30 minutes, four checks beyond the design's own already-recorded loghub
finding: (a) confirmed loghub's `LICENSE` directly via the GitHub API
(research/academic only, SPDX `NOASSERTION`) rather than trusting the prior
citation; (b) `elastic/examples`' other `Common Data Formats/` entries
(`cef`, `nginx_logs`, `nginx_json_logs`, `twitter`) — all still web/HTTP-
adjacent, and reusing one repo for both `log` and `weblog` would weaken
their intended independence; (c) Apache Hadoop's own Apache-2.0 test-
resource tree — no committed sample log dump found; (d) a Zenodo search for
an independently CC-licensed loghub mirror — nothing usable in the time
box. **No licensable real source found.** Per the ruling, synthesized.

`third_party/synth-log-lines-v1/`:

- `gen_corpus.py` — deterministic generator, `SEED = 20260927`, no clock.
  Writes `synthetic_log_lines.txt`, 999,960 bytes, SHA-256
  `a91f736b7e118a4cb004e36dbd172fc27b3bbc44f098d84eece027a6352b0617`.
  Structural shape: `DATE TIME PID LEVEL component: message`
  (Hadoop-DataNode-log-like), invented component/message vocabulary, level
  mix 95.6% INFO / 4.3% WARN / 0.4% ERROR (measured on the committed file).
- **Fidelity informant, never a source**: this lane fetched loghub's
  HDFS_2k.log to `/tmp` to READ its structural ratios (level mix; rough
  share of lines with an IP:port, a hash-shaped token, a path) — never
  committed anywhere, deleted before this lane's first commit, no text or
  field value copied. `PROVENANCE.md` states this explicitly.
- `PROVENANCE.md` also records a **known fidelity gap, not hidden**:
  `requirements.md` line 102 (C4, from an earlier REAL-HDFS measurement)
  predicts `-` (0x2d) is "3.6× commoner" under log-measured frequencies,
  moving the bench's `loglines/iso-ts` pick. This synthetic corpus does
  NOT reproduce that: `ppm('-')` is 4,984 under `default.rxt` and 4,782
  under this corpus's own derived table — essentially flat. Recorded so a
  reader does not treat this corpus as a byte-frequency match to real
  HDFS data; it is a structural stand-in.

## 3. Analyzer runs

Both `generate.py` stubs invoke the real `scripts/pcrec_analyze.py`
(`--scan freq,cpfreq`) and write `generated_preview.rxt` beside themselves
— committed as a SCRATCH CHECK, deliberately **not**
`src/findings/{weblog,log}.rxt` (that retargeting, plus `--check` and
`GEN_TABLES` wiring, is B5's build half). Both run clean (`--check` passes
after a bare run) and both compile fully as ASCII input (`weblog`'s
1,000,000-byte sample is pure ASCII, confirmed; `log`'s synthetic corpus
likewise), so `freq` and `cpfreq` both emit and — per design.md §10.2's own
stated identity for ASCII input — carry numerically identical derived
values.

## 4. R35 census — byte-rate movers, computed WITHOUT a compile

`docs/dev/lanes/findb5src_evidence/byte_rate_movers.py` (output:
`byte_rate_movers_output.txt`, same directory). **What it is**: B2 (route
resolution — `-I`, config/CLI `analysis` naming) has not landed, so there
is no way today to `pcrec --analysis weblog` a real compile. This script is
a PROXY: it parses `src/findings/default.rxt`'s shipped `freq` block and
both `generated_preview.rxt` files, applies design.md §2.5's normalization
formula BY HAND (counts → ppm, verified: `sum(ppm) == 1,000,000` on all
three tables), then computes `argmin(ppm)` — `[OPT-FREQPICK]`'s own rule —
over every necessary-byte SET (size ≥ 2) in
`docs/dev/optloop/c2/reqpos_census.tsv`'s `set_hex` column (1,960 such
rows across the shipped corpus and the bench's `capability`/`syntax`/
`loglines`/`altwide` populations), comparing the pick under `default` vs.
under each candidate bundle.

**Result: NEITHER bundle's byte-rate census is empty.**

- `weblog`: **104 of 1,960** rows move the pick, including
  `bench/loglines/iso-ts` (`{2d,3a}`: default picks `-`, weblog picks `:`)
  — a direct, independent corroboration of `design.md`'s own predicted
  mover for this exact pattern (§13 B5's row: "log's predicted mover is
  C4's iso-ts").
- `log` (synthetic): **262 of 1,960** rows move the pick.

This refutes, ahead of any real measurement, the design's own stated
worry that shipping might have to "wait for B4" on an empty census (§13 B5:
"If `weblog`'s byte census is empty, it waits for B4") — under this proxy
it is not empty. **Caveat, stated plainly**: this is an arithmetic stand-in
for the real R35 census, which needs a compile through B2's route
resolution once it lands; it does not exercise the accessor's stamp,
give-up-identity, or the bigram/run-rarity kind at all (that is B4's own
customer). Handed to the build half as a starting point, not a substitute
for `make test-findings` + the real census.

## 5. What the build half needs

1. Retarget each `generate.py` (in both `third_party/` directories here)
   to write `src/findings/log.rxt` / `src/findings/weblog.rxt` instead of
   `generated_preview.rxt`; `weblog` should `include <log>` per
   `tests/rxtsource/fixtures/analysis_bundle_accept.rxtin`'s own worked
   example (this stub's analyzer call does not compose bundles — that is
   a `.rxt`-level edit on the analyzer's raw output, not an analyzer flag).
2. Add each `generate.py`'s `--check` mode against the real shipped file
   (today it checks against `generated_preview.rxt` only).
3. Add both derived files to the Makefile's `GEN_TABLES` list
   (`third_party/CLAUDE.md`'s "Adding a source" step 4; `[r2 A-6]`) so
   editing either corpus rebuilds the embed.
4. Run the REAL R35 census once B1/B2's accessor + route resolution can
   select a non-default analysis (this lane's §4 above is the proxy to
   start from).
5. §11.4's cpfreq checks (design.md) — both bundles are pure ASCII, so
   `cpfreq`'s `encode-utf8` view is identical to `freq`'s per §10.2's own
   stated identity; worth a real test vector confirming it, not asserted
   here.
6. `bigram` (B4) is out of this row's scope entirely; `weblog`'s real
   customer (C6, the WAF sign check) is a B4 dependency per design.md.

## Plan note

`docs/dev/plan.md`'s `[FINDINGS]` row: append that B5's SOURCING half is
delivered on `lane/findb5src` (this report), build half owed.
