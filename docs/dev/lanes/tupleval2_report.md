# Lane tupleval2 report: the tuple's parts, and first/rest with recursion (design only)

Deliverable: `docs/design/joint_condition.md` §4A revised (§4A.3 rewritten, §4A.11 new, every changed sentence
listed in §4A.10 and marked "[§4A.10, tupleval2]" in place). Evidence: `docs/dev/lanes/tupleval2_check.py` / `.out`.
No edit to `predicates_draft.md`, `plan.md`, `COND-FAMILY.md`, `src/`, `cli/`, `lib/`, `memfn/` or `tests/`.
Spellings are placeholders (D193 add. 4). Citations: `predicates_draft.md` rev 19 by line; `CF:n` =
`docs/design/plan_row_bodies/COND-FAMILY.md`. Every sentence not quoted from the owner is the lane's.

## STATE AT HANDOFF

STATE: complete. Branch lane/tupleval2, cut from lane/tupleval 46b3e371b (NOT on main). Premise test passed at
09:54 (`grep -n '^### 4A' docs/design/joint_condition.md` listed 4A.0..4A.10; `timeout 120 python3 -I
docs/dev/lanes/tupleval_check.py | tail -1` printed `TOTAL cases 47357 differ 0 engine-disagreements 0`). Rulings
file `tupleval2_rulings.md`: EMPTY at 09:54 and 09:58 (first WIP commit); ONE entry (its R-1, the owner's 09:58
words) at 10:02, 10:05 and at the last read before this report's commit; LAST ENTRY APPLIED: R-1 (09:58). It
WITHDREW the brief's "R-3 ... RULED ... tupleval's lean is OVERRULED"; the note was first revised on the brief's
reading (commit 94cfd1ca0), then re-revised on R-1 (this delivery): reaching the parts is OPEN, both positions laid
out, one question **tuple-parts**. Evidence run (from the worktree root): `timeout 120 python3 -I
docs/dev/lanes/tupleval2_check.py` -> `TOTAL cases 42079 differ 0 engine-disagreements 0` (libpcre2-8 10.46,
Python 3.14.4, 0.1 s). The check was sabotaged twice from scratch copies under
`/var/tmp/pcrec-pcrec/scratch/tupleval2/`: the `ge` expectation written `>`: 18 differ (exactly the subjects equal
to a bound); a clause's `==` row written `>=`: 5,535 differ. OWED RUNS: none. UNTESTED, labelled in the note: (B2)'s
product test cost; `$`-bound pairs (as before).

## RULINGS APPLIED

- 09:47 (brief R-1, kept): the colon tells the reference tuple `(h, m):` from the value tuple.
- 09:49 (brief R-2): his words "I meant left right in the expression sense around =  You could use them as you
  say". Applied: §4A.1's "only the right-hand one is a value" (his sides read as the colon's) restated on the
  binding sign's sides; §4A.8 R-1 (ii) restated; R-1 (iii) / **tuple-anywhere** marked ANSWERED YES.
- 09:50 (brief R-3): his "Yes" to "`(a, b) := lo` takes it apart ... with no index and no new operator". Applied
  as the owner's statement of position (B), NOT as a ruling, per 09:58.
- 09:52 (brief R-4, an idea): "functional style first/ rest binding with recursion": worked in §4A.11.
- 09:58 (rulings file R-1): "Nothing is set in stone. I'd like to hear it out. So It's the set that makes it an item
  so you can't break it apart without changing its meaning. Like 9:30, 10:00 broken apart is 9,10 and 30, 00 which
  is gibberish. Makes sense". Applied: §4A.3 lays out (A) and (B) fairly with sub-choices; first/rest's dependence
  stated; one question **tuple-parts**; nothing written as ruled. His example added to table (A) (2 pairs -> 4).

## REACHING THE PARTS, REVISED

§4A.3. Both positions keep: a MATCH's parts are named left of the colon and read as `$h`, `$m`; `lo[1]`, `lo.1` and a
`part(t, i)` built-in are errors.

