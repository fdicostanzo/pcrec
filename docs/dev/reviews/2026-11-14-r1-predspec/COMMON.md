# COMMON brief: critic round crit-predspec (design mode), 2026-11-14

## Scope mandate (binding)
You work ONLY in the pcrec repo (/home/pcrec/projects/pcrec) and, read-only, pcrec-bench
(/home/pcrec/projects/pcrec-bench). You EDIT NOTHING in either repo: no commits, no files, no `make`, no
suites, no worktrees. The ONLY place you write is your own files in the round dir
/var/tmp/pcrec-pcrec/scratch/crit-predspec/ (your findings file, plus a scratch subdir named after your
lens id, e.g. `q1r/`). Never /tmp. Never anywhere else on the machine. Subagents you launch (if any) inherit
this mandate. You are a READ-ONLY CRITIC.

## Subject (frozen)
- `docs/design/predicates_draft.md` rev 2 at commit ae8f8a968edf805477d08e9d97dca175aa6d90ed. Read it via
  `git -C /home/pcrec/projects/pcrec show ae8f8a968:docs/design/predicates_draft.md` (not the live tree).
- Design only: a preliminary SPECIFICATION of the predicate language ([COND-FAMILY] #6). No code, no build
  proposal. SYNTAX IS PLACEHOLDER (the owner rules semantics; spelling later); do not file spelling taste as
  findings, EXCEPT where a spelling makes look-alike forms behave differently (that is the owner's ranked
  criterion, below).
- Rulings frozen at main d5a7529a03dab519f0f6f8695fbe6ceaad3f2cad. Read every ruling file via
  `git -C /home/pcrec/projects/pcrec show d5a7529a0:PATH`:
  - `docs/design/plan_row_bodies/COND-FAMILY.md` = THE OWNER'S RULINGS RECORD for this subject (dated notes;
    the LATEST note on a topic wins). You may and should read it.
  - `docs/dev/decisions.md` D196 (+ addenda 1, 2): intersection semantics, ruled. `grep -n 'D196'` it.
  - `docs/design/cond_family.md` (survey rev 0, D193) and `docs/design/cond_family_syntax_survey.md`:
    older background the subject cites.
  - `studies/andspike/` (CLAUDE.md, spanoracle.py, predicates.py): the D196 X & Y oracle spike (read-only).
- §13 of the subject ALREADY LISTS known contradictions (C1-C28) and open items (O1-O25). A finding that
  only restates one adds nothing: cite the id and add a CONSEQUENCE, a witness, or a recommended
  resolution, or drop it.

## Owner criteria in force (from COND-FAMILY.md, read the notes themselves)
1. RANKED FIRST for this design (2026-11-14 "Q1 critic framing", last note of COND-FAMILY.md):
   LOOK-ALIKE CONSISTENCY / INTUITIVE BEHAVIOUR: forms that look like they should do the same thing must do
   the same thing; a rule whose effect a user cannot predict (e.g. context silently making a predicate
   fail) is a defect EVEN WHEN FORMALLY SOUND. Owner's words: "complex context could cause predicates to
   just not work and it's not clear how the obscure rules impact it. Rx is already hieroglyphics ... that's
   why it was so important to me that things that look like they should do the same thing actually do."
2. NO ALPHABETIC OPERATORS OR STATEMENT KEYWORDS; a word is always a NAME (function, label, binding)
   (COND-FAMILY.md, Q6 + Q9 note, 2026-11-14).
3. `&` IS EXTENSIONAL on every rx/array: membership depends only on the language; two spellings of one
   language behave the same (COND-FAMILY.md, 2026-11-14 note starting "Agreed. RULE: `&` is extensional").

## The question of the round (Q1, the subject's tentative foundation choice, §11 "CONTEXT-MARKED SETS")
- MODEL A (the draft, TENTATIVE): a pattern denotes a set of (left context, span, right context) TRIPLES;
  plain patterns ignore the contexts; `^ $ \b` and regular lookarounds constrain them; `&` intersects
  triples; a label condition's value is the label's span WITH its context inside the match.
