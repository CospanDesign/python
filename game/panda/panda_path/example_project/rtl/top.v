//Top HDL




module top (
  output                siwua,
  output                cas,
  output                dqml,
  output                we,
  input                 clk,
  input                 txe_n,
  input                 rxe_n,
  input                 PMODA4,
  output                PMODA2,
  output                cke,
  output      [11:0]    a,
  output                rd_n,
  output                ras,
  input       [1:0]     button,
  inout       [15:0]    dq,
  input                 ftdi_clk,
  output      [1:0]     ba,
  output      [1:0]     led,
  input                 rst,
  output                PMODA1,
  inout       [7:0]     d,
  output                dqmh,
  input                 PMODA3,
  output                cs_n,
  output                oe_n,
  output                sdram_clk,
  output                wr_n
);

//General Signals
wire                rst_n;

//input handler signals
wire  [31:0]        in_command;
wire  [31:0]        in_address;
wire  [31:0]        in_data;
wire  [31:0]        in_data_count;
wire                ih_ready;
wire                ih_reset;

//output handler signals
wire  [31:0]        out_status;
wire  [31:0]        out_address;
wire  [31:0]        out_data;
wire  [27:0]        out_data_count;
wire                oh_ready;
wire                oh_en;

//master signals
wire                master_ready;
wire                wbm_we_o;
wire                wbm_cyc_o;
wire                wbm_stb_o;
wire  [3:0]         wbm_sel_o;
wire  [31:0]        wbm_adr_o;
wire  [31:0]        wbm_dat_i;
wire  [31:0]        wbm_dat_o;
wire                wbm_ack_i;
wire                wbm_int_i;
wire                mem_we_o;
wire                mem_cyc_o;
wire                mem_stb_o;
wire  [3:0]         mem_sel_o;
wire  [31:0]        mem_adr_o;
wire  [31:0]        mem_dat_i;
wire  [31:0]        mem_dat_o;
wire                mem_ack_i;
wire                mem_int_i;
wire  [31:0]        wbm_debug_out;

//slave signals

//slave 0
wire                s0_i_wbs_we;
wire                s0_i_wbs_cyc;
wire  [31:0]        s0_i_wbs_dat;
wire  [31:0]        s0_o_wbs_dat;
wire  [31:0]        s0_i_wbs_adr;
wire                s0_i_wbs_stb;
wire  [3:0]         s0_i_wbs_sel;
wire                s0_o_wbs_ack;
wire                s0_o_wbs_int;
//slave 1
wire                s1_i_wbs_we;
wire                s1_i_wbs_cyc;
wire  [31:0]        s1_i_wbs_dat;
wire  [31:0]        s1_o_wbs_dat;
wire  [31:0]        s1_i_wbs_adr;
wire                s1_i_wbs_stb;
wire  [3:0]         s1_i_wbs_sel;
wire                s1_o_wbs_ack;
wire                s1_o_wbs_int;
//slave 2
wire                s2_i_wbs_we;
wire                s2_i_wbs_cyc;
wire  [31:0]        s2_i_wbs_dat;
wire  [31:0]        s2_o_wbs_dat;
wire  [31:0]        s2_i_wbs_adr;
wire                s2_i_wbs_stb;
wire  [3:0]         s2_i_wbs_sel;
wire                s2_o_wbs_ack;
wire                s2_o_wbs_int;

//mem slave 0
wire                sm0_i_wbs_we;
wire                sm0_i_wbs_cyc;
wire  [31:0]        sm0_i_wbs_dat;
wire  [31:0]        sm0_o_wbs_dat;
wire  [31:0]        sm0_i_wbs_adr;
wire                sm0_i_wbs_stb;
wire  [3:0]         sm0_i_wbs_sel;
wire                sm0_o_wbs_ack;
wire                sm0_o_wbs_int;


//Startup reset

wire                 startup_rst;

startup start(
  .clk                 (clk                 ),
  .startup_rst         (startup_rst         )
);




//Wishbone Master

