# Lane `uvbuild` — [UTF-VALID] built: `-futf-check` (whole) and `-fstartpos-guard=align`

Lane `uvbuild` (opus), 2026-09-30, branch `lane/uvbuild` from main
`d8d40397`. Brief: build [UTF-VALID] as ruled in D133 (all eleven questions
of `docs/design/utf_valid_design.md` §8 as recommended; `whole` built,
`extent` recorded not built) plus D132 item 2's start alignment. One abi
event, 49 -> 50. Not pushed, not merged.

## 0. What was built

| piece | where |
|---|---|
| design note §10 (the alignment ruling) and status RULED; a MEASURED correction annotated into §1.4 | `docs/design/utf_valid_design.md` |
| `-futf-check` (bit 39, `PCREC_FORCE_UTF_CHECK`, a DEFAULT_OFF contract axis, no deny spelling); `-futf-check=extent` refused BY NAME | `lib/pcrec.h`, `src/core/axes.def`, `cli/main.c` |
| `-fstartpos-guard=align` (bit 40, `PCREC_FORCE_STARTPOS_ALIGN`, the startpos-guard row's force column); refused together with `-fno-startpos-guard` | same, plus `src/core/compile.c` |
| `PCREC_ERR_UTF (-9)` in the shared `PCREC_RX_ABI_H` block | `src/gen/emit_dfa.c` |
| `<prefix>_valid_upto(s, n, startpos)` in EVERY artifact: new seam entry `PCREC_ENCE_VALID_UPTO`, always in both emitters' masks; utf8 body = PCRE2's raw step-back + validator + ASCII fast path; byte body `return n;` | `src/enc/enc.h`, `enc_utf8.c`, `enc_byte.c`, both emitters |
| ONE validator: utf8's `$_var_valid` re-spelled as `$_valid_upto(v, len, 0) == len` (`requires` carries the call) | `src/enc/enc_utf8.c` |
| the LB fact: `Ctx.lb_max`, a parse-time running max via `pcrec_lb_raise` — `\A`/`\b`/`\B` raise 1 (mod_assertions.c), a lookbehind its widest branch in characters, at parse time or deferred, and a T3 one-character lookbehind 1 (mod_lookaround.c) | `src/core/internal.h`, `src/parse/` |
| `<prefix>_VALID_LB`, the `.c`-only macro the body reads, emitted on every artifact beside the residual definitions | `src/gen/emit_dfa.c` (`emit_residual_defs`) |
| the entry prologue: `pcrec_emit_startpos_guard(..., anchored)` writes the axis's value (K50's refusal byte for byte / nothing / the ALIGN seek) and THEN `emit_utf_check`'s one precheck line, at exactly the four caller-position sites (DFA search head + unwrapped match; VM search `_run` + the two anchored `_run`s via `vm_emit_match_guard`, retiring the `mguard` splice buffer). Guard-first is structural | `src/gen/emit_dfa.c`, `src/gen/emit_vm.c` |
| `pcrec_utf_check_on(cx)`: the flag AND a backend with ill-formed byte strings (its table carries a `VAR_VALID` row) — one predicate for the check, the stamp, and the `rx_info.flags` mask | `src/gen/emit_dfa.c` |
| stamps: `<PREFIX>_UTF_CHECK` "inert"/"off"/"whole" (new, unconditional); `<PREFIX>_STARTPOS_GUARD` gains "align" | `src/gen/emit_dfa.c` |
| `rx_info.flags`: both new bits are CONTRACT bits, kept, masked only where inert (`byte`) | `src/gen/emit_dfa.c` |
| `--list-axes`: axis `startpos-guard` gains row `align`; new axis `utf-check` (`inert`/`whole`/`off`) | `src/dump/axes_dump.c` |
| harness: `driver.c` names -9 as `utf <offset>` (exit 3) in both paths; no `gu utf` word (no block can compile `-futf-check`) | `tests/harness/driver.c` |
| new suite `tests/utfcheck/` (`make test-utfcheck`, joins TEST_SECTIONS) | see §3 |
| `make test-axes`: `-futf-check` excluded from the identity sweep BY NAME (asserted present) + its own oracle arm `tests/axes/utfcheck_arm.py` | `tests/axes/` |
| mech: arm `utfcheck` registered; rows S409-S414 | `tests/mech/` |
| [UTF-EXTENT] filed as a not-started row with its D77 trigger | `docs/dev/plan.md` |

