# silentred — two opt-in checks red on main, nobody counting (2026-09-30, sonnet, triage)

Branch `lane/silentred` from main `8f45c733`. Touched: `tests/codegen/run_recursion_identity.sh`,
`tests/codegen/run_encoding_checks.sh`, `tests/codegen/CLAUDE.md`, this report. No `src/`, no abi event.

## 1. Wiring — the K35 reading is right

Neither script is in `make test`. `TEST_SECTIONS` (Makefile:288-299) names neither; `test-codegen`'s
group (Makefile:491) does not run them. `run_recursion_identity.sh` is `make test-recursion-identity`
(Makefile:982, "opt-in ... a claim about a MOMENT"); `run_encoding_checks.sh` is `make test-encoding-checks`
(Makefile:605, opt-in, rides no TEST_SECTIONS entry). Both are reachable only from `make mech` arms
(`recidentity`, `encoding`) and by hand. So "46/46 green" on U2's and K73's trees never ran them. Both were red
on main at `8f45c733` (measured, PROCS=2/1, Mac, LOADED box).

**Recommendation (not done, needs the manager's OK):** wire `test-encoding-checks` (bounded, ~10 min
at PROCS=1 on a loaded Mac; the default `ENC_MAX_BLOCKS=250`) into `TEST_SECTIONS`, and add
`test-recursion-identity` to the merge battery (`scripts/battery.sh`) rather than `make test` (it builds two
reference compilers and ran ~35 min here). The recorded history (D118 -> [VAR] revival: PAIRS=0 for two days;
this red) is the argument: an opt-in gate is a gate nothing re-runs when the surface under it moves.

## 2. Recursion identity (A): 264 -> 0, all four axes, 16/0

Cause: [UCP] U2 (`A_CTX`) moves every one-character lookaround / `\b` off the pre-module reference's route
(VM -> DFA on default/noprefilter/nocaptures; VM program -> context form under `--engine=vm`). No bucket named it.
NOT a regression: U2 is a ruled abi 46 event whose own gate (identity vs `-fno-ctx-node`) is elsewhere.

