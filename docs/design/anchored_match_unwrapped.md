# Anchored match-here via the unwrapped forward DFA — `[ENG-ABS]`'s second mechanism

Status: DESIGN NOTE OF RECORD for lane `engabs`, written 2026-08-29 before
the code, revised as the code landed. §7 carries the MEASURED numbers.

Scope: this note covers `[ENG-ABS]`'s **second** mechanism only — the
anchored match-here entry. The **first** mechanism (`ENG_UNANCH` absorbing
`^`, the DD-7 absorption half) is a different change on the same plan row
and is NOT opened here.

---

## 1. What this row changes, and the measurement that opened it

Today a DFA artifact's `<prefix>_match` runs the artifact's ordinary
UNANCHORED search and then filters:

```c
ptrdiff_t rx_match(const rx_ctx *ctx)
{
    ptrdiff_t capture_spans[RX_NCAPS][2] = {{0}};
    int found = rx_search(ctx->subject, ctx->len, ctx->pos, capture_spans);
    if (found < 0) return (ptrdiff_t)found;
    if (found != 1 || (size_t)capture_spans[0][0] != ctx->pos) return -1;
    return capture_spans[0][1] - capture_spans[0][0];
}
```

`rx_search` is the D7 two-pass engine: a WRAPPED forward scan that finds
where a match ENDS, then a REVERSE scan that finds where that match BEGAN.
`docs/spec/match_api.md` §3.2 documents the shape as non-contractual and
names its worst case (a failing match-here may skim the remainder of the
subject hunting a later match the filter then discards).

**Two measurements make this a scheduled row rather than a filed one.**

1. `docs/dev/opt2_anchored_match_measurement.md` (lane `opt2m`, 2026-08-28)
   measured the REVERSE PASS at ~50 % of the DFA's cost on every MATCHING
   subject of the bench's 85-subject compliance set. A cost-isolation patch
   that deletes the reverse scan (scratch, timing-only, answer-incorrect by
   construction) moves matching subjects from **2.077× behind the VM to
   1.046×** (parity) and the 35 ordinary short valid emails from **1.207×
   behind to 0.571×** (43 % AHEAD).
2. The ORIGINAL `[ENG-ABS]` motivation, recorded 2026-08-18: a FAILING
   `_match` probe against a long subject costs O(subject) on a DFA artifact
   and O(divergence) on a VM artifact.

The manager's reading correction on the `opt2m` doc is the whole reason the
mechanism is what it is: with the WRAPPED forward machine an accept can
belong to a LATER start, and the reverse pass is what lets `rx_match` reject
those. **The start is unneeded only when the machine is UNWRAPPED and run
from `ctx->pos`.** A runtime "anchored" flag on the existing tables cannot
reach this — the start-anywhere self-loop is baked into the subset
construction and the merged states erase which start a thread came from
(DD-7 / `engine_m4.md` §7.3: the wrap is STRUCTURAL).

The number to beat, from `opt2m` §(a): **at or below the VM on matching
subjects, ~0.57× on short valid emails**, and a failing match-here that is
O(1) rather than O(n) on a 1 MB subject. The isolation understates the
target — it still pays the self-loop and skip machinery this form removes.

---

## 2. The third machine: its ROLE, and how it is derived

> The r39 panel's MISCOMPILE-1 was a set derived for the SCAN role reused as
> a VERIFY. This row is exactly a role change for a table, so every table in
> the artifact is named with its role below.

An `ENG_UNANCH` artifact carries these machines after this row:

| machine | role | built from | prune | wrap |
|---|---|---|---|---|
| `<p>_forward` | SCAN: where does a match, starting anywhere at or after `search_from`, END? | `job->nfa` from `nfa->start` | yes | YES (start self-loop) |
| `<p>_reverse` | REWIND: given that end, where did the leftmost such match BEGIN? | `job->rnfa` (pattern reversed) | no | n/a |
| `<p>_anchored` | **MATCH-HERE: given the start `ctx->pos`, where does the match starting THERE end?** | `job->nfa` from `nfa->anch_start` | yes | NO |

**The derivation is a PARAMETER, not a copy.** `nfa_wrap_unanchored` already
leaves the pattern's own start state addressable — `Nfa.anch_start`
deliberately does not move when the wrap is applied (`src/ir/nfa.c`, a
property `src/opt/prefix_k.c` already depends on). So the anchored machine is
the SAME `pcrec_build_dfa` over the SAME `Nfa`, rooted at `anch_start`
instead of `start`:

```c
pcrec_build_dfa(cx, &job->nfa, &job->adfa, /*prune=*/true, /*reverse=*/false,
                PCREC_MAX_DFA_STATES_TABLE, /*root=*/job->nfa.anch_start,
                /*optional=*/true);
```

`pcrec_build_dfa` gains two parameters — the root state and the
optional/mandatory flag (§5.2) — and every call site now STATES its root
rather than inheriting `nfa->start` implicitly. There is no second
construction, no second closure, no `anchored`-only clause anywhere in
`src/ir/dfa.c`; the memory rule `pcrec-general-mechanisms-not-special-cases`
is satisfied by construction.

Three consequences fall out of sharing the NFA and worth stating because
each is load-bearing somewhere below:

- **The alphabet is IDENTICAL.** `eqclasses` scans the whole `Nfa` for
  `N_CLASS` states and refines by the word/newline sets from per-machine
  flags computed off the same scan. Both machines see the same NFA, so
  `adfa->clsmap` is byte-for-byte `dfa->clsmap` and `adfa->ncls ==
  dfa->ncls`. (The artifact still emits its own copy — see §8's OPEN item.)
- **`^` and `\G` cannot appear.** `nfa_has_bot` routes every BOT-family and
  `\G` pattern to `ENG_ATTEMPT`, so on this engine `s1g[] == s1u[]` entry for
  entry and there is no start-position assertion for the anchored machine to
  get wrong.
- **`s0` / `s1u[]` mean the same thing they always did.** The anchored scan
  begins at `ctx->pos`; its context byte is `subject[ctx->pos - 1]`, which is
  the byte `search_from`'s seed already names. Mechanism 4's dispatch is
  reused verbatim (§3.5).

---

## 3. THE ACCEPT DISCIPLINE, and the identity argument

This is the section the row lives or dies on. The claim is:

> **For every subject `s`, every `pos`, and every pattern this engine
> compiles, the unwrapped anchored scan from `pos` reports exactly the
> length today's `search`-plus-filter reports.**

### 3.0 Notation

`N` is the priority Thompson NFA. `a = N.anch_start` is the pattern's own
first state. `nfa_wrap_unanchored` adds `w = SPLIT(a [slot 0, PREFERRED],
any-byte → w [slot 1])` and sets `N.start = w`.

A DFA state is a **priority-ordered list** of NFA states (`src/ir/dfa.c`'s
file header). Its closure walks split edges in preference order and, with
`prune` on, STOPS THE INSTANT `ACCEPT` is reached — lower-priority threads
are dropped and the state is marked accepting.

- `F` = the wrapped forward DFA (`prune`, root `w`) — the SCAN machine.
- `R` = the reverse DFA (no `prune`) — the REWIND machine.
- `A` = the unwrapped forward DFA (`prune`, root `a`) — the MATCH-HERE
  machine.

Fix `p = ctx->pos = search_from`. Write `S_q` for `F`'s state after
consuming `s[p..q)` and `A_q` for `A`'s.

### 3.1 Step one — `F`'s state FACTORS, and the pos-start part is `A`'s

**Claim.** For every `q ≥ p`, either

 (i) `S_q = A_q ++ T_q` as priority-ordered lists, where `T_q` holds exactly
     the threads whose start is `> p`; or

 (ii) a prune inside the `A` part has already fired, and then `T_q` is empty
      and `S_q = A_q` exactly.

*Why the ordering.* `closure(w)` is `closure(a)` followed by the self-loop
thread, because slot 0 is the preferred branch and the closure walk appends
in preference order. Subset construction preserves relative order across a
step (each thread's successors are appended in the thread's own position),
so threads that started at `p` precede every thread that started later, for
all `q`, by induction.

*Why the prune cannot corrupt the `A` part.* Pruning drops threads STRICTLY
BELOW the accepting one.

- If the accept is inside `T_q` (a later start accepted; no `p`-start thread
  accepts at `q`), the cut is entirely inside `T_q`. `A_q` is untouched and
  case (i) still holds — and `A`'s own closure, seeing only the `A` prefix,
  prunes nothing, so `A_q` is what `A` would have computed independently.
- If the accept is inside the `A` part, the cut truncates `A_q` at the same
  index `A`'s own closure would (the two closures see the same prefix in the
  same order and stop at the same `ACCEPT`) and deletes ALL of `T_q`. That
  is case (ii). **From that position onward the two machines are the same
  list over the same NFA with the same transition function, so they step
  identically forever.**
- If `A_q` is empty (every `p`-start thread has died), `A` is dead and `F`
  carries only later starts.

### 3.2 Step two — the accept BITS

A state is accepting iff its closure reached `ACCEPT`. By §3.1:

**`A` accepts at `q` ⟹ `F` accepts at `q`.** The converse is FALSE: `F` can
accept at `q` from a thread in `T_q`. That asymmetry is the entire content
of "an accept can belong to a LATER start", and it is why the reverse pass
exists at all.

### 3.3 Step three — the END rule, and why the two agree

Both scan loops record `last_accept_position` = the LAST `q` whose (viewed —
§3.4) state accepts. Write `E_A` and `E_F` for the two.

**(a) If `E_A` exists, `E_F = E_A`.**
`A` accepts at `E_A`, so `F` does (§3.2), so `E_F ≥ E_A`. At `E_A` the
accept is in the `A` part, so §3.1 case (ii) fires: `S_{E_A} = A_{E_A}` and
the machines coincide from there on. Hence for `q > E_A`, `F` accepts iff
`A` does — and `A` does not, `E_A` being its last. So `E_F = E_A`. ∎

**(b) If `E_A` exists, today's filter PASSES and reports `[p, E_A)`.**
`A`'s accept at `E_A` is a real accepting NFA path from `a` consuming
`s[p..E_A)`, so `P` matches that span. `R` is NON-pruning and records the
FURTHEST-BACK accepting rewind position `≥ search_from = p`; a span the
language contains is one `R` accepts at, so `R` accepts at `p`, and `p` is
the smallest position the loop may reach (`if (rewind_position <=
search_from) break;`). So `match_start_position = p`, the filter
`caps[0][0] != ctx->pos` passes, and the reported length is `E_F - p =
E_A - p`. That is what the new form returns. ∎

**(c) If `E_A` does NOT exist, today's filter FAILS.**
Suppose it did not: then `R` reported `match_start_position = p`, i.e. `P`
matches `s[p..E_F)`. An accepting NFA path from `a` over that span therefore
exists. `A` could only miss it by having PRUNED the thread carrying it — and
a prune requires an earlier accept in the `A` part, i.e. `E_A` exists.
Contradiction. So `E_A` absent ⟹ no match begins at `p` ⟹ today's `_match`
returns `-1`, which is what the new form returns. ∎

**(a)+(b)+(c) is the identity.** Note that (c) is where the argument would
break if `A` were built without pruning, and (b) is where it would break if
`R` were built WITH it — the two machines' `prune` settings are load-bearing
in opposite directions, which is D7's own point restated for a third
machine.

### 3.4 The position VIEWS (`$`, `\Z`, `\z`), and end-of-subject

