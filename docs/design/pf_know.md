# [PF-KNOW] — what a successful prefilter PROVES to the VM, and whether the DFA's class tables can serve it

**Lane `pfknow` (fable, high effort), 2026-09-30, branch `lane/pfknow` from
`d88374d5`. RESEARCH ONLY (D140): nothing under `src/`, `docs/spec/` or
`tests/`; no mechanism is built or scheduled. Instruments and raw data:
`studies/pf_know/` (its CLAUDE.md lists them). Every count below is from
this tree at `d88374d5`; every clock reading is Mac-directional and says
so.**

Charter (D140, Frank's words): *"when we use prefilter on a vm, is there
elements of the vm that can presume certain conditions apply such that they
can skip certain tests in such a way as to make the operation faster? For
instance, if the pre filter is successful, one can presume a fixed prefix
matches and skip ahead to the next piece. But if we trace the pre filter
with the vm, there might be other pieces that we can prove as well such as
class membership, even special case dfa-approved look-arounds. Another
element — if the dfa uses class tables, is there overlap to allow the same
table for vm? My strong guess is no but I'd like that validated."*

Sections: §0 the answers; §1 what exists (the map, so nothing here is
re-invented); §2 what each prefilter kind proves; §3 which VM tests that
makes redundant, and the soundness conditions; §4 the static census; §5 the
dynamic share and the hand twins; §6 question 2, the class tables; §7 what
was refuted; §8 candidate [OPTLOOP] rows; §9 reproduction.

---

## 0. The answers

**Question 1.** On the VM route there is exactly ONE per-position prefilter:
the hybrid's capture-erased forward+reverse DFA pair (`<prefix>_prefilter`,
the same emitter as the DFA artifact, engine_m4.md §6.1). Everything else
in front of a VM program is a whole-window fact (a necessary byte or run, an
end-anchor window, a root minimum width, a start-anchor bound) that proves
something about the WINDOW, never about the bytes at the candidate
position. What the hybrid proves at the candidate `start` is:

- **always**: `s[start, …)` begins a string of `L(erase(P))`, and no match
  of `P` begins before `start` — because `L(P) ⊆ L(erase(P))` for every
  erasure `src/ir/nfa.c` performs (captures, lookarounds, atomicity, the
  count collapse; its own comment at nfa.c:687), so the START is a sound
  lower bound on every hybrid;
- **only where `Vm.mrl_win` holds** (the erasure is captures alone, so the
  prefilter's language IS the pattern's): the reported `[start, end)` is
  the leftmost-first span itself, under the span-equality claim R21 split
  off as BELIEVED-WITH-GATE and whose two counter-examples (K17, K18) are
  both FIXED since 2026-08-15.

Under the exact proof, the VM tests that become redundant are **exactly
the leading fixed-width, choice-free segment of the program** (literal
bytes, class bytes, the DFA-decided `^ $ \b \B \z \G` and [UCP] U2's
one-character context nodes, capture opens — everything up to the first
alternation, variable repeat, lookaround, backreference or call) and,
symmetrically, the **trailing** such segment at a fixed offset from `end`.
Nothing past a choice point is implied: the DFA never says which branch
the winning path took or where a repeat stopped. The limit case — the
whole program is such a segment (`det_all`) — is the trivial member of the
one-pass class `captures_via_dfa_survey.md` §3.3 already ranks first, and
there the VM is redundant in full: every capture sits at a constant
offset from `start` or `end`.

MEASURED. Static (3,347 compiled artifacts, corpus + pcrec-bench): 1,142
hybrids, 569 truly exact; among those, 52% have a non-empty leading
segment, 164 (29%) are wholly implied, and the leading segment is 22% of
the summed minimum width. On the bench's own 47 hybrids the leading
segment is EMPTY on 32 — real patterns open with `^`, `\b` or a class
repeat, not a literal. Dynamic (gcov over bench subjects): the VM executes
0.3-22% of all test lines on every cell measured, the DFA scan the rest;
the leading segment is 0-38% of the VM's tests; the product is 0-5%. Hand
twins (Mac, directional, answer-identical): sparse bench-shaped subjects
x1.000-1.003 on every twin; match-dense synthetics x1.13 for skipping the
VM outright (det_all), x1.04 for a 44-byte caseless prefix, x1.01 for a
5-byte `memcmp` prefix.

**Verdict on question 1.** The proof is real, the redundant tests are
exactly characterisable, a prefix-skip entry is sound and would cost a
few emitted bytes — and it is NOT worth a batch slot on its own: its
prize is a fraction of the VM's share, and the VM's share is small
precisely where the prefilter is doing its job. Where the VM's share is
large (match-dense find-all, whole-subject match), the win that is there
(x1.13) belongs to the WHOLE-PROGRAM case, i.e. to the one-pass rung the
survey already carries. The general mechanism is that rung; a leading
prefix is its degenerate instance and must not be built as a special
case (memory `pcrec-general-mechanisms-not-special-cases`). §8 files it
as a MEMBER of that row with the measured numbers, and names the one
D77 trigger.

