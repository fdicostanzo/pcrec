# COMMON brief — critic round crit-vlb3 (DESIGN mode, SHORT RE-CHECK), 2026-11-06

Read this whole file before your per-lens prompt's question. `R` below means
`/var/tmp/pcrec-pcrec/scratch/crit-vlb3` (spell it out in commands).

## What this round is
A short RE-CHECK of a revised design, and the LAST check before the owner's stage-1 BUILD GO. Rev 3
re-spells rev 2's loop (§5.1) in the "cursor-rung" shape on an owner ruling. Earlier rounds you MAY
read: `docs/dev/reviews/2026-11-05-r3-vlookbehind.md` and `docs/dev/reviews/2026-11-05-r6-vlookbehind-recheck.md`
(each with its RULING block) and their directories (critic texts, verify.md, COMMON, process.md), and the
merged study `docs/design/vlookbehind_pieces.md` (its §6 is where the cursor-rung shape comes from).
Do not assume rev 3's claims (what it fixed, deleted, measured) are true: that is what you check.
Keep it SHORT: the subject is rev 3's DELTA (every `[r-cursor]` mark, the REVISION 3 block, §5.1,
§5.1a, §5.1b, §5.1c, §5.5, §5.6, §6, §7, §10, §16c). Rev 2's unchanged text was reviewed in r6.

## Scope mandate (binding)
- Touch ONLY the pcrec repo (/home/pcrec/projects/pcrec) and, READ-ONLY, pcrec-bench
  (/home/pcrec/projects/pcrec-bench). You EDIT NEITHER repo. You write only under your own
  directory `R/<your-lens>/`. No other files anywhere (no $HOME, no /tmp, no system config).
- Read-only critic: never run `make`, any test suite, `scripts/boxqueue`, `scripts/boxlock`,
  `scripts/battery.sh`, or anything heavy. The box is shared (kit gate jobs hold the box lock; another
  critic round runs concurrently): run every compile, probe and simulation under `nice -n 19`.
  Single-pattern `build/pcrec` compiles, `gcc` of one generated file, the oracle probes and small
  C/python programs of your own are fine (keep pcrec compiles under ~200 total; a python simulation
  over a few million cells is fine, keep it under ~10 CPU-minutes). Run python with `python3 -I`.
  If a script you run writes temp files, set `PCREC_TMPDIR=R/<your-lens>` for it.
- Bound anything that may hang: `timeout 120 <cmd>` (GNU timeout on this box).
- Kill only your own processes, by PID (never `pkill -f`/`pgrep -f`).
- CLEAN-ROOM WALL (D181): nobody opens the pinned PCRE2 source copy, or any PCRE2 source anywhere.
  PCRE2 facts come from public docs (`man pcre2pattern`, `man pcre2api`, `man pcre2unicode`) and from
  the INSTALLED libpcre2-8 10.46 used as a library. A question only PCRE2's CODE can answer: write it
  under a heading "Questions for a pcre2-reader"; do not answer it.

## Subject (frozen)
- Design: `docs/design/vlookbehind.md` REV 3 (PROPOSED), the doc's own commit
  `febde6edd2b27622f2dffc68202b27c23654b0d7`; byte-identical on main HEAD
  `e20dee230d09a528969a9c44df912c7db5598df6` (the merge). Frozen copy: `R/subject_vlookbehind.md` —
  READ THIS COPY; cite its § numbers and line numbers.
- A build would land on main HEAD `e20dee230`. The review tree, built there:
  `/home/pcrec/projects/pcrec/worktrees/crit-vlb3` (`build/pcrec`, `build/libpcrec.a`). Read every piece
  of code the design cites IN THIS TREE (never the live main tree: main moves tonight). No file under
  src/, lib/, cli/, tests/, docs/spec/ differs between `febde6edd` and `e20dee230`. Cited code (file,
  function, field, operand, enum member, comment) that does not say what the design says is a finding.
- Client design in force at the freeze: `docs/design/stream/arev.md` rev 1 (commit `b4878cb6a`, same
  on main HEAD); frozen copy `R/client_arev_rev1.md`. The subject's §16c tail cites it as "main at
  0f7d79795" (the merge of the same content). Read it only where rev 3 names a seam with it.
