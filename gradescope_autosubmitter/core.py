"""Core Gradescope submission functionality."""

import asyncio
import os
import zipfile
import time
import shutil
from datetime import datetime
from fnmatch import fnmatch
from typing import List, Tuple, Optional
from pathlib import Path

from playwright.async_api import async_playwright


def timestamp() -> str:
    """Generate a timestamp string."""
    return datetime.now().strftime("%H:%M:%S.%f")[:-2]


def log(msg: str) -> None:
    """Log a message with timestamp."""
    print(f"[{timestamp()}] {msg}")


class SessionManager:
    """Manages persistent browser sessions."""
    
    def __init__(self, fresh_login: bool = False):
        # Cross-platform session directory
        if os.name == 'nt':  # Windows
            self.session_dir = Path.home() / "AppData" / "Local" / "qut_gradescope"
        else:  # Linux/Mac
            self.session_dir = Path.home() / ".cache" / "qut_gradescope"
        
        self.fresh_login = fresh_login
        
        if fresh_login and self.session_dir.exists():
            log("Using fresh login (clearing session)")
            shutil.rmtree(self.session_dir)
    
    async def get_browser_context(self, headless: bool = True):
        """Get browser context with persistent session."""
        p = await async_playwright().start()
        
        if self.fresh_login:
            # Use regular browser without persistence
            log("🆕 Using fresh browser context (no persistence)")
            browser = await p.chromium.launch(headless=headless)
            context = await browser.new_context()
            return context, p, browser
        else:
            # Use persistent context
            self.session_dir.mkdir(parents=True, exist_ok=True)
            log(f"Using persistent session: {self.session_dir}")
            
            # Use persistent context for session management
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(self.session_dir),
                headless=headless,
                args=[
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            )
            
            # Log context info - persistent contexts don't have .browser
            log(f"Persistent context created with user data directory")
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
    
    def cleanup_session(self):
        """Manually clean up session data."""
        if self.session_dir.exists():
            shutil.rmtree(self.session_dir)
            log("Session data cleared")