**Question 2.** Frank's guess is REFUTED on representation and VALIDATED
on benefit. The DFA prefilter's byte-class map is a partition of the 256
bytes induced by every set the erased pattern's NFA reads; a VM class
bitmap is a set. Measured over the 74 hybrids that carry both: the DFA
partition REFINES 114 of 118 VM bitmaps (the four that it does not are
classes inside erased lookaround bodies — the DFA never saw them). So the
VM *could* index the DFA's 256-byte map and test a bitmap over DFA classes
instead of over bytes. What it would buy: **3,373 bytes over the whole
corpus** (45 B per affected artifact; VM bitmaps are 32 B each and 56 of
the 74 DFAs have ≤8 classes), at the price of two dependent loads per VM
class test instead of one — the VM holds no DFA state, so the class index
is a load, not a register. Meanwhile D139 (2026-09-30) already rules the
sharing that IS worth having: the scan edge consumes the general class
table's ROWS form and the SAME emitters the VM uses, so one class-form
decision serves both engines. And the within-artifact prize is elsewhere:
the forward and reverse byte-class maps coincide on 59/59 measured hybrids
that carry both machines (256 B each, 15.1 KB over the population) — that
is [OPT-D]'s row, unchanged by this note.

---

## 1. What exists — the map

Read before anything else here, because most of what the charter asks for
is already a mechanism with a name.

| mechanism | where | what it does with the prefilter's proof |
|---|---|---|
| **the hybrid** ([M4.6], engine_m4.md §2.6/§6.1) | `emit_vm.c` `vm_emit_search_body`: `pcrec_emit_dfa_engine(cx, "<p>_prefilter", "static ")`, then `rx_search_run` | the ONLY per-position prefilter on the VM route. `if (rx_prefilter(subject, n, search_from, window) != 1) return 0; attempt_position = window[0][0];` — the window START is consumed as the VM's anchored entry; the VM never scans |
| **the MRL ceiling** ([M4.6d], D51 ruling 2) | `rx_window_end` parameter of `rx_match_anchored`; `RX_PRUNE_TOO_SHORT(p, minrest)` at every clamp site | the window END is consumed as a PRUNE: a path whose remaining minimum width cannot reach `window_end` dies. Only where `Vm.mrl_win` — `<PREFIX>_VM_PRUNE_CEILING "prefilter-window"` (240 hybrids) vs `"subject-end"` (121, cut/lookaround-bearing) vs `"none"` (781, no clamp site at all) |
| **the retry re-seed** ([OPT-HYB-RESEED], D‑table `pcrec_reseed_rows`) | `rx_search_run`'s loop tail | after a failed attempt the prefilter is asked again from `attempt_position` (exact/clamped rows) or adaptively (over-approximating rows). The row `exact` is `Vm.mrl_win` verbatim: **it is the one stamp that says whether the prefilter's language is the pattern's** (§2.2) |
| **whole-window pre-checks** ([OPT-REQBYTE]/[OPT-LITSCAN] K65/K66, [OPT-PRECHECK-ADMIT]) | `pcrec_emit_req_byte_check`, `<p>_reqrun` | a necessary byte/run/set is searched over `[search_from, n)`; NOMATCH if absent. Proves a byte EXISTS somewhere, never where |
| **end-anchor window** ([OPT-ENDWIN], `end_window` fact) | `pcrec_emit_end_window_clamp` | clamps `search_from` up to `n - maxw` on `$`/`\z`-ending bounded patterns |
| **root minimum width** ([DD-14.EMPTY]) | `rx_search_run` | NOMATCH when `n - search_from < minw` at the analysis ceiling |
| **start-anchor bound** ([OPT-ANCHOR-VM], `start_anchor` fact) | `attempt_max = search_from` | one attempt on `^`/`\G` patterns |
| **[PATFACTS]** (`src/facts/facts.def`) | ten facts: kinds, nullable, start_anchor, end_window, req_set/req_whole_run/req_run/req_byte, kset_walk, run_pin | the pattern-level facts every pre-check above reads. None is a fact about a POSITION |
| **DFA-side candidate prefilters** (axis B, `dfa_pfs[]`: run-pinned, offset-set, memchr, byte-class; [OPT-LITSCAN] S1; the scan edge [OPT-5]/[OPT-EDGE]; [OPT-FIRSTSET]) | `emit_dfa.c` | live INSIDE `<p>_prefilter`'s forward machine. They prove things to the DFA's own scan loop (a candidate start byte at an offset, a verified pinned run) and the DFA converts them into the window. The VM never sees them, and cannot: what reaches the VM is the window, by the `rx_matchfn` shape |
| **[OPT-VMSEED]** (not built) | plan.md | the same candidate-finding rows as a start seed for the NO-prefilter VM loop (backreference / call patterns). Would prove "no match starts before q" — again a START fact |
| **[ENG-BREP]'s reverse-deterministic rung** (`src/opt/revdet.c`, eng_brep_design.md §3.4) | the VM program | recovers a loop's last-iteration captures by a backward walk from a COMMITTED span — the one existing mechanism that derives captures from an end position rather than by re-matching |
| **captures via a DFA** (`docs/dev/optloop/captures_via_dfa_survey.md`, `onepass_census.md`) | survey + census | ranks (c) the ONE-PASS DFA first (31.5% of capture-bearing corpus patterns are one-pass; 5 of the 17 capture-forced capability hybrids), (a)'s residual second (a HARD end bound), TDFA deferred. §3.1 names the end bound as "the only live item in (a)" |
| **[CTX-PREFILTER]** (census + joint measurement, not built) | docs/dev | a lookaround's necessary one-character condition ADDED to the prefilter — tightening what the prefilter proves, the opposite direction from this note |
| **[OPT-D] / [XART-TABLES] / [OPT-CLSPACK] / [CLS-TREE] / D139** | plan.md, clskit.c | table dedup within an artifact (twins), across artifacts (link-time), the VM's atom table, the kit, and (D139) the scan edge consuming the VM's class-form rows |

