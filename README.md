<div align="center">

# QUT Gradescope Auto Submitter

One command to submit assignments to Gradescope. No more repetitive clicking.
</div>


---

https://github.com/user-attachments/assets/42f96ca3-e640-4c72-8ba7-c43932be0d79

---

## Why This Exists

As a QUT student, I was tired of:
- Clicking through Gradescope 50+ times per assignment when trying to see if I met test cases
- Being forced to wait when I'm trying to get quick feedback on my work
- Losing focus context switching between code editor and browser
- Manual file compression, uploads and form submissions

This tool automates the entire submission process so you can focus on coding, not clicking.

## ⚡ Quick Start

```bash
# Install
pip install qut-gradescope-autosubmitter && playwright install chromium
```
```bash
# One-time setup
gradescope init        # Create config file
gradescope credentials # Save QUT login

# Daily usage
gradescope submit      # Submit current assignment
```

That's it. No more manual submissions.

*Or use it with your existing repository as a [Github Action](https://github.com/marketplace/actions/qut-gradescope-autosubmission)* 😊

> To access the gradescope command in any directory on your machine, you may have to add the tool to your PATH. The installation places the 'gradescope' command in your user's local bin directory.

> **QUT 2FA requirement**
> QUT now enforces 2FA on first login. On your **first** use, `gradescope` will open a browser and you’ll need to complete QUT SSO + 2FA manually. After that, Playwright stores a session so most submissions won’t need re-auth, but QUT may force re-login (and 2FA) more frequently than before.

## 🔄 How It Works

1. **🔐 Authenticates with QUT SSO** - Handles university login automatically (using Playwright)
2. **🎯 Navigates to Gradescope** - Finds your course and assignment using smart matching
3. **📦 Bundles your files** - Creates submission zip (respects .gitignore)
4. **⬆️ Submits automatically** - Handles uploads and form submission
5. **📊 Shows your grade** - Displays results when available

Everything runs locally using browser automation. No data leaves your machine except for the normal submission to Gradescope.

## ✨ Key Features

### 🎨 Beautiful Terminal Interface
Modern CLI built with Rich - panels, progress bars, and custom themes that make terminal work enjoyable.

### 🔐 Flexible Authentication
- **Session persistence** - Stay logged in between submissions (faster)
- **Multiple credential options** - Environment variables, .env files, or interactive prompts
- **Manual login mode** - Browser-based authentication for maximum security

### 🤖 Smart Automation
- **Fuzzy matching** - Finds courses/assignments even with partial names
- **Automatic file detection** - Bundles relevant files intelligently
- **Git integration** - Optional hooks for submit-on-commit workflows
- **CI/CD ready** - GitHub Actions support for automated submissions

### 🛠️ Developer Experience
- **Cross-platform** - Windows, macOS, Linux support
- **Rich help system** - Beautiful documentation and error messages
- **System diagnostics** - Built-in troubleshooting tools
- **Customizable UI** - Adjust colors and behavior to your preference

## ⚙️ Basic Configuration

Create `gradescope.yml` in your project:
```yaml
# Required: Course and assignment details 
course: cab201              # Course code (must partially match Gradescope course name)
assignment: t6q1            # Assignment name (must partially match Gradescope assignment name)

# Optional: Submission settings
zip_name: submission.zip    # Name of the zip file to create and submit
bundle:                     # File patterns to include in submission
  - "*"                    # Everything (respects .gitignore)
  # - "*.py"               # All Python files
  # - "*.cpp"              # All C++ files
  # - "*.h"                # All header files
  # - "src/**/*"           # Everything in src directory

# Optional: Behaviour settings
notify_when_graded: true    # Wait for and display grade (default: true)
headless: false             # Run browser in background (default: false)
always_fresh_login: false   # Always login fresh
manual_login: false         # Open browser for manual login 
no_session_save: false      # Don't save credentials to session env vars
```

## 🔗 Automation Options

**🪝 Git Hooks** (submit to Gradescope before/after every commit):
```bash
gradescope hooks  # Interactive setup
```

**🤖 GitHub Actions** (cloud automation):
[View on Github Marketplace](https://github.com/marketplace/actions/qut-gradescope-autosubmission)

## 📚 Documentation

- **[Command Reference](CLI_REFERENCE.md)** - Complete command guide with examples
- **[Credential Management](CREDENTIALS.md)** - Security options and setup

## ⚠️ Important Notes

**Current Status:**
- ✅ **PyPI Release** - Available on PyPI
- ✅ **Stable Features** - Core submission functionality is reliable and tested

**Usage Responsibility:**
- This tool is provided "as-is" for legitimate academic use
- Users are responsible for complying with QUT academic integrity policies
- Avoid excessive submissions that may trigger rate limiting on QUT SSO
- Use session persistence (default) to minimize login requests

**Limitations:**
- Requires QUT SSO access and Gradescope course enrollment
- May break if QUT or Gradescope significantly change their interfaces
- Some specialized assignment types may not be supported

## 📋 Requirements

- Python 3.8+
- QUT student account with Gradescope access
- Internet connection for initial setup and submissions

## 🔧 Troubleshooting

**Common issues:**
- **Login failures:** Use `gradescope credentials` to reconfigure
- **Assignment not found:** Check course code and assignment name in config matches Gradescope
- **Browser issues:** Run `gradescope doctor` for system diagnostics

For detailed troubleshooting, see the [Command Reference](CLI_REFERENCE.md) or run `gradescope --help`.
