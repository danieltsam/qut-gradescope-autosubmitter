<div align="center">
  
# Gradescope Auto Submitter for QUT

This tool automates the process of submitting assignments to Gradescope via the QUT SSO login system. It was built to streamline a repetitive and manual process that many QUT students face every week: zipping their files, logging into Gradescope, navigating to the correct course and assignment, uploading their submission, and confirming it. And then repeating this process 1 million times.
</br>  
</br>
I built this script to save time, reduce mistakes, and make assignment submissions feel as smooth as pushing to a Git repo and never leave my IDE. It’s especially useful when working on frequent tutorials, labs, or auto-graded assignments that require consistent resubmissions (could also just be my skill issue).
</br>  
</br>
*Currently this script is only working with assignments that have a previous existing submission on Gradescope.*

</div>

## What It Does

- Bundles your project files into a zip archive
- Logs into Gradescope using QUT SSO
- Navigates to your course and assignment automatically
- Uploads your zip file using the file input
- Prints a clear submission receipt in the terminal with timestamp and file info
- Automatically polls for and displays your grade (once available) in the terminal
- Leaves the browser open for visual confirmation



https://github.com/user-attachments/assets/a1e421ff-8c5c-436c-9020-c45f2167e09d



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
