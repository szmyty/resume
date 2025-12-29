#!/usr/bin/env bash
# Build audit wrapper script
# This script wraps the resume build process to capture full diagnostics
# when BUILD_AUDIT=true environment variable is set.

set -euo pipefail

# Determine if audit mode is enabled
BUILD_AUDIT="${BUILD_AUDIT:-false}"

# Generate timestamp for audit files
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
AUDIT_DIR="audit"
AUDIT_FILE="${AUDIT_DIR}/build_${TIMESTAMP}.txt"
REPORT_FILE="${AUDIT_DIR}/build_${TIMESTAMP}_report.txt"

# Ensure audit directory exists
mkdir -p "${AUDIT_DIR}"

# Function to collect LaTeX logs
collect_latex_logs() {
    local audit_file="$1"
    
    echo "" >> "${audit_file}"
    echo "========================================" >> "${audit_file}"
    echo "LATEX LOG FILES" >> "${audit_file}"
    echo "========================================" >> "${audit_file}"
    echo "" >> "${audit_file}"
    
    # Find and append all LaTeX log files
    # Use process substitution to avoid subshell issues
    while IFS= read -r log_file; do
        if [ -f "${log_file}" ]; then
            echo "===== ${log_file} =====" >> "${audit_file}"
            cat "${log_file}" >> "${audit_file}"
            echo "" >> "${audit_file}"
        fi
    done < <(find resumes/*/build -name "*.log" 2>/dev/null)
}

# Function to analyze build output and generate report
generate_diagnostic_report() {
    local audit_file="$1"
    local report_file="$2"
    
    cat > "${report_file}" <<EOF
========================================
BUILD AUDIT DIAGNOSTIC REPORT
========================================
Generated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
Timestamp: ${TIMESTAMP}
Build Command: python engine/build.py
Audit File: ${audit_file}

EOF
    
    # Detect variant being built
    echo "VARIANTS ATTEMPTED:" >> "${report_file}"
    if grep -q "Building variant:" "${audit_file}" 2>/dev/null; then
        grep "Building variant:" "${audit_file}" | sed 's/.*Building variant: /- /' >> "${report_file}"
    else
        echo "- Unable to detect variants" >> "${report_file}"
    fi
    echo "" >> "${report_file}"
    
    # Detect build phases
    echo "BUILD PHASE PROGRESSION:" >> "${report_file}"
    if grep -q "Loading configuration" "${audit_file}" 2>/dev/null; then
        echo "✓ Configuration loading" >> "${report_file}"
    fi
    if grep -q "Validating configuration" "${audit_file}" 2>/dev/null; then
        echo "✓ Configuration validation" >> "${report_file}"
    fi
    if grep -q "Rendering Jinja templates" "${audit_file}" 2>/dev/null; then
        echo "✓ Template rendering" >> "${report_file}"
    fi
    if grep -q "Compiling LaTeX to PDF" "${audit_file}" 2>/dev/null; then
        echo "✓ LaTeX compilation started" >> "${report_file}"
    fi
    if grep -q "built successfully" "${audit_file}" 2>/dev/null; then
        echo "✓ Build completed successfully" >> "${report_file}"
    fi
    echo "" >> "${report_file}"
    
    # Analyze failure
    echo "FAILURE ANALYSIS:" >> "${report_file}"
    
    if grep -q "ERROR" "${audit_file}" 2>/dev/null; then
        echo "Error Type: Build Error Detected" >> "${report_file}"
        echo "" >> "${report_file}"
        echo "Error Messages:" >> "${report_file}"
        grep -A 5 "ERROR" "${audit_file}" | head -20 >> "${report_file}"
        echo "" >> "${report_file}"
    fi
    
    # Check for specific error patterns
    if grep -q "LaTeX compilation failed" "${audit_file}" 2>/dev/null; then
        echo "Failure Category: LaTeX Compilation Error" >> "${report_file}"
        echo "Location: During PDF generation with Tectonic" >> "${report_file}"
        echo "" >> "${report_file}"
    elif grep -q "Template.*not found" "${audit_file}" 2>/dev/null; then
        echo "Failure Category: Missing Template File" >> "${report_file}"
        echo "" >> "${report_file}"
    elif grep -q "YAML.*error" "${audit_file}" 2>/dev/null; then
        echo "Failure Category: Configuration Parse Error" >> "${report_file}"
        echo "" >> "${report_file}"
    elif grep -q "FileNotFoundError" "${audit_file}" 2>/dev/null; then
        echo "Failure Category: Missing File or Command" >> "${report_file}"
        echo "" >> "${report_file}"
    fi
    
    # Check for LaTeX-specific errors in logs
    if grep -q "! LaTeX Error:" "${audit_file}" 2>/dev/null; then
        echo "LaTeX Error Details:" >> "${report_file}"
        grep -A 3 "! LaTeX Error:" "${audit_file}" | head -20 >> "${report_file}"
        echo "" >> "${report_file}"
    fi
    
    if grep -q "! Undefined control sequence" "${audit_file}" 2>/dev/null; then
        echo "LaTeX Issue: Undefined control sequence detected" >> "${report_file}"
        echo "This typically indicates a missing LaTeX package or misspelled command." >> "${report_file}"
        echo "" >> "${report_file}"
    fi
    
    if grep -q "! File.*not found" "${audit_file}" 2>/dev/null; then
        echo "LaTeX Issue: Missing file reference" >> "${report_file}"
        grep "! File.*not found" "${audit_file}" >> "${report_file}"
        echo "" >> "${report_file}"
    fi
    
    # Provide recommendations
    echo "RECOMMENDATIONS:" >> "${report_file}"
    if grep -q "LaTeX compilation failed" "${audit_file}" 2>/dev/null; then
        echo "1. Review the LaTeX log sections below for detailed error messages" >> "${report_file}"
        echo "2. Check for syntax errors in LaTeX templates" >> "${report_file}"
        echo "3. Verify all required LaTeX packages are available" >> "${report_file}"
        echo "4. Look for encoding issues or special characters" >> "${report_file}"
    elif grep -q "FileNotFoundError" "${audit_file}" 2>/dev/null; then
        echo "1. Verify all required files and commands are present" >> "${report_file}"
        echo "2. Check file paths and permissions" >> "${report_file}"
    else
        echo "1. Review the full audit log for detailed error information" >> "${report_file}"
        echo "2. Check that all dependencies are installed correctly" >> "${report_file}"
    fi
    echo "" >> "${report_file}"
    
    # Check for LaTeX-specific errors in logs
    echo "LOG SECTIONS TO REVIEW:" >> "${report_file}"
    
    # Check if any log files were collected
    local has_log_files=false
    if grep -q "===== .*\.log =====" "${audit_file}" 2>/dev/null; then
        has_log_files=true
    fi
    
    if [ "${has_log_files}" = "true" ]; then
        echo "LaTeX logs have been appended to the audit file." >> "${report_file}"
        echo "Look for lines starting with '!' which indicate LaTeX errors." >> "${report_file}"
    else
        echo "No LaTeX log files were found." >> "${report_file}"
        echo "This may indicate the build failed before LaTeX compilation." >> "${report_file}"
    fi
    echo "" >> "${report_file}"
    
    echo "Full build output is available in: ${audit_file}" >> "${report_file}"
}

# Main execution
if [ "${BUILD_AUDIT}" = "true" ]; then
    echo "========================================" | tee "${AUDIT_FILE}"
    echo "BUILD AUDIT MODE ENABLED" | tee -a "${AUDIT_FILE}"
    echo "========================================" | tee -a "${AUDIT_FILE}"
    echo "Timestamp: ${TIMESTAMP}" | tee -a "${AUDIT_FILE}"
    echo "Audit file: ${AUDIT_FILE}" | tee -a "${AUDIT_FILE}"
    echo "Report file: ${REPORT_FILE}" | tee -a "${AUDIT_FILE}"
    echo "========================================" | tee -a "${AUDIT_FILE}"
    echo "" | tee -a "${AUDIT_FILE}"
    
    # Run the build and capture all output
    echo "Running build with full diagnostics..." | tee -a "${AUDIT_FILE}"
    echo "" | tee -a "${AUDIT_FILE}"
    
    # Execute build and capture output, allow it to fail
    set +e
    python engine/build.py 2>&1 | tee -a "${AUDIT_FILE}"
    BUILD_EXIT_CODE=$?
    set -e
    
    echo "" | tee -a "${AUDIT_FILE}"
    echo "========================================" | tee -a "${AUDIT_FILE}"
    echo "BUILD COMPLETED WITH EXIT CODE: ${BUILD_EXIT_CODE}" | tee -a "${AUDIT_FILE}"
    echo "========================================" | tee -a "${AUDIT_FILE}"
    
    # Collect LaTeX logs
    echo "" | tee -a "${AUDIT_FILE}"
    echo "Collecting LaTeX log files..." | tee -a "${AUDIT_FILE}"
    collect_latex_logs "${AUDIT_FILE}"
    
    # Generate diagnostic report
    echo "" | tee -a "${AUDIT_FILE}"
    echo "Generating diagnostic report..." | tee -a "${AUDIT_FILE}"
    generate_diagnostic_report "${AUDIT_FILE}" "${REPORT_FILE}"
    
    echo "" | tee -a "${AUDIT_FILE}"
    echo "========================================" | tee -a "${AUDIT_FILE}"
    echo "AUDIT COMPLETE" | tee -a "${AUDIT_FILE}"
    echo "========================================" | tee -a "${AUDIT_FILE}"
    echo "Audit file: ${AUDIT_FILE}" | tee -a "${AUDIT_FILE}"
    echo "Report file: ${REPORT_FILE}" | tee -a "${AUDIT_FILE}"
    echo "" | tee -a "${AUDIT_FILE}"
    
    # Display the report
    echo ""
    echo "========================================" 
    echo "DIAGNOSTIC REPORT"
    echo "========================================" 
    cat "${REPORT_FILE}"
    echo ""
    echo "Full audit log saved to: ${AUDIT_FILE}"
    echo "Diagnostic report saved to: ${REPORT_FILE}"
    
    # Exit with the same code as the build
    exit ${BUILD_EXIT_CODE}
else
    # Normal build mode - just run the build
    python engine/build.py
fi
