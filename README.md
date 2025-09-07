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

### 🎨 **Rich Terminal UI**
Built with [Rich](https://github.com/Textualize/rich) for a beautiful command-line experience inspired by modern CLI tools like Claude Code. Features panels, tables, progress indicators, and custom color themes that make terminal work enjoyable and pretty!

### 🔐 **Flexible Credential Management**
- **Multiple Options**: Environment variables, .env files, or interactive prompts
- **User-Level Storage**: Credentials work across all your projects
- **Session Persistence**: Stay logged in between submissions
- **Manual Login Mode**: Maximum security with browser-based authentication

### ⚡ **Smart Automation**
- **Intelligent Bundling**: Automatic file detection with .gitignore support
- **Fuzzy Matching**: Find courses and assignments so long as they partially match the name on Gradescope
- **Grade Monitoring**: Wait for and display grades automatically
- **CI/CD Ready**: Can be used as a Git Hook locally or Github Action

### 🛠️ **Developer Experience**
- **Interactive Setup**: Guided configuration and credential management
- **Professional Help System**: Beautiful help pages and command documentation
- **System Diagnostics**: Built-in doctor command for troubleshooting
- **Cross-Platform**: Windows, macOS, Linux support

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
- **Headless capable** - Can run invisibly in the background or show the browser (because it's always fun to watch an automated browser)

**🔒 Security approach:**
- **No credential storage** in the tool itself - uses your system's environment variables or local .env files
- **Session persistence** - Remembers your login between submissions (like staying logged in on a website)
- **Local execution** - Everything runs on your machine, not on external servers

This eliminates the repetitive clicking through Gradescope's interface while maintaining the same security as manual submission.

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

## 🎨 Interface & Customization

### Rich Terminal UI

The interface uses the [Rich](https://github.com/Textualize/rich) library to provide a beautiful, modern CLI experience with:
- **Gorgeous panels and tables** for structured information
- **Live progress tracking** with real-time step indicators
- **Dynamic color themes** with 17+ customizable colors
- **Professional help system** with beautifully formatted documentation

### Color Customization

```bash
gradescope ui
```

Personalize your experience with:
- **Primary Color**: Main interface elements and highlights
- **Success Color**: Completion indicators and positive messages  
- **Warning Color**: Alerts and important notices
- **Error Color**: Error messages and critical alerts

### UI Settings

Fine-tune your experience:
- **Timestamps**: Show/hide detailed timing information
- **Animations**: Enable/disable progress animations
- **Compact Mode**: Reduce visual clutter
- **Step Timings**: Display individual step completion times

## 🤖 Automation

### Git Hooks (Local Automation)

Automatically submit on every commit:

```bash
gradescope hooks
```

**Hook Options:**
- **Full Hooks**: Submit and wait for grade feedback
- **Quick Hooks**: Submit without waiting for grades
- **Pre-commit**: Submit before each commit
- **Post-commit**: Submit after each commit

**Example workflow:**
```bash
git add .
git commit -m "Fix algorithm implementation"
# → Automatic submission to Gradescope
# → Grade feedback in terminal (full mode)
```

### GitHub Actions (Cloud Automation)

CI/CD ready with comprehensive GitHub Actions support for automated cloud submissions, scheduled runs, and team collaboration.

> **📖 Complete Setup Guide:** See [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md) for Git hooks and GitHub Actions automation.

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
| `gradescope hooks` | Setup Git automation | Interactive hook management |
| `gradescope --help` | Show help | Beautiful panels and tables |
| `gradescope --version` | Show version | Professional version display |

> **📖 Complete Reference:** See [CLI_REFERENCE.md](CLI_REFERENCE.md) for all commands, options, examples, and project configurations.  
> **💡 Quick Help:** Use `gradescope --help` or `gradescope [command] --help` for command details.

## 🔐 Security & Session Management

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

## 📖 Documentation

- **[CLI_REFERENCE.md](CLI_REFERENCE.md)** - Complete command reference, options, and project examples
- **[CREDENTIALS.md](CREDENTIALS.md)** - Credential setup, security best practices, and troubleshooting
- **[GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md)** - Git hooks and GitHub Actions automation setup

## 📝 Requirements

- Python 3.8+
- Playwright (automatically installed)
- PyYAML (automatically installed)
- Click (automatically installed)
- Rich (automatically installed)

## ⚠️ Important Disclaimers

**Assignment Support:**
- **Automatic detection**: Works with any assignment without manual setup
- **Universal compatibility**: Handles all submission interfaces seamlessly
- **Limitation**: If QUT or Gradescope change their SSO/UI, this tool breaks

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

Made with ❤️ for QUT students who love efficient workflows and beautiful CLIs.