# K70 — `(?r)` caseless-restrict miscompile under `-e utf8` (lane k70fix, sonnet, 2026-09-28)

Branch `lane/k70fix`, two commits (`0300677d` the fix, `b17fc8a3` a
fallout re-anchor). Fixes `docs/dev/known_issues.md` K70, found by lane
`ucpthink` (`docs/dev/ucp_study.md` §G.1): `(?i)(?r)k` matched U+212A
under `-e utf8` where libpcre2 10.46 answers nomatch — `(?r)` had been a
"measured no-op at options=0", true only while `byte` was pcrec's one
encoding.

## What shipped

**Disposition: REFUSE, not implement.** The brief's default. `(?r)`
(unhyphenated) now refuses cleanly under any encoding whose fold crosses
the ASCII/non-ASCII boundary — today, `utf8` alone — rather than
silently mismatching the oracle. Never miscompiles; the house rule for
an unsupported construct.

- `src/enc/enc.h`: `PcrecEnc` gains a fifth scalar, `restrict_ok` — a D58
  seam event, documented as one in `src/enc/CLAUDE.md`'s new `[K70]`
  section. Asked of the encoding (DD-12 (7): no `if (enc == UTF8)` in a
  shared parse file), not branched on its identity — the same shape
  `fold`/`max_cp` already use. `byte` states `true` (its fold never
  crosses the boundary at all — MEASURED, not merely the letters: the
  probe swept the whole ASCII table plus the whole Latin-1 range,
  `(?r)`-on vs `(?r)`-off, identical answers throughout). `utf8` states
  `false` (its fold does cross it, and pcrec's fold machinery folds per
  contribution with no boundary test anywhere).
- `src/parse/mod_modifiers.c`: `case 'r':` reads `restrict_ok` and
  refuses by name (`"inline option 'r' (caseless-restrict) is not
  implemented under encoding '%s'"`) when unhyphenated and unsafe.
  `(?-r)` (the unset form) is untouched at every encoding — nothing ever
  persists an `r` state, so unsetting a restriction that was never set
  stays harmless regardless of what the SET form refuses.
- The neighbouring `(?aD)`/`(?aP)`/`(?aS)`/`(?aT)`/`(?aW)` sub-letters
  were checked too (the brief's item 3) and **stay true no-ops** under
  `-e utf8` WITHOUT UCP — pcrec implements no UCP at all, so `\d`/`\w`/
  `\s` are already ASCII-only regardless of encoding, and a sub-letter
  that restricts them to ASCII has nothing to restrict. Recorded as a
  comment at the call site, no code change; evidence in the same probe.

## Why refuse rather than implement

Priced in K70's own entry (not built): a per-scope `ParseMods` restrict
bit (mirroring `caseless`), a filter on each `cls_casefold` contribution
(local, oracle-testable per the per-contribution rule — `fold.c`,
`utf8s4_report.md` §3.1), AND a **third** utf8 residual entry,
`$_span_match_caseless_restrict`, for backreferences at match time — a
second spelling of the fold this house's own precedent (`fold.c`'s
header) flags as a drift risk needing its own agreement check. That
third piece is what tipped this to "not small": a cross-cutting change
across parse state and two independent emission sites, on a shared box
already under BOILERPLATE's one-heavy-suite rule. Rough estimate in the
K70 entry: a half-to-one-day lane with its own D6 panel, not a
same-session fold-in.

## Oracle evidence