wishbone_master wm (
  .clk                 (clk                 ),
  .rst                 (rst_n | startup_rst ),

  //input handler signals
  .i_ready             (ih_ready            ),
  .i_ih_rst            (ih_reset            ),
  .i_command           (in_command          ),
  .i_address           (in_address          ),
  .i_data              (in_data             ),
  .i_data_count        (in_data_count       ),

  //output handler signals
  .i_out_ready         (oh_ready            ),
  .o_en                (oh_en               ),
  .o_status            (out_status          ),
  .o_address           (out_address         ),
  .o_data              (out_data            ),
  .o_data_count        (out_data_count      ),
  .o_master_ready      (master_ready        ),

  //interconnect signals
  .o_per_we            (wbm_we_o            ),
  .o_per_adr           (wbm_adr_o           ),
  .o_per_dat           (wbm_dat_o           ),
  .i_per_dat           (wbm_dat_i           ),
  .o_per_stb           (wbm_stb_o           ),
  .o_per_cyc           (wbm_cyc_o           ),
  .o_per_msk           (wbm_msk_o           ),
  .o_per_sel           (wbm_sel_o           ),
  .i_per_ack           (wbm_ack_i           ),
  .i_per_int           (wbm_int_i           ),

  //memory interconnect signals
  .o_mem_we            (mem_we_o            ),
  .o_mem_adr           (mem_adr_o           ),
  .o_mem_dat           (mem_dat_o           ),
  .i_mem_dat           (mem_dat_i           ),
  .o_mem_stb           (mem_stb_o           ),
  .o_mem_cyc           (mem_cyc_o           ),
  .o_mem_msk           (mem_msk_o           ),
  .o_mem_sel           (mem_sel_o           ),
  .i_mem_ack           (mem_ack_i           ),
  .i_mem_int           (mem_int_i           ),

  .o_debug             (wbm_debug_out       )

);

// io ( ft_master_interface )

//wires
wire                 i_ftdi_suspend_n;
wire                 i_ftdi_txe_n;
wire                 i_ftdi_clk;
wire                 i_ftdi_rde_n;
wire                 o_ftdi_siwu;
wire                 o_ftdi_rd_n;
wire                 o_ftdi_wr_n;
wire                 o_ftdi_oe_n;
wire  [15:0]         o_ftdi_debug;


ft_master_interface io  (
  .clk                 (clk                 ),
  .rst                 (rst_n | startup_rst ),
  .i_out_address       (out_address         ),
  .i_ftdi_suspend_n    (i_ftdi_suspend_n    ),
  .i_ftdi_txe_n        (i_ftdi_txe_n        ),
  .i_ftdi_clk          (i_ftdi_clk          ),
  .i_out_status        (out_status          ),
  .i_ftdi_rde_n        (i_ftdi_rde_n        ),
  .i_master_ready      (master_ready        ),
  .i_out_data          (out_data            ),
  .i_out_data_count    (out_data_count      ),
  .i_oh_en             (oh_en               ),
  .o_in_address        (in_address          ),
  .o_in_data_count     (in_data_count       ),
  .o_ftdi_siwu         (o_ftdi_siwu         ),
  .o_oh_ready          (oh_ready            ),
  .o_in_command        (in_command          ),
  .o_ih_reset          (ih_reset            ),
  .o_ftdi_rd_n         (o_ftdi_rd_n         ),
  .o_ih_ready          (ih_ready            ),
  .o_ftdi_wr_n         (o_ftdi_wr_n         ),
  .o_ftdi_oe_n         (o_ftdi_oe_n         ),
  .o_ftdi_debug        (o_ftdi_debug        ),
  .o_in_data           (in_data             ),
  .io_ftdi_data        (d[7:0]              )
);

//Wishbone Memory Interconnect

wishbone_interconnect wi (
  .clk                 (clk                 ),
  .rst                 (rst_n | startup_rst ),

  //master
  .i_m_we              (wbm_we_o            ),
  .i_m_cyc             (wbm_cyc_o           ),
  .i_m_stb             (wbm_stb_o           ),
  .i_m_sel             (wbm_sel_o           ),
  .o_m_ack             (wbm_ack_i           ),
  .i_m_dat             (wbm_dat_o           ),
  .o_m_dat             (wbm_dat_i           ),
  .i_m_adr             (wbm_adr_o           ),
  .o_m_int             (wbm_int_i           ),

  //slave 0
  .o_s0_we             (s0_i_wbs_we         ),
  .o_s0_cyc            (s0_i_wbs_cyc        ),
  .o_s0_stb            (s0_i_wbs_stb        ),
  .o_s0_sel            (s0_i_wbs_sel        ),
  .i_s0_ack            (s0_o_wbs_ack        ),
  .o_s0_dat            (s0_i_wbs_dat        ),
  .i_s0_dat            (s0_o_wbs_dat        ),
  .o_s0_adr            (s0_i_wbs_adr        ),
  .i_s0_int            (s0_o_wbs_int        ),

  //slave 1
  .o_s1_we             (s1_i_wbs_we         ),
  .o_s1_cyc            (s1_i_wbs_cyc        ),
  .o_s1_stb            (s1_i_wbs_stb        ),
  .o_s1_sel            (s1_i_wbs_sel        ),
  .i_s1_ack            (s1_o_wbs_ack        ),
  .o_s1_dat            (s1_i_wbs_dat        ),
  .i_s1_dat            (s1_o_wbs_dat        ),
  .o_s1_adr            (s1_i_wbs_adr        ),
  .i_s1_int            (s1_o_wbs_int        ),

  //slave 2
  .o_s2_we             (s2_i_wbs_we         ),
  .o_s2_cyc            (s2_i_wbs_cyc        ),
  .o_s2_stb            (s2_i_wbs_stb        ),
  .o_s2_sel            (s2_i_wbs_sel        ),
  .i_s2_ack            (s2_o_wbs_ack        ),
  .o_s2_dat            (s2_i_wbs_dat        ),
  .i_s2_dat            (s2_o_wbs_dat        ),
  .o_s2_adr            (s2_i_wbs_adr        ),
  .i_s2_int            (s2_o_wbs_int        )
);

