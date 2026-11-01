# Empty iterations of unbounded repeated groups in pcre2_match: further iterations and captures

Question: after an iteration of an unbounded repeated group matches the empty
string, does the interpreter (`pcre2_match`, not JIT, not DFA) ever start
another iteration? That includes the case where the next iteration is the m-th
mandatory one of X{m,}. And are captures set inside that empty iteration kept in
the reported match? Greedy, lazy and possessive forms are covered, and so are
group bodies that can also match a non-empty string.

Source: tag pcre2-10.46. Files read: src/pcre2_match.c, src/pcre2_compile.c,
src/pcre2_intmodedep.h, doc/pcre2pattern.3, testdata/testoutput2.

## Short answer

1. Mandatory iterations always run. X{m,} is unrolled at compile time into m
   copies of the group. Copies 1 to m-1 are plain, non-repeating groups. Copy m
   is entered unconditionally and carries the repeat. So iterations 1 to m always
   execute, even when every earlier copy matched empty. The empty test lives only
   at the repeating close of copy m, and it only decides whether iteration m+1
   is attempted. (READ)
2. Beyond the minimum, an iteration that ends without consuming anything ends
   the loop on that path. The greedy, lazy and possessive closes all go straight
   on to the item after the group, and none of them leaves a backtracking point
   that would try a further iteration. (READ, DOCUMENTED)
3. Captures set inside the empty iteration are kept. The capture is recorded at
   the group's close before the empty test runs, and the path then continues with
   that capture vector. A final empty iteration therefore overwrites the group's
   capture with an empty string at the current position. (READ, DOCUMENTED by a
   test)
4. "Empty" is judged per iteration attempt: the subject position at this
   iteration's close is compared with the position at its start. It is not
   judged by whether the body could match non-empty. A body like `(a|)` that
   ended empty on this path stops the loop. If backtracking later sends that same
   iteration down a non-empty path, the close then repeats normally. (READ)

## Where the iteration decision is made

### Compile side

The repeat compiler is pcre2_compile.c:7272-7330 and 7360-7660.

- X{m,} with m of 2 or more: the group is copied m times. The copying loop is at
  pcre2_compile.c:7444-7483. Only the close of the final copy becomes a
  repeating close; that step starts at pcre2_compile.c:7558. Earlier copies keep
  an ordinary, non-repeating close. (READ)
- X+ (m = 1): a single copy whose close repeats. No zero-repeat prefix comes
  before it, so the first iteration is mandatory. (READ, pcre2_compile.c:7272-7279)
- X* (m = 0): the same single repeating copy, with a "may be skipped" prefix in
  front of it. The greedy prefix tries the group first; the lazy prefix tries
  the rest of the pattern first. (READ, pcre2_compile.c:7405-7416)
- If the group could match the empty string, its opening opcode is switched to
  a variant that tells the matcher to remember where each iteration started.
  This happens only for the final, repeating copy (pcre2_compile.c:7604-7613).
  The flag is conservative: a group is treated as possibly empty unless every
  branch provably consumes at least one character. A repeated subroutine call
  is always treated as possibly empty (pcre2_compile.c:7324), and so is a branch
  containing (*ACCEPT). (READ, pcre2_compile.c:6100, 8446)
- Possessive (star, plus or {m,} followed by an extra plus): the final copy gets possessive open and close
  opcodes. When m is 2 or more, the whole run of copies is also wrapped in an
  atomic group. (READ, pcre2_compile.c:7615-7650)
- Atomic and script-run groups keep their own opening opcode and just get a
  repeating close (pcre2_compile.c:7591-7597). The matcher still records their
  start, so the same empty test applies to them. (READ)

### Match side: the group close

The handler for every group close is pcre2_match.c:6185-6432. In order:

1. It finds the start-of-group frame and, through it, the subject position where
   this iteration began (pcre2_match.c:6197-6206). Two kinds of group have no
   such frame: plain non-capturing groups proven never to match empty, and
   conditionals without the "may be empty" mark. For them the empty test is
   skipped; it is not needed. (READ)
2. A capturing group writes its start and end offsets into the current capture
   vector (pcre2_match.c:6382-6388). This happens unconditionally, before any
   repeat logic. (READ)
3. A possessive close copies the current state into the enclosing frame,
   including the subject position and the whole capture vector, and returns a
   special signal to the possessive loop (pcre2_match.c:6392-6403). (READ)
4. Greedy or lazy repeating close, when the iteration consumed something
   (pcre2_match.c:6405-6426):
   - Lazy: it first tries the rest of the pattern. If that fails, it jumps back
     to the group start for another iteration.
   - Greedy: it first tries another iteration. If that fails, it falls through
   to the rest.
   (READ)
5. A repeating close where the iteration consumed nothing behaves exactly like
   a non-repeating close. Matching carries on with the next item, and no
   backtracking point is pushed for a further iteration (pcre2_match.c:6428-6432).
   If the rest then fails, backtracking goes back into the body of the empty
   iteration, to its remaining alternatives or inner quantifiers. It does not go
   to a new iteration. (READ)

### Match side: the possessive loop

The possessive loop is pcre2_match.c:5395-5469. It records the subject position
before each iteration. When the body reports a successful close, it marks
"matched at least once". If the position has not moved, it stops looping and
continues after the group; otherwise it starts another iteration. The state the
close copied back, captures included, is what the loop continues with. So an
empty possessive iteration keeps its captures and ends the loop. The loop then
never backtracks into the group. (READ)

### Why captures survive, and when they do not