class GradescopeSubmitter:
    """Main class for handling Gradescope submissions."""
    
    def __init__(self, username: str, password: str, headless: bool = False, fresh_login: bool = False, manual_login: bool = False):
        self.username = username
        self.password = password
        self.headless = headless
        self.manual_login = manual_login
        self.session_manager = SessionManager(fresh_login or manual_login)  # Manual login always uses fresh session
    
    def create_zip(self, file_patterns: List[str], output_filename: str) -> None:
        """Create a zip file from matching file patterns."""
        EXCLUDE_FILES = {
            "gradescope.py", 
            "gradescope.json", 
            "gradescope.yml", 
            "gradescope.yaml",
            ".gradescope.yml",
            ".gradescope.yaml",
            output_filename
        }
        
        matched_files = []
        for root, dirs, files in os.walk("."):
            # Skip hidden directories and common ignore patterns
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
            
            for file in files:
                if file in EXCLUDE_FILES or file.startswith('.'):
                    continue
                
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, ".")
                
                for pattern in file_patterns:
                    if fnmatch(rel_path, pattern):
                        matched_files.append((full_path, rel_path))
                        break
        
        if not matched_files:
            raise ValueError(f"❌ No files matched the patterns: {file_patterns}")
        
        with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for full_path, arcname in matched_files:
                zipf.write(full_path, arcname)
                print(f"📦 Added: {arcname}")
        
        print(f"\n✅ Created: {output_filename} ({len(matched_files)} files)")
    
    def print_submission_summary(self, course_label: str, assignment_label: str, file: str) -> None:
        """Print a formatted submission summary."""
        print("\n🧾 Submission Receipt:")
        print(f'✅ Submitted to "{course_label} > {assignment_label}"')
        print(f"🕒 Time: {datetime.now().strftime('%I:%M %p, %B %d')}")
        print(f"📁 File: {file}")
    
    async def submit_to_gradescope(
        self, 
        course: str, 
        assignment: str, 
        file: str, 
        notify_when_graded: bool = True
    ) -> Tuple[str, str]:
        """Submit a file to Gradescope."""
        context, playwright, browser = await self.session_manager.get_browser_context(self.headless)
        
        # Session workflow:
        # 1. Always check if we're logged in (unless fresh_login is forced)
        # 2. Session check uses SAML redirect to detect login state
        # 3. If logged in, skip login process
        # 4. If not logged in, perform full login
        
        # Create page first so we can reuse it
        page = await context.new_page()
        
        needs_login = True
        current_url = None
        if not self.session_manager.fresh_login:
            # Always check session status - this loads any existing session data
            is_logged_in, current_url = await self.session_manager.is_logged_in(context, page)
            if is_logged_in:
                log("Using existing session...")
                needs_login = False
            else:
                log("🔐 Logging in...")
        
        try:
            # Set up error handling for minor network issues
            page.on('pageerror', lambda error: None)  # Ignore page errors
            page.on('requestfailed', lambda request: None)  # Ignore failed requests
            
            if self.manual_login:
                # Manual login mode - let user login themselves
                log("Opening QUT SSO page for manual login...")
                await page.goto("https://www.gradescope.com.au/auth/saml/qut")
                
                log("Please log in manually in the browser window...")
                log("Waiting for you to complete login...")
                
                # Wait for login to complete by checking for course boxes
                try:
                    await page.wait_for_selector("a.courseBox", timeout=300000)  # 5 minutes
                    log("🔓 Manual login detected as complete!")
                except:
                    raise Exception("❌ Manual login timed out or failed")
                    
            elif needs_login:
                log("Navigating directly to QUT SSO...")
                # Skip Gradescope homepage, go straight to QUT login
                await page.goto("https://www.gradescope.com.au/auth/saml/qut")
                
                if "qut.edu.au" in page.url:
                    log("QUT login detected. Entering credentials...")
                    await page.wait_for_selector('input[name="username"]')
                    await page.fill('input[name="username"]', self.username)
                    await page.fill('input[name="password"]', self.password)
                    
                    # Try to click "Remember Me" checkbox if it exists
                    try:
                        remember_selectors = [
                            'input[name="rememberMe"]',
                            'input[name="remember-me"]', 
                            'input[name="remember_me"]',
                            'input[type="checkbox"][id*="remember"]',
                            'input[type="checkbox"][id*="Remember"]',
                            'input[type="checkbox"][name*="remember"]',
                            'input[type="checkbox"][value*="remember"]'
                        ]
                        
                        for selector in remember_selectors:
                            try:
                                if await page.locator(selector).is_visible(timeout=2000):
                                    await page.check(selector)
                                    log("✅ Remember Me enabled")
                                    break
                            except:
                                continue
                    except:
                        pass  # Silent fail for Remember Me
                    
                    await page.click('button#kc-login')
                    await page.wait_for_selector("a.courseBox")
                    log("🔓 QUT login complete")
            else:
                if current_url and "gradescope.com.au" in current_url:
                    log(f"Already on Gradescope from session check: {current_url}")
                    # We're already on the right page, just wait for course boxes
                    try:
                        await page.wait_for_selector("a.courseBox", timeout=5000)
                    except:
                        # If course boxes aren't ready, we might need to refresh
                        log("Refreshing page to ensure it's ready...")
                        await page.reload()
                        await page.wait_for_selector("a.courseBox")
                else:
                    log("Navigating to Gradescope (already logged in)...")
                    await page.goto("https://www.gradescope.com.au")
                    await page.wait_for_selector("a.courseBox")
            
            log("Finding course...")
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
                    log(f"✅ Found: {course_label}")
                    await page.goto(f"https://www.gradescope.com.au{href}")
                    await page.wait_for_selector('a[href*="/assignments/"]')
                    break
            
            if not course_label:
                raise Exception(f"❌ Could not find course matching '{course}'")
            
            log("Finding assignment...")
            assignment_label = ""
            
            # Try finding assignment links first
            assignments = await page.query_selector_all('a[href*="/assignments/"]')
            for a in assignments:
                label = (await a.inner_text()).strip()
                if assignment.lower() in label.lower():
                    href = await a.get_attribute("href")
                    assignment_label = label
                    log(f"✅ Found: {assignment_label}")
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
                        log(f"Found assignment (button only): {assignment_label}")
                        break
            
            if not assignment_label:
                raise Exception(f"❌ Could not find assignment matching '{assignment}'")
            
            log("Starting submission...")
            resubmit_button = page.locator('button.js-submitAssignment:has-text("Resubmit")')
            submit_button = page.locator(f'button.js-submitAssignment:has-text("{assignment_label}")')
            
            if await resubmit_button.is_visible():
                await resubmit_button.click()
            elif await submit_button.is_visible():
                await submit_button.click()
            else:
                raise Exception("❌ Could not locate a submission button.")
            
            await page.wait_for_selector('input#submission_method_upload')
            await page.check('input#submission_method_upload')
            
            file_input = page.locator('input[type="file"]')
            log("Waiting for file input to appear...")
            try:
                await file_input.wait_for(timeout=10000, state="attached")
            except Exception as e:
                if "strict mode violation" in str(e) and "resolved to 3 elements" in str(e):
                    raise Exception("❌ This assignment has no previous submissions. Please make at least one manual submission through the Gradescope web interface before using this CLI tool.")
                else:
                    raise e
            
            log(f"Uploading: {file}")
            await file_input.set_input_files(file)
            await page.wait_for_timeout(1000)
            
            upload_button = page.locator('button.tiiBtn-primary.js-submitCode')
            log("Clicking Upload...")
            await upload_button.wait_for(timeout=5000)
            await upload_button.click()
            
            await page.wait_for_timeout(3000)
            log("✅ File submitted successfully!")
            self.print_submission_summary(course_label, assignment_label, file)
            
            if notify_when_graded:
                await self._wait_for_grade(page)
            
            if not self.headless:
                log("Leaving the browser open. Press Enter to exit.")
                await asyncio.get_event_loop().run_in_executor(None, input)
            
            return course_label, assignment_label
            
        except Exception as e:
            # Handle browser closure gracefully
            if "Target page, context or browser has been closed" in str(e):
                log("❌ Browser was closed manually during submission")
                log("💡 Tip: Keep the browser window open during submission")
                raise Exception("❌ Submission interrupted - browser was closed")
            elif "Protocol error" in str(e) and "Target closed" in str(e):
                log("❌ Browser connection lost during submission")
                log("💡 Tip: Check your internet connection and try again")
                raise Exception("❌ Submission failed - browser connection lost")
            else:
                # Re-raise other exceptions with original message
                raise e
            
        finally:
            try:
                if browser:  # Regular browser (fresh login)
                    if not browser.is_connected():
                        pass  # Browser already closed
                    else:
                        await browser.close()
                else:  # Persistent context
                    if not context.pages:  # No pages means context might be closed
                        pass  # Context likely already closed
                    else:
                        await context.close()
            except Exception as e:
                # Ignore errors when browser/context is already closed
                if "Target page, context or browser has been closed" not in str(e):
                    pass  # Only ignore the specific "already closed" error
            finally:
                try:
                    await playwright.stop()
                except Exception:
                    # Ignore playwright stop errors
                    pass
    
    async def _wait_for_grade(self, page) -> None:
        """Wait for and display the grade when available."""
        log("Waiting for grade to appear...")
        grade_selector = "div.submissionOutlineHeader--totalPoints"
        max_attempts = 48  # 4 minutes @ 5s interval
        start_time = time.time()
        
        try:
            for i in range(max_attempts):
                await page.reload()
                grade_el = await page.query_selector(grade_selector)
                
                elapsed = int(time.time() - start_time)
                mins, secs = divmod(elapsed, 60)
                timer_display = f"{mins:02d}:{secs:02d}"
                
                if grade_el:
                    grade_text = (await grade_el.inner_text()).strip()
                    if grade_text and not grade_text.startswith("-"):
                        bold_grade = f"\033[1m{grade_text}\033[0m"
                        print()
                        log(f"🏆 Grade returned after {timer_display}: {bold_grade}")
                        break
                
                await asyncio.sleep(5)
            else:
                log(f"\n⌛ Timed out after {max_attempts * 5} seconds with no grade available.")
        except Exception as e:
            if "Target page, context or browser has been closed" in str(e):
                log("❌ Browser was closed while waiting for grade")
                log("💡 Grade monitoring stopped - submission was successful")
            elif "Protocol error" in str(e) and "Target closed" in str(e):
                log("❌ Browser connection lost while waiting for grade")
                log("💡 Grade monitoring stopped - submission was successful")
            else:
                log(f"⚠️ Grade monitoring stopped due to: {e}")
                log("💡 Submission was successful, check Gradescope manually for grade")
