# file29 report (sonnet): file review r29 (predspec20), process changes

## STATE AT HANDOFF
Branch lane/file29 from main 6d6ba12dd. Commits: c9836e342 (review r29 filed + index), the process-changes commit, plus
this report's commit (the branch tip). Rulings file docs/dev/lanes/file29_rulings.md: EMPTY at 16:50 on the box clock
(read before each commit and before this report). No build, no suite run (docs/skill text only). Nothing pruned; the
round dir /var/tmp/pcrec-pcrec/scratch/crit-predspec20 was only read.
OWED: none

## REVIEW FILED
- docs/dev/reviews/2026-11-16-r29-predspec20.md: the coordinator's draft with the header replaced ("dispositions RULED by
  the manager 2026-11-16, session 136"); under each group A-Q the manager's ruling from dispositions.md, summarized and
  labelled the manager's. Group A carries the 16:31 ADDENDUM: the owner's domain-scope words quoted verbatim, "ruled
  against the manager's lean"; the one-witness owner question is recorded as NOT relayed with the manager's per-condition
  reading. Verdict and lessons headings marked ACCEPTED.
- docs/dev/reviews/2026-11-16-r29-predspec20/: the five critic texts as `<lens>_findings.md` (changetab, fixind,
  simulate, ruling, census), verify.md, dispositions.md, process.md, and the round's own scripts prefixed by lens
  (sim_*.py, census_*.py, ruling_*.py, fixind_drill.py, verify_v4_define.py). Not copied: the `evidence/` chain (prior
  lanes' scripts, read-only copies), spans.json (157 KB scratch data), the ruling/work f1-f9 note files, __pycache__.
- Indexed in docs/dev/reviews/CLAUDE.md (now 11.5 KB; the four oldest-in-order memfn index lines r11-r13 and r1-spanarms
  moved to NOTES.md, section "lane file29"). check_claudemd_size.sh --all: within limits. No `plan.md:NNN` or spec line
  cite in the new files (grep clean).

## PROCESS CHANGES APPLIED
All dated 2026-11-16 r29, minimal edits in .claude/skills/pcrec-critic/SKILL.md: (1) §4 ruling-check row: re-check kept
readings when a revision withdraws one; (2) §4 simulate REAL MODE clause: also every worked table the revision adds;
(3) §4 simulate DOMAIN drill: condition-built and second-`&` equal-behaviour pairs; (4) §6.2: opus verifier for
interlocking semantic claims, same-root findings as one item; (5) §5 COMMON: brief from the subject's text, not the
record's paraphrase. Four lessons added at the top of docs/dev/guide/critics.md "Lessons from review rounds"; the
framework paragraph appended, dated, to docs/dev/meta/coordinator_framework.md.

## OPEN ITEMS
None. The review's group A rulings feed rev 21 (not this lane). Premise checks all passed.
