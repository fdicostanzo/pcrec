/* d27 driver: the seven span helpers of match_api.md §11.10, called directly
 * from a translation unit that #includes a callout artifact (GEN_C).
 * §11.10¶1: every callout artifact carries them, "for a code segment and a
 * hand-written binding alike". Every expectation cites §11.10's table row
 * (¶T:<helper>) or ¶1. Prints PASS/FAIL lines; run.sh counts them. */
#include <stdio.h>
#include <string.h>
#include GEN_C

#ifndef PCREC_RX_SPAN_H
#error "PCREC_RX_SPAN_H not defined by a callout artifact (§1¶6b, §11.10¶1)"
#endif

static int fails;

static void check(const char *name, long long want, long long got)
{
    if (want == got) {
        printf("PASS helpers.%s\n", name);
    } else {
        printf("FAIL helpers.%s: expected %lld got %lld\n", name, want, got);
        fails++;
    }
}

static rx_span S(const char *z) { rx_span s = { (const unsigned char *)z, (ptrdiff_t)strlen(z) }; return s; }
static rx_span SN(const char *z, ptrdiff_t n) { rx_span s = { (const unsigned char *)z, n }; return s; }

#define UNSET ((rx_span){ (const unsigned char *)0, -1 })
#define UNSET_P(z) ((rx_span){ (const unsigned char *)(z), -1 })  /* pointer set, length negative */
#define UNSET_M5(z) ((rx_span){ (const unsigned char *)(z), -5 })
#define NULLEMPTY ((rx_span){ (const unsigned char *)0, 0 })

#define SENT 0xD27D27D27ULL

/* rx_u64 / rx_hex: returns, and *out untouched on 0 */
static void num(const char *name, int (*fn)(rx_span, uint64_t *), rx_span s, int want_r, uint64_t want_v)
{
    char nm[128];
    uint64_t v = SENT;
    int r = fn(s, &v);
    snprintf(nm, sizeof nm, "%s.ret", name);
    check(nm, want_r, r);
    snprintf(nm, sizeof nm, "%s.out", name);
    if (want_r)
        check(nm, (long long)want_v, (long long)v);
    else
        check(nm, (long long)SENT, (long long)v); /* "else 0 and *out untouched" */
}

static int u64fn(rx_span s, uint64_t *o) { return rx_u64(s, o); }
static int hexfn(rx_span s, uint64_t *o) { return rx_hex(s, o); }

/* rx_u8next: return, *i, *cp */
static void u8(const char *name, rx_span s, ptrdiff_t i0, int want_r, ptrdiff_t want_i, uint32_t want_cp)
{
    char nm[128];
    ptrdiff_t i = i0;
    uint32_t cp = 0xD27D27u;
    int r = rx_u8next(s, &i, &cp);
    snprintf(nm, sizeof nm, "u8next.%s.ret", name);
    check(nm, want_r, r);
    if (want_r == 0)
        return; /* the spec states nothing about *i / *cp on a 0 return (REPORT gap) */
    snprintf(nm, sizeof nm, "u8next.%s.i", name);
    check(nm, want_i, i);
    snprintf(nm, sizeof nm, "u8next.%s.cp", name);
    check(nm, want_cp, cp);
}

