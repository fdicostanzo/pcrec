# [M6-READ] CONVERSION LOG — what the emitter conversion found

The style of record is `README.md`. This is the other half: **what building it
taught**, kept because the findings are more transferable than the diff.

The conversion landed as one (or two) green commits; this document is the
record those commits collapsed. Each entry keeps its original step, what went
red, and what the fix was, so a reader can reconstruct the sequence without
the hashes.

Every number here was measured. Where a claim is inference rather than
measurement, it says so.

---

## The shape of the whole thing, in two sentences

**The differentials never noticed the rename, because they compare ANSWERS;
the population checks noticed instantly, because they read TEXT.** And: the
neutrality gate proves SAMENESS, while the existing two-artifact differentials
prove COMPILABILITY under harder conditions — this pass needed both, and the
second caught what the first could not.

---

## Step 1 — close the vacuous-pass hole BEFORE renaming

`run_ir_listing.sh`'s SLOTS block compared two extractions that are both
pattern-matched SPELLINGS the emitter writes: `RX_SET(<slot>` in the `.c`,
`set stv[n]` in the listing. Renaming them together is the only CORRECT way to
rename them, and it makes both greps match nothing — after which `diff -q` on
two empty files passes.

**Watched failing, three states, run from the script's real directory:**

| state | old check | new check |
|---|---|---|
| unsabotaged | 79 / 0 | 80 / 0 |
| listing side moved ONLY | 68 / 11 — already caught | 69 / 11 |
| **BOTH sides moved** | **79 / 0 — 11 empty-vs-empty passes** | 69 / 11 |

The middle row is why this was not redundant work: the one-sided sabotage was
*already* caught, so a validation that only tried it would have concluded the
block was safe and skipped the work. Only the both-sides case is vacuous, and
that is the case the conversion actually produces — twice over, because the
listing's prose moves with the emitter AND the slot legend stops the artifact
writing `RX_SET(2,` at all.

**It fired for real, eleven times**, when the listing was renamed and its grep
was not: *"the .c writes 2 slot(s) but the listing-side extraction found none;
the listing's wording changed and this check had stopped reading it."*

**And its macro-resolution half cost nothing later.** Teaching the `.c` side to
resolve symbolic `RX_SET` operands against the artifact's own `#define` lines
meant that when the emitter started writing `RX_SET(RX_SLOT_GROUP1_START, ...)`
the check kept working with **no pin touched at all**. That is the argument for
resolution over a flag-day grep swap, demonstrated rather than asserted.

**Found on the way:** the old numeric-only grep was matching `RX_SET`'s own
`#define` line and silently dropping the operand, because the macro PARAMETER
name (`slot_`) is not `[0-9]+`.

**Process confession worth keeping:** the first sabotage run was done from the
scratchpad and reported 2/20. That is the script's path discovery breaking, not
the sabotage firing — the exact trap `tests/codegen/CLAUDE.md` already
documents. It was caught only because the number was implausible.

---

## `_t` IS NOT PATTERN-SAFE IN C

The rename tool rewrites identifiers inside C string literals. Applying it to
the ENG_ATTEMPT table suffix `_t` (the per-state jump rows, `%s_t%d`) also ate
the tail of `size_t` and `ptrdiff_t`, and the emitter cheerfully produced:

```c
int rx_search(const unsigned char *subject, size_targets_ subject_length,
              size_targets_ search_from, ptrdiff_targets_ (*capture_spans)[2])
```

**No lookaround fixes this.** The tail of a standard type name and a table
suffix are the same three characters, in the same lexical position, with the
same neighbours — there is no context that distinguishes them. Reverted; the
ENG_ATTEMPT and VM prefixed names are done as a fixed list of exact strings
instead.

The general rule: **a rename map for emitted C may contain no entry that is a
suffix of a C keyword or standard type.** `_t` is the one that bites, and it
bites silently — the emitter builds fine and the artifact does not.

---

