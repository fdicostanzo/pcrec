# yespin2 report

History index line: `yespin2 (sonnet, 2026-11-13): re-pinned 36 stale emit_sweep VARIANT_PINS tag floors (nevermatch a60681ae2, minw abi 103, famland abi 99, pffix abi 100) + the stderr-vm manifest witness; full variant coverage clean; no wrong answer, no lost optimisation.`

## STATE AT HANDOFF

Done and committed on lane/yespin2 (from main a07f76d6c). Validation, all
unlocked runs (PCREC_BOXLOCK=0, nice -n 19, jobs=2, comp-jobs=2; manager-approved):
- run1 (`--variant all --emit-pins`, HEAD vs HEAD, 7,034 rows, 0 movers, 0 asymmetric):
  72 TAG FLOOR lines, pins in scratch/yespin2/pins.py.
- run2 (`--variant all` after the re-pin): every tag floor held in every cell; the only
  FAILED reason was `MANIFEST ... (a{2,4})+ does not carry stderr-vm` in lowsize utf8 and
  lowboth utf8 (the witness pattern moved, cause 2 below). Fixed (2 lines).
- run3 (`--variant lowsize --variant lowboth --bases utf8`, the only cells the fix touches):
  `VARIANTS: CLEAN`, rc=0. The literal `VARIANTS: ok` of one single `--variant all` run was
  not re-obtained after the 2-line manifest fix (50 min run); run2 + run3 together cover
  every cell with the final file. Logs: /var/tmp/pcrec-pcrec/scratch/yespin2/run{1,2,3}.log.

STOP RULE: not triggered. Every drop is explained below; none is a wrong answer
(0 movers, 0 asymmetric in all runs) or an optimisation lost at the shipped caps.

CAUSES (method: the same variant -D set built at 646a8c0be and at the tip, corpus
compiled with `--emit-ir` in both, per-pattern tag diffs; then first-parent samples of
the 135 commits between to place each step):
1. 'yes' drops in every variant/base: the 16 never-match patterns go yes -> refused
   (a60681ae2, already shown by yespin). utf8 also gains one refused -> yes
   (`(*UCP)(?<=\w)x`), hence 1788 -> 1776 on 13 rows.
2. lowsize/lowboth only (the lowered size caps): [FIND-MINW] 06699f615 (abi 103) adds
   ~106-120 emitted bytes per artifact (its report), so artifacts at the lowered caps cross
   them. The probe steps exactly at 06699f615 (004a7849e and 3b52b096d read old). Byte: 3
   yes-collapsed -> no-size-cap, 1 yes -> no-size-cap, 3 yes -> yes-collapsed,
   `(?:a(?R)?)+b` no-linked-call -> refused (96 -> 95). utf8: `(a)(?!\1)*z` and
   `(a)(?=\1)*z` no-backreference -> refused (421 -> 419), 5 yes-collapsed -> no-size-cap
   (26 -> 23). So no-backreference, no-linked-call and yes-collapsed are size-cap effects,
   NOT nevermatch.
3. lowsize utf8 edge steps: famland e30a31174 (abi 99; +18 bytes on 12 stamp rows)
   `(?!)*z` yes -> no-size-cap; pffix e41ac3534 (abi 100, emit_dfa.c only)
   `((?:a|){0,4}c)` yes -> yes-collapsed. The commit step is measured; that the extra
   bytes are the stamp/abi text is inferred, not rebuilt.
4. lowdfa utf8 also shows 14 `(*UCP)` classes refused -> no-dfa-overflow (U3), a gain,
   not a failing floor.

## CHANGES

scripts/emit_sweep.py only: 36 tag-floor values lowered in VARIANT_PINS (lowboth, lowsize,
lowdfa byte/utf8; plain and lowthr utf8 emit-ir-auto and -fno-prefilter-collapse yes
1788 -> 1776), from run1's `--emit-pins`; only floors that read BELOW their pin were
touched (the rest, raised by corpus growth, stay valid floors). The lowsize/lowboth utf8
`stderr-vm` manifest witness `(a{2,4})+` -> `(a)(?!\1)*z`. A RE-PINNED 2026-11-13 (lane
yespin2) comment with causes 1-3 sits beside yespin's. Scratch only under
$PCREC_TMPDIR/scratch/yespin2 (bisect builds, probes); no worktrees created.
