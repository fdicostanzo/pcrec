# e1build — [WINDOW-E1] E-1: pcrec builds the analysis object (lane report)

Lane `e1build` (opus), 2026-10-17, branch `lane/e1build` from main
`08ac08a03`. Design of record: `docs/design/memfn/window_contract.md` rev 3.1
§3.7 (3.7.1-3.7.10), D167 add. 2-3, D162 add. 4. Frank's build go 2026-10-17.
NOT merged, NOT pushed.

**Headline.** E-1 is built as §3.7.1 lists it. Every compile attempt builds
the kit's `mf_analysis` once, eagerly, right after its chain resolves, and
hands it to `mf_art_begin`. Building it records no ask and refuses nothing.
**Zero movers**: emit_sweep over the arm x analysis product of §3.7.4/§3.7.4a
(28 runs, every stream) reads 0 movers and 0 asymmetric refusals, and the
stamp/refusal census is identical between the two binaries (§3 below). Light
suites are green. Owed: the full `make test`, the mech rows, `make asan` over
test-findings/test-memfn, and the kit's re-declaration of `bytes`/`fidelity`
(departure D1).

## 1. What was built, file by file

| file | what |
|---|---|
| `src/core/findings.h` | `PcrecFindTblBlock` gains `prov_source`/`prov_bytes`/`prov_fidelity`. `PcrecFindStatus` (UNDERIVED/OK/NONE/UNDERIVABLE/BROKEN). The record gains `byte_rate_status`, `byte_rate_block`, `byte_rate_via`; `byte_rate_have`'s comment re-worded (m6). THE QUERY VOCABULARY: `PcrecFindQuery` (tag, payload version, `unmeasured`), `PCREC_FQ_*` indices, `pcrec_find_query`, `pcrec_find_query_tags`. `PcrecFindDeriv.query` is now a row index. The offer: `PcrecFindKindState`, `PcrecFindSource`, `PcrecFindOffer`, `pcrec_find_offer`. `pcrec_find_byte_rate_answers` (D5 below). |
| `src/core/findings.c` | `find_derivs[]`'s third column indexes `find_queries[]`. `find_derive_byte_rate_status` memoizes and never refuses; `find_raise_byte_rate` holds today's two diagnostics verbatim; `pcrec_find_byte_rate` (the ASK path) sets `asked`, derives, raises. `find_queries[]` is the vocabulary's one home (+ each row's non-raising answer and payload digest; `_Static_assert` on the row count). T-KIND is `find_kind_rows[]`, a first-match table over `FindKindFacts` (8 rows, §3.2's). `pcrec_find_offer` evaluates it and computes the digest from the payload it hands over. |
| `src/core/findings_table.inc` | regenerated (`make gen-findings`): every block row carries its stanza's source/bytes/fidelity. |
| `scripts/findgen.c` | writes the three fields; REFUSES a block with no provenance source and a store `default` block whose source is not `authored` (§3.2's cross-check). |
| `src/core/internal.h` | `RxtFindBlock` gains the stanza's three fields (as written); `Job.analysis`; `pcrec_memfn_analysis_build`'s declaration (gen group). |
| `src/parse/rxt_source.c` | a data block's `provenance` frame carries its block's index (`fbi`) and copies `source`/`bytes`/`fidelity` onto the block when it closes. `serves_check` validates the query against `pcrec_find_query` and names the vocabulary through `pcrec_find_query_tags` (byte-identical text). |
| `src/parse/rxt_find.c` | `chain_serves_enc` reads `pcrec_find_query` (local list gone); `link_from_source` copies the three provenance fields for a runtime (S1/`-I`) bundle. |
| `src/dump/findings_dump.c` | `FIND_QUERIES[]` gone; the resolution rows walk `pcrec_find_query`. |
| `src/gen/memfn_sites.c` | `pcrec_memfn_analysis_build`: the object (one `mf_akind` per query, the offer mapped by two declared cell tables onto `MF_KIND_*`/`MF_PROV_*`), §3.1's invariant checked as an internal error, `KSRCTRACE object` records under `-DPCREC_KS_TRACE`. `pcrec_memfn_art` passes `job->analysis` to `mf_art_begin` and builds nothing. |
| `src/core/compile.c` | `compile_driver` calls `pcrec_memfn_analysis_build(&cx)` right after `pcrec_find_resolve`. |
| `src/facts/req.c` | `req_rate_why` asks `pcrec_find_byte_rate_answers` (no memo read). |
| `scripts/emit_sweep.py` | `--data`'s `data_trace` drops `KSRCTRACE` lines (an offer is not a read; they carry the data's digest), so §13's census is unchanged. |
| `tests/findings/` | `e1_fixtures.py`, `e1_object_check.py` (§14: C-E1-1..5), `c_pert.py` (§15: C-PERT), `structural_check.py` S4 (C-E1-6), `findings_probe.c` + §3 (agreement covers the provenance fields), §12's new "an offer is not an ask" cell. |
| `tests/mech/sabotages/` | S991-S996, S1027-S1031, S1034 (§5). |
| CLAUDE.md | `src/core`, `src/gen`, `src/parse`, `src/dump`, `src/facts`, `scripts`, `tests/findings`. |
| `docs/dev/plan.md` | [WINDOW-E1] -> STATE:started, status line. |
| `docs/dev/lanes/e1build_evidence/` | `g1e1_sweep.sh` (the G1-E1 driver), `g1e1_summary.tsv`, `analysiscount_{ref,new}.out`, `plant_precheck.sh` + `.out`. |

## 2. Departures from the note (the code's facts win; none moves a byte)

- **D1 — the kit's B1 layout has no `bytes`/`fidelity`, and spells the
  authored source `MF_PROV_PRIOR_AUTHORED`** (`memfn/include/memfn.h:835-856`
  on main). The note (§3.1) says B1 owes the two fields in a re-declaration
  before E-1, and §3.7.10 forbids E-1 any kit edit or `MF_SITE_ABI` move.
  Built: the object fills the layout as declared (source, bundle, digest,
  payload). `bytes` and `fidelity` are carried pcrec-side
  (`PcrecFindTblBlock.prov_*`, `PcrecFindOffer`, the trace record) and are
  checked there (C-E1-1). OWED: a kit request for the re-declaration
  (one `MF_SITE_ABI` event), after which `memfn_sites.c` maps the two fields
  (two lines). Reported to main at read time.
- **D2 — `fidelity synthesized` is a PRIOR, per D162 add. 4** ("`measured`
  requires `source measured` and a non-synthesized `fidelity`"), which
  post-dates rev 3.1. The note's T-KIND makes any non-authored block
  MEASURED (and its "today's cells" call `log` measured). Built: T-KIND's
  `prior` fact is "`source authored` OR `fidelity synthesized`", so the
  shipped `log` bundle is PRIOR_AUTHORED (bundle `log`, bytes 0, fidelity
  `synthesized`), `weblog` MEASURED. With no fidelity field in the kit
  layout (D1) the kit could not apply the rule itself. One predicate
  (`find_block_prior`); flipping it is one line. Reported to main at read
  time as a leaning; no reply before delivery.
- **D3 — the trace record lives in the `-DPCREC_KS_TRACE` build, as
  `KSRCTRACE object ...`**, not under `-DPCREC_CAND_TRACE`. C-E1-1's ordering
  assertion (S1031) reads each attempt's `KSTRACE analysis - resolve -`
  record, which exists only in the KS build; §13 already builds it. The
  record is its own line kind, so `emit_sweep.py --data` (which reads
  `KSTRACE\t` lines as asks) is unaffected once `data_trace` skips it.
- **D4 — `byte_rate_derived` is folded into `byte_rate_status`**: the status
  enum's zero member `PCREC_FIND_ST_UNDERIVED` IS "the memo is empty", so a
  separate bool would be a second field to keep in step. S1034's plant tests
  `byte_rate_status == PCREC_FIND_ST_UNDERIVED` where the note says
  `byte_rate_derived`.
- **D5 — `req_rate_why` asks `pcrec_find_byte_rate_answers`**, not
  `pcrec_find_byte_rate(cx) != NULL`: testing the rate pointer at a reader is
  exactly what findings design §6.3 / `structural_check.py` S1 forbids
  (D126 Q4). The new accessor is the same ask answered as a fact; the value
  is the callers' (they ask first). The memo has no outside reader (S4).
- **D6 — S1028's fall-through lands on `authored-absent`, not `measured`
  with a NULL payload.** The built `measured` row requires a derivation, so
  an underivable authored block falls to `authored-absent` (ABSENT). The
  detector is C-E1-1's `l1none/utf8` cell and its reach floor, not the
  payload invariant. Pre-checked detected (§5).
- **D7 — C-PERT's population is distinct (file, pattern) pairs** (5,275),
  not corpus rows (5,790), so its power counts are lower than the
  prototype's (1,009 vs 1,161 default/byte). Floors are measured on this
  population (§4).
- **D8 — §3.7.1's "the three readers" were four spellings in code**: the
  `.rxt` reader's query check also read the vocabulary off
  `find_derivs[]`'s third column; it now reads `pcrec_find_query` directly
  (the derivation's `query` is an index). The refusal texts are
  byte-identical (checked, §3).
- **Not a departure, a fact for G1-E1's reading**: emit_sweep's
  `emit-ir-vm` stream REFUSES every compile carrying `--analysis` on both
  sides (`--emit-ir` does not take the option), so a run with an analysis
  cell reports a reach-floor violation (rc 1) on that stream with 0 movers.
  The verdict is movers/asymmetric, per run (§3).

No departure needed a ruling to keep bytes still; D1 and D2 are flagged for
the manager because each changes what the kit will READ at B3a.

## 3. Zero-mover evidence (G1-E1)

REF = `git archive 08ac08a03` built in scratch; NEW = this branch's
`build/pcrec` (frozen copy). Driver: `e1build_evidence/g1e1_sweep.sh`
(emit_sweep `--ref-bin REF --bin NEW --no-self-check`, every stream: c-default,
c-vm, emit-ir-vm, facts, emit-ir-auto x4, stderr, composition, dumps).

| enc | arm | cells (analysis) | streams | movers | asymmetric | run rc |
|---|---|---|---|---|---|---|
| byte | default (no flag) | none / weblog / mine | 11 / 12 / 12 | 0 | 0 | 0 / 1 / 1 |
| byte | `-fno-req-byte` | none / weblog / mine | 12 each | 0 | 0 | 0 / 1 / 1 |
| byte | `-fno-req-byte -fno-req-run -fno-prefilter` | none / weblog / mine | 12 each | 0 | 0 | 0 / 1 / 1 |
| byte | `--engine=vm -fno-req-byte -fno-req-run` | none / weblog / mine | 12 each | 0 | 0 | 0 / 1 / 1 |
| utf8 | default (`-e utf8`) | none / weblog / mine / l1none | 12 each | 0 | 0 | 0 / 1 / 1 / 1 |
| utf8 | `-fno-req-byte` | none / weblog / mine / l1none | 12 each | 0 | 0 | 0 / 1 / 1 / 1 |
| utf8 | `-fno-req-byte -fno-req-run -fno-prefilter` | none / weblog / mine / l1none | 12 each | 0 | 0 | 0 / 1 / 1 / 1 |
| utf8 | `--engine=vm -fno-req-byte -fno-req-run` | none / weblog / mine / l1none | 12 each | 0 | 0 | 0 / 1 / 1 / 1 |

**28 runs, 0 movers and 0 asymmetric refusals on every stream of every run**
(`e1build_evidence/g1e1_summary.tsv`; logs were in scratch). The `--engine=vm`
arm without denies is every run's own stream 2. Every rc 1 is an instrument
floor, identical on both sides, never a difference; the cause was grepped in
every log:
- 20 runs: `emit-ir-vm` reach 0, because `--emit-ir` refuses `--analysis` on
  both sides (§2's last bullet).
- 3 `l1none` runs: stream-1 reach under the floor (and stream 2's too under
  default) because the compiles that ask refuse "counts nothing via
  encode-latin1" on BOTH sides (reach 1,905 under `-fno-req-byte`, 3,246 under
  the deny-pf arm, 0 under default). These
  are exactly §3.7.4a's populations, compared as keys, identical.
- `utf8/default/l1none` additionally: the composition stream refuses all 386
  files on both sides (every compile asks), so the DELIVER witness has no
  population.

No run with no analysis cell had any violation (rc 0, 8 runs).

**Refusal and stamp census** (§3.7.4/§3.7.4a's floors), rev 3.1's own
instrument `window_contract_rev31/analysiscount.py` run on BOTH binaries:

Both outputs are byte-identical (`diff` empty;
`e1build_evidence/analysiscount_{ref,new}.out`, 27 arms x 5,790 patterns
each). §3.7.7's floors, read from NEW:

| floor (G1-E1) | required | measured |
|---|---|---|
| `""` in `-fno-req-byte` byte (no analysis) | >= 1,900 | 1,973 |
| `""` in the VM deny arm, byte / utf8 | >= 5,300 | 5,337 / 5,367 |
| `l1none` compiles that SUCCEED with `""`, `-fno-req-byte` / deny-pf / VM deny (utf8) | >= 1,900 / 3,200 / 5,300 | 1,905 / 3,246 / 5,367 |
| `l1none` underivable refusals, default / `--engine=vm` (utf8) | identical | 5,364 / 5,367 both sides |

So the B1 population (the compiles a raising offer would have refused) still
compiles, and every compile that asks still refuses with today's text.

**Also compared byte for byte, REF vs NEW**: `--list-analyses`,
`--list-analysis` over default/weblog/log/weblog -e utf8 and five `-I`
fixtures (10 listings, 0 differ); the `serves` refusal texts (unknown query,
wrong derivation): identical.

Compile cost: not gated (§3.7.1) and NOT measured here (the box was shared
with the kit's chain, so run walls are not comparable). The eager offer adds
one normalization per attempt on the arms that asked nothing, as §3.7.1's
arithmetic says.

The `mine` cell is `src/findings/weblog.rxt` renamed `analysis mine` under
`-I` (a measured user bundle answering at stop -I); `l1none` is tests/findings'
own fixture.

## 4. Suites run, with verdicts

All on this box at -j4 or less, with the kit's R-23 chain running. Verdict
read from make's `*** [...test-...] Error` lines.

| suite | verdict |
|---|---|
| `make strict` | clean (`whole tree compiles clean with -Werror -Wshadow`) |
| `make test-findings` | green, 103 passed / 0 failed (incl. §3, §12 new cell, §13, §14 C-E1-1..5 9/9, §15 C-PERT 2/2); re-run after the K37 wrap: green, 103 / 0 |
| `make test-codegen` | first run RED on [K37] (my §15 line invoked `$PCREC` unbounded); wrapped in `$TIMEOUT_BIN`; re-run green, 16/16 scripts |
| `make test-registry` | green |
| `make test-rxtsource` | green (INV-COMPAT 282 files / 5,790 blocks) |
| `make test-core` | green, 7/0 |
| `make test-spec-history` | green, 145/0 |
| `make test-plan-lint` | green, 2/0 |
| `make test-memfn-stamps` / `-deleg` / `-rows` / `-reach` / `-arms` | green: 25/0, 5/0, 232/0, 4/0, 383/0 |
| `structural_check.py` S4 failing direction | `req_rate_why` reverted to `byte_rate_have`: S4 FAILS naming `src/facts/req.c:656` |
| C-PERT full population (`c_pert.py --every 1`, NEW) | 42,200 artifacts x 3 compiles: 0 FAIL; power 1,009 / 617 / 494 / 484 / 219 / 237 / 0 / 0 (default byte/utf8, -fno-req-byte byte/utf8, deny-pf byte/utf8, VM deny byte/utf8); F-5 bucket exactly its 2 pinned witnesses |

C-PERT slice floors (`--every 16`, in `make test`): measured 57 / 33 / 27 /
26 / 9 / 11 / 0 / 0, floored at ~80%: 45 / 26 / 21 / 20 / 7 / 8 / 0 / 0.

## 5. Sabotage rows and their reach

Ids per §3.7.8's map. `make mech` NOT run (box held). A light pre-check
(`e1build_evidence/plant_precheck.sh`, output `plant_precheck.out`) applied
each plant to a `git archive` of the branch, built it, and ran the named
detectors directly: every E-1 row is detected; each row's `SAB_REACH` reads
its expect string on the clean tree (S1029 by design does not).

| id | plant | detector (pre-check FAIL counts: §14 / stamp+refusal cells / §15) | reach |
|---|---|---|---|
| S991 | the offer marks `asked` | §4 nothing-asked, §6 #22, §14 C-E1-4 (1 / 3 / 1) | ok |
| S992 | provenance by NAME | §14 C-E1-1 mdef/auth/log (4 / 0 / 0) | ok |
| S993 | prior-none carries a uniform table | the object invariant (internal error on every utf8 default compile), §14 C-E1-3 (6 / 1 / 1228) | ok |
| S994 | one object per process | §14 ordering + C-E1-4 two targets (3 / 0 / 0) | ok |
| S995 | byte-rate `unmeasured` = ABSENT | §14 C-E1-1 + C-E1-5 (28 / 0 / 0) | ok |
| S996 | the offer digests the COUNTS | §14 C-E1-1 digests + C-E1-4 (25 / 0 / 0) | ok |
| S1027 | the offer raises | §12's new cell, §14 l1none/utf8 (2 / 1 / 0) | ok |
| S1028 | the underivable rows deleted | §14 C-E1-1 l1none/utf8 + reach floor (2 / 0 / 0) | ok |
| S1029 | `authored` loses ARRIVES | declared `SAB_EXPECT=UNREACHED` until [FINDINGS] B4 (reach probe: `run-rarity` payload version > 0) | UNREACHED (by design) |
| S1030 | provenance by LINK (rev 3) | §14 C-E1-1 copy/auth/log (4 / 0 / 0) | ok |
| S1031 | lazy build at the first kit call | §14 ordering assertion (22 / 0 / 0) | ok |
| S1034 | the ask marks only when it derives | §15 C-PERT default arms, §4, §12 refusal (1 / 2 / 168) | ok |

**Held for B3b, not spare** (the note maps them): S997 (no OR of the kit's
`consulted`), S998 (a SIMD-only `consulted`), S1032 (stamp rendered before
`mf_art_end`, lands with B3b), S1033 (a kit row drops its `consulted` bit).
No id of the sixteen is spare. `VALIDATE_ONLY=1` on the twelve: 12 valid. All
782 existing anchors still resolve ([SABANCHOR], test-codegen), and every
existing row anchored in a touched file was re-counted (all 1/1).

## 6. Spec hunks (D80)

None, per §3.7.9: the object is the kit's input (`docs/spec/` describes no
`memfn.h` struct), no stamp, flag, listing, entry, limit or diagnostic
changes, and no refusal moves (§3). `findings_table.inc` gains fields no
listing prints. F-6 (findings.md 3a¶3 reads two ways) stays FILED, not fixed.

## 7. Validation still owed

1. The full `make test` (async, via `scripts/perfrun`) — E-1 touches
   `src/core`, `src/parse`, `src/gen`, `src/facts` and the findings table.
2. `make mech` rows S991 S992 S993 S994 S995 S996 S1027 S1028 S1029 S1030
   S1031 S1034 (passed without suffix; S1029 must read UNREACHED (EXPECTED)).
3. `make asan` over `test-findings` and `test-memfn` (§3.7.7's ASan/LSan row:
   the object outlives `mf_art_end` and dies with the attempt's arena/Job).
4. `make test-axes`: not required by the note for E-1 (its G1-E1 is the
   emit_sweep product above, done); the deny arms it would add are covered.
5. The kit's re-declaration of `mf_prov.bytes`/`fidelity` (D1), main to file.
6. Main's ruling on D2 (synthesized = prior) if the leaning is not accepted.

Not E-1's (unchanged by this lane): RP (render point), the union-over-attempts
abi event (D167 add. 3), C-RP, C-CONS, the B3b hunks.

## 8. Resume notes

A fresh agent finishing the delivery: rebase is not needed (branch point
`08ac08a03`); run the owed items in §7 against the tip; if D2 is ruled the
other way, flip `find_block_prior` (drop the `fidelity synthesized` arm) and
update `e1_object_check.py`'s `log/*` cells to MEASURED with bytes 999960.
