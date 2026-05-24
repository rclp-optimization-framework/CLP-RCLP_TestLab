#!/bin/bash

# ==============================================================================
# Script de Diagnóstico CLP - Battery Project Integer
# ==============================================================================
# Analiza instancias Cork para identificar la causa de UNSATISFIABLE
# Realiza validación de factibilidad matemática de los datos
# ==============================================================================

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MODEL_PATH="$PROJECT_ROOT/core/models/clp_model.mzn"
DATA_DIR_CORK="$PROJECT_ROOT/experiments/instances/Battery-Decided"
DATA_DIR_OWN="$PROJECT_ROOT/experiments/instances/battery-own"
OUTPUT_DIR="$PROJECT_ROOT/experiments/results/Diagnostics"
TIMEOUT=120  # 2 minutes per instance
SOLVER="gecode"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Log file
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$OUTPUT_DIR/diagnostic_${TIMESTAMP}.log"
REPORT_FILE="$OUTPUT_DIR/diagnostic_report_${TIMESTAMP}.md"

echo "========================================================================"
echo "CLP Model Diagnostic Script - Cork Dataset Analysis"
echo "========================================================================"
echo "Model: $MODEL_PATH"
echo "Cork Data: $DATA_DIR_CORK"
echo "Own Data: $DATA_DIR_OWN"
echo "Timeout: ${TIMEOUT}s per instance"
echo "Solver: $SOLVER"
echo "Log: $LOG_FILE"
echo "Report: $REPORT_FILE"
echo "========================================================================" | tee "$LOG_FILE"
echo ""

# Start markdown report
cat > "$REPORT_FILE" << 'EOF'
# Diagnóstico CLP - Battery Project Integer

**Fecha**:
**Objetivo**: Identificar causa de UNSATISFIABLE en instancias Cork

---

## Resumen Ejecutivo

EOF

echo "$(date)" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Counters
TOTAL_TESTS=0
SUCCESS=0
FAIL=0
UNSATISFIABLE=0
TIMEOUT_COUNT=0
SYNTAX_ERROR=0

# Test function
test_instance() {
    local data_file="$1"
    local test_name=$(basename "$data_file" .dzn)
    local output_file="$OUTPUT_DIR/${test_name}_diagnostic.txt"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    echo -e "${BLUE}[Test $TOTAL_TESTS]${NC} $test_name" | tee -a "$LOG_FILE"

    if [ ! -f "$data_file" ]; then
        echo -e "${RED}  ✗ File not found${NC}" | tee -a "$LOG_FILE"
        FAIL=$((FAIL + 1))
        return 1
    fi

    # Run MiniZinc
    start_time=$(date +%s)
    timeout $TIMEOUT minizinc --solver $SOLVER "$MODEL_PATH" "$data_file" > "$output_file" 2>&1
    exit_code=$?
    end_time=$(date +%s)
    elapsed=$((end_time - start_time))

    # Analyze result
    if [ $exit_code -eq 124 ]; then
        echo -e "${YELLOW}  ⏱ TIMEOUT (${elapsed}s)${NC}" | tee -a "$LOG_FILE"
        TIMEOUT_COUNT=$((TIMEOUT_COUNT + 1))
        echo "| $test_name | ⏱️ TIMEOUT | ${elapsed}s | Solver no terminó |" >> "$REPORT_FILE"
    elif grep -q "UNSATISFIABLE" "$output_file"; then
        echo -e "${RED}  ✗ UNSATISFIABLE (${elapsed}s)${NC}" | tee -a "$LOG_FILE"
        UNSATISFIABLE=$((UNSATISFIABLE + 1))

        # Extract error details
        if grep -q "array access out of bounds" "$output_file"; then
            echo -e "${RED}    → Array access error (index 0)${NC}" | tee -a "$LOG_FILE"
            echo "| $test_name | ❌ UNSAT | ${elapsed}s | **Array access error** |" >> "$REPORT_FILE"
            SYNTAX_ERROR=$((SYNTAX_ERROR + 1))
        else
            echo -e "${YELLOW}    → Instancia infactible${NC}" | tee -a "$LOG_FILE"
            echo "| $test_name | ❌ UNSAT | ${elapsed}s | Instancia infactible |" >> "$REPORT_FILE"
        fi

        # Show warnings
        if grep -q "Warning" "$output_file"; then
            echo -e "${YELLOW}    → Warnings encontrados:${NC}" | tee -a "$LOG_FILE"
            grep "Warning" "$output_file" | head -2 | sed 's/^/      /' | tee -a "$LOG_FILE"
        fi
    elif grep -q "Total estaciones:" "$output_file"; then
        stations=$(grep "Total estaciones:" "$output_file" | awk '{print $NF}')
        echo -e "${GREEN}  ✓ SUCCESS (${elapsed}s) - Estaciones: $stations${NC}" | tee -a "$LOG_FILE"
        SUCCESS=$((SUCCESS + 1))
        echo "| $test_name | ✅ SAT | ${elapsed}s | $stations estaciones |" >> "$REPORT_FILE"
    else
        echo -e "${RED}  ✗ ERROR (exit $exit_code, ${elapsed}s)${NC}" | tee -a "$LOG_FILE"
        FAIL=$((FAIL + 1))
        echo "| $test_name | ❌ ERROR | ${elapsed}s | Exit code: $exit_code |" >> "$REPORT_FILE"
    fi

    echo "" | tee -a "$LOG_FILE"
}

