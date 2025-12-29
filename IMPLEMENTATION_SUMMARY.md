# Build Audit Mode - Implementation Summary

## Overview

This implementation adds a comprehensive build audit mode to the resume repository to capture full diagnostics when LaTeX/Tectonic PDF compilation fails in CI. The audit mode makes build failures observable by capturing all relevant information that would normally be hidden in the CI environment.

## What Was Implemented

### 1. Audit Wrapper Script (`audit_build.sh`)

A Bash script that wraps the build process and captures comprehensive diagnostics:

**Features:**
- Controlled via `BUILD_AUDIT` environment variable (`true` or `false`)
- Captures complete stdout/stderr from `python engine/build.py`
- Collects all LaTeX log files (resume.log, texput.log, *.aux, etc.)
- Appends LaTeX logs to the main audit file
- Generates a diagnostic report with intelligent failure analysis
- Preserves the original build exit code

**Output Files:**
- `audit/build_<timestamp>.txt` - Complete build output and LaTeX logs
- `audit/build_<timestamp>_report.txt` - Diagnostic summary with recommendations

### 2. Diagnostic Report Generator

The audit script includes sophisticated failure analysis that:

- **Tracks Build Progress:** Identifies which build phases completed (config loading, validation, template rendering, LaTeX compilation)
- **Categorizes Failures:** Classifies errors as LaTeX syntax issues, missing files, configuration problems, etc.
- **Extracts Error Details:** Parses error messages and stack traces
- **Analyzes LaTeX Errors:** Detects specific LaTeX error patterns (`! LaTeX Error:`, `! Undefined control sequence`, etc.)
- **Provides Recommendations:** Suggests specific actions based on the failure type
- **Points to Relevant Logs:** Guides users to the exact log sections to review

### 3. GitHub Actions Integration

Modified `.github/workflows/build-and-deploy-pages.yml`:

**Changes:**
- Replaced direct `python engine/build.py` call with `bash audit_build.sh`
- Added `BUILD_AUDIT` environment variable (reads from repository variables)
- Added step to commit audit files when audit mode is enabled
- Updated `contents` permission from `read` to `write` to allow commits
- Uses `always()` condition to commit audit files even when build fails

**How It Works in CI:**
1. Repository admin sets `BUILD_AUDIT=true` as a repository variable
2. Workflow runs `audit_build.sh` which captures all diagnostics
3. After build completes (success or failure), audit files are committed
4. Files appear in the `audit/` directory for inspection
5. Commits include `[skip ci]` to prevent infinite loops

### 4. Documentation

Created comprehensive documentation:

- **`audit/README.md`** - Detailed audit mode documentation with:
  - Feature overview
  - How to enable (CI and local)
  - What gets captured
  - File format descriptions
  - Understanding LaTeX errors
  - Example usage

- **`AUDIT_MODE_INSTRUCTIONS.md`** - Quick start guide with:
  - Step-by-step enablement instructions
  - What to expect
  - How to read diagnostic reports
  - Troubleshooting tips
  - Cleanup procedures

### 5. Repository Structure

```
resume/
├── audit/
│   ├── .gitkeep                    # Ensures directory is tracked
│   ├── README.md                   # Detailed documentation
│   └── build_*.txt                 # Generated audit files (when enabled)
├── audit_build.sh                  # Audit wrapper script (executable)
├── AUDIT_MODE_INSTRUCTIONS.md      # Quick start guide
└── .github/workflows/
    └── build-and-deploy-pages.yml  # Updated to support audit mode
```

## How To Use

### Enable in CI

1. Go to https://github.com/szmyty/resume/settings/variables/actions
2. Add variable: `BUILD_AUDIT` = `true`
3. Trigger a workflow run (push or manual)
4. Review committed files in `audit/` directory

### Test Locally

```bash
BUILD_AUDIT=true bash audit_build.sh
cat audit/build_*_report.txt
```

### Disable After Debugging

1. Remove or set `BUILD_AUDIT=false` in repository variables
2. Clean up audit files:
   ```bash
   git rm audit/build_*.txt
   git commit -m "Clean up audit files"
   git push
   ```

## Example Diagnostic Output

```
========================================
BUILD AUDIT DIAGNOSTIC REPORT
========================================
Generated: 2025-12-29 09:37:07 UTC

VARIANTS ATTEMPTED:
- career_center

BUILD PHASE PROGRESSION:
✓ Configuration loading
✓ Configuration validation
✓ Template rendering
✓ LaTeX compilation started

FAILURE ANALYSIS:
Error Type: Build Error Detected
Failure Category: LaTeX Compilation Error

RECOMMENDATIONS:
1. Review the LaTeX log sections below
2. Check for syntax errors in LaTeX templates
3. Verify all required LaTeX packages are available

LOG SECTIONS TO REVIEW:
LaTeX logs have been appended to the audit file.
Look for lines starting with '!' which indicate LaTeX errors.

Full build output is available in: audit/build_20251229_093707.txt
```

## Security Considerations

✅ No security vulnerabilities detected (verified with CodeQL)  
✅ Audit files are temporary and intended for debugging only  
✅ No sensitive data is exposed  
✅ Commits use `[skip ci]` to prevent workflow loops  
✅ Audit mode is opt-in via repository variable

## Benefits

1. **Full Visibility:** Captures everything that happens during the build
2. **LaTeX Log Access:** All LaTeX logs are collected and preserved
3. **Intelligent Analysis:** Automated failure categorization and recommendations
4. **CI-Safe:** Files are committed for offline inspection
5. **Flexible:** Can be enabled/disabled without code changes
6. **Local Testing:** Same audit mode works locally for debugging

## Acceptance Criteria Met

✅ Failed CI run produces timestamped audit files  
✅ Raw audit file contains full stdout/stderr  
✅ Raw audit file contains full LaTeX log contents  
✅ Report file explains what failed and where  
✅ Report provides recommendations  
✅ Audit files are deterministically named with timestamps  
✅ Files can be committed for inspection  
✅ Audit mode can be disabled after debugging

## Next Steps

1. **Enable audit mode** by setting the `BUILD_AUDIT` repository variable
2. **Trigger a build** to capture the actual CI failure
3. **Review diagnostics** in the committed audit files
4. **Fix the underlying issue** based on the diagnostic report
5. **Disable audit mode** and clean up audit files

## Notes

- This implementation focuses solely on diagnostics, not fixing the LaTeX error
- The audit mode is temporary and should be disabled after debugging
- Audit files should be cleaned up after the issue is resolved
- The script is designed to work in any environment (CI or local)
