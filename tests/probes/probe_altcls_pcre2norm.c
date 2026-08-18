/* tests/probes/probe_altcls_pcre2norm.c — [OPT-ALTCLS]'s "what does PCRE2
 * normalize here" survey, answered by MEASUREMENT rather than by reading
 * PCRE2's source or documentation (docs/dev/plan.md's [OPT-ALTCLS] row's own
 * obligation). Uses `pcre2_pattern_info_8` (PCRE2_INFO_SIZE/MINLENGTH/
 * FIRSTCODETYPE/FIRSTCODEUNIT/FIRSTBITMAP — the compiled pattern's own
 * reflection surface) to compare the alternation spelling against the
 * class/factored spelling for both stages.
 *
 * PREDICTOR, stated before the run: if PCRE2 already merges a single-char
 * alternation run into an internal class representation, `a(b|c)+d` and
 * `a([bc])+d` would compile to the SAME `PCRE2_INFO_SIZE` (same opcode
 * sequence); if it prefix-factors, `frank|fred|brad|bobby|janet` and its
 * hand-factored `fr(?:ank|ed)|b(?:rad|obby)|janet` spelling would too.
 *
 * MEASURED (2026-08-17, libpcre2 10.46, this probe): NEITHER holds, and the
 * direction is worth stating because it is not the null result it might
 * look like. `a(b|c)+d` compiles to `PCRE2_INFO_SIZE` 178 against
 * `a([bc])+d`'s 204 — the ALTERNATION spelling is SMALLER in PCRE2's own
 * bytecode, not merely different. `b|c|d|e|f` (181) against `[b-f]` (192)
 * repeats the same direction. `frank|fred|brad|bobby|janet` (217) against
 * the hand-factored `fr(?:ank|ed)|b(?:rad|obby)|janet` (223) is the same
 * story one level up: introducing the non-capturing group boundaries costs
 * PCRE2's interpreter MORE opcode bytes than it saves. `firstcodetype`/
 * `firstcodeunit`/`firstbitmap` (the first-byte optimization PCRE2 DOES
 * apply) agree across every pair in a family, so the size delta is not
 * measuring a first-byte-optimization difference — it is measuring the
 * class/factored spelling costing PCRE2 a BIGGER opcode program for the
 * IDENTICAL language.
 *
 * READING THIS RESULT: it is not a contradiction of [OPT-ALTCLS]'s own
 * measured win (docs/dev/plan.md's row, the emitted-C line-count and
 * VM-rung-collapse evidence) — it is a different compilation TARGET. PCRE2
 * compiles to a general bytecode interpreted by one dispatch loop, where a
 * class opcode carries a 32-byte-equivalent bitmap payload and a
 * non-capturing group costs its own BRA/KET bracket opcodes regardless of
 * whether the group's alternation is exercised; pcrec's stage 1/2 wins come
 * from ELIMINATING SPECIALIZED C: fewer emitted labels/branches (the VM
 * rung collapse), a narrower DFA byte-equivalence-class table, and fewer
 * generated `goto`s for gcc to schedule. A bytecode interpreter and an
 * ahead-of-time C emitter pay for the "same" construct along different
 * axes, and this probe's honest conclusion is that PCRE2 has NOT already
 * captured this win — it is a genuine, unexploited-by-PCRE2 opportunity
 * that is specific to compiling ahead of time to real branches rather than
 * to a portable bytecode.
 *
 * RE2: not measured here. `libre2.so.11` is present on this box (no `-dev`
 * headers, no CLI tool found), but RE2 has no public C ABI comparable to
 * `pcre2_pattern_info_8` — its API is C++, and probing it honestly would
 * need either RE2's C++ headers (a dependency this repo's CLAUDE.md
 * mandate forbids adding here — dependencies belong in pcrec-bench) or a
 * hand-rolled C++ shim built against the installed .so's mangled symbols,
 * which is a different-shaped tool than this dlopen probe and was not
 * built in this session. Recorded as an owed cell rather than skipped
 * silently.
 *
 * Build: TMPDIR=/var/tmp gcc -I tests/fuzz -o /var/tmp/probe \
 *          tests/probes/probe_altcls_pcre2norm.c -ldl
 * Archive: scripts/measure.sh probe_altcls_pcre2norm
 */
