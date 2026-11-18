# archdense report: architecture note for the dense-hit remedy of [REQ-PAST-LAST] ([ARCH-STEP] pilot)

## STATE AT HANDOFF

Lane archdense (opus), branch lane/archdense. T = 57fcb5737dff37bd97429fb1e889ca0233d12e10 (main at launch; every
command in the note runs at T). The note is at `docs/design/dense_hit_arch.md`, STATUS DRAFT, and it is committed.
This lane did architecture only: nothing under src/, cli/, lib/, memfn/, tests/ or scripts/ was edited, the register
was not edited, no make, no suite, no timing, no queue job. The main tree's `build/pcrec` was run read-only twice
(`timeout 60`, output under `$PCREC_TMPDIR/scratch/archdense/`) to show the emitted retry text. Rulings file
`docs/dev/lanes/archdense_rulings.md`: empty at every read (at start, before the commit, before this report); last
R-n applied: none.
Premise test passed: `git grep -n "handoff-attempts-unbounded" $T -- src docs/spec | head` gives 6 lines, and
`git merge-base --is-ancestor f6365477c $T` exits 0.
Stop rule: it did NOT fire. NOTE 1's "the LAST occurrence ... ONCE" (a method) is ruled out by NOTES 2-3. The WHAT is
shared by all three: stop past the last occurrence, no per-hit re-ask on dense hits, no losing case. The note says
this and asks the owner to confirm it under **lookahead-home**.
OWED: none

## FORM AND SITE COUNT

