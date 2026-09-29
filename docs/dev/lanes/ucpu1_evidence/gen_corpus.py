exec(open('/tmp/ucpu1s/gen_ucp.py').read())
D='/Users/fdicostanzo/pcrec/worktrees/ucpu1/tests/ucp/'
HDR_ORACLE = """#
# ORACLE: libpcre2, the options the block states (`encoding utf8` = PCRE2_UTF,
# `(*UCP)`/`flags u` = PCRE2_UCP, `flags i` = PCRE2_CASELESS). Every expectation
# was READ FROM THE ORACLE (10.48, the generator) and re-verified against the
# 10.46 reference; `verify_ucp.py` in this directory re-checks every cell on
# every `make test` against the resolved libpcre2 (it SKIPS loudly without one).
# `# pcre2-only` throughout: python `re` has no PCRE2_UCP and its subject
# decoder is byte-oriented (U14).
"""
U = ['٠١٢', '12', 'a', ' ', '　', ' ', '\u0085', 'x０y', 'Ａ', '\x7f', '\u0080', 'é', ' \t', '_', '۵', '\U0001d7ce']
out=["# [UCP] U1 -- the NARROW UCP sets under `-e utf8` (docs/design/ucp_design.md",
"# §1.1, D130 Q3): `\\d \\D \\s \\S` and `[:digit:] [:xdigit:] [:space:] [:blank:]",
"# [:cntrl:]`, both polarities, at an atom and inside a class, spelled `(*UCP)`,",
"# `(*UTF)(*UCP)` in either order, and `flags u` (`--ucp`). The WIDE sets are",
"# refused at U1 (refusals.rxt). Controls: the same patterns WITHOUT UCP read",
"# ASCII, which is PCRE2_UTF's own default (D130 Q1: UCP is opt-in)." + HDR_ORACLE]
for p in [r'(*UCP)\d', r'(*UCP)\d+', r'(*UCP)\D', r'(*UCP)\s', r'(*UCP)^\s+$', r'(*UCP)\S+', r'(*UCP)[[:digit:]]+', r'(*UCP)[[:^digit:]]', r'(*UCP)[[:xdigit:]]+', r'(*UCP)[[:space:]]', r'(*UCP)[[:blank:]]', r'(*UCP)[[:cntrl:]]', r'(*UCP)[\d_]+', r'(*UCP)[^\d]', r'(*UCP)[^\s\d]+', r'(*UTF)(*UCP)\d', r'(*UCP)(*UTF)\s', r'\d', r'\s']:
    block(out, p, 'utf8', '', '', U)
for p in [r'\d+', r'[[:xdigit:]]+', r'\S', r'[[:^space:]]']:
    block(out, p, 'utf8', 'u', '', U, 'the CLI spelling: `flags u` is `--ucp`')
open(D+'sets_utf8.rxt','w').write('\n'.join(out))

K = ['٠', '5', ' ', ' ', 'é', 'a', 'K', 'k', '０', '　']
out=["# [UCP] U1 -- PCRE2's ASCII-RESTRICTION letters made real (D130 Q5;",
"# ucp_design.md §1.4): `(?aD)` restricts \\d \\D, `(?aS)` \\s \\S, `(?aW)` \\w \\W",
"# \\b \\B, `(?aP)` every POSIX class, `(?aT)` [:digit:] [:xdigit:] (which aP",
"# restricts too). `(?a)` sets all five, `(?-a)` clears all, `(?-aX)` one; the",
"# letters are SCOPED (`(?aD:...)`) and SURVIVE `(?^)`. Without UCP they are",
"# no-ops, as they always were (the no-UCP controls at the end)." + HDR_ORACLE]
for p in [r'(*UCP)(?aD)\d', r'(*UCP)(?a)\d', r'(*UCP)(?a)(?-aD)\d', r'(*UCP)(?a)(?-aD)\s', r'(*UCP)(?-a)\d', r'(*UCP)(?aD-aD)\d', r'(*UCP)(?aDaS)\s', r'(*UCP)(?aD:\d)\d', r'(*UCP)(?aD)(?^)\d', r'(*UCP)(?aD)(?^i)\d', r'(*UCP)(?aS)\s', r'(*UCP)(?aS)[[:space:]]', r'(*UCP)(?aP)[[:space:]]', r'(*UCP)(?aP)\d', r'(*UCP)(?aT)[[:digit:]]', r'(*UCP)(?aT)\d', r'(*UCP)(?aP-aT)[[:digit:]]', r'(*UCP)(?aT)[[:xdigit:]]', r'(*UCP)(?aW)\w+', r'(*UCP)(?aW)\W', r'(*UCP)(?aP)[[:word:]]', r'(*UCP)(?aP)[[:alpha:]]+', r'(*UCP)(?aP)[[:^lower:]]', r'(*UCP)(?aD)[\d\x{660}]', r'(?aD)\d', r'(?a)\s']:
    block(out, p, 'utf8', '', '', K)
