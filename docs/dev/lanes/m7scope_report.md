# m7scope — R-8 / M7 step 1: READ-ONLY scoping of N7 (the encoding seam's span compare)

Lane m7scope (opus), 2026-10-08. Tree read: `worktrees/memfn`, branch
`lane/memfn-m7` @ dfb22593 (main bec97b31 + the kit's R-8 ack). Nothing
was edited and nothing was committed. No make and no suite ran. The probes
used the existing `worktrees/memfn/build/pcrec` (built 10:25) under
`gnutimeout 60`; their outputs are in `worktrees/memfn-slot/m7scope/probes/` (gitignored scratch; regenerable).
`probes/span_text_by_probe.txt` holds the extracted span bodies. All
file:line references are this branch's tip.

## 0. Summary (resume from here)

- **Edit set.** pcrec side: 8 source files, plus checks and pins (§1).
  Kit side: memfn.h, compose.c, fields.def, gate.c, generic.c or a new row
  file, kit.h, the K1 refs, PROVENANCE and the CLAUDE.md files. No byte
  moves in `src/gen/emit_vm.c`, `src/core/compile.c` or
  `src/opt/select_engine.c`.
- **Boundary recommendation:** the kit renders the COMPARE LOOP ONLY (a
  STMT site inside the encoding's function). The backend keeps every other
  byte: the signature, the braces, the full-match `return
  (ptrdiff_t)reflen;`, the fold (as hook text), the return-protocol
  statement (as hook text), the UCP fold function and table, and all the
  doc comments and declarations. Whole-function (FUNC) rendering is wrong
  on linkage, on ABI ownership and under DD-12 (7) (§2).
- **A finding that changes the plan:** `u8_defs_bref_ci`, utf8's caseless
  compare, is NOT a byte mismatch. It is a two-cursor, per-CHARACTER
  decode+fold walk whose consumed length differs from the reference's.
  It is already in N7's manifest row and in C17's vocabulary
  (`span-decode`). Q-R8-1 recommends splitting it into its own pending row
  (N7U).
- **Vocabulary:** `MF_VOCAB` 2 → 3 (op `MF_OP_MISMATCH`, term kind
  `MF_T_REF`, one handoff). `MF_SITE_ABI` 6 → 7, because new hooks
  (`ref`, `reflen`, `fold`) and site facts (`fold_kind`, `fold_map`) are
  appended last. This is a kit-only prep commit, as in M4's Phase A (§3).
- **Overlap verdict: DISJOINT** (§4).
  - Refactor B3 touches `compile.c`, `select_engine.c` (a 4-line comment)
    and tests.
  - B4/B5 touch `select_engine.c`, `emit_vm.c` (the emit-ir chain at
    9443-9541 and VM_PREFILTER_WHY at 11264) and `compile.c`.
  - M7 touches none of those.
  - The only shared file is `src/gen/emit_dfa.c`: M7 touches
    `emit_residual_defs` (3245-3258); B reads `fit.*` elsewhere. That is a
    different function, so the merge risk is low.
  - No branch or worktree has unmerged `src/enc/` work.
- **C17/C12 already scan `src/enc/`.** That landed at R4a (memfnmanifest):
  `SCAN_DIRS`, and the vocabulary lines `span-index` and `span-decode`. The
  scope is unchanged. M7 flips the manifest row and deletes the ceiling
  rows (§5).
- **The rider is confirmed dead.** No pcrec text spells `memchr(`. It also
  breaks S517's anchor, which shares the line (§5.3).
- **Open questions:** Q-R8-1..Q-R8-10 (§8).

## 1. The edit set

### 1.1 Every backend that emits a span match

`src/enc/` has two backends, `enc_byte.c` and `enc_utf8.c`. `enc.c` is the
registry and emitter. It also GENERATES the byte UCP fold table.
`utf8_fold_pairs.inc` is data. There is no third backend.

| entry (mask id) | byte backend | utf8 backend | shape |
|---|---|---|---|
| `PCREC_ENCE_SPAN` | `defs_bref` enc_byte.c:152-162 | `u8_defs_bref` enc_utf8.c:125-135 | byte loop, exact. Byte-identical text in both backends |
| `PCREC_ENCE_SPAN_CASELESS` | `defs_bref_ci` enc_byte.c:183-199 | `u8_defs_bref_ci` enc_utf8.c:167-212 | byte: a byte loop that folds in place (ASCII). utf8: a per-char decode walk (NOT byte-wise) |
| `PCREC_ENCE_SPAN_CASELESS_UCP` (byte only) | `defs_bref_ci_ucp` enc_byte.c:303-327 (fold fn 304-315, loop 317-327), plus the table from `enc_emit_latin1_fold_table` enc.c:120-136 | (no row: utf8's one fold is already Unicode) | byte loop, EXPR fold `$_span_ci_fold(...)` |

The callers stay pcrec's and do not move:
- `vm_bref`, emit_vm.c ~8545-8640 (`took = %s(subject, ...)` and its
  work charge);
- `vm_var`, emit_vm.c:8656-8690;
- `vm_caseless_entry`, emit_vm.c:8477-8483.

The entry choice, the `engine_callable` assertion, `enc_mask` and the call
text are the engine's.

### 1.2 Emitted text, probed (`--features all`; backrefs need it)

The probes are in `probes/*.c`. Each was run with `-p rx -o <name>.c`, so
the decls are in `.h` and the defs in `.c`. By default no `defs_doc`
reaches the artifact; the `-fcomments` probes show it.

**byte `(a+)\1`, utf8 `(a+)\1`, byte `a${v}b` and utf8 `a${v}b` all emit
the same text:**

```
ptrdiff_t rx_span_match(const unsigned char *s, size_t n,
                       const unsigned char *ref, size_t reflen, size_t at)
{
    size_t i;
    for (i = 0; i < reflen; i++) {
        if (at + i >= n || s[at + i] != ref[i])
            return -(ptrdiff_t)i - 1;
    }
    return (ptrdiff_t)reflen;
}
```

**byte `(?i)(ab)\1` and byte `(?i)a${v}b`.** The ASCII fold is in place,
and there are two `on_miss` exits:

```
ptrdiff_t rx_span_match_caseless(const unsigned char *s, size_t n,
                                const unsigned char *ref, size_t reflen,
                                size_t at)
{
    size_t i;
    for (i = 0; i < reflen; i++) {
        unsigned char x, y;
        if (at + i >= n) return -(ptrdiff_t)i - 1;
        x = s[at + i];
        y = ref[i];
        if (x >= 'A' && x <= 'Z') x = (unsigned char)(x + 32);
        if (y >= 'A' && y <= 'Z') y = (unsigned char)(y + 32);
        if (x != y) return -(ptrdiff_t)i - 1;
    }
    return (ptrdiff_t)reflen;
}
```

**byte `--ucp (?i)(ab)\1`, also reached by `(*UCP)` in the pattern.** It
emits `static const unsigned char rx_span_ci_fold_pairs[][2]` (enc.c), then
`static unsigned char rx_span_ci_fold(unsigned char c)` (a binary search),
then:

```
    size_t i;
    for (i = 0; i < reflen; i++) {
        if (at + i >= n || rx_span_ci_fold(s[at + i]) != rx_span_ci_fold(ref[i]))
            return -(ptrdiff_t)i - 1;
    }
    return (ptrdiff_t)reflen;
```

**utf8 `(?i)(ab)\1`.** It emits a ~26 KB `unsigned` fold table,
`rx_span_ci_fold(unsigned c)`, and the inline `rx_decode` (the DECODE
entry, required by this one). Then:

```
    size_t i = 0, j = at;
    while (i < reflen) {
        unsigned x = 0, y = 0;
        size_t lx = rx_decode(ref, reflen, i, &x);
        size_t ly = (j < n) ? rx_decode(s, n, j, &y) : 0;
        if (lx == 0 || ly == 0 ||
            rx_span_ci_fold(x) != rx_span_ci_fold(y))
            return -(ptrdiff_t)(j - at) - 1;
        i += lx;
        j += ly;
    }
    return (ptrdiff_t)(j - at);
```

So the byte-wise compare has **three distinct shapes**: exact, an EXPR
fold, and an in-place fold. All three are covered by **four text
constants**, because `u8_defs_bref` is `defs_bref` verbatim. utf8's
caseless walk is a fourth shape, and it is not a byte mismatch.

### 1.3 What moves and what stays, per file (recommended design, §2)

**pcrec side.** In the list below, "token" means a site token in the
`defs` text that the emitter renders through the kit.

- **`src/enc/enc_byte.c`.**
  - `defs_bref` (152-162): the loop lines become a site token; the
    signature, braces and the tail return stay.
  - `defs_bref_ci` (183-199): the same. The two fold lines become a fold
    template constant (the backend's text).
  - `defs_bref_ci_ucp` (317-327): the same. The fold becomes the EXPR
    template `$_span_ci_fold(@)`. The fold function (304-315) is
    unchanged.
  - `entries_byte[]` (336-344): the three span rows gain their site data
    (Q-R8-3).
- **`src/enc/enc_utf8.c`.**
  - `u8_defs_bref` (125-135): the same as `defs_bref`.
  - `entries_utf8[]` (489-492): the exact row gains its site data.
  - `u8_defs_bref_ci` (167-212) is UNCHANGED under Q-R8-1 (a).
- **`src/enc/enc.c`.** `enc_emit_defs` (143-160) and
  `pcrec_enc_emit_defs` (162-167) render the site token through a renderer
  the gen layer passes in.
  - `pcrec_enc_emit_text` (209) either learns the token or gets a sibling.
    No backend text contains `@` today.
  - `pcrec_enc_emit_inline_defs` (170) is unchanged: no span entry is
    inline.
- **`src/enc/enc.h`.**
  - `PcrecEncEntry` (83-123) gains the site column, OR `PcrecEnc` (220-)
    gains a field (Q-R8-3).
  - The `pcrec_enc_emit_defs` prototype (455) changes.
  - The "WHY TEXT AND NOT A CALLBACK" note (30-34) and the third-encoding
    recipe (36-) are amended. This is a D58 seam event, recorded in place.
- **`src/enc/CLAUDE.md`.** Record the seam event (the
  max_cp/fold/advance/K50 precedent), plus one recipe line: "a backend's
  byte-wise span entry states its site instead of spelling the loop".
- **`src/gen/emit_dfa.c`.** In `emit_residual_defs` (3245-3258), the
  `pcrec_enc_emit_defs` call (3257) passes the gen-side renderer. Call
  site: `pcrec_emit_residual`, 11175.
- **`src/gen/memfn_sites.{c,h}`.** A describer, e.g. `span_site(cx, sb,
  const PcrecEncSpan *)`. It builds `mf_site`/`mf_hooks` from the backend's
  data and calls the door `pcrec_memfn_emit`. The art is created lazily
  (`pcrec_memfn_art`, memfn_sites.c:66). It is ended in the finishing pass
  (compile.c:2731), which runs after `pcrec_emit_residual`, so the
  lifecycle fits.
- **`src/gen/memfn_sites.def`.** New row `DELEG_SITE(N7, MF_OP_MISMATCH,
  DELEG_H(<handoff>), MF_TK_REF, DELEG_LOOP, MF_USE_POSITION)`.
- **`src/gen/memfn_stamps.c:47`.** The rider: delete `"memchr",` (§5.3).
- **Checks and pins.**
  - `tests/memfn/site_manifest.tsv`: N7 → delegated; split N7U
    (Q-R8-1); C17_ROW_FLOOR (`run_site_manifest.sh:38`) 13 → 14 under
    (a).
  - `tests/memfn/c12_ceilings.tsv`: delete the two `span-index` rows
    (enc_byte 3, enc_utf8 1); C12_CEIL_ROWS_FLOOR
    (`run_form_checks.sh:23`) 5 → 3. Under (b) also delete `span-decode`,
    giving 5 → 2.
  - `tests/memfn/run_deleg_sites.sh:28`: `D91_LOOP` gains N7.
  - `tests/memfn/rows.tsv` and `row_floors.tsv`: the new kit row(s), with
    witness, signature, control and census floors.
  - `tests/memfn/arm_fixtures.c` and the pins: fixtures for the new row(s)
    (M4's `render_emit` precedent), ARMS_ROW_FLOOR, and the gate cases.
  - Sabotages per §6.
  - `docs/design/start_table/{call_graph.txt,sabotage_anchors.tsv}`:
    re-derive with their scripts. Anchors are text, but the map records
    owners and lines.

**Kit side.**
- `memfn/include/memfn.h`: `MF_VOCAB` 3; `MF_SITE_ABI` 7; the op, term
  kind and handoff; the hooks and site fields; the K1 reference
  `mf_ref_mismatch` (F8).
- `memfn/src/compose.c`: `vocab[]` (~495-513), `site_check`, `arms[]`.
- `memfn/src/fields.def`: new fields and classes (`fold` EXPR/INPLACE
  shapes; `on_miss` JUMP pasted more than once).
- `memfn/src/gate.c`: lexical classes.
- `memfn/src/generic.c` (totality: the generic row must render MISMATCH),
  or a new `mismatch.c` row file, plus `kit.h`.
- `memfn/src/k1_ref.c`, `PROVENANCE.md`, and
  `memfn/{,include/,src/}CLAUDE.md` (the readers of `MF_SITE_ABI` and
  `MF_VOCAB`, by grep: `memfn.h:40,50`, `include/CLAUDE.md:8,33`,
  `memfn/CLAUDE.md`, `src/CLAUDE.md`).
- `memfn/tests/` belongs to the blinded G2 lane.

**Docs.**
- `integration.md`: a §15.x for the N7 shape as built, §22 M7 as built,
  and §R4.3.4's N7 note.
- `docs/dev/decisions.md`: a D58 addendum, which is main's to write
  (Q-R8-3).
- **No `docs/spec/` hunk and no abi bump.** Nothing a caller observes
  changes: the entry names, signatures, return protocol and stamps are all
  unchanged.

## 2. The boundary under D58 / DD-12 (7)

DD-12 (7) (plan_completed.md:4010-4035) says encodings are "SEALED
backends ... all specialized code within". The per-encoding header is the
right seam for the residue. Under the third-encoding recipe, a new backend
touches only `src/enc/`. Q54's ruling (integration.md §23 item 54) says
"the fold and the encoding semantics stay the encoding's, and the seam
entry builds the `mf_site`, as a pcrec emitter does."

### 2.1 Byte for byte, for the three byte-wise shapes

| emitted bytes | owner after M7 | why |
|---|---|---|
| `decls_bref*_doc`, `decls_bref*` (the .h prototypes and their contract comments) | **backend text, untouched** | caller-facing entry ABI (D58 entry contract); the -fcomments prose is per-encoding |
| `defs_bref*_doc` (e.g. "byte encoding: one byte is one character, so the compare is a memcmp with a prefix count.") | **backend text, untouched** | per-encoding prose, gated by enc.c's comment layer |
| `ptrdiff_t $_span_match[_caseless](const unsigned char *s, size_t n, ... size_t at)` + `{` | **backend text** | the exported entry's signature (DD12a(ii) checks it is identical across backends) |
| `    size_t i;` | **kit** (declared as the site's `result`, with `result_decl` `size_t `) | the walk index is the form's, but pcrec names it because `on_miss` reads it |
| `    for (i = 0; i < reflen; i++) {` … `    }` (the bound test `at + i >= n`, the subject read `s[at + i]`, the reference read `ref[i]`, the `!=`, the temps `unsigned char x, y;`, `x = s[at + i];`, `y = ref[i];`, the layout and the indentation) | **kit** | the compare form itself: F8 `mismatch` |
| `return -(ptrdiff_t)i - 1;` (pasted once in the exact and UCP shapes, twice in the in-place shape) | **backend's TEXT, kit's PLACEMENT** (`on_miss` hook, JUMP class) | the seam's sign-encoded prefix protocol (R32 E4, D47 work unit) is the entry contract, not the kit's |
| `if (x >= 'A' && x <= 'Z') x = (unsigned char)(x + 32);` (and the `y` twin) | **backend's TEXT (a fold template), kit's PLACEMENT** (one paste per side) | the fold is encoding semantics (D23/§4.5: byte folds the 52 ASCII letters only) |
| `$_span_ci_fold(` … `)` around each operand (UCP) | **backend's TEXT (an EXPR fold template), kit's placement** | the same reason |
| `static const unsigned char $_span_ci_fold_pairs[][2] = {...};` and `static unsigned char $_span_ci_fold(unsigned char c) {...}` | **backend/seam text, untouched** (enc.c generator + enc_byte.c:304-315) | the fold's definition, generated from fold.c (K94); file scope, outside the site |
| `    return (ptrdiff_t)reflen;` + `}` | **backend text** | the full-match return protocol (the length a non-length-preserving backend would change) |

The kit's text then contains no encoding name, no prefix and no protocol.
It is a byte mismatch over two operand streams, with an optional
per-byte fold whose text and relation pcrec states. That is D146's
boundary: the hooks are pcrec's, and everything between them is the kit's.

### 2.2 The utf8 caseless walk (`u8_defs_bref_ci`)

This walk is per CHARACTER:
- `$_decode` on both sides;
- independent cursors `i` and `j`;
- the failure prefix is `j - at` subject bytes, and the success return is
  `j - at`, not `reflen`;
- the fold is over code points (a 1,484-pair `unsigned` table).

It is not F8 (requirements.md:143: "the length of the common prefix of
a[0..n) and b[0..n)"). Rendering it in the kit needs a decode hook, a
character-unit stream and a length-changing result: a second, larger
vocabulary item. See Q-R8-1.

### 2.3 Loop body or whole function: recommend the LOOP BODY (STMT)

1. **Linkage.** `$_span_match[_caseless]` is an EXPORTED entry. It is
   declared in the split artifact's public `.h` and called by the engine.
   The kit's FUNC form is a file-scope `static inline` definition named
   through `fn_ref` (memfn.h:73-75). It cannot be an exported entry with
   a public prototype and doc comment.
2. **ABI ownership.** The signature and the return protocol are D58's
   entry contract (`decls_bref_doc`). A FUNC rendering would move a
   caller-facing contract into the kit, and every later kit change to it
   would be a pcrec abi event by construction.
3. **DD-12 (7).** The backend keeps every per-encoding byte: the docs,
   the fold, the protocol and the length semantics. The kit gets only the
   encoding-neutral compare. The third-encoding recipe stays "write text
   in `src/enc/`". A backend opts into the site by placing the token,
   and opts out by spelling its own body (as utf8 caseless does under
   Q-R8-1 (a)).
4. **Zero movers is simpler.** The doc and declaration placement (decls in
   `.h`, defs_doc behind the comment gate) stay on enc.c's existing path.
   The kit reproduces only the loop lines.

## 3. The vocabulary gap

The current contract has nothing that compares the subject with a
RUN-TIME operand. RUN terms are compile-time `run[]`/`mask[]` arrays, and
VERIFY answers a bool. The proposal below is in contract terms; the kit
manager owns the spelling.

### 3.1 Additions

**`MF_VOCAB` 2 → 3**
- **op `MF_OP_MISMATCH`.** Over the subject window starting at `lo` and
  a run-time reference stream `ref[0..reflen)`. Its value is
  `k = the least j in [0, reflen) with lo + j >= n, or with
  fold(s[lo + j]) != fold(ref[j])`; if there is none, the spans are EQUAL.
- **term kind `MF_T_REF` (`MF_TK_REF`).** One REQUIRED term at offset 0.
  Its operands come from hooks, not data, because they are run-time.
  `pred.nterm` is 1, so Q-G2-10 (0 refused) holds.
- **one handoff.** Recommended: a new `MF_H_ON_DIFF`. On a mismatch,
  `result` = k is written, then `on_miss` runs and MAY READ `result`. On
  equality nothing is written and nothing runs. `on_miss` must leave
  (`on_miss_leaves` 1 required, class JUMP). The kit may paste it more
  than once: the in-place shape has two exits.
  - Reusing `MF_H_ON_MISS` or `ASSIGN` would bend their written rules:
    ON_MISS "writes nothing"; ASSIGN with `on_miss_leaves` 1 says
    "`result` is UNSPECIFIED on a miss and `on_miss` must not read it".
    See Q-R8-5.
- **vocab row:** `{ MF_OP_MISMATCH, MF_H_ON_DIFF, MF_TK_REF }` only (D77:
  no ASSIGN/BOOL variant without a customer).

**`MF_SITE_ABI` 6 → 7** (appended LAST, as `count_by_caller` was)
- **`mf_hooks.ref`, `mf_hooks.reflen`.** Side-effect-free C expressions
  (IDENT class today: `ref` and `reflen`).
- **`mf_hooks.fold`.** pcrec's fold TEXT template, with `@` as the byte
  operand.
  - Class EXPR: `F(@)` is an expression. Byte UCP uses
    `$_span_ci_fold(@)`, prefix-rendered by pcrec before it is handed
    over.
  - Class INPLACE: one or more statements mutating the lvalue `@`, e.g.
    `if (@ >= 'A' && @ <= 'Z') @ = (unsigned char)(@ + 32);`.
  - NULL means exact.
- **`mf_site.fold_kind`.** `MF_FOLD_NONE` / `MF_FOLD_EXPR` /
  `MF_FOLD_INPLACE`. pcrec STATES the shape; hooks stay opaque (the
  Q-G2-18 precedent). R1: a stated EXPR/INPLACE with a NULL `fold`
  declines. R2: NONE with `fold` stated is refused.
- **`mf_site.fold_map`.** `const uint8_t *`, 256 bytes, each byte's fold
  representative; NULL means identity. This is the relation as DATA
  (D146: "pcrec's proven facts"). pcrec derives it from
  `pcrec_enc_span_fold(e, ucp)` (enc.c:201), which already returns the
  relation the caseless compare folds by. It is what lets G2 check the
  rendered text, and what a later SIMD row would need (survey.md:720's
  `& 0xDF`). See Q-R8-4.
- **Reused hooks:** `s`, `n` (read limit), `lo` (= `at`), `result`
  (= `i`), `result_decl` (= `size_t `), `on_miss`, `indent`.
- **`empty`:** `reflen == 0` is EQUAL. It reads nothing and runs nothing,
  as `MF_EMPTY_NOP` (STMT).
- **policy:** `MF_P_INLOOP` (D91 budget 2: the compare runs at every VM
  backreference step).

**Read limits (rule 2, stated for the generated space).** The text reads
`s` only in [lo, n) and `ref` only in [0, reflen). It never forms
`s + lo` or reads `s` when `lo >= n`, so `s` may be NULL when `n == 0`.
It never reads `ref` when `reflen == 0`. It writes nothing but `result`
and its own locals. `ref` may ALIAS `s`: a backreference passes
`s + start`, and its span may even overlap the window. No `restrict` and
no non-aliasing assumption is allowed.

**Precondition:** `lo <= n`. The VM always passes `scan_position <=
subject_length`.

**Locals:** the kit's form may declare its own temps (`x`, `y` today).
Their names must not collide with the hook texts, and all of those are
the seam's parameter names.

### 3.2 G2: what a blinded (D27) author needs, in contract terms only

1. **Oracle.** k, as defined above, computed by a plain byte loop over a
   generated fold map. Equality iff k == reflen. On a mismatch, the value
   `on_miss` reads equals k. On equality, `on_miss` never runs.
2. **Generated space.**
   - n from 0 to well past any block width (cover ±1 around 8, 16, 32,
     64 and 128);
   - `lo` in [0, n];
   - `reflen` in [0, n − lo + 3], so subject exhaustion is reached;
   - the mismatch at every j, and none;
   - ref placement: a separate buffer, inside `s` before `lo`, exactly
     `s + lo`, and overlapping the window;
   - NULL `s` with n == 0 and reflen == 0, and NULL `ref` with
     reflen == 0.
3. **Fold maps.**
   - identity;
   - ASCII-52 (A-Z ↔ a-z);
   - Latin-1 representatives;
   - a random idempotent map;
   - a random NON-idempotent, non-injective map (the contract compares
     `map(a) == map(b)`, nothing more);
   - each with both EXPR and INPLACE hook spellings that implement the
     map. In each fixture the hook text and `fold_map` must agree.
4. **Read bounds** under guard pages: the subject ending at a page end
   with exactly n bytes, and `ref` likewise.
5. **Refusals and declines.**
   - `reverse` = 1;
   - any handoff other than the new one;
   - `on_miss_leaves` 0;
   - `on_miss` of class LOOP_EXIT or BRACED, if the kit rules JUMP only:
     the kit opens a loop around it, the M4 LOOP_EXIT precedent;
   - EXPR/INPLACE with no `fold`;
   - NONE with `fold` stated;
   - `nterm` != 1, or REF mixed with SET/RUN;
   - EXPR/FUNC form if only STMT is served;
   - `MF_SITE_ABI` + 1.
6. **Rows:** check (b) reaches every new row at least once; FLOOR_ROWS
   rises in run_g2.sh.

## 4. The overlap check (D153)

- **Refactor B, B3** (lane decfbB3 @ 69ab9650, 7 commits ahead of main).
  - It touches `src/core/compile.c` (+379/−513), `src/core/CLAUDE.md`,
    `src/opt/select_engine.c` (a 4-line comment at 915-920), and tests
    (fallback table, prefilter collapse, resource, mech S253/S259/S633,
    new S646-S651).
  - **No file in M7's edit set.** M7 does not touch `compile.c`. It only
    relies on the finishing-pass ordering at compile.c:2731, which B3
    keeps (see the note below).
- **B4** (dec_fallback.md:705; edit table 629-634). It touches
  `select_engine.c` 855-886 (the admission), the `emit_vm.c` 9443-9541
  `--emit-ir` chain, and the emit-ir-auto stream (a hard gate).
  - **Disjoint:** M7 leaves `emit_vm.c` untouched, since the call sites in
    `vm_bref`/`vm_var` do not change.
- **B5** (dec_fallback.md:706). It touches `esel_of` (select_engine.c
  960-994), the PFLW ternary and `size_term_why` (compile.c), and
  `VM_PREFILTER_WHY` (emit_vm.c:11264).
  - **Disjoint.**
- **Same-file, different-function:** `src/gen/emit_dfa.c`. B reads
  `fit.chosen`/`fit.prefilter` there (dec_fallback.md:601); M7 edits
  `emit_residual_defs` (3245-3258). Expect a clean textual merge. Run
  `git merge` alone, as the house rule says.
- **Worktrees** (`git -C <wt>`):
  - decfbB0, decfbB2, decfbdes, decfbrev2, g2u, m4, r4h: 0 commits ahead
    of main, no dirt in the edit set;
  - decfbB3: as above.
  - **No unmerged branch in the repo touches `src/enc/`, `emit_vm.c`,
    `emit_dfa.c`, `memfn_sites*`, `memfn_stamps.c`, `memfn/{include,src}`
    or the manifest, ceiling or vocab files** (scanned with
    `for-each-ref`).
- **plan.md rows on `src/enc/`.**
  - [VAR] (started; no live lane or worktree);
  - [UCP] U3 (chartered, queued behind [UTF-VALID]);
  - [ENC-MODEL] (not started);
  - [K50-DD12AI-MANIFEST] (not started; it reads emitted artifacts, which
    zero movers leaves unchanged).
  - None is in flight.
- **VERDICT: DISJOINT.** One sequencing note:
  - The identity gate's `--ref` must be M7's own merge-base.
  - If B3 or B4 merges to main before M7's slot, merge main into
    `lane/memfn-m7` first and re-take the ref. B4 moves the
    emit-ir-auto/stderr streams by design, so a stale ref would read B's
    movers as M7's.
- **Ids.**
  - S666-S675: free on main, on every worktree and on every branch tree
    (`ls-tree` grep: no file).
  - They are reserved to the kit in wake.md:10 and requests.md:225.
  - S652-S665 are B3's unused block; do not borrow them.

## 5. Checks and gates

### 5.1 C17 (`tests/memfn/site_manifest_check.py`, `make test-memfn-manifest`)

**It already reads `src/enc/`.**
- `SCAN_DIRS = ('src/gen', 'src/enc')` (line 44, `[rev4.6]` for N7). It
  applies `search_vocab.tsv` to every C string literal inside a
  file-scope definition, with adjacent literals joined and emitter
  comments removed (`c17_lex.py`).
- The vocabulary line the loop needs ALREADY EXISTS: class
  `span-compare`, id `span-index`, regex `s\[at \+ i\]`. It matches
  `defs_bref`, `defs_bref_ci` (`x = s[at + i];`), `defs_bref_ci_ucp` and
  `u8_defs_bref`.
- So does `span-decode` (`\$_decode\(s,`), which matches
  `u8_defs_bref_ci`.

**The manifest N7 change.**
- Today:
  `N7  defs_bref,defs_bref_ci,defs_bref_ci_ucp,u8_defs_bref,u8_defs_bref_ci  MF_VOCAB bump (...)  loop  M7  pending`.
- Under Q-R8-1 (a):
  - N7 becomes `delegated`. Its emitters are the describer and the use
    point, e.g. `span_site,emit_residual_defs`. Its companions are
    `defs_bref,defs_bref_ci,defs_bref_ci_ucp,u8_defs_bref` (an existence
    check only). Op is `MISMATCH/ON_DIFF`, budget loop.
  - New row `N7U  u8_defs_bref_ci  MF_VOCAB bump (per-character decode
    compare)  loop  M7b  pending`.
  - C17_ROW_FLOOR 13 → 14.
- Rule 3 then holds: the backend constants no longer spell `s[at + i]`,
  because the kit does.
- Rule 4 holds for N7U: it still spells `span-decode`.

**C12.**
- Delete `src/enc/enc_byte.c span-index 3` and `src/enc/enc_utf8.c
  span-index 1` from `c12_ceilings.tsv`.
- C12_CEIL_ROWS_FLOOR 5 → 3. The `enc_utf8.c span-decode 1` row stays
  until N7U.

### 5.2 C10 and the rest

- `run_deleg_sites.sh:28` `D91_LOOP` gains N7, citing D91's budget-2
  reading. The new (op, handoff, kinds) must pass `mf_vocab_has`.
- The new kit rows need their `rows.tsv` and census entries.

### 5.3 The rider: `"memchr"` in `src/gen/memfn_stamps.c` `libc_names[]` (line 47)

**Confirmed dead.**
- A grep for a quoted `memchr` in `src/`, `cli/` and `lib/` finds no
  emitted call text.
- The only hits are:
  - registry prose (axes_dump.c, limits.def, emit_dfa.c `.desc`
    strings);
  - row tokens (`"first-memchr-bounded"`);
  - comment text (`emit_dfa.c:5950`, inside `// ...`, which
    `scan_libc_calls` skips).
- Every artifact `memchr(` is kit-rendered, and the kit notes it itself
  (pffind.c, ofsskip.c, precheck.c). C12's memchr ceiling has been 0
  outside the kit since M4.

**Retire or re-aim S513?**
- Deleting the entry removes S513's anchor line. **Recommendation:
  RE-AIM** S513 to a name pcrec still spells, `strlen` (the `[VAR]`
  resolver; `probes/byte_var.c` stamps `RX_MEMFN_LIBC
  "memchr,memcmp,strlen"`).
  - Reach: `a${v}b` → `strlen` in MEMFN_LIBC.
  - Only if the C11 quick arm's population reaches a `${v}` artifact
    (verify by a hand plant).
  - Otherwise RETIRE it, with the equivalence record (the s513tri triage:
    `worktrees/memfn-slot/slot11/S513_triage.md`). See Q-R8-7.

**Collateral:** S517 (`memcmp` dropped) has THE SAME `SAB_BEFORE` line,
`    "memchr", "memcmp", ...`. It must be re-anchored in the same commit.
The triage expects S517 to be an equivalent mutant as well, unless the
quick sample reaches a `${v}` artifact, so re-measure it.

## 6. Sabotage

### 6.1 Rows whose anchors the edit set moves

These get solo mech and must stay DETECTED (S513 excepted).

| row | file | anchor | effect of M7 |
|---|---|---|---|
| S116 | enc_byte.c | `"        if (x >= 'A' && x <= 'Z') x = (unsigned char)(x + 32);\n"` | **moves.** The fold line becomes the INPLACE template (`@` spelling). Re-anchor; same intent ('z' stops folding); suites brefdiff + harness (`fold_agreement_check.c` calls the shipped entry) |
| S394 | enc_utf8.c | `u8_defs_bref_ci_doc, u8_defs_bref_ci,` / `PCREC_ENCE_DECODE, false },` | **moves only if** `PcrecEncEntry` gains a column and the second line changes (missing-field-initializers forces every row to spell it). Avoidable (Q-R8-3) |
| S513 | memfn_stamps.c:47 | the `"memchr", "memcmp", ...` line | **removed** by the rider: re-aim or retire (§5.3) |
| S517 | memfn_stamps.c:47 | the same line | **moves**: re-anchor, re-measure |

**Unmoved, but their detection runs through the migrated compare.**
Recommended as a confidence set in the slot's mech: S106, S109, S271,
S273, S590 (emit_vm.c call sites); S591, S-U2, S-U3 (fold.c);
S68 (memfn/src/pffind.c, codegen).

**Other `src/enc/` rows** (S229, S233, S340, S390, S391, S409, S410,
S412, S-U5, S-U6, S-U9) keep their text anchors. Run
`scripts/m6read_check_sab_anchors.py` and re-derive the start_table
anchor map.

### 6.2 Proposed new rows (S666-S675)

The ids were grepped free (§4). The recommended minimum set is S666,
S667, S669, S670, S671 and S673.

| id | plant | expected detector |
|---|---|---|
| S666 | kit row: the subject-bound test `at + i >= n \|\|` dropped | memfnarms (pin), G2; harness/brefdiff likely (reads past n). MEASURE |
| S667 | kit row: loop bound `i <= reflen` (compares `ref[reflen]`) | memfnarms; harness (spurious mismatches) |
| S668 | kit row: EXPR fold applied to the subject operand only | brefdiff (`fold_agreement_ucp_check`), harness caseless_ucp.rxt |
| S669 | kit row: INPLACE fold pasted for `x` only | brefdiff (`fold_agreement_check`), harness caseless.rxt |
| S670 | kit row: the subject-exhaustion exit falls out of the loop instead of pasting `on_miss` (`(ab)\1` on "aba" then reads as equal) | harness, brefdiff |
| S671 | kit row: `result` is k+1 when `on_miss` runs | memfnarms, G2. **Answer-neutral** (work charge only): the harness is expected UNDETECTED. Needs the new arm pin, M4's S617 precedent |
| S672 | pcrec describer: states `MF_FOLD_NONE` for a caseless entry | harness, brefdiff |
| S673 | backend re-spells the loop (`s[at + i]` returns to `defs_bref`) while N7 is delegated | memfnmanifest (C17 rule 3), memfnforms (C12, ceiling row gone). S524's analogue |
| S674 | `memfn_sites.def` N7 row's budget is `DELEG_SCAN` | memfndeleg (C10) |
| S675 | kit `vocab[]` loses `{MISMATCH, ON_DIFF, REF}` | memfndeleg (C10), harness (every backreference artifact refused) |

## 7. Identity-gate reach (zero movers)

**The sweep.**
- Command: `scripts/emit_sweep.py --ref <M7 merge-base>`, judged by
  `docs/design/memfn/probes/lxrun/memfn_r4c_gate.py --zero-dumps`.
- BOTH bases are mandatory (`--bases byte,utf8`, the default).
- The streams compile `-o -` (self-contained), so the decls are in the
  compared `.c`.
- **Add arms:**
  - `--extra -fcomments` on both bases. The `defs_doc`/`decls_doc` prose
    is only emitted then, and the site token sits between the doc and
    the body.
  - `--extra --ucp` on the byte base (the UCP entry; also reached by
    `(*UCP)` corpus lines such as tests/backrefs/caseless_ucp.rxt).
- **Print a reach count** per (base, stream): the patterns whose
  artifact contains `_span_match`. Require > 0 for each of `span_match`
  and `span_match_caseless`, and for byte `span_ci_fold_pairs` (UCP).
  A gate that never reaches the site proves nothing (MECH-REACH).

**Witness tier** (M4's `zm.sh` shape: `.c`, `.h`, rc and stderr compared
against a pre-edit binary copy):
- **byte:**
  - `(a+)\1`, `(a*)\1`, `^(a)\1$`;
  - `(?<n>a)\k<n>`, `(?J)(?<n>a)|(?<n>b)\k<n>`;
  - `(?i)(ab)\1`, `(?i)(k)\1`;
  - `(a)(?i:(b)\2)\1` (both entries in one artifact);
  - `(?<=a)(b)\1x` and `(?i)(?<=a)(b)\1x` (DD12a(ii)'s witnesses: span
    + back_step);
  - `a${v}b`, `(?i)a${v}b`;
  - `--ucp (?i)(ab)\1`, `(*UCP)(?i)(.)\1`.
- **utf8 (`-e utf8`):**
  - `(a+)\1`, `(é+)\1`, `^(k)\1$`;
  - `(?i)(ab)\1` (the walk is untouched under (a), but its artifact also
    carries the exact entry when mixed);
  - `(a)(?i:(b)\2)\1`;
  - `a${v}b`, `(?i)a${v}b` (with `$_var_valid`).
- **Cross-cuts:**
  - each of the above at `-fcomments`;
  - `-p foo` (prefix substitution reaches the hook text);
  - `--emit-main`;
  - `--engine=vm` explicitly;
  - split output (`-o x.c`, which writes `.h`).
- **Answer-level controls that stay green with zero movers:**
  - `run_backref_diff.sh` §9 / §9b / UCP (the fold agreement checks call
    the SHIPPED entries);
  - `run_encoding_checks.sh` DD12a(i)/(ii) (they excise the residual
    bodies from the artifacts).

**The rider** is covered by the same sweep: every artifact carries
`MEMFN_LIBC`, so a missed memchr note would show as a mover.

## 8. Risks and open questions for the kit manager

- **Q-R8-1. Does utf8's caseless decode walk (`u8_defs_bref_ci`) migrate
  in M7?**
  - (a) Split N7: N7 holds the byte-wise compares (four constants, three
    shapes) and goes delegated in M7. A new pending row N7U holds the
    walk, with its own later vocabulary step (a character-unit REF
    stream with a decode hook and a length-changing result).
  - (b) Migrate it in M7 too, with that larger vocabulary.
  - (c) Rule it outside the site definition.
  - **Recommend (a).** It keeps M7 at the F8 the design names
    (requirements.md:143), avoids designing a decode vocabulary blind,
    and keeps C17 honest (no third state, the row stays pending).
    (c) re-opens Q54's ruled definition.
  - Note that R-8 said "caseless variant included": (a) includes the byte
    caseless compares (ASCII and UCP). Main should confirm that reading.
- **Q-R8-2. Boundary.** **Recommend the loop body** (STMT inside the
  backend's exported function), for the reasons in §2.3. FUNC is
  rejected.
- **Q-R8-3. The seam mechanism.**
  - **Recommend:**
    - a site TOKEN in the backend's `defs` text where the loop was;
    - the backend's per-entry site data (fold kind, fold template,
      `on_miss` text): a `PcrecEncEntry` column, or a `PcrecEnc` field
      keyed by entry id, which avoids touching every row and S394;
    - a renderer callback that the gen layer passes into
      `pcrec_enc_emit_defs`, since `src/enc` cannot include gen or call
      the kit's per-art state.
  - This partially revisits enc.h:30-34 ("WHY TEXT AND NOT A CALLBACK"),
    so it IS a D58 revisit-clause event.
    - Record it in enc.h and src/enc/CLAUDE.md, in the same commit.
    - Propose a D58 addendum to main; decisions.md is main's to write.
  - The third-encoding recipe stays within `src/enc/`.
  - Parameter names (`s`, `n`, `ref`, `reflen`, `at`): recommend ONE
    spelling in enc.h, not per-backend data. DD12a(ii) already proves the
    signatures identical.
- **Q-R8-4. The fold, as text and as data.** **Recommend both:**
  - the backend's text template (zero movers; the encoding owns the
    spelling);
  - `fold_map` derived from `pcrec_enc_span_fold` (the relation the kit
    and G2 can reason about).
  - The risk is two spellings of one fact (D122). G2 ties the text to the
    map, and the existing `fold_agreement*_check.c` already tie the
    shipped text to fold.c, so there is a mechanism between them.
  - Text-only is the alternative. A future SIMD caseless row would then
    need another bump.
- **Q-R8-5. The handoff.** **Recommend a new `MF_H_ON_DIFF`** (result
  written, then `on_miss`, which may read it). Reusing ON_MISS or ASSIGN
  would overload rules memfn.h states in writing (lines 107-118).
  Either way `on_miss` must be JUMP and may be pasted more than once.
- **Q-R8-6. Bump packaging.** **Recommend one kit-only PREP commit:**
  `MF_VOCAB` 3 and `MF_SITE_ABI` 7 (fields appended last), the row(s),
  fixtures and gate cases, with zero pcrec bytes (M4 Phase A precedent).
  Then IMPLEMENT (describer + shadow comparator, M4's I1 shape, over both
  bases), then REPLACE. G2 is red until the blinded lane lands, as at M4.
  Sequence it before the slot's `make test`.
- **Q-R8-7. S513.** **Recommend re-aim to `strlen`**, with a by-hand
  plant proving the quick C11 arm reaches a `${v}` artifact. Otherwise
  retire with the record. Re-anchor S517 in the same commit and
  re-measure it.
- **Q-R8-8. The gate's ref under refactor B's merges.** **Recommend:**
  ref = M7's merge-base. If main moves, merge main first and then re-take
  the ref (§4).
- **Q-R8-9. Generic-row totality.** The generic scalar row must render
  MISMATCH (§14.6). **Recommend:** the generic row renders exactly
  today's EXACT/EXPR shape, plus one named row for the INPLACE shape. Or
  the generic row serves both; the kit's call. Either way each gets a
  pinned target file (the R4h `pins/r4h_target/` precedent), checked byte
  for byte against the pre-edit text above.
- **Q-R8-10. D91 and the spec.** **Recommend:**
  - N7 is budget 2 (loop) in C10's literal, citing D91 (the compare runs
    per VM backreference step);
  - no `docs/spec/` hunk, since nothing a caller observes changes;
  - the kit lane says so explicitly in its report.

**Other risks:**
1. `-Wmissing-field-initializers` (`-Wextra`) on the positional entry
   rows. A new `PcrecEncEntry` column touches every row of both
   backends.
2. `pcrec_enc_emit_text` has only `$`. A new `@` token in `defs` text
   needs its own "no other `@`" rule, as `advance` has (enc.c:244-260).
3. The kit's text must stay ASCII and C99 portable. It now sits inside
   an exported, `-fPIC`-able function: no `static` helpers declared
   inside, and nothing new needs a flush (the run-compare helper
   flush is not involved).
4. G2 needs a guard-page harness for the `ref` operand. Today's driver
   guards only the subject.

## Charter checklist

| item | section |
|---|---|
| 1. Edit set (file:line, both encodings, every backend, emitted text) | §1.1-§1.3; probes/ |
| 2. Boundary under D58/DD-12, byte for byte; loop vs function | §2.1-§2.3 |
| 3. Vocabulary gap: op/fields/classes, MF_VOCAB bump, G2 needs | §3.1-§3.2 |
| 4. Overlap check (B3/B4/B5, worktrees, plan rows); verdict | §4 |
| 5. C17 scan + vocabulary line; manifest N7; rider + S513 | §5.1-§5.3 |
| 6. Sabotage: moved anchors; new rows S666-S675 (ids grepped free) | §6.1-§6.2 |
| 7. Identity-gate witnesses, both encodings | §7 |
| 8. Risks and Q-R8-n with recommendations | §8 |