The EOL and END views are closures of the SAME pre-set with `eol_ok` /
`end_ok` set, interned as variant states and selected by POSITION:
`q == n` → the END view, `q + 1 == n && s[q] == '\n'` → the EOL view.

§3.1's factorisation holds view-for-view: the eol-closure of `A_q ++ T_q` is
the eol-closure of `A_q` followed by the eol-closure of `T_q`, pruned by the
same rule, and `A`'s own eol view is the first half. So §3.2 and §3.3 read
unchanged with "accepts" meaning "the VIEWED state accepts", and a
`$`/`\Z`/`\z`-bearing pattern needs no separate argument.

`A` selects its view objects (axis C) **from its own machine**, not from the
artifact-level OR the SCAN pair shares (§5.3) — a strictly more accurate
derivation that cannot move any existing artifact's bytes.

The end-of-subject boundary itself is `dfa_dir_*`'s `at_bound`: the anchored
direction's is `scan_position >= subject_length`, the forward one's verbatim,
and the boundary accept is recorded through the same `emit_bound_accept`
before the `break` (R30 N9's placement rule — attached to the break, never
peeled below the loop, because the loop has two exits).

### 3.5 The START SEED (mechanism 4: `\b`, `(?m)$`)

`F` seeds from `search_from ? seed_state[class(subject[search_from - 1])] :
s0`. For `_match`, `search_from == ctx->pos`, so **`A` reads the same byte
and takes the same branch**. The emitted `_match` body opens with

```c
    const unsigned char *subject = ctx->subject;
    size_t subject_length = ctx->len;
    size_t search_from = ctx->pos;
```

so every direction string in the emitter (`search_from`,
`subject[search_from - 1]`, `subject_length`, `scan_position`) is reused
character for character and the seeded initializer is the SAME emitted line
as the forward machine's, against the anchored machine's own tables.

The range guard moves above the initializer on the seeded form for K27's
reason (an out-of-range `pos` would otherwise index `s[pos-1]`); the
anchored direction's guard is
`if (search_from > subject_length) return -1;` — `-1` where the search
returns `0`, because this function's failure value is the entry's, not the
search's.

### 3.6 ZERO-LENGTH matches

`emit_scan_loop` probes the accept BEFORE the first step, so a pattern
matching empty at `p` makes `A`'s start state accepting at `q = p` and
`E_A = p`, length `0`. Today: `F` accepts at `p` (the accept is in the `A`
part), `R` starts at `rewind_position = p`, records the start-state accept,
and breaks on `rewind_position <= search_from` — `[p, p)`, length `0`.
Identical, and it is spec §3.2's promised "`0` for a zero-length match at
`ctx->pos`".

A pattern whose start state accepts is also exactly the population
`unanch_start`'s `start_acc` excludes from every prefilter, which is why
§3.7's skip argument does not have to consider it.

### 3.7 The PREFILTER, and why `A` must not have one

`F`'s memchr / byte-class / offset-k skip advances `scan_position` while the
machine is parked in its start state — it CHOOSES WHERE THE SCAN BEGINS.
That is sound for a SEARCH (a skipped position is one no match can begin at)
and **wrong for a MATCH-HERE, where the start is given**. `A` therefore
selects axis B's total fallback `none`, and it does so by DERIVATION rather
than by a branch: `A`'s form is built from an `UnanchStart` whose `kind` is
`DFA_PF_NONE` and whose `ofsk.nsel` is `0` unconditionally (§5.3), and every
one of the six axis-B candidates requires one of those to be non-trivial.
`tests/codegen/run_anchored_match.sh` §2 asserts it from the ARTIFACT (no
`memchr`, no `can_begin_match`, no `ofsskip` inside the `_match` body),
never from the stamp.

The in-loop STAY skips (`<m>_stay<K>`) are a different mechanism and stay:
"while parked in state `K`, these bytes keep you in `K`" is a property of
the machine, direction-free, and it never moves the START. The anchored
direction excludes NO state from `pick_skip_states` (`F` excludes `s0`
because the prefilter owns that position; `A` has no prefilter to own it),
which is expressed as a `DfaDir` field rather than the current
`dir->reverse ? -1 : d->s0` conditional.

### 3.8 `find-all`, restart, and the `_in` entries

`_match` is a single anchored probe; the find-all loop of spec §3.1 drives
`_search` + `_next_pos` and is untouched. The three `_in` entries delegate to
their un-suffixed siblings (a DFA artifact has no resume storage — [DD-14.FB]),
so `<prefix>_match_in` and `<prefix>_match_caps_in` inherit the new form with
no edit: **all four anchored entries spec §3 promises are covered, and two of
them by delegation that already existed.**

### 3.9 `_match_caps` and the DEAD GROUPS

`<prefix>_match_caps` cannot simply stop calling `rx_search`, because
`emit_search_head` is where a DFA artifact writes its PERMANENTLY-UNSET
groups (wave G's dead-capture elision: a DFA artifact can have
`RX_NCAPS > 1`, and every group above 0 is unset). Under the new form
`_match_caps` therefore writes them itself:

```c
ptrdiff_t rx_match_caps(const rx_ctx *ctx, ptrdiff_t (*capture_spans_out)[2])
{
    ptrdiff_t rx_len = rx_match(ctx);
    if (rx_len < 0) return rx_len;               /* caps_out UNTOUCHED */
    if (capture_spans_out) {
        capture_spans_out[0][0] = (ptrdiff_t)ctx->pos;
        capture_spans_out[0][1] = (ptrdiff_t)ctx->pos + rx_len;
        for (int rx_g = 1; rx_g < RX_NCAPS; rx_g++) {
            capture_spans_out[rx_g][0] = PCREC_UNSET;
            capture_spans_out[rx_g][1] = PCREC_UNSET;
        }
    }
    return rx_len;
}
```

