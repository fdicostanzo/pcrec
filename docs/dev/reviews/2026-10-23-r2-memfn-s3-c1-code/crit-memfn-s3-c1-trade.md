# crit-memfn-s3-c1: trade audit and check adequacy (D172 S3, BASE c3ea619c3 .. SUBJECT ae83da9d4)

Disclosure: I read only the review tree plus main's guide inputs. I did NOT open s3_report.md, results/605 tables, the other denylisted files, or journal/responses. Commit subjects in BASE..SUBJECT scrolled past in `git log -12` (they name job 605 / C1 ordering); I use only the ordering. I ran single compiles with build/pcrec, no timing, no suites.

## Trade table (every pin/floor/count/manifest the diff moves)

| pin | old | new | cause stated? | trade judged by? |
|---|---|---|---|---|
| tests/memfn/simd_floor_check.py MOVERS_FLOOR / SIMD_FUNC_FLOOR | 39 / 39 | 46 / 46 (33 in between) | yes (comment: lowered to 33 at S3, "a trade never judged", raised again by r1 C1) | net RAISED; the intermediate lowering was caught by code review r1, not by a person judging it |
| simd_guarded_check.py 'simd-form' | 5 | 6 (3 between) | yes | same |
| emit_sweep DIFFER_PINS `-fno-offset-skip` c-default byte / utf8 | 513 / 604 | 328 / 376 | yes (cover artifacts leave the start family; armcause.py) | lane s3fix600 (job 600), no named human |
| `-fno-run-prefilter` byte / utf8 | 127 / 3 | 54 / 2 | yes | lane |
| `-fno-req-handoff` byte / utf8 | 339 / 519 | 226 / 349 | yes | lane |
| `-fno-req-run` stamp byte / utf8 | 208 / 79 | 102 / 58 | yes | lane |
| `-fno-req-run-fold` stamp byte / utf8 | 32 / 31 | 26 / 27 | yes | lane |
| `-fmemfn-simd` c-default byte / utf8 | 20 / 15 | 9 / 10 | yes, but MEASURED AT ba6ebf720, BEFORE the r1 C1 build that restored caseless SIMD (see F2) | lane |
| `--memfn=no-pres-set-lead` byte / utf8 | 16 / 8 | 14 / 7 | yes | lane |
| `--memfn=no-fd-pres-g1` byte / utf8 | 1271 / 1105 | 944 / 873 | yes | lane |
| `--memfn=no-fd-pres-pick` byte / utf8 | 188 / 263 | 167 / 231 | yes | lane |
| manifests re-chosen: `ab`->`ab+`, `fi`->`(ABC)`, `\Bx`->`(\b)x`, `SS`->`ab?c`, `123`->`ab?c`, `(?i)cat`->`((?i:abc))`, `aa(?i:a)`->`frank|fred`, `é{2}cat`/`a{3}(?i:cat)`->`x{2,5}(?i:cat)`, `ab`->`a+` | n/a | n/a | yes | lane |
| run_start_landing.sh FLOOR_EMW / FLOOR_PROD | 1124 / 1290 | 510 / 705 | yes, "pinned AT the measure" | lane. A LOWERED REACH floor of 54% / 45%: end-minus-width and the product arm now reach about half the corpus on the default path |
| rank_check.py DOOR_CBM_FLOOR | 1400 | 1179 | yes | lane |
| run_libc_census.sh funcs | 169 | 141 | yes (no offset-skip function for fixed-width) | lane |
| run_g2_win.sh FORM_FLOORS wf-floor | 740 | 486 | yes (sites moved to wf-find, which is new at 630) | lane. Floor sits AT the measure, not 10% below |
| run_g2_win.sh FLOOR_SITES / CONTROLS | 1500 / 23 | 2200 / 104 | yes | RAISED |
| run_g2_win.sh FORM_FLOORS generic / pf_memchr / ofsskip | 355 / 210 / 26 | 380 / 215 / 27 | yes | RAISED |
| EFIND_FLOORS (new) | - | libc 320, walk 195, hors 110, run 115, below 95, report 370, refused 17, pair 125, fn 48 | yes (about 90% of measured) | n/a |
| m5_stage1_stamps.tsv (4 rows) RX_DFA_PREFILTER, EMITTED_BYTES | memchr, run-pinned, offset-set-bounded, handoff; 21348, 22179, 25144, 25544 | "none"; 18944, 19267, 20690, 21700 | yes | lane. Size falls, so a gain |
| mech: S922, S1251-S1256, ZK6, ZK7 retired | present | gone | yes (the preview they planted retired) | structural, with named successors S1422/S1423 |
| mech S283 | SAB_EXPECT DETECTED | **UNDETECTED** | yes (plant moves no artifact even at BASE) | lane s3fix600 alone. A mutation row given up |
| mech S284 | UNDETECTED | DETECTED | yes | gain |
| tests/startset/manifests/manifest_s3_dfa.tsv | -25 rows (lookaround/assertion fixed-width hat movers) | removed | yes | lane. Rows no longer witness anything on the default path, and nothing re-adds them under the deny |
| row_floors.tsv | RPT row | PAIR row with PLACEHOLDER/PLACEHOLDER | yes | PAIR has no floor (UNREACHED by design) |
| job 588 bar: foobar match/real cap | none (floor only) | 1.052 | yes (layout effect; 605's 1.032 plus 0.020) | "the manager's cap, 2026-10-23" after the measurement |
| CAPS hex8-bounded throughput/dense | n/a | 1.551 (users ~1.53x slower on all-hex dense bulk) | yes (window_site.md §6) | kit manager + Frank on hex8 ("judgement call") |
| cli/run_cli_tests.sh, run_offset_skip, runcmp, reqcube, prechecks, scan_edge_census, wreply, facts, search_pinned, anchored_match, codegen, c10, pres_pick, cand_oracle ... | witness on default path | witness under `--memfn=no-wf-find` | yes, uniformly | lane. See F1 |

No performance-FORM floor (SIMD count) ends lower than BASE. The only lowered floors are reach/population floors (EMW, PROD, DOOR_CBM, libc funcs, wf-floor), each stated and each a consequence of ~800 patterns leaving the old machines, but nothing records that anyone judged the loss of old-machine reach against the speed of the new machine for those patterns.

## Findings

### F1. CONFIRMED, medium/high, effort M, blast radius ~800 corpus patterns plus every user of the deny: the old machines now have no corpus-level answer or reach check
The commit re-aims about 40 witnesses and checks to `--memfn=no-wf-find`. A grep of tests/ and scripts/ for `no-wf-find` shows hand-picked witnesses only. The corpus answer-identity sweeps (emit_sweep streams, `make test-axes`, harness, the .rxt corpus) never compile the corpus under the deny. The old unanchored scan, end-minus-width, byte-class prefilter, offset-set, handoff and run-pinned paths still ship behind the user-visible deny (registry.md §6¶8a), and they are also the fallback when `cover` declines (C-table rows). Their only remaining population is whatever cover declines naturally plus a few dozen witnesses. A defect in those machines for a pattern that is now cover (for example a `\bword\b` or `[ab]\b` shape) would pass `make test` entirely. Repro of the gap: `grep -rn no-wf-find tests/axes scripts/emit_sweep.py Makefile` finds nothing.
Fix: one `--memfn=no-wf-find` answer-identity pass over the cover movers (the 804 the census already lists), same oracle as the corpus.

### F2. CONFIRMED, medium, effort S, `make test-axes` red: memfn arm population is stale
`pcrec --list-axes` now prints `wf-find` and `wf-hors` (checked: lines 218-219 of the subject binary's output; list_axes_delta.tsv declares them). tests/axes/memfn_arm.py asserts `set(spelling) == {k[0] for k in MEMFN_CLASS}` (line 232) and MEMFN_CLASS has no `wf-` key; `git diff --stat BASE SUBJECT -- tests/axes` is empty. So the opt-in `make test-axes` memfn arm must fail on population, and run_axes.sh has no cell for the new rows. `make test` does not run it, which is why the delivery looked green. Rule: BOILERPLATE "RE-PIN EVERY MANIFEST YOUR CHANGE MOVES". Also, `--memfn=no-wf-find` and `no-wf-hors` have never had a DIFFER class and floor measured, so the deny rows have no reach witness in the axes tier.

### F3. CONFIRMED (code), medium, effort S: the bar's per-row and per-cell sample FAILs do not fail the bar
read_588.py `sample_fails` receives only dropped rows and stratum geomeans. Cells above 1 + floor go to `slow`/`rowfail` and are printed as FAIL but never reach `sample_fails`. The header and window_site.md §6 say "every sample row and cell printed PASS/FAIL", which is true, but a single row 2x slower in one regime and class (about 5 of 36 cells in a 5-pattern stratum shift a gmean by about 2%) passes the bar if the stratum gmean is within 1 + max A/A. Floor = the largest |RT2/RTE - 1| over §6's 24 cells in that regime, so it is the worst noise seen, not a typical one.

### F4. CONFIRMED (code and data), medium, effort M: the mover sample does not represent the movers by shape
Pool: 804 cover movers, but pick_588.py keeps only patterns for which `gsp.compiles` succeeds: `pat.isascii()`, no `\z`/`\Z`, python `re` can parse, and gen_sample's `_gen` can generate a match (backrefs, conditionals and unsupported ops return False). The header records "generatable" 153+136+5+85+12 = 391 of 804, so 51% of movers can never be sampled. Specifically absent from the sample by construction:
- high bytes and utf8: the patterns are ASCII only, compile is `-p rx` byte base (no `-e utf8` arm at all), subjects are printable ASCII + newline. DIFFER_PINS shows utf8 cover movers are hundreds (376 `-fno-offset-skip`), and utf8 prior is NONE so its pick (rightmost member) differs from byte's (rarest). None timed.
- wide windows: `.{3}cat` (6) and `ABCDEFGH` (8) are the widest drawn; G2 stops at k<=8 too; MF_WSPAN_POS is 32 (`\d{4}-\d{2}-\d{2}` is 10, `[0-9a-f]{8}-...` longer). Strata are not width-aware.
- class windows with many members or ranges: strata are only B form (LIBC/WALK) x D x C-run. The WALK/one/norun draws are `[a-]`, `[:a]`, `[[:]`, `(?:(?!a)z|w)`, i.e. two-member sets and one lookahead. The cover class form is a branch chain per byte (`\w`: 4 range tests; `[aeiouAEIOU]`: 10 equality tests; `\W`: 5 tests; compiled and read from the subject binary). Where the old route was a table scan or byte-class prefilter this is a possible loss; nothing times it.
- regime `match`: sample regimes are throughput and search_short only (SREGIMES), yet 605's own failing cell was a `match` LAYOUT effect (foobar match/real, rx_match byte-identical, placement moved). The 24 sampled rows get no layout check.
- the `none` class is dropped wherever the prose itself matches, which removes exactly the frequent-match rows (`...`, `..`, `[^abc]{2,4}?`, `\w\B\w`), leaving real/random only for them.
- the cells in §6 (cells.tsv) are 8 ASCII shapes: `abcdefgh`, `\d{4}`, `\.tar|\.tar\.gz`, hex8, `foobar`, `\bcat\b`, `(?m)done$`, `\w(?=\d)\w`. No caseless, no single byte, no two-value non-case class, no high byte, no utf8.
Concrete patterns that could regress unseen: `\w{1}x`-shaped single-class windows over sparse input, `[aeiouAEIOU]`, `[^a]`, `(?i)a`, `é` / `\xe9` / `[\xe0-\xef]` (memchr on a high byte on utf8 text where that byte is dense), `[0-9a-f]{40}`, `(?i)x/1234` style caseless runs under `-e utf8`.

### F5. CONFIRMED, medium, effort S: acceptance evidence predates the C1 build for the caseless movers
Commit order in BASE..SUBJECT: the job 605 RESULT commit (8671624a4) precedes the r1 C1 commits (d190e3a70, b5b85aeac), which changed how every caseless window is rendered (PAIR stop, `_ofsskip` function; `(?i)cat` now compiles to `rx_mf1_ofsskip(...)`, verified). Job 588 as scripted (s3_job_588) builds from the S3 commit named in the report, and its sample is picked from the cover movers of the compiler it is given, so it can cover C1 only if it is re-run at b5b85aeac. Likewise DIFFER_PINS were measured at ba6ebf720 ("the S3 tree"), and those `-fmemfn-simd` / start-family numbers are floors that C1 moved. Worth confirming 588 and the sweeps ran at the C1 build, not 605-era.

### F6. SUSPECTED, low/medium, effort S: DIFFER_PINS for `-fmemfn-simd` are stale-low floors
Measured pre-C1: 9 / 10 movers. Now `foobar`, `abcdefgh`, `(?i)cat`, `(?i)x/1234` all differ under `-fmemfn-simd` on the subject binary (compiled and cmp'd), so the true count is probably well above the pin. A floor that sits far below the measure catches a 50% loss silently; the `(?i)cat` manifest was swapped to `((?i:abc))` for a reason that C1 removed. `learnings.md §3`: a pin that tracks no population.

### F7. SUSPECTED, low/medium, effort S: controls that share a source with what they control
- census.py declares the mover population from NEW's own `RX_DFA_SCAN "cover"` stamp and then asserts cover artifacts must move. The OFF-arm-zero-movers check against BASE's binary is independent and is what keeps this honest; the bytediff.sh PREDICTED manifest is the author's own list of 45 patterns against a population of 804.
- the DEF arm of job 588 is "byte-identical to main" but proven only on bytediff's 45 rows, not on the 24 sample rows or the 8 cells (job 587's census OFF arm covers the corpus: acceptable, but 588 does not re-read it).
- g2_win_gen's REPORT-refusal predicate is hand-written from `ref.has_stop` and the frame, OK as an independent reference; the `ef_*` population counters are `strstr` on the kit's own output, which counts reach, not a verdict (fine, labelled).
- run_cand_oracle.sh now prints UNREACHED for `[cand-oracle-shipped]`: honest.
- PASS_CONFIGS `kit-proof` pass (tests/memfn/site_census.py) is now a duplicate of `default` (lever inert), so its counts double-count; not a miss.

### F8. SUSPECTED, low, effort S: G2's alphabet cannot reach a high-byte skip table
ALPHA = {a, A, b, c, 0, 1, \n, x}. The D-hors dense stream draws only from it, so `_sh[256]` indexing by a byte >= 0x80 (signed-char bug class, `é` windows) is not generated by the dense stream. The caseless stream adds one 0xC4/0xE4 cube but never a dense site. Plants S1423/S1425 (bound and shift value) are caught; a signedness plant is not offered.

### F9. SUSPECTED, low, effort S: row_floors.tsv reach floors for rows S3 starves are untouched
`fd D1/D1c/D1w/R7w/P0...` and `arms pf_memchr/ofsskip` floors came from the N2 census (a35ca8f90); ~800 patterns left those rows' sites. Only RPT/PAIR lines changed. If the floor check runs against the full corpus it either reads another population or is now silently looser; no re-measure is recorded.

### F10. CONFIRMED, informational: S283 flipped to UNDETECTED
Documented, measured at BASE too, so S3 is not the cause; but the matrix lost a detector with one lane's judgement and no named reader. A dead bit (`PCREC_NO_OFFSET_SKIP` in the run-row mask) stays in the tree.

### F11. User-visible semantics given up (informational, spec'd)
`-fno-offset-skip`, `-fno-run-prefilter`, `-fno-req-handoff`, `-fno-req-run*`, `-fno-start-set` are inert on about 130-185 corpus patterns each (the DIFFER_PINS drop). The replacement deny is `--memfn=no-wf-find` (registry.md §6¶8a).

## PROBED-AND-HELD
- Performance-form floors (SIMD counts) end at or above BASE.
- G2 floors were raised, and plants S1422-S1429 each name a mutation tied to a population counted by EFIND_FLOORS (pair, fn, hors, run, below).
- ABI bump 83->84 re-pinned (run_codegen_tests ABI_EXPECT=84), bytediff mask `abi 8[0-9]`.
- cand_oracle: `cover` witnesses compile without the lever and a UNREACHED line replaces a would-be pass.
- K27 NULL-subject runs on both arms with a "deny arm still renders cover" negative guard.
- run_wordctx_identity: the cover non-difference is PROVED (the deny arm must differ) so the bucket cannot absorb a dead knob.
- wf-floor falling 740->486 is explained (sites moved to wf-find 630), not a loss.
- EMITTED_BYTES shrank on 4 stamped rows: a size gain, stated.
- rows.tsv: ROWS_FLOOR unchanged because RPT out and PAIR in; PAIR witness `(?i)foobar` with control = same pattern under the deny.

## Effort/severity summary
F1 (M, medium-high), F2 (S, medium: opt-in `make test-axes` red), F3 (S), F4 (M), F5 (S, confirm run order), F6-F9 (S, low), F10-F11 informational.
