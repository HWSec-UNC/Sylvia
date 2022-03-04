/////////////////////////////////////////////////////////////
// Created by: Synopsys DC Expert(TM) in wire load mode
// Version   : R-2020.09-SP4
// Date      : Sun May  9 13:02:41 2021
/////////////////////////////////////////////////////////////


module RSA_binary ( clk, start, finished, test_se, RESET, test_si, test_so );
  input clk, start, test_se, RESET, test_si;
  output finished, test_so;
  wire   n15, n16, n17, n18, n19, n20, n21, n22, n23, n24, n25, n26, n27, n28,
         n29, n30, n31, n32, n33, n34, n35, n36, n37, n38, n39, n40, n41, n42,
         n43;
  wire   [2:0] FSM;
  wire   [2:0] next_FSM;
  wire   [2:0] round_index;

  SDFFSRX1 round_index_reg_0_ ( .D(n43), .SI(FSM[2]), .SE(test_se), .CK(clk), 
        .SN(1'b1), .RN(1'b1), .Q(round_index[0]), .QN(n25) );
  SDFFSRX1 FSM_reg_0_ ( .D(next_FSM[0]), .SI(test_si), .SE(test_se), .CK(clk), 
        .SN(1'b1), .RN(1'b1), .Q(FSM[0]), .QN(n20) );
  SDFFSRX1 FSM_reg_2_ ( .D(next_FSM[2]), .SI(FSM[1]), .SE(test_se), .CK(clk), 
        .SN(1'b1), .RN(1'b1), .Q(FSM[2]), .QN(n17) );
  SDFFSRX1 FSM_reg_1_ ( .D(next_FSM[1]), .SI(FSM[0]), .SE(test_se), .CK(clk), 
        .SN(1'b1), .RN(1'b1), .Q(FSM[1]), .QN(n19) );
  SDFFSRX1 round_index_reg_1_ ( .D(n41), .SI(round_index[0]), .SE(test_se), 
        .CK(clk), .SN(1'b1), .RN(1'b1), .Q(round_index[1]), .QN(n24) );
  SDFFSRX1 round_index_reg_2_ ( .D(n40), .SI(round_index[1]), .SE(test_se), 
        .CK(clk), .SN(1'b1), .RN(1'b1), .Q(round_index[2]), .QN(n23) );
  SDFFSRX1 round_index_reg_3_ ( .D(n42), .SI(round_index[2]), .SE(test_se), 
        .CK(clk), .SN(1'b1), .RN(1'b1), .Q(test_so), .QN(n22) );
  INVX1 U20 ( .A(n29), .Y(n15) );
  INVX1 U21 ( .A(n38), .Y(n16) );
  INVX1 U22 ( .A(n32), .Y(n18) );
  INVX1 U23 ( .A(n28), .Y(n21) );
  OAI21X1 U24 ( .A0(n26), .A1(n17), .B0(n27), .Y(next_FSM[2]) );
  NAND3X1 U25 ( .A(FSM[0]), .B(n17), .C(FSM[1]), .Y(n27) );
  AOI21X1 U26 ( .A0(n28), .A1(n20), .B0(n19), .Y(n26) );
  OAI33X1 U27 ( .A0(n19), .A1(FSM[2]), .A2(FSM[0]), .B0(n20), .B1(FSM[1]), 
        .B2(n29), .Y(next_FSM[1]) );
  OAI21X1 U28 ( .A0(FSM[1]), .A1(n15), .B0(n30), .Y(next_FSM[0]) );
  AOI21X1 U29 ( .A0(n16), .A1(FSM[0]), .B0(n31), .Y(n30) );
  AOI21X1 U30 ( .A0(n16), .A1(n21), .B0(FSM[0]), .Y(n31) );
  NAND4X1 U31 ( .A(round_index[1]), .B(n25), .C(n23), .D(n22), .Y(n28) );
  NOR2X1 U32 ( .A(FSM[2]), .B(start), .Y(n29) );
  OAI33X1 U33 ( .A0(n23), .A1(n32), .A2(n17), .B0(n33), .B1(round_index[2]), 
        .B2(n24), .Y(n40) );
  OAI21X1 U34 ( .A0(round_index[1]), .A1(n33), .B0(n34), .Y(n41) );
  NAND3X1 U35 ( .A(round_index[1]), .B(n35), .C(FSM[2]), .Y(n34) );
  OAI33X1 U36 ( .A0(n22), .A1(n36), .A2(n17), .B0(n37), .B1(n33), .B2(n23), 
        .Y(n42) );
  NAND3X1 U37 ( .A(n16), .B(n20), .C(round_index[0]), .Y(n33) );
  AOI21X1 U38 ( .A0(FSM[1]), .A1(n23), .B0(n18), .Y(n36) );
  AOI21X1 U39 ( .A0(n24), .A1(FSM[1]), .B0(n35), .Y(n32) );
  OAI21X1 U40 ( .A0(round_index[0]), .A1(n19), .B0(n20), .Y(n35) );
  OAI33X1 U41 ( .A0(n25), .A1(n20), .A2(n17), .B0(n38), .B1(round_index[0]), 
        .B2(FSM[0]), .Y(n43) );
  NOR2X1 U42 ( .A(FSM[0]), .B(n39), .Y(finished) );
  NAND2X1 U43 ( .A(round_index[1]), .B(n22), .Y(n37) );
  NAND2X1 U44 ( .A(FSM[2]), .B(FSM[1]), .Y(n38) );
  NAND2X1 U45 ( .A(n19), .B(n17), .Y(n39) );
endmodule

