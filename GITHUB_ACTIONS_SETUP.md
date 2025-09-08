# Automation Setup Guide

Complete guide for setting up automated Gradescope submissions using Git hooks (local automation) and GitHub Actions (cloud automation).

## Automation Overview

The QUT Gradescope Auto Submitter supports multiple automation approaches:

1. **Git Hooks** - Local automation that runs on every commit
2. **GitHub Actions** - Cloud-based automation for pushes, schedules, and manual triggers  
3. **Combined Setup** - Use both for maximum automation coverage

---

## Git Hooks (Local Automation)

Git hooks automatically run Gradescope submissions when you commit code locally. This provides immediate feedback and works entirely on your machine.

### Quick Setup

**Interactive Setup (Recommended):**
```bash
gradescope hooks
```

This opens an interactive menu with all options:
- Install full hooks (submit + wait for grade)
- Install quick hooks (submit only, no grade wait)
- View current hooks
- Remove hooks

### Hook Types

#### Full Hooks (With Grade Monitoring)
- **Command**: `gradescope submit --headless`
- **Behavior**: Submit to Gradescope and wait for grade feedback
- **Use Case**: Interactive development when you want immediate grade results
- **Time**: 30 seconds to several minutes (depending on grading speed)

#### Quick Hooks (Submit Only)
- **Command**: `gradescope submit --headless --no-grade-wait`
- **Behavior**: Submit to Gradescope but don't wait for grades
- **Use Case**: Rapid development cycles, CI/CD pipelines
- **Time**: Usually under 10 seconds

### Hook Timing

#### Pre-commit Hooks
- **When**: Runs **before** your commit is finalized
- **Advantage**: Ensures submission happens even if you forget
- **Consideration**: May delay your commit process

#### Post-commit Hooks  
- **When**: Runs **after** your commit is saved
- **Advantage**: Doesn't block the commit process
- **Consideration**: Submission happens after commit is already saved

### Manual Hook Setup

If you prefer manual setup:

#### 1. Create Pre-commit Hook (Full Mode)
```bash
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook for Gradescope submissions (with grade monitoring)
echo "Pre-commit: Checking for gradescope.yml..."

if [ -f "gradescope.yml" ]; then
    echo "Found gradescope.yml, running submission with grade monitoring..."
    gradescope submit --headless
    if [ $? -eq 0 ]; then
        echo "Gradescope submission and grading completed successfully"
    else
        echo "Gradescope submission failed"
        echo "Commit will proceed anyway..."
    fi
else
    echo "No gradescope.yml found, skipping submission"
fi
EOF

chmod +x .git/hooks/pre-commit
```

#### 2. Create Post-commit Hook (Quick Mode)
```bash
cat > .git/hooks/post-commit << 'EOF'
#!/bin/bash
# Post-commit hook for Gradescope submissions (quick mode)
echo "Post-commit: Checking for gradescope.yml..."

if [ -f "gradescope.yml" ]; then
    echo "Found gradescope.yml, running quick submission..."
    gradescope submit --headless --no-grade-wait
    if [ $? -eq 0 ]; then
        echo "Gradescope submission successful (not waiting for grade)"
    else
        echo "Gradescope submission failed"
    fi
else
    echo "No gradescope.yml found, skipping submission"
fi
EOF

chmod +x .git/hooks/post-commit
```

### Example Workflows

#### Development with Full Hooks
```bash
git add solution.py
git commit -m "Implement bubble sort algorithm"
# → Pre-commit hook runs
# → Submits to Gradescope
# → Waits for grade
# → Shows: "Grade returned after 0:45: 15.0 / 15.0 (100%)"
# → Commit completes
```

#### Rapid Development with Quick Hooks
```bash
git add *.py
git commit -m "Work in progress - testing approach"
# → Post-commit hook runs
# → Quick submission to Gradescope
# → "Gradescope submission successful (not waiting for grade)"
# → Continue coding immediately
```

