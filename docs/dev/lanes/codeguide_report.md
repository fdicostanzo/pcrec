# codeguide — THE WIRED CODING GUIDE (2026-09-17, lane codeguide, opus)

Branch `lane/codeguide`, based on `main` at `8e5816d2`. Docs only — nothing
under `src/`, `tests/` or `docs/spec/`; no `make`, no suite, no build.

## Delivered

| file | change |
|---|---|
| `docs/dev/coding_guide.md` | NEW, 271 lines — the guide |
| `CLAUDE.md` | +1 situation-index row (write/change C → read the guide first) |
| `docs/dev/lanes/BOILERPLATE.md` | +1 process rule (a code-writing lane reads it before its first edit), placed immediately above the existing "before writing/altering any CHECK" rule |
| `docs/dev/CLAUDE.md` | +1 Files entry for the new file |

Commits: `b9f1e0d3` (the guide), `8314c23f` (the wiring). Not merged, not pushed.

## Shape taken, and why

The charter's six content areas became six sections, but the ORGANIZING
decision was to write **rules, not findings** — every sentence is something a
writer does or does not do, with the finding cited in parentheses rather than
narrated. That is what keeps it at 271 lines against a source corpus of ~1,200
lines of synthesis plus twelve lens reports.

Three deliberate choices worth the manager's eye:

**1. `[wave N]` markers, exactly as the brief asked, and they are load-bearing
in BOTH directions.** Three rules carry one (§2.2 `sb_fragf`, §2.4
`pcrec_ast_visit`, and §2.4's 75-hand-written-walks count). Each is written so
the rule is complete and correct TODAY and the marker says what replaces it —
e.g. §2.2 states the `PCREC_MAX_EMIT_NAME_LEN` obligation as the live rule and
"do not add a 49th [literal-sized buffer]", then names `sb_fragf` as what
retires the class. A reader who ignores the marker still does the right thing;
a reader who acts on an unbuilt primitive cannot, because the guide never tells
them to. The maintenance footer says the marker is deleted and the rule
restated when the wave lands.

**2. The do-nots (§6) are stated as temptations, not as a record.** The
collation's §5 is a 220-line evidence list; a writer will not read it. §6 keeps
the six a writer is actually likely to violate, each with the one-sentence
mechanism that makes it wrong (the `atomic.c` merge deletes two plant sites AND
the `-Wswitch` alarm; the rung table would have to carry the emitted CFG), and
points at collation §5 for the rest.

**3. §1.2 is stated as the RULE the brief asked for**, in the form that would
have prevented L8-F1: *every `StrBuf` the `Job` owns gets `.cx = &cx` as soon
as the `Job` exists*, followed by "Not 'the four buffers': the comment said
four, there were six." The count is present only as the incident.

## Verification done

No suite is runnable for a docs change, so the verification here is CITATION
verification — every `file:line` in the guide was opened on this branch's own
tree, not copied from a report:

| cite | checked |
|---|---|
| `src/core/compile.c:756-762` | the attachment comment + the four `.cx` writes, verbatim |
| `src/opt/mrl.c:18-24` | the two-units/exhaustive-switch rule's home |
| `src/opt/atomic.c:22-36` | the K20 spine rule + the `u.call.body` back-edge decline |
| `src/core/compile.c:595-691` | the `volatile`/`-Wclobbered` block |
| `src/core/limits.def:134` | `PCREC_MAX_EMIT_NAME_LEN = PCREC_MAX_PREFIX_LEN + 96`, K38 in its own `where` text |
| `src/core/internal.h:62-67` | the five `sb_*` declarations, exactly the five named |
| `src/gen/emit_vm.c:940` | `vm_slot_expr`'s definition; its header text quoted verbatim |
| `src/gen/emit_dfa.c:1965` | `.abi = 26` — the guide states the CURRENT value |
| `src/gen/emit_dfa.c:80` | `emit_comment_safe_byte`'s signature (**corrected from :81** after the check) |
| `tests/harness/run.sh:213` | `GENCFLAGS="${GENCFLAGS:--O1 -std=gnu11 -Wall -Wextra -Werror}"` |
| `Makefile:1171-1174` | `make strict` adds `-Werror -Wshadow`, which is what "promoted by `make strict`" means for `-Wswitch` |

One citation moved (`emit_dfa.c:81` → `:80`); everything else resolved as
written. The five-question rubric and the anti-perversion clause are quoted
verbatim from `code_review_criteria_draft.md` (RATIFIED), including ADDENDUM 1's
extract-first loop, restated as §4.1.

## Findings — three things the distillation surfaced

**F1 — the guide cannot state a "current" `abi` number without becoming a
staleness site, and it does anyway, deliberately.** §3.1 says *"`abi` is **26**
today"* with the file:line. The alternative (pointing at the source without a
value) makes the rule unreadable — a writer needs to know what to grep for. The
number is therefore a KNOWN drift point: it goes stale at the next abi event,
and the D76/D94 ritual's own "every reader of the number, found by grep" sweep
will find it, which is the correct outcome. Flagged so nobody treats the
staleness as a defect in the guide's design.

**F2 — two of the review's rules are stated nowhere in the tree's own comments
and the guide is now their only home.** (a) EP2's `irsb` finding — the four
byte-identity gates compare the `.c` artifact and NO gate reads the `--emit-ir`
listing, whose only comparator is `tests/codegen/run_ir_listing.sh`. (b) EP2
§3.5's anchor cost model — `replace.py` matches whole-file/line-agnostic, so
relocation is free and re-indentation is what breaks. Both live in a lens report
on a parked branch and in this guide, and nowhere else. If the lens reports land
under `reviews/lens_reports/` at merge that is two homes; if they do not, this
guide is the single home for two facts that govern every future emitter wave.
Worth the manager's decision either way.

**F3 — the charter's "escape pattern-derived text in emitted comments" rule is
narrower than the incident that produced it, and the guide widens it.** Lane
`cmtfix`'s finding is TWO hazards, not one: `*/` (closes the comment) and `/*`
(gcc's `-Wcomment` under `-Wall`, which the harness's own `GENCFLAGS` promotes
to an error), the second reachable with no `*/` anywhere in the file. A guide
stating only the first would let a writer pass their own reading and fail the
harness. §3.2 states both, names the `*prevp` threading that makes the
cross-call case work, and cites `run.sh:213` for why `-Werror` is not optional.

## Not done / not in scope

- No `make` of any kind (the brief forbids it; the change compiles nothing).
- The guide does not duplicate `learnings.md` §3 — §5 points at it and adds only
  the review's five new instances, per the brief.
- `docs/dev/reviews/2026-09-17-code-review.md` is UNCOMMITTED in the main tree at
  this writing; the guide cites it by path as its provenance. If it lands under a
  different name the guide's header line needs the one-word fix.

## Validation status

**COMPLETE for what a docs-only change can carry**: all eleven `file:line`
citations opened and verified on this branch, one corrected; the two verbatim
quotations (the five questions, the anti-perversion clause) diffed against the
ratified criteria. Nothing owed. No suite run, none applicable.
