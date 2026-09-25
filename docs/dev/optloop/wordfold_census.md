# `[WORD-FOLD]` — the wide literal-run cube-compare census (the D77 trigger)

Lane `wfcensus`, 2026-09-25. Census only: nothing under `src/`, `lib/` or
`cli/` changed, no mechanism is built. Every population number below is a
COUNT from compiling patterns and reading their real trees/artifacts; the
one exception (RX_VM_FRAMELESS, RX_ENGINE) reads a stamp already emitted by
this worktree's own `build/pcrec`, never a guess.

The row (`docs/dev/plan.md` `[WORD-FOLD]`, chartered unscheduled by Frank
2026-09-11, "8 byte masks then compare?") proposes ONE AND-mask compare
form, `memcpy(&w, subject+pos, 8); (w & K) == T`, uniform across an exact
literal byte (K=0xFF), a caseless letter (K=0xDF) and every other ONE-CUBE
class. Its own D77 gate: **"count corpus+bench literal runs >= 4-8 bytes
with >= 1 cube-but-not-singleton position; a zero-population census parks
the row without prejudice."** This is that census, plus the three
follow-on questions Frank's 2026-09-25 placement proposal asked for: the
frameless precondition, the `(?i)` offset-k degradation, and which cycle-1
losing bench cells the population overlaps.

Instruments: `wf/wf_run_probe.c` (the run walk), `wf/wf_census.py` (the
population driver), `wf/wf_stamps.py` (engine-route stamps for the
qualifying population), `wf/wf_offsetk_probe.c` + inline driver (the
`(?i)` offset-k walk), `wf/wf_report.py` (renders `wf/wf_summary.txt`,
the numbers this document cites). `wf/CLAUDE.md` describes each file.

---

## 0. The headline

**The population is not zero. It clears D77.**

* **16 patterns, corpus+bench combined (byte domain), carry a literal-run
  window of length >= 4 with at least one cube-but-not-singleton
  position** — 9 in the bench sets, 7 in the shipped corpus. Six of the
  nine bench ones reach length >= 8.
* **Four of the nine bench witnesses are cycle-1 LOSING cells on
  `large-subject-throughput`** (`wild-waf-crs-942360-concat-sqli` 5.41x
  behind, `-942270-union-select` 3.56x, `-942160-sleep-benchmark` 3.27x,
  `-942140-dbnames` 1.82x — §5), worth 0.684 of the whole 34-cell losing
  matrix's ~10.284 score. A fifth, `wild-secrets-slack-webhook-url`, is a
  near-tie (0.77x — already close to winning). These are real, not
  synthetic: PCRE2-style WAF rule literals (`sleep`, `union`, `select`,
  `benchmark`, `group_concat`) spelled `(?i)`.
* **The frameless precondition holds on every real witness found**: all 7
  VM-route qualifying-length patterns with a cube-not-singleton position
  read `RX_VM_FRAMELESS "1"` (§4) — zero counter-examples, though the
  population is small enough that this is a clean-so-far result, not a
  proof.
* **The DFA offset-k skip's own claimed degradation is confirmed and
  measured, not merely argued**: of 42 `(?i)` patterns whose offset-k walk
  is producible, **31 (73.8%) have NO case-invariant offset anywhere** —
  fully degraded, including three of the four cycle-1 losing WAF
  witnesses and both purpose-built `altwide/ci-*` caseless witnesses
  (§6).
* **Scenario asymmetry, exactly as Frank's own caution anticipated**: the
  shipped **corpus's own 48 `(?i)` patterns carry ZERO runs of length >=
  4** (they test case-folding mechanics on short synthetic literals, not
  realistic keywords) while the **bench's realistic sets carry 7 of 12**.
  The corpus alone would have parked this row; the bench does not (§7).
