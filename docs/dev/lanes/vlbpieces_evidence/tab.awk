function g0(x,  out,n,i,parts){ n=split(x,parts,"]"); out=""; for(i=1;i<=n;i++){ sub(/,.*/,"",parts[i]); out=out parts[i] "]"}; return out }
NR>1 {
  cf = ($5==0) ? "capfree" : "caps";
  nv = ($3<=1) ? "nvar<=1" : ("nvar>=2," ($4=="True"?"exposed":"not-exposed"));
  if ($5==0) nv = ($3<=1)?"nvar<=1":"nvar>=2";
  k = $2 "\t" cf "\t" nv;
  n[k]++; if ($8!=$9) r[k]++; if ($8!=$10) d[k]++; if (g0($8)!=g0($10)) y[k]++; if ($8!=$11) t[k]++; if (g0($8)!=g0($11)) ty[k]++;
}
END { printf "form\tcaptures\tvariable pieces\tcells\trange differs\tpieces differs (any group / group 0)\ttrim differs (any group / group 0)\n";
      for (k in n) printf "%s\t%d\t%d\t%d / %d\t%d / %d\n", k, n[k], r[k], d[k], y[k], t[k], ty[k] }
