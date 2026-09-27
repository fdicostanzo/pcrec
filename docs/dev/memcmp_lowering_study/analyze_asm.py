#!/usr/bin/env python3
"""Split a gcc/clang arm64 (or x86_64) .s file into per-function bodies and
report: does it call memcmp/bcmp/bl <libcall>, how many load instructions
(ldr/ldrh/ldrb/ldur variants), how many compares, how many branches, and the
raw instruction count of the body. Prints one TSV row per function found.
Heuristic but adequate for this probe's own generated symbol names."""
import re, sys

def split_functions(text, symbols):
    # arm64/x86_64 Mach-O gcc/clang emits "_cmp_memcmp_4:" as a label
    # (leading underscore on darwin). A function body runs from that label
    # to the next ".globl" directive (which always precedes the NEXT
    # function's own label) or EOF. Internal branch-target labels
    # (L3:, LBB0_2:, LFBn:/LFEn:) are NOT boundaries and are left in the
    # body; classify() strips bare label lines before counting.
    lines = text.splitlines()
    bodies = {}
    cur = None
    buf = []
    label_re = re.compile(r'^_?([A-Za-z_][A-Za-z0-9_]*):$')
    for line in lines:
        stripped = line.strip()
        # clang labels carry a trailing "; @name" (arm64) or "## @name" (x86
        # AT&T) comment; strip it before matching.
        for marker in ('##', ';'):
            if marker in stripped:
                stripped = stripped.split(marker, 1)[0].strip()
        if stripped.startswith('.globl') or stripped.startswith('.cfi_endproc'):
            if cur is not None:
                bodies[cur] = buf
                cur = None
                buf = []
            continue
        m = label_re.match(stripped)
        if m and m.group(1) in symbols:
            if cur is not None:
                bodies[cur] = buf
            cur = m.group(1)
            buf = []
            continue
        if cur is not None:
            buf.append(line)
    if cur is not None:
        bodies[cur] = buf
    return bodies

def classify(lines):
    insns = [l.strip() for l in lines if l.strip() and not l.strip().startswith('.')
             and not l.strip().startswith(';') and not l.strip().startswith('#')
             and not l.strip().startswith('L')]
    # drop pure label lines like "LBB0_3:"
    insns = [l for l in insns if not re.match(r'^[.A-Za-z0-9_]+:$', l)]
    calls = [l for l in insns if re.match(r'^(bl|callq?)\b', l)]
    loads = [l for l in insns if re.match(r'^(ldr|ldrh|ldrb|ldur|ldp|movzbl|movzwl|movl|movq|mov)\b', l) and ('[' in l or '(' in l or re.match(r'^ld', l))]
    cmps = [l for l in insns if re.match(r'^(cmp|ccmp|subs|cmpq|cmpl)\b', l)]
    branches = [l for l in insns if re.match(r'^(b\.|cbz|cbnz|tbnz|tbz|je|jne|jmp|jz|jnz|b\b)', l)]
    return {
        'n_insns': len(insns),
        'n_calls': len(calls),
        'calls': ';'.join(calls)[:80],
        'n_loads': len(loads),
        'n_cmps': len(cmps),
        'n_branches': len(branches),
    }

def main():
    path = sys.argv[1]
    text = open(path).read()
    # collect candidate symbol names present in the file
    names = set(re.findall(r'^_?(cmp_(?:memcmp|mask|overlap)_\d+):', text, re.M))
    bodies = split_functions(text, names)
    print("func\tn_insns\tn_calls\tcalls\tn_loads\tn_cmps\tn_branches")
    for name in sorted(bodies, key=lambda s: (s.split('_')[1], int(s.rsplit('_',1)[1]))):
        info = classify(bodies[name])
        print(f"{name}\t{info['n_insns']}\t{info['n_calls']}\t{info['calls']}\t{info['n_loads']}\t{info['n_cmps']}\t{info['n_branches']}")

if __name__ == "__main__":
    main()
