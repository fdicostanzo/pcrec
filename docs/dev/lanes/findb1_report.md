# findb1: [FINDINGS] B1 = [PATFACTS] step 3.1 (lane report)

Lane `findb1` (opus, engine code), 2026-09-27. Branch `lane/findb1` is based on main
`bd8d1075` (abi 39) and is **NOT merged**. The deliverable is ONE abi event,
**39 -> 40**.

**Status: BUILT and committed.** Targeted validation is green (§5). The only red
is the accepted `nm arm_a.o` line in `test-codegen`. The full `make test
CC=gcc-16` is **OWED**: it was launched detached as this lane's last act (§5.3).

## 1. What landed, commit by commit, with the A/B emit diff

**Instrument.** `docs/dev/optloop/s1/s1_identity.py`, REUSED (pf30's), with no
second instrument. B1 added three things to it:
- `DROP_FINDINGS=1`, the named-lines deletion of design §7;
- a per-mover `moved` field naming every `RX_*` stamp that changed, plus `program`;
- a `findings` REACH count.

**Populations.** pcrec-bench's 64 capability patterns × 4 configs (read-only),
and every distinct corpus `pattern` × {`--features all`, `+ --engine=vm`}.

**Grid.** `-e byte` and `-e utf8`, each × {default, `-fno-req-byte`,
`-fno-req-run`, `-fno-offset-skip`}, which gives 8 runs per commit. The driver
was `scratchpad/gate.sh`. The baseline was each commit's predecessor. The last
row compares against main.

**Scale.** Every run compiled 5,938 artifact-configs under byte and 5,966
under utf8. 722 / 694 were refused on both sides (the same refusals).

| commit | what | movers (i=identical, c=changed) |
|---|---|---|
| `d170df58` c1 | **relocation**: `rb_pick`/`rn_scan_index`/`rn_window_start` move to `src/core/findings.c` as plain-array readers (`pcrec_find_set_pick`/`_run_scan_index`/`_run_window_start`); `pcrec_req_window`/`pcrec_req_pick` move to `src/facts/req.c`; `reqbyte.c` deleted; `facts.def` owners repointed; S266/S294 SAB_FILE | 0 c on all 8 |
| `b72c3f2a` c2 | `pcrec_find_byte_rate` (the gate moves inside it) and the four primitives, each with its NONE answer spelled inside (PICK→rightmost, COMPARE→false, MASS set and sequence→`⌊k·10^6/256⌋`). C1/C2a/C2b build a candidate order and ask one primitive. The derived req facts ask the accessor FIRST, before any branch (§6.4 rule 1). S266 and S294 re-anchored | 0 c on all 8 |
| `bfb9f8a1` c3 | C3: G1's density conjunct becomes `pcrec_find_no_commoner(pcrec_find_byte_rate(cx), p, q)`, and its encoding test is gone. S288 re-anchored | 0 c on all 8 |
| `56627dd1` c4 | **relocation**: `set_ppm` moves beside the primitives as `pcrec_find_set_ppm`, verbatim (still ungated) | 0 c on all 8 |
| `51553fa2` c5 | C4: `pcrec_find_set_ppm` = `set_mass(byte_rate(cx), set)` — **the utf8 mover**. `PCREC_ARTIFACT_ABI 39 -> 40` (the gate normalizes the abi digit) | byte: 0 c. utf8: **161 c** (10 bench + 151 corpus) under default/`-fno-req-byte`/`-fno-req-run`; **0** under `-fno-offset-skip` |
| `aca66366` c6 | the data tier: `default.rxt`, the embed, the pre-parse, the buffer-mode reader, normalization; the C table deleted; limits rows | 0 c on all 8 (baseline c5) |
| `8c24a086` c7 | `<P>_FINDINGS`, `rx_info.findings`, the digest; `tests/findings` joins make test; mech arm `findings`; S301 | named-lines gate: corpus 0 c; bench **2 c** per run (the quoted-size row, §2) |
| **B1 vs main** | c7 against `bd8d1075`, abi normalized, named lines dropped | byte: 2 c per run (§2). utf8: 163 c (= 161 + 2) under default and the two req denies; 2 under `-fno-offset-skip` |

After c7 come commits with no functional code change:
- comments;
- the ritual;
- manifests;
- `93e80da7`, which commits the generated `.inc` files (§4.1);
- the (B) re-pin;
- the size_term re-calibration.

A spot check over 6 artifacts (both encodings, DFA and VM) is byte-identical
between c7 and the final HEAD at the same `-o` basename.

**No §9.1 SEMANTIC mover appeared in any relocation commit. No K-row was filed.**

## 2. The movers manifests (`tests/findings/manifests/`)

**`b1_byte_movers.txt`: NOT EMPTY. It has 8 rows, all of them ONE bench
pattern.** The pattern is `wild-logparse-syslogbase-expanded` (auto-caps and
auto-nocaps, × 4 deny sets).
- **Only one line moves**, `RX_VM_PREFILTER_LANG_WHY`. It quotes the byte count
  of the failed exact-prefilter attempt: `size cap retry, exact 1464304 >
  1000000` became `1464689 > …` (+385).
- **Why it moves.** That attempt's artifact carries the new scaffolding, and
  the stamp quotes its own byte count.
- **What does not move.** No program byte, no other stamp, and the retry is the
  same on both sides.
- **The gap.** This is the byte-count reader class that §7's named-lines list
  does not name. **Acceptance item (1) ("EMPTY") is therefore not met literally.**
- It is scaffolding (a size quote), not two copies of one fact disagreeing.
- **REACH.** byte-rate was consumed by 5,938/5,938 artifact-configs under
  default, `-fno-req-run` and `-fno-offset-skip`, and by 1,944/5,938 under
  `-fno-req-byte` (the pick is denied, so only offset-k asks).

**RULED (manager, 2026-09-27): ACCEPTED as a named manifest row; the named-lines
gate is NOT widened.** The row, stated in full:
- pattern: `wild-logparse-syslogbase-expanded` (pcrec-bench capability);
- configs: `auto-caps` and `auto-nocaps`, under every deny set;
- the one line: `RX_VM_PREFILTER_LANG_WHY`;
- counts: `size cap retry, exact 1464304 > 1000000` (main) becomes `size cap
  retry, exact 1464689 > 1000000` (B1), +385 bytes;
- cause: the failed exact-prefilter attempt carries B1's new scaffolding (the
  stamp line, the `rx_info` initializer and the struct member with its
  comment), and the stamp quotes that attempt's own size;
