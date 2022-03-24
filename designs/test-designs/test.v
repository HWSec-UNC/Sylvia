`timescale 1ns / 1ps
`default_nettype none
`define assert(expression) \
        if (expression !== 1) begin \
            $display("ASSERTION FAILED"); \
            $finish; \
        end   
module sanity_test
  (
   input CLK, 
   input RST,
   input enable,
   input [31:0] value,
   output [7:0] led,
   output place_holder_out 
  );
  reg [31:0] count;
  reg [7:0] state;
  assign led = count[23:16];
  always @(posedge CLK) begin
    if(RST) begin
      count <= 0;
      state <= 0;
    end else begin
      if(state == 0) begin
        if(enable) state <= 1;
      end else if(state == 1) begin
        state <= 2;
      end else if(state == 2) begin
        count <= count + value;
        state <= 0;
      end
    end
  end

    place_holder test_1(
    .CLK (CLK),
    .RST (RST),
    .out (test_1_out)
  );

  place_holder test_2(
    .CLK (CLK),
    .RST (RST),
    .out (test_2_out)
  );

  place_holder test_3(
    .CLK (CLK),
    .RST (RST),
    .out (test_3_out)
  );

  place_holder test_4(
    .CLK (CLK),
    .RST (RST),
    .out (test_4_out)
  );

  // initial begin
  //   `assert (place_holder.out == 1)
  // end
  
endmodule



