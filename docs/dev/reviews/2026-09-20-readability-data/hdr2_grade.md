# hdr2 / guesses_B2 grading report

Grader compared each of 226 guesses in `guesses_B2.tsv` (row order) against the
`truth` column of `graded_all.tsv` (same row order), using ONLY that `truth`
column as ground truth. All other columns of `graded_all.tsv` (A/B/C guesses,
verdicts, renamed variants) were ignored — they are earlier, unrelated
experiment runs.

Scale (strict, house convention):
- **correct** — guess captures the actual meaning/purpose in substance.
- **partial** — captures part of the truth, or is directionally right but
  materially incomplete or slightly off.
- **wrong** — contradicts or misidentifies the truth.
- **vacuous** — merely restates the name/type with no added meaning (e.g.
  "Field cx", "Local variable m"), a formulaic name-decode with no real
  insight, or a "no-idea"/"unknown" non-answer. `%correct` does NOT count
  partial.

## 1. Verdict counts by kind and overall

| kind | n | correct | partial | wrong | vacuous | %correct |
|---|---:|---:|---:|---:|---:|---:|
| field | 72 | 23 | 17 | 2 | 30 | 31.9% |
| func | 129 | 107 | 13 | 8 | 1 | 82.9% |
| local | 25 | 1 | 1 | 0 | 23 | 4.0% |
| **OVERALL** | **226** | **131** | **31** | **10** | **54** | **58.0%** |

Field guesses split sharply in two: struct fields with a self-explanatory
running-counter name (`nlabel`, `ngroups`, `nguard`, ...) got correct,
concrete guesses; anything needing real field-specific knowledge (`"Field
cx"`, `"Field enc_mask"`, `"Field rgn_emit"`) got the templated `"Field
<name>"` non-answer, which is vacuous by definition. Function guesses were
strong (many read like they were lifted near-verbatim from the real
doc-comments). Local-variable guesses were almost uniformly the vacuous
`"Local variable <name>"` template.

## 2. Row-order / kind / name mismatches

None. All 226 rows' `kind` and `name` columns matched exactly between
`guesses_B2.tsv` and `graded_all.tsv` at the same row index — the two files
are already in lockstep, no realignment was needed.

## 3. Hardest-to-classify guesses (for spot-check)

