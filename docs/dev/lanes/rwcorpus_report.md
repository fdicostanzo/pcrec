# rwcorpus report — real-world SUBJECT corpus (plan row [REGIME-CORPUS], step 1)

Lane `rwcorpus`, 2026-10-13/14, sonnet. FACTS only: the held-out population of
text pcrec users scan, for validating the search-form decision table
(`docs/design/regime_tables.md`). No patterns, no questions, no timing.
Recipe: `rwcorpus/fetch.sh` + `rwcorpus/manifest.tsv` (88 rows: class, file,
bytes, sha256, url, license, date). Bytes live in `worktrees/.corpus/`
(gitignored), never in git. Provenance/licensing/PII: `rwcorpus/PROVENANCE.md`.
Shape tables below are produced by `rwcorpus/shape.py` (committed).

## Collected, per class (MiB incl. raw archives in the class dir)

| class | subjects | sources (license) |
|---|---|---|
| logs (~40 MiB derived x4 + small) | apache_error, linux_syslog, zookeeper, openstack (40 MiB cap), hadoop (cap), bgl (first 40 MiB), apache_access (10k lines) | Loghub via Zenodo 8196385 (CC-BY-4.0); elastic/examples apache_logs (Apache-2.0) |
| code (~76 MiB) | c.src (Lua + Redis src/tests), java.src (Guava), python.src (Django), javascript.src (jQuery), rust.src (ripgrep), go.src (cobra) | MIT / BSD-3 / Apache-2.0 release tarballs |
| prose (17.5 MiB) | 12 English Gutenberg books (Pride and Prejudice, Moby Dick, Frankenstein, A Tale of Two Cities, Sherlock Holmes, War and Peace, Dracula, Les Miserables, Monte Cristo, Don Quixote, Great Expectations, Huckleberry Finn) | public domain |
| structured | census gazetteer TSV (6.5 MB), USGS earthquakes CSV + GeoJSON, Natural Earth countries GeoJSON (13 MB, ONE line), GPO House bills XML (40 MiB cap, from 47.9 MB zip) | US gov PD, Natural Earth PD |
| markup (~53 MiB) | Python 3.12.7 docs HTML (40 MiB cap), Django docs reStructuredText, jQuery markdown | PSF/0BSD, BSD-3, MIT |
| nonenglish (9 MiB) | Chinese x6, Japanese x5, Cyrillic x7 (Russian, Bulgarian, Serbian), Greek x3, Hebrew x2, Latin-extended x3 (German x2, one more; shares in the script table), French x2 and one Latin-transliterated Sanskrit (near-ASCII) | public domain |
| binary-ish (~110 MiB) | django-5.0.tar and libpng-1.6.43.tar (uncompressed tars: NULs, headers, .mo/.png members), plus verbatim .tar.gz / .tar.bz2 / .zip streams (high entropy, ~42-43% invalid UTF-8) | BSD-3, PNG-RefLib, PSF, US gov PD |

Class sizes against the 1-50 MiB aim: every class has at least one subject in
range; the logs/binary classes are dominated by 40-50 MiB capped files.

## Skipped, and why
- Loghub SSH, Mac, Proxifier, HealthApp, Android, Windows, Thunderbird, HDFS, Spark: SSH/Mac/Proxifier carry client hostnames and user names (PII risk), others are multi-hundred-MB or not needed; HealthApp/Proxifier were fetched by accident and deleted.
- Real-site web access logs beyond the 10k-line elastic sample (NASA-HTTP 1995 carries client hostnames; no clean license statement found).
- Mail archives (mbox): names and addresses of real people; no scrubbable, license-clean source found.
- Project Gutenberg `pg_catalog.csv`: fetched, but no license statement could be established for the catalog; deleted.
- Wikipedia/Wikisource/MDN dumps: CC-BY-SA, not the preferred permissive tier.
- Arabic and Devanagari text: Gutenberg has essentially none (one Sanskrit book is Latin transliteration, `pg9000`; the 'ar' entry is an English title); no PD/CC0 source in these scripts was found within the lane. Scripts actually present: CJK, Kana, Cyrillic, Greek, Hebrew, Latin-extended (table below). A follow-up could add Arabic/Devanagari from a CC0/PD source.
- Govinfo and Natural Earth GeoJSON are fetched whole; nothing was excluded for size except the 40 MiB caps in prep.py.

