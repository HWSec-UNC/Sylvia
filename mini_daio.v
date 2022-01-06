`define assert(signal, value) \
        if (signal !== value) begin \
            $display("ASSERTION FAILED"); \
            $finish; \
        end  
        
module main(clock,xtal,rx_control,reset,bit_in,
		     preamble_1,preamble_2,preamble_3,
		     carrier_loss,biphase_violation,
	 	     clock_out,rx_status,parity,load_A,load_B,load_buff,
		     shift_reg,frame_ofs);
    input clock;
    input [3:0]   xtal;			// clocks
    input [3:0]   rx_control;		// control inputs
    input 	  reset;		// global reset
    input 	  bit_in;		// extracted bit from biphase
    input 	  preamble_1;		// start of block
    input 	  preamble_2;		// start of subframe_A
    input 	  preamble_3;		// start of subframe_B
    input 	  carrier_loss;		// too many biphase violations
    input 	  biphase_violation;	// no transition at end of bit

    output 	  clock_out;		// clock selected from xtal
    output [3:0]  rx_status;		// status outputs
    output 	  parity;		// parity of current subframe
    output 	  load_A;		// load subframe_A from shift_reg
    output 	  load_B;		// load subframe_B from shift_reg
    output 	  load_buff;		// load register bank into buffer
    output [19:0] shift_reg;		// last 20 bits from phase_decoder
    output [1:0]  frame_ofs;		// last 2 bits of frame counter

    reg [6:0] 	  bit_count_A;	
    reg [6:0] 	  bit_count_B;
    reg [8:0] 	  frame_counter;

    reg 	  clock_out;
    reg  	  rx_status_3, rx_status_2, rx_status_1, rx_status_0;
    reg 	  parity;
    reg 	  load_A;
    reg 	  load_B;
    reg 	  load_buff;
    reg [19:0] 	  shift_reg;
    reg [3:0]    pc;
    
    parameter L0 = 0;
    parameter L1 = 1;
    parameter L2 = 2;
    parameter L3 = 3;
    parameter L4 = 4;
    parameter L5 = 5;
    parameter L6 = 6;
    parameter L7 = 7;
    parameter L8 = 8;
    parameter L9 = 9;
    parameter L10 = 10;


    assign 	  rx_status = {rx_status_3, rx_status_2,
			       rx_status_1, rx_status_0};

  initial begin
	bit_count_A = 0;
	bit_count_B = 0;
	frame_counter = 0;
	clock_out = 0;  // was uninitialized
	rx_status_3 = 0; rx_status_2 = 0; rx_status_1 = 0; rx_status_0 = 0;
	parity = 0;
	load_A = 0;
	load_B = 0;
	load_buff = 0;
	shift_reg = 0;
	pc = L0;
  end

  assign frame_ofs[1:0] = frame_counter[1:0];

  
    always @ (posedge clock) begin
	if (reset) begin
	    shift_reg = 0;
	    rx_status_1 = 0; rx_status_0 = 0;
	end else if (pc != L0 && pc != L1) begin
	    shift_reg = {shift_reg[18:0], bit_in};
	    if (carrier_loss) rx_status_0 = 1; 
	    if (biphase_violation) rx_status_1 = 1;
	end
    end // always @ (posedge clock)

  always @ (posedge clock) begin
	 if (reset || pc == L2 || pc == L4 || pc == L6 || pc == L8) begin
	   parity = 0;
	 end else if (pc != L0 && pc != L1) begin
	   parity = parity ^ bit_in;
	 end
  end

  initial begin
    `assert(parity, 0)
  end
endmodule