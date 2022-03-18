module soc_event_queue (
	clk_i,
	rstn_i,
	event_i,
	err_o,
	event_o,
	event_ack_i
);
	parameter QUEUE_SIZE = 2;
	input wire clk_i;
	input wire rstn_i;
	input wire event_i;
	output wire err_o;
	output wire event_o;
	input wire event_ack_i;
	reg [1:0] r_event_count;
	reg [1:0] s_event_count;
	wire s_sample_event;
	assign err_o = event_i & (r_event_count == 2'b11);
	assign event_o = r_event_count != 0;
	assign s_sample_event = event_i | event_ack_i;
	always @(*) begin : proc_s_event_count
		s_event_count = r_event_count;
		if (event_ack_i) begin
			if (!event_i && (r_event_count != 0))
				s_event_count = r_event_count - 1;
		end
		else if (r_event_count != 2'b11)
			s_event_count = r_event_count + 1;
	end
	always @(posedge clk_i or negedge rstn_i) begin : proc_r_event_count
		if (~rstn_i)
			r_event_count <= 0;
		else if (s_sample_event)
			r_event_count <= s_event_count;
	end
endmodule
