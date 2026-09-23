# varmvp — [VAR] the MVP's PATTERN HALF (M1-M8 + M10)

Lane `varmvp`, opus, 2026-09-23, branch `lane/varmvp` from `e289ea06` plus
lane `varrule`'s cherry-picked rulings commit. `abi` 31 → 32.

`${name}` in a pattern compiles once, and the caller supplies the bytes per
call. Contract: `docs/spec/vars.md`. M9 (the replacement side) is gated on
`[M4-SUBST]` and is not in this lane.

---

## §0 — FINDINGS FIRST

Ten, in the order a reviewer should read them. Six are places the design set
met the tree and lost, three are defects checks found on their first
populated run, and one is a check that had been silently comparing nothing
since a CLI change months ago.

### 0.0 The manager's M6 ruling, and the defect it exposed

**RULED mid-flight (Frank, 2026-09-23 ~14:1x) and implemented after M10:** do
not add `$_var_match` / `$_var_match_caseless` as siblings of
`$_bref_match`. `variables_pattern.md` §1.3 proposed the siblings and
**refuted itself in the same paragraph** — it says the variable body is the
backreference body "with `s[ref_start + i]` replaced by `v[i]`", and two
bodies differing only in how they index the reference side are ONE function
with the wrong operand shape.

The existing pair is generalised instead: the reference side becomes
`const unsigned char *ref, size_t reflen`, a backreference passes
`subject + start, end - start` (one line in `vm_bref`), a variable passes its
resolved `(p, len)`. **Renamed `$_span_match` / `$_span_match_caseless`** on
the ruling's own "rename if the spelling is span-source-specific" clause:
`bref` names the backreference and nothing in the new contract does.

**AND THE RENAME EXPOSED A DEFECT NOTHING ELSE WOULD HAVE.**
`src/gen/emit_vm.c`'s `--emit-ir` listing derived `st.has_bref` from
`v->enc_mask & (PCREC_ENCE_BREF | PCREC_ENCE_BREF_CASELESS)`. That bit is now
`PCREC_ENCE_SPAN` and a `${name}` variable sets it, so the listing would have
reported **"NO (backreference)" for a pattern that has none**. It reads
`pcrec_has_bref(root)` now — the same source `select_engine.c` forces the
prefilter off from, which is exactly what the neighbouring `has_call` line
already does and says why. *A fact read off a shared bit stops being that
fact the day the bit is shared, and nothing about the sharing makes a sound.*

**TWO MECHANISMS WERE DELETED RATHER THAN KEPT.**
`PcrecEncEntry.requires` and `pcrec_enc_mask_close` existed solely so the
withdrawn sibling pair's utf8 caseless body could share the backreference
entry's 1,484-pair fold map. With ONE caseless entry there is no cross-entry
dependency and no customer, so both are gone (D77). `pcrec_enc_has_entry`
survives; the validity entry still asks a question about the table.

**IT IS AN EMITTED-TEXT EVENT FOR BACKREFERENCE-BEARING ARTIFACTS TOO**, and
it rides the same `abi` 32 bump rather than a second one. The §0.8 identity
measurement's scope narrows accordingly: +34 bytes is the change for an
artifact carrying neither a variable nor a backreference.

### 0.0a And the rename found a check that had been comparing ZERO pairs

`tests/codegen/run_encoding_checks.sh`'s **DD12a(i)** — the hot-loop shape
identity, the instrument that proves no encoding conditional reached the
engine body — invokes the compiler as

```
pcrec --features all -e byte -p rx -o rx.c -- <pattern>
```

**D118 retired `--source` by making a BARE OPERAND mean a FILE.** Since then
every one of those calls has answered *"not an existing file; a literal
pattern is given with `--pattern`"* and returned 1, which the instrument
turns into "skip this pattern". `PAIRS=0`. Every bucket, every EXCISED
counter, every divergence count: 0.

**REPRODUCED AT THE BRANCH POINT** with that tree's own script and own
binary — `checks passed: 10 / checks failed: 1`, identical — before being
attributed anywhere. It is PRE-EXISTING and not this lane's.