//Wishbone Memory Interconnect

wishbone_mem_interconnect wmi (
  .clk                 (clk                 ),
  .rst                 (rst_n | startup_rst ),

  //master
  .i_m_we              (mem_we_o            ),
  .i_m_cyc             (mem_cyc_o           ),
  .i_m_stb             (mem_stb_o           ),
  .i_m_sel             (mem_sel_o           ),
  .o_m_ack             (mem_ack_i           ),
  .i_m_dat             (mem_dat_o           ),
  .o_m_dat             (mem_dat_i           ),
  .i_m_adr             (mem_adr_o           ),
  .o_m_int             (mem_int_i           ),


  //slave 0
  .o_s0_we             (sm0_i_wbs_we        ),
  .o_s0_cyc            (sm0_i_wbs_cyc       ),
  .o_s0_stb            (sm0_i_wbs_stb       ),
  .o_s0_sel            (sm0_i_wbs_sel       ),
  .i_s0_ack            (sm0_o_wbs_ack       ),
  .o_s0_dat            (sm0_i_wbs_dat       ),
  .i_s0_dat            (sm0_o_wbs_dat       ),
  .o_s0_adr            (sm0_i_wbs_adr       ),
  .i_s0_int            (sm0_o_wbs_int       )
);



// sdb ( device_rom_table )

//Wires


device_rom_table  sdb(
  .clk                 (clk                 ),
  .rst                 (rst_n | startup_rst ),
  .i_wbs_cyc           (s0_i_wbs_cyc        ),
  .i_wbs_stb           (s0_i_wbs_stb        ),
  .i_wbs_we            (s0_i_wbs_we         ),
  .i_wbs_dat           (s0_i_wbs_dat        ),
  .i_wbs_sel           (s0_i_wbs_sel        ),
  .i_wbs_adr           (s0_i_wbs_adr        ),
  .o_wbs_int           (s0_o_wbs_int        ),
  .o_wbs_dat           (s0_o_wbs_dat        ),
  .o_wbs_ack           (s0_o_wbs_ack        )
);



// gpio1 ( wb_gpio )

//Wires
wire  [31:0]         gpio1_gpio_in;

wire  [31:0]         gpio1_gpio_out;

wb_gpio   gpio1(
  .clk                 (clk                 ),
  .rst                 (rst_n | startup_rst ),
  .i_wbs_cyc           (s1_i_wbs_cyc        ),
  .i_wbs_dat           (s1_i_wbs_dat        ),
  .gpio_in             (gpio1_gpio_in       ),
  .i_wbs_we            (s1_i_wbs_we         ),
  .i_wbs_stb           (s1_i_wbs_stb        ),
  .i_wbs_sel           (s1_i_wbs_sel        ),
  .i_wbs_adr           (s1_i_wbs_adr        ),
  .o_wbs_int           (s1_o_wbs_int        ),
  .o_wbs_dat           (s1_o_wbs_dat        ),
  .gpio_out            (gpio1_gpio_out      ),
  .o_wbs_ack           (s1_o_wbs_ack        )
);



// uart1 ( wb_uart )

//Wires
wire                 uart1_i_rx;
wire                 uart1_i_dtr;
wire                 uart1_i_rts;

wire                 uart1_o_cts;
wire                 uart1_o_dsr;
wire                 uart1_o_tx;