FULL form. The site map has 13 rows. Five are existing decision sites the feature changes: S1 (the two re-entering
FIRST rows of `cand_rows[]`), S4 (`emit_req_landmark_move`, the shared re-entry text with its branches), S6 (the
kit presence site's second use), S8 (the `req_parts_in_whole` conjunct) and S9 (the deny column, public bit 46).
Two mechanisms are added: a weaker question at the presence site (S6, U1), and a source for a system constant (S7).
Classes: ROW 3 (S1, S8, S9), SHARED 1 (S4), WIDEN 1 (S6), NEW-SEAM 1 (S7), AS-IS 7 (S2, S3, S5, S10-S13; S3 turns
WIDEN if the design keeps two re-entry forms).
One remodel lands first: U1, the presence site's reply contract widened from "the leftmost hit" to the question the
caller needs. It is a kit seam event, S, with zero movers until a consumer asks. Its shape waits on
**lookahead-home**. The note carries the proposed R-n text; this lane filed nothing. The demotion half waits for
register row 15 (internal deny word, riding [FLAG-DEMOTE]).

## REGISTER ROWS PROPOSED

- P1 (REMODEL, open): one home for "where the search resumes after a failure". It is answered three ways today: the
  VM attempt loop's re-entry (FIRST's `CandUse.reenter`), the forward scan's re-entry (NEXT `handoff-reentry`) and the
  hybrid retry (RETRY rows, `adaptive-dense`'s step block). Rules: Notice siblings; One home per question; Act
  through the row. Event: a second re-entry form selectable on any of the three, or [START-DENSE], or a K105/K88 fix.
  Size M, no-mover. Deletes: the `reenter` bool, the consumer branch in the shared text, and the VM-only route's
  private retry spelling.
- Looked up and not carried, each with its reason in the note: rows 1, 2, 3, 6a, 6c (noted deviation, L, its events
  are [VMREC]/H-FLAGS), 7b, 9, 10, 12 (A-SEAM: its trigger list names [REQ-PAST-LAST]; not carried because no
  `CandUse` field changes; the trigger is restated), 12 (A-PLAN, H-FLAGS, H-LADDER), 13, 19. Row 15: the demotion
  half JOINS [FLAG-DEMOTE].
- No noted-deviation row is proposed (the note recommends no deviation).

## OPEN QUESTIONS FOR THE OWNER

- **lookahead-home**: does pcrec's attempt loop own the block look-ahead and its size B, or does the kit? TODAY
  pcrec decides when to re-ask (`tuning.md` §2.41¶7a), and the kit answers "the leftmost occurrence from here".
  EXAMPLE: `[^@ ]+@x` under `--engine=vm` over 1 MB of ` @x` asks about every 3 bytes. LEANING: the kit owns how the
  position is obtained, B included (B is a system fact, and D146 keeps those out of pcrec). pcrec owns the compare
  and the stop. Also: confirm that NOTE 3 replaces NOTE 1's "LAST occurrence ONCE" as a method.
- **streaming-meaning**: "also helps with streaming": subject streaming, which is parked ([SUBST-STREAM] deferred;
  `match_api.md` §5.2¶6, no streaming state), or the instruction-stream architecture of docs/design/stream/? EXAMPLE:
  a chunked search of `[^@ ]+@x` can look ahead only within the current chunk. LEANING: subject streaming. B comes from
  the page size alone today, and the chunk is stated when streaming re-opens (D77).
- **scan-reentry-too**: does the remedy also reach the DFA forward scan's re-entry? It shares the same text
  `emit_req_landmark_move`. EXAMPLE: K105, `[a-y]\d{0,100}:` over ':'-dense digits at x1.537. LEANING: not in this
  feature. The forward scan stays byte-identical until K105's measurement, and a consumer branch would fire P1's trigger.
- **gate-comparator**: is "no case slower" measured against today's rows, the plain loop, or both? EXAMPLE:
  `[^@ ]{1,5}@x` with one `@x` every 4 KB: today each re-ask jumps about 4 KB, and a block form could lose that jump.
  LEANING: both. The speed gate covers today's rows, and the no-loss NOTE covers demotion.
- **split-deny**: may the attempt rows leave `-fno-req-handoff` (bit 46) while the DFA-route `handoff` row keeps it
  (the audit keeps the bit for K88)? EXAMPLE: after a no-loss verdict, `-fno-req-handoff` would no longer turn off
  `[^@ ]+@x`'s VM re-entry. LEANING: yes, through [FLAG-DEMOTE]'s internal deny word.

## SKILL FRICTION

Places where the skill (`.claude/skills/pcrec-architect/SKILL.md`) or `docs/dev/guide/architecture.md` was unclear,
wrong or missing something on this pilot. Neither file was edited.

1. D-ROW LOOKUP IS DORMANT. Section 4.3 says to read the "Revisit when" triggers of every D-row naming a site "via
   `scripts/entry -g` on the file or function". At T, `scripts/entry D157` (and D144, D146, D147, D195) prints
   "profile decisions dormant (unit 1)", and `-g` does not search decisions. I read decisions.md by hand (awk on the
   heading). The step as written cannot be run with the tool it names.
2. THE CLASS LIST HAS NO "CONDITIONAL" FORM. S3 (`CandUse.reenter`) is AS-IS if the design replaces the per-hit form,
   and WIDEN if it keeps two forms selectable. The skill wants "exactly one" class and forbids algorithm decisions,
   but the class here depends on a design choice. I used AS-IS with the condition and the remodel that follows. A
   "CONDITIONAL <class> on <design item>" spelling would make this checkable.
3. SHARED FOR A SITE THAT IS ALREADY SHARED. The self-check says every SHARED row appears under "Remodels" or as a
   register row. S4 is already the one home: nothing needs remodelling, only a rule binding the design (do not fork
   it per consumer). Nothing in the skill says what to write for "SHARED, already satisfied".
4. REMODEL vs THE FEATURE'S OWN SEAM CHANGE. U1 (widening the kit's reply contract) is the feature's first unit, but
   it is classified WIDEN, so the skill calls it a remodel, and "a remodel with an empty deletes list names another
   reason or is dropped" fits badly. The skill does not separate reshaping existing code for the feature from the
   feature's own new seam fact, which by definition deletes nothing.
5. REQUIREMENTS THAT NAME A METHOD. The owner's NOTE 3 names a method (blocks, B from the page size), while D157 and
   the rule "Across the kit boundary" forbid naming a method across the seam. Who owns the method is then an
   architecture question (lookahead-home). The skill's REQ-OPEN covers requirements that are not stable, but not
   requirements that are stable and pick a method whose home the architecture has to decide.
6. THE GATE'S COMPARATOR. The template's remodel line names the gate ("no existing regex gets slower"). When a
   requirement states its own comparator (here "the plain loop"), the skill does not say to name both. The note
   handles it under Goals and as an owner question.
