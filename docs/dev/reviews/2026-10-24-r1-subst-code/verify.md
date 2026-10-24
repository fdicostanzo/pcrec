# VERIFY round subst (sonnet), 2026-10-24

### TPL-1 HOLDS
- repro: python3 -I tpl/src/h.py tpl/c6.json verify/tpl1 (copy of critic harness, oracle pcre2_substitute 10.46 EXTENDED).
- observed: s0.c record `.encoding = -1` for `<\xe9>` (-e utf8, subst-extended); check accepts a byte rx. Byte rx "ab" `(b)`: pcrec `a<\xc3\xa9>` vs PCRE2 `a<\xe9>` (e1,e2,e5); `<\x{100}>` pcrec `\xc4\x80` vs PCRE2 -57; `<\N{U+41}>` pcrec `A` vs PCRE2 -57 (e3,e4); reverse (template byte, rx utf8): pcrec lone `\xe9`, PCRE2 `\xc3\xa9` (e6). Octal `\351` is refused by pcrec (fine). Spec s2p5 says -1 only for all-ASCII; text-scan misses escapes. Magnitude as claimed.

### EMIT-5 HOLDS
- repro: emit/case/p2.c (libpcre2 pcre2_substitute EXTENDED, UTF) + h.py with `(.)` `\U$1`/`\L$1` -e utf8 subst-extended (verify/e5.json). 12 cases, pcrec == libpcre2 in all 12.
- observed \U: U+03B9 -> U+0345 ; U+03BC -> U+00B5 ; U+01C5 -> U+01C6 ; U+03D0 -> U+03B2 ; also U+00B5 -> U+03BC (pcrec and libpcre2 both). \L of U+01C5 -> U+01C6 (fine).
- UnicodeData (ucd-16.0.0) Simple_Uppercase: 03B9->0399, 03BC->039C, 03D0->0392, 01C5->01C4, 00B5->039C. So all five \U results are non-Unicode (lowercase letters / combining mark); added U+00B5 -> U+03BC is a fifth row the critic did not list. The finding's claim holds; ruling on D26 addendum is the manager's.
### IFACE-4 HOLDS (behaviour), but it is a DOCUMENTED choice
- repro: built iface/d1.c, d4.c in verify/ (gcc -I iface). Element with cap 5 < 2P: -11 NOSPACE need=2*NUM_PIECES. replace_all with o.cap = P-1: -15 MISMATCH. 301-cap rx (big): replace_all -15 (expected 2 by critic). Both reproduced.
- correction: subst_api.md line ~1037 (§10¶7) already says "(... more than RX_SUBST_BATCH_PAIRS pairs per match, or an o->cap below P)" return MISMATCH, so the finding is a design argument against a stated rule, not an undocumented defect. (Some other d1.c lines print **FAIL** from the critic's stale expected values: flatten, RA exact; not part of this finding.)
### EMIT-1 HOLDS
- repro: rebuilt emit/bench (verify/eb, gcc -O2, SUBJECT-emitted em/eu/t1/tu/tw), `taskset -c 7 perf stat -e instructions:u eb/bench MODE 20`, 3 repeats each (spread < 0.001%), per-rep = total/20, 48771 matches/rep, identical output hashes for modes 6/7/9/11/12.
- observed: utf8 \U pcrec (mode 9) 110.9M instr; pcre2 UTF+JIT (mode 12) 95.9M => pcrec 15.7% MORE instructions; same template under byte (mode 6) 70.9M; hand loop (7) 40.5M. Critic's 109.99/94.94/69.92 reproduced within 1%. I did not time the three sub-causes (a)(b)(c) separately; instruction counts only, no wall-clock.
### EMIT-2 HOLDS
- observed (per rep): bare find-all (mode 1) 34.9M; replace_all (mode 2) 52.2M; hand loop (3) 40.3M; pcre2 JIT (5) 67.1M. Overhead over find-all: replace_all 354 instr/match, hand 110 => 3.2x (critic 3.4x); replace_all is still 22% below pcre2 JIT. Headroom claim correct, not a regression.
### EMIT-4 HOLDS
- repro: verify/eb/mini.c (rx + non-case template + PCREC_SUPPORT_IMPLEMENTATION), gcc -O2: `size` text 41,532 B; rx_subst_lower_ 0x2c40 + rx_subst_upper_ 0x2dd0 = 23,056 B (nm -S); with -DPCREC_SUPPORT_STATIC the same program is 14,537 B text. Exactly the critic's figures. (Not tested: --gc-sections.)
### TPL-4 HOLDS
- repro: `/usr/bin/time -v build/pcrec -p t -o t1m.c --subst-file t1m.tmpl` (1,048,576 x 'a') under scripts/watchdog -s 60 -m 2g: max RSS 164,532 KB (~157 B/byte), 0.07 s, 3.1 MB C; 256 KB template: 43,308 KB (~165 B/byte). limits.def has only PCREC_MAX_TEMPLATE_GROUP and _NESTING (lines 178-179), no length/piece row. Outputs correct; low priority as critic said. (4 MB not re-run.)
### IFACE-5 HOLDS
- repro: `build/pcrec -o dp.c --subst '<$1>'` rc 0, dp.h:473 `extern const struct rx_subst_info rx_subst_info;`; `-p pcrec --subst a` rc 0, `extern const struct rx_subst_info pcrec_subst_info;`. `-p rx_subst` is refused (cli.md row 4 gives only the two bare names `rx_subst`.. as refused, `rx`/`pcrec` not). Design/doc issue only; compiles because tags and objects are separate namespaces.
### IFACE-7 HOLDS
- repro: iface/d4.c rebuilt: "aXbYa", `(a)|(b)`, one ab_next consumed, then ctx_init + replace_all -> returns 2, output `aX[|b]Y[a|]` (consumed match copied unreplaced, not counted). Doc gap in §10¶6a/¶7 as claimed.
### CHK-7 HOLDS
- repro: `build/pcrec OPT -p s -o o.c --subst x`: --engine=auto rc 0, --tune=0 rc 0, --size-cap=degrade rc 0 (accepted); --engine=vm, --tune=1, -i rc 1 (refused). Default-valued options are accepted. d27/cli/cli.sh names 6 options.
### CHK-3 PARTLY
- `$65535` rc 0, `$65536` rc 1 (offset 0). Critic's grep of tests/subst missed tests/subst/d27/cli/cli.sh:69, whose refusal loop includes '$65536' (rc!=0 + template offset), so a mutant accepting 65536 IS caught there (d27 section, Makefile target test-subst-d27). Also d27 corpus d_tpl.tsv rows tpl-072/073/111/112 ($65536 / $65535 vs pcre2). Not pinned in tests/subst's own cells; the ACCEPT side ($65535 compiles) is only compared through d27's diff rows, whose BIND mapping (critic) I did not re-run.
### CHK-4 HOLDS
- tests/subst/d27/lib/ref_pcre2.py:15 `L = C.CDLL('libpcre2-8.so.0')` (line 16 per critic is off by one).
### CHK-6 HOLDS
- run_subst_tests.py:329-332: room arm checks only `len(rm)==3 and rm[0]==ns and rm[2]=='1'`; `rm[1]` (need) never read. (Mutant not run.)
### CHK-8 HOLDS
- token counts: tests/subst/cells.tsv S1347 x2, S1348 x2, S1352 x1 (but S1352 row is SAB_EXPECT=UNDETECTED, retired witness, token still in REACH_NEED line 80); subst-extended S1534 x2, S1535 x4. Matches critic.
### CHK-1 HOLDS
- repro: emit `-p r0 --pattern '(a)(b)'`, `-p t0 --subst '[$1|$n|$2]'`, `-p t1 --subst '[${!v}-$1-$0]'`; apply each row's plant by sed to the emitted .c; `gcc -O1 -std=gnu11 -Wall -Wextra -Werror -include r0.h -c`: t0 planted -> `unused parameter 'flags' [-Werror=unused-parameter]`; t1 planted (`nvars < 1 - 1`) -> `comparison of unsigned expression in '< 0' is always false [-Werror=type-limits]`. Unplanted both compile rc 0. run_subst_tests.sh:34 and .py:136 default GENCFLAGS include -Werror, so the "driver build" fails before any cell runs.
### HOUSE-1 HOLDS (count of copies not checked)
- subst_template.c:20-27 header admits "UNIFIES WITH IT AT MERGE"; st_in_prop (82-93) is the same binary search as mod_named_groups.c ng_in_prop; st_name_char (:100-110) mirrors ng_name_char (:118-131, which uses isalpha/pcrec_pat_char). pcrec_group_name_scan already exists in the tree (mod_named_groups.c:145, 5 other callers). "Fifth" copy not counted by me.
### HOUSE-3 HOLDS
- compile.c:208-221 pcrec_prefix_acceptable and compile.c:2539-2543 spell the same two checks and both message strings ("invalid symbol prefix (must be a C identifier, <= %d chars)", "invalid symbol prefix: it %s") twice, despite the comment "share one prefix rule".
### HOUSE-4 HOLDS (two walks); "COND layout five times" not counted
- emit_subst.c emit_subst_item (717-756) and emit_region_items (910-977) switch over the same kinds with the same span expressions (s + c[0][0], ctx->vars[%d]..., s/ctx->len, c[0][0], c[0][1]); VAR text duplicated via snprintf.
### HOUSE-7 HOLDS
- `build/pcrec -p t --features subst-extended --subst '\U$1x${2:-y}' -o - | grep -nP '[^\x00-\x7F]'` -> 3 lines (526 "§2¶13", 537 "§2¶14", 564 "§4¶8"). `--emit-support -o -` -> 0.
### HOUSE-8 HOLDS (reading)
- emit_subst.c:828-839 case_state_tables: while condition is a 3-clause || chain, comment "the last row of each event is unconditional", no `r < n` bound; literals 9 and 3 (st/3, st%3, [9]) present at 828, 830, 856, 864.
### HOUSE-9(1) HOLDS
- subst_template.c:461 and :473-474 spell the same stop predicate `stop != ST_TOP && (s[i]=='}' || (stop==ST_SET_TEXT && s[i]==':'))`; `(SubstItem){` initializer count 9.
### HOUSE-10 HOLDS
- emit_subst.c:1145 `if (unit) free(support_unit(&id));` builds the whole unit to read the id.
### IFACE-9 HOLDS
- subst_api_r4_draft.md still opens with "it replaces docs/spec/subst_api.md at build time, when this comment goes"; lines 1008, 1010, 1024 name RX_FOREACH_PAIRS; replace_design.md:1028, 1353, 1787 too. RX_FOREACH appears nowhere in src/lib/spec/emitted headers (0 in dp.h); D175 (decisions.md:9935) dropped it; subst_api.md says RX_SUBST_BATCH_PAIRS. I did not re-diff the 275 lines.

## NOT REACHED
- HOUSE-4 "COND layout five times" count; HOUSE-1 "fifth copy" count; CHK-3 d27 BIND-mapping claim; CHK-6 mutant run.

## DONE
