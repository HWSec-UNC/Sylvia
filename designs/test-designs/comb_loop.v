module demo (
    input clk, 
    input a,
    output out1
);

    wire b;

    assign b = b ^ a;

    assign out1 = b;


endmodule