/* Must precede EVERY system header (glibc's feature-test-macro guards latch
 * on the FIRST one processed) — pcre2_abi.h's own dlinfo/RTLD_DI_LINKMAP use
 * needs it, and defining it only inside that header is too late once this
 * file's own <stdio.h>/<string.h> have already been processed without it. */
#define _GNU_SOURCE
#include <stdio.h>
#include <string.h>

#include "pcre2_abi.h"

/* PCRE2_INFO_* values from pcre2.h (stable across the 10.x series; this box
 * has no -dev package so the header is unavailable — see pcre2_abi.h's own
 * header for why this project hand-declares rather than includes). */
#define PCRE2_INFO_FIRSTCODEUNIT 5
#define PCRE2_INFO_FIRSTCODETYPE 6
#define PCRE2_INFO_FIRSTBITMAP   7
#define PCRE2_INFO_MINLENGTH     16
#define PCRE2_INFO_SIZE          22

/* `pcre2_pattern_info_8` resolved PROBE-SIDE, on top of the shared shim,
 * rather than added to ../fuzz/pcre2_abi.h's own loader table —
 * probe_subst.c's own precedent (see its header): that loader's dlsym
 * failures are FATAL for every consumer, including pcre2_check.c inside
 * `make test`, so a symbol only one probe needs does not belong there. */
typedef int (*fn_pattern_info)(const pcre2_code_8 *code, uint32_t what,
    void *where);

static void probe(Pcre2Abi *abi, fn_pattern_info info, const char *pat)
{
    int err;
    PCRE2_SIZE erroff;
    pcre2_code_8 *code = abi->compile((PCRE2_SPTR)pat, strlen(pat), 0,
                                       &err, &erroff, NULL);
    if (!code) {
        printf("%-40s COMPILE FAILED (err %d @ %zu)\n", pat, err, (size_t)erroff);
        return;
    }
    uint32_t sz = 0, minlen = 0, fct = 0, fcu = 0;
    uint8_t fbm[32] = {0};
    info(code, PCRE2_INFO_SIZE, &sz);
    info(code, PCRE2_INFO_MINLENGTH, &minlen);
    info(code, PCRE2_INFO_FIRSTCODETYPE, &fct);
    info(code, PCRE2_INFO_FIRSTCODEUNIT, &fcu);
    int has_fbm = info(code, PCRE2_INFO_FIRSTBITMAP, fbm);
    printf("%-40s size=%-6u minlen=%-3u firstcodetype=%u firstcodeunit=%u firstbitmap=%s\n",
           pat, sz, minlen, fct, fcu, has_fbm == 0 ? "set" : "null");
    abi->code_free(code);
}

int main(void)
{
    Pcre2Abi abi;
    char why[256];
    if (pcre2_abi_load(&abi, why, sizeof why) != PCRE2_ABI_OK) {
        printf("SKIP: %s\n", why);
        return 0;
    }
    fn_pattern_info info = (fn_pattern_info)dlsym(abi.handle, "pcre2_pattern_info_8");
    if (!info) {
        printf("SKIP: no pcre2_pattern_info_8: %s\n", dlerror());
        return 0;
    }
    char v[64];
    pcre2_abi_version(&abi, v, sizeof v);
    printf("libpcre2 %s at %s\n\n", v, pcre2_abi_path(&abi));

    printf("-- stage 1: single-char alternation vs class --\n");
    probe(&abi, info, "a(b|c)+d");
    probe(&abi, info, "a([bc])+d");
    probe(&abi, info, "b|c|d|e|f");
    probe(&abi, info, "[b-f]");

    printf("\n-- stage 2: prefix-shared alternation vs manually factored --\n");
    probe(&abi, info, "frank|fred|brad|bobby|janet");
    probe(&abi, info, "fr(?:ank|ed)|b(?:rad|obby)|janet");
    probe(&abi, info, "(?:frank|fred|brad|bobby|janet)+");
    probe(&abi, info, "(?:fr(?:ank|ed)|b(?:rad|obby)|janet)+");
    return 0;
}