int main(void)
{
    /* ---- rx_eq (¶T:rx_eq): set, exactly z's bytes, same length ---- */
    check("eq.same", 1, rx_eq(S("abc"), "abc"));
    check("eq.prefix_span", 0, rx_eq(S("ab"), "abc"));
    check("eq.longer_span", 0, rx_eq(S("abcd"), "abc"));
    check("eq.case_differs", 0, rx_eq(S("ABC"), "abc"));
    check("eq.empty_empty", 1, rx_eq(S(""), ""));
    check("eq.empty_vs_nonempty", 0, rx_eq(S(""), "a"));
    check("eq.nonempty_vs_empty", 0, rx_eq(S("a"), ""));
    check("eq.unset_vs_empty", 0, rx_eq(UNSET, ""));          /* ¶1 unset matches nothing */
    check("eq.unset_ptr_set_vs_empty", 0, rx_eq(UNSET_P("abc"), "")); /* ¶1 "the pointer decides nothing" */
    check("eq.unset_neg5", 0, rx_eq(UNSET_M5("abc"), "abc"));  /* ¶1 "UNSET when its length is negative" */
    check("eq.nullp_len0_vs_empty", 1, rx_eq(NULLEMPTY, "")); /* ¶1 SET span p==NULL len 0 */
    check("eq.nullp_len0_vs_a", 0, rx_eq(NULLEMPTY, "a"));
    check("eq.span_with_nul", 0, rx_eq(SN("a\0", 2), "a"));   /* same length */
    check("eq.span_shorter_than_mem", 1, rx_eq(SN("abcdef", 3), "abc"));
    check("eq.high_bytes", 1, rx_eq(S("\xc3\xa9"), "\xc3\xa9"));

    /* ---- rx_eqi (¶T:rx_eqi): the 26 ASCII letters without case, every other byte exactly ---- */
    check("eqi.upper_lower", 1, rx_eqi(S("ABC"), "abc"));
    check("eqi.mixed", 1, rx_eqi(S("aBz"), "AbZ"));
    check("eqi.a_and_z_edges", 1, rx_eqi(S("Az"), "aZ"));
    check("eqi.at_vs_backtick", 0, rx_eqi(S("@"), "`"));      /* 0x40 vs 0x60: not letters */
    check("eqi.bracket_vs_brace", 0, rx_eqi(S("["), "{"));    /* 0x5B vs 0x7B */
    check("eqi.caret_vs_tilde", 0, rx_eqi(S("^"), "~"));
    check("eqi.latin1_E_acute", 0, rx_eqi(S("\xc9"), "\xe9")); /* non-ASCII exact */
    check("eqi.utf8_E_acute", 0, rx_eqi(S("\xc3\x89"), "\xc3\xa9"));
    check("eqi.digit_vs_symbol", 0, rx_eqi(S("1"), "\x11"));
    check("eqi.length_differs", 0, rx_eqi(S("ab"), "abc"));
    check("eqi.unset", 0, rx_eqi(UNSET, ""));
    check("eqi.nullp_len0", 1, rx_eqi(NULLEMPTY, ""));
    check("eqi.empty", 1, rx_eqi(S(""), ""));

    /* ---- rx_u64 (¶T:rx_u64) ---- */
    num("u64.zero", u64fn, S("0"), 1, 0);
    num("u64.simple", u64fn, S("42"), 1, 42);
    num("u64.leading_zeros", u64fn, S("007"), 1, 7);
    num("u64.many_leading_zeros", u64fn, S("000000000000000000000000000000018446744073709551615"), 1, UINT64_MAX);
    num("u64.max", u64fn, S("18446744073709551615"), 1, UINT64_MAX);
    num("u64.max_plus_1", u64fn, S("18446744073709551616"), 0, 0);
    num("u64.max_times_10", u64fn, S("184467440737095516150"), 0, 0);
    num("u64.wraps_to_small", u64fn, S("18446744073709551617"), 0, 0);
    num("u64.twenty_nines", u64fn, S("99999999999999999999"), 0, 0);
    num("u64.empty", u64fn, S(""), 0, 0);
    num("u64.nullp_len0", u64fn, NULLEMPTY, 0, 0);
    num("u64.unset", u64fn, UNSET, 0, 0);
    num("u64.unset_ptr_digits", u64fn, UNSET_P("12"), 0, 0);
    num("u64.trailing_letter", u64fn, S("12a"), 0, 0);
    num("u64.leading_minus", u64fn, S("-1"), 0, 0);
    num("u64.leading_plus", u64fn, S("+1"), 0, 0);
    num("u64.leading_space", u64fn, S(" 1"), 0, 0);
    num("u64.trailing_space", u64fn, S("1 "), 0, 0);
    num("u64.hex_letters", u64fn, S("ff"), 0, 0);
    num("u64.slash_colon", u64fn, S("/:"), 0, 0);          /* bytes either side of '0'..'9' */
    num("u64.arabic_indic_digit", u64fn, S("\xd9\xa1"), 0, 0);
    num("u64.fullwidth_digit", u64fn, S("\xef\xbc\x91"), 0, 0);
    num("u64.embedded_nul", u64fn, SN("1\0" "2", 3), 0, 0);
    num("u64.span_shorter_than_mem", u64fn, SN("123x", 3), 1, 123);

    /* ---- rx_hex (¶T:rx_hex): either case, no 0x ---- */
    num("hex.lower", hexfn, S("ff"), 1, 255);
    num("hex.upper", hexfn, S("FF"), 1, 255);
    num("hex.mixed", hexfn, S("aBcDeF"), 1, 0xabcdef);
    num("hex.digits", hexfn, S("0123456789"), 1, 0x123456789ULL);
    num("hex.zero", hexfn, S("0"), 1, 0);
    num("hex.max", hexfn, S("ffffffffffffffff"), 1, UINT64_MAX);
    num("hex.max_leading_zeros", hexfn, S("0000ffffffffffffffff"), 1, UINT64_MAX);
    num("hex.overflow", hexfn, S("10000000000000000"), 0, 0);
    num("hex.overflow_wrap", hexfn, S("10000000000000001"), 0, 0);
    num("hex.0x_prefix", hexfn, S("0x10"), 0, 0);
    num("hex.0X_prefix", hexfn, S("0X10"), 0, 0);
    num("hex.g", hexfn, S("g"), 0, 0);
    num("hex.G", hexfn, S("G"), 0, 0);
    num("hex.at_backtick", hexfn, S("@`"), 0, 0);          /* bytes before 'A' and 'a' */
    num("hex.empty", hexfn, S(""), 0, 0);
    num("hex.nullp_len0", hexfn, NULLEMPTY, 0, 0);
    num("hex.unset", hexfn, UNSET, 0, 0);
    num("hex.minus", hexfn, S("-1"), 0, 0);
    num("hex.h_suffix", hexfn, S("ffh"), 0, 0);

    /* ---- rx_in (¶T:rx_in): rx_u64 reads v with lo <= v <= hi ---- */
    check("in.inside", 1, rx_in(S("5"), 1, 10));
    check("in.lo_edge", 1, rx_in(S("1"), 1, 10));
    check("in.hi_edge", 1, rx_in(S("10"), 1, 10));
    check("in.below", 0, rx_in(S("0"), 1, 10));
    check("in.above", 0, rx_in(S("11"), 1, 10));
    check("in.leading_zeros", 1, rx_in(S("0010"), 1, 10));
    check("in.lo_gt_hi", 0, rx_in(S("5"), 10, 1));
    check("in.point", 1, rx_in(S("7"), 7, 7));
    check("in.full_range_max", 1, rx_in(S("18446744073709551615"), 0, UINT64_MAX));
    check("in.overflow_full_range", 0, rx_in(S("18446744073709551616"), 0, UINT64_MAX));
    check("in.not_digits", 0, rx_in(S("x"), 0, UINT64_MAX));
    check("in.hex_not_read", 0, rx_in(S("a"), 0, UINT64_MAX)); /* rx_u64, not rx_hex */
    check("in.empty", 0, rx_in(S(""), 0, UINT64_MAX));
    check("in.unset", 0, rx_in(UNSET, 0, UINT64_MAX));
    check("in.nullp_len0", 0, rx_in(NULLEMPTY, 0, UINT64_MAX));

    /* ---- rx_find (¶T:rx_find) ---- */
    check("find.middle", 2, rx_find(S("hello"), "ll"));
    check("find.start", 0, rx_find(S("hello"), "he"));
    check("find.end", 4, rx_find(S("hello"), "o"));
    check("find.whole", 0, rx_find(S("hello"), "hello"));
    check("find.first_occurrence", 0, rx_find(S("aaa"), "aa"));
    check("find.first_of_two", 1, rx_find(S("xabab"), "ab"));
    check("find.overlap_restart", 2, rx_find(S("aaab"), "ab"));
    check("find.absent", -1, rx_find(S("hello"), "z"));
    check("find.needle_longer", -1, rx_find(S("ab"), "abc"));
    check("find.empty_needle", 0, rx_find(S("hello"), ""));
    check("find.empty_both", 0, rx_find(S(""), ""));
    check("find.nullp_len0_empty", 0, rx_find(NULLEMPTY, ""));
    check("find.nullp_len0_a", -1, rx_find(NULLEMPTY, "a"));
    check("find.unset_empty_needle", -1, rx_find(UNSET, ""));  /* "-1 (none, or s unset)" */
    check("find.unset_a", -1, rx_find(UNSET, "a"));
    check("find.unset_ptr_set", -1, rx_find(UNSET_P("abc"), "a"));
    check("find.past_span_len", -1, rx_find(SN("abcdef", 3), "de"));
    check("find.straddles_span_end", -1, rx_find(SN("abcdef", 4), "de"));
    check("find.ends_at_span_end", 3, rx_find(SN("abcdef", 5), "de"));
    check("find.nul_in_span", 2, rx_find(SN("a\0b", 3), "b"));
    check("find.high_bytes", 1, rx_find(S("x\xc3\xa9"), "\xc3\xa9"));

    /* ---- rx_u8next (¶T:rx_u8next) ---- */
    u8("ascii", S("a"), 0, 1, 1, 'a');
    u8("ascii_nul", SN("\0", 1), 0, 1, 1, 0);
    u8("ascii_7f", S("\x7f"), 0, 1, 1, 0x7f);
    u8("two_byte_min", S("\xc2\x80"), 0, 2, 2, 0x80);
    u8("two_byte", S("\xc3\xa9"), 0, 2, 2, 0xe9);
    u8("two_byte_max", S("\xdf\xbf"), 0, 2, 2, 0x7ff);
    u8("three_byte_min", S("\xe0\xa0\x80"), 0, 3, 3, 0x800);
    u8("three_byte_euro", S("\xe2\x82\xac"), 0, 3, 3, 0x20ac);
    u8("below_surrogates", S("\xed\x9f\xbf"), 0, 3, 3, 0xd7ff);
    u8("above_surrogates", S("\xee\x80\x80"), 0, 3, 3, 0xe000);
    u8("three_byte_max", S("\xef\xbf\xbf"), 0, 3, 3, 0xffff);
    u8("four_byte_min", S("\xf0\x90\x80\x80"), 0, 4, 4, 0x10000);
    u8("four_byte_emoji", S("\xf0\x9f\x98\x80"), 0, 4, 4, 0x1f600);
    u8("four_byte_max", S("\xf4\x8f\xbf\xbf"), 0, 4, 4, 0x10ffff);
    u8("offset_mid", S("a\xc3\xa9z"), 1, 2, 3, 0xe9);
    u8("offset_last", S("a\xc3\xa9z"), 3, 1, 4, 'z');
    u8("end", S("ab"), 2, 0, 2, 0xD27D27u);                    /* 0 at the end; nothing changed */
    u8("past_end", S("ab"), 5, 0, 5, 0xD27D27u);
    u8("empty", S(""), 0, 0, 0, 0xD27D27u);
    u8("nullp_len0", NULLEMPTY, 0, 0, 0, 0xD27D27u);
    u8("unset", UNSET, 0, 0, 0, 0xD27D27u);
    u8("unset_ptr_set", UNSET_P("abc"), 0, 0, 0, 0xD27D27u);
    u8("overlong_c0", S("\xc0\x80"), 0, -1, 0, 0xD27D27u);
    u8("overlong_c1", S("\xc1\xbf"), 0, -1, 0, 0xD27D27u);
    u8("overlong_e0", S("\xe0\x80\x80"), 0, -1, 0, 0xD27D27u);
    u8("overlong_e0_9f", S("\xe0\x9f\xbf"), 0, -1, 0, 0xD27D27u);
    u8("overlong_f0", S("\xf0\x80\x80\x80"), 0, -1, 0, 0xD27D27u);
    u8("overlong_f0_8f", S("\xf0\x8f\xbf\xbf"), 0, -1, 0, 0xD27D27u);
    u8("surrogate_lo", S("\xed\xa0\x80"), 0, -1, 0, 0xD27D27u);
    u8("surrogate_hi", S("\xed\xbf\xbf"), 0, -1, 0, 0xD27D27u);
    u8("above_10ffff", S("\xf4\x90\x80\x80"), 0, -1, 0, 0xD27D27u);
    u8("lead_f5", S("\xf5\x80\x80\x80"), 0, -1, 0, 0xD27D27u);
    u8("lead_ff", S("\xff"), 0, -1, 0, 0xD27D27u);
    u8("lone_continuation", S("\x80"), 0, -1, 0, 0xD27D27u);
    u8("bad_continuation", S("\xc3\x28"), 0, -1, 0, 0xD27D27u);
    u8("bad_third", S("\xe2\x82\x28"), 0, -1, 0, 0xD27D27u);
    u8("bad_fourth", S("\xf0\x9f\x98\x28"), 0, -1, 0, 0xD27D27u);
    u8("missing_continuation", S("\xe2\x82"), 0, -1, 0, 0xD27D27u);
    u8("truncated_by_span_len", SN("\xc3\xa9", 1), 0, -1, 0, 0xD27D27u);
    u8("truncated4_by_span_len", SN("\xf0\x9f\x98\x80", 3), 0, -1, 0, 0xD27D27u);
    u8("bad_at_offset", S("a\x80"), 1, -1, 1, 0xD27D27u);

    return fails ? 1 : 0;
}
