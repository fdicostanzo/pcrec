#!/usr/bin/env python3
"""tests/codegen/stmt_writer_scan.py -- [VMREC] (a) ST: the VM body has ONE
writer (docs/dev/lanes/vmrec_report.md, "Structural checks").

The VM matcher's body buffer (`Job.vmsb`) is written only by the record
renderers in src/gen/vm_stmt.c. Its tiling check catches a foreign write at
run time on the compiles that reach it; this scan catches one STATICALLY, on
every path, including the comment tier a default compile never prints. Rules,
over the C TEXT of every .c/.h under src/, cli/, lib/ (comments and string
literals blanked, so prose and emitted text never count):

  one-writer    `vmsb` is named only in src/gen/vm_stmt.c, in
                src/core/internal.h's one field declaration, and in the
                driver's (src/core/compile.c) buffer LIFECYCLE: free, the
                ctx binding, the comment tier, the size abort, the cleanup
                list (LIFECYCLE below; no write verb is among them);
  opaque-body   `struct VmBody {` is defined only in src/gen/vm_stmt.c;
  no-handle     src/gen/vm_stmt.h declares no function returning a StrBuf.

Usage: stmt_writer_scan.py ROOT [EXPECTED_FILES]. Prints its populations
(files, lines, the allowed mentions it found) so a scan that read nothing
cannot pass: EXPECTED_FILES is the caller's independent count of the same
files (git ls-files), and the two allowed mentions are positive controls.
Prints `PASS:`/`FAIL:` lines; exit 1 on any FAIL."""
import os, re, sys

root = sys.argv[1]
expected = int(sys.argv[2]) if len(sys.argv) > 2 else None
fails = 0

def bad(msg):
    global fails
    fails += 1
    print("FAIL: " + msg)

def code_of(text):
    """C text with comments and string/char literals blanked (newlines kept)."""
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if text.startswith('/*', i):
            j = text.find('*/', i + 2); j = n if j < 0 else j + 2
            out.append(re.sub(r'[^\n]', ' ', text[i:j])); i = j
        elif text.startswith('//', i):
            j = text.find('\n', i); j = n if j < 0 else j
            out.append(' ' * (j - i)); i = j
        elif c in '"\'':
            j = i + 1
            while j < n and text[j] != c:
                j += 2 if text[j] == '\\' else 1
            j = min(j + 1, n)
            out.append(c + re.sub(r'[^\n]', ' ', text[i + 1:j - 1]) + c); i = j
        else:
            out.append(c); i += 1
    return ''.join(out)

# The driver's lifecycle forms: each names the buffer and writes no byte.
LIFECYCLE = re.compile(r'\s*(pcrec_sb_free\(&cx->job->vmsb\);'
                       r'|cx\.job->vmsb\.cx = .*;'
                       r'|pcrec_sb_comments\(&cx\.job->vmsb, \w+\);'
                       r'|cx\.job->vmsb\.abort_over = \w+;'
                       r'|.*&cx\.job->vmsb, &cx\.job->\w+ \};)\s*')

files, nlines = [], 0
for top in ('src', 'cli', 'lib'):
    for d, _, fs in os.walk(os.path.join(root, top)):
        files += [os.path.join(d, f) for f in fs if f.endswith(('.c', '.h'))]
files.sort()
seen = {'vm_stmt.c': 0, 'internal.h': 0, 'body-def': 0, 'lifecycle': 0}
for path in files:
    rel = os.path.relpath(path, root)
    code = code_of(open(path, encoding='utf-8', errors='replace').read())
    lines = code.split('\n')
    nlines += len(lines)
    for no, ln in enumerate(lines, 1):
        if re.search(r'\bvmsb\b', ln):
            if rel == 'src/gen/vm_stmt.c':
                seen['vm_stmt.c'] += 1
            elif rel == 'src/core/internal.h' and re.fullmatch(r'\s*StrBuf\s+vmsb\s*;\s*', ln):
                seen['internal.h'] += 1
            elif rel == 'src/core/compile.c' and LIFECYCLE.fullmatch(ln):
                seen['lifecycle'] += 1
            else:
                bad(f"one-writer: {rel}:{no} names the VM body buffer `vmsb` "
                    "outside src/gen/vm_stmt.c (build a record instead)")
        if re.search(r'\bstruct\s+VmBody\s*\{', ln):
            if rel == 'src/gen/vm_stmt.c':
                seen['body-def'] += 1
            else:
                bad(f"opaque-body: {rel}:{no} defines struct VmBody outside src/gen/vm_stmt.c")
    if rel == 'src/gen/vm_stmt.h':
        for m in re.finditer(r'StrBuf\s*\*\s*\w+\s*\(', code):
            no = code[:m.start()].count('\n') + 1
            bad(f"no-handle: {rel}:{no} declares a function returning a StrBuf")

print(f"population: {len(files)} files, {nlines} lines of C text scanned"
      + (f" (independent count: {expected} files)" if expected is not None else ""))
print(f"population: allowed mentions found: vm_stmt.c {seen['vm_stmt.c']}, "
      f"internal.h field {seen['internal.h']}, compile.c lifecycle {seen['lifecycle']}, "
      f"VmBody definition {seen['body-def']}")
if expected is not None and expected != len(files):
    bad(f"population: scanned {len(files)} files, the independent count is {expected}")
if not files or nlines == 0:
    bad("population: nothing scanned")
for k, what in (('vm_stmt.c', 'the body buffer in vm_stmt.c'),
                ('internal.h', "internal.h's vmsb field"),
                ('body-def', "vm_stmt.c's struct VmBody definition")):
    if seen[k] == 0:
        bad(f"control: the scan did not find {what}, so it reads nothing")
if fails == 0:
    print("PASS: the VM body has one writer (src/gen/vm_stmt.c)")
sys.exit(1 if fails else 0)
