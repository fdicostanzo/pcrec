# cli — command-line compiler tool

Entry point: pcrec command-line tool. Parses flags, calls pcrec_compile(), writes output to disk or stdout.

**[M4.4] (D43.2/D44.8, 2026-08-14):** `-i` and `--emit-main` set
`opt.flags |= PCREC_CASELESS` / `PCREC_EMIT_MAIN` — `pcrec_options` no
longer has separate `caseless`/`emit_main` int fields (lib/CLAUDE.md).

**[M4.5b] (2026-08-15):** five GENERATION AXES for the VM engine
(docs/design/engine_m4.md §4.6/§5.3/§5.6). `--no-captures` sets
`PCREC_NO_CAPTURES`; `--engine=dfa|vm|auto`, `--step-budget=N`,
`--fno-step-budget` and `--backtrack-frames=N` set the new `pcrec_options`
members. They are axes rather than runtime parameters because D18 compiles
options away — and, for the budget specifically, because that is the only
shape the ruled ABI leaves open at all: `rx_matchfn`'s signature is frozen
with no slot for a budget, and adding one to `rx_ctx` is a DD-3 struct
revision D38 reserved for capture export.

**[M4.5c] (2026-08-15):** DD-8's two debug surfaces. `--emit-ir` is a QUERY
shaped like `--count-groups` — it runs the real pipeline (nothing cheaper
could honestly describe the emitted program), prints the VM program listing,
takes no `-o` and emits no C. On a pattern that compiles to the DFA engine it
REFUSES and names the two ways to get a listing, which is an as-built decision:
engine_m4.md §10 and DD-8's row are both silent, and the alternatives were
inventing a DFA listing this milestone was not asked for or printing an empty
one that looks like a bug. `--trace` is a generation axis (`PCREC_TRACE`)
producing an instrumented artifact that prints every resume-frame push/pop and
capture write to stderr; never the default, and the artifact stamps that it is
traced.

**[ENG-BREP] (2026-08-16):** `-fno-possessify` (`PCREC_NO_POSSESSIFY`) is the
first member of D47.3's DENY family — gcc-style spelling, bare flag, a TESTING
AND TUNING AXIS rather than a user feature. It denies the possessification
rewrite (docs/design/eng_brep_design.md §2), which changes no answer by
construction, so the only reason to turn it off is to CHECK that: the row's
primary instrument compiles the same pattern both ways and compares. DENY
rather than FORCE is load-bearing per D47.3 — each quantifier walks its own
ladder skipping denied steps, so a denial composes per-quantifier with no need
to ADDRESS one quantifier inside a pattern. The do-or-die half lives in
OBSERVABILITY rather than in a refusal: the artifact stamps
`<PREFIX>_VM_STRATS`, and a denied strategy appearing there is a hard test
failure.

`-fno-revdet` (`PCREC_NO_REVDET`) is the family's SECOND member, arriving with
the reverse-deterministic rung it denies (docs/design/engine_m4.md §2.5), and
everything above applies to it unchanged — including that its do-or-die is
asserted against `<PREFIX>_VM_RUNGS`'s REVDET bit rather than against the flag
having been passed. What is specific to it: denying the rung drops a qualifying
quantifier one rung to FRAMES, which for a bounded repeat is literal
replication, which is the semantic ground truth its differential compares
against — so the deny flag is not merely how the rung is tested, it is what
makes the ground truth reachable at all. Denying it must not, and does not, deny
possessification: the two are independent, and possessification is a modifier at
every rung rather than a rung of its own.

Neither appears in `--help`, deliberately and per D47.3: these are testing and
tuning axes, documented here and in docs/testing.md, not sprawling top-level
user features. The rest of the family (`-fno-counter`, a value parameter for K)
arrives with the strategies it denies.

`--engine` is DO-OR-DIE: a request the pattern cannot honour is a clean
refusal, never a silent downgrade. `--engine=vm` additionally turns the DFA
prefilter OFF (D44/R21 E-6), which is what makes it usable as an independent
cross-check rather than an echo of the DFA — without that, `span(VM) ==
span(DFA)` is close to a tautology, because the hybrid hands the VM the DFA's
own answer as its starting window.

## Files

- **main.c** — CLI: option parsing ([-p PREFIX] [-e ascii|utf8] [-i] [--emit-main] -o OUT.c 'PATTERN'; -i is ASCII case-insensitive, folded into the automaton at parse time — see OS-1/D23); output file writing; the SR-3 syntax queries (--list-syntax, --explain, --flavour, --list-verbs; **--explain was REWRITTEN at MOD-0.7** from a prefix match on the `syntax` column into a live doorway call — it prints the ROW's declared attribution beside the LIVE recogniser's answer and compares them per row, and it has a THIRD exit code: 0 answered-and-agreed, 1 the query could not be answered (unchanged), **3 at least one row DISSENTS** — a defect surfaced, not a bad question, which is why it is not folded into 1); --count-groups (MOD-0.1 §18.1); and --probe-ask WANT [--] CONSTRUCT (MOD-0.1 §18.2 — one doorway call at ask level claim|verdict|result, real cursor reported before/after; check06's cursor-rule channel; a doorway REFUSING is a normal exit-0 outcome, only a channel that could not run exits 1); --features LIST (MOD-0.1 slice 9 — the enabled set: module names from --list-syntax's module column, a frozen named set (`std1`, D37), or all/none, unknown names refused by name; composes with every mode; installs the set via pcrec_enabled_set_spec before anything consults the gate. **[STD1] phase A (D37, 2026-08-13):** a bare invocation (no `--features` at all) now ALSO resolves through `pcrec_enabled_set_spec`, using `PCREC_DEFAULT_FEATURES` (src/parse/enabled.c, currently `"none"`) instead of skipping the call — behaviourally identical to before (mask stays 0) but gives the enabled-set machinery a named answer for a bare invocation too, which is what lets src/gen's artifact stamp report something honest ("Feature set: none") rather than nothing. An explicit `--features` always overrides the default; the default constant is the SOLE point that later flips to `"std1"`)

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
