import re,sys,glob
rows="""3 3 3
422 461
535 535
543 543
570 579
751 756
777 777
848 852
994 1017
1358 1358
1506 1507
1528 1539
1575 1579
1541 1556
1590 1592
1613 1625
1668 1677
1737 1738
1937 1938
1998 1998
2013 2018
2030 2030
2035 2035
2048 2052
2139 2139
2270 2272
2415 2620
2620 2641
2642 2745
2757 2771
3231 3231
3439 3455
3456 3469
3360 3361
3741 3744
3760 3760
4118 4125
4426 4426
4527 4547
4549 4565
4244 4245
4265 4271
4275 4285
4604 4610
1595 1606
1659 1660
3 3""".split("\n")
R=[tuple(map(int,r.split()[-2:])) if len(r.split())>1 else None for r in rows]
R=[(3,3)]+[r for r in R[1:] if r]
# add 4271 includes (58),(59); (55) 4265-4271 ok
def cov(n): return any(a<=n<=b for a,b in R)
for f in sorted(glob.glob(sys.argv[1]+'/hits_*.txt')):
    h=[int(x) for x in open(f)]
    u=[x for x in h if not cov(x)]
    print(f.split('hits_')[1][:-4],len(h),'uncovered',len(u),u if len(u)<60 else u[:60])
