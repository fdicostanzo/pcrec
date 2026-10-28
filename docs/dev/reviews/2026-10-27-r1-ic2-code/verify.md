# Verify ic2

## Results
Of 17 brief items (about 30 finding IDs), all HOLD as the critics stated, or are latent (ADV-4/CON-13 unreachable today, no route compiles). PARTLY: ADV-5 (facts rows polluted; the .h stamp is not changed, only the translation unit's macro). Refinement on EMIT-2: the ~1.9x over the VM twin is also what BASE's binding costs (not a regression). Nothing REFUTED. I wrote only under crit-ic2/verify and verify.md; no denylisted file opened.

### CON-1 (+ADV-1, ADV-3): HOLDS
Cmd: `pcrec -p rx --emit-main -o o.c --allow-code=c --pattern 'a(?C`c: /* <cp> */ return RX_PASS;`)b'` for each cp.
Observed: U+061C rc0, U+3164 rc0, U+E0041 rc0, U+2028 rc0 (all compile); U+202E rc1 ("contains U+202E ... invisible or bidirectional control").
PropList.txt:28 `061C ; Bidi_Control # Cf ARABIC LETTER MARK` (yes, Bidi_Control).
Means: the refusal list omits a Bidi_Control code point and Default_Ignorables; spec wording over-claims.

### ADV-2: HOLDS
Cmd: pattern (raw CR byte via bash $'..', passed with --pattern, not pattern-esc) = ``a(?C`c: // x<CR>return RX_FAIL;<LF> return RX_PASS;`)b``, `--allow-code=c --emit-main`, gcc -O1, run on `ab`.
Observed: pcrec rc0 accepted; emitted line 566 `        // x^Mreturn RX_FAIL;` ; binary prints `nomatch` (rc1). Control (same without the CR statement, newline instead) prints `match 0 2`.
Means: lone CR accepted and gcc takes the hidden statement; a reviewer's terminal shows the line overwritten.

### CON-8 / EMIT-4 / CHK-2: HOLDS
Cmd: compile ``(?:ab|(x)+)(?C`c: return RX_PASS;`)\1`` (--features all --allow-code=c), take text before first `#define RX_SUBJ`, `gcc -E -dM`.
Observed: live before segments: RX_CUT (line 119), RX_CHARGE_WORK (95), RX_R_STEPS (89), RX_SLOT_WHOLE_START (46) etc.; `grep -c '^#undef RX_(CUT|SLOT|R_|CHARGE)'` = 0.
Source: emit_code.c:160 `{ "\x01Q_", false }, /* <PREFIX>_* stamps */` keeps all; run_code_tests.sh:298 `grep -vE "^(_|${upx}_|PCREC_|RX_PASS$|...|${upx}_H$)"` exempts the same family. Design inline_c.md:983 says RX_CUT/RX_PRUNE_*/RX_SLOT_*/RX_R_* are undef'd.
Means: design promise unmet and the check cannot see it (same source family on both sides).

### ADV-4 / CON-13: HOLDS as latent; UNREACHABLE today
Routes tried (--features all --allow-code=c; .rxt with `target t = top`, definition `d` holding a code segment at offset ~25, `top` = `z<call>`): `(?&d)`, `(?P>d)`, `\g<d>`, `(?&s=d)`, `(?&*=d)`, `(?&=d)`, `(?&d){0}q`, and `--pattern` with `(?(DEFINE)(?<d>..(?C`c:..`)))z(?&d)`: all rc1 "a callout inside a group reached by a subroutine call or recursion (including a lib definition) is not supported". `target t = d` (definition as the target): rc0, but then cx->pat is d's own pattern (no mismatch). Uncalled definition: rc0, zero `#line`/segments emitted (never parsed).
Means: no route reaches code emission from a definition; the code_at/cx->pat mismatch is latent for stage 3 only. The OOB read was not exercised (not reachable).

### ADV-5: HOLDS (facts rows); stamp PARTLY
Cmd: segment text with lines `#define RX_FAKE 1`, `#undef RX_CODE_LANGS`, `#define RX_CODE_LANGS "zzz"`; `--allow-code=c --emit-main` and `--emit-facts`.
Observed: compiles rc0, gcc -Wall -c clean. facts: line 54 `byte RX_CODE_LANGS "c"` (real) plus line 106 `byte RX_FAKE 1` and 107 `byte RX_CODE_LANGS "zzz"` (decision rows from segment text). The stamp is `#define RX_CODE_LANGS "c"` in the .h (a5.h:364), which is unchanged; but `gcc -E -dM a5.c` ends with `RX_CODE_LANGS "zzz"` and RX_FAKE 1 (the TU's effective value).
Means: describe-mode record is polluted by segment text; the header stamp file itself is not altered, the translation unit's macro is.

### ADV-6: HOLDS
Read: run.sh:1692 `allow-code)` arm only checks SHAPE (one non-empty operand); run.sh:1715-1723 `manifest_allow_code` takes any `$(dirname "$rxt")/harness.manifest` `allow-code` line for an ENTRY file, no directory test. Existing grants: tests/code/harness.manifest:5 and tests/code/frag/harness.manifest:4 only. `grep -rn allow-code tests scripts Makefile | grep manifest` finds no check (allow-list or count) restricting it to tests/code/. (S1684 sabotage covers fragment-vs-entry only.)
Means: any tests/ directory with a manifest line would be granted code under plain make test; nothing limits it.

### SLOT-4 / SLOT-6: HOLDS
`grep -rn 'INVOKER_ONLY|invoker-only' src tests lib`: tests/registry/registry_check.c mentions it only at :1260 (refusal wording) and :2486 (by-name engine refusal); NO check that rows of one module agree. Yet src/parse/enabled.c:176-177 says "Every row of a module carries the same value (registry_check asserts it), so the first row answers" and module_invoker_only (enabled.c:178-190) returns the FIRST row's flag. `all` arm (enabled.c:295) tests the flag per ROW; the named-set arm (enabled.c:~309-318) does `mask |= find_module_bits(m, strlen(m))` with no module_invoker_only/flag test (quoted above); safe only because the only named set (std1) holds no code module.
Means: the comment's claim of an assertion is false; a mixed-flag module or a code module added to a named set would escape the gate unchecked.

### CON-10 / SLOT-5: HOLDS
Cmd: `pcrec -p rx <opts> --pattern 'a(?C`c: return RX_PASS;`)b'`. `--allow-code= --emit-ir` rc1 "requires module 'code-c', which only ... --allow-code=c ... enables"; `--emit-ir` rc0 (3715 bytes); `--allow-code= --count-groups` rc0 and `--count-groups` rc0 (both print the count); `--allow-code= --emit-facts` rc1 (same refusal).
Means: an explicit empty grant makes describe modes (emit-ir, emit-facts) refuse while the unset grant parses code; count-groups is unaffected.

### EMIT-1: HOLDS
Cmd: ``a(?:(?C`c: return RX_PASS;`)){0}b`` and ``(?(DEFINE)(?<d>x(?C`c: return RX_PASS;`)))ab`` (--allow-code=c --features all --emit-main), then `gcc -O2 -Wall -Wextra -Werror -c`.
Observed: both pcrec rc0; gcc rc1: `error: 'rx__code1_ref' defined but not used [-Werror=unused-const-variable=]` (e1.c:121, e2.c:124). Control (reached site `a(?C..)b`) gcc rc0.
Means: an unreached code site emits an unused static const that breaks -Werror builds.

### CON-2 / SLOT-12: HOLDS
Cmd: .rxt with 257 `code-header c "hN.h"` lines (distinct), `target t = top`, one code pattern; `pcrec --allow-code=c -o out h.rxt`.
Observed: rc0, no diagnostic; out has 256 `#include "h..h"` lines (last `#include "h256.h"` at line 1030); h257.h absent. Source cli/main.c:2198-2203: `PcrecCodeHeader hdrs[256]; int nh = 0; ... nh < 256`.
Means: the 257th header line is silently dropped.

### CON-6: HOLDS
Cmd: ``()(?C`c: return rx_eq(RX_CAP(1), "") ? RX_PASS : RX_FAIL;`)`` ; driver calls rx_search(NULL,0,0,caps) and rx_search("",0,0,caps).
Observed: `NULL subject: 0, empty non-NULL subject: 1`. emit_code.c:41 as quoted above (`!s.p || s.len < 0`).
Means: group 1 matches empty on both subjects, but on a NULL subject rx_eq reads it as unset.

### CON-9: HOLDS (order-dependent)
Cmd: file with `target free = fr` (code-free) and `target code = cd` (code), no grant, `-o DIR`.
Observed: rc1 refusal at the code target; DIR contains free.c and free.h (written before the refusal). With the code target declared FIRST, nothing is written. With `--allow-code=c` all four files are written.
Means: a refused build leaves partial output of earlier targets.

### CON-7: HOLDS
Cmd: `code-header c <stdint.h>` + ``(a)(?C`c: return RX_CAP(1);`)c`` (m.rxt, 4 lines), `--allow-code=c`, `gcc -fsyntax-only t.c`.
Observed: t.c:547 `#line 1 ".../m.rxt"` then `#include <stdint.h>` (548) and the next `#line` is 564 (the segment); gcc: `m.rxt:12:34: error: incompatible types ...` and `m.rxt:4:26: note: in expansion of macro 'RX_CAP'`. t.c:558 (=547+11, the macro line) is attributed to m.rxt line 12 of a 4-line file.
Means: the macro-set lines inherit the header's `#line`, so a diagnostic points at a nonexistent .rxt line.

### CON-5 / CON-11 / CON-4: HOLDS (all three)
CON-5: `--allow-code=c --code-header c: --pattern ab` -> stderr `malloc: Success`, rc1.
CON-11: ``(?C`c,verify: ..`)`` -> "module 'callouts' is enabled but the callout attribute 'verify' is not implemented yet" (callouts not enabled in that compile); ``(?C`c,: ..`)`` and ``(?C`py: x`)`` -> "(?C...) requires module 'callouts'"; with `--features callouts` ``c,:`` -> "unknown callout attribute ': return RX_PASS;' ...".
CON-4: `pcrec --help | grep -c 'allow-code\|code-header'` = 0.
Means: wording/discoverability defects as stated; behaviour (refusal) is right.

### EMIT-2 / EMIT-3: HOLDS
Method: driver = emitted/code/drv.c (find-all), 1 MiB subject, gcc -O2, `perf stat -e instructions:u taskset -c 7`, 3 repeats, unity builds via `-include`.
EMIT-2 (non-reaching path): ``(\d+)(?:y|z(?C`c: return RX_PASS;`))`` on `12y 345y 6y ` = 56,320,338 / 334 / 337 vs twin `(\d+)(?:y|z)` `--engine=vm` = 29,319,265 / 263 / 274 (both 262,146 matches). Zero fires: the same segment replaced by `__builtin_trap();` runs rc0, no trap. Stamps: segment X_VM_FRAMELESS 0 / ENTRY_SHAPE "plain" / NSLOTS 5; twin 1 / "inline" / 4 (critic said 6 slots; I see 5, immaterial). BASE `(?C"nb")` binding (abi 89 compiler, `--features all`, unity-included with a `static inline` fn returning RX_PASS): 56,320,356 / 349 / 347 = same as the segment.
Means: ~1.9x vs twin on a path that never fires, but NOT a stage-2 regression (BASE binding equals it); goal 3b(b) as worded is unmet by the shared site primitive.
EMIT-3: card_inline.sh:48-50 `ROWS='site_hit|(\d+)@x|12x 345x 6x |` / `site_miss|(\d+)@x|12y 345y 6y |` / `tail|...`. site_miss shape ``(\d+)(?C`c: return RX_PASS;`)x`` on `12y 345y 6y `: segment 3,466,033 / 033 / 036 vs twin 3,466,026 / 011 / 008 instructions (= the driver's subject fill only); trap segment never traps; `#define X_REQ_BYTE "120"` (required byte 'x' absent, whole subject rejected). The VM does not run.
Means: the card's miss row cannot fail and does not measure non-reaching VM paths.

### CHK-1: HOLDS
run_code_tests.sh:175-177 `# Every CLI_MODE_TABLE spelling must have a row` / `modes="$(sed -n '/^#define CLI_MODE_TABLE(X)/,/^$/p' "$ROOT_DIR/cli/main.c" | grep -oE ...` ; line 184 floor `nmodes -ge 15`. `grep -n 'help' run_code_tests.sh` has no `pcrec --help` call. The arm reads the macro, not `--help`; design 5.9/9.1 promise `--help`'s table. (The earlier CON-4 shows --help omits the code options anyway.)
### CHK-4: HOLDS
run_code_tests.sh:349-357 trap_row: `rc=$?` then `if [ $rc -gt 128 ] && [ $rc -ne 137 ]; then ok ... traps` (any signal exit 129-255 except 137 passes; the arm does not check SIGILL/SIGTRAP specifically). Sabotage presence not re-counted by me beyond S1680-S1685 existing under tests/mech/sabotages (six files, as the critic lists).
### CHK-6: HOLDS
Top-level tests/code/*.rxt m/n lines: geoip 3 + ipv4 12 + macros 21 = 36; macros has 2 consume-block cells (skipped), checkable = 3 + 12 + 19 = 34. verify_code.py:372-373 comment says "floor 30 against the 36 checkable cells" and `if agree < 30`. So the "36" is wrong (34), slack 4. (I did not run verify_code.py.)
### CHK-7: HOLDS
tests/axes/run_axes.sh has a floor for tests/callouts only (`co_ran ... -lt 45`, "AXIS FAIL: ... tests/callouts/ case(s) reached this axis"); `grep -n 'tests/code' tests/axes/run_axes.sh` finds nothing about a code-section floor (the two grep hits are in unrelated comments at lines 1796/2062 of other text, no floor). Not run with geoip.c unreadable.
### CHK-5: HOLDS
run_rxtsource_tests.sh:1162-1165 "a head-bearing file's leg-B dump is exactly zero rows too (a body-less `analysis` bundle has no `pattern` block to disagree about), so dropping it from both sides ... changes nothing it could have compared." But lines 793-794 of the same file say these head-bearing files now "carry PATTERN BLOCKS" (ipv4.rxt 3 `pattern` lines, geoip 1, frag/entry 1 = 5 blocks). The comment is stale.

### SLOT-1: HOLDS
`grep -n 'not-config|per-option SCOPE|OPT-SCOPE|SCOPE row|SCOPE-ROW' docs/dev/plan.md docs/dev/decisions.md` in the review tree: zero matching lines in both. Only docs/design/inline_c.md:1257 and :1845 ("The per-option SCOPE row (D20, 5.1)") mention it.
Means: no filed plan row for the per-option SCOPE row the design says is filed at stage 2.

