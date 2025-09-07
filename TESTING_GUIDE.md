# QUT Gradescope Auto Submitter - Testing Guide

This guide will help you test all features of the package thoroughly.

## 🧪 Prerequisites

1. **QUT Student Account** - You'll need valid QUT credentials
2. **Active Assignment** - An assignment on Gradescope you can submit to
3. **Test Files** - Some files to bundle and submit

## 📋 Complete Testing Checklist

### ✅ 1. Installation Test

```bash
# Check version
gradescope --version

# Should show: qut-gradescope-autosubmitter 1.0.0
```

### ✅ 2. System Check

```bash
# Run diagnostics
gradescope doctor

# Should show:
# ✅ Python version
# ✅ Playwright installed  
# ✅ PyYAML available
# ⚠️ No config file (expected)
# ⚠️ Credentials not set (expected)
```

### ✅ 3. Configuration Tests

```bash
# Create config file
gradescope init

# Check the generated gradescope.yml contains:
# - always_fresh_login: false
# - Platform-specific credential instructions
# - Course/assignment placeholders

# Validate empty config (should fail)
gradescope validate

# Edit gradescope.yml with your real course/assignment
# Then validate again (should pass)
gradescope validate
```

### ✅ 4. Credential Setup Tests

**Option A: User-level .env (Recommended)**
```bash
# Test credential management interface
gradescope credentials

# Should show menu:
# 1. Manage saved credentials (.env, user-level)
# 2. Environment variables (session/system)
# 3. Exit

# Choose: 1 → 1 (Save/update credentials)
# Enter your QUT username and password when prompted
# Should show: ✅ Credentials saved to [user-level path]

# Test credential detection
gradescope doctor  # Should show ✅ for credentials
```

**Option B: Environment Variables**
```bash
# Windows PowerShell
$env:GRADESCOPE_USERNAME = "your_qut_username"
$env:GRADESCOPE_PASSWORD = "your_qut_password"

# Linux/Mac
export GRADESCOPE_USERNAME="your_qut_username"
export GRADESCOPE_PASSWORD="your_qut_password"

# Test credentials are set
gradescope doctor  # Should show ✅ for credentials
```

**Test Credential Management Features:**
```bash
# Update saved credentials
gradescope credentials → 1 → 1 (should re-prompt)

# Delete saved credentials  
gradescope credentials → 1 → 2 (should remove .env file)

# Get environment variable help
gradescope credentials → 2 → 1 (setup commands)
gradescope credentials → 2 → 2 (clear commands)
```

**Test Submit-time Credential Prompts:**
```bash
# Clear all credentials first
gradescope credentials → 1 → 2  # Delete .env if exists
unset GRADESCOPE_USERNAME GRADESCOPE_PASSWORD  # Linux/Mac
Remove-Item Env:GRADESCOPE_USERNAME, Env:GRADESCOPE_PASSWORD  # Windows PS

# Run submit - should prompt with options:
gradescope submit --no-grade-wait
# Should show:
# 1) Enter and save to .env (local project file)
# 2) Enter once for this run  
# 3) Cancel
```

### ✅ 5. Session Management Tests

**Test 1: Default Session Persistence**
```bash
# Initial submission (should login)
gradescope submit --headless --course "your_course" --assignment "your_assignment"

# Should show:
# [timestamp] 🌐 Navigating directly to QUT SSO...
# [timestamp] 👤 QUT login detected. Entering credentials...
# [timestamp] 🔓 QUT login complete

# Second submission immediately after (should reuse session)
gradescope submit --headless --course "your_course" --assignment "your_assignment"

# Should show:
# [timestamp] 🔄 Using saved session...
```

**Test 2: Fresh Login Flag**
```bash
# Force fresh login
gradescope submit --fresh-login --headless --course "your_course" --assignment "your_assignment"

# Should show:
# [timestamp] 🧹 Using fresh login (clearing session)
# [timestamp] 🌐 Navigating directly to QUT SSO...
```

**Test 3: Security-Paranoid Mode**
```bash
# Edit gradescope.yml
# Set: always_fresh_login: true

gradescope submit --headless

# Should always show fresh login flow
```

**Test 4: Session Cleanup**
```bash
# Clear sessions manually
gradescope cleanup

# Should show: ✅ Session data cleared
```

### ✅ 6. File Bundling Tests

```bash
# Create test files
echo "print('test')" > test.py
echo "int main() { return 0; }" > test.cpp

# Test specific patterns
gradescope submit --bundle "*.py" --bundle "*.cpp" --file test-bundle.zip

# Check that test-bundle.zip was created with correct files
```

### ✅ 7. Configuration Override Tests

```bash
# Test CLI overrides config file
gradescope submit --course "different_course" --assignment "different_assignment"

# Test environment variable overrides
export GRADESCOPE_COURSE="env_course"
gradescope submit  # Should use env_course
```

### ✅ 8. Error Handling Tests

**Test Invalid Config**
```bash
# Create config with missing course
echo "assignment: test" > bad-config.yml
gradescope validate --config bad-config.yml

# Should show: ❌ Missing required config fields: course
```

**Test Invalid Credentials**
```bash
# Set wrong credentials
export GRADESCOPE_USERNAME="invalid"
export GRADESCOPE_PASSWORD="invalid"

gradescope submit --headless
# Should fail gracefully with error message
```

### ✅ 9. Advanced Feature Tests

**Test Grade Monitoring**
```bash
# Submit and wait for grade
gradescope submit --course "your_course" --assignment "your_assignment"

# Should wait and show grade when available
# Use --no-grade-wait to skip
```

**Test Headless vs Visual Mode**
```bash
# Headless mode (no browser window)
gradescope submit --headless

# Visual mode (browser window opens)
gradescope submit
# Should open browser window and leave it open at the end
```

## 🔍 Debugging Common Issues

### "Could not find course/assignment"
- Check course/assignment names match exactly what's on Gradescope
- Try shorter partial matches
- Use `gradescope validate` to check config

### "Session expired/login failed"
- Use `gradescope cleanup` to clear sessions
- Try `--fresh-login` flag
- Check credentials with `gradescope doctor`

### "Browser timeout"
- Try `--headless` mode
- Check internet connection
- Verify QUT SSO is working in regular browser

### "File not found"
- Check file patterns in bundle configuration
- Verify files exist in current directory
- Use `ls` or `dir` to check what files would be included

## ✅ Success Criteria

After testing, you should be able to:

1. ✅ Install and run all CLI commands
2. ✅ Create and validate configuration files
3. ✅ Submit files successfully (at least once)
4. ✅ See session persistence working (faster second submission)
5. ✅ Use fresh login when needed
6. ✅ Clear sessions with cleanup command
7. ✅ Override config with CLI flags and environment variables

## 🚀 Final Test

Create a realistic workflow:

```bash
# 1. Setup
gradescope init
# Edit config with real course/assignment
export GRADESCOPE_USERNAME="your_username"
export GRADESCOPE_PASSWORD="your_password"

# 2. Multiple submissions (like real development)
echo "version 1" > assignment.py
gradescope submit  # Login + submit

echo "version 2" > assignment.py  
gradescope submit  # Fast submit (reuses session)

echo "version 3" > assignment.py
gradescope submit  # Fast submit

# 3. Cleanup
gradescope cleanup
```

If this workflow completes successfully, your package is ready for production! 🎉
