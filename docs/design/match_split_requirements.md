# [MATCH-SPLIT] — requirements, costing, questions and the survey design (THINKING NOTE)

Lane `msthink` (2026-10-11, opus), from main `e3e78eab` (abi 74). **A requirements note,
not a design.** Nothing here is built, nothing is measured on a clock, no census was
run. The one kind of evidence taken is reading emitted code from single `build/pcrec`
compiles on main (`worktrees/msthink/build/ms/`, not committed). Plan row:
`docs/dev/plan.md` [MATCH-SPLIT] (Frank, session 108: "a general split match. Match
begin/match end/others?"). Frank's charge to this lane: "Before the match split count,
have a lane think about it. Get some requirements. Ask questions. Costing might be
tricky. Then do a survey." So §6 DESIGNS the survey (STEP 0's census) and does not run it.

Read §0 first. §1 is the problem with worked examples, §2 the requirements, §3 the
costing, §4 the family, §5 the questions for Frank, §6 the survey design and §7 the
standing questions.

## 0. Answers first

1. **Frank's wrapper strip is real, and today it costs a full pass on every call.**
   `^\s*\{|\}\s*$` compiles to `RX_DFA_SCAN "attempt"`, `start_max = subject_length`,
   prefilter/table/edge `none`: one anchored attempt **at every position** from
   `search_from` to `n`. A `s/…//g` over an `n`-byte string makes two or three
   `_search` calls (the `{` at 0, the `}` at the end, the final no-match call), and
   **each one walks the whole remaining subject**: about `2n` attempt entries in total.
   The ideal plan does no work between the first and last few bytes: one attempt at 0
   (and only while `search_from == 0`), then a reverse walk from `n` that stops at the
   first byte that is neither whitespace nor `}`. That is `O(prefix + suffix)` against
   `O(n)` per call.
2. **The trim idiom is worse than linear today.** `^\s+|\s+$` (and `(?m)^\s+|\s+$`) also
   take the attempt loop. Its `\s+$` arm, attempted at each position of an INTERNAL
   whitespace run of length `k`, walks to the end of the run before `$` fails. That is
   `O(k²)` per run: the shape of the 2016 Stack Overflow outage (`^[\s‌]+|[\s‌]+$`
   on a 20,000-space comment, as publicly reported). This is read from the emitted loop
   and not measured. It is a **complexity** defect, not a constant factor, and the split
   removes it: `\s+$` alone already gets `rev-end` today, so it is the mixture that
   costs. §6.4 counts the population; filing it as a K row is the manager's call.
3. **The general form is a locator that is a UNION over classes**, and the classes are
   defined on PATHS, not on syntactic branches. An absolute anchor (`^`, `\A`, `\G`,
   `$`, `\Z`, `\z`) anywhere on a path pins that path's start or end by position
   arithmetic. A line anchor (`(?m)^`, `(?m)$`) pins only at the path's leading or
   trailing position; anywhere else it is a landmark, not a pin. The FREE part is the
   machine with the pinning assertion edges deleted. That definition handles
   `(?:^a|b)c`, `(?:^|,)x`, `(^a)*b`, `(?:^)?ab` and dead anchors (`x(?:^|y)z`) with no
   syntactic special case (§2.2).
4. **Soundness is easy for pin classes and hard for landmark classes.** Each pin class
   has an exactly enumerable candidate set ({0}, {search_from}, {line starts}, the
   starts the reverse machine accepts from `n`/`n−1`). The leftmost match start is the
   minimum over the classes' leftmost starts, and FINISH with the FULL machine at that
   start preserves leftmost-first priority among arms. Per-branch LANDMARK classes
   (r1-rinner F2, line-end pins) inherit rev-inner's floor hazards, which Frank held as
   "a bit of a house of cards" on 2026-10-11. I recommend keeping them out of the row's
   scope (Q1).
5. **The costing is tricky for one reason above the others: the API is stateless.** An
   END-class reverse walk is repeated on every find-all call. When the free class
   produces many matches and the end walk does not die early (`x|a[^z]*b$` on `xxx…xb`),
   the split is QUADRATIC where today's unanchored scan is linear. Forward locators
   (start, `\G`, line-start, free) amortize across calls; the backward one does not. So
   the decision needs the end walk's expected length. That quantity is the
   `run_len`/`stay_len` term of [PRIOR-COST-UNIFY]'s proposed primitive, read over the
   reverse machine's stay set (§3.3). No constant is invented here.
6. **[MATCH-SPLIT] should be the general table.** Today's whole-pattern start rows are
   its single-class degenerate cases: `start_max = 0`, `\G`'s
   `start_max = search_from`, the `(?m)^` `memchr('\n')` skip (MLINE), `rev-end`,
   `end-window`, `rev-end-width`, and the unanchored scan. [OPT-ATTEMPT-SPLIT] is its
   START+FREE member, and [ENG-ABS-CARET] is the absorb alternative for that member
   only. In D156's frame it is ONE new LOCATE combinator (min over class sub-locators,
   handing `LOWER`/a point) over existing class rows. It needs no new result type (§4).
7. **What would make it worth building (D77)** is in §6.5. In short: the START+FREE
   member is already met (concat-sqli, measured ×3.51 by I-85 M5.b). The no-free-arm
   shapes (Frank's, trim) need a bench cell or a real-world population (bench wishlist
   item, §6.6). The quadratic class is a defect trigger on its own.

## 1. The problem in general terms

A pattern is a union of paths. Some paths can only match at a fixed position: at 0
(`^`), at `search_from` (`\G`), ending at `n` or `n−1` (`$`), or beginning at a line
start. Others can match anywhere. pcrec chooses ONE route for the whole pattern, so a
pattern that mixes them pays the free route's price on every path, or worse.

- **One `^` arm** forces `ENG_ATTEMPT` for the whole pattern. That route has no
  prefilter, no premultiplied table and no scan edge (`emit_dfa.c:13-17`: the reverse
  machine has no BOT variant, "so the slow shape is `^` on only SOME branches").
