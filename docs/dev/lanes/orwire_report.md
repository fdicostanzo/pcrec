# orwire — wiring the committed oracle store into an existing check

2026-09-10, lane `orwire`. Implements `docs/design/oracle_interface.md` §9
Step 1's own owed remainder: lane `orstore` built the store and captured
the real 387-property `membership` answer set against the true 10.46
reference (`docs/dev/lanes/orstore_report.md`) but deliberately did NOT wire
any existing check to consult it ("the CAPTURE, not the rewiring"). This
lane does the wiring. Branch `lane/orwire`, parked for the manager to merge.

## What was built

`tests/uprops/uprops_compare.py`'s utf8 arm now runs a SECOND, INDEPENDENT
comparison beside the existing live-oracle one, never a replacement:

- **`compare_against_store(mine, store_root, oracle_name, oracle_version,
  encoding)`** (new function) looks up each of pcrec's own swept property
  names in the committed store's `membership` kind via `oracle_store.lookup`
  — the design's own self-checking read path. Because the committed store
  IS the true pin (libpcre2 10.46 / Unicode 16.0.0, exactly pcrec's own
  table pin), every property it covers is compared at **EXACT agreement
  unconditionally** — no drift budget, on ANY box, including this Mac whose
  live-resolved library (Homebrew 10.48 / Unicode 17.0.0) is two versions
  ahead of the pin.
- **`main()`** accepts four new OPTIONAL trailing args
  (`STORE_ROOT STORE_ORACLE_NAME STORE_ORACLE_VERSION STORE_ENCODING`); when
  given, it prints an explicit `[STORE]` provenance block (which store
  instance/version answered, how many properties it covered vs. fell back
  to the `[LIVE]` result) and folds any store disagreement into the same
  `fails`/exit-code path the live comparison already uses. The pre-existing
  live-oracle lines are now prefixed `[LIVE]` for the same reason — every
  run states PROVENANCE, not just on the new path.
- **`tests/uprops/run_uprops_tests.sh`** §3 passes the four store args only
  for `enc = utf8` (the committed store holds only the utf8-arm capture —
  the byte arm is completely untouched, no `[STORE]` line, no behavior
  change), and only when `oracle_store/libpcre2-10.46/membership.tsv`
  exists (a clone missing the file — impossible for a committed path, but
  checked rather than assumed — silently falls back to live-only, matching
  today's behavior byte-for-byte).

## Coverage split

The utf8 arm's own `$NAMES` population (45 categories + 171 scripts ×
2 namespaces = 387) is EXACTLY the population `build_uprops_store.py
remote` captured, so the split measured today is **387 of 387 covered, 0
falling back to `[LIVE]`**. The mechanism does not assume this stays true:
`compare_against_store` returns a `missing` list for any name `mine` asks
about that the store does not have a row for, `main()` counts and prints it
every run (`[STORE] coverage: N of M ... 0 are NOT covered`), and a
`missing` name's answer is unconditionally the existing `[LIVE]` result
above it — never silently dropped from the check.

## Provenance (what the requirement asked for, quoted from a real run)

```
  [LIVE] pinned Unicode 16.0.0; oracle Unicode 17.0.0 -> drift budget: ...
  [LIVE] compared 387 properties; 47542 code points attributed to version drift
  [STORE] consulting the COMMITTED reference store libpcre2-10.46 (encoding=utf8)
          — this IS the true pin (Unicode 16.0.0), so every name it covers is
          compared at EXACT agreement regardless of what library this box
          resolves live
  [STORE] coverage: 387 of 387 properties this run asks about are in the
          committed store and were compared (exact); 0 are NOT covered and
          fall back to the [LIVE] result above
```

A reduced or absent store never reads as though the full one answered: the
`[STORE]` block only ever appears when store args were actually passed
(i.e. the file exists), and its own coverage line states the count that
actually ran, not an assumed one.

## Judgment calls from the orstore report — neither exercised