**Not built, by the ruling**: `extent` (reserved spelling refused); no
composed call sites exist, so -9's PROPAGATE rule (Q11) is spec-only, as
the design said. **Not changed, deliberately**: `--emit-main`'s demo
`main()` still prints `giveup -9` for a refusal, exactly as it prints
`giveup -7` for K50's (a caller-facing demo, not a contract; D77).

### 0.1 The alignment, as built (design §10)

Align is the K50 guard's own condition with the refusal replaced by a SKIP:
`if (!(pos == 0 || G(pos))) do pos++; while (!(G(pos)));` where `G` is the
backend's `start_guard` predicate (no second spelling of "character
start"). Offset 0 is never moved (it is never refused either — a buffer
that itself begins mid-character is ill-formed data, and the check reports
it). A SEARCH runs from the aligned position as if the caller had passed it
(`\G` and lookbehind context included); an ANCHORED entry answers -1 at a
misaligned `ctx->pos` (K73's NOMATCH form), and under `-futf-check` first
validates from the aligned position so no answer is given for an
ill-formed checked range. The search-filter `_match` form gets this for
free (its search seeks, its start filter then rejects).

## 1. The abi event (49 -> 50) and every reader, found by grep

Readers of the NUMBER (grep for the current value across `src lib cli tests
docs/spec docs/guide examples scripts Makefile tools`):

1. `src/gen/emit_dfa.c:51` `#define PCREC_ARTIFACT_ABI 50` (feeds the
   generated-by header line and `rx_info.abi`).
2. `docs/dev/history/abi_changelog.md` — the ONE change-log paragraph ("`rx_info.abi`
   is `50` ..."), new entry above the 49 one.
3. `tests/codegen/run_codegen_tests.sh` — `ABI_EXPECT=50` and the appended
   49->50 clause of its failure message.
4. `tests/codegen/run_recursion_identity.sh` — the (B) `FILEPIN`, re-pinned to
   this lane's last `src/` commit (self-pin, the k73utf convention).

Every other `49` hit is historical prose (tuning.md §2.35, match_api.md §6.3's
VM_RESEED table, S370/S371 headers) and correctly unchanged.

**Second reader class (byte counts that move without citing the digit)** —
found by running the suites that count and by grep for `RE-PINNED`:

| reader | move | how verified |
|---|---|---|
| `tests/codegen/manifests/m5_stage1_stamps.tsv` (cpset census) | every `EMITTED_BYTES` row +377 | same-basename diff of `a`: stamp +29, `PCREC_ERR_UTF` +127, decl +73, `VALID_LB` +21, byte definition +127 |
| `tests/codegen/run_size_term.sh` cap-rescue cell | cap 31,500 -> 31,900 | K=4 bisected at 31,555 (+425, K-invariant) |
| `tests/resource/run_resource_tests.sh` K59-PREMUL witness | 762,381 -> 762,551 | same-basename diff: +29 +21 +120 in the `.c` |
| `tests/registry/run_registry_tests.sh` axes coverage | 155 -> 165 | two single-bit triples (bits 39, 40) + two `check_value_set` pairs |
| `tests/codegen/run_codegen_tests.sh` [M5-SEAM] fixtures | every row `valid_upto:0`; three caller rows; span-compare guard 8 -> 9 | fixture counts read off emitted artifacts |
| S368 anchor (the guard call gained `anchored`) | re-anchored, intent re-verified | SABANCHOR: 375 rows / 391 sites resolve |

## 2. Spec hunks (D80)

- `docs/spec/match_api.md`: §1 (the new per-artifact name, the ABI block's
  three caller refusals); §2 (the `PCREC_ERR_UTF` line); §3.1 and §9.2/§9.4 (#startpos-align, #utf-check) (the -9 return
  row, the align bullet replacing "neither arm rounds", the whole
  `-futf-check` paragraph: range, LB, raw step-back, ORDER, every entry, cost,
  byte-inert); **§3.1.2 `<prefix>_valid_upto`** (new: contract, every artifact,
  the find-all idiom "validate once, loop on the default artifact", extent
  reserved); §3.2 (the anchored entries' -7/-9/-1-under-align); §4 (the code
  block gains -8 and -9; the -9 paragraph with the composed-site PROPAGATE
  rule `ret < FLOOR && ret != PCREC_ERR_UTF`); the abi change log (docs/dev/history/abi_changelog.md);
  §6.3 (`<PREFIX>_STARTPOS_GUARD` and `<PREFIX>_UTF_CHECK` value tables).
  **§3.1's find-all LOOP text is untouched** (k75fix's territory); the idiom
  lives in §3.1.2.
- `docs/spec/tuning.md`: §1 (two contract axes), §2.23 (retitled: three
  values, the align arm, the mask, the sweep covers both spellings), **§2.36**
  (new: `-futf-check`), the bit table, §5.4's flat rows (GATE 1).
- `docs/spec/cli.md` (the two contract flags, the two refusals; the
  tuning-flag roster gains the missing `-fno-cls-kit`/`-fno-cls-pack`),
  `docs/spec/registry.md` (axis list 35 -> 38: `utf-check`, and the stale
  omissions `cls-kit`/`cls-pack`), `docs/spec/rxt_format.md` (the driver's
  `utf <offset>` word), `docs/guide/encodings-and-subjects.md` (pointers).
  `limits.md`: no new limit.

## 3. Oracle evidence — `tests/utfcheck/`

- **The oracle is libpcre2 10.46 (ubuntubudu), PCRE2_UTF with checking ON**:
  `probe_pcre2.c` answered `gen_cases.py`'s 6,464 questions in one light ssh
  session (one small compile, temp dir removed; the command is in the
  directory's CLAUDE.md), committed as `cases_10.46.tsv`. The Mac's 10.48
  gives the identical answer on every row (only a `-33` row's meaningless
  `startchar` differs).
- **Second, independent oracle**: python's strict `bytes.decode('utf-8')`
  over the range the design's §1.3 walk defines, transcribed from the design,
  agrees with libpcre2's refusal AND offset on every row before pcrec is
  scored (5,089+ rows cross-checked).
- **The design's §1 tables reproduced exactly** (23 rows, typed from the note
  and asserted against the transcript).
- **LB**: `rx_VALID_LB` equals `PCRE2_INFO_MAXLOOKBEHIND` on all 42 patterns
  pcrec compiles, including the no-accumulation, dead-DEFINE, `\A`,
  non-atomic `(*naplb:` and `\x{100}` rows. Not built in pcrec (so not in the
  table): `(?<=a{1,3})`, `(*UCP)\b` under utf8, `\X`, `\R`, conditionals,
  `(?<=\1)`, `[[:<:]]`/`[[:>:]]`.
- **Configs, every row**: K (auto engine: DFA unanchored, DFA attempt, VM
  hybrid by pattern), KV (`--engine=vm`), KW (the capture-wrapped `(P)`), KA
  (check + align), A (align alone, well-formed rows), D (the DEFAULT artifact:
  never -9, `valid_upto` still exact, the same answer on every accepted
  range), B (`-e byte`: both flags inert, artifact byte-identical). Every
  entry that takes a subject is driven (`_search`/`_search_in`, `_match`/
  `_match_in`/`_match_caps`/`_match_caps_in`) and required to agree, with
  `caps` untouched on every negative return.
- First green run (pre-regeneration transcript): K/KV/KW 6,025 rows each,
  2,631 refused; KA 1,260 (360 moved, 228 refused); A 840 (280 moved); D
  3,394 + 2,631 tolerant; B 41; LB 42. Final numbers: §5.

### 3.1 FINDING — PCRE2_UTF clips backwards reads at `f` (the design's §1.4 was wrong about the mechanism)

With UTF checking ON, libpcre2 treats `f` (startpos stepped back LB) as
the START OF THE SUBJECT for backwards reads: a `\b` at `f` sees no previous
character, and a nested lookbehind stepping before `f` fails — on
WELL-FORMED text too. So PCRE2_UTF's accepted answer depends on startpos:
`(?<=\ba)b` on `xab` from 2 is (2,3) under PCRE2_UTF (10.46 and 10.48) and
no match from 0 and without UTF. The design said PCRE2 "reads them
unvalidated"; it does not read them. pcrec reads the real bytes (with or
without the flag), which is the answer from startpos 0 and without UTF. On
the three patterns whose reach exceeds LB the accepted answer can differ
(4 cells per config), the refusal set and offset never do; the suite pins
the class EXACTLY and requires each such answer to equal the default
artifact's. Annotated into the design note's §1.4. **Frank may want a ruling
on whether this stays a stated divergence** (the recommendation: yes — the
alternative is an answer that depends on where the caller started).

