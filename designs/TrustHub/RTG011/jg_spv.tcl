##################################################################
### File Name: jg_spv.tcl
### File for security path verification of a design 
##
##     Developed by 
##
##     Nusrat Farzna Dipu
##     Graduate Research Assistant
##     University of Florida
##     Email: ndipu@ufl.edu
##
###################################################################
set ROOT_PATH [pwd]
set RTL_PATH ${ROOT_PATH}/src
analyze -v2k \
	${RTL_PATH}/avalanche_entropy.v \
	${RTL_PATH}/chacha_core.v\
	${RTL_PATH}/chacha_qr.v \
	${RTL_PATH}/chacha.v \
	${RTL_PATH}/pseudo_entropy.v \
	${RTL_PATH}/rosc_entropy.v \
	${RTL_PATH}/sha512_core.v \
	${RTL_PATH}/sha512_h_constants.v \
	${RTL_PATH}/sha512_k_constants.v \
	${RTL_PATH}/sha512.v \
	${RTL_PATH}/sha512_w_mem.v \
	${RTL_PATH}/trng_csprng_fifo.v \
	${RTL_PATH}/trng_csprng.v \
	${RTL_PATH}/trng_debug_ctrl.v \
	${RTL_PATH}/trng_mixer.v \
	${RTL_PATH}/trng.v


elaborate -top {trng}


clock clk
reset reset_n


check_spv -create -from {debug_update} -to {mixer_inst.mixer_ctrl_reg} -name "debug_to_mixer"

prove -all
