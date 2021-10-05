`timescale 1ns / 1ps
`default_nettype none
`define assert(signal, value) \
        if (signal !== value) begin \
            $display("ASSERTION FAILED"); \
            $finish; \
        end       
    
//////////////////////////////////////////////////////////////////////////////////
// Company: UNC Hardware Security Group
// Engineer: Martin Meng
// 
// Create Date: 03/26/2020 10:09:36 PM
// Design Name: 
// Module Name: updowncounter
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module updowncounter(
    input wire clock,
    input wire reset,
    input wire inst,    // 1-bit instruction. 
                        // 0 <-> count up
                        // 1 <-> count down
    output wire [31:0] value
    );
    
    reg [31:0] internalvalue;
    
    always @(posedge clock) begin
        if (reset) begin
           internalvalue <= 0;
        end
        if (inst) begin 
            internalvalue <= internalvalue - 1;
        end
        else begin
            internalvalue <= internalvalue + 1;
        end
    end 
    
    assign value = internalvalue;

    initial begin
    `assert(value, 1)
    end
    
    
endmodule
