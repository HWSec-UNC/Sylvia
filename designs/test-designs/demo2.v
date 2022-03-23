module demo (
    input clk, 
    input enable, out1_visible,
    input [31:0] secret,
    output [31:0] out2, out1
);

    /* The single-cycle composite flow
        secret -> temp1 -> out1
       is possible, since
       (enable & out1_visible & enable) is satisfiable.
    */
    wire [31:0] temp1 = (enable) ? secret : 0;
    assign out1 = (out1_visible & enable) ? temp1 : 0;

    /* The composite flow
        secret -> guard -> out2
       is impossible because of an invariant of execution.
       We always have prev = state - 1, but this flow
       requires (state == 3) on one clock cycle
       and (prev == 1) on the next.
    */

    reg [1:0] state = 0;
    reg [1:0] prev = 2;
    
    reg [31:0] guard = 0;

    always @(posedge clk) begin
        if (enable) begin
            state <= state + 1;
            prev <= prev + 1;
        end

        if (state == 3)
            guard <= secret;
        else
            guard <= 0;
    end

    assign out2 = (prev == 2) ? guard + 1: 0;

endmodule
