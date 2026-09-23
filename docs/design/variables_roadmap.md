# Variables and search/replace — the MVP and the phases

**Status: PROPOSED.** Design only. This note phases the three design notes it
sits beside: `variables_common.md` (the shared grammar, value model and call
interface), `variables_pattern.md` (a variable in a pattern) and
`replace_design.md` (a variable in a replacement template, over D38's already-
ruled substitution design). It assumes all three have been read; it does not
restate their arguments, only their outputs.

## The charter

Frank, 2026-09-23, quoted as given:

> "a variable insertion design. It should be tied to the string search/replace
> feature as the syntax should be the same. I am thinking bash/zsh style
> syntax including implementing features like conditional, or default
> variables, etc (at least on the search/replace side). I'd like it to examine
> the shell variable syntax options and see what might apply. For pattern
> variables, I see the advanced stuff as just a bit of code at the beginning,
> or in a wrapper, that converts it to a fixed string. Ignore the tricky DFA
> engine. If we do try it, that's a different effort. Also consider directions
> to go — for instance, caseless matching. If we can preprocess the variable,
> it might be viable. Need an opinion on call interface, null variables. For
> search/replace, would need its own call interface. Variable pattern and
> replacement string could be separate designs that reference a third common
> variable design. Brainstorm inclusion ideas for string replace (callouts
> that return strings? I think we support that). Then we'll phase an
> MVP/roadmap."

## 1. Where the charter met the tree

Five places the design came out differently from the charter's own framing.
Each is argued in the note that owns it; they are collected here because they
are what a reader of this roadmap most needs to know before reading the
phases.

1. **Substitution is already designed and ruled.**
   `docs/design/subst_template_design.md` is 1,256 lines and D38 (2026-08-14)
   ruled all fourteen of its open questions, including the template language,
   the unset-group default, the output-length contract, the module tiering,
   `--replace`, first-vs-global, and the extension namespace. `replace_design.md`
   §1 tabulates what is settled. **Most of the search/replace half of the
   charter is scheduling work, not design work.**

2. **The shell style and PCRE2's `SUBSTITUTE_EXTENDED` style are the same
   style.** `${n:-word}` and `${n:+yes:no}` are bash's operators spelled
   identically, already ruled into module `subst-extended`. There is no
   departure to negotiate for them.

3. **"Callouts that return strings — I think we support that."** The callout
   ABI does not: native callouts are match-or-fail only, ruled at D38 and
   enforced at every generated call site with `__builtin_trap()`. The
   string-returning mechanism is `rx_renderfn`, ruled at D38 Q13, carried in
   `docs/spec/match_api.md` §2, **reserved with no producer**. So it is
   designed and unbuilt rather than supported. `replace_design.md` §3.1.

4. **A pattern variable is a backreference with a different span source.**
   The VM has no compile-time-literal `memcmp` to give a runtime operand to;
   literals are per-byte `if` chains. What it does have is `vm_bref`
   (`src/gen/emit_vm.c:8103-8245`), which reads a runtime `(start, end)`,
   calls through the encoding seam, and returns a *length* rather than a
   boolean precisely because a caseless fold can change length.
   `variables_pattern.md` §1.

5. **Caseless is viable now, and the charter's own proposal is the one to
   decline.** Preprocessing the value cannot work: a fold is a relation
   between two sides, the subject side is not folded, and under `utf8` there
   is no canonical byte string to fold to (`k` ↔ U+212A is 1 byte ↔ 3, pinned
   at `tests/utf8/axis06_caseless_fold.rxt:25-37`). The existing
   `bref_match_caseless` already handles all of it.
   `variables_pattern.md` §6.

And one measurement that makes the pattern side cheaper than expected:
**`${...}` in a pattern is a spelling PCRE2 accepts and that no subject can
match** — `$` asserts that the next byte is a newline, and `{` is not one.
Verified against the shipped compiler, against python `re` over six
pattern forms, and exhaustively for `${n}` over every subject of length 0..7
from a targeted alphabet (zero matches). Corpus population: **0 of 4,198
shipped `pattern` lines**. `variables_common.md` §0.2.

---

## 2. The MVP