Two things the map settles before any measurement:

1. **The VM-only route has no per-position prefilter at all.** `rx_search_run`
   without `prefn` runs `attempt_position = search_from; … attempt_position++`
   (`emit_vm.c`, the [K49] retry advance) behind the whole-window
   pre-checks. 358 VM artifacts in the census are on this route (338
   corpus, 20 bench; 297 forced by a capture group and declined the hybrid
   for a nullable language or a backreference/call). For them the question
   "what does a successful prefilter prove at the candidate" has the answer
   "nothing, because nothing runs at the candidate" — [OPT-VMSEED] is the
   row that would change that, and it proves a start bound, not bytes.
2. **The DFA-side prefilter forms are not the VM's prefilters.** A
   `memchr`/offset-set/run-pinned row is a fact the DFA's forward scan
   consumes to skip to a candidate; the DFA then walks the candidate to an
   accept and the reverse machine walks back. By the time control reaches
   the VM every one of those facts has been strengthened into "the whole
   span is in the erased language". So the interesting proof is the DFA
   pair's, and the enumeration the charter asks for collapses to one kind
   with one parameter: is the erased language the pattern's own?

## 2. What each prefilter kind proves

### 2.1 The hybrid pair — the one that reaches a position

`<p>_prefilter(subject, n, from, window)` returns 1 with
`window = [start, end)` exactly when the DFA-only artifact for `erase(P)`
would report that span from `from` (it IS that artifact's search entry,
emitted `static`). Established at the candidate:

| fact | holds on | why |
|---|---|---|
| F1 no match of `P` begins in `[from, start)` | every hybrid | `L(P) ⊆ L(erase(P))` (nfa.c:687): a `P`-match there would be an `erase(P)`-match there, and the forward machine's leftmost-first end plus the reverse machine's earliest start would have reported it |
| F2 `s[start, end) ∈ L(erase(P))` | every hybrid | the forward machine accepted at `end`, the reverse machine accepted at `start` |
| F3 `[start, end)` is `P`'s leftmost-first span | `mrl_win` only | erasure of captures alone keeps the language AND (span-equality, R21: BELIEVED-WITH-GATE; K17/K18 the only counter-examples ever found, both FIXED) the preference order. With a lookaround, a cut or a collapsed count erased, `erase(P)` is a strict superset and `end` is the superset's end (the atomic-group comment in `internal.h`: "sound for the prefilter's rejection and its span START and NOT for its span END") |
| F4 every DFA-decidable zero-width test on the accepted path holds at its offset | every hybrid | `^ $ \A \z \Z \G (?m)` and `\b \B` are position VIEWS and a CLASS AXIS of the DFA (src/gen/CLAUDE.md waves B-D); [UCP] U2's ctx nodes (`(?<=\$)`, `(?![\d.])` — one-character lookarounds) are `A_CTX` nodes the DFA decides too. The census confirms: `\bfoo(\d+)\b` and `(?<=\$)(\d+)\.(\d\d)` both stamp reseed row `exact` |

Nothing else is a fact about a position. Which branch of an alternation the
accepting path took, how many iterations a repeat ran, what a multi-
character lookaround body would have matched — the DFA either never knew
(subset construction keeps all alternatives alive) or erased it.

### 2.2 The stamp that lies by omission

`<PREFIX>_VM_PREFILTER_LANG` reads `"exact"` on 1,135 of the 1,142 hybrids
and `"count-collapsed"` on 7. It is a fact about the COUNT-COLLAPSE axis
only (`prefilter_count_independence.md`). The exactness a consumer of the
END needs is `Vm.mrl_win`, whose three conjuncts are nfa.c's three
erasures, and whose one readable surface is the reseed row:
`<PREFIX>_VM_RESEED "exact"` on 569 hybrids; `adaptive`/`adaptive-dense`
on 452 (a lookaround or cut erased, clamp-free); `clamped` on 121. The
"exact" LANG stamp is on 76 `(?<=…)`, 47 `(?=…)`, 53 `\K`, 132 `(?>…)` and
46 possessive-quantifier patterns whose window END is NOT proven (§4.1).
Not a defect — each stamp answers its own question — but a reader of the
artifact who wants "is the prefilter exact" must read the reseed row, and
this note's population splits are on that row. Filed in §8 as a one-line
stamp question for the manager, not a mechanism.

### 2.3 The whole-window facts

A necessary byte/run present in the window, the end-anchor clamp, the root
minimum width, the start-anchor bound: each proves a property of the
SEARCH, consumed once per call in `rx_search_run` above the attempt loop.
None implies a VM test at `attempt_position`, and none becomes stronger by
being traced into the program: the byte the pre-check found may be at any
offset of any candidate. Their only interaction with the question here is
G2 of [OPT-PRECHECK-ADMIT]: on a one-attempt route the pre-check is itself
the linear no-match proof, so it stays even where a prefilter would have
answered.

## 3. Which VM tests the proof makes redundant, and the soundness conditions

### 3.1 The proven-segment statement