- **An end arm folded into the unanchored DFA** widens its first set, so the free arms
  lose their prefilter: `foo|\s+$` scans `{f} ∪ \s` with `byte-class-bounded` where
  `foo` alone is a `memchr('f')`.
- **When no arm is free**, the whole forward scan is gratuitous: Frank's example.

The best LOCATOR differs per class:

| class | where its matches lie | its cheapest locator today | per-call cost shape |
|---|---|---|---|
| START (`^`, `\A`) | start = 0 | one anchored attempt at 0 (`start_max = 0`) | `O(attempt)` if `search_from == 0`, else **zero** |
| SEARCH-START (`\G`) | start = `search_from` | one attempt at `search_from` | `O(attempt)` every call |
| LINE-START (`(?m)^` leading) | start ∈ {0} ∪ {i+1 : s[i]='\n', i+1 < n} | `memchr('\n')` skip + attempts (MLINE) | forward scan to the next candidate; amortizes |
| END (`$`, `\Z`, `\z`) | end ∈ {n} ∪ {n−1 if s[n−1]='\n'} (`\z`: n only) | reverse walk from `n`, `n−1` (`rev-end`); a window clamp when bounded (`end-window`) | the walk length, **every call** |
| LINE-END (`(?m)$` trailing) | end at each `'\n'` or `n` | none (a landmark class; locate_finish §7.2 G14(1), FILED) | a reverse walk per newline |
| FREE | anywhere | unanchored DFA + prefilter, or the hybrid's DFA in front of the VM | forward scan to the match; amortizes |

### 1.1 Worked examples (routes read from main `e3e78eab`, `--features all` where needed)

Each row gives the classes present, today's stamps and per-call cost shape, and the
ideal locator plan. "attempt, n" means `RX_DFA_SCAN "attempt"` with
`start_max = subject_length` and no prefilter.

| pattern | classes | today | per-call cost today | ideal plan |
|---|---|---|---|---|
| `^\s*\{\|\}\s*$` (Frank's wrapper strip) | START + END | dfa, attempt, n | O(n − search_from) attempts; under `s///g` about 2n in total | try 0 (only if `search_from = 0`); reverse walk from n over `\s`, `}`; no forward scan at all |
| `^\s+\|\s+$` (trim) | START + END | dfa, attempt, n | O(n) attempts, O(k²) on an internal whitespace run of length k | try 0; reverse walk over trailing `\s` |
| `(?m)^\s+\|\s+$` | LINE-START + LINE-END (under `(?m)` the `$` is a line end; corrected 2026-10-12, mssurvey) | dfa, attempt, n | as trim, plus a newline test per attempt | `memchr('\n')` line starts; reverse walk per newline |
| `^#\|//.*$` (comment strip, non-m) | START + END | dfa, attempt, n | O(n) | try 0; the end class: the reverse walk over `.*` runs the whole last line. Its START candidate is `//`'s position, so this end class is a LANDMARK in disguise (§3.2); a free `//` locator may be cheaper |
| `(?m)^#\|;\s*$` | LINE-START + LINE-END | dfa, attempt, n | O(n) | line-start class by `memchr('\n')`; the line-end arm is a landmark (`;`) and belongs to the free class in practice |
| `foo\|\s+$` (free + end) | FREE + END | dfa, unanchored, `byte-class-bounded` (first set `{f} ∪ \s`) | O(n), with stops at every whitespace byte | free `memchr('f')`, bounded by the end candidate; reverse walk from n |
| `ab\z\|cd` | FREE + END (fixed width) | dfa, unanchored, `byte-class-bounded`, `end-minus-width` | O(n) | free `memchr('c')`; END is `AT(n−2)`, one verify |
| `^GET \|POST` | START + FREE | dfa, attempt, n, `REQ_BYTE 'T'` | O(n) attempts behind a `memchr('T')` pre-check | try 0; free `POST` by memchr/memmem |
| `(?:^\|,)x` (CSV field) | START + FREE (distributed) | dfa, attempt, n, `REQ_BYTE 'x'` | O(n) | try 0; free `,x` by `memchr(',')` |
| `(?:^\|\s)foo(?:\s\|$)` | START + FREE + END, crossing | dfa, attempt, n, `REQ_BYTE 'f'` | O(n) | free `\sfoo` (`memchr('f')`, offset 1); the START path `^foo…`; the END paths share the free locator (their start is not pinned) |
| `\Gab\|cd` | SEARCH-START + FREE | dfa, attempt, n | O(n) | one attempt at `search_from`; free `memchr('c')` |
| `(?:^a)*b` | START + FREE (quantified) | dfa, attempt, n | O(n) | try 0; free `b` (the zero-iteration path) |
| `(?:^)?ab` | START ⊆ FREE (degenerate) | dfa, attempt, n | O(n) | the free part alone is the whole language: an unanchored `ab` with `memchr` |
| `x(?:^\|y)z` | dead START path | dfa, attempt, n | O(n) | the `^` path is unsatisfiable (x consumed before `^`); the free part is `xyz` |
| `wild-waf-crs-942360-concat-sqli` | START + FREE (`^` in one branch, lowest priority) | dfa, attempt, n; 8.42 ns/B (I-85) | O(n) | measured: split twin 2.40 ns/B (×3.51), object 0.92× by the exact twin (`fixes.md` cand 7) |
| `^(\s*)\{\|\}(\s*)$` (captures) | START + END | vm, hybrid, the hybrid's DFA on attempt, n | the attempt loop is the hybrid's prefilter: O(n) | the same locator; FINISH is the VM over the found start (stage-2 shape) |
| per-branch literals `abc\|xyz\|^q` | START + FREE | attempt | O(n) | free `byte-class {a,x}` (or two memchr); the per-branch LANDMARK split (`abc` vs `xyz` by memmem) is F2's unlock, out of scope (Q1) |

Two of these are worth naming as kinds rather than cases:

- **No free class** (Frank's, trim, `^#|//.*$` read strictly). The entire forward pass is
  unnecessary. This is the shape where the split changes the complexity class, not a
  constant.
- **The anchored arms widen the free prefilter** (`foo|\s+$`, `(?:^|,)x`, concat-sqli).
  Here the gain is the free class's own density. That density is the prior's `MASS` of
  the free part's first set against the whole pattern's: a [PRIOR-COST-UNIFY] quantity,
  and it can be zero (concat-sqli's free first set ⊇ the word class, so its post-split
  residual is per-step cost, `waf_attribution.md` §3.1).

## 2. Requirements

### 2.1 Semantics that must hold

Each requirement is stated with what discharges it. The standard throughout is answer
identity with today's artifact over the `match_api.md` §3.1.3 find-all loop, and
therefore with libpcre2 10.46 wherever today agrees.

- **R1 Leftmost across classes.** The returned start is the minimum over every class's
  leftmost start ≥ `search_from`. Each class locator must hand a LOWER BOUND on its
  class's leftmost start that never skips a true start (`locate_finish.md` §1.2 `LOWER`).
  An exact point (`e` set) lets FINISH skip a retry. A class whose candidate fails at
  FINISH is advanced past that candidate and the minimum is retaken (relocation with
  progress, `locate_finish.md` §2.3).
- **R2 Priority at the same start (ties).** FINISH runs the FULL pattern's anchored
  machine (or the VM over the full program) at the chosen start, never a class's
  sub-machine. A class sub-machine may decide only WHETHER a start is a candidate, never
  WHICH match is reported there. concat-sqli's exact twin used `a + u` legitimately only
  because its `^` arm is lowest priority and starts only at 0. The general row cannot
  rely on that, and FINISH-by-full-machine removes the need.
- **R3 Empty matches and the find-all advance.** The split changes no reported span, so
  the §3.1.3 loop (empty advance `next_pos(start)`, non-empty advance
  `next_pos(end − 1)`, the documented lossy class for empty-preferring patterns) reads
  identically. Nullable class arms must be witnessed: `^\s*` at 0, `\s*$` at `n`, `\s*$`
  at `n − 1` before a final newline, and an empty match at `n` after a non-empty match
  ending at `n`. NULLABLE-ANCH's `empty_admits` fact is the existing statement of which
  empty paths are pinned.
- **R4 `search_from > 0`.** START's class is EMPTY when `search_from > 0` (`^` anchors
  to absolute 0, §3.1¶7). SEARCH-START's single candidate is `search_from`.
  LINE-START's first candidate is `search_from` only if `s[search_from − 1] == '\n'`. The
  END walk is floored at `search_from` and takes the smallest accepting position ≥ it.
- **R5 `\G`.** A `\G` path's start is `search_from` by arithmetic: any bytes consumed
  before `\G` would put the start below `search_from`, which a search never does. Under
  find-all, `\G` means "contiguous with the previous match" (§3.1.3¶10), so the class
  costs one attempt per call.
- **R6 `(?m)` line pins.** LINE-START candidates follow PCRE2's rule: at 0 and after
  each `'\n'`, EXCEPT after a newline at the very end of the subject. pcrec's own
  lookaround definition `(?m)^ ≡ \A|(?<=\n)(?!\z)` already states this. A line anchor
  pins only at the path's leading (`^`) or trailing (`$`) position; elsewhere it is a
  landmark (§2.2). The NEWLINE convention is LF, per DD-11/D66; a later CRLF/ANY
  convention changes the line locator's byte set and nothing else.
- **R7 `$`/`\Z` before a final newline.** END has two seeds, `n` and `n − 1` (only when
  `s[n−1] == '\n'`); `\z` has one. A path that crosses `$` at `n − 1` may still consume
  the `'\n'`. Its end is in {n−1, n}; the start set is what the reverse walk computes.
  `rev-end`'s tie table (`nl_last`, FINISH's ENDSET hand) is the existing statement. The
  split reuses it rather than restating it.
