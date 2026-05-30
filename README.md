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

**PyPI:**

```bash
pip install qut-gradescope-autosubmitter
playwright install chromium
```

**pipx** (isolated CLI, no project venv):

```bash
pipx install qut-gradescope-autosubmitter
playwright install chromium
```

**From source:**

```bash
git clone https://github.com/danieltsam/qut-gradescope-autosubmitter.git
cd qut-gradescope-autosubmitter
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
playwright install chromium
```

After any install, run `gradescope doctor` if something looks off.

## Use

```bash
gradescope init
gradescope login
gradescope submit
```

`bundle` (zip only), `logout`, `validate`, `doctor`, `hooks` are there when you need them.

## Why browser login (not passwords in the CLI)

QUT SSO requires **2FA**. Automating username/password breaks often (selector changes, extra prompts) and means storing credentials on disk — which most people don't want for a coursework helper.

Instead you run **`gradescope login` once**: a real browser window, you sign in and complete 2FA yourself. We save the session under `~/.cache/qut_gradescope` (cookies/profile, same idea as staying logged in on Chrome). Later **`gradescope submit`** reuses that — no password prompts, no secrets in `gradescope.yml`.

Headless submit only works if that session already exists; otherwise the CLI tells you to log in first.

## Config (`gradescope.yml`)

```yaml
course: "cab201"
assignment: "t6q1"
zip_name: submission.zip
include:
  - "*.py"
notify_when_graded: true
headless: false
```

`course` / `assignment` are partial matches on Gradescope. `include` is globs (`bundle` still works for older configs). In a git repo, files come from `git ls-files` so ignored junk doesn't end up in the zip.

## Automation

**Git hooks** (on your machine — session stays local):

```bash
gradescope hooks --install pre-commit --quick
```

**GitHub Actions** in this repo only runs tests on push/PR. Cloud auto-submit workflows were removed: exporting a browser session into CI was fragile and fought 2FA. Hooks or a local `gradescope submit` are the intended loop.

## Publishing to PyPI

Releases use [Trusted Publishing](https://docs.pypi.org/trusted-publishers/) via `.github/workflows/python-publish.yml`:

1. Bump `version` in `pyproject.toml` (must match the GitHub release tag, e.g. `v2.0.0`).
2. On GitHub: **Releases → Draft a new release** → tag `v2.0.0` → publish.
3. The workflow builds the wheel/sdist and uploads to PyPI.

Manual publish (if you prefer): `python -m build` then `twine upload dist/*`.

## Requirements

Python 3.8+, QUT Gradescope access, Chromium (via Playwright).

## Changelog

### 2.0.0

- **Auth:** `gradescope login` / `logout` with a saved browser profile (QUT 2FA handled by you in the browser once). Removed password prompts, `credentials` command, and username/password CLI/env options.
- **CLI:** Slimmer surface; orange Rich output; fixed step markup that leaked `/cyan`.
- **Config:** `include` globs; clearer `gradescope init` template.
- **Bundling:** `git ls-files` when in a repo; skips deleted paths still in the index.
- **CI:** Pytest on push/PR; removed GitHub Action submit workflows.
- **Tests:** `pytest` suite under `tests/`.

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
- `python-publish.yml` for release-triggered uploads.
- Rich-based CLI, Playwright automation, `gradescope.yml` config, git hooks, optional GitHub Action submit.

### Pre-1.0.1

Early development on TestPyPI (`1.0.x` / `1.1.x` dev versions): core CLI, bundling, and Gradescope automation before the stable 1.0 line.
