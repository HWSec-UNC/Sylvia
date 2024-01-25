`timescale 1ns / 1ps
`default_nettype none
`define assert(expression) \
        if (!(expression)) begin \
            $display("ASSERTION FAILED"); \
            $finish; \
        end       

module updowncounter(
    input wire clock,
    input wire reset,
    input wire inst,    // 1-bit instruction. 
                        // 0 <-> count up
                        // 1 <-> count down
    output wire [31:0] value
    );
    
    reg [31:0] internalvalue;
    reg [31:0] internalvalue2;
    
    always @(posedge clock) begin
        if (reset) begin
            internalvalue <= 0;
        end
        else if (inst) begin 
            internalvalue <= internalvalue - 1;
        end
        else begin
            internalvalue <= internalvalue + 1;
        end
    end 

        
    always @(posedge clock) begin
       internalvalue2 <= internalvalue2 + 1;
    end 

    assign value = internalvalue;

    always @(posedge clock) begin
   `assert (value == 1)
    end
    
    
endmodule
