# `--emit-facts` — the pattern-facts listing format

**[PATFACTS] step 3.0, 2026-09-26 (D126, ruled Q8); rows `kinds` and
`nullable` added at step 3.2, rows `kset_walk` and `run_pin` (the first
`E3` rows) and the two route declines at step 3.4, 2026-09-27.** This document is the
CONTRACT for what `pcrec --emit-facts` prints: its sections, their columns,
and what is and is not promised about each. It conforms to
`docs/spec/table_contract.md` (the TSV producer/consumer contract) and adds
only what is specific to this listing. `docs/spec/cli.md` §2 is the flag's own
reference entry. The design is `docs/design/patfacts/design.md` §11
(informational).

## What this listing IS, and what it is not

It is a **DEBUG listing**, with `docs/spec/ir_listing.md`'s status (D106
addendum 2): the format and its vocabularies are promised, the row set and
the prose are advisory. It is not part of the generated artifact, so it has
no `abi` number and moving it is not an `abi` event.

It prints **the pattern-facts record** of a compile — what pcrec concluded
about the PATTERN (which construct kinds it contains, whether it can match
the empty string, the byte every match must contain, the necessary literal
run and set, the start anchor, the end window, the bytes every match carries
at each offset from its own start and where the necessary run sits among
them), each fact's status, whether a
pass consumed it, and WHY it has its value — plus the artifact's own
**decision stamps** (which engine, which prefilter, whether a pre-check was
emitted), which are route decisions the record deliberately does not hold.

It **reads the record, never recomputes it**. Every `facts` row is the value,
status and reason the fact's accessor STORED when the compile asked it, and
the value is rendered by the same renderer the artifact's fact-valued stamps
use (`<PREFIX>_REQ_BYTE`, `_REQ_RUN`, `_END_WINDOW`, `_VM_START`), so a stamp
and the listing cannot spell one value two ways. The `decisions` rows are
read off the finished artifact's text. Only the FINAL compile attempt's record
is listed; a record from an attempt the compiler discarded (a retry, a size
ladder rung) is never shown.

It is **not VM-only**: facts are engine-neutral, and the listing works on a
DFA, hybrid or VM artifact alike.

## The query

`pcrec --emit-facts[=ENC,...] [compile options] --pattern P`

A QUERY, like `--emit-ir`: it takes a pattern, takes no `-o`, runs the
ordinary compile to completion in memory, prints the listing and exits. Every
compile option (`-e`, every `-f`/`-fno-` axis, `--engine`, `--features`, …)
applies unchanged, so the listing describes the compile the caller would have
got. The bare flag lists one compile under the `-e` in effect; `=ENC,...`
(for example `--emit-facts=byte,utf8`) runs one complete, ordinary compile
per listed encoding and concatenates their rows under each section, every row
carrying its `encoding`. A pattern pcrec refuses is refused with the ordinary
compile's diagnostic (exit 1). `--emit-facts` composes with no other query
mode.

## Framing

1. `docs/spec/table_contract.md` applies in full: TAB-separated values, `#`
   comment lines, the last `#` line before a section's first data row is that
   section's header, columns are APPEND-ONLY, an empty field means "none", a
   field never contains a TAB.
2. **Every table is a NAMED `#section`.** The preamble before the first
   `#section` is free prose and belongs to no section.
3. **The section NAME set is the API**: append-only. `facts` and `decisions`
   ship today; a `rate` section (the byte-rate queries a compile consumed)
   is reserved for the findings-data step ([FINDINGS] B1) and will be added,
   not substituted.
4. **Cell escaping is `pcrec_sb_text`'s vocabulary**, the one every registry
   dump uses: a byte below 0x20, and 0x7f, goes out as `\xNN`; every other
   byte passes through as itself.
5. **Column WIDTH is not a contract.** Fields are unpadded.
6. **A `#` line never follows a section's data** (table contract rule 3
   would make it the next section's header by accident).

## The sections

### `facts` — `encoding | fact | grain | epoch | status | used | value | why | note`

One row per record fact, per listed encoding, in the record's own table
order. Every fact the record has is listed, including ones no pass asked
for: after the artifact and every stamp are complete, the listing asks each
unasked fact once, through the same accessor and derivation, which is why
those rows read `used no`. Because the extra asks happen after the artifact
exists, they cannot change a byte of it.

