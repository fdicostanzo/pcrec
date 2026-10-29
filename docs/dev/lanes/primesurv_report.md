# primesurv — cross-bench survey for the primed optimization list

Lane primesurv (sonnet), 2026-10-29. Read-and-analyze only: nothing under `src/`, `cli/`, `lib/` or `memfn/` edited, no compile, no timing. Every number is a bench figure copied from a ledger, report or earlier lane note; ratios are the sources' own (`X/Y`: x2.0 = pcrec takes twice as long). Where a number is my arithmetic on a source figure it says so.

## Summary

1. **Premise note (not a failure): the new regular window (O-111) holds no library comparison.** It ran pcrec at two pins only (capability and syntax, auto and nocaps; no jit, rust, re2, interp). So the "regular bench" contributes pcrec-vs-pcrec movers (the [SCANEDGE-SET] two-sign finding, grp-callout) and no new library gaps. The regular-tier library gaps are the 10-26 `targets_2026-10-26.md` rows (pcrec 9ae59f5d4 against the 6b2dbd3e re-baseline engines); they predate abi 87-91 and are re-measure candidates, not fresh evidence.
2. **Against the D119 target criterion (jit never the target, vectorscan excluded, rust SIMD separated, assisted rows labelled) far fewer cells trail than the headline ratios suggest.** Of the cells the three new readouts name as slow, only subst 5b (rust x3.16, scalar re2 and interp are slower than pcrec), subst 7 (interp x1.29) and unusual js-1m (onig x1.74) trail a non-jit native engine; the unusual default-arm give-ups trail the interpreter by answering nothing. Everything else trails jit alone, or an assisted rust/re2.
3. **Six groupings, three of them already in hand.** (G1) start recovery from a landmark = P1, designed. (G2) VM frame retention across a possessive loop = P2, plus its likely consequence the recursive-member rates = P3; both owed by l9look. (G3) scan-edge admission and selection = P4 and P8, which are ONE mechanism (`src/opt/scanedge.c`), proposed merged. (G4) landmark byte and re-entry on VM routes = P5, mostly landed as [REQRUN-VM]; two cells to re-measure, then one residual. (G5) NEW P9: window-context patterns with a leading keyword set (`\b(?:fail|abort|panic)\b.{0,N}?\b...`), five cells, x19 against rust. (G6) NEW P10: required-byte reject on hazard subjects, five cells, auto is x62-183 slower than its own forced VM.
4. **Ranking by cells moved x gap:** P2 (about 35 give-up cells, categorical) > P1 (3 firm cells, x3; 2 more by stamp inference) > P9 (5 cells, x19 vs rust, x1.9 vs jit, SIMD-confounded) > P10 (5 cells, hazard-subject only) > P4+P8 (5 regressions of x1.07-1.20, population of the relaxation unmeasured) > P3 (6 cells, one trails an eligible engine) > P5 residual (2 cells, re-measure first). P6 and P7 do not survive: neither is a library gap (section "Candidate rows").
5. **Bench asks that turn the most guesses into diagnoses:** a full-roster re-sample of the regular sets at or after abi 91 (one window, jit + rust + re2 + interp + pcrec-auto), `pcrec-auto-noedge` on the five P4 cells, and a quiet re-run of the unusual `pcrec-auto` cell (section "Bench asks").

## Sources read

- subst: outbox O-109; ledger `pcrec-bench/docs/dev/ledgers/2026-10-27-subst-0.1-first-9ae59f5d4.md` (read in full). Our lane `subtri_report.md` (the instruction-count diagnosis of the three cases) and `reqvm1m_report.md` / the [REQRUN-VM] row.
- unusual: O-112; ledger `.../2026-10-29-unusual-0.1-l9-scratch.md` (read in full, including 1(a)-1(h)).
- regular: O-111; ledger `.../2026-10-29-first-window-614d45eb3.md` (read in full). The three 614d45eb3 reports' `.md` bodies and sidecars were NOT read (the ledger's sections 3-7 summarize them and every figure used here is the ledger's); the report TSVs were not opened.
- older inventories: `docs/dev/optloop/targets_2026-10-26.md` (rev 1; read in full), `gapreport_2026-10-11.md` (summary, sections 2.1/2.7 and MANAGER JUDGEMENT), `cycle1_analysis.md` section 0 (criterion).
- design/state: `docs/dev/lanes/revwalk_report.md` (summary, tier table, census), `revwalk_evidence/rows.tsv.gz` (bench rows only, for tier assignment), `docs/dev/optloop/primed_2026-10-29.md`, plan.md and plan_completed.md rows named in "Existing rows".
- NOT read: any pcrec stamp for a regular-tier cell (the targets file read none either: "every cause above is a hypothesis from timings and pattern text"); any bench record or TSV directly; l9look's in-progress notes.