### 3.2 FINDING — pre-existing: a DFA artifact with dead groups writes `caps` on a no-match

`(?(DEFINE)(?<x>\b))b(?&x)` (a DFA artifact with `RX_NCAPS 2`) returns 0
with `caps[1]` written unset: [DD-14 wave G]'s dead-group fill runs at entry,
before any answer, while match_api.md §3.1 says `caps` is untouched on `0`.
Reproduced on the base compiler (d8d40397), `-e byte`, so it predates this
lane. Not fixed here (out of scope); the -7/-9 refusals are emitted ABOVE
that fill, so every negative return leaves `caps` untouched (the driver
asserts it). Worth a K-row.

## 4. `make test-axes`' `-futf-check` arm

`run_axes.sh` derives the bit, asserts `PCREC_FORCE_UTF_CHECK`/`-futf-check`
is present (FATAL otherwise), skips it in the identity job list, and runs it
through `utfcheck_arm.py`: a byte block must answer identically (inert); a
utf8 block identically iff python finds `[startpos - LB, n)` well-formed (LB
from libpcre2 via the borrowed `pcre2_ctypes` binding; startpos-0 cells need
none), else `utf <offset>`. It reads each case's subject and block back from
the `.rxt` by line; unplaceable lines are counted.

## 5. Validation (Mac, gcc-16) — verdicts are make's `*** [test-X] Error` lines

