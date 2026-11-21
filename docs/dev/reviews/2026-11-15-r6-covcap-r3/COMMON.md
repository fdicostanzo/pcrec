# COMMON brief — critic round covcap-r3 (DESIGN mode, a re-check of a revised design before a build go)

## Scope mandate (binding)
- You may READ only the pcrec repo (/home/pcrec/projects/pcrec, including the review tree
  below) and pcrec-bench (/home/pcrec/projects/pcrec-bench).
- You WRITE only under YOUR OWN lens directory
  /var/tmp/pcrec-pcrec/scratch/crit-covcap-r3/<lens>/ (your findings file, your DELIVER
  file, your scratch). Nothing anywhere else on the machine. Not /tmp.
- READ-ONLY: never edit either repo, never commit, never run `make`, any test suite,
  `scripts/boxqueue`/`boxlock`, or any sweep over more than ~300 compiles. You MAY run the
  review tree's built compiler and the round's trace compiler on single patterns, `gcc` on
  their output into your own dir, and the libpcre2 oracles below. The box is busy: prefix
  heavy commands with `nice`, bound every command with `timeout 120` or less.
- Kill nothing except your own processes, by PID.

## Subject (frozen)
- Design: `docs/design/cover_cap.md` REVISION 3 at commit `6630261a7`. Read it as
  `git -C /home/pcrec/projects/pcrec show 6630261a7:docs/design/cover_cap.md` (identical on
  main HEAD). Plan row `[COVER-CAP]`; locate it with `grep -n '^- \[COVER-CAP\]'
  docs/dev/plan.md` ONLY (never print neighbouring rows). The build unit a go is asked for
  is STAGE 1 only (§3.5).
- A build would land on main HEAD `917a3c522`. No file under `src/`, `lib/`, `cli/`,
  `memfn/`, `tests/kitproof/` changed between the design's read commit `4ccd97ca7` and
  `917a3c522`, so every code cite is checked at the review tree; a cite that does not hold
  there is a finding.
- REVIEW TREE (main HEAD, built): /home/pcrec/projects/pcrec/worktrees/crit-covcap-r3
  (`build/pcrec`, `build/pcrec-harness`). Never `cd` into it: use absolute paths or
  `git -C` (a hook blocks `cd worktrees/...`; a `( cd X && ... )` subshell is fine).
- TRACE compiler (the same tree built with -DPCREC_CAND_TRACE):
  /var/tmp/pcrec-pcrec/scratch/crit-covcap-r3/trace/pcrec. `PCREC_KIT_PROOF_TRACE=1` makes
  it print the cover decision's `KITPROOF` record (`why` or `cover`, `k`).
- The design cites the covcap3/covcap4 lanes' scratch (census, prototype, diff10.py):
  those are DENIED to you. Recompute what you need on a small sample. The prototype of rev 3
  does not exist for you: rev 3's rule must be APPLIED, not run (see the run kit).
- Rulings: read decisions.md / plan.md only via
  `git -C /home/pcrec/projects/pcrec show 917a3c522:docs/dev/decisions.md` (never the live
  tree; rulings frozen at decisions.md `bf8319fb8`, plan.md `9e63a8b23`). The owner's
  criteria are D198 (`## D198`), quoted below; D157, D77, D80, D94, D146/D147, D153, D163
  are cited by the design.

## Owner criteria in force (D198, Frank's words; read the row itself for (b)-(f))
(a) "there are two kinds of spans. exact spans that can prove each position is exactly as
the rx requires and the engine does not need to retest, and hull positions that show the
position is possibly matching but not proven. ..."
(c) "why any bound at all? why the artificial constraint?" ... "agree. avoid arbitrary
tuning constants like that."
(d) "... given an rx, kit proves the quick stretch out some distance. if its the whole rx,
then great, done. if its some fraction, then the proven parts are considered done and the
rest is an engine. ..."
(g) NEWER than the previous round, amending (c): "Practically, we might need a max span
length then. I don't want edge cases to ruin the concept. Something sufficiently high that
it's rarely seen but that doesn't become a memory problem."

## Guide, cited documents and code (read what your lens needs)
- `docs/dev/guide/` (architecture.md: goals; coding.md; critics.md).
- `docs/design/kit_proof.md` (§1.1 the cover table, §6.4 X0), `docs/design/kit_proof/x0/`,
  `docs/spec/facts_listing.md` (§4.1, §4.1.2¶7c, §4.1.3, §4.4), `docs/spec/cli.md` §2.6,
  `docs/spec/match_api.md` §6.3.4, `docs/design/CLAUDE.md` (the three standing questions),
  `docs/dev/history/abi_changelog.md`.
- Code: `src/gen/known.c` (`kn_walk`, `kn_step`, `kn_liveness`, `cover_conj[]` C1..C14,
  `cc_exact`, `pcrec_cover`, `cover_window`, `pcrec_cover_proof_diff`), `src/gen/known.h`,
  `src/facts/kset.c` ("THE SPAN SLICE", `pcrec_span_walk`, `pcrec_kset_walk`),
  `src/facts/facts.h` (`MkLang`, `MkEnd`), `src/facts/facts.def`, `src/facts/facts.c`,
  `src/core/limits.def`, `src/opt/scanedge.c`, `memfn/` (`MF_WSPAN_POS`, `MF_WREACH`,
  `MF_MAX_FWD`, `MF_MAX_SPAN_POS`), `tests/kitproof/` (cases.tsv, run_cover.sh, reach.sh,
  oracle.c), `tests/mech/` (the `kitproof` arm, S1131, S1149). Find paths by grep in the
  review tree.
