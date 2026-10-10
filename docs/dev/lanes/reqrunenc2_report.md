# [OPT-REQRUN-ENC] stage 2 — the build (lane `reqrunenc2`, 2026-09-26)

Stage 1 (the D77 census, `docs/dev/optloop/reqrunenc_census.md`) measured
candidate R (rightmost) byte-identical to candidate S on the entire real
`-e utf8` population (912/912 runs) and recommended it. The manager ruled:
**build candidate R, WITH an abi bump** (overruling the census's own "no abi
bump" — the repo's precedent, k64fix `1e6a90b0`, is that a stamp-VALUE and
emitted-text move is an abi event even with no new scaffolding).

## The diff

`src/opt/reqbyte.c`'s `rn_scan_index`: `if (!bytekey) return 0;` becomes
`if (!bytekey) return r->n - 1;`, matching `rb_pick`'s own `!bytekey`
fallback exactly — one mechanism, two call sites, the tree's own
"general mechanisms, not special cases" rule. Comment updated to cite the
census and pcrec-bench's O-60 finding.

## The abi ritual (37 -> 38, D76/D94)

Every reader found by grep and updated in the same change:

- `src/gen/emit_dfa.c:51` — `PCREC_ARTIFACT_ABI 37` -> `38`.
- `tests/codegen/run_codegen_tests.sh` — `ABI_EXPECT=38`; the failure-message
  narrative gains its own `(37->38 -- ...)` clause (the s1step6/c9dec3e4
  template).
- `docs/dev/history/abi_changelog.md` — new `is \`38\`` bullet (the previous `is
  \`37\`` bullet becomes `was \`37\``), the change-log's own gap-free range
  updated to `2` to `38`.
