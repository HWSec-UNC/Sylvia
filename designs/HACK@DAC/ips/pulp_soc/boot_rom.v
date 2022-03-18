module boot_rom (
	clk_i,
	rst_ni,
	init_ni,
	mem_slave,
	test_mode_i
);
	parameter ROM_ADDR_WIDTH = 13;
	input wire clk_i;
	input wire rst_ni;
	input wire init_ni;
	input UNICAD_MEM_BUS_32.Slave mem_slave;
	input wire test_mode_i;
	generic_rom #(
		.ADDR_WIDTH(ROM_ADDR_WIDTH - 2),
		.DATA_WIDTH(32)
	) rom_mem_i(
		.CLK(clk_i),
		.CEN(mem_slave.csn),
		.A(mem_slave.add[ROM_ADDR_WIDTH - 1:2]),
		.Q(mem_slave.rdata)
	);
endmodule
