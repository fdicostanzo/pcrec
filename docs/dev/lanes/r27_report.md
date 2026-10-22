# r27: R-27.1, a REPORT site that is not slower than the default build on candidate-free text (DESIGN ONLY)

Lane r27, 2026-10-21. Branch `lane/memfn-r27`, cut from main `9fe7d47cf` and taken at `cf5909eb1`.
Request: `memfn/docs/requests.md` "## R-27", item R-27.1. Evidence: `docs/dev/lanes/covertime_report.md`
(the 650 harness, `docs/design/kit_proof/measure/`). Rulings file `r27_rulings.md`. The last entry
applied is the kit manager's ruling on the design ("R-27 is the D161 window search ... Do NOT add a
REPORT-only skip ... design only").

**Verdict: DESIGN ONLY. There is NO BUILD GO.** The brief quoted no go, so I asked for one, and the
rulings file then confirmed none exists. Nothing under `memfn/src`, `src/`, `cli/` or `lib/` changed.
The lane delivers:
- the design, and which existing rows qualify under RPT's exactness rule (sections 2 and 3);
- the soundness argument (section 4);
- one timing job of the PROPOSED text, rendered by hand into copies of the harness's own cover
  artifacts and run over the 650 harness unchanged (section 5);
- the build plan and its checks for the lane that gets the go (sections 6 and 7).

## 0. Questions for the kit manager

- **Q1 (the deny).** D144 item 4 says a byte-moving kit change carries its own `options.def` row.
  This change moves bytes only on a preview art (`mf_preview("R-26.6")`, harness builds). On a
  default build RPT is unrouted and nothing moves. r26zk's Q4 left RPT without a row, because B1's
  OFF arm is pcrec's fact deny `PCREC_NO_KIT_PROOF`.
  - My leaning: no new row. The extended verify chain and set scan (E1/E2 below) are rows that
    already exist. Their default-build sites state no `ctx` and name pcrec's tables, so their text
    does not move.
  - If you want a row for the alpha OFF arm, it brings these readers with it: `tests/axes/memfn_arm.py`,
    `tests/cli/run_cli_tests.sh`, `docs/spec/registry.md` §6's floor, and `tests/memfn/rows.tsv`.
- **Q2 (the tie rule for the stop).** P3's port breaks a mass tie toward the RIGHTMOST position.
  For this form the loaded-box probes read the rightmost tie about 1.4x DEF on year4 and 1.25-2x
  on hex8, and the leftmost about 0.9x. The proposed text breaks ties LEFTMOST. That is a kit
  choice (D157), and job 580 measures it.
- **Q3 (the failure shift, E4).** E4 is new arithmetic, not an existing row. Job 580 measures it as
  arm SHF. It is the only candidate found so far for hex8's `search_short` loss. If SHF does not
  clear the bar there, then hex8-bounded is a cell where no qualifying form beats DEF. Under the
  K96 rule, RPT would then fall back to the composer's form, and the cell stays SLOWER.

## 1. What is slow today (artifact reading, `build/r27/base/arts/*/COV/a.c`)

On every one of the 8 cells, RPT's pick is the composer's walk (`fd_nested_walk`). The arms walk
picks the generic row for the cover site, because the site pcrec states is this:
- STMT / ASSIGN;
- k SET terms at offsets 0..k-1;
- `plan_hint` MF_NO_PRED, no `table_ref`;
- one or two `ctx` items.

ofsskip, pf_memchr, pf_walk and precheck all decline it. The generic row's text is
`for (c = lo; c < n; c++) if (CONJ(c)) break;`. It tests every term at every position, and each test
carries its own bound check. It has no stop search: there is no memchr and no table walk.

The default build's site for the same pattern is pcrec's prefilter, one of two shapes:
- lit-l8, foobar, file-ext-order, cat-bounded and done-eol: an ofsskip FUNC. It runs memchr on
  pcrec's ranked byte, then a run compare.
- year4, hex8-bounded and word-digit: pcrec's start-byte table walk in front of its DFA.

## 2. Which EXISTING rows qualify (the ruling's question)

RPT's exactness rule (`kit_report_exact`): the chosen row's class must prove, at every
d in [MF_PROOF_LO, MF_MAX_FWD), exactly the intersection of the REQUIRED sets. Those are span 0's
terms and every `ctx` item. So a row qualifies only if it TESTS every span-0 term and every `ctx`
item at every candidate it yields.