(A) NO ACCESS (lane tupleval's lean): a tuple value is used whole. Strongest case, the owner's 09:58 reason: a tuple
value is a SET of tuples and the parts of a set are projections, which lose the pairing: his `9:30, 10:00` -> `9, 10`
and `30, 00` -> four times back, two never in it; `month_days` 365 -> 372 (7 subjects the table refuses);
`>= (9, 30)` over a day 870 -> 900 (table (A), Python set arithmetic; table (D) of tupleval engine-ran the month
case). Price: nothing new, nothing in the account needs a part; but a part is never usable alone, and first/rest
cannot be written.

(B) TAKING APART ON THE LEFT OF A BINDING: `(lo_h, lo_m) := lo`. Strongest case: the owner's own reading (09:49,
09:50); the draft's ruled-in-design left of `:=` (`predicates_draft.md:726-730`, CF:852), so no new mark, index or
operator; on one tuple it cannot change meaning; first/rest's step. Price: the left of `:=` enters the language
(§13 O51 parse) and on a SET it meets his objection, so a sub-choice: (B1) ONE TUPLE ONLY (each component one
string; `$` values of set-once labels give one tuple per match); (B2) one tuple or a PRODUCT, decided on the set
(exact round trip; `[(1, 2), (1, 3)]` passes; compile-time test decidable, cost UNMEASURED); (B3) any set,
projections (his "gibberish").

What the `[n]`/`.` rejection rests on now: `[n]` reads ENTRIES (§3.2 tool 1), so components would give it two
meanings; `.` needs component names (the record as a value, CF:866); under (A) no route exists, under (B) the
binding is the route ("no index and no new operator").

