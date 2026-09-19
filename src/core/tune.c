/* src/core/tune.c — [OPT-DIAL] THE DIAL'S PINNED POLICY TABLE, AND ITS ONE
 * HOME (docs/design/opt_dial_design.md §3.3 as ratified at its §9 item 2;
 * docs/dev/decisions.md D103; the CONTRACT is docs/spec/tuning.md §5).
 *
 * WHY THIS FILE EXISTS. `--tune=N` names a POSITION and a position names a
 * set of per-axis values. Those values could have been spread across the
 * sites that spend them — a conditional in `compile.c` for the ladder, one
 * in `emit_vm.c` for the entry-chain term, a flag bit set in `cli/main.c` —
 * and every one of them would then be a second place the contract lives.
 * So the table is DATA, in one file, and every site asks it.
 *
 * THE TABLE IS A PINNED CONTRACT (D103 point 1). A cell changes only by an
 * explicit ruled diff — never because a measurement lands. The same
 * `--tune=N` therefore compiles to the same switch set across releases,
 * whatever a later sweep goes on to find. `opt_dial_design.md` §3.2 is the
 * PROPOSAL RUBRIC by which a future cell change is argued; it is not an
 * assignment mechanism and nothing in this file evaluates it.
 *
 * THE ALLOWLIST (design §3.1), which is what keeps the table short: the dial
 * may never set a switch that has no MEASURED two-axis rate. Twenty of the
 * twenty-three `tuning.md` §2 axes therefore have no cell here at all, each
 * with its reason code stated in the spec — "we considered it and the number
 * is missing" and "we forgot it" must not look the same.
 *
 * THE EM-DASH SENTINEL IS 0, AND IT MEANS "THE DIAL DOES NOT TOUCH THIS
 * AXIS AT THIS POSITION" — never "set it to zero". Each SITE resolves the
 * sentinel against its OWN built-in default, which is deliberate: the
 * defaults live where they already lived (`PCREC_SIZE_TERM_THRESHOLD` in
 * `limits.def`, `VM_INLINE_CHAIN_MAX_BYTES` in `emit_vm.c`'s own home, the
 * materiality bar beside `size_term_choose`), so this file adds a dial
 * without becoming a second home for any of them.
 *
 * WHICH MAKES POSITION 0 A STRUCTURAL NO-OP BY CONSTRUCTION, not by care:
 * every cell of the `balanced` row is the sentinel and its deny mask is
 * empty, so there is no code path on which an artifact built at `balanced`
 * can differ from one built with no flag at all. That is an acceptance cell
 * (`tests/codegen/run_tune_dial.sh` section 1) rather than a promise.
 *
 * WHAT IS DELIBERATELY ABSENT. `-fno-anchored-dfa` — the largest size lever
 * the dial has — is NOT in the `min-size` row. Its penalty is a
 * three-population distribution (1.161x / 1.986x / 2.114x,
 * docs/dev/opt2_anchored_match_measurement.md) whose WORST population is
 * what a dial position must be admitted at, and 2.114x fails the working
 * bound of 2.00x by 5.7%. It returns only if its own owed A/B (the shipped
 * flag has never been measured; the ledger's number is a proxy on the
 * mechanism's predecessor) says otherwise, and that would be its own ruled
 * diff. See design §0.1.
 */

#include <stdio.h>
#include <string.h>

#include "internal.h"

/* THE TABLE. One row per position, indexed `tune + 2` by `tune_row()`.
 *
 * Every non-sentinel cell's citation is in `docs/spec/tuning.md` §5 and in
 * the design's §3.3, in the cell itself — a cell with no citation is an
 * em-dash, which is the allowlist made mechanical rather than a rule a
 * reader has to apply afterwards. */