| row | what it tests / needs | on the REPORT site as stated | qualifies on |
|---|---|---|---|
| pf_memchr, pf_memchr_bounded | one SET term, one byte, offset 0 | k > 1 terms: it tests one, so proven[d >= 1] is all ones and not the REQUIRED set | none of the 8 (only a k = 1 site with no ctx) |
| pf_walk, pf_walk_bounded | one SET term over pcrec's TABLE (`table_ref`, `table_name`) | k > 1 terms; no table is named | none |
| precheck (3 rows) | ALL_PRESENT, a presence gate, not a FIND that yields candidates | the op is FIND | none |
| ofsskip (fn-memchr, fn-pair; vrun PREFIX at SIMD) | FUNC/RETURN, miss n; `plan_hint` naming a ONE-BYTE scan position; multi-byte SETs only through pcrec's tables; at most one RUN; offsets >= 0; contract `ctx` NONE | plan_hint unstated; no tables; STMT form; ctx items on 4 of the 8 cells | none as stated |
| ofsskip, with RPT re-describing span 0 (the plan_hint = the rarest one-byte position; consecutive one-byte SETs as one RUN term for the run compare) | as above | lit-l8, foobar, file-ext-order: no ctx, every position one byte | **3 of 8** |
| generic (the composer's form) | every term and every ctx item | exact everywhere | 8 of 8 (today's pick) |

**Reading.** If only existing rows qualify, the fast form reaches the three literal cells. The other
five stay on the generic row:
- cat-bounded and done-eol: their ctx items are not tested by any search row;
- year4, hex8-bounded and word-digit: no one-byte stop, and no pcrec table for a set walk.

On today's numbers four of those five read SLOWER. Only word-digit is already FASTER. The bar is not
met by existing rows alone.

## 3. The design: the D161 window search, built from the existing rows plus two extensions