Let the program be the lowered AST after `pcrec_altcls`,
`pcrec_discharge_atomic` and `pcrec_lower_enc` (the tree `emit_vm.c`
walks). Call a node **det** (deterministic, fixed width) when it is: a
byte or wide class (one test, one char), `A_EMPTY`, a DFA-decided zero-width
node (`A_BOL A_EOL A_END A_CTX A_GSTART`), `\K` (`A_KRESET`, a slot write),
an `A_CAP` or `A_ATOMIC` over a det body, an `A_CAT` of det nodes, or an
`A_REP` with `rmin == rmax` over a det body. The **leading segment** is the
maximal det prefix of the top-level concatenation, descending through a
non-det `A_CAP`/`A_ATOMIC`/`A_CAT` to its own leading det part; the
**trailing segment** is the mirror.

> **Under F2 (every hybrid), every consuming and zero-width test in the
> leading segment succeeds at its fixed offset from `start`.** Every
> accepting path of `erase(P)` passes through the segment's tests at the
> same positions (there is no choice before them), and the DFA has
> exhibited one such path. Under F3 (`mrl_win`), the same holds for the
> trailing segment at its fixed offset from `end`, and the accepting
> path's end IS `end`.

Consequences the VM may draw, in decreasing strength:

- **det_all** (root det): every test is implied; every capture is
  `[start + c1, start + c2)` for constants; the VM has no work. This is
  the trivial subset of ONE-PASS (`onepass_census.md`'s predicate is
  strictly wider: it admits alternations with disjoint first sets and
  repeats decided by the next byte), and the survey's candidate (c) is the
  mechanism that serves it — with a real deterministic walk rather than
  constant offsets in the non-trivial part of the class.
- **leading segment of K bytes** (with its `c` capture opens and `z`
  zero-width tests): `scan_position += K`, the `c` opens written as
  constants, entry at the label after the segment. The K tests, the K
  bounds checks and the `z` context probes are deleted from the hybrid's
  path.
