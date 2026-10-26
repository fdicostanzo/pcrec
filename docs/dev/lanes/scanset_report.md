# scanset report — [SCANEDGE-SET]: a scan edge over a byte-class SET

Lane scanset (opus), 2026-10-26, branch `lane/scanset` off main 570b601d6. Frank's go (2026-10-26):
"Ok I understand. It's more about the dfa states than the pattern. Go ahead."

## 1. Change summary

- **The rule** (`src/opt/scanedge.c`): a state is scan-shaped for a class SET S and exit E when every
  class of S goes to one successor and every other class goes to E. `shaped()` keys a set by its
  LOWEST class, so the pass's existing per-class loop now iterates set keys: each state has exactly
  two targets when scan-shaped, so at most two keys, and the walk stays linear. `same_shape()`
  gains `same_set()` (two sets may share a lowest class). One class is the set of size one: the old
  one-class candidates are exactly the new candidates whose set has one class, so there is no
  parallel path. `chain_cmp` gains a final tie-break on the key (one state's two sets) so the order
  never depends on qsort stability. A bounded edge kills ALL of its set's cells in the head row.
- **The field** (`src/core/internal.h`): `DState.scan_cls` -> `uint8_t scan_set[32]` (a bit per
  class id; `clsmap` is `uint8_t`, so ≤ 256 classes), read through `pcrec_scan_has(st, cls)`.
- **Readers**: `src/gen/known.c` `kn_step` (membership), `src/gen/emit_dfa.c`: `revend_nl_last`
  (membership), `scan_choice`/`scan_tables_bitmap`/`edge_advance` (all through one
  `scan_byte_set`: union(S) as 256 bytes), the state legend and the edge comment (`scan_set_text`:
  "class 1" for one class, unchanged; "classes 1, 2" for more; the legend's example byte is the
  set's lowest class). No memfn edit: the kit's EDGE advance site already takes a 256-byte set and
  the run test comes from clskit over the set's ranges (STOP rule not triggered).
- **No new constant**: no limit on |S| was needed (the set is at most every class but the exit).
- Spec: `docs/spec/tuning.md` §2.18¶1-¶2 (a run counts a byte SET; the three witness shapes).

## 2. Census check (1): run test vs transition row, read off the artifact

`tests/codegen/scan_set_check.py`, run as a coprocess on `run_scan_edge_census.sh`'s existing corpus
sweep (new section (7); no second sweep). Per emitted edge it evaluates the run test (a table read
or a range expression, over bytes) and reads the head's row from the emitted `byte_class` +
`next_state` tables (or a constant-folded step): unbounded edge, run-test bytes == the bytes that
stay on the head and every other byte goes to ONE target; bounded edge, run-test bytes step to dead
and every other byte to ONE target. The two sides come from different sources (subset construction
vs the pass's `scan_set`), which is what lets it fail.

Measured on the landing tree (census2, 5,027 corpus patterns): **1,167 edge-bearing artifacts;
1,380 unbounded and 853 bounded edges checked, 0 mismatches; 251 edges count more than one class;
38 edges skipped**, all `no-state-block` (artifacts whose machine block the parser does not
recognise, e.g. `a+(?=A)`, `x*(?!a)`; printed as FINDING lines, never a pass). Floors: half the
measure (685 unbounded, 121 multi-class), so the one-class rule (0 multi) is red.

Reach vs the survey (rwsurvey Q4: 269 corpus / 11 bench patterns gain on some BUILT machine, an
upper bound). Artifact level, old (main, abi 86) vs new, default flags, `--features all`:

| population | compiled | artifacts carrying a multi-class edge | of them: no edge before | artifacts that lost an edge | one-class artifacts whose edge facts moved |
|---|---|---|---|---|---|
| corpus (distinct `pattern` lines) | 4,483 | 170 | 160 | 0 | 0 |
| bench (pcrec-bench `bench/*/patterns`, read-only) | 271 | **11** | 8 | 0 | 0 |

The bench's 11 are exactly the survey's 11 (tail-space-eol, tail-ext-lower-txt, tail-dotstar-txt,
json-number-extended, base10num-grok and its noatomic twin, winpath-grok,
username-password-pair, cls-s-uc, cls-range, asr-k-uc). The corpus 170 < 269 because the survey
counts machines BUILT and this counts artifacts EMITTED (x-machines and machines not chosen are
not emitted). No existing edge was displaced.

## 3. Witnesses (check (2)) — census section (8) and `tests/classes/scan_set.rxt`

Per machine, `edges/multi-class`, compiled `--features all -fcomments`:

| pattern | flags | new | old (main) |
|---|---|---|---|
| `\S+@\S+` | | anchored 1/1, forward 1/1, reverse 1/1 | none |
| `\s+$` | | anchored 1/1, reverse 2/2 | none |
| `\s+$` | `-fno-rev-end` | reverse 1/0 | reverse 1/0 (forward: EOL view, precondition (3)) |
| `0x[0-9a-fA-F]+` | | anchored 1/1, forward 1/1 | none |
| `[a-z]+\.txt$` | | reverse 1/1 | none |
| `[a-z]+$` (one-class control) | | reverse 1/0 | reverse 1/0; artifact identical to main's but for the abi digits (diffed); its edge comment+guard pinned |
| `(?:[a-z]\|[0-9]X){0,8}` (negative) | | none | none |
| `(?:a\|bc)*` (negative: `a` stays, `b` leaves) | | none | none |

(The brief's `([a-z]|[0-9]X){0,8}` is a CAPTURING group and compiles to the VM: no DFA, so a
vacuous negative. The non-capturing form is used, plus `(?:a|bc)*`, which is the one the S1637
plant actually turns into edges.) `tests/classes/scan_set.rxt`: 11 patterns, 74 cases,
expectations from libpcre2-8 10.46, python3-re cross-checked on non-`# pcre2-only` blocks (0
differences); green on the lane build.

## 4. Sabotage (check (4)) — `run_sabotage_matrix.sh` at 8d94338ea (all REACHED)

| row | plant | detector | result |
|---|---|---|---|
| S1633 | run test = the set's lowest class only (emit) | scanedge (section 7) | DETECTED 169 fail |
| S1634 | `shaped()` back to the one-class rule | scanedge (section 8 + floor) | DETECTED 5 fail |
| S1635 | one-class edge text says "classes" | scanedge (control pin) | DETECTED 3 fail |
| S1636 | run test also counts class 0 (answers move) | corpus `scan_set.rxt` | DETECTED 16 fail |
| S1637 | live classes join the key's set | scanedge (negative row) | DETECTED 265 fail |
| S693 | abi left at 86 (re-aimed 87 -> 86) | codegen | DETECTED 5 fail |
| S213 | exit uniformity deleted (re-anchored) | was counterk.rxt | **UNDETECTED at 8d94338ea** (0/1675) |

S213 FINDING: the new `same_set` conjunct alone refuses counterk's counted-digit chains, so the old
detector went blind, but the plant is still a real miscompile: a differential (plant vs clean,
3,000 generated patterns) found `(?:-?[ab]{2,4}|1b)` on "xbaxb-9bxb" (nomatch vs (1,3)) and
`(?:-{2,4}a[ab]|bb)` on "b--aba" (nomatch vs (1,5)). Both are now blocks of `scan_set.rxt` (4 fail /
70 under the plant, measured by hand with the planted binary) and S213 is re-aimed there. Its mech
row was NOT re-run after the re-aim: OWED, as a stage of the queued job below.

## 5. Measurement (indicative; the bench is the record)

61,440 B subjects, `rx_search`, best of 7 rounds of 2,000 calls, gcc -O2, Zen 4 dev box under
`boxlock` (load ~2.8 from other sessions):

| pattern | subject | old ns/B (stamp) | new ns/B (stamp) |
|---|---|---|---|
| `\s+$` | all spaces | 1.166 (none) | **0.189** (bitmap) |
| `\S+@\S+` | `x@y` + 61,437 `a` | 0.377 (none) | 0.378 (bitmap) |
| `[a-z]+\.txt$` | 61,436 `a` + `.txt` | 1.103 (none) | **0.185** (range) |
| `[a-z]+$` (control) | all `a` | 0.184 (range) | 0.185 (range) |

`\s+$` is back to the pre-4ea6fb19c 0.19 ns/B. `\S+@\S+` does not move: its after-`x@y` state was
already a stay-skip state (`\S` is > 191 stay bytes), so the edge replaces an equally fast skip.

## 6. abi readers (86 -> 87, provisional "next at landing"; 85 stays the kit's)

Found by grep (`abi 86`, `ABI_H 86`, `ABI_EXPECT`, the `PCREC_ARTIFACT_ABI` define):
`src/gen/emit_dfa.c` (define); `docs/spec/match_api.md` (§1 guard block x3, §6 table row 1,
§6¶17); `docs/dev/history/abi_changelog.md` (current-value paragraph); `tests/codegen/
run_codegen_tests.sh` (`ABI_EXPECT`, transition message: added 84->86 and 86->87);
`tests/mech/sabotages/S693_abi_not_bumped.sh` (BEFORE 87 / AFTER 86); `tests/codegen/
run_recursion_identity.sh` FILEPIN self-pinned to `ddd18d3df` (the lane's last src commit; the
manager re-pins to the merge). `S327`'s `86` is an unrelated count. If 87 is taken at landing,
every reader above moves together.

## 7. Files

src: `src/opt/scanedge.c`, `src/core/internal.h`, `src/gen/emit_dfa.c`, `src/gen/known.c`,
`src/ir/dfa.c` (comment). tests: `tests/codegen/scan_set_check.py` (new),
`tests/codegen/run_scan_edge_census.sh` (sections 7, 8), `tests/classes/scan_set.rxt` (new),
`tests/mech/sabotages/S1633..S1637` (new), S213 (re-anchored, re-aimed), S693. docs: spec, changelog,
CLAUDE.md entries (src/opt, tests/codegen, tests/classes), lanes NOTES.md index,
`docs/dev/lanes/scanset_job`. plan.md not touched (the pre-commit plan lint refuses
STATE:started in Backlog; the manager moves the row).

## STATE AT HANDOFF

- Built and committed on `lane/scanset`. Targeted validation done: `make strict` clean; census
  (full corpus) 29/29 green before section (8) grew, 30/30 on the POP subset after; scan_set.rxt
  74/74; mech 6 of 7 rows as expected (S213 finding above, re-aimed, its re-run OWED).
- OWED: job `500-scanset-test` (`docs/dev/lanes/scanset_job`): build, strict, test-codegen,
  `AXES='-fno-scan-edge -fno-view-edge'` run_axes.sh, mech row S213 (job.log.mech), full `make test` via perfrun. Logs in the
  job's run dir (`scripts/boxqueue state scanset-test`); completion lines `sections ran: 79/79`
  (job.log.make), `run_axes.sh: all axes answer-identical` (job.log.axes). A NEW corpus file may
  move population pins (startset manifests, axes allowances, size tripwires, rxtsource census):
  a red there is a re-pin, read with the perfrun note.
- Rulings file `scanset_rulings.md`: no entries ("(none yet)") at every check.