- Rulings files: read `docs/dev/decisions.md` and `docs/dev/plan.md` ONLY as
  `git -C /home/pcrec/projects/pcrec show e20dee230:docs/dev/decisions.md` (same for plan.md, and for
  any other doc you want at the freeze). Find a plan row by `grep -n '^- \[TAG\]'` on that output and
  read that row and its own indented continuation lines only.

## Rulings in force at the freeze
Owner (Frank):
1. Owner Q1 = (A): today's fixed-width lookbehind bytes stay, via the declared one-length row (§5.1b).
2. Owner Q2: the 65535-character branch ceiling rides stage 1.
3. The 255 cap stays the default (accept-set policy; a setting waits for [IFACE-PUSH]).
4. Backreferences inside a lookbehind are stage 2.
5. The fixed-tail hoist and the backward span count stay HELD.
6. 2026-11-06: the cursor-rung shape, because it is always sound ("if it's able to always be true then
   do it; if it's occasionally true then it should use a decision table").
Manager (2026-11-06; these answer the doc's §13 Q5 and Q6):
7. New MEMBERS of existing closed lists (`VmSeek`, `VmLocalKind`) are row additions and do NOT wait for
   [VMREC] (only a new record KIND would); but [VMREC] must list them.
8. `LO_i` takes the span-loop LOW slot family; the per-slot legend and listing text it costs are owed
   by the build.
Standing project rules that bear here: general mechanisms, not special cases; no parallel mechanisms;
build only under a measured need (D77); in-flight refactors outrank optimizations (D153); selections
are declared first-match tables; compatible with PCRE2 unless it is a PCRE2 bug (D26 + addendum); a
contract change carries its spec hunk in the same change (D80); emitted-scaffolding changes are an abi
event with every reader found by grep (D76/D94).

## Guide and cited documents (read at the freeze commit)
- Guide: `docs/dev/guide/{architecture,coding,style,critics}.md`, `docs/dev/learnings.md` §3.
- Design docs: `docs/design/vlookbehind_pieces.md` (§6), `docs/design/lookaround_design.md`,
  `docs/design/stream/{manifesto,roadmap}.md`, `docs/design/utf8_design.md` §2.6 (ill-formed subjects).
- Spec: `docs/spec/pattern_language.md`, `docs/spec/limits.md` §3/§3.1, `docs/spec/match_api.md`.
- Code the design cites (in the review tree; locate by grep — the design's names may be wrong, which
  is a finding): `src/gen/emit_vm.c` (the lookbehind emitters, `vm_goto`, `vm_cost_*`, slot counting,
  the K134 trail checkpoint), `src/gen/vm_stmt.h` (`VmKind`, `VmSeek`/`VSK_BACKSTEP`, `VmLocalKind`,
  `slotx`), the renderer, the encoding seam (`$_back_step`, `$_BACK_STEP_NONE`, the `advance` text and
  its `@N` operand, `src/enc/`, `enc.h`), `limits.def`, `src/parse/mod_lookaround.c`.

## Evidence population (copies, read-only; count from these, not from the prose)
- `R/evidence/vlbrev3_evidence/` (rev 3: `candidates.py`/`.out` the 8.58M-cell candidate-sequence
  check, `model.py`, `mrun.py`, `sweep_cursor.py`/`_summary.txt`, `workdiff.py`/`.out`, `probe.c`,
  `cells_*.txt`/`.out` the 52 libpcre2 cells), `R/evidence/vlbpieces_evidence/` (the study's sweeps),
  `R/evidence/vlbrev2_evidence/premise.out`. If you run one of these scripts, run a COPY in your own
  dir.

## Tools
- Oracle A (libpcre2-8 10.46 as a library): `R/tools/oracle_probe`.
  Compile: `printf '%s\n' 'PATTERN' | R/tools/oracle_probe c [u]`; match:
  `printf '%s\t%s\n' 'PATTERN' 'SUBJECT' | R/tools/oracle_probe m [u]` -> every match as
  `[s-e,g1s-g1e,...]` or `nomatch`. Checked: `(?<=a|bc)x` on `bcx` -> `[2-3]`.
- Oracle B (rev 3's probe, built from `R/evidence/vlbrev3_evidence/probe.c`): `R/tools/probe`.
  Lines `pattern<TAB>subject[<TAB>startpos]`; `R/tools/probe c|m FLAGS` with FLAGS letters
  `u` PCRE2_UTF, `i` PCRE2_UTF|PCRE2_MATCH_INVALID_UTF (ill-formed subjects), `x` decode `\xNN` in the
  subject. Checked: `(?<=(é{0,2}))b` on `\xc3\xa9\xa9b` with `m ix` -> `[12-13,12-12]`.
- pcrec (review tree), checked spellings:
  `nice -n 19 /home/pcrec/projects/pcrec/worktrees/crit-vlb3/build/pcrec --features all -p rx --emit-main -o R/<lens>/x.c --pattern '(?<=a|bc)x'`
  then `gcc -O1 -o R/<lens>/x R/<lens>/x.c` and `R/<lens>/x SUBJECT` (prints `match S E`). UTF-8: add
  `-e utf8`. VM listing: `build/pcrec --features all --emit-ir --pattern P`. TODAY a varying lookbehind
  is REFUSED, so pcrec runs only fixed-width ones: read today's emitted C and listing for those to see
  what the design keeps or extends (the back-step, the `advance` text, slots, trail, frames).

## DENYLIST (PATHS EXCLUDED from every read, git diff, git log -p and grep)
- `docs/dev/lanes/vlbrev3_report.md`, `docs/dev/lanes/vlbrev3_rulings.md`,
  `docs/dev/lanes/vlbrev2_report.md`, `docs/dev/lanes/vlbpieces_report.md`, and every other
  `docs/dev/lanes/vlb*` report or rulings file (the `*_evidence/` copies above are allowed)
- `docs/dev/wake.md`, `docs/dev/owner.md`, `docs/dev/dev_journal.md` (do not read it at all)
- `/var/tmp/pcrec-pcrec/scratch/crit-vlb2/`, `/var/tmp/pcrec-pcrec/scratch/crit-vlookbehind/` and
  `/var/tmp/pcrec-pcrec/scratch/crit-arev*/` (other rounds' scratch dirs; committed review texts under
  `docs/dev/reviews/` ARE allowed)
- `git log` bodies beyond subject lines; job logs; the box queue; any worktree under `worktrees/`
  except `worktrees/crit-vlb3`
- `R/.coord/` and every other critic's directory under R
For git commands add pathspec exclusions, e.g.
`git -C /home/pcrec/projects/pcrec grep -n PATTERN e20dee230 -- . ':!docs/dev/lanes/vlbrev3_report.md' ':!docs/dev/lanes/vlbrev3_rulings.md' ':!docs/dev/lanes/vlbrev2_report.md' ':!docs/dev/lanes/vlbpieces_report.md' ':!docs/dev/wake.md' ':!docs/dev/owner.md' ':!docs/dev/dev_journal.md'`.
For PLAIN grep -r (e.g. in the review tree) add `--exclude=vlbrev3_report.md --exclude=vlbrev3_rulings.md --exclude=vlbrev2_report.md --exclude=vlbpieces_report.md --exclude=wake.md --exclude=owner.md --exclude=dev_journal.md --exclude-dir=.coord --exclude-dir=worktrees`.

## Output format
- Your findings file `R/<lens>/findings.md` DOES NOT EXIST YET: create it, with its headings, as your
  FIRST action and write it INCREMENTALLY (one finding at a time, as you go).
- Sections (exact `##` headings): `## Findings`, `## PROBED-AND-HELD`, optionally
  `## Questions for a pcre2-reader`.
- Each finding: id `<LENS>-n`; CONFIRMED (with a repro: input, command or hand-execution trace,
  observed vs expected) or SUSPECTED (what would confirm it); severity (answer / speed / size /
  maintenance / doc / design); effort; blast radius; the design § and line in the frozen copy (and
  file:line in the review tree where code is cited). A finding against a ruling above or a D-row
  cites it and argues, or is dropped.
- PROBED-AND-HELD: what you checked that held, with case counts.
- If a harness rule refuses your findings-file Write, do not route around it: return the findings as
  your final text instead.
- Your DELIVER file `R/<lens>/DELIVER` exists (the coordinator wrote it). When done run
  `/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-vlb3 --deliver /var/tmp/pcrec-pcrec/scratch/crit-vlb3/<lens>/DELIVER crit-<lens>`
  and fix what it reports until it prints `lanecheck: DONE rc=0`. Then END.
- Final reply at most 150 words.