- Census population code: `docs/dev/optloop/artrev/gen/census.py` (`bench_pop`,
  `corpus_pop`).

## Run kit (/var/tmp/pcrec-pcrec/scratch/crit-covcap-r3/kit/; checked before briefing)
- `kit/kp.sh 'PATTERN' [pcrec flags]`: for byte and utf8, the trace build's `KITPROOF`
  record(s) (a compound pattern prints one per part; the LAST is the compile itself), the
  `RX_DFA_SCAN` route (`"cover"` = the cover route), and today's `span_facts` value
  (`L:set0,set1,...`; a number = one byte, `[n]` = a class of n bytes). E.g.
  `ab|abc|ad` -> cover k=2, `2:97,[2]`; `a{30}` -> `exact/producer-short`, `24:97,...`.
- `python3 -I kit/machine.py 'PATTERN' [cap] [-u] [pcrec flags]`: applies the per-depth
  set rule (rows' live next-byte sets equal at a depth = exact; first accepting depth =
  span) to the EMITTED anchored machine compiled `-fno-scan-edge`, via
  `docs/dev/kvcensus/kvdfa.py` `lang()` with any depth cap (default 5000). It is a python
  implementation of the same rule over the table form (seeded machines: over every start),
  NOT `kn_walk` and NOT a libpcre2 control. E.g. `a[xy]c|b[xy]d` -> span 3, exact 2,
  counterexample `axc`/`bxc`.
- libpcre2 10.46 oracles (built from the tree's sources):
  `kit/oracle` (tests/kitproof/oracle.c: stdin `FLAGS<TAB>PATTERN_HEX<TAB>SUBJECT_HEX`,
  FLAGS `-`, `i`, `u`; out: match at every startoffset + find-all) and `kit/x0pcre`
  (docs/design/kit_proof/x0/x0pcre.c; see its header). python3 `re` is acceptable for the
  base tier (`\z` is python `\Z`).
- Matcher: `build/pcrec -p rx --features all [-e utf8] --emit-main -o X.c --pattern P`,
  then `gcc -O2 X.c`; deny the cover with `--memfn=no-window-search`.
- Make your own temp dirs under your lens directory (or `kit/tmp/`), never /tmp.

## DENYLIST (do not open, grep or diff these; exclude them from EVERY grep and diff)
- `docs/dev/lanes/covcap*_report.md`, `covcap*_deliver.txt`, `covcap*_rulings.md` (main tree
  and every `worktrees/covcap*`)
- `docs/dev/reviews/2026-11-15-r2-covcap0*` (file and dir)
- `docs/dev/reviews/2026-11-15-r5-covcap-r2*` (file and dir) — EXCEPT the fix-induced and
  readiness critics, who are given it as input
- `git show` of earlier revisions of cover_cap.md (`06d373f45`, `86e9d11f4`, `e327a8b49`) —
  EXCEPT the fix-induced critic (rev 2 `06d373f45` only)
- `docs/dev/wake.md`, `docs/dev/owner.md`, `docs/dev/dev_journal.md` (whole file for you)
- `/var/tmp/pcrec-pcrec/scratch/` EXCEPT `crit-covcap-r3/` (in particular covcap3/,
  covcap4/, crit-covcap/, crit-covcap-r2/, spanfacts/, audnight/, audpred/)
- `/var/tmp/pcrec-pcrec/scratch/crit-covcap-r3/.coord/` and the other critics' lens dirs
- every other `worktrees/*` directory, job logs, the box queue, `git log` bodies (subject
  lines only)
- Plain grep exclude string: `--exclude-dir=worktrees --exclude=dev_journal.md
  --exclude=wake.md --exclude=owner.md --exclude='covcap*' --exclude-dir='2026-11-15-r2-covcap0*'
  --exclude='2026-11-15-r2-covcap0*'` (+ `--exclude-dir='2026-11-15-r5-covcap-r2*'
  --exclude='2026-11-15-r5-covcap-r2*'` unless your lens is given it). Grep the REVIEW TREE
  (`worktrees/crit-covcap-r3`) by its absolute path when you grep code.
- git pathspec excludes: `':!docs/dev/dev_journal.md' ':!docs/dev/wake.md'
  ':!docs/dev/owner.md' ':!docs/dev/lanes/covcap*' ':!docs/dev/reviews/2026-11-15-r2-covcap0*'`
  (+ `':!docs/dev/reviews/2026-11-15-r5-covcap-r2*'` unless your lens is given it)

## Output format
Your findings file does NOT exist yet: CREATE it as your FIRST action with headings
`# <LENS> — covcap-r3`, `## Findings`, `## PROBED-AND-HELD`, then APPEND each finding the
moment you have it, one append per finding. Each finding:
- id `<LENS>-n`; CONFIRMED (repro: input, command, observed vs expected) or SUSPECTED
  (what would confirm it); severity (answer / speed / size / maintenance / doc / design);
  effort; blast radius; cite (`file:line` at the review tree, or design §).
- A finding against a ruled D-row or owner criterion cites it and argues, or drops.
- PROBED-AND-HELD at the end: what you tested that held, with case counts.
- If your findings-file Write is refused, SendMessage your findings to the coordinator at
  once marked "relayed"; never route around a refusal.
- When done, run `/home/pcrec/projects/pcrec/scripts/lanecheck --dir
  /var/tmp/pcrec-pcrec/scratch/crit-covcap-r3 --deliver <your DELIVER file> <NAME>` and end
  only once it prints DONE. Final reply at most 150 words.