1. **idx 11 (`Vm.nguard_total`) and the other `*_total` fields** (13, 15, 17,
   19, 21, 23, 25, 62) — guess is the templated "Counts of X total used so
   far." Truth says these are fixed totals a pre-pass computes (used to seed
   other families' bases), not a running "so far" tally. Graded **partial**
   throughout: the guess gets "it's a count of X" right but mischaracterizes
   the running-vs-total nature. Reasonable graders could call some of these
   vacuous instead (they're barely more than name-decoding).
2. **idx 17 (`Vm.nrev_total`)** — truth explicitly warns this is LOOP count,
   not slot count (3 slots/loop, so reading it as slots undercounts 3x). The
   generic guess doesn't specify "slots" so it doesn't clearly walk into the
   trap, but it also doesn't show awareness of it. Graded partial; could
   argue wrong.
3. **idx 28 (`Vm.nrevcaps`)** — guess implies a running "used so far" tally;
   truth says it's a MAX (largest per-body capture count), a different kind
   of quantity than a running count. Close call between partial and wrong.
4. **idx 90 (`vm_slot_lookpos`)** — guess is truncated mid-sentence ("...the
   layout's TOP family but for") right where it would clarify whether lookpos
   is or isn't the topmost slot family; truth (and the guess for idx 89,
   `vm_slot_splice`) both call splice the true "eighth/topmost" family, so
   lookpos claiming "TOP family" reads as a possible contradiction, but the
   truncation makes intent unrecoverable. Graded partial.
5. **idx 98 (`vm_lifts`) and idx 108 (`vm_rev_canmove`)** — guesses are
   section-banner text lifted from the source ("---- THE ATOMIC LIFT: two
   predicates, five callers ----" / "---- §2.5's REVERSE-DETERMINISTIC rung:
   the two facts every site needs ----") rather than a description of what
   the specific function computes. They name the right general topic but not
   the function's actual behavior. Graded partial rather than vacuous because
   the topic name itself is real, specific content — a stricter grader might
   call these vacuous.
6. **idx 107 (`vm_cursor_fits`)** — guess ("THE RUNG DECISION, in ONE place
   (§2.5's ladder, D44.1's extension)") is the same banner style but doesn't
   even name "cursor" — graded vacuous for that reason, in contrast to 98/108
   above; the line between these three is a judgment call.
7. **idx 114 / 117 (`vm_count_slots`, duplicate rows) vs idx 115
   (`vm_count_slots_look`)** — the guess text for 114/117 is actually the
   correct description of 115 (`vm_count_slots_look`, the `A_LOOK` arm), not
   of `vm_count_slots` itself (the overall dispatcher). This looks like a
   row-shift artifact in how `guesses_B2.tsv` was produced (compare idx 79/81,
   which show the identical pattern for `vm_slot_guard`/`vm_slot_mark`).
   Graded wrong for 114/117 since, applied to the named function, the guess
   misidentifies it as "an arm" rather than the dispatcher itself.
8. **idx 79 (`vm_slot_guard`) vs idx 81 (`vm_slot_mark`)** — identical guess
   text ("Returns the slot index for slot class four: a possessified
   frames-rung") appears for both. It matches idx 81's truth ("fourth slot
   class") but not idx 79's (guard is not the fourth family). Same
   row-shift-artifact pattern as item 7.
9. **idx 145 (`vm_alt`)** — guess describes emitting an alternation generically
   ("whose every branch continues to...") but omits the truth's central point
   that it tries the island-trie lowering FIRST and only falls back to the
   serial push-chain. Judged materially incomplete (partial) rather than
   simply correct-but-terse.
10. **idx 158 (`vm_counter_poss_opt`)** — guess says "one frame for the WHOLE
    loop"; truth says "one cut-back frame PER ITERATION" — a direct reversal.
    Graded wrong, but it's a subtle one since both are plausible-sounding
    possessive-rung shapes and the wording is close enough to skim past.
11. **idx 161 (`vm_rep`)** — guess frames the function as itself being "the
    FRAME-based rung," but truth says it's the top-level A_REP dispatcher that
    tries cursor/revdet/counter first and only falls back to frames. Graded
    wrong for conflating the dispatcher with one of its fallback arms.
12. **idx 165 (`vm_look`)** — guess says "all FOUR polarity/direction"
    combinations; truth says "all SIX polarity/direction/atomicity"
    combinations. The overall gist (one function emits every lookaround
    combination) is right, but the concrete count is factually off. Graded
    partial rather than wrong since the core purpose isn't contradicted.
13. **idx 74/75 (`vm_rolef`)** — guess characterizes the function as being for
    "a role string"; truth explicitly says this reading is a documented
    misconception ("used far beyond 'role' text ... the name is historical").
    Graded wrong since the guess states exactly the outdated/incorrect
    reading truth warns against.
14. **idx 37 (`Vm.isl_over_cap`)** — guess "Capacity limit for isl over"
    mischaracterizes a boolean verdict field as if it were a numeric
    threshold/limit value. Graded wrong rather than vacuous because it makes
    an affirmative (incorrect) type claim rather than just restating the name.
15. **idx 94 (`vm_counter_fits`)** — guess adds "...and if so which shape,"
    implying a richer return value; truth says it's a pure boolean fits-check
    with no shape-selection role. Graded partial for the added, unsupported
    claim.
16. **idx 131 (`vm_dyn_add`)** — guess (truncated) captures "sums two
    follow-min terms" but the truncation cuts off exactly where the truth's
    key nuance would go (dropping the outer term past a length cap — this is
    the mechanism `ndynskip`, idx 45, exists to count). Graded partial.
17. **idx 220 (local `cut`)** — truth itself hedges: no local variable
    literally named `cut` was found in the file (closest matches are `cutl`
    locals and a `"cut"` string literal). The guess ("Local variable cut")
    doesn't surface this ambiguity either way. Graded vacuous like other bare
    "Local variable X" answers, but it's arguably an unfair item to grade at
    all given truth's own uncertainty.
18. **idx 30 / 45 / 46 / 47 / 48 (`npush`, `ndynskip`, `nclamp`, `ngst`,
    `nkreset`)** — same templated "Counts of X used so far" pattern as the
    `*_total` fields, but here truth confirms these genuinely ARE running,
    pre-pass "counted as written" tallies. Graded partial rather than correct
    because each truth adds a specific consequence/caveat (gates a parameter,
    counts both TEST and CLAMP forms, etc.) the generic guess doesn't reach —
    a more lenient grader could call several of these correct.
19. **idx 188 (`vm_cls_describe`)** — the guess's example literals appear to
    have been dropped/garbled in the source TSV (reads "...as a human reads
    it: 'a', , , or a count when it", missing what should likely be `[a-z]`
    and `[...]`-style examples that survive in truth). Graded correct on a
    charitable reading of evident intent, but the garbling makes it a genuine
    judgment call.
20. **idx 118 (`vm_emit`, forward-declaration row) vs idx 187 (`vm_emit`, real
    dispatcher row)** — same guess text used for both duplicate-named rows.
    It matches idx 187's truth ("the real dispatcher") well but idx 118's
    truth is specifically about being a forward declaration (a structural
    fact the guess doesn't address). Graded partial for 118, correct for 187.
