00000000000021c0 <rx_search>:
    21c0:	endbr64
    21c4:	xor    %eax,%eax
    21c6:	cmp    %rdx,%rsi
    21c9:	jb     22a0 <rx_search+0xe0>
    21cf:	push   %rbx
    21d0:	mov    %rdi,%r8
    21d3:	mov    %rdx,%r9
    21d6:	mov    %rsi,%rdi
    21d9:	mov    %rcx,%r11
    21dc:	mov    %rdx,%r10
    21df:	mov    $0x3b9aca00,%ebx
    21e4:	nop
    21e5:	data16 cs nopw 0x0(%rax,%rax,1)
    21f0:	mov    %r9,%rsi
    21f3:	lea    0x1(%r9),%r9
    21f7:	mov    %r9,%rdx
    21fa:	cmp    %r9,%rdi
    21fd:	jae    2210 <rx_search+0x50>
    21ff:	jmp    22a8 <rx_search+0xe8>
    2204:	nopl   0x0(%rax)
    2208:	cmp    %rax,%rdi
    220b:	jb     222e <rx_search+0x6e>
    220d:	mov    %rax,%rdx
    2210:	movzbl -0x1(%r8,%rdx,1),%eax
    2216:	sub    $0x30,%eax
    2219:	cmp    $0x9,%eax
    221c:	ja     2298 <rx_search+0xd8>
    221e:	lea    0x1(%rdx),%rax
    2222:	mov    %rax,%rcx
    2225:	sub    %rsi,%rcx
    2228:	cmp    $0x11,%rcx
    222c:	jne    2208 <rx_search+0x48>
    222e:	mov    %rdx,%rax
    2231:	sub    %rsi,%rax
    2234:	mov    %rax,%rcx
    2237:	test   %rax,%rax
    223a:	jle    2260 <rx_search+0xa0>
    223c:	sub    %rax,%rbx
    223f:	js     22bf <rx_search+0xff>
    2241:	cmp    %r10,%rdx
    2244:	jle    2280 <rx_search+0xc0>
    2246:	test   %r11,%r11
    2249:	je     2255 <rx_search+0x95>
    224b:	mov    %rsi,(%r11)
    224e:	add    %rcx,%rsi
    2251:	mov    %rsi,0x8(%r11)
    2255:	mov    $0x1,%eax
    225a:	pop    %rbx
    225b:	ret
    225c:	nopl   0x0(%rax)
    2260:	cmp    %r10,%rdx
    2263:	jle    2280 <rx_search+0xc0>
    2265:	cmp    $0xfffffffffffffffe,%rax
    2269:	je     22b1 <rx_search+0xf1>
    226b:	cmp    $0xfffffffffffffffd,%rax
    226f:	je     22b8 <rx_search+0xf8>
    2271:	lea    0x6(%rax),%rdx
    2275:	cmp    $0x2,%rdx
    2279:	jbe    225a <rx_search+0x9a>
    227b:	test   %rax,%rax
    227e:	je     2246 <rx_search+0x86>
    2280:	add    $0x1,%r10
    2284:	cmp    %rdi,%rsi
    2287:	jb     21f0 <rx_search+0x30>
    228d:	xor    %eax,%eax
    228f:	pop    %rbx
    2290:	ret
    2291:	nopl   0x0(%rax)
    2298:	sub    $0x1,%rdx
    229c:	jmp    222e <rx_search+0x6e>
    229e:	xchg   %ax,%ax
    22a0:	ret
    22a1:	nopl   0x0(%rax)
    22a8:	cmp    %r10,%rsi
    22ab:	jle    2280 <rx_search+0xc0>
    22ad:	xor    %ecx,%ecx
    22af:	jmp    2246 <rx_search+0x86>
    22b1:	mov    $0xfffffffe,%eax
    22b6:	pop    %rbx
    22b7:	ret
    22b8:	mov    $0xfffffffd,%eax
    22bd:	pop    %rbx
    22be:	ret
    22bf:	mov    $0xfffffffc,%eax
    22c4:	pop    %rbx
    22c5:	ret
    22c6:	cs nopw 0x0(%rax,%rax,1)

