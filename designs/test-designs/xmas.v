module top (
    input clk,
    input [31:0] i_data,
    input i_irdy, o_trdy,
    output [31:0] o_data,
    output o_irdy, i_trdy
);

    wire [31:0] data;
    wire irdy, trdy;
    wire q1_is_empty, q1_is_full;
    wire q2_is_empty, q2_is_full;

    queue q1(.clk(clk),
             .write_data(i_data),
             .write_en(i_irdy), .read_en(trdy),
             .read_data(data),
             .is_empty(q1_is_empty), .is_full(q1_is_full));

    // Handshake signals
    assign irdy = ~q1_is_empty;
    assign trdy = ~q2_is_full;

    assign i_trdy = ~q1_is_full;
    assign o_irdy = ~q2_is_empty;

    queue q2(.clk(clk),
             .write_data(data),
             .write_en(irdy), .read_en(o_trdy),
             .read_data(o_data),
             .is_empty(q2_is_empty), .is_full(q2_is_full));


endmodule

module queue (
    input clk, 
    input [31:0] write_data,
    input write_en, read_en,
    output [31:0] read_data,
    output is_empty, is_full
);

    
    reg [31:0] contents = 0;
    reg [1:0] in_use = 0;

    always @(posedge clk) begin
        if (write_en) begin
            contents <= write_data;
            in_use <= 1;
        end

        if (read_en) begin
            in_use <= 0;
        end
    end

    assign read_data = (read_en) ? contents : 0;
    assign is_empty = in_use[0];
    assign is_full = ~is_empty;

endmodule