# `[OPT-REVEND]` — reverse-from-end search for end-pinned patterns

**Lane `revdes`, 2026-10-09. DESIGN + HAND-TWIN; nothing under `src/` is built.**
Code citations are at main `de6acf09` (abi 70). Charter inputs: the plan row
(`docs/dev/plan.md:342`); the census (`docs/dev/optloop/revend_census.md`). Its
"zero start-unanchored unbounded bench cells" was read at capability@0.1 and is
SUPERSEDED: the trigger fired at capability@0.2 (bench O-91 (c), ledger
`2026-10-09-capability-0.2-255bcdd8.md` §6). Also read: `start_table.md`
(refactor A is complete on main) and `where_to_start.md` (D151). Evidence:
`studies/revend_twin/` (the hand-twin, its scripts and verbatim results).

## 0. Answers first

1. **Route and admission (§2).** REVEND is ONE new row in the start table's
   WINDOW slot, `rev-end`, placed before W1 `window`. It hands the same type W1
   hands: a run-time `LOWER` (`search_from := s*`), or a NOMATCH `VERDICT` when
   the walk accepts nothing. Every slot after WINDOW is asked unchanged, and the
   artifact's forward and reverse passes then run over `[s*, n)`. This is the
   twin's **form B**. It ties or beats form A (an exact start handed to the
   anchored entry) on 15 of 17 timed cells. It adds no new handoff type, no new
   edge, no anchored-entry dependency and no new machine. It reuses the
   artifact's own reverse machine and the one reverse-block emitter
   (`emit_scan_loop`, `src/gen/emit_dfa.c:9528`).
   - Admission is three conjuncts:
     - a new fact `end_pin` (the view half of `src/facts/endwin.c`'s `ew_walk`
       plus its `\G` decline, with NO width and NO encoding conjunct);
     - RECOVER selects `reverse-pass` on the artifact's route;
     - the caller-facing entry (`fit.chosen == ENGM_DFA`, W1's own site
       condition).
   - Deny: a row deny, `-fno-rev-end` (one new bit; the manager allocates it).
2. **Exactness (§3).** Every match ends in `E = {n} ∪ {n-1 if $/\Z and
   s[n-1]=='\n'}`. So the minimum accepting position `s*` over the seeds is the
   leftmost-first start. The END is never read off the walk: the unchanged
   forward pass from `s*` finds it. `search_from`, find-all, nullable bodies
   and `$`/`\Z`/`\z` fall out of the seed guard plus the existing reverse
   block's lower bound. `(?m)$`, `\G` and trailing lookarounds are declined by
   the fact.
   - **Under utf8 the walk discharges the K49/K50 obligation by construction.**
     The seeds are boundaries, and the machine accepts only after consuming
     whole well-formed characters. So REVEND serves the utf8 cells W1 declines
     (`decline:enc-multibyte`).
   - Twin evidence: answer identity on 43 patterns (35 byte, 8 utf8), every
     `search_from`, find-all, 0 disagreements in either form.
   - Against libpcre2 10.46: 0 disagreements, except K74's known ill-formed-end
     family, which the twin reproduces from the artifact unchanged.
   - Two sabotage controls make the sweep fail (§6.2).
3. **Interaction (§4).** REVEND before W1 SUBSUMES W1 on the DFA route. Both
   are flat on bounded patterns. W1 stays the row for the VM route (no reverse
   machine), for hybrids until stage 2, and as the deny arm. REVEND is not a
   kit search site: the walk is a DFA step loop (never delegated, T8). Its
   reverse stay-skips are the existing STAY site's `dir_rev_skip`, unchanged.
   **No [MEMFN] request.**
4. **Emitted shape and ABI (§5).** It is an abi event. The readers are listed
   by grep, not edited.
5. **Predictions for the bench (§7)**, from the hand-twin:
   - every acceptance cell at **10-115 ns** on the bench box, against 0.2-2.9
     ms today;
   - all cells at or below RE2's 94-255 ns band; `[a-z]+\.txt$` x
     t-tail-txt-1m (predicted 115 ns) also inside rust's 22-221 ns band;
   - the ratios to the JIT invert to roughly x10^4 in pcrec's favour.
6. **Family (§8).** This is the "seeded reverse walk" family
   (`where_to_start.md` §1.3 item 4): RECOVER's reverse pass, REVEND and D151's
   rev-inner. They share ONE emitted helper (the reverse block, parameterized
   by its seed and lower bound) and the `EXACTREV` mapping. REVEND is the
   cheapest member and should be built first: it lays down the seed-loop
   helper rev-inner reuses.

---

## 1. What fired, and what today costs

Bench O-91 (c) (ledger §6) gives five patterns x three `t-tail-*-1m` bodies
(15 cells), plus `\s+$` x `t-trim-nearmiss-16k`, plus `\d+$` x `t-1m` (§8 item
1 of the ledger names it in the acceptance surface).
- Every pcrec cell stamps `engine=dfa, match=unwrapped, start=reverse-pass`,
  and costs 0.20-2.72 ns/B whatever the tail.
- RE2, rust and vectorscan are 22-255 ns flat. The JIT is at parity with
  pcrec.

These are long-subject THROUGHPUT cells (0.2-2.9 ms per call). O-94/O-95's
driver term, about 40-50 ns per call on some short cells, is noise at that
scale, so the BEFORE numbers are reliable. The AFTER numbers will be
short-call cells, where that term matters (§7).

Why today is linear (`emit_unanchored`, `emit_dfa.c:9715`). The forward pass
records the LAST accepting position and runs until the subject end or a dead
state (`:9806-9808`). An end-pinned pattern accepts only at `n`/`n-1`, so it
always reaches `n`. The start-state skip loop helps only while the machine is
parked in state 0.

## 2. Route and admission — one WINDOW row

### 2.1 Why WINDOW, and why it hands `LOWER`

The WINDOW slot asks "can a match begin before some position computed from
the END?" (`start_table.md` §1.2; `CandSlot`, `src/core/internal.h:7058`).
REVEND gives that question's strongest answer, the exact position:
- no match begins before `s*`, and one begins at `s*`;
- or no match exists.

