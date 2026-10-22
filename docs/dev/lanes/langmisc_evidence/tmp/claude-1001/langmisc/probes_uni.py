# Families H-L, Z: encodings, case folding, UCP, properties, ill-formed UTF-8, code point boundaries
P = []
def p(pat, subj=(), **k):
    k.update(pat=pat, subj=list(subj)); k.setdefault("feats", "all"); k.setdefault("id", "U%03d" % (len(P)+1)); P.append(k)
U = dict(enc="utf8")
ILL = [b"\xff", b"\xc0\x80", b"\xc1\xbf", b"\xed\xa0\x80", b"\xed\xbf\xbf", b"\xf4\x90\x80\x80", b"\xf5\x80\x80\x80", b"\xe2\x82", b"\x80",
       b"a\xffb", b"a\xc3", b"\xe0\x80\xaf", b"\xf0\x80\x80\xaf", b"\xc3\xa9", b"\xef\xbf\xbf", b"\xf4\x8f\xbf\xbf", b"\xee\x80\x80", b"\xed\x9f\xbf"]
# byte vs utf8 for basics, ill-formed subjects
for pat in [".", "(?s).", "[^a]", "\\W", "\\D", "\\S", "\\H", "\\V", "\\N", ".+", "a.b", "b", "[\\x{80}-\\x{10ffff}]", "[^\\x{0}-\\x{7f}]", "\\p{Any}",
            "\\P{L}", "\\X", ".\\z", "(?s).*", "[\\x{d7ff}-\\x{e000}]", "\\p{Cn}", "\\p{Co}", "\\p{Cs}", "\\p{C}", "[^\\p{L}]", "\\x{ffff}", "\\x{10ffff}",
            "\\x{fffd}", "(?i)[^k]", "\\b.", "\\B."]:
    p(pat, ILL, **U)
    p(pat, ILL)
# pattern ill-formed UTF-8
for pat in [b"\xff", b"a\xc3", b"\xc0\x80", b"\xed\xa0\x80", b"\xf4\x90\x80\x80", b"\xf8\x88\x80\x80\x80", b"[\xff]", b"\\\xff", b"\xe2\x82",
            b"(?x)a\xe2\x80\xa8b", b"(?x)a\xc2\x85b", b"(?x)a\xe2\x80\x8eb", b"(?x)a\xe2\x80\x8bb", b"(?x)a\xc2\xa0b", b"(?x)a\xe3\x80\x80b",
            b"(?x)[\xe2\x80\xa8]", b"(?xx)[\xe2\x80\xa8a]", b"(?x)a#\xe2\x80\xa8b", b"(?x)a#\xc2\x85b"]:
    p(pat, [b"ab", b"a\xe2\x80\xa8b", b"a\xc2\x85b", b"\xe2\x80\xa8", b"a", b"b", b"\xc2\xa0", b"a\xc2\xa0b", b"a\xe2\x80\x8bb"], **U)
for pat in [b"(?x)a\x85b", b"(?x)a\xa0b", b"(?x)a\x0bb", b"(?x)a\x0cb", b"(?x)a#c\rb", b"(?x)a#c\x85b", b"(?x)a#c\nb"]:
    p(pat, [b"ab", b"a\x85b", b"a\xa0b"])
# escapes above 0xFF, boundaries
for pat in ["\\x{110000}", "\\x{d800}", "\\x{dfff}", "\\x{d7ff}", "\\x{e000}", "\\x{7f}\\x{80}", "\\x{7ff}\\x{800}", "\\x{ffff}\\x{10000}",
            "[\\x{7f}-\\x{80}]", "[\\x{7ff}-\\x{800}]", "[\\x{ffff}-\\x{10000}]", "[\\x{10fffe}-\\x{10ffff}]", "[^\\x{0}-\\x{10fffe}]",
            "\\x{00000010ffff}", "\\x{1000000}", "[\\x{d7ff}-\\x{e000}]+", "\\777", "\\o{777}", "[\\777]", "\\x{100}+", "é+", "[é]", "[^é]", "[à-ÿ]+",
            "\\é", "[\\é]"]:
    p(pat, ["\x7f\x80", "߿ࠀ", "￿\U00010000", "\U0010fffe", "\U0010ffff", "퟿", "", "ǿ", "ĀĀ", "éé", "è", "a",
            "\U0010ffff퟿"], **U)
