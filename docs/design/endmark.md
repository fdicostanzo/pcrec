# D164 — the MATCH-END MARK (`END_MARK`): design note

**Status: PROPOSED, design + hand-twin; nothing under `src/` changes.** Lane
`endmark`, 2026-10-12, from main `885eccff`, abi 76. Ruling: D164
(`../dev/decisions.md`). Instruments and transcripts: `endmark/` (own CLAUDE.md).
The `.rxt`/pcrec checks this note asks for are build work (§6). Read §0, then §1.3
(the rule) and §2.3 (where D164's own wording is too strong).

**REVISION 2 for B3 (lane `b3rev`, 2026-10-12): read §R first for anything about
the rev-end walk.** It applies the r3 panel (S1-S10, C1-C8) and D164 addendum 4,
tags only where the artifact can tie (Frank, session 110), and supersedes the B3
parts of §0 items 4-5, §2.3, §4.3's `end_pin` row, §5.6 S-EM8..S-EM10 and §6 E3.

## §R. B3 REVISION 2: TAG ONLY WHERE THE ARTIFACT CAN TIE (lane `b3rev`, 2026-10-12)

**Status: PROPOSED, build-ready design; nothing under `src/` changes.** From main
`e8ca1252`, abi 76. Binding inputs: D164 and addenda 1-4, the light D6 panel
`../dev/reviews/2026-10-12-r3-b3-endmark-revend.md` (S1-S10, C1-C8), lanes
b3cost/b3meas. Frank approved the direction (session 110): tag only where the
artifact can tie. Instruments and raw results: `endmark/b3rev/` (own CLAUDE.md),
`endmark/b3rev/timing/` for the clock. This section supersedes the B3 parts of
§0 item 4-5, §2.3, §4.3's `end_pin` row, §5.6 S-EM8..S-EM10 and §6 E3; those
sections stay as the record of the first design and are annotated where they
moved.

### §R.0 Panel finding → where it is answered

| id | finding (short) | answered in |
|---|---|---|
| S1 | mixed artifact: view-based forward machine seeds a lowered reverse machine | §R.2 (one lowering per artifact, by NFA-build parameter), §R.2.1 table |
| S2 | the tie set depends on the previous byte's class | §R.1.2 (D(q,a) per context atom, the absent atom included); witness `(?:\Bx\n\|x)$` §R.6 |
| S3 | scan-edge / stay skips merge on accept BIT | §R.3 (the accept value IS the distance set; four comparison sites compare values); witness `\n{1,4}$` |
| S4 | tagged builds can create refusals | §R.1 rows `overflow`, §R.5 (optional builds + fit rung `drop-end-mark`), §R.4.4 refusal-set compare |
| S5 | an unmarked thread carries d = 0 | §R.1.2 (definition); instrument fixed (`endmark/b3rev/b3rev.py` `rw`), 3 such artifacts |
| S6 | the VM's `$` under the mark is ambiguous | §R.2.3: the VM KEEPS the assertion |
| S7 | `mark_prio`'s forward-NFA cost unstated | §R.1.4: measured, total 230 states over 38 artifacts, max 39 |
| S8 | held cases | §R.6 witness list carries each |
| S9 | the `\n?` tail is hard-coded | §R.2.4: the tail is read from `\Z`'s definitions row |
| S10 | the end-distance fact is encoded ~7 ways | §R.8 (sibling family; leaning: B3 builds the ONE representation, the accept value as a distance set, and `mark_prio` becomes FINISH row `prio-const`) |
| C1 | the win is a few cells; "~40 lines deleted" | §R.4.1 (cell table per class), §R.4.7 (net code: B3 now ADDS code; nothing is deleted) |
| C2 | "at most 2x" is a census maximum | §R.4.3 (N-sweep) |
| C3 | the population is what compiles today | §R.4.4 (refusal-set compare, plain/lowsize/lowboth) |
| C4 | weak gates; tagged scan-edge unmeasured | §R.4.2 (the spike), §R.6.1 (per-artifact gates on emitted states, exemption list, literal floors) |
| C5 | ctx/utf8 figures guessed | §R.4 controls C1-C13 (ctx rows named), utf8 lines |
| C6 | selective tagging uncosted | it IS this design (§R.1) |
| C7 | six mech plants with SAB_REACH | §R.7.2 (ten plants) |
| C8 | movers: re-aims, abi readers, `end_pin`'s two answers | §R.7.3, §R.7.4 (`end_pin` keeps ONE answer, `eol`) |

### §R.1 The selection, as a first-match table

Asked once per compile, after today's three machines are built and LOCATE has
selected `rev-end` on an `end_pin = eol` body (a `$`/`\Z` artifact; a `\z`-only
artifact is unchanged). Rows are data beside `cand_rows[]`'s `rev-end` row
(`start_table.md` §0a), listable as the sub-axis `rev-end-form`.

| # | row | applies when | the walk | machines (NFA build) | a tie is decided by |
|---|---|---|---|---|---|
| F0 | `denied` | `-fno-rev-end-onewalk` (new deny, bit 55; §R.9 Q1) | today's two-seed walk | today's (`$` as a view) | today's tie code where `nl_last` |
| F1 | `one-seed` | `nl_last` is false on today's reverse machine (`revend_nl_last`, unchanged) | ONE seed: `n−1` if `s[n−1]` is in the tail's first-byte set (`'\n'`), else `n`; when the `n−1` walk finds no accept, the seed state's accept AT `n` is probed (a zero-length match at `n`: `\B$` on `"a\n"` is (2,2)) | today's | (no tie is possible) |
| F2 | `tagged` | the TIE FACT holds (§R.1.2) and every lowered machine fit (§R.5) | ONE walk from `n` over the TAGGED reverse machine; at `s*`, D = the accept value read with `s[s*−1]`'s context atom (absent atom at 0 / at the startpos boundary) | LOWERED forward, reverse (tagged), anchored (§R.2) | \|D\| = 1: end = `n − d`; \|D\| ≥ 2: FINISH row `prio-const` (end = `n − c`) when `mark_prio` is `const c`, else `verify-at`, else `search-from` (today's rows) |
| F3 | `two-seed` | the tagged machine was built, fit, and no (state, atom) carries two distances | today's two-seed walk WITHOUT tie code (a tie is proven impossible) | today's | (none) |
| F4 | `overflow` | otherwise: a lowered/tagged build overflowed | today's two-seed walk | today's | today's tie code |

Why F1 needs no tag. `nl_last` false means the seed state at `n` and its views
die on the tail's first byte, so when `s[n−1] = '\n'` the only accept seed `n`
can still reach is AT `n` itself; every start seed `n−1` finds is `≤ n−1`, so
it wins. When `s[n−1] ≠ '\n'`, seed `n−1` does not exist. The end is then a
function of the last byte. This is b3meas §4's argued fix, now built as a twin
(arm U, §R.4.6) and answer-checked (0 wrong of 71,330,165 cells).

Why F3 exists. The brief's binary "non-singleton vs the rest" leaves a gap: an
artifact whose X can consume a final newline (`nl_last` true) but whose
distance at every accepting state is single — `a\n$`, `(?:a|b\n)+$`,
`(?:\n\n|a){0,4}$` — cannot tie, yet its end is NOT a function of the last byte
(`a\n$` on `"a\n"` ends at 2 = `n`, on `"a\n\n"` at 2 = `n−1`). Tagging it would
be correct but spends states on an artifact that cannot tie, against Frank's
direction; the last-byte rule would be wrong. So it keeps today's two seeds,
minus the tie code today emits for it (today's tie code is keyed on `nl_last`,
which over-claims here). Population: 0 shipped (§R.4.0), 3 synthetic witnesses.

**Populations (census at `e8ca1252`, `endmark/b3rev/results/census.txt`):** of the
266 rev-end `$`/`\Z` artifacts (bench 9, corpus 257): F1 `one-seed` **223**
(bench 8, utf8 13), F2 `tagged` **43** (bench 1, `capability/tail-space-eol`;
utf8 3), F3 **0**, F4 **0**. The 43 are exactly today's 43 tie-code artifacts
(control C13: today's emitted `revend_tie` == the probe's `nl_last`, 266/266),
and every one of them carries a tie: today's `nl_last` is exact on the shipped
population and over-claims only on the F3 witnesses.

#### §R.1.2 The tie fact, defined exactly (S2, S5)

