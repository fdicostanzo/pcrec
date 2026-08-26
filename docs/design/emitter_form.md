# [ENG-FORM] — the DFA emitter's FORM as a value, and the emitted artifact's OPAQUE STATE TOKEN

Lane `srForm`, 2026-08-26. Written BEFORE the code and committed first, on
`docs/design/premultiplied_dfa_table.md`'s model. Frank ruled the shape on
2026-08-26 (**D82**); the four BOUNDS in that ruling are this note's §10
acceptance, restated as checks rather than as claims. What is decided *here*
rather than in D82 is named as such in each section.

## 0. The answer in six lines

1. `emit_dfa.c` holds the DFA artifact's FORM as ~14 loose booleans, every one
   in a forward/reverse PAIR, read at ~57 `if (` sites inside one 459-line
   function. A new representation lands TWICE, at every site.
2. Make the form a VALUE: for each axis with >= 2 real forms, an explicit
   PREFERENCE LIST of representation objects `{ name, applies(), emit_* }`, and
   the machine's form is the FIRST APPLICABLE object from each list.
3. The last entry of every list is ALWAYS applicable, so selection is total and
   there is no "no form" arm to forget.
4. The chosen object's `name` **is** the stamp value. One derivation, three
   readers becomes structural rather than conventional.
5. In the EMITTED C, the scan's state becomes an OPAQUE TOKEN: a `typedef` plus
   a block of `static inline` accessors, emitted once per machine per form. The
   loop SKELETON is then emitted ONCE, form-independent, and the forward/reverse
   duplication collapses to one code path called twice.
6. The runtime cost is ZERO by construction and by measurement: gcc flattens the
   accessors, and §10.1 is the objdump-equality gate that proves it.

## 1. What is wrong today (the measured need)

