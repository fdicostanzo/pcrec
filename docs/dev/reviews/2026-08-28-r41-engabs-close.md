# r41 — D6 close panel on the DELIVERED [ENG-ABS] second mechanism (lane/engabs 4a44828: anchored match-here via the unwrapped forward DFA), before merge

Three read-only critics, no make: critic-sem (opus; accept discipline
vs the old form, the VM and libpcre2 with its own alphabet; assertions
at pos > 0; empty matches; the overflow fallback — pending),
critic-checks (sonnet; obligations + what the checks check — REPORTED),
critic-meas (sonnet; reproduce §7/§8 — pending). Opened 2026-08-28
~23:5x EDT, forty-fourth session. The lane is DONE (delivered; tree
clean); merge waits on the panel; the union battery follows the merge.

## critic-checks — findings and triage

| # | severity | finding | disposition |
|---|---|---|---|
| C1 | HOLDS | abi 9→10 at all four D76 sites (`emit_dfa.c:1310`; `run_codegen_tests.sh:2707` ABI_EXPECT=10; `match_api.md:1570`; FILEPIN → 14d1feb = the lane's last src commit); no fifth abi-9 pin anywhere | none |
| C2 | HOLDS | D80 hunks for every caller-observable change: tuning.md §2.15 + §3.1's stamp row, limits.md's second narrower exception, cli.md:224's axis list (r40's miss NOT repeated), match_api.md §3.6; `--help` silent on the flag (D47.3) | none |
| C3 | HOLDS (documented exception) | `RX_DFA_MATCH`/`match_form` non-NULL only on `RX_ENGINE "dfa"` artifacts, NULL on VM incl. hybrids — differs from the scan-fact precedent, and match_api.md argues why (it describes the `_match` ENTRY, not a scan); verified live on 3 compiled patterns | none |
| C4 | HOLDS | `--list-axes` 45 rows / 18 axes reproduced; registry 59→64 DERIVED (`grep -c '^PASS: '`); no hard-coded "4-15" range remains ("4-31, DERIVED, no upper bound"); bit 17 in the dump | none |
| C5 | HOLDS | form-census floors 780/150 derived via the same `floor_check` mechanism as every axis; red on a regression to 0 | none |
| C6 | NIT | `tests/anchored/CLAUDE.md:62-63` says floor 900 / 1009 measured; the shipped `run_anchored_diff.sh:201-202` pins 1150 / 1213 measured — doc drifted from a WIP number; the check is stricter than the doc claims | FIX BEFORE MERGE (one-line doc edit; the manager may land it) |
| C7 | HOLDS (strong) | S189 (`prune=false` on the anchored machine → longest-match accept) is DETECTED ONLY by `tests/anchored/run_anchored_diff.sh`; `alternation.rxt` 26/0 and the structural check 14/0 stay green on the planted tree — detected by the ARTIFACT'S ANSWER, not emitted text; wired into the matrix with "corpus:0fail is expected" | none |
| C8 | HOLDS | `make test-axes`' deny arm is trivially green forever (RXTDUMP drives `_search` only) and the note SAYS so (§9.1/§10.5); the differential's ground truth is the denied build's `_match`, itself derived from the oracle-verified `_search` — a stated, non-circular chain | none; the anchored route for [CHK-2]'s sweep is a [CHK-2] question |
| C9 | HOLDS | the size-log diff is the lane's own quiet re-measurement (7246c72, 14d1feb); plan.md/journal/decisions untouched by the lane | none |
| C10 | GAP (merge readiness) | lane branched at 017bf3d; main advanced 5 docs-only commits (D84 + addenda, r40, journal, the dd13 paper) — true divergence; the critic expected a size-log conflict | manager: main has NOT touched `artifact_size_log.tsv` since 017bf3d (verified: 0 commits), so the lane's log supersedes cleanly; docs-only divergence merges without conflict — `git merge` ALONE, read its result (CLAUDE.md's merge row) |

## critic-meas — findings and triage

Independent harness (the lane's `adriver.c` is not committed; the critic
wrote its own to the same calibration / median-of-5 discipline),
taskset -c 3, load1 0.5-3.6, both compilers built from source.

| # | severity | finding | disposition |
|---|---|---|---|
| M1 | HOLDS (thin) | Q1 matching subjects: first 5-trial run 1.062× (over the ≤ 1.046× target), 10-trial median **1.036×** (lane 1.031×) — MET, but the margin is inside the ±3 % trial-to-trial noise; a single 5-trial run can read as a miss | note §7.1 states the noise band; anyone re-running uses ≥ 10 trials |
| M2 | HOLDS | Q2 short valid emails **0.489×** (lane 0.482×) | none |
| M3 | HOLDS | ALL 1.167-1.186× (lane 1.161), off/vm 2.19× (lane 2.13, +2.7 %), NON-MATCHING 1.55-1.57× (lane 1.550); the critic's own regime filter had a bug first pass (n=47/38 vs 40/45), self-caught | none |
| M4 | HOLDS | failing probe: on 5.79-5.86 ns flat at 1 KB…1 MB; off 1,919 → 1,996,247 ns (x) / 395 → 396,650 (\n); ratio 342,548× (lane 363,305×) | none |
| M5 | NIT (refines) | the flat ~5.8 ns is ~62 % harness call overhead (empty subject 3.6 ns), ~38 % pattern work — O(1) HOLDS, "flat 5.5 ns" overstates the pattern-specific part | one clause in §7 |
| M6 | HOLDS (n=1 per cell) | five other shapes (uuid, iso-ts, 6-way alt, ipv4, `\d{4}-\d{2}-\d{2}$`), match + fail each: abi 10 faster in all 10 cells, 1.47×-13.4×; no slower shape found | suggestive, not swept; recorded |
| M7 | HOLDS exactly | corpus size totals 64,219,443 → 67,362,750 (+4.89 %), 2,875 rows, 0 vanished/new | none |
| M8 | HOLDS | DFA n=1,185: min +111 / median +2,605 / max +44,031 / ratio median 1.175 / max 1.450 exact; p99 6,528 vs the lane's 6,743 (percentile convention) | none |
| M9 | answered | the +44,031 max is `tests/base/d27_large_counts.rxt:43` = `a{1,2000}` (largest-state DFA); not decomposed table-vs-scaffold | none |
| M10 | HOLDS exactly | D81 difference set on 40 sampled patterns: exactly 11 distinct lines, all stamp/comment/struct-init, nothing in a function body (a first pass without same-basename control inflated it via `#include` noise — self-caught) | none |
| M11 | GAP (new information, in the row's favour) | `.o` delta is 1.7-11 % of the SOURCE delta on 8 unwrapped-selecting artifacts (median ~2-5 %), far under the census's general ~17 % `.o`/source ratio — the anchored table is verbose decimal C that compresses in the binary; the shipped-binary cost of the row is much smaller than +4.89 % source suggests; 2 of 10 sampled (ENG_ATTEMPT / "empty") show zero delta both sides, per §5.1/§6 | ACCEPTED → one paragraph in §8 with the numbers (manager or a follow-up, not a merge blocker) |

**Bottom line:** no MET/NOT-MET flip, no wrong number; every headline
reproduced within noise on independent tooling.