## The rename reaches ENGLISH, four distinct ways

Emitted comments and the `--emit-ir` listing are string literals too, so an
identifier rename **is also a prose edit**. Four mechanisms, all measured:

1. **Possessives.** `gcc's` became `gcc'subject` — the `s` after an apostrophe
   is a bare token. It SHIPPED into one emitted comment through a green gate,
   because a comment is object-neutral and the gate is right not to care.
   Found by reading the output.
2. **Pluralisation literals.** `"%d of %d source quantifier%s possessified"`
   passes a bare `"s"` for the plural. It became `"subject"`, so the listing
   read *"2 of 2 source quantifiersubject possessified"*, and
   *"capturing groupsubject"*.
3. **An apostrophe inside a quoted shell context.** A comment I added inside an
   `awk '...'` program contained the word `table's`, which terminated the
   single-quoted string. Caught by `bash -n`.
4. **Articles.** `"the reported START of the match"` became `"the reported
   attempt_position"` — a semantic reversal in prose a user reads.

Tooling now guards (1) and (2) — the exclusion set covers apostrophe- and
backslash-preceded tokens. **Nothing catches (3) and (4) except diffing the
emitted output and the listing against the PRE-CONVERSION BINARY and reading
them.** That diff became the standing procedure after every slice.

---

## TS-1 scans emitted COMMENTS, and the fix is to reword them

`tests/codegen`'s TS-1 sweep looks for non-reentrant/allocating symbols in
emitted code and deliberately does NOT strip comments — its own CLAUDE.md
rules the resolution: *"an emitted comment that merely mentions a denylisted
symbol will trip it; that is deliberate, and the fix is to reword the comment
rather than to weaken the list."*

It fired twice on this pass, both times on the word **`free`**:

- the orientation block's *"a complete, dependency-free matcher"* — six
  artifacts red. Reworded to "self-contained", which is the header's own term.
- the CHARGE_WORK block's *"a slow attempt would look free"* — reworded to
  "look costless". This one appeared late, because the comment was added after
  the previous codegen run, and it is the reason the suite is re-run after
  every emitted-comment edit rather than at the end.

**Every word added to an emitted comment is scanned by TS-1.** (`abort` also
appears in emitted prose, in the pre-existing D49 block — it is emitted by
main's compiler too and TS-1 tolerates it, so it is not this lane's concern.)

## Longer names silently TRUNCATE in fixed `char` buffers

Three sites, one of which made the listing lie:

| site | before | after | symptom |
|---|---|---|---|
| `char slot[24]` (IR listing) | `stv[2] <- pos` (13) | `slot_values[2] <- scan_position` (30) | listing printed `slot_values[2] <- scan_` — **it misreported the slot write** |
| `char accept_tr[160]` | | | gcc `-Wformat-truncation` |
| `char pop_tr[224]` | | | gcc `-Wformat-truncation` |

gcc caught two of the three. The listing's `char slot[24]` produced **no
warning at all** — `snprintf` truncates silently by contract — and was found
only by diffing the listing. `fail_tr` and `exhaust_tr` were widened with them
on exposure rather than on evidence.

This is a defect class worth the width fix independently of any rename.

---

## THE FROZEN ABI BLOCK IS EMITTED FROM `emit_dfa.c`

`emit_rx_abi_types` writes the shared `PCREC_RX_ABI_H` block — and that block
DECLARES fields called `pos` and `caps`. A rename that reaches it renames the
**ABI itself**, and every emitted artifact stops compiling:

```
error: 'rx_ctx' has no member named 'pos'
error: 'rx_ctx' has no member named 'caps'
```

The use-site guards protect `ctx->pos`; nothing protects `size_t pos;` inside
the struct definition except excluding that emitter **by name**, which the tool
now does (109 literals skipped). Measured, not reasoned about: the gate
reported 41 uncompilable and REFUSED to call the sweep a pass.

---

## Rule 1 — a name can carry a PROPERTY, and the rename must preserve it

