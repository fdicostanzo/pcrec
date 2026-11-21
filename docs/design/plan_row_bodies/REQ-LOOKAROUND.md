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

## L1 landing, 2026-11-19 (main d68a1294c): the census reassessment (D191 addendum 1 (b))

Recorded by the manager under the owner's census rule ("After the build, a result that differs from the census's
expectation is a reason to reassess, not to push on"; "a mover here could also be a change in performance").

- **Predicted and seen.** The census at the base predicted 54 movers, all corpus (51 dead fixtures, 3 narrowings),
  no bench pattern. The built feature moved all 54 with the predicted facts and values; none was predicted and
  missing.
- **Differing result 1: a lost pin (review r55 B).** A narrowed run lost its `run_pin`, so about 1 in 12 "keyword
  then lookahead" shapes fell from the `run-pinned` prefilter to `handoff`/`offset-set` (e.g. `xy(?=bc)[bc]c`).
  Reassessed: not landed that way. Fixed in the general form (the pin claims the longest proved sub-stretch around the
  rarest pinnable byte, which also discharges L2's A5): PIN-LOST 0 at landing.
- **Differing result 2: pins gained outside lookarounds.** That general rule GAINS a pin on 48 patterns with no
  lookaround (e.g. `((ab)+c)+` pins `ab`), three of them bench patterns (166 and 168, the 31- and 40-byte literals;
  273 `a+ab`). Reassessed: their emitted C is BYTE-IDENTICAL in all 12 builds (byte/utf8 x default/vm, base vs fix;
  lane l1ftri2), so no bench timing moves. Over the whole corpus 62 default-engine patterns move their C, all census
  movers; exactly one has no lookaround (`(?:abc)+d`, a corpus fixture, now `run-pinned`). No timing run owed.
- **Listing limits the D27 witnesses found (not answers; 0 answer disagreements in 88 witnesses):** a wide consumed
  class (more than 128 members) is never narrowed; a wide class in a lookbehind body drops it; an exact repeat
  `{n}` in a lookahead body ends the item; a lookbehind nested in a lookahead is not joined; two lookaheads before
  `\w+` are not dead. Each is a limit span_arms rev 3.3 states (§5.1, D-10, D-1, D-3; §10 U-nesteditem, U-assoc);
  tests/lookaround/d27_l1/l1d27_limits.tsv names each, and make test goes red when one is lifted.
- **Found on the way, pre-existing:** K146 (nested quantified lookarounds overflow the compile thread in vm_cost at
  nesting 180), filed with [K146-VMCOST-DEPTH].

## L3 remodels

- **Declared multiplicity change of the trace build's ordered record sequence (review r63 EMITTED-1).** Across
  `f52b6d6aa` (RM-2, `PfBound`) the trace build prints fewer FIRST `req-use` records: `req_handoff_k` is a traced
  `cand_select(FIRST)` that BASE asked twice in `req_site_define` and twice in `req_handoff_stamp` and the subject asks
  once in each. Bounded-handoff artifacts lose 2 asks (and their nested reads), unbounded ones 1 (e.g. 240 to 216
  lines on `x{2,5}(?i:cat)` vm). The record SET and the MFPICK lines are identical, no emitted byte, fact or answer
  moves. A trace sweep spanning RM-2 declares it (`scripts/trace_diff.py --declared`, or `--unordered`).

**OBSERVATION (Frank 2026-11-20, after l3feat's stop on the forward-scan re-entry at K<0; his words):** "How does it find the left over dfa part? Using the rx itself or looking at the dfa graph? If available, using the graph might be better. Follow the proved bytes through the whole graph then use that point as the new start. Then remove the unused states." Manager's reply (recorded as the manager's, unmeasured): the re-entry today uses neither; it is gated on a STATE FACT (the scan is back in the DFA's start state with no accept pending, `emit_req_reentry_use`'s comment in src/gen/emit_dfa.c) and then re-asks the kit for the run from the scan position. With the lookbehind's run before the match, the start state can carry a match already in flight (`\d*` folds into it), so the gate is unsound. Two graph-based directions noted: (1) a sound gate, read from the subset construction: re-enter only in states whose NFA set holds no started match; (2) his: run the proved bytes through the graph, start from the state reached, prune unreachable states; it needs the lookbehind's bytes inside the graph, and it overlaps [MATCH-KNOWN] (parked 2026-11-11). Open; discussed, not ruled.
**LEAN (Frank 2026-11-20, his words, a discussion not a ruling):** "Looking forward, we are probably going to have to build a bunch of rx and graph manipulation stuff for the predicate language. I don't know how you planned to implement rx intersection or subtraction but this sounds an awful lot like that. Perhaps we save both this and match start for then when it can be proper manipulation rather than one offs". Manager's reading: both graph-based directions above and [MATCH-KNOWN] wait for a general rx/graph manipulation layer (intersection, complement, running known bytes through a graph, pruning), expected to be built for the predicate language ([COND-FAMILY]); no one-off version is built here. Sent to the predicate manager as from_main.md M-2.
**DISCUSSION (Frank 2026-11-20 evening, his words, on review r65's `(?<=a)(?<=[ab])c` row):** "now that we have this information, 1. some records can be proved. We've discussed that. 2. but those that can't or that have a fixed but complicated lookbehind or lookahead outside the span, could we simply include them in the dfa where legal? Perhaps if we get dfa captures, then the match span is capture 0". Manager's reply (the manager's, unmeasured): that is [ENG-LOOK] (lookaround by product construction in the DFA, chartered 2026-08-23, the first piece of [COND-FAMILY] per D193.1) plus [ENG-TDFA] (tags; the capspike study matched PCRE2's capture offsets on 730 patterns); with the lookaround's bytes inside the DFA's language the forward-scan re-entry that L3 had to decline is sound again, and two lookbehinds at one point are an intersection, the predicate layer's operation. Not ruled; no work launched.
