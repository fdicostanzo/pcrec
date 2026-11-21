# COMMON brief — critic round covcap-r4 (DESIGN mode, the LAST re-check before a stage-1 build go)

## Scope mandate (binding)
- You may READ only the pcrec repo (/home/pcrec/projects/pcrec, including the review tree
  below) and pcrec-bench (/home/pcrec/projects/pcrec-bench).
- You WRITE only under YOUR OWN lens directory
  /var/tmp/pcrec-pcrec/scratch/crit-covcap-r4/<lens>/ (findings file, DELIVER file, scratch).
  Nothing anywhere else on the machine. Not /tmp.
- READ-ONLY: never edit either repo, never commit, never run `make`, any test suite,
  `scripts/boxqueue`/`boxlock`, or any sweep over more than ~300 compiles. You MAY run the
  review tree's built compiler and the round's trace compiler on single patterns, `gcc` on
  their output into your own dir, and the libpcre2 oracles below. Prefix heavy commands with
  `nice`, bound every command with `timeout 120` or less.
- Kill nothing except your own processes, by PID.

## Subject (frozen)
- Design: `docs/design/cover_cap.md` REVISION 4 at commit `5ae776b25` (identical on main HEAD
  `bf16c278f`). Read it as `git -C /home/pcrec/projects/pcrec show 5ae776b25:docs/design/cover_cap.md`.
  Revision 3 is `6630261a7` (only the fix-induced lens may read it / diff against it).
  Plan row `[COVER-CAP]`: locate with `grep -n '^- \[COVER-CAP\]' docs/dev/plan.md` ONLY
  (never print neighbouring rows). The build unit a go is asked for is STAGE 1 only (§3.5).
- A build would land on main HEAD `bf16c278f`. Between rev 3's review tree `917a3c522` and
  `bf16c278f` the only code-area change is `tests/mech/sabotages/S486_dfahat_t_widened.sh`
  (one line); no `src/`, `lib/`, `cli/`, `memfn/`, `tests/kitproof/` change. Every code cite
  is checked at the review tree; a cite that does not hold there is a finding.
- REVIEW TREE (main HEAD, built): /home/pcrec/projects/pcrec/worktrees/crit-covcap-r4
  (`build/pcrec`, `build/pcrec-harness`). Never `cd` into it: absolute paths or `git -C`
  (a `( cd X && ... )` subshell is fine).
- TRACE compiler (same src built with -DPCREC_CAND_TRACE):
  /var/tmp/pcrec-pcrec/scratch/crit-covcap-r4/trace/pcrec. `PCREC_KIT_PROOF_TRACE=1` prints
  the cover decision's `KITPROOF` record (`why` or `cover`, `k`).
- The design cites lane scratch (covcap3/covcap4/covcap5 census, prototype, rowcost.py,
  diff10.py) and the covcap5 report: DENIED to you. Recompute what you need on a small
  sample; a number whose command is not runnable from what the design gives is a finding
  only if a stage-1 BUILD needs it.
- Rulings: read decisions.md / plan.md only via
  `git -C /home/pcrec/projects/pcrec show bf16c278f:docs/dev/decisions.md` (frozen at
  decisions.md `bf8319fb8`, plan.md `9e63a8b23`). Owner criteria: D198 (`## D198`) (a)-(g).
  Also cited: D157, D77, D80, D94, D146/D147, D153, D163, D198.
- Owner amendment in force (D198 (g), 2026-11-15): "Practically, we might need a max span
  length then. I don't want edge cases to ruin the concept. Something sufficiently high
  that it's rarely seen but that doesn't become a memory problem."
- Manager rulings that produced rev 4 (from the committed review r6, quoted): R-1 DELETE the
  new limit PCREC_MAX_EXACT_SPAN; the existing PCREC_ANCHORED_MAX_STATES (4096) IS the max
  exact span on this route; rev 4 must quote that row's label/derivation (or say it is
  missing and propose label text, not invent a derivation), say what happens past it (no
  anchored machine, pattern runs as today), remove outcome 4, plant (e), the a{4097}
  witness, and correct the owner-facing "no cliff" text. R-2 walk stops at min(L, first
  accept); compile-cost row gets a worst case with its command. R-13 cover_window bounds
  order: a named stage-1 build item. R-14 NOTED/PLAN.

## Inputs
- Committed reviews (allowed): `docs/dev/reviews/2026-11-15-r5-covcap-r2.md` +
  `2026-11-15-r5-covcap-r2/`, `docs/dev/reviews/2026-11-15-r6-covcap-r3.md` +
  `2026-11-15-r6-covcap-r3/`.
- Guide: `docs/dev/guide/` (architecture.md, coding.md, critics.md); `docs/design/CLAUDE.md`.
- Cited docs: `docs/design/kit_proof.md` (§1.1, §6.4 X0), `docs/design/kit_proof/x0/`,
  `docs/spec/facts_listing.md`, `docs/spec/cli.md` §2.6, `docs/spec/match_api.md` §6.3.4,
  `docs/dev/history/abi_changelog.md`.
