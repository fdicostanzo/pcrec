# Review r2 (2026-10-22): [M4-SUBST] design R4 light panel, `replace_design.md` §R4 + `subst_api_r4_draft.md`

Panel: two read-only critics (light panel).
- `substr4c1` took PCRE2 semantics, probed against libpcre2-8 10.46 through
  ctypes (scripts on stdin, nothing written).
- `substr4c2` took the interface (embedder, family, unlocks). It ran nothing.

Target: `lane/subst` @ 7cea1fcb6 (design R4, rulings R4-R8 of
`docs/dev/lanes/subst_rulings.md`). Dispositions are the manager's (all
ADOPT); lane `substr4b` applied them as §R4.15 of the note plus in-place
edits, and the last column says where. The critics' full reports are in
their session transcripts; the text below is condensed.

**Verdict.** Three high findings from C1 and two from C2, all real. The
case-forcing rule as drafted was wrong (C1-1); the reference recipes could
end in a silently wrong answer (C1-7, C2-1); a template error was invisible
on a subject with no match (C2-2). None changes the rulings: the design
keeps the optional map, pieces, no malloc, the scratch buffer and the
support unit. Two decisions moved: the check now runs once at context setup
and is emitted inline (open question 3 adopted), and the `\NN` refusal
widens to every group-count-dependent escape (open question 4).

**Lane re-verification (substr4b, libpcre2-8 10.46, ctypes, read-only).**
- C1-1: the 4-rule machine against libpcre2 on 16 named cells (all match:
  `\Ua\ubc` ABc, `\L\uabc` Abc, `\u\U\Lab` ab, `\u\Lab` Ab, `\l\UAB` aB,
  `\L\uAB` AB, `\U\lab` ab, `\u\Uab` AB, `\l\Uab` aB, `\U\uab` Ab,
  `\Ua\Lb\ucd` AbCd, `\L\u$1` on hELLo HELLo, `\u$1\Lx` HELLox, `\UaB\EcD`
  ABcD, `\u\E$1` hELLo, `\U\L\uab` Ab) and 3,000 random sequences of up to 7
  tokens over `\U \L \u \l \E a B $1`: 0 mismatches.
- C1-2: the two SIGSEGVs reproduced (exit 139, each in its own process) and
  the read-past (`"abc\xc3"` → `\xc3\x80`); the no-case control renders
  correctly. Filed as `docs/dev/upstream_issues.md` U22 (U21 is taken by lane
  corefix).
- C1-3: single digits probed on 0, 1, 3 and 9 groups: `\1`-`\9` are ALWAYS
  group references (a missing group is −49, as `$n`), never octal, so their
  meaning does not depend on the group count and they stay accepted. Every
  `\[1-9]\d+` does depend on it: `\10` 0x08 / group 10, `\12` LF / group 12,
  `\77` `?` / group 77 (below 101 groups the byte), `\81` −49 / group 81,
  `\101` `A` / group 101, `\400` −57. `\0`, `\01`, `\012` are octal on any
  pattern, `\08` is NUL then `8`.
- C1-4: `\Uß` and `\U\x{df}` → U+1E9E (3 bytes), `\LȺ` → U+2C65 (3 bytes).
- C1-10: `[${1:-\Qa}b\E}]` with group 1 unset → `[a}b]`; `[${1:+a\Q:\Eb:c}]`
  set → `[a:b]`; an open `\Q` inside text → −58, at top level it runs to the
  end; `[$9]` under UNKNOWN_UNSET without UNSET_EMPTY → −55, with it `[]`.

## Findings and dispositions