LEAN (the lane's): (B1). Held to (B1), the two positions differ only on ONE tuple: a set is never broken apart under
either (his 09:58 reason kept whole), one tuple, which puts back the same, can be (his 09:50 "Yes" kept where it
cannot change meaning). Out of phase 1 until a use; the one candidate is first/rest, whose own lean is "not now", so
the account runs as (A) in practice until then.

## FIRST AND REST WITH RECURSION

§4A.11, examples first. `(y, md...) := (2024, 2, 29)` gives `y = 2024`, `md = (2, 29)`; the rest of a pair is its
plain second entry (`(x)` is `x`, 4A.2), so recursion ends at a plain value and `()` is never needed. The value side
`(x, r...)` builds the product of x with r's components. The library:

    all((b, r...)) := (anything, all(r)...)        all(b) := anything        (anything := /[\s\S]*/)
    ge((b, r...))  := (> b, all(r)...) | (== b, ge(r)...)                     ge(b) := >= b
    gt, le, lt the same;  between(lo, hi) := ge(lo) & le(hi)   (unchanged)

Evidence (F): a small interpreter follows the clauses as written; k = 2, 3, 4 (225, 512, 1,296 subjects); four
orders at 4-5 bounds and between at 2-3 ranges: 40,279 cases; `padded` per component at k = 2: 1,800 cases; 0 differ
from Python integer tuple order, 0 engine disagreements; rows per order exactly k. (FS): the plain clause listed
first, refused k = 2, 3, 4; the rest without its mark, refused k = 3, 4 and harmless at k = 2 (same answer); recursion
on the whole, refused k = 2, 3, 4. No slip is silent.

Price: P1 a rest mark on the binding's left; P2 the same mark on the value side (one meaning, "the remaining
entries"); P3 a tuple of names in a definition head (no local bindings exist, §5.2); P4 several clauses for one name
chosen first-match by head SHAPE (§13 O21 generalised; one form would also serve E-DEPTH's literal heads); P5
termination by ARITY added to §7's literal-decrease rule (`predicates_draft.md:2192-2195`; G4 at `:477`). Not
needed: `()`, a size literal, an index, index arithmetic (rev 18's `lg(j, n, s, lo)` waits on O21 AND `s[n-j+1]`,
`predicates_draft.md:2620-2634`). It NEEDS **tuple-parts** (B); (B1) is enough (every bound is one tuple).

Against the built-in order: built-in = 1 new concept, first/rest = 5 (two widening open/ruled items) minus that 1;
first/rest removes the two-orders look-alike (`>= (9, 30)` becomes an error naming `ge`; table (O) of tupleval: 2,700
of 11,000 differ) and lets the library pad components without modifier-lift. §12 uses: the tuple compares at any
arity only; NOT E-DEPTH (a depth number; shares P4), E-LUHN (iterations, not tuples), E-CAL, E-IPV4 validity,
E-WEEKDAY/E-RFC/E-NEAR, the rest.

VERDICT (the lane's): HELPS AT A NAMED PRICE. Lean: keep the built-in order now (the owner's first criterion, "in
line with existing concepts", favours one concept over five for one family); record first/rest as worked and tested;
TRIGGER: a second any-arity tuple family the built-in cannot express. If he weighs the two-orders look-alike above
the concept count, first/rest is the clean way to remove it. Question **first-rest**.

## WHAT CHANGED IN THE NOTE

The full sentence list is §4A.10's tupleval2 block. In short: header and §4A opening (four owner entries quoted;
evidence named); §4A.0 (three example lines, one comment); §4A.1 (the binding sign's sides); §4A.2 (no `()` for
first/rest); §4A.3 (rewritten: (A), (B), (B1)-(B3), the `[n]`/`.` basis, the lean); §4A.4 (left of `:=` under (B);
two errors under (B); producer (4) points to first/rest); §4A.6 (two rows, one fix); §4A.7 (one row, one look-alike,
two count sentences); §4A.8 ((m4) OPEN; R-1 (ii), (iii)); §4A.9 (two dependencies); §4A.11 (new); Goals, §2, §7 item
10 (pointers); §8 (current ranked list; the older list kept for the record).

## CONSEQUENCES DERIVED BY THE LANE

Each is the lane's, not a ruling.
1. (Replaces tupleval's consequence 5.) Parts of a tuple VALUE: both positions refuse to break a SET apart under the
   lean (B1); they differ only on one tuple, and only first/rest needs that today.
2. The parts of a set of tuples are projections; the round trip is exact iff the set is a product, a property of the
   SET, not its spelling (table (A): `[(1, 2), (1, 3)]` exact; his `[(9, 30), (10, 0)]` 2 -> 4).
3. Dictionary order is definable in the language from first/rest, with exactly the built-in's k rows (table (F)).
4. With first/rest, `x` = `(x)` gives the base case for free: the rest of a pair is plain; no empty tuple.
5. Shape-chosen clauses (P4) and O21's literal heads are one first-match form; E-DEPTH and first/rest would share it.
6. Termination by arity is the same kind of syntactic check §7 already uses, with another measure.
7. Every library-author slip tried is a compile error at k >= 3 (FS); at k = 2 the missing rest mark is harmless.
8. O69 (3)'s trigger "a real use with four or more fields" is met by this note's CIDR list (table (R)) if the order
   were not built in.
9. A search result's groups (O54) and a tuple taken apart would be one meaning of the left of `:=`, under (B).

## QUESTIONS FOR THE OWNER

The note's full current ranked list (§8). Answered, not re-asked: **tuple-value**, **tuple-anywhere** (YES).
Each: reply either way.

1. **first-rest**. Example: `ge((b, r...)) := (> b, all(r)...) | (== b, ge(r)...)`, `ge(b) := >= b`, then
   `ip & ((a, b, c, d): between((10, 1, 128, 0), (10, 1, 131, 255)))` with `between := ge(lo) & le(hi)`; the
   comparison `>= (9, 30)` then an error naming `ge`. Your idea works (k = 2, 3, 4: 0 differ from integer order) and
   needs neither an empty tuple nor an index nor a size number. Forces: for it, one family of rules leaves the
   language for the library, and the `>= (9, 30)` vs `(>= 9, >= 30)` look-alike disappears; against, five new pieces
   (a rest mark used on both sides, names taken apart in a definition head, several clauses chosen by shape,
   termination by tuple length, and taking apart itself) against one sentence for the built-in order, for ONE family.
   Leaning: keep the built-in order now; first/rest recorded, trigger a second family that needs it.
2. **tuple-parts** (reopened, both sides). (A) a tuple is used whole, parts never taken apart: your 09:58 reason,
   "9:30, 10:00 broken apart is 9,10 and 30, 00". (B) `(lo_h, lo_m) := lo` takes ONE tuple apart: your 09:50 "Yes";
   then a SET is refused (B1), allowed only when it is a product (B2), or split into its parts (B3, the gibberish).
   Forces: (A) is free and nothing needs parts today; (B1) loses nothing (a set is still never broken apart) and is
   what first/rest needs; (B2)/(B3) widen for no case. Leaning: (B1), out of phase 1 until a use.
3. **set-arity**: a set of tuples is the rx kind with an ARITY, or a third kind? Example `[(9, 0), (17, 30)]`.
   Leaning: arity.
4. **unset-component**: minutes optional, is `10` in 9:30..11:00? Leaning: no (the tuple does not exist).
5. **joint-loops**: `list & ((h, m): >= (9, 30))` per item; sibling loops an error; the looped warning
   generalised. Leaning: yes to all three.
6. **two-orders**: `>= (9, 30)` and `(>= 9, >= 30)` both legal, different (2,700 of 11,000). Leaning: keep both;
   moot if first-rest is yes.
7. **modifier-lift**: `padded(>= (9, 0))` pads each component. Leaning: yes.
8. **colon-scope**: left of the colon a label (computed included); in a value tuple a binding, `$` for a label's
   value. Leaning: yes.
9. **record-is-product**: `(h: S, m: T)` explained as `((h, m): (S, T))`. Leaning: yes, as an explanation.