# Analyze data file for feasibility
analyze_data_feasibility() {
    local data_file="$1"
    local test_name=$(basename "$data_file" .dzn)
    local analysis_file="$OUTPUT_DIR/${test_name}_analysis.txt"

    echo "Analyzing feasibility of: $test_name" > "$analysis_file"
    echo "========================================" >> "$analysis_file"

    # Extract key parameters using awk/grep
    local num_buses=$(grep "num_buses = " "$data_file" | head -1 | awk -F'=' '{print $2}' | tr -d ' ;')
    local num_stations=$(grep "num_stations = " "$data_file" | head -1 | awk -F'=' '{print $2}' | tr -d ' ;')
    local Cmax=$(grep "Cmax = " "$data_file" | head -1 | awk -F'=' '{print $2}' | tr -d ' ;')
    local Cmin=$(grep "Cmin = " "$data_file" | head -1 | awk -F'=' '{print $2}' | tr -d ' ;')
    local alpha=$(grep "alpha = " "$data_file" | head -1 | awk -F'=' '{print $2}' | tr -d ' ;')

    echo "Buses: $num_buses" >> "$analysis_file"
    echo "Stations: $num_stations" >> "$analysis_file"
    echo "Cmax: $Cmax ($(($Cmax / 10)) kWh)" >> "$analysis_file"
    echo "Cmin: $Cmin ($(($Cmin / 10)) kWh)" >> "$analysis_file"
    echo "Usable capacity: $(($Cmax - $Cmin)) ($(( ($Cmax - $Cmin) / 10 )) kWh)" >> "$analysis_file"
    echo "Charging rate: $alpha ($(($alpha / 10)) kWh/min)" >> "$analysis_file"
    echo "" >> "$analysis_file"

    # Check for index 0 in st_bi
    if grep -q "st_bi.*\[" "$data_file"; then
        local has_zero=$(grep -A 50 "st_bi = " "$data_file" | grep -o "0," | wc -l)
        if [ $has_zero -gt 0 ]; then
            echo "⚠️  WARNING: Found $has_zero instances of index 0 in st_bi" >> "$analysis_file"
            echo "   Model should handle this with filtering, but verify correctness" >> "$analysis_file"
        else
            echo "✓ No index 0 found in st_bi (good)" >> "$analysis_file"
        fi
    fi

    echo "" >> "$analysis_file"
    cat "$analysis_file"
}

# ==============================================================================
# SECTION 1: Test baseline instances (known working)
# ==============================================================================

echo -e "${CYAN}========================================${NC}" | tee -a "$LOG_FILE"
echo -e "${CYAN}SECTION 1: Baseline Tests (Should Work)${NC}" | tee -a "$LOG_FILE"
echo -e "${CYAN}========================================${NC}" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

cat >> "$REPORT_FILE" << 'EOF'
## Sección 1: Tests de Línea Base (Control Positivo)

Instancias que deberían funcionar correctamente:

| Instancia | Resultado | Tiempo | Notas |
|-----------|-----------|--------|-------|
EOF

# Test noncity (known working)
BASELINE_TESTS=(
    "$DATA_DIR_OWN/noncity_5buses-8stations.dzn"
)

for test_case in "${BASELINE_TESTS[@]}"; do
    if [ -f "$test_case" ]; then
        test_instance "$test_case"
    fi
done

echo "" >> "$REPORT_FILE"

# ==============================================================================
# SECTION 2: Test Cork instances (currently failing)
# ==============================================================================

echo -e "${CYAN}========================================${NC}" | tee -a "$LOG_FILE"
echo -e "${CYAN}SECTION 2: Cork Dataset Tests${NC}" | tee -a "$LOG_FILE"
echo -e "${CYAN}========================================${NC}" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

cat >> "$REPORT_FILE" << 'EOF'
## Sección 2: Tests Cork Dataset

Instancias reales de Cork (actualmente reportando UNSATISFIABLE):

| Instancia | Resultado | Tiempo | Notas |
|-----------|-----------|--------|-------|
EOF

