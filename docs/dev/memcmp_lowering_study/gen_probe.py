#!/usr/bin/env python3
"""Generate one C probe file per L (constant compare length), in the shape
P4 emits (src/gen/emit_dfa.c:766, emit_exact_compare): a guarded, constant-
length memcmp against a string literal. One function per L in one file so
each L's -S output is a distinct labeled block; also emits the load+mask
hand-twin (WORD-FOLD shape) and its overlapping-load sibling for L in
{3,5,6,7,9,10,11,13,15} (the odd lengths §3 of the brief asks about) and for
every other L as `#if` guarded so a single file compiles as either the
memcmp probe or the mask probe, selected by a macro."""
import sys

LENGTHS = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,20,24,31,32,33,40,48,64]

def lit_bytes(n):
    # deterministic, printable-ish, avoids quote/backslash
    base = b"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    out = (base * ((n // len(base)) + 1))[:n]
    return out

def c_escape(bs):
    return "".join("\\x%02x" % b for b in bs)

def emit_memcmp_fn(n):
    lit = lit_bytes(n)
    esc = c_escape(lit)
    return f'''
int cmp_memcmp_{n}(const unsigned char *s, size_t pos, size_t n_) {{
    return pos + {n}u <= n_ && !memcmp(s + pos, "{esc}", {n});
}}
'''

def mask_load_type(n):
    # smallest power-of-two-or-exact integer type that covers n bytes,
    # via a load-and-mask over an 8-byte (or 4-byte) window.
    if n <= 4:
        return 4, "uint32_t"
    return 8, "uint64_t"

def emit_mask_fn(n):
    """The load+AND-mask+compare form ([WORD-FOLD] shape): one load of the
    smallest covering width (4 or 8 bytes), masked to the low n bytes,
    compared against the same n-byte literal zero-extended. SAFETY: this
    reads WIDTH bytes starting at s+pos, so it requires pos + WIDTH <= n_
    (a wider read than the run itself) OR the overlapping-load form below."""
    width, ty = mask_load_type(n)
    if n > width:
        return f"/* cmp_mask_{n}: no single-load mask form (n={n} > width={width}) */\n"
    lit = lit_bytes(n)
    mask_bits = n * 8
    mask_hex = "0x" + "ff" * n
    # build the little-endian constant for the literal bytes
    val = int.from_bytes(lit, "little")
    return f'''
int cmp_mask_{n}(const unsigned char *s, size_t pos, size_t n_) {{
    {ty} w;
    if (pos + {width}u > n_) return 0;
    memcpy(&w, s + pos, {width});
    return (w & ({ty}){mask_hex}ULL) == ({ty}){val}ULL;
}}
'''

def emit_overlap_fn(n):
    """The overlapping two-load form: L=7 as load4@0 and load4@3 (or the
    general two half-width loads overlapping by 2*half - n bytes), each
    masked/compared to the corresponding literal slice. SAFETY: requires
    pos + n <= n_ only (no over-read past the run itself)."""
    if n < 5 or n > 8:
        return f"/* cmp_overlap_{n}: only built for 5<=n<=8 in this probe */\n"
    lit = lit_bytes(n)
    half = 4
    off2 = n - half
    lo = lit[:half]
    hi = lit[off2:off2+half]
    vlo = int.from_bytes(lo, "little")
    vhi = int.from_bytes(hi, "little")
    return f'''
int cmp_overlap_{n}(const unsigned char *s, size_t pos, size_t n_) {{
    uint32_t a, b;
    if (pos + {n}u > n_) return 0;
    memcpy(&a, s + pos, 4);
    memcpy(&b, s + pos + {off2}, 4);
    return a == (uint32_t){vlo}ULL && b == (uint32_t){vhi}ULL;
}}
'''

def natural_half_width(n):
    """The smallest natural (power-of-two) load width W such that two
    W-byte windows genuinely overlap and together cover n bytes: W < n and
    2*W >= n. Returns None for n itself a natural width (1,2,4,8 — a
    single load already covers it exactly, no overlap needed) or n > 16
    (out of this comparison's scope — [WORD-FOLD]'s own population is
    short literal-with-case-variation spans, not 64-byte runs)."""
    for w in (2, 4, 8):
        if w < n <= 2 * w:
            return w
    return None

def emit_ovmask_fn(n):
    """[2026-09-27 follow-up, manager + Frank] THE OVERLAPPING MASKED
    form, the primary [WORD-FOLD]/S4 candidate: two overlapping loads of
    one natural width W (W < n <= 2W), each AND-masked with a per-byte
    ASCII case-fold mask (0xDF, clears bit 5 so 'a'..'z' folds onto
    'A'..'Z') and compared against the literal's OWN folded value — a
    genuine ASCII caseless compare, not a trivially-constant-foldable
    all-ones mask. SAFETY: only pos + n <= n_ — P4's own bound, never
    wider. This is the form the manager's note asks to promote to the
    primary mask candidate, ahead of the single-wide-load over-read form
    below (kept as one comparison row only, per the same note)."""
    w = natural_half_width(n)
    if w is None:
        return f"/* cmp_ovmask_{n}: no natural two-window overlap (n={n}) */\n"
    ty = {2: "uint16_t", 4: "uint32_t", 8: "uint64_t"}[w]
    lit = lit_bytes(n)
    off2 = n - w
    lo, hi = lit[:w], lit[off2:off2 + w]
    fold_mask = int.from_bytes(bytes([0xDF]) * w, "little")
    lo_folded = int.from_bytes(bytes(b & 0xDF for b in lo), "little")
    hi_folded = int.from_bytes(bytes(b & 0xDF for b in hi), "little")
    return f'''
int cmp_ovmask_{n}(const unsigned char *s, size_t pos, size_t n_) {{
    {ty} a, b;
    if (pos + {n}u > n_) return 0;
    memcpy(&a, s + pos, {w});
    memcpy(&b, s + pos + {off2}, {w});
    return (a & ({ty}){fold_mask}ULL) == ({ty}){lo_folded}ULL
        && (b & ({ty}){fold_mask}ULL) == ({ty}){hi_folded}ULL;
}}
'''

def main():
    print("#include <string.h>")
    print("#include <stdint.h>")
    print("#include <stddef.h>")
    for n in LENGTHS:
        print(emit_memcmp_fn(n))
    for n in LENGTHS:
        print(emit_mask_fn(n))
    for n in (5,6,7):
        print(emit_overlap_fn(n))
    for n in LENGTHS:
        print(emit_ovmask_fn(n))

if __name__ == "__main__":
    main()
