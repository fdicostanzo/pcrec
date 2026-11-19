
## 2026-11-18 OWNER RULING — lookahead-home: the kit's method (Frank, to session 140, evening)

ASKED AS A RULING (slug lookahead-home, by /q, from docs/design/dense_hit_arch.md rev 2.1: does his "derive it from
a SYSTEM constant" block size bind the kit's method or pcrec's loop; the manager's lean: the kit owns how the
position is obtained, block size included; pcrec owns the compare and the stop). HIS WORDS, in full:
"lookahead-home: I agree with your lean here. The request to kit is to find reasonable starts. Clarify: scenario:
the kit returns a start, pcrec runs an unanchored search which (does or doesn't) find a match. Does it then report
back the last start to kit so that it can report the next start from there? In other words, the unanchored search
may move across several candidates from kit".
RULED: the kit's method (the note's unit U1-k is the first unit; the request text for that answer is the one to
file). OBSERVATION, his: "The request to kit is to find reasonable starts". QUESTION, his (a question, not a
ruling): how the loop and the kit hand positions back and forth. THE MANAGER'S ANSWER to him (from docs/spec/
tuning.md 2.41 para 8c, read this session): the kit keeps no memory; pcrec carries the position and KEEPS the last
hit; after a failed attempt it re-asks, from its own attempt position, only once that position has passed the kept
hit; "none" answers no match. Put back to him as **starts-or-occurrences**: does "find reasonable starts" mean the
kit's answer becomes the next attempt START (the kit folds in the offset K and the stop), or stays "an occurrence
of the required text" from which pcrec derives the start (today; tuning.md 2.41 para 7a keeps the origin pcrec's).

## 2026-11-18 OWNER on starts-or-occurrences: a search loop is fine now; kit-found starts a possible later request (Frank, to session 140, evening)

ASKED (slug starts-or-occurrences: does the kit's answer stay "an occurrence of the required text", pcrec deriving
the start, or become the next attempt START). HIS WORDS, in full: "lookahead-home: why do you prefer occurances? My
thought was the case where the overshoot was high \d{1,1000}foobar. Kit finds the span foobar then jumps back 1000
bytes for the occurrence. It could then scan forward for the set of potential starts \d. That said, that could be
a specific request in the future from pcrec so using a search loop is fine right now."
RECORD: RULED for now: occurrences (pcrec's search loop stays; the request to the kit is R-46 as the accepted note
drafted it). IDEA, his, NOT scheduled: for a run far behind a long variable head (`\d{1,1000}foobar`), the kit
finds the run, steps back the head's maximum, and scans forward for the SET OF POTENTIAL STARTS (the head's first
set, `\d`); "a specific request in the future from pcrec". TRIGGER (the manager's wording): a measured cell where
attempts between (hit - K) and the true start are a measurable share of a search with a large K.
