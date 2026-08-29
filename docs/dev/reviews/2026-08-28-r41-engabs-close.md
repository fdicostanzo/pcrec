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