7. INPUT AMBIGUITIES IN THE BRIEF (manager-side, for BRIEF_TEMPLATE.md rather than the skill). (a) "[REQ-HANDOFF] row"
   does not exist at T (`scripts/entry REQ-HANDOFF`: no item; the rows are [REQ-HANDOFF-L1] and [REQRUN-VM], both in
   plan_completed). (b) "known_issues.md's handoff row": there is no row for this loss; the related rows are K88 and
   K105. (c) "docs/design/stream/ ... ties this to the stream end state": that directory is the INSTRUCTION-stream
   architecture, while the owner's "streaming" reads as SUBJECT streaming (owner question streaming-meaning).
8. THE PARAGRAPH-FORM TRIGGER COUNTS SITES THE FEATURE TOUCHES, BUT NOT SITES IT ONLY SHARES TEXT WITH. S12 (the
   forward scan's re-entry) is not a site the feature intends to change, yet it is reached through S4's shared text.
   The skill does not say whether such a site counts toward the two-site trigger. I did not count it (count 5 without
   it, so the form is not affected).
9. A CLAUDE.md SIZE TRAP OUTSIDE THE SKILL. docs/design/CLAUDE.md was at 12,237 of 12,288 bytes. BOILERPLATE requires
   the new file's line, so I trimmed the header sentence by about 40 bytes to fit (12,286 after). The next lane that
   adds a note there will hit the limit. That directory guide needs a move to NOTES.md (a manager item; not done here).
10. TEMPLATE WITHOUT THE STANDING QUESTIONS. docs/design/CLAUDE.md asks every design note for GOALS and the three
    standing questions. The architect's template has "Goals served" (the tier-1 goals) and no standing-question
    section. Whether an architecture note under docs/design/ owes them is not stated. I treated the measurement
    regime as a design hand-off.

## COMMANDS

All at T = 57fcb5737 (from the worktree root; `T=57fcb5737`):
- `git -C worktrees/archdense rev-parse --show-toplevel`; `git rev-parse HEAD` gives T.
- `scripts/entry REQ-PAST-LAST -l 2`; `scripts/entry LANDWALK -l 1`; `scripts/entry FLAG-DEMOTE -l 2`;
  `scripts/entry VMREC -l 1`; `scripts/entry START-DENSE -l 1`, `K88-HANDOFF-DENSE`, `PRIOR-COST-UNIFY`, `ENG-TACTICS`,
  `FIT-RUNG-ORDER`, `REQ-HANDOFF-L1`, `REQRUN-VM`, `SUBST-STREAM` (`-l 1`/`-l 2`); `scripts/entry REQ-HANDOFF` (no item).
- Decisions, by hand because the profile is dormant: `awk` on `^## D144|D146|D147|D157|D195` in docs/dev/decisions.md.
- The premise: `git grep -n "handoff-attempts-unbounded" $T -- src docs/spec | head`; `git merge-base --is-ancestor
  f6365477c $T`.
- The site map: C1-C17 as listed in the note, each `git grep -n ... $T -- PATHS` with its hit count.
- The tests that bind the code: `git grep -l -E "landmark_position|handoff-attempts|REQ-PAST-LAST|emit_req_landmark_move|pcrec_emit_req_attempt_reentry" $T -- tests scripts`.
- The emitted witness (main tree binary, read-only): `timeout 60 build/pcrec -p rx --engine=vm -o $S/unb.c --pattern
  '[^@ ]+@x'` and the same with `'[^@ ]{1,5}@x'` (S = `$PCREC_TMPDIR/scratch/archdense`), grepped for
  `REQ_HANDOFF|landmark_position|handoff_position`.
- Spec reads: `grep -n s2-41 docs/spec/tuning.md`, giving §2.41¶1-¶10; match_api.md §6.3.7¶11 and §5.2¶6.
- Kit seam: `grep -n "ret_pred\|MF_H_ASSIGN\|head_max\|on_miss_leaves" memfn/include/memfn.h`; memfn/docs/requests.md
  R-30, R-41; memfn/docs/responses.md lines with "R-30".
- The register at T: `git show $T:docs/dev/guide/architecture.md`, register section, grepped for the site files and tag;
  docs/design/stream/roadmap.md §1, A-SEAM, A-HYB, H-LADDER, H-FLAGS.
- The size check: `wc -c docs/design/CLAUDE.md` gives 12,286 (limit 12,288, scripts/check_claudemd_size.sh).
