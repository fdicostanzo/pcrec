# selflip report: when auto loses to pcrec's own forced VM, and what a three-way choice would need to know

Lane selflip (sonnet), 2026-10-26, branch lane/selflip at main f53ed9fc3. FACTS ONLY: nothing under `src/`, `cli/`,
`lib/`, `tests/` was touched. Probe files: `studies/selflip/` (CLAUDE.md there). Timings are local, indicative, same box
as the bench (Ryzen 7 7700X) but a shared one; the bench's numbers are the record. Hypotheses are labelled HYPOTHESIS.

## 0. Answers first

1. **Every row reproduces in direction, and most in size** (section 1 table). The litrun rows reproduce the bench's
   set-grain ratios exactly (x3.9 / x3.7 / x2.1 / x2.0).
2. **The loss is subject-dependent with the compile-time facts held fixed.** Three independent demonstrations
   (section 4): (a) the same pattern `cat` flips sign between two subjects (prose: auto x2.45 faster; dense decoys: VM
   x2.0 faster); (b) `ctx-lazy-64` flips between random letters (VM x2.3 faster) and `a a a a ...` (auto x1.75 faster);
   (c) on capability, `email-owasp` has the same stamps as `ipv4-near-miss` / `uuid-near-miss` / `winpath-near-miss`
   and the opposite sign, and inside ONE artifact `email-owasp` has 2 subjects where VM wins (x62) and 9 where auto
   wins (up to x1000). **No compile-time rule separates the rows.** What would decide it is a runtime fact per site:
   the density of candidates passing each side's cheap filter (litrun, ctx) or how long the DFA attempt survives
   versus the distance to the required byte (capability hazards).
3. **The hazard rows' forced-VM speed is exactly the early reject** (HYPOTHESIS from the targets note: CONFIRMED by the
   generated C and perf): forced VM emits a `memchr` for the required byte (`RX_REQ_WHY "emitted"`); auto's
   `RX_REQ_WHY "one-attempt"` declines that check (row `one-attempt` of emit_dfa.c's PRESENCE slot, "G2"). The check
   costs ~0.007 ns/B (1 MiB in 7.5 us), so it is a 1000x LOSS on ordinary 1 MiB prose (auto 7 ns vs VM 7,556 ns on
   `email-owasp t-1m`), a 62x WIN on the 60 KiB hazard subjects.
4. **Kit-proven as a third route**: provable today on one of the four litrun rows (`lit-l16`, cover k=16), but today's
   kit text for it is a naive byte-compare loop that is BETWEEN auto and VM (24 us vs 59 us vs 15 us). The other
   three litrun rows are blocked by named conjuncts (k > 24 / k > 32 / captures). The capability and ctx rows are
   variable-width: never whole-cover. Even a perfect literal search (glibc `memmem` find-all, my lower bound) only
   ties the VM (section 3).
5. **Table shape**: one row survives as no-flip by argument (pure-literal `cover` with a literal-run kit form, section
   5 row T1, HYPOTHESIS, needs a measurement); one is a runtime-adaptive arm ([ADAPTIVE-ARM]'s trigger is met by the
   `email-owasp` hazard cell, row T2); the rest do not clear D119's no-regression half.

## 1. Q1 + Q2: per row, route, forced-VM route, where the time goes

Stamps from `--emit-facts` / generated C (`studies/selflip/out/*/rx.c`). Local ns are one-shot or find-all over the
bench's own subject file (`FINDALL=1` = the bench's find-all regime); window-B bench ratios in brackets.