- Code (grep the REVIEW TREE by absolute path): `src/gen/known.c` (`kn_walk`, `kn_step`,
  `kn_liveness`, `cover_conj[]`, `pcrec_cover`, `cover_window`, `window_bounds_check`,
  `pcrec_cover_proof_diff`), `src/gen/known.h`, `src/facts/kset.c`, `src/facts/facts.h`,
  `facts.def`, `facts.c`, `facts_dump.c`, `facts_derive.h`, `src/core/limits.def`,
  `src/core/limits.h`, `src/compile.c` (or wherever `cc_anchored` lives), `memfn/`
  (`MF_WSPAN_POS`, `MF_WREACH`, `MF_MAX_FWD`), `tests/kitproof/`, `tests/mech/` (`kitproof`
  arm, sabotage rows), `tests/` expectations reading `span_facts`.

## Run kit (/var/tmp/pcrec-pcrec/scratch/crit-covcap-r4/kit/; reused from round r3, repointed)
- `kit/kp.sh 'PATTERN' [pcrec flags]`: per byte/utf8, the trace build's `KITPROOF` record(s)
  (LAST = the compile itself), the `RX_DFA_SCAN` route (`"cover"` = cover route), today's
  `span_facts`. E.g. `ab|abc|ad` -> cover k=2.
- `python3 -I kit/machine.py 'PATTERN' [cap] [-u] [flags]`: applies the per-depth set rule
  (rows' live next-byte sets equal = exact; first accept = span) to the EMITTED anchored
  machine (`-fno-scan-edge`) via `docs/dev/kvcensus/kvdfa.py` `lang()`, any depth cap
  (default 5000). Python of the same rule over every start; not kn_walk, not libpcre2.
- libpcre2 10.46 oracles: `kit/oracle` (stdin `FLAGS<TAB>PATTERN_HEX<TAB>SUBJECT_HEX`, FLAGS
  `-`,`i`,`u`; out: match at every startoffset + find-all) and `kit/x0pcre`
  (docs/design/kit_proof/x0/x0pcre.c header). python3 `re` OK for base tier.
- Matcher: `build/pcrec -p rx --features all [-e utf8] --emit-main -o X.c --pattern P`, then
  `gcc -O2 X.c`; deny the cover with `--memfn=no-window-search`.
- kp.sh makes temp dirs under `kit/tmp/`; otherwise make temp dirs under your lens dir.

## DENYLIST (do not open, grep or diff these; exclude them from EVERY grep and diff)
- `docs/dev/lanes/covcap*_report.md`, `covcap*_deliver.txt`, `covcap*_rulings.md` (main tree
  and every `worktrees/covcap*`)
- `docs/dev/reviews/2026-11-15-r2-covcap0*` (file and dir)
- `git show`/diff of cover_cap.md revisions other than rev 4 `5ae776b25` — EXCEPT the
  fix-induced lens, which may read rev 3 `6630261a7` and `git diff 6630261a7 5ae776b25 --
  docs/design/cover_cap.md`
- `docs/dev/wake.md`, `docs/dev/owner.md`, `docs/dev/dev_journal.md` (whole file for you)
- `/var/tmp/pcrec-pcrec/scratch/` EXCEPT `crit-covcap-r4/` (in particular covcap3/, covcap4/,
  covcap5/, crit-covcap/, crit-covcap-r2/, crit-covcap-r3/, spanfacts/, audnight/, audpred/)
- `/var/tmp/pcrec-pcrec/scratch/crit-covcap-r4/.coord/` and the other lens's dir
- every other `worktrees/*` directory, job logs, the box queue, `git log` bodies (subject
  lines only)
- Plain grep exclude string: `--exclude-dir=worktrees --exclude=dev_journal.md
  --exclude=wake.md --exclude=owner.md --exclude='covcap*' --exclude-dir='2026-11-15-r2-covcap0*'
  --exclude='2026-11-15-r2-covcap0*'`. Grep code in the REVIEW TREE by its absolute path
  (`/home/pcrec/projects/pcrec/worktrees/crit-covcap-r4/src` etc.), with the same excludes
  minus `--exclude-dir=worktrees`.
- git pathspec excludes: `':!docs/dev/dev_journal.md' ':!docs/dev/wake.md'
  ':!docs/dev/owner.md' ':!docs/dev/lanes/covcap*' ':!docs/dev/reviews/2026-11-15-r2-covcap0*'`

## Output format
Your findings file is `<lens dir>/<lens>.md` (e.g. `readiness/readiness.md`); your DELIVER file `<lens dir>/<lens>_deliver.txt` exists. The findings file does NOT exist yet: CREATE it as your FIRST action with headings
`# <LENS> — covcap-r4`, `## Findings`, `## PROBED-AND-HELD`, then APPEND each finding the
moment you have it, one append per finding. Each finding:
- id `<LENS>-n`; CONFIRMED (repro: input, command, observed vs expected) or SUSPECTED (what
  would confirm it); severity (answer / speed / size / maintenance / doc / design); effort;
  blast radius; cite (`file:line` at the review tree, or design §).
- A finding against a ruled D-row, owner criterion or manager ruling cites it and argues, or drops.
- PROBED-AND-HELD at the end: what you tested that held, with case counts.
- If your findings-file Write is refused, SendMessage your findings to the coordinator at
  once marked "relayed"; never route around a refusal.
- When done, run `/home/pcrec/projects/pcrec/scripts/lanecheck --dir
  /var/tmp/pcrec-pcrec/scratch/crit-covcap-r4 --deliver <your DELIVER file> <NAME>` and end
  only once it prints DONE. Final reply at most 150 words.