On the pre-merge branch (`20e79b8d` / src `6c22a7cd`), logs `/tmp/uvbuild_c2_*.log`,
`/tmp/uvbuild_c3_*.log`, `/tmp/uvbuild_enc2.log`:

| target | verdict |
|---|---|
| `make strict` | clean (pre-merge AND post-merge `1777ba5e`) |
| `make test-utfcheck` | EXIT 0: 42 patterns, every config agrees with 10.46 and python; K/KV/KW ≈6.1k rows each, KA 1,260, A 840, D ≈3.4k + ≈2.7k tolerant, B 41, LB 42/42, CLIP 4/config (pinned) |
| `make test-codegen` | the ONLY `*** Error` sources were the accepted darwin `nm arm_a.o` line and a K37 false positive on `run_utfcheck.sh` (fixed in `20e79b8d`: the check now runs under `$TIMEOUT_BIN`); SABANCHOR 375 rows / 391 sites resolve; [M5-SEAM] fixtures green |
| `make test-registry` | EXIT 0 (axes coverage 165) |
| `make test-cpset-structure` | EXIT 0 (manifest re-recorded) |
| `make test-rxtsource` | EXIT 0 |
| `make test-recursion-identity` | EXIT 0 ((B) whole-file identity vs pin `6c22a7cd`: 2,765/2,766 call-free patterns identical per arm) |
| `make test-encoding-checks` | EXIT 0 after DD12a(i) learned `valid_upto` + the `UTF_CHECK` stamp (EXCISED valid_upto=510, utf_check_stamp=510) |
| `make test-cli` / `test-resource` / `test-reject` / `test-startbnd` / `test-search-pinned` / `test-vars` / `test-vm` / `test-examples` | EXIT 0 each |

