module soc_clk_rst_gen (
	ref_clk_i,
	test_clk_i,
	rstn_glob_i,
	test_mode_i,
	sel_fll_clk_i,
	shift_enable_i,
	soc_fll_slave_req_i,
	soc_fll_slave_wrn_i,
	soc_fll_slave_add_i,
	soc_fll_slave_data_i,
	soc_fll_slave_ack_o,
	soc_fll_slave_r_data_o,
	soc_fll_slave_lock_o,
	per_fll_slave_req_i,
	per_fll_slave_wrn_i,
	per_fll_slave_add_i,
	per_fll_slave_data_i,
	per_fll_slave_ack_o,
	per_fll_slave_r_data_o,
	per_fll_slave_lock_o,
	cluster_fll_slave_req_i,
	cluster_fll_slave_wrn_i,
	cluster_fll_slave_add_i,
	cluster_fll_slave_data_i,
	cluster_fll_slave_ack_o,
	cluster_fll_slave_r_data_o,
	cluster_fll_slave_lock_o,
	rstn_soc_sync_o,
	rstn_cluster_sync_o,
	clk_soc_o,
	clk_per_o,
	clk_cluster_o
);
	input wire ref_clk_i;
	input wire test_clk_i;
	input wire rstn_glob_i;
	input wire test_mode_i;
	input wire sel_fll_clk_i;
	input wire shift_enable_i;
	input wire soc_fll_slave_req_i;
	input wire soc_fll_slave_wrn_i;
	input wire [1:0] soc_fll_slave_add_i;
	input wire [31:0] soc_fll_slave_data_i;
	output wire soc_fll_slave_ack_o;
	output wire [31:0] soc_fll_slave_r_data_o;
	output wire soc_fll_slave_lock_o;
	input wire per_fll_slave_req_i;
	input wire per_fll_slave_wrn_i;
	input wire [1:0] per_fll_slave_add_i;
	input wire [31:0] per_fll_slave_data_i;
	output wire per_fll_slave_ack_o;
	output wire [31:0] per_fll_slave_r_data_o;
	output wire per_fll_slave_lock_o;
	input wire cluster_fll_slave_req_i;
	input wire cluster_fll_slave_wrn_i;
	input wire [1:0] cluster_fll_slave_add_i;
	input wire [31:0] cluster_fll_slave_data_i;
	output wire cluster_fll_slave_ack_o;
	output wire [31:0] cluster_fll_slave_r_data_o;
	output wire cluster_fll_slave_lock_o;
	output wire rstn_soc_sync_o;
	output wire rstn_cluster_sync_o;
	output wire clk_soc_o;
	output wire clk_per_o;
	output wire clk_cluster_o;
	wire s_clk_soc;
	wire s_clk_per;
	wire s_clk_cluster;
	wire s_clk_fll_soc;
	wire s_clk_fll_per;
	wire s_clk_fll_cluster;
	wire s_rstn_soc;
	wire s_rstn_soc_sync;
	wire s_rstn_cluster_sync;
	freq_meter #(
		.FLL_NAME("SOC_FLL"),
		.MAX_SAMPLE(4096)
	) SOC_METER(.clk(s_clk_fll_soc));
	freq_meter #(
		.FLL_NAME("PER_FLL"),
		.MAX_SAMPLE(4096)
	) PER_METER(.clk(s_clk_fll_per));
	freq_meter #(
		.FLL_NAME("CLUSTER_FLL"),
		.MAX_SAMPLE(4096)
	) CLUSTER_METER(.clk(s_clk_fll_cluster));
	gf22_FLL i_fll_soc(
		.FLLCLK(s_clk_fll_soc),
		.FLLOE(1'b1),
		.REFCLK(ref_clk_i),
		.LOCK(soc_fll_slave_lock_o),
		.CFGREQ(soc_fll_slave_req_i),
		.CFGACK(soc_fll_slave_ack_o),
		.CFGAD(soc_fll_slave_add_i[1:0]),
		.CFGD(soc_fll_slave_data_i),
		.CFGQ(soc_fll_slave_r_data_o),
		.CFGWEB(soc_fll_slave_wrn_i),
		.RSTB(rstn_glob_i),
		.PWD(1'b0),
		.RET(1'b0),
		.TM(test_mode_i),
		.TE(shift_enable_i),
		.TD(1'b0),
		.TQ(),
		.JTD(1'b0),
		.JTQ()
	);
	gf22_FLL i_fll_per(
		.FLLCLK(s_clk_fll_per),
		.FLLOE(1'b1),
		.REFCLK(ref_clk_i),
		.LOCK(per_fll_slave_lock_o),
		.CFGREQ(per_fll_slave_req_i),
		.CFGACK(per_fll_slave_ack_o),
		.CFGAD(per_fll_slave_add_i[1:0]),
		.CFGD(per_fll_slave_data_i),
		.CFGQ(per_fll_slave_r_data_o),
		.CFGWEB(per_fll_slave_wrn_i),
		.RSTB(rstn_glob_i),
		.PWD(1'b0),
		.RET(1'b0),
		.TM(test_mode_i),
		.TE(shift_enable_i),
		.TD(1'b0),
		.TQ(),
		.JTD(1'b0),
		.JTQ()
	);
	gf22_FLL i_fll_cluster(
		.FLLCLK(s_clk_fll_cluster),
		.FLLOE(1'b1),
		.REFCLK(ref_clk_i),
		.LOCK(cluster_fll_slave_lock_o),
		.CFGREQ(cluster_fll_slave_req_i),
		.CFGACK(cluster_fll_slave_ack_o),
		.CFGAD(cluster_fll_slave_add_i[1:0]),
		.CFGD(cluster_fll_slave_data_i),
		.CFGQ(cluster_fll_slave_r_data_o),
		.CFGWEB(cluster_fll_slave_wrn_i),
		.RSTB(rstn_glob_i),
		.PWD(1'b0),
		.RET(1'b0),
		.TM(test_mode_i),
		.TE(shift_enable_i),
		.TD(1'b0),
		.TQ(),
		.JTD(1'b0),
		.JTQ()
	);
	pulp_clock_mux2 clk_mux_fll_soc_i(
		.clk0_i(s_clk_fll_soc),
		.clk1_i(ref_clk_i),
		.clk_sel_i(sel_fll_clk_i),
		.clk_o(s_clk_soc)
	);
	pulp_clock_mux2 clk_mux_fll_per_i(
		.clk0_i(s_clk_fll_per),
		.clk1_i(ref_clk_i),
		.clk_sel_i(sel_fll_clk_i),
		.clk_o(s_clk_per)
	);
	pulp_clock_mux2 clk_mux_fll_cluster_i(
		.clk0_i(s_clk_fll_cluster),
		.clk1_i(ref_clk_i),
		.clk_sel_i(sel_fll_clk_i),
		.clk_o(s_clk_cluster)
	);
	assign s_rstn_soc = rstn_glob_i;
	rstgen i_soc_rstgen(
		.clk_i(clk_soc_o),
		.rst_ni(s_rstn_soc),
		.test_mode_i(test_mode_i),
		.rst_no(s_rstn_soc_sync),
		.init_no()
	);
	rstgen i_cluster_rstgen(
		.clk_i(clk_cluster_o),
		.rst_ni(s_rstn_soc),
		.test_mode_i(test_mode_i),
		.rst_no(s_rstn_cluster_sync),
		.init_no()
	);
	assign clk_soc_o = s_clk_soc;
	assign clk_per_o = s_clk_per;
	assign clk_cluster_o = s_clk_cluster;
	assign rstn_soc_sync_o = s_rstn_soc_sync;
	assign rstn_cluster_sync_o = s_rstn_cluster_sync;
endmodule