Selection rows (select_engine.c): `pcrec_select_engine` (`src/opt/select_engine.c:1334`) ANDs `analyses[]`
(`:416`: `captures`, `registry`, `dfa_overflow`); with no row excluding the DFA, auto takes the `default:` arm
(`:1442-1445`, "prefer the DFA whenever it can do the job"): `fit.chosen = ENGM_DFA`. Where `captures` excludes the
DFA (a capture GROUP in the pattern: aws, iso8601, trim, evil), `chosen = ENGM_VM` and `prefilter_decision`
(`:858`) walks `pf_admits[]` (`:667`); the `default` row (`:771`) admits the hybrid DFA prefilter. The hybrid's
shape, the DFA's scan and prefilter (`offset-set`, `run-pinned`, `first-class-bounded`...) are picked later by the
candidate-slot rows in `src/gen/emit_dfa.c` (PRESENCE rows at `:9917-9948`, LOCATE rows beside them). `--engine=vm`
(`:1449`) forces `chosen = ENGM_VM` and R21 E-6 turns the hybrid prefilter OFF (`RX_VM_PREFILTER "none"`).

| row (pattern, subject) | auto route (stamps) | forced VM route | local auto / VM ns [bench] |
|---|---|---|---|
| litrun `lit-l40` (40-byte literal), `lbf-l40` | DFA (`ENGINE_SEL selected`: the `default:` arm), unanchored scan, prefilter `offset-set "0,9*"` (a `memchr` on byte 9 of the literal, then `memcmp "FGHIJKLM"` on the required run, handoff 31), then a byte-at-a-time forward DFA over the 40-byte window, then `end - 40` for the start | `VM_START_SCAN "first-class"` (`memchr` on the first byte), then the VM's literal-run instruction (`VM_LIT_RUNS 1`: one bounds check + one `memcmp`). No prefilter, no DFA | 64,968 / 6,465 [66,480 / 6,591]; `mat-l40` find-all 91,694 / 30,932 [92,360 / 28,205]; `fbf-l40` 6,665 / 472 [6,763 / 396] |
| litrun `lit-l31`, `mat-l31` | same shape, prefilter `offset-set`, req_run `78797a41..@2`, handoff 23 | same | 97,307 / 12,465 [96,099 / 13,853] |
| litrun `lit-l16`, `lbf-l16` | DFA, prefilter `run-pinned` (req_run `666768696a6b6c6d@4`, memchr on `j` then memcmp), forward DFA 16 bytes | same | 58,697 / 14,753 [60,314 / 14,897] |
| litrun aws `\b((?:A3T[A-Z0-9]\|AKIA\|...)[A-Z0-9]{16})\b`, `mat-l31` | `ENGINE vm` (a capture group: `captures` row), hybrid prefilter `first-memchr-bounded`, `VM_LIT_RUNS 6`; the hybrid's forward DFA runs `rx_search_run` | VM only, `VM_START_SCAN "first-class"`, no prefilter | 74,542 / 17,525 [75,577 / 18,488]. CONTROLS in the same pattern: `lbf-l31` 11,652 / 16,606 and `fbf-l31` 13,295 / 16,757 (auto wins, x0.7) |
| bounded `ctx-lazy-64` (`\b(?:fail\|abort\|panic)\b.{0,64}?\b(?:disk\|memory\|socket\|quota)\b`), `t-letters-064k` | the DFA OVERFLOWED (>32000 states: `ENGINE_WHY "dfa overflowed"`), the ladder's `collapsed-prefilter` rung: VM + hybrid with a count-collapsed DFA prefilter (`first-class-bounded`, `DFA_START "reverse-pass"`) | VM, `first-class` start scan (f/a/p), no prefilter; width `[8,inf)` | 75,984 / 30,291 [78,172 / 33,181]. `t-digits-016k` 92 / 92 (no candidate ever) |
| capability `moment-iso8601`, `t-trim-match-60k` | `ENGINE vm` (capture group), hybrid, `DFA_SCAN attempt`, `REQ_BYTE 45` ('-') with `REQ_WHY "one-attempt"` = the presence check DECLINED | VM, anchored, `REQ_WHY "emitted"`: a `memchr` for '-' at entry (`rx.c` line 576) | 22,461 / 364 here [68,400 / 374 in the bench: my driver differs, direction and VM figure agree] |
| capability `email-owasp`, `t-evil-match-60k` | `ENGINE dfa` (NO capture groups: all non-capturing), `DFA_SCAN attempt`, `DFA_MATCH "search-filter"`, `REQ_BYTE 64` ('@'), `REQ_WHY "one-attempt"` | VM, anchored, `memchr` for '@' (`rx.c` line 381) | 22,443 / 354 [23,215 / 375]; `t-evil-nearmiss-16k` 8,986 / 92 [6,170 / 77] |
| capability `trim-nested-star` `^(\s+)*$`, `t-trim-match-60k` | VM + hybrid, no required byte (`REQ_BYTE none`) | VM only | 46,173 / 23,705 [48,200 / 24,500] |
| capability `evil-alt-nested`, `t-evil-match-60k` | VM + hybrid, no required byte | VM only | 33,590 / 11,236 [46,300 / 16,200 (sum)] |

