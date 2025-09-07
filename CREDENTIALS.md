# Credential Management - QUT Gradescope Auto Submitter

Complete guide to setting up and managing your QUT credentials securely.

## 🔐 Where are my credentials stored?

Your Gradescope login can be saved in a user-level file so it works across all your projects:

- **Windows:** `%LOCALAPPDATA%\qut_gradescope_autosubmitter\.env`
- **macOS/Linux:** `~/.qut-gradescope-autosubmitter/.env`

This means:
- ✅ Works across all your programming projects
- ✅ Won't accidentally get shared when you zip/upload projects
- ✅ Easy to delete when you're done with the class

Project-level `.env` files are also supported and will override the user-level values if present.

## 👤 Managing your credentials

### Interactive Setup (Recommended)

```bash
gradescope credentials
```

**Main Menu:**
1. **Manage saved credentials (.env, user-level)** - Recommended for persistent use
2. **Environment variables (session/system)** - Advanced users
3. **Exit**

**Saved Credentials Options:**
1. **Save/update credentials** - Enter/re-enter your QUT login
2. **Delete saved credentials** - Remove the .env file completely
3. **Back**

### What's a .env file?

Think of it like saving your Wi‑Fi password on your laptop — you enter it once, and your computer remembers it so you don't have to type it every time.

This tool can save your Gradescope username and password in a `.env` file so it can log you in automatically next time.

**Security Notes:**
- ⚠️ Anyone with access to your user account can read this file
- 💡 Consider OS keychain or environment variables for stronger security
- 🔒 Don't commit `.env` files to Git repositories

## 🔄 All Setup Methods

### 1. Interactive .env (Easiest)

```bash
gradescope credentials → 1 → 1
# Enter your QUT username and password when prompted
```

**Pros:** Easy setup, works everywhere, persistent
**Cons:** Stored in plaintext file

### 2. Submit-time Prompts

If no credentials are found, `gradescope submit` will prompt:

1. **Enter and save to .env** (recommended)
2. **Enter once for this run** (temporary)
3. **Cancel**

### 3. Environment Variables

**Session-only (temporary):**
```bash
# Windows PowerShell
$env:GRADESCOPE_USERNAME = "n12345678"
$env:GRADESCOPE_PASSWORD = "your_password"

# Linux/Mac
export GRADESCOPE_USERNAME="n12345678"
export GRADESCOPE_PASSWORD="your_password"
```

**Permanent system variables:**
```bash
# Windows PowerShell (permanent)
[Environment]::SetEnvironmentVariable("GRADESCOPE_USERNAME", "n12345678", "User")
[Environment]::SetEnvironmentVariable("GRADESCOPE_PASSWORD", "your_password", "User")
# Restart terminal after this

# Linux/Mac (permanent)
echo 'export GRADESCOPE_USERNAME="n12345678"' >> ~/.bashrc
echo 'export GRADESCOPE_PASSWORD="your_password"' >> ~/.bashrc
source ~/.bashrc
```

### 4. Project .env File

Create `.env` in your project directory:
```bash
GRADESCOPE_USERNAME=n12345678
GRADESCOPE_PASSWORD=your_password
```

**Remember:** Add `.env` to your `.gitignore`!

## 🔒 Security Comparison

| Method | Security Level | Convenience | Team Friendly |
|--------|---------------|-------------|---------------|
| User .env | ⭐⭐ | ⭐⭐⭐ | ⭐ |
| System env vars | ⭐⭐⭐ | ⭐⭐ | ⭐ |
| Session env vars | ⭐⭐ | ⭐ | ⭐ |
| Project .env | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| CLI flags | ⭐ | ⭐ | ⭐ |

**Most Secure:** OS keychain (not yet implemented) or system environment variables  
**Most Convenient:** User-level .env file  
**Best for Teams:** Project .env with proper `.gitignore`

## 🧹 Removing Credentials

### Delete User-level .env
```bash
gradescope credentials → 1 → 2
# OR manually:

# Windows
Remove-Item "$env:LOCALAPPDATA\qut_gradescope_autosubmitter\.env"

# macOS/Linux
rm ~/.qut-gradescope-autosubmitter/.env
```

### Clear Environment Variables
```bash
# Session variables
# Windows
Remove-Variable GRADESCOPE_USERNAME, GRADESCOPE_PASSWORD

# Linux/Mac
unset GRADESCOPE_USERNAME GRADESCOPE_PASSWORD

# System variables
# Windows
setx GRADESCOPE_USERNAME ""
setx GRADESCOPE_PASSWORD ""

# Linux/Mac: Remove from ~/.bashrc, ~/.zshrc, etc.
```

### Delete Project .env
```bash
# Windows
Remove-Item .env

# macOS/Linux  
rm .env
```

## 🎯 Credential Priority Order

The tool checks credentials in this order:

1. **CLI flags** (`--username`, `--password`)
2. **Environment variables** (`GRADESCOPE_USERNAME`, `GRADESCOPE_PASSWORD`)
3. **User-level .env** (`~/.qut-gradescope-autosubmitter/.env`)
4. **Project .env** (`./.env`)
5. **Interactive prompt** (if none found)

## 🔧 Troubleshooting

### Password Issues

**Control characters when pasting:**
- Use right-click paste instead of Ctrl+V on Windows
- The tool automatically detects and sanitizes common paste issues
- If password looks wrong, use `gradescope credentials → 1 → 1` to re-enter

**Password not working:**
- Check for typos using `gradescope credentials → 1 → 1`
- Verify your QUT login works on the QUT website
- Try `gradescope submit --fresh-login` to force new login

### File Permission Issues

**Windows:**
```powershell
# Check if .env file exists
Test-Path "$env:LOCALAPPDATA\qut_gradescope_autosubmitter\.env"

# View contents (be careful - shows password!)
Get-Content "$env:LOCALAPPDATA\qut_gradescope_autosubmitter\.env"
```

**macOS/Linux:**
```bash
# Check if .env file exists
ls -la ~/.qut-gradescope-autosubmitter/.env

# View contents (be careful - shows password!)
cat ~/.qut-gradescope-autosubmitter/.env
```

## 📖 Related Documentation

- [README.md](README.md) - Quick start guide
- [CLI_REFERENCE.md](CLI_REFERENCE.md) - Complete command reference
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Testing procedures
