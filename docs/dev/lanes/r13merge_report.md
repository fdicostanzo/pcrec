# Lane r13merge: main a15fb77b merged into R-13 (report)

Lane r13merge, branch `lane/r13merge` cut from `lane/memfn-r13` @ b8cc6c8b,
2026-10-10. Task: merge main @ a15fb77b (R-12 VMLAZY landed, SPEC-CLEAN's
numbered facts-only specs) into R-13 (batch 1 vrun-w16/vrun-w32 + rankuse's
vrun-kb) and resolve. Merge commit 5256d235. No pcrec emitted byte moves:
R-13 is SIMD-off byte-identical, and the generated provenance line reads
`abi 72`, as on main.

## 1. Conflicts and their resolution

| file | resolution |
|---|---|
| `Makefile` | TEST_SECTIONS keeps both: `test-memfn-simdfloor \`, `test-memfn-rank \`, `test-spec-history` (continuations checked). Each target is defined once; `.PHONY` already listed all three. |
| `docs/dev/lanes/CLAUDE.md` | union: R-13's `rankuse_report.md` line, then main's 13 lines (specclean … sstri). |
| `memfn/docs/journal.md` | union in time order, no entry lost: main's 10-09 evening (pause), main's ~17:15, R-13's ~19:20, main's slot17 read, R-13's night (rankuse), R-13's 10-10 ~00:40 close, main's 10-10 slot19. |
| `memfn/docs/responses.md` | union, no entry lost: main's two 10-09 R-12 entries (N7U notice, slot17 done), R-13's two notices (10-09, 10-10), main's 10-10 R-12 re-landed done. |
| `docs/spec/limits.md` | main's structure; R-13's facts as new §8.3¶3 (below). |
| `docs/spec/registry.md` | main's structure; R-13's rows as §6¶8a, the floor literal as §6¶8b; §6¶8's "no option at present" sentence rewritten (code wins). |
| `docs/spec/tuning.md` | main's structure; R-13's §2.43 text as ¶3a/¶3b; ¶4's "Inert in this build" sentence rewritten (code wins). |
| `docs/spec/match_api.md` | main's file taken whole (the conflict spanned the rewritten region); R-13's three hunks re-applied in §6.3.10. |

Also edited: `tests/registry/axes_registry_check.sh`'s comment now cites
`registry.md §6¶8b` (where the floor literal lives), not §6¶8.

History: every `docs/dev/history/*_record.md` is FROZEN (history/CLAUDE.md), so
R-13's narrative ("born with R4e' batch 1", "[MEMFN] R-13, 2026-10-09", "lane
rankuse", "R4d has not landed", "since R-13") is DROPPED from the spec, not
moved. It is already recorded in `r13_report.md`, `rankuse_report.md`, the kit
journal and responses.md.

## 2. Per-hunk tables (R-13 = `git diff ebcba013 b8cc6c8b`, the merge base to R-13's tip)

### limits.md

| R-13 hunk | now |
|---|---|
| stamp reads `0` at the default `-fno-memfn-simd` | §8.3¶3 (main's §8.3¶2 had only the generic "`0` on an artifact with no guarded block") |
| nonzero exactly where a SIMD row rendered: the `vrun` rows over a FUNC whose predicate is one run | §8.3¶3 (cites `registry.md` §6¶8a for the rows) |
| ≤ 2,700 B per FUNC `vrun-w16`, 2,800 B `vrun-w32`; `tests/memfn/simd_bounds.tsv` states each row's bound, measured over the kit's generated site space | §8.3¶3 (values checked against simd_bounds.tsv: 2700/2800) |
| "What this means for the caps" text (guarded total, `SIMD_GUARDED_BYTES`, no aggregate budget, sum of bounds) | already absorbed by main at §8.3¶2 |
| "([MEMFN] R-13, R4e' batch 1 …)" provenance | dropped (history; files FROZEN) |

### registry.md

| R-13 hunk | now |
|---|---|
| independent control = member-count floor literal, no shared source, raised per row; UNREACHED with no row; FAILS a row with no floor | already absorbed by main at §6¶8; its "the kit defines no option at present, so … no floor is pinned" sentence replaced by the check's behaviour as a fact |
| `vrun-w16`: `deny`, layer `simd`, budget `scan`, `--memfn=no-vrun-w16`, the 16-byte vector run scan on a one-run FUNC (`tuning.md` §2.43) | §6¶8a (table) |
| `vrun-w32`: same form a level up; short spans fall to `vrun-w16`; denied → `vrun-w16` is the top arm | §6¶8a |
| `vrun-kb`: `deny`/`simd`/`scan`; second filter position from the rarity ranking (`mf_pred.rank_*`, D157); denied → scanned position alone | §6¶8a |
| `` `memfn` section floor: 3 `` | §6¶8b, label-prefixed; `axes_registry_check.sh`'s `sed` reads `3` from it (verified) |
| "EMPTY at R4a", "BORN with the first rows … R-13, 2026-10-09; R4d … has not landed", "lane rankuse, 2026-10-09" | dropped (history; files FROZEN) |

### tuning.md (§2.43)

| R-13 hunk | now |
|---|---|
| heading-paragraph: "`-fmemfn-simd` renders the kit's first SIMD rows; the default renders exactly what it rendered before" | §2.43¶4 (rewritten from main's "Inert in this build: no SIMD form exists", which R-13 makes false) |
| "OFF BY DEFAULT until the SIMD hold lifts; turning it on by default is its own ruled event" | already absorbed by main at §2.43¶1 ("default OFF"); the ruling clause is history, dropped |
| "What ON renders today": one-run FUNC, 2-32 B, two-member cube, sole predicate, `<fn>__body`, `#if/#elif/#else` selector, `-march` picks the arm (SSE2 / AVX2 / scalar), short spans fall through, answers never change, `MEMFN_FORMS`/`SIMD_GUARDED_BYTES` | §2.43¶3a, plus the CANDIDATE / no-speed-claim status |
| per-form switches `--memfn=no-vrun-w32` / `no-vrun-w16` / `no-vrun-kb`; a SIMD deny at `-fno-memfn-simd` accepted and does nothing | §2.43¶3b |
| C11 identity + movers halves (`make test-memfn-stamps`), C18 (`make test-memfn-simdfloor`) | §2.43¶4 |
| per-form switches are the kit's `--memfn=` namespace (`registry.md` §6); masked out of `rx_info.flags`; stamp `MEMFN_FORMS` `none` iff identical | already absorbed by main at §2.43¶4 |
| "(R4e' batch 1, [MEMFN] R-13 …)" provenance | dropped (history) |

### match_api.md (§6.3.10)

| R-13 hunk | now |
|---|---|
| `MEMFN_FORMS` is `"none"` at the default; at `-fmemfn-simd` names the SIMD rows, one token per FUNC, site order (`vrun@w32+w16`); levels are the RENDERED ones top-down, never the live one (x86-64 default runs w16, `-mgeneral-regs-only` scalar) | §6.3.10¶4 (main's "no SIMD form exists … today" replaced) |
| "bucket on `none`/not-`none` … ids and level tokens are opaque" | already absorbed by main at §6.3.10¶4 |
| C11's movers half LIVE: an ON compile equals the default exactly where `MEMFN_FORMS` reads `"none"` | §6.3.10¶7 (main's "stays unreached until one does" replaced) |
| `SIMD_GUARDED_BYTES` zero at the default; nonzero where `MEMFN_FORMS` names a SIMD row | §6.3.10¶9 (main's "no SIMD form exists and `-fmemfn-simd` is inert" replaced; cites `tuning.md` §2.43¶3a and `limits.md` §8.3¶3) |
| "is LIVE since R-13", "while no SIMD form existed" | dropped (history; "since `[TAG]`" is a spec-history marker) |

Citations: R-13's citations elsewhere in the tree (`tuning.md §2.43`,
`registry.md §6`, `match_api.md §6.3`, `limits.md`) all resolve; `make
test-spec-history`'s [cites] arm passes on every numbered doc.

## 3. Validation (pinned `taskset -c 12-15`, `-j4`; logs under the session scratchpad `val/`)

Verdicts read from make's `*** [...] Error` lines
(`grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'`) plus each section's own
passed/failed total.

| run | start | end | verdict |
|---|---|---|---|
| `make -j4` | 05:23:35 | 05:23:38 | rc 0 |
| `make strict` | 05:23:38 | 05:23:49 | rc 0 |
| `make test-registry` (first) | 05:23:49 | 05:24:39 | **RED**: `axes_registry_check COVERAGE CHANGED — 217 passing checks, expected 216` (§4) |
| `make test-registry` (after the §4 re-pin) | 05:30:59 | 05:31:49 | green, no Error lines, checks 79/0 |
| `make test-codegen` | 05:24:39 | 05:27:53 | green, run_group 15/15 scripts |
| `make test-memfn-simdfloor` | 05:27:53 | 05:28:19 | green, 51/0 |
| `make test-memfn-rank` | 05:28:19 | 05:28:29 | green, 11/0 |
| `make test-memfn-arch` | 05:28:29 | 05:28:37 | green, 15/0 |
| `make test-memfn-stamps` (C11, the SIMD-on/off identity halves the spec now states) | 05:28:37 | 05:28:55 | green, 25/0 |
| `make test-memfn-guarded` (the `SIMD_GUARDED_BYTES` bounds) | 05:28:55 | 05:30:17 | green, 10/0 |
| `make test-spec-history` (spec edits only, before the report) | 05:23:23 | 05:23:26 | green, 145/0 |
| `make test-spec-history` (final tree, report included) | 05:32:05 | 05:32:08 | green, 145/0 |

## 4. The one red: a coverage pin R-13 never raised

`tests/registry/run_registry_tests.sh` pins `axes_registry_check.sh`'s PASS
count. Main, R-13 and their merge base all pin 216. On main the `[memfn floor]`
arm prints UNREACHED because there are no kit rows. R-13 added three rows
and the `` `memfn` section floor: 3 `` line, so the arm prints `PASS: [memfn
floor] 3 row(s), floor 3`, which makes 217. R-13's own tip carried the same stale
pin, so this miss predates the merge. Re-pinned 216 -> 217 at all four sites,
with a cause comment in the file's convention. No other PASS line moved
(0 UNREACHED lines remain).

## 5. Seen, not changed (outside the merge)

These comments still say "no SIMD form exists". Each one was already on
R-13's tip, and none of them is spec text:
`lib/pcrec.h` (the `PCREC_NO_MEMFN_SIMD` comment), `src/dump/axes_dump.c`
(the memfn-simd row comment) and `tests/memfn/libc_census.py` (two
comments). Editing `lib/pcrec.h`/`src/` comments is a kit-branch follow-up,
not this merge's job.

Not run (forbidden by the brief, heavy): full `make test`, `make test-axes`,
emit_sweep, `make test-memfn-g2`, mech. R-13's own slot18 still owes them.
