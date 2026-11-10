# condsurv report: master row and survey of the conditions / predicates / intersection family

Lane condsurv (opus), 2026-11-10. DESIGN/SURVEY ONLY: nothing under `src/ cli/ lib/ memfn/ tests/`
touched, no `make test`. Branch `lane/condsurv` (fast-forwarded to main `568465ef7` before the first
commit; no change under `src/ cli/ lib/` between `956055581` and `568465ef7`). No rulings file was
named in the brief.

## STATE AT HANDOFF

STATE: delivered. No runs owed.

- **Master row:** `[COND-FAMILY]` in docs/dev/plan.md, Backlog, directly above [CONDITIONALS];
  STATE:not-started; `next:` "owner plans the family from the survey (its §7 questions first)";
  charter = Frank's 2026-11-10 words verbatim. Members are LINKED, not moved (the Policy has no
  nesting rule for rows in other sections; [IFACE-PUSH] and [POS-PARALLEL] are the precedent): the
  umbrella's charter lists them, and the six core member rows ([CONDITIONALS], [POSTFACT],
  [ENG-LOOK], [BRANCH-RESET], [PCRE2-GAPS-TBD], [CLASS-SETOPS]) gained `[COND-FAMILY] (umbrella)`
  in their `refs:`.
- **Survey:** `docs/design/cond_family.md` rev 0 (29 KB). 17 PCRE2 members (P1-P17), 11 pcrec
  members (X1-X11), the readers/neighbours list, and an explicit "not members" list.
- **Members found that were on NO family row before (NEW):**
  1. script runs `(*sr:..)`/`(*asr:..)`: PCRE2's own "match, then filter, backtrack" span predicate
     (reader note `script-run-evaluation.md`), registry verbs, unbuilt, PLANNED, and not in
     [PCRE2-GAPS-TBD]'s member list;
  2. `(*scan_substring:(1)A)`: `&` against a captured span; marked out of scope with a stale
     reason ("revisit post-M4"; M4 has shipped) at `src/parse/mod_verbs.c:226` and its annotation;
  3. pattern variables' `${name:+w}`/`${name-w}` family ([VAR], built): already a condition (an arm
     chosen by a call-time constant);
  4. the substitution template's `${n:+set:unset}` (built): the same SET test on the other side of
     the seam, so one definition of "set" should serve both;
  5. width-1 lookarounds as `A_CTX` ([UCP] U2 T3, built): already the DFA-hosted, width-1 instance
     of the product construction; `(?:(?=a)ab|(?!a)cd)` compiles to the DFA today (MEASURED).
- **The hypothesis, tested (survey §1):** one condition node HOLDS at the IR layer but not at the
  engine layer. What puts ANY member on the DFA is one construction: the main automaton in product
  with a small deterministic checker, differing only in where the checker starts and where its
  state is read (a 4-row (start, read) table, survey §4 C3). Assertion conditions are [ENG-LOOK]'s
  positional product; span `&` is its contained special case. "Only `(?(R))` stays VM" is too
  narrow (the residue also holds relational predicates on unbounded values, backrefs,
  scan_substring over capture values, callouts).
- **First-piece recommendation (survey §5):** the checker product built for its first row with no
  new syntax, first client = capture-free bounded lookarounds that today force the VM ([ENG-LOOK]
  itself). It is the only piece with a measured population (98 and 143 in the 2026-09-29 censuses,
  to be RE-COUNTED because [UCP] U2 moved the width-1 cases since) and every later DFA member rides
  on it. Gates: D153 (remodel overlap with [STREAM] A-REV's DFA-construction site) and D119/D137
  ([ENG-LOOK] is a Candidate). The cheapest piece (the condition node on the VM) unlocks only
  refused syntax with zero measured demand; it leads only if completeness is the goal, and then
  after the name table.
- **Owner questions (survey §7, plain words, each with a leaning):** (1) speed or syntax first
  (leaning speed); (2) name "one product, many (start, read) rows" as the family core (leaning yes);
  (3) script runs as a member (yes, no row until a use); (4) re-mark scan_substring planned (yes);
  (5) honour predicates in the backtracking engine when captures are present, or refuse the mix
  (leaning honour); (6) the master row owns the order of the shared pieces (yes).
- **[ENGINE-WHY]:** the survey's member tables carry its asked-for column ("blocks the DFA because /
  keep the DFA by"), one line per member.

## Validation

- `make test-plan-lint`: checks passed 2, failed 0. `make test-spec-history`: failed 0. `make test-doc-lint`: passed 2, failed 0.
- `scripts/check_claudemd_size.sh --all`: within limits after moving the long `inline_c.md` entry
  of `docs/design/CLAUDE.md` into its NOTES.md (the file was 5 bytes under its 12,288 limit).
- Both pcre2-reader notes pass `scripts/check_pcre2_note.sh` (rc=0).

## Findings (filed here, not fixed)

- F1. `docs/pcre2_compliance.md`'s `base:scan-substring` annotation's reason ("revisit post-M4")
  has expired; survey §7 Q4.
- F2. [PCRE2-GAPS-TBD]'s member list omits script runs, which the registry routes to the same
  `verbs` row as `(*ACCEPT)`.
- F3. The [ENG-LOOK] and [CTX-PREFILTER] censuses (2026-09-29) predate [UCP] U2's `A_CTX`
  lowering of width-1 lookarounds; any selection that reads them must re-count first.
- F4. condinv §0's VERSION message disagreement still stands (P5).

## Evidence

- `docs/dev/lanes/condsurv_evidence/engine_probe.txt` (28 patterns; main-tree `build/pcrec` of
  2026-11-10 06:59, `--features all`).
- `docs/dev/pcre2_notes/script-run-evaluation.md`, `docs/dev/pcre2_notes/dfa-matcher-conditions.md`
  (new; their "Cited by" sections are empty because no code leans on them).