- **R8 Context at a class's start.** A leading `\b`, `\B`, `(?m)^`, a lookbehind or
  `(?<=^)` at a candidate start reads `s[start − 1]` exactly as FINISH will (N1 of
  `assertions_design.md`: the reverse walk's termination boundary must read the byte
  before `search_from`). A class locator that cannot evaluate the context must hand a
  LOWER bound that admits the candidate, never one that rejects it.
- **R9 Captures.** With captures, FINISH is the VM over the found start (the hybrid
  finisher). The class locators run the capture-erased machines (D31). An END walk over
  an exact hybrid is REVEND stage 2's shape. Every slot write is FINISH's, so captures
  move with nothing else.
- **R10 utf8.** Every candidate is a character boundary. 0 and `search_from` are by
  contract. A position after `'\n'` is a boundary on any well-formed or ill-formed
  subject (a newline is never a continuation byte). The END walk's accepting positions
  must be lead positions, which `rev-end` already discharges (K49/K50 by construction).
  The free class keeps today's guards. `-futf-check` validates before any class runs.
- **R11 Give-ups (D158).** No budget may be charged more than today. The sufficient
  condition: **every position at which the split runs FINISH is a position today's
  route would attempt**, and FINISH at that position is today's attempt. Today's
  attempt loop tries every position ≥ `search_from` and stops at the first success. The
  split tries a SUBSET in increasing order and stops at the same success, so steps and
  frames are ≤ today's per call. Where today runs a hybrid whose exact DFA window hands
  the VM one start, the split must hand the same start ([GIVEUP-DIFF]'s direction check
  is the control). The `-fprefilter`/count-collapsed superset cases keep their existing
  declines.
- **R12 Answer identity under every deny.** A deny (`-fno-match-split`, name
  provisional) restores today's route byte for byte. Each class's own deny (`-fno-rev-end`,
  `-fno-end-window`, …) keeps working inside the split, because the class rows ARE those
  rows (§4).

### 2.2 What "an arm's class" means

