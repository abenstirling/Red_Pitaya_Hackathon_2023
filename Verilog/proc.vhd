--------------------------------------------------------------------------------
-- Company: FE
-- Engineer: A. Trost
--
-- Design Name: proc
-- Project Name: Red Pitaya V0.94
-- Target Device: Red Pitaya
-- Tool versions: Vivado 2020.1
-- Description: Morse demo code
-- Sys Registers: 403_00050 ID & start; 00054 threshold; 00058 morse tick
--                    0005C pulse/sample; 00060 sampled data
--------------------------------------------------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.all;
use IEEE.NUMERIC_STD.all;

entity proc is
  port (
    clk_i   : in  std_logic;                      -- bus clock 
    rstn_i  : in  std_logic;                      -- bus reset - active low
    dat_a_i, dat_b_i  : in  std_logic_vector(13 downto 0); -- input (IN1 and IN2)
    dat_a_o, dat_b_o  : out std_logic_vector(13 downto 0); -- output (OUT1 and OUT2)
      
    sys_addr  : in  std_logic_vector(31 downto 0);  -- bus address
    sys_wdata : in  std_logic_vector(31 downto 0);  -- bus write data          
    sys_wen   : in  std_logic;                      -- bus write enable
    sys_ren   : in  std_logic;                      -- bus read enable
    sys_rdata : out std_logic_vector(31 downto 0);  -- bus read data
    sys_err   : out std_logic;                      -- bus error indicator
    sys_ack   : out std_logic                       -- bus acknowledge signal
    );
end proc;

architecture Behavioral of proc is

    -- REGISTER MAP INTERFACE --
    constant REG_ID:       std_logic_vector(19 downto 0)   := x"00050";
    constant REG_ACQ_THR:  std_logic_vector(19 downto 0)   := x"00054";
    constant REG_SR_OUT:   std_logic_vector(19 downto 0)   := x"00058";
    constant REG_SR_IN:    std_logic_vector(19 downto 0)   := x"0005C";
    constant REG_DATA_RX:  std_logic_vector(19 downto 0)   := x"00060";
    constant REG_DATA_TX:  std_logic_vector(19 downto 0)   := x"00064";
    constant REG_STATE:    std_logic_vector(19 downto 0)   := x"00068";
    constant REG_DECIMATE: std_logic_vector(19 downto 0)   := x"0006C";
    constant REG_DATA_RX_DEC:  std_logic_vector(19 downto 0)   := x"00070";

    -- DEFAULT REGISTER VALS --
    constant DEFAULT_REG_STATE: std_logic_vector(31 downto 0)   := x"FEED0000";

    -- TRANSMISSION PART --

    -- a small demo memory (ROM) initialized to Morse sequence: . ... --- EHO in reverse bit order
    type romt is array(31 downto 0) of std_logic;
    signal rom: romt := ('0','0','0','0','0','0','0','0','0','1','1','1','0','1','1','1','0','1','1','1','0','0','0','1','0','1','0','1','0','0','0','1');
    signal rom_addr : unsigned(4 downto 0) := "00000";
    
    -- counters for generating high-frequency LED pulses (dperiod) and morse timing tick (cperiod), dperiod < cperiod
    signal c:       unsigned(15 downto 0) := (others => '0');
    signal d:       unsigned(15 downto 0) := (others => '0');
    signal cperiod: unsigned(15 downto 0) := (others => '0');
    signal dperiod: unsigned(15 downto 0) := (others => '0');

    signal decimate: unsigned(15 downto 0) := (others => '0');

    signal sample: std_logic := '0';
    signal pulse:  std_logic := '0';
    signal tick:   std_logic := '0';
    signal morse:  std_logic := '0';
    
    signal threshold: signed(13 downto 0); -- 14-bit threshold

    -- ACQUISITION PART --
    type ramt is array(0 to 1023) of std_logic;                -- type declaration RAM    

    -- RX RAM (FIFO) structures
    signal rx_ram:    ramt := (others => ('0'));               -- Oversampled Rx Data

    signal rx_dat:   std_logic;                                -- Rx RAM output data (raw)
    signal rx_dat_decim:   std_logic;                          -- Rx RAM output data (decimated)
    signal state_rx: unsigned(1 downto 0) := (others => '0');  -- state
    signal rx_wcnt:  unsigned(7 downto 0) := (others => '0');  -- read and write counter    
    signal rx_rcnt:  unsigned(7 downto 0) := (others => '0');  -- read and write counter    

    -- TX RAM (FIFO) structures
    signal tx_ram: ramt := (others => ('0'));
    signal tx_dat:   std_logic;
    signal state_tx: unsigned(1 downto 0) := (others => '0');
    signal tx_wcnt:  unsigned(7 downto 0) := (others => '0');
    signal tx_rcnt:  unsigned(7 downto 0) := (others => '0');

    signal thr_a: std_logic;                                    -- thresholded data    
    signal ren2:  std_logic;                                    -- delayed read enable
    signal trig: unsigned(1 downto 0) := (others => '0');       -- trigger

