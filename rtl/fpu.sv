module fpu #(
    parameter EXPONENT_WIDTH = 8,
    parameter MANTISSA_WIDTH = 23,
    parameter CLOCK_GATING_EN = 1,    // Enable clock gating
    parameter OPERAND_ISOLATION_EN = 1 // Enable operand isolation
) (
    input  logic                                    clk,
    input  logic                                    rst_n,
    input  logic                                    valid_in,
    input  logic [EXPONENT_WIDTH+MANTISSA_WIDTH:0]  operand_a,
    input  logic [EXPONENT_WIDTH+MANTISSA_WIDTH:0]  operand_b,
    input  logic [2:0]                             operation, // 000: add, 001: sub, 010: mul, 011: div
    output logic [EXPONENT_WIDTH+MANTISSA_WIDTH:0]  result,
    output logic                                    valid_out,
    output logic                                    exception
);

    // Internal signals
    logic sign_a, sign_b, sign_result;
    logic [EXPONENT_WIDTH-1:0] exp_a, exp_b, exp_result;
    logic [MANTISSA_WIDTH-1:0] mantissa_a, mantissa_b, mantissa_result;
    
    // Unpacking stage
    always_comb begin
        sign_a = operand_a[EXPONENT_WIDTH+MANTISSA_WIDTH];
        sign_b = operand_b[EXPONENT_WIDTH+MANTISSA_WIDTH];
        exp_a = operand_a[EXPONENT_WIDTH+MANTISSA_WIDTH-1:MANTISSA_WIDTH];
        exp_b = operand_b[EXPONENT_WIDTH+MANTISSA_WIDTH-1:MANTISSA_WIDTH];
        mantissa_a = operand_a[MANTISSA_WIDTH-1:0];
        mantissa_b = operand_b[MANTISSA_WIDTH-1:0];
    end

    // Clock gating cell
    logic clk_gated;
    logic clock_enable;

    generate
        if (CLOCK_GATING_EN) begin : clock_gate_gen
            logic clk_en_latch;
            
            always_latch begin
                if (!clk)
                    clk_en_latch <= clock_enable;
            end
            
            assign clk_gated = clk & clk_en_latch;
        end else begin : no_clock_gate
            assign clk_gated = clk;
        end
    endgenerate

    // Operand isolation logic
    logic isolate_datapath;
    logic [EXPONENT_WIDTH+MANTISSA_WIDTH:0] operand_a_gated, operand_b_gated;

    generate
        if (OPERAND_ISOLATION_EN) begin : operand_isolation
            assign operand_a_gated = isolate_datapath ? '0 : operand_a;
            assign operand_b_gated = isolate_datapath ? '0 : operand_b;
        end else begin : no_operand_isolation
            assign operand_a_gated = operand_a;
            assign operand_b_gated = operand_b;
        end
    endgenerate

    // Pipeline registers
    logic valid_stage1, valid_stage2;
    logic [EXPONENT_WIDTH+MANTISSA_WIDTH:0] result_stage1, result_stage2;
    logic exception_stage1, exception_stage2;

    // Addition/Subtraction implementation with power optimizations
    function automatic logic [EXPONENT_WIDTH+MANTISSA_WIDTH:0] perform_add_sub(
        input logic is_sub
    );
        // Local variables
        logic [MANTISSA_WIDTH:0] mant_a, mant_b;
        logic [EXPONENT_WIDTH-1:0] exp_diff;
        logic [MANTISSA_WIDTH+1:0] aligned_mant_a, aligned_mant_b;
        logic [MANTISSA_WIDTH+1:0] sum_result;
        logic [4:0] lead_zero_count;
        logic effective_subtract;
        
        // Add hidden bit
        mant_a = {1'b1, mantissa_a};
        mant_b = {1'b1, mantissa_b};

        // Determine effective operation
        effective_subtract = is_sub ^ (sign_a ^ sign_b);

        // Exponent difference for alignment
        if (exp_a >= exp_b) begin
            exp_diff = exp_a - exp_b;
            aligned_mant_a = {mant_a, 1'b0};
            aligned_mant_b = ({mant_b, 1'b0} >> exp_diff);
        end else begin
            exp_diff = exp_b - exp_a;
            aligned_mant_b = {mant_b, 1'b0};
            aligned_mant_a = ({mant_a, 1'b0} >> exp_diff);
        end

        // Addition/Subtraction with carry-save adder for power efficiency
        if (effective_subtract) begin
            sum_result = aligned_mant_a - aligned_mant_b;
        end else begin
            sum_result = aligned_mant_a + aligned_mant_b;
        end

        // Normalization and leading zero detection
        // Using priority encoder for better power efficiency
        casez (sum_result)
            {1'b1, {(MANTISSA_WIDTH+1){1'b?}}}: lead_zero_count = 5'd0;
            {1'b0, 1'b1, {MANTISSA_WIDTH{1'b?}}}: lead_zero_count = 5'd1;
            {2'b00, 1'b1, {(MANTISSA_WIDTH-1){1'b?}}}: lead_zero_count = 5'd2;
            {3'b000, 1'b1, {(MANTISSA_WIDTH-2){1'b?}}}: lead_zero_count = 5'd3;
            {4'b0000, 1'b1, {(MANTISSA_WIDTH-3){1'b?}}}: lead_zero_count = 5'd4;
            default: lead_zero_count = 5'd23;
        endcase

        // Final result assembly with proper bit widths
        return {
            sign_result,                                    // 1 bit
            exp_result - lead_zero_count,                  // EXPONENT_WIDTH bits
            sum_result[MANTISSA_WIDTH+1:2] >> lead_zero_count  // MANTISSA_WIDTH bits
        };
    endfunction

    // Multiplication Logic
    function automatic logic [EXPONENT_WIDTH+MANTISSA_WIDTH:0] perform_mul;
        // Mul implementation here
        return '0; // Placeholder
    endfunction

    // Division Logic
    function automatic logic [EXPONENT_WIDTH+MANTISSA_WIDTH:0] perform_div;
        // Div implementation here
        return '0; // Placeholder
    endfunction

    // Power management FSM
    typedef enum logic [1:0] {
        IDLE,
        ACTIVE,
        SLEEP,
        DEEP_SLEEP
    } power_state_t;

    power_state_t current_power_state, next_power_state;
    logic [7:0] idle_counter;

    // Power state management
    always_ff @(posedge clk_gated or negedge rst_n) begin
        if (!rst_n) begin
            current_power_state <= IDLE;
            idle_counter <= '0;
        end else begin
            current_power_state <= next_power_state;
            if (valid_in)
                idle_counter <= '0;
            else if (idle_counter != 8'hFF)
                idle_counter <= idle_counter + 1;
        end
    end

    // Power state transitions
    always_comb begin
        next_power_state = current_power_state;
        clock_enable = 1'b1;
        isolate_datapath = 1'b0;

        case (current_power_state)
            IDLE: begin
                if (valid_in)
                    next_power_state = ACTIVE;
                else if (idle_counter >= 8'h20)
                    next_power_state = SLEEP;
            end
            
            ACTIVE: begin
                if (!valid_in)
                    next_power_state = IDLE;
            end
            
            SLEEP: begin
                clock_enable = 1'b0;
                isolate_datapath = 1'b1;
                if (valid_in)
                    next_power_state = ACTIVE;
                else if (idle_counter >= 8'h80)
                    next_power_state = DEEP_SLEEP;
            end
            
            DEEP_SLEEP: begin
                clock_enable = 1'b0;
                isolate_datapath = 1'b1;
                if (valid_in)
                    next_power_state = ACTIVE;
            end
        endcase
    end

    // Main operation logic
    always_ff @(posedge clk_gated or negedge rst_n) begin
        if (!rst_n) begin
            valid_stage1 <= 1'b0;
            result_stage1 <= '0;
            exception_stage1 <= 1'b0;
        end else begin
            valid_stage1 <= valid_in;
            exception_stage1 <= 1'b0;
            
            case (operation)
                3'b000: result_stage1 <= perform_add_sub(1'b0);
                3'b001: result_stage1 <= perform_add_sub(1'b1);
                3'b010: result_stage1 <= perform_mul();
                3'b011: result_stage1 <= perform_div();
                default: begin
                    result_stage1 <= '0;
                    exception_stage1 <= 1'b1;
                end
            endcase
        end
    end

    // Output stage
    always_ff @(posedge clk_gated or negedge rst_n) begin
        if (!rst_n) begin
            valid_out <= 1'b0;
            result <= '0;
            exception <= 1'b0;
        end else begin
            valid_out <= valid_stage1;
            result <= result_stage1;
            exception <= exception_stage1;
        end
    end

endmodule