**Its own non-vacuity floor is the only reason it is visible at all.** With a
`>= 0` there, a dead instrument and a clean one print the same thing. And it
went stale because **`test-encoding-checks` is OPT-IN** and rides no
`TEST_SECTIONS` entry, so nothing was running it when the CLI moved
underneath it.

FIXED here rather than reported, for one reason: this lane RENAMED the
entries that instrument reads, and leaving it dead would ship that rename
unverified by the only check that looks at those names — *a witness must
reach its site*. Two further repairs the fix then surfaced:

- **The mechanical rename over that file reached the regex and the tables and
  missed the one place a NAME IS MAPPED TO A DIFFERENT NAME.** A
  `name.startswith('bref_ci_')` normalisation still said `bref_ci_`, so a
  renamed helper matched, fell through with its own name, and `counts[name]`
  raised `KeyError`.
- **`int` was not in the return-type alternation.** `$_var_valid` returns
  `int`, which no residual entry before it did, so the walk did not see its
  region at all — and a region this walk does not see is a whole function on
  the utf8 side with no counterpart on the byte side. `int` and `var_valid`
  are in the pattern now.

And the counter then read `var_valid=0`, which is the file's own stated
failure mode one entry over ("a check that never exercised `span_match`
would be dead code passing silently"), so `^${v}$` joins the explicit
witness list. It is the only witness that reaches an entry present in one
backend's table and **absent from the other's**, which is the sharpest test
of the excision's own claim.

**AFTER THE REPAIR THE INSTRUMENT IS ALIVE AND SAYS SO**: 254 pairs compared,
244 strict-identity / 10 widens-under-utf8, and real excision counts —
`next_pos=508`, `span_match=4`, `span_match_caseless=5`, `var_valid=1`,
`advance=144`, `startpos_guard=420`. **That is what verifies this lane's
rename**: the generalised entries are seen, counted and excised under their
new names, which nothing else in the tree checks.

**AND REVIVING IT SURFACED A BACKLOG THAT IS NOT THIS LANE'S TO CLEAR.** Three
reds appear that were unreachable while `PAIRS=0`, and all three are `[K50]`
startpos territory with no relationship to variables:

| red | what it says |
|---|---|
| `startpos_attempt` never excised | a named region is dead code certifying nothing |
| 2 `[K50]` manifest rows STALE | reached this run and not swept into the gate-refinement class (first: `\z`) |
| 5 pairs entered that class with NO manifest row | the named exclusion grew silently (first: `(?:\Gab)+`) |

**DELIBERATELY NOT RE-DERIVED.** The check's own failure message says *"Re-derive
the rows deliberately; do NOT delete them to go green"*, and that manifest is
a judgement about which patterns legitimately diverge under `[K50]` — a
different row's, not a variable lane's. **They do not touch `make test`**:
`test-encoding-checks` is opt-in and rides no `TEST_SECTIONS` entry, which is
the same fact that let the instrument die.

**Why revive it at all rather than report and leave it**: leaving it dead
would have shipped this lane's rename unverified by the only instrument that
reads those names. Reviving it is what makes §0.0's claim checkable; the
backlog it exposes is a separate row and is named here so it is a list rather
than a silence.

---

The other eight follow.

### 0.1 A mechanical "join `A_BREF`'s case label" pass gets 42 of 43 right, and the wrong one is SILENT

`A_VAR` was added to the `AKind` enum and every TU compiled with `-Wswitch`
to find the sites — **43 distinct switch sites, found by measurement rather
than from the design's own census of 44.** (The difference is a counting
unit: the panel counted switches carrying `case A_…` labels; the compiler
reports only those where the enumerator is genuinely unhandled.)

At 42 of them `A_VAR` genuinely takes `A_BREF`'s arm. At the 43rd it must
not, and nothing would have said so:

```c
bool pcrec_has_bref(const Ast *a)   /* src/opt/atomic.c */
```