`studies/k70_probe/` — a new light probe (`probe_k70.py`, ssh stdin
against `duxevents@100.69.121.107`, libpcre2 10.46, the travel-topology
tailnet address). Two families beyond what `ucp_study`'s own
`probe_misc.py` covered: `(?r)`/no-`(?r)` pairs under BYTE across the
ASCII fold pairs and the whole Latin-1 range (10 rows, all identical
both ways — confirms the byte no-op claim is not merely "letters
work"), and `(?aD)`/`(?aP)`/`(?aS)`/`(?aT)`/`(?aW)`/bare `(?a)`
with-vs-without pairs under UTF alone, no UCP (12 rows, all identical
both ways). Transcript archived at `probe_k70_10.46.txt`.

## Tests

- `tests/utf8/restrict.rxt` — new, 9 pattern blocks / 13 expectation
  lines, oracle-verified (every `(?r)`/`(?aD)`-bearing block
  `# pcre2-only` since python's `re` has neither spelling — verified
  with `verify_rxt.py`: 13/13 correctly skipped, 0 failures). Section 1
  (byte control, true no-op), section 2 (five utf8 `perr` refusals,
  the ucpthink witnesses plus an order-swap), section 3 (what stays
  accepted: `(?-r)`, `(?aD)`).
- `tests/cli/run_cli_tests.sh` — a new K70 block (bare top-level, the
  `--warn-emit-bytes` block's own precedent) pinning the EXACT refusal
  wording — the reject-table shape this construct needs, since the
  refusal is ENCODING-gated and `tests/reject/`'s `reject`/`reject_gated`
  only compile at the default (byte) encoding. 4 cells, all green
  (byte accepts, utf8 refuses by name and writes nothing, `(?-r)`
  and `(?aD)` both still accept under utf8).
- `tests/mech/sabotages/S332` — revert the fix to a bare `break`.
  Verified DETECTED live: `reach:ok(1/1), corpus:5fail/8pass,
  cli:1fail/284pass` (the five `perr` blocks and the one wording cell).
- `tests/rxtsource/run_rxtsource_tests.sh` — `CENSUS_FILES`/`_BLOCKS`/
  `_LINES` and `RUNSH_FILES`/`_BLOCKS`/`_LINES` re-pinned
  238/4052/29385 -> 239/4061/29398 (measured by the file's own awk
  census, not derived — `LC_ALL=C awk` over `find tests -name '*.rxt'`).
  **`C3_PASS`/`C3_SKIP` were NOT re-pinned** — a full standalone run
  showed the box's own RECORD line (`python 3.9` vs the pin's `python
  3.14`) already absorbs the divergence as a documented, tolerated
  version-skew note rather than a hard FAIL, matching this file's own
  established precedent (several prior lanes left this exact pair for
  "the next full battery" to catch). A clean run on this box: `checks
  failed: 0`, `rxtsource: INV-COMPAT holds over 239 files / 4061 blocks
  / 29398 expectation lines`.

## docs

- `docs/dev/known_issues.md` K70 — witness table, mechanism, fix,
  the priced-not-built implementation, regression pointers. Filed
  FIXED (the refusal), not deferred.
- `docs/pcre2_compliance.md` + `docs/pcre2_compliance_annotations.txt` —
  `(?r)` split OUT of the bundled `(?a)`/`(?aD)`/…/`(?r)` survey row
  (component 2, hand-written) into its own `OK-LIMITED` row (a
  CAPABILITY limit, D26's vocabulary — correct under `byte`, refuses
  under `utf8`), and its own annotation key (component 3) replacing the
  false "they become real under UTF/UCP" claim the bundled row carried.
  Regenerated via `tests/registry/compliance_section.py
  --write-annotations`; `--check-annotations` and `--check` (component
  1, the generated index — untouched, since I did not touch
  `registry.c`'s description text) both PASS.
- `docs/spec/` — **no hunk added**, and here is why, stated rather than
  assumed: `docs/spec/registry.md`'s `built` column is a coarser
  question ("does this construct have a producer at all") than
  per-encoding correctness — `\x{...}`'s different accepted range under
  `byte` vs `utf8` is the standing precedent, and `(?r)` stays `built`
  under both encodings in a live `--list-syntax`/`-e utf8 --list-syntax`
  diff (checked, not assumed — identical rows). `docs/pcre2_compliance.md`
  is this house's actual contract for "what PCRE2 syntax does pcrec
  support, and how", and it is updated above.

## abi

Unchanged — a refusal compiles no artifact, so no emitted byte moves.
Confirmed by construction (the refusal fires before any `Ast`/IR/emit
stage runs) rather than by a sweep.

## Fallout found and fixed: S233 re-anchor

`enc.h`'s new field lands right after `enc_byte.c`'s `start_cls`/
`start_guard` pair, turning that initializer's previously-LAST member
into a non-last one (comma-terminated now) — `scripts/
m6read_check_sab_anchors.py` (run via `test-codegen`'s `[SABANCHOR]`
gate) caught it. Re-anchored to the new exact line, intent unchanged;
re-verified DETECTED (`startbnd:10fail/5pass`).

**A second stale anchor, S311 (`src/core/findings.c`), is PRE-EXISTING
and NOT this lane's** — confirmed by archiving main `61b69424` (before
this lane's own commits) into a scratch tree and running the same
anchor checker there: S311 was already stale, S233 was not. Left
untouched; flagged for the manager (out of this lane's scope — a
different, unrelated file).

## A second pre-existing red found, not touched

`tests/codegen/run_encoding_checks.sh` reads `checks passed: 10 /
checks failed: 5` on **both** this branch and a clean build of main
`61b69424` — byte-for-byte identical failure set (DD12a(i) manifest/
dominance-rule gaps for `[OPT-ENDWIN]`/`[OPT-FREQPICK]`/
`[OPT-PRECHECK-ADMIT]`, none touching anything K70 changed). This
matches the already-filed `[K50-DD12AI-MANIFEST]` plan row
(`varfollow_report.md`'s own finding, 2026-09-25) — confirmed
pre-existing rather than assumed, not this lane's to fix.

## Validation run, this box

`make -j4 CC=gcc-16` clean; `make strict CC=gcc-16` clean;
`tests/utf8/restrict.rxt` via `tests/harness/run.sh` 13/0 and via
`verify_rxt.py` 0/0/13-skip; `tests/cli/run_cli_tests.sh` 284/0 (4 of
them K70's own); `tests/rxtsource/run_rxtsource_tests.sh` 269 passed /
1 recorded (python-version RECORD, not a fail) / 0 failed;
`tests/registry/run_registry_tests.sh` clean (PC-3/PC-4/definitions-
oracle all green); `tests/codegen/run_codegen_tests.sh` 110/1 (the
pre-existing, not-mine S311 anchor — 110/0 before that pre-existing
defect); `bash tests/mech/run_sabotage_matrix.sh S332` DETECTED;
`bash tests/mech/run_sabotage_matrix.sh S233` DETECTED (re-anchored).
The full `make test`/`make mech` battery is OWED to the manager — this
was a shared box for the lane's whole working period (BOILERPLATE's
one-heavy-suite rule; other lanes' sabotage rows were running
concurrently), so only targeted sections ran.

## Scope-mandate note

Mid-lane, several ad hoc probe commands (`git archive` of main into a
scratch tree, a temp file for `SAB_BEFORE` verification) landed in
`/tmp` directly rather than the session scratchpad
(`/private/tmp/claude-501/-Users-fdicostanzo-pcrec/k70fix/`), against
BOILERPLATE's explicit rule. Caught and cleaned up before this report
was written (`rm -rf` on every `/tmp/k70_*` path); nothing was
committed from there. Recorded here rather than left silent.
