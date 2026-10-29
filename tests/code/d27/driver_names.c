/* d27 driver: the names a code artifact leaves behind, the binding form and
 * the macro hygiene of match_api.md §11.2¶1a and §11.9¶4-¶5. GEN_C is a
 * self-contained artifact built with -p foo of names.pat (run.sh):
 *   segment 1 returns RX_PASS; segment 2 #defines D27_FROM_CODE and returns
 *   RX_FAIL; the pattern declares the group name nm. */
#include <stdio.h>
#include <string.h>
#include GEN_C

static int fails;
static void res(const char *what, int ok)
{
    printf("%s names.%s\n", ok ? "PASS" : "FAIL", what);
    if (!ok)
        fails++;
}
/* §11.9¶4-¶5: the macro set is #undef'ed after the last segment */
#ifdef RX_SUBJ
#  define D27_RX_SUBJ 1
#else
#  define D27_RX_SUBJ 0
#endif
#if defined(RX_LEN) || defined(RX_POS) || defined(RX_START) || defined(RX_USER)
#  define D27_RX_SCALARS 1
#else
#  define D27_RX_SCALARS 0
#endif
#if defined(RX_CAP_SET) || defined(RX_CAP_S) || defined(RX_CAP_E) || defined(RX_CAP_LEN) || defined(RX_CAP_P) || defined(RX_CAP)
#  define D27_RX_CAPS 1
#else
#  define D27_RX_CAPS 0
#endif
#ifdef RX_G_nm
#  define D27_RX_G 1
#else
#  define D27_RX_G 0
#endif
/* §11.9¶4: the internal macros (<PREFIX>_NSLOTS, _SLOT_*, _R_*) are #undef'ed */
#if defined(FOO_NSLOTS) || defined(FOO_R_STEPS) || defined(FOO_SLOT_WHOLE_START)
#  define D27_INTERNAL 1
#else
#  define D27_INTERNAL 0
#endif
/* §11.9¶4: "what stays defined is the public contract: the stamps of §6.3,
 * the shared block's and §1¶6a's names" */
#if defined(RX_PASS) && defined(RX_FAIL) && defined(PCREC_RX_CALLOUT_H) && defined(PCREC_RX_SPAN_H) && defined(PCREC_RX_ABI_H) && defined(PCREC_UNSET) && defined(PCREC_ERR_STEPS)
#  define D27_PUBLIC 1
#else
#  define D27_PUBLIC 0
#endif
#if defined(FOO_NCAPS) && defined(FOO_CALLOUTS) && defined(FOO_CODE_LANGS) && defined(FOO_CALLOUT_BINDINGS) && defined(FOO_ENGINE) && defined(PCREC_FEATURE_SET)
#  define D27_STAMPS 1
#else
#  define D27_STAMPS 0
#endif
/* §11.9¶4: "it can affect the translation unit's macros after it" */
#ifdef D27_FROM_CODE
#  define D27_SEG_MACRO 1
#else
#  define D27_SEG_MACRO 0
#endif

int main(void)
{
    rx_ctx ctx;
    static const unsigned char subj[] = "a";

    res("macro_set_undef_RX_SUBJ", !D27_RX_SUBJ);
    res("macro_set_undef_scalars", !D27_RX_SCALARS);
    res("macro_set_undef_caps", !D27_RX_CAPS);
    res("macro_set_undef_RX_G_name", !D27_RX_G);
    res("internal_macros_undef", !D27_INTERNAL);
    res("public_names_stay", D27_PUBLIC);
    res("stamps_stay", D27_STAMPS);
    res("segment_macro_reaches_after", D27_SEG_MACRO);
    res("engine_is_vm", strcmp(FOO_ENGINE, "vm") == 0); /* §11¶1 */
    res("code_langs_c", strcmp(FOO_CODE_LANGS, "c") == 0);
    res("callouts_2", FOO_CALLOUTS == 2);
    res("bindings_empty", strcmp(FOO_CALLOUT_BINDINGS, "") == 0);

    /* §11.2¶1 row 3 / ¶1a: <prefix>__code<k>_ref = { <prefix>__code<k>, NULL } */
    res("code1_ref_fn", foo__code1_ref.fn == foo__code1);
    res("code1_ref_user_null", foo__code1_ref.user == NULL);
    res("code2_ref_fn", foo__code2_ref.fn == foo__code2);
    res("code2_ref_user_null", foo__code2_ref.user == NULL);
    memset(&ctx, 0, sizeof ctx);
    ctx.subject = subj;
    ctx.len = 1;
    ctx.pos = 1;
    /* rx_matchfn contract (§2): must accept ncap == 0, caps == NULL */
    res("code1_is_first_segment", foo__code1_ref.fn(&ctx) == RX_PASS);
    res("code2_is_second_segment", foo__code2_ref.fn(&ctx) == RX_FAIL);

    /* the whole: (?C1)a(?C2-fails)|b(?<nm>z)? */
    res("search_a_fails", foo_search(subj, 1, 0, NULL) == 0);
    res("search_b_matches", foo_search((const unsigned char *)"b", 1, 0, NULL) == 1);
    return fails ? 1 : 0;
}
