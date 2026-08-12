# cli — command-line compiler tool

Entry point: pcrec command-line tool. Parses flags, calls pcrec_compile(), writes output to disk or stdout.

## Files

- **main.c** — CLI: option parsing ([-p PREFIX] [-e ascii|utf8] [-i] [--emit-main] -o OUT.c 'PATTERN'; -i is ASCII case-insensitive, folded into the automaton at parse time — see OS-1/D23); output file writing; the SR-3 syntax queries (--list-syntax, --explain, --flavour, --list-verbs; **--explain was REWRITTEN at MOD-0.7** from a prefix match on the `syntax` column into a live doorway call — it prints the ROW's declared attribution beside the LIVE recogniser's answer and compares them per row, and it has a THIRD exit code: 0 answered-and-agreed, 1 the query could not be answered (unchanged), **3 at least one row DISSENTS** — a defect surfaced, not a bad question, which is why it is not folded into 1); --count-groups (MOD-0.1 §18.1); and --probe-ask WANT [--] CONSTRUCT (MOD-0.1 §18.2 — one doorway call at ask level claim|verdict|result, real cursor reported before/after; check06's cursor-rule channel; a doorway REFUSING is a normal exit-0 outcome, only a channel that could not run exits 1); --features LIST (MOD-0.1 slice 9 — the enabled set: module names from --list-syntax's module column, or all/none, unknown names refused by name; composes with every mode; installs the set via pcrec_enabled_set_spec before anything consults the gate)

**A DOORWAY THAT RAISES (R20/MOD07-1)** is a third reason `--explain` and
`--probe-ask` return NULL, and each now prints a different sentence for it.
Both surfaces used to hand the doorways a `Ctx` with no `setjmp`, which was
safe only while no port could `ctx_fail`; once module ports began recursing
into `pcrec_parse_body` the surfaces SIGSEGVed (139) on any query whose body
fails at an open gate — `--features modifiers --explain '(?i:['`. They now
`setjmp`, abandon the answer, and fill a `pcrec_error`. An EMPTY `err->msg`
still means the pre-existing misuse ("no construct matches", "WANT must be
claim, verdict or result"); a FILLED one means the port ran a real parse of
the operator's text and that parse failed, so the operator gets the COMPILE
path's own shape — `pcrec: --explain: <diagnostic> (pattern offset N)` — and
not advice to fix a command line that is fine. Exit 1 either way; cli case12
pins the shape (nonzero AND below 128, which is what separates diagnosed from
killed-by-a-signal).

`--explain`'s exit-3 summary pluralizes its VERB as well as its noun since
R20/MOD07-9: "1 row DISAGREES", "2 rows DISAGREE".

## Conventions

The tool normalizes output paths (e.g., -o out.c generates out.h automatically; -o - prints self-contained C to stdout). It writes the generated .c/.h files to the filesystem.

Compilation goes through lib/pcrec.h, the public header. The SR-3 syntax queries are the one exception: they include src/core/internal.h, because the construct registry is deliberately NOT public surface — the CLI and the test suite are its only consumers today. main.c touches no registry type even so; it calls two functions that return finished text. Promoting one of them into lib/pcrec.h if a library caller ever wants it is easy in a way that un-promoting it would not be.

Maintenance: update this file when files are added/removed or their roles change.
