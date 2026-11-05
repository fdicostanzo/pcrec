# HOUSE lens, crit-memfn-sp1e (code-style/house rules). Read-only; no denylisted file read.

## FINDINGS

### HOUSE-1  The renderer row is split across three parallel arrays on one enum (wrong altitude / duplication)
CONFIRMED (read). severity: maintenance. effort: S. blast: window.c only, no byte.
window.c wf_brows[] (row, holds, libc, path, prepare, basis), wf_b_find[] (find renderer) and
wf_b_text[] (head, next, define) are three tables indexed by the same B_* enum, tied by two
_Static_asserts. The design calls it ONE "renderer row" (span_pick §The tables; the window.c header
says "THE RENDERER ROW ... the text a (frame row, method row, renderer row) triple"). Shared
abstraction: one struct per renderer row carrying holds/libc/path/prepare/find/head/next/define; the
B_HORS-needs-NULL-find and B_FN-needs-NULL-everything cases then read as visible NULL fields in one
row, not as parallel-array holes (wf_b_find[B_HORS]=NULL, wf_b_text[B_FN]={NULL,NULL,NULL}). Three
rows (B-pair, B-memchr, B-walk) repeat the same {d_one_head, d_one_next, NULL} triple (window.c ~2705).

### HOUSE-2  Name reuse and dead-row names (D174, names that do not describe behaviour)
CONFIRMED. severity: maintenance. effort: XS.
(a) `wf_b_text` before 1e was the array of Table B's FIND renderers; 1e reassigns that name to the
head/next/define triple and renames the old one `wf_b_find`. A reader of the old diff/history sees the
same identifier mean two things. (b) d_one_head / d_one_next / d_hors_head / d_hors_next /
d_hors_define / d_hors_prepare (window.c ~1743, 2310, 2663, 2680-2700) keep the names of a DELETED
Table D row ("D-one" has no row left; row_map.tsv records it dissolved). They are B-renderer behaviours
now (find-then-bound head, c+1 resume; probe head, shift resume). Suggest b_find_head / b_step_next /
b_hors_*. (c) comments still teach "D-one" as a live row: window.c:2310 "The resume ...: D-one", 2507
"C++ D-one", 2514 "B, C and D-one are that function's", 2663 "D-one's loop head".

### HOUSE-3  Stale cite: plan_cost.def still says HORS_MIN is "window.c Table D"
CONFIRMED. severity: doc. effort: XS. memfn/src/plan_cost.def:23 "HORS_MIN ... is D-hors's (window.c
Table D)". Table D is deleted by this diff; D-hors is finder.c's first row and hors_facts reads the
constant. File not in the diff (the unit changed the reader, not the cite). Also window.c's `COST(HORS_MIN)`
reader is gone while window.c's enum still expands WC_HORS_MIN (unused constant).
Related: memfn/src/presence.c:73 "density readers (HORS_MIN, MARGIN)" is still true but HORS_MIN's
reader is now finder.c, not window.c; the "named exception" cite should say where.

### HOUSE-4  plan_cost.def is X-macro-expanded a second time for one row (duplication)
CONFIRMED. severity: maintenance. effort: S. finder.c:625-631 re-includes plan_cost.def into a second
anonymous enum (FD_COST_*) solely to read FD_COST_HORS_MIN; window.c:69-76 already expands the same file
into WC_*. Two enums over one table, and the finder one carries every cost row to read one. The
comment says "window.c reads the rest of the table", i.e. the split is by reader, not by meaning.
Shared abstraction: one cost enum in kit.h (or a kit_cost(HORS_MIN) accessor), consumed by both. If the
threshold is the finder's now, say so in plan_cost.def (HOUSE-3) so the owner of the number is findable.

### HOUSE-5  fd_find is two askers behind a NULL pointer (if-chain standing in for a declared asker)
CONFIRMED (design reading). severity: maintenance/design. effort: M. finder.c fd_find (~646-690):
`if (!st && !fd_scope...)`, `if (st) {...} else {...}`, `st ? st->wf : NULL`, and window.c/compose.c
each pass NULL or a struct. The "asker fact" the unit set out to declare is implemented as ONE flag
(`renders_pair`) plus the implicit "st == NULL means composer" mode, so the asker's three differences
(scope gate, need derivation, which facts are stated) are an if/else, not a declared row/field per asker.
Owner preference is declared first-match tables, not if-then. A small `fd_asker` struct (or enum
{COMPOSER, WINDOW}) with the fact-setters as a two-row table would make the third asker an added row.
Not a blocker for stage 1 (ruled "one walk with the asker fact"); file for stage 2.

### HOUSE-6  fd_stop is half input, half scratch; positional initializer with magic values
CONFIRMED. severity: maintenance. effort: XS. window.c wf_find_decide:
`fd_stop st = { set, off, 0, 0, 0, d->rate, &f, 1 };` then `st.hw = hors_window(d,&st.wlo,&st.whi)`, then
fd_find (takes it const), then `fx->wlo = st.wlo`. Eight positional members, three zeros that are
(hw, wlo, whi) overwritten on the next line, and a bare `1` for renders_pair. Use designated
initializers (`.renders_pair = 1`) and compute the window in a local before the struct. Also
`hors_window` is called for every E-find plan even when the stop set cannot reach HORS_MIN (the old
code did the same, so not a regression).

