"""Core Gradescope submission functionality."""

import asyncio
import os
import subprocess
import zipfile
import time
import shutil
from fnmatch import fnmatch
from typing import List, Tuple, Optional
from pathlib import Path

from playwright.async_api import async_playwright
from .rich_console import (
    log_info, log_success, log_warning, log_error,
    log_bundle, create_spinner_progress,
    clear_live,
    StepTracker,
    print_banner,
    console,
)

CONFIG_FILENAMES = {
    "gradescope.yml", "gradescope.yaml", ".gradescope.yml", ".gradescope.yaml",
}


GRADESCOPE_SAML_URL = "https://www.gradescope.com.au/auth/saml/qut"
LOGIN_TIMEOUT_MS = 300_000


class SessionManager:
    """Persistent Chromium profile — cookies survive across `gradescope submit` runs."""

    def __init__(self):
        if os.name == 'nt':
            self.session_dir = Path.home() / "AppData" / "Local" / "qut_gradescope"
        else:
            self.session_dir = Path.home() / ".cache" / "qut_gradescope"

    def session_exists(self) -> bool:
        return self.session_dir.exists() and any(self.session_dir.iterdir())

    async def get_browser_context(self, headless: bool = True):
        """Launch Chromium with a persistent user-data directory (saved cookies)."""
        p = await async_playwright().start()
        self.session_dir.mkdir(parents=True, exist_ok=True)
        log_info(f"Session profile: {self.session_dir}")

        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(self.session_dir),
            headless=headless,
            args=['--disable-dev-shm-usage', '--no-sandbox'],
        )
        return context, p, None
    

    async def is_logged_in(self, context, page=None):
        """Check if we're still logged in by testing SAML redirect."""
        try:
            if page is None:
                page = await context.new_page()
                should_close_page = True
            else:
                should_close_page = False
            
            # Set up response listener to catch main page redirects only
            redirect_url = None
            def handle_response(response):
                nonlocal redirect_url
                # Only catch the main Gradescope page, not assets/JS/CSS
                if (response.url and 
                    response.url.startswith("https://www.gradescope.com.au") and 
                    not response.url.startswith("https://www.gradescope.com.au/assets") and
                    not response.url.startswith("https://www.gradescope.com.au/packs") and
                    not response.url.startswith("https://cdn.gradescope.com.au") and
                    "qut.edu.au" not in response.url and
                    "/auth/saml/" not in response.url):
                    redirect_url = response.url
            
            page.on('response', handle_response)
            
            # Navigate to QUT SAML endpoint
            await page.goto("https://www.gradescope.com.au/auth/saml/qut", timeout=15000)
            
            # Wait a short time for redirect to start
            await page.wait_for_timeout(1000)  # 1 second should be enough
            
            # Check current URL
            current_url = page.url
            
            if should_close_page:
                await page.close()
            
            # If we're on the main Gradescope page, we're logged in
            if (redirect_url and redirect_url.startswith("https://www.gradescope.com.au") and 
                not redirect_url.startswith("https://www.gradescope.com.au/auth")):
                return True, redirect_url
            elif (current_url.startswith("https://www.gradescope.com.au") and 
                  not current_url.startswith("https://www.gradescope.com.au/auth") and
                  "qut.edu.au" not in current_url):
                return True, current_url
            else:
                return False, None
                
        except Exception as e:
            if should_close_page and 'page' in locals():
                await page.close()
            return False, None
    
    def clear_session(self):
        """Remove saved browser profile (cookies, local storage)."""
        if self.session_dir.exists():
            shutil.rmtree(self.session_dir)
            log_success("Gradescope session cleared")

    cleanup_session = clear_session


async def wait_for_gradescope_login(page, steps: Optional[StepTracker] = None) -> None:
    """Open QUT SSO and wait until the user finishes login (including 2FA)."""
    log_info("Opening QUT SSO — complete login in the browser (including 2FA if prompted)...")
    await page.goto(GRADESCOPE_SAML_URL)

    log_warning("Waiting for you to finish login...")
    try:
        await page.wait_for_selector("a.courseBox", timeout=LOGIN_TIMEOUT_MS)
    except Exception:
        current_url = page.url
        if "qut.edu.au" in current_url:
            raise Exception(
                "Login timed out or failed. Complete QUT SSO and 2FA in the browser, then try again."
            ) from None
        raise Exception("Login timed out before Gradescope dashboard loaded.") from None

    if steps:
        steps.complete_step("Login complete — session saved")
    else:
        log_success("Login complete — session saved for future submissions")