- evidence the decision is unchanged:
  - `RX_VM_PREFILTER_LANG` (`count-collapsed`), `RX_ENGINE_SEL`
    (`size-cap-retry`) and `RX_ENGINE` are identical on both sides. The
    per-artifact `moved` list names `LANG_WHY` and nothing else.
  - The attempt is 464,304 / 464,689 bytes over its cap, far past any flip.
  - The artifacts are answer-identical (2,620 cells, 0 diverged).

**The general residual this exposes.** Any abi event that adds stamp bytes to
every artifact can move a SIZE-LADDER decision, for any pattern that sits
within that many bytes of a cap: a K rung, a prefilter collapse, an
anchored/premul drop, or a refusal. B1's growth is +385 bytes per artifact as
the size model counts them. `run_size_term.sh`'s reference build is exactly
that case: its K=4 rung moved from 30,683 to 31,068 against a 31,000 cap
(re-calibrated to 31,500, §3).

**Margins measured on the natural population (cheap sweep,
`scratchpad/capmargin.py`).** The sweep is B1's compiler over 13,064
artifact-configs: bench and corpus × byte/utf8 × auto/`--engine=vm`, at the
default caps (1,000,000 total, 500,000 code).

| cap | nearest pattern | encoding / engine | distance |
|---|---|---|---|
| total bytes | `wild-secrets-username-password-pair` (bench) | utf8, auto | 7,623 under |
| code bytes | `\P{Lo}` (corpus) | utf8, `--engine=vm` | 20,089 under |
| code bytes, refusal side | `\p{L}` (corpus) | utf8, `--engine=vm` | refused 64,908 over |
| quoted retry size | `wild-logparse-syslogbase-expanded` | — | 464,679 from its cap |

