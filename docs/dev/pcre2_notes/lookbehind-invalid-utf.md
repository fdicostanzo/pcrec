# Variable-length lookbehind stepping back over an invalid byte (PCRE2_UTF + PCRE2_MATCH_INVALID_UTF), pcre2 10.46

Question: pattern `(?<*(.{1,3}))b`, UTF + PCRE2_MATCH_INVALID_UTF, subject bytes FF 61 62.
Does group 1 hold 1..2 ("a" only) or 0..2 (spanning FF)?

Paths are under the 10.46 tree. "Interpreter" means the pcre2_match.c matcher without JIT.

## Short answer

- Interpreter (pcre2_match.c), READ: group 1 is 0..2, i.e. it includes the invalid byte FF. Overall match is 2..3. The backward step of a variable-length lookbehind does not treat the invalid byte as a barrier, and the dot inside accepts FF as one character.
- JIT, READ: the code generated for the backward step does treat an invalid byte as a barrier, so the answer there should be 1..2 (INFERRED, not run).
- Documentation, DOCUMENTED: doc/pcre2unicode.3:462-468 promises the barrier behaviour ("a lookbehind assertion fails if it encounters an invalid sequence while moving the current point backwards"; an invalid sequence "acts as a barrier which no match can cross", and "does not match dot"). The interpreter's variable-length path does not honour that in this case. This is an apparent upstream inconsistency, not a pcrec decision.
- Vanilla vs patched 10.46: the copy's ChangeLog and NEWS (top entries, ChangeLog:1-120, NEWS:1-20) mention no fix in this area (10.46 is a security-only release per NEWS). The ChangeLog has no entry about the variable-length lookbehind bound. Anything after the tag cannot be known from this copy. A distribution patch or a later upstream could differ; the source cannot settle that.

## Mechanism, step by step (interpreter)

1. Fragmenting (READ, pcre2_match.c:7122-7222, 7945-8000). With PCRE2_MATCH_INVALID_UTF the subject is validated and split into valid fragments. The first validity failure sets the end of the current fragment just before the bad unit. For FF 61 62 the error is at offset 0, so the first fragment is empty and fails. The matcher then restarts at offset 1 (the first unit after the bad one, skipping stray continuation bytes), validates the rest (valid), and sets the "start of UTF checking" pointer to 1 (7980). The end of subject becomes the true end. The start-of-subject pointer used by the matcher stays at the real start of the whole subject, offset 0 (7266).

2. The fixed-length backward step (READ, 6068-6097): in UTF mode it moves back one character at a time, failing if the pointer is at or before the "start of UTF checking" pointer, and uses the skip-continuation-bytes helper after each unit. So for a FIXED-length lookbehind the checking-start pointer (offset 1 here) is a barrier: a two-character fixed lookbehind before the "b" fails.

3. The variable-length backward step (READ, 6112-6165): at the start of each branch it first goes back as many as the branch's maximum count of characters (3 here), one character at a time, using the same skip-continuation-bytes helper (which only skips bytes of form 10xxxxxx; FF is not such a byte so it counts as a one-byte character). The stop test compares against the start of the WHOLE subject (the real offset 0), not against the checking-start pointer. If it reaches the subject start having stepped fewer than the maximum but at least the minimum, it just lowers the maximum to what it stepped. It then tries the branch body going forward, and on failure moves forward one character at a time until the minimum is reached. Here: from offset 2, step to 1, step to 0, then at the subject start with 2 steps done (>= min 1), so maximum becomes 2 and the first attempt starts at offset 0.

4. The dot (READ, 4850-4856 area and the UTF branch of the greedy single-character repeat at roughly 4600-4640): in UTF mode, it advances one unit and then over continuation bytes; it never validates the unit it consumes. The only bound is the end of the current fragment on the right. So FF is consumed as one character. The greedy `.{1,3}` starting at 0 can reach 3 (FF, 61, 62), but the end-of-assertion check (5977-6000 region, 6283-6290 for the non-atomic lookbehind) requires the group to end exactly at the original position (offset 2) for a variable-length lookbehind; offset 3 fails, backtracking gives 2 characters ending at 2, which succeeds. The capture is therefore 0..2.

5. Non-atomic `(?<*` (READ, 6282-6286) behaves the same for this purpose; only the retry-on-backtrack differs from the atomic form.

6. Why the match is found at 2: the start optimisations are not needed to explain it; at start 1 the engine tries the lookbehind at 1 (steps back to 0 only, group 1 would need to end at 1; "a" is not "b" so the following b test fails) and then at 2 succeeds as above (INFERRED for the walk through start positions; the lookbehind result at 2 is READ).

## The JIT difference

READ (pcre2_jit_compile.c:4550-4580, 8645-8720): the JIT's one-character-backward helper in 8-bit UTF with invalid-UTF mode is documented in its own comment to leave the pointer unchanged on an invalid sequence and, when asked to, jumps to failure at a NUL-class result for an invalid sequence. The lookbehind code asks for that checking mode and compares the pointer to the subject start `begin`. So JIT fails the backward step when it meets FF, giving no 3-wide start; the lookbehind would only be able to step to 1, group 1 = 1..2 (INFERRED; I did not trace the invalid-sequence helper body beyond the jump set-up). So interpreter and JIT plausibly DISAGREE on this input in 10.46; which answer a given consumer saw depends on whether JIT was used (pcre2test uses JIT only when asked; PHP/others usually enable JIT).

## Concrete cases a test might use

- `(?<*(.{1,3}))b` on FF 61 62, PCRE2_MATCH_INVALID_UTF, interpreter: match 2..3, group 1 = 0..2 (READ).
- Same, JIT: expected match 2..3, group 1 = 1..2 (INFERRED).
- Fixed-length contrast `(?<=..)b` on FF 61 62: interpreter fails at 2 (checking-start pointer is 1, only one char available); consistent with the doc barrier (READ, step 2). A variable-length `(?<=.{2,3})b` or `(?<*.{2,3})b` on the same subject succeeds in the interpreter (READ, step 3) which is the inconsistency.
- Same subject with valid text (61 61 62) gives group 1 = 0..2 trivially; the only difference is the invalid byte.

## Not checked

- I did not run anything (not allowed). The JIT invalid-sequence helper and the JIT's start-of-subject register were not traced fully.
- Whether testdata contains a variable-length-lookbehind-with-invalid-UTF case: I searched testinput names only for the option string and found nothing decisive; not traced.
- Post-10.46 upstream history is outside the copy.

## Cited by

(none yet; the manager fills this in when code leans on the note)
