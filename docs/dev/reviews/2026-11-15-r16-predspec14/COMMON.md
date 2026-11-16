# COMMON brief: critic round predspec14 (design, confirming re-check of rev 12 -> rev 14)

## Scope mandate (binding)
- Touch ONLY the two mandated repositories, /home/pcrec/projects/pcrec and /home/pcrec/projects/pcrec-bench, and
  ONLY READ them. You make NO edits to either repo, no commits, no worktrees.
- Write ONLY under your own lens directory `$R/<lens>/` where R=/var/tmp/pcrec-pcrec/scratch/crit-predspec14
  (your findings file and any scratch scripts). Nowhere else on the machine. Not /tmp.
- Read-only critic: NEVER run `make`, a test suite, `scripts/boxqueue`, `scripts/boxlock`, or any build. The owner's
  evening hold is in force until 01:00 box clock: small python3 scripts only, each under `timeout 120`.
- Nobody reads PCRE2 source (D181). Use the box's libpcre2-8 through its public API (ctypes; see
  `$R/evidence/predspec14_anchor.py` for a working wrapper you may import or copy) and python3 `re` as oracles.
  Run python as `python3 -I`, with your cwd your own lens dir.
- Pass patterns in single quotes or via a file; shell quoting eats backslashes.

## The subject (frozen)
- `docs/design/predicates_draft.md` rev 14, branch lane/predspec14, commit 195108b9404371c48b3614c20a1ab638019ad181.
  READ THE COPY: `$R/subject/predicates_draft_rev14.md` (read-only). The previous REVIEWED revision is rev 12
  (`$R/subject/predicates_draft_rev12.md`); the change under review is `$R/subject/rev12_to_rev14.diff`.
  Revs 13 and 14 are both unreviewed; the changelog at the top of rev 14 says what each claims to do.
- It is a DESIGN ONLY document: no build is proposed. NO readiness, cost or schedule lens; do not raise them.
- RULINGS RECORD: `$R/subject/COND-FAMILY_rulings.md` (main's docs/design/plan_row_bodies/COND-FAMILY.md at the
  freeze, main 38f6db8db). Line numbers there are the "CF:n on main" the draft cites. Every entry from line ~1026 to
  the end is a ruling or recorded idea that revs 13-14 fold. NOTE: the record contains one CORRECTION entry
  (it corrects the entry above it) and several "consequences drawn by the manager" / "the manager's reading" /
  "manager's note" passages that are explicitly NOT the owner's rulings. Only the owner's quoted words (and what he
  explicitly agreed to) are rulings. A design statement resting on a manager consequence rather than the owner's
  words is fair game for a finding. Do NOT read the live repo copy of COND-FAMILY.md or decisions.md (may move).
- Evidence the lanes committed (you may read and run them; they emulate rules on top of libpcre2 and python `re`,
  they are NOT pcrec): `$R/evidence/predspec13_anchor.py/.out`, `$R/evidence/predspec14_anchor.py/.out`,
  `$R/evidence/predspec14_census.py`. Run them only from your own lens dir, outputs redirected into it.
- TWO questions are OPEN with the owner: (1) **primitive-transforms** (the provided transforms that cannot be
  written as macro bodies: one pullback primitive under them, or keep them as named primitives; §2.7, §13 O67), and
  (2) **tuple-compare** (a fixed-size tuple compare for the first library; §13 O69). Judge the text under its
  stated leans; DO NOT raise the open questions themselves as findings. BUT every claim of the form "X is a plain
  macro with body B" and "X is NOT EXPRESSIBLE as a macro body" IS testable and in scope where your lens says so.
- Background the subject cites, readable in the repo at main (read-only): docs/design/CLAUDE.md (standing
  questions), docs/dev/guide/critics.md, docs/dev/guide/architecture.md. Ruling files (decisions.md, plan.md) via
  `git -C /home/pcrec/projects/pcrec show 0432001efaa4b66a0f75bb89718d72a2a2753ff2:docs/dev/decisions.md` only, never the live tree.

## Denylist (do NOT open, grep, git-show or diff these)
- every `docs/dev/lanes/predspec*` file (reports, briefs, deliver files) EXCEPT the evidence copies under `$R/evidence/`
- every `docs/dev/reviews/*predspec*` file and directory (all earlier reviews of this subject)
- `/var/tmp/pcrec-pcrec/scratch/crit-predspec12/` and any other `crit-*` round dir; `$R/.coord/`; other lenses' dirs under `$R`
- `docs/dev/dev_journal.md`, `docs/dev/wake.md`, `docs/dev/owner.md`, `memfn/docs/journal.md`
- `worktrees/` (every worktree, notably predspec12/13/14); job logs; the box queue
- `git log` bodies (subject lines only)
For a plain grep in the repo add: `--exclude-dir=worktrees --exclude-dir=reviews --exclude='predspec*' --exclude=dev_journal.md --exclude=wake.md --exclude=owner.md --exclude=journal.md`.
You should need nothing in the repo beyond the guide files above: the subject copies are self-contained.

## Output format
- Your findings file does NOT exist yet: CREATE it as your FIRST action with the headings `# <LENS> findings`,
  `## Findings`, `## PROBED-AND-HELD`, then APPEND each finding the moment you have it, one append per finding.
- Each finding: id `<LENS>-n`; CONFIRMED (with a repro: input, the exact command/script, observed vs expected) or
  SUSPECTED (what would confirm it); severity (answer / design / doc / maintenance); effort; blast radius; the
  subject's § and line in the rev 14 copy. A finding against an owner RULING cites the CF line and argues, or drops.
- End the file with PROBED-AND-HELD: what you checked that held, with case counts.
- Then run: `/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-predspec14 --deliver $R/<lens>/<lens>_deliver.txt <lens>`
  and end only after it prints DONE (fix what it reports otherwise).
- If writing your findings file is REFUSED, SendMessage your findings to the coordinator at once, marked relayed,
  or return them as your final text; never route around a refusal.
- Final reply at most 150 words.