| id | sev | finding (condensed) | disposition | where |
|---|---|---|---|---|
| C1-1 | HIGH | the case rule is wrong: `\Ua\ubc` is `ABc` (draft: ABC), `\L\uabc` is `Abc` (not "acts as `\U`"), `\u\U\Lab` is `ab`. A 4-rule machine fits 24,255 cells: `\U`/`\L` drop a pending one-shot only when a region is set; `\u`/`\l` set the one-shot and CLEAR the region; `\E` clears both; a character takes the one-shot first, else the region | ADOPT: a DECLARED STATE TABLE (first-match per event) with its witnesses as oracle rows | draft §2¶13; note §R4.13, §R4.10 tests |
| C1-2 | HIGH | case forcing over ill-formed UTF-8 has no oracle: libpcre2 segfaults (`\U$_` on `b` over `"ab\xffc"`, `\U$'` over `"abc\xc3\xa0\xff"`) and reads past `$_` on `"abc\xc3"` | ADOPT: ill-formed bytes copied unchanged, 1:1 in sizing; cells out of the differential; upstream row | draft §2¶14a, §9 row 19; `upstream_issues.md` U22 |
| C1-3 | HIGH | `\ddd` accepted while group-count-dependent escapes are refused, but `\101` is one (group 101 or `A`); also `\77`, `\81`, `\400` | ADOPT: refuse every `\[1-9]\d+`; single `\1`-`\9` probed NOT group-count dependent, so kept; accept `\0dd`, `\o{}`; the contradicting rows fixed | draft §2¶10, §2¶12, §9 row 16; note §R4.9 Q4, §R4.13 |
| C1-4 | MED | the scratch bound undercounts: forced CONSTANTS grow (`\Uß` 3 bytes against 2; `\L` U+023A → U+2C65) | ADOPT the runtime form: 1.5× every byte entering the region, rounded up. The compile-time stamp was rejected: a constant's forced form depends on run-time case state, so it is a worst case anyway, and it costs a stamp, an abi reader and a record field to save half of a few bytes | draft §4¶22; note §R4.13 |
| C1-5 | MED | the template's encoding is compared only by helper (C): `\U$1` under the default `-e byte` with a utf8 rx renders `STRAßE` silently (PCRE2 `STRAẞE`) | ADOPT (with C2-4): the setup and the check take the rx's record and compare encodings | draft §2¶5, §3¶8-¶10, §7¶3; note §R4.4 |
| C1-6 | MED | sizing vs BADSPAN order undefined: `x(?=(?1))\|(b\K)` on `"xb"` with `\U$0` sizes `1 − 2`, NOSPACE asks for ~`SIZE_MAX` | ADOPT: the sizing pass validates as it goes and stops at the first failing match; NOSPACE covers only the committable prefix | draft §4¶14, §4¶21; note §R4.5 |
| C1-7 | MED | the recipes are unsafe: `sn` never reset; every recipe writes the tail after `rc < 0`; growing scratch dangles pieces in `pc[0, n)` | ADOPT (with C2-1, C2-8): one error rule, no tail on any negative code, `sn` reset with `n`, scratch grown only from `n == 0`; forced give-up / BADSPAN / NOSPACE recipe tests | draft §4¶4, §6; note §R4.5, §R4.7, §R4.10 |
| C1-8 | LOW-MED | nothing forbids scratch overlapping the subject, the variables or `pc` | ADOPT: a no-overlap rule (UNDEFINED otherwise) | draft §7¶1a |
| C1-9 | LOW | "p never NULL" collides with the legal `(NULL, 0)` subject and unset variables; `k * P` and `n + k * P` unchecked | ADOPT: the named sentinel `rx_subst_empty`; overflow is NOSPACE with `SIZE_MAX` | draft §4¶9, §4¶14; note §R4.5 |
| C1-10 | LOW | `\Q` protects `}` and `:` in conditional text, and an open `\Q` there is −58; NOGROUP under STRICT renders blank where PCRE2's UNKNOWN_UNSET without UNSET_EMPTY gives −55 | ADOPT: both rows | draft §2¶9, §2¶10, §9 row 20 |
| C2-1 | HIGH | §6¶2 breaks on `rc < 0` and writes the tail; `it.rc < 0` (give-up) is a normal loop exit, never checked; `RX_FOREACH`'s recipe never mentions `it.rc` | ADOPT (with C1-7) | draft §6 |
| C2-2 | HIGH | "one check before output" is unobservable on a zero-match find-all: the check lives in `render` | ADOPT: the check runs once at context setup; the per-render check becomes an O(1) memory-safety re-assert plus one range compare per slot the walk reads | draft §3¶8, §3¶12, §4¶10-¶14, §7¶4; note §R4.4 |
| C2-3 | MED | the `(const ptrdiff_t (*)[2])` cast in every recipe hides a wrong caps type | ADOPT: one spelling, `ptrdiff_t (*caps)[2]`, exactly as `<prefix>_next`/`_next_n` (lane/i2build's spec, and this branch's) and `RX_FOREACH`'s `m`; the element only reads it. (`rx_ctx.caps` stays `const`: a field the element does not use) | draft §4¶1, §6; note §R4.2, §R4.7 |
| C2-4 | MED | `ncaps` is an unchecked caller constant; a map-less `$3` on a composed rx reaches a delivered group | ADOPT (with C1-5): the setup takes `rx_info`; no map on a composed rx (`ncaps > ngroups + 1`) is refused | draft §3¶3, §3¶10; note §R4.4 |
| C2-5 | MED | `RX_SUBST_MAP_ABSENT` is all-or-nothing; a typo'd name vanishes | ADOPT: `size_t *nabsent` (with `*bad_ref` the first); the option recommended off | draft §3¶13-¶16 |
| C2-6 | MED | the support unit can change behaviour (UCD, flatten fix) without an abi bump; two units of one abi clash or are silently picked | ADOPT: `pcrec_support_id` content id, compared by the check through the record's `support` pointer (NULL for templates that never call the unit, so they stay link-free); the unit's text is an abi reader (D76/D94) | draft §1¶4, §3¶1, §10¶3; note §R4.14 |
| C2-7 | LOW | library + application both defining the implementation; the case-only stamp collision has no `#error` | ADOPT: `PCREC_SUPPORT_STATIC`; `#ifdef <PREFIX>_PIECES` → `#error` | draft §1¶3, §10¶3a; note §R4.14 |
| C2-8 | LOW | the flatten recipe computes `w + need` before testing `need == SIZE_MAX` | ADOPT (with C1-7): overflow tested first | draft §6¶4 |

