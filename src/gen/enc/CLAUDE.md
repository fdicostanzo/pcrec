# src/gen/enc — the ENCODING BACKENDS

The DD-12 residual seam, built at [M5-SEAM] (D58, 2026-08-18) as a prelude
to M6 so M6's encoding-sensitive residue is born on the seam rather than
retrofitted onto it. Everything an artifact carries that depends on which
ENCODING it was compiled for lives in this directory, in exactly one file
per encoding.

## The rule this directory exists to make structural

DD-12 (7), ruled in as a requirement by Frank: **no encoding conditionals
anywhere** — not in the compiler, not in the emitter, not in the emitted
artifact. Encodings are SEALED BACKENDS, and the only "switch" is WHICH
backend's text an artifact embedded. So there is no `if (enc == UTF8)` in
this tree, and adding one is the design-stop signal, not a patch.

The complementary half is that the per-encoding header is the RIGHT seam
for the enumerable runtime-identity RESIDUE and the WRONG seam for the HOT
PATH (gcc cannot invert decode+compare back into a byte automaton;
malformed-input handling would degrade from automaton structure to runtime
branches). Enforced, not asserted: `tests/codegen/run_codegen_tests.sh`'s
`[M5-SEAM/DD-12(7)]` check reads every emitted engine body for a residual
reference, sabotage-validated by
`tests/mech/sabotages/S68_residual_in_hot_loop.sh`. That sabotage changes
no ANSWER — under the byte backend the residual is the identity — which is
exactly why a structural check is the only instrument that can see it.

## Files

**[M5.0] `PcrecEnc` GAINED ONE SCALAR, AND THAT IS A D58 SEAM EVENT.**
`max_cp` — the greatest code point the encoding has, `0xFF` for `byte` and
`0x10FFFF` for `utf8` — and the ONE question that reads it is "what does
`[^x]` mean here" (`docs/design/utf8_design.md` §2.7.1, §2.7.2). It is not a
code-unit width and not a validity predicate.