- `docs/design/reqpos_2b.md` §2.3 — a DATED AMENDMENT (per the manager's
  ruling: don't rewrite history) citing the census and stating the
  ratified "costs nothing measurable" sentence is falsified.
- `docs/spec/tuning.md` §2.28 (the `[OPT-REQPOS]` tier 2b section) — the
  "leftmost outright" sentence corrected to "rightmost outright", with the
  mechanism and the truncation-window consequence (the admissible range
  collapses to the run's own last 8 bytes for a rightmost-indexed member).
- `src/opt/CLAUDE.md`'s `reqbyte.c` design entry — a new bullet, plus the
  `Tests:` line and the sabotage list extended for §3.6/§4.9 and S294.
- `tests/mech/CLAUDE.md`'s sabotage table — the S294 row, beside S266-S268.
- `tests/codegen/run_recursion_identity.sh` — (B) re-pinned to `fe5a0bbc`
  (this lane's own last `src/`-touching commit — the tree's current
  convention per k66fix/s1build/s1step6: a lane self-pins to its own
  commit, valid because merges here preserve commit hashes; NOT the
  "leave it unset, owed to the manager" convention some earlier 2026-09-02
  reports recorded, which this landing's own precedents have superseded).

Checked and found UNCHANGED (no re-pin needed, verified by reading the code
rather than assumed): `tests/codegen/run_cpset_structure.sh` CHECK 3's
sample-pattern manifest (compiled at DEFAULT/`byte` encoding only — `!bytekey`
never runs there); `tests/codegen/run_encoding_checks.sh`'s DD12a(i)
normalizer (already generically normalizes "WHICH member is scanned" for
`REQ_BYTE`/`REQ_RUN`, byte value AND offset, inside `rx_reqrun`/
`rx_reqrun_whole` blocks only); `docs/design/reqbyte_freq_pick.md` (states
the single-BYTE pick's own encoding rule, `rb_pick`, which this change does
not touch — grepped for a leftmost/run mention, found none); `tests/resource`
and `tests/rxtsource` size/line pins (no utf8-encoded run-bearing pattern
pinned by exact byte count).

## The structural codegen check (the ruling's own acceptance bar)

`tests/codegen/run_prechecks.sh`:

- §3.6/§3.6r — the existing utf8 multi-byte witnesses (`é`, `x(é|è)y`,
  `a\x{1F600}b`, `é@`) updated to their new rightmost-fallback values.
  `x(é|è)y` is the census's own named theoretical exception (a run
  truncated mid-character, where R keeps a lead byte and only S — not
  built — would avoid it): kept in the file as the documented case, not
  silently "fixed".
- §4.5c — the truncation-window witness (`github_pat_[A-Za-z0-9]{4}`)
  updated: the admissible window range collapses to the run's own last
  8 bytes when the scanned member sits at the run's last index.
- **§4.9 (new)** — the ruling's own three acceptance checks: `é@` under
  `-e utf8` stamps `RX_REQ_BYTE "64"` (not the shared UTF-8 lead byte 195);
  `Москва`'s picked byte is asserted OUTSIDE the `0xC2-0xF4` lead-byte
  range by a numeric RANGE test (the general claim, not one more literal);
  and a `byte`-encoding control on the identical two-byte-tie population
  (`é@` with no `-e` flag) confirms the frequency argmin still answers `195`
  (tied-minima leftmost) rather than degrading to "always rightmost" —
  proving `!bytekey` scopes the whole change.

`bash tests/codegen/run_prechecks.sh`: 292 checks passed, 0 failed (was 289
before this lane's +3 new §4.9 checks; §3.6/§4.5c fixes are net-zero count).

## Sabotage row S294

`tests/mech/sabotages/S294_reqrun_enc_decline_leftmost.sh`: reverts
`rn_scan_index`'s `!bytekey` branch to `return 0;` (the pre-fix leftmost
rule). STRUCTURAL DETECTOR ONLY, S266's own precedent one call site over —
every member of a run is a byte every match must contain, so the choice can
move a speed and never an answer; `corpus:0fail` beside a red `prechecks`
arm is the row working. MECH-REACH probe: `é@` under `-e utf8` on the clean
tree stamps `RX_REQ_BYTE "64"` and `RX_REQ_RUN "c3a940@2"`.

Solo mech-matrix run: `bash tests/mech/run_sabotage_matrix.sh S294` —
**[MECH RESULT OWED, run launched async, see below]**.

## Validation

- `make strict CC=gcc-16`: **CLEAN**.
- `bash tests/codegen/run_codegen_tests.sh`: **109/109 checks pass**,
  including the abi=38 assertion.
- `bash tests/codegen/run_prechecks.sh`: **292/292 checks pass**.
- `bash tests/codegen/run_recursion_identity.sh` (the re-pinned (B) gate):
  **[OWED — launched async at `/tmp/recid.log`, background task `bd4rqp4rh`]**.
- `bash tests/mech/run_sabotage_matrix.sh S294`: **[OWED — launched async
  at `/tmp/s294_mech.log`]**.
- Full `make test` (async, `timeout 9000`, per BOILERPLATE's darwin sizing):
  **[OWED — see below]**.

## Rulings received

- Build candidate R (not S), matching `rb_pick`'s own `!bytekey` fallback.
- WITH an abi bump (overruling the census's own "no abi bump" recommendation),
  citing the k64fix `1e6a90b0` precedent (a stamp-VALUE-and-emitted-text
  move is an abi event).

## What is OWED

All three launched before hand-off (per BOILERPLATE's DO-THEN-FINISH — the
lane's report and commits are complete first, these are the last acts):

- `bash tests/mech/run_sabotage_matrix.sh S294` — running, log
  `/tmp/s294_mech.log`.
- `bash tests/codegen/run_recursion_identity.sh` at the new (B) pin —
  running under `timeout 1800`, log `/tmp/recid.log`.
- Full `make test CC=gcc-16` — running detached (`nohup ... & disown`,
  survives the session) under `timeout 9000`, log
  `/tmp/reqrunenc2_make_test.log`. Verdict is `make`'s own `*** [test-X]
  Error` lines / the `sections ran: N/M` trailer, never a bare `FAIL:` grep
  (learnings.md §3, 2026-09-22).

A fresh agent or the manager should poll these three logs' completion
markers rather than re-run any of them.

PARKED on `lane/reqrunenc2`, not merged.
