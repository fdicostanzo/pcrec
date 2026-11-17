# loadwatch report

## STATE AT HANDOFF
Rulings file loadwatch_rulings.md was empty (no R-n applied). Change is committed on lane/loadwatch.
OWED: none

## WHAT CHANGED
- scripts/loadshame: a declared WATCH row table (Steam, VS Code) at the top; each row = display name, command
  names, exe path prefixes, control-group unit patterns, plain-words thing to close. A process matches when ANY
  recogniser hits. New section always printed after the table (one line per application present: user, process
  count, root `command (pid N)` with `*` mark, up time, cores over the sample, what to close; "none present" otherwise).
  New `--present`: no sampling, section only, exit 0 none / 1 any. Default-mode exit codes unchanged.
- scripts/INDEX.md: loadshame line updated.
- Surprise: exe paths of another user's processes are unreadable (we run as pcrec), so the exe-prefix recogniser
  only helps for our own user's processes; on this box matching is by command name and unit. Documented in the header.

## SAMPLE OUTPUT
watched applications (present whether or not a window is visible; a closed window may leave processes):
  Steam: user frank, 18 processes, root steam.sh (pid 4089831), up 9d 13h, cores 0.02 -- close: Steam (File > Exit, ...)
  VS Code: user frank, 15 processes, root code (pid 1172932) *, up 5d 10h, cores 0.02 -- close: VS Code (close every window, then File > Quit)

## CHECKS RUN
- `scripts/loadshame --sec 5`: table plus the section above, rc=1 (box LOADED by other jobs).
- `scripts/loadshame --present`: section with cores n/a, rc=1.
- table-matches-nothing (scratch copy in $PCREC_TMPDIR/scratch/loadwatch, tree not edited): "none present", rc=0.
- `python3 -m py_compile scripts/loadshame`: ok. No CLAUDE.md touched.
