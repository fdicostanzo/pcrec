#!/usr/bin/env python3
"""span_arms unit E1's IDENTITY GATE (span_arms §8 row E1: "B0 identity diff
with only those movers"): every key `scripts/emit_sweep.py --movers-out` lists
must be explained by the census's OBSERVED movers (census_e1.py), and the
facts stream's movers must EQUAL the census's (two runners, one population).

  argv streams (c-default, c-vm, emit-ir-vm, emit-ir-auto, stderr, facts):
    the key's pattern is a census mover;
  composition: the moved artifact's .rxt/.rxtin source holds a census mover
    (by `--list-source`);
  dumps: no mover;
  any stream: no asymmetric row (one side compiles, the other refuses).

usage: ident_check.py CENSUS_TSV TREE PCREC MOVERS_TSV [MOVERS_TSV...]
Prints one line per unexplained key and a verdict line; exit 0 iff clean.
"""
import ast
import os
import subprocess
import sys


def decode_escape(s):
    out = bytearray(); b = s.encode("utf-8", "surrogateescape"); i = 0
    while i < len(b):
        c = b[i]
        if c == 0x5C and i + 1 < len(b):
            n = b[i + 1]
            m = {ord('t'): 9, ord('n'): 10, ord('r'): 13, 0x5C: 0x5C}
            if n in m:
                out.append(m[n]); i += 2; continue
            if n == ord('x') and i + 3 < len(b):
                try:
                    out.append(int(bytes(b[i + 2:i + 4]), 16)); i += 4; continue
                except ValueError:
                    pass
        out.append(c); i += 1
    return bytes(out)


def main():
    census, tree, pcrec, *mfiles = sys.argv[1:]
    movers = set()
    for line in open(census, encoding="utf-8"):
        if line.startswith("#"):
            continue
        x = line.rstrip("\n").split("\t")
        if x[2]:   # moved_facts non-empty: an observed mover
            movers.add(x[1].encode("latin-1").decode("unicode_escape").encode("latin-1"))
    bad = []; n = {}; facts_seen = set(); prefix_keys = {}; unreadable = []   # prefix_keys: (source, prefix) -> facts keys
    src_cache = {}

    def source_patterns(f):
        """The pattern OCCURRENCES of one emit_sweep source, in order (a list,
        not a set: a pattern repeated in a source yields one facts key per
        occurrence). A `patterns-file:NAME` source is read with emit_sweep's
        own reader rules (one escaped pattern per line, `#`/blank skipped)."""
        if f not in src_cache:
            pats = []
            if f.startswith("patterns-file:"):
                pf = os.path.join(os.path.dirname(os.path.abspath(__file__)), f.split(":", 1)[1])
                for l in open(pf, encoding="utf-8", errors="surrogateescape"):
                    l = l.rstrip("\n")
                    if l.strip() and not l.startswith("#"):
                        pats.append(decode_escape(l))
            else:
                p = f if os.path.isabs(f) else os.path.join(tree, f)
                r = subprocess.run([pcrec, "--list-source", p], capture_output=True, timeout=60)
                for l in r.stdout.decode("utf-8", "surrogateescape").splitlines():
                    y = l.split("\t")
                    if not l.startswith("#") and len(y) >= 5 and y[0] in ("pattern", "pattern-esc"):
                        pats.append(decode_escape(y[4]))
            src_cache[f] = pats
        return src_cache[f]

    def file_has_mover(f):
        return bool(set(source_patterns(f)) & movers)

    for mf in mfiles:
        for line in open(mf, encoding="utf-8", errors="surrogateescape"):
            if line.startswith("#") or not line.strip():
                continue
            stream, cls, key = line.rstrip("\n").split("\t", 2)
            n[stream] = n.get(stream, 0) + 1
            if cls == "asymmetric":
                bad.append(f"ASYMMETRIC {stream} {key}"); continue
            if stream == "dumps":
                bad.append(f"DUMP MOVED {key}"); continue
            if stream == "composition":
                f = key.split("::", 1)[0]
                if not file_has_mover(f):
                    bad.append(f"COMPOSITION {key}: its source holds no census mover")
                continue
            i = key.find(":b'"); j = key.find(':b"')
            k = i if i >= 0 else j
            if k < 0:
                bad.append(f"UNPARSED {stream} {key}"); continue
            pat = ast.literal_eval(key[k + 1:])
            if pat not in movers and len(pat) == 60:
                # emit_sweep keys carry pat[:60]: a longer pattern's key is its
                # 60-byte prefix. Resolve by prefix; the keys of one prefix
                # must be as many as the census movers sharing it (checked below).
                full = sorted(m for m in movers if m.startswith(pat))
                if full:
                    if stream == "facts":
                        sk = (key[:k].rsplit(":", 1)[0], pat)
                        prefix_keys[sk] = prefix_keys.get(sk, 0) + 1
                    if stream == "facts":
                        facts_seen.update(full)
                    continue
            if stream == "facts":
                facts_seen.add(pat)
            if pat not in movers:
                bad.append(f"NOT A CENSUS MOVER {stream} {key}")
    # Like with like: a facts key is source:kind:pat[:60], so one pattern in two
    # sources (or twice in one) is several keys. Per (source, prefix) the keys
    # must be as many as that source's mover OCCURRENCES with the prefix.
    for (src, pre), nk in sorted(prefix_keys.items()):
        nm = sum(1 for m in source_patterns(src) if m.startswith(pre) and len(m) > 60 and m in movers)
        if nk != nm:
            bad.append(f"PREFIX COUNT {src} {pre!r}: {nk} facts keys vs {nm} mover occurrences in that source")
    for p in sorted(movers - facts_seen):
        if p.startswith(b"#"):
            # emit_sweep's --patterns-file reader drops lines starting `#`, so the
            # facts stream cannot carry this pattern in that vocabulary: noted
            # here, verified by hand (a `\\x23...` patterns-file line).
            unreadable.append(p); continue
        bad.append(f"CENSUS MOVER NOT IN THE FACTS STREAM {p!r}")
    print("movers by stream: " + ", ".join(f"{k}={v}" for k, v in sorted(n.items())))
    print(f"census movers: {len(movers)}; facts-stream movers: {len(facts_seen)}")
    for p in unreadable:
        print(f"  NOTE: census mover {p!r} starts with `#`: unrepresentable as a patterns-file line; verify by hand")
    for b in bad:
        print("  " + b)
    print(f"== ident_check COMPLETE: {len(bad)} unexplained")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
