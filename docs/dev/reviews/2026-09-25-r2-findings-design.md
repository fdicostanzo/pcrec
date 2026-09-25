# r2 — [FINDINGS] D6 panel on the design note (docs/design/findings/design.md @ lane/findesign)

2026-09-25. Three read-only critics with distinct lenses: **fcrit-model**
(data model, resolution, CLI/library/`.rxt` surfaces), **fcrit-sound**
(answer soundness, checks, stamps, abi), **fcrit-analyzer** (the analyzer,
the embedded store build, sourcing). None ran `make`. Frank ruled the
panel's asks the same session (D123 addendum 8). Dispositions were applied
by lane `findrev` (from main `5a2094e7`) as ONE disposition table,
`design.md` §R, plus in-place edits each marked `[r2 <id>]`.

**Source of this record.** The three critic reports exist only in the
prior session's transcript. This lane worked from the manager's relayed
essentials plus D123 addendum 8. Where the relay carried a finding's
content, it is dispositioned below. Where it carried only a number or a
word, the row says so and records what was (or was not) done. Nothing here
claims a critic said more than the relay shows.

"Applied in" names the `design.md` section(s). The commits are on
`lane/findrev`: `6481ba8e` (§R table, §0, §1), `a1921e9b` (§2–§4),
`52153909` (§5–§7), `2fdca3c6` (§8–§9), `ba920dfa` (§10), `12b089a1` and
`82f46633` (§11), `83f515cd` (§12–§13), `e76070a5` (§14–§16), `05bffa6e`
(§8.3, §17, both CLAUDE.md files).

## fcrit-model

