# lib — public library API

The only header file installed for embedding pcrec as a library. Declares the three public functions and the options/output/error structs.

## Files

- **pcrec.h** — public API: pcrec_compile(), pcrec_output_free(), pcrec_default_options(); encoding enum and option/output/error types. **[M4.4] (docs/design/match_api_m4.md, the MATCH-API FREEZE, D43.2/D44.8, 2026-08-14)** broke `pcrec_options`: the separate `caseless`/`emit_main` `int` fields are GONE, replaced by one `uint64_t flags` word and the `PCREC_CASELESS`/`PCREC_EMIT_MAIN`/`PCREC_NO_CAPTURES` bit constants (the last RESERVED — no code sets or reads it yet; M4.5-era `--no-captures`) — one representation of each boolean fact end to end, from CLI parse (cli/main.c) through this struct through the generated `rx_info.flags` (src/gen/emit_dfa.c). Also added: `pcrec_err_input`/`pcrec_error.input` (subst note §9 Q8, D42.4 — which input string `pos` indexes into; `pcrec_compile()` always sets `PCREC_ERR_INPUT_PATTERN` today). The `<prefix>_search` doc comment is REWRITTEN for the caps-array signature (D44.2) — see docs/design/match_api_m4.md §1.0/§11 for the full generated-ABI surface this header does NOT declare (the fixed types `rx_ctx`/`rx_matchfn`/`rx_group_entry`/`rx_info`/etc. and the `<prefix>_match`/`<prefix>_match_caps`/`<prefix>_info` entries live in the GENERATED .c/.h, per-artifact, never in this file — this remains the compiler's own library surface only).

**[M4.5b] (2026-08-15)** adds three `pcrec_options` members and two enum
families, all GENERATION AXES (D18: options are compiled away): `engine`
(`PCREC_ENGINE_AUTO`/`_DFA`/`_VM` — do-or-die, and `_VM` also disables the DFA
prefilter per D44/R21 E-6), `step_budget` (`PCREC_STEP_BUDGET_DEFAULT`/`_NONE`
or a count of backtrack resumptions), and `frame_capacity`. `PCREC_NO_CAPTURES`
stops being reserved and becomes live (D42.1: captures ON by default, this bit
recovers the pre-M4.5 pure-DFA artifact). The budget is an axis rather than a
runtime parameter not merely by preference but because it is the ONLY shape
the ruled ABI leaves open: `rx_matchfn`'s signature is frozen with no slot for
one, and adding one to `rx_ctx` is a DD-3 struct revision D38 reserved for
capture export (engine_m4.md §4.6).

**[ABI-NS] (D60 addendum, 2026-08-18): `PCREC_ENGINE_DFA`/`PCREC_ENGINE_VM`
became `#define`s here, not `enum` members, and the reason is a real hazard
found and fixed in this lane, not a style pick.** Every generated artifact
now ALSO emits `#define PCREC_ENGINE_DFA 1` / `#define PCREC_ENGINE_VM 2`
in its own `PCREC_RX_ABI_H` block (src/gen/emit_dfa.c), naming
`rx_info.engine`'s formerly number-only contract — the SAME names, on
purpose (D60's addendum: the request value and the outcome value are the
same fact, "which engine"). A consumer TU that includes a generated
artifact's header BEFORE this one used to fail to compile: the artifact's
`#define` textually rewrote this file's `PCREC_ENGINE_DFA = 1,`
enumerator into `1 = 1,` (verified directly against gcc — a hard syntax
error, not a warning). Two IDENTICAL `#define`s of one name are a silent
no-op redefinition regardless of order (verified clean under
`-Wall -Wextra -Werror` both directions); an `enum` and a later `#define`
of its own enumerator are not. `PCREC_ENGINE_AUTO` (0) has no artifact-side
counterpart and stays an `enum` member — keep it that way, and keep the two
`#define` lines below byte-identical to `emit_rx_abi_types`' emission if
either spelling ever changes.

**[M4.5c] (2026-08-15)** adds one flag bit, `PCREC_TRACE` (DD-8): emit an
instrumented matcher that prints every resume-frame push/pop and capture write
to stderr. A generation axis like the rest (D18), never the default, and the
artifact stamps that it is traced — a traced matcher writes to stderr, which
is not something a shipped one should ever do.

## Conventions

This is the sole public interface; everything under src/ is internal. The library works in two modes: -o out.c writes a self-contained .c file (no header), or -o out.c with options.header_name='out.h' writes paired .c/.h files. Generated code has no dependency on pcrec at runtime.

Maintenance: update this file when files are added/removed or their roles change.

**[ENG-BREP] (2026-08-16):** `PCREC_NO_POSSESSIFY` (`1u << 4`) joins the flags
word as the first STRATEGY-DENIAL bit — `-fno-possessify`, D47.3's deny family.
It is unlike every other bit here in one way worth stating: it is a testing and
tuning axis, not a semantic option, so it changes no answer and
`src/gen/emit_dfa.c` deliberately MASKS it out of the emitted `rx_info.flags`.
Two artifacts differing only in this bit are byte-identical, which is what
makes the pass's own byte-identity gate expressible at all.

**[ENG-BREP counter-K] (2026-08-17):** the family reaches its third and last
v1 member and gains the rung's two value knobs.

`PCREC_NO_COUNTER` (`1u << 6`, `-fno-counter`) denies the COUNTER rung. Same
masked-out-of-`rx_info.flags` treatment as its two siblings, and the same
role — except that denying THIS one drops a bounded repeat to literal
replication, which is what ships today and is therefore the semantic ground
truth its differential compares against. `unroll_k` is its value parameter
(K, `PCREC_UNROLL_K_DEFAULT` = 0 meaning `PCREC_DEFAULT_UNROLL_K` in
src/core/limits.h): ONE value per artifact, never per quantifier (D47
ADDENDUM held §4.5 strictly; the clamp that would have varied K moved whole
to plan row [ENG-CLAMP]).

`work_budget` (`PCREC_WORK_BUDGET_DEFAULT`/`_NONE`, `--work-budget=N`) is the
THIRD DD-2 bound, ruled at the D47 SECOND ADDENDUM's settlement 4: work units
spent on forward work the fail label never sees — frames discarded at a cut,
frameless scan iterations — reported as `PCREC_ERR_WORK` (unprefixed since
[ABI-NS], D60). It is a SEPARATE
counter from `step_budget`, which keeps its exact meaning of one backtrack
resumption; nothing is scaled into anything. ONE existence gate in v1 (D49):
`--fno-step-budget` suppresses both counters, which keeps the tests/vm
no-counter pin true as written; splitting the gate later is additive.

Note the deliberate split of homes, since the two constants look alike and are
not: K lives in `src/core/limits.h` because changing it changes what pcrec
ACCEPTS (it decides how many copies a bounded repeat emits, against the
replication caps), while the work budget's default lives beside its siblings in
`src/gen/emit_vm.c` because a runtime give-up budget changes nothing pcrec
accepts, rejects or promises — limits.h's own stated inclusion rule, applied in
both directions.

**[M4.6d] (2026-08-17):** `PCREC_NO_LENGTH_PRUNE` (`1u << 7`,
`-fno-length-prune`) denies MINIMUM-REMAINING-LENGTH pruning (D51 ruling 1).
Same masked-out-of-`rx_info.flags` treatment as its three siblings and for the
same reason. It is the strongest case in the family for that rule: MRL emits a
bound on whichever rung a quantifier already took and changes no rung, slot or
capacity, so a denied artifact is byte-for-byte pre-MRL pcrec — which is what
makes it a differential ground truth, and what a stamp announcing the denial
would destroy.

**[M4.6f] (2026-08-17):** `PCREC_NO_PREFILTER` (`1u << 8`,
`-fno-prefilter`) and `PCREC_FORCE_PREFILTER` (`1u << 9`, `-fprefilter`)
are the D46 close-out for the PREFILTER axis (`fit.prefilter`,
src/opt/select_engine.c, engine_m4.md §6.1/§4.7) — a DIFFERENT SHAPE from
the four bits above and deliberately so: those deny a per-QUANTIFIER
strategy (D47.3's reasoning for DENY over FORCE), while `fit.prefilter` is
ONE verdict for the whole artifact, decided jointly with `--engine`
(auto+captures turns it on, `--engine=vm` turns it off as a side effect,
R21 E-6) with no way before this to ask for the combination independently.
So this is a FORCE PAIR — both directions independently reachable, which is
what decouples "which engine" from "does the hybrid prefilter run ahead of
it". DO-OR-DIE on the FORCE-ON direction only: `PCREC_FORCE_PREFILTER` on a
pattern that compiles to the DFA engine (no VM artifact exists to attach a
prefilter to) REFUSES, the same `--engine`-precedent posture; `PCREC_NO_PREFILTER`
never refuses, because `--engine=vm` already ships that exact
prefilter-free configuration today. Same masked-out-of-`rx_info.flags`
treatment as the four bits above and for the identical reason: the axis
changes no answer, only how one is found. What it DOES is recorded in
`RX_VM_PREFILTER` (src/gen/emit_vm.c, `"hybrid"`/`"none"`) — a SCALAR
string like `RX_ENGINE`/`RX_VM_PRUNE_CEILING`, not a bitmask like
`RX_VM_RUNGS`/`RX_VM_STRATS`/`RX_VM_PRUNES`, because the verdict is
artifact-level rather than per-quantifier and there is nothing to mix.
**[DD-13], 2026-08-25:** the DFA has its own prefilter axis and its own
stamp for it (`RX_DFA_PREFILTER`, five values — src/gen/emit_dfa.c), which
is a DIFFERENT vocabulary rather than this macro widened; `RX_ENGINE` is
the one D46 macro that is now UNCONDITIONAL on both engines
(docs/spec/match_api.md §6.3's (a)/(b) split).
Tests: tests/prefilter/, tests/codegen/run_dfa_stamps.sh.

**[OPT-ALTCLS] (2026-08-17):** `PCREC_NO_ALTCLS_MERGE` (`1u << 10`,
`-fno-altcls-merge`) and `PCREC_NO_ALTCLS_FACTOR` (`1u << 11`,
`-fno-altcls-factor`) are D46's controllability half for
`src/opt/altcls.c` (docs/dev/plan.md's `[OPT-ALTCLS]` row: stage 1 merges a
maximal run of single-char alternation branches into one class, stage 2
prefix-factors a maximal run sharing a literal first byte, running on stage
1's output). BACK to the DENY-only shape the five-member family above uses,
not `PREFILTER`'s force pair — the original reason applies here rather than
the prefilter's exception to it: each mergeable/factorable run is its own
selection point, addressed independently the way each `A_REP` walks its own
possessify/revdet ladder, so there is no artifact-wide verdict for FORCE to
solve an addressing problem for. Two bits rather than one because the two
stages are separately useful to pin, exactly as `-fno-revdet` denying the
rung still leaves possessification live one rung down. Same
masked-out-of-`rx_info.flags` treatment as the rest of the family and for
the identical reason. What the pass DID is recorded in
`<PREFIX>_ALTCLS_MERGES`/`<PREFIX>_ALTCLS_FACTORED` (src/gen/emit_dfa.c's
`pcrec_emit_prologue`) — UNLIKE every other D46 stamp in this file, these
are NOT VM-artifacts-only: the pass runs before either engine is built, so
a capture-free pattern's DFA artifact carries the stamp too. Tests:
tests/altcls/.

**[M4.7g] (2026-08-18, R29 fix lane):** the `<prefix>_search` doc comment is
corrected, and the defect is worth knowing because it survived the [M4.4]
rewrite, a manager read and the spec graduation. It presented the `int`
return as TWO-VALUED (1 on a match, 0 on no match), under which the natural
`if (rx_search(...))` reads an engine GIVE-UP as a match — measured: −3 from
`<prefix>_search` on `(a|aa)+b` built `--backtrack-frames=1`. The comment now
names the negative give-up space (`PCREC_ERR_STEPS`/`_FRAMES`/`_WORK`
inside [`PCREC_ERR_FLOOR`, −2], D49 — unprefixed since [ABI-NS], D60),
says the return is not two-valued,
and states that a give-up leaves `caps` UNTOUCHED like any other failure.
Three adjacent staleness fixes rode along: "RX_NCAPS is 1 on every artifact
this milestone emits" predated M4.5's captures default; `extern const
rx_info <prefix>_info` predated D57's blessed struct-TAG spelling; and the
ABI type list now matches the emitted declaration order. The comment also
now points at `docs/spec/match_api.md` as the authoritative contract rather
than only at the design record — that spec, not this header, is where the
full surface is stated. The emitted `rx_matchfn` ABI comment
(src/gen/emit_dfa.c) had the SAME defect in its own words and was fixed in
the same commit; see the R29 review and the journal entry for both.

**[M5-SEAM] (2026-08-18, D58):** the ENCODING enum is RENAMED and the
`<prefix>_search` doc comment gains the seam's fifth entry.

`PCREC_ENC_ASCII` is now `PCREC_ENC_BYTE`, with NO compatibility alias, and
`-e ascii` is consequently an unknown encoding. Two names for one namespace
member is [SR-10]'s motivating defect, so an alias was the wrong shape; the
old name also asserted something false, since this encoding treats every
byte as a character (`0x80` and up included, with no case and no meaning
attached), which is precisely what "ASCII" does not say. D58's own ruling
text names the encoding `byte`. Taken as one announced boundary under
docs/spec/match_api.md §9's pre-v1 posture.

The enum's comment now also states the PER-COMPILE-CALL rule (D58 ruling 2,
DD-12 (8)): the encoding is this field and nothing else — no process
global, no file global — so mixing encodings in one compilation unit or
binary is supported by construction. The NAMES themselves are defined by
one table, `src/gen/enc/enc.c`; neither `src/core/compile.c` nor
`cli/main.c` maps an encoding name of its own any more, which was
[SR-10]'s recorded instance.

The generated-searcher comment gains `<prefix>_next_pos` alongside the
three entries it already enumerated — the ENCODING RESIDUAL, the next
CHARACTER boundary strictly after `pos`, and the one place an artifact's
byte-vs-character distinction lives. Its contract is
docs/spec/match_api.md §3.1.1; the comment here carries the one warning a
caller needs (do NOT inline the `+ 1` back — that is the single edit that
makes a byte-compiled caller wrong against another encoding's artifact),
because a find-all loop is code the caller writes and this header is what
they read while writing it.

## [DD-14 wave G] `PCREC_NO_SPLICE_CALLS` (bit 13)

Deny the SPLICE linkage at every call site, forcing the CALL linkage everywhere.

**IT IS NOT IN `emit_info_def`'s `strategy_denials` MASK, AND THAT IS THE
DECISION WORTH KNOWING.** Every other member of that mask is a knob with NO
OBSERVABLE EFFECT — the mask exists so two artifacts that behave identically do
not differ in their reflection surface. This flag SELECTS AN ENGINE: a spliced
call has an exact finite lowering, a linked one does not, so denying the splice
can turn a DFA artifact into a VM one. `rx_info.flags` therefore RECORDS it, for
the same reason it records `PCREC_NO_ATOMIC_DISCHARGE` — the one other member of
the deny family with that property.

**THE CONSEQUENCE IS RULED AND WRITTEN DOWN IN TWO PLACES** (design §9.1,
`tests/codegen/run_recursion_identity.sh`'s header): a flag that honestly records
itself cannot be compared byte-for-byte against a compiler that does not have
it, so the identity gate's linkage claim is a SUBJECT-AGAINST-ITSELF section
rather than a fifth reference axis. **Do not "fix" that by adding this bit to
the mask** — it would falsify the artifact's own record of itself to satisfy a
check.

## [DD-13b.W1.2] `pcrec_options.name` (2026-08-31)

One new field, APPENDED so no existing member's offset moves: the artifact's
own NAME, emitted as `rx_info.name` (`docs/spec/match_api.md` §6).

**It is not derivable from `prefix`, which is why it is a field.** `prefix`
says what this artifact's SYMBOLS are called; `name` says what the artifact
IS. A `.rxt` source's `target <prefix> = <definition>` builds one definition
under a prefix, and three targets naming one definition are three artifacts,
three prefixes and ONE name — which is exactly what a consumer walking
several `<prefix>_info` symbols in one binary needs in order to say "these
three are the same matcher, built differently".

**NULL MEANS "use `prefix`", and that IS the rule** Frank ruled at
format_design §6.3: no artifact ever carries a NULL name. So every caller
that predates the field — every `pcrec_compile` in the tree, every CLI
compile without `--source` — stamps its own prefix and needs no edit, and
the emitter has no NULL case to get wrong. `pcrec_default_options`'s
`memset` supplies the NULL; nothing had to be added there.

It is a NAME and not a symbol: it is emitted as a string literal, no
generated identifier derives from it, and it is unconstrained by C
identifier syntax. `.rxt`'s own `name` grammar is stricter, and that is
that format's rule rather than this field's.

## [DD-14.FB] the generated-API comment names three more entries (2026-08-25)

`pcrec.h`'s "Generated searcher contract" block now names
`<prefix>_search_in` / `<prefix>_match_in` / `<prefix>_match_caps_in`, the
`<prefix>_buffers` descriptor and the five sizing macros. Nothing in the
LIBRARY's own surface changed — no new option, no new struct member, no
signature moved — so this is a documentation edit to a header, not an API
change to it. The types themselves stay where every other per-artifact type
does: in the generated `.c`/`.h`, never here, because they are
PER-ARTIFACT-EMITTED (a resume frame is 24 bytes on a call-free artifact and
40 on a call-bearing one, MEASURED). The authoritative contract is
docs/spec/match_api.md §10.
