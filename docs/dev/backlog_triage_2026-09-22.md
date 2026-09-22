# Backlog triage — 2026-09-22

[BACKLOG-TRIAGE] (chartered by Frank 2026-09-19, D113; opened 2026-09-22,
lane `backtri`). Places every not-started and dormant-started plan row into
D86's three lane columns (feature / optimization / administrative-structural)
and records each row's D77 trigger and dependencies. Per the brief: this
lane does **not** rank optimization rows against bench data — that is
lane `optrev`'s [OPTLOOP.1.analysis] cause-ranked deliverable, running in
parallel. The optimization column below is ranked by trigger state and
Frank's own recorded sequencing only, and is explicitly **to be merged with
optrev's cause-ranked mechanisms by the manager**.

## 0. Count discrepancy (read this before the numbers below)

The brief and [BACKLOG-TRIAGE]'s own plan.md row both cite **100** /
**102** not-started rows at open, from an unanchored
`grep -n "STATE:not-started" docs/dev/plan.md`. That grep over-counts: rows
now `STATE:started` or `STATE:completed` frequently carry the phrase
"formerly STATE:not-started" in their own history prose (the same
prose-vs-tag confusion this file's own K35/`[MECH-REACH]` lineage warns
about for checks). An **anchored** count —
`grep -cE "^[[:space:]]*- \[[^]]*\] STATE:not-started" docs/dev/plan.md`
— reads **81**. The full anchored tally for the file: not-started 81,
started 19, completed 69, completed-in-place 2, closed-not-started 2,
deferred 4 (blocked 0) = 177 real rows, plus one non-row hit (the format
template line at plan.md:9, `[Mx.y] STATE:<state>`) and one hit from the
brief's own citation of the grep recipe = the observed raw 100/102.
**This report's inventory uses the anchored 81, not 100/102** — see
"Open questions" for the recommended fix to plan.md's own row text.

## 1. Inventory

100 = 81 anchored `STATE:not-started` rows + 12 `STATE:started` rows found
dormant by the same anchored method plus a text scan for `PARKED`,
"stays gated", "NOT SCHEDULED", "D77: not chartered", "WAIT FOR A WITNESS",
"gated on", "behind Frank's ... hold" — checked against every `STATE:started`
row in the file (19 total; [OPTLOOP], [OPTLOOP.1.analysis], [BENCH-REVIEW],
[BACKLOG-TRIAGE] excluded as in-flight per the brief; [SPEC-1], [OPT-5],
[OPT-VMFL] read and found to show no such language — excluded as genuinely
still-progressing umbrellas/lanes, not parked).

Columns: **size** is the row's own stated size where given (three rows
self-declare `sonnet-sized`), else an estimate marked "est."; **trigger**
quotes the row's own D77 language where it states one; **deps** are row
IDs the trigger names.

### 1a. Not-started rows (81)

