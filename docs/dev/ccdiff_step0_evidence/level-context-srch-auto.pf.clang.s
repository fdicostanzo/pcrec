0000000000002cb0 <rx_prefilter>:
    2cb0:	cmp    %rsi,%rdx
    2cb3:	jbe    2cb8 <rx_prefilter+0x8>
    2cb5:	xor    %eax,%eax
    2cb7:	ret
    2cb8:	push   %rbp
    2cb9:	push   %r15
    2cbb:	push   %r14
    2cbd:	push   %r13
    2cbf:	push   %r12
    2cc1:	push   %rbx
    2cc2:	test   %rdx,%rdx
    2cc5:	je     2ce6 <rx_prefilter+0x36>
    2cc7:	movzbl -0x1(%rdi,%rdx,1),%eax
    2ccc:	lea    0x299d(%rip),%r8        # 5670 <rx_prefilter.rx_reverse_byte_class>
    2cd3:	movzbl (%rax,%r8,1),%eax
    2cd8:	lea    0x3e91(%rip),%r8        # 6b70 <rx_prefilter.rx_reverse_seed_state>
    2cdf:	movzwl (%r8,%rax,2),%ebp
    2ce4:	jmp    2ce8 <rx_prefilter+0x38>
    2ce6:	xor    %ebp,%ebp
    2ce8:	mov    $0xffffffffffffffff,%rax
    2cef:	lea    0x287a(%rip),%r10        # 5570 <rx_prefilter.rx_can_begin_match>
    2cf6:	lea    0x2973(%rip),%r8        # 5670 <rx_prefilter.rx_reverse_byte_class>
    2cfd:	lea    0x236c(%rip),%r11        # 5070 <rx_prefilter.rx_forward_is_accepting_by_class>
    2d04:	lea    0x1465(%rip),%rbx        # 4170 <rx_prefilter.rx_forward_next_state>
    2d0b:	lea    0x3e9e(%rip),%r9        # 6bb0 <rx_prefilter.rx_reverse_stay26>
    2d12:	mov    %rdx,%r14
    2d15:	data16 cs nopw 0x0(%rax,%rax,1)
    2d20:	movzwl %bp,%r15d
    2d24:	test   %r15w,%r15w
    2d28:	jne    2d70 <rx_prefilter+0xc0>
    2d2a:	cmp    $0xffffffffffffffff,%rax
    2d2e:	jne    2d70 <rx_prefilter+0xc0>
    2d30:	mov    %r14,%r12
    2d33:	inc    %r12
    2d36:	cmp    %r12,%rsi
    2d39:	mov    %r12,%r14
    2d3c:	cmova  %rsi,%r14
    2d40:	dec    %r14
    2d43:	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    2d50:	cmp    %rsi,%r12
    2d53:	jae    2dad <rx_prefilter+0xfd>
    2d55:	movzbl -0x1(%rdi,%r12,1),%r13d
    2d5b:	inc    %r12
    2d5e:	cmpb   $0x0,0x0(%r13,%r10,1)
    2d64:	je     2d50 <rx_prefilter+0xa0>
    2d66:	jmp    2da6 <rx_prefilter+0xf6>
    2d68:	nopl   0x0(%rax,%rax,1)
    2d70:	cmp    $0x196,%r15d
    2d77:	jne    2dad <rx_prefilter+0xfd>
    2d79:	mov    %r14,%r12
    2d7c:	inc    %r12
    2d7f:	cmp    %r12,%rsi
    2d82:	mov    %r12,%r14
    2d85:	cmova  %rsi,%r14
    2d89:	dec    %r14
    2d8c:	nopl   0x0(%rax)
    2d90:	cmp    %rsi,%r12
    2d93:	jae    2dad <rx_prefilter+0xfd>
    2d95:	movzbl -0x1(%rdi,%r12,1),%r13d
    2d9b:	inc    %r12
    2d9e:	cmpb   $0x0,0x0(%r13,%r9,1)
    2da4:	jne    2d90 <rx_prefilter+0xe0>
    2da6:	add    $0xfffffffffffffffe,%r12
    2daa:	mov    %r12,%r14
    2dad:	cmp    %rsi,%r14
    2db0:	jae    2de5 <rx_prefilter+0x135>
    2db2:	movzbl (%rdi,%r14,1),%r12d
    2db7:	movzbl (%r12,%r8,1),%r12d
    2dbc:	add    %r15,%r12
    2dbf:	cmpb   $0x0,(%r11,%r12,1)
    2dc4:	cmovne %r14,%rax
    2dc8:	movzwl (%rbx,%r12,2),%ebp
    2dcd:	inc    %r14
    2dd0:	cmp    $0xffff,%bp
    2dd4:	jne    2d20 <rx_prefilter+0x70>
    2dda:	cmp    $0xffffffffffffffff,%rax
    2dde:	jne    2dff <rx_prefilter+0x14f>
    2de0:	jmp    2ed5 <rx_prefilter+0x225>
    2de5:	lea    0x1d84(%rip),%r10        # 4b70 <rx_prefilter.rx_forward_is_accepting>
    2dec:	cmpb   $0x0,(%r15,%r10,1)
    2df1:	cmovne %r14,%rax
    2df5:	cmp    $0xffffffffffffffff,%rax
    2df9:	je     2ed5 <rx_prefilter+0x225>
    2dff:	xor    %ebx,%ebx
    2e01:	cmp    %rsi,%rax
    2e04:	jae    2e1c <rx_prefilter+0x16c>
    2e06:	movzbl (%rdi,%rax,1),%r10d
    2e0b:	movzbl (%r10,%r8,1),%r10d
    2e10:	lea    0x3d59(%rip),%r11        # 6b70 <rx_prefilter.rx_reverse_seed_state>
    2e17:	movzwl (%r11,%r10,2),%ebx
    2e1c:	mov    $0xffffffffffffffff,%r10
    2e23:	lea    0x3846(%rip),%r14        # 6670 <rx_prefilter.rx_reverse_is_accepting_by_class>
    2e2a:	lea    0x293f(%rip),%r15        # 5770 <rx_prefilter.rx_reverse_next_state>
    2e31:	mov    %rax,%r11
    2e34:	cmp    $0x2f2,%ebx
    2e3a:	jne    2e70 <rx_prefilter+0x1c0>
    2e3c:	lea    0x1(%r11),%r12
    2e40:	cmp    %rsi,%r12
    2e43:	jae    2e70 <rx_prefilter+0x1c0>
    2e45:	cmp    %rdx,%r11
    2e48:	jbe    2e70 <rx_prefilter+0x1c0>
    2e4a:	nopw   0x0(%rax,%rax,1)
    2e50:	movzbl -0x1(%rdi,%r11,1),%r12d
    2e56:	cmpb   $0x0,(%r12,%r9,1)
    2e5b:	je     2e70 <rx_prefilter+0x1c0>
    2e5d:	dec    %r11
    2e60:	cmp    %rdx,%r11
    2e63:	ja     2e50 <rx_prefilter+0x1a0>
    2e65:	jmp    2ea0 <rx_prefilter+0x1f0>
    2e67:	nopw   0x0(%rax,%rax,1)
    2e70:	cmp    %rdx,%r11
    2e73:	jbe    2ea3 <rx_prefilter+0x1f3>
    2e75:	movzbl -0x1(%rdi,%r11,1),%r12d
    2e7b:	movzbl (%r12,%r8,1),%r12d
    2e80:	mov    %ebx,%ebx
    2e82:	add    %r12,%rbx
    2e85:	cmpb   $0x0,(%r14,%rbx,1)
    2e8a:	cmovne %r11,%r10
    2e8e:	movzwl (%r15,%rbx,2),%ebx
    2e93:	dec    %r11
    2e96:	cmp    $0xffff,%ebx
    2e9c:	jne    2e34 <rx_prefilter+0x184>
    2e9e:	jmp    2ec1 <rx_prefilter+0x211>
    2ea0:	mov    %rdx,%r11
    2ea3:	test   %rdx,%rdx
    2ea6:	je     2ee2 <rx_prefilter+0x232>
    2ea8:	movzbl -0x1(%rdi,%rdx,1),%edx
    2ead:	movzbl (%rdx,%r8,1),%edx
    2eb2:	mov    %ebx,%esi
    2eb4:	add    %rdx,%rsi
    2eb7:	cmpb   $0x0,(%r14,%rsi,1)
    2ebc:	je     2ec1 <rx_prefilter+0x211>
    2ebe:	mov    %r11,%r10
    2ec1:	cmp    $0xffffffffffffffff,%r10
    2ec5:	je     2ed5 <rx_prefilter+0x225>
    2ec7:	mov    %r10,(%rcx)
    2eca:	mov    %rax,0x8(%rcx)
    2ece:	mov    $0x1,%eax
    2ed3:	jmp    2ed7 <rx_prefilter+0x227>
    2ed5:	xor    %eax,%eax
    2ed7:	pop    %rbx
    2ed8:	pop    %r12
    2eda:	pop    %r13
    2edc:	pop    %r14
    2ede:	pop    %r15
    2ee0:	pop    %rbp
    2ee1:	ret
    2ee2:	mov    %ebx,%edx
    2ee4:	lea    0x3285(%rip),%rsi        # 6170 <rx_prefilter.rx_reverse_is_accepting>
    2eeb:	cmpb   $0x0,(%rdx,%rsi,1)
    2eef:	jne    2ebe <rx_prefilter+0x20e>
    2ef1:	jmp    2ec1 <rx_prefilter+0x211>
    2ef3:	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)