static const PcrecTuneRow TUNE_TABLE[5] = {
    /* −2 `min-size`: the [ART-SIZE] ladder's two parameters, plus
     * `-fno-premul-table` denied UNCONDITIONALLY — premultiplication's
     * denial costs `1 + 0.794*phi_scan` of match time, which is inside a
     * doubling for EVERY share of scan time, so this cell needs no
     * measurement it does not have. */
    { PCREC_TUNE_MIN_SIZE,  "min-size",  95,  40000, 0,
      PCREC_NO_PREMUL_TABLE },

    /* −1 `size`: the ladder's two parameters alone. The three
     * phi-conditional cells (premul, tiered-entry, lambda) stay em-dashed
     * until their own on-demand measurement — a condition is not a cell. */
    { PCREC_TUNE_SIZE,      "size",      85,  80000, 0, 0 },

    /* 0 `balanced`: TODAY'S DEFAULTS, BYTE FOR BYTE (Frank's
     * keep-the-defaults ruling, 2026-09-04). Every cell is the sentinel;
     * this row must stay all-sentinel or the no-op acceptance cell is a
     * lie. */
    { PCREC_TUNE_BALANCED,  "balanced",   0,      0, 0, 0 },

    /* +1 `speed`: the VM entry chain's size term raised to 8,192, which
     * admits the three measured cells just above today's 4,096 (program
     * 5,183 / 5,985 / 6,954 bytes, five times better bytes-per-ns than the
     * next cell up) and admits nothing beyond them. */
    { PCREC_TUNE_SPEED,     "speed",      0,      0, 8192, 0 },

    /* +2 `max-speed`: IDENTICAL TO +1 ON EVERY CELL, and it ships that way
     * DECLARED rather than hidden (design §6.3, S219's precedent).
     *
     * ITS BECOME-REACHABLE CONDITION, stated here because a vacuous row
     * nobody wrote a trigger for is a row that stays vacuous: `+2` becomes
     * distinct from `+1` the day EITHER lambda is implemented (`[CLS-TREE]`
     * — the class-matcher kit's own dial, where `+1` selects frontier point
     * 64 and `+2` selects 256) OR the speed-notch floor `s` is ruled below
     * 1.03, which is what would let the `[ART-SIZE]` ladder's speed side
     * stop being em-dashed. The `+2` cell that revision 1 of the design
     * carried — an entry-chain term of 13,312 — was WITHDRAWN because its
     * number came from a recommendation phrase and not from a measurement,
     * and there is no measured cell above program 6,954 bytes to cite. */
    { PCREC_TUNE_MAX_SPEED, "max-speed",  0,      0, 8192, 0 }
};

/* The alias table is the SAME data read the other way. It is derived from
 * `TUNE_TABLE` rather than written a second time, so a token and its
 * position cannot drift — which is the defect `pcrec_tune_token` below
 * would otherwise be free to have. */

bool pcrec_tune_valid(int tune)
{
    return tune >= PCREC_TUNE_MIN_SIZE && tune <= PCREC_TUNE_MAX_SPEED;
}

const PcrecTuneRow *pcrec_tune_row(int tune)
{
    if (!pcrec_tune_valid(tune)) return &TUNE_TABLE[PCREC_TUNE_BALANCED + 2];
    return &TUNE_TABLE[tune + 2];
}

const char *pcrec_tune_token(int tune)
{
    return pcrec_tune_row(tune)->token;
}

/* Parse BOTH spellings on equal terms: the ordinal (`-2`..`2`, with `+` and
 * leading zeros accepted the way `strtol` accepts them) and the five
 * mnemonic aliases. Returns 0 and writes `*out` on success, non-zero on a
 * value this dial does not have.
 *
 * OUT-OF-RANGE IS REFUSED, NEVER CLAMPED, and that is the point of the
 * stamp: a clamp would let a caller believe they had asked for something
 * the artifact does not have. */
int pcrec_tune_parse(const char *s, int *out)
{
    if (!s || !*s) return 1;

    for (int i = 0; i < 5; i++)
        if (!strcmp(s, TUNE_TABLE[i].token)) { *out = TUNE_TABLE[i].pos; return 0; }

    /* The numeric spelling. `strtol` is not used: it would accept leading
     * whitespace and a trailing `\0`-terminated tail this option has no use
     * for, and the accepted set here is small enough to spell exactly. */
    {
        const char *p = s;
        int sign = 1;
        if (*p == '+' || *p == '-') { sign = (*p == '-') ? -1 : 1; p++; }
        if (p[0] < '0' || p[0] > '9' || p[1] != '\0') return 1;
        int v = sign * (p[0] - '0');
        if (!pcrec_tune_valid(v)) return 1;
        *out = v;
        return 0;
    }
}