| ID | Line | Gist | Size | Column | Trigger | Deps |
|---|---|---|---|---|---|---|
| UTF-PAT | 217 | Validate/test that raw UTF-8 pattern-text already works as Frank guessed | M est. | feature | Frank's chartering guess ("probably close") — needs the validation run itself | M5.0 |
| UTF-RW | 220 | Harvest real-world non-English UTF-8 regexes + a class-shape census, to catch English-bias gaps | M est. | feature | sequenced after M5.0 stages 3-5 (now landed) | M5.0 (met) |
| FORM-CHAR2 | 223 | [FORM-CHAR]'s cls-fold measured SLOWER on its one bench witness; investigate per-site instruction counts | S sonnet-sized | optimization | bench O-19 §1 finding — already measured | FORM-CHAR |
| SEL-SIZE | 224 | Should `auto` decline a warned-size DFA when a VM form exists? ([LIM-2] N1 found a live case) | M est. | optimization | measured accidental case from LIM-2 N1 — already exists | LIM-2 |
| LIM-OVR | 225 | `--list-limits`' `override` column can't express two-lever (raise-only flag + `-D` default) rows | S sonnet-sized, admin column (self-declared) | admin-structural | O-18 §3 finding — already measured | none stated |
| READ-BYTES | 226 | Emit byte comparisons as char literals/comments, not raw decimal, for human readability | S est. | admin-structural | Frank's UNSCHEDULED charter; no trigger stated | none |
| MACPORT-XARGS | 229 | `run_rxtsource_tests.sh` legs B/C use GNU-only `xargs -a`, never run on darwin | S admin column (self-declared) | admin-structural | already measured (14 pre-existing failures, A/B'd) | LIM-OVR (bundle) |
| M3.0 | 254 | Design gate: match-START finding under bounded memory before any streaming code | L est. (milestone) | feature | none stated — design gate is itself the next step | OS-3 |
| M3.1 | 255 | `*_stream_*` API for the DFA engine + chunk-boundary tests | L est. (milestone) | feature | M3.0's design gate landing | M3.0 |
| M7.0 | 263 | Milestone: differential fuzzing vs libpcre2, freestanding/embedded profile, PCRE2 testdata import | L est. (milestone) | feature | spine order (D13/journal 2026-08-13): after M3 | M3 |
| EMIT-ENTRIES | 269 | Emit only the entry points (`search`/`match`) a caller's dependency graph actually needs | M est. | optimization | Frank's 2026-09-21 charter; no measurement trigger stated | none |
| LANG-1 | 270 | Language-integration studies wave 1 (C, Rust, C++): write-up doc + built/tested examples per language | L est. (3 studies) | admin-structural | Frank's 2026-09-21 charter | none |
| LANG-2 | 271 | Language-integration studies wave 2 (JS/TS via native addon vs Wasm) | M est. | admin-structural | wave 1's outcome argues the next language | LANG-1 |
| TT-13 | 491 | Tier the mech battery by CADENCE not a constant — mech rows+cost doubled 08-23→09-04 | M est., admin column (self-declared) | admin-structural | Frank: "schedule ... for later" — explicitly deferred | none |
| TT-14 | 492 | Exec-batching design for the whole suite, switchable, Linux-safe | L est., admin column (self-declared) | admin-structural | Frank's Mac-timing charter; already largely delivered as [TT-4M]/[TT-4M-TIME] (see open questions) | TT-4M family |
| TT-15 | 493 | A cloud (AWS EC2) runner as a cost/latency alternative to 4-hour local runs | M est., admin column (self-declared) | admin-structural | Frank's cost argument; no measurement trigger stated | TT-14 |
| SPEC-1.11 | 566 | `docs/spec/extending.md` — the recipe-per-extension-kind contract for post-1.0 extenders | M est., BOONIES (self-declared) | admin-structural | boonies (late-game); no trigger | SPEC-1 |
| GUIDE-1 | 569 | The user guide, `docs/guide/` | L est. | admin-structural | none stated (chartered as [REL-1.3]) | REL-1 |
| OPTLOOP.1.impl | 596 | Cycle 1's implementation batch: ≤3 mechanisms as axes, bench carve-out, `make test`, full suite at cycle end | M est. | optimization | OPTLOOP.1.analysis's mechanism batch landing | OPTLOOP.1.analysis |
| EDGE-STAMP | 598 | An integer scan-edge-count stamp so bench's [B32] covariate stops reading an emitted comment | S sonnet-sized | admin-structural | bench outbox O-36 — already measured need | OPT-5 |
| V-A | 634 | PCRE2 compat layer + POSIX `regex.h` shim | L est. | feature | none stated | DD-3 |
| V-B | 635 | Language bindings over the generated C (cheap: no runtime dep on pcrec) | M est. | feature | none stated | none |
| V-C | 636 | A grep CLI built on pcrec — end-user speed demonstration | M est. | feature | none stated | none |
| V-D | 637 | Translators from other regex syntaxes (grep/egrep, python `re`, POSIX) into base tier | L est. | feature | DD-11's definitions table made this cheaper (already landed) | DD-11 |
| LIB | 638 | Subpattern libraries | L est. | feature | "depends on rxt format" — [DD-13b] | DD-13b (DD-13) |
| V-E | 639 | Multi-pattern compilation units — recorded design input, explicitly NOT chartered | L est. | feature | D77: "no new effort at 95% of the [win]" — not met | D88 |
| V-F | 698 | Source-scan transformer | M est. | feature | none stated (title only) | none |
| V-G | 710 | User-facing regex testing tool | M est. | feature | none stated (title only) | none |
| V-H | 726 | Debug/trace emission modes (VM tracer, resume-frame trace) | M est. | feature | scheduled with [M4.5]'s bring-up (already past); also DD-8's named future sub-part | DD-8 |
| EMIT-SET | 753 | Caller controls what's emitted into the C file (drop unused entries like `search`) | M est. | optimization | D88 (one artifact per file); no measurement trigger | EMIT-ENTRIES |
| PAT-LINT | 754 | Ahead-of-time optional pattern analysis/linter | M est. | feature | none stated (title only) | none |
| V-I | 783 | Named-results copy helper (library convenience API) | S est. | feature | none stated (title only) | none |
| SIMD-META | 801 | Meta-plan row for `studies/simd1` | S est. | optimization | D119: SIMD explicitly deferred to the end of the loop | OPT-SIMD |
| ENG-THIN | 851 | MRL clamp gating/thinning | M est. | optimization | none stated (title only) | none |
| ENG-PGO | 884 | Profile-guided (findings-file subject profile) selection point beside OPT-A's rarest-byte prior | M est. | optimization | cross-note on [OPT-4]'s default decision | OPT-A, OPT-4 |
| ENG-DIRECT | 924 | Own the frameless-VM "direct DFA" shape ENG-VMFL's STEP 0 found ×9 faster | M est. | optimization | **already measured** (bench O-14, 2026-09-02, ×9.0) | OPT-VMFL |
| ENG-COUNT | 996 | Large bounded counts on the DFA side — explicitly low priority per Frank | L est. | optimization | Frank: "not sure it's worth it"; UNSCHEDULED, opens on measured need | none |
| ENG-CLAMP | 997 | Deferred per-quantifier K downshift | M est. | optimization | none stated (title only) | K22 |
| ENG-LOOK | 1018 | Lookaround by product construction in the DFA (one-char fixed lookaround as an alphabet-context assertion) | L est. | optimization | M6.6.1's design hand-off (already landed) | DD-11 |
| ENG-CUT | 1061 | Full cut construction for atomic groups (replace `A_ATOMIC(X)` with a cut-free deterministic splice) | L est. | optimization | chartered at [M6.4.1]'s design merge | M6.4.1 (met) |
| M4-CALLOUTS | 1062 | Module `callouts` step 2 (behavior), ABI ruled by D38/D39 | M est. | feature | "awaits M4" — **M4 has shipped** (see open questions) | M4 (met, unconfirmed) |
| M4-SUBST | 1098 | Compiled substitution (template compiler, matcher-independent) | L est. | feature | Frank: need not wait on M4 either; M4 has shipped | M4 (met) |
| DD-2 | 1284 | VM step/match limits as a robustness (not security) boundary — two named bounds | M est. | feature | "with M4 design" — **M4 has shipped** | M4 (met, unconfirmed) |
| DD-7 | 1285 | Engine unification ownership — SPLIT 2026-08-14; the capture-prefilter half already answered, `^`/`$` half re-homed to ENG-ABS | S est. — see close/fold §3 | admin-structural | M4.3 panel (unconfirmed whether it ran) | ENG-ABS |
| DD-1 | 1288 | Unicode case-fold design (multi-byte pairs, one-to-many, fold-before-negate) — **already delivered**, see §3 | — | feature | "before M5" — **M5 shipped and this content shipped with it** | M5 (met, superseded) |
| DD-12 | 1289 | The UTF architecture sketch — one-line stub, likely superseded by the real M5.0 design | S est. — see close/fold §3 | feature | none (stub never completed) | M5.0 |
| DD-6 | 1415 | Multiline `^`/`$` as DFA state context (with the assertions module) | M est. | optimization | "with assertions module" — **M6 assertions has shipped** | M6 (met, unconfirmed) |
| DD-3 | 1539 | Generated-API versioning/compat policy for vendored consumers | M est. | admin-structural | "before M3" — not yet due (M3 still not-started) | M3 |
| FREESTANDING | 1540 | Libc-free emission profile (scalar prefilter fallback for a no-glibc build) | M est. | feature | Frank: "File for boonies" — boonies, no measured need | DD-5 |
| DD-5 | 1541 | `--std-c` portable emitter fallback (switch-based) | M est. | feature | none stated | FREESTANDING |
| DD-10 | 1543 | Bound `compile_ast`/`clo_visit`'s remaining unbounded C-stack recursion (musl 128 KB stacks) | M est. | admin-structural | named specifically as a thread-safety item (D19), not just robustness | TS-4 |
| OS-0 | 1556 | The optional ENGINE FINDER module (D20): drive the generator once per point of a product-of-sets request | L est. | admin-structural | none stated | none |
| OS-2 | 1557 | Does the ascii/utf8 encoding axis collapse to one DFA emitter shape? PREDICTED yes | S est. | admin-structural | "Measure when M5 lands" — **M5 has landed, measurement is now due** | M5 (met) |
| OS-3 | 1558 | Is streaming a wrapper over the existing engines? PREDICTED no, with counter-evidence already in hand | S est. | feature | feeds M3.0's design gate directly | M3.0 |
| OS-4 | 1559 | Is the ENG_UNANCH/ENG_ATTEMPT anchoring split earning its keep? Never measured | M est. | optimization | "Measure the cost of the split on the known-slow shape" — named but not run | DD-7, D8 |
| SR-5 | 1604 | Guard the fast-path CLAIM with a real check rather than an assertion | S est. | admin-structural | none stated (title only) | none |
| SR-6 | 1617 | Move module handlers to their own module translation units | M est. | admin-structural | none stated (title only) | none |
| SR-10 | 1666 | "Eat our own dogfood": the registry `syntax` column as a pcrec-compiled, self-checking pattern set | M est. | admin-structural | Frank's [DD-14] ASK 3 cross-note | DD-11, DD-13 |
| BENCH-CEIL | 1749 | The expert-hand-tuned-C ceiling arm for the bench | M est. | admin-structural | none stated (title only, bench-owned) | BENCH-1 |
| OPT-A | 1873 | Pair-scan/rarest-byte prefilter — pcrec 3.0-6.5× behind pcre2-jit on `\bat ` at 1 MB | L est. | optimization | **already measured** (bench O-8, 2026-08-29) | DD-13b (freq band) |
| OPT-VEDGE | 1877 | View-tolerant scan edge: relax `scanedge.c`'s precondition | M est. | optimization | **already measured** (bench O-12 §4, two artifacts at 93.7% of the size cap) | ART-SIZE |
| OPT-NEG | 1880 | Scan a negated singleton class (`\N`) as "does not equal" instead of a bitmap | S OPTIMIZATION column (self-declared) | optimization | Frank's "apropos of nothing" question; answer already derived (no) | none |
| FEAT-VAR | 1881 | Pattern variables: caller-supplied string bound into the pattern at match time | L est., FEATURE column (self-declared) | feature | Frank: "at some point" — explicitly not-now | none |
| OPT-ALTHASH | 1882 | k-byte block hash for wide alternations (vs one-byte-at-a-time trie walk) | L est. | optimization | Frank: explicitly NOT folded into current work | none |
| OPT-CLSPACK | 1884 | Pack N disjoint char classes into one array with a membership tag, if it impacts performance | M est. | optimization | conditional on measured impact — not yet measured | FORM-CHAR2 |
| PFX-1 | 1886 | Per-artifact `-p` prefix only on exported items, not internal statics/labels/macros | S est. | admin-structural | Frank's D96 ADMIN/ABI charter | none |
| OPT-VMLIT | 1888 | Literal-word VM emission: avoid one-byte-per-label consume chains, prefer memcmp-shaped code | M est. | optimization | **partially measured** ([OPT-5] STEP 0, worst case ~2×) | OPT-5 |
| OPT-SIMD | 1921 | SIMD emission for candidate scanning, ISA-neutral from day one (x86 + aarch64) | L est. | optimization | D119: explicitly LAST, no SIMD until the algorithmic phase ends | OPT-A, OPT-B |
| OPT-B | 1942 | Profiled code-level optimization (branch predictability, memory layout), after OPT-A | M est. | optimization | explicitly sequenced after OPT-A | OPT-A |
| OPT-C | 1943 | Compile-time optimization (including what gcc does with pcrec's output), explicitly last | M est. | optimization | explicitly sequenced last | OPT-A, OPT-B |
| OPT-D | 1945 | Deduplicate byte-identical read-only data across an artifact's machines (e.g. shared forward/reverse class bitmaps) | S est. | optimization | Frank's charter is itself the trigger ("no impact space savings") | none |
| TS-4 | 1955 | A `tests/cli` stack-depth case binding `compile_ast`'s recursion budget | S est. | admin-structural | named as DD-10's necessary companion check | DD-10 |
| MECH-3 | 1967 | A measurement wrapper enforcing provenance (interleaved A/B, N trials, load before/after, stamped record) | M est. | admin-structural | named as the OPT waves' "intended measurement vehicle" — precondition for BENCH-1 | none |
| PC-2 | 1972 | Periodic re-survey of pcre2syntax.html against the compliance page | S est. | admin-structural | recurring maintenance, no single trigger | none |
| PCRE2-UP | 1973 | A PCRE2 git sub-repo inside pcrec for differentials against newer-than-10.46 constructs | M est. | admin-structural | explicitly "NOT started, no measured need yet" | none |
| ENC-MODEL | 1979 | The full encoding model: pattern encoding vs subject encoding as translation tables | L est., boonies (self-declared) | feature | boonies, unscheduled | DD-12 |
| FOLD-BASE | 1980 | Diacritic/base-character folding (canonical equivalence + compatibility folding) | L est., boonies (self-declared) | feature | boonies, unscheduled | DD-1 (now delivered — see §3) |
| MULTI-PAT | 1981 | Compile a pattern SET into one scanner artifact (Hyperscan-style) | L est., boonies (self-declared) | feature | boonies, from the Hyperscan discussion | V-E |
| JSONL | 1983 | JSONL as an application domain, five tiers from validator to full parser | L est., boonies (self-declared) | feature | boonies, from watching pcrecdev2's slow reader | V-C |
| WORD-FOLD | 1984 | Word-wide (8-byte) cube compare for literal runs, vectorized across positions | M est., boonies (self-declared) | optimization | boonies investigation, from the cls-fold/cube discussion | CLS-TREE |
| TT-4M-TIME | 1988 | The clean, quiet-box, post-prefix-fix `HARNESS_BATCH` timing number | S est. | admin-structural | "owed 2026-09-10" — **already measured**, per `tt4m_time.md` (see open questions) | TT-4M |

### 1b. Dormant `STATE:started` rows (12)

The three Frank named as PARKED plus nine more found by the same text scan.

| ID | Line | Gist | Size | Column | Trigger | Deps |
|---|---|---|---|---|---|---|
| ENG-ISL | 980 | Alt-island trie mechanism, mid-flight | L (in progress) | optimization | **PARKED 2026-09-21** into [BACKLOG-TRIAGE] (D114) explicitly | none stated |
| DD-13 | 1359 | .rxt-format-driven `(?&name)` composition/library feature, mid-flight (several waves landed) | L (in progress) | feature | **PARKED 2026-09-21** into [BACKLOG-TRIAGE] (D114) explicitly | none stated |
| DD-13b.W1.3 | 1395 | DD-13's Wave 1.3 (composer, name grammar, altwide dogfood, composition identity proof) | M (delivered, sub-row) | feature | parked with its parent DD-13 (D114) | DD-13 |
| CLS-TREE | 1986 | The general class-matcher kit (BSEARCH/PAGE64/BITMAP/etc., DP sectioning) — study done, build not chartered | L est. | optimization | **PARKED 2026-09-21** into [BACKLOG-TRIAGE] (D114) explicitly | none stated |
| TT-4M | 306 | Batched compile+dispatch (STEP 1/2c/2d landed); re-attribution of the ~9.5% vs 4.28×/18.65× gap | M est. | admin-structural | row's own text: **"NOT SCHEDULED — do not charter without Frank's word"** | tt4m_time.md |
| DD-8 | 1287 | `--emit-ir` table-contract adoption — **the chartered sub-task is DONE**; `--emit-dot` and DFA/prefilter listing sections left unscheduled | S est. (remaining tail) | feature | row's own text: "stays started for its future sub-parts" — none scheduled | V-H |
| DD-11 | 1416 | Definitions table (`--list-definitions`) — **chartered work DONE**; follow-on [DD-11.5]/[DD-11.6] stay gated | S-M est. | admin-structural | row's own text: "gated on M6.6" — **M6.6 completed 2026-08-24, gate is stale** (see open questions) | M6.6 (met, unconfirmed) |
| CC-CLANG | 1542 | Clang-as-second-compiler (STEP 1/2 merged; confirmed by `git merge-base`); STEP 3 (bench partial cc axis) remains | S est. (STEP 3 only) | admin-structural | row's own text: STEP 3 "behind Frank's perf hold" | I-22 (bench) |
| BENCH-1 | 1748 | Feature-spanning benchmark + prioritizer — work has moved to the bench repo; row now reads "Bench-owned; pcrec owes the registry seed and the answers" | — see close/fold §3 | admin-structural | superseded in spirit by D119's OPTLOOP cause-taxonomy prioritization | ENG-ABS (first mechanism) |
| OPT-3 | 1843 | DFA scan-edge premultiply (STEP 1 measured+merged); STEP 2 candidates ruled out on the numbers | S est. (remaining tail) | optimization | row's own text: "D77: not chartered" (needs a non-periodic subject, I-10) | none |
| OPT-4.2 | 1876 | Nullable-collapse prefilter decline — o42's witness-gap ruled by Frank | — closed in spirit | optimization | row's own text: **"WAIT FOR A WITNESS — no row, no hunt"** | none |
| ENG-ABS | 1889 | Second mechanism (unwrapped-forward-DFA anchored match) landed; FIRST mechanism (`^`-absorption) never opened | S est. (remaining tail) | optimization | row's own text: "stays gated on [BENCH-1]'s `^`-on-some-branches case ... is NOT opened" | BENCH-1 |

**Total inventory: 93 rows** (81 not-started + 12 dormant-started).

## 2. The three columns, ranked

Ranking criteria in order: (a) Frank's own recorded sequencing; (b) a
measured trigger beats an unmeasured one; (c) unblocks other rows;
(d) small-before-large when otherwise equal (D113).

### 2a. Feature column

1. **M3.0** — design gate for match-START finding under bounded memory.
   Frank's own ratified spine order (D13, 2026-08-13: "STD1 → M4 → M5 → M6
   → M3 → M7") makes this the next spine milestone; M4/M5/M6 are all
   shipped. Unblocks M3.1, OS-3, DD-3.
2. **DD-1 — recommend CLOSE, not opened** (see §3): its content already
   shipped under [M5.0] stage 4. Removing it from the feature queue is
   itself the action.
3. **M4-CALLOUTS / M4-SUBST / DD-2 / DD-6** — all four name "M4" (or the
   assertions module) as their trigger and that milestone is now complete;
   none has been reopened. Grouped together because their common blocker
   (M4/M6-assertions landing) is already MET — a manager read is owed
   before any one of them is chartered (see open questions; DD-6 sits in
   the optimization column by content but is grouped here by shared
   trigger state).
4. **UTF-RW** — the real-world non-English regex harvest: sequenced after
   M5.0 (landed), guards against the English-bias gap Frank explicitly
   named, and is cheap (a study, not an engine change).
5. **UTF-PAT** — validates Frank's own "probably close" guess about raw
   UTF-8 pattern text; small, already-scoped, no design needed.
6. **OS-3 / OS-2** — both explicitly measurable now (M5 has landed for
   OS-2; OS-3 feeds M3.0 directly) and both are read-only measurement
   rows, cheap before M3 starts.
7. **DD-12 — recommend CLOSE or heavy rewrite** (see §3): superseded stub.
8. Everything else (V-A..V-I, LIB, LANG-1/2, FREESTANDING, DD-5, GUIDE-1,
   ENC-MODEL, FOLD-BASE, MULTI-PAT, JSONL, M7.0, PAT-LINT) has no measured
   trigger and no Frank sequencing beyond "boonies"/"expand on arrival" —
   ranked below the spine and M-trigger cluster above, in the order
   Frank filed them (LIB blocks on DD-13b, which is itself parked, so LIB
   cannot open before DD-13 is dispositioned).

### 2b. Optimization column

**Note (per the brief): this ranking is NOT a bench-priority ranking — it
uses trigger state and Frank's sequencing only, and is to be merged with
lane `optrev`'s cause-ranked mechanisms.**

1. **ENG-DIRECT** — trigger already measured and dated (bench O-14,
   2026-09-02, ×9.0 on frames-1 artifacts); Frank's own text: "this IS the
   direct-DFA idea."
2. **OPT-A** — trigger already measured (bench O-8, 2026-08-29,
   3.0-6.5× behind pcre2-jit); named as the FIRST step of BENCH-1's own
   stated optimization workflow.
3. **OPT-VEDGE** — trigger already measured (bench O-12 §4, two artifacts
   at 93.7% of the size cap); Frank's own ruling opened it as "the own
   row."
4. **OPT-VMLIT** — partially measured ([OPT-5] STEP 0); needs one more
   named instrument (`l-03`) to complete the trigger.
5. **OPTLOOP.1.impl** — blocked only on OPTLOOP.1.analysis's own output
   landing; this is the loop's own next step by construction.
6. **ENG-ABS / OPT-4.2** — both explicitly "wait for a witness" per
   Frank's ruling; grouped because BENCH-1 (their shared source of
   witnesses) is itself dormant/bench-owned — resolving BENCH-1's status
   likely resolves both at once (see §3, §4).
7. **OPT-3 (remaining tail)** — small (needs one non-periodic subject),
   explicitly D77-gated, otherwise done.
8. Everything else without a measured trigger (SEL-SIZE, FORM-CHAR2,
   EMIT-ENTRIES, EMIT-SET, ENG-THIN, ENG-PGO, ENG-COUNT, ENG-CLAMP,
   ENG-LOOK, ENG-CUT, OPT-NEG, OPT-ALTHASH, OPT-CLSPACK, EDGE-STAMP,
   WORD-FOLD, DD-6, DD-7, OS-4, SIMD-META, OPT-B, OPT-C) — ranked by
   Frank's own explicit sequencing where stated (OPT-B after OPT-A,
   OPT-C last, SIMD-META/OPT-SIMD last of all per D119).