**No artifact is within 385 bytes of any cap.** The sweep does NOT see the
size term's internal ladder trials (the per-K rung sizes against
`PCREC_SIZE_TERM_THRESHOLD`) or the retry ladder's intermediate attempts. That
margin on the natural population is **OWED**. A future scaffolding bump should
re-run this sweep and add a trial-size readout.

**`b1_utf8_movers.txt`: 491 rows.**
- **What they are.** 161 per deny set are the offset-k cardinality fallback.
  - `RX_DFA_PREFILTER_OFFSETS` moves always.
  - The prefilter FORM (`RX_DFA_PREFILTER`) moves on most of them.
  - G1's `RX_REQ_WHY` (`emitted`↔`dominated`) moves on 82 under default and 95
    under `-fno-req-run`.
  - The program text those stamps name moves with them.
  - The other 2 per deny set are the quoted-size row.
- **None under `-fno-offset-skip`**, which attributes them to C4.
- **REACH.** 5,966 under default. 2,005 under `-fno-req-byte`, where the stamp
  reads `byte-rate=none`, so the default consumed but did not answer.
- **Answer- and give-up-identical** (§13 (2)), measured by
  `tests/findings/b1_mover_answers.py`. It links main's and B1's artifacts into
  `tests/possessify/possdiff_driver.c` and compares span, every capture slot
  and the give-up surface at every start position. Subjects are the pattern's
  own corpus lines, a byte-alphabet sweep, and seeded random strings with UTF-8
  lead/continuation bytes.

  | run | movers | identical | diverged | cells |
  |---|---|---|---|---|
  | utf8 × {default, `-fno-req-byte`, `-fno-req-run`} (each) | 163 | 163 | 0 | 163,770 |
  | utf8 `-fno-offset-skip` | 2 | 2 | 0 | 2,620 |
  | byte × each of the 4 deny sets | 2 | 2 | 0 | 2,620 |
  | c5 alone, vs c4 | 161 | 161 | 0 | 161,150 |

**Instrument blind spot.** `s1_identity.py` compares the `.c` only, never the
paired `.h` that `-o` also writes. The struct's appended `findings` member (in
the ABI-types block) is therefore not seen by the gate. I measured it
separately: it is part of the +385-byte uncut growth (§3).

## 3. The abi readers found (D94), by grep for `39`, plus the byte readers

1. `src/gen/emit_dfa.c` `PCREC_ARTIFACT_ABI` 39 -> 40 (c5).
2. `tests/codegen/run_codegen_tests.sh` `ABI_EXPECT=40`, plus its narrative clause.
3. `docs/spec/match_api.md` §6 change log: "gap-free from 2 to 40" and the new 39 -> 40 entry.
4. `tests/codegen/run_recursion_identity.sh` (B) `FILEPIN` re-pinned to `93e80da7`, the first B1 tree that compiles with no build step (§4.1). (A) is untouched.

**Readers no digit grep reaches**, found by running the suites:
- `tests/resource/run_resource_tests.sh`: the a{5,25000} rescue pin 762270 -> **762381**. That is +55 for the stamp and +56 for the initializer, verified by diff at the same `-o` basename.
- `tests/codegen/run_size_term.sh`: the cap-rescue reference cap 31,000 -> **31,500**.
  - Every artifact grew by **385 code bytes as the size model counts them**: the two `.c` lines plus the struct member and its essential doc-comment.
  - That growth pushed K=4 to 31,068, just over the old cap, and the ladder rightly took K=2.
  - Re-measured: K=6 36,149, K=4 31,068, K=3 31,953, K=2 29,838.
- `tests/registry/run_registry_tests.sh`: the limits_check PASS-count pin 29 -> **31**, for the two new anchored `limits.def` rows (the fifth reader of that shape).
- `tests/registry/limits_check.sh`: its manifest gains 2 rows (62 -> 64).

## 4. Parse-cost measurement (§13 (3)) and what it changed

