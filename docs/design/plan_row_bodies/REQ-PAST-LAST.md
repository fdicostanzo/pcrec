
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

## dense-not-target (2026-11-19 about 11:25, DISCUSSION, not a ruling; recorded 2026-11-20 at the kit's R-46 freeze note)

HIS WORDS (as relayed in the owner view the same hour): "Just don't use kit searches (turn off the bit) but loop every
byte start old school. So therefore, we should not try to optimize for super dense"; then "this is a matter of degrees.
Dense for me could be defined as two+ hits in a single block if we use blocks. Super dense might be hits within some
low N like 8. I don't know N". CLASS: DISCUSSION (no question was asked as a ruling; it is still open in the owner
view under the slug dense-not-target). The kit's job 709 (night of 11-20) measured that the crossover N is NOT one
constant (about k for plain C on hex/word classes, none up to 64 with AVX2, 2 to 4 for "not newline"), so "super
dense = below one N" cannot be stated as one number; "dense = 2+ hits per block" stands as his working scope.
MANAGER'S READING (mine, 2026-11-20, kit question bounded-horizon-scope; answer-identical either way, so the
manager's call, revisitable when the discussion closes): hits within K+1 of each other (closer than the span itself) are
SUPER-DENSE, outside the target; the BOUNDED handoff row states no horizon, only the UNBOUNDED row uses it.

## Post-K38-2 re-measure, 2026-11-20 (lane dhremeas, main): LOSS STILL SHOWN

The re-measure the row waited on (tuning.md §2.41¶8c's timings predated K38-2). The rule was committed before timing (22dad3e20). Counted run 2, on 1 MB of dense " @x", `--engine=vm`, median of 7, A/A floor 0.68 %, threshold 5 %, rows on vs `-fno-req-handoff`:
- `[^@ ]+@x` (unbounded) is 1.490x slower;
- `[^@ ]{1,5}@x` (bounded) is 2.226x slower;
- the no-match tail win persists, at 0.0074 vs 1.55 ms.

The kit's R-46 byte mover was gated on this result, and the gate is now MET. Report: docs/dev/lanes/dhremeas_report.md.

- 2026-11-22 RULING (Frank, "dense-not-target: close"): CLOSED. Super dense is not a target and gets no threshold N
  (the 11-20 night measured no single N: about the literal length for plain C on hex/word, none up to 64 with AVX2, 2-4
  for "not newline"). His "two or more hits per block" stays the dense scope; where the plain every-byte loop wins,
  the measured choice tables pick it per case. Nothing is built.
