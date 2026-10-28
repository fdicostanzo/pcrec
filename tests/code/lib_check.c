/* tests/code/lib_check.c — the library's code grant ([INLINE-C] stage 2;
 * docs/spec/match_api.md §8.2 `allow_code`, §11.9): `allow_code` is the
 * ONLY library door to embedded code. `features` "all" does not open it,
 * naming the module in `features` is refused, an unknown language is
 * refused, and `allow_code = "c"` compiles. Links build/libpcrec.a. */
#include <stdio.h>
#include <string.h>
#include "pcrec.h"

static int fails;

static void row(const char *what, const char *features, const char *allow,
                int want_ok, const char *want_msg)
{
    pcrec_options o;
    pcrec_output out = { 0 };
    pcrec_error e = { 0 };
    pcrec_default_options(&o);
    if (features) o.features = features;
    o.allow_code = allow;
    const int rc = pcrec_compile("a(?C`c: return RX_PASS;`)b", &o, &out, &e);
    const int ok = rc == 0;
    if (ok != want_ok || (!ok && want_msg && !strstr(e.msg, want_msg)) ||
        (ok && (!out.c_src || !strstr(out.c_src, "return RX_PASS;")))) {
        printf("FAIL: library %s: rc %d msg '%s'\n", what, rc, e.msg);
        fails++;
    } else {
        printf("PASS: library %s\n", what);
    }
    if (ok) pcrec_output_free(&out);
}

int main(void)
{
    row("default options refuse code", NULL, NULL, 0, "allow_code");
    row("features \"all\" does not grant code", "all", NULL, 0, "allow_code");
    row("features naming code-c is refused", "code-c", NULL, 0, "code-c");
    row("allow_code \"py\" (unknown) is refused", NULL, "py", 0, "py");
    row("allow_code \"c\" compiles the segment", NULL, "c", 1, NULL);
    row("allow_code \"c\" with features \"all\"", "all", "c", 1, NULL);
    return fails != 0;
}
