# predspec5 report: predicates_draft.md rev 5 (design only)

## STATE AT HANDOFF

STATE: done. Branch `lane/predspec5`, from main 7da9272b2. Deliverable:
`docs/design/predicates_draft.md` rev 5 (REVISION 5 changelog block first). Design text only; nothing under
`src/`, `tests/`, `cli/`, `lib/`, `memfn/` touched; COND-FAMILY.md not edited. Rulings file
`docs/dev/lanes/predspec5_rulings.md` was empty at every checkpoint (no entry to apply). Validation: `make
test-plan-lint` (2 passed, 0 failed), `make test-spec-history` (11 passed), `make test-claudemd-size` (13 passed).
Nothing OWED. Length: 1,437 lines / 125.1 KB against rev 4's 1,426 lines / 123.7 KB (about 1 % over the aim, after
trimming the changelog, the standing questions, §11's reasoning, §13's resolved list and the families paragraph;
the additions are §0.2, two table rows, O39-O40 and the count/occurs bullet).

"CF:n" below and in the spec = line n of `docs/design/plan_row_bodies/COND-FAMILY.md` as of 7da9272b2 (845 lines).
Premise test held: 12 lines carry "2026-11-15"; the audit file existed.

STATUS MARKS: every status mark in the spec is now RULED (with its CF line or a D-number), LEAN (manager reading,
this document's consequence, owner "perhaps", or a review fix) or OPEN (§13). The old marks AGREED, OWNER RULED,
MANAGER LEAN, REVIEW FIX, LEAN ADOPT, IDEA are gone; the source tag stays in parentheses. Owner "AGREED"/proposal
entries became RULED with their line; review FIX-NOW dispositions other than Q1/OWN-1 became LEAN (the audit:
no recorded owner ruling); CF "Lean ADOPT" entries (capability levels CF:472, blessed callouts CF:461, outer layer
CF:564) became LEAN.

## RULINGS FOLDED

| record line | ruling / entry | spec section(s) |
|---|---|---|
| CF:749 | the subject is never an argument; mapping by `(& f)` (already in rev 4; cites updated) | §2.3, §5.2, §5.3, E-CAL fix |
| CF:753 C33 | sections start with `&` only (`(& !B)` covered); others on need | §0.2, §5.2, §13 C33 |
| CF:753 C34 + CF:804 | no partial application in phase 1; the design KEEPS currying (CF:804 says C34 does not supersede CF:308) | §0.2, §2.1, §5.2, §13 C34 |
| CF:753 C35 | explicit `(?m)` keeps PCRE meaning inside the span; otherwise `^`/`$` = span ends; never reads outside | §11 MULTILINE, §13 C35 |
| CF:758 corrected by CF:795 | no `!` inside a normal rx, PARKED for a later plan item (scope unclear); the spelling question NOT closed | §0.2, §2.2, §14 |
| CF:795 (3) | scope: the predicate part is the goal; rx additions limited to `${}` and `&` | §0.2, §11 STATUS, §13 C23 |
| CF:761 | in a filter `^`/`$` = start/end of the span being filtered (`/\w+/ & /^foo/`); `\b` reading beyond refused; foundation string sets; edge lookarounds = manager's reading (LEAN) | §11 THE FILTERED SPAN (stated once), §0.1 L7, L11, L13, NEW L41, §12.12, §13 C15/C27/C32/O17 |
| CF:774 | C9 stands: `\d\d & between(1,12)` = 10-12; `padded(...)` or `\d{1,2}`; no compare-by-value reading | §2.4 rule + STATUS, §12.5, §13 C9 |
| CF:782 | subject numbers add and filter; structural counts via the `occurs` module; "(no number type)" WITHDRAWN | §2.1, §2.5, §8, §13 C21, O23 |
| CF:813 | the number split is not the owner's preference; his ideal = one kind; manager's view (where a test is evaluated) recorded as the manager's | §2.1, §13 O40 |
| CF:823 | `count()` first, `occurs` the fallback; numbers one kind for the user: LEAN ("perhaps") | §2.1, §8, §0.1 L42, §12.9, §13 C21 |
| CF:832 | `count()` refused on BUDGET only, no positional rule; `occurs` may be recommended; the "until you can't" reading withdrawn | §8, §13 C21, O39 |
| CF:840 | `count()` -> `occurs` rewrite = a later plan item [COUNT-TO-OCCURS], not phase 1 | §0.2, §8, §14 |

No two owner QUOTES were found contradicting each other without a later entry resolving them (CF:758 vs CF:795,
CF:782 vs CF:813/823, CF:308 vs CF:753 are each resolved by the later entry), so no STOP-rule item was raised.

## AUDIT FINDINGS FIXED

Audit = `/var/tmp/pcrec-pcrec/scratch/audpred/report_condensed.md` (findings 1-13).

- **1, 2** (C32 over-reach; the in-context rule dropped): answered by CF:761; §11 now states the filtered-span rule
  once with `/\w+/ & /^foo/` vs the lone final pattern `/^foo/`, says it supersedes the `^`/`$` part of CF:713 and
  restores CF:56's understanding; new L41; O17 cites CF:56/CF:713/CF:761 instead of D196 F7 alone. The extension to
  compile-time sets (no filtered span) is marked LEAN (this document).
- **3** (C9 suspect): confirmed by CF:774; §2.4 quotes the confirmation; E-CAL/E-IPV4/L20 unchanged.
- **4** (E-CAL calls a filter with a subject; `leap($year)` a truth value): E-CAL and §4.6 now use the value macro
  `days_in($year, $month)` with the leap test (`$year & leap`) inside the library; no filter is called with a
  subject. "No boolean type" kept as LEAN (CF:595).
- **5** (overclaims): §6.1's "the spec must state it" no longer quoted as the owner's (it is the manager's text,
  CF:657-659); §4.6's "OWNER RULED ... AGREED with the class-count answer" replaced: the concept is RULED (CF:659),
  the tiers/thresholds are the manager's unanswered answer, LEAN, and an OPEN question (O39); §14's "no boolean or
  number type" fixed.
- **6** ("no number type" beyond his words): withdrawn per CF:782 (3); numbers are one kind for the user (LEAN,
  CF:823); what a number is = O40.
- **7** (C34 vs currying; "partially applied macros are macros"; C33-C35 listed open): §2.1 and §5.2 say phase 1 has
  no partial application and the design keeps currying (CF:804); C33-C35 moved to RESOLVED.
- **8** (`!` closing the spelling question; `&` in rx vs C2): §2.2/§0.2 say PARKED (CF:795); C23 restated with the
  owner's `&` rx addition (CF:795) against CF:577, lean Reading A.
- **11** (Q7 "1-based (ruled)" suspect): kept RULED, citing CF:583 ("I agree with your leans", which covers Q7);
  the other two suspect readings (C4's explicit `&`; "Enumerate go.") were not in the brief's fix list: C4 cites
  CF:573, Enumerate stays "design adoption" (CF:648).
- **12** (`&`-at-vm next-end caveat dropped; `x: date` cite; C6 listed open): caveat restored in §6.1 (CF:63, LEAN);
  §5.4 now uses `m(x: T)`; C6 RESOLVED by CF:81/CF:117.
- **9, 10, 13**: 9 needed no spec change (rev 4 was already clean); 10 stays OPEN as C25 (cites CF:614, CF:648); 13
  (entry dates) concerns the record, not the spec: nothing to change here.

Also: the status-mark scheme itself (every mark RULED with a line / LEAN / OPEN), per the brief.

## OPEN ITEMS

For the owner, in plain words (few; each with a leaning):

1. **How big is too big?** Two size limits are named but never set by you: when a relation between two labels gets
   too many classes for one automaton (the "24 fine, 1,440 borderline, 3.65M error" numbers were the manager's answer
   to "how practical", CF:659-663, never replied to), and the budget over which `count()` is refused in favour of
   `occurs` (CF:832). Leaning: one measured, labelled budget shared by both, printed by the cost report, with no
   fixed thresholds in the spec (spec §13 O39).
2. **What is a number?** You want one kind of number (CF:813, CF:823). Rev 4 treated numbers as text sets (`5` is
   the string "5"). Should a count still be "the set of its spellings" (so it can be inserted with `${...}` and
   compared by the same rules as subject digits), or a value of its own? Leaning: keep numbers as canonical numeral
   strings, so no new value kind and counts follow the existing comparison rules; the compiler chooses where a number
   test runs and shows the cost (spec §13 O40).
3. **`&` written inside rx text.** You list `&` (with `${}`) as the rx additions the predicates need (CF:795), but a
   plain PCRE pattern `R&D` treats `&` as a letter. Leaning: `&` is an operator in rx text only directly before a
   `${...}` hole (the guard form `(\d+)&${ <256 }`), so every existing PCRE pattern keeps its meaning (spec §13 C23).
4. **The record vs the earlier reading of `^` for compile-time sets.** Your 11-15 words cover filters (spans being
   filtered). For compile-time sets (`@warn.off(/^dead\./)`, `enumerate(...)` arguments) no span is filtered; the
   spec reads `^`/`$` there as the string's own ends (LEAN). Leaning: keep; it is the same rule with the string as the
   span.