| id | sev | finding | disposition | applied in |
|---|---|---|---|---|
| B1 | blocking | Two blocks of one bundle could both serve one (query, encoding), so which one answered depended on kind order. The analyzer's own defaults collided (`freq` and `cpfreq` both `when byte,utf8`). §7 put kind/via in the digest tag while also claiming `freq`/`cpfreq` give one digest | ACCEPT. (1) At most one block per (query, enc) per bundle: a PARSE error naming both lines. (2) Analyzer defaults split the encodings when both kinds are scanned (`freq` → `byte`, `cpfreq` → `utf8`); on decodable input the two derived tables are identical, so the split picks which block is shown answering, not the answer. (3) Digest settled on one rule, "the bytes whose change could change what the reader sees": `byte-rate` digests the derived table only (no kind, no via); `run-rarity` digests `via` + rows | §2.4, §3.1, §7, §10.2, §11.5 #21 |
| B2 | blocking | `--analysis` REPLACING a config's `analysis` broke D93 (file wins; `--engine` the single exception) | RULED, D123-8 item 2: FILL-ONLY. A conflict keeps the file's value, with a note in `--tune`'s shape. An experiment is a config VARIANT in the file (`config waf-prose from waf` / `analysis prose`). `--analysis` in a config's `pcrec` line is refused. Supersedes D123 item 2's "CLI replaces" clause | §1 row 11, §3.1, §3.2, §5.1, §9, §11.2 F-8, §11.5 #12, §14 (`cli.md`), §15 R10 |
| B3 | blocking | S1 was the whole `include "path"` closure. That is a second resolution walk over files the compile opened for another reason | RULED, D123-8 item 3: S1 = the compiling FILE only. An `analysis` block inside an `include "path"` fragment is refused at parse (this revision's own call; see OPEN 3). Boonies row `[FINDINGS-S1-REVISIT]` | §1 row 8, §2.1, §4.1, §4.2, §9, §17 |
| S4 | should-fix | A `-I` dir that serves `lib` may hold a `<name>.rxt` that is a library, not a bundle. A hard error there punished an unrelated file | RULED, D123-8 item 5: FALL THROUGH to the next stop with a note | §4.1, §4.3, §9, §11.5 #7 |
| S5 | should-fix | One S2 file carrying several bundles | RULED, D123-8 item 5: ONE bundle per `-I` file. More than one is a hard error | §4.1, §9, §11.5 #7 |
| S6 | should-fix | Name → file on a case-insensitive filesystem opens `Log.rxt` for `log` | RULED, D123-8 item 5: lowercase-only names, matched by EXACT directory-entry name. The probe reads the directory for an equality test only, never to discover bundles | §3.1, §4.1, §9, §11.5 #7 |
| S7 | should-fix | "A one-line un-refusal" of `-I` understated the change: it touches every query mode, the mode tables and the lib-dirs lifecycle | ACCEPT. Enumerated in §0.2 and carried as B2 scope | §0.2, §4.2, §13 B2 |
| S8 | should-fix | There was no per-TARGET resolution view | ACCEPT. `--list-analysis FILE` emits `#section targets` (target, configs, analysis, `named_by` = config / cli-fill / none, config line) and a per-target `#section resolution`. Spelling is the manager's under `[DD-13b]` | §5.2, §11.5 #20, §13 B2 |
| S9 | should-fix | One include vs several; selective include's scope | RULED, D123-8 item 4: one `include` per bundle now. Several only later, together with `kinds=` on every line. Notes and the scope question ("one link or the whole onward chain?") are in `[FINDINGS-SELINC]` | §1 row 2, §3.3, §17 |
| S10 | should-fix | The table-contract producers had no enrolment or escaping stated | ACCEPT. Both join `table_contract.md`'s Scope table and its conformance check at birth. Free-text columns go through the contract's escaping | §5.2, §13 B2, §14 |
| S11 | should-fix | Five spec hunks were missing from §14 | ACCEPT. All five are named with locations: `cli.md` file-wins section (`--analysis` as a non-exception, the `pcrec`-line refusal) and `-I` on query modes; `match_api.md`'s `REQ_BYTE` prior sentence (found at `:~2755` on this main, not `~2721`); `rxt_format.md`'s `--list-source` rows for `analysis`/`include`, the `analysis` config line (`:67-69`, `:880`), and the stale `lib` row (`:54`, "CONTENTS are not read") | §14 |
| S12 | should-fix | The store and `analysis_source` are BUFFERS, while the `.rxt` reader opens files | ACCEPT. A NO-FILESYSTEM parse mode: `include "…"` / `lib "…"` in a buffer is refused by name. Owed at B1 | §5.3, §8.2, §9, §11.5 #18, §13 B1 |
| 13–19 | notes | seven notes | **NOT DISPOSITIONED.** The relay carried only their numbers. This lane cannot reconstruct their content from the tree and does not claim to have applied them. The manager should re-supply them from the transcript or close them as lost | — |

## fcrit-sound

| id | sev | finding | disposition | applied in |
|---|---|---|---|---|
| F1 | blocking | **K65** (filed from this finding, `known_issues.md`): on a VM route with no DFA in front, the necessary-byte PICK decides whether a call gives up or answers NOMATCH, so every user bundle would be a give-up switch. "Answers identical" as checked counts a one-sided give-up as budget-bound | ACCEPT. The invariant becomes answers identical AND no give-up TRANSITION, counted as its own population (GIVEUP1). K65's witness is a REACH sabotage row (F-12). B2 now depends on K65's fix (shape (a), D123-8 item 1) and on GIVEUP1 being on main | §6.2a, §11 head, §11.1, §11.2 F-12, §13 B2, §15 R34 |
| F2 | blocking | C3 (`req_byte_dominated_by`, G1) lets a rate decide whether the pre-check is emitted, and no soundness argument covered it | ACCEPT. §6.2a gives the argument. G1 elides only where `dfa_cand_scan_byte ≥ 0`, which requires a DFA scan (a DFA route or the hybrid's inlined prefilter). There, either the machine is linear, or every necessary byte is prefilter-necessary (r1 S1-2's argument), so for EVERY rate table the elided and emitted forms answer and give up identically. Sabotage F-13 drops the `p < 0` guard | §6.2a, §11.2 F-13 |
| F3 | should-fix | One `fire-all` bundle cannot show that EACH reader moved | ACCEPT. One `fire-<reader>` bundle per reader (C1, C2a, C2b, C3, C4; C6 at B4), each with a REACH count. A zero is red | §11.1, §13 B2 |
| F5 | should-fix | An exact-rational `L(x)` reference disagrees with the squaring algorithm in the last bit by design | ACCEPT. `L(x)` is DEFINED by its algorithm. The reference is an independent python re-implementation of that algorithm, written from the spec. The exact-rational value is reported as information only | §2.6, §11.4, §13 B4 |
| F6 | should-fix | Empty sets and ties were undefined | ACCEPT. An empty set in a run query is an asserted caller error; `set_mass(∅) = 0`. With add-one smoothing no other term reaches `L(0)`. Ties are never broken inside the accessor: each reader applies its own pre-findings order | §2.6, §6.1 |
| F8 | should-fix | The `utf8` mover manifest was per READER. C4's movement changes the scan byte G1 compares, so C3 moves on the same artifacts | ACCEPT. The manifest is per ARTIFACT and names every stamp that moved | §11.3, §12, §13 B1, §15 R37 |
| F9 | should-fix | "Program region: 0 movers" named no gate | ACCEPT. The gate is a whole-file diff minus the NAMED lines (abi stamp, `<P>_FINDINGS`, `rx_info.findings`). The list lives in the gate script, so a fourth moving line is red | §7, §11.3, §13 B1 |
| F10 | should-fix | "Consumed" = "asked", and asking can depend on deny flags or reader order, so the stamp would differ across axis builds | ACCEPT. (1) Readers ask at their ANALYSIS, deny-independently. (2) The stamp is rendered after the last reader, from the final attempt's record. (3) FALLBACK only where (1) cannot hold for some reader: the axis and identity gates exempt exactly the two stamp lines, by name. Stamping every query regardless of asking was rejected because it contradicts D123-2's "consumed values only" | §6.4, §13 B1 |
| F11 | should-fix | "abi 32 → 33" is stale. Main is at 33 (K64, `emit_dfa.c:51`) and K65's fix is expected to take the next number | ACCEPT. The text now reads "the next abi number at landing", with no literal, in `design.md`, `docs/design/findings/CLAUDE.md` and `docs/design/CLAUDE.md`. The latter had no literal abi text; its status line was updated | §1 row 14, §7, §13 B1, §14, §15 R21; both CLAUDE.md |
| F13 | should-fix | "gates" (the relay carried one word) | APPLIED AS: every B-step's acceptance now names the suites whose `*** [test-X] Error` lines are its verdict (per the CLAUDE.md situation index). If the critic meant something more specific, it is not captured here | §13 |
| F4, F7, F12 | — | not in the relayed essentials | **NOT DISPOSITIONED** (content unknown to this lane) | — |

## fcrit-analyzer

| id | sev | finding | disposition | applied in |
|---|---|---|---|---|
| A1 | should-fix | Shard 1 has no preceding byte. A uniform "the first byte read is the overlap byte" rule drops byte 0 from `freq` | ACCEPT. A k = 1 exception, plus a fixture: a byte that occurs only at offset 0 must count exactly 1 for every N | §10.4, §11.8, §13 B3 |
| A2 | should-fix | The `cpfreq` seam needs an exact formula that both neighbours compute alone | ACCEPT. Shard K owns the code points whose LEAD byte is in `[start_K, end_K)`: it skips ≤ 3 leading continuation bytes and reads ≤ 3 past its end. More than 3 in a row is invalid UTF-8, which `cpfreq` refuses anyway. Fixture: 2-, 3- and 4-byte code points straddling every cut offset | §10.4, §11.8, §13 B3 |
| A3 | should-fix | Nothing checked that the embedded text equals its committed source | ACCEPT. A per-name digest comparison of the embedded text (read back through the library) against `src/findings/<name>.rxt` | §8.1, §8.2, §11.5 #19 |
| A4 | should-fix | `log` sourcing | RULED, D123-8 item 6: one sourcing-lane attempt, then a labelled `fidelity synthesized` corpus | §0.9, §8.3, §13 B5, §16 |
| A5 | should-fix | `generate.py --check` on a manifest-only source has nothing to recount. It must fail closed or say so, never skip silently | ACCEPT. `make test` prints a named, counted SKIP (PC-3's "skips loudly" shape). An opt-in fetch target re-fetches by url/sha256 and fails CLOSED | §8.1, §11.8, §13 B5 |
| A6 | should-fix | B5 never wired the generator into `GEN_TABLES` | ACCEPT. Each derived `src/findings/<name>.rxt` joins `GEN_TABLES`, and the embed `.inc` becomes a prerequisite of `findings.c`'s object. This avoids the recompile-class defect the Makefile itself records at `:140-147` | §13 B5 |
| A7 | should-fix | The bundle NAME in the stamp is a privacy surface | ACCEPT (documented in §7, §10.5 and the `findings.md` / `match_api.md` hunks). Whether to offer a redaction is OPEN 2 | §7, §10.5, §14, §17 |
| A8 | note | `od` output differs between BSD and GNU | ACCEPT. Pinned to `LC_ALL=C od -An -v -tx1`; only the hex pairs are consumed | §8.1 |

## Found by the revision itself

- **C2b: K65's shape on the RUN window.** While writing §6.2a's per-reader
  argument (asked for by F2), the revision found a second case.
  `rn_window_start` chooses WHICH 8-byte window of a longer necessary run
  is emitted, and it will read `byte-rate`. The absence of any window
  proves NOMATCH, so the ANSWER does not depend on the choice. But on a VM
  route with no DFA in front, only the emitted window is checked, so the
  choice can switch a GIVE-UP exactly as C1's pick did. This is argued from
  K65's mechanism, **not measured**. It is recorded as a §6.2a row with no
  coverage, as B2's third dependency, and as OPEN 1.
- `rn_scan_index` (C2a) is argued safe: the whole emitted run is compared
  at each hit, whichever member is scanned.

## OPEN FOR FRANK

1. **C2b: the run-window choice on no-DFA-front VM routes (§6.2a).** Two
   options. (a) Extend K65's ruled shape (a) to runs: pre-check EVERY
   necessary window on those routes, which makes the choice pick- and
   findings-independent. (b) Take the window findings-blind there (the
   leftmost window). **Rec: (a), inside the owed K65 fix lane**. It is the
   same fix on the run form, one general mechanism, and it lands before
   B2 either way.
2. **A stamp redaction mode (A7).** D123-2 rules "the source name per
   consumed kind" into the stamp, so a user bundle's name ships in every
   binary built under it. Should pcrec offer a digest-only spelling?
   **Rec: no, not now.** Document the disclosure (done), advise neutral
   names, and revisit on a user ask. Redaction would weaken R18's "which
   bundle answered" at exactly the moment a user most needs it.
3. **Confirm: an `analysis` block inside an `include "path"` fragment is a
   parse error (M-B3's corollary).** D123-8 item 3 makes such a block
   unreachable. The alternatives are to accept it as dead text or to
   refuse it. **Rec: refuse** (predictable; small and reversible; the
   `[FINDINGS-S1-REVISIT]` row reopens it under its triggers).

Not for Frank, but owed by the manager: re-supply fcrit-model notes 13–19
and fcrit-sound F4/F7/F12 (and F13's full text) from the transcript, or
close them as lost. This revision does not claim them.

## Verdict

**No BLOCKING item remains unapplied in the design.** All five blocking
findings (M-B1, M-B2, M-B3, S-F1, S-F2) are applied in the text, three of
them under Frank's D123-8 rulings. The design itself does not need a full
re-panel.

B2 now has three EXTERNAL preconditions. They gate the build, not the
design:
- K65's fix on main;
- GIVEUP1 (`lane/chkgaps`) merged;
- a ruling on OPEN 1.

**Recommendation: a focused re-check** (one critic, not a panel) of the
text that no critic has yet seen:
- §6.2a's per-reader argument, including the new C2b row;
- §7's digest rule and §10.2's collision-free defaults (M-B1);
- §6.4's deny-independent asking rule (S-F10).

The findings whose content was not relayed (fcrit-model 13–19; fcrit-sound
F4, F7, F12) are an honest gap in this record. If any of them was
blocking, this verdict does not cover it.
