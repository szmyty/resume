# Build Audit Mode

This directory contains build diagnostic files generated when audit mode is enabled.

## Overview

The build audit mode captures comprehensive diagnostics from the resume build pipeline to help debug failures that occur in CI environments where LaTeX errors may not be fully visible.

## How to Enable Audit Mode

### In GitHub Actions

1. Go to your repository settings
2. Navigate to **Settings** > **Secrets and variables** > **Actions**
3. Click on **Variables** tab
4. Add a new repository variable:
   - Name: `BUILD_AUDIT`
   - Value: `true`
5. Trigger a workflow run (push or manual dispatch)

### Locally

Run the build with audit mode enabled:

```bash
BUILD_AUDIT=true bash audit_build.sh
```

## What Gets Captured

When audit mode is enabled, the following diagnostics are collected:

1. **Full Build Output** (`build_<timestamp>.txt`)
   - Complete stdout and stderr from the build process
   - All Python build script output
   - Tectonic LaTeX compilation output
   - All LaTeX log files (resume.log, texput.log, etc.)

2. **Diagnostic Report** (`build_<timestamp>_report.txt`)
   - Build timestamp
   - Resume variant(s) attempted
   - Build phase progression (which steps completed)
   - Failure analysis with categorization:
     - LaTeX syntax errors
     - Missing files or templates
     - Configuration parse errors
     - Encoding issues
   - Specific error locations
   - Recommendations for fixing the issue
   - Pointers to relevant log sections

## Generated Files

- `audit/build_YYYYMMDD_HHMMSS.txt` - Full build output and logs
- `audit/build_YYYYMMDD_HHMMSS_report.txt` - Human-readable diagnostic report

## After Debugging

Once you've identified and fixed the issue:

1. Disable audit mode by removing or setting `BUILD_AUDIT=false`
2. Delete old audit files:
   ```bash
   git rm audit/build_*.txt
   git commit -m "Clean up audit files"
   git push
   ```

## Audit File Format

### Build Output File

```
========================================
BUILD AUDIT MODE ENABLED
========================================
Timestamp: YYYYMMDD_HHMMSS
...

[Full build output]

========================================
LATEX LOG FILES
========================================

===== resumes/variant/build/resume.log =====
[LaTeX log content]
...
```

### Diagnostic Report File

```
========================================
BUILD AUDIT DIAGNOSTIC REPORT
========================================
Generated: YYYY-MM-DD HH:MM:SS UTC

VARIANTS ATTEMPTED:
- career_center

BUILD PHASE PROGRESSION:
✓ Configuration loading
✓ Configuration validation
✓ Template rendering
✓ LaTeX compilation started
✗ Build failed

FAILURE ANALYSIS:
Error Type: LaTeX Compilation Error
Failure Category: [specific category]

RECOMMENDATIONS:
1. [Specific recommendation]
2. [Specific recommendation]
...

LOG SECTIONS TO REVIEW:
[Guidance on where to look in the logs]
```

## Understanding LaTeX Errors

Common LaTeX error patterns in the logs:

- `! LaTeX Error:` - General LaTeX errors
- `! Undefined control sequence` - Missing package or misspelled command
- `! File ... not found` - Missing file reference
- `! Missing $ inserted` - Math mode error
- `! Package ... Error:` - Package-specific errors

Look for lines starting with `!` in the full audit log for detailed error information.

## Example Usage

```bash
# Enable audit mode locally
BUILD_AUDIT=true bash audit_build.sh

# Review the diagnostic report
cat audit/build_*_report.txt

# Search for specific errors in full log
grep "! LaTeX Error:" audit/build_*.txt
```

## Integration with CI

The audit files are automatically committed to the repository when a build fails in CI with audit mode enabled. This allows you to inspect the exact failure conditions that occurred in the CI environment, even after the workflow run has completed.