- MODEL B (the alternative): patterns stay STRING SETS (value-scoped: a pattern used as a set means the
  strings it matches entirely, alone); context assertions make a SEPARATE, context-dependent KIND, composed
  by D196's IN-CONTEXT intersection (the right operand checked on the exact span with the real subject
  around it, as studies/andspike's spanoracle does by default).
- Both are as stated here; where a rule's meaning under a model is underdetermined, SAY SO and give the two
  readings rather than picking one silently.

## Tools (read-only use)
- Oracle kit (libpcre2 10.49, in-context vs isolated D196 `&`):
  `python3 -I /var/tmp/pcrec-pcrec/scratch/crit-predspec/kit/q.py` (prints usage). Examples:
    q.py find '(?<=\$)\d+' 'a $12 b 34 $5'            -> [(3,5,'12'), (12,13,'5')]
    q.py and '(?<= )\w+' '^S\w*' 'x Sab'              -> None        (in-context: ^ fails mid-line)
    q.py and '(?<= )\w+' '^S\w*' 'x Sab' --isolated   -> (2,5) 'Sab' (value-scoped)
  In-context = Model-A-like / Model-B's D196 composition; --isolated = value-scoped string sets.
- The existing compiler, read-only: /home/pcrec/projects/pcrec/build/pcrec (main's build; NEVER run make).
  Single compiles only, output under YOUR scratch subdir: `build/pcrec --help`;
  `build/pcrec -p rx --emit-main -o DIR/out.c --pattern 'PAT'` then `gcc -O2 -o DIR/a DIR/out.c`. Use it
  only to check a claim about today's PCRE semantics or automaton size (e.g. `size`, or the emitted C's
  state tables). Bound every run: `timeout 60 ...`. At most ~100 compiles per critic.
- Plain grep over the repo: ALWAYS add these excludes:
  `--exclude='predspec*' --exclude='predx*' --exclude=wake.md --exclude=owner.md --exclude-dir=.coord`
  For git grep / git diff add pathspecs
  `':!docs/dev/lanes/predspec*' ':!docs/dev/lanes/predx*' ':!docs/dev/wake.md' ':!docs/dev/owner.md'`.

## Denylist (paths excluded from EVERY read, diff and grep)
docs/dev/lanes/predspec_report.md, docs/dev/lanes/predspec2_report.md, docs/dev/lanes/predx_report.md, any
docs/dev/lanes/predspec* or predx* file, any docs/dev/reviews/ file on predicates, docs/dev/wake.md,
docs/dev/owner.md, the session transcript, other critics' files in the round dir, the round dir's `.coord/`,
`git log` bodies beyond subject lines, job logs, other worktrees, the box queue. The subject cites
"predx S2/C15/..." ids: those live in a DENIED report; work from the subject's own text and COND-FAMILY.md.
If you need a fact that seems to live only in a denied file, say so in your findings (FREEZE NOTE), do not
read it.

## Output format
- Your findings file DOES NOT EXIST YET. CREATE IT AS YOUR FIRST ACTION with these headings:
  `# <LENS ID> findings: crit-predspec`, `## Findings`, `## PROBED-AND-HELD`, and write INCREMENTALLY:
  APPEND EACH FINDING TO YOUR FILE THE MOMENT YOU HAVE IT, ONE APPEND PER FINDING.
- Each finding: id `<LENSID>-n`; CONFIRMED (with a repro: the rule text by §, the input program/subject,
  the command if any, observed vs expected) or SUSPECTED (what would confirm it); severity (answer /
  speed / size / maintenance / doc / design); effort; blast radius; § cited. A finding against a ruled
  item (OWNER RULED / RULED / D196) cites the ruling and argues, or drops.
- `## PROBED-AND-HELD`: what you checked that held, with counts (rules examined, cases run).
- When done, run:
  `/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-predspec --deliver /var/tmp/pcrec-pcrec/scratch/crit-predspec/<NAME>_deliver.txt <NAME>`
  and end only after it prints `lanecheck: DONE rc=0` (fix what it names otherwise). Final reply at most 150
  words.
- If a Write of your findings file is REFUSED, SendMessage your findings to the coordinator (`crit-predspec`)
  at once, marked relayed; do not route around the refusal.
