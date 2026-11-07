# COMMON brief: critic round xarch (design review, rev 0)

## Scope mandate
Touch ONLY the pcrec repo (/home/pcrec/projects/pcrec) and, read-only if ever needed, pcrec-bench.
You are READ-ONLY on both repos: no edits, no commits, no `make`, no suites, no box lock, no
worktrees. Scratch only under YOUR dir /var/tmp/pcrec-pcrec/scratch/crit-xarch/<lens>/ (it exists).
Never /tmp. Set PCREC_TMPDIR=/var/tmp/pcrec-pcrec/scratch/crit-xarch/<lens> for anything you run.
Kill only your own processes, by PID (never pkill -f). Bound every uncertain command with `timeout 120`.
Use absolute paths; never `cd` into a worktree in a chained command (a hook blocks it; use a
`( cd X && ... )` subshell or `git -C`).

## Subject (frozen)
- Design: docs/design/memfn/target_seam.md PROPOSED REVISION 0, held by commit
  e2f9793d1b6b2dac51838e11c1a28c958e44ccdf (written off main aeede1d16). Read it as
  `git -C /home/pcrec/projects/pcrec show e2f9793d1:docs/design/memfn/target_seam.md`.
  It defines the pcrec <-> memfn kit seam for per-target (per-CPU) code-path VARIANTS under
  decisions.md D188 Addendum 1. The kit will shape its SIMD forms by it; the build waits for the
  owner's [XARCH-DEV] go. Design only: nothing in src/ cli/ lib/ memfn/ changed with it.
- Build tree (where a build would land): main HEAD 5b43f8e9a71765aad3e3623f98e7bb68d469abb8, checked
  out read-only at /home/pcrec/projects/pcrec/worktrees/crit-xarch and BUILT there
  (build/pcrec, build/libpcrec.a). Any cited code (file:line) that differs between aeede1d16 and
  5b43f8e9a, or that the line numbers no longer point at, is a finding.
- The kit's IN-FLIGHT branch: lane/memfn-s2e @ 5b6cf41aa (unmerged to main). It changes
  memfn/src/runcmp.c, memfn/src/formhash.c, memfn/src/kit.h, which §3 cites. Read its version with
  `git -C /home/pcrec/projects/pcrec show 5b6cf41aa:<path>`; a claim that holds on main but not on
  the kit's branch is a finding (the kit will write its SIMD forms on top of its branch).
  D188's home, docs/design/memfn/span_cards.md, is rev 1.5 on that branch (rev 1.1 on main):
  read rev 1.5 (`git show 5b6cf41aa:docs/design/memfn/span_cards.md`) as the version in force.
- You may run `build/pcrec` on single patterns (e.g. `-p rx -o F.c --pattern P`, with
  `-fmemfn-simd` for the SIMD-on axis, `--emit-main`, `-fno-memfn-simd`), `gcc -c/-S/-O2` on
  generated or hand-written C, `size`, `nm`, `objdump -d`, and small C/python drivers in your own
  scratch dir (python with `-I`). Spelling checked: `build/pcrec -fmemfn-simd -p rx -o b.c
  --pattern '(?i)cat'` emits `RX_MEMFN_FORMS "vrun@w32+w16"` and AVX2 `#if` guards. gcc here is
  the target compiler; the box is a Zen 4 (AVX2 + AVX-512). At most ~300 compiles per critic.
- Rulings: read decisions.md / plan.md ONLY as
  `git -C /home/pcrec/projects/pcrec show 5b43f8e9a:docs/dev/decisions.md` (and plan.md), never the
  live tree. To read a plan row, locate it by `grep -n '^- \[TAG\]'` and read that row (to the next
  `^- \[` line) only. Rows the note relies on: [XARCH-DEV], [MEMFN-RTDISPATCH] (a sub-row, find it by
  `grep -n '\[MEMFN-RTDISPATCH\]'`), [IFACE-PUSH], [IR-FORM]. Decisions it cites: D188 (+ Addendum 1),
  D155 (+ addendum 5), D157, D146, D147, D165, D76, D94, D77, D80, D153, D174.

## Docs and code you will need (read at the build tree)
- docs/dev/guide/{README,architecture,coding,style,critics}.md (the rules; architecture.md has the
  ranked-goals rule), docs/design/CLAUDE.md (standing questions)
- docs/design/stream/manifesto.md (principle 9: every seam is a document), docs/design/stream/roadmap.md
- docs/design/memfn/: integration.md, requirements.md (RB-3), isa_evaluation.md, linux_results.md,
  span_cards.md (rev 1.5 as above); memfn/CLAUDE.md, memfn/src/CLAUDE.md
- memfn/src/levels.def, memfn/src/ofsskip.c, memfn/src/vany.c, memfn/src/runcmp.c,
  memfn/src/window.c, memfn/src/precheck.c, memfn/src/formhash.c, memfn/src/kit.h (the mf_art /
  sink / MF_P_* / MF_INC_* seam), and the pcrec callers of the kit under src/gen/ (grep `mf_art_begin`)
- docs/spec/match_api.md (§5.3 the dispatch/static rule; the stamps; §6 or docs/dev/history/
  abi_changelog.md for the abi ritual), docs/design/compound_entries.md, docs/design/findall_iter.md
- scripts/emit_sweep.py (the G2 check tool), memfn/tests/run_g2_simd.py (the per-arm test shape)

## DENYLIST (do not open, grep, diff or list; exclude from every git diff/grep)
docs/dev/lanes/xarchseam* (all), xarchseam_rulings.md anywhere, /var/tmp/pcrec-pcrec/scratch/xarchseam/,
any docs/dev/lanes/*_report.md about this subject, git log BODIES (subject lines OK), job logs,
other worktrees (only worktrees/crit-xarch is yours, read-only), the box queue, and
/var/tmp/pcrec-pcrec/scratch/crit-xarch/.coord/ and other critics' dirs.
For plain grep use `--exclude-dir=lanes --exclude-dir=worktrees --exclude-dir=.coord`; for git grep add
pathspecs `':!docs/dev/lanes'`. memfn/docs/responses.md and requests.md ARE readable (the kit's
ledger). The design text cites scratch probes; treat those as claims and check them yourself.

## Output format
Your findings file DOES NOT EXIST YET: CREATE it as your FIRST action at
/var/tmp/pcrec-pcrec/scratch/crit-xarch/<lens>/findings.md, with headings
(`# <LENS> findings`, `## Findings`, `## PROBED-AND-HELD`), and write it INCREMENTALLY.
Each finding: id `<LENS>-n`; CONFIRMED (with a repro: input, command, observed vs expected; or for a
text claim, the quoted lines file:line) or SUSPECTED (what would confirm it); severity (answer / speed /
size / maintenance / doc / design); effort; blast radius; § of the design and file:line in the code.
A finding against a ruled D-row cites it and argues, or drops. End with PROBED-AND-HELD (what you
checked that held, with case counts). If your Write of the findings file is REFUSED, SendMessage the
findings to "crit-xarch" at once, marked relayed, and return them as your final text.
Then run `/home/pcrec/projects/pcrec/scripts/lanecheck --dir /var/tmp/pcrec-pcrec/scratch/crit-xarch --deliver /var/tmp/pcrec-pcrec/scratch/crit-xarch/<lens>.deliver <lens>`
and end only after it prints DONE. Final reply at most 150 words.