Every backtracking point gets a fresh frame, and the frame holds a copy of the
capture vector (pcre2_intmodedep.h:851-858, read). Going forward from the empty
close keeps the vector that already holds the empty iteration's capture.
Backtracking to an earlier point restores that point's older vector. A capture
set in an empty iteration is therefore lost only if the path that set it fails
and the engine backtracks past it. (READ for the mechanism; INFERRED for the
general statement.)

### What the man page promises

pcre2pattern.3:2217-2227 (DOCUMENTED) says that whenever an iteration of such a
group matches no characters, matching moves on to the next item instead of
repeating, and that backtracking into any of the iterations is still possible.
The code agrees. The page does not mention captures, and it does not say that
mandatory copies are exempt; the code shows both.

## Worked examples (from my reading; nothing was run)

Notation: group 1 is given as (start,end) offsets, or "unset".

Greedy `*`:
- `(a|)*b` on "ab": match 0-2. Group 1 = (1,1), the empty string. Iteration 1
  takes "a". Iteration 2 takes the empty alternative, which records (1,1) and
  stops the loop; then b matches. (INFERRED trace)
- `(a|)*b` on "b": match 0-1, group 1 = (0,0). (INFERRED trace)
- `(a|)*\d` on a long run of "a" followed by "4": group 1 is the empty string.
  This is DOCUMENTED by testdata/testoutput2:7533-7537, the only direct test
  evidence I found for "the empty last iteration's capture is kept".

Greedy `+`, where the body can also match non-empty:
- `(?:()|a)+b` on "ab": match 0-2, group 1 = (1,1). Iteration 1 first takes
  the empty alternative and records (0,0); the empty test stops the loop, and b
  fails at 0. Backtracking into iteration 1 takes "a", which restores the vector
  with group 1 unset. That close consumed something, so iteration 2 runs. Its
  empty alternative records (1,1) and stops the loop, and b matches. (INFERRED
  trace)

Lazy:
- `(?:()|a)+?b` on "ab": match 0-2, group 1 UNSET. Iteration 1 takes the empty
  alternative, records (0,0) and stops the loop; b fails at 0. Backtracking into
  iteration 1 takes "a", which discards the (0,0) capture. The lazy close tries
  the rest, and b matches at 1. The engine never tries "empty iteration, then
  an 'a' iteration", so the (0,0) capture is never part of a successful match.
  (INFERRED trace)
- `(a|)+?b` on "b": match 0-1, group 1 = (0,0). The empty iteration's capture
  is kept. (INFERRED trace)
- `(a|)*?b` on "b": the lazy prefix skips the group, b matches, group 1 unset.
  On "ab": skipping fails, then iteration 1 takes "a" and the rest matches.
  Group 1 = (0,1). (INFERRED trace)
- `(a|){2,}?b` on "ab": copy 1 takes "a" (0,1). Copy 2 is the mandatory,
  lazily repeating one: "a" fails, the empty alternative records (1,1) and stops
  the loop, and b matches. Group 1 = (1,1). (INFERRED trace)

Mandatory iterations after empty ones:
- `(a?){3,}b` on "ab": copy 1 takes "a" (0,1). Copy 2 is empty (1,1), and it
  still runs copy 3 because copy 2 is a plain group. Copy 3 is empty (1,1), and
  its repeating close stops there. b matches. Group 1 = (1,1). (INFERRED trace)
- `(a?){3,}b` on "b": three empty copies, all at (0,0); group 1 = (0,0).
  (INFERRED trace)
- `(a?){3,}b` on "aaaab": copies 1 to 3 take "a" each, ending (2,3). Copy 3
  consumed something, so it repeats: (3,4), then an empty iteration (4,4) stops
  the loop. Group 1 = (4,4). (INFERRED trace)

Possessive:
- `(a|)*+b` on "ab": iteration 1 is "a", iteration 2 is empty (1,1) and stops
  the loop. Group 1 = (1,1), the same as the greedy form. (INFERRED trace)
- The group `(?:()|a)` under the possessive plus quantifier (two plus signs), then b, on "ab": here the possessive form differs. At start offset 0,
  iteration 1 takes the empty alternative, the loop stops, and b fails at 0.
  The possessive group is never re-entered, so that start fails. At start
  offset 1, the empty alternative records (1,1) and b matches. Result: match
  1-2 ("b"), group 1 = (1,1). Compare the greedy `(?:()|a)+b`, which matches
  0-2. (INFERRED trace; worth confirming against libpcre2)
- `(a?){3,}+b` on "ab": the same copies as the greedy form, inside an atomic
  wrapper. Group 1 = (1,1). (INFERRED trace)

Summary of the forms: greedy, lazy and possessive all stop after an empty
iteration beyond the minimum, and all keep its captures. They differ only in
what happens when the rest of the pattern fails. Greedy and lazy can backtrack
into the empty iteration's body; possessive cannot.

## Not checked

- JIT and DFA matching (out of scope).
- Interaction with PCRE2_NOTEMPTY or PCRE2_NOTEMPTY_ATSTART beyond the
  whole-match check. I did not trace \K inside the group, or a group whose only
  content is a lookaround or a backreference.
- Bounded repeats X{m,n} with n finite. Their optional copies are nested
  non-repeating groups with no empty test, so they presumably repeat through
  empty matches up to n. (INFERRED, not traced.)
- Perl's behaviour on these patterns. None of the examples above was executed;
  each is a trace from my reading, and each should be confirmed with libpcre2
  before it becomes a test expectation.

## Cited by

(none yet; the manager fills this in when code leans on the note)

## Confirmed against libpcre2 10.46 (manager, 2026-11-01)

Run through libpcre2-8 with default options: `(a|)*b` on "ab" gives group 1 (1,1); `(?:()|a)+?b` on "ab" leaves group 1 unset; `(a?){3,}b` on "ab" gives group 1 (1,1).