# case folding, byte
for pat in ["(?i)k", "(?i)\\xe9", "(?i)[\\xc0-\\xde]", "(?i)[^a]", "(?i)[a-z]+", "(?i)\\x{ff}", "(?i)[[:upper:]]", "(?i)[[:lower:]]", "(?i)[[:^lower:]]",
            "(?i)[^[:lower:]]", "(?i)\\w", "(?i)[^\\W]", "(?i)[k-m]", "(?i)[^k-m]", "(?i)\\x{b5}", "(?i)\\xdf", "(?i)[Z-a]", "(?i)[@-\\x60]",
            "(?i)(a)\\1", "(?i)(\\xe9)\\1", "(?i)\\x5b", "(?i)[^\\x00-\\x60]"]:
    for ucp in (False, True):
        p(pat, ["k", "K", "\xe9", "\xc9", "a", "A", "\xff", "\xb5", "\xdf", "Z", "_", "[", "{", "\\", "^", "`", "aA", "\xe9\xc9", "L", "l", "\xc0", "\xe0"],
          ucp=ucp)
# case folding, utf8
FS = ["k", "K", "K", "s", "S", "ſ", "å", "Å", "Å", "ß", "ẞ", "σ", "ς", "Σ", "Ǆ", "ǅ", "ǆ",
      "ͅ", "ι", "Ι", "ι", "i", "I", "İ", "ı", "µ", "μ", "Μ", "ÿ", "Ÿ", "ẛ", "ṡ", "Ṡ",
      "ss", "θ", "ϑ", "ϴ", "Θ", "Ω", "ω", "ა", "Ა", "Ꭰ", "ꭰ", "\U00010400", "\U00010428", "\U0001e900", "\U0001e922"]
for pat in ["(?i)k", "(?i)s", "(?i)\\x{e5}", "(?i)\\x{df}", "(?i)\\x{3c3}", "(?i)\\x{1c5}", "(?i)\\x{345}", "(?i)i", "(?i)\\x{130}", "(?i)\\x{131}",
            "(?i)\\x{b5}", "(?i)\\x{ff}", "(?i)\\x{1e9b}", "(?i)\\x{3b8}", "(?i)\\x{2126}", "(?i)\\x{10d0}", "(?i)\\x{13a0}", "(?i)\\x{10400}",
            "(?i)\\x{1e900}", "(?i)[a-z]", "(?i)[^k]", "(?i)[^a-z]", "(?i)[k-k]", "(?i)[\\x{3c2}]", "(?i)[\\x{1c4}-\\x{1c6}]", "(?i)[\\x{3a3}-\\x{3a3}]",
            "(?i)[[:lower:]]", "(?i)[[:lower:]k]", "(?i)\\p{Lu}", "(?i)\\p{Ll}", "(?i)\\p{Lt}", "(?i)\\P{Lu}", "(?i)\\p{L&}", "(?i)[^\\p{Lu}]",
            "(?i)\\p{Greek}", "(?i)(k)\\1", "(?i)(\\x{3c3})\\1", "(?i)(\\x{df})\\1", "(?i)(s)\\1", "(?i)(\\x{345})\\1", "(?i)(ss)\\1",
            "(?i)(\\x{1c4})\\1", "(?i)(?<=k)a", "(?i)\\x{130}+", "(?i)[\\x{130}]", "(?i)[\\x{100}-\\x{17f}]", "(?i)[^\\x{100}-\\x{17f}]", "(?i)\\w", "(?i)\\W"]:
    p(pat, FS + ["Ka", "kK", "σς", "ßẞ", "sſ", "ͅι", "ssß", "Ǆǆ"], **U)
# UCP, byte
UB = ["\xaa", "\xb5", "\xba", "\xe9", "\xb2", "\xb3", "\xb9", "\xbc", "\x85", "\xa0", "\xd7", "\xf7", "\xa7", "\xab", "\xbf", "\x80", "\x9f", "\xad", "\xff",
      "\xc0", "a", "5", " ", "\t", "_", "\x7f", "\xa1", "\xb4", "\xb8", "\xa8", "\xaf", "\xa6", "\xa9"]
for pat in ["\\w", "\\W", "\\d", "\\D", "\\s", "\\S", "[[:alpha:]]", "[[:alnum:]]", "[[:digit:]]", "[[:xdigit:]]", "[[:punct:]]", "[[:graph:]]",
            "[[:print:]]", "[[:space:]]", "[[:blank:]]", "[[:cntrl:]]", "[[:upper:]]", "[[:lower:]]", "[[:word:]]", "[[:ascii:]]", "[[:^alpha:]]",
            "\\b.", "\\B.", "a\\b", "(?aW)\\w", "(?aD)\\d", "(?aS)\\s", "(?aP)[[:alpha:]]", "(?aT)[[:digit:]]", "(?aP)[[:digit:]]", "(?a)\\w",
            "(?a)(?^)\\w", "(?aW)(?-aW)\\w", "(?aW:\\w)\\w", "\\h", "\\v", "(?i)[[:upper:]]", "(?i)[[:lower:]]", "(?i)\\xe9", "(?i)\\xff",
            "(?i)(\\xe9)\\1", "(?aW)(?i)\\xe9", "[\\w]", "[^\\w]", "[\\W\\d]", "[[:^digit:]]"]:
    p(pat, UB + ["a\xe9", "\xe9a", "\xe9\xc9", "\xc9\xe9"], ucp=True)
