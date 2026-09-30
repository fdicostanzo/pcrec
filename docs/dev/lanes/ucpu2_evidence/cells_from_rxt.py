# Turns .rxt blocks into oracle cells: the block's options as PCRE2 compile
# bits (utf8 = UTF, u = UCP, i = CASELESS, and MATCH_INVALID_UTF when asked).
import json, re, sys
UTF=0x00080000; UCP=0x00020000; CASELESS=0x8; MIU=0x04000000
def unesc(s):
    s = s[1:-1]; out = bytearray(); i = 0
    while i < len(s):
        if s[i] == '\\':
            n = s[i+1]
            if n == 'x': out.append(int(s[i+2:i+4],16)); i += 4; continue
            out.append({'n':10,'t':9,'r':13,'"':34,'\\':92}.get(n, ord(n))); i += 2; continue
        out += s[i].encode('utf-8'); i += 1
    return bytes(out)
cells = []
miu = '--miu' in sys.argv
for path in [a for a in sys.argv[1:] if not a.startswith('--')]:
    pat = None; enc = flags = ''
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        if line.startswith('pattern '): pat = line[8:]; enc = flags = ''; continue
        if line.startswith('encoding '): enc = line[9:]; continue
        if line.startswith('flags '): flags = line[6:]; continue
        m = re.match(r'^(m|n|ms|ns) (.*)$', line)
        if not m or pat is None: continue
        k, rest = m.groups()
        sp = 0
        if k in ('ms','ns'):
            sp, rest = rest.split(' ',1); sp = int(sp)
        mm = re.match(r'^(".*")(?: (\d+) (\d+))?$', rest)
        subj = unesc(mm.group(1))
        want = [int(mm.group(2)), int(mm.group(3))] if k in ('m','ms') else None
        o = (UTF if enc == 'utf8' else 0) | (UCP if 'u' in flags else 0) | (CASELESS if 'i' in flags else 0) | (MIU if miu and enc == 'utf8' else 0)
        cells.append({'p': pat.encode('utf-8').hex(), 's': subj.hex(), 'o': o, 'sp': sp, 'w': want})
print('@@CELLS@@' + json.dumps(cells))
