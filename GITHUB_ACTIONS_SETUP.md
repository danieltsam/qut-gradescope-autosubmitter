# GitHub Actions Setup Guide (not working yet)

This guide explains how to set up automated Gradescope submissions using GitHub Actions.

## 🚀 Quick Setup

### 1. Repository Secrets

Add these secrets to your GitHub repository (`Settings > Secrets and variables > Actions`):

- `GRADESCOPE_USERNAME`: Your QUT student number (e.g., `n12345678`)
- `GRADESCOPE_PASSWORD`: Your QUT password

### 2. Repository Variables

Add these variables to your GitHub repository (`Settings > Secrets and variables > Actions`):

- `GRADESCOPE_COURSE`: Course code (e.g., `cab201`)
- `GRADESCOPE_ASSIGNMENT`: Assignment name (e.g., `t6q1`)

### 3. Workflow Files

The following workflow files are included:

#### `auto-submit.yml` - Submit on Every Push
- Triggers on push to main/master branch
- Automatically submits your latest code
- Perfect for continuous assignment submissions

#### `scheduled-submit.yml` - Daily Scheduled Submissions
- Runs daily at 11:59 PM
- Only submits if there are commits in the last 24 hours
- Great for assignment deadlines

#### `test-package.yml` - Package Testing
- Tests the package across multiple OS and Python versions
- Ensures code quality and compatibility

## 📋 Configuration Options

### Custom Configuration

Create a `gradescope.yml` file in your repository root:

```yaml
course: cab201
assignment: t6q1
file: submission.zip
bundle: ['*.py', '*.cpp', '*.h']  # Customize file patterns
notify_when_graded: false  # Don't wait for grades in CI
headless: true  # Always run headless in CI
```

### Environment Variables Override

You can override config values using environment variables in your workflows:

```yaml
env:
  GRADESCOPE_COURSE: cab202
  GRADESCOPE_ASSIGNMENT: assignment-1
  GRADESCOPE_FILE: my-submission.zip
```

## 🔒 Security Best Practices

1. **Never commit credentials** - Use GitHub Secrets only
2. **Use repository variables** for non-sensitive config (course, assignment)
3. **Enable branch protection** to prevent accidental submissions
4. **Review workflow runs** regularly

## 🛠️ Customization Examples

### Submit Only Specific File Types

```yaml
- name: Create config file
  run: |
    cat > gradescope.yml << EOF
    course: ${{ vars.GRADESCOPE_COURSE }}
    assignment: ${{ vars.GRADESCOPE_ASSIGNMENT }}
    bundle: ['*.py', '*.txt', 'src/**/*.cpp']
    EOF
```

### Submit Only on Specific Branches

```yaml
on:
  push:
    branches: [ main, submission ]  # Only submit from these branches
```

### Submit Only When Specific Files Change

```yaml
on:
  push:
    paths:
      - 'src/**'
      - '*.py'
      - '!README.md'
```

### Manual Trigger with Parameters

```yaml
on:
  workflow_dispatch:
    inputs:
      assignment:
        description: 'Assignment name'
        required: true
        default: 't6q1'
      course:
        description: 'Course code'
        required: true
        default: 'cab201'
```

## 🚨 Troubleshooting

### Common Issues

1. **"Config file not found"**
   - Ensure `gradescope.yml` exists in repository root
   - Check workflow creates config correctly

2. **"Missing credentials"**
   - Verify secrets are set correctly
   - Check secret names match exactly

3. **"Course/Assignment not found"**
   - Verify course and assignment names match Gradescope
   - Use partial matching (e.g., 'cab201' matches 'CAB201_24se2')

4. **"Browser timeout"**
   - QUT SSO might be slow, increase timeouts
   - Check if QUT systems are operational

### Debug Mode

Add debug output to your workflow:

```yaml
- name: Debug submission
  env:
    GRADESCOPE_USERNAME: ${{ secrets.GRADESCOPE_USERNAME }}
    GRADESCOPE_PASSWORD: ${{ secrets.GRADESCOPE_PASSWORD }}
  run: |
    gradescope doctor
    gradescope validate
    gradescope submit --headless --no-grade-wait
```

## 📊 Monitoring

### View Submission History

- Go to `Actions` tab in your repository
- Click on workflow runs to see logs
- Download submission artifacts

### Notifications

Enable GitHub notifications for:
- Workflow failures
- Successful submissions
- Security alerts

## ⚡ Advanced Usage

### Matrix Submissions

Submit to multiple courses/assignments:

```yaml
strategy:
  matrix:
    include:
      - course: cab201
        assignment: t6q1
      - course: cab202
        assignment: assignment-1

steps:
  - name: Submit to ${{ matrix.course }}
    env:
      GRADESCOPE_COURSE: ${{ matrix.course }}
      GRADESCOPE_ASSIGNMENT: ${{ matrix.assignment }}
```

### Conditional Submissions

Only submit during semester:

```yaml
- name: Check if in semester
  id: semester
  run: |
    CURRENT_MONTH=$(date +%m)
    if [[ $CURRENT_MONTH -ge 2 && $CURRENT_MONTH -le 6 ]] || [[ $CURRENT_MONTH -ge 7 && $CURRENT_MONTH -le 11 ]]; then
      echo "in_semester=true" >> $GITHUB_OUTPUT
    else
      echo "in_semester=false" >> $GITHUB_OUTPUT
    fi

- name: Submit
  if: steps.semester.outputs.in_semester == 'true'
  run: gradescope submit
```

## 🎯 Best Practices

1. **Test locally first** before enabling auto-submission
2. **Use branch protection** to prevent accidental pushes
3. **Monitor quota usage** - GitHub has action minute limits
4. **Set up notifications** for failed submissions
5. **Review logs regularly** to ensure submissions work
6. **Keep credentials secure** - rotate passwords periodically

## 📝 Example Repository Structure

```
my-assignment/
├── .github/
│   └── workflows/
│       ├── auto-submit.yml
│       └── scheduled-submit.yml
├── src/
│   ├── main.py
│   └── utils.py
├── gradescope.yml
├── README.md
└── requirements.txt
```

This setup provides automated, secure, and reliable Gradescope submissions integrated with your development workflow! 🎉


