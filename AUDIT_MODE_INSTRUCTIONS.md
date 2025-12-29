# How to Enable Build Audit Mode in CI

This guide explains how to enable the build audit mode in GitHub Actions to capture full diagnostics when the resume build fails.

⚠️ **IMPORTANT: Temporary Debugging Feature**  
Audit mode is designed for short-term debugging only. It grants the workflow write permissions to commit diagnostic files. **Always disable after debugging** and clean up audit files.

## Quick Start

1. **Add the BUILD_AUDIT variable to your repository:**
   - Go to https://github.com/szmyty/resume/settings/variables/actions
   - Click "New repository variable"
   - Name: `BUILD_AUDIT`
   - Value: `true`
   - Click "Add variable"

2. **Trigger a workflow run:**
   - Push a commit to the `master` or `main` branch, OR
   - Go to Actions → "Build and Deploy Resumes to GitHub Pages" → "Run workflow"

3. **Review the audit files:**
   - After the workflow completes (even if it fails), check the repository
   - New files will be committed to the `audit/` directory:
     - `audit/build_YYYYMMDD_HHMMSS.txt` - Full build output with LaTeX logs
     - `audit/build_YYYYMMDD_HHMMSS_report.txt` - Diagnostic summary
   
4. **Examine the diagnostic report:**
   ```bash
   # Clone/pull the latest changes
   git pull
   
   # View the most recent diagnostic report
   cat audit/build_*_report.txt | tail -50
   ```

## What Gets Captured

When `BUILD_AUDIT=true`:

✅ Complete stdout/stderr from `python engine/build.py`  
✅ All LaTeX log files (resume.log, texput.log, *.aux, etc.)  
✅ Intelligent failure analysis:
  - Which resume variant failed
  - What build phase the failure occurred in
  - Specific error messages and stack traces
  - LaTeX error categorization
  - Recommendations for fixes

## After Debugging

Once you've identified and fixed the issue:

1. **Disable audit mode:**
   - Go to repository settings → Variables → Actions
   - Delete the `BUILD_AUDIT` variable, OR
   - Change its value to `false`

2. **Clean up old audit files:**
   ```bash
   git rm audit/build_*.txt
   git commit -m "Clean up audit files after debugging"
   git push
   ```

## Testing Locally

You can also test audit mode on your local machine:

```bash
# Enable audit mode
BUILD_AUDIT=true bash audit_build.sh

# Review the diagnostic report
cat audit/build_*_report.txt

# Search for specific LaTeX errors
grep "! LaTeX Error:" audit/build_*.txt
```

## Understanding the Output

### Diagnostic Report Structure

```
BUILD AUDIT DIAGNOSTIC REPORT
==============================

VARIANTS ATTEMPTED:         # Which resume(s) were being built
BUILD PHASE PROGRESSION:    # Which steps completed successfully
FAILURE ANALYSIS:           # What went wrong
  - Error Type
  - Failure Category
  - Error Messages
RECOMMENDATIONS:            # What to try next
LOG SECTIONS TO REVIEW:     # Where to look in the full log
```

### Common LaTeX Error Patterns

Look for these in the full audit log (`build_*.txt`):

- `! LaTeX Error:` - General LaTeX compilation errors
- `! Undefined control sequence` - Missing package or typo in command
- `! File ... not found` - Missing file or incorrect path
- `! Missing $ inserted` - Math mode syntax error
- `! Package ... Error:` - Package-specific issues

## Troubleshooting

**Q: The audit files aren't being committed**  
A: Make sure the `BUILD_AUDIT` variable is set to exactly `true` (lowercase) in repository variables.

**Q: The workflow is still failing even with audit mode**  
A: That's expected! Audit mode captures the failure details but doesn't prevent the failure. Review the generated audit files to diagnose the issue.

**Q: I want to see real-time output during the build**  
A: Click on the workflow run in GitHub Actions → click on the "build" job → expand the "Build resume site" step to see live output.

## Example: Reading a Diagnostic Report

```
FAILURE ANALYSIS:
Failure Category: LaTeX Compilation Error
Location: During PDF generation with Tectonic

LaTeX Error Details:
! LaTeX Error: File `default.sty' not found.
```

This tells you:
1. The build failed during PDF generation
2. LaTeX couldn't find the `default.sty` file
3. You should check if the style file exists and is in the right location

## Related Files

- `audit_build.sh` - The audit wrapper script
- `audit/README.md` - Detailed audit mode documentation
- `.github/workflows/build-and-deploy-pages.yml` - The CI workflow configuration