/* [REVW.4] wave 4 (L2-L2-7): THE `vm_entry_shape` RUNG NAMES, one home.
 * The four rung names were spelled in TWO places — `src/gen/emit_vm.c`'s
 * `<PREFIX>_VM_ENTRY_SHAPE` stamp ladder and `cli/main.c`'s own
 * `--vm-entry-shape` menu — with `docs/spec/tuning.md` §2.21 as a third,
 * prose copy. They live here beside the dial's own ordinal table because
 * that is what a rung IS (an ordinal in the dial's direction, [CC-DIFF]
 * STEP 2), and `src/core` is the lowest layer both readers sit above.
 *
 * Index IS the ordinal, `PCREC_VM_ENTRY_AUTO` (0) included — the emitter
 * never asks for AUTO (it resolves the rung first) but the CLI's menu
 * names it, so a table missing it would be a table with a hole. */
static const char *const VM_ENTRY_NAMES[] = {
    "auto", "plain", "shared", "forward", "inline"
};

const char *pcrec_vm_entry_shape_name(int shape)
{
    if (shape < 0 || shape > PCREC_VM_ENTRY_INLINE) return "";
    return VM_ENTRY_NAMES[shape];
}

/* The menu a diagnostic prints: "0 auto, 1 plain, ...". `pcrec_tune_names`'
 * bounded-join policy exactly (an ordered PREFIX, the separator under the
 * same bound as the text it precedes). 44 bytes; its one caller passes
 * 128. */
void pcrec_vm_entry_shape_names(char *buf, size_t cap)
{
    size_t k = 0;
    if (!cap) return;
    buf[0] = 0;
    for (int i = 0; i <= PCREC_VM_ENTRY_INLINE; i++) {
        char item[32];
        int ln = snprintf(item, sizeof item, "%s%d %s", k ? ", " : "",
                          i, VM_ENTRY_NAMES[i]);
        if (ln < 0 || k + (size_t)ln + 1 > cap) break;
        memcpy(buf + k, item, (size_t)ln);
        k += (size_t)ln;
    }
    buf[k] = 0;
}

/* [REVW.4] wave 4 (L2-L2-7): the alias menu a diagnostic prints, rendered
 * from THE TABLE rather than written a second time in `cli/main.c`. The
 * bounded-join policy is `pcrec_enc_names`' (src/enc/enc.c), for its reasons:
 * an ordered PREFIX rather than a gap, and the separator written under the
 * SAME bound as the name it follows, so a tight cap can never emit a
 * dangling ", ". The menu is 44 bytes and its one caller passes 128. */
void pcrec_tune_names(char *buf, size_t cap)
{
    size_t k = 0;
    if (!cap) return;
    for (int i = 0; i < 5; i++) {
        const char *n = TUNE_TABLE[i].token;
        size_t ln = strlen(n) + (k ? 2 : 0);
        if (k + ln + 1 > cap) break;
        if (k) { buf[k++] = ','; buf[k++] = ' '; }
        memcpy(buf + k, n, strlen(n));
        k += strlen(n);
    }
    buf[k] = 0;
}

/* THE THREE VALUE CELLS. Each returns the dial's value or 0, the em-dash
 * sentinel; the CALLER resolves 0 against its own built-in default. */

int pcrec_tune_size_term_bar(int tune)
{
    return pcrec_tune_row(tune)->size_term_bar;
}

long long pcrec_tune_size_term_threshold(int tune)
{
    return pcrec_tune_row(tune)->size_term_threshold;
}

long long pcrec_tune_vm_inline_chain_max(int tune)
{
    return pcrec_tune_row(tune)->vm_inline_chain_max;
}

/* THE DENY MASK. These are OR'd into the caller's own flags, never assigned
 * over them: a caller who typed `-fno-premul-table` at `+1` keeps their
 * denial, because the dial sets a policy and does not revoke an explicit
 * request. Where a FORCE spelling exists the explicit flag wins outright;
 * where one does not, the spec says so rather than implying otherwise
 * (docs/spec/tuning.md §5, the narrowed "where a spelling exists" clause). */
uint64_t pcrec_tune_deny_flags(int tune)
{
    return pcrec_tune_row(tune)->deny_flags;
}
