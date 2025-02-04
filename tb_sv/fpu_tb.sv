`timescale 1ns/1ps

module fpu_tb;
    // Parameters
    localparam EXPONENT_WIDTH = 8;
    localparam MANTISSA_WIDTH = 23;
    localparam CLK_PERIOD = 10;

    // Signals
    logic clk;
    logic rst_n;
    logic valid_in;
    logic [EXPONENT_WIDTH+MANTISSA_WIDTH:0] operand_a;
    logic [EXPONENT_WIDTH+MANTISSA_WIDTH:0] operand_b;
    logic [2:0] operation;
    logic [EXPONENT_WIDTH+MANTISSA_WIDTH:0] result;
    logic valid_out;
    logic exception;

    // Clock generation
    initial begin
        clk = 0;
        forever #(CLK_PERIOD/2) clk = ~clk;
    end

    // DUT instantiation
    fpu #(
        .EXPONENT_WIDTH(EXPONENT_WIDTH),
        .MANTISSA_WIDTH(MANTISSA_WIDTH)
    ) dut (
        .clk(clk),
        .rst_n(rst_n),
        .valid_in(valid_in),
        .operand_a(operand_a),
        .operand_b(operand_b),
        .operation(operation),
        .result(result),
        .valid_out(valid_out),
        .exception(exception)
    );

    // Test stimulus
    initial begin
        // Initialize
        rst_n = 0;
        valid_in = 0;
        operand_a = 0;
        operand_b = 0;
        operation = 0;

        // Wait 100ns and release reset
        #100 rst_n = 1;
        
        // Test case 1: Addition
        #20;
        valid_in = 1;
        operand_a = 32'h3F800000; // 1.0
        operand_b = 32'h3F800000; // 1.0
        operation = 3'b000;       // ADD
        #10;
        valid_in = 0;
        
        // Wait for result
        @(posedge valid_out);
        $display("Addition Result: %h", result);
        
        // Test case 2: Multiplication
        #20;
        valid_in = 1;
        operand_a = 32'h40000000; // 2.0
        operand_b = 32'h40000000; // 2.0
        operation = 3'b010;       // MUL
        #10;
        valid_in = 0;
        
        // Wait for result
        @(posedge valid_out);
        $display("Multiplication Result: %h", result);
        
        // Add more test cases here
        
        #100;
        $finish;
    end

    // Assertions
    property valid_out_follows_valid_in;
        @(posedge clk) disable iff (!rst_n)
        valid_in |-> ##[1:3] valid_out;
    endproperty

    assert property (valid_out_follows_valid_in)
    else $error("Valid out did not assert within expected time after valid_in");

endmodule