- **trailing segment of K' bytes** under F3: the path reaching the
  segment's first instruction at `p ≠ end − K'` cannot be the winner and
  may fail at once; the one reaching `p == end − K'` may skip the K' tests.
  This is one compare against a test the segment would have made anyway
  (`memcmp` of K' bytes), so its prize is bounded by K' − 1 byte compares
  per attempt — and the survey's "hard end bound" (§1) already generalises
  it: with the end known exactly, `RX_PRUNE_TOO_SHORT`'s `≤` becomes an
  `==` at the accept and a `remaining maximum width ≥ end − p` prune
  joins the minimum-width one. Neither is measured here.

What is NOT implied, stated so nobody builds it: class membership at an
offset past a choice point ("the DFA saw a digit at start+7" is true of
SOME accepting path, not of the VM's); a multi-character lookaround's
verdict (erased); a backreference's target (no DFA); the extent of any
repeat, bounded or not (the DFA's accept at `end` fixes the SUM of the
extents on its path, not each one); which alternative an `A_ALT` took —
unless the alternation is an island trie ([ENG-ISL]), whose walk is
deterministic anyway.

### 3.2 Soundness conditions, one per hazard the charter names

| hazard | condition | status |
|---|---|---|
| **captures inside the skipped segment** | every `RX_SET` the segment would have executed is executed with the constant it would have written (`ctx->pos + offset`); the trail must see them (they are trailed writes today, `vm_set`) so a later backtrack rewinds them exactly as before | mechanical; the twin does it |
| **alternation** | the segment stops at the first `A_ALT` — after `pcrec_altcls`, so `(foo\|foobar)x` is `foo(?:\|bar)x` and its segment is `foo` (census: it reads lead 3), while `(xy\|xz)` factored to `x(?:y\|z)` reads lead 1. An island ([ENG-ISL]) is still an `A_ALT` to the predicate | by construction |
| **backtracking re-entry** | a choice-free segment pushes no frame, so no resume label lies inside it: the fail dispatch can never re-enter the skipped tests. The one construct that resumes at a position other than the current one (the span-loop cursor rung) is a repeat, hence outside the segment | by construction; `vm_push_at` is the only push site |
| **caseless** | the DFA folded the same letters (`-i` is "folded into the automaton"); the VM's per-byte `(c \| 0x20) == k` tests are what the skip deletes. The DFA proved the folded equality, so the skip is sound | by construction |
| **utf8** | segment offsets are BYTE offsets on the lowered tree (`A_WCLASS` counts one character but its lowered bytes are what the program tests); the hybrid's window is in bytes; a byte kit/decoder test inside the segment is deleted like any other. K49's mid-character retry cannot reach a hybrid's `attempt_position` (it is the reverse machine's start) | by construction; not measured under `-e utf8` (census is byte-mode) |
| **find-all and resumption** | each `rx_search` call asks the prefilter afresh from `search_from`; the proof is per call and per window. The K75 resume rule (`<p>_next_pos`) moves `search_from` only | by construction |
| **the retry / re-seed loop** | after a failed attempt (only reachable where F3 fails, or on the K17/K18 direction of a span disagreement), `attempt_position++` steps to a position the prefilter did NOT prove. The skip entry must be taken ONLY on a position the prefilter just returned: the first attempt, and the re-seeded attempts of `exact`/`clamped`/the adaptive rows' re-seed arm — never a stepped one. This is the one condition an implementation can get wrong silently: the entry must be selected by the loop, not by the position | design condition; the `retry_seed` text already distinguishes the two arms |
| **over-approximating hybrids** (452 adaptive + 121 clamped) | F2 still licenses the LEADING segment (the erased language is a superset, but the segment's tests are the pattern's own bytes and every erased-language path passes them too); F3 does not hold, so the trailing segment and any end fact are OFF. On a clamped artifact the leading skip composes with the clamp unchanged | sound for the lead; the end is not |
| **the hybrid's forward/reverse split** | `start` is the reverse machine's earliest accept, `end` the forward machine's last accept before its dead transition. Under the start-pinned search ([OPT-5] STEP 2, 15 of the 74 class-bearing hybrids) `start == search_from` by proof and the reverse machine is absent: the segment proof is unchanged | by construction |
| **anchored entries** (`<p>_match`, `<p>_match_caps`) | run the SAME program with NO prefilter, so the segment's tests must STAY in the program: the skip is a SECOND ENTRY LABEL for the hybrid search, not a deletion. `--engine=vm` (prefilter denied) and `-fno-prefilter` take the ordinary label | design condition; also what keeps `run_vm_identity.sh`'s DFA-only bytes untouched |
| **`\K`** | inside the segment it is a slot-0 write at a constant; the report rule (`report_captures`) is unchanged | mechanical |
| **callouts** (D36) | a skipped test fires no callout it would have fired; D36 already permits a prefilter to change fire counts | ruled |
| **span-equality itself** | F3 rests on R21's BELIEVED-WITH-GATE claim. K17/K18 are fixed, the corpus differential and `--engine=vm` cross-check are the standing gate. A LEADING skip does not rest on F3 at all (F2 suffices); only end-side consumers do | the survey's (a)-residual caveat applies to the end, not the start |

### 3.3 Where this sits among the lenses (memory `pcrec-design-evaluation-lenses`)

Specific vs general: the general form is "the VM entry consumes the
prefilter's proof as a fact `(start, end, exact)`" and selects, by a
first-match row table (memory `pcrec-decisions-as-first-match-tables`),
how much of the program the fact discharges: `whole` (det_all / one-pass),
`prefix` (leading segment), `none`. A prefix skip written on its own would
be the special case. Core vs derived: derived — a walk over the existing
lowered tree plus one label. Applicable vs assumption-changing: the
leading skip changes no assumption; the end-side consumers convert R21's
belief into a correctness dependency (the survey's own verdict). Fits-arch:
fits — one entry label, no new machine.

## 4. The static census

`studies/pf_know/census.py` + `segprobe.c`, tree at `d88374d5`, default
engine, `--features all`, byte encoding. Population: every `pattern`/
`pattern-esc` line of every shipped `.rxt` (3,422) plus the read-only
sibling pcrec-bench's `bench/*/patterns/*.rx` (324): 3,746 rows, 3,347
compile (the 399 refusals are refuse-expected corpus rows and bench rows
needing `-e utf8`/`-i`). Engine: 1,847 DFA, 1,500 VM; of the VM artifacts
1,142 hybrid (`RX_VM_PREFILTER "hybrid"`) and 358 prefilter-less.

### 4.1 Exactness, by the row that knows

| hybrids | n | bench | reseed row |
|---|---:|---:|---|
| truly exact (`mrl_win`) | 569 | 23 | `exact` |
| over-approximating, clamp-free | 452 | 20 | `adaptive` 390 / `adaptive-dense` 62 |
| over-approximating, clamped | 121 | 4 | `clamped` |

`RX_VM_PREFILTER_LANG` reads `"exact"` on 1,135 of the 1,142 (§2.2).

### 4.2 The proven segments (probe: `segprobe.c`, definitions §3.1)

| population | n | lead 0 | lead 1-2 | lead 3-7 | lead 8+ | lead zero-width >0 | trail 0 | trail 1-2 | trail 3+ | det_all | Σlead / Σminw |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| hybrid, truly exact | 569 | 274 (48%) | 202 | 76 | 17 | 152 | 214 | 269 | 86 | **164 (29%)** | 22.0% |
| hybrid, over-approx. | 573 | 438 (76%) | 123 | 12 | 0 | 85 | 148 | 409 | 16 | 21 | 19.0% |
| VM, no prefilter | 358 | 223 | 128 | 2 | 5 | — | 272 | 86 | 0 | 4 | — |

Of the 164 wholly-implied exact hybrids, 138 carry a capture (the other
26 are on the VM for `\K`, a discharged atomic or a possessive) — they are
`onepass_census.md`'s population seen from the narrow end (it counts 369
capture-bearing one-pass patterns corpus-wide with a wider predicate).
Of the exact hybrids' 1,424 leading tests, 1,180 (83%) are literal bytes;
the rest are classes. 152 exact hybrids open with a DFA-decided zero-width
test (`^`, `\b`, a ctx node) — the "DFA-approved lookaround" the charter
names, and it is one test each.

### 4.3 The bench's own hybrids — where the segments are

47 bench hybrids (23 exact). Leading segment ZERO on 32: the wild
patterns open with `^` (us-zip, pwd-strength, email-local), `\b`
(github-pat, aws-key, level-context), a one-character lookbehind
(base10num, quotedstring, float-literal — the last is on the DFA at this
pin) or a class repeat (date, phone, iso8601, winpath). Non-zero on 15:
`wild-secrets-github-pat` (det_all, 93 bytes, the whole program),
`wild-secrets-slack-webhook-url` (44 caseless bytes then a `{8,12}`),
`wild-validator-us-zip-owasp` (5 digits after `^`), `syntax/lka-*`/`rec-*`
(2-4 bytes), `codegrammar-*` (1). The distribution in the bench is
narrower than the corpus's: the corpus is test fixtures (`a(b)c`), the
bench is patterns people run.

## 5. The dynamic share and the hand twins

### 5.1 Method

`dyn.py`: the artifact built `--coverage` against a find-all driver, one
pass over the subject, gcov's per-line counts; every executed test line
(`if`/`while`/`switch`) bucketed into the VM program's `lead` (from `rx_L0`
to the first loop/choice construct — a LOWER bound on §3.1's segment,
because an exact bounded span loop is det but the instrument stops at it),
`mid`, `trail`, the DFA prefilter, and the search loop. A test LINE is the
unit: a `memcmp` line counts once, a loop's test once per iteration — so
the DFA's per-byte loop and the VM's per-byte tests are on the same
footing, and a 5-byte `memcmp` is under-counted against 5 byte tests.
Subjects: the bench's committed capability `t-1m.bin`; the loglines and
email throughput texts regenerated by the sibling repo's own generators
into scratch (`--out`); two synthetics of this study for the secrets
patterns (§5.3). `matches` is the driver's find-all count.

