# [REQ-LOOKAROUND]: the owner's words and rulings (row body)

## 2026-11-18 OWNER RULING — context-producer-home: one span, one producer (Frank, to session 140, evening)

ASKED AS A RULING (slug context-producer-home, by /q, from docs/design/req_lookaround_arch.md rev 2.1: for a fixed
lookbehind, ONE producer of "these bytes sit at these offsets before the match" (the lookaround item, read by every
reader, the kit's window site included; [CTX-FACTS-NEG] re-scoped to what the item cannot state) or TWO by layer;
the manager's lean: one). HIS WORDS, in full: "context-producer-home: I do feel like we've covered this ground
several times. The search span the pcrec delivers to kit should have "foobar" with starting index -3. in this case,
the match is proved and search is over. Otherwise, the kit reports back the 0 span subject offset and pcrec does
the match".
RECORD: RULED, and in his word a RE-STATEMENT of ground already covered: for `(?<=foo)bar` the search span pcrec
delivers to the kit is `foobar` starting at index -3 (ONE span with the lookbehind's bytes at their negative
offsets); where that span is the whole pattern the match is proved and the search is over; otherwise the kit
reports the offset-0 subject position and pcrec does the match. The manager's reading (marked as such, to be
checked by the design lane): this is answer (a), ONE producer; it is what D168 ("ONE ... producer of per-offset
sets"), D172 (spans carry negative start offsets; fixed lookbehinds "sourced from main's D168 producer") and D191.2-3
("the run crosses as ONE uncut span with byte sets at signed offsets from the attempt start"; "a run outside the
match is ONE run value, every reader raised together, never a second wider fact") already say. THE MANAGER'S ERROR,
recorded: the question should not have been relayed; the record answered it, and neither the note, its critic
round nor the manager's triage read D191.3 against it. CONSEQUENCES applied the same hour: register row 28 (the
contingent "two producers by layer" deviation) removed; [CTX-FACTS-NEG] noted as re-scoped to the facts the item
cannot state (`\b`, past the end, thread context).

## 2026-11-18 MANAGER'S CALL — remodel-go (not relayed further)

The note's second question (does D191's build go reach the small refactors that land first) is the manager's under
the standing rules: each refactor changes no answer and no emitted byte (gated by byte identity), high-level rule 4
of docs/dev/guide/architecture.md has remodels "built ... FIRST, as its own answer-identical unit", and a choice
with identical answers and equal cost is the manager's (Frank 2026-10-09). CALL: they ride under the unit that
needs them, in the order D191.1 requires: the unit's CENSUS first ("a unit whose census finds NO mover anywhere
stops and reports"), then its remodel commits, then the feature; a unit stopped at its census lands no remodel
commit. Told to the owner the same hour; his to overrule.

## 2026-11-18 evening, OWNER RULING proved-ending-scope

Asked whether his `(?<=foo)bar` "the match is proved and search is over" ending ([CTX-SIDES-PRODUCER]: the cover reads its context sides from the one signed-offset producer) joins L1-L3. HIS WORDS: "proved-ending-scope: i want to get there but i acknowledge that we are doing it in steps. i don't want any one step to get too complicated. so lets schedule it as an item to do after this lands". RECORD: not in L1-L3; scheduled as the next step after L1-L3 land (the manager read "this" as the three go'd units, said so to him), with its own fail-fast census and pre-go briefing (D191 add. 1, 2); it needs its own build go.

OWNER RULING l1-enabler (Frank 2026-11-19, about 12:40, answering /q): "l1-enabler. the l2/l3 might improve some stuff but i suspect the cover work after that will help as well. we have done most of the low hanging fruit optimizations and now are working on smaller improvements to fewer cases. thats just the nature of it. i say proceed to development". CONTEXT: L1's fail-fast census (lane l1build) predicted 54 corpus movers (51 never-listed fixtures, 3 narrowings) and 0 bench movers; the bench's 8 lookaround patterns are L3/L2 shapes. CONSEQUENCE: L1's feature is built after review r53's fixes land, with no extra L3/L2 census first; each later unit still runs its own census (D191 addendum 1). Recorded as a RULING (asked as one, slug l1-enabler).