The brief named two judgment calls orstore flagged live in its report:
**captures-on-nomatch padding** (§5.3's ambiguity) and **`RemoteAdapter.
MAX_BATCH=60`**. This wiring does neither — it only calls `oracle_store.
lookup()` against the ALREADY-COMMITTED store (a pure local read, no ssh,
no new capture), and it never asks a `captures`-kind question (uprops has
none). Both judgment calls stand exactly as orstore left them, unredesigned.

## Live-reference paths: unchanged

`uprops_oracle.c`, the `$WORKDIR/uprops-oracle.txt` sweep, and the
`[LIVE]` drift-budget comparison all run exactly as before this change —
the store consultation is additive. `build_uprops_store.py` (the CAPTURE
tool) is untouched; its own header already names the exact command to
refresh the store (`python3 tests/oracle/build_uprops_store.py remote
--chunk 60`).

## Validation

**Targeted, both arms, real runs through `run_uprops_tests.sh` (this
lane's build, `gcc-16`):**

- `ENC=utf8 bash tests/uprops/run_uprops_tests.sh` (= `make
  test-uprops-utf8`): **26 passed, 0 failed.** §3's utf8 cell now prints
  both tiers — `[LIVE]` 387 compared / 47,542 drift-attributed / 0
  unexplained (unchanged shape from before this lane, wider than the
  historical 62,121-at-10.42 figure only because 10.48/17.0.0 drifted
  further from the 16.0.0 pin than 10.42/14.0.0 did in the other
  direction); `[STORE]` 387 of 387 covered, compared EXACT, **0
  disagreements**.
- `ENC=byte bash tests/uprops/run_uprops_tests.sh` (= `make test-uprops`,
  part of `make test`): **26 passed, 0 failed**, byte-for-byte identical
  output shape to before this lane (no `[STORE]` line — confirms the byte
  arm is genuinely untouched).
- `make strict`: clean (`-Werror -Wshadow` whole-tree) — this lane touches
  no `.c`/`.h` file, run anyway per the brief.
- `bash -n tests/uprops/run_uprops_tests.sh` and `python3 -m py_compile
  tests/uprops/uprops_compare.py`: both clean.
- Direct unit exercise of `compare_against_store` against the real
  committed store (`Greek` vs `sc=Greek`, confirmed non-vacuous — the two
  sets differ, matching `tests/uprops/CLAUDE.md` §4's own documented
  fact) and against a synthetic empty-set `mine`, confirming the function
  reports the expected diff count.

**Sabotage — a SCRATCH COPY only, never the committed store**
(`/private/tmp/.../scratchpad/orwire_sabotage/`, deleted after use, never
under `/Users/fdicostanzo/pcrec`): copied `oracle_store/libpcre2-10.46/
membership.tsv` to the scratch tree, corrupted one row's stored `question`
text (the `property` field, e.g. `Nko` → `CORRUPTED`) while leaving its
`question_hash` untouched, so a lookup for the true property name
recomputes the original hash, finds the row, and finds its stored text no
longer matches — the collision/corruption tripwire.

- Direct call: `compare_against_store({"Nko": ...}, scratch_root, ...)`
  raised `StoreCorruption` naming the exact row (`row 002f1fc5b41016e4's
  stored question 'CORRUPTED\tutf8' != recomputed 'Nko\tutf8'`) — unabsorbed,
  propagated to the caller as designed.
- End-to-end through the real CLI entry point:
  ```
  $ python3 tests/uprops/uprops_compare.py pcrec.txt oracle.txt 16.0.0 16.0.0 \
        scratch_root libpcre2 10.46 utf8
    [LIVE] pinned Unicode 16.0.0; oracle Unicode 16.0.0 -> EXACT agreement required
    [LIVE] compared 1 properties; 0 code points attributed to version drift
    [STORE] consulting the COMMITTED reference store libpcre2-10.46 (encoding=utf8) ...
  FAIL: [STORE] the committed store failed its own self-check and could not
        be consulted: StoreCorruption("...the collision/corruption tripwire fired")
  $ echo $?
  1
  ```
  Loud, named, non-zero exit — never a silently wrong answer, and never
  read as though the full oracle had answered.
- A clean run against the same (uncorrupted) real committed store, with a
  matching `pcrec`/`oracle` line for one real property (`Nko`), confirmed
  `exit 0` with the `[STORE] coverage: 1 of 1 ... compared (exact)` line —
  the positive control beside the sabotage's negative one.

## docs/spec/ — none owed

Searched `docs/spec/` for any mention of `uprops`/`oracle_store`/"oracle
interface": zero hits. This change is test-infrastructure-only (D80's own
scope is "anything a CALLER can observe" — an entry, a flag, a diagnostic,
a module's behaviour); nothing pcrec emits, accepts, or promises moved.
Matches `orstore`'s own precedent (its report made the identical
determination for the store's own landing).

## What was NOT touched (§9's later rungs, unchanged)

`tests/utf8/axis12_scripts.rxt` is a static `.rxt` corpus (baked-in 10.46
answers at authoring time, not a runtime oracle consultation) — it was
never itself a store *consumer* in the sense this ladder step wires; its
population is exactly the `membership` differential population this
wiring now checks exact, so its own answers are corroborated by this
change without the file itself changing. The C3 python tier, PC-3/PC-4,
and the shared-binding family (`bref_oracle.py`/`la_oracle.py`/
`u8_oracle.py`/`atomic_oracle.py`) remain unwired — §9 Steps 2-4, later,
unscheduled rungs, per the design's own text.

## Handback

Branch `lane/orwire`, all changes committed, report committed. Validation
COMPLETE: both arms run for real with the exact numbers above, `make
strict` clean, sabotage validated in both the failing and passing
direction against a scratch-only corrupted copy. Nothing here should move
any existing `make test` result (no `.rxt`, no `src/`, no existing check's
verdict logic touched) — that is a claim from reading the diff plus these
targeted runs, not a full-suite measurement; the manager's own full battery
is the merge standard per BOILERPLATE.
