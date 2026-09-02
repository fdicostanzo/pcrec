0000000000002120 <rx_search>:
    2120:	push   %rbp
    2121:	push   %r15
    2123:	push   %r14
    2125:	push   %r13
    2127:	push   %r12
    2129:	push   %rbx
    212a:	sub    $0xc78,%rsp
    2131:	mov    %rcx,%r14
    2134:	lea    0x698(%rsp),%rax
    213c:	lea    0xb0(%rsp),%rcx
    2144:	mov    %rcx,0x38(%rsp)
    2149:	movq   $0x3f,0x40(%rsp)
    2152:	mov    %rax,0x48(%rsp)
    2157:	movq   $0x5e,0x50(%rsp)
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
    2182:	movdqa %xmm0,0x20(%rsp)
    2188:	movdqa %xmm0,0x10(%rsp)
    218e:	movq   $0xffffffffffffffff,0x30(%rsp)
    2197:	pxor   %xmm0,%xmm0
    219b:	movdqu %xmm0,0x58(%rsp)
    21a1:	movq   $0x1dcd6500,0x68(%rsp)
    21aa:	movq   $0x3b9aca00,0x70(%rsp)
    21b3:	mov    %rdi,0x8(%rsp)
    21b8:	mov    %rdi,0x80(%rsp)
    21c0:	mov    %rsi,0x88(%rsp)
    21c8:	movdqu %xmm0,0x98(%rsp)
    21d1:	movq   $0x0,0xa8(%rsp)
    21dd:	lea    0x80(%rsp),%rbp
    21e5:	lea    0x10(%rsp),%r12
    21ea:	mov    %rdx,(%rsp)
    21ee:	mov    %rdx,%r13
    21f1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    2200:	mov    %r13,0x90(%rsp)
    2208:	mov    %rbp,%rdi
    220b:	mov    %r12,%rsi
    220e:	mov    %r15,%rdx
    2211:	call   31a0 <rx_match_anchored>
    2216:	lea    0x6(%rax),%rcx
    221a:	cmp    $0x4,%rcx
    221e:	jbe    227a <rx_search+0x15a>
    2220:	test   %rax,%rax
    2223:	jns    22cd <rx_search+0x1ad>
    2229:	mov    0x60(%rsp),%rax
    222e:	test   %rax,%rax
    2231:	je     2263 <rx_search+0x143>
    2233:	mov    0x48(%rsp),%rcx
    2238:	nopl   0x0(%rax,%rax,1)
    2240:	dec    %rax
    2243:	mov    %rax,0x60(%rsp)
    2248:	shl    $0x4,%rax
    224c:	mov    0x8(%rcx,%rax,1),%rdx
    2251:	mov    (%rcx,%rax,1),%eax
    2254:	mov    %rdx,0x10(%rsp,%rax,8)
    2259:	mov    0x60(%rsp),%rax
    225e:	test   %rax,%rax
    2261:	jne    2240 <rx_search+0x120>
    2263:	movq   $0x0,0x58(%rsp)
    226c:	cmp    %r15,%r13
    226f:	je     2167 <rx_search+0x47>
    2275:	inc    %r13
    2278:	jmp    2200 <rx_search+0xe0>
    227a:	lea    0x1d7f(%rip),%rax        # 4000 <_fini+0x404>
    2281:	movslq (%rax,%rcx,4),%rcx
    2285:	add    %rax,%rcx
    2288:	jmp    *%rcx
    228a:	mov    $0xfffffffa,%ebx
    228f:	jmp    2167 <rx_search+0x47>
    2294:	mov    $0xfffffffe,%ebx
    2299:	jmp    2167 <rx_search+0x47>
    229e:	mov    $0xfffffffc,%ebx
    22a3:	jmp    2167 <rx_search+0x47>
    22a8:	mov    0x8(%rsp),%rdi
    22ad:	mov    %r15,%rsi
    22b0:	mov    (%rsp),%rdx
    22b4:	mov    %r14,%rcx
    22b7:	call   22f0 <rx_search_deep>
    22bc:	mov    %eax,%ebx
    22be:	jmp    2167 <rx_search+0x47>
    22c3:	mov    $0xfffffffb,%ebx
    22c8:	jmp    2167 <rx_search+0x47>
    22cd:	mov    $0x1,%ebx
    22d2:	test   %r14,%r14
    22d5:	je     2167 <rx_search+0x47>
    22db:	mov    %r13,(%r14)
    22de:	add    %r13,%rax
    22e1:	mov    %rax,0x8(%r14)
    22e5:	jmp    2167 <rx_search+0x47>
    22ea:	nopw   0x0(%rax,%rax,1)

