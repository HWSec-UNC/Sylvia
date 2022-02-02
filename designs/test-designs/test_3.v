module demo (
   input clk, 
   input enable,
   input [31:0] secret,
   output [7:0] led
);

  wire [31:0] temp = (enable) ? secret : 0;
  reg  [7:0]  result = 0;

  assign led = result[7:0];

  always @(posedge clk) begin
    if (enable)
      result <= 255;
    else
      result <= temp[23:16];
  end

endmodule