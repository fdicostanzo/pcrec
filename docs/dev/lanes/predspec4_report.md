# Lane predspec4 report: predicates_draft.md rev 4

Lane predspec4 (sonnet), documentation only (NO BUILD GO). Branch `lane/predspec4`. Deliverable:
`docs/design/predicates_draft.md` rev 4. PREMISE TEST held: `docs/design/plan_row_bodies/COND-FAMILY.md` ends with the
note beginning "RULING (Frank 2026-11-15: "Agree with mapping")". The rulings file
`docs/dev/lanes/predspec4_rulings.md` was empty at every check (start, before commit, before this report).
STATE: complete.

## RULINGS FOLDED

All from COND-FAMILY.md, after "transforms are FILTER MODIFIERS":

1. **C32 (2026-11-14, "agree all four").** `^`/`$` in a condition mean the value's start/end; the edge-assertion error
   covers `\b` and edge lookarounds only. §11 rewritten (definition, error text, interior example); look-alike rows
   L7, L11, L13, L15, L16, L17 now SAME; §12.12 E-CTX-1, 5, 7 become no-error cases; §2.6, §2.7, §7.1 text fixed.
2. **C1.** `A & B` / `B & A` accept the same subjects; D196's left operand picks the reported span. §2.2, new row L39.
3. **C30 and C31.** Modifiers are filter -> filter; counted conditions are a parenthesised literal
   (`occurs.exactly(1, (name: ...))`). §8, §12.9.
4. **Patterns take no arguments.** The call form `isodate(year: S)` and the C22 labelled-argument addendum are
   withdrawn; calling a pattern is an error with the hint; a parameterised pattern is a macro. §4.1, §5.2, §11 (hole
   example), §5.4; rows L3 (reduced), L38, new L40.
5. **Final RULING 2026-11-15 ("Agree with mapping").** The subject is never an argument; positional = required
   parameters, keywords = optional settings, any parameter by name; one application spelling `x & f`; mapping by
   operator sections `(& f)`; no lambda until needed. §2.1, §2.3 (rewritten), §3.5, §5.2 (rewritten), §5.3; rows L5, L6.

## CHANGED SECTIONS

Changelog rev 4, §0 status, §0.1 (rows L3, L5-L7, L11, L13, L15-L17, L38 changed; L39, L40 added), §2.1, §2.2, §2.3,
§2.6, §2.7, §3.5, §4.1, §5.2, §5.3, §5.4, §7.1, §8, §11, §12.9, §12.12, §13, §15 rows. Superseded text replaced, not
left beside the new.

## REMAINING OPEN

Resolved and dated in §13: C1, C20 (re-resolved), C27 note, C30, C31, C32. C29 narrowed (the `isodate(x)` value form is
gone; whether `.year` of `x & isodate` is a value or pattern stays open). NEW, listed not resolved:
- C33 operator sections: which operators have them, parse of `(& f)` vs a condition literal, right-hand sections.
- C34 partial application: "keywords curry" (rev 3) vs keywords = optional settings and any parameter by name.
- C35 `(?m)` `^`/`$` inside a value under the "value's ends" ruling.
O12 (keep or drop `!~`) stays open, with its edge-assertion clause removed. Validation: documentation only, no build or
suite; text checked by grep for stale `isodate(`, `)(x)`, `^`-error mentions.
