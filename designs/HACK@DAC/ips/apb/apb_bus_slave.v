module APB_BUS_SLAVE(
    paddr,  
    pwdata,  
    pwrite, 
    psel,  
    penable,
    prdata,          
    pready,        
    pslverr
);

    parameter APB_ADDR_WIDTH = 32;
    parameter APB_DATA_WIDTH = 32;

    input  reg  [APB_ADDR_WIDTH-1:0]      paddr;
    input reg  [APB_DATA_WIDTH-1:0]  pwdata;
    input reg pwrite;
    input reg psel;
    input reg  penable;
    output reg [APB_DATA_WIDTH-1:0]   prdata;
    output reg  pready;
    output reg  pslverr;

end module;