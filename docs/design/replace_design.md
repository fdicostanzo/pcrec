# Search/replace — the variable layer over a ruled substitution design

**Status: PROPOSED, over a RULED baseline.** Design only; nothing under
`src/`, `cli/`, `lib/` or `tests/` was touched. **REVISION 2 (lane subst,
2026-10-21): §R2 below supersedes the COUPLING this note and
`subst_template_design.md` assumed (one function per pattern and template)
with Frank's independent substitution element over the find-all iterator.
Read §R2 first; superseded passages below are marked in place.** **REVISION 3
(lane substr3, 2026-10-22): §R3 applies the D6 panel r1
(`../dev/reviews/2026-10-22-r1-subst-design.md`, three critics, every finding
accepted). Read §R3 first, then §R2; §R2 passages R3 replaces carry an `[R3: ...]`
marker.** **REVISION 4 (lane substr4, 2026-10-22): §R4 applies Frank's interface
rework and rulings R5-R8 (the template compiled independently of the regex,
an optional reference map, pieces instead of bytes, no glue, module
`subst-extended` designed in, one support unit). Read §R4 first; the §R3 and §R2
passages it replaces carry an `[R4: ...]` marker. Its spec draft is
`subst_api_r4_draft.md`, which replaces `docs/spec/subst_api.md` at build
time.** **REVISION 4a (lane substr4b, 2026-10-22): §R4.15 applies the R4
light panel (`../dev/reviews/2026-10-22-r2-subst-r4-panel.md`, two critics);
the §R4 passages it changed are edited in place.** **REVISION 4b (lane substr4c,
2026-10-22): §R4.16 applies rulings R9-R11 (pieces are `unsigned char`, the
support unit is emitted, one replace-all function in the support unit); each
change is marked `[R4b]`, and the interface has no open question.** **REVISION 4c
(lane substb2, 2026-10-22): §R4.17 applies ruling R13 (the use-case fit
review's G1, F0, G6 and G10 adopted; G2-names and G4 filed as candidates);
each change is marked `[R4c]`. The build of the interface follows on this
branch.**

## REVISION 4 — the interface rework: an independent template, an optional map, pieces, one support unit (lane substr4, 2026-10-22) — READ THIS FIRST

**Status: PROPOSED, design only, NO BUILD GO.** Nothing under `src/`, `cli/`,
`lib/` or `tests/` was touched, and `docs/spec/subst_api.md` is unchanged. The
contract this revision proposes is drafted in full as `subst_api_r4_draft.md`
(the numbered spec form), which replaces `docs/spec/subst_api.md` at build
time. Cites below of the form `draft §N¶K` are to that draft. It applies the
lane brief's rulings and the later entries R5-R8 of
`docs/dev/lanes/subst_rulings.md`; R8 was the last applied in revision 4; revision 4b applies R9-R11 (§R4.16). The probes behind
§R4.13 are `subst_measurements/r4_*`, run against libpcre2 10.46 on the Linux
dev box.

**Status at build (review 2026-10-24 r1 subst, IFACE-8/IFACE-9; lane
substr1fix).** BUILT on lane/substland. The contract is
`docs/spec/subst_api.md`; `subst_api_r4_draft.md` is retired to a pointer.
Every `draft §N¶K` below reads as the spec's same number, and where this
revision's text and the spec disagree, the spec is what ships. Names: every
shared name moved to the `pcrec_subst_*` family at build (`rx_subst_piece`
is `pcrec_subst_piece`, `rx_subst_replace_all` is `pcrec_subst_replace_all`,
`struct rx_subst_info` is `struct pcrec_subst_info`, `RX_SUBST_*` is
`PCREC_SUBST_*`; spec §1¶2); the `rx_subst_*` spellings below are the
design-time names. Sentences the build overtook are marked `[superseded]`.

**The goals, ranked** (IFACE-8: the order the rulings applied them in; a
later goal yields to an earlier one where they conflict).

| rank | goal | ruling | where it yielded |
|---|---|---|---|
| 1 | the template is compiled INDEPENDENTLY of the regex; numbers join through an optional map | R4.0 item 1 | -- |
| 2 | NO ALLOCATION: pieces, bytes only for case forcing, into caller scratch sized first | R4.0 item 5 | goal 4: replace-all's batch is a fixed stack array, so an rx with more than `PCREC_SUBST_BATCH_PAIRS` (256) capture pairs is refused rather than served (IFACE-4's open half, plan [SUBST-CLEANUP]) |
| 3 | ANSWERS equal `pcre2_substitute`'s, every difference a spec §9 row | D26 | never yielded: goals 1-2 cost coverage (a refusal), never a different answer |
| 4 | one-call convenience: replace-all, the setup wrapper | R11, R13 (G1, F0) | amended R4.0 item 4: replace-all is generic over `rx_nextnfn`, not a regex-specific fused form |
| 5 | a support unit only when needed; a plain template is one `.c` | R7, R8, R13 (G6) | -- |
| 6 | shared names cannot collide with an artifact's | review r1 IFACE-5/6 | -- |