`caps_out[0] == [ctx->pos, ctx->pos + length)` is spec §3.3's own sentence,
now true by construction rather than by a filter that proved it. The
"untouched on every negative return, give-up included" rule holds because
the only writes are below the `rx_len < 0` return. `RX_NCAPS == 1` on almost
every DFA artifact, and the loop then emits nothing at run time.

### 3.10 What does NOT change

`<prefix>_search` — its tables, its loop, its prefilter, its reverse pass —
is byte-for-byte what it was. This row adds a machine and rewrites two entry
bodies; it does not touch the search. That is why the answer-identity gate
(§9) is over the whole corpus's `_search` answers AND the anchored entries'
answers separately.

---

## 4. Cost: what the new `_match` pays and what it stops paying

| | today | this form |
|---|---|---|
| failing match-here, 1 MB subject | forward scan over the remainder (memchr-skipped where a prefilter applies), then reject | steps until the anchored machine dies — first divergent byte for a literal-led pattern |
| matching subject | wrapped forward scan to the last accept + REVERSE scan back to the start | one unwrapped forward scan to the last accept |
| tables touched | forward + reverse | anchored only |
| start-state work | self-loop / prefilter machinery on every parked byte | none |

The reverse pass is the ~50 % `opt2m` measured. The self-loop and skip
machinery is the part the isolation patch could NOT remove, which is why the
target is at-or-better than the isolation's 1.046× / 0.571×.

---

## 5. Selection: an `[ENG-FORM]` axis, and the fallback

### 5.1 It is a SELECTION, spelled as axis G

`emitter_form.md`'s six axes are candidate lists whose chosen object's
`name` IS the stamp value, so a stamp cannot disagree with the emitted body.
This row adds **axis G — the MATCH-HERE FORM**, two objects:

| order | candidate | `applies` | `deny` |
|---|---|---|---|
| 1 | `unwrapped` | `job->anchored_ok` — the artifact is `ENG_UNANCH`, is not the empty engine, and the anchored machine BUILT | `PCREC_NO_ANCHORED_DFA` |
| 2 | `search-filter` | always (total fallback) | — |

One derivation (`dfa_match_form(cx)`), three readers: the emitted `_match`
/ `_match_caps` bodies, the `<PREFIX>_DFA_MATCH` stamp, and `rx_info`'s
mirror.

### 5.2 OVERFLOW IS A SELECTION OUTCOME, NEVER A REFUSAL

The anchored machine can exceed the DFA caps — the state cap
(`PCREC_MAX_DFA_STATES_TABLE`, narrowed by `PCREC_MAX_TABLE_ENTRIES/ncls`)
or the per-compile subset-element budget `PCREC_MAX_SUBSET_ELEMS`. A
pattern that compiles today MUST NOT start failing because an OPTIONAL
machine did not fit. So `pcrec_build_dfa` gains an `optional` flag, and
`intern()`'s two "pattern too complex" sites gain ONE line each, placed
after the unchanged `[SEL-1]` record and before the unchanged `ctx_fail`:

```c
    cx->dfa_overflowed = true;                       /* [SEL-1], unchanged */
    snprintf(cx->dfa_overflow_why, ...);             /* [SEL-1], unchanged */
    if (d->optional) { d->overflowed = true; return PCREC_DFA_DEAD; }
    ctx_fail(cx, 0, "pattern too complex ...");      /* unchanged */
```

`PCREC_DFA_DEAD` is `-1`, the value `tr[]` already carries for "dead", so a
partially-built optional machine is well-formed rather than corrupt; the
worklist loop additionally returns on `d->overflowed` so the build stops at
once instead of walking out its remaining rows.

**Three properties this shape has and a `try`/`catch` at the site would not.**

1. The two diagnostics and their `[SEL-1]` records are character-for-character
   unchanged, so `--engine=auto`'s retry contract is untouched.
2. The ORDER of the builds is the mandatory pair FIRST, the optional machine
   SECOND. `PCREC_MAX_SUBSET_ELEMS` is a per-COMPILE budget; building the
   optional machine first could push a mandatory one over it and refuse a
   pattern that compiles today. Second, it cannot.