A class is a property of PATHS through the automaton, not of the syntax.

- **Absolute pins are positional arithmetic.** A path through a `^`/`\A` assertion at
  offset `p` has `p = 0`, and everything it consumed before the assertion came from
  `[start, 0)`, so `start = 0` and the prefix is empty. A path through `\G` has
  `start = search_from` by the same argument with `search_from` in place of 0. A path
  through `$`/`\Z` at offset `p ∈ {n−1, n}` can consume at most the final `'\n'`
  afterwards, so its end is in `{n−1, n}` (`\z`: `n`). **So an absolute anchor ANYWHERE
  on a path pins it.** `a^b` and `x(?:^|y)z`'s `^` path are dead, and the analysis must
  report dead paths rather than classify them.
- **Line pins pin only at the edge.** `(?m)^` at the path's leading position (nothing
  consumed before it) pins the start to a line start. Anywhere else it pins a landmark
  (a `'\n'` at a varying offset from the start): rev-inner's territory, with its floor
  conditions (D151 addenda 5-7). The same holds for `(?m)$` at the trailing position.
- **The FREE part is the machine with every pinning edge deleted** (graph surgery on the
  NFA, not syntax).
  - `(?:^a|b)c` → START paths `^ac`, FREE `bc`.
  - `(?:^|,)x` → START `^x`, FREE `,x`.
  - `(^a)*b` → START (one or more `^a` iterations; the second is dead), FREE `b`.
  - `(?:^)?ab` → START `^ab`, FREE `ab`. The free language contains the start language,
    so the start class adds no candidate the free locator misses, and is redundant.
  - `^?` itself is refused by pcrec ("quantifier does not follow a repeatable item"),
    as PCRE2 refuses it. `(?:^)?` is the legal spelling.
  - `(?:a|$)b` → the `$b` path is dead; the free part is the whole live language. Today
    this is already `unanchored`.
- **Anchors inside lookarounds do not classify** unless proven. `(?<=^)a` pins like `^`
  (a lookbehind at position 0 asserts nothing before 0). `a(?=.*$)` does NOT pin the end:
  the lookahead asserts something about the subject, not about the match. The survey
  counts these separately (§6.2); the build treats them as FREE until a measured
  population says otherwise.
- **The analysis is a fact.** Per pin kind K it publishes: whether some live path passes
  K (`has_K`), whether every live path does (`must_K`), whether the K-deleted machine is
  non-empty (`free_live`), and the dead-path list. Owner: `src/facts/` beside
  `start_anchor`/`end_pin`/`empty_admits`, which become its single-class readers (`must`
  over one kind). This is "one owner per derivation" (PATFACTS); the whole-pattern facts
  are not re-derived.

## 3. Costing — why it is tricky, and what the decision needs

### 3.1 Why it is tricky

1. **The class locators cost different KINDS of work.** START is one attempt, ever.
   SEARCH-START is one attempt per call. LINE-START is a forward byte scan
   (`memchr('\n')`), proportional to the distance to the next line start. FREE is an
   unanchored DFA step per byte (or a prefilter's stop rate × an entry cost). END is a
   REVERSE DFA walk whose length depends on the data near `n`. These are not one unit, so
   there is no single per-byte number to compare against.
2. **The union is a min, so classes bound each other's work.** Forward locators can stop
   at the current best candidate. For example, with END's candidate `s_end` known, the
   free scan only covers `[search_from, s_end)`. The END walk cannot be bounded from
   below by a forward candidate: to learn whether a start below `f` exists, it must
   traverse `[f, n]` first. So **evaluation order is itself a cost decision**. END-first
   bounds the free scan; FREE-first never bounds the END walk. The right order is
   END-first exactly when the END walk is short, which is the same quantity as item 4.
3. **Find-all changes the economics, in opposite directions.**
   - START dies after the first call (`search_from > 0`).
   - SEARCH-START costs one attempt per call.
   - LINE-START and FREE amortize: across a whole find-all they scan the subject about
     once.
   - **END does not amortize under a stateless API.** Each call re-walks from `n`. The
     total is `m × E[walk]` for `m` calls. When the walk dies near `n` (`\s+$`, `}\s*$`)
     that is `m × (tail + 1)`, harmless. When it does not (`x|a[^z]*b$` on `xxx…xb`: the
     walk traverses all of `[search_from, n]` every call, and the free arm wins every
     call), the split is `O(n²)` where today's unanchored scan is `O(n)`. A caller-carried
     find-all state ([FINDALL-NEXT] under [IFACE-PUSH]) could cache the END result: one
     walk per find-all. That is an interface change and Frank's (Q2).
4. **The END walk length is data-dependent and only priced by a prior.** For a reverse
   machine whose live run near `n` is a class repeat (`\s+`, `[^/]*`, `.*`), the expected
   walk length is the expected run of that class's bytes. Under the byte prior that is
   `1/(1 − mass(stay set))`: `\s` ≈ short, `.` (on one long line) ≈ the whole line,
   `[^z]` ≈ the whole subject. This is the critic_family primitive's
   `run_len`/`stay_len` term exactly. The same term prices WORD-WAIT's stays (candidate
   6), so MATCH-SPLIT is a reader of that primitive, not a new one.
5. **The free class may dominate everything.** When the free part's first set is dense
   (concat-sqli: ⊇ the word class), removing the anchored arms buys the route change
   (attempt → unanchored, ×3.51 there) but no density gain. When today is ALREADY
   unanchored (`foo|\s+$`), the only gain is density, and if the end arm's first bytes
   are rare in the prior, removing them buys nothing.
6. **Short calls.** Every extra class adds a fixed per-call entry: a test of
   `search_from == 0`, a reverse-walk setup, one more machine's state. The gapreport's
   bucket A measured that kind of fixed term at ~2.5 ns/call, and SEL-COST's admission
   rule ("the sign must hold in every regime") applies. On a 20-byte subject the split
   can lose where on 1 MiB it wins 1000×.
