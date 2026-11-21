# COMMON brief — critic round covcap-r2 (DESIGN mode)

## Scope mandate (binding)
- You may READ only the pcrec repo (/home/pcrec/projects/pcrec, the review tree
  below) and pcrec-bench (/home/pcrec/projects/pcrec-bench).
- You WRITE only your own findings file (and scratch files) under
  /var/tmp/pcrec-pcrec/scratch/crit-covcap-r2/ — nothing anywhere else on the machine.
- READ-ONLY: never edit either repo, never commit, never run `make`, any test suite,
  `scripts/boxqueue`/`boxlock`, or any sweep over more than ~200 compiles. You MAY run
  the review tree's built compiler on single patterns (and `gcc` on its output into
  your scratch dir). Bound every command: `timeout 60 ...`.
- Kill nothing except your own processes, by PID.

## Subject
- Design: `docs/design/cover_cap.md` REVISION 2, at commit `06d373f45`
  (read it as `git -C /home/pcrec/projects/pcrec show 06d373f45:docs/design/cover_cap.md`;
  it is identical on main HEAD).
- A build would land on main HEAD `6259d6c7a`. No `src/`, `cli/`, `lib/` file changed
  between the two commits (memfn/ only gained an unrelated request R-44), so code cites
  are checked at the review tree below.
- REVIEW TREE (main HEAD, built): /home/pcrec/projects/pcrec/worktrees/crit-covcap-r2
  (binary `build/pcrec`). The design cites code at `75d365a0b`; any cited line that does
  not hold at the review tree is a finding.
- Plan row: `[COVER-CAP]` (locate with `grep -n '^- \[COVER-CAP\]' docs/dev/plan.md` ONLY;
  do not print neighbouring rows).
- Rulings: read decisions.md and plan.md via `git -C /home/pcrec/projects/pcrec show
  6259d6c7a:docs/dev/decisions.md` (never the live tree). D157 is at decisions.md
  `## D157`; D77, D80, D94, D146/D147, D153, D163 are cited by the design.

## Owner criteria in force (Frank's words, verbatim; their only other record is denied to you)
(a) 2026-11-15: "there are two kinds of spans. exact spans that can prove each position
is exactly as the rx requires and the engine does not need to retest, and hull positions
that show the position is possibly matching but not proven. the purpose of the hull
positions is to get better candidates but the work is thrown out. how far to go to get
these is a judgement call. i would say that if the span exceeds N positions, the hull is
not needed. the hull positions can be used to extend a short span and get something to
filter candidates."
(b) 2026-11-15: a span is a stretch of persistent simple byte classes; a branch ends it;
the kit can loop over repeated positions and can detect them by scanning the span
arguments it is passed (pcrec does not need to inform it).
(c) 2026-11-15: "why any bound at all? why the artificial constraint?" ... "agree. avoid
arbitrary tuning constants like that."
(d) D157: pcrec states facts to the kit and never presumes its method.

## Guide and cited documents (read what your lens needs)
- `docs/dev/guide/` (architecture.md: goals; coding.md; critics.md; style.md)
- `docs/design/kit_proof.md` (§1.1 cover_conj table, §R2.2), `docs/design/ctx_span.md`
  §11, `docs/design/offset_k_skip.md` §3.3, `docs/design/alt_normal_form.md`,
  `docs/spec/facts_listing.md` §4.1.2, `docs/spec/cli.md` §2.6, `docs/spec/match_api.md`
  §6.3.4, `docs/design/CLAUDE.md` (the three standing questions).
- Code: `src/facts/kset.c` (`pcrec_span_walk`, `sw_*`, `pcrec_kset_walk`), `src/facts/facts.h`
  (`MkLang`), `src/**/known.c` / `known.h` (cover conjuncts C1..C14, `kn_walk`,
  `cover_window`, `pcrec_cover_proof_diff`), `limits.def`, `memfn/` (`memfn.h`, window.c,
  `MF_WSPAN_POS`, `MF_WREACH`, `MF_MAX_FWD`), `tests/kitproof/` (cases.tsv, oracle.c).
  Find exact paths yourself with grep in the review tree.
- Census population code: `docs/dev/optloop/artrev/gen/census.py` (`bench_pop`, `corpus_pop`).
  The design's own census data and script are DENIED; recompute what you need on a
  small sample (<= 200 compiles).

## Run kit
- `/var/tmp/pcrec-pcrec/scratch/crit-covcap-r2/kit/facts.sh 'PATTERN' [flags]` prints
  `span_facts` and the `RX_DFA_SCAN` route ("cover" = the cover route) for byte and utf8.
  E.g. `ab|abc|ad` -> `2:97,[2]`, cover. `span_facts` value form: `L:set0,set1,...`
  (a number = one byte, `[n]` = a class of n bytes).
- Full listing: `build/pcrec -p rx --features all --emit-facts=byte,utf8 --pattern P`.
- Matcher: `build/pcrec -p rx --emit-main -o X.c --pattern P` then `gcc -O2 X.c`; deny
  the cover with `--memfn=no-window-search`. libpcre2 oracle source: `tests/kitproof/oracle.c`
  (python3 `re` is acceptable for the base tier; `\z` is python `\Z`).

## DENYLIST (do not open, grep or diff these; exclude them from EVERY grep/diff)
- `docs/dev/lanes/covcap*_report.md`, `covcap*_deliver.txt`, `covcap*_rulings.md` (main tree and any worktree)
- `docs/dev/reviews/2026-11-15-r2-covcap0*` (file and dir)
- `docs/dev/wake.md`, `docs/dev/owner.md`, `docs/dev/dev_journal.md` (whole file for you)
- `/var/tmp/pcrec-pcrec/scratch/` EXCEPT `crit-covcap-r2/` (in particular covcap*/, crit-covcap/, spanfacts/, audnight/, audpred/)
- `/var/tmp/pcrec-pcrec/scratch/crit-covcap-r2/.coord/` and other critics' files
- every other `worktrees/*` directory, job logs, the box queue, `git log` bodies (subject lines only)
- `git show` of earlier revisions of cover_cap.md (`e327a8b49`, `86e9d11f4`) — EXCEPT the fix-induced critic.
- Plain grep exclude string: `--exclude-dir=worktrees --exclude=dev_journal.md --exclude=wake.md --exclude=owner.md --exclude='covcap*' --exclude-dir='2026-11-15-r2-covcap0*' --exclude='2026-11-15-r2-covcap0*'`
- git pathspec excludes: `':!docs/dev/dev_journal.md' ':!docs/dev/wake.md' ':!docs/dev/owner.md' ':!docs/dev/lanes/covcap*' ':!docs/dev/reviews/2026-11-15-r2-covcap0*'`

## Output format
Your findings file does NOT exist yet: CREATE it as your FIRST action with headings
`# <LENS> — covcap-r2`, `## Findings`, `## PROBED-AND-HELD`, then APPEND each finding the
moment you have it, one append per finding. Each finding:
- id `<LENS>-n`; CONFIRMED (repro: input, command, observed vs expected) or SUSPECTED
  (what would confirm it); severity (answer / speed / size / maintenance / doc / design);
  effort; blast radius; cite (`file:line` or design §).
- A finding against a ruled D-row or owner criterion cites it and argues, or drops.
- PROBED-AND-HELD: what you tested that held, with case counts.
- If your Write is refused, SendMessage your findings to the coordinator at once marked
  "relayed"; never route around a refusal.
- When done, run `/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-covcap-r2 --deliver <your DELIVER file> <NAME>`
  and end only once it prints DONE. Final reply <= 150 words.
