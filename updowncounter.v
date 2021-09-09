`timescale 1ns / 1ps
`default_nettype none
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
        internalvalue <= reset ? 0: inst ? internalvalue - 1 : internalvalue + 1;
    end 
    
    assign value = internalvalue;
    
    
endmodule