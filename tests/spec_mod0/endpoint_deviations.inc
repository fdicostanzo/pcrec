/* endpoint_deviations.inc — cells where libpcre2 decides a range endpoint
 * differently from check08's five-step model. Included by check08_endpoints.c.
 *
 * Each entry is one exact pattern plus the reason. BOTH directions fail: a
 * cell that deviates and is not listed here fails the check, and a cell listed
 * here that stops deviating fails as a stale pin. Kept in its own file so that
 * adding or removing a pin is a diff a reviewer can read on its own.
 *
 * Measured 2026-08-11 against libpcre2 10.46, over 200 scored cells (100
 * registry rows x both sides). Three cells deviate; the first two are the
 * pair the invariant statement calls "both deviating cells", and the sweep
 * confirms they are exactly the high-side delimiter-eaters. The third only
 * exists because this sweep also covers the 56 rows that are not
 * class-reachable, where the endpoint is literal text.
 */

/* --- the two delimiter-eater cells -----------------------------------------
 * Standalone, `[[.a.]]` and `[[=a=]]` are err 113 (collating elements and
 * equivalence classes are recognised and not supported). As the HIGH endpoint
 * of a range, the same text is err 150 (invalid range) instead: the
 * range-validity check runs before the not-supported check, so the endpoint
 * position changes which of two real errors surfaces. The model predicts the
 * standalone error, because that is what step 3 says.
 *
 * The LOW side does NOT deviate — `[[.a.]-z]` is 113, matching the model — so
 * the asymmetry is the finding, and pinning only the high side is what keeps
 * it visible. */
{ "[0-[.a.]]", "high-side range check (150) precedes the unsupported-construct "
               "check (113); the low-side cell reports 113 and agrees" },
{ "[0-[=a=]]", "as [0-[.a.]]: 150 at the endpoint, 113 standalone" },

/* --- one literal-text cell -------------------------------------------------
 * `(?[[a]])` is a group row, not class-reachable: inside a class it is plain
 * text. The model's rule "if `[S]` is rejected then the doorway was recognised
 * and S whole is the item" is what misfires — `[(?[[a]])]` is rejected (err
 * 122, unmatched parenthesis) but only because the embedded `]` closes the
 * class early and leaves a `)` outside it, which says nothing about a doorway.
 * The real cell is the descending range 0-'(', err 108.
 *
 * Pinned rather than modelled: teaching the extent scan to recognise this
 * would mean parsing class termination, and the cell is literal text on a row
 * that the class-position invariant assigns no value to. */
{ "[0-(?[[a]])]", "`[S]` is rejected for a reason unrelated to a doorway (an "
                  "embedded ] closes the class early), so the model treats all "
                  "of S as the item; the cell is really the range 0-'('" },