begin
    -- ############################################################
    -- ### Ports Logic
    -- ############################################################

    -- generate output by modulating morse with pulses (either maximal possible positive value or 0)
    dat_a_o <= "01111111111111" when (morse and pulse)='1' else "00000000000000";   -- pulsed signal

    -- !!!!!! generate binary signal on output !!!!!!!!!
    dat_b_o <= "01111111111111" when morse='1' else "00000000000000";               -- binary signal (not pulsed) - test

    -- check if input data is bigger than the threshold and convert to binary (simple data filter)
    thr_a <= '1' when signed(dat_a_i) > threshold else '0';

    -- ignore errors  
    sys_err <= '0';

    -- ############################################################
    -- ### LED Pulse Process
    -- ############################################################
    ppulse: process(clk_i)
    begin 
        if rising_edge(clk_i) then
            sample <= '0';
            if rstn_i = '0' then                        -- reset active low
                c <= (others=>'0');
                d <= (others=>'0');
                tick <= '0';
                pulse <= '0';
            else 
                -- modulo counter for morse tick (active one clk_i cycle)
                if c = cperiod then 
                    c <= (others=>'0');
                    tick <= '1';            -- When tick == '1' => new symbol from ROM
                else
                    c <= c + 1; tick <= '0';
                end if;
                
                -- modulo counter for IR LED pulses and sampling
                if d = dperiod then 
                    d <= (others=>'0');
                    sample <= '1';
                    pulse <= not pulse; -- pulsing the LED
                else
                    d <= d + 1;
                end if;
            end if;   
        end if;
    end process;
    
    -- read data from memory, tick defines reading frequency
    pread: process(clk_i)
    begin
        if rising_edge(clk_i) then
            morse <= rom(to_integer(rom_addr)); 
            if rstn_i = '0' then
                rom_addr <= (others=>'0');
            elsif tick = '1' then
                rom_addr <= rom_addr + 1;
            end if;
        end if;
    end process;


    -- ############################################################
    -- ### ACQUISITION ### --
    -- ############################################################

    pram: process(clk_i)                -- read and write data to RAM
    begin
        if rising_edge(clk_i) then
            if state_rx = "01" and sample='1' then        -- write data state
                rx_ram(to_integer(rx_wcnt)) <= thr_a;     -- write thresholded data to RAM
            end if;

            rx_dat       <= rx_ram(to_integer(rx_rcnt));            -- data from RAM (32-bit) to output
            rx_dat_decim <= rx_ram(to_integer(rx_rcnt*decimate));   -- data from RAM (32-bit) to output
        end if;
    end process pram;

    -- registers, write & control logic
    pbus: process(clk_i)
    begin 
        if rising_edge(clk_i) then

            if rstn_i = '0' then                    -- !!!!! Recalculate cperiod and dperiod for generating 57.6 kHz !!!!
                cperiod <= x"0020";                 -- set initial values for simulation purpose... (freq around 7.8 MHz)
                dperiod <= x"0004";
                threshold <= to_signed(200, 14);    -- default threshold (cca. 0.5V at 20V input)
                decimate <= x"0004";
            else
                sys_ack <= sys_wen or sys_ren;      -- acknowledge transactions
            
                if sys_wen='1' then                 -- decode address & write registers
                    case sys_addr(19 downto 0) is
                        when REG_ID =>
                            rx_wcnt <= (others => '0');
                            rx_rcnt <= (others => '0');

                        when REG_ACQ_THR =>
                            threshold <= signed(sys_wdata(13 downto 0));

                        when REG_SR_OUT =>
                            cperiod <= unsigned(sys_wdata(15 downto 0));  -- 16-bit tick period

                        when REG_SR_IN =>
                            dperiod <= unsigned(sys_wdata(15 downto 0));  -- 16-bit pulse/sample period

                        when REG_DECIMATE =>
                            decimate <= unsigned(sys_wdata(15 downto 0)); -- 16-bit pulse/sample period

                        when others =>
                            threshold <= threshold;
                            dperiod   <= dperiod;  -- 16-bit pulse/sample period
                            cperiod   <= cperiod;  -- 16-bit tick period
                    end case;
               end if;    
            end if; 

            -- creating a delayed read enable signal for reading on falling edge of ren
            ren2 <= sys_ren;

            if (ren2 = '1' and sys_ren = '0' and sys_addr(19 downto 0) = REG_DATA_RX) then   -- increasing read counter on falling edge
                rx_rcnt <= rx_rcnt +1;
            end if;

            -- Trigger -- two bits for saving previous state and this state (edge detection)
            if sample = '1' then
                if thr_a = '1' then
                    trig(0) <= '1';
                else
                    trig(0) <= '0';
                end if;
                
                trig(1) <= trig(0);
            end if;
            
            -- State machine for reading and writing data from ACQ RAM (same as in one of the exercises)
            if state_rx = "00" then                                                  -- reset state
                if (sys_wen = '1' and sys_addr(19 downto 0) = X"00050") then
                    state_rx <= "10";
                end if;   
            elsif state_rx = "10" then                                               -- wait for trigger state
               rx_wcnt <= (others => '0');    -- reset write counter
               if trig = "01" then         -- positive edge of signal
                   state_rx <= "01";
               end if;
            elsif state_rx = "01" and sample = '1' then    -- write data state
               rx_wcnt <= rx_wcnt +1;            -- increase write counter
               if rx_wcnt = X"FF" then        -- when RAM full
                   state_rx <= "11";
               end if;
            elsif state_rx = "11" then                                               -- stop state
               if (sys_wen = '1' and sys_addr(19 downto 0) = X"00050") then
                   state_rx <= "10";
               end if;
        end if;
     end if;

            
    end process;
    
    -- ############################################################
    -- ##   Register Read Interface
    -- ############################################################

    with sys_addr(19 downto 0) select
       sys_rdata <= DEFAULT_REG_STATE                         when REG_ID,
                    std_logic_vector(resize(threshold, 32))   when REG_ACQ_THR,
                    X"0000" & std_logic_vector(cperiod)       when REG_SR_OUT,
                    X"0000" & std_logic_vector(dperiod)       when REG_SR_IN,
                    X"0000000" & "000" & rx_dat               when REG_DATA_RX,
                    X"0000000" & "000" & rx_dat_decim         when REG_DATA_RX_DEC,
                    X"00000000"                               when REG_DATA_TX,
                    std_logic_vector(resize(state_rx, 32))    when REG_STATE,
                    X"0000" & std_logic_vector(decimate)      when REG_DECIMATE,
                    X"00000000"                               when others;


end Behavioral;