## Cell inventory

**Bands used.** There is no single band; each source's own, stated per block.

- Library gaps (subst, unusual, regular): I list a cell when pcrec trails the best ELIGIBLE engine by more than x1.10 (D144 addendum 2 tier A / gapconfig) AND the source's own spread does not swallow it (subst: trial spread under 5 percent on every cell quoted; unusual: bench R1 bar x3 against jit, listed here at x1.10 against eligible; regular: targets file reads every ratio as +-5 percent, chained +-7 percent, cutoff x1.3 there).
- Same-library pin movers (O-111): the capability D119 null band is +-19.92 percent on large `>=1 us` cells and +-16.78 percent on short 100 ns-1 us cells, set by one bimodal cell family; the sentinel null (30 identical patterns, median 0.9991, p5-p95 0.892-1.113) is the better small-effect control. A mover is listed when it clears the sentinel null and either clears the stratum band or has disjoint trial ranges (the ledger's own test for `cls-s-uc`).
- "Eligible" = not pcre2-jit (never the target, cycle1 section 0), not vectorscan; rust counts but is flagged SIMD (its prefilters are `memchr`/Teddy); ASSISTED rows (re2/rust/onig/vectorscan running a host-side assist for what the engine cannot do natively) are flagged and not counted as a like-for-like trail (unusual R4).

Full per-cell table with stamps: `docs/dev/lanes/primesurv_cells.tsv` (one row per cell, columns: id, bench, cell, pin, pcrec figure, best eligible and ratio, jit ratio, stamps, group, evidence). Summary by block:

### A. subst@0.1 (9ae59f5d4, abi 84, acc-main 362 MB, library tier; spread under 5 percent)

| id | cell | vs best eligible | vs jit | stamps (pcrec-auto) | group |
|---|---|---|---|---|---|
| S1 | 5b mask-email `[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}` | **x3.16 vs rust** (SIMD-flagged; re2 659 ms and interp 5,352 ms are SLOWER than pcrec 453 ms) | x1.59 (286 ms) | DFA; prefilter `byte-class` (true on 92.8 percent of bytes); start `reverse-pass`; req_byte 64 (`@`) emitted, no req_run | G1 |
| S2 | 2 rare `/(phpmyadmin\|wp-admin)/[a-z]+\.php` | **none**: rust 133.8 ms vs pcrec 128.0 (x0.96); re2 428, interp 618 slower | x2.66 (48 ms) | VM hybrid; prefilter `memchr` on `/`; start `reverse-pass`; req_byte 47, req_run `admin/`@5 emitted | G4 |
| S3 | 7 url-tld-fix (backref in negative lookahead + conditional template) | **x1.29 vs interp** (157.8 ms vs 203.2); rust/re2 unsupported | x3.89 (52 ms) | VM only; no prefilter; start `first-class`; req_byte 47, req_run `s://www.`@3 emitted | G4 |

Diagnosed by subtri (instruction counts, span-identical hand twins, not timing): S1 forward DFA steps 336 M of 362 M bytes for 80,123 matches (twin driven from `@`: 5.477 G to 0.073 G instructions, x75); S3 the found req-run position is discarded and re-derived by a scalar table loop (twin x3.7 instructions, x10.7 keyed on `h`); S2 the DFA prefilter on `/` is 99.6 percent of instructions (twin x1.6, x9.2 with a re-key to `d`). **[REQRUN-VM] landed after this sample (abi 91, instructions:u: case 7 x2.53, case 2 x1.61): S2 and S3 need a re-measure; S1 is not touched by it (subtri: "5b: a second reverse scan-edge run, -0.04 percent instructions").** Also on this sample: size-first sizing costs x1.6-2.0 on libpcre2 AND pcrec (two passes by design): not a trail.

### B. unusual@0.1 (614d45eb3, abi 89, scratch tier; 7 of 19 cells inconclusive-load, `pcrec-auto` among them but `pcrec-vm`, `auto-in`, `vm-in` measured and within 1.5 percent of it)

| id | cell | vs best eligible | vs jit | stamps / facts | group |
|---|---|---|---|---|---|
| U1 | `cscan-onig` default arm: `PCREC_ERR_FRAMES` on 19 of 23 throughput subjects, `nest-brace-128`+, and 4 call-stream cells (100/256, 1,723/4,096, 163/311, 2,620/4,971 calls); wild-sexp 8 gave-up, wild-json 3 gave-up; 24+8+3 = 35 gave-up cells in the verdict table | **trails interp and pcre2-jit-deep, which answer all of them**; onig default answers WRONG silently (not a trail, a wrong answer) | jit default also gives up (-46) on 16+8+4 cells, first at nest-brace-512; pcrec first at 128 and on FLAT input | vm `selected`, prefilter none, req_run `(?{`@1; stack arm 131,072 B = 2,048 resume + 3,072 trail frames; `_in` arm working storage scales with subject LENGTH: idents-1m 138.8 MiB (about 139 B per subject byte), comment-5m 7.6 MiB, js-1m 323.6 MiB | G2 |
| U2 | wild-json `js-1m` 7.7 MB/s | **x1.74 vs onig** (13.4 MB/s, measured cell); pcrec 3.5x faster than interp (2.2, IL) | x21.9 (168) | as U1; 960 MiB interp heap, 323.6 MiB pcrec `_in` | G2/G3 |
| U3 | wild-json short search 197 ns | x1.25 vs onig (158 ns, IL) | x4.8 (41 ns) | as U1 | G3 |
| U4 | `idents-1m` 94.6 MB/s | x1.75 vs rust ASSISTED (165.7, IL); re2 assisted level (95.4) | x3.0 (281) | as U1 | G2 |
| U5 | `nest-paren-32k` (no recursion: parens are plain bytes to cscan) 35 MB/s | pcrec AHEAD of onig (21) and interp (9.9); x14 behind re2/rust ASSISTED (494/446) | x5.4 (192) | as U1; default arm gives up | G2/G3 |
| U6 | `cscan-onig` short search 296 ns | none natively (onig 345, interp 1,229 ns); x2.1 vs rust ASSISTED (141 IL), re2 assisted level (348) | x3.6 (81) | as U1 | G3 |
| U7 | `nest-brace-100k` 11.6 ms | pcrec ahead (interp and onig-deep time out at 60 s) | x4.8 (2.43 ms) | linear, `_in` arm | G3 |

Not trails (checked, for the record): co-luhn x1.21 faster than jit, co-isbn/co-member x1.47 slower than jit but ahead of interp (1,761 vs 1,097; 1,329 vs 672) and onig; callout-site overhead pcrec-vm +104/+47/+55 us per MB vs jit +83/+41/+69 (parity); co-netstr native `consume` x5.4 faster than jit's check-at-end spelling; vars streams flat in distinct values. comment-5m (x2.4) and splice-1m (x2.5) are inside the bench's x3 bar and ahead of every non-jit engine.

### C. regular tier

**C1. O-111 window at 614d45eb3 (pcrec only; same-window N vs B pairs).** Movers that clear the sentinel null:

| id | cell | move | edge change (abi 87) | route | group |
|---|---|---|---|---|---|
| R1 | capability `wild-logparse-base10num-noatomic` large / short | x1.200 (3.629 to 4.354 ms) / x1.176; nocaps x1.199 / x1.168 | range to mixed, 1 to 2 edges | DFA family (unanchored) | G3 |
| R2 | capability `wild-logparse-base10num-grok` (VM) large / short | x1.102 / x1.071 (nocaps x1.104 / x1.078) | range to mixed | VM | G3 |
| R3 | syntax `cls-s-uc` `\S+@\S+` large / short | x1.116 / x1.119 (trial ranges disjoint; nocaps agrees) | edge gained | start landmark `@` is a T2 case in the revwalk census | G3 + G1 |
| R4 | capability `grp-callout` `ca(?C1)t` large / short | x2.78 / x1.18 the same-window literal `cat` (self-comparison, NOT a library gap; libpcre2 side not read) | none | vm, prefilter none, req_why emitted, `vm_frameless` 1, frame_capacity 1, separate-TU indirect call per fire, fires per call unknown | none (see P6) |

Faster or flat on the same mechanism (kept so the sign is visible): `\s+$` large x0.164 (72,999.9 to 11,990.9 ns; a recovery to 6b2dbd3e's 0.192-0.194 ns/B, not a new floor), `.*\.txt$` x0.91-0.93, syntax `cls-range` x0.816, `[a-z]+\.txt$` flat, `wild-secrets-username-password-pair` flat (range to mixed, so a mixed edge alone does not predict a loss).

**C2. 10-26 library gaps (pcrec 9ae59f5d4 against 6b2dbd3e-window engines; stamps NOT read by the source).** Cells at or above x1.3 against the best non-pcrec engine, annotated with what the eligible-engine reading changes. Ratios are `targets_2026-10-26.md`'s.

| id | family | cells | gap (best peer, jit) | eligible reading | group |
|---|---|---|---|---|---|
| T1a | bounded `ctx-lazy-64/256/1024`, `ctx-greedy-256` | 4 | x19.0-19.7 rust; jit x1.84-1.91 | rust-only (SIMD prefilter hypothesis); auto is x2.1-2.4 SLOWER than pcrec's own forced VM on the same subjects; 95 percent of each sum on two letters subjects with no hit | G5 |
| T1b | loglines `level-context` | 1 (short x3.12) | x3.78 rust; jit x0.74 (pcrec AHEAD of jit) | rust-only; the loss is on the no-match subjects (x5.4) | G5 |
| T1c | loglines `stack-frame` | 1 (short x3.06 rust) | x3.08 jit | jit; T3 in the revwalk census (five segments, two superset) | G1 |
| T1d | capability `json-constant`, `slack-webhook`; litrun `aws-access-key-id`; syntax `asr-wb`/`asr-nwb`; utf8 `asr-b-ascii` | 6 | x20.2 rust (jit x0.96, re2 x0.99) / x1.58 / x2.63 / x4.02,x3.94 / x5.95 rust | json-constant is rust-only (SIMD deferral); the others jit (and rust for asr-b-ascii); owner [START-DENSE] / [REQ-HANDOFF-L1] (built) | G4/SIMD |
| T2 | syntax `lit-cat` x3.21 rust (jit x1.44), `esc-hex`, `mod-x`, `esc-nl` x5.35 rust, `cls-s-lc` x4.60 (jit x4.55), `cls-v`, `anc-m-dollar`, others; litrun `lit-l*`; capability `union-select` x7.67 jit | about 25 | per cell | single-literal scan throughput on 1 MB prose: kit `memmem` path vs jit/rust SIMD; litrun `lit-l16/l31/l40/aws` auto is x2.0-3.9 slower than forced VM (VM beats jit) | SIMD/kit; auto-vs-VM = SEL-COST |
| T3 | capability `moment-iso8601` x22.2 jit, `email-owasp` x7.5, `trim-nested-star` x4.0, `evil-alt-nested` x3.7, `pwd-strength-chain` x3.4 | 5 | jit; rust is as slow as pcrec on iso8601 (68.2 us) | NOT a trail vs rust; auto is x183 (iso8601) and x62 (email-owasp) slower than pcrec's own forced VM on the two 60 KiB hazard subjects; on ordinary prose pcrec is x4-6 FASTER than jit; scan-edge fix (landed) closes `trim-nested-star` only | G6 |
| T4 | altwide 17 cells + utf8 `alt-distinct-lead` | 18 | x1.3-25 rust; pcrec at or ahead of jit on 33 of 34 | rust-only (Teddy); altwide not run at 9ae59f5d4 or 614d45eb3 | SIMD thread |
| T5 | utf8 literal pick / caseless (`lit-sharp-s` x13.9 re2, ...) | 12 | re2/rust; pcrec ahead of jit on all 69 | owner [U8-PICK] (started) | existing row |
| T6 | capability `altorder-foo-foobar` x7.96 rust (jit x3.75), `file-ext-order`, `keyword-prefix-order`, `router-prefix-order`; litrun `alt-foo-tails` x7.86 jit; syntax `grp-atomic-alt` | 8 | rust and jit | uniform over every subject, VM 1.2-1.3x faster than auto, vm also 8x slower than jit on litrun: codegen/SIMD, not a route; abi 76-87 movers on the order cells x1.14-1.28 slower (in-band) | SIMD/kit |
| T7 | syntax `lka-*`, `lkb-*` | 6 | x1.9-4.1 jit (only jit supports lookaround) | no scalar peer | existing rows |
| T8 | bounded `cls-atleast-4096` short x7.55 rust | 3 | about 100 ns per call | ns-scale (D144 add. 1): null | none |
| T9 | syntax `bak-*`, `mod-j-uc`, bounded `line-80`, `pw-8-64` | 6 | x1.1-2.1 jit | D119 FUNDAMENTAL | none |
| T10 | capability `concat-sqli` | 1 | x3.20 re2, x2.87 rust | owner [MATCH-SPLIT] (started) | existing row |

## Shared mechanisms

Evidence labels: **diagnosed** = a measurement or instruction count isolates the cause; **stamp-inferred** = the stamps or a pin pair point to it, nothing isolates it; **guess** = pattern shape or arithmetic only.

**G1. Start recovery from a landmark: the walk back is unbounded but structured.** Cells: S1 (diagnosed, x75 instructions), T1c stack-frame (diagnosed: A01 -72 percent, where_to_start.md), R3 `cls-s-uc` (stamp-inferred: `@` is its T2 landmark and the edge it gained is the slower part), T2 `cls-s-lc` / `cls-v` (guess: their rows are T2 by the census but the measured loss is on 1 MB prose where the `\s` runs are 1 byte long, so the literal scan, not the recovery, is probably the cost), `slack-webhook` (T1 fixed, x1.58 jit, guess). Maps to **P1**.

**G2. A possessive loop keeps one set of VM frames per iteration.** Cells: U1 (35 give-ups), U4, U5, and the storage figures. Evidence: **stamp-inferred by the bench** from `deep_mem_bytes` scaling with subject length on flat input (O-112 item 1). Arithmetic of mine, **guess**: idents-1m at 94.6 MB/s with about 139 B written per byte is about 13 GB/s of frame traffic, bandwidth scale, so the rate (P3's idents-1m x3.0) may be the same fact as the give-up. The general reading to confirm: a possessive loop `(?:...)*+` or an atomic body can never be backtracked into once an iteration completes, so its frames are dead at iteration end. That is l9look's to diagnose (owed); I record it so P2 and P3 are scoped as ONE row unless l9look splits them. Maps to **P2 (+P3)**.

**G3. Recursive-member and short-search rates.** Cells: U2, U3, U6, U7, and U5's rate. Against EVERY eligible native engine only U2 (onig x1.74) and U3 (onig x1.25) trail; the rest trail jit alone. Whether G3 is frames (G2) or call overhead is undiagnosed. Maps to **P3**, owed.

**G4. Scan-edge admission and selection.** Cells R1, R2, R3 (regressions x1.07-1.20 where an edge was gained or widened range to mixed, while `\s+$` gained x6.1 by the same mechanism; `username-password-pair` range to mixed is flat). Evidence **stamp-inferred**: the stamp pair (edge kind, edge count) and the census restoring the old program under `-fno-scan-edge` on 28 of the 38 movers; no A/B on the edge exists in the window (O-111 section 0). Same file as **P8** (relax the uniform-exit precondition so every one-state self-loop becomes a scan, forward machines included): a selection rule that prices an edge against run length (P4) and an admission rule that widens the population (P8) are two halves of one decision. Maps to **P4+P8 merged**.

**G5. Window-context patterns with a leading keyword set: `\b(?:k1|k2|k3)\b.{0,N}?\b(?:...)\b`.** Cells T1a (4) and T1b (1). Stamps NOT read. **Stamp-inferred only from the 10-11 gap report** (auto reads 1.58 ns/B on ctx-*, a per-byte table walk; "DFA overflow, count-collapsed hybrid") and from the pcrec-vs-pcrec fact that forced VM is x2.1-2.4 faster on the same subjects; rust's x19 is a keyword-set prefilter (hypothesis). A new candidate row because no plan row owns "drive candidates from the leading keyword set, verify the bounded window": [CTX-PREFILTER] is lookaround, [OPT-ALTHASH] is wide alternations (reconciled into [OPT-LITSCAN]), [DD-11.5] is the span-context producer.

**G6. Required-byte or length reject missing on hazard subjects (auto only).** Cells T3 (5). The subject is a 60 KiB run with none of the pattern's required bytes; forced VM and jit reject it in 0.37 us and 1.46 us, auto walks it (1.11 ns/B on iso8601). Source labels this "hypothesis, not read from code". Not a library trail (rust is as slow as pcrec), so it is a SEL-COST-class self-trail. Counter-evidence to weigh: selflip (2026-10-26) found NO compile-time rule separating these auto-vs-VM cells, "email-owasp shares stamps with 11 auto wins", and named runtime facts (candidate density, attempt survival) as the deciding ones. A required-byte reject is a different mechanism from a route choice, which is why it is a candidate and not closed.

## Candidate rows

Existing plan rows were grepped first (section "Existing rows"). Remodel overlap column per D153.

| # | candidate | cells moved | gap | likely general fix | plan rows touched | remodel overlap | design / measurement still missing |
|---|---|---|---|---|---|---|---|
| P1 | reverse-walk start recovery (exists) | S1 diagnosed; stack-frame diagnosed; cls-s-uc stamp-inferred; 2-3 by guess | x3.16 (S1 vs rust), x3.08 (stack-frame vs jit) | as designed: `back_walk` fact, ADVANCE contract widened, T2 first | [ENG-TACTICS] rev-inner (held), [REQ-HANDOFF-L1], [MEMFN] | [MATCH-SPLIT], kit ADVANCE contract, [DD-11.5] window site | the 4 questions to Frank; expect its build to also change `cls-s-uc`'s edge picture (G4): do not tune R3 under P4 before P1 lands |
| P2 | release a possessive/atomic loop's frames at iteration end (hypothesis) | about 35 give-up cells, 19/23 cscan throughput subjects, 4 streams | categorical (gives up where interp answers) | frames dead after each iteration of an atomic body; general fact "an atomic region's frames die at its exit" | [SITE-FRAMELESS], [ENG-DIRECT], [INLINE-C] stage 3 (rewrites the reached rule) | none named; touches VM frame discipline | owed: l9look; if confirmed, a design note and a limits.md section 8.4 reading (the default arm's budget stays; the retention is the bug) |
| P3 | recursive-member rates | U2 (onig x1.74), U3 (onig x1.25), 4 jit-only | see inventory | undiagnosed; possibly P2's consequence (G2) | as P2 | as P2 | owed: l9look. Do not charter before P2's diagnosis |
| P4+P8 | scan-edge admission and pricing: ONE mechanism | R1, R2, R3 (x1.07-1.20 regressions); P8 population unmeasured | x1.2 at worst | an edge is emitted only when expected run length beats the per-call setup; relax the uniform-exit precondition for one-state self-loops (revwalk R1) | [SCANEDGE-SET] (completed), [OPT-REVEND], [OPT-3-RUNEND], [OPT-5-PERIODK] | [MATCH-SPLIT] none; revwalk R1 | measurement card: edge ns per run vs table-loop ns per byte across run lengths 1-64 (scanedge.c measured 1.2-3.6 ns/B for the table loop, tight loop 0.19); `pcrec-auto-noedge` on R1-R3; the run-length histogram of base10num's subjects (bench) |
| P5 | landmark byte by frequency | S2 and S3 after re-measure at abi 91 | S3 x1.29 vs interp; S2 jit-only (x2.66) | re-key the run on its rarest byte (`d` not `/`: 2.06 M vs 20.0 M occurrences) | [PRIOR-COST-UNIFY] (blocked, D161 re-scope), [MEMFN-PAIRSTOP], [OPT-LITSCAN] | [PRIOR-COST-UNIFY] blocked | re-measure first. subtri twins say the residual is x4.8 (S2) and x4.9 (S3) cycles on top of REQRUN-VM; only S3 trails an eligible engine, so S2's byte choice is jit-only and can wait |
| **P9 (new)** | candidate driving from a leading keyword set with a bounded window verify | T1a x4, T1b x1 | x19 vs rust (SIMD-flagged), x1.9 vs jit; level-context ahead of jit | emit the leading alternation as the candidate finder (kit set-find), verify `.{0,N}?` window anchored | [CTX-PREFILTER] (different), [OPT-LITSCAN], [MEMFN] window site, [START-DENSE] | [DD-11.5] (window), [MEMFN] | stamps of the 5 patterns (our compiler can print them; not read here); whether forced-VM's x2.1-2.4 win already shows what the fix buys; per memory the SIMD part of rust's lead is separated and deferred |
| **P10 (new)** | required-byte / minimum-length reject before the auto route's scan | T3 x5 (hazard subjects only) | x62-183 vs own VM; vs jit x3.4-22 | a necessary-byte presence test over the run before walking it | [OPT-ENDWIN-ENC], [ENG-ABS-CARET], [SEL-COST] (selflip note), [OPT-REQBYTE] (completed) | [OPT-REVEND]/[COMPOUND] partial | read the VM's reject path and auto's missing one with an instruction-count twin (subtri's method); decide against the selflip finding that no static rule exists |
| P6 | callout fire cost | R4 (1 cell) | self-comparison only | none supported | [INLINE-C] binding table, [SITE-FRAMELESS] | none | demote: no library gap (pcrec-vm callout overhead is parity with jit, 5 members). Stamp-inferred cause of the x2.78 is the absent prefilter (axes `prefilter-admit` has a `callout` row) not fire cost; `vm_frameless` is 1 so [SITE-FRAMELESS] does not apply. Re-measure at abi 91 (REQRUN-VM may have moved it), then one line in BOONIES |
| P7 | size-first two passes | all subst cases | x1.6-2.0 on pcre2 too | n/a | [M4-SUBST] | none | demote: not a trail; BOONIES one-liner |

Obscure cells (T8, T9, T4/T6 SIMD families, T2 literal throughput) get no candidate row: they belong to the SIMD kit thread (`-fmemfn-simd` OFF, each form must beat scalar) or to D119 FUNDAMENTAL / D144 add. 1, per the high-impact-focus and one-pass-loss rulings.

## Missing designs

1. **P2/P3:** nothing written; l9look owes the diagnosis. Scope it as one row until it says otherwise.
2. **P4+P8:** no design note. Needs the measurement card above and the question whether P1's T2/T3 walk makes the `cls-s-uc` half moot (then P4+P8 shrinks to the base10num pair and the P8 population).
3. **P9:** no design. First deliverable would be the stamp read of the five patterns and an instruction-count twin (subtri's method) of "candidates from the keyword set"; the SIMD half of rust's x19 must be named and left out.
4. **P10:** no design; the open question is the selflip finding (no static rule). A required-byte reject is a pre-scan, not a route choice, but the lane must show it does not regress the 11 auto wins that share email-owasp's stamps.
5. **P5 residual:** blocked on [PRIOR-COST-UNIFY]'s re-scope (D161); needs the re-measure first.
6. **P1:** designed; the four questions to Frank are the gate, not a missing design.
7. Not primed, no design needed yet: grp-callout, size-first, SIMD families.

## Bench asks

Ordered by how many guesses each turns into a diagnosis.

1. **One full-roster window at abi 91 or later for capability, syntax and subst** (pcrec-auto plus jit, interp, rust, re2 in the same window; for capability the pcrec pair in ONE window, targets Q-a). Turns all of C2 from stale cross-window figures to current ones, and re-measures S2, S3 after REQRUN-VM. Includes altwide (targets Q-b, never run at 9ae59f5d4 or 614d45eb3).
2. **`pcrec-auto-noedge` on base10num-noatomic, base10num-grok and `cls-s-uc`** (O-111 offered five cells): the one A/B that separates edge selection from everything else that moved between 9ae59f5d4 and 614d45eb3. Plus the per-subject structure of `cls-s-uc` (which of the three 1 MB texts carries the +11.6 percent; O-111 section 11 says not read).
3. **Quiet re-run of the unusual cells that read inconclusive-load, `pcrec-auto` first** (7 of 19; `pcrec-vm` agrees within 1.5 percent so the figures stand, but they are not citable).
4. **A default-arm frame high-water stamp** (frames used, not just the give-up code) on `cscan-onig` subjects, flat and nested. Separates "retained per iteration" from "per nesting level" without a profiler. This is a pcrec-side stamp request more than a bench ask; surface it with l9look's result.
5. **Subst 2, 7 and 5b with libpcre2 interp as an explicit eligible column** in the report's summary rows (the ledger ranks against "best other library", which is jit for 2 and 7).
6. **grp-callout: fires per call and the libpcre2 side** (O-111 asks (b); the ledger section 11 says the libpcre2 side was not read). Low priority: P6 is demoted.
7. **Hazard subjects (capability T3) with the interp column and vm-caps in the SAME window** as auto (targets Q-f is pcrec-side; the bench part is the same-window triple), to price P10.

## Existing rows

Grepped in plan.md and plan_completed.md before proposing anything.

- P1: D161 add. 17; [ENG-TACTICS] rev-inner (held), [REQ-HANDOFF-L1] (completed, in plan_completed.md), [MATCH-SPLIT] / [COMPOUND] / [ENTRY-TABLE] (started), [OPT-REVEND] (started).
- P2/P3: [SITE-FRAMELESS] (not-started, filed 2026-10-27; its trigger is a callout or code site, not frame retention), [ENG-DIRECT] (not-started), [INLINE-C] (started; stage 3 brief rewrites the reached rule).
- P4/P8: [SCANEDGE-SET] (completed, abi 87, plan_completed.md), [OPT-3-RUNEND], [OPT-5-PERIODK] (both not-started refiles), [OPT-REVEND].
- P5: [REQRUN-VM] (completed 2026-10-29, abi 91; follow-ups [RUNG-HYB-GROW], kit R-30), [OPT-VMSEED] (folded into it), [PRIOR-COST-UNIFY] (blocked), [MEMFN-PAIRSTOP] (not-started).
- P9: no owner. Nearest: [CTX-PREFILTER] (lookaround, not this), [START-DENSE] (retry slot adaptive rule), [OPT-ALTHASH] (reconciled into [OPT-LITSCAN]), [DD-11.5] (span context producer, the window site). Searched `ctx-lazy`/`level-context` in plan.md: only [SEL-COST]'s selflip note names them.
- P10: no owner. targets_2026-10-26 proposed [REQBYTE-REJECT]; plan.md has no such row (grep empty). Nearest [SEL-COST] (not-started; selflip note 2026-10-26), [OPT-ENDWIN-ENC] (not-started), [OPT-REQBYTE] (completed 2026-09-26).
- Not primed: [U8-PICK] (started; T5), [MATCH-SPLIT] (T10), [OPT-LITSCAN] (started; T2/T6), [SEL-COST] (not-started; the litrun and ctx-* auto-vs-VM cells), [CTX-PREFILTER] / [ENG-LOOK] (T7), [ENG-COUNT] / [OPT-NEG] (T8/T9).

## STATE AT HANDOFF

- STATE: delivered. Report and `primesurv_cells.tsv` committed on lane/primesurv. Nothing under `src/`, `cli/`, `lib/`, `memfn/` edited; no compile, no timing; no box load.
- OWED: none.
- RULINGS FILE `docs/dev/lanes/primesurv_rulings.md`: re-read before the commit and before this report; it was empty (no entries) each time.
- The one finding the manager may not expect: the regular 614d45eb3 window carries no library comparison, so the "regular bench" adds no new library gaps; and by the D119 criterion only S1, S3 and U2 (plus the U1 give-ups) trail a non-jit native engine. P6 and P7 do not survive as library gaps.
- Resume: a fresh agent can take P9 or P10 from "Missing designs"; both need a stamp read first (our compiler, no timing), which this lane did not do because the brief limited answers to the ledgers and reports.
