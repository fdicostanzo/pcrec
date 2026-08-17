#!/usr/bin/env python3
"""ARCHIVED INSTRUMENT (K24 fix lane, 2026-08-17).

Build K24 lever variants from a single baseline gen.c/gen.h pair.

Each variant is the emitter's output with one candidate attribute inserted at
the site the emitter would insert it, so the head-to-head measures exactly
what landing the lever would produce.
"""
import os, shutil, sys

S = sys.argv[1]
base = os.path.join(S, "base")
src = open(os.path.join(base, "gen.c")).read()

SEARCH_DEF = "int rx_search(const unsigned char *s, size_t n, size_t startpos, ptrdiff_t (*caps)[2])\n"
MATCH_DEF = "ptrdiff_t rx_match(const rx_ctx *ctx)\n"
MCAPS_DEF = "ptrdiff_t rx_match_caps(const rx_ctx *ctx, ptrdiff_t (*caps_out)[2])\n"

for needle in (SEARCH_DEF, MATCH_DEF, MCAPS_DEF):
    assert src.count(needle) == 1, (needle, src.count(needle))


def on_wrappers(attr):
    s = src.replace(MATCH_DEF, attr + "\n" + MATCH_DEF)
    return s.replace(MCAPS_DEF, attr + "\n" + MCAPS_DEF)


def on_search(attr):
    return src.replace(SEARCH_DEF, attr + "\n" + SEARCH_DEF)


VARIANTS = {
    # name: (source text, extra cflags)
    "base":        (src, []),
    "fnpi":        (src, ["-fno-partial-inlining"]),          # the known-good control
    "noipa_w":     (on_wrappers("__attribute__((noipa))"), []),
    "noinline_w":  (on_wrappers("__attribute__((noinline))"), []),
    "cold_w":      (on_wrappers("__attribute__((cold))"), []),
    "hot_s_cold_w": (on_wrappers("__attribute__((cold))").replace(
                        SEARCH_DEF, "__attribute__((hot))\n" + SEARCH_DEF), []),
    "hot_s":       (on_search("__attribute__((hot))"), []),
    "noclone_s":   (on_search("__attribute__((noclone))"), []),
    "optattr_s":   (on_search('__attribute__((optimize("no-partial-inlining")))'), []),
    "noipa_s":     (on_search("__attribute__((noipa))"), []),
}

for name, (text, extra) in VARIANTS.items():
    d = os.path.join(S, "v_" + name)
    os.makedirs(d, exist_ok=True)
    shutil.copy(os.path.join(base, "gen.h"), os.path.join(d, "gen.h"))
    open(os.path.join(d, "gen.c"), "w").write(text)
    open(os.path.join(d, "CFLAGS"), "w").write(" ".join(extra) + "\n")
    print(name, "->", d, "extra:", extra)
