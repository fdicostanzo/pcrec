# ADVERSARY — ic1b-code
critic: adversary (untrusted-input author), model: opus; started 2026-10-26 16:10; status: COMPLETE

## ADV-1 `(?C"ref")` binds `rx_callout_ref`, the ABI typedef: artifact does not compile
- status: CONFIRMED
- severity: answer
- effort: S ; blast radius: any pattern naming the binding `ref` (every prefix; the typedef is the shared, unprefixed ABI block)
- where: src/parse/mod_callouts.c:149-170 (name gate: C ident + no `__` only); docs/spec/match_api.md §11.2¶2, cli.md namespace table row 2
- repro: `build/pcrec --features classes,modifiers,callouts -p rx -o ref.c --pattern 'a(?C"ref")b'` -> rc=0, then `gcc -O2 -c ref.c`:
  `ref.h:276: error: 'rx_callout_ref' redeclared as different kind of symbol` (`extern const rx_callout_ref rx_callout_ref;` vs the typedef at ref.h:65).
  Expected: a compile-time refusal (the spec's binding-name rule should reserve `ref`), or a never-colliding binding family.
- argument: the namespace table claims the `rx_callout_<name>` family is clear of every emitted/reserved name; the fixed ABI name `rx_callout_ref` (match_api.md line 162 lists it among the reserved `rx_*` types) is itself IN that family. pcrec accepts and emits C that gcc rejects — "emitted C that is not what the spec says". Fix: refuse name `ref` (and say so in pattern_language.md §7.11 / match_api §11.2), or rename the typedef out of the family (abi event).
  Precedent: match_api.md §2¶11 (D57) already refused a typedef `rx_info` for exactly this reason (an object of the same identifier cannot coexist with a typedef); the callout family re-opens the hole.

## ADV-2 Unknown-attribute diagnostic echoes raw pattern bytes (ESC, BEL, bidi) to the terminal
- status: CONFIRMED
- severity: maintenance (diagnostic hygiene; (c) of the brief)
- effort: S ; blast radius: every `(?C"name,<junk>")` refusal; also the `.rxt` `callout` line and `--callout` refusals (`'%s'` of the raw value, rxt_source.c:3810, cli/main.c:1089)
- where: src/parse/mod_callouts.c:77-79 (`'%.*s'` of the attribute text, unescaped)
- repro: `build/pcrec --features classes,modifiers,callouts -p rx -o e.c --pattern "$(printf 'a(?C"x,\033[31mRED\007")b')" 2>&1 | od -c` -> `unknown callout attribute ' 033 [ 3 1 m R E D \a '`: raw ESC and BEL reach stderr.
  Baseline: the pre-existing pattern refusals I probed (`\k<ESC..>`, `(*ESC..)`, `\p{ESC..}`, `(?<xESC..>`, `(*MARK:ESC..)` under --features all, 5 cases) echo NO pattern byte; this is the first parser diagnostic that does.
- argument: a hostile `.rxt`/pattern can drive the reader's terminal (colour, title, bidi reordering of the message) through pcrec's own error text. The house already has the escaper for this (`pcrec_sb_text`, internal.h:519-536, "protects the frame"); use it for the attribute echo. (CLI-argument echoes like `--features` are pre-existing raw and the user's own bytes; the `.rxt callout` line echo is file-borne, so it belongs in the same fix.)

## ADV-3 `.rxt` `callout 13once`: the harness accepts it as `13:once`, pcrec refuses it
- status: CONFIRMED (pcrec side run; harness side from its regex, run.sh:2790, not executed)
- severity: answer (test-verdict divergence between the format's two readers)
- effort: S ; blast radius: any `.rxt` callout line with no space between N and ATTRS
- where: tests/harness/run.sh:2790 `^callout[[:space:]]+([0-9]+)[[:space:]]*([a-z,]*)[[:space:]]*$` (`[[:space:]]*` admits zero) vs src/parse/rxt_source.c:3803 (requires a space/tab after N)
- repro: block `pattern a(?C13)b` / `features all` / `callout 13once` / `m "ab" 0 2`; `build/pcrec -o out c.rxt` -> `[value-shape] c.rxt:3: 'callout' wants ... (got '13once')`. The harness regex matches it and passes `--callout 13:once`, so the suite runs the block as `once` and passes a file pcrec itself refuses.
- argument: rxt_format.md §1.5¶13a gives one shape; two readers of one format must agree (learnings §3: a control that shares nothing with what it controls). Fix: `[[:space:]]+` before the attrs group when it is non-empty (or `([[:space:]]+([a-z,]*))?`).

## ADV-4 `.rxt` `callout 13 consume once` passes the file reader, then fails in the CLI with no file:line
- status: CONFIRMED
- severity: doc (diagnostic location lost)
- effort: S ; blast radius: `.rxt` callout lines with internal whitespace in ATTRS
- where: rxt_source.c:3805-3807 admits ' '/'\t' anywhere in ATTRS; cli/main.c:1080-1082 (`cli_callout_decl`, sep ' ') refuses them; the cli_err at 1089 carries neither file:line nor target (contrast 2130 and rxt_fail's `[value-shape] file:line`)
- repro: same block with `callout 13 consume once` (also `consume, once`) -> `pcrec: a callout declaration is N ATTRS (... got '13 consume once')` — no path, no line, no target, no `[value-shape]` class tag.
- argument: rxt_format §1.5¶13a says "the line's shape is checked where it is read"; here a shape error escapes the reader and surfaces untagged from a second shape check. One shape reader (or the rxt reader's charset = the CLI's `[a-z,]`) closes it.

## ADV-5 `(?C"x,")` accepted: a trailing empty attribute is refused only when something precedes it
- status: CONFIRMED
- severity: doc (grammar hole, harmless output)
- effort: S ; blast radius: `(?C"name,")`; `--callout 1:once,` refused but `(?C"x,")` accepted
- where: mod_callouts.c:171-175 calls pcrec_callout_attrs with n==0 after the comma; the empty-item check (94-96) lives inside the loop that n==0 never enters
- repro: `--pattern 'a(?C"x,")b'` -> rc 0, binds rx_callout_x; `'a(?C"x,once,")b'` -> "empty callout attribute after ','"; `'a(?C"x,,once")b'` -> "unknown callout attribute ''".
- argument: inline_c.md §2.2 grammar `ident(,attr)*` has no `ident,` production; three spellings of "empty item" get three answers. Fix: `if (id < n)` with `id + 1 == n` -> the same "empty callout attribute" refusal.

## ADV-6 harness.manifest `link FILE`: "beside the manifest" is not enforced; same-basename sources alias; extra tokens dropped
- status: CONFIRMED (manifest_objs replicated verbatim in scratch with a stub gen_cc; run.sh not run)
- severity: maintenance (trust boundary is the test-dir author, so not a security hole; contract mismatch)
- effort: S ; blast radius: any directory carrying harness.manifest (today tests/callouts only, `link stubs.c`)
- where: tests/harness/run.sh:1652-1677; spec rxt_format.md §6¶3 table ("a path beside the manifest"), §6¶4 ("any other manifest line is a harness failure")
- repro: manifest `link ../../evil.c` / `link a/stubs.c` / `link b/stubs.c` / `link one.c two.c` ->
  (1) compiles `<mdir>/../../evil.c` (outside the directory; a symlink beside it would too);
  (2) `a/stubs.c` -> `manifest_stubs.o`; `b/stubs.c` maps to the SAME object, `[ ! -f "$obj" ]` skips its compile and the object is listed twice (b/stubs.c never compiled; link then fails on duplicate symbols, blaming the wrong file);
  (3) `two.c` silently ignored (`read -r kw arg rest`; `rest` unused) — a malformed line that §6¶4 says is a failure.
- argument: the spec's two promises (beside; any other line fails) are claims the reader does not check. Fix: refuse an `arg` containing `/` or a non-empty `rest`, matching §6¶3-4 (a few lines).

## PROBED-AND-HELD
- Delimiters (8 forms: " ` ' ^ % # $ {}) with plain names: all accepted, bind rx_callout_x, `gcc -c` clean (8/8). Doubled-delimiter decodes (`"x"",once"`) and `*/`, empty string, unterminated: refused before emission (4/4). `{x}}`/`$x$$` refused as malformed (correct: the doubled close is a literal, string unterminated, as in PCRE2).
- Names: `int`, `main`, a 5000-char name: accepted, compile clean (no collision: `main` is `rx_callout_main`). Non-ident / UTF-8 / control bytes never reach emitted C: the name gate admits [A-Za-z0-9_] only, and only `ref` (ADV-1) collides. Leading `_` (`_`, `_X`) emits `rx_callout__`/`rx_callout__X`: `__`-shaped, but only a `rx_callout` prefix could own that family and it is refused, so no live collision (noted, not filed).
- `-p` interplay: `rx_callout`, `rx_callout_`, `rx_callout_x` refused per cli.md namespace row 2; `rx_callou`, `RX_CALLOUT`, `rx_Callout` accepted and collision-free. Two artifacts (-p rx, -p foo) sharing a binding in one TU: compile clean (RX_PASS/RX_FAIL guarded by a fixed PCREC_RX_CALLOUT_H).
- Pattern comment line (`Pattern: ...`): `*/` and `/*` escaped as \x2f/\x2a; gcc clean.
- Numbered: `(?C)`, `(?C007)`, 20-digit leading-zero `1`: accepted as 0/7/1; `+1`, `-1`, `256`, `(?C 1)`: refused (7/7).
- Attributes: repeated, `,,`, ` once` refused; `--callout` overflow guarded per digit (n>255 aborts before int overflow); `1:` (empty) accepted (spec allows); duplicate numbers refused ("declared twice"); undeclared-site numbers refused.
- `--emit-main` with a callout: refused with the §1.10¶2 text.
- Manifest lookup per-.rxt directory: output object dirs are per block/batch (`$WORKDIR/b<n>`, `hb<seq>`), so no stale object crosses .rxt files.
- `--emit-ir` callouts section carries only ident names and fixed `why` strings.