**One sentence:** the shared expansion engine with `${name}` and `:-`/`:+`
only, reaching a VM-route pattern variable and a first/global replacement,
with the call interface and the refusal classes settled.

### 2.1 What is in it

| # | item | size | depends on |
|---|---|---|---|
| M1 | The expansion grammar and evaluator: `${ [!] selector [op word] }` with `:-`, `-`, `:+`, `+`, `:?`. One parser, one evaluator, both consumers. Nesting in the `word` position only, bounded by a `limits.def` row. | **M** | — |
| M2 | The value model: `rx_var {const unsigned char *p; size_t len;}` as a fixed-literal ABI type; UNSET is `p == NULL`, EMPTY is `p != NULL && len == 0`; the `:` operators fold EMPTY in with UNSET. | **S** | M1 |
| M3 | The array interface: compile-assigned indices, `<PREFIX>_NVARS`, one `<PREFIX>_VAR_<NAME>` macro per name. No run-time name lookup anywhere. | **S** | M2 |
| M4 | Module `vars`: the registry row for the `${` doorway with `engines = ENGM_VM`, the producer, the `A_VAR` node kind with its own `union u.var`. The DFA decline and the `--engine=dfa` diagnostic come free from `forces_registry`. | **M** | M1 |
| M5 | The five analysis declines: `reqbyte.c`, `startanch.c`, `endwin.c`, `mrl.c` join `A_BREF`'s case labels; `prefix_k.c` is structurally unreachable. Forced complete by the no-`default:` rule. | **S** | M4 |
| M6 | The VM emit arm and the encoding-seam entry pair `$_var_match` / `$_var_match_caseless`, per encoding — `vm_bref`'s block with the span source swapped, same length-returning protocol, same work metering. **Caseless is in the MVP**, because it is the same work. | **M** | M4 |
| M7 | The entry-point parameter: `const rx_var *vars` last, on var-bearing artifacts only; the `_in` siblings too. The `abi` bump with the full D76/D94 ritual, the `docs/spec/match_api.md` hunk, `rx_info.nvars` appended. | **M** | M3, M6 |
| M8 | The refusal classes: `PCREC_ERR_UNSET_VAR` below `PCREC_ERR_FLOOR` (the `PCREC_ERR_STARTPOS` shape), and the UTF-8 validity refusal for a value under `-e utf8`. | **S** | M7 |
| M9 | Replacement side: `${!name}` as the caller variable in a template (module `subst-pcrec`), `${n:-}`/`${n:+}` on both selectors, the entry's `vars` parameter. | **M** | M1, and `[M4-SUBST]`'s own core |
| M10 | Tests: the `.rxt` production (`var` / `var-unset` beside `repl`/`s`/`sg`/`serr`), its `rxt_schema.def` row, three-leg agreement, and the sabotage rows. | **L** | M7, M9, and the manager's spelling ruling |

### 2.2 What is deliberately *not* in it

- Every operator past `:-`/`:+`/`:?` — `#`, `##`, `%`, `%%`, `^`, `^^`, `,`,
  `,,`, `:off:len`, `${#n}`. Phase 2.
- `rx_renderfn` producers. Phase 3.
- The DFA route. Phase 5.
- The sink entry `rx_subst_to`. Phase 4, gated on `[M3]`.
- Any `maxw`/`minw` declaration on a use site. Phase 6, and it may never be
  built.

### 2.3 The one sequencing fact

**M9 is gated on `[M4-SUBST]`'s own core landing**, which is `STATE:not-started`
today. M1-M8 are not: a pattern variable needs the expansion engine and the
VM, neither of which depends on substitution. So the MVP splits cleanly into a
pattern half that can start immediately and a replacement half that is
scheduled behind a milestone.

`subst_template_design.md` §1's own **[MEASURED]** argument applies to M1 too,
and it is what makes this honest: the expansion engine is a pure function of
(template, environment) and needs no matcher at all, so it is buildable and
testable before anything else in either half.

---

## 3. The phases

Each row carries what would open it — a measurement, or Frank's stated want.
D77: nothing here is built ahead of one.

### Phase 2 — the operator suite