The approved sample renamed `RX_MRL_SHORT`/`RX_MRL_CAP` to
`RX_TOO_SHORT`/`RX_CLAMP_SPAN`. Both read better in isolation, and together
they destroyed a property: **`RX_MRL_` was a greppable FAMILY**, and
`tests/mrl` asserts an ABSENCE through it —

```sh
grep -q 'RX_MRL_' "$WORKDIR/bi/off/g.c"   # no bound under -fno-length-prune
```

Two unrelated names make that check match nothing and pass vacuously.
**Patching the grep to an explicit alternation would have worked and been
wrong**, because the next macro added to the family would silently escape it.
The names are `RX_PRUNE_TOO_SHORT` and `RX_PRUNE_CLAMP_SPAN`: full words, no
abbreviation, family prefix restored.

---

## Rule 2 — a variable spelled in two places will be renamed in one

The reverse-deterministic rung spells one variable twice:

```c
"    size_t %s_rv%d_c = 0; unsigned long %s_rv%d_it = 0;\n"   /* DECLARATION */
sb_printf(b, "    %s_mk = w->btn;\n", rv);                     /* USE, rv = "pa_rv0" */
```

The two format strings **share no substring**, so an exact-string rename moved
the uses and could not see the declarations. pcrec built clean and emitted C
that gcc rejects:

```
error: 'pb_rv0_iteration' undeclared
error: 'pb_rv0_frame_mark' undeclared
error: unused variable 'pb_rv0_mk'
```

**Before touching emitted names, grep for BOTH the composed and the direct
spelling.** The declaration site now carries a comment saying the suffixes must
agree, because nothing in the emitter makes that agreement structural.

---

## A BOUNDED CHECK THAT ALWAYS LOOKS AT THE SAME PLACE IS A FIXED FIXTURE

The neutrality gate reported **green three slices running** — "60 swept, 0
uncompilable, 41 of 41 byte-identical" — while rule 2's breakage was already
in the tree.

The bound was `head -n 60` over a **sorted** corpus, so every bounded run
sampled the same alphabetical corner, and that corner contains no revdet
pattern. Three green runs were the same 60 patterns three times.

Fixed: the bound is now **stratified** (every k-th pattern across the whole
file), so a bounded run spans the shape space at the same cost. At `NEUT_N=80`
it compiles 55 artifacts where head-60 compiled 41.

**It was a different suite that caught the breakage**: `tests/altcls`'s
two-artifact differential compiles emitted C with `-Werror` and links two
artifacts in one TU — a strictly stronger compile check than the gate's single
`-c`.

---

## Two pre-existing defects the conversion exposed

Neither was caused by this lane; both were invisible until something
pattern-dependent moved.

**1. `body()` extracted from the DECLARATION.** `tests/codegen`'s extractor
matched `^int <fn>(`, which matches the artifact's declaration near the top as
well as its definition far below — so it had always captured from the
declaration and swept up everything between. Nothing pattern-dependent had ever
landed in that window. The orientation block does, and it quotes the PATTERN,
so the OS-1 case-folding checks (which compare two different patterns that must
compile to the same engine) began reporting a difference that was not in the
engine at all. Fixed by requiring the definition (`!~ ";[ \t]*$"`), which makes
those checks tighter than before.