The coding guide already says not to merge `atomic.c`'s nine predicate
walks, "every one differs in at least one per-kind arm". Eight of the nine
ask something GENERAL and answer "a leaf with no subtree". This one asks
**"does anything in here compare SUBJECT TEXT TO SUBJECT TEXT"**, where
`case A_BREF:` IS the question rather than a per-kind answer — and a
variable compares subject text to the CALLER's bytes, which is the whole
distinction `A_VAR`'s own header states.

**It was found by READING A DIAGNOSTIC, not by a red test**: the
`-fprefilter` refusal named "a backreference" for a pattern that has none.
No check could have gone red, because the one caller that reads the
predicate for a DECISION (`prefilter_decision`) ORs it with `has_var` and
would have declined either way. The arm now carries that whole story.

A second, smaller instance in the same pass: `revdet.c`'s internal error
said "a backreference reached the reverse-deterministic body reversal" for a
variable. That file's own comment, two arms below, says an internal error
naming the wrong construct sends the next reader hunting in the wrong file.
It has its own sentence now.

### 0.2 `variables_pattern.md` §3 is wrong about the mechanism and right about the outcome

§3 says the `${` row resolves against the shipped bare `$` row by SR-9's
tail arbitration, "a tailed row always outranks the tail-less fallback".

**`pcrec_registry_find`/`arbitrate` are never called with `RK_BARE` at all.**
That kind's own comment in `internal.h` says so in as many words: its rows
exist for the DUMP and for D85's definitions machinery, because the
constructs have no doorway. Nothing ranks anything.

The outcome is still right, by a different mechanism: `$` is base grammar
parsed directly in `p_atom`, so `${` is recognised there too — one `if`,
gated on `pcrec_feature_enabled(FEAT_VARS)` exactly as `\Q` is gated on
FEAT_QUOTING. The registry row is carried for the dump and for the D67 stamp
`forces_registry` reads, which is what makes the ENGINE decline free.

### 0.3 The two design notes disagree about a module-off `${`

- `variables_common.md` §4.1: "with the module off today's parse stands in
  full."
- `variables_pattern.md` §7's table: `"requires module 'vars'"`.

**The table shipped.** §4.1 is arguing a different point — that the
COLLISION rule is satisfied, which it is — one sentence too far. The general
house rule (D34 ruling 5 / `extension_design.md` §12) is that recognisers
are always live, production is gated, and a recognised-but-gated construct
says which module would implement it. And the alternative here is worse than
usual: §0.2 of `variables_common.md` proves the gated spelling CANNOT MATCH
ANYTHING, so the choice is between a named refusal and handing a caller who
forgot `--features vars` an artifact that silently matches nothing.

It is a refusal-set move, and its population is measured at **zero shipped
patterns**.

### 0.4 Two checks this landing was the first to POPULATE both failed, both in the K35 shape

**(a) The rxtsource census counted ONE block opener.** Its own header says it
is "written from the FORMAT (docs/spec/rxt_format.md's line kinds), not from
any of the three implementations, which is what makes it a control for all
of them rather than a fourth voice". The format has had TWO `opens_group`
rows since [DD-13b.W23.3]. It counted `pattern` and not `pattern-esc`, and
nothing failed because the shipped corpus had zero such blocks until this
module added one. All three legs read 3995 where the control read 3994.
Both census sites now count both.

**(b) Leg C counted the BINDINGS as expectations.** `verify_rxt.py`'s first
version appended each `var`/`var-unset` line to `results`, which is the
EXPECTATION stream C3 reconciles against the census — 45 entries into a
total the census does not count. C3's own failure sentence, "expectations
are going somewhere neither counted nor reported, which is the one outcome a
skip total exists to prevent", is exactly what happened and exactly what
said so.

### 0.5 A bit set where the text is emitted is too late

`job->enc_mask` is copied to the Job **before the prologue** writes the
residual declarations. `vm_var` may OR its compare's bit during the body
walk because the walk runs above that copy; `vm_emit_vars_resolve` runs
below it. The value-validity entry's bit, set there, never reached the
prologue and the first `-e utf8` build failed at `implicit declaration of
rx_var_valid`. It is set in the plan phase now, where the need is fully
known and where the copy's own comment ("AFTER the walk, which is where the
need was discovered") already pointed.

