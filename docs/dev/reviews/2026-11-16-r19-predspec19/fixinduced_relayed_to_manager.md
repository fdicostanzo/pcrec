# fix-induced lens, crit-predspec19: RELAYED (the critics' findings-file writes were refused by the harness)

Saved by the manager 2026-11-16 from the two critics' hand-back messages to the manager session. Headlines only: the
full texts were sent by the critics to the coordinator by message and did not arrive. UNVERIFIED.

## Critic fixind (first), 9 findings (8 confirmed, 1 suspected); probe in ../fixind/probe.py, probe.out

- Main finding, confirmed by probe: over a LOOPED field, "strictly above 9:00" (the form `lex_ge2 & !lex_le2`)
  accepts the list `9:00,9:15,`, though one entry equals 9:00. It differs from "every entry strictly above" in 14 of
  114 cases.
- The other eight: text not received.

## Critic fixind2 (replacement), 8 confirmed findings (FIXIND-1..8), no scripts run

1. O73 says §3.2 tool 1 stands unchanged, but rev 19 rewrites that tool's "always an rx" rule for arrays of field
   references.
2. §2.1's ruled "no third value kind" (CF:858) is unchanged, yet the field reference is described as "neither a value
   nor a condition" and is passed as an argument.
3. Rev 19 makes `r := ^h` and `refs := [^h, ^m]` errors. That breaks L2 ("a binding equals its expansion"), and L2
   does not record the exception.
4. The `^` row says a reference stands in "exactly two positions", and those include the bound `[^a1, ^a2]` that the
   same row lists as an error.
5. §7.1 limits the `compare.looped` warning to a tuple compare's field; the `^` row and §8 apply it to any reference.
6. §0.2 marks the field reference "RULED" and no longer mentions the open O75 dependency. §4.1 calls the new exception
   "adopted", while DECIDED (63) calls it LEAN.
7. L72 no longer promises an error naming the sigil when no binding `h` exists.
8. §8 says the any-number-of-fields form needs §4.1's exception widened; O69 (3)'s trigger was not updated to say so.