**Where the time goes (perf, local, `perf report --no-children`):**

| case | auto | forced VM |
|---|---|---|
| lit-l40 `mat-l40` (1,638 matches) | 88% `rx_search` (the DFA walk, ~56 ns/match = ~1 ns/B), 10% `memchr` | 53% `memchr` (the first-byte scan), 35% VM entry + `memcmp`: ~17 ns/match |
| lit-l16 `lbf-l16` (no match) | 99.4% `rx_search` (DFA walk of every decoy), 0.4% memchr | 66% memchr, 33% VM |
| lit-l31 `mat-l31` | 82% DFA, 16% memchr | 25% memchr, 73% VM |
| iso8601 `t-trim-match-60k` | 100% `rx_prefilter` (the hybrid's DFA runs the whole 60 KiB `\s` run, then rejects: no '-' | 99.99% one `memchr`: the early reject |
| email-owasp `t-evil-match-60k` | 99.99% `rx_search` (the DFA attempt consumes all 60 KiB of letters) | 99.7% `__memchr_evex`: the early reject |
| trim-nested-star `t-trim-match-60k` (a real match) | 51% `rx_prefilter` + 49% `rx_match_anchored`: TWO PASSES over the same 60 KiB | 99.99% `rx_match_anchored`: one pass. auto/VM = 1.95 = the second pass |
| evil-alt-nested `t-evil-match-60k` | 67.5% prefilter + 32% VM | one VM pass (the DFA pass is also slower per byte than the VM's: ~0.37 vs ~0.19 ns/B) |

Q2 answers: for **litrun** the loss is the DFA's per-byte walk over every window the prefilter admits (the bench's
decoy subjects are built so the required-run prefilter admits every unit: each 40-byte unit is 39 literal bytes plus
`#`), versus one vectorised `memcmp`; the VM has no locate/span-walk split to speak of (memchr + compare). For the
**hazard subjects** the answer to "does auto lack the reject" is yes for iso8601 and email-owasp (G2 declines it);
for trim and evil there is no required byte, so neither side rejects early and the loss is the hybrid's two passes.
The forced VM is fast on iso8601/email because of the reject, not because its walk is faster.

## 2. Q3: kit-proven as a third route (U1 `cover`, kit_proof.md)

Method: the harness build's lever `--harness=kit-proof` (the only way `cover` routes today; `build/pcrec-harness`),
plus a trace build (`-DPCREC_CAND_TRACE`, in `build/trace/`, untracked) whose `PCREC_KIT_PROOF_TRACE=1` prints the first
failing `cover_conj[]` row per pattern (`studies/selflip/sweep.py` ran it for all 219 patterns of the five byte sets).

| row | `cover` verdict today | reading |
|---|---|---|
| lit-l16 | ADMITTED, k=16 (`RX_DFA_SCAN "cover"`) | today's kit text for it is a per-byte `&&` chain (`rx_mf1_s[c]==97 && ...`), 24,117 ns on `lbf-l16`: better than auto (58,697), worse than the VM (14,753). It is the kit's REPORT row at the scalar layer. |
| lit-l31 | declined `exact/producer-short` (k = 31) | blocked by a named conjunct (C8: the span fact's sent positions are fewer than k). Admission of `lit-l24` is the last length that `cover` admitted in my probe (25..31 decline). A kit fact (longer proven span) would move it. |
| lit-l40 | declined `fixed-width` (C7: k > `MF_MAX_SPAN_POS` = `MF_MAX_TERM` = 32, memfn.h) | a kit fact (a literal-run proof form with no 32-term cap) would admit it. |
| aws | declined `finisher-dfa` (C1: the capture group puts the route on the VM); under `--no-captures` it is a DFA and declines `anchored-A` (C4: no anchored machine built; HYPOTHESIS: the `\b` and alternation) | captures are OUT of U1 ([CAPS-KNOWN]); the second decline is a pcrec fact, not a kit one |
| ctx-* | declined `finisher-dfa` | width `[8,inf)`: never a whole-cover |
| iso8601, email-owasp, trim, evil | no site (variable, unbounded width) | never: U1's `cover` is fixed-width only (C7). The kit rows that matter for these are PRESENCE (PRES, window_contract.md), which G2 declines |

**What a perfect literal route would buy** (lower bound, `studies/selflip/memmem_probe.c`, glibc `memmem` find-all
over the same subjects, one call per match): `lbf-l40` 4,914 ns (auto 64,968; VM 6,465), `mat-l40` 35,485 (auto
91,694; VM 30,932), `lbf-l16` 11,830 (VM 14,753), `mat-l31` 40,282 (VM 12,465). So a kit literal route is ~13x
better than auto on the no-match subjects and about EQUAL to the VM on them; on the match-dense subjects the
per-call setup of a one-call-per-match search loses to the VM's resident loop. The third route's value on these rows
is "as good as the VM, no hybrid or VM entry", not better than it.

## 3. Q4: predictors

Population: `studies/selflip/sweep.tsv` (219 patterns: litrun 14, bounded 43, syntax 80, loglines 11, capability 71
less the unmeasured), the window-B auto-caps vs vm-caps per-subject medians summed per pattern over the large regime
(capability: auto from window A, as in the targets note), joined to each pattern's auto stamps and `cover` verdict.
`capjoin.tsv` is the capability join alone. A VM "win" is sum ratio > 1.3.

| set | VM wins (>1.3) | even | auto wins (<0.77) |
|---|---:|---:|---:|
| litrun | 11 | 3 | 0 |
| bounded | 7 | 31 | 4 |
| capability | 4 | 39 | 26 |
| loglines | 0 | 2 | 9 |
| syntax | 0 | 27 | 53 |

**Compile-time facts that do NOT separate** (same facts, both signs):

| shared stamps | VM wins | auto wins (control, named) |
|---|---|---|
| auto = DFA, unanchored, `run-pinned`, width `[3,3]`, `cover k=3` (a pure literal) | litrun `lit-l3` x1.49 (11/27 subjects) | syntax `lit-cat` x0.38, `mod-x` x0.39, `esc-hex` x0.38, `mod-n` x0.37 (3/3 subjects); capability `file-ext-order` even |
| auto = DFA, `attempt`, anchored, `REQ_WHY one-attempt` | capability `email-owasp` (2 subjects x62), syntax `anc-caret` x1.22 | capability `ipv4-near-miss` x0.45, `uuid-near-miss` x0.57, `winpath-near-miss` x0.001, all 11/11 subjects auto |
| VM + hybrid, `attempt`, anchored | capability `iso8601` x3.7, `trim-nested-star` x2.0, `evil-alt-nested` x2.9 | `email-nested-plus` x0.002, `phone-list-nested-plus` x0.74, `date-nested-plus` x0.73, `email-local-nodup` x0.16 |
| `collapsed-prefilter` rung (VM + collapsed DFA prefilter) | bounded `ctx-*` x2.15-2.37 (all 4) | loglines `level-context` x1.07 (even); LOCAL counter-subject `a a a ...` auto x1.75 |

**Same pattern, two subjects, opposite sign** (local, find-all, indicative):

| pattern | subject | auto ns | VM ns | winner |
|---|---|---:|---:|---|
| `cat` (`run-pinned`, `cover k=3`) | syntax `t-1m` (prose) | 273,232 | 670,398 | auto x2.45 |
| `cat` | `cacatcab ` x 7000 (dense decoys) | 128,795 | 65,462 | VM x1.97 |
| `ctx-lazy-64` | `t-letters-064k` | 75,984 | 30,291 | VM x2.5 |
| `ctx-lazy-64` | `a ` x 32768 (every other byte a start) | 53,998 | 94,262 | auto x1.75 |
| `email-owasp` | `t-1m` (bench, A/B) | 7 | 7,556 | auto x1000 |
| `email-owasp` | `t-evil-match-60k` (bench, A/B) | 23,215 | 375 | VM x62 |

So the flip depends only on the subject. The runtime facts that would decide it:
- litrun / `cat` / ctx: **candidate density**, the fraction of positions that pass each side's cheap filter
  (the VM's first-byte or first-class `memchr`; the DFA's required-run or offset prefilter). When candidates are
  rare, the DFA's rarer-run prefilter wins; when every unit is a candidate, the DFA pays ~1 ns/B per candidate
  window and the VM pays one `memcmp` (HYPOTHESIS for the mechanism; the sign pairs above are measured).
- capability hazards: **how far the DFA attempt survives** (`d`) against **the distance to the required byte** (`L`):
  the presence `memchr` wins when `d x 0.38 ns > L x 0.0072 ns`, i.e. when the attempt survives past ~n/53 of the
  subject (local constants: DFA ~0.38 ns/B on a class run, `memchr` ~0.0072 ns/B). That is a runtime comparison.

**One clean compile-time separator exists and it is a regime, not a pattern**: the VM's two-pass hybrid when the
prefilter has no reject power and the match spans the subject (trim, evil): x2.0 and x2.9, while the same hybrid
shape (`email-nested-plus`, ...) wins x500 where the DFA rejects cheaply. Again subject-dependent.

## 4. Q5: draft rows (NOT built)

Table styles: select_engine.c `analyses[]` / `pf_admits[]` (name, predicate, verdict, `esel` token, note, `axlist`),
and emit_dfa.c's candidate slots (`.c = {name, deny-flag, applies}`, `.slot`, `.routes`, `.tok`, `.list`, `.desc`).

**T1 (candidate, no-flip by argument, NEEDS A MEASUREMENT FIRST).** A LOCATE row `cover-literal` ahead of `unanchored`
for a pure literal run (every position a single byte, `width [L,L]`, `req_run` covering the whole pattern), whose
kit REPORT form is a `memchr`/`memcmp` literal search rather than the scalar `&&` chain:

    { .c = { "cover-literal", /* deny: NO_WINDOW_REPORT (bit 57, per plan) */, locate_cover_literal_applies },
      .slot = CAND_SLOT_LOCATE, .routes = CR_DFA, .tok = "cover", .hands = CT_VERDICT,
      .desc = "a pure literal: the kit's literal search proves the whole span, no DFA walk, no VM entry" }

Evidence: lit-l3..l40 (11 rows, 0 auto wins; the DFA walk of the admitted window is what is lost, section 1); the
memmem lower bound ties the VM on dense matches and beats it on no-match (section 2). Control it must carry: syntax
`lit-cat`/`mod-x`/`esc-hex`/`mod-n` (auto x0.38, the `cat` prose subject: the row must not take the first-byte
`memchr` that makes the VM x2.45 slower there; the kit's pick between first-byte and run-pinned is the kit's, D157).
Conflicts: `cover_conj[]` C7 (k <= 32) and C8 (`producer-short` at 25..31) and C1 (captures); overlaps [KIT-VERIFY]
U1 itself (this is U1 widened, not a new mechanism), [MEMFN] (kit literal form), [OPT-LITSCAN]. D153 remodel overlap:
YES, [MEMFN] (kit search sites) and [DD-11.5] only if the span context producer feeds `S_d`.

**T2 (candidate, runtime-adaptive).** A PRESENCE row `one-attempt-deferred` replacing `one-attempt`'s unconditional
decline: take the presence `memchr` only once the attempt has survived ~n/53 bytes (the break-even above; a
ski-rental bound: the added cost is at most ~2% of the attempt's own time, the saving up to x1000/x62). Evidence:
`email-owasp` (2 hazard subjects x62), `iso8601` (x183). Controls it must not regress: `ipv4-near-miss`,
`uuid-near-miss`, `winpath-near-miss`, `email-nested-plus` (all 11/11 subjects auto wins, small absolute times).
Conflicts: G2's own premise ("the check would scan the window the attempt reads anyway", emit_dfa.c:9928) is false
for a `memchr` (53x cheaper per byte than the DFA step) and for an attempt that dies early; [ADAPTIVE-ARM]
(`docs/dev/plan.md`) has this as its trigger shape ("the prior contradicts the text and the compile-time decision
loses by more than the null band": `email-owasp` t-evil-match-60k is a timed witness, 23 us vs 0.375 us), and
memory `pcrec-adaptive-methods-unproven` (Frank 2026-10-21) says run-time switching rows go to Boonies until proven:
this row would have to clear that bar by measurement, so it is a candidate to FILE under [ADAPTIVE-ARM] with this
witness, not to build. No kit involvement (presence is a PRES row, window_contract.md).

**Not a row (does not clear D119's no-regression half):** `collapsed-prefilter` -> VM-without-prefilter (ctx-*: wins
x2.2 on letters, loses x1.75 on `a a a ...`: the same sign-flip bucket as sel_cost.md bucket C); a "pure literal
prefers the VM" row (the `cat` prose pair, lit-cat x0.38); any hybrid-drops-prefilter row (`email-nested-plus` x0.002).
sel_cost.md's conclusion (no compile-time term clears D119) is re-confirmed on 219 patterns: the "separate" tables
above have the same stamps on both sides.

Conflicts with existing rows: T1 sits after `rev-end`/`empty` and before `composite` (kit_proof.md §2.1's order); T2
replaces one row of the PRESENCE slot (`one-attempt` at emit_dfa.c:9926) and touches `REQ_WHY`'s CLOSED four-token set
(rowcon/customers.md:321: a new token is an abi event, D76/D94). Neither touches `analyses[]` or `pf_admits[]`: no
ENGINE-level row is proposed, because the engine choice is not what separates these cells.

## 5. Bench-only questions (relay to the bench dev, memory pcrec-ask-bench-dev)

1. `moment-iso8601 t-trim-match-60k`: the bench's 68.4 us vs my 22.5 us for the same artifact (VM figure agrees at
   0.364 vs 0.374 us; `email-owasp` agrees at 22.4 vs 23.2 us). Does the bench's driver call a different entry
   (`match` with captures vs `search`) for that cell? Not chased (not my site; the direction and the ratio class hold).
2. Do the bench's litrun `throughput/*.bin` generators intend `lbf`/`fbf`/`mat` as decoy-DENSE regimes? The sign
   pairs in section 3 are the reason to ask: a sparse-candidate litrun subject (prose with the literal planted a few
   times) would be the missing counter-subject for section 3's `cat` pair.
3. Is there a capability subject of length >= 256 KiB whose leading class run is SHORT (attempt dies at byte d, no
   required byte anywhere)? That is the subject T2's cost bound needs timed.

## 6. STATE AT HANDOFF

- Branch lane/selflip. Rulings file `docs/dev/lanes/selflip_rulings.md`: re-read before the report commit, "(none yet)".
- Probes (`studies/selflip/`): `probe.c`, `run.sh`, `capjoin.py`, `sweep.py` (ran under `scripts/boxlock run`, ~1,000
  compile-only invocations, one 33 s box hold), `memmem_probe.c`, `sweep.tsv`, `capjoin.tsv`. `out/` (builds, perf data,
  scratch subjects) is gitignored. The trace build in `build/trace/` is untracked scratch.
- Local timings: single-process probes only, no queue jobs; no timing window was running (`scripts/boxqueue status`
  showed only a not-before-2026-10-27 full-suite job).
- STOP RULE: no row failed to reproduce in direction. One magnitude differs (iso8601 auto, question 1 above).
- Owed: nothing.