### 0.6 `<PREFIX>_NVARS` was in the wrong file, and a test asking a caller's question is what caught it

It was stamped into the `.c` beside `<PREFIX>_NSLOTS`, which is genuinely
`.c`-private. `<PREFIX>_NVARS` is CALLER-FACING — `docs/spec/vars.md` §4
publishes it, and a caller reading a header to find out whether this
artifact takes variables reads exactly this.

The harness needs the same fact for the same reason (its driver has to know
which `rx_search` signature to compile against), greps the HEADER for it,
and found nothing — so a block with a var-bearing pattern and NO `var` line
failed to compile with `too few arguments to rx_search`. **The
discriminator had to be the ARTIFACT and not the block**, which is the cell
written to test "an omitted name reads UNSET", and fixing that is what
surfaced the stamp's placement.

### 0.7 An expansion set may read only the POINTERS

`${v+w}` tests `raw_p[i] == NULL` and answers with the word or with nothing,
never with the value — so `raw_len` is written and never read, and
`-Wunused-but-set-variable` under the harness's own `-Werror` GENCFLAGS
rejects the artifact. K28's class: a warning no ANSWER check can see, found
by the corpus on its first run. `(void)` on BOTH arrays, since the mirror
shape (`${v:-w}` with an always-taken word) makes `raw_p` write-only by the
same argument.

### 0.8 The design's own byte-identity wording is understated, and the real number is smaller and sharper

`variables_roadmap.md`'s MECH-M1 says a var-free artifact is "unchanged
except for the `abi` digit". It also gains **two `rx_info` initializer
lines**, because `rx_info` grows members on every artifact while
`PCREC_ERR_UNSET_VAR`'s EMISSION is gated on the var-bearing bit.

MEASURED at **exactly +34 bytes**, on four witnesses spanning 13 KB to
762 KB, each written to the SAME `-o` basename (the house's recorded
basename trap), six changed lines each and **no emitted program byte among
them**. Under `-fcomments` it is exactly +1001 on all twelve cpset rows, the
extra being the shared `PCREC_RX_ABI_H` block's doc-comments, which are
K-invariant. Both numbers are one event seen through two settings.

---

## §1 — WHAT WAS BUILT

| item | where |
|---|---|
| M1 the expansion grammar | `src/core/varexp.c`, `tests/core/varexp_check.c` (47 sub-checks) |
| M2/M3 the value model and by-name resolution | `rx_var` in the shared ABI block; `<prefix>_vars_resolve` in `emit_vm.c` |
| M4 module `vars` | `FEAT_VARS`, the `${name}` `RK_BARE` registry row, `src/parse/mod_vars.c`, `has_var` in `select_engine.c` |
| M5 the `AKind` sweep | 43 sites, found with `-Wswitch`; K63's census comment fixed and the entry closed |
| M6 the VM arm and the seam | `vm_var`; `$_var_match`/`_caseless` per encoding; `$_var_valid` under utf8 |
| M7 the entry shape | `rx_ctx.vars`/`.nvars` appended; trailing pair on `_search`/`_in`; `rx_info.vars`/`.nvars`; `<PREFIX>_NVARS` |
| M8 the refusals | `PCREC_ERR_UNSET_VAR (-8)`; the UTF-8 validity refusal |
| M10 the tests | `tests/vars/` (3 files, 76 cases), `verify_vars.py`, `run_vars_tests.sh`, reject rows, S271/S272 |

### Two general mechanisms rather than special cases

**`PcrecEncEntry.requires`** — one column, closed once inside both emit
functions. The utf8 caseless variable compare SHARES the caseless
backreference compare's 1,484-pair fold map and decoder. All three
alternatives were worse: a second copy doubles a table in any artifact using
both; renaming them into a shared entry moves the emitted bytes of every
caseless-backreference artifact ever built; and writing the implication into
`emit_vm.c` would be the emitter knowing something about an encoding's
residual, which DD-12 (7) forbids outright.

