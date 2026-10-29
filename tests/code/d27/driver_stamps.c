/* d27 driver: the stamps an artifact with code carries, read from the SPLIT
 * form's .h only (match_api.md §6.3.1¶1: `<PREFIX>_CALLOUTS`,
 * `<PREFIX>_CODE_LANGS`, `<PREFIX>_CALLOUT_BINDINGS`, §1¶6a's family and the
 * span helpers are in the .h). GEN_H is the header; the expectations come in
 * as -D macros from run.sh:
 *   WANT_CALLOUTS     integer, or undefined = the stamp must be absent
 *   WANT_BINDINGS     string,  or undefined = absent
 *   WANT_LANGS        string,  or undefined = absent
 *   WANT_SPAN         1 = PCREC_RX_SPAN_H and RX_PASS defined, 0 = neither
 *   P_                the upper-case prefix
 *   WANT_NO_LANGS / WANT_NO_CALLOUTS  (prefix rx) the stamp must be absent */
#include <stdio.h>
#include <string.h>
#include GEN_H

#define CAT_(a, b) a##b
#define CAT(a, b) CAT_(a, b)
#define ST(x) CAT(P_, x)

static int fails;
static void res(const char *what, int ok, const char *detail)
{
    if (ok)
        printf("PASS %s.%s\n", CASE, what);
    else {
        printf("FAIL %s.%s: %s\n", CASE, what, detail);
        fails++;
    }
}

int main(void)
{
    char buf[256];
    (void)buf;
#ifdef WANT_CALLOUTS
    snprintf(buf, sizeof buf, "expected %d got %lld", WANT_CALLOUTS, (long long)ST(_CALLOUTS));
    res("callouts", ST(_CALLOUTS) == WANT_CALLOUTS, buf);
#endif
#ifdef WANT_BINDINGS
    snprintf(buf, sizeof buf, "expected \"%s\" got \"%s\"", WANT_BINDINGS, ST(_CALLOUT_BINDINGS));
    res("bindings", strcmp(ST(_CALLOUT_BINDINGS), WANT_BINDINGS) == 0, buf);
#endif
#ifdef WANT_LANGS
    snprintf(buf, sizeof buf, "expected \"%s\" got \"%s\"", WANT_LANGS, ST(_CODE_LANGS));
    res("code_langs", strcmp(ST(_CODE_LANGS), WANT_LANGS) == 0, buf);
#endif
#ifdef WANT_NO_LANGS /* prefix rx only: the stamp is code-bearing scope (§6.3.2) */
#  ifdef RX_CODE_LANGS
    res("code_langs_absent", 0, "RX_CODE_LANGS defined on an artifact with no code segment");
#  else
    res("code_langs_absent", 1, "");
#  endif
#endif
#ifdef WANT_NO_CALLOUTS /* prefix rx only: callout-bearing scope */
#  if defined(RX_CALLOUTS) || defined(RX_CALLOUT_BINDINGS)
    res("callout_stamps_absent", 0, "RX_CALLOUTS/RX_CALLOUT_BINDINGS defined on a non-callout artifact");
#  else
    res("callout_stamps_absent", 1, "");
#  endif
#endif
#if WANT_SPAN
#  if defined(PCREC_RX_SPAN_H) && defined(RX_PASS) && defined(RX_FAIL) && defined(PCREC_RX_CALLOUT_H)
    res("span_family_present", 1, "");
    {
        rx_span s = { (const unsigned char *)"12", 2 };
        res("span_helper_callable", rx_in(s, 12, 12) == 1, "rx_in(\"12\",12,12) != 1");
    }
#  else
    res("span_family_present", 0, "PCREC_RX_SPAN_H/RX_PASS/RX_FAIL/PCREC_RX_CALLOUT_H missing from the .h");
#  endif
#else
#  if defined(PCREC_RX_SPAN_H) || defined(RX_PASS) || defined(PCREC_RX_CALLOUT_H)
    res("span_family_absent", 0, "a non-callout artifact carries the callout family or span helpers (§1¶6b)");
#  else
    res("span_family_absent", 1, "");
#  endif
#endif
    return fails ? 1 : 0;
}
