<<<<<<< HEAD
# QUT Gradescope Auto Submitter

<div align="center">
  
[![TestPyPI version](https://badge.fury.io/py/qut-gradescope-autosubmitter.svg)](https://test.pypi.org/project/qut-gradescope-autosubmitter/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**🔒 Production-ready automation for QUT Gradescope submissions**

Secure • Fast • Reliable • CI/CD Ready

[Installation](#installation) • [Quick Start](#quick-start) • [GitHub Actions](#github-actions) • [Documentation](#documentation)

> **💡 Why I built this:** As a QUT student, I was frustrated with the repetitive click-heavy Gradescope submission process. I enjoy CLI tools and automation, so I built this to streamline my workflow and make submissions as simple as `gradescope submit`.

</div>

---

## ✨ Features

- **🔐 Secure**: Environment variables, no plaintext passwords
- **⚡ Fast**: Automated file bundling and submission
- **🛠️ CLI Tool**: Global command-line interface after pip install
- **📁 YAML Config**: Modern configuration with validation
- **🤖 CI/CD Ready**: GitHub Actions workflows included
- **🎯 Smart Matching**: Fuzzy course/assignment name matching
- **📊 Grade Monitoring**: Automatic grade retrieval and display
- **🌐 Cross-platform**: Windows, macOS, Linux support

## ⚠️ Important Disclaimers

**Legal & Responsibility:**
- This tool is provided "as-is" without any warranties or guarantees
- Users are solely responsible for their use of this tool and any consequences
- The authors and contributors are not responsible for:
  - Misuse of the tool or violation of university policies
  - Failed submissions, missed deadlines, or academic consequences
  - Any issues arising from automated submission attempts
  - Rate limiting or account restrictions imposed by QUT or Gradescope

**Rate Limiting & Usage:**
- **Fresh Login Mode**: Using `--fresh-login` or `always_fresh_login: true` creates new sessions every time
- **Manual Login Mode**: Using `--manual-login` also triggers new login requests to QUT SSO
- Both modes may trigger rate limiting on QUT SSO if used excessively
- **Recommended**: Use session persistence (default) to minimize SSO requests
- **Best Practice**: Avoid running multiple submissions in rapid succession

**University Policies:**
- Ensure your use complies with QUT's academic integrity policies
- This tool is intended for legitimate assignment submission automation only
- Users are responsible for understanding and following their institution's rules

## ⚠️ Important Limitations

> **🚨 CRITICAL REQUIREMENT**: This tool **requires at least one prior manual submission** to each assignment before it can be used for automation.

**Assignment Requirement:**
- This tool only works with **existing assignments** that already have submissions on Gradescope
- It **cannot create new submissions** for assignments you haven't submitted to before
- You must make at least one manual submission through the Gradescope web interface first
- After the initial manual submission, this tool can handle all subsequent submissions automatically

**Quick Setup for New Assignments:**
1. Go to Gradescope website manually
2. Submit your assignment once (any file is fine)
3. Use this tool for all future submissions to that assignment

> **💡 Why this limitation exists**: Gradescope's interface changes based on whether an assignment has previous submissions, making automation impossible without this initial step.

## 🚀 Installation

```bash
# Install the package from TestPyPI
pip install -i https://test.pypi.org/simple/ qut-gradescope-autosubmitter

# Install browser dependencies  
playwright install chromium
```

> **📦 TestPyPI Note:** This package is currently available on TestPyPI for testing. Once stable, it will be published to the main PyPI repository.

> **⚠️ Dependency Issue:** TestPyPI has limited package availability. If you get Playwright version errors, try installing dependencies separately first:
> ```bash
> pip install playwright pyyaml python-dotenv click
> pip install -i https://test.pypi.org/simple/ qut-gradescope-autosubmitter
playwright install chromium
> ```

### Platform Notes

**Windows:** If you get permission errors, try `pip install --user -i https://test.pypi.org/simple/ qut-gradescope-autosubmitter`

**Linux/Mac:** You may need `python3` and `pip3` instead of `python` and `pip`

## ⚡ Quick Start

### 1. Initialize Configuration

```bash
# Create config file
gradescope init

# Check system requirements
gradescope doctor
```

### 2. Set Credentials

**🔐 Credentials Management**
```bash
gradescope credentials  # Guide for setting up credentials
```

**Available Methods:**

**Option A: Session Environment Variables**

**Linux/Mac (Bash/Zsh):**
```bash
export GRADESCOPE_USERNAME="n12345678"
export GRADESCOPE_PASSWORD="your_password"
# Lasts until terminal closes
```

**Windows PowerShell:**
```powershell
$env:GRADESCOPE_USERNAME = "n12345678"
$env:GRADESCOPE_PASSWORD = "your_password"
# Lasts until terminal closes
```

**Option B: .env File (Good for development)**
```bash
# Create .env file in project directory
GRADESCOPE_USERNAME=n12345678
GRADESCOPE_PASSWORD=your_password
```

> **💡 Pro tip:** The `.env` file is automatically loaded when you run any command, so you don't need to set environment variables every time you open a new terminal!

**Option C: Permanent Environment Variables**

**Windows PowerShell (Permanent):**
```powershell
[Environment]::SetEnvironmentVariable("GRADESCOPE_USERNAME", "n12345678", "User")
[Environment]::SetEnvironmentVariable("GRADESCOPE_PASSWORD", "your_password", "User")
# Restart terminal after this
```

**Linux/Mac (Permanent):**
```bash
# Add to ~/.bashrc, ~/.zshrc, or ~/.profile
echo 'export GRADESCOPE_USERNAME="n12345678"' >> ~/.bashrc
echo 'export GRADESCOPE_PASSWORD="your_password"' >> ~/.bashrc
source ~/.bashrc
```

**🔐 Security & Persistence Comparison:**

| Method | Security Level | Convenience | Duration | When to Use |
|--------|---------------|-------------|----------|-------------|
| **Session env vars** | 🟢 High | 🟡 Medium | Terminal session | Quick testing |
| **.env file** | 🟡 Medium | 🟢 High | Until deleted | Development projects |
| **Permanent env vars** | 🟡 Medium | 🟢 High | Forever | Power users |
| **Manual login** | 🟢 Highest | 🟡 Medium | None | Maximum security |

### 3. Configure Assignment

Edit `gradescope.yml`:
```yaml
# Course Details (edit these!)
course: cab201
assignment: t6q1
zip_name: submission.zip
bundle: ['*']

# Behavior Settings
always_fresh_login: false
headless: false
notify_when_graded: true
manual_login: false
no_session_save: false
```

### 4. Submit

```bash
gradescope submit
```

## 📋 CLI Commands

| Command | Description | Example |
|---------|-------------|---------|
| `gradescope submit` | Submit to Gradescope | `gradescope submit --headless` |
| `gradescope init` | Create config file | `gradescope init --path my-config.yml` |
| `gradescope validate` | Check configuration | `gradescope validate` |
| `gradescope credentials` | Manage credentials | `gradescope credentials` |
| `gradescope doctor` | System diagnostics | `gradescope doctor` |
| `gradescope cleanup` | Clear saved sessions | `gradescope cleanup` |

### Submit Options

```bash
gradescope submit [OPTIONS]

Options:
  -c, --course TEXT      Course name (e.g., CAB201)
  -a, --assignment TEXT  Assignment name
  -f, --file TEXT        Output zip file name
  -b, --bundle TEXT      File patterns (multiple allowed)
  -u, --username TEXT    QUT username
  -p, --password TEXT    QUT password (not recommended)
  --config TEXT          Config file path
  --headless             Run browser in background
  --no-grade-wait        Don't wait for grade
  --fresh-login          Force fresh login (ignore saved session)
  --manual-login         Open browser for manual login (maximum security)
  --no-session-save      Don't save credentials to session env vars
```

## 🔧 Configuration

### YAML Configuration File

```yaml
# gradescope.yml
course: cab201
assignment: t6q1
file: submission.zip
bundle:
  - "*.py"
  - "*.cpp" 
  - "src/**/*"
notify_when_graded: true
headless: false
```

### Environment Variables

All config options can be overridden with environment variables:

**Linux/Mac:**
```bash
export GRADESCOPE_USERNAME="n12345678"
export GRADESCOPE_PASSWORD="your_password"
export GRADESCOPE_COURSE="cab201"
export GRADESCOPE_ASSIGNMENT="t6q1"
export GRADESCOPE_FILE="submission.zip"
export GRADESCOPE_BUNDLE="*.py,*.cpp,*.h"
export GRADESCOPE_NOTIFY_WHEN_GRADED="true"
export GRADESCOPE_HEADLESS="false"
```

**Windows PowerShell:**
```powershell
$env:GRADESCOPE_USERNAME = "n12345678"
$env:GRADESCOPE_PASSWORD = "your_password"
$env:GRADESCOPE_COURSE = "cab201"
$env:GRADESCOPE_ASSIGNMENT = "t6q1"
$env:GRADESCOPE_FILE = "submission.zip"
$env:GRADESCOPE_BUNDLE = "*.py,*.cpp,*.h"
$env:GRADESCOPE_NOTIFY_WHEN_GRADED = "true"
$env:GRADESCOPE_HEADLESS = "false"
```

## 🔒 Security Options

### Session Management

By default, the tool uses **session persistence** for efficiency:
- **First submission**: Login once (3-5 seconds)
- **Subsequent submissions**: Reuse session (1 second)
- **Session expires**: Auto re-login when needed

### Enhanced Security Options

For enhanced security, you have several options:

**Option 1: Manual Login (Highest Security)**
```bash
gradescope submit --manual-login
# Opens browser, you type credentials directly
# Tool never touches your passwords
```

**Option 2: Fresh Login (High Security)**
```yaml
# Config file
always_fresh_login: true  # Always login fresh
```
```bash
# Command line
gradescope submit --fresh-login  # One-time fresh login
```

**What "fresh login" means:**
- Ignores any saved session data
- Forces a complete new login process
- Useful for troubleshooting or when session data is corrupted

### 🎛️ YAML Configuration

All security flags can be set in your `gradescope.yml`:

```yaml
# Course Details (edit these!)
course: cab201
assignment: t6q1
zip_name: submission.zip
bundle: ['*']

# Behavior Settings (can be overridden by CLI flags)
always_fresh_login: false    # Force fresh login every time
headless: false
notify_when_graded: true
manual_login: false          # Open browser for manual login
no_session_save: false       # Don't save credentials to session vars
```

### 🎯 Flag Purpose Guide

**When to use each security flag:**

| Flag | Purpose | Use Case |
|------|---------|----------|
| **`--manual-login`** | You type credentials directly in browser | **Maximum security** - tool never sees passwords |
| **`--fresh-login`** | Always login fresh, ignore session | **Troubleshooting** - force clean login |

> ⚠️ **Rate Limiting Note**: Both `--manual-login` and `--fresh-login` trigger new SSO requests and may cause rate limiting with frequent use.

**Typical workflows:**
- **Most users**: Set environment variables or .env file, then run `gradescope submit`
- **Maximum security**: `gradescope submit --manual-login`
- **Development**: Set permanent env vars or .env file
- **Troubleshooting**: `gradescope submit --fresh-login`

### Manual Session Management
```bash
gradescope cleanup  # Clear saved session data
```

**What `gradescope cleanup` does:**
- Removes all saved browser session data
- Clears cookies and local storage
- Forces fresh login on next submission
- Useful when switching between different QUT accounts

## 🤖 GitHub Actions

> ⚠️ **Status**: GitHub Actions integration is **not yet fully tested** and may require additional configuration. Use with caution.

Automate submissions on every commit!

> 📖 **Detailed Setup Guide**: See [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md) for comprehensive setup instructions, troubleshooting, and advanced configurations.

> ⚠️ **Rate Limiting Warning**: GitHub Actions will trigger new login requests for each run, which may trigger QUT SSO rate limiting if you have frequent commits. Consider using scheduled submissions instead of commit-based submissions for high-frequency repositories.

> ⚠️ **Previous Submission Required**: GitHub Actions workflows require assignments to have at least one prior manual submission before automation can work.

### Setup

1. **Add Repository Secrets** (`Settings > Secrets and Variables > Actions`):
   - `GRADESCOPE_USERNAME`: Your QUT student number
   - `GRADESCOPE_PASSWORD`: Your QUT password

2. **Add Repository Variables**:
   - `GRADESCOPE_COURSE`: Course code (e.g., `cab201`)
   - `GRADESCOPE_ASSIGNMENT`: Assignment name (e.g., `t6q1`)

3. **Add Workflow** (`.github/workflows/auto-submit.yml`):

```yaml
name: Auto Submit to Gradescope

on:
  push:
    branches: [ main ]

jobs:
  submit:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install and submit
      env:
        GRADESCOPE_USERNAME: ${{ secrets.GRADESCOPE_USERNAME }}
        GRADESCOPE_PASSWORD: ${{ secrets.GRADESCOPE_PASSWORD }}
        GRADESCOPE_COURSE: ${{ vars.GRADESCOPE_COURSE }}
        GRADESCOPE_ASSIGNMENT: ${{ vars.GRADESCOPE_ASSIGNMENT }}
      run: |
        pip install -i https://test.pypi.org/simple/ qut-gradescope-autosubmitter
        playwright install chromium
        gradescope submit --headless --no-grade-wait
```

See [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md) for advanced configurations.

## 📖 Examples

### Basic Python Project

```yaml
# gradescope.yml
course: cab201
assignment: "Assignment 1"
bundle: ['*.py', 'requirements.txt']
```

### C++ Project

```yaml
# gradescope.yml  
course: cab202
assignment: t6q1
bundle: ['*.cpp', '*.h', 'Makefile']
```

### Complex Project Structure

```yaml
# gradescope.yml
course: cab301
assignment: "Final Project" 
bundle: 
  - 'src/**/*.py'
  - 'tests/**/*.py'
  - 'docs/**/*.md'
  - 'requirements.txt'
  - 'README.md'
```

### Command Line Overrides

```bash
# Override config file settings
gradescope submit --course cab202 --assignment "Lab 5" --headless

# Submit specific files
gradescope submit -b "*.java" -b "*.xml" --file java-submission.zip

# Quick submission with credentials
gradescope submit -u n12345678 -p password --headless
```

## 🔒 Security Features

- **Environment Variable Support**: No hardcoded credentials
- **Secure Input Prompts**: Hidden password input
- **Input Validation**: Username format validation
- **Git-Safe Defaults**: Sensitive files auto-excluded
- **CI/CD Ready**: Headless mode for automated environments

## 🚨 Troubleshooting

### Common Issues

**"Config file not found"**
```bash
gradescope init  # Create default config
```

**"Course/Assignment not found"**
- Use partial matching: `cab201` matches `CAB201_24se2`
- Check exact names on Gradescope website
- Try shorter search terms

**"Assignment submission failed" or "Assignment not available"**
- **This tool requires at least one prior submission** to the assignment
- Go to Gradescope manually and submit once (any file works)
- Then use this tool for all future submissions
- The tool cannot create new assignment submissions

**"strict mode violation: locator resolved to 3 elements"**
- This error means the assignment has no previous submissions
- Make one manual submission through Gradescope web interface first
- Then the CLI tool will work for all subsequent submissions

**"Browser timeout"**
```bash
gradescope submit --headless  # Try headless mode
```

**"Credentials not found"**

**Linux/Mac:**
```bash
export GRADESCOPE_USERNAME="n12345678"
export GRADESCOPE_PASSWORD="your_password"
```

**Windows PowerShell:**
```powershell
$env:GRADESCOPE_USERNAME = "n12345678"
$env:GRADESCOPE_PASSWORD = "your_password"
```

### Debug Mode

```bash
# Check system status
gradescope doctor

# Validate configuration  
gradescope validate

# Test with verbose output
gradescope submit --headless --no-grade-wait
```

## 🛠️ Development

### Local Development

```bash
# Clone repository
git clone https://github.com/yourusername/qut-gradescope-autosubmitter
cd qut-gradescope-autosubmitter

# Install in development mode
pip install -e .

# Install development tools (optional)
pip install -e ".[dev]"

# Format code (optional)
black gradescope_autosubmitter

# Check for issues (optional)
flake8 gradescope_autosubmitter
```

### Building Package

```bash
# Build package
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

## 📝 Requirements

- Python 3.8+
- Playwright (automatically installed)
- PyYAML (automatically installed)
- Click (automatically installed)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run linting and tests
6. Submit a pull request

## ⚠️ Disclaimer

This tool is not affiliated with QUT or Gradescope. Use responsibly and in accordance with your institution's academic integrity policies.

## 🆘 Support

- 📚 [Documentation](GITHUB_ACTIONS_SETUP.md)
- 🐛 [Issue Tracker](https://github.com/yourusername/qut-gradescope-autosubmitter/issues)
- 💬 [Discussions](https://github.com/yourusername/qut-gradescope-autosubmitter/discussions)

---

<div align="center">

**Made with ❤️ for QUT students**

[⭐ Star this repo](https://github.com/yourusername/qut-gradescope-autosubmitter) if it helped you!

</div>
=======
<div align="center">
  
# Gradescope Auto Submitter for QUT

This tool automates the process of submitting assignments to Gradescope via the QUT SSO login system. It was built to streamline a repetitive and manual process that many QUT students face every week: zipping their files, logging into Gradescope, navigating to the correct course and assignment, uploading their submission, and confirming it. And then repeating this process 1 million times.
</br>  
</br>
I built this script to save time, reduce mistakes, and make assignment submissions feel as smooth as pushing to a Git repo and never leave my IDE. It’s especially useful when working on frequent tutorials, labs, or auto-graded assignments that require consistent resubmissions (could also just be a skill issue on my end).
</br>  
</br>
*Currently this script is only working with assignments that have a previous existing submission on Gradescope.*

</div>


https://github.com/user-attachments/assets/d26a9b0a-efd2-47ca-a623-808727735b32

## What It Does

- Bundles your project files into a zip archive
- Logs into Gradescope using QUT SSO
- Navigates to your course and assignment automatically
- Uploads your zip file using the file input
- Prints a clear submission receipt in the terminal with timestamp and file info
- Automatically polls for and displays your grade (once available) in the terminal
- Leaves the browser open for visual confirmation

## Setup

### 1. Install Playwright

```bash
pip install playwright
playwright install
```

### 2. Download this repo

Download this repo and then grab `gradescope.py` and `gradescope.json` and paste it into the root directory where everything you want to submit exists.

Your working directory should look like this:
```
root-dir/
├── gradescope.py
├── gradescope.json
├── the rest of your actual submission files and directories (e.g. src, include, etc.)
```

### 3. Modify `gradescope.json`

This config file is used to store your default submission settings, making it easy to run the script without passing arguments every time:

```json
{
  "username": "n12345678",
  "password": "yourpassword",
  "course": "cab201",
  "assignment": "t6q1",
  "file": "submission.zip",
  "bundle": ["*"]
}
```
#### Parameter Details
```username```:
Your QUT student number (e.g. "n1234567").
Used to log in via QUT’s Single Sign-On (SSO).

```password```:
Your QUT password.
Used with username for automated login. Be aware that this is stored in plain text unless additional security measures are implemented.

```course```:
The short name of the course to submit to (e.g. "CAB201").
The script searches for this string within course names shown on your Gradescope dashboard. It performs a case-insensitive partial match so don't worry if it's not the exact name, so long as what you enter is a substring of the course name on gradescope.

```assignment```:
The name or partial name of the assignment (e.g. "T6Q1" or "Assignment 2").
Used to find the matching assignment name on the course page. Similarly performs a partial match search for what you enter.

```file```:
The name of the zip file that will be submitted (e.g. "ihatecab202.zip").

```bundle```:
An array of glob-style file patterns (e.g. ["*.py"]) that determine which files are packaged into the zip file.
Used when creating the submission archive. Files like gradescope.py, gradescope.json, and the zip file itself are automatically excluded.

### ⚠️ Warning: Plaintext Passwords
This script reads your QUT password directly from `gradescope.json`, which is stored in plaintext. Use at your own risk. Do **not** upload your config json file to GitHub unless you remove your credentials.

## Usage

```bash
python gradescope.py submit
```

## Example Output

```
📦 Added: LinkedList.cs
📦 Added: Node.cs
📦 Added: Program.cs

✅ Created: submission.zip
[23:20:24.8769 🌐 Navigating to Gradescope login...
[23:20:28.6423 👤 QUT login detected. Entering credentials...
[23:20:30.6151 🔓 QUT login complete
[23:20:30.6152 📘 Searching for course...
[23:20:30.6601 ➡️ Found course: CAB201_24se2
[23:20:31.2912 📄 Searching for assignment...
[23:20:31.3119 ➡️ Found assignment: T6Q1: Linked List (Formative)
[23:20:31.9574 📤 Starting submission...
[23:20:32.0122 ⏳ Waiting for file input to appear...
[23:20:32.0176 📤 Uploading: submission.zip
[23:20:33.0454 📬 Clicking Upload...
[23:20:36.0987 ✅ File submitted successfully!

🧾 Submission Receipt:
✅ Submitted to "CAB201_24se2 > T6Q1: Linked List (Formative)"
🕒 Time: 11:20 PM, August 01
📁 File: submission.zip
[23:20:36.0998 🔍 Waiting for grade to appear...

[23:20:47.9675 🏆 Grade returned after 00:11s: 2.0 / 2.0
[23:20:47.9678 🕒 Leaving the browser open. Press Enter to exit.
```
## Troubleshooting
```"Could not find course/assignment matching..."```

Check your gradescope.json. The script matches based on a partial substring — make sure your course or assignment value exists somewhere in the full label on Gradescope.

```"Playwright timeout error when waiting for grade"```

Gradescope grading can take time. The script polls for about 2 minutes and you can modify this by changing max_attempts in the .py script

```"gradescope.py is not recognized as a command"```

Use ```python gradescope.py submit``` instead of relying on the OS to recognize the script directly.

#### Optional: .gitignore
If you're versioning your submissions with Git, you should ignore the sensitive and generated files:
```python
gradescope.json
submission.zip
```

### Notes

This script was built specifically for QUT’s instance of Gradescope (https://www.gradescope.com.au).

It is not affiliated with QUT or Gradescope.

You’re free to adapt it for other schools, submission types, or workflows.
>>>>>>> 467debcad1d99a2cdd6729e239f43d8a3de31cc0