### Hook Management

#### View Current Hooks
```bash
gradescope hooks
# Choose option: "View current hooks"
```

#### Remove Hooks
```bash
gradescope hooks
# Choose option: "Remove hooks"
```

#### Manual Hook Removal
```bash
rm -f .git/hooks/pre-commit
rm -f .git/hooks/post-commit
```

---

## GitHub Actions (Cloud Automation)

GitHub Actions provide cloud-based automation that runs in GitHub's servers. Perfect for team projects, scheduled submissions, and CI/CD integration.

### Repository Configuration

#### 1. Repository Secrets

Navigate to `Settings > Secrets and variables > Actions` and add:

- **`GRADESCOPE_USERNAME`**: Your QUT student number (e.g., `n12345678`)
- **`GRADESCOPE_PASSWORD`**: Your QUT password

#### 2. Repository Variables

Add these variables in the same location:

- **`GRADESCOPE_COURSE`**: Your course code (e.g., `cab201`)
- **`GRADESCOPE_ASSIGNMENT`**: Your assignment name (e.g., `t6q1`)

### Workflow Files

Create these files in `.github/workflows/`:

#### Auto-Submit on Push
**File**: `.github/workflows/auto-submit.yml`

```yaml
name: Auto Submit to Gradescope

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  submit:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        cache: 'pip'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install playwright pyyaml python-dotenv click rich
        pip install -i https://test.pypi.org/simple/ qut-gradescope-autosubmitter
        playwright install chromium
    
    - name: System check
      run: gradescope doctor
    
    - name: Validate configuration
      run: gradescope validate
    
    - name: Submit to Gradescope
      env:
        GRADESCOPE_USERNAME: ${{ secrets.GRADESCOPE_USERNAME }}
        GRADESCOPE_PASSWORD: ${{ secrets.GRADESCOPE_PASSWORD }}
        GRADESCOPE_COURSE: ${{ vars.GRADESCOPE_COURSE }}
        GRADESCOPE_ASSIGNMENT: ${{ vars.GRADESCOPE_ASSIGNMENT }}
      run: gradescope submit --headless
```

#### Manual Trigger with Parameters
**File**: `.github/workflows/manual-submit.yml`

```yaml
name: Manual Submit to Gradescope

on:
  workflow_dispatch:
    inputs:
      assignment:
        description: 'Assignment name (overrides config)'
        required: false
        type: string
      course:
        description: 'Course code (overrides config)'
        required: false
        type: string
      wait_for_grade:
        description: 'Wait for grade result'
        required: false
        default: true
        type: boolean

jobs:
  submit:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        cache: 'pip'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install playwright pyyaml python-dotenv click rich
        pip install -i https://test.pypi.org/simple/ qut-gradescope-autosubmitter
        playwright install chromium
    
    - name: Submit to Gradescope
      env:
        GRADESCOPE_USERNAME: ${{ secrets.GRADESCOPE_USERNAME }}
        GRADESCOPE_PASSWORD: ${{ secrets.GRADESCOPE_PASSWORD }}
        GRADESCOPE_COURSE: ${{ vars.GRADESCOPE_COURSE }}
        GRADESCOPE_ASSIGNMENT: ${{ vars.GRADESCOPE_ASSIGNMENT }}
      run: |
        cmd="gradescope submit --headless"
        
        if [ "${{ inputs.wait_for_grade }}" = "false" ]; then
          cmd="$cmd --no-grade-wait"
        fi
        
        if [ -n "${{ inputs.assignment }}" ]; then
          cmd="$cmd --assignment '${{ inputs.assignment }}'"
        fi
        
        if [ -n "${{ inputs.course }}" ]; then
          cmd="$cmd --course '${{ inputs.course }}'"
        fi
        
        echo "Running: $cmd"
        eval $cmd
```

#### Scheduled Daily Submissions
**File**: `.github/workflows/scheduled-submit.yml`

