# substd27: blinded tests of compiled substitution (D27)

Target: `docs/spec/subst_api.md` (plus match_api.md §3.8), tested against the
prebuilt `build/pcrec` in the substd27 cell (abi 84) and libpcre2-8 10.46.
Every pcrec driver ran under `-fsanitize=address,undefined`
(`-fno-sanitize-recover`). The thread case also ran under TSan.

## Counts

About **1,763 distinct cases**:

| suite | cases | result |
|---|---|---|
| differential corpus, 11 families (`corpus/d_*.tsv`), each case run 5 ways (sizing, exact cap, cap−1, cap 0, cap+16 canary) plus a limit-0-then-real FRESH check | 1,473 | 0 sanitizer reports. 0 wrong outputs outside the findings below |
| — tpl / grp / name / empty / lim / bsk / utf / byte / big / nogap / fz | 129 / 112 / 102 / 216 / 48 / 72 / 128 / 33 / 15 / 18 / 600 | |
| API drivers (`api/t_*.c`): bind, element, glue, vars, shape, iter, utf, threads | 214 | 2 FAIL (F6, F8), both DOC |
| CLI and header composition (`cli/cli.sh`) | 76 | 2 FAIL (F5) |

PCREC_REFUSED (pattern refused by pcrec, so not a subst case): 22. These are
`(?|…)`, `\X`, `\R`, and `\K` inside a lookaround. Documented differences
tagged KNOWN: §9 row 9 (BADSPAN / −60) and row 11 (ill-formed UTF-8 global
loop, including `\b`).

**OWED:** the counts above come from the per-family runs I made after the
last corpus edit (only the F7 tag was added after its family ran). A final
clean end-to-end run (`run_all.sh`) was still running when I wrote this.
Its output goes to `/tmp/claude-1001/substd27/run_all.log`, and the
per-suite logs go to `/tmp/claude-1001/substd27/out/{diff_*.log,api.log,cli.log}`.

## Findings (wrong output first)