for p in [r'(*UCP)(?aW:a\b)', r'(*UCP)(?aW)a\b', r'(*UCP)(?aW)a\B']:
    block(out, p, 'utf8', '', 'classes,modifiers,assertions', ['aé', 'a b', 'ab'], '`(?aW)` REACHES `\\b`/`\\B`: inside its scope the boundary reads the ASCII word set, which U1 builds (UCP `\\b` itself is refused, refusals.rxt)')
open(D+'knobs.rxt','w').write('\n'.join(out))

C = ['A', 'a', 'K', 'k', 'K', 'ſ', 's', 'Ａ', 'ａ', 'É', 'é', '٠']
out=["# [UCP] U1 -- the CASELESS rules under UCP (ucp_design.md §1.3, T2):",
"# (1) an ASCII-RESTRICTED set folds by the ASCII fold even under UTF|UCP",
"# (`(?aW)(?i)\\w` does NOT reach U+212A/U+017F; `(?aP)(?i)[[:lower:]]` is",
"# exactly [A-Za-z]); (2) the narrow UCP sets are fold-closed; (3) folding is",
"# per contribution -- a literal beside a UCP set folds by the encoding's fold.",
"# `[:lower:]`/`[:upper:]`'s own FOLD-INERT rule is wide under utf8 and is",
"# pinned under `byte` (byte.rxt)." + HDR_ORACLE]
for p in [r'(*UCP)(?i)(?aW)\w', r'(*UCP)(?i)(?aP)[[:lower:]]', r'(*UCP)(?i)(?aP)[[:upper:]]', r'(*UCP)(?i)(?aP)[[:alpha:]]', r'(*UCP)(?i)[[:xdigit:]]', r'(*UCP)(?i)[[:^xdigit:]]', r'(*UCP)(?i)\d', r'(*UCP)(?i)[\dk]', r'(*UCP)(?i)[\d\x{e9}]', r'(*UCP)(?i)(?aP)[[:lower:]k]', r'(*UCP)(?i)k', r'(?i)(?aW)\w']:
    block(out, p, 'utf8', '', '', C)
open(D+'caseless.rxt','w').write('\n'.join(out))

B = [b'\xb2', b'\xe9', b'\xd7', b'\xaa', b'\xb5', b'\xba', b'\xa7', b'\xa2', b'\xab', b'5', b'\x85', b'\xa0', b'\xad', b'\xc9', b'\xdf', b'\xff', b'A', b'a', b'K', b'k', b'\xe6', b'\x7f', b'_']
F='classes,modifiers,ucp'
out=["# [UCP] U1 -- THE BYTE TIER: PCRE2_UCP WITHOUT PCRE2_UTF (ucp_design.md §1.5,",
"# D130 Q4). The bytes are Latin-1 code points, every UCP set is its Unicode",
"# set clamped to [0, 0xFF] (so every one is narrow and all compile), and",
"# `(?i)` folds the 26 ASCII + 30 Latin-1 pairs (T2's `latin1` row) -- `\\xe9`",
"# reaches `\\xc9` under UCP and not without it. `[:lower:]`/`[:upper:]` are",
"# FOLD-INERT under UCP here too (T2's `inert` row). Module `ucp` is named in",
"# `features`: `-e byte` does not imply it (O-71 is utf8's)." + HDR_ORACLE]
for p in [r'(*UCP)\w', r'(*UCP)\W', r'(*UCP)\d', r'(*UCP)\s', r'(*UCP)[[:alpha:]]', r'(*UCP)[[:alnum:]]', r'(*UCP)[[:punct:]]', r'(*UCP)[[:graph:]]', r'(*UCP)[[:print:]]', r'(*UCP)[[:space:]]', r'(*UCP)[[:blank:]]', r'(*UCP)[[:cntrl:]]', r'(*UCP)[[:xdigit:]]', r'(*UCP)[[:lower:]]', r'(*UCP)[[:upper:]]', r'(*UCP)[[:word:]]', r'(*UCP)(?i)[[:lower:]]', r'(*UCP)(?i)[[:upper:]]', r'(*UCP)(?i)[^[:lower:]]', r'(*UCP)(?i)[[:lower:]x]', r'(*UCP)(?i)\xe9', r'(*UCP)(?i)[\xe0-\xe9]', r'(*UCP)(?i)\xb5', r'(*UCP)(?i)\xff', r'(*UCP)(?i)\xdf', r'(*UCP)(?i)k', r'(*UCP)(?i)(?aW)\w', r'(*UCP)(?i)(?aP)[[:lower:]]', r'(*UCP)(?aW)\w', r'(?i)\xe9', r'\w']:
    block(out, p, 'byte', '', F, B)
