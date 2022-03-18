module periph_bus_wrap (
	clk_i,
	rst_ni,
	apb_slave,
	fll_master,
	gpio_master,
	udma_master,
	soc_ctrl_master,
	adv_timer_master,
	soc_evnt_gen_master,
	eu_master,
	mmap_debug_master,
	timer_master,
	hwpe_master,
	stdout_master
);
	parameter APB_ADDR_WIDTH = 32;
	parameter APB_DATA_WIDTH = 32;
	input wire clk_i;
	input wire rst_ni;
	input APB_BUS.Slave apb_slave;
	input APB_BUS.Master fll_master;
	input APB_BUS.Master gpio_master;
	input APB_BUS.Master udma_master;
	input APB_BUS.Master soc_ctrl_master;
	input APB_BUS.Master adv_timer_master;
	input APB_BUS.Master soc_evnt_gen_master;
	input APB_BUS.Master eu_master;
	input APB_BUS.Master mmap_debug_master;
	input APB_BUS.Master timer_master;
	input APB_BUS.Master hwpe_master;
	input APB_BUS.Master stdout_master;
	localparam NB_MASTER = 11;
	wire [(11 * APB_ADDR_WIDTH) - 1:0] s_start_addr;
	wire [(11 * APB_ADDR_WIDTH) - 1:0] s_end_addr;
	APB_BUS #(
		.APB_ADDR_WIDTH(APB_ADDR_WIDTH),
		.APB_DATA_WIDTH(APB_DATA_WIDTH)
	) s_masters[10:0]();
	APB_BUS #(
		.APB_ADDR_WIDTH(APB_ADDR_WIDTH),
		.APB_DATA_WIDTH(APB_DATA_WIDTH)
	) s_slave();
	assign s_slave.paddr = apb_slave.paddr;
	assign s_slave.pwdata = apb_slave.pwdata;
	assign s_slave.pwrite = apb_slave.pwrite;
	assign s_slave.psel = apb_slave.psel;
	assign s_slave.penable = apb_slave.penable;
	assign apb_slave.prdata = s_slave.prdata;
	assign apb_slave.pready = s_slave.pready;
	assign apb_slave.pslverr = s_slave.pslverr;
	assign fll_master.paddr = s_masters[0].paddr;
	assign fll_master.pwdata = s_masters[0].pwdata;
	assign fll_master.pwrite = s_masters[0].pwrite;
	assign fll_master.psel = s_masters[0].psel;
	assign fll_master.penable = s_masters[0].penable;
	assign s_masters[0].prdata = fll_master.prdata;
	assign s_masters[0].pready = fll_master.pready;
	assign s_masters[0].pslverr = fll_master.pslverr;
	assign s_start_addr[0+:APB_ADDR_WIDTH] = 32'h1a100000;
	assign s_end_addr[0+:APB_ADDR_WIDTH] = 32'h1a100fff;
	assign gpio_master.paddr = s_masters[1].paddr;
	assign gpio_master.pwdata = s_masters[1].pwdata;
	assign gpio_master.pwrite = s_masters[1].pwrite;
	assign gpio_master.psel = s_masters[1].psel;
	assign gpio_master.penable = s_masters[1].penable;
	assign s_masters[1].prdata = gpio_master.prdata;
	assign s_masters[1].pready = gpio_master.pready;
	assign s_masters[1].pslverr = gpio_master.pslverr;
	assign s_start_addr[APB_ADDR_WIDTH+:APB_ADDR_WIDTH] = 32'h1a101000;
	assign s_end_addr[APB_ADDR_WIDTH+:APB_ADDR_WIDTH] = 32'h1a10afff;
	assign udma_master.paddr = s_masters[2].paddr;
	assign udma_master.pwdata = s_masters[2].pwdata;
	assign udma_master.pwrite = s_masters[2].pwrite;
	assign udma_master.psel = s_masters[2].psel;
	assign udma_master.penable = s_masters[2].penable;
	assign s_masters[2].prdata = udma_master.prdata;
	assign s_masters[2].pready = udma_master.pready;
	assign s_masters[2].pslverr = udma_master.pslverr;
	assign s_start_addr[2 * APB_ADDR_WIDTH+:APB_ADDR_WIDTH] = 32'h1a102000;
	assign s_end_addr[2 * APB_ADDR_WIDTH+:APB_ADDR_WIDTH] = 32'h1a104fff;
	assign soc_ctrl_master.paddr = s_masters[3].paddr;
	assign soc_ctrl_master.pwdata = s_masters[3].pwdata;
	assign soc_ctrl_master.pwrite = s_masters[3].pwrite;
	assign soc_ctrl_master.psel = s_masters[3].psel;
	assign soc_ctrl_master.penable = s_masters[3].penable;
	assign s_masters[3].prdata = soc_ctrl_master.prdata;
	assign s_masters[3].pready = soc_ctrl_master.pready;
	assign s_masters[3].pslverr = soc_ctrl_master.pslverr;
	assign s_start_addr[3 * APB_ADDR_WIDTH+:APB_ADDR_WIDTH] = 32'h1a104000;
	assign s_end_addr[3 * APB_ADDR_WIDTH+:APB_ADDR_WIDTH] = 32'h1a104fff;
	assign adv_timer_master.paddr = s_masters[4].paddr;
	assign adv_timer_master.pwdata = s_masters[4].pwdata;
	assign adv_timer_master.pwrite = s_masters[4].pwrite;
	assign adv_timer_master.psel = s_masters[4].psel;
	assign adv_timer_master.penable = s_masters[4].penable;
	assign s_masters[4].prdata = adv_timer_master.prdata;
	assign s_masters[4].pready = adv_timer_master.pready;
	assign s_masters[4].pslverr = adv_timer_master.pslverr;
	assign s_start_addr[4 * APB_ADDR_WIDTH+:APB_ADDR_WIDTH] = 32'h1a105000;
	assign s_end_addr[4 * APB_ADDR_WIDTH+:APB_ADDR_WIDTH] = 32'h1a105fff;
	assign soc_evnt_gen_master.paddr = s_masters[5].paddr;
	assign soc_evnt_gen_master.pwdata = s_masters[5].pwdata;
	assign soc_evnt_gen_master.pwrite = s_masters[5].pwrite;
	assign soc_evnt_gen_master.psel = s_masters[5].psel;
	assign soc_evnt_gen_master.penable = s_masters[5].penable;
	assign s_masters[5].prdata = soc_evnt_gen_master.prdata;
	assign s_masters[5].pready = soc_evnt_gen_master.pready;
	assign s_masters[5].pslverr = soc_evnt_gen_master.pslverr;
	assign s_start_addr[5 * APB_ADDR_WIDTH+:APB_ADDR_WIDTH] = 32'h1a106000;
	assign s_end_addr[5 * APB_ADDR_WIDTH+:APB_ADDR_WIDTH] = 32'h1a106fff;
	assign eu_master.paddr = s_masters[6].paddr;
	assign eu_master.pwdata = s_masters[6].pwdata;
	assign eu_master.pwrite = s_masters[6].pwrite;
	assign eu_master.psel = s_masters[6].psel;
	assign eu_master.penable = s_masters[6].penable;
	assign s_masters[6].prdata = eu_master.prdata;
	assign s_masters[6].pready = eu_master.pready;
	assign s_masters[6].pslverr = eu_master.pslverr;
	assign s_start_addr[6 * APB_ADDR_WIDTH+:APB_ADDR_WIDTH] = 32'h1a109000;
	assign s_end_addr[6 * APB_ADDR_WIDTH+:APB_ADDR_WIDTH] = 32'h1a10afff;
	assign timer_master.paddr = s_masters[7].paddr;
	assign timer_master.pwdata = s_masters[7].pwdata;
	assign timer_master.pwrite = s_masters[7].pwrite;
	assign timer_master.psel = s_masters[7].psel;
	assign timer_master.penable = s_masters[7].penable;
	assign s_masters[7].prdata = timer_master.prdata;
	assign s_masters[7].pready = timer_master.pready;
	assign s_masters[7].pslverr = timer_master.pslverr;
	assign s_start_addr[7 * APB_ADDR_WIDTH+:APB_ADDR_WIDTH] = 32'h1a10b000;
	assign s_end_addr[7 * APB_ADDR_WIDTH+:APB_ADDR_WIDTH] = 32'h1a10bfff;
	assign hwpe_master.paddr = s_masters[8].paddr;
	assign hwpe_master.pwdata = s_masters[8].pwdata;
	assign hwpe_master.pwrite = s_masters[8].pwrite;
	assign hwpe_master.psel = s_masters[8].psel;
	assign hwpe_master.penable = s_masters[8].penable;
	assign s_masters[8].prdata = hwpe_master.prdata;
	assign s_masters[8].pready = hwpe_master.pready;
	assign s_masters[8].pslverr = hwpe_master.pslverr;
	assign s_start_addr[8 * APB_ADDR_WIDTH+:APB_ADDR_WIDTH] = 32'h1a10c000;
	assign s_end_addr[8 * APB_ADDR_WIDTH+:APB_ADDR_WIDTH] = 32'h1a10cfff;
	assign stdout_master.paddr = s_masters[9].paddr;
	assign stdout_master.pwdata = s_masters[9].pwdata;
	assign stdout_master.pwrite = s_masters[9].pwrite;
	assign stdout_master.psel = s_masters[9].psel;
	assign stdout_master.penable = s_masters[9].penable;
	assign s_masters[9].prdata = stdout_master.prdata;
	assign s_masters[9].pready = stdout_master.pready;
	assign s_masters[9].pslverr = stdout_master.pslverr;
	assign s_start_addr[9 * APB_ADDR_WIDTH+:APB_ADDR_WIDTH] = 32'h1a10f000;
	assign s_end_addr[9 * APB_ADDR_WIDTH+:APB_ADDR_WIDTH] = 32'h1a10ffff;
	assign mmap_debug_master.paddr = s_masters[10].paddr;
	assign mmap_debug_master.pwdata = s_masters[10].pwdata;
	assign mmap_debug_master.pwrite = s_masters[10].pwrite;
	assign mmap_debug_master.psel = s_masters[10].psel;
	assign mmap_debug_master.penable = s_masters[10].penable;
	assign s_masters[10].prdata = mmap_debug_master.prdata;
	assign s_masters[10].pready = mmap_debug_master.pready;
	assign s_masters[10].pslverr = mmap_debug_master.pslverr;
	assign s_start_addr[10 * APB_ADDR_WIDTH+:APB_ADDR_WIDTH] = 32'h1a110000;
	assign s_end_addr[10 * APB_ADDR_WIDTH+:APB_ADDR_WIDTH] = 32'h1a11ffff;
	apb_node_wrap #(
		.NB_MASTER(NB_MASTER),
		.APB_ADDR_WIDTH(APB_ADDR_WIDTH),
		.APB_DATA_WIDTH(APB_DATA_WIDTH)
	) apb_node_wrap_i(
		.clk_i(clk_i),
		.rst_ni(rst_ni),
		.apb_slave(s_slave),
		.apb_masters(s_masters),
		.start_addr_i(s_start_addr),
		.end_addr_i(s_end_addr)
	);
endmodule