The measurement is an in-process microbenchmark linking `libpcrec.a`, 2,000
iterations × 3 repetitions (`scratchpad/parsecost.c`):
- parse + normalize of `default.rxt` (8,425 bytes, 256 rows): **~47 µs**;
- a minimal compile (`a`) including that parse: **~231 µs**, so the parse is **~20%**;
- other compiles: 11% of `[0-9]+x[0-9]+e[0-9]+` and 6% of `GET /index\.html`.

Run-to-run spread was ~1%, so the parse cost is well above noise. By §13 (3), a
pre-parsed table is generated FROM the same text with an agreement check:
- `scripts/findgen.c` runs the one reader, in buffer mode, over each bundle and
  writes `src/core/findings_table.inc`;
- a compile then only normalizes: **0.77 µs**, and a minimal compile drops to
  ~181 µs;
- `tests/findings/` §3 checks that the table equals a fresh library parse of the
  embedded text.

A side benefit: a compile no longer calls the `.rxt` parser at all, so the
[REVW.3] property that the pipeline does not drag in the `.rxt` tier still holds.

### 4.1 DEVIATION: both generated `.inc` files are COMMITTED (design §8.2 said never)

The first build generated them into `build/gen/`. The suites showed this cannot
hold:
- **15 test scripts** build reference compilers by compiling every
  `src/**/*.c` with `-Ilib -Isrc` only (size_term, n1_budget, resource, the
  identity gates…);
- the (B) gate builds a `git archive` of `src lib cli`.

A source tree must therefore compile with no build step. The fix, on the
GEN_TABLES / `fold_tables.inc` precedent:
- `src/core/findings_store.inc` and `findings_table.inc` are committed;
- `make gen-findings` regenerates them;
- `tests/findings/` §2 (the embed equals its file) and §3 (the table equals a
  fresh parse) are the drift checks.

`findgen.c` moved to `scripts/` for the same reason: a second `main` under
`src/` breaks every reference compiler.

**For Frank/manager:** this amends §8.1/§8.2's "never committed". The
committed text is checked against its source, so it is not an unchecked
second source.

**RULED (manager): the committed `.inc` files are ACCEPTED** (the house
pattern). `docs/design/findings/design.md` §8.2 carries a `[B1]` revision
marker stating the deviation and its reason.

**Should `gen-findings` join `make gen-tables` / GEN_TABLES?** Yes, at B5,
not now:
- B5's `third_party/<src>/generate.py` writes a derived
  `src/findings/<name>.rxt`, after which the store's embed and pre-parse must
  be regenerated from it. `gen-tables` should therefore run `gen-findings`
  after its generator loop.
- `FIND_INCS` should join the GEN_TABLES prerequisite list, which design §13's
  B5 row already asks for.
- It is not done at B1 because no generator produces a bundle yet (the one
  bundle is hand-authored), and because `gen-findings` is heavier than the
  python generators: it builds a stage-0 library. That cost should be judged
  when a generator exists (D77).

### 4.2 The +385 code bytes, line by line (manager's question)

One small artifact (`abc`, default options) was emitted at main `bd8d1075` and
at the tip, with the same `-o` basename, and diffed. Every non-comment line
that changed:

| file | line | bytes |
|---|---|---|
| `.c` | `#define RX_FINDINGS "byte-rate=default:1822fb973b95a4da"` (new) | 55 |
| `.c` | `    .findings = "byte-rate=default:1822fb973b95a4da",` (new) | 56 |
| `.c` / `.h` | the generated-by line's `abi 39` -> `abi 40` | 0 |
| `.c` | `.abi = 39` -> `40` | 0 |
| `.h` (the ABI-types block) | `    const char *findings;    /* <PREFIX>_FINDINGS: the` plus THREE aligned continuation lines of the member's trailing comment | 274 |

That makes 111 + 274 = 385. The 274 counts as CODE because of the size
classifier, `emit_size_measure` (`src/core/compile.c`):
- It classifies a line as prose only when the line STARTS with `/*` or `//`.
- A TRAILING comment that opens after code on a line, and its continuation
  lines, are counted as code. Only 36 of the 274 bytes are the declaration.

This classifier behaviour is pre-existing. Every earlier `rx_info` member with
a multi-line trailing comment (`vars`, `search_form`, …) is charged the same
way.

