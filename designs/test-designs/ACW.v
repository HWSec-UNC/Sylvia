`timescale 1 ns / 1 ps

	module AXI_mem_control #
	(

// ------------------- CONFIGURATION AXI S INTERFACE PARAMETERS ------------------------------

	    parameter integer C_S_CTRL_AXI	= 32,
		parameter integer C_S_CTRL_AXI_ADDR_WIDTH	= 8,
		parameter integer LOG_MAX_OUTS_TRAN     = 4,
		parameter integer MAX_OUTS_TRANS        = 16,

// ------------------- END CONFIGURATION AXI S INTERFACE PARAMETERS ---------------------------


// ------------------- AXI M INTERFACE PARAMETERS  -----------------------------------

		parameter integer C_LOG_BUS_SIZE_BYTE     = 2,
		parameter integer C_M_TARGET_SLAVE_BASE_ADDR = 32'h40000000,
		parameter integer C_M_AXI_BURST_LEN	= 16,
		parameter integer C_M_AXI_ID_WIDTH	= 1,
		parameter integer C_M_AXI_ADDR_WIDTH	= 32,
		parameter integer C_M_AXI_DATA_WIDTH	= 32,
		parameter integer C_M_AXI_ARUSER_WIDTH	= 0,
		parameter integer C_M_AXI_AWUSER_WIDTH	= 0,
		parameter integer C_M_AXI_WUSER_WIDTH	= 0,
		parameter integer C_M_AXI_RUSER_WIDTH	= 0,
		parameter integer C_M_AXI_BUSER_WIDTH	= 0

// ------------------- END AXI M INTERFACE PARAMETERS  -----------------------------------
	)

	(

// ----------------------- GLOBAL PORTS ------------------------------------------

		input wire  ACLK,
		input wire  ARESETN,
		output wire INTR_LINE_R,
		output wire INTR_LINE_W,
		// other opional lines..
// ---------------------- END GLOBAL PORTS --------------------------------------



// ---------------------- WRAPPED MODULE PORTS ---------------------------------

// Additional ports for the configuration of the wrapped module


//---------------------- END WRAPPED MODULE PORTS -----------------------------------


// -------------------- AXI CONFIGURATION S PORTS ------------------------


		input wire [C_S_CTRL_AXI_ADDR_WIDTH-1 : 0] S_AXI_CTRL_AWADDR,
		input wire [2 : 0] S_AXI_CTRL_AWPROT,
		input wire  S_AXI_CTRL_AWVALID,
		output wire  S_AXI_CTRL_AWREADY,

		input wire [C_S_CTRL_AXI-1 : 0] S_AXI_CTRL_WDATA,
		input wire [(C_S_CTRL_AXI/8)-1 : 0] S_AXI_CTRL_WSTRB,
		input wire  S_AXI_CTRL_WVALID,
		output wire  S_AXI_CTRL_WREADY,

		output wire [1 : 0] S_AXI_CTRL_BRESP,
		output wire  S_AXI_CTRL_BVALID,
		input wire  S_AXI_CTRL_BREADY,

		input wire [C_S_CTRL_AXI_ADDR_WIDTH-1 : 0] S_AXI_CTRL_ARADDR,
		input wire [2 : 0] S_AXI_CTRL_ARPROT,
		input wire  S_AXI_CTRL_ARVALID,
		output wire  S_AXI_CTRL_ARREADY,

		output wire [C_S_CTRL_AXI-1 : 0] S_AXI_CTRL_RDATA,
		output wire [1 : 0] S_AXI_CTRL_RRESP,
		output wire  S_AXI_CTRL_RVALID,
		input wire  S_AXI_CTRL_RREADY,

// -------------------- END AXI CONFIGURATION S PORTS ----------------------


//--------------------- M OUTPUT INTERFACE PORTS --------------------------

		output wire [C_M_AXI_ID_WIDTH-1 : 0] M_AXI_AWID,
		output wire [C_M_AXI_ADDR_WIDTH-1 : 0] M_AXI_AWADDR,
		output wire [7 : 0] M_AXI_AWLEN,
		output wire [2 : 0] M_AXI_AWSIZE,
		output wire [1 : 0] M_AXI_AWBURST,
		output wire  M_AXI_AWLOCK,
		output wire [3 : 0] M_AXI_AWCACHE,
		output wire [2 : 0] M_AXI_AWPROT,
		output wire [3 : 0] M_AXI_AWQOS,
		output wire [C_M_AXI_AWUSER_WIDTH-1 : 0] M_AXI_AWUSER,
		output wire  M_AXI_AWVALID,
		input wire  M_AXI_AWREADY,

		output wire [C_M_AXI_DATA_WIDTH-1 : 0] M_AXI_WDATA,
		output wire [C_M_AXI_DATA_WIDTH/8-1 : 0] M_AXI_WSTRB,
		output wire  M_AXI_WLAST,
		output wire [C_M_AXI_WUSER_WIDTH-1 : 0] M_AXI_WUSER,
		output wire  M_AXI_WVALID,
		input wire  M_AXI_WREADY,

		input wire [C_M_AXI_ID_WIDTH-1 : 0] M_AXI_BID,
		input wire [1 : 0] M_AXI_BRESP,
		input wire [C_M_AXI_BUSER_WIDTH-1 : 0] M_AXI_BUSER,
		input wire  M_AXI_BVALID,
		output wire  M_AXI_BREADY,

		output wire [C_M_AXI_ID_WIDTH-1 : 0] M_AXI_ARID,
		output wire [C_M_AXI_ADDR_WIDTH-1 : 0] M_AXI_ARADDR,
		output wire [7 : 0] M_AXI_ARLEN,
		output wire [2 : 0] M_AXI_ARSIZE,
		output wire [1 : 0] M_AXI_ARBURST,
		output wire  M_AXI_ARLOCK,
		output wire [3 : 0] M_AXI_ARCACHE,
		output wire [2 : 0] M_AXI_ARPROT,
		output wire [3 : 0] M_AXI_ARQOS,
		output wire [C_M_AXI_ARUSER_WIDTH-1 : 0] M_AXI_ARUSER,
		output wire  M_AXI_ARVALID,
		input wire  M_AXI_ARREADY,

		input wire [C_M_AXI_ID_WIDTH-1 : 0] M_AXI_RID,
		input wire [C_M_AXI_DATA_WIDTH-1 : 0] M_AXI_RDATA,
		input wire [1 : 0] M_AXI_RRESP,
		input wire  M_AXI_RLAST,
		input wire [C_M_AXI_RUSER_WIDTH-1 : 0] M_AXI_RUSER,
		input wire  M_AXI_RVALID,
		output wire  M_AXI_RREADY

//--------------------- END M OUTPUT INTERFACE PORTS ---------------------

	);

//---------------------  AXI S CONFIGURATION SIGNALS -----------------------
	reg [C_S_CTRL_AXI_ADDR_WIDTH-1 : 0] 	 axi_awaddr;
	reg  	                                 axi_awready;
	reg  	                                 axi_wready;
	reg [1 : 0] 	                         axi_bresp;
	reg  	                                 axi_bvalid;
	reg [C_S_CTRL_AXI_ADDR_WIDTH-1 : 0] 	 axi_araddr;
	reg  	                                 axi_arready;
	reg [C_S_CTRL_AXI-1 : 0] 	             axi_rdata;
	reg [1 : 0] 	                         axi_rresp;
	reg  	                                 axi_rvalid;

	localparam integer ADDR_LSB = (C_S_CTRL_AXI/32) + 1;
	localparam integer OPT_MEM_ADDR_BITS = 5;


	reg [C_S_CTRL_AXI-1:0]	slv_reg0;
	reg [C_S_CTRL_AXI-1:0]	slv_reg1;
	reg [C_S_CTRL_AXI-1:0]	slv_reg2;
	reg [C_S_CTRL_AXI-1:0]	slv_reg3;
	reg [C_S_CTRL_AXI-1:0]	slv_reg4;
	reg [C_S_CTRL_AXI-1:0]	slv_reg5;
	reg [C_S_CTRL_AXI-1:0]	slv_reg6;
	reg [C_S_CTRL_AXI-1:0]	slv_reg7;
	reg [C_S_CTRL_AXI-1:0]	slv_reg8;
	reg [C_S_CTRL_AXI-1:0]	slv_reg9;
	reg [C_S_CTRL_AXI-1:0]	slv_reg10;
	reg [C_S_CTRL_AXI-1:0]	slv_reg11;
	reg [C_S_CTRL_AXI-1:0]	slv_reg12;
	reg [C_S_CTRL_AXI-1:0]	slv_reg13;
	reg [C_S_CTRL_AXI-1:0]	slv_reg14;
	reg [C_S_CTRL_AXI-1:0]	slv_reg15;
	reg [C_S_CTRL_AXI-1:0]	slv_reg16;
	reg [C_S_CTRL_AXI-1:0]	slv_reg17;
	reg [C_S_CTRL_AXI-1:0]	slv_reg18;
	reg [C_S_CTRL_AXI-1:0]	slv_reg19;
	reg [C_S_CTRL_AXI-1:0]	slv_reg20;
	reg [C_S_CTRL_AXI-1:0]	slv_reg21;
	reg [C_S_CTRL_AXI-1:0]	slv_reg22;
	reg [C_S_CTRL_AXI-1:0]	slv_reg23;
	reg [C_S_CTRL_AXI-1:0]	slv_reg24;
	reg [C_S_CTRL_AXI-1:0]	slv_reg25;
	reg [C_S_CTRL_AXI-1:0]	slv_reg26;
	reg [C_S_CTRL_AXI-1:0]	slv_reg27;
	reg [C_S_CTRL_AXI-1:0]	slv_reg28;
	reg [C_S_CTRL_AXI-1:0]	slv_reg29;
	reg [C_S_CTRL_AXI-1:0]	slv_reg30;
	reg [C_S_CTRL_AXI-1:0]	slv_reg31;
	reg [C_S_CTRL_AXI-1:0]	slv_reg32;
	reg [C_S_CTRL_AXI-1:0]	slv_reg33;
	reg [C_S_CTRL_AXI-1:0]	slv_reg34;
	reg [C_S_CTRL_AXI-1:0]	slv_reg35;
	reg [C_S_CTRL_AXI-1:0]	slv_reg36;
	reg [C_S_CTRL_AXI-1:0]	slv_reg37;
	wire	                 slv_reg_rden;
	wire	                 slv_reg_wren;
	reg [C_S_CTRL_AXI-1:0]	 reg_data_out;
	integer	                 byte_index;
	reg	                     aw_en;

	assign S_AXI_CTRL_AWREADY	= axi_awready;
	assign S_AXI_CTRL_WREADY	= axi_wready;
	assign S_AXI_CTRL_BRESP	= axi_bresp;
	assign S_AXI_CTRL_BVALID	= axi_bvalid;
	assign S_AXI_CTRL_ARREADY	= axi_arready;
	assign S_AXI_CTRL_RDATA	= axi_rdata;
	assign S_AXI_CTRL_RRESP	= axi_rresp;
	assign S_AXI_CTRL_RVALID	= axi_rvalid;

//-------------------  END AXI S CONFIGURATION SIGNAL ----------------------

//-------------------  AXI M INTERNAL SIGNALS -----------------------------

    wire [C_M_AXI_ID_WIDTH-1 : 0] M_AXI_AWID_wire;
    wire  [C_M_AXI_ADDR_WIDTH-1 : 0] M_AXI_AWADDR_wire;
    wire [7 : 0] M_AXI_AWLEN_wire;
    wire [2 : 0] M_AXI_AWSIZE_wire;
    wire [1 : 0] M_AXI_AWBURST_wire;
    wire M_AXI_AWLOCK_wire;
    wire [3 : 0] M_AXI_AWCACHE_wire;
    wire [2 : 0] M_AXI_AWPROT_wire;
    wire [3 : 0] M_AXI_AWQOS_wire;
    wire [C_M_AXI_AWUSER_WIDTH-1 : 0] M_AXI_AWUSER_wire;
    wire M_AXI_AWVALID_wire;
    wire M_AXI_AWREADY_wire;

	wire [C_M_AXI_DATA_WIDTH-1 : 0] M_AXI_WDATA_wire;
	wire [C_M_AXI_DATA_WIDTH/8-1 : 0] M_AXI_WSTRB_wire;
	wire M_AXI_WLAST_wire;
	wire [C_M_AXI_WUSER_WIDTH-1 : 0] M_AXI_WUSER_wire;
	wire M_AXI_WVALID_wire;
	wire M_AXI_WREADY_wire;

	wire [C_M_AXI_ID_WIDTH-1 : 0] M_AXI_BID_wire;
	wire [1 : 0] M_AXI_BRESP_wire;
	wire [C_M_AXI_BUSER_WIDTH-1 : 0] M_AXI_BUSER_wire;
	wire M_AXI_BVALID_wire;
	wire M_AXI_BREADY_wire;

    wire [C_M_AXI_ID_WIDTH-1 : 0] M_AXI_ARID_wire;
    wire  [C_M_AXI_ADDR_WIDTH-1 : 0] M_AXI_ARADDR_wire;
    wire [7 : 0] M_AXI_ARLEN_wire;
    wire [2 : 0] M_AXI_ARSIZE_wire;
    wire [1 : 0] M_AXI_ARBURST_wire;
    wire M_AXI_ARLOCK_wire;
    wire [3 : 0] M_AXI_ARCACHE_wire;
    wire [2 : 0] M_AXI_ARPROT_wire;
    wire [3 : 0] M_AXI_ARQOS_wire;
    wire [C_M_AXI_AWUSER_WIDTH-1 : 0] M_AXI_ARUSER_wire;
    wire M_AXI_ARVALID_wire;
    wire M_AXI_ARREADY_wire;

	wire [C_M_AXI_ID_WIDTH-1 : 0] M_AXI_RID_wire;
	wire [C_M_AXI_DATA_WIDTH-1 : 0] M_AXI_RDATA_wire;
	wire [1 : 0] M_AXI_RRESP_wire;
	wire M_AXI_RLAST_wire;
	wire [C_M_AXI_RUSER_WIDTH-1 : 0] M_AXI_RUSER_wire;
	wire M_AXI_RVALID_wire;
	wire M_AXI_RREADY_wire;


	reg [C_M_AXI_ID_WIDTH-1 : 0] M_AXI_AWID_INT;
	reg [C_M_AXI_ADDR_WIDTH-1 : 0] M_AXI_AWADDR_INT;
	reg [7 : 0] M_AXI_AWLEN_INT;
	reg [2 : 0] M_AXI_AWSIZE_INT;
	reg [1 : 0] M_AXI_AWBURST_INT;
    reg M_AXI_AWLOCK_INT;
	reg [3 : 0] M_AXI_AWCACHE_INT;
	reg [2 : 0] M_AXI_AWPROT_INT;
	reg [3 : 0] M_AXI_AWQOS_INT;
	reg [C_M_AXI_AWUSER_WIDTH-1 : 0] M_AXI_AWUSER_INT;
	reg M_AXI_AWVALID_INT;

	reg [C_M_AXI_ID_WIDTH-1 : 0] M_AXI_ARID_INT;
	reg [C_M_AXI_ADDR_WIDTH-1 : 0] M_AXI_ARADDR_INT;
	reg [7 : 0] M_AXI_ARLEN_INT;
	reg [2 : 0] M_AXI_ARSIZE_INT;
 	reg [1 : 0] M_AXI_ARBURST_INT;
    reg M_AXI_ARLOCK_INT;
 	reg [3 : 0] M_AXI_ARCACHE_INT;
 	reg [2 : 0] M_AXI_ARPROT_INT;
	reg [3 : 0] M_AXI_ARQOS_INT;
	reg [C_M_AXI_ARUSER_WIDTH-1 : 0] M_AXI_ARUSER_INT;
	reg M_AXI_ARVALID_INT;


//-------------------  END AXI M INTERNAL SIGNALS -------------------------

//------------------- MEMORY CNTRL LOGIC SIGNALS -------------------------------

	reg AW_ILL_TRANS[MAX_OUTS_TRANS-1 : 0];
	reg [LOG_MAX_OUTS_TRAN-1 : 0] AW_ILL_TRANS_FIL_PTR;
	reg [LOG_MAX_OUTS_TRAN-1 : 0] AW_ILL_DATA_TRANS_SRV_PTR;
	reg [LOG_MAX_OUTS_TRAN-1 : 0] AW_ILL_TRANS_SRV_PTR;
	reg AR_ILL_TRANS[MAX_OUTS_TRANS-1 : 0];
    reg [LOG_MAX_OUTS_TRAN-1 : 0] AR_ILL_TRANS_FIL_PTR;
    reg [LOG_MAX_OUTS_TRAN-1 : 0] AR_ILL_TRANS_SRV_PTR;
	reg AW_STATE;
	reg AR_STATE;
	reg B_STATE;
	reg R_STATE;
	reg AW_ILLEGAL_REQ;
	reg AR_ILLEGAL_REQ;

	wire W_DATA_TO_SERVE;
	wire W_B_TO_SERVE;
	wire W_CH_EN;

    wire AW_CH_EN;
    wire AR_CH_EN;

    reg AW_CH_DIS;
    reg AR_CH_DIS;

    wire AW_EN_RST;
    wire AR_EN_RST;

	wire [15 : 0] AW_ADDR_VALID;
	wire [15 : 0] AR_ADDR_VALID;

	wire [15 : 0] AW_HIGH_ADDR;
	wire [15 : 0] AR_HIGH_ADDR;

	wire AW_ADDR_VALID_FLAG;
	wire AR_ADDR_VALID_FLAG;

	wire AR_OVERFLOW_DETC;
	wire AW_OVERFLOW_DETC;

//------------------- END MEMORY CNTRL LOGIC SIGNALS --------------------------

//-------------------- S CONTROL LOGIC ----------------------------------------
	always @( posedge ACLK )
	begin
	  if ( ARESETN == 1'b0 )
	    begin
	      axi_awready <= 1'b0;
	      aw_en <= 1'b1;
	    end
	  else
	    begin
	      if (~axi_awready && S_AXI_CTRL_AWVALID && S_AXI_CTRL_WVALID && aw_en)
	        begin
	          axi_awready <= 1'b1;
	          aw_en <= 1'b0;
	        end
	        else if (S_AXI_CTRL_BREADY && axi_bvalid)
	            begin
	              aw_en <= 1'b1;
	              axi_awready <= 1'b0;
	            end
	      else
	        begin
	          axi_awready <= 1'b0;
	        end
	    end
	end

	always @( posedge ACLK )
	begin
	  if ( ARESETN == 1'b0 )
	    begin
	      axi_awaddr <= 0;
	    end
	  else
	    begin
	      if (~axi_awready && S_AXI_CTRL_AWVALID && S_AXI_CTRL_WVALID && aw_en)
	        begin
	          axi_awaddr <= S_AXI_CTRL_AWADDR;
	        end
	    end
	end


	always @( posedge ACLK )
	begin
	  if ( ARESETN == 1'b0 )
	    begin
	      axi_wready <= 1'b0;
	    end
	  else
	    begin
	      if (~axi_wready && S_AXI_CTRL_WVALID && S_AXI_CTRL_AWVALID && aw_en )
	        begin
	          axi_wready <= 1'b1;
	        end
	      else
	        begin
	          axi_wready <= 1'b0;
	        end
	    end
	end

	assign slv_reg_wren = axi_wready && S_AXI_CTRL_WVALID && axi_awready && S_AXI_CTRL_AWVALID;

	always @( posedge ACLK )
	begin
	  if ( ARESETN == 1'b0 )
	    begin
		  slv_reg0 <= 0;
	      slv_reg1 <= 0;
	      slv_reg2 <= 0;
	      slv_reg3 <= 0;
	      slv_reg4 <= 0;
	      slv_reg5 <= 0;
	      slv_reg6 <= 0;
	      slv_reg7 <= 0;
	      slv_reg8 <= 0;
	      slv_reg9 <= 0;
	      slv_reg10 <= 0;
	      slv_reg11 <= 0;
	      slv_reg12 <= 0;
	      slv_reg13 <= 0;
	      slv_reg14 <= 0;
	      slv_reg15 <= 0;
	      slv_reg16 <= 0;
	      slv_reg17 <= 0;
	      slv_reg18 <= 0;
	      slv_reg19 <= 0;
	      slv_reg20 <= 0;
	      slv_reg21 <= 0;
	      slv_reg22 <= 0;
	      slv_reg23 <= 0;
	      slv_reg24 <= 0;
	      slv_reg25 <= 0;
	      slv_reg26 <= 0;
	      slv_reg27 <= 0;
	      slv_reg28 <= 0;
	      slv_reg29 <= 0;
	      slv_reg30 <= 0;
	      slv_reg31 <= 0;
	      slv_reg32 <= 0;
	      slv_reg33 <= 0;
	      slv_reg34 <= 0;
	      slv_reg35 <= 0;
	      slv_reg36 <= 0;
	      slv_reg37 <= 0;
	    end
	  else begin
		  slv_reg1 <= 0;
	    if (slv_reg_wren)
	      begin
				case ( axi_awaddr[ADDR_LSB+OPT_MEM_ADDR_BITS:ADDR_LSB] )
					6'h00:
						for ( byte_index = 0; byte_index <= (C_S_CTRL_AXI/8)-1; byte_index = byte_index+1 )
							if ( S_AXI_CTRL_WSTRB[byte_index] == 1 ) begin
								slv_reg0[(byte_index*8) +: 8] <= S_AXI_CTRL_WDATA[(byte_index*8) +: 8];
							end
					6'h01:
						for ( byte_index = 0; byte_index <= (C_S_CTRL_AXI/8)-1; byte_index = byte_index+1 )
							if ( S_AXI_CTRL_WSTRB[byte_index] == 1 ) begin
								slv_reg1[(byte_index*8) +: 8] <= S_AXI_CTRL_WDATA[(byte_index*8) +: 8];
							end
					6'h02:
						for ( byte_index = 0; byte_index <= (C_S_CTRL_AXI/8)-1; byte_index = byte_index+1 )
							if ( S_AXI_CTRL_WSTRB[byte_index] == 1 ) begin
								slv_reg2[(byte_index*8) +: 8] <= S_AXI_CTRL_WDATA[(byte_index*8) +: 8];
							end
					6'h03:
						for ( byte_index = 0; byte_index <= (C_S_CTRL_AXI/8)-1; byte_index = byte_index+1 )
							if ( S_AXI_CTRL_WSTRB[byte_index] == 1 ) begin
								slv_reg3[(byte_index*8) +: 8] <= S_AXI_CTRL_WDATA[(byte_index*8) +: 8];
							end
					6'h04:
						for ( byte_index = 0; byte_index <= (C_S_CTRL_AXI/8)-1; byte_index = byte_index+1 )
							if ( S_AXI_CTRL_WSTRB[byte_index] == 1 ) begin
								slv_reg4[(byte_index*8) +: 8] <= S_AXI_CTRL_WDATA[(byte_index*8) +: 8];
							end
					6'h05:
						for ( byte_index = 0; byte_index <= (C_S_CTRL_AXI/8)-1; byte_index = byte_index+1 )
							if ( S_AXI_CTRL_WSTRB[byte_index] == 1 ) begin
								slv_reg5[(byte_index*8) +: 8] <= S_AXI_CTRL_WDATA[(byte_index*8) +: 8];
							end
					6'h06:
						for ( byte_index = 0; byte_index <= (C_S_CTRL_AXI/8)-1; byte_index = byte_index+1 )
							if ( S_AXI_CTRL_WSTRB[byte_index] == 1 ) begin
								slv_reg6[(byte_index*8) +: 8] <= S_AXI_CTRL_WDATA[(byte_index*8) +: 8];
							end
					6'h07:
						for ( byte_index = 0; byte_index <= (C_S_CTRL_AXI/8)-1; byte_index = byte_index+1 )
							if ( S_AXI_CTRL_WSTRB[byte_index] == 1 ) begin
								slv_reg7[(byte_index*8) +: 8] <= S_AXI_CTRL_WDATA[(byte_index*8) +: 8];
							end
					6'h08:
						for ( byte_index = 0; byte_index <= (C_S_CTRL_AXI/8)-1; byte_index = byte_index+1 )
							if ( S_AXI_CTRL_WSTRB[byte_index] == 1 ) begin
								slv_reg8[(byte_index*8) +: 8] <= S_AXI_CTRL_WDATA[(byte_index*8) +: 8];
							end
					6'h09:
						for ( byte_index = 0; byte_index <= (C_S_CTRL_AXI/8)-1; byte_index = byte_index+1 )
							if ( S_AXI_CTRL_WSTRB[byte_index] == 1 ) begin
								slv_reg9[(byte_index*8) +: 8] <= S_AXI_CTRL_WDATA[(byte_index*8) +: 8];
							end
					6'h0A:
						for ( byte_index = 0; byte_index <= (C_S_CTRL_AXI/8)-1; byte_index = byte_index+1 )
							if ( S_AXI_CTRL_WSTRB[byte_index] == 1 ) begin
								slv_reg10[(byte_index*8) +: 8] <= S_AXI_CTRL_WDATA[(byte_index*8) +: 8];
							end
					6'h0B:
						for ( byte_index = 0; byte_index <= (C_S_CTRL_AXI/8)-1; byte_index = byte_index+1 )
							if ( S_AXI_CTRL_WSTRB[byte_index] == 1 ) begin
								slv_reg11[(byte_index*8) +: 8] <= S_AXI_CTRL_WDATA[(byte_index*8) +: 8];
							end
					6'h0C:
						for ( byte_index = 0; byte_index <= (C_S_CTRL_AXI/8)-1; byte_index = byte_index+1 )
							if ( S_AXI_CTRL_WSTRB[byte_index] == 1 ) begin
								slv_reg12[(byte_index*8) +: 8] <= S_AXI_CTRL_WDATA[(byte_index*8) +: 8];
							end
					6'h0D:
						for ( byte_index = 0; byte_index <= (C_S_CTRL_AXI/8)-1; byte_index = byte_index+1 )
							if ( S_AXI_CTRL_WSTRB[byte_index] == 1 ) begin
								slv_reg13[(byte_index*8) +: 8] <= S_AXI_CTRL_WDATA[(byte_index*8) +: 8];
							end
					6'h0E:
						for ( byte_index = 0; byte_index <= (C_S_CTRL_AXI/8)-1; byte_index = byte_index+1 )
							if ( S_AXI_CTRL_WSTRB[byte_index] == 1 ) begin
								slv_reg14[(byte_index*8) +: 8] <= S_AXI_CTRL_WDATA[(byte_index*8) +: 8];
							end
					6'h0F:
						for ( byte_index = 0; byte_index <= (C_S_CTRL_AXI/8)-1; byte_index = byte_index+1 )
							if ( S_AXI_CTRL_WSTRB[byte_index] == 1 ) begin
								slv_reg15[(byte_index*8) +: 8] <= S_AXI_CTRL_WDATA[(byte_index*8) +: 8];
							end
					6'h10:
						for ( byte_index = 0; byte_index <= (C_S_CTRL_AXI/8)-1; byte_index = byte_index+1 )
							if ( S_AXI_CTRL_WSTRB[byte_index] == 1 ) begin
								slv_reg16[(byte_index*8) +: 8] <= S_AXI_CTRL_WDATA[(byte_index*8) +: 8];
							end
					6'h11:
						for ( byte_index = 0; byte_index <= (C_S_CTRL_AXI/8)-1; byte_index = byte_index+1 )
							if ( S_AXI_CTRL_WSTRB[byte_index] == 1 ) begin
								slv_reg17[(byte_index*8) +: 8] <= S_AXI_CTRL_WDATA[(byte_index*8) +: 8];
							end
					6'h12:
						for ( byte_index = 0; byte_index <= (C_S_CTRL_AXI/8)-1; byte_index = byte_index+1 )
							if ( S_AXI_CTRL_WSTRB[byte_index] == 1 ) begin
								slv_reg18[(byte_index*8) +: 8] <= S_AXI_CTRL_WDATA[(byte_index*8) +: 8];
							end
					6'h13:
						for ( byte_index = 0; byte_index <= (C_S_CTRL_AXI/8)-1; byte_index = byte_index+1 )
							if ( S_AXI_CTRL_WSTRB[byte_index] == 1 ) begin
								slv_reg19[(byte_index*8) +: 8] <= S_AXI_CTRL_WDATA[(byte_index*8) +: 8];
							end
					6'h14:
						for ( byte_index = 0; byte_index <= (C_S_CTRL_AXI/8)-1; byte_index = byte_index+1 )
							if ( S_AXI_CTRL_WSTRB[byte_index] == 1 ) begin
								slv_reg20[(byte_index*8) +: 8] <= S_AXI_CTRL_WDATA[(byte_index*8) +: 8];
							end
					6'h15:
						for ( byte_index = 0; byte_index <= (C_S_CTRL_AXI/8)-1; byte_index = byte_index+1 )
							if ( S_AXI_CTRL_WSTRB[byte_index] == 1 ) begin
								slv_reg21[(byte_index*8) +: 8] <= S_AXI_CTRL_WDATA[(byte_index*8) +: 8];
							end
					6'h16:
						for ( byte_index = 0; byte_index <= (C_S_CTRL_AXI/8)-1; byte_index = byte_index+1 )
							if ( S_AXI_CTRL_WSTRB[byte_index] == 1 ) begin
								slv_reg22[(byte_index*8) +: 8] <= S_AXI_CTRL_WDATA[(byte_index*8) +: 8];
							end
					6'h17:
						for ( byte_index = 0; byte_index <= (C_S_CTRL_AXI/8)-1; byte_index = byte_index+1 )
							if ( S_AXI_CTRL_WSTRB[byte_index] == 1 ) begin
								slv_reg23[(byte_index*8) +: 8] <= S_AXI_CTRL_WDATA[(byte_index*8) +: 8];
							end
					6'h18:
						for ( byte_index = 0; byte_index <= (C_S_CTRL_AXI/8)-1; byte_index = byte_index+1 )
							if ( S_AXI_CTRL_WSTRB[byte_index] == 1 ) begin
								slv_reg24[(byte_index*8) +: 8] <= S_AXI_CTRL_WDATA[(byte_index*8) +: 8];
							end
					6'h19:
						for ( byte_index = 0; byte_index <= (C_S_CTRL_AXI/8)-1; byte_index = byte_index+1 )
							if ( S_AXI_CTRL_WSTRB[byte_index] == 1 ) begin
								slv_reg25[(byte_index*8) +: 8] <= S_AXI_CTRL_WDATA[(byte_index*8) +: 8];
							end
					6'h1A:
						for ( byte_index = 0; byte_index <= (C_S_CTRL_AXI/8)-1; byte_index = byte_index+1 )
							if ( S_AXI_CTRL_WSTRB[byte_index] == 1 ) begin
								slv_reg26[(byte_index*8) +: 8] <= S_AXI_CTRL_WDATA[(byte_index*8) +: 8];
							end
					6'h1B:
						for ( byte_index = 0; byte_index <= (C_S_CTRL_AXI/8)-1; byte_index = byte_index+1 )
							if ( S_AXI_CTRL_WSTRB[byte_index] == 1 ) begin
								slv_reg27[(byte_index*8) +: 8] <= S_AXI_CTRL_WDATA[(byte_index*8) +: 8];
							end
					6'h1C:
						for ( byte_index = 0; byte_index <= (C_S_CTRL_AXI/8)-1; byte_index = byte_index+1 )
							if ( S_AXI_CTRL_WSTRB[byte_index] == 1 ) begin
								slv_reg28[(byte_index*8) +: 8] <= S_AXI_CTRL_WDATA[(byte_index*8) +: 8];
							end
					6'h1D:
						for ( byte_index = 0; byte_index <= (C_S_CTRL_AXI/8)-1; byte_index = byte_index+1 )
							if ( S_AXI_CTRL_WSTRB[byte_index] == 1 ) begin
								slv_reg29[(byte_index*8) +: 8] <= S_AXI_CTRL_WDATA[(byte_index*8) +: 8];
							end
					6'h1E:
						for ( byte_index = 0; byte_index <= (C_S_CTRL_AXI/8)-1; byte_index = byte_index+1 )
							if ( S_AXI_CTRL_WSTRB[byte_index] == 1 ) begin
								slv_reg30[(byte_index*8) +: 8] <= S_AXI_CTRL_WDATA[(byte_index*8) +: 8];
							end
					6'h1F:
						for ( byte_index = 0; byte_index <= (C_S_CTRL_AXI/8)-1; byte_index = byte_index+1 )
							if ( S_AXI_CTRL_WSTRB[byte_index] == 1 ) begin
								slv_reg31[(byte_index*8) +: 8] <= S_AXI_CTRL_WDATA[(byte_index*8) +: 8];
							end
					6'h20:
						for ( byte_index = 0; byte_index <= (C_S_CTRL_AXI/8)-1; byte_index = byte_index+1 )
							if ( S_AXI_CTRL_WSTRB[byte_index] == 1 ) begin
								slv_reg32[(byte_index*8) +: 8] <= S_AXI_CTRL_WDATA[(byte_index*8) +: 8];
							end
					6'h21:
						for ( byte_index = 0; byte_index <= (C_S_CTRL_AXI/8)-1; byte_index = byte_index+1 )
							if ( S_AXI_CTRL_WSTRB[byte_index] == 1 ) begin
								slv_reg33[(byte_index*8) +: 8] <= S_AXI_CTRL_WDATA[(byte_index*8) +: 8];
							end
					6'h22:
						for ( byte_index = 0; byte_index <= (C_S_CTRL_AXI/8)-1; byte_index = byte_index+1 )
							if ( S_AXI_CTRL_WSTRB[byte_index] == 1 ) begin
								slv_reg34[(byte_index*8) +: 8] <= S_AXI_CTRL_WDATA[(byte_index*8) +: 8];
							end
					6'h23:
						for ( byte_index = 0; byte_index <= (C_S_CTRL_AXI/8)-1; byte_index = byte_index+1 )
							if ( S_AXI_CTRL_WSTRB[byte_index] == 1 ) begin
								slv_reg35[(byte_index*8) +: 8] <= S_AXI_CTRL_WDATA[(byte_index*8) +: 8];
							end
					6'h24:
						for ( byte_index = 0; byte_index <= (C_S_CTRL_AXI/8)-1; byte_index = byte_index+1 )
							if ( S_AXI_CTRL_WSTRB[byte_index] == 1 ) begin
								slv_reg36[(byte_index*8) +: 8] <= S_AXI_CTRL_WDATA[(byte_index*8) +: 8];
							end
					6'h25:
						for ( byte_index = 0; byte_index <= (C_S_CTRL_AXI/8)-1; byte_index = byte_index+1 )
							if ( S_AXI_CTRL_WSTRB[byte_index] == 1 ) begin
								slv_reg37[(byte_index*8) +: 8] <= S_AXI_CTRL_WDATA[(byte_index*8) +: 8];
							end
					default : begin
											slv_reg0 <= slv_reg0;
											slv_reg1 <= slv_reg1;
											slv_reg2 <= slv_reg2;
											slv_reg3 <= slv_reg3;
											slv_reg4 <= slv_reg4;
											slv_reg5 <= slv_reg5;
											slv_reg6 <= slv_reg6;
											slv_reg7 <= slv_reg7;
											slv_reg8 <= slv_reg8;
											slv_reg9 <= slv_reg9;
											slv_reg10 <= slv_reg10;
											slv_reg11 <= slv_reg11;
											slv_reg12 <= slv_reg12;
											slv_reg13 <= slv_reg13;
											slv_reg14 <= slv_reg14;
											slv_reg15 <= slv_reg15;
											slv_reg16 <= slv_reg16;
											slv_reg17 <= slv_reg17;
											slv_reg18 <= slv_reg18;
											slv_reg19 <= slv_reg19;
											slv_reg20 <= slv_reg20;
											slv_reg21 <= slv_reg21;
											slv_reg22 <= slv_reg22;
											slv_reg23 <= slv_reg23;
											slv_reg24 <= slv_reg24;
											slv_reg25 <= slv_reg25;
											slv_reg26 <= slv_reg26;
											slv_reg27 <= slv_reg27;
											slv_reg28 <= slv_reg28;
											slv_reg29 <= slv_reg29;
											slv_reg30 <= slv_reg30;
											slv_reg31 <= slv_reg31;
											slv_reg32 <= slv_reg32;
											slv_reg33 <= slv_reg33;
											slv_reg34 <= slv_reg34;
											slv_reg35 <= slv_reg35;
											slv_reg36 <= slv_reg36;
											slv_reg37 <= slv_reg37;
										end
				endcase
			end
	end
end

	always @( posedge ACLK )
	begin
	  if ( ARESETN == 1'b0 )
	    begin
	      axi_bvalid  <= 0;
	      axi_bresp   <= 2'b0;
	    end
	  else
	    begin
	      if (axi_awready && S_AXI_CTRL_AWVALID && ~axi_bvalid && axi_wready && S_AXI_CTRL_WVALID)
	        begin
	          axi_bvalid <= 1'b1;
	          axi_bresp  <= 2'b0;
	        end
	      else
	        begin
	          if (S_AXI_CTRL_BREADY && axi_bvalid)
	            begin
	              axi_bvalid <= 1'b0;
	            end
	        end
	    end
	end

	always @( posedge ACLK )
	begin
	  if ( ARESETN == 1'b0 )
	    begin
	      axi_arready <= 1'b0;
	      axi_araddr  <= 32'b0;
	    end
	  else
	    begin
	      if (~axi_arready && S_AXI_CTRL_ARVALID)
	        begin
	          axi_arready <= 1'b1;
	          axi_araddr  <= S_AXI_CTRL_ARADDR;
	        end
	      else
	        begin
	          axi_arready <= 1'b0;
	        end
	    end
	end

	always @( posedge ACLK )
	begin
	  if ( ARESETN == 1'b0 )
	    begin
	      axi_rvalid <= 0;
	      axi_rresp  <= 0;
	    end
	  else
	    begin
	      if (axi_arready && S_AXI_CTRL_ARVALID && ~axi_rvalid)
	        begin
	          axi_rvalid <= 1'b1;
	          axi_rresp  <= 2'b0;
	        end
	      else if (axi_rvalid && S_AXI_CTRL_RREADY)
	        begin
	          axi_rvalid <= 1'b0;
	        end
	    end
	end

	assign slv_reg_rden = axi_arready & S_AXI_CTRL_ARVALID & ~axi_rvalid;
	always @(*)
	begin
	case ( axi_araddr[ADDR_LSB+OPT_MEM_ADDR_BITS:ADDR_LSB] )
		6'h00   : reg_data_out <= slv_reg0;
		6'h01   : reg_data_out <= slv_reg1;
		6'h02   : reg_data_out <= slv_reg2;
		6'h03   : reg_data_out <= slv_reg3;
		6'h04   : reg_data_out <= slv_reg4;
		6'h05   : reg_data_out <= slv_reg5;
		6'h06   : reg_data_out <= slv_reg6;
		6'h07   : reg_data_out <= slv_reg7;
		6'h08   : reg_data_out <= slv_reg8;
		6'h09   : reg_data_out <= slv_reg9;
		6'h0A   : reg_data_out <= slv_reg10;
		6'h0B   : reg_data_out <= slv_reg11;
		6'h0C   : reg_data_out <= slv_reg12;
		6'h0D   : reg_data_out <= slv_reg13;
		6'h0E   : reg_data_out <= slv_reg14;
		6'h0F   : reg_data_out <= slv_reg15;
		6'h10   : reg_data_out <= slv_reg16;
		6'h11   : reg_data_out <= slv_reg17;
		6'h12   : reg_data_out <= slv_reg18;
		6'h13   : reg_data_out <= slv_reg19;
		6'h14   : reg_data_out <= slv_reg20;
		6'h15   : reg_data_out <= slv_reg21;
		6'h16   : reg_data_out <= slv_reg22;
		6'h17   : reg_data_out <= slv_reg23;
		6'h18   : reg_data_out <= slv_reg24;
		6'h19   : reg_data_out <= slv_reg25;
		6'h1A   : reg_data_out <= slv_reg26;
		6'h1B   : reg_data_out <= slv_reg27;
		6'h1C   : reg_data_out <= slv_reg28;
		6'h1D   : reg_data_out <= slv_reg29;
		6'h1E   : reg_data_out <= slv_reg30;
		6'h1F   : reg_data_out <= slv_reg31;
		6'h20   : reg_data_out <= slv_reg32;
		6'h21   : reg_data_out <= slv_reg33;
		6'h22   : reg_data_out <= slv_reg34;
		6'h23   : reg_data_out <= slv_reg35;
		6'h24   : reg_data_out <= slv_reg36;
		6'h25   : reg_data_out <= slv_reg37;
		default : reg_data_out <= 0;
	endcase
	end

	always @( posedge ACLK )
	begin
	  if ( ARESETN == 1'b0 )
	    begin
	      axi_rdata  <= 0;
	    end
	  else
	    begin
	      if (slv_reg_rden)
	        begin
	          axi_rdata <= reg_data_out;
	        end
	    end
	end

//-------------------- END SLAVE CNTL LOGIC --------------------------------------


//---------------------- INSTANCIATE THE GENERIC AXI M CONTROLLER --------------------------

// Connect optional signals

// Instrantiate the generic AXI M Controller module
AXI_M_Generic_Module MyAXI_M_Generic_Module(
    .clk(ACLK),
    .axi_resetn(ARESETN),
    .m_axi_awid(M_AXI_AWID_wire),
	.m_axi_awaddr(M_AXI_AWADDR_wire),
    .m_axi_awlen(M_AXI_AWLEN_wire),
    .m_axi_awsize(M_AXI_AWSIZE_wire),
    .m_axi_awburst(M_AXI_AWBURST_wire),
	.m_axi_awlock(M_AXI_AWLOCK_wire),
    .m_axi_awcache(M_AXI_AWCACHE_wire),
	.m_axi_awprot(M_AXI_AWPROT_wire),
	.m_axi_awqos(M_AXI_AWQOS_wire),
    .m_axi_awuser(M_AXI_AWUSER_wire),
    .m_axi_awvalid(M_AXI_AWVALID_wire),
	.m_axi_awready(M_AXI_AWREADY_wire),
	.m_axi_wdata(M_AXI_WDATA_wire),
	.m_axi_wstrb(M_AXI_WSTRB_wire),
	.m_axi_wlast(M_AXI_WLAST_wire),
	.m_axi_wuser(M_AXI_WUSER_wire),
	.m_axi_wvalid(M_AXI_WVALID_wire),
	.m_axi_wready(M_AXI_WREADY_wire),
	.m_axi_bid(M_AXI_BID_wire),
	.m_axi_bresp(M_AXI_BRESP_wire),
	.m_axi_buser(M_AXI_BUSER_wire),
	.m_axi_bvalid(M_AXI_BVALID_wire),
	.m_axi_bready(M_AXI_BREADY_wire),
	.m_axi_arid(M_AXI_ARID_wire),
	.m_axi_araddr(M_AXI_ARADDR_wire),
	.m_axi_arlen(M_AXI_ARLEN_wire),
	.m_axi_arsize(M_AXI_ARSIZE_wire),
	.m_axi_arburst(M_AXI_ARBURST_wire),
	.m_axi_arlock(M_AXI_ARLOCK_wire),
	.m_axi_arcache(M_AXI_ARCACHE_wire),
	.m_axi_arprot(M_AXI_ARPROT_wire),
	.m_axi_arqos(M_AXI_ARQOS_wire),
	.m_axi_aruser(M_AXI_ARUSER_wire),
	.m_axi_arvalid(M_AXI_ARVALID_wire),
	.m_axi_arready(M_AXI_ARREADY_wire),
	.m_axi_rid(M_AXI_RID_wire),
	.m_axi_rdata(M_AXI_RDATA_wire),
	.m_axi_rresp(M_AXI_RRESP_wire),
	.m_axi_rlast(M_AXI_RLAST_wire),
	.m_axi_ruser(M_AXI_RUSER_wire),
	.m_axi_rvalid(M_AXI_RVALID_wire),
	.m_axi_rready(M_AXI_RREADY_wire)
);


//---------------------- END INSTANCIATE THE GENERIC AXI M CONTROLLER -----------------------

//------------------------ ACCESS CONTROL WRITE MANAGEMENT ---------------------------------

// single interrupt line
//assign INTR_LINE = ~AR_CH_DIS || ~AW_CH_DIS;

assign INTR_LINE_R = AR_CH_DIS;
assign INTR_LINE_W = AW_CH_DIS;

assign AW_CH_EN = ~AW_ILLEGAL_REQ && ~AW_CH_DIS;
assign AR_CH_EN = ~AR_ILLEGAL_REQ && ~AR_CH_DIS;

assign AW_EN_RST = slv_reg1[0];
assign AR_EN_RST = slv_reg1[1];

always @( posedge ACLK )
begin
    if ( ARESETN == 1'b0) begin
		 AR_CH_DIS <= 0;
		 AW_CH_DIS <= 0;
    end
    else begin
        if (AW_ILLEGAL_REQ) begin
	       AW_CH_DIS <= 1;
		end
		else if (AW_EN_RST) begin
			AW_CH_DIS <= 0;
		end

		if (AR_ILLEGAL_REQ) begin
		  AR_CH_DIS <= 1;
        end
		else if (AR_EN_RST) begin
	       AR_CH_DIS <= 0;
		end
    end
end


assign M_AXI_AWREADY_wire = ~AW_STATE && AW_CH_EN;
assign M_AXI_AWVALID = AW_STATE && ~AW_ILLEGAL_REQ;

assign M_AXI_AWID = M_AXI_AWID_INT;
assign M_AXI_AWADDR = M_AXI_AWADDR_INT;
assign M_AXI_AWLEN = M_AXI_AWLEN_INT;
assign M_AXI_AWSIZE = M_AXI_AWSIZE_INT;
assign M_AXI_AWBURST = M_AXI_AWBURST_INT;
assign M_AXI_AWLOCK = M_AXI_AWLOCK_INT;
assign M_AXI_AWCACHE = M_AXI_AWCACHE_INT;
assign M_AXI_AWPROT = M_AXI_AWPROT_INT;
assign M_AXI_AWQOS = M_AXI_AWQOS_INT;
assign M_AXI_AWUSER = M_AXI_AWUSER_INT;

assign AW_HIGH_ADDR = (M_AXI_AWADDR_wire + ((M_AXI_AWLEN_wire + 1) << C_LOG_BUS_SIZE_BYTE));

assign AW_ADDR_VALID[0] =  (slv_reg0[16] && (AW_HIGH_ADDR <=  slv_reg22[31:16]) && (M_AXI_AWADDR_wire[31:16] >= slv_reg22[15:0]) ) ? 1 : 0;
assign AW_ADDR_VALID[1] =  (slv_reg0[17] && (AW_HIGH_ADDR <=  slv_reg23[31:16]) && (M_AXI_AWADDR_wire[31:16] >= slv_reg23[15:0]) ) ? 1 : 0;
assign AW_ADDR_VALID[2] =  (slv_reg0[18] && (AW_HIGH_ADDR <=  slv_reg24[31:16]) && (M_AXI_AWADDR_wire[31:16] >= slv_reg24[15:0]) ) ? 1 : 0;
assign AW_ADDR_VALID[3] =  (slv_reg0[19] && (AW_HIGH_ADDR <=  slv_reg25[31:16]) && (M_AXI_AWADDR_wire[31:16] >= slv_reg25[15:0]) ) ? 1 : 0;
assign AW_ADDR_VALID[4] =  (slv_reg0[20] && (AW_HIGH_ADDR <=  slv_reg26[31:16]) && (M_AXI_AWADDR_wire[31:16] >= slv_reg26[15:0]) ) ? 1 : 0;
assign AW_ADDR_VALID[5] =  (slv_reg0[21] && (AW_HIGH_ADDR <=  slv_reg27[31:16]) && (M_AXI_AWADDR_wire[31:16] >= slv_reg27[15:0]) ) ? 1 : 0;
assign AW_ADDR_VALID[6] =  (slv_reg0[22] && (AW_HIGH_ADDR <=  slv_reg28[31:16]) && (M_AXI_AWADDR_wire[31:16] >= slv_reg28[15:0]) ) ? 1 : 0;
assign AW_ADDR_VALID[7] =  (slv_reg0[23] && (AW_HIGH_ADDR <=  slv_reg29[31:16]) && (M_AXI_AWADDR_wire[31:16] >= slv_reg29[15:0]) ) ? 1 : 0;
assign AW_ADDR_VALID[8] =  (slv_reg0[24] && (AW_HIGH_ADDR <=  slv_reg30[31:16]) && (M_AXI_AWADDR_wire[31:16] >= slv_reg30[15:0]) ) ? 1 : 0;
assign AW_ADDR_VALID[9] =  (slv_reg0[25] && (AW_HIGH_ADDR <=  slv_reg31[31:16]) && (M_AXI_AWADDR_wire[31:16] >= slv_reg31[15:0]) ) ? 1 : 0;
assign AW_ADDR_VALID[10] =  (slv_reg0[26] && (AW_HIGH_ADDR <=  slv_reg32[31:16]) && (M_AXI_AWADDR_wire[31:16] >= slv_reg32[15:0]) ) ? 1 : 0;
assign AW_ADDR_VALID[11] =  (slv_reg0[27] && (AW_HIGH_ADDR <=  slv_reg33[31:16]) && (M_AXI_AWADDR_wire[31:16] >= slv_reg33[15:0]) ) ? 1 : 0;
assign AW_ADDR_VALID[12] =  (slv_reg0[28] && (AW_HIGH_ADDR <=  slv_reg34[31:16]) && (M_AXI_AWADDR_wire[31:16] >= slv_reg34[15:0]) ) ? 1 : 0;
assign AW_ADDR_VALID[13] =  (slv_reg0[29] && (AW_HIGH_ADDR <=  slv_reg35[31:16]) && (M_AXI_AWADDR_wire[31:16] >= slv_reg35[15:0]) ) ? 1 : 0;
assign AW_ADDR_VALID[14] =  (slv_reg0[30] && (AW_HIGH_ADDR <=  slv_reg36[31:16]) && (M_AXI_AWADDR_wire[31:16] >= slv_reg36[15:0]) ) ? 1 : 0;
assign AW_ADDR_VALID[15] =  (slv_reg0[31] && (AW_HIGH_ADDR <=  slv_reg37[31:16]) && (M_AXI_AWADDR_wire[31:16] >= slv_reg37[15:0]) ) ? 1 : 0;


// ------------ OVERFLOW MANAGEMENT 04/29/2021 -----------------

//assign AW_ADDR_VALID_FLAG = |AW_ADDR_VALID;

assign AW_ADDR_VALID_FLAG = |AW_ADDR_VALID & ~AW_OVERFLOW_DETC;
assign AW_OVERFLOW_DETC = M_AXI_AWADDR_wire[C_M_AXI_ADDR_WIDTH-1] & ~AW_HIGH_ADDR[C_M_AXI_ADDR_WIDTH-1];

// -------------------------------------------------------------

always @(posedge ACLK)
begin
	if(ARESETN == 1'b0)
	   begin
	       AW_STATE <= 1'b0;
	       AW_ILLEGAL_REQ <= 0;
	       AW_ILL_TRANS_FIL_PTR <= 0;
	       M_AXI_AWID_INT <= 0;
           M_AXI_AWADDR_INT <= 0;
           M_AXI_AWLEN_INT <= 0;
           M_AXI_AWSIZE_INT <= 0;
           M_AXI_AWBURST_INT <= 0;
           M_AXI_AWLOCK_INT <= 0;
           M_AXI_AWCACHE_INT <= 0;
           M_AXI_AWPROT_INT <= 0;
           M_AXI_AWQOS_INT <= 0;
           M_AXI_AWUSER_INT <= 0;
	   end
	else
	   begin
	   if(~AW_STATE)
		  begin
			if( M_AXI_AWVALID_wire && M_AXI_AWREADY_wire)
				begin
					AW_STATE <= 1'b1;
					if( AW_ADDR_VALID_FLAG == 1 )
						begin

							AW_ILLEGAL_REQ <= 1'b0;
							AW_ILL_TRANS[AW_ILL_TRANS_FIL_PTR] <= 1'b0;
							M_AXI_AWID_INT <= M_AXI_AWID_wire;
							M_AXI_AWADDR_INT <= M_AXI_AWADDR_wire;
							M_AXI_AWLEN_INT <= M_AXI_AWLEN_wire;
							M_AXI_AWSIZE_INT <= M_AXI_AWSIZE_wire;
							M_AXI_AWBURST_INT <= M_AXI_AWBURST_wire;
							M_AXI_AWLOCK_INT <= M_AXI_AWLOCK_wire;
							M_AXI_AWCACHE_INT <= M_AXI_AWCACHE_wire;
							M_AXI_AWPROT_INT <= M_AXI_AWPROT_wire;
							M_AXI_AWQOS_INT <= M_AXI_AWQOS_wire;
							M_AXI_AWUSER_INT <= M_AXI_AWUSER_wire;
						end
				    else
						begin
							AW_ILLEGAL_REQ <= 1'b1;
							AW_ILL_TRANS[AW_ILL_TRANS_FIL_PTR] <= 1'b1;
							slv_reg4 <= M_AXI_AWADDR_wire;
							slv_reg5[7:0] <= M_AXI_AWLEN_wire;
							slv_reg5[C_M_AXI_DATA_WIDTH - 1 : C_M_AXI_DATA_WIDTH - 1 - C_M_AXI_ID_WIDTH] <= M_AXI_AWID_wire;
							slv_reg5[C_M_AXI_DATA_WIDTH - 1 - C_M_AXI_ID_WIDTH - 1 : C_M_AXI_DATA_WIDTH - 1 - C_M_AXI_ID_WIDTH - 1 - 3] <= M_AXI_AWPROT_wire;
							slv_reg5[C_M_AXI_DATA_WIDTH - 1 - C_M_AXI_ID_WIDTH - 1 - 3 - 1 : C_M_AXI_DATA_WIDTH - 1 - C_M_AXI_ID_WIDTH - 1 - 3 - 1 - 3] <= M_AXI_AWCACHE_wire;
							slv_reg5[C_M_AXI_DATA_WIDTH - 1 - C_M_AXI_ID_WIDTH - 1 - 3 - 1 - 3 - 1 : C_M_AXI_DATA_WIDTH - 1 - C_M_AXI_ID_WIDTH - 1 - 3 - 1 - 3 - 1] <= M_AXI_AWLOCK_wire;
						end
				    AW_ILL_TRANS_FIL_PTR <= AW_ILL_TRANS_FIL_PTR + 1;
				 end
		   end
	     else
	       begin
			 if( (AW_ILLEGAL_REQ == 1'b0 && M_AXI_AWREADY == 1'b1 ) || AW_ILLEGAL_REQ == 1'b1 )
				begin
					AW_STATE <= 1'b0;
					AW_ILLEGAL_REQ <= 0;
				end
   		   end
    end
end

assign M_AXI_WDATA =  W_CH_EN ? M_AXI_WDATA_wire : 0;
assign M_AXI_WSTRB =  W_CH_EN ? M_AXI_WSTRB_wire : 0;
assign M_AXI_WLAST =  W_CH_EN ? M_AXI_WLAST_wire : 0;
assign M_AXI_WUSER =  W_CH_EN ? M_AXI_WUSER_wire : 0;
assign M_AXI_WVALID = W_CH_EN ? M_AXI_WVALID_wire : 0;
assign M_AXI_WREADY_wire = W_CH_EN ? M_AXI_WREADY : 1;

assign W_DATA_TO_SERVE = |(AW_ILL_DATA_TRANS_SRV_PTR ^ AW_ILL_TRANS_FIL_PTR);
assign W_CH_EN = W_DATA_TO_SERVE & ~AW_ILL_TRANS[AW_ILL_DATA_TRANS_SRV_PTR];

always @(posedge ACLK)
begin
	if(ARESETN == 0)
	   begin
	       AW_ILL_DATA_TRANS_SRV_PTR <= 0;
	   end
	else
	   begin
	       if(M_AXI_WLAST_wire == 1 && M_AXI_WVALID_wire == 1)
		      begin
                AW_ILL_DATA_TRANS_SRV_PTR <= AW_ILL_DATA_TRANS_SRV_PTR + 1;
		      end
	   end
end

assign M_AXI_BID_wire = ~B_STATE ? M_AXI_BID : 0;
assign M_AXI_BRESP_wire = ~B_STATE ? M_AXI_BRESP : 2'b11;
assign M_AXI_BUSER_wire = ~B_STATE ? M_AXI_BUSER : 0;
assign M_AXI_BVALID_wire = ~B_STATE ? M_AXI_BVALID : 1;
assign M_AXI_BREADY = ~B_STATE ? M_AXI_BREADY_wire : 0;

assign W_B_TO_SERVE = |(AW_ILL_TRANS_SRV_PTR ^ AW_ILL_TRANS_FIL_PTR);

always @(posedge ACLK)
begin
	if(ARESETN == 1'b0)
	   begin
	       B_STATE <= 0;
	       AW_ILL_TRANS_SRV_PTR <= 0;
	   end
	else
	   begin
	       if(~B_STATE)
		      begin
			     if(M_AXI_WVALID_wire == 1 && M_AXI_WLAST_wire == 1 && AW_ILL_TRANS[AW_ILL_TRANS_SRV_PTR] == 1)
				    begin
					   B_STATE <= 1;
				    end
		      end
	       else
		      begin
			     if(M_AXI_BREADY_wire == 1)
				    begin
					   B_STATE <= 0;
				    end
		      end
		    if(M_AXI_BVALID_wire == 1 && M_AXI_BREADY_wire == 1)
		      begin
		          AW_ILL_TRANS_SRV_PTR <= AW_ILL_TRANS_SRV_PTR + 1;
		      end;
        end;
end

//------------------------ END ACCESS CONTROL WRITE MANAGEMENT ------------------------------

//------------------------ ACCESS CONTROL READS MANAGEMENT ---------------------------------

assign M_AXI_ARREADY_wire = ~AR_STATE && AR_CH_EN;
assign M_AXI_ARVALID = AR_STATE && ~AR_ILLEGAL_REQ;


assign M_AXI_ARID = M_AXI_ARID_INT;
assign M_AXI_ARADDR = M_AXI_ARADDR_INT;
assign M_AXI_ARLEN = M_AXI_ARLEN_INT;
assign M_AXI_ARSIZE = M_AXI_ARSIZE_INT;
assign M_AXI_ARBURST = M_AXI_ARBURST_INT;
assign M_AXI_ARLOCK = M_AXI_ARLOCK_INT;
assign M_AXI_ARCACHE = M_AXI_ARCACHE_INT;
assign M_AXI_ARPROT = M_AXI_ARPROT_INT;
assign M_AXI_ARQOS = M_AXI_ARQOS_INT;
assign M_AXI_ARUSER = M_AXI_ARUSER_INT;

assign AR_HIGH_ADDR = (M_AXI_ARADDR_wire + ((M_AXI_ARLEN_wire + 1) << C_LOG_BUS_SIZE_BYTE));

assign AR_ADDR_VALID[0] =  (slv_reg0[0] && (AR_HIGH_ADDR <=  slv_reg6[31:16]) && (M_AXI_ARADDR_wire[31:16] >= slv_reg6[15:0]) ) ? 1 : 0;
assign AR_ADDR_VALID[1] =  (slv_reg0[1] && (AR_HIGH_ADDR <=  slv_reg7[31:16]) && (M_AXI_ARADDR_wire[31:16] >= slv_reg7[15:0]) ) ? 1 : 0;
assign AR_ADDR_VALID[2] =  (slv_reg0[2] && (AR_HIGH_ADDR <=  slv_reg8[31:16]) && (M_AXI_ARADDR_wire[31:16] >= slv_reg8[15:0]) ) ? 1 : 0;
assign AR_ADDR_VALID[3] =  (slv_reg0[3] && (AR_HIGH_ADDR <=  slv_reg9[31:16]) && (M_AXI_ARADDR_wire[31:16] >= slv_reg9[15:0]) ) ? 1 : 0;
assign AR_ADDR_VALID[4] =  (slv_reg0[4] && (AR_HIGH_ADDR <=  slv_reg10[31:16]) && (M_AXI_ARADDR_wire[31:16] >= slv_reg10[15:0]) ) ? 1 : 0;
assign AR_ADDR_VALID[5] =  (slv_reg0[5] && (AR_HIGH_ADDR <=  slv_reg11[31:16]) && (M_AXI_ARADDR_wire[31:16] >= slv_reg11[15:0]) ) ? 1 : 0;
assign AR_ADDR_VALID[6] =  (slv_reg0[6] && (AR_HIGH_ADDR <=  slv_reg12[31:16]) && (M_AXI_ARADDR_wire[31:16] >= slv_reg12[15:0]) ) ? 1 : 0;
assign AR_ADDR_VALID[7] =  (slv_reg0[7] && (AR_HIGH_ADDR <=  slv_reg13[31:16]) && (M_AXI_ARADDR_wire[31:16] >= slv_reg13[15:0]) ) ? 1 : 0;
assign AR_ADDR_VALID[8] =  (slv_reg0[8] && (AR_HIGH_ADDR <=  slv_reg14[31:16]) && (M_AXI_ARADDR_wire[31:16] >= slv_reg14[15:0]) ) ? 1 : 0;
assign AR_ADDR_VALID[9] =  (slv_reg0[9] && (AR_HIGH_ADDR <=  slv_reg15[31:16]) && (M_AXI_ARADDR_wire[31:16] >= slv_reg15[15:0]) ) ? 1 : 0;
assign AR_ADDR_VALID[10] =  (slv_reg0[10] && (AR_HIGH_ADDR <=  slv_reg16[31:16]) && (M_AXI_ARADDR_wire[31:16] >= slv_reg16[15:0]) ) ? 1 : 0;
assign AR_ADDR_VALID[11] =  (slv_reg0[11] && (AR_HIGH_ADDR <=  slv_reg17[31:16]) && (M_AXI_ARADDR_wire[31:16] >= slv_reg17[15:0]) ) ? 1 : 0;
assign AR_ADDR_VALID[12] =  (slv_reg0[12] && (AR_HIGH_ADDR <=  slv_reg18[31:16]) && (M_AXI_ARADDR_wire[31:16] >= slv_reg18[15:0]) ) ? 1 : 0;
assign AR_ADDR_VALID[13] =  (slv_reg0[13] && (AR_HIGH_ADDR <=  slv_reg19[31:16]) && (M_AXI_ARADDR_wire[31:16] >= slv_reg19[15:0]) ) ? 1 : 0;
assign AR_ADDR_VALID[14] =  (slv_reg0[14] && (AR_HIGH_ADDR <=  slv_reg20[31:16]) && (M_AXI_ARADDR_wire[31:16] >= slv_reg20[15:0]) ) ? 1 : 0;
assign AR_ADDR_VALID[15] =  (slv_reg0[15] && (AR_HIGH_ADDR <=  slv_reg21[31:16]) && (M_AXI_ARADDR_wire[31:16] >= slv_reg21[15:0]) ) ? 1 : 0;

// ------------ OVERFLOW MANAGEMENT 04/29/2021 -----------------

//assign AR_ADDR_VALID_FLAG = |AR_ADDR_VALID;

assign AR_ADDR_VALID_FLAG = |AR_ADDR_VALID & ~AR_OVERFLOW_DETC;
assign AR_OVERFLOW_DETC = M_AXI_ARADDR_wire[C_M_AXI_ADDR_WIDTH-1] & ~AR_HIGH_ADDR[C_M_AXI_ADDR_WIDTH-1];

// -------------------------------------------------------------

always @(posedge ACLK)
begin
	if(ARESETN == 1'b0)
	   begin
	       AR_STATE <= 1'b0;
	       AR_ILLEGAL_REQ <= 0;
	       AR_ILL_TRANS_FIL_PTR <= 0;
	       M_AXI_ARID_INT <= 0;
	       M_AXI_ARADDR_INT <= 0;
	       M_AXI_ARLEN_INT <= 0;
	       M_AXI_ARSIZE_INT <= 0;
	       M_AXI_ARBURST_INT <= 0;
	       M_AXI_ARLOCK_INT <= 0;
	       M_AXI_ARCACHE_INT <= 0;
	       M_AXI_ARPROT_INT <= 0;
	       M_AXI_ARQOS_INT <= 0;
	       M_AXI_ARUSER_INT <= 0;
	       slv_reg2 <= 0;
	       slv_reg3 <= 0;
	   end
	else
	   begin
	       if(~AR_STATE)
		      begin
			     if( M_AXI_ARVALID_wire && M_AXI_ARREADY_wire)
				    begin
					   AR_STATE <= 1;
					   if(AR_ADDR_VALID_FLAG)
						  begin
							AR_ILLEGAL_REQ <= 1'b0;
							AR_ILL_TRANS[AR_ILL_TRANS_FIL_PTR] <= 1'b0;
							M_AXI_ARID_INT <= M_AXI_ARID_wire;
							M_AXI_ARADDR_INT <= M_AXI_ARADDR_wire;
							M_AXI_ARLEN_INT <= M_AXI_ARLEN_wire;
							M_AXI_ARSIZE_INT <= M_AXI_ARSIZE_wire;
							M_AXI_ARBURST_INT <= M_AXI_ARBURST_wire;
							M_AXI_ARLOCK_INT <= M_AXI_ARLOCK_wire;
							M_AXI_ARCACHE_INT <= M_AXI_ARCACHE_wire;
							M_AXI_ARPROT_INT <= M_AXI_ARPROT_wire;
							M_AXI_ARQOS_INT <= M_AXI_ARQOS_wire;
							M_AXI_ARUSER_INT <= M_AXI_ARUSER_wire;
						  end
			           else
				         begin
				            AR_ILLEGAL_REQ <= 1'b1;
						    AR_ILL_TRANS[AR_ILL_TRANS_FIL_PTR] <= 1'b1;
							slv_reg2 <= M_AXI_ARADDR_wire;
							slv_reg3[7:0] <= M_AXI_ARLEN_wire;
							slv_reg3[C_M_AXI_DATA_WIDTH - 1 : C_M_AXI_DATA_WIDTH - 1 - C_M_AXI_ID_WIDTH] <= M_AXI_ARID_wire;
							slv_reg3[C_M_AXI_DATA_WIDTH - 1 - C_M_AXI_ID_WIDTH - 1 : C_M_AXI_DATA_WIDTH - 1 - C_M_AXI_ID_WIDTH - 1 - 3] <= M_AXI_ARPROT_wire;
							slv_reg3[C_M_AXI_DATA_WIDTH - 1 - C_M_AXI_ID_WIDTH - 1 - 3 - 1 : C_M_AXI_DATA_WIDTH - 1 - C_M_AXI_ID_WIDTH - 1 - 3 - 1 - 3] <= M_AXI_ARCACHE_wire;
							slv_reg3[C_M_AXI_DATA_WIDTH - 1 - C_M_AXI_ID_WIDTH - 1 - 3 - 1 - 3 - 1 : C_M_AXI_DATA_WIDTH - 1 - C_M_AXI_ID_WIDTH - 1 - 3 - 1 - 3 - 1] <= M_AXI_ARLOCK_wire;
					     end
					   AR_ILL_TRANS_FIL_PTR <= AR_ILL_TRANS_FIL_PTR + 1;
		             end
			    end
            else
                begin
                    if( (AR_ILLEGAL_REQ == 1'b0 && M_AXI_ARREADY == 1'b1 ) || AR_ILLEGAL_REQ == 1'b1 )
                        begin
                            AR_STATE <= 1'b0;
                            AR_ILLEGAL_REQ <= 0;
                        end
                end
      end
end

assign M_AXI_RID_wire = ~R_STATE ? M_AXI_RID : 0;
assign M_AXI_RDATA_wire = ~R_STATE ? M_AXI_RDATA : 0;
assign M_AXI_RRESP_wire = ~R_STATE ? M_AXI_RRESP : 2'b11;
assign M_AXI_RLAST_wire = ~R_STATE ? M_AXI_RLAST : 1;
assign M_AXI_RUSER_wire = ~R_STATE ? M_AXI_RUSER : 0;
assign M_AXI_RVALID_wire = ~R_STATE ? M_AXI_RVALID : 1;
assign M_AXI_RREADY = ~R_STATE ? M_AXI_RREADY_wire : 0;

always @(posedge ACLK)
begin
	if(ARESETN == 1'b0)
	   begin
	       R_STATE <= 1'b0;
	       AR_ILL_TRANS_SRV_PTR <= 0;
	   end
	else
	   begin
	       if(~R_STATE)
		      begin
			     if(AR_STATE == 1'b1 && AR_ILL_TRANS[AR_ILL_TRANS_SRV_PTR] == 1'b1 )
				    begin
					   R_STATE <= 1'b1;
				    end
		      end
	       else
		      begin
			     if(M_AXI_RREADY_wire == 1'b1)
				    begin
					   R_STATE <= 0;
				    end
		      end
		    if(M_AXI_RREADY_wire == 1 && M_AXI_RVALID_wire == 1 && M_AXI_RLAST_wire == 1)
		      begin
		          AR_ILL_TRANS_SRV_PTR <= AR_ILL_TRANS_SRV_PTR + 1;
		      end
	    end
end

//------------------------ END ACCESS CONTROL READS MANAGEMENT ---------------------------------

endmodule