7. **Size.** The split adds machines. concat-sqli measured 1.214× of the object by the
   row's construction and **0.920×** by the exact twin, because the anchored arm alone
   (`start_max = 0`) is smaller than the attempt artifact. Size is the [SIZE-KNEE] family's
   question, not a cost constant here.

### 3.2 When the split does NOT pay (stated, to be counted)

- **N1** Today's route is already the free class's own route, the anchored arms' first
  bytes are rare under the prior, and there is no START class (`foo|\d+$`: little
  density gain, a per-call END walk added).
- **N2** The END walk does not die near `n` AND the free class matches densely under
  find-all (the quadratic case, §3.1 item 3).
- **N3** An END class whose start is actually a landmark. `//.*$` non-m: every match
  ends at `n`, but its start is the last line's `//`, and the walk runs the whole last
  line. A free locator on `//` (bounded by nothing) may beat it. This is a PRIORITY of
  class locators per path, decided by cost (an END path may also be served by the FREE
  locator).
- **N4** Short-call regimes where the fixed entries exceed the saved scan.
- **N5** A size cap the extra machines push over (the ladder then drops the split row
  first: it is an optional contributor, the [K53-SELRETRY] shape).

### 3.3 What the cost decision needs as inputs (no hand-set constants)

The decision is a first-match row table (memory `pcrec-decisions-as-first-match-tables`)
whose rows read these facts and prices:

| input | source | exists? |
|---|---|---|
| class mix: `has_K`, `must_K`, `free_live`, dead paths | the §2.2 fact | NEW (a fact, `src/facts/`) |
| today's route and its consumer cost per byte / per entry | the route (`cand_route_of`) and PRIOR-COST-UNIFY's `PcrecConsumerCost{step_byte, stop_reentry, verify, attempt}` per route × program class | PROPOSED (critic_family F2/F6 signature) |
| the free part's first-set MASS vs the whole pattern's | `pcrec_find_set_ppm` / `pcrec_dfa_cand_ppm` on the free machine and on today's | EXISTS (applied to a new machine) |
| END walk expected length | the primitive's `run_len`/`stay_len` over the reverse machine's stay set near `n` | PROPOSED (same primitive; WORD-WAIT's `stay_len`) |
| LINE-START candidate rate | `'\n'`'s byte rate under the prior | EXISTS |
| bounded END width (window vs walk) | `end_window` / `end_pin` / fixed width | EXISTS |
| the regime | NOT a compile-time input. The admission must hold in every regime (SEL-COST §3), or the row is an [ADAPTIVE-ARM] (filed) whose initial state reads the primitive | rule EXISTS (`sel_cost.md` §3); arm filed |
| size of the extra machines | the emitted bytes, through the SIZE-KNEE family's decision (not a cost term) | family filed |

D146/D157: pcrec prices only its CONSUMER side here (attempt entries, re-entry, walk
steps) and states densities as facts. The scan FORMS inside each class locator (memchr,
pair, SWAR) are the kit's.

**The proposed decision shape** (for the design note, not ruled):

1. Members whose sign holds in every regime admit unconditionally. These are: no free
   class, where the forward scan disappears; and START/SEARCH-START + FREE where today is
   ATTEMPT, where the route change removes per-position attempt entries. Both reduce work
   at every subject length. The only exception is the fixed per-call term, which is
   measured once and is a consumer cost, not a knob.
2. END classes on routes where FREE matches can repeat admit only when the primitive
   says the walk is short, meaning an expected `run_len` below the free locator's own
   expected inter-match gap. That is a comparison of two primitive outputs; no constant
   is involved.
3. Pure-density members (today already unanchored) are priced by the mass comparison
   alone.

## 4. Relation to existing families (sibling-of-a-family lens)

Every shipped whole-pattern start mechanism is a SINGLE-CLASS case of the split:

| existing row | the class it serves | in the split |
|---|---|---|
| `start_max = 0` (fully `^`-anchored ATTEMPT; BOUND slot) | START only | START's locator row |
| `\G`'s `start_max = search_from` (DD-4) | SEARCH-START only | SEARCH-START's row |
| [OPT-ANCHOR-VM] (the VM attempt loop's start bound) | START on the VM route | START's VM-route row |
| MLINE (`(?m)^`'s `memchr('\n')` attempt skip, memfn M4) | LINE-START only | LINE-START's row |
| `rev-end` ([OPT-REVEND] L2 + stage 2) | END only, unbounded | END's walk row |
| `end-window` ([OPT-ENDWIN]) | END only, bounded | END's clamp row |
| `rev-end-width` / `end-minus-width` (K103 (b), rewtwin) | END only, fixed width | END's `AT(n−W)` row |
| unanchored DFA + `cand_rows[]` NEXT/FIRST/RETRY, the hybrid prefilter, the re-entered handoff ([REQ-HANDOFF-L1]), START-LANDING's RECOVER rows | FREE only | FREE's composite, unchanged |
| [NULLABLE-ANCH]'s `empty_admits` | the empty paths of START/END | the fact's nullable half |
| [OPT-ATTEMPT-SPLIT] | START + FREE | the first two-class member |
| [ENG-ABS-CARET] (BOT variant, absorb `^` into ENG_UNANCH) | START + FREE | the ABSORB alternative for that member only; it cannot serve END (an END arm still forces a full forward scan), so it does not generalize |
| r1-rinner F2 / rev-inner per-branch landmarks; locate_finish §7.2 (`(?m)$` seed-set walk) | LANDMARK classes | out of scope (Q1); the split's interface admits them later as more class rows |

So **yes: [MATCH-SPLIT] should be the general table, and these become its rows**, with
today's single-class selections as its degenerate case (one class present → today's row,
byte-identical). In D156's frame:

- **A new LOCATE combinator `split`.** Its payload is the list of present classes, each
  holding a class sub-locator chosen by first-match over that class's rows. It hands
  `LOWER` (or a point with `e` when the winning class's locator is exact) to FINISH
  `verify-at`, with relocation on a failed candidate.
- **The result type.** The min of `LOWER`s is a `LOWER`, and the min of exact points is
  an exact point, so D156's "revisit when a locator's output is not expressible" is not
  triggered.
- **Path derivation.** The path's `.needs` gains the free machine (and its reverse, or a
  START-LANDING RECOVER row).
- **Stamps.** The stamps follow from the path (D156 addendum 2): the locator is named
  once, from the path.
- **The start table.** `cand_rows[]` gets one LOCATE row plus per-class sub-row sets, and
  the class sub-rows are the existing rows re-keyed by class instead of by whole-pattern
  route.

**Remodel overlap** (memory `pcrec-remodel-first`). The LOCATE slot and path derivation
are lfl0's, shipped. The class sub-row re-keying touches `cand_rows[]`, `pf_admits[]`
(the hybrid admission) and FINISH. [PRIOR-COST-UNIFY] is QUEUED and MATCH-SPLIT's cost
rows read it. That is why the plan row already says "not scheduled ahead of
[PRIOR-COST-UNIFY]", and this note agrees.

## 5. Questions for Frank

Each question gives my leaning and the forces behind it, as discussion. Choices that are
answer-free or follow from rulings are mine; they are listed after the questions and are
not asked.

**Q1. Scope: pin classes only, or landmark classes too?**
Pin classes (absolute anchors anywhere on a path; line anchors at the path's edge) have
exactly enumerable candidates, and their soundness is arithmetic. Landmark classes
(per-branch literals, F2; `(?m)$` mid-path; `//.*$`'s start) need rev-inner's floor and
composition gates, which took three review rounds and are now HELD. My leaning: the row
covers pin classes, and its interface admits landmark classes as later rows, each gated
on its own rev-inner-style soundness argument and its own trigger. The force against
this: concat-sqli's residual and dbnames are free-class problems either way, so the
landmark half buys little that FIRSTSET/handoff do not.

**Q2. Find-all's END re-walk: admission predicate now, or caller-carried state later?**
Under a stateless `_search`, the END walk repeats per call. My leaning: admit END
classes only where the prior says the walk is short (§3.3 item 2). That keeps the API
untouched and covers trim/strip/`\s+$`, the shapes that motivate the row. I would also
record [FINDALL-NEXT] as the place a cached END result could live once [IFACE-PUSH]
opens, rather than a per-artifact static (which would break §5.3 reentrancy). The force
the other way: substitution (`s///g`), the motivating use, is exactly the find-all
regime, and a cached result would make END free on every call after the first.

**Q3. The quadratic trim class: a defect (K row) now, or only a member of this row?**
`^\s+|\s+$` on the ATTEMPT route is `O(k²)` on an internal whitespace run. That is a
complexity property, which pcrec's DFA routes otherwise do not have. pcre2 shares it, as
the outage shows, but RE2/rust do not. My leaning: file it as a K row with the census
count (§6.4), and let [MATCH-SPLIT] be its fix, so it is visible on the known-issues list
whatever the row's scheduling. If he prefers, it can stay a motivating fact inside this
row.

**Q4. Order: the START+FREE member first (concat-sqli, measured), or the general
combinator first?**
[OPT-ATTEMPT-SPLIT] is ratified, measured and subsumed. Building it alone as a one-off
would be the parallel mechanism the house avoids. Building the combinator with only that
member live is implement-then-replace (allowed): the general shape, one class pair
enabled. My leaning: the general combinator with START+FREE as its first enabled pair,
then END, then LINE-START, each gated on its own count. This inherits fixes.md Q2
(default vs `--tune` for the size) unchanged; I am not re-asking it.

**Q5. Is a bench cell needed for the no-free-arm shapes, or is a real-world idiom census
enough?**
The REVEND precedent required a bench cell. Frank's strip and the trim idiom are
"everyone writes these" patterns, but the bench's `wild-*` validators are `^…$`
whole-subject idioms and nothing on the bench substitutes over a long string. My leaning:
ask the bench for a wishlist family `anc-wrap` (strip/trim/comment-strip under find-all,
plus long internal whitespace runs for the quadratic case, §6.6), and let the D77
trigger be that family's cells. The force the other way: the quadratic case is a defect
and does not need a bench cell to justify a fix.

**Choices I make myself (answer-free or following from rulings):**

- The class definition by paths and graph surgery, not by syntax.
- The fact's owner (`src/facts/`, the whole-pattern facts becoming its readers).
- FINISH always by the full machine (R2).
- The candidate merge as a min with relocation.
- The END/FREE evaluation order chosen by the primitive (§3.1 item 2).
- The provisional deny name.
- The survey's instrument and taxonomy (§6).
- Treating `(?:^)?`-redundant START classes as dropped.
- Leaving anchors inside lookarounds unclassified until counted.

### 5.1 Frank's rulings (2026-10-11, session 108)

- **Q1 RULED: pin classes only for now.** Landmark classes stay later rows behind their own soundness argument and trigger.
- **Q2 ANSWERED by Frank's find-all walk-through, sharpened by the manager.** On a pattern with NO free class (trim `^\s+|\s+$`, the wrapper strip), find-all needs no state: call 1 runs the START class at 0 and returns; call 2 arrives with `search_from > 0`, the START class is dead by arithmetic (no `\G`, no line pin), so only the END class remains and its reverse walk runs once from n and stops where the reverse END machine dies (the trailing run, not n); call 3 starts at n and ends. At most a few calls, each linear in what it consumes: K106's fix needs no API change and no admission predicate. The repeated-END-walk cost of §3 exists only when a FREE class is also present: every free match before the end can make the next call re-walk the same suffix. For those mixed patterns: run the free locator first, and consult END only when its earliest possible start lies before the free candidate (bounded end arm: start >= n - max width, a cheap test); an UNBOUNDED end arm (`[^\n]*$`) is admitted only when the expected suffix walk (`stay_len` under the prior) is short. The caller-carried cache stays a candidate for [IFACE-PUSH], not needed for the pin-only first build.
- **Zero-width START arm (Frank's question, `^|end$`).** No new hazard, and a REQUIRED witness. (a) On `"end"` both classes have a candidate at 0 (START's empty `^`, END's `end$` from the reverse walk); the split must hand position 0 to the FULL machine, whose priority returns `(0,0)` — never the END class's own match. (b) The NOTEMPTY retry: python `re` (and PCRE2 `/g`) list `(0,0),(0,3)`; pcrec's caller loop cannot express the retry and lists `(0,0)` only (match_api.md §3.1.3, pre-existing, unchanged by the split); the emitted substitution loop (replace_design.md §3.8) does the retry, and there the finish at 0 under "empty not permitted" must fall through to the END candidate at 0, which it does because the finisher, not the locator, applies the restriction. (c) `^|$` and `$`'s two seeds (n-1 before a final newline, and n): the END walk reports the smallest accepting start >= `search_from`, so find-all meets n-1 then n. (d) utf8: the empty-match advance is one character. Witness cells: `^|end$` on `end`, `xend`, `x`, `end\n`; `^|$` on `""`, `a`, `a\n`.
- **Build order (manager):** pin-only patterns first (START + END with no free class: K106, the wrapper strip), then START + FREE (concat-sqli), then END + FREE behind the admission above.

## 6. The survey design (STEP 0; designed here, NOT run)

### 6.1 Populations, reported separately (K35: every denominator printed)

1. **Bench**: every `bench/*/patterns/*.rx` in pcrec-bench (read-only), compiled the way
   the `pcrec-auto` testee compiles it (`--features all`; `-e utf8` on the `utf8` set).
   Reuse `docs/dev/optloop/revend/census.py`'s population builder.
2. **Corpus**: every `pattern` block of every shipped `.rxt` (`pcrec --list-source`),
   with each block's own encoding/flags.
   - Report the D27/adversarial files separately. `composition_d27.rxt` alone has
     skewed earlier censuses (the lookaround census's matrix file was 58%).
   - The corpus is correctness witnesses, not usage (the wordfold lesson: the corpus
     alone would have parked that row).
3. **Realistic catalog**: `docs/design/eng_brep_measurements/probes/realistic_patterns.txt`
   (40 hand-written), extended with a stated list of real-world idioms: trim, wrapper
   strip, comment strip, CSV field `(?:^|,)`, word-boundary-or-edge
   `(?:^|\s)…(?:\s|$)`, `\G` tokenizers, line-oriented `(?m)` filters, OWASP CRS rules
   with `^` in a branch. The list goes in the survey's output, so it is reviewable.
4. **Denominators**: compiled, refused (by reason), and each encoding, per population.

### 6.2 The class-mix taxonomy (per pattern)

From the §2.2 analysis, computed by a probe linking `libpcrec.a` (the `revend_probe.c`
pattern: a copy of the walk, cross-checked against the shipped facts):

- the present pin classes: S (`^`/`\A`), G (`\G`), LS (`(?m)^` leading), E
  (`$`/`\Z`/`\z`), LE (`(?m)$` trailing), F (free part live);
- the mix label: the set of present classes, e.g. `S+E` (Frank's), `S+F` (concat-sqli),
  `E+F`, `LS+F`, `LS+LE`, `S+E+F`, `G+F`;
- flags:
  - dead anchored paths;
  - a redundant START (free ⊇ start language, decidable on the two machines);
  - anchors inside lookarounds (unclassified);
  - nullable class parts;
  - an END class whose walk crosses an unbounded leading repeat (the quadratic-risk
    flag, §6.4);
  - captures (the VM hat);
- single-class patterns (S-only, E-only, LS-only, F-only, G-only) as the CONTROL
  population (§6.7).

### 6.3 Today's route and the prospective plan, per pattern (compile-only)

- **Today:** `RX_ENGINE`, `RX_DFA_SCAN`, the emitted `start_max` (0 / `search_from` /
  `subject_length`), `RX_DFA_PREFILTER`, `RX_VM_PREFILTER`, `RX_DFA_START`,
  `RX_END_WINDOW`, `RX_REQ_BYTE`/`RX_REQ_RUN`/`RX_REQ_WHY`. Read from the stamps, never
  from emitted comments.
- **The free part:** surgically derived (§2.2) and compiled on its own. Read its route
  and prefilter stamps and the first-set mass via `--emit-facts`. This answers "does the
  split narrow the prefilter?" without a clock.
- **The END part:** whether `rev-end`/`end-window`/fixed width would apply to the END
  sub-machine alone (its `end_pin`/`end_window` facts).

### 6.4 The counts that matter

- **(a)** Patterns per mix label, per population, and per today-route
  (`attempt,n` / `unanchored` / hybrid / VM-only).
- **(b)** The no-free-arm population (`S+E`, `LS+E`, `S+LE`, …), Frank's shape.
- **(c)** The ATTEMPT-with-`start_max = n` population split by mix. This is
  [OPT-ATTEMPT-SPLIT]'s own precondition (D81's 180-of-995 was never split by
  `start_max`). It discharges that row's owed count too.
- **(d)** The quadratic-risk population: an END arm on the ATTEMPT route whose leading
  element is an unbounded repeat of a class (`\s+$`, `[^/]+$` inside a mixed pattern).
  For each, the counted work on a constructed subject (an internal run of k bytes, k ∈
  {1k, 4k, 16k}) as attempt entries and DFA steps from an instrumented artifact. That is
  a work count, not a timing. It confirms or refutes §0 item 2.
- **(e)** The density gain: today's first-set mass vs the free part's, per pattern.
- **(f)** The "gratuitous bytes" per BENCH cell, using walk_survey's per-phase load
  instrument on today's artifact against the ideal plan's predicted loads (start: the
  attempt length; END: the walk to death; free: today's free scan bounded by the min).
  This gives a counted upper bound on each cell's win, weighted by the cell's measured
  ns, in walk_survey's units, so it is comparable with its K-classes.
- **(g)** The N1-N4 decline population (§3.2), per the predicates available without the
  primitive. Each row is marked "needs the primitive" where it does.

### 6.5 What would make the row worth building (D77 trigger, stated before the count)

- **START+FREE:** MET already (concat-sqli 28.9 ms, ×3.51 measured). The count (c) sizes
  it. A population at or near "the witness plus a handful" keeps it as fixes.md
  candidate 7's single-witness case under Q4's general shape.
- **No-free-arm** (`S+E` and kin): a bench cell from the wishlist family (§6.6) showing a
  long-subject find-all at rank, OR a realistic-catalog population of at least the
  idioms named in §6.1, judged by Frank (Q5).
- **Quadratic risk:** any non-zero (d) with superlinear counted work is a defect trigger
  on its own (Q3).
- **END+FREE density:** a bench cell where (e) shows a material mass reduction AND the
  cell trails; otherwise filed.
- **Landmark classes:** none (out of scope, Q1).

### 6.6 Bench wishlist entry (for `docs/dev/bench_wishlist.md`, the manager's to add)

The family is `anc-wrap`, with `s///g`-shaped find-all over 1 KiB / 64 KiB / 1 MiB
subjects:

- patterns: `^\s*\{|\}\s*$`, `^\s+|\s+$`, `(?m)^\s+|\s+$`, `^#|//.*$`, `(?:^|,)x`-style
  CSV, `(?:^|\s)word(?:\s|$)`;
- subjects:
  - a wrapped string;
  - plain text;
  - text with one long internal whitespace run (the quadratic witness);
  - a whitespace-only subject;
  - a no-match subject.

Peers: RE2/rust (linear) and jit (backtracking, which shares the quadratic class).

### 6.7 The instrument's controls

- **C1 single-class agreement (plumbing).** On the single-class control population the
  probe's classes must agree with the shipped facts and stamps: S-only ↔ `start_max = 0`
  / `start_anchor`; E-only ↔ `end_pin`/`end_window`/`rev-end`; LS-only ↔ the MLINE skip;
  G-only ↔ `start_max = search_from`. Report disagreements, never hide them. This shares
  a source with the facts, so it checks plumbing only (C4's lesson in locate_finish §2.1).
- **C2 independent soundness (libpcre2 10.46).** For every pattern the probe classifies
  with NO free part, run libpcre2's find-all over sampled subjects (bench texts plus
  constructed edge subjects: final `'\n'`, empty, whitespace-only). Check that every
  reported start is 0, `search_from` (`\G`), a line start, or a start whose match ends in
  `{n−1, n}`, as the class list predicts. A violation means the classifier is wrong. This
  shares no source with pcrec's analysis.
- **C3 free-part identity.** The free part compiled alone must, on sampled subjects,
  report a subset of the full pattern's match STARTS (never a start the full pattern
  lacks). libpcre2 is the oracle for both.
- **C4 planted classes.** A fixture list with one constructed witness per mix label and
  per §2.2 case (`(?:^a|b)c`, `(?:^|,)x`, `(^a)*b`, `(?:^)?ab`, `x(?:^|y)z`,
  `(?<=^)a`, `a(?=.*$)`, `(?m)^…|…$`, a `\G` arm). Each must land in its predicted
  class, and two plants must fail loudly:
  - deleting the line-anchor edge rule;
  - treating a lookahead `$` as an END pin.
- **C5 reach.** Every mix label in the taxonomy has a population or a stated UNREACHED
  argument ([MECH-REACH]). An empty label is reported as empty, not omitted.
- **C6 the `-o` basename trap.** Every compile pair compared byte-wise uses the same
  `-o` basename. This is the house's recorded trap, four instances so far.

## 7. Standing questions (`docs/design/CLAUDE.md`)

1. **Measurement regime — RELEVANT.** The only number this note cites is concat-sqli's
   (I-85, Linux, throughput regime, `t-1m`, at an older pin; fixes.md's 25 ms is DERIVED
   from it). The costing argument (§3) is that the regime FLIPS the END-class decision:
   find-all density × walk length. So every future number must carry its regime
   (throughput vs search-short vs match, single call vs find-all) and box, and the
   admission rule must hold in every regime or be adaptive.
2. **Independent control — RELEVANT.** The survey's C2/C3 use libpcre2 10.46 and share no
   source with pcrec's analysis. C1 shares a source and is labelled plumbing only. For
   the eventual build: answer identity against today's artifact and libpcre2 over the
   find-all loop, a give-up differential (R11), and a deny-identity sweep (R12).
3. **What moves when data is regenerated — RELEVANT later, not for this note.** The cost
   rows read the byte prior. Regenerating the findings bundle moves the END-class
   admission and the density comparison, and therefore emitted artifacts: an abi event
   by D76/D94 at that time. This note writes no data file. The survey's outputs are
   evidence only; no check reads them.

## 8. Findings (for the manager)

- **F1** The trim class is quadratic on the ATTEMPT route (§0 item 2): read from the
  emitted loop, not measured. §6.4 (d) counts and confirms it. Q3 asks whether to file
  it as a K row.
- **F2** `(?:^)?ab` (a redundant `^`) and `x(?:^|y)z` (a dead `^`) both pay the full
  attempt loop today with no prefilter, though each is equivalent to a pattern pcrec
  serves with `memchr`. They are a cheap degenerate member: the fact's
  redundant/dead-path flags alone move them to the free route.
- **F3** `^(?:a|b$)` correctly gets `start_max = 0`, so the `must` analysis already
  exists for whole-pattern `^`. The new fact generalizes it to `has`/`must`/`free_live`
  per kind. It is not a parallel derivation.

- **Survey run (STEP 0, lane mssurvey, 2026-10-12):** see `docs/dev/lanes/mssurvey_report.md` (counts, trigger verdict, controls); instruments and outputs in `docs/dev/optloop/matchsplit/`.