**The member's comment is avoidable scaffolding cost.** A one-line trailing
comment, or the comment moved above the member as a leading `/* … */` (which
the classifier counts as prose), would cut B1's code growth to about 150
bytes. It is NOT fixed here, although the edit is small: it changes emitted
bytes again, so it needs a new (B) re-pin, and it would re-invalidate the
`make test` already running on this tree. A follow-up could take it together
with teaching the classifier about trailing comments. The classifier half is
the general fix, but it moves every size-term decision, so it is its own abi
event.

## 5. Validation verdicts (Mac, gcc-16)

### 5.1 Targeted suites

The run was serial, on final code. Logs are in the scratchpad
`/private/tmp/claude-501/-Users-fdicostanzo-pcrec/findb1/scratchpad/`.

- `make strict`: `strict: whole tree compiles clean with -Werror -Wshadow` (rc 0).
- `make test-codegen` (`suite_test-codegen2.log`): `run_group: 11/12 scripts
  passed`. The one red is the ACCEPTED `FAIL: nm could not read arm_a.o (no
  rx_search symbol)`, and make printed `*** [test-codegen] Error 1` for it.
  - `run_codegen_tests.sh`, which carries the abi=40 assertion, passes.
  - `run_size_term.sh` 31/0, `run_offset_skip.sh` 23/0.
  - `[SABANCHOR]`: all 308 rows' anchors resolve.
- `make test-registry`: rc 0, no `*** [test-registry] Error`. PC-3 is green on this box.
- `make test-rxtsource`: rc 0.
- `make test-findings`: rc 0. `run_findings_tests.sh` 17/0; `run_analyzer_tests.py` 35 passed.
- `make test-prechecks`: rc 0, 301/0.
- `make test-recursion-identity`: rc 0, `checks passed: 16`, `checks failed: 0`, with (B) against `93e80da7`.
- `make test-resource`: rc 0, 27/0.
- `make test-cli`: rc 0, run on c9's tree before the last two commits, which touch no CLI.

### 5.2 Mech

Solo S301 (`bash tests/mech/run_sabotage_matrix.sh S301`, `mech_S301.log`):
- `reach:ok(1/1),findings:1fail/16pass DETECTED`;
- `mech run COMPLETE: 1 rows (unexpected: 0, undetected: 0, unreached: 0, anomalies: 0 …)`.

S266, S294 and S288 were re-anchored and their anchors resolve (SABANCHOR). Their
solo runs need the harness arm (~30 min each) and are **OWED** to the manager's battery.

### 5.3 OWED: full `make test CC=gcc-16`

Launched detached as this lane's last act:
- log: `scratchpad/make_test_final.log`;
- completion line: `FINDB1 MAKE TEST rc=`.

Read make's `*** [test-X] Error` lines. The expected red is the `nm arm_a.o`
line in test-codegen.

### 5.4 Completed after hand-off (lane findb1, same day)

**Full `make test CC=gcc-16`** (`make_test_final.log`): `sections ran: 44/44`,
`FINDB1 MAKE TEST rc=2`, with exactly two `*** [test-X] Error` lines.
- `test-codegen`: the accepted `nm could not read arm_a.o` red.
- `test-cpset-structure`: its stamp manifest `m5_stage1_stamps.tsv` drifted by
  exactly +385 EMITTED_BYTES on every one of its 12 rows. That is B1's
  per-artifact growth (§4.2), and nothing else moved. It was re-recorded in
  `4534a637` with its own paragraph. `make test-cpset-structure` then read
  rc 0, 28/0.

**Solo mech rows, run serially at `4534a637`** (`mech_S266/S294/S288.log`).
Each run ended `mech run COMPLETE: 1 rows (unexpected: 0, undetected: 0,
unreached: 0)`.

| row | arms | verdict |
|---|---|---|
| S266 | `reach:ok(1/1),prechecks:45fail/255pass,corpus:0fail/29224pass` | DETECTED |
| S294 | `reach:ok(1/1),prechecks:11fail/290pass,corpus:0fail/29224pass` | DETECTED |
| S288 | `reach:ok(1/1),prechecks:1fail/300pass` | DETECTED |

