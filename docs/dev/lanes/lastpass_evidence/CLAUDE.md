# docs/dev/lanes/lastpass_evidence/ — lane lastpass's evidence (2026-11-17)

Evidence for `docs/dev/lanes/lastpass_report.md`: the owner question **last-pass-default** (a bare label set inside a
loop, read by a condition after the loop: every pass, today's reading T, or the regex default R, the last pass that
set it). DESIGN EVIDENCE ONLY; rules nothing. Historical after merge; never edited after.

## Files

- `lastpass_model.py` — the engine. Loads lane pathimpact's path enumerator (`Rx`, in memory, never edited) and lane
  rxmodel's libpcre2 harness (`pcre2h.py`, imported, never edited). Runs every catalogued worked example of
  `docs/design/predicates_draft.md` rev 23.2 that reads a looped label (and nearby group-question and hit lines as
  controls) under T and R, two-valued (absent-under-not), with the branch-scope rule and the one-pattern
  `occurrences` (regex-settles). PART A premise; PART B the catalogue (T3 = the draft's own Kleene text, checked against
  the printed answers); PART B (H1) the hit lines with committed hits; PART C counts over the text sets; PART D R
  checked against libpcre2 (one callout after the regex); PART E the open loop questions; PART F regular forms.
  `LASTPASS_DEFAULT=T` (the switch: R computed as T, MOVED must print 0); `LASTPASS_SABOTAGE=1` (R reads the FIRST
  pass: PART D must fail).
- `lastpass_model.out` — the forward run (about 20 seconds).
- `scan_looped.py`, `scan_looped.out` — the search aid: every `/.../` literal in the draft with a named group inside a
  repeat of upper bound 2 or more, with its line numbers.

Commands: the report's COMMANDS section.