## The open questions (C2's answers)

| # | question | C2's answer | disposition |
|---|---|---|---|
| 1 | piece byte type | `const unsigned char *` | stays OPEN for Frank (leaning unchanged) |
| 2 | support unit emitted or shipped | emitted (`--emit-support`), plus content id and static mode | stays OPEN (leaning unchanged; C2-6/C2-7 applied) |
| 3 | is linking mandatory | no: emit the small check inline, `static`, under the shared guard; only helper and case-forcing users need the unit | ADOPTED (note §R4.4). Lane note: `rx_subst_ctx_init` is inline too, because it runs the check and the recipes' setup needs no unit otherwise |
| 4 | refusing `\NN` | accept the refusal, with a pointed diagnostic | WIDENED by C1-3 to every `\[1-9]\d+`; stays open for Frank |
| 5 | dropping the generic glue loop | confirm, with C2-1 fixed | C2-1 applied; stays open for Frank |

## Family lens

| item | disposition | where |
|---|---|---|
| (a) the case map is not a new data set | VERIFIED and adopted: `third_party/ucd-16.0.0/generate.py` already reads `CaseFolding.txt` (the fold orbits, `src/core/fold_tables.inc`) and `UnicodeData.txt` (general category), and already emits `src/enc/utf8_fold_pairs.inc`; PCRE2's rule (the other orbit member, chosen by category) needs nothing else, and UnicodeData's own uppercase column would be wrong (`00DF` has none, so `ß` would stay). The case table is a third output of the one generator; the control is a new question kind in `oracle_store/libpcre2-10.46/` | note §R4.12 |
| (b) the template escape decoder reuses the pattern parser's | VERIFIED: `esc_char_value` (`src/parse/parse.c`; control escapes, `\x`/`\x{}`, the digit branch returning "backref/octal"), the registry definitions for `\o{}`, `\cX`, `\N{U+}` (`src/parse/registry.c`), and `pcrec_clsport_octal` for `\0dd`. The brief's line numbers were approximate; functions are cited instead | note §R4.10 |
| (c) `rx_group_run` shares one implementation with match_api §5.4¶6 | ADOPT: it is THE implementation of that lookup; later by-name consumers call it | draft §3¶17 |
| (d) a shared stamp-header prefix across `rx_info` and `rx_subst_info` (`abi`, `name`, `encoding`, content id) with one skew check | CANDIDATE, not adopted. Trigger: a third record kind, or the first version-skew report | this file |
| (e) `--emit-support` in the CLI emit-mode table | ADOPT in substance: cli.md has no emit-mode table (the emit commands are separate subsections, §1.10, §2.10, §2.11), so it gets its own subsection naming those siblings | note §R4.14 |

## Unlocks (candidates; none scheduled)

| unlock | why | trigger |
|---|---|---|
| a case-callout slot in the context, mirroring `pcre2_set_substitute_case_callout` (present in 10.46) | the exact sizing pass already absorbs any length change; gives full and locale mappings (`ß` → `SS`, Turkish i) | a user who needs more than simple case mapping |
| the declared case state table driving the emitter, the D27 cell generator and the oracle rows | one table, three readers (Frank's first-match-table doctrine) | the build of `subst-extended` |
| static pre-mapping of constant runs in a case region where no conditional precedes them | saves the run-time pass over constants | a hot `\U` template in a profile |
| a general caller-owned output sink: pieces plus `need`/`sneed` as "emit by reference" | `grep -o`-style extraction, a `writev` streaming writer, parallel find-all | the first stream or iovec consumer (the streaming design's cell, or a grep example) |
| validate-at-init bound templates: one validated context as a "template bound to rx" object | per-find-all validation cost, a safe no-map fast path | partly delivered by C2-2 (the check at setup); the rest when the find-all bench shows the per-call re-assert in a k = 1 loop |

## What the panel confirmed sound (C1)

The `:-` and `:+` semantics and nesting as drafted; NOGROUP is PCRE2's
UNKNOWN_UNSET (`${9:-D}`, `${zz:-D}` render `D`); a pending `\u` never leaks
into the gap or the next match, crosses empty and unset pieces, and `\E`
cancels it; PCRE2 never maps across ASCII (`ı`, KELVIN SIGN and `İ`
unchanged), so 1-byte characters never grow and the 1.5× factor is right;
pieces and no-malloc hold for every non-case form.
