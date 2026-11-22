# r75 SLOT-3 / SLOT-4 at ec578d053 (U3)

Evidence file: `git -C /home/pcrec/projects/pcrec show ec578d053:memfn/src/window.c` (line numbers below).

## SLOT-3: DISCHARGED (one residue, noted)
(1) Reads of the `render` pointer: `git grep -n -E "\.render|->render" ec578d053 -- memfn/src/window.c`
- :3784 `wf_spanrows[st->row].render(rc, t, st)`: a CALL, the column's job.
- :2573 `!wf_spanrows[i].render` in wf_tables_check: a hole check (non-NULL), not a kind test.
No comparison of the pointer, and no `== wf_span_v` anywhere. The old tag reads (:2039, :4350 in r75) are gone.
The `define` column exists (:1989-91, rows :1997-2002): V rows carry `wf_span_v_define`, the others NULL.
Residue (minor, SLOT-3's own shape one column over): the define pointer is still read as a "is V" flag.
- :2045 `wf_spanrows[r].define ? nv++ : 0`: the j numbering. Documented in the column comment (:1990-92), and j is only
  meaningful where a define uses it, so this is a nullable hook with a stated meaning, not an opaque tag.
- :4467-68 `if (.define && .define(...))`: ordinary optional-hook call.
- wf_tables_check (:2570-75) does not check the pairing "define set <=> render is the V text" or that a define row's
  render and define agree on one vs_name j. Nothing breaks today; a row with define but a non-V render would number j
  with no reader. Low severity; one-line check if wanted.

## SLOT-4: DISCHARGED
(2) V head spelling: `git grep -n "vs_head(" ec578d053 -- memfn/src/window.c` gives the definition (:4321) and four calls:
:4334 (vs_sel_head, the selector's head via kit_selector), :4394 (block helper, one-pointer form), :4408 (`__w32` top fn),
:4436 (`__body`). All four go through ONE head writer, vs_head. No other `static inline __attribute__` spelling for V in window.c.
(Other kit families, ofsskip.c/vany.c/vrun.c, write their own `<fn>__body` heads; those are different families
and were not in SLOT-4's scope.)
(3) Name family: `git grep -n "rc->VS\|vs_name(" ec578d053 -- memfn/src/window.c`. The only `printf` that builds
`<p>_mf<h>_vs<j>[__part][_b]` is vs_name (:4310; base from wf_nm "_vs" :3588, the generic per-site name builder that
all rc names share). Callers: :3756 (use), :4431 x2, :4441, :4442. The part strings are `"body"` (:4431) and
`kit_level(LV_X86_W32)->stamp` (:4440, :4442): `__w32` is a stamp from the level table, not a literal. One name function.
(4) Reintroduction: none found. No fourth head spelling, no second `%s%u` builder for `_vs`, no tag read via another
column (S_VWIN/S_VSCAN enum constants appear only as the table's designated initialisers, :1984-2002).
Same-shape notes on these sites: none beyond the SLOT-3 define-flag residue above.
