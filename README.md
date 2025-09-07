# QUT Gradescope Auto Submitter

<div align="center">
  
[![TestPyPI version](https://badge.fury.io/py/qut-gradescope-autosubmitter.svg)](https://test.pypi.org/project/qut-gradescope-autosubmitter/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**🎨 Beautiful CLI tool for QUT Gradescope submissions**

Secure • Fast • Customizable • CI/CD Ready

[Installation](#installation) • [Quick Start](#quick-start) • [How It Works](#how-it-works) • [Documentation](#documentation)

> **💡 Why I built this:** As a QUT student, I was frustrated with the repetitive click-heavy Gradescope submission process. I enjoy CLI tools and automation, so I built this to streamline my workflow and make submissions as simple as `gradescope submit`.

</div>

---

## ✨ Features

### 🎨 **Beautiful Interface**
- **Rich Terminal UI**: Gorgeous panels, tables, and progress indicators
- **Custom Colors**: Personalize your experience with dynamic color themes
- **Smart Progress**: Real-time step tracking with timestamps and timing
- **Responsive Design**: Clean output that adapts to your terminal

### 🔐 **Security & Credentials**
- **Multiple Options**: Environment variables, .env files, or interactive prompts
- **User-Level Storage**: Credentials work across all your projects
- **Session Persistence**: Stay logged in between submissions
- **Manual Login Mode**: Maximum security with browser-based authentication

### ⚡ **Automation & Performance**
- **Smart Bundling**: Automatic file detection with .gitignore support
- **Fuzzy Matching**: Find courses and assignments with partial names
- **Grade Monitoring**: Wait for and display grades automatically
- **CI/CD Ready**: Perfect for GitHub Actions and automation

### 🛠️ **Developer Experience**
- **Interactive Setup**: Guided configuration and credential management
- **Rich Help System**: Beautiful help pages and command documentation
- **System Diagnostics**: Built-in doctor command for troubleshooting
- **Cross-Platform**: Windows, macOS, Linux support

## ⚠️ Important Limitations

If QUT or Gradescope change their SSO/UI, this tool breaks :)

**Assignment Support:**
- **Automatic detection**: Works with any assignment without manual setup
- **Universal compatibility**: Handles all submission interfaces seamlessly

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
> pip install playwright pyyaml python-dotenv click rich
> pip install -i https://test.pypi.org/simple/ qut-gradescope-autosubmitter
> playwright install chromium
> ```

### Platform Notes

**Windows:** If you get permission errors, try `pip install --user -i https://test.pypi.org/simple/ qut-gradescope-autosubmitter`

**Linux/Mac:** You may need `python3` and `pip3` instead of `python` and `pip`

## ⚡ Quick Start

### 1. System Check & Setup

```bash
# Check system requirements and see the beautiful interface
gradescope doctor

# Create config file with guided setup
gradescope init

# Customize your UI interface colors (optional but fun!)
gradescope ui
```

### 2. Set Credentials

**🎨 Interactive Setup (Recommended)**
```bash
gradescope credentials
# Navigate the beautiful menus:
# 1. Manage .env credentials → Save/update credentials
# 2. Environment variables → See copyable commands
# 3. View current status → Check what's configured
```

The credentials system offers multiple options:
- **User-level .env file**: Works across all projects
- **Project-level .env file**: Project-specific credentials  
- **Environment variables**: Session-based or permanent
- **Interactive prompts**: Enter credentials when needed

> **📖 Complete Guide:** See [CREDENTIALS.md](CREDENTIALS.md) for detailed setup, security notes, and troubleshooting.

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

### 4. Submit & Enjoy

```bash
gradescope submit
```





## ⚙️ How It Works

This tool automates the manual Gradescope submission process using browser automation:

**🔍 What the tool does:**
1. **🔐 Logs into QUT SSO** - Handles university single sign-on automatically
2. **🎯 Navigates Gradescope** - Finds your course and assignment using smart matching
3. **📦 Bundles your files** - Creates a zip from your project files (respects .gitignore)
4. **⚡ Submits automatically** - Handles both new submissions and resubmissions seamlessly
5. **📊 Monitors grading** - Waits for and displays your grade when ready

**🎭 What Playwright does:**
- **Browser automation framework** - Controls a real Chromium browser programmatically
- **Cross-platform** - Works identically on Windows, macOS, and Linux
- **Reliable** - Handles dynamic web content, JavaScript, and complex interactions
- **Headless capable** - Can run invisibly in the background or show the browser

**🔒 Security approach:**
- **No credential storage** in the tool itself - uses your system's environment variables or local .env files
- **Session persistence** - Remembers your login between submissions (like staying logged in on a website)
- **Local execution** - Everything runs on your machine, not on external servers

This eliminates the repetitive clicking through Gradescope's interface while maintaining the same security as manual submission.

## 📋 CLI Commands

The tool features a beautiful, consistent interface across all commands:

| Command | Description | Features |
|---------|-------------|----------|
| `gradescope submit` | Submit to Gradescope | Rich progress, live grade monitoring |
| `gradescope init` | Create config file | Interactive setup, validation |
| `gradescope validate` | Check configuration | Detailed status tables |
| `gradescope credentials` | Manage credentials | Multi-level menus, secure storage |
| `gradescope doctor` | System diagnostics | Comprehensive health checks |
| `gradescope ui` | Customize interface | Live color preview, settings |
| `gradescope --help` | Show help | Beautiful panels and tables |
| `gradescope --version` | Show version | Professional version display |

> **📖 Complete Reference:** See [CLI_REFERENCE.md](CLI_REFERENCE.md) for all commands, options, and examples.  
> **💡 Quick Help:** Use `gradescope --help` or `gradescope [command] --help` for command details.

## 🔐 Credential Management

### Easy Interactive Setup

The credentials system provides a beautiful, guided experience:

```bash
gradescope credentials
```

**Main Menu Options:**
1. **Manage .env credentials** - Save to user-level .env file (recommended)
2. **Environment variables** - View copyable commands for your platform  
3. **Exit** - Return to terminal

**Environment Variables Submenu:**
1. **How to set** - Platform-specific commands you can copy
2. **How to delete** - Removal commands for cleanup
3. **View current** - See what's currently configured

### Supported Storage Methods

**Option A: User-Level .env File (Recommended)**
- Works across all your projects
- Secure local storage
- Easy to manage and delete

**Option B: Environment Variables**

*Session Variables (Temporary):*
```bash
# Windows PowerShell
$env:GRADESCOPE_USERNAME='n12345678'
$env:GRADESCOPE_PASSWORD='your_password'

# Linux/Mac
export GRADESCOPE_USERNAME='n12345678'
export GRADESCOPE_PASSWORD='your_password'
```

*Permanent Variables:*
```bash
# Windows PowerShell (Permanent)
[Environment]::SetEnvironmentVariable("GRADESCOPE_USERNAME", "n12345678", "User")
[Environment]::SetEnvironmentVariable("GRADESCOPE_PASSWORD", "your_password", "User")

# Linux/Mac (add to ~/.bashrc, ~/.zshrc, or ~/.profile)
echo 'export GRADESCOPE_USERNAME="n12345678"' >> ~/.bashrc
echo 'export GRADESCOPE_PASSWORD="your_password"' >> ~/.bashrc
```

**Option C: Project-Level .env File**
```bash
# Create .env file in project directory
GRADESCOPE_USERNAME=n12345678
GRADESCOPE_PASSWORD=your_password
```

### Storage Locations

**User-Level .env Files:**
- **Windows:** `%LOCALAPPDATA%\qut_gradescope_autosubmitter\.env`
- **macOS/Linux:** `~/.qut-gradescope-autosubmitter/.env`

**Priority Order:**
1. Project-level .env file (if present)
2. User-level .env file
3. Environment variables
4. Interactive prompt

> **📖 Complete Guide:** See [CREDENTIALS.md](CREDENTIALS.md) for security best practices, troubleshooting, and advanced configuration.

## 📊 Submit Options & Progress

### Command Options

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

### Beautiful Progress Display

The tool shows detailed progress with timestamps and colors:

```
[15:42:31.45] ✓ Created: submission.zip (25 files, 0.1 MB)
[15:42:31.89] ✓ Persistent context created with user data directory
> [1/5] Checking login status...
[15:42:33.12] ✓ Using existing session
    → Completed in 1.8s
> [2/5] Finding course 'cab201'...
[15:42:33.35] ✓ Found course: CAB201_24se2
    → Completed in 0.2s
> [3/5] Finding assignment 't6q1'...
[15:42:33.78] ✓ Found assignment: T6Q1: Linked List (Formative)
    → Completed in 0.4s
> [4/5] Submitting file...
[15:42:34.12] INFO Resubmission detected - clicking resubmit button...
[15:42:34.45] INFO Uploading: submission.zip
[15:42:35.23] INFO Clicking Upload...
    → Completed in 1.8s
> [5/5] Waiting for grade...
Grade returned after 0:42: 15.0 / 15.0 (100%)
[15:42:38.67] ✓ Submission completed! (Total: 7.2s)
```

## 🔒 Security & Session Management

**Default Mode (Recommended):**
- Saves login session for efficiency
- Subsequent submissions are faster  
- Session expires automatically when needed
- Beautiful progress indicators show session status

**Advanced Security Options:**
```bash
gradescope submit --manual-login    # Maximum security - browser login
gradescope submit --fresh-login     # Force new login (troubleshooting)
gradescope cleanup                  # Clear saved sessions
```

## 🎨 Customization

### Color Themes

Personalize your experience with custom colors:

```bash
gradescope ui
```

Choose from:
- **Primary Color**: Main interface elements and highlights
- **Success Color**: Completion indicators and positive messages  
- **Warning Color**: Alerts and important notices
- **Error Color**: Error messages and critical alerts

Pick from 17+ colors including cyan, orange, purple, bright variants, and more!

### UI Settings

Fine-tune your experience:
- **Timestamps**: Show/hide detailed timing information
- **Animations**: Enable/disable progress animations
- **Compact Mode**: Reduce visual clutter
- **Step Timings**: Display individual step completion times

## 🤖 CI/CD Automation

Automate submissions with GitHub Actions, Git hooks, or other CI/CD systems.

> **📖 Setup Guide:** See [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md) for complete automation setup instructions.

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

# Submit specific files with custom colors
gradescope submit -b "*.java" -b "*.xml" --file java-submission.zip

# Quick submission with credentials
gradescope submit -u n12345678 -p password --headless
```

## 🚨 Troubleshooting

### Interactive Diagnostics

```bash
# Beautiful system health check
gradescope doctor

# Validate configuration with detailed feedback
gradescope validate

# Check credentials status
gradescope credentials
```

### Common Issues

**"Config file not found"**
```bash
gradescope init  # Interactive setup with validation
```

**"Course/Assignment not found"**
- Use partial matching: `cab201` matches `CAB201_24se2`
- Check exact names on Gradescope website
- Try shorter search terms

**"Credentials not found"**
```bash
gradescope credentials  # Interactive credential setup
```

**"Browser timeout"**
```bash
gradescope submit --headless  # Try headless mode
```

**Visual Issues or Color Problems**
```bash
gradescope ui  # Reset colors to defaults or customize
```

### Debug Mode

```bash
# Check system status with beautiful output
gradescope doctor

# Validate configuration with detailed tables
gradescope validate

# Test with minimal output
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
- Rich (automatically installed)

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

---

## 🎨 What's New

This version features a complete UI overhaul with:

- **🎨 Rich Terminal Interface**: Beautiful panels, tables, and progress bars
- **🌈 Custom Colors**: 17+ color options for personalizing your experience
- **📊 Smart Progress Tracking**: Real-time step indicators with timestamps
- **🔧 Interactive Menus**: Guided setup and configuration
- **⚡ Enhanced Performance**: Optimized step tracking and reduced duplication
- **🔐 Improved Security**: Multiple credential storage options with guided setup
- **📋 Better Help System**: Professional help pages and command documentation

Transform your Gradescope submission experience from mundane to beautiful! 🚀