RPT's pick becomes the window search over span 0: **search a cheap stop, then test the rest.**
- **The stop.** The span-0 position d* whose set S_d* has the least mass under the art's
  `byte-rate` analysis kind (presence.c's `set_mass`; cardinality where no table is given). A tie
  goes to the LEFTMOST position (Q2).
- **The stop's search** is the finder's own FIND rule for one position:
  - one member: the libc search (D1's form, memchr);
  - a set: the WALK. This follows Frank's 2026-10-21 ruling, "the walk when the subject is not
    known", so no V1/M64 anywhere.
- **The rest:** ofsskip's verify chain over every other span-0 position and every ctx item. A
  failed candidate resumes at c + 1.

This is ofsskip's form: one stream on the scanned position, then the verify chain, resume at
cand + 1. It needs these extensions, each to an existing row and none REPORT-only:

| ext | row | what | why the 8 cells need it | default-build movers |
|---|---|---|---|---|
| E1 | ofsskip's scan | a multi-member scan position searched by the WALK, testing the set with the kit's own range test where pcrec names no table (the generic row's `set_test`, rule 6) | year4, word-digit, hex8 have no one-byte position | none: every default ofsskip site scans one byte (ofs_fn_applies requires it) |
| E2 | ofsskip's verify_chain | (a) `ctx` items tested under their `absent` rule (the generic row's `ctx_pred_test` text, one rendering); (b) a multi-byte SET tested with the kit's own range test where no table is named | cat-bounded, done-eol, hex8 carry ctx; year4, hex8, word-digit verify sets with no table | none: default sites state `ctx` NONE and name tables (contract `ctx` CM(NONE) today) |
| E3 | RPT | re-describe span 0 for ofsskip: the stop as plan_hint/plan_pos, consecutive one-member SETs as one RUN term (the run compare, runcmp.c), FUNC with the site's stem (`fn_ref`, which pcrec states when it names a stem) | the literal cells' word compare; file-ext-order at c + 1 needs it (below) | none: RPT is unrouted |
| E4 (measured, Q3) | the verify chain | the FAILURE SHIFT: a failed test at offset j resumes at c + t, where t is the least t >= 1 with S_{j-t} not a subset of S_j, or j + 1 if none | hex8 `search_short` (prose is dense in [0-9a-f], and re-testing a short hex run from c + 1 is the loss) | none (RPT only) |

Once E1 and E2 land, ofsskip's contract widens. `ctx` and `absent` become served, and a set scan
position without a table becomes served. RPT then picks ofsskip wherever kit_report_exact holds,
which by section 4 is every site where these rows test every REQUIRED term. The composer's form stays
the fallback, for a site the widened row still declines (a stated `floor`, a `reverse` site, more
than one RUN term).

**Text shape matters, and was measured (loaded box, direction only).** These shapes were tried:
- The rest tested as ONE `&&` chain, followed by `c++` (ofsskip's own `if (chain) return cand;
  pos = cand + 1;`), read about 0.9x DEF on year4.
- The same tests as separate branches, each with its own `continue`, read 1.2-1.8x.
- A chain with a per-term bound check read 1.5-1.7x in half the samples.

The proposed text is the single chain with one bound test, `c + k > n`, ahead of it. E4 needs
separate branches, so it pays that shape cost wherever its shift does not win back more (SHF in
job 580).

**The literal cells need the run compare (E3).** file-ext-order's stop `.` occurs once per path
line. Seven byte compares per stop read 1.6-2.0x DEF on `none`. One `memcmp(s + c, ".tar", 4)`,
which gcc inlines as one 32-bit compare, read 0.9-1.0x. That is DEF's own verify.

## 4. Soundness: the stop and the shift remove only positions that cannot be candidates

Notation:
- A candidate c is a position in [lo, n) where CONJ(c) holds. CONJ(c) is every span-0 term,
  under its bound c + off + len <= n, AND every ctx item under its absent rule.
- The generic row yields the least such c, or the miss value if there is none.
- Let K = max over span-0 terms of off + len. Let S_d be the intersection of the span-0 terms' sets
  at offset d, for 0 <= d < K. Every span-0 offset is >= 0 on every REPORT site pcrec builds
  (offsets 0..k-1); the row declines any other site.

The claims:

1. **The bound.** CONJ(c) implies c + K <= n. So once c + K > n holds, it holds for every c' >= c,
   and no candidate lies at or after c. The search may return the miss value.
2. **The stop.** CONJ(c) implies s[c + d*] is in S_d*. A position c with c + d* >= n, or with
   s[c + d*] not in S_d*, is not a candidate.
   - memchr from s + c + d* returns the least p >= c + d* with s[p] == b (S_d* = {b}).
   - The walk advances c while s[c + d*] is not in S_d*.
   - Either way, every position skipped is excluded by this fact, so the first position examined is
     the least position >= c that is not excluded.
   - memchr returns NULL exactly when no p in [c + d*, n) holds b. Then no c' >= c is a candidate,
     and the miss value is returned.
3. **The verify.** At the stop's position the text tests the WHOLE of CONJ(c): every span-0
   position (the stop's own included where it lies in a run compare) and every ctx item, by the
   same text the generic row writes for it. So a yielded c satisfies CONJ(c), and BIND holds.
4. **The resume.** After a failed verify, c + 1 is the least position not yet excluded. With E4,
   the resume is c + t:
   - the test that failed is at offset j, so s[c + j] is not in S_j;
   - position c + u, for 1 <= u < t, would need s[c + j] in S_{j-u};
   - by t's definition S_{j-u} is a subset of S_j, so s[c + j] is not in S_{j-u} either, and
     c + u is not a candidate;
   - for u > j the offset j - u is negative and the formula does not apply, which is why t is at
     most j + 1.
   - A failed ctx item, or a failed run compare (where the failing byte is not known), resumes at
     c + 1.
5. **COMPL and EXACT.** Every skip removes only non-candidates (claims 1, 2 and 4). The first
   position yielded is therefore the least candidate >= lo, which is the generic row's answer.
   Each yielded position satisfies CONJ (claim 3). The answers are identical position for position,
   on every subject.
6. **The proof obligation, proven[d] == the REQUIRED set.** kit_class computes proven[] from the
   terms the row TESTS (`tests` = ARM_TESTS_EVERY), not from its text. The widened ofsskip tests
   every span-0 term (the scan proves the stop's term, and the verify chain tests every other one)
   and every ctx item (E2). So kit_class gives exactly the intersection of the REQUIRED sets at
   every d, the generic row's class. kit_report_exact holds on the same sites as today.
   - The ctx items' SATISFIES rule is rendered by the same `ctx_pred_test` text, so pred_proves'
     position rules (a SATISFIES item wider than one offset proves only its outermost position)
     are unchanged. The two-offset SATISFIES site r26zk's family D holds refused stays refused.

**The checks that must go red** (section 7):
- the byte-loop oracle's COMPL catches a stop that drops a real candidate;
- BIND and EXACT catch a verify that skips a REQUIRED item;
- family C's member-string equality catches a class that claims an untested offset.

## 5. The timing job of the proposed text (580-kit-r27-cover)

- **Instruments:** `docs/dev/lanes/r27_evidence/`:
  - `proto_bodies.py` renders the proposed text by hand into copies of the harness build's COV
    artifacts, replacing only the generic row's loop;
  - `measure_r27.sh` reuses `measure.sh` (build, its gate) and adds arms PRO and SHF, gated against
    the same python `re` answers;
  - `read_r27.py` applies the 650 reading rule per arm, plus R-27.1's bar;
  - `580-kit-r27-cover` is the queue job.
- **Arms:** DEF, COV and AA (the 650 harness's own), plus:
  - PRO: the stop search, one bound test, then the rest as one `&&` chain, resuming at c + 1;
  - SHF: PRO with each test its own branch and E4's shift.
- **Answer gate, no clock:** 216 + 144 arm cells all equal to python `re`.
- **The forms per cell** (the stop is the least default byte-rate mass, a tie to the leftmost):

| cell | stop | rest |
|---|---|---|
| lit-l8 | `b` @1 memchr | memcmp "abcdefgh" |
| foobar | `b` @3 memchr | memcmp "foobar" |
| file-ext-order | `.` @0 memchr | memcmp ".tar" |
| cat-bounded | `c` @0 memchr | memcmp "cat", ctx before and after (SATISFIES) |
| done-eol | `d` @0 memchr | memcmp "done", ctx after `\n` (SATISFIES) |
| year4 | walk `[0-9]` @0 | `[0-9]` @1..3 |
| word-digit | walk `[0-9]` @1 | `\w` @0 |
| hex8-bounded | walk `[0-9a-f]` @0 | `[0-9a-f]` @1..7, ctx before and after |

### RESULT

OWED at the time of writing. The run's own `r27_table.md` is the table, and it is pasted here when
the job ends (section 8).

## 6. Build plan (for the lane that gets the go)

- **ofsskip.c**
  - `ofs_fn_applies`: admit a multi-member scan position, and a multi-byte SET with no table, when
    the site is one the kit re-describes (E1, E2b).
  - The scan: the walk.
  - `verify_chain`: the kit's own set test where no table is named, and ctx items through
    generic.c's ctx_pred_test (exported in kit.h as the one rendering).
  - The contract: `ctx` and `absent` served, `table_ref` NONE served for a set.
- **finder.c / compose.c (E3):** RPT's pick FF_PROOF renders through ofsskip over the re-described
  span 0, where kit_report_exact holds for that arm; otherwise the composer's walk, as today.
  - kit_report_exact is asked of the arm actually chosen, which keeps one function for both the
    ask and the define.
- **presence.c:** export `byte_rate` and `set_mass` (kit.h). They are the stop's mass, the same
  arithmetic P3 uses.
- **E4** only if job 580's SHF reads it necessary (hex8), and then as its own commit with its own
  plant.
- **Zero default movers by construction.** Every widened clause is reachable only from a site with
  `ctx` stated, or a set with no table, or RPT's re-description. No default-build site has any of
  these. The proof of it is the one emit_sweep plain arm.

## 7. Checks the build lane runs (from the brief), and proposed sabotage rows

Checks:
- G2 / family C: the 150 REPORT sites, which then reach ofsskip, with a floor on REPORT sites
  rendered by it;
- `proof_run`'s BIND/PROOF/EXACT/COMPL byte-loop oracle;
- equality of proven[d] by member strings;
- `tests/memfn/run_proof.sh` green, and the memfn targets;
- `make strict`, `make test-codegen`;
- ONE emit_sweep plain arm under `scripts/boxlock run --label kit-r27`;
- the 650 harness re-run by main.

Proposed plants (ids from main; each a `run_proof.sh` plant and a mech row, arm `memfnfinder`):

| plant | what | must go red in |
|---|---|---|
| R27-a | the stop searched one offset off (memchr from c + d* + 1) | COMPL (a real candidate dropped) |
| R27-b | the bound test `c + K > n` off by one (`>=`) | COMPL at c + k = n |
| R27-c | the walk's set test one member short | COMPL |
| R27-d | a ctx item left out of the verify chain | BIND and family C's equality (proven[-1]/[k] all ones) |
| R27-e (E4 only) | the shift ignores the subset test (always j + 1) | COMPL on a non-uniform span |
| R27-f | the resume after a failed verify at c + 2 | COMPL |

## 8. State at handoff, and charter vs committed

- Commits: `8d235a525` (the evidence), then this report. Not merged anywhere.
- Rulings file: the last entry applied is the kit manager's design ruling (window search, no
  REPORT-only skip, design only).
- Job `580-kit-r27-cover`:
  - log: the queue run dir's `job.log`, under `worktrees/.boxqueue/{done,failed}/<TS>-580-kit-r27-cover/`;
  - table: `build/r27/job/r27_table.md` in this worktree;
  - completion line: `== r27 COMPLETE rows=1800 launches=5`.

| promise (brief) | state |
|---|---|
| the form chosen and why | DESIGN (sections 2-3); the build needs the go |
| the soundness argument | done (section 4) |
| G2 fixtures, a planted skip going red | NOT BUILT (no go); plants proposed (section 7) |
| run_proof.sh, memfn targets, strict, codegen | not run: no code changed |
| one emit_sweep plain arm, zero default movers | not run: no code changed; zero movers by construction argued (section 6) |
| self-check table vs the R-27 bar | job 580 on the PROPOSED text (section 5) |
| proposed sabotage rows | section 7 |
