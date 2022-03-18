module lint_jtag_wrap (
	tck_i,
	tdi_i,
	trstn_i,
	tdo_o,
	shift_dr_i,
	pause_dr_i,
	update_dr_i,
	capture_dr_i,
	lint_select_i,
	clk_i,
	rst_ni,
	jtag_lint_master
);
	parameter ADDRESS_WIDTH = 32;
	parameter DATA_WIDTH = 32;
	input wire tck_i;
	input wire tdi_i;
	input wire trstn_i;
	output wire tdo_o;
	input wire shift_dr_i;
	input wire pause_dr_i;
	input wire update_dr_i;
	input wire capture_dr_i;
	input wire lint_select_i;
	input wire clk_i;
	input wire rst_ni;
	input XBAR_TCDM_BUS.Master jtag_lint_master;
	adbg_lintonly_top #(
		.ADDR_WIDTH(ADDRESS_WIDTH),
		.DATA_WIDTH(DATA_WIDTH)
	) dbg_module_i(
		.tck_i(tck_i),
		.tdi_i(tdi_i),
		.tdo_o(tdo_o),
		.trstn_i(trstn_i),
		.shift_dr_i(shift_dr_i),
		.pause_dr_i(pause_dr_i),
		.update_dr_i(update_dr_i),
		.capture_dr_i(capture_dr_i),
		.debug_select_i(lint_select_i),
		.clk_i(clk_i),
		.rstn_i(rst_ni),
		.lint_req_o(jtag_lint_master.req),
		.lint_add_o(jtag_lint_master.add),
		.lint_wen_o(jtag_lint_master.wen),
		.lint_wdata_o(jtag_lint_master.wdata),
		.lint_be_o(jtag_lint_master.be),
		.lint_aux_o(),
		.lint_gnt_i(jtag_lint_master.gnt),
		.lint_r_aux_i(),
		.lint_r_valid_i(jtag_lint_master.r_valid),
		.lint_r_rdata_i(jtag_lint_master.r_rdata),
		.lint_r_opc_i(jtag_lint_master.r_opc)
	);
endmodule
