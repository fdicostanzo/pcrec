00000000000021c0 <rx_prefilter>:
    21c0:	mov    %rdx,%r9
    21c3:	xor    %edx,%edx
    21c5:	cmp    %r9,%rsi
    21c8:	jb     2430 <rx_prefilter+0x270>
    21ce:	push   %r14
    21d0:	mov    %rcx,%r10
    21d3:	xor    %ecx,%ecx
    21d5:	push   %r13
    21d7:	push   %r12
    21d9:	push   %rbp
    21da:	push   %rbx
    21db:	test   %r9,%r9
    21de:	jne    2408 <rx_prefilter+0x248>
    21e4:	mov    %r9,%rax
    21e7:	mov    $0xffffffffffffffff,%r8
    21ee:	lea    0x49ab(%rip),%rbx        # 6ba0 <rx_forward_stay14.9>
    21f5:	lea    0x4aa4(%rip),%r11        # 6ca0 <rx_can_begin_match.10>
    21fc:	lea    0x4bdd(%rip),%r13        # 6de0 <rx_forward_byte_class.12>
    2203:	lea    0x3f96(%rip),%r12        # 61a0 <rx_forward_is_accepting_by_class.7>
    220a:	lea    0x358f(%rip),%rbp        # 57a0 <rx_forward_next_state.6>
    2211:	jmp    2251 <rx_prefilter+0x91>
    2213:	nopl   0x0(%rax,%rax,1)
    2218:	cmp    $0x196,%ecx
    221e:	je     23ef <rx_prefilter+0x22f>
    2224:	cmp    %rsi,%rax
    2227:	jae    22a0 <rx_prefilter+0xe0>
    2229:	movzbl (%rdi,%rax,1),%edx
    222d:	movzbl 0x0(%r13,%rdx,1),%edx
    2233:	add    %ecx,%edx
    2235:	mov    %edx,%edx
    2237:	movzwl 0x0(%rbp,%rdx,2),%ecx
    223c:	cmpb   $0x0,(%r12,%rdx,1)
    2241:	cmovne %rax,%r8
    2245:	add    $0x1,%rax
    2249:	cmp    $0xffff,%ecx
    224f:	je     22b1 <rx_prefilter+0xf1>
    2251:	test   %ecx,%ecx
    2253:	jne    2218 <rx_prefilter+0x58>
    2255:	cmp    $0xffffffffffffffff,%r8
    2259:	jne    2218 <rx_prefilter+0x58>
    225b:	mov    %rax,%r14
    225e:	add    $0x1,%rax
    2262:	cmp    %rsi,%rax
    2265:	jae    2298 <rx_prefilter+0xd8>
    2267:	nopl   (%rax)
    226a:	data16 cs nopw 0x0(%rax,%rax,1)
    2275:	data16 cs nopw 0x0(%rax,%rax,1)
    2280:	movzbl -0x1(%rdi,%rax,1),%edx
    2285:	cmpb   $0x0,(%r11,%rdx,1)
    228a:	jne    2298 <rx_prefilter+0xd8>
    228c:	mov    %rax,%r14
    228f:	add    $0x1,%rax
    2293:	cmp    %rsi,%rax
    2296:	jb     2280 <rx_prefilter+0xc0>
    2298:	mov    %r14,%rax
    229b:	cmp    %rsi,%rax
    229e:	jb     2229 <rx_prefilter+0x69>
    22a0:	lea    0x43f9(%rip),%rdx        # 66a0 <rx_forward_is_accepting.8>
    22a7:	cmpb   $0x0,(%rdx,%rcx,1)
    22ab:	jne    2438 <rx_prefilter+0x278>
    22b1:	xor    %edx,%edx
    22b3:	cmp    $0xffffffffffffffff,%r8
    22b7:	je     23b8 <rx_prefilter+0x1f8>
    22bd:	xor    %r11d,%r11d
    22c0:	cmp    %rsi,%r8
    22c3:	jae    22e1 <rx_prefilter+0x121>
    22c5:	movzbl (%rdi,%r8,1),%eax
    22ca:	lea    0x33cf(%rip),%rdx        # 56a0 <rx_reverse_byte_class.5>
    22d1:	movzbl (%rdx,%rax,1),%edx
    22d5:	lea    0x4ac4(%rip),%rax        # 6da0 <rx_forward_seed_state.11>
    22dc:	movzwl (%rax,%rdx,2),%r11d
    22e1:	mov    %r8,%rax
    22e4:	mov    $0xffffffffffffffff,%rbx
    22eb:	lea    0x33ae(%rip),%r13        # 56a0 <rx_reverse_byte_class.5>
    22f2:	lea    0x2da7(%rip),%r12        # 50a0 <rx_reverse_is_accepting_by_class.2>
    22f9:	lea    0x1ea0(%rip),%rbp        # 41a0 <rx_reverse_next_state.0>
    2300:	jmp    233f <rx_prefilter+0x17f>
    2302:	nopw   0x0(%rax,%rax,1)
    2308:	cmp    %rax,%r9
    230b:	jae    244f <rx_prefilter+0x28f>
    2311:	lea    -0x1(%rax),%rcx
    2315:	movzbl (%rdi,%rcx,1),%edx
    2319:	movzbl 0x0(%r13,%rdx,1),%edx
    231f:	add    %r11d,%edx
    2322:	mov    %edx,%edx
    2324:	movzwl 0x0(%rbp,%rdx,2),%r11d
    232a:	cmpb   $0x0,(%r12,%rdx,1)
    232f:	cmovne %rax,%rbx
    2333:	cmp    $0xffff,%r11d
    233a:	je     23a4 <rx_prefilter+0x1e4>
    233c:	mov    %rcx,%rax
    233f:	cmp    $0x2f2,%r11d
    2346:	jne    2308 <rx_prefilter+0x148>
    2348:	lea    0x1(%rax),%rdx
    234c:	lea    0x324d(%rip),%r14        # 55a0 <rx_reverse_stay26.3>
    2353:	cmp    %rsi,%rdx
    2356:	jae    2308 <rx_prefilter+0x148>
    2358:	jmp    2373 <rx_prefilter+0x1b3>
    235a:	nopw   0x0(%rax,%rax,1)
    2360:	movzbl -0x1(%rdi,%rax,1),%edx
    2365:	lea    -0x1(%rax),%rcx
    2369:	cmpb   $0x0,(%r14,%rdx,1)
    236e:	je     2315 <rx_prefilter+0x155>
    2370:	mov    %rcx,%rax
    2373:	cmp    %rax,%r9
    2376:	jb     2360 <rx_prefilter+0x1a0>
    2378:	test   %r9,%r9
    237b:	je     23a4 <rx_prefilter+0x1e4>
    237d:	movzbl -0x1(%rdi,%r9,1),%edx
    2383:	lea    0x3316(%rip),%rcx        # 56a0 <rx_reverse_byte_class.5>
    238a:	movzbl (%rcx,%rdx,1),%edx
    238e:	lea    0x2d0b(%rip),%rcx        # 50a0 <rx_reverse_is_accepting_by_class.2>
    2395:	add    %r11d,%edx
    2398:	mov    %edx,%edx
    239a:	cmpb   $0x0,(%rcx,%rdx,1)
    239e:	jne    246a <rx_prefilter+0x2aa>
    23a4:	xor    %edx,%edx
    23a6:	cmp    $0xffffffffffffffff,%rbx
    23aa:	je     23b8 <rx_prefilter+0x1f8>
    23ac:	mov    %rbx,(%r10)
    23af:	mov    $0x1,%edx
    23b4:	mov    %r8,0x8(%r10)
    23b8:	pop    %rbx
    23b9:	mov    %edx,%eax
    23bb:	pop    %rbp
    23bc:	pop    %r12
    23be:	pop    %r13
    23c0:	pop    %r14
    23c2:	ret
    23c3:	nopl   0x0(%rax)
    23ca:	data16 cs nopw 0x0(%rax,%rax,1)
    23d5:	data16 cs nopw 0x0(%rax,%rax,1)
    23e0:	movzbl -0x1(%rdi,%rax,1),%edx
    23e5:	cmpb   $0x0,(%rbx,%rdx,1)
    23e9:	je     2298 <rx_prefilter+0xd8>
    23ef:	mov    %rax,%r14
    23f2:	add    $0x1,%rax
    23f6:	cmp    %rsi,%rax
    23f9:	jb     23e0 <rx_prefilter+0x220>
    23fb:	mov    %r14,%rax
    23fe:	jmp    229b <rx_prefilter+0xdb>
    2403:	nopl   0x0(%rax,%rax,1)
    2408:	movzbl -0x1(%rdi,%r9,1),%eax
    240e:	lea    0x49cb(%rip),%rdx        # 6de0 <rx_forward_byte_class.12>
    2415:	movzbl (%rdx,%rax,1),%edx
    2419:	lea    0x4980(%rip),%rax        # 6da0 <rx_forward_seed_state.11>
    2420:	movzwl (%rax,%rdx,2),%ecx
    2424:	jmp    21e4 <rx_prefilter+0x24>
    2429:	nopl   0x0(%rax)
    2430:	mov    %edx,%eax
    2432:	ret
    2433:	nopl   0x0(%rax,%rax,1)
    2438:	xor    %edx,%edx
    243a:	cmp    $0xffffffffffffffff,%rax
    243e:	je     23b8 <rx_prefilter+0x1f8>
    2444:	mov    %rax,%r8
    2447:	xor    %r11d,%r11d
    244a:	jmp    22e1 <rx_prefilter+0x121>
    244f:	test   %r9,%r9
    2452:	jne    237d <rx_prefilter+0x1bd>
    2458:	lea    0x2741(%rip),%rdx        # 4ba0 <rx_reverse_is_accepting.1>
    245f:	cmpb   $0x0,(%rdx,%r11,1)
    2464:	je     23a4 <rx_prefilter+0x1e4>
    246a:	mov    %rax,%rbx
    246d:	jmp    23ac <rx_prefilter+0x1ec>
    2472:	nopl   (%rax)
    2475:	data16 cs nopw 0x0(%rax,%rax,1)