**`pcrec_enc_has_entry`** — "does this backend carry a row at all", which is
how the value-validity refusal reaches a utf8 artifact and no byte artifact
with **no encoding test anywhere in the emitter**. `entries_byte[]` simply
has no such row, because every byte string is a valid `byte` string.

### One MVP narrowing, refused by name with its re-open condition

A default WORD that MIXES literal text with a nested `${...}`, or nests two,
would need run-time concatenation storage whose size is not known until the
call — a buffer-sizing question the design does not rule and the MVP does
not need. `${a:-${b}}`, which `variables_common.md` §1.7 calls "the useful
case and the only one with a real customer", is a SINGLE nested reference
and is supported. The GRAMMAR accepts the mixed form (the replacement side
will be able to render it, writing into an output buffer already); this
CONSUMER refuses it by name.

### One spelling decision this lane made

A backslash inside an operator's WORD makes the next byte literal. Without
it neither `}` nor `$` is spellable in a default, which is a grammar with
unspellable values. The design notes do not rule on it (§4.1 covers a
literal `$` OUTSIDE `${...}`). The alternative — no escape at all, `}`
simply unspellable — is named at the site so a later ruling can take it.

---

## §2 — THE FAILING-DIRECTION STORIES

**M1's grammar**, three plants:

| plant | result |
|---|---|
| the colon is never set | 21 of 45 sub-checks RED |
| the word escape is dropped | 4 RED |
| ONE WORD PIECE PER BYTE | **0 RED** |

The third is the finding. The check's oracle is a ROUND TRIP — each accept
row states the canonical render, and the render is re-parsed and re-rendered
— and **the render CONCATENATES the word's pieces**, so it flattens exactly
the representation that plant moves. *An agreement check cannot see a
difference its own two halves agree to erase; only a field read can.* A
coalescing arm was added (45 → 47 sub-checks) and re-reddens that plant at 2.

**The sabotage rows**, both run solo at `ba6a6c3b`:

| row | verdict | figure |
|---|---|---|
| S271 `vm_var` ignores `caseless` | DETECTED | `reach:ok(1/1), vars:1fail/1pass, corpus:18fail/7pass` |
| S272 `has_var` stops declining the prefilter | DETECTED | `reach:ok(1/1), vars:1fail/1pass, corpus:26fail/50pass` |

Under S271 the `vars` section's CORPUS arm goes red and its ORACLE arm stays
green, which is exactly the split the two arms exist for: the oracle says
what the answer should be while the corpus says what the artifact gives.

`variables_roadmap.md` §2.5 predicted these rows would ship UNREACHED. They
do not, because `tests/vars/` landed in the same delivery — which §2.3 had
already said was possible. Both declare `SAB_REACH` anyway, and each probe
asserts a CLEAN-tree property a future change could remove for a reason
unrelated to the line being planted.

**A backtick inside a double-quoted `SAB_DOC_FIGURE`** is command
substitution and made both rows unsourceable. `w12_report.md` recorded this
exact defect on 2026-08-31; it is in `tests/mech/CLAUDE.md` now because a
row file is the one place in this tree where prose and shell share a quote.

**IT BIT TWICE IN THIS LANE.** The second time was the later edit that
recorded the measured figures above, where the prose naturally wrote "the
`vars` arm's own 1fail". The tripwire caught it both times and named it both
times (`DOES NOT SOURCE`) — the check works; remembering does not. That is
why the note lives in the directory's CLAUDE.md with the explicit rule that
appending a measured figure re-opens the hazard, rather than in a commit
message somebody would have to find.

---

## §3 — THE `abi` 31 → 32 RITUAL, BY GREP

Readers found by grepping for the CURRENT number, then by RUNNING the suites
that count (D94 addendum: a reader that never cites the number still moves
with it).

