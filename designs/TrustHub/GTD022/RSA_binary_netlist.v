
module RSA_binary ( clk, start, finished );
  input clk, start;
  output finished;
  wire   N14, N15, N16, N17, N18, N19, N20, N21, N22, N23, N24, N25, N26, N27,
         N28, N29, N30, N31, N32, N33, N34, N35, N38, N39, N40, N41, N54, N55,
         N56, N57, N61, N62, N63, N64, n8, n9, n10, n11, n12, n13, n14, n15,
         n16, n17, n18, n19, n20, n21, n22;
  wire   [2:0] FSM;
  wire   [2:0] next_FSM;
  wire   [3:0] round_index;
  wire   [3:0] next_round_index;
  wire   [3:2] add_158_carry;

  ADDHX1 add_158_U1_1_1 ( .A(round_index[1]), .B(round_index[0]), .CO(
        add_158_carry[2]), .S(N61) );
  ADDHX1 add_158_U1_1_2 ( .A(round_index[2]), .B(add_158_carry[2]), .CO(
        add_158_carry[3]), .S(N62) );
  XOR2X1 add_158_U2 ( .A(round_index[3]), .B(add_158_carry[3]), .Y(N63) );
  INVX1 I_15 ( .A(N55), .Y(N56) );
  INVX1 I_9 ( .A(N33), .Y(N34) );
  INVX1 I_8 ( .A(N30), .Y(N31) );
  INVX1 I_7 ( .A(N27), .Y(N28) );
  INVX1 I_6 ( .A(FSM[2]), .Y(N25) );
  INVX1 I_5 ( .A(N23), .Y(N24) );
  INVX1 I_4 ( .A(N20), .Y(N21) );
  INVX1 I_3 ( .A(FSM[1]), .Y(N18) );
  INVX1 I_2 ( .A(N16), .Y(N17) );
  INVX1 I_1 ( .A(FSM[0]), .Y(N14) );
  AND2X1 C98 ( .A(N25), .B(N18), .Y(N57) );
  OR2X1 C92 ( .A(N25), .B(N18), .Y(N54) );
  OR2X1 C60 ( .A(round_index[0]), .B(N40), .Y(N41) );
  OR2X1 C59 ( .A(N38), .B(N39), .Y(N40) );
  OR2X1 C58 ( .A(round_index[2]), .B(round_index[3]), .Y(N39) );
  INVX1 I_0 ( .A(round_index[1]), .Y(N38) );
  AND2X1 C34 ( .A(N25), .B(N18), .Y(N35) );
  OR2X1 C28 ( .A(N25), .B(N18), .Y(N32) );
  OR2X1 C23 ( .A(N25), .B(FSM[1]), .Y(N29) );
  OR2X1 C18 ( .A(N25), .B(FSM[1]), .Y(N26) );
  OR2X1 C14 ( .A(FSM[2]), .B(N18), .Y(N22) );
  OR2X1 C9 ( .A(FSM[2]), .B(N18), .Y(N19) );
  OR2X1 C5 ( .A(FSM[2]), .B(FSM[1]), .Y(N15) );
  DFFSRX1 FSM_reg_0_ ( .D(next_FSM[0]), .CK(clk), .RN(1'b1), .SN(1'b1), .Q(
        FSM[0]) );
  DFFSRX1 FSM_reg_2_ ( .D(next_FSM[2]), .CK(clk), .RN(1'b1), .SN(1'b1), .Q(
        FSM[2]) );
  DFFSRX1 FSM_reg_1_ ( .D(next_FSM[1]), .CK(clk), .RN(1'b1), .SN(1'b1), .Q(
        FSM[1]) );
  DFFSRX1 round_index_reg_1_ ( .D(n19), .CK(clk), .RN(1'b1), .SN(1'b1), .Q(
        round_index[1]) );
  DFFSRX1 round_index_reg_2_ ( .D(n20), .CK(clk), .RN(1'b1), .SN(1'b1), .Q(
        round_index[2]) );
  DFFSRX1 round_index_reg_3_ ( .D(n21), .CK(clk), .RN(1'b1), .SN(1'b1), .Q(
        round_index[3]) );
  AND2X1 U10 ( .A(N63), .B(N56), .Y(next_round_index[3]) );
  AND2X1 U11 ( .A(N62), .B(N56), .Y(next_round_index[2]) );
  AND2X1 U12 ( .A(N61), .B(N56), .Y(next_round_index[1]) );
  NOR2X1 U13 ( .A(round_index[0]), .B(n8), .Y(next_round_index[0]) );
  INVX1 U14 ( .A(N56), .Y(n8) );
  NAND2X1 U15 ( .A(n9), .B(n10), .Y(next_FSM[2]) );
  NOR2X1 U16 ( .A(N31), .B(N24), .Y(n9) );
  NAND3X1 U17 ( .A(n11), .B(n12), .C(n13), .Y(next_FSM[1]) );
  NAND2X1 U18 ( .A(start), .B(N17), .Y(n13) );
  INVX1 U19 ( .A(N31), .Y(n12) );
  INVX1 U20 ( .A(N21), .Y(n11) );
  NAND2X1 U21 ( .A(n14), .B(n15), .Y(next_FSM[0]) );
  AOI21X1 U22 ( .A0(N35), .A1(N14), .B0(N21), .Y(n15) );
  AOI21X1 U23 ( .A0(N17), .A1(n16), .B0(n17), .Y(n14) );
  INVX1 U24 ( .A(n10), .Y(n17) );
  AOI21X1 U25 ( .A0(N41), .A1(N34), .B0(N28), .Y(n10) );
  INVX1 U26 ( .A(start), .Y(n16) );
  AND2X1 U27 ( .A(N57), .B(N14), .Y(finished) );
  NAND2X1 U28 ( .A(FSM[2]), .B(n18), .Y(N64) );
  OR2X1 U29 ( .A(N54), .B(n18), .Y(N55) );
  OR2X1 U30 ( .A(N32), .B(n18), .Y(N33) );
  OR2X1 U31 ( .A(N14), .B(N29), .Y(N30) );
  OR2X1 U32 ( .A(N26), .B(n18), .Y(N27) );
  OR2X1 U33 ( .A(N14), .B(N22), .Y(N23) );
  OR2X1 U34 ( .A(N19), .B(n18), .Y(N20) );
  INVX1 U35 ( .A(N14), .Y(n18) );
  OR2X1 U36 ( .A(N14), .B(N15), .Y(N16) );
  MX2X1 U37 ( .A(round_index[0]), .B(next_round_index[0]), .S0(N64), .Y(n22)
         );
  MX2X1 U38 ( .A(round_index[3]), .B(next_round_index[3]), .S0(N64), .Y(n21)
         );
  MX2X1 U39 ( .A(round_index[2]), .B(next_round_index[2]), .S0(N64), .Y(n20)
         );
  MX2X1 U40 ( .A(round_index[1]), .B(next_round_index[1]), .S0(N64), .Y(n19)
         );
  DFFSRX1 round_index_reg_0_ ( .D(n22), .CK(clk), .RN(1'b1), .SN(1'b1), .Q(
        round_index[0]) );
endmodule