9. **OPT-SIMD** — explicitly last by D119 charter ("no SIMD until the
   end"); this is Frank's sequencing, stated with maximum force, so it is
   ranked at the very bottom regardless of any other criterion.

### 2c. Administrative/structural column

1. **MACPORT-XARGS** — *(SUPERSEDED at delivery: lane admin1 found the charter already fixed by Frank on 2026-09-10, fb1b9c5e, the row never re-flagged — archived 2026-09-22; the "14 failures" below is the pre-fix figure.)* already measured (14 pre-existing darwin failures,
   A/B'd), small, self-declared admin column, blocks nothing else but
   fixes a real coverage gap (two legs of the harness never run on darwin).
2. **LIM-OVR** — already measured (O-18 §3), small, self-declared admin +
   sonnet-sized, explicitly meant to bundle with MACPORT-XARGS.
3. **DD-11 (follow-on tail)** — its stated gate (M6.6) is complete; if
   confirmed (see open questions) this becomes immediately actionable and
   is small (a data-table follow-on, not a new design).
4. **EDGE-STAMP** — already measured need (bench outbox O-36), small,
   sonnet-sized, unblocks a bench covariate that today reads an emitted
   comment as its instrument (fragile by construction).
5. **TT-4M-TIME** — already measured per `tt4m_time.md` (see open
   questions on why this row is still open) — closing it is nearly free.
6. **CC-CLANG (STEP 3 tail)** — steps 1-2 already merged; STEP 3 needs
   only Frank lifting "the perf hold," not new design.
7. **MECH-3** — named repeatedly across the journal as the precondition
   for trustworthy A/B measurement in every OTHER row in this column and
   the optimization column; ranked ahead of the remaining untriggered
   admin rows on "unblocks other rows."
8. **BENCH-1 — recommend CLOSE/FOLD in spirit** (see §3, §4): its
   remaining charter now reads "Bench-owned," which the D119/D78 model has
   already made structurally true.
9. Everything else with no measured trigger (SR-5, SR-6, SR-10, TT-13,
   TT-14, TT-15, DD-3, DD-10, TS-4, PFX-1, PC-2, PCRE2-UP, OS-0,
   BENCH-CEIL, SPEC-1.11, GUIDE-1, LANG-1, LANG-2), ranked by Frank's own
   sequencing where stated (DD-3 explicitly "before M3," so behind M3.0;
   PCRE2-UP explicitly "no measured need yet," ranked near the bottom).

## 3. Candidates to CLOSE or FOLD

- **DD-1 — CLOSE.** Its entire remaining charter after the OS-1/D23
  ASCII-fold closure — "multi-byte fold pairs, one-to-many foldings and
  the fold-before-negate rule over byte-range trees" — is verbatim what
  `docs/dev/lanes/CLAUDE.md`'s `utf8s4_report.md` entry describes as
  delivered: "**[M5.0] STAGE 4, DD-1's FOLD CLOSURE** ... `(?i)k` under
  `-e utf8` matches U+212A: `CaseFolding.txt` vendored, the fold
  published as two `PcrecFold` objects the ENCODING chooses between,
  the caseless backreference folding code points in the artifact." DD-1's
  own plan.md text was never updated to point at this landing (evidence:
  the row still reads "What remains here is genuinely Unicode..." with no
  closure note, plan.md:1288).
- **DD-12 — CLOSE or fully rewrite.** The row is a one-line, unfinished
  stub ("— the UTF ARCHITECTURE sketch (Frank,", plan.md:1289) that
  predates the actual UTF-8 architecture built and merged across
  [M5.0]'s five stages (`docs/design/utf8_design.md` and its stage
  reports). Recommend closing as superseded-by-implementation, or if
  Frank wants the sketch preserved as a historical design artifact,
  rewriting it as a pointer to `utf8_design.md` rather than leaving an
  unfinished sentence as an open queue item.
- **DD-7 — likely CLOSE, verify the M4.3 panel.** The row's own text
  already dispositions both of its halves: the capture-prefilter question
  was "ANSWERED by engine_m4.md §7.1," and the `^`/`$` absorption question
  was explicitly "RE-HOMED to [ENG-ABS]." What is unverified is whether
  "pending the M4.3 panel" ever resolved — a grep for "M4.3" beyond this
  row found no other hit in `plan.md` or `decisions.md`, suggesting either
  the panel happened under a different name or the row is simply stale.
  Recommend the manager grep `dev_journal.md` for "M4.3" before closing.
- **BENCH-1 — FOLD into D119's OPTLOOP model.** BENCH-1's charter was "a
  benchmark that SPANS the feature set" plus "the new PRIORITIZER ... a
  worklist generator" for the OPT waves. Both jobs are now done by a
  different, later mechanism: the bench repo itself (D78, an entire
  sibling project) and D119's cause-taxonomy-plus-measured-gap loop
  (2026-09-21), which explicitly names `[OPTLOOP.1.analysis]` as cycle
  1's own worklist generator. BENCH-1's own most recent text already
  concedes this ("Bench-owned; pcrec owes the registry seed and the
  answers"). Recommend folding BENCH-1's remaining open item (the
  "expert-C ceiling arm," [BENCH-CEIL]) directly into the OPTLOOP
  machinery and closing BENCH-1 itself as superseded by D78+D119.
- **OPT-4.2 — CLOSE as a standing ruling, not an open row.** Frank's own
  text is a closed disposition ("WAIT FOR A WITNESS — no row, no hunt");
  there is nothing left to triage here except recording that the
  "impact bounded" finding stands. Recommend converting this from a
  `STATE:started` row to a short note in `known_issues.md` or
  `decisions.md` if it isn't already cross-referenced there, and closing
  the plan row.
- **TT-14 — likely FOLD into TT-4M/TT-4M-TIME.** TT-14's charter
  ("figure something out ... batching ... switchable ... runs on linux
  fine") is, by content, exactly what [TT-4M] built and
  [TT-4M-TIME] is finishing measuring. TT-14's own row text was not
  checked for a closure note in this pass (out of scope for a deep read
  at this lane's size budget) — flagged as a probable duplicate for the
  manager to confirm and fold rather than close outright, since TT-15
  (the cloud-runner idea) may still be a live, distinct alternative TT-14
  was gating.

## 4. Top proposal — one row per column

- **Feature: [M3.0]** — the design gate for match-START finding under
  bounded memory. It is the ratified next spine milestone (D13's order,
  M4/M5/M6 all shipped), it is explicitly a DESIGN step (cheap before any
  code), and two other not-started rows (M3.1, OS-3, DD-3) are waiting on
  it directly.
- **Optimization: [ENG-DIRECT]** (pending reconciliation with `optrev`'s
  cause-ranked output, per the brief) — the only optimization-column row
  with BOTH a dated, named measurement (bench O-14, ×9.0) AND Frank's own
  words identifying it as the mechanism ("this IS the direct-DFA idea").
  If `optrev`'s cause taxonomy ranks a different mechanism higher on
  measured-gap grounds, that ranking should win — this lane has no bench
  data of its own to arbitrate that.
- **Administrative/structural: [MACPORT-XARGS] + [LIM-OVR] together** —
  both already measured, both small, both self-declared as a bundle by
  the manager who chartered them ("bundle into the next admin lane"); a
  natural single small lane that also closes a real darwin coverage gap
  (two harness legs never run on this box today).

## Open questions

1. **The row-count discrepancy itself.** [BACKLOG-TRIAGE]'s own plan.md
   text says "102 not-started rows at open"; the brief said "100." An
   anchored grep finds 81. Recommend the manager re-pin plan.md's own
   [BACKLOG-TRIAGE] row text to 81 and note the anchoring lesson (prose
   mentions of a past state contaminate an unanchored `grep -n`) as a
   `docs/dev/learnings.md` §3 addition — it is the same failure class as
   the "reader whose text never cites the number still moves with it"
   lesson already recorded there for other checks.
2. **DD-11's M6.6 gate.** The row says it "stays STARTED only for the
   M6.6-gated follow-on [DD-11.5]/[DD-11.6]." `plan_completed.md:3658`
   confirms `[M6.6] STATE:completed` (closed 2026-08-24). The gate
   condition appears to have been met for nearly a month without the
   follow-on being reopened or the row's own text being revisited.
3. **M4/M6-assertions-gated rows never reopened.** DD-2, M4-CALLOUTS,
   M4-SUBST all name "M4" as their trigger; DD-6 names "the assertions
   module" (part of M6). `rel1a_report.md` (docs/dev/lanes/CLAUDE.md)
   records that "M4/M5 shipped" as of the README rewrite, and M6.0 is
   `STATE:completed` in `plan_completed.md`. None of these four rows'
   plan.md text shows a post-landing revisit. This reads as a systemic
   gap rather than four independent oversights — worth a standing rule
   ("when a milestone completes, grep plan.md for rows naming it as a
   trigger") rather than four one-off fixes.
4. **CC-CLANG's stale "awaiting merge review."** The row's own text
   still reads "DELIVERED GREEN 2026-09-01 01:32, awaiting merge review,"
   but `git merge-base --is-ancestor origin/lane/cc HEAD` confirms
   `lane/cc` IS merged, and later commits (`adc0f5a8`, `6d92d3b5`,
   `8e0b6245`) build on [CC-CLANG]'s own mechanism. The row text was
   never updated after the actual merge; only STEP 3 (behind "Frank's
   perf hold") is genuinely open.
5. **TT-14 vs TT-4M/TT-4M-TIME.** Flagged above (§3) as a likely
   duplicate; this lane did not do a full read of TT-14's row (its
   snippet alone strongly suggests overlap) to avoid scope creep on a
   pure-triage pass — the manager should confirm before folding.
6. **BENCH-CEIL's relationship to BENCH-1's proposed fold.** If BENCH-1
   folds into D119/OPTLOOP as recommended (§3), BENCH-CEIL (bench-owned,
   depends on BENCH-1's instrument) needs its own dependency line
   re-pointed at whatever OPTLOOP/bench mechanism survives — not
   resolved here, named so it isn't dropped.
7. **Size estimates are largely "est."** Only 3 of 93 rows self-declare a
   size (`sonnet-sized`); this report's S/M/L column is this lane's own
   judgment call on scope as described in each row's text, not a
   measurement. Treat accordingly when sequencing lane launches.