## Scrubbing and checks (logs/code/markup/structured only)
IPv4 -> hashed `10.a.b.c`, e-mails -> `user@example.invalid`, `rhost=`/`user=`
values, ftpd reverse-DNS names. After scrubbing: no non-placeholder e-mail
address in any derived file (grep over logs, code, markup, structured); the only
non-10.x dotted quads left in logs are browser version strings in
apache_access (e.g. `17.0.963.79`). System account names (root, news, cyrus,
test) remain in syslog. Prose/nonenglish are as published. Scrubbing shifts byte
counts a little; the manifest pins post-scrub bytes.

## Notable shape facts
- Line structure ranges from one 13 MB line (Natural Earth GeoJSON) and a 7 MB line in the govinfo XML to ~7-byte median markdown; logs have p50 74-317 B; Gutenberg prose p50 ~68 B (wrapped at ~72); CJK/Japanese prose is paragraph-per-line (p99 up to 3.7 KB).
- Distinct bytes: logs 75-96; ASCII prose 91-120; code 99-198; every binary-class file 256.
- Invalid UTF-8 is zero in all text classes except syslog (0.01%) and the tars (0.8-1.5%); compressed streams are ~42% invalid by the strict-UTF-8 count.
- Multibyte share: CJK 84-96%, Cyrillic/Greek/Hebrew 65-80% of bytes.
- Volatile: the two USGS rows (`updated` field); fetch.sh warns rather than fails.

