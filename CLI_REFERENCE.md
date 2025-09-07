# CLI Reference - QUT Gradescope Auto Submitter

Complete reference for all CLI commands, options, and advanced configuration.

## 📋 All Commands

| Command | Description | Example |
|---------|-------------|---------|
| `gradescope submit` | Submit to Gradescope | `gradescope submit --headless` |
| `gradescope init` | Create config file | `gradescope init --path my-config.yml` |
| `gradescope validate` | Check configuration | `gradescope validate` |
| `gradescope credentials` | Manage credentials | `gradescope credentials` |
| `gradescope doctor` | System diagnostics | `gradescope doctor` |
| `gradescope cleanup` | Clear saved sessions | `gradescope cleanup` |

> **💡 Tip:** Use `gradescope --help` or `gradescope [command] --help` for detailed information about any command and its options.

## 🚀 Submit Command Options

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

### Examples

```bash
# Basic submission
gradescope submit

# Override config settings
gradescope submit --course cab202 --assignment "Lab 5" --headless

# Submit specific files
gradescope submit -b "*.java" -b "*.xml" --file java-submission.zip

# Quick submission with credentials (not recommended)
gradescope submit -u n12345678 -p password --headless
```

## 🔧 Configuration Commands

### gradescope init

```bash
gradescope init [OPTIONS]

Options:
  -p, --path TEXT  Config file path (default: gradescope.yml)
```

Creates an example configuration file with all available settings.

### gradescope validate

```bash
gradescope validate [OPTIONS]

Options:
  --config TEXT  Path to config file
```

Validates configuration file and shows current settings including credential status.

### gradescope doctor

```bash
gradescope doctor
```

Checks system requirements:
- Python version
- Playwright installation
- Browser availability
- Config file status
- Credential status

## 🔐 Credential Management

### gradescope credentials

Interactive credential management with submenus:

**Main Menu:**
1. Manage saved credentials (.env, user-level)
2. Environment variables (session/system)
3. Exit

**Saved Credentials Submenu:**
1. Save/update credentials (user-level .env)
2. Delete saved credentials (user-level .env)
3. Back

**Environment Variables Submenu:**
1. Show setup commands (session/system)
2. Show clear commands
3. Back

## 🧹 Maintenance Commands

### gradescope cleanup

```bash
gradescope cleanup
```

Clears saved browser session data. Use when:
- Switching between QUT accounts
- Session corruption issues
- Login problems

## 🔒 Security Options

### Session Management Modes

**Default (Recommended):**
- Saves login session for efficiency
- Subsequent submissions are faster
- Session expires automatically when needed

**Fresh Login Mode:**
```bash
gradescope submit --fresh-login
# OR set in config:
always_fresh_login: true
```
- Forces new login every time
- Trades convenience for session isolation
- Useful for troubleshooting login issues

**Manual Login Mode:**
```bash
gradescope submit --manual-login
# OR set in config:
manual_login: true
```
- Opens browser for manual login
- Maximum security - tool never handles credentials
- Forces fresh login (overrides session persistence)

### Rate Limiting Considerations

- **Fresh Login** and **Manual Login** create new SSO requests
- Frequent use may trigger QUT SSO rate limiting
- **Recommended:** Use default session persistence for regular use

## 📁 File Bundling

### Bundle Patterns

```yaml
# YAML config examples
bundle:
  - "*"                 # Everything (respects .gitignore)
  - "*.py"              # All Python files
  - "*.cpp"             # All C++ files  
  - "*.h"               # All header files
  - "src/**/*"          # Everything in src directory
  - "!tests/**"         # Exclude tests directory
```

### CLI Bundle Examples

```bash
# Multiple patterns
gradescope submit -b "*.py" -b "*.txt" -b "requirements.txt"

# Complex patterns
gradescope submit -b "src/**/*.java" -b "*.xml" -b "README.md"
```

### Automatically Excluded

- `gradescope.py`, `gradescope.json`, `gradescope.yml`
- Hidden files (starting with `.`)
- `__pycache__`, `node_modules`
- The output zip file itself

## 🌍 Environment Variables

All config options can be overridden with environment variables using `GRADESCOPE_` prefix:

```bash
# Linux/Mac
export GRADESCOPE_USERNAME="n12345678"
export GRADESCOPE_PASSWORD="your_password"
export GRADESCOPE_COURSE="cab201"
export GRADESCOPE_ASSIGNMENT="t6q1"
export GRADESCOPE_BUNDLE="*.py,*.cpp,*.h"
export GRADESCOPE_HEADLESS="true"
export GRADESCOPE_NOTIFY_WHEN_GRADED="false"

# Windows PowerShell
$env:GRADESCOPE_USERNAME = "n12345678"
$env:GRADESCOPE_PASSWORD = "your_password"
$env:GRADESCOPE_COURSE = "cab201"
$env:GRADESCOPE_ASSIGNMENT = "t6q1"
$env:GRADESCOPE_BUNDLE = "*.py,*.cpp,*.h"
$env:GRADESCOPE_HEADLESS = "true"
$env:GRADESCOPE_NOTIFY_WHEN_GRADED = "false"
```

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

**"Assignment submission failed"**
- Try refreshing the page and running again
- Check internet connection
- Verify assignment is still accepting submissions

**"Browser timeout"**
```bash
gradescope submit --headless  # Try headless mode
```

**"Credentials not found"**
```bash
gradescope credentials  # Set up credentials interactively
```

**"Session expired/login failed"**
- Use `gradescope cleanup` to clear sessions
- Try `--fresh-login` flag
- Check credentials with `gradescope doctor`

### Debug Mode

```bash
# Check system status
gradescope doctor

# Validate configuration  
gradescope validate

# Test with minimal output
gradescope submit --headless --no-grade-wait
```

### Platform-Specific Issues

**Windows:**
- Use right-click paste for passwords if Ctrl+V doesn't work
- File paths use backslashes automatically

**macOS/Linux:**
- May need `python3` and `pip3` instead of `python` and `pip`
- Check file permissions for config files

## 📖 More Information

- [README.md](README.md) - Quick start and installation
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Comprehensive testing procedures
- [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md) - CI/CD automation setup