**F1 — BINARY-WRONG (silent wrong output) vs §2¶1** ("The core language is
PCRE2's non-extended replacement template"). In PCRE2 10.46, `$_` is *the
entire input subject* (pcre2api, in the table that sits beside `$&`, `` $` ``
and `$'`). pcrec parses `$_` as the bare name `_`, greedy over
`[A-Za-z0-9_]`.
- Repro: pattern `(?<_>a)(?<_1>b)?`, template `[$_]`, subject `xab-a`, GLOBAL.
  libpcre2 gives `x[xab-a]-[xab-a]`. pcrec gives `x[a]-[a]`, rc 0.
- `$_1`: libpcre2 renders the subject followed by `1`, and pcrec renders group `_1`.
- With no group named `_`, `$_` and `$_x` are refused at bind
  (MISSING_REF, bad_ref 0), where libpcre2 succeeds.
- Driver: `lib/run_diff.py corpus/d_tpl.tsv` (rows tagged `finding:F1`; also `d_name.tsv`).

**F5 — BINARY-WRONG vs §1¶3** ("a translation unit may include any number of
rx headers and subst headers"). Every header's guard is
`PCREC_GEN_<UPPER(PREFIX)>_H`, for both artifact kinds.
- (a) An rx artifact and its subst under one prefix collide on the guard.
  For example `-p pair --pattern '(a)'` and `-p pair -o pair_sub.c --subst
  '[$1]'`: their symbols do not clash (`pair_info` / `pair_subst_info`).
  Including both silently drops the second header, and the first use is then
  a compile error ("unknown type name rx_subst_binding").
- (b) Prefixes that differ only in case, `sq` and `sQ` (both legal by cli.md
  §1.6¶1), also collide, and so do their uppercase macros (`SQ_NREFS`).
- Repro: `cli/cli.sh` cases `include.same.prefix.rx.and.subst` and `include.case.prefixes`.

**F2 — DOC-WRONG §2¶1 / §9.** PCRE2's `$&`, `` $` `` and `$'` are refused at
compile with "'$' must be followed by…". This is a clean refusal, and §2¶3's
"a byte that starts no reference" covers it. But §2¶1 claims PCRE2's
language, and §9 has no row for these forms (or for `$_`, F1).

**F3 — DOC-SILENT §2¶1 / §9.** Under `-e utf8`, pcrec compiles `(?<é>a)`, but
no template can name that group:
- `${é}` is refused ("must start with a letter or an underscore").
- `$é` is refused.
- `${aé}` is refused ("expected an operator").

libpcre2 renders all three. The braced form's character set is not stated,
and §9 has no row.

**F6 — DOC-WRONG §4¶7.** §4¶7 says "The element writes cur->prev and cur->w;
it writes no other caller state". In fact the element also clears
`cur->fits` once the output stops fitting, which §4¶2 requires. Repro:
`api/t_element.c` `el.writes.fits`.

**F8 — DOC-WRONG §6¶2 vs §4¶2.** §6¶2 says "`out == NULL` sizes only and
returns 0". When the size saturates, the glue instead returns
PCREC_SUBST_NOSPACE with `*outlen = SIZE_MAX`, even when `out` is NULL. The
behaviour is sensible and only the text contradicts it.
- Repro: limit 0 on `RX_ITER_INIT(s, SIZE_MAX)`, or a `${!v}` whose
  `len = SIZE_MAX/2` rendered twice (`api/t_glue.c`
  `glue.saturate.null.out`, `t_vars.c` `var.huge.len.saturates`).
- It is reachable for real on 32-bit targets.

**F4 — DOC-SILENT §9.** Under a utf8 rx, the template is not UTF-checked: an
ill-formed template such as `[\xff]` renders as is, where libpcre2 returns
−23 or −8 for the replacement. This is consistent with templates being
encoding-free, but §9 has no row for it.

**F9 — DOC-SILENT §5¶1.** `--subst` accepts these flags and silently ignores
them: `-e utf8`, `-i`, `--no-captures`, `--engine=vm`, `--emit-main` (no main
is emitted) and `--trace`. The output is byte-identical apart from the name.
§5¶1 names only `--pattern`, a file operand and queries as non-combining.

**F7 — DOC-SILENT, minor (wording tier).** A bare `$` followed by a 129-char
name is accepted at compile and refused at bind. The braced form
`${…129…}` is refused at compile. libpcre2 gives −35 for both. §2¶3 names no
name-length limit.

**F10 — DOC-SILENT, minor §4¶5.** The element returns BADSPAN for a
whole-match pair `{-1,-1}` and for a GROUP span whose end precedes its start.
§4¶5 only describes match spans.

**F11 — DOC-SILENT, minor §3¶7.** `rx_shape_match` treats a forged numbered
needs row with number −3 as satisfied, and the element would then index
`c[-3]`. This only happens with hand-made needs, since the matcher is
documented as generic.

**F12 — DOC-SILENT §6¶1.** Two cases where the glue returns 0, copies the
subject and reports nsubst 0:
- An iterator that is not FRESH (ENDED, or already run by the glue) is
  handed to the glue.
- `rx_iter_at(pos > n)` is set. libpcre2 would return BADOFFSET here.

Also, limit 0 on a `-futf-check` artifact copies an ill-formed subject
without checking it. That follows from "runs no search", but the contract
does not state it.

## Attack families that found nothing

Each item lists what was covered:
- **Empty matches and the NOTEMPTY_ATSTART retry:** 27 patterns × subjects × limits 1/2/3/all.
- **The limit argument:** 0..1000 across batch edges 63/64/65/127/128/129; limit 0 leaves the iterator FRESH; limit 1 runs exactly one search.
- **NOSPACE capacity and count:** at every capacity from 0 to need+16, no write past cap (exact mallocs under ASan), canaries intact, retry example §6¶3 verbatim.
- **Numbered groups and unset:** participation and the unset axis (empty/error, error mid-way, error versus NOSPACE ordering, unreferenced unset groups).
- **Names:** duplicate-name runs (first that participated, set-to-empty participates), names sorted and prefixes of each other, `--no-captures` refusals at bind.
- **`\K` and lookaround:** apart from the documented row 9.
- **The element without GAPS** against `PCRE2_SUBSTITUTE_REPLACEMENT_ONLY`.
- **Byte mode:** NUL and high bytes in subject and template.
- **Group counts:** ncaps > 256 (the kmax=1 path) up to 300 groups.
- **Random-grammar differential:** 600 cases, including `-i` and `--engine=vm`.
- **Bind codes, bad_ref and tag:** codes and bad_ref on every path; the tag is not BOUND after a refusal that follows a success.
- **abi and record forgeries:** at bind and in the glue (dlopen case).
- **Element call checks:** k=0, every unknown flag bit, ncap mismatch, other artifact's binding.
- **Saturation arithmetic:** at SIZE_MAX−1 and SIZE_MAX.
- **`${!name}` variables:** NULL p, len 0, absent, duplicates, NULL names, unset=error before any output (no match, limit 0).
- **Iterator outcomes:** give-ups (−2 with 0/0, beating NOSPACE), PCREC_ERR_ITER, STARTPOS, UTF (`-futf-check`), the align guard.
- **Concurrency:** one binding across 8 threads (ASan and TSan).
- **Headers:** include orders, repeated headers, the abi `#error`, `PCREC_SUBST_PAIRS` 0/1/2/3/4/64/256/100000, self-contained `-o -` (two in one TU).
- **Doc examples:** §7¶5 and §6¶3 compiled verbatim.
- **Emitted-C hygiene:** template bytes `*/`, trigraphs, `\`, and newline are all escaped; warning-free under c99/c11/c17 with -Wall -Wextra -Werror.
- **CLI:** mode exclusivity, `--unset=` values, prefix rules, `--subst-file` byte-for-byte including NUL, offsets in refusals, nothing left behind on a refusal.

## Layout (committable as a corpus)

- `run_all.sh [PCREC]` regenerates the corpus and runs everything.
- `corpus/gen_corpus.py` and `gen_fuzz.py` write `d_*.tsv`. Columns and modes are documented in `lib/run_diff.py`.
- `lib/` holds `run_diff.py` (the runner), `ref_pcre2.py` (the libpcre2 reference via ctypes, with limit N emulated by a substitute callout), `diff_driver.c` and `esc.py`.
- `api/` holds `build.sh` and the `t_*.c` drivers.
- `cli/` holds `cli.sh` and `inc_body.c`.
- `out/` is scratch and is not part of the corpus.

## Disclosure

- **Injected at spawn, not used:** `/home/pcrec/projects/pcrec/CLAUDE.md`, `~/.claude/CLAUDE.md`, and the memory index `MEMORY.md`.
- **Read inside the cell:** `docs/spec/CLAUDE.md`.
- **The cell is a git repository:** it contains a `.git` directory (the brief said it would not). I did not query it.
- **Emitted C:** I read the C that `build/pcrec` emits (the product under test, not pcrec's source) to learn the API names.