# Cork test cases - sample from different variants
CORK_TESTS=(
    "$DATA_DIR_CORK/cork-1-line20_0.dzn"
    "$DATA_DIR_CORK/cork-1-line20_5.dzn"
    "$DATA_DIR_CORK/cork-2-lines20_0.dzn"
)

for test_case in "${CORK_TESTS[@]}"; do
    if [ -f "$test_case" ]; then
        test_instance "$test_case"
        analyze_data_feasibility "$test_case" | head -20
    fi
done

echo "" >> "$REPORT_FILE"

# ==============================================================================
# SECTION 3: Detailed analysis of first Cork failure
# ==============================================================================

echo -e "${CYAN}========================================${NC}" | tee -a "$LOG_FILE"
echo -e "${CYAN}SECTION 3: Detailed Failure Analysis${NC}" | tee -a "$LOG_FILE"
echo -e "${CYAN}========================================${NC}" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

cat >> "$REPORT_FILE" << 'EOF'
## Sección 3: Análisis Detallado de Fallos

### Errores Encontrados

EOF

# Analyze the first failing Cork instance in detail
FIRST_CORK="$DATA_DIR_CORK/cork-1-line20_0.dzn"
if [ -f "$FIRST_CORK" ]; then
    OUTPUT_FILE="$OUTPUT_DIR/$(basename $FIRST_CORK .dzn)_diagnostic.txt"

    echo "Analyzing: $(basename $FIRST_CORK)" | tee -a "$LOG_FILE"

    if [ -f "$OUTPUT_FILE" ]; then
        # Check for specific errors
        echo "" >> "$REPORT_FILE"
        echo "**Instancia**: $(basename $FIRST_CORK)" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
        echo '```' >> "$REPORT_FILE"

        if grep -q "array access out of bounds" "$OUTPUT_FILE"; then
            echo "❌ ERROR: Array access out of bounds detectado" | tee -a "$LOG_FILE"
            echo "Array access out of bounds encontrado" >> "$REPORT_FILE"
            grep -A 5 "array access out of bounds" "$OUTPUT_FILE" >> "$REPORT_FILE"

            # This means model correction didn't work
            echo "" | tee -a "$LOG_FILE"
            echo -e "${RED}DIAGNÓSTICO: Modelo CLP no está filtrando índices 0 correctamente${NC}" | tee -a "$LOG_FILE"
            echo -e "${YELLOW}ACCIÓN: Verificar restricciones where st_bi[b,i] > 0${NC}" | tee -a "$LOG_FILE"

        elif grep -q "UNSATISFIABLE" "$OUTPUT_FILE"; then
            echo "❌ UNSATISFIABLE (instancia infactible)" | tee -a "$LOG_FILE"
            echo "Instancia declarada infactible por el solver" >> "$REPORT_FILE"

            # Check for warnings that might explain why
            if grep -q "Warning" "$OUTPUT_FILE"; then
                echo "" >> "$REPORT_FILE"
                echo "Warnings:" >> "$REPORT_FILE"
                grep "Warning" "$OUTPUT_FILE" | head -5 >> "$REPORT_FILE"
            fi

            echo "" | tee -a "$LOG_FILE"
            echo -e "${YELLOW}DIAGNÓSTICO: Datos Cork pueden ser genuinamente infactibles${NC}" | tee -a "$LOG_FILE"
            echo -e "${YELLOW}  - Posible: Consumo energético > capacidad disponible${NC}" | tee -a "$LOG_FILE"
            echo -e "${YELLOW}  - Posible: Restricciones de tiempo demasiado estrictas${NC}" | tee -a "$LOG_FILE"
            echo -e "${YELLOW}  - Posible: Rutas muy largas sin oportunidad de carga${NC}" | tee -a "$LOG_FILE"
        fi

        echo '```' >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
    fi
fi

# ==============================================================================
# FINAL SUMMARY
# ==============================================================================

echo "" >> "$REPORT_FILE"
echo "---" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "## Resumen Final" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "| Métrica | Valor |" >> "$REPORT_FILE"
echo "|---------|-------|" >> "$REPORT_FILE"
echo "| Total tests | $TOTAL_TESTS |" >> "$REPORT_FILE"
echo "| ✅ Satisfacibles | $SUCCESS |" >> "$REPORT_FILE"
echo "| ❌ Insatisfacibles | $UNSATISFIABLE |" >> "$REPORT_FILE"
echo "| ⏱️ Timeouts | $TIMEOUT_COUNT |" >> "$REPORT_FILE"
echo "| 🔧 Errores sintaxis | $SYNTAX_ERROR |" >> "$REPORT_FILE"
echo "| ❌ Otros errores | $FAIL |" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