**1b. And AGAIN, in a second suite, found by the full `make test`.**
`tests/parse`'s `rx_search_body` has the identical bug — `$0 ~ /^int
rx_search\(/` with no definition guard — and `test-parse` went red with
*"ast-identity: 9 of 9 generated pairs differ"*. That check compares the
emitted body of two patterns with the SAME AST (`a|b|c` versus `(a|b)|c`);
the orientation block sits between the declaration and the definition and
QUOTES THE PATTERN, so the two "bodies" differed by their own pattern text.

Its author already knew line 1 quotes the pattern — the pipeline carries
`tail -n +2` to skip it. The orientation block is a SECOND place the pattern
appears, and that is the general hazard: **anything pattern-dependent added
near the top of an artifact will find every extractor that was silently
capturing more than it meant to.** Two suites had one; a sweep found no third.

**2. Seven mech sabotage anchors were stale on `main`.** S08, S09, S21, S22,
S26 (`src/parse/*`), S39, S65 (`src/gen/*`). A sabotage anchors an exact quote
of source; if the quote no longer occurs, the sabotage cannot apply and its row
certifies nothing. Found by a pure-grep checker written blind to the queue
(`scripts/m6read_check_sab_anchors.py`), which found exactly those seven and no
others — an independent second witness that the known drift list was complete.
Repair was the `sabanchors` lane's charter, not this one's.

---

## The legend must be capped, and the readability pass spends emitted LINES

A naive state legend names every state. `((a)|b){0,4000}c` has 4,002 states of
which **4,001 accept**, so the legend emitted 4,000 lines and took that
artifact from 1,704 lines to **5,797** — straight through
`run_ir_listing.sh`'s 2,000-line [ENG-BREP] emitted-size threshold.

Redesigned rather than truncated: past 48 states the legend emits a SUMMARY
(how many states, how many accept, where the start is, how short the shortest
accepted input is), because WHICH states accept stops being orientation once
there are thousands. Examples over 40 bytes are elided with their true length.

Result **1,795 lines — 91 lines of comment layer, headroom 296 → 205.** Not
close yet, but the budget is real and the interaction recurs.

**The size check catching this is the system working**, and it is the kind of
defect no correctness test could see.

---

## An over-claim in a generated comment

The state legend printed `(unreachable)` for any state the breadth-first walk
did not reach. On `^ab(c|d)e$` that is state 4, which is **not** unreachable —
it is selected by a POSITION VIEW (end of subject / end of line) that has no
edge in the transition table the walk follows.

Now: *"no path through the transitions above; a position view can still select
it"* — what the walk actually established, rather than a stronger claim it has
no basis for. **A comment that confidently mislabels a live state is worse than
no comment**, and the row's standard is that the artifact explains itself
correctly.

---

## I almost introduced a second source of truth

The first orientation block re-derived the prefilter's FORM in the prologue so
it could say "calls memchr()" like the sample does. That derivation already
lives in `emit_unanchored`, which owns it — the copy would have agreed today
and drifted later.

Repaired by splitting the statement: the block names the STEP and says its own
comment at the loop describes the form; the prefilter's description is emitted
at its own site where `use_memchr` is in hand. It surfaced only because the
invented helper name did not compile; **had I spelled it correctly it would
have shipped.**

---

## The legends cost nothing (engineering note (iv), discharged cheaply)

Note (iv) requires the emitter to TAG what it emits rather than infer it
afterwards. No tagging pass was needed:

- **DFA state legend** — a breadth-first walk over the transition table the
  emitter is about to write, labelling each state with the shortest input
  reaching it, spelled with each class's representative byte.
- **Class legend** — the same idea over the class map.
- **VM slot legend** — `vm_slot_name` reads the layout arithmetic
  (`vm_slot_guard/low/mark/rev/ctr`) backwards. Deliberately not a parallel
  table: a slot's meaning is decided by the layout, and a second list would be
  a second source of truth about it.
- **VM label intents** — `vm_lbl` already received a `role` string for the
  listing; it now also emits it as a line comment. **One call writes both**, so
  the C and `--emit-ir` cannot drift about what a label is for.

The emitter generates, from its own data, the legend the sample derived BY
HAND — entry for entry. A walk over emitter-owned data **is** the tag.

---

## The four revdet names, and giving up too early

`%s_rvs`, `%s_rvg`, `%s_ns`, `%s_rv<N>_c` were first left short under the rule
that *a confidently wrong full name is worse for a reader than a short one*.
That rule stands — but it is about giving up too EARLY as much as about
guessing, and one more place to look was enough.

The vocabulary is **not** in `eng_brep_design.md`. It is in the emitter's own
emission sites, which is a legitimate and citable source:

```c
char ga[64], gs[64], ns[64];               /* group array, group seen, n seen */
ptrdiff_t %s_rvg[%d][2]                    /* a PAIR per group: a span        */
unsigned char %s_rvs[%d]                   /* a flag per group                */
if (%s_ns >= %d) goto %s_L%d;              /* stop when every group is seen   */
vm_ev(..., "no group to witness: one step is all the retreat needs");
```

That is the backward walk recording each group's span and stopping once every
group has been witnessed — the design's *"a group inside a loop keeps the value
from the last iteration that ENTERED it, repaired to a backward scan"*.

Now `revdet_group_span`, `revdet_group_seen`, `groups_seen`, `cursor`, with the
citation at the declaration site. **No residue remains.**

---

## Self-inflicted damage, reported and repaired

Recorded because a log that only lists other people's defects is not a log.

- `gcc's` → `gcc'subject`, shipped into an emitted comment through a green gate.
- The blanket rename applied to the sabotage FILES renamed emitter CODE quoted
  inside shell strings (`rd->st[K]` → `rd->forward_state[K]`) and three English
  phrases. Four files reverted and their anchors re-derived from real source.
- `"the reported START of the match"` → `"the reported attempt_position"` in
  the emitter, at two sites.
- A heredoc turned `\n` escapes inside a C string literal into actual newlines
  (gcc: unterminated string). Caught at build.
- Commit messages mangled twice by backticks in `git commit -m`; `-F` from then
  on.
- **The apostrophe trap, caught a THIRD time — after documenting it above.**
  Fixing `tests/parse`'s extractor, the explanatory comment I added inside its
  single-quoted `awk` block contained `run_codegen_tests.sh's`, which
  terminated the shell string. `bash -n` caught it. Knowing a trap by name is
  not the same as avoiding it; the only reliable guard is running the thing.

---

## What each gate is FOR

| instrument | proves | blind to |
|---|---|---|
| `run_object_neutrality.sh` | **sameness** — `.text`+`.rodata` bytes and exported symbols identical across two builds | compilability under harder conditions; anything outside its sample |
| two-artifact differentials (altcls, possessify) | **compilability** — `-Werror`, two artifacts one TU — and behavioural equivalence | naming and comments |
| population / anti-vacuity checks | **that the fixtures still match** | answers |
| `--emit-ir` correspondence | that the listing still describes the code | object code |

The internal-symbol arm is INFO, never failure: renaming a static function or a
function-local static table renames its internal-linkage symbol. It is not
executed code and does not survive `strip`, but a check diffing disassembly
TEXT fails on it — the sample stage's first version did exactly that and
produced 200 lines of diff in which every line was a symbol name. **"Neutral"
had to be DEFINED as executed-bytes plus exported-symbols.**

Its sharpest control is self-arming: after the rename, the internal-rename
count MUST be non-zero. It was 0 at the baseline and 80+ after — if it had
stayed 0, the gate would have been reading artifacts the rename never touched.

---

## K24, checked consciously rather than left to the gate

The `noclone` attribute on `<prefix>_search` and the VM's unoutlineable
computed-goto body are load-bearing (K24's regression evidence). Verified:
`noclone` still emitted on both engines, `goto *` present in the VM artifact
and absent from the DFA one, and the structural check passing **with its
attribute-stripped control firing** (1 clone) — the guard is live, not vacuous.

The closest this pass came to K24 was corrupting its comment (`gcc's`), which
is prose, not mechanism.

---

## Commit-shape note

The conversion was originally committed as ~20 incremental slices, which served
the watchdog and the record well and **bisectability badly**: commit `02955dc`
(emitter renamed, pins not yet updated) measured 37 passed / 18 failed. Rather
than infer the red span, it was built in a throwaway worktree and measured.

Restructured per the manager's ruling so no bisect point lands red; this
document is what those slices' messages became.
