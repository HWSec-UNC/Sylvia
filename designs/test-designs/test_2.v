module place_holder (
  input  CLK,
  input  RST,
  output out
);
  
  wire out_wire; 
  
  always @(posedge CLK) begin
    if (RST) begin
      out <= 0;
    end
    else begin
      out <= out + 1 + out_wire;
    end
  end
  
  place_holder_2 test_1(
    .CLK (CLK),
    .RST (RST),
    .out (out_wire)
  );
  
endmodule

module place_holder_2 (
  input  CLK,
  input  RST,
  output out
);
  
  always @(posedge CLK) begin
    if (RST) begin
      out <= 0;
    end
    else begin
      out <= out + 2;
    end
  end
    
endmodule

