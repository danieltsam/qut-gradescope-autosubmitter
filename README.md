<h1 align="center">QUT Gradescope Auto Submitter</h1>

<p align="center">
  <a href="https://pypi.org/project/qut-gradescope-autosubmitter/"><img src="https://img.shields.io/pypi/v/qut-gradescope-autosubmitter?label=PyPI" alt="PyPI"></a>
</p>

As a QUT student, I was tired of:

- Clicking through Gradescope 50+ times per assignment when trying to see if I met test cases
- Being forced to wait when I'm trying to get quick feedback on my work
- Losing focus context switching between code editor and browser
- Manual file compression, uploads and form submissions

This tool automates the submission process so you can focus on coding, not clicking.

https://github.com/user-attachments/assets/42f96ca3-e640-4c72-8ba7-c43932be0d79

## Install

**Recommended — pipx** (installs the CLI globally, separate from your project venv):

```bash
pipx install qut-gradescope-autosubmitter && playwright install chromium
```

If `playwright` isn't found after pipx, either `pip install playwright` once or use `pipx install --include-deps qut-gradescope-autosubmitter` so the Playwright CLI lands on your PATH.

Other options: `pip install qut-gradescope-autosubmitter && playwright install chromium`, or clone this repo and `pip install -e .`.

Run `gradescope doctor` if anything looks broken after install.

## Usage

From your **assignment repo** (where your code lives):

```bash
gradescope init          # creates gradescope.yml
gradescope login         # once — browser opens for QUT SSO + 2FA
gradescope submit        # zip, upload, wait for autograder (optional)
```

**What `submit` does:**

1. Reads `gradescope.yml` for course, assignment, and which files to include.
2. Builds a zip from tracked git files matching your `include` globs.
3. Opens Gradescope in Chromium (or runs headless if you already logged in).
4. Finds your course and assignment, uploads the zip, and handles resubmits.
5. If `notify_when_graded: true`, polls until a score appears in the terminal.

You run this whenever you want feedback — same loop as clicking through Gradescope yourself, minus the manual steps.

## Login & session (why not passwords?)

QUT SSO requires **2FA**, so the CLI doesn't ask for your password. That would mean storing credentials and trying to script around 2FA — brittle and not worth it for a coursework helper.

Instead, **`gradescope login`** opens a normal browser window. You sign in and complete 2FA yourself. The tool saves a Chromium profile under `~/.cache/qut_gradescope` (cookies + local storage — like staying logged in on Chrome).

After that, **`gradescope submit`** reuses that session. No password in config, no secrets in env vars. If the session expires, run `login` again.

With a saved session you can set `headless: true` in config so submit runs without a visible window.

## Config (`gradescope.yml`)

```yaml
course: "cab201"           # partial match on Gradescope course name
assignment: "t6q1"         # partial match on assignment name
zip_name: submission.zip
include:
  - "*.py"
notify_when_graded: true   # wait for autograder score after upload
headless: false
```

In a git repo, only files from `git ls-files` are considered (respects `.gitignore`).

## Git hooks (optional)

To submit on every commit from your assignment repo:

```bash
gradescope hooks --install post-commit --quick
```

Remove with `rm .git/hooks/post-commit`. Install hooks **per repo**, not in this tool repo.

## Requirements

Python 3.8+, QUT Gradescope access, Chromium (via Playwright).

## Changelog

### 2.0.1

- `gradescope login` closes the browser automatically after SSO (no Enter prompt).

### 2.0.0

- Browser session auth (`login` / saved profile) — 2FA handled by you once in the browser.
- Slimmer CLI, orange Rich output, `include` globs, git-based bundling.
- Pytest CI; removed GitHub Action submit workflows (use local submit or hooks).

### 1.0.5

- README: QUT 2FA called out explicitly.
- Removed scheduled-submit workflow.

### 1.0.4

- Python 3.8 compatibility fix (`Optional` typing in credentials helper).

### 1.0.3

- Clearer errors for wrong username/password.
- Headless/SSH: link to submission page when the browser can't stay open.

### 1.0.2

- Maintenance release (tagged on GitHub).

### 1.0.1

- First public PyPI release.
- Rich CLI, Playwright automation, `gradescope.yml`, git hooks, optional GitHub Action submit.

### Pre-1.0.1

Early TestPyPI builds before the stable 1.0 line.
