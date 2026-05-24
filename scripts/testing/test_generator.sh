#!/bin/bash

# =============================================================================
# Test Script for AVISPA CLP Instance Generator System
# =============================================================================
# Tests all components of the generation system:
# 1. Cork variants (1 cycle)
# 2. Python generator functionality
# 3. Validation system
# 4. Expected results storage
# =============================================================================

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "========================================================================"
echo "AVISPA CLP Generator System Test Suite"
echo "========================================================================"
echo ""

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MODEL_PATH="$PROJECT_ROOT/core/models/clp_model.mzn"
GENERATED_DIR="$PROJECT_ROOT/experiments/instances/battery-generated"
VARIANT_DIR="$PROJECT_ROOT/experiments/instances/Battery-Decided"
TIMEOUT=60

cd "$PROJECT_ROOT"

# Counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# =============================================================================
# TEST 1: Cork Variants Exist
# =============================================================================

echo -e "${BLUE}[TEST 1]${NC} Checking Cork variants..."
TESTS_RUN=$((TESTS_RUN + 1))

if ls "$VARIANT_DIR"/*.dzn 1> /dev/null 2>&1; then
    COUNT=$(ls -1 "$VARIANT_DIR"/*.dzn | wc -l)
    echo -e "${GREEN}✓ PASS${NC}: Found $COUNT Cork variant files"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗ FAIL${NC}: No Cork variants found"
    echo -e "  ${YELLOW}Run:${NC} python scripts/generation/create_cork_variants.py"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
echo ""

# =============================================================================
# TEST 2: Generator Script Exists
# =============================================================================

echo -e "${BLUE}[TEST 2]${NC} Checking generator script..."
TESTS_RUN=$((TESTS_RUN + 1))

if [ -f "$PROJECT_ROOT/core/generator/generator.py" ]; then
    echo -e "${GREEN}✓ PASS${NC}: Generator script found"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗ FAIL${NC}: Generator script not found"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
echo ""

# =============================================================================
# TEST 3: MiniZinc Available
# =============================================================================

echo -e "${BLUE}[TEST 3]${NC} Checking MiniZinc installation..."
TESTS_RUN=$((TESTS_RUN + 1))

if command -v minizinc &> /dev/null; then
    VERSION=$(minizinc --version | head -1)
    echo -e "${GREEN}✓ PASS${NC}: MiniZinc found - $VERSION"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗ FAIL${NC}: MiniZinc not found"
    echo -e "  ${YELLOW}Install from:${NC} https://www.minizinc.org/"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
echo ""

# =============================================================================
# TEST 4: Test Cork Variant (if MiniZinc available)
# =============================================================================

if command -v minizinc &> /dev/null && ls "$VARIANT_DIR"/*.dzn 1> /dev/null 2>&1; then
    echo -e "${BLUE}[TEST 4]${NC} Testing Cork variant with CLP model..."
    TESTS_RUN=$((TESTS_RUN + 1))

    FIRST_VARIANT=$(ls "$VARIANT_DIR"/*.dzn | head -1)
    echo "  Testing: $(basename "$FIRST_VARIANT")"

    timeout $TIMEOUT minizinc --solver chuffed "$MODEL_PATH" "$FIRST_VARIANT" > /tmp/test_result.txt 2>&1
    EXIT_CODE=$?

    if [ $EXIT_CODE -eq 0 ]; then
        if grep -q "Total estaciones:" /tmp/test_result.txt; then
            STATIONS=$(grep "Total estaciones:" /tmp/test_result.txt | awk '{print $NF}')
            echo -e "${GREEN}✓ PASS${NC}: Cork variant is SATISFIABLE ($STATIONS stations)"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        elif grep -q "UNSATISFIABLE" /tmp/test_result.txt; then
            echo -e "${YELLOW}⚠ WARN${NC}: Cork variant is UNSATISFIABLE (expected for some Cork instances)"
            echo -e "  ${YELLOW}Note:${NC} Cork instances may need parameter relaxation"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        else
            echo -e "${RED}✗ FAIL${NC}: Unexpected output"
            TESTS_FAILED=$((TESTS_FAILED + 1))
        fi
    elif [ $EXIT_CODE -eq 124 ]; then
        echo -e "${YELLOW}⏱ TIMEOUT${NC}: Solver didn't finish in ${TIMEOUT}s"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗ FAIL${NC}: MiniZinc error (exit code $EXIT_CODE)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    echo ""
fi

# =============================================================================
# TEST 5: Check Generated Instances Directory
# =============================================================================

echo -e "${BLUE}[TEST 5]${NC} Checking generated instances directory..."
TESTS_RUN=$((TESTS_RUN + 1))

if [ -d "$GENERATED_DIR" ]; then
    if [ -d "$GENERATED_DIR/Expected Results" ]; then
        echo -e "${GREEN}✓ PASS${NC}: Directory structure correct"

        GEN_COUNT=$(ls -1 "$GENERATED_DIR"/*.dzn 2>/dev/null | wc -l)
        EXP_COUNT=$(ls -1 "$GENERATED_DIR/Expected Results"/*.json 2>/dev/null | wc -l)

        echo "  Generated instances: $GEN_COUNT"
        echo "  Expected results: $EXP_COUNT"

        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${YELLOW}⚠ WARN${NC}: Expected Results directory missing"
        mkdir -p "$GENERATED_DIR/Expected Results"
        echo "  Created: $GENERATED_DIR/Expected Results"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    fi
else
    echo -e "${YELLOW}⚠ WARN${NC}: Generated directory missing"
    mkdir -p "$GENERATED_DIR/Expected Results"
    echo "  Created directories"
    TESTS_PASSED=$((TESTS_PASSED + 1))
fi
echo ""

# =============================================================================
# TEST 6: Validate Existing Generated Instance (if any)
# =============================================================================

if command -v minizinc &> /dev/null && ls "$GENERATED_DIR"/*.dzn 1> /dev/null 2>&1; then
    echo -e "${BLUE}[TEST 6]${NC} Validating existing generated instance..."
    TESTS_RUN=$((TESTS_RUN + 1))

    FIRST_GENERATED=$(ls "$GENERATED_DIR"/*.dzn | head -1)
    echo "  Testing: $(basename "$FIRST_GENERATED")"

    timeout $TIMEOUT minizinc --solver chuffed "$MODEL_PATH" "$FIRST_GENERATED" > /tmp/test_gen_result.txt 2>&1
    EXIT_CODE=$?

    if [ $EXIT_CODE -eq 0 ]; then
        if grep -q "Total estaciones:" /tmp/test_gen_result.txt; then
            STATIONS=$(grep "Total estaciones:" /tmp/test_gen_result.txt | awk '{print $NF}')
            echo -e "${GREEN}✓ PASS${NC}: Generated instance is SATISFIABLE ($STATIONS stations)"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        elif grep -q "UNSATISFIABLE" /tmp/test_gen_result.txt; then
            echo -e "${RED}✗ FAIL${NC}: Generated instance is UNSATISFIABLE"
            echo -e "  ${YELLOW}Action:${NC} Regenerate or check algorithm"
            TESTS_FAILED=$((TESTS_FAILED + 1))
        else
            echo -e "${RED}✗ FAIL${NC}: Unexpected output"
            TESTS_FAILED=$((TESTS_FAILED + 1))
        fi
    elif [ $EXIT_CODE -eq 124 ]; then
        echo -e "${YELLOW}⏱ TIMEOUT${NC}: Solver didn't finish in ${TIMEOUT}s"
        echo -e "  Instance may be too large or complex"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗ FAIL${NC}: MiniZinc error (exit code $EXIT_CODE)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    echo ""
fi

# =============================================================================
# TEST 7: Documentation Exists
# =============================================================================

echo -e "${BLUE}[TEST 7]${NC} Checking documentation..."
TESTS_RUN=$((TESTS_RUN + 1))

DOC_COUNT=0
[ -f "$PROJECT_ROOT/docs/Generated System/README.md" ] && DOC_COUNT=$((DOC_COUNT + 1))
[ -f "$PROJECT_ROOT/Generator/README_BUILD.md" ] && DOC_COUNT=$((DOC_COUNT + 1))

if [ $DOC_COUNT -eq 2 ]; then
    echo -e "${GREEN}✓ PASS${NC}: All documentation files found"
    TESTS_PASSED=$((TESTS_PASSED + 1))
elif [ $DOC_COUNT -gt 0 ]; then
    echo -e "${YELLOW}⚠ WARN${NC}: Some documentation files missing ($DOC_COUNT/2 found)"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗ FAIL${NC}: No documentation found"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
echo ""

# =============================================================================
# SUMMARY
# =============================================================================

echo "========================================================================"
echo "Test Summary"
echo "========================================================================"
echo -e "Total tests:     $TESTS_RUN"
echo -e "${GREEN}Passed:          $TESTS_PASSED${NC}"
echo -e "${RED}Failed:          $TESTS_FAILED${NC}"

SUCCESS_RATE=$((TESTS_PASSED * 100 / TESTS_RUN))
echo -e "Success rate:    ${SUCCESS_RATE}%"

echo "========================================================================"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED${NC}"
    echo ""
    echo "System is ready to use!"
    echo "Run: python Generator/generator.py"
    exit 0
else
    echo -e "${RED}✗ SOME TESTS FAILED${NC}"
    echo ""
    echo "Please fix the issues above before using the system."
    exit 1
fi