| reader | moved to |
|---|---|
| `src/gen/emit_dfa.c`'s `PCREC_ARTIFACT_ABI` | 32 |
| `tests/codegen/run_codegen_tests.sh` `ABI_EXPECT` + its change-log clause | 32 |
| `docs/spec/match_api.md` §2 (`rx_var`, `rx_ctx`'s two fields, the error code) and §6's change log | the abi 32 entry |
| `docs/spec/vars.md` | NEW — the module's contract page |
| `docs/spec/limits.md` §3.6 | NEW — the two numeric limits |
| `tests/resource/run_resource_tests.sh` | 762367 → 762401 (+34) |
| `tests/codegen/manifests/m5_stage1_stamps.tsv` | all twelve rows +1001 |
| `tests/codegen/run_cpset_structure.sh` CHECK 3 | the accounting note |
| **the `bref_match` spelling, by grep** | 19 files: `run_encoding_checks.sh` (the signature regex, three count tables, the aggregate floors), `run_codegen_tests.sh` (the `[M5-SEAM]` fixture table and its two token rules), `run_backref_diff.sh` §9/§9b, both `fold_agreement*_check.c` (whose CALLS also take the new operand shape), S106/S109/S116, and six CLAUDE.md files |
| `tests/codegen/run_codegen_tests.sh` `[M5-SEAM]` | three `vars` fixtures added; `resid_brefdecl` 5 → 8, and **what the count MEANS changed with it** — the pair is now the runtime span compare serving two constructs, so a floor would let either half vanish |

**Found by the suites and NOT by the grep:** the resource and cpset pins
cite byte COUNTS and no abi digit — `battriage_report.md`'s SECOND READER
CLASS, and its tenth and eleventh recorded instances.

**LEFT DELIBERATELY:** `run_recursion_identity.sh`'s (B) `FILEPIN`. D76
requires it to name a commit reachable AFTER the merge, which a lane
branch's is not (opt5i/ccdiff1's precedent). **It is the manager's at
merge.**

**A drive-by fix in the same hunk:** `match_api.md` §2's quoted ABI block
has been missing `PCREC_ERR_STARTPOS` since [K50], though §4's table and
§6's prose both carry it. Added beside the new code.

---

## §4 — VALIDATION

All on this box (darwin, gcc-16), at the lane's tip unless noted.

| suite | verdict |
|---|---|
| `make strict` | clean after every commit |
| `tests/codegen/run_codegen_tests.sh` | **109 / 0** |
| `tests/codegen/run_cpset_structure.sh` | **28 / 0** |
| `tests/codegen/run_prechecks.sh` | **250 / 0** |
| `tests/resource/run_resource_tests.sh` | **27 / 0 / 0** (1 expected darwin skip) |
| `tests/registry/run_registry_tests.sh` | green (rc 0) |
| `tests/registry/limits_check.sh` | **29 / 0** |
| `tests/reject/run_reject_tests.sh` | **634 / 0** |
| `tests/rxtsource/run_rxtsource_tests.sh` | **214 / 0** |
| `tests/core/run_core_tests.sh` (varexp arm) | **47 / 0** sub-checks |
| `make test-vars` | **2 / 0** (corpus 76/0, oracle 61 agree / 0 disagree) |
| `tests/harness/verify_rxt.py tests/vars/` | 121 own-oracle skips, 0 fail |
| `scripts/m6read_check_sab_anchors.py` | **296 / 296 resolve** |
| `mech S271`, `mech S272` | both DETECTED, reach ok, figures in §2 |

**The full `make test` is the lane's LAST act** and is launched detached; its
log path and completion line are in the handback.

### What the oracle does NOT reach, counted rather than implied

`verify_vars.py` prints its own uncovered population: **11 refusal cells**
(no PCRE2 spelling for "this literal is absent" exists to splice), **4
no-splice-exists** (a word that is a nested reference — resolving one is the
mechanism under test), **1 pattern-esc**. The sweep FAILS on an empty
checked population, because a sweep that checked nothing reads exactly like
a sweep that found nothing wrong.

Its operator-form arm is a SECOND READING of the design's table in python,
and the file says so: what is independent there is the MATCH of the expanded
literal, not the expansion. That arm's own first version was encoding-blind
— under `PCRE2_UTF`, `\xNN` above 0x7F is the CODE POINT and not the byte,
so escaping the Kelvin sign's three UTF-8 bytes byte-by-byte produced a
pattern for three Latin-1 characters and reported **four false
disagreements against a correct artifact**.