Fix (sixth exception, the file's deny-axis style): a moved region is excused IFF (a) the pattern TEXT carries a
lookaround/word-boundary spelling (`CTX_POP`, a new independent census, `CTX_RE`) and (b) the subject compiler with
`-fno-ctx-node` (plus the stamped axes, plus `-fno-alt-island -fno-cls-fold` since the subject's DFA artifact has no VM
stamps to read them from) reproduces the pinned region by EQUALITY. Not folded into the other buckets' deny sets
(their meaning is unchanged). Non-vacuity: bucket <= census, and must fire on default/noprefilter.

Verified every one is that mechanism, not an allowance (final run, `KEEP=1`, log `build/scratch/rec3.log`):

| axis | (A) same | differing | ctx-node-moved | (B) |
|---|---|---|---|---|
| default | 1906 | 0 | 264 | 2744/0 |
| vm | 1760 | 0 | 264 | 2745/0 |
| noprefilter | 1907 | 0 | 264 | 2744/0 |
| nocaptures | 1950 | 0 | 264 | 2744/0 |

264 = exactly the 264 that differed before, on every axis (an earlier draft with only `-fno-ctx-node -fno-lit-run`
restored 261; the 3 left were caseless lookbehinds `(?<=(?i)s)x`, `(?<!(?i)s)x`, `(?i)(?<=a)b` whose pin region has the bitmap
compare and whose deny VM build has the ascii-fold `(c|0x20)==N` — the fold axis, unstamped because the subject is DFA. Found
by diffing regions, not guessed). Final trailer `checks passed: 16 / failed: 0`.

Not validated: no sabotage row for the new bucket (S273's precedent: this gate cannot be scored inside `make mech`'s
`git archive` trees — see varland_report finding 7); the non-vacuity arms are the detector. Side finding: 24 awk/sed
"multibyte conversion failure" lines from the vars `\xff` pattern in a UTF-8 locale on darwin; harmless to the verdict (16/0), pre-existing.

## 3. Encoding checks: 9 pass / 7 FAIL -> 11 / 0 (ENC_MAX_BLOCKS=250 default)

Verdict: ALL SEVEN ARE STALE-CHECK, none a DD-12 (7) violation (same class as enctriage). Attribution below is by reading + a
minimal witness per cause; NOT bisected commit-by-commit (the box is loaded, ~10 min per run). Named commits are where the changed
text first appears in `git log -S`.

| # | FAIL (before) | cause | first-bad | class |
|---|---|---|---|---|
| 1 | DD12a(i) SELECT_BAD 3 pairs (`frank\|fred`, `(frank)\|fred`, `fra(n\|m)k\|frost`): REQ_WHY byte "emitted" / utf8 "dominated" | [FINDINGS] B1's COMPARE-NONE is `false`, only identity elides; utf8's NONE pick is the rightmost run member = `r`, which IS the DFA prefilter's `memchr` byte; byte picks the rarer `f`. The check only allowed byte-dominated/utf8-emitted | findb1 c3 `bfb9f8a1` / [FIND-TIE] `ed51481b` | stale rule (reversed direction legitimate) |
| 2 | "228 of 244 strict pairs differ outside regions" | 225 of them: the NEW `<P>_FINDINGS` stamp + `rx_info.findings` (`byte-rate=default:<digest>` under byte, `byte-rate=none` under utf8) — an encoding-keyed stamp value, no region for it | findb1 c7 `8c24a086` (abi 40) | stale (missing region) |
| 3 | "8 K50 manifest rows STALE" | same FINDINGS line: it turned every gate-class pair's "data-only" diff into a TEXT diff, so GATE fell 164 -> 0 and reached rows read as not swept | as #2 | cascade of #2 |
| 4 | "8 pairs entered gate class without a manifest row" (first `(?m)abc$`) | after #2 was fixed, 8 non-nullable pairs (`foo`, `abc$`, `abc\z`, `x\By`, `fo\|foo\|fool`, ...) remain: byte's prior selects `run-pinned`/`memchr` prefilter, utf8's NONE falls to `offset-set` (declared in `RX_DFA_PREFILTER*`). NOT K50 gate pairs (nullable+manifested) | findb1 c5 `51553fa2` ("the B1 utf8 mover") + S1 run-pin rows | stale (unclassified legitimate mover) |
| 5 | "undeclared-form list does NOT match" (7 diverged vs 4 reached) | 3 of the 7 were #1's `frank\|fred` family in the strict bucket; the remaining 4 equal the manifest's reached rows | as #1 | cascade of #1 |
| 6 | region `back_step` never excised | [UCP] U2: a ONE-CHARACTER lookbehind is a context node and emits no `back_step`; every `(?<=a)` witness went vacuous. `-fno-ctx-node` restores `back_step` (grep count 3) | U2 `37af1479`/`7e8ab18a` | stale witness |
| 7 | DD12a(ii) "only 2 residual entries" | same as #6 (`sigpat` `(?i)(?<=a)(b)\1x`) | U2 | stale witness |

Fixes (all in `run_encoding_checks.sh`, each a NAMED, COUNTED, floored region rather than a widened rule):
- `findings_stamp` region (both lines), plus a per-pair coherence arm: byte must carry a real table, utf8 `byte-rate=none` (else SELECT_BAD).
- REQ_WHY: second direction allowed only under identity (utf8's REQ_BYTE must be a byte its own remaining `memchr`s scan); `req_run_asym` excises the whole `rx_reqrun` def+call from both sides when the stamps differ (still compared token for token when they agree).
- `PRIORFORM` bucket: stamp-declared only (byte `run-pinned*`/`memchr*` vs utf8 `offset-set*`, moved stamps limited to the two prefilter ones, FINDINGS coherence), excludes any K50-manifest row, floored at 1 (11 pairs at slice 250). The K50 manifest is UNTOUCHED (its "do not delete rows to go green" rule held; its five reds were #2/#3/#5).
- Witnesses: `(?<=ab)` added to `main()`'s appended patterns and `sigpat` re-aimed (a two-character lookbehind still emits `back_step`).
- Header comment of the REQ_WHY section rewritten (was "ONE direction only").

Result (final run, log `build/scratch/enc4.log`): `checks passed: 11 / failed: 0`; gate-refinement class 15 pairs (10 data + 5 form), undeclared-form list 4 reached matched EXACTLY, 245 strict pairs (235 identical, 10 data-only), DD12a(ii) 3 entries.

## 4. Owed / caveats
- `ENC_MAX_BLOCKS=0` (whole corpus, a Linux slot per the script) NOT run; the 141 manifest rows unreached at slice 250 are unchecked here. `PRIORFORM` has a floor but no ceiling (its population is corpus-derived; a ceiling would decay).
- No sabotage rows for the four new regions/tiers; the floors and coherence arms are the detectors (see K35).
- `docs/dev/plan.md` row [K50-DD12AI-MANIFEST]: its reds (4)/(5) and three of its first three are explained here (FINDINGS stamp); the manager may want a one-line pointer (not edited: plan.md is the manager's).
- Scratch in `build/scratch/` (gitignored). I wrote two logs to `/tmp` before noticing the scratch rule; deleted.