### HOUSE-7  fd_renderers uses a -1 "either" sentinel as a data value (compose.c ~272-290)
CONFIRMED. severity: maintenance. effort: XS. `{ FF_LIBC_BACK, -1, ...}` overloads the int end_back
column with -1 = "any". Matches the "first match over (pick, end_back, -1 either)" prose, but a first-match
row table should state the wildcard as a named constant (e.g. EB_ANY, as MF_ANY is used everywhere else
in the kit's contracts) rather than a literal. Also the fd_find return value is dropped by select_arm
(`fd_find(...)` result ignored; `rid` is used as the "decided" signal), so the documented "1 with pick, or
0" has a second, implicit meaning (rid non-NULL with return 0 for "?need"). Make select_arm test the
documented return or document `*row` as the signal.

### HOUSE-8  Two parsers of row_map.tsv with different contracts (tests/memfn)
CONFIRMED. severity: maintenance. effort: S. reach_equal.py read_map (requires >=4 columns, ignores
`unit`, maps "-" to None) and rows_check.py section M (read_tsv(...,5), compares "-" literally) parse
the same declared file two ways. A column added to row_map.tsv is read by one and silently ignored by the
other. Shared: one tiny reader (tests/memfn/rowmap.py or a function in an existing shared helper).

### HOUSE-9  reach_equal.py reach_of() signals in-band and does two jobs
CONFIRMED. severity: maintenance. effort: S. reach_of now takes (rmap, base) and, besides parsing REACH
lines, counts END records and appends sentinel keys ("?map", "?dissolved") into the SAME Counter as real
(table,row,field) keys; main() then scans `c` for those prefixes, appends to problems, `del c[k]`. A real
table named "?map" is impossible, but the pattern is the "controls share a source" shape the guide warns of
and mutates a dict the caller then iterates. Return a small result (reach, dissolved, head_records) instead.
The map logic (mapped/dissolved counters, three append sites in main) also grows main() well past one screen.
The module docstring line "A --limit or --no-corpus (the patterns files alone) run is a SMOKE run: ..." is
a 120+ column line in a hard-wrapped docstring.

### HOUSE-10  Comment-history accretion in decider_census.py / run_rows.sh
CONFIRMED. severity: doc. effort: XS. decider_census.py HITS/MEMBER_COUNT comments are a running changelog
("50 at 1a; 51 at 1b; 50 at 1c; 52 at 1d; 52 at 1e ..."), and run_rows.sh's ROWS_FLOOR line is a ~900-char
changelog on one `export` line. Guide (coding.md/style) puts history in NOTES.md / the journal, not in the
constant's comment; keep only the current value and why it is exact. (Precedent: they already carried this
shape, so a LOW item.)

### HOUSE-11  Stale comment in finder.c on the retired fd_route
CONFIRMED. severity: doc. effort: XS. finder.c ~597-599 "until 1e two entries walked it (the composer's
fd_route, the window family's fd_find, after Table D's own walk)" is history prose inside the live
contract comment; the live doc is the two bullets after it. Same for finder.c:106/109/169/206-208/249-256
("SF_WINDOW_STOP until 1e", "Table D's predicate", "moved here unchanged") and window.c:1822 B-hors basis
string ("Table D's D-hors text until span_pick 1e") which is a user-visible basis string in the row
listing context. Move provenance to finder_history.md (the unit already logs there) and leave current
behaviour in code comments. S1079 sabotage header similarly carries three RE-ANCHORED paragraphs.

### HOUSE-12  window.c comment width / layout
CONFIRMED. severity: doc. effort: XS. window.c ~2509 "Under D-HORS (T-FIND's first row; B-hors) B is replaced:
BOUND first, then the window's last" is a >100-column line in an otherwise reflowed block; reflow.

### HOUSE-13  decider_census.tsv classifies fd_renderer as T-FRAME
SUSPECTED. severity: doc. effort: XS. compose.c fd_renderer renders a T-FIND pick through (pick, end_back)
rows, i.e. the "renderer row" of a (frame, method, renderer) triple; the census labels it T-FRAME while
the window-side wf_find_decide (also asking T-FIND then the renderer) is T-FRAME too. Consistent, but
fd_renderer is not a frame choice (the frame is select_arm's arm table). Confirm against span_pick.md's
census taxonomy; if renderer rows are their own class, label them so.

### CLAUDE.md check
memfn/src/CLAUDE.md: updated (11 rows, fd_find, hors_facts, fd_renderers, Table D folded, row_map).
memfn/include/CLAUDE.md updated (CLASS_V 8). tests/memfn/CLAUDE.md lists row_map.tsv and reach_equal --map.
HOLDS. Nit: src/CLAUDE.md still describes B/C/D inside E-find in one sentence that now says "C: C-run's
compares" with B listing five renderers; fine. memfn/src/CLAUDE.md "Do not add a parallel walk" sentence
updated correctly.

### Dead code from the merged walk
None found: grep for fd_route, wfD, wf_dtable, wf_drows, SF_WINDOW_STOP, WF_HORS_ID, ->drow over memfn/,
tests/memfn, tests/mech/sabotages leaves only history comments and the row_map/reach_equal readers by
design (listed above under HOUSE-2/3/11). finder_check.py's `fd_routed` helper name remains
(finder_check.py:512) for "routed decision" -- a test helper whose name predates the merge; rename with
the next touch (XS, doc).

## PROBED-AND-HELD
- Read the full diff of finder.c, kit.h, options.def, memfn.h, window.c, compose.c, CLAUDE.md x3, and
  tests/memfn python/tsv. No compiles run (0 of 50).
- No side effects in predicates: hors_facts writes the fd_x facts (the walk's input builder, not a
  predicate); the D-hors row's predicate is a pure fact test.
- Table-vs-chain: D-hors/D1/.../R7w is a declared first-match row table (fd_rows); fd_renderers is a
  declared row table; wf_brows is a declared row table. The only if-chain standing in for rows is fd_find's
  asker branch (HOUSE-5).
- Stale-name grep: no live code uses fd_route / wfD / wf_dtable / SF_WINDOW_STOP.
- No denylisted file read.