| item | size | opens on |
|---|---|---|
| `${n#pat}` / `##` / `%` / `%%` — prefix/suffix strip | **M** | Frank's stated want. `pat` here is a *shell glob*, not a regex, and that boundary needs ruling before it is built (a regex would be the run-time-pattern hazard `variables_common.md` §1.2 declines) |
| `${n:off:len}` — substring | **S** | Frank's stated want. Cheap on the replacement side (arithmetic on an existing span pair). Refuses rather than splitting a character under `-e utf8` |
| `${n^}` / `^^` / `,` / `,,` — case transform | **M** | Frank's stated want, and the pattern side is where it earns its place (the replacement side already has `\U`/`\L`, and `subst_template_design.md` §7.3 argues an operator there is redundant). **ASCII-only**; refuses by name under `-e utf8` until a 1:n case-mapping table is vendored, which is a `third_party/` question of its own |
| `${#n}` — length, replacement side only | **S** | Frank's stated want. Declined in a pattern: it renders decimal text, which is never what a pattern author means |
| a reserved `${!index}` match counter | **S** | Frank's stated want. Spelled as a *reserved variable name*, not a new operator, to avoid colliding with `${#n}` |

### Phase 3 — renderer producers

| item | size | opens on |
|---|---|---|
| `rx_renderfn` producers: the template syntax that names a renderer, the `extern` declaration emitted only when named, the `out == NULL` sizing pass | **M** | `[M4-SUBST]`'s core landing. The ABI type, the return discipline and the sizing convention are all already ruled (D38 Q11/Q13) — this is the producer for a reservation that has none |
| a renderer's access to the variable environment | **S** | the ruling on `replace_design.md` §5 Q2 — whether `rx_ctx` gains a member, which is `design_callout_abi.md`'s to rule once |

### Phase 4 — the streaming sink

| item | size | opens on |
|---|---|---|
| `rx_subst_to(s, n, sink, ctx)` — no output buffer at all | **M** | **`[M3]` (streaming) landing.** `subst_template_design.md` §7.2 option (c) already offers it with this exact trigger: it "composes with `[M3]` later and removes the buffer-sizing question entirely" |

### Phase 5 — the DFA route

| item | size | opens on |
|---|---|---|
| A variable as a **string edge** in the DFA: the opaque-symbol placement rule, `[FEAT-VAR]` (a) | **L** | **A measured artifact family where the VM route's throughput is the bottleneck** *and* the placement precondition holds. Frank's 2026-09-23 charter defers it ("that's a different effort") and `[FEAT-VAR]` records why it is hard: determinization cannot see the variable's bytes, so `(${v}|ab)c` cannot be determinized without them. The nearest neighbours are `[OPT-VMLIT]` and `[ENG-DIRECT]` |

### Phase 6 — width declarations

| item | size | opens on |
|---|---|---|
| A use-site declaration that a variable is non-empty, or bounded, restoring some of the five declined analyses | **M** | **A measured artifact where the decline is the bottleneck.** Today the prize is a set of optimizations nobody has measured on a pattern nobody has written. `variables_pattern.md` §9 Q1 |

### Phase 7 — the format and the library

