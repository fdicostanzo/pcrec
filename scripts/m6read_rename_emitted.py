#!/usr/bin/env python3
"""[M6-READ] rename emitted identifiers, INSIDE C string literals only.

The emitter writes the artifact's identifiers as text inside sb_printf/sb_puts
format strings. Renaming them with a plain search-and-replace over the source
would also hit the emitter's OWN locals, which happen to share several
spellings (`fs`, `first`, `n`, `s`). This scans the C source for string
literals and rewrites only their contents, so emitter code is untouchable by
construction.

Usage: rename_emitted.py FILE [FILE...]
"""
import re, sys

# Applied in order, longest/most specific first. Each entry is (regex, repl)
# and is matched against the CONTENT of a string literal only.
TABLES = [
    ("fcls",  "forward_byte_class"),
    ("ftr",   "forward_next_state"),
    ("facc2", "forward_is_accepting_by_class"),
    ("facc",  "forward_is_accepting"),
    ("fseed", "forward_seed_state"),
    ("fendv", "forward_end_view"),
    ("fev",   "forward_eol_view"),
    ("first", "can_begin_match"),
    ("rcls",  "reverse_byte_class"),
    ("rtr",   "reverse_next_state"),
    ("racc2", "reverse_is_accepting_by_class"),
    ("racc",  "reverse_is_accepting"),
    ("rseed", "reverse_seed_state"),
    ("rendv", "reverse_end_view"),
    ("rev",   "reverse_eol_view"),
    ("fs",    "forward_stay"),
    ("rs",    "reverse_stay"),
]

LOCALS = [
    ("startpos", "search_from"),
    ("sfound",   "match_start_position"),
    ("erst",     "reverse_view_state"),
    ("rst",      "reverse_state"),
    ("est",      "forward_view_state"),
    ("last",     "last_accept_position"),
    ("pos",      "scan_position"),
    ("pp",       "rewind_position"),
    ("st",       "forward_state"),
    ("end",      "match_end_position"),
    ("cl",       "forward_class"),
    ("rcl",      "reverse_class"),
    ("caps_out", "capture_spans_out"),
    ("caps",     "capture_spans"),
    ("n",        "subject_length"),
    ("s",        "subject"),
]

def literals(src):
    """Yield (start, end) spans of C string literals in src."""
    i, out, N = 0, [], len(src)
    while i < N:
        ch = src[i]
        if ch == '"':
            j = i + 1
            while j < N:
                if src[j] == '\\':
                    j += 2
                    continue
                if src[j] == '"':
                    break
                j += 1
            out.append((i + 1, j))
            i = j + 1
        elif ch == "'":
            j = i + 1
            while j < N:
                if src[j] == '\\':
                    j += 2
                    continue
                if src[j] == "'":
                    break
                j += 1
            i = j + 1
        elif src.startswith('//', i):
            i = src.find('\n', i)
            if i < 0: break
        elif src.startswith('/*', i):
            i = src.find('*/', i) + 2
            if i < 1: break
        else:
            i += 1
    return out

def rewrite_literal(text, pairs, prefixed):
    for old, new in pairs:
        if prefixed:
            # a table name is always written as `%s_<tag>` or passed as "<tag>"
            text = re.sub(r'(?<=_)' + old + r'\b', new, text)
            text = re.sub(r'\A' + old + r'\Z', new, text)
        else:
            # A local is a bare identifier. The exclusion set is load-bearing:
            #   [A-Za-z0-9_]  another identifier's tail (`const` ends in `st`)
            #   %             a printf conversion (`%s`, `%d`) -- NOT the
            #                 emitted subject pointer
            #   \\            a C escape. Without this, `n` matches the `n` of
            #                 every `\n` in every format string and the emitter
            #                 starts writing `\subject_length`.
            # and a precise ABI guard: only `ctx->FIELD` / `ctx.FIELD` are
            # frozen. A blanket "never after . or >" would ALSO protect the
            # VM's own `run->trail`, which must be renamed -- so the guard
            # names the struct rather than the punctuation.
            #   '             an ENGLISH POSSESSIVE inside emitted prose.
            #                 Emitted comments are string literals too, and
            #                 without this `gcc's` becomes `gcc'subject`.
            #                 Measured -- it shipped into one comment before
            #                 anyone read the output.
            text = re.sub(r"(?<![A-Za-z0-9_%\\'])(?<!ctx->)(?<!ctx\.)"
                          + old + r'\b(?![A-Za-z0-9_])', new, text)
    return text

# Functions whose emitted text is FROZEN and must not be touched.
# `emit_rx_abi_types` writes the shared PCREC_RX_ABI_H block -- rx_ctx and its
# fields, rx_matchfn, rx_group_entry, struct rx_info. That block is spec S2's
# verbatim quote and [M6-READ] changes NOTHING in it. It also DECLARES fields
# named `pos` and `caps`, so a rename that reaches it renames the ABI itself
# and every emitted artifact stops compiling. (Measured: it did. The
# use-site guards protect `ctx->pos`; nothing protects `size_t pos;` inside
# the struct definition except excluding the function outright.)
FROZEN_EMITTERS = ["emit_rx_abi_types"]

def frozen_spans(src):
    out = []
    for name in FROZEN_EMITTERS:
        m = re.search(r'^static void ' + name + r'\s*\(', src, re.M)
        if not m:
            continue
        # the function ends at the first `}` in column 0 after its opening
        end = src.find('\n}\n', m.start())
        out.append((m.start(), end if end > 0 else len(src)))
    return out

def main():
    for path in sys.argv[1:]:
        src = open(path).read()
        frozen = frozen_spans(src)
        spans = [(a, b) for (a, b) in literals(src)
                 if not any(fa <= a <= fb for (fa, fb) in frozen)]
        nskip = len(literals(src)) - len(spans)
        out, prev = [], 0
        for a, b in spans:
            out.append(src[prev:a])
            body = src[a:b]
            body = rewrite_literal(body, TABLES, True)
            body = rewrite_literal(body, LOCALS, False)
            out.append(body)
            prev = b
        out.append(src[prev:])
        open(path, 'w').write(''.join(out))
        print("rewrote %d literals in %s (%d skipped inside frozen emitters)"
              % (len(spans), path, nskip))

if __name__ == '__main__':
    main()