### 5.2 Sparse regime — the bench's subjects

| cell | matches | VM lead | VM mid | VM trail | DFA | lead/VM | (lead+trail)/VM | **VM/all** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| capability base10num-grok, t-1m | 49,151 | 49,151 | 487,524 | 0 | 2,762,952 | 9.2% | 9.2% | 14.3% |
| capability quotedstring-grok, t-1m | 2,975 | 2,975 | 57,696 | 0 | 1,276,396 | 4.9% | 4.9% | 4.4% |
| loglines level-context, t-1024k-hit | 193 | 386 | 39,210 | 386 | 4,274,824 | 1.0% | 1.9% | 0.9% |
| email `(orig)` (capture-wrapped), t-a-valid-addrs | 40,330 | 0 | 2,298,818 | 0 | 7,703,003 | 0 | 0 | **22.1%** |
| email `(orig)`, t-d-prose-sparse-addrs | 496 | 0 | 27,040 | 0 | 4,507,017 | 0 | 0 | 0.6% |
| loglines iso-ts with 6 captures, t-1024k-hit | 193 | 0 | 8,685 | 0 | 101,935 | 0 | 0 | 7.7% |
| loglines kv-quoted with 2 captures | 386 | 1,158 | 8,396 | 4,922 | 4,209,032 | 8.0% | 42.0% | 0.3% |
| loglines stack-frame with 3 captures | 659 | 3,954 | 70,203 | 659 | 364,078 | 5.3% | 6.2% | 16.8% |
| `sshd\[(\d+)\]: `, t-1024k-hit | 150 | 150 | 1,144 | 150 | 15,362 | 10.4% | 20.8% | 8.2% |
| `\b(ERROR\|WARN\|INFO\|DEBUG)\b ([a-z]+)`, t-1024k-hit | 798 | 1,596 | 10,775 | 0 | 4,252,581 | 12.9% | 12.9% | 0.3% |
| secrets github-pat, secrets.bin (1 token / 4 KB) | 86 | 258 | 7,224 | 172 | 57,358 | 3.4% (det_all: 100%) | — | 11.7% |
| secrets slack-webhook, secrets.bin | 85 | 2,720 | 4,505 | 0 | 48,884 | 37.6% | 37.6% | 12.7% |
| secrets aws-key, secrets.bin | 85 | 255 | 1,700 | 170 | 4,289,799 | 12.0% | 20.0% | 0.0% |

Three readings. (i) **The VM is a minority of the work on every cell**:
0-22% of executed tests; the prefilter's DFA scan over the subject is the
rest, and on the sparse cells it is everything. (ii) **Where the lead
share is high, the VM share is low, and vice versa**: slack-webhook's 44
byte tests are 38% of a VM that is 13% of the whole (product 4.8%);
email's VM is 22% of the whole and has no leading segment at all. The
product never exceeds 5% on these cells. (iii) The `(lead+trail)/VM` of
42% on kv-quoted is the closing `"` and the `\b` — a trailing segment of
one byte and one context test, whose value under F3 is one `==` (§3.1).

### 5.3 Dense regime and the twins — `studies/pf_know/results/twins.md`

The prize scales with the VM's share, so the twins were run where that
share is largest: match-dense synthetics (`secrets_dense.bin`: 6,000
secrets tokens separated by `" x "`, one match per ~67 B; `sshd_dense.bin`:
60,000 lines `sshd[N]: word`). Each twin is a hand edit of the emitted C
(`twin.py`): `detall` reports the captures off the window and never calls
`rx_match_anchored`; `prefix K LABEL SLOT@OFF` replaces `rx_L0` with
`scan_position += K; RX_SET(...); goto LABEL`. **Answer identity is
checked before timing** (every span of every match, hashed) and held on
all six cells. Mac M1, gcc-16 -O2, load 3.6-6.3 (other lanes' suites were
live), 7 alternating trials, medians:

| twin | sparse (bench-shaped) | dense | VM/all tests (dense) |
|---|---:|---:|---:|
| github-pat, **whole VM skipped** (det_all) | x1.003 | **x1.127** | 11.7% |
| slack-webhook, **44-byte caseless prefix** + `{8}` skipped | x1.001 | **x1.044** | 12.7% (lead 37.6% of VM) |
| `sshd\[(\d+)\]: `, **5-byte memcmp prefix** skipped | x1.000 | x1.009 | 8.2% (lead 10.1% of VM) |

The test-line share predicts the time share well enough to be a planning
number: the whole-VM twin at 11.7% of tests bought 11.3% of time; the
prefix twins bought 4.2% and 0.9% against products of 4.8% and 0.8%.
DIRECTIONAL: darwin, loaded box, no x86 arm (the box was reserved this
evening and tomorrow — the Linux re-measure is OWED only if §8's trigger
fires; the study is committed so it can be re-run there unchanged).

One incidental finding from the slack twin: a CASELESS literal run is
emitted as per-byte `(c | 0x20) == k` tests, not as one compare —
`pcrec_lit_run` is "EXACT only: a caseless letter is a two-member class"
(cpset.c:375). That is [OPT-LITSCAN] S4 / [WORD-FOLD]'s territory and its
census already exists; noted here because the 44-test prefix is the reason
this twin reads x1.04 rather than x1.01.

## 6. Question 2 — the class tables

### 6.1 Representations, side by side

| engine | table | shape | keyed by | what a test costs |
|---|---|---|---|---|
| DFA (both machines of the prefilter, and the anchored machine) | `<p>_<m>_byte_class[256]` | byte → class index (0..C−1); C = the number of distinct transition columns of the machine | byte | one load, then the premultiplied `next_state[state + class]` ([OPT-3]) — the class index is never tested for membership, it is an INDEX |
| DFA scan edge ([OPT-5]/[OPT-EDGE]) | `range` compare, or a 256-byte `bitmap` (`dfa_scans[]`'s `bitmap` row, `scan_tables_bitmap`); D139 retires the edge's own class decision in favour of the ROWS form | byte | one load or one compare |
| DFA candidate prefilter | `<p>_can_begin_match[256]` and the offset-set tables | byte | one load |
| VM per-site bitmap ([FORM-CHAR]/[CLS-TREE] `CLST_SITE`) | `<p>_class_bitmap<i>[32]` | one bit per byte | byte | one load + shift + mask; a singleton, a range and a fold pair compile to compares and own no table |
| VM shared atom table ([OPT-CLSPACK], `CLST_ATOM`, ≥11 table-read classes and ≤64 atoms) | `<p>_class_atoms[256]` + one `static inline` matcher per class | byte → atom | byte | one load + one atom-set test |
| VM wide classes ([CLS-TREE] kit, utf8) | `<p>_wcls<i>` kit matchers | decoded code point | — |

The DFA's `byte_class` IS an atom table — the coarsest partition under
which every state's transitions agree — over the whole machine's
alphabet: every set the erased pattern's NFA reads, literals included as
singletons. The VM's atom table is the same construction over the VM's
table-read class sites only. So on a hybrid the DFA's partition is at
least as fine as the VM's on every class the DFA saw, and the sharing the
charter asks about is: index the DFA map, then test a bitmap over DFA
classes (⌈C/8⌉ bytes) instead of over bytes (32 bytes).

### 6.2 Measured

Over the census's 1,142 hybrids: **74 carry both a DFA and a VM class
table** (6.5%; 4 of them the atom table, none the kit — the corpus's
byte-mode classes are small), holding 118 VM bitmaps (3,776 B).

| question | answer |
|---|---|
| does the DFA forward partition refine the VM bitmap? | **114 of 118 bitmaps**; 66 of 74 artifacts have every bitmap refined |
| the 4 that are not | `a(?!(?:(?<=\w)(?!\w)\|(?<!\w)(?=\w)))b`, `(?<=\b)a`, `email-local-nodup` (`^(?!.*\.\.)…`), `pwd-strength-chain` (`^(?=.*[a-z])…`) — every one a class inside a lookaround body the prefilter erased, exactly the F3-failing population; the DFA never saw the set |
| DFA class counts on the 74 | ≤8: 56; ≤16: 6; ≤32: 9; >32: 3 |
| bytes saved if every refined bitmap became a DFA-class bitmap | **3,373 B corpus-wide** (32 → ⌈C/8⌉ per bitmap; the 256-byte DFA map already exists) |
| forward vs reverse `byte_class` identical | **59 of 59** hybrids carrying both machines (the other 15 are start-pinned, no reverse machine): 15,104 B — [OPT-D]'s within-artifact dedup, not a VM question |

### 6.3 Verdict

Representationally the tables CAN be shared on 97% of the sites, which
refutes the guess as stated. On benefit the guess stands, for four
reasons that do not need a clock:

1. **The prize is 3.4 KB over 3,347 artifacts**, 45 B per affected one,
   against artifacts of 20-30 KB; [ART-SIZE]'s size term would not see it.
2. **It makes the VM test slower, not faster.** The DFA reads its map as an
   index into a premultiplied row; the VM would read it as a first load
   feeding a second dependent load, where today it does one load. The VM
   holds no DFA state at any point — the hybrid hands it a window, not a
   class stream — so there is no register to reuse.
3. **It couples the VM's class tests to the prefilter's alphabet**, which
   is a function of the ERASURE: the four failing sites are the proof that
   a class the VM tests can be invisible to the DFA, so the sharing would
   need a per-site fallback — a parallel mechanism for 3% of sites.
4. **The sharing that is worth having was ruled yesterday.** D139 makes the
   DFA scan edge consume the VM's class-form rows (ROWS) and the SAME
   emitters — range, fold, kit, table — so one class decision and one
   spelling serve both engines. That is one derivation with two readers;
   a shared byte table would be two derivations with a cross-reference.

Nothing to build; [OPT-D] and [XART-TABLES] keep their rows and their
triggers, and this note adds the 59/59 measurement to [OPT-D]'s evidence.

## 7. Refuted, and not built

- **"Trace the prefilter with the VM and prove class membership at other
  offsets"** — refuted as a general mechanism: past the first choice point
  the DFA's accepting path is one of many, and the VM's path is the one
  it chooses; membership at an offset is provable only on the fixed-width
  choice-free segments (§3.1), where the census finds it is 83% literal
  bytes anyway.
- **"DFA-approved lookarounds"** — exist and are already consumed: the
  one-character lookarounds U2 lowers to `A_CTX`, and `\b`-family nodes,
  are DFA-decided and sit in the leading segment of 152 exact hybrids as
  ONE test each. Multi-character lookarounds are erased (F3 fails; 452+121
  hybrids), and the prefilter proves nothing about them; [CTX-PREFILTER]
  is the row that would tighten the prefilter by their necessary byte,
  which is the opposite direction.
- **A leading-segment skip as its own batch item** — sound (§3.2), cheap,
  and bounded by the product of two small shares (≤5% of tests on every
  bench-shaped cell, x1.00-1.04 on the twins). Not proposed; folded into
  the one-pass row as its trivial member (§8).
- **The trailing segment** — one `==` against a `memcmp` the VM does
  anyway; not measured, not proposed.
- **Sharing the DFA's byte-class map with the VM** — refuted on benefit
  (§6.3).
- **Frank's guess ("no overlap")** — refuted on representation (114/118
  refine), upheld on what it was really asking (is there anything to
  gain): no.
