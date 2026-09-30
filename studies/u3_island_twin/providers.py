"""providers.py -- the VECTOR PRODUCERS for the island (ucp_design.md s4):
`static inline int P_in(unsigned cp)` for a non-ASCII code-point interval list.

  kit4      [CLS-TREE]'s sectioned kit at the ONE pinned constant, lambda = 4
            (D131 item 1) -- the study's own `discover` DP + `emit.py`.
  page3w    the whole-set three-stage table (wholeset.PageW3, TS = 10).
  bitmap1   one bitmap over the set's whole span (kit.FormBitmap).

All three are the cls_tree_study's own generators, imported, not copied.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.join(HERE, "..", "cls_tree_study")
sys.path.insert(0, STUDY)
import emit   # noqa: E402
import kit    # noqa: E402
import section  # noqa: E402
import wholeset  # noqa: E402

DISCOVER = os.environ.get("DISCOVER", os.path.join(HERE, "out", "bin", "discover"))


def build_discover(cc="gcc-16"):
    os.makedirs(os.path.dirname(DISCOVER), exist_ok=True)
    if not os.path.exists(DISCOVER):
        subprocess.check_call([cc, "-O2", "-std=gnu11", os.path.join(STUDY, "discover.c"),
                               "-o", DISCOVER, "-lm"])


def provider_c(kind, P, iv):
    """C text defining `static inline int P_in(unsigned cp)` over `iv`."""
    fn = P + "_in"
    if not iv:
        return "static inline int %s(unsigned cp) { (void)cp; return 0; }\n" % fn
    if kind == "kit4":
        build_discover()
        sc, _, _, fo = section.partition_c(iv, 4.0, exe=DISCOVER)
        s, _ = emit.emit(fn, iv, sc, fo, static=True)
        return emit.PRELUDE + s
    if kind == "page3w":
        return wholeset.PageW3(iv).c(fn).replace("int %s(unsigned cp)" % fn,
                                                 "static inline int %s(unsigned cp)" % fn)
    if kind == "bitmap1":
        bm = kit.FormBitmap(iv)
        x = "(cp - %uu)" % bm.base if bm.base else "cp"
        return (bm.tables(fn + "_t") +
                "static inline int %s(unsigned cp)\n{\n"
                "    if ((unsigned)(cp - %uu) > %uu) return 0;\n"
                "    return (int)%s;\n}\n"
                % (fn, bm.base, bm.w - 1, bm.expr(x, fn + "_t")))
    if kind == "refbs":
        return emit.PRELUDE + emit.reference(fn, iv).replace("int %s(unsigned cp)" % fn,
                                              "static inline int %s(unsigned cp)" % fn)
    raise ValueError(kind)


def rodata_hint(kind, iv):
    if kind == "page3w":
        return wholeset.PageW3(iv).rodata()
    if kind == "bitmap1":
        return kit.FormBitmap(iv).rodata()
    return None