| item | size | opens on |
|---|---|---|
| `[V-E]`'s manifest gains a template field and a variable declaration | **M** | `[V-E]` opening. D38 Q7 already ruled the manifest inherits the template field |
| A variable whose value IS a pattern | — | **never, here.** Re-homed to `[LIB]`/definitions (D85's definitions table, D87's AST-level composition, D89's numbering). `variables_common.md` §4.2: it is that feature wearing this feature's syntax |

---

## 4. Dependencies, as a graph

```
  M1 expansion engine ──┬── M2 value model ── M3 array interface ──┐
   (no matcher needed)  │                                          │
                        └── M4 module vars ── M5 declines          │
                                    │                              │
                                    └── M6 VM arm + seam ──────────┴── M7 entry
                                                                        │
                                                                   M8 refusals
                                                                        │
                                                                   M10 tests
  [M4-SUBST] core ──────────────────────────── M9 replacement side ─────┘

  [M3] streaming ───────── phase 4
  [PATFACTS] (D120) ────── absorbs M5, either order
  [V-E] ────────────────── phase 7
  [LIB] / definitions ──── owns the pattern-valued variable, permanently
```

Two notes on the graph:

- **`[PATFACTS]` is not a dependency in either direction.** D120 charters one
  per-pattern analysis record read by every pass, on Frank's own observation
  that the analyses are ad hoc. M5 is five one-line declines, which is that
  observation with a new instance. If `[PATFACTS]` lands first the decline is
  one field; if not, M5 lands as written and migrates under D120's own
  implement-then-replace clause. `variables_pattern.md` §2.
- **The pattern half and the replacement half share M1-M3 and nothing else.**
  That is the whole point of a common note, and it is what makes the two
  halves schedulable independently.

---

## 5. Sizes, and what they mean

**S** ≈ one lane-day, one or two files, no `abi` event.
**M** ≈ a lane, a design decision or two inside it, possibly a spec hunk.
**L** ≈ a lane with its own panel, or a milestone's worth of test work.

M10 is **L** because a new `.rxt` production is not a small thing in this
tree: a `rxt_schema.def` row with its ten columns, agreement across all three
parser legs (`pcrec`, `tests/harness/run.sh`, `tests/harness/verify_rxt.py`),
W23-S3's per-row drive, the corpus census pins, and the sabotage rows. The
`ext`-block staging path exists if that work is not ready
(`docs/spec/rxt_format.md`'s graduation rule), and the spelling is the
manager's call (memory `pcrec-dd13b-syntax-is-managers`).

M7 is **M** rather than **S** entirely because of the `abi` ritual: the bump,
the identity-gate re-pin, the spec hunk in the same change, and the site list
found **by grep over the number** — with `battriage`/`evtriage3`'s addendum
that a reader whose text cites a *byte count* and no abi digit still moves
with it, and `w4_report.md` §0(5)'s that a coverage guard can move while
spelling a number it never touched.

---

## 6. The plan rows this would fill

| row | state today | what this design gives it |
|---|---|---|
| `[FEAT-VAR]` | `STATE:not-started`, "expand on arrival, not before" | Its four recorded design questions: (b) and (c) answered from the code, (d) answered as a signature change with the abi ritual, (a) deferred to phase 5 by the 2026-09-23 charter |
| `[M4-SUBST]` | `STATE:not-started`, design ruled by D38 | The variable layer it predates; §3.8's finding that the emitted global loop is **not** `match_api.md` §3.1's caller loop with a splice; §5 Q6's question about whether a var-bearing pattern can stream |
| `[M4-CALLOUTS]` | `STATE:not-started`, ABI ruled by D38/D39 | `rx_renderfn`'s first producer (phase 3), and §5 Q2's question routed back to `design_callout_abi.md` to be ruled once |
| `[PATFACTS]` | `STATE:not-started` (D120) | A first outside customer, and a concrete five-site instance of the ad-hoc-analysis observation that chartered it |
| `[LIB]` | `STATE:not-started`, blocked on `[DD-13b]` | Permanent ownership of the pattern-valued variable, rather than that feature being half-built here |

---

## 7. What this roadmap does not settle

Collected from the three notes' own open-question sections; each is named
there with its recommendation.

- Whether `${name}` in a **pattern** is the variable or whether a pattern must
  also write `${!name}` (`variables_common.md` §7 Q4). A caller-facing taste
  call, Frank's.
- Whether `${!...}` is spent on "the caller's environment"
  (`variables_common.md` §7 Q2, `replace_design.md` §5 Q1).
- Whether `rx_info` carries a variable names table in the same `abi` event
  (`variables_pattern.md` §9 Q2). Recommendation is yes, because adding it
  later is a second event for a `.rodata`-only table.
- Whether a renderer sees the environment through `ctx->user` or a new
  `rx_ctx` member (`replace_design.md` §5 Q2). Belongs to
  `design_callout_abi.md`, ruled once.
- The `.rxt` production's spelling and staging (`replace_design.md` §5 Q5).
  The manager's.
- Module naming: `vars` on the pattern side; the replacement side rides D38's
  ruled `subst` / `subst-extended` / `subst-pcrec`
  (`variables_common.md` §7 Q6).