# UCP + properties, utf8
UU = ["٣", "²", " ", " ", " ", "᠎", "​", "　", "\u0085", "é", "一", "́", "Ⅰ", "ª",
      "ʰ", "Ɐ", "ǅ", "\U0001d7ce", "‍", "‿", "͂", "Ͱ", "ἀ", "a", "_", "5", " ", "͸", "\U000e0001",
      "", "\U000f0000", "­", "؀", "\U0001f600", "$", "§", "™", "ก"]
for pat in ["\\d", "\\D", "\\s", "\\S", "\\w", "\\W", "[[:alpha:]]", "[[:digit:]]", "[[:space:]]", "[[:punct:]]", "[[:graph:]]", "[[:print:]]",
            "[[:upper:]]", "[[:lower:]]", "[[:xdigit:]]", "[[:cntrl:]]", "[[:blank:]]", "[[:alnum:]]", "[[:word:]]", "\\b", "\\B", "(?aW)\\w",
            "(?aW)\\b", "(?aP)[[:alpha:]]", "(?aD)\\d", "(?aS)\\s", "(?aT)[[:xdigit:]]", "\\h", "\\v", "\\H", "\\V", "[\\d]", "[\\s\\d]"]:
    p(pat, UU, ucp=True, **U)
for pat in ["\\p{L}", "\\p{Lu}", "\\p{L&}", "\\p{Lc}", "\\p{LC}", "\\p{Any}", "\\p{Xan}", "\\p{Xps}", "\\p{Xsp}", "\\p{Xuc}", "\\p{Xwd}", "\\p{Greek}",
            "\\p{sc=Greek}", "\\p{scx=Greek}", "\\p{Script=Greek}", "\\p{Script_Extensions=Greek}", "\\p{sc:Greek}", "\\p{^L}", "\\P{^L}", "\\pL", "\\PL",
            "\\p{ L u }", "\\p{l_u}", "\\p{LU}", "\\p{grek}", "\\p{Grek}", "\\p{SC=GREEK}", "\\p{Han}", "\\p{Latin}", "\\p{Common}", "\\p{Inherited}",
            "\\p{Zinh}", "\\p{Qaai}", "\\p{Katakana_Or_Hiragana}", "\\p{Hrkt}", "\\p{Alphabetic}", "\\p{bc=L}", "\\p{InGreek}", "\\p{Foo}", "\\p",
            "\\p{", "\\p{L", "\\p{}", "\\p{Nd}", "\\p{N}", "\\p{Cf}", "\\p{Zl}", "\\p{Zs}", "\\p{Sm}", "\\p{Pc}", "\\p{Me}", "\\p{Lm}", "\\p{Cc}",
            "[\\p{L}\\d]", "[^\\p{L}]", "[\\P{L}]", "[\\p{Greek}a]", "\\p{L}+", "\\P{Any}", "\\p{^Any}", "\\p{Cn}", "\\p{Unknown}", "\\p{Zzzz}",
            "\\p{Arabic}", "\\p{sc=Arabic}", "\\p{Thaana}", "\\p{Yi}", "\\p{Kawi}", "\\p{Nag_Mundari}", "\\p{Todhri}", "\\p{Garay}", "\\p{L&amp}",
            "\\p{Xan", "\\p{gc=L}", "\\p{General_Category=L}", "\\p{isGreek}", "\\p{Is_Greek}", "\\p{Greek_}", "\\p{ Greek }", "\\p{G r e e k}",
            "\\p{-Greek}", "\\p{^ Greek}", "\\p{ ^Greek}", "\\p{Bidi_Class=L}", "\\p{Bidi_Control}", "\\p{bidi_m}", "\\p{Lowercase}", "\\p{Emoji}"]:
    p(pat, UU + ["٠", "،", "ـ"], **U)
for pat in ["\\p{L}", "\\p{Greek}", "\\p{Latin}", "\\p{Common}", "\\p{Han}", "\\p{Lu}", "\\p{Xwd}", "\\P{L}", "\\p{Cn}", "\\p{Any}", "[\\p{Han}]",
            "\\p{Han}a|b", "\\P{Any}", "[^\\P{Any}]", "\\p{Inherited}", "\\p{Zs}"]:
    p(pat, UB + ["b"])
# \h \v under utf8 / byte
for pat in ["\\h", "\\v", "\\H", "\\V", "[\\h]", "[\\v]", "[^\\h]", "\\R"]:
    p(pat, ["\t", " ", " ", " ", "᠎", " ", " ", "​", " ", " ", "　", "\n", "\x0b", "\x0c", "\r", "\x85",
            " ", " ", "a"], **U)
PROBES = P