## Shape per file (computed by shape.py)
| file | bytes | lines | len min/p50/p90/p99/max | distinct | ASCII % | UTF-8 multibyte % | invalid % | top-10 bytes |
|---|---|---|---|---|---|---|---|---|
| prose/pg76.txt | 622460 | 12350 | 0/68/74/80/85 | 91 | 95.25 | 4.75 | 0.00 | ` :16.8% e:7.9% t:6.6% o:5.9% a:5.8% n:5.3% h:4.2% s:3.9% i:3.9% d:3.8%` |
| prose/pg84.txt | 448885 | 7741 | 0/69/74/76/100 | 97 | 99.23 | 0.77 | 0.00 | ` :16.0% e:10.2% t:6.6% a:5.9% o:5.6% n:5.4% i:4.8% s:4.6% r:4.6% h:4.3%` |
| prose/pg98.txt | 807197 | 16283 | 0/68/73/78/83 | 94 | 97.39 | 2.61 | 0.00 | ` :15.7% e:9.2% t:6.5% a:5.9% o:5.7% n:5.2% i:4.7% h:4.7% r:4.6% s:4.5%` |
| prose/pg135.txt | 3369207 | 73590 | 0/66/72/76/213 | 120 | 97.97 | 2.03 | 0.00 | ` :15.3% e:9.7% t:6.6% a:5.9% o:5.4% h:5.1% n:5.0% i:4.9% s:4.7% r:4.3%` |
| prose/pg345.txt | 890348 | 15853 | 0/70/73/77/86 | 107 | 98.43 | 1.57 | 0.00 | ` :17.6% e:9.1% t:6.5% a:5.9% o:5.8% n:5.0% h:4.8% s:4.4% i:4.3% r:4.1%` |
| prose/pg996.txt | 2391678 | 43289 | 0/69/72/78/88 | 111 | 98.11 | 1.89 | 0.00 | ` :16.5% e:9.0% t:6.8% a:6.1% o:6.0% h:5.1% n:5.1% i:4.7% s:4.6% r:4.1%` |
| prose/pg1184.txt | 2787124 | 61680 | 0/64/73/78/121 | 132 | 95.71 | 4.29 | 0.00 | ` :15.1% e:9.3% t:6.3% a:5.8% o:5.6% n:4.9% i:4.7% s:4.5% h:4.5% r:4.3%` |
| prose/pg1342.txt | 772386 | 14915 | 0/69/73/77/160 | 104 | 98.19 | 1.81 | 0.00 | ` :16.3% e:9.5% t:6.5% a:5.7% o:5.6% n:5.2% i:4.9% h:4.6% s:4.5% r:4.5%` |
| prose/pg1400.txt | 1058204 | 20780 | 0/68/73/78/85 | 97 | 96.67 | 3.33 | 0.00 | ` :16.2% e:8.8% t:6.5% a:5.9% o:5.7% n:5.0% i:4.5% h:4.5% s:4.3% r:4.0%` |
| prose/pg1661.txt | 607606 | 12310 | 0/67/72/78/89 | 103 | 96.61 | 3.39 | 0.00 | ` :16.2% e:9.0% t:6.5% a:5.8% o:5.7% n:4.8% h:4.7% i:4.5% s:4.5% r:4.2%` |
| prose/pg2600.txt | 3359610 | 66041 | 0/68/73/77/85 | 115 | 96.90 | 3.10 | 0.00 | ` :15.4% e:9.3% t:6.5% a:5.8% o:5.6% n:5.4% i:4.9% h:4.9% s:4.8% r:4.3%` |
| prose/pg2701.txt | 1276315 | 22331 | 0/69/72/77/85 | 114 | 98.16 | 1.84 | 0.00 | ` :15.5% e:9.3% t:6.9% a:6.0% o:5.5% n:5.2% i:5.0% s:5.0% h:4.9% r:4.1%` |
| nonenglish/pg1982.txt | 38473 | 594 | 0/68/118/121/121 | 153 | 53.08 | 46.92 | 0.00 | `\xe3:10.9% \x81:8.6%  :7.9% e:4.6% t:3.7% o:3.4% r:3.0% \x82:2.7% i:2.7% n:2.6%` |
| nonenglish/pg2790.txt | 67720 | 1641 | 0/44/67/75/97 | 147 | 41.27 | 58.73 | 0.00 | `\xd0:21.5%  :10.5% \xd1:7.6% \xb0:3.7% e:2.6% \xb8:2.5% \r:2.4% \n:2.4% \xb5:2.3% t:2.1%` |
| nonenglish/pg2890.txt | 115195 | 1834 | 0/70/77/88/741 | 145 | 38.97 | 61.03 | 0.00 | `\xd0:21.8%  :19.8% \xd1:8.7% \xb0:3.4% \xb5:2.6% \xb8:2.5% \xbe:2.4% \x82:2.1% \xbd:1.8% \x80:1.6%` |
| nonenglish/pg4572.txt | 95985 | 1680 | 0/73/73/74/79 | 154 | 23.29 | 76.71 | 0.00 | `\xe5:6.7% \xe4:4.1% \xe6:3.5%  :3.1% \xbc:3.0% \xef:2.8% \x80:2.8% \x8c:2.7% \xe8:2.5% \xe7:2.4%` |
| nonenglish/pg4573.txt | 100953 | 1726 | 0/73/73/75/80 | 154 | 22.31 | 77.69 | 0.00 | `\xe5:6.8% \xe4:4.0% \xe6:3.7% \x80:3.4%  :3.1% \xbc:2.8% \xef:2.7% \xe8:2.5% \x8c:2.5% \xe7:2.4%` |
| nonenglish/pg4580.txt | 667880 | 11106 | 0/73/73/74/89 | 156 | 6.52 | 93.48 | 0.00 | `\xe5:8.2% \xe4:4.7% \xe6:4.2% \xbc:3.5% \xe7:3.3% \xef:3.3% \x80:3.2% \x8c:3.1% \xe8:3.1% \xe9:2.9%` |
| nonenglish/pg6696.txt | 595842 | 9152 | 0/69/72/74/79 | 102 | 96.67 | 3.33 | 0.00 | ` :14.0% e:13.4% n:8.3% i:6.1% r:5.1% s:4.4% t:4.2% h:4.1% a:4.0% d:3.8%` |
| nonenglish/pg6698.txt | 1226130 | 19355 | 0/68/71/73/89 | 105 | 97.44 | 2.56 | 0.00 | `e:13.7%  :13.2% n:7.6% i:7.3% s:6.7% t:5.0% r:4.4% d:4.4% a:3.5% h:3.4%` |
| nonenglish/pg7221.txt | 382970 | 10046 | 0/37/97/103/103 | 156 | 10.44 | 89.56 | 0.00 | `\xe5:6.5% \xe6:5.1% \xe8:3.9% \x80:3.6% \xe4:3.6% \xe7:3.3% \xbc:3.2% \x8c:3.1% \xe9:2.7% \x82:2.6%` |
| nonenglish/pg7290.txt | 217952 | 2625 | 0/97/97/97/98 | 158 | 11.81 | 88.19 | 0.00 | `\xe5:6.4% \xe4:5.0% \xbc:4.1% \x80:4.1% \xe6:4.0% \xef:3.7% \xe8:3.7% \x8c:3.5% \xe7:2.7%  :2.1%` |
| nonenglish/pg7317.txt | 338372 | 6942 | 0/37/97/97/97 | 153 | 9.92 | 90.08 | 0.00 | `\xe5:6.9% \xe6:4.6% \xe4:4.2% \x80:3.9% \x8c:3.7% \xbc:3.5% \xe8:3.3% \xe7:3.2% \xef:3.0% \xe3:2.6%` |
| nonenglish/pg8186.txt | 922226 | 17811 | 0/66/70/71/108 | 94 | 99.98 | 0.02 | 0.00 | ` :14.3% e:13.1% s:6.0% a:5.6% i:5.5% t:5.4% n:5.0% r:4.9% u:4.8% o:4.4%` |
| nonenglish/pg8453.txt | 726547 | 15332 | 0/65/70/71/108 | 94 | 99.98 | 0.02 | 0.00 | ` :14.7% e:13.1% s:5.9% a:5.7% t:5.3% i:5.1% n:5.0% r:5.0% u:4.7% o:4.5%` |
| nonenglish/pg9000.txt | 35209 | 850 | 0/50/70/75/79 | 92 | 99.56 | 0.44 | 0.00 | ` :13.5% a:12.8% t:5.8% r:5.7% h:5.6% e:5.5% o:4.8% n:4.4% i:4.3% s:3.7%` |
| nonenglish/pg11291.txt | 430037 | 5292 | 0/108/119/122/235 | 151 | 18.60 | 81.40 | 0.00 | `\xd0:29.8% \xd1:10.8%  :9.8% \xb0:4.8% \xb8:4.2% \xb5:3.8% \xbe:3.7% \xbd:2.2% \x80:2.0% \x81:2.0%` |
| nonenglish/pg14741.txt | 220529 | 5655 | 0/45/67/111/199 | 150 | 23.09 | 76.91 | 0.00 | `\xd0:26.3% \xd1:11.9%  :8.1% \xb5:3.5% \xbe:3.3% \r:2.6% \n:2.6% \x82:2.3% \xb0:2.3% \x81:2.3%` |
| nonenglish/pg15008.txt | 239177 | 4767 | 0/34/124/130/134 | 146 | 25.13 | 74.87 | 0.00 | `\xd0:28.6%  :9.4% \xd1:8.7% \xb0:4.6% \xbe:3.3% \xb5:3.2% \xb8:3.1% .:2.0% \r:2.0% \n:2.0%` |
| nonenglish/pg17814.txt | 189012 | 3853 | 0/46/91/122/137 | 150 | 23.52 | 76.48 | 0.00 | `\xce:25.9% \xcf:11.6%  :8.3% \xb1:3.5% \x84:2.5% \xbf:2.5% \xbd:2.3% \xb5:2.2% \r:2.0% \n:2.0%` |
| nonenglish/pg17839.txt | 186151 | 3310 | 0/68/89/122/132 | 148 | 29.93 | 70.07 | 0.00 | `\xce:23.5%  :16.5% \xcf:11.0% \xb1:3.1% \xbf:2.8% \xbd:2.5% \x84:2.4% \xb5:2.0% \xb9:1.9% \r:1.8%` |
| nonenglish/pg20175.txt | 452084 | 3149 | 0/84/323/909/2188 | 150 | 19.68 | 80.32 | 0.00 | `\xc3:39.8%  :12.9% \xa1:4.7% \xb4:3.0% \xa5:2.8% \xad:2.4% \xaf:2.4% \xa9:2.3% \xaa:1.8% \xb3:1.7%` |
| nonenglish/pg26731.txt | 227670 | 3531 | 0/71/114/121/125 | 148 | 24.52 | 75.48 | 0.00 | `\xce:24.5%  :12.8% \xcf:12.6% \xb1:3.6% \x84:2.9% \xbf:2.9% \xbd:2.3% \xb9:2.3% \xb5:2.2% \x80:1.7%` |
| nonenglish/pg30774.txt | 102381 | 1387 | 0/70/131/137/139 | 152 | 30.38 | 69.62 | 0.00 | `\xd0:22.5% \xd1:12.1%  :8.5% \xbe:3.3% \xb0:2.4% \xb8:2.1% \xbd:2.0% \xb5:2.0% e:1.9% \x80:1.8%` |
| nonenglish/pg31617.txt | 564929 | 1933 | 0/115/793/2197/5260 | 153 | 4.21 | 95.79 | 0.00 | `\xe3:25.9% \x81:14.3% \x80:9.1% \x82:5.3% \x8b:4.8% \x8a:4.3% \xe5:1.7% \x84:1.2% \x93:1.1% \xae:1.0%` |
| nonenglish/pg31757.txt | 180913 | 1320 | 0/68/355/871/1483 | 153 | 12.32 | 87.68 | 0.00 | `\xe3:20.5% \x81:15.0% \x82:5.6% \x80:3.6% \xe5:2.4% \x8b:1.8% \xe6:1.8%  :1.7% \xaa:1.4% \xae:1.4%` |
| nonenglish/pg33307.txt | 223791 | 1474 | 0/67/358/1486/5332 | 153 | 9.93 | 90.07 | 0.00 | `\xe3:22.3% \x81:16.6% \x82:5.9% \x80:3.3% \xe5:2.7% \x8b:1.9% \xe6:1.7% \x84:1.4% \xae:1.4% \x8c:1.4%` |
| nonenglish/pg34013.txt | 367445 | 1074 | 0/70/1021/3736/7261 | 153 | 5.96 | 94.04 | 0.00 | `\xe3:25.9% \x81:14.1% \x80:9.7% \x82:5.0% \x8b:5.0% \x8a:4.3% \xe5:1.3% \x84:1.2% \xe6:1.1% \x8c:0.9%` |
| nonenglish/pg37196.txt | 72242 | 986 | 0/70/128/134/190 | 150 | 35.26 | 64.74 | 0.00 | `\xd0:22.7% \xd1:9.4%  :8.8% \xbe:3.4% \xb8:2.9% \xb5:2.7% \xb0:2.5% e:2.4% \xbd:2.2% t:2.0%` |
| nonenglish/pg43740.txt | 249476 | 2544 | 0/127/134/138/180 | 132 | 21.24 | 78.76 | 0.00 | `\xd7:39.1%  :11.3% \x95:4.9% \x99:4.3% \x94:2.8% \x90:2.7% \x9c:2.6% \x91:2.3% \xa8:2.3% \x9e:2.0%` |
| nonenglish/pg61024.txt | 156148 | 1836 | 0/120/131/133/136 | 119 | 24.76 | 75.24 | 0.00 | `\xd7:37.5%  :11.8% \x95:4.6% \x99:3.7% \x94:3.1% \x9c:2.5% \x90:2.4% \xa8:2.2% \x91:2.0% \x9e:2.0%` |
| binary/raw/libpng-1.6.43.tar.gz | 1554715 | 6068 | 0/171/584/1259/4966 | 256 | 49.94 | 6.97 | 43.09 | `\xff:0.4% 8:0.4% \x1c:0.4% \x92:0.4% \xa3:0.4% \xc3:0.4% \xbd:0.4% \x93:0.4% \x8c:0.4% \xe1:0.4%` |
| logs/apache_error.log | 5121846 | 56481 | 34/96/108/121/186 | 78 | 100.00 | 0.00 | 0.00 | ` :12.6% r:5.5% e:5.3% o:4.9% t:4.8% 0:4.7% n:3.9% i:3.8% 2:3.5% 1:3.3%` |
| logs/linux_syslog.log | 2302067 | 25567 | 0/74/139/192/1030 | 96 | 99.99 | 0.00 | 0.01 | ` :13.1% o:5.8% e:5.6% ::4.3% t:3.6% 0:3.5% s:3.5% 2:3.4% r:3.3% c:3.1%` |
| logs/zookeeper.log | 10599180 | 74380 | 0/139/174/209/388 | 80 | 100.00 | 0.00 | 0.00 | ` :8.7% e:6.8% r:5.6% 1:4.9% 0:4.1% n:4.1% 2:4.0% o:3.7% ::3.5% 8:3.1%` |
| logs/openstack.log | 41942978 | 140875 | 0/317/345/366/454 | 79 | 100.00 | 0.00 | 0.00 | ` :6.6% 1:6.3% a:5.2% e:5.2% -:5.1% 0:4.8% 2:4.3% 4:4.1% 5:4.0% c:3.8%` |
| logs/hadoop.log | 41942934 | 355100 | 0/90/210/282/578 | 92 | 100.00 | 0.00 | 0.00 | `e:7.0% a:6.4%  :5.6% o:5.3% t:5.1% .:4.8% r:4.1% 0:3.7% n:3.6% p:3.3%` |
| logs/bgl.log | 41942927 | 309536 | 0/127/147/196/477 | 75 | 100.00 | 0.00 | 0.00 | `0:10.7% 1:9.0% -:8.7%  :8.3% .:4.2% 2:4.0% 5:3.9% 6:3.5% R:3.2% N:2.9%` |
| logs/apache_access.log | 2369603 | 10000 | 0/230/314/444/1363 | 88 | 100.00 | 0.00 | 0.00 | ` :7.9% 0:6.7% /:5.1% 1:5.0% .:4.7% e:4.1% o:3.6% t:3.0% 2:3.0% i:2.8%` |
| code/c.src | 7231205 | 191918 | 0/34/74/113/678 | 119 | 99.97 | 0.03 | 0.00 | ` :22.7% e:6.5% t:4.6% i:3.7% r:3.6% n:3.6% s:3.4% a:3.2% o:3.1% l:2.7%` |
| code/go.src | 467001 | 15272 | 0/24/70/105/201 | 99 | 100.00 | 0.00 | 0.00 | ` :11.8% e:7.1% t:5.6% r:4.8% o:4.4% n:4.4% i:4.0% a:3.6% s:3.6% \t:3.4%` |
| code/java.src | 28100746 | 786097 | 0/31/80/100/10193 | 190 | 99.98 | 0.02 | 0.00 | ` :18.1% e:8.1% t:6.1% a:4.3% r:4.3% i:4.1% n:4.0% o:3.7% s:3.7% l:3.1%` |
| code/javascript.src | 2730048 | 82159 | 0/23/71/116/87443 | 145 | 99.99 | 0.01 | 0.00 | ` :12.1% e:8.0% t:6.0% \t:5.5% r:4.2% n:4.1% s:3.8% a:3.8% i:3.6% o:3.5%` |
| code/python.src | 17011821 | 463514 | 0/34/72/86/172 | 198 | 99.96 | 0.04 | 0.00 | ` :26.4% e:7.7% t:4.9% s:4.8% a:4.0% r:3.6% o:3.4% i:3.2% l:3.2% n:3.2%` |
| code/rust.src | 1691876 | 50217 | 0/30/73/79/117 | 149 | 99.97 | 0.03 | 0.00 | ` :24.0% e:7.1% t:5.4% r:4.4% s:3.9% a:3.9% i:3.5% n:3.4% o:3.3% \n:3.0%` |
| markup/python_docs.html | 41942992 | 514933 | 0/47/218/495/5495 | 157 | 99.81 | 0.19 | 0.00 | ` :9.6% s:7.6% a:7.0% e:6.5% n:5.2% t:4.7% l:4.6% ":4.3% >:4.1% <:4.1%` |
| markup/django_docs.rst | 5827256 | 155958 | 0/32/77/84/532 | 136 | 99.99 | 0.01 | 0.00 | ` :14.8% e:8.4% t:6.1% a:5.2% o:4.9% s:4.7% i:4.4% n:4.4% r:3.9% l:3.0%` |
| markup/jquery_md.md | 25712 | 651 | 0/7/104/361/518 | 95 | 99.99 | 0.01 | 0.00 | ` :12.5% e:8.7% t:6.4% o:5.2% s:5.1% r:4.6% a:4.4% i:4.2% n:4.1% u:3.6%` |
| structured/census_gazetteer_places.tsv | 6498405 | 32330 | 0/200/200/200/202 | 84 | 100.00 | 0.00 | 0.00 | ` :58.5% \t:5.5% 0:3.7% 2:2.9% 1:2.6% 4:2.6% 3:2.5% 5:2.4% 7:2.2% 8:2.1%` |
| structured/govinfo_bills.xml | 41943000 | 69592 | 0/130/786/4284/7233062 | 117 | 99.78 | 0.22 | 0.00 | `e:8.3%  :7.9% t:5.7% n:5.2% a:5.2% i:5.0% r:4.4% o:4.1% s:3.6% l:3.0%` |
| structured/usgs_2024q1.csv | 2038655 | 10547 | 0/189/222/241/245 | 105 | 99.89 | 0.11 | 0.00 | `,:11.4% 0:9.2% 2:6.8% 1:6.1% .:5.2% 4:4.9% 3:4.2% 5:3.4% 6:3.1% 9:3.0%` |
| structured/usgs_2024q1.geojson | 4172801 | 5825 | 657/712/741/786/988 | 109 | 99.94 | 0.06 | 0.00 | `":13.1% e:6.3% ,:5.8% t:5.2% ::4.7% a:4.3% s:3.9% u:3.2% 0:3.0% l:2.9%` |
| structured/ne_10m_admin_0_countries.geojson | 13287234 | 1 | 0/13287233/13287233/13287233/13287233 | 173 | 99.50 | 0.50 | 0.00 | `,:8.6% .:8.3% 1:8.2% 2:6.9% 6:6.8% 5:6.7% 4:6.7% 3:6.7% 7:6.6% 8:6.1%` |
| binary/django-5.0.tar | 49960960 | 1054705 | 0/26/75/311/153673 | 256 | 93.55 | 4.97 | 1.48 | ` :13.9% \x00:13.4% e:5.5% t:4.0% s:3.9% a:3.5% o:3.0% r:3.0% i:2.9% n:2.8%` |
| binary/libpng-1.6.43.tar | 6615040 | 178809 | 0/29/72/106/11217 | 256 | 99.09 | 0.11 | 0.80 | ` :18.7% \x00:6.1% e:5.2% t:4.1% n:3.8% i:3.7% r:3.1% o:3.1% a:3.0% s:3.0%` |
| binary/libpng-1.6.43.tar.gz | 1554715 | 6068 | 0/171/584/1259/4966 | 256 | 49.94 | 6.97 | 43.09 | `\xff:0.4% 8:0.4% \x1c:0.4% \x92:0.4% \xa3:0.4% \xc3:0.4% \xbd:0.4% \x93:0.4% \x8c:0.4% \xe1:0.4%` |
| binary/python-3.12.7-docs-html.tar.bz2 | 8390435 | 38165 | 0/143/516/1101/3446 | 256 | 51.64 | 6.62 | 41.74 | `\x00:0.6% \x10:0.5%  :0.5% @:0.5% \x14:0.5% D:0.5% (:0.5% $:0.5% \x08:0.5% H:0.5%` |
| binary/BILLS-118-1-hr.zip | 47893641 | 183038 | 0/176/606/1255/3813 | 256 | 50.64 | 6.94 | 42.41 | `\x00:1.0% \x08:0.5% \xdb:0.5% 8:0.4% L:0.4% 1:0.4% m:0.4% u:0.4% h:0.4% \xea:0.4%` |