3. `Ctx.dfa_overflowed` means "the DFA ENGINE cannot compile this pattern",
   which is FALSE when only the optional machine overflowed — the driver
   therefore SAVES and RESTORES `dfa_overflowed`/`dfa_overflow_why` across
   the optional build. Without that, a later unrelated `ctx_fail` would see
   a stale `true` and take `[SEL-1]`'s retry path for the wrong reason.
   (`Ctx.subset_elems` is NOT restored: the memory really was spent, and
   K7's bound is a claim about what the construction spends.)

An overflowed anchored machine selects `search-filter`. **It is stamped, it
is counted, and it is never a diagnostic** — see §9's pinned population.

### 5.3 What the anchored form's `UnanchStart` is

`dfa_form_derive` reads the artifact's start analysis (`UnanchStart`) for
the view flags, the prefilter verdict and the candidate set. The anchored
machine has no start analysis — it does not search — so it is derived from
a value built by `anch_start()`: a copy of the search's `UnanchStart` with

- `kind = DFA_PF_NONE`, `cand` zeroed, `ofsk` zeroed — §3.7's invariant, and
  the reason axis B selects `none` without a branch anywhere;
- `eol` / `endv` / `viewsel` / `views` recomputed **from the anchored machine
  alone** (§3.4), where the search pair uses the artifact-level OR of its two
  machines. Strictly more accurate, and structurally incapable of moving an
  existing artifact's bytes because it is a different object.

### 5.4 The deny flag

`-fno-anchored-dfa` / `PCREC_NO_ANCHORED_DFA`, **bit 17** (the next free bit
after `[OPT-K]`'s `PCREC_NO_OFFSET_SKIP` at 16). It is a `deny` field on the
`unwrapped` candidate, which is D82's shape: the flag removes the object, the
fallback is selected by the ordinary walk, and nothing branches on the flag.

Under the flag the anchored machine is not built at all (the build is gated
on the same selection, so the flag costs no compile time either) and the
artifact is `search-filter` — the pre-row compiler's `_match` body,
character for character, **plus the new stamp line** (D81: selection facts
are stamped unconditionally, so the denied build is NOT byte-identical to
the pre-row compiler; it differs by exactly `<PREFIX>_DFA_MATCH` and
`rx_info.match_form`). §9 states that as the gate rather than claiming
byte-identity r39's A1 finding already refuted for `[OPT-K]`.

`--list-axes` gains the axis through the same live accessor the other six
DFA axes use, so the registry check sees it with no hand-copied restatement;
`docs/spec/tuning.md` gains §2.15 in §2.14's deny-only shape; the axis
registry check's named-check count moves 59 → 60.

---

## 6. The `abi` bump and its FOUR sites (D76)

This change moves EMITTED PROGRAM BYTES on every `ENG_UNANCH` DFA artifact
that selects the form (a new table block and two rewritten entry bodies),
and SCAFFOLDING on every DFA artifact (one stamp line) and every artifact of
either engine (one `rx_info` field). `abi` moves **9 → 10**, in this one
change, at all four sites:

| # | site | what moves |
|---|---|---|
| 1 | `src/gen/emit_dfa.c` — `.abi = 10` | the stamp itself |
| 2 | `tests/codegen/run_codegen_tests.sh` — `ABI_EXPECT` and the [DD-14.FB] §10.4 sentence | the expectation both engines are checked against |
| 3 | `docs/spec/match_api.md` §6 — "`rx_info.abi` is `10`" (and §1's cross-reference) | the contract |
| 4 | `tests/codegen/run_recursion_identity.sh` — comparison (B)'s FILEPIN | the whole-file reference |

Comparison (A) of `run_recursion_identity.sh` (`goto <p>_L0;` through
`<p>_accept:`, i.e. the VM PROGRAM) is expected byte-identical: every byte
this row writes on a VM artifact is the one `rx_info` field, which is above
that region. Comparison (B) compares whole files and is re-pinned here.

**What moves on which artifact kind** (r37 A12's lesson — say it explicitly):

- `ENG_UNANCH` DFA artifact that selects `unwrapped`: a file-scope
  `<p>_anchored_state` accessor block, an anchored table set inside
  `<prefix>_match`, rewritten `_match` / `_match_caps` bodies, one
  `#define <PREFIX>_DFA_MATCH "unwrapped"`, one `rx_info.match_form` field.
  `<prefix>_search` is untouched.
- `ENG_ATTEMPT`, empty-engine, overflowed or `-fno-anchored-dfa` DFA
  artifact: the stamp line (`"search-filter"`) and the `rx_info` field. The
  bodies are unchanged character for character.
- VM artifact, hybrid or not: the `rx_info` field only
  (`.match_form = NULL`). The hybrid does NOT stamp `<PREFIX>_DFA_MATCH` —
  its `_match` is the VM's own anchored body, not this emitter's — which is
  why the stamp lives in `emit_dfa_stamps` (DFA-only) and not in
  `pcrec_emit_dfa_scan_stamps` (shared with the hybrid).

Spec hunks owed in the same change (D80): §3.2's mechanism paragraph and its
COST-CONSEQUENCE caveat (the worst case goes away when the form is selected,
and the caveat must now say WHICH artifacts still have it and how a caller
reads that off the stamp), §3.3's cross-reference, §6's `abi` sentence, §6's
`rx_info` field list, §6.3's macro table and its value set, and
`docs/spec/tuning.md` §2.15. `docs/spec/limits.md` DOES get a hunk after all, and the
reason is worth stating: no new cap is introduced — the anchored machine is
charged against the ceilings that already exist — but that document's
`[SEL-1]` paragraph is precisely about what crossing one of those three
ceilings MEANS, and this row adds a second, narrower answer to it (no
diagnostic, no fallback engine, just the other form of one entry). The set of
patterns pcrec accepts is unchanged in either direction, so no ceiling joins
its list.

---

## 7. Measurement

Discipline is `docs/dev/opt2_anchored_match_measurement.md`'s: `taskset`
pinned, median of 5 interleaved trials, ≥ 1 s per trial, `load1` recorded at
the start, the bench's subjects and patterns read READ-ONLY.

Arms: **default** (this compiler), **`-fno-anchored-dfa`** (the same
compiler, form denied — the honest "before", since it is the same binary),
and the VM (`--engine=vm`) for the ratio `opt2m` states the target in.

| # | question | number to beat |
|---|---|---|
| 1 | matching compliance subjects, DFA vs VM | ≤ 1.046× (isolation parity); today 2.077× |
| 2 | 35 short valid emails, DFA vs VM | ≤ 0.571×; today 1.207× |
| 3 | FAILING match-here on a 1 MB subject that diverges at byte 3 | O(1), not O(n) — a flat curve against subject length |
| 4 | `_search` on the same corpus | UNCHANGED (this row does not touch it) |

### 7.1 MEASURED (2026-08-29, lane engabs)

Box and discipline: `taskset -c 3`, `adriver` transcribed from `opt2m`'s (§1
there) — per-subject iteration calibration toward a 30 ms timed run, **median
of 5 independent process invocations** per subject before summing into set
totals. Artifacts are the `(?:orig)\z` spelling `opt2m` measured, all
`--features all`, all from this worktree's build:

| arm | invocation | stamps |
|---|---|---|
| `on` | default | `RX_ENGINE "dfa"`, `RX_DFA_MATCH "unwrapped"`, `RX_DFA_PREFILTER "byte-class-bounded"`, `RX_DFA_TABLE "premultiplied"` |
| `off` | `-fno-anchored-dfa` | the same, `RX_DFA_MATCH "search-filter"` |
| `vm` | `--engine=vm` | `RX_ENGINE "vm"` |

`load1` 1.47 → 0.88 across the series (no number here turns on it: the
calibration is self-normalizing per subject, `opt2m` §1's argument).

**THE `off` ARM REPRODUCES `opt2m`'s NUMBERS, which is what makes the `on`
column comparable to the row's targets rather than to a new baseline**:
2.132× vs `opt2m`'s 2.133× on the set, 2.074× vs 2.077× on the matching
split, 1.223× vs 1.207× on the short valid emails. Different lane, different
build, same measurement.

#### Questions 1, 2 and 4 — the compliance set (85 subjects, `orig`/`match`)

Set totals, ns per call summed over the split:

| split | n | `on` | `off` | `vm` | **on/vm** | off/vm | on/off |
|---|---|---|---|---|---|---|---|
| ALL | 85 | 72,585.0 | 133,274.8 | 62,516.8 | **1.161** | 2.132 | 0.545 |
| MATCHING | 40 | 48,337.1 | 97,202.1 | 46,874.6 | **1.031** | 2.074 | 0.497 |
| NON-MATCHING | 45 | 24,247.9 | 36,072.7 | 15,642.2 | **1.550** | 2.306 | 0.672 |
| short valid emails (`len <= 40`) | 35 | 899.8 | 2,284.3 | 1,867.3 | **0.482** | 1.223 | 0.394 |

- **Question 1 MET.** Matching subjects: **1.031×** the VM, against a target
  of ≤ 1.046× (the isolation's parity figure) and a starting point of 2.074×.
  The form is at parity with the backtracking VM on the specimen's own
  matching population.
- **Question 2 MET, with room.** The 35 short valid emails: **0.482×** — the
  DFA answers them **2.07× FASTER than the VM** — against a target of ≤ 0.571×
  and a starting point of 1.223× behind. The isolation understated it by 16 %
  for the reason §4 gives: it still paid the self-loop and skip machinery this
  form removes outright.
- The NON-MATCHING split improves least (2.306× → 1.550×), and that is the
  expected shape rather than a shortfall: `opt2m` measured the reverse pass at
  13.9 % of cost there, because a non-matching compliance subject is a
  NEAR-MISS email that the forward scan walks to the end regardless. What
  question 3 is about is the other kind of failure.
- **Question 4 holds by construction and is checked, not asserted**:
  `<prefix>_search` is byte-for-byte unchanged, and
  `tests/anchored/run_anchored_diff.sh` compares it between the two builds on
  every cell.

#### Question 3 — the FAILING match-here on a long subject

The original `[ENG-ABS]` motivation. Subject: `"abc\n"` followed by filler —
`abc` is a valid atom prefix and the newline cannot continue it (not an atom
byte, not `.`, not `@`), so the match at `ctx->pos = 0` fails at byte 3. Two
fillers, because the spec caveat's parenthesis ("the state-0 `memchr` skip
keeps this a skim rather than a per-byte walk") is a real distinction: `x` is
a candidate start, so the prefilter skips nothing; `\n` is not, so the skip
loop runs. Median of 3, ns per call:

| filler | length | `on` | `off` | `vm` | **off/on** |
|---|---|---|---|---|---|
| `x` | 1 KB | 5.5 | 1,921.3 | 15.9 | 350× |
| `x` | 16 KB | 5.4 | 30,884.8 | 15.8 | 5,744× |
| `x` | 256 KB | 5.5 | 495,905.5 | 15.8 | 90,709× |
| `x` | **1 MB** | **5.5** | **1,988,004.8** | 15.8 | **363,305×** |
| `\n` | 1 KB | 5.4 | 401.4 | 15.8 | 74× |
| `\n` | 16 KB | 5.4 | 5,858.2 | 15.8 | 1,090× |
| `\n` | 256 KB | 5.4 | 96,878.5 | 15.7 | 17,927× |
| `\n` | **1 MB** | **5.4** | **379,549.9** | 15.7 | **70,759×** |

**The `on` column is FLAT — 5.4 to 5.5 ns at every length, on both fillers —
and the `off` column is linear in the subject.** That is the claim: a failing
match-here costs O(divergence), not O(subject). It is also **2.9× faster than
the VM's own anchored body** at 15.8 ns, which the row did not promise. The
two fillers differ by 5× in the `off` column and not at all in the `on` one,
which is the spec caveat's skim-versus-walk distinction becoming moot.
(r41 critic-meas, M5: of the flat ~5.5-5.8 ns, an empty-subject call
measures ~3.6 ns — about 62 % is the harness's call/loop cost and ~38 % the
pattern's own divergence work; O(1) holds, "flat 5.5 ns" is mostly the
instrument.)

#### What this closes

`[OPT-2]`'s lever (a) is discharged: the reverse pass is gone from the
anchored entry, the ~50 % it cost on matching subjects is recovered, and
§3.2's documented worst case no longer applies to an artifact that selects
the form.

---

## 8. Size

The census's shipped `.o` median is 6,760 B; `docs/dev/artifact_size_log.tsv`
(comment-excluded `.c`+`.h` SOURCE bytes, the units `scripts/size_diff`
diffs) puts the 1,185 corpus DFA artifacts at min 9,071 / median 15,338 /
p99 21,794 / max 97,789 B.

The form adds ONE table set per selecting artifact — a 256-byte class table,
a transition table (`n × ncls` cells), an accept table, and the view/seed
tables the machine's own dimensions ask for. The anchored machine is
typically SMALLER than the wrapped forward machine (no self-loop means fewer
merged states), so the expected delta is well under a doubling of the
artifact's table bytes.

The `[ART-SIZE.1b]` tripwire pins are `MAX_SIZE_BYTES = 1,400,000` and
`MAX_GCC_CPU_S = 8.0`; the corpus max is 651,344 B on a VM artifact
(`tests/counterk`), which this row does not touch, and the largest DFA
artifact is 97,789 B — 14× under the pin. The tripwire is not at risk; the
number that matters is `scripts/size_diff`'s old-vs-new log, reported as a
delivery number.

### 8.1 MEASURED (2026-08-29)

`scripts/size_diff` over the whole corpus, `tests/size/run_size_log.sh` at
`PROCS=10`, `load1_at_start` 1.34 — 2,875 rows, 0 vanished, 0 new. Units are
the log's own: comment-excluded `.c`+`.h` SOURCE bytes.

| population | n | delta min | median | p99 | max | ratio median | ratio max |
|---|---|---|---|---|---|---|---|
| DFA artifacts | 1,185 | +111 B | **+2,605 B** | +6,743 B | +44,031 B | **1.175×** | 1.450× |
| VM artifacts | 1,690 | +63 B | +63 B | +63 B | +63 B | 1.003× | 1.003× |

Corpus total 64,219,443 → 67,362,750 source bytes, **+4.89 %**.

- The DFA median grows 15,338 → 18,003 B and the largest DFA artifact 97,789
  → 141,820 B — **10× under** the `MAX_SIZE_BYTES = 1,400,000` tripwire. The
  corpus's worst artifact overall is unchanged in kind (a VM artifact,
  `tests/counterk/counterk.rxt:1807`, 651,344 → 651,407 B) and the worst
  `gcc_cpu_s` is 4.943 s against the 8.0 s pin. `check_size_tripwire.sh`
  reports **OK** on the new log; the tripwire is not approached from either
  side.
- The DFA delta is a table set, as §8 predicted, and lands well under a
  doubling: **the anchored machine really is smaller than the wrapped forward
  one**, which is the size half of §2's derivation confirming itself.
- The VM delta is a CONSTANT 63 B on all 1,690 — the `rx_info` member and
  nothing else. See the next paragraph for why it is not 716.

**A MEASURED SIZE FINDING THIS ROW DID NOT SET OUT TO MAKE.**
`tests/lib/size_count.sh`'s comment classifier is LINE-BASED: it recognises a
line that STARTS a block comment and tracks the block to its end, so a comment
placed ABOVE a struct member costs zero counted bytes — while the continuation
lines of a TRAILING multi-line comment do not start a block and are counted as
CODE. The first draft of `rx_info.match_form` used the trailing shape its two
neighbours (`scan`, `prefilter`) use, and `size_diff` reported **+716 B on
every one of the 2,875 artifacts**, +7.82 % on the corpus total. Moving the
comment above the member took the VM delta to +63 B, the DFA median from
+3,258 B to +2,605 B, and the corpus total from +7.82 % to +4.89 %. **`scan`
and `prefilter` still carry the trailing shape and therefore still carry that
cost**; changing them moves emitted text for two other rows' stamps — two more
`abi` bumps — and is not this row's to do. Recorded here and in
`tests/size/CLAUDE.md` rather than done.

**OPEN (not built, no measured need — D77).** `adfa->clsmap` is
byte-identical to `dfa->clsmap` by §2's derivation, so the artifact emits a
duplicate 256-entry class table — measured at **1,478 B of emitted source**
on a representative artifact (the table is printed as decimal cells, not raw
bytes), i.e. **57 % of the +2,605 B median DFA delta** above and 8.2 % of a
median DFA artifact. That is a larger share than §8's first estimate assumed,
and it is the strongest of the three OPEN items for that reason. Sharing it is a conditional
emitted-text shape, i.e. another axis. Named here with its measurement, not
built.

**The `.o` side (r41 critic-meas, M11 — measured after delivery, in the
row's favour).** On 10 DFA artifacts spanning 9-141 KB of source, compiled
`-O2 -c` in both forms: the `.o` delta is **1.7-11.0 % of the SOURCE delta**
(median ~2-5 %) on the 8 that select `unwrapped` — e.g. the largest sampled,
`c{1,}?(?:$|[\n\t]+?01{1,2}|[^abc]){2,}`, +11,152 B of source and +1,232 B of
`.o` — against the census's general ~17 % `.o`/source ratio. The anchored
table is verbose decimal C that compresses in the binary far more than the
rest of the artifact does, so the shipped-binary cost of this row is well
under the +4.89 % source headline. The 2 sampled artifacts on ENG_ATTEMPT /
`empty` scan show zero delta on both sides, as §5.1/§6 say they must.

---

## 9. The checks

| # | kind | what |
|---|---|---|
| 1 | structural | `tests/codegen/run_anchored_match.sh` — reads the ARTIFACT: the stamp present on every DFA artifact with the value the body actually has; the anchored table block present **iff** `unwrapped`; NO prefilter construct inside the `_match` body (§3.7); `_match_caps` writing the dead groups (§3.9); the fallback population PINNED at an exact count |
| 2 | identity | the `-fno-anchored-dfa` build vs the default build over the WHOLE corpus: answer-identical on every entry, and differing from the pre-row compiler's output by exactly the new stamp line and the `rx_info` field — **NOT byte-identical** (D81), which is r39 A1's correction applied at design time rather than after |
| 3 | identity | the existing DFA-vs-VM gates (`run_vm_identity*.sh`) stay green — they exercise `_match` on both engines and are the strongest existing check of the accept discipline |
| 4 | sweep | `make test-axes` gains `-fno-anchored-dfa` (the manager runs the sweep) |
| 5 | sabotage | one `tests/mech` row that breaks the ACCEPT DISCIPLINE — the natural one is "record the FIRST accept instead of the last", which §3.3(a) is precisely the argument against, and which a greedy pattern detects |
| 6 | census | the form census floors: axis G's two values are new populations, and `RX_DFA_TABLE`'s `mixed` population may move because the composition now spans three machines rather than two (§5.1) |

### 9.1 MEASURED OUTCOMES (2026-08-29)

| # | instrument | result |
|---|---|---|
| 1 | `tests/codegen/run_anchored_match.sh` | **14 passed / 0 failed**. Census over 2,786 corpus patterns: 1,489 vm, 288 refused, **825 unwrapped**, 180 `search-filter`(attempt), 4 `search-filter`(empty), **0 `search-filter`(overflow)** |
| 2 | `tests/anchored/run_anchored_diff.sh` | **5 passed / 0 failed**. 1,213 patterns × 18 subjects, every position 0..n+1, all four anchored entries + every capture pair + the search control — **147,986 cells, 0 divergences** |
| 3 | `tests/codegen/run_recursion_identity.sh` | green; (B) whole-file identity 2,224/2,224 against the re-pinned `14d1feb`, (A) program-region identity against the UNCHANGED pre-module `ac4917d` with exactly the four named wave-G elision patterns moving — i.e. this row writes no VM program byte |
| 4 | `make test-codegen` | 106 / 31 / 22 / 7 checks, 0 failed, after `[M6.2-KRESET rule 3b]` grew its second arm |
| 5 | `tests/mech` S189 | pre-validated DETECTED, with `tests/base/alternation.rxt` **26/0** and `run_anchored_match.sh` **14/0** on the same planted tree |
| 6 | `tests/registry` | 64 / 0 (coverage re-pinned 59 → 64) |
| 7 | `make strict` | clean |
| 8 | the D81 DIFFERENCE SET, measured | the `-fno-anchored-dfa` build against the PRE-ROW compiler over **2,498 corpus patterns**: **0 byte-identical, 2,498 differing ONLY in the expected lines, 0 other, 0 refusal mismatches** |
| 9 | `make -k -j12 test` (delivery run) | **sections ran: 27/27**, zero `FAIL` lines anywhere, `test-anchored-match` **14/0 + 5/0** inside it. ONE red: `test-corpus` 26,630 passed / **29 failed**, all of them `tests/counterk/counterk.rxt`'s `((a)|ab){4000}c` at exit 124 — the KNOWN load cell the `[ART-SIZE.1b]` journal already records failing under `-j12`. Re-run SOLO on a quiet box: **1,634 passed / 0 failed** |

**CHECK 8 IS THE ONE THE BRIEF NAMES AND D81 MAKES FALSE IN ITS OBVIOUS
FORM.** A "byte-identical under the deny flag" claim would be wrong — selection
facts are stamped unconditionally — so what is measured instead is the exact
DIFFERENCE SET, and it comes back as precisely eleven distinct lines over the
whole corpus:

```
#define RX_DFA_MATCH "search-filter"        (DFA artifacts only)
.abi = 9,  ->  .abi = 10,
.match_form = NULL,  /  .match_form = "search-filter",
const char           *match_form;           + its 5-line block comment
```

Nothing else moves on any of the 2,498, which is what makes the denied build a
usable control rather than a second variant.


**AND THE ONE THING THAT MEASURED NOTHING, stated because it is the row's own
vacuity risk realised.** `make test-axes`'s `-fno-anchored-dfa` sweep is
**trivially green and always will be**: `tests/harness/run.sh`'s `RXTDUMP`
records the driver's exit code and stdout, which is `<prefix>_search`'s answer,
and this row does not touch `<prefix>_search`. The corpus driver's own anchored
arm is an `_in`-vs-un-suffixed cross-check whose two sides are one code path.
So the axis sweep is a control on the SEARCH, and instrument 2 is the only
thing in the tree that can be red for a wrong anchored ANSWER. The flag still
joins the sweep — an axis with no sweep entry is the omission `[CHK-2]` exists
to catch — but nobody should read its green as evidence about this form.

**The vacuity trap this row must avoid**, named because the brief names it:
today `docs/spec/match_api.md` §3.2's caveat describes a COST, not a
refusal, so no existing test asserts a refusal that could silently become a
fallback. The new one is check 1's PINNED FALLBACK COUNT: if the anchored
machine silently stopped building for everything, `search-filter` would be
100 % and the check must go red on the COUNT, not merely on the presence of
a stamp value that is still legitimately reachable.

---

## 10. Open questions

1. **`ENG_ATTEMPT` keeps `search-filter`.** Its `_match` skims too (an
   attempt loop with `start_max = n` on `(^a|b)c`), and the fix there is a
   different mechanism — clamp the attempt loop to one start — with its own
   accept-discipline argument. Not opened by this row; the stamp names the
   population honestly so a bench row can find it.
2. **The `\z`-view fold** (`opt2m` lever (b), 3-5 %) belongs to `[DD-13]`(b)
   and is not folded in here.
3. **Class-table sharing** (§8.1's OPEN) — measured at **1,478 B, 57 % of the
   median DFA delta**, which is far more than §8's pre-measurement estimate of
   "~1.7 % of a median artifact" and makes this the strongest of the three
   OPEN items. Still not built: it is a conditional emitted-text shape, i.e.
   another axis with another `abi` bump, and D77 says wait for the need.
4. **`scan` and `prefilter`'s trailing comments cost every artifact ~700 B**
   of counted source (§8.1's classifier finding). Fixing them is two other
   rows' emitted text and therefore two other `abi` bumps; recorded, not done.
5. **`make test-axes`'s `-fno-anchored-dfa` arm is trivially green** and
   cannot be otherwise (§9.1). Whether the sweep should gain a route that
   drives the ANCHORED entries — the corpus driver already has the `_in`
   cross-check machinery and would need only an oracle for the anchored
   answer, which `tests/anchored/` now supplies — is a real question about
   `[CHK-2]`'s sweep and not this row's to rule.
6. **The NON-MATCHING split improves least** (2.306× → 1.550×, §7.1). The
   remaining gap there is not the reverse pass; `opt2m` measured that at
   13.9 % on non-matching subjects. What is left is the forward scan itself
   on a near-miss email, which is `[OPT-3]`/`[OPT-K]` territory rather than
   this row's.
