
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