* **A cube-not-singleton position is not always caseless** — one corpus
  witness (`tests/recursion/d27/sr_spellings.rxt:404` and five siblings)
  reaches a 10-byte run via `(j|k)` (a 2-member class differing by one
  bit, XOR 0x01), an incidental non-caseless one-cube, independent
  confirmation of the row's own "every other one-cube class participates
  identically" claim and of `cls_tree_study.md`'s provenance-blind
  `cube_of` finding, on real corpus material rather than a constructed
  set (§3).

**Recommendation, stated once**: the row should open. Frank's 2026-09-25
placement proposal is corroborated: fold `[WORD-FOLD]` and `[OPT-VMLIT]`'s
exact-memcmp case into ONE cycle-3 "wide literal-run compare" row (§8),
with `[OPT-REQPOS]` tier 2b's caseless carve-out as its search-side twin.

---

## 1. Method

`wf/wf_run_probe.c` drives the real parser + `pcrec_altcls` +
`pcrec_discharge_atomic` + `pcrec_lower_enc` pipeline prefix
`docs/dev/optloop/c2/reqpos_probe.c` established and cross-checked (its own
header states why: `pcrec_altcls` FACTORS alternations before anything
downstream sees them, so skipping it measures the wrong tree). After the
lowering every `A_CLASS` is a BYTE class, matching the row's own scope
statement ("byte-domain cubes only ... utf8 multi-byte folds were never
byte cubes").

**The one-cube test** (`byte_cube_of`) is `studies/cls_tree_study/kit.py`'s
/ `discover.c`'s `cube_of` — the closed-form AND/OR-of-ranges test,
MEASURED there against all 1,114,112 code points with zero disagreement —
specialized to the FIXED 8-bit byte domain the plan row's own AND-mask
form uses (`K` is 8 bits by construction, not a dynamically-sized DP
section), followed by an exact 256-point check against the interval list
directly (cheap at this width, and it closes any residual false-positive
risk the O(k) shortcut exists to avoid at a much larger domain). A
singleton byte is the `nfree == 0` case of the SAME test, not a separate
function — the plan row's own claim that a singleton, a caseless pair and
a window's dead tail are "the same test, uniformly."

**The run walk** mirrors `reqpos_probe.c`'s `head`/`tail`/`best`
cat/alt merge structure exactly (the A_CAT spine walked iteratively for
the same segfault-avoidance reason stated there), tracking a `Pos`
(cube/singleton/K/T) per position instead of a required byte. `best`
keeps the SINGLE LONGEST run per pattern — the same simplification
`reqpos_census.md` used for its own tier tables — which is the right
witness for a POPULATION question ("does pattern P carry a run of length
>= N") even though it under-counts a pattern's second-longest run.

**Verification.** Nine hand-picked patterns (plain literal, caseless
literal, a digit run, a non-cube `[a-z]` break, `(?i)github_pat_`, a
literal-word alternation both caseful and caseless, a mid-run `.` break,
and `{a,c}`'s incidental cube) were checked by hand against the probe's
output before the corpus/bench run — every one matched the expected
run, length, K/T values and break point (`wf/CLAUDE.md` records the
cases). This is not a cross-check against a landed mechanism the way
`reqpos_probe.c`'s was (no shipped stamp computes this fact today), so
hand verification is the census's own soundness argument; §3 below
independently re-derives one corpus finding (`{j,k}`) by the same
by-hand method as a second check.

**Known false negatives** (all safe — under-report only, `reqpos_probe.c`'s
own stated direction): an `A_ALT`'s common run is prefix/suffix only
(`(?:xabcy|zabcw)` misses `abc`); a run is not merged across repeat
iterations; a lookaround's body is not descended into. See
`wf/wf_run_probe.c`'s header for the full statement.

**Populations**: `bench` is every `bench/*/patterns/*.rx` export across
pcrec-bench's six sets (read-only); `corpus` is every `pattern`/
`pattern-esc` line of every shipped `.rxt`, decoded out of
`--list-source`'s field escaping — the identical population and decoder
`reqpos_census.py` used.

---

## 2. Population: literal-run windows by length and composition

| | bench (N=249) | corpus, byte (N=3,995) | corpus, `-e utf8` (N=3,995) |
|---|---|---|---|
| run >= 4, **all-exact** | 69 | 110 | 167 |
| run >= 4, **has cube-not-singleton** | **9** | **7** | 298 (see caveat) |
| run >= 8, all-exact | 36 | 22 | 23 |
| run >= 8, has cube-not-singleton | **8** | **6** | 6 |

**The utf8 arm's >= 4 cube-not-singleton count (298) is NOT literal-run
population and must not be read as one.** Inspection (150 of the 298 rows
contain neither `[^` nor a wide-class escape and are still all explained)
shows the entire inflation is `.` and `[^...]`'s own UTF-8 multi-byte
LOWERING — a negated/wildcard class splices into a byte-length-branching
alternation whose CONTINUATION bytes (`10xxxxxx`, `0x80-0xBF`) are
trivially one-cube (`K=0xC0,T=0x80`) by construction, with nothing to do
with case-folding or a real subject literal. Every sampled instance was a
bare `.`, `\G.`, `(?m)^.`/`(?m).$`, `\b.\b`, or a `[^c]`-shaped assertion
witness — never a real multi-byte literal. **This artifact is confined to
the 4-7 byte band and vanishes at the >= 8 tier**, where the utf8 arm's
count (29, 6 cube-ns) matches the byte arm almost exactly (28, 6) — so the
row's own ">= 8" headline is unaffected by it. The byte-domain columns are
the ones this census's recommendation is built on, per the row's own
scope statement.

**Caseless population, specifically** (pattern text containing `(?i)` or
`(?i:`):

| | bench | corpus |
|---|---|---|
| total `(?i)` patterns | 12 | 48 |
| of which, a run of length >= 4 | **7** | **0** |

§7 reads this asymmetry.

---

## 3. The nine bench and seven corpus witnesses

Bench (all nine, with the actual literal content):

| pattern | run len | exact / cube-ns | witness content |
|---|---|---|---|
| `altwide/ci-256` | 12 | 0 / 12 | `(?i)` alternation of random 12-char words, purpose-built caseless witness |
| `altwide/ci-512` | 12 | 0 / 12 | same family, wider table |
| `wild-secrets-slack-webhook-url` | 14 | 2 / 12 | `(?i)https://hooks.slack.com/...` — `.` positions land as exact (still cube, `nfree=0`), letters cube-ns |
| `wild-waf-crs-942140-dbnames` | 19 | 2 / 17 | `(?i)` SQL/DB-name keyword alternation |
| `wild-waf-crs-942160-sleep-benchmark` | 9 | 0 / 9 | `(?i:...benchmark...)` |
| `wild-waf-crs-942270-union-select` | 6 | 0 / 6 | `(?i)union.*?select.*?from` — `select` |
| `wild-waf-crs-942360-concat-sqli` | 12 | 1 / 11 | `(?i)` SQL keyword alternation, `group_concat` |
| `loglines/http-5xx` | 12 | — | (not caseless; a one-cube from adjacent-code-point structure) |
| `syntax/mod-s` | 9 | — | (not caseless) |

Corpus (byte domain, all seven): one is a genuine incidental cube unrelated
to case at all, and six are one family:

* `tests/base/alternation_trie.rxt:133` — `[ab]xy|a[xz]yy|[ab]`, a 4-byte
  run via the `{a,b}` class (XOR 0x01).
* `tests/recursion/d27/sr_spellings.rxt:{404,432,448,466,482,499}` — a
  10-byte run `abcdefghi` + a trailing `{j,k}` class (XOR 0x01, K=0xFE,
  T=0x6a) from `^(a)(b)(c)(d)(e)(f)(g)(h)(i)(j|k)(?10)$`-shaped D27
  subroutine-call witnesses. **NOT caseless** — hand-verified independently
  (per-position AND/OR aggregate over `{0x6a,0x6b}` by hand): a second,
  structurally different one-cube family, exactly the row's own claim that
  "every other one-cube class participates identically" and
  `cls_tree_study.md`'s finding that a provenance-blind cube test finds
  case-fold-shaped structure with no fold table and no case involved at
  all — reached here on REAL corpus material, not a constructed set.

---

## 4. The frameless precondition

`docs/design/offset_k_skip.md`'s sibling fact (`emit_vm.c`'s
`RX_VM_FRAMELESS` stamp, `v->has_push ? 0 : 1`, already shipped) is the
row's own precondition: "no label inside the window may be a live resume
target." Compiling the qualifying (best_len >= 4) population at
`--features all -p rx` and reading the emitted stamps:

| | bench qualifying (N=78) | corpus qualifying (N=117) |
|---|---|---|
| engine `dfa` | 57 | 67 |
| engine `vm` | 17 | 46 |
| engine `-` (refused at default flags) | 4 | 4 |
| of the `vm` rows, `RX_VM_FRAMELESS "1"` | 9 / 17 | 30 / 46 |

**The subset that actually matters — VM-route AND cube-not-singleton —
is 100% frameless**: all seven such patterns (the slack-webhook-url
witness and the six `sr_spellings` ones) read `RX_VM_FRAMELESS "1"`. Zero
counter-examples on this population — a clean result, but the population
is seven patterns, not a proof that the precondition always holds where a
cube-run does.

**DFA-route qualifying patterns carry no frame concept at all** — 12 of
the 16 total cube-not-singleton witnesses (`ci-256`/`512`, the four WAF
CRS ones, `http-5xx`, `mod-s`, `alternation_trie`) route through the DFA,
where "frame" is a VM-only idea; the AND-mask form there would need to
embed the compare into the scan/table machinery instead, a DIFFERENT
emission site (`[OPT-K]`'s territory, not `emit_vm.c`'s) that this census
does not further characterize.

---

## 5. Which cycle-1 losing bench cells carry a run

Joining the nine bench cube-not-singleton witnesses against
`docs/dev/optloop/cycle1_rows.tsv` (the same 125-row ranked table
`reqpos_census.md` §3 joined against):

| pattern | regime | rank | score | ratio (pcrec vs algo target) | algo target |
|---|---|---|---|---|---|
| `wild-waf-crs-942360-concat-sqli` | large-subject-throughput | 11 | 0.2435 | **5.41x behind** | re2-longest |
| `wild-waf-crs-942270-union-select` | large-subject-throughput | 15 | 0.1831 | **3.56x behind** | rust |
| `wild-waf-crs-942160-sleep-benchmark` | large-subject-throughput | 17 | 0.1708 | **3.27x behind** | rust |
| `wild-waf-crs-942140-dbnames` | large-subject-throughput | 24 | 0.0866 | **1.82x behind** | re2 |
| `wild-secrets-slack-webhook-url` | large-subject-throughput | 44 | 0.0000 | 0.77x (near-tie) | re2-longest |
| `wild-waf-crs-942360-concat-sqli` | short-subject-search | 27 | 0.0617 | 1.53x behind | rust |
| `wild-waf-crs-942140-dbnames` | short-subject-search | 48 | 0.0000 | 0.61x (win) | rust |
| `wild-waf-crs-942270-union-select` | short-subject-search | 57 | 0.0000 | 0.54x (win) | rust |
| `wild-waf-crs-942160-sleep-benchmark` | short-subject-search | 70 | 0.0000 | 0.41x (win) | pcre2-dfa |
| `wild-secrets-slack-webhook-url` | short-subject-search | 76 | 0.0000 | 0.36x (win) | rust |

**Four of the row's nine real witnesses are cycle-1's own named losses,
all on `large-subject-throughput` — the regime a scan-side cube compare
targets directly** — summing to 0.6840 of the 34-cell losing matrix's
~10.284 total score (6.65%). All four already route through the DFA
(§4), so the mechanism these four need is the scan-side AND-mask form,
not `emit_vm.c`'s fused compare. `ci-256`/`ci-512` and the other four
witnesses (`http-5xx`, `mod-s`, `alternation_trie`, the `sr_spellings`
family) are not in cycle-1's ranked population (`altwide`/`syntax`/
`corpus` are outside `capability@0.1`, and `sr_spellings` is a corpus
correctness witness, not a throughput one) and are not claimed as losing
cells — named here only as additional structural population, per §0.

---

## 6. `(?i)` and the DFA offset-k skip: measured, not argued

`wf/wf_offsetk_probe.c` drives the SHIPPED `pcrec_prefix_ksets`
(`src/opt/prefix_k.c`) directly — not a re-derivation — over every `(?i)`
pattern in bench+corpus (60 total), through the identical D7-fast-path
pipeline prefix `n1_measure.c` established (parse -> altcls -> discharge
-> callgraph -> select_engine -> postresolve -> lower_enc -> build_nfa),
excluding `^`/`\G`-anchored patterns (`pcrec_nfa_has_bot`, 18 of 60) as
outside the unanchored D7 route this walk answers for — the same scope
line `n1_measure.c` draws. `k[0]` (the DFA-start-state offset) is read as
unconstrained (this probe does not build a DFA); every reported fact is
about offsets `j >= 1`, which `docs/design/offset_k_skip.md` §3.5 states
come ENTIRELY from the NFA walk and never from `k[0]`.

| | count |
|---|---|
| `(?i)` patterns, bench+corpus | 60 |
| excluded (anchored / `\G`, out of this walk's scope) | 18 |
| walk producible | **42** |
| has >= 1 case-invariant offset (`count == 1` somewhere, `j >= 1`) | 11 |
| **fully degraded — no invariant offset anywhere** | **31 (73.8% of producible)** |

The fully-degraded 31 include `ci-256`/`ci-512` and three of the four
cycle-1 losing WAF witnesses (`dbnames`, `sleep-benchmark`,
`union-select` — `concat-sqli` is itself `^`-anchored and out of this
walk's scope). This directly confirms the plan row's own claim
("memchr needs one exact byte, a caseless offset has two, so the
caseless twin loses the whole mechanism") as a MEASURED population rather
than the worked single-pattern example (`(?i)needle`) the row states —
and shows the SELECTION-PREFERENCE alternative the row proposes ("scan a
case-invariant offset ... digits/punct/`_` never fold") would still find
nothing on nearly three-quarters of this population: a genuinely
degenerate case, not merely an inconvenient one. A worked positive
control from this same run: `(?i)[0-9a-f]{8}-[0-9a-f]{4}` (a UUID-shaped
witness) DOES carry an invariant offset — its hyphen, at `k=8`, count 1 —
confirming the walk reproduces `offset_k_skip.md`'s own `uuid` worked
example independently.

---

## 7. Scenario classes the corpus lacks — enumerated, not counted

Per the row's own caution ("the shipped corpus may contain NO example ...
the census enumerates scenario classes too"). The corpus's 48 `(?i)`
patterns are overwhelmingly short (2-6 byte) unit witnesses for
case-folding CORRECTNESS (`tests/base/cls_fold.rxt`, `tests/modifiers/
scope.rxt`, `tests/atomic_groups/atomic_case.rxt`) rather than realistic
caseless keyword text, which is exactly why §2's corpus caseless column
reads zero. Scenario classes with no corpus (and mostly no bench)
representative today, each plausibly a long caseless literal window in
real deployment:

* **HTTP header names and values** (`Content-Type`, `Authorization`,
  `X-Forwarded-For`), matched caselessly per RFC 7230 — a common
  real-world caseless-literal shape entirely absent from both populations.
* **Config-key / environment-variable style tokens** (`DATABASE_URL`,
  `AWS_SECRET_ACCESS_KEY`) — the WAF/secrets bench sets already carry an
  adjacent shape (`github_pat_`, `AKIA`) but those are case-EXACT, not
  caseless; a caseless variant is unrepresented.
* **MIME types and protocol schemes** (`application/json`, `text/html`,
  `ftp://`) matched caselessly.
* **Boolean/null literal aliases** (`TRUE`/`False`/`NULL` in
  case-insensitive config or SQL dialects) — `wild-codegrammar-
  json-constant` (cycle-1's own rank-10 losing cell) is CASE-EXACT
  JSON, not a caseless variant; a caseless config-language sibling is
  unrepresented.
* **DNS/hostnames**, which RFC 1035 makes caseless by definition, and
  HTTP methods (`get`/`GET`/`Get`) — both common in log/WAF matching and
  absent from either population as a LONG multi-byte caseless run
  (`altwide/ci-*` tests the mechanism in the abstract, with random rather
  than realistic words).

None of these change §0's verdict (population is not zero without them);
they are recorded as the corpus's/bench's own known gap, matching the
plan row's explicit instruction, not as an additional trigger.

---

## 8. Recommended cycle-3 row shape

Corroborating Frank's 2026-09-25 placement proposal: **`[WORD-FOLD]`
becomes the general form of a cycle-3 "wide literal-run compare" row**,
subsuming:

1. **`[OPT-VMLIT]`'s exact-memcmp case** (K=0xFF at every position) — its
   own trigger read (`vmlit_trigger_read.md` §3) already declines to
   redesign the caseless form and defers to this row by name; §1's cube
   test already treats a singleton as `nfree == 0` of the identical test,
   so the two rows share ONE emission form rather than two.
2. **`[OPT-REQPOS]` tier 2b's caseless carve-out** (`reqpos_census.md`
   §1's known false negative iii, "every caselessly folded literal ...
   contributes no byte, so every `(?i)` pattern's run figure is a
   floor") — the search-side `REQ_RUN` prefilter today can only express
   an exact-byte run; §5's four cycle-1 losing WAF cells are DFA-route
   and exactly the population a caseless-aware `REQ_RUN` widening would
   reach.
3. A DFA-scan-edge landing site for the twelve DFA-route witnesses (§4),
   which is NEITHER `emit_vm.c`'s per-attempt fused compare (VM-only) NOR
   `REQ_RUN`'s single-pass search prefilter (a decision made once before
   the main scan) — a third, so-far-unnamed emission site this census
   did not design, only located by population.

**What is NOT recommended**: building the mechanism on `ci-256`/`ci-512`
alone (a purpose-built abstract witness) or on the utf8 arm's inflated
count (§2's caveat) — the real, load-bearing population is the four
cycle-1 losing WAF cells (§5) plus the offset-k degradation (§6), both
independently measured.

---

## 9. What is owed, and to whom

* **No timing.** Every number above is a count or a stamp read, per D77.
  What a scan-side AND-mask compare costs against today's DFA transition
  loop on the four named losing cells is a Linux measurement in
  `[OPT-5]` STEP 0's shape, owed before any build.
* **The DFA-route emission site is not designed here.** §8 item 3 names
  the gap (neither `emit_vm.c` nor `REQ_RUN` fits the twelve DFA-route
  witnesses) without proposing where it lands — a design note's job, not
  this census's.
* **`[OPT-REQPOS]` tier 2b's caseless widening** needs its own population
  read against `RbSet`'s current exact-byte-only representation before a
  design note can size the change — not attempted here (out of this
  census's scope, per the brief).
* **The VM-route frameless precondition's 100% rate is small-sample**
  (7 patterns) — a larger population (once a design note exists to
  target one) should re-check it rather than assume it generalizes.
