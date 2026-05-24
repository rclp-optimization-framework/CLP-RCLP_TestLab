#!/bin/bash

# ==============================================================================
# CLP Model Test Script - Preliminary Battery Tests
# ==============================================================================
# Tests the CLP model with Cork dataset instances (Battery Project Integer)
# Maximum execution time: 5 minutes per instance
# ==============================================================================

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MODEL_PATH="$PROJECT_ROOT/core/models/clp_model.mzn"
DATA_DIR="$PROJECT_ROOT/experiments/instances/battery-own"
OUTPUT_DIR="$PROJECT_ROOT/experiments/results/Preliminary_Tests"
TIMEOUT=300  # 5 minutes in seconds
SOLVER="gecode"  # or "chuffed", "coin-bc"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Log file
LOG_FILE="$OUTPUT_DIR/test_results_$(date +%Y%m%d_%H%M%S).log"

echo "========================================================================"
echo "CLP Model Preliminary Testing - Cork Dataset"
echo "========================================================================"
echo "Model: $MODEL_PATH"
echo "Data: $DATA_DIR"
echo "Timeout: ${TIMEOUT}s (5 minutes)"
echo "Solver: $SOLVER"
echo "Log: $LOG_FILE"
echo "========================================================================" | tee "$LOG_FILE"
echo ""

# Test instances (first 2 from each variant as requested)
TEST_CASES=(
    "noncity_5buses-8stations.dzn"
    "noncity_10buses-15stations.dzn"
)

# Counters
TOTAL=0
SUCCESS=0
FAIL=0
TIMEOUT_COUNT=0

# Run tests
for test_case in "${TEST_CASES[@]}"; do
    TOTAL=$((TOTAL + 1))
    data_file="$DATA_DIR/$test_case"
    output_file="$OUTPUT_DIR/${test_case%.dzn}_output.txt"

    echo -e "${BLUE}[Test $TOTAL/${#TEST_CASES[@]}]${NC} Running: $test_case" | tee -a "$LOG_FILE"

    if [ ! -f "$data_file" ]; then
        echo -e "${RED}  ✗ ERROR: Data file not found${NC}" | tee -a "$LOG_FILE"
        FAIL=$((FAIL + 1))
        continue
    fi

    # Run MiniZinc with timeout
    start_time=$(date +%s)
    timeout $TIMEOUT minizinc --solver $SOLVER "$MODEL_PATH" "$data_file" > "$output_file" 2>&1
    exit_code=$?
    end_time=$(date +%s)
    elapsed=$((end_time - start_time))

    # Check result
    if [ $exit_code -eq 124 ]; then
        echo -e "${YELLOW}  ⏱ TIMEOUT after ${elapsed}s${NC}" | tee -a "$LOG_FILE"
        TIMEOUT_COUNT=$((TIMEOUT_COUNT + 1))
        echo "TIMEOUT" >> "$output_file"
    elif [ $exit_code -eq 0 ]; then
        # Check if solution was found
        if grep -q "Total estaciones:" "$output_file"; then
            stations=$(grep "Total estaciones:" "$output_file" | awk '{print $NF}')
            echo -e "${GREEN}  ✓ SUCCESS (${elapsed}s) - Stations: $stations${NC}" | tee -a "$LOG_FILE"
            SUCCESS=$((SUCCESS + 1))
        else
            echo -e "${RED}  ✗ UNSATISFIABLE (${elapsed}s)${NC}" | tee -a "$LOG_FILE"
            FAIL=$((FAIL + 1))
        fi
    else
        echo -e "${RED}  ✗ ERROR (exit code: $exit_code, ${elapsed}s)${NC}" | tee -a "$LOG_FILE"
        FAIL=$((FAIL + 1))
    fi

    echo "" | tee -a "$LOG_FILE"
done

# Summary
echo "========================================================================" | tee -a "$LOG_FILE"
echo "Test Summary" | tee -a "$LOG_FILE"
echo "========================================================================" | tee -a "$LOG_FILE"
echo "Total tests:    $TOTAL" | tee -a "$LOG_FILE"
echo -e "${GREEN}Successful:     $SUCCESS${NC}" | tee -a "$LOG_FILE"
echo -e "${RED}Failed:         $FAIL${NC}" | tee -a "$LOG_FILE"
echo -e "${YELLOW}Timeouts:       $TIMEOUT_COUNT${NC}" | tee -a "$LOG_FILE"
echo "========================================================================" | tee -a "$LOG_FILE"

# Exit with appropriate code
if [ $SUCCESS -eq $TOTAL ]; then
    exit 0
else
    exit 1
fi