Information order (`where_to_start.md` §1.4: EXACT before WINDOW) puts it
first in the slot. `start_table.md` §4.4 already filed REVEND as a WINDOW
row, but with `hands = CAND`. That type would have needed a new WINDOW →
VERIFIER edge, and it would have bypassed every later slot through a
skeleton the row selected (the "skeleton is fixed, never selected" rule,
§0a item 2).

**This design changes that to `hands = LOWER | VERDICT`.** `s*` is written
into `search_from`, exactly where W1 writes `n - W`. Everything downstream
then runs as it does under W1:
- PRESENCE scans `[s*, n)`;
- NEXT's prefilter and the forward machine scan from `s*`;
- RECOVER's reverse pass keeps the window's `LOWER` as its bound (§1.6 "RECOVER's
  accepted LOWER": E2's, which is now `s*`).

So the edge is E2 itself (`cand_nodes[]`, `emit_dfa.c:8054`), already
declared. The extra work over form A is one forward and one reverse pass over
`[s*, n)`. Since every match ends at `n - eps`, that range is the match plus
at most one byte: O(match), never O(subject).

The twin measured both forms (§6.3). Form B ties or beats form A on 15 of 17
cells. It loses by 3-5 ns only on the two cells where the walk matches a
`\w+`/`[a-z]+` run (`\w+\z` and `[a-z]+\.txt$` on t-tail-txt). Form A's
anchored-entry call costs more than the redundant passes it saves (the call
is out of line, and the anchored `.*` machine is slower than the forward
`.*` stay loop). Form B also needs no anchored entry. Under
`-fno-anchored-dfa`, `<prefix>_match` is a wrapper AROUND `<prefix>_search`
(`dfa_matches[]`, `emit_dfa.c:7707`), and form A would have needed a
conjunct to avoid recursing.

### 2.2 The row

```
{ .c = { "rev-end", PCREC_NO_REV_END, cand_rev_end_applies },
  .slot = CAND_SLOT_WINDOW, .routes = CR_DFA, .tok = "reverse",
  .map = CM_EXACTREV, .hands = CT_LOWER | CT_VERDICT, .giveup = CG_NEUTRAL,
  .list = { [CAND_ROUTE_DFA] = { "end-window", 1, "rev-end", PCREC_NO_REV_END } },
  .u.window = { .clamp = false, .walk = true } }
```

It sits at the head of the WINDOW block (`cand_rows[]`, `emit_dfa.c:8160`),
before `window` (`:8163`). W1's listing order moves 1 → 2 and `none` 2 → 3,
which is a listing change and so a spec change (§9). `CM_EXACTREV` is the
mapping `start_table.md` §1.4 reserved for D151. This row is its first user.

### 2.3 The predicate: three conjuncts, each a line with its own sabotage row

```c
static bool cand_rev_end_applies(const CandSel *s)
{
    if (pcrec_fact_end_pin(s->cx) == PCREC_EPIN_NONE) return false;      /* R1 */
    if (cand_route_of(s->cx) != CAND_ROUTE_DFA) return false;             /* R2a */
    if (cand_read(CAND_SLOT_WINDOW, CAND_SLOT_RECOVER, s, ...)->u.recover.pinned)
        return false;                                                      /* R2b */
    return s->cx->job->fit.chosen == ENGM_DFA;                            /* R3 */
}
```

- **R1, the new fact `end_pin`** (`facts.def`, E2, `PF_CORE`, owner
  `src/facts/endwin.c`). Its value is `none` / `eol` / `z`: the existing
  `ew_walk` (`endwin.c`), plus its `\G` decline (3) and multiline decline
  (4). It has NO width decline (1) and NO encoding decline (2). This is the
  general fact `end_window` already computes on the way to its own answer.
  `end_window` becomes a READER of `end_pin` (end_pin, then the encoding
  test, then `pcrec_cwmax`), so the two cannot drift. `end_window`'s `why`
  order is kept (its `enc-multibyte` decline is still tested first), so its
  `--emit-facts` row is byte-identical. `end_pin` gets no fact deny of its
  own. `-fno-end-window` (bit 29) keeps emptying `end_window` only, and the
  row deny removes the row.
- **R2, a reverse machine exists.** R2a is the route (`job->rdfa` exists on
  ENG_UNANCH only, `src/core/internal.h:2627`). R2b reads the RECOVER
  selection through `cand_read`: a declared selection edge WINDOW → RECOVER,
  acyclic because RECOVER reads nothing. `pinned` has no reverse machine
  (`emit_unanchored`'s `if (!pinned)` arms, `:9753`). In fact no end-pinned
  pattern is `pinned`: P1 needs a PLAIN-view accept at s0, which a `$`/`\z`
  accept never is. But the predicate READS the selection rather than relying
  on that argument, which is the K84 rule. VM-only artifacts (backreferences,
  `(*pla:...)`, a refused reverse machine) fail R2a and decline. They keep W1
  where W1 applies.
- **R3, the caller-facing entry**, W1's own site condition (`:9784`).
  - The VM hybrid's inlined prefilter never clamps.
  - The VM entry's window site (`emit_vm.c:13140`) is stage 2 (§10 Q3),
    because the reverse tables live in the prefilter's function, not the VM
    entry's.

What is NEW: the fact `end_pin` (a split of existing code), the row, the
predicate, one `CandWindow` payload field (`walk`), and the emitter arm
(§5). What is REUSED: the reverse machine, its tables and the reverse-block
emitter, the stamp macro, the listing axis, and the WINDOW → successors edge.

### 2.4 Deny/force axis, and what `make test-axes` needs

- **Deny only.** `-fno-rev-end` / `PCREC_NO_REV_END`, a row `deny` field in
  D82's shape. The flag removes the row, the walk selects W1 or `none`, and
  nothing branches on the flag. No force flag (D148 Q3's "deny only",
  restated for new rows in `start_table.md` §3.7).
- **`make test-axes`** enumerates its arms from `--list-axes`. The new listing
  row brings the `-fno-rev-end` arm in automatically, and the arm must be
  answer-identical to default over the corpus. Two things are owed:
  - a population FLOOR for the arm: the number of corpus artifacts whose
    `<PREFIX>_END_WINDOW` reads `"reverse"`, counted by the sweep, not hand
    written. K35 and learnings §3 apply: an arm whose population is 0 is a
    dead arm and must read red;
  - the axis's DIVERGENCE CLASS is empty: this is an optimization, not a
    contract axis, so no exclusion is added.

## 3. Exactness

### 3.1 The leftmost start

Let `E` be the set of possible match ends:
- `{n}` for `\z`;
- for `$`/`\Z`: `{n}` plus `{n-1}` when `s[n-1] == '\n'` (`EW_EOL_SLACK`,
  the shipped LF convention).

The admission fact guarantees that every match of the pattern ends in `E`.

The existing reverse machine seeded at `e` accepts at exactly the positions
`p` where some path of the pattern matches `[p, e)`. Its end-context views at
the seed apply `$`/`\z` (the `rewind_position + 1 >= subject_length` view
test the reverse block already emits), and its left-context views apply `\b`
and lookbehind at each position. That is the property today's reverse pass
relies on when it is seeded at the forward end.

So `s* = min` over `e in E` of the earliest accepting position `>=
search_from` is the minimum start of any match, which is the leftmost-first
match's start. Leftmost-first picks the smallest start with ANY match, then
the priority-preferred end. REVEND claims only the start.

### 3.2 The end, and captures

Never read off the walk. At `s*` the end may still be `n` or `n-1`, chosen by
priority: `\s*?$` on `" \n"` is `(0,1)`, `\s*$` is `(0,2)`. Under form B the
artifact's unchanged forward pass from `search_from = s*` finds the
leftmost-first END. Its first accepting thread starts at `s*`, by
construction the leftmost. The reverse pass then recovers `s*` again.

DFA artifacts have only group 0. A captures-bearing pattern is a VM hybrid.
Its stage 2 hands `s*` as the VM entry's `search_from`, and the VM's own
attempt at `s*` produces the captures over the found span (§10 Q3).

### 3.3 `search_from > 0`, find-all, the second call

- A seed `e < search_from` is skipped (no match ending before the caller's
  start can start at or after it).
- The walk stops at `search_from` with the existing lower-bound test
  (`if (rewind_position <= search_from) break;`, after the accept test). It
  reads `subject[search_from - 1]` for left context and accepts nothing below
  `search_from`, which is the obligation `where_to_start.md` §2.5 records for
  every reverse walk.
- `search_from > n` keeps today's `return 0` guard.

The find-all second call starts at the previous end, `n` or `n-1`:
- a non-empty match ended at `n`: the second call's seeds `>= n` find only an
  empty match at `n`, if the body is nullable, else nothing;
- an empty match at `n`: the caller's empty-match rule
  (`match_api.md` §3.1) moves to `n+1`, and the guard ends the loop.

The twin runs this loop in every sweep, with 0 disagreements (§6.1).

### 3.4 `$` vs `\z` vs `\Z` vs `(?m)$`

- `\z` seeds `{n}`; `$` and `\Z` seed `{n, n-1}`. A pattern mixing them
  (`\d+$|\w+\z`) takes the weakest view (`ew_walk`'s A_ALT arm) and seeds
  both. The reverse machine's views reject the `\z` branch at `n-1`. Seeding
  a position where no match can end is always sound: the walk then accepts
  nothing.
- `(?m)$` pins nothing to the end (D62 control 3) and is declined by the
  fact.
- A future DOLLAR_ENDONLY or a multi-byte newline convention (DD-11) changes
  `eps` (`EW_EOL_SLACK`) and the seed list, and nothing else.

### 3.5 Empty matches, nullable bodies

A nullable body (`\s*$`, `a*\z`, `x*$`) accepts at the seed itself, so `s*`
can equal `n` or `n-1`. That is the same answer today's forward pass reports
(the census timing block's `\s*$` no-match row reports an empty match at `n`).

When `s[n-1]=='\n'` the `n-1` walk can reach further than the `n` walk:
`a*$` on `"aa\n"` gives `n` from seed `n` and 0 from seed `n-1`. So the
minimum over BOTH seeds is load-bearing. The `firstseed` sabotage control
(§6.2) is exactly this: 552 + 355 disagreements on `a*$` and `.*$`.

### 3.6 utf8: the K49/K50 obligation

`[OPT-ENDWIN]` declines utf8 because its clamp is a byte OFFSET that can land
inside a character. Under K50 that is a wrong answer for negative assertions,
not merely a wasted attempt.

The walk never computes an offset. Its accept positions are
- the seeds: `n`, and `n-1` only when `s[n-1]` is the ASCII newline. Both
  are character starts.
- positions reached by consuming bytes backwards through a machine whose
  forward language consists of whole well-formed characters. Under the
  default invalid-tolerant contract an ill-formed byte matches nothing
  (`docs/spec/tuning.md` §2.36). So the machine is in a non-accepting
  mid-sequence state at every continuation byte, and dead at any ill-formed
  one.

It therefore accepts only at character starts, and `search_from := s*`
satisfies the K50 boundary contract the entry guard checks.
- The entry's startpos guard (`if (!(search_from == 0 || ... (subject[search_from] & 0xC0) != 0x80)) return PCREC_ERR_STARTPOS;`)
  runs before the walk. A caller's mid-character startpos is still refused,
  as today.
- Twin evidence: 8 utf8 patterns over tests/utf8 subjects plus multibyte and
  ill-formed edges, 0 twin disagreements.
  - Against libpcre2 (UTF + MATCH_INVALID_UTF): 0 disagreements on 7 of the
    8.
  - `\B\w*\z` disagrees on 55 cells, every one an ill-formed subject end
    (`a\xce`, `ab\x80`). That is **K74** (open, deferred: "`$` and `\B` at
    an ill-formed subject END diverge"), and the twin gives the artifact's
    answer on every one of them.

So REVEND discharges the obligation rather than declining. Under utf8 it is
the replacement for W1 that the plan row named.

### 3.7 Absent or refused reverse machine

R2 declines and the artifact keeps its current WINDOW row (W1 or `none`). No
row of this design ever runs without its machine. The decline is a predicate
read, not an assertion.

### 3.8 The give-up posture

`NEUTRAL` on the DFA route: no VM attempt exists to skip.

Stage 2 on the hybrid would be `ONE_WAY`, D151 Q4's posture for the reverse
walk family. Skipped attempts below `s*` cannot match, but they could have
spent budget, so a give-up may become an answer, never the reverse.

## 4. Interactions

### 4.1 With the other slots

| slot | under `rev-end` | why it is sound and cheap |
|---|---|---|
| PRESENCE | asked, over `[s*, n)` | the necessary-byte/run pre-check now scans O(match) bytes. It MUST come after the walk: before it, a pre-check over `[search_from, n)` would be the O(subject) term again. That order is the slot order today (W1's clamp precedes the pre-check, `:9785` → `:9792`) |
| WIDTH | VM only | — |
| FIRST | asked | the handoff's window starts at `max(s*, c - K)`; sound for the same reason it is under W1 |
| NEXT | asked | prefilters scan from `s*`. The first candidate IS `s*` |
| RETRY | VM hybrid only | — (stage 2) |
| BOUND | ATTEMPT / VM only | not on this route |
| RECOVER | asked, `reverse-pass` | its lower bound is `search_from = s*` (E2's LOWER, §1.6) |

### 4.2 With `[OPT-ENDWIN]` (W1): REVEND subsumes it on the DFA route

With REVEND first in the slot, the class B byte rows (bounded width,
start-unanchored; corpus 117, bench 5 + `letters-bounded-tail-z`) move from
W1 to REVEND on the DFA route.
- Both are flat. W1 scans `<= W` bytes forward plus the match back. REVEND
  walks the match back, then forward and back again over it.
- On `abc$` that is a handful of steps either way. On
  `(?:[a-z]{0,1024})\z` over letters it is about 2 x 1024 steps either way
  (the walk reaches the window's floor and the DFA dies there).
- W1 does not become dead. It remains the row for the VM-only route, the
  hybrid until stage 2, and the `-fno-rev-end` arm. Its own sabotage S264
  keeps reaching through those.

This is §10 Q1 for Frank: the alternative order (W1 first) keeps class B's
bytes unchanged, at the cost of the table's information order.

### 4.3 With `memfn` (D146/D147)

- The walk is a DFA step loop. `integration.md` §8.5 marks "any DFA or VM step,
  and T8/T9 (the engine)" as never delegated. It stays pcrec's.
- The reverse block's skip loops (the `stay`/run arms `emit_scan_loop` writes
  inside the walk) are the existing STAY site's `dir_rev_skip`
  (`tests/memfn/site_manifest.tsv`). REVEND emits the same block a second time
  under the seed loop, and the kit's bytes do not change.
- The site manifest checks sites by FUNCTION, so C17
  (`tests/memfn/run_site_manifest.sh`) must be re-run to confirm that a second
  call site of the same emitter adds no row. If it does, that row is a
  manifest re-pin in the build commit, not a kit request.
- **No [MEMFN] request.**

### 4.4 With `[ENG-TACTICS]` rev-inner (D151)

See §8.

## 5. Emitted shape and the ABI event

### 5.1 The C (form B; the twin's `mktwin.py TWIN_FORM=lower` is this text)

Placed by the WINDOW emitter at W1's position in the body (`:9784-9785` for
`emit_unanchored`; `emit_attempt` is not routed: R2a). The reverse machine's
tables are emitted BEFORE the window text when the row is `rev-end` (today
`emit_machine_tables(c, &rev)` is at `:9797`, after the clamp and the
pre-check, because nothing before needed it). That table move is conditional
on the row, so W1 and `none` artifacts stay byte-identical.

```c
    if (search_from > subject_length) return 0;
    /* [OPT-REVEND] every match of this pattern ends at the subject's end (or
     * before a final newline): walk the reverse machine back from there;
     * the smallest accepting position is the leftmost match start. */
    size_t revend_start = (size_t)-1;
    for (int revend_seed = 0; revend_seed < 2; revend_seed++) {   /* 1 under \z */
        size_t match_end_position = subject_length;
        if (revend_seed == 1) {
            if (subject_length == 0 || subject[subject_length - 1] != '\n') break;
            match_end_position = subject_length - 1;
        }
        if (match_end_position < search_from) break;
        size_t match_start_position = (size_t)-1;
        size_t rewind_position = match_end_position;
        <the reverse block emit_scan_loop(c, &rev) writes today, label renamed>
        if (match_start_position < revend_start) revend_start = match_start_position;
    }
    if (revend_start == (size_t)-1) return 0;
    search_from = revend_start;
    <the body as today: pre-check, forward pass, reverse pass>
```

- The `\z` arm emits `revend_seed < 1` and no newline arm: the seed count
  comes from `end_pin`.
- The block's label (`<p>_reverse_scan_views`) needs a distinct name in the
  walk copy. That is a parameter of `emit_scan_loop`, which the family helper
  (§8) needs anyway.

### 5.2 Stamps

- `<PREFIX>_END_WINDOW` gains a token, `"reverse"`. Its vocabulary is a
  number or `"none"` today (`match_api.md`'s [OPT-ENDWIN] entry, `:3886`), so
  the vocabulary is closed + 1. Spelling is the manager's call (memory
  `pcrec-dd13b-syntax-is-managers`).
- `RX_DFA_SCAN`, `RX_DFA_PREFILTER` and `RX_DFA_START` are UNCHANGED and stay
  truthful: under form B those mechanisms still run, over `[s*, n)`. This is
  a second reason for form B. Form A would have left three stamps naming
  passes that no longer run, which is the "reverse-pass on 452 artifacts with
  no reverse machine" defect class `start_table.md` §0 lists.
- `rx_info` has no field for the window, so it does not move.

### 5.3 The ABI readers (found by grep; NOT edited by this lane)

The rule (CLAUDE.md situation index; D76/D94): grep the tree for the CURRENT
abi number's readers at build time. Main is at 70 and RQ-3 is in flight at
71, so REVEND's number is whatever main reads then plus one. The sites
today, from
`grep -rnE "PCREC_ARTIFACT_ABI|abi[ =:]+70\b|\babi 70\b|ABI_H 70"` plus a
grep for `abi 69 -> 70` re-pins:

- `src/gen/emit_dfa.c:54` `#define PCREC_ARTIFACT_ABI 70` (the one constant;
  both emission sites read it);
- `lib/pcrec.h` (the abi comment block), `lib/CLAUDE.md`, `src/gen/CLAUDE.md`;
- `docs/spec/match_api.md:301-305` (the TU-collision guard example) and
  `:2318` ("`rx_info.abi` is `70` on every artifact today");
- `tests/registry/limits_check.sh` (`:348`, the abi digit reader);
- `tests/codegen/run_codegen_tests.sh` (abi reader);
- `tests/codegen/run_recursion_identity.sh:1217-1222` (the identity gate's
  FILEPIN self-pin, the "(B) pin");
- `tests/codegen/run_cpset_structure.sh:898` and
  `tests/resource/run_resource_tests.sh:736` (re-recorded at 69 → 70; check
  whether REVEND moves their witnesses: the cpset/resource witnesses are not
  end-pinned unless the census says so);
- `tests/mech/sabotages/S693_abi_not_bumped.sh:7,20` (`SAB_BEFORE` pins the
  current constant: re-anchor);
- `docs/design/start_table/sabotage_anchors.tsv`,
  `docs/design/dec_fallback/sabotage_anchors.tsv` and the two
  `call_graph*.txt` (they cite the constant's line).

Then, per the D94 addendum, run the suites that COUNT even where no reader
cites the number: registry, codegen, rxtsource.

### 5.4 Movers

Every artifact the row admits moves:
- corpus class U DFA byte rows (32 distinct, census §3.1);
- class B byte rows (117; under §10 Q1's leaning);
- class B/U utf8 rows (1 + 0 today);
- on the bench, the 15 + 2 acceptance cells, the 5 class B cells
  (`anc-dollar`, `anc-z-lc`, `anc-z-uc`, `ctrl-abc-dollar`,
  `wild-semdiv-dollar-trailing-newline-pcre2`) and `letters-bounded-tail-z`.

The build's movers census is mechanical: `emit_sweep` default vs
`-fno-rev-end`, and the moved set must equal the set whose `END_WINDOW` stamp
reads `"reverse"`.

## 6. The hand-twin (`studies/revend_twin/`, scratch tier)

`mktwin.py` takes each UNMODIFIED artifact (emitted with the bench's flags,
`--features all`, `-e utf8` on utf8 rows) and rewrites its `<p>_search`:
- **form A**: the forward pass is deleted, the artifact's own reverse block
  runs from each seed, and `<p>_match` from `s*` gives the end;
- **form B** (`TWIN_FORM=lower`): the walk sets `search_from = s*` and the
  body is untouched.

Every marker is asserted, so an artifact of another shape is refused, never
half-transformed. Patterns: `patterns.tsv`, 43 rows:
- the bench's five;
- the census's 24 DFA-routed class U corpus witnesses;
- 6 edge shapes (`\s*$`, `a*?$`, an alternation-with-repeat, `\d+$|\w+\z`,
  `(?i)`, `\s+\Z`);
- 8 utf8 shapes.

### 6.1 Answer identity (`run_check.sh`; `results/check*.txt`)

Per pattern, the subject pools are:
- 848 byte subjects, every quoted subject of `tests/assertions/*.rxt`
  (`end_window.rxt` among them) and `tests/base/*.rxt`, plus 48 hand edges;
- 300 utf8 subjects;
- 12 synthesized ~1 MiB bodies: matching / non-matching / trailing-newline /
  no-tail, plus the 16 KiB whitespace near-miss.

Every `search_from` in `[0, n+1]` is tried, plus a find-all loop.

| sweep | patterns | twin vs artifact | find-all | artifact = twin vs libpcre2 10.46 |
|---|---|---|---|---|
| form A, byte (`check.txt`) | 35 | **0** / 742,945 cells | **0** / 42,164 calls | 0 / 659,925 oracle cells |
| form A, utf8 (`check_utf8.txt`) | 8 | **0** / 12,440 | **0** / 2,969 | 0 / 7,016, except K74's 55 cells on `\B\w*\z` (ill-formed end; artifact and twin identical) |
| form B, all (`check_lower.txt`) | 43 | **0** / 755,385 | **0** / 45,133 | as form A (the same 55 K74 cells) |

The utf8 rows of the FIRST form-A run compiled the oracle with `PCRE2_UCP`.
pcrec's `-e utf8` implies the ucp MODULE, not UCP semantics (`docs/spec/cli.md:219`),
so `\w` stays ASCII. Those rows are superseded by `check_utf8.txt`; the twin
had 0 disagreements there too.

### 6.2 The controls (the sweep must be able to fail)

`TWIN_SABOTAGE` plants two wrong walks over `controls.tsv` (`\d+$`, `\s+$`,
`a*$`, `.*$`):

| control | what it breaks | result |
|---|---|---|
| `noeol` | drops the `n-1` seed | **red**: `\d+$` 10 + 70, `a*$` 552 + 355, `.*$` 552 + 355 disagreements (pool + long); `\s+$` 0 (its `n` walk covers `"\n"`) |
| `firstseed` | first accepting seed instead of the minimum | **red** on `a*$` and `.*$` (552 + 355 each); 0 on `\d+$`/`\s+$`, whose `n` walk dies at once on a trailing newline |

The per-pattern zeros are themselves findings for the build's sabotage plan
(§9.2). A `firstseed` sabotage is only detected by a pattern that can consume
`\n` AND is nullable or has a cheaper path at `n-1`. The answer net must name
such a pattern.

### 6.3 Timing (`run_timing.sh`; `results/timing*.txt`)

- **Regime: scratch tier.** Linux dev box (7700X, gcc 15.2, `-O2`, governor
  `performance`).
- One core pinned (`taskset -c 7`), calls interleaved (artifact, twin), 20
  calls x 15 rounds, 3 repeats.
- load1 3.4-4.1 throughout: another chain was running on this 16-thread box;
  the per-run load is printed on every line.
- Subjects are `mksubj.py`'s stand-ins, NOT the bench's bytes: a prose body,
  then the bench manifest's described last lines (`total 20250614`,
  `saved to report.txt`, `end of file` + 3 spaces, `[20\n`), and a 16 KiB+1
  whitespace near-miss.
- Medians of the three repeats' medians, ns per call, with the [min, worst
  median] range:

| pattern | subject | today | form A | form B |
|---|---|---:|---:|---:|
| `\d+$` | t-tail-digits-1m (match) | 698 us | 32.5 [21-37] | **27.6** [21-31] |
| `\d+$` | t-tail-txt-1m | 646 us | 12.5 [8-16] | **5.0** [4-9] |
| `\d+$` | t-tail-space-1m | 652 us | 16.1 [9-17] | **6.0** [4-7] |
| `\d+$` | t-1m (`[20\n`, match) | 712 us | 30.1 [20-31] | **17.0** [12-20] |
| `\w+\z` | t-tail-digits-1m (match) | 2,074 us | 34.0 [21-35] | **36.1** [24-37] |
| `\w+\z` | t-tail-txt-1m (match) | 2,418 us | 24.6 [22-28] | **28.6** [18-33] |
| `\w+\z` | t-tail-space-1m | 2,316 us | 14.5 [10-17] | **17.1** [7-17] |
| `\s+$` | t-tail-digits-1m | 2,050 us | 12.1 [11-16] | **14.0** [4-16] |
| `\s+$` | t-tail-txt-1m | 2,023 us | 16.6 [12-20] | **13.0** [4-15] |
| `\s+$` | t-tail-space-1m (match) | 1,785 us | 31.6 [20-36] | **27.1** [16-28] |
| `\s+$` | t-trim-nearmiss-16k | 19.4 us | 8.5 [4-9] | **3.5** [3-4] |
| `[a-z]+\.txt$` | t-tail-digits-1m | 2,184 us | 28.1 [19-28] | **21.6** [12-23] |
| `[a-z]+\.txt$` | t-tail-txt-1m (match) | 2,313 us | 63.1 [47-66] | **68.6** [50-72] |
| `[a-z]+\.txt$` | t-tail-space-1m | 2,304 us | 27.1 [17-28] | **21.6** [12-23] |
| `.*\.txt$` | t-tail-digits-1m | 96 us | 22.1 [15-25] | **9.1** [9-9] |
| `.*\.txt$` | t-tail-txt-1m (match) | 103 us | 64.6 [44-67] | **32.6** [31-33] |
| `.*\.txt$` | t-tail-space-1m | 98 us | 22.1 [16-23] | **9.0** [9-10] |

- The swing is x10^3-x10^5 on every cell.
- Form B ties or beats form A on 15 of 17 cells. On the two `\w+`/`[a-z]+`
  matching cells it is 3-5 ns slower, inside the run-to-run range.
- Today's per-byte figures on this box match the bench's within x1.3 on the
  four DFA-loop patterns (0.62-2.3 vs 0.70-2.72 ns/B). `.*\.txt$`'s memchr
  is 2x faster here (0.09 vs 0.20).

## 7. Predicted values for the bench (O-91 ask 2)

**Derivation.** The bench point equals the Linux form-B median x 1.6, plus 5
ns, rounded to 5. Both terms are UNMEASURED transfer terms:
- the x 1.6 is the 7700X → Ryzen 1600 short-call factor. On long DFA loops
  the two boxes are within x1.3 (§6.3), so a short, branch- and call-bound
  path is expected to scale nearer the clock ratio, about 1.5;
- the + 5 ns is the bench's caps-route floor tax (ledger §8 item 4: 10.5 vs
  5.0 ns).

The range is [Linux form-B min, 2.5 x point]. The falsifiable claims are the
ceiling and size independence, not the point.

| pattern | t-tail-digits-1m | t-tail-txt-1m | t-tail-space-1m | today (bench) |
|---|---:|---:|---:|---:|
| tail-digits-eol `\d+$` | **50** (20-125), match | **15** (4-40) | **15** (4-40) | 735-737 us |
| tail-word-eoz `\w+\z` | **65** (25-165), match | **50** (20-125), match | **30** (7-75) | 2.21-2.25 ms |
| tail-space-eol `\s+$` | **25** (4-65) | **25** (4-65) | **50** (15-125), match | 1.78 ms |
| tail-ext-lower-txt `[a-z]+\.txt$` | **40** (12-100) | **115** (50-290), match | **40** (12-100) | 2.84-2.85 ms |
| tail-dotstar-txt `.*\.txt$` | **20** (8-50) | **55** (30-140), match | **20** (8-50) | 210 us |

Plus `\s+$` x t-trim-nearmiss-16k **10 ns** (3-25), today 29.1 us, RE2 95 ns;
and `\d+$` x t-1m **30 ns** (12-75), a match before the final newline.

- **Ceiling claim:** every one of the 17 cells is ≤ 250 ns with the bench's
  fixed driver ([B133]). If the AFTER window runs on the grown driver, add
  O-94's 40-50 ns per call, and the ceiling becomes ≤ 300 ns.
- **Size-independence claim:** the same pattern and tail on a 64 KiB body
  reads the same number within noise.
- The two matching `[a-z]+\.txt$`/`.*\.txt$` cells are the slowest because
  their walk covers 10-19 bytes, and the forward and reverse passes repeat
  them (form B).
- Against the peers: at or below RE2's 94-255 ns band on all 17 cells (the
  slowest, 115 ns, inside it). Inside rust's 22-221 ns band and vectorscan's
  34-146 ns band on most cells.

## 8. Family: the seeded reverse walk

One operation: "seed a reverse machine at a known position, walk down to a
lower bound, take the smallest accepting position". `where_to_start.md` §1.3
item 4 named it. Three members:

| member | machine | seed | lower bound | slot / map | hat |
|---|---|---|---|---|---|
| RECOVER `reverse-pass` (shipped) | whole pattern, reverse | the forward match END | `search_from` (E2's LOWER) | RECOVER / `RECOVER` | — (it IS the start) |
| **REVEND** | the SAME machine | `n`, `n-1` | `search_from` | WINDOW / `EXACTREV`, hands `LOWER` | the unchanged body |
| rev-inner (D151, `start_table.md` §4.1) | PREFIX `P`, reverse | a landmark hit `h` | the previous resume point | NEXT / `EXACTREV`, hands `CAND` (give-up `LOWER`, E11) | anchored forward / one VM attempt |

**They share ONE emitted helper.** `emit_scan_loop(c, &rev)` already writes
the reverse block. It hard-codes four things:
- the seed variable (`match_end_position`);
- the result (`match_start_position`);
- the lower bound (`search_from`);
- the label.

The family helper is that function with those four as parameters, over a
`DfaForm` of any reverse machine. REVEND is its first non-RECOVER caller:
seed = loop variable, lower bound = `search_from`. rev-inner is its second:
seed = `h`, lower bound = the resume point, machine = `P`'s.

**They share one row shape:** `map = EXACTREV`, a reverse machine read
through a declared selection edge, and the `NEUTRAL`/`ONE_WAY` posture by
route. They do NOT share a slot. REVEND answers WINDOW's question (from the
END), and rev-inner answers NEXT's (from a landmark). Folding them into one
row would be the product-row smell (`start_table.md` §0a item 2).

**Build order:** REVEND first. It needs no new machine, no new fact beyond a
split, and no new handoff type. It establishes the parameterized helper and
the `EXACTREV` mapping's first user, under the cheapest possible soundness
argument. rev-inner then adds only its prefix machine (the builder
parameter, `where_to_start.md` §1.3 item 4) and its landmark scan. Building
rev-inner first would put the helper's design under the harder member's
constraints, with the soundness model still gated on D151 item 2.

## 9. The build plan

### 9.1 Steps

1. **S0 — the fact split (no mover).** Add `end_pin` to `facts.def` and
   `src/facts/endwin.c`, and make `end_window` its reader. Verify that
   `--emit-facts` gains exactly one row and that every `end_window` row is
   byte-identical. Run `emit_sweep` over all arms: 0 emitted bytes move.
   Spec: the facts listing in `docs/spec/` that enumerates facts, if one does
   (D80); the facts layer's CLAUDE.md.
2. **S1 — the helper (no mover).** Parameterize `emit_scan_loop`'s reverse
   arm by (seed, result, lower bound, label). RECOVER calls it with today's
   names, and every artifact is byte-identical (`emit_sweep`). The same
   parameterization is the rev-inner prerequisite.
3. **S2 — the row (the abi event).** Add the `rev-end` row, its predicate,
   the `CandWindow.walk` payload, the conditional early reverse tables, the
   seed loop, the `"reverse"` stamp token, the listing row and
   `-fno-rev-end`. Then:
   - the abi bump with every §5.3 reader re-pinned in the same commit;
   - the movers census;
   - the answer net `tests/assertions/rev_end.rxt` (§9.3);
   - the codegen structural check: the stamp reads `"reverse"` ⇔ the walk is
     emitted, and a declining pattern emits no walk and is byte-identical
     under `-fno-rev-end`;
   - the sabotage rows;
   - the test-axes arm's population floor;
   - `make test-codegen`, then the counting suites, then the full battery
     (the manager's, at merge).
4. **S3 — the bench AFTER window** on the acceptance cells (via the inbox;
   §11's questions first).
5. **Filed, not scheduled (D77):**
   - stage 2: the VM hybrid route, triggered by a captures-bearing
     end-pinned bench cell;
   - a lockstep two-seed walk (one pass, two states), triggered by a
     `$`-pattern cell whose two walks are both long, e.g. `\s*$` on
     whitespace ending in `\n`. The bound today is ≤ 2x the existing reverse
     walk.

### 9.2 Sabotage plan (ids NOT taken; 7 needed)

1. Seed `n-1` dropped (the `noeol` control). It must be witnessed by `\d+$`
   AND `a*$` on `"...\n"` subjects.
2. Minimum over seeds replaced by first-accepting seed (`firstseed`). Its
   witness must be a nullable `$` pattern that consumes `\n` (`a*$`, `.*$`),
   because the obvious tail patterns do NOT detect it (§6.2).
3. The `match_end_position < search_from` seed guard deleted: an empty match
   reported below `search_from` (nullable `$` pattern, `search_from == n`
   with a final newline).
4. `end_pin` over-admits `rmin == 0` repeats: the A_REP arm returns the
   body's view, so `(?:a$)?b` would be admitted. Detected by a wrong answer
   on a subject where the only match is not end-pinned.
5. `end_pin` admits `(?m)$`: drop decline (4). Detected by multiline
   subjects.
6. The row's deny field unplumbed (`-fno-rev-end` inert). Structural:
   the test-axes arm's population floor or the codegen check reads red.
7. The early reverse-table move made unconditional, so W1/`none` artifacts
   move. Structural: the identity sweep of non-admitted artifacts.

Each lands with `SAB_REACH` from birth ([MECH-REACH]). Rows 1-5 are
answer-level. 6-7 are structural, read by checks whose expectation comes
from `--list-axes`/`emit_sweep`, not from the row.

### 9.3 The answer net and its oracle

`tests/assertions/rev_end.rxt`, in `end_window.rxt`'s shape: every claim at a
subject where the row is inert (`-fno-rev-end` arm via the axes sweep) and
where it fires. Cells:
- matching / non-matching tails;
- a final newline (both seeds, the priority-chosen end: `\s*?$` vs `\s*$`
  on `" \n"`);
- `search_from` at 0, mid-match, `n-1`, `n`, `n+1`;
- nullable bodies;
- find-all `mc` cells;
- `\d+$|\w+\z`;
- utf8 multibyte tails and an ill-formed byte before the tail.

Expectations come from python3 `re` (base tier, `\Z` mapped as
`end_window.rxt` documents) and from libpcre2 for `\Z` (`verify_pcre2.py`),
never from pcrec. K74 cells are out of scope (`known_fail` keeps them).

### 9.4 Spec hunks (D80)

- `docs/spec/tuning.md`:
  - a new `§2.x -fno-rev-end — PCREC_NO_REV_END (bit N)` in §2.26's table
    shape: what it controls, default ON, stamp, answer-identical YES,
    engine-selecting no;
  - §2.26 gains one line: W1 is now the WINDOW slot's second row, and on the
    DFA route REVEND precedes it;
  - the flags index row (`:4074` region).
- `docs/spec/match_api.md`:
  - the `<PREFIX>_END_WINDOW` vocabulary (`:3886` entry): `"reverse"`
    added, with its meaning;
  - the abi sentence (`:2318`) and the TU-guard example (`:301-305`).
- `--list-axes`' `end-window` axis listing (its spec, wherever the listing
  is pinned): one row inserted.
- `docs/design/start_table.md` §4.4: REVEND's `hands` corrected from `CAND`
  to `LOWER | VERDICT`, pointing here (manager's merge, not this lane).

## 10. Open questions for Frank (discussion: problem, forces, leaning)

**Q1. Does REVEND take the bounded patterns from W1?**
- **Problem.** The table's rule (EXACT before WINDOW) puts `rev-end` first,
  which moves about 120 corpus artifacts and 6 bench cells (the class B
  floor cells at 24-454 ns) that W1 already serves flat.
- **For REVEND first:** one general row is the house rule; utf8 class B is
  served only by REVEND anyway; and a later reader sees one end-anchored
  mechanism on the DFA route rather than two splitting by width.
- **Against:** the mover set grows from about 40 artifacts to about 160 for
  no measured speed gain. The twin predicts parity on `abc$`-class cells,
  and parity is what D119's do-not-regress bar would have to confirm on the
  bench.
- **The alternative,** W1 first with REVEND admitted only where W1 declines,
  keeps those bytes still. But it makes REVEND's population "unbounded or
  multibyte", which is a width conjunct that exists only to stay out of
  W1's way: the special-case smell.
- **Leaning: REVEND first.** Accept the larger mover set with the 5 class B
  bench cells named as do-not-regress cells in the AFTER window. W1 stays
  the VM-route row and the deny arm.

**Q2. Form B over form A.**
- **Forces.** A is the "pure" design: no redundant passes, and the row hands
  an exact `CAND`. B fits the existing typed graph (it hands `LOWER`, edge
  E2), keeps three stamps truthful, needs no anchored entry, and measured
  equal or faster on 15 of 17 cells.
- **Leaning: B.** File A as a refinement only if a cell shows the redundant
  O(match) passes mattering (a long matched tail, e.g. `.*\.txt$` on one
  huge line).

**Q3. Stage 2, the VM hybrid route.**
- **Forces.** None of the bench's tail family is captures-bearing, and the
  auto-caps route serves them as pure DFA. The census's class U VM rows are
  `(a*)$`, `(a+)$` and backreference witnesses. Building the hybrid arm now
  means emitting the prefilter's reverse tables into the VM entry, and a
  `ONE_WAY` posture to rule.
- **Leaning: file it with its trigger** (a captures-bearing end-pinned bench
  cell, e.g. `(\d+)$`), per D77.

## 11. Bench-only questions (for the manager to relay)

1. Will the AFTER window run on the fixed driver ([B133])? The predictions
   assume it. On the grown driver, add O-94's 40-50 ns per call.
2. Can the AFTER window add one smaller body for the same three tails (a
   64 KiB `t-tail-*` variant)? REVEND's claim is size-independence, and the
   1 MiB body alone cannot show it.
3. Please keep the 5 class B cells (`anc-dollar`, `anc-z-lc`, `anc-z-uc`,
   `ctrl-abc-dollar`, `wild-semdiv-dollar-trailing-newline-pcre2`) and
   `letters-bounded-tail-z` in the AFTER window as do-not-regress cells
   (§10 Q1).

## 12. Standing questions (`docs/design/CLAUDE.md`)

**12.1 The measurement regime — RELEVANT.**
- Every number here is scratch tier: Linux 7700X, warm repeated calls on one
  subject, one pinned core, load1 about 4 from a concurrent chain.
- The BEFORE numbers are long-call throughput, which this regime reads
  correctly. The AFTER numbers are short calls, where latency, call overhead
  and the driver dominate. That is why §7 states transfer terms and a
  ceiling, and why the bench's verdict regime (D144 add. 4) is the official
  one.
- No decision here flips with the regime. Form A vs B differs by a few ns on
  a x10^4 swing, and the leaning would survive a reversal.

**12.2 The independent control — RELEVANT.**
- The twin-vs-artifact compare SHARES its reverse machine and reverse block
  with the subject (the twin is built from the artifact). It proves the
  seeding, not the machine.
- The independent leg is libpcre2 10.46 on every cell where it answers the
  same question: 0 disagreements beyond K74, which is known, pre-existing
  and identical in the artifact.
- The sweep's ability to fail is shown by two planted controls (§6.2).
- The build's answer net takes expectations from python `re`/libpcre2. Its
  structural checks take theirs from `emit_sweep` and `--list-axes`, never
  from the row's own predicate.
- Population (K35): the axis floor counts admitted artifacts from the
  emitted stamp.

**12.3 What moves when data is regenerated — RELEVANT, little.**
- REVEND reads no calibration or table.
- The `end_pin` fact is derived per compile.
- The stamp and the emitted walk move only with the row's admission, and
  that is the §5 abi event.
- A regenerated bench body (new prose) moves nothing in the design. The
  predictions depend only on the tails.