## 6. Held items, deviations, open questions

**Held.**
- **HELD by D126**: PATFACTS §11.6 check 1 (the non-perturbation check) and its
  sabotage row. There is no failing witness (D77), so neither was built.
- **Deferred to B4**: `run-rarity`'s NONE answer (open item 6).

**Deviations.**
1. **`facts.def`'s OWNER for `req_run`/`req_byte` is `src/facts/req.c`, not
   `src/core/findings.c`.**
   - The readers do live in `findings.c`, as ruling (3) says, and take plain byte
     arrays. The design itself says "the file needs no facts-layer type".
   - The compositions into the facts (`ReqRun`/`ReqSet`/`PfWhyCode`) live with
     the walk.
   - A `src/core` owner would have to include `facts_derive.h`, which is an
     include back-edge.
2. **Where the stamp sits.** `<P>_FINDINGS` is written beside the `rx_info`
   definition, not with `REQ_BYTE`'s prologue family. §6.4 rule 2 requires
   rendering after the last reader, and offset-k asks during DFA body emission.
   Under `-fno-req-byte` it asks AFTER the prologue, and §4 of the tests
   witnesses exactly that ("offset-k only").
3. **`default_ppm.tsv`** is RUNEST's own dump, copied verbatim, as §8.1 names it.
4. **`match_api.md` §6's struct listing** also gains the `[VAR]` `vars`/`nvars`
   members, which it had omitted.
5. **The derivation vocabulary table** stays in `rxt_source.c`; B0's comment
   said it would move to `findings.c`. Moving it is cosmetic and not needed at
   B1, and the table remains the one home. Open.

**Ruling on open item 5: C8's kind is PICK.**
- `[OPT-A]`'s rarest-byte choice selects which sound key the candidate scan
  keys on, and every candidate is sound.
- Its no-information answer is today's `cand_from_escapes` choice, which the
  row can place as the primitive's NONE index. That index is "the index of the
  NONE candidate in the reader's order", and PICK already takes it.
- If the row instead weighs "scan the whole set as a class" against "memchr one
  byte", that is a MASS comparison (set mass against byte rate), which also
  needs no new kind.
- A new kind would be needed only if the no-information answer were neither a
  candidate nor a mass comparison, and I found no such shape.

**Open items (2)(3)(4) of q4amend.** All three are accepted as ruled:
- the primitives take `rate`;
- the readers live in `findings.c`;
- the threaded `pick` is published through the facts record. PATFACTS 3.0
  already added `ReqSet.rightmost`, so no side channel was needed.

**Stale spots from q4amend's list, NOT fixed.** The lane edited no design doc,
so these remain:
- findings `design.md` §1 row 13;
- §6.2a's `dfa_cand_scan_byte`/line citations;
- §6.4 rule 1's "C1/C2 are the named exception";
- §9's "reader's NONE fallback";
- §11.2, which lacks S301's row (S301 exists now; the design should cite it);
- §11.7's widened text;
- §13's B1 row scope (the primitives, the reader moves, the `reqbyte.c` deletion);
- §14's per-reader wording;
- §15's R24 row;
- PATFACTS line citations;
- the §8.1/§8.2 "never committed" text (superseded by §4.1 above);
- §6.1's "facts.def's OWNER column names this file" (superseded by deviation 1);
- §7's named-lines list, which lacks the struct member line and the quoted-size class (§2).

**Other notes.**
- `tools/review/out/` censuses were not regenerated.
- `include_graph.py` has no `findings` layer entry for `src/findings/`, and
  there is no `.c` there now.
- `rate:builtin-prior` in `--emit-facts` still reads correctly: the default
  bundle IS that prior.

## 7. For a fresh agent resuming

Read `make_test_final.log` for `FINDB1 MAKE TEST rc=` and the `***` lines. If
the result is green apart from the accepted red, delivery is complete. §2's byte
manifest is RULED accepted, and the pre-parsed table is RULED correct per §13 (3).
The manager still rules on:
- §4.1's committed `.inc` deviation;
- deviation 1.

Remaining owed items are the solo mech runs for S266, S294 and S288, and the
manager's battery at merge.