```yaml
name: Scheduled Submit to Gradescope

on:
  schedule:
    # Run daily at 6 PM UTC (adjust for your timezone)
    - cron: '0 18 * * *'
  workflow_dispatch: # Allow manual triggering

jobs:
  submit:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        cache: 'pip'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install playwright pyyaml python-dotenv click rich
        pip install -i https://test.pypi.org/simple/ qut-gradescope-autosubmitter
        playwright install chromium
    
    - name: Submit to Gradescope
      env:
        GRADESCOPE_USERNAME: ${{ secrets.GRADESCOPE_USERNAME }}
        GRADESCOPE_PASSWORD: ${{ secrets.GRADESCOPE_PASSWORD }}
        GRADESCOPE_COURSE: ${{ vars.GRADESCOPE_COURSE }}
        GRADESCOPE_ASSIGNMENT: ${{ vars.GRADESCOPE_ASSIGNMENT }}
      run: gradescope submit --headless
```

### Configuration Setup

Create `gradescope.yml` in your repository root:

```yaml
course: "cab201"
assignment: "t6q1"
bundle:
  - "*.py"
  - "*.java"
  - "*.cpp"
  - "*.c"
  - "requirements.txt"
  - "README.md"
headless: true
notify_when_graded: true
```

### Usage Examples

#### Automatic on Push
```bash
git add solution.py
git push origin main
# → GitHub Action triggers automatically
# → Submits to Gradescope in the cloud
# → Check Actions tab for results
```

#### Manual Trigger
1. Go to your repository on GitHub
2. Click **Actions** tab
3. Select **Manual Submit to Gradescope**
4. Click **Run workflow**
5. Fill in parameters (optional)
6. Click **Run workflow**

#### Scheduled Submissions
- Automatically runs daily at the scheduled time
- Perfect for deadline reminders
- Check Actions tab for logs

---

## Combined Setup: Git Hooks + GitHub Actions

For maximum automation coverage, use both:

### Local Development Flow
```bash
# Work locally with Git hooks
git add *.py
git commit -m "Implement solution"
# → Git hook submits locally
# → Get immediate feedback

# Push to share with team
git push origin main
# → GitHub Action submits from cloud
# → Team can see results in Actions tab
```

### Configuration

1. **Git Hooks**: Quick local feedback
2. **GitHub Actions**: Team visibility and backup submissions
3. **Scheduled Actions**: Deadline reminders

### Best Practices

1. **Local Hooks**: Use quick mode for development
2. **GitHub Actions**: Use full mode for official submissions
3. **Documentation**: Document your automation setup for teammates
4. **Testing**: Test both locally and in GitHub before deadlines

---

## Troubleshooting

### Git Hooks Issues

**Hook not running:**
```bash
# Check if hook file exists and is executable
ls -la .git/hooks/
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/post-commit
```

**Unicode errors on Windows:**
- Hooks should not contain emojis or special characters
- Use the interactive setup to create clean hooks: `gradescope hooks`

### GitHub Actions Issues

**Credentials not working:**
- Verify secrets are set correctly in repository settings
- Check that variable names match exactly
- Ensure QUT credentials are valid

**Workflow not triggering:**
- Check branch names in workflow files
- Verify workflow files are in `.github/workflows/`
- Check Actions tab for error messages

**Submission failures:**
- Run `gradescope doctor` locally first
- Check that `gradescope.yml` is valid
- Verify course and assignment names

### General Issues

**Configuration problems:**
```bash
gradescope validate  # Check configuration
gradescope doctor    # Check system requirements
```

**Session issues:**
```bash
gradescope cleanup   # Clear saved sessions
```

## Related Documentation

- **[Main README](../README.md)** - Quick start guide and overview
- **[Command Reference](CLI_REFERENCE.md)** - Complete command documentation
- **[Credential Management](CREDENTIALS.md)** - Security options and setup