**IT IS RECORDED RATHER THAN QUIETLY ADDED, because the design's §5 opened by
claiming the opposite.** r54 E2 retracted "the seam needs no interface change":
what survives is the claim the third-encoding recipe below actually makes — the
ENTRIES TABLE is untouched by the second backend (four residual bodies under
their existing signatures, no `PcrecEncEntry` field, `pcrec_enc_ready`
untouched, both emit functions untouched, this directory's recipe unchanged) —
and `PcrecEnc` itself gains this one scalar. D58's revisit clause asks for
exactly that distinction to be written down.

**THE PENDING `utf8` ROW CARRIES `0x10FFFF` THOUGH IT HAS NO BACKEND.** The
field answers a question about the ENCODING, not about whether pcrec can
compile it, and a `0` there would mean "complement within `{0}`" the day the
backend lands — a wrong value waiting for a reader, which is D67 contract note
2's unsound direction. `pcrec_enc_ready` still refuses the encoding by name, so
nothing reads it today.

**A CODEPAGE BACKEND WILL NOT FIT IT** (§5.7.3, R-ASKS-3(b)): a codepage's
repertoire is 256 code points SCATTERED across Unicode, so no maximum
describes it and this field is the contiguous-repertoire special case of "what
set does a complement complement within". Recorded with its trigger under D77,
not built for.

**[M5.0] STAGE 2: `enc_utf8.c` LANDED — THE SEAM'S SECOND BACKEND, AND THE
THIRD-ENCODING RECIPE'S FIRST EXECUTION.** One new file in this directory, one
`extern` in `enc.h`, one row swap in `enc.c` (the pending `entries == NULL`
row became `&pcrec_enc_backend_utf8`); NOTHING in `src/core`, `src/gen` outside
this directory, `cli/` or `lib/` was touched to make `-e utf8` compile — which
is the recipe below working as ruled. The entries table's INTERFACE is
unchanged (D58's revisit clause honoured by having nothing to record there):
the four residual entries carry UTF-8 bodies under their existing signatures,
no `PcrecEncEntry` field was added, `pcrec_enc_ready` is untouched, both emit
functions are untouched. `back_step` carries §5.2.1's declared-length repair
(the line that makes a malformed run answer `BACK_STEP_NONE` rather than a
position the forward parse disagrees with); the two `bref` compares are the
byte backend's bodies verbatim (`utf8-exact`, UTF-8 being a prefix code) plus
an ASCII-only fold (the non-ASCII closure is stage 4's). `tests/codegen/
run_encoding_checks.sh`'s DD12a(ii) is the second-backend validation that the
signatures match across both backends.

**[K49] `PcrecEnc` GAINED A SECOND SCALAR — `advance` — AND IT IS A THIRD KIND
OF CONTRIBUTION, not a fifth entry.** D58's revisit clause asks for exactly
this to be written down, so: the entries table above is a table of FUNCTIONS an
artifact exports; `advance` is INLINE TEXT spliced into an engine body, the
statements that move a failed unanchored attempt's START to the next position
the search may try. `pos++` under `byte`, `pos++` then skip continuation bytes
under `utf8`. The entries table's interface is again untouched — no
`PcrecEncEntry` field, no signature change, `pcrec_enc_ready` untouched, both
emit functions untouched — and the third-encoding recipe below grows by one
line: a backend now also writes its `advance`.

**WHY IT COULD NOT BE A CALL TO `next_pos`, which computes exactly this
position.** Two independent reasons that happen to agree. `next_pos` carries
`engine_callable = false`, and DD-12 (7), `tests/codegen`'s [M5-SEAM] check and
sabotage row S68 all forbid an engine body calling it. And a call would have
MOVED THE BYTE ARTIFACT, turning D76's identity gate from a proof into a
re-pin.

**WHAT K49 REFUTED, because the rationale one paragraph down was the thing
that was wrong.** `next_pos`' `engine_callable = false` is justified below by
*"unanchoredness is the automaton's own self-loop, so there is no external
advance for an engine to route through."* **There is.** The emitted VM's
`<prefix>_search_run` has always carried `attempt_position++`, a genuine
external advance in shared emitter code, and while it stepped one byte a
`utf8` search could retry inside a character and — on a leading negative
assertion, which succeeds exactly where its body has no path — report a match
there. The CONCLUSION (`engine_callable = false`) survives and the REASON is
replaced: the engine does not call the entry because the advance is emitted
inline from this field instead. `docs/design/utf8_design.md` §5.5 carries the
same refutation for its own version of the claim, and the DFA half of it is
still open as K50.

**THE RULE IS NOW SPELLED TWICE PER BACKEND** (`advance` and `next_pos`), and
that is a drift hazard this directory already has a precedent for: the caseless
compare and `cls_casefold` are two spellings of one fold, tied by
`tests/backrefs/fold_agreement_check.c`. The tie here is
`tests/codegen/run_encoding_checks.sh`'s K49 advance-agreement section, which
EXTRACTS the advance from an emitted artifact, compiles it, and compares it
against that same artifact's linked `next_pos` over an exhaustive sweep of a
role-complete byte alphabet — with non-vacuity asserted in both directions
(`byte` must answer `pos + 1` everywhere, `utf8` must not, somewhere).

**[K50] `PcrecEnc` GAINED A THIRD AND FOURTH CONTRIBUTION — `start_cls` AND
`start_guard` — AND THEY ARE ONE RULE ASKED AS A PREDICATE RATHER THAN AS A
STEP.** D58's revisit clause again, so: `advance` says how to MOVE a failed
attempt's start; these say WHERE a match may BEGIN. Two consumers need the
predicate and neither can use a step. `src/ir/nfa.c`'s `nfa_wrap_unanchored`
is not a loop the emitter can see at all — it is an AUTOMATON, and gating its
split needs the rule as a BYTE SET evaluated inside the subset construction.
`src/gen/emit_dfa.c`'s `ENG_ATTEMPT` start loop cannot take the `advance` text
without moving every byte artifact: its step is a `for` header's increment, and
replacing that with a trailing statement is exactly the emitted-scaffolding
move D76 makes an abi event, so it takes a `continue` guard instead — which is
ADDITIVE, and a backend with no restriction contributes nothing.

**BOTH ARE NULL UNDER `byte`, AND THAT IS THE ANSWER RATHER THAN A DEFAULT.**
Every position is a character boundary there, so the IR builds no gate node,
neither emitter emits a guard, and `PCREC_NO_STARTPOS_GUARD` is masked out of
`rx_info.flags` because it could not have acted — which is what makes "the
encoding with no defect pays nothing for K50's fix" a construction rather than
a comparison. A backend that wrote out the tautology instead would be honest
and would move every artifact in the tree for nothing.

**THE RULE IS NOW SPELLED FOUR TIMES PER BACKEND** (`next_pos`, `advance`,
`start_cls`, `start_guard`), which is the drift hazard this directory already
had at two and has a precedent for at both. The tie is the same one:
`tests/codegen/run_encoding_checks.sh`'s advance-agreement section, plus
`tests/utf8/run_startbnd_diff.sh`, which reads the emitted guard out of a real
artifact and sweeps it against an INDEPENDENTLY WRITTEN boundary predicate in
its driver — never against the backend's own text.

**AND `start_cls` OWES A DISJOINTNESS THE DFA CHECKS RATHER THAN ASSUMES.** The
subset construction carries the boundary property on its CLASS AXIS
(`UPC_NOSTART`), which is a PARTITION, so a byte that is not a character start
must be neither a word byte nor a newline. UTF-8 satisfies it (continuation
bytes are 0x80..0xBF; both other sets are ASCII). A backend that does not is
refused at `pcrec_enc_start_cls_ok()` with an internal error, because the
failure mode is SILENT: a non-start byte classified `UPC_WORD` would read as a
character start to the gate and re-open K50.

**ONE CLAUSE OF THE utf8 GUARD IS A RULING AND NOT ARITHMETIC.** It opens
`@P == 0 ||`, because offset 0 is always a valid start even on a subject that
begins with a continuation byte. The byte test is LOCAL, which is what libpcre2
asks under `PCRE2_UTF` — but libpcre2 asks it only after a whole-subject
validation pass has already rejected such a subject, and `utf8_design.md`
§2.6/ASK 1 rules that pcrec has NO such pass ("no validation pass, no error
return"). Without the clause the guard turns "an ill-formed sequence matches
nothing" into "ill-formed input is an error". MEASURED as a defect before it
was a clause: 21 oracle-verified `tests/utf8` cells stopped answering.

- **enc.h** — the seam's whole interface: the `PcrecEnc` row (id, the ONE
  spelling of the encoding's name, the complement universe `max_cp`, a
  NULL-terminated table of `PcrecEncEntry` rows, [K49]'s `advance` text, and
  [K50]'s `start_cls`/`start_guard` pair),
  the entry ids that are also the bits of a
  per-artifact MASK, the registry accessors, `pcrec_enc_emit_text` and
  `pcrec_enc_advance`. Read
  its header comment before adding a backend; it carries the third-encoding
  recipe and the reason a backend is TEXT rather than emitter code.

  **THE ENTRIES BECAME A TABLE AT [M6.5.2], and that is D58's own revisit
  clause being honoured** — *"the second consumer is the seam's validation
  event; ANY INTERFACE CHANGE IT FORCES GETS RECORDED AGAINST THIS ENTRY."*
  The second consumer arrived early (a caseless backreference compare) and it
  forced one: with three entries, two unconditional text blobs would put two
  exported functions of DEAD CODE into every artifact pcrec has ever emitted,
  including one with no backreference in it. They cannot be `static` (an
  unused `static` fails the harness's `-Werror` generated-code build, which is
  why `next_pos` is exported), so they would be LINKED dead weight. A
  per-entry mask keeps the cost where the construct is. The road not taken was
  two more string fields — simpler, and it does not generalise: lookbehind's
  back-step ([M6.6]) is the next residual entry D58 already names.

  **THAT PREDICTION WAS TESTED AT [M6.6.2] WAVE D AND IT HELD, WHICH IS THE
  FINDING** (lookaround_design.md §4.3, prediction P-1). The back-step landed
  as ONE enumerator (`PCREC_ENCE_BACK_STEP`), ONE `entries_byte[]` row, and
  one `|=` in the emitter's `A_LOOK` arm. **No field was added to
  `PcrecEncEntry`, no signature changed, `pcrec_enc_ready` was untouched, both
  emit functions were untouched, and the third-encoding recipe below is
  unchanged.** D58's revisit clause — *"any interface change it forces gets
  recorded against this entry"* — is honoured here by having nothing to
  record, and this paragraph is that record.

  `pcrec_enc_ready` moved with it (from `decls != NULL` to "has a non-empty
  entries array"), which R32 E11 found: the readiness predicate is a THIRD
  site the change touches, not the two emit functions alone, and the
  `-e utf8` refusal path reads it.

  **`engine_callable` is the other half**, and it is a fact about the ENTRY
  rather than about any artifact. **It has a consumer on the compile path, not
  only in a test**: `src/gen/emit_vm.c`'s `A_BREF` arm asks
  `pcrec_enc_entry_engine_callable` before it emits the call, so an emitter may
  route a construct through a residual entry only if the BACKEND says that
  entry may be called from an engine body. That is the same rule
  `tests/codegen`'s [M5-SEAM] check enforces from OUTSIDE, enforced from
  INSIDE at the one site that could break it — a backend whose compare
  declared `false` would otherwise emit an artifact the codegen check rejects
  two steps and one test run away from the cause. Failing direction
  demonstrated by flipping the byte backend's `PCREC_ENCE_BREF` row to
  `false`: `(a)\1` refuses by name instead of compiling. `next_pos` carries `false`: unanchoredness
  is the automaton's own self-loop, so there is no external advance for an
  engine to route through, and an engine that DID route through it would match
  identically under this backend while changing the hot path's shape under any
  other. The two backreference entries carry `true`, because a backreference
  compare has NO automaton representation whatsoever — forbidding the call
  forbids the construct.
- **enc.c** — the registry TABLE (the encoding namespace's one definition),
  the by-id/by-name lookups, the rendered name menu for diagnostics, and the
  `$`-to-prefix substitution every backend's text goes through. The table
  carries a row for `utf8` with NO backend on purpose: a name pcrec knows
  but cannot compile must be refused BY ITS OWN NAME (`src/core/compile.c`
  reads the row's `name`), never fall out of a lookup as "unknown". That is
  [SR-10]'s single-namespace rule applied to the half this table owns — its
  motivating instance was compile.c's diagnostic and cli/main.c's name
  mapping drifting apart, and neither of those sites maps an encoding name
  of its own any more.
- **enc_utf8.c** — the `PCREC_ENC_UTF8` backend ([M5.0] stage 2). Four
  residual bodies where a character is one to four bytes: `next_pos` skips
  forward over continuation bytes; `back_step` walks back one
  DECLARED-LENGTH-validated run per step (§5.2.1's repair — a malformed run
  answers `BACK_STEP_NONE`); the case-sensitive `bref_match` is `enc_byte.c`'s
  body verbatim (UTF-8 is a prefix code, so an exact compare is a byte
  compare); the caseless one folds the 52 ASCII letters and nothing else (the
  non-ASCII simple-fold closure is stage 4's, and the LENGTH-return protocol is
  what will let that land without the shared emitter changing). [K49] added its
  `advance`: `next_pos`' boundary rule written as an inline step, because an
  engine may not call the entry — the two are tied by the advance-agreement
  check named above rather than left to drift. Text, not
  emitter code, ASCII-only, `$` the one substituted character — `enc_byte.c`'s
  rules.
- **enc_byte.c** — the `PCREC_ENC_BYTE` backend. One byte is one character, so
  every residual entry is the identity shape or
  close to it, and [K49]'s `advance` is the bare `@P++;` the emitter used to
  hard-code — reproduced character for character, which is the whole of this
  backend's stake in that fix: the byte artifact does not move. It carries no
  comment into the artifact on purpose; a comment there would be new emitted
  scaffolding on exactly the path D76's identity gate pins. FOUR entries today, each with its contract comment emitted
  into the artifact alongside its declaration — the contract lives with the
  backend so a future backend cannot land a residual declaration nobody wrote
  a contract for:

  - `<prefix>_next_pos` — the next character boundary strictly after `pos`,
    every position >= n counting as a boundary.
  - `<prefix>_bref_match` / `<prefix>_bref_match_caseless` ([M6.5.2]) — the
    backreference compare, case-sensitive and case-folding. **TWO ENTRIES, NOT
    ONE WITH A FLAG**: D18/D23's rule is that an option compiles away, and D23
    MEASURED the alternative (a runtime fold indirection) costing 26% on a
    pattern containing no letters at all.
  - `<prefix>_back_step` ([M6.6.2] wave D) — the position exactly `k`
    CHARACTERS before `pos`, or `<prefix>_BACK_STEP_NONE` when fewer than `k`
    characters precede it. **A SENTINEL RATHER THAN A SIGNED LENGTH**, and the
    divergence from the compare's protocol one bullet up is deliberate: a
    back-step's failure carries no second fact, and the WORK it did is `k`,
    which the caller already knows AT COMPILE TIME and charges with a literal
    (lookaround_design.md §3.7). `(size_t)-1` cannot collide with a legal
    position, because a legal position is <= n and a SIZE_MAX-byte subject is
    not representable. `s` and `n` are parameters this backend ignores because
    a UTF-8 backend walking back over continuation bytes must reject a
    MALFORMED sequence — a failure mode the byte backend cannot have — and
    adding a parameter later is the ABI break the seam exists to avoid.
    ENGINE-CALLABLE, for the compares' reason: a back-step has no automaton
    representation, so forbidding the call would forbid the construct.

  **THE RETURN IS A LENGTH, AND THE SIGN CARRIES A SECOND FACT**, and both
  halves are designed for the backend that does not exist yet. Under this
  backend the compare cannot change length — but `(?i)^(ss)\1$` on "ss\xdf"
  is the cell a UTF-8 build has to answer differently, with one captured
  character folding to two and the consumed length no longer equalling the
  captured one. Returning a LENGTH is what lets that backend give a different
  answer WITHOUT THE SHARED EMITTER CHANGING A CHARACTER: it never computes a
  length, it only adds the one it is given. On failure the value is negative
  and `-(r) - 1` is the prefix that DID compare equal — the work a
  `(a*)\1`-shaped compare does before failing, which the fail label never sees
  and the work budget must therefore be told about. A bare `-1` sentinel could
  not carry it (R32 E4: the first design recommended charging that prefix and
  its own signature could not express it).

  **THE FOLD IS SPELLED ARITHMETICALLY AND IS TIED TO pcrec's OWN.** A
  `tolower()` here would be a DEFECT rather than a shortcut — it is
  locale-dependent at the CALLER's run time, in a locale pcrec does not
  control, and an artifact whose answers change with `setlocale` is not the
  self-contained matcher APPROACH promises. What keeps this spelling in step
  with `cls_casefold`'s is `tests/backrefs/fold_agreement_check.c`, which
  walks all 65,536 ordered byte pairs against `pcrec_ascii_fold`
  (src/core/fold.c) with the residual side read out of an artifact pcrec
  actually emitted.

## Adding a backend (the DD-12 third-encoding recipe)

One new `enc_<name>.c` here, plus its `extern` in `enc.h` and its row in
`enc.c`'s table. The row carries the backend's residual ENTRIES, its `max_cp`,
(since [K49]) its `advance` text, and (since [K50]) its `start_cls` byte set
and `start_guard` expression — all five in this directory. A backend that
restricts no position writes NULL for the last two and is complete.

Both of those files are in THIS directory; the Makefile
already globs `src/gen/enc/*.c`. **Nothing in `src/core`, `src/gen`, `cli/`
or `lib/` is touched.** If a backend ever requires touching a shared file
outside this directory, that is the derailment DD-12 names — stop and take
it to a design decision rather than patching the shared file.

Two constraints on the residual text itself:

- **`$` is the prefix placeholder and the only character substituted**, so
  residual text must contain no other `$`.
- **Emitted text is ASCII-only**, including inside comments — the artifact
  is source someone else's toolchain compiles (src/gen/CLAUDE.md's standing
  rule).

## Where the seam is consumed

`src/gen/emit_dfa.c`'s `emit_residual_decls`/`emit_residual_defs` (the
declarations ride `pcrec_emit_prologue`, so they land in the `.h` of a split
artifact and the `.c` of a self-contained one; the definitions ride the
exported `pcrec_emit_residual`, called by BOTH emitters). Those two
functions are the entire extent of the emitter's knowledge about encodings:
look up the backend, copy the text of every entry the artifact's MASK names,
substitute the prefix.

**THE MASK IS DISCOVERED BY EMITTING, not predicted.** `Job.enc_mask` starts
at `PCREC_ENCE_NEXT_POS` (promised unconditionally by
docs/spec/match_api.md §3.1) and the VM emitter ORs in whichever compare
entries its `A_BREF` arm actually emits calls to — which is why the prologue
is written AFTER the program body, the same discipline the class pool and the
cursor local already follow. So "the artifact declares exactly the entries it
calls" is true by construction, and a backref-free artifact carries exactly
the residual text it always did.

`src/core/compile.c` gates on the registry (a member with no backend is
refused, a non-member is refused with the rendered menu) and `cli/main.c`
resolves `-e NAME` / `--encoding=NAME` through `pcrec_enc_by_name`.

Maintenance: update this file when files are added/removed or their roles
change.
