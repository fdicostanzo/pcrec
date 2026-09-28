# findtie — [FIND-TIE] (2026-09-28, lane findtie, opus)

Ruled by Frank on lane findb5's report §6: the run reader's DATA tie rule
(leftmost) disagreed with its NONE rule (rightmost); make a PICK's data tie
follow its NONE order, in the run reader — the one inconsistent spelling.

## 1. Every PICK-kind tie site, found by grep, with its data-tie and none-tie order

`src/core/findings.c` has exactly three readers built on the PICK primitive
(`pcrec_find_pick`), plus one MASS-kind reader that also resolves ties (a
different question kind, no PICK involved). No other file in the tree calls
`pcrec_find_pick` or spells a rate tie of its own
(`tests/findings/structural_check.py` S1/S2 assert that).

| reader | kind | data-tie order (rate present) | NONE order (rate absent) | consistent? |
|---|---|---|---|---|
| `pcrec_find_set_pick` (necessary SET) | PICK | candidate order `[rightmost, 255..0]` → earliest-candidate tie rule lands on `rightmost` | `rightmost` (the threaded set member) | **YES, always was** |
| `pcrec_find_run_scan_index` (necessary RUN's scan member) | PICK | candidate order was the run's own left-to-right order → earliest-candidate tie rule landed on **leftmost** | `n - 1` (positional **rightmost**) | **NO — the one inconsistent spelling** |
| `pcrec_find_run_window_start` (RUN's truncation window) | MASS (sequence), not PICK | strict `<` keeps the first-found (lowest-`s`) window on a mass tie → **leftmost** | every window ties (uniform mass) → same loop → **leftmost** | YES, always was (MASS's NONE answer is spelled inside `pcrec_find_seq_mass`/`pcrec_find_set_mass`, D126 Q4, not by this reader) |

No second inconsistent site was found. `pcrec_find_run_window_start` is a
MASS reader, not a PICK — D126 Q4 spells MASS's NONE answer once, inside the
primitive (`uniform_mass`), and this reader's own loop already treats a tie
the same way whether or not a rate applies (leftmost `s`), so it needed no
change. The brief's "general mechanism, not special case" instruction is
satisfied by fixing the one PICK reader the same way `pcrec_find_set_pick`
already does it — reorder the candidates so the reader's own NONE candidate
is also the earliest, rather than inventing a second tie-breaking rule.

## 2. The fix

`pcrec_find_run_scan_index` (`src/core/findings.c`) now builds its candidate
order `[n-1, n-2, ..., 0]` (a local `cand[PCREC_MAX_REQ_RUN_SCAN]` array,
bounded by the one caller's own invariant — `RbRun`/`ReqRun`'s `whole` array
is sized `PCREC_MAX_REQ_RUN_SCAN`, `src/facts/facts_derive.h`/`facts.h`) and
asks `pcrec_find_pick(rate, cand, n, 0)`, mapping the returned candidate
index back with `n - 1 - result`. `pcrec_find_pick`'s own earliest-candidate
tie rule (unchanged) now lands on the run's positional rightmost member —
the same shape `pcrec_find_set_pick` already uses (`[rightmost, ...]`
threaded first). The NONE branch (`!rate`) is untouched in effect: passing
`rightmost = 0` into the reversed space still maps back to `n - 1`, the same
answer as before.

## 3. `docs/design/findings/design.md` §11.4 / B4's [r3 F4] tiebreak question

The report row on `[r3 F4]` asks whether §2.6's tie rule and C6's row (the
letter argmin's own order) have a verified TIEBREAK population. This row
answers the general shape of that question for the `req_run`/`req_byte`
family: **a PICK's tie must be spelled ONCE, as "equal to this reader's own
NONE answer," never re-derived per reader** — `pcrec_find_set_pick` already
did this by construction (its candidate order starts at the threaded
`rightmost`), and `pcrec_find_run_scan_index` did not (its candidate order
was the run's own bytes, in the run's own left-to-right order, unrelated to
which candidate the NONE branch answers). The fix generalizes directly:
whichever candidate a reader's NONE answer names should be the FIRST
candidate in the array a data pick walks. `run-rarity`/markov1's own C6 row
(§2.6, [r3 F4]) is a different accessor (bigram-based, not built by B4 yet)
and this lane does not touch it — but the rule to apply there, when it
lands, is the same one: build C6's candidate order so its NONE candidate is
first, rather than re-deriving a tie rule from scratch. No new verified
population is added by this lane for §2.6/C6 itself; this row closes the
question for the `PICK` primitive's three built readers only.

## 4. Witnesses (confirmed live)

```
$ build/pcrec -p rx -o /tmp/w1.c --pattern 'кириллица+' -e utf8 --analysis weblog
$ grep RX_REQ_BYTE /tmp/w1.c
#define RX_REQ_BYTE "134"        # 0x86, a UTF-8 CONTINUATION byte — was 208 (0xD0, the lead byte)

$ build/pcrec -p rx -o /tmp/w2.c --pattern '[a-z]+@é' -e utf8 --analysis weblog
$ grep RX_REQ_BYTE /tmp/w2.c
#define RX_REQ_BYTE "169"        # 0xA9, é's trailing byte — was 195 (0xC3, the shared lead byte)

$ build/pcrec -p rx -o /tmp/w3.c --pattern '[a-z]+@é' -e utf8 --analysis log
$ grep RX_REQ_BYTE /tmp/w3.c
#define RX_REQ_BYTE "169"        # same member as weblog: the tie rule decides it, not the bundle
```

Added as `tests/codegen/run_prechecks.sh` §4.10a/§4.10b/§4.10c
(oracle-verified is not applicable here — every reader in this file is a
SPEED choice among analysis-proven-necessary bytes, `docs/design/findings/
design.md` §6.2a; the check is the stamp against the emitted text, the
house shape for this file, not a `.rxt` match cell).

## 5. Movers — the DEFAULT axis, both encodings (IMPORTANT, per the brief)

The built-in `default` analysis declares `serves byte-rate when byte via
unigram` (`src/findings/default.rxt`), so a DEFAULT compile (no analysis
named) under `-e byte` reads real data too, and the shipped table ties
every zero-count byte at its 2 ppm floor — so the default axis can hit a
data tie exactly like a named analysis can. Measured live:

```
$ build/pcrec -p rx -o /tmp/d1.c --pattern 'é@'          # no analysis, -e byte (default)
BEFORE (main d604bee9): RX_REQ_BYTE "195"  RX_REQ_RUN "c3a940@0"
AFTER  (this lane):     RX_REQ_BYTE "169"  RX_REQ_RUN "c3a940@1"
```

`é@`'s tied pair (0xC3/0xA9, both at the floor) now resolves rightmost
(0xA9) under the DEFAULT byte-rate table too, not only under `weblog`/`log`.
This is expected and answer-identical (§6.2a); the sample above is the
default-path mover this brief asked to be stated prominently. The
corpus-wide DEFAULT-path mover COUNT (distinct from the ship_weblog/
ship_log counts findb5's manifests track) is **OWED** — see §7.

Two existing structural witnesses in `tests/codegen/run_prechecks.sh`
already sat on real DATA ties and were re-derived to their new correct
values in the same change (not merely re-pinned — computed by hand from the
mechanism, matching the file's own convention):

- **§4.9c** (the `byte`-encoding tie control for `é@`, default axis): was
  asserting `"195"` / `"c3a940@0"` (leftmost of the tie) as the CORRECT,
  untouched-by-`[OPT-REQRUN-ENC]` answer; now asserts `"169"` /
  `"c3a940@1"` (rightmost), with its prose corrected to explain why.
- **§4.5** (`github_pat_[A-Za-z0-9]{4}`'s truncation-window witness): the
  literal `_` (0x5F) occurs TWICE in `github_pat_` (index 6 and index 10),
  tied at the same ppm — the pre-fix leftmost tie picked index 6, forcing a
  4-window mass comparison the prose described; the rightmost tie now picks
  index 10, which is close enough to the run's own end that only ONE 8-byte
  window remains valid (`hi_s = n - 8`) — same window content
  (`"hub_pat_"`), scanned at local index 7 instead of 3. Re-derived by hand
  (§4.5's own convention), not by re-running the compiler and copying its
  answer.
- **§5.9r** (K66's own witness, `eeeeeeee~#~#~#~#`'s repeated `~`/`#`
  tail): the four `~` occurrences in the 8-byte window tie; local index
  moved 0 -> 6 (rightmost of the tie). Window content unchanged.

## 6. Emitted-scaffolding? — D76/D94

**Not scaffolding** (comments, declarations, layout are unchanged) — it is a
DIFFERENT BYTE CHOICE, `[OPT-REQRUN-ENC]`'s own precedent (abi 37 -> 38) for
exactly this shape: the change moves the emitted `memchr`/`memcmp` TARGET
BYTE and the `<PREFIX>_REQ_RUN` stamp's `@idx` VALUE on real populations (§5
above), with no struct offset and no `rx_info` member touched. Per that
precedent (and K64fix's, cited there) a stamp-VALUE-and-emitted-text move
IS an `abi` event even with no new scaffolding. Bumped `abi` 43 -> 44
(`src/gen/emit_dfa.c`'s `PCREC_ARTIFACT_ABI`). D94's grep for the old digit
plus the suites-that-count rule: `docs/spec/match_api.md` §6 (new top
entry), `docs/spec/findings.md` §4 (reader table row), `docs/spec/tuning.md`
§2.28, `docs/design/reqpos_2b.md` §2.3 (a SECOND AMENDMENT beside
`[OPT-REQRUN-ENC]`'s own), `src/core/CLAUDE.md`'s findings.c entry — all
updated in this change. `make test-codegen`'s `run_prechecks.sh` is GREEN
(304/0, see §8); the comparison-(B) FILEPIN re-pin in
`run_recursion_identity.sh` is the manager's at merge, per the standing
convention (a lane branch commit is not reachable from main yet —
`opt5i_report.md`/`ccdiff1_report.md`'s own precedent).

## 7. Validation — COMPLETE (light) / OWED (heavy)

**COMPLETE, run live on this box:**
- `make -j4 CC=gcc-16` — clean build.
- `make strict CC=gcc-16` — `strict: whole tree compiles clean with -Werror -Wshadow`.
- `PCREC=build/pcrec bash tests/codegen/run_prechecks.sh` — **304 passed, 0 failed**
  (was 301; +3 for §4.10a/b/c; §4.5 and §5.9r re-derived and green, §4.9c
  corrected and green).
- All witnesses in §4/§5 above hand-verified against the built compiler.

**OWED — the box was held by `land84`'s `make test`+`mech` chain for this
lane's whole working period (BOILERPLATE: one heavy suite at a time); exact
commands for the manager or a follow-up lane:**

1. **The corpus-wide movers census**, `docs/dev/lanes/findb5_evidence/
   ship_census.py`'s shape, restricted to the CORPUS population (not
   pcrec-bench) per this brief's own scope, base = main `d604bee9`, tip =
   this lane's own last commit, `-e byte`/`-e utf8` × default/`weblog`/`log`:
   ```
   BASE=<pcrec built from d604bee9>  NEW=<pcrec built from this lane's tip>
   SCR=<scratch dir>  POPS=corpus  PROCS=4 \
     python3 docs/dev/lanes/findb5_evidence/ship_census.py
   ```
   Report separately: (a) the DEFAULT-axis IDENTITY section's mover count
   at each encoding (this is the number §5 above asks to be stated
   prominently — a sample is already given), (b) the `ship_weblog`/
   `ship_log` mover DELTA against the counts already recorded in
   `tests/findings/manifests/ship_weblog_movers.txt` /
   `ship_log_movers.txt` (findb5's own corpus-only figures: weblog 153
   byte / 781 utf8, log 315 byte / 971 utf8 — this lane's tie fix can only
   change WHICH stamps moved on an already-moving artifact or add movers
   among previously-identical ones that happened to tie; it cannot remove
   the population findb5 measured, since every artifact `ship_census.py`
   calls a mover there differs from NEW-default for a reason unrelated to
   this lane's own tie order too — re-run and diff rather than assume).
   Re-pin `tests/findings/manifests/ship_weblog_movers.txt` /
   `ship_log_movers.txt` if the corpus-only rows move.
2. **The mech sabotage row**, S329 (this lane's own; S294 stays as its own
   row, NONE-path only, unaffected — confirmed by hand in §9 below):
   ```
   bash tests/mech/run_sabotage_matrix.sh S329
   ```
   Expected: `prechecks` DETECTED (structural-only — every member of a run
   is necessary, so no differential/corpus arm can see this plant; S294's
   own precedent), `harness` green (`corpus:0fail`).
3. `bash tests/codegen/run_recursion_identity.sh` comparison (B) FILEPIN
   re-pin, once this branch has a commit reachable from `main`.

## 8. Light re-derivation, S294 unaffected

By hand (not run — `make mech` is the heavy chain owed above): S294 plants
`if (!rate) return rightmost;` -> `if (!rate) return 0;` inside
`pcrec_find_pick`, the primitive both `pcrec_find_set_pick` and
`pcrec_find_run_scan_index` share for their NONE answer. My change touches
neither that line nor the NONE branch's effective behaviour (§2's "the NONE
branch is untouched in effect" — passing `rightmost = 0` in the reversed
space still maps back to `n - 1`). S294's own `SAB_REACH` witness (`é@`
under `-e utf8`, NO analysis — the NONE case, since `default` declares
`byte` only) is unaffected: `pcrec_find_run_scan_index` for that call still
returns `n - 1` on the clean tree and would still revert to the leftmost
NONE answer under S294's plant, exactly as before this lane. Confirmed live:
`é@ -e utf8` (no analysis) still stamps `RX_REQ_BYTE "64"` / `RX_REQ_RUN
"c3a940@2"` on this lane's tip, matching S294's own `SAB_REACH` literal
exactly.

## Files touched

- `src/core/findings.c` / `findings.h` — the fix, `pcrec_find_run_scan_index`.
- `src/gen/emit_dfa.c` — `PCREC_ARTIFACT_ABI` 43 -> 44.
- `src/core/CLAUDE.md` — findings.c entry addendum.
- `tests/codegen/run_prechecks.sh` — §4.9c corrected, §4.5/§5.9r re-derived,
  new §4.10 (a/b/c).
- `tests/mech/sabotages/S329_find_run_scan_data_tie_leftmost.sh` — new row.
- `docs/spec/match_api.md` §6, `docs/spec/findings.md` §4,
  `docs/spec/tuning.md` §2.28, `docs/design/reqpos_2b.md` §2.3 — D80 spec
  hunks.
- `docs/dev/plan.md` — `[FIND-TIE]` row, STATE:not-started -> STATE:started
  with the delivery addendum.