for p in [r'\w', r'(?i)\xe9']:
    block(out, p, 'byte', 'u', F, B, '`flags u` (`--ucp`) under `byte`')
open(D+'byte.rxt','w').write('\n'.join(out))

out=["# [UCP] U1 -- WHAT IS REFUSED, BY NAME, and never answered with the ASCII",
"# meaning (which would be a miscompile). libpcre2 ACCEPTS every construct",
"# here but the last three; pcrec refuses them as CAPABILITY limits:",
"#   - the WIDE UCP sets under `-e utf8` (D130 Q3; limits.md §3.8): \\w \\W and",
"#     [:alpha:] [:alnum:] [:word:] [:lower:] [:upper:] [:graph:] [:print:]",
"#     [:punct:], either polarity, at an atom or inside a class, spelled",
"#     `(*UCP)` or `flags u`, and `(?aW)` does NOT help [:word:] (aP does);",
"#   - UCP `\\b`/`\\B` under BOTH encodings (U2 for byte, U3/U4 for utf8);",
"#   - `--ucp` without module `ucp` enabled (the byte default).",
"# The last three are PCRE2 errors too: (*UTF) is refused under `byte`",
"# (D130 Q2), and a start-of-pattern option is start-only.",
"# `verify_ucp.py` counts these blocks and checks nothing about them: a",
"# `perr` is pcrec's refusal, not a libpcre2 answer.",""]
for p in [r'(*UCP)\w', r'(*UCP)\W+', r'(*UCP)[\w-]', r'(*UCP)[^\W]', r'(*UCP)[[:alpha:]]', r'(*UCP)[[:^alnum:]]', r'(*UCP)[x[:word:]]', r'(*UCP)[[:lower:]]', r'(*UCP)(?i)[[:upper:]]', r'(*UCP)[[:graph:]]', r'(*UCP)[[:print:]]', r'(*UCP)[[:punct:]]', r'(*UCP)(?aW)[[:word:]]', r'(*UCP)(?aD)\w']:
    perr(out, p, 'utf8', '', '', 'a WIDE UCP set under utf8')
perr(out, r'\w+', 'utf8', 'u', '', '`flags u` reaches the same refusal')
perr(out, r'(*UCP)\b', 'utf8', '', 'classes,modifiers,assertions', 'UCP \\b under utf8')
perr(out, r'(*UCP)a\B', 'utf8', '', 'classes,modifiers,assertions', 'UCP \\B under utf8')
perr(out, r'(*UCP)\b', 'byte', '', 'classes,modifiers,assertions,ucp', 'UCP \\b under byte (U2)')
perr(out, r'\bx', 'byte', 'u', 'classes,modifiers,assertions,ucp', '`flags u` + \\b under byte')
perr(out, r'\d', 'byte', 'u', 'classes,modifiers', '--ucp with module ucp NOT enabled (byte does not imply it)')
perr(out, r'(*UTF)a', 'byte', '', 'classes,modifiers,ucp', '(*UTF) under byte, gate open')
perr(out, r'a(*UCP)', 'utf8', '', '', 'a start-of-pattern option not at the start')
perr(out, r'(*UCP)*', 'utf8', '', '', 'an option is not a repeatable item')
open(D+'refusals.rxt','w').write('\n'.join(out))
print('ok')