---

## §5 — WHAT IS OWED

1. **The (B) `FILEPIN`** in `run_recursion_identity.sh` — the manager's at
   merge, by D76 (§3).
2. **`make test`** — launched detached as the lane's last act; log path in
   the handback.
3. **`scripts/emit_sweep.py --ref e289ea06`** — the var-free identity claim
   is measured by hand in §0.8 on four witnesses at the same `-o` basename,
   which is the brief's stated substitute while the box was held. The full
   five-stream sweep is a stronger statement and is not run here. Its
   PREDICTED shape: `c-default` and `c-vm` move on every reached artifact
   (+34 bytes, six lines); `emit-ir-vm` 0 movers (the listing has no
   `A_VAR` producer — §6); `composition` header-only; `dumps` +1 row
   (`--list-syntax` gains the `${name}` row).
4. **`make test-axes`** — no deny axis was added, so there is nothing new to
   sweep. Stated rather than skipped silently.
5. **`C3_*` pins in `run_rxtsource_tests.sh`** — deliberately NOT re-pinned,
   per that file's own 2026-09-08 note: they are box-sensitive on darwin and
   owed from a Linux/10.46 run.
6. **The census plan's own owed list** (`tests/vars/gen_corpus_plan.md` §6):
   two `+`/`:+` SET-and-non-empty cells, the lookaround pair (a refused
   lookbehind and a matching lookahead), and the generator on its stated
   D77 trigger.

---

## §6 — NOT BUILT, AND WHY

**`VE_VAR`, the `--emit-ir` listing event** (`variables_pattern.md` §4.4).
The section proposes one and correctly argues it must NOT join the `slots`
family. It is not built here, and the reason is D77 rather than time: the
listing's own byte-identity arm (`irsb`) is what would catch a drift in it,
and there is nothing yet for it to catch — no consumer reads a variable row.
The section's own reserved-with-no-producer precedent (`VE_ISLAND`,
`VE_CALLOUT`) is the shape this follows. **The trigger:** the first
`--emit-ir` consumer that needs to see which expansion a program point
reads, which is most likely the replacement side (M9), whose template
rendering has more to say in a listing than a single span compare does.

**The `[M5-SEAM]` fixture rows** — **DONE, and the M6 ruling is why it got
cheap.** `variables_pattern.md` §4.3 named this as a site the abi grep does
not reach, and it was owed while the design had TWO new entries needing their
own per-family pin. With ONE generalised pair there is no new entry at all:
three `vars` fixtures join the existing table (case-sensitive, caseless, and
one artifact carrying a backreference AND a variable, which declares
`span_match:2` and is the cell that says the sharing is real rather than two
entries with one name), and `resid_brefdecl` re-pins 5 → 8. A ruling that
removed a mechanism removed its check obligation with it.

**One thing the fixture table taught:** its heredoc is UNQUOTED, so `${v}` in
a fixture pattern is parameter expansion and not pattern text. The script
died at `v: unbound variable` under `set -u` — the loud version. The quiet
version, an unset variable expanding to nothing, is what `set -u` is on for.

---

## §7 — RULINGS RECEIVED

The lane consumed lane `varrule`'s cherry-picked commit (`032014f6`) and
worked to it throughout:

- **D121 addendum Q1-Q6** — no `flags` word on `rx_var`; `${!name}` spent on
  the caller's environment; UTF-8 validation unconditional in the MVP; BOTH
  `${name}` and `${!name}` accepted in a pattern; the operator phases
  decided after the MVP; the module is `vars`.
- **The splice WRAP** — `(?:…)` unconditional, because a reference is one
  node. `verify_vars.py` wraps unconditionally and says so.
- **The `.rxt` spelling** (the manager's, DD-13b) — `var <name> "<value>"`
  and `var-unset <name>`, block-scoped, repeatable, the existing quoted
  subject escape set, no second vocabulary.

No ruling was needed mid-flight and none was requested.
