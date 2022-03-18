module apb_node (
	penable_i,
	pwrite_i,
	paddr_i,
	pwdata_i,
	prdata_o,
	pready_o,
	pslverr_o,
	penable_o,
	pwrite_o,
	paddr_o,
	psel_o,
	pwdata_o,
	prdata_i,
	pready_i,
	pslverr_i,
	START_ADDR_i,
	END_ADDR_i
);
	parameter NB_MASTER = 8;
	parameter APB_DATA_WIDTH = 32;
	parameter APB_ADDR_WIDTH = 32;
	input wire penable_i;
	input wire pwrite_i;
	input wire [31:0] paddr_i;
	input wire [31:0] pwdata_i;
	output reg [31:0] prdata_o;
	output reg pready_o;
	output reg pslverr_o;
	output reg [NB_MASTER - 1:0] penable_o;
	output reg [NB_MASTER - 1:0] pwrite_o;
	output reg [(NB_MASTER * 32) - 1:0] paddr_o;
	output wire [NB_MASTER - 1:0] psel_o;
	output reg [(NB_MASTER * 32) - 1:0] pwdata_o;
	input wire [(NB_MASTER * 32) - 1:0] prdata_i;
	input wire [NB_MASTER - 1:0] pready_i;
	input wire [NB_MASTER - 1:0] pslverr_i;
	input wire [(NB_MASTER * APB_ADDR_WIDTH) - 1:0] START_ADDR_i;
	input wire [(NB_MASTER * APB_ADDR_WIDTH) - 1:0] END_ADDR_i;
	genvar i;
	integer s_loop1;
	integer s_loop2;
	integer s_loop3;
	integer s_loop4;
	integer s_loop5;
	integer s_loop6;
	integer s_loop7;
	generate
		for (i = 0; i < NB_MASTER; i = i + 1) begin : genblk1
			assign psel_o[i] = (paddr_i >= START_ADDR_i[i * APB_ADDR_WIDTH+:APB_ADDR_WIDTH]) && (paddr_i <= END_ADDR_i[i * APB_ADDR_WIDTH+:APB_ADDR_WIDTH]);
		end
	endgenerate
	always @(*)
		for (s_loop1 = 0; s_loop1 < NB_MASTER; s_loop1 = s_loop1 + 1)
			if (psel_o[s_loop1] == 1'b1)
				penable_o[s_loop1] = penable_i;
			else
				penable_o[s_loop1] = 1'sb0;
	always @(*)
		for (s_loop2 = 0; s_loop2 < NB_MASTER; s_loop2 = s_loop2 + 1)
			if (psel_o[s_loop2] == 1'b1)
				pwrite_o[s_loop2] = pwrite_i;
			else
				pwrite_o[s_loop2] = 1'sb0;
	always @(*)
		for (s_loop3 = 0; s_loop3 < NB_MASTER; s_loop3 = s_loop3 + 1)
			if (psel_o[s_loop3] == 1'b1)
				paddr_o[s_loop3 * 32+:32] = paddr_i;
			else
				paddr_o[s_loop3 * 32+:32] = 1'sb0;
	always @(*)
		for (s_loop4 = 0; s_loop4 < NB_MASTER; s_loop4 = s_loop4 + 1)
			if (psel_o[s_loop4] == 1'b1)
				pwdata_o[s_loop4 * 32+:32] = pwdata_i;
			else
				pwdata_o[s_loop4 * 32+:32] = 1'sb0;
	always @(*) begin
		prdata_o = 1'sb0;
		for (s_loop5 = 0; s_loop5 < NB_MASTER; s_loop5 = s_loop5 + 1)
			if (psel_o[s_loop5] == 1'b1)
				prdata_o = prdata_i[s_loop5 * 32+:32];
	end
	always @(*) begin
		pready_o = 1'sb0;
		for (s_loop6 = 0; s_loop6 < NB_MASTER; s_loop6 = s_loop6 + 1)
			if (psel_o[s_loop6] == 1'b1)
				pready_o = pready_i[s_loop6];
	end
	always @(*) begin
		pslverr_o = 1'sb0;
		for (s_loop7 = 0; s_loop7 < NB_MASTER; s_loop7 = s_loop7 + 1)
			if (psel_o[s_loop7] == 1'b1)
				pslverr_o = pslverr_i[s_loop7];
	end
endmodule
