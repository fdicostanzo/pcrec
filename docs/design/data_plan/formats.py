# formats.py INC OUTDIR : storage-format sizes for the uprops interval pool (problem A, ruling R2)
import re, sys, zlib, lzma, struct, collections
inc, out = sys.argv[1], sys.argv[2]
t = open(inc).read()
pool_txt = t[t.index('pcrec_uprop_iv[] = {'):]
pool_txt = pool_txt[:pool_txt.index('};')]
iv = [(int(a, 0), int(b, 0)) for a, b in re.findall(r'\{\s*(0x[0-9A-Fa-f]+|\d+)u?\s*,\s*(0x[0-9A-Fa-f]+|\d+)u?\s*\}', pool_txt)]
names_txt = t[t.index('pcrec_uprop_names[] = {'):]
names_txt = names_txt[:names_txt.index('};')]
rows = re.findall(r'\{\s*"([^"]+)",\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\s*\}', names_txt)
sets = {}
for name, ns, off, n, cioff, cin in rows:
    for o, k in ((int(off), int(n)), (int(cioff), int(cin))):
        sets.setdefault((o, k), name)
spans = sorted(sets)
print(f"rows {len(rows)}  distinct sets {len(spans)}  pool intervals {len(iv)}  name bytes ~{sum(len(r[0])+1 for r in rows)}")
def vl(x):
    n = 1
    while x >= 128: x >>= 7; n += 1
    return n
def varint(x):
    b = bytearray()
    while x >= 128: b.append((x & 127) | 128); x >>= 7
    b.append(x); return bytes(b)
F0 = len(iv) * 8
blob = bytearray(); per = {}
for (o, k) in spans:
    prev = 0; s = bytearray()
    for lo, hi in iv[o:o+k]:
        s += varint(lo - prev) + varint(hi - lo); prev = hi
    per[(o, k)] = len(s); blob += s
F1 = len(blob)
raw = b''.join(struct.pack('<II', lo, hi) for lo, hi in iv)
Z0 = len(zlib.compress(raw, 9)); Z1 = len(zlib.compress(bytes(blob), 9)); X1 = len(lzma.compress(bytes(blob), preset=9))
open(f"{out}/varint.bin", "wb").write(blob); open(f"{out}/pairs.bin", "wb").write(raw)
open(f"{out}/varint.z", "wb").write(zlib.compress(bytes(blob), 9))
# per-set compressed bitmap (Frank's idea): 0x110000 bits each, zlib -9
def bitmap(ivs):
    x = 0
    for lo, hi in ivs: x |= ((1 << (hi - lo + 1)) - 1) << lo
    return x.to_bytes(0x110000 // 8, 'little')
bmz = {}
for sp in spans: bmz[sp] = len(zlib.compress(bitmap(iv[sp[0]:sp[0]+sp[1]]), 9))
BMZ = sum(bmz.values())
# shared two-stage (block-indexed) table: code point -> membership record over ALL distinct sets
NS = len(spans); B = 128
ev = collections.defaultdict(int)
for i, sp in enumerate(spans):
    bit = 1 << i
    for lo, hi in iv[sp[0]:sp[0]+sp[1]]:
        ev[lo] ^= bit; ev[hi + 1] ^= bit
member = [0] * 0x110000; cur = 0; pts = sorted(ev) + [0x110000]; last = 0
for pnt in pts:
    pnt = min(pnt, 0x110000)
    member[last:pnt] = [cur] * (pnt - last); last = pnt
    if pnt < 0x110000: cur ^= ev[pnt]
recid = {}; cprec = [recid.setdefault(m, len(recid)) for m in member]
blocks = {}; stage1 = []
for b in range(0, 0x110000, B):
    blk = tuple(cprec[b:b+B]); stage1.append(blocks.setdefault(blk, len(blocks)))
nrec = len(recid); recbytes = (NS + 7) // 8
s1 = len(stage1) * 2; s2 = len(blocks) * B * 2; rt = nrec * recbytes
print(f"F0 pairs u32x2        {F0:8d}")
print(f"F1 delta-varint       {F1:8d}   ({F0/F1:.2f}x)")
print(f"Z0 zlib(pairs)        {Z0:8d}   ({F0/Z0:.2f}x)")
print(f"Z1 zlib(varint)       {Z1:8d}   ({F0/Z1:.2f}x)")
print(f"X1 xz(varint)         {X1:8d}   ({F0/X1:.2f}x)")
print(f"BMZ per-set zlib bitmap {BMZ:8d} ({F0/BMZ:.2f}x)")
print(f"TS two-stage shared: stage1 {s1} + stage2 {len(blocks)} blocks*{B}*2 = {s2} + records {nrec}*{recbytes}B = {rt}  total {s1+s2+rt}")
# per-property examples
want = ['L', 'LU', 'N', 'GREEK', 'HAN', 'ZS', 'ALPHABETIC', 'IDCONTINUE', 'XIDC', 'EMOJI', 'WHITESPACE', 'CN']
byname = {}
for name, ns, off, n, cioff, cin in rows: byname.setdefault(name, (int(off), int(n)))
print("prop          intervals  pairs  varint  zbitmap")
for w in want:
    if w in byname:
        sp = byname[w]; print(f"{w:14s} {sp[1]:6d} {sp[1]*8:7d} {per[sp]:7d} {bmz[sp]:7d}")