class GradescopeSubmitter:
    """Main class for handling Gradescope submissions."""

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.session_manager = SessionManager()
    
    def _candidate_paths(self) -> List[str]:
        """Project files: from git when available, otherwise a directory walk."""
        if Path(".git").exists():
            result = subprocess.run(
                ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                capture_output=True,
                check=False,
            )
            if result.returncode == 0:
                return [p for p in result.stdout.decode().split("\0") if p]

        paths = []
        for root, dirs, files in os.walk("."):
            dirs[:] = [
                d for d in dirs
                if not d.startswith(".") and d not in ("__pycache__", "node_modules", ".venv", "venv")
            ]
            for name in files:
                if name.startswith("."):
                    continue
                rel = os.path.relpath(os.path.join(root, name), ".")
                paths.append(rel)
        return paths

    def create_zip(self, file_patterns: List[str], output_filename: str) -> None:
        """Create a zip from paths matching include globs."""
        skip = CONFIG_FILENAMES | {output_filename}

        matched_files = []
        for rel_path in self._candidate_paths():
            if rel_path in skip or any(rel_path.endswith(f"/{s}") for s in skip):
                continue
            if not Path(rel_path).is_file():
                continue  # git index can list deleted paths
            if any(fnmatch(rel_path, pat) for pat in file_patterns):
                matched_files.append((rel_path, rel_path))

        if not matched_files:
            raise ValueError(f"No files matched include patterns: {file_patterns}")

        with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
            for full_path, arcname in sorted(matched_files):
                zipf.write(full_path, arcname)

        size = os.path.getsize(output_filename)
        size_str = f"{size / 1024:.0f} KB" if size < 1024 * 1024 else f"{size / (1024 * 1024):.1f} MB"
        sample = [arc for _, arc in sorted(matched_files)]
        log_bundle(output_filename, len(matched_files), size_str, sample)

    async def submit_to_gradescope(
        self, 
        course: str, 
        assignment: str, 
        file: str, 
        notify_when_graded: bool = True
    ) -> Tuple[str, str]:
        """Submit a file to Gradescope."""
        # Initialize step tracker
        total_steps = 5 if notify_when_graded else 4
        steps = StepTracker(total_steps)
        try:
            return await self._submit_flow(
                steps, course, assignment, file, notify_when_graded, total_steps
            )
        except Exception:
            steps.stop()
            raise

    async def _submit_flow(
        self,
        steps: StepTracker,
        course: str,
        assignment: str,
        file: str,
        notify_when_graded: bool,
        total_steps: int,
    ) -> Tuple[str, str]:
        clear_live()
        context, playwright, _browser = await self.session_manager.get_browser_context(self.headless)
        clear_live()

        page = await context.new_page()

        steps.next_step("Checking saved session...")
        page.on('pageerror', lambda _error: None)
        page.on('requestfailed', lambda _request: None)

        is_logged_in, _ = await self.session_manager.is_logged_in(context, page)

        try:
            if is_logged_in:
                steps.complete_step("Using saved session")
                try:
                    await page.wait_for_selector("a.courseBox", timeout=5000)
                except Exception:
                    log_info("Refreshing Gradescope dashboard...")
                    await page.reload()
                    await page.wait_for_selector("a.courseBox")
            elif self.headless:
                raise Exception(
                    "No saved Gradescope session. Run `gradescope login` once "
                    "(opens a browser for QUT SSO and 2FA), then run `gradescope submit` again."
                )
            else:
                log_info("Browser login required — complete SSO in the window.")
                await wait_for_gradescope_login(page, steps)
            
            # Step 2: Find Course
            steps.next_step(f"Finding course '{course}'...")
            courses = await page.query_selector_all("a.courseBox")
            course_label = ""
            
            for c in courses:
                shortname_elem = await c.query_selector("h3.courseBox--shortname")
                if not shortname_elem:
                    continue
                shortname = (await shortname_elem.inner_text()).strip()
                
                if course.lower() in shortname.lower():
                    href = await c.get_attribute("href")
                    course_label = shortname
                    steps.complete_step(f"Found course: {course_label}")
                    await page.goto(f"https://www.gradescope.com.au{href}")
                    await page.wait_for_selector('a[href*="/assignments/"]')
                    break
            
            if not course_label:
                raise Exception(f"❌ Could not find course matching '{course}'")
            
            # Step 3: Find Assignment
            steps.next_step(f"Finding assignment '{assignment}'...")
            assignment_label = ""
            
            # Try finding assignment links first
            assignments = await page.query_selector_all('a[href*="/assignments/"]')
            for a in assignments:
                label = (await a.inner_text()).strip()
                if assignment.lower() in label.lower():
                    href = await a.get_attribute("href")
                    assignment_label = label
                    steps.complete_step(f"Found assignment: {assignment_label}")
                    await page.goto(f"https://www.gradescope.com.au{href}")
                    await page.wait_for_selector('button.js-submitAssignment')
                    break
            
            # Fallback: try matching visible submission buttons on the same course page
            if not assignment_label:
                buttons = await page.query_selector_all('button.js-submitAssignment')
                for b in buttons:
                    label = (await b.inner_text()).strip()
                    if assignment.lower() in label.lower():
                        assignment_label = label
                        steps.complete_step(f"Found assignment (button): {assignment_label}")
                        break
            
            if not assignment_label:
                raise Exception(f"❌ Could not find assignment matching '{assignment}'")
            
            # Step 4: Submit File  
            steps.next_step("Submitting file...")
            
            # Check if this is a first-time submission (button) or resubmission (link)
            resubmit_button = page.locator('button.js-submitAssignment:has-text("Resubmit")')
            submit_button = page.locator(f'button.js-submitAssignment:has-text("{assignment_label}")')
            
            is_first_submission = await submit_button.is_visible() and not await resubmit_button.is_visible()
            
            if await resubmit_button.is_visible():
                log_info("Resubmission detected - clicking resubmit button...")
                await resubmit_button.click()
                await page.wait_for_selector('input#submission_method_upload')
                await page.check('input#submission_method_upload')
                
                # Handle resubmission file input
                file_input = page.locator('input[type="file"]')
                log_info("Waiting for file input to appear...")
                try:
                    await file_input.wait_for(timeout=10000, state="attached")
                except Exception as e:
                    raise e
                
                log_info(f"Uploading: {file}")
                await file_input.set_input_files(file)
                await page.wait_for_timeout(1000)
                
                upload_button = page.locator('button.tiiBtn-primary.js-submitCode')
                log_info("Clicking Upload...")
                await upload_button.wait_for(timeout=5000)
                await upload_button.click()
                
            elif await submit_button.is_visible():
                log_info("First submission detected - clicking submit button...")
                await submit_button.click()
                
                # Wait for modal to open
                log_info("Waiting for submission modal to open...")
                await page.wait_for_selector('dialog#submit-code-modal', timeout=10000)
                
                # Ensure upload method is selected
                await page.wait_for_selector('input#submission_method_upload')
                await page.check('input#submission_method_upload')
                
                # Handle first-time submission - use same approach as resubmissions
                log_info("Handling first-time submission...")
                
                # Handle the dropzone with file chooser interception
                log_info("Setting up file chooser interception for dropzone...")
                dropzone = page.locator('.js-dropzone')
                await dropzone.wait_for(timeout=5000)
                
                # Set up file chooser interception before clicking dropzone
                log_info("Waiting for file chooser and setting files...")
                async with page.expect_file_chooser() as fc_info:
                    # Click the dropzone to trigger the file chooser
                    await dropzone.click()
                
                # Handle the file chooser when it appears
                file_chooser = await fc_info.value
                await file_chooser.set_files(file)
                log_success(f"Set files via file chooser: {file}")
                
                # Wait a moment for the file to be processed by dropzone
                await page.wait_for_timeout(2000)
                
                # Check if the dropzone shows the file preview
                try:
                    file_preview = page.locator('.js-dropzonePreview')
                    preview_container = page.locator('.js-dropzonePreviewContainer')
                    if await file_preview.is_visible() or await preview_container.is_visible():
                        log_success("✅ File appears in dropzone preview")
                    else:
                        log_warning("⚠️ File not visible in dropzone preview")
                except:
                    log_warning("⚠️ Could not check dropzone preview")
                
                # Click the upload button in the modal
                upload_button = page.locator('button.tiiBtn-primary.js-submitCode')
                log_info("Clicking Upload...")
                await upload_button.wait_for(timeout=5000)
                await upload_button.click()
                
            else:
                raise Exception("❌ Could not locate a submission button.")
            
            await page.wait_for_timeout(3000)
            steps.complete_step("File submitted successfully!")

            submission_url = page.url
            if self.headless:
                log_info(f"Submission URL: {submission_url}")

            grade_text = None
            if notify_when_graded:
                steps.next_step("Waiting for autograder...")
                grade_text = await self._wait_for_grade(page)
                if grade_text:
                    console.print()
                    log_success(f"Grade: {grade_text}")

            if not self.headless:
                log_info("Leaving the browser open. Press Enter to exit.")
                await asyncio.get_event_loop().run_in_executor(None, input)

            return course_label, assignment_label

        except Exception as e:
            # Handle browser closure gracefully
            if "Target page, context or browser has been closed" in str(e):
                log_error("Browser was closed manually during submission")
                log_info("Tip: Keep the browser window open during submission")
                raise Exception("❌ Submission interrupted - browser was closed")
            elif "Protocol error" in str(e) and "Target closed" in str(e):
                log_error("Browser connection lost during submission")
                log_info("Tip: Check your internet connection and try again")
                raise Exception("❌ Submission failed - browser connection lost")
            else:
                # Re-raise other exceptions with original message
                raise e
            
        finally:
            try:
                await context.close()
            except Exception:
                pass
            try:
                await playwright.stop()
            except Exception:
                pass
    
    async def _wait_for_grade(self, page) -> Optional[str]:
        """Wait for grade; return score text or None."""
        grade_selector = "div.submissionOutlineHeader--totalPoints"
        max_attempts = 48  # 4 minutes @ 5s interval
        grade_text = None

        try:
            with create_spinner_progress() as progress:
                task = progress.add_task("Checking grade", total=None)

                for _ in range(max_attempts):
                    await page.reload()
                    grade_el = await page.query_selector(grade_selector)

                    if grade_el:
                        text = (await grade_el.inner_text()).strip()
                        if text and not text.startswith("-"):
                            grade_text = text
                            break

                    await asyncio.sleep(5)
                else:
                    log_warning(
                        f"No grade after {max_attempts * 5}s — check Gradescope in the browser."
                    )
        except Exception as e:
            if "Target page, context or browser has been closed" in str(e):
                log_error("Browser was closed while waiting for grade")
                log_info("Grade monitoring stopped - submission was successful")
            elif "Protocol error" in str(e) and "Target closed" in str(e):
                log_error("Browser connection lost while waiting for grade")
                log_info("Grade monitoring stopped - submission was successful")
            else:
                log_warning(f"Grade monitoring stopped due to: {e}")
                log_info("Submission was successful, check Gradescope manually for grade")

        return grade_text


async def interactive_login(clear_first: bool = False) -> None:
    """Open a browser so the user can log in; cookies are stored for later submits."""
    print_banner("login")
    session_manager = SessionManager()
    if clear_first:
        session_manager.clear_session()

    context, playwright, _browser = await session_manager.get_browser_context(headless=False)
    page = await context.new_page()
    try:
        await wait_for_gradescope_login(page)
        log_info("Session saved. Press Enter to close the browser.")
        await asyncio.get_event_loop().run_in_executor(None, input)
    finally:
        try:
            await context.close()
        except Exception:
            pass
        try:
            await playwright.stop()
        except Exception:
            pass