| column | content | promised |
|---|---|---|
| `encoding` | the compile's encoding (`-e`'s spelling) | yes |
| `fact` | the fact's name | **no** — a later step may add, rename or split facts |
| `grain` | `pattern` (one answer per compile; node-grain facts are not listed) | vocabulary yes |
| `epoch` | the seal the fact is asked after: `E1` structural, `E2` lowered, `E3` machine | vocabulary yes |
| `status` | **CLOSED**: `derived` / `denied` / `declined` / `absent` (below) | yes |
| `used` | **CLOSED**: `yes` — a compiler pass asked for the fact while the artifact was built; `no` — only the listing asked | yes |
| `value` | the fact's value, by its one renderer: a byte as decimal, a run as lowercase hex (with `@idx`, the scanned member's index, where the stamp carries it, and — since `abi` 59, only where some position is not an exact byte — `/` and each position's mask in hex, `tuning.md` §2.28), a set as a comma-joined ascending byte list, the start anchor as `<PREFIX>_VM_START`'s token, the kind mask as a comma-joined list of kind names in a fixed order (`bref`, `linked_call`, `var`, `atomic`, `lookaround`, `live_capture`, `collapsible_rep`; since [UCP] U2 `lookaround` counts only lookarounds that stay sub-matches — a one-character lookaround is a context node, `tuning.md` §2.32, and is not in it), nullability as `yes`/`no`, the k-set walk as a comma-joined list of its offsets in order (a one-byte offset as that byte in decimal, a wider one as `[N]`, its byte count), the run pin as the offset in decimal (a pin on the whole window), or `o:at+len` (a pin on the exact stretch `at .. at+len` of a masked window, `tuning.md` §2.30), the run window's maximum byte offset from the attempt start (`req_run_maxoff`, since `abi` 61, [K82] (B)) as a decimal or `unbounded` (with `why` `decline:unbounded`), the value `<PREFIX>_REQ_HANDOFF` carries where the handoff applies (`tuning.md` §2.41); `none` where the fact has no answer; EMPTY on an `absent` row | spellings shared with a stamp are that stamp's (`match_api.md` §6.3, `tuning.md` §2.25-§2.28); others advisory |
| `why` | **CLOSED token grammar** + detail (below) | the grammar yes; reason NAMES no |
| `note` | prose (the fact's kind and owning source file today) | no wording promise (D26) |

**`status`:**

- `derived` — the fact's derivation ran; its value may still be an empty
  answer (`none`) when the pattern simply has nothing to find;
- `denied` — a fact-level `-fno-` flag stored the fact's empty value without
  deriving it (the build is indistinguishable from a pattern with nothing to
  find, for every consumer of the fact); `why` names the flag;
- `declined` — the derivation ran and declined for a stated structural
  reason; `why` names it;
- `absent` — the fact is not derivable on this compile's route, or the
  listing's own forced ask of it failed; its `value` is empty. The `E3`
  facts are derivable only on a route whose forward scan runs the
  unanchored machine (`<PREFIX>_DFA_SCAN "unanchored"`, a DFA or a hybrid
  artifact); on every other route they are `absent` with a `decline:` naming
  the route (below), and no pass can have consumed them.

**`why`** is empty for a plain derivation, else exactly one of:

- `deny:<flag>` — `<flag>` is the `-fno-` spelling exactly as `--list-axes`
  and the CLI accept it (`deny:-fno-req-byte`). Where two flags can deny a
  fact and both were given, the lower-numbered bit is named.
- `decline:<reason>` — e.g. `decline:enc-multibyte` (the end window under an
  encoding with non-boundary positions), `decline:force-failed` (the
  listing's own ask failed; the compile's result is unaffected),
  `decline:attempt-unwrapped-nfa` (an `E3` fact on a route whose forward scan
  is the anchored-attempt machine, `<PREFIX>_DFA_SCAN "attempt"`) and
  `decline:no-forward-nfa` (an `E3` fact on an artifact with no DFA scan at
  all).
- `rate:<source>` — for a fact CHOSEN by a byte-rate rule, which rule
  answered: `rate:builtin-prior` (the shipped byte-frequency prior) or
  `rate:none(<encoding>)->rightmost` (the prior does not apply to this
  encoding, and its no-rate answer decided: the candidate with the fewest
  members, ties to the rightmost — so the rightmost member wherever every
  candidate is one byte, `findings.md` §4).

Which `-fno-` flag empties which fact is stated, flag by flag, in
`docs/spec/tuning.md`'s "Facts emptied" line for that flag, and the listing
is checked against that text (`tests/codegen/run_facts_checks.sh`).

### `decisions` — `encoding | stamp | value`

One row per VALUE stamp in the finished artifact, in the order the artifact
carries them: every object-like `#define` whose name is `<PREFIX>_…` or
`PCREC_FEATURE_…`, read off the artifact's emitted C (compiled without a
paired header, so every stamp is in the one `.c` text). `stamp` is the macro
name exactly as emitted; `value` is its replacement text exactly as emitted
(a quoted string stays quoted). The function-like machinery macros a VM
artifact defines (`<PREFIX>_PUSH(...)` and its family) are code, not stamps,
and are not listed. What each stamp means is its own spec's
(`match_api.md` §6.3, `tuning.md`); this section promises only that it is the
artifact's stamp block, byte for byte.

## Guarantees

1. **The listing never refuses a compile that succeeded.** A forced ask that
   fails is recorded as that one fact's `absent` / `decline:force-failed`
   row; the rest of the listing, and the exit status, are the compile's.
2. **The listing never changes the compile.** Its only extra work happens
   after the artifact and every stamp exist, and it reads the record rather
   than re-deriving anything, so the artifact a `--emit-facts` compile builds
   is the artifact the same options build without it.
3. **One spelling per value.** A fact-valued stamp and the fact's `value`
   cell come from one renderer.

## What is NOT promised

The fact NAMES and the row set (every migration step of the record may add,
rename or split facts), value spellings beyond those shared with a stamp,
`why` reason names beyond the token grammar, and `note` text. Tools that key
on this listing should resolve columns by name and treat unknown facts,
sections and trailing columns as ignorable (table contract consumer rules).
