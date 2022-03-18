module apb_gpio (
	HCLK,
	HRESETn,
	dft_cg_enable_i,
	PADDR,
	PWDATA,
	PWRITE,
	PSEL,
	PENABLE,
	PRDATA,
	PREADY,
	PSLVERR,
	gpio_in,
	gpio_in_sync,
	gpio_out,
	gpio_dir,
	gpio_padcfg,
	interrupt
);
	parameter APB_ADDR_WIDTH = 12;
	input wire HCLK;
	input wire HRESETn;
	input wire dft_cg_enable_i;
	input wire [APB_ADDR_WIDTH - 1:0] PADDR;
	input wire [31:0] PWDATA;
	input wire PWRITE;
	input wire PSEL;
	input wire PENABLE;
	output reg [31:0] PRDATA;
	output wire PREADY;
	output wire PSLVERR;
	input wire [31:0] gpio_in;
	output wire [31:0] gpio_in_sync;
	output wire [31:0] gpio_out;
	output wire [31:0] gpio_dir;
	output reg [191:0] gpio_padcfg;
	output wire interrupt;
	reg [31:0] r_gpio_inten;
	reg [31:0] r_gpio_inttype0;
	reg [31:0] s_gpio_inttype0;
	reg [31:0] r_gpio_inttype1;
	reg [31:0] s_gpio_inttype1;
	reg [31:0] r_gpio_out;
	reg [31:0] r_gpio_dir;
	reg [31:0] r_gpio_sync0;
	reg [31:0] r_gpio_sync1;
	reg [31:0] r_gpio_in;
	reg [31:0] r_gpio_en;
	reg [31:0] r_gpio_lock;
	wire [31:0] s_gpio_rise;
	wire [31:0] s_gpio_fall;
	wire [31:0] s_is_int_rise;
	wire [31:0] s_is_int_rifa;
	wire [31:0] s_is_int_fall;
	wire [31:0] s_is_int_all;
	wire s_rise_int;
	wire [4:0] s_apb_addr;
	reg [31:0] r_status;
	reg [7:0] s_clk_en;
	wire [7:0] s_clkg;
	genvar i;
	assign s_apb_addr = PADDR[6:2];
	assign gpio_in_sync = r_gpio_sync1;
	assign s_gpio_rise = r_gpio_sync1 & ~r_gpio_in;
	assign s_gpio_fall = ~r_gpio_sync1 & r_gpio_in;
	assign s_is_int_fall = (~s_gpio_inttype1 & ~s_gpio_inttype0) & s_gpio_fall;
	assign s_is_int_rise = (~s_gpio_inttype1 & s_gpio_inttype0) & s_gpio_rise;
	assign s_is_int_rifa = (s_gpio_inttype1 & ~s_gpio_inttype0) & (s_gpio_rise | s_gpio_fall);
	assign s_is_int_all = (r_gpio_inten & r_gpio_en) & ((s_is_int_rise | s_is_int_fall) | s_is_int_rifa);
	assign s_rise_int = |s_is_int_all;
	assign interrupt = s_rise_int;
	always @(*) begin : sv2v_autoblock_1
		reg signed [31:0] i;
		for (i = 0; i < 16; i = i + 1)
			begin
				s_gpio_inttype0[i] = r_gpio_inttype0[i * 2];
				s_gpio_inttype0[16 + i] = r_gpio_inttype1[i * 2];
				s_gpio_inttype1[i] = r_gpio_inttype0[(i * 2) + 1];
				s_gpio_inttype1[16 + i] = r_gpio_inttype1[(i * 2) + 1];
			end
	end
	always @(posedge HCLK or negedge HRESETn)
		if (~HRESETn)
			r_status <= 'h0;
		else if (s_rise_int)
			r_status <= r_status | s_is_int_all;
		else if (((PSEL && PENABLE) && !PWRITE) && (s_apb_addr == 5'b00110))
			r_status <= 'h0;
	generate
		for (i = 0; i < 8; i = i + 1) begin : genblk1
			pulp_clock_gating i_clk_gate(
				.clk_i(HCLK),
				.en_i(s_clk_en[i]),
				.test_en_i(dft_cg_enable_i),
				.clk_o(s_clkg[i])
			);
		end
	endgenerate
	always @(*) begin : proc_clk_en
		begin : sv2v_autoblock_2
			reg signed [31:0] i;
			for (i = 0; i < 8; i = i + 1)
				s_clk_en[i] = ((r_gpio_en[i * 4] | r_gpio_en[(i * 4) + 1]) | r_gpio_en[(i * 4) + 2]) | r_gpio_en[(i * 4) + 3];
		end
	end
	always @(posedge s_clkg[0] or negedge HRESETn)
		if (~HRESETn) begin
			r_gpio_sync0[3:0] <= 'h0;
			r_gpio_sync1[3:0] <= 'h0;
			r_gpio_in[3:0] <= 'h0;
		end
		else begin
			r_gpio_sync0[3:0] <= gpio_in[3:0];
			r_gpio_sync1[3:0] <= r_gpio_sync0[3:0];
			r_gpio_in[3:0] <= r_gpio_sync1[3:0];
		end
	always @(posedge s_clkg[1] or negedge HRESETn)
		if (~HRESETn) begin
			r_gpio_sync0[7:4] <= 'h0;
			r_gpio_sync1[7:4] <= 'h0;
			r_gpio_in[7:4] <= 'h0;
		end
		else begin
			r_gpio_sync0[7:4] <= gpio_in[7:4];
			r_gpio_sync1[7:4] <= r_gpio_sync0[7:4];
			r_gpio_in[7:4] <= r_gpio_sync1[7:4];
		end
	always @(posedge s_clkg[2] or negedge HRESETn)
		if (~HRESETn) begin
			r_gpio_sync0[11:8] <= 'h0;
			r_gpio_sync1[11:8] <= 'h0;
			r_gpio_in[11:8] <= 'h0;
		end
		else begin
			r_gpio_sync0[11:8] <= gpio_in[11:8];
			r_gpio_sync1[11:8] <= r_gpio_sync0[11:8];
			r_gpio_in[11:8] <= r_gpio_sync1[11:8];
		end
	always @(posedge s_clkg[3] or negedge HRESETn)
		if (~HRESETn) begin
			r_gpio_sync0[15:12] <= 'h0;
			r_gpio_sync1[15:12] <= 'h0;
			r_gpio_in[15:12] <= 'h0;
		end
		else begin
			r_gpio_sync0[15:12] <= gpio_in[15:12];
			r_gpio_sync1[15:12] <= r_gpio_sync0[15:12];
			r_gpio_in[15:12] <= r_gpio_sync1[15:12];
		end
	always @(posedge s_clkg[4] or negedge HRESETn)
		if (~HRESETn) begin
			r_gpio_sync0[19:16] <= 'h0;
			r_gpio_sync1[19:16] <= 'h0;
			r_gpio_in[19:16] <= 'h0;
		end
		else begin
			r_gpio_sync0[19:16] <= gpio_in[19:16];
			r_gpio_sync1[19:16] <= r_gpio_sync0[19:16];
			r_gpio_in[19:16] <= r_gpio_sync1[19:16];
		end
	always @(posedge s_clkg[5] or negedge HRESETn)
		if (~HRESETn) begin
			r_gpio_sync0[23:20] <= 'h0;
			r_gpio_sync1[23:20] <= 'h0;
			r_gpio_in[23:20] <= 'h0;
		end
		else begin
			r_gpio_sync0[23:20] <= gpio_in[23:20];
			r_gpio_sync1[23:20] <= r_gpio_sync0[23:20];
			r_gpio_in[23:20] <= r_gpio_sync1[23:20];
		end
	always @(posedge s_clkg[6] or negedge HRESETn)
		if (~HRESETn) begin
			r_gpio_sync0[27:24] <= 'h0;
			r_gpio_sync1[27:24] <= 'h0;
			r_gpio_in[27:24] <= 'h0;
		end
		else begin
			r_gpio_sync0[27:24] <= gpio_in[27:24];
			r_gpio_sync1[27:24] <= r_gpio_sync0[27:24];
			r_gpio_in[27:24] <= r_gpio_sync1[27:24];
		end
	always @(posedge s_clkg[7] or negedge HRESETn)
		if (~HRESETn) begin
			r_gpio_sync0[31:28] <= 'h0;
			r_gpio_sync1[31:28] <= 'h0;
			r_gpio_in[31:28] <= 'h0;
		end
		else begin
			r_gpio_sync0[31:28] <= gpio_in[31:28];
			r_gpio_sync1[31:28] <= r_gpio_sync0[31:28];
			r_gpio_in[31:28] <= r_gpio_sync1[31:28];
		end
	always @(posedge HCLK or negedge HRESETn)
		if (~HRESETn) begin
			r_gpio_inten <= 1'sb0;
			r_gpio_inttype0 <= 1'sb0;
			r_gpio_inttype1 <= 1'sb0;
			r_gpio_out <= 1'sb0;
			r_gpio_dir <= 1'sb0;
			r_gpio_en <= 1'sb0;
			r_gpio_lock <= 1'sb0;
			begin : sv2v_autoblock_3
				reg signed [31:0] i;
				for (i = 0; i < 32; i = i + 1)
					gpio_padcfg[i * 6+:6] <= 6'b000010;
			end
		end
		else if ((PSEL && PENABLE) && PWRITE) begin : sv2v_autoblock_4
			reg signed [31:0] pwdata_l;
			case (s_apb_addr)
				5'b00000: begin
					if (r_gpio_lock[0] == 1'b0)
						pwdata_l = PWDATA;
					else
						pwdata_l = 1'sb0;
					r_gpio_dir <= pwdata_l;
				end
				5'b00010: begin
					if (r_gpio_lock[2] == 1'b0)
						pwdata_l = PWDATA;
					else
						pwdata_l = 1'sb0;
					r_gpio_out <= pwdata_l;
				end
				5'b10000: r_gpio_out <= r_gpio_out | PWDATA;
				5'b10001: r_gpio_out <= r_gpio_out & ~PWDATA;
				5'b00011: r_gpio_inten <= PWDATA;
				5'b00100: r_gpio_inttype0 <= PWDATA;
				5'b00101: r_gpio_inttype1 <= PWDATA;
				5'b00111: r_gpio_en <= PWDATA;
				5'b10010: r_gpio_lock <= PWDATA;
				5'b01000: begin
					gpio_padcfg[0+:6] <= PWDATA[5:0];
					gpio_padcfg[6+:6] <= PWDATA[13:8];
					gpio_padcfg[12+:6] <= PWDATA[21:16];
					gpio_padcfg[18+:6] <= PWDATA[29:24];
				end
				5'b01001: begin
					gpio_padcfg[24+:6] <= PWDATA[5:0];
					gpio_padcfg[30+:6] <= PWDATA[13:8];
					gpio_padcfg[36+:6] <= PWDATA[21:16];
					gpio_padcfg[42+:6] <= PWDATA[29:24];
				end
				5'b01010: begin
					gpio_padcfg[48+:6] <= PWDATA[5:0];
					gpio_padcfg[54+:6] <= PWDATA[13:8];
					gpio_padcfg[60+:6] <= PWDATA[21:16];
					gpio_padcfg[66+:6] <= PWDATA[29:24];
				end
				5'b01011: begin
					gpio_padcfg[72+:6] <= PWDATA[5:0];
					gpio_padcfg[78+:6] <= PWDATA[13:8];
					gpio_padcfg[84+:6] <= PWDATA[21:16];
					gpio_padcfg[90+:6] <= PWDATA[29:24];
				end
				5'b01100: begin
					gpio_padcfg[96+:6] <= PWDATA[5:0];
					gpio_padcfg[102+:6] <= PWDATA[13:8];
					gpio_padcfg[108+:6] <= PWDATA[21:16];
					gpio_padcfg[114+:6] <= PWDATA[29:24];
				end
				5'b01101: begin
					gpio_padcfg[120+:6] <= PWDATA[5:0];
					gpio_padcfg[126+:6] <= PWDATA[13:8];
					gpio_padcfg[132+:6] <= PWDATA[21:16];
					gpio_padcfg[138+:6] <= PWDATA[29:24];
				end
				5'b01110: begin
					gpio_padcfg[144+:6] <= PWDATA[5:0];
					gpio_padcfg[150+:6] <= PWDATA[13:8];
					gpio_padcfg[156+:6] <= PWDATA[21:16];
					gpio_padcfg[162+:6] <= PWDATA[29:24];
				end
				5'b01111: begin
					gpio_padcfg[168+:6] <= PWDATA[5:0];
					gpio_padcfg[174+:6] <= PWDATA[13:8];
					gpio_padcfg[180+:6] <= PWDATA[21:16];
					gpio_padcfg[186+:6] <= PWDATA[29:24];
				end
			endcase
		end
	always @(*)
		case (s_apb_addr)
			5'b00000:
				if (r_gpio_lock[0] == 1'b0)
					PRDATA = r_gpio_dir;
				else
					PRDATA = 1'sb0;
			5'b00001:
				if (r_gpio_lock[1] == 1'b0)
					PRDATA = r_gpio_in;
				else
					PRDATA = 1'sb0;
			5'b00010:
				if (r_gpio_lock[2] == 1'b0)
					PRDATA = r_gpio_out;
				else
					PRDATA = 1'sb0;
			5'b00011: PRDATA = r_gpio_inten;
			5'b00100: PRDATA = r_gpio_inttype0;
			5'b00101: PRDATA = r_gpio_inttype1;
			5'b00110: PRDATA = r_status;
			5'b00111: PRDATA = r_gpio_en;
			5'b10010: PRDATA = r_gpio_lock;
			5'b01000: PRDATA = {2'b00, gpio_padcfg[18+:6], 2'b00, gpio_padcfg[12+:6], 2'b00, gpio_padcfg[6+:6], 2'b00, gpio_padcfg[0+:6]};
			5'b01001: PRDATA = {2'b00, gpio_padcfg[42+:6], 2'b00, gpio_padcfg[36+:6], 2'b00, gpio_padcfg[30+:6], 2'b00, gpio_padcfg[24+:6]};
			5'b01010: PRDATA = {2'b00, gpio_padcfg[66+:6], 2'b00, gpio_padcfg[60+:6], 2'b00, gpio_padcfg[54+:6], 2'b00, gpio_padcfg[48+:6]};
			5'b01011: PRDATA = {2'b00, gpio_padcfg[90+:6], 2'b00, gpio_padcfg[84+:6], 2'b00, gpio_padcfg[78+:6], 2'b00, gpio_padcfg[72+:6]};
			5'b01100: PRDATA = {2'b00, gpio_padcfg[114+:6], 2'b00, gpio_padcfg[108+:6], 2'b00, gpio_padcfg[102+:6], 2'b00, gpio_padcfg[96+:6]};
			5'b01101: PRDATA = {2'b00, gpio_padcfg[138+:6], 2'b00, gpio_padcfg[132+:6], 2'b00, gpio_padcfg[126+:6], 2'b00, gpio_padcfg[120+:6]};
			5'b01110: PRDATA = {2'b00, gpio_padcfg[162+:6], 2'b00, gpio_padcfg[156+:6], 2'b00, gpio_padcfg[150+:6], 2'b00, gpio_padcfg[144+:6]};
			5'b01111: PRDATA = {2'b00, gpio_padcfg[186+:6], 2'b00, gpio_padcfg[180+:6], 2'b00, gpio_padcfg[174+:6], 2'b00, gpio_padcfg[168+:6]};
			default: PRDATA = 'h0;
		endcase
	assign gpio_out = r_gpio_out;
	assign gpio_dir = r_gpio_dir;
	assign PREADY = 1'b1;
	assign PSLVERR = 1'b0;
endmodule
