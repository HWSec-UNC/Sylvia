module soc_interconnect (
	clk,
	rst_n,
	test_en_i,
	L2_D_o,
	L2_A_o,
	L2_CEN_o,
	L2_WEN_o,
	L2_BE_o,
	L2_ID_o,
	L2_Q_i,
	FC_DATA_req_i,
	FC_DATA_add_i,
	FC_DATA_wen_i,
	FC_DATA_wdata_i,
	FC_DATA_be_i,
	FC_DATA_aux_i,
	FC_DATA_gnt_o,
	FC_DATA_r_aux_o,
	FC_DATA_r_valid_o,
	FC_DATA_r_rdata_o,
	FC_DATA_r_opc_o,
	FC_INSTR_req_i,
	FC_INSTR_add_i,
	FC_INSTR_wen_i,
	FC_INSTR_wdata_i,
	FC_INSTR_be_i,
	FC_INSTR_aux_i,
	FC_INSTR_gnt_o,
	FC_INSTR_r_aux_o,
	FC_INSTR_r_valid_o,
	FC_INSTR_r_rdata_o,
	FC_INSTR_r_opc_o,
	UDMA_TX_req_i,
	UDMA_TX_add_i,
	UDMA_TX_wen_i,
	UDMA_TX_wdata_i,
	UDMA_TX_be_i,
	UDMA_TX_aux_i,
	UDMA_TX_gnt_o,
	UDMA_TX_r_aux_o,
	UDMA_TX_r_valid_o,
	UDMA_TX_r_rdata_o,
	UDMA_TX_r_opc_o,
	UDMA_RX_req_i,
	UDMA_RX_add_i,
	UDMA_RX_wen_i,
	UDMA_RX_wdata_i,
	UDMA_RX_be_i,
	UDMA_RX_aux_i,
	UDMA_RX_gnt_o,
	UDMA_RX_r_aux_o,
	UDMA_RX_r_valid_o,
	UDMA_RX_r_rdata_o,
	UDMA_RX_r_opc_o,
	DBG_RX_req_i,
	DBG_RX_add_i,
	DBG_RX_wen_i,
	DBG_RX_wdata_i,
	DBG_RX_be_i,
	DBG_RX_aux_i,
	DBG_RX_gnt_o,
	DBG_RX_r_aux_o,
	DBG_RX_r_valid_o,
	DBG_RX_r_rdata_o,
	DBG_RX_r_opc_o,
	HWPE_req_i,
	HWPE_add_i,
	HWPE_wen_i,
	HWPE_wdata_i,
	HWPE_be_i,
	HWPE_aux_i,
	HWPE_gnt_o,
	HWPE_r_aux_o,
	HWPE_r_valid_o,
	HWPE_r_rdata_o,
	HWPE_r_opc_o,
	AXI_Slave_aw_addr_i,
	AXI_Slave_aw_prot_i,
	AXI_Slave_aw_region_i,
	AXI_Slave_aw_len_i,
	AXI_Slave_aw_size_i,
	AXI_Slave_aw_burst_i,
	AXI_Slave_aw_lock_i,
	AXI_Slave_aw_cache_i,
	AXI_Slave_aw_qos_i,
	AXI_Slave_aw_id_i,
	AXI_Slave_aw_user_i,
	AXI_Slave_aw_valid_i,
	AXI_Slave_aw_ready_o,
	AXI_Slave_ar_addr_i,
	AXI_Slave_ar_prot_i,
	AXI_Slave_ar_region_i,
	AXI_Slave_ar_len_i,
	AXI_Slave_ar_size_i,
	AXI_Slave_ar_burst_i,
	AXI_Slave_ar_lock_i,
	AXI_Slave_ar_cache_i,
	AXI_Slave_ar_qos_i,
	AXI_Slave_ar_id_i,
	AXI_Slave_ar_user_i,
	AXI_Slave_ar_valid_i,
	AXI_Slave_ar_ready_o,
	AXI_Slave_w_user_i,
	AXI_Slave_w_data_i,
	AXI_Slave_w_strb_i,
	AXI_Slave_w_last_i,
	AXI_Slave_w_valid_i,
	AXI_Slave_w_ready_o,
	AXI_Slave_b_id_o,
	AXI_Slave_b_resp_o,
	AXI_Slave_b_user_o,
	AXI_Slave_b_valid_o,
	AXI_Slave_b_ready_i,
	AXI_Slave_r_id_o,
	AXI_Slave_r_user_o,
	AXI_Slave_r_data_o,
	AXI_Slave_r_resp_o,
	AXI_Slave_r_last_o,
	AXI_Slave_r_valid_o,
	AXI_Slave_r_ready_i,
	APB_PADDR_o,
	APB_PWDATA_o,
	APB_PWRITE_o,
	APB_PSEL_o,
	APB_PENABLE_o,
	APB_PRDATA_i,
	APB_PREADY_i,
	APB_PSLVERR_i,
	AXI_Master_aw_id_o,
	AXI_Master_aw_addr_o,
	AXI_Master_aw_len_o,
	AXI_Master_aw_size_o,
	AXI_Master_aw_burst_o,
	AXI_Master_aw_lock_o,
	AXI_Master_aw_cache_o,
	AXI_Master_aw_prot_o,
	AXI_Master_aw_region_o,
	AXI_Master_aw_user_o,
	AXI_Master_aw_qos_o,
	AXI_Master_aw_valid_o,
	AXI_Master_aw_ready_i,
	AXI_Master_w_data_o,
	AXI_Master_w_strb_o,
	AXI_Master_w_last_o,
	AXI_Master_w_user_o,
	AXI_Master_w_valid_o,
	AXI_Master_w_ready_i,
	AXI_Master_b_id_i,
	AXI_Master_b_resp_i,
	AXI_Master_b_valid_i,
	AXI_Master_b_user_i,
	AXI_Master_b_ready_o,
	AXI_Master_ar_id_o,
	AXI_Master_ar_addr_o,
	AXI_Master_ar_len_o,
	AXI_Master_ar_size_o,
	AXI_Master_ar_burst_o,
	AXI_Master_ar_lock_o,
	AXI_Master_ar_cache_o,
	AXI_Master_ar_prot_o,
	AXI_Master_ar_region_o,
	AXI_Master_ar_user_o,
	AXI_Master_ar_qos_o,
	AXI_Master_ar_valid_o,
	AXI_Master_ar_ready_i,
	AXI_Master_r_id_i,
	AXI_Master_r_data_i,
	AXI_Master_r_resp_i,
	AXI_Master_r_last_i,
	AXI_Master_r_user_i,
	AXI_Master_r_valid_i,
	AXI_Master_r_ready_o,
	rom_csn_o,
	rom_add_o,
	rom_rdata_i,
	L2_pri_D_o,
	L2_pri_A_o,
	L2_pri_CEN_o,
	L2_pri_WEN_o,
	L2_pri_BE_o,
	L2_pri_Q_i
);
	parameter USE_AXI = 1;
	parameter ADDR_WIDTH = 32;
	parameter N_HWPE_PORTS = 4;
	parameter N_MASTER_32 = 5 + N_HWPE_PORTS;
	parameter N_MASTER_AXI_64 = 1;
	parameter DATA_WIDTH = 32;
	parameter BE_WIDTH = DATA_WIDTH / 8;
	parameter ID_WIDTH = N_MASTER_32 + (N_MASTER_AXI_64 * 4);
	parameter AUX_WIDTH = 8;
	parameter N_L2_BANKS = 4;
	parameter N_L2_BANKS_PRI = 2;
	parameter ADDR_L2_WIDTH = 12;
	parameter ADDR_L2_PRI_WIDTH = 12;
	parameter ROM_ADDR_WIDTH = 10;
	parameter AXI_32_ID_WIDTH = 12;
	parameter AXI_32_USER_WIDTH = 6;
	parameter AXI_ADDR_WIDTH = 32;
	parameter AXI_DATA_WIDTH = 64;
	parameter AXI_STRB_WIDTH = 8;
	parameter AXI_USER_WIDTH = 6;
	parameter AXI_ID_WIDTH = 7;
	input wire clk;
	input wire rst_n;
	input wire test_en_i;
	output reg [(N_L2_BANKS * DATA_WIDTH) - 1:0] L2_D_o;
	output reg [(N_L2_BANKS * ADDR_L2_WIDTH) - 1:0] L2_A_o;
	output reg [N_L2_BANKS - 1:0] L2_CEN_o;
	output reg [N_L2_BANKS - 1:0] L2_WEN_o;
	output reg [(N_L2_BANKS * BE_WIDTH) - 1:0] L2_BE_o;
	output reg [(N_L2_BANKS * 32) - 1:0] L2_ID_o;
	input wire [(N_L2_BANKS * DATA_WIDTH) - 1:0] L2_Q_i;
	input wire FC_DATA_req_i;
	input wire [ADDR_WIDTH - 1:0] FC_DATA_add_i;
	input wire FC_DATA_wen_i;
	input wire [DATA_WIDTH - 1:0] FC_DATA_wdata_i;
	input wire [BE_WIDTH - 1:0] FC_DATA_be_i;
	input wire [AUX_WIDTH - 1:0] FC_DATA_aux_i;
	output wire FC_DATA_gnt_o;
	output wire [AUX_WIDTH - 1:0] FC_DATA_r_aux_o;
	output wire FC_DATA_r_valid_o;
	output wire [DATA_WIDTH - 1:0] FC_DATA_r_rdata_o;
	output wire FC_DATA_r_opc_o;
	input wire FC_INSTR_req_i;
	input wire [ADDR_WIDTH - 1:0] FC_INSTR_add_i;
	input wire FC_INSTR_wen_i;
	input wire [DATA_WIDTH - 1:0] FC_INSTR_wdata_i;
	input wire [BE_WIDTH - 1:0] FC_INSTR_be_i;
	input wire [AUX_WIDTH - 1:0] FC_INSTR_aux_i;
	output wire FC_INSTR_gnt_o;
	output wire [AUX_WIDTH - 1:0] FC_INSTR_r_aux_o;
	output wire FC_INSTR_r_valid_o;
	output wire [DATA_WIDTH - 1:0] FC_INSTR_r_rdata_o;
	output wire FC_INSTR_r_opc_o;
	input wire UDMA_TX_req_i;
	input wire [ADDR_WIDTH - 1:0] UDMA_TX_add_i;
	input wire UDMA_TX_wen_i;
	input wire [DATA_WIDTH - 1:0] UDMA_TX_wdata_i;
	input wire [BE_WIDTH - 1:0] UDMA_TX_be_i;
	input wire [AUX_WIDTH - 1:0] UDMA_TX_aux_i;
	output wire UDMA_TX_gnt_o;
	output wire [AUX_WIDTH - 1:0] UDMA_TX_r_aux_o;
	output wire UDMA_TX_r_valid_o;
	output wire [DATA_WIDTH - 1:0] UDMA_TX_r_rdata_o;
	output wire UDMA_TX_r_opc_o;
	input wire UDMA_RX_req_i;
	input wire [ADDR_WIDTH - 1:0] UDMA_RX_add_i;
	input wire UDMA_RX_wen_i;
	input wire [DATA_WIDTH - 1:0] UDMA_RX_wdata_i;
	input wire [BE_WIDTH - 1:0] UDMA_RX_be_i;
	input wire [AUX_WIDTH - 1:0] UDMA_RX_aux_i;
	output wire UDMA_RX_gnt_o;
	output wire [AUX_WIDTH - 1:0] UDMA_RX_r_aux_o;
	output wire UDMA_RX_r_valid_o;
	output wire [DATA_WIDTH - 1:0] UDMA_RX_r_rdata_o;
	output wire UDMA_RX_r_opc_o;
	input wire DBG_RX_req_i;
	input wire [ADDR_WIDTH - 1:0] DBG_RX_add_i;
	input wire DBG_RX_wen_i;
	input wire [DATA_WIDTH - 1:0] DBG_RX_wdata_i;
	input wire [BE_WIDTH - 1:0] DBG_RX_be_i;
	input wire [AUX_WIDTH - 1:0] DBG_RX_aux_i;
	output wire DBG_RX_gnt_o;
	output wire [AUX_WIDTH - 1:0] DBG_RX_r_aux_o;
	output wire DBG_RX_r_valid_o;
	output wire [DATA_WIDTH - 1:0] DBG_RX_r_rdata_o;
	output wire DBG_RX_r_opc_o;
	input wire [N_HWPE_PORTS - 1:0] HWPE_req_i;
	input wire [(N_HWPE_PORTS * ADDR_WIDTH) - 1:0] HWPE_add_i;
	input wire [N_HWPE_PORTS - 1:0] HWPE_wen_i;
	input wire [(N_HWPE_PORTS * DATA_WIDTH) - 1:0] HWPE_wdata_i;
	input wire [(N_HWPE_PORTS * BE_WIDTH) - 1:0] HWPE_be_i;
	input wire [(N_HWPE_PORTS * AUX_WIDTH) - 1:0] HWPE_aux_i;
	output wire [N_HWPE_PORTS - 1:0] HWPE_gnt_o;
	output wire [(N_HWPE_PORTS * AUX_WIDTH) - 1:0] HWPE_r_aux_o;
	output wire [N_HWPE_PORTS - 1:0] HWPE_r_valid_o;
	output wire [(N_HWPE_PORTS * DATA_WIDTH) - 1:0] HWPE_r_rdata_o;
	output wire [N_HWPE_PORTS - 1:0] HWPE_r_opc_o;
	input wire [AXI_ADDR_WIDTH - 1:0] AXI_Slave_aw_addr_i;
	input wire [2:0] AXI_Slave_aw_prot_i;
	input wire [3:0] AXI_Slave_aw_region_i;
	input wire [7:0] AXI_Slave_aw_len_i;
	input wire [2:0] AXI_Slave_aw_size_i;
	input wire [1:0] AXI_Slave_aw_burst_i;
	input wire AXI_Slave_aw_lock_i;
	input wire [3:0] AXI_Slave_aw_cache_i;
	input wire [3:0] AXI_Slave_aw_qos_i;
	input wire [AXI_ID_WIDTH - 1:0] AXI_Slave_aw_id_i;
	input wire [AXI_USER_WIDTH - 1:0] AXI_Slave_aw_user_i;
	input wire AXI_Slave_aw_valid_i;
	output wire AXI_Slave_aw_ready_o;
	input wire [AXI_ADDR_WIDTH - 1:0] AXI_Slave_ar_addr_i;
	input wire [2:0] AXI_Slave_ar_prot_i;
	input wire [3:0] AXI_Slave_ar_region_i;
	input wire [7:0] AXI_Slave_ar_len_i;
	input wire [2:0] AXI_Slave_ar_size_i;
	input wire [1:0] AXI_Slave_ar_burst_i;
	input wire AXI_Slave_ar_lock_i;
	input wire [3:0] AXI_Slave_ar_cache_i;
	input wire [3:0] AXI_Slave_ar_qos_i;
	input wire [AXI_ID_WIDTH - 1:0] AXI_Slave_ar_id_i;
	input wire [AXI_USER_WIDTH - 1:0] AXI_Slave_ar_user_i;
	input wire AXI_Slave_ar_valid_i;
	output wire AXI_Slave_ar_ready_o;
	input wire [AXI_USER_WIDTH - 1:0] AXI_Slave_w_user_i;
	input wire [AXI_DATA_WIDTH - 1:0] AXI_Slave_w_data_i;
	input wire [AXI_STRB_WIDTH - 1:0] AXI_Slave_w_strb_i;
	input wire AXI_Slave_w_last_i;
	input wire AXI_Slave_w_valid_i;
	output wire AXI_Slave_w_ready_o;
	output wire [AXI_ID_WIDTH - 1:0] AXI_Slave_b_id_o;
	output wire [1:0] AXI_Slave_b_resp_o;
	output wire [AXI_USER_WIDTH - 1:0] AXI_Slave_b_user_o;
	output wire AXI_Slave_b_valid_o;
	input wire AXI_Slave_b_ready_i;
	output wire [AXI_ID_WIDTH - 1:0] AXI_Slave_r_id_o;
	output wire [AXI_USER_WIDTH - 1:0] AXI_Slave_r_user_o;
	output wire [AXI_DATA_WIDTH - 1:0] AXI_Slave_r_data_o;
	output wire [1:0] AXI_Slave_r_resp_o;
	output wire AXI_Slave_r_last_o;
	output wire AXI_Slave_r_valid_o;
	input wire AXI_Slave_r_ready_i;
	output wire [ADDR_WIDTH - 1:0] APB_PADDR_o;
	output wire [DATA_WIDTH - 1:0] APB_PWDATA_o;
	output wire APB_PWRITE_o;
	output wire APB_PSEL_o;
	output wire APB_PENABLE_o;
	input wire [DATA_WIDTH - 1:0] APB_PRDATA_i;
	input wire APB_PREADY_i;
	input wire APB_PSLVERR_i;
	output wire [AXI_32_ID_WIDTH - 1:0] AXI_Master_aw_id_o;
	output wire [ADDR_WIDTH - 1:0] AXI_Master_aw_addr_o;
	output wire [7:0] AXI_Master_aw_len_o;
	output wire [2:0] AXI_Master_aw_size_o;
	output wire [1:0] AXI_Master_aw_burst_o;
	output wire AXI_Master_aw_lock_o;
	output wire [3:0] AXI_Master_aw_cache_o;
	output wire [2:0] AXI_Master_aw_prot_o;
	output wire [3:0] AXI_Master_aw_region_o;
	output wire [AXI_32_USER_WIDTH - 1:0] AXI_Master_aw_user_o;
	output wire [3:0] AXI_Master_aw_qos_o;
	output wire AXI_Master_aw_valid_o;
	input wire AXI_Master_aw_ready_i;
	output wire [DATA_WIDTH - 1:0] AXI_Master_w_data_o;
	output wire [BE_WIDTH - 1:0] AXI_Master_w_strb_o;
	output wire AXI_Master_w_last_o;
	output wire [AXI_32_USER_WIDTH - 1:0] AXI_Master_w_user_o;
	output wire AXI_Master_w_valid_o;
	input wire AXI_Master_w_ready_i;
	input wire [AXI_32_ID_WIDTH - 1:0] AXI_Master_b_id_i;
	input wire [1:0] AXI_Master_b_resp_i;
	input wire AXI_Master_b_valid_i;
	input wire [AXI_32_USER_WIDTH - 1:0] AXI_Master_b_user_i;
	output wire AXI_Master_b_ready_o;
	output wire [AXI_32_ID_WIDTH - 1:0] AXI_Master_ar_id_o;
	output wire [ADDR_WIDTH - 1:0] AXI_Master_ar_addr_o;
	output wire [7:0] AXI_Master_ar_len_o;
	output wire [2:0] AXI_Master_ar_size_o;
	output wire [1:0] AXI_Master_ar_burst_o;
	output wire AXI_Master_ar_lock_o;
	output wire [3:0] AXI_Master_ar_cache_o;
	output wire [2:0] AXI_Master_ar_prot_o;
	output wire [3:0] AXI_Master_ar_region_o;
	output wire [AXI_32_USER_WIDTH - 1:0] AXI_Master_ar_user_o;
	output wire [3:0] AXI_Master_ar_qos_o;
	output wire AXI_Master_ar_valid_o;
	input wire AXI_Master_ar_ready_i;
	input wire [AXI_32_ID_WIDTH - 1:0] AXI_Master_r_id_i;
	input wire [DATA_WIDTH - 1:0] AXI_Master_r_data_i;
	input wire [1:0] AXI_Master_r_resp_i;
	input wire AXI_Master_r_last_i;
	input wire [AXI_32_USER_WIDTH - 1:0] AXI_Master_r_user_i;
	input wire AXI_Master_r_valid_i;
	output wire AXI_Master_r_ready_o;
	output wire rom_csn_o;
	output wire [ROM_ADDR_WIDTH - 1:0] rom_add_o;
	input wire [DATA_WIDTH - 1:0] rom_rdata_i;
	output wire [(N_L2_BANKS_PRI * DATA_WIDTH) - 1:0] L2_pri_D_o;
	output wire [(N_L2_BANKS_PRI * ADDR_L2_PRI_WIDTH) - 1:0] L2_pri_A_o;
	output wire [N_L2_BANKS_PRI - 1:0] L2_pri_CEN_o;
	output wire [N_L2_BANKS_PRI - 1:0] L2_pri_WEN_o;
	output wire [(N_L2_BANKS_PRI * BE_WIDTH) - 1:0] L2_pri_BE_o;
	input wire [(N_L2_BANKS_PRI * DATA_WIDTH) - 1:0] L2_pri_Q_i;
	localparam N_CH0 = N_MASTER_32;
	localparam N_CH1 = N_MASTER_AXI_64 * 4;
	localparam N_CH0_BRIDGE = N_CH0;
	localparam N_CH1_BRIDGE = N_CH1;
	localparam PER_ID_WIDTH = N_CH0_BRIDGE + N_CH1_BRIDGE;
	localparam N_PERIPHS = 3 + N_L2_BANKS_PRI;
	localparam L2_OFFSET_PRI = 15'h1000;
	localparam [(N_PERIPHS * ADDR_WIDTH) - 1:0] PER_START_ADDR = 160'h1c0080001c0000001a000000100000001a100000;
	localparam [(N_PERIPHS * ADDR_WIDTH) - 1:0] PER_END_ADDR = 160'h1c0100001c0080001a040000104000001a200000;
	localparam [ADDR_WIDTH - 1:0] TCDM_START_ADDR = 32'h1c010000;
	localparam [ADDR_WIDTH - 1:0] TCDM_END_ADDR = 32'h1c082000;
	wire [N_MASTER_32 - 1:0] FC_data_req_INT_32;
	wire [(N_MASTER_32 * ADDR_WIDTH) - 1:0] FC_data_add_INT_32;
	reg [ADDR_WIDTH - 1:0] FC_DATA_add_int;
	wire [N_MASTER_32 - 1:0] FC_data_wen_INT_32;
	wire [(N_MASTER_32 * DATA_WIDTH) - 1:0] FC_data_wdata_INT_32;
	wire [(N_MASTER_32 * BE_WIDTH) - 1:0] FC_data_be_INT_32;
	wire [(N_MASTER_32 * AUX_WIDTH) - 1:0] FC_data_aux_INT_32;
	wire [N_MASTER_32 - 1:0] FC_data_gnt_INT_32;
	wire [(N_MASTER_32 * AUX_WIDTH) - 1:0] FC_data_r_aux_INT_32;
	wire [N_MASTER_32 - 1:0] FC_data_r_valid_INT_32;
	wire [(N_MASTER_32 * DATA_WIDTH) - 1:0] FC_data_r_rdata_INT_32;
	wire [N_MASTER_32 - 1:0] FC_data_r_opc_INT_32;
	wire [(N_MASTER_AXI_64 * 4) - 1:0] AXI_data_req_INT_64;
	wire [((N_MASTER_AXI_64 * 4) * ADDR_WIDTH) - 1:0] AXI_data_add_INT_64;
	wire [(N_MASTER_AXI_64 * 4) - 1:0] AXI_data_wen_INT_64;
	wire [((N_MASTER_AXI_64 * 4) * DATA_WIDTH) - 1:0] AXI_data_wdata_INT_64;
	wire [((N_MASTER_AXI_64 * 4) * BE_WIDTH) - 1:0] AXI_data_be_INT_64;
	wire [((N_MASTER_AXI_64 * 4) * AUX_WIDTH) - 1:0] AXI_data_aux_INT_64;
	wire [(N_MASTER_AXI_64 * 4) - 1:0] AXI_data_gnt_INT_64;
	wire [((N_MASTER_AXI_64 * 4) * AUX_WIDTH) - 1:0] AXI_data_r_aux_INT_64;
	wire [(N_MASTER_AXI_64 * 4) - 1:0] AXI_data_r_valid_INT_64;
	wire [((N_MASTER_AXI_64 * 4) * DATA_WIDTH) - 1:0] AXI_data_r_rdata_INT_64;
	wire [(N_MASTER_AXI_64 * 4) - 1:0] AXI_data_r_opc_INT_64;
	wire [(N_CH0 + N_CH1) - 1:0] PER_data_req_DEM_2_L2_XBAR;
	wire [((N_CH0 + N_CH1) * ADDR_WIDTH) - 1:0] PER_data_add_DEM_2_L2_XBAR;
	wire [(N_CH0 + N_CH1) - 1:0] PER_data_wen_DEM_2_L2_XBAR;
	wire [((N_CH0 + N_CH1) * DATA_WIDTH) - 1:0] PER_data_wdata_DEM_2_L2_XBAR;
	wire [((N_CH0 + N_CH1) * BE_WIDTH) - 1:0] PER_data_be_DEM_2_L2_XBAR;
	wire [((N_CH0 + N_CH1) * AUX_WIDTH) - 1:0] PER_data_aux_DEM_2_L2_XBAR;
	wire [(N_CH0 + N_CH1) - 1:0] PER_data_gnt_DEM_2_L2_XBAR;
	wire [(N_CH0 + N_CH1) - 1:0] PER_data_r_valid_DEM_2_L2_XBAR;
	wire [((N_CH0 + N_CH1) * DATA_WIDTH) - 1:0] PER_data_r_rdata_DEM_2_L2_XBAR;
	wire [(N_CH0 + N_CH1) - 1:0] PER_data_r_opc_DEM_2_L2_XBAR;
	wire [((N_CH0 + N_CH1) * AUX_WIDTH) - 1:0] PER_data_r_aux_DEM_2_L2_XBAR;
	wire [N_PERIPHS - 1:0] PER_data_req_TO_BRIDGE;
	wire [(N_PERIPHS * ADDR_WIDTH) - 1:0] PER_data_add_TO_BRIDGE;
	wire [N_PERIPHS - 1:0] PER_data_wen_TO_BRIDGE;
	wire [(N_PERIPHS * DATA_WIDTH) - 1:0] PER_data_wdata_TO_BRIDGE;
	wire [(N_PERIPHS * BE_WIDTH) - 1:0] PER_data_be_TO_BRIDGE;
	wire [(N_PERIPHS * PER_ID_WIDTH) - 1:0] PER_data_ID_TO_BRIDGE;
	wire [(N_PERIPHS * AUX_WIDTH) - 1:0] PER_data_aux_TO_BRIDGE;
	wire [N_PERIPHS - 1:0] PER_data_gnt_TO_BRIDGE;
	wire [(N_PERIPHS * DATA_WIDTH) - 1:0] PER_data_r_rdata_TO_BRIDGE;
	reg [N_PERIPHS - 1:0] PER_data_r_valid_TO_BRIDGE;
	reg [(N_PERIPHS * PER_ID_WIDTH) - 1:0] PER_data_r_ID_TO_BRIDGE;
	reg [N_PERIPHS - 1:0] PER_data_r_opc_TO_BRIDGE;
	reg [(N_PERIPHS * AUX_WIDTH) - 1:0] PER_data_r_aux_TO_BRIDGE;
	wire [((N_CH0 + N_CH1) * DATA_WIDTH) - 1:0] TCDM_data_wdata_DEM_TO_XBAR;
	wire [((N_CH0 + N_CH1) * ADDR_WIDTH) - 1:0] TCDM_data_add_DEM_TO_XBAR;
	wire [((N_CH0 + N_CH1) * (ADDR_L2_WIDTH + $clog2(N_L2_BANKS))) - 1:0] TCDM_data_add_DEM_TO_XBAR_resized;
	wire [(N_CH0 + N_CH1) - 1:0] TCDM_data_req_DEM_TO_XBAR;
	wire [(N_CH0 + N_CH1) - 1:0] TCDM_data_wen_DEM_TO_XBAR;
	wire [((N_CH0 + N_CH1) * BE_WIDTH) - 1:0] TCDM_data_be_DEM_TO_XBAR;
	wire [(N_CH0 + N_CH1) - 1:0] TCDM_data_gnt_DEM_TO_XBAR;
	wire [((N_CH0 + N_CH1) * DATA_WIDTH) - 1:0] TCDM_data_r_rdata_DEM_TO_XBAR;
	wire [(N_CH0 + N_CH1) - 1:0] TCDM_data_r_valid_DEM_TO_XBAR;
	wire [(N_L2_BANKS * DATA_WIDTH) - 1:0] TCDM_data_wdata_TO_MEM;
	wire [(N_L2_BANKS * ADDR_L2_WIDTH) - 1:0] TCDM_data_add_TO_MEM;
	wire [N_L2_BANKS - 1:0] TCDM_data_req_TO_MEM;
	wire [N_L2_BANKS - 1:0] TCDM_data_wen_TO_MEM;
	wire [(N_L2_BANKS * BE_WIDTH) - 1:0] TCDM_data_be_TO_MEM;
	wire [(N_L2_BANKS * ID_WIDTH) - 1:0] TCDM_data_ID_TO_MEM;
	reg [(N_L2_BANKS * DATA_WIDTH) - 1:0] TCDM_data_rdata_TO_MEM;
	reg [N_L2_BANKS - 1:0] TCDM_data_rvalid_TO_MEM;
	reg [(N_L2_BANKS * ID_WIDTH) - 1:0] TCDM_data_rID_TO_MEM;
	assign rom_csn_o = ~PER_data_req_TO_BRIDGE[2];
	assign rom_add_o = PER_data_add_TO_BRIDGE[2 * ADDR_WIDTH+:ADDR_WIDTH];
	assign PER_data_r_rdata_TO_BRIDGE[2 * DATA_WIDTH+:DATA_WIDTH] = rom_rdata_i;
	assign PER_data_gnt_TO_BRIDGE[2] = 1'b1;
	always @(posedge clk or negedge rst_n) begin : proc_
		if (~rst_n)
			PER_data_r_valid_TO_BRIDGE[2] <= 1'sb0;
		else begin
			PER_data_r_ID_TO_BRIDGE[2 * PER_ID_WIDTH+:PER_ID_WIDTH] <= PER_data_ID_TO_BRIDGE[2 * PER_ID_WIDTH+:PER_ID_WIDTH];
			PER_data_r_valid_TO_BRIDGE[2] <= PER_data_req_TO_BRIDGE[2];
			PER_data_r_aux_TO_BRIDGE[2 * AUX_WIDTH+:AUX_WIDTH] <= PER_data_aux_TO_BRIDGE[2 * AUX_WIDTH+:AUX_WIDTH];
			PER_data_r_opc_TO_BRIDGE[2] <= 1'b0;
		end
	end
	genvar k;
	generate
		for (k = 0; k < N_L2_BANKS_PRI; k = k + 1) begin : genblk1
			assign L2_pri_D_o[k * DATA_WIDTH+:DATA_WIDTH] = PER_data_wdata_TO_BRIDGE[(k + 3) * DATA_WIDTH+:DATA_WIDTH];
			assign L2_pri_A_o[k * ADDR_L2_PRI_WIDTH+:ADDR_L2_PRI_WIDTH] = PER_data_add_TO_BRIDGE[((k + 3) * ADDR_WIDTH) + ((ADDR_L2_PRI_WIDTH + 1) >= 2 ? ADDR_L2_PRI_WIDTH + 1 : ((ADDR_L2_PRI_WIDTH + 1) + ((ADDR_L2_PRI_WIDTH + 1) >= 2 ? ADDR_L2_PRI_WIDTH : 3 - (ADDR_L2_PRI_WIDTH + 1))) - 1)-:((ADDR_L2_PRI_WIDTH + 1) >= 2 ? ADDR_L2_PRI_WIDTH : 3 - (ADDR_L2_PRI_WIDTH + 1))];
			assign L2_pri_CEN_o[k] = ~PER_data_req_TO_BRIDGE[k + 3];
			assign L2_pri_WEN_o[k] = PER_data_wen_TO_BRIDGE[k + 3];
			assign L2_pri_BE_o[k * BE_WIDTH+:BE_WIDTH] = PER_data_be_TO_BRIDGE[(k + 3) * BE_WIDTH+:BE_WIDTH];
			assign PER_data_r_rdata_TO_BRIDGE[(k + 3) * DATA_WIDTH+:DATA_WIDTH] = L2_pri_Q_i[k * DATA_WIDTH+:DATA_WIDTH];
			assign PER_data_gnt_TO_BRIDGE[k + 3] = 1'b1;
			wire [1:1] sv2v_tmp_F9248;
			assign sv2v_tmp_F9248 = 1'sb0;
			always @(*) PER_data_r_opc_TO_BRIDGE[k + 3] = sv2v_tmp_F9248;
			always @(posedge clk or negedge rst_n) begin : proc_L2_CH_pri_rvalid_gen
				if (~rst_n) begin
					PER_data_r_valid_TO_BRIDGE[k + 3] <= 1'sb0;
					PER_data_r_ID_TO_BRIDGE[(k + 3) * PER_ID_WIDTH+:PER_ID_WIDTH] <= 1'sb0;
					PER_data_r_aux_TO_BRIDGE[(k + 3) * AUX_WIDTH+:AUX_WIDTH] <= 1'sb0;
				end
				else begin
					PER_data_r_valid_TO_BRIDGE[k + 3] <= PER_data_req_TO_BRIDGE[k + 3];
					PER_data_r_ID_TO_BRIDGE[(k + 3) * PER_ID_WIDTH+:PER_ID_WIDTH] <= PER_data_ID_TO_BRIDGE[(k + 3) * PER_ID_WIDTH+:PER_ID_WIDTH];
					PER_data_r_aux_TO_BRIDGE[(k + 3) * AUX_WIDTH+:AUX_WIDTH] <= PER_data_aux_TO_BRIDGE[(k + 3) * AUX_WIDTH+:AUX_WIDTH];
				end
			end
		end
	endgenerate
	always @(*) begin
		FC_DATA_add_int = FC_DATA_add_i;
		if (FC_DATA_add_i[31:20] == 12'h000)
			FC_DATA_add_int[31:20] = 12'h1c0;
	end
	assign FC_data_req_INT_32 = {FC_INSTR_req_i, UDMA_TX_req_i, UDMA_RX_req_i, DBG_RX_req_i, FC_DATA_req_i};
	assign FC_data_add_INT_32 = {FC_INSTR_add_i, UDMA_TX_add_i, UDMA_RX_add_i, DBG_RX_add_i, FC_DATA_add_int};
	assign FC_data_wen_INT_32 = {FC_INSTR_wen_i, UDMA_TX_wen_i, UDMA_RX_wen_i, DBG_RX_wen_i, FC_DATA_wen_i};
	assign FC_data_wdata_INT_32 = {FC_INSTR_wdata_i, UDMA_TX_wdata_i, UDMA_RX_wdata_i, DBG_RX_wdata_i, FC_DATA_wdata_i};
	assign FC_data_be_INT_32 = {FC_INSTR_be_i, UDMA_TX_be_i, UDMA_RX_be_i, DBG_RX_be_i, FC_DATA_be_i};
	assign FC_data_aux_INT_32 = {FC_INSTR_aux_i, UDMA_TX_aux_i, UDMA_RX_aux_i, DBG_RX_aux_i, FC_DATA_aux_i};
	assign {FC_INSTR_gnt_o, UDMA_TX_gnt_o, UDMA_RX_gnt_o, DBG_RX_gnt_o, FC_DATA_gnt_o} = FC_data_gnt_INT_32;
	assign {FC_INSTR_r_aux_o, UDMA_TX_r_aux_o, UDMA_RX_r_aux_o, DBG_RX_r_aux_o, FC_DATA_r_aux_o} = FC_data_r_aux_INT_32;
	assign {FC_INSTR_r_valid_o, UDMA_TX_r_valid_o, UDMA_RX_r_valid_o, DBG_RX_r_valid_o, FC_DATA_r_valid_o} = FC_data_r_valid_INT_32;
	assign {FC_INSTR_r_rdata_o, UDMA_TX_r_rdata_o, UDMA_RX_r_rdata_o, DBG_RX_r_rdata_o, FC_DATA_r_rdata_o} = FC_data_r_rdata_INT_32;
	assign {FC_INSTR_r_opc_o, UDMA_TX_r_opc_o, UDMA_RX_r_opc_o, DBG_RX_r_opc_o, FC_DATA_r_opc_o} = FC_data_r_opc_INT_32;
	assign TCDM_data_req_DEM_TO_XBAR[N_CH0 - 1:N_CH0 - N_HWPE_PORTS] = HWPE_req_i;
	assign TCDM_data_add_DEM_TO_XBAR[ADDR_WIDTH * (((N_CH0 - 1) >= (N_CH0 - N_HWPE_PORTS) ? N_CH0 - 1 : ((N_CH0 - 1) + ((N_CH0 - 1) >= (N_CH0 - N_HWPE_PORTS) ? ((N_CH0 - 1) - (N_CH0 - N_HWPE_PORTS)) + 1 : ((N_CH0 - N_HWPE_PORTS) - (N_CH0 - 1)) + 1)) - 1) - (((N_CH0 - 1) >= (N_CH0 - N_HWPE_PORTS) ? ((N_CH0 - 1) - (N_CH0 - N_HWPE_PORTS)) + 1 : ((N_CH0 - N_HWPE_PORTS) - (N_CH0 - 1)) + 1) - 1))+:ADDR_WIDTH * ((N_CH0 - 1) >= (N_CH0 - N_HWPE_PORTS) ? ((N_CH0 - 1) - (N_CH0 - N_HWPE_PORTS)) + 1 : ((N_CH0 - N_HWPE_PORTS) - (N_CH0 - 1)) + 1)] = HWPE_add_i;
	assign TCDM_data_wen_DEM_TO_XBAR[N_CH0 - 1:N_CH0 - N_HWPE_PORTS] = HWPE_wen_i;
	assign TCDM_data_wdata_DEM_TO_XBAR[DATA_WIDTH * (((N_CH0 - 1) >= (N_CH0 - N_HWPE_PORTS) ? N_CH0 - 1 : ((N_CH0 - 1) + ((N_CH0 - 1) >= (N_CH0 - N_HWPE_PORTS) ? ((N_CH0 - 1) - (N_CH0 - N_HWPE_PORTS)) + 1 : ((N_CH0 - N_HWPE_PORTS) - (N_CH0 - 1)) + 1)) - 1) - (((N_CH0 - 1) >= (N_CH0 - N_HWPE_PORTS) ? ((N_CH0 - 1) - (N_CH0 - N_HWPE_PORTS)) + 1 : ((N_CH0 - N_HWPE_PORTS) - (N_CH0 - 1)) + 1) - 1))+:DATA_WIDTH * ((N_CH0 - 1) >= (N_CH0 - N_HWPE_PORTS) ? ((N_CH0 - 1) - (N_CH0 - N_HWPE_PORTS)) + 1 : ((N_CH0 - N_HWPE_PORTS) - (N_CH0 - 1)) + 1)] = HWPE_wdata_i;
	assign TCDM_data_be_DEM_TO_XBAR[BE_WIDTH * (((N_CH0 - 1) >= (N_CH0 - N_HWPE_PORTS) ? N_CH0 - 1 : ((N_CH0 - 1) + ((N_CH0 - 1) >= (N_CH0 - N_HWPE_PORTS) ? ((N_CH0 - 1) - (N_CH0 - N_HWPE_PORTS)) + 1 : ((N_CH0 - N_HWPE_PORTS) - (N_CH0 - 1)) + 1)) - 1) - (((N_CH0 - 1) >= (N_CH0 - N_HWPE_PORTS) ? ((N_CH0 - 1) - (N_CH0 - N_HWPE_PORTS)) + 1 : ((N_CH0 - N_HWPE_PORTS) - (N_CH0 - 1)) + 1) - 1))+:BE_WIDTH * ((N_CH0 - 1) >= (N_CH0 - N_HWPE_PORTS) ? ((N_CH0 - 1) - (N_CH0 - N_HWPE_PORTS)) + 1 : ((N_CH0 - N_HWPE_PORTS) - (N_CH0 - 1)) + 1)] = HWPE_be_i;
	assign HWPE_gnt_o = TCDM_data_gnt_DEM_TO_XBAR[N_CH0 - 1:N_CH0 - N_HWPE_PORTS];
	assign HWPE_r_valid_o = TCDM_data_r_valid_DEM_TO_XBAR[N_CH0 - 1:N_CH0 - N_HWPE_PORTS];
	assign HWPE_r_rdata_o = TCDM_data_r_rdata_DEM_TO_XBAR[DATA_WIDTH * (((N_CH0 - 1) >= (N_CH0 - N_HWPE_PORTS) ? N_CH0 - 1 : ((N_CH0 - 1) + ((N_CH0 - 1) >= (N_CH0 - N_HWPE_PORTS) ? ((N_CH0 - 1) - (N_CH0 - N_HWPE_PORTS)) + 1 : ((N_CH0 - N_HWPE_PORTS) - (N_CH0 - 1)) + 1)) - 1) - (((N_CH0 - 1) >= (N_CH0 - N_HWPE_PORTS) ? ((N_CH0 - 1) - (N_CH0 - N_HWPE_PORTS)) + 1 : ((N_CH0 - N_HWPE_PORTS) - (N_CH0 - 1)) + 1) - 1))+:DATA_WIDTH * ((N_CH0 - 1) >= (N_CH0 - N_HWPE_PORTS) ? ((N_CH0 - 1) - (N_CH0 - N_HWPE_PORTS)) + 1 : ((N_CH0 - N_HWPE_PORTS) - (N_CH0 - 1)) + 1)];
	genvar j;
	generate
		for (j = 0; j < (N_CH0 + N_CH1); j = j + 1) begin : genblk2
			assign TCDM_data_add_DEM_TO_XBAR_resized[j * (ADDR_L2_WIDTH + $clog2(N_L2_BANKS))+:ADDR_L2_WIDTH + $clog2(N_L2_BANKS)] = TCDM_data_add_DEM_TO_XBAR[(j * ADDR_WIDTH) + (((ADDR_L2_WIDTH + $clog2(N_L2_BANKS)) + 1) >= 2 ? (ADDR_L2_WIDTH + $clog2(N_L2_BANKS)) + 1 : (((ADDR_L2_WIDTH + $clog2(N_L2_BANKS)) + 1) + (((ADDR_L2_WIDTH + $clog2(N_L2_BANKS)) + 1) >= 2 ? ADDR_L2_WIDTH + $clog2(N_L2_BANKS) : 3 - ((ADDR_L2_WIDTH + $clog2(N_L2_BANKS)) + 1))) - 1)-:(((ADDR_L2_WIDTH + $clog2(N_L2_BANKS)) + 1) >= 2 ? ADDR_L2_WIDTH + $clog2(N_L2_BANKS) : 3 - ((ADDR_L2_WIDTH + $clog2(N_L2_BANKS)) + 1))];
		end
	endgenerate
	XBAR_L2 #(
		.N_CH0(N_CH0),
		.N_CH1(N_CH1),
		.N_SLAVE(N_L2_BANKS),
		.ID_WIDTH(N_CH0 + N_CH1),
		.ADDR_IN_WIDTH(ADDR_L2_WIDTH + $clog2(N_L2_BANKS)),
		.DATA_WIDTH(DATA_WIDTH),
		.BE_WIDTH(BE_WIDTH),
		.ADDR_MEM_WIDTH(ADDR_L2_WIDTH)
	) XBAR_L2_i(
		.data_req_i(TCDM_data_req_DEM_TO_XBAR),
		.data_add_i(TCDM_data_add_DEM_TO_XBAR_resized),
		.data_wen_i(TCDM_data_wen_DEM_TO_XBAR),
		.data_wdata_i(TCDM_data_wdata_DEM_TO_XBAR),
		.data_be_i(TCDM_data_be_DEM_TO_XBAR),
		.data_gnt_o(TCDM_data_gnt_DEM_TO_XBAR),
		.data_r_valid_o(TCDM_data_r_valid_DEM_TO_XBAR),
		.data_r_rdata_o(TCDM_data_r_rdata_DEM_TO_XBAR),
		.data_req_o(TCDM_data_req_TO_MEM),
		.data_add_o(TCDM_data_add_TO_MEM),
		.data_wen_o(TCDM_data_wen_TO_MEM),
		.data_wdata_o(TCDM_data_wdata_TO_MEM),
		.data_be_o(TCDM_data_be_TO_MEM),
		.data_ID_o(TCDM_data_ID_TO_MEM),
		.data_r_rdata_i(TCDM_data_rdata_TO_MEM),
		.data_r_valid_i(TCDM_data_rvalid_TO_MEM),
		.data_r_ID_i(TCDM_data_rID_TO_MEM),
		.clk(clk),
		.rst_n(rst_n)
	);
	XBAR_BRIDGE #(
		.N_CH0(N_CH0_BRIDGE),
		.N_CH1(N_CH1_BRIDGE),
		.N_SLAVE(N_PERIPHS),
		.ID_WIDTH(PER_ID_WIDTH),
		.AUX_WIDTH(AUX_WIDTH),
		.ADDR_WIDTH(ADDR_WIDTH),
		.DATA_WIDTH(DATA_WIDTH),
		.BE_WIDTH(BE_WIDTH)
	) XBAR_BRIDGE_i(
		.data_req_i(PER_data_req_DEM_2_L2_XBAR),
		.data_add_i(PER_data_add_DEM_2_L2_XBAR),
		.data_wen_i(PER_data_wen_DEM_2_L2_XBAR),
		.data_wdata_i(PER_data_wdata_DEM_2_L2_XBAR),
		.data_be_i(PER_data_be_DEM_2_L2_XBAR),
		.data_aux_i(PER_data_aux_DEM_2_L2_XBAR),
		.data_gnt_o(PER_data_gnt_DEM_2_L2_XBAR),
		.data_r_valid_o(PER_data_r_valid_DEM_2_L2_XBAR),
		.data_r_rdata_o(PER_data_r_rdata_DEM_2_L2_XBAR),
		.data_r_opc_o(PER_data_r_opc_DEM_2_L2_XBAR),
		.data_r_aux_o(PER_data_r_aux_DEM_2_L2_XBAR),
		.data_req_o(PER_data_req_TO_BRIDGE),
		.data_add_o(PER_data_add_TO_BRIDGE),
		.data_wen_o(PER_data_wen_TO_BRIDGE),
		.data_wdata_o(PER_data_wdata_TO_BRIDGE),
		.data_be_o(PER_data_be_TO_BRIDGE),
		.data_ID_o(PER_data_ID_TO_BRIDGE),
		.data_aux_o(PER_data_aux_TO_BRIDGE),
		.data_gnt_i(PER_data_gnt_TO_BRIDGE),
		.data_r_rdata_i(PER_data_r_rdata_TO_BRIDGE),
		.data_r_valid_i(PER_data_r_valid_TO_BRIDGE),
		.data_r_ID_i(PER_data_r_ID_TO_BRIDGE),
		.data_r_opc_i(PER_data_r_opc_TO_BRIDGE),
		.data_r_aux_i(PER_data_r_aux_TO_BRIDGE),
		.clk(clk),
		.rst_n(rst_n),
		.START_ADDR(PER_START_ADDR),
		.END_ADDR(PER_END_ADDR)
	);
	genvar i;
	generate
		for (i = 0; i < (N_CH0 - N_HWPE_PORTS); i = i + 1) begin : FC_DEMUX_32
			l2_tcdm_demux #(
				.ADDR_WIDTH(ADDR_WIDTH),
				.DATA_WIDTH(DATA_WIDTH),
				.BE_WIDTH(BE_WIDTH),
				.AUX_WIDTH(AUX_WIDTH),
				.N_PERIPHS(N_PERIPHS)
			) DEMUX_MASTER_32(
				.clk(clk),
				.rst_n(rst_n),
				.test_en_i(test_en_i),
				.data_req_i(FC_data_req_INT_32[i]),
				.data_add_i(FC_data_add_INT_32[i * ADDR_WIDTH+:ADDR_WIDTH]),
				.data_wen_i(FC_data_wen_INT_32[i]),
				.data_wdata_i(FC_data_wdata_INT_32[i * DATA_WIDTH+:DATA_WIDTH]),
				.data_be_i(FC_data_be_INT_32[i * BE_WIDTH+:BE_WIDTH]),
				.data_aux_i(FC_data_aux_INT_32[i * AUX_WIDTH+:AUX_WIDTH]),
				.data_gnt_o(FC_data_gnt_INT_32[i]),
				.data_r_aux_o(FC_data_r_aux_INT_32[i * AUX_WIDTH+:AUX_WIDTH]),
				.data_r_valid_o(FC_data_r_valid_INT_32[i]),
				.data_r_rdata_o(FC_data_r_rdata_INT_32[i * DATA_WIDTH+:DATA_WIDTH]),
				.data_r_opc_o(FC_data_r_opc_INT_32[i]),
				.data_req_o_TDCM(TCDM_data_req_DEM_TO_XBAR[i]),
				.data_add_o_TDCM(TCDM_data_add_DEM_TO_XBAR[i * ADDR_WIDTH+:ADDR_WIDTH]),
				.data_wen_o_TDCM(TCDM_data_wen_DEM_TO_XBAR[i]),
				.data_wdata_o_TDCM(TCDM_data_wdata_DEM_TO_XBAR[i * DATA_WIDTH+:DATA_WIDTH]),
				.data_be_o_TDCM(TCDM_data_be_DEM_TO_XBAR[i * BE_WIDTH+:BE_WIDTH]),
				.data_gnt_i_TDCM(TCDM_data_gnt_DEM_TO_XBAR[i]),
				.data_r_valid_i_TDCM(TCDM_data_r_valid_DEM_TO_XBAR[i]),
				.data_r_rdata_i_TDCM(TCDM_data_r_rdata_DEM_TO_XBAR[i * DATA_WIDTH+:DATA_WIDTH]),
				.data_req_o_PER(PER_data_req_DEM_2_L2_XBAR[i]),
				.data_add_o_PER(PER_data_add_DEM_2_L2_XBAR[i * ADDR_WIDTH+:ADDR_WIDTH]),
				.data_wen_o_PER(PER_data_wen_DEM_2_L2_XBAR[i]),
				.data_wdata_o_PER(PER_data_wdata_DEM_2_L2_XBAR[i * DATA_WIDTH+:DATA_WIDTH]),
				.data_be_o_PER(PER_data_be_DEM_2_L2_XBAR[i * BE_WIDTH+:BE_WIDTH]),
				.data_aux_o_PER(PER_data_aux_DEM_2_L2_XBAR[i * AUX_WIDTH+:AUX_WIDTH]),
				.data_gnt_i_PER(PER_data_gnt_DEM_2_L2_XBAR[i]),
				.data_r_valid_i_PER(PER_data_r_valid_DEM_2_L2_XBAR[i]),
				.data_r_rdata_i_PER(PER_data_r_rdata_DEM_2_L2_XBAR[i * DATA_WIDTH+:DATA_WIDTH]),
				.data_r_opc_i_PER(PER_data_r_opc_DEM_2_L2_XBAR[i]),
				.data_r_aux_i_PER(PER_data_r_aux_DEM_2_L2_XBAR[i * AUX_WIDTH+:AUX_WIDTH]),
				.PER_START_ADDR(PER_START_ADDR),
				.PER_END_ADDR(PER_END_ADDR),
				.TCDM_START_ADDR(TCDM_START_ADDR),
				.TCDM_END_ADDR(TCDM_END_ADDR)
			);
		end
		for (i = 0; i < N_CH1; i = i + 1) begin : FC_DEMUX_64
			l2_tcdm_demux #(
				.ADDR_WIDTH(ADDR_WIDTH),
				.DATA_WIDTH(DATA_WIDTH),
				.BE_WIDTH(BE_WIDTH),
				.AUX_WIDTH(AUX_WIDTH),
				.N_PERIPHS(N_PERIPHS)
			) DEMUX_AXI64(
				.clk(clk),
				.rst_n(rst_n),
				.test_en_i(test_en_i),
				.data_req_i(AXI_data_req_INT_64[i]),
				.data_add_i(AXI_data_add_INT_64[i * ADDR_WIDTH+:ADDR_WIDTH]),
				.data_wen_i(AXI_data_wen_INT_64[i]),
				.data_wdata_i(AXI_data_wdata_INT_64[i * DATA_WIDTH+:DATA_WIDTH]),
				.data_be_i(AXI_data_be_INT_64[i * BE_WIDTH+:BE_WIDTH]),
				.data_aux_i(AXI_data_aux_INT_64[i * AUX_WIDTH+:AUX_WIDTH]),
				.data_gnt_o(AXI_data_gnt_INT_64[i]),
				.data_r_aux_o(AXI_data_r_aux_INT_64[i * AUX_WIDTH+:AUX_WIDTH]),
				.data_r_valid_o(AXI_data_r_valid_INT_64[i]),
				.data_r_rdata_o(AXI_data_r_rdata_INT_64[i * DATA_WIDTH+:DATA_WIDTH]),
				.data_r_opc_o(AXI_data_r_opc_INT_64[i]),
				.data_req_o_TDCM(TCDM_data_req_DEM_TO_XBAR[N_CH0 + i]),
				.data_add_o_TDCM(TCDM_data_add_DEM_TO_XBAR[(N_CH0 + i) * ADDR_WIDTH+:ADDR_WIDTH]),
				.data_wen_o_TDCM(TCDM_data_wen_DEM_TO_XBAR[N_CH0 + i]),
				.data_wdata_o_TDCM(TCDM_data_wdata_DEM_TO_XBAR[(N_CH0 + i) * DATA_WIDTH+:DATA_WIDTH]),
				.data_be_o_TDCM(TCDM_data_be_DEM_TO_XBAR[(N_CH0 + i) * BE_WIDTH+:BE_WIDTH]),
				.data_gnt_i_TDCM(TCDM_data_gnt_DEM_TO_XBAR[N_CH0 + i]),
				.data_r_valid_i_TDCM(TCDM_data_r_valid_DEM_TO_XBAR[N_CH0 + i]),
				.data_r_rdata_i_TDCM(TCDM_data_r_rdata_DEM_TO_XBAR[(N_CH0 + i) * DATA_WIDTH+:DATA_WIDTH]),
				.data_req_o_PER(PER_data_req_DEM_2_L2_XBAR[N_CH0 + i]),
				.data_add_o_PER(PER_data_add_DEM_2_L2_XBAR[(N_CH0 + i) * ADDR_WIDTH+:ADDR_WIDTH]),
				.data_wen_o_PER(PER_data_wen_DEM_2_L2_XBAR[N_CH0 + i]),
				.data_wdata_o_PER(PER_data_wdata_DEM_2_L2_XBAR[(N_CH0 + i) * DATA_WIDTH+:DATA_WIDTH]),
				.data_be_o_PER(PER_data_be_DEM_2_L2_XBAR[(N_CH0 + i) * BE_WIDTH+:BE_WIDTH]),
				.data_aux_o_PER(PER_data_aux_DEM_2_L2_XBAR[(N_CH0 + i) * AUX_WIDTH+:AUX_WIDTH]),
				.data_gnt_i_PER(PER_data_gnt_DEM_2_L2_XBAR[N_CH0 + i]),
				.data_r_valid_i_PER(PER_data_r_valid_DEM_2_L2_XBAR[N_CH0 + i]),
				.data_r_rdata_i_PER(PER_data_r_rdata_DEM_2_L2_XBAR[(N_CH0 + i) * DATA_WIDTH+:DATA_WIDTH]),
				.data_r_opc_i_PER(PER_data_r_opc_DEM_2_L2_XBAR[N_CH0 + i]),
				.data_r_aux_i_PER(PER_data_r_aux_DEM_2_L2_XBAR[(N_CH0 + i) * AUX_WIDTH+:AUX_WIDTH]),
				.PER_START_ADDR(PER_START_ADDR),
				.PER_END_ADDR(PER_END_ADDR),
				.TCDM_START_ADDR(TCDM_START_ADDR),
				.TCDM_END_ADDR(TCDM_END_ADDR)
			);
		end
	endgenerate
	always @(*) begin : sv2v_autoblock_1
		reg [31:0] i;
		for (i = 0; i < N_L2_BANKS; i = i + 1)
			begin
				L2_D_o[i * DATA_WIDTH+:DATA_WIDTH] = TCDM_data_wdata_TO_MEM[i * DATA_WIDTH+:DATA_WIDTH];
				L2_A_o[i * ADDR_L2_WIDTH+:ADDR_L2_WIDTH] = TCDM_data_add_TO_MEM[i * ADDR_L2_WIDTH+:ADDR_L2_WIDTH] - L2_OFFSET_PRI;
				L2_CEN_o[i] = ~TCDM_data_req_TO_MEM[i];
				L2_WEN_o[i] = TCDM_data_wen_TO_MEM[i];
				L2_BE_o[i * BE_WIDTH+:BE_WIDTH] = TCDM_data_be_TO_MEM[i * BE_WIDTH+:BE_WIDTH];
				L2_ID_o[i * 32+:32] = TCDM_data_ID_TO_MEM[i * ID_WIDTH+:ID_WIDTH];
				TCDM_data_rdata_TO_MEM[i * DATA_WIDTH+:DATA_WIDTH] = L2_Q_i[i * DATA_WIDTH+:DATA_WIDTH];
			end
	end
	always @(posedge clk or negedge rst_n)
		if (rst_n == 1'b0) begin : sv2v_autoblock_2
			reg [31:0] i;
			for (i = 0; i < N_L2_BANKS; i = i + 1)
				begin
					TCDM_data_rID_TO_MEM[i * ID_WIDTH+:ID_WIDTH] <= 1'sb0;
					TCDM_data_rvalid_TO_MEM[i] <= 1'sb0;
				end
		end
		else begin : sv2v_autoblock_3
			reg [31:0] i;
			for (i = 0; i < N_L2_BANKS; i = i + 1)
				if (TCDM_data_req_TO_MEM[i]) begin
					TCDM_data_rID_TO_MEM[i * ID_WIDTH+:ID_WIDTH] <= TCDM_data_ID_TO_MEM[i * ID_WIDTH+:ID_WIDTH];
					TCDM_data_rvalid_TO_MEM[i] <= 1'b1;
				end
				else
					TCDM_data_rvalid_TO_MEM[i] <= 1'b0;
		end
	lint_2_apb #(
		.ADDR_WIDTH(ADDR_WIDTH),
		.DATA_WIDTH(DATA_WIDTH),
		.BE_WIDTH(BE_WIDTH),
		.ID_WIDTH(PER_ID_WIDTH),
		.AUX_WIDTH(AUX_WIDTH)
	) lint_2_apb_i(
		.clk(clk),
		.rst_n(rst_n),
		.data_req_i(PER_data_req_TO_BRIDGE[0]),
		.data_add_i(PER_data_add_TO_BRIDGE[0+:ADDR_WIDTH]),
		.data_wen_i(PER_data_wen_TO_BRIDGE[0]),
		.data_wdata_i(PER_data_wdata_TO_BRIDGE[0+:DATA_WIDTH]),
		.data_be_i(PER_data_be_TO_BRIDGE[0+:BE_WIDTH]),
		.data_aux_i(PER_data_aux_TO_BRIDGE[0+:AUX_WIDTH]),
		.data_ID_i(PER_data_ID_TO_BRIDGE[0+:PER_ID_WIDTH]),
		.data_gnt_o(PER_data_gnt_TO_BRIDGE[0]),
		.data_r_valid_o(PER_data_r_valid_TO_BRIDGE[0]),
		.data_r_rdata_o(PER_data_r_rdata_TO_BRIDGE[0+:DATA_WIDTH]),
		.data_r_opc_o(PER_data_r_opc_TO_BRIDGE[0]),
		.data_r_aux_o(PER_data_r_aux_TO_BRIDGE[0+:AUX_WIDTH]),
		.data_r_ID_o(PER_data_r_ID_TO_BRIDGE[0+:PER_ID_WIDTH]),
		.master_PADDR(APB_PADDR_o),
		.master_PWDATA(APB_PWDATA_o),
		.master_PWRITE(APB_PWRITE_o),
		.master_PSEL(APB_PSEL_o),
		.master_PENABLE(APB_PENABLE_o),
		.master_PRDATA(APB_PRDATA_i),
		.master_PREADY(APB_PREADY_i),
		.master_PSLVERR(APB_PSLVERR_i)
	);
	lint_2_axi #(
		.ADDR_WIDTH(ADDR_WIDTH),
		.DATA_WIDTH(DATA_WIDTH),
		.BE_WIDTH(BE_WIDTH),
		.ID_WIDTH(PER_ID_WIDTH),
		.USER_WIDTH(AXI_32_USER_WIDTH),
		.AUX_WIDTH(AUX_WIDTH),
		.AXI_ID_WIDTH(AXI_32_ID_WIDTH),
		.REGISTERED_GRANT("FALSE")
	) i_lint_2_axi(
		.clk_i(clk),
		.rst_ni(rst_n),
		.data_req_i(PER_data_req_TO_BRIDGE[1]),
		.data_addr_i(PER_data_add_TO_BRIDGE[ADDR_WIDTH+:ADDR_WIDTH]),
		.data_we_i(~PER_data_wen_TO_BRIDGE[1]),
		.data_wdata_i(PER_data_wdata_TO_BRIDGE[DATA_WIDTH+:DATA_WIDTH]),
		.data_be_i(PER_data_be_TO_BRIDGE[BE_WIDTH+:BE_WIDTH]),
		.data_aux_i(PER_data_aux_TO_BRIDGE[AUX_WIDTH+:AUX_WIDTH]),
		.data_ID_i(PER_data_ID_TO_BRIDGE[PER_ID_WIDTH+:PER_ID_WIDTH]),
		.data_gnt_o(PER_data_gnt_TO_BRIDGE[1]),
		.data_rvalid_o(PER_data_r_valid_TO_BRIDGE[1]),
		.data_rdata_o(PER_data_r_rdata_TO_BRIDGE[DATA_WIDTH+:DATA_WIDTH]),
		.data_ropc_o(PER_data_r_opc_TO_BRIDGE[1]),
		.data_raux_o(PER_data_r_aux_TO_BRIDGE[AUX_WIDTH+:AUX_WIDTH]),
		.data_rID_o(PER_data_r_ID_TO_BRIDGE[PER_ID_WIDTH+:PER_ID_WIDTH]),
		.aw_id_o(AXI_Master_aw_id_o),
		.aw_addr_o(AXI_Master_aw_addr_o),
		.aw_len_o(AXI_Master_aw_len_o),
		.aw_size_o(AXI_Master_aw_size_o),
		.aw_burst_o(AXI_Master_aw_burst_o),
		.aw_lock_o(AXI_Master_aw_lock_o),
		.aw_cache_o(AXI_Master_aw_cache_o),
		.aw_prot_o(AXI_Master_aw_prot_o),
		.aw_region_o(AXI_Master_aw_region_o),
		.aw_user_o(AXI_Master_aw_user_o),
		.aw_qos_o(AXI_Master_aw_qos_o),
		.aw_valid_o(AXI_Master_aw_valid_o),
		.aw_ready_i(AXI_Master_aw_ready_i),
		.w_data_o(AXI_Master_w_data_o),
		.w_strb_o(AXI_Master_w_strb_o),
		.w_last_o(AXI_Master_w_last_o),
		.w_user_o(AXI_Master_w_user_o),
		.w_valid_o(AXI_Master_w_valid_o),
		.w_ready_i(AXI_Master_w_ready_i),
		.b_id_i(AXI_Master_b_id_i),
		.b_resp_i(AXI_Master_b_resp_i),
		.b_valid_i(AXI_Master_b_valid_i),
		.b_user_i(AXI_Master_b_user_i),
		.b_ready_o(AXI_Master_b_ready_o),
		.ar_id_o(AXI_Master_ar_id_o),
		.ar_addr_o(AXI_Master_ar_addr_o),
		.ar_len_o(AXI_Master_ar_len_o),
		.ar_size_o(AXI_Master_ar_size_o),
		.ar_burst_o(AXI_Master_ar_burst_o),
		.ar_lock_o(AXI_Master_ar_lock_o),
		.ar_cache_o(AXI_Master_ar_cache_o),
		.ar_prot_o(AXI_Master_ar_prot_o),
		.ar_region_o(AXI_Master_ar_region_o),
		.ar_user_o(AXI_Master_ar_user_o),
		.ar_qos_o(AXI_Master_ar_qos_o),
		.ar_valid_o(AXI_Master_ar_valid_o),
		.ar_ready_i(AXI_Master_ar_ready_i),
		.r_id_i(AXI_Master_r_id_i),
		.r_data_i(AXI_Master_r_data_i),
		.r_resp_i(AXI_Master_r_resp_i),
		.r_last_i(AXI_Master_r_last_i),
		.r_user_i(AXI_Master_r_user_i),
		.r_valid_i(AXI_Master_r_valid_i),
		.r_ready_o(AXI_Master_r_ready_o)
	);
	axi64_2_lint32 #(
		.AXI_ADDR_WIDTH(AXI_ADDR_WIDTH),
		.AXI_DATA_WIDTH(AXI_DATA_WIDTH),
		.AXI_STRB_WIDTH(AXI_STRB_WIDTH),
		.AXI_USER_WIDTH(AXI_USER_WIDTH),
		.AXI_ID_WIDTH(AXI_ID_WIDTH),
		.BUFF_DEPTH_SLICES(4),
		.DATA_WIDTH(DATA_WIDTH),
		.BE_WIDTH(BE_WIDTH),
		.ADDR_WIDTH(ADDR_WIDTH),
		.AUX_WIDTH(AUX_WIDTH)
	) axi64_2_lint32_i(
		.clk(clk),
		.rst_n(rst_n),
		.test_en_i(test_en_i),
		.AW_ADDR_i(AXI_Slave_aw_addr_i),
		.AW_PROT_i(AXI_Slave_aw_prot_i),
		.AW_REGION_i(AXI_Slave_aw_region_i),
		.AW_LEN_i(AXI_Slave_aw_len_i),
		.AW_SIZE_i(AXI_Slave_aw_size_i),
		.AW_BURST_i(AXI_Slave_aw_burst_i),
		.AW_LOCK_i(AXI_Slave_aw_lock_i),
		.AW_CACHE_i(AXI_Slave_aw_cache_i),
		.AW_QOS_i(AXI_Slave_aw_qos_i),
		.AW_ID_i(AXI_Slave_aw_id_i),
		.AW_USER_i(AXI_Slave_aw_user_i),
		.AW_VALID_i(AXI_Slave_aw_valid_i),
		.AW_READY_o(AXI_Slave_aw_ready_o),
		.AR_ADDR_i(AXI_Slave_ar_addr_i),
		.AR_PROT_i(AXI_Slave_ar_prot_i),
		.AR_REGION_i(AXI_Slave_ar_region_i),
		.AR_LEN_i(AXI_Slave_ar_len_i),
		.AR_SIZE_i(AXI_Slave_ar_size_i),
		.AR_BURST_i(AXI_Slave_ar_burst_i),
		.AR_LOCK_i(AXI_Slave_ar_lock_i),
		.AR_CACHE_i(AXI_Slave_ar_cache_i),
		.AR_QOS_i(AXI_Slave_ar_qos_i),
		.AR_ID_i(AXI_Slave_ar_id_i),
		.AR_USER_i(AXI_Slave_ar_user_i),
		.AR_VALID_i(AXI_Slave_ar_valid_i),
		.AR_READY_o(AXI_Slave_ar_ready_o),
		.W_USER_i(AXI_Slave_w_user_i),
		.W_DATA_i(AXI_Slave_w_data_i),
		.W_STRB_i(AXI_Slave_w_strb_i),
		.W_LAST_i(AXI_Slave_w_last_i),
		.W_VALID_i(AXI_Slave_w_valid_i),
		.W_READY_o(AXI_Slave_w_ready_o),
		.B_ID_o(AXI_Slave_b_id_o),
		.B_RESP_o(AXI_Slave_b_resp_o),
		.B_USER_o(AXI_Slave_b_user_o),
		.B_VALID_o(AXI_Slave_b_valid_o),
		.B_READY_i(AXI_Slave_b_ready_i),
		.R_ID_o(AXI_Slave_r_id_o),
		.R_USER_o(AXI_Slave_r_user_o),
		.R_DATA_o(AXI_Slave_r_data_o),
		.R_RESP_o(AXI_Slave_r_resp_o),
		.R_LAST_o(AXI_Slave_r_last_o),
		.R_VALID_o(AXI_Slave_r_valid_o),
		.R_READY_i(AXI_Slave_r_ready_i),
		.data_W_req_o(AXI_data_req_INT_64[1:0]),
		.data_W_gnt_i(AXI_data_gnt_INT_64[1:0]),
		.data_W_wdata_o(AXI_data_wdata_INT_64[0+:DATA_WIDTH * 2]),
		.data_W_add_o(AXI_data_add_INT_64[0+:ADDR_WIDTH * 2]),
		.data_W_wen_o(AXI_data_wen_INT_64[1:0]),
		.data_W_be_o(AXI_data_be_INT_64[0+:BE_WIDTH * 2]),
		.data_W_aux_o(AXI_data_aux_INT_64[0+:AUX_WIDTH * 2]),
		.data_W_r_valid_i(AXI_data_r_valid_INT_64[1:0]),
		.data_W_r_rdata_i(AXI_data_r_rdata_INT_64[0+:DATA_WIDTH * 2]),
		.data_W_r_opc_i(AXI_data_r_opc_INT_64[1:0]),
		.data_W_r_aux_i(AXI_data_r_aux_INT_64[0+:AUX_WIDTH * 2]),
		.data_R_req_o(AXI_data_req_INT_64[3:2]),
		.data_R_gnt_i(AXI_data_gnt_INT_64[3:2]),
		.data_R_wdata_o(AXI_data_wdata_INT_64[DATA_WIDTH * 2+:DATA_WIDTH * 2]),
		.data_R_add_o(AXI_data_add_INT_64[ADDR_WIDTH * 2+:ADDR_WIDTH * 2]),
		.data_R_wen_o(AXI_data_wen_INT_64[3:2]),
		.data_R_be_o(AXI_data_be_INT_64[BE_WIDTH * 2+:BE_WIDTH * 2]),
		.data_R_aux_o(AXI_data_aux_INT_64[AUX_WIDTH * 2+:AUX_WIDTH * 2]),
		.data_R_r_valid_i(AXI_data_r_valid_INT_64[3:2]),
		.data_R_r_rdata_i(AXI_data_r_rdata_INT_64[DATA_WIDTH * 2+:DATA_WIDTH * 2]),
		.data_R_r_opc_i(AXI_data_r_opc_INT_64[3:2]),
		.data_R_r_aux_i(AXI_data_r_aux_INT_64[AUX_WIDTH * 2+:AUX_WIDTH * 2])
	);
endmodule