Measured on the tree at `7bb6b5c` with `tests/../scratchpad/srForm/census.sh`
(`if (` counted as raw text so that emitted-C `if`s inside string literals
count, which is the plan row's convention; brace nesting counted with string
literals STRIPPED, so it is the C code's own nesting):

| function | lines | `if (` (raw) | `if (` (C code) | max C nesting |
|---|---|---|---|---|
| `emit_unanchored` | 459 | 57 | 31 | 5 |
| `emit_attempt`    | 447 | 47 | 33 | 4 |

The form booleans in `emit_unanchored`, all of them read more than once:

    eol  endv  viewsel  views  empty          (artifact-wide, from unanch_start)
    fpm  rpm                                  (table representation, PER MACHINE)
    facc2 racc2                               (class-indexed accept, PER MACHINE)
    fseed rseed                               (mechanism 4 start seeding, PER MACHINE)
    prefilter  use_memchr                     (forward only)
    nfskip/fskip[] nrskip/rskip[]             (skip states, PER MACHINE)

Eleven of the fourteen are a forward/reverse PAIR. That pairing is the whole
defect: every axis is stated twice, and every new axis is written twice into the
same function. [OPT-3] STEP 2 (the pre-multiplied table) added ~20 branch sites
to `emit_unanchored` for ONE new representation, which is what chartered this
row.

## 2. The two layers

**LAYER 1, the emitter.** Decisions become SELECTION over candidate lists. Six
axes qualify under D82 bound (3) ("only axes with >= 2 real forms; a one-site
boolean stays a boolean"); §3 lists them.

**LAYER 2, the emitted C.** The scan's state becomes an opaque token with an
accessor block. §5 is the accessor set; §6 is the resulting loop skeleton.

The two layers meet at exactly one place: the representation object's
`emit_token` method writes the accessor block, and nothing else in the emitter
knows how a state is spelled.

## 3. The axes and their candidate lists

Order is PREFERENCE order; the last entry of each list is always applicable.
A candidate may carry a `deny` flag mask: a set bit in `cx->opt->flags` REMOVES
the candidate from the list, which is how a `-fno-*` flag is expressed (D82:
"the deny flag = a filter on the candidate list") rather than as an `if` inside
the chosen object's emitter.

### Axis A — TABLE REPRESENTATION (per machine)

| # | object | applies when | deny flag |
|---|---|---|---|
| 1 | `premul_u16` | `n * ncls <= 65535` and no emitted seed cell is negative | `PCREC_NO_PREMUL_TABLE` |
| 2 | `indexed_i16` | always | — |

Stamp: `<PREFIX>_DFA_TABLE` is `"premultiplied"` / `"indexed"` when the two
machines choose the same object and `"mixed"` when they differ — composed from
the two objects' `name`s, never re-derived. Future ENTRIES, named here and
deliberately NOT built (D77 — wait for the measurement): `premul_u32` (above the
u16 bound), `two_byte` (a 16-bit alphabet). Each is one object plus one
`emit_token` body; §10.4 measures that claim with a throwaway.

### Axis B — PREFILTER (the forward scan only)

| # | object | applies when | deny flag |
|---|---|---|---|
| 1 | `memchr-bounded` | forward && `kind == MEMCHR` && `views` | — |
| 2 | `memchr` | forward && `kind == MEMCHR` | — |
| 3 | `byte-class-bounded` | forward && `kind == BYTE_CLASS` && `views` | — |
| 4 | `byte-class` | forward && `kind == BYTE_CLASS` | — |
| 5 | `none` | always | — |

**REVISED DURING IMPLEMENTATION (2026-08-26): FIVE objects, not three.** The
draft above made the `-bounded` half a `stamp()` method over three objects, on
the reading that the D11 bound is a fact rather than a form. It is a form: the
bounded skip stops at `n-1` and LOSES the `return 0` early-out, so it is
different emitted text, not the same text with a different label. Five objects
makes `<PREFIX>_DFA_PREFILTER`'s five values literally `obj->c.name` — which is
§0.4's whole claim — and removes the only `stamp()` method the design had.

`forward &&` is a clause in each candidate's `applies` rather than a branch in
`dfa_form_derive`: the reverse machine walks a range the forward scan already
proved contains a match, so every real form declines and the list's total
fallback is what it selects. **The deny column is empty on purpose and it is a FINDING, not an
omission:** `PCREC_NO_PREFILTER` today gates only the VM hybrid's
`fit.prefilter` (does a VM artifact get a DFA prefilter at all,
`src/opt/select_engine.c`), never `emit_unanchored`'s own start-state filter, so
the DFA scan's prefilter axis has NO deny flag and no axis sweep. Inventing one
here would be a caller-observable change outside this row's charter; [CHK-2]'s
registry check is where the gap belongs.

### Axis C — VIEW HANDLING (artifact-wide, carried per machine)

| # | object | applies when |
|---|---|---|
| 1 | `end_and_eol` | `endv && eol` |
| 2 | `end_only` | `endv && !eol` |
| 3 | `eol_only` | `eol && !endv` |
| 4 | `none` | always (no view selector emitted) |

These are `emit_view_select`'s existing three branches plus the "not called at
all" case, which today is an `if (viewsel)` at each of the two call sites.

### Axis D — SEED (per machine)

| # | object | applies when |
|---|---|---|
| 1 | `seeded` | `dfa_needs_seed(d)` — mechanism 4, the context byte decides the start state |
| 2 | `constant` | always |

### Axis E — WHERE THE ACCEPT IS RECORDED (per machine)

| # | object | applies when |
|---|---|---|
| 1 | `by-class` | `dfa_has_clsacc(d)` — some state's accept depends on the next byte |
| 2 | `scalar-viewed` | `views` — the D11 order: record AFTER the view selector |
| 3 | `scalar-plain` | always — record at the TOP of the loop |

**REVISED DURING IMPLEMENTATION (2026-08-26): THREE objects, not two.** The
draft had the accept as a two-form axis and left the RECORDING POSITION as two
`if (views)` sites in the skeleton — which is the same defect one level down.
The three real forms are exactly the three positions the accept can be
recorded at, and each object fills exactly one of three `emit_*` slots
(`emit_top` / `emit_after_view` / `emit_tail`), so the skeleton calls them
through NULL checks instead of branching on a form. `by-class` implies `views`
by construction (a next-byte-sensitive accept needs a class context), so the
ordering of entries 1 and 2 is not a tiebreak between overlapping candidates.

### Axis F — SCAN DIRECTION (per machine)

| # | object |
|---|---|
| 1 | `forward` |
| 2 | `reverse` |

Not a candidate LIST: the two objects are named directly by `emit_unanchored`,
one per `dfa_form_derive` call, because "which machine am I emitting" is not a
question about the machine's dimensions. It is still a representation object in
every other sense, and it is the axis that collapses the duplication. It is a *representation* axis
in exactly the same sense as the others: the direction is how the scan spells
its position, its bound, its recorded answer and its class read, and every one
of those is a form with two variants. The object carries the position variable,
the recorded variable, the body indent, the machine's table-name stem, and five
methods (§4).

### What STAYS a boolean (D82 bound 3, D75 addendum)

`views` (the D11 bound), `viewsel`, `empty`, and — in `emit_attempt`, which this
row does not relayer — `anchored`, `a_bot`, `a_gst`, `gseed`, `gtbl`. These are
FACTS the objects read, not representations with two emitted forms. `views` in
particular gates six sites but has no second emitted shape of its own: it
bounds a skip and orders an evaluation, which is the direction object's method
asking a question, not a candidate to select.

## 4. The object interface

Data first, methods only where the emitted text genuinely differs.

```c
typedef struct DfaRepr {
    const char *name;             /* the stamp value: "premultiplied" / "indexed" */
    unsigned    deny;             /* flag bit that REMOVES this candidate; 0 = none */
    bool      (*applies)(Ctx *cx, const Dfa *d);
    const char *cell_type;        /* the transition/view table's cell type */
    const char *state_type;       /* the C type behind the opaque token */
    int         acc_stride;       /* accept-table cells per state: ncls or 1 */
    int       (*state_const)(int st, const Dfa *d);   /* emit-time scaling */
    int       (*dead_cell)(const Dfa *d);             /* the table's dead value */
    void      (*emit_token)(StrBuf *c, const DfaForm *f);  /* LAYER 2: the block */
    void      (*emit_tr_comment)(StrBuf *c, const DfaForm *f);
} DfaRepr;
```

`DfaPf`, `DfaView`, `DfaSeed`, `DfaAcc` and `DfaDir` follow the same shape:
`name`, `deny`, `applies`, and the one or two `emit_*` methods that write that
axis's text. A machine's chosen objects plus the facts they read are one value:

```c
typedef struct DfaForm {
    const Dfa    *d;
    const char   *p;              /* the artifact prefix */
    const DfaDir *dir;            /* axis F — also supplies the table-name stem */
    const DfaRepr *repr;          /* axis A */
    const DfaPf  *pf;             /* axis B (`none` on the reverse machine) */
    const DfaView *view;          /* axis C */
    const DfaSeed *seed;          /* axis D */
    const DfaAcc *acc;            /* axis E */
    bool  views, eol, endv, viewsel;
    int   s0, nskip, skip[4];
    CandSet cand;
} DfaForm;
```

Selection is one generic walk per axis, written once:

    for each candidate in list:
        if (candidate->deny & flags) continue;
        if (candidate->applies(cx, d)) return candidate;
    /* unreachable: the last entry's applies() returns true */

## 5. LAYER 2 — the opaque state token

Per machine, emitted at FILE SCOPE immediately above the search function (the
hybrid's `static <prefix>_prefilter` gets it in the same place, by
construction — it is the same emitter call). The tables stay where they are,
inside the function; an accessor takes the table it reads as a parameter, so
the token abstracts the STATE REPRESENTATION and nothing else. gcc constant-
folds a block-scope `static const` array's address through an inline call, which
§10.1 measures rather than assumes.

The accessor set, per machine `M` with class count `NC`, PRE-MULTIPLIED form:

```c
typedef unsigned <p>_<M>_state;
static inline <p>_<M>_state <p>_<M>_step(const unsigned short *transitions,
                                         <p>_<M>_state s, unsigned cl)
{ return transitions[s + cl]; }
static inline int <p>_<M>_is_dead(<p>_<M>_state s)          { return s == 65535; }
static inline int <p>_<M>_accepts(const unsigned char *a, <p>_<M>_state s)
{ return a[s]; }
static inline int <p>_<M>_accepts_class(const unsigned char *a,
                                        <p>_<M>_state s, unsigned cl)
{ return a[s + cl]; }                                    /* axis E == by_class */
static inline unsigned <p>_<M>_row(<p>_<M>_state s)         { return s / NC; }
static inline int <p>_<M>_view_live(const unsigned short *v, unsigned row)
{ return v[row] != 65535; }                              /* axis C != none */
static inline <p>_<M>_state <p>_<M>_view_take(const unsigned short *v, unsigned row)
{ return v[row]; }
```

INDEXED form — same seven names, same signatures, different bodies:

```c
typedef int <p>_<M>_state;
    step:         return transitions[s * NC + cl];
    is_dead:      return s < 0;
    accepts:      return a[s];
    accepts_class:return a[s * NC + cl];
    row:          return (unsigned)s;
    view_live:    return v[row] >= 0;
    view_take:    return v[row];
```

Three properties of this set are decided HERE and are load-bearing:

1. **`row` is not free and must not be hoisted.** Under the pre-multiplied form
   `row(s)` is a DIVISION. Today the un-multiply lives inside the second operand
   of a `&&` whose first operand is `__builtin_expect(pos + 1 >= n, 0)`, so it
   runs at most twice per search and never per byte (premul note §6). The
   emitted view selector therefore calls `row()` INLINE at each use site and
   never into a hoisted local. A "tidier" `unsigned row = M_row(s);` above the
   `if` would put a divide on the hot path — the single most expensive mistake
   available in this file.
2. **`accepts` is textually identical in both forms** and that is the point: the
   representation lives in the typedef and in the bodies of `step` / `is_dead` /
   `row`, not in the accessor set's shape. An axis whose accessors all had to
   change name would not be one axis.
3. **The token never carries a raw index.** D82 bound (2): the loop may step,
   test dead, probe accept and (rarely) ask for a row. It may not scale, add or
   compare-to-zero. Emitted state CONSTANTS (start state, skip guard, seed cell)
   are scaled at EMIT time by `repr->state_const`, so the emitted comparison
   `<M>_state == 1234` has a form-dependent NUMBER and a form-independent SHAPE.

Accessors are emitted only when the machine's other axes need them
(`accepts_class` under axis E `by_class`; `row`/`view_live`/`view_take` under
axis C != `none`), so no artifact carries a dead accessor. An unused
`static inline` would not warn under `-Wall -Wextra` in any case; this is for
the artifact's reader, not for the compiler.

## 6. The loop skeleton, emitted once

    <M>_state <M>_state_var = <seed object's initializer>;
    for (;;) {
        [axis E scalar, !views] if (<M>_accepts(<M>_is_accepting, st)) rec = pos;
        [axis B]                <prefilter block>
        [skip states]           <one guarded skip per skip state>
        [axis C != none]        <view selector>
        [views && axis E scalar] if (<M>_accepts(<M>_is_accepting, view_st)) rec = pos;
        [axis E by_class]       <boundary arm + class-indexed accept + step>
        [axis E scalar]         <bound break + step>
                                if (<M>_is_dead(st)) break;
    }

Everything in angle brackets is one object's method. The braces, the `for (;;)`,
the `break` and the accessor CALLS are written once, in `emit_scan_loop`, and
that function is called twice: once with the forward `DfaForm`, once with the
reverse one.

## 7. Assembly order

1. `unanch_start(fd, rd, &us)` — the facts, unchanged, still one derivation.
2. `us.empty` -> head + the three-line empty body, return. **Before any token
   block is emitted**, so an empty artifact grows nothing.
3. Select: `dfa_form_derive(cx, fd, &fwd, DIR_FORWARD, &us)` and the same for
   the reverse machine.
4. `repr->emit_token(fwd)`, `repr->emit_token(rev)` — file scope, above the
   function.
5. `emit_search_head`.
6. `emit_machine_tables(fwd)`, `emit_machine_tables(rev)` — one path, called
   twice, the direction object supplying the section comment and the name stem.
7. the forward preamble, `emit_scan_loop(fwd)`, the middle, `emit_scan_loop(rev)`,
   the tail.

## 8. The stamp

Three stamps read the emitter's own selection:

- `<PREFIX>_DFA_TABLE` = compose(`fwd.repr->name`, `rev.repr->name`).
- `<PREFIX>_DFA_PREFILTER` = `fwd.pf->stamp(&us)`.
- `<PREFIX>_DFA_SCAN` — unchanged; it names the emitter, not a form.

`dfa_table_name` and `dfa_prefilter_name` are called from the stamp path BEFORE
any body exists, so selection must not emit. It does not: `applies()` is pure
and the `emit_*` methods are only reached from the body path. This is exactly
`unanch_start`'s existing contract ("NOTHING HERE EMITS"), extended to the
objects.

## 9. What could go wrong

1. **An accessor gcc will not flatten.** The whole design rests on it. Remedy
   order is D82's: `always_inline` first, hand-inlining last, and §10.1 records
   which was needed rather than assuming neither was.
2. **A token that leaks its representation.** The failure looks like an emitted
   `<M>_state_var / 18` or `< 0` outside the accessor block. §10.3's structural
   check greps the emitted body for exactly that and fails on it.
3. **A candidate list with no total fallback.** Selection returns NULL and the
   emitter writes nothing where a form belonged — a silent miscompile, not a
   crash. Every list's last entry has `applies` returning `true`
   unconditionally, and the selection walk asserts it found something.
4. **An axis that is really one site.** D75 addendum's failure: a candidate list
   whose objects each have one caller is a framework for its own sake. Six axes
   qualified; `views`, `viewsel`, `empty` and `emit_attempt`'s five `\G`/anchor
   booleans did not, and stay booleans.
5. **A `row()` hoisted out of its `&&`.** §5 property 1. It changes no answer,
   passes every identity gate, and costs a divide per byte. The timing gate
   (§10.1) is what would catch it; the comment at the emitted site is what
   should stop it being written.
6. **The hybrid drifting.** `emit_vm.c` calls `pcrec_emit_dfa_engine` for its
   inlined `static <prefix>_prefilter`. The token block is emitted by that call,
   so the hybrid gets it by construction. `run_premul_table.sh`'s hybrid arm is
   the standing check that it did.

## 10. Acceptance (D82's four bounds, as checks)

### 10.1 RUNTIME COST ZERO (bound 1)

`gcc -O2 -c` the probe artifact, `objdump -d`, normalise addresses and symbol
comments away, and require the `rx_search` instruction sequence to be EQUAL to
the same tree's pre-change sequence — same mnemonics in the same order.
Probes: `orig` (the bench's email pattern, premultiplied + memchr-free forward
loop AND the reverse loop), a `memchr`-prefilter artifact, a `views` artifact
(`(?:P)\z`), plus `-fno-premul-table` and `-fno-prefilter` arms of `orig`.
Then `tests/bench/fdriver.c` on t-a/t-b/t-c against 3.516 / 1.799 / 1.803
ns/byte, `taskset -c 3`, median of 5, >= 1 s trials, load1 beside each — AFTER
the manager's battery is done.

### 10.2 ANSWER IDENTITY (bound 1's other half)

Every answer byte-identical over (a) `make test`'s corpus, (b) the bench's 91
subjects (85 compliance `(?:P)\z` + 3 throughput find-all + 3 synthetic), across
today's compiler, this lane's compiler, and this lane's compiler under
`-fno-premul-table` and `-fno-prefilter`.

### 10.3 THE LOOP TEXT MOVES ONCE (bound 4)

`abi` 7 -> 8 at all four sites in ONE commit (D76): `src/gen/emit_dfa.c`'s
`.abi`, `tests/codegen/run_codegen_tests.sh`'s `ABI_EXPECT`,
`docs/spec/match_api.md` §6's "abi is N" sentence, and
`tests/codegen/run_recursion_identity.sh`'s `FILEPIN`. `run_premul_table.sh` §4
reads the accessor block's TYPEDEF and the `step` accessor's body instead of
hunting the loop's state-variable declaration. Sabotage rows anchored on moved
lines re-anchored, each proved to DETECT solo. `[SABANCHOR]` clean.

### 10.4 THE NUMBERS THAT DEFINE THE ROW (bound 4)

`emit_unanchored`'s lines / `if (` / max nesting before and after; the count of
form booleans; and the count of branch sites a NEW table representation would
touch — demonstrated by adding a throwaway `premul_u32` object in scratch and
counting the lines it needed. Target: one object + one `emit_token` body, zero
sites in `emit_scan_loop`, zero sites in the assembly.
