0000000000002120 <rx_search>:
    2120:	push   %rbp
    2121:	push   %r15
    2123:	push   %r14
    2125:	push   %r13
    2127:	push   %r12
    2129:	push   %rbx
    212a:	sub    $0xc78,%rsp
    2131:	mov    %rcx,%r14
    2134:	lea    0x788(%rsp),%rax
    213c:	lea    0xc8(%rsp),%rcx
    2144:	mov    %rcx,0x58(%rsp)
    2149:	movq   $0x48,0x60(%rsp)
    2152:	mov    %rax,0x68(%rsp)
    2157:	movq   $0x4f,0x70(%rsp)
    2160:	xor    %ebx,%ebx
    2162:	cmp    %rsi,%rdx
    2165:	jbe    217b <rx_search+0x5b>
    2167:	mov    %ebx,%eax
    2169:	add    $0xc78,%rsp
    2170:	pop    %rbx
    2171:	pop    %r12
    2173:	pop    %r13
    2175:	pop    %r14
    2177:	pop    %r15
    2179:	pop    %rbp
    217a:	ret
    217b:	mov    %rsi,%r15
    217e:	pcmpeqd %xmm0,%xmm0
    2182:	movdqa %xmm0,0x40(%rsp)
    2188:	movdqa %xmm0,0x30(%rsp)
    218e:	movdqa %xmm0,0x20(%rsp)
    2194:	movdqa %xmm0,0x10(%rsp)
    219a:	movq   $0xffffffffffffffff,0x50(%rsp)
    21a3:	pxor   %xmm0,%xmm0
    21a7:	movdqu %xmm0,0x78(%rsp)
    21ad:	movq   $0x1dcd6500,0x88(%rsp)
    21b9:	movq   $0x3b9aca00,0x90(%rsp)
    21c5:	mov    %rdi,0x8(%rsp)
    21ca:	mov    %rdi,0x98(%rsp)
    21d2:	mov    %rsi,0xa0(%rsp)
    21da:	movdqu %xmm0,0xb0(%rsp)
    21e3:	movq   $0x0,0xc0(%rsp)
    21ef:	lea    0x98(%rsp),%rbp
    21f7:	lea    0x10(%rsp),%r12
    21fc:	mov    %rdx,(%rsp)
    2200:	mov    %rdx,%r13
    2203:	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    2210:	mov    %r13,0xa8(%rsp)
    2218:	mov    %rbp,%rdi
    221b:	mov    %r12,%rsi
    221e:	mov    %r15,%rdx
    2221:	call   32d0 <rx_match_anchored>
    2226:	lea    0x6(%rax),%rcx
    222a:	cmp    $0x4,%rcx
    222e:	jbe    2290 <rx_search+0x170>
    2230:	test   %rax,%rax
    2233:	jns    22e3 <rx_search+0x1c3>
    2239:	mov    0x80(%rsp),%rax
    2241:	test   %rax,%rax
    2244:	je     2279 <rx_search+0x159>
    2246:	mov    0x68(%rsp),%rcx
    224b:	nopl   0x0(%rax,%rax,1)
    2250:	dec    %rax
    2253:	mov    %rax,0x80(%rsp)
    225b:	shl    $0x4,%rax
    225f:	mov    0x8(%rcx,%rax,1),%rdx
    2264:	mov    (%rcx,%rax,1),%eax
    2267:	mov    %rdx,0x10(%rsp,%rax,8)
    226c:	mov    0x80(%rsp),%rax
    2274:	test   %rax,%rax
    2277:	jne    2250 <rx_search+0x130>
    2279:	movq   $0x0,0x78(%rsp)
    2282:	cmp    %r15,%r13
    2285:	je     2167 <rx_search+0x47>
    228b:	inc    %r13
    228e:	jmp    2210 <rx_search+0xf0>
    2290:	lea    0x1d69(%rip),%rax        # 4000 <_fini+0x4b8>
    2297:	movslq (%rax,%rcx,4),%rcx
    229b:	add    %rax,%rcx
    229e:	jmp    *%rcx
    22a0:	mov    $0xfffffffa,%ebx
    22a5:	jmp    2167 <rx_search+0x47>
    22aa:	mov    $0xfffffffe,%ebx
    22af:	jmp    2167 <rx_search+0x47>
    22b4:	mov    $0xfffffffc,%ebx
    22b9:	jmp    2167 <rx_search+0x47>
    22be:	mov    0x8(%rsp),%rdi
    22c3:	mov    %r15,%rsi
    22c6:	mov    (%rsp),%rdx
    22ca:	mov    %r14,%rcx
    22cd:	call   2300 <rx_search_deep>
    22d2:	mov    %eax,%ebx
    22d4:	jmp    2167 <rx_search+0x47>
    22d9:	mov    $0xfffffffb,%ebx
    22de:	jmp    2167 <rx_search+0x47>
    22e3:	mov    $0x1,%ebx
    22e8:	test   %r14,%r14
    22eb:	je     2167 <rx_search+0x47>
    22f1:	mov    %r13,(%r14)
    22f4:	add    %r13,%rax
    22f7:	mov    %rax,0x8(%r14)
    22fb:	jmp    2167 <rx_search+0x47>

