#!/usr/bin/env python3
"""
QUT Gradescope Auto Submitter - Automation Setup Script

This script helps you set up automated Gradescope submissions using:
- GitHub Actions workflows
- Git hooks
- Environment variables and configuration
"""

import os
import sys
import shutil
from pathlib import Path
import json
import yaml

def print_banner():
    print("""
╭────────────────────────────────────────────────────────────────────╮
│  🎯 QUT Gradescope Auto Submitter - Automation Setup                │
│                                                                    │
│  Set up automated submissions with GitHub Actions and Git hooks   │
╰────────────────────────────────────────────────────────────────────╯
""")

def check_requirements():
    """Check if we're in the right environment."""
    errors = []
    
    # Check if we're in a git repository
    if not Path('.git').exists():
        errors.append("❌ Not in a Git repository")
    
    # Check if gradescope is installed
    try:
        import subprocess
        result = subprocess.run(['gradescope', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            errors.append("❌ Gradescope CLI not installed")
    except FileNotFoundError:
        errors.append("❌ Gradescope CLI not found in PATH")
    
    return errors

def setup_github_actions():
    """Set up GitHub Actions workflows."""
    print("\n🚀 Setting up GitHub Actions...")
    
    workflows_dir = Path('.github/workflows')
    workflows_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy workflow files (these would be bundled with the package)
    workflow_files = [
        'auto-submit.yml',
        'scheduled-submit.yml', 
        'manual-submit.yml',
        'matrix-submit.yml'
    ]
    
    for workflow in workflow_files:
        source = Path(__file__).parent / '.github/workflows' / workflow
        dest = workflows_dir / workflow
        
        if source.exists():
            shutil.copy2(source, dest)
            print(f"  ✅ Copied {workflow}")
        else:
            print(f"  ⚠️  {workflow} not found, skipping")
    
    print("\n📋 GitHub Actions setup complete!")
    print("\n🔧 Next steps for GitHub Actions:")
    print("1. Go to your GitHub repository settings")
    print("2. Navigate to 'Secrets and variables' > 'Actions'")
    print("3. Add these secrets:")
    print("   - GRADESCOPE_USERNAME: Your QUT student number")
    print("   - GRADESCOPE_PASSWORD: Your QUT password")
    print("4. Add these variables:")
    print("   - GRADESCOPE_COURSE: Your course code (e.g., cab201)")
    print("   - GRADESCOPE_ASSIGNMENT: Your assignment name (e.g., t6q1)")

def setup_git_hooks():
    """Set up Git hooks."""
    print("\n🪝 Setting up Git hooks...")
    
    hooks_dir = Path('.git/hooks')
    hooks_dir.mkdir(exist_ok=True)
    
    print("\nGit hooks behavior:")
    print("1. Full hooks (submit + wait for grade)")
    print("2. Quick hooks (submit only, no grade wait)")
    print("3. Skip Git hooks setup")
    
    while True:
        hook_type = input("\nChoose hook behavior (1-3): ").strip()
        
        if hook_type in ["1", "2"]:
            print("\nAvailable Git hooks:")
            print("1. Pre-commit hook (submit before each commit)")
            print("2. Post-commit hook (submit after each commit)")
            print("3. Both hooks")
            print("4. Back to hook type selection")
            
            while True:
                choice = input("\nChoose hook timing (1-4): ").strip()
                
                if choice == "1":
                    if hook_type == "1":
                        create_pre_commit_hook(hooks_dir, with_grade=True)
                    else:
                        create_pre_commit_hook(hooks_dir, with_grade=False)
                    return
                elif choice == "2":
                    if hook_type == "1":
                        create_post_commit_hook(hooks_dir, with_grade=True)
                    else:
                        create_post_commit_hook(hooks_dir, with_grade=False)
                    return
                elif choice == "3":
                    if hook_type == "1":
                        create_pre_commit_hook(hooks_dir, with_grade=True)
                        create_post_commit_hook(hooks_dir, with_grade=True)
                    else:
                        create_pre_commit_hook(hooks_dir, with_grade=False)
                        create_post_commit_hook(hooks_dir, with_grade=False)
                    return
                elif choice == "4":
                    break
                else:
                    print("  ❌ Invalid choice, please enter 1-4")
        elif hook_type == "3":
            print("  ⏭️  Skipping Git hooks setup")
            break
        else:
            print("  ❌ Invalid choice, please enter 1-3")

def create_pre_commit_hook(hooks_dir, with_grade=False):
    """Create pre-commit hook."""
    if with_grade:
        hook_content = '''#!/bin/bash
# Pre-commit hook for Gradescope submissions (with grade monitoring)
echo "Pre-commit: Checking for gradescope.yml..."

if [ -f "gradescope.yml" ]; then
    echo "Found gradescope.yml, running submission with grade monitoring..."
    gradescope submit --headless
    if [ $? -eq 0 ]; then
        echo "Gradescope submission and grading completed successfully"
    else
        echo "Gradescope submission failed"
        echo "Commit will proceed anyway..."
    fi
else
    echo "No gradescope.yml found, skipping submission"
fi
'''
    else:
        hook_content = '''#!/bin/bash
# Pre-commit hook for Gradescope submissions (quick mode)
echo "Pre-commit: Checking for gradescope.yml..."

if [ -f "gradescope.yml" ]; then
    echo "Found gradescope.yml, running quick submission..."
    gradescope submit --headless --no-grade-wait
    if [ $? -eq 0 ]; then
        echo "Gradescope submission successful (not waiting for grade)"
    else
        echo "Gradescope submission failed"
        echo "Commit will proceed anyway..."
    fi
else
    echo "No gradescope.yml found, skipping submission"
fi
'''
    
    hook_file = hooks_dir / 'pre-commit'
    hook_file.write_text(hook_content)
    hook_file.chmod(0o755)
    hook_type = "full" if with_grade else "quick"
    print(f"  ✅ Pre-commit hook installed ({hook_type} mode)")

def create_post_commit_hook(hooks_dir, with_grade=False):
    """Create post-commit hook."""
    if with_grade:
        hook_content = '''#!/bin/bash
# Post-commit hook for Gradescope submissions (with grade monitoring)
echo "Post-commit: Checking for gradescope.yml..."

if [ -f "gradescope.yml" ]; then
    echo "Found gradescope.yml, running submission with grade monitoring..."
    gradescope submit --headless
    if [ $? -eq 0 ]; then
        echo "Gradescope submission and grading completed successfully"
    else
        echo "Gradescope submission failed"
    fi
else
    echo "No gradescope.yml found, skipping submission"
fi
'''
    else:
        hook_content = '''#!/bin/bash
# Post-commit hook for Gradescope submissions (quick mode)
echo "Post-commit: Checking for gradescope.yml..."

if [ -f "gradescope.yml" ]; then
    echo "Found gradescope.yml, running quick submission..."
    gradescope submit --headless --no-grade-wait
    if [ $? -eq 0 ]; then
        echo "Gradescope submission successful (not waiting for grade)"
    else
        echo "Gradescope submission failed"
    fi
else
    echo "No gradescope.yml found, skipping submission"
fi
'''
    
    hook_file = hooks_dir / 'post-commit'
    hook_file.write_text(hook_content)
    hook_file.chmod(0o755)
    hook_type = "full" if with_grade else "quick"
    print(f"  ✅ Post-commit hook installed ({hook_type} mode)")

def setup_configuration():
    """Set up gradescope.yml configuration."""
    print("\n⚙️ Setting up configuration...")
    
    if Path('gradescope.yml').exists():
        print("  📄 gradescope.yml already exists")
        overwrite = input("  Overwrite existing configuration? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("  ⏭️  Keeping existing configuration")
            return
    
    print("\n📋 Please provide configuration details:")
    
    course = input("Course code (e.g., cab201): ").strip()
    assignment = input("Assignment name (e.g., t6q1): ").strip()
    
    config = {
        'course': course,
        'assignment': assignment,
        'zip_name': 'submission.zip',
        'bundle': ['*'],
        'always_fresh_login': False,
        'headless': False,
        'notify_when_graded': True,
        'manual_login': False,
        'no_session_save': False
    }
    
    with open('gradescope.yml', 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    print("  ✅ gradescope.yml created")

def setup_credentials():
    """Help user set up credentials."""
    print("\n🔐 Setting up credentials...")
    print("\nRecommended: Use the interactive credentials manager")
    print("Run: gradescope credentials")
    print("\nThis will guide you through saving your credentials securely.")

def create_gitignore():
    """Ensure sensitive files are in .gitignore."""
    gitignore_path = Path('.gitignore')
    
    additions = [
        '# QUT Gradescope Auto Submitter',
        '.env',
        'submission.zip',
        '*.zip',
    ]
    
    if gitignore_path.exists():
        content = gitignore_path.read_text()
        if '.env' in content:
            print("  ✅ .gitignore already configured")
            return
    
    print("\n📝 Updating .gitignore...")
    
    with open('.gitignore', 'a') as f:
        f.write('\n' + '\n'.join(additions) + '\n')
    
    print("  ✅ Added sensitive files to .gitignore")

def main():
    print_banner()
    
    # Check requirements
    errors = check_requirements()
    if errors:
        print("❌ Setup requirements not met:")
        for error in errors:
            print(f"   {error}")
        print("\nPlease fix these issues and run the setup again.")
        sys.exit(1)
    
    print("✅ All requirements met!")
    
    # Setup components
    try:
        setup_configuration()
        setup_credentials()
        create_gitignore()
        setup_github_actions()
        setup_git_hooks()
        
        print("\n🎉 Automation setup complete!")
        print("\n📋 Summary:")
        print("  ✅ Configuration file created")
        print("  ✅ .gitignore updated")
        print("  ✅ GitHub Actions workflows ready")
        print("  ✅ Git hooks configured")
        
        print("\n🚀 Next steps:")
        print("1. Set up credentials: gradescope credentials")
        print("2. Test submission: gradescope submit")
        print("3. Push to GitHub to trigger automated workflows")
        print("4. Configure repository secrets in GitHub")
        
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
