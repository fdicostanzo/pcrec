import csv,sys,collections
rows=list(csv.DictReader(open(sys.argv[1]),delimiter='\t',quoting=csv.QUOTE_NONE))
print('rows',len(rows))
by=collections.Counter((r['source'].split(':')[0]) for r in rows); print(by)
print('ERR utf8',sum(r['wr_utf8']=='ERR' for r in rows),'ERR byte',sum(r['wr_byte']=='ERR' for r in rows))
cl=[r for r in rows if r['caseless']=='1']; print('caseless scope',len(cl),collections.Counter(r['source'].split(':')[0] for r in cl))
tw=[r for r in cl if r['twin_wr_utf8']!='']; print('with literal k/s twin',len(tw))
aff=[]
for r in tw:
    if r['wr_utf8']=='ERR': continue
    d=(r['wr_utf8']!=r['twin_wr_utf8'] or r['run_utf8']!=r['twin_run_utf8'])
    s=(r['eng_utf8'],r['scan_utf8'],r['pf_utf8'],r['hand_utf8'])!=(r['twin_eng'],r['twin_scan'],r['twin_pf'],r['twin_hand'])
    r['d']=d; r['s']=s
    if d or s: aff.append(r)
print('twin differs (run or strategy):',len(aff),' run differs:',sum(r['d'] for r in aff),' strategy differs:',sum(r['s'] for r in aff))
with open(sys.argv[2],'w') as f:
    f.write('source\tid\tpattern\twr_utf8_today\ttwin_wr\trun_utf8\ttwin_run\tstrategy_utf8\tstrategy_twin\n')
    for r in aff:
        f.write('\t'.join([r['source'],r['id'],r['pattern'],r['wr_utf8'],r['twin_wr_utf8'],r['run_utf8'],r['twin_run_utf8'],'/'.join([r['eng_utf8'],r['scan_utf8'],r['pf_utf8'],'h'+r['hand_utf8']]),'/'.join([r['twin_eng'],r['twin_scan'],r['twin_pf'],'h'+r['twin_hand']])])+'\n')
for src in ('corpus','bench'):
    a=[r for r in aff if r['source'].startswith(src)]; print(src,len(a))
print('--- twin-eligible but unaffected examples')
for r in tw[:0]: pass