Let the lowered body be `X·M·T` (T = the tail, `\n?\z` today, §R.2.4) with
`L = maxw(T')` (1 for `$`/`\Z`). Build the REVERSE subset construction (prune
off, as D7's reverse machine already is) over pairs (NFA state, d): a thread
starts at the seed `n` with d = 0 and d grows by one per byte the TAIL consumes;
crossing M freezes it. A thread that reaches ACCEPT without crossing any M (an
unmarked path end: `b\z` in `a$|b\z`, `\w+\z` in `\d+$|\w+\z`) carries **d = 0**:
its reported end is its consumed end, `n` (S5; 3 shipped artifacts carry such an
arm, `ab\z|b\Z`, `\d+$|\w+\z`, `\s*$|x\z`). A tagged state q is the set of its
pairs. For each context atom a — the atoms of `Dfa.natoms` (the previous byte's
class-axis context) **plus the absent atom** (position 0, and the walk's
termination boundary at `startpos`, assertions_design.md §3.8.3.1) — define

    D(q, a) = { d : (ACCEPT, d) is in q's closure under context a }.

The walk reads D(q, a) where it reads today's accept cell. **The tie fact** is
"some reachable q and some a have |D(q, a)| ≥ 2". It is a property of the BUILT
tagged machine, computed while building it (one OR over the accept cells), never
a separate walk. Measured on the 43: every tie occurs under every atom including
the absent one (class-dependent ties: 0); the S2 witness `(?:\Bx\n|x)$` is
class-dependent (a tie under the word atom only) and must be in the witness file
(§R.6), since the population has none.

Built how. As ONE tagged subset construction in `src/ir/dfa.c` (a thread carries
d; pairs intern as the state), not as the probe's product of L+1 untagged
machines: the product needs L+1 builds and a product pass, and its
non-accepting junk states (an unmarked arm in the d = 1 machine) need a trim
the direct construction never creates. The probe's product is the build's
INDEPENDENT CONTROL (§R.6.2): two constructions, one answer.

#### §R.1.3 The walk at `s*`

`s*` is the smallest accepting position (today's rule, unchanged). The accept
cell at `s*` holds D as a bitmask (§R.3). |D| = 1 (bit d): end = `n − d`, SPAN.
|D| ≥ 2: ENDSET, which FINISH takes by first match: `prio-const` (new, §R.8),
`verify-at`, `search-from` — today's two rows, unchanged. On a VM hybrid's
inlined body the hand is projected as today (`cand_project`); a SPAN reaches the
VM's `verify-at` with the window ceiling at the reported end, exactly as today's
seed position does (§R.2.3).

#### §R.1.4 `mark_prio`, the fact (S7)

Computed over the UNPRUNED anchored forward machine of the lowered NFA
(`pcrec_build_dfa`, prune off, root `anch_start`), on demand, only for an F2
artifact: at every pre-set's END closure the accepting distances are listed in
priority order; where two or more distinct distances appear the FIRST is
recorded; one recorded value is `const c`, none is `none` (impossible on F2 by
the tie fact), more is `state-dependent`. Overflow of its cap answers
`state-dependent` (the safe side: FINISH runs). A context atom is evaluated per
atom (the build's DFA already carries atoms); the probe does not model it and
reports those 5 artifacts as unmodelled.

**Measured** (`b3rev_probe.c`, exact over pcrec's own NFA and DFA): on the 38
modelled F2 artifacts `mark_prio` is `const 0` on 28 and `const 1` on 10;
`state-dependent` on none (b3meas's empirical classification agrees: all 30 of
its tie artifacts const). **Cost: 230 unpruned states in total, median 4, max 39**
(`([^/]+)$` under utf8) against the 32,000 cap; at N = 2048 in the sweep
(§R.4.3) it is N + 4. The synthetic `(?:\s+|x\s*?)$` reads `state-dependent`, the
witness for FINISH's verify-at arm. The probe's classification is checked
against libpcre2's choice on every observed tie by b3meas's method (§R.6.2).

### §R.2 One lowering per artifact (S1, D164 addendum 4)

**The decision.** `$`/`\Z` lowering is an NFA-BUILD PARAMETER, not a second tree.
The endmark pass (§4.1) marks each path-final `$`/`\Z` node (`A_EOL` with a tail
bit, from the tail walk §1.1) and does NOT rewrite it. `pcrec_build_nfa` gains a
`lower_eol` argument: under it, a tail-bit `A_EOL` builds `M·T` with an
`ACC(d)` accept per tail length (§2.2's mechanism); without it, today's N_EOL.
One tree; per artifact the selection decides which build every machine uses.
That keeps §2.2's D7 argument true as written: every machine of an F2 artifact
reads ONE language. (Multi-character trailing lookaheads, E2, stay an AST
rewrite: they have no "today's machine" to keep.)

#### §R.2.1 Which machine is built from which NFA, per form

| form | forward `dfa` | reverse `rdfa` | anchored `adfa` | VM program (hybrid) |
|---|---|---|---|---|
| F0 `denied`, F1, F3, F4 | today's (`$` view) | today's | today's | today's (`$` assertion) |
| F2 `tagged` | `lower_eol`, ACC(d) → accept value {d} (§R.3) | `lower_eol`, TAGGED (§R.1.2) | `lower_eol`, ACC(d) | today's (`$` assertion, §R.2.3) |
| `-fno-rev-end` (no rev-end walk) | today's | today's | today's | today's |

- **The relocate** (`search-from`, F2's tie arm when the anchored machine is
  absent: `-fno-anchored-dfa` or its optional build overflowed): the composite
  from `s*` runs the LOWERED forward machine (its END accept value gives `back`)
  and the tagged reverse machine (the composite reads its accept TRUTH, ignoring
  D). This is S1's cell: `(?:\s+|x\s*?)$` on `"x\n"` reads (0,1) because the
  forward machine now carries the tail.
- **`-fno-rev-end`** never selects the walk, so no machine uses the mark and
  D164 addendum 3 stands: today's artifact, byte for byte.
- **Order.** compile.c builds today's three machines (unchanged), LOCATE and the
  form row are asked, and only F2 builds the lowered three as OPTIONAL machines
  (§R.5); on F2 they replace today's in the Job; on any overflow today's stay.

#### §R.2.2 Measured: addendum 4's forward and anchored growth (`results/census.txt`)

On the F2 set (43; 38 modelled for the tagged figures, 5 context-atom artifacts
unmodelled): forward machine emitted states **216 → 290 (+34%), per artifact max
+3**; anchored **163 → 215 (+32%), max +6** (`[^c]{0,4}?$`, 6 → 12). The tag
itself costs the forward/anchored machines NOTHING: the Moore minimization with
`back` as an output equals the untagged lowered count on every modelled
artifact (C8/C9, 220/220), because D3's accept-pruning already leaves one
winning distance per accepting state; one artifact outside F2 (`ab\z|b\Z`, an F1
row that is never lowered) has pre-sets that disagree on `back` and would need a
split. Over all 266 (the counterfactual "lower everywhere"): forward 2,015 →
2,751 (+37%), max +5. The SWEEP (§R.4.3): forward + 3 and anchored + 2 at every N.

**Time on the tie path** (`timing/results/report.txt` §A; today's `X$` artifact
vs the lowered `X(?:\n)?\z`, same flags, from `s*`, nl-m subjects; 782 subjects ×
6 arms answer-checked, 0 wrong): verify-at (`_match`) today/lowered **1.09-1.31**
class geomean (the LOWERED machine is FASTER: no `$` view probe per step); the
relocate (`-fno-rev-end` `_search` from `s*`) **0.97-1.07**, per cell p5-p95
0.73-1.38, A/A 0.87-1.20. Addendum 4's "not slower" holds.

#### §R.2.3 The VM keeps the assertion (S6)

On a hybrid the VM program keeps `$` as today's assertion (`N_EOL`'s VM arm). The
reasons, in order:

1. At a given position m, `\n?\z` succeeds in at most one way (§1.2), so the
   lowered tail and the assertion are the same test; the mark position IS the
   assertion position. Writing it as `\n?` would add a choice point that
   frames frameless `X$` programs (VM_FRAMELESS, the tier, STEPS give-ups,
   possessify's follow sets: the panel's D158 concern) for no answer; writing it
   as a deterministic tail test would move emitted VM text on every `$` program
   for the same answer.
2. Addendum 4's rule is about machines that answer "where does the match end"
   FROM AN AUTOMATON (the D7 seeding argument). The VM answers it from its own
   leftmost-first run, and its window ceiling (§2.2 F3) is the reported end it
   is handed — today's seed position, F2's `n − d` — which is the assertion's
   position. Nothing the VM reads changes meaning.
3. D158: the give-up surface does not move (no program changes).

The VM's slot-1 mark (§2.1) remains E2's, for multi-character lookaheads.
**This is a reading of addendum 4 for Frank to confirm (§R.9 Q3).**

#### §R.2.4 The tail comes from one definition (S9)

`T` is `plain(Y)` of `\Z`'s definitions row (`src/parse/registry.c`'s `z_def`,
`(?=\n?\z)`; `$` chains to it by `DEFK_ROW`), parsed once per compile, never a
hard-coded `'\n'`. Everything that reads the tail derives from it: L = maxw(T'),
the distance domain 0..L, F1's first-byte set, and `nl_last`'s byte class. A
newline convention (DD-11) is then a different definition row, not new code:
CRLF gives L = 2 and D ⊆ {0, 2}; ANYCRLF D ⊆ {0, 1, 2}. NOTEOL is a match-time
option pcrec does not have (`docs/pcre2_options.md`); the trigger is a request.

### §R.3 The accept value IS the distance set (S3)

`DView.accept` (a `uint8_t`, today 0/1) carries the distance set as a bitmask
(bit d) on an F2 machine: the tagged reverse machine's cells hold D(q, a); the
lowered forward and anchored machines' END-view cells hold {b} (one winner, by
D3's pruning). Every machine that is not F2 keeps 0/1, i.e. the set {0}. Readers
that TEST an accept stay truth tests; the four readers that COMPARE two accepts
compare VALUES:

| site | today | after |
|---|---|---|
| `src/opt/minimize.c:133` initial partition key | `if (accept) a \|= 1u << u` | keyed by the value |
| `src/opt/scanedge.c:287` `acc_of` (and `end_acc_of`, which calls it) | `accept != 0` | the value |
| `src/ir/dfa.c:1204` `view_same`, view equality at interning | `(bool)a->accept == (bool)b->accept` | values equal |
| `src/gen/emit_dfa.c:3992` `state_acc_varies` (the stay skip's eligibility; callers :4121, :4833, :12447) | `(bool)` compare | values |

`scanedge.c:222` (`class_invariant`) already compares values. The census is
`grep -n '\.accept' src` (40 reads in 5 files); the build re-greps it and
classifies every read as TEST or COMPARE.

On a 0/1 machine a value compare IS the truth compare, so every non-F2 artifact
is byte-identical by construction (the B3.0 commit's zero-mover claim, §R.7.1; today every accept is set from a `bool`, `src/ir/dfa.c:978/1374/1495`).
The emitted accept table is already a `u8` per cell (timing/ E1), so the set
rides the existing table: no new array, no separate `back` table. The walk reads
`d` as the cell's lowest set bit (F2's SPAN) or the whole mask (ENDSET).

**Measured** (`b3rev_probe.c` links a probe-local copy of scanedge.c with
`acc_of` reading the value, beside the shipped pass): on the 266 the two passes
produce the same machine (0 artifacts differ), so S3 has no shipped witness; the
synthetic `\n{1,4}$` (tagged 7 states: shipped pass 4, value pass 5) and
`\n\n?$` (4 vs 5) are where the shipped pass merges differing distance sets: the
sabotage witnesses. The stay skip records its landing position's cell (read with
that position's atom), so a value-compared `state_acc_varies` is conservative
(a class-varying D declines the skip); population 0.

### §R.4 What was measured

All counts are pcrec's own machines (`b3rev_probe.c` links `libpcrec.a`);
"post" is after the scan-edge pass, i.e. the emitted count. Controls
(`results/census.txt`): C1 reverse today probe == emitted 266/266; C2/C3 forward
and anchored today == emitted (`-fno-rev-end`) 265/265, 169/169; C4/C5 the
patched-NFA lowered machines == the CLI-emitted `X(?:\n)?\z` artifacts 264/265
(the miss, `(?s)(.+)$`, emits no forward table under `-fno-rev-end`), 169/169;
C6/C7 the tagged product with an OR output == the untagged machine 254/266 (the
12 misses are context-atom patterns, `\bfoo$`-shaped, all outside F2: the product
does not carry the class context in its state, b3cost's known 22); C8-C12 the
forward/anchored tagged model with `back` ignored == pcrec's minimizer, its
closure accept == pcrec's END accept, rebuilt post == pcrec post, 220/220 each;
C13 today's emitted tie code == the probe's `nl_last` 266/266.

#### §R.4.0 Populations and literal floors

rev-end `$`/`\Z` artifacts **266** (bench **9**, corpus **257**); F1 **223**; F2
**43** (bench **1**); mark_prio const0 **28**, const1 **10**, context-atom **5**;
unmarked-arm (S5) **3**; utf8 F2 **3**; F2 reverse growth over 2× today + 1: **2**
(`[^c]{0,4}?$`, `[^c]{0,4}$`). Re-counted by the probe at every build step (K35),
never copied.

#### §R.4.1 The cells, per class (C1)

ns/call class geomeans, Linux dev box, `taskset -c 2`, A/A per-cell p5-p95
0.87-1.27 (b3meas §2 for B/today; `timing/` for U, W and the F2 finishers).
"m" = matching, "n" = not; "nl" = the subject ends in `'\n'`.

| class (artifacts) | form | nl-m | nl-n | nonl-m | nonl-n |
|---|---|---|---|---|---|
| F1 no tie (109 twinned) | U (today's text, one seed) vs today | **0.72x** | **0.67-0.71x** | 0.92x | 0.98-1.00x |
| F1 no tie | W (form W, §R.4.6) vs today | **0.61x** | **0.53x** | 0.68x | 0.66x |
| F2 const, bounded X (12) | tagged (plain) vs today | **0.38x** (T/B 2.56-2.66) | (b3meas 0.50x) | 0.66x | (0.75x) |
| F2 const, unbounded X (17) | tagged vs today | **0.37x** (T/B 2.67-2.77) | (0.54x) | 0.70-0.76x | (0.72x) |
| F2 state-dependent (1, synthetic) | tagged + verify-at vs today | 0.54-0.68x | — | 0.73-0.76x | — |

The split C1 asked for: the 3.00× → 1.00× pass lands only on F2 cells whose
subject ends in a newline (the per-line regime), 2.4-2.8× faster there; on F2
cells without a final newline the tagged walk is still 1.3-1.5× faster (the
dropped seed-loop and view probes); on F1 cells the one-seed rule alone is
1.4× on nl cells and neutral otherwise. Bench: 1 of 9 artifacts is F2
(`tail-space-eol`), 8 are F1.

#### §R.4.2 The spike C4 asked for: the tagged machine after scan-edge

On the F2 set the scan-edge pass compacts NOTHING: tagged reverse **281 → 281**
states (today's pass took today's machines 160 → 151). Tagged post vs today
post: **151 → 281 (1.86x), per artifact median 1.75, p90 2.25, max 2.75, +7
states max**. Over 2× today: the `[^c]{1,3}` family (4 → 9, = 2×4+1) and
`[^c]{0,4}`/`[^c]{0,4}?` (4 → 11): today's pass collapses their counted run, the
tagged machine's run has two live classes (`'\n'` and the rest) and is not
scan-shaped. The counterfactual "tag all 266" is 1,505 → 2,741 post (1.82x); the
pass buys 4% there. So selective tagging also avoids the one place tags cost
the most: compacted bounded runs (the sweep below).

#### §R.4.3 The N-sweep (C2; `results/sweep.txt`)

| family | today reverse post | tagged reverse post | forward today → lowered | anchored | mark_prio states |
|---|---|---|---|---|---|
| `\s{0,N}$` | **4** (constant: scan-edge) | **2N + 3** (no compaction) | 3N+2 → +3 | 2N+2 → +2 | 2N + 4 |
| `[a-z]{0,N}\s{0,N}$` | 2N + 2 | 3N + 6 (N ≥ 2) | 6N+2 → +3 | 4N+2 → +2 | 4N + 4 |
| `\w{1,N}\s{0,N}$` | N + 4 | 2N + 9 | 6N → +3 | 4N+1 → +2 | 4N + 3 |
| `(?s).{0,N}$` | N + 2 | 2N + 3 | 3N+2 → +3 | 2N+2 → +2 | 2N + 4 |

C2's worry, `|Q|²` pairs, does not appear: every family is LINEAR in N (the d = 0
and d = 1 threads stay in lock-step). Two real findings instead. (1) The
tagged reverse machine is never larger than today's FORWARD machine (3N+2 to
6N+2), which is built today on every rev-end artifact and reaches the 32,000
state cap first; so no family here reaches the cap through the tag (§R.4.4).
(2) The tag DEFEATS scan-edge compaction: `\s{0,N}$` goes from 4 states to 2N+3,
a linear table where today's is constant, and its emitted bytes grow with it
(predicted 528 KB → 1.49 MB at N = 6144). That is a BYTE-cap event, not a state
one: §R.4.4 counts it, §R.5 declines it.

#### §R.4.4 The refusal-SET compare (C3; `results/refusal.txt`)

Keys = (population, pattern, variant) → `ok` | the refusal class. Population:
the 266, the four sweep families at N up to 16,384, and the 21
`tests/resource` witnesses each with `$` and `\s*$` appended (360 keys per
variant); variants: shipped (`plain`), emit_sweep's `lowsize` and `lowboth`
reference builds (60,000-byte cap; `lowboth` adds the 3,000-element DFA budget).
By design B3 never refuses (§R.5), so the shipped refusal set is unchanged by
construction; what is counted is the set the declines must catch: keys that
WOULD join the refusal set if B3 had no decline, from the probe's tagged states
and today's bytes per state.

**Shipped caps (`plain`).** Of the 84 F2 keys that compile today, the tagged form
would push **10** over the 1,000,000-byte cap and **none** over a state cap
(§R.4.3's finding (1): the tag never outgrows today's forward machine): the
sweep's `\s{0,6144}$` (528 KB today → about 1.49 MB predicted), `[a-z]{0,N}\s{0,N}$`
at N = 3072 and 4096 and `\w{1,N}\s{0,N}$` at N = 3328 and 3584 (0.88-0.95 MB →
1.01-1.09 MB), `((a)|bc){0,4000}d\s*$` (615 KB → 1.2 MB), and four utf8
`\p{L}`-family witnesses with `\s*$` appended (`\p{L}+\s*$`, `(?:\p{L}?)+\s*$`,
`\p{L}\s*$`, `(\p{L})\s*$`: 0.80-0.83 MB → 1.30-1.34 MB). With `drop-end-mark`
(§R.5) each compiles exactly as today (F4's machines, one extra compile
attempt), so the refusal set moves by **+0 keys**; without the decline it would
move by +10. **`lowsize`/`lowboth`:** today refuses 51 / 21 keys; the 33 F2 keys
that compile there stay under the 60,000-byte cap when tagged: +0 either way.
The figures are predictions (the probe's tagged and lowered state counts × the
per-state bytes of today's reverse and anchored tables); the build measures
them (gate G3, §R.6.1). `\p{L}+\s*$` is a realistic shape (trailing blanks after
a word): under the shipped cap B3 declines it, i.e. it keeps today's walk.

#### §R.4.5 The utf8 and context-atom lines (C5)

utf8 F2: 3 artifacts (`\s+?$`, `([^/]+)$`, `(\s+)$`), reverse 3/8/3 → 5/15/5,
mark_prio const on all three (`([^/]+)$`: 39 unpruned states, the population's
max). `(\p{L}+)$`, b3cost's outlier (454 → 907), is F1: it cannot tie, it is
never tagged. Context-atom F2 artifacts: 5 (`\W{0,2}?(?:\B|)$` and siblings);
their tagged reverse figures pass the product control (C6), their
forward/anchored tagged figures and `mark_prio` are unmodelled by the probe and
owed to the build's own census check (§R.6.2).

#### §R.4.6 [REVEND-WALK-FORM]: the form, decided once

`timing/` built and answer-checked (0 wrong over 90,962,254 cells, every arm) nine
arms on b3meas's population: T today; R today's algorithm in plain table style;
V = R plus today's per-iteration view probe; S = R plus today's stay placement;
U = today's text with the one-seed rule; P = U's algorithm in R's style; W = P
with the views resolved at the seed and the first step peeled; B and Q = the
tagged walk plain and in today's step shape. Findings:

- **The whole style gap is the per-iteration view probe** at the loop top
  (`rewind + 1 >= n` plus the view-state copy): V/R 1.30-1.71 reproduces T/R
  1.22-1.60, T/V 0.92-0.96, and per-artifact fits `ns = a + b·loads` give T−R
  `a` +0.93 ns per call with `b` unchanged (ratio 1.006): a per-CALL constant,
  not a per-byte one. The stay placement costs nothing (S/R 0.98-1.00), nor
  does the step shape on the tagged walk (Q/B 0.95-1.01).
- **Form W is the fastest one-seed form**: W/R 0.79-0.96, U/W 1.20-1.50,
  T/W 1.47-1.90 (L regimes; K4/M1 within ±0.05).

**Decision: the B3 build emits F1's and F2's walks in form W**: the seed's views
are resolved once before the loop (the seed IS the view state), the first step
is peeled, and the loop body carries no view probe. The probe sits in the shared
`emit_reverse_block`, so RECOVER's reverse pass (every ENG_UNANCH composite)
pays the same ~1 ns per call; moving it there changes every composite artifact,
so it is FILED as `[REVBLOCK-VIEW]` (trigger: the next reverse-block emission
change, or a bench reverse-pass cell at rank), not folded into B3.

#### §R.4.7 Net code (C1)

Under selective tagging NOTHING is deleted: today's two-seed walk and its tie
code remain as F0, F3 and F4, and `revend_nl_last` becomes F1's predicate. Added:
the form table (5 rows), F1's one-seed walk, the `lower_eol` build parameter and
`ACC(d)`, the tagged subset construction, the tie fact, `mark_prio`, FINISH's
`prio-const` row, the value compares (4 sites), the `drop-end-mark` rung, the
deny and its axes row. No net-simplification claim is made.

### §R.5 Declines, never refusals (S4)

Every machine F2 adds is built OPTIONAL (`Dfa.optional`, the anchored machine's
mechanism, `anchored_match_unwrapped.md` §5.2): an overflow of a state cap or of
the DFA element budget records and returns, and the form row falls to F4
(today's machines, today's tie code). The optional builds are charged to their
own caps and never to the engine-selection budget, so the engine route cannot
move. After emission, an F2 artifact over a byte cap takes a new `fit_rungs[]`
row **`drop-end-mark`** (label `size`, the FIRST size rung: it costs no answer
and no other optimization), which retries the compile with the form pinned to
F4. One ladder (D163): no second fallback mechanism. `COMPILE_MAX_ATTEMPTS`'s
table check (dec_fallback.md) covers the new row.

### §R.6 Checks

#### §R.6.1 Gates, per artifact, on EMITTED states and size_bytes (C4)

Each gate's expectation comes from the probe (`b3rev_probe.c`, re-run on the
built tree), which shares no code with the emitter's walk:

| gate | predicate (every F2 artifact) | exemptions (named) | measured |
|---|---|---|---|
| G1 reverse | emitted reverse states ≤ 2 × today's + 1 | `[^c]{0,4}?$`, `[^c]{0,4}$` (4 → 11: today's run is scan-compacted) | 41 of 43 within |
| G2 forward, anchored | emitted states ≤ 2 × today's + 4, each machine | none | max 6 → 12 |
| G3 bytes | emitted size_bytes ≤ today's + (probe Δstates × today's per-state bytes per role) × 1.10 + 512 | none | owed at build |
| G4 identity | every F1 artifact: forward and anchored tables byte-identical to today's; F3/F4/F0 artifacts byte-identical to today's except F3's dropped tie code | none | — |

Floors (§R.4.0) are literal and re-counted.

#### §R.6.2 Independent controls and witnesses

1. **Oracle-first witnesses, green on today before the build** (`rev2corp`
   precedent): `tests/endmark/b3_rows.rxt`, one block per row and class:
   F1 (`\d+$`, `\B$` on `"a\n"` → (2,2), the startpos cells); F2 const0
   (`\s+$`), const1 (`\s*?$`), state-dependent (`(?:\s+|x\s*?)$`, `"x\n"` →
   (0,1), and under `-fno-anchored-dfa`: the relocate, S1's cell); S2
   (`(?:\Bx\n|x)$` on `"ax\n"`, `" x\n"`); S3 (`\n{1,4}$`, `\n\n?$`); S5
   (`ab\z|b\Z`, `\d+$|\w+\z`, `\s*$|x\z`); F3 (`(?:a|b\n)+$`, `a\n$`,
   `(?:\n\n|a){0,4}$`); F4 (a near-cap synthetic under a lowered-cap reference
   build); S8's held cases (`$` find-all on `"\n"`, `\s*?$` find-all,
   startpos > 0, `\Z` = `$`, `\z` unmarked, `(?m)$` never rev-end, a utf8
   block). Expectations from libpcre2 10.46.
2. **The tie fact and `mark_prio` against an independent construction**: a
   census check runs `b3rev_probe.c` (the PRODUCT of two untagged builds, and
   the closure over pcrec's NFA) and compares its row, tie fact and
   `mark_prio` with the build's `--emit-ir` lines on the whole population; the
   probe's `mark_prio` is itself checked against libpcre2's choice on every
   observed tie (b3meas's empirical method).
3. **The deny arm** in `make test-axes`: default vs `-fno-rev-end-onewalk`,
   answer identity over the corpus plus the give-up differential (D158).
4. **emit_sweep**: the mover manifest is exactly the F1 + F2 set (266 rows),
   and every other artifact is byte-identical (B3.1/B3.2), zero movers at B3.0.

### §R.7 The build: steps, sabotage, movers

#### §R.7.1 Steps

| step | content | movers / abi |
|---|---|---|
| E0 | `tests/endmark/b3_rows.rxt` (§R.6.2 item 1), green on today; the probe census check | none |
| B3.0 | the value compares (§R.3, four sites, an assertion that every non-F2 accept is 0/1); the `--emit-ir` summary row `rev-end-form` and the `--emit-facts` fact `end_mark`; the form table with only F0 reachable | zero (emit_sweep); spec: `ir_listing.md`, `facts_listing.md` |
| B3.1 | F1 `one-seed` in form W | the 223 F1 artifacts; abi event |
| B3.2 | `lower_eol` + ACC(d), the tagged construction, the tie fact, F2/F3/F4, `mark_prio` + FINISH `prio-const`, the optional builds, `drop-end-mark`, the deny (bit 55, `axes.def`) | the 43 F2 artifacts (+ F3/F4 where reachable); abi event; spec: `tuning.md` deny row, `limits.md` rung |

#### §R.7.2 Sabotage plan (C7): ten plants, ids to be issued by main

Each row's SAB_REACH reads the new `--emit-ir` summary row (`rev-end-form`,
`mark_prio`) or a stamp, never emitted-text greps.

| plant | what it does wrong | witness / detector | SAB_REACH |
|---|---|---|---|
| P1 | tags dropped: F2's accept value collapsed to truth | `\s*?$` on `" \n"` reports (0,2), PCRE2 (0,1) | `--emit-ir` `rev-end-form tagged` on `\s*?$` |
| P2 | `mark_prio` returns the second distance | `\s+$` / `\s*?$` nl cells | `mark_prio const0` on `\s+$` |
| P3 | F1 skips the zero-length probe at `n` | `\B$` on `"a\n"` → (2,2) lost | `rev-end-form one-seed` on `\B$` |
| P4 | `mark_prio` computed on the PRUNED machine | `(?:\s+\|x\s*?)$` reads const; `"x\n"` | `mark_prio state-dependent` |
| P5 | `mark_prio`'s cap overflow answers const | lowered-cap reference build, the sweep's `\s{0,N}$` | `mark_prio` line under the reference build |
| P6 | the hybrid consults the fact (VM ceiling below the reported end) | a captures witness, `(\s*?)$` on `"a \n"` | `RX_VM_PREFILTER` hybrid + `rev-end-form tagged` |
| P7 | D read class-blind (union over atoms) | `(?:\Bx\n\|x)$` on `"ax\n"` → (1,3), `" x\n"` → (1,2) | `rev-end-form tagged` on it |
| P8 | scan-edge compares accept truth (S3) | `\n{1,4}$` nl cells | `rev-end-form tagged` on `\n{1,4}$` |
| P9 | a lowered build overflow REFUSES instead of declining | the F4 witness under the reference build compiles today | `rev-end-form overflow` |
| P10 | F2's forward machine built without `lower_eol` (S1, the split) | `(?:\s+\|x\s*?)$` on `"x\n"` under `-fno-anchored-dfa` → (0,1) | `rev-end-form tagged` + `finish search-from` |

**Request: a range of 10 sabotage ids from main** (none invented here).

#### §R.7.3 Movers (C8)

The ten rows that grep `for (int revend_seed` (S758-S760, S767, S771-S773) or
`revend_seed` (S769, S778, S779) lose their reach on `\s+$` (now F2) and on the
hybrid witnesses (now F1). Each re-aim, intent re-verified against the row's own
header:

| row | intent | re-aimed at |
|---|---|---|
| S758 n−1 seed dropped | a match ending before a final newline is lost | F1's n−1 choice; its own detectors (`\d+$` on `"abc123\n"`, `a*$` on `"aa\n"`) are F1 artifacts; reach `rev-end-form one-seed` |
| S759 first accepting seed, not the smallest | smallest start over two seeds | F0 (`-fno-rev-end-onewalk` on `\s*$\|x\z`) and the F3 witness; reach `rev-end-form denied`/`two-seed` |
| S760 seed guard deleted | a seed below `startpos` walks | F1's guard (one guard per seed form); reach `one-seed` |
| S767 `nl_last` says no tie | a tie-capable artifact loses its tie handling | now: every artifact takes F1, so `\s+$`-family nl cells answer wrong; reach `rev-end-form tagged` on `\s+$` (the row the plant removes) |
| S769, S779 hybrid conjuncts | the hybrid's inlined body walks | reach `rev-end-form one-seed` on `(\d+)$` with `RX_VM_PREFILTER "hybrid"` |
| S771 deny unplumbed | `-fno-rev-end` inert | reach any `rev-end-form` row |
| S772 search-from ahead of verify-at | a tie relocates where the anchored machine exists | F0 on `\s+$` (today's tie) and F2 state-dependent `(?:\s+\|x\s*?)$` |
| S773 DFA_SCAN stamp forked | the stamp vs LOCATE's selection | reach any `rev-end-form` row |
| S778 superset span | `\w{1,2}(?:(?=)\|)$` (F1) | reach `rev-end-form one-seed` |

S765/S766 (endmark.md §5.3) re-aim to the F2 tag arm and FINISH's `prio-const`.
Plus: form-census floors, `DIFFER_PINS`, cpset manifests, FILEPINs,
`VARIANT_PINS`, the startset manifests, `tests/codegen/run_rev_end.sh`,
`run_dfa_stamps.sh`, `run_premul_table.sh` (the byte-count class is RUN, not
grepped: §5.3).

**abi readers by grep** of `PCREC_ARTIFACT_ABI` (76, `src/gen/emit_dfa.c:54`)
at `e8ca1252`: 17 files — `src/gen/emit_dfa.c`, `src/enc/CLAUDE.md`,
`tests/memfn/site_manifest.tsv`, `tests/mech/sabotages/S825_span_match_exported.sh`,
`tests/mech/sabotages/S693_abi_not_bumped.sh`, `tests/mech/CLAUDE.md`,
`tests/backrefs/run_backref_diff.sh`, `tests/backrefs/CLAUDE.md`,
`tests/backrefs/fold_agreement_check.c`, `..._utf8_check.c`, `..._ucp_check.c`,
`docs/spec/match_api.md`, `tests/codegen/run_codegen_tests.sh`,
`tests/codegen/run_encoding_checks.sh`, `tests/codegen/run_recursion_identity.sh`,
`tests/codegen/CLAUDE.md`, `scripts/emit_sweep.py`. The build re-greps at each
abi event (B3.1, B3.2) and runs the suites that count (registry, codegen,
rxtsource).

#### §R.7.4 `end_pin` has one answer (C8)

`end_pin` stays a TREE fact over the unlowered tree: `eol` for every `$`/`\Z`
artifact, on every form row. §2.3's "the pin is `z`" is withdrawn: with `$`'s
lowering an NFA-build parameter (§R.2), the tree never says `\z`. Its five
readers are unchanged; F2 reads `end_pin = eol` AND its own form row.

### §R.8 The sibling family (S10: one `EndDist` fact)

The match-end offset is encoded today as: `eolvar`/`endvar` views; the
forward `ACC(back)` (§2.2); the reverse tags (§R.1.2); ENDSET's `D`;
`EW_EOL_SLACK` (W1); `nl_last`; FINISH's tie rows. **Leaning: yes, B3 builds the
first reader of ONE representation, now**: the accept value as the distance set
(§R.3) on every machine, with today's machines as the {0} case. It costs B3
nothing extra (it is how F2 stores D) and it is what makes S3's fix structural.
And `mark_prio` is a FINISH row `prio-const` ahead of `verify-at`/`search-from`
(S10's own proposal), so the tie decision lives in one first-match table.

Not migrated now (D77), each with its trigger:

| member | stays because | trigger |
|---|---|---|
| `eolvar`/`endvar` views on non-F2 machines | addendum 3 (forward `$` keeps its view) | a measured cost of the view (`[REVBLOCK-VIEW]`'s ~1 ns/call is the first) |
| `EW_EOL_SLACK` | W1 reads widths, not ends | W1 on an F2 artifact |
| `nl_last` | F1's cheap predicate (no tagged build needed) | the tagged build becoming as cheap as the predicate |
| ENDSET `D` | FINISH's hand type, already a set | none: it already IS this representation |

Unlocks (with triggers): (A) a DFA door for `\K`: START_MARK, the same tagged
construction run forward (trigger: a bench cell VM-forced only by `\K`); (B)
newline conventions as tail data (§R.2.4; trigger: a NEWLINE request); (C)
rev-inner reports an end through a bounded tail with tags (trigger: the
rev-inner build); (D) E2's forward `ACC(b)` rides the same accept value, so the
VM → DFA trailing-lookahead set needs no `back` table either (trigger: E2);
(E) F1's last-byte rule generalizes to a CRLF tail by the last two bytes
(trigger: DD-11 CRLF).

### §R.9 Questions for Frank (discussion)

**Q1. A deny flag spends a bit.** 55 of 64 used; F0 makes it 56 (8 left;
`[IFACE-PUSH]`'s hard trigger is ≤ 4). The alternative is D164's own shape, a
harness-only lever with no bit. *Forces:* every other start/scan selection
row is deniable (D46, test-axes' answer identity runs on deny arms); the lever
is a lowering-pass control. *Leaning:* the deny flag, because F1/F2 are
selections, not a lowering.

**Q2. Selective tagging deletes nothing.** The two-seed walk stays as three rows
(F0/F3/F4). *Forces:* Frank's direction (tag only where it can tie) vs the first
design's "~40 lines deleted". *Leaning:* accept: the rows are data, and the
two-seed walk is the decline every optional build needs anyway.

**Q3. The VM keeps `$` as an assertion (§R.2.3).** A reading of addendum 4
(machines that answer the end from an automaton) for Frank to confirm.

**Q4. [REVBLOCK-VIEW].** The ~1 ns/call view probe also sits in every
composite's reverse pass. *Leaning:* file it (every ENG_UNANCH artifact moves),
B3 takes form W for its own walks only.

### §R.10 The standing questions (`docs/design/CLAUDE.md`)

1. **Measurement regime: relevant.** Counts: exact, pcrec's own builds at
   `e8ca1252`, gcc 15.2.0 on the Linux dev box, 13 controls. Clock: the Linux
   dev box (Ryzen 7 7700X), gcc 15.2 `-O2`, `taskset -c 2`, warm back-to-back
   calls over 2-24 subjects (latency of dependent calls), A/A per-cell p5-p95
   0.87-1.27, two runs agreeing. The SELECTION reads no timing (it is
   structural), so no regime can flip a row; the form decision (W) rests on a
   per-call ~1 ns constant consistent across L/K4/M1; a Zen 1 box (ubuntubudu)
   is unmeasured and the official verdict is the bench's (D144 add. 4).
2. **Independent control: relevant.** §R.6.2: libpcre2 10.46 on the ORIGINAL
   pattern for every witness; the probe's product of untagged builds against
   the build's direct tagged construction; `mark_prio` against libpcre2's
   observed tie choices; the deny arm. Populations counted by the probe (K35);
   every SAB_REACH reads an `--emit-ir` line on the witness the detector uses.
3. **What moves when data is regenerated: relevant only as emitted text.** No
   table or calibration: the tie fact, D and `mark_prio` are derived per compile.
   B3.1 and B3.2 are abi events (readers §R.7.3); spec hunks: `tuning.md` (the
   deny), `ir_listing.md` (`rev-end-form`, `mark_prio`), `facts_listing.md`
   (`end_mark`), `limits.md` (`drop-end-mark`).

---

## 0. Answers first

1. **The lowering is exact.** It fires where a POSITIVE lookahead ends its path, and
   `$`, `\Z` and `(?m)$` count as lookaheads (`(?=\n?\z)`, `(?=\n?\z)`, `(?=\n|\z)`).
   It replaces `X(?=Y)` with `X END_MARK Y`. libpcre2 10.46 was run on the original
   and on the lowered spelling, with an empty capture group `()` standing in for the
   mark. Both were compared at every start position of every subject over a
   4-letter alphabet up to length 5, plus find-all. The comparison covered group 0,
   every capture and the find-all sequence: **3,527 patterns, 28,237,887 cells, 0
   differences** (`endmark/results/diff_all_len5.txt`). Six deliberately wrong
   variants each go red (§1.5).
2. **Two consequences D164 did not name.** First, a capture that ENCLOSES the mark
   (`(\d+(?=px))`, `(foo$)`) must close at the mark, not after Y. A report-time rule
   handles it, and dropping that rule is one of the planted failures. Second, a
   negative lookahead never lowers: `(?!Y)` is not a concatenation.
3. **The forward DFA needs nothing new beyond an accept offset.** Each lowered
   path's accept node carries `back` = Y's consumed length. D3's accept-pruning
   (`src/ir/dfa.c`'s header) already picks the first accept in priority order, so
   the scan reports `pos − back`. Fixed-width Y needs no state splitting. Variable
   bounded Y splits by distance up to `maxw(Y)`. Unbounded Y keeps its lookahead,
   and the pattern stays on the VM as today. A priority-NFA twin over the lowered
   NFA agrees with libpcre2 on **120,304 / 120,304** cells (`endmark/twin.py`
   part A).
4. **The reverse walk is one walk from `n`, and the tie is not gone.** D164 says "no
   two seeds, no tags, no tie special case". The first holds. The other two are too
   strong. A reverse DFA cannot see priority, so when both ends (`n` and `n−1`) can
   be reached from the leftmost start, the pattern's priority must still choose.
   What the mark changes is that the tie becomes the GENERAL case of "a reverse
   accept carrying more than one mark distance", the reverse half of the forward
   mechanism, and stops being a `$`-specific two-seed special case. It is resolved
   by a static fact (`mark_prio`, §2.3) on every common shape, and by today's FINISH
   rows otherwise.
5. **B3, counted** (the twin is answer-checked against libpcre2; loads are subject
   bytes; k = 16,000):

   | cell | today | mark, `mark_prio` constant | mark, no fact (forward run on every possible tie) |
   |---|---|---|---|
   | `\s+$` on `Q·\t^k·\n` | 48,004 (3.00×) | **16,002 (1.00×)** | 32,003 (2.00×) |
   | `\s*?$` on `q·␠^k·\n` | 48,004 (3.00×) | **16,002 (1.00×)** | 32,003 (2.00×) |
   | `(?:\s+\|x\s*?)$` (priority depends on the state) | 48,005 (3.00×) | 32,004 (2.00×): FINISH | 32,004 (2.00×) |
   | `\d+$`, `[a-z]+\.txt$`, `\s+$` with no final `\n` | 1.00× | 1.00× | 1.00× |

   The twin's "today" reproduces compound.md §B.5's 48,007 measurement to 3 loads.
   G3's bound for the final-newline shape becomes **1.00× where `mark_prio` is
   constant** (true for `\s+$`, `\s*?$`, `[\s\w]*$` and the bench's
   `tail-space-eol`) and 2.00× where it is not.
6. **The census is small and concentrated** (§3; `endmark/results/census.txt`).
   - 2 bench and 22 corpus patterns go VM → DFA because the only thing forcing the
     VM was a bounded path-final lookahead. The bench pair is `syntax/lka-pos` and
     `lka-verb`: `item(?= done)`, the cell `ctx_prefilter_joint.md` found losing
     per-byte on the VM.
   - 4 corpus patterns gain an exact hybrid prefilter (captures keep them on the VM).
   - The rev-end `$`/`\Z` artifacts move: 9 bench and 257 corpus. Of those, 1 bench
     (`capability/tail-space-eol`, `\s+$`) and 42 corpus carry tie code today.
   - If `$` lowers on every consumer (§6, Q1), every path-final-`$` artifact moves:
     37 bench and 851 corpus, plus 54 path-final `(?m)$` DFA artifacts.
7. **It is one AST pass and one new node kind** (§4). `src/opt/endmark.c` runs after
   `pcrec_discharge_atomic` and before `pcrec_callgraph_build`, and it rewrites in
   place. The new node is `A_ENDMARK`, `\K`'s mirror. One invariant keeps it small:
   **everything inside the engine speaks CONSUMPTION, and only the report speaks the
   mark.** Group 0's caller-visible end does not change meaning, so no `match_api`
   hunk is needed. The changes are abi events, a `facts_listing`/`ir_listing` hunk,
   and one harness-only lever.

## 1. Semantics

### 1.1 What "ends its path" means

A node is in TAIL position when nothing consumes or asserts after it before the
match is accepted. The tail positions, as the walk that defines them:

- the root;
- the LAST element of a concatenation (trailing empty `(?:)` elements skipped);
- every arm of an alternation in a tail;
- the body of a capture or an atomic group in a tail;
- the body of a repeat in a tail **whose maximum is 1** (`?`, `??`, `?+`, `{0,1}`,
  `{1}`).

That is all. A repeat with max > 1 is NOT a tail for its body, because the body
re-enters at the mark, not after Y. This is the planted failure `through-rep`
(`(?:a(?=a))+`). A conditional's arms are declined (not walked) until a census
shows one. The tail walk is `endmark/tail_probe.c`'s `tail_walk`.

### 1.2 Why it is exact

PCRE2's `(?=Y)` is atomic and zero-width. At position `m` it succeeds iff Y matches
at `m`, its captures come from Y's first (priority) match, and the cursor returns to
`m`. Take `X(?=Y)` in tail position:

- **Same starts, same order.** Any start that has a match of `X(?=Y)` has a match
  of `X·Y` and the reverse. So the leftmost start is the same.
- **Same end.** At that start, backtracking enumerates X's candidate ends `m` in
  X's priority order. In the original, the first `m` where Y succeeds is the match,
  ending at `m`. In `X END_MARK Y` the same enumeration tries Y, as consumption, at
  each `m`, and the first success is the same `m`. The mark records `m`.
- **Same captures.** Inside Y, the first success in Y's priority order is the same
  match in both spellings. Captures in X were set by the same path.
- **The lookahead's atomicity is unobservable.** Atomicity would cut backtracking
  INTO Y when something after the lookahead failed, and in tail position nothing
  comes after. For the same reason, an atomic group or a possessive `?+` around a
  tail is transparent, and PCRE2's non-atomic `(?*Y)` lowers identically.
- **Alternation.** Each arm is tried independently, and an arm without a mark
  reports its consumed end (no mark was crossed, exactly as `\K`'s
  `PCREC_UNSET`).
- **Optional groups** (`(?:X(?=Y))?`, `??`): the group is entered once or skipped,
  with no re-entry.

`$` and `\Z` are exactly `(?=\n?\z)` (pcre2pattern). `X$` therefore lowers to
`X END_MARK \n? \z`. At a given `m`, the tail `\n?\z` succeeds in at most one way
(m = n, or m = n−1 with s[n−1] = '\n'), so the tail adds no priority of its own.
`(?m)$` is `(?=\n|\z)`. `\z` consumes nothing (rule L6 below). `\b` is not a
lookahead: it is two-sided and half of it is negative. It is already a context node
(`A_CTX`), and the mark leaves it alone.

### 1.3 The rule, as a first-match table

For a lookahead-like node `N` in tail position, with body Y: let
`Y' = plain(Y)` be Y with its own tail positive lookaheads replaced by their bodies
(no second mark: the first mark already set the end) and its tail `$`/`\Z`/`(?m)$`
replaced by their consuming bodies. Then:

| # | row | applies when | becomes |
|---|---|---|---|
| L1 | `negative` | `(?!`, `(?<!`, `(*nla:` … | unchanged (an assertion) |
| L2 | `behind` | a lookbehind | unchanged |
| L3 | `called` | N lies inside a group that is a subroutine-call target, or the root under `(?R)`/`(?0)`, or Y' contains a call | unchanged (a call site re-enters the body with another continuation; K93's lesson) |
| L4 | `unbounded` | `cwmax(Y')` unbounded | unchanged (the VM, as today; §2.2) |
| L5 | `ctx` | N was born `A_CTX` (one-character language, `src/parse/ctxnode.c`) | unchanged: answer-free, no movers |
| L6 | `zero-width` | `maxw(Y') = 0` (`\z`, `(?=)`, `(?=\b)`) | `Y'` alone (a mark would equal the consumed end) |
| L7 | `mark` | otherwise | `END_MARK · Y'` |

The rows are data (`start_table.md` §0a's rule), listable under `--list-axes` as a
sub-axis of the pass (the listing is not a deny surface: §5.4). L4 is a D77 choice.
Lowering an unbounded Y would buy only an exact hybrid prefilter, on 3 corpus
patterns (§3.1). The trigger to revisit it is a bench cell.

### 1.4 Captures that enclose the mark

`(\d+(?=px))` reports group 1 = `\d+`'s span. After lowering, the group's close is
reached AFTER Y. The rule: a capture that is an ANCESTOR of a lowered mark (static,
known when the pass runs) reports its end at the mark when the winning path crossed
a mark, and at its own close otherwise. It is applied at report time
(`<prefix>_report_captures`), with no change to how `vm_cap` writes. This is exact,
because tail position puts the capture's close after the mark on the same path. A
mark crossed outside the capture cannot occur: if the capture were in that mark's
Y, it would hold no mark node, since inner tails lower without one.
Captures INSIDE Y are set by ordinary consumption and need nothing (`a(?=(b)(c)?)`
in the families; PCRE2 sets them, §1.2).

### 1.5 The differential (`endmark/diff_lowering.py`)

Patterns are generated from a small AST, so each capture's identity is known in both
spellings:

- X: 17 shapes, greedy/lazy/possessive/atomic, alternations in both orders,
  captures inside;
- Y: 16 shapes, including alternations, captures, a nested positive and a negative
  lookahead, `$`, and `\n?\z`;
- 12 wrappers: plain, `(?*`, enclosing capture, `?`/`??`, alternation either side,
  a non-tail control, an atomic group, `\K` before, and a capture before the
  lookahead;
- an anchor family (`$ \Z (?m)$ \z` × 17 X × plain/capture/alternation, plus a
  mix);
- 21 curated cases (below);
- four UTF-8 patterns over `{a, é, b, \n}`.

The curated cases include find-all where the consumed context passes the next match
(`a(?=aa)` on `aaaa` must report `(0,1),(1,2)`), the empty match `(?=ab)`, `\K`
plus a mark, nested tails, captures inside alternating Y, enclosing captures across
arms, the greedy/lazy variable-Y pair `a+(?=a?b)` / `a+?(?=a?b)`, the tie
`q|a$|a\n$`, and the non-tail controls.

**Result: 3,527 patterns, 28,237,887 cells, 0 differences** (libpcre2 10.46; byte
subjects ≤ 5 over `{a,b,c,\n}`, UTF subjects ≤ 4 over `{a,é,b,\n}`, every start
position, find-all under `match_api.md` §3.1.3's protocol on REPORTED spans).

**The controls**, each a deliberately wrong variant (`endmark/results/diff_plants.txt`,
curated set):

| plant | what it does wrong | differences |
|---|---|---|
| `consumed-end` | reports the consumed end, not the mark | 54,054 |
| `no-close-at-mark` | drops §1.4's capture rule | 2,858 |
| `lower-negative` | lowers `(?!b)` like a positive | 23,090 |
| `lower-nontail` | lowers lookaheads that are not path-final | 4,904 |
| `through-rep` | treats a looping repeat as a tail | 296 |
| `findall-consumed` | resumes find-all at the consumed end | 2,476 |

## 2. Engines

### 2.1 The VM

`A_ENDMARK` is `vm_set(v, 1, "(ptrdiff_t)scan_position", …)`: `\K`'s arm with
slot 1 instead of slot 0 (`src/gen/emit_vm.c`'s `A_KRESET` case). It is trailed, it
is rewound by `<prefix>_unwind`, and it shows in the listing as a slot write. Slot 1
is group 0's end, reserved by `nstate`'s `2 * ncaps` and written by nothing today.
`<prefix>_report_captures` writes
`capture_spans[0][1] = slot_values[1] != PCREC_UNSET ? slot_values[1] : match_start + match_length`,
plus §1.4's ancestor list, on an artifact that has a mark. A mark-free artifact
keeps its text byte for byte, as `\K`'s `nkreset` predicate does. The anchored
entries return the REPORTED length.

**Give-up posture.** At a tail, `X·Y` does the same work as `X(?=Y)`: Y's
alternatives are tried until the first success, and on total failure the VM
backtracks into X. Frame use differs, though. The lookahead's sub-match pops its
frames on success, while consumed Y's choice points stay on the stack until accept.
So a FRAMES give-up can move at the capacity boundary. D158 asks for a give-up
differential across the lever (§5.5), not an argument.

### 2.2 The forward DFA

The NFA builder (`src/ir/nfa.c`) gives each lowered path its own accept node
`ACC(b)`, where `b` is Y′'s consumed BYTE length:

- **Fixed-width Y′** (`minw = maxw`, measured in bytes): one `ACC(L)` per distinct
  length. There is no state splitting, because a thread's distance to its accept
  is fixed by the node.
- **Variable bounded Y′:** Y′ is built as the product with a distance counter
  `0..maxw(Y′)`, so each length lands on its own `ACC(l)`. The bound comes from
  `maxw`. No constant is introduced: the product is charged to the existing
  NFA/DFA state caps, and overflow takes the existing `fit_rungs[]` path to the VM.
- **Unbounded Y′:** L4 keeps the lookahead.

**Priority among different ends uses the existing mechanism, unchanged.** It is
D3's priority subset construction with accept-pruning: "closure walks split edges
in preference order and stops the instant ACCEPT is reached — lower-priority threads
are pruned and the state is marked accepting" (`src/ir/dfa.c`'s header). An
accepting DFA state therefore carries the `b` of the first `ACC` reached in priority
order. The scan's last-accept rule records `pos − b[state]`, and a later accept from
a higher-priority thread overwrites it. This is leftmost-first exactly, because the
end is decided by which thread accepts, and that thread knows its distance. The
emitted change is one per-state `back` table beside the accept table, or a constant
when every accepting state has the same `b`. It is a new emitted table, so it is an
abi event.

Measured in the twin, the unanchored leftmost-first scan over the lowered NFA,
reporting `pos − d`, agrees with libpcre2 at every start position. The cases are
`\d+(?=px)`, `a+(?=a?b)`, `a+?(?=a?b)` (variable Y, both preferences), an
alternation with marks in some arms, `foo(?=bar|ba)`, `(?=ab)`, `[ab]*$` and
`[ab\n]*?$`. Result: **120,304 cells, 0 differences.** The plant `fwd-consumed-end`
gives 3,811.

**What reads the consumed end, unchanged.** These all speak consumption, which is
correct:

- the D7 reverse pass seeds at the forward scan's accept position. The reverse
  machine over the lowered language finds the leftmost start: any start that has a
  match has a consumed match, by the §1.2 argument;
- `[START-LANDING]`'s `end-minus-width` (start = consumed end − consumed width);
- W1's end window;
- the necessary byte/run pre-checks (Y's bytes become necessary, a free gain);
- the VM hybrid's window ceiling.

The hybrid's prefilter language becomes exact. The body records no
`NFA_ERASED_LOOK` for a lowered tail, so `pcrec_cand_lang_exact` holds and
`Vm.mrl_win` can arm. **Obligation:** the ceiling handed to the VM is the CONSUMED
end, never the reported one. A ceiling at the mark would starve Y and lose matches
(§5.6's sabotage row S-EM4).

### 2.3 The reverse walk (rev-end): this is B3

> **[b3rev] Superseded for the build by §R** (§R.1 the form table, §R.1.2 the tie
> fact per context atom, §R.2 one lowering per artifact by NFA-build parameter, so
> the `end_pin = z` reading below is withdrawn, §R.7.4). Kept as the first design.

After lowering, a path-final `$` reads `X END_MARK \n? \z`. The `end_pin` fact sees
`\z` at every path end and answers `z`. There is ONE seed, at `n`. The walk reads the
reversed lowered language: optionally the final `'\n'` (the tail), then the mark,
then X reversed.

**Why the tie does not disappear.** At the smallest accepting position `s*`, two
reverse paths may both have reached it. One has X consuming the final `'\n'` (mark
at `n`); the other has the tail consuming it (mark at `n−1`). Both are real matches
starting at `s*`. Leftmost-first priority chooses between them, and priority is a
forward property the reverse walk cannot see (`\s+$` → `n`, `\s*?$` → `n−1`,
compound.md's `lazy tie` cell). An untagged walk merges the two paths into one
subset state and loses which ends are possible. So the walk needs to know the
DISTANCE at which each reverse thread crossed the mark. That is the reverse half of
§2.2's mechanism: forward threads carry their distance from the mark to the accept,
and reverse threads carry their distance from the seed to the mark. It is general,
not `$`-specific. A bounded trailing context of length ≤ L gives distances
`0..L`, and `$` is L = 1. The reverse machine is built with prune off, as D7's
already is, and its accepting states carry the SET of distances that reach them. At
`s*`:

- **one distance `d`** → end = `n − d`. No forward pass.
- **several distances (a tie)** → the static fact `mark_prio`:
  - **constant `c`** (in every reachable situation where several distances accept,
    priority picks `c`) → end = `n − c`. No forward pass.
  - **otherwise** → FINISH's ENDSET rows as today: `verify-at` is one anchored run
    from `s*`, and `search-from` is the relocate.

**`mark_prio`, the fact.** It is computed at compile time by exploring the anchored
forward NFA closure lists of the lowered pattern WITHOUT pruning, each thread
carrying its mark distance. At the subject end (with `\z` true), it lists the
accepting distances in priority order. Wherever two or more distances appear, it
records the first. If one value is recorded, the fact is `const c`; if none, `none`
(no tie is possible); otherwise `state-dependent`. It is asked only when the built
reverse machine has an accepting state with two or more distances (the old
`nl_last`, generalized). Its exploration is charged to the existing DFA state cap,
and overflow answers `state-dependent`, the safe direction. Twin results
(`endmark/results/twin_k16000.txt`):

| X in `X$` | `mark_prio` | answers vs libpcre2 (today / tagged+fact / untagged+forward) |
|---|---|---|
| `\s+` | const 0 | 0 / 0 / 0 wrong of 4,005 random subjects |
| `\s*?` | const 1 | 0 / 0 / 0 |
| `\d+`, `[a-z]+\.txt` | none (no tie possible) | 0 / 0 / 0 |
| `a\|a\n` | const 1 | 0 / 0 / 0 |
| `a\n\|a` | const 0 | 0 / 0 / 0 |
| `\s+\|x\s*?` | **state-dependent** | 0 / 0 / 0 |
| `[\s\w]*` | const 0 | 0 / 0 / 0 |
| `a\n{0,2}?`, `a\n{0,2}` | const 1 / const 0 | 0 / 0 / 0 |

The controls (`endmark/results/twin_plants.txt`):

| plant | wrong answers |
|---|---|
| tags dropped | 36 to 383 per pattern, on 7 of 10 patterns |
| the fact flipped | 42 to 383 per pattern |
| the untagged walk skipping its forward run | 42 to 383 |

**Reverse machine size** (reachable subset states, twin part C):

| X | today `rev(X)` | mark, untagged | mark, tagged |
|---|---|---|---|
| `\s+` | 2 | 3 | 4 |
| `[a-z]+\.txt` | 6 | 7 | 12 |
| `\d+\.\d{1,3}` | 6 | 7 | 12 |
| `[a-z]+=[^\n]*` | 3 | 4 | 7 |

Tagging at most doubles the machine for L = 1. That is the price of one walk.

**When is a forward finish still needed?**

1. A tie whose priority is state-dependent (above).
2. Captures. The VM hybrid's stage 2 hands the VM `s*` with ceiling `n`, and the
   VM's own leftmost-first run sets the mark, so the hybrid needs neither the tags
   nor the fact.

**What is deleted.** The second seed, `revend_tie`'s bookkeeping, and the `eol ? 2 :
1` seed count in `emit_rev_end`. `PCREC_EPIN_EOL` loses every producer on a path
lowered by L7 (§4.3).

**Compound's G3.** compound.md §B.5's final-newline cells read 1.00× where
`mark_prio` is constant (both measured shapes) and 2.00× where it is
state-dependent. That is the bound B3's gate states for G3.

## 3. Census (`endmark/census.py`, `endmark/results/census.txt`)

The populations are `docs/dev/optloop/revend/census.py`'s builders, imported:

- the bench: 367 rows, 351 parsed, compiled as pcrec-auto does;
- the corpus: 5,645 rows, 5,236 parsed, with each block's encoding and `-i`.

The probe is `tail_probe.c`, which runs the real parser and the pre-selection
rewrites with captures requested. FACTS is `pcrec --emit-facts`. On the
VM → DFA set, the probe's verdict and the shipped engine stamp disagree **0 times**.

### 3.1 Path-final positive lookaheads (multi-character; one-character ones are `A_CTX` today)

| population | today → after the lowering | patterns |
|---|---|---|
| bench | **VM → DFA** (only a bounded tail lookahead forced the VM) | **2**: `syntax/lka-pos` `item(?= done)`, `syntax/lka-verb` `item(*pla: done)` |
| corpus | **VM → DFA** | **22** (`abc(?=def)`, `a(?=\n?\z)`, `z(?=ab\|cd)`, `z(?*abc)`, `z(?=a(?!b))`, …) |
| corpus | VM, captures: DFA under `--no-captures`; the hybrid prefilter becomes exact | 4 |
| corpus | VM, another VM-only construct (`(?<=`, `\1`) | 6 |
| corpus | VM, call-bearing (L3) | 1 |

Y widths: the bench pair is fixed at L = 5. The corpus has fixed L = 0..3 (22
patterns), variable L ≤ 2 (8) and unbounded (3, all already VM for another reason).
So the forward machine needs distance splitting on at most 8 corpus patterns, all
with L ≤ 2.

**Prediction for the bench pair.** `item(?= done)` moves from the VM to the DFA
route. The necessary run grows from `item` to `item done` (9 bytes), because Y is
now necessary consumption. The cells today read auto == forced-VM at 1.21 ns/B
(`ctx_prefilter_joint.md`). After the change they should read like the corpus's
other literal-run DFA patterns. That is a direction, not a number: the bench window
measures it.

### 3.2 `$` / `\Z` rev-end artifacts: the B3 movers

| population | rev-end artifacts with `end_pin = eol` | with tie code today | without |
|---|---|---|---|
| bench | **9** | 1 (`capability/tail-space-eol`, `\s+$`) | 8 |
| corpus | **257** | 42 (`[^c]{1,3}\Z`, `\s*?$`, `(?:a\|a\n)$`, `(\s+){2}$`, …) | 215 |

All 266 lose their second seed. The 43 with tie code are the ones whose cost
changes (3.00× → 1.00× or 2.00×). The other 223 cost the same, because seed `n−1`
died at once.

### 3.3 Every path-final `$`: the movers if `$` lowers on every consumer

| population | route today | patterns |
|---|---|---|
| bench | rev-end / attempt / VM | 9 / 27 / 1 |
| corpus | rev-end / attempt / VM / unanchored (`end_pin none`) | 257 / 298 / 296 / 22 |

In addition, path-final `(?m)$` appears on 2 bench and 52 corpus DFA artifacts and
14 corpus VM artifacts. Path-final negative lookaheads (which never lower) appear on
1 bench and 11 corpus patterns, all VM.

### 3.4 What could get worse

- **Forward `$` machines** (§3.3), only if Q1 picks the uniform form. The views
  (`eolvar`) become a mark accept with `back` 0/1. The state count should stay about
  the same: one "after the final `\n`" state replaces one EOL-variant state. This is
  unmeasured on pcrec itself, and it is E3's gate (§6).
- **VM frame use** on the roughly 30 corpus patterns whose tail lookahead becomes consumption (33 carry one; L3/L4 keep about 3)
  (§2.1): the give-up differential.
- **Compile time** of `mark_prio`: bounded by the DFA state cap, and asked only of
  tie-capable reverse machines (43 artifacts today).
- **No answer**, by §1.5.

## 4. Where it sits

### 4.1 The pass

`pcrec_endmark_lower(Ctx *, Ast *)` goes in a new `src/opt/endmark.c`, called from
`src/core/compile.c` **after `pcrec_discharge_atomic` and before
`pcrec_callgraph_build`**:

- **Before the call graph**, so that every fact the graph derives
  (lookaround-held calls joining TOP, K93) is derived from the final tree. L3 needs
  only the set of call targets, which is a scan of `A_CALL` nodes' `u.call.target`
  (and `(?R)`/`(?0)` for the root). It does not need the graph.
- **Before the E1 seal and `pcrec_select_engine`**, so that the kind mask, the
  widths and the engine choice all see the lowered tree. A lowered tail carries no
  `A_LOOK`, so `forces_registry`'s walk no longer finds its VM_ONLY stamp. No new
  `analyses[]` row is needed.

**In place, and never reallocating a group root** (`pcrec_lower_enc`'s discipline,
utf8s1 R2). The `A_LOOK` node is rewritten to `A_CAT(A_ENDMARK, body)`, so parent
pointers and `u.call.body` stay valid, and captures inside Y keep their identity.
The node's `reg` stamp is cleared.

### 4.2 The node

`A_ENDMARK` is a zero-width leaf with no payload. That puts it with `A_KRESET`'s
arms in the ~73 exhaustive-switch sites over 27 files that list `A_KRESET`, and the
`-Wswitch` alarm (mrl.c's rule) enumerates them. It is NOT a bare anchor for
`pcrec_is_bare_anchor`, because the user never writes it. Repeats never contain one,
since L7 only fires at max-1 tails. It is not repeatable by construction.

### 4.3 The facts it must update

The rule is the invariant in §0 item 7: facts speak consumption.

| fact | after the lowering |
|---|---|
| `end_pin` (`src/facts/endwin.c`) | **[b3rev §R.7.4: withdrawn; `end_pin` stays `eol`, `$`'s lowering is an NFA-build parameter]** a lowered `$` path ends in `\z`, so the pin is `z`. `PCREC_EPIN_EOL` keeps producers only where `$` did not lower (a mid-path `$` followed by `\z`). Its 5 readers are re-derived (§5.3). |
| `end_window` (W1) | consumed width = X's plus the tail's 1 = today's `EW_EOL_SLACK`. Same numbers. |
| `width` / `minw` / `nullable` / `empty_admits` | consumption. `(?=ab)` stops being nullable. That is right for every reader (the prefilter's nullable decline, the attempt bound), because the match cannot begin without reading `ab`. The reported span is empty, and only the caller's find-all reads that, from `caps`. |
| `kinds` (E1) | gains an `ENDMARK` bit. `LOOK` clears where every lookahead lowered. |
| `start_*` | unchanged. |
| the stamp offset `Ctx.first_vmonly_pos` | **a hazard, already live on main for the free atomic discharge (F4).** It is first-wins at parse time. If the first VM-only construct was a lowered lookahead and another remains, `RX_ENGINE_WHY` would point at a construct the tree no longer has. The fix is general: the stamp record becomes per node (an arena list of `(node, offset)`), and select_engine reads the offset of the node its walk found. That keeps "the `engine_why` text and its offset come from one place" (`mod_assertions.c`'s note). |

### 4.4 The sibling check

**The position-pin family** (compound.md's U3, D163's derivation hook) is
`start_anchor`, `end_pin`, `pin_split` and the startpos facts. After the lowering,
`end_pin` has two values that matter, `z` and `none`. That simplifies the family
rather than adding to it.

**The compound tool.** Q's derivation (P with `^`/`\A`/`\G` killed) runs on the
lowered tree, so Q's rev-end is the one-seed walk, and B4 (the compound driver)
inherits G3's 1.00×/2.00×. Captures on demand (compound.md §D,
`select-by-arg`) needs nothing new: the VM arm reports the mark (§2.1), and the
DFA arm reports `pos − back`.

**FINISH's ENDSET hand** survives, only for the state-dependent tie.
`locate_finish.md`'s `(I, e, D)` result keeps `D` = the end set. One-seed rev-end
hands `D = {n − d}` or `{n, n−1}`, so no type changes.

## 5. Interface and checks

### 5.1 Stamps and routes

No new stamp. These values move:

- `RX_ENGINE` and `RX_ENGINE_WHY` on the VM → DFA set;
- `RX_VM_PREFILTER_LANG` on the 4 captures cases (`exact`);
- `RX_REQ_RUN` (Y's bytes become necessary).

None of these adds vocabulary. `RX_DFA_SCAN "rev-end"` is unchanged. The mark is
visible in pcrec's own output, as D164 requires. In `--emit-ir`, the VM listing
shows the slot-1 write (`END_MARK`) and the DFA listing shows the back table. In
`--emit-facts`, a new pattern fact `end_mark` gives the count of lowered tails and
their `back` range, with owner `src/opt/endmark.c`.

### 5.2 abi and spec (D76/D94, D80)

**abi.** Each build step that moves emitted text is an abi event, with readers found
by grep (§5.3):

- E2: the VM's report text, the VM → DFA artifacts and the back table;
- E3: the rev-end walk, plus the forward `$` machines if Q1 picks the uniform form.

**Spec.** `match_api.md` needs no hunk: group 0's end is PCRE2's end before and
after, the find-all protocol reads `caps`, and the `_match` entries already return
"the match length". The spec hunks are:

- `facts_listing.md`: the `end_mark` row;
- `ir_listing.md`: the slot-1 write and the back table;
- `tuning.md`: one sentence that path-final lookaheads lower, so a route can change,
  with no axis row (§5.4).

The rows table (§1.3) is listed beside the `ctx-node` rows in
`src/dump/axes_dump.c`.

### 5.3 Readers by grep of the names that move

Found at `885eccff`. Each count is files / hits over `src tests scripts docs/spec`.

| name | files / hits | what happens |
|---|---|---|
| `revend_tie` | 4 / 18 | deleted; S765/S766 re-aimed at the tag-set arm |
| `revend_seed` | 15 / 23 | the loop goes; S758/S759/S760 re-aimed |
| `nl_last` (`revend_nl_last`) | 4 / 10 | becomes "an accepting reverse state carries ≥ 2 distances"; S767 re-aimed |
| `PCREC_EPIN_EOL` | 4 / 5 | re-derived (§4.3) |
| `CAND_HAND_ENDSET` | 4 / 17 | survives; its population shrinks |
| `report_captures` | 3 / 16 | gains the slot-1 arm (mark artifacts only) |
| `last_accept_position` | 15 / 64 | gains `− back[state]` where a back table exists |
| `emit_search_success` | 5 / 12 | reads the reported end |
| `NFA_ERASED_LOOK` | 6 / 6 | not set for a lowered tail |
| `pcrec_has_lookaround` | 12 / 20 | false where every lookahead lowered (`mrl_win` arms) |
| `first_vmonly_pos` | 8 / 13 | per-node (§4.3) |

`tests/codegen/run_rev_end.sh`, `run_dfa_stamps.sh` and `run_premul_table.sh` read
the rev-end text. The byte-count reader class must be run, not grepped:
`cpset`'s EMITTED_BYTES manifest, the resource rungs, the recursion-identity FILEPIN,
emit_sweep's pins, and the startset manifests (`k7980`/`revtri`/`sltri` precedent).

### 5.4 The lever (D163 addendum 2's shape)

There is no flags bit and no `-fno-…`. One internal, harness-only force-off
(`--harness=no-endmark` on `build/pcrec-harness`, which compound's B0 builds)
compiles today's tree: no pass, no mark. The artifact self-marks `"forced-off"` in
its facts listing. `make test-axes` runs it as a declared internal arm (answer
identity over the whole corpus), and bisects use it. This is the control that does
not share a source with the pass: the same compiler with the pass skipped.

### 5.5 Checks

1. **The libpcre2 differential, standing.** `tests/endmark/` runs §1.5's
   generators through pcrec, not through PCRE2 with `()`. It compiles each pattern
   (default, `--engine=vm`, `--no-captures`, `-e utf8`) and compares pcrec at every
   start position, plus find-all, against libpcre2 on the ORIGINAL pattern. The
   oracle reads the original pattern, the subject reads the lowered tree, and they
   share nothing.
2. **The lever arm.** Answer identity, and the give-up differential: the set of
   cells that give up must not grow in either direction (D158).
3. **Structural.** A `"rev-end"` artifact with `end_pin = z` emits one seed, the tag
   arm exactly when the reverse machine has a multi-distance accept, and no forward
   run when `mark_prio` is constant. A mark artifact's `report_captures` reads
   slot 1. The back table is present iff some accepting state has `b > 0`.
4. **Corpus witnesses** (`tests/endmark/*.rxt`, oracle-first, green on today's
   compiler before the build: the `rev2corp` precedent). These are the curated
   cells, the enclosing-capture cells, `a(?=aa)` find-all, the bench pair's
   shapes, `\s+$`/`\s*?$`/`(?:\s+|x\s*?)$` on final-newline subjects, and a UTF-8
   block.
5. **Census floors.** VM → DFA ≥ 2 bench and ≥ 20 corpus; rev-end-eol → one-seed
   ≥ 260. The floors are re-counted by the probe (K35), never copied.

### 5.6 Sabotage rows (ids NOT taken; **12 needed**; every row's witness is named, and its reach is proved by the witness file carrying the shape)

| row | plant | detector |
|---|---|---|
| S-EM1 | the report uses the consumed end | `tests/endmark` find-all + group 0 |
| S-EM2 | §1.4's ancestor list dropped | enclosing-capture cells |
| S-EM3 | L1 deleted (negatives lower) | `a(?!b)` cells |
| S-EM4 | the hybrid ceiling is the mark, not the consumed end | the 4 captures cases (match lost) |
| S-EM5 | the tail walk passes a max > 1 repeat | `(?:a(?=a))+` |
| S-EM6 | the tail walk passes a non-last CAT element | `a(?=b)b` |
| S-EM7 | `back` read as 0 | the bench pair |
| S-EM8 | tags merged in the reverse machine | `\s*?$` final-newline cells |
| S-EM9 | `mark_prio` returns the second accepting distance | `\s+$` / `\s*?$` |
| S-EM10 | `mark_prio` says `const` on a state-dependent shape | `(?:\s+|x\s*?)$` |
| S-EM11 | L3 deleted | a call-target tail (`(?(DEFINE)(?<n>a(?=bc)))x(?&n)`) |
| S-EM12 | the lever ignored | test-axes' internal arm reads movers where it must read none |

Re-aims: S758–S760 and S765–S767 (§5.3), plus S771 if the `-fno-rev-end` plumbing
moves. Their re-aim sites are derived by `scripts/sabotage_anchors.py --step` on
each commit's diff, not hand-listed.

## 6. Build plan

| step | content | movers / abi |
|---|---|---|
| **E0** | `tests/endmark/*.rxt` (oracle-first) and the probe promoted to a census check | none |
| **E1** | `A_ENDMARK` with every switch arm; the pass behind the lever, default OFF; VM slot 1, report and ancestor rule; NFA `ACC(b)`; the DFA back table | zero movers: emit_sweep, every stream and variant, against main |
| **E2** | the pass ON for L7 over `A_LOOK` (the multi-character lookaheads) | the VM → DFA set, about 30 corpus and 2 bench lowered programs, Y-run gains. abi event |
| **E3** | **[b3rev: replaced by §R.7.1's E0/B3.0-B3.2]** `$`/`\Z`/`(?m)$` lowered; rev-end's one tagged walk; `mark_prio`; the second seed and `revend_tie` deleted (B3) | 266 rev-end artifacts (Q1: plus the forward `$` machines). abi event. Gate: the forward state counts on §3.3's population do not grow by more than one per machine |
| **E4** | the per-node stamp offset (§4.3) | none if folded into E2 |

E2 and E3 are separable. E3 is what compound's B4 waits for.

## 7. Questions for Frank (discussion)

**Q1: should `$` lower on every consumer, or does the forward machine keep its
views?**

- *The problem.* `$` IS a lookahead (`(?=\n?\z)`), and the general rule lowers
  every path-final positive lookahead. Applied to `$` everywhere, the forward
  machines of about 890 corpus and bench artifacts move. Today they handle `$` with
  the `eolvar` view, and nothing measured says the view is slow.
- *The forces.* The house rule against parallel mechanisms says one rule, uniformly
  applied. D77 says not to move 890 artifacts without a measured gain. The views
  stay in any case, for mid-path `$`. Lowering only for the reverse walk would make
  `$` mean two things depending on which machine reads it. That is the quirky shape
  Frank's ruling rejected.
- *My leaning:* uniform, as E3's own abi event, gated on a state-count and size
  census of the moved forward machines that shows no growth. If the census shows
  growth, it is a finding to bring back, not a reason to special-case.
- *Room to disagree:* the reverse-only form is smaller and ships B3 sooner.

**Q2: should D164's "no tags, no tie special case" be amended?**

- *The problem.* §2.3 shows a reverse walk cannot see priority, so a tie must still
  be decided.
- *The forces.* Frank disliked revb3's tagged two-seed walk. The tags here are not a
  `$` fix. They are the mark's distance in the reverse direction, the same
  mechanism the forward machine uses for any bounded context, and the second seed
  is gone.
- *My leaning:* amend D164's consequence sentence to say "one seed; mark distances
  in the reverse machine; ties decided by the static priority fact or by FINISH",
  and keep the ruling's direction.

**Q3: should unbounded Y stay a lookahead (L4)?**

- *The problem.* Lowering unbounded Y gives the VM hybrid an exact prefilter. The
  DFA cannot carry an unbounded distance, so it would gain nothing there.
- *The forces.* Three corpus patterns, none bench. D77.
- *My leaning:* keep L4, and file the trigger: a bench cell with a path-final
  unbounded lookahead on a hybrid.

**Q4: should the lowered structure be visible beyond facts and IR?** D164 says
visible in pcrec's output only.

- *My leaning:* the `end_mark` fact and the IR listing, with no stamp until a
  consumer asks.

## 8. Standing questions (`docs/design/CLAUDE.md`)

1. **The measurement regime.** Relevant. Every number here is COUNTED or
   ORACLE-CHECKED; no clock was read:
   - subject-byte loads in a priority-NFA twin (exact by construction; "today"
     reproduces compound.md's measured 48,007 to 3 loads);
   - compile-side stamps on this box's build at `885eccff`;
   - libpcre2 10.46 on this box.

   The bench pair's improvement is a direction, owed to a bench window. No decision
   here would flip in a different timing regime, because none rests on timing.
2. **The independent control.** Relevant.
   - The lowering's exactness is checked against libpcre2 on the ORIGINAL pattern,
     with the mark spelled as a PCRE2 capture group. The expectation comes from
     PCRE2's lookahead semantics; the subject is the rewrite.
   - The twin's answers are checked against libpcre2 too.
   - Six plus four plants go red.
   - The census's probe is cross-checked against the shipped engine stamp (0
     disagreements on the VM → DFA set). The populations are counted by the probe,
     and the floors (§5.5) are re-counted, not copied (K35).
   - The build-time control is the lever: the same compiler with the pass skipped.
3. **What moves when data is regenerated.** Relevant only as emitted text. There is
   no data table or calibration. `mark_prio` and `back` are derived per compile
   from the pattern. The emitted bytes move at E2/E3 (abi events, readers in
   §5.3), and the spec hunks are in §5.2.

## 9. Findings

- **F1. D164's consequence sentence over-claims (§2.3).** One seed, yes. "No tags,
  no tie special case" cannot hold for a reverse walk, because priority is forward.
  What is true: the tie stops being a `$` special case and the second walk goes.
- **F2. Enclosing captures need a rule D164 did not state (§1.4).** Planted, it
  costs 2,858 cells.
- **F3. The hybrid ceiling must be the consumed end (§2.2).** This is the one place
  where reading the mark would lose matches.
- **F4. `Ctx.first_vmonly_pos` goes stale under any tree rewrite that removes a
  stamped node (§4.3), and it is ALREADY LIVE on main.** It is first-wins at parse
  time, and `Ast` carries no position. The free atomic discharge already removes a
  stamped node: `--features all 'a++b(?<=ab)'` stamps
  `RX_ENGINE_WHY "(\?<=...) at pattern offset 2"`. Offset 2 is the discharged
  possessive `+`; the lookbehind is at offset 4. The same text appears on
  `a++bc(?=de)x(?<=dex)` (lookbehind at 12). This is a stamp-value defect, not an
  answer defect, and it is worth a K entry. The per-node record in §4.3 fixes both
  the existing case and this pass's.
- **F5. The unlock is narrow (§3.1).** 2 bench and 22 corpus patterns. Most
  path-final lookaheads are one character, and those have been DFA since [UCP] U2's
  context node. The bench pair is the population that matters.
- **F6. `z(?=)` and `(?=\b)`-style tails are zero-width (L6).** They need no mark,
  and the empty lookahead disappears.