## Script mix of the nonenglish class (shape.py --scripts)

| file | non-ASCII chars | script shares of non-ASCII chars |
|---|---|---|
| nonenglish/pg1982.txt | 6017 | Kana 60%, CJK 28%, other 13%, Latin-ext 0% |
| nonenglish/pg2790.txt | 19814 | Cyrillic 99%, other 1% |
| nonenglish/pg2890.txt | 35122 | Cyrillic 100%, other 0% |
| nonenglish/pg4572.txt | 24543 | CJK 84%, other 16% |
| nonenglish/pg4573.txt | 26143 | CJK 83%, other 17% |
| nonenglish/pg4580.txt | 208112 | CJK 85%, other 15% |
| nonenglish/pg6696.txt | 9882 | Latin-ext 99%, other 1% |
| nonenglish/pg6698.txt | 15652 | Latin-ext 100%, other 0% |
| nonenglish/pg7221.txt | 114323 | CJK 84%, other 16%, Kana 0% |
| nonenglish/pg7290.txt | 64073 | CJK 79%, other 21%, Kana 0% |
| nonenglish/pg7317.txt | 101601 | CJK 81%, other 19% |
| nonenglish/pg8186.txt | 52 | other 100% |
| nonenglish/pg8453.txt | 52 | other 100% |
| nonenglish/pg9000.txt | 52 | other 100% |
| nonenglish/pg11291.txt | 174881 | Cyrillic 100%, other 0%, Latin-ext 0% |
| nonenglish/pg14741.txt | 84635 | Cyrillic 99%, other 0%, Latin-ext 0% |
| nonenglish/pg15008.txt | 89466 | Cyrillic 100%, other 0%, Latin-ext 0% |
| nonenglish/pg17814.txt | 71910 | Greek 99%, other 1%, Latin-ext 0% |
| nonenglish/pg17839.txt | 64862 | Greek 99%, other 1%, Latin-ext 0% |
| nonenglish/pg20175.txt | 181524 | Latin-ext 100%, other 0%, Greek 0% |
| nonenglish/pg26731.txt | 85541 | Greek 99%, other 1%, Latin-ext 0% |
| nonenglish/pg30774.txt | 35605 | Cyrillic 99%, Latin-ext 0%, other 0% |
| nonenglish/pg31617.txt | 180390 | Kana 54%, other 28%, CJK 17%, CJK-ExtA 0% |
| nonenglish/pg31757.txt | 52874 | Kana 62%, CJK 29%, other 9% |
| nonenglish/pg33307.txt | 67188 | Kana 65%, CJK 26%, other 9%, Latin-ext 0% |
| nonenglish/pg34013.txt | 115181 | Kana 54%, other 29%, CJK 17%, CJK-ExtA 0% |
| nonenglish/pg37196.txt | 23344 | Cyrillic 100%, other 0%, Latin-ext 0% |
| nonenglish/pg43740.txt | 98122 | Hebrew 99%, other 0%, Latin-ext 0% |
| nonenglish/pg61024.txt | 58692 | Hebrew 100%, other 0%, Latin-ext 0% |