**Mech** (`bash tests/mech/run_sabotage_matrix.sh S<id>`, logs `/tmp/uvbuild_mech_S*.log`):
S409 DETECTED (utfcheck 192 fail), S410 DETECTED (971), S411 DETECTED
(2,499), S412 DETECTED (1,033), S413 DETECTED (934), S414 DETECTED, and the
re-anchored S368 DETECTED (startbnd). All reach probes ok.

**test-axes**: `AXES="-futf-check"` subset run over `tests/utf8 tests/ucp
tests/vars tests/harness/giveup.rxt` — result in §5.1.

### 5.1 test-axes, `-futf-check` arm (post-merge build `1777ba5e`)

`CC=gcc-16 SKIP_ORACLE=1 AXES="-futf-check" bash tests/axes/run_axes.sh tests/utf8 tests/ucp tests/vars tests/harness/giveup.rxt`
(log `/tmp/uvbuild_axes_subset.log`): EXIT 0. Baseline 4,884 cases; the arm read
`byte=1336 utf8=3498 refused=949 agree=3498 unplaced=50 lb_unchecked=0 guard=0 fail=0 lost=0 gained=0`
— 949 utf8 cells correctly `utf <offset>` against python + libpcre2's LB,
every other cell identical. The 50 unplaced lines (pattern-esc blocks and
other shapes the line reader does not place) are still held to identity.
The identity job list correctly skipped `-futf-check`. Full corpus owed.

### Reproducers for the two findings

```sh
# §3.1 — PCRE2_UTF clips backwards reads at f (libpcre2 10.46 and 10.48):
#   (?<=\ba)b on "xab" from 2: PCRE2_UTF -> (2,3); from 0 -> nomatch; without UTF -> nomatch
#   (?<=(?<=..)a)b on "zzzab" from 4: PCRE2_UTF -> nomatch; without UTF -> (4,5)
printf 'x\t(?<=\\ba)b\t786162\t2\tS\t2\n' | ./probe          # tests/utfcheck/probe_pcre2.c
# pcrec (any -e utf8 artifact, flag or not) answers from the real bytes: nomatch / (4,5).

# §3.2 — a DFA artifact with dead groups writes caps on a no-match (predates this lane, -e byte):
build/pcrec -p rx --features all -o gen.c --pattern '(?(DEFINE)(?<x>\b))b(?&x)'
#   rx_search("zz", 2, 0, caps) returns 0 and sets caps[1] = {-1,-1} (caps[0] untouched);
#   match_api.md §3.1 says caps is untouched on 0.
```

## 6. Owed

- **A Linux full `make test`** (the manager schedules it; not run on the Mac
  per the brief).
- **The full-corpus `make test-axes AXES="-futf-check"`** (only the subset
  in §5.1 ran on the Mac).
- Main was merged into the lane at `1777ba5e` (k75fix, wirechk): the only
  conflicts were TEST_SECTIONS (both `test-encoding-checks` and
  `test-utfcheck` kept) and the lanes index; `make strict` clean after.
  Mech rows use S409-S414 of the reserved S409-S419.