**Premise test (the brief's).** Today the binding is MANDATORY. The element
and the glue both take an `rx_subst_binding`, and only `pcrec_subst_bind` can
make one BOUND. The element returns `PCREC_SUBST_MISMATCH` for any binding
that is not (`subst_api.md` §4¶4), and the glue takes nothing else
(`subst_api.md` §6¶1). So a template cannot render a match until it has been
bound to one rx's record, and the bind refuses any number or name that rx does
not have. That is the coupling Frank's rulings remove.

**STOP RULE: did not fire.** Every form, the extended module included, is
rendered without allocation.

- **No bytes written.** A form whose bytes already exist is a piece pointing
  at them:
  - the artifact's constant data: literals, `$$`, every escape, and
    conditional default text;
  - the subject: references and gaps;
  - a caller variable: `${!name}`.
- **Bytes written into the caller's scratch.** Only case forcing writes
  bytes. It writes them into the caller's scratch, sized exactly before any
  write, and a too-small scratch returns NOSPACE with the size needed
  (§R4.13).
- **Renderer segments** (`rx_renderfn`) still have no producer. If one ever
  exists, it writes scratch the same way.

### R4.0 Frank's rulings (2026-10-22)

From the lane brief:

1. **Setup is INDEPENDENT of the regex.** The template and the regex are
   compiled independently, so their group numbers need not correspond. The
   render takes an OPTIONAL lookup table from the template's references to the
   regex's groups, and NULL means the numbers match (identity). "Users of C
   can do glue work."
2. **A table has three possible sources:**
   - (A) the caller fills it by hand, reading the template's published
     reference list;
   - (B) there is no table, because the numbers match (1:1 use);
   - (C) one universal helper cross-references the regex's group table with
     the template's BY NAME, for sets of regexes and templates that share a
     group-name vocabulary.
3. **Missing-group handling is optional**: a run-time choice between blank
   and an error (its default was open; R6 below rules it).
4. **NO fused "substitute with this regex" one-call form.** The user can write
   it, and there is no substitution-specific optimization work. `[amended by
   R11/R13: one replace-all function, generic over rx_nextnfn, and a tested
   setup wrapper recipe; the goal table above, rank 4]`
5. **The render RETURNS AN ARRAY OF PIECES `{const char *ptr, size_t len}`.**
   `[amended by R9: the pointer is const unsigned char *]`
   - There is no string handling in pcrec, and the array fits other languages'
     string types. NO MALLOC.
   - Pieces point into the template's constant data, the subject, or the
     caller's variable values.
   - Byte-producing forms (case transforms) write into a CALLER-PROVIDED
     scratch buffer, and a too-small buffer returns NOSPACE with the size
     needed and nothing half-written.

From `subst_rulings.md`:

- **R5** (the manager, Frank's refinement; to be applied here):
  - (1) A lookup-table entry deliberately set to "no group" is INTENTIONAL: it
    always renders as an unset reference, never an error. The name helper
    takes an option for a name the regex does not have: refuse it, or mark
    the entry "no group".
  - (2) An unset group at match time is decided PER REFERENCE by the template,
    through PCRE2's extended forms (`${n:-text}`, `${n:+set:unset}`), with
    PCRE2's exact semantics measured on libpcre2 10.46. Rev 4 designs module
    `subst-extended` in, and maps each form onto pieces without malloc.
  - (3) For plain references, the manager leans towards BLANK by default with
    a strict flag.
- **R6** (Frank): "Plain `$n`/`${name}` on an unset group renders BLANK by
  default; a strict flag makes it an error. State the difference from PCRE2's
  default (PCRE2_ERROR_UNSET) in the spec."
- **R7** (Frank): "There are a number of universal functions like that one
  [flatten], and the xref helper, that should be part of a library or source
  the user may have. Then they are included once." Every regex-independent
  and template-independent helper lives in ONE support unit. The manager
  leans towards `pcrec --emit-support` as the vehicle. Each artifact carries
  only its data, its render and the shared types. The RX side is out of
  scope (a candidate only).
- **R8** (Frank): KEEP flatten in the support unit ("it will help with
  debugging"). `pcrec --emit-support` MUST WORK BY ITSELF: no pattern, no
  template and no other flag, writing to stdout or `-o FILE`. Specify it in
  the spec draft, with the cli.md hunk.

### R4.1 What changed against R3

| R3 piece | R4 | where |
|---|---|---|
| `pcrec_subst_bind`, mandatory, against one rx's record; `rx_subst_binding` | WITHDRAWN. The element takes an optional MAP, where NULL means identity. One check validates any map, and the rx-aware resolver survives as helper (C) | §R4.3, §R4.4; draft §3 |
| the NEEDED shape: named rows first, then numbered | the REFERENCE LIST, in first-appearance order across numbers and names (the map's index) | draft §3¶2 |
| `rx_shape_match` | `pcrec_subst_map_names` (helper C), in the support unit: the same walk, writing SLOTS and runs, with an option to mark a missing reference `RX_SUBST_NOGROUP` (R5.1) | draft §3¶13-¶16 |
| no way to say "no group" | `RX_SUBST_NOGROUP` in a map: always unset, never an error (R5.1) | draft §3¶6 |
| the element writes bytes through a cursor | the element writes PIECES, `k * P` per call | §R4.5; draft §4 |
| the glue `pcrec_subst` (limit, sizing pass, retry over a FRESH copy, `PCREC_SUBST_PAIRS`) | WITHDRAWN (rulings 4 and 5): recipes in draft §6 | §R4.7 |
| NOSPACE: a byte capacity, and the retry matches again | NOSPACE: pieces (`k * P`) or scratch bytes, decided before any write; nothing is searched twice | §R4.5 |
| `--unset=empty\|error`, a compile-time axis with a stamp | the run-time flag `RX_SUBST_STRICT`, default BLANK (R6); `--unset=` and `<S>_SUBST_UNSET` go | §R4.6 |
| `subst-extended` refused | DESIGNED IN (R5.2): conditionals, escapes, `\1`-`\9`, case forcing, as libpcre2 10.46 measures them; selected with `--features subst-extended` | §R4.13; draft §2¶7-¶14 |
| `seg_user`, `<S>_NSEGS`, `PCREC_SUBST_RENDER` | gone; −13 is reserved | §R4.5 |
| every helper a `static inline` in every subst header (about 250 lines each) | ONE support unit, `pcrec --emit-support`; headers carry types and declarations only (R7, R8) | §R4.14; draft §10 |
| bind's encoding refusal | helper (C) only | draft §2¶5 |
| §R3.13's timing cell | RETIRED (ruling 4) | §R4.11 |
| Q-F2, Q-F3 | CLOSED by ruling 4 and the recipes | §R4.9 |

Unchanged from R3: the core template language and its parser, the batch
element, BADSPAN (§R3.6), the same-build rule (§R3.8, now also covering the
support unit), `${!name}` resolved once per find-all (§R3.7, through
`rx_subst_ctx_init`'s new signature), `rx_group_run` (it moves into the support
unit), the header guards (§R3.11), and the answer differences of §R3.10 rows
9 and 11.

### R4.2 The interface on one page

`[superseded at build: the check and the setup are static inline; replace-all
(R11, §R4.16) is in the support unit; every name is the pcrec_subst_* family
(see the status note at the head of this revision). The spec's §1-§10 are the
interface.]`

```c
/* in every subst header (the types block) */
typedef struct rx_subst_piece { const unsigned char *p; size_t len; } rx_subst_piece;
typedef struct rx_subst_run   { int first, count; } rx_subst_run;
typedef struct rx_subst_map   { const int *slot; size_t nslot;
                                const rx_subst_run *run; size_t nrun; } rx_subst_map;
typedef struct rx_subst_out   { rx_subst_piece *pc; size_t cap, n;
                                unsigned char *scratch; size_t scap, sn;
                                size_t prev, need, sneed; } rx_subst_out;
#define RX_SUBST_GAPS    0x1u      /* a gap piece before each match */
#define RX_SUBST_STRICT  0x2u      /* unset group or variable: an error (default: blank) */
#define RX_SUBST_NOGROUP (-1)      /* a map entry: "no group", always unset, never an error */

/* + in the types block, static, one copy per translation unit (§R4.15, panel r2) */
static int pcrec_subst_check(const struct rx_subst_info *t, const rx_subst_map *map,
                             const struct rx_info *rx, unsigned flags, int *bad_ref);
static int rx_subst_ctx_init(rx_ctx *ctx, const rx_iter *it, const struct rx_info *rx,
                             const struct rx_subst_info *t, const rx_subst_map *map,
                             rx_var *vres, unsigned flags, int *bad_ref);  /* runs the check */

/* per template */
int dmy_render(const rx_ctx *ctx, const rx_subst_map *map,      /* map NULL: identity */
               ptrdiff_t (*caps)[2], size_t k, unsigned flags, rx_subst_out *o);

/* the support unit (pcrec --emit-support): only for helper or case-forcing users */
int    pcrec_subst_map_names(const struct rx_subst_info *t, const struct rx_info *rx,
                             unsigned opts, int *slot, size_t nslot,
                             rx_subst_run *run, size_t nrun,
                             rx_subst_map *map, int *bad_ref, size_t *nabsent);  /* helper (C) */
int    rx_group_run(const struct rx_info *rx, const char *name, const char *ref, int *first);
size_t rx_subst_flatten(const rx_subst_piece *pc, size_t n,
                        unsigned char *restrict out, size_t cap);
extern const unsigned long long pcrec_support_id;               /* the unit's content id */
/* + the UTF-8 case mapping the case regions call */
```

The template publishes these stamps: `<S>_NREFS` (references a map covers,
`max(1, n)`), `<S>_PIECES` (pieces per match, the gap included, at least 1),
`<S>_MAXNUM` and `<S>_NVREFS`. With these a caller sizes every array
statically: `rx_subst_piece pc[64 * DMY_PIECES]` holds a 64-match batch.

### R4.3 The map's entry: why a slot list with optional runs, not "(first group, count)"

The brief proposed a table entry of `(first group, count)`, with count 1
normally, so that duplicate-name groups are expressible. The intent is right:
a duplicated name needs several candidates, and the first one that
participated wins (match_api.md §5.4¶6). Without that rule, crit1's
`(?J)(?<n>a)|(?<n>b)` cell renders `x[a][]y` where PCRE2 renders `x[a][b]y`.
But the pair cannot index either of the two things a "group" could mean:

- **Over group NUMBERS**, a run is not contiguous. In `(?J)(?<n>a)(x)(?<n>b)`,
  `n` is groups 1 and 3, so `{1, 2}` would name groups 1 and 2, which is
  wrong.
- **Over ROWS of `rx->groups`**, as R3's binding used it, unnamed groups have
  no row. A hand-filler mapping `$1` to the rx's group 3 has nothing to point
  at, and the render would need the rx's record per call. That is the
  coupling ruling 1 removes.

**R4's entry is a SLOT LIST with optional runs over it** (draft §3¶4-¶5).
There are three levels, and at each one NULL means "the simple case":

| map | reference r reads | who uses it |
|---|---|---|
| `NULL` | slot `k` for `$k`; a name is refused | (B): 1:1 use |
| `{slot, nslot, NULL, 0}` | `slot[r]`, one entry | (A): a hand-filler's renumbering; the common hand case is ONE `int` array |
| `{slot, nslot, run, nrun}` | the first participating slot of `slot[run[r].first, +count)` | (C), and any hand-filler who wants duplicates |

**The plain-int alternative** (`const int *map`, one slot per reference) is
the middle row. It is the simplest thing a hand-filler writes, and R4 keeps it
as that row. On its own it cannot express a duplicated name, and duplicated
names are what helper (C) must serve. So the runs are a second, optional
array, not a replacement. Indexing slots rather than rows keeps the map
independent of `rx_group_entry`'s layout and of `rx_info`. That is why the
pcre2-ovector unlock (§R4.11) can use the same map.

**"No group" is an entry value** (R5.1): `RX_SUBST_NOGROUP` (-1) in
`slot[]`. It never participates, so the reference is always unset:
- plain, it renders empty, even under `RX_SUBST_STRICT`;
- `${n:-text}` renders `text`;
- `${n:+set:unset}` renders `unset`.

That is the deliberate "this regex has no such group" that ruling R5.1
describes (draft §3¶6). Helper (C)'s option `RX_SUBST_MAP_ABSENT` writes that
value for a reference the rx lacks, instead of refusing it (draft §3¶14).
With that option, one template serves a SET of regexes that each carry only
some of its names (ruling 2C's case).

**`$0` and the whole-subject forms are not in the map.** `$0`, `$&`,
`` $` ``, `$'` and `$_` are defined by the match span and the subject. A
caller who wants a reference to read the whole match maps it to slot 0.

**Named references with no map (B) are refused, never guessed**: the check
returns `MISSING_REF` naming the reference.

### R4.4 One validation

**[R4a: rewritten by panel r2, findings C2-2, C1-5 and C2-4, and open
question 3 adopted (§R4.15).]**

**One function, `pcrec_subst_check`, validates a template, a map and an rx
together, whatever the map's source** (draft §3¶8-¶12). It is a `static`
function in the subst types block, under its shared guard, so a translation
unit holds one copy however many subst headers it includes. It refuses:

- a record of another abi, or of another support unit's text (the content
  id, §R4.14);
- an unknown flag;
- an rx of another encoding than the record's, when the record's is not -1
  (C1-5: a `\U$1` template compiled under the default `-e byte` and used with
  a utf8 rx rendered `STRAßE` silently where PCRE2 renders `STRAẞE`);
- NO map on a composed rx (`ncaps > ngroups + 1`): the no-map form is for a
  template and pattern written together, and on a composed rx `$k` above
  `ngroups` would reach a delivered group by number (C2-4);
- a map whose arrays are shorter than the reference list;
- an entry that is neither `RX_SUBST_NOGROUP` nor a slot in `[0, ncaps)`;
- a run that is empty or reaches past `nslot`;
- with no map, a number `>= ncaps` or any name.

It reads `ncaps`, `ngroups` and `encoding` from the rx's record (C2-4: a
bare `ncaps` was an unchecked caller constant). It is `O(nrefs + nslot)` and
never allocates. Helper (C) ends by calling it.

**It runs ONCE, at context setup** (`rx_subst_ctx_init`, now also `static`
in the types block and taking the rx's record and the map). That makes a bad
template, map or rx observable on a subject with NO match (C2-2: with the
check inside the element, a zero-match find-all never called it, so whether
an error showed depended on the data).

**What the per-render check becomes: a memory-safety re-assert** (draft
§4¶10). Per call the element tests, in `O(1)`, the flag bits, the vars, the
scratch pointer and the map's two lengths; the run walk, which reads every
slot it uses anyway, adds one range compare per slot read. Nothing a valid
setup admits can fail it; it fires only on a context filled by hand without
the check, or a map changed after it, and then it is a `MISMATCH`, never an
out-of-bounds read. The full-check pass per call (R4's "check per call, no
token") is gone, and with it R4's unmeasured per-match cost in a k = 1 loop.
No token was needed: the setup is the object that was always there (`ctx`).

**Linking (open question 3, ADOPTED as the critic answered it).** Because the
check and the setup are `static` in the types block, a program that uses a
template with no case forcing and no helper needs NO support unit: a plain
template is one `.c` again and `-o -` stays self-contained (APPROACH.md's "no
dependency on pcrec itself"). Only helper users (`map_names`, `rx_group_run`,
`flatten`) and case-forcing templates (which call the case mapping) link the
support unit, and a case-forcing template without one fails to LINK. The
rule is still written once: the check's text is emitted by one emitter
function into the one shared block. (Lane note: the critic listed
`ctx_init` among the optional helpers; it is inline here because the recipes'
setup call is what makes "a plain template is one `.c`" true in practice,
and it is the call that runs the check.)

### R4.5 Pieces

- **Fixed stride.** A call writes exactly `k * P` pieces, where `P =
  <S>_PIECES` with gaps and `P - 1` without (draft §4¶5). Empty pieces (an
  empty gap, an unset group, a conditional's padding) are written with
  `len` 0, never dropped. A conditional takes the larger of its two texts'
  piece counts, and the shorter text is padded. The case region is one piece
  (§R4.13). The consequences:
  - NOSPACE in pieces is static, `k * P`, and is decided before any match is
    rendered;
  - match `i`'s pieces sit at a known offset, so per-match output (a JSON
    line, a templated `grep -o`) needs no index array;
  - adjacent literals merge (`x\ny$$` is one piece), so `P` counts items,
    not bytes.
- **`p` is never NULL.** A zero-length piece points at a valid address that
  must not be read. Rust's `from_raw_parts` and some FFI layers reject NULL
  even at length 0, and the flatten's `memcpy` stays out of the `NULL, 0`
  undefined case. [R4a, C1-9] The sentinel is NAMED: `rx_subst_empty`, a
  constant byte in the types block, used wherever the source would be NULL or
  undefined (a `(NULL, 0)` subject, match_api.md §3.1¶8; an unset group's
  `{-1, -1}`; a variable with `p == NULL`). The `k * P`, `n + k * P` and
  scratch sums are overflow-checked: overflow is NOSPACE with `need`/`sneed`
  `SIZE_MAX` (draft §4¶14).
- **`const unsigned char *`, not ruling 5's `const char *`**, because the
  subject (`rx_iter.s`) and `rx_var.p` are `unsigned char`. A piece is then
  exactly the `{p, len}` half of `rx_var`. This is a question for Frank
  (§R4.9).
- **"Nothing half-written"** (draft §4¶10, ¶21):
  - NOSPACE (pieces or scratch) is decided before anything is written, and
    the counts do not move;
  - an error at match `i` (BADSPAN, or UNSET under the strict flag) commits
    the whole matches `0 .. i-1` and nothing of match `i`.
- **No match is ever searched twice.** R3's NOSPACE retry re-ran the
  find-all (§R3.10 row 7). With pieces:
  - a byte buffer that is too small is the caller's flatten, which grows the
    buffer and flattens the same batch again (draft §6¶4);
  - a scratch NOSPACE re-renders the same `caps` with a bigger scratch
    (draft §6¶7), from `n == 0` and `sn == 0`, because growing scratch
    invalidates every piece that points into it [R4a, C1-7].
- **[R4a, C1-6] The scratch sizing pass stops at the first failing match.**
  It validates each match's spans and unset references as it sizes, and
  stops before the first that fails, so `sneed` covers only the prefix §4¶21
  would commit. Before this, `x(?=(?1))|(b\K)` on `"xb"` (span `[2,1)`) under
  `\U$0` computed `1 − 2` as a size, and NOSPACE asked for nearly `SIZE_MAX`.

  This difference from PCRE2 is now in pcrec's favour (draft §9 row 7).

### R4.6 Unset: blank by default, a strict flag (R6, RULED)

- **Plain references.** A group that did not participate renders an empty
  piece. `RX_SUBST_STRICT` makes it `PCREC_SUBST_UNSET` at that match (draft
  §4¶23). This holds for `$n`, `${name}`, `\1`-`\9` and references inside
  conditional text.
- **The conditionals' own tests never error.** Choosing a text is what they
  do.
- **`RX_SUBST_NOGROUP` never errors** (R5.1).
- **`${!name}` follows the same flag**, with `PCREC_ERR_UNSET_VAR` before
  any output.
- **The spec states the difference from PCRE2 plainly** (draft §4¶23, §9 row
  5): libpcre2's default is `PCRE2_ERROR_UNSET` (−55) unless
  `SUBSTITUTE_UNSET_EMPTY`. That covers conditional text too: libpcre2 gives
  −55 for `${1:-$2}` with both groups unset, and pcrec renders it blank.

D38 Q3's generation axis therefore becomes a call flag. It costs one
predictable branch per referenced group per match, which is unmeasured and of
the run walk's class. `--unset=` leaves the CLI, and with it the
`<S>_SUBST_UNSET` stamp and the record's `unset` field.

### R4.7 How it interlocks with the iterators

The support unit ships no loop (rulings 4 and 5). The reference recipes are
in draft §6, each a few lines, and `tests/subst/` runs each one at build. They
share one rule: **the caller's loop owns "how many" and "where the bytes go";
the element owns spans, gaps and references.** The two core shapes:

```c
/* per match: <prefix>_next, gap pieces included, written to a stream */
while (rx_next(&it, caps)) {
    o.n = 0; o.sn = 0;
    if ((rc = dmy_render(&ctx, map, caps, 1, flags | RX_SUBST_GAPS, &o)) < 0)
        return rc;                                     /* a prefix: no tail */
    for (size_t i = 0; i < o.n; i++) fwrite(pc[i].p, 1, pc[i].len, f);
}
if (it.rc < 0) return it.rc;                           /* a give-up: no tail */
if (n > o.prev) fwrite(s + o.prev, 1, n - o.prev, f);  /* the tail: o.prev is the last end */

/* batch: <prefix>_next_n, 64 matches per element call */
do {
    got = rx_next_n(&it, caps, 64);
    o.n = 0; o.sn = 0;
    if ((rc = dmy_render(&ctx, map, caps, got, flags | RX_SUBST_GAPS, &o)) < 0) return rc;
    consume(pc, o.n);                                  /* writev, rx_subst_flatten, a rope ... */
} while (got == 64);
if (it.rc < 0) return it.rc;
```

[R4a, C1-7 + C2-1 + C2-8] R4's recipes broke out of the loop on `rc < 0` and
then wrote the tail, and never read `it.rc`, so an error, a NOSPACE or a
give-up produced output that looked complete with the later matches left
unreplaced; §6¶4 also reset `n` but not `sn`, and its flatten computed
`w + need` before testing `need == SIZE_MAX`. The draft's §6 now states one
ERROR RULE (a negative return from the setup, the element or the iterator
means the output is a prefix: return the code, write no tail), and every
recipe follows it. `tests/subst/` runs each recipe with a forced give-up, a
forced `BADSPAN` and a forced NOSPACE. The `(const ptrdiff_t (*)[2])` cast is
gone: the element's `caps` is spelled as the iterators' (C2-3).

[R4b, R11] The recipes stay for every destination that is not one caller
buffer (a `FILE *`, a scatter list, a rope). For the one buffer, the support
unit holds `rx_subst_replace_all` (draft §10¶6-¶10): the batch recipe's loop,
error rule and sizing written once.

- **The gap pieces.** With `RX_SUBST_GAPS`, piece 0 of each match is
  `s[prev, start)`, and the tail `s[o.prev, n)` is the caller's last write.
  Without the flag there are no gap pieces and no tail: replacements only. A
  caller who wants the gaps skipped (an edit list) can also keep the flag and
  step over every `P`-th piece.
- **`RX_FOREACH`** gives one match per body, so it calls the element with
  `k = 1` (draft §6¶5). That is one element call per match, the caller's
  choice. `<prefix>_next_n` is the batch path.
- **Limits and resumption are free.** R3's glue could not resume after its
  `limit` (§R3.4), and it capped `next_n` so as not to over-fetch. A caller's
  loop counts its own matches, and with `_next` or `_next_n` the iterator
  stays resumable (match_api.md §3.8). Only `RX_FOREACH`'s early-exit rule
  (match_api.md §3.8.2¶4) still applies, to its own users.
- **The variables.** `rx_subst_ctx_init` resolves `${!name}` by name from the
  iterator's variables once per find-all. A caller with its own variables
  fills `ctx.vars` in the template's `vrefs` order. That is the same
  identity, hand or by-name choice the group map makes.

### R4.8 In-place and streaming (§R2.6), as far as pieces change them

- **Pieces are borrowed** (draft §7¶1). Nothing in a batch is read until the
  caller consumes the pieces, so §R2.6's in-place write rule gains one term.
  A write must land below every byte the next search reads (`lo −
  back-reach`), AND below the lowest source of every piece not yet consumed.
  With `k = 1` and immediate consumption, that is §R2.6's rule as written.
  In-place stays a contract with no build.
- **Streaming gets cheaper, not harder.** A window glue flushes the pieces of
  the matches before its holdback point and then slides. That flush is a
  `writev` of pointers into the window, with no copy. §R2.6's holdback is
  unchanged, and so is its rule that `$_`, `` $` `` and `$'` refuse streaming.
  A case region's piece is in scratch, so it outlives the window.
- **The flatten** declares `out` `restrict` against every piece (draft
  §10¶5). Flattening into the subject is the in-place case above.

### R4.9 Questions for Frank (plain words)

Ruled since the brief, and applied: unset renders blank by default with a
strict flag (R6); flatten is kept, in the support unit (R8); the helpers live
once in a support unit written by `pcrec --emit-support`, which works on its
own (R7, R8).

[R4b] Rulings R9-R11 closed the first two questions and the replace-all
question (below). The interface now has NO open question.

Closed, each as ruled:

1. **[CLOSED, R9: "agree unsigned".]** Pieces are `const unsigned char *`,
   the type of the subject everywhere in the API (draft §4¶3, §9 row 2).
2. **[CLOSED, R10: "agree".]** The support unit is written by
   `pcrec --emit-support`, not shipped. Frank's Makefile concern (a re-emit
   must not force recompiles) is the plan row `[CLI-OUTKEEP]`: `-o` writes
   only when the output's bytes change. That row is its own change; the
   subst build does not implement it (draft §10¶2).

3. **[ANSWERED by panel r2's adoption, §R4.4.]** Only helper users and
   case-forcing templates link the support file. The check and the context
   setup are small `static` functions in the shared types block, one copy per
   translation unit, written by one emitter function.
4. **[WIDENED by panel r2, C1-3.]** Every PCRE2 escape whose meaning depends
   on the pattern's group count: `\` followed by `1`-`9` and at least one
   more digit. Measured: `\10` is group 10 or byte 0x08, `\101` is group 101
   or `A`, `\77` is group 77 or `?`, `\81` is group 81 or an unknown-group
   error, `\400` is group 400 or an error.
   - Leaning: refuse them all at template compile, pointing at `${10}`,
     `\o{10}` or `\010`. `\1` to `\9` alone are always group references on
     any pattern (probed: their meaning never depends on the group count;
     a missing group is an unknown group, as `$8` is), so they stay
     accepted, as do `\0dd` and `\o{}`.
5. **[CLOSED, R11: "3. yes".]** The "substitute everything into my buffer"
   function returns, ONCE, as `rx_subst_replace_all` in the support unit, over
   pieces and over the existing matcher types (§R4.16).

Manager-level, decided here (say if any is wrong):

- the stride is fixed, and empty and padding pieces are kept;
- `p` is never NULL;
- the matches before a failing one are committed;
- the check runs once at context setup; the element re-asserts memory
  safety only (§R4.4, panel r2);
- the no-map form is refused on a composed rx (panel r2, C2-4);
- the reference list is in first-appearance order;
- the extended module is selected with `--features subst-extended`;
- the case region runs from the first case escape to the template's end
  (§R4.13);
- PCRE2's case-forcing combinations are reproduced as measured, oddities
  included (D26 exact tier).

### R4.10 What the existing build keeps and drops

Sizes are lines in `lane/subst` at c09063494. "Rewrite" means the file's job
stays and its text is mostly new.

**The template parser.** `src/parse/subst_template.c` (296 lines) is KEPT.
That covers the core language, the greedy rules, names, the UTF check and
every refusal. It changes in four ways:

- the reference list goes into first-appearance order;
- adjacent `SUBST_LIT` items merge, and `npieces` is counted;
- **NEW:** the `subst-extended` grammar of draft §2¶7-¶14 (conditionals,
  escapes, `\1`-`\9`, the `\NN` refusal, case escapes) is added. The
  conditionals reuse `src/core/varexp.c`, which already parses and refuses
  `${n:-w}` (`subst_template.c`'s header), so its operator forms become
  accepted under the module instead of refused. That is about 250 lines.
- **[R4a, family (b)] The escapes reuse the pattern parser's decoder**, not a
  second copy: `esc_char_value` in `src/parse/parse.c` (the control escapes,
  `\x`/`\x{}` with its encoding range check, and the digit branch it returns
  as "backref/octal"), the registry rows' definitions for `\o{}`, `\cX` and
  `\N{U+}` (`src/parse/registry.c`), and `pcrec_clsport_octal` for `\0dd`.
  The `\NN` refusal is that digit branch's "needs the group count" case. The
  template parser calls them through a narrow entry; how that entry is cut
  (the decoder takes a `Ctx`) is a build question.

`SubstTmpl` (`src/core/internal.h`) changes: `nnamed`/`nneeds` become
`nrefs`, and `npieces` and the case-region start are added. Items gain the
kinds `COND_UNSET`, `COND_SET` and `CASE_REGION`.

**The needs and shape records.** `needs` becomes `refs` (the same
`rx_group_entry` rows), and `nruns` becomes `nrefs`. These go: `nsegs`,
`unset`, `<S>_NSEGS` and `<S>_SUBST_UNSET`. These are added: `npieces`,
`uses`, `<S>_PIECES`, and `subst-extended` in `<S>_SUBST_MODULES`.

**bind becomes the check (inline, in the types block) plus helper (C) (in the
support unit)** [R4a]. Gone:
`pcrec_subst_bind`, `rx_subst_binding` and `PCREC_SUBST_BOUND`.
`rx_shape_match` becomes `pcrec_subst_map_names`, the same loop writing slots
and runs, plus the `RX_SUBST_MAP_ABSENT` option. It keeps the negative-number
refusal and the run-slot range test. `pcrec_subst_check` is new, at about 25
lines. `rx_group_run` is unchanged and moves into the support unit.

**The element: byte copy becomes pieces.** In `src/gen/emit_subst.c`:

- the binding's identity tests become the support check's call, the vars
  test and the room test;
- each item's `rx_subst_put` becomes one piece store;
- the gap becomes a piece;
- the run walk reads the map's slots, and stays in the render as a private
  `static` (it is hot, per match);
- **NEW:** conditionals (one participation test, then one text's pieces and
  the padding) and the case region (a sizing pass, then a writing pass into
  scratch, both over the same item interpreter).

The element emitter grows from about 70 lines to about 200.

**The NOSPACE logic.** `rx_subst_cur`, `rx_subst_put`, saturation, `fits` and
`PCREC_SUBST_PAIRS` all go. NOSPACE becomes one compare for pieces and the
case region's sizing pass for scratch. The flatten holds the only remaining
saturation, in about 12 lines.

**The glue.** `pcrec_subst` is WITHDRAWN (about 40 lines). Its batch doubling
was a copy of `RX_FOREACH`'s (the substfix residual), so that duplication
goes with it.

**The support unit (NEW, R7 and R8).** `src/gen/emit_subst.c` gains
`pcrec_emit_support`, which writes the file of draft §10: the shared blocks,
the declarations, and under `PCREC_SUPPORT_IMPLEMENTATION` helper (C),
`rx_group_run`, the flatten, the UTF-8 case mapping and the content id
[R4a: the check and `rx_subst_ctx_init` moved to the types block, §R4.4].
That is about 280 lines of emitted text, most of it moved from today's
block. The case mapping table is a new GENERATED table from existing
vendored data (§R4.12). §R4.14 says what leaves every header.

**The CLI.** In `cli/main.c`:

- `--unset=` goes, with its two refusals and its help line;
- `--features subst-extended` becomes accepted on a subst compile, and only
  that module;
- `--emit-support [-o FILE]` is new, a standalone mode like the other emit
  commands.

That is about 60 lines.

**The spec.** `docs/spec/subst_api.md` is replaced by the draft. Each in-tree
citation of it (§1¶2, §1¶3, §2¶1, §2¶5, §3¶3, §5¶2, §5 and §9) exists in the
draft with the topic its citer means. The spec has never been on main, so its
other paragraphs are renumbered freely. `cli.md` gets the hunk in §R4.14.
match_api.md §3.8¶9a (it names `rx_subst_ctx_init`) and §4's reservation of
−11..−16 stand.

**The tests and the driver.** The answers stay, because they are
`pcre2_substitute`'s and the recipes reproduce its global loop.

- `tests/subst/cells.tsv` (75 lines): about 10 `bind:` expectations become
  `check:`, and the `UNSET` column becomes the strict flag. NEW cells: one
  per §R4.13 transcript row, oracle `pcre2_substitute` with `EXTENDED`; the
  NOGROUP and MAP_ABSENT arms; a scratch NOSPACE re-render. [R4a] Also:
  the case state table's witness rows (draft §2¶13) as oracle rows; the
  `\[1-9]\d` refusals and the accepted `\1`-`\9`/`\0dd`/`\o{}`; the
  encoding refusal and the composed-rx no-map refusal at setup, on a
  zero-match subject; every draft §6 recipe under a forced give-up, a
  forced `BADSPAN` and a forced NOSPACE (no tail written, code returned);
  `\Uß` and `\LȺ` sized by the bound; pcrec-only ill-formed-UTF-8 case
  cells (draft §2¶14a), never sent to libpcre2 (it crashes, U23).
  [R4b] `rx_subst_replace_all` (draft §10¶6-¶10): a forced give-up, a forced
  `BADSPAN`, a forced `UNSET` and a forced NOSPACE of the output buffer and
  of the scratch (the code returned, `*len` as §10¶8-¶9 say, no tail, no
  partial output counted as success); a zero-match subject; a buffer of
  exactly the needed size and one a byte short; and an EQUIVALENCE test that
  runs it beside the §6¶4 buffer recipe over the whole corpus and asserts the
  same bytes, the same length and the same code (draft §10¶10).
- `subst_drv.c` (401 lines): rewritten around the draft §6 recipes, through
  flatten, in the three map modes, linking an emitted support unit.

**The D27 corpus.** What still applies:

- the eleven differential families (`corpus/d_*.tsv`, about 1,500 cases)
  apply unchanged. Only `lib/diff_driver.c` (141 lines, rewritten to the
  batch recipe) and `run_diff.py`'s unset column (now the strict flag) move;
- the API drivers (`api/t_*.c`, about 950 lines) test the OLD promises, so
  most are rewritten or retired. `t_bind` and `t_shape` go to the check and
  helper (C), `t_glue` is retired into the recipes, `t_element` moves to
  pieces, and `t_vars`, `t_threads`, `t_iter` and `t_utf` adapt;
- `cli/cli.sh`: its `--unset` cases become refused-option cases.

**A fresh D27 round is OWED** for the new surfaces: the map's modes and
NOGROUP, the check, pieces and stride, NOSPACE before any write,
commit-on-error, scratch, the extended module, and `--emit-support`. It goes
to a writer blinded to `src/` and given only the draft (D27).

**Sabotage rows S1346-S1382 (37):**

- **KEPT, re-anchored to the piece form (25):** S1346, S1347, S1348, S1352,
  S1354, S1357, S1359, S1360, S1361, S1362, S1365, S1366, S1369, S1370,
  S1371, S1372, S1373, S1374, S1375, S1376, S1377, S1379, S1380 (its witness
  loses `--unset=`), S1381, S1382. S1354 and S1375 now plant the flag's
  default.
- **RE-AIMED (6):**
  - S1351 becomes "the check accepts a slot `>= ncaps`";
  - S1353 becomes the room compare;
  - S1356 becomes the check's abi test;
  - S1358 becomes helper (C)'s `k <= ngroups`;
  - S1368 and S1378 move to helper (C).
- **RETIRED with the glue (6):** S1349, S1350 (its saturation returns as a
  flatten row), S1355, S1363, S1364 and S1367.
- **NEW (about 15):**
  - the core interface (about 7): a name accepted with no map, a run past
    `nslot`, the gap left out of the stride, a NULL `p`, NOSPACE committing
    part of a batch, an error committing match `i`, flatten writing on a
    short buffer;
  - the extended module (about 8): `:-` firing on a set-but-empty group,
    padding dropped, the case region's state reset at a conditional's end,
    `\NN` accepted (a three-digit form included), scratch sized one byte
    short, NOGROUP erroring under strict, a pending one-shot kept when a
    region is already set (the state table's first row), an ill-formed byte
    case-mapped;
  - the panel r2 surfaces (about 3): the setup's encoding compare dropped,
    the composed-rx no-map refusal dropped, the sizing pass not stopping at a
    failing match;
  - the support unit (about 3): its names without the abi suffix,
    `--emit-support` needing an argument, and the content id not compared.

  Ids come at build, from a range the manager names.

**Rough size of the change:**

- product code: about 900 lines touched, about 600 of them new (the
  extended module and the support emitter);
- the case mapping table: new generated data;
- spec: a full replacement, about 600 lines, plus cli.md's hunk;
- tests: about 1,600 lines rewritten, plus the extended cells;
- mech: 25 kept, 6 re-aimed, 6 retired, about 15 new;
- one D27 round.

Two build lanes is the honest size: one for the interface, R4's core, and one
for `subst-extended` and the case data, which can follow.

### R4.11 Lenses: siblings, and what pieces unlock

**SIBLING-OF-A-FAMILY.**

- **Pieces and capture pairs.** A piece is a capture pair RESOLVED: `{s +
  caps[k][0], caps[k][1] - caps[k][0]}`, generalized to the artifact's
  constants, the caller's variables and scratch. It is exactly the `{p, len}`
  value half of `rx_var` (match_api.md §2¶1). So these are one family with two
  spellings: offsets where everything is in the subject (caps), and pointers
  where it is not (pieces). If a third consumer wants `{p, len}`, the shared
  block could hoist an `rx_bytes` type that `rx_var` then holds. That is an rx
  abi event: a candidate for [IFACE-PUSH], not here. POSIX `struct iovec` is a
  third sibling, with the same shape and different types.
- **Is the by-name helper the same as `rx_group_run`?** No. It is a LOOP over
  `rx_group_run`, plus D61 for numbered references. `rx_group_run` stays the
  single name-to-run primitive (§R3.2). It is the same thing R3 built as
  `rx_shape_match`, with its output changed from rows to slots and with the
  NOGROUP option added.
- **The map is the per-match consumer family's binding** (§R3.12). The
  extract-to-struct member, when it comes, takes the same map. The helper
  serves it unchanged if it reads any `rx_group_entry` reference list rather
  than a template record. So at build the helper takes `(refs, nrefs)`, and
  the template signature is a one-line wrapper. That is cheap, and it is the
  general form.
- **The support unit and the rx shared block.** Every rx header still carries
  `RX_FOREACH`'s machinery (`rx_foreach_begin`/`_pull`) and the iterator's
  setters as `static inline` text. The same R7 treatment would move the
  non-inline-critical parts into the same support unit. That is a CANDIDATE
  only (R7 puts it out of scope), and moving it is an rx abi event.
  `RX_FOREACH`'s per-batch pull is hot and probably stays inline.
- **`rx_ctx`'s function family** (draft §4¶27) keeps its three rows. The
  `rx_substfn` row's binding column changes to "the map, optional".

**UNLOCKS, each with its trigger:**

| unlock | why pieces enable it | trigger |
|---|---|---|
| zero-copy output: `writev` straight from the piece array | pieces are iovec-shaped | a user writing substitutions to a file or socket |
| bindings for other languages with no pcrec string type: Rust `&[u8]` slices, Python `bytes.join`, Go `[]byte` | `p` is never NULL and nothing is owned | the first binding |
| editors, ropes and patch lists: a gap piece is "unchanged", a template piece is "new" | the fixed stride says which is which | an editor or diff use |
| NOSPACE without re-matching (draft §9 row 7) | the pieces of a batch stay valid | built in |
| one template over a SET of regexes that share names only partly | helper (C)'s `RX_SUBST_MAP_ABSENT` plus `${name:-...}` | a user with several patterns and one output format |
| the pcre2-ovector adapter (§R3.12's named member) | the map indexes SLOTS, not `rx_info` rows; the adapter converts `PCRE2_SIZE` pairs to `ptrdiff_t` | the bench wants templated output from both engines |
| the shape-contract version (§R3.8's narrower alternative) | the element no longer reads `rx_info`, only `rx_ctx`, caps and the map | unchanged: a prebuilt template library or an [ART-MGR] catalog |

**§R3.13's timing cell is RETIRED.** Its only consequence was building the
fused form, and ruling 4 rules that out. Nothing measures the per-call check,
the run-time strict branch or the case region's two passes. All three are
labelled UNMEASURED, with triggers in §R4.4 and §R4.6. The case region's
trigger is a user's hot `\U` template.

### R4.12 The standing questions (`docs/design/CLAUDE.md`)

1. **Measurement regime: relevant only to answers.** R4 produces no timing.
   The §R4.13 probes are ANSWERS from libpcre2 10.46 (bytes, codes and
   counts), which hold on any box. The moved costs are labelled unmeasured,
   with triggers.
2. **Independent control: relevant.**
   - The answers' oracle stays `pcre2_substitute`, a different implementation
     of the whole job, now with `SUBSTITUTE_EXTENDED` for the module.
   - The recipes in `tests/subst/` are caller code, written by the test
     author and not shipped.
   - **The case mapping table is NOT a new data set** [R4a, family (a),
     verified against the tree]. PCRE2's observed rule is "the other member of
     the code point's simple-fold class, chosen by general category" (`ß` →
     `ẞ`, U+01C6 → U+01C4). The fold classes are the orbits
     `third_party/ucd-16.0.0/generate.py` already builds from the vendored
     `CaseFolding.txt` for `src/core/fold_tables.inc`, and the general
     category is the `UnicodeData.txt` column the same script already reads.
     UnicodeData's own uppercase column would be wrong here: `00DF` has none,
     so `ß` would stay `ß`. The case table is therefore a third output of that
     ONE generator, a sibling of `fold_tables.inc` and of the emitted
     `src/enc/utf8_fold_pairs.inc` (today's one derived table that reaches
     generated code), and nothing new is vendored. The generator also asserts
     the bound's property (no ASCII/non-ASCII crossing; growth at most 3/2).
     Its control must not share that source: libpcre2's own answer for every
     code point under `\U`, `\L`, `\u` and `\l`, collected by RUNNING
     libpcre2 into `oracle_store/libpcre2-10.46/` as a new question kind
     beside `membership.tsv`, which is that store's charter. NEW-DATASET lens:
     no new data source; the product's derivation stays in `third_party/`,
     the control's answers in `oracle_store/`.
   - The populations are counted by the existing runners. A per-code-point
     check counts 0x110000 minus the surrogates.
   - A fresh D27 writer covers the interface promises.
   - Each new sabotage row's witness reach is owed at build ([MECH-REACH]).
3. **What moves when regenerated: relevant.**
   - No rx artifact moves, because the types block lives only in subst
     headers and the support unit (§R3.8).
   - Every subst artifact's text changes, which is no event, because none has
     ever been on main.
   - After landing, a change to the types block or to the support unit's text
     is an abi event (D76/D94). A UCD regeneration that moves the case table
     moves the support unit's bytes, so it is one too, with readers found by
     grep.

### R4.13 Module `subst-extended`, measured (R5.2)

**Probes:** `subst_measurements/r4_probe_ext*.py`, transcript
`subst_measurements/r4_transcript.txt`. These are libpcre2 10.46 2025-08-27
`pcre2_substitute` calls with `GLOBAL | OVERFLOW_LENGTH | EXTENDED`, through
ctypes and the D27 corpus's `ref_pcre2.py`: 97 cells, answers only. The draft
§2¶7-¶14 states each rule. What the probes established:

| rule | witness (template on pattern, subject → output) |
|---|---|
| `${n:-t}` fires on UNSET only; a set-empty group renders itself | `[${1:-D}]` on `(a?)b`, `b ab` → `[] [a]`; on `(a)?b` → `[D] [a]` |
| `${n:+s:u}`: set (empty included) picks `s`; `${n:+s}` with no `u` renders nothing when unset | `[${1:+S:N}]` on `(a?)b` → `[S] [S]`; `[${1:+S}]` on `(a)?b` → `[] [S]` |
| no-colon and other operators are refused | `${1-D}`, `${1+S:N}` → −58; `${1:=D}`, `${1:?D}` → −59 |
| text is a template: nesting, escapes, `$$` | `[${1:-${2:-z}}]` → `[z] [c] [a]`; `[${1:-x$$y}]` → `[x$y]`; `[${1:-a\:b\}c}]` → `[a:b}c]` |
| `:` is literal in `:-` text, and the first unescaped `:` splits `:+` text; `}` closes | `[${1:-a:b}]` → `[a:b]`; `[${1:+a}b:c}]` → `[b:c}] [ab:c}]` |
| an unset reference INSIDE text is −55 unless `UNSET_EMPTY` | `[${1:-$2}]` → −55 (pcrec: blank by default, R6) |
| unknown group in a condition | `${9:-D}` → −49 (pcrec: `MISSING_REF` or NOGROUP) |
| escapes | `\n\t\x41\x{42}\101\\\$` → LF TAB `A B A \ $` (on a pattern below 101 groups; pcrec refuses `\101`, panel r2 C1-3); `\a\e\f\r\0`; `\o{101}` → `A`; `\cA` → 0x01; `\x4` → 0x04; `\q` and a trailing `\` → −57 |
| UTF-only escapes | `\x{100}` and `\N{U+41}` → −57 without UTF; with UTF, U+0100 as UTF-8 and `A` |
| `\Q..\E` | `<\Qa$1\E>` → `<a$1>`; an unterminated `\Q` runs to the end at top level, and is −58 inside conditional text; inside text `\Q` protects `}` and `:` (`[${1:-\Qa}b\E}]` → `[a}b]`, `[${1:+a\Q:\Eb:c}]` → `[a:b]`) [R4a, C1-10] |
| `\1`-`\9` are groups on any pattern; every `\[1-9]\d+` depends on the pattern | `<\1>` → the group; `\8` on one group → −49 (as `$8`); `\10` → 0x08 below ten groups, group 10 with twelve; `\101` → `A` or group 101; `\77` → `?` or group 77; `\81` → −49 or group 81; `\400` → −57 [R4a, C1-3] |
| case forcing persists, applies to literals, and outlives a branch | `\U$1 x \L$2 Y\E z` → `HELLO X world y z`; `${2:-\Ux}y` → `XY`; `${1:+\U$1:x}y$1` → `BYB` |
| single-character combinations | `\u\Lab` → `Ab`; `\l\UAB` → `aB`; `\L\uAB` → `AB`; `\U\lab` → `ab`. [R4a, C1-1] R4's reading "`\L\u$1` acts as `\U`" was WRONG (its sources were all uppercase): `\u` ENDS the region, so `\L\uabc` → `Abc`, `\Ua\ubc` → `ABc`, `\u\U\Lab` → `ab`. The rule is the declared state table of draft §2¶13 |
| `\u` applies to the next character produced, even through a condition | `\u${2:-x}` → `X` |
| `\E` ends `\Q` first, and then case forcing | `\U\Qa$\E$1` → `A$B` |
| UTF mapping is single code point and may change length | `ß` → `ẞ` (2 → 3 bytes); U+01C6 → U+01C4 under `\U` and `\u`; `ı` unchanged under `\U`; U+212A and U+0130 unchanged under `\L`; a CONSTANT grows too (`\Uß`, `\U\x{df}` → `ẞ`; `\LȺ` → `ⱥ`, 2 → 3) [R4a, C1-4] |
| ill-formed UTF-8 under case forcing | libpcre2 10.46 SEGFAULTS (`\U$_`, pattern `b`, UTF + MATCH_INVALID_UTF, `"ab\xffc"`) or reads past the substring (`"abc\xc3"` → `\xc3\x80`); pcrec copies ill-formed bytes unchanged (draft §2¶14a, §9 row 19; `upstream_issues.md` U23) [R4a, C1-2] |
| byte mode changes ASCII only | `\U` on bytes 0xE0 0xC0 leaves them |
| `$*MARK` renders empty with no mark | pcrec keeps refusing it (no artifact reports a mark), draft §9 row 17 |
| `${!v}` is −35 | pcrec's own form (draft §9 row 18) |

**How each form maps onto pieces, with no malloc:**

- **Escapes, `\Q..\E` and every literal run** are constant bytes, merged into
  literal pieces.
- **A conditional** is one participation test (the map's run walk, the same
  as a plain reference), then the chosen text's pieces, padded to the
  larger text's count, so the stride stays fixed. A default text is literal
  pieces in the artifact's constant data, so no scratch is needed (R5.2's
  expectation, confirmed).
- **Case forcing cannot be resolved at compile time.** The state is the
  template's running state in OUTPUT order, and a branch can switch it on
  for everything after it (`${2:-\Ux}y`). So R4 makes ONE CASE REGION per
  template: from the first case escape, in template order, to the template's
  end. It is rendered into scratch as ONE piece per match, by the same item
  interpreter run twice:
  - a sizing pass, so that NOSPACE is decided before any write, with
    `sneed` exact;
  - then a writing pass that applies the case state dynamically.

  Everything before the region stays zero-copy. Bytes inside the region that
  end up unforced are copied unchanged, which costs bytes and never changes
  an answer.

  A tighter region (ending at a `\E` that every path reaches) is a later
  refinement with no trigger yet.
- **Scratch bound.** Under UTF-8 a single-code-point mapping grows a
  character from at most 2 bytes to 3 (ß → ẞ, ɐ → Ɐ, Ⱥ → ⱥ). [R4a, C1-4]
  R4's bound ("constant bytes plus 1.5 times the copied bytes") undercounted,
  because forced CONSTANTS grow as well: `\Uß` writes 3 bytes against a
  bound of 2. The bound is now 1.5 times EVERY byte that enters the region,
  constants included, rounded up (draft §4¶22). The alternative, a
  compile-time stamp of the constants' worst case, was not chosen: a
  constant's forced form depends on the run-time case state (a branch can
  switch `\U` on), so the stamp would itself be a worst case over states;
  it would add a stamp, an abi reader and a record field to save at most
  half the constant bytes of one region, which are few. The exact sizing
  pass still reports `sneed` exactly; the bound is only for a caller who
  wants never to see a scratch NOSPACE. Its truth for all of Unicode is a
  property of the derived table, asserted by the generator and checked by
  the per-code-point control (§R4.12). Ill-formed bytes count one each.
- **`\[1-9]\d+` refused** (§R4.9 question 4, widened by C1-3) and
  **`$*MARK` refused** are the two places where the extended module differs
  from PCRE2 in what it accepts. Both are stated in draft §9.

### R4.14 The support unit (R7, R8)

**What it is.** It is one file holding the larger functions that are
independent of both the regex and the template:

- `pcrec_subst_map_names` and `rx_group_run`;
- `rx_subst_flatten`;
- [R4b] `rx_subst_replace_all`, the one replace-all function (§R4.16);
- the UTF-8 case mapping;
- `pcrec_support_id`, its content id.

[R4a] `pcrec_subst_check` and `rx_subst_ctx_init` left it for the types
block (§R4.4, open question 3 adopted).

It also carries the rx shared block and the subst types block under their
guards (draft §10).

**The vehicle.** `pcrec --emit-support [-o FILE]` writes it.

- **On its own (R8).** It takes no pattern, template or other option, and
  anything else on the line is refused. It writes to stdout by default, or to
  FILE.
- **One file, with an implementation guard.** One translation unit of the
  program defines `PCREC_SUPPORT_IMPLEMENTATION` before including it. Every
  other unit includes it for the declarations, or does not include it at
  all, because each subst header already declares what it calls.
- **Deterministic.** Its text depends only on the pcrec build. [R4b] A
  Makefile that re-emits it would recompile its users every time; plan row
  `[CLI-OUTKEEP]` (`-o` writes only when the bytes change) is the cure, and
  the subst build does not implement it.
- **The alternative: a fixed file shipped in the pcrec tree** (for example
  `lib/pcrec_support.h`). It is simpler to find, but it can drift from the
  compiler a user runs, and it would be the first generated-code dependency
  pcrec did not emit. [R4b] R10 ruled the emitted file (§R4.9 question 2).

**Version safety.** Every external name is a macro over a name that carries
the abi (`rx_subst_flatten` → `rx_subst_flatten_v<abi>`). A subst artifact
and a support unit from different builds fail to LINK. The run-time abi
comparison in the check then covers only `dlopen`.

[R4a, C2-6] **The abi alone is not enough**: the unit carries the case table
and the flatten and helper logic, so a UCD update or a flatten fix changes
its behaviour under the same abi, and two units of one abi both define the
same names (a duplicate-symbol error, or with static archives a silent
pick). So the unit defines `pcrec_support_id`, a 64-bit hash of its own text
computed by the emitter, and a record whose template calls into the unit
holds `support = &pcrec_support_id` and `support_id` from its own build;
the check refuses a difference at setup (draft §10¶3). A record that calls
nothing there holds NULL and references no support symbol, which keeps the
plain template link-free. The unit's text is named as a READER of the abi
number (D76/D94): a change to its text is an abi event, and the identity
gate pins its bytes.

[R4a, C2-7] **`PCREC_SUPPORT_STATIC`** (draft §10¶3a) makes every definition
`static` for one translation unit, for a library and an application that
each want a private copy. And each subst header opens its stamps with
`#ifdef <PREFIX>_PIECES` / `#error`, so the documented case-only prefix
collision (`dmy` and `DMY` share `DMY_PIECES`) is caught at compile rather
than by reading §1¶3.

**What R7 deletes from the as-built block** (presented as the simplification
it is):

- **Almost every function body in every subst header.** Today each header
  carries about 250 lines of `static inline` code: `rx_subst_put`,
  `rx_subst_span`, `rx_subst_group`, `rx_subst_run_slot`, `rx_group_run`,
  `rx_shape_match`, `pcrec_subst_bind`, `rx_subst_ctx_init` and
  `pcrec_subst`. Some of them are withdrawn by §R4.1, and the rest move to
  the support unit, except two [R4a]: the check and `rx_subst_ctx_init` stay
  in the shared types block as `static` functions (about 45 lines, one copy
  per translation unit under the shared guard), so that a plain template
  needs no support unit. The per-match run walk stays in the artifact, as the
  render's own private code. A subst header becomes types, macros, the
  stamps, the two shared functions and two declarations.
- **The `rx_shape` spelling of the `subst-block` reservation** (cli.md
  §1.6¶2; review item MF2). Nothing is named `rx_shape*` any more.
- **What does NOT go, against the rulings file's expectation:**
  - The other reserved spellings stay. `rx_subst*`, `pcrec_subst*` and
    `rx_group*` are still the types', flags', and support functions' names,
    and a pattern prefix can still collide with them.
  - MF1's guard rule stays: each artifact still has its own header with its
    own declarations, and its guard must still differ from an rx header's of
    the same prefix.
  - What R7 does remove is the larger class behind both items: TWO HEADERS
    DEFINING THE SAME FUNCTION TEXT (a subst header and the support file, or
    two subst headers of different builds in one unit). After R7 a header
    defines no function, so the only same-name collisions left are types and
    macros. The shared guard and the abi `#error` already handle those.

**The `cli.md` hunk** (for the build; `docs/spec/cli.md` §1.19¶1 today
describes the subst compile with `--unset=`):

> `pcrec [-p PREFIX] [-e ENC] [--features subst-extended] -o OUT.c --subst
> TEMPLATE` (or `--subst-file FILE`) compiles a substitution template
> (the subst spec's §5). `--features` takes `subst-extended` and no other
> module there; every pattern-compile option is refused.

and a NEW subsection beside it, `### 1.20 --emit-support: the subst support
unit`, with its TOC row [R4a, family (e)]:

> `pcrec --emit-support [-o FILE]` writes the subst support unit (the subst
> spec's section 10) to stdout or FILE. It is the one emit command that
> takes no pattern (`--emit-main` §1.10, `--emit-ir` §2.10 and
> `--emit-facts` §2.11 all take one): no pattern, template, query or other
> option, and it refuses any. Its output depends only on the pcrec build.

cli.md has no emit-mode TABLE today (the panel's "emit-mode table" does not
exist; the emit commands are separate subsections), so the new mode is a
subsection that names its three siblings, not a table row. (The hunk lands
in the same commit as the draft, which is when the new section 10 exists to
be cited by number.)

**The RX side (out of scope, a CANDIDATE only).** The same treatment applies
to the rx shared block's inline helpers: the iterator setters, and the
`rx_foreach_*` machinery behind `RX_FOREACH`. It would make the support unit
the one home for all of pcrec's shared caller-side code. The cost is an rx
abi event and every rx caller linking the unit. The trigger is a second
module whose shared code is not hot.

### R4.15 The R4 light panel applied (panel r2, lane substr4b, 2026-10-22)

Two critics reviewed §R4 and the draft: C1 on PCRE2 semantics (probed against
libpcre2-8 10.46 through ctypes) and C2 on the interface. The record, with
each finding's text, its disposition and where it landed, is
`../dev/reviews/2026-10-22-r2-subst-r4-panel.md`. Every finding was ADOPTED
by the manager; one was narrowed by the evidence (C1-3's single digits).

| id | what changed | where |
|---|---|---|
| C1-1 | case forcing is a declared 4-rule state table; R4's "until `\E` or the other one" and "`\L\u$1` acts as `\U`" were wrong; witnesses are oracle rows | draft §2¶13; §R4.13; §R4.10 tests |
| C1-2 | ill-formed bytes under case forcing are copied unchanged, 1:1 in sizing; kept out of the differential; libpcre2 segfault filed | draft §2¶14a, §9 row 19; `upstream_issues.md` U23 |
| C1-3 | every `\[1-9]\d+` refused; `\1`-`\9` alone stay (probed: never group-count dependent); `\0dd` and `\o{}` accepted | draft §2¶10, §2¶12, §9 row 16; §R4.9 Q4; §R4.13 |
| C1-4 | the scratch bound is 1.5× every byte entering the region; the stamp alternative is argued against | draft §4¶22; §R4.13 |
| C1-5, C2-4 | the setup and the check take the rx's record; encodings compared; no map on a composed rx refused | draft §2¶5, §3¶3, §3¶8-¶12, §7¶3-¶4; §R4.4 |
| C2-2 | the check runs once at setup (observable on zero matches); the per-render check becomes a memory-safety re-assert | draft §4¶10-¶14; §R4.4 |
| C1-6 | the sizing pass stops at the first failing match; NOSPACE covers only the committable prefix | draft §4¶14, §4¶21; §R4.5 |
| C1-7, C2-1, C2-8 | every recipe has a correct error exit (no tail on any negative code, `it.rc` read, `sn` reset with `n`, scratch grown only from `n == 0`, overflow tested first); forced-failure recipe tests | draft §4¶4, §6; §R4.5, §R4.7, §R4.10 |
| C1-8 | no-overlap rule for scratch and the piece array | draft §7¶1a |
| C1-9 | the sentinel `rx_subst_empty`; overflow checks on `k * P`, `n + k * P` and the scratch sums | draft §4¶9, §4¶14; §R4.5 |
| C1-10 | `\Q` inside conditional text; an open `\Q` there refused; NOGROUP-under-STRICT vs PCRE2's −55 | draft §2¶9, §2¶10, §9 row 20 |
| C2-3 | `caps` spelled `ptrdiff_t (*caps)[2]` exactly as `_next`/`_next_n`/`RX_FOREACH`; the recipes lose their cast | draft §4¶1, §6 |
| C2-5 | the name helper reports `*nabsent`; MAP_ABSENT recommended off | draft §3¶13-¶16 |
| C2-6 | the support unit's content id, compared by the check; its text is an abi reader (D76/D94) | draft §1¶4, §3¶1, §10¶3; §R4.14 |
| C2-7 | `PCREC_SUPPORT_STATIC`; `#error` on the stamp-name collision | draft §1¶3, §10¶3a; §R4.14 |
| open question 3 | adopted: the check and setup are inline; only helper and case-forcing users link the support unit | §R4.4, §R4.9, draft §10¶1 |
| family (a) | the case map is a third output of the existing UCD generator, not a new data set; control in `oracle_store/` | §R4.12 |
| family (b) | the template escapes reuse the pattern parser's decoder | §R4.10 |
| family (c) | `rx_group_run` is THE implementation of match_api.md §5.4¶6's lookup | draft §3¶17 |
| family (d) | a shared stamp-header prefix (`rx_info`/`rx_subst_info`): CANDIDATE, not adopted; trigger: a third record kind, or the first skew report | review file |
| family (e) | `--emit-support` is a new cli.md subsection (no emit-mode table exists) | §R4.14 |
| unlocks | five recorded as candidates with triggers; none scheduled | review file |

### R4.16 Rulings R9-R11 applied (revision 4b, lane substr4c, 2026-10-22)

| ruling | what it said | where it landed |
|---|---|---|
| R9 | pieces are `const unsigned char *` | already so in draft §4¶3 and §9 row 2, and in every recipe; the open question is closed (§R4.9 Q1) |
| R10 | the support unit is emitted by `pcrec --emit-support` | the open question is closed (§R4.9 Q2); the Makefile concern points at plan row `[CLI-OUTKEEP]`, not built here (draft §10¶2, §R4.14) |
| R11 | ONE replace-all function in the support unit, over the existing function-pointer types | draft §10¶6-¶10, §6¶8, §8 table, §9 row 1; tests in §R4.10; §R4.7 |

**The signature** (draft §10¶6):

```c
int rx_subst_replace_all(rx_nextnfn next_n, rx_iter *it,
                         const struct rx_subst_info *t, const rx_ctx *ctx,
                         const rx_subst_map *map, unsigned flags,
                         rx_subst_out *o,
                         unsigned char *restrict out, size_t cap, size_t *len);
```

**The matcher type.** `rx_matchfn` is the anchored match-here type and cannot
iterate. The type that fits is its find-all sibling `rx_nextnfn`
(match_api.md §2¶8a; `rx_info.next_n`), which main and lane/i2build both
define, and the support unit reads no other. No new matcher interface is
invented. The element comes from the record (`t->render`).

**Two consequences, for Frank's eye.** (1) "Never allocates" means the
workspace is the caller's: `o` carries the piece array and, for a case-forcing
template, the scratch (the case region's size depends on the match, so no
fixed stack buffer could bound it). The function's own storage is one stack
array of `RX_FOREACH_PAIRS` capture pairs, the figure `RX_FOREACH` already
uses. `[superseded: D175 dropped RX_FOREACH; the bound is the support unit's
own PCREC_SUBST_BATCH_PAIRS, 256, spec §10]` (2) The return is an `int` code, not a size, because the error codes
are negative `int`s: the size needed arrives in `*len` with
`PCREC_SUBST_NOSPACE`, and a scratch shortfall is told apart by
`o->sneed > o->scap`.

**Behaviour.** `[superseded by G1, §R4.17: it returns the number of matches
substituted, spec §10¶10]` It writes the full result and returns 0 with `*len`; on too
small a buffer it keeps matching, sums, and returns NOSPACE with the total
(no match searched twice); every other negative code is returned as is, with
no tail, by the §6¶1 error rule. The batch recipe is its reference, and the
equivalence test pins them together.

**Open questions for the interface: none.**

### R4.17 Ruling R13 applied (revision 4c, lane substb2, 2026-10-22)

Frank: "Agree with subst changes." The source is the use-case fit review
(`../dev/reviews/2026-10-22-r3-subst-usecase-fit.md` on lane/substuc
2ff5940ab, 29 blind use cases, 0 wrong answers from the design).

| id | adopted change | where |
|---|---|---|
| G1 | `rx_subst_replace_all` returns the NUMBER OF MATCHES substituted (`>= 0`, `INT_MAX` when there are more), `pcre2_substitute`'s own convention. A caller learns "did anything change?" and the count without the recipe. The ten parameters stay (R12) | draft §10¶6-¶7, §6¶8, §8 |
| G10 | `out == NULL` with `cap == 0` SIZES ONLY, as the flatten does: the count is returned and `*len` is the total, with nothing written. One sizing rule for both byte writers | draft §10¶7 |
| F0 | a short tested SETUP WRAPPER (one call per rx and template into a caller buffer) in `examples/` and in the spec's §6 recipes. No API change | draft §6¶9; `examples/subst/` |
| G6 | a template whose encoding is `byte` (or -1, all ASCII) emits the ASCII case step INLINE in its element and needs no support unit. Only the UTF-8 case table lives in the unit. So "a plain template is one `.c`" holds for byte-mode case forcing too | draft §1¶5, §10¶1 (the extended-forms build applies it) |
| static assert | the spec states the build-time check a no-map caller can write: `_Static_assert(<S>_MAXNUM < <RX>_NCAPS, ...)` | draft §3¶3 |

FILED AS CANDIDATES (not built):

- **G2-names**: `<PREFIX>_GROUP_<name>` stamps on the rx and a per-template
  reference X-macro, so a by-name map is checked at build time. Trigger: a
  user asking for build-time name checks.
- **G4**: an in-place flatten that stages the pieces its writes would
  overwrite in scratch. Trigger: the first in-place user.

**What the interface build (lane substb2) builds of §R4.** Everything but
the extended module: the core template language over pieces, the map, the
check and the setup, the support unit with its content id and
`PCREC_SUPPORT_STATIC`, the flatten, the helper (C), replace-all, the
recipes, `--emit-support`, and the HOOKS the extended forms need (the
scratch fields of `rx_subst_out`, `sneed`, the scratch NOSPACE rule, `uses`
and `support`/`support_id` in the record). Module `subst-extended`
(§R4.13), the case table and G6's inline step come with the extended-forms
build; until then the module is refused at compile as today. `[superseded:
module subst-extended is built, lane substext, spec §2¶7]`

---

## REVISION 3 — the panel's dispositions applied (lane substr3, 2026-10-22) — READ §R4 FIRST

**Status: PROPOSED, design only.** Nothing under `src/`, `cli/`, `lib/` or
`tests/` was touched. Two probes were run on the Linux dev box against the head
of `lane/subst` (abi 84, the I4 iterator) and libpcre2 10.46. Per the lane brief,
their sources and transcripts stay in the session scratchpad. The transcript
lines this section rests on are quoted in §R3.14.

### R3.0 What changed, finding by finding

Each panel id maps to the section that discharges it. The review file has the
critics' verbatim text and the manager's dispositions.

| id | what R3 does | where |
|---|---|---|
| crit1-1 | §R2.5 rule 1's "ordered and non-overlapping by construction" is false. The element checks every span and returns `PCREC_SUBST_BADSPAN`. PCRE2's stricter test is stated, the corner is documented with a witness, and nothing is added to match_api §3.8 | §R3.6, §R3.14 |
| crit1-2 | names bind to a (first, count) RUN of `rx->groups` rows, and the render walks it per match_api §5.4¶6. `rx_group_run` is the one name-to-run helper; two other sites are named as later adopters | §R3.2 |
| crit1-3 | the NOSPACE capacity differs from PCRE2's by exactly 1 (no NUL). Labelled and spec'd | §R3.5, §R3.10 |
| crit1-4 | the unset axis already has D38 Q3's strict variant. R3 names it `error` and gives it a code | §R3.7 |
| crit1-5 | probed: consistent with match_api §9 and with `_search` in a loop. Pinned as stated behaviour; the PCRE2 difference is located in libpcre2's anchored retry | §R3.14 |
| crit1-6, crit3-1 | distinct codes, and `*outlen`/`*nsubst` are written on every return path | §R3.5 |
| crit2-1 | the element is BATCH-shaped (k matches per call; per-match is k = 1). Q-F2 is restated | §R3.1, §R3.16 |
| crit2-2 | subst and rx artifacts come from ONE pcrec build, checked at compile (`#error`) and at bind. The shape-contract alternative is named as a candidate | §R3.8 |
| crit2-3 | the glue sizes its buffer from `rx->ncaps` and drives `next_n` itself, with k = 1 above the batch buffer. No group count PCRE2 accepts is refused | §R3.4 |
| crit2-4 | the timing cell is rebuilt: separated vs a D163 composite twin, A/A floors, the listed cells, `pcre2_substitute` as an external row | §R3.13 |
| crit2-5 | `ctx.ncap` vs §2¶6 is reconciled; renderer segments get their `user`; "no resume after `limit`" is stated | §R3.1, §R3.4, §R3.9 |
| crit2-6 | the NEEDED shape is an `rx_group_entry` array and bind is a generic shape match. The version number goes to [IFACE-PUSH]; the `.h`/`.c` stamp rule follows §6.3.1; the three function types are recorded as one family | §R3.2, §R3.8, §R3.12 |
| crit2-7 | the general form is a PER-MATCH CONSUMER. Only the shape type and the generic bind are built; two later members are named with triggers | §R3.12 |
| crit3-2 | the binding records the rx, its `ncaps` and a tag. The glue and the element check them once per call | §R3.3 |
| crit3-3 | lengths saturate. An overflow is NOSPACE with `*outlen = SIZE_MAX`, and a length never travels through a signed return | §R3.4, §R3.5 |
| crit3-4 | `<S>_NREFS` is `max(1, n)` | §R3.3 |
| crit3-5 | bind has distinct codes and names the offending reference; `dlopen` is covered by the run-time abi check | §R3.3, §R3.5 |
| crit3-6 | `${!name}` is resolved once per call by the glue, against the iterator's variables; bind cannot see them | §R3.7 |
| crit3-7 | `out` contents after a failure are unspecified, `out` must not overlap `s` (`restrict` plus a UB sentence) | §R3.9 |
| crit3-8 | a context-init helper for custom glue, and a §3.8¶9 spec hunk naming the `rx_iter` fields pcrec's shared code reads | §R3.9 |
| crit3-9 | thread safety is stated | §R3.9 |
| crit3-10 | the differences from PCRE2, and the grow-and-retry recipe | §R3.10 |
| crit3-11 | `--subst-file`; the header include order | §R3.11 |
| crit3-12 | in-place stays a contract only, and the overlap rule is now explicit | §R3.9, §R2.6 |

One finding is the lane's own, made while writing §R3.9 (F-R3-1): §R2.4's glue read
`it->vars` on a FRESH iterator. On a FRESH iterator with no `rx_iter_vars` call, that
field is garbage (match_api §3.8¶5: "every field `RX_ITER_INIT` does not write may hold
any value before the first call"). The §R3.9 helper reads it only when the
`PCREC_ITER_OPT_VARS` bit says it was set.

### R3.1 The element is batch-shaped

**[R4: the batch stays; the cursor, `rx_subst_put`, the byte output and the binding argument are SUPERSEDED by §R4.5 (pieces) and the draft's §4 (`<s>_render(ctx, map, caps, k, flags, o)`)]**

crit2-1 is right that §R2.8's "one out-of-TU call per match" is not D171's
class. D171 accepted a FIXED cost per find-all. The I4 note measured `next_n`
at k = 64 against the per-match loop, and found the gain comes from removing
calls. So the element renders a BATCH: k consecutive matches of one find-all
per call. The per-match render is the case k = 1.

```c
/* Where one find-all's output stands between element calls. */
typedef struct rx_subst_cur {
    size_t prev;   /* end of the last match consumed: the next gap starts here */
    size_t w;      /* bytes the output needs so far; SIZE_MAX once that overflowed */
    int    fits;   /* 1 while every one of those bytes is in out */
} rx_subst_cur;

#define RX_SUBST_GAPS 0x1u   /* copy [cur->prev, start) before each rendering */

/* Renders k consecutive matches. caps holds k * ctx->ncap pairs; match i is at
 * caps + i * ctx->ncap, as <prefix>_next_n writes them. With RX_SUBST_GAPS the
 * gap before each match is copied first (substitution). Without it the
 * renderings are written back to back (a templated grep -o). Any other flag
 * bit is refused. Bytes go to out[cur->w, cap) while everything fits, and
 * never past cap. Returns 0 or a negative code (§R3.5); the length is in
 * cur->w, never in the return value. */
typedef int rx_substfn(const struct rx_subst_binding *b, const rx_ctx *ctx,
                       const ptrdiff_t (*caps)[2], size_t k, unsigned flags,
                       unsigned char *restrict out, size_t cap, rx_subst_cur *cur);
```

What moved, and why:

- **The gap copy moves into the element** (§R2.5 rule 1 had it in the glue).
  A batch cannot be rendered without its gaps unless the element hands k
  separate renderings back. Handing them back would take a second buffer or
  k returns, which is the per-match shape again. `RX_SUBST_GAPS` keeps the
  render-only use that §R2.4's "custom glue is first-class" promised.
- **The length travels in `cur->w` (a `size_t`), and the return is a code.**
  So no length can be read as a code (crit3-3's ptrdiff_t cast), and a
  rendering longer than `PTRDIFF_MAX` needs no special case: it saturates
  (§R3.4).
- **One write helper**, `rx_subst_put(cur, out, cap, src, len)`, sits in the
  subst block. Every emitted render calls it for every byte run. It holds the
  fit test and the saturation, so the overflow rule is written once rather than
  in every emitted template.
- **`ctx` carries what is constant over the call**: `subject`, `len`, `ncap`,
  `vars`/`nvars` (the per-call resolved view, §R3.7) and `user`. Per match, the
  element sets `pos` and `caps` in a local copy, only when the template has
  `rx_renderfn` segments (match_api §2¶7). For each segment, `user` is that
  segment's own pointer, taken from the binding (§R3.3). This discharges
  crit2-5's "segments unbindable".
- **`ctx.ncap` gets its first producer.** The element's `ctx.ncap` is the
  `ncaps` of a COMPLETED match. That is the "ncaps on completion" reading the
  type's own comment already gives. match_api §2¶6 currently says the field has
  no producer; phase B's spec hunk says that the subst element is now the first
  producer, and that it writes the completion value, not a watermark. The
  element checks `ctx->ncap == b->ncaps` once per call (§R3.3).

**Cost, restated.** There is one out-of-TU call per BATCH, not per match. At the
glue's doubling, a find-all of M matches makes about `M/64 + 7` element calls,
plus one `next_n` call per batch. Inside the element, each named reference costs
two loads (the run, and the first row's slot) plus one participation test per
run member. A run of one is the common case. Numbered references cost nothing
extra (D61). All of this is UNMEASURED. §R3.13 is the cell that measures it.

### R3.2 The needed shape, the run, and the generic bind

**[R4: the NEEDED shape becomes the REFERENCE LIST in first-appearance order; the bind is SUPERSEDED by the optional map, the one check and helper (C) (§R4.3, §R4.4). The satisfaction table survives as helper (C)'s table; `rx_group_run` and its later adopters stand]**

**The NEEDED shape is an `rx_group_entry` array** (crit2-6). `rx_group_entry`
already exists in the shared block (match_api §2¶8), and it already has every
column a reference needs:

| column | a `$k` / `${k}` row | a `${name}` row | a `${site.group}` row (Q-M2) |
|---|---|---|---|
| `name` | NULL | `"name"` | `"group"` |
| `number` | `k` | `-1` (any) | `-1` |
| `slot` | `-1` (needed, not delivered) | `-1` | `-1` |
| `ref` | NULL | NULL | `"site"` |

So the subst record's reference list is `const rx_group_entry *needs`, and
`rx_subst_ref` (§R2.4) is withdrawn. Bind becomes a generic match of a needed
array against an offered shape (`rx_info`'s `ncaps`, `ngroups` and `groups`).
It knows nothing about templates. That is the shape type crit2-7 asks to have
built now, and the only one (§R3.12).

**Satisfaction**, replacing §R2.2's table:

| needed row | satisfied when | binding records |
|---|---|---|
| `number == 0` | always | nothing (slot 0 is a constant) |
| `number == k ≥ 1`, `name == NULL` | `k <= ngroups && k < ncaps` | nothing (slot `k` is a constant, D61) |
| `name != NULL` | `rx_group_run` finds a run of `count ≥ 1` rows in the right scope, and every row of the run has `slot >= 0` | `{first, count}`: row indexes into `rx->groups` |

**A name binds to its RUN**, not to one slot (crit1-2). A run's members are
contiguous ROWS of `rx->groups`, because the array is sorted by (name, number)
(match_api §5.4¶4-¶5). Their SLOTS are not contiguous. So the binding stores
`{first, count}` into `rx->groups`, and `rx->groups` itself is the slot list.
Per match, the render walks the run per match_api §5.4¶6: the first row whose
slot participated (both offsets set) is the group, and a run with no
participating member is unset. crit1's cell `(?J)(?<n>a)|(?<n>b)`, `[${n}]` on
`"xaby"` then renders `x[a][b]y`, which is PCRE2's answer. §R2.2's single-int
binding gave `x[a][]y`. The run of one is a one-row walk.

**One name-to-run helper**, in the subst block:

```c
/* The run of rows named `name` in scope `ref` (NULL: the caller scope,
 * rows [0, nnames); otherwise the delivered rows [nnames, nentries) of site
 * `ref`, match_api §5.5). Writes the first row's index to *first and returns
 * the run's length, 0 when there is none. bsearch, then walk back to the
 * run's head (match_api §5.4¶6's first two steps). */
static inline int rx_group_run(const struct rx_info *rx, const char *name,
                               const char *ref, int *first);
```

There are three name-to-run sites today, and the bind uses only this one. The
other two are LATER ADOPTERS and are not rewritten now:

- match_api §5.4¶6's caller prose. It can point at `rx_group_run` once the helper
  moves into the rx shared block, which is an rx abi event. The trigger is the
  next rx abi event, or [IFACE-PUSH].
- The compiler's own resolution for the emitted `\k<name>`. This is C under
  `src/`, not header text, so "one helper" there means the same algorithm checked
  by an agreement cell (phase B: `rx_group_run` against the compiler's resolver
  over the `(?J)` corpus). It does not mean shared code.

### R3.3 The binding

**[R4: WITHDRAWN (ruling 1): no binding object; §R4.3-§R4.4]**

```c
typedef struct rx_subst_run { int first, count; } rx_subst_run;   /* rows of rx->groups */

typedef struct rx_subst_binding {
    uint32_t                    tag;      /* PCREC_SUBST_BOUND, written last by a successful bind */
    int32_t                     ncaps;    /* rx->ncaps at bind: the pairs every caps entry holds */
    const struct rx_info       *rx;       /* the record bound against */
    const struct rx_subst_info *sub;
    const rx_subst_run         *runs;     /* the caller's <S>_NREFS entries, one per NAMED row */
    void *const                *seg_user; /* one per rx_renderfn segment; NULL when the
                                             template has none (bind checks the count) */
} rx_subst_binding;

/* 0 = bound. Otherwise PCREC_SUBST_MISMATCH (a record from another build, or
 * nruns / nseg too small) or PCREC_SUBST_MISSING_REF (the rx delivers no slot
 * for needs[*bad_ref]). *bad_ref is -1 unless the code is MISSING_REF. Reads
 * only the two records. Never allocates. On a refusal, b->tag is not BOUND. */
static inline int pcrec_subst_bind(rx_subst_binding *b, const struct rx_info *rx,
                                   const struct rx_subst_info *sub,
                                   rx_subst_run *runs, size_t nruns,
                                   void *const *seg_user, size_t nseg,
                                   int *bad_ref);
```

- **The binding carries the rx** (crit3-2), so the glue takes no separate
  `rx`. Pairing a binding with the wrong rx through the glue is then
  impossible. What remains is a caller who hands the element a `caps` array
  from a different artifact. The element catches that once per call:
  `ctx->ncap != b->ncaps` returns `PCREC_SUBST_MISMATCH`. It does not catch a
  different rx with the same `ncaps`. That case is UNDEFINED, and phase B's spec
  says so beside match_api §3.8¶8's "another artifact" rule, which has the same
  shape and the same reason (D165 addendum 3: no owner check).
- **`<S>_NREFS` is `max(1, number of named rows)`** (crit3-4), so
  `rx_subst_run runs[<S>_NREFS]` is never a zero-length array. `nruns` is
  checked against the record's own count.
- **Distinct refusals** (crit3-5): `MISMATCH` for "these records do not belong
  together" (a different abi, a `nruns` that is too small, a missing
  `seg_user`), and `MISSING_REF` with the offending row's index, from which a
  diagnostic names the reference, `rx->name`, and what the rx does offer
  (§R2.2's message). The `dlopen` case is covered: bind compares `rx->abi`,
  `sub->abi` and the including header's `PCREC_RX_ABI_H` at run time.
- **Read-only after bind.** Nothing writes a binding after bind returns
  (§R3.9, thread safety).

### R3.4 The glue

**[R4: WITHDRAWN (rulings 4 and 5): no shipped loop; the draft's §6 recipes, §R4.7]**

```c
#ifndef PCREC_SUBST_PAIRS
#define PCREC_SUBST_PAIRS 256          /* the glue's batch buffer, in pairs */
#endif

/* Every match of `it` (FRESH, setters applied), up to `limit` of them, gaps
 * copied, each match rendered, the tail copied. Returns 0 or a negative code
 * (§R3.5). *outlen and *nsubst are written on EVERY path: on 0, the produced
 * length and the substitution count; on PCREC_SUBST_NOSPACE, the capacity
 * that suffices (SIZE_MAX: none does) and the full count; on any other code,
 * 0 and 0. out == NULL sizes only. out must not overlap s[0, n). */
static inline int pcrec_subst(const rx_subst_binding *b, rx_iter *it, size_t limit,
                              unsigned char *restrict out, size_t cap,
                              size_t *outlen, size_t *nsubst)
{
    *outlen = 0; *nsubst = 0;
    if (b->tag != PCREC_SUBST_BOUND || b->rx->abi != PCREC_RX_ABI_H
        || b->sub->abi != PCREC_RX_ABI_H || b->ncaps != b->rx->ncaps || !b->rx->next_n)
        return PCREC_SUBST_MISMATCH;                       /* once per call */
    const size_t nc = (size_t)b->ncaps;                    /* >= 1 (match_api §5¶2) */
    size_t kmax = nc <= PCREC_SUBST_PAIRS ? PCREC_SUBST_PAIRS / nc : 1;
    if (kmax > 64) kmax = 64;
    ptrdiff_t buf[kmax * nc][2];                           /* >= one match at any ncaps */
    rx_var vres[b->sub->nvrefs ? b->sub->nvrefs : 1];      /* ${!name}, once per call */
    rx_ctx ctx;
    int rc = rx_subst_ctx_init(&ctx, it, b, vres);         /* §R3.7, §R3.9 */
    if (rc < 0) return rc;
    rx_subst_cur cur = { 0, 0, out != NULL };
    size_t k = 1, done = 0;
    while (done < limit) {
        size_t want = k < limit - done ? k : limit - done;  /* never fetch past limit */
        size_t got = b->rx->next_n(it, buf, want);
        rc = b->sub->render(b, &ctx, (const ptrdiff_t (*)[2])buf, got, RX_SUBST_GAPS,
                            out, cap, &cur);
        if (rc < 0) return rc;
        done += got;
        if (got < want) {                                  /* the iterator ended */
            if (it->rc < 0) return it->rc;
            break;
        }
        if (k < kmax) k = 2 * k < kmax ? 2 * k : kmax;
    }
    rx_subst_put(&cur, out, cap, ctx.subject + cur.prev, ctx.len - cur.prev);   /* the tail */
    *nsubst = done;
    *outlen = cur.w;
    return (cur.w == SIZE_MAX || (out && !cur.fits)) ? PCREC_SUBST_NOSPACE : 0;
}
```

- **It drives `next_n` itself**, not `RX_FOREACH` (crit2-3). This is for two
  reasons. First, `RX_FOREACH` refuses `ncaps > RX_FOREACH_PAIRS` (the I4
  ruling's 255-group ceiling), while PCRE2 has no group limit below 65,535; the
  glue's buffer is sized from `rx->ncaps` and falls to k = 1 above
  `PCREC_SUBST_PAIRS`, so no group count PCRE2 accepts is refused. Second,
  `RX_FOREACH` over-fetches past a stop. crit2-4's `limit = 4` cell fetches 7
  matches (1 + 2 + 4). The glue caps every request at the remaining limit, so
  `limit = 1` runs exactly one search, and `limit = 4` fetches exactly 4.
- **Stack cost.** The buffer is a VLA of `16 * kmax * ncaps` bytes on LP64.
  That is 4,096 bytes when `ncaps <= 256`, and `16 * ncaps` above it (k = 1).
  At PCRE2's ceiling that is 1 MiB, more than a 128 KB thread stack holds (the
  same class as match_api §5.3's frame-size note). A caller with that many
  groups writes the ten-line custom glue with a heap buffer, because the element
  takes any `caps` array (§R3.12). Phase B's spec states the bound. The glue
  needs C99 (VLAs, `for` declarations), as `RX_FOREACH` already does.
- **`limit`** keeps §R2.4's meaning: `1` is PCRE2's non-global substitution,
  and `SIZE_MAX` is global. With `limit == 0` the loop does not run, the
  subject is copied, and the iterator stays FRESH. **No resume after a
  `limit` stop** (crit2-5). The iterator is then BOUND, positioned after match
  `limit`, but the tail has already been copied into `out`. So a second
  `pcrec_subst` call on it would produce a second copy of the rest. The spec
  says: after a return with `*nsubst == limit`, the iterator's state is
  unspecified for the glue. A caller who wants to resume uses the element and
  its own loop.
- **Saturation** (crit3-3). `rx_subst_put` adds lengths with an overflow test.
  A total past `SIZE_MAX - 1` sets `cur.w = SIZE_MAX` and clears `fits`, and
  the glue returns NOSPACE with `*outlen = SIZE_MAX`, meaning no buffer
  suffices. That is reachable only with 32-bit `size_t`. `*nsubst <= n + 1`,
  and gcc caps an object at `PTRDIFF_MAX` bytes, so the count cannot wrap.

### R3.5 Codes and `*outlen`

**[R4: `*outlen`/`*nsubst` go with the glue; NOSPACE now means pieces or scratch, decided before any write (§R4.5); `PCREC_SUBST_RENDER` (−13) is reserved with no producer; the draft's §8 is the table]**

The subst codes sit below `PCREC_ERR_ITER` (−10), which keeps them clear of the
give-up range and of every existing refusal. Their VALUES are PROPOSED and are
fixed at landing as the next free numbers below the floor, the same house rule
as an abi number. Every code is distinct, and an element or glue never returns
`-1`.

| name (PROPOSED value) | returned by | meaning | `*outlen`, `*nsubst` |
|---|---|---|---|
| `PCREC_SUBST_NOSPACE` (−11) | glue | `out` too small. The output in `out` is the first `cap` bytes or less (unspecified, §R3.9) | the capacity that suffices, or `SIZE_MAX` (none does); the FULL count |
| `PCREC_SUBST_BADSPAN` (−12) | element, glue | the rx reported a span the splice cannot express (§R3.6) | 0, 0 |
| `PCREC_SUBST_RENDER` (−13) | element, glue | an `rx_renderfn` segment returned `-1` | 0, 0 |
| `PCREC_SUBST_UNSET` (−14) | element, glue | `--unset=error`: a referenced GROUP is unset in this match (PCRE2's −55 class) | 0, 0 |
| `PCREC_SUBST_MISMATCH` (−15) | bind, glue, element | the records, binding, flags or caps do not belong together (§R3.3) | 0, 0 |
| `PCREC_SUBST_MISSING_REF` (−16) | bind | the rx delivers no slot for `needs[*bad_ref]` (PCRE2's −49 class, at bind) | (bind writes `*bad_ref`) |
| `PCREC_ERR_UNSET_VAR` (−8, exists) | glue | `--unset=error`: a `${!name}` variable is unset (§R3.7) | 0, 0 |
| the iterator's code (§4) | glue | a give-up or refusal ended the find-all | 0, 0 |

**NOSPACE's capacity is PCRE2's minus one** (crit1-3). PCRE2 reports 12 for
`a*` → `[$0]` on `"bab"` because it counts its NUL terminator; pcrec reports 11
because the output has no NUL (D38 Q4, length only). The spec states this
exactly. A caller porting a PCRE2 grow-and-retry loop that adds 1 gets a
buffer one byte larger than needed, which is harmless.

**On a code other than NOSPACE, `*outlen` and `*nsubst` are 0.** PCRE2 writes
`PCRE2_UNSET` (`~0`) there. pcrec does not, because `SIZE_MAX` already means
"no buffer suffices" on NOSPACE. The return code is what tells the caller
which case it is in.

### R3.6 Span validation: BADSPAN

**§R2.5 rule 1 was FALSE** (crit1-1, BLOCKER). A `\K` reached through a
SUBROUTINE CALL from a lookaround runs, and the iterator then reports a span
whose end precedes its start, or whose start precedes the previous match's
end. pcrec refuses `\K` written lexically inside a lookaround, as PCRE2 does,
but not one reached through a call. The iterator reports these spans
correctly, as `pcre2_match` does (§R3.14 probe 1). What fails is the splice: an
unsigned gap wraps, and `memcpy` runs `SIZE_MAX` bytes.

**The rule.** The element checks every span before it uses one:

- with `RX_SUBST_GAPS`: `end < start`, or `start < cur->prev`, returns
  `PCREC_SUBST_BADSPAN`;
- without it (renderings back to back): only `end < start` is refused. Overlap
  is harmless there, and a templated `grep -o` over `x|(?<=(?1))y|(\Kx)`
  renders both of the overlapping matches.

**PCRE2's test is stricter, and pcrec documents the corner rather than
matching it.** `pcre2_substitute` returns −60 (BADSUBSPATTERN) when a match
STARTS BEFORE THE SEARCH START, or ends before it starts. The search start
equals the previous match's end, except after an empty match whose
NOTEMPTY_ATSTART retry failed. There the search starts one character later,
so a match reported at the empty match's own position is accepted by pcrec
and refused by PCRE2. The iterator does not expose its per-search start, and
cheap exposure is not available. `next_n` writes only caps. A start field
would be an `rx_iter` layout change and an abi event, and in a batch it would
need one word per entry. So R3 takes the manager's "else" branch: pcrec checks
against the previous END, and the spec names the corner with its witness
(§R3.14, probe 1c). `^|(?<=(?1))y|(?!)(\Kz)` on `"zy"`: the iterator reports
`[0,0) [0,2)`, pcrec renders `[][zy]`, and PCRE2 returns −60.

**match_api §3.8 gains NO "ordered, non-overlapping" sentence** (the manager's
ruling). The iterator legitimately reports such spans, as `pcre2_match` does,
and the restriction belongs to the consumer that needs it. §R2.8's closing
claim that "the two spec needs are clarifications" loses its first item.

**Population.** Every pattern that reaches a `\K` through a call from a
lookaround. Both witnesses are crit1's. The cost is two compares per match,
inside the element.

### R3.7 The unset axis and `${!name}`

**[R4: the axis becomes the run-time flag of §R4.6 (default BLANK, ruled R6); `${!name}` resolution stands, through `rx_subst_ctx_init`'s new signature]**

**D38 Q3 already decided the axis** (crit1-4): "unset-but-existing group renders
EMPTY by default, as a GENERATION AXIS with a strict PCRE2-error variant". R3
spells the two values `--unset=empty` (the default) and `--unset=error`. Under
`error` the element returns `PCREC_SUBST_UNSET` on the first match in which a
referenced group (a run: none of its members participated) is unset. PCRE2's
own default is the error (−55), and its `SUBSTITUTE_UNSET_EMPTY` is pcrec's
default. That difference was ruled at D38, and §R3.10 lists it. The record
carries the axis value the subst was compiled with (`unset`), and that value
is stamped.

**`${!name}` is resolved once per call, by the glue, against the iterator's
variables** (crit3-6). Bind cannot check it: variables are bound to the
ITERATOR (`rx_iter_vars`, match_api §3.8¶4), not to the rx, and they are not
known until the call. `rx_subst_ctx_init` scans the iterator's `rx_var` array by
name once per call (variables_common.md §3.2's rule) for each of the record's
`vrefs`. It writes the matches, in the template's own order, into the glue's
`vres` array, and points `ctx.vars` at that array. A name the caller did not
pass is UNSET (variables_common.md §3.4). The render then reads its j-th
variable as `ctx->vars[j]`, a constant index, and every entry still carries its
name. So an `rx_renderfn` segment that scans `ctx->vars` by name still works.

Unset variables follow the same axis. `empty` renders nothing (variables_common
§2.4's replacement default). `error` returns the existing `PCREC_ERR_UNSET_VAR`
before any output, because a variable cannot change between matches. This
keeps one code per meaning.

### R3.8 One build, and the version number

**Same-build rule** (crit2-2): **a subst artifact and an rx artifact used
together must come from the same pcrec build, which means the same `abi`.**
This is checked twice:

- **At compile time**, by the shared block's existing `#error`. The subst header
  carries a copy of the rx shared block under `PCREC_RX_ABI_H`, so a TU that
  includes a subst header and an rx header of different abi does not compile.
- **At bind** (and again by the glue), by comparing `rx->abi`, `sub->abi` and
  the including header's number. This covers `dlopen` and separately compiled
  TUs.

An rx abi event (any scaffolding change, D76/D94, comments included) therefore
also orphans every subst artifact built before it. That cost is accepted and
stated, not designed around.

**The narrower alternative is NOT designed here.** It would key the bind to a
SHAPE-CONTRACT version (the render on primitives: subject, caps, vars), so that
a subst would survive rx scaffolding changes. It is named as a candidate under
[DD-3] / [RXINFO-REMODEL], for the manager to file. Its trigger is a caller who
needs subst and rx artifacts from different builds (a prebuilt template library
or an [ART-MGR] catalog).

**Q-M3 is resolved: no new number.** The subst record carries `abi`, which
equals the shared `PCREC_RX_ABI_H`. That is all the same-build rule needs. The
subst block lives only in subst headers, so its LANDING changes no rx artifact
(no rx abi event, and today's artifacts stay byte-identical). Any LATER change
to the subst block's text is an abi event under D76/D94, moving every rx reader.
That is the cost §R2.10(3) weighed. A subst-block number of its own is filed
with [IFACE-PUSH] as a candidate.

**Stamps follow match_api §6.3.1¶1.** The subst `.h` carries the constants a
caller needs to DECLARE STORAGE or `_Static_assert`:

- `<S>_NREFS`: the binding's run count, `max(1, n)`;
- `<S>_NSEGS`: the `seg_user` count, `max(1, n)`;
- `<S>_MAXNUM`: the highest `$k`, or 0.

This is the same family as `<PREFIX>_NCAPS`, `<PREFIX>_NVARS` and §10.4's
sizing macros. Every other subst stamp (`<S>_UNSET`, the module tier, the
template's reference census) goes into the `.c` only.

### R3.9 The caller contract

**[R4: `out`'s overlap and after-failure rules become the pieces-are-borrowed and commit rules (draft §7¶1-¶2, §4¶21); `rx_subst_ctx_init` takes `(ctx, it, ncaps, t, vres, flags)`]**

- **`out` must not overlap `s[0, n)`** (crit3-7). The glue and the element
  declare `out` `restrict`. An overlapping call is UNDEFINED, and the spec says
  so in one sentence. In-place is the separate contract of §R2.6 (crit3-12),
  still contract-only.
- **`out` after a failure** (Q-M1, crit3-7): on any negative return, NOSPACE
  included, the contents of `out[0, cap)` are UNSPECIFIED. This is PCRE2's own
  stance. A caller who needs the subject intact keeps it out of place, and the
  previous rule already requires that.
- **Thread safety** (crit3-9). A binding is read-only after bind, so one
  binding may serve any number of threads at once, each with its own
  iterator, `out` and `vres`. The records are `const`. The glue keeps all
  per-call state in automatic storage. The iterator's own rule is match_api
  §3.8¶11's.
- **The context-init helper** (crit3-8):

  ```c
  /* ctx for an element call over iterator `it` with binding `b`: subject, len
   * and ncap from them; vars resolved into vres (b->sub->nvrefs entries, at
   * least 1); user NULL (segments get theirs per call, §R3.1). Returns 0 or
   * PCREC_ERR_UNSET_VAR (--unset=error). Reads it->vars only when the
   * iterator is BOUND or ENDED, or FRESH with PCREC_ITER_OPT_VARS set. */
  static inline int rx_subst_ctx_init(rx_ctx *ctx, const rx_iter *it,
                                      const rx_subst_binding *b, rx_var *vres);
  ```

  A custom glue calls this instead of writing `rx_ctx`'s eight members
  positionally. That leaves the struct's layout free to grow without breaking
  callers. The last clause of the comment is the fix for F-R3-1 (§R3.0).
- **The iterator fields pcrec's shared code reads.** Phase B's spec hunk to
  match_api §3.8¶9 adds one sentence: `s` and `n` hold their bound values in
  every state; `vars` and `nvars` hold them once the iterator is BOUND (bind
  normalizes them) and, while FRESH, only if `rx_iter_vars` was called
  (`PCREC_ITER_OPT_VARS`). pcrec's shared blocks (`RX_FOREACH`, the subst
  block) read exactly these fields. A caller still reads them only through
  `rx_subst_ctx_init`.

### R3.10 Where pcrec's substitution differs from `pcre2_substitute`

**[R4: rows 1-3, 5-8 and 10 and the grow-and-retry recipe are SUPERSEDED by the draft's §9 and §6¶4 (no match is searched twice); rows 4, 9 and 11 stand]**

| # | PCRE2 | pcrec | source |
|---|---|---|---|
| 1 | NOSPACE capacity counts the NUL (`a*`→`[$0]` on `"bab"`: 12) | no NUL, so 11 | D38 Q4; §R3.5 |
| 2 | writes a NUL; `PCRE2_UCHAR *` | length only; `unsigned char *`; embedded NULs are legal output | D38 Q4 |
| 3 | `SUBSTITUTE_EXTENDED`, `_LITERAL`, `_UNKNOWN_UNSET` as run-time flags | the dialect is the template's compile-time module tier; unknown references are a bind refusal; unset is a compile-time axis | D38 Q3/Q5; §R3.7 |
| 4 | unknown group: −49 at substitute time | `MISSING_REF` at bind, before any output | §R3.3 |
| 5 | unset group: −55 unless `UNSET_EMPTY` | empty unless `--unset=error` | D38 Q3 |
| 6 | NOSPACE: the error, no count | NOSPACE and the full count | §R3.5 |
| 7 | the NOSPACE retry is a second call | the same: a second pass over a FRESH copy of the iterator (match_api §3.8¶10) | §R2.5 rule 4 |
| 8 | non-global (1) or global (all) | any `limit`; `0` copies the subject | §R3.4 |
| 9 | −60 when a match starts before the SEARCH start | `BADSPAN` when it starts before the previous END; the empty-retry corner differs | §R3.6 |
| 10 | on error, `outlength = PCRE2_UNSET` | 0, with the code | §R3.5 |
| 11 | `MATCH_INVALID_UTF` global iteration: the anchored retry reports a match past an ill-formed byte | the iterator's answer, equal to `_search` in a loop | §R3.14 probe 2 |

**The grow-and-retry recipe**, which phase B's guide and spec carry:

```c
rx_iter it0 = RX_ITER_INIT(s, n), it = it0;     /* keep a FRESH copy for the retry */
size_t len, k;
int rc = pcrec_subst(&b, &it, SIZE_MAX, out, cap, &len, &k);
if (rc == PCREC_SUBST_NOSPACE && len != SIZE_MAX) {
    unsigned char *big = malloc(len ? len : 1);
    it = it0;                                    /* a second match pass, as PCRE2's */
    rc = pcrec_subst(&b, &it, SIZE_MAX, big, len, &len, &k);
}
```

### R3.11 The CLI and the header

**[R4: `--unset=` leaves the CLI (§R4.6); the rest stands]**

- **`--subst-file FILE`** (crit3-11) beside `--subst TEMPLATE`. It reads the
  template from a file, byte for byte, so a template with quotes, `$` or a
  newline needs no shell escaping. The two options are mutually exclusive,
  and each excludes `--pattern`. Spelling is the manager's call.
- **`-o dmy.c` also writes `dmy.h`**, as an rx compile does. The `.h` holds the
  rx shared block (guard `PCREC_RX_ABI_H`), then the subst block (guard
  `PCREC_SUBST_H`, which `#error`s unless `PCREC_RX_ABI_H` is defined to the
  number the subst was built with), then `dmy`'s own declarations.
- **Include order.** A TU may include an rx header and any number of subst
  headers in any order. Whichever comes first defines the shared block and the
  guard drops the later copies; the subst block follows the shared block
  inside each subst header, so its precondition always holds. One
  `#include "dmy.h"` is enough to write a custom glue, and `RX_FOREACH` comes
  with it.

### R3.12 The general form: a per-match consumer

**[R4: the family stands; the shared binding is now the optional map and helper (C) (§R4.11); the `rx_substfn` row's binding column reads "the map, optional"]**

crit2-7's unlock, accepted as design text. A substitution is one member of a
family: a **per-match consumer**. It is a spec over a DECLARED NEEDED SHAPE,
bound once to an OFFERED shape, and driven per batch. The family:

| member | what it consumes into | status | trigger |
|---|---|---|---|
| render (this note) | bytes, with or without gaps | DESIGNED (phase B builds it) | built |
| extract-to-struct | a typed record per match (named fields, numeric conversion) | NAMED, not built | a structured-extraction ask from a user |
| a pcre2-ovector adapter | renders over a libpcre2 ovector instead of an iterator's caps | NAMED, not built | the bench wants templated output from both engines over one template |
| split, count, callbacks | glue only: no element, because none needs a shape | glue recipes | when asked |

**Built now (in phase B): only the shared shape type and the generic bind.** The
shape type is `rx_group_entry` as the needed array, plus `rx_subst_run`. The
bind is `pcrec_subst_bind`'s matcher, written over two shapes, not over
templates. The batch element makes §R2.6's sink and streaming glue thin loops
over `next_n` (D38 §7.2's `pcrec_subst_to`).

**One function family over `rx_ctx`** (crit2-6), recorded here so a fourth
member is a row rather than a surprise:

| type | consumes | produces | binding |
|---|---|---|---|
| `rx_matchfn` | `ctx` (pos, caps so far) | a length or fail | `rx_callout_ref.user` |
| `rx_renderfn` | `ctx` (one completed match) | one segment's bytes | per-segment `user` (§R3.3 `seg_user`) |
| `rx_substfn` | a binding, `ctx`, a batch of k matches | the batch's bytes into a cursor | `rx_subst_binding` |

Q-M5 is answered by this table. `rx_substfn` is not an `rx_renderfn`, because it
consumes a batch and a binding, and a renderer consumes one match. A compiled
subst used as another template's segment would be a k = 1 adapter, a
`rx_renderfn` wrapping a binding. That is an unlock, not built, and its trigger
is a template that names another compiled template.

### R3.13 The phase-B timing cell, rebuilt

**[R4: RETIRED: ruling 4 rules out the fused form this cell could build (§R4.11)]**

crit2-4. The question is whether the separated design (the shipped form: the
glue in the caller's TU, the batch element out of TU) loses to a fused one.
The comparator is a hand-written **D163 composite twin**: one TU, one exported
symbol, the render inlined into the `__one` loop. This is what §R2.7's fused
convenience would emit.

| arm | what |
|---|---|
| `SEP` | the shipped glue, batch element in another TU (static link) |
| `SEP-PLT` | the same with the element in a `-fPIC` shared object |
| `K1` | the shipped glue with the batch forced to 1 (the per-match shape) |
| `COMP` | the composite twin |
| `SEP'`, `COMP'` | A/A repeats; floor = max(\|median ratio − 1\|, IQR/median) per ratio (D165's convention) |
| `PCRE2` | `pcre2_substitute(GLOBAL)`: an external row, reported, never gated |

| cell | why |
|---|---|
| `a` → `b` over 1 MiB of `a` | the densest case: the call cost is all there is |
| `(\w+)` → `<$1>` over prose | ordinary density |
| `$1` at `ncaps ≈ 30` | the caps buffer's width, and the batch at `kmax = 8` |
| `${w}` named, dense | the run walk's two loads |
| `limit = 4` on a dense subject | fetch count = 4 exactly (a correctness check run in the timing harness) |

**Gate.** `SEP/COMP <= 1 + floor` on the two dense cells. A loss builds §R2.7's
fused composite, which is Q-F2's trigger. `K1/SEP` is a diagnostic. It reports
how much the batch shape is worth, and gates nothing. The cell is quiet-gated
and queued like the I4 parity cell. The thresholds are UNMEASURED DEFAULTS
until the first run.

### R3.14 The two probes

**Probe 1: does the iterator TERMINATE on both backward-span patterns?** YES.
It drove `<p>_next` directly with a cap of `4n + 16` iterations (a cap hit
would be non-termination), then `RX_FOREACH` under the same cap.

- Short subjects. `x(?=(?1))|(b\K)` on `"xb"` gives `[2,1)` and ends with `rc 0`;
  on `"bxbx"`, `[1,1) [3,2)`. `x|(?<=(?1))y|(\Kx)` on `"xy"` gives
  `[0,1) [0,2)` and ends with `rc 0`; on `"xyxyyx"`, five matches.
- Long subjects. The units `xb`, `xy`, `xyb`, `bx`, `xxyy` and `xbxy` were each
  repeated 1,000 and 100,000 times (up to 400,000 bytes). Every run ENDED with
  `rc 0`. Every match count is at most `n` (for example, `k1` on `'xb'x100000`
  gives 100,000 matches, all backward; `k2` on `'xxyy'x100000` gives 300,000
  matches, 100,000 of them starting before the previous end). `RX_FOREACH`
  gave the same counts. No cap was hit.
- **Probe 1c, the corner.** `^|(?<=(?1))y|(?!)(\Kz)` on `"zy"`: the iterator
  gives `[0,0) [0,2)`, `pcre2_match` from 1 gives `[0,2)`, and
  `pcre2_substitute(GLOBAL)` gives −60. This is §R3.6's corner witness.

The iterator is lane/i2build's (unmerged). This lane reports the result and
changes nothing there. Termination is by construction: `lo` never decreases,
and each search starts at or after it.

**Probe 2: the iterator on an ill-formed UTF-8 subject** (crit1-5). It is
CONSISTENT with match_api §9 as written, and with `_search` in a loop. It is
NOT a defect candidate. Over 15 cells (`x*`, `''` and `a|x*`, under `-e utf8`,
on `"a\xffb"`, `"a\xe3b"`, `"a\x80b"`, `"\xff"` and `"a\xe3\x81b"`):

- the iterator, the match_api §3.1.3 `_search` loop and a per-position `_search`
  agree on all 15. `x*` on `"a\xffb"` gives `(0,0) (1,1) (2,2) (3,3)`. A stray
  continuation start is refused (`rc -7` at that position) and skipped, per
  §9.2 and §9.5;
- match_api §9.3¶1 says "an ill-formed LEAD byte (`0xFF`, a truncated `0xE3`) is
  a valid start and is attempted", and the empty match at 1 is exactly that;
- **libpcre2's single searches agree with pcrec's at every offset.** Under
  `PCRE2_UTF|PCRE2_MATCH_INVALID_UTF`, `x*` and `''` from offsets 0-3 of
  `"a\xffb"` and of `"a\xe3b"` give `(0,0) (1,1) (2,2) (3,3)`;
- **PCRE2's global iteration differs on 6 of 15 cells**, the three with an
  interior ill-formed lead byte (`"a\xffb"`, `"a\xe3b"`, `"a\xe3\x81b"`) for
  `x*` and for `''`. It reports 3 matches, none at 1. The cause is located: its
  NOTEMPTY_ATSTART|ANCHORED retry at offset 0 returns `(2,2)`, a match NOT at
  the anchor, past the invalid byte. So PCRE2's loop never searches from 1.
  This is the class match_api §9.3¶3 already states for the anchored entries
  (libpcre2 under `PCRE2_ANCHORED` reports a match at a moved start; pcrec's
  anchored contract cannot). `a|x*`, whose retry is not needed, agrees on all
  five subjects.

So the corpus pins the iterator's answer as STATED behaviour: `sg` cells with
`x*` → `[$0]` on `"a\xffb"` giving `[]a[]\xff[]b[]`, 4 substitutions. The
oracle column records libpcre2's 3 as the known difference. One spec candidate
goes to the manager: match_api §3.8¶2 says "the matches are PCRE2's global
iteration's" without the ill-formed exception, and its phase-B hunk should cite
§9.3¶3's class.

### R3.15 The standing questions, what R3 changes

1. **Measurement regime.** R3 adds no number. §R3.13's cell names its regime:
   dense independent matches, one thread, the dev box, gcc 15.2, the quiet
   gate, and D165's floors. The two probes are ANSWERS (spans, counts,
   termination), not timings.
2. **Independent control.** The corpus oracle stays `pcre2_substitute`. Where
   pcrec differs by design, the expectation is pcrec's stated behaviour and the
   cell carries PCRE2's answer beside it: §R3.10 rows 1, 6, 9 and 11, each with
   a witness. The run-walk cell is controlled by PCRE2's own duplicate-name
   answer. The BADSPAN cells are controlled by PCRE2's −60. The PROPOSED
   sabotage rows for phase B (S1346-S1355) are listed in the review file's
   candidates. Their witnesses and reach counts are owed at build.
3. **What moves when regenerated.** No rx artifact moves at landing. After
   landing, a change to the subst block is an rx abi event (§R3.8).

### R3.16 Open questions, restated after R3

**[R4: Q-F2 and Q-F3 are CLOSED by ruling 4 and the recipes; Q-F1 is answered by ruling 1 (independent, optional map); Q-F4 stands with §R4.8's added term. Frank's open items are §R4.9]**

For Frank, in plain words, with the leaning first. These four are unchanged in
substance, and their leanings are updated:

- **Q-F1. When does a template meet its rx?** Leaning: once, at run time,
  before any output, by filling a small binding from the rx's record. This
  works for any rx whose group names fit, including one where the same name
  occurs twice. Numbered groups cost nothing extra. The new constraint is that
  the template and the rx must come from the same pcrec build, and both the
  compiler and the bind check it. An optional build-time check exists when the
  user names the pattern.
- **Q-F2. Should a one-symbol "substitute with this pattern" function also
  ship?** Leaning, stronger than before: no, unless the timing cell shows the
  separate pieces losing to it on dense matches. The pieces now hand over up to
  64 matches per call instead of one, so the remaining difference is only that
  the fused form can inline the rendering into the match loop. If it ever
  ships, it is built from the same two pieces.
- **Q-F3. First vs all.** Leaning: one function with a "how many" argument
  (1 = first, unlimited = all). The argument now also caps how far the
  iterator runs ahead, so "first" does exactly one search.
- **Q-F4. In-place substitution.** Leaning: the contract is written down and
  built only when someone asks. The out-of-place rule is now explicit: the
  output may not overlap the subject.

For the manager, R3 closes the five: Q-M1 (unspecified, §R3.9), Q-M2 (allowed,
the `ref` column, §R3.2), Q-M3 (shared abi; own number to [IFACE-PUSH], §R3.8),
Q-M4 (§R3.5's table) and Q-M5 (no, §R3.12). One new item: whether
`PCREC_SUBST_PAIRS`'s 256, copied from `RX_FOREACH_PAIRS`, should be measured
in §R3.13. It is an unmeasured default and is labelled as one.

---

## REVISION 2 — compiled substitution as an INDEPENDENT ELEMENT (lane subst, 2026-10-21) — READ §R3 FIRST

**Status: PROPOSED, design only.** Nothing under `src/`, `cli/`, `lib/` or
`tests/` was touched. The probe behind every **[MEASURED]** claim below is
`subst_measurements/` (`glue.c`, `run.sh`, `transcript.txt`), run on the
Linux dev box against libpcre2 10.46 at the head of lane/i2build (abi 84).

### R2.0 Why this revision exists

Frank, 2026-10-21 (to be filed as D173):

> "for substitution: it would be another entry item or a wrapper for a
> specific rx? i'd try to make it an independent element that can use an rx
> of the right shape but not a specific rx. i suspect that the
> rx/substituion relationship is either 1:N or even M:N. also, it might be
> good to allow glue between rx and sub. i guess what i am saying is to not
> presume interdependency if modularity is cheap. i think the best bet is an
> almost independent piece that turns a substitution spec into a function
> that runs like { while (next(...)) compiled_subst(subject, offsets,
> target). ...} (for discussion, not specifying). consider its interface
> with the iterators you just wrote."

This supersedes the `[M4-SUBST]` charter's *"pattern AND replacement
template compiled together into one emitted C function (match + splice)"*,
which both this note (§0) and `subst_template_design.md` (§1, §5) were built
on. The template LANGUAGE those notes ruled is untouched. What changes is the
COUPLING: who owns the loop, where references are resolved, and what is one
artifact.

**Verdict, up front.** Modularity is cheap here, and the STOP RULE did not
fire. The find-all iterator already IS the hard half of the old design: its
iteration is PCRE2's global iteration (`match_api.md` §3.8¶2), so the emitted
substitution loop with its measured empty-match machinery (`subst_template_design.md`
§6) no longer needs to exist. A substitution element then needs only (a) the
rx's SHAPE, which `rx_info` already publishes, and (b) a render function per
template. The probe joins the two through a 40-line generic glue and agrees
with `pcre2_substitute` on every cell tried (R2.3). The one cost found is one
out-of-TU call per match plus one table load per NAMED reference. It is
unmeasured and of the same class as the iterator's accepted fixed cost (D171).
R2.8 names the measurement that would justify a fused form, and that fused
form is a composition of the same two elements, not a third mechanism.

### R2.1 What was stale — the design of record against today's tree

`subst_template_design.md` was written 2026-08-14, before M4 shipped
(2026-08-18) and two months before the find-all iterator (D165, I1/I4,
2026-10-13..21). This note's own §1-§5 (2026-09-23) inherited its frame. Each
row is one claim; the disposition is **STANDS**, **SUPERSEDED** (by Frank's
direction), **CLOSED** (the tree now answers it), **MOVED** (same promise,
different time or place) or **DUE** (deferred until something that has now
shipped).

| # | claim of record | where | today | disposition |
|---|---|---|---|---|
| 1 | pattern and template compiled together into one function | charter; std §1, §5; this note §0 | Frank 2026-10-21 | **SUPERSEDED** — R2.2 |
| 2 | C1-C11, the capture-offset contract | std §2 | all delivered: `<PREFIX>_NCAPS` (C1, C7), `caps[0]` the whole match (C3), `PCREC_UNSET` (C5), every pair written (C6, `match_api.md` §5¶4), stable until reuse (C8, §5¶8), the `groups[]` index (C10/D39, §5.4) | **STANDS**, and is now the bind's input |
| 3 | `rx_span`, `RX_NCAPS`, `RX_UNSET`, `rx_subst(s, n, out, outlen)` | std §5.2, this note §4.1 | `rx_span` retired (D44.2); `<PREFIX>_NCAPS`, `PCREC_UNSET`; no per-pattern subst entry | **SUPERSEDED** — R2.4 |
| 4 | group count from `--count-groups` at template compile | std §1, §8.3 | `rx_info.ncaps` / `ngroups` / `nnames` / `groups` at run time (§6 rows 4-6, 18, 24) | **MOVED** — the bind reads `rx_info` (R2.2) |
| 5 | the emitted global loop and its measured empty-match rule | std §6.1, §6.2; this note §3.8 | the iterator's iteration IS PCRE2's global iteration, retry included (§3.8¶2); `\G`, UTF stepping and stray continuation bytes are its own (§3.8¶2, §3.1.3¶4) | **CLOSED** — [MEASURED] R2.3: std §6.1's cells, the `\|a` and `x*\|y` retry cells and `ab\K` agree with `pcre2_substitute` byte for byte |
| 6 | this note §3.8's "seam": the substitution loop is NOT §3.1.3's caller loop plus a splice | this note §3.8 | the iterator carries the retry; §3.1.3's lossy loop is no longer the alternative | **CLOSED** — the seam was real against §3.1.3, and the iterator removed it |
| 7 | first vs global as a GENERATION AXIS (two emitted functions) | std §5.3; this note §4.3 | the loop is the iterator's; the element renders ONE match | **SUPERSEDED** — no axis; R2.4's `limit` |
| 8 | several templates over one matcher as entries of one file, `--replace` repeatable | std §5.5; D38 Q7; this note §4.4 | D88 add. 1: one exported call interface per file | **SUPERSEDED** — one template per subst artifact; 1:N and M:N by linking (R2.5) |
| 9 | references resolved and bounds-checked AT COMPILE TIME | charter; std §4 | there is no rx at template-compile time | **MOVED** — resolved ONCE at bind, before any substitution (R2.2); the D26 promise ("never discovered at substitute time") holds |
| 10 | `--no-captures` × a `$n` template is a compile-time error | D44.7; `match_api_m4.md` §11 item 12 | the template no longer sees the rx's options | **MOVED** — a bind refusal: the rx delivers no slot for group n (`ncaps == 1`) |
| 11 | duplicate names (`(?J)`) deferred to module `named-groups` | D38 Q10 | `named-groups` and `(?J)` shipped; §5.4¶5-¶6 publish the run and the "first that participated" algorithm `\k<name>` uses | **DUE** — R2.2 binds a name to its run; render applies §5.4¶6 |
| 12 | `${name}` gated on module `named-groups` | std §3.1, C10 | shipped | **MOVED** — the gate is on the RX (it must have been compiled with the module to have names); the template compiler needs no module to spell `${name}` |
| 13 | the template language: tiers `subst` / `subst-extended` / `subst-pcrec`; §3.2's grammar corners; §3.3's case forcing; §7.1's namespace rule; Q1 `$0` core; Q2 bare `$name`; Q3 unset = generation axis, default empty; Q4 length-only, no NUL; Q5 `${!...}`; Q8 the which-input error tag; Q9 encoding-blind; Q11 exact sizing; Q13 `rx_renderfn` | std §3, §7; D38 | unchanged by the coupling | **STANDS** — all of it is about the template, not about who loops |
| 14 | Q12 (`rx_span` breaks), Q14 (`unsigned char` subject) | D38 | applied at M4 | **CLOSED** |
| 15 | `rx_subst(..., vars, nvars)`, the pair per entry | this note §4.2; `variables_roadmap.md` M9 | the pattern side binds variables ONCE per find-all (`rx_iter_vars`, §3.8¶4); `rx_ctx` carries `vars`/`nvars` | **SUPERSEDED** — the glue hands the iterator's binding to the render through `rx_ctx` (R2.4): one array, bound once, both consumers |
| 16 | streaming holdback stamped from `maxw`; a var-bearing pattern refuses streaming | plan row (2026-09-06); this note §5 Q6 | no chunked iterator exists ([M3], [ITER-BLOCK]) | **STANDS**, and gains one term (R2.6): a referenced group may lie before the reported start |
| 17 | in-place is free when replacement ≤ match | plan row (2026-09-06) | the iterator forbids changing `s[0, n)` while live (§3.8¶8); lookbehind reads before `lo`; a group may lie before the match | **STANDS AS A GOAL, CONTRACT RESTATED** — R2.6 |
| 18 | `rx_renderfn` reserved, no producer | `match_api.md` §2¶7 | still no producer | **STANDS** — template segments still use it; the element's own render is renderfn-shaped plus a binding (R2.4) |

### R2.2 What a shape is, and when a template binds to one

**The shape an rx OFFERS** is exactly what `rx_info` already publishes and
nothing more:

- `ncaps`: the caps slots this build delivers (1 on a DFA or `--no-captures`
  build);
- `ngroups`: the pattern's own group count. By D61's permanent-prefix promise
  (§6¶4), slot `k` IS group `k` for `1 <= k <= ngroups` on every captures-on
  build, a composed one included;
- `groups[0 .. nnames)`: the caller-scope name index, sorted, each row
  `{name, number, slot}`, with duplicate names as a run (§5.4¶5). Rows
  `[nnames, nentries)` are a composed artifact's site-scoped `site.group`
  names (§5.5).

**The shape a template NEEDS** is its reference list: the group NUMBERS it
names (`$k`, `${k}`) and the group NAMES it names (`${name}`, `$name`).

**[R3: this table is SUPERSEDED by §R3.2's satisfaction table (the needed shape as `rx_group_entry` rows; names bind to runs).]**

**Satisfaction** (the rule the bind applies):

| reference | satisfied when | slot used |
|---|---|---|
| `$0` | always (`ncaps >= 1`, §5¶2) | 0 |
| `$k`, `k >= 1` | `k <= ngroups` and `k < ncaps` | `k` (D61) — a CONSTANT in the emitted render |
| `${name}` | `name` has a run in `groups[0 .. nnames)` and every row of the run has `slot >= 0` | the run, resolved once |

A failed row is a refusal that names the reference, the rx (`rx_info.name`)
and what the rx does offer. That is the old §4.2 diagnostic's content, one
step later.

**When.** **[PROPOSED]** ONE mechanism: references are resolved at BIND, once
per (rx, subst) pair, before the first substitution, by generic code reading
the rx's `rx_info`. Three reasons:

1. **It is the general form.** A template bound at compile time to one
   declared shape could not serve two rx whose names sit in different slots.
   The probe's M:N cell is that case: `${y}.${m}` over `(?<y>\d+)-(?<m>\d+)`
   and over `(?<m>\d+)/(?<y>\d+)`, one render, two bindings, both
   oracle-exact.
2. **It is cheap where it matters.** Numbered references need no table: D61
   makes slot `k` constant, so `$1` compiles to `caps[1]` exactly as in the
   fused design. Only NAMED references read a slot from the binding, one
   L1-resident `int` load per reference per match.
3. **The D26/AOT promise survives intact.** PCRE2 finds an unknown group at
   substitute time (`-49`, std §4.1). Here it surfaces at bind, once, before
   any output is produced. The probe's shape cell is PCRE2's `-49` class
   refused at bind.

**A build-time check is an INPUT, not a second mechanism.** `--shape-from
PATTERN` (or a `.rxt` `for TARGET`, R2.7) runs the SAME resolver against a
pattern's shape at subst compile time. That gives the build-time diagnostic
std §4.2 wanted, including "list what does exist", for the common case where
the user knows the rx. The run-time bind still runs and still decides. A
caller who includes the rx's header may also write
`_Static_assert(RX_NCAPS > DMY_MAXNUM, ...)`, because numbers have macros.
Names do not, and nothing here adds name macros.

**Not proposed: pinning name slots as constants at compile time.** Its only
gain is the one `int` load per named reference. Trigger: phase B's timing
cell (R2.8) shows that load measurable on a dense named-reference cell.

**[R3: the paragraph below is right about the rule and wrong about the binding: a single slot per name cannot hold a run (crit1-2). SUPERSEDED by §R3.2's (first, count) run.]**

**Duplicate names** (row 11, now DUE). A name binds to its RUN. The render
applies §5.4¶6, "the first member that participated", which is PCRE2's rule
and the same algorithm the emitted `\k<name>` uses, so caller, matcher and
substitution cannot disagree. A run of one, the common case, is a single slot.

### R2.3 [MEASURED] the glue over today's iterator, against `pcre2_substitute`

`subst_measurements/glue.c` compiles nine artifacts with the lane's pcrec. It
binds hand-written renders (stand-ins for what the template compiler would
emit) through `rx_info`, runs the generic glue of R2.4, and compares each cell
with libpcre2 10.46 `pcre2_substitute(GLOBAL | UNSET_EMPTY |
OVERFLOW_LENGTH)`. Every cell also runs the sizing pass (`out == NULL`) on a
copy of the fresh iterator (§3.8¶10) and checks that it reports the produced
length.

| cell | rx | template | subject | output (pcrec = pcre2) | count |
|---|---|---|---|---|---|
| std §6.1 | `a*` | `[$0]` | `bab` | `[]b[a][]b[]` | 4 |
| std §6.1 | `a*` | `[$0]` | `aab` | `[aa][]b[]` | 3 |
| retry (§3.1.3¶9's lossy class) | `\|a` | `[$0]` | `aaa` | `[][a][][a][][a][]` | 7 |
| retry | `x*\|y` | `[$0]` | `xyy` | `[x][][y][][y][]` | 6 |
| `\K` | `ab\K` | `[$0]` | `ababab` | `ab[]ab[]ab[]` | 3 |
| unset group (Q3 default empty) | `(a)\|(b)` | `[$1\|$2]` | `xaby` | `x[a\|][\|b]y` | 2 |
| group | `(a+)b` | `<$1>` | `xaabzaab` | `x<aa>z<aa>` | 2 |
| group before the match | `(?<=(a))b` | `<$1>` | `abab` | `a<a>a<a>` | 2 |
| 1:N (second subst, same rx) | `(a)\|(b)` | `[$0]` | `xaby` | `x[a][b]y` | 2 |
| M:N (named) | `(?<y>\d+)-(?<m>\d+)` | `${y}.${m}` | `on 2026-10 and 2027-11.` | `on 2026.10 and 2027.11.` | 2 |
| M:N (same subst, other order) | `(?<m>\d+)/(?<y>\d+)` | `${y}.${m}` | `on 10/2026 and 11/2027.` | `on 2026.10 and 2027.11.` | 2 |
| shape refusal | `a*` | `[$1\|$2]` | — | BIND REFUSED (pcre2: `-49`) | — |
| undersized buffer | `a*` | `[$0]` | `bab`, cap 5 | NOSPACE, required 11 | — |

`fails=0` (`transcript.txt`). Scope, stated so nobody reads more into it: 12
cells chosen to hit the rules the design depends on. This is not a corpus.
The renders are hand-written by the same author as the glue, so phase B's
D27 spec-first corpus (std §8.4) is still owed. No timing was taken.

### R2.4 The element, the binding and the glue — the interface

Three pieces, with one owner each:

| piece | emitted where | per | what it knows |
|---|---|---|---|
| **rx** | its own artifact (unchanged) | pattern | how to find matches; publishes its shape in `rx_info` |
| **subst** | its own artifact (NEW) | template | how to render ONE match into bytes; publishes its reference list |
| **glue** | shared code in the subst artifact's header (static inline, prefix-independent, like `RX_FOREACH`) | nothing | gaps, the loop, sizing, the count |

**[R3: `rx_subst_ref`, the per-match `rx_substfn` and `struct rx_subst_info` below are SUPERSEDED by §R3.1 (the batch-shaped element) and §R3.2 (the needed shape as an `rx_group_entry` array).]**

**The subst artifact** (`pcrec -p dmy --subst '${y}.${m}'`, R2.7) exports one
call interface (D88 add. 1): a render function and a record.

```c
/* dmy.h — shared blocks first: the rx block (rx_ctx, rx_iter, rx_info,
 * RX_FOREACH; guarded by PCREC_RX_ABI_H as today) and the subst block below
 * (guarded by its own macro, R2.7 Q-M3). */
typedef struct rx_subst_ref {
    const char *name;     /* NULL for a numbered reference */
    int         number;   /* the group number when name == NULL */
} rx_subst_ref;

/* Renders ONE match. Returns the FULL length of the rendering; writes it to
 * out only when it fits in cap (all or nothing: snprintf's convention), and
 * writes nothing when out is NULL. -1 = a renderer segment failed. slot[] is
 * the binding (one entry per NAMED reference; NULL when there are none);
 * ctx carries the subject, the match's caps, and the variables. */
typedef ptrdiff_t rx_substfn(const int *slot, const rx_ctx *ctx,
                             unsigned char *out, size_t cap);

struct rx_subst_info {
    unsigned            abi;
    const char         *name;          /* the artifact's own name */
    const char         *template_text;
    int                 nrefs;         /* NAMED references: the binding's size */
    const rx_subst_ref *refs;          /* every reference, numbered ones too */
    int                 maxnum;        /* highest $k, or 0 */
    rx_substfn         *render;
};

#define DMY_NREFS  2      /* int slot[DMY_NREFS] is the binding */
#define DMY_MAXNUM 0
extern const struct rx_subst_info dmy_subst_info;
ptrdiff_t dmy_render(const int *slot, const rx_ctx *ctx,
                     unsigned char *out, size_t cap);
```

The render for `${y}.${m}` is straight-line code. It has no template
interpreter and no name lookup. This is what the probe hand-wrote:

```c
ptrdiff_t dmy_render(const int *slot, const rx_ctx *ctx,
                     unsigned char *out, size_t cap)
{
    const ptrdiff_t (*c)[2] = ctx->caps;
    size_t ly = c[slot[0]][0] < 0 ? 0 : (size_t)(c[slot[0]][1] - c[slot[0]][0]);
    size_t lm = c[slot[1]][0] < 0 ? 0 : (size_t)(c[slot[1]][1] - c[slot[1]][0]);
    size_t need = ly + 1 + lm;
    if (out && need <= cap) {
        if (ly) memcpy(out, ctx->subject + c[slot[0]][0], ly);   /* unset: ly == 0 */
        out[ly] = '.';
        if (lm) memcpy(out + ly + 1, ctx->subject + c[slot[1]][0], lm);
    }
    return (ptrdiff_t)need;
}
```

(A `$1` would read `c[1]`, a constant. A duplicated name would walk its run
per §5.4¶6. The unset arm is D38 Q3's axis at its default. The guard keeps
`subject + -1` from ever being formed.)

**[R3: the `int slot[]` binding is SUPERSEDED by §R3.3's `rx_subst_binding` (runs, `ncaps`, identity, segment `user`s).]**

**The binding** is caller-owned, `int slot[<S>_NREFS]`, filled once:

```c
/* 0 = bound; < 0 = refused (abi mismatch, or a reference this rx does not
 * deliver). Never allocates. Reads only rx_info. */
static inline int pcrec_subst_bind(const struct rx_info *rx,
                                   const struct rx_subst_info *sub, int *slot);
```

**[R3: the glue below is SUPERSEDED by §R3.4 (drives `next_n` with a buffer sized from `ncaps`, no over-fetch past `limit`, saturating lengths, `*outlen`/`*nsubst` on every path, the binding carries the rx). Its `rx_ctx` initializer reads `it->vars` on a FRESH iterator (F-R3-1).]**

**The glue** is the loop Frank sketched, made exact:

```c
/* Every match of `it` (FRESH, setters applied), up to `limit` of them, with
 * the gaps copied and each match rendered. Returns the substitution count
 * (>= 0), PCREC_SUBST_NOSPACE with *outlen = the capacity that would have
 * sufficed, a renderer's failure (its code value is Q-M4), or the iterator's
 * own code when it ended with rc < 0. out == NULL: size only. */
static inline ptrdiff_t pcrec_subst(const struct rx_info *rx, rx_iter *it,
                                    const struct rx_subst_info *sub,
                                    const int *slot, size_t limit,
                                    unsigned char *out, size_t cap,
                                    size_t *outlen)
{
    const unsigned char *s = it->s;
    size_t n = it->n, w = 0, prev = 0;
    ptrdiff_t count = 0;
    int fits = out != NULL;
    rx_ctx ctx = { s, n, 0, (size_t)rx->ncaps, NULL, NULL, it->vars, it->nvars };
    if (limit == 0) goto tail;
    RX_FOREACH(rx, it, m) {
        size_t st = (size_t)m[0][0], gap = st - prev;      /* R2.5 rule 1 */
        if (fits && w + gap > cap) fits = 0;
        if (fits) memcpy(out + w, s + prev, gap);
        w += gap;
        ctx.pos = st; ctx.caps = (const ptrdiff_t (*)[2])m;
        ptrdiff_t r = sub->render(slot, &ctx, fits ? out + w : NULL, fits ? cap - w : 0);
        if (r < 0) return r;
        if (fits && w + (size_t)r > cap) fits = 0;
        w += (size_t)r;
        prev = (size_t)m[0][1];
        if ((size_t)++count == limit) goto tail;           /* early exit: §3.8.2¶4 */
    }
    if (it->rc < 0) return it->rc;
tail:
    if (fits && w + (n - prev) > cap) fits = 0;
    if (fits) memcpy(out + w, s + prev, n - prev);
    w += n - prev;
    *outlen = w;
    return (out && !fits) ? PCREC_SUBST_NOSPACE : count;
}
```

A caller doing PCRE2's whole job, `pcre2_substitute(GLOBAL)`, writes:

```c
int slot[DMY_NREFS];
if (pcrec_subst_bind(&ymd_info, &dmy_subst_info, slot) < 0) die("shape");
rx_iter it = RX_ITER_INIT(s, n);
size_t len;
ptrdiff_t k = pcrec_subst(&ymd_info, &it, &dmy_subst_info, slot, SIZE_MAX,
                          out, cap, &len);
```

`limit = 1` is PCRE2's non-global substitution. The first-vs-global
generation axis (row 7) dissolves into one compare per match. The axis existed
to keep the global loop's empty-match machinery out of the first-match path,
and that machinery now lives in the iterator. `RX_FOREACH` starts its batches
at one entry (I4's doubling), so `limit = 1` fetches one match.

**[R3: the two paragraphs below are SUPERSEDED by §R3.9 (the context-init helper, the §3.8¶9 hunk, and F-R3-1: `it->vars` is garbage on a FRESH iterator without `rx_iter_vars`) and §R3.7 (`${!name}` resolved once per call).]**

**What the glue reads that a caller may not.** `it->s`, `it->n`, `it->vars`
and `it->nvars` are fields §3.8¶9 leaves "unspecified to the caller". The glue
is pcrec's own shared code, exactly as `RX_FOREACH` reads `it->hdr`, so phase
B's spec hunk names what the glue relies on (they hold their bound values
while the iterator is FRESH or BOUND), rather than re-passing `s, n` and
reopening D165 add. 2 Q3's "a mismatch is impossible by construction".

**Variables.** A template's `${!name}` (this note §2) reads `ctx->vars`, and
the glue fills `ctx` from the iterator's own binding (`rx_iter_vars`). One
array, bound once per find-all, serves the pattern's variables and the
template's. That supersedes §4.2's per-entry pair (row 15).

**Custom glue is first-class.** Nothing obliges a caller to use
`pcrec_subst`. A caller can call `RX_FOREACH` plus `<s>_render` and emit only
the replacements (a templated `grep -o`), write one JSON line per match,
render two templates per match in one pass, or substitute in a sink. The
element is useful without the glue. This is the modularity Frank asked for,
and it costs the caller nothing they did not choose.

### R2.5 The glue's rules — who does what

**[R3: rule 1 is FALSE as written (panel crit1-1, BLOCKER): a `\K` reached through a subroutine call from a lookaround reports backward and overlapping spans. SUPERSEDED by §R3.6 (the element checks every span, `PCREC_SUBST_BADSPAN`); the spec sentence proposed at its end is WITHDRAWN.]**

1. **Gaps are the glue's.** It copies `[prev_end, start)` before each match and
   `[last_end, n)` at the end. This needs reported spans ORDERED and
   NON-OVERLAPPING: each one starts at or after the previous one's end. That
   holds by construction. Every search starts at `lo`, which is at least the
   previous end. `\K` only moves a reported start later (§3.1¶16). `\K` inside
   a lookaround is refused (as in PCRE2), so `start <= end`. The `ab\K` cell
   witnesses it. **But the spec never says it in one sentence.** Phase B adds
   it to §3.8 as a stated property of the iteration (a spec hunk, not an
   emitted change).
2. **The empty-match rule is the iterator's**, not the glue's (rows 5 and 6).
   The glue has no branch on empty spans.
3. **A group may lie OUTSIDE the reported span.** A lookbehind capture
   (`(?<=(a))b`) or a group before `\K` precedes the start. The render reads
   the subject, not the gap, so buffer mode is unaffected (the `lbcap` cell),
   but in-place and streaming must account for it (R2.6).
**[R4: rule 4 is SUPERSEDED: pieces are sized before any write and no match is searched twice (§R4.5).]**
4. **Sizing is single-pass by default.** The glue writes while the output
   fits, keeps counting past the overflow and always reports the capacity
   required. This is PCRE2's `OVERFLOW_LENGTH` behaviour made unconditional,
   which is D38 Q4/Q11's ruled contract unchanged. A caller who wants exact
   pre-sizing copies the FRESH iterator (§3.8¶10) and runs once with `out ==
   NULL`. That costs a second match pass, the caller's choice. There is no
   general bound without matching: an empty-matching rx substitutes `n + 1`
   times.
5. **A failure mid-way** (a give-up from the iterator, or a renderer's `-1`)
   returns its code. **[PROPOSED]** the output buffer's contents are then
   UNSPECIFIED, as PCRE2's are on error, and a caller who needs the subject
   intact substitutes out of place (Q-M1).
   **[R3: rule 5 is decided: §R3.5's codes, `out` unspecified (§R3.9).]**
6. **Unset groups render per the template's Q3 axis** (default empty), decided
   when the subst is compiled.
7. **Output is length-only, no NUL** (D38 Q4), 8-bit clean.

### R2.6 In-place and streaming — the honest contract

**[R4: stands, with §R4.8's added term: a write must also land below every unconsumed piece's source]**

**In-place** (the 2026-09-06 charter's mode (1)). The idea "free when
replacement ≤ match" is true for the write cursor against the gaps, but three
facts of today's tree make it a contract rather than a free mode:

- The iterator says `s[0, n)` must not change while it is live (§3.8¶8,
  UNDEFINED). In-place writes into `s`.
- The matcher reads behind `lo`: lookbehind, `\b`, and a `\K` match whose
  reading began before its reported start. The bound on how far it reads is
  the pattern's BACK-REACH, not LB: LB (`<prefix>_VALID_LB`, §9.4) is the
  lookbehind width the UTF check covers, and `\K` and a lookbehind nested in
  a lookahead both read past it (substfix correction, 2026-10-22). Neither
  number is in `rx_info` today.
- The render reads referenced groups, and by R2.5 rule 3 these may lie before
  the reported start.

The sufficient rule is that every write lands below every byte still to be
read: below `lo − back-reach` for the next search, and below the lowest
referenced group start of the current match. The glue can check this per match before
writing (sizing the render first with `out == NULL`). It needs three things:
a §3.8¶8 relaxation ("bytes below `lo − back-reach` may change"), the
back-reach published in `rx_info` (an abi event; unbounded for a pattern
whose reach is not finite, which then refuses in-place), and a rule for what
happens when the check fails
mid-subject. **[PROPOSED]** ROADMAP, with this contract recorded so the build
does not discover it (D77). Trigger: a user ask, or a measured need where the
out-of-place copy dominates. Pure deletion (an empty template) always
satisfies the write rule, and is the obvious first instance.

**Streaming** (mode (2)) needs a CHUNKED iterator, which is [M3]'s, with
[ITER-BLOCK] as its nearest sibling. The element needs no change: a render
reads `ctx->subject` at absolute offsets, and a window glue rebases them. The
holdback the plan row stamps from `maxw` gains one term: the back-reach
(above), which also bounds any referenced group before the start, because a
group can only precede the start through lookbehind or `\K`. The templates'
`$_`, `` $` `` and `$'` (subst_api.md §2¶1) read the WHOLE subject, so a
template carrying one refuses streaming as a var-bearing pattern does. This note's Q6 (a
var-bearing pattern refuses streaming) stands. D38 §7.2's sink form
`rx_subst_to(sink)` becomes a GLUE variant (`pcrec_subst_to`): no element
change, which is the point of the split.

### R2.7 The CLI and emission surface

- **A subst artifact is its own artifact.** It has its own `-p` prefix, its
  own `.c`/`.h`, one exported call interface (`<s>_render` + `<s>_subst_info`),
  and no pattern. That satisfies D88 add. 1 as written. It is NOT an
  [EMIT-ENTRIES] unit of an rx artifact, because a second exported interface
  in the rx's file is exactly what D88 add. 1 forbids.
- **CLI** (spelling is the manager's call): `pcrec -p dmy --subst TEMPLATE -o
  dmy.c`, exclusive with `--pattern`. Optional `--shape-from PATTERN` gives the
  build-time check (R2.2), and `--unset=empty|...` is D38 Q3's axis. D38 Q7's
  repeatable `--replace` on an rx compile is retired (row 8).
- **`.rxt` source world** (D118, [DD-13b]): a `subst` target kind, with an
  optional `for TARGET` that runs the build-time check against a sibling
  target's shape. std §8.1's `repl`/`s`/`sg`/`serr` test lines carry over as
  the corpus form, with `sg` driving the glue at `SIZE_MAX` and `s` at
  `limit = 1`.
- **Library**: the template is a second kind of compile input.
  `pcrec_err_input`'s `PCREC_ERR_INPUT_TEMPLATE` is already in `lib/pcrec.h`
  (D38 Q8) and finally gets its producer. The entry's shape is phase B's,
  under [IFACE-PUSH]'s one-push rule.
**[R3: the bullet below on the subst block's versioning is decided by §R3.8 (same build, shared abi); the header layout and include order are §R3.11.]**

- **The rx artifact does not change.** The subst block (types, bind, glue)
  lives only in subst headers, which include a copy of the rx shared block
  under its existing guard. Its `#error` on an abi mismatch already refuses a
  subst and an rx built by pcrecs of different abi in one TU. The bind
  re-checks `rx->abi` at run time for the `dlopen` case. So phase B is **not
  an rx abi event**, and today's artifacts stay byte-identical. The subst
  block's own versioning is Q-M3.
- **The FUSED convenience** (D38's old shape, `<p>_subst(s, n, out, &outlen)`
  in one symbol) is still reachable, as a D163 COMPOSITE: one file exporting
  one interface, holding a private rx and a private subst, built from the
  same two elements by the same composition machinery. It is not a third
  mechanism. **[PROPOSED]** not built until R2.8's measurement or a user ask.

**[R3: this table is SUPERSEDED by §R3.1's restated cost (one call per BATCH, two loads per named reference) and §R3.13's rebuilt timing cell; the closing paragraph's "two spec clarifications" lose the first (§R3.6: no ordering sentence in §3.8).]**

### R2.8 What modularity costs — named, and the measurement that would act on it

| cost | size | measured? | the trigger to act |
|---|---|---|---|
| one call per match into another TU (`sub->render` through a pointer in the glue; a direct call from a hand loop) | about 1-2 ns per match, the class of D171's accepted iterator setup cost | **NO** — structural estimate | phase B's timing cell: `a` → `b` over 1 MiB of `a` (densest) and `(\w+)` → `<$1>` over prose, separated against a hand-fused twin (render inlined into the loop). A dense-cell loss beyond noise under D165's parity-gate convention builds R2.7's fused composite |
| one `int` load per NAMED reference per match | one L1 hit | **NO** | the same cell with `${name}`; a loss → compile-time slot pinning against a declared shape (R2.2's "not proposed") |
| the template can no longer tell the rx compiler which groups it needs (a fused compile could capture only `$2`, or pick the DFA when only `$0` is used) | a VM-vs-DFA difference when the template uses only `$0` | n/a | none needed today: a `$0`-only template binds to a `--no-captures` (DFA) rx, and the bind refuses the unsafe pairing. A partial-capture rx option ("deliver only these groups") would serve fused and separated alike. It does not exist; noted, not filed (D77) |

Nothing else found. No row of the iterator's contract contradicts the
independent element. The two spec needs (R2.5 rule 1's ordering sentence,
R2.4's fields the glue reads) are clarifications, not changes.

### R2.9 What of D38 still stands

Everything about the TEMPLATE: the three module tiers, the grammar corners,
case forcing as an output-stream operator, the `${!...}` namespace rule, bare
`$name`, `$0` core, unset as a generation axis (default empty), length-only
output with the capacity always reported, exact sizing with `rx_renderfn`'s
`out == NULL` convention, the which-input error tag, encoding-blindness, and
`rx_renderfn` itself. Everything about the COUPLING is superseded: one
function per (pattern, template), first/global as an axis, repeatable
`--replace` on an rx, and compile-time resolution against the pattern being
compiled (MOVED to bind, same promise). The emitted loop is CLOSED by the
iterator.

### R2.10 The three standing questions (`docs/design/CLAUDE.md`)

1. **Measurement regime — relevant.** R2.3's numbers are ANSWERS (bytes and
   counts), not timings, so the regime does not flip them. Every timing claim
   in R2.8 is marked unmeasured, and the phase-B cell is named with its
   regime: dense independent matches, one thread, the dev box, gcc 15.2, the
   D165 parity convention.
2. **Independent control — relevant.** The oracle is libpcre2's own
   `pcre2_substitute`, a different implementation of the whole job (loop,
   retry, splice). It shares nothing with the iterator or the glue. python
   `re.sub` is the second oracle std §8.2 established, and its unset
   rendering matches the Q3 default (re-checked: `(a)|(b)` → `x[a|][|b]y`).
   The population is 12 cells plus 1, counted by the probe's own
   `fails=` line. The renders were hand-written by the glue's author, which is
   the residual dependence, and why std §8.4's D27 corpus stays owed in phase
   B.
3. **What moves when regenerated — relevant, and mostly nothing.** rx
   artifacts do not move (R2.7). A subst artifact is new emitted text with its
   own identity pins in phase B. If the subst block takes the shared abi
   number rather than its own (Q-M3), every rx artifact's abi readers move in
   phase B's commit. That is the cost Q-M3 weighs.
   **[R3: item 3's open choice is made: the shared abi, no own number (§R3.8).]**

### R2.11 Open questions

For Frank (plain words, leaning first):

- **Q-F1. When does a template meet its rx?** Leaning: once, at run time,
  through the rx's reflection record, before any substitution. This works
  for any rx with the right group names, and numbered groups cost nothing
  extra. An optional build-time check is available when the user names the
  pattern. The alternative bakes the slots in at template compile, which ties
  the template to one group layout.
- **Q-F2. Should the one-symbol "substitute with this pattern" function also
  ship?** Leaning: not until phase B's timing shows the separate pieces losing
  on dense matches, or someone asks. When it ships, it is built from the same
  two pieces.
- **Q-F3. First vs all.** Leaning: one substitution function with a "how many"
  argument (1 = first, unlimited = all) instead of two emitted functions. The
  reason for two functions is gone now that the iterator owns the loop.
- **Q-F4. In-place substitution.** Leaning: write the contract down now (R2.6)
  and build it on an ask. It needs a relaxation of the iterator's "subject
  must not change" rule and a published lookbehind width.

**[R3: Q-M1..Q-M5 below are CLOSED by §R3.16; Frank's Q-F1..Q-F4 above are restated there with updated leanings.]**

For the manager:

- **Q-M1.** Output contents after a mid-way failure: unspecified (leaning,
  PCRE2's own stance) or "the prefix written so far is valid".
- **Q-M2.** Delivered composed groups by name (`${a.local}`): allow (leaning).
  They are only addressable by name (§5.5¶5). The spelling is a PCRE2 error
  today, so it sits inside D38 Q5's rule.
- **Q-M3.** The subst block's version: its own number (leaning, so rx
  artifacts never move for a subst change) or the shared artifact abi.
- **Q-M4.** The code values: `PCREC_SUBST_NOSPACE` and the renderer-failure
  code, below `PCREC_ERR_FLOOR` beside `PCREC_ERR_ITER` (leaning) or D38's
  `-1`. The probe used `-1` for NOSPACE, and a renderer's `-1` passes
  through the glue unchanged, so the two collide there: the values must
  differ.
- **Q-M5.** Whether `rx_substfn` should BE `rx_renderfn`, with the binding
  carried in `ctx->user`. That would let a compiled subst act as a segment of
  another template. Leaning no: `user` belongs to the template's own renderer
  segments, and overloading it makes the two compete.

---


## 0. Read this section before any other

> **SUPERSEDED IN PART by §R2 (2026-10-21).** The scope quoted below
> ("pattern AND replacement template compiled together into one emitted C
> function") is superseded by Frank's 2026-10-21 direction; see §R2.1 rows
> 1 and 7-9. The rest of this section (the variable layer is the new thing)
> stands.

**This note does not design substitution. `docs/design/subst_template_design.md`
already did, and D38 (2026-08-14) ruled all fourteen of its open questions.**
That note is 1,256 lines, its measurements were taken against libpcre2 10.46
with twelve predictions stated before the first run, and three of them were
refuted. It is the design of record for `[M4-SUBST]`.

Its scope, in its own words: *the `pcre2_substitute` capability as an AOT
artifact — pattern AND replacement template compiled together into one emitted
C function (match + splice), first/global modes, caller-buffer zero-allocation
mode plus an output-sizing mode.*

So this note's actual job is narrow and it is stated here so nobody re-opens
settled ground:

1. **§1 records what is already ruled**, in a table, so a reader can tell at a
   glance which parts of the charter are asking for something that exists.
2. **§2 adds the one genuinely new thing**: the caller's variable environment
   reaching the replacement side, which `subst_template_design.md` predates
   and does not contemplate.
3. **§3 answers the charter's brainstorm list** against that baseline, one
   verdict per item.
4. **§4 settles the call interface** with variables in it, against §5.2's
   ruled surface.

**Three findings decided the shape of this note**, and each corrects a premise
in the charter:

- **The shell style and PCRE2's `SUBSTITUTE_EXTENDED` style are the same
  style** (§1.2). `${n:-default}` and `${n:+alt}` are bash's operators,
  spelled identically, because PCRE2 borrowed them from shell. The charter
  asks me to "pick the pcrec syntax = the shell style... and state every
  departure from PCRE2." For those two forms there is no departure to state;
  they are already ruled in, verbatim.
- **"Callouts that return strings? I think we support that" — the callout ABI
  does not, and a different, already-ruled mechanism does** (§3.1). Callouts
  are match-or-fail only, ruled at D38 and enforced at every generated call
  site with `__builtin_trap()`. The string-returning sibling is `rx_renderfn`,
  ruled at D38 Q13, already carried in `docs/spec/match_api.md` §2, with its
  `out == NULL` sizing convention already specified. It is designed and
  reserved, not built — which is a different answer from "we support that."
- **The two-call overflow protocol the charter asks me to weigh is the one
  PCRE2 shape D38 deliberately declined** (§4.1), and the ruled replacement is
  strictly better: one function, `out == NULL` for sizing, the required
  capacity *always* reported. There is no argument left to have; there is a
  ruling to cite.

---

## 1. What is already ruled

### 1.1 The rulings, as a table

Every row is **[RATIFIED]**. Section numbers are into
`subst_template_design.md`; question numbers are its §9, all ruled by D38.

| topic | ruled | where |
|---|---|---|
| `$0` / `${0}` is the whole match | core tier | Q1 |
| `$n` / `${n}` is capture group *n* | core tier, resolved and **bounds-checked at compile time** | §3.1, §4 |
| `${name}` is the named group | core language tier, gated additionally on module `named-groups` | §3.1 |
| bare `$name` (no braces), greedy, PCRE2-exact | supported — the compile-time check defuses the footgun | Q2 |
| `$$` is a literal `$` | core tier | §3.1 |
| a backslash is an **ordinary literal byte** in the core tier | **[MEASURED]** PCRE2 behaviour, not a simplification: `x\ny` is five bytes without `EXTENDED` | §3.1 |
| `\n` `\x41` `\$` `\u` `\l` `\U` `\L` `\E` | module `subst-extended` | §3.3 |
| `${n:-word}` and `${n:+yes:no}` | module `subst-extended` | §3.3 |
| case forcing is a **pending operator on the output byte stream**, not on the next template item | **[MEASURED]**, three corners a naive design gets wrong | §3.3 |
| an UNSET but existing group renders as | **a generation axis, default empty** | Q3 |
| output buffer | **length-only, no NUL termination, no NUL budget**, 8-bit clean | Q4 |
| the pcrec-only extension namespace | **`${!...}` reserved**, on a **testable rule**: every pcrec-only template form must be a spelling PCRE2 rejects | Q5, §7.1 |
| callback template segments | `rx_renderfn(const rx_ctx *, unsigned char *out, size_t cap) -> ptrdiff_t`, `-1` fails, `out == NULL` returns the length it would produce | Q13, §7.2 |
| sizing mode | **exact by contract**; renderers must honour `out == NULL` and be deterministic across the two passes | Q11 |
| where the template comes from | **`--replace` now, repeatable**; `[V-E]`'s manifest gains a template field when that design lands | Q7 |
| first vs global | **a generation axis, not a flag** — two functions that differ in code, not in a branch | §5.3 |
| the global empty-match rule | **[MEASURED]**, and it refutes the intuitive reading | §6.1 |
| `pcrec_error` gains a which-input tag | landed: `pcrec_err_input` with `PCREC_ERR_INPUT_TEMPLATE` is **in `lib/pcrec.h` today** | Q8 |
| module tiering | `subst` / `subst-extended` / `subst-pcrec` | §3.0 |
| UTF | byte offsets throughout; global-mode step width is `[M5]`'s only change | Q9 |
| duplicate group names under `(?J)` | deferred, lands with module `named-groups` | Q10 |
| `--no-captures` × a `$n`-referencing template | a **compile-time** error | D44.7 |

### 1.2 The shell style is already the ruled style

The charter asks for bash/zsh-style syntax on the replacement side. Setting
the two vocabularies side by side:

| bash | PCRE2 `SUBSTITUTE_EXTENDED` | pcrec (ruled) |
|---|---|---|
| `${name}` | `${name}` | `${name}` — the named group |
| `${n:-word}` | `${n:-word}` | same, `subst-extended` |
| `${n:+word}` | `${n:+yes:no}` (and one-armed `${n:+yes}`) | same, `subst-extended` |
| `${name:?word}` | — | `subst-pcrec` (§3.4) |
| `${name#pat}` `%` `^^` `,,` `:off:len` `${#name}` | — | `subst-pcrec` (§3.4) |

The first three rows are identical across all three columns. So the charter's
instruction and D38's ruling agree, and the honest statement is not "pcrec
picks the shell style over PCRE2's" but **"PCRE2 already uses the shell style
for the forms it has, and pcrec extends it with the forms it does not."** Every
extension lands in `subst-pcrec` under Q5's already-ruled namespace rule.

### 1.3 The departures from PCRE2, collected

D26 requires each to be tiered. There are five and they are all tier 3 (API
shape and error timing), none tier 1 (what a pattern matches):

1. **The `EXTENDED` dialect is a module, not a run-time bit.** D18: the
   template is baked in, so the dialect is a singleton dimension by
   construction and can never become a generation axis. §3.4 there.
2. **`SUBSTITUTE_LITERAL` is not an option.** It is the degenerate template
   compiler — a template with no `$` — and needs no code. **[MEASURED]** in
   PCRE2, `LITERAL` *beats* `EXTENDED` when both are set.
3. **`SUBSTITUTE_UNKNOWN_UNSET` has no analogue.** References resolve at
   compile time, so there is no run time at which a name can be unknown. An
   unknown name is a build error. This is the AOT win the plan row names.
4. **Output is length-only, no NUL.** Q4. PCRE2 terminates, requires room for
   the terminator, and **[MEASURED]** reports the length *inclusive* of it on
   overflow but *exclusive* on success — the same variable meaning two things
   depending on the return value. pcrec's `*outlen` means bytes produced on
   success and capacity required on overflow, uniformly.
5. **Sizing is not an option you must remember to pass.** §4.1.

None of these changes what a replacement *produces* for a given match and
template, which is the tier that is exact.

---

## 2. The variable layer — the one new thing

`subst_template_design.md` predates the variable charter and contemplates one
source of values: the match. The addition is a second source: the caller.

### 2.1 The spelling

**[PROPOSED]**, and it costs no new ruling because D38 Q5 already reserved the
namespace it uses:

> In a replacement template, `${!name}` is the caller's variable `name`.
> A bare `${name}` remains the capture group, exactly as ruled.

`variables_common.md` §1.4 carries the argument; the short form is that the
brace namespace on this side is fully occupied by the match's own groups, so a
caller variable cannot spell itself `${name}` here without colliding with a
ruled production. `${!...}` is reserved, is **[MEASURED]** rejected by libpcre2
10.46 in both dialects, and satisfies §7.1's testable namespace rule.

By that rule's own terms, `${!name}` is module `subst-pcrec`.

### 2.2 The operator suite reaches both selectors

**[PROPOSED]** every operator applies to either selector, with no per-selector
table:

```
    ${1:-none}        group 1, or "none" if it is unset or empty
    ${!prefix:-dev}   the caller's variable, or "dev"
    ${!user^^}        the caller's variable, uppercased   (subst-pcrec)
    ${1:0:3}          the first three bytes of group 1     (subst-pcrec)
```

This is what makes the charter's "the syntax should be the same" true in the
place it matters: one grammar, one evaluator, one value model
(`variables_common.md` §2), reaching two selector namespaces. The UNSET/EMPTY
distinction is the same distinction on both sides — `{-1,-1}` for a group that
did not participate, `p == NULL` for a variable the caller left unset — which
is why `:-` and `-` mean the same thing regardless of which selector precedes
them.

### 2.3 What a variable does *not* change

Three things, stated because each is a plausible assumption:

- **It does not change the unset default.** D38 Q3's generation axis
  (default empty) governs groups *and* variables on this side. The pattern
  side's refusal default (`variables_pattern.md` §5) is the deliberate
  asymmetry, and it does not leak here: in a template, rendering empty
  produces visible wrong output, not a silently wider language.
- **It does not force any engine.** A template variable never touches the
  matcher; it is spliced into the output. Only a *pattern* variable forces the
  VM.
- **It does not interact with `--no-captures`.** D44.7's compile-time error is
  about `$n` references; `${!name}` references nothing the matcher produces, so
  a `--no-captures` artifact can carry a variable-bearing template and that is
  a useful combination (a template that reads only the caller's environment
  and the whole match).

---

## 3. The brainstorm, item by item

One verdict each: **MVP**, **ROADMAP** (with what would open it), or
**DECLINE** (with the reason).

### 3.1 Callouts that return strings

**Verdict: already ruled as `rx_renderfn`; ROADMAP (phase 3).**

The charter says "I think we support that." The precise state of the tree:

- **The callout ABI does not carry a string return, and deliberately.**
  `design_callout_abi.md` §2 ruled native callouts **match-or-fail only**:
  `rx_matchfn` returns a length or `-1`, and values below `RX_ERR_FLOOR` are
  reserved and **enforced today** at every generated call site with
  `if (ret < RX_ERR_FLOOR) __builtin_trap();`. `abort()` and `longjmp` were
  both considered and rejected with reasons. F4 in that note's freeze list is
  the same rule from the match-API side.
- **`rx_renderfn` is the string-returning sibling and it is ruled.** D38 Q13:
  `rx_renderfn(const rx_ctx *, unsigned char *out, size_t cap) -> ptrdiff_t`,
  `-1` to fail, `out == NULL` returning the length it would produce while
  writing nothing. `docs/spec/match_api.md` §2 carries it today as an ABI
  type: *"Emitted ONLY when a substitution template names it."*
- **So a "replacement callout" is exactly `(match, group spans, user) → bytes`,
  and that is what `rx_renderfn` is.** It takes `const rx_ctx *`, which carries
  the subject, the position, the capture array and `void *user` — so the
  callback chooses its own group rather than being handed a pre-selected one,
  which the first draft's bespoke signature could not do. D38 Q6 subsumed the
  user-data question into the `rx_callout_ref` binding unit.

What the variable layer adds is one line: a renderer should also see the
caller's environment. **[RATIFIED — Frank 2026-09-23]** it does, and §5 Q2
below is now ANSWERED rather than open, by the same ruling that resolved
MECH-B2 on the pattern side (`variables_common.md` §3.3): `rx_ctx` gains
`vars`/`nvars` as two fields APPENDED at the end — a per-*call* field, not
the per-*binding* one `user` is — so a renderer reading `const rx_ctx *ctx`
sees `ctx->vars`/`ctx->nvars` directly, with no route through `ctx->user`
needed at all. This is the same fixed-literal ABI type every artifact
already shares, appended once rather than substituted, which is what makes
it NOT the change D38 §1.1 recorded Frank rejecting: that rejection was
about a per-call `user` PARAMETER threading a second, inconsistent way for
data to reach a callout alongside `user`'s own per-binding arrival, not
about `rx_ctx` gaining a new field outright. A var-free artifact's
`rx_renderfn` callers see `ctx->nvars == 0` and read nothing further.

The withdrawn draft below is retained as the record of what was proposed
before the ruling (`ctx->user`, in the meantime) — it is superseded, not
merely an alternative.

### 3.2 Case transforms

**Verdict: `\U \L \E \u \l` are MVP-adjacent (ruled `subst-extended`);
`${!n^^}`-style operators are ROADMAP.**

D38 already ruled the PCRE2 forms, with **[MEASURED]** semantics including the
three corners (a pending force skips an empty group and lands on the next
literal; a one-shot force *cancels* an active run rather than nesting; a run
spans `$n` boundaries and literal text alike).

`subst_template_design.md` §7.3 already argues against the operator form and
this note agrees: a pcrec `${!upper:1}` would be **redundant with** `\U$1\E`
and "should be justified on ergonomics or not built." The bash operators
`^`/`^^`/`,`/`,,` are worth having only because the *pattern* side has no
`\U` equivalent (`variables_pattern.md` §6.3), so the operator earns its place
there and rides along here for one grammar. ASCII-only, refusing by name under
`-e utf8` until a 1:n case-mapping table exists — the same restriction the
pattern side takes and for the same reason.

### 3.3 Substring `${n:off:len}`

**Verdict: ROADMAP.** Cheap on this side (a group's span is already a pair of
offsets, so a substring is arithmetic on them, no copy). What it needs before
building is a stated want, not a measurement: nothing in the corpus or the
bench asks for it. D77.

One correctness note for whoever builds it: under `-e utf8` an offset is a
*byte* offset by D38 Q9's ruling that the template compiler is encoding-blind,
so `${1:0:3}` can split a character. **[PROPOSED]** it refuses rather than
splitting — a truncated character is a malformed output, and producing one
silently is the shape §2.3's UTF-8 validation rule exists to prevent.

### 3.4 Default and alternate on unset groups

**Verdict: MVP on the variable selector, already-ruled `subst-extended` on the
group selector.**

`${n:-}` / `${n:+}` are D38-ruled. `${!name:-}` / `${!name:+}` are the same
operators over the other selector and come free with §2.2's one grammar.
`${name:?word}` is new on both selectors and is the loud one — **[PROPOSED]**
it fails the substitution (returning the template's own error, not a match
failure), which is the template-side analogue of the pattern side's refused
call and lands in `subst-pcrec`.

### 3.5 A per-match counter

**Verdict: ROADMAP, and the spelling matters more than the feature.**

Numbering replacements (`${#}` as the 1-based match index in a global
substitution) is genuinely useful and genuinely cheap — the emitted global
loop already carries the count as its return value (`subst_template_design.md`
§5.2: "Count as the return value... it is what a caller actually wants to
branch on"), so the number exists and is not currently readable from a
template.

But `${#name}` is bash's **length** operator (§1.2's table), so `${#}` and
`${#name}` would be two unrelated operators distinguished only by whether a
name follows — which is exactly the greedy-name ambiguity D38 Q2's measurement
found in `$name`. **[PROPOSED]** spell the counter `${!n}`-free and distinct —
e.g. `${!index}` as a *reserved variable name* rather than a new operator, so
it rides §2.1's namespace with no grammar change at all. That is the general
mechanism: a counter is a variable the engine sets, not a new syntactic form.

### 3.6 Conditional replacement (if-then-else)

**Verdict: MVP for the two-armed form, because PCRE2 already has it.**

**[MEASURED]** at `subst_template_design.md` §3.3: `${n:+yes:no}` is PCRE2's
own two-armed selector and the one-armed `${n:+yes}` is also valid. So the
if-then-else the charter asks about is a ruled `subst-extended` form, not an
extension. Nothing to design.

The richer form — a predicate over the value rather than over its
set/unset-ness — is `design_callout_abi.md` §3's **embedded code** direction
(Frank's `\{ strlen($1) == 5 }` sketch), which that note records as *distant
future* with its restriction set explicitly TBD, and which §6 Q6 there leaves
open by Frank's own ruling. **DECLINE** for this design; it is a different
feature with a different open question, and `rx_renderfn` (§3.1) is the escape
hatch that covers its use cases today without a new language.

### 3.7 Recursion and nesting limits

**Verdict: MVP, as a `limits.def` row.**

`variables_common.md` §1.7: nesting is permitted in the `word` position only,
bounded at **compile time**, because the template is parsed when the artifact
is built. So there is no run-time recursion in the emitted code and the bound
is an ordinary `src/core/limits.def` row — visible to `--list-limits`,
raisable by the documented mechanism, and read by the D107 limits detector for
free.

The thing to *not* build: a run-time recursion depth counter. There is nothing
recursive at run time to count.

### 3.8 The global loop and empty-match advancement

> **CLOSED by §R2 (§R2.1 rows 5-6, 2026-10-21).** The find-all iterator's
> iteration IS PCRE2's global iteration, retry included (`match_api.md`
> §3.8¶2), and the substitution loop is now the iterator plus the glue
> (§R2.4). The seam below was real against §3.1.3's caller loop, and the
> iterator removed it. [MEASURED] in §R2.3. The four inherited gaps: `\G`
> and UTF stepping are the iterator's (§3.8¶2, §3.1.3¶4), lookbehind under
> the loop is witnessed by §R2.3's `lbcap` cell, and newline conventions
> remain [DD-11]'s.

**Verdict: MVP, ruled, and do not re-derive it.**

`subst_template_design.md` §6.1 is **[MEASURED]** against libpcre2 and it
**refutes the intuitive rule**, which is why this note cites it rather than
restating it in its own words:

> An empty match is suppressed **only at the position where an empty match was
> just produced** — not at the end of a non-empty match.

The discriminating cell is `a*` on `"aab"` with replacement `[$0]`, which
gives `[aa][]b[]` and not `[aa]b[]`. A design that suppresses at the previous
match's end is wrong by one substitution, and that was the note's own
prediction P10 before it was measured.

**One thing worth flagging for whoever implements it**, because it is a
genuine seam and neither note owns both sides: `docs/spec/match_api.md` §3.1.3¶9's
*caller-driven* find-all loop is explicitly **lossy** relative to PCRE2 and
python for empty-preferring patterns — it has no way to express PCRE2's
"NOTEMPTY_ATSTART retry," so its result is always a strict subset. §6.1's
emitted loop *does* express the retry ("that search is retried not-empty-at-
start and anchored"). So the emitted substitution loop is **not** the §3.1
loop with a splice in it, and building it that way would produce a different
substitution count on exactly the empty-preferring patterns §6.1 measured.
`[PC-5]` already classifies `NOTEMPTY`/`NOTEMPTY_ATSTART` as `EMITTED-LOOP`
for this reason. **[PROPOSED]** the implementation note for `[M4-SUBST]` states
this seam explicitly; it is the kind of thing that reads as a defect when
found later.

**The variable layer inherits four empty-match-advancement gaps from the
ruled baseline, stated here explicitly rather than left implicit.**
`subst_template_design.md` §6.1's rule is oracle-verified for two axes —
empty match after a non-empty match (the rule's whole point) and empty match
at end (the `"aab"` example's trailing `[]`) — with empty match at start
implicit in the same trace (`"bab"`'s empty match at offset 0). Four more are
**explicitly** marked open in that ruled baseline, and this note does not
reopen them, only names them so the variable layer's own inheritance is on
the record rather than silent:

- **`\G`** — cited, not solved, deferred to `[DD-4]` (`subst_template_design.md`
  §6.2, "whichever lands second must not introduce a second copy of it").
- **UTF-8 mid-codepoint advancement** — deferred entirely (`subst_template_design.md`
  §6.2, "a step-width question in the emitted loop... Deferred entirely"), in
  contrast to `docs/spec/rxt_format.md`'s own `mc` find-all count, which
  states the identical-shaped rule NORMATIVELY — the eventual
  `[M4-SUBST]` implementation should reuse that rule rather than re-derive
  it.
- **Newline/CRLF conventions inside the loop** — deferred to `[DD-11]`
  (`subst_template_design.md` §6.2, "the probe does not exercise it,
  deliberately... `[DD-11]` owns `NEWLINE`/`BSR`").
- **Lookbehind-anchored interaction with the global loop** — not discussed in
  either the ruled baseline or this note before now; recorded here as a
  fifth open item with no owner yet named.

None of these four are variable-specific, and `[DD-4]`/`[DD-11]` are
pre-existing dependencies of the ruled baseline this design correctly
declines to re-litigate. But the variable layer makes the UTF-8 question
MORE material than it was: a caller-supplied variable's bytes are spliced
into the output stream at exactly the position the deferred step-width
question governs, so caller-controlled multi-byte content is a new way to
exercise a rule nobody has built yet — worth a note for whoever opens
`[M4-SUBST]`, not a design change here.

### 3.9 A `--replace` `.rxt` block kind

**Verdict: MVP, and this note PROPOSES rather than rules.**

`subst_template_design.md` §8.1 already proposes the shape, in the existing
directive grammar: a block-scoped `repl <template>` beside `flags`/`features`,
with `s "<subject>" "<expected>"`, `sg` for global, and `serr` for a template
that fails to compile. The `<expected>` field reuses the existing quoted-subject
escape set unchanged, which matters because substitution output is exactly
where an embedded NUL or newline needs writing down.

**The variable-binding directive itself lives in `variables_common.md` §3.5,
not here** — the underlying `rx_var` array is shared between the pattern and
replacement consumers (§4.2 below), and a test author reading this note
needs one pointer to the shared binding mechanism rather than a
substitution-scoped proposal that a pattern-side reader (`variables_pattern.md`
proposes no `.rxt` syntax of its own) would have no reason to find. In brief:
`var <name> "<value>"` (block-scoped, repeatable) and `var-unset <name>`
(declares the slot UNSET, a state distinct from `var name ""`'s EMPTY,
`variables_common.md` §2.2) bind a variable identically whether the block is
a bare `m`/`n` match case or a `repl`-bearing substitution case.

**This does not rule the spelling.** Memory `pcrec-dd13b-syntax-is-managers`:
`.rxt` format spelling and syntax are the manager's call, and the machinery a
new production must satisfy is real — a `rxt_schema.def` row with its ten
columns, and agreement across all three parser legs (`pcrec` itself,
`tests/harness/run.sh`, `tests/harness/verify_rxt.py`), checked by W23-S3.
`docs/spec/rxt_format.md`'s graduation rule also offers the staging path: an
`ext` block can carry this before it is a production, and must graduate "the
day something in an `ext` block needs pcrec to ACT on it."

---

## 4. The call interface

### 4.1 The output protocol — ruled, and the charter's three options collapse to it

> **SIGNATURE SUPERSEDED by §R2.4 (2026-10-21).** The protocol stands
> (length-only, capacity always reported, `out == NULL` sizes, no
> allocation). The per-pattern `rx_subst(s, n, out, outlen)` entry does not:
> it becomes the shared glue `pcrec_subst(rx, it, sub, slot, limit, out, cap,
> &outlen)`. The sink form becomes a glue variant (§R2.6).

The charter asks me to argue two-call overflow versus a caller-supplied
allocator versus a callback sink. D38 already ruled, and the ruling is none of
the three as stated — it is the two-call protocol's two calls **merged into
one function**:

```c
/* On entry *outlen is the capacity of out; on return it is the number of
 * bytes produced. Returns the number of substitutions (0 = no match, subject
 * copied through), or RX_SUBST_NOSPACE with *outlen set to the capacity that
 * would suffice. out may be NULL: nothing is written, *outlen receives the
 * required capacity. Allocates nothing, ever. */
int rx_subst(const unsigned char *s, size_t n,
             unsigned char *out, size_t *outlen);
```

Why this beats the plain two-call protocol, in the ruled note's own terms:
**[MEASURED]** PCRE2 without `OVERFLOW_LENGTH` returns `-48` on an undersized
buffer and sets the length to `PCRE2_UNSET` — *the caller learns nothing*, and
must have remembered to pass an option to learn anything. Always reporting the
required capacity costs one `size_t` store on a path that is already failing,
and removes an option. `out == NULL` is the same idea reached from the other
end, and it is the pre-flight call.

- **A caller-supplied allocator: DECLINE.** "Allocates nothing, ever" is the
  embedded-niche property and the reason this is an AOT compiler. An allocator
  hook re-introduces allocation and a failure mode, to save a caller one call
  they can already skip by sizing generously.
- **A callback sink: ROADMAP**, and it is already offered rather than invented
  — §7.2 option (c), `rx_subst_to(s, n, sink, ctx)`. Its trigger is stated
  there: it *"composes with `[M3]` later and removes the buffer-sizing question
  entirely,"* and writing straight to a socket or a `FILE *` is the embedded
  story. D77-shaped: build it when `[M3]` (streaming) arrives, not before.

### 4.2 Variables on the entry

> **SUPERSEDED by §R2.4 "Variables" (§R2.1 row 15, 2026-10-21).** There is
> no `rx_subst` entry to carry a `vars, nvars` pair. The glue fills
> `rx_ctx.vars` from the iterator's own `rx_iter_vars` binding, so one array
> bound once serves pattern and template alike.

**[RATIFIED — Frank 2026-09-23]**, by the same rule the pattern side takes
(`variables_common.md` §3.1-§3.3; `variables_pattern.md` §4), so that there
is one rule and not two — and by the manager's default extension of it to
this entry (`variables_common.md` §3.3's caller-buffer-siblings precedent):

```c
int rx_subst(const unsigned char *s, size_t n,
             unsigned char *out, size_t *outlen,
             const rx_var *vars, size_t nvars);
```

`rx_subst` is not `rx_ctx`-shaped — it takes no context struct to append
`vars`/`nvars` to — so it takes the pair directly, the same shape
`variables_pattern.md` §4.1 gives `rx_search` and its `_in` siblings rather
than the shape `rx_match` keeps (unchanged, because `rx_match` **is**
`rx_ctx`-shaped and carries the array through its context instead — the
ruling that resolved MECH-B2, `variables_common.md` §3.3). The pair
appears **only on artifacts whose template names a variable**, which is
D18's rule unchanged (a fixed choice is compiled away) and which means a
variable-free substituter is byte-identical to the ruled surface.

Each `rx_var` now carries a `name` (`variables_common.md` §3.1); the
artifact resolves its own mentioned names against the supplied array once
per call, at entry, before the match+splice begins (§3.2's mechanism) — a
caller no longer writes to a compile-assigned index. The internal index
macros are still shared with the pattern side: one `<PREFIX>_NVARS`, one
`<PREFIX>_VAR_<NAME>` per name, over the union of the names the pattern and
the template mention — the right union, because a single artifact can carry
both a pattern variable and a template variable and they should share a
namespace and one resolved table — but, per the ruling, these are the
artifact's own INTERNAL bookkeeping, never what a caller writes.

`vars`/`nvars` go last, after `outlen`, so the ruled parameter positions do
not move.

### 4.3 First and global

> **SUPERSEDED by §R2.4 (§R2.1 row 7, 2026-10-21).** The iterator owns the
> loop, so the reason for two emitted functions is gone: the glue's `limit`
> argument (1 = first, `SIZE_MAX` = all) replaces the generation axis.

**[RATIFIED]** §5.3: a **generation axis**, not a flag. `{first}` emits
`rx_subst`; `{global}` emits `rx_subst`; `{first, global}` emits
`rx_subst_first` and `rx_subst_all`. The two genuinely differ in code — the
first-match form has no loop, no carried position and none of §6's empty-match
machinery — so a run-time flag would put the whole global state machine into
the first-match path and pay for it on every call. D18 forbids exactly that
trade.

### 4.4 The generated shape

> **SUPERSEDED IN PART by §R2.7 (§R2.1 row 8, 2026-10-21).** One template
> per subst ARTIFACT, never entries of the rx's file (D88 add. 1); 1:N and M:N
> are linking. The "template compiles to a small program of segments"
> paragraph stands, now emitted as `<s>_render`.

**[RATIFIED]** §5.5: nothing ties one pattern to one template. The splice code
is per-template, the matcher is per-pattern and shared, so `rx_subst_redact`
and `rx_subst_expand` over one matcher is the same named-entry-point
mechanism and needs no new machinery. Q7 ruled `--replace` repeatable on that
basis.

**[PROPOSED]** the template compiles to a small program at build time, exactly
as the pattern does — a sequence of segments, each a literal run, a group
reference, a variable reference, or a renderer call — and the expansion half
of `variables_common.md` §5 is what evaluates a segment's operators. One
program form, two sources of value. This is the charter's "the replacement
TEMPLATE compiled to a small program at compile time, like the pattern," and
it is what makes the operator suite shareable rather than duplicated.

Note the constraint that shapes packaging: **D88, one artifact per emitted
file, always.** Composition is linking, never a multi-pattern translation
unit. So several templates over one matcher is several entry points in one
file (one artifact), and several *patterns* is several files.

**One consequence of §4.2's ruling worth stating for this packaging claim.**
`rx_subst_redact` and `rx_subst_expand` sharing one matcher each carry their
OWN `vars, nvars` pair (§4.2) — the pair is per-ENTRY, resolved by that
entry alone at call time, not a value bound once for the whole artifact.
Two templates over one pattern that mention different variable sets do not
force either call site to supply more than it needs, even though the
artifact's own internal index table (`variables_pattern.md` §4.3 covers the
pattern side's; this side shares it, §4.2 above) is sized to the union of
every name either side mentions.

---

## 5. Open questions

Numbered; recommendations are this note's, not rulings. Questions already
ruled by D38 are not re-opened here.

1. **Is `${!name}` the right spelling on this side?** §2.1 spends D38 Q5's
   reserved prefix. The alternative is a distinct sigil for caller variables
   (`@{name}`, say), keeping `${!...}` free for later extensions.
   *Recommend `${!name}`*: Q5 reserved the prefix for pcrec extensions
   generally and this is the extension with the widest reach; the remaining
   namespace after it is still large.

2. **~~Does a renderer see the variable environment directly?~~ RULED**
   (Frank, 2026-09-23, §3.1 above): yes, automatically — `rx_ctx` gains
   `vars`/`nvars` as appended fields (`variables_common.md` §3.3), so a
   renderer receiving `const rx_ctx *` already has them, with no route
   through `ctx->user` needed. Ruled once, on the ABI side
   (`variables_common.md` §3.3), exactly as this question anticipated it
   would be rather than twice.

3. **The counter's spelling.** §3.5 proposes a reserved *variable name* rather
   than a new operator, to avoid colliding with bash's `${#name}` length
   operator. *Recommend as proposed*, but the reserved-name mechanism is new
   and needs its own rule (which names are reserved, and what happens when a
   caller supplies one).

4. **Does `${1:0:3}` refuse or split under `-e utf8`?** §3.3 proposes refuse.
   The counter-argument is that D38 Q9 ruled the template compiler
   encoding-blind, and a refusal is an encoding-aware behaviour appearing in a
   component ruled not to have one. *Recommend: refuse, and note that the
   refusal is a compile-time property of the artifact's declared encoding
   rather than a run-time branch* — which keeps Q9's "no encoding conditional
   in the emitted artifact" intact.

5. **The `.rxt` production's spelling and staging.** §3.9 proposes `var` /
   `var-unset` beside §8.1's `repl` / `s` / `sg` / `serr`, and explicitly does
   not rule. The manager's call, per memory `pcrec-dd13b-syntax-is-managers`;
   the `ext`-then-graduate path is available if the format work is not ready.

6. **Does `[M4-SUBST]`'s streaming holdback survive a variable?** That row's
   2026-09-06 sharpening sizes the holdback buffer from `cwmax`/`maxw`, and
   `variables_pattern.md` §2 makes a *pattern* variable's `maxw` unbounded.
   So a var-bearing pattern would refuse streaming by that row's own honest-
   refusal rule. That is probably correct and it is certainly a consequence
   nobody has written down. *Recommend: confirm it is the intended reading
   when `[M4-SUBST]` opens*, rather than discovering it at build time.

---

## 6. The four lenses

| lens | verdict |
|---|---|
| **specific vs general** | **GENERAL**, and mostly by *not adding*. The substitution design was already ruled; this note adds one selector to an existing grammar and one parameter to an existing entry, and routes every brainstorm item either to a ruled mechanism (`rx_renderfn`, `${n:+yes:no}`, the generation axis) or to an existing module tier. The one place it resists a specific mechanism is §3.5, where a counter becomes a reserved variable name rather than a new operator. |
| **core vs derived** | **DERIVED.** Nothing in the matcher moves. The template compiler is, in `subst_template_design.md` §1's **[MEASURED]** argument, a pure function of the template text and the *shape* of the capture data — it never needs a matcher, and the variable layer does not change that: a variable is a second source of bytes for a splice that already exists. |
| **applicable vs assumption-changing** | **APPLICABLE.** A variable-free template is byte-identical to the ruled surface (§4.2's parameter appears only when named). The one assumption this note *tests* rather than changes is §3.8's: that the emitted global loop is the §3.1 caller loop with a splice — it is not, and saying so now is cheaper than finding it in a substitution count later. |
| **fits-arch vs refactor** | **FITS**, and more cleanly than the pattern side, because the hooks are already cut: `pcrec_err_input.PCREC_ERR_INPUT_TEMPLATE` is **in `lib/pcrec.h` today** with no producer, `rx_renderfn` is in `docs/spec/match_api.md` §2 today with no producer, `${!...}` is reserved today with no spender, and the module names `subst`/`subst-extended`/`subst-pcrec` are ruled. This note spends three of those four reservations on what they were reserved for. The packaging constraint (D88, one artifact per file) is satisfied by §4.4 without a change. |