wb_uart   uart1(
  .clk                 (clk                 ),
  .rst                 (rst_n | startup_rst ),
  .i_wbs_cyc           (s2_i_wbs_cyc        ),
  .i_rx                (uart1_i_rx          ),
  .i_wbs_dat           (s2_i_wbs_dat        ),
  .i_wbs_we            (s2_i_wbs_we         ),
  .i_dtr               (uart1_i_dtr         ),
  .i_wbs_stb           (s2_i_wbs_stb        ),
  .i_wbs_sel           (s2_i_wbs_sel        ),
  .i_rts               (uart1_i_rts         ),
  .i_wbs_adr           (s2_i_wbs_adr        ),
  .o_wbs_ack           (s2_o_wbs_ack        ),
  .o_wbs_dat           (s2_o_wbs_dat        ),
  .o_cts               (uart1_o_cts         ),
  .o_dsr               (uart1_o_dsr         ),
  .o_tx                (uart1_o_tx          ),
  .o_wbs_int           (s2_o_wbs_int        )
);



// mem1 ( wb_sdram )

//Wires

wire                 mem1_o_sdram_ready;
wire                 mem1_o_sdram_cs_n;
wire  [1:0]          mem1_o_sdram_data_mask;
wire                 mem1_o_ext_sdram_clk;
wire  [1:0]          mem1_o_sdram_bank;
wire                 mem1_o_sdram_ras;
wire                 mem1_o_sdram_cas;
wire  [31:0]         mem1_debug;
wire                 mem1_o_sdram_cke;
wire                 mem1_o_sdram_we;
wire  [11:0]         mem1_o_sdram_addr;
wire                 mem1_o_sdram_clk;

wb_sdram  mem1(
  .clk                 (clk                 ),
  .rst                 (rst_n | startup_rst ),
  .i_wbs_cyc           (sm0_i_wbs_cyc       ),
  .i_wbs_dat           (sm0_i_wbs_dat       ),
  .i_wbs_we            (sm0_i_wbs_we        ),
  .i_wbs_stb           (sm0_i_wbs_stb       ),
  .i_wbs_sel           (sm0_i_wbs_sel       ),
  .i_wbs_adr           (sm0_i_wbs_adr       ),
  .o_sdram_ready       (mem1_o_sdram_ready  ),
  .o_sdram_cs_n        (mem1_o_sdram_cs_n   ),
  .o_sdram_data_mask   (mem1_o_sdram_data_mask),
  .o_ext_sdram_clk     (mem1_o_ext_sdram_clk),
  .o_sdram_bank        (mem1_o_sdram_bank   ),
  .o_sdram_ras         (mem1_o_sdram_ras    ),
  .o_sdram_cas         (mem1_o_sdram_cas    ),
  .debug               (mem1_debug          ),
  .o_wbs_dat           (sm0_o_wbs_dat       ),
  .o_wbs_ack           (sm0_o_wbs_ack       ),
  .o_sdram_cke         (mem1_o_sdram_cke    ),
  .o_sdram_we          (mem1_o_sdram_we     ),
  .o_wbs_int           (sm0_o_wbs_int       ),
  .o_sdram_addr        (mem1_o_sdram_addr   ),
  .o_sdram_clk         (mem1_o_sdram_clk    ),
  .io_sdram_data       (dq[15:0]            )
);





//Bindings
assign  siwua               = o_ftdi_siwu;
assign  cas                 = mem1_o_sdram_cas;
assign  dqml                = mem1_o_sdram_data_mask[0];
assign  we                  = mem1_o_sdram_we;
assign  i_ftdi_txe_n        = txe_n;
assign  i_ftdi_rde_n        = rxe_n;
assign  uart1_i_rts         = PMODA4;
assign  PMODA2              = uart1_o_tx;
assign  cke                 = mem1_o_sdram_cke;
assign  a[11:0]             = mem1_o_sdram_addr[11:0];
assign  rd_n                = o_ftdi_rd_n;
assign  ras                 = mem1_o_sdram_ras;
assign  gpio1_gpio_in[3:2]  = button[1:0];
assign  i_ftdi_clk          = ftdi_clk;
assign  ba[1:0]             = mem1_o_sdram_bank[1:0];
assign  led[1:0]            = gpio1_gpio_out[1:0];
assign  PMODA1              = uart1_o_cts;
assign  dqmh                = mem1_o_sdram_data_mask[1];
assign  uart1_i_rx          = PMODA3;
assign  cs_n                = mem1_o_sdram_cs_n;
assign  oe_n                = o_ftdi_oe_n;
assign  sdram_clk           = mem1_o_sdram_clk;
assign  wr_n                = o_ftdi_wr_n;

//Invert Reset for this board
assign  rst_n               = ~rst;


endmodule