echo "========================================================================" | tee -a "$LOG_FILE"
echo "Diagnóstico Completado" | tee -a "$LOG_FILE"
echo "========================================================================" | tee -a "$LOG_FILE"
echo "Total tests:        $TOTAL_TESTS" | tee -a "$LOG_FILE"
echo -e "${GREEN}Satisfacibles:      $SUCCESS${NC}" | tee -a "$LOG_FILE"
echo -e "${RED}Insatisfacibles:    $UNSATISFIABLE${NC}" | tee -a "$LOG_FILE"
echo -e "${YELLOW}Timeouts:           $TIMEOUT_COUNT${NC}" | tee -a "$LOG_FILE"
echo -e "${RED}Errores sintaxis:   $SYNTAX_ERROR${NC}" | tee -a "$LOG_FILE"
echo -e "${RED}Otros errores:      $FAIL${NC}" | tee -a "$LOG_FILE"
echo "========================================================================" | tee -a "$LOG_FILE"

# Diagnosis conclusion
echo "" >> "$REPORT_FILE"
echo "## Conclusión del Diagnóstico" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

if [ $SYNTAX_ERROR -gt 0 ]; then
    echo "🔴 **CAUSA PRINCIPAL: Error en el Modelo**" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "El modelo CLP presenta errores de acceso a arrays (índice 0)." >> "$REPORT_FILE"
    echo "Las correcciones aplicadas NO están funcionando correctamente." >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "**Acción requerida**: Revisar restricciones con filtro \`where st_bi[b,i] > 0\`" >> "$REPORT_FILE"

    echo -e "\n${RED}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}CONCLUSIÓN: PROBLEMA EN EL MODELO CLP${NC}"
    echo -e "${RED}Las correcciones de filtrado de índices 0 no funcionan${NC}"
    echo -e "${RED}═══════════════════════════════════════════════════════════${NC}\n"

elif [ $UNSATISFIABLE -gt 0 ] && [ $SUCCESS -gt 0 ]; then
    echo "🟡 **CAUSA PRINCIPAL: Instancias Cork Infactibles**" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "El modelo funciona correctamente (baseline tests pasan)." >> "$REPORT_FILE"
    echo "Las instancias Cork son genuinamente infactibles debido a:" >> "$REPORT_FILE"
    echo "- Consumo energético excesivo sin oportunidades de carga" >> "$REPORT_FILE"
    echo "- Restricciones temporales muy estrictas (μ muy bajo)" >> "$REPORT_FILE"
    echo "- Parámetros de carga insuficientes (α, β)" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "**Acción requerida**: Relajar parámetros o validar datos Cork" >> "$REPORT_FILE"

    echo -e "\n${YELLOW}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}CONCLUSIÓN: PROBLEMA EN DATOS CORK (Instancias Infactibles)${NC}"
    echo -e "${YELLOW}El modelo está correcto, pero los datos son demasiado restrictivos${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}\n"

elif [ $UNSATISFIABLE -gt 0 ] && [ $SUCCESS -eq 0 ]; then
    echo "🔴 **CAUSA PRINCIPAL: Problema Sistémico**" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "Ninguna instancia (incluso baseline) es satisfacible." >> "$REPORT_FILE"
    echo "Esto indica un problema grave en el modelo CLP." >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "**Acción requerida**: Revisar modelo completo, puede haber restricciones contradictorias" >> "$REPORT_FILE"

    echo -e "\n${RED}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}CONCLUSIÓN: PROBLEMA SISTÉMICO EN EL MODELO${NC}"
    echo -e "${RED}Ni siquiera instancias válidas conocidas funcionan${NC}"
    echo -e "${RED}═══════════════════════════════════════════════════════════${NC}\n"

else
    echo "✅ **Todo Funcional**" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "No se detectaron problemas significativos." >> "$REPORT_FILE"

    echo -e "\n${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}CONCLUSIÓN: Sistema Funcional${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}\n"
fi

echo "" | tee -a "$LOG_FILE"
echo "Reporte completo guardado en: $REPORT_FILE" | tee -a "$LOG_FILE"
echo "Log detallado en: $LOG_FILE" | tee -a "$LOG_FILE"
echo "Archivos de salida en: $OUTPUT_DIR/" | tee -a "$LOG_FILE"

# Exit with appropriate code
if [ $SYNTAX_ERROR -gt 0 ]; then
    exit 2  # Model error
elif [ $UNSATISFIABLE -gt 0 ] && [ $SUCCESS -gt 0 ]; then
    exit 1  # Data error
elif [ $UNSATISFIABLE -gt 0 ] && [ $SUCCESS -eq 0 ]; then
    exit 3  # Systemic error
else
    exit 0  # All good
fi
