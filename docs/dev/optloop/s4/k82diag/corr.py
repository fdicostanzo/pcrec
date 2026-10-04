import re, collections
mac={}
for l in open('pc.out'):
    m=re.search(r'^(\S+)\s+n=\s*(\d+) base=\s*([\d.]+) new=\s*([\d.]+) d=\s*([+-][\d.]+) pass=([\d.]+) memchr/call=([\d.]+) cmp/call=([\d.]+) u,c,sel,uni=(.*)',l)
    if m: mac[m.group(1)]=m.groups()
rows=[]
for l in open('lx_unionsrch.txt'):
    f=l.split()
    if len(f)<9 or not f[1].startswith('short:'): continue
    id=f[1][6:]; b,n=float(f[3]),float(f[4]); fl=float(f[7]); v=f[8]
    m=mac[id]; rows.append((n-b,id,int(m[1]),b,n,fl,v,m[6],m[7],m[5],m[3],m[4]))
rows.sort()
grp=collections.defaultdict(list)
for r in rows:
    print("%-26s n=%4d lx base=%7.2f new=%7.2f d=%+6.2f fl=%.3f %-10s | gate memchr=%s cmp=%s pass=%s | mac d=%s"%(r[1],r[2],r[3],r[4],r[0],r[5],r[6],r[7],r[8],r[9],r[11]))
    grp[(r[7],r[8],r[9])].append(r)
print()
for k,v in sorted(grp.items()):
    news=[x[4] for x in v]; ds=[x[0] for x in v]
    print("memchr=%s cmp=%s pass=%s: cells=%d lx new %.2f..%.2f  delta %+.2f..%+.2f  REG=%d WIN=%d"%(k[0],k[1],k[2],len(v),min(news),max(news),min(ds),max(ds),sum(1 for x in v if x[6]=='REGRESSION'),sum(1 for x in v if x[6]=='WIN')))