- **The manager's framing "for each prefilter kind, what it establishes"**
  — the enumeration collapses: the VM route has one per-position
  prefilter kind with one exactness bit; the DFA-side forms are that
  prefilter's internals and the whole-window checks prove nothing at a
  position (§1).

## 8. Candidate [OPTLOOP] rows, with the evidence

Per D137 these are candidates for the next cycle's MEASURED selection,
not scheduled work. Per D77 each names the measurement that would trigger
it.

1. **[PF-KNOW] itself: CLOSE as a research row; no mechanism of its own.**
   Its output is this note and the numbers above.
2. **Member of the one-pass / captures-via-DFA row** (`captures_via_dfa_
   survey.md` §3.3, `onepass_census.md`; not yet a plan row of its own):
   the `det_all` subset (164 exact hybrids, 29%; 138 with captures; in the
   bench `github-pat`, `grp-cap`, `grp-named`, `grp-named-quote`) is where
   the VM is redundant in full, measured x1.13 on a match-dense subject
   and x1.00 sparse. A one-pass rung serves it with constant offsets and
   the rest of the one-pass class with a deterministic walk; a leading
   prefix is the same rung stopping early. Recommended shape when that row
   is designed: the VM entry consumes `(start, end, exact)` as a fact and a
   first-match row table selects `whole` / `prefix` / `none`, the prefix
   row being the fallback of the whole row rather than a mechanism.
   **TRIGGER**: a bench cell in the match-dense regime (whole-subject
   `match`, or find-all over a hit-dense subject such as email's
   `t-a-valid-addrs`) on which a hybrid's VM share is measured ≥10% of
   TIME on Linux. Today's ledgers have no such cell — the capability
   throughput rows are nomatch on `t-1m` for 12 of the 17 capture-forced
   hybrids, so their VM never runs there.
3. **[OPT-D] evidence** (no new row): forward and reverse `byte_class`
   coincide on 59/59 hybrids that carry both; 256 B each; the anchored
   machine's map is a third copy on DFA artifacts (not counted here).
4. **A stamp question for the manager, not a row**: `<PREFIX>_VM_PREFILTER_
   LANG` answers the count-collapse axis only and reads `"exact"` on
   lookaround/atomic/`\K` hybrids whose END is unproven; the exactness
   fact a reader wants is `Vm.mrl_win`, visible only through the reseed
   row. Whether it deserves its own stamp line (an abi event, D76/D94) is
   a spec question — filed, not argued.
5. **Not a row, a pointer**: the caseless-literal per-byte lowering seen in
   §5.3 belongs to [OPT-LITSCAN] S4 / [WORD-FOLD], whose census exists.

## 9. Reproduction

`studies/pf_know/CLAUDE.md` has the commands. In short: build the tree,
`gcc-16 … segprobe.c build/libpcrec.a`, run `census.py` with `BENCH`
pointing at the read-only sibling checkout, `dyn.py` per cell, `twin.py`
per twin. The committed `census.tsv`/`summary.json`/`results/` are the
2026-09-30 run at `d88374d5`. The subjects are the bench's own committed
`capability/throughput/t-1m.bin` and its generators run with `--out` into
scratch (nothing in the bench checkout was written: `git status` clean);
the two dense synthetics and the sparse `secrets.bin` are generated by
`studies/pf_know/gen_dense.py` (seeded).
